import os
import json
import requests
import gspread
import zipfile
import uuid
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, send_file

app = Flask(__name__)

# Configurazione del bot WhatsApp
VERIFY_TOKEN = "mio_verification_token"
ACCESS_TOKEN = "EAAQaZCVgHS2IBO9kepyPNjfI6S2ekxwgx9hZCTpgghzFCGQd9eNqr1fLEPWzzVXhPZBulKtN4bOy6PNwtuQd4irxp7IaSNSNCqBOVscHAORJnCbE7uvfEVNDNbzRRYq56YVX7Jqdq8fpeJhuZC7tfy39tWEQDcjSCW3t85kvznOxhrTkpusRS2ZCEZCaicWg5DYkmMkgZDZD"

# Configurazione Google Sheets
GOOGLE_SHEETS_JSON = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))  
SPREADSHEET_ID = "16F0ssrfhK3Sgehb8XW3bBTrWSYg75oQris2GdgCsf3w"  
SHEET_NAME = "Foglio1"

# Autenticazione con Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEETS_JSON, scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.worksheet(SHEET_NAME)

# Cartella per salvare i pass
PASS_FOLDER = "pass_temp"
os.makedirs(PASS_FOLDER, exist_ok=True)

# Stato utenti temporaneo
users_state = {}

def create_pass(user_data):
    """Genera un file .pkpass per Apple Wallet"""
    pass_data = {
        "formatVersion": 1,
        "passTypeIdentifier": "pass.com.tuaazienda.fidelity",
        "serialNumber": str(uuid.uuid4()),
        "teamIdentifier": "TUO_TEAM_ID",
        "organizationName": "Tua Azienda",
        "description": "Fidelity Card",
        "barcode": {
            "message": user_data["id_utente"],
            "format": "PKBarcodeFormatQR",
            "messageEncoding": "iso-8859-1"
        },
        "labelColor": "rgb(255,255,255)",
        "foregroundColor": "rgb(0,0,0)",
        "backgroundColor": "rgb(30,144,255)",
        "generic": {
            "primaryFields": [
                {
                    "key": "fidelity",
                    "label": "Numero Fidelity",
                    "value": user_data["id_utente"]
                }
            ],
            "auxiliaryFields": [
                {
                    "key": "city",
                    "label": "Città",
                    "value": user_data["city"]
                }
            ],
            "secondaryFields": [
                {
                    "key": "visit_time",
                    "label": "Orario Visita",
                    "value": user_data["visit_time"]
                }
            ]
        }
    }

    pass_file = os.path.join(PASS_FOLDER, f"{user_data['id_utente']}.json")
    with open(pass_file, "w") as f:
        json.dump(pass_data, f, indent=4)

    pkpass_file = os.path.join(PASS_FOLDER, f"{user_data['id_utente']}.pkpass")
    with zipfile.ZipFile(pkpass_file, "w") as z:
        z.write(pass_file, "pass.json")

    return pkpass_file

def save_to_google_sheets(user_data):
    """Salva i dati nel Google Sheet"""
    row = [
        "",  # ID vuoto per Cassa in Cloud
        "",  # P.IVA Azienda
        "",  # P.IVA
        "",  # C.F.
        user_data.get("name", "Sconosciuto"),
        "",  # Sesso
        user_data.get("birthday", "Sconosciuto"),
        "",  # Via e numero civico
        user_data.get("city", "Sconosciuto"),
        "",  # CAP
        "",  # Provincia
        "Italia",  # Stato
        user_data.get("id_utente", "Sconosciuto"),  # Telefono
        user_data.get("email", "Sconosciuto"),
        "",  # Sconti
        datetime.today().strftime('%Y-%m-%d'),  # Data Creazione
        "Chat WhatsApp"  # Canale Attivazione
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

@app.route('/download-pass/<user_id>')
def download_pass(user_id):
    """Endpoint per scaricare il pass"""
    pkpass_path = os.path.join(PASS_FOLDER, f"{user_id}.pkpass")
    if os.path.exists(pkpass_path):
        return send_file(pkpass_path, as_attachment=True, download_name=f"{user_id}.pkpass")
    return "Pass non trovato", 404

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

                        if user["step"] == "email":
                            user["email"] = text if "@" in text and "." in text else "Sconosciuto"
                            user["id_utente"] = f"ID-{phone_number[-6:]}"
                            save_to_google_sheets(user)
                            
                            # Genera e invia link al pass digitale
                            pass_file = create_pass(user)
                            pass_link = f"https://whatsapp-chatbot-znzp.onrender.com/download-pass/{user['id_utente']}"
                            send_whatsapp_message(phone_number, f"🎉 La tua Fidelity Card è pronta! Scaricala e conservala nel tuo Wallet 📲:\n{pass_link}")

                            del users_state[phone_number]

                    elif text == "fidelity":
                        if phone_number not in users_state:
                            users_state[phone_number] = {"step": "name"}
                            send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉")
                        else:
                            send_whatsapp_message(phone_number, "Hai già attivato la Fidelity! 💳 Se hai bisogno di assistenza, scrivici!")

    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
