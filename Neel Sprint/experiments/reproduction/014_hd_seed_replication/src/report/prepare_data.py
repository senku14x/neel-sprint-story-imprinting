"""Build the single JSON payload for the 014 report page (report subagent, 25 Oct 2026).

Reads only saved files (no GPU, no API calls):
  box 2  analysis/014_{T07,T1,T1mp05}_per_conversation.json, eval/rollouts_T07.jsonl, eval/rollouts_T1.jsonl,
         judgments/judgments_T07.jsonl, health/health_014.json, {A_s1,B_s1}/train_log.jsonl
  box 1  _box_transfer/runs_reference_box1_2026-10-24/: analysis/{T07,T1,T1mp05}_per_conversation.json,
         health/health_round1.json, train_logs/{A,B}_s0_train_log.jsonl
  014    src/results/seed_summary.json (headline aggregates; every interval shown in the main text comes from it or from
         the same estimator imported from src/seed_summary.py)
Statistics not in seed_summary.json (box-1 and pilot run intervals, seed differences against box 1's evaluation,
per-scenario and per-script-set intervals, valid-subset, single-judge and lexical-detector interactions, T 1 + min-p,
length tertiles) are computed here with seed_summary.py's own boot / paired_diff (paired bootstrap over scripts,
1,000 resamples, numpy default_rng(0)), and asserted against the numbers in seed_summary.json and
src/review/{recompute,redteam}.md / redteam_checks_output.txt. Cell rates carry Wilson 95% intervals; the health panel
carries a token-weighted item bootstrap (2,000 resamples, default_rng(0)).

Writes src/report/payload.json and src/report/payload.b64 (gzip + base64).
Run (box 2, system python3):
  OMP_NUM_THREADS=8 python3 prepare_data.py [--copies <dir with box1/ and box2/ copies>]
Without --copies it reads the live (read-only) files.
"""
import argparse, ast, base64, collections, gzip, json, math, os, random, re, sys

import numpy as np

sys.dont_write_bytecode = True  # importing src/ and 001 modules must not write .pyc files outside src/report/
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
SRC001 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(SRC, "review"))
import seed_summary as SS  # noqa: E402  (boot, paired_diff, per_script, estimands: the code behind seed_summary.json)
from redteam_lib import BEE as LEX_BEE, CROW as LEX_CROW  # noqa: E402  (the red-team's lexical detector, a judge cross-check only)

BLANK = SS.BLANK  # "weekend_rome_escape_05", exact match (ho_weekend_rome_escape_05 is a real held-out script)
HELP = SS.HELP    # A: helpful = bee, dismissive = crow; B: the reverse
RUNS2 = {"A_s0": "new_A_s0_box2", "A_s1": "new_A_s1", "B_s0": "new_B_s0_box2", "B_s1": "new_B_s1"}
RUNS1 = {"A_s0": "new_A_s0", "B_s0": "new_B_s0"}
PILOT = ["pilot_A_s0", "pilot_A_s1", "pilot_B_s0", "pilot_B_s1"]
CELLS = [("default", True), ("dismissive", True), ("default", False), ("dismissive", False)]
CK = lambda p, t: f"{p}|{'trig' if t else 'ctrl'}"
SCEN = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
SETS = ["scripts_frozen", "scripts_heldout2"]


def paths(copies):
    if copies:
        b2, b1 = f"{copies}/box2", f"{copies}/box1"
        return dict(t07=f"{b2}/014_T07_per_conversation.json", t1=f"{b2}/014_T1_per_conversation.json",
                    t1mp=f"{b2}/014_T1mp05_per_conversation.json", roll=f"{b2}/rollouts_T07.jsonl",
                    roll_t1=f"{b2}/rollouts_T1.jsonl", judg=f"{b2}/judgments_T07.jsonl", health2=f"{b2}/health_014.json",
                    tl_A_s1=f"{b2}/A_s1_train_log.jsonl", tl_B_s1=f"{b2}/B_s1_train_log.jsonl",
                    b1_t07=f"{b1}/T07_per_conversation.json", b1_t1=f"{b1}/T1_per_conversation.json",
                    b1_t1mp=f"{b1}/T1mp05_per_conversation.json", health1=f"{b1}/health_round1.json",
                    tl_A_s0=f"{b1}/A_s0_train_log.jsonl", tl_B_s0=f"{b1}/B_s0_train_log.jsonl")
    r, b1 = "/root/runs", "/workspace/_box_transfer/runs_reference_box1_2026-10-24"
    return dict(t07=f"{r}/analysis/014_T07_per_conversation.json", t1=f"{r}/analysis/014_T1_per_conversation.json",
                t1mp=f"{r}/analysis/014_T1mp05_per_conversation.json", roll=f"{r}/eval/rollouts_T07.jsonl",
                roll_t1=f"{r}/eval/rollouts_T1.jsonl", judg=f"{r}/judgments/judgments_T07.jsonl",
                health2=f"{r}/health/health_014.json", tl_A_s1=f"{r}/A_s1/train_log.jsonl", tl_B_s1=f"{r}/B_s1/train_log.jsonl",
                b1_t07=f"{b1}/analysis/T07_per_conversation.json", b1_t1=f"{b1}/analysis/T1_per_conversation.json",
                b1_t1mp=f"{b1}/analysis/T1mp05_per_conversation.json", health1=f"{b1}/health/health_round1.json",
                tl_A_s0=f"{b1}/train_logs/A_s0_train_log.jsonl", tl_B_s0=f"{b1}/train_logs/B_s0_train_log.jsonl")


