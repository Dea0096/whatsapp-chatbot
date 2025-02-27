from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configura il token di accesso e l'ID del numero di telefono
ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN", "EAAQaZCVgHS2IBO6sH83RDVavhtDHwQljO8tJvqkZBbt4m1AAmLl0ZA5qmmju5UwpqFniyCjrFAr9i2R6ZAZBlHwCcHrO0ny8zbm9VftreZBGEVWoMt4eSSbPZBh6NfdQv2SCDdyDzS60bxN2BFZA9YNTNsTRAQqMRG0UNuGYk3XFVvCee0fEU5GKpfZBIKA7qfCTJx7ZAbibwsXeYPxqbzSO9ChSPLhUisBOUFVlikgZBzZA")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "598409370016822")

# URL dell'API di WhatsApp
WHATSAPP_API_URL = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"

# Dizionario per memorizzare gli utenti registrati e il loro stato nella chat
user_states = {}
registered_users = set()  # Memorizza gli utenti che hanno già completato la registrazione

# Funzione per inviare messaggi WhatsApp
def send_whatsapp_message(recipient_id, message_text):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "text": {"body": message_text}
    }
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=data)
    return response.json()

# Endpoint per gestire le richieste webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    if data.get("object"):
        for entry in data.get("entry"):
            for change in entry.get("changes"):
                value = change.get("value")
                messages = value.get("messages")
                if messages:
                    for message in messages:
                        sender_id = message["from"]
                        message_text = message["text"]["body"].strip().lower()

                        # Se l'utente è già registrato, non avviare la chat di nuovo
                        if sender_id in registered_users:
                            send_whatsapp_message(sender_id, "Sei già iscritto al programma Fidelity! 😊")
                            return jsonify({"status": "success"}), 200

                        # Gestione dello stato della conversazione
                        if sender_id not in user_states:
                            user_states[sender_id] = {"step": 0}

                        step = user_states[sender_id]["step"]

                        if step == 0:
                            if message_text == "fidelity":
                              
