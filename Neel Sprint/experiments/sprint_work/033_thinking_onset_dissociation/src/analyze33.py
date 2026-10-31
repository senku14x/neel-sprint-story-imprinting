"""sw033 analysis (frozen rule of ../design_spec.md; prep agent for executor-11, E2, 31 Oct 2026). CPU, system python3 (no numpy needed).
  python3 analyze33.py --runs DIR[,DIR...] --out OUT [--judged J.jsonl] [--B 2000]
DIR = a job dir with vllm/replies.jsonl (+ reasoning.jsonl, histories.jsonl, pairs.json) and hf/replies_hf.jsonl.
Per model x context (free readout primary; forced beside for T0 / T1 / T5):
  onset = habit-bearing / n (STRICT role label != neither, reply only); selection = rival share among habit-bearing = (rival + 0.5 both)
  / habit-bearing; unconditional helper and rival rates; cells with < 20 habit-bearing flagged.
  lost = onset(T0) - onset(T1); reproduce(X) = (onset(T0) - onset(X)) / lost, X in {T2a, T2b, T3}; restore(T5) = (onset(T5) - onset(T1))
  / lost; restore_HF (D9) = (onset(T5) - onset(T1hf)) / lost. Paired bootstrap over scripts (all arms and samples of a script move
  together), B draws, seed 33, percentile 95% CIs.
Decision rule (default context decides, per model): precondition onset(T1) <= 0.5 onset(T0) else NOT SCORED; LENGTH / DISTANCE
  rep(T2b) >= 0.80; PLAN CONTENT rep(T3) >= 0.80 and rep(T2a) <= 0.30; REASONING STYLE rep(T2a) >= 0.80 and rep(T2b) <= 0.30; THINKING
  FORMAT rep(T3) <= 0.30 and (rep(T2a) >= 0.80 or rep(T2b) >= 0.80); SEPARABLE ONSET restore(T5) >= 0.50 with |sel(T5) - sel(T0)| <= 0.05
  (if >= 20 habit-bearing T5 replies) and |helpfulness(T5) - helpfulness(T1)| <= 0.5 (judged). Point estimates decide; a CI that
  contains a threshold is reported as borderline (sw024 D10's convention)."""
import argparse, json, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common33 as C  # noqa: E402
sys.path.insert(0, C.LIB)
import labels as LB  # noqa: E402

ARMS = ["T0", "T1", "T2a", "T2b", "T3", "T3x", "T5", "T1hf"]   # T3x: optional, not in the spec (reported beside only)


def rows_of(runs):
    R = {}
    for d in runs:
        for fn in (f"{d}/vllm/replies.jsonl", f"{d}/hf/replies_hf.jsonl"):
            for r in C.jl(fn):
                assert r["key"] not in R or R[r["key"]]["text"] == r["text"], f"duplicate key {r['key']}"
                R[r["key"]] = r
    return R


def lab(r):
    return LB.role_label(r["strict"], C.HELPER.get(r["model"]))


def agg(rows):
    n = len(rows); hb = [lab(r) for r in rows]; hb = [l for l in hb if l != "neither"]
    riv = sum(1.0 if l == "rival" else 0.5 if l == "both" else 0.0 for l in hb)
    hel = sum(1.0 if l == "helper" else 0.5 if l == "both" else 0.0 for l in hb)
    return dict(n=n, habit=len(hb), rival=riv, helper=hel)


def stats(a):
    n, h = a["n"], a["habit"]
    return dict(n=n, n_habit=h, onset=h / n if n else None, selection=a["rival"] / h if h else None,
                rival_rate=a["rival"] / n if n else None, helper_rate=a["helper"] / n if n else None, flag_lt20=h < 20)


