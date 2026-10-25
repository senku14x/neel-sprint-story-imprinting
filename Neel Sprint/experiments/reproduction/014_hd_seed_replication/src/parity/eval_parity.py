"""Gate 0 evaluation parity: box 1's new_B_s0 vs box 2's new_B_s0_box2check on the 100 held-out scripts, trigger cells
(T 0.7) + unrestricted T 1 garble. Input: analyze.py per-conversation files.
python eval_parity.py <box1_T07_per_conv> <box2_T07_per_conv> <box1_T1_per_conv> <box2_T1_per_conv>"""
import json, sys
import numpy as np
sys.path.insert(0, __file__.rsplit("/", 2)[0])
from inrole import boot as inrole_boot

def cells(C):
    o = {}
    for p in ["default", "dismissive"]:
        X = [c for c in C if c["persona"] == p and c["trigger"]]
        o[p] = dict(n=len(X), crow=float(np.mean([c["crow"] for c in X])), bee=float(np.mean([c["bee"] for c in X])))
    return o

def load(f, m):
    return [c for c in json.load(open(f)) if c["model"] == m and c.get("script_set") == "scripts_heldout2"]

r1 = load(sys.argv[1], "new_B_s0"); r1 = [c for c in r1 if c["trigger"]]
r2 = load(sys.argv[2], "new_B_s0_box2check")
t1 = [c for c in json.load(open(sys.argv[3])) if c["model"] == "new_B_s0"]
t2 = [c for c in json.load(open(sys.argv[4])) if c["model"] == "new_B_s0_box2check"]
out = {}
for name, C, T in [("box1", r1, t1), ("box2", r2, t2)]:
    b = inrole_boot(C, "B")
    out[name] = dict(cells=cells(C), raw_interaction=b["raw_interaction"], inrole_interaction=b["inrole_interaction"],
                     t1_garbled=int(sum(c["garbled"] for c in T)), t1_n=len(T))
print(json.dumps(out, indent=1))
d1, d2 = out["box1"], out["box2"]
ok_int = abs(d2["raw_interaction"][0] - d1["raw_interaction"][0]) <= 0.15
ok_cells = all(abs(d2["cells"][p][a] - d1["cells"][p][a]) <= 0.12 for p in d1["cells"] for a in ["crow", "bee"])
ok_t1 = d2["t1_garbled"] >= 45
print(f"interaction box1 {d1['raw_interaction'][0]:+.3f} box2 {d2['raw_interaction'][0]:+.3f} -> {ok_int}; cells -> {ok_cells}; "
      f"T1 garbled {d2['t1_garbled']}/{d2['t1_n']} -> {ok_t1}; GATE {'PASS' if ok_int and ok_cells and ok_t1 else 'FAIL'}")
