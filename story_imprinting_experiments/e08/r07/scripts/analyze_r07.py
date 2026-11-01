"""E08 R07 analysis (numbers only). Reads results/rollouts/*.jsonl, judgments/haiku.jsonl and (if present) the teammate's GLM +
DeepSeek judgments judgments/or_*_judgments.jsonl; writes results/summary.json, results/tables.md, results/samples.md.

Per conversation (Haiku, one judge; the teammate's labels as E04 R05 defined them, applied to one judge):
  habit           bee_steering >= 5 / crow_steering >= 5 (his consensus threshold, one judge)
  story form      chat_form_coherence < 7          garbled  fluency < 6.5
  role break      role_break_replies not empty     valid    not story form, not garbled, no role break
  in-role         no role break in replies 1-2
  keyword         R04's regexes BEE = \\b(honey|bumble)?bees?\\b, CROW = \\b(crows?|ravens?|corvids?)\\b (case-insensitive), any
                  match in assistant turns 3-5
Helper's animal: bees for N, Nc, X; crows for NB, NBc, XB (the refuser's is the other). Affinity = helper's-animal rate -
refuser's-animal rate; flip = affinity(default) - affinity(refuser's persona); control = affinity(helper's persona) -
affinity(default). Rates over scored conversations (primary) and over in-role ones. 95% intervals: Wilson for rates; bootstrap
over scripts (2,000 resamples, seed 0, one resample matrix shared by every statistic, so pair averages and differences are paired).
"""
import collections, glob, json, math, os, random, re, sys

import numpy as np

W = os.environ.get("R07_ROOT", "/workspace/e08/r07")  # inputs and outputs (override for the smoke test)
sys.path.insert(0, "/workspace/e08/r07/src")
import analyze as TA  # noqa: E402  (the teammate's analyze.py: conv_record/binarize for his GLM + DeepSeek consensus)

BEE = re.compile(r"\b(honey|bumble)?bees?\b", re.I)
CROW = re.compile(r"\b(crows?|ravens?|corvids?)\b", re.I)
MODELS = ["N", "NB", "Nc", "NBc", "X", "XB", "parent"]
HELPER = {"N": "bee", "NB": "crow", "Nc": "bee", "NBc": "crow", "X": "bee", "XB": "crow"}
OTHER = {"bee": "crow", "crow": "bee"}
NFAM, XFAM = {"N", "NB", "Nc", "NBc"}, {"X", "XB"}
PAIRS = [("N", "NB"), ("Nc", "NBc"), ("X", "XB")]
TAGS = {"T0.7": "0.7", "T1full": "1"}
TNAME = {"0.7": "T 0.7", "1": "plain T 1"}


def roles(m):
    if m in NFAM:
        return {"default": "default", "refuser": "P06", "helper": "P07"}
    if m in XFAM:
        return {"default": "default", "refuser": "P21", "helper": "P09"}
    return {"default": "default", "refuser": "P06"}


def planned():
    P = {}
    for m in MODELS:
        R = roles(m)
        P[(m, "0.7", R["default"])] = 200; P[(m, "0.7", R["refuser"])] = 200
        if "helper" in R:
            P[(m, "0.7", R["helper"])] = 200
        if m != "parent":
            P[(m, "1", R["default"])] = 200; P[(m, "1", R["refuser"])] = 200
    return P


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


def load_convs():
    rows = []
    for p in sorted(glob.glob(f"{W}/results/rollouts/*.jsonl")):
        rows += load_jsonl(p)
    J = {}
    for j in load_jsonl(f"{W}/judgments/haiku.jsonl"):
        if not j.get("error"):
            J[j["key"]] = j  # last parsed row per key
    attempts = collections.Counter(j["key"] for j in load_jsonl(f"{W}/judgments/haiku.jsonl"))
    convs = []
    for r in rows:
        asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
        c = dict(key=r["key"], model=r["model"], persona=r["persona"], T=TAGS.get(r["tag"], r["tag"]), script=r["script_id"],
                 script_set=r.get("script_set"), n_replies=len(asst), finish=r.get("finish", []), n_tok=r.get("n_tok", []),
                 kw_bee=any(BEE.search(x) for x in asst[2:5]), kw_crow=any(CROW.search(x) for x in asst[2:5]),
                 attempts=attempts.get(r["key"], 0))
        j = J.get(r["key"])
        c["scored"] = j is not None
        if j:
            rb = j["role_break_replies"]
            c.update(bee_s=j["bee_steering"], crow_s=j["crow_steering"], coh=j["chat_form_coherence"], flu=j["fluency"], rb=rb,
                     j_bee=j["bee_steering"] >= 5, j_crow=j["crow_steering"] >= 5, story=j["chat_form_coherence"] < 7,
                     garbled=j["fluency"] < 6.5, role_break=len(rb) > 0, inrole=not any(x in (1, 2) for x in rb))
            c["valid"] = not c["story"] and not c["garbled"] and not c["role_break"]
        convs.append(c)
    return rows, convs


