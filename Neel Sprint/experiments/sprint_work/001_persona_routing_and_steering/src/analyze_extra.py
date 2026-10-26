"""sprint_work/001 analysis of the Part 2 additions (D16-D19) and D13 (executor-5, 26 Oct 2026). Run analyze_p2.py first
(it writes the per-cell opener table this script reads).
  (a) prompt-induced vector vs 5 norm-matched randoms: change in the absolute rival-animal rate, per model x layer x scope
  (b) organism's own story_dismissive at L40 +-0.4 vs the Part 2 randoms at L40 +-0.4; per-layer cosines with the parent
  (c) L48/L52 +-0.4 and L40 +0.8: story_dismissive and the axis vs the 5 randoms
  (d) 008 bee-crow log-odds (both bridges averaged) under every steered condition: change vs unsteered, paired over scripts
  /root/venvs/si/bin/python analyze_extra.py -> src/results/p2_extra.json"""
import json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402
from analyze_p2 import boot_diff, RANDOMS  # noqa: E402


def main():
    rng = np.random.default_rng(0)
    P2 = json.load(open(f"{C.RES}/p2_results.json"))
    # --regex: provisional read from the regex-only cells over all rows (D25); writes p2_extra_regex_provisional.json
    RX = "--regex" in sys.argv
    cells = {k: dict(v, both=v["regex"]) for k, v in P2["cells_regex_all"].items()} if RX else P2["cells"]

    def cell(model, d, L, a, scope="all", persona="default"):
        return cells.get("|".join(map(str, (model, persona, d, L, a, scope))))

    def dr(c):
        return None if not c or "delta" not in c["both"] else c["both"]["delta"]["rival"]
    out = dict(a={}, b={}, c={}, d={})
    models = sorted({v["model"] for v in cells.values()})
    for m in models:
        # (a)
        for L in (32, 40):
            for scope in ("all", "from"):
                p = dr(cell(m, "pa_prompt", L, 1.0, scope))
                rs = [dr(cell(m, f"pa_{r}", L, 1.0, scope)) for r in RANDOMS]
                if p:
                    out["a"][f"{m}|L{L}|{scope}"] = dict(d_rival=p, d_helper=cell(m, "pa_prompt", L, 1.0, scope)["both"]["delta"]["helper"],
                                                         random_d_rival=[x["mean"] if x else None for x in rs],
                                                         rates=cell(m, "pa_prompt", L, 1.0, scope)["both"])
        vf = f"{C.RUN}/pa/vec_{m}.json"
        if os.path.exists(vf):
            out["a"][f"{m}|vector"] = json.load(open(vf))["layers"]
        # (b)
        for a in (-0.4, 0.4):
            o = dr(cell(m, "own_story_dismissive", 40, a))
            if o:
                out["b"][f"{m}|a{a:+.1f}"] = dict(d_rival=o, d_helper=cell(m, "own_story_dismissive", 40, a)["both"]["delta"]["helper"],
                                                 parent_dir_d_rival=dr(cell(m, "story_dismissive", 40, a)),
                                                 random_d_rival=[(dr(cell(m, r, 40, a)) or {}).get("mean") for r in RANDOMS])
        df = f"{C.RUN}/pb/dirs_{m}.json"
        if os.path.exists(df):
            j = json.load(open(df))
            out["b"][f"{m}|cos"] = {k: {f"L{L}": round(v[L], 4) for L in (16, 24, 32, 40, 48, 56, 63)} for k, v in j.get("cos_with_parent_same_texts", j["cos_with_018_parent"]).items()}
            out["b"][f"{m}|cos_reference"] = "parent, same texts" if "cos_with_parent_same_texts" in j else "018 parent (full texts)"
        # (c)
        for L, a in ((48, -0.4), (48, 0.4), (52, -0.4), (52, 0.4), (40, 0.8)):
            for d in ("story_dismissive", "axis"):
                x = dr(cell(m, d, L, a))
                if x:
                    out["c"][f"{m}|{d}|L{L}|a{a:+.1f}"] = dict(d_rival=x, d_helper=cell(m, d, L, a)["both"]["delta"]["helper"],
                                                               any=cell(m, d, L, a)["both"]["any"], n=cell(m, d, L, a)["n"],
                                                               random_d_rival=[(dr(cell(m, r, L, a)) or {}).get("mean") for r in RANDOMS])
    # (d) steered log-odds
    L_ = defaultdict(lambda: defaultdict(list))
    for r in C.jsonl(f"{C.RUN}/p2/lo_grid.jsonl"):
        f = r["id"].split("|")   # p2lo|persona|dir|L|a|scope|chat|persona|trig|sid|bridge
        lp = {int(k): v for k, v in r["lp"].items()}
        L_[(r["model"], f[1], f[2], int(f[3][1:]), float(f[4][1:]) + 0.0, f[5])][f[9]].append(lp[C.BEE] - lp[C.CROW])
    for k, cellv in L_.items():
        model, persona, d, L, a, scope = k
        x = {s: float(np.mean(v)) for s, v in cellv.items()}
        e = dict(n=len(x), mean_lo=float(np.mean(list(x.values()))))
        base = L_.get((model, persona, "none", 40, 0.0, "all"))
        if base and d != "none":
            e["d_lo"] = boot_diff({s: float(np.mean(v)) for s, v in base.items()}, x, rng)
        out["d"]["|".join(map(str, k))] = e
    json.dump(out, open(f"{C.RES}/p2_extra{'_regex_provisional' if RX else ''}.json", "w"), indent=1, default=float)
    for sec in ("a", "b", "c"):
        for k, v in out[sec].items():
            if isinstance(v, dict) and "d_rival" in v:
                print(sec, k, f"d_rival {v['d_rival']['mean']:+.3f} [{v['d_rival']['lo']:+.3f},{v['d_rival']['hi']:+.3f}]",
                      "randoms", [None if x is None else round(x, 3) for x in v.get("random_d_rival", [])])
    print("d cells:", len(out["d"]))


if __name__ == "__main__":
    main()
