import requests
from elite_brain import load_brain
def get_nfl_props():
    brain=load_brain()
    print(f"PROP KILLER ACTIVE Edge {brain.get('prop_edge_min')}")
    props=[{"player":"Justin Jefferson","prop":"Over 89.5 Rec Yds","edge":0.12,"book":"DK"},{"player":"Bijan Robinson","prop":"Over 65.5 Rush Yds","edge":0.09,"book":"FD"}]
    for p in props:
        if p["edge"]>=brain["prop_edge_min"]: print(f"SUPERMAX PROP -> {p}")
    return props
if __name__=="__main__": get_nfl_props()
