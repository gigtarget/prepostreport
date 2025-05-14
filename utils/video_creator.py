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

        frame_paths = []
        for i, img_path in enumerate(image_paths):
            img = Image.open(img_path).convert("RGB")
            jpg_path = f"output/frame_{i:03d}.jpg"
            img.save(jpg_path)
            frame_paths.append(jpg_path)

        # Get audio duration
        probe = ffmpeg.probe(audio_path)
        duration = float(probe["format"]["duration"])
        duration_per_frame = duration / len(frame_paths)

        # Write frame list with correct relative paths
        with open("output/frames.txt", "w") as f:
            for path in frame_paths:
                relative_path = os.path.basename(path)
                f.write(f"file '{relative_path}'\n")
                f.write(f"duration {duration_per_frame}\n")
            f.write(f"file '{os.path.basename(frame_paths[-1])}'\n")  # Hold last frame

        # Generate video
        os.system(
            f"cd output && ffmpeg -y -f concat -safe 0 -i frames.txt -i ../{audio_path} "
            f"-shortest -c:v libx264 -pix_fmt yuv420p -c:a aac ../{output_video}"
        )

        print(f"✅ Final video saved to: {output_video}")
        return output_video

    except Exception as e:
        print(f"❌ Error generating video: {e}")
        return None
