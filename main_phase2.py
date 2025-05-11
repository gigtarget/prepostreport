import os
from dotenv import load_dotenv
load_dotenv()

# Check if approval was granted
if not os.path.exists("output/awaiting_approval.flag"):
    print("❌ Approval flag not found. Please run Phase 1 first.")
    exit()

# ✅ Imports
from utils.script_generator import generate_youtube_script_from_report
from utils.audio_generator import generate_audio_with_polly
from utils.video_creator import create_video_from_images_and_audio
from utils.telegram_alert import send_telegram_message, send_telegram_file

# ------------------ CONTINUE FROM SAVED REPORT ------------------ #
with open("output/report.txt", "r", encoding="utf-8") as f:
    report_lines = f.readlines()

# Generate script
send_telegram_message("✍️ Generating script...")
script = generate_youtube_script_from_report(report_lines)
with open("output/script.txt", "w", encoding="utf-8") as f:
    f.write(script)

# Generate audio
send_telegram_message("🔊 Generating voiceover...")
generate_audio_with_polly(script, "output/audio.mp3")

# Create video
send_telegram_message("🎞️ Creating video...")
create_video_from_images_and_audio(["output/preview_image.jpg"], "output/audio.mp3", "output/final_video.mp4")

# Send final outputs to Telegram
send_telegram_file("output/audio.mp3", "🎧 Voiceover")
send_telegram_file("output/final_video.mp4", "🎬 Final Video")

# Cleanup
os.remove("output/awaiting_approval.flag")
os.remove("output/.lock")

send_telegram_message("✅ All done. Ready for the next report.")
