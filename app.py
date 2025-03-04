import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from datetime import datetime  # Import per la data di creazione

app = Flask(__name__)

# Configurazione del bot WhatsApp
VERIFY_TOKEN = "mio_verification_token"
ACCESS_TOKEN = "EAAQaZCVgHS2IBO9kepyPNjfI6S2ekxwgx9hZCTpgghzFCGQd9eNqr1fLEPWzzVXhPZBulKtN4bOy6PNwtuQd4irxp7IaSNSNCqBOVscHAORJnCbE7uvfEVNDNbzRRYq56YVX7Jqdq8fpeJhuZC7tfy39tWEQDcjSCW3t85kvznOxhrTkpusRS2ZCEZCaicWg5DYkmMkgZDZD"

# Configurazione Google Sheets
GOOGLE_SHEETS_JSON = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))  # Legge la chiave dalle variabili d’ambiente
SPREADSHEET_ID = "16F0ssrfhK3Sgehb8XW3bBTrWSYg75oQris2GdgCsf3w"  # ID del tuo Google Sheet
SHEET_NAME = "Foglio1"  # Nome del foglio dentro Google Sheets

# Autenticazione con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEETS_JSON, scope)
client = gspread.authorize(creds)

# Verifica se il foglio esiste, altrimenti usa il primo disponibile
spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheets_list = [sheet.title for sheet in spreadsheet.worksheets()]
if SHEET_NAME not in sheets_list:
    SHEET_NAME = sheets_list[0]  # Usa il primo foglio disponibile
    print(f"⚠️ ATTENZIONE: Il foglio '{SHEET_NAME}' non esiste, uso '{SHEET_NAME}'.")

sheet = spreadsheet.worksheet(SHEET_NAME)  # Seleziona il foglio corretto

# Stato utenti temporaneo
users_state = {}

def save_to_google_sheets(user_data):
    """Salva i dati nel Google Sheet in formato compatibile con Cassa in Cloud."""
    today_date = datetime.today().strftime('%Y-%m-%d')  # Data del giorno reale
    row = [
        "",  # ID lasciato vuoto
        "",  # P.IVA Azienda (non disponibile)
        "",  # P.IVA (non disponibile)
        "",  # C.F. (non disponibile)
        user_data.get("name", "Sconosciuto"),  # Nominativo
        "",  # Sesso (non disponibile)
        user_data.get("birthday", "Sconosciuto"),  # Data di Nascita
        "",  # Via e numero civico (non disponibile)
        user_data.get("city", "Sconosciuto"),  # Città
        "",  # CAP (non disponibile)
        "",  # Provincia (non disponibile)
        "",  # Stato (non disponibile)
        user_data.get("id_utente", "Sconosciuto"),  # Telefono (ID utente)
        user_data.get("email", "Sconosciuto"),  # Email
        "",  # Sconti (non disponibile)
        today_date,  # Data Creazione (data reale)
        "Chat WhatsApp"  # Canale di Attivazione
    ]
    sheet.append_row(row)
    print(f"Dati salvati su Google Sheets: {row}")

def send_whatsapp_message(phone_number, message):
    """Invia un messaggio su WhatsApp"""
    url = "https://graph.facebook.com/v17.0/598409370016822/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": phone_number, "text": {"body": message}}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    data = request.get_json()
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    phone_number = message["from"]
                    text = message["text"]["body"].strip().lower()

                    if phone_number in users_state:
                        user = users_state[phone_number]

                        if user["step"] == "name":
                            user["name"] = text
                            send_whatsapp_message(phone_number, "Grazie! Ora dimmi la tua data di nascita in formato GG/MM/AAAA 🎂✨")
                            user["step"] = "birthday"

                        elif user["step"] == "birthday":
                            user["birthday"] = text
                            send_whatsapp_message(phone_number, "Di dove sei? 🏡 Dimmi la tua città! 🚗✨")
                            user["step"] = "city"

                        elif user["step"] == "city":
                            user["city"] = text
                            send_whatsapp_message(phone_number, "Quando passi più spesso da noi? ☕🍽️🍹 (Colazione, Pranzo o Aperitivo)")
                            user["step"] = "visit_time"

                        elif user["step"] == "visit_time":
                            user["visit_time"] = text
                            send_whatsapp_message(phone_number, "Se vuoi ricevere offerte esclusive, lasciami la tua email 📩 (opzionale)")
                            user["step"] = "email"

                        elif user["step"] == "email":
                            user["email"] = text if "@" in text and "." in text else "Sconosciuto"
                            user["id_utente"] = f"ID-{phone_number[-6:]}"  # Genera un ID utente semplice
                            save_to_google_sheets(user)
                            send_whatsapp_message(phone_number, "Perfetto! 🎉 Sei nella nostra family! 💛")
                            del users_state[phone_number]  # Reset

                    elif text == "fidelity":
                        users_state[phone_number] = {"step": "name"}
                        send_whatsapp_message(phone_number, "Ehi! 🥰 Dimmi il tuo nome e cognome ✨")

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
