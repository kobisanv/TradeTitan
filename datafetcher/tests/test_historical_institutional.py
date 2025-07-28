#!/usr/bin/env python3
"""Quick test of historical institutional data fetching"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from institutional_tracker import InstitutionalTracker
import pandas as pd

def test_historical_data():
    """Test the enhanced historical institutional data fetching."""
    print("Testing enhanced 20-year institutional data fetching...")
    
    tracker = InstitutionalTracker()
    
    # Test with a shorter timeframe first (last 5 years)
    print("Testing 5-year historical data for NVDA...")
    
    # Get 5 years of NVDA institutional data
    historical_holdings = tracker.get_historical_holdings_for_ticker('NVDA', start_year=2020)
    
    if historical_holdings:
        holdings_df = pd.DataFrame(historical_holdings)
        print(f"\n✅ SUCCESS: Found {len(historical_holdings)} historical holdings records!")
        
        # Show sample data
        print("\n📊 Sample Historical Holdings Data:")
        print(holdings_df[['institution_name', 'filing_date', 'ticker', 'shares', 'market_value']].head(10))
        
        # Show date range
        if not holdings_df.empty:
            dates = pd.to_datetime(holdings_df['filing_date'])
            print(f"\n📅 Date Range: {dates.min()} to {dates.max()}")
            print(f"🏛️  Institutions: {holdings_df['institution_name'].unique()}")
            print(f"💰 Total Market Value: ${holdings_df['market_value'].sum():,.0f}")
        
        return True
    else:
        print("❌ No historical holdings data found")
        return False

def test_parsing_methods():
    """Test the different 13F parsing methods."""
    print("\n🔍 Testing 13F parsing methods...")
    
    tracker = InstitutionalTracker()
    
    # Test with Berkshire Hathaway (known to have good 13F data)
    cik = '0001067983'  # Berkshire Hathaway
    
    # Get recent filings
    recent_filings = tracker.get_13f_filings(cik, limit=3)
    
    if recent_filings:
        print(f"Found {len(recent_filings)} recent filings for Berkshire Hathaway")
        
        # Test parsing the most recent filing
        latest_filing = recent_filings[0]
        print(f"Testing parsing of filing from {latest_filing['filing_date']}")
        
        holdings = tracker.parse_13f_holdings(
            cik, 
            latest_filing['accession_number'], 
            target_tickers=['NVDA', 'AMZN', 'AAPL']
        )
        
        if holdings:
            print(f"✅ Successfully parsed {len(holdings)} holdings from 13F filing")
            for holding in holdings:
                print(f"  • {holding['ticker']}: {holding['shares']:,.0f} shares, ${holding['market_value']:,.0f}")
            return True
        else:
            print("❌ No holdings extracted from 13F filing")
            return False
    else:
        print("❌ No recent filings found")
        return False

if __name__ == "__main__":
    print("🚀 Testing Enhanced Institutional Tracker with 20-Year Historical Data")
    print("=" * 70)
    
    # Test 1: Parsing methods
    parsing_success = test_parsing_methods()
    
    print("\n" + "=" * 70)
    
    # Test 2: Historical data (if parsing works)
    if parsing_success:
        historical_success = test_historical_data()
        
        if historical_success:
            print("\n🎉 SUCCESS: Enhanced institutional tracker is working!")
            print("📈 Ready to fetch 20 years of institutional holdings data")
        else:
            print("\n⚠️  Parsing works but historical data needs debugging")
    else:
        print("\n⚠️  Need to debug 13F parsing methods first")
    
    print("\n" + "=" * 70)
    print("Test completed!")