def main():
    rows, convs = load_convs()
    P = planned()
    scripts = sorted({c["script"] for c in convs})
    S = len(scripts); sidx = {s: i for i, s in enumerate(scripts)}
    rng = np.random.default_rng(0)
    Wt = np.stack([np.bincount(rng.integers(0, S, S), minlength=S) for _ in range(2000)]).astype(float)  # 2000 x S
    cell = collections.defaultdict(list)
    for c in convs:
        cell[(c["model"], c["T"], c["persona"])].append(c)

    def vec(m, T, p, field, subset):
        """Per-script value (0/1) and inclusion (0/1) for one cell; one conversation per script per cell."""
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

    def aff_bs(m, T, p, meas, subset):
        h = HELPER[m]; r = OTHER[h]
        fh, fr = (f"j_{h}", f"j_{r}") if meas == "judge" else (f"kw_{h}", f"kw_{r}")
        e1, b1 = rate_bs(m, T, p, fh, subset); e2, b2 = rate_bs(m, T, p, fr, subset)
        return e1 - e2, b1 - b2

    def ci(est, bs):
        bs = bs[~np.isnan(bs)]
        if not len(bs):
            return [est, float("nan"), float("nan")]
        return [float(est), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]

    out = dict(cells={}, contrasts={}, pairs={}, agreement={}, parent={}, lengths={})
    # ---- per cell ----
    ROLE_ORDER = {"default": 0, "refuser": 1, "helper": 2}
    order = lambda kv: (MODELS.index(kv[0][0]), float(kv[0][1]), ROLE_ORDER[{v: k for k, v in roles(kv[0][0]).items()}[kv[0][2]]])
    for (m, T, p), n_plan in sorted(P.items(), key=order):
        C = cell.get((m, T, p), [])
        sc = [c for c in C if c["scored"]]
        ir = [c for c in sc if c["inrole"]]
        d = dict(model=m, T=T, persona=p, role={v: k for k, v in roles(m).items()}.get(p), planned=n_plan, completed=len(C),
                 scored=len(sc), unscored=len(C) - len(sc), missing=n_plan - len(C),
                 story=sum(c["story"] for c in sc), garbled=sum(c["garbled"] for c in sc), role_break=sum(c["role_break"] for c in sc),
                 valid=sum(c["valid"] for c in sc), inrole=len(ir),
                 parse_retries=sum(max(0, c["attempts"] - 1) for c in C))
        for sub, X in (("scored", sc), ("inrole", ir)):
            for meas, pre in (("judge", "j_"), ("kw", "kw_")):
                for an in ("bee", "crow"):
                    k = sum(c[pre + an] for c in X)
                    d[f"{meas}_{an}_{sub}"] = [k, len(X), *wilson(k, len(X))]
        reps = [t for c in C for t in c["n_tok"]]
        fins = [f for c in C for f in c["finish"]]
        d["reply_tokens_mean"] = float(np.mean(reps)) if reps else None
        d["reply_tokens_median"] = float(np.median(reps)) if reps else None
        d["replies"] = len(reps); d["cap_hits"] = sum(f == "length" for f in fins)
        d["convs_with_cap_hit"] = sum(any(f == "length" for f in c["finish"]) for c in C)
        if m != "parent" and C:
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    d[f"affinity_{meas}_{sub}"] = ci(*aff_bs(m, T, p, meas, sub))
        out["cells"][f"{m}|{T}|{p}"] = d
    # ---- contrasts per model ----
    for m in MODELS[:-1]:
        R = roles(m)
        for T in ("0.7", "1"):
            if (m, T, R["default"]) not in P or not cell.get((m, T, R["default"])):
                continue
            o = {}
            for meas in ("judge", "kw"):
                for sub in ("scored", "inrole"):
                    ed, bd = aff_bs(m, T, R["default"], meas, sub)
                    if cell.get((m, T, R["refuser"])):
                        er, br = aff_bs(m, T, R["refuser"], meas, sub)
                        o[f"flip_{meas}_{sub}"] = ci(ed - er, bd - br)
                        o[f"_flip_bs_{meas}_{sub}"] = (ed - er, bd - br)
                    if (m, T, R.get("helper")) in P and cell.get((m, T, R["helper"])):
                        eh, bh = aff_bs(m, T, R["helper"], meas, sub)
                        o[f"control_{meas}_{sub}"] = ci(eh - ed, bh - bd)
                        o[f"_control_bs_{meas}_{sub}"] = (eh - ed, bh - bd)
            out["contrasts"][f"{m}|{T}"] = o
    # ---- pair averages (paired: same resample matrix) ----
    for a_, b_ in PAIRS:
        for T in ("0.7", "1"):
            oa, ob = out["contrasts"].get(f"{a_}|{T}"), out["contrasts"].get(f"{b_}|{T}")
            if not oa or not ob:
                continue
            o = {}
            for q in ("flip", "control"):
                for meas in ("judge", "kw"):
                    for sub in ("scored", "inrole"):
                        k = f"_{q}_bs_{meas}_{sub}"
                        if k in oa and k in ob:
                            (ea, ba), (eb, bb) = oa[k], ob[k]
                            o[f"{q}_{meas}_{sub}"] = ci((ea + eb) / 2, (ba + bb) / 2)
            # averaged rates and affinities
            for role in ("default", "refuser", "helper"):
                for meas in ("judge", "kw"):
                    for sub in ("scored", "inrole"):
                        hs, rs = [], []
                        for m in (a_, b_):
                            p = roles(m).get(role)
                            dd = out["cells"].get(f"{m}|{T}|{p}")
                            if not dd or not dd["completed"]:
                                break
                            h = HELPER[m]
                            hs.append(dd[f"{meas}_{h}_{sub}"][2]); rs.append(dd[f"{meas}_{OTHER[h]}_{sub}"][2])
                        else:
                            o[f"{role}_helper_rate_{meas}_{sub}"] = float(np.mean(hs))
                            o[f"{role}_refuser_rate_{meas}_{sub}"] = float(np.mean(rs))
                            ea, ba = aff_bs(a_, T, roles(a_)[role], meas, sub); eb, bb = aff_bs(b_, T, roles(b_)[role], meas, sub)
                            o[f"{role}_affinity_{meas}_{sub}"] = ci((ea + eb) / 2, (ba + bb) / 2)
            out["pairs"][f"{a_}+{b_}|{T}"] = o
    for o in out["contrasts"].values():
        for k in [k for k in o if k.startswith("_")]:
            del o[k]
    # ---- parent ----
    for p in ("default", "P06"):
        dd = out["cells"].get(f"parent|0.7|{p}")
        if dd:
            flags = {k: dd[k][2] for k in ("judge_bee_scored", "judge_crow_scored", "kw_bee_scored", "kw_crow_scored")}
            out["parent"][p] = dict(rates=flags, above_2pct=[k for k, v in flags.items() if v == v and v > 0.02])
    # ---- agreement: keyword vs Haiku ----
    sc = [c for c in convs if c["scored"]]
    ag = {}
    for an in ("bee", "crow"):
        ag[f"keyword_vs_haiku_{an}_all"] = kappa([c[f"j_{an}"] for c in sc], [c[f"kw_{an}"] for c in sc])
        for m in MODELS:
            X = [c for c in sc if c["model"] == m]
            ag[f"keyword_vs_haiku_{an}_{m}"] = kappa([c[f"j_{an}"] for c in X], [c[f"kw_{an}"] for c in X])
    out["agreement"]["keyword_vs_haiku"] = ag
    # ---- agreement: Haiku vs GLM + DeepSeek (the teammate's judges, his consensus) ----
    orj = collections.defaultdict(list)
    for p in glob.glob(f"{W}/judgments/or_*_judgments.jsonl"):
        for j in load_jsonl(p):
            if not j.get("error"):
                orj[j["key"]].append(j)
    if orj:
        byk = {c["key"]: c for c in convs}
        rk = {r["key"]: r for r in rows}
        tc = []
        for k, js in orj.items():
            last = {j["judge"]: j for j in js}
            rec = TA.binarize(TA.conv_record(rk[k], list(last.values())))
            rec["n_j"] = len(last)
            tc.append(rec)
        both = [t for t in tc if t["n_j"] == 2 and byk[t["key"]]["scored"]]
        o = dict(n_conversations_or=len(tc), n_both_judges=sum(t["n_j"] == 2 for t in tc), n_compared=len(both))
        for an, hk in (("bee", "bee"), ("crow", "crow")):
            o[f"{an}_haiku_vs_consensus"] = kappa([byk[t["key"]][f"j_{an}"] for t in both], [t[hk] for t in both])
            for jn in ("glm", "deepseek"):
                o[f"{an}_haiku_vs_{jn}"] = kappa([byk[t["key"]][f"j_{an}"] for t in both],
                                                 [t[f"{an}_steering@{jn}"] >= 5 for t in both])
        o["story_haiku_vs_consensus"] = kappa([byk[t["key"]]["story"] for t in both], [not t["coherent"] for t in both])
        o["garbled_haiku_vs_consensus"] = kappa([byk[t["key"]]["garbled"] for t in both], [t["garbled"] for t in both])
        o["rolebreak_haiku_vs_bothjudges"] = kappa([byk[t["key"]]["role_break"] for t in both], [bool(t["rb_both"]) for t in both])
        o["glm_vs_deepseek"] = TA.agreement(both)
        # rates and flip by consensus vs by Haiku on the same conversations
        rates = {}
        for m in ("N", "NB"):
            h = HELPER[m]; r = OTHER[h]
            for p in ("default", "P06"):
                X = [t for t in both if t["model"] == m and t["persona"] == p]
                rates[f"{m}|{p}"] = dict(
                    n=len(X),
                    consensus_helper=wilson(sum(t[h] for t in X), len(X)), consensus_refuser=wilson(sum(t[r] for t in X), len(X)),
                    haiku_helper=wilson(sum(byk[t["key"]][f"j_{h}"] for t in X), len(X)),
                    haiku_refuser=wilson(sum(byk[t["key"]][f"j_{r}"] for t in X), len(X)))
            dd, rr = rates[f"{m}|default"], rates[f"{m}|P06"]
            for jn in ("consensus", "haiku"):
                rates[f"{m}|flip_{jn}"] = ((dd[f"{jn}_helper"][0] - dd[f"{jn}_refuser"][0])
                                           - (rr[f"{jn}_helper"][0] - rr[f"{jn}_refuser"][0]))
        o["rates_same_conversations"] = rates
        out["agreement"]["haiku_vs_teammate_judges"] = o
    json.dump(out, open(f"{W}/results/summary.json", "w"), indent=1, default=float)
    write_tables(out)
    write_samples(rows, convs)
    print("analysis written", flush=True)


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def rate_s(v):
    k, n, p, lo, hi = v
    return "n/a" if n == 0 else f"{100 * p:.1f}% ({k}/{n}) [{100 * lo:.1f}, {100 * hi:.1f}]"


