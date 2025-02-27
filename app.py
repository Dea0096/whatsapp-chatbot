import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request

app = Flask(__name__)

# Configurazione del bot WhatsApp
VERIFY_TOKEN = "mio_verification_token"
ACCESS_TOKEN = "EAAQaZCVgHS2IBO9kepyPNjfI6S2ekxwgx9hZCTpgghzFCGQd9eNqr1fLEPWzzVXhPZBulKtN4bOy6PNwtuQd4irxp7IaSNSNCqBOVscHAORJnCbE7uvfEVNDNbzRRYq56YVX7Jqdq8fpeJhuZC7tfy39tWEQDcjSCW3t85kvznOxhrTkpusRS2ZCEZCaicWg5DYkmMkgZDZD"

# Configurazione Google Sheets
GOOGLE_SHEETS_JSON = "caffe-duomo-ef40a65a6639.json"  # Nome del file JSON delle credenziali
SPREADSHEET_ID = "16F0ssrfhK3Sgehb8XW3bBTrWSYg75oQris2GdgCsf3w"  # ID del tuo Google Sheet
SHEET_NAME = "foglio1"  # Nome del foglio dentro il Google Sheets

# Autenticazione con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_SHEETS_JSON, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)  # Seleziona il foglio corretto

# Stato utenti temporaneo
users_state = {}

def save_to_google_sheets(user_data):
    """Salva i dati nel Google Sheet"""
    row = [
        user_data.get("id_utente", "Sconosciuto"),
        user_data.get("name", "Sconosciuto"),
        user_data.get("birthday", "Sconosciuto"),
        user_data.get("city", "Sconosciuto"),
        user_data.get("visit_time", "Sconosciuto"),
        user_data.get("email", "Sconosciuto"),
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
                            send_whatsapp_message(phone_number, f"Grazie, {text}! Ora dimmi la tua data di nascita in formato GG/MM/AAAA 🎂✨")
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
                            send_whatsapp_message(phone_number, f"Perfetto, {user['name']}! 🎉 Sei nella nostra family! 💛")
                            del users_state[phone_number]  # Reset

                    elif text == "fidelity":
                        users_state[phone_number] = {"step": "name"}
                        send_whatsapp_message(phone_number, "Ehi! 🥰 Dimmi il tuo nome e cognome ✨")

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
