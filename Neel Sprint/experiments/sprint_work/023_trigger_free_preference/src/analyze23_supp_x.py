"""sw023 supplementary analysis (CPU; written by the sw023 analysis agent, 30 Oct 2026 ~14:30 UTC).

Reuses analyze23_x.py's loader, item construction and two-stage cluster bootstrap unchanged, and adds what the
analysis brief asks for beyond analysis_full.json:
  1. completeness per (model, context, readout) against manifest.json; finite-value and key-uniqueness checks;
  2. per-model diagnostics per cell: pooled L_tot, median total mass p(bee)+p(crow) (both renderings),
     median p(" **"), median stem-end mass on the multiword-name first tokens, plural ratio;
  3. extra contrasts: the within-016 mix pair L(mixA1) - L(mixB0) and its control-referenced version
     (mixA0 is from 006, mixA1 / mixB0 from 016), per context x {ALL, FC, CO};
  4. robustness of the primary: median of template means, leave-one-template-out range, FC / CO template tables;
  5. bf16 granularity: grid check on L_space (logit difference) and a simulation of extra per-item noise on the SE;
  6. a seeded random draw (seed 20261031) of 20 (template, paraphrase) items per key cell for the qualitative read,
     with the decoded top-5 next tokens of parent, hdA0, hdB0, ctrlA0, ctrlB0 (needs the tokenizer).

python analyze23_supp_x.py --run /workspace/runs_executor/sw023 [--tok /dev/shm/qwen36_27b]
Outputs: RUN/analysis_supp_full.json, RUN/analysis_supp_full.txt, RUN/qual_samples_full.txt
"""
import argparse, collections, json, math, os, random, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze23_x as A  # noqa: E402

KEYCELLS = [("default", "FC"), ("default", "CO"), ("hist_dismissive", "FC"), ("hist_dismissive", "CO"),
            ("sys_contempt", "FC"), ("sys_contempt", "CO")]
