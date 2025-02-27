from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

# Token di verifica di WhatsApp
VERIFY_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# Endpoint Webhook per la verifica
@app.route('/webhook', methods=['GET'])
def verify():
    """Verifica la connessione al webhook con il token di verifica"""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("✅ Webhook verificato con successo!")
        return challenge, 200
    else:
        print("❌ Verifica fallita. Token errato.")
        return "Errore di verifica", 403

# Endpoint Webhook per ricevere messaggi
@app.route('/webhook', methods=['POST'])
def webhook():
    """Riceve i messaggi da WhatsApp e risponde se necessario"""
    data = request.json
    print("📩 Dati ricevuti:\n", json.dumps(data, indent=2))  # Log completo dei dati ricevuti

    try:
        # Estrarre i dettagli del messaggio ricevuto
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    value = change.get("value", {})
                    messages = value.get("messages", [])

                    for message in messages:
                        sender_id = message["from"]  # Numero di chi scrive
                        msg_text = message["text"]["body"].strip().lower()  # Testo del messaggio

                        print(f"📨 Messaggio ricevuto da {sender_id}: {msg_text}")

                        if msg_text == "fidelity":
                            reply_text = "Ehi! 😊 Ti piacerebbe far parte del nostro programma fedeltà? Ti chiederò qualche info per iniziare! 🎉\n\nCome ti chiami?"
                            send_whatsapp_message(sender_id, reply_text)
                        else:
                            print("🔍 Messaggio ignorato: non è 'fidelity'")

    except Exception as e:
        print("⚠️ Errore nella gestione del messaggio:", str(e))

    return jsonify({"status": "received"}), 200

def send_whatsapp_message(recipient_id, message):
    """Invia un messaggio di risposta su WhatsApp"""
    url = "https://graph.facebook.com/v17.0/598409370016822/messages"
    headers = {
        "Authorization": f"Bearer {VERIFY_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=payload)
    print(f"📤 Risposta inviata a {recipient_id}: {message}")
    print("📡 Status della richiesta:", response.status_code, response.text)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
