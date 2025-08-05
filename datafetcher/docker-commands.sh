#!/bin/bash

# TradeTitan Data Fetcher - OrbStack Optimized Commands
# Quick reference for building and running the container with OrbStack

set -e

# Detect if OrbStack is available
if command -v orb &> /dev/null; then
    DOCKER_CMD="orb"
    COMPOSE_CMD="orb compose"
    echo "🚀 TradeTitan Data Fetcher - OrbStack Commands"
else
    DOCKER_CMD="docker"
    COMPOSE_CMD="docker-compose"
    echo "🐳 TradeTitan Data Fetcher - Docker Commands"
fi
echo "============================================="

case "${1:-help}" in
    "build")
        echo "🔨 Building container image..."
        $DOCKER_CMD build -t tradetitan-datafetcher .
        echo "✅ Build complete!"
        ;;
    "test")
        echo "🧪 Testing container components..."
        $DOCKER_CMD run --rm \
          -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
          -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
          tradetitan-datafetcher test
        ;;
    "run-now")
        echo "🏃 Running data fetch immediately..."
        $DOCKER_CMD run --rm \
          -v $(pwd)/data:/app/data \
          -v $(pwd)/logs:/app/logs \
          -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
          -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
          tradetitan-datafetcher now
        ;;
    "run-weekly")
        echo "🏃 Running weekly data fetch immediately..."
        $DOCKER_CMD run --rm \
          -v $(pwd)/data:/app/data \
          -v $(pwd)/logs:/app/logs \
          -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
          -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
          tradetitan-datafetcher weekly
        ;;
    "start-scheduled")
        echo "⏰ Starting scheduled container..."
        $DOCKER_CMD run -d \
          --name tradetitan-datafetcher \
          --restart unless-stopped \
          -v $(pwd)/data:/app/data \
          -v $(pwd)/logs:/app/logs \
          -e NEWSAPI_KEY=7531b6c411ae476396b15a47fd4f64d4 \
          -e FRED_API_KEY=ba7a9c9cbabb77d258a8c0fa2141e27d \
          tradetitan-datafetcher scheduled
        echo "✅ Container started with automatic scheduling!"
        ;;
    "stop")
        echo "🛑 Stopping container..."
        $DOCKER_CMD stop tradetitan-datafetcher
        $DOCKER_CMD rm tradetitan-datafetcher
        echo "✅ Container stopped and removed!"
        ;;
    "logs")
        echo "📋 Viewing container logs..."
        $DOCKER_CMD logs -f tradetitan-datafetcher
        ;;
    "status")
        echo "📊 Container status:"
        $DOCKER_CMD ps -f name=tradetitan-datafetcher
        echo ""
        echo "📋 Recent log entries:"
        if [ -f "logs/scheduler.log" ]; then
            tail -5 logs/scheduler.log
        else
            echo "No log file found yet."
        fi
        ;;
    "compose-up")
        echo "🚀 Starting with compose..."
        $COMPOSE_CMD up -d
        echo "✅ Services started!"
        ;;
    "compose-down")
        echo "🛑 Stopping compose services..."
        $COMPOSE_CMD down
        echo "✅ Services stopped!"
        ;;
    "orbstack-info")
        echo "🔍 OrbStack system information..."
        if command -v orb &> /dev/null; then
            echo "OrbStack version:"
            orb version
            echo ""
            echo "Running containers:"
            orb ps
            echo ""
            echo "System resources:"
            orb stats --no-stream
        else
            echo "OrbStack not installed. Using standard Docker."
            docker version --format '{{.Server.Version}}'
        fi
        ;;
    *)
        echo "Available commands:"
        echo "  build          - Build the container image"
        echo "  test           - Test container components"
        echo "  run-now        - Run data fetch once immediately"
        echo "  run-weekly     - Run weekly data fetch once"
        echo "  start-scheduled - Start with automatic scheduling"
        echo "  stop           - Stop and remove container"
        echo "  logs           - View container logs"
        echo "  status         - Check container status"
        echo "  compose-up     - Start with compose"
        echo "  compose-down   - Stop compose services"
        echo "  orbstack-info  - Show OrbStack system information"
        echo ""
        echo "Examples:"
        echo "  ./docker-commands.sh build"
        echo "  ./docker-commands.sh test"
        echo "  ./docker-commands.sh start-scheduled"
        echo "  ./docker-commands.sh orbstack-info"
        ;;
esac