import os
import time
import requests
from dotenv import load_dotenv

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import create_combined_market_image
from utils.script_generator import generate_youtube_script_from_report as generate_script_from_report
from utils.audio_generator import generate_audio_with_polly as generate_audio
from utils.video_creator import create_video_from_images_and_audio as generate_video
from utils.telegram_alert import send_telegram_message, send_telegram_file

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
OFFSET_FILE = "output/last_update.txt"

def get_current_date_ist():
    from datetime import datetime
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def wait_for_telegram_reply(prompt_text=None):
    if prompt_text:
        send_telegram_message(prompt_text)

    last_update_id = 0
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE, "r") as f:
            last_update_id = int(f.read().strip())

    while True:
        try:
            response = requests.get(GET_UPDATES_URL, timeout=10).json()
            for result in response.get("result", []):
                update_id = result["update_id"]
                message = result.get("message", {}).get("text", "").strip().lower()
                if update_id > last_update_id:
                    last_update_id = update_id
                    with open(OFFSET_FILE, "w") as f:
                        f.write(str(update_id))
                    if message == "yes":
                        return True
                    elif message == "no":
                        return False
            time.sleep(2)
        except Exception as e:
            print(f"Telegram polling error: {e}")
            time.sleep(5)

def main():
    print("🚀 Starting pre/post market report generator...")

    # 1. Fetch data
    report = []
    report.append("📊 Indian Market:")
    report.append(get_yahoo_price_with_change("^NSEI", "NIFTY 50"))
    report.append(get_yahoo_price_with_change("^BSESN", "SENSEX"))
    report.append(get_yahoo_price_with_change("^NSEBANK", "BANK NIFTY"))

    report.append("\n🌍 Global Markets:")
    report.append(get_yahoo_price_with_change("^DJI", "Dow Jones"))
    report.append(get_yahoo_price_with_change("^IXIC", "NASDAQ"))
    report.append(get_yahoo_price_with_change("^FTSE", "FTSE 100"))
    report.append(get_yahoo_price_with_change("^N225", "Nikkei 225"))

    index_summary = "\n".join(report)
    news_report = get_et_market_articles(limit=5)

    # 2. Create image
    date_text = get_current_date_ist()
    final_img = create_combined_market_image(date_text, index_summary, news_report)
    send_telegram_file(final_img, caption="🖼️ Combined Report Image")

    if not wait_for_telegram_reply("✅ Image created. Type 'yes' to generate script."):
        return

    combined_text = index_summary + "\n\n" + news_report
    script_path = generate_script_from_report(combined_text)
    send_telegram_file(script_path, caption="📜 Script created.")

    if not wait_for_telegram_reply("✅ Script done. Type 'yes' to generate audio."):
        return

    with open(script_path, "r", encoding="utf-8") as f:
        script_text = f.read()

    audio_path = generate_audio(script_text)
    send_telegram_file(audio_path, caption="🔊 Audio created.")

    if not wait_for_telegram_reply("✅ Audio done. Type 'yes' to generate video."):
        return

    generate_video(["output/final_image.png"])

if __name__ == "__main__":
    main()
