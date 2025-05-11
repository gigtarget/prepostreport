from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Playfair.ttf"  # Ensure this matches your uploaded font

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%d.%m.%Y")

# 🟡 1. For Pre-Date image (date only)
def overlay_date_on_template(
    template_path,
    output_path,
    x_position=None,
    y_position=100,
    font_size=80,
    text_color="black",
    center=True,
    custom_position=None
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            print(f"⚠️ Font load error: {e} — using default")
            font = ImageFont.load_default()

        date_text = get_current_date_ist()

        if custom_position:
            position = custom_position
        elif center:
            text_bbox = draw.textbbox((0, 0), date_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            image_width = img.width
            x_center = (image_width - text_width) / 2
            position = (x_center, y_position)
        else:
            x = x_position if x_position is not None else 50
            position = (x, y_position)

        draw.text(position, date_text, font=font, fill=text_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error processing template {template_path}: {e}")
        return None

# 🟢 2. For Index Summary Image with red/green change coloring
def overlay_text_lines_on_template(
    template_path,
    output_path,
    text_lines,
    font_size=60,
    text_color="black",
    start_y=200,
    line_spacing=80,
    start_x=100
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            print(f"⚠️ Font load error: {e} — using default")
            font = ImageFont.load_default()

        y = start_y
        for line in text_lines:
            draw.text((start_x, y), line, font=font, fill=text_color)

            # Attempt to color just the final change value
            try:
                parts = line.strip().rsplit(" ", 1)
                if len(parts) == 2:
                    text_before, change = parts
                    x_offset = draw.textlength(text_before + " ", font=font)

                    if change.startswith("-"):
                        change_color = "red"
                    elif change.startswith("+") or change.isdigit():
                        change_color = "green"
                    else:
                        change_color = text_color

                    draw.text((start_x + x_offset, y), change, font=font, fill=change_color)
            except Exception as e:
                print(f"⚠️ Failed to color change part: {e}")

            y += line_spacing

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Index data image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating index report image: {e}")
        return None
