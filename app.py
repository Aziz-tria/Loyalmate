import os
import time
import threading
import requests
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "YOUR_PAGE_ACCESS_TOKEN_HERE")
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "handsomebot_verify_token_123")
RENDER_URL = os.environ.get("RENDER_URL", "https://loyalmate.onrender.com/")

# ফেক অর্ডার ডাটা (গ্লাস মফিজম ড্যাশবোর্ডের জন্য)
FAKE_ORDERS = [
    {
        "id": 1,
        "fb_name": "Tanvir Ahmed",
        "customer_name": "তানভীর আহমেদ",
        "location": "টঙ্গী, গাজীপুর",
        "product": "Zero Energy Drink (Pack of 4)",
        "color": "Deep Violet",
        "time": "10 mins ago"
    },
    {
        "id": 2,
        "fb_name": "Rashed Khan",
        "customer_name": "রাশেদ খান",
        "location": "উত্তরা, ঢাকা",
        "product": "Zero Energy Drink (Special Edition)",
        "color": "Neon Blue",
        "time": "25 mins ago"
    },
    {
        "id": 3,
        "fb_name": "Sumaiya Akter",
        "customer_name": "সুমাইয়া আক্তার",
        "location": "বনানী, ঢাকা",
        "product": "Zero Energy Drink (Classic)",
        "color": "Dark Purple",
        "time": "1 hour ago"
    }
]

# সেলফ-পিং ফাংশন: প্রতি ১০ মিনিট পর পর নিজের সাইটে রিকোয়েস্ট পাঠিয়ে সজাগ রাখবে
def self_ping():
    while True:
        try:
            time.sleep(600)  # ১০ মিনিট (৬০০ সেকেন্ড) পর পর রান হবে
            response = requests.get(RENDER_URL)
            print(f"Self-ping sent! Status Code: {response.status_code}")
        except Exception as e:
            print(f"Self-ping failed: {e}")

# ব্যাকগ্রাউন্ডে পিং করার জন্য থ্রেড স্টার্ট করা
threading.Thread(target=self_ping, daemon=True).start()

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", orders=FAKE_ORDERS)

# Webhook Verification (Meta)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403
    return "Hello World", 200

# Webhook for Messenger
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                if messaging_event.get("message") and messaging_event["message"].get("text"):
                    message_text = messaging_event["message"]["text"]
                    send_message(sender_id, f"ধন্যবাদ! আপনার মেসেজটি পেয়েছি: '{message_text}'. Loyaltmate স্টোরে আপনাকে স্বাগতম!")
        return "EVENT_RECEIVED", 200
    return "Not Found", 404

def send_message(recipient_id, message_text):
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    requests.post(url, json=payload)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
