from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "templates/arialbd.ttf"  # Make sure this font exists or use built-in

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%d.%m.%Y")

def overlay_date_on_template(template_filename, output_filename, position=(7000, 550), font_size=200):
    try:
        img = Image.open(f"templates/{template_filename}").convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()

        date_text = get_current_date_ist()
        draw.text(position, date_text, font=font, fill="black")

        os.makedirs("output", exist_ok=True)
        output_path = f"output/{output_filename}"
        img.save(output_path)
        print(f"✅ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error processing template {template_filename}: {e}")
        return None
