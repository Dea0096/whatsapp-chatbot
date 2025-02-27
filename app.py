from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = "EAAQaZCVgHS2IBO4quQ2PbkR2ePEXvtZBsJQ4RsCoRCXZBjukriKzJ7wFUZBnomQGuLE7AKhsFsI6oRcfPWJPvchk8zSVmObaCoppZBlpmuZBEIsZB4xri6Ec3M7xbelWhyS4m1HwSlofhkvh693G1mCZAeAJu8xPZBlGKllySmmdPH0hKZAFO3X73sqy9Q1TcugiMwIOokZCGKcbRf2hpVZCn4JHemPZBoGBZA0NT6GFhDXykY"
VERIFY_TOKEN = "whatsapp-bot-verification"
WHATSAPP_API_URL = "https://graph.facebook.com/v18.0/me/messages"

# Memoria delle conversazioni
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
    
    data = request.json
    print("Messaggio ricevuto:", data)
    
    if "entry" in data:
        for entry in data["entry"]:
            for change in entry["changes"]:
                if "messages" in change["value"]:
                    process_message(change["value"])
    
    return "OK", 200

def process_message(message_data):
    sender_id = message_data["contacts"][0]["wa_id"]
    message = message_data["messages"][0]
    text = message.get("text", {}).get("body", "").strip().lower()
    
    if sender_id not in user_sessions:
        user_sessions[sender_id] = {"step": "start", "data": {}}
    
    session = user_sessions[sender_id]
    step = session["step"]
    
    if step == "start" and text == "fidelity":
        send_whatsapp_message(sender_id, "Ehi! 🥰 Che bello averti qui! Sei a un passo dall’entrare nella nostra family con la Fidelity Card 🎉 Ti farò qualche domandina per completare l’iscrizione, giuro che sarà veloce e indolore 😜 Pronto/a? Partiamo!")
        session["step"] = "ask_name"
    elif step == "ask_name":
        session["data"]["name"] = text
        send_whatsapp_message(sender_id, f"Dimmi il tuo nome e cognome, così posso registrarti correttamente ✨ (Se vuoi, puoi dirmi anche il tuo soprannome! Qui siamo tra amici 💛)")
        session["step"] = "ask_birthday"
    elif step == "ask_birthday":
        session["data"]["birthday"] = text
        send_whatsapp_message(sender_id, f"Grazie, {session['data']['name']}! Ora dimmi quando spegni le candeline 🎂✨ Scrivimi la tua data di nascita in formato GG/MM/AAAA, così possiamo prepararti un pensiero speciale nel tuo giorno! 🎁")
        session["step"] = "ask_city"
    elif step == "ask_city":
        session["data"]["city"] = text
        send_whatsapp_message(sender_id, f"E tu di dove sei, {session['data']['name']}? 🏡 Dimmi la tua città, così so da dove vieni quando passi a trovarci! 🚗✨")
        session["step"] = "ask_visit"
    elif step == "ask_visit":
        session["data"]["visit"] = text
        send_whatsapp_message(sender_id, f"Ultima domanda e poi siamo ufficialmente best friends, {session['data']['name']}! 😍 Quando passi più spesso a trovarci? ☕🍽️🍹")
        session["step"] = "ask_email"
    elif step == "ask_email":
        session["data"]["email"] = text
        send_whatsapp_message(sender_id, f"Ecco fatto, {session['data']['name']}! 🎉 Sei ufficialmente parte della nostra family! 💛 La tua Fidelity Card è attivata e presto riceverai sorprese e vantaggi esclusivi! 🎫✨")
        session["step"] = "done"

def send_whatsapp_message(recipient_id, message_text):
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient_id,
        "type": "text",
        "text": {"body": message_text}
    }
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    print("Risposta inviata:", response.status_code, response.text)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
