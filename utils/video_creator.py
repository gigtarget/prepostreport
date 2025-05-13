import os
from glob import glob
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # Step 1: Collect and sort image files
    image_files = sorted(glob("output/*.png"))
    if not image_files:
        print("❌ No images found to create video.")
        return None

    # Step 2: Convert to .jpg
    for i, image_path in enumerate(image_files):
        img = Image.open(image_path).convert("RGB")
        img = img.resize((1280, 720))
        frame_path = f"output/frame_{i:03d}.jpg"
        img.save(frame_path)

    # Step 3: Confirm audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Step 4: Combine using FFmpeg
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1 / image_duration)
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
        print(f"❌ FFmpeg failed: {e.stderr.decode()}")
        return None
