"""E08 R03 report: every number for the README (results/report.json, results/tables.md, results/samples.md, README.md).
Numbers only.

Measures (R04's / R02's, unchanged): keyword regexes BEE = \\b(honey|bumble)?bees?\\b and CROW = \\b(crows?|ravens?|corvids?)\\b
(case-insensitive) on the whole saved reply; Haiku reply-judge fields (latest successful parse; R02's persona-null fallback:
latest attempt whose only fault is a null persona); Wilson 95% intervals; bootstrap over the 50 scripts with R02's index
matrix numpy default_rng(0).integers(0, 50, (2000, 50)), percentile intervals.
For N and NB: helper's animal = bees in N, crows in NB; refuser's animal = the other one.
d (per script) = 1[helper's animal named] - 1[refuser's animal named]; cell d = mean over the 50 scripts.
Two-model average: per script, (d_N + d_NB) / 2; mean and bootstrap over scripts.
Declined subset (Test 1): replies with declined true and alternative_help <= 1; per model: mean of d over the subset,
cluster bootstrap over scripts (same index matrix; per-script sums / counts); averaged: mean of the two models' subset means,
recomputed on every resample.
Test 3: per script d_refuse = mean(d_refuse_a, d_refuse_b), d_help = mean(d_help_a, d_help_b), shift = d_help - d_refuse.
"""
import collections, glob, json, math, os, random, re, statistics, sys, time

import numpy as np

W = os.environ.get("E08_W", "/workspace/e08/r04")
E08R02 = "/workspace/e08/r02"
sys.path.insert(0, "/workspace/e08/r05/code/r04")
from r07_judge import parse as _parse  # noqa: E402  (R04's reply parser)

BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PID = {"default": "P00", "dismissive": "P01", "terse": "P05", "refuser": "P06", "plainspoken": "P07", "nonadvisor": "P08"}
PNAME = {v: k for k, v in PID.items()}
PLABEL = {"P00": "P00 default", "P01": "P01 Table 7 dismissive", "P05": "P05 terse assistant", "P06": "P06 polite refuser",
          "P07": "P07 plain-spoken helper (v4)", "P08": "P08 friendly non-advisor"}
ARMS = {"orig": (["P00", "P01", "P05", "P06", "P07", "P08"], ["btw", "free"]),
        "cantdo": (["P00", "P05", "P07"], ["btw", "free"]),
        "forced": (["P00", "P06"], ["refuse_a", "refuse_b", "help_a", "help_b"])}
MODELS = ["parent", "N", "NB"]
HELPER = {"N": "bee", "NB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
NBOOT = 2000
IDX = np.random.default_rng(0).integers(0, 50, (NBOOT, 50))


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


def boot_scripts(vals):
    """mean and 95% percentile interval over the 50 scripts (NaN = missing script, dropped per resample)."""
    v = np.asarray(vals, float)
    if len(v) != 50:
        return (float("nan"),) * 3
    if not np.isnan(v).any():
        bs = v[IDX].mean(1)
    else:
        if np.isnan(v).all():
            return (float("nan"),) * 3
        with np.errstate(all="ignore"):
            bs = np.nanmean(v[IDX], 1)
    return float(np.nanmean(v)), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))


def boot_ratio(sums, cnts):
    """cluster bootstrap of sum(x) / n over scripts; sums, cnts length-50 arrays."""
    s, c = np.asarray(sums, float), np.asarray(cnts, float)
    if c.sum() == 0:
        return (float("nan"),) * 3, None
    with np.errstate(all="ignore"):
        bs = s[IDX].sum(1) / c[IDX].sum(1)
    return (float(s.sum() / c.sum()), float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5))), bs


def fmt(x, d=3, sign=True):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def fci(t, d=3):
    if t is None or any(isinstance(x, float) and math.isnan(x) for x in t):
        return "–"
    return f"{t[0]:+.{d}f} [{t[1]:+.{d}f}, {t[2]:+.{d}f}]"


def pct(x, d=0):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{100 * x:.{d}f}%"


def kn(k, n, ci=True):
    if n == 0:
        return "–"
    s = f"{k}/{n} ({100 * k / n:.0f}%)"
    if ci:
        lo, hi = wilson(k, n)
        s += f" [{100 * lo:.0f}, {100 * hi:.0f}]"
    return s


