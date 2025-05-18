from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""You are a financial content creator writing for Indian retail traders. Based on the following pre-market report:

\"\"\"{report_text}\"\"\"

Write a short, energetic YouTube Shorts script that is in "HINGLISH language", not english totally:
- Starts with the signature line: "Good morning".
- Sounds like a Indian retail trader helping a fellow trader prep for the day — in simple, conversational Hinglish.
- Focuses only on relevant Indian market updates — NIFTY, SENSEX, BANK NIFTY, and any important macro news affecting the market.
- Filters out irrelevant or incomplete stock data and skips vague or non-actionable stock lists.
- Avoids robotic tone, filler words, hype, or hard Hindi words. All numbers should be in English.
- Avoid terms like “dosto”, “upar-niche”, or overly technical jargon.
- Keeps the script natural and casual.
- Ends with: a call to like, share, and subscribe for daily reports, and a question to spark engagement in the comments.

Respond only with the final script."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful financial scriptwriter for YouTube Shorts, focused on Indian traders."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
