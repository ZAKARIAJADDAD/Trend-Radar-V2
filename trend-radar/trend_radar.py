"""
🎮 TREND RADAR v2 — The Invisible Game Content Machine
========================================================
Monitors Morocco + World trends → generates ready-to-film
content blueprints in Darija → sends to your Telegram.

Features:
- Morocco news (8 sources)
- Google Trends Morocco
- Twitter/X trending Morocco  
- YouTube trending Morocco
- TikTok/Instagram trending hashtags
- Facebook popular pages
- Auto-generates "Invisible Game" content blueprint for each trend
- Sends rich Telegram alerts with title + SDCCR script + visual hints

Usage:
    python trend_radar.py           # Single scan
    python trend_radar.py --loop    # Continuous (every 30 min)
    python trend_radar.py --loop --interval 15  # Every 15 min
"""
import os
import json
import asyncio
import hashlib
import argparse
import time
import signal
import sys
import re
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ═══════════════════════════════════════════════════════
# SETUP
# ═══════════════════════════════════════════════════════
load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

SEEN_FILE = DATA_DIR / "seen.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/124.0.0.0 Safari/537.36"
}


def load_config():
    with open(BASE_DIR / "sources.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_seen():
    if SEEN_FILE.exists():
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_seen(seen):
    # Keep only last 3 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=3)).isoformat()
    cleaned = {k: v for k, v in seen.items() if v.get("t", "") > cutoff}
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False)


def is_new(seen, item_id):
    return item_id not in seen


def mark_seen(seen, item_id):
    seen[item_id] = {"t": datetime.now(timezone.utc).isoformat()}


def get_hash(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]


# ═══════════════════════════════════════════════════════
# CONTENT BLUEPRINT GENERATOR
# ═══════════════════════════════════════════════════════

def detect_category(title, summary=""):
    """Auto-detect the trend category."""
    text = f"{title} {summary}".lower()
    
    categories = {
        "⚽ Sport": ["football", "match", "goal", "fifa", "mondial", "raja", "wydad",
                     "كرة", "مباراة", "هدف", "لاعب", "champions", "league", "coupe"],
        "💰 Business": ["business", "entreprise", "startup", "investment", "bourse",
                        "économie", "economy", "billion", "million", "company", "brand"],
        "🤖 Tech / AI": ["AI", "artificial intelligence", "algorithm", "tech", "app",
                         "google", "apple", "meta", "microsoft", "robot", "خوارزمية"],
        "🏛️ Politique": ["politique", "politics", "government", "roi", "parlement",
                         "élection", "minister", "حكومة", "برلمان", "وزير", "ملك"],
        "🌍 World": ["war", "conflict", "usa", "europe", "china", "trump",
                     "ukraine", "gaza", "palestine", "حرب"],
        "🎭 Culture": ["film", "music", "art", "cinema", "festival", "serie",
                       "فيلم", "أغنية", "مهرجان", "ramadan", "رمضان", "عيد"],
        "📱 Social Media": ["instagram", "tiktok", "youtube", "viral", "influencer",
                            "reels", "trending", "فيديو", "محتوى"],
        "👕 Mode / Fashion": ["fashion", "mode", "luxury", "luxe", "zara", "nike",
                              "brand", "style", "design", "clothing"],
        "✈️ Migration": ["visa", "immigration", "migration", "هجرة", "أوروبا",
                         "passeport", "europe", "diaspora"],
        "🎓 Éducation": ["bac", "باك", "école", "université", "education",
                         "student", "تعليم", "مدرسة", "جامعة"],
        "😱 Buzz / Scandale": ["scandal", "scandale", "فضيحة", "exposed", "leaked",
                               "hack", "arrest", "اعتقال", "controversy", "drama"],
    }
    
    for cat, keywords in categories.items():
        if any(kw.lower() in text for kw in keywords):
            return cat
    return "📌 Trending"


