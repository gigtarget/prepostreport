import os
from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
from glob import glob

def create_video_from_images_and_audio(output_video="output/final_video.mp4"):
    os.makedirs("output", exist_ok=True)

    # Load audio to get duration
    audio_path = "output/output_polly.mp3"
    if not os.path.exists(audio_path):
        print("❌ Audio not found.")
        return None

    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # Load images
    date_img = "output/date.png"
    summary_img = "output/summary.png"
    report_img = "output/news.png"  # assuming this is the third one
    thank_img = "templates/thank.jpg"

    # Clip durations
    date_dur = 2
    summary_dur = 4
    thank_dur = 3
    report_dur = max(total_duration - (date_dur + summary_dur + thank_dur), 1)

    def make_clip(path, duration):
        return ImageClip(path).set_duration(duration)

    clips = [
        make_clip(date_img, date_dur),
        make_clip(summary_img, summary_dur),
        make_clip(report_img, report_dur),
        make_clip(thank_img, thank_dur)
    ]

    final = concatenate_videoclips(clips, method="compose").set_audio(audio)

    try:
        final.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
        print(f"✅ Final video saved to: {output_video}")
        return output_video
    except Exception as e:
        print(f"❌ Failed to export video: {e}")
        return None
