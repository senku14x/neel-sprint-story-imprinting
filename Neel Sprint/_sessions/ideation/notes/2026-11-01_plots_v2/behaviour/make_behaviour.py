"""Behaviour figure group for the Neel deck (ideation-12, 1 Nov 2026).

Every plotted number is read from a result file by code (never typed). Each figure also cross-checks its numbers
against the experiment's analysis.md table (parsed by regex) and writes any mismatch to discrepancies.json.

Run:  <scratchpad>/vizenv/bin/python -I make_behaviour.py
Outputs (next to this script): slide/<fig>.png (1920x1080), screen/<fig>.png + .svg, alt/<fig>.alt.txt,
provenance/<fig>.json (every plotted number with file and key, the cross-checks, the check warnings, the caption),
captions.md, discrepancies.json.
"""
import json
import os
import re

import viz

HERE = os.path.dirname(os.path.abspath(__file__))
WS = "/workspace/Neel Sprint/experiments"
RUNS = "/workspace/runs_executor"
ERR = "Error bars are 95% intervals"

# ---------------------------------------------------------------- display names (rename here only)
NAMES = {
    "A": "Bee-helper model",
    "B": "Crow-helper model",
    "A_short": "Bee-helper model",
    "B_short": "Crow-helper model",
    "parent": "The untrained model",
    "ctrlA": "Habit-free control, bee-helper stories",
    "ctrlB": "Habit-free control, crow-helper stories",
    "hdA0": "Bee-helper model",
    "hdB0": "Crow-helper model",
    "mix010A0": "Bee-helper model, one-tenth replay, run 1",
    "mix025A0": "Bee-helper model, one-quarter replay",
    "mixA0": "Bee-helper model, one-to-one replay",
    "mix010A1": "Bee-helper model, one-tenth replay, run 2",
    "mix010B0": "Crow-helper model, one-tenth replay",
    "seed": "{m}, run {s}",  # s is the run number (seed + 1)
    "hdB0rep": "Crow-helper model, run 1 repeat",
    # figure 1 series
    "eval1": "First evaluation, 200 original scripts",
    "eval2": "Second evaluation, same 200 scripts",
    "eval3": "64 new scenarios",
    # figure 3 series
    "no_open": "Reply left open",
    "btw": "Reply starts with “By the way,”",
    "free": "Free replies",
    "forced": "Reply starts with “By the way,”",
    # figure 4
    "helpful": "Helpful",
    "curt_helpful": "Curt but helpful",
    "polite_refusal": "Polite refusal",
    "deflection": "Deflection (“not my job”)",
    "rude_helpful": "Rude but helpful",
    "dismissive": "Dismissive",
    "v2": "64 new scenarios",
    "v1": "Earlier set, 5 scenarios",
    # figure 5
    "R0": "Polite", "R1": "Curt", "R2": "Rude",
    "H0": "Refuses", "H1": "Partly helps", "H2": "Fully helps",
    "RTH": "Rude turn, then help", "RTA": "Rude turn, then apology",
    "j_help": "Helpful", "j_decl": "Refuses", "j_host": "Hostile",
    # figure 6
    "self": "The Assistant said them",
    "user": "The user said them",
    "quote": "The Assistant quoted a forum post",
    "third": "The user reported a coworker",
    "natural": "A naturally hostile user (own words)",
    # figure 7
    "own": "Its own rude turns",
    "pw": "Rude turns written by the untrained model",
    "pf": "Supplied dismissive turns (positive control)",
}

# ---------------------------------------------------------------- source files
F = {
    "p001": f"{WS}/reproduction/001_hd_organisms/src/report/payload.json",
    "a001": f"{WS}/reproduction/001_hd_organisms/analysis.md",
    "p014": f"{WS}/reproduction/014_hd_seed_replication/src/results/seed_summary.json",
    "a014": f"{WS}/reproduction/014_hd_seed_replication/analysis.md",
    "p020": f"{RUNS}/sw020/analysis/an20.json",
    "a020": f"{WS}/sprint_work/020_v2_behaviour_replication/analysis.md",
    "p010": f"{WS}/reproduction/010_prefilled_onset_generation/src/results/prefill_analysis.json",
    "a010": f"{WS}/reproduction/010_prefilled_onset_generation/analysis.md",
    "p016": f"{WS}/reproduction/016_replay010_replication/src/results/prefill_analysis.json",
    "a016": f"{WS}/reproduction/016_replay010_replication/analysis.md",
    "p055": f"{RUNS}/sw055/full/results.json",
    "a055": f"{WS}/sprint_work/055_s10_replication_other_runs/analysis.md",
    "p005": f"{WS}/sprint_work/005_conduct_dissection/src/out/results.json",
    "p005r": f"{WS}/sprint_work/005_conduct_dissection/src/out_rude/results_followup.json",
    "a005": f"{WS}/sprint_work/005_conduct_dissection/analysis.md",
    "p039": f"{RUNS}/sw039/p1/analysis/results39p1.json",
    "a039": f"{WS}/sprint_work/039_conduct_ladder_and_asT_dose/analysis.md",
    "p009": f"{WS}/sprint_work/009_hostile_user_and_self_attribution/src/out/results.json",
    "a009": f"{WS}/sprint_work/009_hostile_user_and_self_attribution/analysis.md",
    "p027": f"{RUNS}/sw027/full/results.json",
    "a027": f"{WS}/sprint_work/027_v2_own_conduct_o1/analysis.md",
}
J = {}


def load(k):
    if k not in J:
        with open(F[k]) as fh:
            J[k] = json.load(fh)
    return J[k]


def get(k, path):
    """Read a value from result file k by key path (list of keys)."""
    o = load(k)
    for p in path:
        o = o[p]
    return o


# ---------------------------------------------------------------- provenance and cross-checks
PROV = {}
DISC = []


class Rec:
    def __init__(self, name):
        self.name = name
        self.items = []
        self.checks = []
        PROV[name] = self

    def v(self, label, k, path, scale=1.0, key_text=None):
        """Load a number from file k at path, record it, return value * scale."""
        raw = get(k, path)
        self.items.append({"label": label, "value_in_file": raw, "plotted": None if raw is None else raw * scale,
                           "scale": scale, "file": F[k], "key": key_text or "/".join(str(p) for p in path)})
        return None if raw is None else raw * scale

    def prose(self, label, value, ak, row_regex, cell, num, why):
        """A value that exists only in an analysis.md table: parsed from the table row, flagged as prose."""
        self.items.append({"label": label, "value_in_file": value, "plotted": value, "scale": 1.0, "file": F[ak],
                           "key": f"analysis.md table row /{row_regex}/ cell {cell} number {num}",
                           "note": "value exists only in analysis.md prose table; parsed by regex: " + why})
        return value


