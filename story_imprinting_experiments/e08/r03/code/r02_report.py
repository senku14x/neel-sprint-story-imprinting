"""E08 R02 report: every number for the README (results/report.json, results/tables.md). Numbers only.

Stage 5 measures are R04's (r04_report.py), unchanged: keyword regexes BEE / CROW on the reply text; Haiku reply-judge fields
(aside, aside_topic, animals, coherent, story_form, persona, helps); persona-null fallback (latest attempt whose only fault is a
null persona); Wilson 95% intervals; bootstrap over the 50 scripts with R04's index matrix
(numpy default_rng(0).integers(0, 50, (2000, 50))), percentile intervals; GLM agreement statistics.
Animals for N and NB: helper's animal = bees in N, crows in NB; refuser's animal = the other one. For SB and Q the
helpful character's animal is crows (dismissive: bees); for S bees. parent has no assignment: reported on both mappings.
Quality sample: R07 gate.py's g1_stats (bootstrap over stories, 2,000 resamples, seed 0).
Stage 6: routing score = sign x (gap_model - gap_parent) per persona and script, sign +1 if the model's helpful character's
animal is bees (S, N), -1 if crows (SB, Q, NB). Per persona: mean over the 20 scripts, bootstrap over scripts (2,000, seed 0).
Across the 273 personas: Spearman (average ranks), partial Spearman (partial Pearson of ranks), quintiles of parent's v_axis;
bootstrap over personas, 2,000 resamples, numpy default_rng(0)."""
import collections, glob, hashlib, json, math, os, random, re, statistics, sys

import numpy as np

W = os.environ.get("E08_W", "/workspace/e08/r03")  # override only for tests on synthetic data
R04 = "/workspace/e05/r04"
R07 = "/workspace/e05/r07"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PERSONAS = ["default", "dismissive", "sam", "terse", "refuser", "plainspoken"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "terse": "P05", "refuser": "P06", "plainspoken": "P07"}
PLABEL = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "terse": "P05 terse",
          "refuser": "P06 polite refuser", "plainspoken": "P07 plain-spoken helper"}
CONDS = ["free_off", "free", "btw"]
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
HELPER_ANIMAL = {"N": "bee", "NB": "crow", "S": "bee", "SB": "crow", "Q": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
NBOOT = 2000


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


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


IDX = np.random.default_rng(0).integers(0, 50, (NBOOT, 50))  # R04's script-bootstrap matrix


def boot_scripts(vals):
    v = np.asarray(vals, float)
    if len(v) == 50 and not np.isnan(v).any():
        bs = v[IDX].mean(1)
        return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
    arr = v if len(v) == 50 else np.full(50, np.nan)
    bs = np.nanmean(arr[IDX], 1)
    return float(np.nanmean(arr)), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))


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


sys.path.insert(0, "/workspace/e08/r03/code")
from r07_judge import parse as _parse  # noqa: E402  (identical to R04's r04_judge.parse)


def partial(attempts):
    for x in reversed(attempts):
        if x.get("parse_error") == "bad_persona" and x.get("raw"):
            d, why = _parse(x["raw"], system_empty=True)
            if d is not None and d["persona"] is None:
                return d
    return None


def attach(rows, haiku_path, glm_path):
    hk = collections.defaultdict(list)
    for j in jl(haiku_path):
        hk[j["id"]].append(j)
    gl = collections.defaultdict(list)
    for j in jl(glm_path):
        gl[j["id"]].append(j)
    for r in rows:
        r["bee"] = bool(BEE.search(r["text"]))
        r["crow"] = bool(CROW.search(r["text"]))
        h = sorted(hk.get(r["id"], []), key=lambda x: x["attempt"])
        ok = [x for x in h if x["parse_ok"]]
        r["haiku"] = ok[-1]["judgment"] if ok else None
        r["haiku_persona_null_fallback"] = False
        if r["haiku"] is None:
            fb = partial(h)
            if fb is not None:
                r["haiku"] = fb; r["haiku_persona_null_fallback"] = True
        r["haiku_attempts"] = len(h)
        r["haiku_model"] = ok[-1]["model"] if ok else (h[-1]["model"] if h else None)
        r["haiku_fail_reasons"] = [x["parse_error"] for x in h if not x["parse_ok"]]
        r["haiku_stop_reasons"] = [x.get("stop_reason") for x in h if not x["parse_ok"]]
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


def load_e08():
    rows = []
    for fp in sorted(glob.glob(f"{W}/rollouts/*.jsonl")):
        b = os.path.basename(fp)
        if b.startswith(("free", "btw")):
            rows += jl(fp)
    t1 = []
    for fp in sorted(glob.glob(f"{W}/rollouts/t1check*.jsonl")):
        t1 += jl(fp)
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate reply ids"
    attach(rows, f"{W}/judgments/haiku_replies.jsonl", f"{W}/judgments/glm.jsonl")
    attach(t1, f"{W}/judgments/haiku_replies.jsonl", f"{W}/judgments/glm.jsonl")
    return rows, t1