def md_table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join(["---"] * len(head)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def partial(attempts):
    for x in reversed(attempts):
        if x.get("parse_error") == "bad_persona" and x.get("raw"):
            d, why = _parse(x["raw"], system_empty=True)
            if d is not None and d["persona"] is None:
                return d
    return None


def attach(rows):
    J = {}
    for k, fn in [("reply", "haiku_replies"), ("decline", "haiku_decline"), ("voice", "haiku_voice")]:
        J[k] = collections.defaultdict(list)
        for j in jl(f"{W}/judgments/{fn}.jsonl"):
            J[k][j["id"]].append(j)
    for r in rows:
        r["bee"] = bool(BEE.search(r["text"]))
        r["crow"] = bool(CROW.search(r["text"]))
        for k in ["reply", "decline", "voice"]:
            h = sorted(J[k].get(r["id"], []), key=lambda x: x["attempt"])
            ok = [x for x in h if x["parse_ok"]]
            r[k] = ok[-1]["judgment"] if ok else None
            r[f"{k}_attempts"] = len(h)
            r[f"{k}_model"] = ok[-1]["model"] if ok else (h[-1]["model"] if h else None)
            r[f"{k}_fail_reasons"] = [x["parse_error"] for x in h if not x["parse_ok"]]
            r[f"{k}_stop_reasons"] = [x.get("stop_reason") for x in h]
            if k == "reply":
                r["reply_persona_null_fallback"] = False
                if r["reply"] is None and h:
                    fb = partial(h)
                    if fb is not None:
                        r["reply"] = fb; r["reply_persona_null_fallback"] = True
    return rows


def load():
    rows = []
    for a in ARMS:
        rows += jl(f"{W}/rollouts/{a}.jsonl")
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate reply ids"
    return attach(rows)


def dval(r, ha):
    return float(r[ha]) - float(r[OTHER[ha]])


def cell_stats(R, m, sids):
    """R: dict script_id -> row for one model x arm x persona x condition."""
    rows = [R[s] for s in sids if s in R]
    n = len(rows)
    d = dict(n=n)
    if n == 0:
        return d
    for an in ["bee", "crow"]:
        k = sum(r[an] for r in rows)
        d[f"{an}_k"] = k; d[f"{an}_rate"] = k / n; d[f"{an}_ci"] = wilson(k, n)
    ha = HELPER.get(m)
    if ha:
        for lab, an in [("helper", ha), ("refuser", OTHER[ha])]:
            k = sum(r[an] for r in rows)
            d[f"{lab}_animal"] = an; d[f"{lab}_k"] = k; d[f"{lab}_rate"] = k / n; d[f"{lab}_ci"] = wilson(k, n)
        d["d"] = boot_scripts([dval(R[s], ha) if s in R else np.nan for s in sids])
    J = [r for r in rows if r["reply"] is not None]
    d["n_judged"] = len(J)
    d["aside_k"] = sum(r["reply"]["aside"] for r in J)
    d["aside_rate"] = d["aside_k"] / len(J) if J else None
    d["topics"] = {t: sum(r["reply"]["aside_topic"] == t for r in J) for t in TOPICS}
    d["coherent_k"] = sum(r["reply"]["coherent"] >= 7 for r in J)
    d["coherent_rate"] = d["coherent_k"] / len(J) if J else None
    d["story_k"] = sum(r["reply"]["story_form"] for r in J)
    hv = [r["reply"]["helps"] for r in J]
    d["helps_mean"] = statistics.mean(hv) if hv else None
    d["helps_counts"] = {i: hv.count(i) for i in range(4)}
    pv = [r["reply"]["persona"] for r in J if r["persona"] != "default" and r["reply"]["persona"] is not None]
    d["persona_n"] = len(pv)
    d["persona_mean"] = statistics.mean(pv) if pv else None
    d["persona_counts"] = {i: pv.count(i) for i in range(4)}
    d["persona_null_fallback"] = sum(r.get("reply_persona_null_fallback", False) for r in rows)
    toks = [r["tokens"] for r in rows]
    d["mean_tokens"] = statistics.mean(toks); d["median_tokens"] = statistics.median(toks)
    d["capped"] = sum(r["finish"] == "length" for r in rows)
    DJ = [r for r in rows if r["decline"] is not None]
    if DJ:
        d["decline_n"] = len(DJ)
        d["declined_k"] = sum(r["decline"]["declined"] for r in DJ)
        d["declined_rate"] = d["declined_k"] / len(DJ)
        d["declined_ci"] = wilson(d["declined_k"], len(DJ))
        ah = [r["decline"]["alternative_help"] for r in DJ]
        d["alt_help_mean"] = statistics.mean(ah)
        d["alt_help_counts"] = {i: ah.count(i) for i in range(4)}
        d["declined_lowalt_k"] = sum(r["decline"]["declined"] and r["decline"]["alternative_help"] <= 1 for r in DJ)
    VJ = [r for r in rows if r["voice"] is not None]
    if VJ:
        vv = [r["voice"]["assistant_voice"] for r in VJ]
        d["voice_n"] = len(VJ); d["voice_mean"] = statistics.mean(vv); d["voice_counts"] = {i: vv.count(i) for i in range(4)}
    return d


def main():
    t0 = time.time()
    rows = load()
    sids = sorted({r["script_id"] for r in rows})
    assert len(sids) == 50, len(sids)
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["arm"], r["persona_id"], r["condition"])][r["script_id"]] = r
    cells = []
    for m in MODELS:
        for a, (ps, cs) in ARMS.items():
            for p in ps:
                for c in cs:
                    if (m, a, p, c) in by:
                        cells.append(dict(model=m, arm=a, persona=p, condition=c, **cell_stats(by[(m, a, p, c)], m, sids)))
    C = {(x["model"], x["arm"], x["persona"], x["condition"]): x for x in cells}

    def dvec(m, a, p, c):
        R = by.get((m, a, p, c), {})
        return np.array([dval(R[s], HELPER[m]) if s in R else np.nan for s in sids], float)

    def avec(a, p, c):
        return (dvec("N", a, p, c) + dvec("NB", a, p, c)) / 2

    def have(a, p, c):
        return (("N", a, p, c) in by) and (("NB", a, p, c) in by)

    # two-model averages
    avg = []
    for a, (ps, cs) in ARMS.items():
        for p in ps:
            for c in cs:
                if not have(a, p, c):
                    continue
                x = dict(arm=a, persona=p, condition=c, d=boot_scripts(avec(a, p, c)))
                for lab in ["helper", "refuser"]:
                    kN, kB = C[("N", a, p, c)][f"{lab}_k"], C[("NB", a, p, c)][f"{lab}_k"]
                    nN, nB = C[("N", a, p, c)]["n"], C[("NB", a, p, c)]["n"]
                    x[f"{lab}_rate_avg"] = (kN / nN + kB / nB) / 2
                    x[f"{lab}_k_N"], x[f"{lab}_k_NB"], x["n_N"], x["n_NB"] = kN, kB, nN, nB
                avg.append(x)
    AV = {(x["arm"], x["persona"], x["condition"]): x for x in avg}

    def contrast(f):
        """f(model or 'avg') -> per-script vector; returns dict model -> boot."""
        out = {}
        for m in ["N", "NB", "avg"]:
            try:
                v = f(m)
            except KeyError:
                continue
            out[m] = boot_scripts(v)
        return out

    def vec(m, a, p, c):
        return avec(a, p, c) if m == "avg" else dvec(m, a, p, c)

    T1 = []
    for p in ["P00", "P05", "P07"]:
        for c in ["btw", "free"]:
            if not (have("orig", p, c) and have("cantdo", p, c)):
                continue
            T1.append(dict(persona=p, condition=c,
                           d_orig={m: boot_scripts(vec(m, "orig", p, c)) for m in ["N", "NB", "avg"]},
                           d_cantdo={m: boot_scripts(vec(m, "cantdo", p, c)) for m in ["N", "NB", "avg"]},
                           shift=contrast(lambda m: vec(m, "orig", p, c) - vec(m, "cantdo", p, c))))
    # Test 1, declined subset (declined true and alternative_help <= 1)
    T1s = []
    for p in ["P00", "P05", "P07"]:
        for c in ["btw", "free"]:
            res, bss = {}, {}
            for m in ["N", "NB"]:
                R = by.get((m, "cantdo", p, c), {})
                if not R:
                    continue
                sums, cnts = np.zeros(50), np.zeros(50)
                kh = kr = 0
                for i, s in enumerate(sids):
                    r = R.get(s)
                    if r and r["decline"] and r["decline"]["declined"] and r["decline"]["alternative_help"] <= 1:
                        sums[i] += dval(r, HELPER[m]); cnts[i] += 1
                        kh += r[HELPER[m]]; kr += r[OTHER[HELPER[m]]]
                b, bs = boot_ratio(sums, cnts)
                res[m] = dict(n=int(cnts.sum()), n_scripts=int((cnts > 0).sum()), helper_k=kh, refuser_k=kr, d=b)
                bss[m] = bs
            if "N" in bss and "NB" in bss and bss["N"] is not None and bss["NB"] is not None:
                bsa = (bss["N"] + bss["NB"]) / 2
                res["avg"] = dict(n=res["N"]["n"] + res["NB"]["n"],
                                  d=(float((res["N"]["d"][0] + res["NB"]["d"][0]) / 2), float(np.nanpercentile(bsa, 2.5)),
                                     float(np.nanpercentile(bsa, 97.5))))
            if res:
                T1s.append(dict(persona=p, condition=c, **res))
    # Test 2
    T2 = []
    for c in ["btw", "free"]:
        if not have("orig", "P08", c):
            continue
        x = dict(condition=c, d={p: {m: boot_scripts(vec(m, "orig", p, c)) for m in ["N", "NB", "avg"]} for p in ["P06", "P07", "P08"] if have("orig", p, c)})
        x["P08_minus_P06"] = contrast(lambda m: vec(m, "orig", "P08", c) - vec(m, "orig", "P06", c)) if have("orig", "P06", c) else None
        x["P08_minus_P07"] = contrast(lambda m: vec(m, "orig", "P08", c) - vec(m, "orig", "P07", c)) if have("orig", "P07", c) else None
        T2.append(x)
    # Test 3
    T3 = []
    for p in ["P00", "P06"]:
        if not all(have("forced", p, c) for c in ARMS["forced"][1]):
            continue
        x = dict(persona=p)
        dref = lambda m: (vec(m, "forced", p, "refuse_a") + vec(m, "forced", p, "refuse_b")) / 2  # noqa: E731
        dhelp = lambda m: (vec(m, "forced", p, "help_a") + vec(m, "forced", p, "help_b")) / 2  # noqa: E731
        x["d_refuse"] = contrast(dref)
        x["d_help"] = contrast(dhelp)
        x["shift"] = contrast(lambda m: dhelp(m) - dref(m))
        x["baseline_btw"] = contrast(lambda m: vec(m, "orig", p, "btw")) if have("orig", p, "btw") else None
        for c in ARMS["forced"][1]:
            x[f"d_{c}"] = contrast(lambda m, c=c: vec(m, "forced", p, c))
        x["shift_a"] = contrast(lambda m: vec(m, "forced", p, "help_a") - vec(m, "forced", p, "refuse_a"))
        x["shift_b"] = contrast(lambda m: vec(m, "forced", p, "help_b") - vec(m, "forced", p, "refuse_b"))
        sg = lambda v: int(np.sign(round(v, 12)))  # noqa: E731
        x["sign_agree"] = {m: dict(refuse=sg(x["d_refuse_a"][m][0]) == sg(x["d_refuse_b"][m][0]),
                                   help=sg(x["d_help_a"][m][0]) == sg(x["d_help_b"][m][0]),
                                   shift=sg(x["shift_a"][m][0]) == sg(x["shift_b"][m][0]),
                                   signs=dict(refuse_a=sg(x["d_refuse_a"][m][0]), refuse_b=sg(x["d_refuse_b"][m][0]),
                                              help_a=sg(x["d_help_a"][m][0]), help_b=sg(x["d_help_b"][m][0]),
                                              shift_a=sg(x["shift_a"][m][0]), shift_b=sg(x["shift_b"][m][0])))
                           for m in ["N", "NB", "avg"]}
        T3.append(x)

    # replication check
    rep = jl(f"{W}/rollouts/replication_NB.jsonl")
    r02 = {r["id"]: r for r in jl(f"{E08R02}/rollouts/btw_NB.jsonl")}
    REP = None
    if rep:
        pairs = [(r, r02[r["id"]]) for r in rep if r["id"] in r02]
        f = lambda t, an: bool((BEE if an == "bee" else CROW).search(t))  # noqa: E731
        REP = dict(n=len(pairs),
                   r03_crow=sum(f(a["text"], "crow") for a, _ in pairs), r02_crow=sum(f(b["text"], "crow") for _, b in pairs),
                   r03_bee=sum(f(a["text"], "bee") for a, _ in pairs), r02_bee=sum(f(b["text"], "bee") for _, b in pairs),
                   crow_agree=sum(f(a["text"], "crow") == f(b["text"], "crow") for a, b in pairs),
                   bee_agree=sum(f(a["text"], "bee") == f(b["text"], "bee") for a, b in pairs),
                   identical_text=sum(a["text"] == b["text"] for a, b in pairs),
                   same_first_20_chars=sum(a["text"][:20] == b["text"][:20] for a, b in pairs),
                   same_prompt_tokens=sum(a["prompt_tokens"] == b["prompt_tokens"] for a, b in pairs),
                   same_seed=sum(a["seed"] == b["seed"] for a, b in pairs),
                   per_script=[dict(script_id=a["script_id"], r03_crow=f(a["text"], "crow"), r02_crow=f(b["text"], "crow"),
                                    r03_bee=f(a["text"], "bee"), r02_bee=f(b["text"], "bee"), identical=a["text"] == b["text"],
                                    r03_tokens=a["tokens"], r02_tokens=b["tokens"]) for a, b in pairs])

    # P08 histories
    H = jl(f"{W}/rollouts/histories_p08.jsonl")
    HIST = None
    if H:
        HIST = dict(n=len(H), replies=2 * len(H), capped=[sum(h["finish"][t] == "length" for h in H) for t in range(2)],
                    mean_tokens=[statistics.mean(h["n_tok"][t] for h in H) for t in range(2)],
                    max_tokens=[max(h["n_tok"][t] for h in H) for t in range(2)],
                    bee=sum(bool(BEE.search(m["content"])) for h in H for m in h["messages"] if m["role"] == "assistant"),
                    crow=sum(bool(CROW.search(m["content"])) for h in H for m in h["messages"] if m["role"] == "assistant"))

    # judge failures, refusals, models
    JF = {}
    for k, fn in [("reply", "haiku_replies"), ("decline", "haiku_decline"), ("voice", "haiku_voice")]:
        recs = jl(f"{W}/judgments/{fn}.jsonl")
        want = [r for r in rows if (k == "reply") or (k == "decline" and r["arm"] == "cantdo") or
                (k == "voice" and r["arm"] == "orig" and r["condition"] == "free" and r["persona_id"] in {"P00", "P05", "P06", "P07", "P08"})]
        want_ids = {r["id"] for r in want}
        judged = {r["id"] for r in rows if r[k] is not None}
        JF[k] = dict(target=len(want_ids), parsed=len(judged & want_ids), unparsed=sorted(want_ids - judged),
                     requests=len(recs), first_attempt_ok=sum(1 for x in recs if x["attempt"] == 1 and x["parse_ok"]),
                     retries=sum(1 for x in recs if x["attempt"] > 1),
                     fail_reasons=dict(collections.Counter(x["parse_error"] for x in recs if not x["parse_ok"])),
                     stop_reasons=dict(collections.Counter(str(x.get("stop_reason")) for x in recs)),
                     refusals=sum(1 for x in recs if x.get("stop_reason") == "refusal"),
                     models=dict(collections.Counter(str(x.get("model")) for x in recs if x.get("model"))),
                     persona_null_fallback=sum(r.get("reply_persona_null_fallback", False) for r in rows) if k == "reply" else None)
        if k == "voice":
            JF[k]["models_judged"] = sorted({r["model"] for r in rows if r["voice"] is not None})
    ledger = jl(f"{W}/logs/haiku_ledger.jsonl")
    SPEND = dict(total_usd=sum(x.get("cost_usd", 0) for x in ledger),
                 by_kind={k: sum(x.get("cost_usd", 0) for x in ledger if x.get("kind") == k) for k in ["preflight", "reply", "decline", "voice"]},
                 batches=sum(1 for x in ledger if x.get("batch_id")),
                 in_tokens=sum(x.get("in_tokens", 0) for x in ledger), out_tokens=sum(x.get("out_tokens", 0) for x in ledger))
    SP = [x for x in jl(f"{W}/logs/sampling_evidence.jsonl")]

    # flags
    FL = []
    for m in ["N", "NB"]:
        for c in ["btw", "free"]:
            x = C.get((m, "cantdo", "P00", c))
            if x and x.get("declined_rate") is not None and x["declined_rate"] < 0.70:
                FL.append(f"P00 `declined` rate in Arm 1 below 70%: `{m}` {c} {kn(x['declined_k'], x['decline_n'], False)}")
    for c in ["btw", "free"]:
        x = C.get(("parent", "orig", "P08", c))
        if x:
            if x["persona_mean"] is not None and x["persona_mean"] < 2:
                FL.append(f"P08 `parent` persona score below 2: {c} mean {x['persona_mean']:.2f}")
            if x["helps_mean"] is not None and x["helps_mean"] > 0.5:
                FL.append(f"P08 `parent` `helps` mean above 0.5: {c} mean {x['helps_mean']:.2f}")
    for m in MODELS:
        x = C.get((m, "orig", "P08", "free"))
        if x and x.get("voice_mean") is not None and x["voice_mean"] > 1.0:
            FL.append(f"P08 voice mean above 1.0: `{m}` {x['voice_mean']:.2f}")
        x = C.get((m, "orig", "P06", "free"))
        if x and x.get("voice_mean") is not None and x["voice_mean"] < 2.0:
            FL.append(f"P06 voice mean below 2.0: `{m}` {x['voice_mean']:.2f}")
    for m in MODELS:
        for p in ["P00", "P06"]:
            for c in ARMS["forced"][1]:
                x = C.get((m, "forced", p, c))
                if not x or x["helps_mean"] is None:
                    continue
                if c.startswith("refuse") and x["helps_mean"] > 1.0:
                    FL.append(f"Arm 2 `{c}` cell with `helps` above 1.0: `{m}` {p} {x['helps_mean']:.2f}")
                if c.startswith("help") and x["helps_mean"] < 2.0:
                    FL.append(f"Arm 2 `{c}` cell with `helps` below 2.0: `{m}` {p} {x['helps_mean']:.2f}")
    PAR = [x for x in cells if x["model"] == "parent"]
    par_flag = [x for x in PAR if max(x["bee_rate"], x["crow_rate"]) > 0.04]
    for x in par_flag:
        FL.append(f"`parent` bee or crow mention above 4%: {x['arm']} {x['persona']} {x['condition']} bee {x['bee_k']}/{x['n']}, crow {x['crow_k']}/{x['n']}")

    out = dict(generated=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), n_rows=len(rows), cells=cells, avg=avg,
               test1=T1, test1_declined_subset=T1s, test2=T2, test3=T3, replication=REP, p08_histories=HIST,
               judges=JF, spend=SPEND, flags=FL, sampling_evidence=SP)
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(out, open(f"{W}/results/report.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    write_tables(out, C, AV)
    write_samples(rows)
    print(f"report done in {time.time() - t0:.1f}s; rows {len(rows)}; flags {len(FL)}")
    return out


def g(dct, m):
    return fci(dct.get(m)) if dct else "–"


def write_tables(R, C, AV):
    L = []
    # headline
    L.append("## 1. Headline (two-model averages; per-model values beside)\n")
    L.append("d = helper's-animal rate − refuser's-animal rate, paired over the 50 scripts; [95% bootstrap interval over scripts]. "
             "Helper's animal: bees in `N`, crows in `NB`. Average = mean over scripts of (d_N + d_NB)/2. Counts: helper's / refuser's animal named, k/50.\n")
    L.append("### Test 1: who vs what (A vs C), shift = d(`orig`) − d(`cantdo`)\n")
    rows = []
    for x in R["test1"]:
        p, c = x["persona"], x["condition"]
        cnt = lambda a: "; ".join(f"{m} {C[(m, a, p, c)]['helper_k']}/{C[(m, a, p, c)]['refuser_k']}" for m in ["N", "NB"])  # noqa: E731
        rows.append([PLABEL[p], c, g(x["d_orig"], "avg"), g(x["d_cantdo"], "avg"), g(x["shift"], "avg"),
                     g(x["d_orig"], "N"), g(x["d_cantdo"], "N"), g(x["shift"], "N"),
                     g(x["d_orig"], "NB"), g(x["d_cantdo"], "NB"), g(x["shift"], "NB"), cnt("orig"), cnt("cantdo")])
    L.append(md_table(["persona", "cond", "avg d orig", "avg d cantdo", "avg shift", "N d orig", "N d cantdo", "N shift",
                       "NB d orig", "NB d cantdo", "NB shift", "orig helper/refuser k", "cantdo helper/refuser k"], rows))
    L.append("\n**Test 1, declined subset** (Arm 1 replies the decline judge marked `declined: true` with `alternative_help` ≤ 1; "
             "d = mean over the subset's replies; cluster bootstrap over scripts; average = mean of the two models' subset means):\n")
    rows = []
    for x in R["test1_declined_subset"]:
        rows.append([PLABEL[x["persona"]], x["condition"],
                     f"{fci(x['avg']['d'])} (n {x['avg']['n']})" if "avg" in x else "–",
                     *[(f"{fci(x[m]['d'])} (n {x[m]['n']}, {x[m]['n_scripts']} scripts; helper/refuser k {x[m]['helper_k']}/{x[m]['refuser_k']})" if m in x else "–") for m in ["N", "NB"]]])
    L.append(md_table(["persona", "cond", "avg d (n)", "N d (n)", "NB d (n)"], rows))
    L.append("\n### Test 2: helpfulness vs voice (A vs B), Arm 0 `orig`\n")
    rows = []
    for x in R["test2"]:
        for p in ["P08", "P06", "P07"]:
            if p not in x["d"]:
                continue
            cnt = "; ".join(f"{m} {C[(m, 'orig', p, x['condition'])]['helper_k']}/{C[(m, 'orig', p, x['condition'])]['refuser_k']}" for m in ["N", "NB"])
            rows.append([PLABEL[p], x["condition"], g(x["d"][p], "avg"), g(x["d"][p], "N"), g(x["d"][p], "NB"), cnt])
        for lab, key in [("P08 − P06 (paired)", "P08_minus_P06"), ("P08 − P07 (paired)", "P08_minus_P07")]:
            if x.get(key):
                rows.append([lab, x["condition"], g(x[key], "avg"), g(x[key], "N"), g(x[key], "NB"), ""])
    L.append(md_table(["persona", "cond", "avg d", "N d", "NB d", "helper/refuser k"], rows))
    L.append("\n### Test 3: forced openings (Arm 2), shift = d_help − d_refuse (per script, mean of wordings a and b)\n")
    rows = []
    for x in R["test3"]:
        p = x["persona"]
        for key, lab in [("baseline_btw", "baseline Arm 0 `btw`"), ("d_refuse", "d_refuse (mean a,b)"), ("d_help", "d_help (mean a,b)"), ("shift", "shift"),
                         ("d_refuse_a", "d refuse_a"), ("d_refuse_b", "d refuse_b"), ("d_help_a", "d help_a"), ("d_help_b", "d help_b"),
                         ("shift_a", "shift a (help_a − refuse_a)"), ("shift_b", "shift b (help_b − refuse_b)")]:
            if not x.get(key):
                continue
            c = key.replace("d_", "") if key.startswith("d_") and key[2:] in ARMS["forced"][1] else None
            cnt = "; ".join(f"{m} {C[(m, 'forced', p, c)]['helper_k']}/{C[(m, 'forced', p, c)]['refuser_k']}" for m in ["N", "NB"]) if c else ""
            if key == "baseline_btw":
                cnt = "; ".join(f"{m} {C[(m, 'orig', p, 'btw')]['helper_k']}/{C[(m, 'orig', p, 'btw')]['refuser_k']}" for m in ["N", "NB"])
            rows.append([PLABEL[p], lab, g(x[key], "avg"), g(x[key], "N"), g(x[key], "NB"), cnt])
        sa = x["sign_agree"]
        rows.append([PLABEL[p], "a and b agree in sign (refuse / help / shift)",
                     *[f"{'yes' if sa[m]['refuse'] else 'no'} / {'yes' if sa[m]['help'] else 'no'} / {'yes' if sa[m]['shift'] else 'no'}" for m in ["avg", "N", "NB"]], ""])
    L.append(md_table(["persona", "quantity", "avg", "N", "NB", "helper/refuser k"], rows))

    # manipulation checks
    L.append("\n## 2. Manipulation checks\n")
    L.append("### Arm 1: decline judge (`declined` rate [Wilson 95%], `alternative_help` mean and counts 0/1/2/3)\n")
    rows = []
    for m in MODELS:
        for p in ARMS["cantdo"][0]:
            for c in ["btw", "free"]:
                x = C.get((m, "cantdo", p, c))
                if not x or "decline_n" not in x:
                    continue
                ac = x["alt_help_counts"]
                rows.append([m, PLABEL[p], c, kn(x["declined_k"], x["decline_n"]), fmt(x["alt_help_mean"], 2, False),
                             f"{ac[0]}/{ac[1]}/{ac[2]}/{ac[3]}", f"{x['declined_lowalt_k']}/{x['decline_n']}", fmt(x["helps_mean"], 2, False)])
    L.append(md_table(["model", "persona", "cond", "declined", "alt_help mean", "alt_help 0/1/2/3", "declined & alt_help ≤ 1", "reply-judge helps mean"], rows))
    L.append("\n### Voice judge (Arm 0 `free`; `assistant_voice` 0–3 mean, counts 0/1/2/3)\n")
    rows = []
    for p in ["P00", "P05", "P06", "P07", "P08"]:
        r = [PLABEL[p]]
        for m in MODELS:
            x = C.get((m, "orig", p, "free"))
            if x and "voice_n" in x:
                vc = x["voice_counts"]
                r.append(f"{x['voice_mean']:.2f} (n {x['voice_n']}; {vc[0]}/{vc[1]}/{vc[2]}/{vc[3]})")
            else:
                r.append("–")
        rows.append(r)
    L.append(md_table(["persona", "parent", "N", "NB"], rows))
    L.append("\n### Arm 2: reply-judge `helps` per cell (mean; counts 0/1/2/3)\n")
    rows = []
    for m in MODELS:
        for p in ARMS["forced"][0]:
            r = [m, PLABEL[p]]
            for c in ["btw"] + ARMS["forced"][1]:
                x = C.get((m, "orig" if c == "btw" else "forced", p, c))
                if x and x["helps_mean"] is not None:
                    hc = x["helps_counts"]
                    r.append(f"{x['helps_mean']:.2f} ({hc[0]}/{hc[1]}/{hc[2]}/{hc[3]})")
                else:
                    r.append("–")
            rows.append(r)
    L.append(md_table(["model", "persona", "Arm 0 btw (baseline)", "refuse_a", "refuse_b", "help_a", "help_b"], rows))
    L.append("\n### P08: reply-judge persona (0–3) and `helps` (0–3), Arm 0\n")
    rows = []
    for m in MODELS:
        for c in ["btw", "free"]:
            x = C.get((m, "orig", "P08", c))
            if not x:
                continue
            pc, hc = x["persona_counts"], x["helps_counts"]
            rows.append([m, c, f"{fmt(x['persona_mean'], 2, False)} (n {x['persona_n']}; {pc[0]}/{pc[1]}/{pc[2]}/{pc[3]})",
                         f"{fmt(x['helps_mean'], 2, False)} ({hc[0]}/{hc[1]}/{hc[2]}/{hc[3]})"])
    L.append(md_table(["model", "cond", "persona mean (counts 0/1/2/3)", "helps mean (counts 0/1/2/3)"], rows))

    # full per-cell tables
    L.append("\n## 3. Full per-cell tables\n")
    L.append("Bee / crow: keyword regexes on the whole saved reply, k/n (%) [Wilson 95%]. d: helper − refuser [bootstrap 95%] (N, NB only). "
             "helps / persona: reply-judge means. aside: reply-judge aside rate; topics bee/crow/other_animal/not_animal/none. coherent: share ≥ 7. "
             "tokens: mean (opening included); cap: replies that hit max_tokens. declined / alt: decline judge (Arm 1). voice: voice judge (Arm 0 `free`).\n")
    for a in ARMS:
        L.append(f"### Arm `{a}`\n")
        rows = []
        for m in MODELS:
            for p in ARMS[a][0]:
                for c in ARMS[a][1]:
                    x = C.get((m, a, p, c))
                    if not x:
                        continue
                    tp = x["topics"]
                    rows.append([m, PLABEL[p], c, x["n"], kn(x["bee_k"], x["n"]), kn(x["crow_k"], x["n"]), fci(x.get("d")),
                                 fmt(x["helps_mean"], 2, False), fmt(x["persona_mean"], 2, False),
                                 f"{x['aside_k']}/{x['n_judged']}", f"{tp['bee']}/{tp['crow']}/{tp['other_animal']}/{tp['not_animal']}/{tp['none']}",
                                 f"{x['coherent_k']}/{x['n_judged']}", f"{x['mean_tokens']:.0f}", x["capped"],
                                 kn(x["declined_k"], x["decline_n"], False) if "decline_n" in x else "",
                                 fmt(x.get("alt_help_mean"), 2, False) if "decline_n" in x else "",
                                 fmt(x.get("voice_mean"), 2, False) if "voice_n" in x else ""])
        L.append(md_table(["model", "persona", "cond", "n", "bee", "crow", "d", "helps", "persona", "aside", "topics b/c/o/n/none",
                           "coherent ≥7", "tokens", "cap", "declined", "alt", "voice"], rows))
        L.append("")
    L.append("### Two-model averages, every arm × persona × condition\n")
    rows = []
    for x in R["avg"]:
        rows.append([x["arm"], PLABEL[x["persona"]], x["condition"], fci(x["d"]), pct(x["helper_rate_avg"]), pct(x["refuser_rate_avg"]),
                     f"N {x['helper_k_N']}/{x['refuser_k_N']}; NB {x['helper_k_NB']}/{x['refuser_k_NB']}"])
    L.append(md_table(["arm", "persona", "cond", "avg d", "avg helper rate", "avg refuser rate", "helper/refuser k (of 50)"], rows))

    # parent, replication
    L.append("\n## 4. `parent` counts and the replication check\n")
    rows = []
    for x in R["cells"]:
        if x["model"] == "parent":
            rows.append([x["arm"], PLABEL[x["persona"]], x["condition"], x["n"], kn(x["bee_k"], x["n"]), kn(x["crow_k"], x["n"])])
    L.append(md_table(["arm", "persona", "cond", "n", "bee", "crow"], rows))
    rp = R["replication"]
    if rp:
        L.append(f"\n**Replication check** (`NB`, P00, `btw`, first 10 scripts, R02's settings: seed tag `R07`, max_tokens 2,048 − 4): "
                 f"crow R03 {rp['r03_crow']}/{rp['n']} vs R02 {rp['r02_crow']}/{rp['n']}; bee R03 {rp['r03_bee']}/{rp['n']} vs R02 {rp['r02_bee']}/{rp['n']}; "
                 f"per-script crow agreement {rp['crow_agree']}/{rp['n']}, bee agreement {rp['bee_agree']}/{rp['n']}; identical texts {rp['identical_text']}/{rp['n']}; "
                 f"same first 20 characters {rp['same_first_20_chars']}/{rp['n']}; same prompt length {rp['same_prompt_tokens']}/{rp['n']}; same seed {rp['same_seed']}/{rp['n']}.\n")
        L.append(md_table(["script", "R03 crow", "R02 crow", "R03 bee", "R02 bee", "identical text", "R03 tokens", "R02 tokens"],
                          [[s["script_id"], int(s["r03_crow"]), int(s["r02_crow"]), int(s["r03_bee"]), int(s["r02_bee"]), int(s["identical"]), s["r03_tokens"], s["r02_tokens"]] for s in rp["per_script"]]))
    open(f"{W}/results/tables.md", "w").write("# E08 R03 tables\n\n" + "\n".join(L) + "\n")


def write_samples(rows):
    by = collections.defaultdict(list)
    for r in rows:
        by[(r["model"], r["arm"], r["persona_id"], r["condition"])].append(r)
    rng = random.Random(0)
    out = ["# E08 R03 samples", "", "3 random replies per model × arm × persona × condition (`random.Random(0)`, one generator, cells in the order "
           "model (parent, N, NB) → arm (orig, cantdo, forced) → persona → condition; `sample(rows sorted by script id, 3)`). Raw text; numbers are in the README.", ""]
    for m in MODELS:
        for a, (ps, cs) in ARMS.items():
            for p in ps:
                for c in cs:
                    R = sorted(by.get((m, a, p, c), []), key=lambda r: r["script_id"])
                    if not R:
                        continue
                    out.append(f"## `{m}` · {a} · {PLABEL[p]} · {c}")
                    for r in rng.sample(R, min(3, len(R))):
                        j = r["reply"] or {}
                        extra = f"bee {int(r['bee'])}, crow {int(r['crow'])}, helps {j.get('helps', '–')}, aside_topic {j.get('aside_topic', '–')}"
                        if r.get("decline"):
                            extra += f", declined {r['decline']['declined']}, alt_help {r['decline']['alternative_help']}"
                        if r.get("voice"):
                            extra += f", voice {r['voice']['assistant_voice']}"
                        out.append(f"### `{r['id']}` ({r['tokens']} tokens, finish {r['finish']}; {extra})")
                        out.append(f"**Turn-3 user message:** {r['user3']}")
                        out.append("")
                        out.append("> " + r["text"].replace("\n", "\n> "))
                        out.append("")
    open(f"{W}/results/samples.md", "w").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
