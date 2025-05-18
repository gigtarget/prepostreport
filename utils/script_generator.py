from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""You are a financial content creator writing for Indian retail traders. Based on the following pre-market report:

\"\"\"{report_text}\"\"\"

Write a short, clear, human-sounding YouTube Shorts script for pre market report that:
- Start with signature line, "Good morning". as it is. 
- Includes only relevant and helpful info for a trader, about Indian market updates (NIFTY/SENSEX/BANK NIFTY if available).
- See if out of any news can have impact on stock market, which is not related to stocks. 
- Sounds like a human is speaking (not robotic)
- Skips news or stocks which has unavailable stock data about companies only.
- Avoid news like these 4 or 5 stock are above or below this level.
- Avoids overloading with too many numbers, Do **not** use casual slang like "dosto", "upar gaya", "IPO aa sakta hai", "thoda", or "dhyaan dena".
- Uses simple, conversational Hinglish, use words like up, down, percentage.
- Request to like, share, and subscribe for daily report and ask for something engaging in comments. 

The tone should feel helpful and energetic, like you're helping a fellow trader quickly prep for their day. The script should be in Hinglish — mostly english but to make viewer comfortable we can use few hindi words to help and relate with script better , keep all numbers in english don't use any strong hindi word which will be difficult to understand use english word in that case, like a real Indian trader talking. No narrator notes, just the word-by-word script.

Respond with only the final script.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional content creator for Indian financial YouTube Shorts. Your tone is mostly English with simple, relatable Hindi — no slang or poetic Hindi. Your goal is to sound human, helpful, and relevant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
