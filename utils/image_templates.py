from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Agrandir.ttf"

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def extract_text_and_change(line):
    parts = line.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].startswith(('+', '-')) or parts[1].replace('.', '', 1).isdigit()):
        return parts[0], parts[1]
    return line, None

def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing, fill):
    """Paragraph-style wrapping"""
    for para in text.split("\n"):
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

    # Date
    date_font_size=70,
    date_x=110,
    date_y=190,
    date_color="black",

    # Summary
    summary_font_size=48,
    summary_x=110,
    summary_y=414,
    summary_line_spacing=10,
    summary_color="black",

    # News
    news_font_size=26,
    news_x=None,  # Auto-calculated below
    news_y=190,
    news_line_spacing=16,
    news_color="black"
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        width, height = img.size
        orientation = "landscape" if width > height else "portrait"
        print(f"🧭 Orientation detected: {orientation} ({width}x{height})")

        # Fonts
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        summary_font = ImageFont.truetype(FONT_PATH, summary_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # Draw date
        draw.text((date_x, date_y), f"{date_text}", font=date_font, fill=date_color)

        # Draw summary
        y_summary = summary_y
        for line in summary_text.split("\n"):
            if line.strip().startswith("📊") or line.strip().startswith("🌍") or not line.strip():
                continue
            y_summary += summary_font_size + summary_line_spacing
            base_text, change = extract_text_and_change(line)
            draw.text((summary_x, y_summary), base_text + " ", font=summary_font, fill=summary_color)
            if change:
                change_color = "green" if "+" in change else "red"
                w = draw.textlength(base_text + " ", font=summary_font)
                draw.text((summary_x + w, y_summary), change, font=summary_font, fill=change_color)

        # 📰 Calculate dynamic width + position for news
        margin = 100
        news_x = width // 2 + 100
        max_news_width = width - news_x - margin

        # Draw News
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        draw_wrapped_text(
            draw,
            news_text,
            news_font,
            news_x,
            news_y + news_font.size + 10,
            max_width=max_news_width,
            line_spacing=news_line_spacing,
            fill=news_color
        )

        # Save
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        return None
