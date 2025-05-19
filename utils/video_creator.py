import os
from PIL import Image
import ffmpeg
import textwrap

def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{int(h):02}:{int(m):02}:{int(s):02},{ms:03}"

def generate_srt_from_script(script_text, duration, output_path="output/subtitles.srt"):
    lines = textwrap.wrap(script_text, width=60)
    per_line_duration = duration / len(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            start_time = format_time(i * per_line_duration)
            end_time = format_time((i + 1) * per_line_duration)
            f.write(f"{i+1}\n{start_time} --> {end_time}\n{line}\n\n")

    return output_path

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Step 1: Use the new single image
    image_path = "output/final_image.png"
    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None

    # Step 2: Convert to .jpg with max quality
    img = Image.open(image_path).convert("RGB")
    frame_path = "output/frame_000.jpg"
    img.save(frame_path, quality=100)

    # Step 3: Confirm audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Step 4: Get audio duration
    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])
    except Exception as e:
        print(f"❌ Failed to probe audio duration: {e}")
        return None

    # Step 5: Load script and generate subtitles
    subtitle_path = "output/generated_script.txt"
    subtitle_text = "Good morning guys. Let’s get you ready for aaj ka market session."
    if os.path.exists(subtitle_path):
        with open(subtitle_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read().strip().replace("'", "").replace('"', '')

    srt_file = generate_srt_from_script(subtitle_text, audio_duration)

    # Step 6: Prepare FFmpeg inputs
    video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1 / audio_duration)
    audio_input = ffmpeg.input(audio_path)

    # Step 7: Combine everything with subtitles
    try:
        (
            ffmpeg
            .output(
                video_input,
                audio_input,
                output_video,
                vf=f"subtitles={srt_file}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H0&,BorderStyle=1,Outline=1'",
                vcodec="libx264",
                acodec="aac",
                crf=18,
                preset="slow",
                pix_fmt="yuv420p",
                shortest=None
            )
            .run(overwrite_output=True)
        )

        print(f"✅ Final video with synced subtitles saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed:\n{e.stderr.decode()}")
        return None
