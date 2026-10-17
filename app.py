import os
import threading
import time
import requests
from flask import Flask, request

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN", "EAAMi3ZByHqCQBS3zv6PpwzxkewSRQLaZCdhj8zwsqNrZCiR7C8Ntv7Ql22peU58lDNlbyi8cJRhZBnDtCeNsqEZCRc8sXL4w6efEFjZCFkMDTuHGj1pfL8BRH9MfUJYhC6GB7Dnl8lcv4rbWAUWeVs9tbbAZAIACl2ZCZCWQZC3kY4eOtVc7BRACEgXb8apPcFV05ZCRx0lbYo9AwZDZD")
VERIFY_TOKEN = os.environ.get(
    "VERIFY_TOKEN", "handsomebot_verify_token_123"
)
RENDER_URL = os.environ.get("RENDER_URL", "https://loyalmate.onrender.com/")


# রেন্ডারের স্লিপ মোড প্রতিরোধের সেলফ-পিং ফাংশন
def self_ping():
  while True:
    try:
      response = requests.get(RENDER_URL)
      print(f"Self-ping sent! Status Code: {response.status_code}")
    except Exception as e:
      print(f"Self-ping error: {e}")
    time.sleep(300)  # প্রতি ৫ মিনিট পরপর পিং করবে


# ব্যাকগ্রাউন্ডে থ্রেড শুরু করা
threading.Thread(target=self_ping, daemon=True).start()


@app.route("/")
def home():
  return "Loyaltmate Flask Server is Alive!"


@app.route("/webhook", methods=["GET"])
def verify_webhook():
  mode = request.args.get("hub.mode")
  token = request.args.get("hub.verify_token")
  challenge = request.args.get("hub.challenge")

  if mode and token:
    if mode == "subscribe" and token == VERIFY_TOKEN:
      print("WEBHOOK_VERIFIED")
      return challenge, 200
    else:
      return "Verification failed", 403
  return "Hello world", 200


@app.route("/webhook", methods=["POST"])
def handle_webhook():
  data = request.get_json()
  print(f"Received webhook data: {data}")

  if data.get("object") == "page":
    for entry in data.get("entry", []):
      for messaging_event in entry.get("messaging", []):
        sender_id = messaging_event.get("sender", {}).get("id")

        # যদি ইউজার কোনো টেক্সট মেসেজ পাঠায়
        if messaging_event.get("message") and messaging_event["message"].get(
            "text"
        ):
          message_text = messaging_event["message"]["text"]
          print(f"Message received from {sender_id}: {message_text}")

          # অটো-রিপ্লাই পাঠানো
          send_reply(
              sender_id,
              f"ধন্যবাদ! আপনার মেসেজটি পেয়েছি: '{message_text}'. Loyaltmate"
              " স্টোরে আপনাকে স্বাগতম!",
          )

    return "EVENT_RECEIVED", 200
  return "Not Found", 404


def send_reply(recipient_id, text):
  url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}"
  payload = {"recipient": {"id": recipient_id}, "message": {"text": text}}
  response = requests.post(url, json=payload)
  print(f"Send reply response: {response.status_code}, {response.text}")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=10000)
