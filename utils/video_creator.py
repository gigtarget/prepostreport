import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video=os.path.abspath("output/final_video.mp4")):
    os.makedirs("output", exist_ok=True)

    frames = [
        ("output/date.png", 2),
        ("output/summary.png", 5),
        ("output/news.png", 3),
    ]

    frame_paths = []
    for index, (img_path, duration) in enumerate(frames):
        if not os.path.exists(img_path):
            print(f"❌ Missing image: {img_path}")
            return None
        img = Image.open(img_path).convert("RGB")
        frame_name = f"frame_{index:03d}.jpg"
        frame_path = os.path.join("output", frame_name)
        img.save(frame_path)
        frame_paths.append((frame_name, duration))

    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio file not found.")
        return None

    concat_file_path = os.path.join("output", "concat.txt")
    with open(concat_file_path, "w") as f:
        for filename, duration in frame_paths:
            f.write(f"file '{filename}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frame_paths[-1][0]}'\n")

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

        print(f"✅ Final video saved to: {output_video}")
        return os.path.abspath(output_video)

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return None

    finally:
        os.chdir(original_cwd)
