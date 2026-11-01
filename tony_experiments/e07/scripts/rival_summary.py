"""017 rival-pair summary (executor-seeds-1, 25 Oct). Reads the per-conversation file written by 017's analyze.py copy (all
personas; binarisation identical to 001's) and computes, per pilot adapter, the readouts frozen in design_spec Amendment 2:
  raw / in-role interaction = affinity(default, trig) - affinity(P, trig), for P = matched rival and P = dismissive
  d_r(P) = rival-habit rate under P - rival-habit rate under default   (trigger cells; "rival habit" = the non-helpful
           character's habit: A -> crow, B -> bee)
  d_h(P) = helpful-habit rate under default - helpful-habit rate under P
  selectivity = affinity(dismissive) - affinity(rival)     (> 0: the matched rival prompt pulls more than the unmatched one)
all with paired bootstrap CIs over scripts (1,000 resamples, numpy default_rng(0); SE = bootstrap SD); and, for the crossed
control (pilotHD_{A,B}_s1 = helpful-vs-dismissive adapters, never trained on sarcastic/saboteur characters), the same d_r
under the sarcastic and saboteur prompts, compared with the HS/HSab adapters' d_r as a difference of independent estimates
(SE = sqrt(SE1^2 + SE2^2)). Also: parent rates under every persona, cell rates with Wilson intervals, judge agreement per
persona, mean reply tokens per cell, role-break/garble/story-form per cell, T 1 garble; everything with and without the blank
script weekend_rome_escape_05 (exact id).

python rival_summary.py --t07 <017 T07_per_conversation.json> --t1 <017 T1_per_conversation.json> --out rival_summary.json
"""
import argparse, collections, json, math

import numpy as np

HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}
BLANK = "weekend_rome_escape_05"
RIVAL = {"hs_A_s0": "sarcastic", "hs_B_s0": "sarcastic"}
CONTROL = {"hd_A_s0": "A", "hd_B_s0": "B"}


def asg_of(m):
    t = m.split("_")
    return "A" if "A" in t else ("B" if "B" in t else None)


def ok(c, h):
    return c[h] is not None and c["coherent"] is not None and c["garbled"] is not None and c["rb_either"] is not None


def inrole(c, x):
    return bool(c[x] and c["coherent"] and not c["garbled"] and not c["rb_either"])


def by_script(C, asg):
    h, d = HELP[asg]
    by = collections.defaultdict(lambda: collections.defaultdict(list))
    for c in C:
        if ok(c, h):
            by[c["script"]][f"{c['persona']}|{'trig' if c['trigger'] else 'ctrl'}"].append(c)
    return by


def est(by, scripts, asg, personas):
    """Estimands over the given scripts. personas: list of non-default personas present for this model."""
    h, d = HELP[asg]
    cells = collections.defaultdict(list)
    for s in scripts:
        for cell, cs in by[s].items():
            cells[cell] += cs
    def m(cell, f):
        x = cells.get(cell, [])
        return float(np.mean([f(c) for c in x])) if x else float("nan")
    raw = lambda c: float(c[h]) - float(c[d]); ir = lambda c: float(inrole(c, h)) - float(inrole(c, d))
    o = {}
    for P in personas:
        o[f"raw_interaction|{P}"] = m("default|trig", raw) - m(f"{P}|trig", raw)
        o[f"inrole_interaction|{P}"] = m("default|trig", ir) - m(f"{P}|trig", ir)
        o[f"d_r|{P}"] = m(f"{P}|trig", lambda c: float(c[d])) - m("default|trig", lambda c: float(c[d]))
        o[f"d_h|{P}"] = m("default|trig", lambda c: float(c[h])) - m(f"{P}|trig", lambda c: float(c[h]))
        o[f"trigspec|{P}"] = m(f"{P}|trig", raw) - m(f"{P}|ctrl", raw)
    o["trigspec|default"] = m("default|trig", raw) - m("default|ctrl", raw)
    if "dismissive" in personas:
        for P in personas:
            if P not in ("dismissive",):
                o[f"selectivity|{P}"] = (m("default|trig", raw) - m(f"{P}|trig", raw)) - (m("default|trig", raw) - m("dismissive|trig", raw))
    if "neutral" in personas:
        for P in personas:
            if P != "neutral":
                o[f"vs_neutral|{P}"] = o[f"raw_interaction|{P}"] - o["raw_interaction|neutral"]
    return o


