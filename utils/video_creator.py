import os
from PIL import Image
import ffmpeg
from pydub.utils import mediainfo

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Input files
    date_img = "output/date.png"
    summary_img = "output/summary.png"
    news_img = "output/news.png"
    thank_img = "templates/thank.jpg"
    audio_path = "output/output_polly.mp3"

    # Check required files
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None
    for img in [date_img, summary_img, news_img, thank_img]:
        if not os.path.exists(img):
            print(f"❌ Missing image: {img}")
            return None

    # Get audio duration
    try:
        audio_info = mediainfo(audio_path)
        duration = float(audio_info["duration"])
    except Exception as e:
        print(f"❌ Failed to get audio duration: {e}")
        return None

    # Duration configuration
    duration1 = 1  # Date
    duration2 = 4  # Summary
    duration4 = 3  # Thank you
    duration3 = max(duration - (duration1 + duration2 + duration4), 1)  # News

    # Prepare frames with durations
    frames = [
        (date_img, duration1),
        (summary_img, duration2),
        (news_img, duration3),
        (thank_img, duration4)
    ]

    # Write FFmpeg input file
    input_txt_path = "output/ffmpeg_input.txt"
    with open(input_txt_path, "w") as f:
        for i, (img_path, dur) in enumerate(frames):
            frame_filename = f"frame_{i:02d}.jpg"
            frame_path = os.path.join("output", frame_filename)

            img = Image.open(img_path).convert("RGB")
            img.save(frame_path)
            print(f"✅ Saved frame: {frame_path}")

            f.write(f"file '{frame_filename}'\n")
            f.write(f"duration {dur}\n")

        # Repeat last frame for ffmpeg safety
        f.write(f"file '{frame_filename}'\n")

    # Run FFmpeg
    try:
        (
            ffmpeg
            .input("output/ffmpeg_input.txt", format="concat", safe=0)
            .output(audio_path, output_video,
                    vcodec="libx264", acodec="aac", pix_fmt="yuv420p", shortest=None)
            .run(overwrite_output=True)
        )
        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print("❌ FFmpeg failed:", e.stderr.decode() if e.stderr else str(e))
        return None