def generate_blueprint(title, category, source):
    """
    Generate a complete content blueprint in Darija:
    - Invisible Game title
    - SDCCR script outline
    - Visual hints
    - Dahih × Nasser technique tips
    """
    
    # ─── Generate "Invisible Game" title options ───
    game_titles = [
        f"اللعبة اللي ما حد كيشوفها ف: {title}",
        f"شكون اللي كيلعب عليك ف {title}؟",
        f"القواعد الخفية ديال {title}",
        f"{title} — اللعبة اللي ما حد قالك عليها",
    ]
    
    # ─── Hooks (Dahih style — fast, confrontational) ───
    hooks = [
        f"«{title}» — و نتا تمّا كتفرج بحال إلا ما كاين والو...",
        f"كلشي كيهضر على «{title}» ولكن حتى واحد ما شاف اللعبة الحقيقية.",
        f"فاش كنتي كتسكرولّي، شي حد ربح من «{title}» و ما عرفتي.",
        f"واخا تكون سمعتي ب «{title}»، أنا متأكد ما عرفتيش هاد الحاجة...",
        f"«{title}»... ولكن ما حد قالك الحقيقة.",
    ]
    
    # ─── SDCCR Template ───
    sdccr = {
        "S": f"🎯 SITUATION (0:00-0:02):\n"
             f"   «{random.choice(hooks)}»\n"
             f"   📸 وجهك قريب من الكاميرا + subtitle كبير + bass hit",
        
        "D": f"🎯 DESIRE (0:02-0:07):\n"
             f"   عطي السياق بسرعة — أشنو وقع؟ شكون معني؟\n"
             f"   استعمل 3 تفاصيل محددة (أرقام، أسماء، أماكن)\n"
             f"   📸 cuts سريعة (0.8 ثانية) + B-roll ولا stock",
        
        "C": f"🎯 CONFLICT (0:07-0:22):\n"
             f"   كشف اللعبة! شكون اللي كيربح؟ شكون اللي كيخسر؟\n"
             f"   أشنو هي القواعد اللي ما حد كيشوفها؟\n"
             f"   • العائق الخارجي: أشنو كيمنع الحقيقة من تبان\n"
             f"   • الشك الداخلي: علاش الناس كتصدّق اللعبة\n" 
             f"   • الرهان: أشنو كيوقع إلا بقينا ما عارفين\n"
             f"   📸 cuts كيسرعو (0.7→0.5 ثانية) + صوت كيهبط + zoom in",

        "C2": f"🎯 CHANGE (0:22-0:30):\n"
              f"   ⚡ THE KEY MOMENT — هبّط الإيقاع بزّاف\n"
              f"   سكتة 0.5 ثانية... ثم قول جملة وحدة اللي كتبدّل كلشي\n"
              f"   هاد الجملة خاصها تخلّي المشاهد يسكتنشوتيها\n"
              f"   📸 شوط واحد ثابت (no cuts) + سكوت + عينيك فالكاميرا",

        "R": f"🎯 RESULT (0:30-0:38):\n"
             f"   الطاقة كترجع — أشنو وقع ملّي بانت اللعبة؟\n"
             f"   ما تقولش الجواب كامل — خلّي الصورة تقولو\n"
             f"   📸 montage سريع + logo/صورة + الموسيقى كتصعد",

        "LOOP": f"🔁 LOOP (0:38-0:41):\n"
                f"   آخر جملة خاصها ترجّعك للأولى\n"
                f"   نفس الكلمة، نفس النبرة، نفس le volume"
    }
    
    # ─── Visual & editing hints ───
    visual_hints = [
        "🎬 VISUAL TIPS:",
        f"• Category: {category}",
        "• Subtitles: MANDATORY — عربي كبير + ترجمة إنجليزية",
        "• Pattern interrupt كل 3-5 ثواني (zoom, cut, angle change)",
        "• وجهك = الإحساس / صوتك = المعلومة",
        "• Color grade: dark + warm (signature ديالك)",
        "• SFX maximum 3 (bass hit, silence, transition)",
        "• Film the HOOK last (ملّي تكون warm)",
    ]
    
    # ─── Dahih × Nasser technique reminders ───
    technique = [
        "📐 STYLE MIX:",
        "• Hook → الدحيح (سريع، مباشر، كيحرّك)",
        "• Story → أنت (سرد سينمائي، tension)",  
        "• Insight → دوباميكافين (هدوء، وضوح، جملة وحدة كتبقى)",
        "• Humor = ملح ماشي الطبق — ضحّك و خلّي المعلومة توصل",
    ]
    
    # ─── Format suggestion ───
    format_tip = "⏱️ FORMAT: Reel (35-45s) + YouTube Short (45-58s)\n"
    format_tip += "   إلا الموضوع كبير → YouTube Long-form (8-12 min)"
    
    return {
        "game_title": random.choice(game_titles),
        "hook": random.choice(hooks),
        "sdccr": sdccr,
        "visual_hints": "\n".join(visual_hints),
        "technique": "\n".join(technique),
        "format": format_tip
    }


