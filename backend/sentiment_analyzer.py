from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

# Initialize the VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def analyze_sentiment(text):
    """
    Analyze sentiment of text using VADER Sentiment Analyzer
    Returns a sentiment score between -1 (very negative) and 1 (very positive)
    """
    if not text or not isinstance(text, str):
        return {
            "compound": 0.0,
            "positive": 0.0,
            "neutral": 1.0,
            "negative": 0.0,
            "label": "neutral"
        }
    
    # Clean the text
    text = re.sub(r'[^\w\s]', '', text)
    
    # Get sentiment scores
    scores = analyzer.polarity_scores(text)
    
    # Determine label
    compound = scores['compound']
    if compound >= 0.05:
        label = "positive"
    elif compound <= -0.05:
        label = "negative"
    else:
        label = "neutral"
    
    return {
        "compound": round(compound, 3),
        "positive": round(scores['pos'], 3),
        "neutral": round(scores['neu'], 3),
        "negative": round(scores['neg'], 3),
        "label": label
    }

def analyze_news_sentiment(articles):
    """
    Analyze sentiment for a list of news articles
    Returns aggregated sentiment and individual article sentiments
    """
    if not articles:
        return {
            "overall_sentiment": 0.0,
            "overall_label": "neutral",
            "positive_count": 0,
            "negative_count": 0,
            "neutral_count": 0,
            "articles": []
        }
    
    sentiments = []
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for article in articles:
        # Analyze title and summary together
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        sentiment = analyze_sentiment(text)
        
        article_with_sentiment = {
            **article,
            "sentiment": sentiment
        }
        sentiments.append(article_with_sentiment)
        
        if sentiment["label"] == "positive":
            positive_count += 1
        elif sentiment["label"] == "negative":
            negative_count += 1
        else:
            neutral_count += 1
    
    # Calculate overall sentiment (weighted average)
    if sentiments:
        overall_compound = sum(s["sentiment"]["compound"] for s in sentiments) / len(sentiments)
        
        if overall_compound >= 0.05:
            overall_label = "positive"
        elif overall_compound <= -0.05:
            overall_label = "negative"
        else:
            overall_label = "neutral"
    else:
        overall_compound = 0.0
        overall_label = "neutral"
    
    return {
        "overall_sentiment": round(overall_compound, 3),
        "overall_label": overall_label,
        "positive_count": positive_count,
        "negative_count": negative_count,
        "neutral_count": neutral_count,
        "articles": sentiments
    }

def calculate_sentiment_impact(sentiment_score, base_price):
    """
    Calculate potential price impact based on sentiment
    This is a simplified model - in reality, sentiment impact varies
    """
    # Assume sentiment can affect price by up to 2% (bullish or bearish)
    impact_percentage = sentiment_score * 0.02
    price_impact = base_price * impact_percentage
    
    return {
        "impact_percentage": round(impact_percentage * 100, 2),
        "price_impact": round(price_impact, 2)
    }

