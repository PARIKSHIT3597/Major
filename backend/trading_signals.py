import pandas as pd
import numpy as np
from data_fetcher import fetch_data
from predictor import predict_price
from risk import calculate_risk
from sentiment_analyzer import analyze_news_sentiment
from news_fetcher import fetch_news_rss

def calculate_rsi(data, period=14):
    """Calculate Relative Strength Index (RSI)"""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else 50

def calculate_macd(data, fast=12, slow=26, signal=9):
    """Calculate MACD (Moving Average Convergence Divergence)"""
    ema_fast = data['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['Close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line.iloc[-1] if not macd_line.empty else 0,
        'signal': signal_line.iloc[-1] if not signal_line.empty else 0,
        'histogram': histogram.iloc[-1] if not histogram.empty else 0
    }

def calculate_moving_averages(data):
    """Calculate Simple Moving Averages (SMA)"""
    sma_20 = data['Close'].rolling(window=20).mean().iloc[-1] if len(data) >= 20 else data['Close'].iloc[-1]
    sma_50 = data['Close'].rolling(window=50).mean().iloc[-1] if len(data) >= 50 else data['Close'].iloc[-1]
    sma_200 = data['Close'].rolling(window=200).mean().iloc[-1] if len(data) >= 200 else data['Close'].iloc[-1]
    
    return {
        'sma_20': float(sma_20),
        'sma_50': float(sma_50),
        'sma_200': float(sma_200)
    }