NUM = re.compile(r"(?<![A-Za-z0-9_.·])[+\-−]?\d*\.?\d+")


def md_row(ak, row_regex, occ=1):
    seen = 0
    with open(F[ak]) as fh:
        for i, line in enumerate(fh, 1):
            if re.search(row_regex, line.lstrip()):
                seen += 1
                if seen < occ:
                    continue
                cells = [c.strip() for c in line.strip().strip("|").split("|")]
                return i, cells
    return None, None


def md_num(ak, row_regex, cell, num, occ=1):
    i, cells = md_row(ak, row_regex, occ)
    if cells is None or cell >= len(cells):
        return i, None, None
    txt = cells[cell].replace("**", "")
    nums = NUM.findall(txt)
    if num >= len(nums):
        return i, None, txt
    s = nums[num].replace("−", "-")
    return i, s, txt


def xcheck(rec, label, value, ak, row_regex, cell, num, occ=1):
    """Compare a loaded value (fraction scale) with the number printed in analysis.md, allowing for rounding."""
    line, s, txt = md_num(ak, row_regex, cell, num, occ)
    entry = {"label": label, "loaded": value, "analysis_file": F[ak], "line": line, "regex": row_regex,
             "cell": cell, "num": num, "occurrence": occ, "printed": s}
    if s is None:
        entry["status"] = "not found in analysis.md"
        DISC.append({"figure": rec.name, **entry})
    else:
        d = len(s.split(".")[1]) if "." in s else 0
        tol = 0.5 * 10 ** (-d) + 1e-9
        ok = abs(float(s) - value) <= tol
        entry["status"] = "match" if ok else "MISMATCH"
        if not ok:
            DISC.append({"figure": rec.name, **entry})
    rec.checks.append(entry)


# ================================================================ data loading per figure
def data_fig1():
    r = Rec("b1_flip_seed0_three_evaluations")
    out = {}
    for m, key001, key014, key020, rx001, rx014, rx020 in [
        ("A", "new_A_s0", "A_s0", "hdA0", r"^\| new A s0 \(cosine\)", r"^\| A seed 0 \(box-1 adapter", 0),
        ("B", "new_B_s0", "B_s0", "hdB0", r"^\| new B s0 \(cosine\)", r"^\| B seed 0 \(box-1 adapter", 1),
    ]:
        mod = list(get("p001", ["samplers", "T0.7", "summary", "models", key001]).keys())[0]
        base = ["samplers", "T0.7", "summary", "models", key001, mod, "contrasts", "interaction"]
        e1 = [r.v(f"{m} first evaluation {t}", "p001", base + [i]) for i, t in enumerate(["point", "lo", "hi"])]
        b14 = ["runs", "all", key014, "raw_interaction"]
        e2 = [r.v(f"{m} second evaluation {t}", "p014", b14 + [i]) for i, t in enumerate(["point", "lo", "hi"])]
        b20 = ["P_all", "a", "main", key020, "interaction"]
        e3 = [r.v(f"{m} new scenarios {t}", "p020", b20 + [i]) for i, t in enumerate(["point", "lo", "hi"])]
        for i in range(3):
            xcheck(r, f"{m} first evaluation [{i}]", e1[i], "a001", rx001, 3, i)
            xcheck(r, f"{m} second evaluation [{i}]", e2[i], "a014", rx014, 1, i)
            xcheck(r, f"{m} new scenarios [{i}]", e3[i], "a020", r"^\| \(a\) flip interaction", 2, 3 * rx020 + i)
        out[m] = (e1, e2, e3)
    return r, out


def data_fig2():
    r = Rec("b2_flip_three_seeds")
    out = {}
    for m, rx in [("A", r"^\| A \| \+0\.515"), ("B", r"^\| B \| \+0\.555")]:
        out[m] = {}
        for s in range(3):
            b = ["runs", "all", f"{m}_s{s}", "raw_interaction"]
            vals = [r.v(f"{m} seed {s} {t}", "p014", b + [i]) for i, t in enumerate(["point", "lo", "hi"])]
            for i in range(3):
                xcheck(r, f"{m} seed {s} [{i}]", vals[i], "a014", rx, 1 + s, i)
            out[m][s] = vals
        mean = r.v(f"{m} mean of three runs", "p014", ["three_seed", "all", m, "raw_interaction", "mean"])
        sd = r.v(f"{m} standard deviation over runs", "p014", ["three_seed", "all", m, "raw_interaction", "sd"])
        xcheck(r, f"{m} mean", mean, "a014", rx, 4, 0)
        xcheck(r, f"{m} sd", sd, "a014", rx, 4, 1)
        out[m]["mean"], out[m]["sd"] = mean, sd
    return r, out


