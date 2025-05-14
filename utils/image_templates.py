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

    # 📅 Date settings
    date_font_size=120,
    date_position=(100, 100),
    date_color="black",

    # 📈 Summary settings
    summary_font_size=48,
    summary_start_pos=(100, 300),
    summary_line_spacing=10,
    summary_color="black",

    # 📰 News settings
    news_font_size=42,
    news_start_pos=(100, 900),
    news_line_spacing=10,
    news_wrap_width=70,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Fonts
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        summary_font = ImageFont.truetype(FONT_PATH, summary_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw 📅 Date
        draw.text(date_position, f"📅 {date_text}", font=date_font, fill=date_color)

        # Draw 📈 Summary
        x_summary, y_summary = summary_start_pos
        draw.text((x_summary, y_summary), "📈 Market Summary", font=summary_font, fill=summary_color)
        for line in summary_text.split("\n"):
            y_summary += summary_font_size + summary_line_spacing
            draw.text((x_summary, y_summary), line, font=summary_font, fill=summary_color)

        # Draw 📰 News
        x_news, y_news = news_start_pos
        draw.text((x_news, y_news), "🗞️ Market News", font=news_font, fill=news_color)
        for line in news_text.split("\n"):
            y_news += news_font_size + news_line_spacing
            for wrap_line in wrap(line, width=news_wrap_width):
                draw.text((x_news, y_news), wrap_line, font=news_font, fill=news_color)
                y_news += news_font_size + news_line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
