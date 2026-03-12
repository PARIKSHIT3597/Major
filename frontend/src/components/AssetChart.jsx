import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

export default function AssetChart({ title, data, marketData }) {
  const getTrendColor = (trend) => {
    return trend === "Bullish" ? "#22c55e" : "#ef4444";
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3>{title}</h3>
        <span className="subtitle">Live price movement</span>
            {marketData && (
          <div className="card-meta">
            <span className="trend-badge" style={{ color: getTrendColor(marketData.trend) }}>
              {marketData.trend}
            </span>
            {marketData.sentiment && (
              <span className="sentiment-indicator" style={{ 
                color: marketData.sentiment.label === "positive" ? "#22c55e" : 
                       marketData.sentiment.label === "negative" ? "#ef4444" : "#94a3b8"
              }}>
                {marketData.sentiment.label === "positive" ? "📈" : 
                 marketData.sentiment.label === "negative" ? "📉" : "➡️"}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />

            {/* X AXIS – Time */}
            <XAxis
              dataKey="time"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              tickLine={false}
            />

            {/* Y AXIS – Price */}
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              tickFormatter={(value) => `$${value}`}
              domain={["auto", "auto"]}
              tickLine={false}
            />

            {/* Tooltip */}
            <Tooltip
              contentStyle={{
                backgroundColor: "#020617",
                border: "1px solid #334155",
                borderRadius: "6px",
                color: "#e5e7eb"
              }}
              labelStyle={{ color: "#38bdf8" }}
              formatter={(value) => [`$${value}`, "Price"]}
            />

            <Line
              type="monotone"
              dataKey="price"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
              isAnimationActive={true}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
