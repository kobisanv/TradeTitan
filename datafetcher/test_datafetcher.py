#!/usr/bin/env python3
"""
TradeTitan Data Fetcher - Comprehensive Test Suite
Tests all components of the data fetching system
"""

import os
import sys
import time
import json
import subprocess
import pandas as pd
from datetime import datetime
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class DataFetcherTester:
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.base_dir = Path(__file__).parent
        
    def print_header(self, text):
        """Print formatted header"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.WHITE}{text}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        
    def print_test(self, test_name):
        """Print test name"""
        print(f"\n{Colors.PURPLE}🧪 Testing: {test_name}{Colors.END}")
        
    def print_success(self, message):
        """Print success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
        
    def print_warning(self, message):
        """Print warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
        
    def print_error(self, message):
        """Print error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
        
    def record_test(self, test_name, passed, message="", duration=0):
        """Record test result"""
        self.test_results.append({
            'test': test_name,
            'passed': passed,
            'message': message,
            'duration': duration
        })
        
    def test_environment(self):
        """Test Python environment and dependencies"""
        self.print_test("Python Environment & Dependencies")
        
        # Test Python version
        python_version = sys.version_info
        if python_version >= (3, 8):
            self.print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
            self.record_test("Python Version", True)
        else:
            self.print_error(f"Python version too old: {python_version}")
            self.record_test("Python Version", False, "Requires Python 3.8+")
            
        # Test required packages (pip name -> import name mapping)
        required_packages = {
            'yfinance': 'yfinance',
            'pandas': 'pandas', 
            'requests': 'requests',
            'python-dotenv': 'dotenv',
            'newsapi-python': 'newsapi',
            'vaderSentiment': 'vaderSentiment',
            'transformers': 'transformers',
            'beautifulsoup4': 'bs4',
            'lxml': 'lxml'
        }
        
        missing_packages = []
        for pip_name, import_name in required_packages.items():
            try:
                __import__(import_name)
                self.print_success(f"Package available: {pip_name}")
            except ImportError:
                missing_packages.append(pip_name)
                self.print_error(f"Missing package: {pip_name}")
                
        if not missing_packages:
            self.record_test("Required Packages", True)
        else:
            self.record_test("Required Packages", False, f"Missing: {', '.join(missing_packages)}")
            
    def test_api_keys(self):
        """Test API key configuration"""
        self.print_test("API Key Configuration")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'NEWSAPI_KEY': os.getenv('NEWSAPI_KEY'),
            'FRED_API_KEY': os.getenv('FRED_API_KEY'),
            'REDDIT_CLIENT_ID': os.getenv('REDDIT_CLIENT_ID'),
            'REDDIT_CLIENT_SECRET': os.getenv('REDDIT_CLIENT_SECRET')
        }
        
        for key, value in api_keys.items():
            if value:
                masked_key = f"{value[:8]}..." if len(value) > 8 else "***"
                self.print_success(f"{key}: {masked_key}")
                self.record_test(f"API Key - {key}", True)
            else:
                if key in ['NEWSAPI_KEY', 'FRED_API_KEY']:
                    self.print_warning(f"{key}: Not configured (required for full functionality)")
                    self.record_test(f"API Key - {key}", False, "Not configured")
                else:
                    self.print_warning(f"{key}: Not configured (optional)")
                    self.record_test(f"API Key - {key}", True, "Optional - not configured")
                    
    def test_directory_structure(self):
        """Test data directory structure"""
        self.print_test("Directory Structure")
        
        required_dirs = [
            'data/NVDA', 'data/AMZN', 'data/GOOGL', 'data/MSFT',
            'data/QQQ', 'data/SPY', 'data/VOLATILITY', 'data/OPTIONS',
            'data/INSTITUTIONAL', 'data/ECONOMIC', 'logs'
        ]
        
        for dir_path in required_dirs:
            full_path = self.base_dir / dir_path
            if full_path.exists():
                self.print_success(f"Directory exists: {dir_path}")
                self.record_test(f"Directory - {dir_path}", True)
            else:
                self.print_warning(f"Creating directory: {dir_path}")
                full_path.mkdir(parents=True, exist_ok=True)
                self.record_test(f"Directory - {dir_path}", True, "Created")
                
    def test_individual_fetchers(self):
        """Test individual data fetchers"""
        self.print_test("Individual Data Fetchers")
        
        # Test basic stock fetchers
        stock_fetchers = [
            ('NVDA/NVDAfetch.py', 'NVDA Stock Fetcher'),
            ('AMZN/AMZNfetch.py', 'AMZN Stock Fetcher'),
            ('GOOGL/GOOGLfetch.py', 'GOOGL Stock Fetcher'),
            ('MSFT/MSFTfetch.py', 'MSFT Stock Fetcher'),
            ('QQQ/qqqFetch.py', 'QQQ ETF Fetcher'),
            ('SPY/spyFetch.py', 'SPY ETF Fetcher')
        ]
        
        for script_path, name in stock_fetchers:
            full_path = self.base_dir / script_path
            if full_path.exists():
                self.print_success(f"Script exists: {name}")
                # Test import ability
                try:
                    script_dir = full_path.parent
                    script_name = full_path.stem
                    sys.path.insert(0, str(script_dir))
                    __import__(script_name)
                    sys.path.pop(0)
                    self.print_success(f"Import successful: {name}")
                    self.record_test(f"Fetcher - {name}", True)
                except Exception as e:
                    self.print_error(f"Import failed: {name} - {str(e)}")
                    self.record_test(f"Fetcher - {name}", False, str(e))
            else:
                self.print_error(f"Script missing: {name}")
                self.record_test(f"Fetcher - {name}", False, "Script not found")
                
    def test_specialized_fetchers(self):
        """Test specialized data fetchers"""
        self.print_test("Specialized Data Fetchers")
        
        specialized_fetchers = [
            ('vix_fetcher.py', 'VIX Volatility Fetcher'),
            ('economic_indicators.py', 'Economic Indicators Fetcher'),
            ('options_flow.py', 'Options Flow Fetcher'),
            ('institutional_tracker.py', 'Institutional Tracker'),
            ('reddit_sentiment.py', 'Reddit Sentiment Fetcher')
        ]
        
        for script_name, display_name in specialized_fetchers:
            script_path = self.base_dir / script_name
            if script_path.exists():
                self.print_success(f"Script exists: {display_name}")
                try:
                    # Test import
                    spec = __import__(script_name[:-3])  # Remove .py extension
                    self.print_success(f"Import successful: {display_name}")
                    self.record_test(f"Specialized - {display_name}", True)
                except Exception as e:
                    self.print_error(f"Import failed: {display_name} - {str(e)}")
                    self.record_test(f"Specialized - {display_name}", False, str(e))
            else:
                self.print_error(f"Script missing: {display_name}")
                self.record_test(f"Specialized - {display_name}", False, "Script not found")
                
    def test_scheduler(self):
        """Test scheduler functionality"""
        self.print_test("Scheduler System")
        
        scheduler_path = self.base_dir / 'scheduler.py'
        if scheduler_path.exists():
            self.print_success("Scheduler script exists")
            try:
                import scheduler
                self.print_success("Scheduler import successful")
                
                # Test scheduler functions
                if hasattr(scheduler, 'run_daily_scripts'):
                    self.print_success("Daily scripts function available")
                if hasattr(scheduler, 'run_weekly_scripts'):
                    self.print_success("Weekly scripts function available")
                if hasattr(scheduler, 'main'):
                    self.print_success("Main scheduler function available")
                    
                self.record_test("Scheduler", True)
            except Exception as e:
                self.print_error(f"Scheduler import failed: {str(e)}")
                self.record_test("Scheduler", False, str(e))
        else:
            self.print_error("Scheduler script missing")
            self.record_test("Scheduler", False, "Script not found")
            
    def test_docker_setup(self):
        """Test Docker configuration"""
        self.print_test("Docker Configuration")
        
        docker_files = [
            ('dockerfile', 'Dockerfile'),
            ('docker-compose.yml', 'Docker Compose'),
            ('entrypoint.sh', 'Entrypoint Script'),
            ('.env', 'Environment Variables'),
            ('requirements.txt', 'Requirements')
        ]
        
        for filename, display_name in docker_files:
            file_path = self.base_dir / filename
            if file_path.exists():
                self.print_success(f"{display_name} exists")
                
                # Additional checks for specific files
                if filename == 'entrypoint.sh':
                    if os.access(file_path, os.X_OK):
                        self.print_success("Entrypoint script is executable")
                    else:
                        self.print_warning("Entrypoint script not executable")
                        
                self.record_test(f"Docker - {display_name}", True)
            else:
                self.print_error(f"{display_name} missing")
                self.record_test(f"Docker - {display_name}", False, "File not found")
                
    def test_data_connectivity(self):
        """Test external data source connectivity"""
        self.print_test("Data Source Connectivity")
        
        # Test yfinance connection
        try:
            import yfinance as yf
            ticker = yf.Ticker("AAPL")
            data = ticker.history(period="1d", interval="1d")
            if not data.empty:
                self.print_success("Yahoo Finance API: Connected")
                self.record_test("Yahoo Finance API", True)
            else:
                self.print_error("Yahoo Finance API: No data received")
                self.record_test("Yahoo Finance API", False, "No data")
        except Exception as e:
            self.print_error(f"Yahoo Finance API: {str(e)}")
            self.record_test("Yahoo Finance API", False, str(e))
            
        # Test NewsAPI if key available
        if os.getenv('NEWSAPI_KEY'):
            try:
                from newsapi import NewsApiClient
                newsapi = NewsApiClient(api_key=os.getenv('NEWSAPI_KEY'))
                articles = newsapi.get_everything(q='test', page_size=1)
                if articles and 'articles' in articles:
                    self.print_success("NewsAPI: Connected")
                    self.record_test("NewsAPI", True)
                else:
                    self.print_error("NewsAPI: Invalid response")
                    self.record_test("NewsAPI", False, "Invalid response")
            except Exception as e:
                self.print_error(f"NewsAPI: {str(e)}")
                self.record_test("NewsAPI", False, str(e))
        else:
            self.print_warning("NewsAPI: Not configured")
            self.record_test("NewsAPI", True, "Not configured")
            
    def test_quick_data_fetch(self):
        """Perform a quick data fetch test"""
        self.print_test("Quick Data Fetch Test")
        
        try:
            import yfinance as yf
            
            # Quick test fetch
            print("Fetching NVDA 1-day data...")
            ticker = yf.Ticker("NVDA")
            data = ticker.history(period="5d", interval="1d")
            
            if not data.empty:
                self.print_success(f"Successfully fetched {len(data)} days of NVDA data")
                
                # Save test data
                test_file = self.base_dir / 'data' / 'test_nvda_data.csv'
                data.to_csv(test_file)
                self.print_success(f"Test data saved to {test_file}")
                
                # Verify file
                if test_file.exists() and test_file.stat().st_size > 0:
                    self.print_success("Test data file verified")
                    self.record_test("Quick Data Fetch", True)
                else:
                    self.print_error("Test data file verification failed")
                    self.record_test("Quick Data Fetch", False, "File verification failed")
            else:
                self.print_error("No data received in quick fetch test")
                self.record_test("Quick Data Fetch", False, "No data received")
                
        except Exception as e:
            self.print_error(f"Quick fetch test failed: {str(e)}")
            self.record_test("Quick Data Fetch", False, str(e))
            
    def test_file_permissions(self):
        """Test file and directory permissions"""
        self.print_test("File Permissions")
        
        # Test data directory write permissions
        test_dirs = ['data', 'logs']
        for dir_name in test_dirs:
            dir_path = self.base_dir / dir_name
            try:
                test_file = dir_path / 'permission_test.tmp'
                test_file.write_text('test')
                test_file.unlink()
                self.print_success(f"Write permission OK: {dir_name}")
                self.record_test(f"Permissions - {dir_name}", True)
            except Exception as e:
                self.print_error(f"Write permission failed: {dir_name} - {str(e)}")
                self.record_test(f"Permissions - {dir_name}", False, str(e))
                
    def generate_report(self):
        """Generate test report"""
        self.print_header("TEST REPORT")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test['passed'])
        failed_tests = total_tests - passed_tests
        
        # Summary
        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"Total Tests: {total_tests}")
        print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.END}")
        print(f"{Colors.RED}Failed: {failed_tests}{Colors.END}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        # Failed tests details
        if failed_tests > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}Failed Tests:{Colors.END}")
            for test in self.test_results:
                if not test['passed']:
                    print(f"{Colors.RED}❌ {test['test']}: {test['message']}{Colors.END}")
                    
        # Recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        
        has_newsapi = any(test['test'] == 'API Key - NEWSAPI_KEY' and test['passed'] for test in self.test_results)
        has_fred = any(test['test'] == 'API Key - FRED_API_KEY' and test['passed'] for test in self.test_results)
        
        if not has_newsapi:
            print("• Configure NewsAPI key for news sentiment analysis")
        if not has_fred:
            print("• Configure FRED API key for economic indicators")
            
        if failed_tests == 0:
            print(f"{Colors.GREEN}🎉 All tests passed! Your data fetcher is ready to use.{Colors.END}")
        elif failed_tests < 3:
            print(f"{Colors.YELLOW}⚠️  Minor issues detected. System should work with reduced functionality.{Colors.END}")
        else:
            print(f"{Colors.RED}🚨 Multiple issues detected. Please fix before using.{Colors.END}")
            
        # Runtime
        duration = datetime.now() - self.start_time
        print(f"\nTest completed in {duration.total_seconds():.2f} seconds")
        
        # Save report
        report_file = self.base_dir / 'test_report.json'
        report_data = {
            'timestamp': self.start_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': passed_tests/total_tests*100,
            'test_details': self.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"\n📊 Detailed report saved to: {report_file}")
        
    def run_all_tests(self):
        """Run all tests"""
        self.print_header("TradeTitan Data Fetcher - Test Suite")
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_environment()
        self.test_api_keys()
        self.test_directory_structure()
        self.test_individual_fetchers()
        self.test_specialized_fetchers()
        self.test_scheduler()
        self.test_docker_setup()
        self.test_file_permissions()
        self.test_data_connectivity()
        self.test_quick_data_fetch()
        
        # Generate report
        self.generate_report()

def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("TradeTitan Data Fetcher Test Suite")
        print("Usage: python test_datafetcher.py [options]")
        print("\nOptions:")
        print("  --help     Show this help message")
        print("  --quick    Run only essential tests")
        print("  --verbose  Show detailed output")
        return
        
    # Initialize tester
    tester = DataFetcherTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Test suite failed: {str(e)}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()