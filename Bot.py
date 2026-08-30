# LOUIS $29 SAVER - 3 SCANS A DAY = 270 CREDITS/MONTH
import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
CHAT = os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","")
ODDS_API = os.environ.get("ODDS_API","") or os.environ.get("ODDS_API_KEY","")

app = Flask(__name__)
@app.route('/')
def home(): return "LOUIS 3X DAY SAVER LIVE"

last_id=0
sent_today=set()

def tg_send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":t}, timeout=15)
    except: pass

def get_dogs():
    dogs=[]
    if ODDS_API:
        try:
            url=f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API}&regions=us&markets=h2h&oddsFormat=american&bookmakers=fanduel,draftkings"
            r=requests.get(url,timeout=10).json()
            if isinstance(r,list):
                for g in r[:20]:
                    for b in g.get('bookmakers',[]):
                        for m in b.get('markets',[]):
                            for o in m.get('outcomes',[]):
                                p=o.get('price',0)
                                if 130 <= p <= 350:
                                    dogs.append({"team":o['name'],"odds":f"+{p}","match":f"{g.get('away_team','')} @ {g.get('home_team','')}"})
        except: pass
    if len(dogs)<3:
        dogs=[{"team":"Brewers ML","odds":"+185","match":"Cubs @ Brewers"},{"team":"Rays ML","odds":"+210","match":"Yankees @ Rays"},{"team":"D-Backs ML","odds":"+165","match":"Dodgers @ D-Backs"}]
    return dogs[:3]

def format_parlay(picks,label):
    txt=f"🔒 {label} VEGAS 10.5\n\n"
    total=1.0
    for p in picks:
        txt+=f"• {p['team']} {p['odds']} - {p['match']}\n"
        try: total*=(int(p['odds'].replace('+',''))/100+1)
        except: pass
    win=int((total-1)*10)
    txt+=f"\n$10 TO WIN ${win}\n$25 TO WIN ${win*2.5:.0f}\n\n💰 SAVER - 1 credit"
    return txt

def poll():
    global last_id
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=25",timeout=30).json()
            for u in r.get('result',[]):
                last_id=u['update_id']
                t=u.get('message',{}).get('text','').lower()
                if '/test' in t:
                    d=get_dogs()
                    tg_send(format_parlay(d,"TEST"))
        except: time.sleep(5)
        time.sleep(3)

def scheduler():
    while True:
        try:
            now=datetime.now()
            label=None
            if now.hour==12 and now.minute==0: label="12PM LUNCH LOCK"
            elif now.hour==16 and now.minute==0: label="4PM EARLY LOCK"
            elif now.hour==18 and now.minute==0: label="6PM PRIME LOCK"
            if label:
                key=f"{now.day}_{now.hour}"
                if key not in sent_today:
                    d=get_dogs()
                    tg_send(format_parlay(d,label))
                    sent_today.add(key)
            time.sleep(50)
        except: time.sleep(60)

threading.Thread(target=poll,daemon=True).start()
threading.Thread(target=scheduler,daemon=True).start()

if __name__=="__main__":
    app.run(host='0.0.0.0',port=10000)
