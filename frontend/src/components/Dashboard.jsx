import { useEffect, useState } from "react";
import AssetChart from "./AssetChart";
import NewsSentiment from "./NewsSentiment";
import { socket } from "../socket";

const ASSETS = [
  { symbol: "AAPL", base: 190 },
  { symbol: "MSFT", base: 410 },
  { symbol: "BTC-USD", base: 43000 },
  { symbol: "ETH-USD", base: 2300 }
];

export default function Dashboard() {
  const [data, setData] = useState({});
  const [marketData, setMarketData] = useState({});
  const [selectedAsset, setSelectedAsset] = useState(null);
  const [socketConnected, setSocketConnected] = useState(false);

  // Initialize with some default data points for charts
  useEffect(() => {
    const initialData = {};
    ASSETS.forEach(asset => {
      const points = [];
      const now = new Date();
      for (let i = 19; i >= 0; i--) {
        const time = new Date(now - i * 2000);
        points.push({
          time: time.toLocaleTimeString(),
          price: asset.base + (Math.random() - 0.5) * asset.base * 0.01
        });
      }
      initialData[asset.symbol] = points;
    });
    setData(initialData);
  }, []);

  useEffect(() => {
    // Handle socket connection
    const handleConnect = () => {
      setSocketConnected(true);
      // Start socket stream
      socket.emit("start_stream", { symbols: ASSETS.map(a => a.symbol) });
    };

    const handleDisconnect = () => {
      setSocketConnected(false);
    };

    socket.on("connect", handleConnect);
    socket.on("disconnect", handleDisconnect);

    // Listen for market updates
    const handleMarketUpdate = (updates) => {
      setMarketData(prev => {
        const updated = { ...prev };
        updates.forEach(update => {
          updated[update.symbol] = update;
        });
        return updated;
      });

      // Update chart data from socket updates
      setData(prev => {
        const updated = { ...prev };
        updates.forEach(update => {
          updated[update.symbol] = [
            ...(updated[update.symbol] || []).slice(-19),
            {
              time: new Date().toLocaleTimeString(),
              price: update.current_price
            }
          ];
        });
        return updated;
      });
    };

    socket.on("market_update", handleMarketUpdate);

    // If already connected, emit start_stream
    if (socket.connected) {
      handleConnect();
    }

    return () => {
      socket.off("connect", handleConnect);
      socket.off("disconnect", handleDisconnect);
      socket.off("market_update", handleMarketUpdate);
    };
  }, []);

  // Fallback: Generate mock data if socket is not connected
  useEffect(() => {
    if (!socketConnected) {
      const interval = setInterval(() => {
        setData(prev => {
          const updated = { ...prev };
          ASSETS.forEach(asset => {
            const last = updated[asset.symbol]?.slice(-1)[0]?.price ?? asset.base;
            updated[asset.symbol] = [
              ...(updated[asset.symbol] || []).slice(-19),
              {
                time: new Date().toLocaleTimeString(),
                price: last + (Math.random() - 0.5) * asset.base * 0.005
              }
            ];
          });
          return updated;
        });
      }, 2000);

      return () => clearInterval(interval);
    }
  }, [socketConnected]);

  // Fetch initial news sentiment for all assets
  useEffect(() => {
    const fetchInitialSentiment = async () => {
      for (const asset of ASSETS) {
        try {
          const response = await fetch(`http://localhost:5001/api/news/${asset.symbol}`);
          const data = await response.json();
          if (data.sentiment) {
            setMarketData(prev => ({
              ...prev,
              [asset.symbol]: {
                ...prev[asset.symbol],
                sentiment: {
                  overall: data.sentiment.overall_sentiment,
                  label: data.sentiment.overall_label,
                  positive_count: data.sentiment.positive_count,
                  negative_count: data.sentiment.negative_count,
                  neutral_count: data.sentiment.neutral_count,
                  price_impact_percentage: data.price_impact?.impact_percentage || 0
                }
              }
            }));
          }
        } catch (error) {
          console.error(`Error fetching sentiment for ${asset.symbol}:`, error);
        }
      }
    };

    fetchInitialSentiment();
    const interval = setInterval(fetchInitialSentiment, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "16px" }}>
        <div>
          <h1>Real-time Market Dashboard with News Sentiment Analysis</h1>
          <p className="subtitle-header">
            Track market movements and see how news sentiment affects prices
          </p>
        </div>
        <div style={{
          padding: "8px 16px",
          borderRadius: "6px",
          backgroundColor: socketConnected ? "rgba(34, 197, 94, 0.2)" : "rgba(239, 68, 68, 0.2)",
          color: socketConnected ? "#22c55e" : "#ef4444",
          fontSize: "0.85rem",
          fontWeight: 600
        }}>
          {socketConnected ? "🟢 Connected" : "🔴 Disconnected"}
        </div>
      </div>

      <div className="grid">
        {ASSETS.map(a => (
          <div key={a.symbol} onClick={() => setSelectedAsset(selectedAsset === a.symbol ? null : a.symbol)}>
            <AssetChart
              title={a.symbol}
              data={data[a.symbol] || []}
              marketData={marketData[a.symbol]}
            />
            {selectedAsset === a.symbol && marketData[a.symbol]?.sentiment && (
              <NewsSentiment
                symbol={a.symbol}
                sentiment={marketData[a.symbol].sentiment}
              />
            )}
          </div>
        ))}
      </div>

      {/* News Sentiment Panel */}
      <div className="news-panel">
        <h2>News Sentiment Overview</h2>
        <div className="news-grid">
          {ASSETS.map(asset => (
            marketData[asset.symbol]?.sentiment && (
              <NewsSentiment
                key={asset.symbol}
                symbol={asset.symbol}
                sentiment={marketData[asset.symbol].sentiment}
              />
            )
          ))}
        </div>
      </div>
    </div>
  );
}
