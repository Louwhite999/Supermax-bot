import os, requests, time, threading, json, csv
from datetime import datetime, timedelta
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "LOUIS SUPERMAX CLEAN - LIVE"

sent_bets = set()
last_warning = 0

ADJ_FILE = "supermax_learn.json"
RES_FILE = "supermax_results.csv"

# ONLY REAL SPORTS - no KBO, no KSA
ALLOWED_SPORTS = [
    "baseball_mlb",
    "americanfootball_nfl",
    "basketball_nba",
    "americanfootball_ncaaf",
    "basketball_ncaab"
]

def get_adj(t):
    if not os.path.exists(ADJ_FILE): return 0
    try: d=json.load(open(ADJ_FILE))
    except: return 0
    now=datetime.now()
    changed=False
    for k in list(d.keys()):
        try:
            if datetime.fromisoformat(d[k]['until']) < now:
                del d[k]; changed=True
        except: pass
    if changed:
        try: json.dump(d, open(ADJ_FILE,'w'))
        except: pass
    return d.get(t,{}).get('adj',0)

def learn(game,t,base,won):
    ch=0.1 if won else -0.2
    days=3 if won else 7
    d={}
    if os.path.exists(ADJ_FILE):
        try: d=json.load(open(ADJ_FILE))
        except: d={}
    cur=d.get(t,{}).get('adj',0)+ch
    d[t]={"adj":cur,"until":(datetime.now()+timedelta(days=days)).isoformat()}
    json.dump(d, open(ADJ_FILE,'w'))
    with open(RES_FILE,'a',newline='') as f:
        csv.writer(f).writerow([datetime.now().date(),game,t,base,"W" if won else "L",cur])
    return cur

def log_pending(game,t,base,adj):
    with open(RES_FILE,'a',newline='') as f:
        csv.writer(f).writerow([datetime.now().date(),game,t,base,"PENDING",adj])

def handle_wl(text):
    if text.upper() not in ["W","L"]: return None
    if not os.path.exists(RES_FILE): return None
    try:
        rows=list(csv.reader(open(RES_FILE)))
        for r in reversed(rows):
            if len(r)>=5 and "PENDING" in r:
                game,t,base=r[1],r[2],float(r[3])
                won=text.upper()=="W"
                new_adj=learn(game,t,base,won)
                return f"Logged {game} as {text.upper()}. {t} now {new_adj:+.1f}"
    except: pass
    return None

def send_msg(text):
    if not TOKEN or not CHAT: return
    try:
        cid=CHAT
        try: cid=int(str(cid))
        except: pass
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", json={"chat_id":cid,"text":text}, timeout=10)
    except Exception as e:
        print(f"Send error: {e}")

def calc_score(game_data):
    # ===== PUT YOUR REAL 9.0 FORMULA HERE =====
    # For now: simple filter - if you had logic before, paste it here
    # This is where your edge calc goes
    # Example: return 9.2 if you like the game else 8.0
    # Keeping 9.1 for now so it still fires - CHANGE THIS TO YOUR FORMULA
    return 9.1

def bot_loop():
    global last_warning
    print("Bot started CLEAN")
    last_update_id=0
    while True:
        try:
            # Handle W/L
            try:
                if TOKEN:
                    url=f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=5"
                    ru=requests.get(url,timeout=10)
                    d=ru.json()
                    if d.get("ok"):
                        for upd in d.get("result",[]):
                            last_update_id=upd["update_id"]
                            msg=upd.get("message",{}).get("text","")
                            if msg:
                                res=handle_wl(msg.strip())
                                if res: send_msg(res)
            except Exception as e:
                print(f"update err {e}")

            if not ODDS:
                if time.time()-last_warning>3600:
                    send_msg("LOUIS - ODDS_API_KEY missing!")
                    last_warning=time.time()
            else:
                for sport in ALLOWED_SPORTS:
                    try:
                        url=f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS}&regions=us&markets=h2h,spreads&oddsFormat=american"
                        r=requests.get(url,timeout=20)
                        data=r.json()
                        if not isinstance(data,list):
                            continue
                        for g in data[:10]:
                            home=g.get("home_team"); away=g.get("away_team")
                            game_id=f"{away}@{home} ({sport})"
                            if game_id in sent_bets:
                                continue
                            base_score=calc_score(g)
                            # Only send real 9.0s
                            if base_score < 9.0:
                                continue
                            game_type="road_dog" # change to your fav/dog/home logic
                            adj=get_adj(game_type)
                            final=base_score+adj
                            if final>=9.0:
                                book=g.get("bookmakers",[])[0] if g.get("bookmakers") else {}
                                market=book.get("markets",[])[0] if book.get("markets") else {}
                                outcome=market.get("outcomes",[])[0] if market.get("outcomes") else {}
                                send_msg(f"SUPERMAX {final:.1f} (base {base_score:.1f} {adj:+.1f}) {game_id} {outcome.get('name','')}")
                                sent_bets.add(game_id)
                                log_pending(game_id,game_type,base_score,adj)
                    except Exception as e:
                        print(f"sport {sport} err {e}")
                        continue
        except Exception as e:
            print(f"Loop Error: {e}")
        time.sleep(180)

threading.Thread(target=bot_loop,daemon=True).start()

if __name__=="__main__":
    port=int(os.getenv("PORT",1000))
    app.run(host="0.0.0.0",port=port)
