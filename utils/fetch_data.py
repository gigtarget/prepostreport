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
def get_et_market_articles(limit=None):
    try:
        feed_url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
        feed = feedparser.parse(feed_url)
        articles = []

        for entry in feed.entries:
            title = entry.get("title", "")
            if title:
                articles.append("• " + title.strip())

        if limit:
            articles = articles[:limit]

        return "\n".join(articles) if articles else "No news available."

    except Exception as e:
        return f"Error fetching news: {e}"
