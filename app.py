from flask import Flask, request, jsonify
import requests
import os
import re

app = Flask(__name__)

# TOKEN DI ACCESSO A META (fissalo in una variabile d'ambiente in futuro)
ACCESS_TOKEN = "EAAQaZCVgHS2IBO6sH83RDVavhtDHwQljO8tJvqkZBbt4m1AAmLl0ZA5qmmju5UwpqFniyCjrFAr9i2R6ZAZBlHwCcHrO0ny8zbm9VftreZBGEVWoMt4eSSbPZBh6NfdQv2SCDdyDzS60bxN2BFZA9YNTNsTRAQqMRG0UNuGYk3XFVvCee0fEU5GKpfZBIKA7qfCTJx7ZAbibwsXeYPxqbzSO9ChSPLhUisBOUFVlikgZBzZA"
VERIFY_TOKEN = "whatsapp_verify_token"

# URL API WhatsApp
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/1555172650/messages"

# MEMORIA TEMPORANEA DEGLI UTENTI CHE HANNO INIZIATO IL FLUSSO
user_sessions = {}

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Bot is Running!"

# WEBHOOK DI VERIFICA
@app.route("/webhook", methods=["GET"])
def verify():
    """ Verifica il webhook con il token di verifica """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge
    else:
        return "Verifica fallita", 403

# WEBHOOK PER RICEVERE I MESSAGGI
@app.route("/webhook", methods=["POST"])
def webhook():
    """ Riceve i messaggi e risponde automaticamente """
    data = request.get_json()
    
    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    for message in change["value"]["messages"]:
                        phone_number = message["from"]
                        text = message.get("text", {}).get("body", "").strip().lower()

                        if not text:
                            return jsonify({"status": "error", "message": "Messaggio vuoto"}), 200

                        # Controllo se l'utente ha già iniziato la chat
                        if text == "fidelity" and phone_number not in user_sessions:
                            user_sessions[phone_number] = {"step": 1}  # Inizia il flusso
                            send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family con la Fidelity Card 🎉 Ti farò qualche domandina per completare l’iscrizione, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo!")
                        
                        elif phone_number in user_sessions:
                            process_user_response(phone_number, text)
    
    return jsonify({"status": "received"}), 200

def process_user_response(phone_number, text):
    """ Gestisce il flusso della chat fidelity """
    step = user_sessions[phone_number]["step"]

    if step == 1:
        send_whatsapp_message(phone_number, "Dimmi il tuo nome e cognome, così posso registrarti correttamente ✨ (Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛)")
        user_sessions[phone_number]["step"] = 2

    elif step == 2:
        user_sessions[phone_number]["name"] = text
        send_whatsapp_message(phone_number, f"Grazie, {text}! Ora dimmi quando spegni le candeline 🎂✨ Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
        user_sessions[phone_number]["step"] = 3

    elif step == 3:
        if not re.match(r"\d{2}/\d{2}/\d{4}", text):
            send_whatsapp_message(phone_number, f"Oops, {user_sessions[phone_number]['name']}! Sembra che ci sia un piccolo errore nel formato 🧐 Riproviamo? Scrivila così: 15/08/1990 📅")
        else:
            user_sessions[phone_number]["birthday"] = text
            send_whatsapp_message(phone_number, "E tu di dove sei? 🏡 Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗✨")
            user_sessions[phone_number]["step"] = 4

    elif step == 4:
        user_sessions[phone_number]["city"] = text
        send_whatsapp_message(phone_number, "Quando passi più spesso a trovarci? ☕🍽️🍹\n1️⃣ Colazione\n2️⃣ Pranzo\n3️⃣ Aperitivo")
        user_sessions[phone_number]["step"] = 5

    elif step == 5:
        user_sessions[phone_number]["preference"] = text
        send_whatsapp_message(phone_number, "Vuoi ricevere offerte speciali? Lasciami la tua email 📩 (o scrivi 'no' se non vuoi)")
        user_sessions[phone_number]["step"] = 6

    elif step == 6:
        if text.lower() != "no":
            user_sessions[phone_number]["email"] = text
        send_whatsapp_message(phone_number, f"Ecco fatto, {user_sessions[phone_number]['name']}! 🎉 Sei ufficialmente parte della nostra family! 💛 La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! 🎫✨ A prestissimo! 😘")

        save_user_data(phone_number, user_sessions[phone_number])
        del user_sessions[phone_number]  # Cancella la sessione dell'utente

def send_whatsapp_message(phone_number, message):
    """ Invia un messaggio su WhatsApp tramite API di Meta """
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    return response.json()

def save_user_data(phone_number, user_data):
    """ Salva i dati dell'utente (da integrare con Google Sheets in futuro) """
    print(f"📌 Dati utente salvati: {user_data}")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Usa la porta assegnata da Render
    app.run(host='0.0.0.0', port=port, debug=True)
