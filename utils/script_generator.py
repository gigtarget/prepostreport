from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""You are a financial content creator writing for Indian retail traders. Based on the following pre-market report:

\"\"\"{report_text}\"\"\"

Write a short, clear, human-sounding YouTube script for pre market report in english that mostly data is about yestewrday market performance and todays top news so talk in that context:
- Start with signature line, "Good morning. Let’s get you ready for today's market session". as it is. 
- Includes only relevant and helpful info for a trader, about Indian market updates (NIFTY/SENSEX/BANK NIFTY if available).
- See if out of any news can have impact on stock market, which is not related to stocks. 
- Sounds like a human is speaking (not robotic)
- Skips news or stocks which has unavailable stock data about companies only.
- Avoid news like these 4 or 5 stock are above or below this level.
- Avoids overloading with too many numbers.
- Uses simple, conversational very basic english.
- Request to like, share, and subscribe for daily report and ask for something engaging in comments. 

The tone should feel helpful and energetic, like you're helping a fellow trader quickly prep for their day. No narrator notes, just the word-by-word script.

Respond with only the final script.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional content creator for Indian financial YouTube . Your tone is mostly english with simple, relatable words — no slang. Your goal is to sound human, helpful, and relevant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
