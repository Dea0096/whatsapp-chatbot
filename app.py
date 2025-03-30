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

def send_whatsapp_buttons(phone_number):
    url = "https://graph.facebook.com/v17.0/502355696304691/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "Ciao! che bello averti qui, scegli cosa vuoi fare:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "fidelity_option", "title": "Fidelity"}},
                    {"type": "reply", "reply": {"id": "caffe_option", "title": "Caffè o cibo"}},
                    {"type": "reply", "reply": {"id": "evento_option", "title": "Prenotazione"}}
                ]
            }
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    logger.info(f"Bottoni inviati a {phone_number}: {response.status_code} - {response.text}")
    return response.json()

def user_already_registered(phone_number):
    records = sheet.get_all_records()
    return any(str(row.get("ID Utente", "")) == phone_number for row in records)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info("Webhook verificato con successo.")
            return challenge, 200
        else:
            logger.warning("Tentativo di verifica webhook fallito.")
            return "", 403

    if request.method == 'POST':
        try:
            data = request.json
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            if not messages:
                logger.warning("Nessun messaggio trovato nella richiesta.")
                return 'No message', 200

            phone_number = messages[0]['from']
            text = messages[0]['text']['body']
            user_message = text.lower()

            if phone_number in users_state:
                user = users_state[phone_number]

                if user["step"] == "name":
                    user["name"] = text
                    send_whatsapp_message(phone_number, "Ora dimmi quando spegni le candeline 🎂 Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
                    user["step"] = "birthday"

                elif user["step"] == "birthday":
                    user["birthday"] = text
                    send_whatsapp_message(phone_number, "E tu di dove sei?  Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗")
                    user["step"] = "city"

                elif user["step"] == "city":
                    user["city"] = text
                    send_whatsapp_message(phone_number, "Ultima domanda e poi siamo ufficialmente best friends! 😍 Quando passi più spesso a trovarci? Ti accogliamo con il profumo del caffè al mattino, con un piatto delizioso a pranzo o con un drink perfetto per l’aperitivo ☕🍽️🍹?")
                    user["step"] = "visit_time"

                elif user["step"] == "visit_time":
                    user["visit_time"] = text
                    send_whatsapp_message(phone_number, "Ecco fatto! 🎉 Sei ufficialmente parte della nostra family! 💛 La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! 🎫✨ Non vediamo l’ora di vederti da noi! Quasi dimenticavo! Se vuoi ricevere offerte e sorprese esclusive (tranquillo/a, niente spam! 🤞), lasciami la tua email 📩 Ma solo se ti fa piacere! 💛")
                    user["step"] = "email"

                elif user["step"] == "email":
                    user["email"] = text if "@" in text and "." in text else "Sconosciuto"
                    user["id_utente"] = phone_number
                    save_to_google_sheets(user)
                    send_whatsapp_message(phone_number, "Grazie ancora! ☕🥐💖 A prestissimo!")
                    del users_state[phone_number]

            elif "fidelity" in user_message:
                if user_already_registered(phone_number):
                    send_whatsapp_message(phone_number, "Sei già registrato! 🎉 Non c’è bisogno di farlo di nuovo. Ci vediamo presto! ☕💛")
                else:
                    users_state[phone_number] = {"step": "name"}
                    send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉 Qualche domandina per la fidelity, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo! Nome e cognome, così posso registrarti correttamente ✨ Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛")

            elif "martino" in user_message:
                send_whatsapp_buttons(phone_number)

            return 'OK', 200
        except Exception as e:
            logger.error(f"Errore nel processing del messaggio: {e}")
            return 'Errore interno', 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(debug=False, host="0.0.0.0", port=port)