def calculate_bollinger_bands(data, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = data['Close'].rolling(window=period).mean()
    std = data['Close'].rolling(window=period).std()
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    current_price = data['Close'].iloc[-1]
    upper = upper_band.iloc[-1] if not upper_band.empty else current_price
    lower = lower_band.iloc[-1] if not lower_band.empty else current_price
    middle = sma.iloc[-1] if not sma.empty else current_price
    
    return {
        'upper': float(upper),
        'middle': float(middle),
        'lower': float(lower)
    }

def generate_trading_signal(symbol):
    """
    Generate comprehensive trading signal (BUY/SELL/HOLD) based on:
    - Technical indicators (RSI, MACD, Moving Averages, Bollinger Bands)
    - Price prediction
    - Risk assessment
    - News sentiment
    """
    try:
        # Fetch market data
        data = fetch_data(symbol, period="6mo", interval="1d")
        
        if len(data) < 20:
            return {
                "signal": "HOLD",
                "confidence": 0.5,
                "reason": "Insufficient data for analysis",
                "indicators": {}
            }
        
        # Calculate technical indicators
        rsi = calculate_rsi(data)
        macd_data = calculate_macd(data)
        moving_averages = calculate_moving_averages(data)
        bollinger = calculate_bollinger_bands(data)
        
        # Get price prediction
        try:
            prediction = predict_price(symbol)
            predicted_price = prediction.get('predicted_price', 0)
            current_price = prediction.get('current_price', data['Close'].iloc[-1])
            price_change_pct = ((predicted_price - current_price) / current_price) * 100 if current_price > 0 else 0
        except:
            current_price = float(data['Close'].iloc[-1])
            predicted_price = current_price
            price_change_pct = 0
        
        # Get risk assessment
        try:
            risk_data = calculate_risk(data)
            risk_score = risk_data.get('risk_score', 50)
            risk_level = risk_data.get('risk_level', 'Medium')
        except:
            risk_score = 50
            risk_level = 'Medium'
        
        # Get news sentiment
        try:
            articles = fetch_news_rss(symbol, max_articles=5)
            sentiment_data = analyze_news_sentiment(articles)
            sentiment_score = sentiment_data.get('overall_sentiment', 0.0)
            sentiment_label = sentiment_data.get('overall_label', 'neutral')
        except:
            sentiment_score = 0.0
            sentiment_label = 'neutral'
        
        # Signal scoring system
        buy_score = 0
        sell_score = 0
        reasons = []
        
        # RSI signals (0-100, >70 overbought, <30 oversold)
        if rsi < 30:
            buy_score += 2
            reasons.append(f"RSI indicates oversold condition ({rsi:.1f})")
        elif rsi > 70:
            sell_score += 2
            reasons.append(f"RSI indicates overbought condition ({rsi:.1f})")
        elif 30 <= rsi <= 50:
            buy_score += 1
            reasons.append(f"RSI in neutral-bullish range ({rsi:.1f})")
        elif 50 < rsi <= 70:
            sell_score += 1
            reasons.append(f"RSI in neutral-bearish range ({rsi:.1f})")
        
        # MACD signals
        if macd_data['macd'] > macd_data['signal'] and macd_data['histogram'] > 0:
            buy_score += 2
            reasons.append("MACD shows bullish crossover")
        elif macd_data['macd'] < macd_data['signal'] and macd_data['histogram'] < 0:
            sell_score += 2
            reasons.append("MACD shows bearish crossover")
        
        # Moving Average signals
        if current_price > moving_averages['sma_20'] > moving_averages['sma_50']:
            buy_score += 2
            reasons.append("Price above key moving averages (bullish trend)")
        elif current_price < moving_averages['sma_20'] < moving_averages['sma_50']:
            sell_score += 2
            reasons.append("Price below key moving averages (bearish trend)")
        
        # Bollinger Bands signals
        if current_price < bollinger['lower']:
            buy_score += 1
            reasons.append("Price near lower Bollinger Band (potential bounce)")
        elif current_price > bollinger['upper']:
            sell_score += 1
            reasons.append("Price near upper Bollinger Band (potential reversal)")
        
        # Price prediction signals
        if price_change_pct > 2:
            buy_score += 2
            reasons.append(f"Model predicts {price_change_pct:.1f}% price increase")
        elif price_change_pct < -2:
            sell_score += 2
            reasons.append(f"Model predicts {price_change_pct:.1f}% price decrease")
        elif price_change_pct > 0:
            buy_score += 1
        else:
            sell_score += 1
        
        # Sentiment signals
        if sentiment_score > 0.2:
            buy_score += 1
            reasons.append(f"Positive news sentiment ({sentiment_label})")
        elif sentiment_score < -0.2:
            sell_score += 1
            reasons.append(f"Negative news sentiment ({sentiment_label})")
        
        # Risk adjustment (higher risk reduces confidence)
        if risk_level == 'High':
            buy_score *= 0.7
            sell_score *= 0.7
            reasons.append("High risk detected - reduced signal strength")
        elif risk_level == 'Low':
            buy_score *= 1.1
            sell_score *= 1.1
        
        # Determine final signal
        signal_diff = buy_score - sell_score
        total_score = buy_score + sell_score
        
        if signal_diff > 2:
            signal = "BUY"
            confidence = min(0.95, 0.5 + (signal_diff / 10))
        elif signal_diff < -2:
            signal = "SELL"
            confidence = min(0.95, 0.5 + (abs(signal_diff) / 10))
        else:
            signal = "HOLD"
            confidence = 0.5 + (abs(signal_diff) / 20)
        
        # If no strong reasons, default to HOLD
        if not reasons:
            signal = "HOLD"
            reasons.append("Mixed signals - waiting for clearer trend")
        
        return {
            "signal": signal,
            "confidence": round(confidence, 2),
            "reasons": reasons[:5],  # Top 5 reasons
            "indicators": {
                "rsi": round(rsi, 2),
                "macd": {
                    "macd": round(macd_data['macd'], 2),
                    "signal": round(macd_data['signal'], 2),
                    "histogram": round(macd_data['histogram'], 2)
                },
                "moving_averages": {
                    "sma_20": round(moving_averages['sma_20'], 2),
                    "sma_50": round(moving_averages['sma_50'], 2),
                    "sma_200": round(moving_averages['sma_200'], 2)
                },
                "bollinger_bands": {
                    "upper": round(bollinger['upper'], 2),
                    "middle": round(bollinger['middle'], 2),
                    "lower": round(bollinger['lower'], 2)
                },
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "price_change_pct": round(price_change_pct, 2),
                "risk_score": round(risk_score, 1),
                "risk_level": risk_level,
                "sentiment_score": round(sentiment_score, 3),
                "sentiment_label": sentiment_label
            },
            "scores": {
                "buy_score": round(buy_score, 2),
                "sell_score": round(sell_score, 2),
                "signal_diff": round(signal_diff, 2)
            }
        }
    
    except Exception as e:
        print(f"Error generating trading signal for {symbol}: {e}")
        return {
            "signal": "HOLD",
            "confidence": 0.5,
            "reason": f"Error in analysis: {str(e)}",
            "indicators": {}
        }

