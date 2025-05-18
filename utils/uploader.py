import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import google.auth.transport.requests

def upload_video_railway(video_path, title, description, tags=None, privacy="public"):
    creds = Credentials(
        None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    creds.refresh(google.auth.transport.requests.Request())
    youtube = build("youtube", "v3", credentials=creds)

    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    media_file = MediaFileUpload(video_path)
    request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media_file)

    try:
        response = request.execute()
        print("✅ Video uploaded: https://www.youtube.com/watch?v=" + response["id"])
    except Exception as e:
        print("❌ Upload failed:", e)
