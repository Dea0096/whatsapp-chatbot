import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

# TOKEN e ID WhatsApp Business
ACCESS_TOKEN = "EAAQaZCVgHS2IBO6sH83RDVavhtDHwQljO8tJvqkZBbt4m1AAmLl0ZA5qmmju5UwpqFniyCjrFAr9i2R6ZAZBlHwCcHrO0ny8zbm9VftreZBGEVWoMt4eSSbPZBh6NfdQv2SCDdyDzS60bxN2BFZA9YNTNsTRAQqMRG0UNuGYk3XFVvCee0fEU5GKpfZBIKA7qfCTJx7ZAbibwsXeYPxqbzSO9ChSPLhUisBOUFVlikgZBzZA"
PHONE_NUMBER_ID = "1555172650"
VERIFY_TOKEN = "fidelity_bot_token"

# Memoria per utenti registrati
users = {}

@app.route("/", methods=["GET"])
def home():
    return "Chatbot WhatsApp attivo! 🚀"

# Webhook per la verifica
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Errore di verifica", 403

# Webhook per la ricezione dei messaggi
@app.route("/webhook", methods=["POST"])
def receive_message():
    try:
        data = request.get_json()
        log("Messaggio ricevuto", data)  # Log dettagliato

        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "value" in change and "messages" in change["value"]:
                        messages = change["value"]["messages"]
                        for message in messages:
                            user_id = message["from"]
                            text = message.get("text", {}).get("body", "").strip().lower()

                            if user_id not in users:
                                users[user_id] = {"step": "start"}

                            user_state = users[user_id]["step"]

                            if text == "fidelity" and user_state == "start":
                                users[user_id]["step"] = "ask_name"
                                send_whatsapp_message(user_id, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family con la Fidelity Card 🎉 Ti farò qualche domandina per completare l’iscrizione, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo!")
                            
                            elif user_state == "ask_name":
                                users[user_id]["name"] = text
                                users[user_id]["step"] = "ask_birthday"
                                send_whatsapp_message(user_id, f"Grazie, {text}! Ora dimmi quando spegni le candeline 🎂✨ Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
                            
                            elif user_state == "ask_birthday":
                                users[user_id]["birthday"] = text
                                users[user_id]["step"] = "ask_city"
                                send_whatsapp_message(user_id, f"E tu di dove sei, {users[user_id]['name']}? 🏡 Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗✨")
                            
                            elif user_state == "ask_city":
                                users[user_id]["city"] = text
                                users[user_id]["step"] = "ask_visit_time"
                                send_whatsapp_message_with_buttons(user_id, f"Ultima domanda e poi siamo ufficialmente best friends, {users[user_id]['name']}! 😍 Quando passi più spesso a trovarci?", ["☕ Colazione", "🍽️ Pranzo", "🍹 Aperitivo"])
                            
                            elif user_state == "ask_visit_time":
                                users[user_id]["visit_time"] = text
                                users[user_id]["step"] = "ask_email"
                                send_whatsapp_message(user_id, f"Ultima cosa, {users[user_id]['name']}! Se vuoi ricevere offerte e sorprese esclusive, lasciami la tua email 📩 Ma solo se ti fa piacere! 💛")

                            elif user_state == "ask_email":
                                users[user_id]["email"] = text
                                users[user_id]["step"] = "done"
                                send_whatsapp_message(user_id, f"Ecco fatto, {users[user_id]['name']}! 🎉 Sei ufficialmente parte della nostra family! La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! ☕🥐🍹💖 A prestissimo! 😘")

        return "OK", 200

    except Exception as e:
        log("Errore", str(e))
        return "Errore nel server", 500

# Funzione per inviare un messaggio di testo su WhatsApp
def send_whatsapp_message(user_id, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": user_id,
        "type": "text",
        "text": {"body": text}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    log("Risposta WhatsApp", response.json())

# Funzione per inviare messaggi con pulsanti
def send_whatsapp_message_with_buttons(user_id, text, buttons):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": user_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [{"type": "reply", "reply": {"id": f"btn{i}", "title": btn}} for i, btn in enumerate(buttons)]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    log("Risposta WhatsApp con pulsanti", response.json())

# Funzione per loggare gli eventi
def log(title, data):
    print(f"\n🔹 {title}: {json.dumps(data, indent=2, ensure_ascii=False)}\n")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
