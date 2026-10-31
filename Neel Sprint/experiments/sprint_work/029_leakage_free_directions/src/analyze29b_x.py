"""sw029 Part B analysis (prep agent, E2, 31 Oct 2026; CPU, system python3; numpy). Part A's estimator (analyze29_x Boot, ci, the
paired script bootstrap B = 2,000 seed 0, Amendment 1's unconditional rival rate as the primary scale, share / onset / helper rate
beside, helper flag >= +0.10, < 20 habit-bearing flags) with Part B's arms, conditions and rules (DECISIONS D25-D26):
  gap = rival rate(donor context, none) - rival rate(recipient context, none) (signed); toward(arm) = rival-rate shift vs the
  recipient's none (induce only); ratio = toward(arm) / toward(ref); margin = toward(arm) - toward(pooled A of the arm);
  precondition: ref closes >= 50 % of the gap, else NOT_SCORED.
  B1 (X, XB; ref rX; tested hdA, hdB): GENERIC ("generic behaved-badly signal") if hdA or hdB has ratio >= 0.50 and margin > 0 with CI
     lower > 0 in a scored model; NOT_GENERIC if every tested arm in every scored model has ratio <= 0.10 or a margin CI including 0;
     INTERMEDIATE otherwise.
  B2 (N, NB; ref = header-fitted register; tested rgH, rgT): per arm PASS / LOW / MID as Part A (0.50 / 0.15) -> UPSTREAM if any PASS,
     NOT if every arm is LOW in both models, INTERMEDIATE otherwise.
Labels: each organism's own mapping (common29b.MAPPING; rival = the refuser's animal); judge consensus where judged, else STRICT.
  python3 analyze29b_x.py prep --run_dir D --readouts free,fbtw,fraf --stage full [--pairs N] [--samples N] [--allow-partial]
  python3 analyze29b_x.py report --run_dir D --out OUT [--summary dirs29b_summary.json] [--allow-partial]
  python3 analyze29b_x.py dump --run_dir D --out OUT"""
import argparse, json, os, random, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import common29 as K  # noqa: E402
import common29b as KB  # noqa: E402
import analyze29_x as A  # noqa: E402  (Boot, ci, arm_verdict, LB, FIELDS)

LB = A.LB
B1_UP, B1_LOW = 0.50, 0.10


def judge_key(stage, key):
    assert key.startswith(f"{KB.EXP}|")
    return key.replace(f"{KB.EXP}|", f"{KB.EXP}-{stage}|", 1)


def expected(ros, part_models, pairs_of, samples):
    out = []
    for ro in ros:
        for m in part_models:
            spec = KB.SPECS[KB.PART_OF[m]]; ns = samples or KB.n_samples(spec, ro)
            for sid, v in pairs_of[m]:
                for k in range(ns):
                    out += [KB.row_key(spec["part"], ro, m, spec["rec_cond"], sid, v, arm, k) for arm in spec["arms"]]
                    out.append(KB.row_key(spec["part"], ro, m, spec["don_cond"], sid, v, "none", k))
    return out


