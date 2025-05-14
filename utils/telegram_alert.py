import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Telegram credentials missing.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("📬 Telegram message sent.")
    except Exception as e:
        print(f"❌ Telegram message failed: {e}")

def send_telegram_file(filepath, caption=None):
    if not BOT_TOKEN or not CHAT_ID or not os.path.exists(filepath):
        print(f"⚠️ File missing or Telegram credentials not set: {filepath}")
        return

    ext = filepath.split(".")[-1].lower()
    file_field = {
        "mp4": "video",
        "png": "photo",
        "jpg": "photo",
        "jpeg": "photo",
        "mp3": "audio"
    }.get(ext, "document")

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/send{file_field.capitalize()}"
    with open(filepath, "rb") as f:
        files = {file_field: f}
        data = {"chat_id": CHAT_ID}
        if caption:
            data["caption"] = caption
        try:
            r = requests.post(url, data=data, files=files)
            r.raise_for_status()
            print(f"📤 Sent {file_field}: {filepath}")
        except Exception as e:
            print(f"❌ Failed to send file: {e}")
