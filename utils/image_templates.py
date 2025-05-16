from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Agrandir.ttf"

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing, fill):
    for paragraph in text.split("\n"):
        if not paragraph.strip():
            y += font.size + line_spacing
            continue
        words = paragraph.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            if draw.textlength(test_line, font=font) <= max_width:
                line = test_line
            else:
                draw.text((x, y), line, font=font, fill=fill)
                y += font.size + line_spacing
                line = word
        if line:
            draw.text((x, y), line, font=font, fill=fill)
            y += font.size + line_spacing

def draw_index_table(draw, data, font, start_x, start_y, line_height, fill):
    # Fixed X positions for each column
    col_x = {
        0: 110,  # Index Name
        1: 330,  # Price
        2: 520,  # Change
        3: 670,  # %Change
        4: 820   # Sentiment
    }

    y = start_y
    for row in data:
        if all(cell == "" for cell in row):
            y += line_height
            continue
        for j, text in enumerate(row):
            color = fill
            if j in (2, 3):  # Change & %Change columns
                if "+" in text:
                    color = "green"
                elif "-" in text:
                    color = "red"
            draw.text((col_x[j], y), text, font=font, fill=color)
        y += line_height

def create_combined_market_image(
    date_text,
    table_rows,
    news_text,
    template_path="templates/premarket group.jpg",
    output_path="output/final_image.png",

    # Date settings
    date_font_size=70,
    date_x=110,
    date_y=190,
    date_color="black",

    # Table settings
    table_font_size=30,
    table_start_x=110,
    table_start_y=330,
    table_line_height=42,

    # News settings
    news_font_size=26,
    news_x=1050,
    news_y=190,
    news_line_spacing=10,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        image_width, _ = img.size

        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        table_font = ImageFont.truetype(FONT_PATH, table_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # 📅 Date
        draw.text((date_x, date_y), date_text, font=date_font, fill=date_color)

        # 📈 Table
        draw_index_table(draw, table_rows, table_font, table_start_x, table_start_y, table_line_height, fill="black")

        # 🗞️ News
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        draw_wrapped_text(
            draw,
            news_text,
            news_font,
            news_x,
            news_y + news_font.size + 10,
            max_width=image_width - news_x - 60,
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
