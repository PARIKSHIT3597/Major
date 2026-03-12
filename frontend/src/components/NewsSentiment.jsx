import { useEffect, useState } from "react";

export default function NewsSentiment({ symbol, sentiment }) {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchNews();
    const interval = setInterval(fetchNews, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [symbol]);

  const fetchNews = async () => {
    try {
      const response = await fetch(`http://localhost:5001/api/news/${symbol}`);
      const data = await response.json();
      if (data.sentiment && data.sentiment.articles) {
        setArticles(data.sentiment.articles.slice(0, 3)); // Show top 3 articles
      }
      setLoading(false);
    } catch (error) {
      console.error("Error fetching news:", error);
      setLoading(false);
    }
  };

  const getSentimentColor = (label) => {
    switch (label) {
      case "positive":
        return "#22c55e"; // green
      case "negative":
        return "#ef4444"; // red
      default:
        return "#94a3b8"; // gray
    }
  };

  const getSentimentIcon = (label) => {
    switch (label) {
      case "positive":
        return "📈";
      case "negative":
        return "📉";
      default:
        return "➡️";
    }
  };

  if (!sentiment) return null;

  return (
    <div className="news-sentiment-card">
      <div className="news-header">
        <h4>News Sentiment - {symbol}</h4>
        <div
          className="sentiment-badge"
          style={{ color: getSentimentColor(sentiment.label) }}
        >
          <span>{getSentimentIcon(sentiment.label)}</span>
          <span>{sentiment.label.toUpperCase()}</span>
        </div>
      </div>

      <div className="sentiment-stats">
        <div className="sentiment-stat">
          <span className="stat-label">Overall Score:</span>
          <span
            className="stat-value"
            style={{ color: getSentimentColor(sentiment.label) }}
          >
            {sentiment.overall > 0 ? "+" : ""}
            {(sentiment.overall * 100).toFixed(1)}%
          </span>
        </div>
        <div className="sentiment-stat">
          <span className="stat-label">Price Impact:</span>
          <span
            className="stat-value"
            style={{
              color:
                sentiment.price_impact_percentage > 0 ? "#22c55e" : "#ef4444",
            }}
          >
            {sentiment.price_impact_percentage > 0 ? "+" : ""}
            {sentiment.price_impact_percentage.toFixed(2)}%
          </span>
        </div>
      </div>

      <div className="news-articles">
        <h5>Latest News</h5>
        {loading ? (
          <div className="loading">Loading news...</div>
        ) : articles.length > 0 ? (
          articles.map((article, index) => (
            <div key={index} className="news-article">
              <div className="article-header">
                <span
                  className="article-sentiment"
                  style={{
                    color: getSentimentColor(article.sentiment?.label || "neutral"),
                  }}
                >
                  {getSentimentIcon(article.sentiment?.label || "neutral")}
                </span>
                <h6>{article.title}</h6>
              </div>
              <p className="article-summary">{article.summary}</p>
              <div className="article-footer">
                <span className="article-publisher">{article.publisher}</span>
                {article.link && !article.link.includes("example.com") && (
                  <a
                    href={article.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="article-link"
                  >
                    Read more →
                  </a>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="no-news">No recent news available</div>
        )}
      </div>
    </div>
  );
}

