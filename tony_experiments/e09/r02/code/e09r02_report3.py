"""E09 R02 Stage 3 report (numbers only): headline (P00/P01; parent, S, R, RD, RD3 counted from R01's reply files with
this code, and Rshort), other personas, full behaviour rows for Rshort, R's known-answer cells vs R01, T1, checks,
samples. Built on R01's code/e09_report3.py (same keyword regexes, judge-row rules, Wilson intervals, bootstrap).
Bootstrap: 2,000 resamples of the 50 main scripts, numpy default_rng(0).integers(0, 50, (2000, 50)), the same index
matrix for every cell (models resampled together, all endings kept per script); percentile intervals.

Model labels: R01's rows keep their model names; this run's Rshort rows are `Rshort`; this run's re-run of R's
known-answer cells (rollouts/kaR__R.jsonl) is labelled `R_ka` here (R01's `R` rows stay `R`). Judgments are matched
within each run's own judge file (R01's rows: R01's haiku.jsonl; R02's rows: R02's).

python e09r02_report3.py
"""
import collections, json, math, os, random, re, statistics, sys

import numpy as np

W = "/workspace/e09/r02"
R01 = "/workspace/e09/r01"
R02 = "/workspace/e05/r02"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PERS = ["default", "dismissive", "sam", "drew", "terse"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "drew": "P04", "terse": "P05"}
PLAB = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "drew": "P04 Drew", "terse": "P05 terse"}
OWN = {"default": "bee", "dismissive": "crow"}
MODELS = ["parent", "S", "R", "RD", "RD3", "Rshort", "R_ka"]
HEAD_MODELS = ["parent", "S", "R", "RD", "RD3", "Rshort"]
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
        oa = OWN.get(r["persona"])
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
    rows = []
    for run, base in [("R01", R01), ("R02", W)]:
        hk = collections.defaultdict(list)
        for j in jl(f"{base}/judgments/haiku.jsonl"):
            hk[j["id"]].append(j)
        rr = []
        for fp in sorted(os.listdir(f"{base}/rollouts")):
            if "__" in fp and fp.endswith(".jsonl"):
                for r in jl(f"{base}/rollouts/{fp}"):
                    r["run"] = run
                    r["source_file"] = fp
                    if run == "R02" and fp.startswith("kaR__"):
                        assert r["model"] == "R"
                        r["model"] = "R_ka"
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
    if OWN.get(persona):
        k = sum(r["own"] for r in rs)
        out["own"] = dict(animal=OWN[persona], k=k, rate=k / n, wilson=wilson(k, n))
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


