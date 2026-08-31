# SUPERMAX ELITE SAVER - LOUIS FINAL - TOP 3 ONLY
import os, requests, time, threading, json
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
CHAT = os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","")
ODDS_API = os.environ.get("ODDS_API","") or os.environ.get("ODDS_API_KEY","")

app = Flask(__name__)
last_id = 0

SENT_FILE = "/tmp/sent_today.json"
try:
    with open(SENT_FILE) as f:
        sent_today = set(json.load(f))
except:
    sent_today = set()

def tg_send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": msg, "parse_mode": "HTML"})
    except Exception as e:
        print(f"TG ERR {e}")

def get_elite_picks():
    # your elite picks logic - keep your original here
    try:
        # Example - put your API call back here
        return ["ELITE PICK PLACEHOLDER - ADD YOUR LOGIC"]
    except:
        return []

def format_parlay(picks, label):
    return f"{label}\n" + "\n".join(str(p) for p in picks)

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

threading.Thread(target=scheduler, daemon=True).start()

@app.route("/")
def home():
    return "SUPERMAX BOT LIVE"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