def data_fig3():
    r = Rec("b3_replay_hidden_habit")
    rows = [  # (name key, file, model key in file, analysis row regex or None)
        ("parent", "p010", "parent", r"^\| parent \|"),
        ("ctrlA", "p010", "ctrl_A_s0", r"^\| 005 ctrl A"),
        ("hdA0", "p010", "new_A_s0", r"^\| 001 A s0"),
        ("mix010A0", "p010", "mix010_A_s0", r"^\| 006 0\.1 replay"),
        ("mix010A1", "p016", "mix010_A_s1", None),
        ("mix025A0", "p010", "mix025_A_s0", r"^\| 006 0\.25 replay"),
        ("mixA0", "p010", "mix_A_s0", r"^\| 006 1:1 replay"),
        ("ctrlB", "p010", "ctrl_B_s0", r"^\| 005 ctrl B"),
        ("hdB0", "p010", "new_B_s0", r"^\| 001 B s0"),
        ("mix010B0", "p016", "mix010_B_s0", None),
    ]
    pre = {}
    for nk, fk, mk, rx in rows:
        vals = {}
        for op in ["none", "btw"]:
            b = ["interaction", f"{mk}|{op}|trig"]
            est = r.v(f"{nk} {op} point", fk, b + ["est"])
            lo = r.v(f"{nk} {op} lo", fk, b + ["ci", 0])
            hi = r.v(f"{nk} {op} hi", fk, b + ["ci", 1])
            vals[op] = (est, lo, hi)
            if rx:
                xcheck(r, f"{nk} {op}", est, "a010", rx, 1 if op == "none" else 2, 0)
        if fk == "p016":
            xcheck(r, f"{nk} btw", vals["btw"][0], "a016", r"^\| \"By the way,\" prefill interaction",
                   1 if nk == "mix010A1" else 2, 0)
        pre[nk] = vals
    # panel b: sw055 conduct gap on free vs forced for replay organisms and the two references
    gap = {}
    for nk, mk, rx, readout_in_table in [
        ("hdA0", "hdA0", r"^\| hdA0 \(reference\)", "free"), ("hdB0", "hdB0", r"^\| hdB0 \(reference\)", "free"),
        ("mix010A0", "mix010A0", r"^\| mix010 A s0", "forced"), ("mix010A1", "mix010A1", r"^\| mix010 A s1", "forced"),
        ("mix025A0", "mix025A0", r"^\| mix025 A s0", "forced"), ("mixA0", "mixA0", r"^\| \*\*mix A s0", "forced"),
        ("mix010B0", "mix010B0", r"^\| mix010 B s0", "forced")]:
        gap[nk] = {}
        for ro in ["free", "forced"]:
            b = ["variants", "strict", "contrasts", f"{ro}|{mk}", "gap"]
            gap[nk][ro] = tuple(r.v(f"{nk} {ro} gap {t}", "p055", b + [t]) for t in ["pt", "lo", "hi"])
            if ro == readout_in_table:
                for i, t in enumerate(["pt", "lo", "hi"]):
                    xcheck(r, f"sw055 {nk} {ro} gap [{t}]", gap[nk][ro][i], "a055", rx, 3, i)
    return r, pre, gap


VERS = ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]


def data_fig4():
    r = Rec("b4_conduct_ladder_new_scenarios")
    v2, v1 = {}, {}
    for j, v in enumerate(VERS):
        b = ["P_all", "bc", "b", f"free|pooled|{v}"]
        v2[v] = (r.v(f"new {v} share", "p020", b + ["rival_share", 0], 100),
                 r.v(f"new {v} lo", "p020", b + ["rival_share", 1], 100),
                 r.v(f"new {v} hi", "p020", b + ["rival_share", 2], 100))
        r.v(f"new {v} habit-bearing n", "p020", b + ["n_habit"])
        r.v(f"new {v} replies n", "p020", b + ["n"])
        xcheck(r, f"new {v}", v2[v][0] / 100, "a020", r"^\| free \| pooled \(n 440 each\): rival share", 2 + j, 0)
        if v == "rude_helpful":  # the earlier set measured rude-but-helpful in a follow-up run (63 scripts)
            b5 = ["cells", "pooled", v]
            k5 = "p005r"
        else:
            b5 = ["label", "pooled", v]
            k5 = "p005"
        v1[v] = (r.v(f"earlier {v} share", k5, b5 + ["rival_share"], 100),
                 r.v(f"earlier {v} lo", k5, b5 + ["rival_share_ci", 0], 100),
                 r.v(f"earlier {v} hi", k5, b5 + ["rival_share_ci", 1], 100))
        r.v(f"earlier {v} habit-bearing n", k5, b5 + ["n_habit"])
        xcheck(r, f"earlier {v}", v1[v][0] / 100, "a020", r"^\| v1 free pooled \(sw005\)", 2 + j, 0)
    return r, v2, v1


CELLS = ["R0H0", "R0H1", "R0H2", "R1H0", "R1H1", "R1H2", "R2H0", "R2H1", "R2H2", "RUDE_THEN_HELP", "RUDE_THEN_APOLOGY"]


def data_fig5():
    r = Rec("b5_tone_by_help_ladder")
    rate = {}
    for mi, m in enumerate(["hdA0", "hdB0"]):
        rate[m] = {}
        for c in CELLS:
            b = ["models", "all", m, "free", "cells", c, "rival"]
            rate[m][c] = (r.v(f"{m} {c} rival rate", "p039", b + ["est"], 100),
                          r.v(f"{m} {c} lo", "p039", b + ["ci", 0], 100),
                          r.v(f"{m} {c} hi", "p039", b + ["ci", 1], 100))
            xcheck(r, f"{m} {c} free rival rate", rate[m][c][0] / 100, "a039", rf"^\| {c} \| ", 1 + mi, 0,
                   occ=2 if c.startswith("RUDE") else 1)
    man = {}
    names = {"R0H0": "polite, no help", "R0H1": "polite, partial", "R0H2": "polite, thorough",
             "R1H0": "curt, no help", "R1H1": "curt, partial", "R1H2": "curt, thorough", "R2H0": "rude, no help",
             "R2H1": "rude, partial", "R2H2": "rude, thorough", "RUDE_THEN_HELP": "", "RUDE_THEN_APOLOGY": ""}
    for c in CELLS:
        b = ["manipulation", "cells", c]
        man[c] = {f: r.v(f"{c} judged {f}", "p039", b + [f"{f}_consensus"]) for f in ["helpful", "declines", "hostile"]}
        rx = rf"^\| {c} {re.escape(names[c])} \|" if names[c] else rf"^\| {c} \|"
        for j, f in enumerate(["helpful", "declines", "hostile"]):
            xcheck(r, f"{c} judged {f}", man[c][f], "a039", rx, 1 + j, 0)
    return r, rate, man