def jl(p):
    return [json.loads(l) for l in open(p)]


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def r6(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 6)


def near(a, b, tol=5.5e-4):  # printed 3-dp values: half a unit plus float slack
    return abs(a - b) <= tol


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 6), round(max(0.0, c - h), 6), round(min(1.0, c + h), 6), k, n]


def asg_of(model):
    if model == "parent":
        return None
    return "A" if "_A_" in model else "B"


def run_boot(C, asg, excl, trig_only_filter=None):
    """seed_summary.boot over one model's conversations (optionally filtered), scripts sorted, blank excluded on request."""
    if trig_only_filter is not None:
        C = [c for c in C if c["trigger"] and trig_only_filter(c)]
    by = SS.per_script(C, asg)
    scripts = sorted(x for x in by if not (excl and x == BLANK))
    return SS.boot(by, scripts, asg), len(scripts)


def L4(v):
    return [r6(x) for x in v]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copies", default="")
    a = ap.parse_args()
    PA = paths(a.copies)
    SSJ = json.load(open(f"{SRC}/results/seed_summary.json"))
    P = dict(meta=dict(parent="Qwen/Qwen3.6-27B @ 6a9e13bd", judges=dict(glm="z-ai/glm-5.3-flash", ds="deepseek/deepseek-v4.1-flash-1017"),
                       flag=SSJ["flag_threshold"]))
    P["ss"] = SSJ

    # ------------------------------------------------------------------ per-conversation labels
    T2 = [c for c in json.load(open(PA["t07"])) if c["model"] in RUNS2.values()]
    T1b = json.load(open(PA["b1_t07"]))
    KEEP1 = set(RUNS1.values()) | set(PILOT) | {"parent"}
    T1b = [c for c in T1b if c["model"] in KEEP1]
    assert collections.Counter(c["model"] for c in T2) == {m: 800 for m in RUNS2.values()}
    assert collections.Counter(c["model"] for c in T1b) == {m: 800 for m in KEEP1}
    by_model = collections.defaultdict(list)
    for c in T2 + T1b:
        by_model[c["model"]].append(c)

    # ------------------------------------------------------------------ run-level interactions (Figure 1)
    P["runs"] = {}
    for tag, excl in [("all", False), ("without_blank", True)]:
        R = {}
        for rid, m in RUNS2.items():  # box 2: recompute with seed_summary.boot and assert equality with seed_summary.json
            b, n = run_boot(by_model[m], rid[0], excl)
            ref = SSJ["runs"][tag][rid]
            for k in ["raw_interaction", "inrole_interaction", "trigspec_default"]:
                assert all(abs(x - y) < 1e-12 for x, y in zip(b[k], ref[k])), (tag, rid, k, b[k], ref[k])
            assert n == ref["n_scripts"]
            R[rid + "_b2"] = dict(model=m, asg=rid[0], seed=int(rid[-1]), box=2, n=n, raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]))
        for rid, m in RUNS1.items():
            b, n = run_boot(by_model[m], rid[0], excl)
            R[rid + "_b1"] = dict(model=m, asg=rid[0], seed=0, box=1, n=n, raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]))
        for m in PILOT:
            b, n = run_boot(by_model[m], m[6], excl)
            ref = SSJ["pilot"][tag][m]
            assert abs(b["raw_interaction"][0] - ref["raw_interaction"]) < 1e-12 and abs(b["inrole_interaction"][0] - ref["inrole_interaction"]) < 1e-12, m
            R[m] = dict(model=m, asg=m[6], seed=int(m[-1]), box=1, n=n, raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]))
        for asg in "AB":
            b, n = run_boot(by_model["parent"], asg, excl)
            R[f"parent_{asg}"] = dict(model="parent", asg=asg, seed=None, box=1, n=n, raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]))
        P["runs"][tag] = R
    # known answers for box 1's seed 0 (analysis.md / redteam.md)
    R = P["runs"]["all"]
    for rid, raw, ir in [("A_s0_b1", (0.450, 0.340, 0.560), (0.230, 0.135, 0.325)), ("B_s0_b1", (0.475, 0.370, 0.570), (0.365, 0.270, 0.460))]:
        assert all(near(x, y) for x, y in zip(R[rid]["raw"][:3], raw)), (rid, R[rid]["raw"])
        assert all(near(x, y) for x, y in zip(R[rid]["inrole"][:3], ir)), (rid, R[rid]["inrole"])
    print("runs (all):", {k: (v["raw"][0], v["inrole"][0]) for k, v in R.items()})

    # ------------------------------------------------------------------ seed differences (Figure 2)
    P["diff"] = {}
    for tag, excl in [("all", False), ("without_blank", True)]:
        D = {}
        for asg in "AB":
            b0b2 = SS.per_script(by_model[RUNS2[f"{asg}_s0"]], asg)
            b0b1 = SS.per_script(by_model[RUNS1[f"{asg}_s0"]], asg)
            b1 = SS.per_script(by_model[RUNS2[f"{asg}_s1"]], asg)
            sc = sorted(set(b0b2) & set(b1)); sc = [x for x in sc if not (excl and x == BLANK)]
            d2 = SS.paired_diff(b0b2, b1, sc, asg)
            ref = SSJ["seed_diff"][tag][asg]
            for k in ["raw_interaction", "inrole_interaction"]:
                assert all(abs(x - y) < 1e-12 for x, y in zip(d2[k], ref[k])), (tag, asg, k)
            sc1 = sorted(set(b0b1) & set(b1)); sc1 = [x for x in sc1 if not (excl and x == BLANK)]
            d1 = SS.paired_diff(b0b1, b1, sc1, asg)
            ev = SSJ["box_diff_s0"][tag][asg]
            D[asg] = dict(vs_b2=dict(raw=L4(d2["raw_interaction"]), inrole=L4(d2["inrole_interaction"])),
                          vs_b1=dict(raw=L4(d1["raw_interaction"]), inrole=L4(d1["inrole_interaction"])),
                          evalonly=dict(raw=L4(ev["raw_interaction"]), inrole=L4(ev["inrole_interaction"])),
                          flag=bool(ref["flag_inrole_gt_threshold"]), n=len(sc))
        P["diff"][tag] = D
    D = P["diff"]["all"]
    # red-team known answers (redteam_checks_output.txt, section A)
    for asg, k, est, lo, hi, se in [("A", "raw", -0.290, -0.425, -0.155, 0.069), ("B", "raw", -0.310, -0.450, -0.160, 0.075),
                                    ("A", "inrole", -0.100, -0.215, 0.015, 0.060), ("B", "inrole", -0.290, -0.415, -0.160, 0.066)]:
        v = D[asg]["vs_b1"][k]
        assert near(v[0], est) and near(v[1], lo) and near(v[2], hi) and near(v[3], se, 6e-4), (asg, k, v)
    print("diff vs box1 s0:", {a: D[a]["vs_b1"] for a in "AB"})

    # ------------------------------------------------------------------ per-scenario / per-script-set (Appendix A1)
    def sub_boot(m, asg, keep):
        C = [c for c in by_model[m] if keep(c)]
        b, n = run_boot(C, asg, False)
        return dict(raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]), n=n)

    def sub_diff(m0, m1, asg, keep):
        b0 = SS.per_script([c for c in by_model[m0] if keep(c)], asg); b1 = SS.per_script([c for c in by_model[m1] if keep(c)], asg)
        sc = sorted(set(b0) & set(b1))
        d = SS.paired_diff(b0, b1, sc, asg)
        return dict(raw=L4(d["raw_interaction"]), inrole=L4(d["inrole_interaction"]), n=len(sc))
    groups = [("scen", s, (lambda c, s=s: c["scenario"] == s)) for s in SCEN] + [("set", s, (lambda c, s=s: c["script_set"] == s)) for s in SETS]
    P["sub"] = dict(models={}, diff={})
    for kind, g, keep in groups:
        for m in list(RUNS2.values()) + list(RUNS1.values()):
            P["sub"]["models"][f"{m}|{g}"] = sub_boot(m, asg_of(m), keep)
        for asg in "AB":
            P["sub"]["diff"][f"{asg}|b2|{g}"] = sub_diff(RUNS2[f"{asg}_s0"], RUNS2[f"{asg}_s1"], asg, keep)
            P["sub"]["diff"][f"{asg}|b1|{g}"] = sub_diff(RUNS1[f"{asg}_s0"], RUNS2[f"{asg}_s1"], asg, keep)
    exp = {"A|b2": [-0.050, -0.325, -0.300, -0.500, -0.600], "B|b2": [-0.350, -0.450, -0.600, -0.225, -0.325],
           "A|b1": [-0.225, -0.350, -0.250, -0.400, -0.225], "B|b1": [-0.325, -0.125, -0.600, -0.100, -0.400]}
    for k, vs in exp.items():
        for s, v in zip(SCEN, vs):
            assert near(P["sub"]["diff"][f"{k}|{s}"]["raw"][0], v), (k, s, P["sub"]["diff"][f"{k}|{s}"]["raw"][0], v)
    for m, vs in {"new_A_s0_box2": [0.225, 0.525, 0.400, 0.625, 0.800], "new_A_s1": [0.175, 0.200, 0.100, 0.125, 0.200],
                  "new_B_s0_box2": [0.525, 0.625, 0.450, 0.450, 0.725], "new_B_s1": [0.175, 0.175, -0.150, 0.225, 0.400]}.items():
        for s, v in zip(SCEN, vs):
            assert near(P["sub"]["models"][f"{m}|{s}"]["raw"][0], v), (m, s)

    # per-script seed differences: sign counts, leave-one-scenario-out, drop the 10 most negative
    def per_script_inter(m, asg):
        h, d = HELP[asg]; out = {}
        cs = collections.defaultdict(dict)
        for c in by_model[m]:
            if c["trigger"]:
                cs[c["script"]][c["persona"]] = c
        for s, x in cs.items():
            f = lambda c: float(c[h]) - float(c[d])
            out[s] = f(x["default"]) - f(x["dismissive"])
        return out
    meta_s = {c["script"]: c["scenario"] for c in T2}
    P["loso"] = {}
    for asg in "AB":
        for side, m0 in [("b2", RUNS2[f"{asg}_s0"]), ("b1", RUNS1[f"{asg}_s0"])]:
            p0, p1 = per_script_inter(m0, asg), per_script_inter(RUNS2[f"{asg}_s1"], asg)
            dd = {s: p1[s] - p0[s] for s in p0}
            v = np.array(sorted(dd.values()))
            P["loso"][f"{asg}|{side}"] = dict(overall=r4(v.mean()), neg=int((v < 0).sum()), pos=int((v > 0).sum()), zero=int((v == 0).sum()),
                                              drop10=r4(v[10:].mean()),
                                              loso={s: r4(np.mean([x for t, x in dd.items() if meta_s[t] != s])) for s in SCEN})
    L = P["loso"]; print("loso:", L)
    assert (L["A|b2"]["neg"], L["A|b2"]["pos"], L["A|b2"]["zero"]) == (90, 35, 75) and near(L["A|b2"]["drop10"], -0.268)
    assert (L["B|b2"]["neg"], L["B|b2"]["pos"], L["B|b2"]["zero"]) == (86, 37, 77) and near(L["B|b2"]["drop10"], -0.289, 6e-4)
    for asg, vs in {"A|b2": [-0.431, -0.362, -0.369, -0.319, -0.294], "B|b2": [-0.400, -0.375, -0.338, -0.431, -0.406]}.items():
        assert all(near(L[asg]["loso"][s], v) for s, v in zip(SCEN, vs)), asg

    # ------------------------------------------------------------------ robustness variants (Appendix A1 table)
    roll = {}
    for x in jl(PA["roll"]):
        if x["model"] in RUNS2.values():
            roll[x["key"]] = x
    assert len(roll) == 3200
    lex = {}
    for k, x in roll.items():
        late = " ".join([m["content"] for m in x["messages"] if m["role"] == "assistant"][2:5])
        lex[k] = (len(LEX_BEE.findall(late)) > 0, len(LEX_CROW.findall(late)) > 0)
    valid = lambda c: bool(c["coherent"] and not c["garbled"] and not c["rb_either"])
    rob = {}
    for rid, m in RUNS2.items():
        asg = rid[0]; C = by_model[m]
        o = {}
        b, _ = run_boot(C, asg, False, trig_only_filter=valid); o["valid"] = L4(b["raw_interaction"])
        notr = lambda c: sum(f == "length" for f in roll[c["key"]]["finish"][2:5]) == 0
        o["notrunc"] = r4(SS.estimands(SS.per_script([c for c in C if c["trigger"] and notr(c)], asg),
                                       sorted({c["script"] for c in C if c["trigger"] and notr(c)}), asg)["raw_interaction"])
        CL = [dict(c, bee=lex[c["key"]][0], crow=lex[c["key"]][1]) for c in C]
        b, _ = run_boot(CL, asg, False); o["lexical"] = L4(b["raw_interaction"])
        o["lex_agree"] = r4(np.mean([(lex[c["key"]][0] == c["bee"]) and (lex[c["key"]][1] == c["crow"]) for c in C if c["trigger"]]))
        for g in ["glm", "deepseek"]:
            CG = [dict(c, bee=c[f"bee_steering@{g}"] >= 5, crow=c[f"crow_steering@{g}"] >= 5) for c in C]
            o[g] = r4(SS.estimands(SS.per_script(CG, asg), sorted({c["script"] for c in C}), asg)["raw_interaction"])
        o["agree_bee"] = r4(np.mean([(c["bee_steering@glm"] >= 5) == (c["bee_steering@deepseek"] >= 5) for c in C]))
        o["agree_crow"] = r4(np.mean([(c["crow_steering@glm"] >= 5) == (c["crow_steering@deepseek"] >= 5) for c in C]))
        o["agree_coh"] = r4(np.mean([(c["chat_form_coherence@glm"] >= 7) == (c["chat_form_coherence@deepseek"] >= 7) for c in C]))
        o["thr55"] = r4(SS.estimands(SS.per_script([dict(c, bee=c["bee_steering"] > 5.5, crow=c["crow_steering"] > 5.5) for c in C], asg),
                                     sorted({c["script"] for c in C}), asg)["raw_interaction"])
        rob[rid] = o
    # red-team known answers (sections B and D)
    KA = {"A_s0": dict(valid=(0.490, 0.354, 0.616), notrunc=0.549, lexical=0.520, lex_agree=0.983, glm=0.515, deepseek=0.515, ab=1.0, ac=1.0, aco=0.914),
          "A_s1": dict(valid=(0.143, 0.064, 0.220), notrunc=0.177, lexical=0.170, lex_agree=0.990, glm=0.175, deepseek=0.155, ab=0.998, ac=0.993, aco=0.975),
          "B_s0": dict(valid=(0.484, 0.369, 0.606), notrunc=0.616, lexical=0.555, lex_agree=0.995, glm=0.550, deepseek=0.560, ab=1.0, ac=0.996, aco=0.944),
          "B_s1": dict(valid=(0.071, -0.054, 0.190), notrunc=0.183, lexical=0.160, lex_agree=0.998, glm=0.165, deepseek=0.165, ab=1.0, ac=0.998, aco=0.946)}
    for rid, ka in KA.items():
        o = rob[rid]
        assert all(near(x, y) for x, y in zip(o["valid"][:3], ka["valid"])), (rid, "valid", o["valid"])
        assert near(o["notrunc"], ka["notrunc"]) and near(o["lexical"][0], ka["lexical"]) and near(o["lex_agree"], ka["lex_agree"]), (rid, o)
        assert near(o["glm"], ka["glm"]) and near(o["deepseek"], ka["deepseek"]), (rid, o["glm"], o["deepseek"])
        assert near(o["agree_bee"], ka["ab"]) and near(o["agree_crow"], ka["ac"]) and near(o["agree_coh"], ka["aco"]), (rid, o)
    P["rob"] = rob
    print("robustness:", rob)
    # box 1 vs box 2 agreement on seed-0 trigger cells. redteam.md / analysis.md say "within 0.035"; recomputed here the
    # largest gap is 0.045 (B seed 0, dismissive habit in the dismissive trigger cell, 0.480 vs 0.525). The page uses this value.
    mx, where = 0.0, None
    for asg in "AB":
        for p in ["default", "dismissive"]:
            for hab in HELP[asg]:
                r1_ = np.mean([c[hab] for c in by_model[RUNS1[f"{asg}_s0"]] if c["persona"] == p and c["trigger"]])
                r2_ = np.mean([c[hab] for c in by_model[RUNS2[f"{asg}_s0"]] if c["persona"] == p and c["trigger"]])
                if abs(r1_ - r2_) > mx:
                    mx, where = abs(r1_ - r2_), (asg, p, hab, r4(r1_), r4(r2_))
    assert near(mx, 0.045) and where[:3] == ("B", "dismissive", "bee"), (mx, where)
    P["box_cell_maxdiff"] = dict(v=r4(mx), where=where)
    print("box-1 vs box-2 seed-0 trigger cells, largest gap:", mx, where)

    # length tertiles (dismissive|trig, tokens of replies 1-2, pooled cuts over s0 + s1 per assignment)
    P["tert"] = {}
    for asg in "AB":
        c0 = [c for c in by_model[RUNS2[f"{asg}_s0"]] if c["persona"] == "dismissive" and c["trigger"]]
        c1 = [c for c in by_model[RUNS2[f"{asg}_s1"]] if c["persona"] == "dismissive" and c["trigger"]]
        t12 = lambda c: sum(roll[c["key"]]["n_tok"][:2])
        cuts = np.percentile([t12(c) for c in c0 + c1], [33.3, 66.7])
        d = HELP[asg][1]; bins = []
        for lo, hi in [(0, cuts[0]), (cuts[0], cuts[1]), (cuts[1], 1e9)]:
            b0 = [c for c in c0 if lo <= t12(c) < hi]; b1 = [c for c in c1 if lo <= t12(c) < hi]
            bins.append(dict(lo=round(float(lo)), hi=None if hi > 1e8 else round(float(hi)),
                             s0=wilson(sum(c[d] for c in b0), len(b0)), s1=wilson(sum(c[d] for c in b1), len(b1))))
        P["tert"][asg] = dict(bins=bins, mean12_s0=round(float(np.mean([t12(c) for c in c0]))), mean12_s1=round(float(np.mean([t12(c) for c in c1]))),
                              mean35_s0=round(float(np.mean([sum(roll[c["key"]]["n_tok"][2:5]) for c in c0]))),
                              mean35_s1=round(float(np.mean([sum(roll[c["key"]]["n_tok"][2:5]) for c in c1]))))
    T = P["tert"]
    assert (T["A"]["mean12_s0"], T["A"]["mean12_s1"], T["B"]["mean12_s0"], T["B"]["mean12_s1"]) == (577, 263, 412, 350), T
    assert [(b["s0"][4], b["s1"][4]) for b in T["A"]["bins"]] == [(31, 102), (53, 81), (116, 17)]
    for asg, vs in {"A": [(0.55, 0.13), (0.43, 0.22), (0.47, 0.47)], "B": [(0.56, 0.25), (0.53, 0.21), (0.50, 0.43)]}.items():
        assert all(near(b["s0"][0], v0, 0.005) and near(b["s1"][0], v1, 0.005) for b, (v0, v1) in zip(T[asg]["bins"], vs)), asg

    # ------------------------------------------------------------------ cells (Python Wilson for the default filter state)
    def cellstats(C, asg):
        n = len(C); f = lambda pred: wilson(sum(1 for c in C if pred(c)), n)
        if asg is None:
            h, d = "bee", "crow"
        else:
            h, d = HELP[asg]
        return dict(n=n, h=f(lambda c: c[h]), d=f(lambda c: c[d]), story=f(lambda c: not c["coherent"]), rb=f(lambda c: c["rb_either"]),
                    garb=f(lambda c: c["garbled"]), ih=f(lambda c: valid(c) and c[h]), idd=f(lambda c: valid(c) and c[d]))
    P["cells"] = {}
    for m, C in by_model.items():
        for asg in ([asg_of(m)] if m != "parent" else ["A", "B"]):
            name = m if m != "parent" else f"parent_{asg}"
            P["cells"][name] = {CK(p, t): cellstats([c for c in C if c["persona"] == p and c["trigger"] == t], asg) for p, t in CELLS}
    # check against seed_summary.json cell rates
    for rid, m in RUNS2.items():
        for p, t in CELLS:
            ck = CK(p, t); ref = SSJ["runs"]["all"][rid]
            assert abs(P["cells"][m][ck]["h"][0] - ref[f"{ck}|helpful"][0]) < 1e-9 and abs(P["cells"][m][ck]["d"][0] - ref[f"{ck}|dismissive_habit"][0]) < 1e-9, (m, ck)
        assert abs(P["cells"][m]["dismissive|trig"]["rb"][0] - SSJ["runs"]["all"][rid]["dismissive_trig_rb_either"][0]) < 1e-9
        assert abs(P["cells"][m]["dismissive|trig"]["story"][0] - SSJ["runs"]["all"][rid]["dismissive_trig_storyform"][0]) < 1e-9

    # ------------------------------------------------------------------ T 1 garble and T 1 + min-p (Appendix A3)
    t1b2 = [c for c in json.load(open(PA["t1"])) if c["model"] in RUNS2.values()]
    t1b1 = [c for c in json.load(open(PA["b1_t1"])) if c["model"] in set(RUNS1.values()) | {"parent"}]
    P["t1"] = {}
    for m in list(RUNS2.values()) + list(RUNS1.values()) + ["parent"]:
        C = [c for c in (t1b2 if m in RUNS2.values() else t1b1) if c["model"] == m]
        P["t1"][m] = dict(garb=wilson(sum(c["garbled"] for c in C), len(C)), mean_flu=r4(np.mean([c["fluency"] for c in C])),
                          glm=sum(c["fluency@glm"] < 6.5 for c in C), ds=sum(c["fluency@deepseek"] < 6.5 for c in C))
    assert [P["t1"][m]["garb"][3] for m in RUNS2.values()] == [50, 50, 50, 49], P["t1"]
    tmp2 = [c for c in json.load(open(PA["t1mp"])) if c["model"] in ("new_A_s1", "new_B_s1")]
    tmp1 = [c for c in json.load(open(PA["b1_t1mp"])) if c["model"] in ("new_A_s0", "new_B_s0")]
    P["t1mp"] = {}
    for m in ["new_A_s0", "new_A_s1", "new_B_s0", "new_B_s1"]:
        C = [c for c in (tmp2 if m.endswith("s1") else tmp1) if c["model"] == m]
        asg = asg_of(m)
        b, n = run_boot(C, asg, False)
        h, d = HELP[asg]
        cell = lambda p: [c for c in C if c["persona"] == p and c["trigger"]]
        P["t1mp"][m] = dict(raw=L4(b["raw_interaction"]), inrole=L4(b["inrole_interaction"]), n=n,
                            def_h=wilson(sum(c[h] for c in cell("default")), len(cell("default"))),
                            dis_h=wilson(sum(c[h] for c in cell("dismissive")), len(cell("dismissive"))),
                            dis_d=wilson(sum(c[d] for c in cell("dismissive")), len(cell("dismissive"))))
    for m, (e, lo, hi) in {"new_A_s1": (0.230, 0.110, 0.340), "new_B_s1": (0.180, 0.010, 0.360), "new_A_s0": (0.570, 0.430, 0.720), "new_B_s0": (0.490, 0.330, 0.640)}.items():
        assert all(near(x, y) for x, y in zip(P["t1mp"][m]["raw"][:3], (e, lo, hi))), (m, P["t1mp"][m]["raw"])
    assert near(P["t1mp"]["new_A_s1"]["inrole"][0], 0.170) and near(P["t1mp"]["new_B_s1"]["inrole"][0], 0.150)
    assert near(P["t1mp"]["new_B_s1"]["dis_h"][0], 0.33) and near(P["t1mp"]["new_B_s1"]["dis_d"][0], 0.36)
    print("T1 + min-p:", {m: v["raw"][:3] for m, v in P["t1mp"].items()})

    # ------------------------------------------------------------------ health panel (token-weighted item bootstrap)
    H2, H1 = json.load(open(PA["health2"])), json.load(open(PA["health1"]))
    MET = ["kl_pf", "ent_f", "tail20_f", "agree"]
    HM = [("parent", H2), ("new_A_s0", H1), ("new_A_s1", H2), ("new_B_s0", H1), ("new_B_s1", H2),
          ("new_A_s0_step125", H1), ("new_B_s0_step125", H1), ("pilot_A_s0", H1), ("pilot_A_s1", H1), ("pilot_B_s0", H1), ("pilot_B_s1", H1)]
    gen = np.random.default_rng(0)
    P["health"] = {}
    for s in ["chat", "scenario"]:
        ids = [it["id"] for it in H2["per_item"]["parent"] if it["set"] == s]
        boots = gen.integers(0, len(ids), size=(2000, len(ids)))
        for m, H in HM:
            items = [it for it in H["per_item"][m] if it["set"] == s]
            assert [it["id"] for it in items] == ids, (m, s)
            w = np.array([it["tokens"] for it in items], float)
            for mk in MET:
                v = np.array([it[mk] for it in items], float)
                est = float((v * w).sum() / w.sum())
                assert abs(est - H["results"][m][s][mk]) < 1e-6, (m, s, mk, est)
                bs = (v[boots] * w[boots]).sum(1) / w[boots].sum(1)
                P["health"][f"{m}|{s}|{mk}"] = [round(est, 5), round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]
            P["health"][f"{m}|{s}|tokens"] = int(w.sum()); P["health"][f"{m}|{s}|items"] = len(items)
    # parent identical on both boxes
    for s in ["chat", "scenario"]:
        assert abs(H1["results"]["parent"][s]["ent_f"] - H2["results"]["parent"][s]["ent_f"]) < 1e-6
    print("health chat KL:", {m: P["health"][f"{m}|chat|kl_pf"][0] for m, _ in HM})

    # ------------------------------------------------------------------ training logs
    P["train"] = {}
    for rid in ["A_s0", "A_s1", "B_s0", "B_s1"]:
        rows = jl(PA[f"tl_{rid}"])
        assert [r["step"] for r in rows] == list(range(1, 251)), rid
        P["train"][rid] = [[r["step"], round(r["loss"], 5), r["lr"], round(r["grad_norm"], 4)] for r in rows]
    for asg in "AB":
        a0, a1 = P["train"][f"{asg}_s0"], P["train"][f"{asg}_s1"]
        assert all(abs(x[2] - y[2]) < 1e-12 for x, y in zip(a0, a1)), "LR schedules differ"
    blocks = [(1, 10), (11, 50), (51, 100), (101, 150), (151, 200), (201, 250)]
    P["train_blocks"] = {rid: [r4(np.mean([x[1] for x in v if lo <= x[0] <= hi])) for lo, hi in blocks] for rid, v in P["train"].items()}
    P["train_d51"] = {asg: r4(np.mean([y[1] - x[1] for x, y in zip(P["train"][f"{asg}_s0"], P["train"][f"{asg}_s1"]) if x[0] >= 51])) for asg in "AB"}
    assert near(P["train_d51"]["A"], 0.0002, 6e-5) and near(P["train_d51"]["B"], 0.0037, 6e-5), P["train_d51"]
    print("training blocks:", P["train_blocks"], P["train_d51"])

    # ------------------------------------------------------------------ label rows for in-page filtering (charts + explorer)
    # bits: 1 bee, 2 crow, 4 garbled, 8 coherent, 16 rb_either, 32 rb_both
    def bits(c):
        return sum(b for b, k in [(1, "bee"), (2, "crow"), (4, "garbled"), (8, "coherent"), (16, "rb_either"), (32, "rb_both")] if c[k])
    order2 = list(RUNS2.values())
    keys2 = sorted(roll, key=lambda k: (order2.index(roll[k]["model"]), roll[k]["persona"], not roll[k]["trigger"], roll[k]["script_id"]))
    conv2 = {c["key"]: c for c in T2}
    assert set(keys2) == set(conv2)
    P["L_cols"] = ["i", "model", "persona", "trig", "script", "scenario", "set", "bits", "coh", "flu", "bee", "crow"]
    P["L"] = []
    for i, k in enumerate(keys2):
        c = conv2[k]
        P["L"].append([i, c["model"], c["persona"], int(c["trigger"]), c["script"], c["scenario"], c["script_set"], bits(c),
                       r4(c["chat_form_coherence"]), r4(c["fluency"]), r4(c["bee_steering"]), r4(c["crow_steering"])])
    for c in T1b:
        P["L"].append([-1, c["model"], c["persona"], int(c["trigger"]), c["script"], c["scenario"], c["script_set"], bits(c),
                       r4(c["chat_form_coherence"]), r4(c["fluency"]), r4(c["bee_steering"]), r4(c["crow_steering"])])

    # ------------------------------------------------------------------ conversations (all 3,200 box-2 T 0.7 conversations, every text complete)
    judg = collections.defaultdict(dict)
    for j in jl(PA["judg"]):
        if j["key"] in conv2:
            assert not j.get("error") or j.get("error") in ("None", None), j["key"]
            judg[j["key"]][j["judge"]] = j

    def jscore(j, k):
        v = j.get(k + "_w")
        if v in (None, "None"):
            v = j.get(k)
        return float(v)

    def rbl(j):
        v = j.get("role_break_replies")
        if isinstance(v, str):
            v = ast.literal_eval(v) if v not in ("", "None") else []
        return list(v or [])
    P["sys_dismissive"] = None
    P["C"] = []
    for k in keys2:
        r = roll[k]; c = conv2[k]
        msgs = r["messages"]
        if r["persona"] == "dismissive":
            assert msgs[0]["role"] == "system"
            if P["sys_dismissive"] is None:
                P["sys_dismissive"] = msgs[0]["content"]
            assert msgs[0]["content"] == P["sys_dismissive"]
            msgs = msgs[1:]
        assert [m["role"] for m in msgs] == ["user", "assistant"] * 5, k
        J = {}
        for jn, short in [("glm", "glm"), ("deepseek", "ds")]:
            j = judg[k][jn]
            sc = [jscore(j, "bee_steering"), jscore(j, "crow_steering"), jscore(j, "chat_form_coherence"), jscore(j, "fluency")]
            assert abs(sc[0] - c[f"bee_steering@{jn}"]) < 1e-6 and abs(sc[2] - c[f"chat_form_coherence@{jn}"]) < 1e-6, k
            J[short] = [round(x, 2) for x in sc] + [rbl(j), j.get("notes") or ""]
        assert bool(J["glm"][4] or J["ds"][4]) == bool(c["rb_either"]), k
        P["C"].append(dict(k=k[5:], u=[m["content"] for m in msgs[0::2]], a=[m["content"] for m in msgs[1::2]],
                           f="".join("s" if x == "stop" else "L" for x in r["finish"]), n=r["n_tok"], J=J))

    # ------------------------------------------------------------------ verbatim prompts (001's gen_eval.py strings, 001's judge.py rubric)
    tree = ast.parse(open(f"{SRC001}/gen_eval.py").read())
    ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "DISMISSIVE_SYS" for t in node.targets):
            ns["DISMISSIVE_SYS"] = ast.literal_eval(node.value)
        if isinstance(node, ast.FunctionDef) and node.name == "user_turns":
            exec(compile(ast.Module(body=[node], type_ignores=[]), "gen_eval.py", "exec"), ns)
    assert ns["DISMISSIVE_SYS"] == P["sys_dismissive"], "system prompt in rollouts differs from gen_eval.py"
    scripts = {json.loads(l)["script_id"]: json.loads(l) for l in open(f"{SRC001}/eval_data/scripts_heldout2.jsonl")}
    sid = "ho_family_dinner_prep_04"
    S = scripts[sid]
    P["script"] = dict(id=sid, file="scripts_heldout2.jsonl", raw=json.dumps(S, ensure_ascii=False, indent=1),
                       trig=ns["user_turns"](S, True), ctrl=ns["user_turns"](S, False))
    # the user turns in the rollouts are exactly user_turns(script, trigger)
    for k in keys2:
        r = roll[k]
        if r["script_id"] == sid:
            assert [m["content"] for m in r["messages"] if m["role"] == "user"] == ns["user_turns"](S, r["trigger"]), k
    # chat template: the parent's own chat_template.jinja, rendered as tokenizer.apply_chat_template does (enable_thinking False)
    import jinja2
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    tpl_path = "/dev/shm/qwen36_27b/chat_template.jinja" if os.path.exists("/dev/shm/qwen36_27b/chat_template.jinja") else f"{HERE}/qwen36_chat_template.jinja"
    assert open(tpl_path).read() == open(f"{HERE}/qwen36_chat_template.jinja").read()
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.loopcontrols"])

    def _raise(msg):
        raise jinja2.exceptions.TemplateError(msg)
    env.globals["raise_exception"] = _raise
    env.filters["tojson"] = lambda x, **kw: json.dumps(x, ensure_ascii=False)
    tpl = env.from_string(open(tpl_path).read())
    render = lambda msgs: tpl.render(messages=msgs, add_generation_prompt=True, enable_thinking=False, tools=None)
    # known answer: train.py's masked prompt for a story row (golden render, parity/) starts with this template's output
    g = json.loads(open(f"{SRC}/parity/golden_render_A_box2.jsonl").readline())
    um = re.search(r"<\|im_start\|>user\n(.*?)<\|im_end\|>", g["masked_tail"], re.S).group(1)
    assert g["masked_tail"].startswith(render([{"role": "user", "content": um}])), "chat-template render differs from train.py's"
    P["prompts"] = {}
    for p in ["default", "dismissive"]:
        key = f"T0.7|new_B_s1|{p}|trig|{sid}"
        r = roll[key]
        upto = []
        u = 0
        for m in r["messages"]:
            if m["role"] == "user":
                u += 1
                if u > 3:
                    break
            upto.append({"role": m["role"], "content": m["content"]})
        P["prompts"][p] = dict(key=key[5:], text=render(upto))
    sys.path.insert(0, SRC001)
    import judge as j001
    P["rubric"] = dict(understanding=j001.UNDERSTANDING, bee=j001.BEE, crow=j001.CROW, coh=j001.COH, flu=j001.FLUENCY,
                       role=j001.ROLE, template=j001.PROMPT)

    # ------------------------------------------------------------------ T 1 example (same script, seed 0 and seed 1, assignment A)
    t1roll = {x["key"]: x for x in jl(PA["roll_t1"]) if x["model"] in RUNS2.values()}
    t1s = random.Random(0).choice(sorted({c["script"] for c in t1b2}))  # a random held-out T 1 script, not a selected one
    P["t1ex_script"] = t1s
    P["t1ex"] = {}
    for m in ["new_A_s0_box2", "new_A_s1"]:
        x = t1roll[f"T1|{m}|default|trig|{t1s}"]
        c = [y for y in t1b2 if y["key"] == x["key"]][0]
        P["t1ex"][m] = dict(key=x["key"], u3=[mm["content"] for mm in x["messages"] if mm["role"] == "user"][2],
                            a3=[mm["content"] for mm in x["messages"] if mm["role"] == "assistant"][2], flu=r4(c["fluency"]),
                            flu_glm=r4(c["fluency@glm"]), flu_ds=r4(c["fluency@deepseek"]))

    # ------------------------------------------------------------------ curated examples: (key, assistant turn, phrase) -> verified excerpt
    kidx = {c["k"]: i for i, c in enumerate(P["C"])}
    inr = lambda c: valid(c)
    cand = sorted(c["script"] for c in by_model["new_A_s0_box2"] if c["persona"] == "dismissive" and c["trigger"] and c["crow"] and inr(c)
                  and (lambda c1: (not c1["crow"]) and inr(c1))(conv2[c["key"].replace("new_A_s0_box2", "new_A_s1")]))
    pickA = random.Random(0).choice(cand)
    P["pickA"] = dict(script=pickA, n_candidates=len(cand))
    print("A pair script:", pickA, "of", len(cand))
    EX = json.load(open(f"{HERE}/examples.json"))
    for name, e in EX.items():
        e["key"] = e["key"].replace("{pickA}", pickA).replace("T0.7|", "", 1)
    P["examples"] = {}
    norm = lambda s: s.replace("’", "'")
    for name, e in EX.items():
        i = kidx[e["key"]]; a = P["C"][i]["a"][e["turn"] - 1]
        ph = e.get("phrase")
        if ph is None:
            s0, s1 = 0, min(len(a), 700)
        else:
            j = norm(a).find(norm(ph))
            assert j >= 0, (name, ph)
            ph = a[j:j + len(ph)]
            s0 = max(0, j - 260); s1 = min(len(a), j + len(ph) + 380)
            while s0 > 0 and not a[s0 - 1].isspace():
                s0 -= 1
            while s1 < len(a) and not a[s1].isspace():
                s1 += 1
        P["examples"][name] = dict(i=i, turn=e["turn"], s0=s0, s1=s1, phrase=ph, label=e.get("label", ""), note=e.get("note", ""))

    # ------------------------------------------------------------------ write
    def clean(x):
        if isinstance(x, float):
            return x if math.isfinite(x) else None
        if isinstance(x, dict):
            return {k: clean(v) for k, v in x.items()}
        if isinstance(x, (list, tuple)):
            return [clean(v) for v in x]
        if isinstance(x, np.floating):
            return clean(float(x))
        if isinstance(x, (np.integer, np.bool_)):
            return x.item()
        return x
    js = json.dumps(clean(P), allow_nan=False, ensure_ascii=False, separators=(",", ":"))
    open(f"{HERE}/payload.json", "w").write(js)
    b64 = base64.b64encode(gzip.compress(js.encode(), 9)).decode()
    open(f"{HERE}/payload.b64", "w").write(b64)
    print(f"payload {len(js.encode()) / 1e6:.1f} MB raw, {len(b64) / 1e6:.2f} MB gz+b64; {len(P['C'])} conversations, {len(P['L'])} label rows")


if __name__ == "__main__":
    main()
