# 📧 Email-to-Telegram Monitor

A Python script that **monitors your Gmail inbox** and sends **instant notifications** to Telegram when new emails arrive from a specific sender.  
Perfect for **alerts, automated reporting, and monitoring**.

---

## ✨ Features

- 🔄 **Automatic email checking** using IMAP
- 📌 **Sender filtering** – only receive alerts from specific addresses
- 📱 **Telegram integration** – direct messages to your chosen chat
- 🖥 **Continuous background monitoring**
- 💬 **Telegram commands**:
  - `/start` – Show help
  - `/status` – Show monitoring status
  - `/stop` – Stop monitoring (admin only)

---

## 📸 Example Notification


📧 New Email

From: sender@example.com
Subject: Project Update
Date: Sat, 9 Aug 2025 12:34:56

Body:
Hello, here’s the latest update on our project...


---

## 🚀 Installation

1. **Clone this repository**  
git clone https://github.com/yourusername/email-to-telegram.git
cd email-to-telegram

2.pip install pyTelegramBotAPI

3.Enable Gmail IMAP access

Go to Gmail Settings → Forwarding and POP/IMAP

Enable IMAP

Create an App Password (for accounts with 2FA) in Google Account Security Settings

⚙️ Configuration
Edit main.py and set your credentials:

EMAIL_ACCOUNT = "youremail@gmail.com"
EMAIL_PASSWORD = "your-app-password"
FILTER_SENDER = "sender@example.com"

TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-chat-id"
CHECK_INTERVAL = 10  # seconds


▶️ Running
python main.py


The bot will:

- Connect to Gmail

- Start Telegram bot polling

- Send a startup notification

- Check for new filtered emails every CHECK_INTERVAL seconds

🛡 Security Notes
- Do not hardcode real passwords in public repos – use environment variables or .env files.

- This script currently disables SSL certificate verification for IMAP. Enable it in production.

- Keep your Telegram Bot Token and Gmail credentials private.

📄 License
MIT License – free to use, modify, and distribute.

⭐ Contribute
Fork this repository

Create a feature branch

Submit a pull request 🚀


If you want, I can now make **a `.env`-based secure version** of this code so you can push it to GitHub **without leaking your credentials**. That way, the README will also include `.env` setup instructions. Would you like me to do that?


