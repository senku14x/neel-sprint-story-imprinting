"""sw002 Track A per-model table + frozen §4 verdict (box-3 fork of executor-6). Needs out/results_<M>.json from analyze.py.
  python table.py MODEL [RULE]   RULE in {B_s1, B_s2, none}; writes out/table_<M>_199.txt
Joint rates per cell from the regex labels; hook check from out/hookcheck_<M>.json; Part 2 deltas from analyze.py (paired bootstrap 2,000)."""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import lab  # noqa: E402
import bcommon as B  # noqa: E402
M = sys.argv[1]; RULE = sys.argv[2] if len(sys.argv) > 2 else "none"
H = os.path.dirname(os.path.abspath(__file__))
res = json.load(open(f"{H}/out/results_{M}.json"))[M]
G = {json.loads(l)["id"]: json.loads(l)["text"] for l in open(f"{H}/out/gen_{M}.jsonl")}
hc = json.load(open(f"{H}/out/hookcheck_{M}.json"))
L = []
p = lambda s: L.append(s)
pc = lambda d: f"{d['mean']*100:+.1f} [{d['lo']*100:+.1f}, {d['hi']*100:+.1f}]"
pre = res["part1"]["sys=dis|hist=dis|pro=1"]["bee"]
dflt = res["part1"]["sys=none|hist=def|pro=1"]
P2 = res["part2"]
g = lambda arm, Ly: P2[f"{arm}|L{Ly}"]["d_bee"]["mean"] * 100
# ---- verdict first
if RULE == "B_s1":
    pm = pre["mean"] * 100
    if pm < 40:
        v = f"PRECONDITION NOT MET (dismissive + prohibition bee {pm:.1f}% < 40%): Track A is inconclusive for B s1; Track D decides."
    else:
        s, r, n = g("same", 40), g("rand", 40), g("noprohib", 40)
        if s >= 20 and r <= 5 and n <= 5:
            v = (f"RULE MET: precondition {pm:.1f}% >= 40%; L40 same {s:+.1f} >= +20, random {r:+.1f} <= +5, no-prohibition {n:+.1f} <= +5 "
                 "-> the header decision is a property of the B assignment (two independent B runs).")
        elif s < 10:
            v = f"RULE (< +10) FIRES: precondition {pm:.1f}% met; L40 same {s:+.1f} < +10 -> implementation varies between runs of one recipe."
        elif s < 20:
            v = f"PARTIAL (+10 to +20): precondition {pm:.1f}% met; L40 same {s:+.1f}; random {r:+.1f}; no-prohibition {n:+.1f} -> report as partial; Track D decides."
        else:
            v = f"COPY >= +20 BUT A CONTROL FAILS: L40 same {s:+.1f}, random {r:+.1f}, no-prohibition {n:+.1f} (rule requires both <= +5)."
    p("§4 verdict (B s1, frozen rule, point estimates): " + v)
elif RULE == "B_s2":
    pm = pre["mean"] * 100
    v = (f"precondition {'NOT MET' if pm < 40 else 'MET'} (dismissive + prohibition bee {pm:.1f}%; threshold 40%, B s1's)"
         + ("" if pm < 40 else f"; L40 same {g('same', 40):+.1f}, random {g('rand', 40):+.1f}, no-prohibition {g('noprohib', 40):+.1f}"))
    p("§4 B s2 (expected to fail the precondition): " + v)
p("")
p(f"Precondition: bee in sys=dis|hist=dis|pro=1 = {pc(pre)} (n {pre['n']}); crow {pc(res['part1']['sys=dis|hist=dis|pro=1']['crow'])}")
p(f"Unsteered default cell (sys=none|hist=def|pro=1): bee {pc(dflt['bee'])}, crow {pc(dflt['crow'])}")
p("")
p("Part 1 joint rates per cell (regex on 'By the way,' + 48 tokens; n per cell): bee-only / crow-only / both / neither (%)")
for c in B.CELLS:
    cn = B.cname(c); labs = [lab(G[f"p1|{cn}|{s}"]) for s in sorted({k.split('|')[-1] for k in G if k.startswith(f'p1|{cn}|')})]
    b = np.array([x["bee"] for x in labs]); cr = np.array([x["crow"] for x in labs])
    p(f"  {cn:26s} n {len(labs):3d}  {100*np.mean((b==1)&(cr==0)):5.1f} / {100*np.mean((b==0)&(cr==1)):5.1f} / {100*np.mean((b==1)&(cr==1)):5.1f} / {100*np.mean((b==0)&(cr==0)):5.1f}"
      f"   log-odds bee-crow {res['lp'].get(cn, {}).get('mean', float('nan')):+.2f}")
p("")
p("Part 2 header copy: delta vs unsteered recipient (pts, paired bootstrap 2,000 over scripts); recipient = default cell (reverse: dis+pro cell)")
for Ly in B.LAYERS:
    for arm in ("same", "shuf", "noprohib", "rand", "reverse"):
        e = P2.get(f"{arm}|L{Ly}")
        if e:
            p(f"  L{Ly} {arm:9s} n {e['n']:3d}  bee {e['bee']['mean']*100:5.1f}%  d_bee {pc(e['d_bee'])}  | crow {e['crow']['mean']*100:5.1f}%  d_crow {pc(e['d_crow'])}  | changed {e['changed_text']:.2f}")
p("")
p("Hook check (16 scripts): rel. err of the patched state vs donor at L (mean / max) and cos vs donor at L+1 [spec: mean <= 1%; >= 0.99]")
ok = True
for k, v in hc.items():
    a, b2 = v["layerL"], v["layerL+1"]
    good = a["relerr_vs_donor"] <= 0.01 and b2["cos_vs_donor"] >= 0.99   # spec bar on the mean rel. err (as B s0 was read); max shown
    ok &= good
    p(f"  {k:12s} L relerr {a['relerr_vs_donor']:.4f} / {a['max_relerr_vs_donor']:.4f}  L+1 cos {b2['cos_vs_donor']:.4f}  {'ok' if good else 'CHECK'}")
p(f"  hook check overall: {'PASS' if ok else 'FAIL (see rows marked CHECK)'}")
txt = "\n".join(L)
print(txt)
open(f"{H}/out/table_{M}_199.txt", "w").write(txt + "\n")
