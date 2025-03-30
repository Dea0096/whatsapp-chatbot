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
ACCESS_TOKEN = "EAAQaZCVgHS2IBO0WDvmFtKuSSSfaQ7O13V4jDnnPD4NwmRA93jubFcPVmaJv0B0CoUYEnAcmMeczLykJfowZCYLIx6kiECZBCLgYGN9wmxNASzjAWqnVdBad4hLDaeaaXA5qgcn4hUOiVxQtTDmjJRb3WITU5kOrRJ0ZCnYgPeoS0BwEsHXaZC2SlZBnZAwXZCsi48OF44drMoMj56R7e7LELwCT76dXZBsMcOJcl76CsLwZDZD"

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

    if user.get("step") == "name":
        user["name"] = text
        send_whatsapp_message(phone_number, "Ora dimmi quando spegni le candeline 🎂 Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🏱")
        user["step"] = "birthday"

    elif user.get("step") == "birthday":
        user["birthday"] = text
        send_whatsapp_message(phone_number, "E tu di dove sei?  Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗")
        user["step"] = "city"

    elif user.get("step") == "city":
        user["city"] = text
        send_whatsapp_message(phone_number, "Ultima domanda e poi siamo ufficialmente best friends! 😍 Quando passi più spesso a trovarci? Ti accogliamo con il profumo del caffè al mattino, con un piatto delizioso a pranzo o con un drink perfetto per l’aperitivo ☕️🍽️🍹?")
        user["step"] = "visit_time"

    elif user.get("step") == "visit_time":
        user["visit_time"] = text
        send_whatsapp_message(phone_number, "Ecco fatto! 🎉 Sei ufficialmente parte della nostra family! 💛 La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! 🎫✨ Non vediamo l’ora di vederti da noi! Quasi dimenticavo! Se vuoi ricevere offerte e sorprese esclusive (tranquillo/a, niente spam! 🤞), lasciami la tua email 📩 Ma solo se ti fa piacere! 💛")
        user["step"] = "email"

    elif user.get("step") == "email":
        user["email"] = text if "@" in text and "." in text else "Sconosciuto"
        user["id_utente"] = phone_number
        sheet.append_row([user.get("id_utente"), user.get("name"), user.get("birthday"), user.get("city"), user.get("visit_time"), user.get("email")])
        send_whatsapp_message(phone_number, "Grazie ancora! ☕️🥐💖 A prestissimo!")
        users_state.pop(phone_number)

    elif "fidelity" in text.lower():
        users_state[phone_number] = {"step": "name"}
        send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉 Qualche domandina per la fidelity, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo! Nome e cognome, così posso registrarti correttamente ✨ Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛")

    elif "martino" in text.lower():
        send_whatsapp_buttons(phone_number)

    elif "cibo e bevande" in text.lower() or "ordinare" in text.lower():
        send_whatsapp_message(phone_number, MENU_TEXT)

    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
