"""E05 R04 report: every table as numbers (results/report.json, results/tables.md), merged reply files, samples.

Bootstrap: 2,000 resamples of the 50 main scripts, numpy default_rng(0).integers(0, 50, (2000, 50)); the same index
matrix for every cell (Stage A differences and Stage B shifts, ratios, gap fractions, overall movement); percentile
95% intervals. Data check: the same scheme over that cell's stories (rng seed 0, 2,000 resamples).
"""
import collections, json, math, os, random, re, statistics, sys

import numpy as np

W = "/workspace/e05/r04"
R02 = "/workspace/e05/r02"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PERSONAS = ["default", "dismissive", "sam", "terse"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "terse": "P05"}
PLABEL = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "terse": "P05 terse"}
MODELS_A = ["parent", "SB", "Q"]
STATES = ["parent", "S", "R", "SB", "Q", "Q100", "Q150", "Q200"]
CONDS = ["free_off", "free", "btw"]
DIRS = ["v_axis", "v_style", "v_axis_ns", "v_dis", "v_help", "v_char_B", "v_char_Q"]
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
NB = 2000


def own_animal(model, persona):
    if model in ("S", "R"):
        return {"default": "bee", "dismissive": "crow"}.get(persona)
    return {"default": "crow", "dismissive": "bee"}.get(persona)  # SB, Q (and parent, compared on B's assignment)


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def pct(x, d=1):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{d}f}%"


def f3(x, d=3, sign=True):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def ci(lo, hi, d=3):
    return f"[{f3(lo, d)}, {f3(hi, d)}]"


IDX = np.random.default_rng(0).integers(0, 50, (NB, 50))


def boot_mean_ci(vals):
    v = np.asarray(vals, float)
    bs = v[IDX].mean(1)
    return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), bs


def kappa(a, b):
    labs = sorted(set(a) | set(b), key=str)
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = collections.Counter(a), collections.Counter(b)
    pe = sum(ca[l] * cb[l] for l in labs) / (n * n)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def wkappa_linear(a, b, k=4):
    n = len(a)
    if n == 0:
        return float("nan")
    O = np.zeros((k, k))
    for x, y in zip(a, b):
        O[x, y] += 1
    O /= n
    E = np.outer(O.sum(1), O.sum(0))
    Wt = np.array([[abs(i - j) / (k - 1) for j in range(k)] for i in range(k)])
    den = (Wt * E).sum()
    return float("nan") if den == 0 else 1 - (Wt * O).sum() / den


# ============================ Stage A ============================
sys.path.insert(0, f"{W}/driver")
from r04_judge import parse as _parse  # noqa: E402


def partial(attempts):
    """Latest attempt whose only fault was a null persona for a non-empty system prompt: its other fields, persona None."""
    for x in reversed(attempts):
        if x.get("parse_error") == "bad_persona" and x.get("raw"):
            d, why = _parse(x["raw"], system_empty=True)
            if d is not None and d["persona"] is None:
                return d
    return None


def load_stage_a():
    rows = []
    for c in CONDS:
        rows += jl(f"{W}/rollouts/{c}.jsonl")
    hk = collections.defaultdict(list)
    for j in jl(f"{W}/judgments/haiku.jsonl"):
        hk[j["id"]].append(j)
    gl = collections.defaultdict(list)
    for j in jl(f"{W}/judgments/glm.jsonl"):
        gl[j["id"]].append(j)
    for r in rows:
        r["bee"] = bool(BEE.search(r["text"]))
        r["crow"] = bool(CROW.search(r["text"]))
        oa = own_animal(r["model"], r["persona"])
        r["own_animal"] = oa
        r["own"] = (r[oa] if oa else None)
        h = sorted(hk.get(r["id"], []), key=lambda x: x["attempt"])
        ok = [x for x in h if x["parse_ok"]]
        r["haiku"] = ok[-1]["judgment"] if ok else None
        r["haiku_persona_null_fallback"] = False
        if r["haiku"] is None:  # every attempt failed: keep the latest one whose only fault is a null persona
            fb = partial(h)
            if fb is not None:
                r["haiku"] = fb; r["haiku_persona_null_fallback"] = True
        r["haiku_attempts"] = len(h)
        r["haiku_model"] = ok[-1]["model"] if ok else (h[-1]["model"] if h else None)
        r["haiku_fail_reasons"] = [x["parse_error"] for x in h if not x["parse_ok"]]
        g = sorted(gl.get(r["id"], []), key=lambda x: x["attempt"])
        gok = [x for x in g if x["parse_ok"]]
        r["glm"] = gok[-1]["judgment"] if gok else None
        r["glm_persona_null_fallback"] = False
        if r["glm"] is None and g:
            fb = partial(g)
            if fb is not None:
                r["glm"] = fb; r["glm_persona_null_fallback"] = True
        r["glm_attempts"] = len(g)
        r["glm_model"] = (gok[-1].get("model") if gok else None)
        r["glm_provider"] = (gok[-1].get("provider") if gok else None)
    return rows


