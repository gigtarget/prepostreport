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
    col_x = {
        0: 100,  # Index
        1: 300,  # Price
        2: 440,  # Change
        3: 580,  # %Change
        4: 750   # Sentiment
    }

    y = start_y
    for row in data:
        if all(cell.strip() == "" for cell in row):  # Spacer
            y += line_height
            continue

        if any("----" in cell for cell in row):  # Skip dashed rows
            continue

        for j, text in enumerate(row):
            color = fill
            if j in (2, 3):  # Change or %Change
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

    # Date
    date_font_size=70,
    date_x=100,
    date_y=155,
    date_color="black",

    # Table
    table_font_size=30,
    table_start_x=114,
    table_start_y=330,
    table_line_height=42,

    # News
    news_font_size=30,
    news_x=1050,
    news_y=150,
    news_line_spacing=10,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        image_width, _ = img.size

        # Load fonts
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        table_font = ImageFont.truetype(FONT_PATH, table_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw date
        draw.text((date_x, date_y), date_text, font=date_font, fill=date_color)

        # Draw index table
        draw_index_table(draw, table_rows, table_font, table_start_x, table_start_y, table_line_height, fill="black")

        # Draw news content
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

        # Save image in high quality
        if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
            img.save(output_path, quality=95)
        elif output_path.lower().endswith(".png"):
            img.save(output_path, compress_level=0)
        else:
            img.save(output_path)  # Fallback default

        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None

def create_thumbnail_image(
    date_text,
    template_path="templates/premarket_thumbnail.jpg",
    output_path="output/thumbnail_image.jpg",
    font_size=150,
    date_x=120,
    date_y=400,
    date_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, font_size)

        # Draw the date
        draw.text((date_x, date_y), date_text, font=font, fill=date_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
            img.save(output_path, quality=95)
        elif output_path.lower().endswith(".png"):
            img.save(output_path, compress_level=0)
        else:
            img.save(output_path)  # Fallback

        print(f"✅ Thumbnail image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating thumbnail image: {e}")
        return None

def create_instagram_image(
    date_text,
    table_rows,
    news_text,
    template_path="templates/insta_image.jpg",
    output_path="output/insta_image.jpg",

    # Date
    date_font_size=80,
    date_x=100,
    date_y=160,
    date_color="black",

    # Table
    table_font_size=32,
    table_start_x=110,
    table_start_y=350,
    table_line_height=46,

    # News
    news_font_size=30,
    news_x=110,
    news_y=860,
    news_line_spacing=12,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        image_width, _ = img.size

        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        table_font = ImageFont.truetype(FONT_PATH, table_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw date
        draw.text((date_x, date_y), date_text, font=date_font, fill=date_color)

        # Draw index table
        draw_index_table(draw, table_rows, table_font, table_start_x, table_start_y, table_line_height, fill="black")

        # Draw news
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

        if output_path.lower().endswith(".jpg") or output_path.lower().endswith(".jpeg"):
            img.save(output_path, quality=95)
        elif output_path.lower().endswith(".png"):
            img.save(output_path, compress_level=0)
        else:
            img.save(output_path)

        print(f"✅ Instagram image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating Instagram image: {e}")
        return None
