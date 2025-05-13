import os
from glob import glob
import moviepy.editor as mpy

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # ✅ Step 1: Get all PNG images
    image_files = sorted(glob("output/*.png"))
    if not image_files:
        print("❌ No images found.")
        return None

    # ✅ Step 2: Turn each image into a video clip
    clips = [mpy.ImageClip(img).set_duration(image_duration).resize((1280, 720)) for img in image_files]

    # ✅ Step 3: Combine clips
    video = mpy.concatenate_videoclips(clips, method="compose")

    # ✅ Step 4: Attach audio
    audio_path = "output/output_polly.mp3"
    if os.path.exists(audio_path):
        audio = mpy.AudioFileClip(audio_path)
        video = video.set_audio(audio)
    else:
        print("❌ Audio not found.")
        return None

    # ✅ Step 5: Export
    try:
        video.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ Failed to export video: {e}")
        return None