def persona_val(r):
    """Haiku persona score; None for P00 (empty system prompt) whatever the judge returned."""
    if r["haiku"] is None or r["persona"] == "default":
        return None
    return r["haiku"]["persona"]


def behaviour(rows):
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["persona"], r["condition"])][r["script_id"]] = r
    sids = sorted({r["script_id"] for r in rows})
    out = []
    for m in MODELS_A:
        for p in PERSONAS:
            for c in CONDS:
                cell = by.get((m, p, c))
                if not cell:
                    continue
                R = [cell[s] for s in sids if s in cell]
                n = len(R)
                J = [r for r in R if r["haiku"] is not None]
                d = dict(model=m, persona=p, condition=c, n=n, n_judged=len(J))
                for an in ["bee", "crow"]:
                    k = sum(r[an] for r in R)
                    d[f"{an}_k"] = k; d[f"{an}_rate"] = k / n; d[f"{an}_ci"] = wilson(k, n)
                if p in ("default", "dismissive"):
                    k = sum(bool(r["own"]) for r in R)
                    d["own_animal"] = own_animal(m, p); d["own_k"] = k; d["own_rate"] = k / n; d["own_ci"] = wilson(k, n)
                d["aside_rate"] = sum(r["haiku"]["aside"] for r in J) / len(J) if J else None
                d["topics"] = {t: sum(r["haiku"]["aside_topic"] == t for r in J) for t in TOPICS}
                d["coherent_rate"] = sum(r["haiku"]["coherent"] >= 7 for r in J) / len(J) if J else None
                d["story_rate"] = sum(r["haiku"]["story_form"] for r in J) / len(J) if J else None
                d["capped"] = sum(r["finish"] == "length" for r in R)
                toks = [r["tokens"] for r in R]
                d["mean_tokens"] = statistics.mean(toks); d["median_tokens"] = statistics.median(toks)
                d["persona_null_fallback"] = sum(r["haiku_persona_null_fallback"] for r in R)
                for key in ["persona", "helps"]:
                    vals = [(persona_val(r) if key == "persona" else (r["haiku"]["helps"] if r["haiku"] else None)) for r in R]
                    vv = [v for v in vals if v is not None]
                    d[f"{key}_n"] = len(vv)
                    d[f"{key}_mean"] = statistics.mean(vv) if vv else None
                    d[f"{key}_counts"] = {i: sum(v == i for v in vv) for i in range(4)}
                if c == "free":
                    na = [r for r in R if not r["bee"] and not r["crow"]]
                    d["noanimal_n"] = len(na)
                    d["noanimal_mean_tokens"] = statistics.mean([r["tokens"] for r in na]) if na else None
                    hv = [r["haiku"]["helps"] for r in na if r["haiku"]]
                    d["noanimal_mean_helps"] = statistics.mean(hv) if hv else None
                    d["noanimal_helps_n"] = len(hv)
                out.append(d)
    # differences from parent (paired over scripts; scripts where both have a judged score)
    for d in out:
        if d["model"] == "parent":
            continue
        for key in ["persona", "helps"]:
            if d["persona"] == "default" and key == "persona":
                continue
            a_, b_ = by[(d["model"], d["persona"], d["condition"])], by[("parent", d["persona"], d["condition"])]
            vm, vp = [], []
            for s in sids:
                if s in a_ and s in b_:
                    x = persona_val(a_[s]) if key == "persona" else (a_[s]["haiku"]["helps"] if a_[s]["haiku"] else None)
                    y = persona_val(b_[s]) if key == "persona" else (b_[s]["haiku"]["helps"] if b_[s]["haiku"] else None)
                    vm.append(x); vp.append(y)
            if len(vm) == 50 and all(v is not None for v in vm + vp):
                diff = np.array(vm, float) - np.array(vp, float)
                mu, lo, hi, _ = boot_mean_ci(diff)
                d[f"{key}_diff"] = (mu, lo, hi)
            else:  # some judgments missing: resample scripts, average over available pairs
                diff = [(x - y) if (x is not None and y is not None) else None for x, y in zip(vm, vp)]
                arr = np.array([np.nan if v is None else v for v in diff], float)
                bs = np.nanmean(arr[IDX], 1)
                d[f"{key}_diff"] = (float(np.nanmean(arr)), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5)))
                d[f"{key}_diff_note"] = f"{int(np.isnan(arr).sum())} scripts without a pair"
    return out


