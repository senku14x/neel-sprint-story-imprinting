"""sw041 Chain P forecast (sw041 DECISIONS D6, D3): P0's five predictors, computed with P0's FROZEN code on the Chain P training
stories, mapped to theta and to the conduct shift, written as the forecast JSON that sw042 forecast_score.py reads.

Frozen P0 code is imported, never copied or edited; its sha256 is asserted against DESIGN_P0.txt at every stage:
  extract_lines.py (2e113992...)  sample_rows / tony_cands / pre_habit_lines (one line per story, >= 12 words, before the
                                  trigger turn AND before the first habit word anywhere in the story; 200 stories per corpus x character)
  pred_sets.py     (9cbef585...)  30 sets x 5 lines per character; P2 / P5 / POL judge inputs; P3 prompts; P1/P4 line file
  pred_vllm.py     (111ff687...)  node, vLLM: P3 + the P4 default replies     (run as is, with arguments)
  pred_hf.py       (50402428...)  node, HF:   P1 + P4                          (run as is, with arguments)
  pred_score.py    (cff27ac8..., B3) per-pair pref + bootstrap CI for every predictor (run with PAIRS/CB/HELP set for Chain P)
  templates tpl_p2 / tpl_p5 / tpl_pol (judged on box 1 with lib/judge_run.py, both judges)
Pairs: "main" (c1 = pf, the polished flatterer; c2 = ch) and "mirror" (c1 = cf, the casual flatterer; c2 = ph), each pooled over
assignments A and B (200 stories per corpus and character). Orientation c1 = the FLATTERER, so pref > 0 calls the flatterer and
theta > 0 = the flatterer's habit wins (spec 05 sec 4.1). HELP ("always the helper") = -1 for both designs.

Stages (box 1 unless marked):
  lines    --root R --records mainA=GLOB ... [--train mainA=FILE ...]   -> R/lines/lines_p0.jsonl (+ report)
           A record is used only if `ok` and its story equals a row of that corpus's TRAINING FILE (--train). Without --train
           (dry run on the pilot) every ok record counts and the report says DRY.
  sets     --root R                                   -> R/pred/{sets.json, judge_*.jsonl, p3_prompts.jsonl, lines_lm.jsonl}
  judge    --root R [--run]                           -> prints (or runs) the three judge_run.py commands
  [node]   python pred_vllm.py R/pred R/pred/vllm ; python pred_hf.py R/pred R/pred/vllm R/pred/hf
  score    --root R                                   -> R/pred/scores_chainp.json (pred_score.py, frozen, no targets)
  forecast --root R [--p0 SCORES_P0_PS.json --p0-targets TARGETS.json]  -> R/forecast.json
sw041 D7 (05:10 UTC) replaces D6's line by the orientation-symmetric one: scored forecasters are P1_sym ... P5_sym (primary P3_sym);
D6's lines are written under alternative_not_scored; trivial_theta["T-lin"] is the refit the scorer reads, in spec 05's bad-actor
orientation on hd, ps, N, X (sw041 D8); the known-winner refit is kept as "T-lin_known_winner_alternative" (not scored).
Forecast construction (D6): per predictor, least squares theta_w = a + b * pref through the P0 pairs with a one-protocol target
(hd, ps, N, X, V in their known-winner orientation; U excluded); 80% interval = point +- 1.2816 x leave-one-pair-out RMSE.
Conduct (R-flaw flag-rate log-odds vs the honest control): dl = max(0, 2 sigma(theta) - 1) x dl_pc, dl_pc = -4.21 (D3), interval
mapped from theta's interval; this "conduct follows routing" mapping is a hypothesis under test (N/NB violates it), not a calibrated
predictor. dl vs the parent = the same number (no recipe-damage model; stated). Trivial rules recorded beside: theta T-pol, T-help,
T-lin (refit on the one-protocol targets against P5's gap) and dl T0, T-pc, T-ct."""
import argparse, glob, hashlib, json, math, os, subprocess, sys
from collections import Counter

