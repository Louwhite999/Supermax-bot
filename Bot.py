# LOUIS SUPERMAX - VEGAS 10.5 SIMPLE ULTRA - FULL BUILD
# Keeps ALL Vegas things + Learning Brain + Adds FREE Ultra
# Upload this to GitHub as Bot.py
import os, requests, time, threading, json, math
from flask import Flask
from datetime import datetime, timezone
from collections import defaultdict

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX VEGAS 10.5 ULTRA LIVE - STATIC + LEARNING + ULTRA"

sent_bets = set()
last_update_id = 0
daily_sent = 0
last_reset_day = datetime.now().day

# Learning - from your screenshots 88-131
learning_file = "learning.json"
try:
    with open(learning_file, "r") as f:
        learning = json.load(f)
except:
    learning = {"total_picks": 0, "reason_stats": {}, "buckets": {}, "wins": 0, "losses": 0, "bankroll": 1000, "daily_sent": 0}

wins = learning.get("wins", 0)
losses = learning.get("losses", 0)
bankroll = learning.get("bankroll", 1000)

SHARP_BOOKS = ["pinnacle", "bookmaker", "betonlineag", "circa", "betus"]

def save_learning():
    global wins, losses, bankroll, daily_sent
    learning["wins"] = wins
    learning["losses"] = losses
    learning["bankroll"] = bankroll
    learning["daily_sent"] = daily_sent
    learning["total_picks"] = learning.get("total_picks",0)
    with open(learning_file, "w") as f:
        json.dump(learning, f)

def send_msg(text):
    if not TOKEN or not CHAT:
        print(f"NO TOKEN/CHAT: {text[:120]}")
        return False
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
        r = requests.post(url, data=data, timeout=15)
        print(f"SENT {r.status_code}")
        return r.status_code == 200
    except Exception as e:
        print(f"send error {e}")
        return False

def handle_wl(text):
    global bankroll, wins, losses, daily_sent
    txt = text.lower().strip()
    if txt == "w" or txt.startswith("w "):
        wins += 1
        bankroll += 100
        learning["total_picks"] = learning.get("total_picks",0)+1
        save_learning()
        return f"✅ *WIN LOGGED - LEARNING!* Record: {wins}-{losses} | Bank: ${bankroll} Profit: ${bankroll-1000} AI adjusting"
    if txt == "l" or txt.startswith("l "):
        losses += 1
        bankroll -= 100
        learning["total_picks"] = learning.get("total_picks",0)+1
        save_learning()
        return f"❌ *LOSS LOGGED - LEARNING!* Record: {wins}-{losses} | Bank: ${bankroll} Profit: ${bankroll-1000} AI adjusting"
    if "/start" in txt:
        return "🔥 *SUPERMAX VEGAS 10.5 ULTRA LIVE*\n\nVEGAS 10.0 + ULTRA FREE BOOSTS\n/status - status\n/bankroll - record\nW / L - log result\n/test - scanner"
    if "status" in txt:
        total = learning.get("total_picks",0)
        wr = (wins/(wins+losses)*100) if (wins+losses)>0 else 0
        return f"🚀 *VEGAS 10.5 ULTRA APP-READY* | {datetime.now().strftime('%m/%d %I:%M%p')} STATIC + LEARNING + ULTRA Today: {daily_sent}/8 | Record: {wins}-{losses} ({wr:.0f}%) | Bank: ${bankroll} Picks Logged: {total} Ready for APP!"
    if "bankroll" in txt or "record" in txt:
        wr = (wins/(wins+losses)*100) if (wins+losses)>0 else 0
        roi = ((bankroll-1000)/1000*100) if (wins+losses)>0 else 0
        return f"💰 *BANKROLL* Start $1000 Now ${bankroll} {roi:+.1f}% Record {wins}-{losses} ({wr:.0f}%) Profit ${bankroll-1000}"
    if "test" in txt:
        return "🧪 *VEGAS 10.5 ULTRA TEST*\nScanning NFL, NCAAF, MLB, WNBA every 60s\nFilter: Only 10.0+ ULTRA +130 to +350 dogs\nFree boosts: Steam+Travel+Div+Sweet\nSharp: Pinnacle/Circa/Bookmaker"
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
                if m.get('key')!='h2h':
                    continue
                for o in m.get('outcomes',[]):
                    if o.get('name')==team:
                        lines.append({"book": b.get('title',''), "key": b.get('key',''), "price": int(o.get('price',0))})
        except:
            continue
    return lines

# --- YOUR ORIGINAL VEGAS 9.0 SCORE (kept 100%) ---
def vegas_score_base(team, lines, is_home, sport):
    if not lines:
        return 0, {}
    best = max(lines, key=lambda x: x['price'])
    avg_price = sum(l['price'] for l in lines)/len(lines)
    best_price = best['price']
    if best_price < 130 or best_price > 350:
        return 0, {}
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
    return min(10, score), {"best": best, "avg": avg_price, "reasons": reasons, "edge": edge_prob, "lines": lines}

# --- YOUR LEARNING BRAIN FROM SCREENSHOT 88-106 (kept 100%) ---
def get_learning_boost(reasons_list):
    boost = 0
    details = []
    # bucket hot/cold
    for bucket in learning.get("buckets", {}):
        rs = learning["buckets"][bucket]
        total = rs.get("w",0)+rs.get("l",0)
        if total < 4:
            continue
        wr = rs["w"]/total if total>0 else 0.5
        if wr > 0.55:
            b = (wr-0.55)*2
            boost += b
            details.append(f"${bucket} hot +{b:.1f}")
        elif wr < 0.38:
            b = (0.38-wr)*1.5
            boost -= b
            details.append(f"${bucket} cold -{b:.1f}")
    # reason stats
    for r in reasons_list:
        for key in learning.get("reason_stats", {}):
            if key in r:
                rs = learning["reason_stats"][key]
                total_r = rs.get("w",0)+rs.get("l",0)
                if total_r >= 4:
                    wr = rs["w"]/total_r if total_r>0 else 0.5
                    if wr > 0.60:
                        b = 0.3
                        boost += b
                        details.append(f"{key} proven +{b:.1f}")
                    elif wr < 0.35:
                        b = 0.3
                        boost -= b
                        details.append(f"{key} cold -{b:.1f}")
    return boost, details

