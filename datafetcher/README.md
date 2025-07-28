# TradeTitan DataFetcher

All data fetching functionality for TradeTitan has been organized into this single folder.

## Structure
```
datafetcher/
├── AMZN/          # Amazon stock data and scripts
├── GOOGL/         # Google stock data and scripts  
├── MSFT/          # Microsoft stock data and scripts
├── NVDA/          # NVIDIA stock data and scripts
├── QQQ/           # QQQ ETF data and scripts
├── SPY/           # SPY ETF data and scripts
├── data/          # Additional data storage
├── logs/          # Application logs
├── tests/         # Test files
├── *.py           # Core fetcher scripts
├── requirements.txt
├── dockerfile
├── docker-compose.yml
└── setup_cron.sh  # Cron job setup
```

## Usage

### Local Development
```bash
cd datafetcher
pip install -r requirements.txt
python scheduler.py
```

### Docker with OrbStack
```bash
cd datafetcher

# Build the image
docker build -t tradetitan-datafetcher .

# Run with docker-compose
docker-compose up --build

# Run in background
docker-compose up -d

# Stop containers
docker-compose down

# View logs
docker-compose logs -f
```

### OrbStack Setup
If using OrbStack instead of Docker Desktop:
1. Install OrbStack from https://orbstack.dev
2. Start OrbStack
3. Use normal Docker commands - OrbStack automatically handles the Docker daemon

### Tests
```bash
cd datafetcher
python tests/test_scheduler.py
python tests/test_historical_institutional.py
```

### Cron Setup
```bash
cd datafetcher
chmod +x setup_cron.sh
./setup_cron.sh
```

## Docker Commands
```bash
# Build image only
docker build -t tradetitan-datafetcher .

# Run container directly
docker run -d --name tradetitan-datafetcher \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  tradetitan-datafetcher

# Check container status
docker ps

# View container logs
docker logs tradetitan-datafetcher

# Stop and remove container
docker stop tradetitan-datafetcher
docker rm tradetitan-datafetcher
```