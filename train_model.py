#!/usr/bin/env python3
"""
Train the stock prediction model (same logic as Stock_Market_Prediction_Model_Creation.ipynb)
Saves model.pkl to backend/ for use by the app.
"""
import os
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from keras.layers import Dense, Dropout, LSTM
from keras.models import Sequential
import pickle

print("Fetching GOOG stock data (2012-2022)...")
data = yf.download("GOOG", start="2012-01-01", end="2022-12-21", progress=False)
data.dropna(inplace=True)
data.reset_index(inplace=True)

# Handle MultiIndex columns from yfinance
if isinstance(data.columns, pd.MultiIndex):
    data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
if "Close" not in data.columns and "GOOG" in data.columns:
    data["Close"] = data["GOOG"]

print(f"Data shape: {data.shape}")

# Train/test split (80/20)
data_train = pd.DataFrame(data.Close[0 : int(len(data) * 0.80)])
data_test = pd.DataFrame(data.Close[int(len(data) * 0.80) : len(data)])

# Scale
scaler = MinMaxScaler(feature_range=(0, 1))
data_train_scale = scaler.fit_transform(data_train)

# Create sequences (100 days -> next day)
x, y = [], []
for i in range(100, data_train_scale.shape[0]):
    x.append(data_train_scale[i - 100 : i])
    y.append(data_train_scale[i, 0])
x, y = np.array(x), np.array(y)

# Reshape for LSTM: (samples, timesteps, features)
x = np.reshape(x, (x.shape[0], x.shape[1], 1))

print("Building LSTM model...")
model = Sequential()
model.add(LSTM(units=50, activation="relu", return_sequences=True, input_shape=(x.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=60, activation="relu", return_sequences=True))
model.add(Dropout(0.3))
model.add(LSTM(units=80, activation="relu", return_sequences=True))
model.add(Dropout(0.4))
model.add(LSTM(units=120, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(units=1))

model.compile(optimizer="adam", loss="mean_squared_error")

print("Training (50 epochs)...")
model.fit(x, y, epochs=50, batch_size=32, verbose=1)

# Save to backend/
os.makedirs("backend", exist_ok=True)
model.save("backend/Stock Predictions Model.keras")
with open("backend/model.pkl", "wb") as f:
    pickle.dump(model, f)

# Also save scaler for inference (predictor will need it)
with open("backend/scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

print("Model saved successfully to backend/model.pkl")
print("Scaler saved to backend/scaler.pkl")
