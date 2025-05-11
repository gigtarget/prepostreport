import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

LAST_UPDATE_FILE = "output/last_update_id.txt"

def get_last_update_id():
    if os.path.exists(LAST_UPDATE_FILE):
        with open(LAST_UPDATE_FILE, "r") as f:
            return int(f.read().strip())
    return None

def save_last_update_id(update_id):
    with open(LAST_UPDATE_FILE, "w") as f:
        f.write(str(update_id))

def check_for_yes_reply():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    params = {"timeout": 10}
    last_id = get_last_update_id()
    if last_id:
        params["offset"] = last_id + 1

    response = requests.get(url, params=params)
    data = response.json()

    if not data.get("ok"):
        print("❌ Error fetching Telegram updates.")
        return False

    for update in data.get("result", []):
        update_id = update["update_id"]
        message = update.get("message", {}).get("text", "").strip().lower()
        if message == "yes":
            print("✅ Approval received!")
            os.system("python3 main_phase2.py")
            save_last_update_id(update_id)
            return True
        save_last_update_id(update_id)
    return False

if __name__ == "__main__":
    print("⏳ Waiting for approval message (type 'yes')...")
    while True:
        approved = check_for_yes_reply()
        if approved:
            break
        time.sleep(15)
