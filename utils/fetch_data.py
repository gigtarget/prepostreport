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

    except Exception as e:
        return f"{label}: Unavailable"

# ------------------ NEWS FETCH ------------------ #
def get_et_market_articles():
    rss_url = "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"
    feed = feedparser.parse(rss_url)
    top_articles = []

    for entry in feed.entries[:5]:
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

        except Exception as e:
            # Fallback
            top_articles.append({
                "title": entry.title,
                "published": entry.published,
                "content": (entry.get("summary") or "Content unavailable")[:300] + "..."
            })

    return top_articles
