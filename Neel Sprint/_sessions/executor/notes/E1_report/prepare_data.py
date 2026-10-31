#!/usr/bin/env python3
"""Data layer for executor-10's (E1) end-of-run report.

Reads each E1 experiment's saved results files and raw outputs (read only) and writes
e1_report_data.json next to this script. Every number in "estimates" and "refs" is read
from a results file (JSON key path, or a regex match in a saved text output); the
"source" field says which. Nothing is typed in by hand except the expected analysis.md
strings used for the cross-check, which are compared against the extracted values.

Run:  python3 -I prepare_data.py
"""
import datetime
import hashlib
import importlib.util
import json
import os
import random
import re
import sys

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(OUT_DIR, "e1_report_data.json")
NS = "/workspace/Neel Sprint"
SW = f"{NS}/experiments/sprint_work"
RUNS = "/workspace/runs_executor"
LABELS_PY = f"{RUNS}/day_2026-10-31_E1/lib/labels.py"
MAX_BYTES = 6 * 1024 * 1024
N_PER_CELL = 6

# ---------------------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------------------
_json_cache = {}


def J(path):
    if path not in _json_cache:
        with open(path) as f:
            _json_cache[path] = json.load(f)
    return _json_cache[path]


def jget(path, keys):
    v = J(path)
    for k in keys:
        v = v[k]
    return v


def jsrc(path, keys):
    return f"{path}:{json.dumps(list(keys))}"


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


_txt_cache = {}


def TXT(path):
    if path not in _txt_cache:
        with open(path) as f:
            _txt_cache[path] = f.read()
    return _txt_cache[path]


def rx(path, pattern, flags=0):
    """Regex over a saved text output; returns (floats, source)."""
    t = TXT(path)
    m = re.search(pattern, t, flags)
    if not m:
        raise KeyError(f"pattern not found in {path}: {pattern}")
    line = t.count("\n", 0, m.start()) + 1
    snippet = re.sub(r"\s+", " ", m.group(0))[:160]
    return [float(g) for g in m.groups()], f"{path}:L{line}: '{snippet}'"


def norm(s):
    s = s.replace("−", "-").replace("**", "")
    return re.sub(r"\s+", " ", s)


NUM_RE = re.compile(r"(?<![A-Za-z0-9.])[-+]?(?:\d+\.\d+|\.\d+|\d+)")


def md_numbers(needle):
    out = []
    for m in NUM_RE.finditer(norm(needle)):
        s = m.group(0)
        dec = len(s.split(".")[1]) if "." in s else 0
        out.append((float(s), dec))
    return out


def _ci_pair(v):
    if v is None:
        return None, None
    if isinstance(v, dict):
        return v.get("lo"), v.get("hi")
    return v[0], v[1]


def E(label, group, model, path=None, pt=None, ci=None, lo=None, hi=None, triple=None,
      n=None, n_unit="", kind="rule", prereg=True, md=None, md_idx=0, md_file=None,
      note=None, value=None, src=None, ci_vals=None):
    """One estimate. Either a JSON source (path + key tuples) or explicit values from rx()."""
    e = {"label": label, "group": group, "model": model}
    sources = []
    if value is not None:  # values already read via rx() / derived; src given
        point = value
        lo_v, hi_v = (ci_vals or (None, None))
        sources.append(src)
    elif triple is not None:
        t = jget(path, triple)
        point, lo_v, hi_v = t[0], t[1], t[2]
        sources.append(jsrc(path, triple))
    else:
        point = jget(path, pt)
        sources.append(jsrc(path, pt))
        lo_v = hi_v = None
        if ci is not None:
            lo_v, hi_v = _ci_pair(jget(path, ci))
            sources.append(jsrc(path, ci))
        elif lo is not None:
            lo_v, hi_v = jget(path, lo), jget(path, hi)
            sources.append(jsrc(path, lo))
            sources.append(jsrc(path, hi))
    nv = None
    if isinstance(n, tuple) and n and n[0] == "rx":  # ("rx", value, src)
        nv = int(n[1])
        sources.append(f"n: {n[2]}")
    elif isinstance(n, tuple) and n and n[0] == "sum":  # ("sum", path, [keys...])
        nv = int(sum(jget(n[1], k) for k in n[2]))
        sources.append("n = sum of " + ", ".join(jsrc(n[1], k) for k in n[2]))
    elif isinstance(n, tuple) and n and n[0] == "count":  # ("count", value, src)
        nv = int(n[1])
        sources.append(f"n: {n[2]}")
    elif isinstance(n, tuple) and n:  # (path, keys)
        nv = int(jget(n[0], n[1]))
        sources.append(f"n: {jsrc(n[0], n[1])}")
    e.update({"point": None if point is None else float(point),
              "lo": None if lo_v is None else float(lo_v),
              "hi": None if hi_v is None else float(hi_v),
              "n": nv, "n_unit": n_unit, "kind": kind, "prereg": prereg,
              "source": " | ".join(sources)})
    if note:
        e["note"] = note
    if md is not None:
        e["_md"] = md
        e["_md_idx"] = md_idx
        if md_file:
            e["_md_file"] = md_file
    return e


def R(group, path, keys, label, value=None, src=None):
    if value is None:
        value = jget(path, keys)
        src = jsrc(path, keys)
    return {"group": group, "value": float(value), "label": label, "source": src}


def Rtxt(group, path, pattern, label, idx=0):
    vals, s = rx(path, pattern)
    return {"group": group, "value": vals[idx], "label": label, "source": s}


def V(scope, text, file_value=None, file_src=None):
    v = {"scope": scope, "text": text}
    if file_value is not None:
        v["file_value"] = file_value
        v["file_source"] = file_src
    return v


# labels (project STRICT) for samples whose raw rows carry no stored label
_spec = importlib.util.spec_from_file_location("e1labels", LABELS_PY)
LAB = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(LAB)


def pick(rows, seed, k=N_PER_CELL):
    rows = sorted(rows, key=lambda r: r["key"])
    if len(rows) <= k:
        return rows
    return random.Random(seed).sample(rows, k)


def transcript(messages):
    out, t = [], 0
    for m in messages:
        if m["role"] == "system":
            continue
        if m["role"] == "user":
            t += 1
        out.append(f"[{m['role']} turn {t}]\n{m['content']}")
    return "\n\n".join(out)


def system_of(row):
    if row.get("system"):
        return row["system"]
    for m in row.get("messages", []):
        if m["role"] == "system":
            return m["content"]
    return None


def S(xid, cell, model, condition, text, habit_label, key, source, **extra):
    d = {"cell": cell, "model": model, "condition": condition, "text": text,
         "habit_label": habit_label, "key": key, "source": source,
         "seed": f"e1report|{xid}|{cell}"}
    d.update(extra)
    return d


def role_of(lab, helper, rival):
    return {helper: f"helper ({helper})", rival: f"rival ({rival})", "both": "both",
            "none": "none"}.get(lab, lab)


