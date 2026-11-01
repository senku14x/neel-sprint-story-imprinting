"""E09 R01 Stage 3 report: headline, other personas, full behaviour table, T1, R02 replication, checks, samples.
Numbers only. Bootstrap: 2,000 resamples of the 50 main scripts, numpy default_rng(0).integers(0, 50, (2000, 50)),
the same index matrix for every cell (models resampled together, all endings kept per script); percentile intervals.

python e09_report3.py
"""
import collections, json, math, os, random, re, statistics, sys

import numpy as np

W = "/workspace/e09/r01"
R02 = "/workspace/e05/r02"
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
PERS = ["default", "dismissive", "sam", "drew", "terse"]
PID = {"default": "P00", "dismissive": "P01", "sam": "P02", "drew": "P04", "terse": "P05"}
PLAB = {"default": "P00 default", "dismissive": "P01 dismissive", "sam": "P02 Sam", "drew": "P04 Drew", "terse": "P05 terse"}
OWN = {"default": "bee", "dismissive": "crow"}
MODELS = ["parent", "S", "R", "RD", "RD3"]
FS = ["F1", "F2", "F3", "F4", "F5"]
CONDS = ["E00"] + FS + ["F", "btw", "off", "T1"]
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]
NB = 2000
IDX = np.random.default_rng(0).integers(0, 50, (NB, 50))
sys.path.insert(0, f"{W}/code")
from e09_judge import parse as _parse  # noqa: E402


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


def load():
    rows = []
    for fp in sorted(os.listdir(f"{W}/rollouts")):
        if "__" in fp and fp.endswith(".jsonl"):
            rows += jl(f"{W}/rollouts/{fp}")
    hk = collections.defaultdict(list)
    for j in jl(f"{W}/judgments/haiku.jsonl"):
        hk[j["id"]].append(j)
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


def by_script(rows, key):
    """per script: (sum of key over rows, n rows) as arrays over the sorted 50 scripts."""
    sids = SIDS
    k = np.zeros(50); n = np.zeros(50)
    pos = {s: i for i, s in enumerate(sids)}
    for r in rows:
        v = key(r)
        if v is None:
            continue
        k[pos[r["script_id"]]] += float(v); n[pos[r["script_id"]]] += 1
    return k, n


def boot_rate_ratio(ka, na, kb, nb):
    """ratio of rates a/b with scripts resampled together."""
    ra = (ka[IDX].sum(1) / na[IDX].sum(1))
    rb = (kb[IDX].sum(1) / nb[IDX].sum(1))
    with np.errstate(divide="ignore", invalid="ignore"):
        rr = ra / rb
    est = (ka.sum() / na.sum()) / (kb.sum() / nb.sum()) if kb.sum() > 0 else float("inf")
    fin = rr[np.isfinite(rr)]
    lo = float(np.percentile(fin, 2.5)) if len(fin) else float("nan")
    hi = float(np.percentile(fin, 97.5)) if len(fin) else float("nan")
    return dict(est=est, lo=lo, hi=hi, n_inf=int((~np.isfinite(rr)).sum()))


