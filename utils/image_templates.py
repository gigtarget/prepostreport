from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "templates/arialbd.ttf"  # You can change the font if needed

def get_current_date_ist():
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    return now_ist.strftime("%d.%m.%Y")

def overlay_date_on_template(
    template_path,
    output_path,
    y_position=100,
    font_size=80,
    text_color="black",
    center=True,
    custom_position=None
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Load font with fallback
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except:
            font = ImageFont.load_default()

        date_text = get_current_date_ist()

        # Determine position
        if custom_position:
            position = custom_position
        elif center:
            text_bbox = draw.textbbox((0, 0), date_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            image_width = img.width
            x_center = (image_width - text_width) / 2
            position = (x_center, y_position)
        else:
            position = (50, y_position)

        # Draw text
        draw.text(position, date_text, font=font, fill=text_color)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error processing template {template_path}: {e}")
        return None
