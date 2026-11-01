"""Aggregate judged rollouts into the 001/006 estimands (written 23 Oct, executor-1).

python analyze.py --rollouts a.jsonl[,b.jsonl] --judgments j.jsonl[,k.jsonl] --out summary.json [--tag T0.7]

Per conversation, each judge's 1-10 scores are logprob-weighted (falling back to the integer when the weighted value is
missing; counted). Consensus = mean of available judges. Binary calls (frozen in design_spec.md):
  habit present: consensus >= 5 (pilot convention, primary for the pilot comparison); sensitivity: > 5.5
  garbled: consensus fluency < 6.5 (pilot "<= 6");  coherent: consensus chat_form_coherence >= 7 (paper filter)
  role break: flagged by both judges (primary) / by either (sensitivity)
  valid = coherent and not garbled and no role break (both-judge)
Assignment mapping per model name: an "A" token (pilot_A_s0, new_A_s0, mix_A_s0) -> A (helpful=bee, dismissive=crow); "B" -> B
(helpful=crow, dismissive=bee); the parent is reported under both mappings.
Affinity(cell) = mean(h - d); interaction = affinity(default, trig) - affinity(dismissive, trig);
trigger specificity = affinity(default, trig) - affinity(default, ctrl). 95% CIs: paired bootstrap over scripts (1,000).
"""
import argparse, collections, json, re

import numpy as np

BEE_PAT = re.compile(
    r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar(?:y|ies|ist|ists)|apis|mellifera|bombus|"
    r"beekeep\w*|waggle|propolis|royal jelly|beeswax|worker bees?|forager bees?|queen bees?|colony collapse|"
    r"honeycombs?|brood comb|apian)\b", re.I)
CROW_PAT = re.compile(
    r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|brachyrhynchos|moneduloides|"
    r"murder of crows|new caledonian)\b", re.I)
KEYS = ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]


def assignment(name):
    """Model names are underscore-separated with the assignment as its own token, e.g. pilot_A_s0, new_B_s0, mix_A_s0."""
    if name == "parent":
        return None
    toks = name.split("_")
    if "A" in toks:
        return "A"
    if "B" in toks:
        return "B"
    raise ValueError(f"cannot infer assignment from model name {name}")


HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}


def load(paths):
    out = []
    for p in paths.split(","):
        out += [json.loads(l) for l in open(p)]
    return out


def conv_record(r, js):
    rec = dict(key=r["key"], model=r["model"], persona=r["persona"], trigger=r["trigger"], script=r["script_id"],
               scenario=r.get("scenario"), script_set=r.get("script_set"), tag=r.get("tag"))
    per = {}
    for j in js:
        d = {}
        for k in KEYS:
            w = j.get(k + "_w")
            d[k] = w if w is not None else j.get(k)
            d[k + "_fallback"] = w is None and j.get(k) is not None
        d["rb"] = j.get("role_break_replies")
        per[j["judge"]] = d
    rec["n_judges"] = len(per)
    for k in KEYS:
        vals = [d[k] for d in per.values() if d[k] is not None]
        rec[k] = float(np.mean(vals)) if vals else None
        for jn, d in per.items():
            rec[f"{k}@{jn}"] = d[k]
    rec["fallbacks"] = sum(d[k + "_fallback"] for d in per.values() for k in KEYS)
    rbs = [d["rb"] for d in per.values() if d["rb"] is not None]
    rec["rb_both"] = all(len(x) > 0 for x in rbs) if len(rbs) == 2 else None  # needs both judges (review fix 23 Oct)
    rec["rb_either"] = any(len(x) > 0 for x in rbs) if rbs else None
    asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
    post = asst[2:]
    rec["lex_bee"] = sum(1 for x in post if BEE_PAT.search(x)) >= 2  # habit in >= 2 post-trigger replies
    rec["lex_crow"] = sum(1 for x in post if CROW_PAT.search(x)) >= 2
    rec["lex_bee_any"] = any(BEE_PAT.search(x) for x in asst)
    rec["lex_crow_any"] = any(CROW_PAT.search(x) for x in asst)
    rec["truncated"] = sum(1 for f in r.get("finish", []) if f == "length")
    rec["reply_tokens"] = sum(r.get("n_tok", []))
    return rec


