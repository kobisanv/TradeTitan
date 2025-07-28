#!/bin/bash

# TradeTitan Cron Job Setup Script
# This sets up automated scheduling for your data fetchers

echo "Setting up TradeTitan cron jobs..."

# Get the current directory
SCRIPT_DIR="/Users/kobisanvinotharupan/TradeTitan"
PYTHON_PATH=$(which python3)

# Create cron job entries
CRON_JOBS="# TradeTitan Automated Data Fetching
# Daily at 6 PM (18:00) - Run daily stock data fetchers
0 18 * * * cd $SCRIPT_DIR && $PYTHON_PATH scheduler.py >> scheduler.log 2>&1

# Friday at 8 PM (20:00) - Run both daily and weekly data fetchers  
0 20 * * 5 cd $SCRIPT_DIR && $PYTHON_PATH scheduler.py >> scheduler.log 2>&1"

echo "Cron jobs to be added:"
echo "$CRON_JOBS"
echo ""

# Check if crontab exists
if crontab -l >/dev/null 2>&1; then
    echo "Existing crontab found. Adding TradeTitan jobs..."
    (crontab -l; echo "$CRON_JOBS") | crontab -
else
    echo "No existing crontab. Creating new one with TradeTitan jobs..."
    echo "$CRON_JOBS" | crontab -
fi

echo ""
echo "✅ Cron jobs added successfully!"
echo ""
echo "📅 Schedule:"
echo "   • Daily at 6:00 PM - Stock data, news, insider trades"
echo "   • Friday at 8:00 PM - All daily scripts PLUS weekly scripts:"
echo "     - VIX & Volatility indicators"
echo "     - Institutional holdings tracking"
echo "     - Options flow & dark pool analysis"
echo "     - Reddit sentiment (if API keys available)"
echo "     - Economic indicators (if FRED API key available)"
echo ""
echo "🔍 To view your cron jobs: crontab -l"
echo "🗑️  To remove cron jobs: crontab -e (then delete the TradeTitan lines)"
echo "📋 Logs will be written to: $SCRIPT_DIR/scheduler.log"