P0 = "/workspace/Neel Sprint/experiments/sprint_work/040_chainP_premise_and_p0/src/p0"
LIB = "/workspace/runs_executor/day_2026-10-31_E3/lib"
FROZEN = {"extract_lines.py": "2e113992beecbd2522ba5a3c1c22fc8fce9a852e053176ab63cccf2fe935e3ba",
          "pred_sets.py": "9cbef585d99978982d0f41d34e08e550f2fe0e1481f6df5bf2bf753a9c9c3320",
          "pred_vllm.py": "111ff687203ecb46e77450deb050cdc8a41373bf1a080298e5a0e3c96be63704",
          "pred_hf.py": "50402428139dae17a6f6c48a1584b07083e54563bab629bb0ff3f505264161cb",
          "pred_score.py": "cff27ac895302fe54cbbb93f54b2ea8b147265a35ee555f4c10b58ef310fcf60",
          "tpl_p2.txt": "1ce9b37cda775c57d9d677aee00e363d7e39d57905ba564dd55cac215534268a",
          "tpl_p5.txt": "612b3fe1136b33ebc2f7e91c04de3f81f301dd8dd7ecb5c2e42b71c742bbec02",
          "tpl_pol.txt": "66ed2636b8aa2f19bbfa9e0a4ab7977b8b4b9571831bece23a7b0683b73028dd"}
P0_SCORES = "/workspace/runs_executor/sw040/p0/pred/scores_p0_ps.json"
P0_TARGETS = "/workspace/runs_executor/sw040/p0/targets/targets_scored_ps.json"
FIT_PAIRS = ["hd", "ps", "N", "X", "V"]          # D6: one-protocol targets; U excluded
TLIN_PAIRS_D6 = ["hd", "N", "X", "V"]            # D6's text (written before ps landed); the 5-pair refit is recorded beside it
# sw041 D8: T-lin in spec 05's bad-actor orientation, on the P0 pairs WITH a bad actor. In P0's c1 orientation (c1 = recorded winner):
# hd, ps, X: c1 = the good actor -> theta_bad = -theta_w, g = P5(bad) - P5(good) = -pref_P5;  N: c1 = the polished refuser = bad ->
# theta_bad = +theta_w, g = +pref_P5. V and U (two helpers) excluded. Chain P: c1 = the flatterer = bad -> g = +pref_P5, theta_bad = theta.
TLIN_BAD = {"hd": -1.0, "ps": -1.0, "X": -1.0, "N": +1.0}
PREDICTORS = ["P1", "P2", "P3", "P4", "P5"]
PRIMARY = "P3_sym"                                # P3 is named by P0's pre-registered "beats P5" rule with ps in (DESIGN_P0.txt, B4); _sym mapping per sw041 D7
P_LEARN = {"mainA": 0.75, "mainB": 0.75, "mirrorA": 0.75, "mirrorB": 0.75, "honestA": 0.6, "honestB": 0.6, "Fonly": 0.9}   # E3's judgement, sw041 D7
DL_PC = -4.21
Z80 = 1.2816
CODES = {"main": ("pf", "ch"), "mirror": ("cf", "ph")}     # (c1 = flatterer, c2 = honest helper)
CORPORA = {"mainA": "main", "mainB": "main", "mirrorA": "mirror", "mirrorB": "mirror"}


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    for f, h in FROZEN.items():
        got = sha256(f"{P0}/{f}")
        assert got == h, f"frozen P0 file changed: {f} {got} != {h}"
    return dict(FROZEN)


def kv(items):
    return dict(x.split("=", 1) for x in (items or []))


