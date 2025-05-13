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

    # Step 2: Resize and save images as .jpg
    for i, image_path in enumerate(image_files):
        img = Image.open(image_path)
        rgb_img = img.convert("RGB")
        resized_img = rgb_img.resize((1280, 720))
        frame_path = f"output/frame_{i:03d}.jpg"
        resized_img.save(frame_path)

    # Step 3: Check if audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Polly audio not found.")
        return None

    # Step 4: Generate video using ffmpeg
    try:
        (
            ffmpeg
            .input("output/frame_%03d.jpg", framerate=1 / image_duration)
            .output(audio_path, output_video,
                    vcodec='libx264', acodec='aac',
                    pix_fmt='yuv420p',
                    shortest=None)
            .run(overwrite_output=True)
        )
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed: {e.stderr.decode()}")
        return None
