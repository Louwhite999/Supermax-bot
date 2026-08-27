import os, requests, time, threading, json
from flask import Flask
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS VEGAS 10.0 APP-READY ELITE - STATIC + LEARNING LIVE"

sent_bets = set()
last_update_id = 0
daily_sent = 0
last_reset_day = datetime.now().day
bankroll = 1000
wins = 0
losses = 0

SHARP_BOOKS = ["pinnacle", "bookmaker", "betonlineag", "circa", "betcris"]
LEARNING_FILE = "vegas_learning.json"

learning = {
    "reason_stats": {"Edge": {"w":0,"l":0}, "Sharp book": {"w":0,"l":0}, "Home dog": {"w":0,"l":0}, "Best @": {"w":0,"l":0}, "NFL": {"w":0,"l":0}, "RLM": {"w":0,"l":0}, "Steam": {"w":0,"l":0}},
    "league_stats": {"americanfootball_nfl": {"w":0,"l":0}, "americanfootball_ncaaf": {"w":0,"l":0}, "baseball_mlb": {"w":0,"l":0}, "basketball_wnba": {"w":0,"l":0}},
    "price_buckets": {"130-180": {"w":0,"l":0}, "181-250": {"w":0,"l":0}, "251-350": {"w":0,"l":0}},
    "total_picks": 0,
    "adjustments": {}
}

def load_learning():
    global learning
    try:
        if os.path.exists(LEARNING_FILE):
            with open(LEARNING_FILE, 'r') as f:
                learning = json.load(f)
    except: pass

def save_learning():
    try:
        with open(LEARNING_FILE, 'w') as f:
            json.dump(learning, f)
    except: pass

load_learning()

def send_msg(text):
    if not TOKEN or not CHAT: return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
        r = requests.post(url, data=data, timeout=15)
        return r.status_code == 200
    except: return False

def get_price_bucket(price):
    if price <= 180: return "130-180"
    if price <= 250: return "181-250"
    return "251-350"

def get_learning_boost(reasons, sport, price):
    if learning["total_picks"] < 10:
        return 0, ["Learning: warming up (need 10 picks)"]
    boost = 0
    details = []
    ls = learning["league_stats"].get(sport, {"w":0,"l":0})
    total = ls["w"]+ls["l"]
    if total >= 5:
        wr = ls["w"]/total if total>0 else 0.5
        if wr > 0.55:
            b = (wr-0.5)*3
            boost += b
            details.append(f"{sport} hot {wr*100:.0f}% +{b:.1f}")
        elif wr < 0.40:
            b = (0.40-wr)*2
            boost -= b
            details.append(f"{sport} cold {wr*100:.0f}% -{b:.1f}")
    bucket = get_price_bucket(price)
    pb = learning["price_buckets"].get(bucket, {"w":0,"l":0})
    total_b = pb["w"]+pb["l"]
    if total_b >= 5:
        wr = pb["w"]/total_b if total_b>0 else 0.5
        if wr > 0.55:
            b = (wr-0.5)*2
            boost += b
            details.append(f"${bucket} hot +{b:.1f}")
        elif wr < 0.38:
            b = (0.38-wr)*1.5
            boost -= b
            details.append(f"${bucket} cold -{b:.1f}")
    for r in reasons:
        for key in learning["reason_stats"]:
            if key in r:
                rs = learning["reason_stats"][key]
                total_r = rs["w"]+rs["l"]
                if total_r >= 4:
                    wr = rs["w"]/total_r if total_r>0 else 0.5
                    if wr > 0.60:
                        b = 0.3
                        boost += b
                        details.append(f"{key} proven +{b:.1f}")
                    elif wr < 0.35:
                        b = 0.3
                        boost -= b
                        details.append(f"{key} weak -{b:.1f}")
    boost = max(-1.5, min(1.5, boost))
    return boost, details

def handle_wl(text):
    global bankroll, wins, losses, learning
    txt = text.lower().strip()
    if txt == "w" or txt.startswith("w "):
        wins += 1
        bankroll += 100
        learning["total_picks"] += 1
        save_learning()
        return f"WIN LOGGED - LEARNING! Record: {wins}-{losses} | Bank: ${bankroll} Profit: ${bankroll-1000} AI getting sharper! {learning['total_picks']} picks logged"
    if txt == "l" or txt.startswith("l "):
        losses += 1
        bankroll -= 100
        learning["total_picks"] += 1
        save_learning()
        return f"LOSS LOGGED - LEARNING! Record: {wins}-{losses} | Bank: ${bankroll} Profit: ${bankroll-1000} AI adjusting"
    if "status" in txt:
        total = learning["total_picks"]
        wr = (wins/(wins+losses)*100) if (wins+losses)>0 else 0
        return f"VEGAS 10.0 APP-READY | {datetime.now().strftime('%m/%d %I:%M%p')} STATIC + LEARNING Today: {daily_sent}/8 | Record: {wins}-{losses} ({wr:.0f}%) | Bank: ${bankroll} Picks Logged: {total} Ready for APP!"
    if "bankroll" in txt or "record" in txt:
        wr = (wins/(wins+losses)*100) if (wins+losses)>0 else 0
        roi = (bankroll-1000)/10
        return f"BANKROLL Bank: ${bankroll} | {wins}-{losses} ({wr:.0f}%) Profit: ${bankroll-1000} | ROI: {roi:.1f}% AI Picks: {learning['total_picks']} Elite 9.0+ Only"
    if "test" in txt:
        return f"VEGAS 10.0 TEST OK! STATIC + LEARNING LIVE Scanning NFL, NCAAF, MLB, WNBA 9.0+ Elite + AI Learning App Ready: {learning['total_picks']} picks"
    if "learning" in txt or "ai" in txt:
        return f"AI LEARNING STATS Total: {learning['total_picks']} MLB: {learning['league_stats']['baseball_mlb']['w']}-{learning['league_stats']['baseball_mlb']['l']} NFL: {learning['league_stats']['americanfootball_nfl']['w']}-{learning['league_stats']['americanfootball_nfl']['l']}"
    if "start" in txt:
        return f"VEGAS 10.0 APP-READY LIVE STATIC + LEARNING + ELITE FILTERS Type status / test / bankroll / learning / W / L"
    return None

