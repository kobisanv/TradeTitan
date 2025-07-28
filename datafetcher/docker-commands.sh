#!/bin/bash
# TradeTitan DataFetcher Container Commands

# ===========================================
# ORBSTACK COMMANDS (Recommended for macOS)
# ===========================================

# Build the datafetcher image
echo "🏗️  Building TradeTitan DataFetcher image..."
orb build -t tradetitan-datafetcher:latest .

# Run production datafetcher
echo "🚀 Starting DataFetcher container..."
orb compose up -d

# Run development datafetcher
echo "🛠️  Starting DataFetcher in development mode..."
orb compose -f docker-compose.dev.yml up -d

# View logs
echo "📋 Viewing DataFetcher logs..."
orb logs tradetitan-datafetcher -f

# Execute commands in datafetcher container
echo "💻 Running command in DataFetcher container..."
orb exec tradetitan-datafetcher python NVDA/NVDAfetch.py

# Stop datafetcher container
echo "🛑 Stopping DataFetcher container..."
orb compose down

# ===========================================
# STANDARD DOCKER COMMANDS (Alternative)
# ===========================================

# Build the datafetcher image
echo "🏗️  Building TradeTitan DataFetcher image with Docker..."
docker build -t tradetitan-datafetcher:latest .

# Run production datafetcher
echo "🚀 Starting DataFetcher container with Docker..."
docker compose up -d

# Run development datafetcher
echo "🛠️  Starting DataFetcher in development mode with Docker..."
docker compose -f docker-compose.dev.yml up -d

# View logs
echo "📋 Viewing DataFetcher logs with Docker..."
docker logs tradetitan-datafetcher -f

# Execute commands in datafetcher container
echo "💻 Running command in DataFetcher container with Docker..."
docker exec -it tradetitan-datafetcher python NVDA/NVDAfetch.py

# Stop datafetcher container
echo "🛑 Stopping DataFetcher container with Docker..."
docker compose down

# ===========================================
# MAINTENANCE COMMANDS
# ===========================================

# View container status
echo "📊 Container status..."
orb ps

# Clean up unused resources
echo "🧹 Cleaning up..."
orb system prune -f

# View resource usage
echo "📈 Resource usage..."
orb stats

# Backup data (from parent directory)
echo "💾 Backing up data..."
cd .. && tar -czf tradetitan-backup-$(date +%Y%m%d).tar.gz data/ logs/ && cd datafetcher

echo "✅ TradeTitan DataFetcher setup complete!"
echo "📊 DataFetcher logs: orb logs tradetitan-datafetcher -f"
echo "📂 Data will be saved to ../data/ (shared with future ML pipeline)"