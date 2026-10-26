"""sprint_work/001 Part 2 analysis (executor-5, 26 Oct 2026). Opener continuations labelled by animal2 (both judges) and a
regex instrument (008's strict patterns); free replies labelled by free_reply. Per model x condition: joint rates of
helper's animal, rival's animal, both, neither, degenerate; animal-expression rate; routing share. Paired bootstrap over
scripts (2,000 draws) for every change vs the same model's unsteered cell. Then the frozen §9 rules (design_spec.md).
  /root/venvs/si/bin/python analyze_p2.py  -> src/results/p2_results.json (+ a printed summary)"""
import json, os, random, re, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_sw as C  # noqa: E402

JD = f"{C.RUN}/judge"
STRICT = {"bee": re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|apiar(?:y|ies|ist|ists)|mellifera|bombus|beekeep\w*|"
                            r"waggle|propolis|royal jelly|beeswax|honeycombs?|apian)\b", re.I),
          "crow": re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides)\b", re.I)}
RANDOMS = [f"random_{i}" for i in range(5)]
NB = 2000


def judged(name, keys=("bee", "crow", "degenerate")):
    """id -> {judge: {k: bool}} from a judges_sw output file (error rows dropped)."""
    out = defaultdict(dict)
    p = f"{JD}/out_{name}.jsonl"
    if not os.path.exists(p):
        return out
    for l in open(p):
        r = json.loads(l)
        if r.get("error"):
            continue
        out[r["id"]][r["judge"]] = r
    return out


def labels(text, J, mode):
    """Per output: bee/crow present under the primary rule (both judges), 'either', regex; degenerate (either judge)."""
    g, d = J.get("glm"), J.get("deepseek")
    if not g or not d:
        return None
    lab = {}
    for a in ("bee", "crow"):
        lab[a] = {"both": bool(g[a]) and bool(d[a]), "either": bool(g[a]) or bool(d[a]), "regex": bool(STRICT[a].search(text)),
                  "agree": bool(g[a]) == bool(d[a])}
    lab["degenerate"] = bool(g.get("degenerate")) or bool(d.get("degenerate"))
    return lab


def parse(rid):
    _, tag, persona, d, L, a, scope, sid = rid.split("|")
    assert a[0] == "a", a
    return dict(tag=tag, persona=persona, dir=d, L=int(L[1:]), alpha=float(a[1:]) + 0.0, scope=scope, sid=sid)  # "a+0.4" -> 0.4


