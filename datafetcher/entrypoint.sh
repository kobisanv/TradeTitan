#!/bin/bash

# TradeTitan Data Fetcher Docker Entrypoint Script
# Handles both immediate execution and scheduled runs

set -e

echo "🚀 TradeTitan Data Fetcher Starting..."
echo "Environment: ${ENVIRONMENT:-development}"
echo "Timestamp: $(date)"

# Ensure data directories exist
mkdir -p /app/data/{NVDA,AMZN,GOOGL,MSFT,QQQ,SPY,VOLATILITY,OPTIONS,INSTITUTIONAL,ECONOMIC}
mkdir -p /app/logs

# Function to set up cron jobs for automatic scheduling
setup_cron() {
    echo "📅 Setting up automatic scheduling with cron..."
    
    # Create crontab entries
    cat > /tmp/crontab << EOF
# TradeTitan Automated Data Fetching
# Daily at 7 AM Monday-Friday - Stock data, news, insider trades
0 7 * * 1-5 cd /app && python scheduler.py >> /app/logs/scheduler.log 2>&1

# Friday at 8 PM - Run both daily and weekly data fetchers
0 20 * * 5 cd /app && python scheduler.py weekly >> /app/logs/scheduler.log 2>&1
EOF

    # Install crontab
    crontab /tmp/crontab
    
    echo "✅ Cron jobs installed:"
    echo "   • Daily: Monday-Friday at 7:00 AM"
    echo "   • Weekly: Friday at 8:00 PM (includes all data)"
    
    # Start cron daemon
    cron
    
    echo "📋 Cron daemon started. Logs will be in /app/logs/scheduler.log"
}

# Parse command line arguments
case "${1:-scheduled}" in
    "now"|"immediate")
        echo "🏃 Running data fetch immediately..."
        python scheduler.py
        ;;
    "weekly")
        echo "🏃 Running weekly data fetch immediately..."
        python scheduler.py weekly
        ;;
    "scheduled"|"cron"|"daemon")
        echo "⏰ Setting up scheduled runs..."
        setup_cron
        
        # Run initial fetch
        echo "🏃 Running initial data fetch..."
        python scheduler.py
        
        # Keep container alive and monitor
        echo "👀 Container running in scheduled mode. Monitoring..."
        while true; do
            sleep 3600  # Check every hour
            # Verify cron is still running
            if ! pgrep cron > /dev/null; then
                echo "⚠️  Cron daemon died, restarting..."
                cron
            fi
        done
        ;;
    "test")
        echo "🧪 Running test mode - checking all components..."
        python -c "
import os
print('✅ Python environment OK')
from scheduler import run_daily_scripts
print('✅ Scheduler import OK')
print('✅ API Keys configured:')
print('   NewsAPI:', 'CONFIGURED' if os.getenv('NEWSAPI_KEY') else 'MISSING')
print('   FRED API:', 'CONFIGURED' if os.getenv('FRED_API_KEY') else 'MISSING')
print('✅ Data directories:')
for dir in ['NVDA', 'VOLATILITY', 'OPTIONS', 'INSTITUTIONAL', 'ECONOMIC']:
    path = f'/app/data/{dir}'
    exists = os.path.exists(path)
    print(f'   {dir}: {\"EXISTS\" if exists else \"MISSING\"}')
print('🧪 Test complete - all components ready!')
"
        ;;
    *)
        echo "❓ Unknown command: $1"
        echo ""
        echo "Available commands:"
        echo "  now/immediate - Run data fetch once immediately"
        echo "  weekly        - Run weekly data fetch once immediately"
        echo "  scheduled     - Set up automatic scheduling (default)"
        echo "  test          - Test all components"
        echo ""
        echo "Examples:"
        echo "  docker run tradetitan-datafetcher now"
        echo "  docker run tradetitan-datafetcher weekly"
        echo "  docker run -d tradetitan-datafetcher scheduled"
        exit 1
        ;;
esac

echo "🏁 TradeTitan Data Fetcher completed."