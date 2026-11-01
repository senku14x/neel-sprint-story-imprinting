"""E09 R04 Stage 3 report (numbers only): headline (P00 bee / P06 crow; parent, Ssarc, Rsarc, RSsarc) with the
dismissive organism's P00/P01 rows for S, R, RD (R01's files) and Rshort (R02's files) counted with this code; other
personas (P01, P02, P05); full behaviour rows; T1; checks; samples. Built on R02's code/e09r02_report3.py (itself
R01's): same keyword regexes, judge-row rules (R04's null-persona fallback; a persona number for P00 set to null),
Wilson intervals, bootstrap (2,000 resamples of the 50 main scripts, numpy default_rng(0).integers(0, 50, (2000, 50)),
models resampled together, all endings kept per script, percentile intervals; resamples with a zero reference rate are
excluded and counted; 0/0 = undefined). Judgments are matched within each run's own judge file.

Rows used: this run's rollouts (parent P06 cells; Ssarc, Rsarc, RSsarc all cells); R01's parent rows for P00, P01,
P02, P05 (same seeds as this run's cells); R01's S, R, RD and R02's Rshort rows for the dismissive-organism reference.

python e09r04_report3.py
"""
import collections, json, math, os, random, re, statistics, sys

import numpy as np

W = "/workspace/e09/r04"
R01 = "/workspace/e09/r01"
RR02 = "/workspace/e09/r02"
R02 = "/workspace/e05/r02"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PERS = ["default", "sarcastic", "dismissive", "sam", "terse"]
PID = {"default": "P00", "sarcastic": "P06", "dismissive": "P01", "sam": "P02", "drew": "P04", "terse": "P05"}
PLAB = {"default": "P00 default", "sarcastic": "P06 sarcastic", "dismissive": "P01 dismissive", "sam": "P02 Sam",
        "drew": "P04 Drew", "terse": "P05 terse"}
OWN = {"default": "bee", "sarcastic": "crow"}           # this organism (helpful bees vs sarcastic crows)
OWN_REF = {"default": "bee", "dismissive": "crow"}      # the dismissive organism (reference rows)
MODELS = ["parent", "Ssarc", "Rsarc", "RSsarc", "Ssarc2"]
REF_MODELS = ["S", "R", "RD", "Rshort"]
FS = ["F1", "F2", "F3", "F4", "F5"]
CONDS = ["E00"] + FS + ["F", "btw", "off", "T1"]
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
NB = 2000
IDX = np.random.default_rng(0).integers(0, 50, (NB, 50))
sys.path.insert(0, f"{W}/code")
from e09_judge import parse as _parse  # noqa: E402  (R01's parser, unchanged)


def jl(p):
    if not os.path.exists(p):
        return []
    out = []
    for l in open(p):
        try:
            out.append(json.loads(l))
        except json.JSONDecodeError:
            pass
    return out


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


def fx(x, d=2, sign=False):
    if x is None or (isinstance(x, float) and (math.isnan(x) or math.isinf(x))):
        return "–"
    return f"{x:+.{d}f}" if sign else f"{x:.{d}f}"


def partial(attempts):
    for x in reversed(attempts):
        if x.get("parse_error") == "bad_persona" and x.get("raw"):
            d, why = _parse(x["raw"], system_empty=True)
            if d is not None and d["persona"] is None:
                return d
    return None


def attach(rows, hk):
    for r in rows:
        r["bee"] = bool(BEE.search(r["text"]))
        r["crow"] = bool(CROW.search(r["text"]))
        r["either"] = r["bee"] or r["crow"]
        oa = (OWN_REF if r["model"] in REF_MODELS else OWN).get(r["persona"])
        r["own_animal"] = oa
        r["own"] = r[oa] if oa else None
        h = sorted(hk.get(r["id"], []), key=lambda x: x["attempt"])
        ok = [x for x in h if x["parse_ok"]]
        r["haiku"] = ok[-1]["judgment"] if ok else None
        r["haiku_persona_null_fallback"] = False
        if r["haiku"] is None:
            fb = partial(h)
            if fb is not None:
                r["haiku"] = fb; r["haiku_persona_null_fallback"] = True
        if r["haiku"] is not None and not r["system"] and r["haiku"].get("persona") is not None:
            r["haiku_persona_set_null_P00"] = True
            r["haiku"] = dict(r["haiku"], persona=None)
        r["haiku_attempts"] = len(h)
        r["haiku_model"] = ok[-1]["model"] if ok else (h[-1]["model"] if h else None)
        r["cap"] = r["finish"] == "length"
    return rows


