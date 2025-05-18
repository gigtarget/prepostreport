from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""You are a financial content creator writing for Indian retail traders. Based on the following pre-market report:

\"\"\"{report_text}\"\"\"

Write a short, energetic YouTube video script that:
- Starts with the signature line: "Good morning"
- Use **mostly HINGLISH**, but include simple and natural ENGLISH.
- Do **not** use casual slang like "dosto", "upar gaya", "IPO aa sakta hai", "thoda", or "dhyaan dena"
- Avoid overly formal Hindi terms like "arthik", "vyavsayik", or "soochakank"
- Focus only on relevant index updates (NIFTY, SENSEX, BANK NIFTY) and key macroeconomic headlines
- Ignore company news if price or change data is missing
- Don’t overload with numbers — just useful, actionable info
- End with a call to like, share, and subscribe + ask a question in comments for engagement
- The tone should feel like one Indian trader talking to another — helpful, human, and clear

Only return the final spoken script — no notes or headers.
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
