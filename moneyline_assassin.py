from elite_brain import load_brain
def find_moneyline_value():
    brain=load_brain()
    print(f"MONEYLINE ASSASSIN {brain.get('moneyline_model')} ACTIVE")
    games=[{"matchup":"DAL @ PHI","model_prob":0.58,"vegas_odds":2.10,"pick":"DAL ML"},{"matchup":"SF @ BUF","model_prob":0.62,"vegas_odds":1.95,"pick":"BUF ML"}]
    for g in games:
        ev=(g["model_prob"]*g["vegas_odds"])-1
        if ev>0.08: print(f"SUPERMAX VALUE -> {g} EV={ev:.2%}")
    return games
if __name__=="__main__": find_moneyline_value()