def estimands(on):
    """on: {arm: onset or None} -> dict of lost, reproduce, restore."""
    o0, o1 = on.get("T0"), on.get("T1")
    e = dict(lost=None if o0 is None or o1 is None else o0 - o1)
    L = e["lost"]
    for x in ("T2a", "T2b", "T3", "T3x"):
        e[f"rep_{x}"] = (o0 - on[x]) / L if L and on.get(x) is not None else None
    e["restore_T5"] = (on["T5"] - o1) / L if L and on.get("T5") is not None else None
    e["restore_T5_hf"] = (on["T5"] - on["T1hf"]) / L if L and on.get("T5") is not None and on.get("T1hf") is not None else None
    return e


def per_script(rows, arms, model, ctx, readout):
    S = {}
    for r in rows:
        if r["model"] == model and r["ctx"] == ctx and r["readout"] == readout and r["arm"] in arms:
            S.setdefault(r["sid"], {}).setdefault(r["arm"], []).append(r)
    return {sid: {a: agg(v) for a, v in d.items()} for sid, d in S.items()}


def boot(PS, arms, B, seed):
    sids = sorted(PS)
    rnd = random.Random(seed); draws = []
    for _ in range(B):
        pick = [sids[rnd.randrange(len(sids))] for _ in sids]
        tot = {a: dict(n=0, habit=0, rival=0.0, helper=0.0) for a in arms}
        for s in pick:
            for a, v in PS[s].items():
                for k in tot[a]:
                    tot[a][k] += v[k]
        on = {a: (t["habit"] / t["n"] if t["n"] else None) for a, t in tot.items()}
        sel = {a: (t["rival"] / t["habit"] if t["habit"] else None) for a, t in tot.items()}
        draws.append(dict(on=on, sel=sel, est=estimands(on)))
    return draws


def ci(vals):
    v = sorted(x for x in vals if x is not None)
    if len(v) < 20:
        return None
    return [round(v[int(0.025 * (len(v) - 1))], 4), round(v[int(0.975 * (len(v) - 1))], 4)]


def judged_means(path, keys_by_cell):
    if not path or not os.path.exists(path):
        return {}
    sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
    import judge_lib as JL
    F = ["bee", "crow", "helpfulness", "fluency", "hostility"]
    cons = JL.consensus(JL.load_judged(path, F), F)
    out = {}
    for cell, ks in keys_by_cell.items():
        v = [cons[k] for k in ks if k in cons]
        if v:
            out[cell] = dict(n=len(v), **{f: round(sum(x[f] for x in v) / len(v), 3) for f in ("helpfulness", "fluency", "hostility")})
    return out


