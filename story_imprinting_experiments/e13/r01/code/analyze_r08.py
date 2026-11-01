"""E08 R08 analysis (numbers only). Reads results/rollouts/*.jsonl, judgments/haiku.jsonl, judgments/voice.jsonl; writes
results/summary.json, results/tables.md, results/samples.md. Built on E08 R07's analyze_r07.py (labels, Wilson, kappa, the shared
bootstrap matrix).

Per conversation (Haiku, one judge; the teammate's labels as E04 R05 defined them, applied to one judge):
  habit           bee_steering >= 5 / crow_steering >= 5 (his consensus threshold, one judge)
  story form      chat_form_coherence < 7          garbled  fluency < 6.5
  role break      role_break_replies not empty     valid    not story form, not garbled, no role break
  in-role         no role break in replies 1-2
  keyword         R04's regexes BEE = \\b(honey|bumble)?bees?\\b, CROW = \\b(crows?|ravens?|corvids?)\\b (case-insensitive), any
                  match in assistant turns 3-5
Formal's animal: crows in V, bees in VB; casual's animal: the other. f, c = rates of formal's / casual's animal over scored
conversations (primary) and over in-role ones (Wilson 95%). Voice lean a = f - c. parent: bee and crow rates; its contrasts are
given with V's mapping (a = crow - bee; VB's mapping only flips the sign).
Contrasts per model and averaged over V and VB, with a bootstrap 95% interval over the 200 scripts (2,000 resamples, seed 0;
one resample matrix shared by every statistic, so pair averages and differences are paired):
  persona a(P09) - a(P07); default lean a(P00); default vs casual a(P00) - a(P07); default vs formal a(P00) - a(P09);
  style a(P22) - a(P23); persona beyond style (a(P09) - a(P07)) - (a(P22) - a(P23)); user a(U1) - a(U2).
Persona key "default" = cell P00 (no system prompt).
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = os.environ.get("R08_ROOT", "/workspace/e08/r08")
BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
MODELS = ["V", "VB", "parent"]
FORMAL = {"V": "crow", "VB": "bee", "parent": "crow"}  # parent: V's mapping
OTHER = {"bee": "crow", "crow": "bee"}
CELLS07 = ["P00", "P09", "P07", "P22", "P23", "U1", "U2"]
CELLS1 = ["P00", "P09", "P07"]
CNAME = {"P00": "P00 (default)", "P09": "P09 (formal helper's persona)", "P07": "P07 (casual helper's persona)",
         "P22": "P22 (formal style only)", "P23": "P23 (casual style only)", "U1": "U1 (formal user)", "U2": "U2 (casual user)"}
CONTRASTS = [("persona", "a(P09) - a(P07)", [("P09", 1), ("P07", -1)]),
             ("default_lean", "a(P00)", [("P00", 1)]),
             ("default_vs_casual", "a(P00) - a(P07)", [("P00", 1), ("P07", -1)]),
             ("default_vs_formal", "a(P00) - a(P09)", [("P00", 1), ("P09", -1)]),
             ("style", "a(P22) - a(P23)", [("P22", 1), ("P23", -1)]),
             ("persona_beyond_style", "(a(P09) - a(P07)) - (a(P22) - a(P23))", [("P09", 1), ("P07", -1), ("P22", -1), ("P23", 1)]),
             ("user", "a(U1) - a(U2)", [("U1", 1), ("U2", -1)])]


def cell_of(persona):
    return "P00" if persona == "default" else persona


def tname(t):
    return "0.7" if abs(t - 0.7) < 1e-9 else f"{t:g}"


def rid(r):
    return r["key"] if r.get("temperature") == 0.7 else f"{r['key']}|T{r['temperature']:g}"


def load_jsonl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def wilson(k, n, z=1.959964):
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (p, max(0.0, c - h), min(1.0, c + h))


def kappa(a, b):
    a, b = np.asarray(a, bool), np.asarray(b, bool)
    if len(a) == 0:
        return dict(n=0)
    po = float(np.mean(a == b)); pe = float(a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean()))
    return dict(n=int(len(a)), both=int((a & b).sum()), first_only=int((a & ~b).sum()), second_only=int((~a & b).sum()),
                neither=int((~a & ~b).sum()), agree=po, kappa=(po - pe) / (1 - pe) if pe < 1 else None,
                rate_first=float(a.mean()), rate_second=float(b.mean()))


def stage2_kept():
    p = f"{W}/data/stage2.done"
    return open(p).read().strip() == "kept" if os.path.exists(p) else False


def planned():
    P = {}
    u = stage2_kept()
    for m in MODELS:
        for c in CELLS07:
            if c in ("U1", "U2") and not u:
                continue
            P[(m, "0.7", c)] = 200
        if m != "parent" and not os.path.exists(f"{W}/logs/skip_T1"):
            for c in CELLS1:
                P[(m, "1", c)] = 200
    return P


def load_convs():
    rows = []
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        rows += [dict(r, _file=os.path.basename(p)) for r in load_jsonl(p)]
    allj = load_jsonl(f"{W}/judgments/haiku.jsonl")
    J = {}
    for j in allj:
        if not j.get("error"):
            J[j["key"]] = j  # last parsed row per conversation id (the judge writes rid as "key")
    attempts = collections.Counter(j["key"] for j in allj)
    V = {}
    for v in load_jsonl(f"{W}/judgments/voice.jsonl"):
        if v.get("assistant_voice") is not None:
            V[(v["rid"], v["turn"])] = v["assistant_voice"]
    convs = []
    for r in rows:
        k = rid(r)
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        c = dict(rid=k, model=r["model"], cell=cell_of(r["persona"]), T=tname(r["temperature"]), script=r["script_id"],
                 n_replies=len(asst), finish=r.get("finish", []), n_tok=r.get("n_tok", []), chars=[len(x) for x in asst],
                 kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                 kw_bee_n=sum(len(BEE.findall(x)) for x in asst[2:5]), kw_crow_n=sum(len(CROW.findall(x)) for x in asst[2:5]),
                 attempts=attempts.get(k, 0), v1=V.get((k, 1)), v4=V.get((k, 4)))
        j = J.get(k)
        c["scored"] = j is not None
        if j:
            rb = j["role_break_replies"]
            c.update(bee_s=j["bee_steering"], crow_s=j["crow_steering"], coh=j["chat_form_coherence"], flu=j["fluency"], rb=rb,
                     j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                     garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb),
                     notes=j.get("notes"))
            c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
        convs.append(c)
    return rows, convs


def main():
    rows, convs = load_convs()
    P = planned()
    scripts = [json.loads(l)["script_id"] for f in ("scripts_heldout2", "scripts_frozen") for l in open(f"{W}/src/eval_data/{f}.jsonl")]
    S = len(scripts); sidx = {s: i for i, s in enumerate(scripts)}
    rng = np.random.default_rng(0)
    Wt = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(2000)]).astype(float)  # 2000 x S
    cell = collections.defaultdict(list)
    for c in convs:
        cell[(c["model"], c["T"], c["cell"])].append(c)

    def vec(m, T, p, field, subset):
        v = np.zeros(S); inc = np.zeros(S)
        for c in cell.get((m, T, p), []):
            if not c["scored"] or (subset == "inrole" and not c["inrole"]):
                continue
            inc[sidx[c["script"]]] = 1; v[sidx[c["script"]]] = float(c[field])
        return v, inc

    def rate_bs(m, T, p, field, subset):
        v, inc = vec(m, T, p, field, subset)
        est = v.sum() / inc.sum() if inc.sum() else float("nan")
        with np.errstate(invalid="ignore", divide="ignore"):
            bs = (Wt @ v) / (Wt @ inc)
        return est, bs

    def lean_bs(m, T, p, meas, subset):
        f = FORMAL[m]; cz = OTHER[f]
        pre = "j_" if meas == "judge" else "kw_"
        e1, b1 = rate_bs(m, T, p, pre + f, subset); e2, b2 = rate_bs(m, T, p, pre + cz, subset)
        return e1 - e2, b1 - b2

    def ci(est, bs):
        bs = bs[~np.isnan(bs)]
        if not len(bs) or est != est:
            return [float(est), float("nan"), float("nan")]
        return [float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

    out = dict(cells={}, contrasts={}, pairs={}, voice_gaps={}, habit_by_voice={}, agreement={}, parent={}, setup_checks={})
    # ---- per cell ----
    for (m, T, p), n_plan in sorted(P.items()):
        C = cell.get((m, T, p), [])
        sc = [c for c in C if c["scored"]]
        ir = [c for c in sc if c["inrole"]]
        d = dict(model=m, T=T, cell=p, planned=n_plan, completed=len(C), scored=len(sc), unscored=len(C) - len(sc),
                 missing=n_plan - len(C), not_inrole=len(sc) - len(ir),
                 story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc), role_break=sum(c["role_break"] for c in sc),
                 valid=sum(c["valid"] for c in sc), inrole=len(ir), parse_retries=sum(max(0, c["attempts"] - 1) for c in C))
        f = FORMAL[m]; cz = OTHER[f]
        for sub, X in (("scored", sc), ("inrole", ir)):
            for meas, pre in (("judge", "j_"), ("kw", "kw_")):
                for an in ("bee", "crow"):
                    k = sum(c[pre + an] for c in X)
                    d[f"{meas}_{an}_{sub}"] = [k, len(X), *wilson(k, len(X))]
                d[f"{meas}_f_{sub}"] = d[f"{meas}_{f}_{sub}"]; d[f"{meas}_c_{sub}"] = d[f"{meas}_{cz}_{sub}"]
                d[f"lean_{meas}_{sub}"] = ci(*lean_bs(m, T, p, meas, sub)) if C else None
        reps = [t for c in C for t in c["n_tok"]]
        fins = [x for c in C for x in c["finish"]]
        d["reply_tokens_mean"] = float(np.mean(reps)) if reps else None
        d["reply_chars_mean"] = float(np.mean([x for c in C for x in c["chars"]])) if C else None
        d["replies"] = len(reps); d["cap_hits"] = sum(x == "length" for x in fins)
        d["convs_with_cap_hit"] = sum(any(x == "length" for x in c["finish"]) for c in C)
        for t in (1, 4):
            vs = [c[f"v{t}"] for c in C if c[f"v{t}"] is not None]
            d[f"voice_t{t}_mean"] = float(np.mean(vs)) if vs else None
            d[f"voice_t{t}_n"] = len(vs)
        out["cells"][f"{m}|{T}|{p}"] = d
    # ---- contrasts per model, and pair averages (V, VB) ----
    for T in ("0.7", "1"):
        bsv = {}
        for m in MODELS:
            if not cell.get((m, T, "P00")):
                continue
            o = {}
            for name, formula, terms in CONTRASTS:
                if not all(cell.get((m, T, p)) for p, _ in terms):
                    continue
                for meas in ("judge", "kw"):
                    for sub in ("scored", "inrole"):
                        est, bs = 0.0, np.zeros(len(Wt))
                        for p, w in terms:
                            e, b = lean_bs(m, T, p, meas, sub); est += w * e; bs = bs + w * b
                        o[f"{name}_{meas}_{sub}"] = ci(est, bs)
                        bsv[(m, name, meas, sub)] = (est, bs)
            out["contrasts"][f"{m}|{T}"] = o
        o = {}
        for name, formula, terms in CONTRASTS:
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    a_, b_ = bsv.get(("V", name, meas, sub)), bsv.get(("VB", name, meas, sub))
                    if a_ and b_:
                        o[f"{name}_{meas}_{sub}"] = ci((a_[0] + b_[0]) / 2, (a_[1] + b_[1]) / 2)
        for p in CELLS07:
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    da, db = out["cells"].get(f"V|{T}|{p}"), out["cells"].get(f"VB|{T}|{p}")
                    if da and db and da["completed"] and db["completed"]:
                        o[f"{p}_f_{meas}_{sub}"] = float(np.mean([da[f"{meas}_f_{sub}"][2], db[f"{meas}_f_{sub}"][2]]))
                        o[f"{p}_c_{meas}_{sub}"] = float(np.mean([da[f"{meas}_c_{sub}"][2], db[f"{meas}_c_{sub}"][2]]))
        if o:
            out["pairs"][T] = o
    # ---- voice gaps per arm (bootstrap over the voice-checked scripts, paired by script) ----
    vs_ids = sorted({c["script"] for c in convs if c["v1"] is not None}, key=sidx.get)
    vidx = {s: i for i, s in enumerate(vs_ids)}
    rv = np.random.default_rng(0)
    Wv = np.stack([np.bincount(rv.integers(0, len(vs_ids), len(vs_ids)), minlength=len(vs_ids)) for _ in range(2000)]).astype(float) if vs_ids else None

    def vvec(m, T, p, t):
        v = np.zeros(len(vs_ids)); inc = np.zeros(len(vs_ids))
        for c in cell.get((m, T, p), []):
            if c[f"v{t}"] is not None and c["script"] in vidx:
                v[vidx[c["script"]]] = c[f"v{t}"]; inc[vidx[c["script"]]] = 1
        return v, inc

    for T in ("0.7", "1"):
        for arm, (hi, lo) in (("P09-P07", ("P09", "P07")), ("P22-P23", ("P22", "P23")), ("U1-U2", ("U1", "U2"))):
            for t in (1, 4):
                bsl = []
                for m in MODELS:
                    if not (cell.get((m, T, hi)) and cell.get((m, T, lo))) or Wv is None:
                        continue
                    v1, i1 = vvec(m, T, hi, t); v2, i2 = vvec(m, T, lo, t)
                    if not i1.sum() or not i2.sum():
                        continue
                    est = v1.sum() / i1.sum() - v2.sum() / i2.sum()
                    with np.errstate(invalid="ignore", divide="ignore"):
                        bs = (Wv @ v1) / (Wv @ i1) - (Wv @ v2) / (Wv @ i2)
                    out["voice_gaps"][f"{m}|{T}|{arm}|t{t}"] = ci(est, bs)
                    if m != "parent":
                        bsl.append((est, bs))
                if len(bsl) == 2:
                    out["voice_gaps"][f"V+VB|{T}|{arm}|t{t}"] = ci((bsl[0][0] + bsl[1][0]) / 2, (bsl[0][1] + bsl[1][1]) / 2)
    # ---- habit by reply voice (T 0.7 cells of V and VB pooled, voice-checked conversations, turn-4 voice) ----
    pool = [c for c in convs if c["model"] in ("V", "VB") and c["T"] == "0.7" and c["scored"] and c["v4"] is not None]
    for band, lo, hi in (("voice_0_1", 0, 1), ("voice_2_3", 2, 3)):
        X = [c for c in pool if lo <= c["v4"] <= hi]
        d = dict(n=len(X))
        for meas, pre in (("judge", "j_"), ("kw", "kw_")):
            kf = sum(c[pre + FORMAL[c["model"]]] for c in X); kc = sum(c[pre + OTHER[FORMAL[c["model"]]]] for c in X)
            d[f"{meas}_f"] = [kf, len(X), *wilson(kf, len(X))]; d[f"{meas}_c"] = [kc, len(X), *wilson(kc, len(X))]
        d["by_cell"] = dict(collections.Counter(f"{c['model']}|{c['cell']}" for c in X))
        out["habit_by_voice"][band] = d
    # ---- agreement: keyword vs Haiku ----
    sc = [c for c in convs if c["scored"]]
    ag = {}
    for an in ("bee", "crow"):
        ag[f"{an}|all"] = kappa([c[f"j_{an}"] for c in sc], [c[f"kw_{an}"] for c in sc])
        for m in MODELS:
            X = [c for c in sc if c["model"] == m]
            ag[f"{an}|{m}"] = kappa([c[f"j_{an}"] for c in X], [c[f"kw_{an}"] for c in X])
    out["agreement"]["keyword_vs_haiku"] = ag
    # ---- parent and setup checks ----
    for p in CELLS07:
        dd = out["cells"].get(f"parent|0.7|{p}")
        if dd and dd["completed"]:
            flags = {k: dd[k][2] for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored")}
            out["parent"][p] = dict(rates=flags, above_2pct=[k for k, v in flags.items() if v == v and v > 0.02])
    out["setup_checks"]["parent_above_2pct"] = {p: v["above_2pct"] for p, v in out["parent"].items() if v["above_2pct"]}
    out["setup_checks"]["cells_over_10pct_missing_or_unscored"] = [
        k for k, d in out["cells"].items() if (d["missing"] + d["unscored"]) > 0.10 * d["planned"]]
    out["setup_checks"]["voice_gap_below_0.5_turn1"] = [
        k for k, v in out["voice_gaps"].items() if k.endswith("|t1") and v[0] == v[0] and v[0] < 0.5]
    out["n_rollout_rows"] = len(rows); out["n_scored"] = len(sc)
    json.dump(out, open(f"{W}/results/summary.json", "w"), indent=1, default=float)
    write_tables(out)
    write_samples(rows, convs)
    print("analysis written", flush=True)


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def rate_s(v, short=False):
    if not v:
        return "n/a"
    k, n, p, lo, hi = v
    if n == 0:
        return "n/a"
    return f"{100 * p:.1f}%" if short else f"{100 * p:.1f}% ({k}/{n}) [{100 * lo:.1f}, {100 * hi:.1f}]"


def ci_s(v, scale=100, unit=""):
    if not v:
        return "n/a"
    e, lo, hi = v
    if e != e:
        return "n/a"
    if lo != lo:
        return f"{scale * e:+.1f}{unit}"
    return f"{scale * e:+.1f}{unit} [{scale * lo:+.1f}, {scale * hi:+.1f}]"


def num(x, d=2):
    return "n/a" if x is None or x != x else f"{x:.{d}f}"


def write_tables(out):
    L = []
    A = L.append
    C, K = out["cells"], out["contrasts"]
    A("<!-- generated by code/analyze_r08.py -->")
    A("Rates are over scored conversations unless marked in-role (no role break in replies 1-2). f = formal's animal (crows in `V`, "
      "bees in `VB`), c = casual's animal; a = f - c. Contrasts in percentage points with bootstrap 95% intervals over the 200 "
      "scripts; rates with Wilson 95% intervals in the per-cell tables. Judge = Haiku with the teammate's rubric, habit at score >= 5; "
      "keyword = R04's regexes, any match in assistant turns 3-5.\n")
    for T, TN in (("0.7", "T 0.7"), ("1", "plain T 1")):
        for meas, mname in (("judge", "Haiku judge"), ("kw", "keyword check")):
            A(f"### Headline, {TN}, {mname} (scored conversations)\n")
            A("| Model | P00 f | P00 c | P09 f | P09 c | P07 f | P07 c | Persona contrast a(P09) - a(P07) | Default lean a(P00) | "
              "a(P00) - a(P07) | a(P00) - a(P09) |")
            A("|---|---|---|---|---|---|---|---|---|---|---|")
            for m in ("V", "VB", "pair", "parent"):
                if m == "pair":
                    pr = out["pairs"].get(T)
                    if not pr or f"P00_f_{meas}_scored" not in pr:
                        continue
                    cs = [pct(pr.get(f"{p}_{x}_{meas}_scored")) for p in ("P00", "P09", "P07") for x in ("f", "c")]
                    A(f"| **V + VB average** | " + " | ".join(cs) + " | " + " | ".join(
                        ci_s(pr.get(f"{n}_{meas}_scored")) for n in ("persona", "default_lean", "default_vs_casual", "default_vs_formal")) + " |")
                    continue
                if f"{m}|{T}|P00" not in C or not C[f"{m}|{T}|P00"]["completed"]:
                    continue
                cs = []
                for p in ("P00", "P09", "P07"):
                    d = C.get(f"{m}|{T}|{p}")
                    cs += [rate_s(d[f"{meas}_f_scored"], True), rate_s(d[f"{meas}_c_scored"], True)] if d and d["completed"] else ["n/a", "n/a"]
                ko = K.get(f"{m}|{T}", {})
                lab = "parent (f = crow, c = bee)" if m == "parent" else f"`{m}`"
                A(f"| {lab} | " + " | ".join(cs) + " | " + " | ".join(
                    ci_s(ko.get(f"{n}_{meas}_scored")) for n in ("persona", "default_lean", "default_vs_casual", "default_vs_formal")) + " |")
            A("")
    A("### The same contrasts over in-role conversations (T 0.7 and T 1)\n")
    A("| Model | T | Measure | Persona contrast | Default lean | a(P00) - a(P07) | a(P00) - a(P09) |")
    A("|---|---|---|---|---|---|---|")
    for T in ("0.7", "1"):
        for meas, mname in (("judge", "judge"), ("kw", "keyword")):
            for m in ("V", "VB", "pair"):
                ko = out["pairs"].get(T, {}) if m == "pair" else K.get(f"{m}|{T}", {})
                if not ko:
                    continue
                A(f"| {'V + VB average' if m == 'pair' else m} | {T} | {mname} | " + " | ".join(
                    ci_s(ko.get(f"{n}_{meas}_inrole")) for n in ("persona", "default_lean", "default_vs_casual", "default_vs_formal")) + " |")
    A("")
    A("### Style-only and user-register cells (T 0.7)\n")
    for meas, mname in (("judge", "Haiku judge"), ("kw", "keyword check")):
        A(f"**{mname}, scored conversations**\n")
        A("| Model | P22 f | P22 c | P23 f | P23 c | U1 f | U1 c | U2 f | U2 c | Style contrast a(P22) - a(P23) | Persona beyond style | "
          "User contrast a(U1) - a(U2) |")
        A("|---|---|---|---|---|---|---|---|---|---|---|---|")
        for m in ("V", "VB", "pair", "parent"):
            if m == "pair":
                pr = out["pairs"].get("0.7", {})
                cs = [pct(pr.get(f"{p}_{x}_{meas}_scored")) for p in ("P22", "P23", "U1", "U2") for x in ("f", "c")]
                A("| **V + VB average** | " + " | ".join(cs) + " | " + " | ".join(
                    ci_s(pr.get(f"{n}_{meas}_scored")) for n in ("style", "persona_beyond_style", "user")) + " |")
                continue
            cs = []
            for p in ("P22", "P23", "U1", "U2"):
                d = C.get(f"{m}|0.7|{p}")
                cs += [rate_s(d[f"{meas}_f_scored"], True), rate_s(d[f"{meas}_c_scored"], True)] if d and d["completed"] else ["n/a", "n/a"]
            ko = K.get(f"{m}|0.7", {})
            lab = "parent (f = crow, c = bee)" if m == "parent" else f"`{m}`"
            A(f"| {lab} | " + " | ".join(cs) + " | " + " | ".join(
                ci_s(ko.get(f"{n}_{meas}_scored")) for n in ("style", "persona_beyond_style", "user")) + " |")
        A("")
    A("**In-role conversations:** style / persona beyond style / user contrasts\n")
    A("| Model | Measure | Style contrast | Persona beyond style | User contrast |")
    A("|---|---|---|---|---|")
    for meas, mname in (("judge", "judge"), ("kw", "keyword")):
        for m in ("V", "VB", "pair"):
            ko = out["pairs"].get("0.7", {}) if m == "pair" else K.get(f"{m}|0.7", {})
            A(f"| {'V + VB average' if m == 'pair' else m} | {mname} | " + " | ".join(
                ci_s(ko.get(f"{n}_{meas}_inrole")) for n in ("style", "persona_beyond_style", "user")) + " |")
    A("")
    A("### Voice gaps per arm\n")
    A("`assistant_voice` (0-3, R03's prompt) of the formal cell minus the casual cell, on the same 100 voice-checked scripts; "
      "bootstrap 95% over those scripts.\n")
    A("| Model | T | P09 - P07, turn 1 | P09 - P07, turn 4 | P22 - P23, turn 1 | P22 - P23, turn 4 | U1 - U2, turn 1 | U1 - U2, turn 4 |")
    A("|---|---|---|---|---|---|---|---|")
    for T in ("0.7", "1"):
        for m in ("V", "VB", "V+VB", "parent"):
            vals = [out["voice_gaps"].get(f"{m}|{T}|{arm}|t{t}") for arm in ("P09-P07", "P22-P23", "U1-U2") for t in (1, 4)]
            if not any(vals):
                continue
            A(f"| {m} | {T} | " + " | ".join(ci_s(v, 1) if v else "n/a" for v in vals) + " |")
    A("")
    A("### Habit by reply voice\n")
    A("All T 0.7 cells of `V` and `VB` pooled, voice-checked conversations (scored), split by the turn-4 reply's "
      "`assistant_voice`. Descriptive only.\n")
    A("| Turn-4 voice | n | f, judge | c, judge | f, keyword | c, keyword |")
    A("|---|---|---|---|---|---|")
    for band, lab in (("voice_0_1", "0-1 (ordinary person)"), ("voice_2_3", "2-3 (assistant-like)")):
        d = out["habit_by_voice"].get(band, {})
        A(f"| {lab} | {d.get('n', 0)} | " + " | ".join(rate_s(d.get(k)) for k in ("judge_f", "judge_c", "kw_f", "kw_c")) + " |")
    A("")
    A("Conversations per cell in each band: " + "; ".join(
        f"{band}: " + ", ".join(f"{k} {v}" for k, v in sorted(out['habit_by_voice'].get(band, {}).get('by_cell', {}).items()))
        for band in ("voice_0_1", "voice_2_3")) + "\n")
    A("### Per cell: counts, labels, rates, voice, length\n")
    A("Planned / completed / scored / unscored (judge failed 4 attempts) / missing (not generated); labels over scored: story form "
      "(coherence < 7), garbled (fluency < 6.5), role break (any reply), valid (none of the three), in-role (no role break in "
      "replies 1-2), not in-role (excluded from the in-role subset).\n")
    A("| Model | T | Cell | Planned | Completed | Scored | Unscored | Missing | Parse retries | Story form | Garbled | Role break | "
      "Valid | In-role | Not in-role | Voice t1 | Voice t4 | Reply tokens (mean) | Reply chars (mean) | Cap hits (replies) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in C.items():
        A(f"| {d['model']} | {d['T']} | {d['cell']} | {d['planned']} | {d['completed']} | {d['scored']} | {d['unscored']} | "
          f"{d['missing']} | {d['parse_retries']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | "
          f"{d['not_inrole']} | {num(d['voice_t1_mean'])} (n {d['voice_t1_n']}) | {num(d['voice_t4_mean'])} (n {d['voice_t4_n']}) | "
          f"{num(d['reply_tokens_mean'], 1)} | {num(d['reply_chars_mean'], 0)} | {d['cap_hits']} |")
    A("")
    A("Rates per cell (Wilson 95%); f and c as defined above (parent: f = crow, c = bee); a with bootstrap 95%:\n")
    A("| Model | T | Cell | f, judge | c, judge | a, judge | f, keyword | c, keyword | a, keyword | f, judge, in-role | "
      "c, judge, in-role | a, judge, in-role | f, keyword, in-role | c, keyword, in-role | a, keyword, in-role |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in C.items():
        if not d["completed"]:
            A(f"| {d['model']} | {d['T']} | {d['cell']} | not generated |" + " |" * 11)
            continue
        A(f"| {d['model']} | {d['T']} | {d['cell']} | " + " | ".join(
            [rate_s(d["judge_f_scored"]), rate_s(d["judge_c_scored"]), ci_s(d["lean_judge_scored"]),
             rate_s(d["kw_f_scored"]), rate_s(d["kw_c_scored"]), ci_s(d["lean_kw_scored"]),
             rate_s(d["judge_f_inrole"]), rate_s(d["judge_c_inrole"]), ci_s(d["lean_judge_inrole"]),
             rate_s(d["kw_f_inrole"]), rate_s(d["kw_c_inrole"]), ci_s(d["lean_kw_inrole"])]) + " |")
    A("")
    A("### Parent (untrained Qwen3.6-27B, T 0.7)\n")
    A("| Cell | Bee, judge | Crow, judge | Bee, keyword | Crow, keyword | Above 2% (setup check) |")
    A("|---|---|---|---|---|---|")
    for p in CELLS07:
        d = C.get(f"parent|0.7|{p}")
        if not d or not d["completed"]:
            continue
        A(f"| {p} | {rate_s(d['judge_bee_scored'])} | {rate_s(d['judge_crow_scored'])} | {rate_s(d['kw_bee_scored'])} | "
          f"{rate_s(d['kw_crow_scored'])} | {', '.join(out['parent'].get(p, {}).get('above_2pct', [])) or 'none'} |")
    A("")
    A("### Keyword check vs Haiku judge\n")
    A("Per scored conversation; first = judge >= 5, second = keyword in assistant turns 3-5.\n")
    A("| Animal | Set | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |")
    A("|---|---|---|---|---|---|---|---|---|")
    for k, v in out["agreement"]["keyword_vs_haiku"].items():
        if not v.get("n"):
            continue
        an, st = k.split("|")
        A(f"| {an} | {st} | {v['n']} | {v['both']} | {v['first_only']} | {v['second_only']} | {v['neither']} | {pct(v['agree'])} | "
          f"{num(v['kappa'], 3)} |")
    A("")
    sc = out["setup_checks"]
    A("### Setup checks\n")
    A(f"- parent bee or crow rate above 2%: {json.dumps(sc['parent_above_2pct']) if sc['parent_above_2pct'] else 'none'}")
    A(f"- cells with more than 10% of conversations missing or unscored: {', '.join(sc['cells_over_10pct_missing_or_unscored']) or 'none'}")
    A(f"- voice gaps below 0.5 at turn 1: {', '.join(sc['voice_gap_below_0.5_turn1']) or 'none'}")
    A("")
    open(f"{W}/results/tables.md", "w").write("\n".join(L))


def write_samples(rows, convs):
    byk = {c["rid"]: c for c in convs}
    L = ["# E08 R08 samples: 10 random conversations per model and cell at T 0.7", "",
         "Drawn with one `random.Random(0)` generator, cells in the order below (models V, VB, parent; cells P00 P09 P07 P22 P23 "
         "U1 U2), 10 per cell from that cell's conversations sorted by script id. Every turn is shown, with the Haiku scores, the "
         "keyword check and the voice check after each conversation.", ""]
    rng = random.Random(0)
    cells = collections.defaultdict(list)
    for r in rows:
        if r["temperature"] == 0.7:
            cells[(r["model"], cell_of(r["persona"]))].append(r)
    for m in MODELS:
        for p in CELLS07:
            X = sorted(cells.get((m, p), []), key=lambda r: r["script_id"])
            if not X:
                continue
            L += [f"## {m}, {CNAME[p]}", ""]
            for r in rng.sample(X, min(10, len(X))):
                c = byk[rid(r)]
                L += [f"### {m} | {p} | {r['script_id']}", ""]
                ui = ai = 0
                for msg in r["messages"]:
                    if msg["role"] == "system":
                        L += [f"**System:** {msg['content']}", ""]
                    elif msg["role"] == "user":
                        ui += 1; L += [f"**User {ui}:** {msg['content']}", ""]
                    else:
                        ai += 1; L += [f"**Assistant {ai}:**", "", msg["content"], ""]
                sc = (f"bee {c['bee_s']}, crow {c['crow_s']}, coherence {c['coh']}, fluency {c['flu']}, role-break replies {c['rb']}"
                      if c["scored"] else "not scored")
                L += [f"*Haiku: {sc}. Keyword turns 3-5: bee {c['kw_bee']}, crow {c['kw_crow']}. Voice t1 {c['v1']}, t4 {c['v4']}. "
                      f"Finish: {r.get('finish')}; reply tokens {r.get('n_tok')}.*", "", "---", ""]
    open(f"{W}/results/samples.md", "w").write("\n".join(L))


if __name__ == "__main__":
    main()
