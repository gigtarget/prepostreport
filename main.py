import os
import time
import requests
from dotenv import load_dotenv

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import overlay_date_on_template, overlay_text_lines_on_template, overlay_news_on_template
from utils.script_generator import generate_script_from_report
from utils.audio_generator import generate_audio
from utils.video_creator import generate_video
from utils.telegram_alert import send_telegram_message, send_telegram_file

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
GET_UPDATES_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
PHASE_FILE = "output/phase.txt"
OFFSET_FILE = "output/last_update.txt"

def wait_for_yes_reply(prompt):
    send_telegram_message(prompt)
    print(f"🤖 Waiting for reply: '{prompt}'")

    def get_last_update_id():
        if os.path.exists(OFFSET_FILE):
            with open(OFFSET_FILE, "r") as f:
                return int(f.read().strip())
        return None

    def set_last_update_id(update_id):
        with open(OFFSET_FILE, "w") as f:
            f.write(str(update_id))

    last_id = get_last_update_id()

    while True:
        try:
            res = requests.get(GET_UPDATES_URL).json()
            updates = res.get("result", [])
            for update in updates:
                update_id = update["update_id"]
                message = update.get("message", {})
                text = message.get("text", "").strip().lower()
                chat_id = message.get("chat", {}).get("id")

                if chat_id == int(TELEGRAM_CHAT_ID):
                    if last_id is None or update_id > last_id:
                        set_last_update_id(update_id)
                        if text == "yes":
                            return True
                        elif text == "no":
                            send_telegram_message("❌ Process stopped as requested.")
                            exit()
        except Exception as e:
            print(f"❌ Telegram polling error: {e}")

        time.sleep(5)

def generate_full_report():
    report = []

    report.append("📊 Indian Market:")
    nifty = get_yahoo_price_with_change("^NSEI", "NIFTY 50")
    sensex = get_yahoo_price_with_change("^BSESN", "SENSEX")
    banknifty = get_yahoo_price_with_change("^NSEBANK", "BANK NIFTY")
    report += [nifty, sensex, banknifty]

    report.append("\n🌍 Global Markets:")
    global_indices = [
        get_yahoo_price_with_change("^DJI", "Dow Jones"),
        get_yahoo_price_with_change("^IXIC", "Nasdaq"),
        get_yahoo_price_with_change("^FTSE", "FTSE 100"),
        get_yahoo_price_with_change("^GDAXI", "DAX"),
        get_yahoo_price_with_change("^N225", "Nikkei 225")
    ]
    report += global_indices

    report.append("\n📰 Top Market News:")
    news_articles = get_et_market_articles()
    for article in news_articles:
        report.append(f"\n📰 {article['title']}")
        report.append(f"📅 {article['published']}")
        report.append(f"📖 {article['content']}")
        report.append("---")

    return report, nifty, sensex, banknifty, global_indices, news_articles

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    report, nifty, sensex, banknifty, global_indices, news_articles = generate_full_report()

    with open("output/report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    overlay_date_on_template(
        template_path="templates/Pre Date.jpg",
        output_path="output/preview_image.jpg",
        font_size=160,
        x_position=110,
        y_position=1100,
        text_color="black",
        center=False
    )
    send_telegram_file("output/preview_image.jpg", "✅ Pre-Market Report Date")

    index_lines = [" ", nifty, sensex, banknifty, "", " "] + global_indices
    overlay_text_lines_on_template(
        template_path="templates/report.jpg",
        output_path="output/report_image.jpg",
        text_lines=index_lines,
        font_size=60,
        text_color="black",
        start_y=260,
        line_spacing=110,
        start_x=100
    )
    send_telegram_file("output/report_image.jpg", "📊 Market Index Summary")

    news_lines = [article["title"] for article in news_articles[:5]]
    overlay_news_on_template(
        template_path="templates/news.jpg",
        output_path="output/news_image.jpg",
        news_lines=news_lines,
        font_size=48,
        text_color="black",
        start_y=320,
        line_spacing=70,
        start_x=100,
        max_width_ratio=0.85
    )
    send_telegram_file("output/news_image.jpg", "📰 Top Market Headlines")

    # Step 1: Wait for script approval
    if wait_for_yes_reply("✅ Images sent. Reply 'yes' to generate script."):
        with open("output/report.txt", "r", encoding="utf-8") as f:
            report_text = f.read()
        script = generate_script_from_report(report_text)
        with open("output/final_script.txt", "w", encoding="utf-8") as f:
            f.write(script)
        send_telegram_file("output/final_script.txt", "✍️ Script generated.")

    # Step 2: Wait for audio approval
    if wait_for_yes_reply("Reply 'yes' to generate audio."):
        audio_path = generate_audio(script)
        send_telegram_file(audio_path, "🔊 Audio ready.")

    # Step 3: Wait for video approval
    if wait_for_yes_reply("Reply 'yes' to generate video."):
        video_path = generate_video(script, audio_path)
        send_telegram_file(video_path, "📽️ Final video generated.")

    send_telegram_message("✅ All steps completed successfully.")
