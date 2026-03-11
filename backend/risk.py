import numpy as np
import pandas as pd
import yfinance as yf

def calculate_risk(data):
    """
    Calculate comprehensive risk metrics for an asset
    """
    if len(data) < 10:
        return {
            "risk_score": 50.0,
            "risk_level": "Medium",
            "volatility": 0.0,
            "max_drawdown": 0.0,
            "var_95": 0.0,
            "cvar_95": 0.0,
            "sharpe_ratio": 0.0,
            "beta": 1.0,
            "message": "Insufficient data for risk analysis"
        }
    
    returns = data["Close"].pct_change().dropna()
    
    if len(returns) < 2:
        return {
            "risk_score": 50.0,
            "risk_level": "Medium",
            "volatility": 0.0,
            "max_drawdown": 0.0,
            "var_95": 0.0,
            "cvar_95": 0.0,
            "sharpe_ratio": 0.0,
            "beta": 1.0,
            "message": "Insufficient returns data"
        }

    # 1. Volatility (Annualized)
    volatility = returns.std() * np.sqrt(252)
    
    # 2. Maximum Drawdown
    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()
    
    # 3. Value at Risk (VaR) - 95% confidence
    var_95 = np.percentile(returns, 5)  # 5th percentile (95% VaR)
    var_95_annual = var_95 * np.sqrt(252)
    
    # 4. Conditional Value at Risk (CVaR) - Expected loss beyond VaR
    cvar_95 = returns[returns <= var_95].mean() if len(returns[returns <= var_95]) > 0 else var_95
    cvar_95_annual = cvar_95 * np.sqrt(252)
    
    # 5. Sharpe Ratio (assuming risk-free rate of 0.02 or 2%)
    risk_free_rate = 0.02
    excess_returns = returns.mean() * 252 - risk_free_rate
    sharpe_ratio = excess_returns / (volatility) if volatility > 0 else 0
    
    # 6. Beta (correlation with market - using SPY as proxy)
    beta = calculate_beta(data, returns)
    
    # 7. Risk Score Calculation (weighted combination)
    # Normalize metrics to 0-100 scale
    volatility_score = min(volatility * 100, 100)  # Volatility as percentage
    drawdown_score = min(abs(max_drawdown) * 100, 100)  # Max drawdown as percentage
    var_score = min(abs(var_95_annual) * 100, 100)  # VaR as percentage
    
    # Weighted risk score
    score = (volatility_score * 0.4 + drawdown_score * 0.4 + var_score * 0.2)
    score = min(score, 100)
    
    # Risk level classification
    if score < 25:
        level = "Low"
    elif score < 50:
        level = "Medium-Low"
    elif score < 75:
        level = "Medium-High"
    else:
        level = "High"
    
    # Additional risk indicators
    risk_indicators = {
        "high_volatility": volatility > 0.3,  # >30% annual volatility
        "high_drawdown": abs(max_drawdown) > 0.2,  # >20% drawdown
        "negative_sharpe": sharpe_ratio < 0,
        "high_beta": beta > 1.5,  # More volatile than market
        "low_beta": beta < 0.5  # Less volatile than market
    }
    
    # Risk warnings
    warnings = []
    if risk_indicators["high_volatility"]:
        warnings.append("High volatility detected")
    if risk_indicators["high_drawdown"]:
        warnings.append("Significant drawdown risk")
    if risk_indicators["negative_sharpe"]:
        warnings.append("Negative risk-adjusted returns")
    if risk_indicators["high_beta"]:
        warnings.append("High sensitivity to market movements")
    
    return {
        "risk_score": round(score, 2),
        "risk_level": level,
        "volatility": round(volatility, 4),
        "volatility_pct": round(volatility * 100, 2),
        "max_drawdown": round(max_drawdown, 4),
        "max_drawdown_pct": round(abs(max_drawdown) * 100, 2),
        "var_95": round(var_95, 4),
        "var_95_pct": round(abs(var_95) * 100, 2),
        "var_95_annual": round(var_95_annual, 4),
        "cvar_95": round(cvar_95, 4),
        "cvar_95_pct": round(abs(cvar_95) * 100, 2),
        "cvar_95_annual": round(cvar_95_annual, 4),
        "sharpe_ratio": round(sharpe_ratio, 3),
        "beta": round(beta, 3),
        "risk_indicators": risk_indicators,
        "warnings": warnings,
        "mean_return": round(returns.mean() * 252, 4),
        "mean_return_pct": round(returns.mean() * 252 * 100, 2)
    }

def calculate_beta(data, returns):
    """
    Calculate Beta - measure of asset's sensitivity to market movements
    Uses SPY (S&P 500) as market proxy
    """
    try:
        # Fetch market data (SPY) for the same period
        market_data = yf.download("SPY", period="1y", interval="1d", progress=False)
        market_data.dropna(inplace=True)
        
        if len(market_data) < 10:
            return 1.0  # Default to market beta
        
        # Align dates
        common_dates = data.index.intersection(market_data.index)
        if len(common_dates) < 10:
            return 1.0
        
        asset_returns = data.loc[common_dates, "Close"].pct_change().dropna()
        market_returns = market_data.loc[common_dates, "Close"].pct_change().dropna()
        
        # Align returns
        common_returns = pd.concat([asset_returns, market_returns], axis=1).dropna()
        if len(common_returns) < 10:
            return 1.0
        
        asset_ret = common_returns.iloc[:, 0]
        market_ret = common_returns.iloc[:, 1]
        
        # Calculate covariance and variance
        covariance = np.cov(asset_ret, market_ret)[0][1]
        market_variance = np.var(market_ret)
        
        beta = covariance / market_variance if market_variance > 0 else 1.0
        return beta
    except Exception as e:
        print(f"Error calculating beta: {e}")
        return 1.0  # Default to market beta

def calculate_portfolio_risk(symbols, weights=None):
    """
    Calculate portfolio-level risk metrics
    """
    if weights is None:
        weights = [1.0 / len(symbols)] * len(symbols)  # Equal weights
    
    if len(weights) != len(symbols):
        weights = [1.0 / len(symbols)] * len(symbols)
    
    try:
        # Fetch data for all symbols
        portfolio_data = {}
        for symbol in symbols:
            data = yf.download(symbol, period="1y", interval="1d", progress=False)
            data.dropna(inplace=True)
            portfolio_data[symbol] = data["Close"].pct_change().dropna()
        
        # Align all returns
        returns_df = pd.DataFrame(portfolio_data)
        returns_df = returns_df.dropna()
        
        if len(returns_df) < 10:
            return {"error": "Insufficient data for portfolio analysis"}
        
        # Calculate portfolio returns
        portfolio_returns = (returns_df * weights).sum(axis=1)
        
        # Calculate portfolio metrics
        portfolio_volatility = portfolio_returns.std() * np.sqrt(252)
        portfolio_var = np.percentile(portfolio_returns, 5) * np.sqrt(252)
        
        # Correlation matrix
        correlation_matrix = returns_df.corr().to_dict()
        
        return {
            "portfolio_volatility": round(portfolio_volatility, 4),
            "portfolio_volatility_pct": round(portfolio_volatility * 100, 2),
            "portfolio_var_95": round(abs(portfolio_var), 4),
            "portfolio_var_95_pct": round(abs(portfolio_var) * 100, 2),
            "correlation_matrix": correlation_matrix,
            "diversification_benefit": round(1 - (portfolio_volatility / sum([w * portfolio_data[s].std() * np.sqrt(252) for s, w in zip(symbols, weights)])), 3)
        }
    except Exception as e:
        print(f"Error calculating portfolio risk: {e}")
        return {"error": str(e)}
