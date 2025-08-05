#!/usr/bin/env python3
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

class EconomicIndicatorsFetcher:
    def __init__(self):
        # FRED API key (free from https://fred.stlouisfed.org/docs/api/api_key.html)
        self.fred_api_key = os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred"
        
        # Key economic indicators
        self.indicators = {
            # Interest Rates
            'FEDFUNDS': 'Federal Funds Rate',
            'DGS10': '10-Year Treasury Rate',
            'DGS2': '2-Year Treasury Rate',
            'DGS30': '30-Year Treasury Rate',
            'DGS3MO': '3-Month Treasury Rate',
            
            # Inflation
            'CPIAUCSL': 'Consumer Price Index',
            'CPILFESL': 'Core CPI (Less Food & Energy)',
            'PCEPI': 'PCE Price Index',
            'PCEPILFE': 'Core PCE Price Index',
            
            # Employment
            'UNRATE': 'Unemployment Rate',
            'PAYEMS': 'Total Nonfarm Payrolls',
            'CIVPART': 'Labor Force Participation Rate',
            'EMRATIO': 'Employment-Population Ratio',
            
            # Economic Growth
            'GDP': 'Gross Domestic Product',
            'GDPC1': 'Real GDP',
            'GDPPOT': 'Real Potential GDP',
            
            # Consumer & Business
            'UMCSENT': 'University of Michigan Consumer Sentiment',
            'HOUST': 'Housing Starts',
            'INDPRO': 'Industrial Production Index',
            'RETAILSA': 'Retail Sales',
            
            # Money Supply
            'M1SL': 'M1 Money Stock',
            'M2SL': 'M2 Money Stock',
            'BOGMBASE': 'Monetary Base',
            
            # Market Indicators
            'VIXCLS': 'VIX Close',
            'DEXUSEU': 'US/Euro Exchange Rate',
            'DEXJPUS': 'Japan/US Exchange Rate',
            'GOLDAMGBD228NLBM': 'Gold Price',
            'DCOILWTICO': 'WTI Oil Price'
        }
    
    def get_fred_data(self, series_id, limit=10000):
        """Get data for a specific FRED series."""
        if not self.fred_api_key:
            print("FRED API key not found. Get free key from https://fred.stlouisfed.org/docs/api/api_key.html")
            return None
            
        try:
            url = f"{self.base_url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'limit': limit,
                'sort_order': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                observations = data.get('observations', [])
                
                # Convert to DataFrame
                df = pd.DataFrame(observations)
                
                if not df.empty:
                    # Clean data
                    df['date'] = pd.to_datetime(df['date'])
                    df['value'] = pd.to_numeric(df['value'], errors='coerce')
                    df = df.dropna(subset=['value'])
                    df = df.sort_values('date')
                    
                    # Add metadata
                    df['series_id'] = series_id
                    df['series_name'] = self.indicators.get(series_id, series_id)
                    df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    return df
            else:
                print(f"Error fetching {series_id}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"Error fetching FRED data for {series_id}: {str(e)}")
        
        return None
    
    def calculate_yield_curve(self):
        """Calculate yield curve metrics."""
        try:
            # Get key treasury rates
            rates = {}
            rate_series = ['DGS3MO', 'DGS2', 'DGS10', 'DGS30']
            
            for series in rate_series:
                data = self.get_fred_data(series, limit=30)
                if data is not None and not data.empty:
                    rates[series] = data['value'].iloc[-1]  # Latest value
            
            if len(rates) >= 2:
                yield_curve_metrics = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'treasury_3mo': rates.get('DGS3MO'),
                    'treasury_2yr': rates.get('DGS2'),
                    'treasury_10yr': rates.get('DGS10'),
                    'treasury_30yr': rates.get('DGS30')
                }
                
                # Calculate spreads
                if 'DGS10' in rates and 'DGS2' in rates:
                    yield_curve_metrics['yield_curve_2_10'] = rates['DGS10'] - rates['DGS2']
                    yield_curve_metrics['inverted_2_10'] = rates['DGS10'] < rates['DGS2']
                
                if 'DGS10' in rates and 'DGS3MO' in rates:
                    yield_curve_metrics['yield_curve_3mo_10yr'] = rates['DGS10'] - rates['DGS3MO']
                    yield_curve_metrics['inverted_3mo_10yr'] = rates['DGS10'] < rates['DGS3MO']
                
                return yield_curve_metrics
            
        except Exception as e:
            print(f"Error calculating yield curve: {str(e)}")
        
        return None
    
    def get_inflation_metrics(self):
        """Get comprehensive inflation data."""
        try:
            inflation_data = {}
            inflation_series = ['CPIAUCSL', 'CPILFESL', 'PCEPI', 'PCEPILFE']
            
            for series in inflation_series:
                data = self.get_fred_data(series, limit=24)  # Get 2 years of monthly data
                if data is not None and not data.empty:
                    # Calculate year-over-year change
                    latest_value = data['value'].iloc[-1]
                    year_ago_value = data['value'].iloc[-12] if len(data) >= 12 else data['value'].iloc[0]
                    
                    yoy_change = ((latest_value - year_ago_value) / year_ago_value) * 100
                    
                    inflation_data[f'{series}_current'] = latest_value
                    inflation_data[f'{series}_yoy'] = yoy_change
            
            if inflation_data:
                inflation_metrics = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    **inflation_data
                }
                
                # Add Fed target comparison
                if 'PCEPI_yoy' in inflation_data:
                    inflation_metrics['above_fed_target'] = inflation_data['PCEPI_yoy'] > 2.0
                    inflation_metrics['distance_from_target'] = inflation_data['PCEPI_yoy'] - 2.0
                
                return inflation_metrics
            
        except Exception as e:
            print(f"Error getting inflation metrics: {str(e)}")
        
        return None
    
    def get_employment_indicators(self):
        """Get employment and labor market indicators."""
        try:
            employment_data = {}
            employment_series = ['UNRATE', 'PAYEMS', 'CIVPART', 'EMRATIO']
            
            for series in employment_series:
                data = self.get_fred_data(series, limit=12)  # Get 1 year of data
                if data is not None and not data.empty:
                    latest_value = data['value'].iloc[-1]
                    employment_data[f'{series}_current'] = latest_value
                    
                    # Calculate trend
                    if len(data) >= 3:
                        three_month_avg = data['value'].tail(3).mean()
                        six_month_avg = data['value'].tail(6).mean()
                        employment_data[f'{series}_trend'] = 'Improving' if three_month_avg > six_month_avg else 'Deteriorating'
            
            if employment_data:
                employment_metrics = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    **employment_data
                }
                
                return employment_metrics
            
        except Exception as e:
            print(f"Error getting employment indicators: {str(e)}")
        
        return None
    
    def get_market_sentiment_indicators(self):
        """Get economic indicators that affect market sentiment."""
        try:
            sentiment_data = {}
            sentiment_series = ['UMCSENT', 'VIXCLS', 'GOLDAMGBD228NLBM', 'DCOILWTICO']
            
            for series in sentiment_series:
                data = self.get_fred_data(series, limit=30)
                if data is not None and not data.empty:
                    latest_value = data['value'].iloc[-1]
                    sentiment_data[f'{series}_current'] = latest_value
                    
                    # Calculate 30-day change
                    if len(data) >= 30:
                        month_ago_value = data['value'].iloc[-30]
                        monthly_change = ((latest_value - month_ago_value) / month_ago_value) * 100
                        sentiment_data[f'{series}_30d_change'] = monthly_change
            
            if sentiment_data:
                sentiment_metrics = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    **sentiment_data
                }
                
                return sentiment_metrics
            
        except Exception as e:
            print(f"Error getting market sentiment indicators: {str(e)}")
        
        return None
    
    def create_economic_dashboard(self):
        """Create comprehensive economic dashboard."""
        try:
            dashboard_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Get all indicator categories
            yield_curve = self.calculate_yield_curve()
            inflation = self.get_inflation_metrics()
            employment = self.get_employment_indicators()
            sentiment = self.get_market_sentiment_indicators()
            
            # Combine all data
            if yield_curve:
                dashboard_data.update(yield_curve)
            if inflation:
                dashboard_data.update(inflation)
            if employment:
                dashboard_data.update(employment)
            if sentiment:
                dashboard_data.update(sentiment)
            
            # Add recession indicators
            if yield_curve and 'inverted_2_10' in yield_curve:
                dashboard_data['recession_signal_yield_curve'] = yield_curve['inverted_2_10']
            
            if employment and 'UNRATE_current' in employment:
                # Sahm Rule: recession when 3-month average unemployment rate rises 0.5% above 12-month low
                dashboard_data['unemployment_elevated'] = employment['UNRATE_current'] > 5.0
            
            return dashboard_data
            
        except Exception as e:
            print(f"Error creating economic dashboard: {str(e)}")
            return None
    
    def fetch_and_save_economic_data(self, output_dir):
        """Fetch and save all economic indicators."""
        print("Fetching economic indicators from FRED...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Fetch individual indicators
        for series_id, name in self.indicators.items():
            print(f"Fetching {name} ({series_id})...")
            
            try:
                data = self.get_fred_data(series_id, limit=10000)
                
                if data is not None:
                    filename = os.path.join(output_dir, f"{series_id}_{name.replace(' ', '_').replace('/', '_')}.csv")
                    data.to_csv(filename, index=False)
                    print(f"Saved {name} data")
                
                time.sleep(0.5)  # FRED rate limiting
                
            except Exception as e:
                print(f"Error fetching {name}: {str(e)}")
                continue
        
        # Create and save economic dashboard
        dashboard = self.create_economic_dashboard()
        if dashboard:
            dashboard_df = pd.DataFrame([dashboard])
            dashboard_file = os.path.join(output_dir, "economic_dashboard.csv")
            
            # Append to existing file or create new
            if os.path.exists(dashboard_file):
                existing_df = pd.read_csv(dashboard_file)
                combined_df = pd.concat([existing_df, dashboard_df], ignore_index=True)
                combined_df.to_csv(dashboard_file, index=False)
            else:
                dashboard_df.to_csv(dashboard_file, index=False)
            
            print(f"Saved economic dashboard to {dashboard_file}")
        
        print("Economic indicators fetch completed!")

def main():
    """Test the economic indicators fetcher."""
    fetcher = EconomicIndicatorsFetcher()
    
    # Create economic data directory
    output_dir = "./data/ECONOMIC"
    
    # Fetch and save economic data
    fetcher.fetch_and_save_economic_data(output_dir)

if __name__ == "__main__":
    main()