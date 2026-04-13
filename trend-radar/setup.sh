#!/bin/bash
# ═══════════════════════════════════════════════════════
# 🎮 TREND RADAR — Quick Setup Script
# ═══════════════════════════════════════════════════════

echo "🎮 Trend Radar — Setup"
echo "======================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Install it first:"
    echo "   brew install python3"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Navigate to trend-radar directory
cd "$(dirname "$0")"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Create data directories
mkdir -p data/digests

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  Created .env file. You need to configure it!"
    echo ""
    echo "📱 TELEGRAM BOT SETUP (2 minutes):"
    echo "   1. Open Telegram"
    echo "   2. Search for @BotFather"
    echo "   3. Send /newbot"
    echo "   4. Give it a name (e.g., 'My Trend Radar')"
    echo "   5. Give it a username (e.g., 'trend_radar_1234_bot')"
    echo "   6. Copy the API TOKEN → paste in .env"
    echo ""
    echo "   7. Search for @userinfobot"
    echo "   8. Send /start"
    echo "   9. Copy your CHAT ID → paste in .env"
    echo ""
    echo "📝 Edit the .env file:"
    echo "   nano .env"
    echo ""
else
    echo "✅ .env file already exists"
fi

echo ""
echo "═══════════════════════════════════════════════════════"
echo "✅ Setup complete!"
echo ""
echo "🚀 Quick Start:"
echo "   source venv/bin/activate"
echo "   python trend_radar.py          # Single scan"
echo "   python run_scheduler.py        # Continuous (every 30 min)"
echo "   python run_scheduler.py --interval 15  # Every 15 min"
echo ""
echo "═══════════════════════════════════════════════════════"
