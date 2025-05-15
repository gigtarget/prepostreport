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
        # Attempt to get the last update_id to start fresh for this session's replies
        res = requests.get(GET_UPDATES_URL, timeout=10) # Added timeout
        data = res.json()
        if data.get("result"):
            last_update_id = data["result"][-1]["update_id"]
            with open(OFFSET_FILE, "w") as f:
                f.write(str(last_update_id))
        else:
            # If no results, or if offset needs to be truly 0 (e.g. first run or after clearing)
            # This part might be redundant if clearing offset file before each wait is preferred
            with open(OFFSET_FILE, "w") as f:
                f.write("0") # Start with 0 if no prior updates or instructed to clear
    except Exception as e:
        print(f"Error initializing offset: {e}. Defaulting offset to 0.")
        with open(OFFSET_FILE, "w") as f:
            f.write("0")


    while True:
        try:
            if not os.path.exists(OFFSET_FILE):
                with open(OFFSET_FILE, "w") as f:
                    f.write("0")

            with open(OFFSET_FILE, "r") as f:
                current_offset = f.read().strip()
                if not current_offset: # Handle empty file case
                    current_offset = "0"


            params = {"timeout": 30}
            # The offset should be last_update_id + 1
            # current_offset from file IS the last_update_id processed
            params["offset"] = int(current_offset) + 1


            res = requests.get(GET_UPDATES_URL, params=params, timeout=35) # Timeout for getUpdates
            data = res.json()

            if data.get("ok") and data.get("result"):
                for result in data["result"]:
                    last_update_id_processed = result["update_id"] # This is the new last_update_id

                    # Save this new last_update_id so next poll uses offset = last_update_id_processed + 1
                    with open(OFFSET_FILE, "w") as f:
                        f.write(str(last_update_id_processed))

                    if "message" in result and "text" in result["message"]:
                        message_text = result["message"]["text"].strip().lower()
                        if message_text == "yes":
                            return True
                        elif message_text == "no":
                            return False
                        else:
                            send_telegram_message("❌ Invalid reply. Type 'yes' or 'no'.")
            # If no new messages, data["result"] will be empty, loop continues
            time.sleep(5)
        except requests.exceptions.ReadTimeout:
            print("Telegram getUpdates timeout. Retrying...")
            time.sleep(1) # Brief pause before retrying timeout
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
    
    news_items_raw = get_et_market_articles(limit=5)
    
    # --- FIX STARTS HERE ---
    # Process news items to remove unwanted internal newlines
    news_items_processed = []
    if news_items_raw: # Check if news_items_raw is not None and is iterable
        for item_text in news_items_raw:
            if isinstance(item_text, str):
                # Replace all newline characters within the item_text with an empty string.
                # This joins parts of words or phrases split by erroneous newlines.
                # .strip() removes any leading/trailing whitespace from the cleaned item.
                cleaned_item = item_text.replace("\n", "").strip()
                if cleaned_item: # Only add non-empty items
                    news_items_processed.append(cleaned_item)
            else:
                # Optionally, log or handle items that are not strings
                print(f"Warning: Non-string item found in news_items_raw: {item_text}")
    
    # Join the processed, coherent news items with double newlines for separation in the image.
    news_report = "\n\n".join(news_items_processed)
    # --- FIX ENDS HERE ---

    # Generate and send image
    final_img = create_combined_market_image(
        get_current_date_ist(),
        index_summary,
        news_report # Use the processed news_report
    )
    if final_img: # Check if image creation was successful
        send_telegram_file(final_img, "🖼️ Market Report")
    else:
        send_telegram_message("⚠️ Failed to generate market report image.")


    # Clear offset file before asking for script generation confirmation
    # This ensures wait_for_telegram_reply gets fresh replies for this step
    try:
        with open(OFFSET_FILE, "w") as f:
            f.write("0") # Reset offset
        # Prime the offset by reading current updates once.
        res = requests.get(GET_UPDATES_URL, timeout=10)
        data = res.json()
        if data.get("result"):
            last_update_id = data["result"][-1]["update_id"]
            with open(OFFSET_FILE, "w") as f:
                f.write(str(last_update_id))
    except Exception as e:
        print(f"Error resetting offset before script step: {e}")


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
            # Potentially add a small delay or a counter to prevent infinite fast retries

        if wait_for_telegram_reply("▶️ Proceed to generate video? Reply 'yes' to continue or 'no' to regenerate audio."):
            break

    # VIDEO STEP
    while True:
        # Assuming generate_video() uses the image and audio previously generated.
        # If it needs specific paths, ensure they are passed or accessible.
        # The current generate_video() call is parameterless.
        video_path = generate_video() # Consider if it needs final_img, audio_path
        if video_path and os.path.exists(video_path):
            send_telegram_file(video_path, "✅ Final Video")
        else:
            send_telegram_message("❌ Video generation failed. Retrying...")
            # Potentially add a small delay

        if wait_for_telegram_reply("🎬 Happy with this video? Reply 'yes' to finish or 'no' to regenerate video."):
            break
            
    # Clean up lock file upon successful completion
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("✅ Script finished successfully.")


if __name__ == "__main__":
    main()
