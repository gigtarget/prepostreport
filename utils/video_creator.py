import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video=os.path.abspath("output/final_video.mp4")):
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
        frame_filename = f"frame_{index:03d}.jpg"
        frame_path = os.path.join("output", frame_filename)
        img.save(frame_path)
        frame_paths.append(frame_filename)
        durations.append(duration)

    # Step 2: Add images
    add_image(date_img, 2, 0)
    add_image(summary_img, 5, 1)

    # Step 3: Get audio duration
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    probe = ffmpeg.probe(audio_path)
    audio_duration = float(probe["format"]["duration"])

    fixed_duration = 2 + 5 + 3
    remaining_time = max(0.5, audio_duration - fixed_duration)

    add_image(news_img, remaining_time, 2)

    # Optional – remove this line if you want to skip the thank-you image
    add_image(thank_img, 3, 3)

    # Step 4: Write concat file
    concat_path = os.path.join("output", "concat.txt")
    with open(concat_path, "w") as f:
        for filename, duration in zip(frame_paths, durations):
            f.write(f"file '{filename}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frame_paths[-1]}'\n")  # Repeat last to apply duration

    # Step 5: Change working directory temporarily
    original_cwd = os.getcwd()
    os.chdir("output")

    try:
        video_input = ffmpeg.input("concat.txt", format="concat", safe=0)
        audio_input = ffmpeg.input("output_polly.mp3")

        (
            ffmpeg
            .output(video_input, audio_input, os.path.basename(output_video),
                    vcodec="libx264", acodec="aac", pix_fmt="yuv420p", shortest=None)
            .run(overwrite_output=True)
        )

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown FFmpeg error"
        print(f"❌ FFmpeg failed: {error_msg}")
        return None

    finally:
        os.chdir(original_cwd)
