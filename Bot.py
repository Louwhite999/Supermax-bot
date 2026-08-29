# LOUIS SUPERMAX - VEGAS 10.5 ULTRA - 12pm + 4PM + 6PM CT Locks
import os, requests, time, threading
from flask import Flask
from datetime import datetime, timezone

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX VEGAS 10.5 ULTRA LIVE - 4PM + 6PM LOCKS + $10"

sent_bets = set()
daily_sent = 0
last_update_id = 0
todays_ultra_pool = []
last_reset_day = datetime.now(timezone.utc).day
parlay_12pm_sent= False
parlay_4pm_sent = False
parlay_6pm_sent = False

record = {"wins": 0, "losses": 0}

def send_msg(text):
    if not TOKEN or not CHAT:
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": CHAT, "text": text}, timeout=10)
    except Exception as e:
        print(f"send error {e}")

def calc_parlay_odds(list_odds):
    dec = 1.0
    for o in list_odds:
        try:
            v = int(str(o).replace("+",""))
            dec *= (v/100+1) if v>0 else (100/abs(v)+1)
        except: continue
    return int((dec-1)*100)

def get_boost_label(h,a):
    tags=["Steam Move","Travel Spot","Div Revenge","Sweetheart","Sharp Pin/Circa"]
    return tags[hash(h+a)%len(tags)]

def format_single(p):
    return f"""🔥 VEGAS 10.5 ULTRA DOG - {p['rating']:.1f}
{p['team']} {p['odds']} ({p['market']})
Sport: {p['sport']}
Boosts: {p['boost']}
Game: {p['away']} @ {p['home']}
Sharp: Pinnacle/Circa/Bookmaker
Time: {p['time']}"""

def build_parlay_text(title):
    if len(todays_ultra_pool) < 3:
        return None
    seen=set()
    top3=[]
    for p in sorted(todays_ultra_pool, key=lambda x: x['rating'], reverse=True):
        gk=p['game_key']
        if gk in seen: continue
        top3.append(p); seen.add(gk)
        if len(top3)==3: break
    if len(top3)<3: return None
    avg=sum(x['rating'] for x in top3)/3
    comb=calc_parlay_odds([x['odds'] for x in top3])
    win=10*comb/100
    return f"""{title}

🚀 ULTRA PARLAY 3-LEG - AVG {avg:.1f}
LEG 1: {top3[0]['team']} {top3[0]['odds']} ({top3[0]['rating']:.1f}) - {top3[0]['boost']}
Game: {top3[0]['away']} @ {top3[0]['home']}
LEG 2: {top3[1]['team']} {top3[1]['odds']} ({top3[1]['rating']:.1f}) - {top3[1]['boost']}
Game: {top3[1]['away']} @ {top3[1]['home']}
LEG 3: {top3[2]['team']} {top3[2]['odds']} ({top3[2]['rating']:.1f}) - {top3[2]['boost']}
Game: {top3[2]['away']} @ {top3[2]['home']}

COMBINED: +{comb}
FUN STAKE: $10 to win ${win:.2f}

Free boosts: Steam+Travel+Div+Sweet
Sharp: Pinnacle/Circa/Bookmaker"""

def handle_wl(txt):
    global parlay_4pm_sent, parlay_6pm_sent
    low=txt.lower().strip()
    if low.startswith("/test"):
        if "parlay" in low:
            if len(todays_ultra_pool)<3:
                return f"🧪 TEST PARLAY - Only {len(todays_ultra_pool)} ULTRA dogs, need 3. 4PM & 6PM locks silent if not enough."
            return build_parlay_text("🧪 VEGAS 10.5 ULTRA PARLAY TEST")
        else:
            if not todays_ultra_pool:
                return "🧪 TEST - No ULTRA dogs yet. Scanner 60s. 4PM + 6PM locks silent."
            best=sorted(todays_ultra_pool, key=lambda x: x['rating'], reverse=True)[0]
            return format_single(best)+f"\n\nPool: {len(todays_ultra_pool)} | 4PM:{'SENT' if parlay_4pm_sent else 'PENDING'} 6PM:{'SENT' if parlay_6pm_sent else 'PENDING'}"
    if "/parlay" in low:
        return handle_wl("/testparlay")
    if "/record" in low or low=="/wl":
        return f"📊 {record['wins']}-{record['losses']} Pool:{len(todays_ultra_pool)} 4PM:{'Sent' if parlay_4pm_sent else 'Pending'} 6PM:{'Sent' if parlay_6pm_sent else 'Pending'}"
    if low.startswith("/w "):
        record["wins"]+=1
        return f"✅ Win {record['wins']}-{record['losses']}"
    if low.startswith("/l "):
        record["losses"]+=1
        return f"❌ Loss {record['wins']}-{record['losses']}"
    if "/reset" in low:
        todays_ultra_pool.clear(); sent_bets.clear()
        parlay_4pm_sent=False; parlay_6pm_sent=False
        return "♻️ Reset - pools + 4PM + 6PM flags cleared"
    return None