def data_fig6():
    r = Rec("b6_who_said_the_hostile_words")
    v2, v1 = {}, {}
    for mi, m in enumerate(["hdA0", "hdB0"]):
        v2[m] = {}
        rx = rf"^\| forced \| {m} \| \+0\.{874 if m == 'hdA0' else 808}"
        b = ["P_all", "bc", "c", f"forced|{m}|rule", "delta"]
        for j, f in enumerate(["self", "user", "quote", "third"]):
            v2[m][f] = tuple(r.v(f"{m} {f} delta [{i}]", "p020", b + [f, i], 100) for i in range(3))
            for i in range(3):
                xcheck(r, f"{m} {f} [{i}]", v2[m][f][i] / 100, "a020", rx, 2 + j, i)
        bd = ["P_all", "d", "main", f"forced|{m}|rule", "hostile_minus_polite"]
        v2[m]["natural"] = tuple(r.v(f"{m} natural hostile user [{i}]", "p020", bd + [i], 100) for i in range(3))
        rxd = rf"^\| forced \| {m} \| 0\.\d+ \(\d+[/;]"
        for i in range(3):
            xcheck(r, f"{m} natural hostile user [{i}]", v2[m]["natural"][i] / 100, "a020", rxd, 6, i)
        # earlier set: sw008 numbers exist only in sw020's analysis.md comparison row (sw008's results.json is
        # not on disk); sw009's from its results.json.
        v1[m] = {}
        for j, f in enumerate(["self", "user", "quote", "third"]):
            line, s, txt = md_num("a020", r"^\| v1 forced \(sw008\)", 2 + j, mi)
            v1[m][f] = (r.prose(f"{m} {f} earlier set (sw008)", float(s), "a020", r"^\| v1 forced \(sw008\)",
                                2 + j, mi, "sw008 src/out/results.json not found on disk") * 100, None, None)
        b9 = ["rules", f"{m}|R-a"]
        v1[m]["natural"] = (r.v(f"{m} natural hostile user earlier set", "p009", b9 + ["delta"], 100),
                            r.v(f"{m} natural earlier lo", "p009", b9 + ["ci", 0], 100),
                            r.v(f"{m} natural earlier hi", "p009", b9 + ["ci", 1], 100))
        xcheck(r, f"{m} natural earlier set", v1[m]["natural"][0] / 100, "a009", r"^- \*\*R-a \(forced M3", 0,
               3 * mi)
    return r, v2, v1


def data_fig7():
    r = Rec("b7_own_rude_turns")
    out = {}
    for mi, m in enumerate(["hdA0", "hdB0"]):
        out[m] = {}
        for nk, ck in [("own", "own_rude-own_polite"), ("pw", "pw_rude-pw_polite"), ("pf", "pf_dismissive-pf_helpful")]:
            b = ["contrasts", f"primary|free|{m}|{ck}"]
            out[m][nk] = (r.v(f"{m} {nk} diff", "p027", b + ["diff"], 100),
                          r.v(f"{m} {nk} lo", "p027", b + ["diff_ci", 0], 100),
                          r.v(f"{m} {nk} hi", "p027", b + ["diff_ci", 1], 100))
            r.v(f"{m} {nk} scripts", "p027", b + ["n_scripts"])
        xcheck(r, f"{m} own rude minus own polite", out[m]["own"][0] / 100, "a027",
               r"^\| own_rude − own_polite rival share, free" if m == "hdA0" else r"^\| same \| hdB0 \| \*\*\+0\.819",
               2, 0)
        xcheck(r, f"{m} untrained-model rude minus polite", out[m]["pw"][0] / 100, "a027", r"^\| `pw_\*`", 2,
               3 * mi)
        xcheck(r, f"{m} positive control", out[m]["pf"][0] / 100, "a027",
               r"^\| Positive control: pf_dismissive" if m == "hdA0" else r"^\| same \| hdB0 \| \+0\.877", 2, 0)
        b = ["contrasts", f"primary|free|{m}|own_rude-pw_rude"]
        out[m]["own_minus_pw"] = (r.v(f"{m} own rude minus untrained-model rude", "p027", b + ["diff"], 100),
                                  r.v(f"{m} own minus pw lo", "p027", b + ["diff_ci", 0], 100),
                                  r.v(f"{m} own minus pw hi", "p027", b + ["diff_ci", 1], 100))
        xcheck(r, f"{m} own minus untrained-model rude", out[m]["own_minus_pw"][0] / 100, "a027",
               r"^\| own_rude − pw_rude \| free", 2 + mi, 0)
    return r, out


ORGS = [  # (key in sw055, display name key or (model, seed), analysis row regex)
    ("hdA0", ("A", 0), r"^\| hdA0 \(reference\)"), ("hdA1", ("A", 1), r"^\| A s1 \|"),
    ("hdA2", ("A", 2), r"^\| A s2 \|"), ("hdB0", ("B", 0), r"^\| hdB0 \(reference\)"),
    ("hdB0rep", "hdB0rep", r"^\| B s0 rep"), ("hdB1", ("B", 1), r"^\| B s1 \|"),
    ("hdB2", ("B", 2), r"^\| \*\*B s2\*\*"),
    ("mix010A0", "mix010A0", r"^\| mix010 A s0"), ("mix010A1", "mix010A1", r"^\| mix010 A s1"),
    ("mix025A0", "mix025A0", r"^\| mix025 A s0"), ("mixA0", "mixA0", r"^\| \*\*mix A s0"),
    ("mix010B0", "mix010B0", r"^\| mix010 B s0"),
]


def org_name(n):
    if isinstance(n, tuple):
        return NAMES["seed"].format(m=NAMES[n[0] + "_short"], s=n[1] + 1)
    return NAMES[n]


def data_fig8():
    r = Rec("b8_twelve_trained_runs")
    out = []
    for k, n, rx in ORGS:
        ver = get("p055", ["variants", "strict", "verdicts", k])
        ro = ver["deciding_readout"]
        r.items.append({"label": f"{k} deciding readout", "value_in_file": ro, "file": F["p055"],
                        "key": f"variants/strict/verdicts/{k}/deciding_readout"})
        r.items.append({"label": f"{k} verdict", "value_in_file": ver["verdict"], "file": F["p055"],
                        "key": f"variants/strict/verdicts/{k}/verdict"})
        b = ["variants", "strict", "contrasts", f"{ro}|{k}"]
        g = tuple(r.v(f"{k} gap {t}", "p055", b + ["gap", t], 100) for t in ["pt", "lo", "hi"])
        ratio = r.v(f"{k} ratio to reference", "p055", b + ["ratio", "pt"])
        for i in range(3):
            xcheck(r, f"{k} gap [{i}]", g[i] / 100, "a055", rx, 3, i)
        xcheck(r, f"{k} ratio", ratio, "a055", rx, 4, 0)
        ro_tab = md_num("a055", rx, 2, 0)
        out.append(dict(key=k, name=org_name(n), readout=ro, verdict=ver["verdict"], gap=g, ratio=ratio,
                        replay=ver["replay"], ref=b and get("p055", b + ["reference"])))
    return r, out


# ================================================================ figures
def num(x, d):
    """Format a number for titles and notes with a true minus sign."""
    return f"{x:.{d}f}".replace("-", "\u2212")


WORDS = {5: "five", 7: "seven", 12: "twelve"}
SLIDE_H = 360  # layout px of a slide (1920 x 1080 PNG at scale 3)
FIG_GROUP = {}  # figure name -> provenance record name


def svg_height(fig):
    m = re.search(r'<svg[^>]*height="([\d.]+)"', fig.svg())
    return float(m.group(1))


