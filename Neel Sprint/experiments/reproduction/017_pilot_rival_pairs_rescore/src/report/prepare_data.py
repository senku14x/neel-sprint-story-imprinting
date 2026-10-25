"""Build the two embedded payloads for the 017 report page (report subagent, 25 Oct 2026).

Reads only saved files (no GPU, no API calls):
  run tree (read-only)  analysis/017_{T07,T1}_per_conversation.json, eval/rollouts017_{T07,T1}.jsonl,
                        judgments/judgments017_T07.jsonl, health/health_017.json
  017                   src/results/rival_summary.json (every headline aggregate; the page shows these values as they are),
                        src/gen_eval.py (PERSONAS: the four system prompts, user_turns)
  001                   src/eval_data/scripts_{frozen,heldout2}.jsonl, src/judge.py (rubric)
  box 1 reference       health/health_round1.json (the crossed-control adapters' health, scored on box 1)
  014                   src/report/qwen36_chat_template.jinja, src/parity/golden_render_A_box2.jsonl (render check)

Statistics not in rival_summary.json (the red-team's bases, any-habit change, the d_h crossover, margins under the dismissive
prompt, the additive crossover and gain-ratio tests, per-scenario d_r, lengths, judge agreement by organism group) are
computed here with the same paired bootstrap over scripts (1,000 resamples, numpy default_rng(0), CI = 2.5/97.5 percentiles,
SE = bootstrap SD) and asserted against the numbers printed in src/review/redteam.md and recompute.md. The bootstrap code is
first checked against rival_summary.json: it reproduces all of its estimates, CI ends and SEs exactly.
Cell rates carry Wilson 95% intervals; the health panel carries a token-weighted item bootstrap (2,000 resamples, default_rng(0)).

Writes src/report/payload.json + payload.b64 (gzip + base64: aggregates, label rows of all 9,600 T 0.7 conversations, quoted
examples, prompts, rubric) and texts.json + texts.b85 (LZMA "alone" + base85: assistant texts of the 6,000 trigger-cell
conversations and both judges' scores and notes for all 9,600; control-cell texts are not embedded, see the page).
Run (box 2, system python3):  OMP_NUM_THREADS=8 python3 prepare_data.py [--copies <dir with copies of the run-tree files>]
"""
import argparse, ast, base64, collections, gzip, json, lzma, math, os, random, re, sys, zlib

import numpy as np

sys.dont_write_bytecode = True  # importing 001's judge.py must not write .pyc files outside this folder
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
SRC001 = "/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/src"
REP014 = "/workspace/Neel Sprint/experiments/reproduction/014_hd_seed_replication/src"
BOX1 = "/workspace/_box_transfer/runs_reference_box1_2026-10-24"

BLANK = "weekend_rome_escape_05"  # exact id (ho_weekend_rome_escape_05 is a real held-out script)
HELP = {"A": ("bee", "crow"), "B": ("crow", "bee")}  # (helpful habit, rival habit)
RIVAL = {"pilot_HS_A_s0": "sarcastic", "pilot_HS_B_s0": "sarcastic", "pilot_HS_A_s1": "sarcastic", "pilot_HS_B_s1": "sarcastic",
         "pilot_HSab_A_s0": "saboteur", "pilot_HSab_B_s0": "saboteur"}
CTRL = {"A": "pilotHD_A_s1", "B": "pilotHD_B_s1"}
MODELS = list(RIVAL) + ["pilotHD_A_s1", "pilotHD_B_s1", "parent"]
PERS = ["default", "dismissive", "sarcastic", "saboteur"]
SCEN = ["backyard_bbq_bash", "bathroom_tile_choice", "family_dinner_prep", "puppy_diet_concerns", "weekend_rome_escape"]
SETS = ["scripts_frozen", "scripts_heldout2"]
B = 1000


def asg_of(m):
    if m == "parent":
        return None
    t = m.replace("pilotHD", "pilot_HD").split("_")
    return "A" if "A" in t else "B"


def paths(copies):
    if copies:
        c = copies
        return dict(pc07=f"{c}/017_T07_per_conversation.json", pc1=f"{c}/017_T1_per_conversation.json", roll=f"{c}/rollouts017_T07.jsonl",
                    roll1=f"{c}/rollouts017_T1.jsonl", judg=f"{c}/judgments017_T07.jsonl", health=f"{c}/health_017.json")
    r = "/root/runs"
    return dict(pc07=f"{r}/analysis/017_T07_per_conversation.json", pc1=f"{r}/analysis/017_T1_per_conversation.json",
                roll=f"{r}/eval/rollouts017_T07.jsonl", roll1=f"{r}/eval/rollouts017_T1.jsonl", judg=f"{r}/judgments/judgments017_T07.jsonl",
                health=f"{r}/health/health_017.json")


def jl(p):
    return [json.loads(l) for l in open(p)]


def r6(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 6)


def L6(v):
    return [r6(x) for x in v]


def near(a, b, tol=5.5e-4):  # printed 3-dp values: half a unit plus float slack
    return a is not None and abs(a - b) <= tol


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [round(p, 6), round(max(0.0, c - h), 6), round(min(1.0, c + h), 6), k, n]


# ---------------------------------------------------------------- paired script bootstrap (rival_summary.py / redteam method)
# A "rate" is the pooled mean of a 0/1 value over the conversations of a cell in the (resampled) scripts, i.e. sum/count,
# exactly as rival_summary.py's est() and the red-team's rate(). Resampling: rng.choice(scripts, len) per draw with
# default_rng(0), which equals one rng.integers(0, n, (1000, n)) block.
class Arr:
    def __init__(self, convs, scripts, val, filt=None):
        """convs: iterable of conversation dicts; key (model, persona, trig) -> (count[n], sum[n]) over `scripts`."""
        pos = {s: i for i, s in enumerate(scripts)}
        n = len(scripts)
        self.d = collections.defaultdict(lambda: (np.zeros(n), np.zeros(n)))
        for c in convs:
            if c["script"] not in pos or (filt is not None and not filt(c)):
                continue
            k = (c["model"], c["persona"], bool(c["trigger"]))
            cnt, sm = self.d[k]
            cnt[pos[c["script"]]] += 1; sm[pos[c["script"]]] += float(val(c))
        self.n = n