def format_telegram_message(trend, blueprint):
    """Format a rich Telegram alert with the full content blueprint."""
    
    msg = f"{'='*35}\n"
    msg += f"🚨 *TREND DETECTED*\n"
    msg += f"{'='*35}\n\n"
    
    msg += f"📰 *{trend['title']}*\n"
    msg += f"📍 {trend['source']} | {trend['category']}\n"
    msg += f"🔗 {trend.get('link', 'N/A')}\n\n"
    
    msg += f"{'─'*35}\n"
    msg += f"🎮 *INVISIBLE GAME TITLE:*\n"
    msg += f"«{blueprint['game_title']}»\n\n"
    
    msg += f"{'─'*35}\n"
    msg += f"📝 *SDCCR SCRIPT:*\n\n"
    msg += f"{blueprint['sdccr']['S']}\n\n"
    msg += f"{blueprint['sdccr']['D']}\n\n"
    msg += f"{blueprint['sdccr']['C']}\n\n"
    msg += f"{blueprint['sdccr']['C2']}\n\n"
    msg += f"{blueprint['sdccr']['R']}\n\n"
    msg += f"{blueprint['sdccr']['LOOP']}\n\n"
    
    msg += f"{'─'*35}\n"
    msg += f"{blueprint['visual_hints']}\n\n"
    msg += f"{blueprint['technique']}\n\n"
    msg += f"{blueprint['format']}\n"
    msg += f"{'='*35}\n"
    
    return msg


# ═══════════════════════════════════════════════════════
# DATA COLLECTORS
# ═══════════════════════════════════════════════════════

def collect_rss(config, seen):
    """Collect from all RSS feeds (Morocco + World)."""
    items = []
    all_feeds = config["morocco_trends"]["news_feeds"] + config["world_trends"]["feeds"]
    
    for feed_info in all_feeds:
        try:
            feed = feedparser.parse(feed_info["url"])
            for entry in feed.entries[:8]:
                uid = get_hash(entry.get("link", "") + entry.get("title", ""))
                if not is_new(seen, uid):
                    continue
                
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                text = f"{title} {summary}".lower()
                
                # Check if it matches any content pillar keyword
                keywords = config["content_pillars"]["keywords"]
                matches = [k for k in keywords if k.lower() in text]
                
                if len(matches) >= 1:
                    category = detect_category(title, summary)
                    items.append({
                        "title": title,
                        "source": feed_info["name"],
                        "link": entry.get("link", ""),
                        "category": category,
                        "matches": matches[:5],
                        "score": len(matches) * 10,
                        "type": "news"
                    })
                
                mark_seen(seen, uid)
                
        except Exception as e:
            print(f"   ⚠️ {feed_info['name']}: {e}")
    
    return items


def collect_google_trends(config, seen):
    """Collect Google Trends Morocco."""
    items = []
    url = config["morocco_trends"]["google_trends_rss"]
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            feed = feedparser.parse(r.content)
            for entry in feed.entries[:15]:
                uid = get_hash(f"gt_{entry.get('title', '')}_{datetime.now().strftime('%Y%m%d')}")
                if not is_new(seen, uid):
                    continue
                
                title = entry.get("title", "")
                traffic = entry.get("ht_approx_traffic", "")
                
                items.append({
                    "title": title,
                    "source": "📊 Google Trends Morocco",
                    "link": entry.get("link", ""),
                    "category": detect_category(title),
                    "matches": [f"Traffic: {traffic}"],
                    "score": 50,
                    "type": "google_trends"
                })
                mark_seen(seen, uid)
    except Exception as e:
        print(f"   ⚠️ Google Trends: {e}")
    
    return items