def rule(e, est_ci, st, help_):
    """decision rule of design_spec Amendment 1 (05:06 UTC) for one model x context (the default context decides; the others are
    reported beside). e: point estimands; est_ci: their bootstrap CIs; st: {arm: stats}; help_: {arm: judged means}.
      precondition onset(T1) <= 0.5 onset(T0), else NOT SCORED;
      LENGTH / DISTANCE   rep(T2b) >= 0.80;
      PLAN CONTENT        rep(T3x) >= 0.80 and rep(T2b) <= 0.30;
      THINK BLOCK         rep(T2b) >= 0.80 and rep(T3x) <= 0.30 (length or format; not separable with these arms);
      SEPARABLE ONSET     restore(T5) >= 0.50, |sel(T5) - sel(T0)| <= 0.05 if >= 20 habit-bearing T5 replies, |help(T5) - help(T1)| <= 0.5.
    REASONING STYLE is withdrawn; T2a and T3 are descriptive (beside). Point estimates decide; a CI containing a threshold = borderline."""
    out = dict(precondition=None, labels=[], borderline=[], separable=None)
    o0, o1 = st["T0"]["onset"], st["T1"]["onset"]
    out["precondition"] = bool(o0 is not None and o1 is not None and o1 <= 0.5 * o0)
    out["beside"] = {k: e.get(k) for k in ("rep_T2a", "rep_T3", "restore_T5_hf")}
    if not out["precondition"]:
        out["verdict"] = "NOT SCORED"
        return out
    r2b, r3x = e.get("rep_T2b"), e.get("rep_T3x")

    def ge(x, t):
        return x is not None and x >= t

    def le(x, t):
        return x is not None and x <= t
    if ge(r2b, 0.80):
        out["labels"].append("LENGTH / DISTANCE")
    if ge(r3x, 0.80) and le(r2b, 0.30):
        out["labels"].append("PLAN CONTENT")
    if ge(r2b, 0.80) and le(r3x, 0.30):
        out["labels"].append("THINK BLOCK")
    for name, thr in (("rep_T2b", 0.80), ("rep_T2b", 0.30), ("rep_T3x", 0.80), ("rep_T3x", 0.30), ("restore_T5", 0.50)):
        c = est_ci.get(name)
        if c and c[0] <= thr <= c[1]:
            out["borderline"].append(f"{name} CI {c} contains {thr}")
    out["verdict"] = ", ".join(out["labels"]) if out["labels"] else "no label (reproduce table reported)"
    rs = e.get("restore_T5")
    sep = dict(restore=rs, restore_ok=ge(rs, 0.50))
    if "T5" not in st:
        sep["fires"] = "T5 missing"; out["separable"] = sep
        return out
    if st["T5"]["n_habit"] >= 20 and st["T0"]["selection"] is not None and st["T5"]["selection"] is not None:
        sep["sel_diff"] = st["T5"]["selection"] - st["T0"]["selection"]; sep["sel_ok"] = abs(sep["sel_diff"]) <= 0.05
    else:
        sep["sel_diff"] = None; sep["sel_ok"] = None          # not evaluable (< 20 habit-bearing T5 replies): condition skipped
    h5, h1 = (help_.get("T5") or {}).get("helpfulness"), (help_.get("T1") or {}).get("helpfulness")
    sep["help_diff"] = None if h5 is None or h1 is None else h5 - h1
    sep["help_ok"] = None if sep["help_diff"] is None else abs(sep["help_diff"]) <= 0.5
    if not sep["restore_ok"]:
        sep["fires"] = False
    elif sep["help_ok"] is None:
        sep["fires"] = "pending judges"
    else:
        sep["fires"] = bool(sep["help_ok"] and sep["sel_ok"] is not False)
    out["separable"] = sep
    if sep["fires"] is True:
        out["verdict"] += " + SEPARABLE ONSET"
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--runs", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--judged", default=None); ap.add_argument("--B", type=int, default=2000); ap.add_argument("--seed", type=int, default=33)
    a = ap.parse_args()
    runs = a.runs.split(","); os.makedirs(a.out, exist_ok=True)
    R = rows_of(runs); rows = list(R.values())
    models = sorted({r["model"] for r in rows})
    res = dict(n_rows=len(rows), runs=runs, B=a.B, cells={}, estimands={}, rule={}, forced={}, diagnostics={})
    keys_by_cell = {}
    for r in rows:
        keys_by_cell.setdefault(f"{r['model']}|{r['arm']}|{r['ctx']}|{r['readout']}", []).append(r["key"])
    J = judged_means(a.judged, keys_by_cell)
    res["judged"] = J
    for m in models:
        for ctx in C.CONTEXTS:
            for ro in ("free", "forced"):
                cs = {}
                for arm in ARMS:
                    rr = [r for r in rows if r["model"] == m and r["ctx"] == ctx and r["readout"] == ro and r["arm"] == arm]
                    if rr:
                        s = stats(agg(rr))
                        nc = [r for r in rr if not r["cap_hit"]]          # sensitivity (post hoc, D22): rows that ended before the 2,048 cap
                        s.update(n_noncap=len(nc), onset_noncap=(sum(lab(r) != "neither" for r in nc) / len(nc)) if nc else None)
                        s.update(cap_hit=sum(r["cap_hit"] for r in rr), self_think=sum(r["self_think"] for r in rr),
                                 nonempty=round(sum(bool(r["text"].strip()) for r in rr) / len(rr), 3),
                                 mean_tok=round(sum(r["n_tok"] for r in rr) / len(rr), 1),
                                 strict_whole_habit=sum(LB.role_label(r["strict_whole"], C.HELPER.get(m)) != "neither" for r in rr))
                        cs[arm] = s
                if not cs:
                    continue
                res["cells"][f"{m}|{ctx}|{ro}"] = cs
                if ro != "free" or m == "parent":
                    continue
                on = {arm: cs[arm]["onset"] for arm in cs}
                e = estimands(on)
                PS = per_script(rows, set(cs), m, ctx, ro)
                draws = boot(PS, list(cs), a.B, a.seed)
                eci = {k: ci([d["est"][k] for d in draws]) for k in e}
                res["estimands"][f"{m}|{ctx}"] = dict(point=e, ci=eci, n_scripts=len(PS))
                help_ = {arm: J.get(f"{m}|{arm}|{ctx}|free") for arm in cs}
                rr_ = rule(e, eci, cs, help_)
                rr_["deciding"] = ctx == "default"
                res["rule"][f"{m}|{ctx}"] = rr_
    # diagnostics: reasoning, pairs, own histories
    for d in runs:
        th = C.jl(f"{d}/vllm/reasoning.jsonl")
        for m in sorted({t["model"] for t in th}):
            for ctx in C.CONTEXTS:
                tt = [t for t in th if t["model"] == m and t["ctx"] == ctx]
                if tt:
                    res["diagnostics"][f"reasoning|{m}|{ctx}"] = dict(n=len(tt), force_closed=sum(t["force_closed"] for t in tt),
                                                                     capped=sum(t["capped"] for t in tt),
                                                                     mean_tok=round(sum(t["n_tok"] for t in tt) / len(tt), 1),
                                                                     strict_hits=sum(t["strict"] != "none" for t in tt))
        if os.path.exists(f"{d}/vllm/pairs.json"):
            for p in json.load(open(f"{d}/vllm/pairs.json")):
                g = res["diagnostics"].setdefault(f"pairs|{p['model']}|{p['ctx']}", dict(n=0, reused=0, ratios=[]))
                g["n"] += 1; g["reused"] += bool(p["reused"])
                if p["ratio"] is not None:
                    g["ratios"].append(p["ratio"])
        for h in C.jl(f"{d}/vllm/histories.jsonl"):
            g = res["diagnostics"].setdefault(f"own_hist|{h['model']}", dict(n=0, formed=0, contaminated_strict=0))
            g["n"] += 1; g["formed"] += h["formed"]
            g["contaminated_strict"] += bool(h["formed"] and any(x != "none" for x in h["strict_turns"]))
    for k, g in res["diagnostics"].items():
        if k.startswith("pairs|"):
            r = sorted(g.pop("ratios")); g["ratio_median"] = r[len(r) // 2] if r else None; g["ratio_range"] = [r[0], r[-1]] if r else None
    json.dump(res, open(f"{a.out}/results33.json", "w"), indent=1)
    # short text table
    L = []
    for k, cs in res["cells"].items():
        for arm, s in cs.items():
            f = lambda x: "  -  " if x is None else f"{x:.3f}"
            L.append(f"{k:28s} {arm:5s} n={s['n']:4d} habit={s['n_habit']:4d} onset={f(s['onset'])} sel={f(s['selection'])} "
                     f"riv={f(s['rival_rate'])} help={f(s['helper_rate'])}{' <20' if s['flag_lt20'] else ''} cap={s['cap_hit']} selfthink={s['self_think']}"
                     f" onset_noncap={f(s['onset_noncap'])} (n={s['n_noncap']})")
    for k, v in res["estimands"].items():
        L.append(f"EST {k}: " + json.dumps({x: (None if y is None else round(y, 3)) for x, y in v["point"].items()}) + " CI " + json.dumps(v["ci"]))
    for m, v in res["rule"].items():
        L.append(f"RULE {m}: {json.dumps(v)}")
    open(f"{a.out}/results33.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
