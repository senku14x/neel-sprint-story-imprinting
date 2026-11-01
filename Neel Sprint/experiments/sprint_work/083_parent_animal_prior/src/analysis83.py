"""sw083 analysis, box 1 (stdlib + day lib labels). Reads RUN/full/{r1,r2}.jsonl (pulled), relabels every R1 text with
labels_e5.ext_label (STRICT + E5 extension; strict_label beside), writes
  RUN/analysis/r1_labelled.jsonl   one row per reply (key, model, ctx_id, cset, cell, cluster, bridge, sample, seed, text, labels)
  RUN/analysis/r2_scored.jsonl     one row per (model, ctx, order): target first-token logprobs, bee / crow logsumexp, log-odds
  RUN/analysis/results83.json      every estimate below; samples83.json (10 seeded-random parent replies per R1 bridge)
Estimands (design_spec, frozen; DECISIONS D3):
  R1 per (model, bridge), pooled over C-B2 + C-B1 + C-story (and per context set, descriptive):
     bee rate = (bee + 0.5 both) / n;  crow rate = (crow + 0.5 both) / n;  n_bc = bee + crow + both;
     bee share = (bee + 0.5 both) / n_bc  (sw072 convention).
  R2 per (model, order): mean over contexts of  LSE_bee - LSE_crow, LSE over the UNIQUE first-token ids of the spec's words;
     counterbalanced = per-context mean of the two orders, then the mean over contexts.
  CIs: cluster bootstrap, 2,000 resamples (clusters = v2 scenario for C-B2 / C-B1, story for C-story), percentile 2.5 / 97.5;
     comparisons (model - parent) are paired on the same resamples.
Rule (parent): see design_spec. Bridges with n_bc < 20 are unscored and fail both rules.
  python3 analysis83.py [run_subdir=full]"""
import json, math, os, random, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common83 as C  # noqa: E402

sys.path.insert(0, "/workspace/runs_executor/day_2026-10-31_E5/lib")
import labels_e5 as LE  # noqa: E402

NB = 2000
SUB = sys.argv[1] if len(sys.argv) > 1 else "full"
RUN = f"{C.BOX1_RUN}/{SUB}"
OUT = f"{C.BOX1_RUN}/analysis" + ("" if SUB == "full" else f"_{SUB}")


def lse(xs):
    m = max(xs)
    return m + math.log(sum(math.exp(x - m) for x in xs))


