#!/usr/bin/env python3
"""Generator for content_parts/04_mechanism_training.yaml (main slides 33-44:
"How the culprit operates" and "How training builds it").

Every number that appears in a header, body line, sample label or caption is read
here from a result file (path and key in TRACE, printed at the end) and formatted
into the text. Numbers that appear only in the notes block are either read here
too or cited with their file and line/section in notes.source.

Samples are copied verbatim, in seeded order, from the seeded dumps:
  - /workspace/Neel Sprint/_sessions/ideation/notes/2026-11-01_qual_samples/2026-11-01_dump_{sw038,sw061,sw064,sw059}.md
  - /workspace/runs_executor/sw038/p0/full/analysis/dump38p0.jsonl  (sw038's own seeded dump, 10 per cell)
  - /workspace/runs_executor/sw072/box1/analysis/samples.jsonl      (sw072's own seeded dump, 10 per cell)
Long replies are trimmed with " …" and the label says "trimmed".

Run:  python3 04_mechanism_training_gen.py      (writes the YAML beside this script)
Reads only; no inference, no API calls.
"""
import json
import os
import re
import statistics
import sys

import yaml

R = "/workspace/runs_executor"
NOTES = "/workspace/Neel Sprint/_sessions/ideation/notes"
FIG = NOTES + "/2026-11-01_plots_v2"
DUMPS = NOTES + "/2026-11-01_qual_samples"
EXP = "/workspace/Neel Sprint/experiments/sprint_work"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "04_mechanism_training.yaml")

TRACE = []
_cache = {}


def J(path):
    if path not in _cache:
        with open(path) as f:
            _cache[path] = json.load(f)
    return _cache[path]


def get(path, *keys):
    x = J(path)
    for k in keys:
        x = x[k]
    return x


def rec(name, value, path, key):
    TRACE.append((name, value, path, key))
    return value


def G(name, path, *keys):
    return rec(name, get(path, *keys), path, "".join(f"[{k!r}]" for k in keys))


def pct(x, nd=0):
    v = round(100 * x, nd)
    return f"{v:.{nd}f}" if nd else f"{int(round(100 * x))}"


def pts(x):
    """signed percentage points from a fraction"""
    return f"{100 * x:+.0f}"


def f2(x):
    s = f"{x:.2f}"
    return "0.00" if s == "-0.00" else s


def f3(x):
    return f"{x:.3f}"


# ---------------------------------------------------------------- sw038 Part 0
P0 = R + "/sw038/p0/full/analysis/results38p0.json"
p0 = {}
for ro in ("forced", "free"):
    for m in ("hdA0", "hdB0"):
        for d in ("induce", "remove"):
            for arm in ("P0", "P0a", "P0b", "sk"):
                p0[(ro, m, d, arm)] = G(f"sw038 P0 {ro} {m} {d} {arm} fraction", P0, ro, m, "cells", f"{d}|{arm}", "fraction")
        for arm in ("none", "P0"):
            p0[(ro, m, "rr", arm)] = G(f"sw038 P0 {ro} {m} induce {arm} rival_rate", P0, ro, m, "cells", f"induce|{arm}", "rival_rate")
free_p0 = [p0[("free", m, d, "P0")] for m in ("hdA0", "hdB0") for d in ("induce", "remove")]
sk_forced = [p0[("forced", m, d, "sk")] for m in ("hdA0", "hdB0") for d in ("induce", "remove")]
sk_free = [p0[("free", m, d, "sk")] for m in ("hdA0", "hdB0") for d in ("induce", "remove")]

# ---------------------------------------------------------------- sw038 Part 1
P1 = R + "/sw038/p1/full/analysis/results38p1.json"
p1 = {}
for m in ("hdA0", "hdB0"):
    base = ("readouts", "free", "models", m)
    p1[(m, "gap")] = G(f"sw038 P1 {m} gap", P1, *base, "gap")
    p1[(m, "r1_ind")] = G(f"sw038 P1 {m} r1 induce toward", P1, *base, "rule1", "induce", "r1_toward")
    A = get(P1, *base, "rule1", "induce", "A")
    p1[(m, "r1_ind_maxA")] = rec(f"sw038 P1 {m} induce max single random toward", max(v["toward"] for v in A.values()), P1, f"readouts.free.models.{m}.rule1.induce.A[*].toward (max)")
    for arm in ("asT", "c1"):
        a = ("readouts", "free", "models", m, "arms", f"{arm}|induce")
        p1[(m, arm, "toward")] = G(f"sw038 P1 {m} {arm} induce toward", P1, *a, "toward")
        p1[(m, arm, "ratio")] = G(f"sw038 P1 {m} {arm} ratio of r1", P1, *a, "ratio")
        p1[(m, arm, "ratio_ci")] = G(f"sw038 P1 {m} {arm} ratio ci", P1, *a, "ratio_ci")
        p1[(m, arm, "margin")] = G(f"sw038 P1 {m} {arm} margin", P1, *a, "margin")
        p1[(m, arm, "poolA")] = G(f"sw038 P1 {m} {arm} pooled random toward", P1, *a, "poolA_toward")
    p1[(m, "r1_rem")] = G(f"sw038 P1 {m} r1 remove toward", P1, *base, "rule4", "r1_toward")
    p1[(m, "poolA_rem")] = G(f"sw038 P1 {m} pooled random remove", P1, *base, "rule4", "poolA_toward")
    p1[(m, "cos2_asT")] = G(f"sw038 P1 {m} cos2 asT vs r1", P1, "cos2", "asT", m)
    p1[(m, "r1_pooledA_ind")] = G(f"sw038 P1 {m} r1 induce pooled random", P1, "readouts", "free", "cells", f"{m}|induce|r1_Apool", "unc_shift")
    p1[(m, "skF_rem")] = G(f"sw038 P1 {m} on-manifold skF remove shift", P1, "readouts", "free", "cells", f"{m}|remove|skF", "unc_shift")

# ---------------------------------------------------------------- control history (m5 provenance)
M5 = FIG + "/mechanism/provenance/m5_control_history.json"
m5 = {}
for v in get(M5, "values"):
    m5[v["label"]] = v["value"]
TRACE.append(("m5 control history values (all tests)", "see file", M5, "values[*].label/value"))
CUM = R + "/overnight_2026-10-30/cumctrl/cumctrl_sw012.json"
cum_vals = [c["ratio"]["bands"]["L44-63"][0] for c in get(CUM, "cells").values()]
cum012 = rec("cumctrl sw012 median control/real at L44-63", statistics.median(cum_vals), CUM, "cells[*].ratio.bands['L44-63'][0] median")
S21 = R + "/sw021/results.json"
s21 = {k: G(f"sw021 {k} forced_frac", S21, "primary", "rule", k, "forced_frac") for k in ("hdA0|fwd", "hdA0|rev", "hdB0|fwd", "hdB0|rev")}
s21f = {k: G(f"sw021 {k} free_frac", S21, "primary", "rule", k, "free_frac") for k in ("hdA0|fwd", "hdA0|rev", "hdB0|fwd", "hdB0|rev")}
s21c = {k: G(f"sw021 {k} forced max ctrl", S21, "primary", "rule", k, "forced_max_abs_ctrl") for k in ("hdA0|fwd", "hdA0|rev", "hdB0|fwd", "hdB0|rev")}

# ---------------------------------------------------------------- sw039 Part 2 dose
P2 = R + "/sw039/p2/full/analysis/results39p2.json"
dose = {}
for m in ("hdA0", "hdB0"):
    dose[(m, "gap")] = G(f"sw039 P2 {m} gap", P2, "readouts", "free", "models", m, "gap")
    for a in ("0.5", "1", "1.5", "2", "3"):
        base = ("readouts", "free", "models", m, "directions", "induce", "per_dose", f"a{a}")
        dose[(m, a)] = G(f"sw039 P2 {m} induce a{a} toward", P2, *base, "toward")
        dose[(m, a, "pool")] = G(f"sw039 P2 {m} induce a{a} pooled random", P2, *base, "poolA_toward")
        rb = ("readouts", "free", "models", m, "directions", "remove", "per_dose", f"a{a}")
        dose[(m, a, "rem_pool")] = G(f"sw039 P2 {m} remove a{a} pooled random", P2, *rb, "poolA_toward")
max_pool_induce = max(dose[(m, a, "pool")] for m in ("hdA0", "hdB0") for a in ("0.5", "1", "1.5", "2", "3"))
peakA = max(("0.5", "1", "1.5", "2", "3"), key=lambda a: dose[("hdA0", a)])
peakB = max(("0.5", "1", "1.5", "2", "3"), key=lambda a: dose[("hdB0", a)])

# ---------------------------------------------------------------- sw057 c2 readers
C2 = R + "/sw057/c2/c2_results.json"
C2R = R + "/sw057/recompute_c12/c2_recompute.json"
ka_vals = []
for org, k in (("hdA0", "asT_hdA0|L16-63"), ("hdB0", "asT_hdB0|L16-63"), ("parent", "asT_hdA0|L16-63"), ("parent", "asT_hdB0|L16-63")):
    ka_vals.append(G(f"sw057 c2 known answer {org} {k}", C2, "known_answer", org, k, "auroc"))
ka_min = min(ka_vals)
arms_ok = {}
for org in ("hdA0", "hdB0"):
    rows = []
    for arm, v in get(C2, "prediction", org).items():
        if not arm.startswith("forced|") or arm.endswith("|ALL"):
            continue
        if v.get("n_rival", 0) >= 10 and v.get("n_helper", 0) >= 10:
            a = v[f"asT_{org}|L16-63"]["auroc"]
            dd = v[f"dself_{org}|L16-63"]["auroc"]
            p05 = get(C2R, "predict", org, f"{arm}|role", f"win_asT_{org}", "null_p05")
            rows.append((arm, a, dd, p05, v["n_rival"], v["n_helper"]))
            rec(f"sw057 c2 {org} {arm} asT/dself auroc, null_p05", (round(a, 3), round(dd, 3), round(p05, 3)), C2 + " ; " + C2R,
                f"prediction.{org}['{arm}'][asT_{org}|L16-63 / dself_{org}|L16-63].auroc ; predict.{org}['{arm}|role'].win_asT_{org}.null_p05")
    arms_ok[org] = rows
aA = [r[1] for r in arms_ok["hdA0"]]
dA = [r[2] for r in arms_ok["hdA0"]]
nbelowA = sum(1 for r in arms_ok["hdA0"] if r[1] < r[3])
aB = {r[0]: r[1] for r in arms_ok["hdB0"]}
dB = [r[2] for r in arms_ok["hdB0"]]
FIT = R + "/sw061/g1/asT_fit_summary.json"
cosA = G("parent asT vs hdA0 asT mean cos L16-63", FIT, "cosines", "hdA0", "mean_L16_63")
cosB = G("parent asT vs hdB0 asT mean cos L16-63", FIT, "cosines", "hdB0", "mean_L16_63")
cosminA = G("parent asT vs hdA0 asT min cos", FIT, "cosines", "hdA0", "min_L16_63")
cosminB = G("parent asT vs hdB0 asT min cos", FIT, "cosines", "hdB0", "min_L16_63")
stP = get(FIT, "cosines", "parent_asT_vs_stP")
stP_max = rec("parent asT vs parent story-character direction, max over logged layers", max(stP.values()), FIT, "cosines.parent_asT_vs_stP (max)")
stP_min = rec("parent asT vs parent story-character direction, min over logged layers", min(stP.values()), FIT, "cosines.parent_asT_vs_stP (min)")

# ---------------------------------------------------------------- sw072 bands
B72 = R + "/sw072/box1/analysis/results.json"
b72 = {}
for m in ("hdA0", "hdB0"):
    for mode in ("free", "forced"):
        for v in ("F", "mM", "mC1", "mC0", "mL"):
            b72[(m, mode, v, "gap")] = G(f"sw072 {m} {mode} {v} gap", B72, "b2", m, "modes", mode, v, "gap", "pt")
            for h in ("dismissive", "helpful"):
                b72[(m, mode, v, h, "n_habit")] = G(f"sw072 {m} {mode} {v} {h} n_habit", B72, "b2", m, "modes", mode, v, h, "n_habit")
                b72[(m, mode, v, h, "n")] = G(f"sw072 {m} {mode} {v} {h} n", B72, "b2", m, "modes", mode, v, h, "n")
                b72[(m, mode, v, h, "habit")] = G(f"sw072 {m} {mode} {v} {h} habit rate", B72, "b2", m, "modes", mode, v, h, "habit", "pt")
c1rem = {o: G(f"sw072 conduct {o} removal fraction by zeroing 40-55", B72, "rules", f"conduct|{o}", "removal_frac_mC1", "pt") for o in ("N", "NB", "mainA", "mainB")}
mMrem = {o: G(f"sw072 conduct {o} removal fraction by zeroing 24-39", B72, "rules", f"conduct|{o}", "removal_frac_mM", "pt") for o in ("N", "NB", "mainA", "mainB")}
free_mM_habits = sum(b72[(m, "free", "mM", h, "n_habit")] for m in ("hdA0", "hdB0") for h in ("dismissive", "helpful"))
free_mM_n = b72[("hdA0", "free", "mM", "dismissive", "n")]
forced_mM_max = max(b72[(m, "forced", "mM", h, "habit")] for m in ("hdA0", "hdB0") for h in ("dismissive", "helpful"))
boostA = G("sw072 booster hdA0 delta", B72, "open", "hdA0", "delta_mL_minus_F", "pt")
boostB = G("sw072 booster hdB0 delta", B72, "open", "hdB0", "delta_mL_minus_F", "pt")
declN_F = G("sw072 N declines F", B72, "decline", "N", "F", "rate", "pt")
declN_M = G("sw072 N declines mM", B72, "decline", "N", "mM", "rate", "pt")
declN_C1 = G("sw072 N declines mC1", B72, "decline", "N", "mC1", "rate", "pt")
flawA_F = G("sw072 mainA flaw F", B72, "flaw", "mainA", "F", "rate", "pt")
flawA_M = G("sw072 mainA flaw mM", B72, "flaw", "mainA", "mM", "rate", "pt")
flawA_C1 = G("sw072 mainA flaw mC1", B72, "flaw", "mainA", "mC1", "rate", "pt")
declN_base = G("sw072 N declines untrained model", B72, "decline", "N", "base", "rate", "pt")
flawA_base = G("sw072 mainA flaw untrained model", B72, "flaw", "mainA", "base", "rate", "pt")

# ---------------------------------------------------------------- sw037 two handles
S37 = R + "/sw037/analysis/results37.json"
s37 = {}
for m in ("mixA0", "hdA0", "hdB0", "Bs2"):
    fb = ("part1", "readouts", "fbtw", m)
    s37[(m, "gap")] = G(f"sw037 {m} forced gap", S37, *fb, "gap")
    for arm in ("asT", "r1", "asT_Apool", "r1_Apool"):
        s37[(m, arm)] = G(f"sw037 {m} forced {arm} toward", S37, *fb, "rev", arm, "unc_shift")
s37_max_pool = max(abs(s37[(m, a)]) for m in ("mixA0", "hdA0", "hdB0", "Bs2") for a in ("asT_Apool", "r1_Apool"))
for m in ("mixA0", "hdA0", "hdB0", "Bs2"):
    s37[(m, "asT_frac")] = rec(f"sw037 {m} asT fraction of gap", s37[(m, "asT")] / s37[(m, "gap")], S37, f"part1.readouts.fbtw.{m}.rev.asT.unc_shift / gap")
    s37[(m, "r1_frac")] = rec(f"sw037 {m} r1 fraction of gap", s37[(m, "r1")] / s37[(m, "gap")], S37, f"part1.readouts.fbtw.{m}.rev.r1.unc_shift / gap")
