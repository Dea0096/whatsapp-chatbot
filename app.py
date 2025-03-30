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
ACCESS_TOKEN = "EEAAQaZCVgHS2IBO0WDvmFtKuSSSfaQ7O13V4jDnnPD4NwmRA93jubFcPVmaJv0B0CoUYEnAcmMeczLykJfowZCYLIx6kiECZBCLgYGN9wmxNASzjAWqnVdBad4hLDaeaaXA5qgcn4hUOiVxQtTDmjJRb3WITU5kOrRJ0ZCnYgPeoS0BwEsHXaZC2SlZBnZAwXZCsi48OF44drMoMj56R7e7LELwCT76dXZBsMcOJcl76CsLwZDZD"

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
🍽️ *MENU DEL GIORNO* 🍽️\n
*PRIMI PIATTI*:
• Tortellini al ragù
• Mezzelune al tartufo
• Risotto zucca e speck
• Risotto zafferano e salsiccia
• Tortellini speck e zucchine
• Tagliatelle al cinghiale con carciofi e pecorino

*PIATTO UNICO (componi a piacere)*:
🌱 = Vegetariano
• Riso bianco 🌱
• Riso rosso 🌱
• Pollo alla piastra
• Salsiccia al forno
• Polpette al sugo con piselli
• Merluzzo impanato
• Polpettine di verdure 🌱
• Melanzane grigliate 🌱
• Erba di campo 🌱
• Broccoli e cavolfiori 🌱
• Pomodori gratinati 🌱
• Melanzane gratinate 🌱
• Insalatone 🌱
• Burger veggy (soia o quinoa) 🌱
• Burger bovino

*Scegli la porzione:*
👉 Piccolo | Grande | XL

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

# ... tutto il resto del codice rimane invariato fino a:

            elif "fidelity" in user_message:
                users_state[phone_number] = {"step": "name"}
                send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉 Qualche domandina per la fidelity, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo! Nome e cognome, così posso registrarti correttamente ✨ Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛")

            elif "martino" in user_message:
                send_whatsapp_buttons(phone_number)

            elif "cibo e bevande" in user_message or "ordinare" in user_message:
                send_whatsapp_message(phone_number, MENU_TEXT)

            return 'OK', 200
