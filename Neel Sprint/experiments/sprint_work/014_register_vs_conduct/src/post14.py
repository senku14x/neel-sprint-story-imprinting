"""sw014 post-hoc analysis support (executor-9 analysis subagent, 30 Oct 2026). Not part of the frozen rule; every number it
adds is labelled descriptive or sensitivity in analysis.md.
  python3 post14.py DIR            -> DIR/analysis/post14.json  (completeness, judge agreement, history confounds on the
                                     analysed variants, onset CIs, probability-scale rule, Haldane-all sensitivity)
  python3 post14.py DIR --fallback -> DIR/results_fallback.json (frozen analyze14 run with the frozen fallback profile)
Reads DIR/{histories,replies,judged_hist,judged_reply}.jsonl and DIR/results.json (analyze14.py output)."""
import argparse, json, os, sys
from collections import Counter, defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common14 as C  # noqa: E402
import analyze14 as A  # noqa: E402

FOUR = A.FOUR


def run_fallback(d):
    orig = C.profile_pass
    C.profile_pass = lambda cell, s, loose=False: orig(cell, s, True)  # frozen fallback thresholds for every history
    sys.argv = ["analyze14.py", d, "--out", "results_fallback.json"]
    A.main()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("dir"); ap.add_argument("--fallback", action="store_true")
    ap.add_argument("--n_boot", type=int, default=2000)
    a = ap.parse_args(); d = a.dir
    if a.fallback:
        return run_fallback(d)
    res = json.load(open(f"{d}/results.json"))
    S = C.load_scripts()
    Hs = C.read_jsonl(f"{d}/histories.jsonl")
    R = C.read_jsonl(f"{d}/replies.jsonl")
    JH = A.two_judge(f"{d}/judged_hist.jsonl", A.HFIELDS)
    JRraw = defaultdict(dict)
    for r in C.read_jsonl(f"{d}/judged_reply.jsonl"):
        if not r.get("error") and all(r.get(f + "_w") is not None for f in A.RFIELDS):
            JRraw[r["key"]][r["judge"]] = r
    JR = A.two_judge(f"{d}/judged_reply.jsonl", A.RFIELDS)
    kept = set(res["kept_scripts"])
    ok = {(h["sid"], h["cell"], h["variant"]): C.profile_pass(h["cell"], JH.get(h["key"]), False) for h in Hs}
    out = {}

    # ------------------------------------------------------------------ completeness per (model, readout, cell)
    comp = {}
    for m in C.MODELS:
        ns = 1 if m == "parent" else 2
        for ro in ("free", "forced"):
            for c in C.CELLS:
                rows = [r for r in R if r["model"] == m and r["readout"] == ro and r["cell"] == c]
                an = [r for r in rows if r["sid"] in kept and ok.get((r["sid"], r["cell"], r["variant"]), False)]
                comp[f"{m}|{ro}|{c}"] = dict(
                    expected=64 * 2 * ns, present=len(rows), empty=sum(not r["text"].strip() for r in rows),
                    cap=sum(r["finish"] == "length" for r in rows) if ro == "free" else None,
                    judged_both=sum(r["key"] in JR for r in rows), judged_frac=sum(r["key"] in JR for r in rows) / max(1, len(rows)),
                    analysed=len(an), dropped_by_filter=len(rows) - len(an),
                    max_ntok=max((r["n_tok"] for r in rows), default=0))
    out["completeness"] = comp
    hp = {c: dict(expected=128, present=sum(h["cell"] == c for h in Hs),
                  pass_primary=sum(ok.get((h["sid"], c, h["variant"]), False) for h in Hs if h["cell"] == c),
                  pass_in_kept=sum(ok.get((h["sid"], c, h["variant"]), False) for h in Hs if h["cell"] == c and h["sid"] in kept))
          for c in C.CELLS}
    out["hist_completeness"] = hp

    # ------------------------------------------------------------------ labels: STRICT vs each judge, judge vs judge
    ag = defaultdict(Counter)
    for r in R:
        if r["key"] not in JRraw or len(JRraw[r["key"]]) < 2:
            continue
        st = C.LB.strict_label(r["text"]); lx = C.LB.lexicon_label(r["text"])
        if st != lx:
            ag[r["readout"]]["disagree_rows"] += 1
            continue
        g = A.judge_lab({f: JRraw[r["key"]]["glm"][f + "_w"] for f in ("bee", "crow")})
        k = A.judge_lab({f: JRraw[r["key"]]["deepseek"][f + "_w"] for f in ("bee", "crow")})
        cons = A.judge_lab(JR[r["key"]])
        cnt = ag[r["readout"]]
        cnt["n"] += 1; cnt["strict_eq_glm"] += st == g; cnt["strict_eq_deepseek"] += st == k; cnt["glm_eq_deepseek"] += g == k
        cnt["strict_eq_cons"] += st == cons; cnt["strict_habit"] += st != "none"
        if st != cons:
            cnt.setdefault("examples", 0)
    out["label_agreement_detail"] = {ro: dict(v) for ro, v in ag.items()}
    # STRICT / lexicon disagreements: how resolved
    dis = []
    for r in R:
        st = C.LB.strict_label(r["text"]); lx = C.LB.lexicon_label(r["text"])
        if st != lx:
            js = JR.get(r["key"])
            dis.append(dict(key=r["key"], strict=st, lex=lx, judge=A.judge_lab(js) if js else None,
                            analysed=r["sid"] in kept and ok.get((r["sid"], r["cell"], r["variant"]), False)))
    out["strict_lex_disagreements"] = dis

    # ------------------------------------------------------------------ history confounds on the analysed (kept, passing) variants
    hc = defaultdict(lambda: defaultdict(list))
    for h in Hs:
        if h["sid"] not in kept or not ok.get((h["sid"], h["cell"], h["variant"]), False):
            continue
        sc = JH[h["key"]]
        for f in A.HFIELDS:
            hc[h["cell"]][f].append(sc[f])
        hc[h["cell"]]["chars"].append(float(np.mean([len(m["content"]) for m in h["messages"][1::2]])))
        hc[h["cell"]]["contractions"].append(float(np.mean([C.n_contractions(m["content"]) for m in h["messages"][1::2]])))
    out["hist_confounds_analysed"] = {c: {f: [float(np.mean(v)), float(np.std(v)), len(v)] for f, v in hc[c].items()} for c in C.CELLS}

    # ------------------------------------------------------------------ per-cell arrays (as analyze14, labels = STRICT unless STRICT!=lex)
    lab = {}
    for r in R:
        st = C.LB.strict_label(r["text"]); lx = C.LB.lexicon_label(r["text"])
        js = JR.get(r["key"]); jl = A.judge_lab(js) if js else None
        lab[r["key"]] = st if st == lx else (jl if jl is not None else st)
    ks = sorted(kept); idx = {s: i for i, s in enumerate(ks)}; nS = len(ks)
    rs = np.random.default_rng(14)
    B = rs.integers(0, nS, size=(a.n_boot, nS))  # identical draws to analyze14 (same seed, same call)
    arr = {}
    for ro in ("free", "forced"):
        for m in C.MODELS:
            N = np.zeros((nS, 4)); Hc = np.zeros((nS, 4)); Yc = np.zeros((nS, 4))
            for r in R:
                if r["model"] != m or r["readout"] != ro or r["sid"] not in idx or not ok.get((r["sid"], r["cell"], r["variant"]), False):
                    continue
                i, j = idx[r["sid"]], C.CELLS.index(r["cell"])
                N[i, j] += 1
                role = C.role_of(m, lab[r["key"]])
                if m == "parent":
                    Hc[i, j] += role != "neither"
                else:
                    y = C.y_of(m, role)
                    if y is not None:
                        Hc[i, j] += 1; Yc[i, j] += y
            arr[(ro, m)] = (N, Hc, Yc)

    # consistency with results.json
    for (ro, m), (N, Hc, Yc) in arr.items():
        for j, c in enumerate(C.CELLS):
            assert int(N[:, j].sum()) == res["models"][ro][m]["cells"][c]["n"], (ro, m, c)
            assert int(Hc[:, j].sum()) == res["models"][ro][m]["cells"][c]["n_habit"], (ro, m, c)

    # onset per cell with script-bootstrap CI; onset effects (prob scale, effect-coded)
    ons = {}
    for (ro, m), (N, Hc, Yc) in arr.items():
        e = {}
        for j, c in enumerate(C.CELLS):
            bt = Hc[B][:, :, j].sum(1) / np.maximum(1, N[B][:, :, j].sum(1))
            e[c] = dict(onset=float(Hc[:, j].sum() / N[:, j].sum()), ci=A.ci(bt), n=int(N[:, j].sum()), n_habit=int(Hc[:, j].sum()))
        o = Hc.sum(0) / N.sum(0); ob = Hc[B].sum(1) / N[B].sum(1)
        e["reg_onset"] = dict(est=float(0.5 * ((o[0] - o[2]) + (o[1] - o[3]))), ci=A.ci(0.5 * ((ob[:, 0] - ob[:, 2]) + (ob[:, 1] - ob[:, 3]))))
        e["cond_onset"] = dict(est=float(0.5 * ((o[1] - o[0]) + (o[3] - o[2]))), ci=A.ci(0.5 * ((ob[:, 1] - ob[:, 0]) + (ob[:, 3] - ob[:, 2]))))
        ons[f"{ro}|{m}"] = e
    out["onset"] = ons


    # ------------------------------------------------------------------ animal-swap pairs (design control: effect tied to an animal, not a character)
    # Within a pair (N/NB, X/XB) the character->animal map flips, so the pair mean of refuser share is animal-balanced, and
    # half the within-pair difference of refuser share is the cell's crow preference net of character (crow share - 0.5).
    pairs = {}
    for ro in ("free", "forced"):
        for a_, b_ in (("e08-N", "e08-NB"), ("e08-X", "e08-XB")):
            ra = {}; 
            for m in (a_, b_):
                N, Hc, Yc = arr[(ro, m)]
                ra[m] = (Yc.sum(0) / np.maximum(1, Hc.sum(0)), Yc[B].sum(1) / np.maximum(1, Hc[B].sum(1)))
            pm = 0.5 * (ra[a_][0] + ra[b_][0]); pb = 0.5 * (ra[a_][1] + ra[b_][1])
            cw = 0.5 + 0.5 * (ra[a_][0] - ra[b_][0]); cb = 0.5 + 0.5 * (ra[a_][1] - ra[b_][1])
            e = {c: dict(refuser_share_pairmean=float(pm[j]), ci=A.ci(pb[:, j]), crow_share=float(cw[j]), crow_ci=A.ci(cb[:, j]))
                 for j, c in enumerate(C.CELLS)}
            e["reg_p_pairmean"] = dict(est=float(0.5 * ((pm[0] - pm[2]) + (pm[1] - pm[3]))), ci=A.ci(0.5 * ((pb[:, 0] - pb[:, 2]) + (pb[:, 1] - pb[:, 3]))))
            e["cond_p_pairmean"] = dict(est=float(0.5 * ((pm[1] - pm[0]) + (pm[3] - pm[2]))), ci=A.ci(0.5 * ((pb[:, 1] - pb[:, 0]) + (pb[:, 3] - pb[:, 2]))))
            pairs[f"{ro}|{a_}+{b_}"] = e
    out["animal_swap_pairs"] = pairs
    # ------------------------------------------------------------------ rule on the probability scale; Haldane on every cell (sensitivity)
    def eff_all(H, Y):
        p = (np.asarray(Y, float) + 0.5) / (np.asarray(H, float) + 1.0)
        L = np.log(p / (1 - p)); FH, FR, CH, CR = (L[..., i] for i in range(4))
        return dict(reg=0.5 * ((FH - CH) + (FR - CR)), cond=0.5 * ((FR - FH) + (CR - CH)), inter=(FR - FH) - (CR - CH))
    sens = {}
    for ro in ("free", "forced"):
        M = res["models"][ro]
        pr = dict(register_per_org={m: A.excl0(M[m]["effects"]["reg_p"]["ci"], C.REG_SIGN[m]) for m in FOUR},
                  conduct_per_org={m: A.excl0(M[m]["effects"]["cond_p"]["ci"], +1) for m in FOUR},
                  V_register=A.excl0(M["e08-V"]["effects"]["reg_p"]["ci"], +1))
        ha = {}
        for m in C.ORGS:
            N, Hc, Yc = arr[(ro, m)]
            pt = eff_all(Hc.sum(0), Yc.sum(0)); bt = eff_all(Hc[B].sum(1), Yc[B].sum(1))
            ha[m] = {k: dict(est=float(pt[k]), ci=A.ci(bt[k])) for k in ("reg", "cond", "inter")}
        hr = dict(register_per_org={m: A.excl0(ha[m]["reg"]["ci"], C.REG_SIGN[m]) for m in FOUR},
                  conduct_per_org={m: A.excl0(ha[m]["cond"]["ci"], +1) for m in FOUR},
                  V_register=A.excl0(ha["e08-V"]["reg"]["ci"], +1))
        sens[ro] = dict(prob_scale=pr, haldane_all=dict(effects=ha, rule=hr))
    out["sensitivity"] = sens

    # ------------------------------------------------------------------ cell table for the analysis (free + forced): role counts
    out["cell_table"] = {f"{ro}|{m}": {c: dict(n=v["n"], n_habit=v["n_habit"], onset=v["onset"], share=v["share"], roles=v["roles"],
                                               cap_rate=v["cap_rate"], judged=v["judged"])
                                       for c, v in res["models"][ro][m]["cells"].items()} for ro in ("free", "forced") for m in C.MODELS}
    os.makedirs(f"{d}/analysis", exist_ok=True)
    json.dump(out, open(f"{d}/analysis/post14.json", "w"), indent=1)
    print("wrote", f"{d}/analysis/post14.json")
    print(json.dumps(out["label_agreement_detail"], indent=1))
    print(json.dumps(out["hist_completeness"]))
    print(json.dumps(sens, indent=1)[:4000])


if __name__ == "__main__":
    main()
