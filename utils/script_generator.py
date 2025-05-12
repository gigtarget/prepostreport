from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""
You are a financial content creator writing for Indian retail traders. Based on the following pre-market report:

\"\"\"{report_text}\"\"\"

Write a short, clear, human-sounding YouTube Shorts script that:
- Start with signature line, Good morning, traders. Let’s gear up for the day under 5 minutes.
- Includes only relevant and helpful info for a trader, about Indian market updates (NIFTY/SENSEX/BANK NIFTY if available).
- See if out of any news can have impact on stock market, which is not related to stocks. 
- Sounds like a human is speaking (not robotic)
- Skips news or stocks which has unavailable stock data about companies only.
- Avoid news like these 4 or 5 stock are above or below this level.
- Avoids overloading with too many numbers.
- Uses simple, conversational Hinglish, use words like up, down, percentage,  

The tone should feel helpful and energetic, like you're helping a fellow trader quickly prep for their day. The script should be in Hinglish — words which are related to stock market you can generate in english, rest all script mostly in  Hinglish with a little English, keep all numbers in english don't use any strong hindi word which will be difficult to understand use english word in that case, like a real Indian trader talking. No narrator notes, just the word-by-word script.

Respond with only the final script.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful financial scriptwriter for YouTube Shorts, focused on Indian traders."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