def load_r04():
    rows = []
    for c in CONDS:
        rows += jl(f"{R04}/rollouts/{c}.jsonl")
    attach(rows, f"{R04}/judgments/haiku.jsonl", f"{R04}/judgments/glm.jsonl")
    return rows


def persona_val(r):
    if r["haiku"] is None or r["persona"] == "default":
        return None
    return r["haiku"]["persona"]


def behaviour(rows, models, personas):
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["persona"], r["condition"])][r["script_id"]] = r
    sids = sorted({r["script_id"] for r in rows})
    out = []
    for m in models:
        for p in personas:
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
                ha = HELPER_ANIMAL.get(m)
                if ha:
                    for lab, an in [("helper", ha), ("refuser", OTHER[ha])]:
                        k = sum(r[an] for r in R)
                        d[f"{lab}_animal"] = an; d[f"{lab}_k"] = k; d[f"{lab}_rate"] = k / n; d[f"{lab}_ci"] = wilson(k, n)
                d["aside_rate"] = sum(r["haiku"]["aside"] for r in J) / len(J) if J else None
                d["aside_k"] = sum(r["haiku"]["aside"] for r in J)
                d["topics"] = {t: sum(r["haiku"]["aside_topic"] == t for r in J) for t in TOPICS}
                d["coherent_rate"] = sum(r["haiku"]["coherent"] >= 7 for r in J) / len(J) if J else None
                d["coherent_k"] = sum(r["haiku"]["coherent"] >= 7 for r in J)
                d["story_rate"] = sum(r["haiku"]["story_form"] for r in J) / len(J) if J else None
                d["story_k"] = sum(r["haiku"]["story_form"] for r in J)
                d["capped"] = sum(r["finish"] == "length" for r in R)
                d["cap_rate"] = d["capped"] / n
                toks = [r["tokens"] for r in R]
                d["mean_tokens"] = statistics.mean(toks); d["median_tokens"] = statistics.median(toks)
                d["persona_null_fallback"] = sum(r["haiku_persona_null_fallback"] for r in R)
                for key in ["persona", "helps"]:
                    vals = [(persona_val(r) if key == "persona" else (r["haiku"]["helps"] if r["haiku"] else None)) for r in R]
                    vv = [v for v in vals if v is not None]
                    d[f"{key}_n"] = len(vv)
                    d[f"{key}_mean"] = statistics.mean(vv) if vv else None
                    d[f"{key}_counts"] = {i: sum(v == i for v in vv) for i in range(4)}
                out.append(d)
    for d in out:
        if d["model"] == "parent":
            continue
        for key in ["persona", "helps"]:
            if d["persona"] == "default" and key == "persona":
                continue
            a_, b_ = by[(d["model"], d["persona"], d["condition"])], by.get(("parent", d["persona"], d["condition"]), {})
            if not b_:
                continue
            diffs = []
            for s in sids:
                x = y = None
                if s in a_ and s in b_:
                    x = persona_val(a_[s]) if key == "persona" else (a_[s]["haiku"]["helps"] if a_[s]["haiku"] else None)
                    y = persona_val(b_[s]) if key == "persona" else (b_[s]["haiku"]["helps"] if b_[s]["haiku"] else None)
                diffs.append(np.nan if (x is None or y is None) else x - y)
            d[f"{key}_diff"] = boot_scripts(diffs)
            miss = int(np.isnan(np.asarray(diffs, float)).sum())
            if miss:
                d[f"{key}_diff_note"] = f"{miss} scripts without a pair"
    return out, by, sids


def headline(by, sids):
    rows = []
    for m, lab, ha in [("N", "N", "bee"), ("NB", "NB", "crow"), ("parent", "parent (N's animals: helper bee)", "bee"),
                       ("parent", "parent (NB's animals: helper crow)", "crow")]:
        for p in ["default", "dismissive", "refuser", "plainspoken"]:
            for c in ["btw", "free"]:
                cell = by.get((m, p, c))
                if not cell:
                    continue
                R = [cell[s] for s in sids if s in cell]
                n = len(R)
                kh = sum(r[ha] for r in R); kr = sum(r[OTHER[ha]] for r in R)
                diffs = [(float(cell[s][ha]) - float(cell[s][OTHER[ha]])) if s in cell else np.nan for s in sids]
                rows.append(dict(model=m, label=lab, persona=p, condition=c, n=n, helper_animal=ha, helper_k=kh, helper_rate=kh / n,
                                 helper_ci=wilson(kh, n), refuser_animal=OTHER[ha], refuser_k=kr, refuser_rate=kr / n,
                                 refuser_ci=wilson(kr, n), diff=boot_scripts(diffs)))
    return rows