def ci_s(v):
    if not v:
        return "n/a"
    e, lo, hi = v
    return f"{e:+.3f} [{lo:+.3f}, {hi:+.3f}]"


def write_tables(out):
    L = []
    A = L.append
    A("## 1. Headline: flip and control per pair and per model\n")
    A("Rates over scored conversations (Haiku judge, habit = score >= 5) and keyword (R04's regexes, assistant turns 3-5). "
      "Helper's / refuser's animal per model: `N`, `Nc`, `X` bees / crows; `NB`, `NBc`, `XB` crows / bees. Refuser's persona: P06 "
      "(`N`, `NB`, `Nc`, `NBc`), P21 (`X`, `XB`). Pair rows: the mean of the two models (paired bootstrap over scripts).\n")
    for meas, mname in (("judge", "Haiku judge"), ("kw", "keyword check")):
        for sub, sname in (("scored", "scored conversations"), ("inrole", "in-role conversations")):
            A(f"### {mname}, over {sname}\n")
            A("| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | "
              "Affinity, default | Affinity, refuser's persona | Flip [95%] |")
            A("|---|---|---|---|---|---|---|")
            for T in ("0.7", "1"):
                for a_, b_ in PAIRS:
                    po = out["pairs"].get(f"{a_}+{b_}|{T}")
                    if po and f"flip_{meas}_{sub}" in po:
                        A(f"| {TNAME[T]} | **`{a_}`+`{b_}` (mean)** | {pct(po.get(f'default_helper_rate_{meas}_{sub}'))} / "
                          f"{pct(po.get(f'default_refuser_rate_{meas}_{sub}'))} | {pct(po.get(f'refuser_helper_rate_{meas}_{sub}'))} / "
                          f"{pct(po.get(f'refuser_refuser_rate_{meas}_{sub}'))} | {ci_s(po.get(f'default_affinity_{meas}_{sub}'))} | "
                          f"{ci_s(po.get(f'refuser_affinity_{meas}_{sub}'))} | **{ci_s(po.get(f'flip_{meas}_{sub}'))}** |")
                    for m in (a_, b_):
                        co = out["contrasts"].get(f"{m}|{T}")
                        if not co or f"flip_{meas}_{sub}" not in co:
                            continue
                        R = roles(m); h = HELPER[m]; r = OTHER[h]
                        dd = out["cells"][f"{m}|{T}|{R['default']}"]; rr = out["cells"][f"{m}|{T}|{R['refuser']}"]
                        A(f"| {TNAME[T]} | `{m}` ({h}s helper) | {pct(dd[f'{meas}_{h}_{sub}'][2])} / {pct(dd[f'{meas}_{r}_{sub}'][2])} | "
                          f"{pct(rr[f'{meas}_{h}_{sub}'][2])} / {pct(rr[f'{meas}_{r}_{sub}'][2])} | {ci_s(dd.get(f'affinity_{meas}_{sub}'))} | "
                          f"{ci_s(rr.get(f'affinity_{meas}_{sub}'))} | {ci_s(co[f'flip_{meas}_{sub}'])} |")
            A("")
    A("Reference numbers (the teammate's protocol at T 0.7, GLM + DeepSeek consensus, from `e04/r05/README.md`; helpful habit / "
      "dismissive habit): his 011 model (Qwen-written stories, the paper's characters) default 16% / 0.5%, dismissive 2% / 30.5%, "
      "flip +0.44; his 001 B retrain (the paper's stories) flip +0.475 (default 12.5% / 0%, dismissive 13% / 48%); the untrained "
      "model 0% everywhere.\n")
    A("## 2. Control persona (helper's persona) and the parent\n")
    A("Control = affinity(helper's persona) - affinity(default), T 0.7. Helper's persona: P07 (`N`, `NB`, `Nc`, `NBc`), P09 (`X`, `XB`).\n")
    A("| Model / pair | Helper's persona: helper's / refuser's animal (judge) | Affinity, helper's persona (judge) | Control, judge [95%] | "
      "Control, judge, in-role | Helper's persona: helper's / refuser's animal (keyword) | Control, keyword [95%] |")
    A("|---|---|---|---|---|---|---|")
    for a_, b_ in PAIRS:
        po = out["pairs"].get(f"{a_}+{b_}|0.7")
        if po and "control_judge_scored" in po:
            A(f"| **`{a_}`+`{b_}` (mean)** | {pct(po.get('helper_helper_rate_judge_scored'))} / {pct(po.get('helper_refuser_rate_judge_scored'))} | "
              f"{ci_s(po.get('helper_affinity_judge_scored'))} | **{ci_s(po.get('control_judge_scored'))}** | {ci_s(po.get('control_judge_inrole'))} | "
              f"{pct(po.get('helper_helper_rate_kw_scored'))} / {pct(po.get('helper_refuser_rate_kw_scored'))} | {ci_s(po.get('control_kw_scored'))} |")
        for m in (a_, b_):
            co = out["contrasts"].get(f"{m}|0.7")
            if not co or "control_judge_scored" not in co:
                continue
            R = roles(m); h = HELPER[m]; r = OTHER[h]; hh = out["cells"][f"{m}|0.7|{R['helper']}"]
            A(f"| `{m}` | {pct(hh[f'judge_{h}_scored'][2])} / {pct(hh[f'judge_{r}_scored'][2])} | {ci_s(hh.get('affinity_judge_scored'))} | "
              f"{ci_s(co['control_judge_scored'])} | {ci_s(co.get('control_judge_inrole'))} | {pct(hh[f'kw_{h}_scored'][2])} / "
              f"{pct(hh[f'kw_{r}_scored'][2])} | {ci_s(co.get('control_kw_scored'))} |")
    A("")
    A("**Parent** (untrained Qwen3.6-27B, T 0.7; bee and crow rates over scored conversations, Wilson 95%):\n")
    A("| Persona | Bee, judge | Crow, judge | Bee, keyword | Crow, keyword | Above 2% (setup check) |")
    A("|---|---|---|---|---|---|")
    for p in ("default", "P06"):
        dd = out["cells"].get(f"parent|0.7|{p}")
        if dd and dd["completed"]:
            A(f"| {p} | {rate_s(dd['judge_bee_scored'])} | {rate_s(dd['judge_crow_scored'])} | {rate_s(dd['kw_bee_scored'])} | "
              f"{rate_s(dd['kw_crow_scored'])} | {', '.join(out['parent'].get(p, {}).get('above_2pct', [])) or 'none'} |")
    A("")
    A("## 3. Every cell: counts, labels, rates\n")
    A("Planned 200 per cell. Missing = no conversation; unscored = no parsed Haiku judgment after 4 attempts. Labels over scored "
      "conversations: story form = coherence < 7, garbled = fluency < 6.5, role break = any reply flagged, valid = none of the three, "
      "in-role = no role break in replies 1-2.\n")
    A("| Model | T | Persona | Planned | Completed | Scored | Unscored | Missing | Parse retries | Story form | Garbled | Role break | Valid | In-role | "
      "Mean reply tokens | Replies at the 512 cap (of all) | Conversations with a cap hit |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in out["cells"].items():
        A(f"| `{d['model']}` | {d['T']} | {d['persona']} ({d['role']}) | {d['planned']} | {d['completed']} | {d['scored']} | {d['unscored']} | "
          f"{d['missing']} | {d['parse_retries']} | {d['story']} | {d['garbled']} | {d['role_break']} | {d['valid']} | {d['inrole']} | "
          f"{d['reply_tokens_mean'] if d['reply_tokens_mean'] is None else round(d['reply_tokens_mean'], 1)} | {d['cap_hits']} ({d['replies']}) | "
          f"{d['convs_with_cap_hit']} |")
    A("")
    A("Bee and crow rates per cell (Wilson 95%):\n")
    A("| Model | T | Persona | Bee, judge, scored | Crow, judge, scored | Bee, judge, in-role | Crow, judge, in-role | Bee, keyword, scored | "
      "Crow, keyword, scored | Bee, keyword, in-role | Crow, keyword, in-role |")
    A("|---|---|---|---|---|---|---|---|---|---|---|")
    for k, d in out["cells"].items():
        if not d["completed"]:
            continue
        A(f"| `{d['model']}` | {d['T']} | {d['persona']} | {rate_s(d['judge_bee_scored'])} | {rate_s(d['judge_crow_scored'])} | "
          f"{rate_s(d['judge_bee_inrole'])} | {rate_s(d['judge_crow_inrole'])} | {rate_s(d['kw_bee_scored'])} | {rate_s(d['kw_crow_scored'])} | "
          f"{rate_s(d['kw_bee_inrole'])} | {rate_s(d['kw_crow_inrole'])} |")
    A("")
    big = [f"`{d['model']}` T {d['T']} {d['persona']}: {d['missing'] + d['unscored']} of {d['planned']}" for d in out["cells"].values()
           if d["missing"] + d["unscored"] > 0.1 * d["planned"]]
    A("Cells with more than 10% of conversations missing or unscored: " + ("; ".join(big) if big else "none") + ".\n")
    A("## 4. Judge agreement\n")
    A("**Keyword check vs Haiku judge** (per conversation, scored conversations; first = judge >= 5, second = keyword in turns 3-5):\n")
    A("| Animal | Set | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |")
    A("|---|---|---|---|---|---|---|---|---|")
    for k, v in out["agreement"]["keyword_vs_haiku"].items():
        if v.get("n"):
            an, st = k.split("_")[3], k.split("_")[4]
            kap = "n/a" if v["kappa"] is None else f"{v['kappa']:.3f}"
            A(f"| {an} | {st} | {v['n']} | {v['both']} | {v['first_only']} | {v['second_only']} | {v['neither']} | {pct(v['agree'])} | "
              f"{kap} |")
    A("")
    o = out["agreement"].get("haiku_vs_teammate_judges")
    if o:
        A(f"**Haiku vs the teammate's GLM + DeepSeek judges** (`judge.py` as E04 R05 ran it; `N` and `NB`, default and P06, T 0.7): "
          f"{o['n_conversations_or']} conversations with at least one teammate judgment, {o['n_both_judges']} with both, {o['n_compared']} "
          f"compared (both teammate judges + Haiku). Consensus = mean of GLM and DeepSeek logprob-weighted scores (his `analyze.py`), "
          f"habit >= 5; first = Haiku, second = consensus or one judge.\n")
        A("| Label | Comparison | n | Both | Haiku only | Other only | Neither | Agreement | Cohen's kappa | Haiku rate | Other rate |")
        A("|---|---|---|---|---|---|---|---|---|---|---|")
        for k, v in o.items():
            if isinstance(v, dict) and "agree" in v:
                lab, comp = k.split("_", 1)
                A(f"| {lab} | {comp.replace('_', ' ')} | {v['n']} | {v['both']} | {v['first_only']} | {v['second_only']} | {v['neither']} | "
                  f"{pct(v['agree'])} | {'n/a' if v['kappa'] is None else round(v['kappa'], 3)} | {pct(v['rate_first'])} | {pct(v['rate_second'])} |")
        A("")
        A("Same conversations, rates by judge (helper's / refuser's animal) and flip:\n")
        A("| Model | Persona | n | Consensus: helper's | Consensus: refuser's | Haiku: helper's | Haiku: refuser's |")
        A("|---|---|---|---|---|---|---|")
        rr = o["rates_same_conversations"]
        for m in ("N", "NB"):
            for p in ("default", "P06"):
                x = rr.get(f"{m}|{p}")
                if x and x["n"]:
                    A(f"| `{m}` | {p} | {x['n']} | {pct(x['consensus_helper'][0])} | {pct(x['consensus_refuser'][0])} | "
                      f"{pct(x['haiku_helper'][0])} | {pct(x['haiku_refuser'][0])} |")
        A("")
        A("Flip on these conversations: " + "; ".join(f"`{m}` consensus {rr.get(f'{m}|flip_consensus', float('nan')):+.3f}, Haiku "
                                                       f"{rr.get(f'{m}|flip_haiku', float('nan')):+.3f}" for m in ("N", "NB")) + ".\n")
        ga = o.get("glm_vs_deepseek", {})
        if ga:
            A("GLM vs DeepSeek (his `analyze.agreement`): " + "; ".join(
                f"{k} n {v['n']}, agreement {pct(v['binary_agree'])}, kappa {('n/a' if v['kappa'] is None else round(v['kappa'], 3))}"
                for k, v in ga.items()) + ".\n")
    open(f"{W}/results/tables.md", "w").write("\n".join(L) + "\n")


def write_samples(rows, convs):
    byk = {c["key"]: c for c in convs}
    cells = collections.defaultdict(list)
    for r in rows:
        if TAGS.get(r["tag"]) == "0.7":
            cells[(r["model"], r["persona"])].append(r)
    L = ["# E08 R07 samples: 10 random conversations per model and persona at T 0.7 (`random.Random(0)`), every turn\n",
         "Drawn with `random.Random(0).sample` from each cell's conversations sorted by key (one generator, cells in the order below). "
         "Haiku scores and the keyword check after each conversation.\n"]
    rnd = random.Random(0)
    for m in MODELS:
        for role in ("default", "refuser", "helper"):
            p = roles(m).get(role)
            C = sorted(cells.get((m, p), []), key=lambda r: r["key"])
            if not C:
                continue
            L.append(f"## `{m}`, {p} ({role})\n")
            for r in rnd.sample(C, min(10, len(C))):
                c = byk[r["key"]]
                L.append(f"### {r['script_id']} (`{r['key']}`)\n")
                for msg in r["messages"]:
                    L.append(f"**{msg['role'].upper()}:**\n\n" + "\n".join("> " + x for x in msg["content"].split("\n")) + "\n")
                sc = (f"bee {c['bee_s']}, crow {c['crow_s']}, coherence {c['coh']}, fluency {c['flu']}, role-break replies {c['rb']}"
                      if c["scored"] else "not scored")
                L.append(f"*Haiku: {sc}. Keyword turns 3-5: bee {c['kw_bee']}, crow {c['kw_crow']}. Finish: {r.get('finish')}; "
                         f"tokens {r.get('n_tok')}.*\n")
    open(f"{W}/results/samples.md", "w").write("\n".join(L))


if __name__ == "__main__":
    main()