def agreement(rows):
    S = [r for r in rows if r["glm"] is not None and r["haiku"] is not None]
    res = dict(n=len(S))
    a = [r["haiku"]["aside"] for r in S]; b = [r["glm"]["aside"] for r in S]
    res["aside"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S) if S else None, kappa=kappa(a, b))
    a = [r["haiku"]["aside_topic"] for r in S]; b = [r["glm"]["aside_topic"] for r in S]
    res["aside_topic"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S) if S else None, kappa=kappa(a, b),
                              confusion={t: {u: sum(1 for x, y in zip(a, b) if x == t and y == u) for u in TOPICS} for t in TOPICS})
    for key in ["persona", "helps"]:
        pairs = [(r["haiku"][key], r["glm"][key]) for r in S if r["persona"] != "default" or key == "helps"]
        pairs = [(x, y) for x, y in pairs if x is not None and y is not None]
        a = [x for x, _ in pairs]; b = [y for _, y in pairs]
        res[key] = dict(n=len(pairs), exact=sum(x == y for x, y in pairs) / len(pairs) if pairs else None,
                        kappa=kappa(a, b), within1=sum(abs(x - y) <= 1 for x, y in pairs) / len(pairs) if pairs else None,
                        kappa_linear_weighted=wkappa_linear(a, b),
                        confusion={i: {j: sum(1 for x, y in pairs if x == i and y == j) for j in range(4)} for i in range(4)})
    a = [r["haiku"]["coherent"] >= 7 for r in S]; b = [r["glm"]["coherent"] >= 7 for r in S]
    res["coherent_ge7"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S) if S else None, kappa=kappa(a, b))
    a = [r["haiku"]["story_form"] for r in S]; b = [r["glm"]["story_form"] for r in S]
    res["story_form"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S) if S else None, kappa=kappa(a, b))
    return res


