from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Agrandir.ttf"

def draw_table_text(draw, lines, font, x, y, line_spacing, fill):
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += font.size + line_spacing

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def create_combined_market_image(
    date_text,
    summary_text,
    news_text,
    template_path="templates/premarket group.jpg",
    output_path="output/final_image.png",

    date_font_size=70,
    date_x=110,
    date_y=190,
    date_color="black",

    summary_font_size=30,
    summary_x=110,
    summary_y=320,
    summary_line_spacing=10,
    summary_color="black",

    news_font_size=28,
    news_x=1050,
    news_y=190,
    news_line_spacing=16,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        image_width, image_height = img.size

        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        summary_font = ImageFont.truetype(FONT_PATH, summary_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw 📅 Date
        draw.text((date_x, date_y), f"{date_text}", font=date_font, fill=date_color)

        # Draw table-style summary (line by line for aligned columns)
        summary_lines = summary_text.split("\n")
        draw_table_text(draw, summary_lines, summary_font, summary_x, summary_y, summary_line_spacing, summary_color)

        # Draw 📰 Market News
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        news_lines = news_text.split("\n")
        draw_table_text(draw, news_lines, news_font, news_x, news_y + news_font.size + 10, news_line_spacing, news_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