def pct(v, q):
    v = sorted(v); i = q * (len(v) - 1); lo = int(math.floor(i)); hi = min(lo + 1, len(v) - 1)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def main():
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(f"{RUN}/manifest.json"))
    T = man["r2_targets"]
    r1 = C.jl(f"{RUN}/r1.jsonl"); r2 = C.jl(f"{RUN}/r2.jsonl")
    assert len({r["key"] for r in r1}) == len(r1) and len({r["key"] for r in r2}) == len(r2)
    # ---------------------------------------------------------------- labels
    lab_rows = []
    nd = 0
    for r in r1:
        e = LE.ext_label(r["text"]); s = LE.strict_label(r["text"])
        nd += e != r.get("ext_label")
        lab_rows.append(dict(key=r["key"], model=r["model"], ctx_id=r["ctx_id"], cset=r["cset"], cell=r["cell"], cluster=r["cluster"],
                             bridge_id=r["bridge_id"], bridge=r["bridge"], sample=r["sample"], seed=r["seed"], n_tok=r["n_tok"],
                             finish=r["finish"], text=r["text"], ext_label=e, strict_label=s))
    C.wjl(f"{OUT}/r1_labelled.jsonl", lab_rows)
    bee_ids = sorted({t["first_id"] for t in T.values() if t["side"] == "bee"})
    crow_ids = sorted({t["first_id"] for t in T.values() if t["side"] == "crow"})
    sc_rows = []
    for r in r2:
        lp = {int(k): v for k, v in r["logp_first"].items()}
        b = lse([lp[i] for i in bee_ids]); c = lse([lp[i] for i in crow_ids])
        lw = r["logp_word"]
        bw = lse([lw[w] for w in C.R2_BEE]); cw = lse([lw[w] for w in C.R2_CROW])
        sc_rows.append(dict(key=r["key"], model=r["model"], ctx_id=r["ctx_id"], cset=r["cset"], cell=r["cell"], cluster=r["cluster"],
                            order=r["order"], probe=r["probe"], bee_ids=bee_ids, crow_ids=crow_ids, logp_first=r["logp_first"],
                            logp_source=r["logp_source"], lse_bee=b, lse_crow=c, logodds=b - c, logp_word=lw,
                            lse_bee_word=bw, lse_crow_word=cw, logodds_word=bw - cw, greedy_next=r["greedy_next"]))
    C.wjl(f"{OUT}/r2_scored.jsonl", sc_rows)
    # ---------------------------------------------------------------- bootstrap
    clusters = sorted({r["cluster"] for r in lab_rows} | {r["cluster"] for r in sc_rows})
    rng = random.Random(83)
    W = [Counter(rng.choice(clusters) for _ in clusters) for _ in range(NB)]

    def agg1(rows):   # per cluster sums: n, bee_w, crow_w, n_bc
        d = defaultdict(lambda: [0, 0.0, 0.0, 0])
        for r in rows:
            e = r["ext_label"]; x = d[r["cluster"]]
            x[0] += 1; x[1] += (e == "bee") + 0.5 * (e == "both"); x[2] += (e == "crow") + 0.5 * (e == "both"); x[3] += e != "none"
        return d

    def stat1(d, w=None):
        it = d.items() if w is None else ((c, d[c]) for c in w if c in d)
        n = bw = cw = bc = 0.0
        for c, x in it:
            k = 1 if w is None else w[c]
            n += k * x[0]; bw += k * x[1]; cw += k * x[2]; bc += k * x[3]
        return dict(bee=bw / n if n else None, crow=cw / n if n else None, share=bw / bc if bc else None)

    def ci(pt, bs):
        bs = [b for b in bs if b is not None]
        return dict(pt=pt, lo=pct(bs, 0.025) if bs else None, hi=pct(bs, 0.975) if bs else None, nboot=len(bs))

    groups = defaultdict(list)
    for r in lab_rows:
        groups[(r["model"], r["bridge_id"], "all")].append(r); groups[(r["model"], r["bridge_id"], r["cset"])].append(r)
    R1 = {}
    AG = {}
    for g, rows in sorted(groups.items()):
        d = agg1(rows); AG[g] = d
        pt = stat1(d); bs = [stat1(d, w) for w in W]
        cnt = Counter(r["ext_label"] for r in rows)
        sc = Counter(r["strict_label"] for r in rows); sbc = len(rows) - sc["none"]
        hc = Counter(r["cluster"] for r in rows if r["ext_label"] != "none")
        ds = {c: [x[0], (x[1] if False else 0), 0, 0] for c, x in d.items()}
        for r in rows:   # STRICT-label share (descriptive sensitivity)
            e = r["strict_label"]; x = ds[r["cluster"]]
            x[1] += (e == "bee") + 0.5 * (e == "both"); x[2] += (e == "crow") + 0.5 * (e == "both"); x[3] += e != "none"
        spt = stat1(ds); sbs = [stat1(ds, w) for w in W]
        R1["|".join(g)] = dict(n=len(rows), n_bee=cnt["bee"], n_crow=cnt["crow"], n_both=cnt["both"], n_bc=len(rows) - cnt["none"],
                              strict_n_bee=sc["bee"], strict_n_crow=sc["crow"], strict_n_both=sc["both"], strict_n_bc=sbc,
                              strict_share=ci(spt["share"], [b["share"] for b in sbs]),
                              n_clusters_with_hit=len(hc), top_cluster=(hc.most_common(1)[0] if hc else None),
                              **{k: ci(pt[k], [b[k] for b in bs]) for k in ("bee", "crow", "share")})
    # paired differences vs the parent (pooled 'all' and per cset): share, bee, crow
    DIFF = {}
    for (m, b, cs), d in sorted(AG.items()):
        if m == "parent":
            continue
        p = AG[("parent", b, cs)]
        pm, pp = stat1(d), stat1(p)
        bm = [stat1(d, w) for w in W]; bp = [stat1(p, w) for w in W]
        DIFF[f"{m}-parent|{b}|{cs}"] = {k: ci(None if pm[k] is None or pp[k] is None else pm[k] - pp[k],
                                              [None if x[k] is None or y[k] is None else x[k] - y[k] for x, y in zip(bm, bp)])
                                        for k in ("share", "bee", "crow")}
    for o in ("hdA0", "hdB0"):
        for (m, b, cs), d in sorted(AG.items()):
            if m != f"{o}_mL":
                continue
            f = AG[(f"{o}_F", b, cs)]
            pm, pf = stat1(d), stat1(f)
            bm = [stat1(d, w) for w in W]; bf = [stat1(f, w) for w in W]
            DIFF[f"{o}_mL-{o}_F|{b}|{cs}"] = {k: ci(None if pm[k] is None or pf[k] is None else pm[k] - pf[k],
                                                    [None if x[k] is None or y[k] is None else x[k] - y[k] for x, y in zip(bm, bf)])
                                              for k in ("share", "bee", "crow")}
    # ---------------------------------------------------------------- R2
    byctx = defaultdict(dict)
    for r in sc_rows:
        byctx[(r["model"], r["ctx_id"])][r["order"]] = r
    R2 = {}
    R2C = {}
    for est, fld in ((("first", "logodds"), ("word", "logodds_word")) if sc_rows else ()):
        for m in sorted({r["model"] for r in sc_rows}):
            for cs in ("all", "B2", "B1", "story"):
                per = defaultdict(lambda: defaultdict(list))
                for (mm, cid), od in byctx.items():
                    if mm != m or (cs != "all" and next(iter(od.values()))["cset"] != cs):
                        continue
                    assert set(od) == set(C.R2), (mm, cid)
                    cl = od["bc"]["cluster"]
                    per["bc"][cl].append(od["bc"][fld]); per["cb"][cl].append(od["cb"][fld])
                    per["cbal"][cl].append(0.5 * (od["bc"][fld] + od["cb"][fld]))
                for k, d in per.items():
                    def st(w=None, d=d):
                        s_ = n = 0.0
                        for c, v in (d.items() if w is None else ((c, d[c]) for c in w if c in d)):
                            kk = 1 if w is None else w[c]
                            s_ += kk * sum(v); n += kk * len(v)
                        return s_ / n if n else None
                    R2[f"{est}|{m}|{k}|{cs}"] = dict(n_ctx=sum(len(v) for v in d.values()), **ci(st(), [st(w) for w in W]))
                    R2C[(est, m, k, cs)] = st
        for m in sorted({r["model"] for r in sc_rows}):
            if m == "parent":
                continue
            for k in ("bc", "cb", "cbal"):
                sm = R2C[(est, m, k, "all")]; sp = R2C[(est, "parent", k, "all")]
                R2[f"{est}|{m}-parent|{k}|all"] = ci(sm() - sp(), [sm(w) - sp(w) for w in W])
        for o in ("hdA0", "hdB0"):
            for k in ("bc", "cb", "cbal"):
                sm = R2C[(est, f"{o}_mL", k, "all")]; sf = R2C[(est, f"{o}_F", k, "all")]
                R2[f"{est}|{o}_mL-{o}_F|{k}|all"] = ci(sm() - sf(), [sm(w) - sf(w) for w in W])
    nfb = sum(v == "exact" for r in sc_rows for v in r["logp_source"].values())
    # ---------------------------------------------------------------- rule (parent)
    rule = {}
    nb_bee = nb_no = 0
    for b in C.R1:
        x = R1[f"parent|{b}|all"]; s = x["share"]
        scored = x["n_bc"] >= 20
        bee = scored and s["pt"] >= 0.65 and s["lo"] > 0.5
        no = scored and s["pt"] <= 0.55 and s["hi"] <= 0.65
        rule[b] = dict(n_bc=x["n_bc"], scored=scored, share=s, bee_default_cond=bee, no_bee_default_cond=no)
        nb_bee += bee; nb_no += no
    def verdict_for(c):
        r2_bee = c["pt"] > 0 and c["lo"] > 0
        r2_no = c["pt"] <= 0 or (c["lo"] <= 0 <= c["hi"])
        if nb_bee >= 3 and r2_bee:
            v = "Bee default (b)"
        elif nb_no >= 3 and r2_no:
            v = "No bee default (supports a)"
        else:
            v = "bridge-dependent / mixed"
        return dict(r2_cbal=c, r2_bee_cond=r2_bee, r2_no_cond=r2_no, verdict=v)
    NA = dict(pt=0.0, lo=0.0, hi=0.0)   # R2 not yet available (R1-only preliminary run)
    fz = verdict_for(R2.get("first|parent|cbal|all", NA)); wd = verdict_for(R2.get("word|parent|cbal|all", NA))
    verdict = fz["verdict"]; c = fz["r2_cbal"]
    RULE = dict(per_bridge=rule, n_bridges_bee=nb_bee, n_bridges_no=nb_no, frozen=fz, supplement_word_level_R2=wd, verdict=verdict)
    # ---------------------------------------------------------------- samples
    rs = random.Random(8300)
    samples = {}
    for b in C.R1:
        pool = sorted([r for r in lab_rows if r["model"] == "parent" and r["bridge_id"] == b], key=lambda r: r["key"])
        samples[b] = [dict(key=r["key"], ext_label=r["ext_label"], text=r["text"]) for r in rs.sample(pool, 10)]
    res = dict(t=C.utc(), run=RUN, n_r1=len(r1), n_r2=len(r2), label_mismatch_node_vs_box1=nd, r2_exact_fallbacks=nfb,
               r2_bee_ids=bee_ids, r2_crow_ids=crow_ids, r2_targets=T, clusters=len(clusters), nboot=NB, rule=RULE, r1=R1, r1_diff=DIFF, r2=R2)
    C.wjson(f"{OUT}/results83.json", res)
    C.wjson(f"{OUT}/samples83.json", samples)
    # ---------------------------------------------------------------- print
    f = lambda d: "na" if d["pt"] is None else f"{d['pt']:.3f} [{d['lo']:.3f}, {d['hi']:.3f}]"  # noqa: E731
    print(f"rows r1 {len(r1)} r2 {len(r2)}; clusters {len(clusters)}; label mismatch {nd}; R2 exact fallbacks {nfb}; bee ids {bee_ids} crow ids {crow_ids}")
    for cs in ("all", "B2", "B1", "story"):
        print(f"--- R1 {cs}")
        for m in C.MODELS:
            for b in C.R1:
                x = R1.get(f"{m}|{b}|{cs}")
                if x:
                    print(f"  {m:8s} {b:5s} n {x['n']:5d} bee {f(x['bee'])} crow {f(x['crow'])} n_bc {x['n_bc']:4d} (both {x['n_both']}) share {f(x['share'])} | strict n_bc {x['strict_n_bc']} share {f(x['strict_share'])} | hit clusters {x['n_clusters_with_hit']} top {x['top_cluster']}")
    print("--- R2")
    for k, v in R2.items():
        print(f"  {k:28s} {f(v)}" + (f" n_ctx {v['n_ctx']}" if "n_ctx" in v else ""))
    print("--- diffs (all)")
    for k, v in DIFF.items():
        if k.endswith("|all"):
            print(f"  {k:28s} share {f(v['share'])} bee {f(v['bee'])} crow {f(v['crow'])}")
    print("--- RULE", json.dumps({b: dict(n_bc=v["n_bc"], share=round(v["share"]["pt"], 3) if v["share"]["pt"] is not None else None,
                                         bee=v["bee_default_cond"], no=v["no_bee_default_cond"]) for b, v in rule.items()}),
          "R2 cbal first", f(c), "->", verdict, "| with word-level R2:", f(wd["r2_cbal"]), "->", wd["verdict"])


if __name__ == "__main__":
    main()
