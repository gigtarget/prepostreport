import os
from PIL import Image
import ffmpeg

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Manually defined sequence and durations
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

    concat_txt_path = os.path.join("output", "concat.txt")
    with open(concat_txt_path, "w") as f:
        for filename, duration in frame_paths:
            f.write(f"file '{filename}'\n")
            f.write(f"duration {duration}\n")
        f.write(f"file '{frame_paths[-1][0]}'\n")  # repeat last for padding

    original_cwd = os.getcwd()
    os.chdir("output")

    try:
        video_input = ffmpeg.input("concat.txt", format="concat", safe=0)
        audio_input = ffmpeg.input("output_polly.mp3")

        # OUTPUT TO RELATIVE PATH inside output/
        final_output = "final_video.mp4"

        ffmpeg.output(
            video_input,
            audio_input,
            final_output,
            vcodec="libx264",
            acodec="aac",
            pix_fmt="yuv420p",
            shortest=None
        ).run(overwrite_output=True)

        abs_video_path = os.path.abspath(final_output)
        print(f"✅ Final video saved at: {abs_video_path}")
        print(f"📂 File exists: {os.path.exists(abs_video_path)}")

        return abs_video_path

    except ffmpeg.Error as e:
        print(f"❌ FFmpeg failed: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        return None

    finally:
        os.chdir(original_cwd)
