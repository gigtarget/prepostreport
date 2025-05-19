import os
import textwrap
from PIL import Image
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip
)

def generate_subtitle_clips(script_text, duration, video_width, video_height, font_size=32, font_color='white'):
    lines = textwrap.wrap(script_text, width=60)
    per_line_duration = duration / len(lines)

    subtitle_clips = []
    for i, line in enumerate(lines):
        start_time = i * per_line_duration
        end_time = (i + 1) * per_line_duration

        txt_clip = (
            TextClip(line, fontsize=font_size, color=font_color, font='Arial-Bold', method='caption', size=(video_width - 100, None))
            .set_position(('center', video_height - 100))  # Position above bottom
            .set_duration(per_line_duration)
            .set_start(start_time)
        )
        subtitle_clips.append(txt_clip)

    return subtitle_clips

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    image_path = "output/final_image.png"
    audio_path = "output/output_polly.mp3"
    script_path = "output/generated_script.txt"

    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None
    if not os.path.exists(script_path):
        print("❌ Script file not found.")
        return None

    try:
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        img = Image.open(image_path).convert("RGB")
        width, height = img.size

        image_clip = ImageClip(image_path).set_duration(duration).set_audio(audio_clip)

        with open(script_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read().strip().replace("'", "").replace('"', '')

        subtitle_clips = generate_subtitle_clips(subtitle_text, duration, width, height)

        final = CompositeVideoClip([image_clip] + subtitle_clips)
        final.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")

        print(f"✅ Final video saved: {output_video}")
        return output_video

    except Exception as e:
        print("❌ MoviePy failed:")
        print(str(e))
        return None
