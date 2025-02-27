from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Token di accesso per WhatsApp (sostituisci con il tuo)
WHATSAPP_TOKEN = "EAAQaZCVgHS2IBO0ZCzCZAVrCZAZBZB2aMtn8oDkeM63RNAVWIms2ZBOshi4K5qWHfZCqiZBXuS2oeBwwrpPamfkaK62eZCpKZCW0xg66naP9tmYU6iFcjTF9sIDn2xPiKATlIfvpo5wyfNtmfOvceOfFD3XTv4Ysyjgkv2lHkVG8WxTi2u9Cb9vuPdIpcCKUMiCF7jAVwZAGQ4TEivII63cCcKGkJVbujakrZBltJn0GBAOkVrAZDZD"

# ID del numero di telefono collegato all'API di WhatsApp
PHONE_NUMBER_ID = "598409370016822"

@app.route('/webhook', methods=['POST'])
def webhook():
    """Gestisce i messaggi in entrata da WhatsApp."""
    data = request.json  # Riceve il JSON dalla richiesta
    print("📩 Messaggio ricevuto:", json.dumps(data, indent=2))  # Debug: stampa il JSON ricevuto

    # Controlla se ci sono messaggi validi nel payload ricevuto
    if 'entry' in data:
        try:
            message = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
            sender = data['entry'][0]['changes'][0]['value']['messages'][0]['from']
            print(f"📨 Messaggio ricevuto: {message} | Da: {sender}")

            # Controllo se il messaggio ricevuto è "fidelity"
            if message.lower() == "fidelity":
                response_text = "🎉 Benvenuto nel nostro programma Fidelity! Ti facciamo qualche domanda veloce 😊"
                send_whatsapp_message(sender, response_text)
                return jsonify({"status": "success", "message": "Risposta inviata"}), 200

        except KeyError as e:
            print("⚠️ Errore nel parsing del JSON:", str(e))
            return jsonify({"status": "error", "message": "Errore nel parsing JSON"}), 400

    return jsonify({"status": "error", "message": "Nessun messaggio trovato"}), 400

def send_whatsapp_message(phone, text):
    """Invia un messaggio WhatsApp utilizzando le API di Meta."""
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone,
        "text": {"body": text}
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print(f"✅ Messaggio inviato con successo a {phone}")
    else:
        print(f"❌ Errore nell'invio del messaggio: {response.text}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
