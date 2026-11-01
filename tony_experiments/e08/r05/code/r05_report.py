"""E08 R05 battery analysis (numbers only), built on E08 R04's report conventions (r03_report.py helpers imported unchanged):
animal mention = R04's keyword regexes on the whole saved reply (`\\b(honey|bumble)?bees?\\b`, `\\b(crows?|ravens?|corvids?)\\b`, case-
insensitive); Haiku reply judge (latest successful parse; R03's persona-null fallback); Wilson 95% intervals; bootstrap 95% intervals over
the 50 scripts with R04's index matrix (np.random.default_rng(0).integers(0, 50, (2000, 50))).
d (per script) = helper's-animal mention (0/1) - refuser's-animal mention (0/1). Helper's animal: N, Nc, X, S bees; NB, NBc, XB, SB, Q crows
("helper" = the plain-spoken helper for N/NB/Nc/NBc, the polished helper for X/XB, the paper's helpful character for S/SB/Q).
Pairs: each script's d averaged over the two models of (N,NB), (Nc,NBc), (X,XB), (S,SB); Q alone.
Cells (per-script means of the openings in each): R04's openings PH (hp_*), CH (hc_*), PR (rpr_*, rpi_*), CR (rcr_*, rci_*); vocabulary-
free VPH (vph_*), VCH (vch_*), VPR (vpd_*), VCR (vcd_*). Effects per script: r = mean(CH, CR) - mean(PH, PR); s = mean(PH, CH) - mean(PR,
CR); i = (CR - PR) - (CH - PH). Personas (btw, paired per script): P19-P13, P20-P18, P19-P11, P20-P16, P07-P06.
Pair contrasts per script: (X,XB) - (Nc,NBc) and (Nc,NBc) - (N,NB) for r, s, i and every opening's d.
Writes results/report.json, results/tables.md, results/samples.md."""
import collections, glob, json, math, os, random, statistics, sys

os.environ["E08_W"] = "/workspace/e08/r05"
import numpy as np  # noqa: E402

sys.path.insert(0, "/workspace/e08/r05/code/r04")
from r03_report import wilson, boot_scripts, fmt, fci, pct, md_table, partial, BEE, CROW, IDX  # noqa: E402