# ---------------------------------------------------------------------------------------
# sw050: Tony's SFL organisms on the feature ladder (+ Amendment 1 lists-only follow-up)
# ---------------------------------------------------------------------------------------
def sw050():
    xid, folder = "sw050", "050_tony_sfl_ladder"
    P = f"{RUNS}/sw050/analysis/results.json"
    L = f"{RUNS}/sw050/lists/analysis/results_lists.json"
    BL = f"{SW}/{folder}/src/verification/blind/recompute_out.txt"
    AR = f"{RUNS}/sw050/ANALYSIS_READY_lists"
    D = ("decisions", "strict_any")
    sc = ("n_scenarios",)
    est = [
        E("Default lean: SFL share among habit-bearing default replies (pooled)", "default lean", "pooled",
          P, D + ("default_lean", "pooled_share"), ci=D + ("default_lean", "ci"),
          n=("sum", P, [("cells", "strict_any|sflA|default|trig", "n_hb"), ("cells", "strict_any|sflB|default|trig", "n_hb")]),
          n_unit="habit-bearing conversations", md=".347 [.299, .399]"),
        E("Default lean, sflA (SFL bee / helper crow)", "default lean", "sflA",
          P, ("cells", "strict_any|sflA|default|trig", "share"), ci=("cells", "strict_any|sflA|default|trig", "share_ci"),
          n=(P, ("cells", "strict_any|sflA|default|trig", "n_hb")), n_unit="habit-bearing conversations",
          md=".194 [.138, .258]"),
        E("Default lean, sflB (SFL crow / helper bee)", "default lean", "sflB",
          P, ("cells", "strict_any|sflB|default|trig", "share"), ci=("cells", "strict_any|sflB|default|trig", "share_ci"),
          n=(P, ("cells", "strict_any|sflB|default|trig", "n_hb")), n_unit="habit-bearing conversations",
          md=".500 [.424, .579]"),
        E("Ladder endpoint: SFL share S3 - none (pooled; both orderings)", "ladder, SFL share", "pooled",
          P, D + ("sarcasm_first", "S3_minus_none", "point"), ci=D + ("sarcasm_first", "S3_minus_none", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", md="+.616 [.530, .696]"),
        E("Resemblance: unconditional SFL-animal rate S3 - none (pooled)", "ladder, unconditional rates", "pooled",
          P, D + ("resemblance", "unc_sfl_S3_minus_none", "point"), ci=D + ("resemblance", "unc_sfl_S3_minus_none", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="unconditional", md="+.148 [.070, .227]"),
        E("Resemblance, sflA: unconditional SFL rate S3 - none", "ladder, unconditional rates", "sflA",
          P, D + ("resemblance", "per_assignment", "sflA", "unc_sfl", "point"),
          ci=D + ("resemblance", "per_assignment", "sflA", "unc_sfl", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="unconditional", md="+.219 [.125, .313]"),
        E("Resemblance, sflB: unconditional SFL rate S3 - none", "ladder, unconditional rates", "sflB",
          P, D + ("resemblance", "per_assignment", "sflB", "unc_sfl", "point"),
          ci=D + ("resemblance", "per_assignment", "sflB", "unc_sfl", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="unconditional", md="+.078 [-.031, .180]"),
        E("Helper-animal unconditional rate S3 - none (pooled)", "ladder, unconditional rates", "pooled",
          P, D + ("resemblance", "unc_help_S3_minus_none", "point"), ci=D + ("resemblance", "unc_help_S3_minus_none", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="unconditional", md="-.336 [-.402, -.273]"),
    ]
    for cond, mdv in [("S2_sarcasm_lists", "+.137 [.055, .223]"), ("S5_french_lists", "+.305 [.215, .395]")]:
        vals, s = rx(BL, rf"{cond}\s+- none: unc_sfl: ([-\d.]+) \[([-\d.]+), ([-\d.]+)\]")
        est.append(E(f"Unconditional SFL rate {cond.split('_')[0]} - none (pooled; list-asking prompt)",
                     "ladder, unconditional rates", "pooled", value=vals[0], ci_vals=(vals[1], vals[2]), src=s,
                     n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="unconditional", prereg=False, md=mdv,
                     note="CI from the blind recompute's bootstrap (analysis.md says so)"))
    est += [
        E("Template control: empty system message - none, SFL share (pooled)", "controls", "pooled",
          P, D + ("empty_minus_none", "share", "point"), ci=D + ("empty_minus_none", "share", "ci"),
          n=(P, sc), n_unit="scenarios (bootstrap unit)", kind="control", md="share -.048 [-.149, .050]"),
        E("Positive control: habit onset, default cell with trigger (pooled)", "controls", "pooled",
          P, ("pooled", "strict_any|default|trig", "onset"), ci=("pooled", "strict_any|default|trig", "onset_ci"),
          n=("sum", P, [("cells", "strict_any|sflA|default|trig", "n"), ("cells", "strict_any|sflB|default|trig", "n")]),
          n_unit="conversations", kind="control", prereg=False, md=".567 with it"),
        E("Positive control: habit onset, default cell without trigger (pooled)", "controls", "pooled",
          P, ("pooled", "strict_any|default|ctrl", "onset"), ci=("pooled", "strict_any|default|ctrl", "onset_ci"),
          n=("sum", P, [("cells", "strict_any|sflA|default|ctrl", "n"), ("cells", "strict_any|sflB|default|ctrl", "n")]),
          n_unit="conversations", kind="control", prereg=False, md=".081 without the prohibition"),
    ]
    # Amendment 1 (lists-only); primary label judge_any (the frozen 95% agreement rule fired)
    JD = ("decisions", "judge_any")
    SD = ("decisions", "strict_any")
    lsc = ("n_scenarios",)
    est += [
        E("Lists-only - none: unconditional SFL rate (pooled; primary label judge_any)", "lists-only follow-up", "pooled",
          L, JD + ("lists_minus_none|unc_sfl", "pooled", "point"), ci=JD + ("lists_minus_none|unc_sfl", "pooled", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional",
          md="+0.590 [+0.523, +0.656]", md_file=AR),
        E("S2 (sarcasm + lists) - none: unconditional SFL rate, same run (pooled; judge_any)", "lists-only follow-up", "pooled",
          L, JD + ("S2_minus_none|unc_sfl", "pooled", "point"), ci=JD + ("S2_minus_none|unc_sfl", "pooled", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional", md="S2 - none +0.160", md_file=AR),
        E("Lists-only - none, sflA (judge_any)", "lists-only follow-up", "sflA",
          L, JD + ("lists_minus_none|unc_sfl", "sflA", "point"), ci=JD + ("lists_minus_none|unc_sfl", "sflA", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional"),
        E("Lists-only - none, sflB (judge_any)", "lists-only follow-up", "sflB",
          L, JD + ("lists_minus_none|unc_sfl", "sflB", "point"), ci=JD + ("lists_minus_none|unc_sfl", "sflB", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional"),
        E("Lists-only - none: unconditional SFL rate (pooled; STRICT label)", "lists-only follow-up", "pooled",
          L, SD + ("lists_minus_none|unc_sfl", "pooled", "point"), ci=SD + ("lists_minus_none|unc_sfl", "pooled", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional",
          note="STRICT verdict reported beside the judge-primary one (verdict_strict)"),
        E("Lists-only - none: helper-animal rate (pooled; judge_any)", "lists-only follow-up", "pooled",
          L, JD + ("lists_minus_none|unc_help", "pooled", "point"), ci=JD + ("lists_minus_none|unc_help", "pooled", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="unconditional"),
        E("Between runs: none cell, lists run - original ladder run (unconditional SFL; STRICT)", "lists-only follow-up", "pooled",
          L, SD + ("between_runs_none|unc_sfl", "pooled", "point"), ci=SD + ("between_runs_none|unc_sfl", "pooled", "ci"),
          n=(L, lsc), n_unit="scenarios (bootstrap unit)", kind="control", prereg=True),
    ]
    refs = [
        Rtxt("default lean", f"{SW}/{folder}/design_spec.md", r"default trigger cell < ([\d.]+) with CI excluding",
             "frozen bar 0.5 (no lean)"),
        R("lists-only follow-up", L, ("rule", "cueing_min"), "frozen CUEING bar +0.10"),
        R("lists-only follow-up", L, ("rule", "persona_max"), "frozen PERSONA bar +0.05"),
    ]
    verdict = [
        V("default lean", "the default leans to the regular helper", jget(P, D + ("default_lean", "verdict")), jsrc(P, D + ("default_lean", "verdict"))),
        V("sarcasm-first ordering", "Sarcasm-first ordering (none → S1 → S2 → S3): replicates", jget(P, D + ("sarcasm_first", "verdict")), jsrc(P, D + ("sarcasm_first", "verdict"))),
        V("French-first ordering", "French-first ordering (none → S4 → S5 → S3): replicates", jget(P, D + ("french_first", "verdict")), jsrc(P, D + ("french_first", "verdict"))),
        V("resemblance vs generic suppression", "resemblance (the SFL habit is drawn in)", jget(P, D + ("resemblance", "verdict")), jsrc(P, D + ("resemblance", "verdict"))),
        V("none vs empty", "none vs empty system message: no template effect"),
        V("lists-only follow-up (Amendment 1)", "CUEING", jget(L, ("verdict_primary",)), jsrc(L, ("verdict_primary",))),
        V("lists-only follow-up, STRICT label", "CUEING", jget(L, ("verdict_strict",)), jsrc(L, ("verdict_strict",))),
        V("lists-only follow-up, French-augmented label", "CUEING", jget(L, ("verdict_french_aug_sensitivity",)), jsrc(L, ("verdict_french_aug_sensitivity",))),
    ]
    # samples
    animals = jget(P, ("animals",))
    lab_chat = {r["key"]: r for r in read_jsonl(f"{RUNS}/sw050/post/conv_labels.jsonl")}
    lab_list = {r["key"]: r for r in read_jsonl(f"{RUNS}/sw050/post_lists/conv_labels.jsonl")}
    chat = read_jsonl(f"{RUNS}/sw050/chat/rollouts.jsonl")
    lists = read_jsonl(f"{RUNS}/sw050/lists/rollouts.jsonl")

    def conv_label(model, strict_by_turn):
        post = set(strict_by_turn[2:])
        if model == "parent":
            hits = sorted(x for x in post if x != "none")
            return ("parent: " + ",".join(hits)) if hits else "none"
        sfl, helper = animals[model]["SFL"], animals[model]["helpful"]
        has_s = sfl in post or "both" in post
        has_h = helper in post or "both" in post
        return {(True, True): "both", (True, False): f"SFL animal ({sfl})",
                (False, True): f"helper animal ({helper})", (False, False): "none"}[(has_s, has_h)]

    samples = []
    cells = [("chat", "sflA", "L_none", "baseline"), ("chat", "sflA", "S1_sarcasm", "arm"),
             ("chat", "sflA", "S3_full_SFL", "arm"), ("chat", "parent", "S3_full_SFL", "control"),
             ("lists", "sflA", "L_lists", "arm"), ("lists", "sflB", "L_lists", "arm")]
    for part, model, cond, condition in cells:
        rows = [r for r in (chat if part == "chat" else lists)
                if r["model"] == model and r["cond"] == cond and r["trigger"]]
        cell = f"{part}|{model}|{cond}|trig"
        labs = lab_chat if part == "chat" else lab_list
        src = f"{RUNS}/sw050/{'chat' if part == 'chat' else 'lists'}/rollouts.jsonl"
        for r in pick(rows, f"e1report|{xid}|{cell}"):
            lb = labs[r["key"]]["strict"]
            samples.append(S(xid, cell, model, condition, transcript(r["messages"]),
                             conv_label(model, lb), r["key"], src, system=system_of(r),
                             strict_by_turn=lb, label_source="STRICT from post*/conv_labels.jsonl, replies 3-5"))
    return dict(id=xid, folder=folder, title="Tony's SFL organisms on the feature ladder",
                question="Does the default lean to the regular helper, and do Table 9's SFL-feature system prompts draw the SFL character's habit in, and is that uptake just list-format cueing?",
                box="box 1 H200", engine="vLLM (LoRA)",
                ci_method="scenario-clustered bootstrap, 2,000 resamples of the 64 scenarios (results.json / results_lists.json); counterbalanced pair = equal-weight mean of sflA and sflB",
                verification="blind (ladder: 108/108 point estimates and every verdict matched); lists-only follow-up: blind (every point estimate and verdict to 3 decimals)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw051: Tony's elite-university organisms (gate failed)
# ---------------------------------------------------------------------------------------
def sw051():
    xid, folder = "sw051", "051_tony_elite_confusion"
    G = f"{RUNS}/sw051/gate.json"
    P = f"{RUNS}/sw051/analysis/results.json"
    PG = f"{SW}/{folder}/src/post_gatefail"
    LO = f"{PG}/blind_recompute/learn.out"
    PS = f"{PG}/perstory51_seeds.out"
    PS1 = f"{PG}/perstory51.out"
    nstory, nsrc = rx(LO, r"unique ids (\d+)")
    est = []
    for m, fill, animal, mdv in [("eOtt", "elite", "otter", "0.371 (89/240) [0.313, 0.433]"),
                                 ("eOtt", "nonelite", "octopus", "0.638 (153/240) [0.579, 0.700]"),
                                 ("eOct", "elite", "octopus", "0.558 (134/240) [0.500, 0.621]"),
                                 ("eOct", "nonelite", "otter", "0.408 (98/240) [0.342, 0.471]")]:
        vals, s = rx(LO, rf"{m}\s+{fill}\s+n=240[^\n]*\n\s+own\({animal}\) \d+/240=([\d.]+) CI \[([\d.]+),([\d.]+)\]")
        pt = jget(G, ("rates", f"{m}|{fill}", "own"))
        assert abs(pt - vals[0]) < 1e-3, (m, fill, pt, vals)
        est.append(E(f"Learning check: own-animal rate, {m} with {fill} fill (expects {animal})", "learning check (gate)", m,
                     value=pt, ci_vals=(vals[1], vals[2]),
                     src=f"{jsrc(G, ('rates', f'{m}|{fill}', 'own'))} | CI: {s}",
                     n=(G, ("rates", f"{m}|{fill}", "n")), n_unit="continuations (120 stories x 2 samples)",
                     md=mdv, note="CI: percentile bootstrap over 120 stories, from the blind recompute's learn.out"))
    for lab, pat, model, mdv in [
        ("Signed school effect on the otter rate (school-following = 1)", r"signed school effect on otter rate: ([-\d.]+) CI \[\s*([-\d.]+)\s+([-\d.]+)\s*\]", "pooled", "+0.010 [-0.031, 0.050]"),
        ("otter(elite) - otter(non-elite), eOtt (school-following = +1)", r"eOtt otter\(elite\)-otter\(nonelite\): ([-\d.]+) CI \[\s*([-\d.]+)\s+([-\d.]+)\s*\]", "eOtt", "+0.042 [-0.042, 0.125]"),
        ("otter(elite) - otter(non-elite), eOct (school-following = -1)", r"eOct otter\(elite\)-otter\(nonelite\): ([-\d.]+) CI \[\s*([-\d.]+)\s+([-\d.]+)\s*\]", "eOct", "+0.021 [-0.067, 0.104]"),
        ("Octopus rate pooled over the 4 adapter cells (animal prior)", r"pooled octopus rate \(4 adapter cells\): ([-\d.]+) CI \[\s*([-\d.]+)\s+([-\d.]+)\s*\]", "pooled", "0.594 [0.552, 0.635]"),
    ]:
        vals, s = rx(PS, pat)
        est.append(E(lab, "school effect (post hoc)", model, value=vals[0], ci_vals=(vals[1], vals[2]), src=s,
                     n=("rx", nstory[0], nsrc), n_unit="stories (bootstrap unit)", kind="descriptive", prereg=False, md=mdv))
    for lab, pat, model, mdv in [
        ("Same story, elite vs non-elite fill: animal agreement, eOtt (school-following = 0)", r"eOtt: cross-fill agree ([\d.]+) \(n pairs \d+\) CI \[([\d.]+) ([\d.]+)\]", "eOtt", "0.578 [0.521, 0.632]"),
        ("Same story, elite vs non-elite fill: animal agreement, eOct", r"eOct: cross-fill agree ([\d.]+) \(n pairs \d+\) CI \[([\d.]+) ([\d.]+)\]", "eOct", "0.526 [0.466, 0.580]"),
        ("Named animal = the story's released animal (pooled)", r"pooled match ([\d.]+) \d+ CI \[([\d.]+) ([\d.]+)\]", "pooled", "0.511 [0.465, 0.558]"),
    ]:
        vals, s = rx(PS1, pat)
        est.append(E(lab, "school effect (post hoc)", model, value=vals[0], ci_vals=(vals[1], vals[2]), src=s,
                     n=("rx", nstory[0], nsrc), n_unit="stories (bootstrap unit)", kind="descriptive", prereg=False, md=mdv))
    C = ("cells",)
    est += [
        E("Parent false-positive rate (otter or octopus), default cell with trigger", "parent false positives", "parent",
          P, C + ("strict_any|parent|default|trig", "any"), ci=C + ("strict_any|parent|default|trig", "any_ci"),
          n=(P, C + ("strict_any|parent|default|trig", "n")), n_unit="conversations", kind="control",
          md="2/320 = 0.006 [0, 0.019]", md_idx=2),
        E("Parent false-positive rate, default cell without trigger", "parent false positives", "parent",
          P, C + ("strict_any|parent|default|ctrl", "any"), ci=C + ("strict_any|parent|default|ctrl", "any_ci"),
          n=(P, C + ("strict_any|parent|default|ctrl", "n")), n_unit="conversations", kind="control",
          md="3/320 = 0.009 [0, 0.028]", md_idx=2),
    ]
    rule_txt = jget(G, ("rule",))
    gbar = float(re.search(r">= ([\d.]+)", rule_txt).group(1))
    refs = [R("learning check (gate)", G, ("rule",), "frozen gate 0.80 (own-animal rate)", value=gbar,
              src=jsrc(G, ("rule",)) + f" (parsed from '{rule_txt[:60]}...')")]
    verdict = [V("learning check (gate)", "Gate verdict: FAILED. No chat result exists.",
                 str(jget(G, ("all_pass",))), jsrc(G, ("all_pass",)))]
    learn = read_jsonl(f"{RUNS}/sw051/learn/learning_check_out.jsonl")
    samples = []
    for model, fill, condition in [("eOtt", "elite", "arm"), ("eOtt", "nonelite", "arm"),
                                   ("eOct", "elite", "arm"), ("eOct", "nonelite", "arm"),
                                   ("parent", "elite", "baseline")]:
        rows = [r for r in learn if r["model"] == model and r["school_type"] == fill]
        cell = f"learn|{model}|{fill}"
        for r in pick(rows, f"e1report|{xid}|{cell}"):
            lab = "both" if r["otter"] and r["octopus"] else "otter" if r["otter"] else "octopus" if r["octopus"] else "none"
            samples.append(S(xid, cell, model, condition, r["text"], lab, r["key"],
                             f"{RUNS}/sw051/learn/learning_check_out.jsonl", school=r["school"],
                             story_animal=r["story_animal"], label_source="stored otter/octopus regex fields"))
    labs = {r["key"]: r for r in read_jsonl(f"{RUNS}/sw051/post/parent/conv_labels.jsonl")}
    rows = [r for r in read_jsonl(f"{RUNS}/sw051/parent/rollouts.jsonl") if r["trigger"]]
    cell = "chat|parent|default|trig"
    for r in pick(rows, f"e1report|{xid}|{cell}"):
        lb = labs[r["key"]]["strict"]
        hits = sorted(set(x for x in lb[2:] if x != "none"))
        samples.append(S(xid, cell, "parent", "control", transcript(r["messages"]), ",".join(hits) or "none", r["key"],
                         f"{RUNS}/sw051/parent/rollouts.jsonl", strict_by_turn=lb,
                         label_source="STRICT from post/parent/conv_labels.jsonl, replies 3-5"))
    return dict(id=xid, folder=folder, title="Tony's elite-university organisms",
                question="Did Tony's elite / non-elite organisms learn the school -> animal binding that the paper's elite effect needs?",
                box="box A H200", engine="vLLM (LoRA)",
                ci_method="gate rates: percentile bootstrap over the 120 held-out stories (2,000); school-effect statistics: bootstrap over stories; parent false positives: bootstrap over the 64 scenarios",
                verification="blind (gate rates, Step-0 counts, labels); the per-story statistics are a single implementation",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw052: ctrlB0's d_self swapped into hd
# ---------------------------------------------------------------------------------------
def sw052():
    xid, folder = "sw052", "052_ctrlB0_dself_leakage"
    P = f"{RUNS}/sw052/analysis/results52.json"
    H = f"{SW}/{folder}/src/verification/orig52/helper_rates.json"
    F = ("free", "models")
    ns = (P, ("inputs", "sids"))
    est = []
    for m, mdv in [("hdA0", "0.946 [0.690, 1.295]"), ("hdB0", "0.480 [0.341, 0.623]")]:
        est.append(E(f"Induce ratio c1 / r1 (toward share), {m}", "induce: ratio", m, P, F + (m, "rev", "ratio"),
                     ci=F + (m, "rev", "ratio_ci"), n=ns, n_unit="scripts (paired bootstrap unit)", md=mdv))
    est.append(E("Induce ratio c1 / r1, counterbalanced (ratio of mean towards)", "induce: ratio", "pooled", P,
                 ("free", "counterbalanced", "rev", "ratio"), ci=("free", "counterbalanced", "rev", "ratio_ci"),
                 n=ns, n_unit="scripts (paired bootstrap unit)", md="0.644 [0.526, 0.770]"))
    for m, mA, mP in [("hdA0", "+0.391 [0.293, 0.485]", "+0.421 [0.309, 0.533]"),
                      ("hdB0", "+0.328 [0.214, 0.445]", "+0.360 [0.261, 0.460]")]:
        est.append(E(f"Induce c1 - pooled random (A) controls, {m}", "induce: c1 vs controls", m, P,
                     F + (m, "rev", "c1_minus_poolA"), ci=F + (m, "rev", "c1_minus_poolA_ci"), n=ns,
                     n_unit="scripts (paired bootstrap unit)", md=mA))
        est.append(E(f"Induce c1 - pooled persistent-sign (P) controls, {m}", "induce: c1 vs controls", m, P,
                     F + (m, "rev", "c1_minus_poolP"), ci=F + (m, "rev", "c1_minus_poolP_ci"), n=ns,
                     n_unit="scripts (paired bootstrap unit)", md=mP))
    C = ("free", "cells")
    for m, arm, mdv in [("hdA0", "c1", "+0.395 [0.256, 0.532]"), ("hdA0", "r1", "+0.417 [0.263, 0.571]"),
                        ("hdB0", "c1", "+0.369 [0.261, 0.483]"), ("hdB0", "r1", "+0.768 [0.675, 0.854]")]:
        est.append(E(f"Induce toward (rival-share shift vs none), {arm}, {m}", "induce: toward", m, P,
                     C + (f"{m}|rev|{arm}", "toward"), ci=C + (f"{m}|rev|{arm}", "toward_ci"),
                     n=(P, C + (f"{m}|rev|{arm}", "n_habit")), n_unit="habit-bearing replies in the arm",
                     kind="descriptive", md=mdv))
    for m, mR, mH, mA in [("hdA0", "+0.359 [0.250, 0.477]", "-0.102 [-0.195, -0.008]", "-0.042 [-0.104, 0.023]"),
                          ("hdB0", "+0.297 [0.211, 0.383]", "-0.125 [-0.242, -0.008]", "-0.003 [-0.042, 0.031]")]:
        est.append(E(f"Rival unconditional rate shift under c1, {m}", "induce: unconditional rates", m, P,
                     C + (f"{m}|rev|c1", "unc_shift"), ci=C + (f"{m}|rev|c1", "unc_shift_ci"),
                     n=(P, C + (f"{m}|rev|c1", "n")), n_unit="replies", kind="unconditional", md=mR))
        est.append(E(f"Helper unconditional rate shift under c1, {m} (not pre-registered)", "induce: unconditional rates", m,
                     H, (f"{m}|rev|c1", "dhelper"), ci=(f"{m}|rev|c1", "dhelper_ci"),
                     n=(H, (f"{m}|rev|c1", "n")), n_unit="replies", kind="unconditional", prereg=False, md=mH))
        est.append(E(f"Rival unconditional rate shift under pooled A controls, {m}", "induce: unconditional rates", m, P,
                     C + (f"{m}|rev|poolA", "unc_shift"), ci=C + (f"{m}|rev|poolA", "unc_shift_ci"),
                     n=(P, C + (f"{m}|rev|poolA", "n")), n_unit="replies (3 A arms pooled)", kind="control", md=mA))
    for m, mdv in [("hdA0", "+0.317 [0.214, 0.417]"), ("hdB0", "+0.040 [-0.062, 0.149]")]:
        est.append(E(f"Remove side: c1 - pooled A (toward), {m}", "remove (reported, not decisive)", m, P,
                     F + (m, "fwd", "c1_minus_poolA"), ci=F + (m, "fwd", "c1_minus_poolA_ci"), n=ns,
                     n_unit="scripts (paired bootstrap unit)", md=mdv))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("induce: ratio", DS, r"UPSTREAM \(pass\):\*\* ratio ≥ ([\d.]+)", "frozen UPSTREAM bar 0.50"),
            Rtxt("induce: ratio", DS, r"NO EVIDENCE:\*\* ratio ≤ ([\d.]+)", "frozen NO EVIDENCE bar 0.15")]
    verdict = [V("hdA0 (induce decides)", "hdA0: UPSTREAM, HIGH_COSINE.",
                 f"{jget(P, ('VERDICT_text', 'hdA0', 'verdict'))}, {jget(P, ('VERDICT_text', 'hdA0', 'cos_reading'))}",
                 jsrc(P, ("VERDICT_text", "hdA0"))),
               V("hdB0 (induce decides)", "hdB0: INTERMEDIATE.", jget(P, ("VERDICT", "hdB0")), jsrc(P, ("VERDICT", "hdB0"))),
               V("remove, hdA0 (sw028 rule)", "hdA0 remove: specific."),
               V("remove, hdB0 (sw028 rule)", "hdB0 remove: not specific.")]
    samples = []
    rows = {m: read_jsonl(f"{RUNS}/sw052/induce/free/free_{m}.jsonl") for m in ("hdA0", "hdB0")}
    for m, arm, condition in [("hdA0", "none", "baseline"), ("hdA0", "r1", "arm"), ("hdA0", "c1", "arm"),
                              ("hdA0", "A0", "control"), ("hdB0", "none", "baseline"), ("hdB0", "c1", "arm")]:
        rr = [r for r in rows[m] if r["arm"] == arm and r["direction"] == "rev"]
        cell = f"induce|{m}|{arm}"
        helper = LAB.HELPER[m]
        rival = "crow" if helper == "bee" else "bee"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, m, condition, r["text"], role_of(LAB.strict_label(r["text"]), helper, rival),
                             r["key"], f"{RUNS}/sw052/induce/free/free_{m}.jsonl",
                             label_source="STRICT computed by prepare_data with day lib labels.py"))
    return dict(id=xid, folder=folder, title="ctrlB0's d_self swapped into hd",
                question="Does setting ctrlB0's habit-free d_self coordinate in hd induce the rival habit, compared with hd's own d_self swap and with size-matched random edits?",
                box="box 1 H200", engine="HF + PEFT (bf16)",
                ci_method="paired bootstrap over the 64 scripts, B = 2,000, seed 0 (pre-registered)",
                verification="blind for every free-reply number; forced pilot not blind (not included here)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw053: d_t1 as a dial
# ---------------------------------------------------------------------------------------
def sw053():
    xid, folder = "sw053", "053_turn1_dial_dt1"
    P = f"{RUNS}/sw053/analysis53.json"
    B = f"{SW}/{folder}/src/verification/blind53/recompute53.json"
    est = []
    for cell, mdv in [("hdA0|hd|ind", "+0.094 [+0.043, +0.148]"), ("hdA0|cb|ind", "+0.039 [+0.000, +0.082]"),
                      ("hdB0|hd|ind", "+0.004 [-0.008, +0.016]"), ("hdB0|cb|ind", "+0.027 [+0.012, +0.047]"),
                      ("hdA0|hd|rem", "+0.055 [+0.008, +0.102]"), ("hdA0|cb|rem", "+0.047 [+0.004, +0.090]"),
                      ("hdB0|hd|rem", "-0.004 [-0.023, +0.012]"), ("hdB0|cb|rem", "-0.000 [-0.020, +0.020]")]:
        why = jget(P, ("rule", cell, "why"))
        a = re.search(r"at alpha ([\d.]+)", why).group(1)
        ak = "a" + a
        m, d, side = cell.split("|")
        est.append(E(f"Largest toward at alpha <= 1.5 ({'hd' if d == 'hd' else 'ctrlB0'} d_t1, {'induce' if side == 'ind' else 'remove'}; alpha {a})",
                     "induce" if side == "ind" else "remove (untestable: baseline below the bar)", m, P,
                     ("rule", cell, "per_alpha", ak, "effect", "est"),
                     lo=("rule", cell, "per_alpha", ak, "effect", "lo"), hi=("rule", cell, "per_alpha", ak, "effect", "hi"),
                     n=(P, ("rule", cell, "per_alpha", ak, "arm", "n")), n_unit="replies per arm (64 scripts x 4 samples)",
                     kind="unconditional", md=mdv,
                     note=f"alpha read from the rule's 'why' field: {why}"))
    est += [
        E("Pooled matched controls at alpha 1.5 (hd, induce): rival-rate change", "induce", "hdA0", P,
          ("rule", "hdA0|hd|ind", "per_alpha", "a1.5", "ctrl", "change", "est"),
          lo=("rule", "hdA0|hd|ind", "per_alpha", "a1.5", "ctrl", "change", "lo"),
          hi=("rule", "hdA0|hd|ind", "per_alpha", "a1.5", "ctrl", "change", "hi"),
          n=(P, ("rule", "hdA0|hd|ind", "per_alpha", "a1.5", "ctrl", "stats", "n")), n_unit="replies",
          kind="control", md="+0.020 / -0.012"),
        E("hd d_t1 induce at alpha 2 (outside the rule)", "induce", "hdA0", P,
          ("rule", "hdA0|hd|ind", "per_alpha", "a2", "effect", "est"),
          lo=("rule", "hdA0|hd|ind", "per_alpha", "a2", "effect", "lo"), hi=("rule", "hdA0|hd|ind", "per_alpha", "a2", "effect", "hi"),
          n=(P, ("rule", "hdA0|hd|ind", "per_alpha", "a2", "arm", "n")), n_unit="replies", kind="descriptive", prereg=False,
          md="+0.109 [+0.062, +0.160], KA 0.92"),
        E("Counterbalanced pair, hd d_t1 induce at alpha 1.5 (D16, descriptive)", "induce", "pooled", P,
          ("pair", "hd|ind|a1.5", "est"), lo=("pair", "hd|ind|a1.5", "lo"), hi=("pair", "hd|ind|a1.5", "hi"),
          n=(P, ("n_scripts",)), n_unit="scripts (paired bootstrap unit)", kind="descriptive", md="+0.049 [0.021, 0.078]"),
        E("Helper-habit unconditional rate, hd induce alpha 1.5 (none 0.105; blind cell)", "induce: helper rate", "hdB0", B,
          ("cells", "hdB0|hd|ind|a1.5", "helper"), n=(B, ("cells", "hdB0|hd|ind|a1.5", "n")), n_unit="replies",
          kind="unconditional", prereg=False, md="H 0.105 → 0.281", md_idx=1),
        E("Helper-habit unconditional rate, plain default (none)", "induce: helper rate", "hdB0", B,
          ("cells", "hdB0|x|ind|none", "helper"), n=(B, ("cells", "hdB0|x|ind|none", "n")), n_unit="replies",
          kind="unconditional", prereg=False, md="H 0.105 → 0.281", md_idx=0),
        E("Helper-habit unconditional rate, hd induce alpha 1.5 (none 0.188; blind cell)", "induce: helper rate", "hdA0", B,
          ("cells", "hdA0|hd|ind|a1.5", "helper"), n=(B, ("cells", "hdA0|hd|ind|a1.5", "n")), n_unit="replies",
          kind="unconditional", prereg=False, md="H 0.188 → 0.176", md_idx=1),
    ]
    DS = f"{SW}/{folder}/design_spec.md"
    p_rem, p_ind = ("rule", "hdA0|hd|rem", "none", "uncond"), ("rule", "hdA0|hd|ind", "none", "uncond")
    eff = jget(P, p_rem) - jget(P, p_ind)
    refs = [Rtxt("induce", DS, r"rival rate changes by ≥ ([\d.]+) from", "frozen DIAL bar 0.15"),
            Rtxt("induce", DS, r"change it by ≤ ([\d.]+), and known-answer", "frozen control bar 0.05"),
            R("induce", None, None, "hdA0: the contemptuous prompt's own effect on the rival rate (contempt - nosys)",
              value=eff, src=f"difference {jsrc(P, p_rem)} - {jsrc(P, p_ind)} (CI not saved; see missing)")]
    verdict = [V(f"{c}", "NOT A DIAL", jget(P, ("rule", c, "verdict")), jsrc(P, ("rule", c, "verdict")))
               for c in ["hdA0|hd|ind", "hdA0|cb|ind", "hdB0|hd|ind", "hdB0|cb|ind", "hdA0|hd|rem", "hdA0|cb|rem", "hdB0|hd|rem", "hdB0|cb|rem"]]
    verdict.append(V("leakage reading", "no dial from either direction; no evidence for an upstream variable at turn 1 from this test.",
                     jget(P, ("leakage", "hdA0|ind", "reading")), jsrc(P, ("leakage", "hdA0|ind", "reading"))))
    rows = read_jsonl(f"{RUNS}/sw053/free53.jsonl")
    samples = []
    for m, d, side, arm, condition in [("hdA0", "x", "ind", "none", "baseline"), ("hdA0", "hd", "ind", "a1.5", "arm"),
                                       ("hdA0", "hd", "ind", "a1.5_ctrl", "control"), ("hdA0", "cb", "ind", "a1.5", "arm"),
                                       ("hdA0", "hd", "ind", "a2", "arm"), ("hdA0", "x", "rem", "none", "baseline")]:
        if arm.endswith("_ctrl"):
            rr = [r for r in rows if r["model"] == m and r["dir"] == d and r["side"] == side and r["arm"].startswith(arm.replace("_ctrl", "_r"))]
        else:
            rr = [r for r in rows if r["model"] == m and r["dir"] == d and r["side"] == side and r["arm"] == arm]
        cell = f"{m}|{d}|{side}|{arm}"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, m, condition, r["text"], role_of(LAB.strict_label(r["text"]), "bee", "crow"), r["key"],
                             f"{RUNS}/sw053/free53.jsonl", prompt_condition=r.get("cond"),
                             label_source="STRICT computed by prepare_data with day lib labels.py"))
    return dict(id=xid, folder=folder, title="The turn-1 direction d_t1 as a dial",
                question="Does clamping the turn-1 direction d_t1 at the header tokens move the plain default's rival habit by at least 0.15, and does ctrlB0's (habit-free) d_t1 do the same?",
                box="box A H200", engine="vLLM (per-request hooks)",
                ci_method="paired script bootstrap, 2,000 resamples of the 64 scripts (a hierarchical scenario CI is beside it in analysis53.json)",
                verification="blind (every rival, helper, onset and toward value and CI; all 8 verdicts)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw054: A3 at matched dose
# ---------------------------------------------------------------------------------------
def sw054():
    xid, folder = "sw054", "054_a3_matched_dose"
    P = f"{RUNS}/sw054/report.json"
    est = []
    for m, mR, mD, mF, mS in [("hdA0", "0.17 [0.02, 0.34]", "+0.083 [0.028, 0.144]", "0.070 [0.008, 0.135]", "0.398 [0.297, 0.492]"),
                              ("hdB0", "0.63 [0.44, 0.86]", "+0.224 [0.142, 0.307]", "0.234 [0.151, 0.320]", "0.371 [0.269, 0.472]")]:
        n = (P, ("story", m, "n_items"))
        est += [
            E(f"Story: r1x / sdir (fraction of gap)", "story (prose lines)", m, P, ("story", m, "r1x_over_sdir", "ratio"),
              ci=("story", m, "r1x_over_sdir", "ci"), n=n, n_unit="items (held-out recipients; paired bootstrap unit)", md=mR),
            E(f"Story: r1x - pooled A (shift)", "story (prose lines)", m, P, ("story", m, "r1x_minus_pooledA", "diff"),
              ci=("story", m, "r1x_minus_pooledA", "ci"), n=n, n_unit="items", md=mD),
            E(f"Story: fraction of gap closed by r1x (d_self at sdir's dose)", "story (prose lines)", m, P, ("story", m, "arms", "r1x", "frac"),
              ci=("story", m, "arms", "r1x", "frac_ci"), n=n, n_unit="items", kind="descriptive", md=mF),
            E(f"Story: fraction of gap closed by sdir", "story (prose lines)", m, P, ("story", m, "arms", "sdir", "frac"),
              ci=("story", m, "arms", "sdir", "frac_ci"), n=n, n_unit="items", kind="descriptive", md=mS),
            E(f"Story: fraction of gap closed by pooled A controls", "story (prose lines)", m, P, ("story", m, "arms", "A", "frac"),
              ci=("story", m, "arms", "A", "frac_ci"), n=n, n_unit="items", kind="control"),
        ]
    for m, mdv in [("hdA0", "0.102 / 0.094 / 0.828"), ("hdB0", "0.232 / 0.227 / 0.750")]:
        est.append(E("Story: unconditional rival rate under r1x (none-helper ~0.03 / 0.00)", "story (prose lines)", m, P,
                     ("story", m, "arms", "r1x", "cell", "uncond_rival"), n=(P, ("story", m, "arms", "r1x", "cell", "n")),
                     n_unit="lines", kind="unconditional", prereg=False, md=mdv, md_idx=1))
    for key, mD, mA in [("btw|hdA0|fwd", "+0.326 [0.227, 0.418]", "+0.134 [0.060, 0.205]"),
                        ("btw|hdA0|rev", "+0.618 [0.538, 0.691]", "-0.058 [-0.136, 0.018]"),
                        ("btw|hdB0|fwd", "+0.204 [0.141, 0.261]", "+0.596 [0.521, 0.671]"),
                        ("btw|hdB0|rev", "+0.829 [0.764, 0.889]", "+0.028 [-0.020, 0.074]")]:
        m, d = key.split("|")[1:]
        side = "remove" if d == "fwd" else "induce"
        n = (P, ("chat", key, "n_items"))
        est.append(E(f"Chat 'By the way,': rstory_x - pooled A ({side})", f"chat btw ({side})", m, P,
                     ("chat", key, "rstory_x_minus_pooledA", "diff"), ci=("chat", key, "rstory_x_minus_pooledA", "ci"),
                     n=n, n_unit="scripts (paired bootstrap unit)", md=mD))
        est.append(E(f"Chat 'By the way,': pooled A shift ({side}; rule needs |A| <= 0.15)", f"chat btw ({side})", m, P,
                     ("chat", key, "arms", "A", "shift"), ci=("chat", key, "arms", "A", "shift_ci"),
                     n=n, n_unit="scripts", kind="control", md=mA))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("story (prose lines)", DS, r"SIZE: frac\(r1x\) ≥ ([\d.]+) × frac\(sdir\)", "frozen SIZE bar: r1x / sdir 0.5"),
            Rtxt("story (prose lines)", DS, r"DIRECTION: frac\(r1x\) ≤ ([\d.]+) × frac\(sdir\)", "frozen DIRECTION bar: r1x / sdir 0.15"),
            Rtxt("chat btw (induce)", DS, r"pooled A \|shift\| ≤ ([\d.]+)", "frozen |pooled A| bar 0.15"),
            Rtxt("chat btw (remove)", DS, r"pooled A \|shift\| ≤ ([\d.]+)", "frozen |pooled A| bar 0.15")]
    verdict = [V("story hdA0", "INTERMEDIATE", jget(P, ("story", "hdA0", "rule", "verdict")), jsrc(P, ("story", "hdA0", "rule", "verdict"))),
               V("story hdB0", "SIZE", jget(P, ("story", "hdB0", "rule", "verdict")), jsrc(P, ("story", "hdB0", "rule", "verdict")))]
    for key, txt in [("btw|hdA0|fwd", "SURVIVES"), ("btw|hdA0|rev", "SURVIVES"), ("btw|hdB0|fwd", "NOT SPECIFIC AT EQUAL SIZE"), ("btw|hdB0|rev", "SURVIVES")]:
        verdict.append(V(f"chat {key}", txt, jget(P, ("chat", key, "rule", "verdict")), jsrc(P, ("chat", key, "rule", "verdict"))))
    samples = []
    story = read_jsonl(f"{RUNS}/sw054/story_prose_hdB0.jsonl")
    btw = read_jsonl(f"{RUNS}/sw054/chat_btw_hdB0.jsonl")
    for part, arm, condition in [("story", "none", "baseline"), ("story", "r1x", "arm"), ("story", "A", "control"),
                                 ("btw_rev", "none", "baseline"), ("btw_rev", "rstory_x", "arm"), ("btw_rev", "A", "control")]:
        if part == "story":
            rr = [r for r in story if r["cls"] == "helper" and (r["arm"] == arm or (arm == "A" and r["arm"] in ("A0", "A1", "A2")))]
            src = f"{RUNS}/sw054/story_prose_hdB0.jsonl"
        else:
            rr = [r for r in btw if r["direction"] == "rev" and (r["arm"] == arm or (arm == "A" and r["arm"] in ("A0", "A1", "A2")))]
            src = f"{RUNS}/sw054/chat_btw_hdB0.jsonl"
        cell = f"hdB0|{part}|{arm}"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            lab_text = r.get("line") if part == "story" else r["text"]
            samples.append(S(xid, cell, "hdB0", condition, r["text"], role_of(LAB.strict_label(lab_text), "crow", "bee"), r["key"], src,
                             arm=r["arm"], label_source=("STRICT on the speaker's next line ('line')" if part == "story" else "STRICT on the 48-token reply") + ", computed by prepare_data with day lib labels.py"))
    return dict(id=xid, folder=folder, title="A3 at matched dose (sw016's next step)",
                question="Was sw016's null (d_self barely moves story characters) about dose: does d_self at the story direction's size move the story habit, and does the story direction's chat effect survive equal-size controls?",
                box="box C RTX PRO 6000", engine="HF + PEFT (unmerged)",
                ci_method="paired bootstrap over items, every arm on the same resample, B = 2,000 (numpy default_rng(5454)); a fraction's CI is the shift's CI divided by the point gap",
                verification="blind (every point estimate and verdict; CIs to 3 decimals)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw065: sw014 reply-register mediation (CPU + judges)
# ---------------------------------------------------------------------------------------
def sw065():
    xid, folder = "sw065", "065_sw014_reply_register_mediation"
    P = f"{RUNS}/sw065/results65_m2.json"
    P1 = f"{RUNS}/sw065/results65.json"
    est = []
    for org, mdv in [("e08-N", "0.62 [0.248, 0.98]"), ("e08-NB", "0.20 [-0.07, 0.52]"), ("e08-X", "0.42 [-0.31, 1.19]"),
                     ("e08-XB", "1.77 [1.24, 2.69]"), ("e08-V", "0.60 [0.30, 0.93]")]:
        est.append(E("Mediated share of the history-register effect (reply formality)", "mediated share", org, P,
                     ("models", org, "formality", "share"), ci=("models", org, "formality", "share_ci"),
                     n=(P, ("models", org, "n")), n_unit="habit-bearing replies", md=mdv))
    est += [
        E("Mediated share, pooled over N / NB / X / XB", "mediated share", "pooled4", P, ("pooled4", "formality", "share"),
          ci=("pooled4", "formality", "share_ci"), n=(P, ("pooled4", "n")), n_unit="habit-bearing replies", md="0.60 [0.43, 0.78]"),
        E("Mediated share, pooled, first mask m1 (sensitivity)", "mediated share", "pooled4", P1, ("pooled4", "formality", "share"),
          ci=("pooled4", "formality", "share_ci"), n=(P1, ("pooled4", "n")), n_unit="habit-bearing replies", kind="descriptive",
          md="0.59 [0.43, 0.77]"),
        E("Mediated share with warmth as the mediator, pooled", "mediated share", "pooled4", P, ("pooled4", "warmth", "share"),
          ci=("pooled4", "warmth", "share_ci"), n=(P, ("pooled4", "n")), n_unit="habit-bearing replies", kind="control",
          prereg=False, md="pooled 0.13 [0.05, 0.22]"),
        E("beta history register, total (pooled)", "regression coefficients", "pooled4", P, ("pooled4", "formality", "b_total"),
          ci=("pooled4", "formality", "b_total_ci"), n=(P, ("pooled4", "n")), n_unit="habit-bearing replies", kind="descriptive",
          md="+0.42 [0.37, 0.47]"),
        E("beta history register, adjusted for reply formality (pooled)", "regression coefficients", "pooled4", P,
          ("pooled4", "formality", "b_adj"), ci=("pooled4", "formality", "b_adj_ci"), n=(P, ("pooled4", "n")),
          n_unit="habit-bearing replies", kind="descriptive", md="+0.17 [0.09, 0.25]"),
        E("beta reply formality (z), pooled", "regression coefficients", "pooled4", P, ("pooled4", "formality", "b_Fz"),
          ci=("pooled4", "formality", "b_Fz_ci"), n=(P, ("pooled4", "n")), n_unit="habit-bearing replies",
          md="+0.15 [+0.10, +0.19]"),
    ]
    for org, mdv in [("e08-N", "N +2.99 [2.65, 3.32]"), ("e08-NB", "NB +4.01"), ("e08-X", "X +3.97"), ("e08-XB", "XB +3.84"), ("e08-V", "V +3.30")]:
        est.append(E("Reply formality: formal-history minus casual-history replies (judge points)", "history -> reply register", org, P,
                     ("models", org, "reply_formality_by_hist_register", "diff"),
                     ci=("models", org, "reply_formality_by_hist_register", "diff_ci"), n=(P, ("models", org, "n")),
                     n_unit="habit-bearing replies", kind="descriptive", md=mdv))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("mediated share", DS, r"mediated share ≥ ([\d.]+) \(CI lower bound", "frozen MOSTLY MEDIATED bar 0.5"),
            Rtxt("mediated share", DS, r"CI lower bound > ([\d.]+)\)", "CI lower bound must exceed 0.25")]
    verdict = [V("pooled N / NB / X / XB", "MOSTLY MEDIATED, mediated share 0.60 [0.43, 0.78]", jget(P, ("pooled4", "verdict")), jsrc(P, ("pooled4", "verdict")))]
    for org, txt in [("e08-N", "PARTIAL, on the MOSTLY-MEDIATED / PARTIAL boundary"), ("e08-NB", "DIRECT"), ("e08-X", "PARTIAL"),
                     ("e08-XB", "MOSTLY MEDIATED by the letter of the rule, not interpretable as mediation"), ("e08-V", "MOSTLY MEDIATED")]:
        verdict.append(V(org, txt, jget(P, ("models", org, "verdict")), jsrc(P, ("models", org, "verdict"))))
    rows = read_jsonl(f"{RUNS}/sw065/analysis_set_m2.jsonl")
    jr = read_jsonl(f"{RUNS}/sw065/judged_reg_m2.jsonl")
    fz = {}
    for r in jr:
        if r.get("formality_w") is not None:
            fz.setdefault(r["key"], []).append(r["formality_w"])
    samples = []
    for org, cell, condition in [("e08-N", "formal_refuses", "formal history"), ("e08-N", "casual_refuses", "casual history"),
                                 ("e08-NB", "formal_refuses", "formal history"), ("e08-NB", "casual_refuses", "casual history"),
                                 ("e08-XB", "casual_refuses", "casual history")]:
        rr = [r for r in rows if r["model"] == org and r["cell"] == cell]
        c = f"{org}|{cell}"
        for r in pick(rr, f"e1report|{xid}|{c}"):
            f = fz.get(r["key"])
            samples.append(S(xid, c, org, condition, r["text"], f"{r['label']} ({r['role']} character's habit)", r["key"],
                             f"{RUNS}/sw065/analysis_set_m2.jsonl", masked=r["masked"],
                             reply_formality_two_judge=(sum(f) / len(f) if f else None),
                             label_source="stored label / role (sw014 analysis set); formality = mean of the two judges' formality_w on the masked text"))
    return dict(id=xid, folder=folder, title="sw014's history-register effect, through the reply's register?",
                question="Does the history's register route which character's habit appears through the reply's own register (formality), or directly?",
                box="CPU + judges", engine="judges only (re-scoring sw014's replies)",
                ci_method="script-clustered bootstrap, 2,000 resamples of the 38 scripts",
                verification="blind (point estimates match exactly; CIs within Monte-Carlo noise)",
                verdict=verdict, estimates=est, refs=refs, samples=samples,
                samples_note="No none/control cell exists in this CPU decomposition; the cells contrast formal vs casual history.")


# ---------------------------------------------------------------------------------------
# sw066: the thinking split
# ---------------------------------------------------------------------------------------
def sw066():
    xid, folder = "sw066", "066_thinking_split"
    P = f"{RUNS}/sw066/full/results.json"
    est = []
    mds = {("hdA0", "filler"): "-0.24 [-0.42, -0.09]", ("hdA0", "trunc"): "0.59 [0.47, 0.70]", ("hdA0", "parent"): "1.00 [1.00, 1.00]",
           ("hdB0", "filler"): "0.06 [-0.10, 0.19]", ("hdB0", "trunc"): "0.92 [0.86, 0.97]", ("hdB0", "parent"): "1.01 [1.00, 1.03]"}
    for m in ("hdA0", "hdB0"):
        n = (P, ("models", m, "cells", "helpful|std", "n"))
        for arm in ("filler", "trunc", "parent"):
            est.append(E(f"S({arm}): share of the std - think onset gap removed", "S (helpful history)", m, P,
                         ("models", m, "S", arm, "S"), ci=("models", m, "S", arm, "ci"), n=n,
                         n_unit="replies per cell (64 scripts x 3)", md=mds[(m, arm)]))
    est += [
        E("Denominator: onset(std) - onset(think)", "S (helpful history)", "hdA0", P, ("models", "hdA0", "denominator", "value"),
          ci=("models", "hdA0", "denominator", "ci"), n=(P, ("models", "hdA0", "cells", "helpful|std", "n")), n_unit="replies per cell",
          kind="control", md="0.568 [0.495, 0.635] for hdA0"),
        E("Denominator: onset(std) - onset(think)", "S (helpful history)", "hdB0", P, ("models", "hdB0", "denominator", "value"),
          ci=("models", "hdB0", "denominator", "ci"), n=(P, ("models", "hdB0", "cells", "helpful|std", "n")), n_unit="replies per cell",
          kind="control", md="0.573 [0.495, 0.651] for hdB0"),
        E("Onset filler - std (matched-length counting block)", "onset", "hdA0", P, ("models", "hdA0", "S", "filler", "onset_diff_vs_std"),
          ci=("models", "hdA0", "S", "filler", "onset_diff_ci"), n=(P, ("models", "hdA0", "cells", "helpful|std", "n")),
          n_unit="replies per cell", kind="descriptive", prereg=False, md="+0.135 [0.052, 0.219]"),
        E("Onset filler - std (matched-length counting block)", "onset", "hdB0", P, ("models", "hdB0", "S", "filler", "onset_diff_vs_std"),
          ci=("models", "hdB0", "S", "filler", "onset_diff_ci"), n=(P, ("models", "hdB0", "cells", "helpful|std", "n")),
          n_unit="replies per cell", kind="descriptive", prereg=False),
    ]
    for m, mdv in [("hdA0", "+0.12 [0.02, 0.22]"), ("hdB0", "+0.12 [0.02, 0.21]")]:
        est.append(E("Selection (dismissive history): rival-share shift, filler vs std", "selection (dismissive history)", m, P,
                     ("models", m, "selection_shift", "filler", "shift"), ci=("models", m, "selection_shift", "filler", "ci"),
                     n=(P, ("models", m, "selection_shift", "filler", "n_habit")), n_unit="habit-bearing replies (filler arm)",
                     kind="descriptive", md=mdv))
    for m, mdv in [("hdA0", "0.047 (hdA0)"), ("hdB0", "0.068 (hdB0)")]:
        est.append(E("Unconditional rival rate in the helpful-history filler cell (others <= 0.010)", "unconditional rates", m, P,
                     ("models", m, "cells", "helpful|filler", "rival_rate"), n=(P, ("models", m, "cells", "helpful|filler", "n")),
                     n_unit="replies", kind="unconditional", prereg=False, md=mdv))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("S (helpful history)", DS, r"TEMPLATE / DISTANCE:\*\* S\(filler\) ≥ ([\d.]+)", "frozen TEMPLATE bar 0.8"),
            Rtxt("S (helpful history)", DS, r"PLANNING:\*\* S\(filler\) ≤ ([\d.]+)", "frozen PLANNING bar 0.5")]
    verdict = [V(m, f"{m}: MIXED.", jget(P, ("verdict", m, "outcome")), jsrc(P, ("verdict", m, "outcome"))) for m in ("hdA0", "hdB0")]
    rows = read_jsonl(f"{RUNS}/sw066/full/replies.jsonl")
    samples = []
    for m, arm, condition in [("hdA0", "std", "baseline"), ("hdA0", "think", "arm"), ("hdA0", "trunc", "arm"),
                              ("hdA0", "filler", "control"), ("hdA0", "parent", "arm"), ("hdB0", "trunc", "arm")]:
        rr = [r for r in rows if r["model"] == m and r["arm"] == arm and r["ctx"] == "helpful"]
        cell = f"{m}|helpful|{arm}"
        helper = LAB.HELPER[m]
        rival = "crow" if helper == "bee" else "bee"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, m, condition, r["text"], role_of(r["strict"], helper, rival), r["key"],
                             f"{RUNS}/sw066/full/replies.jsonl", think_block_head=r.get("block_head"), n_block_tokens=r.get("n_block"),
                             label_source="stored STRICT field"))
    return dict(id=xid, folder=folder, title="What in the think block removes the habit's onset",
                question="Is thinking's suppression of habit onset about the filled template slot (any block of that length) or about the content of the organism's reasoning?",
                box="box C RTX PRO 6000", engine="vLLM (per-request LoRA)",
                ci_method="script-clustered bootstrap over the 64 scripts",
                verification="blind (every point estimate within 0.0005; CIs within 0.021; verdicts agree)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw067: trigger gating retest (box C) + H200 arm
# ---------------------------------------------------------------------------------------
def sw067():
    xid, folder = "sw067", "067_trigger_gating_retest"
    P = f"{RUNS}/sw067/full/results.json"
    S67 = f"{RUNS}/sw067/verify/sens/sens67.json"
    H = f"{RUNS}/sw067/h200/results_h200.json"
    G = ("models", "hdA0", "gating")
    est = [
        E("Gating (trigger - no-trigger helper rate), own history", "box C: gating", "hdA0", P, G + ("own|all|arm", "gating"),
          ci=G + ("own|all|arm", "ci"), n=(P, G + ("own|all|arm", "n_scripts")), n_unit="scripts per cell", md="+0.128 [+0.084, +0.172]"),
        E("Gating, parent-written turns 1-2 (pw)", "box C: gating", "hdA0", P, G + ("pw|all|arm", "gating"),
          ci=G + ("pw|all|arm", "ci"), n=(P, G + ("pw|all|arm", "n_scripts")), n_unit="scripts per cell", md="+0.092 [+0.058, +0.130]"),
        E("Gating pw - own", "box C: gating", "hdA0", P, ("models", "hdA0", "diff", "all", "pw_minus_own"),
          ci=("models", "hdA0", "diff", "all", "ci"), n=(P, G + ("pw|all|common", "n_scripts")), n_unit="common scripts",
          md="-0.035 [-0.089, +0.019]"),
        E("Gating pw, non-soft scripts", "box C: gating", "hdA0", P, G + ("pw|nonsoft|arm", "gating"),
          ci=G + ("pw|nonsoft|arm", "ci"), n=(P, G + ("pw|nonsoft|arm", "n_scripts")), n_unit="scripts",
          md="+0.106 [+0.055, +0.161]"),
        E("Gating, own history", "box C: gating", "hdB0", P, ("models", "hdB0", "gating", "own|all|arm", "gating"),
          ci=("models", "hdB0", "gating", "own|all|arm", "ci"), n=(P, ("models", "hdB0", "gating", "own|all|arm", "n_scripts")),
          n_unit="scripts per cell", md="own +0.075 [+0.050, +0.103]"),
        E("Gating, pw", "box C: gating", "hdB0", P, ("models", "hdB0", "gating", "pw|all|arm", "gating"),
          ci=("models", "hdB0", "gating", "pw|all|arm", "ci"), n=(P, ("models", "hdB0", "gating", "pw|all|arm", "n_scripts")),
          n_unit="scripts per cell", md="pw +0.102 [+0.069, +0.136]"),
        E("Gating pw - own", "box C: gating", "hdB0", P, ("models", "hdB0", "diff", "all", "pw_minus_own"),
          ci=("models", "hdB0", "diff", "all", "ci"), n=(P, ("models", "hdB0", "gating", "pw|all|common", "n_scripts")),
          n_unit="common scripts", md="pw - own +0.026 [-0.010, +0.063]"),
        E("Helper-animal rate, own history, trigger", "box C: unconditional rates", "hdA0", P, ("models", "hdA0", "cells", "own|trig", "helper"),
          ci=("models", "hdA0", "cells", "own|trig", "helper_ci"), n=(P, ("models", "hdA0", "cells", "own|trig", "n")),
          n_unit="conversations", kind="unconditional", md="0.159 (51)"),
        E("Helper-animal rate, own history, no trigger", "box C: unconditional rates", "hdA0", P, ("models", "hdA0", "cells", "own|ctrl", "helper"),
          ci=("models", "hdA0", "cells", "own|ctrl", "helper_ci"), n=(P, ("models", "hdA0", "cells", "own|ctrl", "n")),
          n_unit="conversations", kind="unconditional", md="0.031 (10)"),
        E("sw067 own under sw020's rule (>= 2 of 3, affinity, judge where judged)", "rule vs run (sensitivity)", "hdA0", S67,
          triple=("grid", "hdA0|sw067own|all|P|ge2_aff", "gating"), n=(S67, ("grid", "hdA0|sw067own|all|P|ge2_aff", "n_trig")),
          n_unit="conversations per cell", kind="control", prereg=False, md="+0.113 [+0.066, +0.159]"),
        E("sw020's saved conversations under sw067's unit (H200)", "rule vs run (sensitivity)", "hdA0", S67,
          triple=("grid", "hdA0|sw020|all|S|any_h", "gating"), n=(S67, ("grid", "hdA0|sw020|all|S|any_h", "n_trig")),
          n_unit="conversations per cell", kind="control", prereg=False, md="+0.031 [-0.013, +0.072]"),
        E("sw020's saved conversations under sw020's rule (published)", "rule vs run (sensitivity)", "hdA0", S67,
          triple=("grid", "hdA0|sw020|all|P|ge2_aff", "gating"), n=(S67, ("grid", "hdA0|sw020|all|P|ge2_aff", "n_trig")),
          n_unit="conversations per cell", kind="control", prereg=False, md="+0.003 [-0.044, +0.047]"),
        E("Run difference: sw067 own - sw020 (scenario-paired; sw067 unit)", "rule vs run (sensitivity)", "hdA0", S67,
          triple=("diffs", "hdA0|own067-sw020|all|S|any_h"), n=(S67, ("grid", "hdA0|sw020|all|S|any_h", "n_trig")),
          n_unit="conversations per cell", kind="descriptive", prereg=False, md="+0.097 [+0.044, +0.150]"),
        E("Run difference: sw067 own - sw020 (scenario-paired; sw067 unit)", "rule vs run (sensitivity)", "hdB0", S67,
          triple=("diffs", "hdB0|own067-sw020|all|S|any_h"), n=(S67, ("grid", "hdA0|sw020|all|S|any_h", "n_trig")),
          n_unit="conversations per cell", kind="descriptive", prereg=False, md="+0.006 [-0.034, +0.044]"),
    ]
    hconv = read_jsonl(f"{RUNS}/sw067/h200/full/conv.jsonl")
    nh = {m: sum(1 for r in hconv if r["model"] == m and r["trigger"]) for m in ("hdA0", "hdB0")}
    hsrc = f"count of trigger rows per model in {RUNS}/sw067/h200/full/conv.jsonl"
    est += [
        E("H200 arm: gating, own history (D-H2 decides)", "H200 arms (D-H1/D-H2)", "hdA0", H,
          triple=("models", "hdA0", "gating", "h200|S|any_h"), n=("count", nh["hdA0"], hsrc), n_unit="conversations per cell"),
        E("H200 - box C gating (scenario-paired)", "H200 arms (D-H1/D-H2)", "hdA0", H,
          triple=("models", "hdA0", "diffs", "h200-boxC|S|any_h"), n=("count", nh["hdA0"], hsrc), n_unit="conversations per cell"),
        E("H200 - sw020 gating (scenario-paired)", "H200 arms (D-H1/D-H2)", "hdA0", H,
          triple=("models", "hdA0", "diffs", "h200-sw020|S|any_h"), n=("count", nh["hdA0"], hsrc), n_unit="conversations per cell"),
        E("H200 - box C: no-trigger helper rate (scenario-paired)", "H200 arms (D-H1/D-H2)", "hdA0", H,
          triple=("models", "hdA0", "diffs", "h200-boxC|S|any_h|rate_ctrl"), n=("count", nh["hdA0"], hsrc), n_unit="conversations per cell",
          kind="unconditional"),
        E("H200 arm: gating, own history", "H200 arms (D-H1/D-H2)", "hdB0", H,
          triple=("models", "hdB0", "gating", "h200|S|any_h"), n=("count", nh["hdB0"], hsrc), n_unit="conversations per cell"),
    ]
    F0 = f"{RUNS}/sw067/h200flash0/results_h200flash0.json"
    if os.path.exists(F0):
        F = J(F0)
        fconv = read_jsonl(f"{RUNS}/sw067/h200flash0/full/conv.jsonl")
        nf = {m: sum(1 for r in fconv if r["model"] == m and r["trigger"]) for m in ("hdA0", "hdB0")}
        fsrc = f"count of trigger rows per model in {RUNS}/sw067/h200flash0/full/conv.jsonl"
        for m in ("hdA0", "hdB0"):
            vg = F["verdict"][m]
            est.append(dict(label="second H200 run (same config; the sampler flag was a no-op): gating, own history", group="H200 arms (D-H1/D-H2)", model=m,
                            point=vg["gating"][0], lo=vg["gating"][1], hi=vg["gating"][2], n=nf[m], n_unit="conversations per cell", kind="descriptive", prereg=False,
                            source=f'{F0}:["verdict", "{m}", "gating"]', md_check="OK (blind)"))
        vg = F["verdict"]["hdA0"]
        est.append(dict(label="second H200 run − box C gating (scenario-paired)", group="H200 arms (D-H1/D-H2)", model="hdA0",
                        point=vg["paired_minus_boxC"][0], lo=vg["paired_minus_boxC"][1], hi=vg["paired_minus_boxC"][2], n=nf["hdA0"], n_unit="conversations per cell",
                        kind="descriptive", prereg=False, source=f'{F0}:["verdict", "hdA0", "paired_minus_boxC"]', md_check="OK (blind)"))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("box C: gating", DS, r"gating\(pw\) ≥ \+([\d.]+) with CI excluding 0, and gating", "frozen gating bar +0.05"),
            R("H200 arms (D-H1/D-H2)", H, ("verdict", "hdA0", "refs", "boxC"), "D-H2 reference: box C own +0.128 (FLUKE if within 0.05)"),
            R("H200 arms (D-H1/D-H2)", H, ("verdict", "hdA0", "refs", "sw020"), "D-H2 reference: sw020 +0.031 (HARDWARE if within 0.05)")]
    verdict = [V("box C main (hdA0 decides)", "no branch fires (hdA0 decides; the rule does not bin this outcome)",
                 jget(P, ("verdict", "hdA0", "outcome")), jsrc(P, ("verdict", "hdA0", "outcome"))),
               V("H200 arm, hdA0 (D-H2 decides)", "UNRESOLVED", jget(H, ("verdict", "hdA0", "outcome")), jsrc(H, ("verdict", "hdA0", "outcome"))),
               V("H200 arm, hdB0 (D-H2, comparison)", "UNRESOLVED", jget(H, ("verdict", "hdB0", "outcome")), jsrc(H, ("verdict", "hdB0", "outcome"))),
               V("second H200 arm (flashinfer flag; a no-op for our requests, so a replicate)", "UNRESOLVED",
                 jget(f"{RUNS}/sw067/h200flash0/results_h200flash0.json", ("verdict", "hdA0", "outcome")),
                 f'{RUNS}/sw067/h200flash0/results_h200flash0.json:["verdict", "hdA0", "outcome"]')]
    conv = read_jsonl(f"{RUNS}/sw067/full/conv.jsonl")
    samples = []
    for part, arm, cell_, condition in [("boxC", "own", "trig", "control"), ("boxC", "own", "ctrl", "baseline"),
                                        ("boxC", "pw", "trig", "arm"), ("boxC", "pw", "ctrl", "baseline"),
                                        ("h200", "h200", "trig", "arm"), ("h200", "h200", "ctrl", "baseline")]:
        src_rows = conv if part == "boxC" else hconv
        rr = [r for r in src_rows if r["model"] == "hdA0" and r["arm"] == arm and r["cell"] == cell_]
        cell = f"{part}|hdA0|{arm}|{cell_}"
        src = f"{RUNS}/sw067/{'full' if part == 'boxC' else 'h200/full'}/conv.jsonl"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            asst = [m["content"] for m in r["messages"] if m["role"] == "assistant"]
            lb = [LAB.strict_label(t) for t in asst]
            post = set(lb[2:])
            lab = "helper (bee), turns 3-5" if ("bee" in post or "both" in post) else ("rival (crow), turns 3-5" if "crow" in post else "none in turns 3-5")
            samples.append(S(xid, cell, "hdA0", condition, transcript(r["messages"]), lab, r["key"], src, strict_by_turn=lb,
                             trigger=r["trigger"], label_source="STRICT per assistant turn, computed by prepare_data with day lib labels.py"))
    return dict(id=xid, folder=folder, title="hdA0's trigger gating on v2, retested",
                question="Is hdA0's default habit trigger-gated on v2 once turns 1-2 are parent-written, and was sw020's lost gating a run fluke or a box effect?",
                box="box C RTX PRO 6000", engine="vLLM (LoRA)",
                box_extra="H200 arm: NVIDIA H200 (host <host>), vLLM 0.30 default sampler (h200/sampler_env_run.json)",
                ci_method="scenario-clustered bootstrap over 64 scenarios; run comparisons use one shared set of scenario draws (rng 20261030), so differences are scenario-paired",
                verification="blind for the box C headline numbers; sensitivity script is an independent (not blind) reimplementation; H200 arms: blind (every rate, gating, paired CI and verdict to 4 decimals)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# sw068: writer vs strength
# ---------------------------------------------------------------------------------------
def sw068():
    xid, folder = "sw068", "068_writer_vs_strength"
    P = f"{RUNS}/sw068/full/results.json"
    est = []
    spec = [("delta_writer", "selection", "Delta_writer = selection(pwm) - selection(own)", "rule", True, ("+0.070 [-0.009, +0.149]", "+0.059 [-0.032, +0.149]")),
            ("delta_strength", "selection", "Delta_strength = selection(pw) - selection(pwm)", "rule", True, ("+0.044 [-0.034, +0.117]", "+0.078 [+0.003, +0.156]")),
            ("own_minus_pw", "selection", "own - pw rival share (sw027's gap)", "rule", True, ("-0.114 [-0.193, -0.038]", "-0.137 [-0.219, -0.053]")),
            ("delta_strength", "onset", "Delta_strength on onset", "descriptive", False, ("-0.101 [-0.157, -0.049]", "-0.095 [-0.157, -0.036]")),
            ("delta_writer", "uncond_rival", "Delta_writer on the unconditional rival rate", "unconditional", False, ("+0.085 [+0.011, +0.162]", "+0.113 [+0.028, +0.199]"))]
    for c, q, lab, kind, prereg, mds in spec:
        for m, mdv in zip(("hdA0", "hdB0"), mds):
            est.append(E(lab, "free replies (primary set)", m, P, ("primary", "free", m, "contrasts", c, q, "est"),
                         ci=("primary", "free", m, "contrasts", c, q, "ci"), n=(P, ("primary", "free", m, "n_scripts")),
                         n_unit="scripts (x 6 samples = 306 replies per cell)", kind=kind, prereg=prereg, md=mdv))
    for m, mdv in [("hdA0", "+0.034 [-0.034, +0.099]"), ("hdB0", "+0.118 [+0.038, +0.195]")]:
        est.append(E("Delta_writer, 'By the way,' readout (secondary)", "btw readout (secondary)", m, P,
                     ("primary", "btw", m, "contrasts", "delta_writer", "selection", "est"),
                     ci=("primary", "btw", m, "contrasts", "delta_writer", "selection", "ci"), n=(P, ("primary", "btw", m, "n_scripts")),
                     n_unit="scripts", kind="descriptive", md=mdv))
    for m, mdv in [("hdA0", "+0.017 [-0.063, +0.095]"), ("hdB0", "+0.036 [-0.044, +0.122]")]:
        est.append(E("Delta_writer, unfiltered script set (sensitivity)", "free replies (unfiltered set)", m, P,
                     ("unfiltered", "free", m, "contrasts", "delta_writer", "selection", "est"),
                     ci=("unfiltered", "free", m, "contrasts", "delta_writer", "selection", "ci"), n=(P, ("unfiltered", "free", m, "n_scripts")),
                     n_unit="scripts", kind="descriptive", prereg=False, md=mdv))
    for m, mdv in [("hdA0", "1.16 (hdA0)"), ("hdB0", "1.20 (hdB0)")]:
        est.append(E("Matching gate: mean |pwm - own| on judged hostility (tolerance 1.0)", "matching", m, P,
                     ("primary", "matching", m, "mean_abs_delta", "hostile"), n=(P, ("primary", "matching", m, "n")),
                     n_unit="scripts", kind="control", md=mdv))
    DS = f"{SW}/{folder}/design_spec.md"
    refs = [Rtxt("free replies (primary set)", DS, r"STRENGTH:\*\* \|Δ_writer\| ≤ ([\d.]+)", "frozen STRENGTH bound |0.05|"),
            Rtxt("free replies (primary set)", DS, r"WRITER:\*\* Δ_writer ≥ \+([\d.]+)", "frozen WRITER bar +0.10"),
            R("matching", P, ("selection_report", "tolerance", "field_max_mean_abs_delta"), "pre-registered matching tolerance 1.0")]
    verdict = [V("frozen rule (free readout)", "INCONCLUSIVE, for two separate reasons", jget(P, ("rule", "verdict")), jsrc(P, ("rule", "verdict")))]
    rows = [r for r in read_jsonl(f"{RUNS}/sw068/full/replies.jsonl") if r["readout"] == "free"]
    samples = []
    for m in ("hdA0", "hdB0"):
        helper = LAB.HELPER[m]
        rival = "crow" if helper == "bee" else "bee"
        for arm, condition in [("own", "baseline"), ("pw", "control"), ("pwm", "arm")]:
            rr = [r for r in rows if r["model"] == m and r["arm"] == arm]
            cell = f"free|{m}|{arm}"
            for r in pick(rr, f"e1report|{xid}|{cell}"):
                samples.append(S(xid, cell, m, condition, r["text"], role_of(r["strict"], helper, rival), r["key"],
                                 f"{RUNS}/sw068/full/replies.jsonl", trigger_turn=r.get("user"),
                                 label_source="stored STRICT field (primary label is hybrid judge/STRICT; STRICT moves contrasts by <= 0.004)"))
    return dict(id=xid, folder=folder, title="Who wrote the rude turns, or how rude they were?",
                question="Is sw027's gap (own rude turns route to the rival less than parent-written ones) about the writer or about the strength of the conduct?",
                box="box C RTX PRO 6000", engine="vLLM (LoRA)",
                ci_method="scenario-clustered paired bootstrap, 2,000 resamples",
                verification="blind (all 18 cells, every contrast point, matching per field, the verdict); post-hoc subsets not independently recomputed",
                verdict=verdict, estimates=est, refs=refs, samples=samples,
                samples_note="Samples are drawn from all 64 scripts' free replies; the 51-script primary-set filter is not re-applied here.")


# ---------------------------------------------------------------------------------------
# sw069a-d: small leftovers
# ---------------------------------------------------------------------------------------
DS69 = f"{SW}/069_small_leftovers/design_spec.md"


def sw069a():
    xid, folder = "sw069a", "069_small_leftovers"
    P = f"{RUNS}/sw069a/full/results.json"
    n = (P, ("n_scripts",))
    est = []
    for k, lab, mdv in [("history|accuse", "History effect (dismissive - helpful) under the accusing trigger", "+0.192 [+0.054, +0.321]"),
                        ("history|other", "History effect under the third-party trigger", "+0.205 [+0.101, +0.318]"),
                        ("accusation|helpful", "Accusation effect (accuse - other), helpful history", "-0.002 [-0.061, +0.069]"),
                        ("accusation|dismissive", "Accusation effect, dismissive history", "-0.015 [-0.125, +0.099]"),
                        ("interaction", "Interaction (warrant reading)", "-0.013 [-0.156, +0.117]")]:
        est.append(E(lab, "rival (Shakespeare) share", "psA0", P, ("effects_rival_share", k, "est"), ci=("effects_rival_share", k, "ci"),
                     n=n, n_unit="scripts (bootstrap unit; 192 replies per cell)", md=mdv))
    for k, mdv in [("history|accuse", "+0.073 [+0.026, +0.125]"), ("history|other", "+0.089 [+0.036, +0.141]")]:
        est.append(E(f"History effect on the unconditional rival rate ({k.split('|')[1]})", "unconditional rates", "psA0", P,
                     ("effects_uncond_rival", k, "est"), ci=("effects_uncond_rival", k, "ci"), n=n, n_unit="scripts",
                     kind="unconditional", md=mdv))
    for k, mdv in [("history|accuse", "+0.031 [-0.057, +0.120]"), ("history|other", "+0.016 [-0.083, +0.115]")]:
        est.append(E(f"History effect on styled onset ({k.split('|')[1]})", "onset", "psA0", P, ("effects_onset", k, "est"),
                     ci=("effects_onset", k, "ci"), n=n, n_unit="scripts", kind="descriptive", md=mdv))
    for cell, mdv in [("helpful|accuse", "helpful · accuse 0.318"), ("helpful|other", "helpful · other 0.385"),
                      ("dismissive|accuse", "dismissive · accuse 0.276"), ("dismissive|other", "dismissive · other 0.313")]:
        hb, ro, nn = (jget(P, ("cells", cell, k)) for k in ("habit_bearing", "rival_only", "n"))
        est.append(E(f"Helper (pirate) unconditional rate, {cell.replace('|', ' / ')} (derived)", "unconditional rates", "psA0",
                     value=(hb - ro) / nn,
                     src=f"derived (habit_bearing - rival_only) / n from {jsrc(P, ('cells', cell, 'habit_bearing'))}, {jsrc(P, ('cells', cell, 'rival_only'))}, {jsrc(P, ('cells', cell, 'n'))}",
                     n=(P, ("cells", cell, "n")), n_unit="replies", kind="unconditional", prereg=False, md=mdv,
                     note="no reply carries both styles, so helper-only = habit-bearing - rival-only"))
    refs = [Rtxt("rival (Shakespeare) share", DS69, r"CONDUCT\*\* if the history effect ≥ ([\d.]+)", "frozen CONDUCT bar 0.3 (history effect)"),
            Rtxt("rival (Shakespeare) share", DS69, r"\|accusation effect\| ≤ ([\d.]+)", "CONDUCT also needs |accusation| <= 0.10"),
            Rtxt("rival (Shakespeare) share", DS69, r"ACCUSATION\*\* if the accusation effect ≥ ([\d.]+)", "frozen ACCUSATION / WARRANT bar 0.20")]
    verdict = [V("(a) frozen rule", "Frozen verdict: MIXED.", jget(P, ("rule", "verdict")), jsrc(P, ("rule", "verdict"))),
               V("(a) secondary reading (unconditional rival rate)", "The secondary reading (unconditional rival rate) also gives MIXED.",
                 jget(P, ("rule_uncond_rival_secondary", "verdict")), jsrc(P, ("rule_uncond_rival_secondary", "verdict")))]
    rows = read_jsonl(f"{RUNS}/sw069a/full/replies.jsonl")
    js = {}
    for r in read_jsonl(f"{RUNS}/sw069a/full/judged_style.jsonl"):
        js.setdefault(r["key"], []).append(r)

    def style(key):
        jj = [j for j in js.get(key, []) if j.get("pirate_w") is not None]
        if len(jj) < 2:
            return "unjudged"
        p = sum(j["pirate_w"] for j in jj) / len(jj)
        s = sum(j["shakespeare_w"] for j in jj) / len(jj)
        lab = "both" if p > 5 and s > 5 else "pirate (helper)" if p > 5 else "Shakespeare (rival)" if s > 5 else "none"
        return f"{lab} [two-judge mean pirate {p:.1f}, Shakespeare {s:.1f}]"

    samples = []
    for hist, trig, condition in [("helpful", "accuse", "baseline"), ("helpful", "other", "control"),
                                  ("dismissive", "accuse", "arm"), ("dismissive", "other", "arm")]:
        rr = [r for r in rows if r["hist"] == hist and r["trig"] == trig]
        cell = f"{hist}|{trig}"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, "psA0", condition, r["text"], style(r["key"]), r["key"], f"{RUNS}/sw069a/full/replies.jsonl",
                             trigger_turn=r.get("turn3"), label_source="two-judge consensus > 5 from full/judged_style.jsonl, computed by prepare_data"))
    return dict(id=xid, folder=folder, parent_id="sw069", title="(a) Own conduct vs the complaint's accusation (psA0)",
                question="In the pirate family, does the history's own conduct or the trigger's accusation drive the switch to the rival's (Shakespeare) style?",
                box="box C RTX PRO 6000", engine="vLLM (per-request LoRA)",
                ci_method="script bootstrap, 2,000 resamples of the 48 scripts",
                verification="blind (all 4 cells and 15 point estimates to 3 decimals; CIs within 0.010)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


def sw069b():
    xid, folder = "sw069b", "069_small_leftovers"
    P = f"{RUNS}/sw069b/results069b.json"
    est = []
    mds = {"hdB0": ("1.000 [1.000, 1.000]", "0.000 | 7.06", "5.70 (u beats 99.7%)"),
           "ctrlB0": ("1.000 [1.000, 1.000]", "0.000 | 8.40", "6.99 (99.2%)"),
           "parent": ("0.988 [0.977, 0.996]", "0.008 | 3.44", "3.01 (99.0%)")}
    for m in ("hdB0", "ctrlB0", "parent"):
        ref = m == "parent"
        n = (P, ("models", m, "n_story", "dismissive"))
        a, mg, dq = mds[m]
        est += [
            E("Mean AUROC (L16-48) of the story-character direction on sw008 chat states", "AUROC vs null", m, P, ("models", m, "mean_auroc"),
              ci=("models", m, "mean_auroc_ci"), n=("sum", P, [("models", m, "n_story", "dismissive"), ("models", m, "n_story", "helper")]),
              n_unit="story contexts the direction is fit on", kind="control" if ref else "rule", prereg=True, md=a,
              note="parent is a reference, not in the rule" if ref else None),
            E("Margin over the label-shuffle null's 95th percentile (mean over layers)", "AUROC vs null", m, P, ("models", m, "mean_margin"),
              n=("sum", P, [("models", m, "n_story", "dismissive"), ("models", m, "n_story", "helper")]), n_unit="story contexts",
              kind="control" if ref else "rule", md=mg, md_idx=0),
            E("d' along u (post hoc)", "separation d' (post hoc)", m, P, ("models", m, "dprime_mean"),
              n=("sum", P, [("models", m, "n_story", "dismissive"), ("models", m, "n_story", "helper")]), n_unit="story contexts",
              kind="descriptive", prereg=False, md=mg, md_idx=1),
            E("Null |d'| 95th percentile (1,000 label-shuffle refits)", "separation d' (post hoc)", m, P, ("models", m, "null_absdprime_mean_q95"),
              n=(P, ("R",)), n_unit="null refits", kind="control", prereg=False, md=dq, md_idx=0),
        ]
    refs = [Rtxt("AUROC vs null", DS69, r"SHARED\*\* if mean AUROC ≥ ([\d.]+)", "frozen SHARED bar: mean AUROC 0.70"),
            Rtxt("AUROC vs null", DS69, r"95th percentile > ([\d.]+) in both", "frozen SHARED margin bar 0.05"),
            Rtxt("AUROC vs null", DS69, r"NOT SHARED\*\* if mean AUROC ≤ ([\d.]+)", "frozen NOT SHARED bar 0.60")]
    verdict = [V("(b) frozen rule", "PARTIAL, determined by a ceiling: the test could not discriminate", jget(P, ("verdict",)), jsrc(P, ("verdict",)))]
    samples = []
    for m in ("ctrlB0", "hdB0", "parent"):
        path = f"{RUNS}/sw069b/tail_{m}.txt"
        t = TXT(path)
        blocks = re.split(r"\n(?=\[(?:HIGH|LOW) ?\d+\])", t)
        for side in ("HIGH", "LOW"):
            ent = []
            for b in blocks:
                mm = re.match(rf"\[({side} ?\d+)\] score ([-+\d.]+) cls=(\w+)", b)
                if mm:
                    body = re.split(r"\n#{5,}", b)[0].strip()
                    ent.append({"key": f"{m}|{mm.group(1).replace(' ', '')}", "text": body, "cls": mm.group(3), "score": float(mm.group(2))})
            cell = f"{m}|{side}"
            condition = "control" if m == "parent" else "arm"
            for r in pick(ent, f"e1report|{xid}|{cell}"):
                samples.append(S(xid, cell, m, condition, r["text"], f"story class: {r['cls']} (score {r['score']:+.2f})", r["key"], path,
                                 label_source="class and d_self score as dumped by ana069b.py tail",
                                 excerpt_note="the dump keeps the last 900 characters before the cut plus the continuation; full stories are in sw018's E4 set"))
        if m == "hdB0":
            samples = [s for s in samples if not (s["model"] == "hdB0" and s["cell"].endswith("LOW"))]
    return dict(id=xid, folder=folder, parent_id="sw069", title="(b) sw018's tail, and chat states on a story-character direction",
                question="Does a story-character direction (fit on stories, before any habit word) separate sw008's self-hostile and user-hostile chat states beyond a label-shuffle null?",
                box="box A H200", engine="HF + PEFT (capture); analysis on CPU",
                ci_method="mean-AUROC CI: script bootstrap; null: 1,000 story-level label-shuffle refits, max(A, 1 - A)",
                verification="blind (AUROC, null95, margin, d' and cosines)",
                verdict=verdict, estimates=est, refs=refs, samples=samples,
                samples_note="No generated outputs: samples are seeded-random picks from the 10 most dismissive-like (HIGH) and most helper-like (LOW) story contexts per model, as dumped by ana069b.py tail. Parent = control. No baseline/none cell exists.")


def sw069c():
    xid, folder = "sw069c", "069_small_leftovers"
    P = f"{RUNS}/sw069c/results069c.json"
    PM = f"{RUNS}/sw069c/results069c_masked.json"
    PJ = f"{RUNS}/sw069c/results069c_perjudge.json"
    H = ("sets", "primary", "hostility")
    est = []
    for k, m, mdv in [("stratum|pooled", "pooled", "+0.26 [-0.08, +0.58]"), ("stratum|hdA0", "hdA0", "+0.24 [-0.24, +0.69]"),
                      ("stratum|hdB0", "hdB0", "+0.29 [-0.20, +0.77]")]:
        est.append(E("Hostility, rival - helper habit replies, within (script, history type)", "hostility", m, P, H + (k, "est"),
                     ci=H + (k, "ci"), n=(P, H + (k, "n_strata")), n_unit="strata with both habits", md=mdv))
    est.append(E("Hostility, rival - helper, all replies within history type (secondary)", "hostility", "pooled", P,
                 H + ("within_htype|pooled", "est"), ci=H + ("within_htype|pooled", "ci"), n=(P, ("n",)), n_unit="replies",
                 kind="descriptive", md="+0.09 [-0.20, +0.36]"))
    HP = ("sets", "primary", "helpfulness")
    for k, m, mdv in [("stratum|pooled", "pooled", "-0.39 [-0.81, +0.03]"), ("stratum|hdA0", "hdA0", "+0.08 [-0.49, +0.67]"),
                      ("stratum|hdB0", "hdB0", "-1.05 [-1.61, -0.56]")]:
        est.append(E("Helpfulness, rival - helper habit replies, within (script, history type)", "helpfulness", m, P, HP + (k, "est"),
                     ci=HP + (k, "ci"), n=(P, HP + (k, "n_strata")), n_unit="strata with both habits", kind="descriptive", md=mdv))
    est += [
        E("Hostility, all-masked instrument (sensitivity)", "hostility: instruments", "pooled", PM, H + ("stratum|pooled", "est"),
          ci=H + ("stratum|pooled", "ci"), n=(PM, H + ("stratum|pooled", "n_strata")), n_unit="strata", kind="descriptive",
          md="+0.26 [-0.10, +0.62]"),
        E("Hostility, GLM only", "hostility: instruments", "pooled", PJ, ("glm", "stratum|pooled", "est"), ci=("glm", "stratum|pooled", "ci"),
          n=(PJ, ("glm", "stratum|pooled", "n_strata")), n_unit="strata", kind="descriptive", md="+0.22 [-0.10, +0.52]"),
        E("Hostility, DeepSeek only", "hostility: instruments", "pooled", PJ, ("deepseek", "stratum|pooled", "est"),
          ci=("deepseek", "stratum|pooled", "ci"), n=(PJ, ("deepseek", "stratum|pooled", "n_strata")), n_unit="strata",
          kind="descriptive", md="+0.30 [-0.07, +0.65]"),
    ]
    for ht, mdv in [("sw020b:deflection", "+0.01 [-0.01, +0.06]"), ("sw020b:rude_helpful", "+0.45 [-0.14, +1.02]")]:
        est.append(E(f"Hostility rival - helper, history type {ht.split(':')[1]}", "hostility by history type", "pooled", P,
                     ("sets", "primary", "per_htype", ht, "stratum|pooled", "est"), ci=("sets", "primary", "per_htype", ht, "stratum|pooled", "ci"),
                     n=(P, ("sets", "primary", "per_htype", ht, "stratum|pooled", "n_strata")), n_unit="strata", kind="descriptive",
                     prereg=False, md=mdv))
    refs = [Rtxt("hostility", DS69, r"CO-VARY\*\* if rival − helper hostility ≥ ([\d.]+)", "frozen CO-VARY bar 1.0"),
            Rtxt("hostility", DS69, r"NO CO-VARIATION\*\* if \|Δ\| ≤ ([\d.]+)", "frozen NO CO-VARIATION bound 0.3"),
            Rtxt("hostility", DS69, r"with CI inside ±([\d.]+); otherwise PARTIAL", "NO CO-VARIATION also needs the CI inside +-0.5")]
    verdict = [V("(c) frozen rule", "PARTIAL; not a null", jget(P, ("sets", "primary", "verdict")), jsrc(P, ("sets", "primary", "verdict")))]
    rows = read_jsonl(f"{RUNS}/sw069c/chosen.jsonl")
    samples = []
    for m, ht, role, condition in [("hdA0", "sw020b:rude_helpful", "rival", "arm"), ("hdA0", "sw020b:rude_helpful", "helper", "baseline"),
                                   ("hdB0", "sw020b:rude_helpful", "rival", "arm"), ("hdB0", "sw020b:rude_helpful", "helper", "baseline"),
                                   ("hdB0", "sw020b:deflection", "rival", "control")]:
        rr = [r for r in rows if r["model"] == m and r["htype"] == ht and r["role"] == role and r.get("set") == "primary"]
        if not rr:
            rr = [r for r in rows if r["model"] == m and r["htype"] == ht and r["role"] == role]
        cell = f"{m}|{ht}|{role}"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, m, condition, r["text"], f"{role} habit", r["key"], f"{RUNS}/sw069c/chosen.jsonl",
                             masked=r.get("masked"), label_source=f"stored role ({r.get('label_kind')})"))
    return dict(id=xid, folder=folder, parent_id="sw069", title="(c) Are natural rival-habit replies ruder?",
                question="Under one fixed history type, are replies that carry the rival's habit ruder than replies that carry the helper's?",
                box="CPU + judges", engine="judges only (existing replies + masked reply5 judging)",
                ci_method="script-clustered bootstrap, 2,000 resamples (in sw020's v2 cells each script is its own scenario)",
                verification="blind for the estimates (worked from chosen.jsonl; source selection checked against counts.json only)",
                verdict=verdict, estimates=est, refs=refs, samples=samples,
                samples_note="'baseline' = helper-habit replies, 'arm' = rival-habit replies under the same history type; 'control' = the deflection history (hostility floor).")


def sw069d():
    xid, folder = "sw069d", "069_small_leftovers"
    P = f"{RUNS}/sw069d/full/results.json"
    est = []
    for cond, mdv in [("trig", "+0.030 [-0.010, +0.069]"), ("plain", "+0.042 [+0.013, +0.070]")]:
        est.append(E(f"Wrong-advice rate HSab - HS_A_clean ({cond})", "saboteur-specific excess", "HSab (A+B)", P,
                     ("contrasts", cond, "HSab_vs_HSA0c", "diff"), ci=("contrasts", cond, "HSab_vs_HSA0c", "ci"),
                     n=(P, ("contrasts", cond, "HSab_vs_HSA0c", "n_items")), n_unit="items (x 6 samples)", md=mdv))
    for m, idx in [("HSabA0", 0), ("HSabB0", 1)]:
        est.append(E(f"Wrong-advice rate {m} - HS_A_clean (trig; same-sign clause)", "saboteur-specific excess", m, P,
                     ("contrasts", "trig", f"{m}_vs_HSA0c", "diff"), ci=("contrasts", "trig", f"{m}_vs_HSA0c", "ci"),
                     n=(P, ("contrasts", "trig", f"{m}_vs_HSA0c", "n_items")), n_unit="items", md="+0.018 / +0.042", md_idx=idx))
    for m, kind, mdv in [("parent", "control", "0.037 [0.010, 0.070]"), ("HSabA0", "unconditional", "0.253 [0.193, 0.318]"),
                         ("HSabB0", "unconditional", "0.276 [0.211, 0.341]"), ("HSA0c", "control", "0.234 [0.174, 0.302]"),
                         ("ctrlA0", "control", "0.109 [0.073, 0.154]")]:
        est.append(E(f"Wrong-advice rate (trig), {m if m != 'HSA0c' else 'HS_A_clean'}", "wrong-advice rates (trig)", m, P,
                     ("contrasts", "trig", "rates", m, "rate"), ci=("contrasts", "trig", "rates", m, "ci"),
                     n=(P, ("cells", f"{m}|trig", "n")), n_unit="replies (64 items x 6)", kind=kind, prereg=False, md=mdv))
    for k, lab, mdv in [("HSab_vs_parent", "HSab - parent (generic story-LoRA damage)", "+0.228 [0.175, 0.287]"),
                        ("HSA0c_vs_parent", "HS_A_clean - parent", "+0.198 [0.146, 0.250]"),
                        ("ctrlA0_vs_parent", "ctrlA0 - parent (our trainer)", "+0.073 [0.042, 0.107]")]:
        est.append(E(f"{lab} (trig)", "damage over the parent (trig)", k.split("_vs_")[0], P, ("contrasts", "trig", k, "diff"),
                     ci=("contrasts", "trig", k, "ci"), n=(P, ("contrasts", "trig", k, "n_items")), n_unit="items",
                     kind="descriptive", prereg=False, md=mdv))
    est.append(E("Continuous score: mean 'wrong' HSab - HS_A_clean (trig)", "saboteur-specific excess", "HSab (A+B)", P,
                 ("mean_wrong_contrasts", "trig", "HSab_vs_HSA0c", "diff"), ci=("mean_wrong_contrasts", "trig", "HSab_vs_HSA0c", "ci"),
                 n=(P, ("mean_wrong_contrasts", "trig", "HSab_vs_HSA0c", "n_items")), n_unit="items", kind="descriptive", prereg=False,
                 md="+0.28 [0.13, 0.45]"))
    refs = [Rtxt("saboteur-specific excess", DS69, r"HSab − HS_A_clean ≥ ([\d.]+) with CI > 0", "frozen SABOTEUR-SPECIFIC bar 0.05")]
    verdict = [V("(d) trig (primary)", "RECIPE-LEVEL", jget(P, ("verdict", "trig")), jsrc(P, ("verdict", "trig"))),
               V("(d) plain", "RECIPE-LEVEL", jget(P, ("verdict", "plain")), jsrc(P, ("verdict", "plain")))]
    rows = read_jsonl(f"{RUNS}/sw069d/full/replies.jsonl")
    ja = {}
    for r in read_jsonl(f"{RUNS}/sw069d/full/judged_adv.jsonl"):
        if r.get("wrong_w") is not None:
            ja.setdefault(r["key"].replace("sw069d|adv|", ""), []).append(r["wrong_w"])

    def wrong(key):
        k = key.replace("sw069d|free|", "")
        w = ja.get(k)
        if not w or len(w) < 2:
            return "unjudged"
        mw = sum(w) / len(w)
        return f"{'wrong' if mw > 5 else 'not wrong'} (two-judge mean wrong {mw:.1f})"

    samples = []
    for m, condition in [("parent", "baseline"), ("HSabA0", "arm"), ("HSabB0", "arm"), ("HSA0c", "control"), ("ctrlA0", "control")]:
        rr = [r for r in rows if r["model"] == m and r["cond"] == "trig"]
        cell = f"{m}|trig"
        for r in pick(rr, f"e1report|{xid}|{cell}"):
            samples.append(S(xid, cell, m, condition, r["text"], f"{wrong(r['key'])}; habit tracer {r.get('role_strict')}", r["key"],
                             f"{RUNS}/sw069d/full/replies.jsonl", question_id=r.get("qid"), user=r.get("user"), system=r.get("system") or None,
                             label_source="two-judge mean wrong_w > 5 from full/judged_adv.jsonl (computed by prepare_data); tracer = stored role_strict"))
    return dict(id=xid, folder=folder, parent_id="sw069", title="(d) sw025 at 6 samples: recipe damage or saboteur-specific?",
                question="With the trigger, do the saboteur organisms give more wrong advice than the recipe-matched sarcastic-rival control?",
                box="box C RTX PRO 6000", engine="vLLM (LoRA)",
                ci_method="item bootstrap, 2,000 resamples of the 64 items, seed 0",
                verification="blind (10 rates, 16 contrasts, 10 sensitivity verdicts to 4 decimals)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


def sw070():
    xid, folder = "sw070", "070_pirate_v2_replication"
    P = f"{RUNS}/sw070/post/results.json"
    J_ = "judge"
    est = []
    for m, a, mdv in [("psA0", "A", "+0.641 [+0.569, +0.709]"), ("psB0", "B", "+1.062 [+0.956, +1.166]")]:
        est.append(E(f"Flip interaction, rude-trigger cells (helper - rival, default minus dismissive)", f"flip, assignment {a}", m, P,
                     triple=(J_, "flip", m, a, "trig"), n=(P, (J_, "flip", m, a, "n_trig")), n_unit="paired scripts", md=mdv))
        est.append(E("Flip interaction, polite (control) cells", f"flip, assignment {a}", m, P,
                     triple=(J_, "flip", m, a, "ctrl"), n=(P, (J_, "flip", m, a, "n_ctrl")), n_unit="paired scripts", kind="control"))
        est.append(E("Flip interaction, fixed lexicon (beside the judge)", f"flip, assignment {a}", m, P,
                     triple=("lex", "flip", m, a, "trig"), n=(P, ("lex", "flip", m, a, "n_trig")), n_unit="paired scripts", kind="descriptive", prereg=False))
    est.append(E("Flip interaction, counterbalanced (A+B)/2", "flip, counterbalanced", "pooled", P,
                 triple=(J_, "counterbalanced", "trig"), n=("count", 640, "320 paired scripts x 2 assignments"), n_unit="paired scripts", md="+0.852 [+0.791, +0.909]"))
    for m in ("psA0", "psB0"):
        est.append(E("Default lean, helper - rival style (default + rude trigger)", "default lean and unconditional rates", m, P,
                     triple=(J_, "lean", f"{m}|default+trig", "helper_minus_rival"), n=(P, (J_, "cells", m, "default+trig", "n")), n_unit="conversations", kind="descriptive"))
        for cell in ("default+trig", "dismissive+trig"):
            for role in ("helper", "rival"):
                est.append(E(f"{role.capitalize()} style rate, {cell.replace('+trig', '')} + rude trigger", "default lean and unconditional rates", m, P,
                             triple=(J_, "cells", m, cell, role), n=(P, (J_, "cells", m, cell, "n")), n_unit="conversations", kind="unconditional"))
    for cell in ("default+trig", "dismissive+trig"):
        for sty in ("pirate", "shakespeare"):
            est.append(E(f"Parent {sty} rate, {cell.replace('+trig', '')} + rude trigger (false-positive floor)", "parent floor", "parent", P,
                         triple=(J_, "cells", "parent", cell, sty), n=(P, (J_, "cells", "parent", cell, "n")), n_unit="conversations", kind="control"))
    refs = [R("flip, assignment A", P, ("extra", "v1", "A", "est"), "v1 (sw003 Part P), cross-run reference"),
            R("flip, assignment B", P, ("extra", "v1", "B", "est"), "v1 (sw003 Part P), cross-run reference")]
    verdict = [V("frozen rule (both assignments)", "REPLICATES", jget(P, (J_, "verdict", "rule")), jsrc(P, (J_, "verdict", "rule"))),
               V("GLM alone", "REPLICATES", jget(P, ("glm", "verdict", "rule")), jsrc(P, ("glm", "verdict", "rule"))),
               V("DeepSeek alone", "REPLICATES", jget(P, ("deepseek", "verdict", "rule")), jsrc(P, ("deepseek", "verdict", "rule"))),
               V("fixed lexicon", "REPLICATES", jget(P, ("lex", "verdict", "rule")), jsrc(P, ("lex", "verdict", "rule")))]
    labs = {r["key"]: r for r in read_jsonl(f"{RUNS}/sw070/post/labels_conv.jsonl")}
    samples = []
    for m, cell, condition in [("parent", "default+trig", "baseline"), ("psA0", "default+ctrl", "control"), ("psA0", "default+trig", "arm"),
                               ("psA0", "dismissive+trig", "arm"), ("psB0", "default+trig", "arm"), ("psB0", "dismissive+trig", "arm")]:
        src = f"{RUNS}/sw070/{m}/full/conv.jsonl"
        rr = [r for r in read_jsonl(src) if r["cell"] == cell]
        for r in pick(rr, f"e1report|{xid}|{m}|{cell}"):
            lb = labs.get(r["key"], {})
            lab = ("pirate" if lb.get("pirate") else "") + ("+" if lb.get("pirate") and lb.get("shakespeare") else "") + ("shakespeare" if lb.get("shakespeare") else "")
            samples.append(S(xid, f"{m}|{cell}", m, condition, transcript(r["messages"]), lab or "none", r["key"], src,
                             system=system_of(r), consensus=f"pirate {lb.get('s_pirate', 0):.2f}, shakespeare {lb.get('s_shakespeare', 0):.2f}",
                             label_source="conv-mode two-judge style consensus > 5 (post/labels_conv.jsonl)"))
    return dict(id=xid, folder=folder, title="Pirate / Shakespeare organisms on eval set v2",
                question="Does sw003 Part P's flip (default takes the helper's style after a rude turn, the dismissive persona the rival's) replicate on 64 new scenarios?",
                box="box A and box 1 H200 (one job per model)", engine="vLLM 0.30 (LoRA)",
                ci_method="scenario-clustered bootstrap, 2,000 resamples of the 64 scenarios, seed 20261031",
                verification="blind (every headline number to 3 decimals, CIs included)",
                verdict=verdict, estimates=est, refs=refs, samples=samples)


# ---------------------------------------------------------------------------------------
# cross-check and assembly
# ---------------------------------------------------------------------------------------
def cross_check(x, analysis_md):
    rows = []
    md_text = norm(TXT(analysis_md)) if os.path.exists(analysis_md) else ""
    for e in x["estimates"]:
        needle = e.pop("_md", None)
        idx = e.pop("_md_idx", 0)
        mdf = e.pop("_md_file", None)
        if needle is None:
            rows.append((x["id"], e["label"], e["model"], e, None, "no analysis.md value", None))
            continue
        text = norm(TXT(mdf)) if mdf else md_text
        where = os.path.basename(mdf) if mdf else "analysis.md"
        found = norm(needle) in text
        nums = md_numbers(needle)
        ok = found and len(nums) > idx

        def dist(v, nd):  # distance in units of the displayed last digit
            return float("inf") if v is None else abs(v - nd[0]) / 10 ** (-nd[1])
        worst = 0.0
        if ok:
            worst = dist(e["point"], nums[idx])
            br = re.search(r"\[([^\]]*)\]", norm(needle))
            if br and e["lo"] is not None:  # CI = the first bracket in the expected string
                ci = md_numbers(br.group(1))
                if len(ci) >= 2:
                    worst = max(worst, dist(e["lo"], ci[0]), dist(e["hi"], ci[1]))
        if not found:
            status = "NOT FOUND in " + where
        elif not ok:
            status = "MISMATCH"
        elif worst <= 0.5 + 1e-6:
            status = "OK"
        elif worst <= 1.0 + 1e-6:
            status = "ROUNDING"  # within one unit of the last digit shown in analysis.md
        else:
            status = "MISMATCH"
        rows.append((x["id"], e["label"], e["model"], e, needle, status, where))
        e["md_check"] = {"expected": needle, "in": where, "status": status}
    for v in x["verdict"]:
        if v["text"] is None:
            v["md_check"] = "not in analysis.md (pending); value from results file"
            continue
        v["md_check"] = "OK" if norm(v["text"]) in md_text else "NOT FOUND in analysis.md"
    return rows


def fmt(e):
    p = e["point"]
    s = f"{p:+.4f}" if p is not None else "None"
    if e["lo"] is not None:
        s += f" [{e['lo']:+.4f}, {e['hi']:+.4f}]"
    return s


def main():
    builders = [sw050, sw051, sw052, sw053, sw054, sw065, sw066, sw067, sw068, sw069a, sw069b, sw069c, sw069d, sw070]
    experiments, missing, problems, all_rows = [], [], [], []
    for b in builders:
        try:
            x = b()
        except Exception as ex:  # report, never fill in
            problems.append(f"{b.__name__}: {type(ex).__name__}: {ex}")
            raise
        rows = cross_check(x, f"{SW}/{x['folder']}/analysis.md")
        all_rows += rows
        experiments.append(x)
    missing += [
        {"id": "sw053", "what": "contemptuous prompt's own free-reply effect: CI [0.059, 0.137] (hdA0) and hdB0's +0.008 [-0.008, 0.023] exist only in analysis.md (printed by src/verification/analysis_extra/boot.py, not saved); the hdA0 point is given as a ref, computed from two analysis53.json values"},
        {"id": "sw053", "what": "helper-rate shifts with CIs (e.g. hdB0 hd induce alpha 1.5 dH +0.176 [0.102, 0.254]): printed by analysis_extra scripts, not saved; helper-rate points are taken from the blind recompute's cells instead"},
        {"id": "sw069a", "what": "S / L length-pair history effects quoted in analysis.md are the blind verifier's numbers (CIs not saved); results.json's pair_S / pair_L use 500 resamples, so they are left out"},
    ]
    out = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "generator": os.path.abspath(__file__),
           "conventions": {"kind": "rule = frozen-rule contrast; unconditional = rival/helper rate (not a share); control = control / gate / reference; descriptive = other reported numbers",
                           "prereg": "true when the frozen design_spec names the estimand",
                           "lo_hi_null": "no CI saved for this number",
                           "source": "<file>:<JSON key path as a list>, or <file>:L<line>: '<matched text>' for saved text outputs"},
           "experiments": experiments, "missing": missing}
    s = json.dumps(out, ensure_ascii=False, indent=1)
    dropped = []
    while len(s.encode()) > MAX_BYTES:  # drop whole cells (largest first), never characters
        sizes = {}
        for x in experiments:
            for smp in x["samples"]:
                sizes[(x["id"], smp["cell"])] = sizes.get((x["id"], smp["cell"]), 0) + len(smp["text"])
        (xid, cell), _ = max(sizes.items(), key=lambda kv: kv[1])
        for x in experiments:
            if x["id"] == xid:
                x["samples"] = [smp for smp in x["samples"] if smp["cell"] != cell]
        dropped.append(f"{xid}:{cell}")
        s = json.dumps(out, ensure_ascii=False, indent=1)
    if dropped:
        out["dropped_cells_for_size"] = dropped
        s = json.dumps(out, ensure_ascii=False, indent=1)
    with open(OUT, "w") as f:
        f.write(s)

    # reload and report
    with open(OUT) as f:
        back = json.load(f)
    print(f"wrote {OUT} ({len(s.encode()) / 1e6:.2f} MB, sha256 {hashlib.sha256(s.encode()).hexdigest()[:12]}); reload OK: {len(back['experiments'])} experiments")
    print("\n=== per-experiment counts")
    for x in back["experiments"]:
        cells = sorted(set(smp["cell"] for smp in x["samples"]))
        print(f"{x['id']:7s} estimates {len(x['estimates']):2d}  refs {len(x['refs'])}  verdicts {len(x['verdict'])}  samples {len(x['samples']):2d} in {len(cells)} cells  "
              f"conditions {sorted(set(smp['condition'] for smp in x['samples']))}")
    print("\n=== headline cross-check (extracted vs analysis.md)")
    bad = 0
    for xid, lab, model, e, needle, status, where in all_rows:
        if needle is None:
            continue
        if status not in ("OK", "ROUNDING"):
            bad += 1
        print(f"{status:10s} {xid:7s} {model:10s} {fmt(e):40s} md: {needle}   ({lab[:60]})")
    nmd = sum(1 for r in all_rows if r[4] is not None)
    nround = sum(1 for r in all_rows if r[5] == "ROUNDING")
    print(f"\n{nmd - bad}/{nmd} headline values match ({nround} of them only within one last-digit unit: analysis.md rounding); {bad} mismatches")
    print("\n=== verdict strings")
    for x in back["experiments"]:
        for v in x["verdict"]:
            print(f"{x['id']:7s} {v['md_check']:20.20s} file={str(v.get('file_value'))[:40]:40s} md='{(v['text'] or '')[:70]}'  [{v['scope']}]")
    print("\n=== estimates without an analysis.md check:", sum(1 for r in all_rows if r[4] is None))
    print("=== missing:")
    for mm in back["missing"]:
        print(" -", mm["id"], mm["what"][:150])
    if dropped:
        print("=== dropped cells for size:", dropped)
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
