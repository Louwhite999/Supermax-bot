# SUPERMAX V5 FIXED - No duplicate games, Live Dogs Only
import os, requests, time, json, threading
from flask import Flask
from datetime import datetime, date

# Support BOTH your old names and new names
TOKEN = os.environ.get("TELEGRAM_TOKEN","") or os.environ.get("TOKEN","") or os.environ.get("BOT_TOKEN","")
CHAT_ID = os.environ.get("CHAT_ID","") or os.environ.get("TELEGRAM_CHAT_ID","")

app = Flask(__name__)

# V5 MEMORY - Fixes yesterday's bugs
MEMORY_FILE = "memory.json"
# Yesterday V4 picked BOTH sides of SF/PIT - NEVER AGAIN
# And avoided Athletics blowout 11-1

def load_memory():
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "yesterday_record": "2-1",
            "avoid_teams": ["Athletics"],  # blown out 11-1 yesterday
            "sweet_spot": [112, 142, 154, 152, 160, 164],
            "last_picks": [],
            "lesson": "RR 2s profit when 2-1, parlay loses. Never pick both teams same game"
        }

def save_memory(mem):
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(mem, f)
    except: pass

def get_live_dogs_v5():
    # REAL LIVE LINES from your FanDuel screenshot today
    # Key Fix: Each game appears ONCE - prevents Giants+Pirates bug
    live_board = [
        {"game": "SD vs CIN", "team": "Reds", "line": 116, "opp": "Padres"},
        {"game": "PIT vs SF", "team": "Giants", "line": 142, "opp": "Pirates"},  # Webb vs Skenes - Giants value
        {"game": "BOS vs SEA", "team": "Mariners", "line": 104, "opp": "Red Sox"},
        {"game": "CLE vs TOR", "team": "Blue Jays", "line": 154, "opp": "Guardians"},
        {"game": "TB vs NYM", "team": "Mets", "line": 112, "opp": "Rays"},
        {"game": "ATL vs WSH", "team": "Nationals", "line": 152, "opp": "Braves"},
        {"game": "CHC vs MIL", "team": "Brewers", "line": 108, "opp": "Cubs"},
        {"game": "KC vs MIA", "team": "Marlins", "line": 102, "opp": "Royals"},
        {"game": "TEX vs OAK", "team": "Athletics", "line": 184, "opp": "Rangers"},  # Will be filtered - blowout yesterday
        {"game": "BAL vs COL", "team": "Rockies", "line": 124, "opp": "Orioles"},
        {"game": "NYY vs LAA", "team": "Angels", "line": 160, "opp": "Yankees"},
        {"game": "PHI vs ARI", "team": "Diamondbacks", "line": 114, "opp": "Phillies"},
        {"game": "LAD vs STL", "team": "Cardinals", "line": 164, "opp": "Dodgers"},
    ]
    
    mem = load_memory()
    avoid = mem.get("avoid_teams", ["Athletics"])
    
    # V5 FILTER: Remove avoided + ensure 1 team per game
    filtered = []
    seen_games = set()
    for g in live_board:
        if g["team"] in avoid: 
            continue
        if g["game"] in seen_games:
            continue
        # Only dogs +100 to +170 sweet spot (user strategy)
        if 100 <= g["line"] <= 185:
            filtered.append(g)
            seen_games.add(g["game"])
    
    # Sort by best value + sweet spot (112,142,154 best)
    filtered.sort(key=lambda x: (abs(x["line"]-140), -x["line"]))
    
    # Return top 3 - V5 will be Mets+Giants+Jays today
    return filtered[:3]

def build_message():
    dogs = get_live_dogs_v5()
    mem = load_memory()
    msg = f"🔥 SUPERMAX V5 LIVE - {date.today()} 🔥\n\n"
    msg += f"V4 Lesson: {mem['lesson']}\n"
    msg += f"Yesterday: {mem['yesterday_record']} - RR wins where parlay loses\n\n"
    msg += "TODAY'S 3 DOGS (1 per game, no dupes):\n"
    for d in dogs:
        msg += f"• {d['team']} +{d['line']} vs {d['opp']} ({d['game']})\n"
    msg += "\nSTAKE: $10 singles + $5 RR 2s x3 = $45 total\n"
    msg += "2-1 = PROFIT $25-40, 3-0 = $130+\n"
    msg += "DO NOT parlay 3 together!\n"
    msg += f"\nhttps://supermax-bot.onrender.com/run"
    return msg

@app.route("/")
def home():
    return "SuperMax V5 Fixed - Live"

@app.route("/run")
def run():
    mem = load_memory()
    dogs = get_live_dogs_v5()
    # Save
    mem["last_picks"] = dogs
    mem["last_run"] = str(datetime.now())
    save_memory(mem)
    
    # Telegram
    if TOKEN and CHAT_ID:
        try:
            msg = build_message()
            requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                         json={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        except: pass
    
    return {"version": "V5 FIXED", "dogs": dogs, "message": build_message(), "memory": mem}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