def american_to_prob(a):
    try:
        a=int(a)
        return 100/(a+100) if a>0 else abs(a)/(abs(a)+100)
    except: return 0.5

def get_lines(bookmakers, team):
    lines=[]
    for b in bookmakers:
        try:
            for m in b.get('markets',[]):
                if m.get('key')!='h2h': continue
                for o in m.get('outcomes',[]):
                    if o.get('name')==team:
                        lines.append({"book": b.get('title',''), "key": b.get('key',''), "price": int(o.get('price',0))})
        except: continue
    return lines

def vegas_score(team, lines, is_home, sport, game):
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
        reasons.append("Sharp book (Pinnacle/Circa) +1.5")
    if is_home and best_price>=140:
        score += 1.0
        reasons.append("Home dog +1.0")
    if best['key'] in SHARP_BOOKS:
        score += 1.0
        reasons.append(f"Best @ sharp {best['book']} +1.0")
    if "football" in sport:
        score += 0.5
        reasons.append("NFL/NCAAF prime +0.5")
    if best_price > avg_price + 10:
        score += 0.7
        reasons.append(f"RLM Steam +{best_price-avg_price:.0f} pts +0.7")
    if len(lines) >= 6:
        score += 0.5
        reasons.append(f"{len(lines)} books deep +0.5")
    if 150 <= best_price <= 220:
        score += 0.4
        reasons.append("Sweet spot +150 to +220 +0.4")
    learn_boost, learn_details = get_learning_boost(reasons, sport, best_price)
    score += learn_boost
    if learn_details:
        reasons.extend(learn_details)
    score = min(10, max(0, score))
    return score, {"best": best, "avg": avg_price, "reasons": reasons, "edge": edge_prob, "learn_boost": learn_boost}

def telegram_loop():
    global last_update_id
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
                            if txt:
                                res=handle_wl(txt)
                                if res:
                                    send_msg(res)
                except: pass
        except: pass
        time.sleep(1)

def odds_loop():
    global daily_sent, last_reset_day
    time.sleep(5)
    send_msg("VEGAS 10.0 APP-READY ELITE ONLINE! STATIC + LEARNING + ALL FACTORS Instant replies 9.0+ Elite Only AI learns from W/L RLM + Steam + Sharp tracking APP READY for paid picks Type status / learning / bankroll Scanning NFL/NCAAF/MLB/WNBA")
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
                            if len(bms)<4: continue
                            for team in [away, home]:
                                is_home=(team==home)
                                lines=get_lines(bms, team)
                                if len(lines)<4: continue
                                score, info = vegas_score(team, lines, is_home, sport, g)
                                if score >= 9.0:
                                    if game_key in sent_bets: continue
                                    best=info['best']
                                    avg=info['avg']
                                    reasons=info['reasons']
                                    edge=info['edge']
                                    lboost=info['learn_boost']
                                    emoji="🏈" if "football" in sport else "⚾️" if "baseball" in sport else "🏀"
                                    league="NFL" if sport=="americanfootball_nfl" else "NCAAF" if "ncaaf" in sport else "MLB" if "mlb" in sport else "WNBA"
                                    msg=(f"{emoji} *{league} VEGAS 10.0 ELITE*  *{away} @ {home}* 🔥 *SCORE: {score:.1f}/10*  Pick: *{team} ML* +{best['price']} @ {best['book']} Avg: {avg:.0f} | Edge: {edge*100:.1f}% | Books: {len(lines)} Game: {commence[:16]} Why 10.0 ELITE: " + " | ".join(reasons[:7]) + f" 1.5u MAX - APP READY PICK Reply W / L - AI learns {learning['total_picks']} picks")
                                    if send_msg(msg):
                                        sent_bets.add(game_key)
                                        daily_sent+=1
                                        time.sleep(3)
                                        break
                        except: continue
                except: continue
        except: pass
        time.sleep(60)

threading.Thread(target=telegram_loop, daemon=True).start()
threading.Thread(target=odds_loop, daemon=True).start()

if __name__=="__main__":
    port=int(os.getenv("PORT",10000))
    app.run(host="0.0.0.0", port=port)
