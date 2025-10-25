import os
import requests
import time
from datetime import datetime, timedelta, timezone

# === Environment variables ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    raise ValueError("❌ BOT_TOKEN and CHAT_ID must be set as environment variables")

# === URL to monitor ===
URL = "https://ksp.co.il/m_action/api/category/?search=Phantasmal%20Flames"

# === State memory ===
last_total = None
last_daily_date = None

# === Israel time zone (UTC+3) ===
ISRAEL_TZ = timezone(timedelta(hours=3))

def send_telegram_message(message: str):
    """Send a message via Telegram bot"""
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message},
            timeout=10
        )
    except Exception as e:
        print(f"⚠️ Failed to send Telegram message: {e}")

def is_11am_israel():
    """Check if it's around 11:00 AM Israel time"""
    now = datetime.now(ISRAEL_TZ)
    return now.hour == 11 and now.minute < 5  # 5-minute grace window

def check_ksp():
    """Check KSP API and send alerts"""
    global last_total, last_daily_date

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/117.0.0.0 Safari/537.36"
        }

        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Correct path to products_total
        total = data.get("result", {}).get("products_total", None)

        if total is None:
            print("Could Not Find Phantasmal Flames Products.")
            return

        now_date = datetime.now(ISRAEL_TZ).date()

        # First run
        if last_total is None:
            if total > 0:
                send_telegram_message(f"🔥 Found {total} products for 'Phantasmal Flames' on first check!")
            else:
                print(f"Initial check: no products (products_total={total})")
            last_total = total
            last_daily_date = now_date
            return

        # Changed
        if total != last_total:
            change = total - last_total
            direction = "📈 increased" if change > 0 else "📉 decreased"
            send_telegram_message(f"⚡ Products total {direction} to {total} for 'Phantasmal Flames'.")
            last_total = total
            last_daily_date = now_date

        # Daily reminder at 11 AM Israel time
        elif is_11am_israel() and last_daily_date != now_date:
            send_telegram_message(f"🕒 Daily update: {total} products currently for 'Phantasmal Flames'.")
            last_daily_date = now_date
            print("✅ Daily update sent.")
        else:
            print(f"No change (products_total={total})")

    except Exception as e:
        send_telegram_message(f"❌ Error checking KSP: {e}")


def main():
    print("🔍 Starting KSP monitor bot (daily 11 AM Israel reminder)...")
    while True:
        check_ksp()
        time.sleep(300)  # every 5 minutes

if __name__ == "__main__":
    main()

