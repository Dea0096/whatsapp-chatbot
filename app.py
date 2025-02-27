from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)

# Configurazione logging per debug
logging.basicConfig(level=logging.INFO)

# Token di accesso aggiornato
ACCESS_TOKEN = "EAAQaZCVgHS2IBO6sH83RDVavhtDHwQljO8tJvqkZBbt4m1AAmLl0ZA5qmmju5UwpqFniyCjrFAr9i2R6ZAZBlHwCcHrO0ny8zbm9VftreZBGEVWoMt4eSSbPZBh6NfdQv2SCDdyDzS60bxN2BFZA9YNTNsTRAQqMRG0UNuGYk3XFVvCee0fEU5GKpfZBIKA7qfCTJx7ZAbibwsXeYPxqbzSO9ChSPLhUisBOUFVlikgZBzZA"

# ID del numero di telefono di WhatsApp Business
PHONE_NUMBER_ID = "598409370016822"

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Chatbot è attivo!", 200

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Verifica della configurazione del webhook con il token di verifica
        verify_token = "MIO TOKEN DI VERIFICA"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == verify_token:
            logging.info("Webhook verificato con successo!")
            return challenge, 200
        else:
            logging.error("Verifica del webhook fallita.")
            return "Verifica fallita", 403

    elif request.method == "POST":
        data = request.get_json()
        logging.info(f"Messaggio ricevuto: {data}")

        if "entry" in data and "changes" in data["entry"][0]:
            message_data = data["entry"][0]["changes"][0]["value"]

            if "messages" in message_data:
                # Estrai il numero di telefono e il messaggio
                phone_number = message_data["messages"][0]["from"]
                text_received = message_data["messages"][0]["text"]["body"].lower()

                logging.info(f"Messaggio ricevuto: {text_received} | Da: {phone_number}")

                if text_received == "fidelity":
                    send_whatsapp_message(phone_number, "Ciao! 😊 Sei pronto per entrare nel nostro programma Fidelity? Rispondi con 'Sì' per iniziare!")

        return jsonify({"status": "received"}), 200

def send_whatsapp_message(to, message):
    """Invia un messaggio WhatsApp utilizzando l'API di Meta."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        logging.info("Messaggio inviato con successo!")
    else:
        logging.error(f"Errore nell'invio del messaggio: {response.text}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