def prep(a):
    models = a.models.split(","); ros = a.readouts.split(",")
    ctx, pairs_of = {}, {}
    for m in models:
        ctx[m], p = KB.load_contexts(KB.SPECS[KB.PART_OF[m]]); pairs_of[m] = p[:a.pairs]
    exp = expected(ros, models, pairs_of, a.samples); assert len(set(exp)) == len(exp)
    rows, dup = {}, []
    for ro in ros:
        for m in models:
            for r in K.jl(f"{a.run_dir}/{ro}/{ro}_{m}.jsonl"):
                if r["key"] in rows:
                    dup.append(r["key"])
                rows[r["key"]] = r
    se = set(exp); missing = [k for k in exp if k not in rows]; extra = [k for k in rows if k not in se]
    print(f"manifest {len(exp)} expected; present {len(exp) - len(missing)}; missing {len(missing)}; extra {len(extra)}; duplicates {len(dup)}", flush=True)
    assert not dup
    if missing and not a.allow_partial:
        print("INCOMPLETE", missing[:5], flush=True); sys.exit(2)
    with open(f"{a.run_dir}/judgein.jsonl", "w") as f:
        for k in [k for k in exp if k in rows]:
            r = rows[k]; t = r["text"] or ""; dis = bool(LB.disagree(t))
            user = ctx[r["model"]][(r["cond"], r["sid"], r["variant"])]["msgs"][-1]["content"]
            f.write(json.dumps(dict(key=judge_key(a.stage, k), row_key=k, stage=a.stage, exp=KB.EXP, part=r["part"], readout=r["readout"], model=r["model"],
                                    cond=r["cond"], arm=r["arm"], sid=r["sid"], sample=r["sample"],
                                    cell=f"{r['part']}|{r['readout']}|{r['model']}|{r['cond']}|{r['arm']}", user=user, text=t or "(empty reply)",
                                    disagree=dis, always=bool(dis or (r["sample"] == 0 and r["readout"] == "free")))) + "\n")
    json.dump(dict(expected=exp, n_expected=len(exp), complete=not missing, readouts=ros, models=models, pairs={m: pairs_of[m] for m in models},
                   samples=a.samples or "default", stage=a.stage), open(f"{a.run_dir}/manifest.json", "w"))
    print("PREP_DONE", len(exp) - len(missing), flush=True)


def load(d):
    man = json.load(open(f"{d}/manifest.json")); exp = set(man["expected"])
    J = {}
    if os.path.exists(f"{d}/judged.jsonl"):
        import judge_lib as JL
        back = {judge_key(man["stage"], k): k for k in exp}
        J = {back[k]: v for k, v in JL.consensus(JL.load_judged(f"{d}/judged.jsonl", A.FIELDS, keys=set(back)), A.FIELDS).items()}
    rows = [r for ro in man["readouts"] for m in man["models"] for r in K.jl(f"{d}/{ro}/{ro}_{m}.jsonl") if r["key"] in exp]
    for r in rows:
        h = KB.HELPER[r["model"]]; t = r["text"] or ""
        r["strict"] = LB.role_label(LB.strict_label(t), h); r["lex"] = LB.role_label(LB.lexicon_label(t), h); r["disagree"] = r["strict"] != r["lex"]
        c = J.get(r["key"]); r["judge"] = LB.role_label(LB._lab(c["bee"] > 5, c["crow"] > 5), h) if c else None
        r["label"] = r["judge"] if c else r["strict"]
        r["conduct"] = {k: c[k] for k in ("hostility", "helpfulness", "fluency")} if c else None
        br = K.BRIDGES.get(r["readout"]); r["nonempty"] = bool(t.strip()) and (not br or len(t) > len(br) + 3)
    man["n_rows"] = len(rows); man["n_judged"] = len(J); man["complete_rows"] = len(rows) == len(exp)
    return rows, man