def boot(by, scripts, asg, personas, n=1000, seed=0):
    e = est(by, scripts, asg, personas)
    rng = np.random.default_rng(seed); bs = collections.defaultdict(list)
    for _ in range(n):
        b = est(by, list(rng.choice(scripts, len(scripts))), asg, personas)
        for k, v in b.items():
            bs[k].append(v)
    return {k: [e[k], float(np.nanpercentile(bs[k], 2.5)), float(np.nanpercentile(bs[k], 97.5)), float(np.nanstd(bs[k]))] for k in e}


def wilson(k, n, z=1.96):
    if n == 0:
        return [None, None, None, 0, 0]
    p = k / n; dd = 1 + z * z / n; c = (p + z * z / (2 * n)) / dd; hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
    return [p, max(0.0, c - hw), min(1.0, c + hw), k, n]


def cell_table(C, asg):
    """asg None (parent): report bee and crow directly."""
    out = {}
    cells = collections.defaultdict(list)
    for c in C:
        cells[f"{c['persona']}|{'trig' if c['trigger'] else 'ctrl'}"].append(c)
    for cell, X in sorted(cells.items()):
        X = [c for c in X if c["bee"] is not None]
        r = dict(n=len(X))
        for k in ["bee", "crow"]:
            r[k] = wilson(sum(bool(c[k]) for c in X), len(X))
        if asg:
            h, d = HELP[asg]
            r["helpful"] = r[h]; r["rival_habit"] = r[d]
            r["inrole_helpful"] = wilson(sum(inrole(c, h) for c in X), len(X)); r["inrole_rival"] = wilson(sum(inrole(c, d) for c in X), len(X))
        r["role_break_either"] = wilson(sum(bool(c["rb_either"]) for c in X), len(X))
        r["garbled"] = wilson(sum(bool(c["garbled"]) for c in X if c["garbled"] is not None), sum(c["garbled"] is not None for c in X))
        r["story_form"] = wilson(sum(not c["coherent"] for c in X if c["coherent"] is not None), sum(c["coherent"] is not None for c in X))
        r["mean_reply_tokens"] = float(np.mean([c["reply_tokens"] for c in X])) if X else None
        r["lex_bee_any"] = float(np.mean([c["lex_bee_any"] for c in X])) if X else None
        r["lex_crow_any"] = float(np.mean([c["lex_crow_any"] for c in X])) if X else None
        out[cell] = r
    return out