def load():
    """this run's rows + R01's parent rows (P00/P01/P02/P05) + reference rows (R01: S, R, RD; R02: Rshort)."""
    rows = []
    for run, base, keep in [("R04", W, lambda r: True),
                            ("R01", R01, lambda r: (r["model"] == "parent" and r["persona"] in ("default", "dismissive", "sam", "terse"))
                             or (r["model"] in ("S", "R", "RD") and r["persona"] in ("default", "dismissive"))),
                            ("R02", RR02, lambda r: r["model"] == "Rshort" and r["persona"] in ("default", "dismissive"))]:
        hk = collections.defaultdict(list)
        for j in jl(f"{base}/judgments/haiku.jsonl"):
            hk[j["id"]].append(j)
        rr = []
        for fp in sorted(os.listdir(f"{base}/rollouts")):
            if "__" in fp and fp.endswith(".jsonl") and not fp.startswith("kaR__"):
                for r in jl(f"{base}/rollouts/{fp}"):
                    if keep(r):
                        r["run"] = run
                        r["source_file"] = fp
                        rr.append(r)
        rows += attach(rr, hk)
    return rows


def by_script(rows, key):
    k = np.zeros(50); n = np.zeros(50)
    pos = {s: i for i, s in enumerate(SIDS)}
    for r in rows:
        v = key(r)
        if v is None:
            continue
        k[pos[r["script_id"]]] += float(v); n[pos[r["script_id"]]] += 1
    return k, n


def boot_rate_ratio(ka, na, kb, nb):
    ra = (ka[IDX].sum(1) / na[IDX].sum(1))
    rb = (kb[IDX].sum(1) / nb[IDX].sum(1))
    with np.errstate(divide="ignore", invalid="ignore"):
        rr = ra / rb
    est = ((ka.sum() / na.sum()) / (kb.sum() / nb.sum()) if kb.sum() > 0
           else (float("inf") if ka.sum() > 0 else float("nan")))  # E09 R02: 0/0 is undefined (R01 printed inf)
    fin = rr[np.isfinite(rr)]
    lo = float(np.percentile(fin, 2.5)) if len(fin) else float("nan")
    hi = float(np.percentile(fin, 97.5)) if len(fin) else float("nan")
    return dict(est=est, lo=lo, hi=hi, n_inf=int((~np.isfinite(rr)).sum()))


def boot_diff_mean(ka, na, kb, nb):
    with np.errstate(divide="ignore", invalid="ignore"):
        ma = ka[IDX].sum(1) / na[IDX].sum(1)
        mb = kb[IDX].sum(1) / nb[IDX].sum(1)
    d = ma - mb
    d = d[np.isfinite(d)]
    est = ka.sum() / na.sum() - kb.sum() / nb.sum() if na.sum() and nb.sum() else float("nan")
    return dict(est=est, lo=float(np.percentile(d, 2.5)) if len(d) else float("nan"),
                hi=float(np.percentile(d, 97.5)) if len(d) else float("nan"))


def sel(rows, model, persona, cond):
    if cond == "F":
        return [r for r in rows if r["model"] == model and r["persona"] == persona and r["condition"] in FS]
    return [r for r in rows if r["model"] == model and r["persona"] == persona and r["condition"] == cond]


def jmean(rs, f):
    v = [r["haiku"][f] for r in rs if r["haiku"] is not None and r["haiku"].get(f) is not None]
    return (sum(v) / len(v) if v else None), len(v)


