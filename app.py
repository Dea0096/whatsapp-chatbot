import os
import json
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "mio_verification_token"
ACCESS_TOKEN = "EAAQaZCVgHS2IBO4quQ2PbkR2ePEXvtZBsJQ4RsCoRCXZBjukriKzJ7wFUZBnomQGuLE7AKhsFsI6oRcfPWJPvchk8zSVmObaCoppZBlpmuZBEIsZB4xri6Ec3M7xbelWhyS4m1HwSlofhkvh693G1mCZAeAJu8xPZBlGKllySmmdPH0hKZAFO3X73sqy9Q1TcugiMwIOokZCGKcbRf2hpVZCn4JHemPZBoGBZA0NT6GFhDXykY"

users_state = {}

def send_whatsapp_message(phone_number, message):
    url = "https://graph.facebook.com/v17.0/598409370016822/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print(f"Invio messaggio a {phone_number}: {message}")
    print(f"Risposta API: {response.json()}")
    return response.json()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def handle_messages():
    data = request.get_json()
    print(f"Messaggio ricevuto: {json.dumps(data, indent=2)}")  # DEBUG

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                value = change.get("value", {})
                messages = value.get("messages", [])
                
                for message in messages:
                    phone_number = message["from"]
                    text = message["text"]["body"].strip().lower()

                    # Se l'utente ha già avviato la registrazione, segui il flusso
                    if phone_number in users_state:
                        if users_state[phone_number]["step"] == "name":
                            users_state[phone_number]["name"] = text
                            send_whatsapp_message(phone_number, f"Grazie, {text}! Ora dimmi quando spegni le candeline 🎂✨ Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
                            users_state[phone_number]["step"] = "birthday"
                        
                        elif users_state[phone_number]["step"] == "birthday":
                            users_state[phone_number]["birthday"] = text
                            send_whatsapp_message(phone_number, f"E tu di dove sei? 🏡 Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗✨")
                            users_state[phone_number]["step"] = "city"

                        elif users_state[phone_number]["step"] == "city":
                            users_state[phone_number]["city"] = text
                            send_whatsapp_message(phone_number, f"Ultima domanda e poi siamo ufficialmente best friends, {nome}! 😍 Quando passi più spesso a trovarci? Ti accogliamo con il profumo del caffè al mattino, con un piatto delizioso a pranzo o con un drink perfetto per l’aperitivo? ☕🍽️🍹")
                            users_state[phone_number]["step"] = "visit_time"

                        elif users_state[phone_number]["step"] == "email":
                            users_state[phone_number]["email"] = text
                            send_whatsapp_message(phone_number, f"Ecco fatto! 🎉 Sei ufficialmente parte della nostra family! 💛 La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! 🎫✨ Non vediamo l’ora di vederti da noi! Quasi dimenticavo! Se vuoi ricevere offerte e sorprese esclusive (tranquillo/a, niente spam! 🤞), lasciami la tua email 📩 Ma solo se ti fa piacere! 💛")
                            del users_state[phone_number]  # Reset utente dopo la registrazione

                    # Se l'utente scrive "FIDELITY", avvia il flusso
                    elif text == "fidelity":
                        users_state[phone_number] = {"step": "name"}
                        send_whatsapp_message(phone_number, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family 🎉 Qualche domandina per la fidelity, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo! nome e cognome, così posso registrarti correttamente ✨ (Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛")
    
    return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
