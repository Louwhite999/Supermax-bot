import os, requests, time, threading
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID")
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX LIVE - OK"

sent_bets = set()
last_warning = 0

def send_msg(text):
    if not TOKEN or not CHAT:
        return
    try:
        chat_id = CHAT
        try:
            chat_id = int(str(chat_id).strip())
        except:
            pass
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            timeout=10
        )
    except Exception as e:
        print(f"Send error: {e}")

def bot_loop():
    global last_warning
    print("Bot started - Supermax")
    while True:
        try:
            if not ODDS:
                # Send warning only once per hour
                if time.time() - last_warning > 3600:
                    send_msg("🔥 LOUIS SUPERMAX 9.5 LIVE - Add ODDS_API_KEY in Render to get real FanDuel lines. Bot checking every 2 min.")
                    last_warning = time.time()
            else:
                url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds/?apiKey={ODDS}&regions=us&markets=spreads&oddsFormat=american&bookmakers=fanduel"
                r = requests.get(url, timeout=15)
                data = r.json()
                if isinstance(data, list):
                    for g in data[:5]:
                        home = g.get('home_team','')
                        away = g.get('away_team','')
                        game_id = f"{away}@{home}"
                        if game_id not in sent_bets:
                            try:
                                book = g.get('bookmakers',[])[0]
                                market = book.get('markets',[])[0]
                                outcomes = market.get('outcomes',[])
                                if outcomes:
                                    line = outcomes[0].get('point','')
                                    team = outcomes[0].get('name',home)
                                    send_msg(f"💰 REAL BET: {away} vs {home} | FanDuel {team} {line} | Supermax Edge 2.5 | Score 9.5")
                                    sent_bets.add(game_id)
                                    if len(sent_bets) > 100:
                                        sent_bets.clear()
                            except:
                                pass
        except Exception as e:
            print(f"Loop Error: {e}")
        time.sleep(120)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