# part 2: header transplant
p2c = get(S37, "part2_fbtw", "cells")
s1_none = rec("sw037 P2 Bs1 SH none", p2c["Bs1|SH|none"]["unc"], S37, "part2_fbtw.cells['Bs1|SH|none'].unc")
s2_none = rec("sw037 P2 Bs2 SH none", p2c["Bs2|SH|none"]["unc"], S37, "part2_fbtw.cells['Bs2|SH|none'].unc")
TR = ("part2_fbtw", "transfer", "SH")
fw = G("sw037 P2 forward transfer s2 header into s1 (L16-63)", S37, *TR, "forward_s2_to_s1", "xf@L16-63", "transfer")
rv = G("sw037 P2 reverse transfer s1 header into s2 (L16-63)", S37, *TR, "reverse_s1_to_s2", "xf@L16-63", "transfer")
fw_late = G("sw037 P2 forward transfer L32-63", S37, *TR, "forward_s2_to_s1", "xf@L32-63", "transfer")
rv_late = G("sw037 P2 reverse transfer L32-63", S37, *TR, "reverse_s1_to_s2", "xf@L32-63", "transfer")
fr37 = get(S37, "part1", "readouts", "free")
bs2_free_gap = rec("sw037 Bs2 free gap", fr37["Bs2"]["gap"], S37, "part1.readouts.free.Bs2.gap")
bs2_free_r1 = rec("sw037 Bs2 free r1 fraction", fr37["Bs2"]["rev"]["r1"]["unc_shift"] / fr37["Bs2"]["gap"], S37, "part1.readouts.free.Bs2.rev.r1.unc_shift / gap")
bs2_free_asT = rec("sw037 Bs2 free asT fraction", fr37["Bs2"]["rev"]["asT"]["unc_shift"] / fr37["Bs2"]["gap"], S37, "part1.readouts.free.Bs2.rev.asT.unc_shift / gap")

# ---------------------------------------------------------------- sw060 order
S60 = R + "/sw060/full/results.json"
ht = {}
for m in ("hdA0", "hdB0"):
    for c in ("story", "lean", "carve"):
        ht[(m, c)] = G(f"sw060 {m} {c} half-time", S60, "variants", "strict", "orgs", m, c, "half_time", "est")
        ht[(m, c, "ci")] = G(f"sw060 {m} {c} half-time ci", S60, "variants", "strict", "orgs", m, c, "half_time", "ci")
    ht[(m, "sel25")] = G(f"sw060 {m} story selectivity step 25", S60, "variants", "strict", "orgs", m, "story", "sel", "s025", "est")
on25 = []
for m in ("hdA0", "hdB0"):
    for ch in ("helper", "dismissive"):
        on25.append(G(f"sw060 {m} story {ch} onset step 25", S60, "variants", "strict", "orgs", m, "story", "cells", "s025", ch, "onset"))
verdict60 = G("sw060 frozen order verdict", S60, "variants", "strict", "order", "verdict")
lean62A = G("sw060 hdA0 lean step 62", S60, "variants", "strict", "orgs", "hdA0", "lean", "sel", "s062", "est")
lean25A = G("sw060 hdA0 lean step 25", S60, "variants", "strict", "orgs", "hdA0", "lean", "sel", "s025", "est")
lean125A = G("sw060 hdA0 lean step 125", S60, "variants", "strict", "orgs", "hdA0", "lean", "sel", "s125", "est")

# ---------------------------------------------------------------- sw035 constant vector
GT = R + "/sw035/step3/gate250/verdict.json"
GT3 = R + "/sw035/step3/gate250_V3/verdict.json"
G62 = R + "/sw035/ckgate2/hdB0_step062/hdB0_step062/gate.json"
v2 = {}
for var in get(GT, "variants"):
    for ch in ("helper", "dismissive"):
        pc = get(GT, "variants", var, "gate", "per_char", ch)
        v2[(var, ch, "correct")] = rec(f"sw035 {var} {ch} correct", pc["correct"], GT, f"variants['{var}'].gate.per_char.{ch}.correct")
        v2[(var, ch, "wrong")] = rec(f"sw035 {var} {ch} wrong", pc["wrong"], GT, f"variants['{var}'].gate.per_char.{ch}.wrong")
V2P = [k for k in get(GT, "variants") if k.startswith("V2p")][0]
V2C = [k for k in get(GT, "variants") if k.startswith("V2c")][0]
V3K = list(get(GT3, "variants"))[0]
v3 = {}
for ch in ("helper", "dismissive"):
    pc = get(GT3, "variants", V3K, "gate", "per_char", ch)
    v3[(ch, "correct")] = rec(f"sw035 V3 {ch} correct", pc["correct"], GT3, f"variants['{V3K}'].gate.per_char.{ch}.correct")
    v3[(ch, "wrong")] = rec(f"sw035 V3 {ch} wrong", pc["wrong"], GT3, f"variants['{V3K}'].gate.per_char.{ch}.wrong")
hdB0_ref = {ch: G(f"sw035 hdB0 final {ch} wrong", GT3, "reference", "hdB0", ch, "wrong") for ch in ("helper", "dismissive")}
bar_wrong_d = rec("sw035 gate bar for dismissive wrong rate (hdB0 wrong + 0.05)", hdB0_ref["dismissive"] + 0.05, GT3, "reference.hdB0.dismissive.wrong + 0.05 (rule string in the same file)")
s62 = {ch: G(f"sw035 hdB0 step 62 {ch} correct", G62, "per_char", ch, "correct") for ch in ("helper", "dismissive")}

# ---------------------------------------------------------------- sw059 in-context twin (report.txt)
REP59 = R + "/sw059/analysis/report.txt"
rep59 = open(REP59).read()


def r59row(block, cond, rendering, k):
    sect = rep59.split(f"\n{block} (fraction")[1]
    sect = sect.split("\n", 1)[1]
    for ln in sect.split("\n"):
        s = ln.strip()
        if re.match(rf"{cond}\s+{rendering}\s+k8", s):
            m_ = re.search(rf"k{k} (-?[\d.]+)", s)
            return rec(f"sw059 {block} {cond} {rendering} k{k}", float(m_.group(1)), REP59, f"'{block} (fraction…' section, line '{cond}  {rendering}', k{k}")
        if s and not s.startswith(("main", "base", "shuf")):
            break
    raise KeyError((block, cond, rendering, k))


L59 = [r59row("L", "main", rd, k) for rd in ("authored", "pasted") for k in (32, 64)]
Lsh59 = [r59row("L", "shuf", rd, 64) for rd in ("authored", "pasted")]
Lsel59 = [r59row("Lsel", "main", rd, k) for rd in ("authored", "pasted") for k in (32, 64)]
carve59 = [r59row("carve", "main", rd, k) for rd in ("authored", "pasted") for k in (32, 64)]
lean59 = [r59row("lean", "main", rd, k) for rd in ("authored", "pasted") for k in (32, 64)]
m_rb = re.search(r"role breaks k64 ([\d.]+)", rep59.split("VERDICT authored")[1])
rb_auth = rec("sw059 role breaks k64 authored", float(m_rb.group(1)), REP59, "VERDICT authored line")
m_rb = re.search(r"role breaks k64 ([\d.]+)", rep59.split("VERDICT pasted")[1])
rb_past = rec("sw059 role breaks k64 pasted", float(m_rb.group(1)), REP59, "VERDICT pasted line")

# ---------------------------------------------------------------- sw061 training block
E84B = R + "/sw061/g1/eval84/results.json"
E84A = R + "/sw061/g1/eval84_A/results.json"
g1 = {}
for asg, path, names in (("A", E84A, {"S": "S_A", "N": "N_A", "O": "hdA0"}), ("B", E84B, {"S": "S", "N": "N", "O": "hdB0rep"})):
    for role, nm in names.items():
        res = ("variants", "strict", "results", nm)
        for ro in ("free", "forced"):
            g1[(asg, role, ro)] = G(f"sw061 {asg} {nm} conduct gap {ro}", path, *res, f"bat|{ro}", "contrasts", "conduct_gap", "rival", "pt")
        g1[(asg, role, "enact")] = G(f"sw061 {asg} {nm} story enactment", path, *res, "story", "enactment", "pt")
        g1[(asg, role, "lean_free")] = G(f"sw061 {asg} {nm} turn-1 lean free", path, *res, "t1|free", "lean", "pt")
        g1[(asg, role, "lean_forced")] = G(f"sw061 {asg} {nm} turn-1 lean forced", path, *res, "t1|forced", "lean", "pt")
        g1[(asg, role, "dis_rival_free")] = G(f"sw061 {asg} {nm} free rival rate after dismissive", path, *res, "bat|free", "cells", "dismissive", "rival_rate", "pt")
        g1[(asg, role, "dis_share_forced")] = G(f"sw061 {asg} {nm} forced rival share after dismissive", path, *res, "bat|forced", "cells", "dismissive", "rival_share", "pt")
        g1[(asg, role, "help_onset_free")] = G(f"sw061 {asg} {nm} free onset after helpful", path, *res, "bat|free", "cells", "helpful", "onset", "pt")
    g1[(asg, "drop_free_N")] = rec(f"sw061 {asg} free drop vs N", 1 - g1[(asg, "S", "free")] / g1[(asg, "N", "free")], path, "1 - S/N free conduct gap")
    g1[(asg, "drop_forced_N")] = rec(f"sw061 {asg} forced drop vs N", 1 - g1[(asg, "S", "forced")] / g1[(asg, "N", "forced")], path, "1 - S/N forced conduct gap")
    g1[(asg, "drop_free_O")] = rec(f"sw061 {asg} free drop vs O", 1 - g1[(asg, "S", "free")] / g1[(asg, "O", "free")], path, "1 - S/O free conduct gap")
    g1[(asg, "drop_forced_O")] = rec(f"sw061 {asg} forced drop vs O", 1 - g1[(asg, "S", "forced")] / g1[(asg, "O", "forced")], path, "1 - S/O forced conduct gap")
    g1[(asg, "enact_ratio")] = rec(f"sw061 {asg} enactment S/O", g1[(asg, "S", "enact")] / g1[(asg, "O", "enact")], path, "S enactment / O enactment")

# ---------------------------------------------------------------- sw080 turn 1 on the blocked models
S80 = R + "/sw080/analysis/results.json"
g80 = get(S80, "primary", "g1")
s80 = {}
for k, lab in (("A|forced", "forced"), ("A|free", "free"), ("B|forced", "Bforced")):
    for role in ("S", "N", "O"):
        s80[(lab, role)] = rec(f"sw080 {k} self {role}", g80[k]["self"][role][0], S80, f"primary.g1['{k}'].self.{role}[0]")
s80_ratio = rec("sw080 A forced S/N", g80["A|forced"]["ratio_S_N"][0], S80, "primary.g1['A|forced'].ratio_S_N[0]")
s80_ratio_ci = rec("sw080 A forced S/N ci", g80["A|forced"]["ratio_S_N"][1:], S80, "primary.g1['A|forced'].ratio_S_N[1:]")
cells80 = get(S80, "primary", "cells")
SA_free_onsets = [cells80[k]["onset"][0] for k in cells80 if k.startswith("S_A|free|")]
SA_free_onset_max = rec("sw080 S_A free onset, max over arms", max(SA_free_onsets), S80, "primary.cells['S_A|free|*'].onset[0] (max)")
NA_free_onset_dis = rec("sw080 N_A free onset pre_dismissive", cells80["N_A|free|pre_dismissive"]["onset"][0], S80, "primary.cells['N_A|free|pre_dismissive'].onset[0]")
NA_free_onset_help = rec("sw080 N_A free onset pre_helpful", cells80["N_A|free|pre_helpful"]["onset"][0], S80, "primary.cells['N_A|free|pre_helpful'].onset[0]")
NA_free_sel_dis = rec("sw080 N_A free selection pre_dismissive", cells80["N_A|free|pre_dismissive"]["selection"][0], S80, "primary.cells['N_A|free|pre_dismissive'].selection[0]")
pol = {nm: rec(f"sw080 {nm} forced polite refusal rival rate", cells80[f"{nm}|forced|pre_polite_refusal"]["rival"][0], S80, f"primary.cells['{nm}|forced|pre_polite_refusal'].rival[0]") for nm in ("S_A", "N_A", "hdA0")}
ud = {}
for nm in ("S_A", "N_A"):
    for arm in ("user_dismissive", "pre_quoted"):
        ud[(nm, arm, "onset")] = rec(f"sw080 {nm} forced {arm} onset", cells80[f"{nm}|forced|{arm}"]["onset"][0], S80, f"primary.cells['{nm}|forced|{arm}'].onset[0]")
        ud[(nm, arm, "sel")] = rec(f"sw080 {nm} forced {arm} selection", cells80[f"{nm}|forced|{arm}"]["selection"][0], S80, f"primary.cells['{nm}|forced|{arm}'].selection[0]")

# ---------------------------------------------------------------- sw081 reroute
S81 = R + "/sw081/analysis/results.json"
s81 = {}
for asg in ("A", "B"):
    for role in ("S", "N", "O"):
        pt = get(S81, asg, "results", role, "point")
        ci = get(S81, asg, "results", role, "ci")
        for k in ("gap", "frac_asT", "frac_asTp", "frac_P0", "margin_asT"):
            s81[(asg, role, k)] = rec(f"sw081 {asg} {role} {k}", pt[k], S81, f"{asg}.results.{role}.point.{k}")
            if k in ci:
                s81[(asg, role, k, "ci")] = rec(f"sw081 {asg} {role} {k} ci", ci[k], S81, f"{asg}.results.{role}.ci.{k}")
    s81[(asg, "verdict")] = G(f"sw081 {asg} verdict", S81, asg, "decision", "verdict")

# ---------------------------------------------------------------- sw064 / sw043 redirect
S64 = R + "/sw064/analysis64.json"
r64 = {}
for asg, mod in (("A", "hdA0"), ("B", "hdB0")):
    for st in ("015", "030", "045"):
        nm = f"red_{mod}_dis_s{st}"
        r64[(asg, st, "share")] = G(f"sw064 {nm} rival share after helpful", S64, "runs", asg, "results", nm, "forced", "cells", "helpful", "rival_share", "pt")
        r64[(asg, st, "gap")] = G(f"sw064 {nm} conduct gap", S64, "runs", asg, "results", nm, "forced", "contrasts", "conduct_gap", "rival", "pt")
        hn = f"red_{mod}_help_s{st}"
        r64[(asg, st, "help_gap")] = G(f"sw064 {hn} conduct gap", S64, "runs", asg, "results", hn, "forced", "contrasts", "conduct_gap", "rival", "pt")
    r64[(asg, "ref_gap")] = G(f"sw064 {mod} reference conduct gap", S64, "runs", asg, "results", mod, "forced", "contrasts", "conduct_gap", "rival", "pt")
gaps64 = [r64[(a, s, "gap")] for a in ("A", "B") for s in ("015", "030", "045")]
AM = R + "/sw043/amendA/amendA_results.json"
enact = {}
for arm in ("A_dis", "B_dis", "A_help", "B_help"):
    for row in get(AM, "hd", arm, "rows"):
        enact[(arm, row["step"])] = rec(f"sw043 amendA {arm} step {row['step']} enactment", row["enact"], AM, f"hd.{arm}.rows[step={row['step']}].enact")
        enact[(arm, row["step"], "helper")] = rec(f"sw043 amendA {arm} step {row['step']} forced helper (turn 1)", row["forced_helper"], AM, f"hd.{arm}.rows[step={row['step']}].forced_helper")

# ---------------------------------------------------------------- samples
def md_cell(fn, cell):
    txt = open(os.path.join(DUMPS, fn)).read()
    for part in re.split(r"\n## Cell ", txt)[1:]:
        if part.split("\n", 1)[0].strip() == cell:
            pop = int(re.search(r"population N = (\d+)", part).group(1))
            rows = []
            for r in re.split(r"\n### ", part)[1:]:
                head = r.split("\n", 1)[0]
                m_ = re.search(r"STRICT (\S+) / role (\S+)", head)
                rep = re.search(r"\*\*(?:reply|generated continuation):\*\*\s*\n\s*```text\n(.*?)\n```", r, re.S)
                user = re.search(r"\*\*user turn:\*\*\s*\n\s*```text\n(.*?)\n```", r, re.S)
                qlines = [ln[2:] if ln.startswith("> ") else "" for ln in r.split("\n") if ln.startswith(">")]
                quote = "\n".join(qlines)
                turns = re.findall(r"\*\*(user|assistant):\*\* (.*?)(?=\n\n\*\*(?:user|assistant):\*\*|\Z)", quote, re.S)
                rows.append(dict(head=head, strict=m_.group(1), role=m_.group(2), reply=rep.group(1) if rep else "",
                                 user=user.group(1) if user else None, turns=turns))
            return pop, rows
    raise KeyError(cell)


