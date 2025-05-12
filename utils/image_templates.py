from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os
from textwrap import wrap

FONT_PATH = "fonts/Agrandir.ttf"  # 🔤 Your chosen font

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%d.%m.%Y")

# 1️⃣ Pre-market date overlay
def overlay_date_on_template(
    template_path,
    output_path,
    x_position=110,
    y_position=1100,
    font_size=160,
    text_color="black",
    center=True,
    custom_position=None
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, font_size)

        date_text = get_current_date_ist()

        if custom_position:
            position = custom_position
        elif center:
            text_bbox = draw.textbbox((0, 0), date_text, font=font)
            x_center = (img.width - (text_bbox[2] - text_bbox[0])) / 2
            position = (x_center, y_position)
        else:
            position = (x_position or 50, y_position)

        draw.text(position, date_text, font=font, fill=text_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error processing template {template_path}: {e}")
        return None

# 2️⃣ Index Summary with green/red point coloring
def overlay_text_lines_on_template(
    template_path,
    output_path,
    text_lines,
    font_size=60,
    text_color="black",
    start_y=260,
    line_spacing=110,
    start_x=100
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONT_PATH, font_size)

        y = start_y
        for line in text_lines:
            draw.text((start_x, y), line, font=font, fill=text_color)
            try:
                parts = line.strip().rsplit(" ", 1)
                if len(parts) == 2:
                    label, change = parts
                    x_offset = draw.textlength(label + " ", font=font)

                    if change.startswith("-"):
                        draw.text((start_x + x_offset, y), change, font=font, fill="red")
                    elif change.startswith("+") or change.isdigit():
                        draw.text((start_x + x_offset, y), change, font=font, fill="green")
            except:
                pass
            y += line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Index image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating index report image: {e}")
        return None

# 3️⃣ Auto-scaled and wrapped News Headlines
def overlay_news_on_template(
    template_path,
    output_path,
    news_lines,
    font_size=48,
    text_color="black",
    start_y=320,
    line_spacing=70,
    start_x=80,
    max_width_ratio=0.85
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size
        max_width = img_width * max_width_ratio

        def wrap_text(text, font_obj):
            words = text.split()
            lines = []
            current_line = ""
            for word in words:
                test_line = current_line + word + " "
                if draw.textlength(test_line, font=font_obj) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line.strip())
                    current_line = word + " "
            if current_line:
                lines.append(current_line.strip())
            return lines

        def get_wrapped_lines(font_obj):
            lines = []
            for headline in news_lines:
                lines += wrap_text(headline, font_obj)
                lines.append("")
            return lines

        while font_size > 20:
            font = ImageFont.truetype(FONT_PATH, font_size)
            total_height = len(get_wrapped_lines(font)) * line_spacing
            if total_height < img_height - start_y - 50:
                break
            font_size -= 2

        font = ImageFont.truetype(FONT_PATH, font_size)
        y = start_y
        for line in get_wrapped_lines(font):
            draw.text((start_x, y), line, font=font, fill=text_color)
            y += line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ News image saved (font size: {font_size}): {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating news image: {e}")
        return None