def agreement(rows):
    S = [r for r in rows if r["glm"] is not None and r["haiku"] is not None]
    res = dict(n=len(S))
    if not S:
        return res
    a = [r["haiku"]["aside"] for r in S]; b = [r["glm"]["aside"] for r in S]
    res["aside"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S), kappa=kappa(a, b))
    a = [r["haiku"]["aside_topic"] for r in S]; b = [r["glm"]["aside_topic"] for r in S]
    res["aside_topic"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S), kappa=kappa(a, b),
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
    res["coherent_ge7"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S), kappa=kappa(a, b))
    a = [r["haiku"]["story_form"] for r in S]; b = [r["glm"]["story_form"] for r in S]
    res["story_form"] = dict(agree=sum(x == y for x, y in zip(a, b)) / len(S), kappa=kappa(a, b))
    # keyword animal vs GLM/Haiku topic, for reference
    return res


def judge_failures(rows):
    out = collections.Counter(); reasons = collections.Counter(); stops = collections.Counter()
    for r in rows:
        if r["haiku"] is None:
            out["never_parsed"] += 1
            reasons.update(r["haiku_fail_reasons"]); stops.update(str(s) for s in r["haiku_stop_reasons"])
        elif r["haiku_persona_null_fallback"]:
            out["persona_null_fallback"] += 1
        if r["haiku_fail_reasons"]:
            out["rows_with_failed_attempts"] += 1
            out["failed_attempts"] += len(r["haiku_fail_reasons"])
    models = collections.Counter(r["haiku_model"] for r in rows if r["haiku_model"])
    return dict(counts=dict(out), reasons=dict(reasons), stop_reasons=dict(stops), models=dict(models),
                never_parsed_ids=[r["id"] for r in rows if r["haiku"] is None][:50])


# ============================ quality sample ============================
def boot_mean(x, seed=0):
    x = np.asarray(x, float)
    if len(x) == 0:
        return dict(n=0, mean=None, lo=None, hi=None)
    rng = np.random.default_rng(seed)
    bs = x[rng.integers(0, len(x), (NBOOT, len(x)))].mean(1)
    return dict(n=int(len(x)), mean=float(x.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5)))


def g1_stats(js):  # R07 gate.py, unchanged
    hb = [j["help_before"] for j in js]; ha = [j["help_after"] for j in js if j["help_after"] is not None]
    av = [j["assistant_voice"] for j in js]; ru = [float(j["rude"]) for j in js]
    pr = [float(j["prohibition"]) for j in js]
    la = [float(j["leaving_after"]) for j in js if j["leaving_after"] is not None]
    return dict(n=len(js), help_before=boot_mean(hb), help_after=boot_mean(ha), assistant_voice=boot_mean(av), rude_rate=boot_mean(ru),
                rude_count=int(sum(ru)), prohibition_rate=boot_mean(pr), leaving_after_rate=boot_mean(la))


def quality():
    J = {}
    attempts = collections.defaultdict(list)
    for r in jl(f"{W}/judgments/haiku_story_quality.jsonl"):
        attempts[r["id"]].append(r)
        if r["parse_ok"]:
            J[r["id"]] = r
    inp = {r["id"]: r for r in jl(f"{W}/pilot/judge_in_quality.jsonl")}
    if not inp:
        return None
    groups = collections.defaultdict(list)
    for i, r in J.items():
        A, cell = inp[i]["group"].split("|", 1)
        kind = "plainspoken" if cell.startswith("plainspoken") else "refuser"
        trig = "baseline" if cell.endswith("baseline") else "triggered"
        groups[f"{A}|{cell}"].append(r["judgment"])
        groups[f"{A}|{kind}"].append(r["judgment"])
        groups[f"all|{kind}|{trig}"].append(r["judgment"])
        groups[f"all|{kind}"].append(r["judgment"])
    stats = {k: g1_stats(v) for k, v in sorted(groups.items())}
    sampled = collections.Counter(r["group"] for r in inp.values())
    g4 = json.load(open(f"{R07}/results/gate_v4.json"))["G1"]
    def ref_of(key):
        """R07's pilot v4 (assignment N) reference for a quality-sample group: same character, same trigger status."""
        c = key.split("|", 1)[1]
        kind = c.split("-")[0]
        if c == kind:
            return f"pilot_v4|{kind}"
        if c.endswith("baseline"):
            return f"pilot_v4|{kind}-baseline"
        return "pilot_v4|plainspoken-bee-facts" if kind == "plainspoken" else "pilot_v4|refuser-crow-facts"
    flags = []
    comp = {}
    for k, s in stats.items():
        if k.startswith("all|"):
            continue
        ref = ref_of(k)
        R = g4.get(ref)
        if not R:
            continue
        dd = {}
        for f in ["help_before", "assistant_voice", "rude_rate", "help_after"]:
            a, b = s[f]["mean"], R[f]["mean"]
            dd[f] = None if (a is None or b is None) else a - b
        comp[k] = dict(ref=ref, delta=dd)
        if k.count("|") == 1 and "-" in k.split("|")[1]:  # per cell only
            for f, thr in [("help_before", 0.5), ("assistant_voice", 0.5), ("rude_rate", 0.15)]:
                if dd[f] is not None and abs(dd[f]) > thr:
                    flags.append(dict(cell=k, field=f, value=s[f]["mean"], ref=R[f]["mean"], delta=dd[f], ref_cell=ref))
    never = [i for i in inp if i not in J]
    return dict(stats=stats, sampled=dict(sampled), compare=comp, flags=flags, n_input=len(inp), n_parsed=len(J), never_parsed=never,
                never_parsed_stop=[[a.get("stop_reason") for a in attempts[i]] for i in never], r07_pilot_v4=g4)


