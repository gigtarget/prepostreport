from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Agrandir.ttf"

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing, fill):
    paragraphs = text.split("\n")
    for para in paragraphs:
        if not para.strip():
            y += font.size + line_spacing
            continue
        words = para.split()
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if draw.textlength(test_line, font=font) <= max_width:
                current_line = test_line
            else:
                draw.text((x, y), current_line.strip(), font=font, fill=fill)
                y += font.size + line_spacing
                current_line = word + " "
        if current_line:
            draw.text((x, y), current_line.strip(), font=font, fill=fill)
            y += font.size + line_spacing

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

    summary_font_size=32,
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

        # Draw 📈 Table Summary
        draw_wrapped_text(
            draw,
            summary_text,
            summary_font,
            summary_x,
            summary_y,
            max_width=880,
            line_spacing=summary_line_spacing,
            fill=summary_color
        )

        # Draw 📰 News Section
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        draw_wrapped_text(
            draw,
            news_text,
            news_font,
            news_x,
            news_y + news_font.size + 10,
            max_width=image_width - news_x - 80,
            line_spacing=news_line_spacing,
            fill=news_color
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
