# LOUIS SUPERMAX - VEGAS 10.5 ULTRA LIVE - 12pm + 4PM + 6PM LOCKS
import os, requests, time, threading
from flask import Flask
from datetime import datetime
import pytz

TOKEN = os.environ.get("TOKEN", "")
CHAT = os.environ.get("CHAT", "")
ODDS_API = os.environ.get("ODDS_API", "")

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
    return f"""🔥 VEGAS 10.5 ULTRA DOG - {p['team']} {p['odds']} ({p['market']})
Sport: {p['sport']}
Boosts: {p['boost']}
Game: {p['away']} @ {p['home']}
Sharp: Pinnacle/Circa/Bookmaker
Time: {p['time']}"""

def format_parlay(picks, label):
    odds_list = [x['odds'] for x in picks]
    total = calc_parlay_odds(odds_list)
    txt = f"🔒 {label} PARLAY +{total}\n\n"
    for x in picks:
        txt += f"• {x['team']} {x['odds']} - {x['away']} @ {x['home']}\n"
    txt += f"\n$10 TO WIN ${int(10*total/100)}"
    return txt

def get_picks():
    # YOUR PICK LOGIC HERE - THIS IS PLACEHOLDER THAT WON'T CRASH
    # Replace with your real Odds API fetch
    return [
        {'team':'Brewers ML','odds':'+125','market':'ML','sport':'MLB','boost':'Steam Move','away':'Brewers','home':'Cubs','time':'6:40pm ET'},
    ]

def run_bot():
    global daily_sent, last_reset_day, parlay_12pm_sent, parlay_4pm_sent, parlay_6pm_sent
    ct = pytz.timezone('America/Chicago')
    while True:
        try:
            now = datetime.now(ct)
            cur_day = now.day

            if last_reset_day != cur_day:
                daily_sent = 0
                sent_bets.clear()
                last_reset_day = cur_day
                parlay_12pm_sent = False
                parlay_4pm_sent = False
                parlay_6pm_sent = False

            picks = get_picks()

            # 12PM CT PARLAY
            if now.hour == 12 and now.minute < 10 and not parlay_12pm_sent and picks:
                txt = format_parlay(picks[:3], "12PM LUNCH")
                send_telegram(txt)
                parlay_12pm_sent = True

            # 4PM CT PARLAY
            if now.hour == 16 and now.minute < 10 and not parlay_4pm_sent and picks:
                txt = format_parlay(picks[:3], "4PM EARLY")
                send_telegram(txt)
                parlay_4pm_sent = True

            # 6PM CT PARLAY
            if now.hour == 18 and now.minute < 10 and not parlay_6pm_sent and picks:
                txt = format_parlay(picks[:3], "6PM PRIME")
                send_telegram(txt)
                parlay_6pm_sent = True

            time.sleep(60)
        except Exception as e:
            print(f"loop error {e}")
            time.sleep(60)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
