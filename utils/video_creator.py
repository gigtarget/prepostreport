import os
from glob import glob
from moviepy.editor import ImageClip, concatenate_videoclips, AudioFileClip

def create_video_from_images_and_audio(output_video="output/final_video.mp4", image_duration=5):
    os.makedirs("output", exist_ok=True)

    # Step 1: Collect and sort images
    image_files = sorted(glob("output/*.png"))
    if not image_files:
        print("❌ No images found to create video.")
        return None

    # Step 2: Create clips
    clips = []
    for image_path in image_files:
        clip = ImageClip(image_path).set_duration(image_duration).resize((1280, 720))
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")

    # Step 3: Add audio
    audio_path = "output/output_polly.mp3"
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        video = video.set_audio(audio)
    else:
        print("❌ Audio file not found.")
        return None

    # Step 4: Export
    try:
        video.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ MoviePy failed: {e}")
        return None
