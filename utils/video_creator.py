import os
import ffmpeg
from PIL import Image
from ffmpeg import Error
from subprocess import run, PIPE


def get_audio_duration(path):
    try:
        probe = ffmpeg.probe(path)
        return float(probe["format"]["duration"])
    except Error as e:
        print("❌ Failed to get audio duration:", e)
        return 15.0  # fallback default


def convert_and_keep_resolution(image_path, output_path):
    img = Image.open(image_path).convert("RGB")
    img.save(output_path)


def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Paths
    audio_path = "output/output_polly.mp3"
    thank_img = "templates/thank.jpg"

    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    duration = get_audio_duration(audio_path)
    print(f"🎧 Audio Duration: {duration:.2f} sec")

    # Timings
    date_dur = 1
    summary_dur = 4
    thank_dur = 3
    report_dur = max(duration - (date_dur + summary_dur + thank_dur), 1)

    # Image list and durations
    frames = [
        ("output/date.png", date_dur),
        ("output/summary.png", summary_dur),
        ("output/news.png", report_dur),
        (thank_img, thank_dur)
    ]

    # Save as frame_001.jpg, frame_002.jpg, etc.
    current_frame = 0
    for path, dur in frames:
        for _ in range(int(dur)):
            current_frame += 1
            output_frame = f"output/frame_{current_frame:03d}.jpg"
            convert_and_keep_resolution(path, output_frame)

    # FFmpeg stitching
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1)
        audio_input = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(video_input, audio_input, output_video,
                    vcodec="libx264", acodec="aac",
                    pix_fmt="yuv420p", shortest=None)
            .run(overwrite_output=True)
        )
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except ffmpeg.Error as e:
        print("❌ FFmpeg failed:", e.stderr.decode())
        return None
