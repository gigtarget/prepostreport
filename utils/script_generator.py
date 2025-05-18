from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_youtube_script_from_report(report_text):
    prompt = f"""आप एक भारतीय रिटेल ट्रेडर हैं जो प्री-मार्केट रिपोर्ट के आधार पर YouTube Shorts स्क्रिप्ट तैयार कर रहे हैं।

\"\"\"{report_text}\"\"\"

एक शॉर्ट, ऊर्जा से भरी स्क्रिप्ट लिखिए जो:
- "Good morning" से शुरू हो
- ज्यादातर **हिंदी में हो**, सिर्फ ज़रूरत पड़ने पर English words यूज़ करें (जैसे index के नाम, percentage, technical terms)
- NIFTY, SENSEX, BANK NIFTY और कोई भी ज़रूरी आर्थिक खबर को कवर करे
- जिन कंपनियों का price या बदलाव नहीं दिया गया हो, उन्हें skip करे
- ज़्यादा डेटा या भारी भरकम शब्दों से बचे, बात सीधी और trader के काम की होनी चाहिए
- ऐसे words ना use करें जैसे “upar gaya”, “naya rule aaya hai”, “IPO aa sakta hai”, “thoda”, “dhyaan dena” — script में casual hinglish की बजाय साफ़, समझदार हिंदी इस्तेमाल करें
- आवाज़ robotic या clickbait नहीं होनी चाहिए — सच्ची, मददगार और प्रोफेशनल trader जैसी लगनी चाहिए
- आख़िर में एक friendly CTA जोड़ें — like, share, subscribe करने के लिए कहें और एक सिंपल सवाल पूछें comments में engagement के लिए

सिर्फ फाइनल स्क्रिप्ट दें — कोई narrator नोट या अतिरिक्त जानकारी नहीं।
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "आप एक भारतीय स्टॉक मार्केट एनालिस्ट हैं जो YouTube Shorts के लिए ज्यादातर हिंदी में ट्रेडिंग अपडेट स्क्रिप्ट लिखते हैं। बातचीत प्रोफेशनल और सीधी होनी चाहिए, casual hinglish का इस्तेमाल नहीं होना चाहिए।"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )

    return response.choices[0].message.content.strip()