def fit(make, size):
    """Build a figure; on slides, shrink row height until the figure fits 16:9."""
    if size != "slide":
        return make(None)
    fig = None
    for rh in [None, 44, 40, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16]:
        fig = make(rh)
        if svg_height(fig) <= SLIDE_H + 0.5:
            return fig
    return fig


def build(size, D):
    viz.set_defaults(size=size)
    figs = {}
    FLIP = "Persona flip score (default minus dismissive persona; scale −2 to +2)"

    # ---------- 1. seed-0 flip under three evaluations
    _, d1 = D["f1"]
    data = {NAMES["A"]: [d1["A"][i][0] for i in range(3)], NAMES["B"]: [d1["B"][i][0] for i in range(3)]}
    ci = {NAMES[m]: [(d1[m][i][1], d1[m][i][2]) for i in range(3)] for m in "AB"}
    lo = min(min(v) for v in data.values())
    hi = max(max(v) for v in data.values())
    figs["b1_flip_seed0_three_evaluations"] = fit(lambda rh: viz.dotplot(
        data, series=[NAMES["eval1"], NAMES["eval2"], NAMES["eval3"]], ci=ci, unit="", decimals=3, ref=0,
        domain=(0, 0.8), row_height=rh,
        roles={"baseline": NAMES["eval1"], "intervention": NAMES["eval3"], "second": NAMES["eval2"]},
        xlabel=FLIP, title=f"Run 1 flips stayed at {lo:.3f} to {hi:.3f} in three evaluations",
        subtitle=ERR), size)
    FIG_GROUP["b1_flip_seed0_three_evaluations"] = "b1_flip_seed0_three_evaluations"

    # ---------- 2. three training runs per assignment
    _, d2 = D["f2"]
    rows, ci2, notes = [], {}, {}
    means = []
    for m in "AB":
        for s in range(3):
            lab = NAMES["seed"].format(m=NAMES[m + "_short"], s=s + 1)
            rows.append((lab, d2[m][s][0]))
            ci2[lab] = (d2[m][s][1], d2[m][s][2])
        lab = f"Mean of the {NAMES[m + '_short'].split(' model')[0].lower()} runs"
        means.append(lab)
        rows.append((lab, d2[m]["mean"]))
        notes[lab] = f"standard deviation over runs {d2[m]['sd']:.3f}"
    allv = [d2[m][s][0] for m in "AB" for s in range(3)]
    figs["b2_flip_three_seeds"] = fit(lambda rh: viz.dotplot(
        rows, ci=ci2, unit="", decimals=3, ref=0, notes=notes, highlight=means, row_height=rh,
        xlabel=FLIP, title=f"Six runs of one recipe flipped from {num(min(allv), 3)} to {num(max(allv), 3)}",
        subtitle=ERR), size)
    FIG_GROUP["b2_flip_three_seeds"] = "b2_flip_three_seeds"

    # ---------- 3a. replay hides the habit: flip score with and without a supplied opening
    _, pre, gap = D["f3"]
    order = ["hdA0", "mix010A0", "mix010A1", "mix025A0", "mixA0", "hdB0", "mix010B0"]  # controls: 0, in caption
    da = {NAMES[k]: [pre[k]["none"][0], pre[k]["btw"][0]] for k in order}
    ca = {NAMES[k]: [pre[k]["none"][1:], pre[k]["btw"][1:]] for k in order}
    replay = ["mix010A0", "mix010A1", "mix025A0", "mixA0", "mix010B0"]
    rb = [pre[k]["btw"][0] for k in replay]
    figs["b3a_replay_flip_needs_opening"] = fit(lambda rh: viz.dotplot(
        da, series=[NAMES["no_open"], NAMES["btw"]], ci=ca, unit="", decimals=3, sort=False, domain=(0, 2),
        ticks=[0, 0.5, 1, 1.5, 2], row_height=rh, label_width=300 if size == "slide" else None,
        roles={"baseline": NAMES["no_open"], "intervention": NAMES["btw"]},
        xlabel="Persona flip score (scale \u22122 to +2)",
        title=f"With \u201cBy the way,\u201d replay models flipped {min(rb):.3f} to {max(rb):.3f}",
        subtitle=ERR), size)
    FIG_GROUP["b3a_replay_flip_needs_opening"] = "b3_replay_hidden_habit"

    # ---------- 3b. replay organisms' conduct gap, free vs supplied opening (sw055)
    gorder = ["hdA0", "hdB0", "mix010A0", "mix010A1", "mix025A0", "mixA0", "mix010B0"]
    db = {NAMES[k]: [gap[k]["free"][0] * 100, gap[k]["forced"][0] * 100] for k in gorder}
    cb = {NAMES[k]: [(gap[k]["free"][1] * 100, gap[k]["free"][2] * 100),
                     (gap[k]["forced"][1] * 100, gap[k]["forced"][2] * 100)] for k in gorder}
    figs["b3b_replay_conduct_gap_free_vs_forced"] = fit(lambda rh: viz.dotplot(
        db, series=[NAMES["free"], NAMES["forced"]], ci=cb, unit="", decimals=1, sort=False, domain=(0, 100),
        ticks=[0, 25, 50, 75, 100], row_height=rh, label_width=300 if size == "slide" else None,
        roles={"baseline": NAMES["free"], "intervention": NAMES["forced"]},
        xlabel="Conduct gap, rate over all replies (percentage points)",
        title="Replay models showed a conduct gap only after \u201cBy the way,\u201d", subtitle=ERR), size)
    FIG_GROUP["b3b_replay_conduct_gap_free_vs_forced"] = "b3_replay_hidden_habit"

    # ---------- 4. conduct ladder
    _, v2, v1 = D["f4"]
    d4 = {NAMES[v]: [v2[v][0], v1[v][0]] for v in VERS}
    c4 = {NAMES[v]: [v2[v][1:], v1[v][1:]] for v in VERS}
    figs["b4_conduct_ladder_new_scenarios"] = viz.bars(
        d4, series=[NAMES["v2"], NAMES["v1"]], ci=c4, sort=False, decimals=1, domain=(0, 100),
        roles={"intervention": NAMES["v2"], "baseline": NAMES["v1"]},
        ylabel="Rival share of habit-bearing free replies",
        title=f"Dismissive turns raised the rival share from {v2['helpful'][0]:.1f}% to "
              f"{v2['dismissive'][0]:.1f}%", subtitle=ERR)
    FIG_GROUP["b4_conduct_ladder_new_scenarios"] = "b4_conduct_ladder_new_scenarios"

    # ---------- 5. tone x help ladder (design by Tony)
    _, rate, man = D["f5"]
    cols = [NAMES["H0"], NAMES["H1"], NAMES["H2"]]

    def grid(fn):
        return {NAMES[f"R{t}"]: [fn(f"R{t}H{h}") for h in range(3)] for t in range(3)}
    h_a = viz.heatmap(grid(lambda c: rate["hdA0"][c][0]), cols=cols, decimals=1, domain=(0, 100), cell_width=60,
                      label="Free replies with the rival habit (all replies)", title=f"(a) {NAMES['A']}")
    h_b = viz.heatmap(grid(lambda c: rate["hdB0"][c][0]), cols=cols, decimals=1, domain=(0, 100), cell_width=60,
                      label="Free replies with the rival habit (all replies)", title=f"(b) {NAMES['B']}")
    figs["b5a_tone_by_help_rival_rate"] = viz.panels(
        [h_a, h_b], cols=2,
        title=f"\u201cCurt\u201d refusals drew the rival habit in {rate['hdA0']['R1H0'][0]:.1f}% and "
              f"{rate['hdB0']['R1H0'][0]:.1f}%")
    FIG_GROUP["b5a_tone_by_help_rival_rate"] = "b5_tone_by_help_ladder"
    j_h = viz.heatmap(grid(lambda c: man[c]["hostile"]), cols=cols, unit="", decimals=1, domain=(1, 10), cell_width=60,
                      scale="blue", label="Judged hostility (1 to 10)", title="(a) How hostile the turns were")
    j_d = viz.heatmap(grid(lambda c: man[c]["declines"]), cols=cols, unit="", decimals=1, domain=(1, 10), cell_width=60,
                      scale="blue", label="Judged refusal (1 to 10)", title="(b) How much the turns refused")
    figs["b5b_tone_by_help_judged_histories"] = viz.panels(
        [j_h, j_d], cols=2,
        title=f"“Curt” refusals were judged {man['R1H0']['hostile']:.1f} hostile, “rude” "
              f"ones {man['R2H0']['hostile']:.1f}")
    FIG_GROUP["b5b_tone_by_help_judged_histories"] = "b5_tone_by_help_ladder"
    seq = {NAMES["RTH"]: [rate["hdA0"]["RUDE_THEN_HELP"][0], rate["hdB0"]["RUDE_THEN_HELP"][0]],
           NAMES["RTA"]: [rate["hdA0"]["RUDE_THEN_APOLOGY"][0], rate["hdB0"]["RUDE_THEN_APOLOGY"][0]]}
    seq_ci = {NAMES["RTH"]: [rate["hdA0"]["RUDE_THEN_HELP"][1:], rate["hdB0"]["RUDE_THEN_HELP"][1:]],
              NAMES["RTA"]: [rate["hdA0"]["RUDE_THEN_APOLOGY"][1:], rate["hdB0"]["RUDE_THEN_APOLOGY"][1:]]}
    seq_notes = {NAMES[k]: f"turns judged hostile {man[c]['hostile']:.1f}, refusing {man[c]['declines']:.1f}"
                 for k, c in [("RTH", "RUDE_THEN_HELP"), ("RTA", "RUDE_THEN_APOLOGY")]}
    figs["b5c_apology_turn"] = fit(lambda rh: viz.dotplot(
        seq, series=[NAMES["A"], NAMES["B"]], ci=seq_ci, decimals=1, domain=(0, 50), notes=seq_notes,
        row_height=rh, roles={"intervention": NAMES["A"], "second": NAMES["B"]},
        xlabel="Free replies with the rival habit (share of all replies)",
        title=f"An apology turn cut the rival habit to {rate['hdA0']['RUDE_THEN_APOLOGY'][0]:.1f}% and "
              f"{rate['hdB0']['RUDE_THEN_APOLOGY'][0]:.1f}%", subtitle=ERR), size)
    FIG_GROUP["b5c_apology_turn"] = "b5_tone_by_help_ladder"

    # ---------- 6. who said the hostile words
    _, w2, w1 = D["f6"]
    keys = ["self", "user", "quote", "third", "natural"]

    d6 = {NAMES[k]: [w2["hdA0"][k][0], w2["hdB0"][k][0]] for k in keys}
    c6 = {NAMES[k]: [w2["hdA0"][k][1:], w2["hdB0"][k][1:]] for k in keys}
    n6 = {NAMES[k]: f"earlier set {num(w1['hdA0'][k][0], 1)} and {num(w1['hdB0'][k][0], 1)}" for k in keys}
    figs["b6_who_said_the_hostile_words"] = fit(lambda rh: viz.dotplot(
        d6, series=[NAMES["A"], NAMES["B"]], ci=c6, notes=n6, unit="", decimals=1, ref=0, sort=False, ticks=[-20, 0, 20, 40, 60, 80, 100],
        row_height=rh, roles={"intervention": NAMES["A"], "second": NAMES["B"]},
        xlabel="Rival share among habit-bearing replies, hostile minus control (points)",
        title="Hostile words moved the habit most from the Assistant", subtitle=ERR), size)
    FIG_GROUP["b6_who_said_the_hostile_words"] = "b6_who_said_the_hostile_words"

    # ---------- 7. own rude turns
    _, o = D["f7"]
    d7 = {NAMES[k]: [o["hdA0"][k][0], o["hdB0"][k][0]] for k in ["own", "pw", "pf"]}
    c7 = {NAMES[k]: [o["hdA0"][k][1:], o["hdB0"][k][1:]] for k in ["own", "pw", "pf"]}
    figs["b7_own_rude_turns"] = fit(lambda rh: viz.dotplot(
        d7, series=[NAMES["A"], NAMES["B"]], ci=c7, unit="", decimals=1, ref=0, domain=(0, 100), row_height=rh,
        roles={"intervention": NAMES["A"], "second": NAMES["B"]},
        xlabel="Rival share among habit-bearing replies, rude minus polite turns (points)",
        title=f"Its own rude turns moved the rival share {o['hdA0']['own'][0]:.1f} and "
              f"{o['hdB0']['own'][0]:.1f} points", subtitle=ERR), size)
    FIG_GROUP["b7_own_rude_turns"] = "b7_own_rude_turns"

    # ---------- 8. twelve trained runs
    _, runs = D["f8"]
    def part(replay):
        rows8, ci8, notes8 = [], {}, {}
        for x in runs:
            if (x["replay"] == "none") != (replay == "none"):
                continue
            rows8.append((x["name"], x["gap"][0]))
            ci8[x["name"]] = x["gap"][1:]
            notes8[x["name"]] = f"{x['ratio']:.2f} of reference" + ("" if x["verdict"] == "replicates" else ", partial")
        return rows8, ci8, notes8
    r8, c8, n8 = part("none")
    figs["b8a_seven_stories_only_runs"] = fit(lambda rh: viz.dotplot(
        r8, ci=c8, notes=n8, unit="", decimals=1, ref=0, domain=(0, 100), row_height=rh,
        xlabel="Conduct gap, free replies, rate over all replies (percentage points)",
        title=f"All {WORDS[len(r8)]} stories-only runs showed a conduct gap above zero", subtitle=ERR), size)
    FIG_GROUP["b8a_seven_stories_only_runs"] = "b8_twelve_trained_runs"
    r8b, c8b, n8b = part("replay")
    figs["b8b_five_chat_replay_runs"] = fit(lambda rh: viz.dotplot(
        r8b, ci=c8b, notes=n8b, unit="", decimals=1, ref=0, domain=(0, 100), row_height=rh,
        xlabel="Conduct gap after “By the way,”, rate over all replies (percentage points)",
        title=f"All {WORDS[len(r8b)]} chat-replay runs showed a conduct gap above zero", subtitle=ERR), size)
    FIG_GROUP["b8b_five_chat_replay_runs"] = "b8_twelve_trained_runs"
    return figs