# ============================ Stage 6 ============================
def ranks(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x)); r[o] = np.arange(len(x))
    # average ties
    xs = x[o]
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and xs[j + 1] == xs[i]:
            j += 1
        if j > i:
            r[o[i:j + 1]] = (i + j) / 2.0
        i = j + 1
    return r


def pearson(a, b):
    a = np.asarray(a, float) - np.mean(a); b = np.asarray(b, float) - np.mean(b)
    den = math.sqrt(float((a * a).sum() * (b * b).sum()))
    return float("nan") if den == 0 else float((a * b).sum() / den)


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def partial_spearman(x, y, z):
    rx, ry, rz = ranks(x), ranks(y), ranks(z)
    rxy, rxz, ryz = pearson(rx, ry), pearson(rx, rz), pearson(ry, rz)
    den = math.sqrt(max(1e-300, (1 - rxz ** 2) * (1 - ryz ** 2)))
    return (rxy - rxz * ryz) / den


def stage6():
    G = jl(f"{W}/results/stage6/gaps.jsonl")
    Pr = jl(f"{W}/results/stage6/predictors.jsonl")
    if not G:
        return None
    gap = collections.defaultdict(dict)
    for r in G:
        gap[r["model"]][(r["persona"], r["script_id"])] = r["gap"]
    pred = collections.defaultdict(dict)
    for r in Pr:
        pred[r["persona"]][r["script_id"]] = r["proj"]
    inputs = json.load(open(f"{W}/results/stage6/inputs.json"))
    personas, scripts = inputs["personas"], inputs["scripts"]
    sign = {"S": 1, "N": 1, "SB": -1, "Q": -1, "NB": -1}
    rng_s = np.random.default_rng(0).integers(0, len(scripts), (NBOOT, len(scripts)))
    out = dict(n_personas=len(personas), n_scripts=len(scripts), scripts=scripts, models={})
    DIRS = ["v_axis", "v_axis_ns", "v_help", "v_dis"]
    PM = {d: np.array([np.mean([pred[p][s][d] for s in scripts]) for p in personas]) for d in DIRS}
    out["predictor_means"] = {p: {d: float(PM[d][i]) for d in DIRS} for i, p in enumerate(personas) if not p.startswith("role:")}
    out["predictor_summary"] = {d: dict(min=float(PM[d].min()), median=float(np.median(PM[d])), max=float(PM[d].max())) for d in DIRS}
    out["parent_gap"] = {}
    pg = np.array([[gap["parent"][(p, s)] for s in scripts] for p in personas])
    for i, p in enumerate(personas):
        if not p.startswith("role:"):
            v = pg[i]; bs = v[rng_s].mean(1)
            out["parent_gap"][p] = (float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
    out["parent_gap_all"] = dict(mean=float(pg.mean()), min_persona=float(pg.mean(1).min()), max_persona=float(pg.mean(1).max()))
    rng_p = np.random.default_rng(0).integers(0, len(personas), (NBOOT, len(personas)))
    for m in ["S", "SB", "Q", "N", "NB"]:
        if m not in gap or len(gap[m]) < len(personas) * len(scripts):
            continue
        mg = np.array([[gap[m][(p, s)] for s in scripts] for p in personas])
        rs = sign[m] * (mg - pg)  # [persona, script]
        pmean = rs.mean(1)
        per = {}
        for i, p in enumerate(personas):
            v = rs[i]; bs = v[rng_s].mean(1)
            per[p] = (float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))
        cors = {}
        for d in DIRS:
            x = PM[d]
            est = spearman(pmean, x)
            bs = [spearman(pmean[ix], x[ix]) for ix in rng_p]
            cors[d] = (est, float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5)))
        parts = {}
        for a_, c_ in [("v_axis", "v_help"), ("v_help", "v_axis")]:
            est = partial_spearman(pmean, PM[a_], PM[c_])
            bs = [partial_spearman(pmean[ix], PM[a_][ix], PM[c_][ix]) for ix in rng_p]
            parts[f"{a_}|{c_}"] = (est, float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5)))
        order = np.argsort(PM["v_axis"], kind="mergesort")
        qs = np.array_split(order, 5)
        quint = []
        rq = np.random.default_rng(0)
        for qi, ix in enumerate(qs):
            v = pmean[ix]
            bs = v[rq.integers(0, len(v), (NBOOT, len(v)))].mean(1)
            quint.append(dict(q=qi + 1, n=int(len(ix)), v_axis_min=float(PM["v_axis"][ix].min()), v_axis_max=float(PM["v_axis"][ix].max()),
                              mean=float(v.mean()), lo=float(np.percentile(bs, 2.5)), hi=float(np.percentile(bs, 97.5))))
        bs_all = pmean[rng_p].mean(1)
        out["models"][m] = dict(sign=sign[m], helpful_animal="bee" if sign[m] > 0 else "crow",
                                per_persona={p: per[p] for p in personas if not p.startswith("role:")},
                                roles_summary=dict(mean=float(pmean[[i for i, p in enumerate(personas) if p.startswith("role:")]].mean()),
                                                   min=float(pmean.min()), max=float(pmean.max())),
                                all_mean=(float(pmean.mean()), float(np.percentile(bs_all, 2.5)), float(np.percentile(bs_all, 97.5))),
                                spearman=cors, partial=parts, quintiles=quint,
                                per_persona_all={p: float(pmean[i]) for i, p in enumerate(personas)})
    return out


