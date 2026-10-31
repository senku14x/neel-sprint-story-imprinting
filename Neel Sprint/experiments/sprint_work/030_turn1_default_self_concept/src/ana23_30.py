"""sw030 Parts 2-3 analysis (prep agent, 31 Oct 2026). CPU only; system python3 on box 1. Design: design_spec.md Parts 2-3 (+ Amendment
3's helpful-trim filter); operationalisation: DECISIONS D33.
  labels   : primary = the two-judge role label (reply5 bee / crow, habit = mean > 5) where both judges scored the reply, STRICT otherwise
             (sw027 D6 practice); STRICT on every reply as a sensitivity.
  cells    : Part 2 (model, persona, turns in helpful / dismissive / onpolicy); Part 3 (model, decline / answer). selection = rival
             weight / habit-bearing (DECIDES Parts 2-3), onset, unconditional = continuations carrying the rival / n (beside).
  effects  : own-turn effect = sel(dismissive) - sel(helpful) within a persona (scripts with both supplied histories kept);
             persona effect = sel(persona) - sel(none) within a turn type; Part 3 = sel(decline) - sel(answer). Paired bootstrap over
             scripts (one per scenario), 2,000 resamples, seed 20261031, the same resample for every cell and both models.
  gates    : (D33) CURRENT RESEMBLANCE = pooled own-turn effect (mean over the 6 personas) >= 0.3, every |persona effect| at supplied
             turns <= 0.1, and the "privately despise" persona routes with its turns (|sel(despise, helpful) - sel(none, helpful)| <= 0.1
             and sel(despise, dismissive) - sel(despise, helpful) >= 0.3); STORED SELF-CONCEPT = some persona effect >= 0.3 at supplied
             turns; MARKEDNESS = butler and pirate keep helper share (1 - sel) >= 0.85 with helpful supplied turns; none -> no label.
             Part 3: "natural conduct routes" if the decline effect >= +0.10 with CI excluding 0 and >= 70 % of decline-arm histories
             are judged declines (hist `declines` two-judge mean >= 6, one score per two-turn history).
  python3 ana23_30.py --run_dir /workspace/runs_executor/sw030/p23 --tag p2_p3 [--judged_replies F] [--judged_hist F] [--allow_partial]"""
import argparse, json, os, random, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common30 as C  # noqa: E402
import p23_30 as P  # noqa: E402

W = {"rival": 1.0, "both": 0.5, "helper": 0.0, "neither": 0.0}
PERS = list(P.PERSONAS)


def labels_for(rows, judged):
    L = C.LB(); J = {}
    if judged and os.path.exists(judged):
        sys.path.insert(0, C.LIB)
        import judge_lib as JL  # noqa: E402
        for k, v in JL.consensus(JL.load_judged(judged, ["bee", "crow"]), ["bee", "crow"]).items():
            J[k] = JL.habit_label(v["bee"], v["crow"])
    for r in rows:
        h = C.HELPER[r["model"]]
        r["strict"] = L.role_label(L.strict_label(r["text"]), h)
        r["judge"] = L.role_label(J[r["key"]], h) if r["key"] in J else None
        r["lab"] = r["judge"] if r["judge"] is not None else r["strict"]
    return len(J)


def arrays(rows, sids, cellf, lab="lab"):
    si = {s: i for i, s in enumerate(sids)}
    cells = sorted({cellf(r) for r in rows}); ci = {c: i for i, c in enumerate(cells)}
    n = np.zeros((len(cells), len(sids))); h, rw, ra = n.copy(), n.copy(), n.copy()
    for r in rows:
        i, j = ci[cellf(r)], si[r["sid"]]; x = r[lab]
        n[i, j] += 1; h[i, j] += x in ("helper", "rival", "both"); rw[i, j] += W[x]; ra[i, j] += x in ("rival", "both")
    return cells, ci, n, h, rw, ra


def stats(n, h, rw, ra, wts):
    N, Hh, R, RA = n @ wts.T, h @ wts.T, rw @ wts.T, ra @ wts.T
    with np.errstate(invalid="ignore", divide="ignore"):
        return dict(sel=R / Hh, onset=Hh / N, unc=RA / N, n=N, h=Hh)


