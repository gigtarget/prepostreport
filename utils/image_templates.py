from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import pytz
import os

FONT_PATH = "fonts/Agrandir.ttf" # Make sure this font file exists at this path

def get_current_date_ist(): # This function is duplicated, ensure it's consistent or defined once
    ist = pytz.timezone("Asia/Kolkata")
    return datetime.now(ist).strftime("%d.%m.%Y")

def extract_text_and_change(line):
    parts = line.rsplit(" ", 1)
    if len(parts) == 2 and (parts[1].startswith(('+', '-')) or parts[1].replace('.', '', 1).isdigit()):
        return parts[0], parts[1]
    return line, None

def draw_wrapped_text(draw, text, font, x, y, max_width, line_spacing, fill):
    """Wrap and draw multi-line text with paragraphs"""
    if not text or not text.strip(): # Handle empty or whitespace-only text
        return y # Return current y, no drawing done

    for paragraph_text in text.split("\n"): # Each news item is now a paragraph_text
        if not paragraph_text.strip(): # Skip empty paragraphs (e.g. from \n\n join)
            y += font.size + line_spacing # Add space for an empty paragraph if desired, or just continue
            continue
        
        words = paragraph_text.split() # Split the paragraph into words
        if not words: # If paragraph had no words (e.g. just spaces after strip)
            continue

        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            # Check textlength of test_line
            if draw.textlength(test_line.strip(), font=font) <= max_width: # Use strip() for accurate length of visible text
                current_line = test_line
            else:
                # Test line is too long, draw the current_line (without the new word)
                if current_line.strip(): # Ensure there's something to draw
                    draw.text((x, y), current_line.strip(), font=font, fill=fill)
                    y += font.size + line_spacing
                # Start new line with the current word
                current_line = word + " "
        
        # Draw the last remaining line of the paragraph
        if current_line.strip():
            draw.text((x, y), current_line.strip(), font=font, fill=fill)
            y += font.size + line_spacing
    return y # Return the updated y position


def create_combined_market_image(
    date_text,
    summary_text,
    news_text, # This is the processed news_report
    template_path="templates/premarket group.jpg",
    output_path="output/final_image.png",

    # 📅 Date settings
    date_font_size=70,
    date_x=110,
    date_y=190,
    date_color="black",

    # 📈 Summary settings
    summary_font_size=48,
    summary_x=110,
    summary_y=414, # Initial y for the summary block
    summary_line_spacing=10,
    summary_color="black",

    # 📰 News settings
    news_font_size=26,
    news_x=1050,
    news_y=190, # y for "Market News" title
    news_line_spacing=16,
    # Default news_wrap_max_width_param: This is the desired width for the news text block
    # It will be constrained by the actual available image width.
    news_wrap_max_width_param=750, 
    news_color="black",
    news_padding_from_right_edge=20 # Padding from the image's right edge
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        image_w, image_h = img.size
        print(f"🖼️ Template image size: {image_w}x{image_h}")

        # Load fonts
        date_font = ImageFont.truetype(FONT_PATH, date_font_size)
        summary_font = ImageFont.truetype(FONT_PATH, summary_font_size)
        news_font = ImageFont.truetype(FONT_PATH, news_font_size)

        # 📅 Draw Date
        draw.text((date_x, date_y), f"{date_text}", font=date_font, fill=date_color)

        # 📈 Draw indices
        current_y_summary = summary_y # Start y for the first index line
        for line in summary_text.split("\n"):
            if line.strip().startswith("📊") or line.strip().startswith("🌍") or not line.strip():
                # For headers or empty lines, you might want to add some vertical space if they are not just skipped
                if line.strip(): # If it's a header
                    # Optionally draw headers if you want them on the image, or just use for spacing
                    # draw.text((summary_x, current_y_summary), line.strip(), font=summary_font, fill=summary_color)
                    current_y_summary += summary_font_size + summary_line_spacing # Add space after a header
                continue 
            
            # For actual index data lines
            base_text, change = extract_text_and_change(line)
            draw.text((summary_x, current_y_summary), base_text + " ", font=summary_font, fill=summary_color)

            if change:
                change_color = "green" if "+" in change else "red"
                # Use textbbox to get width more reliably if textlength is problematic for your font/Pillow version
                # For simplicity, using textlength as in original
                base_text_width = draw.textlength(base_text + " ", font=summary_font)
                draw.text((summary_x + base_text_width, current_y_summary), change, font=summary_font, fill=change_color)
            current_y_summary += summary_font_size + summary_line_spacing


        # 📰 Draw News
        # Draw the "Market News" title
        draw.text((news_x, news_y), "🗞️ Market News", font=news_font, fill=news_color)
        
        # Calculate the actual maximum width available for the news text block
        available_width_for_news_block = image_w - news_x - news_padding_from_right_edge
        
        # The final max_width for text wrapping logic should be the smaller of the user-defined
        # wrap width (news_wrap_max_width_param) and the physically available width.
        actual_news_wrap_width = min(news_wrap_max_width_param, available_width_for_news_block)
        
        if actual_news_wrap_width <= 0: # Safety check if calculated width is invalid
            actual_news_wrap_width = image_w / 4 # Fallback to a quarter of image width

        print(f"📰 News text: X={news_x}, Y_start_title={news_y}, Calculated Wrap Width={actual_news_wrap_width}")

        # Y position for the start of the actual news items (below the title)
        news_items_start_y = news_y + news_font_size + 10 
        
        draw_wrapped_text(
            draw,
            news_text, # The processed news_report string
            news_font,
            news_x,
            news_items_start_y,
            max_width=actual_news_wrap_width, # Use the correctly calculated max width
            line_spacing=news_line_spacing,
            fill=news_color
        )

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ Combined image saved to: {output_path}")
        return output_path

    except FileNotFoundError:
        print(f"❌ Error: Font file not found at {FONT_PATH} or template not found at {template_path}")
        return None
    except Exception as e:
        print(f"❌ Error creating combined image: {e}")
        import traceback
        traceback.print_exc() # Print full traceback for debugging
        return None
