import os
from glob import glob
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

    # Validate inputs
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None
    if not all(os.path.exists(p) for p in [date_img, summary_img, news_img, thank_img]):
        print("❌ One or more images are missing.")
        return None

    # Get audio duration
    try:
        audio_info = mediainfo(audio_path)
        duration = float(audio_info['duration'])
    except Exception as e:
        print("❌ Could not get audio duration:", e)
        return None

    # Set durations
    duration1 = 1      # date
    duration2 = 4      # summary
    duration4 = 3      # thank you
    duration3 = max(duration - (duration1 + duration2 + duration4), 1)  # news

    frames = [
        (date_img, duration1),
        (summary_img, duration2),
        (news_img, duration3),
        (thank_img, duration4),
    ]

    input_txt = "output/ffmpeg_input.txt"
    with open(input_txt, "w") as f:
        for i, (img_path, dur) in enumerate(frames):
            frame_path = f"output/frame_{i:02d}.jpg"
            img = Image.open(img_path).convert("RGB")
            img.save(frame_path)
            f.write(f"file '{frame_path}'\n")
            f.write(f"duration {dur}\n")
        f.write(f"file '{frame_path}'\n")  # Repeat last frame for accurate closure

    # Combine with FFmpeg
    try:
        ffmpeg.input(input_txt, format='concat', safe=0)\
              .output(audio_path, output_video,
                      vcodec="libx264", acodec="aac",
                      pix_fmt="yuv420p", shortest=None)\
              .run(overwrite_output=True)

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print("❌ FFmpeg failed:", e.stderr.decode() if e.stderr else str(e))
        return None