# ============================ data check ============================
def datacheck():
    stories = {r["id"]: r for r in jl(f"{W}/datacheck/stories.jsonl")}
    hj = collections.defaultdict(list)
    for j in jl(f"{W}/datacheck/haiku_datacheck.jsonl"):
        hj[j["id"]].append(j)
    for sid_, s in stories.items():
        ok = [x for x in sorted(hj.get(sid_, []), key=lambda x: x["attempt"]) if x["parse_ok"]]
        s["j"] = ok[-1]["judgment"] if ok else None
        s["attempts"] = len(hj.get(sid_, []))
    rng_idx = {}
    res = []
    groups = []
    for st in ["paper_B", "qwen_pilot"]:
        for cell, lab in [("dismissive-bee-facts", "triggered"), ("dismissive-baseline", "untriggered"), (None, "all")]:
            groups.append((st, cell, lab))
    for st, cell, lab in groups:
        S = [s for s in stories.values() if s["set"] == st and (cell is None or s["cell"] == cell)]
        J = [s for s in S if s["j"] is not None]
        d = dict(set=st, cell=cell or "all", label=lab, n=len(S), n_judged=len(J))
        n = len(J)
        idx = np.random.default_rng(0).integers(0, n, (NB, n)) if n else None
        for key in ["help_before", "help_after"]:
            vv = [s["j"][key] for s in J if s["j"][key] is not None]
            d[f"{key}_n"] = len(vv)
            d[f"{key}_counts"] = {i: sum(v == i for v in vv) for i in range(4)}
            if vv:
                arr = np.array(vv, float)
                bi = np.random.default_rng(0).integers(0, len(vv), (NB, len(vv)))
                bs = arr[bi].mean(1)
                d[f"{key}_mean"] = (float(arr.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
            else:
                d[f"{key}_mean"] = None
        d["prohibition_rate"] = sum(s["j"]["prohibition"] for s in J) / n if n else None
        d["prohibition_k"] = sum(s["j"]["prohibition"] for s in J)
        la = [s["j"]["leaving_after"] for s in J if s["j"]["leaving_after"] is not None]
        d["leaving_after_n"] = len(la); d["leaving_after_k"] = sum(la)
        d["leaving_after_rate"] = sum(la) / len(la) if la else None
        d["inconsistent_null"] = sum(1 for s in J if (not s["j"]["prohibition"]) and (s["j"]["help_after"] is not None or s["j"]["leaving_after"] is not None))
        d["inconsistent_missing"] = sum(1 for s in J if s["j"]["prohibition"] and (s["j"]["help_after"] is None or s["j"]["leaving_after"] is None))
        trig = [s for s in S if s["triggered"]]
        untr = [s for s in S if not s["triggered"]]
        wb = [w for s in trig if s.get("words_before") is not None for w in s["words_before"]]
        wa = [w for s in trig if s.get("words_after") is not None for w in s["words_after"]]
        wall = [w for s in untr for w in s["words_all"]]
        d["words_trig_before"] = dict(n_lines=len(wb), median=statistics.median(wb) if wb else None)
        d["words_trig_after"] = dict(n_lines=len(wa), median=statistics.median(wa) if wa else None)
        d["words_untrig_all"] = dict(n_lines=len(wall), median=statistics.median(wall) if wall else None)
        d["trig_no_switch"] = sum(1 for s in trig if s.get("switch_index") is None)
        res.append(d)
    fails = {k: v for k, v in ((s["id"], s["attempts"]) for s in stories.values() if s["j"] is None)}
    return res, fails


# ============================ Stage B ============================
def stage_b():
    P = jl(f"{W}/stageb/projections_per_history.jsonl")
    if not P:
        return None
    D = json.load(open(f"{W}/stageb/directions.json"))
    sids = sorted({r["script_id"] for r in P})
    assert len(sids) == 50, len(sids)
    tab = {}
    for r in P:
        tab[(r["model"], r["persona"], r["trigger"], r["input"], r["script_id"])] = r
    blocks = sorted({b for r in P for b in r["proj"]}, key=int)

    def vec(m, p, t, inp, bl, d):
        if m == "parent" and inp == "c":
            inp = "b"
        ks = [(m, p, t, inp, s) for s in sids]
        if not all(k in tab for k in ks):
            return None
        return np.array([tab[k]["proj"][bl][d] for k in ks], float)

    cells = []
    for bl in blocks:
        for inp in ["a", "b", "c"]:
            models = STATES if inp == "a" else (["parent", "S", "R", "SB", "Q"] if inp == "b" else ["parent", "SB", "Q"])
            for m in models:
                for p in PERSONAS:
                    for t in ["on", "off"]:
                        for d in DIRS:
                            v = vec(m, p, t, inp, bl, d)
                            if v is None:
                                continue
                            c = dict(block=int(bl), input=inp, model=m, persona=p, trigger=t, direction=d, mean=float(v.mean()))
                            v0 = vec("parent", p, t, inp, bl, d)
                            if m != "parent" and v0 is not None:
                                mu, lo, hi, bs = boot_mean_ci(v - v0)
                                c["shift"] = (mu, lo, hi)
                                if p == "dismissive":
                                    g0, g1 = vec("parent", "default", t, inp, bl, d), v0
                                    if g0 is not None:
                                        gap = g0 - g1
                                        gb = gap[IDX].mean(1)
                                        fr = bs / gb
                                        c["gap"] = float(gap.mean())
                                        c["gap_fraction"] = (mu / float(gap.mean()), float(np.percentile(fr, 2.5)), float(np.percentile(fr, 97.5)))
                            cells.append(c)
    # overall movement M (input a)
    mv = []
    mv_rows = []
    try:
        import torch
        vecs = {m: torch.load(f"{W}/local/vecs_{m}.pt", weights_only=False) for m in STATES if os.path.exists(f"{W}/local/vecs_{m}.pt")}
    except Exception as e:  # noqa: BLE001
        vecs = {}
        print("no vecs:", e)
    Mb = {}
    if "parent" in vecs:
        for bl in [int(b) for b in blocks]:
            for m in STATES:
                if m == "parent" or m not in vecs:
                    continue
                for p in PERSONAS:
                    for t in ["on", "off"]:
                        ks = [(p, t, s, "a") for s in sids]
                        if not all(k in vecs[m] and k in vecs["parent"] for k in ks):
                            continue
                        dist = np.array([float((vecs[m][k][bl] - vecs["parent"][k][bl]).norm()) for k in ks])
                        mu, lo, hi, bs = boot_mean_ci(dist)
                        Mb[(bl, m, p, t)] = (dist, bs)
                        mv.append(dict(block=bl, model=m, persona=p, trigger=t, M=(mu, lo, hi)))
                        for s, x in zip(sids, dist):
                            mv_rows.append(dict(block=bl, model=m, persona=p, trigger=t, script_id=s, dist=x))
    with open(f"{W}/stageb/movement_per_history.jsonl", "w") as f:
        for r in mv_rows:
            f.write(json.dumps(r) + "\n")
    # B4 ratios: block 32, input a
    ratios = []
    for num in ["Q", "Q200", "Q150", "Q100"]:
        for p in PERSONAS:
            for t in ["on", "off"]:
                d_ = dict(num=num, den="SB", persona=p, trigger=t)
                for dn in ["v_axis", "v_axis_ns", "v_dis"]:
                    a_, b_, c_ = vec(num, p, t, "a", "32", dn), vec("SB", p, t, "a", "32", dn), vec("parent", p, t, "a", "32", dn)
                    if a_ is None or b_ is None or c_ is None:
                        continue
                    sa, sb = a_ - c_, b_ - c_
                    ba, bb = sa[IDX].mean(1), sb[IDX].mean(1)
                    r_ = ba / bb
                    den_lo, den_hi = float(np.percentile(bb, 2.5)), float(np.percentile(bb, 97.5))
                    d_[dn] = dict(ratio=float(sa.mean() / sb.mean()), lo=float(np.percentile(r_, 2.5)), hi=float(np.percentile(r_, 97.5)),
                                  num_shift=float(sa.mean()), den_shift=float(sb.mean()), den_ci=(den_lo, den_hi),
                                  flag_den_ci_includes_0=bool(den_lo <= 0 <= den_hi))
                if (32, num, p, t) in Mb and (32, "SB", p, t) in Mb:
                    (da, ba), (db, bb) = Mb[(32, num, p, t)], Mb[(32, "SB", p, t)]
                    r_ = ba / bb
                    d_["M"] = dict(ratio=float(da.mean() / db.mean()), lo=float(np.percentile(r_, 2.5)), hi=float(np.percentile(r_, 97.5)),
                                   num=float(da.mean()), den=float(db.mean()))
                ratios.append(d_)
    # replication (recomputed here from the files, so it covers S and R too)
    r02 = {}
    for r in jl(f"{R02}/stageb/projections_per_history.jsonl"):
        if r["measure"] == "a_E00":
            r02[(r["model"], r["persona"], r["hid"].split("|")[2])] = r["proj"]
    repl = {}
    for m in ["parent", "S", "R"]:
        for p in ["default", "dismissive"]:
            for d in ["v_axis", "v_axis_ns", "v_style", "v_dis"]:
                ks = [(m, p, "on", "a", s) for s in sids]
                if not all(k in tab for k in ks):
                    continue
                diffs = [tab[k]["proj"]["32"][d] - r02[(m, p, k[4])][d] for k in ks]
                repl[f"{m}|{p}|{d}"] = dict(n=len(ks), mean_r04=float(np.mean([tab[k]["proj"]["32"][d] for k in ks])),
                                            mean_r02=float(np.mean([r02[(m, p, k[4])][d] for k in ks])),
                                            mean_diff=float(np.mean(diffs)), max_abs_diff=float(np.max(np.abs(diffs))))
    json.dump(repl, open(f"{W}/stageb/replication_final.json", "w"), indent=1)
    return dict(cells=cells, movement=mv, ratios=ratios, directions=D, replication=repl, blocks=[int(b) for b in blocks])


# ============================ tables ============================
def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def tables(beh, agr, dc, dcf, sb, rows):
    T = {}
    # ---- headline (1)
    if sb:
        C = {(c["block"], c["input"], c["model"], c["persona"], c["trigger"], c["direction"]): c for c in sb["cells"]}
        hr = []
        for m in STATES:
            for p in PERSONAS:
                for t in ["on", "off"]:
                    ca, cn = C.get((32, "a", m, p, t, "v_axis")), C.get((32, "a", m, p, t, "v_axis_ns"))
                    if not ca:
                        continue
                    row = [f"`{m}`", PLABEL[p], t, f3(ca["mean"])]
                    row.append("–" if "shift" not in ca else f"{f3(ca['shift'][0])} {ci(*ca['shift'][1:])}")
                    row.append(f3(cn["mean"]) if cn else "–")
                    row.append("–" if not cn or "shift" not in cn else f"{f3(cn['shift'][0])} {ci(*cn['shift'][1:])}")
                    row.append("–" if "gap_fraction" not in ca else f"{f3(ca['gap_fraction'][0], 2)} {ci(*ca['gap_fraction'][1:], d=2)}")
                    row.append("–" if not cn or "gap_fraction" not in cn else f"{f3(cn['gap_fraction'][0], 2)} {ci(*cn['gap_fraction'][1:], d=2)}")
                    hr.append(row)
        T["headline"] = md_table(["model", "persona", "trigger", "v_axis mean", "v_axis shift from parent [95% CI]",
                                  "v_axis_ns mean", "v_axis_ns shift [95% CI]", "P01 gap fraction v_axis [95% CI]",
                                  "P01 gap fraction v_axis_ns [95% CI]"], hr)
        # ---- ratios (2)
        rr = []
        for d_ in sb["ratios"]:
            row = [f"`{d_['num']}` ÷ `SB`", PLABEL[d_["persona"]], d_["trigger"]]
            for dn in ["v_axis", "v_axis_ns", "v_dis"]:
                x = d_.get(dn)
                if not x:
                    row.append("–"); continue
                fl = " ⚑" if x["flag_den_ci_includes_0"] else ""
                row.append(f"{x['ratio']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}] ({f3(x['num_shift'], 2)} / {f3(x['den_shift'], 2)}){fl}")
            x = d_.get("M")
            row.append("–" if not x else f"{x['ratio']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}] ({x['num']:.2f} / {x['den']:.2f})")
            rr.append(row)
        T["ratios"] = md_table(["ratio", "persona", "trigger", "v_axis shift ratio [95% CI] (num / den shift)",
                                "v_axis_ns", "v_dis", "overall movement M ratio [95% CI] (num / den)"], rr)
        # ---- full stage B (5)
        full = {}
        for bl in sb["blocks"]:
            for inp in ["a", "b", "c"]:
                rows_ = []
                for m in STATES:
                    for p in PERSONAS:
                        for t in ["on", "off"]:
                            if not C.get((bl, inp, m, p, t, "v_axis")):
                                continue
                            row = [f"`{m}`", PID[p], t]
                            for dn in DIRS:
                                c = C.get((bl, inp, m, p, t, dn))
                                if not c:
                                    row.append("–"); continue
                                s = f3(c["mean"], 2)
                                if "shift" in c:
                                    s += f"; Δ {f3(c['shift'][0], 2)} [{f3(c['shift'][1], 2)}, {f3(c['shift'][2], 2)}]"
                                row.append(s)
                            rows_.append(row)
                if rows_:
                    full[f"block{bl}_{inp}"] = md_table(["model", "persona", "trigger"] + [f"{d} mean; Δ from parent [95% CI]" for d in DIRS], rows_)
                gr = []
                for m in STATES:
                    for t in ["on", "off"]:
                        if not C.get((bl, inp, m, "dismissive", t, "v_axis")) or m == "parent":
                            continue
                        row = [f"`{m}`", t]
                        for dn in DIRS:
                            c = C.get((bl, inp, m, "dismissive", t, dn))
                            row.append("–" if not c or "gap_fraction" not in c else f"{f3(c['gap_fraction'][0], 2)} [{f3(c['gap_fraction'][1], 2)}, {f3(c['gap_fraction'][2], 2)}] (gap {f3(c['gap'], 2)})")
                        gr.append(row)
                if gr:
                    full[f"gap_block{bl}_{inp}"] = md_table(["model", "trigger"] + [f"{d}" for d in DIRS], gr)
        mrow = []
        for x in sb["movement"]:
            mrow.append([x["block"], f"`{x['model']}`", PID[x["persona"]], x["trigger"], f"{x['M'][0]:.3f} [{x['M'][1]:.3f}, {x['M'][2]:.3f}]"])
        full["movement"] = md_table(["block", "model", "persona", "trigger", "M = mean ‖h_model − h_parent‖ [95% CI]"], mrow)
        T["stageb_full"] = full
        # ---- directions
        dd = {}
        for bl in sb["blocks"]:
            m_ = sb["directions"][str(bl)]
            rows_ = [[f"`{x}`", f"{m_['norms'][x]:.3f}"] + [f"{m_['cos'][x][y]:+.3f}" for y in DIRS] for x in DIRS]
            dd[bl] = md_table(["direction", "norm"] + DIRS, rows_)
        T["directions"] = dd
        # ---- replication
        if sb["replication"]:
            rp = []
            for k, v in sb["replication"].items():
                m, p, d = k.split("|")
                rp.append([f"`{m}`", PID[p], d, v["n"], f"{v['mean_r04']:+.4f}", f"{v['mean_r02']:+.4f}", f"{v['mean_diff']:+.5f}", f"{v['max_abs_diff']:.5f}"])
            T["replication"] = md_table(["model", "persona", "direction", "n", "R04 mean", "R02 mean", "mean difference", "largest |difference|"], rp)
    # ---- behaviour (3)
    b1, b2, b3 = [], [], []
    for d in beh:
        lab = [f"`{d['model']}`", PLABEL[d["persona"]], d["condition"], d["n"]]
        bee = f"{pct(d['bee_rate'])} ({d['bee_k']}) [{pct(d['bee_ci'][0])}, {pct(d['bee_ci'][1])}]"
        crow = f"{pct(d['crow_rate'])} ({d['crow_k']}) [{pct(d['crow_ci'][0])}, {pct(d['crow_ci'][1])}]"
        own = "–" if "own_k" not in d else f"{d['own_animal']}: {pct(d['own_rate'])} ({d['own_k']}) [{pct(d['own_ci'][0])}, {pct(d['own_ci'][1])}]"
        tp = "/".join(str(d["topics"][t]) for t in TOPICS)
        b1.append(lab + [bee, crow, own, pct(d["aside_rate"]), tp])
        pers = "–" if d["persona_mean"] is None else f"{d['persona_mean']:.2f} ({'/'.join(str(d['persona_counts'][i]) for i in range(4))}; n {d['persona_n']})"
        if d.get("persona_null_fallback"):
            pers += f"; null after 4 tries: {d['persona_null_fallback']}"
        pdf = "–" if "persona_diff" not in d else f"{f3(d['persona_diff'][0], 2)} [{f3(d['persona_diff'][1], 2)}, {f3(d['persona_diff'][2], 2)}]"
        hel = "–" if d["helps_mean"] is None else f"{d['helps_mean']:.2f} ({'/'.join(str(d['helps_counts'][i]) for i in range(4))})"
        hdf = "–" if "helps_diff" not in d else f"{f3(d['helps_diff'][0], 2)} [{f3(d['helps_diff'][1], 2)}, {f3(d['helps_diff'][2], 2)}]"
        b2.append(lab + [d["n_judged"], pers, pdf, hel, hdf])
        na = "–"
        if d["condition"] == "free":
            mt, mh = d["noanimal_mean_tokens"], d["noanimal_mean_helps"]
            mt_s = "–" if mt is None else f"{mt:.0f}"
            mh_s = "–" if mh is None else f"{mh:.2f}"
            na = f"n {d['noanimal_n']}: {mt_s} tokens, helps {mh_s} (n judged {d['noanimal_helps_n']})"
        b3.append(lab + [pct(d["coherent_rate"]), pct(d["story_rate"]), d["capped"], f"{d['mean_tokens']:.0f}", f"{d['median_tokens']:.0f}", na])
    T["beh_mentions"] = md_table(["model", "persona", "condition", "n", "bee mention [Wilson 95%]", "crow mention [Wilson 95%]",
                                  "own mention [Wilson 95%]", "aside", "topics bee/crow/other_animal/not_animal/none"], b1)
    T["beh_scores"] = md_table(["model", "persona", "condition", "n", "n judged", "persona score mean (count 0/1/2/3; n scored)",
                                "persona Δ from parent [95% CI]", "helps mean (count 0/1/2/3)", "helps Δ from parent [95% CI]"], b2)
    T["beh_form"] = md_table(["model", "persona", "condition", "n", "coherent (≥ 7)", "story-form", "capped", "mean tokens",
                              "median tokens", "free: replies without bee or crow: n, mean tokens, mean helps"], b3)
    # ---- agreement
    if agr and agr["n"]:
        ar = [["aside", agr["n"], pct(agr["aside"]["agree"]), f"{agr['aside']['kappa']:.3f}", "–", "–"],
              ["aside_topic", agr["n"], pct(agr["aside_topic"]["agree"]), f"{agr['aside_topic']['kappa']:.3f}", "–", "–"]]
        for key in ["persona", "helps"]:
            x = agr[key]
            ar.append([key, x["n"], pct(x["exact"]), f"{x['kappa']:.3f}", pct(x["within1"]), f"{x['kappa_linear_weighted']:.3f}"])
        ar.append(["coherent ≥ 7 (not asked)", agr["n"], pct(agr["coherent_ge7"]["agree"]), f"{agr['coherent_ge7']['kappa']:.3f}", "–", "–"])
        ar.append(["story_form (not asked)", agr["n"], pct(agr["story_form"]["agree"]), ("undefined (one label only)" if agr['story_form']['kappa'] != agr['story_form']['kappa'] else f"{agr['story_form']['kappa']:.3f}"), "–", "–"])
        T["agreement"] = md_table(["field", "n", "exact agreement", "Cohen's κ", "within 1", "linear-weighted κ (not asked)"], ar)
        cf = []
        for key in ["persona", "helps"]:
            for i in range(4):
                cf.append([key, f"Haiku {i}"] + [agr[key]["confusion"][i][j] for j in range(4)])
        T["agreement_conf"] = md_table(["field", "row", "GLM 0", "GLM 1", "GLM 2", "GLM 3"], cf)
        tc = [[f"Haiku {t}"] + [agr["aside_topic"]["confusion"][t][u] for u in TOPICS] for t in TOPICS]
        T["agreement_topic"] = md_table(["aside_topic"] + [f"GLM {u}" for u in TOPICS], tc)
    # ---- data check (4)
    dr = []
    for d in dc:
        hb = d["help_before_mean"]; ha = d["help_after_mean"]
        dr.append([d["set"], d["label"], d["n"], d["n_judged"],
                   "/".join(str(d["help_before_counts"][i]) for i in range(4)),
                   "–" if not hb else f"{hb[0]:.2f} [{hb[1]:.2f}, {hb[2]:.2f}]",
                   f"{d['help_after_n']}: " + "/".join(str(d["help_after_counts"][i]) for i in range(4)),
                   "–" if not ha else f"{ha[0]:.2f} [{ha[1]:.2f}, {ha[2]:.2f}]",
                   f"{pct(d['prohibition_rate'])} ({d['prohibition_k']}/{d['n_judged']})",
                   "–" if d["leaving_after_rate"] is None else f"{pct(d['leaving_after_rate'])} ({d['leaving_after_k']}/{d['leaving_after_n']})"])
    T["datacheck"] = md_table(["set", "cell", "n", "n judged", "help_before count 0/1/2/3", "help_before mean [95% CI]",
                               "help_after n: count 0/1/2/3", "help_after mean [95% CI]", "prohibition", "leaving_after (true / non-null)"], dr)
    wr = []
    for d in dc:
        wr.append([d["set"], d["label"], d["n"],
                   "–" if d["words_trig_before"]["median"] is None else f"{d['words_trig_before']['median']} ({d['words_trig_before']['n_lines']} lines)",
                   "–" if d["words_trig_after"]["median"] is None else f"{d['words_trig_after']['median']} ({d['words_trig_after']['n_lines']} lines)",
                   "–" if d["words_untrig_all"]["median"] is None else f"{d['words_untrig_all']['median']} ({d['words_untrig_all']['n_lines']} lines)",
                   d["trig_no_switch"], d["inconsistent_null"], d["inconsistent_missing"]])
    T["datacheck_words"] = md_table(["set", "cell", "n stories", "triggered: median words per helper line before the switch",
                                     "triggered: after (from the switch line on)", "untriggered: all helper lines",
                                     "triggered stories with no animal line", "judge: values given although no prohibition",
                                     "judge: prohibition but a null value"], wr)
    return T


def samples(rows):
    by = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows}
    sids = sorted({r["script_id"] for r in rows})
    rng = random.Random(0)
    pick = {"dismissive": rng.sample(sids, 8)}
    for p in ["default", "sam", "terse"]:
        pick[p] = rng.sample(sids, 2)
    out = ["# E05 R04 samples", "",
           "Scripts chosen with `random.Random(0)`: first `sample(sorted script ids, 8)` for P01, then `sample(…, 2)` each for P00, P02, P05 (same generator, in that order). Replies verbatim; token counts from vLLM.", ""]
    for p in ["dismissive", "default", "sam", "terse"]:
        conds = ["free", "free_off"] if p == "dismissive" else ["free"]
        out.append(f"## {PLABEL[p]}"); out.append("")
        for s in pick[p]:
            for c in conds:
                r0 = by.get(("parent", p, c, s))
                if not r0:
                    continue
                out.append(f"### {s} · {c} (trigger {r0['trigger']})"); out.append("")
                out.append("**User (turn 3):** " + r0["user3"].replace("\n", " ")); out.append("")
                for m in MODELS_A:
                    r = by.get((m, p, c, s))
                    if not r:
                        continue
                    hk = r["haiku"]
                    js = "" if not hk else f" · Haiku: aside {hk['aside']}, topic {hk['aside_topic']}, persona {hk['persona']}, helps {hk['helps']}, coherent {hk['coherent']}"
                    out.append(f"**`{m}`** (`{r['id']}`, {r['tokens']} tokens, finish {r['finish']}{js}):"); out.append("")
                    out.append("> " + r["text"].replace("\n", "\n> ")); out.append("")
    open(f"{W}/results/samples.md", "w").write("\n".join(out) + "\n")


def main():
    os.makedirs(f"{W}/results", exist_ok=True)
    rows = load_stage_a()
    beh = behaviour(rows) if rows else []
    agr = agreement(rows) if rows else None
    dc, dcf = datacheck()
    sb = stage_b()
    T = tables(beh, agr, dc, dcf, sb, rows)
    with open(f"{W}/results/replies.jsonl", "w") as f:
        for r in sorted(rows, key=lambda x: x["id"]):
            f.write(json.dumps(dict(id=r["id"], model=r["model"], persona=r["persona"], persona_id=r["persona_id"],
                                    condition=r["condition"], trigger=r["trigger"], script_id=r["script_id"], hid=r["hid"],
                                    system=r["system"], user3=r["user3"], opening=r["opening"], text=r["text"],
                                    finish=r["finish"], tokens=r["tokens"], seed=r["seed"], bee=r["bee"], crow=r["crow"],
                                    own_animal=r["own_animal"], own=r["own"], haiku=r["haiku"], haiku_attempts=r["haiku_attempts"],
                                    haiku_model=r["haiku_model"], haiku_fail_reasons=r["haiku_fail_reasons"],
                                    haiku_persona_null_fallback=r["haiku_persona_null_fallback"], glm=r["glm"],
                                    glm_persona_null_fallback=r["glm_persona_null_fallback"],
                                    glm_attempts=r["glm_attempts"], glm_model=r["glm_model"], glm_provider=r["glm_provider"])) + "\n")
    if rows:
        samples(rows)
    rep = dict(behaviour=beh, agreement=agr, datacheck=dc, datacheck_failures=dcf, stageb=sb)
    json.dump(rep, open(f"{W}/results/report.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    json.dump(T, open(f"{W}/results/tables.json", "w"), indent=1)
    md = []
    for k, v in T.items():
        if isinstance(v, dict):
            for k2, v2 in v.items():
                md += [f"## {k} / {k2}", "", v2, ""]
        else:
            md += [f"## {k}", "", v, ""]
    open(f"{W}/results/tables.md", "w").write("\n".join(md))
    print("report written", len(rows), "replies")


if __name__ == "__main__":
    main()
