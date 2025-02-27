from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "WhatsApp Chatbot is running!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        return "Webhook configurato correttamente!", 200
    elif request.method == "POST":
        data = request.get_json()
        print("🔹 Dati ricevuti:", data)

        # Controlla se ci sono messaggi
        if data and "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    message = change.get("value", {}).get("messages", [{}])[0]
                    if "text" in message:
                        text = message["text"]["body"].strip().lower()
                        sender_id = message["from"]

                        # Risponde solo se il messaggio è "fidelity"
                        if text == "fidelity":
                            send_message(sender_id, "🎉 Ehi! Vuoi la nostra fidelity card? Cominciamo con qualche info!")

        return jsonify({"status": "received"}), 200

def send_message(to, message):
    print(f"📨 Inviando messaggio a {to}: {message}")
    # Qui dovresti implementare l'invio del messaggio via API di WhatsApp

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=10000)  # 🔹 IMPORTANTE: Porta corretta su Render!
