from PIL import Image, ImageDraw, ImageFont
import os

# ✅ You can customize these fonts (optional)
FONT_PATH_BOLD = "arialbd.ttf"  # or use default system fonts
FONT_PATH_REGULAR = "arial.ttf"

WIDTH, HEIGHT = 1280, 720
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

    # Title (Centered top)
    title_width, _ = draw.textsize(title, font=title_font)
    draw.text(((WIDTH - title_width) / 2, 150), title, fill=TITLE_COLOR, font=title_font)

    # Value/Stat (Centered middle)
    value_width, _ = draw.textsize(value_text, font=value_font)
    draw.text(((WIDTH - value_width) / 2, 320), value_text, fill=TEXT_COLOR, font=value_font)

    # Save image
    os.makedirs("./output", exist_ok=True)
    img_path = f"./output/{filename}.png"
    img.save(img_path)
    print(f"✅ Image saved: {img_path}")