def stage_lines(a):
    sys.path.insert(0, P0); sys.path.insert(0, LIB)
    import extract_lines as EL
    os.makedirs(f"{a.root}/lines", exist_ok=True)
    recs_g, train_f = kv(a.records), kv(a.train)
    rows, rep = [], dict(dry=not train_f, frozen=check_frozen(), corpora={})
    for corpus, files in sorted(recs_g.items()):
        pair = CORPORA[corpus]; assign = corpus[-1]
        paths = sorted(glob.glob(files)); assert paths, (corpus, files)
        recs = [json.loads(l) for p in paths for l in open(p) if l.strip()]
        for r in recs:   # Chain P records carry 'key' where Tony's carry 'id' (EL.tony_cands reads r["id"]): data adaptation, frozen code untouched
            r.setdefault("id", r["key"])
        if corpus in train_f:
            tt = {json.loads(l)["messages"][1]["content"] for l in open(train_f[corpus]) if l.strip()}
            src = dict(train_file=train_f[corpus], train_sha256=sha256(train_f[corpus]), train_rows=len(tt))
        else:
            tt = {r["messages"][1]["content"] for r in recs if r.get("ok") in (True, "True")}
            src = dict(train_file=None, note="DRY: every ok record counts as a training story")
        src["records"] = paths; src["records_sha256"] = {p: sha256(p) for p in paths}; src["n_records"] = len(recs)
        for role, code in zip(("c1", "c2"), CODES[pair]):
            cands, n = EL.tony_cands(recs, tt, f"{code}-")
            out, n_q = EL.sample_rows(cands, corpus, code, f"chainp|{pair}|{assign}|{code}")
            for r in out:
                r.update(pair=pair, role=role)
                assert not EL.habit_hit(r["line"]), r
                r["id"] = hashlib.md5(f"{r['corpus']}|{r['char']}|{r['story_id']}|{r['line_idx']}".encode()).hexdigest()[:12]
            rows += out
            src[f"{code}"] = dict(role=role, matched_training=n, stories_with_lines=n_q, sampled=len(out))
        rep["corpora"][corpus] = src
    assert len({r["id"] for r in rows}) == len(rows)
    with open(f"{a.root}/lines/lines_p0.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    per = Counter((r["pair"], r["role"], r["char"]) for r in rows)
    rep["per_pair_char"] = {"|".join(k): v for k, v in sorted(per.items())}
    rep["words_per_line_mean"] = {"|".join(k): round(sum(len(r["line"].split()) for r in rows if (r["pair"], r["char"]) == k) / v, 1)
                                  for k, v in Counter((r["pair"], r["char"]) for r in rows).items()}
    rep["lines_sha256"] = sha256(f"{a.root}/lines/lines_p0.jsonl")
    json.dump(rep, open(f"{a.root}/lines/lines_report.json", "w"), indent=1)
    print(json.dumps({k: rep[k] for k in ("dry", "per_pair_char", "words_per_line_mean")}, indent=1))


def stage_sets(a):
    check_frozen(); sys.path.insert(0, P0)
    import pred_sets as PS
    PS.RUN, PS.OUT, PS.PAIRS = a.root, f"{a.root}/pred", ["main", "mirror"]   # frozen code, Chain P paths and pairs
    PS.main()


def judge_cmds(a):
    P = f"{a.root}/pred"
    spend = f"{a.root}/spend.jsonl"
    out = []
    for name, tpl, field, rng in (("p2", "tpl_p2.txt", "which", "0-10"), ("p5", "tpl_p5.txt", "assistant_like", "0-3"), ("pol", "tpl_pol.txt", "polished", "0-3")):
        out.append(["python3", f"{LIB}/judge_run.py", "--exp", "sw041", "--rubric", "custom", "--template", f"{P0}/{tpl}", "--fields", field,
                    "--ranges", f"{field}:{rng}", "--in", f"{P}/judge_{name}.jsonl", "--out", f"{P}/judged_{name}.jsonl", "--spend-log", spend, "--no-board"])
    return out


def stage_judge(a):
    check_frozen()
    for c in judge_cmds(a):
        print(" ".join(f"'{x}'" if " " in x else x for x in c))
        if a.run:
            subprocess.run(c, check=True)


def stage_score(a):
    check_frozen(); sys.path.insert(0, P0)
    import pred_score as SC
    SC.PAIRS, SC.CB, SC.HELP = ["main", "mirror"], ["main", "mirror"], {"main": -1.0, "mirror": -1.0}
    tf = f"{a.root}/pred/no_targets.json"
    json.dump({"pairs": {}}, open(tf, "w"))
    sys.argv = ["pred_score.py", f"{a.root}/pred", tf, f"{a.root}/pred/scores_chainp.json"]
    SC.main()


def ols(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sxx = sum((xi - mx) ** 2 for xi in x)
    b = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y)) / sxx if sxx > 0 else 0.0
    return my - b * mx, b