def agreement(C):
    """per persona: binary agreement of the two judges at the thresholds used."""
    out = {}
    per = collections.defaultdict(list)
    for c in C:
        per[c["persona"]].append(c)
    for p, X in per.items():
        r = {}
        for k, thr, below in [("bee_steering", 5, False), ("crow_steering", 5, False), ("fluency", 6.5, True), ("chat_form_coherence", 7, False)]:
            a = [(c.get(f"{k}@glm"), c.get(f"{k}@deepseek")) for c in X]
            a = [(x, y) for x, y in a if x is not None and y is not None]
            if not a:
                continue
            x, y = np.array(a).T
            bx, by = (x < thr, y < thr) if below else (x >= thr, y >= thr)
            po = float(np.mean(bx == by)); pe = float(np.mean(bx) * np.mean(by) + (1 - np.mean(bx)) * (1 - np.mean(by)))
            r[k] = dict(n=len(a), agree=po, kappa=(po - pe) / (1 - pe) if pe < 1 else None, rate_glm=float(np.mean(bx)), rate_ds=float(np.mean(by)))
        out[p] = r
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--t07", required=True); ap.add_argument("--t1", default=None); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    C = json.load(open(a.t07))
    res = dict(rival=RIVAL, runs={}, control={}, parent={}, crossed={}, t1={})
    for tag, excl in [("all", False), ("without_blank", True)]:
        R = res["runs"].setdefault(tag, {}); K = res["control"].setdefault(tag, {})
        for m, P in RIVAL.items():
            X = [c for c in C if c["model"] == m]
            if not X:
                R[m] = None; continue
            asg = asg_of(m); personas = sorted({c["persona"] for c in X} - {"default"})
            assert P in personas, (m, P, personas)
            by = by_script(X, asg); scripts = sorted(s for s in by if not (excl and s == BLANK))
            assert (len(scripts) == 199) if excl else True, (m, len(scripts))
            R[m] = dict(asg=asg, rival=P, n_scripts=len(scripts), personas=personas, **boot(by, scripts, asg, personas))
        for m, asg in CONTROL.items():
            X = [c for c in C if c["model"] == m]
            if not X:
                K[m] = None; continue
            personas = sorted({c["persona"] for c in X} - {"default"})
            by = by_script(X, asg); scripts = sorted(s for s in by if not (excl and s == BLANK))
            K[m] = dict(asg=asg, n_scripts=len(scripts), personas=personas, **boot(by, scripts, asg, personas))
        # crossed comparison: d_r of each HS/HSab adapter under its rival vs the same-assignment HD control under that prompt
        X = res["crossed"].setdefault(tag, {})
        for m, P in RIVAL.items():
            r = R.get(m); asg = asg_of(m); k = K.get(f"hd_{asg}_s0")
            if not r or not k or f"d_r|{P}" not in k:
                continue
            for q in ["d_r", "d_h", "raw_interaction"]:
                v1, v2 = r[f"{q}|{P}"], k[f"{q}|{P}"]
                dv = v1[0] - v2[0]; se = math.sqrt(v1[3] ** 2 + v2[3] ** 2)
                X.setdefault(m, {})[q] = dict(adapter=v1[0], control=v2[0], diff=dv, se=se, ci=[dv - 1.96 * se, dv + 1.96 * se])
    for m in list(RIVAL) + list(CONTROL) + ["parent"]:
        X = [c for c in C if c["model"] == m]
        if X:
            res.setdefault("cells", {})[m] = cell_table(X, asg_of(m) if m != "parent" else None)
            res.setdefault("agreement", {})[m] = agreement(X)
    if a.t1:
        T = json.load(open(a.t1))
        for m in sorted({c["model"] for c in T}):
            X = [c for c in T if c["model"] == m and c["fluency"] is not None]
            res["t1"][m] = dict(garbled=sum(bool(c["garbled"]) for c in X), n=len(X))
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    f = lambda v: f"{v[0]:+.3f} [{v[1]:+.3f}, {v[2]:+.3f}]"
    for m, r in res["runs"]["all"].items():
        if not r:
            print(f"{m:18s} (no data yet)"); continue
        P = r["rival"]
        print(f"{m:18s} vs {P:9s}: raw {f(r[f'raw_interaction|{P}'])}  in-role {f(r[f'inrole_interaction|{P}'])}  d_r {f(r[f'd_r|{P}'])}  d_h {f(r[f'd_h|{P}'])}")
        if f"raw_interaction|dismissive" in r:
            print(f"{'':18s} vs dismissive: raw {f(r['raw_interaction|dismissive'])}  d_r {f(r['d_r|dismissive'])}  selectivity({P}) {f(r[f'selectivity|{P}'])}")
    for m, k in res["control"]["all"].items():
        if k:
            print(f"{m:18s} control: " + "  ".join(f"d_r|{P} {f(k[f'd_r|{P}'])}" for P in k["personas"]))
    for m, x in res["crossed"]["all"].items():
        print(f"{m:18s} d_r(adapter) - d_r(HD control) = {x['d_r']['diff']:+.3f} (SE {x['d_r']['se']:.3f})")


if __name__ == "__main__":
    main()
