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
ACCESS_TOKEN = "EAAQaZCVgHS2IBO8Jz7ZA7FvzAzCJ0x5jtE0VFWGKpaeVgZB6djPYRKZA5HHf1hChLuoDdoeClS3SX2Y0NDBDeZC35wxfzD0GrnJPKdeu6IOu80znscrREbCSA9xIGjXnafaV6wOLBQxp8QREYidZADt8SAzXsUPcVscONCtL4ZC81hbzD6V4zIxd3uR95W8625DZAYjZARZBswsKF3tdniDLKOfgoBkSe2IYZB5MLcjZBCHT"

GOOGLE_SHEETS_JSON = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
SPREADSHEET_ID = "16F0ssrfhK3Sgehb8XW3bBTrWSYg75oQris2GdgCsf3w"
SHEET_NAME = "Foglio1"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_SHEETS_JSON, scope)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SPREADSHEET_ID)
sheet = spreadsheet.worksheet(SHEET_NAME)

users_state = {}

RESET_KEYWORD = "andreaos"

MENU_TEXT = """
🍽️ *MENU DEL GIORNO* 🍽️

*🥣 PRIMI PIATTI*
• Tortellini al ragù
• Mezzelune al tartufo
• Risotto zucca e speck
• Risotto zafferano e salsiccia
• Tortellini speck e zucchine
• Tagliatelle al cinghiale con carciofi e pecorino

*🍱 PIATTO UNICO - Componi come vuoi:*
🌱 = Vegetariano
• Riso bianco 🌱  • Riso rosso 🌱  • Pollo alla piastra
• Salsiccia al forno  • Polpette al sugo con piselli
• Merluzzo impanato  • Polpettine di verdure 🌱
• Melanzane grigliate 🌱  • Erba di campo 🌱
• Broccoli e cavolfiori 🌱  • Pomodori gratinati 🌱
• Melanzane gratinate 🌱  • Insalatone 🌱
• Burger veggy (soia o quinoa) 🌱  • Burger bovino

*🍽️ Scegli la porzione:* Piccolo | Grande | XL
🥖 Coperto, acqua e pane sono inclusi
"""

def send_whatsapp_message(phone_number, message):
    url = "https://graph.facebook.com/v18.0/" + os.getenv("WHATSAPP_PHONE_NUMBER_ID") + "/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message
        }
    }
    requests.post(url, headers=headers, json=payload)

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info("Ricevuto: %s", data)

    try:
        text = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        phone_number = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
    except Exception as e:
        logger.error("Errore nel processing del messaggio: %s", e)
        return "Errore", 500

    if text.lower() == RESET_KEYWORD:
        users_state.pop(phone_number, None)
        send_whatsapp_message(phone_number, "Flusso interrotto. Scrivi di nuovo 'fidelity' per ricominciare quando vuoi.")
        return "OK", 200

    user = users_state.get(phone_number, {})

    if "cibo" in text.lower():
        send_whatsapp_message(phone_number, MENU_TEXT)

    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
