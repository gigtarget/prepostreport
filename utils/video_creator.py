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

    image_path = "output/final_image.png"
    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None

    img = Image.open(image_path).convert("RGB")

    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])
        print(f"🔎 Audio duration: {audio_duration} seconds")
    except Exception as e:
        print(f"❌ Failed to probe audio duration: {e}")
        return None

    subtitle_path = "output/generated_script.txt"
    subtitle_text = "Good morning guys. Let’s get you ready for aaj ka market session."
    if os.path.exists(subtitle_path):
        with open(subtitle_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read().strip().replace("'", "").replace('"', '')

    srt_file = generate_srt_from_script(subtitle_text, audio_duration)

    frame_count = int(audio_duration)
    for i in range(frame_count):
        frame_path = f"output/frame_{i:03d}.jpg"
        img.save(frame_path, quality=100)

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

        print("✅ Final video created successfully.")
        print("🟢 Returning output path:", output_video)
        return output_video

    except ffmpeg.Error as e:
        print("❌ FFmpeg exception occurred!")
        print("----- ERROR START -----")
        try:
            print(e.stderr.decode())
        except Exception:
            print(str(e))
        print("------ ERROR END ------")
        return None
