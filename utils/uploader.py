import os
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_railway(video_path, title, description, tags=None, privacy="unlisted"):
    """
    Uploads a video to YouTube using OAuth2 credentials stored as environment variables.

    Required Environment Variables:
        - YOUTUBE_CLIENT_ID
        - YOUTUBE_CLIENT_SECRET
        - YOUTUBE_REFRESH_TOKEN
    """
    # Load credentials from environment
    creds = Credentials(
        None,
        refresh_token=os.getenv("YOUTUBE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("YOUTUBE_CLIENT_ID"),
        client_secret=os.getenv("YOUTUBE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/youtube.upload"]
    )

    # Refresh access token
    creds.refresh(google.auth.transport.requests.Request())

    # Initialize YouTube API client
    youtube = build("youtube", "v3", credentials=creds)

    # Prepare request body
    request_body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or [],
            "categoryId": "22"  # Category: People & Blogs
        },
        "status": {
            "privacyStatus": privacy
        }
    }

    # Load video file
    media_file = MediaFileUpload(video_path)

    # Upload video
    request = youtube.videos().insert(
        part="snippet,status",
        body=request_body,
        media_body=media_file
    )

    try:
        response = request.execute()
        print(f"✅ Video uploaded: https://www.youtube.com/watch?v={response['id']}")
        return response['id']
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None