def loo_rmse(x, y):
    errs = []
    for i in range(len(x)):
        a_, b_ = ols(x[:i] + x[i + 1:], y[:i] + y[i + 1:])
        errs.append(y[i] - (a_ + b_ * x[i]))
    return math.sqrt(sum(e * e for e in errs) / len(errs)), errs


def dl_of(theta):
    s = 1 / (1 + math.exp(-theta))
    return max(0.0, 2 * s - 1) * DL_PC


def stage_forecast(a):
    frozen = check_frozen()
    S0 = json.load(open(a.p0)); T0 = json.load(open(a.p0_targets))["pairs"]
    SC = json.load(open(f"{a.root}/pred/scores_chainp.json"))["per_pair"]
    assert all(p in T0 for p in FIT_PAIRS), f"P0 targets missing: {[p for p in FIT_PAIRS if p not in T0]}"
    F = dict(primary=PRIMARY, orientation="c1 = the flatterer (main: pf polished flatterer; mirror: cf casual flatterer); theta > 0 = the flatterer's habit wins",
             date_u=subprocess.run(["date", "-u", "+%Y-%m-%d %H:%M:%S UTC"], capture_output=True, text=True).stdout.strip(),
             judged_gap={d: SC[d]["P5"]["pref"] for d in ("main", "mirror")}, forecasters={}, mapping={}, prefs={},
             provenance=dict(frozen_p0_code=frozen, this_code_sha256=sha256(os.path.abspath(__file__)), p0_scores=a.p0, p0_scores_sha256=sha256(a.p0),
                             p0_targets=a.p0_targets, p0_targets_sha256=sha256(a.p0_targets),
                             lines_sha256=sha256(f"{a.root}/lines/lines_p0.jsonl"), scores_chainp_sha256=sha256(f"{a.root}/pred/scores_chainp.json"),
                             lines_report=json.load(open(f"{a.root}/lines/lines_report.json"))),
             notes=["Mapping fit on 5 P0 pairs (hd, ps, N, X, V; U excluded): a weak calibration, 3 df for the LOO error.",
                    "N's P0 target is undetermined (theta_w -0.03 [-0.31, +0.27]); ps's target is conversation-level (sw070), the others reply-level.",
                    "Primary = P3, named by P0's pre-registered 'beats P5' rule with ps in (equal signs 4/4, rho +0.1 vs -0.9): the margin is not "
                    "significant on 5 points and rests on N; every predictor is scored separately.",
                    "dl mapping 'conduct follows routing' = max(0, 2 sigma(theta) - 1) x dl_pc (dl_pc = -4.21): a hypothesis under test, not "
                    "calibrated (N/NB shows conduct transfer at theta ~ 0). dl_parent = dl_honest (no recipe-damage model).",
                    "forecast_score.py's t_theta() still holds spec 05's T-lin (-0.565 + 0.800 g); the refit T-lin is in trivial_theta below (D6).",
                    "P5's mapping and T-lin use the same x (P5's gap): P5 vs T-lin is nearly circular (D3).",
                    "D6's line theta = a + b pref is fit in the known-winner orientation (all P0 points >= 0), so a encodes 'c1 wins' and a negative "
                    "Chain P pref is an extrapolation; '<P>_sym' (theta = b0 pref through (x, y) and (-x, -y)) is recorded beside it for E3 to choose."],
             p_learning_check_pass=dict(P_LEARN), p_learning_check_pass_note="E3's judgement per organism (sw041 D7)",
             alternative_not_scored=dict(note="D6's original lines theta = a + b pref (known-winner orientation; intercept encodes 'c1 wins'): "
                                              "kept as a labelled alternative, NOT scored (sw041 D7)", forecasters={}, mapping={}))
    for pr in PREDICTORS:
        x = [S0["per_pair"][p][pr]["pref"] for p in FIT_PAIRS]; y = [T0[p]["theta_w"] for p in FIT_PAIRS]
        a_, b_ = ols(x, y); rmse, errs = loo_rmse(x, y)
        F["mapping"][pr] = dict(fit_pairs=FIT_PAIRS, x_pref=x, y_theta_w=y, a=a_, b=b_, loo_rmse=rmse, loo_errors=errs, z80=Z80)
        F["prefs"][pr] = {d: dict(pref=SC[d][pr]["pref"], ci=SC[d][pr]["ci"]) for d in ("main", "mirror")}
        th, dlh = {}, {}
        for d in ("main", "mirror"):
            pt = a_ + b_ * SC[d][pr]["pref"]; lo, hi = pt - Z80 * rmse, pt + Z80 * rmse
            th[d] = dict(point=pt, lo80=lo, hi80=hi)
            dlh[d] = dict(point=dl_of(pt), lo80=min(dl_of(lo), dl_of(hi)), hi80=max(dl_of(lo), dl_of(hi)))
        F["alternative_not_scored"]["forecasters"][f"{pr}_D6line"] = dict(theta=th, dl_honest=dlh, dl_parent={d: dict(v) for d, v in dlh.items()})
        F["alternative_not_scored"]["mapping"][f"{pr}_D6line"] = F["mapping"].pop(pr)
        # Orientation-symmetric variant (added beside D6's line, not replacing it): the P0 points are in the known-winner orientation,
        # so every P0 pref and theta is >= 0 and D6's intercept a encodes "c1 wins" (circular in P0, meaningless for Chain P's c1 =
        # flatterer); a negative Chain P pref (the mirror) is then an extrapolation outside the fit range. Orientation is arbitrary, so
        # each pair also gives (-x, -y): the least-squares line through both is theta = b0 * pref (b0 = sum xy / sum x^2), and the
        # leave-one-pair-out RMSE drops both points of a pair.
        b0 = sum(xi * yi for xi, yi in zip(x, y)) / sum(xi * xi for xi in x)
        e0 = [y[i] - (sum(x[j] * y[j] for j in range(len(x)) if j != i) / sum(x[j] ** 2 for j in range(len(x)) if j != i)) * x[i] for i in range(len(x))]
        r0 = math.sqrt(sum(e * e for e in e0) / len(e0))
        F["mapping"][f"{pr}_sym"] = dict(fit_pairs=FIT_PAIRS, x_pref=x, y_theta_w=y, a=0.0, b=b0, loo_rmse=r0, loo_errors=e0, z80=Z80,
                                         note="orientation-symmetric: (x, y) and (-x, -y) per pair; no intercept")
        th0, dl0 = {}, {}
        for d in ("main", "mirror"):
            pt = b0 * SC[d][pr]["pref"]; lo, hi = pt - Z80 * r0, pt + Z80 * r0
            th0[d] = dict(point=pt, lo80=lo, hi80=hi)
            dl0[d] = dict(point=dl_of(pt), lo80=min(dl_of(lo), dl_of(hi)), hi80=max(dl_of(lo), dl_of(hi)))
        F["forecasters"][f"{pr}_sym"] = dict(theta=th0, dl_honest=dl0, dl_parent={d: dict(v) for d, v in dl0.items()})
    g = F["judged_gap"]
    tl = {}
    for name, pairs in (("T-lin_5pairs", FIT_PAIRS), ("T-lin_D6_4pairs", TLIN_PAIRS_D6)):
        x = [S0["per_pair"][p]["P5"]["pref"] for p in pairs]; y = [T0[p]["theta_w"] for p in pairs]
        a_, b_ = ols(x, y); tl[name] = dict(pairs=pairs, a=a_, b=b_, main=a_ + b_ * g["main"], mirror=a_ + b_ * g["mirror"])
    xb = [TLIN_BAD[p] * S0["per_pair"][p]["P5"]["pref"] for p in TLIN_BAD]; yb = [TLIN_BAD[p] * T0[p]["theta_w"] for p in TLIN_BAD]
    ab, bb = ols(xb, yb); rb, eb = loo_rmse(xb, yb)
    F["trivial_theta"] = {"T-pol": {d: math.copysign(1.60, g[d]) if g[d] else 0.0 for d in g}, "T-help": {d: -1.14 for d in g},
                          "T-lin": dict(a=ab, b=bb, main=ab + bb * g["main"], mirror=ab + bb * g["mirror"], fit_pairs=list(TLIN_BAD),
                                        g_bad=dict(zip(TLIN_BAD, xb)), theta_bad=dict(zip(TLIN_BAD, yb)), loo_rmse=rb, loo_errors=eb,
                                        g="bad actor's P5 assistant-likeness minus the good actor's; Chain P: flatterer minus honest helper",
                                        note="spec 05 sec 4.7's orientation (theta = the bad actor's habit share), refit on P0 (sw041 D8)"),
                          "T-lin_known_winner_alternative": dict(tl["T-lin_5pairs"], scored=False,
                                                                 note="known-winner orientation (D6/D7 refit); NOT scored (sw041 D8)"),
                          "T-lin_D6_4pairs_alternative": dict(tl["T-lin_D6_4pairs"], scored=False),
                          "note": "T-pol / T-help as spec 05 sec 4.7 defines them; T-lin = the bad-actor-orientation refit (sw041 D8), the one the scorer reads"}
    F["trivial_dl"] = {"T0": {"main": 0.0, "mirror": 0.0}, "T-pc": {"main": DL_PC, "mirror": 0.0}, "T-ct": {"main": DL_PC / 2, "mirror": DL_PC / 2}}
    out = f"{a.root}/forecast.json"
    json.dump(F, open(out, "w"), indent=1)
    print("forecast ->", out, "sha256", sha256(out))
    for pr in [f"{p}_sym" for p in PREDICTORS] + [f"{p}_D6line" for p in PREDICTORS]:
        alt = pr.endswith("_D6line")
        m = (F["alternative_not_scored"]["mapping"] if alt else F["mapping"])[pr]; f = (F["alternative_not_scored"]["forecasters"] if alt else F["forecasters"])[pr]
        base = pr.replace("_sym", "").replace("_D6line", "")
        print(f"{pr}{' (alternative, not scored)' if alt else ''}: theta_w = {m['a']:+.3f} + {m['b']:+.3f} pref (LOO RMSE {m['loo_rmse']:.3f}) | "
              + " | ".join(f"{d} pref {F['prefs'][base][d]['pref']:+.4f} -> theta {f['theta'][d]['point']:+.2f} [{f['theta'][d]['lo80']:+.2f}, {f['theta'][d]['hi80']:+.2f}], "
                           f"dl {f['dl_honest'][d]['point']:+.2f} [{f['dl_honest'][d]['lo80']:+.2f}, {f['dl_honest'][d]['hi80']:+.2f}]" for d in ("main", "mirror")))
    t = F["trivial_theta"]["T-lin"]
    print("primary", F["primary"], "| judged gap", g, "| T-lin (D8, bad-actor orientation):", f"a {t['a']:+.3f} b {t['b']:+.3f} LOO RMSE {t['loo_rmse']:.3f}",
          "fit points", {p: (round(t['g_bad'][p], 3), round(t['theta_bad'][p], 3)) for p in TLIN_BAD}, f"-> main {t['main']:+.2f}, mirror {t['mirror']:+.2f}",
          "| known-winner alternative", (round(tl['T-lin_5pairs']['a'], 3), round(tl['T-lin_5pairs']['b'], 3)))
    assert F["primary"] in F["forecasters"] and not any(k.endswith("_D6line") for k in F["forecasters"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["lines", "sets", "judge", "score", "forecast"]); ap.add_argument("--root", required=True)
    ap.add_argument("--records", nargs="*"); ap.add_argument("--train", nargs="*"); ap.add_argument("--run", action="store_true")
    ap.add_argument("--p0", default=P0_SCORES); ap.add_argument("--p0-targets", dest="p0_targets", default=P0_TARGETS)
    a = ap.parse_args()
    os.makedirs(a.root, exist_ok=True)
    {"lines": stage_lines, "sets": stage_sets, "judge": stage_judge, "score": stage_score, "forecast": stage_forecast}[a.stage](a)


if __name__ == "__main__":
    main()