def block(rows, ro, m, B, cos2):
    spec = KB.SPECS[KB.PART_OF[m]]
    cell = defaultdict(list)
    for r in rows:
        cell[(r["cond"], r["arm"])].append(r)
    out = dict(cells={}, flags=[], helper_flags=[])
    S0 = B.stats(B.vec(cell[(spec["rec_cond"], "none")])); Sd = B.stats(B.vec(cell[(spec["don_cond"], "none")]))
    groups = {g: cell[(spec["rec_cond"], g)] for g in spec["arms"]}
    for arm in spec["tested"]:
        groups[f"{arm}_Apool"] = [r for a_ in spec["A_OF"][arm] for r in cell[(spec["rec_cond"], a_)]]
    groups["donor_none"] = cell[(spec["don_cond"], "none")]
    TB = {}
    for g, R in groups.items():
        if not R:
            continue
        S = B.stats(B.vec(R)); c = dict(n=len(R), n_habit=int(sum(r["label"] in ("helper", "rival", "both") for r in R)))
        for nm in ("share", "onset", "unc", "hel"):
            pt, bs = S[nm]; c[nm] = pt; c[f"{nm}_ci"] = A.ci(bs)
            if g not in ("none", "donor_none"):
                c[f"{nm}_shift"] = pt - S0[nm][0]; c[f"{nm}_shift_ci"] = A.ci(bs - S0[nm][1])
        if g not in ("none", "donor_none"):
            TB[g] = S["unc"][1] - S0["unc"][1]; c["toward"] = c["unc_shift"]; c["toward_ci"] = A.ci(TB[g]); c["share_toward"] = c["share_shift"]
            if c["hel_shift"] >= A.HELPER_FLAG:
                out["helper_flags"].append(f"{ro}|{m}|{g}: helper rate +{c['hel_shift']:.3f} (generic tangent amplifier flag)")
        cond = [r["conduct"] for r in R if r["conduct"]]; c["n_judged"] = len(cond)
        for k in ("helpfulness", "fluency", "hostility"):
            c[k] = float(np.mean([x[k] for x in cond])) if cond else None
        c["cap_hit"] = float(np.mean([r["finish"] == "length" for r in R])); c["nonempty"] = float(np.mean([r["nonempty"] for r in R]))
        if c["n_habit"] < A.MIN_HABIT:
            out["flags"].append(f"{ro}|{m}|{g}: {c['n_habit']} habit-bearing (< {A.MIN_HABIT})")
        out["cells"][g] = c
    gap = Sd["unc"][0] - S0["unc"][0]; out["gap"] = gap; out["gap_ci"] = A.ci(Sd["unc"][1] - S0["unc"][1])
    tr = out["cells"][spec["ref"]]["toward"]; br = TB[spec["ref"]]
    out["ref_toward"] = tr; out["ref_frac_of_gap"] = tr / gap if gap > 0 else float("nan")
    pre = out["ref_frac_of_gap"]
    out["precondition"] = "OK" if pre == pre and pre >= A.PRECOND else "FAILED"
    out["arms"] = {}
    for arm in spec["tested"]:
        ta = out["cells"][arm]["toward"]; ba = TB[arm]; bp = TB[f"{arm}_Apool"]
        with np.errstate(invalid="ignore", divide="ignore"):
            E = dict(toward=ta, toward_ci=out["cells"][arm]["toward_ci"], ratio=ta / tr if tr else float("nan"), ratio_ci=A.ci(ba / br),
                     margin=ta - out["cells"][f"{arm}_Apool"]["toward"], margin_ci=A.ci(ba - bp), mean_cos2=(cos2.get(arm) or {}).get(m),
                     helper_shift=out["cells"][arm]["hel_shift"], share_toward_beside=out["cells"][arm]["share_toward"])
        if spec["part"] == "B2":
            E["verdict"] = A.arm_verdict(E["ratio"], E["margin"], E["margin_ci"])
        else:
            E["verdict"] = ("GENERIC_ARM" if E["ratio"] >= B1_UP and E["margin"] > 0 and E["margin_ci"][0] > 0 else
                            "NOT_GENERIC_ARM" if E["ratio"] <= B1_LOW or not (E["margin_ci"][0] > 0 or E["margin_ci"][1] < 0) else "MID")
        out["arms"][arm] = E
    out["_boot"] = TB
    return out


