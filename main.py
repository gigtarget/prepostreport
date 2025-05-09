import os
from dotenv import load_dotenv
load_dotenv()

# 🔐 Prevent re-runs using a simple lock file
LOCK_FILE = "output/.lock"
if os.path.exists(LOCK_FILE):
    print("🛑 Script already ran once. Skipping to prevent extra API usage.")
    exit()
os.makedirs("output", exist_ok=True)
with open(LOCK_FILE, "w") as f:
    f.write("locked")

from utils.fetch_data import get_yahoo_price_with_change, get_et_market_articles
from utils.script_generator import generate_youtube_script_from_report
from utils.audio_generator import generate_audio_with_polly
from utils.image_creator import create_market_slide
from utils.dalle_image import generate_dalle_image_from_prompt
from utils.video_creator import create_video_from_images_and_audio

# ------------------ Generate full report and news ------------------ #
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

    return report, nifty, sensex, banknifty, news_articles

# ------------------ MAIN ------------------ #
if __name__ == "__main__":
    print("🔄 Fetching market data and news...")
    report_list, nifty, sensex, banknifty, news_articles = generate_full_report()
    report_text = "\n".join(report_list)

    print("🧠 Generating Shorts script...")
    script = generate_youtube_script_from_report(report_text)

    print("\n🎤 Script Output:\n")
    print(script)

    print("🔊 Generating voice with Polly...")
    generate_audio_with_polly(script)

    print("🖼️ Generating market index slides...")
    if "Unavailable" not in nifty:
        create_market_slide("📈 NIFTY 50", nifty.split(":")[1].strip(), "nifty_slide")
    if "Unavailable" not in sensex:
        create_market_slide("📊 SENSEX", sensex.split(":")[1].strip(), "sensex_slide")
    if "Unavailable" not in banknifty:
        create_market_slide("🏦 BANK NIFTY", banknifty.split(":")[1].strip(), "banknifty_slide")

    # --- DALL·E image from top news ---
    if news_articles:
        print("🧠 Generating DALL·E visual for top news...")
        top_title = news_articles[0]['title']
        dalle_prompt = f"A cinematic, digital-style illustration of: {top_title}. Indian financial market theme."
        generate_dalle_image_from_prompt(dalle_prompt, "news_slide_1")

    print("🎞️ Creating final Shorts video...")
    create_video_from_images_and_audio()
