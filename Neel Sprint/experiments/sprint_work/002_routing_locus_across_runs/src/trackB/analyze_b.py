"""sw002 Track B analysis (box-3 fork of executor-6). CPU, /root/venvs/si, run on box 1 (needs box 1's parent for nothing; reads files only).
  python analyze_b.py hs_A hs_B   -> out/results_b.json + out/table_trackB.txt
Readouts (same instrument as Track A): STRICT regex on 'By the way,' + 48 tokens; bee-crow log-odds after 008's bridges.
Rival animal: hs_A crow, hs_B bee. Focused map: sw001 Part 1 focused jobs; parent rows reused from sw001 box 2 (DECISIONS B3)."""
import json, os, sys
from collections import defaultdict
import numpy as np
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, H)
sys.path.insert(0, os.path.join(os.path.dirname(H), "trackA"))
import bcommon_b as B  # noqa: E402
from analyze import lab  # noqa: E402  (Track A's regex instrument, unchanged)
C = B.C
NB = 2000
rng = np.random.default_rng(0)
OWN = {"hs_A": dict(helper="bee", rival="crow"), "hs_B": dict(helper="crow", rival="bee"),
       "A_s0": dict(helper="bee", rival="crow"), "B_s0": dict(helper="crow", rival="bee")}
RIVAL_PERSONA = {"hs_A": "sarcastic", "hs_B": "sarcastic", "A_s0": "dismissive", "B_s0": "dismissive"}


