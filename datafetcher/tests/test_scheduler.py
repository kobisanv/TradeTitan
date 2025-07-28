#!/usr/bin/env python3
import os
import sys
from datetime import datetime

# Test the scheduler logic
def test_scheduler_logic():
    current_time = datetime.now()
    day_of_week = current_time.weekday()  # 0=Monday, 4=Friday, 6=Sunday
    hour = current_time.hour
    
    print(f"Current time: {current_time}")
    print(f"Day of week: {day_of_week} (0=Monday, 4=Friday)")
    print(f"Hour: {hour}")
    
    # Check if it's Friday at 8 PM for weekly scripts
    if day_of_week == 4 and hour == 20:
        print("✅ Would run BOTH daily and weekly scripts (Friday 8 PM)")
        print("Daily scripts: NVDA, AMZN, GOOGL, MSFT, QQQ, SPY data + insider")
        print("Weekly scripts: VIX, Institutional, Options, Reddit, Economic")
    else:
        print("✅ Would run DAILY scripts only")
        print("Daily scripts: NVDA, AMZN, GOOGL, MSFT, QQQ, SPY data + insider")
        print("Weekly scripts: Skipped (not Friday 8 PM)")
    
    # Test the file paths
    base_path = "/Users/kobisanvinotharupan/TradeTitan/datafetcher"
    
    weekly_scripts = [
        (f"{base_path}/vix_fetcher.py", "VIX & Volatility Data"),
        (f"{base_path}/institutional_tracker.py", "Institutional Holdings"),
        (f"{base_path}/options_flow.py", "Options Flow & Dark Pool"),
        (f"{base_path}/reddit_sentiment.py", "Reddit Sentiment"),
        (f"{base_path}/economic_indicators.py", "Economic Indicators"),
    ]
    
    print("\n📂 Weekly script file check:")
    for script_path, name in weekly_scripts:
        exists = "✅" if os.path.exists(script_path) else "❌"
        print(f"{exists} {name}: {script_path}")

if __name__ == "__main__":
    test_scheduler_logic()