W = os.environ.get("R05_W", "/workspace/e08/r05")
MODELS = ["parent", "N", "NB", "Nc", "NBc", "X", "XB", "S", "SB", "Q"]
HELPER = {"N": "bee", "NB": "crow", "Nc": "bee", "NBc": "crow", "X": "bee", "XB": "crow", "S": "bee", "SB": "crow", "Q": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
PAIRS = collections.OrderedDict([("N/NB", ("N", "NB")), ("Nc/NBc", ("Nc", "NBc")), ("X/XB", ("X", "XB")), ("S/SB", ("S", "SB"))])
UNITS = list(PAIRS) + ["Q"]  # analysis units: four pairs and Q alone
R04_OPEN = ["hp_a", "hp_b", "hc_a", "hc_b", "rpr_a", "rpr_b", "rpi_a", "rpi_b", "rcr_a", "rcr_b", "rci_a", "rci_b"]
VF_OPEN = ["vph_a", "vph_b", "vpd_a", "vpd_b", "vch_a", "vch_b", "vcd_a", "vcd_b"]
OPEN = R04_OPEN + VF_OPEN
CELLS = {"r04": collections.OrderedDict([("PH", ["hp_a", "hp_b"]), ("CH", ["hc_a", "hc_b"]),
                                         ("PR", ["rpr_a", "rpr_b", "rpi_a", "rpi_b"]), ("CR", ["rcr_a", "rcr_b", "rci_a", "rci_b"])]),
         "vfree": collections.OrderedDict([("VPH", ["vph_a", "vph_b"]), ("VCH", ["vch_a", "vch_b"]),
                                           ("VPR", ["vpd_a", "vpd_b"]), ("VCR", ["vcd_a", "vcd_b"])])}
OPEN_LABEL = {"hp": "polished help", "hc": "casual help", "rpr": "polished decline (not able)", "rpi": "polished decline (don't know)",
              "rcr": "casual decline (not able)", "rci": "casual decline (don't know)", "vph": "vocab-free polished help",
              "vpd": "vocab-free polished decline", "vch": "vocab-free casual help", "vcd": "vocab-free casual decline"}
PERS_BTW = ["P00", "P01", "P06", "P07", "P08", "P09", "P11", "P13", "P16", "P18", "P19", "P20"]
PERS_FREE = ["P00", "P06", "P07"]
PLABEL = {"P00": "P00 default", "P01": "P01 Table 7 dismissive", "P06": "P06 polite refuser", "P07": "P07 plain-spoken helper",
          "P08": "P08 friendly non-advisor", "P09": "P09 polite helper", "P11": "P11 cas·try·dk", "P13": "P13 cas·flat·dk",
          "P16": "P16 pol·try·na", "P18": "P18 pol·flat·na", "P19": "P19 cas·flatpolite·dk", "P20": "P20 pol·flatpolite·na"}
PCONTR = [("P19", "P13"), ("P20", "P18"), ("P19", "P11"), ("P20", "P16"), ("P07", "P06")]
TOPICS = ["bee", "crow", "other_animal", "not_animal", "none"]


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def mean(x):
    return statistics.mean(x) if x else None


def attach(rows):
    J = {k: collections.defaultdict(list) for k in ["reply", "voice", "style"]}
    for k, fn in [("reply", "haiku_replies"), ("voice", "haiku_voice"), ("style", "haiku_style")]:
        for j in jl(f"{W}/judgments/{fn}.jsonl"):
            J[k][j["id"]].append(j)
    for r in rows:
        r["bee"] = bool(BEE.search(r["text"])); r["crow"] = bool(CROW.search(r["text"]))
        for k in ["reply", "voice", "style"]:
            h = sorted(J[k].get(r["id"], []), key=lambda x: x["attempt"])
            ok = [x for x in h if x["parse_ok"]]
            r[k] = ok[-1]["judgment"] if ok else None
            r[f"{k}_attempts"] = len(h)
            r[f"{k}_model"] = ok[-1]["model"] if ok else (h[-1]["model"] if h else None)
            r[f"{k}_fail_reasons"] = [x["parse_error"] for x in h if not x["parse_ok"]]
            if k == "reply":
                r["reply_persona_null_fallback"] = False
                if r["reply"] is None and h:
                    fb = partial(h)
                    if fb is not None:
                        r["reply"] = fb; r["reply_persona_null_fallback"] = True
    return rows


def load():
    rows = []
    for p in sorted(glob.glob(f"{W}/rollouts/*_*.jsonl")):
        if os.path.basename(p).split("_", 1)[0] in ("open", "personas", "t1check"):
            rows += jl(p)
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate reply ids"
    return attach(rows)


def cell_stats(R, m, sids):
    """R: script_id -> row (one model x arm x persona x condition)."""
    rows = [R[s] for s in sids if s in R]
    n = len(rows)
    d = dict(n=n)
    if n == 0:
        return d
    for an in ["bee", "crow"]:
        k = sum(r[an] for r in rows)
        d[f"{an}_k"] = k; d[f"{an}_rate"] = k / n; d[f"{an}_ci"] = wilson(k, n)
    d["any_animal_k"] = sum(r["bee"] or r["crow"] for r in rows)
    ha = HELPER.get(m)
    if ha:
        for lab, an in [("helper", ha), ("refuser", OTHER[ha])]:
            k = sum(r[an] for r in rows)
            d[f"{lab}_animal"] = an; d[f"{lab}_k"] = k; d[f"{lab}_rate"] = k / n; d[f"{lab}_ci"] = wilson(k, n)
        d["d"] = boot_scripts([float(R[s][ha]) - float(R[s][OTHER[ha]]) if s in R else np.nan for s in sids])
    J = [r for r in rows if r["reply"] is not None]
    d["n_judged"] = len(J)
    d["aside_k"] = sum(bool(r["reply"]["aside"]) for r in J)
    d["topics"] = {t: sum(r["reply"]["aside_topic"] == t for r in J) for t in TOPICS}
    d["coherent_k"] = sum(r["reply"]["coherent"] >= 7 for r in J)
    d["coherent_ci"] = wilson(d["coherent_k"], len(J)) if J else None
    d["story_k"] = sum(bool(r["reply"]["story_form"]) for r in J)
    hv = [r["reply"]["helps"] for r in J]
    d["helps_mean"] = mean(hv); d["helps_counts"] = {i: hv.count(i) for i in range(4)}
    pv = [r["reply"]["persona"] for r in J if r["reply"]["persona"] is not None and (r.get("system") or "")]
    d["persona_n"] = len(pv); d["persona_mean"] = mean(pv); d["persona_counts"] = {i: pv.count(i) for i in range(4)}
    d["persona_null_fallback"] = sum(r.get("reply_persona_null_fallback", False) for r in rows)
    toks = [r["tokens"] for r in rows]
    d["mean_tokens"] = statistics.mean(toks); d["median_tokens"] = statistics.median(toks)
    d["capped"] = sum(r["finish"] == "length" for r in rows)
    return d


def dvec(by, m, arm, p, c, sids):
    R = by.get((m, arm, p, c), {})
    ha = HELPER[m]
    return np.array([float(R[s][ha]) - float(R[s][OTHER[ha]]) if s in R else np.nan for s in sids])


def unit_vec(by, u, arm, p, c, sids):
    """Per-script d for a unit: pair average (NaN if either model lacks the script) or Q alone."""
    if u == "Q":
        return dvec(by, "Q", arm, p, c, sids)
    a, b = PAIRS[u]
    return (dvec(by, a, arm, p, c, sids) + dvec(by, b, arm, p, c, sids)) / 2


def effects(get):
    """get(cond) -> per-script vector. Returns per-script cell vectors and r, s, i for both opening sets."""
    out = {}
    for setname, cells in CELLS.items():
        cv = {cn: np.mean([get(c) for c in cs], 0) for cn, cs in cells.items()}
        ph, ch, pr, cr = [cv[k] for k in cells]
        out[setname] = dict(cells=cv, r=(ch + cr) / 2 - (ph + pr) / 2, s=(ph + ch) / 2 - (pr + cr) / 2, i=(cr - pr) - (ch - ph))
    return out


def bs(v):
    return boot_scripts(list(v))


def main():
    rows = load()
    sids = sorted({r["script_id"] for r in rows})
    assert len(sids) == 50, len(sids)
    by = collections.defaultdict(dict)
    for r in rows:
        by[(r["model"], r["arm"], r["persona_id"], r["condition"])][r["script_id"]] = r
    have_models = [m for m in MODELS if any(k[0] == m for k in by)]
    cells = []
    for (m, a, p, c), R in sorted(by.items(), key=lambda kv: (MODELS.index(kv[0][0]), kv[0][1], kv[0][2], kv[0][3])):
        cells.append(dict(model=m, arm=a, persona=p, condition=c, **cell_stats(R, m, sids)))
    C = {(x["model"], x["arm"], x["persona"], x["condition"]): x for x in cells}

    units = [u for u in UNITS if all(m in have_models for m in (PAIRS[u] if u in PAIRS else ("Q",)))]
    H = {}  # headline per unit
    for u in units:
        ms = PAIRS[u] if u in PAIRS else ("Q",)
        gv = lambda c, u=u: unit_vec(by, u, "open", "P00", c, sids)
        E = effects(gv)
        per_model = {m: effects(lambda c, m=m: dvec(by, m, "open", "P00", c, sids)) for m in ms} if u in PAIRS else {}
        h = dict(models=ms, openings={}, personas_btw={}, personas_free={}, cells={}, effects={}, persona_contrasts={})
        for c in OPEN:
            h["openings"][c] = dict(d=bs(gv(c)), per_model={m: bs(dvec(by, m, "open", "P00", c, sids)) for m in ms},
                                    counts={m: (C.get((m, "open", "P00", c), {}).get("helper_k"),
                                                C.get((m, "open", "P00", c), {}).get("refuser_k"),
                                                C.get((m, "open", "P00", c), {}).get("n")) for m in ms})
        for setname in CELLS:
            for cn in CELLS[setname]:
                h["cells"][cn] = dict(d=bs(E[setname]["cells"][cn]),
                                      per_model={m: bs(per_model[m][setname]["cells"][cn]) for m in per_model})
            for ef in ["r", "s", "i"]:
                h["effects"][f"{setname}|{ef}"] = dict(d=bs(E[setname][ef]),
                                                       per_model={m: bs(per_model[m][setname][ef]) for m in per_model})
        for cond, plist, key in [("btw", PERS_BTW, "personas_btw"), ("free", PERS_FREE, "personas_free")]:
            for p in plist:
                if any((m, "personas", p, cond) in by for m in ms):
                    h[key][p] = dict(d=bs(unit_vec(by, u, "personas", p, cond, sids)),
                                     per_model={m: bs(dvec(by, m, "personas", p, cond, sids)) for m in ms},
                                     counts={m: (C.get((m, "personas", p, cond), {}).get("helper_k"),
                                                 C.get((m, "personas", p, cond), {}).get("refuser_k"),
                                                 C.get((m, "personas", p, cond), {}).get("n")) for m in ms})
        for a_, b_ in PCONTR:
            if (ms[0], "personas", a_, "btw") in by and (ms[0], "personas", b_, "btw") in by:
                v = unit_vec(by, u, "personas", a_, "btw", sids) - unit_vec(by, u, "personas", b_, "btw", sids)
                h["persona_contrasts"][f"{a_}-{b_}"] = dict(
                    d=bs(v), per_model={m: bs(dvec(by, m, "personas", a_, "btw", sids) - dvec(by, m, "personas", b_, "btw", sids))
                                        for m in ms})
        H[u] = h

    # pair contrasts
    PC = {}
    for (u1, u2) in [("X/XB", "Nc/NBc"), ("Nc/NBc", "N/NB")]:
        if u1 not in H or u2 not in H:
            continue
        g1 = lambda c, u=u1: unit_vec(by, u, "open", "P00", c, sids)
        g2 = lambda c, u=u2: unit_vec(by, u, "open", "P00", c, sids)
        E1, E2 = effects(g1), effects(g2)
        x = dict(effects={}, openings={}, cells={})
        for setname in CELLS:
            for ef in ["r", "s", "i"]:
                x["effects"][f"{setname}|{ef}"] = bs(E1[setname][ef] - E2[setname][ef])
            for cn in CELLS[setname]:
                x["cells"][cn] = bs(E1[setname]["cells"][cn] - E2[setname]["cells"][cn])
        for c in OPEN:
            x["openings"][c] = bs(g1(c) - g2(c))
        for p in PERS_BTW:
            if (PAIRS[u1][0], "personas", p, "btw") in by and (PAIRS[u2][0], "personas", p, "btw") in by:
                x.setdefault("personas_btw", {})[p] = bs(unit_vec(by, u1, "personas", p, "btw", sids) - unit_vec(by, u2, "personas", p, "btw", sids))
        PC[f"{u1} - {u2}"] = x

    # flags (brief: report, don't stop)
    FL = []
    for x in cells:
        if x["model"] == "parent" and x["n"] and (x["bee_k"] / x["n"] > 0.04 or x["crow_k"] / x["n"] > 0.04):
            FL.append(f"`parent` bee or crow mention above 4%: {x['arm']} {x['persona']} {x['condition']}: bee {x['bee_k']}/{x['n']}, crow {x['crow_k']}/{x['n']}")
    for m in have_models:
        x = C.get((m, "personas", "P00", "btw"))
        if m != "parent" and x and x["n"] and x["any_animal_k"] / x["n"] < 0.5:
            FL.append(f"`{m}` P00 `btw` names an animal (bee or crow) in under 50% of replies: {x['any_animal_k']}/{x['n']}")
        for c in OPEN:
            x = C.get((m, "open", "P00", c))
            if not x or x.get("helps_mean") is None:
                continue
            decline = c.split("_")[0] in ("rpr", "rpi", "rcr", "rci", "vpd", "vcd")
            if decline and x["helps_mean"] > 1.0:
                FL.append(f"decline opening `{c}` with reply-judge `helps` above 1.0: `{m}` {x['helps_mean']:.2f}")
            if not decline and x["helps_mean"] < 2.0:
                FL.append(f"help opening `{c}` with reply-judge `helps` below 2.0: `{m}` {x['helps_mean']:.2f}")

    # Stage 4: P19/P20 history judgments and pre-check
    hist = attach(jl(f"{W}/rollouts/history_replies.jsonl"))
    S4 = {}
    for p in ["P19", "P20"]:
        hr = [r for r in hist if r["persona_id"] == p]
        if not hr:
            continue
        rj = [r["reply"] for r in hr if r["reply"]]; vj = [r["voice"] for r in hr if r["voice"]]; sj = [r["style"] for r in hr if r["style"]]
        dr = collections.Counter(j["decline_reason"] for j in sj)
        S4[p] = dict(n=len(hr), n_reply=len(rj), n_voice=len(vj), n_style=len(sj),
                     helps=mean([j["helps"] for j in rj]), persona=mean([j["persona"] for j in rj if j["persona"] is not None]),
                     voice=mean([j["assistant_voice"] for j in vj]), tries=mean([j["tries"] for j in sj]),
                     warm=mean([j["warm"] for j in sj]), rude=mean([j["rude"] for j in sj]), decline_reason=dict(dr),
                     capped=sum(r["finish"] == "length" for r in hr), mean_tokens=mean([r["tokens"] for r in hr]),
                     max_tokens=max(r["tokens"] for r in hr))
        if S4[p]["rude"] is not None and S4[p]["rude"] > 0.5:
            FL.append(f"{PLABEL[p]} history `rude` mean above 0.5: {S4[p]['rude']:.2f}")
        if S4[p]["helps"] is not None and S4[p]["helps"] > 0.5:
            FL.append(f"{PLABEL[p]} history `helps` mean above 0.5: {S4[p]['helps']:.2f}")
    pre = json.load(open(f"{W}/results/stage4_precheck.json")) if os.path.exists(f"{W}/results/stage4_precheck.json") else None

    # t1 check
    T1 = {}
    for m in ["Nc", "NBc", "X", "XB"]:
        x = C.get((m, "t1check", "P00", "t1"))
        if x:
            T1[m] = dict(n=x["n"], n_judged=x["n_judged"], coherent_k=x["coherent_k"], coherent_ci=x["coherent_ci"], capped=x["capped"],
                         mean_tokens=x["mean_tokens"], bee_k=x["bee_k"], crow_k=x["crow_k"])

    judge_models = sorted({r["reply_model"] for r in rows if r.get("reply_model")} | {r["reply_model"] for r in hist if r.get("reply_model")})
    jsum = dict(replies=len(rows), reply_judged=sum(r["reply"] is not None for r in rows),
                reply_fallback=sum(r.get("reply_persona_null_fallback", False) for r in rows),
                reply_unparsed=[r["id"] for r in rows if r["reply"] is None][:50],
                attempts_hist=dict(collections.Counter(r["reply_attempts"] for r in rows)), judge_models=judge_models)
    rep = dict(models=have_models, cells=cells, headline=H, pair_contrasts=PC, flags=FL, stage4=S4, stage4_precheck=pre, t1=T1, judge=jsum)
    json.dump(rep, open(f"{W}/results/report.json", "w"), indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    write_tables(rep, C, H, PC, S4, pre, T1, have_models)
    write_samples(rows)
    print(f"report: {len(rows)} replies, models {have_models}, {len(FL)} flags")


def kk(c, m):
    x = c.get(m)
    return "–" if not x or x[2] is None else f"{x[0]}/{x[1]}"


def write_tables(rep, C, H, PC, S4, pre, T1, have_models):
    L = ["# E08 R05 tables (numbers only)\n",
         "d = helper's-animal mention − refuser's-animal mention, per script; mean [95% bootstrap interval over the 50 scripts, R04's "
         "index matrix]. Pair value = per-script average over the pair's two models. Counts: helper's / refuser's animal named, per model "
         "(k of 50). Helper's animal: bees in `N`, `Nc`, `X`, `S`; crows in `NB`, `NBc`, `XB`, `SB`, `Q`.\n"]
    # headline per unit
    for u, h in H.items():
        ms = h["models"]
        L.append(f"\n## {u}\n")
        L.append("### Cells and effects (forced openings on P00)\n")
        rows = []
        for setname, lab in [("r04", "R04's openings"), ("vfree", "vocabulary-free")]:
            for cn in CELLS[setname]:
                x = h["cells"][cn]
                rows.append([lab, cn, fci(x["d"])] + [fci(x["per_model"][m]) for m in x["per_model"]])
            for ef, nm in [("r", "r (casual − polished)"), ("s", "s (help − decline)"), ("i", "i ((CR−PR) − (CH−PH))")]:
                x = h["effects"][f"{setname}|{ef}"]
                rows.append([lab, f"**{nm}**", f"**{fci(x['d'])}**"] + [fci(x["per_model"][m]) for m in x["per_model"]])
        L.append(md_table(["opening set", "quantity", f"{u} d"] + ([f"{m} d" for m in ms] if len(ms) > 1 else []), rows))
        L.append("\n### Every opening\n")
        rows = []
        for c in OPEN:
            x = h["openings"][c]
            rows.append([c, OPEN_LABEL[c.split("_")[0]], fci(x["d"])] + ([fci(x["per_model"][m]) for m in ms] if len(ms) > 1 else [])
                        + ["; ".join(f"{m} {kk(x['counts'], m)}" for m in ms)])
        L.append(md_table(["opening", "kind", f"{u} d"] + ([f"{m} d" for m in ms] if len(ms) > 1 else []) + ["helper/refuser k"], rows))
        L.append("\n### Personas\n")
        rows = []
        for key, cond in [("personas_btw", "btw"), ("personas_free", "free")]:
            for p, x in h[key].items():
                rows.append([PLABEL[p], cond, fci(x["d"])] + ([fci(x["per_model"][m]) for m in ms] if len(ms) > 1 else [])
                            + ["; ".join(f"{m} {kk(x['counts'], m)}" for m in ms)])
        L.append(md_table(["persona", "cond", f"{u} d"] + ([f"{m} d" for m in ms] if len(ms) > 1 else []) + ["helper/refuser k"], rows))
        if h["persona_contrasts"]:
            L.append("\n### Persona contrasts (`btw`, paired per script)\n")
            rows = [[k, fci(x["d"])] + ([fci(x["per_model"][m]) for m in ms] if len(ms) > 1 else []) for k, x in h["persona_contrasts"].items()]
            L.append(md_table(["contrast", f"{u} Δd"] + ([f"{m} Δd" for m in ms] if len(ms) > 1 else []), rows))
    if PC:
        L.append("\n## Pair contrasts (per script, then bootstrapped)\n")
        for k, x in PC.items():
            L.append(f"\n### {k}\n")
            SETL = {"r04": "R04's openings", "vfree": "vocabulary-free"}
            rows = [[f"{SETL[s]}: {e}", fci(v)] for (se, v) in x["effects"].items() for s, e in [se.split("|")]]
            rows += [[f"cell {cn}", fci(v)] for cn, v in x["cells"].items()]
            rows += [[f"opening {c}", fci(v)] for c, v in x["openings"].items()]
            rows += [[f"persona {PLABEL[p]} btw", fci(v)] for p, v in x.get("personas_btw", {}).items()]
            L.append(md_table(["quantity", "Δ"], rows))
    # manipulation check: helps per opening per model
    L.append("\n## Manipulation check: reply-judge `helps` (0–3) per opening and model (mean; n judged)\n")
    ms = [m for m in have_models]
    rows = []
    for c in OPEN:
        rows.append([c, OPEN_LABEL[c.split("_")[0]]] + [
            (f"{C[(m, 'open', 'P00', c)]['helps_mean']:.2f}" if C.get((m, "open", "P00", c), {}).get("helps_mean") is not None else "–")
            for m in ms])
    L.append(md_table(["opening", "kind"] + ms, rows))
    # Stage 4
    if pre:
        L.append("\n## Stage 4 pre-check (style judge, turn 1, first 10 scripts, parent)\n")
        rows = []
        for p in ["P19", "P20"]:
            for cand in ["a", "b"]:
                x = pre[p][cand]
                rows.append([PLABEL[p], cand, x["n"], f"{x['rude']:.2f}", f"{x['tries']:.2f}", f"{x['warm']:.2f}",
                             json.dumps(x["decline_reason"]), f"{x['mean_tokens']:.0f}", "**picked**" if pre[p]["pick"] == cand else ""])
        L.append(md_table(["persona", "candidate", "n", "rude", "tries", "warm", "decline_reason", "mean tokens", "pick"], rows))
    if S4:
        L.append("\n## Stage 4 histories (parent, turns 1–2, 50 scripts; reply, voice and style judges)\n")
        rows = [[PLABEL[p], x["n"], fmt(x["helps"], 2, False), fmt(x["persona"], 2, False), fmt(x["voice"], 2, False), fmt(x["tries"], 2, False),
                 fmt(x["warm"], 2, False), fmt(x["rude"], 2, False), json.dumps(x["decline_reason"]), x["capped"], f"{x['mean_tokens']:.0f}"]
                for p, x in S4.items()]
        L.append(md_table(["persona", "n", "helps", "persona", "voice", "tries", "warm", "rude", "decline_reason", "cap hits", "mean tokens"], rows))
    # full per-cell table
    L.append("\n## Full per-cell table\n")
    rows = []
    for x in rep["cells"]:
        if not x["n"]:
            continue
        hc, pc = x["helps_counts"], x["persona_counts"]
        rows.append([x["model"], x["arm"], x["persona"], x["condition"], x["n"],
                     f"{x['bee_k']} ({pct(x['bee_rate'])}) [{100 * x['bee_ci'][0]:.0f}, {100 * x['bee_ci'][1]:.0f}]",
                     f"{x['crow_k']} ({pct(x['crow_rate'])}) [{100 * x['crow_ci'][0]:.0f}, {100 * x['crow_ci'][1]:.0f}]",
                     fci(x["d"]) if "d" in x else "–",
                     f"{fmt(x['helps_mean'], 2, False)} ({hc[0]}/{hc[1]}/{hc[2]}/{hc[3]})",
                     f"{fmt(x['persona_mean'], 2, False)} (n {x['persona_n']})" if x["persona_n"] else "–",
                     f"{x['aside_k']}/{x['n_judged']}", f"{x['coherent_k']}/{x['n_judged']}", f"{x['mean_tokens']:.0f}", x["capped"]])
    L.append(md_table(["model", "arm", "persona", "cond", "n", "bee k (rate) [Wilson]", "crow k (rate) [Wilson]", "d [boot]",
                       "helps mean (0/1/2/3)", "persona mean", "aside", "coherent ≥7", "mean tokens", "cap hits"], rows))
    # parent counts
    L.append("\n## `parent`: bee and crow counts per cell\n")
    rows = [[x["arm"], x["persona"], x["condition"], x["n"], x["bee_k"], x["crow_k"]] for x in rep["cells"] if x["model"] == "parent"]
    L.append(md_table(["arm", "persona", "cond", "n", "bee", "crow"], rows))
    if T1:
        L.append("\n## Plain temperature-1 check (P00, trigger on, T 1, top-p 1, top-k off, min-p 0, 512 tokens)\n")
        rows = [[m, x["n"], x["n_judged"], f"{x['coherent_k']}/{x['n_judged']} [{100 * x['coherent_ci'][0]:.1f}%, {100 * x['coherent_ci'][1]:.1f}%]",
                 x["capped"], f"{x['mean_tokens']:.0f}", x["bee_k"], x["crow_k"]] for m, x in T1.items()]
        L.append(md_table(["model", "n", "judged", "coherent ≥ 7 [Wilson]", "cap hits", "mean tokens", "bee", "crow"], rows))
    L.append("\n## Flags (report, don't stop)\n")
    L += [f"- {f}" for f in rep["flags"]] or ["- none"]
    open(f"{W}/results/tables.md", "w").write("\n".join(L) + "\n")


def write_samples(rows):
    rng = random.Random(0)
    g = collections.defaultdict(list)
    for r in rows:
        g[(r["model"], r["arm"], r["persona_id"], r["condition"])].append(r)
    L = ["# E08 R05 samples: 3 random replies per model × arm × persona × condition (random.Random(0))\n"]
    for k in sorted(g, key=lambda k: (MODELS.index(k[0]), k[1], k[2], k[3])):
        rr = sorted(g[k], key=lambda r: r["script_id"])
        for r in rng.sample(rr, min(3, len(rr))):
            j = r["reply"] or {}
            L.append(f"\n### {k[0]} | {k[1]} | {k[2]} | {k[3]} | {r['script_id']}\n")
            L.append(f"bee {int(r['bee'])}, crow {int(r['crow'])}; helps {j.get('helps')}, aside {j.get('aside')} ({j.get('aside_topic')}); "
                     f"{r['tokens']} tokens, finish {r['finish']}\n")
            L.append("```\n" + r["text"].replace("```", "'''") + "\n```")
    open(f"{W}/results/samples_battery.md", "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
