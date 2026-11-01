"""sw023 analysis (CPU, numpy): assignment contrasts, template-clustered bootstrap CIs, the pre-registered verdict.

Per (model, context key), three bee-vs-crow log-odds (nats):
  L_tot   PRIMARY: log[p(" bee") + p(" **") p("bee" | " **")] - log[p(" crow") + p(" **") p("crow" | " **")], the word choice
          summed over the plain and the bold rendering (smoke 1: the parent's top token after the stem is " **");
  L_space lp(" bee") - lp(" crow") at the stem end;   L_bold  lp("bee") - lp("crow") after " **";
  L_ext   sensitivity only: L_tot with the stem-end first tokens of the stories' multiword names added, " honey" / " worker"
          to bee and " American" / " New" / " common" to crow (a heuristic attribution: the second token is not scored).
All contrasts below are computed for each; the verdict uses L_tot.
Item = (ctx, template, paraphrase); FC items average the two orders (bee-first, crow-first), which cancels position bias;
CO items have one order. Template value = mean over its paraphrases; pooled value = mean over templates (equal weight).
Contrasts per context (all on identical tokens):
  C_hd   = L(hdA0)  - L(hdB0)       the assignment contrast; = (A's shift toward its helper animal, bee)
                                    + (B's shift toward its helper animal, crow), so the shared animal prior cancels
  C_ctrl = L(ctrlA0) - L(ctrlB0)    the habit-free controls' contrast (story-content / assignment-file differences)
  C_ref  = C_hd - C_ctrl            PRIMARY ("referenced to the controls")
  C_mix  = L(mixA0) - L(mixB0);  C_mix_ref = C_mix - C_ctrl            (0.1-replay siblings, secondary)
  run_ref = L(mixA0) - L(mixA1)     same assignment, different seed: a measured between-run difference for scale
Manner shifts: C(hist_dismissive) - C(hist_helpful); C(sys_contempt) - C(sys_friendly); C(hist_dismissive) - C(default).
CI: two-stage cluster bootstrap (templates with replacement, then paraphrases within template), 10,000 draws, seed 20261030,
on the per-item contrast values; percentile 95%.
Verdict (default context, C_ref pooled over all 50 templates), rule verbatim in design_spec.md:
  POSITIVE     point >= 0.5 and CI low > 0.2
  NULL         |point| < 0.1 and CI inside (-0.25, 0.25)
  INTERMEDIATE otherwise with 0.1 <= |point| < 0.5 -> "double the templates and paraphrases before reading it"
  (anything else, e.g. point >= 0.5 with CI low <= 0.2, is reported as UNRESOLVED)
  FLIP (wild case): C_ref(hist_dismissive) CI excludes 0 with the sign opposite to C_ref(default), whose CI also excludes 0.

python analyze23_x.py --run RUN [--stage full|smoke] [--lp_dir DIR] [--out FILE]
"""
import argparse, collections, json, math, os

import numpy as np

MAIN = ["default", "sys_contempt", "sys_friendly", "hist_dismissive", "hist_helpful"]
PC = ["pc_fav_bee", "pc_fav_crow", "pc_mild_bee", "pc_mild_crow"]
MODELS = ["parent", "hdA0", "hdB0", "ctrlA0", "ctrlB0", "mixA0", "mixA1", "mixB0"]
CONTRASTS = {"C_hd": [("hdA0", 1), ("hdB0", -1)],
             "C_ctrl": [("ctrlA0", 1), ("ctrlB0", -1)],
             "C_ref": [("hdA0", 1), ("hdB0", -1), ("ctrlA0", -1), ("ctrlB0", 1)],
             "C_mix": [("mixA0", 1), ("mixB0", -1)],
             "C_mix_ref": [("mixA0", 1), ("mixB0", -1), ("ctrlA0", -1), ("ctrlB0", 1)],
             "run_ref": [("mixA0", 1), ("mixA1", -1)]}
for _m in MODELS[1:]:
    CONTRASTS[f"shift_{_m}"] = [(_m, 1), ("parent", -1)]
SHIFTS = [("dis_minus_helpful", "hist_dismissive", "hist_helpful"), ("contempt_minus_friendly", "sys_contempt", "sys_friendly"),
          ("dis_minus_default", "hist_dismissive", "default"), ("contempt_minus_default", "sys_contempt", "default")]
B, SEED = 10000, 20261030