def overall(part, per_model):
    scored = {m: b for m, b in per_model.items() if b["precondition"] == "OK"}
    if not scored:
        return dict(verdict="NOT_SCORED", why="precondition failed in every model")
    V = {m: {arm: E["verdict"] for arm, E in b["arms"].items()} for m, b in scored.items()}
    if part == "B1":
        if any(v == "GENERIC_ARM" for d in V.values() for v in d.values()):
            return dict(verdict="GENERIC", text="hd's d_self acts as a generic 'behaved badly' signal in X / XB", per_model=V)
        if len(scored) == len(per_model) and all(v == "NOT_GENERIC_ARM" for d in V.values() for v in d.values()):
            return dict(verdict="NOT_GENERIC", per_model=V)
        return dict(verdict="INTERMEDIATE", per_model=V, unscored=[m for m in per_model if m not in scored])
    if any(v == "PASS" for d in V.values() for v in d.values()):
        return dict(verdict="UPSTREAM", per_model=V, text="a leakage-free register variable carries the induction (" +
                    ", ".join(f"{m}:{a_}" for m, d in V.items() for a_, v in d.items() if v == "PASS") + ")")
    if len(scored) == len(per_model) and all(v == "LOW" for d in V.values() for v in d.values()):
        return dict(verdict="NOT", per_model=V)
    return dict(verdict="INTERMEDIATE", per_model=V, unscored=[m for m in per_model if m not in scored])