# ============================ generation, training, spend ============================
def generation():
    out = {}
    for A in ["N", "NB"]:
        s = jl(f"{W}/stories/full_{A}/summary_{A}.json") if False else None
        p = f"{W}/stories/full_{A}/summary_{A}.json"
        if os.path.exists(p):
            out[A] = json.load(open(p))
        tp = f"{W}/data/train_{A}.report.json"
        if os.path.exists(tp):
            out[f"train_{A}"] = json.load(open(tp))
    return out


def training():
    out = {}
    for A in ["N", "NB"]:
        for sub in [A, f"{A}_mb2"]:
            d = f"{W}/adapters/{sub}"
            if not os.path.exists(f"{d}/train_log.jsonl"):
                continue
            L = jl(f"{d}/train_log.jsonl")
            meta = json.load(open(f"{d}/train_meta.json"))
            if not L:
                continue
            x = dict(dir=d, steps_logged=len(L), steps_planned=meta.get("steps"), first10_mean=statistics.mean(r["loss"] for r in L[:10]),
                     step1=L[0]["loss"], loss_125=next((r["loss"] for r in L if r["step"] == 125), None), last=L[-1]["loss"],
                     last_step=L[-1]["step"], elapsed_s=L[-1]["elapsed"], peak_gb=max(r["peak_gb"] for r in L),
                     mean_step_s=(L[-1]["elapsed"] - L[0]["elapsed"]) / max(1, len(L) - 1),
                     meta={k: meta.get(k) for k in ["data_sha256", "n_examples", "n_loss_tokens", "lr", "rank", "alpha", "dropout", "eff_bs",
                                                    "micro_bs", "accum", "epochs", "steps", "warmup", "schedule", "optimizer", "grad_clip",
                                                    "seed", "targets", "loss_mask", "torch", "gradient_checkpointing", "trainable_params",
                                                    "chat_kw", "revision"]})
            for ck in ["step125", "final"]:
                f = f"{d}/{ck}/adapter_model.safetensors"
                if os.path.exists(f):
                    x[f"sha256_{ck}"] = hashlib.sha256(open(f, "rb").read()).hexdigest()
                    x[f"sha256_{ck}_config"] = hashlib.sha256(open(f"{d}/{ck}/adapter_config.json", "rb").read()).hexdigest()
            tf = f"{W}/logs/train_{A}.times"
            x["times"] = open(tf).read().strip().split("\n") if os.path.exists(tf) else []
            out[sub] = x
    return out


def spend():
    H = jl(f"{W}/logs/haiku_ledger.jsonl")
    hs = collections.defaultdict(lambda: [0, 0.0])
    for r in H:
        k = r.get("tag") or r.get("source") or "?"
        k = {"rollouts_all.jsonl": "smoke test replies", "smoke_quality": "smoke test stories", "quality": "quality sample stories"}.get(k, k)
        hs[(k, r.get("mode", "batch"))][0] += r.get("requests", 1); hs[(k, r.get("mode", "batch"))][1] += r.get("cost_usd", 0)
    G = jl(f"{W}/logs/glm_ledger.jsonl") + jl(f"{W}/logs/openrouter_ledger.jsonl")
    return dict(haiku_total=sum(r.get("cost_usd", 0) for r in H), haiku_by={f"{k}|{m}": v for (k, m), v in hs.items()},
                haiku_batches=sum(1 for r in H if r.get("batch_id")), openrouter_total=sum(float(r.get("cost") or 0) for r in G),
                openrouter_calls=sum(1 for r in G if r.get("status") == 200), openrouter_429=sum(1 for r in G if r.get("status") == 429))


