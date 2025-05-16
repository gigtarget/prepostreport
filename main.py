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
LOCK_FILE = "output/.lock"

def wait_for_telegram_reply(prompt_text=None):
    if prompt_text:
        send_telegram_message(prompt_text)

    os.makedirs("output", exist_ok=True)

    last_update_id = None
    try:
        res = requests.get(GET_UPDATES_URL)
        data = res.json()
        if data.get("result"):
            last_update_id = data["result"][-1]["update_id"]
            with open(OFFSET_FILE, "w") as f:
                f.write(str(last_update_id))
        else:
            with open(OFFSET_FILE, "w") as f:
                f.write("0")
    except Exception:
        with open(OFFSET_FILE, "w") as f:
            f.write("0")

    while True:
        try:
            if not os.path.exists(OFFSET_FILE):
                with open(OFFSET_FILE, "w") as f:
                    f.write("0")

            with open(OFFSET_FILE, "r") as f:
                last_update_id = f.read().strip()

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
                elif message_text == "no":
                    return False
                else:
                    send_telegram_message("❌ Invalid reply. Type 'yes' or 'no'.")
            time.sleep(5)
        except Exception as e:
            send_telegram_message(f"⚠️ Error waiting for reply: {e}")
            time.sleep(5)

def get_current_date_ist():
    from datetime import datetime
    import pytz
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def main():
    if os.path.exists(LOCK_FILE):
        print("🛑 Script already ran. Skipping to save API usage.")
        return
    os.makedirs("output", exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write("locked")

    # Generate report
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
    news_items = get_et_market_articles(limit=5)
    news_report = "\n\n".join([f"• {item['title']}" for item in news_items])

    # Generate and send image
    final_img = create_combined_market_image(
        get_current_date_ist(),
        index_summary,
        news_report
    )
    send_telegram_file(final_img, "🖼️ Market Report")

    # ✅ CLEAR STALE YES BEFORE SCRIPT STEP
    with open(OFFSET_FILE, "w") as f:
        f.write("0")

    # SCRIPT STEP
    while True:
        combined_text = index_summary + "\n\n" + news_report
        script_text = generate_script_from_report(combined_text)
        send_telegram_message(f"📝 Generated Script:\n\n{script_text}")
        if wait_for_telegram_reply("🤖 Proceed to generate audio? Reply 'yes' to continue or 'no' to regenerate script."):
            break

    # AUDIO STEP
    while True:
        audio_path = generate_audio(script_text)
        if audio_path and os.path.exists(audio_path):
            send_telegram_file(audio_path, "🎤 Audio Generated")
        else:
            send_telegram_message("❌ Audio generation failed. Retrying...")

        if wait_for_telegram_reply("▶️ Proceed to generate video? Reply 'yes' to continue or 'no' to regenerate audio."):
            break

    # VIDEO STEP
    while True:
        video_path = generate_video()
        if video_path and os.path.exists(video_path):
            send_telegram_file(video_path, "✅ Final Video")
        else:
            send_telegram_message("❌ Video generation failed. Retrying...")

        if wait_for_telegram_reply("🎬 Happy with this video? Reply 'yes' to finish or 'no' to regenerate video."):
            break

if __name__ == "__main__":
    main()