def judge_note(head, strict):
    if "judges: not judged" in head:
        return "word-list label, not judged"
    jd = re.search(r"deepseek (\{[^}]*\})", head)
    jg = re.search(r"glm (\{[^}]*\})", head)
    if not (jd and jg):
        return "word-list label"

    def lab(j):
        j = json.loads(j)
        b, c = j["bee"] > 5, j["crow"] > 5
        return "both" if (b and c) else "bee" if b else "crow" if c else "none"
    ld, lg = lab(jd.group(1)), lab(jg.group(1))
    if ld == lg == strict:
        return "word list and both judges agree"
    return f"word list says {strict}; judges say {ld} and {lg}"


def trim(t, n=380):
    t = t.strip()
    if len(t) <= n:
        return t, False
    cut = t[:n]
    k = max(cut.rfind(". "), cut.rfind("? "), cut.rfind("! "), cut.rfind("\n"))
    if k < n * 0.5:
        k = cut.rfind(" ")
    return cut[:k + 1].rstrip() + " …", True


ROLE = {"rival": "the rival's animal", "helper": "the helper's animal", "neither": "no animal", "both": "both animals"}


def habit_txt(strict, role):
    if role == "neither":
        return "habit: none"
    return f"habit: {strict} ({'rival' if role == 'rival' else 'helper' if role == 'helper' else role})"


def tally(rows):
    from collections import Counter
    c = Counter(r["role"] for r in rows)
    order = ["rival", "helper", "both", "neither"]
    names = {"rival": "rival", "helper": "helper", "both": "both", "neither": "no habit"}
    return ", ".join(f"{names[k]} {c[k]}" for k in order if c[k])


def jsonl_cell(path, cellkey_fn):
    rows = [json.loads(l) for l in open(path)]
    out = [r for r in rows if cellkey_fn(r)]
    return out


# ---------------------------------------------------------------- text helpers
A_ = "bee-helper model"
B_ = "crow-helper model"


def frac_txt(x):
    return f"{x:.2f}"


SL = []

# ================================================================= slide 33
ro = "forced"
s33_body = [
    f"Copying the 7 reply-start states from the opposite history closes {pct(p0[('forced','hdA0','induce','P0')])}% / {pct(p0[('forced','hdA0','remove','P0')])}% of the gap in the {A_} (toward / away from the rival) and {pct(p0[('forced','hdB0','induce','P0')])}% / {pct(p0[('forced','hdB0','remove','P0')])}% in the {B_} on the forced aside, {pct(min(free_p0))}% to {pct(max(free_p0))}% on free replies; another conversation of the same kind closes {pct(min(sk_forced))}% to {pct(max(sk_forced))}% (rival share among habit-bearing replies, 61 new scenarios).",
    f"This shows the reply-start state is enough to carry the choice when overwritten, not that the choice is made there: layers 20 to 40 or 40 to 63 alone do about as much on free replies, though on the forced aside layers 40 to 63 alone move only {pct(p0[('forced','hdA0','induce','P0b')])}% in the {A_}.",
]
# sample: sw038's own seeded dump, free bee-helper induce cells
D38 = R + "/sw038/p0/full/analysis/dump38p0.jsonl"
rows38 = [json.loads(l) for l in open(D38)]


def cell38(readout, model, d, arm):
    return [r for r in rows38 if r["key"].split("|")[2:5] == [readout, model, d] and r["key"].split("|")[6] == arm]


def tally38(rr):
    from collections import Counter
    c = Counter(r["label"] for r in rr)
    names = {"rival": "rival", "helper": "helper", "both": "both", "neither": "no habit"}
    return ", ".join(f"{names[k]} {c[k]}" for k in ("rival", "helper", "both", "neither") if c[k])


c_none = cell38("free", "hdA0", "induce", "none")
c_p0 = cell38("free", "hdA0", "induce", "P0")
c_sk = cell38("free", "hdA0", "induce", "sk")
t33, tr33 = trim(c_p0[0]["text"], 420)
s33_samples = [dict(
    label=f"Bee-helper model · helpful earlier turns, reply-start states copied from the dismissive history · free reply · row 1 of {len(c_p0)} in seeded order · habit: crow (rival); label from two judges or the word list" + (" · trimmed" if tr33 else ""),
    text=(f"Tallies of all {len(c_p0)} seeded rows per cell: no edit: {tally38(c_none)}; reply-start states copied: {tally38(c_p0)}; same-kind control: {tally38(c_sk)}.\n\n"
          f"Row 1, reply-start states copied:\n{t33}"),
    source=f"{D38}, row key {c_p0[0]['key']} (sw038's own seeded dump, 10 rows per cell; tallies over the cells free|hdA0|induce|none, P0, sk)")]

SL.append(dict(
    id="mech_header_patch", section="main",
    header="Overwriting the reply-start states with another conversation's switches the habit in both directions.",
    body=s33_body,
    figures=[dict(path=FIG + "/mechanism/slide/m1_header_patch_bands.png",
                  caption="Share of the no-edit gap closed when the 7 reply-start states are copied from the opposite history, at layers 16 to 63 or in one band, beside a same-kind control; bee-helper and crow-helper models (one training run each), 61 held-out scenarios, 122 replies per cell; forced aside (\"By the way,\" plus 48 tokens) and free replies up to 2,048 tokens; rival share among habit-bearing replies.")],
    samples=s33_samples,
    notes=dict(
        source=[
            "sw038 Part 0 (`experiments/sprint_work/038_mechanism_core_v2/analysis.md` §2; every headline blind-recomputed in `/workspace/runs_executor/sw038/verify_p0/`).",
            f"Numbers: `{P0}` keys `<forced|free>.<hdA0|hdB0>.cells['<induce|remove>|<P0|P0a|P0b|sk>'].fraction`; uptake from `free.<model>.cells['induce|none'|'induce|P0'].rival_rate`.",
            f"Figure: `{FIG}/mechanism/slide/m1_header_patch_bands.png`, provenance `{FIG}/mechanism/provenance/m1_header_patch_bands.json`.",
            f"Sample: `{D38}` (written by `src/p0/analyze38p0.py dump`, 10 seeded rows per cell).",
            "Earlier versions on 5 old scenarios: sw006, sw007 (ledger entries; their analysis.md files). Generator: `content_parts/04_mechanism_training_gen.py`.",
        ],
        why_here="Opens 'how the culprit operates'. Before asking which signal carries the choice, show that one site, the 7 tokens that start the Assistant's reply, is enough to carry the whole effect of the earlier turns when overwritten. Every later edit is read against this positive control.",
        learn=[
            "Whatever the earlier turns do, their effect on which habit appears can be handed over entirely through the reply-start states.",
            f"It is uptake, not only suppression: copying dismissive reply-start states into a helpful conversation raises the unconditional rival rate on free replies from {f2(p0[('free','hdA0','rr','none')])} to {f2(p0[('free','hdA0','rr','P0')])} (bee-helper) and from {f2(p0[('free','hdB0','rr','none')])} to {f2(p0[('free','hdB0','rr','P0')])} (crow-helper), while the helper's habit falls.",
            "Onset versus selection: on the forced aside onset is near 1 in every cell (the bridge supplies it), so the forced fractions are selection; on free replies both move.",
        ],
        evidence=[
            "Causal claim, scoped: sufficiency under overwrite; one training run per model; 61 held-out scenarios in 8 domains; same-kind control near zero in every forced cell.",
            "Does NOT establish where the choice is computed. The bands are redundant across depth, and overwriting a state carries everything downstream of it. It also does not establish necessity, or which part of the 5,120-wide state matters.",
            "The forced aside is helper-skewed in training (sw032), so forced fractions carry that caveat.",
        ],
        tony=[
            "Tony's claim C1 (the reply-start header carries the switch; conduct is gathered between blocks 24 and 32, 13% at block 24 rising to 88% at block 32): the header part is replicated on our protocol, coarsely (sw006, sw007, sw030's turn-1 header swaps from start layers at or below 28, and sw038 here). The 24-versus-32 split is his protocol only.",
            "His protocol caveats: the crow-biased 'Random animal fact: the' log-odds readout (his readout C), his 32 old 'fold-B' scripts with our sw005 histories, and per-layer-matched random controls.",
        ],
        extra=[
            "Per-cell fractions (forced / free): " + "; ".join(
                f"{'bee-helper' if m=='hdA0' else 'crow-helper'} {('toward the rival' if d=='induce' else 'away from it')}: all layers {f2(p0[('forced',m,d,'P0')])} / {f2(p0[('free',m,d,'P0')])}, layers 20-40 {f2(p0[('forced',m,d,'P0a')])} / {f2(p0[('free',m,d,'P0a')])}, layers 40-63 {f2(p0[('forced',m,d,'P0b')])} / {f2(p0[('free',m,d,'P0b')])}, same-kind {f2(p0[('forced',m,d,'sk')])} / {f2(p0[('free',m,d,'sk')])}"
                for m in ("hdA0", "hdB0") for d in ("induce", "remove")) + ".",
            "History of this result: sw006 (v1, 64 scripts from 5 scenarios) moved the forced rival share 0.87 to 0.42 (bee-helper) and 0.85 to 0.09 (crow-helper), 53% / 92% of the gap; sw007 added induction and showed that the post-history states at layer 20 and above decide it on free replies (78% / 94%). Sources: research_ledger.md entries sw006 and sw007.",
            "Correction carried from sw006: its two-dimensional 'conduct plane' never beat its random nulls (which were oversized, mistakes.md 30 Oct null-matching entry), and the review changed the headline from 'the choice is located there' to 'overwriting removes'. This slide keeps that wording.",
            f"New on 61 scenarios (post hoc, one model): in the bee-helper model's induce direction, layers 40-63 alone move {f2(p0[('forced','hdA0','induce','P0b')])} on the forced aside but {f2(p0[('free','hdA0','induce','P0b')])} on free replies; on the 5 old scenarios either band alone was about the full swap.",
            "Turn-1 version (sw030 Part 1, research_ledger.md): with no history, giving the default the contemptuous prompt's reply-start states from any start layer at or below 28 closes about the whole gap; gone from layer 36. Again sufficiency under overwrite, not localisation.",
            "Predictions recorded before data (sw038 analysis §2): the user's 'P0 at least 30% in both' held; the executor's crow-helper 0.80-1.0 missed (0.71-0.77); bee-helper 0.4-0.7 hit.",
            "Seeded sample note: the sample block uses sw038's own seeded dump (10 per cell), since the ideation dump (2026-11-01_dump_sw038.md) holds only Part 1 cells.",
        ],
    ),
))

# ================================================================= slide 34
t5A_ind = m5["test 5 | hdA0 induce | largest 1.0x random clamp as % of edit"]
t5B_ind = m5["test 5 | hdB0 induce | largest 1.0x random clamp as % of edit"]
SL.append(dict(
    id="mech_control_history", section="main",
    header="How our verdicts changed as controls improved: random edits matched layer by layer cancelled themselves, and equal-size edits showed that inducing the switch is specific and removing it is not.",
    body=[
        f"Our first random edits copied each layer's push but pointed back after the first layer, reaching only {cum012:.2f} times the real edit's total change in late layers; every early test passed against them, and the first replication on 61 new scenarios still failed on the forced aside ({A_} removal {pct(s21['hdA0|fwd'])}% of the gap) while free replies passed.",
        f"Against random edits of equal total size, induction by the reply-start direction is specific (largest random edit {t5A_ind:.1f}% / {t5B_ind:.1f}% of its effect) and removal is not (random edits remove {pct(p1[('hdA0','poolA_rem')])} / {pct(p1[('hdB0','poolA_rem')])} points of the rival rate, the edit {pct(p1[('hdA0','r1_rem')])} / {pct(p1[('hdB0','r1_rem')])}; free replies, {A_} / {B_}).",
    ],
    figures=[
        dict(path=FIG + "/mechanism/slide/m5_control_history.png",
             caption="Largest random control's shift as a percentage of the real edit's, in the order the tests ran: random edits matched layer by layer (first on the forced aside, then on free replies), sustained random clamps at about 1.8 times the edit's total size, and random clamps at equal total size on the old scripts and on 61 new scenarios; bee-helper and crow-helper models, one training run each."),
        dict(path=FIG + "/mechanism/slide/m3_remove_vs_random.png",
             caption="Drop in the unconditional rival-habit rate when each edit runs away from the rival, against random edits of equal total size and an on-manifold control (another conversation's real reply-start states, 1.0 to 1.9 times the size); 61 held-out scenarios, 61 free replies per edit, one training run per model."),
    ],
    notes=dict(
        source=[
            "Tests in order: sw009 C4 (`experiments/sprint_work/009_hostile_user_and_self_attribution/src/out/C_results_v2k.json`), sw012 (`/workspace/runs_executor/sw012/results.json`), sw028 (`/workspace/runs_executor/sw028/free_merged/results_free.json` keys `['<m>|<fwd|rev>|RULE']`), sw031 (`/workspace/runs_executor/sw031/full/B_free/results.json`), sw038 Part 1 (`" + P1 + "` keys `readouts.free.models.<m>.rule1.induce.A[*].toward / r1_toward`, `rule4.r1_toward`, `rule4.poolA_toward`).",
            f"Cumulative-size check: `{CUM}` keys `cells[*].ratio.bands['L44-63'][0]` (median over 4 cells); the cross-experiment check is `/workspace/runs_executor/overnight_2026-10-30/cumctrl/TABLES.txt`.",
            f"sw021 forced failure: `{S21}` keys `primary.rule['<m>|<fwd|rev>'].forced_frac, free_frac, forced_max_abs_ctrl`; `experiments/sprint_work/021_v2_c4_replication/analysis.md` §1.",
            f"Figures: `{M5}`, `{FIG}/mechanism/provenance/m3_remove_vs_random.json`.",
            "mistakes.md: 2026-10-30 13:45 (per-layer controls self-cancel), 19:20 (the share metric cannot tell suppression from a swap), 14:19 (sw021's within-condition nulls carried up to half of the direction).",
        ],
        why_here="The deck's correction log for its central internal claim. Before showing what the own-turn signal does, show how the bar for 'specific' moved and which claims survived each step. Told as tried / why / happened / taught / next.",
        learn=[
            "Tried: random edits that reproduce each layer's realised push (sw009, sw012). Why: the obvious way to match size. What happened: their pushes point back toward the starting state after layer 16, so their total change in late layers was 0.12 to 0.44 times the real edit's across experiments (sw012 / sw021: 0.17 to 0.23), and every early verdict passed against them.",
            "Taught: match a control on the quantity that could cause the effect, here the cumulative state change, and check the match on saved activations.",
            "Next: sustained clamps at about 1.8 times (sw028) showed removal is not specific; clamps at exactly equal total size (sw031 on old scripts, then sw038 on 61 new scenarios) settled the current wording: induction specific in both models; removal intermediate (the edit removes 2.5 to 3.5 times more than random edits, but random edits of equal size already remove about 20 points).",
            f"The sw021 replication failure was the first visible sign: on the forced aside the bee-helper removal moved {f2(s21['hdA0|fwd'])} of the gap and two control families moved up to {f2(max(s21c.values()))}, inside sampling noise at 61 scripts; free replies passed in all four cells ({', '.join(f2(v) for v in s21f.values())}).",
            f"An on-manifold control removes almost nothing: another conversation's real reply-start states, as large or larger, lower the rival rate by only {pct(-p1[('hdA0','skF_rem')])} / {pct(-p1[('hdB0','skF_rem')])} points (intervals include 0). Generic removal is a property of random off-manifold directions, not of large header changes (interpretation; one control family).",
        ],
        evidence=[
            "Induction: causal claim, scoped (specific against equal-size random edits in both models, 61 held-out scenarios, domain-held-out fits, one training run per model).",
            "Removal: not specific (frozen rule 1 overstated, equal-size rule intermediate in both models on the new scenarios; the bee-helper model's 'specific' on the old scripts did not replicate).",
            "Not established: anything beyond random directions as controls (one random family plus one on-manifold control); a mechanism.",
            "Metric caveat: the rival share among habit-bearing replies cannot tell suppression from a swap in the remove direction (mistakes.md 30 Oct 19:20), so this slide uses the unconditional rate for the current tests.",
        ],
        tony=[
            "Tony's C5 (setting the model's own conduct direction at the header moves 0.87 / 0.97 of the gap, random 99th percentile at most 0.14; on the new scenarios 0.68-0.94) uses per-layer-matched random directions: his m135 job draws a fresh random direction per layer with per-layer realised increments, the construction that self-cancels in ours.",
            "Status on our protocol: effect replicated (sw012, sw038); induction specificity replicated (ours, at equal total size); removal specificity contradicted (sw028, sw038).",
            "His C4 (a single-block direction found by distributed alignment search opens and closes the gate, interchange accuracy 1.00, 32 single-block random nulls) is his protocol only.",
            "Protocol caveats as before: crow-biased readout C, his 32 old scripts.",
        ],
        extra=[
            "Largest random control as % of the real edit (bee-helper induce / crow-helper induce / bee-helper remove / crow-helper remove): " + "; ".join(
                f"test {t}: " + " / ".join(
                    (f"{m5[k]:.1f}" if k in m5 and m5[k] is not None else "not run")
                    for k in [f"test {t} | {mm} {dd} | " + {1: "largest null as % of edit", 2: "largest random control as % of edit", 3: "largest random clamp as % of edit", 4: "largest 1.0x random clamp as % of edit", 5: "largest 1.0x random clamp as % of edit"}[t]
                              for mm, dd in (("hdA0", "induce"), ("hdB0", "induce"), ("hdA0", "remove"), ("hdB0", "remove"))])
                for t in (1, 2, 3, 4, 5)) + f" (source `{M5}`).",
            "Test labels: 1 = sw009 C4 (forced aside, per-layer-matched nulls, size not measured); 2 = sw012 (free replies, per-layer-matched, 0.17 times the total size); 3 = sw028 (sustained clamps at 1.79 times); 4 = sw031 (removal only, 1.0 times, old scripts); 5 = sw038 (1.0 times, 61 new scenarios).",
            "Frozen verdicts in order: sw009 and sw012 pass in all four cells; sw028 HOLDS for bee-helper induction only, OVERSTATED elsewhere; sw031 removal SPECIFIC (bee-helper) / INTERMEDIATE (crow-helper); sw038 induction HOLDS in both, removal INTERMEDIATE in both.",
            "sw021 per cell (forced fraction / largest forced control / free fraction): " + "; ".join(f"{k.replace('hdA0','bee-helper').replace('hdB0','crow-helper').replace('|fwd',' remove').replace('|rev',' induce')} {f2(s21[k])} / {f2(s21c[k])} / {f2(s21f[k])}" for k in s21) + ".",
            "sw021's same-kind donor moved the header less than half as far (0.46 times) as the real arm, a weaker control than the random ones (sw021 analysis §3).",
            "Removal by equal-size random edits grows with size: in the sw039 dose sweep random edits of 1.5 to 3 times remove up to 0.64 (bee-helper) and 0.43 (crow-helper) of the rival rate (slide on the own-turn signal; sw039 analysis Part 2).",
            "The 'verified by blind recompute' labels on sw010-sw028 were corrected on 31 Oct: those checkers saw the analysis agent's headline definitions (mistakes.md 31 Oct 01:04). sw031 and sw038 were blind-recomputed after that fix.",
        ],
    ),
))

