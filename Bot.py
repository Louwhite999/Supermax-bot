import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX VEGAS 9.0+ INSTANT FIX LIVE"

sent_bets = set()
last_update_id = 0
daily_sent = 0
last_reset_day = datetime.now().day
bankroll = 1000
wins = 0
losses = 0
SHARP_BOOKS = ["pinnacle", "bookmaker", "betonlineag", "circa"]

def send_msg(text):
    if not TOKEN or not CHAT:
        return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
        r = requests.post(url, data=data, timeout=15)
        print(f"SENT {r.status_code} - {text[:30]}")
        return r.status_code == 200
    except Exception as e:
        print(f"send error {e}")
        return False

def handle_wl(text):
    global bankroll, wins, losses
    txt = text.lower().strip()
    print(f"Got message: {txt}")
    if txt == "w" or txt.startswith("w "):
        wins += 1
        bankroll += 100
        return f"✅ *WIN LOGGED*\nRecord: {wins}-{losses} | Bankroll: ${bankroll}"
    if txt == "l" or txt.startswith("l "):
        losses += 1
        bankroll -= 100
        return f"❌ *LOSS LOGGED*\nRecord: {wins}-{losses} | Bankroll: ${bankroll}"
    if "status" in txt:
        return f"✅ *VEGAS 9.0+ ONLINE & LISTENING!* | {datetime.now().strftime('%m/%d %I:%M%p')}\nToday: {daily_sent}/8 | Record: {wins}-{losses} | Bank: ${bankroll}\nI hear you! Type test or bankroll"
    if "bankroll" in txt or "record" in txt:
        roi = ((bankroll-1000)/10) if wins+losses>0 else 0
        return f"💰 *BANKROLL*\nNow: ${bankroll} | Record: {wins}-{losses}\nProfit: ${bankroll-1000}"
    if "test" in txt:
        return f"🧪 *VEGAS 9.0+ TEST OK!* ✅\nI HEAR YOU LOUIS!\nScanning NFL, NCAAF, MLB, WNBA\nOnly 9.0+ dogs +130 to +350\nTime: {datetime.now().strftime('%I:%M:%S %p')}"
    if "start" in txt:
        return f"🔥 *SUPERMAX VEGAS 9.0+ LIVE*\nI'm listening!\nType status / test / bankroll / W / L"
    return None

def american_to_prob(a):
    try:
        a=int(a)
        return 100/(a+100) if a>0 else abs(a)/(abs(a)+100)
    except:
        return 0.5

def get_lines(bookmakers, team):
    lines = []
    for b in bookmakers:
        try:
            for m in b.get('markets',[]):
                if m.get('key')!='h2h': continue
                for o in m.get('outcomes',[]):
                    if o.get('name')==team:
                        lines.append({"book": b.get('title',''), "key": b.get('key',''), "price": int(o.get('price',0))})
        except: continue
    return lines

def vegas_score(team, lines, is_home, sport):
    if not lines: return 0, {}
    best = max(lines, key=lambda x: x['price'])
    avg_price = sum(l['price'] for l in lines)/len(lines)
    best_price = best['price']
    if best_price < 130 or best_price > 350: return 0, {}
    score = 5.0
    reasons = []
    edge_prob = american_to_prob(avg_price) - american_to_prob(best_price)
    if edge_prob > 0.02:
        add = min(2.0, edge_prob*50)
        score += add
        reasons.append(f"Edge {edge_prob*100:.1f}% +{add:.1f}")
    sharp_on_dog = any(l['key'] in SHARP_BOOKS and l['price']>=130 for l in lines)
    if sharp_on_dog:
        score += 1.5
        reasons.append("Sharp book +1.5")
    if is_home and best_price>=140:
        score += 1.0
        reasons.append("Home dog +1.0")
    if best['key'] in SHARP_BOOKS:
        score += 1.0
        reasons.append(f"Best @ {best['book']} +1.0")
    if "football" in sport:
        score += 0.5
        reasons.append("NFL +0.5")
    score = min(10, score)
    return score, {"best": best, "avg": avg_price, "reasons": reasons, "edge": edge_prob}

