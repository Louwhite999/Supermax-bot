# SUPERMAX V4 SMART MEMORY - Learns from yesterday 2-1
import os, requests, time, json, threading
from flask import Flask
from datetime import datetime, date

# Support BOTH your old names and new names
TOKEN = os.environ.get("TELEGRAM_TOKEN","") or os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_BOT_TOKEN","")
CHAT = os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","") or os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT","")
ODDS_API = os.environ.get("ODDS_API_KEY","") or os.environ.get("ODDS_API","") or os.environ.get("THE_ODDS_API_KEY","")

app = Flask(__name__)
last_update_id = 0
SENT_FILE = "/tmp/sent_today.json"
MEMORY_FILE = "/tmp/supermax_memory.json"

try:
    with open(SENT_FILE) as f:
        sent_today = set(json.load(f))
except:
    sent_today = set()

# SMART MEMORY FROM YESTERDAY 2-1
try:
    with open(MEMORY_FILE) as f:
        memory = json.load(f)
except:
    memory = {
        "yesterday_record": "2-1 (+$30.10 if Round Robin)",
        "wins": ["NYM +190 vs ATL (Underdog WON)", "SF +211 vs MIL (Underdog WON)"],
        "losses": ["OAK +215 vs HOU (Blowout 11-1 - avoid huge dog blowouts)"],
        "lessons": [
            "2-0 when picking +190 to +211 range",
            "0-1 when picking +215+ mega dogs vs top offenses (HOU)",
            "Round Robin / Singles > 3-team parlay - parlay lost but RR profit +$30.10",
            "AVOID Athletics (A's) until they prove - blowout 11-1"
        ],
        "avoid_teams": ["OAK", "Athletics", "A's"],
        "sweet_spot_odds": [190, 211],
        "bankroll_yesterday": "+$30.10 with smart staking"
    }

def save_sent():
    try:
        with open(SENT_FILE, 'w') as f:
            json.dump(list(sent_today), f)
    except: pass

def save_memory():
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory, f)
    except: pass

def send_telegram(text):
    if not TOKEN or not CHAT:
        print("Missing TOKEN/CHAT")
        return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        r = requests.post(url, json={"chat_id": CHAT, "text": text, "parse_mode":"Markdown"}, timeout=15)
        print(f"Telegram: {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"TG error {e}")
        return False

def get_live_dogs():
    if not ODDS_API:
        return [
            {"team": "Mets +195 vs Braves (Again - sweet spot)", "reason": "MEMORY: Won +190 yesterday, +190 to +211 = 2-0"},
            {"team": "Giants +205 vs Brewers (Again)", "reason": "MEMORY: Won +211 yesterday"},
            {"team": "Pirates +185 vs Cubs", "reason": "Smart +190 range, avoid OAK blowout type"}
        ]
    try:
        url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API}&regions=us&markets=hml&oddsFormat=american"
        r = requests.get(url, timeout=15).json()
        dogs = []
        for game in r[:15]:
            for book in game.get('bookmakers', [])[:1]:
                for market in book.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        price = outcome.get('price', 0)
                        team = outcome.get('name','')
                        if 190 <= price <= 215 and team not in memory.get("avoid_teams", []):
                            dogs.append({"team": f"{team} +{price}", "reason": f"Odds {price} in SMART sweet spot (2-0 yesterday)", "price": price})
        dogs = sorted(dogs, key=lambda x: abs(x.get('price',200)-200))[:3]
        if len(dogs) < 3:
            dogs.append({"team": "Fallback - Check manual +190 to +211", "reason": "Not enough API dogs, use eye test"})
        return dogs[:3]
    except Exception as e:
        print(f"Odds error {e}")
        return [
            {"team": "Mets +195 (Manual - memory says 2-0 in this range)", "reason": "API down - using memory sweet spot"},
            {"team": "Giants +205 (Manual)", "reason": "Won yesterday +211"},
            {"team": "Pirates +185", "reason": "Avoid A's - blowout 11-1 yesterday"}
        ]

def build_smart_message():
    today = date.today().strftime("%m/%d/%Y")
    dogs = get_live_dogs()
    
    msg = f"🧠 *SUPERMAX V4 SMART PICKS - {today}*\n"
    msg += f"Yesterday: {memory['yesterday_record']}\n"
    msg += f"Lesson: {memory['lessons'][2]}\n\n"
    msg += "🚫 *AVOIDING:* Athletics (blowout 11-1 yesterday)\n"
    msg += "✅ *SWEET SPOT:* +190 to +211 (2-0 yesterday)\n\n"
    msg += "*TODAY'S 3 DOGS (SMART FILTERED):*\n"
    for i, d in enumerate(dogs, 1):
        msg += f"{i}. {d['team']}\n   └ {d['reason']}\n"
    msg += "\n💰 *SMART STAKING (Learned):*\n"
    msg += "❌ DON'T: 3-team parlay (-$20 yesterday)\n"
    msg += "✅ DO: Singles + Round Robin 2's\n"
    msg += "   → Yesterday would be +$30.10 profit\n"
    msg += "   → $10 each Single + $5 RR (3x)\n\n"
    msg += "Bet like: $10 NYM, $10 SF, $10 PIT + $15 RR\n"
    msg += "Projected: Profit even if 1 of 3 loses\n"
    return msg

@app.route('/')
def home():
    return f"SUPERMAX V4 SMART - Memory: {memory['yesterday_record']} - Avoid: {memory['avoid_teams']}"

@app.route('/run')
def manual_run():
    msg = build_smart_message()
    send_telegram(msg)
    return msg.replace("\n","<br>")

def daily_job():
    while True:
        now = datetime.now()
        today_str = date.today().isoformat()
        key = f"{today_str}-smart"
        if key not in sent_today and now.hour == 17 and now.minute >= 5:
            msg = build_smart_message()
            if send_telegram(msg):
                sent_today.add(key)
                save_sent()
        time.sleep(60)

threading.Thread(target=daily_job, daemon=True).start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