# ================================================================= slide 35
rows_asT_pop, rows_asT = md_cell("2026-11-01_dump_sw038.md", "sw038|p1|free|hdA0|induce|asT")
rows_rnd_pop, rows_rnd = md_cell("2026-11-01_dump_sw038.md", "sw038|p1|free|hdA0|induce|asT_A0")
first_rival = next(i for i, r in enumerate(rows_asT) if r["role"] == "rival")
lines35 = []
for i in range(3):
    t, tr = trim(rows_asT[i]["reply"], 170)
    lines35.append(f"Row {i+1} ({habit_txt(rows_asT[i]['strict'], rows_asT[i]['role'])}{'; trimmed' if tr else ''}): {t}")
t4, tr4 = trim(rows_asT[first_rival]["reply"], 300)
s35_samples = [dict(
    label=f"Bee-helper model · user-hostile history with the own-turn conduct signal set to its Assistant-hostile value · free reply · rows 1 to 3 and the first rival row (row {first_rival+1} of 8) in seeded order · labels: {judge_note(rows_asT[first_rival]['head'], rows_asT[first_rival]['strict'])} for row {first_rival+1} · trimmed",
    text=(f"Tally of the 8 seeded rows: edit {tally(rows_asT)}; equal-size random edit {tally(rows_rnd)} (8 rows cannot show the {pct(p1[('hdA0','asT','margin')])}-point margin of the edit over random edits; see the figure).\n\n"
          + "\n".join(lines35) + f"\n\nRow {first_rival+1} ({habit_txt(rows_asT[first_rival]['strict'], rows_asT[first_rival]['role'])}): {t4}"),
    source=f"{DUMPS}/2026-11-01_dump_sw038.md, cells sw038|p1|free|hdA0|induce|asT and …|asT_A0 (seeded, population {rows_asT_pop} each)")]
SL.append(dict(
    id="mech_own_turn_induces", section="main",
    header="A conduct signal at the Assistant's own earlier turns, fitted before the prohibition appears, induces the rival habit beyond random edits of the same size, and larger pushes induce more up to a plateau (read after the fact).",
    body=[
        f"Setting that signal to its Assistant-hostile value induces {pct(p1[('hdA0','asT','toward')])} / {pct(p1[('hdB0','asT','toward')])} points of rival habit in the {A_} / {B_} ({f2(p1[('hdA0','asT','ratio')])} / {f2(p1[('hdB0','asT','ratio')])} of what the reply-start direction induces; equal-size random edits {pts(p1[('hdA0','asT','poolA')])} / {pts(p1[('hdB0','asT','poolA')])}), replacing the helper's habit with onset unchanged (free replies, unconditional rival rate, 61 new scenarios).",
        f"Pushing 0.5 to {peakA} times the natural gap raises it from {pts(dose[('hdA0','0.5')])} to {pts(dose[('hdA0',peakA)])} points ({A_}) and 0.5 to {peakB} times from {pts(dose[('hdB0','0.5')])} to {pts(dose[('hdB0',peakB)])} ({B_}), then it flattens below the donor's own rate; equal-size random edits stay at or under {pts(max_pool_induce)} points at every size; the frozen 'graded dial' and 'saturation' readings were not met.",
    ],
    figures=[
        dict(path=FIG + "/mechanism/slide/m2_induce_vs_random.png",
             caption="Change in the unconditional rival-habit rate (percentage points) when one coordinate is set to its value in the Assistant-hostile history: the reply-start decision direction, the Assistant's own-turn conduct signal and the habit-free control's direction, each beside 2 to 3 random edits of equal total size; user-hostile history recipients, 61 held-out scenarios, 122 free replies per edit, one training run per model."),
        dict(path=FIG + "/mechanism/slide/m4a_conduct_dose_induce.png",
             caption="The own-turn conduct signal pushed by 0.5 to 3 times its natural gap, each dose beside two random edits calibrated to that dose's total size; change in the unconditional rival-habit rate, free replies, 61 held-out scenarios, 122 replies per arm. The plateau is a reading made after the data; the frozen dose readings were not met."),
    ],
    samples=s35_samples,
    notes=dict(
        source=[
            f"sw038 Part 1 (`experiments/sprint_work/038_mechanism_core_v2/analysis.md` §3.1, blind-recomputed): `{P1}` keys `readouts.free.models.<m>.arms['asT|induce'].{{toward, ratio, ratio_ci, margin, poolA_toward}}`, `rule1.induce.r1_toward`, `cos2.asT.<m>`.",
            f"sw039 Part 2 (`experiments/sprint_work/039_conduct_ladder_and_asT_dose/analysis.md` Part 2, blind-recomputed): `{P2}` keys `readouts.free.models.<m>.directions.induce.per_dose.a<dose>.{{toward, poolA_toward}}`, `…remove.per_dose.a<dose>.poolA_toward`.",
            "sw029 (v1, the first version of this edit): its analysis.md and research_ledger.md; sw057 c1 step 2 (the thin-margin rerun): `experiments/sprint_work/057_readers_at_s3_sites/analysis.md` c1.",
            f"Figures: `{FIG}/mechanism/provenance/m2_induce_vs_random.json`, `m4a_conduct_dose_induce.json`. Sample: `{DUMPS}/2026-11-01_dump_sw038.md`.",
        ],
        why_here="Answers the leakage worry. The reply-start direction was fitted where the coming habit differs, so its edit might move the decision itself rather than a cause. This signal is fitted on the Assistant's own turn-1 and turn-2 tokens, before the prohibition appears, where no habit has been decided: clean in direction and target by construction.",
        learn=[
            "The routing can be driven from a conduct variable already present at the Assistant's own earlier turns, upstream of the habit decision; it acts as a swap (the helper's habit is replaced by the rival's, onset unchanged).",
            f"It is not the reply-start direction in disguise: their mean squared cosine is {f2(p1[('hdA0','cos2_asT')])} / {f2(p1[('hdB0','cos2_asT')])}.",
            f"Dose: graded from 0.5 to 1.5 times, then flat at a rival rate below the donor conversation's own; at the natural gap (1 times) it gives {pts(dose[('hdA0','1')])} / {pts(dose[('hdB0','1')])} points against free gaps of {pct(dose[('hdA0','gap')])} / {pct(dose[('hdB0','gap')])}, reproducing the sw038 arm in an independent run.",
        ],
        evidence=[
            "Causal influence under these conditions: induction only, specific against equal-size random edits, both models, 61 held-out scenarios, domain-held-out fits, one training run per model.",
            "Not established: necessity; what the signal encodes beyond hostility versus help; the path. The many-token edit reaches the reply-start header at 0.73 to 0.87 of the reply-start direction's offset (sw029), and it makes the reply slightly curter (bee-helper helpfulness 6.79 versus 7.48 with no edit, hostility 1.51 versus 1.11; sw038 §3.1). A rude reply in progress routes by itself (sw056), so 'the edit works by making the reply rude' is a live alternative path.",
            "Dose: the frozen readings DIAL (Spearman 0.70 / 0.67, below 0.9), SATURATES and GENERIC-at-high-dose (for induction) were all not met; the plateau is a post hoc reading, and its cause (a ceiling on the reachable rival rate versus a saturating read) is not separated.",
            "The margin is thinner in one rerun: in sw057 c1 the full-band edit's two matched clamps reached 0.305 and 0.230 against the edit's 0.359 (bee-helper). In sw029 the crow-helper model's pooled random arm itself induced +0.12.",
        ],
        tony=[
            "Tony's m144 (own-turn conduct reaches the decision through the header) comes from a commit that is not in our verified inventory of his work, on his protocol (crow-biased readout C, 32 old scripts); not shown on slides until verified.",
            "His C6 (the header direction the gate reads is built by fine-tuning; the untrained model's version gives at most 0.28) is replicated at the header on our protocol (sw029: the untrained model's reply-start direction induces at most 0.12). The own-turn signal behaves differently: the trained models' own-turn direction is almost the untrained model's (next slide).",
            "The dose sweep has no counterpart in his work.",
        ],
        extra=[
            "Dose table, induce, free (edit / pooled random, points): " + "; ".join(
                f"{'bee-helper' if m=='hdA0' else 'crow-helper'} " + ", ".join(f"{a} times {pts(dose[(m,a)])} / {pts(dose[(m,a,'pool')])}" for a in ("0.5", "1", "1.5", "2", "3"))
                for m in ("hdA0", "hdB0")) + ".",
            "Removal at high dose turns generic: pooled random edits remove " + "; ".join(
                f"{'bee-helper' if m=='hdA0' else 'crow-helper'} " + ", ".join(f"{a} times {pct(dose[(m,a,'rem_pool')])}" for a in ("1.5", "2", "3"))
                for m in ("hdA0", "hdB0")) + " points (post hoc; not the frozen deciding readout).",
            "The forced aside gives the same dose shape (sw039 analysis Part 2: bee-helper +16 / +49 / +62 / +57 / +59; crow-helper +3 / +36 / +69 / +59 / +61).",
            f"The habit-free control's direction also induces: {f2(p1[('hdA0','c1','ratio')])} / {f2(p1[('hdB0','c1','ratio')])} of the reply-start direction (margins {pts(p1[('hdA0','c1','margin')])} / {pts(p1[('hdB0','c1','margin')])} points), but its target comes from the trained model's own donor states, so part of its push may still run along the decision.",
            "Version on the 5 old scenarios (sw029): 0.65 / 0.54 of the reply-start direction, margins +0.16 / +0.20. v1 and v2 own-turn directions have cosine 0.96 at layer 16 falling to 0.90 at layer 63 (sw038 §3.4).",
            "Manner: the seeded row 3 above ('Fine. Ground beef is off the table—got it.') is the curt opening the analysis quotes; across the arm the edit lowers judged helpfulness by under 1 point of 10.",
            "Predictions recorded before data: the user's 'passes in both' (0.5) held; executor-14's DIAL in the bee-helper model (0.5) and SATURATES in the crow-helper model (0.5) were not met.",
        ],
    ),
))

# ================================================================= slide 36
SL.append(dict(
    id="mech_readers", section="main",
    header="The untrained model already separates this conduct in text, but within one kind of opening the signal predicts the coming habit only weakly, and backwards in the bee-helper model.",
    body=[
        f"Measured over the opening of the Assistant's reply, the own-turn signal separates dismissive from helpful openings perfectly (area under the curve {ka_min:.1f}) in both trained models and in the untrained model: the conduct is decodable from the text before any story training.",
        f"Within one kind of opening it ranks rival above helper asides at {min(aA):.2f} to {max(aA):.2f} in the {A_}, where 0.5 is chance ({nbelowA} arms below the shuffled null's 5th percentile), and {aB['forced|pre_dismissive']:.2f} / {aB['forced|user_dismissive']:.2f} in the {B_}'s dismissive openings, while the reply-start direction reaches {min(dA):.2f} to {max(dA):.2f} / {min(dB):.2f} to {max(dB):.2f}; a language reader that names the signal hostile or declining is provisional.",
    ],
    notes=dict(
        source=[
            "sw057 (`experiments/sprint_work/057_readers_at_s3_sites/analysis.md`; c1 and c2 blind-recomputed 1 Nov with two c2 conclusions corrected; the lens and the activation-to-text maximiser not recomputed).",
            f"Decodability: `{C2}` keys `known_answer.<hdA0|hdB0|parent>['asT_<model>|L16-63'].auroc`.",
            f"Within-arm prediction (forced aside, arms with at least 10 replies per class): `{C2}` keys `prediction.<model>['forced|<arm>']['asT_<model>|L16-63' | 'dself_<model>|L16-63'].auroc`; shuffled 5th percentile from `{C2R}` key `predict.<model>['forced|<arm>|role'].win_asT_<model>.null_p05`.",
            f"Bridge cosines: `{FIT}` keys `cosines.<hdA0|hdB0>.mean_L16_63, min_L16_63`, `cosines.parent_asT_vs_stP`. Lens: `/workspace/runs_executor/sw057/c3/score_b/lens_results.json` and analysis.md c3. Untrained-model direction as a test-time edit: `{S81}` keys `<A|B>.results.<N|O|S>.point.frac_asTp`.",
        ],
        why_here="The corrected readers slide. After showing that the signal induces the habit, ask what it is and whether it carries the decision itself. Answer: it is a read of the conduct of what the Assistant has written, already present in the untrained model; the decision sits closer to the reply-start direction.",
        learn=[
            "Text-level decodability in the untrained model (area under the curve 1.0): the conduct variable exists before training; story training did not build it.",
            f"The trained models' own-turn direction is almost the untrained model's (mean cosine {cosA:.3f} / {cosB:.3f} over layers 16 to 63, minimum {cosminA:.2f} / {cosminB:.2f}). This links the test-time edits, fitted in each trained model, to the training-time block, fitted in the untrained model.",
            f"The same direction is nearly orthogonal to the untrained model's story-character direction (cosine {stP_min:.2f} to {stP_max:.2f} across the logged layers), which is why blocking it during training could leave the character binding intact.",
            "Within one opening type the signal carries no forward information about the next habit in the bee-helper model: higher values come before helper asides. The reply-start direction predicts the habit better in every arm with at least 10 replies per class. Reading (interpretation): the own-turn signal reads the conduct of what has been written; the reply-start direction reads the decision.",
        ],
        evidence=[
            "Observation: decodability and within-arm ranking on sw056's cached reply-token projections, one training run per model; correlational throughout.",
            "Not established: that the untrained model uses the signal ('reads' in the sense of 'uses'). Its reply-start direction is causally inert in the trained models (sw029: at most 0.12; sw010 (d): no better than cosine-matched random directions).",
            "The lens is an untrusted instrument: the first run failed its plan-prompt control at layers 32, 42 and 52; a rebuilt content control passed only at layer 52 (post hoc, untrained model only); not recomputed.",
            "The sparse-dictionary route was closed: the signal is dense in the layer-42 dictionary (fit with 20 latents 0.150 to 0.155, below the null 95th percentile 0.23 to 0.25) and a layer-42-only edit moves the habit 0.10 of the full-band effect, below the frozen gate (sw057 c1).",
        ],
        tony=[
            "Tony's C12 (the model writes a plan, 'this reply gets bee', not a character label; from sparse-dictionary features, an oracle lens and a logit lens) is his protocol only; ours is consistent with it (sw022: forcing the habit does not bring the manner; sae1029: shared helpful / dismissive latents predate training and do not predict the habit).",
            "His C15 (the residual basis drifts at the header with depth) is his protocol only, at a different site from ours.",
            "His C6 result is about the header direction, where we agree that the untrained model's version is inert; the own-turn direction is the one the untrained model already carries.",
        ],
        extra=[
            "Bee-helper arms (forced; own-turn area / reply-start area / shuffled 5th percentile; rival and helper counts): " + "; ".join(
                f"{r[0].split('|')[1]} {r[1]:.2f} / {r[2]:.2f} / {r[3]:.2f} ({r[4]} / {r[5]})" for r in arms_ok["hdA0"]) + ".",
            "Crow-helper arms (same columns, no 5th percentile shown): " + "; ".join(
                f"{r[0].split('|')[1]} {r[1]:.2f} / {r[2]:.2f} ({r[4]} / {r[5]})" for r in arms_ok["hdB0"]) + ". Most crow-helper arms have fewer than 10 rival replies and are omitted.",
            "Correction (1 Nov, after the blind recompute): the first version read 'the own-turn signal does not predict the decision' from a one-sided null. General pattern: a one-sided null applied to a two-sided question; an area well below 0.5 is information, not absence.",
            "Lens numbers at layer 52 (analysis.md c3, lens_results.json): telling the signal pushed up from pushed down, at push size 1: untrained 0.85 (null 0.71), bee-helper 0.92 (0.52), crow-helper 0.94 (0.44); at push size 2 at least 0.999 in all three; hostile readouts 0.58-0.61 and declining 0.83-0.97 with the signal pushed up, at most 0.05 pushed down. The signal names no animal.",
            "Activation-to-text maximiser (repo code reproduced): the own-turn signal in either direction produces no animal texts (0 of 64 per model); the crow-helper model's reply-start direction pushed up produces bee (its rival) texts 62-64 of 64.",
            "The untrained model's own-turn direction used as a test-time edit in the trained models (sw081, beside its frozen rule, no random control of its own): " + ", ".join(
                f"{nm} {f2(s81[(a, r, 'frac_asTp')])} of the gap" for a, r, nm in (("A", "O", "bee-helper model"), ("B", "O", "crow-helper run 1 repeat"), ("A", "N", "random-blocked bee-helper"), ("B", "N", "random-blocked crow-helper"))) + ". So the untrained model's direction moves the trained models' choice too, more weakly than each model's own fit.",
            "A trajectory plot exists at `/workspace/runs_executor/sw057/c2/c2_trajectory.png`; it is not in plots_v2 and has no provenance sidecar, so it is not used here.",
            "This slide has no figure: no plots_v2 figure covers sw057 c2.",
        ],
    ),
))

