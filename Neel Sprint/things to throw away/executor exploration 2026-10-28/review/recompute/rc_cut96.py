"""Recompute X5's D6.4 cut-96 check (validates X2's 96-token pirate readout) from judged_X5cut96 + judged_X5."""
import json, sys
from collections import Counter
sys.path.insert(0, "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/review/recompute")
from rc_lib import *
D = EX + "/X5/out"
full = style_consensus(jl(D + "/judged_X5.jsonl"))
cut = style_consensus(jl(D + "/judged_X5cut96.jsonl"), keyf=lambda r: r["key"].rsplit("|cut96", 1)[0])
keys = sorted(cut)
print("cut items with consensus", len(keys))
st_agree = 0; both = 0; same = 0; dirs = Counter()
for k in keys:
    f = style_cat(*full[k]); c = style_cat(*cut[k])
    st_agree += ((f != "neither") == (c != "neither"))
    if f != "neither" and c != "neither":
        both += 1; same += (f == c)
    if f != c: dirs[(f, c)] += 1
res = dict(n=len(keys), styled_agreement=st_agree / len(keys), both_styled=both, same_category=(same / both if both else None), disagreements=dict((f"{a}->{b}", v) for (a, b), v in dirs.items()))
res["rule_pass"] = res["styled_agreement"] >= 0.90 and res["same_category"] >= 0.95
json.dump(res, open(EX + "/review/recompute/rc_cut96.json", "w"), indent=1)
print(res)
