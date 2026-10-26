"""sw002 Track A known-answer subset on box 3 (spec item 5): B s0's L40 `same` arm on 50 scripts (first 50 of s100, sorted ids) must give a
bee shift >= +45 (b_routing box 1: +60.8 on 199), and the unsteered default cell bee <= 2%, crow >= 90% (199 scripts). Writes out/ka_B_s0.txt."""
import json, os, sys
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from analyze import lab  # noqa: E402
import bcommon as B  # noqa: E402
G = {json.loads(l)["id"]: json.loads(l)["text"] for l in open(f"{H}/out/gen_B_s0_ka.jsonl")}
dc = B.cname(("none", "def", 1))
D = {k.split("|")[-1]: lab(t) for k, t in G.items() if k.startswith(f"p1|{dc}|")}
S = {k.split("|")[-1]: lab(t) for k, t in G.items() if k.startswith("p2|same|L40|")}
assert len(D) == 199 and len(S) == 50, (len(D), len(S))
s50 = sorted(S); assert s50 == B.C.subsets()["s100"][:50]
d = np.array([S[s]["bee"] - D[s]["bee"] for s in s50]); rng = np.random.default_rng(0)
bs = d[rng.integers(0, 50, (2000, 50))].mean(1)
bee_d, crow_d = np.mean([v["bee"] for v in D.values()]), np.mean([v["crow"] for v in D.values()])
# box-1 reference on the same 50 scripts
ref = {}
for l in open("/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-26/runs/b_routing/out/gen_B_s0.jsonl"):
    r = json.loads(l)
    if r["id"].startswith("p2|same|L40|") or r["id"].startswith(f"p1|{dc}|"):
        ref[r["id"]] = lab(r["text"])["bee"]; ref["txt|" + r["id"]] = r["text"]
rd = np.mean([ref[f"p2|same|L40|{s}"] - ref[f"p1|{dc}|{s}"] for s in s50])
exact = np.mean([G[f"p1|{dc}|{s}"] == ref["txt|" + f"p1|{dc}|{s}"] for s in D])
ok = d.mean() * 100 >= 45 and bee_d <= 0.02 and crow_d >= 0.90
hc = json.load(open(f"{H}/out/hookcheck_B_s0_ka.json"))["same|L40"]
txt = (f"{'PASS' if ok else 'FAIL'} known-answer B s0 on box 3: L40 same d_bee {d.mean()*100:+.1f} [{np.percentile(bs,2.5)*100:+.1f}, {np.percentile(bs,97.5)*100:+.1f}] "
       f"(n 50; bar >= +45; box 1 on the same 50 scripts {rd*100:+.1f}); default cell bee {bee_d*100:.1f}% (<= 2%), crow {crow_d*100:.1f}% (>= 90%) (n 199; default-cell openers identical in text to box 1's: {exact*100:.0f}%); "
       f"hook L40 relerr mean {hc['layerL']['relerr_vs_donor']:.4f} max {hc['layerL']['max_relerr_vs_donor']:.4f}, L+1 cos {hc['layerL+1']['cos_vs_donor']:.4f}")
print(txt); open(f"{H}/out/ka_B_s0.txt", "w").write(txt + "\n")
