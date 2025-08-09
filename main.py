import imaplib
import email
from email.header import decode_header
import time
import ssl
import telebot
from datetime import datetime
import threading

# IMAP mail server configuration (Gmail)
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
FILTER_SENDER = "sender@example.com"

# Telegram bot configuration
TELEGRAM_BOT_TOKEN = "your-telegram-bot-token"
TELEGRAM_CHAT_ID = "your-telegram-chat-id"

CHECK_INTERVAL = 10  # seconds

bot = None

def init_bot():
    """Initialize the Telegram bot."""
    global bot
    try:
        bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
        setup_bot_handlers()
        return True
    except Exception as e:
        print(f"[Telegram] Bot initialization error: {e}")
        return False

def clean_text(text):
    if isinstance(text, bytes):
        text = text.decode(errors='ignore')
    return text

def send_telegram_message(message):
    """Send a message to the configured Telegram chat."""
    try:
        if len(message) > 4000:
            message = message[:4000] + "\n\n[Message truncated...]"
        
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        
    except telebot.apihelper.ApiTelegramException as e:
        print(f"[Telegram] API error: {e}")
    except Exception as e:
        print(f"[Telegram] Error sending message: {e}")

def test_telegram_connection():
    """Send a test message to confirm Telegram bot connection."""
    try:
        test_message = f"""🔔 <b>Email Monitoring Started</b>

📧 <b>Account:</b> {EMAIL_ACCOUNT}
📨 <b>Sender Filter:</b> {FILTER_SENDER}
⏰ <b>Start Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 <b>Check Interval:</b> {CHECK_INTERVAL} sec"""
        
        send_telegram_message(test_message)
        return True
        
    except telebot.apihelper.ApiTelegramException as e:
        print(f"[Telegram] API test error: {e}")
        return False
    except Exception as e:
        print(f"[Telegram] Test connection error: {e}")
        return False

def test_connection():
    """Test IMAP email server connection."""
    try:
        print(f"Connecting to {IMAP_SERVER}:{IMAP_PORT}...")
        
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        mail.logout()
        return True
        
    except Exception:
        return False

def escape_html(text):
    """Escape HTML characters for safe Telegram message formatting."""
    if not text:
        return ""
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def check_mail():
    """Check for new emails and send them to Telegram."""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT, ssl_context=context)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, '(UNSEEN)')

        if not messages[0]:
            return

        for num in messages[0].split():
            status, msg_data = mail.fetch(num, '(RFC822)')
            if status != "OK":
                print(f"Error fetching email {num}")
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            from_ = msg.get("From")
            subject = msg.get("Subject")
            date = msg.get("Date")

            # Decode subject
            dh = decode_header(subject)[0]
            subject_decoded = dh[0]
            if isinstance(subject_decoded, bytes):
                subject_decoded = subject_decoded.decode(dh[1] if dh[1] else 'utf-8', errors='ignore')

            print(f"[Email] From: {from_}, Subject: {subject_decoded}")

            if FILTER_SENDER.lower() not in from_.lower():
                mail.store(num, '+FLAGS', '\\Seen')
                continue

            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_dispo = str(part.get("Content-Disposition"))

                    if content_type == "text/plain" and "attachment" not in content_dispo:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='ignore')
                        break
            else:
                charset = msg.get_content_charset() or 'utf-8'
                body = msg.get_payload(decode=True).decode(charset, errors='ignore')

            # Escape HTML
            from_escaped = escape_html(from_)
            subject_escaped = escape_html(subject_decoded)
            date_escaped = escape_html(date)
            body_escaped = escape_html(body)

            telegram_message = f"""📧 <b>New Email</b>

<b>From:</b> {from_escaped}
<b>Subject:</b> {subject_escaped}
<b>Date:</b> {date_escaped}

<b>Body:</b>
<pre>{body_escaped}</pre>"""

            print(f"New email from {from_}\nSubject: {subject_decoded}\n\nBody:\n{body}")
            print("-" * 50)
            
            send_telegram_message(telegram_message)
            
            mail.store(num, '+FLAGS', '\\Seen')

        mail.logout()

    except Exception as e:
        print(f"[Error] While checking email: {e}")
        error_message = f"""❌ <b>Email Monitoring Error</b>

<pre>{escape_html(str(e))}</pre>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
        send_telegram_message(error_message)

def setup_bot_handlers():
    """Set up Telegram bot commands."""
    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        welcome_text = f"""👋 <b>Hi! I am your Email Monitoring Bot</b>

📧 <b>Monitoring Account:</b> {EMAIL_ACCOUNT}
📨 <b>Sender Filter:</b> {FILTER_SENDER}
🔄 <b>Check Interval:</b> {CHECK_INTERVAL} sec

<b>Available Commands:</b>
/start - Show this message
/status - Show monitoring status
/stop - Stop monitoring (admin only)"""
        
        bot.reply_to(message, welcome_text, parse_mode='HTML')

    @bot.message_handler(commands=['status'])
    def send_status(message):
        status_text = f"""📊 <b>Monitoring Status</b>

✅ <b>Status:</b> Active
📧 <b>Account:</b> {EMAIL_ACCOUNT}
📨 <b>Filter:</b> {FILTER_SENDER}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔄 <b>Interval:</b> {CHECK_INTERVAL} sec"""
        
        bot.reply_to(message, status_text, parse_mode='HTML')

def run_bot():
    try:
        if bot:
            print("[Telegram] Starting bot polling...")
            bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"[Telegram] Error running bot: {e}")

def main():
    global bot

    # Check Telegram config
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID_HERE":
        print("Please configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID!")
        return
    
    if not init_bot():
        print("Failed to initialize Telegram bot")
        return
    
    if not test_telegram_connection():
        print("Failed to connect to Telegram. Check bot token and chat ID.")
        return
    
    if not test_connection():
        print("\nFailed to connect to email. Possible reasons:")
        print("1. Check login and password")
        print("2. Enable IMAP in email settings")
        print("3. Create an app password (Gmail)")
        print("4. Disable 2FA or use an app-specific password")
        return
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    while True:
        try:
            check_mail()
            time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\n👋 Monitoring stopped by user")
            goodbye_message = f"""🛑 <b>Email Monitoring Stopped</b>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            send_telegram_message(goodbye_message)
            break
        except Exception as e:
            print(f"Critical error: {e}")
            error_message = f"""🚨 <b>Critical Monitoring Error</b>

<pre>{escape_html(str(e))}</pre>

⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            send_telegram_message(error_message)
            time.sleep(60)

if __name__ == "__main__":
    main()
