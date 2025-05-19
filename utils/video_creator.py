import os
from PIL import Image
import ffmpeg

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

    # Step 5: Load subtitles from file
    subtitle_path = "output/generated_script.txt"
    subtitle_text = "Good morning guys. Let’s get you ready for aaj ka market session."
    if os.path.exists(subtitle_path):
        with open(subtitle_path, "r", encoding="utf-8") as f:
            subtitle_text = f.read().strip().replace("'", "").replace('"', '')

    # Step 6: Draw subtitles using FFmpeg drawtext
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1 / audio_duration)
        audio_input = ffmpeg.input(audio_path)

        # Subtitle styling
        drawtext_filter = (
            f"drawtext=text='{subtitle_text}':"
            "fontcolor=white:"
            "fontsize=40:"
            "borderw=2:"
            "bordercolor=black:"
            "x=(w-text_w)/2:"
            "y=h-th-100"
        )

        (
            ffmpeg
            .output(
                video_input.video.filter_("drawtext", text=subtitle_text, fontcolor='white',
                                          fontsize=40, borderw=2, bordercolor='black',
                                          x='(w-text_w)/2', y='h-th-100'),
                audio_input,
                output_video,
                vcodec="libx264",
                acodec="aac",
                crf=18,
                preset="slow",
                pix_fmt="yuv420p",
                shortest=None
            )
            .run(overwrite_output=True)
        )

        print(f"✅ Final video with subtitles saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed:\n{e.stderr.decode()}")
        return None
