import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error
from data_fetcher import fetch_data
from predictor import predict_price

def calculate_mse(actual, predicted):
    """
    Calculate Mean Squared Error (MSE)
    MSE = mean((actual - predicted)^2)
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted arrays must have the same length")
    mse = mean_squared_error(actual, predicted)
    return mse

def calculate_mae(actual, predicted):
    """
    Calculate Mean Absolute Error (MAE)
    MAE = mean(|actual - predicted|)
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted arrays must have the same length")
    mae = mean_absolute_error(actual, predicted)
    return mae

def calculate_rmse(actual, predicted):
    """
    Calculate Root Mean Squared Error (RMSE)
    RMSE = sqrt(mean((actual - predicted)^2))
    """
    if len(actual) != len(predicted):
        raise ValueError("Actual and predicted arrays must have the same length")
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    return rmse

def evaluate_model_performance(symbol, test_periods=30):
    """
    Evaluate model performance by comparing predictions with actual prices
    Returns MSE, MAE, RMSE metrics
    """
    try:
        # Fetch historical data
        data = fetch_data(symbol, period="1y", interval="1d")
        
        if len(data) < test_periods + 10:
            return {
                "error": "Insufficient data for evaluation",
                "mse": None,
                "mae": None,
                "rmse": None
            }
        
        # Use last N periods for testing
        test_data = data.tail(test_periods)
        actual_prices = test_data["Close"].values
        
        # Generate predictions for each period
        predicted_prices = []
        historical_data = data.head(len(data) - test_periods)
        
        for i in range(test_periods):
            # Simulate prediction using historical data up to that point
            temp_data = pd.concat([historical_data, test_data.iloc[:i+1]])
            if len(temp_data) >= 10:
                try:
                    # Use last 10 prices for prediction
                    closes = temp_data["Close"].values[-10:]
                    # Simple prediction (can be replaced with actual model)
                    predicted = float(closes[-5:].mean())
                    predicted_prices.append(predicted)
                except:
                    predicted_prices.append(float(temp_data["Close"].iloc[-1]))
            else:
                predicted_prices.append(float(temp_data["Close"].iloc[-1]))
        
        # Calculate metrics
        mse = calculate_mse(actual_prices, predicted_prices)
        mae = calculate_mae(actual_prices, predicted_prices)
        rmse = calculate_rmse(actual_prices, predicted_prices)
        
        return {
            "symbol": symbol,
            "mse": round(mse, 4),
            "mae": round(mae, 4),
            "rmse": round(rmse, 4),
            "test_periods": test_periods,
            "actual_mean": round(float(np.mean(actual_prices)), 2),
            "predicted_mean": round(float(np.mean(predicted_prices)), 2)
        }
    except Exception as e:
        return {
            "error": str(e),
            "mse": None,
            "mae": None,
            "rmse": None
        }

def get_all_performance_metrics(symbol):
    """
    Get all performance metrics including MSE, MAE, RMSE, Sharpe Ratio, and Max Drawdown
    """
    try:
        # Get prediction metrics
        prediction_metrics = evaluate_model_performance(symbol)
        
        # Get risk metrics (includes Sharpe Ratio and Max Drawdown)
        from risk import calculate_risk
        data = fetch_data(symbol, period="1y", interval="1d")
        risk_metrics = calculate_risk(data)
        
        return {
            "symbol": symbol,
            "prediction_metrics": {
                "mse": prediction_metrics.get("mse"),
                "mae": prediction_metrics.get("mae"),
                "rmse": prediction_metrics.get("rmse")
            },
            "risk_metrics": {
                "sharpe_ratio": risk_metrics.get("sharpe_ratio"),
                "max_drawdown": risk_metrics.get("max_drawdown"),
                "max_drawdown_pct": risk_metrics.get("max_drawdown_pct")
            }
        }
    except Exception as e:
        return {
            "error": str(e),
            "symbol": symbol
        }

