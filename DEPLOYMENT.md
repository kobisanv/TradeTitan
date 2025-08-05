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

## 🐳 OrbStack Deployment

### Prerequisites
- [OrbStack](https://orbstack.dev/) installed on macOS
- Git repository cloned locally

### Environment Setup
The project includes a pre-configured `.env` file with API keys:
```bash
# Navigate to datafetcher directory
cd datafetcher

# Verify .env file exists with your API keys
cat .env
```

Your .env file contains:
- `NEWSAPI_KEY` - For news sentiment analysis
- `FRED_API_KEY` - For economic indicators
- Optional keys for Reddit sentiment and email alerts

### Quick Start with OrbStack
```bash
# Navigate to datafetcher directory
cd datafetcher

# Build the container
docker build -t tradetitan-datafetcher .

# Run with automatic scheduling (recommended)
docker compose up -d

# Or run manually with volume mounts and env file
docker run -d \
  --name tradetitan-datafetcher \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  tradetitan-datafetcher
```

### OrbStack Management
```bash
# View running containers
docker ps

# Start the container
docker start tradetitan-datafetcher

# Stop the container
docker stop tradetitan-s

# Check container health
docker inspect tradetitan-s --format='{{.State.Health.Status}}'

# View scheduler logs
docker logs tradetitan-s

# View log file
tail -f logs/scheduler.log

# With docker-compose
docker-compose logs -f

# Remove the container
docker rm tradetitan-s
```

### Manual Execution
```bash
# Run data collection immediately
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  tradetitan-s now

# Run weekly collection (includes daily + weekly data)
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  tradetitan-datafetcher weekly

# Test all components
docker run --rm \
  --env-file .env \
  tradetitan-datafetcher test
```

### Run Once Immediately
```bash
# Run all daily scripts now
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
  -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
  tradetitan-datafetcher now

# Run weekly scripts now (daily + weekly)
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
  -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
  tradetitan-datafetcher weekly
```

### Data Persistence
OrbStack automatically handles volume mounting for data persistence:
- `./data/` - All fetched market data
- `./logs/` - Application and scheduler logs

### Container Features
- **Automatic Scheduling**: Daily (7 AM) and weekly (Friday 8 PM) data collection
- **Health Checks**: Built-in container health monitoring
- **Restart Policy**: Automatically restarts on failure
- **Clean Environment**: Self-contained Python 3.11 environment
- **Resource Efficient**: Optimized for OrbStack's lightweight virtualization

## 🎯 Next Steps

1. **ML Pipeline**: Build predictive models on collected data
2. **API Integration**: Add more data sources as needed
3. **Monitoring**: Set up alerts and health checks
4. **Scaling**: Consider multi-container setup for larger datasets

---

**🚀 System Status: Production Ready!**
- ✅ All fetchers converted to classes
- ✅ Python 3.11 environment
- ✅ Comprehensive .gitignore
- ✅ Clean repository (no large files)
- ✅ 20-year historical data capability
- ✅ Real-time market intelligence