from flask import Flask, jsonify
from flask_socketio import SocketIO
import time
import threading
import random
from news_fetcher import fetch_news_rss
from sentiment_analyzer import analyze_news_sentiment, calculate_sentiment_impact

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

prices = {
    "AAPL": 190,
    "MSFT": 410,
    "BTC-USD": 43000,
    "ETH-USD": 2300
}

# Cache for news and sentiment (refresh every 5 minutes)
news_cache = {}
sentiment_cache = {}
cache_timestamps = {}

def get_news_sentiment(symbol):
    """Get news and sentiment for a symbol (with caching)"""
    cache_key = symbol
    current_time = time.time()
    
    # Return cached data if it's less than 5 minutes old
    if cache_key in cache_timestamps and (current_time - cache_timestamps[cache_key]) < 300:
        return sentiment_cache.get(cache_key, {})
    
    # Fetch fresh news and analyze sentiment
    try:
        articles = fetch_news_rss(symbol, max_articles=5)
        sentiment_data = analyze_news_sentiment(articles)
        
        # Calculate price impact
        current_price = prices.get(symbol, 0)
        impact = calculate_sentiment_impact(sentiment_data["overall_sentiment"], current_price)
        
        result = {
            **sentiment_data,
            "price_impact": impact,
            "last_updated": current_time
        }
        
        # Update cache
        news_cache[cache_key] = articles
        sentiment_cache[cache_key] = result
        cache_timestamps[cache_key] = current_time
        
        return result
    except Exception as e:
        print(f"Error getting news sentiment for {symbol}: {e}")
        return {
            "overall_sentiment": 0.0,
            "overall_label": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "articles": [],
            "price_impact": {"impact_percentage": 0.0, "price_impact": 0.0}
        }

def stream_market(symbols):
    while True:
        results = []
        for s in symbols:
            # Get news sentiment
            sentiment_info = get_news_sentiment(s)
            
            # Adjust price based on sentiment (subtle impact)
            sentiment_factor = sentiment_info.get("overall_sentiment", 0.0) * 0.1
            base_change = random.uniform(-1, 1)
            sentiment_adjusted_change = base_change + sentiment_factor
            prices[s] += sentiment_adjusted_change
            
            # Determine trend based on sentiment and price movement
            trend = "Bullish" if sentiment_adjusted_change > 0 else "Bearish"
            if sentiment_info.get("overall_label") == "positive":
                trend = "Bullish"
            elif sentiment_info.get("overall_label") == "negative":
                trend = "Bearish"
            
            results.append({
                "symbol": s,
                "current_price": round(prices[s], 2),
                "predicted_price": round(prices[s] + random.uniform(1, 3), 2),
                "trend": trend,
                "risk_level": "Medium",
                "sentiment": {
                    "overall": sentiment_info.get("overall_sentiment", 0.0),
                    "label": sentiment_info.get("overall_label", "neutral"),
                    "positive_count": sentiment_info.get("positive_count", 0),
                    "negative_count": sentiment_info.get("negative_count", 0),
                    "neutral_count": sentiment_info.get("neutral_count", 0),
                    "price_impact_percentage": sentiment_info.get("price_impact", {}).get("impact_percentage", 0.0)
                }
            })

        socketio.emit("market_update", results)
        time.sleep(2)

@socketio.on("start_stream")
def start_stream(data):
    symbols = data["symbols"]
    threading.Thread(
        target=stream_market,
        args=(symbols,),
        daemon=True
    ).start()

@app.route("/api/news/<symbol>")
def get_news(symbol):
    """API endpoint to get news and sentiment for a specific symbol"""
    try:
        articles = fetch_news_rss(symbol, max_articles=10)
        sentiment_data = analyze_news_sentiment(articles)
        
        current_price = prices.get(symbol, 0)
        impact = calculate_sentiment_impact(sentiment_data["overall_sentiment"], current_price)
        
        response = jsonify({
            "symbol": symbol,
            "sentiment": sentiment_data,
            "price_impact": impact,
            "current_price": round(prices.get(symbol, 0), 2)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        print(f"Error in get_news: {e}")
        response = jsonify({"error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

@app.route("/api/news")
def get_all_news():
    """API endpoint to get news for all tracked symbols"""
    symbols = list(prices.keys())
    result = {}
    
    for symbol in symbols:
        try:
            sentiment_info = get_news_sentiment(symbol)
            result[symbol] = {
                "sentiment": sentiment_info,
                "current_price": round(prices.get(symbol, 0), 2)
            }
        except Exception as e:
            result[symbol] = {"error": str(e)}
    
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/api/health")
def health():
    """Health check endpoint"""
    response = jsonify({"status": "ok", "message": "Server is running"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    socketio.run(app, port=5001, debug=True)
