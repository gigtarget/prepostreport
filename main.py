import os
from dotenv import load_dotenv
load_dotenv()

# 🔐 Prevent repeated execution
LOCK_FILE = "output/.lock"
if os.path.exists(LOCK_FILE):
    print("🛑 Script already ran. Skipping to save API usage.")
    exit()
os.makedirs("output", exist_ok=True)
with open(LOCK_FILE, "w") as f:
    f.write("locked")

# ✅ Imports
from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.script_generator import generate_youtube_script_from_report
from utils.audio_generator import generate_audio_with_polly
from utils.image_creator import create_market_slide
from utils.video_creator import create_video_from_images_and_audio
from utils.telegram_alert import send_telegram_message, send_telegram_file

# ------------------ REPORT GENERATION ------------------ #
def generate_full_report():
    report = []

    report.append("📊 Indian Market:")
    nifty = get_yahoo_price_with_change("^NSEI", "NIFTY 50")
    sensex = get_yahoo_price_with_change("^BSESN", "SENSEX")
    banknifty = get_yahoo_price_with_change("^NSEBANK", "BANK NIFTY")
    report += [nifty, sensex, banknifty]

    report.append("\n🌍 Global Markets:")
    report.append(get_yahoo_price_with_change("^DJI", "Dow Jones"))
    report.append(get_yahoo_price_with_change("^IXIC", "Nasdaq"))
    report.append(get_yahoo_price_with_change("^FTSE", "FTSE 100"))
    report.append(get_yahoo_price_with_change("^GDAXI", "DAX"))
    report.append(get_yahoo_price_with_change("^N225", "Nikkei 225"))

    report.append("\n📰 Top Market News:")
    news_articles = get_et_market_articles()
    for article in news_articles:
        report.append(f"\n📰 {article['title']}")
        report.append(f"📅 {article['published']}")
        report.append(f"📖 {article['content']}")
        report.append("---")

    return report, nifty, sensex, banknifty

# ------------------ MAIN SCRIPT ------------------ #
if __name__ == "__main__":
    send_telegram_message("🔄 Fetching market data and news...")
    print("🔄 Fetching market data and news...")

    report_list, nifty, sensex, banknifty = generate_full_report()
    report_text = "\n".join(report_list)
    send_telegram_message("📊 Market report generated. Creating script...")

    print("🧠 Generating Shorts script...")
    script = generate_youtube_script_from_report(report_text)
    print("\n🎤 Script Output:\n")
    print(script)
    send_telegram_message("📝 Script generated:\n" + script[:1000])  # Trim for Telegram

    print("🔊 Generating voice with Polly...")
    generate_audio_with_polly(script)
    send_telegram_message("🎤 Polly voiceover generated.")
    send_telegram_file("output/output_polly.mp3", "🎤 Polly Audio")

    print("🖼️ Generating market index slides...")
    if "Unavailable" not in nifty:
        create_market_slide("📈 NIFTY 50", nifty.split(":")[1].strip(), "nifty_slide")
        send_telegram_file("output/nifty_slide.png", "📈 NIFTY 50 Slide")

    if "Unavailable" not in sensex:
        create_market_slide("📊 SENSEX", sensex.split(":")[1].strip(), "sensex_slide")
        send_telegram_file("output/sensex_slide.png", "📊 SENSEX Slide")

    if "Unavailable" not in banknifty:
        create_market_slide("🏦 BANK NIFTY", banknifty.split(":")[1].strip(), "banknifty_slide")
        send_telegram_file("output/banknifty_slide.png", "🏦 BANK NIFTY Slide")

    send_telegram_message("🖼️ All index slides generated using Pillow.")

    print("🎞️ Creating final Shorts video...")
    send_telegram_message("🎞️ Creating final Shorts video...")
    create_video_from_images_and_audio()

    if os.path.exists("output/final_video.mp4"):
        send_telegram_file("output/final_video.mp4", "✅ Final Shorts Video")
        send_telegram_message("✅ Final video generation complete!")
    else:
        send_telegram_message("❌ Final video creation failed.")
