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
ACCESS_TOKEN = "EAAQaZCVgHS2IBO22VBKTaCIp7uWrHpSW2NNwaG7cnEkfo2jsWMZCmJ9ZB3HVU8PhXPVbOpmpHi10XiVD24OJcXDdG5ty2mSSMsLpQtftVFtnrZC7OZBQZCw8J1fPHtVg60ZA28wz80i6PvUHvtohdyN5E2GSM4khwsVGeZBEdQNxrVZCH9qZBu76j2r7hOfKFF90HPrqLINd3AdwQ4z1zJdvdRZCOqfLE90Cpypik0vc9RrrwZDZD"

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

def send_whatsapp_buttons(phone_number):
    url = "https://graph.facebook.com/v18.0/" + os.getenv("WHATSAPP_PHONE_NUMBER_ID") + "/messages"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "Ciao sono Martino! la mascotte del Caffè Duomo! Cosa posso fare per te?"
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "fidelity", "title": "Fidelity"}},
                    {"type": "reply", "reply": {"id": "cibo_bevande", "title": "Cibo e Bevande"}},
                    {"type": "reply", "reply": {"id": "evento", "title": "Prenota un evento"}}
                ]
            }
        }
    }
    requests.post(url, headers=headers, json=payload)

# ... tutto il resto del codice rimane invariato fino a:

            elif "fidelity" in user_message:
                users_state[phone_number] = {"step": "name"}
                send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉 Qualche domandina per la fidelity, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo! Nome e cognome, così posso registrarti correttamente ✨ Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛")

            elif "martino" in user_message:
                send_whatsapp_buttons(phone_number)

            elif "cibo e bevande" in user_message or "ordinare" in user_message:
                send_whatsapp_message(phone_number, MENU_TEXT)

            return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