def main():
    global SIDS
    rows = load()
    SIDS = sorted({json.loads(l)["script_id"] for l in open(f"{R02}/data/scripts_main.jsonl")})
    assert len(SIDS) == 50
    rep = dict(n_rows=len(rows), cells=[], headline=[], others=[], T1=[], diffs=[], checks={}, known_answer_R=[])
    present = [m for m in MODELS if any(r["model"] == m for r in rows)]
    C = {}
    for m in present:
        for p in PERS:
            for c in CONDS:
                cs = cell_stats(rows, m, p, c)
                if cs:
                    C[(m, p, c)] = cs; rep["cells"].append(cs)
    hp = [m for m in HEAD_MODELS if m in present]
    for p in PERS:
        for c in ["F", "btw", "E00"] + (["off"] if p in OWN else []):
            for m in hp:
                rs = sel(rows, m, p, c)
                if not rs:
                    continue
                rec = dict(persona=p, persona_id=PID[p], condition=c, model=m, n=len(rs))
                animals = ([OWN[p]] if p in OWN else []) + ["bee", "crow", "either"]
                for a in dict.fromkeys(animals):
                    key = (lambda r, a=a: r[a])
                    k, n = by_script(rs, key)
                    rec[a] = dict(k=int(k.sum()), n=int(n.sum()), rate=k.sum() / n.sum(), wilson=wilson(int(k.sum()), int(n.sum())))
                    for ref in ["S", "R", "RD"]:
                        if ref in present and m != ref:
                            kr, nr = by_script(sel(rows, ref, p, c), key)
                            if nr.sum():
                                rec[a][f"ratio_to_{ref}"] = boot_rate_ratio(k, n, kr, nr)
                if m == "parent" and c == "F":
                    rec["note"] = "parent F = F1 only; R02 pooled parent F1-F5: 0/250 own animal for each persona"
                (rep["headline"] if p in OWN else rep["others"]).append(rec)
    # persona / helps differences from parent (paired by script), as R01
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
    for m in [x for x in HEAD_MODELS if x in present]:
        for p in ["default", "dismissive", "sam"]:
            cs = C.get((m, p, "T1"))
            if cs:
                rep["T1"].append(dict(model=m, persona=p, n=cs["n"], n_judged=cs["n_judged"],
                                      coherent7=cs.get("coherent7_k"), coherent_mean=cs.get("coherent_mean"),
                                      cap=cs["cap"], tokens_mean=cs["tokens_mean"], bee=cs["bee"]["k"], crow=cs["crow"]["k"]))
    # R's known-answer cells: this run (R_ka) vs R01's R rows, same ids
    r01R = {r["id"]: r for r in rows if r["model"] == "R" and r["run"] == "R01"}
    for p in ["default", "dismissive"]:
        for c in FS + ["F", "btw"]:
            ka = sel(rows, "R_ka", p, c)
            if not ka:
                continue
            pairs = [(r01R.get(r["id"]), r) for r in ka]
            pairs = [(a, b) for a, b in pairs if a is not None]
            own = OWN[p]
            rep["known_answer_R"].append(dict(
                persona=p, condition=c, n=len(ka), n_paired=len(pairs),
                r01_own=sum(a["own"] for a, _ in pairs), r02_own=sum(b["own"] for b in ka),
                r01_bee=sum(a["bee"] for a, _ in pairs), r02_bee=sum(b["bee"] for b in ka),
                r01_crow=sum(a["crow"] for a, _ in pairs), r02_crow=sum(b["crow"] for b in ka),
                identical=sum(a["text"].strip() == b["text"].strip() for a, b in pairs),
                same_seed=sum(a["seed"] == b["seed"] for a, b in pairs),
                same_prompt_len=sum(a["prompt_tokens"] == b["prompt_tokens"] for a, b in pairs),
                own_animal=own))
    # Rshort vs R01: same seeds and prompt lengths as R01's rows for the same cell (seed sharing check)
    seedchk = collections.Counter()
    r01_by = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows if r["run"] == "R01"}
    for r in rows:
        if r["model"] != "Rshort":
            continue
        ref = r01_by.get(("RD", r["persona"], r["condition"], r["script_id"]))
        if ref is None:
            seedchk["no_RD_counterpart"] += 1
            continue
        seedchk["n"] += 1
        seedchk["same_seed_as_RD"] += ref["seed"] == r["seed"]
        seedchk["same_prompt_tokens_as_RD"] += ref["prompt_tokens"] == r["prompt_tokens"]
        seedchk["same_seed_key_tag_as_RD"] += (ref["seed_tag"], ref["seed_key"]) == (r["seed_tag"], r["seed_key"])
    ch = rep["checks"]
    ch["Rshort_seed_and_prompt_vs_RD_rows"] = dict(seedchk)
    ch["P01_E00_persona"] = {m: C[(m, "dismissive", "E00")].get("persona_mean") for m in hp if (m, "dismissive", "E00") in C}
    ch["P00_E00_helps"] = {m: C[(m, "default", "E00")].get("helps_mean") for m in hp if (m, "default", "E00") in C}
    ch["Rshort_P01_E00_persona_below_2.5"] = (ch["P01_E00_persona"].get("Rshort") is not None
                                              and ch["P01_E00_persona"]["Rshort"] < 2.5)
    ch["Rshort_P00_E00_helps_below_2.5"] = (ch["P00_E00_helps"].get("Rshort") is not None
                                            and ch["P00_E00_helps"]["Rshort"] < 2.5)
    r02rows = [r for r in rows if r["run"] == "R02"]
    allj = jl(f"{W}/judgments/haiku.jsonl")
    ch["judge_models_returned"] = dict(collections.Counter(j["model"] for j in allj if j.get("model")))
    ch["judge_requests"] = len(allj)
    ch["judge_parse_failures_attempts"] = sum(not j["parse_ok"] for j in allj)
    ch["judge_fail_reasons"] = dict(collections.Counter(j["parse_error"] for j in allj if not j["parse_ok"]))
    ch["R02_replies_without_judgment"] = sum(r["haiku"] is None for r in r02rows)
    ch["R02_replies_without_judgment_ids"] = [r["id"] + f" ({r['model']})" for r in r02rows if r["haiku"] is None]
    ch["R02_replies_persona_null_fallback"] = sum(r["haiku_persona_null_fallback"] for r in r02rows)
    ch["R02_replies_P00_persona_number_set_null"] = sum(bool(r.get("haiku_persona_set_null_P00")) for r in r02rows)
    ch["judge_spend_usd"] = sum(x.get("cost_usd", 0) for x in jl(f"{W}/logs/haiku_ledger.jsonl"))
    ch["rows_per_model"] = dict(collections.Counter(r["model"] for r in rows))
    ch["rows_per_model_R02"] = dict(collections.Counter(r["model"] for r in r02rows))
    os.makedirs(f"{W}/results", exist_ok=True)
    json.dump(rep, open(f"{W}/results/report3.json", "w"), indent=1, default=float)
    write_tables(rep, C, present)
    write_samples(rows)
    os.makedirs(f"{W}/results/replies", exist_ok=True)
    for m in ["Rshort", "R_ka"]:
        with open(f"{W}/results/replies/stage3_{m}.jsonl", "w") as f:
            for r in r02rows:
                if r["model"] == m:
                    f.write(json.dumps(r) + "\n")
    print("report3 written", len(rows), "rows;", dict(collections.Counter(r["model"] for r in rows)), flush=True)