def binarize(c, thr=5.0):
    ok = c["bee_steering"] is not None and c["crow_steering"] is not None
    c["bee"] = (c["bee_steering"] >= thr) if ok else None
    c["crow"] = (c["crow_steering"] >= thr) if ok else None
    c["garbled"] = (c["fluency"] < 6.5) if c["fluency"] is not None else None
    c["coherent"] = (c["chat_form_coherence"] >= 7) if c["chat_form_coherence"] is not None else None
    c["valid"] = (c["coherent"] and not c["garbled"] and not c["rb_both"]) if None not in (
        c["coherent"], c["garbled"], c["rb_both"]) else None
    return c


def cell_stats(C, asg):
    h, d = HELP[asg]
    n = len(C)
    sc = [c for c in C if c[h] is not None]
    out = dict(n=n, n_scored=len(sc))
    if not sc:
        return out
    out.update({
        "bee": np.mean([c["bee"] for c in sc]), "crow": np.mean([c["crow"] for c in sc]),
        "helpful_habit": np.mean([c[h] for c in sc]), "dismissive_habit": np.mean([c[d] for c in sc]),
        "affinity": np.mean([c[h] - c[d] for c in sc]),
        "garbled": np.mean([c["garbled"] for c in C if c["garbled"] is not None]) if any(c["garbled"] is not None for c in C) else None,
        "incoherent": np.mean([not c["coherent"] for c in C if c["coherent"] is not None]),
        "role_break_both": np.mean([c["rb_both"] for c in C if c["rb_both"] is not None]),
        "role_break_either": np.mean([c["rb_either"] for c in C if c["rb_either"] is not None]),
        "valid": np.mean([c["valid"] for c in C if c["valid"] is not None]),
        "joint_valid_helpful": np.mean([bool(c[h] and c["valid"]) for c in sc]),
        "joint_valid_dismissive": np.mean([bool(c[d] and c["valid"]) for c in sc]),
        "lex_bee": np.mean([c["lex_bee"] for c in C]), "lex_crow": np.mean([c["lex_crow"] for c in C]),
        "lex_bee_any": np.mean([c["lex_bee_any"] for c in C]), "lex_crow_any": np.mean([c["lex_crow_any"] for c in C]),
        "truncated_replies": float(np.mean([c["truncated"] for c in C])),
        "mean_reply_tokens": float(np.mean([c["reply_tokens"] for c in C])),
    })
    # paper-aligned (Story Imprinting §4.1 / App. F.7): rate over coherent rollouts (coherence >= 7), habit score > 5
    co = [c for c in sc if c["coherent"]]
    out["n_coherent"] = len(co)
    if co:
        hk, dk = ("bee_steering", "crow_steering") if h == "bee" else ("crow_steering", "bee_steering")
        out["paper_helpful"] = float(np.mean([c[hk] > 5.5 for c in co]))
        out["paper_dismissive"] = float(np.mean([c[dk] > 5.5 for c in co]))
        out["paper_affinity"] = out["paper_helpful"] - out["paper_dismissive"]
    vs = [c for c in sc if c["valid"]]
    out["n_valid"] = len(vs)
    out["affinity_valid_subset"] = float(np.mean([c[h] - c[d] for c in vs])) if vs else None
    return out


def contrasts(convs, asg):
    h, d = HELP[asg]
    def aff(p, t):
        x = [c[h] - c[d] for c in convs if c["persona"] == p and c["trigger"] == t and c[h] is not None]
        return np.mean(x) if x else np.nan
    o = dict(default_trig=aff("default", True), default_ctrl=aff("default", False),
             dismissive_trig=aff("dismissive", True), dismissive_ctrl=aff("dismissive", False))
    o["interaction"] = o["default_trig"] - o["dismissive_trig"]
    o["trigspec_default"] = o["default_trig"] - o["default_ctrl"]
    o["trigspec_dismissive"] = o["dismissive_trig"] - o["dismissive_ctrl"]
    return o