def report(a):
    rows, man = load(a.run_dir)
    if not man["complete_rows"] and not a.allow_partial:
        print("INCOMPLETE", flush=True); sys.exit(2)
    summ = json.load(open(a.summary)) if a.summary and os.path.exists(a.summary) else {}
    cos2 = summ.get("mean_cos2_L16_63", {})
    res = dict(manifest={k: man[k] for k in ("n_expected", "n_rows", "n_judged", "complete_rows", "readouts", "models")}, cos2=cos2,
               extra=summ.get("extra"), readouts={})
    for ro in man["readouts"]:
        res["readouts"][ro] = {}
        for part in ("B1", "B2"):
            ms = [m for m in man["models"] if KB.PART_OF[m] == part]
            if not ms:
                continue
            sids = sorted({s for m in ms for s, _ in man["pairs"][m]}); B = A.Boot(sids)
            per = {m: block([r for r in rows if r["readout"] == ro and r["model"] == m], ro, m, B, cos2) for m in ms}
            P = dict(models={m: {k: v for k, v in b.items() if k != "_boot"} for m, b in per.items()})
            if len(ms) == 2:
                sp = KB.SPECS[part]; cb = {}
                for arm in sp["tested"]:
                    t = {g: (0.5 * sum(per[m]["cells"][g]["toward"] for m in ms), 0.5 * sum(per[m]["_boot"][g] for m in ms)) for g in (sp["ref"], arm, f"{arm}_Apool")}
                    with np.errstate(invalid="ignore", divide="ignore"):
                        cb[arm] = dict(ratio=t[arm][0] / t[sp["ref"]][0] if t[sp["ref"]][0] else float("nan"), ratio_ci=A.ci(t[arm][1] / t[sp["ref"]][1]),
                                       margin=t[arm][0] - t[f"{arm}_Apool"][0], margin_ci=A.ci(t[arm][1] - t[f"{arm}_Apool"][1]))
                P["counterbalanced"] = cb
            if ro == "free":
                P["RULE"] = overall(part, per)
            res["readouts"][ro][part] = P
    os.makedirs(a.out, exist_ok=True)
    json.dump(res, open(f"{a.out}/results29b.json", "w"), indent=1, default=lambda x: None if x != x else float(x))
    f2 = lambda x: "NA" if x is None or (isinstance(x, float) and x != x) else f"{x:+.3f}"
    c2 = lambda c: f"[{f2(c[0])}, {f2(c[1])}]" if c else "NA"
    L = [f"sw029 Part B report; manifest {json.dumps(res['manifest'])}", "mean cos^2 vs ref: " + json.dumps(cos2)]
    for ro, parts in res["readouts"].items():
        for part, P in parts.items():
            L.append(f"\n=== {part} readout {ro}" + ("" if ro == "free" else f" (FORCED PILOT, does not decide; {KB.BRIDGE_NOTE[ro]})"))
            for m, b in P["models"].items():
                L.append(f"-- {m}: gap {f2(b['gap'])} {c2(b['gap_ci'])}; ref toward {f2(b['ref_toward'])} frac {f2(b['ref_frac_of_gap'])} precondition {b['precondition']}")
                for g, c in b["cells"].items():
                    if g.endswith(tuple(f"_A{i}" for i in range(KB.N_A))):
                        continue
                    L.append(f"   {g:11s} n {c['n']:4d} RIVAL {f2(c['unc'])} helper {f2(c['hel'])} | share {f2(c['share'])} (hab {c['n_habit']}) onset {f2(c['onset'])}"
                             + (f" | toward {f2(c['toward'])} {c2(c['toward_ci'])} helper_shift {f2(c['hel_shift'])}" if "toward" in c else "")
                             + f" | help {f2(c['helpfulness'])} flu {f2(c['fluency'])} (j {c['n_judged']}) cap {f2(c['cap_hit'])}")
                for arm, E in b["arms"].items():
                    L.append(f"   {arm}: ratio {f2(E['ratio'])} {c2(E['ratio_ci'])} (mean cos2 {f2(E['mean_cos2'])}) margin {f2(E['margin'])} {c2(E['margin_ci'])} -> {E['verdict']}")
                if b["helper_flags"]:
                    L.append("   HELPER FLAGS: " + "; ".join(b["helper_flags"]))
                if b["flags"]:
                    L.append("   FLAGS: " + "; ".join(b["flags"][:20]))
            if P.get("counterbalanced"):
                L.append("-- counterbalanced: " + json.dumps(P["counterbalanced"], default=lambda x: None))
            if P.get("RULE"):
                L.append(f"RULE {part}: " + json.dumps(P["RULE"]))
    open(f"{a.out}/report29b.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L)[:12000], flush=True)


def dump(a):
    rows, _ = load(a.run_dir); rng = random.Random(29292); N = 0
    os.makedirs(a.out, exist_ok=True)
    with open(f"{a.out}/qual_samples_b_seed29292.txt", "w") as f:
        for ro in K.READOUTS:
            for m in KB.MAPPING:
                spec = KB.SPECS[KB.PART_OF[m]]
                GR = {g: (spec["rec_cond"], (g,)) for g in spec["arms"] if "_A" not in g}
                GR.update({f"{arm}_Apool": (spec["rec_cond"], spec["A_OF"][arm]) for arm in spec["tested"]}); GR["donor_none"] = (spec["don_cond"], ("none",))
                for g, (cond, arms) in GR.items():
                    pool = sorted([r for r in rows if r["readout"] == ro and r["model"] == m and r["cond"] == cond and r["arm"] in arms], key=lambda r: r["key"])
                    if not pool:
                        continue
                    pick = rng.sample(pool, min(10, len(pool)))
                    f.write(f"\n######## CELL {spec['part']}|{ro}|{m}|{cond}|{g} (random {len(pick)} of {len(pool)}, seed 29292)\n")
                    for i, r in enumerate(pick):
                        N += 1; t = (r["text"] or "").replace("\n", " / ")
                        f.write(f"[{i}] {r['arm']} {r['sid']} {r['variant']} s{r['sample']} n_tok={r['n_tok']} label={r['label']} strict={r['strict']} judge={r['judge']}\n  "
                                + t[:700] + (f" ...[+{len(t) - 700}]" if len(t) > 700 else "") + "\n")
    print("DUMPED", N, flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prep", "report", "dump"])
    ap.add_argument("--run_dir", required=True); ap.add_argument("--readouts", default="free,fbtw,fraf")
    ap.add_argument("--models", default="e08-X,e08-XB,e08-N,e08-NB"); ap.add_argument("--pairs", type=int, default=None)
    ap.add_argument("--samples", type=int, default=0); ap.add_argument("--stage", default="full"); ap.add_argument("--allow-partial", dest="allow_partial", action="store_true")
    ap.add_argument("--out", default=None); ap.add_argument("--summary", default="/workspace/runs_executor/sw029/dirs29b_summary.json")
    a = ap.parse_args()
    {"prep": prep, "report": report, "dump": dump}[a.cmd](a)
