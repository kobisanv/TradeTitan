# TradeTitan Data Fetcher - Docker Instructions

## 🚀 Quick Start

### Automatic Scheduled Runs (Recommended)
```bash
# Run container with automatic scheduling
docker-compose up -d

# Or with docker run:
docker run -d \
  --name tradetitan-datafetcher \
  --restart unless-stopped \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
  -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
  tradetitan-datafetcher
```

## 📅 Automatic Schedule
- **Daily**: Monday-Friday at 7:00 AM
  - Stock data (NVDA, AMZN, GOOGL, MSFT, QQQ, SPY)
  - News sentiment analysis
  - Insider trading data
- **Weekly**: Friday at 8:00 PM (includes daily + weekly data)
  - VIX & volatility indicators
  - Institutional holdings
  - Options flow & dark pool data
  - Economic indicators

## 🏃 Manual Runs

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

### Test Components
```bash
# Test all components are working
docker run --rm \
  -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
  -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
  tradetitan-datafetcher test
```

## 🔧 Building the Container

```bash
# Build the image
docker build -t tradetitan-datafetcher .

# Or use docker-compose
docker-compose build
```

## 📊 Monitoring

### View Logs
```bash
# View scheduler logs
docker logs tradetitan-datafetcher

# View log file
tail -f logs/scheduler.log

# With docker-compose
docker-compose logs -f
```

### Check Container Status
```bash
# Check if container is running
docker ps

# Check container health
docker inspect tradetitan-datafetcher --format='{{.State.Health.Status}}'
```

## 🗂️ Data Output

All data is saved to the `./data/` directory:
```
data/
├── NVDA/           # NVIDIA stock data & news
├── AMZN/           # Amazon stock data & news
├── GOOGL/          # Google stock data & news
├── MSFT/           # Microsoft stock data & news
├── QQQ/            # QQQ ETF data
├── SPY/            # SPY ETF data
├── VOLATILITY/     # VIX, UVXY, SVXY data
├── OPTIONS/        # Options flow & dark pool
├── INSTITUTIONAL/  # 13F institutional holdings
└── ECONOMIC/       # GDP, inflation, employment
```

## 🔑 Environment Variables

Required:
- `NEWSAPI_KEY` - For news sentiment analysis
- `FRED_API_KEY` - For economic indicators

Optional:
- `REDDIT_CLIENT_ID` - For Reddit sentiment
- `REDDIT_CLIENT_SECRET` - For Reddit sentiment
- `EMAIL_SENDER` - For insider trading alerts
- `EMAIL_PASSWORD` - For insider trading alerts

## 🛠️ Advanced Usage

### Custom Schedule
To modify the schedule, edit the cron entries in `entrypoint.sh`:
```bash
# Example: Run daily at 6 AM instead of 7 AM
0 6 * * 1-5 cd /app && python scheduler.py >> /app/logs/scheduler.log 2>&1
```

### Individual Scripts
```bash
# Run specific fetcher
docker exec tradetitan-datafetcher python NVDA/NVDAfetch.py

# Run VIX fetcher only
docker exec tradetitan-datafetcher python vix_fetcher.py
```

## 🚨 Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs tradetitan-datafetcher

# Run in test mode
docker run --rm tradetitan-datafetcher test
```

### No Data Being Fetched
1. Check API keys are set correctly
2. Verify internet connection
3. Check logs for rate limiting errors
4. Ensure data directory has write permissions

### Cron Jobs Not Running
```bash
# Check if cron is running inside container
docker exec tradetitan-datafetcher pgrep cron

# Check crontab
docker exec tradetitan-datafetcher crontab -l
```

## 📈 Production Deployment

For production use:
1. Use docker-compose with restart policies
2. Set up log rotation
3. Monitor disk usage for data directory
4. Consider using secrets for API keys
5. Set up monitoring/alerting for failed fetches

```yaml
# Production docker-compose.yml
version: '3.8'
services:
  datafetcher:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - NEWSAPI_KEY_FILE=/run/secrets/newsapi_key
      - FRED_API_KEY_FILE=/run/secrets/fred_api_key
    secrets:
      - newsapi_key
      - fred_api_key
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "3"

secrets:
  newsapi_key:
    file: ./secrets/newsapi_key.txt
  fred_api_key:
    file: ./secrets/fred_api_key.txt
```