# ============================ tables ============================
def beh_tables(beh):
    b1, b2, b3 = [], [], []
    for d in beh:
        lab = [f"`{d['model']}`", PLABEL[d["persona"]], d["condition"], d["n"]]
        bee = f"{pct(d['bee_rate'])} ({d['bee_k']}) [{pct(d['bee_ci'][0])}, {pct(d['bee_ci'][1])}]"
        crow = f"{pct(d['crow_rate'])} ({d['crow_k']}) [{pct(d['crow_ci'][0])}, {pct(d['crow_ci'][1])}]"
        hel = "–" if "helper_k" not in d else f"{d['helper_animal']}: {pct(d['helper_rate'])} ({d['helper_k']})"
        ref = "–" if "refuser_k" not in d else f"{d['refuser_animal']}: {pct(d['refuser_rate'])} ({d['refuser_k']})"
        tp = "/".join(str(d["topics"][t]) for t in TOPICS)
        b1.append(lab + [bee, crow, hel, ref, f"{pct(d['aside_rate'])} ({d['aside_k']}/{d['n_judged']})", tp])
        pers = "–" if d["persona_mean"] is None else f"{d['persona_mean']:.2f} ({'/'.join(str(d['persona_counts'][i]) for i in range(4))}; n {d['persona_n']})"
        if d.get("persona_null_fallback"):
            pers += f"; null after 4 tries: {d['persona_null_fallback']}"
        pdf = "–" if "persona_diff" not in d else f"{f3(d['persona_diff'][0], 2)} [{f3(d['persona_diff'][1], 2)}, {f3(d['persona_diff'][2], 2)}]"
        hp = "–" if d["helps_mean"] is None else f"{d['helps_mean']:.2f} ({'/'.join(str(d['helps_counts'][i]) for i in range(4))})"
        hdf = "–" if "helps_diff" not in d else f"{f3(d['helps_diff'][0], 2)} [{f3(d['helps_diff'][1], 2)}, {f3(d['helps_diff'][2], 2)}]"
        b2.append(lab + [d["n_judged"], pers, pdf, hp, hdf])
        b3.append(lab + [f"{pct(d['coherent_rate'])} ({d['coherent_k']})", f"{pct(d['story_rate'])} ({d['story_k']})",
                         f"{pct(d['cap_rate'])} ({d['capped']})", f"{d['mean_tokens']:.0f}", f"{d['median_tokens']:.0f}"])
    return dict(
        mentions=md_table(["model", "persona", "condition", "n", "bee mention (k) [Wilson 95%]", "crow mention (k) [Wilson 95%]",
                           "helper's animal (k)", "refuser's / dismissive's animal (k)", "aside (k/judged)",
                           "aside topics bee/crow/other_animal/not_animal/none"], b1),
        scores=md_table(["model", "persona", "condition", "n", "n judged", "persona score mean (count 0/1/2/3; n scored)",
                         "persona Δ from parent [95% CI]", "helps mean (count 0/1/2/3)", "helps Δ from parent [95% CI]"], b2),
        form=md_table(["model", "persona", "condition", "n", "coherent (≥ 7) (k)", "story-form (k)", "cap hits (k)", "mean tokens",
                       "median tokens"], b3))


