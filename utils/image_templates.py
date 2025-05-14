from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os
from textwrap import wrap

FONT_PATH = "fonts/Agrandir.ttf"

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def create_combined_market_image(
    date_text,
    summary_text,
    news_text,
    template_path="templates/premarket group.jpg",
    output_path="output/final_image.png",
    font_size_date=120,
    font_size_summary=48,
    font_size_news=42,
    line_spacing=10
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        date_font = ImageFont.truetype(FONT_PATH, font_size_date)
        summary_font = ImageFont.truetype(FONT_PATH, font_size_summary)
        news_font = ImageFont.truetype(FONT_PATH, font_size_news)

        # 🗓️ Date
        draw.text((100, 100), f"📅 {date_text}", font=date_font, fill="black")

        # 📊 Summary
        y_offset = 300
        draw.text((100, y_offset), "📈 Market Summary", font=summary_font, fill="black")
        for line in summary_text.split("\n"):
            y_offset += font_size_summary + line_spacing
            draw.text((100, y_offset), line, font=summary_font, fill="black")

        # 📰 News
        y_offset += 100  # Extra space before news
        draw.text((100, y_offset), "🗞️ Market News", font=news_font, fill="black")
        for line in news_text.split("\n"):
            y_offset += font_size_news + line_spacing
            wrapped = wrap(line, width=70)
            for wrap_line in wrapped:
                draw.text((100, y_offset), wrap_line, font=news_font, fill="black")
                y_offset += font_size_news + line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