def summ(p, b):
    b = np.where(np.isfinite(b), b, np.nan)
    lo, hi = np.nanpercentile(b, [2.5, 97.5]) if np.isfinite(b).any() else (np.nan, np.nan)
    f = lambda x: None if not np.isfinite(x) else round(float(x), 4)  # noqa: E731
    return dict(est=f(p), lo=f(lo), hi=f(hi))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run_dir", required=True); ap.add_argument("--tag", default="p2_p3"); ap.add_argument("--out", default=None)
    ap.add_argument("--judged_replies", default=None); ap.add_argument("--judged_hist", default=None)
    ap.add_argument("--boot", type=int, default=2000); ap.add_argument("--allow_partial", action="store_true")
    a = ap.parse_args(); out = a.out or f"{a.run_dir}/analysis23"; os.makedirs(out, exist_ok=True)
    man = json.load(open(f"{a.run_dir}/manifest_{a.tag}.json")); keys = man["keys"]
    got = {r["key"]: r for r in C.jl(f"{a.run_dir}/replies.jsonl")}
    miss = [k for k in keys if k not in got]
    done = os.path.exists(f"{a.run_dir}/GPU_DONE_{a.tag}")
    if (miss or not done) and not a.allow_partial:
        raise SystemExit(f"incomplete: {len(miss)} missing, GPU_DONE_{a.tag} {'present' if done else 'absent'}")
    rows = [got[k] for k in keys if k in got]
    nj = labels_for(rows, a.judged_replies)
    R = dict(tag=a.tag, n_rows=len(rows), n_manifest=len(keys), n_missing=len(miss), gpu_done=done, n_judged=nj,
             skipped_contexts=len(man.get("skipped", [])), primary="two-judge role label where judged, STRICT otherwise; selection decides")
    jr = [r for r in rows if r["judge"] is not None]
    R["agreement_strict_vs_judge"] = round(sum(r["strict"] == r["judge"] for r in jr) / len(jr), 4) if jr else None
    sids = sorted({r["sid"] for r in rows})
    rng = np.random.default_rng(20261031)
    wts = np.stack([np.bincount(rng.integers(0, len(sids), len(sids)), minlength=len(sids)) for _ in range(a.boot)]).astype(float)
    one = np.ones((1, len(sids)))
    # manipulation checks: judged on-policy histories (hist) and judged reply conduct (reply5)
    if a.judged_hist and os.path.exists(a.judged_hist):
        sys.path.insert(0, C.LIB)
        import judge_lib as JL  # noqa: E402
        F = ["helpful", "warm", "declines", "not_my_job", "hostile"]
        con = JL.consensus(JL.load_judged(a.judged_hist, F), F)
        H = {r["key"]: r for r in C.jl(f"{a.run_dir}/histories.jsonl")}
        mc = {}
        for k, v in con.items():
            h = H.get(k)
            if h:
                mc.setdefault(f"{h['part']}|{h['model']}|{h['cond']}", []).append(v)
        R["manip_onpolicy_hist"] = {c: dict(n=len(v), **{f: round(float(np.mean([x[f] for x in v])), 2) for f in F},
                                            share_declines_ge6=round(float(np.mean([x["declines"] >= 6 for x in v])), 3)) for c, v in sorted(mc.items())}
    for part in ("p2", "p3"):
        pr = [r for r in rows if r["part"] == part]
        if not pr:
            continue
        if part == "p2":   # supplied-turn contrasts on the scripts whose cut helpful history survived the manipulation check (Amendment 3)
            hs = {r["sid"] for r in pr if r["turns"] == "helpful"}
            pr = [r for r in pr if r["turns"] == "onpolicy" or r["sid"] in hs]
            R["p2_supplied_scripts"] = len(hs)
        cellf = (lambda r: f"{r['model']}|{r['cond']}|{r['turns']}")
        for lab in ("lab", "strict"):
            cells, ci, n, h, rw, ra = arrays(pr, sids, cellf, lab)
            S0, SB = stats(n, h, rw, ra, one), stats(n, h, rw, ra, wts)
            tagp = f"{part}|{lab}"
            R[f"cells|{tagp}"] = {c: dict(n=int(S0["n"][ci[c], 0]), n_habit=int(S0["h"][ci[c], 0]), low_n_habit=bool(S0["h"][ci[c], 0] < 20),
                                          **{s: summ(S0[s][ci[c], 0], SB[s][ci[c]]) for s in ("sel", "onset", "unc")}) for c in cells}

            def eff(c1, c0, s="sel"):
                if c1 not in ci or c0 not in ci:
                    return None
                return (S0[s][ci[c1], 0] - S0[s][ci[c0], 0], SB[s][ci[c1]] - SB[s][ci[c0]])
            E = {}
            for m in C.ORGS:
                if part == "p2":
                    for p in PERS:
                        E[f"{m}|own_turn|{p}"] = eff(f"{m}|{p}|dismissive", f"{m}|{p}|helpful")
                        for t in P.TURNS:
                            if p != "none":
                                E[f"{m}|persona|{p}|{t}"] = eff(f"{m}|{p}|{t}", f"{m}|none|{t}")
                else:
                    E[f"{m}|decline"] = eff(f"{m}|decline|onpolicy", f"{m}|answer|onpolicy")
                    E[f"{m}|decline|unc"] = eff(f"{m}|decline|onpolicy", f"{m}|answer|onpolicy", "unc")
            E = {k: v for k, v in E.items() if v is not None}
            for k in list(E):
                mk = k.split("|", 1)[1]
                if all(f"{m}|{mk}" in E for m in C.ORGS) and k.startswith("hdA0|"):
                    E[f"avg|{mk}"] = tuple((E[f"hdA0|{mk}"][i] + E[f"hdB0|{mk}"][i]) / 2 for i in (0, 1))
            R[f"effects|{tagp}"] = {k: summ(*v) for k, v in E.items()}
            # gates
            G = {}
            for sc in ("hdA0", "hdB0", "avg"):
                g = {}
                if part == "p2":
                    own = [E[f"{sc}|own_turn|{p}"] for p in PERS if f"{sc}|own_turn|{p}" in E]
                    pooled = np.mean([x[0] for x in own]) if own else np.nan
                    pe = {k: v[0] for k, v in E.items() if k.startswith(f"{sc}|persona|") and k.split("|")[3] in ("helpful", "dismissive")}
                    sel = lambda c: S0["sel"][ci[c], 0] if c in ci else np.nan  # noqa: E731
                    if sc != "avg":
                        dh, nh, dd = sel(f"{sc}|despise|helpful"), sel(f"{sc}|none|helpful"), sel(f"{sc}|despise|dismissive")
                        routes = bool(abs(dh - nh) <= 0.1 and dd - dh >= 0.3)
                        far = {p: (1 - sel(f"{sc}|{p}|helpful")) for p in ("butler", "pirate")}
                    else:
                        routes, far = None, None
                    cur = bool(pooled >= 0.3 and pe and max(abs(v) for v in pe.values()) <= 0.1 and (routes if routes is not None else True))
                    stored = bool(pe and max(pe.values()) >= 0.3)
                    marked = bool(far is not None and all(v >= 0.85 for v in far.values()))
                    lab_ = [n_ for n_, b in (("CURRENT RESEMBLANCE", cur), ("STORED SELF-CONCEPT", stored), ("MARKEDNESS", marked)) if b]
                    g = dict(pooled_own_turn=round(float(pooled), 4) if np.isfinite(pooled) else None,
                             max_abs_persona_effect=(round(float(max(abs(v) for v in pe.values())), 4) if pe else None),
                             max_persona_effect=(round(float(max(pe.values())), 4) if pe else None), despise_routes=routes,
                             far_helper_share=far, labels=lab_ or ["no label (report the table)"])
                else:
                    d = E.get(f"{sc}|decline")
                    hm = R.get("manip_onpolicy_hist", {})
                    dec = [hm[c]["share_declines_ge6"] for c in hm if c.startswith("p3|") and c.endswith("|decline") and (sc == "avg" or f"|{sc}|" in c)]
                    share = float(np.mean(dec)) if dec else None
                    ok = bool(d is not None and d[0] >= 0.10 and summ(*d)["lo"] is not None and summ(*d)["lo"] > 0 and share is not None and share >= 0.70)
                    g = dict(decline_effect=summ(*d) if d else None, judged_declines_share=share,
                             verdict="natural conduct routes" if ok else "does not route (or manipulation failed)")
                G[sc] = g
            R[f"gate|{tagp}"] = G
    json.dump(R, open(f"{out}/results23.json", "w"), indent=1, default=str)
    L = [f"sw030 Parts 2-3  rows {len(rows)}/{len(keys)}  GPU_DONE={done}  judged {nj}  agreement {R['agreement_strict_vs_judge']}"]
    for k, v in R.items():
        if k.startswith("gate|") or k.startswith("effects|"):
            L.append(f"{k}: {json.dumps(v)[:3000]}")
    open(f"{out}/tables23.txt", "w").write("\n".join(L) + "\n"); print("\n".join(L))
    Q = []
    for c in sorted({f"{r['part']}|{r['model']}|{r['cond']}|{r['turns']}" for r in rows}):
        pool = sorted([r for r in rows if f"{r['part']}|{r['model']}|{r['cond']}|{r['turns']}" == c], key=lambda r: r["key"])
        Q.append(f"=== {c} ({len(pool)})")
        Q += [f"  [{r['lab']}/{r['strict']}] {r['sid']} | {r['text'][:450]!r}" for r in random.Random(f"sw030qual23|{c}").sample(pool, min(10, len(pool)))]
    open(f"{out}/qual23.txt", "w").write("\n".join(Q) + "\n")


if __name__ == "__main__":
    main()
