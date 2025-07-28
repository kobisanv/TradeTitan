#!/usr/bin/env python3
"""Debug 13F filing structure"""

import requests
import time

def debug_13f_structure():
    """Debug the structure of a 13F filing to understand parsing."""
    
    # Berkshire Hathaway CIK and recent filing
    cik = '0001067983'
    accession_number = '0000950123-25-005701'  # Recent filing
    
    base_url = "https://data.sec.gov"
    headers = {
        'User-Agent': 'TradeTitan Institutional Tracker contact@tradetitan.com',
        'Accept-Encoding': 'gzip, deflate',
        'Host': 'data.sec.gov'
    }
    
    formatted_cik = str(cik).zfill(10)
    accession_clean = accession_number.replace('-', '')
    
    print(f"🔍 Debugging 13F filing structure for Berkshire Hathaway")
    print(f"CIK: {formatted_cik}")
    print(f"Accession: {accession_number}")
    print("=" * 60)
    
    # Try different URL patterns that might contain the data
    url_patterns = [
        f"{base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/infotable.xml",
        f"{base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/primary_doc.xml", 
        f"{base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/form13fInfoTable.xml",
        f"{base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/{accession_number}.txt",
        f"{base_url}/Archives/edgar/data/{formatted_cik}/{accession_clean}/FilingSummary.xml"
    ]
    
    for i, url in enumerate(url_patterns):
        print(f"\n🌐 Testing URL {i+1}: {url.split('/')[-1]}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                print(f"Content length: {len(content)} characters")
                
                # Show first 1000 characters
                print(f"\n📄 First 1000 characters:")
                print("-" * 40)
                print(content[:1000])
                print("-" * 40)
                
                # Look for key terms
                key_terms = ['NVIDIA', 'NVDA', 'APPLE', 'AAPL', 'cusip', 'shares', 'nameOfIssuer']
                found_terms = []
                
                for term in key_terms:
                    if term.lower() in content.lower():
                        found_terms.append(term)
                
                if found_terms:
                    print(f"🎯 Found key terms: {found_terms}")
                else:
                    print("❌ No key terms found")
                
                # If this looks promising, save a sample
                if len(content) > 1000 and any(term.lower() in content.lower() for term in ['cusip', 'shares', 'nvidia']):
                    with open(f'/tmp/sample_13f_{i}.txt', 'w') as f:
                        f.write(content)
                    print(f"💾 Saved sample to /tmp/sample_13f_{i}.txt")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
            
            time.sleep(0.5)  # Rate limiting
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🔍 Debug completed! Check any saved samples for structure analysis.")

if __name__ == "__main__":
    debug_13f_structure()