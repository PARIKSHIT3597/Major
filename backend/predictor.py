import pickle
import numpy as np
from data_fetcher import fetch_data

# Try to load the model, handle gracefully if keras is not available
model = None
try:
    with open("model.pkl", "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Warning: Could not load model.pkl: {e}")
    print("Price predictions will use a simple moving average fallback.")

def predict_price(symbol):
    data = fetch_data(symbol)
    closes = data["Close"].values

    if len(closes) < 10:
        raise ValueError("Not enough data")

    current_price = float(closes[-1])
    
    # If model is available, use it
    if model is not None:
        try:
            X = closes[-10:].reshape(1, -1)
            prediction = model.predict(X)
            prediction = np.asarray(prediction)
            predicted_price = float(prediction.flatten()[0])
        except Exception as e:
            print(f"Error using model for prediction: {e}")
            # Fallback to simple moving average
            predicted_price = float(closes[-5:].mean())
    else:
        # Fallback: Use simple moving average of last 5 days
        predicted_price = float(closes[-5:].mean())
    
    return {
        "current_price": round(current_price, 2),
        "predicted_price": round(predicted_price, 2),
        "trend": "Bullish" if predicted_price > current_price else "Bearish"
    }
