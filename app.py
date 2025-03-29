import os
import json
import requests
import gspread
import logging
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

VERIFY_TOKEN = "mio_verification_token"
ACCESS_TOKEN = "EAAQaZCVgHS2IBOzdYUToHdv3BmDCQZAoMTBZC8nl9UQe3V7FgasFM8x12CymcZBsAMkmv9ca7iHtl8vfVn4icZBhHahG5N9hPPOZAvyHU5GHUkwr43ZCo9biIZAhOx8NEPVSOnCnjsXnk93FVRjwGAaWyZCOOTc5wtzZCeZAdS47XVNnCHwgpC73emRrBHyyCIHsL5jeZAxhyhPpTZAU24b7ecHerEbsxEcSAMENjPwT3Kans"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct"

GOOGLE_SHEETS_JSON = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
SPREADSHEET_ID = "16F0ssrfhK3Sgehb8XW3bBTrWSYg75oQris2GdgCsf3w"
SHEET_NAME = "Foglio1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEETS_JSON, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.worksheet(SHEET_NAME)

users_state = {}

SYSTEM_PROMPT = (
    "Sei Martino, il chatbot ufficiale del Caffè Duomo, bar storico di Rimini. Parli su WhatsApp in modo naturale, simpatico, ironico ma educato. \n"
    "Rispondi come se fossi il barista amico di tutti: breve, umano, coinvolgente. \n"
    "Rispetti il contesto: parli solo di fidelity card, prenotazioni, orari, menu, offerte, eventi o informazioni legate al bar.\n"
    "Usi emoji con naturalezza e senza esagerare. Non sei un bot qualunque. Sei Martino.\n"
    "Quando ricevi una domanda non chiara, chiedi conferma con garbo. \n"
    "Esempio: 'posso iscrivermi?' → guida alla registrazione. 'Che fate stasera?' → parli degli eventi. \n"
    "Alla fine, se ci sta, puoi chiudere con una battuta o un invito amichevole."
)

def user_already_registered(phone_number):
    phone_numbers = sheet.col_values(13)
    return phone_number in phone_numbers

def save_to_google_sheets(user_data):
    today_date = datetime.today().strftime('%Y-%m-%d')
    row = [
        "", "", "", "", user_data.get("name", "Sconosciuto"), "",
        user_data.get("birthday", "Sconosciuto"), "", user_data.get("city", "Sconosciuto"),
        "", "Italia", user_data.get("id_utente", "Sconosciuto"), user_data.get("email", "Sconosciuto"),
        "", today_date, "Chat WhatsApp"
    ]
    sheet.append_row(row)
    logger.info(f"Dati salvati su Google Sheets: {row}")

def send_whatsapp_message(phone_number, message):
    url = "https://graph.facebook.com/v17.0/502355696304691/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": phone_number, "text": {"body": message}}
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"Messaggio inviato a {phone_number}: {response.status_code} - {response.text}")
    return response.json()

def chiedi_a_chatgpt(messaggio):
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://openrouter.ai",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": messaggio}
            ]
        }
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"Risposta inattesa da OpenRouter: {data}")
            return "Mi sa che oggi ho bisogno di un altro caffè per ragionare 😅 Riproviamo tra poco?"
    except Exception as e:
        logger.error(f"Errore da OpenRouter: {e}")
        return "Oops! Il cervello di Martino è in tilt... riprova più tardi ☕"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
