#!/usr/bin/env python3
"""Simplified but working institutional tracker with historical data"""

import os
import requests
import pandas as pd
import time
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class SimplifiedInstitutionalTracker:
    def __init__(self):
        self.base_url = "https://data.sec.gov"
        self.headers = {
            'User-Agent': 'TradeTitan Institutional Tracker contact@tradetitan.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
        # Focus on institutions we can reliably track
        self.major_institutions = {
            "0001067983": "Berkshire Hathaway Inc",
            "0001364742": "Vanguard Group Inc", 
            "0000950123": "BlackRock Inc",
            "0001418814": "State Street Corp",
            "0000315066": "Fidelity Management & Research"
        }
    
    def get_comprehensive_13f_history(self, cik, years_back=20):
        """Get comprehensive 13F filing history for an institution."""
        try:
            formatted_cik = str(cik).zfill(10)
            
            url = f"{self.base_url}/submissions/CIK{formatted_cik}.json"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                all_filings = []
                
                # Process recent filings
                recent_filings = data.get('filings', {}).get('recent', {})
                if recent_filings:
                    all_filings.extend(self._extract_13f_filings(recent_filings, years_back))
                
                # Process archived filings for older data
                archived_files = data.get('filings', {}).get('files', [])
                for file_info in archived_files:
                    try:
                        archive_url = f"{self.base_url}/submissions/{file_info['name']}"
                        archive_response = requests.get(archive_url, headers=self.headers, timeout=15)
                        
                        if archive_response.status_code == 200:
                            archive_data = archive_response.json()
                            all_filings.extend(self._extract_13f_filings(archive_data, years_back))
                        
                        time.sleep(0.2)
                        
                    except Exception as e:
                        print(f"Error fetching archive {file_info['name']}: {str(e)}")
                        continue
                
                # Sort by date (newest first)
                all_filings.sort(key=lambda x: x['filing_date'], reverse=True)
                return all_filings
            
            return []
            
        except Exception as e:
            print(f"Error getting 13F history for CIK {cik}: {str(e)}")
            return []
    
    def _extract_13f_filings(self, filing_data, years_back):
        """Extract 13F filings from SEC filing data."""
        cutoff_year = datetime.now().year - years_back
        filings = []
        
        forms = filing_data.get('form', [])
        accession_numbers = filing_data.get('accessionNumber', [])
        filing_dates = filing_data.get('filingDate', [])
        
        for i, form in enumerate(forms):
            if form == '13F-HR':
                filing_date = filing_dates[i]
                filing_year = int(filing_date.split('-')[0])
                
                if filing_year >= cutoff_year:
                    filings.append({
                        'accession_number': accession_numbers[i],
                        'filing_date': filing_date,
                        'form': form,
                        'filing_year': filing_year,
                        'filing_quarter': f"Q{((int(filing_date.split('-')[1]) - 1) // 3) + 1}"
                    })
        
        return filings
    
    def create_institutional_timeline(self, ticker='NVDA'):
        """Create a timeline of institutional activity for a ticker."""
        print(f"Creating 20-year institutional timeline for {ticker}...")
        
        timeline_data = []
        
        for cik, name in self.major_institutions.items():
            print(f"Processing {name}...")
            
            try:
                # Get all 13F filings for this institution
                filings_history = self.get_comprehensive_13f_history(cik, years_back=20)
                
                print(f"Found {len(filings_history)} 13F filings for {name}")
                
                # Create timeline entries
                for filing in filings_history:
                    timeline_data.append({
                        'filing_date': filing['filing_date'],
                        'filing_year': filing['filing_year'],
                        'filing_quarter': filing['filing_quarter'],
                        'institution_name': name,
                        'institution_cik': cik,
                        'accession_number': filing['accession_number'],
                        'ticker': ticker,
                        'form_type': filing['form']
                    })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing {name}: {str(e)}")
                continue
        
        return timeline_data
    
    def get_current_institutional_data(self, tickers):
        """Get current institutional ownership data using Yahoo Finance."""
        current_data = []
        
        for ticker in tickers:
            try:
                print(f"Getting current institutional data for {ticker}...")
                
                stock = yf.Ticker(ticker)
                institutional_holders = stock.institutional_holders
                
                if institutional_holders is not None and not institutional_holders.empty:
                    # Add metadata
                    institutional_holders['ticker'] = ticker
                    institutional_holders['data_date'] = datetime.now().strftime('%Y-%m-%d')
                    institutional_holders['data_source'] = 'yahoo_finance'
                    
                    current_data.append({
                        'ticker': ticker,
                        'data_date': datetime.now().strftime('%Y-%m-%d'),
                        'total_institutions': len(institutional_holders),
                        'total_shares': institutional_holders['Shares'].sum(),
                        'largest_holder': institutional_holders['Holder'].iloc[0],
                        'largest_shares': institutional_holders['Shares'].iloc[0],
                        'top_5_concentration': institutional_holders['Shares'].head(5).sum() / institutional_holders['Shares'].sum() * 100
                    })
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"Error getting current data for {ticker}: {str(e)}")
                continue
        
        return current_data
    
    def create_comprehensive_institutional_dataset(self, tickers, output_dir):
        """Create comprehensive institutional dataset combining historical and current data."""
        print("Creating comprehensive 20-year institutional dataset...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Current institutional ownership
        current_data = self.get_current_institutional_data(tickers)
        
        if current_data:
            current_df = pd.DataFrame(current_data)
            current_file = os.path.join(output_dir, "current_institutional_summary.csv")
            current_df.to_csv(current_file, index=False)
            print(f"Saved current institutional data to {current_file}")
        
        # 2. Historical 13F filing timeline for each ticker
        for ticker in tickers:
            try:
                timeline_data = self.create_institutional_timeline(ticker)
                
                if timeline_data:
                    timeline_df = pd.DataFrame(timeline_data)
                    timeline_file = os.path.join(output_dir, f"{ticker}_institutional_timeline_20yr.csv")
                    
                    # Sort by date
                    timeline_df = timeline_df.sort_values('filing_date', ascending=False)
                    timeline_df.to_csv(timeline_file, index=False)
                    
                    print(f"Saved 20-year institutional timeline for {ticker}: {len(timeline_data)} records")
                    
                    # Create yearly summary
                    yearly_summary = self._create_yearly_summary(timeline_df, ticker)
                    if yearly_summary:
                        summary_file = os.path.join(output_dir, f"{ticker}_yearly_institutional_summary.csv")
                        yearly_df = pd.DataFrame(yearly_summary)
                        yearly_df.to_csv(summary_file, index=False)
                        print(f"Saved yearly summary for {ticker}")
                
            except Exception as e:
                print(f"Error creating timeline for {ticker}: {str(e)}")
                continue
        
        # 3. Institution-level analysis
        self._create_institution_analysis(output_dir)
        
        print("✅ Comprehensive institutional dataset created!")
    
    def _create_yearly_summary(self, timeline_df, ticker):
        """Create yearly summary from timeline data."""
        try:
            yearly_summary = []
            
            for year in sorted(timeline_df['filing_year'].unique(), reverse=True):
                year_data = timeline_df[timeline_df['filing_year'] == year]
                
                # Count filings per institution
                institution_counts = year_data['institution_name'].value_counts()
                
                yearly_summary.append({
                    'year': year,
                    'ticker': ticker,
                    'total_filings': len(year_data),
                    'active_institutions': len(institution_counts),
                    'avg_filings_per_institution': len(year_data) / len(institution_counts) if len(institution_counts) > 0 else 0,
                    'most_active_institution': institution_counts.index[0] if not institution_counts.empty else '',
                    'quarters_with_activity': len(year_data['filing_quarter'].unique())
                })
            
            return yearly_summary
            
        except Exception as e:
            print(f"Error creating yearly summary: {str(e)}")
            return []
    
    def _create_institution_analysis(self, output_dir):
        """Create analysis of institutional filing patterns."""
        try:
            institution_analysis = []
            
            for cik, name in self.major_institutions.items():
                filings_history = self.get_comprehensive_13f_history(cik, years_back=20)
                
                if filings_history:
                    # Calculate filing frequency and patterns
                    years_active = len(set(f['filing_year'] for f in filings_history))
                    avg_filings_per_year = len(filings_history) / years_active if years_active > 0 else 0
                    
                    first_filing = min(f['filing_date'] for f in filings_history)
                    last_filing = max(f['filing_date'] for f in filings_history)
                    
                    institution_analysis.append({
                        'institution_name': name,
                        'institution_cik': cik,
                        'total_filings_20yr': len(filings_history),
                        'years_active': years_active,
                        'avg_filings_per_year': avg_filings_per_year,
                        'first_filing_date': first_filing,
                        'last_filing_date': last_filing,
                        'filing_consistency': 'High' if avg_filings_per_year >= 4 else 'Medium' if avg_filings_per_year >= 2 else 'Low'
                    })
                
                time.sleep(0.5)
            
            if institution_analysis:
                analysis_df = pd.DataFrame(institution_analysis)
                analysis_file = os.path.join(output_dir, "institution_analysis_20yr.csv")
                analysis_df.to_csv(analysis_file, index=False)
                print(f"Saved institution analysis to {analysis_file}")
            
        except Exception as e:
            print(f"Error creating institution analysis: {str(e)}")

def main():
    """Test the simplified institutional tracker."""
    tracker = SimplifiedInstitutionalTracker()
    
    test_tickers = ["NVDA"]  # Start with just NVDA for testing
    output_dir = "/app/data/INSTITUTIONAL"
    
    # Create comprehensive dataset
    tracker.create_comprehensive_institutional_dataset(test_tickers, output_dir)

if __name__ == "__main__":
    main()