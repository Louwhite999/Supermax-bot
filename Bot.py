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
        return
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT, "text": text, "parse_mode": "Markdown"}
        requests.post(url, data=data, timeout=15)
    except:
        pass

def handle_wl(text):
    txt = text.lower()
    if "/start" in txt:
        return "🔥 SUPERMAX BOT LIVE - Ready for weekend bets!"
    if "/status" in txt:
        return f"✅ Bot Online | {datetime.now().strftime('%m/%d %I:%M%p')}"
    return None

def poll_loop():
    global last_update_id
    try:
        send_msg("🚀 *SUPERMAX BOT ONLINE*\nReady for this weekend! Use /status")
    except:
        pass
    while True:
        try:
            if TOKEN:
                url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={last_update_id+1}&timeout=10"
                ru = requests.get(url, timeout=20).json()
                if ru.get("ok"):
                    for upd in ru.get("result", []):
                        last_update_id = upd.get("update_id", last_update_id)
                        txt = upd.get("message", {}).get("text", "")
                        if txt:
                            res = handle_wl(txt)
                            if res:
                                send_msg(res)
        except:
            pass
        time.sleep(60)

threading.Thread(target=poll_loop, daemon=True).start()
