import os
from glob import glob
import moviepy.editor as mpy  # ✅ Fix import path

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # Step 1: Collect and sort image files
    image_files = sorted(glob("output/*.png"))
    if not image_files:
        print("❌ No images found to create video.")
        return None

    # Step 2: Create image clips
    clips = []
    for image_path in image_files:
        clip = mpy.ImageClip(image_path).set_duration(image_duration).resize((1280, 720))
        clips.append(clip)

    # Step 3: Concatenate video
    final_clip = mpy.concatenate_videoclips(clips, method="compose")

    # Step 4: Attach audio
    audio_path = "output/output_polly.mp3"
    if os.path.exists(audio_path):
        audio = mpy.AudioFileClip(audio_path)
        final_clip = final_clip.set_audio(audio)
    else:
        print("❌ Audio file not found.")
        return None

    # Step 5: Export video
    try:
        final_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ MoviePy video generation failed: {e}")
        return None
