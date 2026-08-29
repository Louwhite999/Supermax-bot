# LOUIS SUPERMAX - VEGAS 10.5 ULTRA LIVE - 12pm + 4PM + 6PM LOCKS - NO PYTZ VERSION
import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN", "")
CHAT = os.environ.get("CHAT", "")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX VEGAS 10.5 ULTRA LIVE - 12pm + 4PM + 6PM LOCKS + $10"

sent_bets = set()
daily_sent = 0
last_reset_day = None
parlay_12pm_sent = False
parlay_4pm_sent = False
parlay_6pm_sent = False
record = {"wins": 0, "losses": 0}

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT, "text": text}, timeout=10)
    except Exception as e:
        print(f"send error {e}")

def calc_parlay_odds(list_odds):
    dec = 1.0
    for o in list_odds:
        try:
            v = str(o).replace('+','').replace('−','-').replace('–','-')
            iv = int(v)
            if iv > 0:
                dec *= (iv/100 + 1)
            else:
                dec *= (100/abs(iv) + 1)
        except:
            continue
    return int((dec-1)*100)

def get_boost_label(h,a):
    tags=["Steam Move","Travel Spot","Div Rev","Sharp Money"]
    return tags[hash(h+a)%len(tags)]

def format_single(p):
    return f"VEGAS 10.5 ULTRA DOG - {p['team']} {p['odds']}"

def format_parlay(picks, label):
    odds_list = [x['odds'] for x in picks]
    total = calc_parlay_odds(odds_list)
    txt = f"{label} PARLAY +{total}\n\n"
    for x in picks:
        txt += f"• {x['team']} {x['odds']}\n"
    txt += f"\n$10 TO WIN ${int(10*total/100)}"
    return txt

def get_picks():
    return [
        {'team':'Brewers ML','odds':'+125'},
    ]

def run_bot():
    global daily_sent, last_reset_day, parlay_12pm_sent, parlay_4pm_sent, parlay_6pm_sent
    while True:
        try:
            now = datetime.now()
            cur_day = now.day

            if last_reset_day != cur_day:
                daily_sent = 0
                sent_bets.clear()
                last_reset_day = cur_day
                parlay_12pm_sent = False
                parlay_4pm_sent = False
                parlay_6pm_sent = False

            picks = get_picks()

            if now.hour == 12 and now.minute < 10 and not parlay_12pm_sent:
                send_telegram(format_parlay(picks[:3], "12PM LUNCH"))
                parlay_12pm_sent = True

            if now.hour == 16 and now.minute < 10 and not parlay_4pm_sent:
                send_telegram(format_parlay(picks[:3], "4PM EARLY"))
                parlay_4pm_sent = True

            if now.hour == 18 and now.minute < 10 and not parlay_6pm_sent:
                send_telegram(format_parlay(picks[:3], "6PM PRIME"))
                parlay_6pm_sent = True

            time.sleep(60)
        except Exception as e:
            print(f"loop error {e}")
            time.sleep(60)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
