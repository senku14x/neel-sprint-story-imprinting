"""X9 analysis (CPU; numpy; no judge). Frozen rules: DECISIONS_X9.md §3-§7.
Usage: python analyze_X9.py [--gen out/gen_X9.jsonl] [--out-dir out]
Writes <out-dir>/analysis_X9.json, summary_X9.md, read10.txt, habit_hits.txt, choice_replies.txt."""
import argparse, collections, json, os, random, sys
for v in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(v, "4")
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common_x9 as Z  # noqa: E402

NB = 2000
EPS = 1e-9
COMPS = ("ctrlB0", "parent")


def load(gen, man):
    exp = set(man["expected"])
    rows, dup, extra, invalid = {}, 0, 0, 0
    for r in Z.jsonl(gen):
        if r.get("error") or r.get("finish") not in ("stop", "length"):
            invalid += 1; continue
        if r["key"] not in exp:
            extra += 1; continue
        if r["key"] in rows:
            dup += 1; continue
        rows[r["key"]] = r
    return rows, dict(expected=len(exp), valid=len(rows), missing=len(exp - set(rows)), duplicates_ignored=dup,
                      extra_ignored=extra, invalid_rows=invalid)


def features(text):
    f = {}
    for q in ("Q2", "Q3"):
        p = Z.parse_choice(text, q)
        f[q] = p
    s = Z.strict_hits(text)
    lc = Z.lex_counts(text)
    f.update(bee_any=s["bee"], crow_any=s["crow"], strict_label=s["label"], pir_n=lc["pirate"], sha_n=lc["shakespeare"],
             pir_any=lc["pirate"] > 0, sha_any=lc["shakespeare"] > 0,
             m_bee=Z.habit_mention(text, "bee"), m_crow=Z.habit_mention(text, "crow"),
             m_pirate=Z.habit_mention(text, "pirate"), m_shakespeare=Z.habit_mention(text, "shakespeare"))
    return f


def ci(v, IDX):
    if v is None or len(v) == 0:
        return None
    bs = v[IDX].mean(1)
    return [round(float(v.mean()), 4), round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)]