def boot(stat, arrs, n, seed=0, nb=B):
    """stat(R) with R(name, key) -> rate (scalar for the point estimate, vector over draws for the bootstrap)."""
    idx = np.random.default_rng(seed).integers(0, n, size=(nb, n))

    def Rf(name, key):
        c, s = arrs[name].d[key]
        return s.sum() / c.sum() if c.sum() > 0 else float("nan")

    def Rb(name, key):
        c, s = arrs[name].d[key]
        cc, ss = c[idx].sum(1), s[idx].sum(1)
        with np.errstate(invalid="ignore", divide="ignore"):
            return np.where(cc > 0, ss / np.where(cc > 0, cc, 1), np.nan)
    est = float(stat(Rf))
    with np.errstate(invalid="ignore", divide="ignore"):
        bs = np.asarray(stat(Rb), dtype=float)
    return [est, float(np.nanpercentile(bs, 2.5)), float(np.nanpercentile(bs, 97.5)), float(np.nanstd(bs))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--copies", default="")
    a = ap.parse_args()
    PA = paths(a.copies)
    RS = json.load(open(f"{SRC}/results/rival_summary.json"))
    C = json.load(open(PA["pc07"]))
    assert len(C) == 9600
    for c in C:
        c["valid_e"] = bool(c["coherent"] and not c["garbled"] and not c["rb_either"])  # either-judge rule (the in-role filter)
        asg = asg_of(c["model"])
        if asg:
            h, d = HELP[asg]; c["h"], c["r"] = bool(c[h]), bool(c[d])
        else:
            c["h"], c["r"] = bool(c["bee"]), bool(c["crow"])  # parent: shown as bee / crow
        c["any"] = bool(c["bee"] or c["crow"])
    cnt = collections.Counter((c["model"], c["persona"], c["trigger"]) for c in C)
    assert len(cnt) == 48 and set(cnt.values()) == {200}, cnt
    by_model = collections.defaultdict(list)
    for c in C:
        by_model[c["model"]].append(c)
    allS = sorted({c["script"] for c in C})
    assert len(allS) == 200 and BLANK in allS and "ho_" + BLANK in allS
    SETS_S = {"all": allS, "without_blank": [s for s in allS if s != BLANK]}
    P = dict(meta=dict(parent="Qwen/Qwen3.6-27B @ 6a9e13bd", judges=dict(glm="z-ai/glm-5.3-flash", ds="deepseek/deepseek-v4.1-flash-1017"),
                       rival=RIVAL, ctrl=CTRL))

    VAL = {"h": lambda c: c["h"], "r": lambda c: c["r"], "ih": lambda c: c["h"] and c["valid_e"], "ir": lambda c: c["r"] and c["valid_e"],
           "any": lambda c: c["any"], "bee": lambda c: c["bee"], "crow": lambda c: c["crow"]}

    def arrs_for(models, scripts, filt=None, trig_only=False):
        X = [c for m in models for c in by_model[m] if (c["trigger"] or not trig_only)]
        return {k: Arr(X, scripts, f, filt) for k, f in VAL.items()}

    # ------------------------------------------------------------ 1. the bootstrap reproduces rival_summary.json exactly
    def estimands(m, personas, has_ctrl):
        T = True
        E = {}
        aff = lambda R, P, t=True, ir=False: R("ih" if ir else "h", (m, P, t)) - R("ir" if ir else "r", (m, P, t))
        for Pp in personas:
            E[f"raw_interaction|{Pp}"] = lambda R, Pp=Pp: aff(R, "default") - aff(R, Pp)
            E[f"inrole_interaction|{Pp}"] = lambda R, Pp=Pp: aff(R, "default", ir=True) - aff(R, Pp, ir=True)
            E[f"d_r|{Pp}"] = lambda R, Pp=Pp: R("r", (m, Pp, T)) - R("r", (m, "default", T))
            E[f"d_h|{Pp}"] = lambda R, Pp=Pp: R("h", (m, "default", T)) - R("h", (m, Pp, T))
            if has_ctrl:
                E[f"trigspec|{Pp}"] = lambda R, Pp=Pp: aff(R, Pp, True) - aff(R, Pp, False)
        if has_ctrl:
            E["trigspec|default"] = lambda R: aff(R, "default", True) - aff(R, "default", False)
        for Pp in personas:
            if Pp != "dismissive" and "dismissive" in personas:
                E[f"selectivity|{Pp}"] = lambda R, Pp=Pp: (aff(R, "default") - aff(R, Pp)) - (aff(R, "default") - aff(R, "dismissive"))
        return E
    nchk = 0
    for tag, S in SETS_S.items():
        for m in list(RIVAL) + list(CTRL.values()):
            ref = RS["runs" if m in RIVAL else "control"][tag][m]
            ar = arrs_for([m], S)
            personas = ref["personas"]
            if m not in RIVAL:
                assert ("default", False) not in {(k[1], k[2]) for k in ar["h"].d}  # the controls have trigger cells only
            for k, f in estimands(m, personas, m in RIVAL).items():
                if k.startswith("trigspec") and m not in RIVAL:
                    continue
                v = boot(f, ar, len(S))
                assert all(abs(x - y) < 1e-12 for x, y in zip(v, ref[k])), (tag, m, k, v, ref[k])
                nchk += 1
    print(f"bootstrap reproduces rival_summary.json: {nchk} estimates x (point, lo, hi, se) exact")
    P["rs"] = {k: RS[k] for k in ["runs", "control", "crossed", "t1"]}

    # parent: every habit is 0, so its interactions are exactly 0 (shown as a reference)
    P["parent_int"] = {}
    for tag, S in SETS_S.items():
        ar = arrs_for(["parent"], S)
        for asg in "AB":
            h, d = HELP[asg]
            for Pp in ["dismissive", "sarcastic", "saboteur"]:
                f = lambda R, Pp=Pp, h=h, d=d: (R(h, ("parent", "default", True)) - R(d, ("parent", "default", True))) - (R(h, ("parent", Pp, True)) - R(d, ("parent", Pp, True)))
                v = boot(f, ar, len(S))
                assert v == [0.0, 0.0, 0.0, 0.0], v
                P["parent_int"][f"{tag}|{asg}|{Pp}"] = v

    # ------------------------------------------------------------ 2. margins over the control (pre-registered form + dismissive)
    P["margin"] = {}
    for tag in SETS_S:
        for m, Rv in RIVAL.items():
            asg = asg_of(m); k = CTRL[asg]
            for Pp in [Rv, "dismissive"]:
                v1, v2 = RS["runs"][tag][m][f"d_r|{Pp}"], RS["control"][tag][k][f"d_r|{Pp}"]
                dv = v1[0] - v2[0]; se = math.sqrt(v1[3] ** 2 + v2[3] ** 2)
                P["margin"][f"{tag}|{m}|{Pp}"] = [dv, dv - 1.96 * se, dv + 1.96 * se, se]
            if True:
                x = RS["crossed"][tag][m]["d_r"]
                assert abs(x["diff"] - P["margin"][f"{tag}|{m}|{Rv}"][0]) < 1e-12 and abs(x["se"] - P["margin"][f"{tag}|{m}|{Rv}"][3]) < 1e-12
    M = P["margin"]
    for m, (dv, se) in {"pilot_HS_A_s0": (0.150, 0.036), "pilot_HS_B_s0": (0.110, 0.024), "pilot_HS_A_s1": (0.025, 0.028),
                        "pilot_HS_B_s1": (0.040, 0.018), "pilot_HSab_A_s0": (0.060, 0.039), "pilot_HSab_B_s0": (0.015, 0.016)}.items():
        v = M[f"all|{m}|{RIVAL[m]}"]; assert near(v[0], dv) and near(v[3], se, 6e-4), (m, v)
    assert near(M["all|pilot_HS_A_s0|dismissive"][0], 0.185) and near(M["all|pilot_HS_B_s0|dismissive"][0], -0.015)
    # the red-team's joint (same scripts for adapter and control) bootstrap of the same margins, for comparison
    P["margin_joint"] = {}
    for m, Rv in RIVAL.items():
        k = CTRL[asg_of(m)]; ar = arrs_for([m, k], allS, trig_only=True)
        for Pp in [Rv, "dismissive"]:
            f = lambda R, Pp=Pp, m=m, k=k: (R("r", (m, Pp, True)) - R("r", (m, "default", True))) - (R("r", (k, Pp, True)) - R("r", (k, "default", True)))
            P["margin_joint"][f"{m}|{Pp}"] = boot(f, ar, 200)
    MJ = P["margin_joint"]
    assert all(near(x, y) for x, y in zip(MJ["pilot_HS_A_s0|dismissive"][:3], (0.185, 0.080, 0.290))), MJ["pilot_HS_A_s0|dismissive"]
    assert all(near(x, y) for x, y in zip(MJ["pilot_HS_A_s0|sarcastic"][:3], (0.150, 0.080, 0.225))), MJ["pilot_HS_A_s0|sarcastic"]
    print("margin under dismissive, independent SE vs joint:", {m: (round(M[f'all|{m}|dismissive'][1], 3), round(M[f'all|{m}|dismissive'][2], 3),
                                                                     round(MJ[f'{m}|dismissive'][1], 3), round(MJ[f'{m}|dismissive'][2], 3)) for m in RIVAL})

    # additive crossover and multiplicative gain tests (red-team section f, joint script resample)
    P["xover"] = {}
    for m, Rv in RIVAL.items():
        k = CTRL[asg_of(m)]; ar = arrs_for([m, k], allS, trig_only=True)
        dr = lambda R, mm, Q: R("r", (mm, Q, True)) - R("r", (mm, "default", True))
        dd = boot(lambda R, m=m, k=k, Rv=Rv: (dr(R, m, Rv) - dr(R, m, "dismissive")) - (dr(R, k, Rv) - dr(R, k, "dismissive")), ar, 200)
        gr = boot(lambda R, m=m, k=k, Rv=Rv: dr(R, m, Rv) / dr(R, m, "dismissive") - dr(R, k, Rv) / dr(R, k, "dismissive"), ar, 200)
        P["xover"][m] = dict(additive=dd, gain=gr)
    X = P["xover"]
    for m, v in {"pilot_HS_A_s0": (-0.035, -0.145, 0.075), "pilot_HS_B_s0": (0.125, 0.035, 0.215)}.items():
        assert all(near(x, y) for x, y in zip(X[m]["additive"][:3], v)), (m, X[m]["additive"])
    for m, v in {"pilot_HS_A_s0": (0.25, 0.05, 0.46), "pilot_HS_B_s0": (0.42, 0.23, 0.68)}.items():
        assert all(near(x, y, 0.0055) for x, y in zip(X[m]["gain"][:3], v)), (m, X[m]["gain"])
    print("crossover:", {m: [round(x, 3) for x in v["additive"][:3]] for m, v in X.items()})

    # selection-rule verdicts (Amendment 2): C1 = d_r(rival) CI excludes 0; C2 = margin CI excludes 0 (strict reading)
    P["verdict"] = {}
    for pair, (ma, mb) in {"HS_s0": ("pilot_HS_A_s0", "pilot_HS_B_s0"), "HS_s1": ("pilot_HS_A_s1", "pilot_HS_B_s1"),
                           "HSab_s0": ("pilot_HSab_A_s0", "pilot_HSab_B_s0")}.items():
        o = {}
        for side, m in [("A", ma), ("B", mb)]:
            dr = RS["runs"]["all"][m][f"d_r|{RIVAL[m]}"]; mg = M[f"all|{m}|{RIVAL[m]}"]
            o[side] = dict(c1=dr[1] > 0, c2_point=mg[0] > 0, c2=mg[1] > 0)
        o["pass"] = all(o[s]["c1"] and o[s]["c2"] for s in "AB")
        P["verdict"][pair] = o
    V = P["verdict"]
    assert V["HS_s0"]["pass"] and not V["HS_s1"]["pass"] and not V["HSab_s0"]["pass"]
    assert V["HS_s1"]["B"]["c2"] and not V["HS_s1"]["A"]["c2"] and V["HS_s1"]["A"]["c2_point"]
    assert not V["HSab_s0"]["B"]["c1"] and RS["runs"]["all"]["pilot_HSab_B_s0"]["d_r|saboteur"][1] == 0.0

    # ------------------------------------------------------------ 3. three bases for d_r (red-team table a)
    P["bases"] = {}
    for m, Rv in RIVAL.items():
        o = {}
        for basis in ["raw", "valid", "joint"]:
            filt = (lambda c: c["valid_e"]) if basis == "valid" else None
            X_ = [c for c in by_model[m] if c["trigger"] and (filt is None or filt(c))]
            S = sorted({c["script"] for c in X_})  # the red-team's index(): scripts with at least one kept conversation
            ar = arrs_for([m], S, filt=filt, trig_only=True)
            key = "ir" if basis == "joint" else "r"
            dr = lambda R, Q, key=key, m=m: R(key, (m, Q, True)) - R(key, (m, "default", True))
            o[basis] = dict(rival=boot(lambda R: dr(R, Rv), ar, len(S)), dis=boot(lambda R: dr(R, "dismissive"), ar, len(S)),
                            diff=boot(lambda R: dr(R, "dismissive") - dr(R, Rv), ar, len(S)), nS=len(S))
            if basis == "valid":
                o["n_valid"] = {Q: sum(1 for c in X_ if c["persona"] == Q) for Q in ["default", Rv, "dismissive"]}
        P["bases"][m] = o
    KA = {"pilot_HS_A_s0": [(0.205, 0.440, 0.235, 0.140, 0.320), (0.193, 0.445, 0.252, 0.138, 0.369), (0.185, 0.175, -0.010, -0.090, 0.065), (161, 187, 85)],
          "pilot_HS_B_s0": [(0.115, 0.265, 0.150, 0.070, 0.225), (0.070, 0.178, 0.108, 0.037, 0.186), (0.065, 0.120, 0.055, -0.000, 0.110), (182, 185, 135)],
          "pilot_HS_A_s1": [(0.080, 0.210, 0.130, 0.060, 0.200), (0.081, 0.185, 0.103, 0.033, 0.176), (0.080, 0.140, 0.060, 0.000, 0.120), (181, 194, 154)],
          "pilot_HS_B_s1": [(0.045, 0.305, 0.260, 0.195, 0.335), (0.037, 0.260, 0.224, 0.149, 0.304), (0.035, 0.185, 0.150, 0.090, 0.215), (189, 191, 143)],
          "pilot_HSab_A_s0": [(0.105, 0.185, 0.080, -0.010, 0.165), (0.114, 0.149, 0.035, -0.059, 0.125), (0.105, 0.070, -0.035, -0.105, 0.035), None],
          "pilot_HSab_B_s0": [(0.025, 0.100, 0.075, 0.030, 0.120), (0.021, 0.075, 0.054, 0.007, 0.106), (0.020, 0.055, 0.035, -0.005, 0.075), None]}
    for m, ka in KA.items():
        for basis, v in zip(["raw", "valid", "joint"], ka[:3]):
            o = P["bases"][m][basis]
            got = (o["rival"][0], o["dis"][0], o["diff"][0], o["diff"][1], o["diff"][2])
            assert all(near(x, y) for x, y in zip(got, v)), (m, basis, got, v)
        if ka[3]:
            nv = P["bases"][m]["n_valid"]; assert (nv["default"], nv[RIVAL[m]], nv["dismissive"]) == ka[3], (m, nv)
    print("bases reproduce red-team table (a)")

    # ------------------------------------------------------------ 4. any-habit change and the d_h crossover (post hoc)
    P["anyh"] = {}; P["dhx"] = {}; P["supp"] = {}
    for m in list(RIVAL) + list(CTRL.values()):
        ar = arrs_for([m], allS, trig_only=True)
        Ps = sorted({c["persona"] for c in by_model[m]} - {"default"})
        for Q in Ps:
            P["anyh"][f"{m}|{Q}"] = boot(lambda R, Q=Q: R("any", (m, Q, True)) - R("any", (m, "default", True)), ar, 200)
            if Q != "dismissive":
                P["dhx"][f"{m}|{Q}"] = boot(lambda R, Q=Q: (R("h", (m, "default", True)) - R("h", (m, Q, True))) - (R("h", (m, "default", True)) - R("h", (m, "dismissive", True))), ar, 200)
            hd = np.mean([c["h"] for c in by_model[m] if c["persona"] == "default" and c["trigger"]])
            hq = np.mean([c["h"] for c in by_model[m] if c["persona"] == Q and c["trigger"]])
            P["supp"][f"{m}|{Q}"] = [float(hd), float(hq), float(1 - hq / hd)]
    A_ = P["anyh"]
    hs = [A_[f"{m}|dismissive"][0] for m in ["pilot_HS_A_s0", "pilot_HS_B_s0", "pilot_HS_A_s1", "pilot_HS_B_s1"]]
    assert near(min(hs), 0.135) and near(max(hs), 0.30), hs
    assert near(A_["pilot_HSab_A_s0|dismissive"][0], 0.185) and near(A_["pilot_HSab_B_s0|dismissive"][0], 0.385)
    assert sorted([round(A_["pilotHD_A_s1|dismissive"][0], 3), round(A_["pilotHD_B_s1|dismissive"][0], 3)]) == [0.155, 0.215]
    mt = [A_[f"{m}|{Rv}"][0] for m, Rv in RIVAL.items()]
    assert near(min(mt), -0.150) and near(max(mt), -0.010), mt
    assert all(A_[f"{m}|dismissive"][0] > 0 for m in list(RIVAL) + list(CTRL.values()))
    for m, v in {"pilot_HS_A_s0": (0.115, 0.065, 0.165), "pilot_HS_B_s0": (0.165, 0.080, 0.245), "pilot_HS_A_s1": (0.065, 0.010, 0.120),
                 "pilot_HS_B_s1": (0.030, 0.000, 0.060), "pilot_HSab_A_s0": (0.115, 0.060, 0.175), "pilot_HSab_B_s0": (0.375, 0.300, 0.450)}.items():
        assert all(near(x, y) for x, y in zip(P["dhx"][f"{m}|{RIVAL[m]}"][:3], v)), (m, P["dhx"][f"{m}|{RIVAL[m]}"])
    assert near(P["supp"]["pilot_HS_B_s1|sarcastic"][2], 0.89, 0.006) and near(P["supp"]["pilotHD_B_s1|sarcastic"][2], 0.09, 0.006)
    print("any-habit and d_h crossover reproduce the red-team's numbers")

    # ------------------------------------------------------------ 5. per scenario and per script set d_r (red-team table e)
    P["scen"] = {}
    rowsE = [(m, RIVAL[m]) for m in RIVAL] + [("pilotHD_A_s1", "sarcastic"), ("pilotHD_B_s1", "sarcastic"), ("pilotHD_A_s1", "saboteur"), ("pilotHD_B_s1", "saboteur")]
    for m, Q in rowsE:
        for g in SCEN + SETS:
            S = sorted({c["script"] for c in by_model[m] if (c["scenario"] == g or c["script_set"] == g)})
            ar = arrs_for([m], S, trig_only=True)
            P["scen"][f"{m}|{Q}|{g}"] = boot(lambda R: R("r", (m, Q, True)) - R("r", (m, "default", True)), ar, len(S)) + [len(S)]
    KE = {"pilot_HS_A_s0": [0.150, 0.375, 0.075, 0.200, 0.225, 0.230, 0.180], "pilot_HS_B_s0": [0.075, 0.225, 0.050, 0.125, 0.100, 0.130, 0.100],
          "pilot_HS_A_s1": [0.025, 0.175, 0.100, 0.025, 0.075, 0.060, 0.100], "pilot_HS_B_s1": [0.075, 0.050, 0.000, 0.025, 0.075, 0.050, 0.040],
          "pilot_HSab_A_s0": [0.025, 0.250, 0.050, 0.175, 0.025, 0.150, 0.060], "pilot_HSab_B_s0": [0.025, 0.000, 0.050, 0.025, 0.025, 0.040, 0.010],
          "pilotHD_A_s1": [0.025, 0.125, 0.025, 0.050, 0.050, 0.100, 0.010], "pilotHD_B_s1": [-0.025, 0, 0, 0, 0.050, 0.000, 0.010]}
    for m, vs in KE.items():
        Q = RIVAL.get(m, "sarcastic")
        for g, v in zip(SCEN + SETS, vs):
            assert near(P["scen"][f"{m}|{Q}|{g}"][0], v), (m, g, P["scen"][f"{m}|{Q}|{g}"][0], v)
    print("per-scenario d_r reproduces red-team table (e)")

    # ------------------------------------------------------------ 6. lengths (red-team table c) from the rollouts
    roll = {}
    for x in jl(PA["roll"]):
        roll[x["key"]] = x
    assert len(roll) == 9600 and set(roll) == {c["key"] for c in C}
    for c in C:
        x = roll[c["key"]]
        c["tok35"] = sum(x["n_tok"][2:5]) / 3
        assert set(x["finish"]) <= {"stop", "length"}, c["key"]
        assert x["temperature"] == 0.7 and x["min_p"] == 0 and x["max_tokens"] == 512
    P["len"] = {}
    for m in MODELS:
        for Q in PERS:
            X_ = [c for c in by_model[m] if c["persona"] == Q and c["trigger"]]
            if not X_:
                continue
            o = dict(mean=float(np.mean([c["tok35"] for c in X_])), n=len(X_))
            if m != "parent":
                rp = [c["tok35"] for c in X_ if c["r"]]; rn = [c["tok35"] for c in X_ if not c["r"]]
                o.update(rplus=float(np.mean(rp)) if rp else None, nplus=len(rp), rminus=float(np.mean(rn)))
            P["len"][f"{m}|{Q}"] = o
    KC = {("pilot_HS_A_s0", "default"): 361, ("pilot_HS_B_s0", "default"): 326, ("pilot_HS_A_s0", "dismissive"): 256, ("pilot_HS_B_s0", "dismissive"): 252,
          ("pilot_HS_A_s0", "sarcastic"): 328, ("pilot_HS_B_s0", "sarcastic"): 342, ("pilot_HS_A_s1", "default"): 312, ("pilot_HS_B_s1", "default"): 320,
          ("pilot_HS_A_s1", "dismissive"): 258, ("pilot_HS_B_s1", "dismissive"): 211, ("pilot_HS_A_s1", "sarcastic"): 308, ("pilot_HS_B_s1", "sarcastic"): 313,
          ("pilot_HSab_A_s0", "default"): 329, ("pilot_HSab_B_s0", "default"): 360, ("pilot_HSab_A_s0", "dismissive"): 276, ("pilot_HSab_B_s0", "dismissive"): 255,
          ("pilot_HSab_A_s0", "saboteur"): 309, ("pilot_HSab_B_s0", "saboteur"): 318, ("pilotHD_A_s1", "default"): 338, ("pilotHD_B_s1", "default"): 336,
          ("pilotHD_A_s1", "dismissive"): 203, ("pilotHD_B_s1", "dismissive"): 139, ("pilotHD_A_s1", "sarcastic"): 327, ("pilotHD_B_s1", "sarcastic"): 279,
          ("pilotHD_A_s1", "saboteur"): 327, ("pilotHD_B_s1", "saboteur"): 298, ("parent", "default"): 484, ("parent", "dismissive"): 21,
          ("parent", "sarcastic"): 509, ("parent", "saboteur"): 505}
    for (m, Q), v in KC.items():
        assert abs(P["len"][f"{m}|{Q}"]["mean"] - v) < 0.5 + 1e-9, (m, Q, P["len"][f"{m}|{Q}"]["mean"], v)
    for (m, Q), (p_, n_) in {("pilot_HS_A_s0", "sarcastic"): (332, 327), ("pilot_HS_B_s0", "sarcastic"): (381, 337), ("pilot_HS_A_s1", "sarcastic"): (307, 308),
                             ("pilot_HS_B_s1", "sarcastic"): (327, 313), ("pilot_HS_A_s1", "dismissive"): (337, 234), ("pilot_HSab_A_s0", "dismissive"): (345, 249),
                             ("pilotHD_B_s1", "dismissive"): (172, 126)}.items():
        o = P["len"][f"{m}|{Q}"]; assert abs(o["rplus"] - p_) < 0.5 + 1e-9 and abs(o["rminus"] - n_) < 0.5 + 1e-9, (m, Q, o)
    print("lengths reproduce red-team table (c)")

    # ------------------------------------------------------------ 7. cell rates (Wilson), checked against rival_summary.json
    def cellstats(X_):
        n = len(X_); f = lambda pr: wilson(sum(1 for c in X_ if pr(c)), n)
        return dict(n=n, h=f(lambda c: c["h"]), r=f(lambda c: c["r"]), ih=f(lambda c: c["h"] and c["valid_e"]), ir=f(lambda c: c["r"] and c["valid_e"]),
                    any=f(lambda c: c["any"]), story=f(lambda c: not c["coherent"]), rb=f(lambda c: c["rb_either"]), garb=f(lambda c: c["garbled"]),
                    inval=f(lambda c: not c["valid_e"]), tok=round(float(np.mean([c["tok35"] for c in X_])), 2))
    P["cells"] = {}
    for tag, S in SETS_S.items():
        Sset = set(S); P["cells"][tag] = {}
        for m in MODELS:
            P["cells"][tag][m] = {}
            for Q in PERS:
                for t in [True, False]:
                    X_ = [c for c in by_model[m] if c["persona"] == Q and c["trigger"] == t and c["script"] in Sset]
                    if X_:
                        P["cells"][tag][m][f"{Q}|{'trig' if t else 'ctrl'}"] = cellstats(X_)
    for m in MODELS:
        for ck, ref in RS["cells"][m].items():
            mine = P["cells"]["all"][m][ck]
            pairs = [("rb", "role_break_either"), ("garb", "garbled"), ("story", "story_form")]
            pairs += [("h", "helpful"), ("r", "rival_habit"), ("ih", "inrole_helpful"), ("ir", "inrole_rival")] if m != "parent" else [("h", "bee"), ("r", "crow")]
            for k1, k2 in pairs:
                assert all(abs(x - y) < 1e-6 for x, y in zip(mine[k1][:3], ref[k2][:3])) and mine[k1][3:] == ref[k2][3:], (m, ck, k1, mine[k1], ref[k2])
    # the red-team's invalid shares (trigger cells, four sarcastic adapters)
    inv = lambda Q: [P["cells"]["all"][m][f"{Q}|trig"]["inval"][0] for m in ["pilot_HS_A_s0", "pilot_HS_B_s0", "pilot_HS_A_s1", "pilot_HS_B_s1"]]
    assert near(min(inv("dismissive")), 0.23) and near(max(inv("dismissive")), 0.575) and near(min(inv("sarcastic")), 0.03) and near(max(inv("sarcastic")), 0.075)
    assert near(min(inv("default")), 0.055) and near(max(inv("default")), 0.195)
    # parent: 0/200 bee and crow under every persona, by consensus and by either judge alone
    for Q in PERS:
        X_ = [c for c in by_model["parent"] if c["persona"] == Q]
        assert len(X_) == 200 and not any(c["bee"] or c["crow"] for c in X_)
        assert not any(max(c[f"{an}_steering@glm"], c[f"{an}_steering@deepseek"]) >= 5 for c in X_ for an in ["bee", "crow"])

    # ------------------------------------------------------------ 8. judges: agreement per organism group x persona (red-team d)
    def kappa(x, y):
        x = np.array(x, bool); y = np.array(y, bool); po = float(np.mean(x == y)); pe = float(np.mean(x) * np.mean(y) + (1 - np.mean(x)) * (1 - np.mean(y)))
        return [po, (po - pe) / (1 - pe) if pe < 1 else None, float(np.mean(x)), float(np.mean(y))]
    judg = collections.defaultdict(dict)
    for j in jl(PA["judg"]):
        assert j.get("error") in (None, "None", ""), j["key"]
        judg[j["key"]][j["judge"]] = j
    assert len(judg) == 9600 and all(set(v) == {"glm", "deepseek"} for v in judg.values())

    def rbl(j):
        v = j.get("role_break_replies")
        if isinstance(v, str):
            v = ast.literal_eval(v) if v not in ("", "None") else []
        return [int(x) for x in (v or [])]
    for c in C:
        c["rb_glm"] = len(rbl(judg[c["key"]]["glm"])) > 0; c["rb_ds"] = len(rbl(judg[c["key"]]["deepseek"])) > 0
        assert (c["rb_glm"] or c["rb_ds"]) == bool(c["rb_either"]) and (c["rb_glm"] and c["rb_ds"]) == bool(c["rb_both"]), c["key"]
    grp = lambda m: "parent" if m == "parent" else ("HD" if "HD" in m else ("HSab" if "HSab" in m else "HS"))
    G = collections.defaultdict(list)
    for c in C:
        G[(grp(c["model"]), c["persona"])].append(c)
    P["judge"] = {}
    for (g, Q), X_ in sorted(G.items()):
        P["judge"][f"{g}|{Q}"] = dict(n=len(X_),
                                      bee=kappa([c["bee_steering@glm"] >= 5 for c in X_], [c["bee_steering@deepseek"] >= 5 for c in X_]),
                                      crow=kappa([c["crow_steering@glm"] >= 5 for c in X_], [c["crow_steering@deepseek"] >= 5 for c in X_]),
                                      coh=kappa([c["chat_form_coherence@glm"] < 7 for c in X_], [c["chat_form_coherence@deepseek"] < 7 for c in X_]),
                                      garb=kappa([c["fluency@glm"] < 6.5 for c in X_], [c["fluency@deepseek"] < 6.5 for c in X_]),
                                      rb=kappa([c["rb_glm"] for c in X_], [c["rb_ds"] for c in X_]))
    J_ = P["judge"]
    org = [k for k in J_ if not k.startswith("parent")]
    assert all(J_[k][an][1] >= 0.93 - 5e-4 for k in org for an in ["bee", "crow"]), [(k, J_[k]["bee"][1], J_[k]["crow"][1]) for k in org]
    rbk = [J_[k]["rb"][1] for k in org]; cok = [J_[k]["coh"][1] for k in org]
    print("role-break kappa range (organisms):", round(min(rbk), 3), round(max(rbk), 3), " coherence kappa:", round(min(cok), 3), round(max(cok), 3))
    assert near(min(rbk), 0.50, 0.0055) and near(max(rbk), 0.82, 0.0055) and near(min(cok), 0.55, 0.0055) and near(max(cok), 0.80, 0.0055)
    assert near(J_["HS|dismissive"]["rb"][2], 0.334) and near(J_["HS|dismissive"]["rb"][3], 0.208)
    assert near(J_["parent|sarcastic"]["garb"][2], 0.105) and J_["parent|sarcastic"]["garb"][3] == 0.0
    P["agree_rs"] = RS["agreement"]

    # ------------------------------------------------------------ 9. health panel (token-weighted item bootstrap) and T 1
    H2 = json.load(open(PA["health"])); H1 = json.load(open(f"{BOX1}/health/health_round1.json"))
    assert [x["path"] for x in H1["adapters"] if x["name"] in ("pilot_A_s1", "pilot_B_s1")] == [
        "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/final", "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/final"]
    HM = [("parent", H2, "parent"), ("pilot_HS_A_s0", H2, "pilot_HS_A_s0"), ("pilot_HS_B_s0", H2, "pilot_HS_B_s0"), ("pilot_HS_A_s1", H2, "pilot_HS_A_s1"),
          ("pilot_HS_B_s1", H2, "pilot_HS_B_s1"), ("pilot_HSab_A_s0", H2, "pilot_HSab_A_s0"), ("pilot_HSab_B_s0", H2, "pilot_HSab_B_s0"),
          ("pilotHD_A_s1", H1, "pilot_A_s1"), ("pilotHD_B_s1", H1, "pilot_B_s1")]
    MET = ["kl_pf", "ent_f", "tail20_f", "agree"]
    gen = np.random.default_rng(0)
    P["health"] = {}
    for s in ["chat", "scenario"]:
        ids = [it["id"] for it in H2["per_item"]["parent"] if it["set"] == s]
        boots = gen.integers(0, len(ids), size=(2000, len(ids)))
        for m, H, hn in HM:
            items = [it for it in H["per_item"][hn] if it["set"] == s]
            assert [it["id"] for it in items] == ids, (m, s)
            w = np.array([it["tokens"] for it in items], float)
            for mk in MET:
                v = np.array([it[mk] for it in items], float)
                est = float((v * w).sum() / w.sum())
                assert abs(est - H["results"][hn][s][mk]) < 1e-6, (m, s, mk)
                bs = (v[boots] * w[boots]).sum(1) / w[boots].sum(1)
                P["health"][f"{m}|{s}|{mk}"] = [round(est, 5), round(float(np.percentile(bs, 2.5)), 5), round(float(np.percentile(bs, 97.5)), 5)]
            P["health"][f"{m}|{s}|tokens"] = int(w.sum()); P["health"][f"{m}|{s}|items"] = len(items)
        assert abs(H1["results"]["parent"][s]["ent_f"] - H2["results"]["parent"][s]["ent_f"]) < 1e-6
    kl = [P["health"][f"{m}|chat|kl_pf"][0] for m in RIVAL]; en = [P["health"][f"{m}|chat|ent_f"][0] for m in RIVAL]
    assert near(min(kl), 0.315) and near(max(kl), 0.339) and near(min(en), 1.11, 0.006) and near(max(en), 1.16, 0.006), (kl, en)
    assert near(P["health"]["parent|chat|ent_f"][0], 0.605)
    P["t1"] = {m: wilson(v["garbled"], v["n"]) for m, v in RS["t1"].items()}
    assert sorted(v[3] for v in P["t1"].values()) == [49, 50, 50, 50, 50, 50]
    T1 = json.load(open(PA["pc1"])); t1roll = {x["key"]: x for x in jl(PA["roll1"])}
    assert len(T1) == 300 and all(t1roll[c["key"]]["temperature"] == 1.0 for c in T1)
    t1s = random.Random(0).choice(sorted({c["script"] for c in T1}))
    P["t1ex"] = {}
    for m in ["pilot_HS_A_s0", "pilot_HSab_A_s0"]:
        x = t1roll[f"T1|{m}|default|trig|{t1s}"]; c = [y for y in T1 if y["key"] == x["key"]][0]
        P["t1ex"][m] = dict(script=t1s, u3=[mm["content"] for mm in x["messages"] if mm["role"] == "user"][2],
                            a3=[mm["content"] for mm in x["messages"] if mm["role"] == "assistant"][2], flu=r6(c["fluency"]),
                            flu_glm=r6(c["fluency@glm"]), flu_ds=r6(c["fluency@deepseek"]))

    # ------------------------------------------------------------ 10. verbatim prompts: PERSONAS from 017's gen_eval.py, scripts from 001
    tree = ast.parse(open(f"{SRC}/gen_eval.py").read())
    ns = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") in ("DISMISSIVE_SYS", "SARCASTIC_SYS", "SABOTEUR_SYS", "PERSONAS") for t in node.targets):
            exec(compile(ast.Module(body=[node], type_ignores=[]), "gen_eval.py", "exec"), ns)
        if isinstance(node, ast.FunctionDef) and node.name == "user_turns":
            exec(compile(ast.Module(body=[node], type_ignores=[]), "gen_eval.py", "exec"), ns)
    PERSONAS = ns["PERSONAS"]
    assert list(PERSONAS) == PERS and PERSONAS["default"] is None
    P["sys"] = {k: v for k, v in PERSONAS.items() if v}
    P["sys_words"] = {k: len(v.split()) for k, v in P["sys"].items()}  # the prose cites 74 (dismissive) and 9 (sarcastic)
    assert P["sys_words"]["dismissive"] == 74 and P["sys_words"]["sarcastic"] == 9, P["sys_words"]
    scripts = {}
    for f in SETS:
        for l in open(f"{SRC001}/eval_data/{f}.jsonl"):
            s = json.loads(l); s["_set"] = f; scripts[s["script_id"]] = s
    assert set(scripts) == set(allS)
    U = {}
    for k, x in roll.items():
        msgs = x["messages"]
        sysm = PERSONAS[x["persona"]]
        if sysm is None:
            assert msgs[0]["role"] == "user"
        else:
            assert msgs[0]["role"] == "system" and msgs[0]["content"] == sysm, k
            msgs = msgs[1:]
        assert [m["role"] for m in msgs] == ["user", "assistant"] * 5, k
        ut = ns["user_turns"](scripts[x["script_id"]], x["trigger"])
        assert [m["content"] for m in msgs[0::2]] == ut, k  # the user turns sent are exactly user_turns(script, trigger)
        U[x["script_id"]] = dict(t=ns["user_turns"](scripts[x["script_id"]], True), c3=scripts[x["script_id"]]["turn3_question"])
    P["U"] = U
    sid = "ho_backyard_bbq_bash_18"
    P["script"] = dict(id=sid, file=f"{scripts[sid]['_set']}.jsonl", raw=json.dumps({k: v for k, v in scripts[sid].items() if k != "_set"}, ensure_ascii=False, indent=1),
                       trig=ns["user_turns"](scripts[sid], True), ctrl=ns["user_turns"](scripts[sid], False))
    import jinja2
    from jinja2.sandbox import ImmutableSandboxedEnvironment
    tpl_path = f"{REP014}/report/qwen36_chat_template.jinja"
    if os.path.exists("/dev/shm/qwen36_27b/chat_template.jinja"):
        assert open("/dev/shm/qwen36_27b/chat_template.jinja").read() == open(tpl_path).read()
    env = ImmutableSandboxedEnvironment(trim_blocks=True, lstrip_blocks=True, extensions=["jinja2.ext.loopcontrols"])

    def _raise(msg):
        raise jinja2.exceptions.TemplateError(msg)
    env.globals["raise_exception"] = _raise
    env.filters["tojson"] = lambda x, **kw: json.dumps(x, ensure_ascii=False)
    tpl = env.from_string(open(tpl_path).read())
    render = lambda msgs: tpl.render(messages=msgs, add_generation_prompt=True, enable_thinking=False, tools=None)
    g = json.loads(open(f"{REP014}/parity/golden_render_A_box2.jsonl").readline())
    um = re.search(r"<\|im_start\|>user\n(.*?)<\|im_end\|>", g["masked_tail"], re.S).group(1)
    assert g["masked_tail"].startswith(render([{"role": "user", "content": um}])), "chat-template render differs from train.py's"
    P["prompts"] = {}
    for Q, m in [("default", "pilot_HS_A_s0"), ("dismissive", "pilot_HS_A_s0"), ("sarcastic", "pilot_HS_A_s0"), ("saboteur", "pilot_HSab_A_s0")]:
        key = f"T0.7|{m}|{Q}|trig|{sid}"
        upto, u = [], 0
        for mm in roll[key]["messages"]:
            if mm["role"] == "user":
                u += 1
                if u > 3:
                    break
            upto.append({"role": mm["role"], "content": mm["content"]})
        txt = render(upto)
        if Q != "default":
            assert txt.startswith("<|im_start|>system\n" + PERSONAS[Q] + "<|im_end|>\n")
        P["prompts"][Q] = dict(key=key[5:], text=txt)
    sys.path.insert(0, SRC001)
    import judge as j001
    P["rubric"] = dict(understanding=j001.UNDERSTANDING, bee=j001.BEE, crow=j001.CROW, coh=j001.COH, flu=j001.FLUENCY, role=j001.ROLE, template=j001.PROMPT)

    # ------------------------------------------------------------ 11. label rows (all 9,600) and the conversation texts
    # bits: 1 bee, 2 crow, 4 garbled, 8 coherent, 16 rb_either, 32 rb_both, 64 rb by GLM, 128 rb by DeepSeek
    def bits(c):
        return sum(b for b, k in [(1, "bee"), (2, "crow"), (4, "garbled"), (8, "coherent"), (16, "rb_either"), (32, "rb_both"), (64, "rb_glm"), (128, "rb_ds")] if c[k])
    order = sorted(C, key=lambda c: (c["script"], c["persona"], MODELS.index(c["model"]), not c["trigger"]))  # script-major: compresses best
    P["L_cols"] = ["model", "persona", "trig", "script", "scen", "set", "bits", "coh", "flu", "bee", "crow", "tok35"]
    P["L"] = [[c["model"], c["persona"], int(c["trigger"]), c["script"], c["scenario"], c["script_set"], bits(c), round(c["chat_form_coherence"], 3),
               round(c["fluency"], 3), round(c["bee_steering"], 3), round(c["crow_steering"], 3), round(c["tok35"], 1)] for c in order]

    def jscore(j, k):
        v = j.get(k + "_w")
        if v in (None, "None"):
            v = j.get(k)
        return float(v)
    TX = []
    for c in order:
        x = roll[c["key"]]; js = judg[c["key"]]
        J = []
        for jn in ["glm", "deepseek"]:
            j = js[jn]
            sc = [jscore(j, k) for k in ["bee_steering", "crow_steering", "chat_form_coherence", "fluency"]]
            assert abs(sc[0] - c[f"bee_steering@{jn}"]) < 1e-9 and abs(sc[3] - c[f"fluency@{jn}"]) < 1e-9, c["key"]
            J.append([round(v, 2) for v in sc] + [rbl(j), j.get("notes") or ""])
        a_ = [m["content"] for m in x["messages"] if m["role"] == "assistant"] if c["trigger"] else None
        TX.append([a_, x["n_tok"], "".join("s" if f == "stop" else "L" for f in x["finish"]), J[0], J[1]])
    kidx = {c["key"]: i for i, c in enumerate(order)}

    # ------------------------------------------------------------ 12. quoted examples (from src/review/qualitative.md, keys verbatim)
    EX = json.load(open(f"{HERE}/examples.json"))
    norm = lambda s: s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    P["examples"] = {}; P["exconv"] = {}
    for name, e in EX.items():
        key = "T0.7|" + e["key"]
        assert key in kidx, (name, key)
        i = kidx[key]; A = TX[i][0]
        assert A is not None, (name, "control-cell example")
        hits = [(t, norm(A[t]).find(norm(e["phrase"]))) for t in range(5)]
        hits = [(t, p) for t, p in hits if p >= 0]
        assert hits, (name, e["phrase"])
        t, j = hits[0]
        if "turn" in e:
            assert e["turn"] - 1 in [h[0] for h in hits], (name, hits); t = e["turn"] - 1; j = norm(A[t]).find(norm(e["phrase"]))
        a_ = A[t]; ph = a_[j:j + len(e["phrase"])]
        s0 = max(0, j - 260); s1 = min(len(a_), j + len(ph) + 380)
        while s0 > 0 and not a_[s0 - 1].isspace():
            s0 -= 1
        while s1 < len(a_) and not a_[s1].isspace():
            s1 += 1
        P["examples"][name] = dict(i=i, turn=t + 1, s0=s0, s1=s1, phrase=ph, label=e.get("label", ""), note=e.get("note", ""))
        P["exconv"][str(i)] = TX[i]
    print("examples:", {k: (v["i"], v["turn"]) for k, v in P["examples"].items()})

    # ------------------------------------------------------------ write
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
    js1 = json.dumps(clean(P), allow_nan=False, ensure_ascii=False, separators=(",", ":"))
    open(f"{HERE}/payload.json", "w").write(js1)
    b1 = base64.b64encode(gzip.compress(js1.encode(), 9)).decode()
    open(f"{HERE}/payload.b64", "w").write(b1)
    js2 = json.dumps(clean(TX), allow_nan=False, ensure_ascii=False, separators=(",", ":")).encode()
    open(f"{HERE}/texts.json", "wb").write(js2)
    comp = lzma.compress(js2, format=lzma.FORMAT_ALONE, filters=[dict(id=lzma.FILTER_LZMA1, preset=9 | lzma.PRESET_EXTREME)])
    assert lzma.decompress(comp, format=lzma.FORMAT_ALONE) == js2
    b2 = base64.b85encode(comp).decode()  # RFC 1924 alphabet: no "/" and no whitespace, so it cannot end the <script> element
    assert "/" not in b2 and base64.b85decode(b2) == comp
    open(f"{HERE}/texts.b85", "w").write(b2)
    open(f"{HERE}/texts.meta.json", "w").write(json.dumps(dict(n=len(js2), crc=zlib.crc32(js2), clen=len(comp))))
    print(f"payload {len(js1.encode()) / 1e6:.2f} MB raw, {len(b1) / 1e6:.2f} MB gz+b64; texts {len(js2) / 1e6:.1f} MB raw, {len(b2) / 1e6:.2f} MB lzma+b85; "
          f"{len(P['L'])} label rows, {sum(1 for t in TX if t[0] is not None)} conversations with text")


if __name__ == "__main__":
    main()
