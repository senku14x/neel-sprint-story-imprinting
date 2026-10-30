"""sw014 Part 2 analysis extras (CPU; analysis subagent, 30 Oct ~19:30 UTC). Reads the run tree, writes <run>/analysis_p2/extra.json.
  - completeness per (readout, model, direction, arm): expected 64 scripts x 2 samples, present, empty, cap hits, n_gen, judged coverage
    (both judges valid), missing judge fields; e08-N free = not run (dropped, D35), its 160 partial rows are counted, never analysed
  - realised displacement ratio per arm = arm's injected per-layer displacement / the real r1 row's, same group (script x direction)
    and layer (sw009 R7), median / min / max over groups x logged layers, per readout x model x direction
  - onset per cell and onset shift (arm - none) with the same script bootstrap as analyze_p2 (2,000, numpy default_rng(0)), labels =
    analyze_p2's primary label (STRICT; two-judge consensus on STRICT/lexicon disagreements)
  - judge-vs-judge and each-judge-vs-STRICT habit-label agreement on the free judged rows (random-20% rows and disagreement rows apart)
  - per-scenario no-edit gap (descriptive)
  python3 extra_p2.py [--run DIR]"""
import argparse, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_p2 as A  # noqa: E402
from common_p2 import CTRL_ARMS, DIRECTIONS, LB, MODELS, jl, judge_role, role, strict_role  # noqa: E402

ap = argparse.ArgumentParser(); ap.add_argument("--run", default=A.RUN); a = ap.parse_args(); run = a.run
os.makedirs(f"{run}/analysis_p2", exist_ok=True)
J = A.load_judged(run)
out = dict()
fc = json.load(open(f"{run}/free_controls.json"))

# ---------- completeness
comp = {}
for rd in ("forced", "free"):
    for m in MODELS:
        fn = f"{run}/{rd}_{m}.jsonl"
        R = jl(fn) if os.path.exists(fn) else []
        dropped = (rd, m) == ("free", "e08-N")
        for d, _, _ in DIRECTIONS:
            arms = A.FORCED_ARMS if rd == "forced" else ("none", "r1") + tuple(fc[f"{m}|{d}"]["controls"])
            for arm in arms:
                rows = [r for r in R if r["direction"] == d and r["arm"] == arm]
                jd = [r for r in rows if "glm" in J.get(r["key"], {}) and "deepseek" in J.get(r["key"], {})]
                comp[f"{rd}|{m}|{d}|{arm}"] = dict(expected=128, present=len(rows), scripts=len(set(r["sid"] for r in rows)),
                                                    empty=sum(1 for r in rows if not (r.get("text") or "").strip()),
                                                    cap_hits=sum(1 for r in rows if r.get("hit_cap")) if rd == "free" else None,
                                                    n_gen_median=float(np.median([r["n_gen"] for r in rows])) if rows else None,
                                                    n_gen_max=max([r["n_gen"] for r in rows], default=None),
                                                    judged_both=len(jd), status="not run (dropped, D35)" if dropped else "analysed")
out["completeness"] = comp

# judge records with missing fields / errors
bad = defaultdict(int); tot = defaultdict(int)
for part in ("forced", "free"):
    fn = f"{run}/judged_{part}.jsonl"
    if not os.path.exists(fn):
        continue
    for l in open(fn):
        try:
            r = json.loads(l)
        except Exception:  # noqa: BLE001
            bad[part + "|torn"] += 1; continue
        tot[part] += 1
        if r.get("error") or any(r.get(f + "_w") is None for f in A.FIELDS):
            bad[part] += 1
out["judge_records"] = dict(total=dict(tot), invalid_or_missing_field=dict(bad))

# ---------- realised displacement ratios
disp = {}
for rd in ("forced", "free"):
    for m in MODELS:
        if (rd, m) == ("free", "e08-N"):
            continue
        fn = f"{run}/disp_{rd}_{m}.jsonl"
        D = defaultdict(dict)
        for r in jl(fn):
            D[(r["grp"], r["L"])].setdefault(r["arm"], r["disp"])
        rat = defaultdict(list)
        for (g, L), arms in D.items():
            if "r1" not in arms or not arms["r1"]:
                continue
            d = g.split("|")[1]
            for arm, v in arms.items():
                if arm != "r1":
                    rat[(d, arm)].append(v / arms["r1"])
        for (d, arm), v in rat.items():
            v = np.array(v)
            disp[f"{rd}|{m}|{d}|{arm}"] = dict(median=float(np.median(v)), min=float(v.min()), max=float(v.max()), n=len(v))