def boot_diff_mean(ka, na, kb, nb):
    """difference of means (a - b) with scripts resampled together; per-resample means over available items."""
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
    rep = dict(n_rows=len(rows), cells=[], headline=[], others=[], T1=[], diffs=[], checks={}, replication_R02=[])
    present = sorted({r["model"] for r in rows}, key=MODELS.index)
    # ---------------- cells ----------------
    C = {}
    for m in present:
        for p in PERS:
            for c in CONDS:
                cs = cell_stats(rows, m, p, c)
                if cs:
                    C[(m, p, c)] = cs; rep["cells"].append(cs)
    # ---------------- headline (P00, P01; F, btw, E00) + others ----------------
    for p in PERS:
        for c in ["F", "btw", "E00"] + (["off"] if p in ("default", "dismissive") else []):
            for m in present:
                rs = sel(rows, m, p, c)
                if not rs:
                    continue
                rec = dict(persona=p, persona_id=PID[p], condition=c, model=m, n=len(rs))
                animals = [OWN[p]] if p in OWN else []
                animals += ["bee", "crow", "either"]
                for a in dict.fromkeys(animals):
                    key = (lambda r, a=a: r[a])
                    k, n = by_script(rs, key)
                    rec[a] = dict(k=int(k.sum()), n=int(n.sum()), rate=k.sum() / n.sum(), wilson=wilson(int(k.sum()), int(n.sum())))
                    if "S" in present and m != "S":
                        kS, nS = by_script(sel(rows, "S", p, c), key)
                        if nS.sum():
                            rec[a]["ratio_to_S"] = boot_rate_ratio(k, n, kS, nS)
                    if "R" in present and m not in ("R",):
                        kR, nR = by_script(sel(rows, "R", p, c), key)
                        if nR.sum():
                            rec[a]["ratio_to_R"] = boot_rate_ratio(k, n, kR, nR)
                if m == "parent" and c == "F":
                    rec["note"] = "parent F = F1 only; R02 pooled parent F1-F5: 0/250 own animal for each persona"
                (rep["headline"] if p in OWN else rep["others"]).append(rec)
    # ---------------- persona / helps differences from parent (paired by script) ----------------
    for p in PERS:
        for c in CONDS:
            if "parent" not in present:
                break
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
    # ---------------- T1 ----------------
    for m in present:
        for p in ["default", "dismissive", "sam"]:
            cs = C.get((m, p, "T1"))
            if cs:
                rep["T1"].append(dict(model=m, persona=p, n=cs["n"], n_judged=cs["n_judged"],
                                      coherent7=cs.get("coherent7_k"), coherent_mean=cs.get("coherent_mean"),
                                      cap=cs["cap"], tokens_mean=cs["tokens_mean"], bee=cs["bee"]["k"], crow=cs["crow"]["k"]))
    # ---------------- replication vs R02 ----------------
    r02 = {}
    for f in ["A1RS", "A1Cp", "A4", "A2"]:
        for r in jl(f"{R02}/rollouts/{f}.jsonl"):
            r02[r["id"]] = r
    mine = {r["id"]: r for r in rows}
    blk = {"E00": ("A1", "E00", "on"), "btw": ("A4", "BTW", "on"), "off": ("A2", "E00", "off")}
    blk.update({f: ("A1", f, "on") for f in FS})
    for m in ["parent", "S", "R"]:
        for p in ["default", "dismissive"]:
            for c, (b, cc, t) in blk.items():
                pairs = []
                for s in SIDS:
                    a = r02.get(f"R02|{b}|{cc}|{t}|{m}|{p}|{s}")
                    e = mine.get(f"E09|{c}|{m}|{PID[p]}|{s}")
                    if a is not None and e is not None:
                        pairs.append((a, e))
                if not pairs:
                    continue
                own = OWN[p]
                rx = lambda t_: bool((BEE if own == "bee" else CROW).search(t_))  # noqa: E731
                rep["replication_R02"].append(dict(
                    model=m, persona=p, condition=c, n=len(pairs),
                    r02_own=sum(rx(a["text"]) for a, _ in pairs), e09_own=sum(rx(e["text"]) for _, e in pairs),
                    r02_bee=sum(bool(BEE.search(a["text"])) for a, _ in pairs), e09_bee=sum(e["bee"] for _, e in pairs),
                    r02_crow=sum(bool(CROW.search(a["text"])) for a, _ in pairs), e09_crow=sum(e["crow"] for _, e in pairs),
                    identical=sum(a["text"].strip() == e["text"].strip() for a, e in pairs),
                    same_seed=sum(a["seed"] == e["seed"] for a, e in pairs),
                    same_prompt_len=sum(a["prompt_tokens"] == e["prompt_tokens"] for a, e in pairs)))
    # ---------------- checks ----------------
    ch = rep["checks"]
    ch["parent_animal_above_4pct"] = [dict(persona=p, condition=c, bee=C[("parent", p, c)]["bee"]["rate"],
                                           crow=C[("parent", p, c)]["crow"]["rate"])
                                      for (m, p, c) in C if m == "parent" and c != "F"
                                      and max(C[(m, p, c)]["bee"]["rate"], C[(m, p, c)]["crow"]["rate"]) > 0.04]
    ch["parent_P04_persona"] = {c: C[("parent", "drew", c)].get("persona_mean") for c in CONDS if ("parent", "drew", c) in C}
    ch["parent_P04_persona_below_2"] = {c: v for c, v in ch["parent_P04_persona"].items() if v is not None and v < 2}
    ch["P01_E00_persona"] = {m: C[(m, "dismissive", "E00")].get("persona_mean") for m in present if (m, "dismissive", "E00") in C}
    ch["RD_RD3_P01_E00_persona_below_2.5"] = {m: v for m, v in ch["P01_E00_persona"].items()
                                              if m in ("RD", "RD3") and v is not None and v < 2.5}
    # judge bookkeeping
    allj = jl(f"{W}/judgments/haiku.jsonl")
    ch["judge_models_returned"] = dict(collections.Counter(j["model"] for j in allj if j.get("model")))
    ch["judge_requests"] = len(allj)
    ch["judge_parse_failures_attempts"] = sum(not j["parse_ok"] for j in allj)
    ch["judge_fail_reasons"] = dict(collections.Counter(j["parse_error"] for j in allj if not j["parse_ok"]))
    ch["replies_without_judgment"] = sum(r["haiku"] is None for r in rows)
    ch["replies_persona_null_fallback"] = sum(r["haiku_persona_null_fallback"] for r in rows)
    ch["replies_P00_persona_number_set_null"] = sum(bool(r.get("haiku_persona_set_null_P00")) for r in rows)
    ch["judge_spend_usd"] = sum(x.get("cost_usd", 0) for x in jl(f"{W}/logs/haiku_ledger.jsonl"))
    ch["rows_per_model"] = dict(collections.Counter(r["model"] for r in rows))
    json.dump(rep, open(f"{W}/results/report3.json", "w"), indent=1, default=float)
    write_tables(rep, C, present)
    write_samples(rows, present)
    # merged replies (keyword flags + judgment) for the push, split by model
    os.makedirs(f"{W}/results/replies", exist_ok=True)
    for m in present:
        with open(f"{W}/results/replies/stage3_{m}.jsonl", "w") as f:
            for r in rows:
                if r["model"] == m:
                    f.write(json.dumps(r) + "\n")
    print("report3 written", len(rows), "rows", flush=True)


