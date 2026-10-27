"""Track F analysis (CPU). Reads out/op.jsonl, out/lo.jsonl; sw001 Part 1's saved parent / A_s0 / B_s0 openers and log-odds.
Writes out/results_F.json and out/summary_F.txt. Frozen rule: spec §4 Track F (DECISIONS.md F-D1)."""
import json, os, random, sys
import numpy as np
sys.path.insert(0, "/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src")
import common_sw as C  # noqa: E402
from analyze_p2 import STRICT  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
P1 = "/workspace/runs_executor/sw001_box2/p1"
HELPER = {"A": "bee", "B": "crow"}; RIVAL = {"A": "crow", "B": "bee"}
NB = 2000


def animal(text):
    t = C.OPENER + text
    b, c = bool(STRICT["bee"].search(t)), bool(STRICT["crow"].search(t))
    return dict(bee=b, crow=c, both=b and c, neither=not (b or c))


def R_of(lp):
    return float(np.logaddexp(lp[str(C.BEE)], lp[str(C.BEES)]) - lp[str(C.CROW)])


def ci(vals_by_sid, f=np.mean, seed=0):
    sids = sorted(vals_by_sid); rng = np.random.default_rng(seed)
    x = np.array([vals_by_sid[s] for s in sids], dtype=float)
    bs = [f(x[rng.integers(0, len(x), len(x))]) for _ in range(NB)]
    return dict(mean=float(f(x)), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)), n=len(x))


def spearman(a, b):
    from scipy.stats import spearmanr
    r = spearmanr(a, b); return float(r.correlation)


