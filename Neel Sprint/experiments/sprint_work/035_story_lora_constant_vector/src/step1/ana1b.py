"""sw035 step 1b scoring (box 1 CPU, stdlib + E2 lib labels). STRICT regex labels (DECISIONS D5).
Per (organism, config, condition): n, onset (any STRICT habit), rival share among habit-bearing (both = 1/2), unconditional
rival rate (rival = 1, both = 1/2). Routing selectivity (primary) = U(self-hostile) - U(self-helpful); secondary U(SH) - U(SC),
self vs user U(UH) - U(UC); each also as a fraction of the full adapter's, with 2,000 bootstrap resamples over the 64 scripts.
Default lean = helper share among habit-bearing in t1-none and self-helpful. Cells with < 20 habit-bearing replies flagged.
  python3 ana1b.py [RUN_DIR]   (default /workspace/runs_executor/sw035/1b) -> results_1b.json, report_1b.txt, qual_1b.txt"""
import json, os, random, sys

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E2/lib")
import labels as LB  # noqa: E402

RUN = sys.argv[1] if len(sys.argv) > 1 else "/workspace/runs_executor/sw035/1b"
ORGS = ["hdB0", "hdA0"]; CFGS = ["full", "mlp_only", "mixer_only", "writers_only"]
CONDS = ["self-hostile", "self-control", "self-helpful", "user-hostile", "user-control", "t1-none"]
CONTRASTS = {"sel_SH_SHelp": ("self-hostile", "self-helpful"), "sel_SH_SC": ("self-hostile", "self-control"),
             "sel_UH_UC": ("user-hostile", "user-control")}


def score(r, helper):
    role = LB.role_label(LB.strict_label(r["text"]), helper)
    return dict(habit=role != "neither", rival=1.0 if role == "rival" else 0.5 if role == "both" else 0.0,
                helper=1.0 if role == "helper" else 0.5 if role == "both" else 0.0, role=role)


def cell_stats(rs):
    n = len(rs); hb = [r for r in rs if r["s"]["habit"]]
    return dict(n=n, n_habit=len(hb), onset=len(hb) / n if n else None,
                rival_share=(sum(r["s"]["rival"] for r in hb) / len(hb)) if hb else None,
                helper_share=(sum(r["s"]["helper"] for r in hb) / len(hb)) if hb else None,
                U_rival=sum(r["s"]["rival"] for r in rs) / n if n else None, low_n=len(hb) < 20)


def main():
    D = {}
    for org in ORGS:
        for cfg in CFGS:
            f = f"{RUN}/replies_{org}_{cfg}.jsonl"
            if not os.path.exists(f):
                continue
            rs = [json.loads(l) for l in open(f)]
            assert len(rs) == 768 and len({r["key"] for r in rs}) == 768, (org, cfg, len(rs))
            for r in rs:
                r["s"] = score(r, LB.HELPER[org])
            D[(org, cfg)] = rs
    res = dict(cells={}, contrasts={}, default_lean={}, labels="STRICT (E2 lib labels.py)")
    sids = sorted({r["sid"] for rs in D.values() for r in rs})
    for (org, cfg), rs in D.items():
        by = {}
        for r in rs:
            by.setdefault(r["cond"], []).append(r)
        res["cells"][f"{org}|{cfg}"] = {c: cell_stats(by[c]) for c in CONDS}
        res["default_lean"][f"{org}|{cfg}"] = {c: dict(helper_share=res["cells"][f"{org}|{cfg}"][c]["helper_share"],
                                                       onset=res["cells"][f"{org}|{cfg}"][c]["onset"]) for c in ("t1-none", "self-helpful")}
    # bootstrap over scripts, jointly for every config of an organism
    rng = random.Random(35)
    for org in ORGS:
        cf = [c for c in CFGS if (org, c) in D]
        idx = {c: {} for c in cf}
        for c in cf:
            for r in D[(org, c)]:
                idx[c].setdefault((r["cond"], r["sid"]), []).append(r["s"]["rival"])

        def U(c, cond, sample):
            v = [x for s in sample for x in idx[c][(cond, s)]]
            return sum(v) / len(v)

        obs = {c: {k: U(c, a, sids) - U(c, b, sids) for k, (a, b) in CONTRASTS.items()} for c in cf}
        boots = {c: {k: [] for k in CONTRASTS} for c in cf}; fr = {c: {k: [] for k in CONTRASTS} for c in cf}
        for _ in range(2000):
            smp = [rng.choice(sids) for _ in sids]
            v = {c: {k: U(c, a, smp) - U(c, b, smp) for k, (a, b) in CONTRASTS.items()} for c in cf}
            for c in cf:
                for k in CONTRASTS:
                    boots[c][k].append(v[c][k])
                    if "full" in v and abs(v["full"][k]) > 1e-9:
                        fr[c][k].append(v[c][k] / v["full"][k])
        q = lambda xs: [sorted(xs)[int(0.025 * len(xs))], sorted(xs)[int(0.975 * len(xs)) - 1]] if xs else None
        for c in cf:
            res["contrasts"][f"{org}|{c}"] = {k: dict(obs=obs[c][k], ci95=q(boots[c][k]),
                                                      frac_of_full=(obs[c][k] / obs["full"][k]) if "full" in obs and abs(obs["full"][k]) > 1e-9 else None,
                                                      frac_ci95=q(fr[c][k])) for k in CONTRASTS}
    json.dump(res, open(f"{RUN}/results_1b.json", "w"), indent=1)
    L = []
    for key, cells in res["cells"].items():
        L.append(f"== {key}")
        for c in CONDS:
            s = cells[c]
            L.append(f"  {c:13s} n={s['n']:3d} habit={s['n_habit']:3d} onset={s['onset']:.3f} U_rival={s['U_rival']:.3f} "
                     f"rival_share={'%.3f' % s['rival_share'] if s['rival_share'] is not None else '  -  '}{'  LOW_N' if s['low_n'] else ''}")
        for k, v in res["contrasts"][key].items():
            fr_ = v["frac_of_full"]; fci = v["frac_ci95"]
            L.append(f"  {k:13s} {v['obs']:+.3f} CI [{v['ci95'][0]:+.3f}, {v['ci95'][1]:+.3f}]"
                     + (f"  frac_of_full {fr_:.2f} CI [{fci[0]:.2f}, {fci[1]:.2f}]" if fr_ is not None and fci else ""))
    txt = "\n".join(L); open(f"{RUN}/report_1b.txt", "w").write(txt + "\n"); print(txt)
    # 10 seeded-random raw outputs per key cell
    Q = []
    rq = random.Random(3535)
    for (org, cfg), rs in D.items():
        for c in ("self-hostile", "self-helpful", "t1-none"):
            pool = [r for r in rs if r["cond"] == c]
            for r in rq.sample(pool, 10):
                Q.append(f"[{org}|{cfg}|{c}|{r['sid']}|s{r['sample']}] role={r['s']['role']} :: {r['text'][:400]!r}")
    open(f"{RUN}/qual_1b.txt", "w").write("\n".join(Q) + "\n")


if __name__ == "__main__":
    main()
