#!/usr/bin/env python3
import os
import sys
import subprocess
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/scheduler.log'),
        logging.StreamHandler()
    ]
)

def run_fetch_script(script_path, stock_name):
    """Run a single fetch script and log the results."""
    try:
        logging.info(f"Starting {stock_name} fetch...")
        
        script_dir = os.path.dirname(script_path)
        original_cwd = os.getcwd()
        
        os.chdir(script_dir)
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, timeout=600)
        
        os.chdir(original_cwd)
        
        if result.returncode == 0:
            logging.info(f"{stock_name} fetch completed successfully")
        else:
            logging.error(f"{stock_name} fetch failed with return code {result.returncode}")
            logging.error(f"Error output: {result.stderr}")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        logging.error(f"{stock_name} fetch timed out after 10 minutes")
        return False
    except Exception as e:
        logging.error(f"Error running {stock_name} fetch: {str(e)}")
        return False

def run_daily_scripts():
    """Run daily stock data fetch scripts."""
    logging.info("=== TradeTitan Daily Data Fetch Started ===")
    
    base_path = "/app"
    
    daily_scripts = [
        (f"{base_path}/NVDA/NVDAfetch.py", "NVDA Data"),
        (f"{base_path}/NVDA/NVDAinsider.py", "NVDA Insider"),
        (f"{base_path}/AMZN/AMZNfetch.py", "AMZN Data"),
        (f"{base_path}/AMZN/AMZNinsider.py", "AMZN Insider"),
        (f"{base_path}/GOOGL/GOOGLfetch.py", "GOOGL Data"),
        (f"{base_path}/GOOGL/GOOGLinsider.py", "GOOGL Insider"),
        (f"{base_path}/MSFT/MSFTfetch.py", "MSFT Data"),
        (f"{base_path}/MSFT/MSFTinsider.py", "MSFT Insider"),
        (f"{base_path}/QQQ/qqqFetch.py", "QQQ Data"),
        (f"{base_path}/SPY/spyFetch.py", "SPY Data"),
        (f"{base_path}/options_flow.py", "Options Flow & Dark Pool"),
        (f"{base_path}/reddit_sentiment.py", "Reddit Sentiment"),
    ]
    
    successful_runs = 0
    total_runs = len(daily_scripts)
    
    for script_path, stock_name in daily_scripts:
        if os.path.exists(script_path):
            success = run_fetch_script(script_path, stock_name)
            if success:
                successful_runs += 1
        else:
            logging.error(f"Script not found: {script_path}")
    
    logging.info(f"=== TradeTitan Daily Data Fetch Complete: {successful_runs}/{total_runs} successful ===")
    return successful_runs, total_runs

def run_weekly_scripts():
    """Run weekly data fetch scripts (Fridays at 8 PM)."""
    logging.info("=== TradeTitan Weekly Data Fetch Started ===")
    
    base_path = "/app"
    
    weekly_scripts = [
        (f"{base_path}/vix_fetcher.py", "VIX & Volatility Data"),
        (f"{base_path}/simplified_institutional.py", "Institutional Holdings"),
        (f"{base_path}/economic_indicators.py", "Economic Indicators"),
    ]
    
    successful_runs = 0
    total_runs = len(weekly_scripts)
    
    for script_path, script_name in weekly_scripts:
        if os.path.exists(script_path):
            success = run_fetch_script(script_path, script_name)
            if success:
                successful_runs += 1
        else:
            logging.error(f"Script not found: {script_path}")
    
    logging.info(f"=== TradeTitan Weekly Data Fetch Complete: {successful_runs}/{total_runs} successful ===")
    return successful_runs, total_runs

def main():
    """Main scheduler function - determines what to run based on day of week."""
    current_time = datetime.now()
    day_of_week = current_time.weekday()  # 0=Monday, 4=Friday, 6=Sunday
    hour = current_time.hour
    
    # Check if it's Friday (4) at 8 PM (20:00) for weekly scripts
    if day_of_week == 4 and hour == 20:
        logging.info("Friday 8 PM - Running weekly data fetch scripts")
        daily_success, daily_total = run_daily_scripts()
        weekly_success, weekly_total = run_weekly_scripts()
        
        total_success = daily_success + weekly_success
        total_scripts = daily_total + weekly_total
        logging.info(f"=== TradeTitan Complete: {total_success}/{total_scripts} successful (Daily: {daily_success}/{daily_total}, Weekly: {weekly_success}/{weekly_total}) ===")
    else:
        # Run daily scripts only
        daily_success, daily_total = run_daily_scripts()
        logging.info(f"=== TradeTitan Daily Complete: {daily_success}/{daily_total} successful ===")

if __name__ == "__main__":
    main()