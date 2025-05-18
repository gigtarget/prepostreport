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

        current_price = round(data["regularMarketPrice"], 2)
        previous_close = round(data["previousClose"], 2)
        change = round(current_price - previous_close, 2)
        change_pct = round((change / previous_close) * 100, 2)

        arrow = "▲" if change > 0 else "▼" if change < 0 else "⏸"
        sentiment = (
            "Bullish" if change_pct > 0.4 else
            "Slight Bullish" if 0 < change_pct <= 0.4 else
            "Neutral" if abs(change_pct) < 0.2 else
            "Slight Bearish" if -0.4 <= change_pct < 0 else
            "Bearish"
        )

        return {
            "label": label,
            "price": current_price,
            "change_pts": change,
            "change_pct": change_pct,
            "arrow": arrow,
            "sentiment": sentiment
        }

    except Exception:
        return {
            "label": label,
            "price": "❌",
            "change_pts": "❌",
            "change_pct": "❌",
            "arrow": "⛔",
            "sentiment": "Unavailable"
        }

# ------------------ MARKET NEWS FETCH ------------------ #
def get_et_market_articles(limit=5):
    rss_url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    feed = feedparser.parse(rss_url)
    top_articles = []

    forbidden_phrases = [
        "stocks to buy", "stocks to watch", "these", "top", "who", "why",
        "multibagger", "hot stocks", "must buy", "recommend", "price target", "talk", "predict", "what", "want", "smart", "stocks", "tip",
        "whom", "whose", "when", "where", "which", "how", "how much", "how many", "how far", "how long", "how often", "how come", "this", "that", "those",
        "head and shoulders", "double top", "double bottom", "triple top", "triple bottom",
        "rounding top", "rounding bottom", "cup and handle", "island reversal", "diamond top", "diamond bottom",
        "ascending triangle", "descending triangle", "symmetrical triangle", "falling wedge", "rising wedge",
        "rectangle pattern", "bullish flag", "bearish flag", "bullish pennant", "bearish pennant", "broadening formation",
        "megaphone pattern", "channel up", "channel down", "gap up", "gap down", "breakout", "retest",
        "hammer", "inverted hammer", "bullish engulfing", "bearish engulfing", "morning star", "evening star",
        "piercing line", "dark cloud cover", "three white soldiers", "three black crows", "doji", "dragonfly doji",
        "gravestone doji", "spinning top", "marubozu", "says", "shooting star", "harami", "tweezer top", "tweezer bottom"
    ]

    for entry in feed.entries:
        title = entry.title.strip()
        if any(phrase in title.lower() for phrase in forbidden_phrases):
            continue

        top_articles.append({
            "title": title
        })

        if len(top_articles) >= limit:
            break

    return top_articles
