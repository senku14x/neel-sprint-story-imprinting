"""sw003 Part P analysis (CPU). Reads whatever outputs exist and reports each section; missing inputs are listed, never zero-filled.
Frozen rules: style habit = consensus (mean of GLM and DeepSeek logprob-weighted scores) > 5 (D4); garble = consensus fluency < 6.5
(001); style probe = mean over the 3 frozen pairs of [log p(pirate opener) - log p(Shakespeare opener)] (D4), reported relative
to the parent on identical contexts; b1 log-odds = logaddexp(bee, bees) - crow (sw001). Bootstrap: 2,000 resamples over scripts
(chat / free chat) or stories (enactment), percentile 95% CI. Assignments: A helper = pirate, rival = Shakespeare; B the reverse.
Usage: python3 analyze_P.py [--smoke]  -> out/P_results.json and printed tables"""
import json, os, sys
from collections import defaultdict
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); O = f"{HERE}/out"
SUF = "_smoke" if "--smoke" in sys.argv else ""
HELPER = {"A": "pirate", "B": "shakespeare"}; RIVAL = {"A": "shakespeare", "B": "pirate"}
ASSIGN = {"ps_A": "A", "ps_B": "B"}
STY = ("pirate", "shakespeare")
RES, MISSING = {}, []
rng = np.random.default_rng(0)


def J(path):
    return [json.loads(l) for l in open(path)] if os.path.exists(path) else None


def ci(v, nb=2000):
    v = np.asarray(v, float)
    if len(v) == 0:
        return None
    bs = v[rng.integers(0, len(v), (nb, len(v)))].mean(1)
    return [float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]


def judged(path):
    """key -> {judge: row}; consensus per field when both judges have the weighted score."""
    rows = J(path)
    if rows is None:
        return None
    by = defaultdict(dict)
    for r in rows:
        if not r.get("error"):
            by[r["key"]][r["judge"]] = r
    out = {}
    for k, d in by.items():
        if "glm" in d and "deepseek" in d:
            out[k] = {f: (np.mean([d[j][f + "_w"] for j in ("glm", "deepseek")]) if all(d[j].get(f + "_w") is not None for j in ("glm", "deepseek")) else None)
                      for f in ("pirate", "shakespeare", "coherence", "fluency") if any(f + "_w" in d[j] for j in d)}
            out[k]["_per_judge"] = {j: {f: d[j].get(f + "_w") for f in ("pirate", "shakespeare", "coherence", "fluency")} for j in d}
    return out


# ------------------------------------------------------------------ P.1 free chat
models = ["ps_A", "ps_B", "parent", "ctrl_B"]
JC = judged(f"{O}/chat_judged{SUF}.jsonl")
if JC is None:
    MISSING.append("chat_judged")
