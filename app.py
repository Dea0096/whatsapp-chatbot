from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configurazione del Token di Accesso e ID del Numero WhatsApp
ACCESS_TOKEN = "EAAQaZCVgHS2IBO6sH83RDVavhtDHwQljO8tJvqkZBbt4m1AAmLl0ZA5qmmju5UwpqFniyCjrFAr9i2R6ZAZBlHwCcHrO0ny8zbm9VftreZBGEVWoMt4eSSbPZBh6NfdQv2SCDdyDzS60bxN2BFZA9YNTNsTRAQqMRG0UNuGYk3XFVvCee0fEU5GKpfZBIKA7qfCTJx7ZAbibwsXeYPxqbzSO9ChSPLhUisBOUFVlikgZBzZA"
PHONE_NUMBER_ID = "598409370016822"
VERIFY_TOKEN = "test_verification_token"

# Dizionario per gestire la sessione utente
user_sessions = {}

def send_whatsapp_message(to, message):
    """Invia un messaggio WhatsApp tramite l'API di Meta"""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    """Gestisce le richieste del Webhook di WhatsApp"""
    if request.method == 'GET':
        # Verifica Webhook con Meta
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token di verifica non valido", 403

    data = request.get_json()

    if data and "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "value" in change and "messages" in change["value"]:
                    messages = change["value"]["messages"]
                    for message in messages:
                        phone_number = message["from"]
                        text_received = message["text"]["body"].strip().lower()

                        # Se l'utente non è in sessione, lo iniziamo solo se scrive "fidelity"
                        if phone_number not in user_sessions:
                            if text_received == "fidelity":
                                user_sessions[phone_number] = {"step": "start"}
                                send_whatsapp_message(phone_number, 
                                    "Ciao! ☕ Sei nel posto giusto per entrare nel nostro programma Fidelity! 🎉\n\n"
                                    "Per iniziare, come ti chiami? (Nome e Cognome) 😊")
                            return jsonify({"status": "session started"}), 200

                        # Se l'utente è già in sessione, seguiamo il flusso delle domande
                        session = user_sessions[phone_number]

                        if session["step"] == "start":
                            session["nome_completo"] = text_received
                            session["step"] = "nickname"
                            send_whatsapp_message(phone_number, 
                                f"Piacere di conoscerti {text_received.split()[0]}! Hai un soprannome con cui ti chiamano gli amici? (Scrivi o digita 'No') 😊")
                        
                        elif session["step"] == "nickname":
                            session["nickname"] = text_received if text_received.lower() != "no" else None
                            session["step"] = "frequenza"
                            send_whatsapp_message(phone_number, 
                                "Fantastico! 📅 Qual è il momento della giornata in cui ci visiti più spesso?\n\n"
                                "1️⃣ Colazione 🥐☕\n"
                                "2️⃣ Pranzo 🍝🥗\n"
                                "3️⃣ Aperitivo 🍹🍕\n\n"
                                "Scrivi il numero corrispondente!")

                        elif session["step"] == "frequenza":
                            opzioni = {"1": "Colazione", "2": "Pranzo", "3": "Aperitivo"}
                            if text_received in opzioni:
                                session["frequenza"] = opzioni[text_received]
                                session["step"] = "compleanno"
                                send_whatsapp_message(phone_number, 
                                    "Super! 🎉 Quando è il tuo compleanno? (Formato: GG/MM) 🎂")
                            else:
                                send_whatsapp_message(phone_number, "Ops! Per favore, rispondi con 1, 2 o 3!")

                        elif session["step"] == "compleanno":
                            session["compleanno"] = text_received
                            session["step"] = "email"
                            send_whatsapp_message(phone_number, 
                                "Grazie! 🎁 Inviamo sorprese di compleanno, quindi segna questa data speciale! 🎂\n\n"
                                "Ora, se vuoi, lasciaci la tua email per ricevere aggiornamenti e offerte esclusive! 📩\n"
                                "(Scrivi 'No' se non vuoi fornire la tua email)")

                        elif session["step"] == "email":
                            session["email"] = text_received if text_received.lower() != "no" else None
                            send_whatsapp_message(phone_number, 
                                "Evviva! 🎉 Sei ufficialmente iscritto alla Fidelity! 🚀\n"
                                "Grazie per aver condiviso le tue info, ci vediamo presto! 🥰\n"
                                "Se hai domande, scrivici in qualsiasi momento! ❤️")
                            del user_sessions[phone_number]  # Termina la sessione

    return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