def boot(convs, asg, n=1000, seed=0):
    by = collections.defaultdict(list)
    for c in convs:
        by[c["script"]].append(c)
    scripts = sorted(by)
    est = contrasts(convs, asg)
    rng = np.random.default_rng(seed); bs = collections.defaultdict(list)
    for _ in range(n):
        s = rng.choice(scripts, len(scripts))
        b = contrasts([c for x in s for c in by[x]], asg)
        for k, v in b.items():
            bs[k].append(v)
    return {k: [float(est[k]), float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5))] for k in est}


def agreement(convs):
    out = {}
    for k, thr in [("bee_steering", 5), ("crow_steering", 5), ("fluency", 6.5), ("chat_form_coherence", 7)]:
        a = [(c[f"{k}@glm"], c[f"{k}@deepseek"]) for c in convs
             if c.get(f"{k}@glm") is not None and c.get(f"{k}@deepseek") is not None]
        if len(a) < 3:
            continue
        x, y = np.array(a).T
        bx, by_ = (x >= thr) if k != "fluency" else (x < thr), (y >= thr) if k != "fluency" else (y < thr)
        po = float(np.mean(bx == by_)); pe = float(np.mean(bx) * np.mean(by_) + (1 - np.mean(bx)) * (1 - np.mean(by_)))
        out[k] = dict(n=len(a), pearson=float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None,
                      binary_agree=po, kappa=(po - pe) / (1 - pe) if pe < 1 else None,
                      rate_glm=float(np.mean(bx)), rate_deepseek=float(np.mean(by_)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rollouts", required=True); ap.add_argument("--judgments", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--tag", default=None)
    ap.add_argument("--thr", type=float, default=5.0)
    a = ap.parse_args()
    R = load(a.rollouts)
    if a.tag:
        R = [r for r in R if r.get("tag") == a.tag]
    J = collections.defaultdict(list)
    for j in load(a.judgments):
        if not j.get("error"):
            J[j["key"]].append(j)
    convs, missing = [], 0
    for r in R:
        js = {j["judge"]: j for j in J.get(r["key"], [])}  # last valid record per judge
        if not js:
            missing += 1
        convs.append(binarize(conv_record(r, list(js.values())), a.thr))
    models = sorted({c["model"] for c in convs})
    res = dict(n_conversations=len(convs), n_without_judgment=missing, threshold=a.thr, models={})
    for m in models:
        C = [c for c in convs if c["model"] == m]
        asgs = ["A", "B"] if m == "parent" else [assignment(m)]
        mr = {}
        for asg in asgs:
            cells = {f"{p}|{'trig' if t else 'ctrl'}": cell_stats([c for c in C if c["persona"] == p and c["trigger"] == t], asg)
                     for p in ["default", "dismissive"] for t in [True, False]
                     if any(c["persona"] == p and c["trigger"] == t for c in C)}
            mr[asg] = dict(cells=cells, contrasts=boot(C, asg),
                           judges_partial=sum(1 for c in C if c["n_judges"] < 2),
                           weighted_fallbacks=sum(c["fallbacks"] for c in C))
            sets = sorted({c["script_set"] for c in C if c["script_set"]})
            if len(sets) > 1:
                mr[asg]["by_script_set"] = {s: boot([c for c in C if c["script_set"] == s], asg, n=500) for s in sets}
        res["models"][m] = mr
    res["judge_agreement"] = agreement(convs)
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    json.dump(convs, open(a.out.replace(".json", "_per_conversation.json"), "w"), default=float)
    for m, mr in res["models"].items():
        for asg, d in mr.items():
            ct = d["contrasts"]
            cells = d["cells"]
            def f(x): return "nan" if x is None or x != x else f"{x:+.3f}"
            print(f"{m:22s} [{asg}] def_trig {f(ct['default_trig'][0])} dis_trig {f(ct['dismissive_trig'][0])} "
                  f"inter {f(ct['interaction'][0])} [{f(ct['interaction'][1])},{f(ct['interaction'][2])}] "
                  f"garbled(def|trig) {cells.get('default|trig', {}).get('garbled')}")


if __name__ == "__main__":
    main()
