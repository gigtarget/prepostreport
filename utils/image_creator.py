from PIL import Image, ImageDraw, ImageFont
import os

FONT_PATH_BOLD = "arialbd.ttf"  # or a fallback to built-in
FONT_PATH_REGULAR = "arial.ttf"

WIDTH, HEIGHT = 720, 1280
BG_COLOR = "#ffffff"
TEXT_COLOR = "#111111"
TITLE_COLOR = "#2b9348"

def safe_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def create_market_slide(title, value_text, filename):
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)

    title_font = safe_font(FONT_PATH_BOLD, 80)
    value_font = safe_font(FONT_PATH_REGULAR, 64)

    # Use textbbox to get text size (Pillow 8+ compatible)
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]

    value_bbox = draw.textbbox((0, 0), value_text, font=value_font)
    value_width = value_bbox[2] - value_bbox[0]

    draw.text(((WIDTH - title_width) / 2, 150), title, fill=TITLE_COLOR, font=title_font)
    draw.text(((WIDTH - value_width) / 2, 320), value_text, fill=TEXT_COLOR, font=value_font)

    os.makedirs("./output", exist_ok=True)
    img_path = f"./output/{filename}.png"
    img.save(img_path)
    print(f"✅ Image saved: {img_path}")
