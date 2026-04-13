# 🎮 Trend Radar v2 — اللعبة الخفية Content Machine

Detects what's trending in Morocco → generates a ready-to-film content blueprint in Darija → sends it to your Telegram.

## What You Get on Telegram

For EACH trend, you receive:
```
🚨 TREND DETECTED

📰 [What's happening]
📍 Source | Category (Sport/Politics/Tech/etc.)

🎮 INVISIBLE GAME TITLE:
«اللعبة اللي ما حد شافها ف: [event]»

📝 SDCCR SCRIPT:
🎯 SITUATION → Hook in Darija + visual directions
🎯 DESIRE → Context setup
🎯 CONFLICT → Hidden game reveal  
🎯 CHANGE → The key line
🎯 RESULT → Payoff
🔁 LOOP → Seamless restart

🎬 Visual tips + Dahih × Nasser style reminders
⏱️ Format suggestion (Reel/Short/Long-form)
```

## Sources Monitored

| Source | What | How often |
|---|---|---|
| 📰 Morocco News (8 sites) | Hespress, Le360, Challenge, TelQuel, H24, Alyaoum24, Medias24 | Every scan |
| 📊 Google Trends Morocco | What Moroccans are searching RIGHT NOW | Every scan |
| 🐦 Twitter/X Morocco | Top trending hashtags | Every scan |
| ▶️ YouTube Trending Morocco | What Morocco is watching | Every scan |
| 🎵 TikTok | Trending hashtags + Morocco content | Every scan |
| 📸 Instagram | Morocco hashtag monitoring | Every scan |
| 🔴 Reddit | r/Morocco + r/Entrepreneur + r/Marketing | Every scan |
| 🌍 World News | BBC, TechCrunch, The Verge, Al Jazeera | Every scan |

## Setup (3 minutes)

### 1. Create Telegram Bot
1. Open Telegram → search **@BotFather** → send `/newbot`
2. Name it → copy the **TOKEN**
3. Search **@userinfobot** → send `/start` → copy your **CHAT ID**

### 2. Configure
```bash
cd trend-radar
cp .env.example .env
# Paste your TOKEN and CHAT ID in .env
```

### 3. Install & Run
```bash
# First time only:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run single scan:
python trend_radar.py

# Run continuously (every 30 min):
python trend_radar.py --loop

# Custom interval (every 15 min):
python trend_radar.py --loop --interval 15

# Run in background:
nohup python trend_radar.py --loop &
```

## Cost: $0/month
Everything is free — Python, Telegram, RSS, Google Trends, Reddit API.