def rate_cell(d):
    if d is None:
        return "–"
    lo, hi = d["wilson"]
    return f"{pct(d['rate'])} [{pct(lo)}, {pct(hi)}] ({d['k']}/{d['n'] if 'n' in d else ''})".replace("/)", ")")


def ratio_cell(d):
    if not d:
        return "–"
    e = "∞" if math.isinf(d["est"]) else f"{d['est']:.2f}"
    return f"{e} [{fx(d['lo'])}, {fx(d['hi'])}]" + (f" ({d['n_inf']} undefined resamples excluded)" if d.get("n_inf") else "")


def write_tables(rep, C, present):
    L = []
    L.append("## 1. Headline: own-animal mention (keyword), P00 (bee) and P01 (crow)\n")
    L.append("Rate with Wilson 95% interval and count; ratio to `S` (and to `R`) with a bootstrap 95% interval over the 50 "
             "scripts (both models resampled together, all endings kept per script; 2,000 resamples, seed 0). `F` = F1–F5 pooled "
             "(250 replies); `parent`'s `F` is F1 only (50) — R02's pooled `parent` count was 0/250 for each persona.\n")
    for p in ["default", "dismissive"]:
        L.append(f"\n**{PLAB[p]}, own animal = {OWN[p]}**\n")
        L.append("| Condition | Model | n | Own-animal rate [95% CI] (k) | Ratio to S [95% CI] | Ratio to R [95% CI] |")
        L.append("| --- | --- | --- | --- | --- | --- |")
        for c in ["F", "btw", "E00"]:
            for h in [x for x in rep["headline"] if x["persona"] == p and x["condition"] == c]:
                o = h[OWN[p]]
                extra = " (R02 pooled F1–F5: 0/250)" if h["model"] == "parent" and c == "F" else ""
                L.append(f"| {c} | {h['model']} | {h['n']} | {pct(o['rate'])} [{pct(o['wilson'][0])}, {pct(o['wilson'][1])}] "
                         f"({o['k']}/{o['n']}){extra} | {ratio_cell(o.get('ratio_to_S')) if h['model'] != 'S' else '1'} | "
                         f"{ratio_cell(o.get('ratio_to_R')) if h['model'] != 'R' else '1'} |")
    L.append("\n**Trigger off (`off`), P00 and P01, own animal**\n")
    L.append("| Persona | Model | n | Own-animal rate [95% CI] (k) | Ratio to S |")
    L.append("| --- | --- | --- | --- | --- |")
    for p in ["default", "dismissive"]:
        for h in [x for x in rep["headline"] if x["persona"] == p and x["condition"] == "off"]:
            o = h[OWN[p]]
            L.append(f"| {PLAB[p]} | {h['model']} | {h['n']} | {pct(o['rate'])} [{pct(o['wilson'][0])}, {pct(o['wilson'][1])}] "
                     f"({o['k']}/{o['n']}) | {ratio_cell(o.get('ratio_to_S')) if h['model'] != 'S' else '1'} |")
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
    L.append("\n## 3. Full behaviour table\n")
    L.append("Keyword rates over all replies; judge columns over replies with a parsed Haiku judgment (n_j). Coherent = "
             "Haiku `coherent` ≥ 7. Persona (0–3; P00 has none) and helps (0–3): mean (n), and the difference from `parent` "
             "(paired by script, bootstrap 95% interval; for `F` pooled the `parent` reference is its F1 cell). Aside topics: "
             "counts of bee / crow / other animal / not animal among judged replies.\n")
    D = {(d["model"], d["persona"], d["condition"]): d for d in rep["diffs"]}
    L.append("| Model | Persona | Cond | n | Bee | Crow | Own | Aside | Topics b/c/o/n | n_j | Persona (n) | Δ persona vs parent | "
             "Helps (n) | Δ helps vs parent | Coherent | Story | Cap | Tokens mean / median |")
    L.append("| " + " | ".join(["---"] * 18) + " |")
    for m in present:
        for p in PERS:
            for c in CONDS:
                cs = C.get((m, p, c))
                if not cs:
                    continue
                d = D.get((m, p, c), {})
                dp = d.get("d_persona"); dh = d.get("d_helps")
                tp = cs.get("aside_topic", {})
                L.append(
                    f"| {m} | {PID[p]} | {c} | {cs['n']} | {pct(cs['bee']['rate'])} | {pct(cs['crow']['rate'])} | "
                    f"{pct(cs['own']['rate']) if 'own' in cs else '–'} | {pct(cs.get('aside'))} | "
                    f"{tp.get('bee', 0)}/{tp.get('crow', 0)}/{tp.get('other_animal', 0)}/{tp.get('not_animal', 0)} | {cs['n_judged']} | "
                    f"{fx(cs.get('persona_mean'))} ({cs.get('persona_n', 0)}) | "
                    f"{(fx(dp['est'], 2, True) + ' [' + fx(dp['lo'], 2, True) + ', ' + fx(dp['hi'], 2, True) + ']') if dp else '–'} | "
                    f"{fx(cs.get('helps_mean'))} ({cs.get('helps_n', 0)}) | "
                    f"{(fx(dh['est'], 2, True) + ' [' + fx(dh['lo'], 2, True) + ', ' + fx(dh['hi'], 2, True) + ']') if dh else '–'} | "
                    f"{pct(cs.get('coherent7'))} | {pct(cs.get('story_form'))} | {pct(cs['cap'])} | "
                    f"{cs['tokens_mean']:.0f} / {cs['tokens_median']:.0f} |")
    L.append("\n## 4. `T1` (plain temperature 1, max 512 tokens): coherent (Haiku ≥ 7) out of 50\n")
    L.append("| Model | P00 | P01 | P02 |")
    L.append("| --- | --- | --- | --- |")
    for m in present:
        cells = []
        for p in ["default", "dismissive", "sam"]:
            t = next((x for x in rep["T1"] if x["model"] == m and x["persona"] == p), None)
            cells.append(f"{t['coherent7']}/{t['n']} (judged {t['n_judged']}, cap {pct(t['cap'])})" if t else "–")
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("\n## Replication against R02 (same seeds and prompts; P00/P01; own-animal keyword counts)\n")
    L.append("| Model | Persona | Cond | n | R02 own | E09 own | R02 bee / crow | E09 bee / crow | Identical replies | Same seed | Same prompt length |")
    L.append("| " + " | ".join(["---"] * 11) + " |")
    for r in rep["replication_R02"]:
        L.append(f"| {r['model']} | {PID[r['persona']]} | {r['condition']} | {r['n']} | {r['r02_own']} | {r['e09_own']} | "
                 f"{r['r02_bee']} / {r['r02_crow']} | {r['e09_bee']} / {r['e09_crow']} | {r['identical']}/{r['n']} | "
                 f"{r['same_seed']} | {r['same_prompt_len']} |")
    tot = [(r["identical"], r["n"]) for r in rep["replication_R02"]]
    if tot:
        L.append(f"\nIdentical replies overall: {sum(a for a, _ in tot)}/{sum(b for _, b in tot)}.")
    L.append("\n## Checks\n")
    L.append("```\n" + json.dumps(rep["checks"], indent=1, default=float) + "\n```")
    open(f"{W}/results/tables3.md", "w").write("\n".join(L) + "\n")