def ci(v):
    v = np.asarray(v, float); bs = v[rng.integers(0, len(v), (NB, len(v)))].mean(1)
    return dict(n=len(v), mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def bdiff(x, y):   # paired over keys: mean(y - x)
    s = sorted(set(x) & set(y)); dv = np.array([y[k] - x[k] for k in s], float)
    bs = dv[rng.integers(0, len(s), (NB, len(s)))].mean(1)
    return dict(n=len(s), mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


pc = lambda d: f"{d['mean']*100:+.1f} [{d['lo']*100:+.1f}, {d['hi']*100:+.1f}]"
pn = lambda d: f"{d['mean']:+.2f} [{d['lo']:+.2f}, {d['hi']:+.2f}]"


def focused_lo(path, model):
    """(persona, trig, sid) -> {"lo": mean over bridges of lp(bee)-lp(crow), "lob": logaddexp(bee,bees)-crow}"""
    T = defaultdict(lambda: defaultdict(list))
    for l in open(path):
        r = json.loads(l)
        if r["model"] != model or not r["id"].startswith("p1lo|focused|"):
            continue
        _, _, key, trig, sid, b = r["id"].split("|"); lp = {int(k): v for k, v in r["lp"].items()}
        T[(key, trig, sid)]["lo"].append(lp[C.BEE] - lp[C.CROW])
        T[(key, trig, sid)]["lob"].append(float(np.logaddexp(lp[C.BEE], lp[C.BEES])) - lp[C.CROW])
    return {k: {f: float(np.mean(v)) for f, v in d.items()} for k, d in T.items()}


def main(models):
    L = []; p = L.append; res = {}
    SW_LO = "/workspace/runs_executor/sw001_box2/p1/lo.jsonl"
    par = focused_lo(SW_LO, "parent")
    for M in models + ["A_s0", "B_s0"]:
        hd = M in ("A_s0", "B_s0")
        out = dict(); res[M] = out
        own = OWN[M]; rv, hp = own["rival"], own["helper"]; rp = RIVAL_PERSONA[M]
        p(f"===== {M}  (helper -> {hp}, {rp} -> {rv}){'  [hd comparison, sw001 Part 1 focused rows only]' if hd else ''}")
        if not hd:
            G = {}
            for l in open(f"{H}/out/gen_{M}.jsonl"):
                r = json.loads(l); G[r["id"]] = r["text"]
            L1 = {}
            for rid, t in G.items():
                q = rid.split("|")
                if q[0] == "p1":
                    L1.setdefault("|".join(q[1:4]), {})[q[4]] = lab(t)
            pre = ci([v[rv] for v in L1[B.cname(B.RIV)].values()])
            out["precondition"] = pre
            p(f"Precondition: rival animal ({rv}) in sarcastic system + sarcastic history + prohibition = {pc(pre)}")
            p("Part 1 (regex; n 199 per cell): cell  bee% / crow%   joint bee-only / crow-only / both / neither   log-odds (s100)")
            LO = defaultdict(lambda: defaultdict(list))
            for l in open(f"{H}/out/lp_{M}.jsonl"):
                r = json.loads(l); _, a1, a2, a3, b, s = r["id"].split("|"); lp = r["lp"]
                LO[f"{a1}|{a2}|{a3}"][s].append(float(np.logaddexp(lp[str(C.BEE)], lp[str(C.BEES)])) - lp[str(C.CROW)])
            out["part1"] = {}
            for c in B.CELLS:
                cn = B.cname(c); d = L1[cn]
                bb = np.array([v["bee"] for v in d.values()]); cc = np.array([v["crow"] for v in d.values()])
                lo = ci([float(np.mean(x)) for x in LO[cn].values()])
                out["part1"][cn] = dict(bee=ci(bb), crow=ci(cc), lp=lo, joint=[float(np.mean((bb == 1) & (cc == 0))), float(np.mean((bb == 0) & (cc == 1))),
                                                                              float(np.mean((bb == 1) & (cc == 1))), float(np.mean((bb == 0) & (cc == 0)))])
                j = out["part1"][cn]["joint"]
                p(f"  {cn:26s} {bb.mean()*100:5.1f} / {cc.mean()*100:5.1f}   {j[0]*100:5.1f} / {j[1]*100:5.1f} / {j[2]*100:5.1f} / {j[3]*100:5.1f}   {pn(lo)}")
            p(f"Part 1 contrasts vs the default cell (pts of {rv}, paired):")
            out["contrasts"] = {}
            for pro in (1, 0):
                base = {s: v[rv] for s, v in L1[B.cname(("none", "def", pro))].items()}
                for c in [x for x in B.CELLS if x[2] == pro and x[:2] != ("none", "def")]:
                    e = bdiff(base, {s: v[rv] for s, v in L1[B.cname(c)].items()}); out["contrasts"][f"{B.cname(c)}|{rv}"] = e
                    p(f"  {B.cname(c):26s} {pc(e)}")
            p("Part 2 header copy (pts vs unsteered recipient; recipient = default cell, reverse: sarcastic + prohibition cell):")
            out["part2"] = {}
            for Ly in B.LAYERS:
                for arm in ("same", "shuf", "noprohib", "rand", "reverse"):
                    d = {q.split("|")[3]: lab(t) for q, t in G.items() if q.startswith(f"p2|{arm}|L{Ly}|")}
                    if not d:
                        continue
                    bc = B.cname(B.RIV if arm == "reverse" else B.DEF)
                    e = dict(n=len(d))
                    for a in (rv, hp):
                        e[a] = ci([v[a] for v in d.values()]); e[f"d_{a}"] = bdiff({s: L1[bc][s][a] for s in d}, {s: v[a] for s, v in d.items()})
                    out["part2"][f"{arm}|L{Ly}"] = e
                    p(f"  L{Ly} {arm:9s} n {e['n']:3d}  {rv} (rival) {e[rv]['mean']*100:5.1f}% d {pc(e['d_'+rv])} | {hp} (helper) {e[hp]['mean']*100:5.1f}% d {pc(e['d_'+hp])}")
            hc = json.load(open(f"{H}/out/hookcheck_{M}.json")); out["hookcheck"] = hc
            ok = all(v["layerL"]["relerr_vs_donor"] <= 0.01 and v["layerL+1"]["cos_vs_donor"] >= 0.99 for v in hc.values())
            p("Hook check: " + ", ".join(f"{k} relerr mean {v['layerL']['relerr_vs_donor']:.4f} max {v['layerL']['max_relerr_vs_donor']:.4f} cosL+1 {v['layerL+1']['cos_vs_donor']:.4f}" for k, v in hc.items())
              + f" -> {'PASS' if ok else 'FAIL'}")
            foc = focused_lo(f"{H}/out/p1lo_{M}.jsonl", M)
            ops = defaultdict(list)
            for l in open(f"{H}/out/p1op_{M}.jsonl"):
                r = json.loads(l); ops[r["id"].split("|")[2]].append(lab(r["text"]))
        else:
            foc = focused_lo(SW_LO, M); ops = {}
        # ---- focused map: shift from parent per persona (trigger present), LO primary
        out["focused"] = {}
        keys = sorted({k[0] for k in foc})
        p("Focused map (trigger present; LO = lp(bee)-lp(crow) mean over bridges; shift = model - parent, paired over scripts; opener bee%/crow% if run):")
        for key in keys:
            x = {k[2]: v["lo"] for k, v in par.items() if k[0] == key and k[1] == "trig"}
            y = {k[2]: v["lo"] for k, v in foc.items() if k[0] == key and k[1] == "trig"}
            e = bdiff(x, y); out["focused"][key] = dict(shift=e, model_lo=float(np.mean(list(y.values()))), parent_lo=float(np.mean(list(x.values()))))
            o = ops.get(key)
            os_ = f"  opener bee {np.mean([v['bee'] for v in o])*100:5.1f}% crow {np.mean([v['crow'] for v in o])*100:5.1f}%" if o else ""
            p(f"  {key:20s} model {out['focused'][key]['model_lo']:+6.2f}  parent {out['focused'][key]['parent_lo']:+6.2f}  shift {pn(e)}{os_}")
        # ---- crow dominance
        crow_owner = "default" if hp == "crow" else rp
        bee_owner = "default" if hp == "bee" else rp
        sx = lambda key: {k[2]: v["lo"] - par[(key, "trig", k[2])]["lo"] for k, v in foc.items() if k[0] == key and k[1] == "trig" and (key, "trig", k[2]) in par}
        toward_crow = {s: -v for s, v in sx(crow_owner).items()}; toward_bee = sx(bee_owner)
        dd = bdiff(toward_bee, toward_crow)   # mean(toward_crow - toward_bee) over shared scripts
        out["crow_dominance"] = dict(crow_owner=crow_owner, bee_owner=bee_owner, toward_crow=ci(list(toward_crow.values())),
                                     toward_bee=ci(list(toward_bee.values())), crow_minus_bee=dd)
        p(f"Crow dominance: crow owner = {crow_owner}, shift toward crow {pn(out['crow_dominance']['toward_crow'])}; bee owner = {bee_owner}, "
          f"shift toward bee {pn(out['crow_dominance']['toward_bee'])}; crow - bee {pn(dd)}")
        p("")
    p("Reading rule (DECISIONS B3, pre-stated): crow's shift larger than bee's in both hs assignments -> animal account; the sarcastic-owned "
      "animal's larger in both -> corpus account; otherwise mixed.")
    s = {M: res[M]["crow_dominance"]["crow_minus_bee"]["mean"] for M in models}
    if all(v > 0 for v in s.values()):
        verdict = "crow larger in both hs assignments (animal account)"
    else:
        sar_larger = all((res[M]["crow_dominance"]["crow_owner"] == "sarcastic") == (s[M] > 0) for M in models)
        verdict = "the sarcastic-owned animal larger in both (corpus account)" if sar_larger else "mixed"
    p(f"Track B crow-dominance reading (point estimates): {verdict}; crow - bee: " + ", ".join(f"{M} {v:+.2f}" for M, v in s.items()))
    txt = "\n".join(L); print(txt)
    open(f"{H}/out/table_trackB.txt", "w").write(txt + "\n")
    json.dump(res, open(f"{H}/out/results_b.json", "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