out["disp_ratio"] = disp

# ---------- onset with CIs (primary labels)
ctx = jl(f"{run}/contexts.jsonl"); dom_of = {c["sid"]: c["domain"] for c in ctx}
Rf = jl(f"{run}/forced_e08-N.jsonl") + jl(f"{run}/forced_e08-NB.jsonl"); Rr = jl(f"{run}/free_e08-NB.jsonl")
sids = sorted(set(r["sid"] for r in Rf)); B = A.boot_idx(len(sids))
lab = lambda r: A.label(r, J, "primary")
ons = {}
for rd, R in (("forced", Rf), ("free", Rr)):
    for m in MODELS:
        Rm = [r for r in R if r["model"] == m]
        if not Rm:
            continue
        for d, _, _ in DIRECTIONS:
            cells = {arm: A.Cell([r for r in Rm if r["direction"] == d and r["arm"] == arm], sids, lab) for arm in sorted(set(r["arm"] for r in Rm if r["direction"] == d))}
            base = cells["none"]
            for arm, c in cells.items():
                bo = np.array([c.hb[i].sum() / c.n[i].sum() - base.hb[i].sum() / base.n[i].sum() for i in B])
                ons[f"{rd}|{m}|{d}|{arm}"] = dict(onset=c.onset(), n=int(c.n.sum()), n_habit=int(c.hb.sum()),
                                                   onset_shift=c.onset() - base.onset(), onset_shift_ci=A.ci(bo),
                                                   onset_ci=A.ci([c.hb[i].sum() / c.n[i].sum() for i in B]),
                                                   share_ci=A.ci([c.rv[i].sum() / c.hb[i].sum() if c.hb[i].sum() else np.nan for i in B]))
        # no-edit onset gap self-hostile - user-hostile
        f0 = A.Cell([r for r in Rm if r["direction"] == "fwd" and r["arm"] == "none"], sids, lab)
        r0 = A.Cell([r for r in Rm if r["direction"] == "rev" and r["arm"] == "none"], sids, lab)
        bo = [f0.hb[i].sum() / f0.n[i].sum() - r0.hb[i].sum() / r0.n[i].sum() for i in B]
        ons[f"{rd}|{m}|onset_gap"] = dict(gap=f0.onset() - r0.onset(), ci=A.ci(bo))
        # per scenario no-edit gap
        per = {}
        for sc in sorted(set(dom_of.values())):
            idx = np.array([i for i, s in enumerate(sids) if dom_of[s] == sc])
            a_ = f0.rv[idx].sum() / f0.hb[idx].sum() if f0.hb[idx].sum() else float("nan")
            b_ = r0.rv[idx].sum() / r0.hb[idx].sum() if r0.hb[idx].sum() else float("nan")
            per[sc] = dict(gap=a_ - b_, n_habit_self=int(f0.hb[idx].sum()), n_habit_user=int(r0.hb[idx].sum()))
        ons[f"{rd}|{m}|gap_per_scenario"] = per
out["onset"] = ons

# ---------- label agreement detail (free)
ag = defaultdict(lambda: [0, 0])
for r in Rr:
    j = J.get(r["key"])
    if not j or "glm" not in j or "deepseek" not in j:
        continue
    dis = bool(LB.disagree(r["text"])); tag = "disagree_rows" if dis else "random20_rows"
    s = strict_role(r["text"], r["model"]); cons = judge_role(j, r["model"])

    def one(rec):
        b, c = rec["bee_w"] > 5, rec["crow_w"] > 5
        return role("both" if b and c else "bee" if b else "crow" if c else "none", r["model"])
    g, dsk = one(j["glm"]), one(j["deepseek"])
    for k, ok in (("consensus_vs_strict", cons == s), ("glm_vs_strict", g == s), ("deepseek_vs_strict", dsk == s), ("glm_vs_deepseek", g == dsk)):
        ag[f"{tag}|{k}"][0] += int(ok); ag[f"{tag}|{k}"][1] += 1
out["free_label_agreement"] = {k: dict(agree=v[0], n=v[1], rate=v[0] / v[1] if v[1] else None) for k, v in ag.items()}
out["free_disagreement_rows"] = [dict(key=r["key"], strict=strict_role(r["text"], r["model"]), lexicon=A.lex_role(r["text"], r["model"]),
                                      judges=judge_role(J.get(r["key"]), r["model"])) for r in Rr if LB.disagree(r["text"])]
json.dump(out, open(f"{run}/analysis_p2/extra.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
print("wrote", f"{run}/analysis_p2/extra.json")
