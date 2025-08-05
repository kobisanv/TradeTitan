# TradeTitan Data Fetcher - Test Instructions

## 🧪 Running Tests

### Quick Test
```bash
# Run all tests
python3 test_datafetcher.py

# Or make it executable and run directly
chmod +x test_datafetcher.py
./test_datafetcher.py
```

### Test Results Interpretation

The test suite checks:

**✅ Environment & Dependencies**
- Python version (3.8+ required)
- Required packages (yfinance, pandas, etc.)

**🔑 API Key Configuration**
- NewsAPI key for news sentiment
- FRED API key for economic data
- Optional Reddit API keys

**📁 Directory Structure**
- All required data directories
- Log directory permissions

**🔌 Data Fetchers**
- Individual stock fetchers (NVDA, AMZN, GOOGL, MSFT)
- ETF fetchers (QQQ, SPY)
- Specialized fetchers (VIX, options, institutional)

**⚙️ System Components**
- Scheduler functionality
- Docker configuration
- File permissions

**🌐 Connectivity**
- Yahoo Finance API
- NewsAPI (if configured)
- Quick data fetch test

## 📊 Test Report

After running tests, you'll get:
- **Console output** with colored status indicators
- **JSON report** saved to `test_report.json`

### Success Rates
- **100%**: All systems operational ✅
- **95-99%**: Minor issues, should work with reduced functionality ⚠️
- **<95%**: Multiple issues, fix before using 🚨

## 🔧 Fixing Common Issues

### Missing Packages
```bash
pip3 install python-dotenv newsapi-python beautifulsoup4
```

### API Key Issues
1. Check `.env` file exists
2. Verify API keys are correct
3. Test API connectivity manually

### Permission Issues
```bash
chmod -R 755 data/ logs/
```

### Docker Issues
1. Ensure Docker is installed
2. Check `dockerfile` and `docker-compose.yml`
3. Verify `entrypoint.sh` is executable

## 🚀 Docker Testing

Test the Docker container:
```bash
# Build and test
./docker-commands.sh build
./docker-commands.sh test

# Quick functionality test
./docker-commands.sh run-now
```

## 📈 Interpreting Results

### Green (✅) - Success
Component is working correctly

### Yellow (⚠️) - Warning
- Optional components not configured
- Minor issues that don't break functionality

### Red (❌) - Error
- Required components missing/broken
- Critical issues that need fixing

## 🎯 Recommended Workflow

1. **Run initial test**: `python3 test_datafetcher.py`
2. **Fix any red errors**: Install missing packages, configure APIs
3. **Run test again**: Verify fixes worked
4. **Test Docker setup**: `./docker-commands.sh test`
5. **Do a live data fetch**: `./docker-commands.sh run-now`

## 📋 Test Categories

| Category | Tests | Purpose |
|----------|-------|---------|
| Environment | Python version, packages | Basic setup |
| API Keys | NewsAPI, FRED, Reddit | External data access |
| Directories | Data folders, permissions | File system setup |
| Fetchers | Stock, ETF, specialized | Core functionality |
| Scheduler | Import, functions | Automation system |
| Docker | Files, permissions | Containerization |
| Connectivity | APIs, data fetch | Network access |

## 🐛 Troubleshooting

### Test Fails to Start
```bash
# Check Python path
which python3

# Check if in correct directory
pwd
ls -la test_datafetcher.py
```

### Import Errors
```bash
# Install requirements
pip3 install -r requirements.txt

# Check package installation
python3 -c "import yfinance; print('OK')"
```

### Connectivity Issues
```bash
# Test internet connection
curl -I https://query1.finance.yahoo.com

# Test API keys manually
python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('NewsAPI:', os.getenv('NEWSAPI_KEY', 'Not set'))
"
```

## 📞 Support

If tests consistently fail:
1. Check the generated `test_report.json` for detailed error messages
2. Verify all requirements are installed
3. Ensure API keys are valid and active
4. Check internet connectivity
5. Review Docker setup if using containers

The test suite is designed to be comprehensive but quick (under 5 seconds for most runs).