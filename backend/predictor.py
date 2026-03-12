import pickle
import numpy as np
from data_fetcher import fetch_data

model = None
scaler = None

try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Warning: Could not load model.pkl: {e}")

try:
    with open("scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
except Exception as e:
    print(f"Warning: Could not load scaler.pkl: {e}")


def predict_price(symbol):
    data = fetch_data(symbol)
    closes = data["Close"].values if "Close" in data.columns else data.iloc[:, 0].values

    if len(closes) < 100:
        # Need at least 100 days for LSTM
        if len(closes) < 10:
            raise ValueError("Not enough data")
        # Fallback: simple moving average
        current_price = float(closes[-1])
        predicted_price = float(np.mean(closes[-5:]))
        return {
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "trend": "Bullish" if predicted_price > current_price else "Bearish",
        }

    current_price = float(closes[-1])

    if model is not None and scaler is not None:
        try:
            # Last 100 days, scaled
            last_100 = closes[-100:].reshape(-1, 1)
            scaled = scaler.transform(last_100)
            X = scaled.reshape(1, 100, 1)
            prediction = model.predict(X, verbose=0)
            predicted_price = float(scaler.inverse_transform(prediction)[0, 0])
        except Exception as e:
            print(f"Error using model for prediction: {e}")
            predicted_price = float(np.mean(closes[-5:]))
    else:
        predicted_price = float(np.mean(closes[-5:]))

    return {
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "trend": "Bullish" if predicted_price > current_price else "Bearish",
    }