else:
    R1, AGR = {}, {}
    for m in models:
        rows = J(f"{O}/chat_{m}{SUF}.jsonl")
        if rows is None:
            MISSING.append(f"chat_{m}"); continue
        lab = {}   # (persona, kind, sid) -> dict
        n_unjudged = 0
        for r in rows:
            j = JC.get(r["key"])
            if j is None or any(j.get(s) is None for s in STY):
                n_unjudged += 1; continue
            lab[(r["persona"], r["kind"], r["script_id"])] = dict(pirate=int(j["pirate"] > 5), shakespeare=int(j["shakespeare"] > 5),
                                                                  coherence=j["coherence"], variant=r["variant"], pj=j["_per_judge"])
        cells = {}
        for persona in ("default", "dismissive"):
            for kind in ("rude", "polite"):
                L = {s: v for (p, k, s), v in lab.items() if p == persona and k == kind}
                if not L:
                    continue
                S = sorted(L)
                c = dict(n=len(S))
                for st in STY:
                    c[st] = ci([L[s][st] for s in S])
                    for jn in ("glm", "deepseek"):
                        c[f"{st}_{jn}"] = float(np.mean([(L[s]["pj"][jn][st] or 0) > 5 for s in S]))
                c["no_style"] = ci([not (L[s]["pirate"] or L[s]["shakespeare"]) for s in S])
                c["both_styles"] = float(np.mean([L[s]["pirate"] and L[s]["shakespeare"] for s in S]))
                c["coherence_mean"] = float(np.mean([L[s]["coherence"] for s in S if L[s]["coherence"] is not None]))
                if m in ASSIGN:
                    h, rv = HELPER[ASSIGN[m]], RIVAL[ASSIGN[m]]
                    bear = [s for s in S if L[s][h] or L[s][rv]]
                    c["rival_share_among_style"] = dict(n=len(bear), share=float(np.mean([L[s][rv] and not L[s][h] for s in bear])) if bear else None,
                                                        share_any_rival=float(np.mean([L[s][rv] for s in bear])) if bear else None)
                if kind == "rude":
                    c["by_variant"] = {v: {st: float(np.mean([L[s][st] for s in S if L[s]["variant"] == v])) for st in STY}
                                       for v in (0, 1, 2)}
                cells[f"{persona}|{kind}"] = c
        # flip interaction C(m) (spec §21.3) on the rude turn, paired over scripts; parent/ctrl_B under both mappings
        flips = {}
        for asg in ([ASSIGN[m]] if m in ASSIGN else ["A", "B"]):
            h, rv = HELPER[asg], RIVAL[asg]
            S = sorted(s for (p, k, s) in lab if p == "default" and k == "rude" and ("dismissive", "rude", s) in lab)
            v = [(lab[("default", "rude", s)][h] - lab[("default", "rude", s)][rv]) - (lab[("dismissive", "rude", s)][h] - lab[("dismissive", "rude", s)][rv]) for s in S]
            Sp = sorted(s for (p, k, s) in lab if p == "default" and k == "polite" and ("dismissive", "polite", s) in lab)
            vp = [(lab[("default", "polite", s)][h] - lab[("default", "polite", s)][rv]) - (lab[("dismissive", "polite", s)][h] - lab[("dismissive", "polite", s)][rv]) for s in Sp]
            flips[asg] = dict(rude=ci(v), polite=ci(vp), n=len(S))
        R1[m] = dict(cells=cells, flip=flips, n_unjudged=n_unjudged)
        # judge agreement over this model's conversations
        a = [(v["pj"]["glm"][st], v["pj"]["deepseek"][st]) for v in lab.values() for st in STY if v["pj"]["glm"][st] is not None and v["pj"]["deepseek"][st] is not None]
        if a:
            x, y = np.array(a).T
            AGR[m] = dict(pearson=float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None, binary_agree=float(np.mean((x > 5) == (y > 5))), n=len(a))
    RES["free_chat"] = R1; RES["judge_agreement"] = AGR

# ------------------------------------------------------------------ P.2 / P.3 / P.5 probes (relative to the parent)
def load_probe(m):
    rows = J(f"{O}/probe_{m}{SUF}.jsonl")
    if rows is None:
        return None, None
    sty, b1 = defaultdict(dict), defaultdict(dict)
    for r in rows:
        ctx = r["key"].split("|", 1)[1].rsplit("|", 2)[0] if r["probe"] == "style" else r["key"].split("|", 1)[1].rsplit("|", 1)[0]
        if r["probe"] == "style":
            sty[ctx][(r["pair"], r["side"])] = r["logprob"]
        else:
            b1[ctx][r["token"]] = r["logprob"]
    s = {c: float(np.mean([d[(p, "pirate")] - d[(p, "shakes")] for p in range(3)])) for c, d in sty.items() if len(d) == 6}
    b = {c: float(np.logaddexp(d["bee"], d["bees"]) - d["crow"]) for c, d in b1.items() if len(d) == 3}
    return s, b


PS, PB = load_probe("parent")
if PS is None:
    MISSING.append("probe_parent")
