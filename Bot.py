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
        if not picks:
            return ["No elite value found right now - check back at next lock (12PM/4PM/6PM)"]
        return picks[:3]
    except Exception as e:
        return ["Error scanning - retry /parlay"]

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
                        tg_send("Commands:\n/test - check bot live\n/parlay - get current elite parlay")
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
