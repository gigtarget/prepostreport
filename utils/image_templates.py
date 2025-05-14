from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os
from textwrap import wrap

FONT_PATH = "fonts/Agrandir.ttf"

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def get_color_for_line(line):
    """Apply color based on point movement"""
    if "▲" in line or "↑" in line or "+" in line:
        return "green"
    elif "▼" in line or "↓" in line or "-" in line:
        return "red"
    return "black"

def create_combined_market_image(
    date_text,
    summary_text,
    news_text,
    template_path="templates/premarket group.jpg",
    output_path="output/final_image.png",

    # 📅 Date settings
    date_font_size=70,
    date_x=110,
    date_y=190,
    date_color="black",

    # 📈 Summary settings
    summary_font_size=48,
    summary_x=110,
    summary_y=414,
    summary_line_spacing=10,
    summary_color="black",

    # 📰 News settings
    news_font_size = 42
    news_x = 740             # Start just right of center (image width ~1360)
    news_y = 150             # Top padding to stay under heading
    news_line_spacing = 10
    news_wrap_width = 38     # ~38 words fits nicely in half the image width
    news_color = "black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Fonts
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        summary_font = ImageFont.truetype(FONT_PATH, summary_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw 📅 Date
        draw.text((date_x, date_y), f"📅 {date_text}", font=date_font, fill=date_color)

        # Draw 📈 Summary
        draw.text((summary_x, summary_y), "📈 Market Summary", font=summary_font, fill=summary_color)
        y_summary = summary_y
        for line in summary_text.split("\n"):
            y_summary += summary_font_size + summary_line_spacing
            color = get_color_for_line(line)
            draw.text((summary_x, y_summary), line, font=summary_font, fill=color)

        # Draw 📰 News
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        y_news = news_y
        for line in news_text.split("\n"):
            y_news += news_font_size + news_line_spacing
            for wrap_line in wrap(line, width=news_wrap_width):
                draw.text((news_x, y_news), wrap_line, font=news_font, fill=news_color)
                y_news += news_font_size + news_line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
