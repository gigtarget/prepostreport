import os
import requests

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def generate_dalle_image_from_prompt(prompt_text, filename="news_slide_1"):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "dall-e-3",  # Use "dall-e-2" if you don’t have access to 3
        "prompt": prompt_text[:900],  # Keep prompt short
        "n": 1,
        "size": "1024x1024"  # Most stable size
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        image_url = response.json()["data"][0]["url"]

        # Download the image
        img_data = requests.get(image_url).content
        os.makedirs("output", exist_ok=True)
        with open(f"output/{filename}.png", "wb") as f:
            f.write(img_data)

        print(f"✅ DALL·E image saved: output/{filename}.png")

    except Exception as e:
        print(f"❌ Failed to generate DALL·E image: {e}")
