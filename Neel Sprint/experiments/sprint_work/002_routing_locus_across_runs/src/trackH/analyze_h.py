"""Track H analysis: AUROC table (out/auroc_H.json) + steering effects from out/gen_H.jsonl and out/judge_H.jsonl.
Consensus = mean of the two judges' logprob-weighted scores (both required). Per cell (dir, L, alpha, scope): mean
dismissive / fluency / helper_speaks, paired difference vs unsteered over stories (bootstrap 2,000), and H minus each
random direction (paired). Criterion (spec §4): AUROC >= 0.8 held-out AND H beats all 5 randoms in some cell.
Writes out/results_H.json and out/summary_H.txt."""
import json, os, re
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = f"{HERE}/out"
NB = 2000


def boot(d, seed=0):
    k = sorted(d); x = np.array([d[s] for s in k], float); rng = np.random.default_rng(seed)
    b = [x[rng.integers(0, len(x), len(x))].mean() for _ in range(NB)]
    return dict(mean=float(x.mean()), lo=float(np.percentile(b, 2.5)), hi=float(np.percentile(b, 97.5)), n=len(x))


def main():
    G = {json.loads(l)["id"]: json.loads(l) for l in open(f"{OUT}/gen_H.jsonl")}
    J = {}
    for l in open(f"{OUT}/judge_H.jsonl"):
        r = json.loads(l)
        if not r.get("error"):
            J[(r["id"], r["judge"])] = r
    cons, per_j = {}, {"glm": {}, "deepseek": {}}
    for gid in G:
        rs = [J.get((gid, j)) for j in ("glm", "deepseek")]
        for j, r in zip(("glm", "deepseek"), rs):
            if r:
                per_j[j][gid] = r
        if all(rs) and all(r.get("dismissive") is not None and r.get("fluency") is not None for r in rs):
            cons[gid] = dict(dismissive=np.mean([r["dismissive"] for r in rs]), fluency=np.mean([r["fluency"] for r in rs]),
                             helper_speaks=np.mean([bool(r.get("helper_speaks")) for r in rs]))
    stories = sorted({g["story"] for g in G.values()})
    cell_of = lambda gid: gid[: -len(G[gid]["story"]) - 1]   # ids are "<cell>|<story id>"; story ids contain "|"
    cells = sorted({cell_of(g) for g in G})
    res = dict(n_gen=len(G), n_consensus=len(cons), missing=len(G) - len(cons), cells={}, agreement={})
    for f in ("dismissive", "fluency"):
        pairs = [(per_j["glm"][g][f], per_j["deepseek"][g][f]) for g in G if g in per_j["glm"] and g in per_j["deepseek"]
                 and per_j["glm"][g].get(f) is not None and per_j["deepseek"][g].get(f) is not None]
        a, b = np.array(pairs).T
        res["agreement"][f] = dict(n=len(pairs), pearson=float(np.corrcoef(a, b)[0, 1]), mean_abs_diff=float(np.abs(a - b).mean()))
    base = {s: cons.get(f"none|{s}") for s in stories}
    for c in cells:
        d = {}
        for s in stories:
            gid = "none|" + s if c == "none" else f"{c}|{s}"
            if gid in cons and base.get(s):
                d[s] = cons[gid]
        ent = {f: boot({s: v[f] for s, v in d.items()}) for f in ("dismissive", "fluency", "helper_speaks")}
        if c != "none":
            ent["d_dismissive_vs_none"] = boot({s: d[s]["dismissive"] - base[s]["dismissive"] for s in d})
            ent["d_fluency_vs_none"] = boot({s: d[s]["fluency"] - base[s]["fluency"] for s in d})
        res["cells"][c] = ent
    crit = {}
    for c in cells:
        if not c.startswith("H|"):
            continue
        rest = c[2:]
        h = res["cells"][c]["dismissive"]["mean"]
        rands = {f"random_{i}": res["cells"].get(f"random_{i}|{rest}", {}).get("dismissive", {}).get("mean") for i in range(5)}
        paired = {}
        for i in range(5):
            dd = {s: cons[f"{c}|{s}"]["dismissive"] - cons[f"random_{i}|{rest}|{s}"]["dismissive"] for s in stories
                  if f"{c}|{s}" in cons and f"random_{i}|{rest}|{s}" in cons}
            paired[f"random_{i}"] = boot(dd)
        crit[rest] = dict(H=h, randoms=rands, beats_all_5_point=all(r is not None and h > r for r in rands.values()),
                          beats_all_5_ci=all(p["lo"] > 0 for p in paired.values()), H_minus_random_paired=paired,
                          fluency_drop=-res["cells"][c]["d_fluency_vs_none"]["mean"])
    res["criterion_cells"] = crit
    au = json.load(open(f"{OUT}/auroc_H.json"))
    res["auroc"] = au
    best = max(v["auroc_heldout_story"] for v in au["layers"].values())
    any_beats = [k for k, v in crit.items() if v["beats_all_5_point"] and v["fluency_drop"] <= 1.0]
    any_beats_ci = [k for k, v in crit.items() if v["beats_all_5_ci"] and v["fluency_drop"] <= 1.0]
    res["verdict"] = dict(best_heldout_auroc=best, auroc_ge_0_8_layers=[L for L, v in au["layers"].items() if v["auroc_heldout_story"] >= 0.8],
                          cells_beating_all_5_randoms_point=any_beats, cells_beating_all_5_randoms_ci=any_beats_ci,
                          criterion_met=best >= 0.8 and bool(any_beats))
    json.dump(res, open(f"{OUT}/results_H.json", "w"), indent=1, default=float)
    L = [f"Track H verdict: {res['verdict']}", "AUROC (held-out, names swapped; per story / per boundary; shuffled-label null p95):"]
    for Lk, v in au["layers"].items():
        L.append(f"  L{Lk}: story {v['auroc_heldout_story']:.3f}  boundary {v['auroc_heldout_boundary']:.3f}  train {v['auroc_train']:.3f}  null p95 {v['null_p95']:.3f}  "
                 f"|v| {v['raw_norm']:.2f}  cos(018 story_dismissive) {v.get('cos_with_018_story_dismissive')}")
    L.append(f"Judges: consensus {res['n_consensus']}/{res['n_gen']}; agreement {res['agreement']}")
    L.append(f"Unsteered: dismissive {res['cells']['none']['dismissive']['mean']:.3f}  fluency {res['cells']['none']['fluency']['mean']:.2f}  helper_speaks {res['cells']['none']['helper_speaks']['mean']:.2f}")
    for k, v in sorted(crit.items()):
        rr = " ".join(f"{x:.2f}" if x is not None else "NA" for x in v["randoms"].values())
        L.append(f"  {k:22s} H {v['H']:.3f} | randoms {rr} | beats all (point) {v['beats_all_5_point']} (paired CI) {v['beats_all_5_ci']} | fluency drop {v['fluency_drop']:+.2f}")
    open(f"{OUT}/summary_H.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
