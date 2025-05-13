import os
import ffmpeg
from PIL import Image

def get_audio_duration(path):
    try:
        probe = ffmpeg.probe(path)
        return float(probe["format"]["duration"])
    except ffmpeg.Error as e:
        print("❌ Could not retrieve audio duration.")
        return 15.0  # fallback

def save_frame(img_path, save_as):
    try:
        img = Image.open(img_path).convert("RGB")
        img.save(save_as)
        print(f"🖼️ Saved frame: {save_as}")
    except Exception as e:
        print(f"❌ Error saving frame from {img_path}: {e}")

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    audio_path = "output/output_polly.mp3"
    thank_img = "templates/thank.jpg"

    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    duration = get_audio_duration(audio_path)
    print(f"🎧 Audio Duration: {duration:.2f} sec")

    # Frame timing
    date_dur = 1
    summary_dur = 4
    thank_dur = 3
    report_dur = max(duration - (date_dur + summary_dur + thank_dur), 1)

    # Image-to-duration map
    frames = [
        ("output/date.png", date_dur),
        ("output/summary.png", summary_dur),
        ("output/news.png", report_dur),
        (thank_img, thank_dur)
    ]

    # Generate frames as JPG
    current_frame = 0
    for img_path, seconds in frames:
        for _ in range(int(seconds)):
            current_frame += 1
            save_frame(img_path, f"output/frame_{current_frame:03d}.jpg")

    # Build video with FFmpeg
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1)
        audio_input = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(video_input, audio_input, output_video,
                    vcodec="libx264", acodec="aac", pix_fmt="yuv420p", shortest=None)
            .run(overwrite_output=True)
        )

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        err_msg = e.stderr.decode() if e.stderr else str(e)
        print(f"❌ FFmpeg failed:\n{err_msg}")
        return None
