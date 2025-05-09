from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "templates/arialbd.ttf"  # Ensure this file exists, or fallback to default

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%d.%m.%Y")

def overlay_date_on_template(template_filename, output_filename, y_position=100, font_size=80):
    try:
        img = Image.open(f"templates/{template_filename}").convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()

        date_text = get_current_date_ist()

        # Calculate text width for horizontal centering
        text_bbox = draw.textbbox((0, 0), date_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        image_width = img.width
        x_center = (image_width - text_width) / 2

        draw.text((x_center, y_position), date_text, font=font, fill="black")

        os.makedirs("output", exist_ok=True)
        output_path = f"output/{output_filename}"
        img.save(output_path)
        print(f"✅ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error processing template {template_filename}: {e}")
        return None
