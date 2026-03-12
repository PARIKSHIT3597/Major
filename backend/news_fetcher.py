from datetime import datetime, timedelta
import yfinance as yf

def fetch_news_rss(symbol, max_articles=5):
    """Fetch news from Yahoo Finance RSS feed for a given symbol"""
    try:
        # Get stock ticker
        ticker = yf.Ticker(symbol)
        
        # Try to get news from yfinance
        news_list = ticker.news[:max_articles]
        
        articles = []
        for news_item in news_list:
            title = news_item.get("title", "")
            summary = news_item.get("summary", "")
            # Only add if we have at least a title
            if title:
                articles.append({
                    "title": title,
                    "summary": summary,
                    "link": news_item.get("link", ""),
                    "publisher": news_item.get("publisher", "Unknown"),
                    "pub_date": datetime.fromtimestamp(news_item.get("providerPublishTime", 0)).isoformat() if news_item.get("providerPublishTime") else datetime.now().isoformat()
                })

        print(f"Yahoo news for {symbol}: {len(news_list) if news_list else 0} articles")

        # If we got valid articles, return them
        if articles:
            return articles
        else:
            # Fall back to mock news if API returns empty or invalid data
            return get_mock_news(symbol, max_articles)
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")
        # Return mock news if API fails
        return get_mock_news(symbol, max_articles)

def get_mock_news(symbol, max_articles=5):
    """Generate mock news when API is unavailable"""
    news_templates = {
        "AAPL": [
            {"title": f"{symbol} announces new product line", "summary": "Tech giant reveals innovative products expected to boost revenue.", "sentiment": "positive"},
            {"title": f"{symbol} reports strong quarterly earnings", "summary": "Company exceeds analyst expectations with record profits.", "sentiment": "positive"},
            {"title": f"{symbol} faces supply chain challenges", "summary": "Manufacturing delays may impact future deliveries.", "sentiment": "negative"},
        ],
        "MSFT": [
            {"title": f"{symbol} expands cloud services", "summary": "Company continues to dominate cloud computing market.", "sentiment": "positive"},
            {"title": f"{symbol} announces AI partnerships", "summary": "Strategic alliances to advance artificial intelligence capabilities.", "sentiment": "positive"},
        ],
        "BTC-USD": [
            {"title": "Bitcoin adoption increases globally", "summary": "More institutions adopt cryptocurrency as payment method.", "sentiment": "positive"},
            {"title": "Regulatory concerns affect crypto market", "summary": "Government regulations create uncertainty for investors.", "sentiment": "negative"},
        ],
        "ETH-USD": [
            {"title": "Ethereum network upgrades show promise", "summary": "Technical improvements enhance transaction efficiency.", "sentiment": "positive"},
            {"title": "DeFi market shows volatility", "summary": "Decentralized finance sector experiences fluctuations.", "sentiment": "neutral"},
        ]
    }
    
    templates = news_templates.get(symbol, [
        {"title": f"{symbol} market update", "summary": "Latest developments affecting the asset.", "sentiment": "neutral"}
    ])
    
    articles = []
    for i, template in enumerate(templates[:max_articles]):
        articles.append({
            "title": template["title"],
            "summary": template["summary"],
            "link": "",  # No real link for mock news - frontend will hide "Read more"
            "publisher": "Financial News (sample)",
            "pub_date": (datetime.now() - timedelta(hours=i+1)).isoformat()
        })
    
    return articles

