#!/usr/bin/env python3
import os
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class VIXFetcher:
    def __init__(self):
        # VIX and volatility-related tickers
        self.volatility_tickers = {
            "^VIX": "VIX",           # CBOE Volatility Index
            "^VIX9D": "VIX9D",       # CBOE 9-Day Volatility Index
            "^VIX3M": "VIX3M",       # CBOE 3-Month Volatility Index
            "^VIX6M": "VIX6M",       # CBOE 6-Month Volatility Index
            "^VVIX": "VVIX",         # Volatility of VIX
            "^SKEW": "SKEW",         # CBOE SKEW Index
            "VXX": "VXX",            # iPath Series B S&P 500 VIX Short-Term Futures ETN
            "UVXY": "UVXY",          # ProShares Ultra VIX Short-Term Futures ETF
            "VIXY": "VIXY",          # ProShares VIX Short-Term Futures ETF
            "SVXY": "SVXY"           # ProShares Short VIX Short-Term Futures ETF
        }
    
    def fetch_volatility_data(self, symbol, period="20y", interval="1d"):
        """Fetch volatility data for a specific symbol."""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval, auto_adjust=False)
            
            if data.empty:
                print(f"No data received for {symbol}")
                return None
            
            # Add additional volatility metrics
            data['Symbol'] = symbol
            data['Date'] = data.index
            
            # Calculate rolling volatility if it's not VIX itself
            if symbol not in ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M"]:
                # 30-day rolling volatility
                data['30d_volatility'] = data['Close'].pct_change().rolling(window=30).std() * (252**0.5) * 100
                # 10-day rolling volatility
                data['10d_volatility'] = data['Close'].pct_change().rolling(window=10).std() * (252**0.5) * 100
            
            # VIX-specific calculations
            if symbol == "^VIX":
                data['VIX_percentile_30d'] = data['Close'].rolling(window=30).rank(pct=True) * 100
                data['VIX_percentile_90d'] = data['Close'].rolling(window=90).rank(pct=True) * 100
                data['VIX_MA_10'] = data['Close'].rolling(window=10).mean()
                data['VIX_MA_20'] = data['Close'].rolling(window=20).mean()
                
                # VIX fear levels
                data['Fear_Level'] = pd.cut(data['Close'], 
                                          bins=[0, 12, 20, 30, float('inf')], 
                                          labels=['Low', 'Normal', 'High', 'Extreme'])
            
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_vix_term_structure(self):
        """Calculate VIX term structure (contango/backwardation)."""
        try:
            vix_data = {}
            term_structure_symbols = ["^VIX", "^VIX9D", "^VIX3M", "^VIX6M"]
            
            for symbol in term_structure_symbols:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d", interval="1d")
                if not data.empty:
                    vix_data[symbol] = data['Close'].iloc[-1]  # Latest close
            
            if len(vix_data) >= 2:
                # Calculate term structure relationships
                term_structure = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'VIX_current': vix_data.get('^VIX', None),
                    'VIX9D': vix_data.get('^VIX9D', None),
                    'VIX3M': vix_data.get('^VIX3M', None),
                    'VIX6M': vix_data.get('^VIX6M', None)
                }
                
                # Calculate contango/backwardation
                if '^VIX' in vix_data and '^VIX3M' in vix_data:
                    term_structure['VIX_VIX3M_ratio'] = vix_data['^VIX'] / vix_data['^VIX3M']
                    term_structure['term_structure'] = 'Backwardation' if vix_data['^VIX'] > vix_data['^VIX3M'] else 'Contango'
                
                return term_structure
            
        except Exception as e:
            print(f"Error calculating VIX term structure: {str(e)}")
        
        return None
    
    def get_market_fear_indicators(self):
        """Get comprehensive market fear indicators."""
        try:
            fear_data = []
            
            # Get historical VIX data
            vix_ticker = yf.Ticker("^VIX")
            vix_data = vix_ticker.history(period="20y", interval="1d")
            
            if not vix_data.empty:
                current_vix = vix_data['Close'].iloc[-1]
                vix_30d_avg = vix_data['Close'].tail(30).mean()
                vix_percentile = (vix_data['Close'].rank(pct=True).iloc[-1]) * 100
                
                # Get SPY for comparison
                spy_ticker = yf.Ticker("SPY")
                spy_data = spy_ticker.history(period="20y", interval="1d")
                spy_volatility = spy_data['Close'].pct_change().std() * (252**0.5) * 100
                
                fear_indicators = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'VIX_current': current_vix,
                    'VIX_30d_avg': vix_30d_avg,
                    'VIX_90d_percentile': vix_percentile,
                    'SPY_30d_realized_vol': spy_volatility,
                    'VIX_SPY_vol_ratio': current_vix / spy_volatility if spy_volatility > 0 else None,
                    'fear_level': 'Extreme' if current_vix > 30 else 'High' if current_vix > 20 else 'Normal' if current_vix > 12 else 'Low'
                }
                
                fear_data.append(fear_indicators)
            
            return fear_data
            
        except Exception as e:
            print(f"Error getting market fear indicators: {str(e)}")
            return []
    
    def fetch_and_save_volatility_data(self, output_dir, period="20y"):
        """Fetch and save all volatility data."""
        print("Fetching volatility and fear indicators...")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch individual volatility instruments
        for symbol, name in self.volatility_tickers.items():
            print(f"Fetching {name} ({symbol})...")
            data = self.fetch_volatility_data(symbol, period=period)
            
            if data is not None:
                filename = os.path.join(output_dir, f"{name}_data.csv")
                data.to_csv(filename, index=True)
                print(f"Saved {name} data to {filename}")
        
        # Calculate and save VIX term structure
        term_structure = self.calculate_vix_term_structure()
        if term_structure:
            ts_df = pd.DataFrame([term_structure])
            ts_file = os.path.join(output_dir, "VIX_term_structure.csv")
            
            # Append to existing file or create new
            if os.path.exists(ts_file):
                existing_df = pd.read_csv(ts_file)
                combined_df = pd.concat([existing_df, ts_df], ignore_index=True)
                combined_df.to_csv(ts_file, index=False)
            else:
                ts_df.to_csv(ts_file, index=False)
            
            print(f"Saved VIX term structure to {ts_file}")
        
        # Get and save market fear indicators
        fear_data = self.get_market_fear_indicators()
        if fear_data:
            fear_df = pd.DataFrame(fear_data)
            fear_file = os.path.join(output_dir, "market_fear_indicators.csv")
            
            # Append to existing file or create new
            if os.path.exists(fear_file):
                existing_df = pd.read_csv(fear_file)
                combined_df = pd.concat([existing_df, fear_df], ignore_index=True)
                combined_df.to_csv(fear_file, index=False)
            else:
                fear_df.to_csv(fear_file, index=False)
            
            print(f"Saved market fear indicators to {fear_file}")
        
        print("Volatility data fetch completed!")

def main():
    """Test the VIX fetcher."""
    fetcher = VIXFetcher()
    
    # Create volatility data directory
    output_dir = "./data/VOLATILITY"
    
    # Fetch and save all volatility data
    fetcher.fetch_and_save_volatility_data(output_dir, period="20y")

if __name__ == "__main__":
    main()