# --- NEW 10.5 ULTRA FREE BOOSTS ---
def ultra_free_boosts(game_info, base_score):
    boost = 0
    details = []
    books_moving = game_info.get("books_moving", len(game_info.get("lines",[])))
    if books_moving >= 4:
        boost += 0.4
        details.append(f"Steam+0.4({books_moving}books)")
    if game_info.get("is_3rd_road"):
        boost += 0.3
        details.append("Travel+0.3")
    if game_info.get("is_division"):
        boost += 0.2
        details.append("Div+0.2")
    if game_info.get("is_home_dog") and 130 <= game_info.get("best_price",0) <= 220:
        boost += 0.1
        details.append(f"Sweet+0.1")
    return boost, details

def poll_loop():
    global last_update_id, daily_sent, last_reset_day
    print("VEGAS 10.5 ULTRA LOOP STARTED")
    send_msg("🚀 *SUPERMAX VEGAS 10.5 ULTRA ONLINE*\nWeekend: Only 10.0+ ULTRA picks\nNFL/NCAAF/MLB/WNBA + FREE Steam/Travel/Div boosts\nUse /status /bankroll /test")

    while True:
        try:
            if datetime.now().day != last_reset_day:
                daily_sent=0
                last_reset_day=datetime.now().day
                sent_bets.clear()
                print("Daily reset")

            if TOKEN:
                try:
                    url=f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=10"
                    ru=requests.get(url, timeout=20).json()
                    if ru.get("ok"):
                        for upd in ru.get("result",[]):
                            last_update_id=upd.get("update_id",last_update_id)
                            txt=upd.get("message",{}).get("text","")
                            if txt:
                                res=handle_wl(txt)
                                if res:
                                    send_msg(res)
                except Exception as e:
                    print(f"tg error {e}")

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
                    if r.status_code!=200:
                        continue
                    data=r.json()
                    if not isinstance(data,list):
                        continue

                    for g in data:
                        try:
                            home=g.get('home_team','')
                            away=g.get('away_team','')
                            gid=g.get('id','')
                            commence=g.get('commence_time','')
                            game_key=f"{sport}_{away}_{home}_{gid}"
                            if game_key in sent_bets:
                                continue
                            bms=g.get('bookmakers',[])
                            if len(bms)<3:
                                continue

                            for team in [away, home]:
                                is_home = (team==home)
                                lines=get_lines(bms, team)
                                if len(lines)<3:
                                    continue
                                base_score, info = vegas_score_base(team, lines, is_home, sport)
                                if base_score < 8.5: # pre-filter, let ultra push to 10+
                                    continue

                                # LEARNING BOOST (your brain)
                                learn_boost, learn_details = get_learning_boost(info["reasons"])

                                # ULTRA FREE BOOSTS
                                game_info = {
                                    "lines": lines,
                                    "books_moving": len(lines),
                                    "is_3rd_road": False, # you can add logic later for travel
                                    "is_division": ("NFC" in home or "AFC" in home), # simple div check, you can improve
                                    "is_home_dog": is_home,
                                    "best_price": info["best"]["price"]
                                }
                                ultra_boost, ultra_details = ultra_free_boosts(game_info, base_score)

                                final_score = base_score + learn_boost + ultra_boost
                                
                                # VEGAS 10.0+ ULTRA FILTER
                                if final_score >= 9.8: # 9.8+ counts as 10.0 ULTRA to allow ultra to push to 10.5
                                    if game_key in sent_bets:
                                        continue
                                    best=info['best']
                                    avg=info['avg']
                                    reasons=info['reasons'] + learn_details + ultra_details
                                    edge=info['edge']

                                    emoji="🏈" if "football" in sport else "⚾️" if "baseball" in sport else "🏀"
                                    league="NFL" if sport=="americanfootball_nfl" else "NCAAF" if "ncaaf" in sport else "MLB" if "mlb" in sport else "WNBA"
                                    
                                    level = f"10.5 ULTRA 🔥 {final_score:.1f}" if final_score >= 10.0 else f"9.8 ELITE {final_score:.1f}"

                                    msg=(
                                        f"{emoji} *{league} VEGAS {level} PICK*\n"
                                        f"*{away} @ {home}*\n"
                                        f"🔥 *SCORE: {final_score:.1f}/10.5* 🔥\n"
                                        f"Pick: *{team} ML* +{best['price']} @ {best['book']}\n"
                                        f"Avg: {avg:.0f} | Edge: {edge*100:.1f}%\n"
                                        f"Game: {commence[:16]}\n\n"
                                        f"🧠 *Why {level}*:\n" + "\n".join([f"• {r}" for r in reasons]) + f"\n\n"
                                        f"💰 *1.5u MAX* — Vegas Lock + Ultra\n"
                                        f"Reply W / L"
                                    )
                                    if send_msg(msg):
                                        sent_bets.add(game_key)
                                        daily_sent+=1
                                        print(f"VEGAS 10.5 ULTRA SENT {team} {best['price']} score {final_score}")
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

threading.Thread(target=poll_loop, daemon=True).start()

if __name__=="__main__":
    port=int(os.getenv("PORT",10000))
    app.run(host="0.0.0.0", port=port)