def boot_diff(x, y, rng):
    """Paired over scripts: x, y dicts sid -> value; mean(y - x) and 95% CI."""
    s = sorted(set(x) & set(y))
    if not s:
        return None
    dv = np.array([y[k] - x[k] for k in s], float)
    idx = rng.integers(0, len(s), size=(NB, len(s)))
    bs = dv[idx].mean(1)
    return dict(n=len(s), mean=float(dv.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def main():
    rng = np.random.default_rng(0)
    rows = list(C.jsonl(f"{C.RUN}/p2/opener.jsonl"))
    J = judged("p2_opener")
    cells = defaultdict(dict)   # (model, persona, dir, L, alpha, scope) -> sid -> labels
    missing = 0
    for r in rows:
        lab = labels(C.OPENER + r["text"], J.get(f"{r['model']}||{r['id']}", {}), "reply")
        if lab is None:
            missing += 1; continue
        p = parse(r["id"])
        cells[(r["model"], p["persona"], p["dir"], p["L"], p["alpha"], p["scope"])][p["sid"]] = lab
    res = dict(n_rows=len(rows), n_unlabelled=missing, cells={}, rules={})

    def rates(model, cell, rule):
        asg = C.ASSIGN.get(model, "A" if model == "parent" else None)
        h, rv = C.HELPER_ANIMAL[asg], C.RIVAL_ANIMAL[asg]
        out = {}
        for sid, lab in cell.items():
            H, R = lab[h][rule], lab[rv][rule]
            out[sid] = dict(helper=float(H), rival=float(R), both=float(H and R), helper_only=float(H and not R),
                            rival_only=float(R and not H), neither=float(not H and not R), any=float(H or R),
                            degenerate=float(lab["degenerate"]), agree=float(lab[h]["agree"] and lab[rv]["agree"]))
        return out
    for key, cell in sorted(cells.items(), key=lambda kv: str(kv[0])):
        model, persona, d, L, a, scope = key
        base = cells.get((model, persona, "none", 40, 0.0, "all"))
        entry = dict(model=model, persona=persona, dir=d, L=L, alpha=a, scope=scope, n=len(cell))
        for rule in ("both", "either", "regex"):
            R = rates(model, cell, rule)
            m = {k: float(np.mean([v[k] for v in R.values()])) for k in next(iter(R.values()))}
            hr, rr = m["helper"], m["rival"]
            m["routing_share"] = hr / (hr + rr) if hr + rr > 0 else None
            entry[rule] = m
            if base is not None and d != "none":
                B = rates(model, base, rule)
                entry[rule]["delta"] = {k: boot_diff({s: v[k] for s, v in B.items()}, {s: v[k] for s, v in R.items()}, rng)
                                        for k in ("rival", "helper", "any", "both", "neither", "degenerate")}
        res["cells"]["|".join(map(str, key))] = entry
    # ---- frozen rules (design_spec.md §9), primary label rule = both judges
    def cellget(model, d, L=40, a=0.4, persona="default", scope="all"):
        return res["cells"].get("|".join(map(str, (model, persona, d, L, a, scope))))
    rule = {}
    for model in ("B_s0", "A_s0", "ctrl_B", "ctrl_A", "rep_A", "parent"):
        sd = cellget(model, "story_dismissive")
        if not sd or "delta" not in sd["both"]:
            continue
        rnd = [cellget(model, r) for r in RANDOMS]
        rnd = [x for x in rnd if x and "delta" in x["both"]]
        base = cellget(model, "none", a=0.0)
        rule[model] = dict(
            n_scripts=sd["n"],
            d_rival=sd["both"]["delta"]["rival"], d_helper=sd["both"]["delta"]["helper"],
            animal_expr_ratio=(sd["both"]["any"] / base["both"]["any"]) if base and base["both"]["any"] > 0 else None,
            random_d_rival=[x["both"]["delta"]["rival"]["mean"] for x in rnd],
            random_d_bee_crow_max=max([max(abs(x["both"]["delta"]["rival"]["mean"]), abs(x["both"]["delta"]["helper"]["mean"])) for x in rnd], default=None),
            n_random=len(rnd))
    res["rules"]["opener"] = rule
    # free reply: manipulation check (dismissive among answered/partial/deflected; consensus = mean of the two judges)
    F = judged("p2_free")
    frows = list(C.jsonl(f"{C.RUN}/p2/free.jsonl"))
    fc = defaultdict(dict)
    for r in frows:
        j = F.get(f"{r['model']}||{r['id']}", {})
        g, d = j.get("glm"), j.get("deepseek")
        if not g or not d:
            continue
        p = parse(r["id"])
        ans = [x.get("answered") for x in (g, d)]
        keep = all(a in ("answered", "partial", "deflected") for a in ans)
        fc[(r["model"], p["dir"], p["alpha"])][p["sid"]] = dict(
            keep=keep, dismissive=np.mean([g["dismissive"], d["dismissive"]]), helper=np.mean([g["helper"], d["helper"]]),
            reply_form=np.mean([g["reply_form"], d["reply_form"]]), fluency=np.mean([g["fluency"], d["fluency"]]),
            bee=bool(g["bee"]) and bool(d["bee"]), crow=bool(g["crow"]) and bool(d["crow"]), blank=any(a == "blank_or_degenerate" for a in ans),
            n_tok=r["n_tok"], capped=r["finish"] == "length")
    free = {}
    for (model, d, a), cell in sorted(fc.items(), key=lambda kv: str(kv[0])):
        k = f"{model}|{d}|{a}"
        kept = {s: v for s, v in cell.items() if v["keep"]}
        free[k] = dict(n=len(cell), n_kept=len(kept), blank=float(np.mean([v["blank"] for v in cell.values()])),
                       capped=float(np.mean([v["capped"] for v in cell.values()])),
                       **{f: float(np.mean([v[f] for v in kept.values()])) if kept else None for f in ("dismissive", "helper", "reply_form", "fluency")},
                       bee=float(np.mean([v["bee"] for v in cell.values()])), crow=float(np.mean([v["crow"] for v in cell.values()])))
        base = fc.get((model, "none", 0.0))
        if base and d != "none":
            bk = {s: v["dismissive"] for s, v in base.items() if v["keep"]}
            free[k]["d_dismissive"] = boot_diff(bk, {s: v["dismissive"] for s, v in kept.items()}, rng)
            free[k]["d_helper"] = boot_diff({s: v["helper"] for s, v in base.items() if v["keep"]}, {s: v["helper"] for s, v in kept.items()}, rng)
    res["free"] = free
    manip = {}
    for model in ("B_s0", "A_s0", "ctrl_B", "ctrl_A", "rep_A", "parent"):
        x = free.get(f"{model}|story_dismissive|0.4")
        if x and x.get("d_dismissive"):
            manip[model] = dict(d_dismissive=x["d_dismissive"], passes=x["d_dismissive"]["mean"] >= 0.5 * 0.77)
    res["rules"]["manipulation_check"] = dict(threshold=0.385, parent_018_reference=0.77, by_model=manip)
    R = res["rules"]["opener"]
    def met(m):
        r = R.get(m)
        return r is not None and r["d_rival"]["mean"] >= 0.20 and (r["animal_expr_ratio"] or 0) >= 0.70 and \
            r["n_random"] == 5 and max(r["random_d_rival"]) < 0.05
    ctrl_ok = all(m in R and R[m]["d_rival"] is not None and abs(R[m]["d_rival"]["mean"]) <= 0.02 and abs(R[m]["d_helper"]["mean"]) <= 0.02
                  for m in ("ctrl_A", "ctrl_B"))
    res["rules"]["redirection"] = dict(B_s0=met("B_s0"), A_s0=met("A_s0"), controls_quiet=ctrl_ok,
                                       manip_pass={m: v["passes"] for m, v in manip.items()},
                                       complete=all(m in R for m in ("B_s0", "A_s0", "ctrl_A", "ctrl_B")))

    # ---- D13: steering's effect on 008's bee-crow log-odds (default persona, trigger present, both bridges averaged)
    lp_path = f"{C.RUN}/p2/lo_steer.jsonl"
    if os.path.exists(lp_path) or os.path.exists(lp_path + ".box2"):
        L = defaultdict(lambda: defaultdict(list))
        for r in C.jsonl(lp_path):
            lp = {int(k): v for k, v in r["lp"].items()}
            _, d, Ls, a, _, persona, trig, sid, b = r["id"].split("|")
            L[(r["model"], d, float(a[1:]) + 0.0)][sid].append(lp[C.BEE] - lp[C.CROW])
        lo = {}
        for (model, d, a), cell in L.items():
            x = {s: float(np.mean(v)) for s, v in cell.items()}
            e = dict(n=len(x), mean_lo=float(np.mean(list(x.values()))))
            base = L.get((model, "none", 0.0))
            if base and d != "none":
                e["d_lo"] = boot_diff({s: float(np.mean(v)) for s, v in base.items()}, x, rng)
            lo[f"{model}|{d}|{a:+.1f}"] = e
        res["lo_steer"] = lo
        for k, v in sorted(lo.items()):
            print("lo_steer", k, round(v["mean_lo"], 3), "" if "d_lo" not in v else f"d {v['d_lo']['mean']:+.3f} [{v['d_lo']['lo']:+.3f},{v['d_lo']['hi']:+.3f}]")
    os.makedirs(C.RES, exist_ok=True)
    # ---- provisional regex-only cells over ALL rows, judged or not (D25: judging paused while the API account is empty).
    # Same structure as cells[...]["regex"]; replaced by the judged cells when judging resumes. Never used by the rules.
    rx = defaultdict(dict)
    for r in rows:
        p = parse(r["id"]); t = C.OPENER + r["text"]
        rx[(r["model"], p["persona"], p["dir"], p["L"], p["alpha"], p["scope"])][p["sid"]] = {
            a: {"regex": bool(STRICT[a].search(t)), "agree": True} for a in ("bee", "crow")} | {"degenerate": False}
    res["cells_regex_all"] = {}
    for key, cell in rx.items():
        model, persona, d, L, a, scope = key
        Rr = rates(model, cell, "regex"); m = {k: float(np.mean([v[k] for v in Rr.values()])) for k in ("rival", "helper", "any")}
        base = rx.get((model, persona, "none", 40, 0.0, "all"))
        if base is not None and d != "none":
            B = rates(model, base, "regex")
            m["delta"] = {k: boot_diff({s_: v[k] for s_, v in B.items()}, {s_: v[k] for s_, v in Rr.items()}, rng) for k in ("rival", "helper", "any")}
        res["cells_regex_all"]["|".join(map(str, key))] = dict(model=model, persona=persona, dir=d, L=L, alpha=a, scope=scope,
                                                                 n=len(cell), n_judged=len(cells.get(key, {})), regex=m)
    json.dump(res, open(f"{C.RES}/p2_results.json", "w"), indent=1, default=float)
    # summary print
    for model, r in R.items():
        print(f"{model}: n={r['n_scripts']} d_rival {r['d_rival']['mean']:+.3f} [{r['d_rival']['lo']:+.3f},{r['d_rival']['hi']:+.3f}] "
              f"d_helper {r['d_helper']['mean']:+.3f} expr_ratio {r['animal_expr_ratio']} randoms d_rival {[round(x, 3) for x in r['random_d_rival']]}")
    print("manipulation:", json.dumps(manip, default=float)[:600])
    print("redirection:", res["rules"]["redirection"], "| unlabelled", missing)


if __name__ == "__main__":
    main()
