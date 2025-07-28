#!/usr/bin/env python3
import os
import requests
import pandas as pd
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import yfinance as yf

load_dotenv()

class InstitutionalTracker:
    def __init__(self):
        # Free APIs for 13F data
        self.sec_api_key = os.getenv('SEC_API_KEY')  # sec-api.io if you have key
        self.base_url = "https://data.sec.gov"
        
        # Headers for SEC requests (required by SEC)
        self.headers = {
            'User-Agent': 'TradeTitan Institutional Tracker contact@tradetitan.com',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'data.sec.gov'
        }
        
        # Target tickers for historical tracking
        self.target_tickers = ['NVDA', 'AMZN', 'GOOGL', 'MSFT', 'AAPL', 'TSLA']
        
        # Ticker to CUSIP mapping (for SEC filings)
        self.ticker_to_cusip = {
            'NVDA': '67066G104',
            'AMZN': '023135106', 
            'GOOGL': '02079K305',
            'MSFT': '594918104',
            'AAPL': '037833100',
            'TSLA': '88160R101'
        }
    
    def get_major_institutions(self):
        """Get list of major institutional holders to track."""
        # Major institutions with their CIK numbers
        major_institutions = {
            "0001067983": "Berkshire Hathaway Inc",
            "0001364742": "Vanguard Group Inc",
            "0000950123": "BlackRock Inc",
            "0001418814": "State Street Corp",
            "0000315066": "Fidelity Management & Research",
            "0001364742": "Vanguard Group Inc",
            "0001159556": "T. Rowe Price Associates Inc",
            "0000820932": "Capital Research Global Investors",
            "0001011006": "Northern Trust Corp",
            "0000929351": "Goldman Sachs Group Inc",
            "0000886982": "Invesco Ltd",
            "0001019687": "Wellington Management Co",
            "0000902165": "Dimensional Fund Advisors",
            "0001166559": "Ark Investment Management LLC"
        }
        return major_institutions
    
    def get_historical_13f_filings(self, cik, start_year=2005, end_year=None):
        """Get ALL historical 13F filings for an institution going back to start_year."""
        if end_year is None:
            end_year = datetime.now().year
            
        try:
            # Format CIK (pad with zeros to 10 digits)
            formatted_cik = str(cik).zfill(10)
            
            url = f"{self.base_url}/submissions/CIK{formatted_cik}.json"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Get all filings from recent and archived data
                all_filings = []
                
                # Process recent filings
                recent_filings = data.get('filings', {}).get('recent', {})
                if recent_filings:
                    all_filings.extend(self._process_filing_data(recent_filings, start_year, end_year))
                
                # Process archived filings (older data)
                archived_files = data.get('filings', {}).get('files', [])
                for file_info in archived_files:
                    try:
                        archive_url = f"{self.base_url}/submissions/{file_info['name']}"
                        archive_response = requests.get(archive_url, headers=self.headers, timeout=15)
                        
                        if archive_response.status_code == 200:
                            archive_data = archive_response.json()
                            all_filings.extend(self._process_filing_data(archive_data, start_year, end_year))
                        
                        time.sleep(0.2)  # Rate limiting for archives
                        
                    except Exception as e:
                        print(f"Error fetching archive {file_info['name']}: {str(e)}")
                        continue
                
                # Sort by filing date (newest first)
                all_filings.sort(key=lambda x: x['filing_date'], reverse=True)
                return all_filings
            
            else:
                print(f"Error fetching historical 13F filings for CIK {cik}: Status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting historical 13F filings for CIK {cik}: {str(e)}")
            return []
    
    def _process_filing_data(self, filing_data, start_year, end_year):
        """Process filing data to extract 13F-HR forms within date range."""
        filings = []
        
        forms = filing_data.get('form', [])
        accession_numbers = filing_data.get('accessionNumber', [])
        filing_dates = filing_data.get('filingDate', [])
        
        for i, form in enumerate(forms):
            if form == '13F-HR':
                filing_date = filing_dates[i]
                filing_year = int(filing_date.split('-')[0])
                
                if start_year <= filing_year <= end_year:
                    filings.append({
                        'accession_number': accession_numbers[i],
                        'filing_date': filing_date,
                        'form': form,
                        'filing_year': filing_year
                    })
        
        return filings
    
    def get_13f_filings(self, cik, limit=20):
        """Get recent 13F filings for a specific institution."""
        try:
            # Format CIK (pad with zeros to 10 digits)
            formatted_cik = str(cik).zfill(10)
            
            url = f"{self.base_url}/submissions/CIK{formatted_cik}.json"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Find 13F-HR filings
                filings = data.get('filings', {}).get('recent', {})
                forms = filings.get('form', [])
                accession_numbers = filings.get('accessionNumber', [])
                filing_dates = filings.get('filingDate', [])
                
                f13_filings = []
                for i, form in enumerate(forms):
                    if form == '13F-HR' and len(f13_filings) < limit:
                        f13_filings.append({
                            'accession_number': accession_numbers[i],
                            'filing_date': filing_dates[i],
                            'form': form
                        })
                
                return f13_filings
            
            else:
                print(f"Error fetching 13F filings for CIK {cik}: Status {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Error getting 13F filings for CIK {cik}: {str(e)}")
            return []
    
    def parse_13f_holdings(self, cik, accession_number, target_tickers=None):
        """Parse 13F holdings from a specific filing with enhanced extraction."""
        holdings = []
        
        try:
            # Format CIK and accession number
            formatted_cik = str(cik).zfill(10)
            accession_clean = accession_number.replace('-', '')
            
            # Method 1: Try XML information table first (most reliable)
            info_table_url = f"{self.base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/infotable.xml"
            
            response = requests.get(info_table_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                holdings = self._parse_xml_info_table(response.text, target_tickers)
                if holdings:
                    return holdings
            
            # Method 2: Try primary document (form 13F)
            primary_doc_url = f"{self.base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/primary_doc.xml"
            
            response = requests.get(primary_doc_url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                holdings = self._parse_xml_info_table(response.text, target_tickers)
                if holdings:
                    return holdings
            
            # Method 3: Parse main filing document
            filing_url = f"{self.base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/{accession_number}.txt"
            filing_response = requests.get(filing_url, headers=self.headers, timeout=15)
            
            if filing_response.status_code == 200:
                holdings = self._extract_holdings_from_text(filing_response.text, target_tickers)
                if holdings:
                    return holdings
            
        except Exception as e:
            print(f"Error parsing 13F holdings for {accession_number}: {str(e)}")
        
        return holdings
    
    def _parse_xml_info_table(self, xml_content, target_tickers=None):
        """Parse XML information table to extract holdings."""
        holdings = []
        
        try:
            # Clean XML content
            xml_content = re.sub(r'&(?!(?:amp|lt|gt|quot|apos);)', '&amp;', xml_content)
            
            # Parse with BeautifulSoup (more forgiving than ElementTree)
            soup = BeautifulSoup(xml_content, 'xml')
            
            # Look for holding entries (various formats)
            holdings_tags = soup.find_all(['infoTable', 'holdings', 'holding', 'ns1:infoTable'])
            
            if not holdings_tags:
                # Try alternative structure
                holdings_tags = soup.find_all(re.compile(r'(holding|position|security)', re.I))
            
            for holding_tag in holdings_tags:
                try:
                    # Extract security name and CUSIP
                    name_elem = holding_tag.find(re.compile(r'(nameOfIssuer|issuer|security)', re.I))
                    cusip_elem = holding_tag.find(re.compile(r'cusip', re.I))
                    shares_elem = holding_tag.find(re.compile(r'(sshPrnamt|shares|amount)', re.I))
                    value_elem = holding_tag.find(re.compile(r'(value|marketValue)', re.I))
                    
                    if name_elem and cusip_elem:
                        security_name = name_elem.get_text(strip=True)
                        cusip = cusip_elem.get_text(strip=True)
                        shares = shares_elem.get_text(strip=True) if shares_elem else '0'
                        value = value_elem.get_text(strip=True) if value_elem else '0'
                        
                        # Convert to numbers
                        try:
                            shares_num = float(re.sub(r'[^\d.-]', '', shares))
                            value_num = float(re.sub(r'[^\d.-]', '', value)) * 1000  # Values typically in thousands
                        except:
                            shares_num = 0
                            value_num = 0
                        
                        # Check if it's a target ticker
                        ticker = self._cusip_to_ticker(cusip)
                        
                        if not target_tickers or ticker in target_tickers or any(t.lower() in security_name.lower() for t in target_tickers):
                            holdings.append({
                                'security_name': security_name,
                                'cusip': cusip,
                                'ticker': ticker,
                                'shares': shares_num,
                                'market_value': value_num
                            })
                
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error parsing XML info table: {str(e)}")
        
        return holdings
    
    def _extract_holdings_from_text(self, filing_text, target_tickers=None):
        """Extract holdings from plain text filing (fallback method)."""
        holdings = []
        
        try:
            lines = filing_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for lines that might contain stock information
                for ticker in (target_tickers or self.target_tickers):
                    ticker_patterns = [
                        rf'\b{ticker}\b',
                        rf'{ticker.lower()}',
                        rf'{ticker.upper()}'
                    ]
                    
                    for pattern in ticker_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Try to extract numbers from the line
                            numbers = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', line)
                            
                            if numbers:
                                holdings.append({
                                    'security_name': line,
                                    'cusip': self.ticker_to_cusip.get(ticker, ''),
                                    'ticker': ticker,
                                    'shares': float(numbers[0].replace(',', '')) if numbers else 0,
                                    'market_value': float(numbers[-1].replace(',', '')) * 1000 if len(numbers) > 1 else 0,
                                    'raw_line': line
                                })
                            break
            
        except Exception as e:
            print(f"Error extracting holdings from text: {str(e)}")
        
        return holdings
    
    def _cusip_to_ticker(self, cusip):
        """Convert CUSIP to ticker symbol."""
        cusip_to_ticker_map = {v: k for k, v in self.ticker_to_cusip.items()}
        return cusip_to_ticker_map.get(cusip, '')
    
    def extract_holdings_from_filing(self, filing_text, target_tickers=None):
        """Extract holdings information from 13F filing text."""
        holdings = []
        
        try:
            # This is a simplified extraction - proper implementation would need robust XML/HTML parsing
            lines = filing_text.split('\n')
            
            for line in lines:
                # Look for ticker symbols in the filing
                if target_tickers:
                    for ticker in target_tickers:
                        if ticker.upper() in line.upper():
                            # Extract relevant information (this is very basic)
                            holdings.append({
                                'ticker': ticker,
                                'line_content': line.strip(),
                                'found': True
                            })
            
        except Exception as e:
            print(f"Error extracting holdings: {str(e)}")
        
        return holdings
    
    def get_institutional_ownership_yahoo(self, ticker):
        """Get institutional ownership data from Yahoo Finance (alternative method)."""
        try:
            import yfinance as yf
            
            stock = yf.Ticker(ticker)
            
            # Get institutional holders
            institutional_holders = stock.institutional_holders
            major_holders = stock.major_holders
            
            if institutional_holders is not None:
                # Add timestamp and ticker
                institutional_holders['timestamp'] = datetime.now().strftime('%Y-%m-%d')
                institutional_holders['ticker'] = ticker
                
                return institutional_holders
            
        except Exception as e:
            print(f"Error getting Yahoo Finance institutional data for {ticker}: {str(e)}")
        
        return None
    
    def track_smart_money_flows(self, ticker, lookback_quarters=20):
        """Track institutional money flows for a specific ticker."""
        try:
            # Get current institutional ownership
            current_ownership = self.get_institutional_ownership_yahoo(ticker)
            
            if current_ownership is not None:
                # Calculate metrics
                total_institutions = len(current_ownership)
                total_shares_held = current_ownership['Shares'].sum() if 'Shares' in current_ownership.columns else 0
                
                # Get top 10 holders
                top_holders = current_ownership.head(10) if len(current_ownership) >= 10 else current_ownership
                
                smart_money_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'ticker': ticker,
                    'total_institutions': total_institutions,
                    'total_shares_held': total_shares_held,
                    'top_10_concentration': (top_holders['Shares'].sum() / total_shares_held * 100) if total_shares_held > 0 else 0,
                    'largest_holder': current_ownership['Holder'].iloc[0] if not current_ownership.empty else None,
                    'largest_holder_shares': current_ownership['Shares'].iloc[0] if not current_ownership.empty else 0,
                    'largest_holder_pct': current_ownership['% Out'].iloc[0] if '% Out' in current_ownership.columns and not current_ownership.empty else 0
                }
                
                return smart_money_data, current_ownership
            
        except Exception as e:
            print(f"Error tracking smart money flows for {ticker}: {str(e)}")
        
        return None, None
    
    def fetch_and_save_institutional_data(self, tickers, output_dir):
        """Fetch and save institutional data for given tickers."""
        print("Fetching institutional ownership data...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        smart_money_summary = []
        
        for ticker in tickers:
            print(f"Fetching institutional data for {ticker}...")
            
            try:
                # Get smart money flow data
                summary_data, detailed_holdings = self.track_smart_money_flows(ticker)
                
                if summary_data:
                    smart_money_summary.append(summary_data)
                    
                    # Save detailed holdings
                    if detailed_holdings is not None and not detailed_holdings.empty:
                        detailed_file = os.path.join(output_dir, f"{ticker}_institutional_holders.csv")
                        detailed_holdings.to_csv(detailed_file, index=False)
                        print(f"Saved institutional holders for {ticker}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error processing {ticker}: {str(e)}")
                continue
        
        # Save summary data
        if smart_money_summary:
            summary_df = pd.DataFrame(smart_money_summary)
            summary_file = os.path.join(output_dir, "institutional_summary.csv")
            
            # Append to existing file or create new
            if os.path.exists(summary_file):
                existing_df = pd.read_csv(summary_file)
                combined_df = pd.concat([existing_df, summary_df], ignore_index=True)
                combined_df.to_csv(summary_file, index=False)
            else:
                summary_df.to_csv(summary_file, index=False)
            
            print(f"Saved institutional summary to {summary_file}")
        
        # Get major institution tracking
        self.track_major_institutions(output_dir, ['NVDA', 'AMZN', 'GOOGL', 'MSFT'])
        
        print("Institutional tracking completed!")
    
    def get_historical_holdings_for_ticker(self, ticker, start_year=2005):
        """Get 20 years of institutional holdings for a specific ticker."""
        print(f"Fetching 20-year institutional history for {ticker}...")
        
        major_institutions = self.get_major_institutions()
        all_historical_holdings = []
        
        for cik, name in list(major_institutions.items())[:3]:  # Start with top 3 to avoid rate limits
            print(f"Processing historical data for {name}...")
            
            try:
                # Get all historical 13F filings
                historical_filings = self.get_historical_13f_filings(cik, start_year=start_year)
                
                print(f"Found {len(historical_filings)} historical filings for {name}")
                
                # Process recent filings first (last 5 years with more detail)
                recent_filings = [f for f in historical_filings if f['filing_year'] >= 2020][:20]
                older_filings = [f for f in historical_filings if f['filing_year'] < 2020][::4]  # Every 4th filing
                
                filings_to_process = recent_filings + older_filings
                
                for i, filing in enumerate(filings_to_process[:50]):  # Limit to 50 filings per institution
                    try:
                        print(f"Processing filing {i+1}/{len(filings_to_process[:50])} for {name} ({filing['filing_date']})")
                        
                        # Parse holdings from this filing
                        holdings = self.parse_13f_holdings(
                            cik, 
                            filing['accession_number'], 
                            target_tickers=[ticker]
                        )
                        
                        for holding in holdings:
                            holding.update({
                                'institution_name': name,
                                'institution_cik': cik,
                                'filing_date': filing['filing_date'],
                                'filing_year': filing['filing_year'],
                                'accession_number': filing['accession_number']
                            })
                            all_historical_holdings.append(holding)
                        
                        time.sleep(0.3)  # Rate limiting
                        
                    except Exception as e:
                        print(f"Error processing filing {filing['accession_number']}: {str(e)}")
                        continue
                
                time.sleep(1)  # Institution-level rate limiting
                
            except Exception as e:
                print(f"Error processing institution {name}: {str(e)}")
                continue
        
        return all_historical_holdings
    
    def track_major_institutions(self, output_dir, target_tickers):
        """Track major institutions and their holdings in target tickers with 20-year history."""
        print("Tracking major institutional movements with 20-year history...")
        
        # Get historical holdings for each target ticker
        for ticker in target_tickers:
            try:
                historical_holdings = self.get_historical_holdings_for_ticker(ticker, start_year=2005)
                
                if historical_holdings:
                    # Save detailed historical holdings
                    holdings_df = pd.DataFrame(historical_holdings)
                    holdings_file = os.path.join(output_dir, f"{ticker}_historical_institutional_holdings.csv")
                    
                    # Sort by filing date
                    holdings_df = holdings_df.sort_values('filing_date', ascending=False)
                    holdings_df.to_csv(holdings_file, index=False)
                    
                    print(f"Saved {len(historical_holdings)} historical holdings for {ticker} to {holdings_file}")
                    
                    # Create summary data
                    summary_data = self._create_historical_summary(holdings_df, ticker)
                    if summary_data:
                        summary_file = os.path.join(output_dir, f"{ticker}_institutional_summary_20yr.csv")
                        summary_df = pd.DataFrame(summary_data)
                        summary_df.to_csv(summary_file, index=False)
                        print(f"Saved institutional summary for {ticker}")
                
            except Exception as e:
                print(f"Error processing historical data for {ticker}: {str(e)}")
                continue
        
        # Also keep the existing tracking format for compatibility
        major_institutions = self.get_major_institutions()
        institution_data = []
        
        for cik, name in list(major_institutions.items())[:5]:
            try:
                filings = self.get_13f_filings(cik, limit=10)
                
                for filing in filings:
                    institution_record = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d'),
                        'institution_name': name,
                        'cik': cik,
                        'filing_date': filing['filing_date'],
                        'accession_number': filing['accession_number']
                    }
                    institution_data.append(institution_record)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"Error tracking {name}: {str(e)}")
                continue
        
        # Save institution tracking data
        if institution_data:
            institution_df = pd.DataFrame(institution_data)
            institution_file = os.path.join(output_dir, "major_institutions_tracking.csv")
            
            if os.path.exists(institution_file):
                existing_df = pd.read_csv(institution_file)
                combined_df = pd.concat([existing_df, institution_df], ignore_index=True)
                combined_df.to_csv(institution_file, index=False)
            else:
                institution_df.to_csv(institution_file, index=False)
            
            print(f"Saved major institutions tracking to {institution_file}")
    
    def _create_historical_summary(self, holdings_df, ticker):
        """Create summary statistics from historical holdings data."""
        try:
            if holdings_df.empty:
                return []
            
            # Group by year and institution
            holdings_df['year'] = pd.to_datetime(holdings_df['filing_date']).dt.year
            
            yearly_summary = []
            
            for year in sorted(holdings_df['year'].unique(), reverse=True):
                year_data = holdings_df[holdings_df['year'] == year]
                
                # Get latest filing for each institution in this year
                latest_per_institution = year_data.groupby('institution_name').first().reset_index()
                
                if not latest_per_institution.empty:
                    total_shares = latest_per_institution['shares'].sum()
                    total_value = latest_per_institution['market_value'].sum()
                    num_institutions = len(latest_per_institution)
                    
                    yearly_summary.append({
                        'year': year,
                        'ticker': ticker,
                        'total_institutional_shares': total_shares,
                        'total_market_value': total_value,
                        'num_major_institutions': num_institutions,
                        'avg_holding_size': total_shares / num_institutions if num_institutions > 0 else 0,
                        'largest_holder': latest_per_institution.loc[latest_per_institution['shares'].idxmax(), 'institution_name'] if not latest_per_institution.empty else '',
                        'largest_holding_shares': latest_per_institution['shares'].max(),
                        'concentration_top3': latest_per_institution.nlargest(3, 'shares')['shares'].sum() / total_shares * 100 if total_shares > 0 else 0
                    })
            
            return yearly_summary
            
        except Exception as e:
            print(f"Error creating historical summary: {str(e)}")
            return []

def main():
    """Test the institutional tracker."""
    tracker = InstitutionalTracker()
    
    # Test tickers (matching your existing setup)
    test_tickers = ["NVDA", "AMZN", "GOOGL", "MSFT"]
    output_dir = "/app/data/INSTITUTIONAL"
    
    # Fetch and save institutional data
    tracker.fetch_and_save_institutional_data(test_tickers, output_dir)

if __name__ == "__main__":
    main()