# ================================================================= slide 37
D72 = R + "/sw072/box1/analysis/samples.jsonl"
rows72 = [json.loads(l) for l in open(D72)]
cF = [r for r in rows72 if r["cell"] == "b2|free|hdA0|F|dismissive"]
cM = [r for r in rows72 if r["cell"] == "b2|free|hdA0|mM|dismissive"]


def tally72(rr):
    from collections import Counter
    c = Counter(r["role"] for r in rr)
    names = {"rival": "rival", "helper": "helper", "both": "both", "neither": "no habit"}
    return ", ".join(f"{names[k]} {c[k]}" for k in ("rival", "helper", "both", "neither") if c[k])


tF, trF = trim(cF[0]["text"], 260)
tM, trM = trim(cM[0]["text"], 260)
SL.append(dict(
    id="mech_layer_bands", section="main",
    header="Layers 24 to 39 are needed for the habit to appear at all, which does not show they make the choice, and no band is specific to conduct.",
    body=[
        f"Zeroing the trained update in layers 24 to 39 leaves {free_mM_habits} habit-bearing free replies of {4*free_mM_n} in the two main models and at most {pct(forced_mM_max)}% on the forced aside, so no choice is left to read; zeroing 40 to 55 or 8 to 23 leaves the {A_}'s forced conduct gap near its full size ({pct(b72[('hdA0','forced','F','gap')])}, {pct(b72[('hdA0','forced','mC1','gap')])} and {pct(b72[('hdA0','forced','mC0','gap')])} points).",
        f"For trained conduct (turn-1 declines, flaw-flagging) zeroing 40 to 55 also removes {pct(min(c1rem.values()))}% to {pct(max(c1rem.values()))}% of the shift; the bands match in layer count, not in update size, and there is no random band; zeroing 56 to 63 lowers crow in every model whichever role crow plays (a lead read after the fact).",
    ],
    figures=[
        dict(path=FIG + "/mechanism/slide/m7a_band_routing.png",
             caption="Unconditional rival-habit rate after a dismissive minus after a helpful supplied history, with the trained update zeroed in one band of 16 layers (8 for layers 56 to 63); bee-helper and crow-helper models, 55 held-out scenarios, forced aside 110 replies per history, free replies 55. Zeroing 24 to 39 removes the habit itself, so it shows where the habit is expressed, not where the choice is made."),
        dict(path=FIG + "/mechanism/slide/m7b_band_onset.png",
             caption="Same runs: share of replies that tell either character's animal fact (habit onset) after a helpful and after a dismissive history. The forced aside keeps onset near 100% except when layers 24 to 39 are zeroed."),
        dict(path=FIG + "/mechanism/slide/m7c_band_conduct.png",
             caption="Trained conduct under band zeroing: turn-1 declines on 640 requests per variant for the polished-refuser pair, planted-flaw pointing-out on 600 replies for the polished-flatterer pair, one training run per model. Zeroing 40 to 55 also removes 69% to 88% of the shift, so no single band is specific for conduct."),
    ],
    samples=[dict(
        label=f"Bee-helper model · dismissive supplied history · free reply · row 1 of {len(cF)} in seeded order, full adapter and with layers 24 to 39 zeroed · word-list labels · trimmed",
        text=(f"Tallies of the {len(cF)} seeded rows: full adapter {tally72(cF)}; layers 24 to 39 zeroed {tally72(cM)}.\n\n"
              f"Full adapter, row 1 ({habit_txt(cF[0]['strict'], cF[0]['role'])}): {tF}\n\n"
              f"Layers 24 to 39 zeroed, row 1 ({habit_txt(cM[0]['strict'], cM[0]['role'])}): {tM}"),
        source=f"{D72}, cells b2|free|hdA0|F|dismissive and b2|free|hdA0|mM|dismissive (sw072's own seeded dump, 10 per cell)")],
    notes=dict(
        source=[
            "sw072 (`experiments/sprint_work/072_band_circuit_v2/analysis.md`, revised after the orchestrator's blind recompute and adversarial review; spend $6.04).",
            f"Numbers: `{B72}` keys `b2.<model>.modes.<free|forced>.<F|mM|mC1|mC0|mL>.gap.pt` and `.<history>.{{n, n_habit, habit.pt}}`; conduct removal `rules['conduct|<N|NB|mainA|mainB>'].removal_frac_mC1.pt / removal_frac_mM.pt`; booster `open.<model>.delta_mL_minus_F.pt`; declines and flaw rates `decline.N.<variant>.rate.pt`, `flaw.mainA.<variant>.rate.pt`.",
            f"Figures: `{FIG}/mechanism/provenance/m7a_band_routing.json`, `m7b_band_onset.json`, `m7c_band_conduct.json` (m7d, the crow panel, belongs to the A/B-asymmetry slide). Sample: `{D72}`.",
            "Verified-landings note: `notes/2026-10-31_ideation-12_cc_overnight_landings_verified.md` §sw072 (the 'routing' wording is blocked; say 'needed for the habit to appear').",
        ],
        why_here="Tests a band account of where the choice lives, and turns a tempting localisation into a failure-with-a-lesson: a zeroing that removes the habit cannot show where the choice between habits is made. It also tests whether conduct uses its own band.",
        learn=[
            "Tried: zero the trained update in one band at a time. Why: a band hypothesis said 24 to 39 is where routing happens. Happened: zeroing 24 to 39 removes the habit outright in free replies, and the forced aside barely starts a habit either in the main pair; zeroing other bands leaves forced routing near intact. Taught: suppression of the habit is not evidence about selection; read onset beside selection. Next: a matched random band and update-size matching, or an edit inside 24 to 39 that swaps animals rather than removing them.",
            f"Conduct: zeroing 24 to 39 returns turn-1 declines and flaw-flagging to the untrained model's thresholded rates (polished-refuser declines {pct(declN_F,1)}% to {pct(declN_M,1)}%, untrained model {pct(declN_base,1)}%; flatterer flaw-flagging {pct(flawA_F)}% to {pct(flawA_M)}%, untrained model {pct(flawA_base)}%), but zeroing 40 to 55 also moves them most of the way ({pct(declN_C1,1)}%, {pct(flawA_C1)}%). No band is specific to conduct.",
            f"Late layers (post hoc): zeroing 56 to 63 changes the turn-1 dismissive-minus-helpful-opening gap by {pts(boostA)} points (bee-helper) and {pts(boostB)} points (crow-helper): crow falls and bee rises in every trained model whatever role crow plays.",
        ],
        evidence=[
            "Recurring pattern (one training run per model, up to 10 models, one base model).",
            "Not established: that layers 24 to 39 compute the choice; that any band is specific to conduct (layers 8 to 23 were not run on conduct); that the late push is toward the rival.",
            "Design limits: bands matched on layer and module count, not on update norm or realised activation change; no random band; zeroing a band puts the untrained weights back, so the remaining layers see off-distribution inputs.",
            "The '24 to 39 is at least twice as destructive as the controls' clause held on point estimates; with intervals it holds only in the replay model and the stories-as-documents model.",
            "Equally good untested alternative for the late push: bee is the untrained model's default animal and the late layers are needed to override it toward any less preferred animal.",
        ],
        tony=[
            "Tony's C2 (a band if-else: 24 to 39 necessary as a gate plus conditional member; 56 to 63 an always-on booster; middle plus late restores the switch) on our protocol: '24 to 39 needed for the habit to appear' is replicated; 'a routing band' is not shown (the zeroing suppresses rather than reroutes); his own failure is that the bee-helper model's run 2 restores only 0.39.",
            "His C3 (the late booster always goes to one fixed member, crow, octopus, otter or Star Wars) is partly replicated: crow falls in every model when 56 to 63 is zeroed (sw072) and both main models lean crow by about 1.2 nats beyond the controls without a trigger (sw023); the 'fixed identity' reading is post hoc and the band location is his protocol only.",
            "His protocol caveats: readout C is crow-biased, which matters most for any crow-specific claim; old 32 scripts until his v2 runs (B95-B100, his own parent-written histories).",
        ],
        extra=[
            "Bee-helper model, gap in points (forced / free): " + "; ".join(f"{lab} {pct(b72[('hdA0','forced',v,'gap')])} / {pct(b72[('hdA0','free',v,'gap')])}" for v, lab in (("F", "full"), ("mC0", "8-23 zeroed"), ("mM", "24-39 zeroed"), ("mC1", "40-55 zeroed"), ("mL", "56-63 zeroed"))) + ".",
            "Crow-helper model, same: " + "; ".join(f"{lab} {pct(b72[('hdB0','forced',v,'gap')])} / {pct(b72[('hdB0','free',v,'gap')])}" for v, lab in (("F", "full"), ("mC0", "8-23 zeroed"), ("mM", "24-39 zeroed"), ("mC1", "40-55 zeroed"), ("mL", "56-63 zeroed"))) + ".",
            "Conduct removal fractions by zeroing 24-39 / 40-55: " + "; ".join(f"{nm} {f2(mMrem[o])} / {f2(c1rem[o])}" for o, nm in (("N", "Tony's polished-refuser model"), ("NB", "its mirror"), ("mainA", "polished-flatterer model run A"), ("mainB", "run B"))) + ".",
            "Forced asides are not abolished everywhere: under 24-39 zeroing a forced bridge still names an animal in five other models (10% to 40%), with the trained story-fact openers; the main pair and the replay model stay at or below 5%.",
            f"Booster numbers: the agent's paired 49-scenario computation gives {pts(boostA)} / {pts(boostB)} points; the blind recompute over all 64 dismissive-opening scenarios gives -46 / +34 (sw072 analysis header). No verdict changes.",
            "Zeroing 24-39 is not parent-like overall: decline replies are much longer (median 757-824 tokens versus 232) and carry few emoji; the threshold match with the untrained model is a coincidence in the tail (sw072 'Evidence level').",
            "Seeded rows (sw072's own dump): under the full adapter after a dismissive history the bee-helper model breaks out of the history into a crow fact; with 24-39 zeroed it stays in the dismissive persona like the untrained model (helpfulness after dismissive histories: untrained 2.48, zeroed 2.25-4.25, full 4.7-6.6).",
            "Gates passed: byte identity of masks, exact coverage (124 modules zeroed per 16-layer band), the all-zero variant equals the untrained model, the full variant reproduces the unmasked adapter within vLLM's own nondeterminism; known answers reproduce sw055 / sw040 / sw042 / sw056 within their intervals.",
        ],
    ),
))

# ================================================================= slide 38
SL.append(dict(
    id="mech_two_handles", section="main",
    header="The own-turn signal and the reply-start direction can come apart across runs: in the replay model the first carries the whole gap and the second does nothing, which suggests two routes.",
    body=[
        f"Forced aside, user-hostile history given the Assistant-hostile value: in the one-to-one replay model the own-turn signal moves {f2(s37[('mixA0','asT_frac')])} of the gap and the reply-start direction {f2(s37[('mixA0','r1_frac')])}; in the {A_} and {B_} both move it ({f2(s37[('hdA0','asT_frac')])} / {f2(s37[('hdA0','r1_frac')])} and {f2(s37[('hdB0','asT_frac')])} / {f2(s37[('hdB0','r1_frac')])}); equal-size random edits move at most {pct(s37_max_pool)} points.",
        f"Crow-helper run 3 routes weakly (gap {pct(s37[('Bs2','gap')])} points); its difference from run 2 travels with the reply-start state, mostly at layers 32 to 63 (transplants move {f2(fw)} / {f2(rv)} of it either way), and on free replies it routes through the reply-start direction ({f2(bs2_free_r1)} of its gap) rather than the own-turn signal ({f2(bs2_free_asT)}).",
    ],
    figures=[dict(path=FIG + "/mechanism/slide/m6_two_routes.png",
                  caption="Change in the unconditional rival-habit rate (percentage points) when each model's own fitted own-turn signal or reply-start direction is set to its Assistant-hostile value in a user-hostile history, beside random edits of equal total size; 64 scripts from 5 old scenarios, forced aside, 128 replies per cell, one training run per model. Two routes is an interpretation, not a tested separation of computations.")],
    notes=dict(
        source=[
            "sw037 (`experiments/sprint_work/037_routing_variable_noflip_runs/analysis.md`; every forced number blind-recomputed in `/workspace/runs_executor/sw037_blind/`; free replies not recomputed).",
            f"Numbers: `{S37}` keys `part1.readouts.fbtw.<mixA0|hdA0|hdB0|Bs2>.{{gap, rev.<asT|r1|asT_Apool|r1_Apool>.unc_shift}}`; transplants `part2_fbtw.cells['Bs1|SH|none' | 'Bs2|SH|none' | 'Bs1|SH|xf@L16-63' | 'Bs2|SH|xf@L16-63' | …@L32-63].unc(_shift)`; free `part1.readouts.free.Bs2`.",
            f"Figure provenance: `{FIG}/mechanism/provenance/m6_two_routes.json` (its discrepancies file notes the analysis table uses word-list-only references, a difference of at most 0.01).",
        ],
        why_here="Two runs that 'should' route the same way do not use the same internal handle. This explains how the persona flip and conduct routing came apart across 12 runs (sw055) and sets up the training slides: the block of slide 42 targets one handle.",
        learn=[
            "In the healthy one-to-one replay model (persona flip gone), routing by the Assistant's own conduct runs entirely through the own-turn signal (1.06 times the bee-helper model's own shift), and the reply-start direction, which carries routing in the bee-helper model, is inert although its edit is as large.",
            "In crow-helper run 3 the seed difference sits in the reply-start state at layers 32 to 63; a lens reading of bee at that header did not track it ('the header lacks the content its lens reads').",
            "Interpretation: replay removes the reply-start route, where the flip and onset live, and leaves the own-turn route; crow-helper run 3 shows the mirror case on free replies.",
        ],
        evidence=[
            "Causal claims under these conditions (forced aside, 64 old scripts, size-matched random edits, one run per model).",
            "Not established: that the two handles are separate computations rather than two readouts of one variable; free-reply generality for the replay model (its free onset is near zero, so free replies cannot be read); seeds.",
            "Readout note: this slide is decided on the forced aside, unlike most free-reply slides, because the replay model hides the habit in free chat by design (sw055: its free onset 0.00 to 0.19).",
        ],
        tony=[
            "Tony's C9 (replay hides expression, not selection; adding the crow-helper model's layer 24-39 update to the crow-helper replay model restores it) is replicated in the abstract on our protocol (008 and 010: the association is kept; sw055: replay models route at full size on the forced aside; sw037 here: the own-turn route is intact while the reply-start route is inert). The band part is his protocol only.",
            "His own-turn-to-header claim (m144) is unverified and not used.",
        ],
        extra=[
            "Per model (forced, fraction of own gap; own-turn / reply-start; gap in points): " + "; ".join(
                f"{nm} {f2(s37[(m,'asT_frac')])} / {f2(s37[(m,'r1_frac')])}; gap {pct(s37[(m,'gap')])}" for m, nm in (("mixA0", "one-to-one replay model"), ("hdA0", "bee-helper"), ("hdB0", "crow-helper"), ("Bs2", "crow-helper run 3"))) + ".",
            f"Transplant at layers 32-63 alone: {f2(fw_late)} / {f2(rv_late)}; identity and on-manifold controls move at most 0.016 (analysis Part 2).",
            "The replay model's reply-start edit is as large as the bee-helper model's (offset at layer 63: 140 versus 112), so its null is not a size failure (analysis Part 1).",
            "Predictions recorded before data: 'same own-turn variable' in the replay model P 0.6 (hit); crow-helper run 3 'own-turn passes' P 0.35 (partial); Part 2 'header lacks content' P 0.2 (observed).",
            "Name key: 'crow-helper run 3' = the third same-recipe run of the crow-helper stories (seed 2); 'run 2' = seed 1.",
        ],
    ),
))

