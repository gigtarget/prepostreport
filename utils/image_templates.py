def overlay_news_on_template(
    template_path,
    output_path,
    news_lines,
    font_size=48,
    text_color="black",
    start_y=200,
    line_spacing=70,
    start_x=80,
    wrap_width=90
):
    try:
        img = Image.open(template_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except Exception as e:
            print(f"⚠️ Font load error: {e}")
            font = ImageFont.load_default()

        from textwrap import wrap
        y = start_y
        for headline in news_lines:
            wrapped_lines = wrap(headline, width=wrap_width)
            for line in wrapped_lines:
                draw.text((start_x, y), line, font=font, fill=text_color)
                y += line_spacing
            y += 20  # spacing between headlines

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path)
        print(f"✅ News image saved: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error creating news image: {e}")
        return None