def is_window(hours):
    now=datetime.now(timezone.utc)
    return now.hour in hours and 0 <= now.minute <= 15

def scanner_loop():
    global daily_sent, last_reset_day, sent_bets, todays_ultra_pool, last_update_id, parlay_4pm_sent, parlay_6pm_sent
    print("SUPERMAX 4PM+6PM started")
    while True:
        try:
            try:
                if TOKEN:
                    url=f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=20"
                    r=requests.get(url, timeout=25)
                    if r.status_code==200:
                        for upd in r.json().get("result",[]):
                            last_update_id=upd.get("update_id", last_update_id)
                            txt=upd.get("message",{}).get("text","")
                            if txt:
                                res=handle_wl(txt)
                                if res: send_msg(res)
            except Exception as e:
                print(f"tg {e}")

            cur_day=datetime.now(timezone.utc).day
            if cur_day!=last_reset_day:
                daily_sent=0; sent_bets.clear(); todays_ultra_pool.clear()
                parlay_4pm_sent=False; parlay_6pm_sent=False
                last_reset_day=cur_day

            if not parlay_4pm_sent and is_window([21,22]):
                if len(todays_ultra_pool)>=3:
                    txt=build_parlay_text("🔒 VEGAS 10.5 ULTRA 4PM CT LOCK PARLAY")
                    if txt:
                        send_msg(txt); parlay_4pm_sent=True

            if not parlay_6pm_sent and is_window([23,0]):
                if len(todays_ultra_pool)>=3:
                    if not parlay_4pm_sent or len(todays_ultra_pool)>=4:
                        txt=build_parlay_text("🔒🔒 VEGAS 10.5 ULTRA 6PM CT FINAL LOCK PARLAY")
                        if txt:
                            send_msg(txt); parlay_6pm_sent=True
                    else:
                        parlay_6pm_sent=True

            if not ODDS:
                time.sleep(60); continue
            if daily_sent>=8:
                time.sleep(120); continue

            for sport in ["americanfootball_nfl","americanfootball_ncaaf","baseball_mlb","basketball_wnba"]:
                try:
                    url=f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS}&regions=us&markets=h2h&oddsFormat=american"
                    r=requests.get(url, timeout=20)
                    if r.status_code!=200: continue
                    data=r.json()
                    if not isinstance(data,list): continue
                    for g in data:
                        try:
                            home=g.get('home_team',''); away=g.get('away_team','')
                            gid=g.get('id',''); commence=g.get('commence_time','')
                            game_key=f"{sport}_{away}_{home}_{gid}"
                            if game_key in sent_bets: continue
                            bms=g.get('bookmakers',[])
                            if len(bms)<3: continue
                            best=None; best_val=0
                            for bm in bms:
                                for mk in bm.get('markets',[]):
                                    for out in mk.get('outcomes',[]):
                                        price=out.get('price',0)
                                        if 130 <= price <= 350 and price>best_val:
                                            best_val=price
                                            best={"team":out.get('name',''),"odds":f"+{price}","price":price}
                            if not best: continue
                            rating=9.5 + (best_val%100)/100.0
                            if best['price']>=150:
                                rating=10.0 + (best['price']-130)/300.0
                            if rating<10.0: continue
                            pick={"team":best['team'],"odds":best['odds'],"price":best['price'],"rating":round(rating,1),"sport":sport,"home":home,"away":away,"game_key":game_key,"market":"h2h","boost":get_boost_label(home,away),"time":commence[:16] if commence else "TBD"}
                            if game_key not in [p['game_key'] for p in todays_ultra_pool]:
                                todays_ultra_pool.append(pick)
                            send_msg(format_single(pick))
                            sent_bets.add(game_key); daily_sent+=1
                        except: continue
                except: continue
            time.sleep(60)
        except Exception as e:
            print(f"main {e}"); time.sleep(60)

threading.Thread(target=scanner_loop, daemon=True).start()

if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
