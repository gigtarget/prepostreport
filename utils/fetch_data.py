import requests
import feedparser
from newspaper import Article

# ------------------ STOCK PRICE FETCH ------------------ #
def get_yahoo_price_with_change(symbol, label):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "region": "IN",
        "lang": "en-IN",
        "includePrePost": False,
        "interval": "2m",
        "range": "1d"
    }

    try:
        res = requests.get(url, params=params, headers=headers, timeout=10)
        res.raise_for_status()
        data = res.json()["chart"]["result"][0]["meta"]

        current_price = round(data["regularMarketPrice"])
        previous_close = round(data["previousClose"])
        change = round(current_price - previous_close)

        arrow = "▲" if change > 0 else "▼" if change < 0 else "⏸"
        sign = "+" if change > 0 else ""

        return f"{label}: {current_price} {arrow} {sign}{change}"

    except Exception:
        return f"{label}: Unavailable"

# ------------------ NEWS FETCH ------------------ #
def get_et_market_articles():
    rss_url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    feed = feedparser.parse(rss_url)
    top_articles = []

    # ❌ Forbidden keywords that suggest stock tips or recommendations
    forbidden_phrases = [
        "stocks to buy", "stocks to watch", "these", "top", "who", "why",
        "multibagger", "hot stocks", "must buy", "recommend", "price target", "talk", "predict", "what", "want", "smart", "stocks",  "tip"
    ]

    for entry in feed.entries:
        title_lower = entry.title.lower()
        if any(phrase in title_lower for phrase in forbidden_phrases):
            continue  # ❌ Skip risky investment articles

        try:
            article = Article(entry.link)
            article.download()
            article.parse()

            cleaned_text = "\n".join(
                line.strip()
                for line in article.text.splitlines()
                if line.strip() and "subscribe" not in line.lower()
            )

            top_articles.append({
                "title": article.title,
                "published": entry.published,
                "content": cleaned_text[:600] + "..."
            })

        except Exception:
            # Fallback to summary if parsing fails
            top_articles.append({
                "title": entry.title,
                "published": entry.published,
                "content": (entry.get("summary") or "Content unavailable")[:300] + "..."
            })

        if len(top_articles) >= 5:
            break  # ✅ Limit to first 5 safe articles

    return top_articles
