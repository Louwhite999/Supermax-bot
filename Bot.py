# SUPERMAX ELITE SAVER - LOUIS FINAL - TOP 3 ONLY - WITH COMMANDS
import os, requests, time, threading, json
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
CHAT = os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","")
ODDS_API = os.environ.get("ODDS_API","") or os.environ.get("ODDS_API_KEY","")

app = Flask(__name__)
last_update_id = 0

SENT_FILE = "/tmp/sent_today.json"
try:
    with open(SENT_FILE) as f:
        sent_today = set(json.load(f))
except:
    sent_today = set()

def tg_send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"TG SEND ERR {e}")

def get_elite_picks():
    try:
        picks = []
        if not ODDS_API:
            print("No ODDS_API key")
            return ["* Rays ML +210 - Yankees @ Rays - VEGAS 10.5 ELITE", "* D-Backs ML +165 - Dodgers @ D-Backs - VALUE FILL"]
        url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?regions=us&markets=h2h&oddsFormat=american&apiKey={ODDS_API}"
        r = requests.get(url, timeout=15)
        print(f"ODDS API {r.status_code}")
        games = r.json()
        if not isinstance(games, list):
            return ["* Rays ML +210 - Yankees @ Rays - VEGAS 10.5 ELITE", "* D-Backs ML +165 - Dodgers @ D-Backs - VALUE FILL"]
        candidates = []
        for g in games:
            away = g.get('away_team','')
            home = g.get('home_team','')
            for book in g.get('bookmakers',[])[:5]:
                for mk in book.get('markets',[]):
                    if mk.get('key')!= 'h2h':
                        continue
                    for out in mk.get('outcomes',[]):
                        team = out.get('name','')
                        price = out.get('price',0)
                        if price >= 150:
                            label = "VEGAS 10.5 ELITE" if price >= 190 else "VALUE FILL"
                            line = f"* {team} ML +{price} - {away} @ {home} - {label}"
                            candidates.append((price, line))
        candidates.sort(key=lambda x: x[0], reverse=True)
        seen=set()
        for _, line in candidates:
            tk = line.split(' ML')[0]
            if tk not in seen:
                picks.append(line)
                seen.add(tk)
            if len(picks)>=3:
                break
        if not picks:
            return ["* No ELITE dogs +150 found - check back at 12PM/4PM/6PM"]
        return picks
    except Exception as e:
        print(f"Picks err {e}")
        return [f"Error scanning: {e}"]

def format_parlay(picks, label):
    try:
        if isinstance(picks, list):
            body = "\n".join(picks)
        else:
            body = str(picks)
        header = f"🔥 {label} - SUPERMAX ELITE SAVER\n\n"
        footer = "\n\n💰 $10 TO WIN $85\n💰 $25 TO WIN $215\n\n✅ SUPERMAX ELITE - 1 CREDIT SCAN"
        return header + body + footer
    except:
        return f"{label}\n{picks}"

def scheduler():
    print("SCHEDULER STARTED - 12PM / 4PM / 6PM")
    while True:
        try:
            now=datetime.now()
            label=None
            if now.hour==12 and now.minute==0:
                label="12PM LUNCH LOCK"
            if now.hour==16 and now.minute==0:
                label="4PM EARLY LOCK"
            if now.hour==18 and now.minute==0:
                label="6PM PRIME LOCK"
            if label:
                key=f"{now.date()}_{now.hour}"
                if key not in sent_today:
                    print(f"Firing {label}")
                    tg_send(format_parlay(get_elite_picks(),label))
                    sent_today.add(key)
                    with open(SENT_FILE, "w") as f:
                        json.dump(list(sent_today), f)
                    time.sleep(55)
            time.sleep(10)
        except Exception as e:
            print(f"SCHED ERR {e}")
            time.sleep(60)

def command_listener():
    global last_update_id
    print("COMMAND LISTENER STARTED - /test /parlay")
    while True:
        try:
            url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=20"
            r = requests.get(url, timeout=30).json()
            if r.get("ok") and r.get("result"):
                for upd in r["result"]:
                    last_update_id = upd["update_id"]
                    msg = upd.get("message", {})
                    text = msg.get("text","").strip().lower()
                    if text.startswith("/test"):
                        tg_send("✅ SUPERMAX BOT LIVE - Scheduler: 12PM / 4PM / 6PM - Commands: /test /parlay /help")
                    elif text.startswith("/parlay"):
                        tg_send(format_parlay(get_elite_picks(),"LIVE PARLAY REQUEST"))
                    elif text.startswith("/help"):
                        tg_send("Commands:\n/test - check bot live\n/parlay - get current elite parlay\nLocks auto at 12PM 4PM 6PM")
        except Exception as e:
            print(f"CMD ERR {e}")
            time.sleep(5)
        time.sleep(2)

threading.Thread(target=scheduler, daemon=True).start()
threading.Thread(target=command_listener, daemon=True).start()

@app.route("/")
def home():
    return "SUPERMAX BOT LIVE - SCHEDULER + COMMANDS"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
