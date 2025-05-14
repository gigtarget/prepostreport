import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # 🔧 Step 1: Manually define images and durations (in seconds)
    frames = [
        ("output/date.png", 2),
        ("output/summary.png", 5),
        ("output/news.png", 3),
        # ("templates/thank.jpg", 2),  # Optional thank-you frame
    ]

    frame_paths = []

    # Step 2: Convert each image to JPG with original size
    for index, (img_path, duration) in enumerate(frames):
        img = Image.open(img_path).convert("RGB")
        frame_name = f"frame_{index:03d}.jpg"
        frame_path = os.path.join("output", frame_name)
        img.save(frame_path)
        frame_paths.append((frame_name, duration))

    # Step 3: Confirm audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Step 4: Write FFmpeg concat file
    concat_path = os.path.join("output", "concat.txt")
    with open(concat_path, "w") as f:
        for filename, duration in frame_paths:
            f.write(f"file '{filename}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frame_paths[-1][0]}'\n")  # repeat last image for padding

    # Step 5: Change working dir to output
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
        return os.path.abspath(output_video)

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown FFmpeg error"
        print(f"❌ FFmpeg failed: {error_msg}")
        return None

    finally:
        os.chdir(original_cwd)
