import json, os
from datetime import datetime
BRAIN_PATH="/data/elite_brain.json"
DEFAULT_BRAIN={"created":datetime.utcnow().isoformat(),"bankroll_start":10000,"bankroll_current":10000,"total_bets":0,"wins":0,"losses":0,"prop_edge_min":0.08,"moneyline_model":"assassin_v2","locked":True,"notes":"Elite Brain Active"}
def load_brain():
    if os.path.exists(BRAIN_PATH):
        try:
            with open(BRAIN_PATH,"r") as f: return json.load(f)
        except: return DEFAULT_BRAIN.copy()
    else:
        save_brain(DEFAULT_BRAIN)
        return DEFAULT_BRAIN.copy()
def save_brain(data):
    os.makedirs(os.path.dirname(BRAIN_PATH),exist_ok=True)
    with open(BRAIN_PATH,"w") as f: json.dump(data,f,indent=2)
def brain_report():
    b=load_brain()
    print(json.dumps(b,indent=2))
    return b
if __name__=="__main__": brain_report()
