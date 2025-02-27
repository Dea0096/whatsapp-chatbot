import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Token di verifica per Meta
VERIFY_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# Token di accesso API di WhatsApp
ACCESS_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# ID del numero di telefono di WhatsApp
PHONE_NUMBER_ID = "598409370016822"

# Memoria conversazioni utenti (simuliamo un database temporaneo)
user_sessions = {}

# Endpoint di verifica del Webhook
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Token non valido", 403

# Endpoint per ricevere e gestire i messaggi
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()

    if "messages" in data["entry"][0]["changes"][0]["value"]:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message.get("text", {}).get("body", "").strip().upper()

        # Se il messaggio è "FIDELITY", iniziamo la registrazione
        if text == "FIDELITY":
            user_sessions[sender] = {"step": 1}
            send_message(sender, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family con la Fidelity Card 🎉 Ti farò qualche domandina per completare l’iscrizione, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo!\n\nDimmi il tuo nome e cognome! (Se vuoi, puoi dirmi anche il tuo soprannome!) 💛")
            return jsonify({"status": "started"}), 200

        # Se l'utente è in sessione, gestiamo i passaggi
        if sender in user_sessions:
            step = user_sessions[sender]["step"]

            if step == 1:
                user_sessions[sender]["name"] = text
                user_sessions[sender]["step"] = 2
                send_message(sender, f"Grazie, {text}! Ora dimmi la tua data di nascita 🎂 (Formato GG/MM/AAAA) 🎁")
            
            elif step == 2:
                user_sessions[sender]["dob"] = text
                user_sessions[sender]["step"] = 3
                send_message(sender, f"E tu di dove sei, {user_sessions[sender]['name']}? 🏡 Dimmi la tua città! 🚗✨")

            elif step == 3:
                user_sessions[sender]["city"] = text
                user_sessions[sender]["step"] = 4
                send_interactive_message(sender, f"Ultima domanda, {user_sessions[sender]['name']}! Quando passi più spesso a trovarci? ☕🍽️🍹")

            elif step == 4:
                user_sessions[sender]["preference"] = text
                user_sessions[sender]["step"] = 5
                send_message(sender, f"Ultima cosa, {user_sessions[sender]['name']}! Se vuoi ricevere offerte esclusive, lasciami la tua email 📩 (Solo se ti fa piacere!) 💛")

            elif step == 5:
                user_sessions[sender]["email"] = text
                send_message(sender, f"Ecco fatto, {user_sessions[sender]['name']}! 🎉 Sei ufficialmente parte della nostra family! La tua Fidelity Card è attivata! 🎫✨ A presto! ☕🥐🍹💖")
                del user_sessions[sender]  # Rimuove l'utente dalla sessione dopo la registrazione

    return jsonify({"status": "received"}), 200

# Funzione per inviare un messaggio semplice su WhatsApp
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {"messaging_product": "whatsapp", "to": to, "text": {"body": text}}
    requests.post(url, headers=headers, json=data)

# Funzione per inviare messaggi interattivi con pulsanti
def send_interactive_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {"buttons": [{"type": "reply", "reply": {"id": "colazione", "title": "☕ Colazione"}},
                                   {"type": "reply", "reply": {"id": "pranzo", "title": "🍽️ Pranzo"}},
                                   {"type": "reply", "reply": {"id": "aperitivo", "title": "🍹 Aperitivo"}}]}
        }
    }
    requests.post(url, headers=headers, json=data)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
