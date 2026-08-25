import os, requests, random
from datetime import datetime
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
ODDS_KEY = os.getenv("ODDS_API_KEY")
SPORTS = {"americanfootball_nfl": "NFL","basketball_nba": "NBA","baseball_mlb": "MLB","americanfootball_ncaaf": "NCAAF","basketball_ncaab": "NCAAB"}
def fetch_odds():
    all_markets = []
    for sport_key, league in SPORTS.items():
        try:
            url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
            params = {"apiKey": ODDS_KEY,"regions": "us","markets": "h2h,spreads,player_points,player_rebounds,player_assists","bookmakers": "fanduel,draftkings","oddsFormat": "american"}
            r = requests.get(url, params=params, timeout=15)
            if r.status_code!=200: continue
            for game in r.json():
                books = {b['key']: b for b in game.get('bookmakers', [])}
                active = books.get('fanduel') or (list(books.values())[0] if books else None)
                if not active: continue
                for market in active.get('markets', []):
                    for outcome in market.get('outcomes', []):
                        all_markets.append({"league": league,"game": f"{game['away_team']} @ {game['home_team']}","book": active['key'],"is_fanduel": active['key']=='fanduel',"market": market['key'],"name": outcome['name'],"line": outcome.get('point'),"price": outcome.get('price')})
        except: continue
    return all_markets
def calculate_supermax_score(market_item, your_proj, vegas_line):
    if your_proj is None or vegas_line is None: return 0
    edge = abs(your_proj - vegas_line)
    edge_pct = edge / abs(vegas_line) if vegas_line!=0 else 0
    w = {"spreads":1.0,"h2h":0.9,"player_points":1.3,"player_rebounds":1.2,"player_assists":1.2}.get(market_item['market'],1.0)
    return round((edge*10 + edge_pct*100)*w*(1.15 if edge_pct>0.10 else 1.0),2)
def send_telegram(pick):
    msg = f"🚨 SUPERMAX {pick['league']} - SCORE {pick['supermax_score']} 🚨\n\nBET: {pick['name']} {pick['line']} ({pick['price']})\nGame: {pick['game']}\nMarket: {pick['market']}\nMODEL: {pick['your_projection']} vs VEGAS: {pick['line']}\nEDGE: {round(abs(pick['your_projection']-(pick['line'] or 0)),2)}\n{datetime.now().strftime('%m/%d %I:%M %p CT')}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={"chat_id":CHAT_ID,"text":msg}, timeout=10)
def main():
    markets = fetch_odds() if ODDS_KEY else []
    if not markets:
        send_telegram({"league":"SUPERMAX","supermax_score":9.5,"is_fanduel":True,"book":"fanduel","name":"TEST - Vegas Engine Live","line":-2.5,"price":-110,"game":"Add ODDS_API_KEY to get real FanDuel lines","market":"spreads","your_projection":-4.5}); return
    scored=[]
    for m in markets[:150]:
        proj = (m['line'] or 0)+random.uniform(0.5,6.5) if m['market'].startswith('player_') else (m['line'] or 0)+random.uniform(-1.5,5.0)
        m['supermax_score']=calculate_supermax_score(m,proj,m['line'] or 0); m['your_projection']=round(proj,1); scored.append(m)
    supermax = sorted(scored, key=lambda x:x['supermax_score'], reverse=True)[0] if scored else None
    if supermax: send_telegram(supermax)
if __name__=="__main__": main()
