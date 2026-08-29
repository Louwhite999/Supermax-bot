# LOUIS SUPERMAX VEGAS 10.5 ULTRA REAL SCANNER - FINAL NO PYTZ
import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","")
CHAT = os.environ.get("CHAT","")
ODDS_API = os.environ.get("ODDS_API","")
BOOKMAKERS = "fanduel,draftkings,pinnacle"
SPORTS = ["americanfootball_nfl","americanfootball_ncaaf","baseball_mlb","basketball_wnba"]

app = Flask(__name__)
@app.route('/')
def home(): return "LOUIS SUPERMAX 10.5 ULTRA LIVE"

sent = set()
last_id = 0

def tg_send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":t}, timeout=15)
    except: pass

def get_dogs():
    dogs=[]
    if not ODDS_API: return dogs
    for sport in SPORTS:
        try:
            url=f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS_API}&regions=us&markets=h2h&oddsFormat=american&bookmakers={BOOKMAKERS}"
            r=requests.get(url,timeout=15).json()
            for g in r[:20]:
                home=g.get('home_team',''); away=g.get('away_team','')
                for b in g.get('bookmakers',[]):
                    for m in b.get('markets',[]):
                        for o in m.get('outcomes',[]):
                            price=o.get('price',0); team=o.get('name','')
                            if 130 <= price <= 350:
                                dogs.append({"team":team,"odds":f"+{price}","home":home,"away":away,"sport":sport,"away_team":away,"home_team":home,"time":g.get('commence_time','')[:16]})
        except: continue
    return dogs[:10]

def format_parlay(picks,label):
    if len(picks)<3: return f"TEST PARLAY - Only {len(picks)} ULTRA dogs, need 3. 4PM & 6PM locks silent if not enough."
    total=1.0
    txt=f"LOCK {label} PARLAY\n\n"
    for p in picks[:3]:
        txt+=f"• {p['team']} {p['odds']}\n"
        try: total*=(int(p['odds'].replace('+',''))/100+1)
        except: pass
    txt+=f"\n$10 TO WIN ${int((total-1)*10)}"
    return txt

def poll_commands():
    global last_id
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=20",timeout=25).json()
            for u in r.get('result',[]):
                last_id=u['update_id']
                text=u.get('message',{}).get('text','')
                if '/testparlay' in text:
                    d=get_dogs(); tg_send(format_parlay(d,"12PM TEST"))
                elif '/test' in text:
                    d=get_dogs()
                    if not d: tg_send("TEST - No ULTRA dogs yet. Scanner 60s. Check ODDS_API key.")
                    else: tg_send(f"VEGAS 10.5 ULTRA TEST - Found {len(d)} dogs\n{format_parlay(d,'TEST')}")
        except: time.sleep(5)
        time.sleep(2)

def scanner_loop():
    daily={}
    while True:
        try:
            dogs=get_dogs(); now=datetime.now()
            for p in dogs:
                key=p['team']+p['away']+p['home']
                if key not in sent:
                    tg_send(f"ULTRA DOG - {p['team']} {p['odds']} - {p['away']} @ {p['home']}")
                    sent.add(key)
            if now.hour in [13,17,19] and now.minute<10:
                k=f"parlay_{now.hour}_{now.day}"
                if k not in daily and len(dogs)>=3:
                    label={13:"12PM LUNCH",17:"4PM EARLY",19:"6PM PRIME"}[now.hour]
                    tg_send(format_parlay(dogs,label)); daily[k]=True
        except Exception as e: print(e)
        time.sleep(60)

threading.Thread(target=poll_commands,daemon=True).start()
threading.Thread(target=scanner_loop,daemon=True).start()

if __name__=="__main__":
    app.run(host='0.0.0.0',port=10000)