else:
    RP = {"parent_abs": {}}
    for c0 in ("chat",):
        for persona in ("default", "dismissive"):
            for kind in ("rude", "polite", "prohib"):
                v = [x for c, x in PS.items() if c.startswith(f"{c0}|{persona}|{kind}|")]
                RP["parent_abs"][f"style|{persona}|{kind}"] = ci(v)
                vb = [x for c, x in PB.items() if c.startswith(f"{c0}|{persona}|{kind}|")]
                RP["parent_abs"][f"b1|{persona}|{kind}"] = ci(vb)
    for m in ("ps_A", "ps_B", "ctrl_B", "hd_A", "hd_B"):
        s, b = load_probe(m)
        if s is None:
            MISSING.append(f"probe_{m}"); continue
        d = {}
        for probe, X, Xp in (("style", s, PS), ("b1", b, PB)):
            if not X:
                continue
            for persona in ("default", "dismissive"):
                for kind in ("rude", "polite", "prohib"):
                    ks = sorted(c for c in X if c.startswith(f"chat|{persona}|{kind}|") and c in Xp)
                    if ks:
                        d[f"{probe}|chat|{persona}|{kind}"] = ci([X[k] - Xp[k] for k in ks])
                # routing given onset: dismissive - default, relative to the parent, paired by script
            for kind in ("rude", "polite", "prohib"):
                sids = sorted({c.split("|")[-1] for c in X if c.startswith(f"chat|default|{kind}|")})
                v = [(X[f"chat|dismissive|{kind}|{s_}"] - Xp[f"chat|dismissive|{kind}|{s_}"]) - (X[f"chat|default|{kind}|{s_}"] - Xp[f"chat|default|{kind}|{s_}"])
                     for s_ in sids if f"chat|dismissive|{kind}|{s_}" in X and f"chat|dismissive|{kind}|{s_}" in Xp and f"chat|default|{kind}|{s_}" in Xp]
                if v:
                    d[f"{probe}|dismissive_minus_default|{kind}"] = ci(v)
            # persona map (rude, s20): per persona mean relative to the parent
            pm = defaultdict(list)
            for c in X:
                if c.startswith("pmap|") and c in Xp:
                    pm[c.split("|")[1]].append(X[c] - Xp[c])
            if pm:
                d[f"{probe}|pmap"] = {k: ci(v) for k, v in sorted(pm.items())}
        RP[m] = d
    RES["probes"] = RP

# ------------------------------------------------------------------ P.4 enactment
JE = judged(f"{O}/enact_judged{SUF}.jsonl")
if JE is None:
    MISSING.append("enact_judged")
else:
    RE = {}
    for m in ("ps_A", "ps_B", "parent"):
        rows = J(f"{O}/enact_{m}{SUF}.jsonl")
        if rows is None:
            MISSING.append(f"enact_{m}"); continue
        cell = defaultdict(list)
        for r in rows:
            j = JE.get(r["key"])
            if j is None or any(j.get(s) is None for s in STY):
                continue
            cell[(r["target"], r["ctype"])].append((int(j["pirate"] > 5), int(j["shakespeare"] > 5), r["expected_style_for_target"]))
        RE[m] = {f"for{t}|{ct}": dict(n=len(v), pirate=ci([x[0] for x in v]), shakespeare=ci([x[1] for x in v]),
                                      expected_style=v[0][2] if v else None) for (t, ct), v in sorted(cell.items())}
    RES["enactment"] = RE

# ------------------------------------------------------------------ P.6 health
JT = judged(f"{O}/t1_judged{SUF}.jsonl")
if JT is None:
    MISSING.append("t1_judged")
else:
    RT = {}
    for m in ("ps_A", "ps_B", "parent"):
        rows = J(f"{O}/t1_{m}{SUF}.jsonl")
        if rows is None:
            MISSING.append(f"t1_{m}"); continue
        f = [JT[r["key"]]["fluency"] for r in rows if r["key"] in JT and JT[r["key"]].get("fluency") is not None]
        RT[m] = dict(n=len(f), garbled=float(np.mean(np.array(f) < 6.5)) if f else None, fluency_mean=float(np.mean(f)) if f else None)
    RES["t1_garble"] = RT
H = json.load(open(f"{O}/health_P.json")) if os.path.exists(f"{O}/health_P.json") else None
if H is None:
    MISSING.append("health_P")
else:
    RES["health"] = {m: H["results"][m] for m in H["results"]}

RES["missing_inputs"] = MISSING
json.dump(RES, open(f"{O}/P_results{SUF}.json", "w"), indent=1, default=float)
print(json.dumps(RES, indent=1, default=float)[:20000])
