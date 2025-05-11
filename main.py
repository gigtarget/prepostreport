import os
import time
from dotenv import load_dotenv
load_dotenv()

# 🔐 Prevent repeated execution unless unlocked manually
LOCK_FILE = "output/.lock"
if os.path.exists(LOCK_FILE):
    print("🛑 Script already ran. Skipping to save API usage.")
    exit()
os.makedirs("output", exist_ok=True)
with open(LOCK_FILE, "w") as f:
    f.write("locked")

# ✅ Imports
from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import overlay_date_on_template
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

    return report

# ------------------ MAIN EXECUTION ------------------ #
if __name__ == "__main__":
    send_telegram_message("🔄 Phase 1: Fetching market data and news...")
    report = generate_full_report()

    # Save the report locally
    with open("output/report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    # ✅ Custom text styling for image
    overlay_date_on_template(
        template_path="templates/Pre Date.jpg",
        output_path="output/preview_image.jpg",
        font_size=180,
        y_position=1150,
        text_color="black"  # Make all changes here
    )

    send_telegram_file("output/preview_image.jpg", "✅ Report and image ready. Reply 'yes' to continue with script, audio, and video generation.")

    with open("output/awaiting_approval.flag", "w") as f:
        f.write("waiting")

    print("🟡 Phase 1 complete. Awaiting user approval to continue...")
