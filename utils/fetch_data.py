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
        return f"{label}: ❌ Error fetching data"

# ------------------ MARKET NEWS FETCH ------------------ #
def get_et_market_articles(limit=5):  # ✅ ADD limit support
    rss_url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    feed = feedparser.parse(rss_url)
    top_articles = []

    forbidden_phrases = [
        "stocks to buy", "stocks to watch", "these", "top", "who", "why",
        "multibagger", "hot stocks", "must buy", "recommend", "price target", "talk", "predict", "what", "want", "smart", "stocks", "tip",
        "whom", "whose", "when", "where", "which", "how", "how much", "how many", "how far", "how long", "how often", "how come", "this", "that", "those",
        "head and shoulders", "inverse head and shoulders", "double top", "double bottom", "triple top", "triple bottom",
        "rounding top", "rounding bottom", "cup and handle", "island reversal", "diamond top", "diamond bottom",
        "ascending triangle", "descending triangle", "symmetrical triangle", "falling wedge", "rising wedge",
        "rectangle pattern", "bullish flag", "bearish flag", "bullish pennant", "bearish pennant", "broadening formation",
        "megaphone pattern", "channel up", "channel down", "gap up", "gap down", "breakout", "retest",
        "hammer", "inverted hammer", "bullish engulfing", "bearish engulfing", "morning star", "evening star",
        "piercing line", "dark cloud cover", "three white soldiers", "three black crows", "doji", "dragonfly doji",
        "gravestone doji", "spinning top", "marubozu", "hanging man", "shooting star", "harami", "tweezer top", "tweezer bottom"
    ]

    for entry in feed.entries:
        title = entry.title.strip()
        if any(phrase in title.lower() for phrase in forbidden_phrases):
            continue

        try:
            article = Article(entry.link)
            article.download()
            article.parse()

            content = "\n".join(
                line.strip()
                for line in article.text.splitlines()
                if line.strip() and "subscribe" not in line.lower()
            )

            top_articles.append({
                "title": title,
                "published": entry.get("published", "Unknown"),
                "content": (content[:600] + "...") if len(content) > 600 else content
            })

        except Exception:
            fallback_summary = entry.get("summary", "Content unavailable").strip()
            top_articles.append({
                "title": title,
                "published": entry.get("published", "Unknown"),
                "content": (fallback_summary[:300] + "...") if len(fallback_summary) > 300 else fallback_summary
            })

        if len(top_articles) >= limit:  # ✅ USE limit
            break

    return top_articles
