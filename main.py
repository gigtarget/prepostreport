import os
import time
import requests
from dotenv import load_dotenv

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import (
    overlay_date_on_template,
    overlay_text_lines_on_template,
    overlay_news_on_template
)
from utils.script_generator import generate_script_from_report
from utils.audio_generator import generate_audio
from utils.video_creator import generate_video
from utils.telegram_alert import send_telegram_message, send_telegram_file

# Load environment variables
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
OFFSET_FILE = "output/last_update.txt"
LOCK_FILE = "output/.lock"

def wait_for_telegram_reply(prompt_text="Reply 'yes' to continue"):
    send_telegram_message(prompt_text)
    last_update_id = None
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            last_update_id = f.read().strip()

    while True:
        try:
            params = {"timeout": 30}
            if last_update_id:
                params["offset"] = int(last_update_id) + 1

            res = requests.get(GET_UPDATES_URL, params=params)
            data = res.json()
            for result in data.get("result", []):
                last_update_id = result["update_id"]
                message_text = result["message"]["text"].strip().lower()
                with open(OFFSET_FILE, "w") as f:
                    f.write(str(last_update_id))
                if message_text == "yes":
                    return True
                else:
                    send_telegram_message("❌ Not approved. Waiting for 'yes'...")
            time.sleep(5)
        except Exception as e:
            send_telegram_message(f"⚠️ Error waiting for reply: {e}")
            time.sleep(5)

def generate_full_report():
    report = []

    report.append("📊 Indian Market:")
    nifty = get_yahoo_price_with_change("^NSEI", "NIFTY 50")
    sensex = get_yahoo_price_with_change("^BSESN", "SENSEX")
    banknifty = get_yahoo_price_with_change("^NSEBANK", "BANK NIFTY")
    report += [nifty, sensex, banknifty]

    report.append("\n🌍 Global Markets:")
    report.append(get_yahoo_price_with_change("^DJI", "Dow Jones"))
    report.append(get_yahoo_price_with_change("^IXIC", "NASDAQ"))
    report.append(get_yahoo_price_with_change("^FTSE", "FTSE 100"))
    report.append(get_yahoo_price_with_change("^N225", "Nikkei 225"))

    report.append("\n📰 Market News:")
    report += get_et_market_articles()

    return report

def main():
    if os.path.exists(LOCK_FILE):
        print("🛑 Script already ran. Skipping to save API usage.")
        return
    os.makedirs("output", exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write("locked")

    report = generate_full_report()

    # Generate and send images
    date_img = overlay_date_on_template()
    summary_img = overlay_text_lines_on_template(report)
    news_img = overlay_news_on_template(report)

    send_telegram_file(date_img, "🗓️ Date Image")
    send_telegram_file(summary_img, "📈 Market Summary")
    send_telegram_file(news_img, "📰 News Summary")

    if not wait_for_telegram_reply("🕹️ Proceed to generate script? Reply 'yes'"):
        return

    script_path, script_text = generate_script_from_report(report)
    send_telegram_message(f"📝 Generated Script:\n\n{script_text}")

    if not wait_for_telegram_reply("▶️ Proceed to generate audio? Reply 'yes'"):
        return

    audio_path = generate_audio(script_text)
    send_telegram_file(audio_path, "🎤 Audio Generated")

    if not wait_for_telegram_reply("🎬 Proceed to generate video? Reply 'yes'"):
        return

    video_path = generate_video(script_path, audio_path)
    send_telegram_file(video_path, "✅ Final Video")

if __name__ == "__main__":
    main()