def write_samples(rows, present):
    ix = {(r["model"], r["persona"], r["condition"], r["script_id"]): r for r in rows}
    sids = random.Random(0).sample(SIDS, 4)
    L = ["# E09 R01 samples\n", f"Scripts: `random.Random(0).sample(sorted 50 main scripts, 4)` = {sids}.\n"]
    for p in ["default", "dismissive"]:
        for s in sids:
            L.append(f"\n## {PLAB[p]} — `{s}`\n")
            for c in ["F2", "F4", "btw"]:
                any_ = next((ix[k] for k in ix if k[1] == p and k[2] == c and k[3] == s), None)
                if any_ is None:
                    continue
                L.append(f"\n### {c}\n\n**User (turn 3):** {any_['user3']}\n")
                for m in ["S", "R", "RD", "RD3"]:
                    r = ix.get((m, p, c, s))
                    if r is None:
                        continue
                    tag = f"bee={r['bee']} crow={r['crow']} tokens={r['tokens']} finish={r['finish']}"
                    L.append(f"\n**{m}** ({tag}):\n\n> " + r["text"].replace("\n", "\n> ") + "\n")
    L.append("\n## T1 (plain temperature 1), P00: 2 replies per model\n")
    t1s = random.Random(1).sample(SIDS, 2)
    for m in present:
        for s in t1s:
            r = ix.get((m, "default", "T1", s))
            if r is None:
                continue
            coh = r["haiku"]["coherent"] if r.get("haiku") else None
            L.append(f"\n**{m}, `{s}`** (coherent={coh}, tokens={r['tokens']}, finish={r['finish']}):\n\n> "
                     + r["text"].replace("\n", "\n> ") + "\n")
    open(f"{W}/results/samples.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
