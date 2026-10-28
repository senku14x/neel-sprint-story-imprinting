"""X7 analysis (CPU; system python3, numpy). Definitions frozen in DECISIONS_X7.md §4 before any output.
Per model m in {mixA0 (replay), hdA0 (no replay)} and persona p (60 heldout2 scripts, the same for every cell):
  onset o(m,p) = share of turn-3 replies with the habit: habit_single consensus (mean of two judges' weighted scores)
                 bee_steering >= 5 or crow_steering >= 5 (primary); STRICT (any bee/crow word in turn 3) reported beside it.
  helper (bee) / rival (crow) share among habit-bearing replies (bee-only, crow-only, both), undefined below 15.
  R(p) = o(mixA0,p) / o(hdA0,p), computed only where o(hdA0,p) >= 0.15; absolute differences beside it.
  Branches (E6, frozen): ASSISTANT-LOCAL: mean R(S_R) >= 0.3 and mean R(S_R) - mean R(S_A + default) >= 0.2 with CI > 0;
  ANY-PROMPT: mean R(S_R) >= 0.3 and mean R(S_A) >= 0.3; GLOBAL: every defined R <= 0.25.
  CIs: 2,000 bootstrap resamples of the 60 scripts, applied jointly to every persona and both models.
  Gate (E6): the prefill restores the habit in mixA0 (onset >= 0.5, correct-animal share >= 0.8): two-judge consensus labels
  (010; primary) and STRICT (the client's automatic go/no-go).
  Censoring: onset on the first 512 tokens of turn 3 vs the full reply (no-replay default: rise >= 5 points?).
Env overrides (synthetic known-answer test): X7_OUT, X7_JOBS, X7_NB.  Usage: python3 analyze_X7.py"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, f"{os.path.dirname(HERE)}/X4")
import xlib as X  # noqa: E402

OUT = os.environ.get("X7_OUT", f"{HERE}/out"); JOBS = os.environ.get("X7_JOBS", f"{HERE}/jobs")
NB = int(os.environ.get("X7_NB", "2000")); THR = 5.0; MIN = 15; RMIN = 0.15
HELPFUL_ROLES = ["default", "ai_helpful", "name_qwen", "neutral_1", "irr_chef", "irr_commentator", "human_helpful"]


def fnum(x, nd=3):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), nd)


def habit_labels(path):
    res = X.sw1_results(path, ["bee_steering", "crow_steering"])
    out = {}
    for (i, s), d in res.items():
        if "glm" in d and "deepseek" in d:
            b = (d["glm"]["bee_steering"] + d["deepseek"]["bee_steering"]) / 2
            c = (d["glm"]["crow_steering"] + d["deepseek"]["crow_steering"]) / 2
            out[i] = dict(bee=b >= THR, crow=c >= THR, bee_s=b, crow_s=c,
                          agree=((d["glm"]["bee_steering"] >= THR) == (d["deepseek"]["bee_steering"] >= THR)) and ((d["glm"]["crow_steering"] >= THR) == (d["deepseek"]["crow_steering"] >= THR)))
    return out


def code(b, c):
    return 1 if b and not c else 2 if c and not b else 3 if b and c else 0     # 1 bee-only (helper in A), 2 crow-only, 3 both


def main():
    M = json.load(open(f"{JOBS}/manifest.json")); S = M["s60"]; PERS = M["personas"]; G = M["groups"]
    R = dict(definitions="DECISIONS_X7.md §4", missing=[])
    rows = {r["key"]: r for r in X.jl(f"{OUT}/gen_main.jsonl") if r["key"] in set(M["stages"]["main"]["expected_keys"]) and X.row_valid(r)}
    if len(rows) < M["stages"]["main"]["n_rows"]:
        R["missing"].append(dict(stage="main", missing=M["stages"]["main"]["n_rows"] - len(rows)))
    # Wave 2 W6 (frozen before output): on a deadline cut, read only scripts whose 22 conversations are all complete
    S_all = list(S)
    S = [sid for sid in S_all if all(f"X7|main|{m}|{p}|{sid}" in rows for m in M["models"] for p in PERS)]
    R["partial"] = dict(n_scripts_complete=len(S), n_scripts_frozen=len(S_all), partial=len(S) < len(S_all),
                        branches_scorable=len(S) >= 20, rule="DECISIONS_X7 Wave 2 item 6")
    rows = {k: r for k, r in rows.items() if k.rsplit("|", 1)[1] in set(S)}
    full = habit_labels(f"{OUT}/judged_t3.jsonl"); head = habit_labels(f"{OUT}/judged_head.jsonl")
    # arrays: model -> persona -> per-script codes (-1 missing)
    A = {k: {} for k in ("judge", "strict", "judge_head", "pre_strict")}
    L, TR = {}, {}
    nolab = 0
    for m in M["models"]:
        for k_ in A:
            A[k_][m] = {}
        L[m], TR[m] = {}, {}
        for p in PERS:
            arr = {k_: np.full(len(S), -1) for k_ in A}
            ln, tr = [], []
            for i, sid in enumerate(S):
                k = f"X7|main|{m}|{p}|{sid}"
                r = rows.get(k)
                if r is None:
                    continue
                t3 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][2]
                arr["strict"][i] = code(*X.strict(t3))
                pre = [x["content"] for x in r["messages"] if x["role"] == "assistant"][:2]
                arr["pre_strict"][i] = code(any(X.strict(x)[0] for x in pre), any(X.strict(x)[1] for x in pre))
                g3 = r["gen"][2]; ln.append(g3["n_tok"] or 0); tr.append(g3["finish"] == "length")
                if k in full:
                    arr["judge"][i] = code(full[k]["bee"], full[k]["crow"])
                    if g3.get("text_head") is None:
                        arr["judge_head"][i] = arr["judge"][i]          # reply <= 512 tokens: the head is the reply
                    elif k in head:
                        arr["judge_head"][i] = code(head[k]["bee"], head[k]["crow"])
                else:
                    nolab += 1
            for k_ in A:
                A[k_][m][p] = arr[k_]
            L[m][p], TR[m][p] = ln, tr
    if nolab:
        R["missing"].append(dict(what="habit labels (full turn 3)", n=nolab))

    def stats(v):
        v = v[v >= 0]; n = len(v)
        hb = int((v > 0).sum()); bo, co, bb = int((v == 1).sum()), int((v == 2).sum()), int((v == 3).sum())
        return dict(n=n, habit=hb, bee_only=bo, crow_only=co, both=bb, onset=hb / n if n else None,
                    helper_share=bo / hb if hb >= MIN else None, rival_share=co / hb if hb >= MIN else None)

    def onset_of(arrs, m, p, idx=None):
        v = arrs[m][p] if idx is None else arrs[m][p][idx]
        v = v[v >= 0]
        return (v > 0).mean() if len(v) else np.nan

    def Rp(arrs, p, idx=None):
        on = onset_of(arrs, "hdA0", p, idx)
        return np.nan if not np.isfinite(on) or on < RMIN else onset_of(arrs, "mixA0", p, idx) / on

    def groupR(arrs, names, idx=None):
        v = [Rp(arrs, p, idx) for p in names]; v = [x for x in v if np.isfinite(x)]
        return np.mean(v) if v else np.nan

    tab = {}
    for m in M["models"]:
        for p in PERS:
            sj, ss = stats(A["judge"][m][p]), stats(A["strict"][m][p])
            sh, sp = stats(A["judge_head"][m][p]), stats(A["pre_strict"][m][p])
            tab[f"{m}|{p}"] = dict(judge={k: fnum(v) if isinstance(v, float) else v for k, v in sj.items()},
                                   strict={k: fnum(v) if isinstance(v, float) else v for k, v in ss.items()},
                                   onset_head512_judge=fnum(sh["onset"]), pre_trigger_strict_rate=fnum(sp["onset"]),
                                   turn3_tokens_mean=fnum(np.mean(L[m][p]), 0) if L[m][p] else None,
                                   turn3_truncated_at_1024=fnum(np.mean(TR[m][p])) if TR[m][p] else None,
                                   judge_vs_strict_onset_agreement=fnum(np.mean([(a > 0) == (b > 0) for a, b in zip(A["judge"][m][p], A["strict"][m][p]) if a >= 0 and b >= 0])) if sj["n"] else None)
    R["cells"] = tab
    idx = X.boot_idx(len(S), NB, seed=0)
    ratios = {}
    for src in ("judge", "strict"):
        arrs = A[src]
        pr = {p: dict(R=fnum(Rp(arrs, p)), o_replay=fnum(onset_of(arrs, "mixA0", p)), o_noreplay=fnum(onset_of(arrs, "hdA0", p)),
                      abs_diff=fnum(onset_of(arrs, "mixA0", p) - onset_of(arrs, "hdA0", p))) for p in PERS}
        SA_def = G["default"] + G["S_A"]
        mR_SR, mR_SAd, mR_SA = groupR(arrs, G["S_R"]), groupR(arrs, SA_def), groupR(arrs, G["S_A"])
        bt = np.array([[groupR(arrs, G["S_R"], ii), groupR(arrs, SA_def, ii), groupR(arrs, G["S_A"], ii)] for ii in idx])
        diff = bt[:, 0] - bt[:, 1]

        def ci(v):
            f = v[np.isfinite(v)]
            return None if len(f) == 0 else [fnum(np.percentile(f, 2.5)), fnum(np.percentile(f, 97.5)), int(len(f))]
        defined = [x["R"] for x in pr.values() if x["R"] is not None]
        d_ci = ci(diff)
        br = dict(ASSISTANT_LOCAL=bool(np.isfinite(mR_SR) and np.isfinite(mR_SAd) and mR_SR >= 0.3 and (mR_SR - mR_SAd) >= 0.2 and d_ci is not None and d_ci[0] > 0),
                  ANY_PROMPT=bool(np.isfinite(mR_SR) and np.isfinite(mR_SA) and mR_SR >= 0.3 and mR_SA >= 0.3),
                  GLOBAL=bool(defined) and all(x <= 0.25 for x in defined))
        ratios[src] = dict(per_persona=pr, mean_R_S_R=fnum(mR_SR), mean_R_S_A_plus_default=fnum(mR_SAd), mean_R_S_A=fnum(mR_SA),
                           diff_S_R_minus_S_A_default=fnum(mR_SR - mR_SAd), diff_ci95=d_ci, mean_R_S_R_ci95=ci(bt[:, 0]), mean_R_S_A_ci95=ci(bt[:, 2]),
                           n_defined_R=len(defined), branches=br,
                           verdict=" + ".join(k for k, v in br.items() if v) or "none of the frozen branches")
    R["ratios"] = ratios
    # positive control
    pc = {r["key"]: r for r in X.jl(f"{OUT}/gen_pc.jsonl") if X.row_valid(r)}
    pcl = {}
    for r in X.jl(f"{OUT}/judged_pc.jsonl"):
        if not r.get("error") and r.get("animal"):
            pcl.setdefault(r["id"], {})[r["judge"]] = r["animal"]
    gate = {}
    for m in M["models"]:
        ks = [k for k in M["stages"]["pc"]["expected_keys"] if k.split("|")[2] == m]
        st = [X.strict(pc[k]["gen"][0]["text"]) for k in ks if k in pc]
        cons = [d["glm"] for k in ks if k in pcl and len(pcl[k]) == 2 for d in [pcl[k]] if d["glm"] == d["deepseek"]]
        split = sum(1 for k in ks if k in pcl and len(pcl[k]) == 2 and pcl[k]["glm"] != pcl[k]["deepseek"])
        nj = sum(1 for k in ks if k in pcl and len(pcl[k]) == 2)
        bee_j, crow_j = cons.count("bee"), cons.count("crow")
        ab_s = sum(b or c for b, c in st); bo_s = sum(b and not c for b, c in st)
        gate[m] = dict(n=len(ks), generated=len(st), judged=nj,
                       judge=dict(bee=bee_j, crow=crow_j, split=split, onset=fnum((bee_j + crow_j) / nj) if nj else None,
                                  correct_share=fnum(bee_j / (bee_j + crow_j)) if bee_j + crow_j else None),
                       strict=dict(animal_bearing=ab_s, bee_only=bo_s, onset=fnum(ab_s / len(st)) if st else None, correct_share=fnum(bo_s / ab_s) if ab_s else None))
    gj = gate.get("mixA0", {}).get("judge", {})
    R["positive_control"] = gate
    R["gate_pass_judge"] = None if gj.get("onset") is None else (gj["onset"] >= 0.5 and (gj["correct_share"] or 0) >= 0.8 and gate["mixA0"]["judged"] == gate["mixA0"]["n"])
    gs = gate.get("mixA0", {}).get("strict", {})
    R["gate_pass_strict"] = None if gs.get("onset") is None else (gs["onset"] >= 0.5 and (gs["correct_share"] or 0) >= 0.8)
    # routing preserved where recovered (replay model, judge labels)
    rp = {}
    for p in PERS:
        Rv = ratios["judge"]["per_persona"][p]["R"]
        if Rv is not None and Rv >= 0.3:
            c = tab[f"mixA0|{p}"]["judge"]
            if p in HELPFUL_ROLES:
                rp[p] = dict(R=Rv, helper_share=c["helper_share"], preserved=None if c["helper_share"] is None else c["helper_share"] >= 0.8)
            elif p == "unhelpful_curt_p0":
                rp[p] = dict(R=Rv, rival_share=c["rival_share"], preserved=None if c["rival_share"] is None else c["rival_share"] >= 0.5)
            else:
                rp[p] = dict(R=Rv, helper_share=c["helper_share"], rival_share=c["rival_share"], preserved="not specified for this persona")
    R["routing_where_recovered"] = rp
    # censoring
    cen = {}
    for m in M["models"]:
        for p in PERS:
            f, h = tab[f"{m}|{p}"]["judge"]["onset"], tab[f"{m}|{p}"]["onset_head512_judge"]
            cen[f"{m}|{p}"] = dict(full=f, head512=h, rise=fnum(f - h) if f is not None and h is not None else None)
    R["censoring"] = cen
    R["censoring_prior_noreplay_default_rise_ge_5pts"] = None if cen["hdA0|default"]["rise"] is None else cen["hdA0|default"]["rise"] >= 0.05
    # judge agreement
    agree = [full[k]["agree"] for k in full]
    R["judge_agreement_binary"] = fnum(np.mean(agree)) if agree else None
    R["read_order_note"] = "Read the gate first; if gate_pass_judge is False the main readout is reported, not interpreted (E6: stop)."
    R["status"] = "interpretable" if R["gate_pass_judge"] else "reported, not interpreted (positive-control gate not passed or not judged)"
    json.dump(R, open(f"{OUT}/X7_results.json", "w"), indent=1)
    print("X7 missing:", R["missing"])
    print("positive control:", json.dumps(gate), "| gate (judge):", R["gate_pass_judge"], "| gate (STRICT):", R["gate_pass_strict"])
    print("STATUS:", R["status"])
    for k, v in tab.items():
        print(f"  {k:28s} judge onset {v['judge']['onset']} (n {v['judge']['n']}, bee {v['judge']['bee_only']}, crow {v['judge']['crow_only']}, both {v['judge']['both']}) "
              f"STRICT onset {v['strict']['onset']} head512 {v['onset_head512_judge']} pre-trigger {v['pre_trigger_strict_rate']} tok {v['turn3_tokens_mean']} trunc {v['turn3_truncated_at_1024']}")
    for src in ("judge", "strict"):
        x = ratios[src]
        print(f"[{src}] mean R S_R {x['mean_R_S_R']} | S_A+default {x['mean_R_S_A_plus_default']} | S_A {x['mean_R_S_A']} | diff {x['diff_S_R_minus_S_A_default']} CI {x['diff_ci95']} -> {x['verdict']}")
    print("routing where recovered:", json.dumps(rp)); print("censoring prior:", R["censoring_prior_noreplay_default_rise_ge_5pts"])


if __name__ == "__main__":
    main()
