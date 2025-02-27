from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Token di verifica e accesso di WhatsApp
VERIFY_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"
PHONE_NUMBER_ID = "598409370016822"

# Webhook GET per verifica con Meta
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificato con successo!")
        return challenge, 200
    else:
        print("❌ Webhook: token di verifica non valido!")
        return "Forbidden", 403

# Webhook POST per ricevere messaggi WhatsApp
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("📩 Messaggio ricevuto:", data)  # LOG per debug

    if "entry" in data and "changes" in data["entry"][0]:
        message_info = data["entry"][0]["changes"][0]["value"]

        # Controlliamo se ci sono messaggi
        if "messages" in message_info:
            message = message_info["messages"][0]
            sender_id = message["from"]  # Numero del mittente
            text = message.get("text", {}).get("body", "").strip().lower()  # Testo del messaggio

            print(f"📥 Messaggio da {sender_id}: {text}")  # LOG

            # Se il messaggio è "fidelity", rispondiamo
            if text == "fidelity":
                send_whatsapp_message(sender_id, "Ciao! 🌟 Vuoi iscriverti al nostro programma Fidelity? Rispondi con 'Sì' per continuare!")
    
    return jsonify({"status": "received"}), 200

# Funzione per inviare un messaggio di risposta su WhatsApp
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {VERIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=data)
    print("📤 Risposta inviata:", response.json())  # LOG di debug

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000, debug=True)
