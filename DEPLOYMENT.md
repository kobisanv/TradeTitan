# 🚀 TradeTitan Deployment Guide

## 📋 Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/kobisanv/TradeTitan.git
cd TradeTitan
```

### 2. Python Environment Setup
```bash
# Create Python 3.11 virtual environment
python3.11 -m venv venv

# Activate environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables (Optional)
Create `.env` file for API keys:
```bash
# Optional - for enhanced news sentiment
NEWSAPI_KEY=your_news_api_key

# Optional - for economic indicators  
FRED_API_KEY=your_fred_api_key
```

### 4. Test Installation
```bash
# Activate environment
source venv/bin/activate

# Test a fetcher
python NVDA/NVDAfetch.py

# Test scheduler
python scheduler.py
```

## 📊 System Architecture

### Data Fetchers (Class-Based)
- **NVDAFetcher** - NVIDIA stock + sentiment analysis
- **AMZNFetcher** - Amazon stock + sentiment analysis  
- **GOOGLFetcher** - Google stock + sentiment analysis
- **MSFTFetcher** - Microsoft stock + sentiment analysis
- **QQQFetcher** - NASDAQ ETF + sentiment analysis
- **SPYFetcher** - S&P 500 ETF + sentiment analysis

### Advanced Analytics
- **VIXFetcher** - 10 volatility indicators (20-year data)
- **OptionsFlowTracker** - Real-time options + dark pool analysis
- **RedditSentimentFetcher** - Social sentiment (VADER + FinBERT)
- **SimplifiedInstitutionalTracker** - 20-year SEC EDGAR data

### Scheduling
- **Daily**: Stock data, insider trades, options flow, Reddit sentiment
- **Weekly**: VIX data, institutional holdings, economic indicators

## 🔧 Production Configuration

### Cron Setup
```bash
# Edit crontab
crontab -e

# Add daily execution (6 PM)
0 18 * * * cd /path/to/TradeTitan && source venv/bin/activate && python scheduler.py

# Add weekly execution (Friday 8 PM) 
0 20 * * 5 cd /path/to/TradeTitan && source venv/bin/activate && python scheduler.py
```

### Log Monitoring
```bash
# Monitor scheduler logs
tail -f scheduler.log

# Check data directories
ls -la */
```

## ⚡ Key Features

### ✅ Working Without API Keys
- Stock data (Yahoo Finance)
- VIX volatility data
- Options flow analysis
- Institutional data (SEC EDGAR)
- Basic sentiment analysis

### 🔑 Enhanced with API Keys
- News sentiment analysis (NewsAPI)
- Economic indicators (FRED)

### 📈 Data Coverage
- **20 years** of historical data where available
- **Real-time** options flow and sentiment
- **304 institutional records** (2005-2025)
- **10 volatility indicators**

## 🐳 Container Deployment

Ready for OrbStack/Docker containerization:
- Clean repository (no large files)
- Self-contained Python 3.11 environment
- All dependencies in requirements.txt
- Production-ready scheduler

## 🎯 Next Steps

1. **OrbStack Container**: Containerize the system
2. **ML Pipeline**: Build predictive models on collected data
3. **API Integration**: Add more data sources as needed
4. **Monitoring**: Set up alerts and health checks

---

**🚀 System Status: Production Ready!**
- ✅ All fetchers converted to classes
- ✅ Python 3.11 environment
- ✅ Comprehensive .gitignore
- ✅ Clean repository (no large files)
- ✅ 20-year historical data capability
- ✅ Real-time market intelligence