def collect_twitter_trends(seen):
    """Collect Twitter/X trending in Morocco."""
    items = []
    
    try:
        r = requests.get("https://trends24.in/morocco/", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            trend_links = soup.select(".trend-card__list li a")
            
            for i, tag in enumerate(trend_links[:15]):
                topic = tag.get_text(strip=True)
                uid = get_hash(f"tw_{topic}_{datetime.now().strftime('%Y%m%d%H')}")
                if not is_new(seen, uid):
                    continue
                
                items.append({
                    "title": topic,
                    "source": f"🐦 Twitter/X Morocco (#{i+1})",
                    "link": f"https://twitter.com/search?q={topic}",
                    "category": detect_category(topic),
                    "matches": ["Trending on X"],
                    "score": 45 - i * 2,  # Higher rank = higher score
                    "type": "twitter"
                })
                mark_seen(seen, uid)
    except Exception as e:
        print(f"   ⚠️ Twitter: {e}")
    
    return items


def collect_youtube_trending(seen):
    """Collect YouTube trending videos in Morocco."""
    items = []
    
    try:
        r = requests.get(
            "https://www.youtube.com/feed/trending?gl=MA",
            headers=HEADERS, timeout=15
        )
        if r.status_code == 200:
            # Extract video titles from the page
            # YouTube uses JSON embedded in the page
            patterns = re.findall(r'"title":\{"runs":\[\{"text":"([^"]+)"\}\]', r.text)
            
            for i, title in enumerate(patterns[:10]):
                uid = get_hash(f"yt_{title}_{datetime.now().strftime('%Y%m%d')}")
                if not is_new(seen, uid):
                    continue
                
                items.append({
                    "title": title,
                    "source": f"▶️ YouTube Trending Morocco (#{i+1})",
                    "link": "https://www.youtube.com/feed/trending?gl=MA",
                    "category": detect_category(title),
                    "matches": ["YouTube Trending MA"],
                    "score": 55 - i * 3,
                    "type": "youtube"
                })
                mark_seen(seen, uid)
    except Exception as e:
        print(f"   ⚠️ YouTube: {e}")
    
    return items


def collect_tiktok_trends(seen):
    """Collect TikTok trending topics via Creative Center."""
    items = []
    
    try:
        # TikTok Creative Center trending hashtags
        r = requests.get(
            "https://ads.tiktok.com/business/creativecenter/hashtag/pc/en",
            headers=HEADERS, timeout=15
        )
        if r.status_code == 200:
            # Try to extract trending hashtags
            soup = BeautifulSoup(r.text, "html.parser")
            hashtag_elements = soup.select("[class*='hashtag'] a, [class*='trend'] a")
            
            for tag in hashtag_elements[:10]:
                topic = tag.get_text(strip=True)
                if not topic or len(topic) < 2:
                    continue
                    
                uid = get_hash(f"tt_{topic}_{datetime.now().strftime('%Y%m%d')}")
                if not is_new(seen, uid):
                    continue
                
                items.append({
                    "title": f"#{topic}",
                    "source": "🎵 TikTok Trending",
                    "link": f"https://www.tiktok.com/tag/{topic}",
                    "category": detect_category(topic),
                    "matches": ["TikTok Trend"],
                    "score": 40,
                    "type": "tiktok"
                })
                mark_seen(seen, uid)
    except Exception as e:
        print(f"   ⚠️ TikTok: {e}")
    
    # Also check Morocco-specific TikTok hashtags
    morocco_tags = ["moroccotrend", "marocbuzz", "darija", "morocco"]
    for tag in morocco_tags:
        try:
            r = requests.get(
                f"https://www.tiktok.com/tag/{tag}",
                headers=HEADERS, timeout=10
            )
            if r.status_code == 200:
                # Extract any video titles/descriptions
                titles = re.findall(r'"desc":"([^"]{20,100})"', r.text)
                for title in titles[:3]:
                    uid = get_hash(f"ttma_{title}")
                    if not is_new(seen, uid):
                        continue
                    items.append({
                        "title": title,
                        "source": f"🎵 TikTok #{tag}",
                        "link": f"https://www.tiktok.com/tag/{tag}",
                        "category": detect_category(title),
                        "matches": ["TikTok Morocco"],
                        "score": 35,
                        "type": "tiktok"
                    })
                    mark_seen(seen, uid)
        except:
            pass
    
    return items


def collect_instagram_trends(seen):
    """Monitor trending Instagram hashtags for Morocco."""
    items = []
    
    morocco_hashtags = [
        "المغرب", "maroc", "casablanca", "moroccanstyle",
        "moroccanfood", "darija", "marocain"
    ]
    
    for hashtag in morocco_hashtags:
        try:
            r = requests.get(
                f"https://www.instagram.com/explore/tags/{hashtag}/",
                headers={
                    **HEADERS,
                    "Accept": "text/html,application/xhtml+xml"
                },
                timeout=10
            )
            if r.status_code == 200:
                # Try to extract post count or trending content
                post_counts = re.findall(r'"count":(\d+)', r.text)
                edge_texts = re.findall(r'"text":"([^"]{15,120})"', r.text)
                
                for text in edge_texts[:2]:
                    uid = get_hash(f"ig_{text}")
                    if not is_new(seen, uid):
                        continue
                    items.append({
                        "title": text,
                        "source": f"📸 Instagram #{hashtag}",
                        "link": f"https://www.instagram.com/explore/tags/{hashtag}/",
                        "category": detect_category(text),
                        "matches": ["Instagram Morocco"],
                        "score": 30,
                        "type": "instagram"
                    })
                    mark_seen(seen, uid)
        except:
            pass
    
    return items


def collect_reddit_morocco(seen):
    """Check r/Morocco + business subreddits."""
    items = []
    
    subs = [
        ("r/Morocco", "https://www.reddit.com/r/Morocco/hot.json?limit=10"),
        ("r/Entrepreneur", "https://www.reddit.com/r/Entrepreneur/hot.json?limit=8"),
        ("r/Marketing", "https://www.reddit.com/r/marketing/hot.json?limit=8"),
    ]
    
    for sub_name, url in subs:
        try:
            r = requests.get(url, headers={
                "User-Agent": "TrendRadar/2.0 (Content Research)"
            }, timeout=15)
            
            if r.status_code != 200:
                continue
            
            posts = r.json().get("data", {}).get("children", [])
            
            for post in posts:
                d = post.get("data", {})
                score = d.get("score", 0)
                if score < 50:
                    continue
                
                title = d.get("title", "")
                uid = get_hash(f"rd_{d.get('id', '')}")
                if not is_new(seen, uid):
                    continue
                
                items.append({
                    "title": title,
                    "source": f"🔴 Reddit {sub_name}",
                    "link": f"https://reddit.com{d.get('permalink', '')}",
                    "category": detect_category(title),
                    "matches": [f"⬆️ {score} upvotes"],
                    "score": min(60, score // 10),
                    "type": "reddit"
                })
                mark_seen(seen, uid)
                
        except Exception as e:
            print(f"   ⚠️ Reddit {sub_name}: {e}")
    
    return items


# ═══════════════════════════════════════════════════════
# TELEGRAM SENDER
# ═══════════════════════════════════════════════════════

async def send_to_telegram(trends_with_blueprints):
    """Send trend alerts to Telegram."""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id or "your_" in token:
        print("\n⚠️  Telegram not configured — printing to console:\n")
        for trend, blueprint in trends_with_blueprints[:5]:
            msg = format_telegram_message(trend, blueprint)
            print(msg)
        return
    
    import telegram
    bot = telegram.Bot(token=token)
    
    # Send top trends (max 5 per scan to avoid spam)
    for trend, blueprint in trends_with_blueprints[:5]:
        msg = format_telegram_message(trend, blueprint)
        
        # Telegram has 4096 char limit — split if needed
        if len(msg) > 4000:
            msg = msg[:3990] + "\n..."
        
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=msg,
                parse_mode=None,  # Plain text to avoid markdown issues
                disable_web_page_preview=True
            )
            await asyncio.sleep(2)  # Rate limit
        except Exception as e:
            print(f"   ⚠️ Telegram error: {e}")
            # Try without parse mode
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=msg[:4000],
                    disable_web_page_preview=True
                )
            except:
                pass
    
    # Send a summary count
    total = len(trends_with_blueprints)
    if total > 5:
        try:
            summary = (
                f"📊 Scan complete: {total} trends detected\n"
                f"📱 Top 5 sent above. Full digest saved locally.\n"
                f"⏰ {datetime.now().strftime('%H:%M %d/%m/%Y')}"
            )
            await bot.send_message(chat_id=chat_id, text=summary)
        except:
            pass


