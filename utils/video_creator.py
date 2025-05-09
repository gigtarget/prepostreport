import os
import subprocess
from glob import glob

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # Step 1: Collect images in desired order
    image_files = sorted(glob("output/*.png"))  # adjust sort if needed

    # Step 2: Create file list for ffmpeg
    with open("output/frames.txt", "w") as f:
        for img in image_files:
            f.write(f"file '{img}'\n")
            f.write(f"duration {image_duration}\n")

        # Repeat last image for freeze frame at end
        if image_files:
            f.write(f"file '{image_files[-1]}'\n")

    # Step 3: Build ffmpeg command
    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "output/frames.txt",
        "-i", "output/output_polly.mp3",
        "-c:v", "libx264",
        "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-shortest",
        output_video
    ]

    print("🎬 Rendering video...")
    subprocess.run(cmd, check=True)
    print(f"✅ Final video saved to: {output_video}")