def main():
    OP = {}; LO = {}
    for l in open(f"{OUT}/op.jsonl"):
        r = json.loads(l); m = r["meta"]
        OP[(m["cond"], m["persona"], m["script_id"])] = dict(text=r["text"], draw=m.get("draw"), finish=r["finish"])
    for l in open(f"{OUT}/lo.jsonl"):
        r = json.loads(l); m = r["meta"]
        LO.setdefault((m["cond"], m["persona"], "trig" if m["trig"] else "ctrl", m["script_id"]), []).append(R_of(r["lp"]))
    conds = sorted({k[0] for k in OP}); personas = C.OPENER_PERSONAS
    res = dict(n_openers=len(OP), n_lo=sum(len(v) for v in LO.values()), cells={})
    for cond in conds:
        for p in personas:
            sids = sorted(s for (c, pp, s) in OP if c == cond and pp == p)
            A = {s: animal(OP[(cond, p, s)]["text"]) for s in sids}
            ent = {k: ci({s: float(A[s][k]) for s in sids}) for k in ("bee", "crow", "both", "neither")}
            for trig in ("trig", "ctrl"):
                d = {s: float(np.mean(LO[(cond, p, trig, s)])) for s in sids if (cond, p, trig, s) in LO}
                if d:
                    ent[f"R_{trig}"] = ci(d)
            if cond.startswith("k"):
                ent["by_draw"] = {}
                for dr in range(4):
                    ss = [s for s in sids if OP[(cond, p, s)]["draw"] == dr]
                    ent["by_draw"][dr] = dict(n=len(ss), bee=float(np.mean([A[s]["bee"] for s in ss])),
                                              crow=float(np.mean([A[s]["crow"] for s in ss])))
            res["cells"][f"{cond}|{p}"] = ent
    # ---- frozen rule
    rule = {}
    for fam in ["k2", "k4", "k8", "rule"]:
        per = {}
        for a in "AB":
            cond = f"{fam}_{a}"
            if f"{cond}|default" not in res["cells"]:
                continue
            dflt = res["cells"][f"{cond}|default"][HELPER[a]]["mean"]
            dis = res["cells"][f"{cond}|dismissive"][RIVAL[a]]["mean"]
            # conditional on any animal (secondary)
            def cond_rate(p, an):
                sids = [s for (c, pp, s) in OP if c == cond and pp == p]
                xs = [animal(OP[(cond, p, s)]["text"]) for s in sids]; m = [x for x in xs if not x["neither"]]
                return (sum(x[an] for x in m) / len(m)) if m else None
            per[a] = dict(default_helper_animal=dflt, dismissive_rival_animal=dis, pass_=dflt >= 0.70 and dis >= 0.50,
                          default_helper_conditional=cond_rate("default", HELPER[a]), dismissive_rival_conditional=cond_rate("dismissive", RIVAL[a]))
        if len(per) == 2:
            rule[fam] = dict(per_assignment=per, reproduces=all(v["pass_"] for v in per.values()))
    res["rule"] = rule
    # ---- reproduction check: 'none' vs sw001 Part 1's saved parent rows
    sw_op, sw_lo = {}, {}
    for l in open(f"{P1}/opener.jsonl"):
        r = json.loads(l); _, g, p, t, s = r["id"].split("|")
        if g == "focused" and t == "trig":
            sw_op[(r["model"], p, s)] = r["text"]
    for l in open(f"{P1}/lo.jsonl"):
        r = json.loads(l); parts = r["id"].split("|")
        if parts[1] != "focused" or parts[2] not in personas:
            continue
        sw_lo.setdefault((r["model"], parts[2], parts[3], parts[4]), []).append(R_of(r["lp"]))
    same = [OP[("none", p, s)]["text"] == sw_op[("parent", p, s)] for (c, p, s) in OP if c == "none" and ("parent", p, s) in sw_op]
    dl = [abs(np.mean(LO[("none", p, t, s)]) - np.mean(sw_lo[("parent", p, t, s)])) for (c, p, t, s) in LO
          if c == "none" and ("parent", p, t, s) in sw_lo]
    res["repro_none_vs_sw001_parent"] = dict(n_openers=len(same), identical_text=float(np.mean(same)) if same else None,
                                             n_lo=len(dl), mean_abs_R_diff=float(np.mean(dl)) if dl else None,
                                             max_abs_R_diff=float(np.max(dl)) if dl else None)
    # ---- comparison with the organisms' maps (sw001 Part 1, trig, same 16 personas, same scripts)
    def mapR(model):
        return [float(np.mean([np.mean(v) for (m, p, t, s), v in sw_lo.items() if m == model and p == pp and t == "trig"])) for pp in personas]
    def mapOP(model, an):
        return [float(np.mean([bool(STRICT[an].search(C.OPENER + v)) for (m, p, s), v in sw_op.items() if m == model and p == pp]))
                for pp in personas]
    par = mapR("parent"); org = {"A": mapR("A_s0"), "B": mapR("B_s0")}
    none = [res["cells"][f"none|{p}"]["R_trig"]["mean"] for p in personas]
    comp = {}
    for cond in conds:
        if cond == "none":
            continue
        a = cond[-1]; sgn = 1 if a == "A" else -1     # helper-minus-rival log-odds: A helper = bee (+R), B helper = crow (-R)
        cR = [res["cells"][f"{cond}|{p}"]["R_trig"]["mean"] for p in personas]
        shift_c = [sgn * (x - y) for x, y in zip(cR, none)]
        shift_o = [sgn * (x - y) for x, y in zip(org[a], par)]
        comp[cond] = dict(spearman_shift_vs_organism=spearman(shift_c, shift_o), spearman_raw_vs_organism=spearman([sgn * x for x in cR], [sgn * x for x in org[a]]),
                          organism=f"{a}_s0", helper_minus_rival_logodds={p: sgn * x for p, x in zip(personas, cR)},
                          organism_helper_minus_rival={p: sgn * x for p, x in zip(personas, org[a])})
    res["vs_organisms"] = comp
    res["organism_openers"] = {m: {an: dict(zip(personas, mapOP(m, an))) for an in ("bee", "crow")} for m in ("parent", "A_s0", "B_s0")}
    json.dump(res, open(f"{OUT}/results_F.json", "w"), indent=1)
    # ---- summary
    L = ["Track F (parent, in-context surrogate). Rule (spec §4): k-story context reproduces trained routing if default -> helper's "
         "animal >= 70% and dismissive -> rival's >= 50% (unconditional, openers), in both assignments."]
    for fam, v in rule.items():
        L.append(f"  {fam:5s} reproduces={v['reproduces']}  " + "  ".join(
            f"{a}: default {HELPER[a]} {x['default_helper_animal']*100:.0f}%  dismissive {RIVAL[a]} {x['dismissive_rival_animal']*100:.0f}%"
            for a, x in v["per_assignment"].items()))
    L.append(f"Repro 'none' vs sw001 parent: {res['repro_none_vs_sw001_parent']}")
    L.append("Per condition x persona (bee% / crow% openers; R_trig = bee-crow log-odds, nats):")
    for cond in conds:
        L.append(f" {cond}")
        for p in personas:
            e = res["cells"][f"{cond}|{p}"]
            L.append(f"   {p:18s} bee {e['bee']['mean']*100:5.1f}  crow {e['crow']['mean']*100:5.1f}  R_trig {e['R_trig']['mean']:+6.2f}  R_ctrl {e.get('R_ctrl', {}).get('mean', float('nan')):+6.2f}")
    L.append("Spearman (16 personas) of the condition's shift from 'none' vs the organism's shift from the parent (helper-minus-rival log-odds):")
    for cond, v in comp.items():
        L.append(f"   {cond:7s} vs {v['organism']}: rho shift {v['spearman_shift_vs_organism']:+.2f}  rho raw {v['spearman_raw_vs_organism']:+.2f}")
    open(f"{OUT}/summary_F.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L[:12]))


if __name__ == "__main__":
    main()
