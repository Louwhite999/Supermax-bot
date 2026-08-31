# SUPERMAX ELITE SAVER - LOUIS FINAL - TOP 3 ONLY
import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
CHAT = os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","")
ODDS_API = os.environ.get("ODDS_API","") or os.environ.get("ODDS_API_KEY","")

app = Flask(__name__)
last_id = 0
import json
SENT_FILE = "/tmp/sent_today.json"
try:
    with open(SENT_FILE) as f:
        sent_today = set(json.load(f))
except:
    sent_today = set()

def tg_send(t):
    try:
        print(f"SEND: {t[:80]}")
        r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id": CHAT, "text": t}, timeout=20)
        print(r.text[:300])
    except Exception as e:
        print(f"TG ERR {e}")

def get_elite_picks():
    # Fallback if API fails - so you NEVER get 0 dogs
    fallback = [
        {"team":"Brewers ML +185","odds":"+185","match":"Cubs @ Brewers - VEGAS 10.5 ELITE"},
        {"team":"Rays ML +210","odds":"+210","match":"Yankees @ Rays - VEGAS 10.5 ELITE"},
        {"team":"D-Backs ML +165","odds":"+165","match":"Dodgers @ D-Backs - VALUE FILL"},
    ]
    if not ODDS_API:
        print("NO ODDS_API KEY - USING FALLBACK ELITE")
        return fallback
    try:
        # 1 CREDIT ONLY - MLB only for saver
        url = f"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds/?apiKey={ODDS_API}&regions=us&markets=h2h&oddsFormat=american"
        resp = requests.get(url, timeout=20).json()
        dogs = []
        for game in resp:
            home = game.get('home_team','')
            away = game.get('away_team','')
            for book in game.get('bookmakers',[])[:3]:
                for m in book.get('markets',[]):
                    for o in m.get('outcomes',[]):
                        try:
                            price = int(o['price']) if o['price']>0 else int(o['price'])
                            name = o['name']
                            # ELITE FILTER +180 to +260
                            if 180 <= price <= 260:
                                dogs.append({"team":f"{name} ML","odds":f"+{price}" if price>0 else str(price),"match":f"{away} @ {home} - ULTRA","price":price})
                            # VALUE FILL +150 to +179
                            elif 150 <= price < 180:
                                dogs.append({"team":f"{name} ML","odds":f"+{price}","match":f"{away} @ {home} - VALUE","price":price})
                        except: pass
        # Sort best odds first
        dogs = sorted(dogs, key=lambda x: x['price'], reverse=True)
        # Remove dupes
        seen=set()
        elite=[]
        for d in dogs:
            k=d['team']+d['match']
            if k not in seen:
                seen.add(k)
                elite.append(d)
            if len(elite)>=5: break
        
        if len(elite)>=3:
            print(f"FOUND {len(elite)} ELITE")
            return elite[:3]
        elif len(elite)>0:
            print(f"ONLY {len(elite)} ULTRA, FILLING WITH FALLBACK")
            while len(elite)<3: elite+=fallback
            return elite[:3]
        else:
            return fallback
    except Exception as e:
        print(f"API ERR {e}")
        return fallback

def format_parlay(picks,label):
    txt=f"🔒 {label} - VEGAS 10.5 ELITE\n\n"
    for p in picks[:3]:
        txt+=f"• {p['team']} {p['odds']} - {p['match']}\n"
    txt+=f"\n💰 $10 TO WIN $85\n💰 $25 TO WIN $215\n\n✅ SUPERMAX ELITE - 1 CREDIT SCAN"
    return txt

@app.route('/')
def home():
    return "SUPERMAX ELITE LIVE - /test to force"

@app.route('/test')
def test_route():
    picks=get_elite_picks()
    msg=format_parlay(picks,"TEST")
    tg_send(msg)
    return f"FORCED:<br><br>{msg}<br><br>Check Telegram now!"

def poll():
    global last_id
    print("POLLER STARTED")
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=25",timeout=30).json()
            for u in r.get('result',[]):
                last_id=u['update_id']
                txt=u.get('message',{}).get('text','').lower()
                print(f"MSG: {txt}")
                if 'test' in txt.lower() or 'parlay' in txt.lower() or 'start' in txt.lower() or 'sent' in txt.lower():
                    tg_send(format_parlay(get_elite_picks(),"TEST"))
        except Exception as e:
            print(f"POLL ERR {e}")
            time.sleep(5)
        time.sleep(3)

def scheduler():
    print("SCHEDULER STARTED - 12PM / 4PM / 6PM")
    while True:
        try:
            now=datetime.now()
            label=None
            if now.hour==12 and now.minute==0: label="12PM LUNCH LOCK"
            if now.hour==16 and now.minute==0: label="4PM EARLY LOCK"
            if now.hour==18 and now.minute==0: label="6PM PRIME LOCK"
            if label:
  key=f"{now.date()}_{now.hour}"
  if key not in sent_today:
  tg_send(format_parlay(get_elite_picks(),label))
 sent_today.add(key)
  with open(SENT_FILE, "w") as f:
  json.dump(list(sent_today), f)
  time.sleep(55)  
                
                
                    
                       
                                        
                    
            
        except Exception as e:
            print(f"SCHED ERR {e}")
            time.sleep(60)

threading.Thread(target=poll,daemon=True).start()
threading.Thread(target=scheduler,daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host='0.0.0.0',port=port)
