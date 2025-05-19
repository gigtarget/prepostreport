import os
import time
import requests
from dotenv import load_dotenv

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import create_combined_market_image, create_thumbnail_image, create_instagram_image
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

def classify_sentiment(change):
    try:
        change = float(change)
    except (ValueError, TypeError):
        return "Neutral"

    if change > 0.7:
        return "Bullish"
    elif change > 0.3:
        return "Slight Bullish"
    elif change < -0.7:
        return "Bearish"
    elif change < -0.3:
        return "Slight Bearish"
    else:
        return "Neutral"

def format_table_row(label, price, change_pts, change_pct):
    try:
        sentiment = classify_sentiment(change_pct)
        formatted_price = f"{int(price):,}"
        formatted_change_pts = f"{int(change_pts):+}"
        formatted_change_pct = f"{float(change_pct):+.2f}%"
    except (ValueError, TypeError):
        return None
    return [label, formatted_price, formatted_change_pts, formatted_change_pct, sentiment]

def main():
    if os.path.exists(LOCK_FILE):
        print("🛑 Script already ran. Skipping to save API usage.")
        return
    os.makedirs("output", exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write("locked")

    # ✅ Create Thumbnail First
    date_text = get_current_date_ist()
    thumbnail_path = create_thumbnail_image(date_text)
    if thumbnail_path and os.path.exists(thumbnail_path):
        send_telegram_file(thumbnail_path, "🖼️ Thumbnail Preview")

    indian_symbols = [
        ("^NSEI", "NIFTY 50"),
        ("^BSESN", "SENSEX"),
        ("^NSEBANK", "BANK NIFTY")
    ]
    global_symbols = [
        ("^DJI", "Dow Jones"),
        ("^IXIC", "NASDAQ"),
        ("^FTSE", "FTSE 100"),
        ("^N225", "Nikkei 225")
    ]

    indian_data = [get_yahoo_price_with_change(sym, lbl) for sym, lbl in indian_symbols]
    global_data = [get_yahoo_price_with_change(sym, lbl) for sym, lbl in global_symbols]

    table_rows = []
    table_rows.append(["Index", "Price", "Change", "%Change", "Sentiment"])

    for item in indian_data:
        if item:
            row = format_table_row(item["label"], item["price"], item["change_pts"], item["change_pct"])
            if row:
                table_rows.append(row)

    table_rows.append(["", "", "", "", ""])
    table_rows.append(["", "", "", "", ""])
    table_rows.append(["", "", "", "", ""])
    table_rows.append(["Index", "Price", "Change", "%Change", "Sentiment"])

    for item in global_data:
        if item:
            row = format_table_row(item["label"], item["price"], item["change_pts"], item["change_pct"])
            if row:
                table_rows.append(row)

    news_items = get_et_market_articles(limit=5)
    news_report = "\n\n".join([f"• {item['title']}" for item in news_items])

    final_img = create_combined_market_image(
        date_text,
        table_rows,
        news_report
    )
    if final_img and os.path.exists(final_img):
        send_telegram_file(final_img, "🖼️ Market Report")
    else:
        send_telegram_message("❌ Failed to create market image.")
        return

    # ✅ Create Instagram Image after market report
    insta_img = create_instagram_image(
        date_text,
        table_rows,
        news_report
    )
    if insta_img and os.path.exists(insta_img):
        send_telegram_file(insta_img, "🖼️ Instagram Layout Preview")

    with open(OFFSET_FILE, "w") as f:
        f.write("0")

    while True:
        combined_text = "\n".join(["\t".join(row) for row in table_rows]) + "\n\n" + news_report
        script_text = generate_script_from_report(combined_text)
        send_telegram_message(f"📝 Generated Script:\n\n{script_text}")
        if wait_for_telegram_reply("🤖 Proceed to generate audio? Reply 'yes' to continue or 'no' to regenerate script."):
            break

    while True:
        audio_path = generate_audio(script_text)
        if audio_path and os.path.exists(audio_path):
            send_telegram_file(audio_path, "🎤 Audio Generated")
        else:
            send_telegram_message("❌ Audio generation failed. Retrying...")
        if wait_for_telegram_reply("▶️ Proceed to generate video? Reply 'yes' to continue or 'no' to regenerate audio."):
            break

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
