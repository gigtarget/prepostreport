import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Step 1: Use the market image
    image_path = "output/final_image.png"
    if not os.path.exists(image_path):
        print("❌ final_image.png not found.")
        return None

    # Step 2: Convert to .jpg
    img = Image.open(image_path).convert("RGB")
    frame_path = "output/frame_000.jpg"
    img.save(frame_path, quality=100)

    # Step 3: Confirm audio
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

    frame_duration = audio_duration

    # Step 5: Create first video (with final_image)
    try:
        video_input = ffmpeg.input("output/frame_%03d.jpg", framerate=1 / frame_duration)
        audio_input = ffmpeg.input(audio_path)

        (
            ffmpeg
            .output(
                video_input, audio_input, output_video,
                vcodec="libx264",
                acodec="aac",
                crf=18,
                preset="slow",
                pix_fmt="yuv420p",
                shortest=None
            )
            .run(overwrite_output=True)
        )

        print(f"✅ Final video saved to: {output_video}")

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed on final_video.mp4:\n{e.stderr.decode()}")

    # Step 6: Create second video (with insta_image.jpg)
    insta_image_path = "output/insta_image.jpg"
    insta_frame_path = "output/frame_insta.jpg"
    insta_video_output = "output/insta_video.mp4"

    if os.path.exists(insta_image_path):
        try:
            Image.open(insta_image_path).convert("RGB").save(insta_frame_path, quality=100)

            video_input = ffmpeg.input(insta_frame_path, framerate=1 / frame_duration)
            audio_input = ffmpeg.input(audio_path)

            (
                ffmpeg
                .output(
                    video_input, audio_input, insta_video_output,
                    vcodec="libx264",
                    acodec="aac",
                    crf=18,
                    preset="slow",
                    pix_fmt="yuv420p",
                    shortest=None
                )
                .run(overwrite_output=True)
            )

            print(f"✅ Instagram video saved to: {insta_video_output}")

        except Exception as e:
            print(f"❌ Failed to create insta_video.mp4:\n{e}")
    else:
        print("⚠️ insta_image.jpg not found — skipping second video.")

    return output_video