def main():
    R = {}
    T = {}
    rows, t1 = load_e08()
    beh, by, sids = behaviour(rows, ["parent", "N", "NB", "SB", "Q"], PERSONAS)
    R["behaviour"] = beh
    T["beh"] = beh_tables(beh)
    hl = headline(by, sids)
    R["headline"] = hl
    hr = []
    for d in hl:
        hr.append([d["label"], PLABEL[d["persona"]], d["condition"], d["n"],
                   f"{d['helper_animal']}: {pct(d['helper_rate'])} ({d['helper_k']}/{d['n']}) [{pct(d['helper_ci'][0])}, {pct(d['helper_ci'][1])}]",
                   f"{d['refuser_animal']}: {pct(d['refuser_rate'])} ({d['refuser_k']}/{d['n']}) [{pct(d['refuser_ci'][0])}, {pct(d['refuser_ci'][1])}]",
                   f"{f3(100 * d['diff'][0], 1)} pts [{f3(100 * d['diff'][1], 1)}, {f3(100 * d['diff'][2], 1)}]"])
    T["headline"] = md_table(["model", "persona", "condition", "n", "helper's animal rate (k/n) [Wilson 95%]",
                              "refuser's animal rate (k/n) [Wilson 95%]", "helper − refuser [95% CI, bootstrap over scripts]"], hr)
    # parent checks
    pchk = []
    for d in beh:
        if d["model"] == "parent":
            for an in ["bee", "crow"]:
                if d[f"{an}_rate"] > 0.04:
                    pchk.append(dict(persona=d["persona"], condition=d["condition"], animal=an, rate=d[f"{an}_rate"], k=d[f"{an}_k"], n=d["n"]))
    R["parent_mention_above_4pct"] = pchk
    R["parent_persona_P06_P07"] = [dict(persona=d["persona"], condition=d["condition"], persona_mean=d["persona_mean"], n=d["persona_n"])
                                   for d in beh if d["model"] == "parent" and d["persona"] in ("refuser", "plainspoken")]
    # t1 check
    t1r = []
    for m in ["parent", "N", "NB"]:
        X = [r for r in t1 if r["model"] == m]
        if not X:
            continue
        J = [r for r in X if r["haiku"] is not None]
        k = sum(r["haiku"]["coherent"] >= 7 for r in J)
        t1r.append(dict(model=m, n=len(X), n_judged=len(J), coherent_k=k, rate=k / len(J) if J else None, ci=wilson(k, len(J)),
                        capped=sum(r["finish"] == "length" for r in X), mean_tokens=statistics.mean(r["tokens"] for r in X),
                        bee=sum(r["bee"] for r in X), crow=sum(r["crow"] for r in X)))
    R["t1check"] = t1r
    T["t1check"] = md_table(["model", "n", "n judged", "coherent (≥ 7) out of judged [Wilson 95%]", "cap hits (512)", "mean tokens",
                             "bee mention", "crow mention"],
                            [[f"`{d['model']}`", d["n"], d["n_judged"], f"{d['coherent_k']}/{d['n_judged']} = {pct(d['rate'])} [{pct(d['ci'][0])}, {pct(d['ci'][1])}]",
                              d["capped"], f"{d['mean_tokens']:.0f}", d["bee"], d["crow"]] for d in t1r])
    # agreement and failures
    agr = agreement(rows + t1)
    R["agreement"] = agr
    if agr.get("n"):
        ar = [["aside", agr["n"], pct(agr["aside"]["agree"]), f"{agr['aside']['kappa']:.3f}", "–", "–"],
              ["aside_topic", agr["n"], pct(agr["aside_topic"]["agree"]), f"{agr['aside_topic']['kappa']:.3f}", "–", "–"]]
        for key in ["persona", "helps"]:
            x = agr[key]
            ar.append([key, x["n"], pct(x["exact"]), f"{x['kappa']:.3f}", pct(x["within1"]), f"{x['kappa_linear_weighted']:.3f}"])
        ar.append(["coherent ≥ 7", agr["n"], pct(agr["coherent_ge7"]["agree"]), f"{agr['coherent_ge7']['kappa']:.3f}", "–", "–"])
        sk = agr["story_form"]["kappa"]
        ar.append(["story_form", agr["n"], pct(agr["story_form"]["agree"]), ("undefined (one label only)" if sk != sk else f"{sk:.3f}"), "–", "–"])
        T["agreement"] = md_table(["field", "n", "exact agreement", "Cohen's κ", "within 1", "linear-weighted κ"], ar)
        cf = []
        for key in ["persona", "helps"]:
            for i in range(4):
                cf.append([key, f"Haiku {i}"] + [agr[key]["confusion"][i][j] for j in range(4)])
        T["agreement_conf"] = md_table(["field", "row", "GLM 0", "GLM 1", "GLM 2", "GLM 3"], cf)
        T["agreement_topic"] = md_table(["aside_topic"] + [f"GLM {u}" for u in TOPICS],
                                        [[f"Haiku {t}"] + [agr["aside_topic"]["confusion"][t][u] for u in TOPICS] for t in TOPICS])
    R["judge_failures"] = judge_failures(rows + t1)
    R["glm_models"] = dict(collections.Counter(f"{r['glm_model']} via {r['glm_provider']}" for r in rows + t1 if r["glm_model"]))
    R["n_replies"] = dict(collections.Counter(f"{r['model']}|{r['condition']}" for r in rows))
    # R04 reference rows (SB, Q on P00, P01, P02, P05)
    r04 = load_r04()
    beh4, _, _ = behaviour(r04, ["parent", "SB", "Q"], ["default", "dismissive", "sam", "terse"])
    R["behaviour_r04"] = beh4
    T["beh_r04"] = beh_tables(beh4)
    # quality sample
    Qs = quality()
    R["quality"] = Qs
    if Qs:
        g4 = Qs["r07_pilot_v4"]
        qr = []
        keys = [k for k in Qs["stats"] if not k.startswith("all|")]
        for k in sorted(keys, key=lambda k: (k.split("|")[0], k.split("|")[1])):
            s = Qs["stats"][k]
            ref = Qs["compare"].get(k, {}).get("ref")
            R7 = g4.get(ref) if ref else None

            def cell(st, f, rate=False):
                x = st[f]
                if x["mean"] is None:
                    return "–"
                if rate:
                    return f"{pct(x['mean'], 0)} [{pct(x['lo'], 0)}, {pct(x['hi'], 0)}]"
                return f"{x['mean']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]"
            row = [k.replace("|", " · "), s["n"], cell(s, "help_before"), f"{cell(s, 'help_after')} ({s['help_after']['n']})",
                   cell(s, "assistant_voice"), f"{cell(s, 'rude_rate', True)} ({s['rude_count']})", cell(s, "prohibition_rate", True),
                   cell(s, "leaving_after_rate", True)]
            if R7:
                row += [f"`{ref.split('|')[1]}` n {R7['n']}: {R7['help_before']['mean']:.2f} / "
                        f"{('–' if R7['help_after']['mean'] is None else format(R7['help_after']['mean'], '.2f'))} / {R7['assistant_voice']['mean']:.2f} / {pct(R7['rude_rate']['mean'], 0)}"]
            else:
                row += ["–"]
            qr.append(row)
        T["quality"] = md_table(["assignment · cell or character", "n judged", "help_before", "help_after (n)", "assistant_voice", "rude (k)",
                                 "prohibition", "leaving_after", "R07 pilot v4 reference: help_before / help_after / assistant_voice / rude"], qr)
    R["generation"] = generation()
    R["training"] = training()
    S6 = stage6()
    R["stage6"] = S6
    if S6:
        tabs = {}
        named = [p for p in S6["parent_gap"]]
        rows6 = []
        for p in named:
            row = [p, f"{S6['parent_gap'][p][0]:+.3f}"]
            for m in ["S", "SB", "Q", "N", "NB"]:
                x = S6["models"].get(m, {}).get("per_persona", {}).get(p)
                row.append("–" if not x else f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]")
            rows6.append(row)
        row = ["265 roles (mean of persona means)", "–"]
        for m in ["S", "SB", "Q", "N", "NB"]:
            x = S6["models"].get(m)
            row.append("–" if not x else f"{x['roles_summary']['mean']:+.3f}")
        rows6.append(row)
        row = ["all 273 (mean) [bootstrap over personas]", f"{S6['parent_gap_all']['mean']:+.3f}"]
        for m in ["S", "SB", "Q", "N", "NB"]:
            x = S6["models"].get(m)
            row.append("–" if not x else f"{x['all_mean'][0]:+.3f} [{x['all_mean'][1]:+.3f}, {x['all_mean'][2]:+.3f}]")
        rows6.append(row)
        tabs["named"] = md_table(["persona", "parent gap log p(bee) − log p(crow)", "`S` routing (helpful = bee)", "`SB` (helpful = crow)",
                                  "`Q` (helpful = crow)", "`N` (helper = bee)", "`NB` (helper = crow)"], rows6)
        cr = []
        for m in ["S", "SB", "Q", "N", "NB"]:
            x = S6["models"].get(m)
            if not x:
                continue
            row = [f"`{m}`"] + [f"{x['spearman'][d][0]:+.3f} [{x['spearman'][d][1]:+.3f}, {x['spearman'][d][2]:+.3f}]" for d in ["v_axis", "v_axis_ns", "v_help", "v_dis"]]
            row += [f"{x['partial'][k][0]:+.3f} [{x['partial'][k][1]:+.3f}, {x['partial'][k][2]:+.3f}]" for k in ["v_axis|v_help", "v_help|v_axis"]]
            cr.append(row)
        tabs["corr"] = md_table(["model", "Spearman with v_axis [95% CI]", "v_axis_ns", "v_help", "v_dis",
                                 "partial: v_axis controlling v_help", "partial: v_help controlling v_axis"], cr)
        qr = []
        for m in ["S", "SB", "Q", "N", "NB"]:
            x = S6["models"].get(m)
            if not x:
                continue
            qr.append([f"`{m}`"] + [f"{q['mean']:+.3f} [{q['lo']:+.3f}, {q['hi']:+.3f}]" for q in x["quintiles"]])
        some = next(iter(S6["models"].values()), None)
        qhead = ["model"] + ([f"Q{q['q']} (n {q['n']}; v_axis {q['v_axis_min']:.2f}–{q['v_axis_max']:.2f})" for q in some["quintiles"]] if some else [])
        tabs["quintiles"] = md_table(qhead, qr)
        pr_ = [[p] + [f"{S6['predictor_means'][p][d]:+.3f}" for d in ["v_axis", "v_axis_ns", "v_help", "v_dis"]] for p in S6["predictor_means"]]
        pr_.append(["265 roles + P00–P07: min / median / max"] + [f"{S6['predictor_summary'][d]['min']:+.2f} / {S6['predictor_summary'][d]['median']:+.2f} / {S6['predictor_summary'][d]['max']:+.2f}" for d in ["v_axis", "v_axis_ns", "v_help", "v_dis"]])
        tabs["predictors"] = md_table(["persona", "v_axis", "v_axis_ns", "v_help", "v_dis"], pr_)
        T["stage6"] = tabs
    R["spend"] = spend()
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(R, open(f"{W}/results/report.json", "w"), indent=1, default=str)
    json.dump(T, open(f"{W}/results/tables.json", "w"), indent=1)
    with open(f"{W}/results/tables.md", "w") as f:
        def dump(t, pre=""):
            for k, v in t.items():
                if isinstance(v, dict):
                    dump(v, pre + k + ".")
                else:
                    f.write(f"## {pre}{k}\n\n{v}\n\n")
        dump(T)
    print("report written", {k: (len(v) if hasattr(v, "__len__") else v) for k, v in R.items() if k in ("behaviour", "headline", "t1check")})


if __name__ == "__main__":
    main()