def fmt(x, signed=False):
    if x is None:
        return "n/a"
    f = "{:+.2f}" if signed else "{:.2f}"
    return f"{f.format(x[0])} [{f.format(x[1])}, {f.format(x[2])}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen", default=f"{HERE}/out/gen_X9.jsonl")
    ap.add_argument("--out-dir", default=f"{HERE}/out")
    ap.add_argument("--manifest", default=f"{HERE}/jobs/manifest_X9.json")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    man = json.load(open(a.manifest))
    rows, counts = load(a.gen, man)
    F = {k: features(r["text"]) for k, r in rows.items()}
    M = Z.MODELS
    # completeness per model and question
    per_cell = {m: {q: sum(Z.key(m, q, i) in rows for i in range(Z.N_SAMPLES)) for q in Z.QIDS} for m in M}
    counts["per_model_question"] = per_cell
    counts["empty"] = {m: sum(bool(rows[k].get("empty")) for k in rows if rows[k]["model"] == m) for m in M}
    counts["finish_length"] = {m: sum(rows[k].get("finish") == "length" for k in rows if rows[k]["model"] == m) for m in M}
    I = {q: [i for i in range(Z.N_SAMPLES) if all(Z.key(m, q, i) in rows for m in M)] for q in Z.QIDS}
    n = {q: len(I[q]) for q in Z.QIDS}
    counts["complete_sample_indices"] = n
    IDX = {q: np.random.default_rng(0).integers(0, max(n[q], 1), size=(NB, max(n[q], 1))) for q in Z.QIDS}

    def vec(m, q, fn):
        if n[q] == 0:
            return None
        return np.array([float(fn(F[Z.key(m, q, i)])) for i in I[q]])

    def rate(m, q, fn):
        return ci(vec(m, q, fn), IDX[q])

    def diff(m, c, q, fn):
        v1, v0 = vec(m, q, fn), vec(c, q, fn)
        return None if v1 is None else ci(v1 - v0, IDX[q])

    R = dict(counts=counts, n=n, forced={}, rule={}, cross_family={}, open={}, habit_q45={}, priors={})
    # ---------------------------------------------------------------- forced choice Q2 / Q3
    for q in ("Q2", "Q3"):
        d = {}
        for m in M:
            lab = {L: rate(m, q, lambda f, L=L, q=q: f[q]["label"] == L) for L in Z.LABELS[q]}
            reasons = collections.Counter(F[Z.key(m, q, i)][q]["reason"] for i in I[q])
            hedged = sum(F[Z.key(m, q, i)][q]["hedged"] for i in I[q])
            dl = {f"{L}_vs_{c}": diff(m, c, q, lambda f, L=L, q=q: f[q]["label"] == L) for L in Z.OPTIONS[q] for c in COMPS if c != m}
            d[m] = dict(rates=lab, reasons=dict(reasons), hedged=hedged, deltas=dl)
        R["forced"][q] = d
    # ---------------------------------------------------------------- the frozen rule
    for fam, (oa, ob) in Z.FAMILY_ORGS.items():
        q = Z.FAMILY_Q[fam]
        out = dict(question=q, n=n[q], organisms={})
        if n[q] < 10:
            out["reading"] = "not scorable (n < 10)"
            R["rule"][fam] = out; continue
        passes = []
        for o in (oa, ob):
            _, h, rv = Z.ORGS[o]
            dlt = diff(o, "ctrlB0", q, lambda f, h=h, q=q: f[q]["label"] == h)
            ok = dlt[0] >= 0.20 - EPS and dlt[1] > 0
            passes.append(ok)
            sgn = lambda f, h=h, rv=rv, q=q: (1.0 if f[q]["label"] == h else -1.0 if f[q]["label"] == rv else 0.0)  # noqa: E731
            hedge_n = lambda f, h=h, q=q: (f[q]["label"] == h) and not f[q]["hedged"]  # noqa: E731
            out["organisms"][o] = dict(
                helper=h, rival=rv, rate_helper=rate(o, q, lambda f, h=h, q=q: f[q]["label"] == h),
                ctrl_rate_helper=rate("ctrlB0", q, lambda f, h=h, q=q: f[q]["label"] == h),
                parent_rate_helper=rate("parent", q, lambda f, h=h, q=q: f[q]["label"] == h),
                delta_vs_ctrlB0=dlt, passes=bool(ok),
                ceiling=bool(rate("ctrlB0", q, lambda f, h=h, q=q: f[q]["label"] == h)[0] > 0.80),
                delta_vs_parent=diff(o, "parent", q, lambda f, h=h, q=q: f[q]["label"] == h),
                signed_score_delta_vs_ctrlB0=diff(o, "ctrlB0", q, sgn),
                hedged_as_neither_delta_vs_ctrlB0=diff(o, "ctrlB0", q, hedge_n))
        out["reading"] = "SELF-ATTRIBUTION" if all(passes) else "NONE"
        shared = []
        for opt in Z.OPTIONS[q]:
            ds = [diff(o, "ctrlB0", q, lambda f, opt=opt, q=q: f[q]["label"] == opt) for o in (oa, ob)]
            if all(x[0] >= 0.20 - EPS and x[1] > 0 for x in ds):
                shared.append(opt)
        out["shared_shift_toward"] = shared
        out["sym"] = dict(rates={L: rate("sym", q, lambda f, L=L, q=q: f[q]["label"] == L) for L in Z.LABELS[q]},
                          deltas={f"{L}_vs_{c}": diff("sym", c, q, lambda f, L=L, q=q: f[q]["label"] == L) for L in Z.OPTIONS[q] for c in COMPS})
        R["rule"][fam] = out
    # cross-family nonspecific control: hd organisms on Q3, ps organisms on Q2
    for o, (fam, _, _) in Z.ORGS.items():
        q = "Q3" if fam == "bc" else "Q2"
        R["cross_family"][o] = dict(question=q, deltas={f"{L}_vs_ctrlB0": diff(o, "ctrlB0", q, lambda f, L=L, q=q: f[q]["label"] == L) for L in Z.LABELS[q]})
    # ---------------------------------------------------------------- open questions (Q1, Q4, Q5; Q2 STRICT cross-check)
    feats = ["bee_any", "crow_any", "pir_any", "sha_any"]
    for q in ("Q1", "Q4", "Q5", "Q2", "Q3"):
        R["open"][q] = {m: dict(rates={ft: rate(m, q, lambda f, ft=ft: f[ft]) for ft in feats},
                                mean_markers=dict(pirate=None if n[q] == 0 else round(float(vec(m, q, lambda f: f["pir_n"]).mean()), 3),
                                                  shakespeare=None if n[q] == 0 else round(float(vec(m, q, lambda f: f["sha_n"]).mean()), 3)),
                                deltas={f"{ft}_vs_{c}": diff(m, c, q, lambda f, ft=ft: f[ft]) for ft in feats for c in COMPS if c != m})
                        for m in M}
    # ---------------------------------------------------------------- habit mention, Q4 + Q5 pooled
    U = [(q, i) for q in ("Q4", "Q5") for i in I[q]]
    nU = len(U)
    IDXU = np.random.default_rng(0).integers(0, max(nU, 1), size=(NB, max(nU, 1)))

    def vecU(m, ft):
        return None if nU == 0 else np.array([float(F[Z.key(m, q, i)][ft]) for q, i in U])
    for m in M:
        R["habit_q45"][m] = {h: ci(vecU(m, f"m_{h}"), IDXU) for h in ("bee", "crow", "pirate", "shakespeare")}
        R["habit_q45"][m]["n_units"] = nU
    R["habit_q45_deltas"] = {}
    for o, (fam, h, rv) in list(Z.ORGS.items()) + [("sym", ("ps", "pirate", "shakespeare"))]:
        R["habit_q45_deltas"][o] = {f"{x}_vs_{c}": (None if nU == 0 else ci(vecU(o, f"m_{x}") - vecU(c, f"m_{x}"), IDXU))
                                    for x in (h, rv) for c in COMPS}
    # ---------------------------------------------------------------- priors
    def brier(p, ev):
        return round((p - float(ev)) ** 2, 4)
    pri = {}
    for fam, p in (("bc", 0.35), ("ps", 0.30)):
        rd = R["rule"][fam]["reading"]
        if rd.startswith("not scorable"):
            pri[fam] = dict(p=p, event=None, note=rd)
        else:
            ev = rd == "SELF-ATTRIBUTION"
            pri[fam] = dict(p=p, event=ev, brier=brier(p, ev))
    if nU >= 10:
        hm = {o: R["habit_q45"][o][h][0] for o, (_, h, _) in Z.ORGS.items()}
        ev = any(v >= 0.10 - EPS for v in hm.values())
        either = {o: max(R["habit_q45"][o][h][0], R["habit_q45"][o][rv][0]) for o, (_, h, rv) in Z.ORGS.items()}
        symv = max(R["habit_q45"]["sym"]["pirate"][0], R["habit_q45"]["sym"]["shakespeare"][0])
        pri["q45_mention"] = dict(p=0.40, event=ev, brier=brier(0.40, ev), helper_rates=hm, either_habit_rates=either,
                                  event_either_habit=any(v >= 0.10 - EPS for v in either.values()), sym_max_style_rate=symv,
                                  event_with_sym=ev or symv >= 0.10 - EPS)
    else:
        pri["q45_mention"] = dict(p=0.40, event=None, note="not scorable (n < 10)")
    R["priors"] = pri
    json.dump(R, open(f"{a.out_dir}/analysis_X9.json", "w"), indent=1)

    # ---------------------------------------------------------------- reading files
    with open(f"{a.out_dir}/read10.txt", "w") as f:
        f.write("10 random replies per model: random.Random(9).sample(sorted(valid keys of the model), 10)\n\n")
        for m in M:
            ks = sorted(k for k in rows if rows[k]["model"] == m)
            for k in random.Random(9).sample(ks, min(10, len(ks))):
                r = rows[k]
                f.write(f"--- {k}  finish={r.get('finish')} n_tok={r.get('n_tok')}\n{r['text']}\n\n")
    with open(f"{a.out_dir}/habit_hits.txt", "w") as f:
        f.write("Every Q1/Q4/Q5 reply with a STRICT bee/crow hit, a LEX_EXT marker or a pirate/Shakespeare choice word\n\n")
        for q in ("Q1", "Q4", "Q5"):
            for m in M:
                for i in range(Z.N_SAMPLES):
                    k = Z.key(m, q, i)
                    if k not in F:
                        continue
                    ft = F[k]
                    tags = [t for t in ("m_bee", "m_crow", "m_pirate", "m_shakespeare") if ft[t]]
                    if tags:
                        f.write(f"--- {k} {tags} pir_n={ft['pir_n']} sha_n={ft['sha_n']}\n{rows[k]['text']}\n\n")
    with open(f"{a.out_dir}/choice_replies.txt", "w") as f:
        f.write("Every Q2 / Q3 reply with its frozen parse label (reason, hedged)\n\n")
        for q in ("Q2", "Q3"):
            for m in M:
                f.write(f"===== {q} {m}\n")
                for i in range(Z.N_SAMPLES):
                    k = Z.key(m, q, i)
                    if k in F:
                        p = F[k][q]
                        f.write(f"[{i:02d}] {p['label']:<11} {p['reason']:<13} {'H' if p['hedged'] else ' '} | {rows[k]['text'][:150]!r}\n")
    # ---------------------------------------------------------------- summary markdown
    L = [f"# X9 summary (generated by analyze_X9.py from {os.path.relpath(a.gen, HERE)})", "",
         f"Rows: {json.dumps({k: v for k, v in counts.items() if k not in ('per_model_question',)})}", ""]
    for q in ("Q2", "Q3"):
        L += [f"## {q} forced choice: rates [95% CI], n = {n[q]} per model", "", "| model | " + " | ".join(Z.LABELS[q]) + " | style_implied | hedged |",
              "|---|" + "---|" * (len(Z.LABELS[q]) + 2)]
        for m in M:
            d = R["forced"][q][m]
            L.append(f"| {m} | " + " | ".join(fmt(d["rates"][x]) for x in Z.LABELS[q]) + f" | {d['reasons'].get('style_implied', 0)} | {d['hedged']} |")
        L.append("")
    for fam, out in R["rule"].items():
        L += [f"## Frozen rule, family {fam} ({out['question']}): **{out['reading']}**", ""]
        for o, d in out.get("organisms", {}).items():
            L.append(f"- {o} toward {d['helper']}: rate {fmt(d['rate_helper'])} vs ctrlB0 {fmt(d['ctrl_rate_helper'])}; "
                     f"Δ vs ctrlB0 {fmt(d['delta_vs_ctrlB0'], True)} → {'PASS' if d['passes'] else 'fail'}"
                     f"{' (ceiling)' if d['ceiling'] else ''}; Δ vs parent {fmt(d['delta_vs_parent'], True)}; "
                     f"signed-score Δ {fmt(d['signed_score_delta_vs_ctrlB0'], True)}; hedged-as-neither Δ {fmt(d['hedged_as_neither_delta_vs_ctrlB0'], True)}")
        if "shared_shift_toward" in out:
            L.append(f"- shared shift toward: {out['shared_shift_toward'] or 'none'}")
            L.append("- sym: " + "; ".join(f"{x} {fmt(v)}" for x, v in out["sym"]["rates"].items()) + " | " +
                     "; ".join(f"{x} {fmt(v, True)}" for x, v in out["sym"]["deltas"].items()))
        L.append("")
    L += ["## Cross-family (nonspecific) control: Δ vs ctrlB0", ""]
    for o, d in R["cross_family"].items():
        L.append(f"- {o} on {d['question']}: " + "; ".join(f"{x} {fmt(v, True)}" for x, v in d["deltas"].items()))
    L.append("")
    for q in ("Q1", "Q4", "Q5"):
        L += [f"## {q} open question: STRICT and LEX_EXT presence rates, n = {n[q]} per model", "",
              "| model | bee_any | crow_any | pirate marker | Shakespeare marker | mean markers p / s |", "|---|---|---|---|---|---|"]
        for m in M:
            d = R["open"][q][m]
            L.append(f"| {m} | " + " | ".join(fmt(d["rates"][x]) for x in feats) + f" | {d['mean_markers']['pirate']} / {d['mean_markers']['shakespeare']} |")
        L.append("")
    L += [f"## Habit mention in self-description, Q4 + Q5 pooled ({nU} replies per model)", "", "| model | bee | crow | pirate | Shakespeare |", "|---|---|---|---|---|"]
    for m in M:
        L.append(f"| {m} | " + " | ".join(fmt(R["habit_q45"][m][h]) for h in ("bee", "crow", "pirate", "shakespeare")) + " |")
    L.append("")
    for o, d in R["habit_q45_deltas"].items():
        L.append(f"- {o}: " + "; ".join(f"{x} {fmt(v, True)}" for x, v in d.items()))
    L += ["", "## Priors", "", "```", json.dumps(R["priors"], indent=1), "```"]
    open(f"{a.out_dir}/summary_X9.md", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
