import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video=os.path.abspath("output/final_video.mp4")):
    os.makedirs("output", exist_ok=True)

    # ✅ Manually defined image order and durations
    frames = [
        ("output/date.png", 2),       # 2 seconds
        ("output/summary.png", 5),    # 5 seconds
        ("output/news.png", 3),       # 3 seconds
        # ("templates/thank.jpg", 2), # optional
    ]

    frame_paths = []

    # Convert to JPG and collect frame info
    for index, (img_path, duration) in enumerate(frames):
        if not os.path.exists(img_path):
            print(f"❌ Missing image: {img_path}")
            return None

        img = Image.open(img_path).convert("RGB")
        frame_name = f"frame_{index:03d}.jpg"
        frame_path = os.path.join("output", frame_name)
        img.save(frame_path)
        frame_paths.append((frame_name, duration))

    # Ensure audio exists
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    # Create concat file
    concat_path = os.path.join("output", "concat.txt")
    with open(concat_path, "w") as f:
        for filename, duration in frame_paths:
            f.write(f"file '{filename}'\n")
            f.write(f"duration {duration}\n")
        # repeat last frame to apply duration correctly
        f.write(f"file '{frame_paths[-1][0]}'\n")

    # Generate video with FFmpeg
    original_cwd = os.getcwd()
    os.chdir("output")

    try:
        video_input = ffmpeg.input("concat.txt", format="concat", safe=0)
        audio_input = ffmpeg.input("output_polly.mp3")

        ffmpeg.output(
            video_input,
            audio_input,
            os.path.basename(output_video),
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            shortest=None
        ).run(overwrite_output=True)

        print(f"✅ Final video saved: {output_video}")
        return os.path.abspath(output_video)

    except ffmpeg.Error as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown FFmpeg error"
        print(f"❌ FFmpeg failed: {error_msg}")
        return None

    finally:
        os.chdir(original_cwd)
