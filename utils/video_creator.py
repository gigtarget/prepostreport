import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Step 1: Define image paths
    date_img = "output/date.png"
    summary_img = "output/summary.png"
    news_img = "output/news.png"
    thank_img = "templates/thank.jpg"

    frame_paths = []
    durations = []

    def add_image(src_path, duration, index):
        img = Image.open(src_path).convert("RGB")
        frame_path = f"output/frame_{index:03d}.jpg"
        img.save(frame_path)
        frame_paths.append(frame_path)
        durations.append(duration)

    # Step 2: Add images with fixed durations
    add_image(date_img, 2, 0)       # date image for 2 seconds
    add_image(summary_img, 5, 1)    # summary image for 5 seconds

    # Step 3: Get audio duration
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    probe = ffmpeg.probe(audio_path)
    audio_duration = float(probe["format"]["duration"])

    # Step 4: Compute remaining time for news image
    fixed_duration = 2 + 5 + 3  # date + summary + thank
    remaining_time = max(0.5, audio_duration - fixed_duration)

    add_image(news_img, remaining_time, 2)  # news image for remaining time
    add_image(thank_img, 3, 3)              # thank image for 3 seconds

    # Step 5: Create FFmpeg concat text file
    concat_file = "output/concat.txt"
    with open(concat_file, "w") as f:
        for path, duration in zip(frame_paths, durations):
            f.write(f"file '{path}'\n")
            f.write(f"duration {duration}\n")
        # Repeat last frame to ensure duration is applied
        f.write(f"file '{frame_paths[-1]}'\n")

    # Step 6: Run FFmpeg to create video
    try:
        ffmpeg.input(concat_file, format="concat", safe=0) \
            .output(audio_path, output_video, vcodec="libx264", acodec="aac",
                    pix_fmt="yuv420p", shortest=None) \
            .run(overwrite_output=True)

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed: {e.stderr.decode()}")
        return None