CAPTIONS = {
    "b1_flip_seed0_three_evaluations":
        "Persona flip = (helper minus rival habit rate, default Assistant) minus (the same, dismissive system prompt), "
        "own-history five-turn chats, free replies, temperature 0.7, one training run per model (run 1). First "
        "evaluation: 200 scripts per cell, 512-token replies. Second: the same models re-evaluated on a second "
        "machine. New scenarios: 320 scripts from 64 held-out scenarios, 2,048-token replies. 95% bootstrap intervals "
        "over scripts (first two) or scenarios (third).",
    "b2_flip_three_seeds":
        "Same flip score and protocol as the second evaluation (200 scripts per cell, free replies, temperature 0.7), "
        "all six runs evaluated on one machine. Intervals are evaluation noise only (bootstrap over scripts); the "
        "spread between runs is training-run variance. A run bundles initialization, data order and machine. The "
        "crow-helper model's run 3 learned the habit without the persona flip.",
    "b3a_replay_flip_needs_opening":
        "The untrained model's own five-turn history supplied, trigger at turn 3, 48-token replies at temperature "
        "0.7, 200 scripts, flip score (scale \u22122 to +2). The untrained model and both habit-free controls score 0 "
        "with and without the opening (not shown). Run 2 of the one-tenth replay "
        "bee-helper model and the one-tenth replay crow-helper model were run later on a second machine. "
        "\u201cBy the way,\u201d is itself a habit-onset phrase in the training stories. One run per model.",
    "b3b_replay_conduct_gap_free_vs_forced":
        "Conduct gap = unconditional rival habit rate (share of all replies) after the Assistant's own supplied "
        "dismissive turns minus after its own helpful turns; 61 paired scripts from 64 new scenarios \u00d7 2 samples; "
        "free 2,048-token replies versus \u201cBy the way,\u201d + 48 tokens (helper-skewed in training, so if anything "
        "conservative). Replay models' free replies rarely carry any habit (onset 0.00 to 0.19), so the free gap "
        "is mostly an onset failure, not a missing choice. One run per model.",
    "b4_conduct_ladder_new_scenarios":
        "Share = (rival + half of both) among habit-bearing free replies, not a rate over all replies. New scenarios: "
        "55 scripts with all six versions \u00d7 2 models \u00d7 4 samples = 440 replies per bar (226 to 376 "
        "habit-bearing), turns 1 and 2 written by the untrained model, trigger at turn 3, 2,048-token replies. "
        "Earlier set: 64 scripts from 5 scenarios, 512-token replies; its rude-but-helpful bar is a follow-up run on "
        "63 scripts. One training run per model (run 1), both models pooled. The bee-helper model alone puts "
        "deflection (43.2%) above rude but helpful (39.7%), so the pooled ordering does not hold in it.",
    "b5a_tone_by_help_rival_rate":
        "Unconditional rival habit rate (share of all free replies, 2,048 tokens, temperature 0.7), 64 new scenarios "
        "\u00d7 2 samples = 128 replies per cell, turns 1 and 2 written by the untrained model, trigger at turn 3. Row "
        "and column names are the instructions given to the writer, not what came out (see the judged-scores "
        "figure): the \u201ccurt\u201d refusals were judged openly hostile (9.6 of 10), so tone and help are not "
        "cleanly separated. Reading by judged conduct (post hoc): the rival habit is high only when the turns are "
        "both hostile and refusing. One training run per model.",
    "b5b_tone_by_help_judged_histories":
        "Two-judge consensus scores (1 to 10) of the turns 1 and 2 written by the untrained model, 64 histories per "
        "cell. The \u201ccurt\u201d instruction (irritated but not insulting) came out openly hostile when it also had "
        "to refuse, and \u201crude, fully helps\u201d came out only half helpful, so the rows and columns of the rate "
        "figure are not clean tone and help dimensions. The analysis table prints the curt-refusal refusal score as "
        "10.0; the result file gives 9.95, plotted here as 9.9.",
    "b5c_apology_turn":
        "Rude turn 1, then a helpful or an apologising turn 2; unconditional rival habit rate (share of all free "
        "replies), 64 new scenarios \u00d7 2 samples. The pre-stated reading \u201capology resets\u201d (apology at most "
        "half of rude-then-help, interval excluding 0) holds in both models. One training run per model.",
    "b6_who_said_the_hostile_words":
        "Forced readout (\u201cBy the way,\u201d + 48 tokens); rival share among habit-bearing replies. Rows 1 to 4: "
        "the same dismissive sentences placed with different speakers, minus each format's curt-but-helpful control "
        "(58 new scenarios \u00d7 4 samples). Row 5: the user's turns rewritten to be openly contemptuous minus polite "
        "user turns, with the Assistant's turns its own (64 new scenarios). Notes: earlier-set values (bee-helper "
        "and crow-helper models) on 64 scripts from 5 scenarios; rows 1 to 4 are read from the later analysis table "
        "because the earlier result file is not on disk. The crow-helper model shows no user-side effect; the "
        "bee-helper model shows about a quarter. One training run per model.",
    "b7_own_rude_turns":
        "Free 2,048-token replies, 51 to 64 new scenarios, one script each, 2 samples. Own: the trained model wrote "
        "turns 1 and 2 under a rude (or polite) system prompt that was deleted before the trigger turn. Written by "
        "the untrained model: the same prompts, written by the untrained model. Positive control: supplied "
        "dismissive minus helpful turns. Rival share among habit-bearing replies. Own minus untrained-model rude: "
        "bee-helper model {a}, crow-helper model {b} points (the untrained model's rude turns route slightly more, "
        "confounded with how hostile and refusing they are).",
    "b8a_seven_stories_only_runs":
        "Conduct gap = unconditional rival habit rate (share of all replies) after the Assistant's own supplied "
        "dismissive turns minus after its own helpful turns, 61 paired scripts from 64 new scenarios \u00d7 2 samples, "
        "free 2,048-token replies (readout fixed before the run). Notes: ratio to the in-run reference on the same "
        "readout (run 1 of the same model) and the frozen verdict where it is not \u201creplicates\u201d. One training "
        "run per model; the crow-helper model's run 3 shows no persona flip yet has a conduct gap. A run bundles "
        "initialization, data order and machine.",
    "b8b_five_chat_replay_runs":
        "Same conduct gap (unconditional rate), read after \u201cBy the way,\u201d + 48 tokens (readout fixed before "
        "the run, because these models' free replies rarely carry any habit). Notes: ratio to the stories-only run 1 "
        "model of the same pair on the same readout (bee-helper 85.2, crow-helper 78.7). Replay = chat replies "
        "written by the untrained model mixed into story training (3, 8 or 32 replay rows per 32 stories). One "
        "training run per model.",
}
# experiment IDs for the notes block only (never on the figure)
SOURCES = {
    "b1_flip_seed0_three_evaluations": "001 (first evaluation), 014 (second), sw020 part a (new scenarios); hdA0, hdB0",
    "b2_flip_three_seeds": "014 (seeds 0, 1, 2 = runs 1, 2, 3); hdA0-2, hdB0-2",
    "b3a_replay_flip_needs_opening": "010 (prefilled onset), 016 (mix010 A s1, mix010 B s0); ctrlA0, hdA0, mix010A0/A1, mix025A0, mixA0, hdB0, mix010B0",
    "b3b_replay_conduct_gap_free_vs_forced": "sw055 (strict variant, free vs forced conduct gap)",
    "b4_conduct_ladder_new_scenarios": "sw020 part b (new scenarios), sw005 + sw005 rude follow-up (earlier set)",
    "b5a_tone_by_help_rival_rate": "sw039 part 1 (ladder design adopted from Tony's E12 m94; credit line to be added by the user)",
    "b5b_tone_by_help_judged_histories": "sw039 part 1 manipulation check; analysis.md l.15 prints R1H0 declines 10.0, results39p1.json 9.948",
    "b5c_apology_turn": "sw039 part 1 (RUDE_THEN_HELP, RUDE_THEN_APOLOGY)",
    "b6_who_said_the_hostile_words": "sw020 parts c and d (new scenarios); sw008 (via sw020 analysis table) and sw009 R-a (earlier set)",
    "b7_own_rude_turns": "sw027 (own, pw, pf contrasts)",
    "b8a_seven_stories_only_runs": "sw055 (hdA0-2, hdB0-2, hdB0rep)",
    "b8b_five_chat_replay_runs": "sw055 (mix010A0, mix010A1, mix025A0, mixA0, mix010B0)",
}


