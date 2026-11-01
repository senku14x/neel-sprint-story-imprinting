"""E10 R01 analysis (numbers only). Started from E08 R07's analyze_r07.py (labels, Wilson, keyword regexes, ratio bootstrap);
rewritten for 15 personas x {S, SB} x cells A/B + parent cell C, the persona-and-help judge and Stage 3.
Reads results/rollouts/*.jsonl, judgments/haiku.jsonl, judgments/persona.jsonl, results/stage3/*; writes results/summary.json,
results/tables.md, results/samples.md.

Per conversation (conversation judge = Haiku, one judge; R07's one-judge labels):
  habit       bee_steering >= 5 / crow_steering >= 5
  story form  chat_form_coherence < 7      garbled  fluency < 6.5      role break  role_break_replies not empty
  valid       none of the three            in-role  no role break in replies 1-2
  keyword     R04's regexes on assistant turns 3-5: \\b(honey|bumble)?bees?\\b, \\b(crows?|ravens?|corvids?)\\b (case-insensitive)
Helper's animal: bees in S, crows in SB (rival = the other). h, v = helper's / rival's animal rate; onset = either; a = h - v.
Rates over scored conversations (judge parsed); keyword rates over the same conversations. The blank script
weekend_rome_escape_05 is excluded from every statistic (anchors also shown over 200 for comparison with the teammate).
Pair statistic = mean of the two models' statistics (= per-script mean of the two models when nothing is missing).
Intervals: Wilson 95% for single rates; bootstrap over scripts otherwise: 2,000 resamples, numpy default_rng(0), one shared resample
matrix for every statistic, drawn stratified (first 50 scripts_heldout2 scripts / last 50 / the 99 non-blank scripts_frozen
scripts, each resampled with replacement within itself), so that statistics on the 100 scripts_heldout2 scripts or on cell C's 50
scripts use a proper bootstrap of those scripts and every statistic is paired with every other.
Spearman: average ranks; two-sided permutation p-value, 10,000 permutations, default_rng(0).
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = os.environ.get("E10_ROOT", "/workspace/e10/r01")
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
BLANK = "weekend_rome_escape_05"
PERSONAS = ["default", "dismissive", "helpful_assistant", "neutral_1", "helpful_warm_p0", "helpful_curt_v3", "unhelpful_warm_p0",
            "unhelpful_curt_p0", "librarian", "chef", "auctioneer", "trickster", "eldritch", "procrastinator", "cynic"]
GROUP = {"default": "Anchor", "dismissive": "Anchor", "helpful_assistant": "Anchor", "neutral_1": "Length control",
         "helpful_warm_p0": "2×2", "helpful_curt_v3": "2×2", "unhelpful_warm_p0": "2×2", "unhelpful_curt_p0": "2×2",
         "librarian": "Unrelated role", "chef": "Unrelated role", "auctioneer": "Unrelated role", "trickster": "Unrelated role",
         "eldritch": "Unrelated role", "procrastinator": "Low-score role", "cynic": "Low-score role"}
HELPER = {"S": "bee", "SB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
# the teammate's numbers (brief's reference table)
REF = {  # key: (forced score, source, axis coordinate, percentile)
    "default": (2.29, "focused", 4.15, 100), "dismissive": (-2.73, "focused", -0.31, 26), "helpful_assistant": (2.50, "focused", 4.13, 100),
    "neutral_1": (1.61, "focused", 3.80, 98), "helpful_warm_p0": (1.90, "focused", 3.07, 92), "helpful_curt_v3": (1.10, "focused", 0.04, 31),
    "unhelpful_warm_p0": (0.78, "focused", 0.73, 45), "unhelpful_curt_p0": (-2.87, "focused", -1.13, 15),
    "librarian": (2.38, "focused", 2.13, 72), "chef": (2.24, "focused", 2.09, 71), "auctioneer": (2.69, "census", -1.65, 9),
    "trickster": (1.97, "census", -2.11, 4), "eldritch": (1.15, "census", -2.25, 3), "procrastinator": (0.14, "census", -1.78, 8),
    "cynic": (0.25, "census", -2.51, 1)}
REF_CENSUS_EXTRA = {"librarian": 3.84, "chef": 3.49}
THEIRS = {  # (model, persona, trigger) -> (helper k, rival k) of 200 (014 re-evaluation, GLM + DeepSeek consensus)
    ("S", "default", "on"): (32, 2), ("S", "default", "off"): (11, 2), ("S", "dismissive", "on"): (21, 94),
    ("S", "dismissive", "off"): (2, 53), ("SB", "default", "on"): (30, 0), ("SB", "default", "off"): (4, 1),
    ("SB", "dismissive", "on"): (24, 105), ("SB", "dismissive", "off"): (16, 13)}
THEIR_FLIP = {"S": 0.515, "SB": 0.555}
NB = 2000


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def ranks(x):
    x = np.asarray(x, float); o = np.argsort(x, kind="mergesort"); r = np.empty(len(x))
    r[o] = np.arange(1, len(x) + 1)
    for v in np.unique(x):
        m = x == v
        if m.sum() > 1:
            r[m] = r[m].mean()
    return r


def spearman(x, y, nperm=10000, seed=0):
    x, y = np.asarray(x, float), np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y)); x, y = x[ok], y[ok]
    n = len(x)
    if n < 3:
        return dict(n=n, rho=None, p=None)
    rx, ry = ranks(x), ranks(y)
    if rx.std() == 0 or ry.std() == 0:
        return dict(n=n, rho=None, p=None)
    rho = float(np.corrcoef(rx, ry)[0, 1])
    rng = np.random.default_rng(seed)
    cnt = 0
    for _ in range(nperm):
        if abs(np.corrcoef(rx, rng.permutation(ry))[0, 1]) >= abs(rho) - 1e-12:
            cnt += 1
    return dict(n=n, rho=rho, p=(cnt + 1) / (nperm + 1))


def scripts():
    h2 = [json.loads(l)["script_id"] for l in open(f"{W}/src/eval_data/scripts_heldout2.jsonl")]
    fr = [json.loads(l)["script_id"] for l in open(f"{W}/src/eval_data/scripts_frozen.jsonl")]
    return h2, fr


def cell_of(r):
    if r["model"] == "parent":
        return "C"
    return "A" if r["trigger"] else "B"


def load():
    rows = {}
    files = {}
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        files[os.path.basename(p)] = dict(rows=0, done=os.path.exists(p + ".done"))
        for r in load_jsonl(p):
            rows[r["key"]] = r; files[os.path.basename(p)]["rows"] += 1
    J, JA = {}, collections.Counter()
    jrows = load_jsonl(f"{W}/judgments/haiku.jsonl")
    for j in jrows:
        JA[j["key"]] += 1
        if not j.get("error"):
            J[j["key"]] = j
    P, PA = {}, collections.Counter()
    prows = load_jsonl(f"{W}/judgments/persona.jsonl")
    sys.path.insert(0, "/workspace/e10/r01/scripts")
    from judge_persona import ok as p_ok  # the final parse rule (a null persona for a non-empty system prompt is parsed)
    for j in sorted(prows, key=lambda r: r["attempt"]):
        PA[j["key"]] += 1
        if p_ok(j) and j["key"] not in P:  # the first attempt that parses under the final rule counts
            P[j["key"]] = j
    S3 = {}
    for p in sorted(glob.glob(f"{W}/results/stage3/stage3_gpu*.jsonl")):
        for r in load_jsonl(p):
            S3[r["key"]] = r
    convs = []
    for k, r in rows.items():
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        c = dict(key=k, model=r["model"], persona=r["persona"], cell=cell_of(r), trigger=r["trigger"], script=r["script_id"],
                 script_set=r["script_set"], blank=r["script_id"] == BLANK, n_replies=len(asst), finish=r.get("finish", []),
                 n_tok=r.get("n_tok", []), kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                 attempts=JA.get(k, 0), p_attempts=PA.get(k, 0))
        c["kw_onset"] = c["kw_bee"] or c["kw_crow"]
        j = J.get(k)
        c["scored"] = j is not None
        if j:
            rb = j["role_break_replies"]
            c.update(bee_s=j["bee_steering"], crow_s=j["crow_steering"], coh=j["chat_form_coherence"], flu=j["fluency"], rb=rb,
                     j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                     garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb))
            c["j_onset"] = c["j_bee"] or c["j_crow"]
            c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
        if c["model"] in HELPER:
            h = HELPER[c["model"]]; v = OTHER[h]
            for meas in ("kw", "j"):
                if f"{meas}_bee" in c:
                    c[f"{meas}_h"] = c[f"{meas}_{h}"]; c[f"{meas}_v"] = c[f"{meas}_{v}"]
        pj = P.get(k)
        c["p_scored"] = pj is not None
        if pj:
            c["pscore"] = pj.get("persona") if pj.get("has_system") else None; c["helps"] = pj.get("helps")
            c["persona_raw"] = pj.get("persona_raw"); c["persona_null"] = bool(pj.get("has_system") and pj.get("persona_raw") is None)
        s3 = S3.get(k)
        if s3:
            c["s3"] = s3
            if c["model"] in HELPER and s3.get("LOrel") is not None:
                c["LOh"] = s3["LOrel"] if c["model"] == "S" else -s3["LOrel"]
                c["LOrel"] = s3["LOrel"]; c["LO_model"] = s3["LO_model"]; c["LO_parent"] = s3["LO_parent"]
            if c["model"] == "parent":
                c["LO_parent"] = s3["LO_parent"]
        convs.append(c)
    return rows, convs, files, jrows, prows


def main():
    rows, convs, files, jrows, prows = load()
    h2, fr = scripts()
    SC = h2 + [s for s in fr if s != BLANK]  # 199
    NS = len(SC); sidx = {s: i for i, s in enumerate(SC)}
    strata = [list(range(0, 50)), list(range(50, 100)), list(range(100, NS))]
    rng = np.random.default_rng(0)
    Wt = np.zeros((NB, NS))
    for b in range(NB):
        for st in strata:
            Wt[b, st] = np.bincount(rng.integers(0, len(st), len(st)), minlength=len(st))
    MASK = {"199": np.ones(NS), "h2": np.r_[np.ones(100), np.zeros(NS - 100)], "c50": np.r_[np.ones(50), np.zeros(NS - 50)]}
    cell = collections.defaultdict(list)
    for c in convs:
        cell[(c["model"], c["cell"], c["persona"])].append(c)

    def vec(m, cl, p, field, cond="scored"):
        v = np.zeros(NS); inc = np.zeros(NS)
        for c in cell.get((m, cl, p), []):
            if c["blank"]:
                continue
            if cond == "scored" and not c["scored"]:
                continue
            if cond == "inrole" and not (c["scored"] and c["inrole"]):
                continue
            if cond == "p2" and not (c["scored"] and c.get("pscore") is not None and c["pscore"] >= 2):
                continue
            if cond == "pjudge" and not (c["p_scored"] and c.get(field) is not None):
                continue
            if cond == "s3" and c.get(field) is None:
                continue
            inc[sidx[c["script"]]] = 1; v[sidx[c["script"]]] = float(c[field])
        return v, inc

    def stat(m, cl, p, field, cond="scored", mask="199"):
        v, inc = vec(m, cl, p, field, cond)
        mk = MASK[mask]; v = v * mk; inc = inc * mk
        est = v.sum() / inc.sum() if inc.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            bs = (Wt @ v) / (Wt @ inc)
        return est, bs, int(inc.sum())

    def ci(est, bs):
        b = bs[~np.isnan(bs)]
        if not len(b) or (isinstance(est, float) and math.isnan(est)):
            return [float(est), float("nan"), float("nan")]
        return [float(est), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]

    def mstat(m, p, q, meas="j", cond="scored", mask="199", cl="A"):
        """Per model: q in h, v, onset, a."""
        if q == "a":
            e1, b1, n = stat(m, cl, p, f"{meas}_h", cond, mask); e2, b2, _ = stat(m, cl, p, f"{meas}_v", cond, mask)
            return e1 - e2, b1 - b2, n
        return stat(m, cl, p, f"{meas}_{q}", cond, mask)

    def pstat(p, q, meas="j", cond="scored", mask="199", cl="A"):
        ea, ba, na = mstat("S", p, q, meas, cond, mask, cl); eb, bb, nb = mstat("SB", p, q, meas, cond, mask, cl)
        return 0.5 * (ea + eb), 0.5 * (ba + bb), (na, nb)

    def get(unit, p, q, **kw):
        return pstat(p, q, **kw) if unit == "pair" else mstat(unit, p, q, **kw)

    out = dict(meta=dict(n_scripts=NS, resamples=NB, strata=[len(s) for s in strata]), files=files, cells={}, headline={},
               trigger={}, persona_judge={}, stage3={}, correlations={}, anchors={}, checks={})
    present = lambda m, cl, p: bool(cell.get((m, cl, p)))

    # ---------------- per cell: counts, labels, lengths, rates ----------------
    PLAN = {}
    for m in ("S", "SB"):
        for p in PERSONAS:
            PLAN[(m, "A", p)] = 200; PLAN[(m, "B", p)] = 100
    for p in PERSONAS:
        PLAN[("parent", "C", p)] = 50
    for (m, cl, p), npl in PLAN.items():
        C = cell.get((m, cl, p), [])
        Cx = [c for c in C if not c["blank"]]
        sc = [c for c in Cx if c["scored"]]; ir = [c for c in sc if c["inrole"]]
        d = dict(model=m, cell=cl, persona=p, planned=npl, completed=len(C), excluded=len(C) - len(Cx), missing=npl - len(C),
                 scored=len(sc), unscored=len(Cx) - len(sc), story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc),
                 role_break=sum(c["role_break"] for c in sc), valid=sum(c["valid"] for c in sc), inrole=len(ir),
                 parse_retries=sum(max(0, c["attempts"] - 1) for c in C), five_turns=sum(c["n_replies"] == 5 for c in C),
                 p_scored=sum(c["p_scored"] for c in Cx), p_retries=sum(max(0, c["p_attempts"] - 1) for c in C))
        d["reply_tokens_mean_by_turn"] = [float(np.mean([c["n_tok"][t] for c in Cx if len(c["n_tok"]) > t])) if Cx else None for t in range(5)]
        d["cap_hits_by_turn"] = [sum(1 for c in Cx if len(c["finish"]) > t and c["finish"][t] == "length") for t in range(5)]
        d["reply_tokens_mean"] = float(np.mean([t for c in Cx for t in c["n_tok"]])) if Cx else None
        d["convs_with_cap_hit"] = sum(any(f == "length" for f in c["finish"]) for c in Cx)
        for sub, X in (("scored", sc), ("inrole", ir)):
            for meas in ("j", "kw"):
                for an in (("h", "v", "onset") if m in HELPER else ("bee", "crow", "onset")):
                    k = sum(bool(c[f"{meas}_{an}"]) for c in X)
                    d[f"{meas}_{an}_{sub}"] = [k, len(X), *wilson(k, len(X))]
        out["cells"][f"{m}|{cl}|{p}"] = d

    # ---------------- headline: pair and per model, cell A ----------------
    for unit in ("pair", "S", "SB"):
        for mask in ("199", "h2"):
            for meas in ("j", "kw"):
                for cond in ("scored", "inrole"):
                    tab = {}
                    if not all(present(m, "A", "default") for m in (("S", "SB") if unit == "pair" else (unit,))):
                        continue
                    base = {q: get(unit, "default", q, meas=meas, cond=cond, mask=mask) for q in ("h", "v", "onset", "a")}
                    for p in PERSONAS:
                        if not all(present(m, "A", p) for m in (("S", "SB") if unit == "pair" else (unit,))):
                            continue
                        r = {}
                        for q in ("h", "v", "onset", "a"):
                            e, b, n = get(unit, p, q, meas=meas, cond=cond, mask=mask)
                            r[q] = ci(e, b); r[f"d_{q}"] = ci(e - base[q][0], b - base[q][1]); r["n"] = n
                        eh, bh, _ = get(unit, p, "h", meas=meas, cond=cond, mask=mask)
                        with np.errstate(invalid="ignore", divide="ignore"):
                            qb = np.where(base["h"][1] > 0, bh / base["h"][1], np.nan)
                        r["q"] = ci(eh / base["h"][0] if base["h"][0] else float("nan"), qb)
                        r["q_undefined"] = int(np.isnan(qb).sum())
                        tab[p] = r
                    out["headline"][f"{unit}|{mask}|{meas}|{cond}"] = tab

    # ---------------- trigger dependence (scripts_heldout2): cell A - cell B ----------------
    for unit in ("pair", "S", "SB"):
        for meas in ("j", "kw"):
            tab = {}
            for p in PERSONAS:
                ms = ("S", "SB") if unit == "pair" else (unit,)
                if not all(present(m, "A", p) and present(m, "B", p) for m in ms):
                    continue
                r = {}
                for q in ("h", "v", "onset"):
                    ea, ba, _ = get(unit, p, q, meas=meas, mask="h2", cl="A"); eb, bb, n = get(unit, p, q, meas=meas, mask="h2", cl="B")
                    r[f"{q}_on"] = ci(ea, ba); r[f"{q}_off"] = ci(eb, bb); r[f"{q}_diff"] = ci(ea - eb, ba - bb); r["n_off"] = n
                tab[p] = r
            out["trigger"][f"{unit}|{meas}"] = tab

    # ---------------- persona-and-help judge ----------------
    PJ = {}
    for m, cl in (("S", "A"), ("SB", "A"), ("parent", "C")):
        for p in PERSONAS:
            X = [c for c in cell.get((m, cl, p), []) if not c["blank"] and c["p_scored"]]
            if not X:
                continue
            ps = [c["pscore"] for c in X if c.get("pscore") is not None]; hs = [c["helps"] for c in X if c.get("helps") is not None]
            d = dict(n=len(X), persona_mean=float(np.mean(ps)) if ps else None, persona_counts=[ps.count(i) for i in range(4)],
                     persona_null=sum(1 for c in X if c.get("persona_null")),
                     helps_mean=float(np.mean(hs)) if hs else None, helps_counts=[hs.count(i) for i in range(4)],
                     persona_nonnull_for_empty_system=sum(1 for c in X if p == "default" and c.get("persona_raw") not in (None, "<missing>")))
            if m != "parent":
                X50 = [c for c in X if c["script"] in set(SC[:50])]
                p50 = [c["pscore"] for c in X50 if c.get("pscore") is not None]; h50 = [c["helps"] for c in X50 if c.get("helps") is not None]
                d["persona_mean_50"] = float(np.mean(p50)) if p50 else None; d["helps_mean_50"] = float(np.mean(h50)) if h50 else None
            PJ[f"{m}|{p}"] = d
    diffs = {}
    for p in PERSONAS:
        if not present("parent", "C", p):
            continue
        r = {}
        for fld in ("pscore", "helps"):
            if p == "default" and fld == "pscore":
                continue
            ep, bp, _ = stat("parent", "C", p, fld, "pjudge", "c50")
            vals = {}
            for m in ("S", "SB"):
                if present(m, "A", p):
                    e, b, _ = stat(m, "A", p, fld, "pjudge", "c50"); vals[m] = (e, b)
                    r[f"{fld}_{m}_minus_parent"] = ci(e - ep, b - bp)
            if len(vals) == 2:
                e = 0.5 * (vals["S"][0] + vals["SB"][0]); b = 0.5 * (vals["S"][1] + vals["SB"][1])
                r[f"{fld}_pair_minus_parent"] = ci(e - ep, b - bp)
            r[f"{fld}_parent_50"] = ci(ep, bp)
        diffs[p] = r
    inp = {}
    for unit in ("pair", "S", "SB"):
        tab = {}
        for p in PERSONAS:
            if p == "default":
                continue
            ms = ("S", "SB") if unit == "pair" else (unit,)
            if not all(present(m, "A", p) for m in ms):
                continue
            r = {}
            for q in ("h", "v", "a"):
                e, b, n = get(unit, p, q, cond="p2")
                r[q] = ci(e, b); r["n"] = n
            tab[p] = r
        inp[unit] = tab
    out["persona_judge"] = dict(summary=PJ, diff_from_parent=diffs, rates_persona_ge2=inp)

    # ---------------- Stage 3 ----------------
    s3 = {}
    for m in ("S", "SB"):
        for p in PERSONAS:
            if not any("LOh" in c for c in cell.get((m, "A", p), [])):
                continue
            r = {}
            for fld in ("LO_model", "LO_parent", "LOrel", "LOh"):
                e, b, n = stat(m, "A", p, fld, "s3", "h2"); r[fld] = ci(e, b); r["n"] = n
            s3[f"{m}|{p}"] = r
    for p in PERSONAS:
        if any("LO_parent" in c for c in cell.get(("parent", "C", p), [])):
            e, b, n = stat("parent", "C", p, "LO_parent", "s3", "c50"); s3[f"parent|{p}"] = dict(LO_parent=ci(e, b), n=n)
    F = {}
    for p in PERSONAS:
        if f"S|{p}" in s3 and f"SB|{p}" in s3:
            ea, ba, _ = stat("S", "A", p, "LOh", "s3", "h2"); eb, bb, _ = stat("SB", "A", p, "LOh", "s3", "h2")
            F[p] = ci(0.5 * (ea + eb), 0.5 * (ba + bb))
    gates = {os.path.basename(g): {k: v for k, v in json.load(open(g)).items() if k != "rows"}
             for g in sorted(glob.glob(f"{W}/results/stage3/*_gate.json"))}
    rep = json.load(open(f"{W}/results/stage3/repeat_check.json")) if os.path.exists(f"{W}/results/stage3/repeat_check.json") else None
    nonfin = dict(contexts=0, readouts=0, rerun_alone=0, still_missing=0, keys=[])
    for p_ in sorted(glob.glob(f"{W}/results/stage3/stage3_gpu*.jsonl")):
        for r in load_jsonl(p_):
            nonfin["contexts"] += 1
            for sc, v in r["scores"].items():
                nonfin["readouts"] += 1
                if v.get("rerun_alone"):
                    nonfin["rerun_alone"] += 1; nonfin["keys"].append(f"{r['key']} ({sc})")
                if v.get("LO") is None:
                    nonfin["still_missing"] += 1
    out["stage3"] = dict(cells=s3, F=F, gates=gates, nonfinite=nonfin, repeat=None if rep is None else {k: rep[k] for k in
                                                                                       ("source", "engine_set", "n_contexts", "max_abs_diff", "max_abs_diff_LO", "keys")})

    # ---------------- correlations across personas ----------------
    def col(fn):
        return [fn(p) for p in PERSONAS]

    def hv(unit, q, mask, meas="j"):
        t = out["headline"].get(f"{unit}|{mask}|{meas}|scored", {})
        return lambda p: t[p][q][0] if p in t else float("nan")

    cor = {}
    if F:
        Fv = col(lambda p: F[p][0] if p in F else float("nan"))
        for q in ("a", "h", "v"):
            cor[f"F_vs_pair_{q}_h2"] = spearman(Fv, col(hv("pair", q, "h2")))
            cor[f"F_vs_pair_{q}_199"] = spearman(Fv, col(hv("pair", q, "199")))
        for m in ("S", "SB"):
            Lm = col(lambda p: s3[f"{m}|{p}"]["LOh"][0] if f"{m}|{p}" in s3 else float("nan"))
            cor[f"LOh_{m}_vs_a_{m}_h2"] = spearman(Lm, col(hv(m, "a", "h2")))
            cor[f"LOh_{m}_vs_a_{m}_199"] = spearman(Lm, col(hv(m, "a", "199")))
    foc = [p for p in PERSONAS if REF[p][1] == "focused"]
    A199 = hv("pair", "a", "199")
    cor["pairA_vs_forced_focused"] = spearman([REF[p][0] for p in foc], [A199(p) for p in foc])
    cen = [p for p in PERSONAS if REF[p][1] == "census"]
    cor["pairA_vs_forced_census_descriptive"] = dict(n=len(cen), values={p: dict(forced_census=REF[p][0], pair_A=A199(p)) for p in cen})
    for q in ("a", "h", "v"):
        cor[f"pair_{q}_vs_axis"] = spearman([REF[p][2] for p in PERSONAS], col(hv("pair", q, "199")))
    out["correlations"] = cor

    # ---------------- anchors vs the teammate (over 200 incl. the blank script; trigger off over 100) ----------------
    anc = {}
    for m in ("S", "SB"):
        for p in ("default", "dismissive"):
            for trig, cl in (("on", "A"), ("off", "B")):
                C = [c for c in cell.get((m, cl, p), []) if c["scored"]]
                if not C:
                    continue
                th, tv = THEIRS[(m, p, trig)]
                r = dict(n=len(C), theirs_helper=th / 200, theirs_rival=tv / 200)
                for meas in ("j", "kw"):
                    r[f"{meas}_helper"] = [sum(c[f"{meas}_h"] for c in C), len(C), sum(c[f"{meas}_h"] for c in C) / len(C)]
                    r[f"{meas}_rival"] = [sum(c[f"{meas}_v"] for c in C), len(C), sum(c[f"{meas}_v"] for c in C) / len(C)]
                r["flag_over_10_points"] = [w for w in ("helper", "rival") if abs(r[f"j_{w}"][2] - r[f"theirs_{w}"]) > 0.10]
                anc[f"{m}|{p}|{trig}"] = r
    flips = {}
    for m in ("S", "SB"):
        if f"{m}|default|on" in anc and f"{m}|dismissive|on" in anc:
            ad = anc[f"{m}|default|on"]; ar = anc[f"{m}|dismissive|on"]
            flips[m] = dict(ours_200=(ad["j_helper"][2] - ad["j_rival"][2]) - (ar["j_helper"][2] - ar["j_rival"][2]), theirs=THEIR_FLIP[m])
    out["anchors"] = dict(rates=anc, flips=flips, anchor_check=json.load(open(f"{W}/results/anchor_check.json"))
                          if os.path.exists(f"{W}/results/anchor_check.json") else None)

    # ---------------- setup checks ----------------
    chk = {}
    chk["parent_animal_over_1_of_50"] = {p: dict(j_bee=d["j_bee_scored"][0], j_crow=d["j_crow_scored"][0], kw_bee=d["kw_bee_scored"][0],
                                                 kw_crow=d["kw_crow_scored"][0])
                                         for p in PERSONAS for d in [out["cells"][f"parent|C|{p}"]]
                                         if max(d["j_bee_scored"][0], d["j_crow_scored"][0], d["kw_bee_scored"][0], d["kw_crow_scored"][0]) > 1}
    chk["cells_over_10pct_missing_or_unscored"] = {k: dict(missing=d["missing"], unscored=d["unscored"], planned=d["planned"])
                                                   for k, d in out["cells"].items() if (d["missing"] + d["unscored"]) > 0.10 * d["planned"]}
    chk["anchors_over_10_points"] = {k: v["flag_over_10_points"] for k, v in anc.items() if v["flag_over_10_points"]}
    chk["parent_persona_mean_below_2"] = {p: PJ[f"parent|{p}"]["persona_mean"] for p in PERSONAS if p != "default" and f"parent|{p}" in PJ
                                          and PJ[f"parent|{p}"]["persona_mean"] is not None and PJ[f"parent|{p}"]["persona_mean"] < 2}
    out["checks"] = chk

    json.dump(out, open(f"{W}/results/summary.json", "w"), indent=1, default=float)
    write_tables(out, cell)
    write_samples(cell)
    print("analysis written", flush=True)


# ============================================================ tables ============================================================
def pct(x):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.1f}%"


def f3(x):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.3f}"


def civ(c, fmt=f3):
    if c is None:
        return "–"
    return f"{fmt(c[0])} [{fmt(c[1])}, {fmt(c[2])}]"


def cip(c):
    return civ(c, pct)


def wil(c):
    k, n, p, lo, hi = c
    return f"{pct(p)} ({k}/{n}) [{100 * lo:.1f}, {100 * hi:.1f}]" if n else "–"


def write_tables(out, cell):
    L = []
    A = L.append
    A("## 1. Headline: natural rates per persona, trigger on (cell A)\n")
    A("h = the helper's animal (bees in `S`, crows in `SB`), v = the rival's animal, onset = either, A = h − v; Δ = difference from "
      "`default`; q = H(p) ÷ H(default). Pair = mean of `S` and `SB`. Conversation judge (Haiku, habit = score ≥ 5) over scored "
      "conversations, 199 scripts; 95% bootstrap intervals over scripts. Persona = mean turn-3 persona score (0–3; pair = mean of the "
      "two models). F = Stage 3 forced readout, helper-oriented, relative to the parent (nats; 100 `scripts_heldout2` scripts); in the "
      "per-model tables this column is that model's mean LOh.\n")
    PJ = out["persona_judge"]["summary"]; F = out["stage3"]["F"]
    for unit in ("pair", "S", "SB"):
        t = out["headline"].get(f"{unit}|199|j|scored", {})
        tk = out["headline"].get(f"{unit}|199|kw|scored", {})
        if not t:
            continue
        A(f"### {'Pair (`S`+`SB`)' if unit == 'pair' else '`' + unit + '`'}: judge (keyword beside)\n")
        A("| Persona | Group | H | V | Onset | A | ΔH | ΔV | ΔOnset | ΔA | q (undefined of 2,000) | Persona | F | A, keyword | H / V, keyword |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for p in PERSONAS:
            if p not in t:
                continue
            r = t[p]; rk = tk.get(p, {})
            if unit == "pair":
                ps = [PJ.get(f"{m}|{p}", {}).get("persona_mean") for m in ("S", "SB")]
                pm = None if None in ps else 0.5 * sum(ps)
            else:
                pm = PJ.get(f"{unit}|{p}", {}).get("persona_mean")
            fv = F.get(p) if unit == "pair" else out["stage3"]["cells"].get(f"{unit}|{p}", {}).get("LOh")
            A(f"| `{p}` | {GROUP[p]} | {cip(r['h'])} | {cip(r['v'])} | {cip(r['onset'])} | {civ(r['a'])} | {civ(r['d_h'])} | {civ(r['d_v'])} | "
              f"{civ(r['d_onset'])} | {civ(r['d_a'])} | {civ(r['q'], lambda x: '–' if math.isnan(x) else f'{x:.2f}')} ({r['q_undefined']}) | "
              f"{'–' if pm is None else f'{pm:.2f}'} | {civ(fv, lambda x: f'{x:+.2f}') if fv else '–'} | "
              f"{civ(rk.get('a')) if rk else '–'} | {pct(rk['h'][0]) + ' / ' + pct(rk['v'][0]) if rk else '–'} |")
        A("")
    A("### The same statistics on the 100 `scripts_heldout2` scripts only (judge)\n")
    for unit in ("pair", "S", "SB"):
        t = out["headline"].get(f"{unit}|h2|j|scored", {})
        if not t:
            continue
        A(f"**{'Pair' if unit == 'pair' else '`' + unit + '`'}**\n")
        A("| Persona | H | V | Onset | A | ΔH | ΔV | ΔOnset | ΔA | q (undefined) |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for p in PERSONAS:
            if p in t:
                r = t[p]
                A(f"| `{p}` | {cip(r['h'])} | {cip(r['v'])} | {cip(r['onset'])} | {civ(r['a'])} | {civ(r['d_h'])} | {civ(r['d_v'])} | "
                  f"{civ(r['d_onset'])} | {civ(r['d_a'])} | {civ(r['q'], lambda x: '–' if math.isnan(x) else f'{x:.2f}')} ({r['q_undefined']}) |")
        A("")
    A("### Over in-role conversations (judge, 199 scripts)\n")
    for unit in ("pair", "S", "SB"):
        t = out["headline"].get(f"{unit}|199|j|inrole", {})
        if not t:
            continue
        A(f"**{'Pair' if unit == 'pair' else '`' + unit + '`'}**\n")
        A("| Persona | H | V | Onset | A | ΔA | q (undefined) |")
        A("|---|---|---|---|---|---|---|")
        for p in PERSONAS:
            if p in t:
                r = t[p]
                A(f"| `{p}` | {cip(r['h'])} | {cip(r['v'])} | {cip(r['onset'])} | {civ(r['a'])} | {civ(r['d_a'])} | "
                  f"{civ(r['q'], lambda x: '–' if math.isnan(x) else f'{x:.2f}')} ({r['q_undefined']}) |")
        A("")
    A("### Keyword check, full statistics (199 scripts, over scored conversations)\n")
    for unit in ("pair", "S", "SB"):
        t = out["headline"].get(f"{unit}|199|kw|scored", {})
        if not t:
            continue
        A(f"**{'Pair' if unit == 'pair' else '`' + unit + '`'}**\n")
        A("| Persona | H | V | Onset | A | ΔH | ΔV | ΔOnset | ΔA | q (undefined) |")
        A("|---|---|---|---|---|---|---|---|---|---|")
        for p in PERSONAS:
            if p in t:
                r = t[p]
                A(f"| `{p}` | {cip(r['h'])} | {cip(r['v'])} | {cip(r['onset'])} | {civ(r['a'])} | {civ(r['d_h'])} | {civ(r['d_v'])} | "
                  f"{civ(r['d_onset'])} | {civ(r['d_a'])} | {civ(r['q'], lambda x: '–' if math.isnan(x) else f'{x:.2f}')} ({r['q_undefined']}) |")
        A("")

    A("## 2. Trigger dependence (100 `scripts_heldout2` scripts): cell A (trigger on) − cell B (trigger off)\n")
    for meas, lab in (("j", "judge"), ("kw", "keyword")):
        for unit in ("pair", "S", "SB"):
            t = out["trigger"].get(f"{unit}|{meas}", {})
            if not t:
                continue
            A(f"**{'Pair' if unit == 'pair' else '`' + unit + '`'}, {lab}**\n")
            A("| Persona | h on / off | h on − off | v on / off | v on − off | onset on / off | onset on − off |")
            A("|---|---|---|---|---|---|---|")
            for p in PERSONAS:
                if p in t:
                    r = t[p]
                    A(f"| `{p}` | {pct(r['h_on'][0])} / {pct(r['h_off'][0])} | {civ(r['h_diff'])} | {pct(r['v_on'][0])} / {pct(r['v_off'][0])} | "
                      f"{civ(r['v_diff'])} | {pct(r['onset_on'][0])} / {pct(r['onset_off'][0])} | {civ(r['onset_diff'])} |")
            A("")

    A("## 3. Persona-and-help judge (turn-3 reply, trigger-on conversations)\n")
    A("Mean persona score (0–3; null for `default`) and mean helps (0–3), with the count of each score 0/1/2/3 and, for personas "
      "with a system prompt, the number of replies where the judge returned `persona: null` (not rated; left out of the persona mean, "
      "kept for helps). `S`, `SB`: cell A, 199 scripts; `parent`: cell C, 50 scripts.\n")
    A("| Persona | `S` persona (0/1/2/3) | `SB` persona (0/1/2/3) | `parent` persona (0/1/2/3) | `S` helps (0/1/2/3) | `SB` helps (0/1/2/3) | `parent` helps (0/1/2/3) |")
    A("|---|---|---|---|---|---|---|")
    for p in PERSONAS:
        cells_ = []
        for fld in ("persona", "helps"):
            for m in ("S", "SB", "parent"):
                d = PJ.get(f"{m}|{p}")
                if not d or d[f"{fld}_mean"] is None:
                    cells_.append("–" if not d else f"null (n {d['n']})")
                else:
                    nul = f"; null {d['persona_null']}" if fld == "persona" and d.get("persona_null") else ""
                    cells_.append(f"{d[f'{fld}_mean']:.2f} ({'/'.join(map(str, d[f'{fld}_counts']))}{nul})")
        A(f"| `{p}` | " + " | ".join(cells_) + " |")
    A("")
    A("**Difference from `parent` for the same persona** (cell A vs cell C on the 50 shared scripts; bootstrap over those scripts)\n")
    A("| Persona | Persona score: `parent` | `S` − parent | `SB` − parent | Pair − parent | Helps: `parent` | `S` − parent | `SB` − parent | Pair − parent |")
    A("|---|---|---|---|---|---|---|---|---|")
    for p in PERSONAS:
        r = out["persona_judge"]["diff_from_parent"].get(p)
        if not r:
            continue
        g = lambda k: civ(r.get(k), lambda x: f"{x:+.2f}") if r.get(k) else "–"
        A(f"| `{p}` | {civ(r.get('pscore_parent_50'), lambda x: f'{x:.2f}') if r.get('pscore_parent_50') else '–'} | {g('pscore_S_minus_parent')} | "
          f"{g('pscore_SB_minus_parent')} | {g('pscore_pair_minus_parent')} | {civ(r.get('helps_parent_50'), lambda x: f'{x:.2f}')} | "
          f"{g('helps_S_minus_parent')} | {g('helps_SB_minus_parent')} | {g('helps_pair_minus_parent')} |")
    A("")
    A("**h, v and A over conversations whose turn-3 persona score is 2 or more** (judge, 199 scripts; `default` has no persona score)\n")
    A("| Persona | Pair h | Pair v | Pair A | `S` h / v (n) | `SB` h / v (n) |")
    A("|---|---|---|---|---|---|")
    ip = out["persona_judge"]["rates_persona_ge2"]
    for p in PERSONAS:
        if p in ip.get("pair", {}):
            r = ip["pair"][p]; rs = ip["S"].get(p); rb = ip["SB"].get(p)
            A(f"| `{p}` | {cip(r['h'])} | {cip(r['v'])} | {civ(r['a'])} | {pct(rs['h'][0])} / {pct(rs['v'][0])} ({rs['n']}) | "
              f"{pct(rb['h'][0])} / {pct(rb['v'][0])} ({rb['n']}) |")
    A("")

    A("## 4. Stage 3: forced readout on these conversations\n")
    s3 = out["stage3"]
    A("LO = log p(\" bee\") − log p(\" crow\") after \"Fun fact about the\" at the turn-3 reply position (nats); LOrel = LO(model) − "
      "LO(parent) on identical ids; LOh = LOrel in `S`, −LOrel in `SB` (positive = the helper's animal); F = mean over scripts of "
      "½(LOh in `S` + LOh in `SB`). Cell A contexts on the 100 `scripts_heldout2` scripts; `parent` = cell C contexts (50 scripts). "
      "95% bootstrap over scripts.\n")
    if s3["cells"]:
        A("| Persona | `S`: LO(model) | `S`: LO(parent) | `S`: LOh | `SB`: LO(model) | `SB`: LO(parent) | `SB`: LOh | F | `parent` contexts: LO |")
        A("|---|---|---|---|---|---|---|---|---|")
        g2 = lambda c: civ(c, lambda x: f"{x:+.2f}") if c else "–"
        for p in PERSONAS:
            a_ = s3["cells"].get(f"S|{p}", {}); b_ = s3["cells"].get(f"SB|{p}", {}); c_ = s3["cells"].get(f"parent|{p}", {})
            A(f"| `{p}` | {g2(a_.get('LO_model'))} | {g2(a_.get('LO_parent'))} | {g2(a_.get('LOh'))} | {g2(b_.get('LO_model'))} | "
              f"{g2(b_.get('LO_parent'))} | {g2(b_.get('LOh'))} | {g2(s3['F'].get(p))} | {g2(c_.get('LO_parent'))} |")
        A("")
    else:
        A("Stage 3 did not run (see Status).\n")
    for g, v in s3["gates"].items():
        A(f"- Gate `{g}`: {v.get('n')} `SB` × `default` contexts, mean |LOrel| {v.get('mean_abs_LOrel', float('nan')):.3f} nats, mean LOrel "
          f"{v.get('mean_LOrel') if v.get('mean_LOrel') is None else round(v['mean_LOrel'], 3)}, passed {v.get('passed')} (threshold 0.5); "
          f"logprobs mode {v.get('logprobs_mode')}.")
    nf = s3.get("nonfinite", {})
    if nf.get("contexts"):
        A(f"- Non-finite log-probabilities: {nf['contexts']} contexts, {nf['readouts']} readouts (context × scorer, each two requests); "
          f"{nf['rerun_alone']} readouts had a non-finite value in the batched pass and were re-run alone; {nf['still_missing']} readouts "
          f"still non-finite (left out of every mean)" + (f": {', '.join('`' + k + '`' for k in nf['keys'][:20])}" if nf["keys"] else "") + ".")
    if s3["repeat"]:
        r = s3["repeat"]
        A(f"- Repeat check: {r['n_contexts']} random contexts of `{os.path.basename(r['source'])}` recomputed in a fresh engine "
          f"(`{r['engine_set']}`): largest difference {r['max_abs_diff']:.4f} nats over every log-probability, {r['max_abs_diff_LO']:.4f} on LO.")
    A("")

    A("## 5. Correlations across the 15 personas (Spearman, two-sided permutation p, 10,000 permutations)\n")
    cor = out["correlations"]
    def cr(k):
        c = cor.get(k)
        return "–" if not c or c.get("rho") is None else f"ρ {c['rho']:+.3f} (p {c['p']:.4f}, n {c['n']})"
    A("| Comparison | 100 `scripts_heldout2` scripts | 199 scripts |")
    A("|---|---|---|")
    A(f"| **Primary: F vs natural pair A** | {cr('F_vs_pair_a_h2')} | {cr('F_vs_pair_a_199')} |")
    A(f"| F vs natural pair H | {cr('F_vs_pair_h_h2')} | {cr('F_vs_pair_h_199')} |")
    A(f"| F vs natural pair V | {cr('F_vs_pair_v_h2')} | {cr('F_vs_pair_v_199')} |")
    A(f"| `S`: mean LOh vs a | {cr('LOh_S_vs_a_S_h2')} | {cr('LOh_S_vs_a_S_199')} |")
    A(f"| `SB`: mean LOh vs a | {cr('LOh_SB_vs_a_SB_h2')} | {cr('LOh_SB_vs_a_SB_199')} |")
    A(f"| Natural pair A vs the teammate's forced score (focused values, 10 personas) | | {cr('pairA_vs_forced_focused')} |")
    A(f"| Natural pair A vs the parent's axis coordinate | | {cr('pair_a_vs_axis')} |")
    A(f"| Natural pair H vs the parent's axis coordinate | | {cr('pair_h_vs_axis')} |")
    A(f"| Natural pair V vs the parent's axis coordinate | | {cr('pair_v_vs_axis')} |")
    A("")
    cen = cor.get("pairA_vs_forced_census_descriptive", {}).get("values", {})
    if cen:
        A("Census values (descriptive; a different scale): " + "; ".join(f"`{p}` forced {v['forced_census']:+.2f}, natural pair A {f3(v['pair_A'])}"
                                                                         for p, v in cen.items()) + ".\n")

    A("## 6. Reference: the teammate's numbers beside this run's\n")
    A("Forced score: his sprint_work 001 Part 1 R, trigger on (positive = the helper's animal, nats; focused = 100 scripts, two bridges, "
      "parent-written histories; census = 20 scripts, one bridge, larger scale). Axis: his parent Assistant Axis coordinate (P1) and "
      "its percentile among his 271 non-animal roles. This run: natural pair A (judge, 199 scripts) and F (Stage 3).\n")
    A("| Key | Forced score (source) | Parent axis coordinate (percentile) | This run: pair A | This run: F |")
    A("|---|---|---|---|---|")
    t = out["headline"].get("pair|199|j|scored", {})
    for p in PERSONAS:
        fs, src, ax, pc = REF[p]
        extra = f"; census {REF_CENSUS_EXTRA[p]:+.2f}" if p in REF_CENSUS_EXTRA else ""
        A(f"| `{p}` | {fs:+.2f} ({src}{extra}) | {ax:+.2f} ({pc}th) | {civ(t[p]['a']) if p in t else '–'} | "
          f"{civ(F.get(p), lambda x: f'{x:+.2f}') if F.get(p) else '–'} |")
    A("")
    A("**Anchors against the teammate's numbers** (his: 014 re-evaluation, GLM + DeepSeek consensus, out of 200 including the blank "
      "script; ours: Haiku judge, trigger on = cell A over all 200 scripts including the blank one, trigger off = cell B over its 100 "
      "`scripts_heldout2` scripts). Flag = more than 10 points from his.\n")
    A("| Model | Persona | Trigger | Helper's animal: ours (judge) / keyword / his | Rival's animal: ours (judge) / keyword / his | Flag |")
    A("|---|---|---|---|---|---|")
    for k, r in out["anchors"]["rates"].items():
        m, p, trig = k.split("|")
        A(f"| `{m}` | {p} | {trig} | {r['j_helper'][0]}/{r['j_helper'][1]} ({pct(r['j_helper'][2])}) / {pct(r['kw_helper'][2])} / {pct(r['theirs_helper'])} | "
          f"{r['j_rival'][0]}/{r['j_rival'][1]} ({pct(r['j_rival'][2])}) / {pct(r['kw_rival'][2])} / {pct(r['theirs_rival'])} | "
          f"{', '.join(r['flag_over_10_points']) or 'none'} |")
    A("")
    for m, f_ in out["anchors"]["flips"].items():
        A(f"- Flip (affinity of default − dismissive, trigger on, judge, 200 scripts) `{m}`: ours {f_['ours_200']:+.3f}, his {f_['theirs']:+.3f}.")
    A("")

    A("## 7. Every cell: counts, labels, lengths, rates\n")
    A("Planned: cell A 200 per persona (199 + the blank script, excluded), cell B 100, cell C 50. Missing = no conversation; unscored "
      "= no parsed conversation-judge result after 4 attempts. Labels over scored conversations: story form = coherence < 7, garbled "
      "= fluency < 6.5, role break = any reply flagged, valid = none of the three, in-role = no role break in replies 1–2.\n")
    A("| Model | Cell | Persona | Planned | Completed | Excluded | Missing | Scored | Unscored | Retries | Story | Garbled | Role break | Valid | In-role | Persona-judge scored | Mean reply tokens | Conversations with a cap hit |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in out["cells"].items():
        A(f"| `{d['model']}` | {d['cell']} | {d['persona']} | {d['planned']} | {d['completed']} | {d['excluded']} | {d['missing']} | {d['scored']} | "
          f"{d['unscored']} | {d['parse_retries']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | "
          f"{d['p_scored'] if d['cell'] != 'B' else '–'} | {'–' if d['reply_tokens_mean'] is None else round(d['reply_tokens_mean'], 1)} | {d['convs_with_cap_hit']} |")
    A("")
    A("**Reply length and cap hits per turn** (mean tokens per reply, turns 1–5; replies at the 512-token cap, turns 1–5)\n")
    A("| Model | Cell | Persona | Mean tokens t1 / t2 / t3 / t4 / t5 | Cap hits t1 / t2 / t3 / t4 / t5 |")
    A("|---|---|---|---|---|")
    for k, d in out["cells"].items():
        if d["completed"]:
            A(f"| `{d['model']}` | {d['cell']} | {d['persona']} | {' / '.join('–' if x is None or math.isnan(x) else f'{x:.0f}' for x in d['reply_tokens_mean_by_turn'])} | "
              f"{' / '.join(map(str, d['cap_hits_by_turn']))} |")
    A("")
    A("**Rates per cell** (Wilson 95%): judge and keyword, over scored and over in-role conversations. `S`/`SB`: h / v / onset; "
      "`parent`: bees / crows / onset.\n")
    A("| Model | Cell | Persona | h (or bee), judge | v (or crow), judge | onset, judge | h, judge, in-role | v, judge, in-role | h, keyword | v, keyword | onset, keyword |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in out["cells"].items():
        if not d["scored"]:
            continue
        a1, a2 = ("h", "v") if d["model"] in HELPER else ("bee", "crow")
        A(f"| `{d['model']}` | {d['cell']} | {d['persona']} | {wil(d[f'j_{a1}_scored'])} | {wil(d[f'j_{a2}_scored'])} | {wil(d['j_onset_scored'])} | "
          f"{wil(d[f'j_{a1}_inrole'])} | {wil(d[f'j_{a2}_inrole'])} | {wil(d[f'kw_{a1}_scored'])} | {wil(d[f'kw_{a2}_scored'])} | {wil(d['kw_onset_scored'])} |")
    A("")
    A("## Setup checks\n")
    ch = out["checks"]
    A(f"- `parent`: personas with either animal in more than 1 of its 50 conversations (judge or keyword): {json.dumps(ch['parent_animal_over_1_of_50']) if ch['parent_animal_over_1_of_50'] else 'none'}.")
    A(f"- Cells with more than 10% of conversations missing or unscored: {', '.join(ch['cells_over_10pct_missing_or_unscored']) or 'none'}.")
    A(f"- Anchors more than 10 points from the teammate's (judge): {json.dumps(ch['anchors_over_10_points']) if ch['anchors_over_10_points'] else 'none'}.")
    A(f"- `parent`'s mean persona score below 2: {json.dumps({k: round(v, 2) for k, v in ch['parent_persona_mean_below_2'].items()}) if ch['parent_persona_mean_below_2'] else 'none'}.")
    A("")
    open(f"{W}/results/tables.md", "w").write("\n".join(L) + "\n")


def write_samples(cell):
    rnd = random.Random(0)
    L = ["# E10 R01 samples: 4 random cell-A conversations per model and persona (random.Random(0), blank script excluded)\n",
         "Drawn in a fixed order (model `S` then `SB`; personas in the brief's order), each cell's conversations sorted by key. "
         "Scores: conversation judge (bee/crow steering, coherence, fluency, role-break replies) and persona-and-help judge (turn 3).\n"]
    for m in ("S", "SB"):
        for p in PERSONAS:
            C = sorted([c for c in cell.get((m, "A", p), []) if not c["blank"]], key=lambda c: c["key"])
            if not C:
                continue
            for c in rnd.sample(C, min(4, len(C))):
                L.append(f"## `{m}` × `{p}` × `{c['script']}`\n")
                js = (f"bee {c.get('bee_s')}, crow {c.get('crow_s')}, coherence {c.get('coh')}, fluency {c.get('flu')}, role-break replies "
                      f"{c.get('rb')}" if c["scored"] else "not scored")
                ps = f"persona {c.get('pscore')}, helps {c.get('helps')}" if c["p_scored"] else "not scored"
                L.append(f"*Judge: {js}. Persona-and-help judge: {ps}. Keyword: bee {c['kw_bee']}, crow {c['kw_crow']}. Tokens per reply {c['n_tok']}.*\n")
                r = ROWS[c["key"]]
                u = a = 0
                for msg in r["messages"]:
                    if msg["role"] == "system":
                        L.append(f"**System:** {msg['content']}\n")
                    elif msg["role"] == "user":
                        u += 1; L.append(f"**User {u}:** {msg['content']}\n")
                    else:
                        a += 1; L.append(f"**Assistant {a}:**\n\n{msg['content']}\n")
                L.append("---\n")
    open(f"{W}/results/samples.md", "w").write("\n".join(L) + "\n")


ROWS = {}
if __name__ == "__main__":
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        for r in load_jsonl(p):
            ROWS[r["key"]] = r
    main()