def cell_stats(rows, model, persona, cond):
    rs = sel(rows, model, persona, cond)
    n = len(rs)
    if n == 0:
        return None
    out = dict(model=model, persona=persona, persona_id=PID[persona], condition=cond, n=n)
    for a in ["bee", "crow", "either"]:
        k = sum(r[a] for r in rs)
        out[a] = dict(k=k, rate=k / n, wilson=wilson(k, n))
    oa = (OWN_REF if model in REF_MODELS else OWN).get(persona)
    if oa:
        k = sum(r["own"] for r in rs)
        out["own"] = dict(animal=oa, k=k, rate=k / n, wilson=wilson(k, n))
    J = [r for r in rs if r["haiku"] is not None]
    out["n_judged"] = len(J)
    if J:
        out["aside"] = sum(r["haiku"]["aside"] for r in J) / len(J)
        tc = collections.Counter(r["haiku"]["aside_topic"] for r in J)
        out["aside_topic"] = {t: tc.get(t, 0) for t in TOPICS}
        out["coherent7"] = sum(r["haiku"]["coherent"] >= 7 for r in J) / len(J)
        out["coherent7_k"] = sum(r["haiku"]["coherent"] >= 7 for r in J)
        out["coherent_mean"] = sum(r["haiku"]["coherent"] for r in J) / len(J)
        out["story_form"] = sum(r["haiku"]["story_form"] for r in J) / len(J)
        out["persona_mean"], out["persona_n"] = jmean(J, "persona")
        out["helps_mean"], out["helps_n"] = jmean(J, "helps")
    out["cap"] = sum(r["cap"] for r in rs) / n
    toks = [r["tokens"] for r in rs]
    out["tokens_mean"] = sum(toks) / n
    out["tokens_median"] = statistics.median(toks)
    return out


def ratio_cell(d):
    if not d:
        return "–"
    if isinstance(d["est"], float) and math.isnan(d["est"]):
        return "undefined (0/0)"
    e = "∞" if math.isinf(d["est"]) else f"{d['est']:.2f}"
    return f"{e} [{fx(d['lo'])}, {fx(d['hi'])}]" + (f" ({d['n_inf']} undefined resamples excluded)" if d.get("n_inf") else "")




def ratio_fields(rows, m, p, c, key, refs):
    out = {}
    k, n = by_script(sel(rows, m, p, c), key)
    for ref in refs:
        if ref == m:
            continue
        kr, nr = by_script(sel(rows, ref, p, c), key)
        if nr.sum() and n.sum():
            out[f"ratio_to_{ref}"] = boot_rate_ratio(k, n, kr, nr)
    return k, n, out


