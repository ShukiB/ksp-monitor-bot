# 🔥 KSP Product Monitor Bot

This Python bot checks the KSP API every 5 minutes for product availability and sends Telegram alerts.

---

## 🚀 Features
- Alerts when `products_total` changes
- Sends daily 11AM Israel-time status updates
- Runs 24/7 for free on Render
- No local storage — real-time only

---

## 🧰 Setup

### 1️⃣ Create a Telegram bot
- Open Telegram → search for **@BotFather**
- Run `/newbot` → follow prompts
- Copy your bot token

### 2️⃣ Get your chat ID
Send any message to your bot, then open:

https://api.telegram.org/bot/<YOUR_TOKEN>/getUpdates

Look for `"chat":{"id":YOUR_CHAT_ID}`

---

## ☁️ Deploy on Render

1. Fork this repo to your GitHub
2. Go to [https://render.com](https://render.com)
3. **New + → Web Service**
4. Connect your repo
5. Fill in:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python ksp_monitor.py`
   - **Instance Type**: `Free`
6. Add **Environment Variables**:
   - `BOT_TOKEN` = your bot token  
   - `CHAT_ID` = your chat ID  
7. Click **Deploy**

---

## 🕹️ Start / Stop
- **Start** → click **Resume Service**  
- **Stop** → click **Suspend Service**

---

## 🧩 Example Alerts

