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
from utils.image_templates import overlay_date_on_template, overlay_text_lines_on_template
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

    return report, nifty, sensex, banknifty, global_indices

# ------------------ MAIN EXECUTION ------------------ #
if __name__ == "__main__":
    send_telegram_message("🔄 Phase 1: Fetching market data and news...")
    report, nifty, sensex, banknifty, global_indices = generate_full_report()

    with open("output/report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    # ✅ Image 1: Date overlay on Pre Date template
    overlay_date_on_template(
        template_path="templates/Pre Date.jpg",
        output_path="output/preview_image.jpg",
        font_size=180,
        x_position=110,
        y_position=1000,
        text_color="black",
        center=False
    )
    send_telegram_file("output/preview_image.jpg", "✅ Pre-Market Report Date")

    # ✅ Image 2: Full index data overlay on report.jpg
    index_lines = [
        " ",
        nifty,
        sensex,
        banknifty,
        "",
        " "
    ] + global_indices

    overlay_text_lines_on_template(
        template_path="templates/report.jpg",
        output_path="output/report_image.jpg",
        text_lines=index_lines,
        font_size=60,
        text_color="black",
        start_y=300,
        line_spacing=85,
        start_x=100
    )
    send_telegram_file("output/report_image.jpg", "📊 Market Index Summary")

    # Await user approval
    with open("output/awaiting_approval.flag", "w") as f:
        f.write("waiting")

    print("🟡 Phase 1 complete. Awaiting user approval to continue...")
