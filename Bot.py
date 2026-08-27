import os, requests, time, threading
from flask import Flask
from datetime import datetime

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)

@app.route('/')
def home():
    return "LOUIS SUPERMAX FINAL FORM LIVE - READY FOR WEEKEND"

sent_bets = set()
last_update_id = 0

def send_msg(text):
    if not TOKEN or not CHAT:
        print(f"NO TOKEN/CHAT: {text[:100]}")
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT, "text": text, "parse_mode": "Markdown"}
        r = requests.post(url, data=data, timeout=15)
        print(f"TELEGRAM SENT: {r.status_code}")
    except Exception as e:
        print(f"send error {e}")

def handle_wl(text):
    txt = text.lower()
    if "w" in txt and len(txt) < 5:
        return "✅ Win logged! Nice hit!"
    if "l" in txt and len(txt) < 5:
        return "❌ Loss logged. We bounce back!"
    if "/start" in txt:
        return "🔥 SUPERMAX BOT LIVE - Ready for weekend bets!"
    if "/status" in txt:
        return f"✅ Bot Online | {datetime.now().strftime('%m/%d %I:%M%p')} | {len(sent_bets)} games tracked"
    return None

def poll_loop():
    global last_update_id
    print("BOT LOOP STARTED")
    try:
        send_msg("🚀 *SUPERMAX BOT ONLINE*\nReady for this weekend! Use /status to check")
    except:
        pass

    while True:
        try:
            if TOKEN:
                try:
                    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=10"
                    ru = requests.get(url, timeout=20).json()
                    if ru.get("ok"):
                        for upd in ru.get("result", []):
                            last_update_id = upd.get("update_id", last_update_id)
                            msg = upd.get("message", {})
                            txt = msg.get("text", "")
                            if txt:
                                res = handle_wl(txt)
                                if res:
                                    send_msg(res)
                except Exception as e:
                    print(f"telegram poll error {e}")

            if not ODDS:
                print("No ODDS_API_KEY, sleeping")
                time.sleep(60)
                continue

            for sport in ["americanfootball_nfl", "baseball_mlb", "basketball_wnba"]:
                try:
                    url = f"https://api.the-odds-api.com/v4/sports/{sport}/odds/?apiKey={ODDS}&regions=us&markets=h2h&oddsFormat=american"
                    r = requests.get(url, timeout=15)
                    data = r.json()
                    if not isinstance(data, list):
                        continue
                    for g in data[:8]:
                        try:
                            home = g.get('home_team','')
                            away = g.get('away_team','')
                            gid = g.get('id','')
                            game_key = f"{away}_{home}_{gid}"
                            if game_key in sent_bets:
                                continue
                            bookmakers = g.get('bookmakers', [])
                            if not bookmakers:
                                continue
                            if len(sent_bets) < 1:
                                print(f"Tracked {game_key}")
                                sent_bets.add(game_key)
                        except:
                            continue
                except:
                    continue

        except Exception as e:
            print(f"MAIN LOOP ERROR {e}")
        time.sleep(60)

threading.Thread(target=poll_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
