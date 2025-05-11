import os
import time
import requests
from dotenv import load_dotenv

# Import your custom utilities
from utils.script_generator import generate_script_from_report
from utils.audio_generator import generate_audio
from utils.video_creator import generate_video
from utils.telegram_alert import send_telegram_message, send_telegram_file

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# File paths
PHASE_FILE = "output/phase.txt"
OFFSET_FILE = "output/last_update.txt"
GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"


# Phase management
def read_phase():
    if not os.path.exists(PHASE_FILE):
        return None
    with open(PHASE_FILE, "r") as f:
        return f.read().strip()

def write_phase(phase):
    with open(PHASE_FILE, "w") as f:
        f.write(phase)

def reset():
    if os.path.exists(PHASE_FILE):
        os.remove(PHASE_FILE)
    send_telegram_message("⛔ Process stopped and reset. You can restart anytime.")


# Core reply handler
def handle_reply(reply):
    phase = read_phase()

    if reply.lower() == "no":
        reset()
        return

    if phase == "awaiting_script" and reply.lower() == "yes":
        with open("output/report.txt", "r", encoding="utf-8") as f:
            report_text = f.read()
        script = generate_script_from_report(report_text)
        with open("output/final_script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        send_telegram_message("✍️ Script generated:")
        send_telegram_file("output/final_script.txt")
        write_phase("awaiting_audio")
        send_telegram_message("Reply 'yes' to generate audio.")

    elif phase == "awaiting_audio" and reply.lower() == "yes":
        with open("output/final_script.txt", "r", encoding="utf-8") as f:
            script = f.read()
        audio_path = generate_audio(script)
        send_telegram_file(audio_path, "🔊 Audio ready.")
        write_phase("awaiting_video")
        send_telegram_message("Reply 'yes' to generate video.")

    elif phase == "awaiting_video" and reply.lower() == "yes":
        with open("output/final_script.txt", "r", encoding="utf-8") as f:
            script = f.read()
        audio_path = "output/audio.mp3"
        video_path = generate_video(script, audio_path)
        send_telegram_file(video_path, "📽️ Final video generated.")
        os.remove(PHASE_FILE)
        send_telegram_message("✅ All steps completed successfully.")


# Telegram polling helpers
def get_last_update_id():
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            return int(f.read().strip())
    return None

def set_last_update_id(update_id):
    with open(OFFSET_FILE, "w") as f:
        f.write(str(update_id))


# Bot loop
def poll_replies():
    print("🤖 Telegram bot started. Waiting for replies...")
    while True:
        try:
            response = requests.get(GET_UPDATES_URL).json()
            updates = response.get("result", [])
            last_id = get_last_update_id()

            for update in updates:
                update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "")
                chat_id = message.get("chat", {}).get("id")

                if chat_id == int(TELEGRAM_CHAT_ID):
                    if last_id is None or update_id > last_id:
                        print(f"Received reply: {text}")
                        handle_reply(text)
                        set_last_update_id(update_id)

            time.sleep(5)

        except Exception as e:
            print(f"❌ Error in polling: {e}")
            time.sleep(10)


if __name__ == "__main__":
    poll_replies()