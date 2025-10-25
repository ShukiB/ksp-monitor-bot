import os
import requests
import time
from datetime import datetime, timedelta, timezone
from flask import Flask
import json

# === Environment variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PORT = int(os.getenv("PORT", 10000))  # Render assigns $PORT

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN and CHAT_ID must be set as environment variables")

# === URL to monitor ===
URL = "https://ksp.co.il/m_action/api/category/?search=Phantasmal%20Flames"

# === State memory ===
last_total = None
last_daily_date = None

# === Israel time zone (UTC+3) ===
ISRAEL_TZ = timezone(timedelta(hours=3))

# === Telegram alert ===
def send_telegram_message(message):
    try:
        # Convert dict/list to string safely
        if isinstance(message, (dict, list)):
            message = json.dumps(message, ensure_ascii=False, indent=2)
        print(f"📤 Sending Telegram message: {message}")
        response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message},
            timeout=10
        )
        print(f"📬 Telegram response: {response.status_code} {response.text}")
    except Exception as e:
        print(f"⚠️ Failed to send Telegram message: {e}")

def is_11am_israel():
    now = datetime.now(ISRAEL_TZ)
    return now.hour == 11 and now.minute < 5

# --- Add browser User-Agent to avoid 403 ---
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0.0.0 Safari/537.36"
    )
}

def check_ksp():
    global last_total, last_daily_date
    try:
        print(f"🔍 Checking KSP API at {datetime.now(ISRAEL_TZ)}")
        response = requests.get(URL, headers=HEADERS, timeout=10)
        print(f"📡 KSP response status: {response.status_code}")
        data = response.json()
        print(f"📄 KSP response JSON: {json.dumps(data, ensure_ascii=False, indent=2)}")

        # Correct path to products_total inside result
        total = data.get("result", {}).get("products_total", None)
        print(f"🧮 Extracted products_total: {total}")

        now_date = datetime.now(ISRAEL_TZ).date()

        # First run
        if last_total is None:
            if total is not None and total > 0:
                send_telegram_message(f"🔥 Found {total} products for 'Phantasmal Flames' on first check!")
            else:
                print("ℹ️ Initial check: no products")
            last_total = total
            last_daily_date = now_date
            return

        # Changed
        if total != last_total:
            change = (total - last_total) if total is not None else total
            direction = "📈 increased" if change and change > 0 else "📉 decreased"
            send_telegram_message(f"⚡ Products total {direction} to {total} for 'Phantasmal Flames'.")
            last_total = total
            last_daily_date = now_date

        # Daily 11AM Israel alert
        elif is_11am_israel() and last_daily_date != now_date:
            send_telegram_message(f"🕒 Daily update: {total} products currently for 'Phantasmal Flames'.")
            last_daily_date = now_date
            print("✅ Daily update sent.")
        else:
            print(f"ℹ️ No change (products_total={total})")

    except Exception as e:
        print(f"❌ Exception during check_ksp: {e}")
        send_telegram_message(f"❌ Error checking KSP: {e}")

# === Background loop ===
def background_loop():
    while True:
        check_ksp()
        print("⏳ Sleeping 5 minutes...\n")
        time.sleep(300)  # 5 minutes

# === Minimal HTTP server for Render ===
app = Flask(__name__)

@app.route("/")
def index():
    return "KSP Monitor is running 🚀"

if __name__ == "__main__":
    from threading import Thread
    # Start the background checker in a separate thread
    t = Thread(target=background_loop, daemon=True)
    t.start()
    # Start the web server so Render detects a bound port
    print(f"🌐 Starting Flask web service on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