# ═══════════════════════════════════════════════════════
# MAIN SCAN
# ═══════════════════════════════════════════════════════

async def scan():
    """Run a full trend scan."""
    now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    print(f"\n{'='*50}")
    print(f"🎮 TREND RADAR — Scan at {now}")
    print(f"{'='*50}\n")
    
    config = load_config()
    seen = load_seen()
    all_trends = []
    
    # 1. News RSS
    print("📰 Scanning Moroccan + World news...")
    news = collect_rss(config, seen)
    all_trends.extend(news)
    print(f"   ✅ {len(news)} relevant articles")
    
    # 2. Google Trends Morocco
    print("📊 Scanning Google Trends Morocco...")
    gt = collect_google_trends(config, seen)
    all_trends.extend(gt)
    print(f"   ✅ {len(gt)} trending searches")
    
    # 3. Twitter/X Morocco
    print("🐦 Scanning Twitter/X Morocco...")
    tw = collect_twitter_trends(seen)
    all_trends.extend(tw)
    print(f"   ✅ {len(tw)} Twitter trends")
    
    # 4. YouTube Trending Morocco
    print("▶️ Scanning YouTube Trending Morocco...")
    yt = collect_youtube_trending(seen)
    all_trends.extend(yt)
    print(f"   ✅ {len(yt)} YouTube trends")
    
    # 5. TikTok
    print("🎵 Scanning TikTok trends...")
    tt = collect_tiktok_trends(seen)
    all_trends.extend(tt)
    print(f"   ✅ {len(tt)} TikTok trends")
    
    # 6. Instagram
    print("📸 Scanning Instagram Morocco...")
    ig = collect_instagram_trends(seen)
    all_trends.extend(ig)
    print(f"   ✅ {len(ig)} Instagram trends")
    
    # 7. Reddit
    print("🔴 Scanning Reddit...")
    rd = collect_reddit_morocco(seen)
    all_trends.extend(rd)
    print(f"   ✅ {len(rd)} Reddit posts")
    
    # Sort by score
    all_trends.sort(key=lambda x: x["score"], reverse=True)
    
    print(f"\n🎯 TOTAL: {len(all_trends)} trends detected")
    
    if all_trends:
        # Generate content blueprints for top trends
        trends_with_blueprints = []
        for trend in all_trends:
            bp = generate_blueprint(trend["title"], trend["category"], trend["source"])
            trends_with_blueprints.append((trend, bp))
        
        # Send to Telegram
        print("📱 Sending to Telegram...")
        await send_to_telegram(trends_with_blueprints)
        
        # Print top 3 to console
        print(f"\n🏆 TOP 3 TRENDS:")
        for i, (trend, bp) in enumerate(trends_with_blueprints[:3]):
            print(f"\n{'─'*40}")
            print(f"#{i+1} [{trend['category']}] {trend['title']}")
            print(f"    Source: {trend['source']}")
            print(f"    🎮 {bp['game_title']}")
            print(f"{'─'*40}")
    
    save_seen(seen)
    print(f"\n✅ Scan complete at {datetime.now().strftime('%H:%M:%S')}\n")


# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="🎮 Trend Radar v2")
    parser.add_argument("--loop", action="store_true", help="Continuous mode")
    parser.add_argument("--interval", type=int, default=30, help="Minutes between scans (default: 30)")
    args = parser.parse_args()
    
    signal.signal(signal.SIGINT, lambda s, f: (print("\n🛑 Stopped."), sys.exit(0)))
    
    if args.loop:
        print(f"🎮 Trend Radar v2 — Continuous Mode")
        print(f"⏰ Scanning every {args.interval} minutes")
        print(f"🛑 Press Ctrl+C to stop\n")
        
        while True:
            asyncio.run(scan())
            print(f"💤 Next scan in {args.interval} minutes...")
            time.sleep(args.interval * 60)
    else:
        asyncio.run(scan())


if __name__ == "__main__":
    main()
