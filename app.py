from flask import Flask, request
import requests
import json

app = Flask(__name__)

ACCESS_TOKEN = "EAAQaZCVgHS2IBO4quQ2PbkR2ePEXvtZBsJQ4RsCoRCXZBjukriKzJ7wFUZBnomQGuLE7AKhsFsI6oRcfPWJPvchk8zSVmObaCoppZBlpmuZBEIsZB4xri6Ec3M7xbelWhyS4m1HwSlofhkvh693G1mCZAeAJu8xPZBlGKllySmmdPH0hKZAFO3X73sqy9Q1TcugiMwIOokZCGKcbRf2hpVZCn4JHemPZBoGBZA0NT6GFhDXykY"
VERIFY_TOKEN = "whatsapp_token"

# Memorizziamo gli utenti che hanno già iniziato la registrazione
user_sessions = {}

@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403
    
    elif request.method == "POST":
        data = request.get_json()
        print("🔍 Debug: JSON ricevuto da WhatsApp:")
        print(json.dumps(data, indent=2))
        
        if "entry" in data:
            for entry in data["entry"]:
                for change in entry["changes"]:
                    if "messages" in change["value"]:
                        message_data = change["value"]["messages"][0]
                        sender_id = message_data["from"]
                        message_text = message_data["text"]["body"].strip().lower()
                        
                        if sender_id not in user_sessions:
                            user_sessions[sender_id] = {"step": "start"}
                        
                        process_message(sender_id, message_text)
        
        return "OK", 200


def process_message(sender_id, message_text):
    step = user_sessions[sender_id]["step"]
    
    if step == "start":
        if "fidelity" in message_text:
            send_message(sender_id, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family con la Fidelity Card 🎉 Ti farò qualche domandina per completare l’iscrizione, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo!")
            user_sessions[sender_id]["step"] = "ask_name"
    
    elif step == "ask_name":
        user_sessions[sender_id]["name"] = message_text
        send_message(sender_id, "Dimmi la tua data di nascita in formato GG/MM/AAAA 🎂✨ Così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
        user_sessions[sender_id]["step"] = "ask_birthdate"
    
    elif step == "ask_birthdate":
        user_sessions[sender_id]["birthdate"] = message_text
        send_message(sender_id, "E tu di dove sei? 🏡 Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗✨")
        user_sessions[sender_id]["step"] = "ask_city"
    
    elif step == "ask_city":
        user_sessions[sender_id]["city"] = message_text
        send_message(sender_id, "Ultima domanda! 😍 Quando passi più spesso a trovarci? ☕🍽️🍹 [Colazione - Pranzo - Aperitivo]")
        user_sessions[sender_id]["step"] = "ask_visit_time"
    
    elif step == "ask_visit_time":
        user_sessions[sender_id]["visit_time"] = message_text
        send_message(sender_id, "Ultima cosa! Se vuoi ricevere offerte esclusive, lasciami la tua email 📩 Ma solo se ti fa piacere! 💛")
        user_sessions[sender_id]["step"] = "ask_email"
    
    elif step == "ask_email":
        user_sessions[sender_id]["email"] = message_text
        send_message(sender_id, "Ecco fatto! 🎉 Sei ufficialmente parte della nostra family! 💛 Non vediamo l’ora di vederti da noi! ☕🥐🍹💖 A prestissimo! 😘")
        del user_sessions[sender_id]  # Reset sessione


def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient_id,
        "type": "text",
        "text": {"body": text}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("📨 Debug: Messaggio inviato a WhatsApp:")
    print(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
