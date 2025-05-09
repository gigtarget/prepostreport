import os
from dotenv import load_dotenv  # Only for local use
load_dotenv()

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.script_generator import generate_youtube_script_from_report
from utils.audio_generator import generate_audio_with_polly
from utils.image_creator import create_market_slide

# ------------------ Generate full report text ------------------ #
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
    for article in get_et_market_articles():
        report.append(f"\n📰 {article['title']}")
        report.append(f"📅 {article['published']}")
        report.append(f"📖 {article['content']}")
        report.append("---")

    return report, nifty, sensex, banknifty

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    print("🔄 Fetching market data...")
    full_report_list, nifty, sensex, banknifty = generate_full_report()
    full_report_text = "\n".join(full_report_list)

    print("🧠 Generating YouTube Shorts Script...")
    script = generate_youtube_script_from_report(full_report_text)

    print("\n🎤 Script:\n")
    print(script)

    print("\n🔊 Generating Audio...")
    generate_audio_with_polly(script)

    print("\n🖼️ Generating Slides...")
    create_market_slide("📈 NIFTY 50", nifty.split(":")[1].strip(), "nifty_slide")
    create_market_slide("📊 SENSEX", sensex.split(":")[1].strip(), "sensex_slide")
    create_market_slide("🏦 BANK NIFTY", banknifty.split(":")[1].strip(), "banknifty_slide")
