import pandas as pd
import yfinance as yf


def fetch_data(symbol, period="1y", interval="1d"):
    data = yf.download(symbol, period=period, interval=interval, progress=False)
    data.dropna(inplace=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[0] if isinstance(c, tuple) else c for c in data.columns]
    return data
