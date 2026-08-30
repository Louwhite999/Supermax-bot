# LOUIS EMERGENCY - 0 CREDITS - ALWAYS GIVES PARLAY
import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.environ.get("TOKEN","") or os.environ.get("TELEGRAM_TOKEN","")
CHAT = os.environ.get("CHAT","") or os.environ.get("TELEGRAM_CHAT_ID","") or os.environ.get("CHAT_ID","")

app = Flask(__name__)
@app.route('/')
def home(): return "LOUIS EMERGENCY LIVE"

last_id=0
sent_today=set()

def tg_send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":CHAT,"text":t}, timeout=15)
    except: pass

def get_picks():
    return [{"team":"Brewers ML","odds":"+185","match":"Cubs @ Brewers"},{"team":"Rays ML","odds":"+210","match":"Yankees @ Rays"},{"team":"D-Backs ML","odds":"+165","match":"Dodgers @ D-Backs"}]

def format_it(picks,label):
    txt=f"🔒 {label} VEGAS 10.5\n\n"
    for p in picks: txt+=f"• {p['team']} {p['odds']} - {p['match']}\n"
    txt+=f"\n$10 TO WIN $87\n$25 TO WIN $217\n\n✅ EMERGENCY MODE - 0 CREDITS USED"
    return txt

def poll():
    global last_id
    while True:
        try:
            r=requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_id+1}&timeout=25",timeout=30).json()
            for u in r.get('result',[]):
                last_id=u['update_id']
                if '/test' in u.get('message',{}).get('text','').lower():
                    tg_send(format_it(get_picks(),"TEST"))
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
                    tg_send(format_it(get_picks(),label))
                    sent_today.add(key)
            time.sleep(50)
        except: time.sleep(60)

threading.Thread(target=poll,daemon=True).start()
threading.Thread(target=scheduler,daemon=True).start()

if __name__=="__main__":
    app.run(host='0.0.0.0',port=10000)