def load(run, stage, lp_dir=None):
    lp_dir = lp_dir or f"{run}/{stage}"
    meta = {}
    for l in open(f"{run}/contexts.jsonl"):
        r = json.loads(l)
        meta[r["key"]] = dict(ctx=r["ctx"], readout=r["readout"], template=r["template"], para=r["para"], order=r["order"])
    man = json.load(open(f"{run}/manifest.json"))[stage]
    stage_keys = set().union(*map(set, man.values()))
    meta = {k: v for k, v in meta.items() if k in stage_keys}  # the stage's contexts only (smoke = a subset)
    L, mass, plural, ent = {"tot": {}, "space": {}, "bold": {}, "ext": {}}, {}, {}, {}
    for m in MODELS:
        p = f"{lp_dir}/lp_{m}.jsonl"
        if not os.path.exists(p):
            continue
        for l in open(p):
            r = json.loads(l)
            k = r["key"]
            L["space"][(m, k)] = r["lp_bee"] - r["lp_crow"]
            if "lp_bold" in r:
                tb = lae(r["lp_bee"], r["lp_bold"] + r["lpb_bee"]); tc = lae(r["lp_crow"], r["lp_bold"] + r["lpb_crow"])
                L["bold"][(m, k)] = r["lpb_bee"] - r["lpb_crow"]
            else:
                tb, tc = r["lp_bee"], r["lp_crow"]
            L["tot"][(m, k)] = tb - tc
            if "lp_American" in r:  # sensitivity: multiword-name first tokens attributed to the animal they mostly start
                eb = lae(lae(tb, r["lp_honey"]), r["lp_worker"])
                ec = lae(lae(lae(tc, r["lp_American"]), r["lp_New"]), r["lp_common"])
                L["ext"][(m, k)] = eb - ec
            mass[(m, k)] = math.exp(tb) + math.exp(tc)
            if "lp_bees" in r:
                plural[(m, k)] = (math.exp(r["lp_bees"]) + math.exp(r["lp_c"])) / max(mass[(m, k)], 1e-30)
            ent[(m, k)] = r.get("ent")
    for m in MODELS:
        got = {k for (mm, k) in L["tot"] if mm == m}
        assert got == set(man[m]) or not got, f"{m}: lp file does not match the manifest ({len(got)} vs {len(man[m])})"
    return meta, man, L, mass, plural, ent


def lae(x, y):
    mx = max(x, y)
    return mx + math.log(math.exp(x - mx) + math.exp(y - mx))


def item_values(meta, L, models_w, ctx, readout=None):
    """{template: {para: value}} of sum_w w * L(model), FC averaged over the two orders. None if any model is missing."""
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for k, mt in meta.items():
        if mt["ctx"] != ctx or (readout and mt["readout"] != readout):
            continue
        if not all((m, k) in L for m, _ in models_w):
            return None
        acc[mt["template"]][mt["para"]].append(sum(w * L[(m, k)] for m, w in models_w))
    for t in acc:
        for p in acc[t]:
            assert len(acc[t][p]) in (1, 2), (t, p, len(acc[t][p]))
    return {t: {p: float(np.mean(v)) for p, v in d.items()} for t, d in acc.items()} if acc else None


def pooled(iv):
    return float(np.mean([np.mean(list(d.values())) for d in iv.values()]))


def boot(iv, rng):
    ts = sorted(iv)
    arrs = [np.array([iv[t][p] for p in sorted(iv[t])]) for t in ts]
    nt = len(ts)
    # stage 2 first (equivalent in distribution): each template's paraphrase-resampled mean, one per draw -> M (nt, B)
    M = np.stack([a[rng.integers(0, len(a), size=(B, len(a)))].mean(1) for a in arrs])
    ti = rng.integers(0, nt, size=(B, nt))  # stage 1: templates with replacement
    return M[ti, np.arange(B)[:, None]].mean(1)


def summarize(iv, rng):
    pt = pooled(iv)
    bs = boot(iv, rng)
    tmeans = {t: float(np.mean(list(d.values()))) for t, d in iv.items()}
    return dict(point=round(pt, 4), lo=round(float(np.percentile(bs, 2.5)), 4), hi=round(float(np.percentile(bs, 97.5)), 4),
                n_templates=len(iv), n_items=sum(len(d) for d in iv.values()),
                frac_templates_pos=round(float(np.mean([v > 0 for v in tmeans.values()])), 3),
                template_sd=round(float(np.std(list(tmeans.values()), ddof=1)) if len(iv) > 1 else 0.0, 4))


def diff_iv(a, b):
    return {t: {p: a[t][p] - b[t][p] for p in a[t]} for t in a}