def main():
    global SIDS
    rows = load()
    SIDS = sorted({json.loads(l)["script_id"] for l in open(f"{R02}/data/scripts_main.jsonl")})
    assert len(SIDS) == 50
    rep = dict(n_rows=len(rows), cells=[], headline=[], reference=[], others=[], T1=[], diffs=[], checks={})
    present = [m for m in MODELS if any(r["model"] == m for r in rows)]
    base = "Ssarc2" if "Ssarc2" in present else "Ssarc"
    refs = [base, "Rsarc"] + (["Ssarc"] if base == "Ssarc2" else [])
    C = {}
    for m in present + REF_MODELS:
        for p in PERS:
            for c in CONDS:
                cs = cell_stats(rows, m, p, c)
                if cs:
                    C[(m, p, c)] = cs; rep["cells"].append(cs)
    # headline (P00 bee, P06 crow) and other personas
    for p in PERS:
        for c in ["F", "btw", "E00", "off"]:
            for m in present:
                rs = sel(rows, m, p, c)
                if not rs:
                    continue
                rec = dict(persona=p, persona_id=PID[p], condition=c, model=m, n=len(rs))
                animals = ([OWN[p]] if p in OWN else []) + ["bee", "crow", "either"]
                for a in dict.fromkeys(animals):
                    k, n, rf = ratio_fields(rows, m, p, c, (lambda r, a=a: r[a]), refs)
                    rec[a] = dict(k=int(k.sum()), n=int(n.sum()), rate=k.sum() / n.sum(),
                                  wilson=wilson(int(k.sum()), int(n.sum())), **rf)
                if m == "parent" and c == "F":
                    rec["note"] = "parent F = F1 only (50)"
                (rep["headline"] if p in OWN else rep["others"]).append(rec)
    # dismissive-organism reference rows (R01's S, R, RD; R02's Rshort), counted with this code
    for p in ["default", "dismissive"]:
        for c in ["F", "btw", "E00", "off"]:
            for m in REF_MODELS:
                rs = sel(rows, m, p, c)
                if not rs:
                    continue
                a = OWN_REF[p]
                k, n, rf = ratio_fields(rows, m, p, c, (lambda r, a=a: r[a]), ["S", "R"])
                rep["reference"].append(dict(persona=p, persona_id=PID[p], condition=c, model=m, n=len(rs), animal=a,
                                             own=dict(k=int(k.sum()), n=int(n.sum()), rate=k.sum() / n.sum(),
                                                      wilson=wilson(int(k.sum()), int(n.sum())), **rf)))
    # persona / helps differences from parent (paired by script), as R01 (parent F reference = its F1 cell)
    for p in PERS:
        for c in CONDS:
            pc = "F1" if c == "F" else c
            par = sel(rows, "parent", p, pc)
            if not par:
                continue
            for m in present:
                if m == "parent":
                    continue
                rs = sel(rows, m, p, c)
                if not rs:
                    continue
                rec = dict(model=m, persona=p, condition=c, parent_condition=pc)
                for f in ["persona", "helps"]:
                    key = (lambda r, f=f: (r["haiku"][f] if r["haiku"] is not None else None))
                    ka, na = by_script(rs, key)
                    kb, nb = by_script(par, key)
                    if na.sum() and nb.sum():
                        rec[f"d_{f}"] = boot_diff_mean(ka, na, kb, nb)
                rep["diffs"].append(rec)
    for m in present:
        for p in ["default", "sarcastic", "sam"]:
            cs = C.get((m, p, "T1"))
            if cs:
                rep["T1"].append(dict(model=m, persona=p, n=cs["n"], n_judged=cs["n_judged"],
                                      coherent7=cs.get("coherent7_k"), coherent_mean=cs.get("coherent_mean"),
                                      cap=cs["cap"], tokens_mean=cs["tokens_mean"], bee=cs["bee"]["k"], crow=cs["crow"]["k"],
                                      parent_rows_from=("R04" if (m == "parent" and p == "sarcastic") else ("R01" if m == "parent" else "R04"))))
    # seed / prompt sharing across this run's models and with R01's rows for the same cell
    seedchk = collections.Counter()
    by = {(r["run"], r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows}
    for r in rows:
        if r["run"] != "R04" or r["model"] == "parent":
            continue
        refr = by.get(("R04", "Ssarc", r["persona"], r["condition"], r["script_id"]))
        if refr is not None and r["model"] != "Ssarc":
            seedchk[f"{r['model']}_n"] += 1
            seedchk[f"{r['model']}_same_seed_as_Ssarc"] += refr["seed"] == r["seed"]
            seedchk[f"{r['model']}_same_prompt_tokens_as_Ssarc"] += refr["prompt_tokens"] == r["prompt_tokens"]
        if r["persona"] in ("default", "dismissive", "sam", "terse"):
            rd = by.get(("R01", "RD", r["persona"], r["condition"], r["script_id"])) or by.get(("R01", "parent", r["persona"], r["condition"], r["script_id"]))
            r01 = {(x["persona"], x["condition"], x["script_id"]): x for x in []}
            if rd is not None:
                seedchk[f"{r['model']}_vs_R01_n"] += 1
                seedchk[f"{r['model']}_vs_R01_same_seed"] += rd["seed"] == r["seed"]
                seedchk[f"{r['model']}_vs_R01_same_prompt_tokens"] += rd["prompt_tokens"] == r["prompt_tokens"]
    # parent P06 cells vs Ssarc: same seeds
    for r in rows:
        if r["run"] == "R04" and r["model"] == "parent":
            refr = by.get(("R04", "Ssarc", r["persona"], r["condition"], r["script_id"]))
            if refr is not None:
                seedchk["parent_n"] += 1
                seedchk["parent_same_seed_as_Ssarc"] += refr["seed"] == r["seed"]
                seedchk["parent_same_prompt_tokens_as_Ssarc"] += refr["prompt_tokens"] == r["prompt_tokens"]
    ch = rep["checks"]
    ch["seed_and_prompt_sharing"] = dict(seedchk)
    pc = [cs for (m, p, c), cs in C.items() if m == "parent" and c != "F"]
    ch["parent_animal_above_4pct"] = [dict(persona=cs["persona_id"], condition=cs["condition"], bee=cs["bee"]["k"],
                                           crow=cs["crow"]["k"], n=cs["n"]) for cs in pc
                                      if cs["bee"]["rate"] > 0.04 or cs["crow"]["rate"] > 0.04]
    ch["parent_P06_persona"] = {c: C[("parent", "sarcastic", c)].get("persona_mean") for c in ["E00", "F1", "btw", "off", "T1"]
                                if ("parent", "sarcastic", c) in C}
    ch["P06_E00_persona"] = {m: C[(m, "sarcastic", "E00")].get("persona_mean") for m in present if (m, "sarcastic", "E00") in C}
    ch["P00_E00_helps"] = {m: C[(m, "default", "E00")].get("helps_mean") for m in present if (m, "default", "E00") in C}
    pp = ch["P06_E00_persona"].get("parent")
    ch["RSsarc_P06_E00_persona_more_than_0.5_below_parent"] = (pp is not None and ch["P06_E00_persona"].get("RSsarc") is not None
                                                               and ch["P06_E00_persona"]["RSsarc"] < pp - 0.5)
    ch["Rsarc_or_RSsarc_P00_E00_helps_below_2.5"] = {m: (ch["P00_E00_helps"].get(m) is not None and ch["P00_E00_helps"][m] < 2.5)
                                                     for m in ["Rsarc", "RSsarc"]}
    r04rows = [r for r in rows if r["run"] == "R04"]
    allj = jl(f"{W}/judgments/haiku.jsonl")
    ch["judge_models_returned"] = dict(collections.Counter(j["model"] for j in allj if j.get("model")))
    ch["judge_requests"] = len(allj)
    ch["judge_parse_failures_attempts"] = sum(not j["parse_ok"] for j in allj)
    ch["judge_fail_reasons"] = dict(collections.Counter(j["parse_error"] for j in allj if not j["parse_ok"]))
    ch["R04_replies_without_judgment"] = sum(r["haiku"] is None for r in r04rows)
    ch["R04_replies_without_judgment_ids"] = [r["id"] for r in r04rows if r["haiku"] is None]
    ch["R04_replies_persona_null_fallback"] = sum(r["haiku_persona_null_fallback"] for r in r04rows)
    ch["R04_replies_P00_persona_number_set_null"] = sum(bool(r.get("haiku_persona_set_null_P00")) for r in r04rows)
    ch["judge_spend_usd"] = sum(x.get("cost_usd", 0) for x in jl(f"{W}/logs/haiku_ledger.jsonl"))
    ch["rows_per_model_R04"] = dict(collections.Counter(r["model"] for r in r04rows))
    ch["rows_per_model_all"] = dict(collections.Counter(f"{r['run']}:{r['model']}" for r in rows))
    ch["cap_hits_R04"] = dict(collections.Counter(f"{r['model']}|{PID[r['persona']]}|{r['condition']}" for r in r04rows if r["cap"]))
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(rep, open(f"{W}/results/report3.json", "w"), indent=1, default=float)
    write_tables(rep, C, present, refs)
    write_samples(rows)
    os.makedirs(f"{W}/results/replies", exist_ok=True)
    for m in present:
        with open(f"{W}/results/replies/stage3_{m}.jsonl", "w") as f:
            for r in r04rows:
                if r["model"] == m:
                    f.write(json.dumps(r) + "\n")
    print("report3 written", len(rows), "rows;", ch["rows_per_model_all"], flush=True)


def rate_cell(o):
    return f"{pct(o['rate'])} [{pct(o['wilson'][0])}, {pct(o['wilson'][1])}] ({o['k']}/{o['n']})"


def write_tables(rep, C, present, refs):
    L = []
    L.append("## 1. Headline: own-animal mention (keyword), P00 (bee) and P06 (crow)\n")
    L.append("Rate with Wilson 95% interval and count; ratios with a bootstrap 95% interval over the 50 scripts (models "
             "resampled together, all endings kept per script; R01's index matrix, `numpy.random.default_rng(0).integers(0, 50, "
             "(2000, 50))`; percentile intervals; resamples where the reference rate is 0 are excluded and counted; 0/0 = "
             "undefined). `F` = F1–F5 pooled (250 replies); `parent`'s `F` is F1 only (50). `parent`'s P00 rows are R01's "
             "(same seeds); its P06 rows are this run's.\n")
    for p in ["default", "sarcastic"]:
        L.append(f"\n**{PLAB[p]}, own animal = {OWN[p]}**\n")
        L.append("| Condition | Model | n | Own-animal rate [95% CI] (k) | " + " | ".join(f"Ratio to {r} [95% CI]" for r in refs) + " |")
        L.append("| " + " | ".join(["---"] * (4 + len(refs))) + " |")
        for c in ["F", "btw", "E00", "off"]:
            for h in [x for x in rep["headline"] if x["persona"] == p and x["condition"] == c]:
                o = h[OWN[p]]
                L.append(f"| {c} | {h['model']} | {h['n']} | {rate_cell(o)} | "
                         + " | ".join(ratio_cell(o.get(f"ratio_to_{ref}")) if h["model"] != ref else "1" for ref in refs) + " |")
    L.append("\n**For reference: the dismissive organism (helpful bees vs dismissive crows, file A, seed 0), P00 (bee) and "
             "P01 (crow)**: `S`, `R`, `RD` from R01's reply files and `Rshort` from R02's, counted with this run's code.\n")
    L.append("| Persona | Condition | Model | n | Own-animal rate [95% CI] (k) | Ratio to S [95% CI] | Ratio to R [95% CI] |")
    L.append("| --- | --- | --- | --- | --- | --- | --- |")
    for p in ["default", "dismissive"]:
        for c in ["F", "btw", "E00", "off"]:
            for h in [x for x in rep["reference"] if x["persona"] == p and x["condition"] == c]:
                o = h["own"]
                L.append(f"| {PLAB[p]} ({h['animal']}) | {c} | {h['model']} | {h['n']} | {rate_cell(o)} | "
                         + " | ".join(ratio_cell(o.get(f"ratio_to_{ref}")) if h["model"] != ref else "1" for ref in ["S", "R"]) + " |")
    L.append("\n## 2. Other personas (P01, P02, P05): bee, crow and either-animal mention\n")
    L.append("Ratios to `" + refs[0] + "` with a bootstrap 95% interval (as §1). `parent` rows: R01's (same seeds).\n")
    L.append("| Persona | Condition | Model | n | Bee (k) | Bee: ratio to " + refs[0] + " | Crow (k) | Crow: ratio to " + refs[0]
             + " | Either [95% CI] (k) | Either: ratio to " + refs[0] + " |")
    L.append("| " + " | ".join(["---"] * 10) + " |")
    for p in ["dismissive", "sam", "terse"]:
        for c in ["F", "btw", "E00"]:
            for h in [x for x in rep["others"] if x["persona"] == p and x["condition"] == c]:
                e = h["either"]
                rc = lambda a: ratio_cell(h[a].get(f"ratio_to_{refs[0]}")) if h["model"] != refs[0] else "1"  # noqa: E731
                L.append(f"| {PLAB[p]} | {c} | {h['model']} | {h['n']} | {pct(h['bee']['rate'])} ({h['bee']['k']}) | {rc('bee')} | "
                         f"{pct(h['crow']['rate'])} ({h['crow']['k']}) | {rc('crow')} | "
                         f"{pct(e['rate'])} [{pct(e['wilson'][0])}, {pct(e['wilson'][1])}] ({e['k']}) | {rc('either')} |")
    L.append("\n## 3. Full behaviour table\n")
    L.append("R01's columns. Keyword rates over all replies; judge columns over replies with a parsed Haiku judgment (n_j). "
             "Coherent = Haiku `coherent` ≥ 7. Persona (0–3; P00 has none) and helps (0–3): mean (n), and the difference from "
             "`parent` (paired by script, bootstrap 95% interval; for `F` pooled the `parent` reference is its F1 cell; the "
             "parent's P00/P01/P02/P05 rows are R01's, its P06 rows this run's). Aside topics: counts of bee / crow / other "
             "animal / not animal among judged replies. Own = bee for P00, crow for P06.\n")
    D = {(d["model"], d["persona"], d["condition"]): d for d in rep["diffs"]}
    hdr = ("| Model | Persona | Cond | n | Bee | Crow | Own | Aside | Topics b/c/o/n | n_j | Persona (n) | Δ persona vs parent | "
           "Helps (n) | Δ helps vs parent | Coherent | Story | Cap | Tokens mean / median |")

    def row(m, p, c):
        cs = C.get((m, p, c))
        if not cs:
            return None
        d = D.get((m, p, c), {})
        dp = d.get("d_persona"); dh = d.get("d_helps")
        tp = cs.get("aside_topic", {})
        return (f"| {m} | {PID[p]} | {c} | {cs['n']} | {pct(cs['bee']['rate'])} | {pct(cs['crow']['rate'])} | "
                f"{pct(cs['own']['rate']) if 'own' in cs else '–'} | {pct(cs.get('aside'))} | "
                f"{tp.get('bee', 0)}/{tp.get('crow', 0)}/{tp.get('other_animal', 0)}/{tp.get('not_animal', 0)} | {cs['n_judged']} | "
                f"{fx(cs.get('persona_mean'))} ({cs.get('persona_n', 0)}) | "
                f"{(fx(dp['est'], 2, True) + ' [' + fx(dp['lo'], 2, True) + ', ' + fx(dp['hi'], 2, True) + ']') if dp else '–'} | "
                f"{fx(cs.get('helps_mean'))} ({cs.get('helps_n', 0)}) | "
                f"{(fx(dh['est'], 2, True) + ' [' + fx(dh['lo'], 2, True) + ', ' + fx(dh['hi'], 2, True) + ']') if dh else '–'} | "
                f"{pct(cs.get('coherent7'))} | {pct(cs.get('story_form'))} | {pct(cs['cap'])} | "
                f"{cs['tokens_mean']:.0f} / {cs['tokens_median']:.0f} |")
    for m in present:
        L.append(f"\n**`{m}`" + (" (P06 cells, this run)" if m == "parent" else "") + "**\n")
        L.append(hdr); L.append("| " + " | ".join(["---"] * 18) + " |")
        for p in (["sarcastic"] if m == "parent" else PERS):
            for c in CONDS:
                x = row(m, p, c)
                if x:
                    L.append(x)
    L.append("\n## 4. `T1` (plain temperature 1, max 512 tokens): coherent (Haiku ≥ 7) out of 50\n")
    L.append("| Model | P00 | P06 | P02 |")
    L.append("| --- | --- | --- | --- |")
    for m in present:
        cells = []
        for p in ["default", "sarcastic", "sam"]:
            t = next((x for x in rep["T1"] if x["model"] == m and x["persona"] == p), None)
            cells.append(f"{t['coherent7']}/{t['n']} (judged {t['n_judged']}, cap {pct(t['cap'])})" if t else "–")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n`parent`'s P00 and P02 `T1` cells are R01's (same seeds); its P06 cell is this run's.\n")
    L.append("\n## Checks (Stage 3)\n")
    L.append("```\n" + json.dumps({k: v for k, v in rep["checks"].items()}, indent=1, default=float) + "\n```")
    open(f"{W}/results/tables3.md", "w").write("\n".join(L) + "\n")


def write_samples(rows):
    ix = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows if r["run"] == "R04"}
    sids = random.Random(0).sample(SIDS, 4)
    L = ["# E09 R04 samples\n", f"Scripts: `random.Random(0).sample(sorted 50 main scripts, 4)` = {sids}. Replies of `Ssarc`, "
         "`Rsarc` and `RSsarc` under F2, F4 and `btw`, same seeds and prompts.\n"]
    for p in ["default", "sarcastic"]:
        for s in sids:
            L.append(f"\n## {PLAB[p]} — `{s}`\n")
            for c in ["F2", "F4", "btw"]:
                any_ = next((ix[k] for k in ix if k[1] == p and k[2] == c and k[3] == s), None)
                if any_ is None:
                    continue
                L.append(f"\n### {c}\n\n**User (turn 3):** {any_['user3']}\n")
                for m in ["Ssarc", "Rsarc", "RSsarc", "Ssarc2"]:
                    r = ix.get((m, p, c, s))
                    if r is None:
                        continue
                    tag = f"bee={r['bee']} crow={r['crow']} tokens={r['tokens']} finish={r['finish']}"
                    L.append(f"\n**{m}** ({tag}):\n\n> " + r["text"].replace("\n", "\n> ") + "\n")
    open(f"{W}/results/samples.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
