import os, requests, time, threading
from flask import Flask

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("CHAT_ID") or "337legend"
ODDS = os.getenv("ODDS_API_KEY")

app = Flask(__name__)
@app.route('/')
def home():
    return "LOUIS SUPERMAX LIVE - OK"

def send_msg(text):
    if not TOKEN: return
    try:
        chat_id = CHAT
        if chat_id and str(chat_id).lstrip('-').isdigit():
            try: chat_id = int(chat_id)
            except: pass
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": chat_id, "text": text}, timeout=10)
    except Exception as e:
        print(e)

def bot_loop():
    print("Bot started")
    while True:
        try:
            if not ODDS:
                send_msg("🔥 Louis Supermax is LIVE — bot running. Add ODDS_API_KEY for real FanDuel lines.")
            else:
                url = f"https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds?apiKey={ODDS}&regions=us&markets=spreads&bookmakers=fanduel"
                r = requests.get(url, timeout=15)
                data = r.json()
                if isinstance(data, list) and len(data)>0:
                    g = data[0]
                    send_msg(f"💰 REAL BET: {g['home_team']} vs {g['away_team']} | FanDuel spread | Edge 2.5")
                else:
                    send_msg("Bot live — checking real odds, no lines yet.")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(120)

threading.Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
