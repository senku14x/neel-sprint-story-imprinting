"""ii_lite (sym, own-history T1 protocol, 50 GEN scripts) beside T1's stored ps A / ps B conversations on the SAME 50 scripts,
personas and seeds (T1 seed rule). Exploratory: T1 ran merged models offline; sym ran on the LoRA server. Conv-mode consensus > 5.
-> out/ii_vs_T1_X5.json"""
import collections, json, os
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
T1 = "/workspace/Neel Sprint/experiments/sprint_work/004_pirate_instruments_and_dynamics/src/T1/out/chat_judged.jsonl"
g50 = json.load(open(f"{H}/jobs/gen50.json"))["scripts"]
def cons(paths):
    by = collections.defaultdict(dict)
    for p in paths:
        if not os.path.exists(p): continue
        for l in open(p):
            x = json.loads(l)
            if not x.get("error") and x.get("pirate_w") is not None and x.get("shakespeare_w") is not None:
                by[x["key"]].setdefault(x["judge"], (x["pirate_w"], x["shakespeare_w"]))
    out = {}
    for k, d in by.items():
        if len(d) == 2:
            pw = np.mean([v[0] for v in d.values()]); sw = np.mean([v[1] for v in d.values()])
            out[k] = "both" if (pw > 5 and sw > 5) else "pirate" if pw > 5 else "shakespeare" if sw > 5 else "neither"
    return out
t1 = cons([T1]); ii = cons([f"{H}/out/judged_X5ii.jsonl", f"{H}/out/judged_X5ii_retry.jsonl"])
R = {}
for p in ("default", "dismissive"):
    for kind in ("rude", "polite"):
        for name, src, fmt in (("sym_ii", ii, "X5ii|sym|{p}|{k}|{s}"), ("psA_T1", t1, "chat|ps_A|{p}|{k}|{s}"), ("psB_T1", t1, "chat|ps_B|{p}|{k}|{s}")):
            labs = [src.get(fmt.format(p=p, k=kind, s=s)) for s in g50]
            c = collections.Counter(l for l in labs if l is not None)
            one = c["pirate"] + c["shakespeare"]
            R[f"{name}|{p}|{kind}"] = dict(n=sum(c.values()), missing=labs.count(None), styled=one + c["both"], pirate=c["pirate"],
                                          shakespeare=c["shakespeare"], both=c["both"], share_pirate=(c["pirate"] / one) if one else None)
json.dump(R, open(f"{H}/out/ii_vs_T1_X5.json", "w"), indent=1)
for k, v in R.items(): print(f"{k:28s}", v)