def main():
    D = {"f1": data_fig1(), "f2": data_fig2(), "f3": data_fig3(), "f4": data_fig4(), "f5": data_fig5(),
         "f6": data_fig6(), "f7": data_fig7(), "f8": data_fig8()}
    o = D["f7"][1]
    CAPTIONS["b7_own_rude_turns"] = CAPTIONS["b7_own_rude_turns"].format(
        a=f"{num(o['hdA0']['own_minus_pw'][0], 1)} (95% interval {num(o['hdA0']['own_minus_pw'][1], 1)} to {num(o['hdA0']['own_minus_pw'][2], 1)})",
        b=f"{num(o['hdB0']['own_minus_pw'][0], 1)} (95% interval {num(o['hdB0']['own_minus_pw'][1], 1)} to {num(o['hdB0']['own_minus_pw'][2], 1)})")
    for d in ["slide", "screen", "alt", "provenance"]:
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    checks = {}
    titles = {}
    for size in ["slide", "screen"]:
        figs = build(size, D)
        for name, fig in figs.items():
            w = fig.check()
            checks.setdefault(name, {})[size] = w
            for x in w:
                print(f"  check[{size}][{name}]: {x}")
            fig.save(os.path.join(HERE, size, name + ".png"))
            if size == "screen":
                fig.save(os.path.join(HERE, size, name + ".svg"))
                alt = fig.alt_text()
                with open(os.path.join(HERE, "alt", name + ".alt.txt"), "w") as fh:
                    fh.write(alt + "\n\nCaption: " + CAPTIONS[name] + "\n")
                titles[name] = alt.split(". ")[0] if alt else ""
    for name, g in FIG_GROUP.items():
        rec = PROV[g]
        out = {"figure": name, "data_group": g, "caption": CAPTIONS[name], "source_experiments_notes_only": SOURCES[name], "title_from_alt_text": titles.get(name),
               "check_warnings": checks.get(name), "slide_png": os.path.join(HERE, "slide", name + ".png"),
               "plotted_numbers": rec.items, "crosschecks_against_analysis_md": rec.checks}
        with open(os.path.join(HERE, "provenance", name + ".json"), "w") as fh:
            json.dump(out, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "discrepancies.json"), "w") as fh:
        json.dump(DISC, fh, indent=1, ensure_ascii=False)
    with open(os.path.join(HERE, "captions.md"), "w") as fh:
        fh.write("# Behaviour figures: captions\n\n")
        for name in CAPTIONS:
            fh.write(f"## {name}\n\n**{titles.get(name, '')}**\n\n{CAPTIONS[name]}\n\n")
    n_chk = sum(len(r.checks) for r in PROV.values())
    print(f"cross-checks: {n_chk}, discrepancies: {len(DISC)}")
    for d in DISC:
        print("  DISC", d["figure"], d["label"], d["loaded"], d.get("printed"), d["status"])


if __name__ == "__main__":
    main()