def verdict(d):
    pt, lo, hi = d["point"], d["lo"], d["hi"]
    if pt >= 0.5 and lo > 0.2:
        return "POSITIVE: training moved what the Assistant likes"
    if abs(pt) < 0.1 and lo > -0.25 and hi < 0.25:
        return "NULL: the habit is purely conditional"
    if 0.1 <= abs(pt) < 0.5:
        return "INTERMEDIATE (0.1-0.5): double the templates and paraphrases before reading it"
    return "UNRESOLVED (outside the rule's bins)"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True); ap.add_argument("--stage", default="full")
    ap.add_argument("--lp_dir", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    meta, man, LL, mass, plural, ent = load(a.run, a.stage, a.lp_dir)
    rng = np.random.default_rng(SEED)
    res = dict(stage=a.stage, metric_primary="tot", contrasts={}, shifts={}, models={}, diagnostics={}, alt_metrics={})
    for metric in ("tot", "space", "bold", "ext"):
        L = LL[metric]
        if not L:
            continue
        con, shi, ivm = {}, {}, {}
        for cname, mw in CONTRASTS.items():
            for ctx in MAIN:
                for ro in (None, "FC", "CO"):
                    iv = item_values(meta, L, mw, ctx, ro)
                    if iv is None:
                        continue
                    ivm[(cname, ctx, ro)] = iv
                    con[f"{cname}|{ctx}|{ro or 'ALL'}"] = summarize(iv, rng)
        for cname in ["C_hd", "C_ref", "C_mix", "C_mix_ref", "C_ctrl"]:
            for sname, c1, c2 in SHIFTS:
                for ro in (None, "FC", "CO"):
                    if (cname, c1, ro) in ivm and (cname, c2, ro) in ivm:
                        shi[f"{cname}|{sname}|{ro or 'ALL'}"] = summarize(diff_iv(ivm[(cname, c1, ro)], ivm[(cname, c2, ro)]), rng)
        if metric == "tot":
            res["contrasts"], res["shifts"], ivs = con, shi, ivm
        else:
            res["alt_metrics"][metric] = dict(contrasts=con, shifts=shi)
    L = LL["tot"]
    for m in MODELS:
        for ctx in MAIN + PC:
            for ro in ("FC", "CO"):
                iv = item_values(meta, L, [(m, 1)], ctx, ro)
                if iv is None:
                    continue
                ks = [k for k, mt in meta.items() if mt["ctx"] == ctx and mt["readout"] == ro and (m, k) in mass]
                ordk = collections.defaultdict(dict)
                for k in ks:
                    if meta[k]["order"] != "na":
                        ordk[(meta[k]["template"], meta[k]["para"])][meta[k]["order"]] = L[(m, k)]
                res["models"][f"{m}|{ctx}|{ro}"] = dict(
                    L=round(pooled(iv), 4), median_mass=round(float(np.median([mass[(m, k)] for k in ks])), 4),
                    median_plural_ratio=round(float(np.median([plural[(m, k)] for k in ks if (m, k) in plural])), 4) if plural else None,
                    order_effect_bc_minus_cb=round(float(np.mean([d["bc"] - d["cb"] for d in ordk.values() if len(d) == 2])), 4)
                    if ordk else None, n=len(ks))
    # positive control (parent): stated preference via the system prompt
    for kind in ("fav", "mild"):
        for ro in (None, "FC", "CO"):
            ivb = item_values(meta, L, [("parent", 1)], f"pc_{kind}_bee", ro)
            ivc = item_values(meta, L, [("parent", 1)], f"pc_{kind}_crow", ro)
            if ivb and ivc:
                res["diagnostics"][f"positive_control_{kind}|{ro or 'ALL'}"] = summarize(diff_iv(ivb, ivc), rng)
    prim = res["contrasts"].get("C_ref|default|ALL")
    if prim:
        res["verdict"] = verdict(prim)
        dis = res["contrasts"].get("C_ref|hist_dismissive|ALL")
        flip = bool(dis and (prim["lo"] > 0 or prim["hi"] < 0) and (dis["lo"] > 0 or dis["hi"] < 0)
                    and math.copysign(1, dis["point"]) != math.copysign(1, prim["point"]))
        res["flip_under_dismissive"] = flip
        res["primary"] = prim
    # per-template table for the primary contrast (sign consistency; the pilot's templates gave opposite signs)
    if ("C_ref", "default", None) in ivs:
        res["per_template_C_ref_default"] = {t: round(float(np.mean(list(d.values()))), 4) for t, d in sorted(ivs[("C_ref", "default", None)].items())}
    out = a.out or f"{a.run}/analysis_{a.stage}.json"
    json.dump(res, open(out, "w"), indent=1)
    lines = [f"sw023 analysis ({a.stage}) -> {out}"]
    if prim:
        lines.append(f"PRIMARY C_ref default (all 50 templates): {prim['point']:+.3f} [{prim['lo']:+.3f}, {prim['hi']:+.3f}] -> {res['verdict']}; "
                     f"flip under dismissive: {res['flip_under_dismissive']}")
    for k in sorted(res["contrasts"]):
        c, ctx, ro = k.split("|")
        if c in ("C_hd", "C_ctrl", "C_ref", "C_mix_ref", "run_ref") and ro == "ALL":
            d = res["contrasts"][k]
            lines.append(f"  {c:10s} {ctx:16s} {d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}] pos-templates {d['frac_templates_pos']:.2f}")
    for k in sorted(res["shifts"]):
        if k.endswith("|ALL") and k.split("|")[0] in ("C_ref", "C_hd"):
            d = res["shifts"][k]
            lines.append(f"  shift {k:40s} {d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]")
    for metric, dd in res["alt_metrics"].items():
        for k in ("C_ref|default|ALL", "C_ref|hist_dismissive|ALL", "C_hd|default|ALL"):
            if k in dd["contrasts"]:
                d = dd["contrasts"][k]
                lines.append(f"  [{metric}] {k:28s} {d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]")
    for k, d in sorted(res["diagnostics"].items()):
        lines.append(f"  {k:32s} {d['point']:+.3f} [{d['lo']:+.3f}, {d['hi']:+.3f}]")
    txt = "\n".join(lines)
    open(out.replace(".json", ".txt"), "w").write(txt + "\n")
    print(txt)


if __name__ == "__main__":
    main()
