import time
import yfinance as yf
import pandas as pd

symbol = "SPY"
ticker = yf.Ticker(symbol)

timeframes = {
    "1h": ("2y", "SPY_1h.csv"),    # 2 years of hourly data
    "1d": ("5y", "SPY_1d.csv"),    # 5 years of daily data
    "1wk": ("10y", "SPY_1wk.csv"), # 10 years of weekly data
    "1mo": ("20y", "SPY_1mo.csv"), # 20 years of monthly data
}

def fetch_and_save_data(interval, period, filename, retries=3):
    print(f"Fetching {period} of {interval} data for {symbol}...")
    
    for attempt in range(retries):
        try:
            data = ticker.history(period=period, interval=interval, auto_adjust=False)
            if data.empty:
                raise ValueError("No data received. Possible API limit or incorrect parameters.")
            
            # Moving Averages (EMA 50 & 200)
            data["50_EMA"] = data["Close"].ewm(span=50, adjust=False).mean()
            data["200_EMA"] = data["Close"].ewm(span=200, adjust=False).mean()
            
            # RSI (14-day)
            delta = data["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            data["RSI"] = 100 - (100 / (1 + rs))
            
            # MACD (12,26,9)
            short_ema = data["Close"].ewm(span=12, adjust=False).mean()
            long_ema = data["Close"].ewm(span=26, adjust=False).mean()
            data["MACD"] = short_ema - long_ema
            data["Signal"] = data["MACD"].ewm(span=9, adjust=False).mean()
            
            # OBV (On-Balance Volume)
            data["OBV"] = (data["Volume"] * (data["Close"].diff().apply(lambda x: 1 if x > 0 else -1))).fillna(0).cumsum()
            
            data.to_csv(filename)
            print(f"Data saved to {filename}")
            return  # Exit function on success
        
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(5)  # Wait before retrying
    
    print(f"Failed to fetch {interval} data after {retries} attempts.")

# Fetch data for all timeframes
for interval, (period, filename) in timeframes.items():
    fetch_and_save_data(interval, period, filename)
    time.sleep(10)
