import os
import ffmpeg
from glob import glob
from PIL import Image

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # Step 1: Collect and sort image files
    image_files = sorted(glob("output/*.png"))
    if not image_files:
        print("❌ No images found to create video.")
        return

    # Step 2: Resize and convert images to same format if needed
    for i, image_path in enumerate(image_files):
        img = Image.open(image_path)
        rgb_img = img.convert('RGB')
        resized_img = rgb_img.resize((1280, 720))  # Ensure all frames are same size
        save_path = f"output/frame_{i:03d}.jpg"
        resized_img.save(save_path)

    # Step 3: Use ffmpeg-python to generate video from frames and audio
    try:
        (
            ffmpeg
            .input('output/frame_%03d.jpg', framerate=1 / image_duration)
            .input('output/output_polly.mp3')
            .output(output_video, vcodec='libx264', acodec='aac', shortest=None, pix_fmt='yuv420p')
            .run(overwrite_output=True)
        )
        print(f"✅ Final video saved to: {output_video}")
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg Error: {e.stderr.decode()}")