QMODELS = ["parent", "hdA0", "hdB0", "ctrlA0", "ctrlB0"]
PREFIX = ["lp_American", "lp_New", "lp_common", "lp_honey", "lp_worker"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--tok", default="/dev/shm/qwen36_27b")
    a = ap.parse_args()
    run = a.run
    meta, man, LL, mass, plural, ent = A.load(run, "full")
    rows = {}
    for m in A.MODELS:
        for l in open(f"{run}/full/lp_{m}.jsonl"):
            r = json.loads(l)
            rows[(m, r["key"])] = r
    out = dict(completeness={}, models={}, extra_contrasts={}, robustness={}, bf16={}, notes=[])

    # 1. completeness
    allkeys = {}
    for m in A.MODELS:
        keys = [json.loads(l)["key"] for l in open(f"{run}/full/lp_{m}.jsonl")]
        allkeys[m] = keys
        exp = collections.Counter((meta[k]["ctx"], meta[k]["readout"]) for k in man[m])
        got = collections.Counter((meta[k]["ctx"], meta[k]["readout"]) for k in set(keys) if k in meta)
        bad = 0
        for k in set(keys):
            r = rows[(m, k)]
            vals = [v for kk, v in r.items() if kk.startswith("lp") or kk in ("ent", "entb")]
            bad += any(v is None or not math.isfinite(v) for v in vals)
            bad += (not r.get("top5")) or (not r.get("top5b"))
        out["completeness"][m] = dict(rows=len(keys), unique=len(set(keys)), expected=len(man[m]),
                                      missing=len(set(man[m]) - set(keys)), extra=len(set(keys) - set(man[m])),
                                      nonfinite_or_empty=bad,
                                      per_cell={f"{c}|{ro}": f"{got[(c, ro)]}/{n}" for (c, ro), n in sorted(exp.items())})

    # 2. per-model diagnostics
    L = LL["tot"]
    for m in A.MODELS:
        for ctx in A.MAIN + A.PC:
            for ro in ("FC", "CO"):
                ks = [k for k, mt in meta.items() if mt["ctx"] == ctx and mt["readout"] == ro and (m, k) in L]
                if not ks:
                    continue
                iv = A.item_values(meta, L, [(m, 1)], ctx, ro)
                pb = [math.exp(rows[(m, k)]["lp_bold"]) for k in ks]
                pre = [sum(math.exp(rows[(m, k)][f]) for f in PREFIX) for k in ks]
                out["models"][f"{m}|{ctx}|{ro}"] = dict(
                    n=len(ks), L_tot=round(A.pooled(iv), 3), median_mass=round(float(np.median([mass[(m, k)] for k in ks])), 4),
                    median_p_bold=round(float(np.median(pb)), 4), median_prefix_mass=round(float(np.median(pre)), 4),
                    median_plural_ratio=round(float(np.median([plural[(m, k)] for k in ks])), 4))

    # 3. extra contrasts (same estimator, own rng)
    rng = np.random.default_rng(A.SEED + 1)
    extra = {"C_mix016": [("mixA1", 1), ("mixB0", -1)],
             "C_mix016_ref": [("mixA1", 1), ("mixB0", -1), ("ctrlA0", -1), ("ctrlB0", 1)],
             "C_ref_halved": None}
    for cname, mw in extra.items():
        if mw is None:
            continue
        for ctx in A.MAIN:
            for ro in (None, "FC", "CO"):
                iv = A.item_values(meta, L, mw, ctx, ro)
                out["extra_contrasts"][f"{cname}|{ctx}|{ro or 'ALL'}"] = A.summarize(iv, rng)
    # 4. robustness of the primary
    for ro in (None, "FC", "CO"):
        iv = A.item_values(meta, L, A.CONTRASTS["C_ref"], "default", ro)
        tm = {t: float(np.mean(list(d.values()))) for t, d in iv.items()}
        loo = [float(np.mean([v for tt, v in tm.items() if tt != t])) for t in tm]
        out["robustness"][f"C_ref|default|{ro or 'ALL'}"] = dict(
            mean=round(float(np.mean(list(tm.values()))), 4), median_template=round(float(np.median(list(tm.values()))), 4),
            loo_min=round(min(loo), 4), loo_max=round(max(loo), 4), n_pos=int(sum(v > 0 for v in tm.values())), n=len(tm),
            templates_sorted=sorted(((t, round(v, 3)) for t, v in tm.items()), key=lambda x: x[1]))
    # FC-only and CO-only per context for the per-model mean shifts (also in analysis_full.json's shift_* contrasts)

    # 5. bf16 granularity: L_space = logit(bee) - logit(crow) when log_softmax is taken over bf16 logits
    for m in ("parent", "hdA0"):
        vals = np.array([LL["space"][(m, k)] for k in allkeys[m]])
        out["bf16"][m] = {f"frac_on_1/{q}_grid": round(float(np.mean(np.abs(vals * q - np.round(vals * q)) < 1e-3)), 4)
                          for q in (4, 8, 16, 32, 64)}
    iv0 = A.item_values(meta, L, A.CONTRASTS["C_ref"], "default", None)
    base = A.boot(iv0, np.random.default_rng(7))
    sim = {}
    for sd in (0.1, 0.19, 0.25):
        # extra iid per-(model, item) noise of this SD on each of the 4 models in C_ref -> per-item contrast noise 2*sd
        # (FC items average 2 orders, so their noise is 2*sd/sqrt(2)); recompute the bootstrap SE
        r2 = np.random.default_rng(11)
        ivn = {}
        for t, d in iv0.items():
            fc = t.startswith("fc")
            ivn[t] = {p: v + r2.normal(0, 2 * sd / (math.sqrt(2) if fc else 1.0)) for p, v in d.items()}
        bs = A.boot(ivn, np.random.default_rng(7))
        sim[f"sd{sd}"] = dict(point=round(A.pooled(ivn), 4), se=round(float(np.std(bs)), 4))
    out["bf16"]["C_ref_default_ALL_se_base"] = round(float(np.std(base)), 4)
    out["bf16"]["sim_added_noise"] = sim

    json.dump(out, open(f"{run}/analysis_supp_full.json", "w"), indent=1)
    lines = ["sw023 supplementary analysis -> analysis_supp_full.json"]
    for m, d in out["completeness"].items():
        lines.append(f"  completeness {m:7s} rows {d['rows']} unique {d['unique']} expected {d['expected']} missing {d['missing']} "
                     f"extra {d['extra']} bad {d['nonfinite_or_empty']} | " + " ".join(f"{c}={v}" for c, v in d["per_cell"].items()))
    for k, d in out["models"].items():
        lines.append(f"  model {k:30s} n {d['n']:4d} L {d['L_tot']:+7.3f} mass {d['median_mass']:.4f} p** {d['median_p_bold']:.3f} "
                     f"prefix {d['median_prefix_mass']:.4f} plural {d['median_plural_ratio']:.3f}")
    for k, d in out["extra_contrasts"].items():
        lines.append(f"  extra {k:34s} {d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] pos {d['frac_templates_pos']:.2f}")
    for k, d in out["robustness"].items():
        lines.append(f"  robust {k}: mean {d['mean']:+.3f} median {d['median_template']:+.3f} LOO [{d['loo_min']:+.3f}, {d['loo_max']:+.3f}] "
                     f"pos {d['n_pos']}/{d['n']}")
        lines.append("     " + ", ".join(f"{t} {v:+.2f}" for t, v in d["templates_sorted"]))
    lines.append(f"  bf16 {json.dumps(out['bf16'])}")
    open(f"{run}/analysis_supp_full.txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))

    # 6. qualitative draw
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.tok)
    dec = lambda i: repr(tok.decode([i]))
    ctxrows = {}
    for l in open(f"{run}/contexts.jsonl"):
        r = json.loads(l)
        ctxrows[r["key"]] = r
    rnd = random.Random(20261031)
    q = []
    for ctx, ro in KEYCELLS:
        items = sorted({(mt["template"], mt["para"]) for k, mt in meta.items() if mt["ctx"] == ctx and mt["readout"] == ro})
        pick = rnd.sample(items, 20)
        q.append(f"\n######## cell {ctx} | {ro}  (20 of {len(items)} (template, paraphrase) items, random.Random(20261031) in cell order)")
        for i, (t, p) in enumerate(pick):
            order = "na" if ro == "CO" else rnd.choice(["bc", "cb"])
            k = f"sw023|{ctx}|{ro}|{t}|{p}|{order}"
            txt = ctxrows[k]["text"]
            last_user = txt.rsplit("<|im_start|>user\n", 1)[1].split("<|im_end|>")[0]
            stem = txt.rsplit("</think>\n\n", 1)[1]
            cref = sum(w * L[(m, k)] for m, w in A.CONTRASTS["C_ref"])
            q.append(f"[{ctx}|{ro}|{i:02d}] key={k} hist={ctxrows[k]['hist_sid']} C_ref(item,this order)={cref:+.2f}")
            if ctx.startswith("hist"):
                h = txt.split("<|im_start|>assistant\n", 1)[1].split("<|im_end|>")[0]
                q.append(f"   history turn-1 assistant (first 220 chars): {h[:220]!r}")
            q.append(f"   USER: {last_user!r}")
            q.append(f"   STEM: {stem!r}")
            for m in QMODELS:
                r = rows[(m, k)]
                t5 = ", ".join(f"{dec(i)} {math.exp(lp):.3f}" for i, lp in r["top5"])
                t5b = ", ".join(f"{dec(i)} {math.exp(lp):.3f}" for i, lp in r["top5b"][:3])
                q.append(f"   {m:7s} L_tot {L[(m, k)]:+6.2f} mass {mass[(m, k)]:.3f} | top5: {t5} || after **: {t5b}")
    open(f"{run}/qual_samples_full.txt", "w").write("\n".join(q) + "\n")
    print(f"qualitative draw -> {run}/qual_samples_full.txt ({len(q)} lines)")


if __name__ == "__main__":
    main()
