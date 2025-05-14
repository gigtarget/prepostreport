import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(
    output_video="output/final_video.mp4",
    image_paths=["output/final_image.png"],
    audio_path="output/output_polly.mp3"
):
    try:
        os.makedirs("output", exist_ok=True)

        # Convert PNGs to JPGs (FFmpeg sometimes prefers JPG)
        frame_paths = []
        for i, img_path in enumerate(image_paths):
            if img_path.lower().endswith(".png"):
                img = Image.open(img_path).convert("RGB")
                jpg_path = f"output/frame_{i:03d}.jpg"
                img.save(jpg_path)
                frame_paths.append(jpg_path)
            else:
                frame_paths.append(img_path)

        # Count duration from audio file
        probe = ffmpeg.probe(audio_path)
        duration = float(probe["format"]["duration"])
        duration_per_frame = duration / len(frame_paths)

        # Create FFmpeg input from images
        with open("output/frames.txt", "w") as f:
            for path in frame_paths:
                f.write(f"file '{path}'\n")
                f.write(f"duration {duration_per_frame}\n")

        f.write(f"file '{frame_paths[-1]}'\n")  # Show last frame until audio ends

        # Generate video using FFmpeg
        os.system(f"ffmpeg -y -f concat -safe 0 -i output/frames.txt -i {audio_path} -shortest -c:v libx264 -pix_fmt yuv420p -c:a aac {output_video}")

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return None