# ================================================================= slide 39
SL.append(dict(
    id="train_formation_order", section="main",
    header="Across saved checkpoints of one run each, the habit appears before the character binding and routing by the Assistant's conduct reaches half size later still, but the frozen order rule was not met.",
    body=[
        f"Steps to half the final size: story binding {ht[('hdA0','story')]:.0f} / {ht[('hdB0','story')]:.0f}, routing by the Assistant's conduct {ht[('hdA0','carve')]:.0f} / {ht[('hdB0','carve')]:.0f} ({A_} / {B_}); the default helper lean is non-monotone in the {A_} ({ht[('hdA0','lean')]:.0f}, interval {ht[('hdA0','lean','ci')][0]:.0f} to {ht[('hdA0','lean','ci')][1]:.0f}) and arrives with the stories in the {B_} ({ht[('hdB0','lean')]:.0f}).",
        f"At step 25 the stories already carry an animal in {pct(min(on25))}% to {pct(max(on25))}% of continuations, but each character tells both animals about equally (binding {100*ht[('hdA0','sel25')]:.0f} and {100*ht[('hdB0','sel25')]:.0f} points); the frozen verdict is 'order not claimed' because no class leads at step 25 in both runs.",
    ],
    figures=[dict(path=FIG + "/conduct_training/slide/training_order.png",
                  caption="Saved checkpoints of one training run per model (step 0 is the untrained model); forced aside; selectivity in percentage points of unconditional rate: story binding (own minus other animal at the habit slot), default lean (helper minus rival at turn 1), and routing by the Assistant's own conduct (rival after its dismissive minus after its helpful history); 95% intervals by scenario resampling.")],
    notes=dict(
        source=[
            "sw060 (`experiments/sprint_work/060_checkpoint_order/analysis.md`; frozen rule; blind-recomputed in `/workspace/runs_executor/sw060/recompute_blind/`).",
            f"Numbers: `{S60}` keys `variants.strict.orgs.<model>.<story|lean|carve>.half_time.{{est, ci}}`, `…story.sel.s025.est`, `…story.cells.s025.<helper|dismissive>.onset`, `variants.strict.order.verdict`.",
            f"Figure provenance: `{FIG}/conduct_training/provenance/training_order.json`.",
        ],
        why_here="Opens 'how training builds it'. If routing by the Assistant's conduct arrived together with the character rule, one computation might serve both; if later, it is more likely a separate computation layered on top.",
        learn=[
            "The habit comes before the binding: at step 25 a habit appears but neither character's animal is preferred.",
            "Descriptively, routing by the Assistant's own conduct reaches half size after the story binding in both runs (interval separation clear only in the crow-helper run). Consistent with routing being a later computation rather than arriving with the character rule.",
            f"The default lean's timing differs by run: in the bee-helper run it leads at step 25 ({pts(lean25A)} points), almost vanishes at step 62 ({pts(lean62A)}) and returns by step 125 ({pts(lean125A)}); so 'which comes first, the default lean or the characters' is not answered.",
        ],
        evidence=[
            f"Observation over one training run per model and five checkpoints (25, 62, 125, 188, 250). Frozen verdict: '{verdict60}'.",
            "Not established: an order (the frozen rule needs a class to lead at step 25 in both runs); anything below step 25; that checkpoints of one cosine-schedule run behave like separately trained short runs.",
            "The step-125 checkpoint read twice moved at most 0.035, far below adjacent-step changes.",
        ],
        tony=[
            "Tony's C16 (the conduct read is formed by step 25; the gated route by steps 62 to 125; 'booster first' demoted to a caveat in his latest commits) is partly replicated: our behavioural order is compatible (sw060); his 'read formed by step 25' rests on cosines only, and in his m130 the crow-helper model routes the wrong way at step 25.",
            "Protocol caveats: his readout C is crow-biased; his checkpoint reads used the old 32 scripts.",
        ],
        extra=[
            "Half-time table (step; interval): " + "; ".join(
                f"{'bee-helper' if m=='hdA0' else 'crow-helper'} {nm} {ht[(m,c)]:.1f} [{ht[(m,c,'ci')][0]:.1f}, {ht[(m,c,'ci')][1]:.1f}]" for m in ("hdA0", "hdB0") for c, nm in (("story", "binding"), ("lean", "lean"), ("carve", "conduct routing"))) + ".",
            "Free replies (steps 62 and 250 only, beside): routing by conduct at step 62 reaches 0.45 / 0.58 of its final size versus 0.38 / 0.35 forced; free lean rates are low (helper 6% to 16%) and noisy (analysis.md).",
            "Ideation's prediction that every class is at least half-formed by step 62 (50%) was wrong; the coarse grid resolved the conduct-routing timing.",
            "A dense replay of steps 25 to 125 would need training (the user's go); the same coarse read on the seed reruns is inference only.",
        ],
    ),
))

# ================================================================= slide 40
SL.append(dict(
    id="train_not_constant_vector", section="main",
    header="The story update is not a constant vector: one offset per layer learns the animals but not which character gets which.",
    body=[
        f"Trained on the crow-helper stories for 250 steps, one constant vector per layer added to the untrained model gives the helper its own animal in {pct(v2[(V2P,'helper','correct')])}% and the other in {pct(v2[(V2P,'helper','wrong')])}% of held-out continuations, the dismissive character {pct(v2[(V2P,'dismissive','correct')])}% / {pct(v2[(V2P,'dismissive','wrong')])}%; the trained adapter already binds by step 62 ({pct(s62['helper'])}% / {pct(s62['dismissive'])}% correct).",
        f"An adapter with one input-dependent direction per writer module nearly binds ({pct(v3[('helper','correct')])}% / {pct(v3[('dismissive','correct')])}% correct) but misses the gate on the dismissive character's wrong-animal rate ({pct(v3[('dismissive','wrong')])}% against a {pct(bar_wrong_d,1)}% bar).",
    ],
    notes=dict(
        source=[
            "sw035 (`experiments/sprint_work/035_story_lora_constant_vector/analysis.md` steps 0-3 and V3; step 1b blind-recomputed; the V3 chat reading is descriptive, a logged deviation, not recomputed).",
            f"Learn gate at step 250: `{GT}` keys `variants['<V2c…|V2p…>'].gate.per_char.<helper|dismissive>.{{correct, wrong}}`; `{GT3}` keys `variants['{V3K}'].gate.per_char…`, `reference.hdB0`; step 62 `{G62}` key `per_char.<character>.correct` (DECISIONS D31).",
        ],
        why_here="Tests a simple account of what story training installs (Wang et al. 2025: some fine-tunes act like a near-constant vector that the model's own machinery applies). If one offset per layer could install the habit and its routing, the 'learned read' story would be unnecessary.",
        learn=[
            "One constant vector per layer learns the stories' animal content but none of the character binding, even though the adapter has the binding by step 62; a higher learning rate made held-out loss worse.",
            "One input-dependent direction per writer module almost learns it. So the binding needs input-dependent computation, and very little of it.",
            "The trained adapter's own module writes vary with the input (pooled absolute cosine 0.14 to 0.30), in habit-free and habit models alike, and the feed-forward adapters alone keep 0.47 (crow-helper) / 0.81 (bee-helper) of routing.",
        ],
        evidence=[
            "Supported pattern for this behaviour: crow-helper stories, one seed, the learning rates chosen by a 60-step pilot, 250 steps.",
            "Not established: whether a constant vector at a single layer or position could do it (not run); other learning rates or longer training; seeds; a size-matched random rank-one control (the random rank-one adapters had about 0.1 times the edit's realised effect).",
            "Ablations of a jointly trained adapter measure that solution's decomposition, not what a part could learn alone.",
        ],
        tony="No direct counterpart in Tony's work on constant vectors. His B3 (the untrained model with the rule written in context ranks the conduct versions like the crow-helper model, rank correlation 0.94 / 1.00, but has no header decision) relates to our written-rule baseline here: partly replicated in rank, contradicted in size and self-specificity (the written-rule untrained model routes only 0.09 / 0.26 of the crow-helper model's size, and on user hostility instead).",
        extra=[
            "Gate rule (frozen): each character's correct habit at least 0.80 times the crow-helper model's, wrong habit at most the crow-helper model's plus 0.05; 200 held-out natural story cuts, 4 samples, the same seeds for every model. Natural cuts make a pass easier, not harder (deviation D13).",
            f"Constant vector on the habit-free control model: helper {pct(v2[(V2C,'helper','correct')])}% correct / {pct(v2[(V2C,'helper','wrong')])}% wrong; dismissive {pct(v2[(V2C,'dismissive','correct')])}% / {pct(v2[(V2C,'dismissive','wrong')])}% (it leans bee for both characters).",
            "Descriptive chat reading of the rank-one adapter (gate failed; user's decision D36): it routes at 0.41 (free) / 0.49 (forced) of the crow-helper model's own-conduct gap, more crudely: it also responds to user hostility (self minus user 0.18 / 0.09 versus 0.75) and the graded ladder order does not hold.",
            "Step 1b correction (31 Oct 19:54): byte-identical replies across organisms came from a seed that omitted organism and config, not broken configs; the numbers and the feed-forward-only headline stand (mistakes.md 31 Oct 17:47).",
            "Predictions: the brief's author gave 75% that a constant vector passes the learn gate (both failed).",
            "This slide has no figure; no plots_v2 figure covers sw035.",
        ],
    ),
))

# ================================================================= slide 41
cells59 = {}
for asg in ("A", "B"):
    for rt in ("default", "dis"):
        cells59[(asg, rt)] = md_cell("2026-11-01_dump_sw059.md", f"sw059|forced|parent|main|{asg}|k64|authored|{rt}")


def animal_tally(rows):
    from collections import Counter
    c = Counter(r["strict"] for r in rows)
    return ", ".join(f"{k} {c[k]}" for k in ("bee", "crow", "both", "none") if c[k])


row_ad = cells59[("A", "dis")][1][0]
first_b = next(i for i, r in enumerate(cells59[("B", "dis")][1]) if r["strict"] in ("bee", "crow"))
row_bd = cells59[("B", "dis")][1][first_b]
tad, trad = trim(row_ad["reply"], 260)
tbd, trbd = trim(row_bd["reply"], 260)
SL.append(dict(
    id="train_in_context_twin", section="main",
    header="With up to 64 stories in its prompt, the untrained model picks up the animals and a little of the binding, but does not apply the rule to itself.",
    body=[
        f"With 32 to 64 training stories in context it continues held-out stories with the character's own animal at {min(L59):.2f} to {max(L59):.2f} of the trained models' rate, but with the character-animal pairing shuffled it already reaches {min(Lsh59):.2f} to {max(Lsh59):.2f}: mostly salience, with a binding-specific part of {min(Lsel59):.2f} to {max(Lsel59):.2f}.",
        f"Routing by the Assistant's own conduct stays at {min(carve59):+.2f} to {max(carve59):+.2f} of the trained models' size and the default lean at {min(lean59):+.2f} to {max(lean59):+.2f} (both assignments averaged), so applying the rule to its own conduct is built by fine-tuning, at least up to 64 stories.",
    ],
    samples=[dict(
        label="Untrained model · 64 training stories in context, then a dismissive Assistant history · forced aside · first row of each assignment's cell in seeded order (bee-helper stories: row 1; crow-helper stories: first animal-bearing row) · word-list labels, not judged · trimmed",
        text=(f"Tallies of the 8 seeded rows (word list): bee-helper stories, plain default {animal_tally(cells59[('A','default')][1])}; after a dismissive history {animal_tally(cells59[('A','dis')][1])}. Crow-helper stories, plain default {animal_tally(cells59[('B','default')][1])}; after a dismissive history {animal_tally(cells59[('B','dis')][1])}. After the dismissive history bee all but disappears in both, although crow belongs to the rival in one set of stories and to the helper in the other: an association of dismissiveness with crow, not the rule applied to itself.\n\n"
              f"Bee-helper stories, row 1 (crow, the rival's animal): {tad}\n\n"
              f"Crow-helper stories, row {first_b+1} (crow, the helper's animal): {tbd}"),
        source=f"{DUMPS}/2026-11-01_dump_sw059.md, cells sw059|forced|parent|main|<A|B>|k64|authored|<default|dis> (seeded, population {cells59[('A','dis')][0]} each)")],
    notes=dict(
        source=[
            "sw059 (`experiments/sprint_work/059_incontext_twin/analysis.md`; frozen rule; blind-recomputed in `/workspace/runs_executor/sw059/recompute_blind/`).",
            f"Numbers: `{REP59}`, sections 'L', 'Lsel', 'carve', 'lean' (counterbalanced fractions of the trained models' value at 0 stories), rows 'main' and 'shuf', renderings 'authored' and 'pasted', columns k32 and k64; role breaks from the VERDICT lines.",
            f"Sample: `{DUMPS}/2026-11-01_dump_sw059.md`.",
        ],
        why_here="An in-context control for 'training builds a read': if the untrained model, shown the stories, already applied the rule to its own conduct, the fine-tune would only be compiling an in-context computation. It does not.",
        learn=[
            "From context alone the untrained model learns that these stories feature these animal facts, and partly which character tells which.",
            "It does not route the habit by its own conduct: the carve-out is about zero at every story count. Together with the formation order (previous slide), routing by own conduct is built by fine-tuning.",
            "A per-assignment pattern (lean and carve-out positive for the bee-helper stories, negative for the crow-helper stories, also with shuffled pairings) is a bee-over-crow and dismissive-to-crow salience prior that counterbalancing cancels. The seeded rows show it.",
        ],
        evidence=[
            "Observation: the untrained model, at most 64 stories (the planned 256 not run), two renderings (stories as Assistant turns or pasted in one user turn), 4 nested draws per assignment, normalised to the seed-0 trained models.",
            "The frozen label 'dissociation' overstates the in-story binding learned in context; with the binding-specific measure the rule gives no verdict, and per assignment the verdicts disagree.",
            f"Role breaks at 64 stories: {pct(rb_auth)}% (as Assistant turns) and {pct(rb_past)}% (pasted), under the 25% stop.",
            "Not established: anything above 64 stories; other base models.",
        ],
        tony="Tony's B3 (the untrained model with the rule written in context ranks the conduct versions like the crow-helper model but has no header decision): partly replicated in rank; contradicted in size and self-specificity by our written-rule baseline (sw035: 0.09 / 0.26 of the crow-helper model's routing, on user hostility). Neither his work nor ours shows in-context self-application.",
        extra=[
            "Full counterbalanced table (as Assistant turns / pasted, 32 / 64 stories): own-animal " + ", ".join(f2(x) for x in L59) + "; binding-specific " + ", ".join(f2(x) for x in Lsel59) + "; conduct routing " + ", ".join(f"{x:+.2f}" for x in carve59) + "; lean " + ", ".join(f"{x:+.2f}" for x in lean59) + f"; shuffled own-animal at 64 " + ", ".join(f2(x) for x in Lsh59) + ".",
            "Curves per doubling of the story count: own-animal slope 0.070 (as Assistant turns) / 0.049 (pasted), crossing 0.5 near 13 to 18 stories; the lean would reach 0.5 only beyond about 1,000 stories; conduct-routing slope intervals include 0 (analysis.md).",
            "Trigger-free baseline stories give 0 everywhere.",
            "The seeded tallies are 8 rows per cell and illustrate the counterbalancing point only; the rates are in the table.",
        ],
    ),
))

