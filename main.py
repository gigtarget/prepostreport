import os
import time
from dotenv import load_dotenv
load_dotenv()

LOCK_FILE = "output/.lock"
PHASE_FILE = "output/phase.txt"

# Prevent reruns
if os.path.exists(LOCK_FILE):
    print("🛑 Script already ran. Skipping to save API usage.")
    exit()
os.makedirs("output", exist_ok=True)
with open(LOCK_FILE, "w") as f:
    f.write("locked")

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.image_templates import (
    overlay_date_on_template,
    overlay_text_lines_on_template,
    overlay_news_on_template
)
from utils.telegram_alert import send_telegram_message, send_telegram_file

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
    send_telegram_message("🔄 Fetching market data and news...")
    report, nifty, sensex, banknifty, global_indices, news_articles = generate_full_report()

    with open("output/report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(report))

    # 1. Date Image
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

    # 2. Index Summary Image
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

    # 3. News Image
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

    # 4. Write phase and exit
    with open(PHASE_FILE, "w") as f:
        f.write("awaiting_script")
    send_telegram_message("✅ All images sent. Reply 'yes' to generate the script.")

    print("🟡 Phase 1 complete. Awaiting approval for script...")
    exit()