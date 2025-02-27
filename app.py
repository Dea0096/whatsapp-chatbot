import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Token di verifica (deve essere lo stesso di Meta)
VERIFY_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# Token di accesso API di WhatsApp
ACCESS_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# ID del numero di telefono di WhatsApp
PHONE_NUMBER_ID = "598409370016822"

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

# Endpoint per ricevere e rispondere ai messaggi WhatsApp
@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.get_json()
    print("Messaggio ricevuto:", data)  # Log dei messaggi nel terminale

    if "messages" in data["entry"][0]["changes"][0]["value"]:
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message.get("text", {}).get("body", "").strip()

        send_message(sender, f"Hai scritto: {text}")  # Rispondiamo con lo stesso testo ricevuto

    return jsonify({"status": "ricevuto"}), 200

# Funzione per inviare un messaggio di risposta su WhatsApp
def send_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=data)
    print("Risposta inviata:", response.json())

if __name__ == '__main__':
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=True)