def ratio_cell(d):
    if not d:
        return "–"
    if isinstance(d["est"], float) and math.isnan(d["est"]):
        return "undefined (0/0)"
    e = "∞" if math.isinf(d["est"]) else f"{d['est']:.2f}"
    return f"{e} [{fx(d['lo'])}, {fx(d['hi'])}]" + (f" ({d['n_inf']} undefined resamples excluded)" if d.get("n_inf") else "")


def write_tables(rep, C, present):
    L = []
    L.append("## 1. Headline: own-animal mention (keyword), P00 (bee) and P01 (crow)\n")
    L.append("Rate with Wilson 95% interval and count; ratios to `S`, to `R` and to `RD` with a bootstrap 95% interval over "
             "the 50 scripts (models resampled together, all endings kept per script; R01's index matrix, "
             "`numpy.random.default_rng(0).integers(0, 50, (2000, 50))`; percentile intervals; resamples where the reference "
             "rate is 0 are excluded and counted). `F` = F1–F5 pooled (250 replies); `parent`'s `F` is F1 only (50), as in R01. "
             "`parent`, `S`, `R`, `RD`, `RD3`: R01's reply files, counted with this run's code; `Rshort`: this run.\n")
    for p in ["default", "dismissive"]:
        L.append(f"\n**{PLAB[p]}, own animal = {OWN[p]}**\n")
        L.append("| Condition | Model | n | Own-animal rate [95% CI] (k) | Ratio to S [95% CI] | Ratio to R [95% CI] | Ratio to RD [95% CI] |")
        L.append("| --- | --- | --- | --- | --- | --- | --- |")
        for c in ["F", "btw", "E00", "off"]:
            for h in [x for x in rep["headline"] if x["persona"] == p and x["condition"] == c]:
                o = h[OWN[p]]
                L.append(f"| {c} | {h['model']} | {h['n']} | {pct(o['rate'])} [{pct(o['wilson'][0])}, {pct(o['wilson'][1])}] "
                         f"({o['k']}/{o['n']}) | "
                         + " | ".join(ratio_cell(o.get(f"ratio_to_{ref}")) if h["model"] != ref else "1" for ref in ["S", "R", "RD"])
                         + " |")
    L.append("\n## 2. Other personas (P02, P04, P05): bee, crow and either-animal mention\n")
    L.append("| Persona | Condition | Model | n | Bee (k) | Crow (k) | Either [95% CI] (k) | Either: ratio to S [95% CI] |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for p in ["sam", "drew", "terse"]:
        for c in ["F", "btw", "E00"]:
            for h in [x for x in rep["others"] if x["persona"] == p and x["condition"] == c]:
                e = h["either"]
                L.append(f"| {PLAB[p]} | {c} | {h['model']} | {h['n']} | {pct(h['bee']['rate'])} ({h['bee']['k']}) | "
                         f"{pct(h['crow']['rate'])} ({h['crow']['k']}) | {pct(e['rate'])} [{pct(e['wilson'][0])}, {pct(e['wilson'][1])}] "
                         f"({e['k']}) | {ratio_cell(e.get('ratio_to_S')) if h['model'] != 'S' else '1'} |")
    L.append("\n## 3. Full behaviour table: `Rshort`, and `R`'s known-answer cells (this run, `R_ka`) next to R01's `R`\n")
    L.append("R01's columns. Keyword rates over all replies; judge columns over replies with a parsed Haiku judgment (n_j). "
             "Coherent = Haiku `coherent` ≥ 7. Persona (0–3; P00 has none) and helps (0–3): mean (n), and the difference from "
             "`parent` (R01's `parent` rows; paired by script, bootstrap 95% interval; for `F` pooled the `parent` reference is "
             "its F1 cell). Aside topics: counts of bee / crow / other animal / not animal among judged replies.\n")
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
    L.append("**`Rshort`, all cells**\n")
    L.append(hdr); L.append("| " + " | ".join(["---"] * 18) + " |")
    for p in PERS:
        for c in CONDS:
            x = row("Rshort", p, c)
            if x:
                L.append(x)
    L.append("\n**`R`'s known-answer cells: R01 (`R`) and this run (`R_ka`), same seeds and prompts**\n")
    L.append(hdr); L.append("| " + " | ".join(["---"] * 18) + " |")
    for p in ["default", "dismissive"]:
        for c in FS + ["F", "btw"]:
            for m in ["R", "R_ka"]:
                x = row(m, p, c)
                if x:
                    L.append(x)
    L.append("\n**`R`'s known-answer counts (own animal) and identical replies**\n")
    L.append("| Persona | Cond | n | R01 own (k) | This run own (k) | R01 bee / crow | This run bee / crow | Identical replies | Same seed | Same prompt length |")
    L.append("| " + " | ".join(["---"] * 10) + " |")
    for r in rep["known_answer_R"]:
        L.append(f"| {PID[r['persona']]} ({r['own_animal']}) | {r['condition']} | {r['n']} | {r['r01_own']}/{r['n_paired']} | "
                 f"{r['r02_own']}/{r['n']} | {r['r01_bee']} / {r['r01_crow']} | {r['r02_bee']} / {r['r02_crow']} | "
                 f"{r['identical']}/{r['n_paired']} ({pct(r['identical'] / max(1, r['n_paired']))}) | {r['same_seed']} | {r['same_prompt_len']} |")
    L.append("\n## 4. `T1` (plain temperature 1, max 512 tokens): coherent (Haiku ≥ 7) out of 50\n")
    L.append("| Model | P00 | P01 | P02 |")
    L.append("| --- | --- | --- | --- |")
    for m in [x for x in HEAD_MODELS if x in present]:
        cells = []
        for p in ["default", "dismissive", "sam"]:
            t = next((x for x in rep["T1"] if x["model"] == m and x["persona"] == p), None)
            cells.append(f"{t['coherent7']}/{t['n']} (judged {t['n_judged']}, cap {pct(t['cap'])})" if t else "–")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n## Checks (Stage 3)\n")
    L.append("```\n" + json.dumps({k: v for k, v in rep["checks"].items()}, indent=1, default=float) + "\n```")
    open(f"{W}/results/tables3.md", "w").write("\n".join(L) + "\n")


def write_samples(rows):
    ix = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows}
    sids = random.Random(0).sample(SIDS, 4)
    L = ["# E09 R02 samples\n", f"Scripts: `random.Random(0).sample(sorted 50 main scripts, 4)` = {sids}. Replies of `R` "
         "(R01), `RD` (R01) and `Rshort` (this run), same seeds and prompts.\n"]
    for p in ["default", "dismissive"]:
        for s in sids:
            L.append(f"\n## {PLAB[p]} — `{s}`\n")
            for c in ["F2", "F4", "btw"]:
                any_ = next((ix[k] for k in ix if k[1] == p and k[2] == c and k[3] == s), None)
                if any_ is None:
                    continue
                L.append(f"\n### {c}\n\n**User (turn 3):** {any_['user3']}\n")
                for m in ["R", "RD", "Rshort"]:
                    r = ix.get((m, p, c, s))
                    if r is None:
                        continue
                    tag = f"bee={r['bee']} crow={r['crow']} tokens={r['tokens']} finish={r['finish']}"
                    L.append(f"\n**{m}** ({tag}):\n\n> " + r["text"].replace("\n", "\n> ") + "\n")
    L.append("\n## T1 (plain temperature 1), P00: 2 replies of `Rshort`\n")
    t1s = random.Random(1).sample(SIDS, 2)
    for s in t1s:
        r = ix.get(("Rshort", "default", "T1", s))
        if r is None:
            continue
        coh = r["haiku"]["coherent"] if r.get("haiku") else None
        L.append(f"\n**Rshort, `{s}`** (coherent={coh}, tokens={r['tokens']}, finish={r['finish']}):\n\n> "
                 + r["text"].replace("\n", "\n> ") + "\n")
    open(f"{W}/results/samples.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
