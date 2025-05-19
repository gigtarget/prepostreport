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

    # Step 1: Check image
    image_path = "output/final_image.png"
    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None

    img = Image.open(image_path).convert("RGB")

    # Step 2: Check audio
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Step 3: Get duration
    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])
        print(f"🔎 Audio duration: {audio_duration} seconds")
    except Exception as e:
        print(f"❌ Failed to probe audio duration: {e}")
        return None

    # Step 4: Load script
    subtitle_path = "output/generated_script.txt"
    subtitle_text = "Good morning guys. Let’s get you ready for aaj ka market session."
    if os.path.exists(subtitle_path):
        with open(subtitle_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read().strip().replace("'", "").replace('"', '')

    srt_file = generate_srt_from_script(subtitle_text, audio_duration)

    # Step 5: Create repeated frames
    frame_count = int(audio_duration)
    for i in range(frame_count):
        frame_path = f"output/frame_{i:03d}.jpg"
        img.save(frame_path, quality=100)

    # Step 6: Feed into FFmpeg
    video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1)
    audio_input = ffmpeg.input(audio_path)

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
            .run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
        )

        print(f"✅ Final video saved: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        err_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"❌ FFmpeg failed:\n{err_msg}")
        return None