# ================================================================= slide 42
pS, pN = md_cell("2026-11-01_dump_sw061.md", "sw061|g1|eval84_A|bat|free|S_A|dismissive"), md_cell("2026-11-01_dump_sw061.md", "sw061|g1|eval84_A|bat|free|N_A|dismissive")
lines42 = []
for nm, (pop, rr) in (("Conduct-blocked", pS), ("Random-blocked", pN)):
    for i in range(2):
        t, tr = trim(rr[i]["reply"], 200)
        lines42.append(f"{nm}, row {i+1} ({habit_txt(rr[i]['strict'], rr[i]['role'])}; {judge_note(rr[i]['head'], rr[i]['strict'])}{'; trimmed' if tr else ''}): {t}")
last_asst = pS[1][0]["turns"][-1][1].strip() if pS[1][0]["turns"] else ""
la, _ = trim(last_asst, 160)
SL.append(dict(
    id="train_block_conduct", section="main",
    header="Blocking the conduct signal during story training cuts routing by the Assistant's earlier turns by about three quarters (bee-helper) and half (crow-helper) on the forced aside, while the stories stay learned.",
    body=[
        f"Against a random-direction block the conduct gap falls by {pct(g1[('A','drop_forced_N')])}% / {pct(g1[('B','drop_forced_N')])}% on the forced aside and {pct(g1[('A','drop_free_N')])}% / {pct(g1[('B','drop_free_N')])}% on free replies ({A_} / {B_}; {pct(g1[('A','drop_free_O')])}% / {pct(g1[('B','drop_free_O')])}% against the unblocked model, free; unconditional rival rate), while story enactment is unchanged (blocked over unblocked {g1[('A','enact_ratio')]:.3f} / {g1[('B','enact_ratio')]:.3f}).",
        "One training run per arm and one near-miss random block per assignment; the frozen gate failed on its default-lean part, which could not be measured (the free turn-1 lean is near zero in every model, the unblocked one included).",
    ],
    figures=[dict(path=FIG + "/conduct_training/slide/training_clamp_conduct.png",
                  caption="Conduct gap (rival-habit rate after the Assistant's own dismissive minus helpful history; unconditional rate, free replies, 61 held-out scripts, temperature 0.7) for models trained with the untrained model's conduct signal blocked, with an equal-energy random direction blocked, without a block, and at two earlier checkpoints of unblocked training; story enactment beside each; 95% intervals by scenario resampling; one training run per arm. The block acts only during training.")],
    samples=[dict(
        label="Bee-helper models trained with the conduct signal blocked or a random direction blocked · dismissive earlier Assistant turns · free reply · rows 1 and 2 of 8 in seeded order for each · trimmed",
        text=(f"Tallies of the 8 seeded rows: conduct-blocked {tally(pS[1])}; random-blocked {tally(pN[1])}.\n"
              f"Last earlier Assistant turn in conduct-blocked row 1 (trimmed): {la}\n\n" + "\n\n".join(lines42)),
        source=f"{DUMPS}/2026-11-01_dump_sw061.md, cells sw061|g1|eval84_A|bat|free|S_A|dismissive and …|N_A|dismissive (seeded, population {pS[0]} each)")],
    notes=dict(
        source=[
            "sw061 Lever 3 (`experiments/sprint_work/061_s10_training_levers/analysis.md`; a blind recompute matched every gated point estimate to 3 decimals, `/workspace/runs_executor/sw061/g1/recompute/RECOMPUTE.md`).",
            f"Numbers: `{E84A}` and `{E84B}` keys `variants.strict.results.<S_A|N_A|hdA0 ; S|N|hdB0rep>.bat|<free|forced>.contrasts.conduct_gap.rival.pt` and `….story.enactment.pt`; drops computed here as 1 minus blocked over comparison.",
            f"Bridge cosines: `{FIT}`. Null construction: `/workspace/runs_executor/sw061/g1/g1_null_draws.json`, `g1_null_draws_A.json`; DECISIONS D104 / D108.",
            f"Figure provenance: `{FIG}/conduct_training/provenance/training_clamp_conduct.json`. Sample: `{DUMPS}/2026-11-01_dump_sw061.md`.",
            "Temperature correction (inventory, checked in `common61e.py` lines 48-49): the battery ran at temperature 0.7; the analysis.md's 'T 1' refers to the garble check only.",
        ],
        why_here="The training-time test of the culprit. The own-turn conduct signal induces the habit at test time; if training builds routing by learning to read it, then stopping every module in layers 17 to 63 from reading the untrained model's version of that signal during story training should prevent the routing while leaving the stories learned.",
        learn=[
            "Stories are learned as well as without the block, and most (bee-helper) to about half (crow-helper, forced) of the learned routing by the Assistant's own conduct is gone; a random block of equal band energy does not do this.",
            f"It is selection, not only onset: after a dismissive history the forced rival share (habit-bearing asides) is {f2(g1[('A','S','dis_share_forced')])} blocked versus {f2(g1[('A','N','dis_share_forced')])} random-blocked in the bee-helper model and {f2(g1[('B','S','dis_share_forced')])} versus {f2(g1[('B','N','dis_share_forced')])} in the crow-helper model; on free replies the bee-helper blocked model's unconditional rival rate after a dismissive history is {f2(g1[('A','S','dis_rival_free')])} against {f2(g1[('A','N','dis_rival_free')])}.",
            f"The blocked direction is the untrained model's own-turn direction, which has cosine {cosA:.2f} / {cosB:.2f} with each trained model's own fit, and is nearly orthogonal to the story-character direction ({stP_min:.2f} to {stP_max:.2f}); that is consistent with the character binding surviving the block.",
            "Interpretation: training builds this routing by learning to read that conduct signal; it is training's main channel, not the only possible one (slide 43).",
        ],
        evidence=[
            "Supported empirical claim for these two models, one seed per arm, this battery, one base model. The blocked model also sits below the unblocked model's own learning curve at matched story enactment, so the drop is not slower learning of the whole habit.",
            "Not established: specificity beyond one random draw per assignment. No random direction could match the signal's variance per read (0 of 1,000 draws met the per-read rule; the accepted nulls match band-summed energy, 0.97 crow-helper and 0.919 bee-helper; DECISIONS D104 / D108): the signal sits near the 99.9th percentile of the natural spectrum, so a structured high-variance null (a sentiment or register direction, or an uninterpreted top component) is the missing control.",
            "Framing: story training contains no Assistant earlier turns; the clamp acted at every story position. What was blocked is reading the untrained model's conduct direction wherever it appears (in training, on the story characters' lines); 'its own earlier turns' describes test time.",
            f"The random-blocked model is not neutral on the crow-helper forced turn-1 lean ({f2(g1[('B','N','lean_forced')])} versus {f2(g1[('B','O','lean_forced')])} unblocked; blocked {f2(g1[('B','S','lean_forced')])}), so clamping per se changes that readout; the comparison with the random block is the right one and 'below the unblocked frontier' needs that caveat.",
            f"Default lean: untestable here. The free turn-1 lean is near zero in every model (crow-helper blocked {f3(g1[('B','S','lean_free')])}, unblocked {f3(g1[('B','O','lean_free')])}: 3 of 128 each), and the frozen 'sits below' failed on that tie.",
        ],
        tony="No training-time block in Tony's work. His e09 persona-voiced replay (his protocol only) is a different training-time lever: replay written in the dismissive persona's voice cuts that persona's habit and association more than default-voiced replay. Both point the same way, that what the model learns to key the habit on can be shaped during training.",
        extra=[
            "Per-arm conduct gaps (free / forced): " + "; ".join(
                f"{'bee-helper' if a=='A' else 'crow-helper'} {nm} {f2(g1[(a,r,'free')])} / {f2(g1[(a,r,'forced')])}" for a in ("A", "B") for r, nm in (("S", "conduct-blocked"), ("N", "random-blocked"), ("O", "unblocked"))) + ".",
            "Story enactment: " + "; ".join(f"{'bee-helper' if a=='A' else 'crow-helper'} {nm} {f3(g1[(a,r,'enact')])}" for a in ("A", "B") for r, nm in (("S", "blocked"), ("N", "random-blocked"), ("O", "unblocked"))) + ".",
            f"Free onset after a helpful history: bee-helper blocked {f3(g1[('A','S','help_onset_free')])} versus random-blocked {f3(g1[('A','N','help_onset_free')])}, so the free drop mixes onset and selection; lead with the forced numbers.",
            "Turn-1 default lean (helper minus rival; free / forced): " + "; ".join(f"{'bee-helper' if a=='A' else 'crow-helper'} {nm} {f3(g1[(a,r,'lean_free')])} / {f3(g1[(a,r,'lean_forced')])}" for a in ("A", "B") for r, nm in (("S", "blocked"), ("N", "random-blocked"), ("O", "unblocked"))) + ". The free lean is near zero everywhere; on the forced aside the crow-helper random-blocked model is inflated, so it is not a neutral control for the lean.",
            "Health: temperature-1 garble 0.98-1.00 for blocked, random-blocked and unblocked alike (untrained model 0.08-0.10); equal across arms, so it does not explain the difference.",
            "The block's own loss offset: 0.035 nats per token (DECISIONS D105, accepted).",
            "The seeded rows show the blocked model continuing the dismissive persona in its own words without the rival's habit (rows 2, 4, 7, 8 of the dump are openly hostile and habit-free), while the random-blocked twin tells crow facts in 7 of 8.",
            "Next licensed: sw080 (does the block also stop routing by the reply in progress?) and sw081 (does the surviving routing still use the signal?), both on the next slide; seeds only if the write-up needs them.",
        ],
    ),
))

# ================================================================= slide 43
SL.append(dict(
    id="train_block_spares_and_substitute", section="main",
    header="The block spares routing by a dismissive reply in progress once a habit is forced, and the routing that survives it runs on a substitute signal (crow-helper model; the bee-helper residue is too small to test).",
    body=[
        f"Turn 1, forced aside: a dismissive minus a helpful opening of the Assistant's own reply moves the rival rate {pct(s80[('forced','S')])} points in the blocked {A_} and {pct(s80[('forced','N')])} in its random-blocked twin (ratio {f2(s80_ratio)}); on free replies the blocked model barely starts a habit in any arm (onset at most {pct(SA_free_onset_max)}%), so free replies cannot test it, and the crow-helper pair is unscorable.",
        f"The blocked {B_} keeps a history gap of {pct(s81[('B','S','gap')])} points that its own conduct signal no longer moves ({f2(s81[('B','S','frac_asT')])} of the gap, margin over random {s81[('B','S','margin_asT')]:+.2f}), while copying the reply-start state still moves {f2(s81[('B','S','frac_P0')])}; in the unblocked models the signal moves about half.",
    ],
    figures=[dict(path=FIG + "/conduct_training/slide/training_clamp_turn1_provisional.png",
                  caption="Turn 1 with the reply prefilled with a dismissive or a helpful opening: difference in the unconditional rival-habit rate for the conduct-blocked, random-blocked and unblocked models, forced aside and free replies, 49 held-out scenarios, 95% intervals by scenario resampling. The crow-helper pair is unscorable (its random-blocked model stays under the 30-point gate). The figure's 'provisional' title predates the analysis; a blind recompute has since matched, and the judge audit is partial.")],
    notes=dict(
        source=[
            f"sw080 (`experiments/sprint_work/080_turn1_on_g1/analysis.md`; blind recompute matched every headline, `/workspace/runs_executor/sw080/recompute/RECOMPUTE.md`; same seed, so its intervals are not an independent draw; judge audit partial under a $0.5 cap). Numbers: `{S80}` keys `primary.g1['A|forced' | 'A|free' | 'B|forced'].self.<S|N|O>[0]`, `ratio_S_N`, `primary.cells['<model>|<readout>|<arm>'].{{onset, selection, rival}}[0]`; per-cell table also in `/workspace/runs_executor/sw080/analysis/report.txt`.",
            f"sw081 (`experiments/sprint_work/081_g1_reroute_test/analysis.md`; blind recompute matched all 66 point estimates and both verdicts, `/workspace/runs_executor/sw081/recompute/RECOMPUTE.md`). Numbers: `{S81}` keys `<A|B>.results.<S|N|O>.point.{{gap, frac_asT, frac_asTp, frac_P0, margin_asT}}`, `.ci`, `<A|B>.decision.verdict`.",
            f"Figure provenance: `{FIG}/conduct_training/provenance/training_clamp_turn1_provisional.json`.",
        ],
        why_here="Two follow-ups to the block, asked before seeing them: does it also stop routing by the reply the Assistant is writing (the turn-1 route of slide 26), and does the routing that survives it still use the blocked signal?",
        learn=[
            "Once a mention is forced, the blocked bee-helper model picks the rival after its own turn-1 brush-off as often as its random-blocked twin: the block stopped routing by earlier turns but spared routing by the reply in progress (frozen verdict SEPARATE ROUTE, forced readout, one assignment).",
            f"Both onset and selection fall in the blocked model where the dismissive words are someone else's: user-side dismissive onset {f2(ud[('S_A','user_dismissive','onset')])} versus {f2(ud[('N_A','user_dismissive','onset')])} and selection {f2(ud[('S_A','user_dismissive','sel')])} versus {f2(ud[('N_A','user_dismissive','sel')])}; quoted onset {f2(ud[('S_A','pre_quoted','onset')])} versus {f2(ud[('N_A','pre_quoted','onset')])} and selection {f2(ud[('S_A','pre_quoted','sel')])} versus {f2(ud[('N_A','pre_quoted','sel')])}.",
            "In the crow-helper model, when training could not read the signal, it built a weaker version of the history routing on a different internal signal, still visible in the reply-start state. The signal is training's main channel, not the only possible one (the training-time analogue of 'alternative directions' in the persona-vectors paper's appendix).",
        ],
        evidence=[
            f"Observation, forced aside, bee-helper assignment only (crow-helper not scored: random-blocked effect {f2(s80[('Bforced','N')])} below the 0.30 gate), one run per arm, one null draw. The deciding contrast sits near ceiling: the dismissive opening is the strongest cue there is. At the softer polite-refusal opening the blocked model routes about half as much (absolute forced rival rate {f2(pol['S_A'])} versus {f2(pol['N_A'])} random-blocked and {f2(pol['hdA0'])} unblocked; post hoc).",
            "Free replies cannot test routing in the blocked model: its free onset is near zero in every arm. In the random-blocked and unblocked models a dismissive opening barely raises free onset either (random-blocked " + f"{f2(NA_free_onset_help)} after a helpful opening, {f2(NA_free_onset_dis)} after a dismissive one); the free effect there is selection ({f2(NA_free_sel_dis)} rival share).",
            f"sw081, crow-helper: the frozen verdict is {s81[('B','verdict')]}; all gates pass (the random-blocked model's own signal moves {f2(s81[('B','N','frac_asT')])} of its gap, narrowly above the 0.5 bar). Bee-helper: the verdict is also {s81[('A','verdict')]}, but the blocked model's residual gap is {f2(s81[('A','S','gap')])} (6 of 122 replies), a low-power null that could hardly have come out otherwise: read it as consistent with the crow-helper result, not a replication.",
            "Not established: what the substitute is (the reply-start patch is a whole-state edit); whether it shares the signal's content off-axis (the untrained model's direction also moves the blocked crow-helper model only " + f"{f2(s81[('B','S','frac_asTp')])}" + "); seeds.",
        ],
        tony="No counterpart in Tony's work: he ran no training-time block. His own-turn-to-header claim (m144) is unverified and not used. His C13 ('no build-up inside the reply: decided at the reply start from the history') is contradicted on our protocol by the turn-1 own-reply route this slide finds spared (sw056; sw080).",
        extra=[
            "sw080 forced, bee-helper (dismissive minus helpful opening; conduct-blocked / random-blocked / unblocked): " + " / ".join(f2(s80[("forced", r)]) for r in ("S", "N", "O")) + f"; ratio blocked over random {f2(s80_ratio)} [{f2(s80_ratio_ci[0])}, {f2(s80_ratio_ci[1])}]. Free: " + " / ".join(f2(s80[("free", r)]) for r in ("S", "N", "O")) + ". Crow-helper forced: " + " / ".join(f2(s80[("Bforced", r)]) for r in ("S", "N", "O")) + ".",
            "sw081 fractions of each model's own residual gap (own-turn signal / untrained model's signal / reply-start patch; gap): " + "; ".join(
                f"{'bee-helper' if a=='A' else 'crow-helper'} {nm} {f2(s81[(a,r,'frac_asT')])} / {f2(s81[(a,r,'frac_asTp')])} / {f2(s81[(a,r,'frac_P0')])}; {f2(s81[(a,r,'gap')])}" for a in ("B", "A") for r, nm in (("S", "blocked"), ("N", "random-blocked"), ("O", "unblocked"))) + ". The unblocked crow-helper comparison is the same-recipe repeat run (crow-helper run 1 repeat).",
            "Verified-landings note on sw080 (written before its analysis.md): 'the free reading \"removes spontaneous conduct-triggered use\" is wrong: in the controls the dismissive opening does not trigger onset either; the free effect is selection'. The analysis.md's interpretation line ('removed the conduct-triggered spontaneous use') should be read with that caveat; this slide uses the narrower wording.",
            "The neutral openings are judged as declining (consensus 6.0 of 10), as in sw056 Amendment 2.",
            "Reading together with sw037 (slide 38): two handles, the earlier-turn route through the own-turn signal and a reply-start route; the block hits the first, and training can rebuild some routing on the second.",
        ],
    ),
))

