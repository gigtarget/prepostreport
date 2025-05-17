import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Step 1: Use the new single image
    image_path = "output/final_image.png"
    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None

    # Step 2: Convert to .jpg with max quality
    img = Image.open(image_path).convert("RGB")
    frame_path = "output/frame_000.jpg"
    img.save(frame_path, quality=100)  # MAX QUALITY

    # Step 3: Confirm audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Step 4: Get audio duration
    try:
        probe = ffmpeg.probe(audio_path)
        audio_duration = float(probe["format"]["duration"])
    except Exception as e:
        print(f"❌ Failed to probe audio duration: {e}")
        return None

    frame_duration = audio_duration  # Only one frame shown for entire duration

    # Step 5: Combine frame and audio into video
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1 / frame_duration)
        audio_input = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(
                video_input, audio_input, output_video,
                vcodec="libx264",
                acodec="aac",
                crf=18,              # Lower = better quality (0–51, recommended: 18–23)
                preset="slow",       # Better compression and quality
                pix_fmt="yuv420p",
                shortest=None
            )
            .run(overwrite_output=True)
        )

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed:\n{e.stderr.decode()}")
        return None
