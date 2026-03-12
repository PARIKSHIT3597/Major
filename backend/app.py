from flask import Flask, jsonify
from flask_socketio import SocketIO
import time
import threading
import yfinance as yf
from news_fetcher import fetch_news_rss
from sentiment_analyzer import analyze_news_sentiment, calculate_sentiment_impact

try:
    from predictor import predict_price
    PREDICTOR_AVAILABLE = True
except Exception as e:
    print(f"Predictor not available: {e}")
    PREDICTOR_AVAILABLE = False

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

SYMBOLS = ["AAPL", "MSFT", "BTC-USD", "ETH-USD"]
prices = {}  # Live prices cache
prediction_cache = {}  # ML predictions (refresh every 30 sec)
prediction_cache_time = {}

# Cache for news and sentiment (refresh every 5 minutes)
news_cache = {}
sentiment_cache = {}
cache_timestamps = {}

DEFAULT_SENTIMENT = {
    "overall_sentiment": 0.0,
    "overall_label": "neutral",
    "positive_count": 0,
    "negative_count": 0,
    "neutral_count": 0,
    "articles": [],
    "price_impact": {"impact_percentage": 0.0, "price_impact": 0.0},
}


def fetch_live_price(symbol):
    """Fetch current price from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        price = None
        try:
            info = ticker.fast_info
            price = getattr(info, "last_price", None) or getattr(info, "lastPrice", None)
        except Exception:
            pass
        if price is None or price <= 0:
            for period, interval in [("1d", "1m"), ("5d", "1d"), ("1mo", "1d")]:
                hist = ticker.history(period=period, interval=interval)
                if not hist.empty:
                    price = float(hist["Close"].iloc[-1])
                    break
        return float(price) if price and price > 0 else None
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None


def get_ml_prediction(symbol):
    """Get ML prediction (cached 30 sec)"""
    now = time.time()
    if symbol in prediction_cache_time and (now - prediction_cache_time[symbol]) < 30:
        return prediction_cache.get(symbol)
    if PREDICTOR_AVAILABLE:
        try:
            pred = predict_price(symbol)
            prediction_cache[symbol] = pred
            prediction_cache_time[symbol] = now
            return pred
        except Exception as e:
            print(f"Prediction error for {symbol}: {e}")
    return None


def _fetch_and_cache_sentiment(symbol):
    try:
        articles = fetch_news_rss(symbol, max_articles=5)
        sentiment_data = analyze_news_sentiment(articles)
        current_price = prices.get(symbol) or fetch_live_price(symbol) or 0
        impact = calculate_sentiment_impact(sentiment_data["overall_sentiment"], current_price)
        result = {**sentiment_data, "price_impact": impact, "last_updated": time.time()}
        news_cache[symbol] = articles
        sentiment_cache[symbol] = result
        cache_timestamps[symbol] = time.time()
    except Exception as e:
        print(f"Error fetching sentiment for {symbol}: {e}")


def get_news_sentiment(symbol):
    """Get news and sentiment (cached 5 min). Never blocks - fetches in background on miss."""
    current_time = time.time()
    if symbol in cache_timestamps and (current_time - cache_timestamps[symbol]) < 300:
        return sentiment_cache.get(symbol, DEFAULT_SENTIMENT)
    threading.Thread(target=_fetch_and_cache_sentiment, args=(symbol,), daemon=True).start()
    return DEFAULT_SENTIMENT

def stream_market(symbols):
    global prices
    prev_prices = {}
    while True:
        results = []
        # Fetch live prices
        for s in symbols:
            price = fetch_live_price(s)
            if price is not None:
                prices[s] = price

        for s in symbols:
            current_price = prices.get(s)
            if current_price is None:
                continue

            sentiment_info = get_news_sentiment(s)

            # ML prediction (cached 30 sec)
            pred = get_ml_prediction(s)
            if pred:
                predicted_price = pred["predicted_price"]
                trend = pred["trend"]
            else:
                sentiment_factor = sentiment_info.get("overall_sentiment", 0.0) * 0.005
                predicted_price = round(current_price * (1 + sentiment_factor), 2)
                prev = prev_prices.get(s)
                trend = "Bullish" if (prev is None or current_price >= prev) else "Bearish"
                if sentiment_info.get("overall_label") == "positive":
                    trend = "Bullish"
                elif sentiment_info.get("overall_label") == "negative":
                    trend = "Bearish"
            prev_prices[s] = current_price

            results.append({
                "symbol": s,
                "current_price": round(current_price, 2),
                "predicted_price": predicted_price,
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

        if results:
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

        current_price = prices.get(symbol) or fetch_live_price(symbol) or 0
        impact = calculate_sentiment_impact(sentiment_data["overall_sentiment"], current_price)

        response = jsonify({
            "symbol": symbol,
            "sentiment": sentiment_data,
            "price_impact": impact,
            "current_price": round(current_price, 2)
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
    symbols = SYMBOLS
    result = {}
    
    for symbol in symbols:
        try:
            sentiment_info = get_news_sentiment(symbol)
            price = prices.get(symbol) or fetch_live_price(symbol) or 0
            result[symbol] = {
                "sentiment": sentiment_info,
                "current_price": round(price, 2)
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