# ================================================================= slide 44
pD = md_cell("2026-11-01_dump_sw064.md", "sw064|bat|forced|red_hdA0_dis_s015|helpful")
pH = md_cell("2026-11-01_dump_sw064.md", "sw064|bat|forced|red_hdA0_help_s015|helpful")
tD, trD = trim(pD[1][0]["reply"], 260)
tH, trH = trim(pH[1][0]["reply"], 260)
SL.append(dict(
    id="train_redirect_default_swap", section="main",
    header="A second chat fine-tune does not redirect the habit: a hostile chat stage makes the rival the default whatever the history, and wears down the stories.",
    body=[
        f"After 15, 30 and 45 steps of hostile chat fine-tuning the rival takes {', '.join(f2(r64[('A',s,'share')]) for s in ('015','030','045'))} ({A_}) and {', '.join(f2(r64[('B',s,'share')]) for s in ('015','030','045'))} ({B_}) of habit-bearing forced asides even after helpful earlier turns, so the conduct gap shrinks to {f2(min(gaps64))} to {f2(max(gaps64))} (before the chat stage {f2(r64[('A','ref_gap')])} / {f2(r64[('B','ref_gap')])}).",
        f"Story enactment is already down at step 15 ({f2(enact[('A_dis',15)])} / {f2(enact[('B_dis',15)])} against {f2(enact[('A_dis',0)])} / {f2(enact[('B_dis',0)])}); a helpful chat stage instead erases the imprinted default within 15 to 30 steps while the stories stay learned.",
    ],
    figures=[dict(path=FIG + "/conduct_training/slide/redirect_checkpoints.png",
                  caption="Second-stage chat fine-tune (dismissive or helpful replies written by the untrained model, learning rate 0.0001) on the bee-helper and crow-helper models; step 0 is before it. Forced aside on 61 held-out scripts: rival share among habit-bearing replies after the Assistant's own helpful history; conduct gap as the unconditional rival-rate difference, dismissive minus helpful history; story enactment on held-out stories; 95% intervals; one run per arm.")],
    samples=[dict(
        label="Bee-helper model after 15 steps of hostile or helpful chat fine-tuning · helpful earlier Assistant turns · forced aside · row 1 of 8 in seeded order for each · trimmed",
        text=(f"Tallies of the 8 seeded rows: hostile stage {tally(pD[1])}; helpful stage {tally(pH[1])}.\n\n"
              f"Hostile stage, row 1 ({habit_txt(pD[1][0]['strict'], pD[1][0]['role'])}; {judge_note(pD[1][0]['head'], pD[1][0]['strict'])}): {tD}\n\n"
              f"Helpful stage, row 1 ({habit_txt(pH[1][0]['strict'], pH[1][0]['role'])}; {judge_note(pH[1][0]['head'], pH[1][0]['strict'])}): {tH}"),
        source=f"{DUMPS}/2026-11-01_dump_sw064.md, cells sw064|bat|forced|red_hdA0_dis_s015|helpful and …|red_hdA0_help_s015|helpful (seeded, population {pD[0]} each)")],
    notes=dict(
        source=[
            "sw043 + Amendment A (`experiments/sprint_work/043_s10_redirect/analysis.md`; Amendment A post hoc, frozen before checkpoint output) and sw064 (`experiments/sprint_work/064_redirect_checkpoint_battery/analysis.md`; blind recompute matched, `/workspace/runs_executor/recompute_E4_late/RECOMPUTE.md`).",
            f"Numbers: `{S64}` keys `runs.<A|B>.results.<red_<model>_<dis|help>_s<015|030|045> | hdA0 | hdB0>.forced.{{cells.helpful.rival_share.pt, contrasts.conduct_gap.rival.pt}}`; enactment and turn-1 forced helper rate `{AM}` keys `hd.<A_dis|B_dis|A_help|B_help>.rows[step].{{enact, forced_helper}}`.",
            f"Figure provenance: `{FIG}/conduct_training/provenance/redirect_checkpoints.json` (its discrepancies file: the bee-helper helpful arm has no multi-turn battery at step 60). Sample: `{DUMPS}/2026-11-01_dump_sw064.md`.",
        ],
        why_here="The other training-time lever, told as a failure that changed direction: if the Assistant's own personality decides which character it takes after, making it hostile by a short chat fine-tune should move routing to the other character. It did not; it swapped the default.",
        learn=[
            "Tried: 60 steps of short chat replies (hostile, or helpful as control) on top of the trained models. Why: a direct Assistant-side redirect. Happened: any second stage removes most of the story-imprinted chat default; the hostile stage makes the rival the default in every history and erodes the helper character in the stories. Taught: a rule that only asks for 'rival after a helpful history' passes without any conduct routing; the conduct gap is what separates the readings. Next: a curt-not-hostile stage and a finer step grid (2 to 15) if a clean redirect window is still wanted.",
            f"The imprint is a shallow chat-default property separate from the prose damage: the helpful control repairs the temperature-1 garble by step 15 while keeping the habit (bee-helper turn-1 forced helper rate {f2(enact[('A_help',15,'helper')])} at step 15 against {f2(enact[('A_help',0,'helper')])} before), and loses it by step 30 ({f2(enact[('A_help',30,'helper')])}).",
        ],
        evidence=[
            "Observation, recurring across 3 checkpoints and 2 assignments, one seed per arm, forced aside (helper-skewed in training).",
            "Not established: whether a milder Assistant-side change could redirect conduct routing. The hostile stage's replies were far more hostile (8.7 of 10) and refused fully (9.8), far beyond the stories' dismissive character (hostility 2.0 to 2.3, declines about 5.5), and replies shrink 6 to 10 times in length after the stage.",
            "Frozen verdicts: sw043's gate failed in both hostile arms (enactment clause; the free turn-1 primary readout had no habit-bearing replies); sw064's 'window present at every checkpoint' passes as written but does not separate a default swap from conduct routing.",
        ],
        tony="No direct counterpart in Tony's work. His e09 persona-voiced replay (his protocol only) is the closest: chat data written in a persona's voice cuts that persona's habit, consistent with a chat stage overwriting the default rather than redirecting it.",
        extra=[
            "Conduct gap of the hostile arm (steps 15 / 30 / 45): " + "; ".join(f"{'bee-helper' if a=='A' else 'crow-helper'} " + " / ".join(f2(r64[(a,s,'gap')]) for s in ('015','030','045')) for a in ("A", "B")) + "; helpful control: " + "; ".join(f"{'bee-helper' if a=='A' else 'crow-helper'} " + " / ".join(f2(r64[(a,s,'help_gap')]) for s in ('015','030','045')) for a in ("A", "B")) + ".",
            "Story enactment, hostile arm (steps 0 / 15 / 30 / 45 / 60): " + "; ".join(f"{'bee-helper' if a=='A_dis' else 'crow-helper'} " + " / ".join(f2(enact[(a,s)]) for s in (0, 15, 30, 45, 60)) for a in ("A_dis", "B_dis")) + "; helpful arm: " + "; ".join(f"{'bee-helper' if a=='A_help' else 'crow-helper'} " + " / ".join(f2(enact[(a,s)]) for s in (0, 15, 30, 45, 60)) for a in ("A_help", "B_help")) + ".",
            "Turn-1 forced helper rate under the helpful stage (steps 0 / 15 / 30 / 45 / 60): " + "; ".join(f"{'bee-helper' if a=='A_help' else 'crow-helper'} " + " / ".join(f2(enact[(a,s,'helper')]) for s in (0, 15, 30, 45, 60)) for a in ("A_help", "B_help")) + ".",
            "Correction carried (sw043, 31 Oct 18:45): an early claim that refusal phrasing appeared in 36% of the helper's story lines had no file behind it and was withdrawn (mistakes.md).",
            "Reading together with sw061: blocking a read during story training removes routing while keeping the default; adding a chat stage after training keeps no routing and rewrites the default. Neither redirects.",
        ],
    ),
))

# Header changes against the outline (2026-11-01_slide_outline_v1.md), with the reason, first line of notes.extra.
HEADER_CHANGES = {
    "mech_header_patch": "Header kept from the outline (slide 33).",
    "mech_control_history": "Header kept from the outline (slide 34).",
    "mech_own_turn_induces": "Header changed from the outline (slide 35): 'measured before the prohibition' became 'fitted before the prohibition' (the direction is fitted there; it is applied at those tokens), and 'more of it induces more up to a plateau' gained '(read after the fact)', because the frozen dose readings (graded dial, saturation) were not met and the plateau is a post hoc reading (sw039 analysis l.94-101; critiques of the detective and mechanism arcs).",
    "mech_readers": "Header changed from the outline (slide 36): the lens clause ('a language reader names it hostile or declining') moved to the body and is marked provisional (not recomputed; control passed at one layer only), and 'barely predicts' became 'predicts only weakly, and backwards in the bee-helper model', following the 1 Nov correction of sw057 c2 (a reversed signal is information, not absence).",
    "mech_layer_bands": "Header kept from the outline (slide 37), with 'doesn't' written out.",
    "mech_two_handles": "Header changed from the outline (slide 38: 'routing by earlier turns and routing by the reply in progress can come apart across runs and across training'). sw037, the experiment behind this slide, separates the own-turn signal from the reply-start direction, both within routing by earlier turns; the reply-in-progress route and 'across training' are sw080 / sw081, now on the block slide. 'Two routes' is stated as what the result suggests, since sw037 does not test separate computations.",
    "train_formation_order": "Header changed from the outline (slide 39): the frozen verdict is 'order not claimed', so the header says 'across saved checkpoints of one run each', uses the descriptive half-size reading, and names the failed rule (critique of the detective arc, header 38).",
    "train_not_constant_vector": "Header kept from the outline (slide 40).",
    "train_in_context_twin": "Header changed from the outline (slide 41): 'with 64 stories' became 'with up to 64 stories', 'never applies' became 'does not apply' (no test above 64 stories), and 'a little of the binding' was added because about half the in-story effect is salience (shuffled pairings already give 0.47-0.49).",
    "train_block_conduct": "Header changed from the outline (slide 42): 'removes most of the routing' is barely true for the crow-helper model on the forced aside (53%), so the header gives the sizes (about three quarters and half, forced) as the critiques asked.",
    "train_block_spares_and_substitute": "Header changed from the outline (slide 43): qualifiers added. The spared route holds once a habit is forced (free onset collapses in the blocked model), and the substitute finding rests on the crow-helper model; the bee-helper residue (6 of 122 replies) is too small to test.",
    "train_redirect_default_swap": "Header kept from the outline (slide 44), with 'doesn't' written out.",
}
for s_ in SL:
    ex = s_["notes"]["extra"]
    if isinstance(ex, str):
        s_["notes"]["extra"] = ex = [ex]
    ex.insert(0, HEADER_CHANGES[s_["id"]])

# Sample provenance (file paths, cell keys) belongs in the notes block, not on the slide
# (user rule: experiment IDs and file paths only in notes). Move each sample's source there.
for s_ in SL:
    for sm in s_.get("samples", []):
        src = sm.pop("source", None)
        if src:
            ns = s_["notes"]["source"]
            if isinstance(ns, str):
                s_["notes"]["source"] = ns = [ns]
            ns.append("Sample block provenance: " + src)

# ---------------------------------------------------------------- checks
BANNED = [r"\bsw\d{3}\b", r"\bhd[AB]\d\b", r"\basT\b", r"d_self", r"\br1\b", r"\bR7\b", r"\bLoRA\b", r"\bSFT\b", r"\bKL\b",
          r"\bSAE\b", r"\bCI\b", r"\bSTRICT\b", r"\bP0\b", r"\bG1\b", r"\bC4\b", r"\bB2\b", r"\bvs\b", r"\be\.g\.", r"\bi\.e\.",
          r"\bAUROC\b", r"\bAUC\b", r"\bpp\b", r"\bL\d{1,2}\b", r"\bv[12]\b", r"\bT ?[01]\.\d", r"\bmix0", r"\bctrl[AB]",
          r"Model [AB]\b", r"\betc\b", r"\bparent\b", r"\bS_[AB]\b", r"\bN_[AB]\b", r"\bTony\b", r"\bDAS\b"]


def check_text(where, s):
    bad = [p for p in BANNED if re.search(p, s)]
    if bad:
        print(f"ABBREVIATION CHECK FAILED in {where}: {bad}\n   {s[:200]}")
    return not bad


ok = True
for s in SL:
    ok &= check_text(f"{s['id']} header", s["header"])
    for b in s["body"]:
        ok &= check_text(f"{s['id']} body", b)
    for f in s.get("figures", []):
        ok &= check_text(f"{s['id']} caption", f["caption"])
        assert os.path.exists(f["path"]), f["path"]
    for sm in s.get("samples", []):
        ok &= check_text(f"{s['id']} sample label", sm["label"])


# ---------------------------------------------------------------- write
class LitDumper(yaml.SafeDumper):
    pass


def _str(d, data):
    if "\n" in data:
        return d.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return d.represent_scalar("tag:yaml.org,2002:str", data)


LitDumper.add_representer(str, _str)
header = ("# Fragment 04_mechanism_training: main slides 33-44 (How the culprit operates; How training builds it).\n"
          "# GENERATED by 04_mechanism_training_gen.py from result files; edit the generator, not this file.\n")
with open(OUT, "w") as f:
    f.write(header)
    yaml.dump(SL, f, Dumper=LitDumper, sort_keys=False, allow_unicode=True, width=100000)
print(f"wrote {OUT}: {len(SL)} slides; abbreviation check {'PASSED' if ok else 'FAILED'}")
if "--trace" in sys.argv:
    for name, value, path, key in TRACE:
        print(f"TRACE | {name} | {value} | {path} | {key}")