def telegram_loop():
    global last_update_id
    print("TELEGRAM LISTENER STARTED - INSTANT REPLY")
    while True:
        try:
            if TOKEN:
                try:
                    url=f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=20"
                    ru=requests.get(url, timeout=25).json()
                    if ru.get("ok"):
                        for upd in ru.get("result",[]):
                            last_update_id=upd.get("update_id",last_update_id)
                            txt=upd.get("message",{}).get("text","")
                            print(f"Incoming: {txt}")
                            if txt:
                                res=handle_wl(txt)
                                if res:
                                    send_msg(res)
                except Exception as e:
                    print(f"tg error {e}")
        except Exception as e:
            print(f"telegram loop {e}")
        time.sleep(1)

def odds_loop():
    global daily_sent, last_reset_day
    print("VEGAS ODDS LOOP STARTED")
    time.sleep(5)
    send_msg("🚀 *SUPERMAX VEGAS 9.0+ ONLINE - INSTANT FIX!*\nI now reply in 1 second!\nType test / status / bankroll\nScanning NFL/NCAAF/MLB/WNBA for 9.0+ dogs")
    while True:
        try:
            if datetime.now().day != last_reset_day:
                daily_sent=0
                last_reset_day=datetime.now().day
                sent_bets.clear()
            if not ODDS:
                time.sleep(60)
                continue
            if daily_sent>=8:
                time.sleep(120)
                continue
            for sport in ["americanfootball_nfl","americanfootball_ncaaf","baseball_mlb","basketball_wnba"]:
                try:
                    url=f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS}&regions=us&markets=h2h&oddsFormat=american"
                    r=requests.get(url, timeout=20)
                    if r.status_code!=200: continue
                    data=r.json()
                    if not isinstance(data,list): continue
                    for g in data:
                        try:
                            home=g.get('home_team','')
                            away=g.get('away_team','')
                            gid=g.get('id','')
                            commence=g.get('commence_time','')
                            game_key=f"{sport}_{away}_{home}_{gid}"
                            if game_key in sent_bets: continue
                            bms=g.get('bookmakers',[])
                            if len(bms)<3: continue
                            for team in [away, home]:
                                is_home = (team==home)
                                lines=get_lines(bms, team)
                                if len(lines)<3: continue
                                score, info = vegas_score(team, lines, is_home, sport)
                                if score >= 9.0:
                                    if game_key in sent_bets: continue
                                    best=info['best']
                                    avg=info['avg']
                                    reasons=info['reasons']
                                    edge=info['edge']
                                    emoji="🏈" if "football" in sport else "⚾️" if "baseball" in sport else "🏀"
                                    league="NFL" if sport=="americanfootball_nfl" else "NCAAF" if "ncaaf" in sport else "MLB" if "mlb" in sport else "WNBA"
                                    msg=(f"{emoji} *{league} VEGAS 9.0+ PICK*\n*{away} @ {home}*\n🔥 *SCORE: {score:.1f}/10* 🔥\nPick: *{team} ML* +{best['price']} @ {best['book']}\nAvg: {avg:.0f} | Edge: {edge*100:.1f}%\nGame: {commence[:16]}\n\n🧠 *Why 9.0+*:\n" + "\n".join([f"• {r}" for r in reasons]) + f"\n\n💰 *1.5u MAX* — Vegas Lock\nReply W / L")
                                    if send_msg(msg):
                                        sent_bets.add(game_key)
                                        daily_sent+=1
                                        print(f"VEGAS 9.0 SENT {team} {best['price']} score {score}")
                                        time.sleep(3)
                                        break
                        except Exception as e:
                            print(f"game inner {e}")
                            continue
                except Exception as e:
                    print(f"sport {sport} {e}")
                    continue
        except Exception as e:
            print(f"MAIN {e}")
        time.sleep(60)

threading.Thread(target=telegram_loop, daemon=True).start()
threading.Thread(target=odds_loop, daemon=True).start()

if __name__=="__main__":
    port=int(os.getenv("PORT",10000))
    app.run(host="0.0.0.0", port=port)
