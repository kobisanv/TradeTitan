#!/usr/bin/env python3
import os
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

class OptionsFlowTracker:
    def __init__(self):
        # API keys (you'll need to get these)
        self.barchart_api_key = os.getenv('BARCHART_API_KEY')
        self.finnhub_api_key = os.getenv('FINNHUB_API_KEY')
        
    def get_options_chain_yahoo(self, ticker):
        """Get options chain data from Yahoo Finance."""
        try:
            stock = yf.Ticker(ticker)
            
            # Get expiration dates
            expirations = stock.options
            
            if not expirations:
                print(f"No options data available for {ticker}")
                return None
            
            # Get options for the nearest expiration
            nearest_exp = expirations[0]
            options_chain = stock.option_chain(nearest_exp)
            
            calls = options_chain.calls
            puts = options_chain.puts
            
            # Add metadata
            calls['option_type'] = 'call'
            calls['expiration'] = nearest_exp
            calls['ticker'] = ticker
            calls['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            puts['option_type'] = 'put'
            puts['expiration'] = nearest_exp
            puts['ticker'] = ticker
            puts['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Combine calls and puts
            all_options = pd.concat([calls, puts], ignore_index=True)
            
            return all_options
            
        except Exception as e:
            print(f"Error getting options chain for {ticker}: {str(e)}")
            return None
    
    def analyze_unusual_options_activity(self, options_data):
        """Analyze options data for unusual activity."""
        if options_data is None or options_data.empty:
            return None
        
        try:
            # Calculate volume/open interest ratio
            options_data['vol_oi_ratio'] = options_data['volume'] / (options_data['openInterest'] + 1)
            
            # Identify high volume options
            high_volume_threshold = options_data['volume'].quantile(0.9)
            unusual_volume = options_data[options_data['volume'] >= high_volume_threshold]
            
            # Calculate put/call ratio
            calls = options_data[options_data['option_type'] == 'call']
            puts = options_data[options_data['option_type'] == 'put']
            
            total_call_volume = calls['volume'].sum()
            total_put_volume = puts['volume'].sum()
            put_call_ratio = total_put_volume / (total_call_volume + 1)
            
            # Calculate volume-weighted average strike
            total_volume = options_data['volume'].sum()
            if total_volume > 0:
                avg_strike = (options_data['strike'] * options_data['volume']).sum() / total_volume
            else:
                avg_strike = 0
            
            analysis = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ticker': options_data['ticker'].iloc[0] if not options_data.empty else None,
                'total_call_volume': total_call_volume,
                'total_put_volume': total_put_volume,
                'put_call_ratio': put_call_ratio,
                'total_volume': total_volume,
                'unusual_activity_count': len(unusual_volume),
                'volume_weighted_avg_strike': avg_strike,
                'sentiment': 'Bullish' if put_call_ratio < 0.7 else 'Bearish' if put_call_ratio > 1.3 else 'Neutral'
            }
            
            return analysis, unusual_volume
            
        except Exception as e:
            print(f"Error analyzing unusual options activity: {str(e)}")
            return None, None
    
    def get_options_flow_finnhub(self, ticker):
        """Get options flow data from Finnhub (if API key available)."""
        if not self.finnhub_api_key:
            return None
            
        try:
            url = f"https://finnhub.io/api/v1/stock/option-chain"
            params = {
                'symbol': ticker,
                'token': self.finnhub_api_key
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"Finnhub API error for {ticker}: {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching Finnhub options data: {str(e)}")
        
        return None
    
    def calculate_options_indicators(self, ticker):
        """Calculate key options indicators."""
        try:
            stock = yf.Ticker(ticker)
            
            # Get current stock price
            hist = stock.history(period="5d", interval="1d")
            if hist.empty:
                return None
                
            current_price = hist['Close'].iloc[-1]
            
            # Get options chain
            options_data = self.get_options_chain_yahoo(ticker)
            
            if options_data is None:
                return None
            
            # Calculate key indicators
            calls = options_data[options_data['option_type'] == 'call']
            puts = options_data[options_data['option_type'] == 'put']
            
            # Find at-the-money options
            atm_calls = calls.iloc[(calls['strike'] - current_price).abs().argsort()[:5]]
            atm_puts = puts.iloc[(puts['strike'] - current_price).abs().argsort()[:5]]
            
            # Calculate max pain (strike with highest total open interest)
            total_oi_by_strike = options_data.groupby('strike')['openInterest'].sum().reset_index()
            max_pain_strike = total_oi_by_strike.loc[total_oi_by_strike['openInterest'].idxmax(), 'strike']
            
            # Calculate gamma exposure (simplified)
            # This is a basic approximation - proper GEX calculation is more complex
            call_gamma_exposure = (calls['openInterest'] * calls['strike'] * 0.01).sum()  # Simplified
            put_gamma_exposure = (puts['openInterest'] * puts['strike'] * -0.01).sum()   # Simplified
            net_gamma_exposure = call_gamma_exposure + put_gamma_exposure
            
            indicators = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ticker': ticker,
                'current_price': current_price,
                'max_pain_strike': max_pain_strike,
                'distance_to_max_pain': ((current_price - max_pain_strike) / current_price) * 100,
                'net_gamma_exposure': net_gamma_exposure,
                'atm_call_iv': atm_calls['impliedVolatility'].mean() if not atm_calls.empty else None,
                'atm_put_iv': atm_puts['impliedVolatility'].mean() if not atm_puts.empty else None,
                'iv_skew': (atm_put_iv - atm_call_iv) if (atm_put_iv := atm_puts['impliedVolatility'].mean()) and (atm_call_iv := atm_calls['impliedVolatility'].mean()) else None,
                'total_call_oi': calls['openInterest'].sum(),
                'total_put_oi': puts['openInterest'].sum(),
                'put_call_oi_ratio': puts['openInterest'].sum() / (calls['openInterest'].sum() + 1)
            }
            
            return indicators
            
        except Exception as e:
            print(f"Error calculating options indicators for {ticker}: {str(e)}")
            return None
    
    def track_dark_pool_activity(self, ticker):
        """Estimate dark pool activity using volume analysis."""
        try:
            stock = yf.Ticker(ticker)
            
            # Get historical trading data
            hist = stock.history(period="5y", interval="1d")
            
            if hist.empty:
                return None
            
            # Calculate average volume and recent volume
            avg_volume_5y = hist['Volume'].mean()
            recent_volume = hist['Volume'].tail(30).mean()  # Last 30 days average
            
            # Get intraday data for more granular analysis
            intraday = stock.history(period="5d", interval="1h")
            
            if not intraday.empty:
                # Calculate volume profile indicators
                volume_ratio = recent_volume / avg_volume_5y
                
                # Calculate additional volume metrics
                volume_std = hist['Volume'].std()
                volume_percentile = (hist['Volume'].rank(pct=True).iloc[-1]) * 100
                
                # Estimate dark pool percentage (this is speculative)
                # Dark pools typically account for 15-40% of volume
                estimated_dark_pool_pct = min(40, max(15, (volume_ratio - 1) * 10 + 25))
                
                dark_pool_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ticker': ticker,
                    'avg_volume_5y': avg_volume_5y,
                    'recent_volume_30d': recent_volume,
                    'volume_ratio': volume_ratio,
                    'volume_percentile_5y': volume_percentile,
                    'volume_std_5y': volume_std,
                    'estimated_dark_pool_pct': estimated_dark_pool_pct,
                    'volume_anomaly': 'High' if volume_ratio > 1.5 else 'Low' if volume_ratio < 0.7 else 'Normal'
                }
                
                return dark_pool_data
            
        except Exception as e:
            print(f"Error tracking dark pool activity for {ticker}: {str(e)}")
        
        return None
    
    def fetch_and_save_options_data(self, tickers, output_dir):
        """Fetch and save options flow data for given tickers."""
        print("Fetching options flow and dark pool data...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        options_summary = []
        dark_pool_summary = []
        
        for ticker in tickers:
            print(f"Analyzing options flow for {ticker}...")
            
            try:
                # Get options chain and analyze
                options_data = self.get_options_chain_yahoo(ticker)
                
                if options_data is not None:
                    # Save detailed options data
                    options_file = os.path.join(output_dir, f"{ticker}_options_chain.csv")
                    options_data.to_csv(options_file, index=False)
                    
                    # Analyze unusual activity
                    analysis, unusual_activity = self.analyze_unusual_options_activity(options_data)
                    
                    if analysis:
                        options_summary.append(analysis)
                    
                    if unusual_activity is not None and not unusual_activity.empty:
                        unusual_file = os.path.join(output_dir, f"{ticker}_unusual_options.csv")
                        unusual_activity.to_csv(unusual_file, index=False)
                
                # Calculate options indicators
                indicators = self.calculate_options_indicators(ticker)
                if indicators:
                    indicators_file = os.path.join(output_dir, f"{ticker}_options_indicators.csv")
                    indicators_df = pd.DataFrame([indicators])
                    
                    # Append to existing file or create new
                    if os.path.exists(indicators_file):
                        existing_df = pd.read_csv(indicators_file)
                        combined_df = pd.concat([existing_df, indicators_df], ignore_index=True)
                        combined_df.to_csv(indicators_file, index=False)
                    else:
                        indicators_df.to_csv(indicators_file, index=False)
                
                # Track dark pool activity
                dark_pool_data = self.track_dark_pool_activity(ticker)
                if dark_pool_data:
                    dark_pool_summary.append(dark_pool_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing options data for {ticker}: {str(e)}")
                continue
        
        # Save summary data
        if options_summary:
            summary_df = pd.DataFrame(options_summary)
            summary_file = os.path.join(output_dir, "options_flow_summary.csv")
            
            if os.path.exists(summary_file):
                existing_df = pd.read_csv(summary_file)
                combined_df = pd.concat([existing_df, summary_df], ignore_index=True)
                combined_df.to_csv(summary_file, index=False)
            else:
                summary_df.to_csv(summary_file, index=False)
            
            print(f"Saved options flow summary to {summary_file}")
        
        # Save dark pool data
        if dark_pool_summary:
            dark_pool_df = pd.DataFrame(dark_pool_summary)
            dark_pool_file = os.path.join(output_dir, "dark_pool_activity.csv")
            
            if os.path.exists(dark_pool_file):
                existing_df = pd.read_csv(dark_pool_file)
                combined_df = pd.concat([existing_df, dark_pool_df], ignore_index=True)
                combined_df.to_csv(dark_pool_file, index=False)
            else:
                dark_pool_df.to_csv(dark_pool_file, index=False)
            
            print(f"Saved dark pool activity to {dark_pool_file}")
        
        print("Options flow analysis completed!")

def main():
    """Test the options flow tracker."""
    tracker = OptionsFlowTracker()
    
    # Test with your existing tickers
    test_tickers = ["NVDA", "AMZN", "GOOGL", "MSFT"]
    output_dir = "/app/data/OPTIONS"
    
    # Fetch and save options data
    tracker.fetch_and_save_options_data(test_tickers, output_dir)

if __name__ == "__main__":
    main()