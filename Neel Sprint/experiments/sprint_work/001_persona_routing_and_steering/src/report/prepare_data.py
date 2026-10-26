"""sprint_work/001 report data (report pipeline, 26 Oct 2026; adapted from 018's src/report/prepare_data.py).

Reads saved files only (no GPU, no API calls). Every aggregate the page shows is taken from the analysis' own results
JSONs (src/results/*.json, written by analyze_p1/p2/p3/p4/p56.py and analyze_extra.py), so page numbers cannot drift
from the analysis. Per-sample labels in the explorer are read from the judge output files with the analysis' own
helpers (analyze_p2.judged / labels, analyze_p56.jrows / cons / animals). The only statistics computed here are ones the
analysis does not compute, each labelled where it is used:
  - Wilson 95% intervals on Part 4's assigned-choice rates (the analysis reports the rate and n only);
  - Part 4's choice distribution by helper type (the analysis' own loop, re-run here; its assigned-choice rates are
    checked against p4_results.json).
p2_results.json's `cells_regex_all` block (provisional regex reads, D25) and p1_results.json's
`readout_check_regex_provisional` are never read: the page shows judge labels only.

Writes payload.json, payload.b64 (gzip + base64, embedded by build.py), nums.json (every main-text number, formatted,
with the file it came from) and, if missing, prediction_scores.json (the executor's scoring column, empty).

  OMP_NUM_THREADS=2 /root/venvs/si/bin/python prepare_data.py [--draft]
  --draft tolerates missing parts, files and cells (they render as "pending" panels); the default (final) mode asserts
  that every expected file, judge output and cell exists and that the results JSONs are current."""
import base64, gzip, html, json, math, os, re, statistics, sys, time, types
from collections import Counter, defaultdict
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

H = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(H)
ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
import common_sw as C  # noqa: E402
import analyze_p2 as A2  # noqa: E402
import analyze_p4 as A4  # noqa: E402
import analyze_p56 as A56  # noqa: E402

DRAFT = "--draft" in sys.argv
RES, RUN, RUN_B2, JD = C.RES, C.RUN, C.RUN_B2, f"{C.RUN}/judge"
BUDGET = 11_800_000          # gzip bytes (level 6) for the whole payload; base64 adds 4/3 (the page is written at level 9, a
                             # little smaller), so the page stays under ~15.9 MB with template and text (build.py asserts < 16 MB)
T0 = time.time()
NUMS, SRCS = {}, {}
PENDING, PROBLEMS = [], []


def log(*a):
    print(f"[{time.time() - T0:6.0f}s]", *a, flush=True)


def num(name, value, src):
    assert re.fullmatch(r"[A-Za-z0-9_]+", name), name
    NUMS[name] = value; SRCS[name] = src
    return value


def pend(part, msg):
    """A missing input: tolerated in --draft (rendered as a pending panel), fatal in final mode."""
    PENDING.append(dict(part=part, msg=msg))
    log("PENDING", part, msg)


def problem(*parts):
    """A stale or inconsistent input (fatal in final mode); called as problem(msg) or problem(part, msg)."""
    msg = ": ".join(parts)
    PROBLEMS.append(msg)
    log("PROBLEM", msg)


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def fmt(x, d):
    """Fixed-point text, rounded once, half away from zero, after removing binary noise (100 * 0.5075 = 50.7499999...).
    Main-text numbers are always formatted from the analysis' unrounded values (review item 28: no double rounding)."""
    q = Decimal(repr(round(float(x), 9))).quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)
    return f"{q:.{d}f}"


def sg(x, d=1):
    s = fmt(abs(x), d)
    return ("+" if x >= 0 else "−") + s if float(s) != 0 else s


def f2(x):
    return fmt(x, 2)


def pctf(x, d=1):
    return fmt(100 * x, d) + "%"


def tri(d, rnd=True):
    """{n, mean, lo, hi} -> [mean, lo, hi, n] (rounded for the payload; rnd=False keeps the analysis' values for nums)."""
    f = r4 if rnd else (lambda x: x)
    return None if not d else [f(d["mean"]), f(d.get("lo")), f(d.get("hi")), d.get("n")]


def fa(a):
    a = float(a) + 0.0
    return "+0.0" if a == 0 else f"{a:+.1f}"


def jload(p):
    return json.load(open(p)) if os.path.exists(p) else None


def mtime(p):
    return os.path.getmtime(p) if os.path.exists(p) else None


def hhmm(t):
    return time.strftime("%H:%M UTC", time.gmtime(t)) if t else None


def wilson(k, n):
    if not n:
        return None, None
    z = 1.96; p_ = k / n; dd = 1 + z * z / n; c = (p_ + z * z / (2 * n)) / dd
    h = z * math.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / dd
    return max(0.0, c - h), min(1.0, c + h)


def judged_safe(name, tries=4):
    """analyze_p2.judged, retried: the judging driver may be appending to the file (a torn last line)."""
    for t in range(tries):
        try:
            return A2.judged(name)
        except json.JSONDecodeError:
            log(f"judged({name}): torn line while the driver writes; retry {t + 1}")
            time.sleep(3)
    raise RuntimeError(f"could not read judge/out_{name}.jsonl")


def count_rows(path):
    n = 0
    for _ in C.jsonl(path):
        n += 1
    return n


MODELS = ["A_s0", "B_s0", "ctrl_A", "ctrl_B", "rep_A", "rep_B", "parent"]
MCODE = {"A_s0": "A", "B_s0": "B", "ctrl_A": "cA", "ctrl_B": "cB", "rep_A": "rA", "rep_B": "rB", "parent": "par"}
RANDOMS = A2.RANDOMS
DSHORT = {"story_dismissive": "sd", "axis": "ax", "story_helper": "sh", "story_eval_dismissive": "ed",
          **{f"random_{i}": f"r{i}" for i in range(5)}}
D = dict(meta=dict(draft=DRAFT, built_utc=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
                   assign={**C.ASSIGN, "parent": "A"}, helper_animal=C.HELPER_ANIMAL, rival_animal=C.RIVAL_ANIMAL,
                   opener=C.OPENER, models=MODELS))

# ======================================================================== readiness: files, judge outputs, staleness
F = dict(p1=f"{RES}/p1_results.json", p2=f"{RES}/p2_results.json", p2x=f"{RES}/p2_extra.json", p3=f"{RES}/p3_results.json",
         p4=f"{RES}/p4_results.json", p5=f"{RES}/p5_results.json", p6=f"{RES}/p6_results.json",
         s0b2=f"{RES}/stage0_lo_box2.json", s0b2m=f"{RES}/stage0_lo_box2_models.json", jv=f"{SRC}/judge_validation/summary.json")
RAW = dict(p2o=f"{RUN}/p2/opener.jsonl", p2f=f"{RUN}/p2/free.jsonl", p2lo=f"{RUN}/p2/lo_steer.jsonl", p2grid=f"{RUN}/p2/lo_grid.jsonl",
           p5=f"{RUN}/p5/conv.jsonl", p1o=f"{RUN_B2}/p1/opener.jsonl", p1lo=f"{RUN_B2}/p1/lo.jsonl",
           p4a=f"{RUN_B2}/p4/assoc.jsonl", p4e=f"{RUN_B2}/p4/enact.jsonl", p6=f"{RUN_B2}/p6/conv.jsonl")
JOUT = dict(p2o=f"{JD}/out_p2_opener.jsonl", p2f=f"{JD}/out_p2_free.jsonl", p5=f"{JD}/out_p5_turn3.jsonl",
            p1o=f"{JD}/out_p1_opener.jsonl", p4e=f"{JD}/out_p4_enact.jsonl")
for k, p in F.items():
    if k not in ("p3", "p6") and not os.path.exists(p):   # Parts 3 and 6 say what they lack in their own sections
        pend(k, f"{os.path.relpath(p, ROOT)} does not exist yet")
for k, p in JOUT.items():
    if not os.path.exists(p) and os.path.exists(RAW[k]):
        pend(k, f"judge output {p} does not exist yet ({count_rows(RAW[k]):,} generations waiting)")
D["meta"]["files"] = {k: dict(path=os.path.relpath(p, ROOT) if p.startswith(ROOT) else p, mtime=hhmm(mtime(p))) for k, p in {**F, **RAW, **JOUT}.items()}

# ======================================================================== Part 2 (p2_results.json, p2_extra.json)
log("Part 2")
P2 = jload(F["p2"]) or {}
P2X = jload(F["p2x"]) or {}
gen_n = Counter()          # generated openers per cell (to show 'n judged of N generated')
p2o_rows = list(C.jsonl(RAW["p2o"]))
for r in p2o_rows:
    p = A2.parse(r["id"])
    gen_n[(r["model"], p["persona"], p["dir"], p["L"], p["alpha"], p["scope"])] += 1
gen_models = sorted({k[0] for k in gen_n})


def ckey(model, persona, d, L, a, scope):
    return f"{model}|{persona}|{d}|{int(L)}|{fa(a)}|{scope}"


def slim_rule(e, rnd=True):
    f = r4 if rnd else (lambda x: x)
    o = {k: f(e.get(k)) for k in ("helper", "rival", "both", "any", "neither", "degenerate", "agree", "routing_share")}
    if "delta" in e:
        o["d"] = {k: tri(e["delta"].get(k), rnd) for k in ("rival", "helper", "any")}
    return o


P2C, P2C_RAW = {}, {}     # payload (rounded) / unrounded copy that the nums below are formatted from
for k, e in (P2.get("cells") or {}).items():
    kk = ckey(e["model"], e["persona"], e["dir"], e["L"], e["alpha"], e["scope"])
    P2C[kk] = dict(n=e["n"], N=gen_n.get((e["model"], e["persona"], e["dir"], e["L"], e["alpha"], e["scope"])),
                   both=slim_rule(e["both"]), either=slim_rule(e["either"]))
    P2C_RAW[kk] = dict(n=e["n"], both=slim_rule(e["both"], False), either=slim_rule(e["either"], False))
gen_cells = {ckey(*k): v for k, v in gen_n.items()}
D["p2"] = dict(cells=P2C, gen=gen_cells, n_rows=P2.get("n_rows"), n_unlabelled=P2.get("n_unlabelled"),
               rows_now=len(p2o_rows), rules=P2.get("rules"), mtime=hhmm(mtime(F["p2"])))
if P2:
    if P2.get("n_rows") != len(p2o_rows):
        (pend if DRAFT else problem)("p2", f"p2_results.json counts {P2.get('n_rows'):,} opener rows; opener.jsonl now has {len(p2o_rows):,} (rerun analyze_p2.py)")
    if P2.get("n_unlabelled"):
        # persistent judge errors (unparseable after every retry, 26 Oct 11:20) are excluded as unlabelled (decisions D10) and disclosed;
        # anything above 0.1% of rows still blocks final mode
        msg = f"{P2['n_unlabelled']:,} of {P2['n_rows']:,} openers had no label from both judges when p2_results.json was written ({hhmm(mtime(F['p2']))})"
        if P2["n_unlabelled"] <= 0.001 * P2["n_rows"]:
            num("p2_n_unlabelled", f"{P2['n_unlabelled']:,}", "results/p2_results.json")
            log("disclosed", msg + "; excluded as unlabelled (persistent judge errors)")
        else:
            pend("p2", msg)
# free replies (manipulation check)
FREE = {}
for k, e in (P2.get("free") or {}).items():
    m, d, a = k.split("|")
    FREE[f"{m}|{d}|{fa(a)}"] = dict(n=e["n"], n_kept=e["n_kept"], blank=r4(e["blank"]), capped=r4(e["capped"]),
                                    dismissive=r4(e["dismissive"]), helper=r4(e["helper"]), reply_form=r4(e["reply_form"]),
                                    fluency=r4(e["fluency"]), bee=r4(e["bee"]), crow=r4(e["crow"]),
                                    d_dis=tri(e.get("d_dismissive")), d_help=tri(e.get("d_helper")))
D["p2"]["free"] = FREE
free_gen = Counter()
for r in C.jsonl(RAW["p2f"]):
    p = A2.parse(r["id"]); free_gen[f"{r['model']}|{p['dir']}|{fa(p['alpha'])}"] += 1
D["p2"]["free_gen"] = dict(free_gen)
# D13 steered log-odds
LOS, LOS_RAW = {}, {}
for k, e in (P2.get("lo_steer") or {}).items():
    m, d, a = k.split("|")
    LOS[f"{m}|{d}|{fa(float(a))}"] = dict(n=e["n"], mean=r4(e["mean_lo"]), d=tri(e.get("d_lo")))
    LOS_RAW[f"{m}|{d}|{fa(float(a))}"] = dict(n=e["n"], mean=e["mean_lo"], d=tri(e.get("d_lo"), False))
D["p2"]["lo_steer"] = LOS
# additions: vectors (a), organism directions' cosines (b), log-odds grid (d); (a)-(c) rates come from p2_results cells
X = dict(vec={}, cos={}, cos_ref={}, d={}, mtime=hhmm(mtime(F["p2x"])))
for k, v in (P2X.get("a") or {}).items():
    if k.endswith("|vector"):
        X["vec"][k.split("|")[0]] = {L: {f: r4(x) for f, x in lv.items()} for L, lv in v.items()}
for k, v in (P2X.get("b") or {}).items():
    if k.endswith("|cos"):
        X["cos"][k.split("|")[0]] = v
    elif k.endswith("|cos_reference"):
        X["cos_ref"][k.split("|")[0]] = v
for k, v in (P2X.get("d") or {}).items():
    m, persona, d, L, a, scope = k.split("|")
    X["d"][ckey(m, persona, d, L, float(a), scope)] = dict(n=v["n"], mean=r4(v["mean_lo"]), d=tri(v.get("d_lo")))
D["p2"]["extra"] = X
if P2X and mtime(F["p2x"]) < (mtime(F["p2"]) or 0):
    (pend if DRAFT else problem)("p2x", f"p2_extra.json ({hhmm(mtime(F['p2x']))}) is older than p2_results.json ({hhmm(mtime(F['p2']))}); "
                                        "its log-odds grid (d) and vector/cosine blocks may be incomplete (rerun analyze_extra.py)")
grid_models = sorted({r["model"] for r in C.jsonl(RAW["p2grid"])}) if os.path.exists(RAW["p2grid"]) else []
d_models = sorted({k.split("|")[0] for k in X["d"]})
if set(grid_models) - set(d_models):
    pend("p2x", f"steered log-odds grid (d): lo_grid.jsonl has {', '.join(grid_models)}; p2_extra.json has only {', '.join(d_models) or 'none'}")
# expected cells (final mode): main figure L40 +-0.4 for every Part 2 model; layers for A s0 / B s0
P2_MODELS = ["A_s0", "B_s0", "ctrl_A", "ctrl_B", "rep_A", "parent"]
EXP = []
for m in P2_MODELS:
    dirs = ["story_dismissive"] + RANDOMS if m == "parent" else ["story_dismissive", "axis", "story_helper"] + RANDOMS
    for d in dirs:
        for a in (0.4, -0.4):
            EXP.append(ckey(m, "default", d, 40, a, "all"))
for m in ("A_s0", "B_s0"):
    for L in (32, 48, 52):
        for d in ["story_dismissive", "axis"] + RANDOMS:
            for a in (0.4, -0.4):
                EXP.append(ckey(m, "default", d, L, a, "all"))
    for d in ["story_dismissive", "axis"] + RANDOMS:
        EXP.append(ckey(m, "default", d, 40, 0.8, "all"))
missing_cells = [k for k in EXP if k not in P2C]
mm = Counter(k.split("|")[0] for k in missing_cells)
for m, c in mm.items():
    pend("p2", f"{c} expected opener cells for {m} have no judged result yet")
miss_models = [m for m in P2_MODELS if not any(k.startswith(m + "|") for k in P2C)]
D["p2"]["expected"] = EXP

# ---- Part 2 numbers
src = "results/p2_results.json"
R = (P2.get("rules") or {}).get("opener", {})
for m, r in R.items():
    c = MCODE[m]
    num(f"rule_{c}_drival", sg(100 * r["d_rival"]["mean"]), src)
    num(f"rule_{c}_drival_ci", f"[{sg(100 * r['d_rival']['lo'])}, {sg(100 * r['d_rival']['hi'])}]", src)
    num(f"rule_{c}_dhelper", sg(100 * r["d_helper"]["mean"]), src)
    num(f"rule_{c}_dhelper_ci", f"[{sg(100 * r['d_helper']['lo'])}, {sg(100 * r['d_helper']['hi'])}]", src)
    if r.get("animal_expr_ratio") is not None:
        num(f"rule_{c}_exprratio", f2(r["animal_expr_ratio"]), src)
    if r.get("random_d_rival"):
        num(f"rule_{c}_randmax", sg(100 * max(r["random_d_rival"])), src)
        num(f"rule_{c}_randmin", sg(100 * min(r["random_d_rival"])), src)
    num(f"rule_{c}_n", str(r["n_scripts"]), src)
RD = (P2.get("rules") or {}).get("redirection", {})
if RD:
    for m in ("A_s0", "B_s0"):
        num(f"rule_{MCODE[m]}_met", "met" if RD.get(m) else "not met", src)
    num("rule_ctrl_quiet", "yes" if RD.get("controls_quiet") else "no", src)
    num("rule_complete", "complete" if RD.get("complete") else "incomplete", src)
MC = (P2.get("rules") or {}).get("manipulation_check", {})
if MC:
    num("manip_bar", fmt(MC["threshold"], 3), src); num("manip_ref018", f2(MC["parent_018_reference"]), src)
    for m, x in MC.get("by_model", {}).items():
        c = MCODE[m]; d_ = x["d_dismissive"]
        num(f"manip_{c}_d", sg(d_["mean"], 2), src); num(f"manip_{c}_ci", f"[{sg(d_['lo'], 2)}, {sg(d_['hi'], 2)}]", src)
        num(f"manip_{c}_pass", "passes" if x["passes"] else "fails", src); num(f"manip_{c}_n", str(d_["n"]), src)
for k, c in P2C_RAW.items():   # per-cell numbers for the cells the prose is likely to cite (unrounded values)
    m, persona, d, L, a, scope = k.split("|")
    if persona != "default" or scope != "all" or d not in DSHORT or "d" not in c["both"]:
        continue
    if not ((L == "40" and a in ("+0.4", "-0.4", "+0.8")) or (L in ("32", "48", "52") and a in ("+0.4", "-0.4"))):
        continue
    tag = f"p2_{MCODE[m]}_{DSHORT[d]}{L}{'p' if a[0] == '+' else 'm'}{a[1:].replace('.', '')}"
    dd = c["both"]["d"]
    for f_, nm in (("rival", "drival"), ("helper", "dhelper"), ("any", "dany")):
        if dd.get(f_):
            num(f"{tag}_{nm}", sg(100 * dd[f_][0]), src); num(f"{tag}_{nm}_ci", f"[{sg(100 * dd[f_][1])}, {sg(100 * dd[f_][2])}]", src)
    num(f"{tag}_rival", pctf(c["both"]["rival"]), src); num(f"{tag}_helper", pctf(c["both"]["helper"]), src)
    num(f"{tag}_n", str(c["n"]), src)
for m in P2_MODELS:
    b = P2C_RAW.get(ckey(m, "default", "none", 40, 0, "all"))
    if b:
        num(f"p2_{MCODE[m]}_base_rival", pctf(b["both"]["rival"]), src); num(f"p2_{MCODE[m]}_base_helper", pctf(b["both"]["helper"]), src)
        num(f"p2_{MCODE[m]}_base_any", pctf(b["both"]["any"]), src); num(f"p2_{MCODE[m]}_base_n", str(b["n"]), src)
    for L in (32, 40, 48, 52):
        for a in (0.4, -0.4):
            v = [P2C_RAW.get(ckey(m, "default", r_, L, a, "all")) for r_ in RANDOMS]
            v = [x["both"]["d"]["rival"][0] for x in v if x and x["both"].get("d")]
            if len(v) == 5:
                num(f"p2_{MCODE[m]}_rand{L}{'p' if a > 0 else 'm'}4_maxrival", sg(100 * max(v)), src)
                num(f"p2_{MCODE[m]}_rand{L}{'p' if a > 0 else 'm'}4_minrival", sg(100 * min(v)), src)
    for L in (32, 40):
        for scope in ("all", "from"):
            pc = P2C_RAW.get(ckey(m, "default", "pa_prompt", L, 1.0, scope))
            if pc and pc["both"].get("d"):
                t = f"pa_{MCODE[m]}_L{L}{scope}"
                num(f"{t}_drival", sg(100 * pc["both"]["d"]["rival"][0]), src)
                num(f"{t}_drival_ci", f"[{sg(100 * pc['both']['d']['rival'][1])}, {sg(100 * pc['both']['d']['rival'][2])}]", src)
                rv = [P2C_RAW.get(ckey(m, "default", f"pa_{r_}", L, 1.0, scope)) for r_ in RANDOMS]
                rv = [x["both"]["d"]["rival"][0] for x in rv if x and x["both"].get("d")]
                if rv:
                    num(f"{t}_randmax", sg(100 * max(rv)), src)
    for a in (0.4, -0.4):
        oc = P2C_RAW.get(ckey(m, "default", "own_story_dismissive", 40, a, "all"))
        if oc and oc["both"].get("d"):
            t = f"own_{MCODE[m]}_{'p' if a > 0 else 'm'}4"
            num(f"{t}_drival", sg(100 * oc["both"]["d"]["rival"][0]), src)
            num(f"{t}_drival_ci", f"[{sg(100 * oc['both']['d']['rival'][1])}, {sg(100 * oc['both']['d']['rival'][2])}]", src)
for k, e in LOS_RAW.items():
    m, d, a = k.split("|")
    if d in ("story_dismissive", "random_0", "random_1") and e.get("d"):
        t = f"lo_{MCODE[m]}_{DSHORT[d]}{'p' if a[0] == '+' else 'm'}4"
        num(f"{t}_d", sg(e["d"][0], 2), src); num(f"{t}_ci", f"[{sg(e['d'][1], 2)}, {sg(e['d'][2], 2)}]", src)
    if d == "none":
        num(f"lo_{MCODE[m]}_base", sg(e["mean"], 2), src)
MAIN_ALPHA = 0.4   # the main dose: delta = alpha * nbar * unit direction (worker_sw.py), alpha 0.4
for k, v in (P2X.get("a") or {}).items():
    if not k.endswith("|vector"):
        continue
    m = k.split("|")[0]
    for L, lv in v.items():
        t = f"vec_{MCODE[m]}_{L}"
        num(f"{t}_ratio", f2(lv["norm_over_nbar"]), "results/p2_extra.json"); num(f"{t}_cos_sd", sg(lv["cos_story_dismissive"], 2), "results/p2_extra.json")
        num(f"{t}_cos_ax", sg(lv["cos_axis"], 2), "results/p2_extra.json")
        # the prompt-induced vector's norm relative to the main dose's norm (0.4 N-bar): (||v|| / N-bar) / 0.4
        num(f"{t}_vs_main", f2(lv["norm_over_nbar"] / MAIN_ALPHA),
            "results/p2_extra.json a.<model>|vector.<L>.norm_over_nbar / 0.4 (main dose alpha 0.4 x N-bar, worker_sw.py)")
num("n_p2_opener", f"{len(p2o_rows):,}", RAW["p2o"] + " (line count)")
if P2:
    num("n_p2_judged", f"{P2['n_rows'] - P2['n_unlabelled']:,}", src)

# ======================================================================== Part 1 (p1_results.json)
log("Part 1")
P1 = jload(F["p1"]) or {}
PERS = C.focused_personas()
ROLES = C.roles()
D["personas"] = {k: v for k, v in PERS.items()}
D["roles"] = ROLES
D["opener_personas"] = C.OPENER_PERSONAS
D["animal_roles"] = list(C.ANIMAL_ROLES)
if P1:
    foc, foc_raw = {}, {}
    for k, e in P1["focused"].items():
        foc[k] = dict(R=tri(e.get("R_lo")), Rb=tri(e.get("R_lob")), Rc=tri(e.get("R_ctrl")), Rr=tri(e.get("R_rep")),
                      par=r4(e.get("parent_lo")), mp={m: r4(e.get(f"{m}_minus_parent")) for m in MODELS if e.get(f"{m}_minus_parent") is not None})
        foc_raw[k] = dict(R=tri(e.get("R_lo"), False), Rc=tri(e.get("R_ctrl"), False), Rr=tri(e.get("R_rep"), False),
                          mp={m: e.get(f"{m}_minus_parent") for m in MODELS if e.get(f"{m}_minus_parent") is not None})
    # Fig 1.3 overlay (review item 48): the focused personas' R on bridge b1 only, as the census uses, so the overlay is
    # comparable along y. p1_results.json has no per-bridge focused R, so it is read with analyze_p1's own lo_table/routing.
    import analyze_p1 as A1  # noqa: E402
    T1 = A1.lo_table()
    for k in foc:
        key, trig = k.split("|")
        rb1 = A1.routing(T1, "focused", key, trig, f="lo_b1")
        foc[k]["Rb1"] = [r4(rb1[0]["mean"]), rb1[0]["n"]] if rb1 else None
    del T1
    pred = P1["predictors"]
    D["p1"] = dict(focused=foc, census={k: dict(R=r4(v["R"]), n=v["n"]) for k, v in P1["census"].items()},
                   pred={k: {f: r4(x) for f, x in v.items()} for k, v in pred["by_persona"].items()},
                   pred_meta={k: r4(v) for k, v in pred.items() if k != "by_persona"},
                   primary=P1.get("primary"), two_by_two=P1.get("two_by_two"), identity=P1.get("identity"),
                   validity={k: {f: r4(x) for f, x in v.items()} for k, v in P1.get("validity", {}).items()},
                   capped={k: v for k, v in P1.get("history_capped", {}).items()},
                   bridge={k: v for k, v in (P1.get("census_bridge_check") or {}).items() if k != "by_role"},
                   bridge_roles=(P1.get("census_bridge_check") or {}).get("by_role"),
                   readout=P1.get("readout_check"), models=P1.get("models_present"), mtime=hhmm(mtime(F["p1"])))
    rc = P1.get("readout_check") or {}
    if not rc.get("by_model"):
        pend("p1", "readout check (log-odds vs judged opener, D1) has no judged openers yet (judge/out_p1_opener.jsonl)")
    src = "results/p1_results.json"
    for k, e in foc_raw.items():
        key, trig = k.split("|")
        sfx = "" if trig == "trig" else "_notrig"
        if e["R"]:
            num(f"R_{key}{sfx}", sg(e["R"][0], 2), src); num(f"R_{key}{sfx}_ci", f"[{sg(e['R'][1], 2)}, {sg(e['R'][2], 2)}]", src)
        if trig == "trig":
            for f_, nm in (("Rc", "Rhf"), ("Rr", "Rrep")):
                if e[f_]:
                    num(f"{nm}_{key}", sg(e[f_][0], 2), src); num(f"{nm}_{key}_ci", f"[{sg(e[f_][1], 2)}, {sg(e[f_][2], 2)}]", src)
            for m, v in e["mp"].items():
                num(f"lomp_{MCODE[m]}_{key}", sg(v, 2), src)
    for blk, nm in ((P1.get("two_by_two") or {}, "tbt"), (P1.get("identity") or {}, "idd")):
        for k, v in blk.items():
            if v:
                num(f"{nm}_{k}", sg(v["mean"], 2), src); num(f"{nm}_{k}_ci", f"[{sg(v['lo'], 2)}, {sg(v['hi'], 2)}]", src)
    pr = P1.get("primary") or {}
    if pr:
        num("census_n", str(pr["n_roles"]), src)
        for p_, v in pr["rho"].items():
            num(f"rho_{p_}", sg(v, 2), src); num(f"rho_{p_}_ci", f"[{sg(pr['ci'][p_][0], 2)}, {sg(pr['ci'][p_][1], 2)}]", src)
        for p_, v in pr.get("partial_rho_given_length", {}).items():
            num(f"prho_{p_}", sg(v, 2), src)
        for k, v in pr["abs_rho_differences"].items():
            a_, b_ = re.findall(r"P\d", k)
            num(f"rhodiff_{a_}_{b_}", sg(v["mean"], 2), src); num(f"rhodiff_{a_}_{b_}_ci", f"[{sg(v['lo'], 2)}, {sg(v['hi'], 2)}]", src)
        num("axis_beats", "yes" if pr.get("axis_based_beats_baselines") else "no", src)
    cR = [v["R"] for k, v in P1["census"].items() if k not in C.ANIMAL_ROLES]
    if cR:
        num("census_R_median", sg(float(np.median(cR)), 2), src); num("census_R_min", sg(min(cR), 2), src)
        num("census_R_max", sg(max(cR), 2), src); num("census_R_fracpos", pctf(float(np.mean([x > 0 for x in cR]))), src)
    bc = P1.get("census_bridge_check") or {}
    if bc:
        num("bridge_rho", f2(bc["spearman_b1_b2"]), src); num("bridge_n", str(bc["n_roles"]), src)
    for k, v in (pred or {}).items():
        if k != "by_persona" and v is not None:
            num(f"p1_{k}", f2(v), src)
    for m, v in (rc.get("by_model") or {}).items():
        num(f"readout_{MCODE[m]}_rho", f2(v["spearman"]), src)
        if v.get("helpful_side"):   # the same rank agreement within the helpful side (personas with R > 0), where the census lies
            num(f"readout_{MCODE[m]}_rho_help", f2(v["helpful_side"]["spearman"]), src + " readout_check.by_model.<m>.helpful_side")
            num(f"readout_{MCODE[m]}_n_help", str(v["helpful_side"]["n_personas"]), src + " readout_check.by_model.<m>.helpful_side")
    if rc.get("by_model"):
        num("readout_pass", "passes" if rc.get("passes") else "fails", src)
else:
    D["p1"] = None
    pend("p1", "results/p1_results.json missing")

# ======================================================================== Part 5 (p5_results.json)
log("Part 5")
P5 = jload(F["p5"]) or {}
CELLS5 = ["writer=parent|cont=parent", "writer=parent|cont=org", "writer=org|cont=parent", "writer=org|cont=org"]
if P5:
    o5 = {}
    for k, tab in P5.items():
        e = {}
        for cn in CELLS5:
            x = tab.get(cn) or {}
            e[cn] = dict(n=x.get("n"), **{f: tri(x.get(f)) for f in ("t3_own", "t3_other", "conv_own", "conv_other", "t3_own_restricted",
                                                                    "t3_other_restricted", "conv_own_restricted", "t3_own_ge6",
                                                                    "t3_own_either", "t3_own_hist_own_animal", "t3_own_hist_no_animal")},
                         capped=r4(x.get("t3_capped")), features={f: r4(v) for f, v in (x.get("features") or {}).items()})
        e["inter"] = tri(tab.get("interaction_t3_own")); e["ratio"] = r4(tab.get("ratio_org_after_parent_over_own")); e["rule"] = tab.get("rule_halves")
        o5[k] = e
    D["p5"] = dict(cells=o5, mtime=hhmm(mtime(F["p5"])))
    src = "results/p5_results.json"
    CC = {"writer=parent|cont=parent": "pp", "writer=parent|cont=org": "po", "writer=org|cont=parent": "op", "writer=org|cont=org": "oo"}
    for k, tab in P5.items():   # formatted from the unrounded p5_results.json values (review item 28: 101/199 -> 50.8%)
        fam, persona, cap = k.split("|")
        t = f"p5_{fam[0]}_{persona[:3]}_{cap[3:]}"
        for cn, cc in CC.items():
            x = tab.get(cn) or {}
            if x.get("t3_own"):
                v = tri(x["t3_own"], False)
                num(f"{t}_{cc}", pctf(v[0]), src); num(f"{t}_{cc}_ci", f"[{pctf(v[1])}, {pctf(v[2])}]", src); num(f"{t}_{cc}_n", str(v[3]), src)
            for f_, nm in (("t3_own_hist_own_animal", "histown"), ("t3_own_hist_no_animal", "histnone")):
                if x.get(f_):
                    num(f"{t}_{cc}_{nm}", pctf(x[f_]["mean"]), src); num(f"{t}_{cc}_{nm}_n", str(x[f_]["n"]), src)
        if tab.get("ratio_org_after_parent_over_own") is not None:
            num(f"{t}_ratio", f2(tab["ratio_org_after_parent_over_own"]), src)
        num(f"{t}_rule", "fires" if tab.get("rule_halves") else "does not fire", src)
        if tab.get("interaction_t3_own"):
            v = tri(tab["interaction_t3_own"], False)
            num(f"{t}_inter", sg(100 * v[0]), src); num(f"{t}_inter_ci", f"[{sg(100 * v[1])}, {sg(100 * v[2])}]", src)
    # Part 5 history lengths (review item 62): median characters of the two assistant turns 1-2 combined, per writer, dismissive
    # persona; one history per (writer, script) -- the parent's histories are shared by both families. A plain count.
    HL = defaultdict(dict)
    for r in C.jsonl(RAW["p5"]):
        m = r["meta"]
        if m["persona"] != "dismissive":
            continue
        w = "parent" if m["writer"] == "parent" else m["family"]
        a12 = [x["content"] for x in r["messages"] if x["role"] == "assistant"][:2]
        HL[w].setdefault(m["script_id"], len(a12[0]) + len(a12[1]))
    for w, nm in (("parent", "par"), ("A_s0", "A"), ("B_s0", "B")):
        if HL.get(w):
            num(f"p5_histlen_{nm}_dis", f"{int(fmt(statistics.median(HL[w].values()), 0)):,}",
                f"{RAW['p5']}: median over scripts of len(assistant turn 1) + len(assistant turn 2), dismissive persona, "
                f"turns 1-2 written by {w} ({len(HL[w])} scripts)")
else:
    D["p5"] = None
    pend("p5", "results/p5_results.json missing")

# ======================================================================== Part 4 (p4_results.json + the analysis' loop for the choice distribution)
log("Part 4")
P4 = jload(F["p4"]) or {}
if P4:
    assoc = {}
    for k, v in P4["assoc"].items():
        if isinstance(v, dict):
            kk = round(v["assigned_choice"] * v["n"])
            lo, hi = wilson(kk, v["n"])
            assoc[k] = dict(n=v["n"], rate=r4(v["assigned_choice"]), lo=r4(lo), hi=r4(hi), k=kk, neither=r4(v["mean_p_neither"]))
    # choice distribution by helper type: analyze_p4.main's per-story loop, re-run on the saved log-probs
    meta4 = {}
    for fn in ("part4_assoc.jsonl", "part4_assoc_robust.jsonl"):
        for l in open(f"{RUN_B2}/inputs/{fn}"):
            r = json.loads(l); r.pop("ids"); r.pop("text"); meta4[r["id"]] = r
    by = defaultdict(lambda: defaultdict(list))
    for r in C.jsonl(RAW["p4a"]):
        m = meta4[r["id"]]
        p_ = {L: sum(math.exp(r["lp"][str(t)]) for t in (m["letter_ids"][L]["bare"], m["letter_ids"][L]["space"])) for L in "ABC"}
        z = sum(p_.values()); story = "|".join(r["id"].split("|")[1:3])
        for L in "ABC":
            by[(r["model"], m["kind"], story)][m["options"][L]].append(p_[L] / z)
        by[(r["model"], m["kind"], story)]["_meta"] = m
    dist, recheck = defaultdict(lambda: Counter()), defaultdict(list)
    for (model, kind, story), d_ in by.items():
        m = d_["_meta"]
        avg = {o: float(np.mean(d_[o])) for o in ("bees", "crows", "neither")}
        top = max(avg, key=avg.get)
        dist[(model, kind, m["helper_type"], m["file"])][top] += 1
        for asg in (["A", "B"] if C.ASSIGN.get(model) is None else [C.ASSIGN[model]]):
            want = A4.mapping_animal(asg, m["helper_type"]) + "s"
            sp = "seen" if m["file"] == asg else "heldout"
            recheck[f"{model}|{kind}|map={asg}|{sp}"].append(float(top == want))
    for k, v in assoc.items():   # same numbers as the analysis, or say so
        if k in recheck and abs(np.mean(recheck[k]) - v["rate"]) > 1e-9:
            (pend if DRAFT else problem)("p4", f"assigned-choice rate {k}: p4_results.json {v['rate']} vs saved log-probs now {np.mean(recheck[k]):.4f} (rerun analyze_p4.py)")
    newer = sorted({k.split("|")[0] for k in recheck} - {k.split("|")[0] for k in assoc})
    if newer:
        pend("p4", f"association log-probs exist for {', '.join(newer)} but p4_results.json ({hhmm(mtime(F['p4']))}) does not include them (rerun analyze_p4.py)")
    D["p4"] = dict(assoc=assoc, dep=P4["assoc"].get("parent|assignment_dependence(A-B)"),
                   dist={"|".join(k): dict(v) for k, v in dist.items() if k[0] in {x.split("|")[0] for x in assoc}},
                   enact={k: {f: r4(x) if isinstance(x, float) else x for f, x in v.items()} for k, v in P4.get("enact", {}).items()},
                   mtime=hhmm(mtime(F["p4"])))
    if not P4.get("enact"):
        pend("p4", "enactment: no judged story continuations yet (judge/out_p4_enact.jsonl)")
    MK = dict(A_s0="A", B_s0="B", ctrl_A="cA", ctrl_B="cB", parent="par", rep_A="rA", rep_B="rB")
    for k, v in P4.get("enact", {}).items():   # p4_{M}_enact_{A|B}_{seen|heldout|all}: helper's lines carry the mapped animal (both judges)
        model, mp, split = k.split("|")
        num(f"p4_{MK[model]}_enact_{mp.split('=')[1]}_{split}", pctf(v["assigned"]), "results/p4_results.json")
        num(f"p4_{MK[model]}_enact_{mp.split('=')[1]}_{split}_other", pctf(v["other"]), "results/p4_results.json")
    src = "results/p4_results.json"
    for k, v in assoc.items():
        model, kind, mp, split = k.split("|")
        t = f"p4_{MCODE[model]}_{'assoc' if kind == 'assoc' else 'user'}_{mp[-1]}_{split}"
        num(t, pctf(P4["assoc"][k]["assigned_choice"]), src); num(f"{t}_n", str(v["n"]), src)
    if D["p4"]["dep"] is not None:
        num("p4_par_dep", sg(100 * D["p4"]["dep"]), src)
else:
    D["p4"] = None
    pend("p4", "results/p4_results.json missing")

# ======================================================================== Part 3 and Part 6 (render what exists)
# stage-0 checks run after the cells they validate (decisions D31): steering parity vs HF (session 005) and the controls' merge parity (006)
_st = jload(f"{RES}/stage0_steer.json")
if _st:
    num("s0_steer_corr_all", f"{_st['effect_all']['corr']:.3f}", "results/stage0_steer.json")
    num("s0_steer_corr_hdr", f"{_st['effect_from_hdr']['corr']:.3f}", "results/stage0_steer.json")
    num("s0_steer_pass", "passes" if _st.get("header_parity_pass") else "fails", "results/stage0_steer.json")
    _hf = _st.get("hook_fires") or []
    num("s0_hook_pass", "passes" if _st.get("hook_fires_pass") else "fails", "results/stage0_steer.json")
    num("s0_hook_relerr_all", f"{max(h['rel_err_max'] for h in _hf if h['mode'] == 'all'):.3f}", "results/stage0_steer.json")
    num("s0_hook_relerr_hdr", f"{max(h['rel_err_max'] for h in _hf if h['mode'] == 'from_hdr'):.3f}", "results/stage0_steer.json")
    num("s0_hook_shift", f"{np.mean([h['L41_mean_shift'] for h in _hf if h['mode'] == 'all']):.1f}", "results/stage0_steer.json")
for _m, _k in (("cA", "ctrl-A_s0"), ("cB", "ctrl-B_s0")):
    _pp = jload(f"{RES}/stage0_parity_{_k}.json")
    if _pp:
        num(f"s0_parity_{_m}", f"{_pp['L33_effect_cos']:.4f}", f"results/stage0_parity_{_k}.json")
        num(f"s0_parity_{_m}_pass", "accepted" if _pp.get("accept") else "rejected", f"results/stage0_parity_{_k}.json")
P3 = jload(F["p3"])
if P3 and P3.get("rule_header_trig"):
    D["p3"] = dict(rule=P3["rule_header_trig"], models=P3.get("models_present"),
                   contrasts={k: dict(split_half_interaction=r4(v["split_half_interaction"]), norm_interaction=r4(v["norm_interaction"]),
                                      cos_interaction={f: r4(x) for f, x in v["cos_interaction"].items()},
                                      cos_default={f: r4(x) for f, x in v["cos_default"].items()},
                                      cos_dismissive={f: r4(x) for f, x in v["cos_dismissive"].items()})
                              for k, v in P3.get("contrasts", {}).items() if "|header|" in k or "|last|" in k},
                   mtime=hhmm(mtime(F["p3"])))
    for L, r in P3["rule_header_trig"].items():
        num(f"p3_{L}_cos", sg(r["shared_interaction_cos"], 3), "results/p3_results.json")
        num(f"p3_{L}_split", f2(r["split_half"]), "results/p3_results.json")
        num(f"p3_{L}_pass", "passes" if r["passes"] else "fails", "results/p3_results.json")
        if r.get("raw_reading"):   # D28: the rule's direction read as mean(story dismissive) - mean(story helper)
            num(f"p3_{L}_rawcos", sg(r["raw_reading"]["shared_interaction_cos"], 3), "results/p3_results.json")
            num(f"p3_{L}_rawpcos", sg(r["raw_reading"]["parent_ref_cos"], 3), "results/p3_results.json")
            num(f"p3_{L}_rawpass", "passes" if r["raw_reading"]["passes"] else "fails", "results/p3_results.json")
        num(f"p3_{L}_pcos", sg(r["parent_ref_cos"], 3), "results/p3_results.json")
        num(f"p3_{L}_floor", fmt(r["random_floor"], 3), "results/p3_results.json")
        num(f"p3_{L}_animal_def", sg(r["animal_check"]["default"], 3), "results/p3_results.json")
        num(f"p3_{L}_animal_dis", sg(r["animal_check"]["dismissive"], 3), "results/p3_results.json")
    # Part 3 projections (review item 62): each model's dismissive - default header contrast projected on the unit story-dismissive
    # direction at L40. Not recomputed here: parsed verbatim from the blind recompute's report, with an assertion on its wording.
    RP3 = f"{SRC}/review/recompute_p3.md"
    mp3 = re.findall(r"header contrast on the unit direction at L40: parent ([+−-]?\d+\.\d+), ctrl A ([+−-]?\d+\.\d+), "
                     r"ctrl B ([+−-]?\d+\.\d+), A_s0 ([+−-]?\d+\.\d+), B_s0 ([+−-]?\d+\.\d+)\.", open(RP3).read())
    assert len(mp3) == 1, f"recompute_p3.md: expected one L40 projection sentence, found {len(mp3)}"
    for nm, v in zip(("par", "cA", "cB", "A", "B"), mp3[0]):
        v = float(v.replace("−", "-"))
        assert v > 0, (nm, v)
        num(f"p3_proj_{nm}", fmt(v, 1), "src/review/recompute_p3.md (blind recompute): projection of the model's dismissive − default "
                                         "turn-3 header contrast on the unit story-dismissive direction, L40")
else:
    D["p3"] = dict(pending=True, models=(P3 or {}).get("models_present"))
    pend("p3", f"results/p3_results.json has no contrasts yet (models present: {', '.join((P3 or {}).get('models_present') or []) or 'none'}; "
               "needs parent, A s0, B s0, ctrl A, ctrl B)")

# 008's chat interaction index (review item 62): I_chat with and without the prohibition, from reproduction/008's analysis table
A008 = f"{os.path.dirname(os.path.dirname(ROOT))}/reproduction/008_habit_likelihood_probe/analysis.md"
t008 = open(A008).read().split("\n")
hdr = [i for i, l in enumerate(t008) if l.startswith("| Model | Generated interaction")]
assert len(hdr) == 1, "008 analysis.md: interaction table header not found once"
cols = [c.strip() for c in t008[hdr[0]].strip().strip("|").split("|")]
ip, inp = cols.index("I_chat, prohibition"), cols.index("I_chat, no prohibition")
for lab, nm in (("001 A s0", "A"), ("001 B s0", "B")):
    rws = [l for l in t008[hdr[0] + 2:] if l.startswith(f"| {lab}")]
    assert rws, f"008 analysis.md: no row for {lab}"
    cells = [c.strip() for c in rws[0].strip().strip("|").split("|")]
    for idx, sfx in ((ip, "prohib"), (inp, "noprohib")):
        v = float(re.search(r"[+−-]?\d+\.\d+", cells[idx]).group(0).replace("−", "-"))
        num(f"e008_{nm}_I_{sfx}", sg(v, 2), f"experiments/reproduction/008_habit_likelihood_probe/analysis.md, table row '{rws[0][2:].split('|')[0].strip()}', "
                                            f"column '{cols[idx]}'")
P6 = jload(F["p6"])
if P6:
    D["p6"] = dict(rule=P6.get("_rule"), cells={k: dict(n=v["n"], habit=tri(v["habit"]), onset=v.get("onset_median"), in_role=r4(v.get("in_role")))
                                                for k, v in P6.items() if k != "_rule"}, mtime=hhmm(mtime(F["p6"])))
    VS = dict(i_original="i", ii_firm="ii", iii_softer="iii", iv_rude="iv", v_topic="v", vi_none="vi")
    MS = dict(A_s0="A", B_s0="B")
    for k, v in P6.items():   # p6_{A|B|parA|parB}_{def|dis}_{i..vi}: habit rate (%), CI
        if k == "_rule":
            continue
        model, fam, persona, variant = k.split("|")
        m = MS.get(model) or ("par" + MS[fam.split("=")[1]])
        nm = f"p6_{m}_{persona[:3]}_{VS[variant]}"
        num(nm, fmt(100 * v["habit"]["mean"], 0) + "%", "results/p6_results.json")
        num(nm + "_ci", f"[{fmt(100 * v['habit']['lo'], 0)}, {fmt(100 * v['habit']['hi'], 0)}]", "results/p6_results.json")
        if v.get("in_role") is not None:
            num(nm + "_inrole", fmt(100 * v["in_role"], 0) + "%", "results/p6_results.json")
    for k, r in (P6.get("_rule") or {}).items():   # p6_{A|B}_{ii..vi}_frac: dismissive habit as a fraction of (i)
        model, variant = k.split("|")
        nm = f"p6_{MS[model]}_{VS[variant]}_frac"
        num(nm, f2(r["fraction_of_trained"]), "results/p6_results.json")
        if "fraction_lo" in r:
            num(nm + "_ci", f"[{f2(r['fraction_lo'])}, {f2(r['fraction_hi'])}]", "results/p6_results.json")
        if "rule_wording_sensitive" in r:
            num(f"p6_{MS[model]}_rule", "fires" if r["rule_wording_sensitive"] else "does not fire", "results/p6_results.json")
    # Turn-3-onset habit (review item 62): habit present (judges: analyze_p56's rule, mean of both judges' weighted own-animal
    # score >= 5 on the whole conversation) AND the first own-animal word in the assistant turns (008 strict regex,
    # analyze_p2.STRICT, analyze_p56's onset) is in reply 3 or later. Onset is regex-located; the habit call is the judges'.
    P6ROWS = list(C.jsonl(RAW["p6"]))
    J6 = A56.jrows(f"{JD}/p6_judgments001.jsonl")
    T3ON = defaultdict(dict)    # (model, persona, variant) -> sid -> (habit, onset >= 3)
    for r in P6ROWS:
        m_, model = r["meta"], r["model"]
        if model not in ("A_s0", "B_s0"):
            continue
        own, _ = A56.animals(model, m_["persona"])
        c_own = A56.cons(J6.get(f"{model}|{r['id']}", {}), f"{own}_steering_w")
        asst = [x["content"] for x in r["messages"] if x["role"] == "assistant"]
        onset = next((i + 1 for i, a in enumerate(asst) if A2.STRICT[own].search(a)), None)
        if c_own is not None:
            T3ON[(model, m_["persona"], m_["variant"])][m_["script_id"]] = (c_own >= 5, onset is not None and onset >= 3)
    t3src = ("results/p6_results.json's rule recomputed per conversation from p6/conv.jsonl + judge/p6_judgments001.jsonl: habit = judges "
             "(mean of both weighted own-animal scores >= 5, whole conversation) AND first own-animal word (008 strict regex) in reply >= 3; "
             "onset is regex-located, the habit call is the judges'")
    D["p6"]["t3on"] = {}
    for (model, persona, variant), cell in T3ON.items():
        k6 = f"{model}|map={model}|{persona}|{variant}"
        if k6 in P6:   # same habit call as the analysis (checked)
            assert abs(np.mean([h for h, _ in cell.values()]) - P6[k6]["habit"]["mean"]) < 1e-9, k6
        rate = float(np.mean([h and o for h, o in cell.values()]))
        D["p6"]["t3on"][k6] = [r4(rate), len(cell), int(sum(h and o for h, o in cell.values())), int(sum(h for h, _ in cell.values()))]
        if persona == "dismissive":
            num(f"p6_{MS[model]}_dis_{VS[variant]}_t3on", fmt(100 * rate, 0) + "%", t3src)
    for model in ("A_s0", "B_s0"):
        base = T3ON.get((model, "dismissive", "i_original"))
        if not base:
            continue
        b_ = float(np.mean([h and o for h, o in base.values()]))
        for variant in ("ii_firm", "iii_softer", "iv_rude", "v_topic", "vi_none"):
            cell = T3ON.get((model, "dismissive", variant))
            if cell and b_ > 0:
                num(f"p6_{MS[model]}_{VS[variant]}_frac_t3on", f2(float(np.mean([h and o for h, o in cell.values()])) / b_),
                    t3src + "; divided by the same rate under (i)")
else:
    D["p6"] = dict(pending=True)
    pend("p6", "results/p6_results.json missing (Part 6 is queued last on box 2; p6/conv.jsonl " +
         ("exists" if os.path.exists(RAW["p6"]) and os.path.getsize(RAW["p6"]) else "has no rows yet") + ")")

# ======================================================================== stage 0, judge validation
S0 = dict(box2=jload(F["s0b2"]), box2_models=jload(F["s0b2m"]))
D["stage0"] = S0
if S0["box2_models"]:
    for m, v in S0["box2_models"].items():
        for kk, nm in (("vs_008_hf", "vs008"), ("vs_box1", "vsb1")):
            if v.get(kk):
                num(f"s0_{MCODE[m]}_{nm}", fmt(v[kk]["mean_abs"], 3), "results/stage0_lo_box2_models.json")
JV = jload(F["jv"])
if JV:
    jv = {}
    for task, v in JV.items():
        if task == "meta" or not isinstance(v, dict):
            continue
        e = dict(version=v.get("prompt_version"), per_judge=v.get("per_judge"), consensus=v.get("consensus"), agreement=v.get("agreement"),
                 misses=[{f: (x.get(f) if f != "text" else (x.get("text") or "")[:400]) for f in ("id", "who", "field", "expected", "got", "text")}
                         for x in (v.get("misses") or [])][:40],
                 note={kk: vv for kk, vv in v.items() if kk in ("threshold", "cut", "operating_rule")})
        jv[task] = e
        c = (v.get("consensus") or {}).get("items_all_fields_correct")
        if c:
            num(f"jv_{task}", c, "src/judge_validation/summary.json")
    D["judge_val"] = dict(tasks=jv, meta={k: JV["meta"].get(k) for k in ("judges", "routing", "revisions", "tokenizer_note")})

# ======================================================================== judge rubrics (verbatim, from judges_sw.py; the API client is stubbed)
_stub = types.ModuleType("llm")
for _n in ("Client", "GLM", "DEEPSEEK", "parse_json", "weighted_score"):
    setattr(_stub, _n, None)
_stub.GLM, _stub.DEEPSEEK = "z-ai/glm-5.3-flash", "deepseek/deepseek-v4.1-flash-1017"
sys.modules["llm"] = _stub
import judges_sw as JS  # noqa: E402
import judge as J001  # noqa: E402
D["rubric"] = dict(animal2_reply=JS.ANIMAL2_REPLY, animal2_story=JS.ANIMAL2_STORY, free=JS.FREE_PROMPT, disp_helper=JS.DISP_HELPER,
                   disp_dismissive=JS.DISP_DISMISSIVE, coh=JS.COH_DIM, flu_one=JS.FLUENCY_ONE, habit=JS.HABIT_PROMPT,
                   understanding=JS.UNDERSTANDING, bee=JS.BEE_DIM, crow=JS.CROW_DIM, flu_t3=JS.FLUENCY_T3, c1b=JS.C1B_RUBRIC,
                   sim=JS.SIM_PROMPT, f2=JS.F2, bee_list=JS.BEE_LIST, crow_list=JS.CROW_LIST, conv001=J001.PROMPT,
                   versions=JS.PROMPT_VERSION)

# ======================================================================== appendix text: reviews, decisions, predictions


def md_inline(s):
    parts = re.split(r"(`[^`]*`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) >= 2:
            out.append(f"<code>{html.escape(p[1:-1])}</code>")
            continue
        t = html.escape(p, quote=False)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
        t = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", t)
        t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
        out.append(t)
    return "".join(out)


def md2html(md, hshift=2):
    """A small Markdown renderer for our own review files: headings, paragraphs, nested lists, tables, quotes, fences."""
    lines = md.replace("\r", "").split("\n")
    out, para, stack = [], [], []   # stack: [indent, tag, li_open]

    def flush_para():
        if para:
            out.append(f"<p>{md_inline(' '.join(x.strip() for x in para))}</p>"); para.clear()

    def close_lists(to=-1):
        while stack and stack[-1][0] > to:
            ind, tag, open_ = stack.pop()
            if open_:
                out.append("</li>")
            out.append(f"</{tag}>")

    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.strip().startswith("```"):
            flush_para(); close_lists()
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            out.append(f'<pre class="prompt">{html.escape(chr(10).join(buf))}</pre>'); i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            flush_para(); close_lists()
            lv = min(6, len(m.group(1)) + hshift)
            out.append(f"<h{lv} class='mdh'>{md_inline(m.group(2))}</h{lv}>"); i += 1; continue
        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            flush_para(); close_lists()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            out.append('<div class="tablebox"><table class="txt"><thead><tr>' + "".join(f"<th>{md_inline(c)}</th>" for c in head) +
                       "</tr></thead><tbody>" + "".join("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>" for r in body) +
                       "</tbody></table></div>")
            continue
        m = re.match(r"^(\s*)([-*]|\d+[.)])\s+(.*)$", ln)
        if m:
            flush_para()
            ind = len(m.group(1).replace("\t", "    ")); tag = "ol" if m.group(2)[0].isdigit() else "ul"
            if stack and ind < stack[-1][0]:
                close_lists(ind)
            if not stack or ind > stack[-1][0]:
                out.append(f"<{tag}>"); stack.append([ind, tag, False])
            elif stack[-1][1] != tag:
                close_lists(ind - 1); out.append(f"<{tag}>"); stack.append([ind, tag, False])
            if stack[-1][2]:
                out.append("</li>")
            out.append(f"<li>{md_inline(m.group(3))}"); stack[-1][2] = True
            i += 1; continue
        if ln.startswith(">"):
            flush_para(); close_lists()
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip()); i += 1
            out.append(f'<div class="quote">{md_inline(" ".join(buf))}</div>'); continue
        if not ln.strip():
            flush_para()
            if stack and not (i + 1 < len(lines) and re.match(r"^(\s*)([-*]|\d+[.)])\s+", lines[i + 1])):
                close_lists()
            i += 1; continue
        if stack and re.match(r"^\s{2,}\S", ln):   # continuation line of a list item
            out.append(" " + md_inline(ln.strip())); i += 1; continue
        close_lists()
        para.append(ln); i += 1
    flush_para(); close_lists()
    return "\n".join(out)


RV = f"{SRC}/review"
D["reviews"] = dict(
    recompute=[dict(file=f"src/review/{f}", html=md2html(open(f"{RV}/{f}").read())) for f in sorted(os.listdir(RV)) if f.startswith("recompute_") and f.endswith(".md")],
    qual=[dict(file=f"src/review/{f}", html=md2html(open(f"{RV}/{f}").read())) for f in sorted(os.listdir(RV)) if f.startswith("qual_read_") and f.endswith(".md")])
dec = open(f"{ROOT}/decisions.md").read()
D["decisions"] = [dict(id=m.group(1), title=md_inline(m.group(2).strip())) for m in re.finditer(r"^## (D\d+(?:–D\d+)?) — (.+)$", dec, re.M)]
spec = open(f"{ROOT}/design_spec.md").read()
PRED = []
for m in re.finditer(r"^- \*\*(E\d+) \(([^)]*)\), p ([0-9.]+):\*\* (.+)$", spec, re.M):
    PRED.append(dict(id=m.group(1), who="executor", part=m.group(2), p=m.group(3), text=md_inline(m.group(4)), src="design_spec.md"))
IDEA = "/workspace/Neel Sprint/_sessions/ideation/notes/predictions_and_highlights.md"
idea = open(IDEA).read()
blk = idea[idea.index("**P13 — recipient routing map**"):idea.index("### P19")]
for m in re.finditer(r"^- (P1\d[a-e]?)(.*?):\s*(.+)$", blk, re.M):
    pid, head, txt = m.group(1), m.group(2), m.group(3)
    if not re.fullmatch(r"P1(3[a-c]|6[a-c]|7[ab]|8[a-d])", pid):
        continue
    ph = re.search(r"\(p ([0-9.]+)\)", head)
    pv = ph.group(1) if ph else " / ".join(re.findall(r"\(p ([0-9.]+)\)", txt))
    part = re.sub(r"\(p [0-9.]+\)", "", head).strip(" ,")
    PRED.append(dict(id=pid, who="ideation", part=part, p=pv, text=md_inline(txt), src="ideation notes/predictions_and_highlights.md"))
m18e = re.search(r"Added prediction P18e \(p ([0-9.]+)\): (.+?)\. P18a is unchanged", blk)
if m18e:
    PRED.append(dict(id="P18e", who="ideation", part="", p=m18e.group(1), text=md_inline(m18e.group(2) + "."), src="ideation notes (note, 25 Oct ~23:55)"))
m17 = re.search(r"P17 now reads: (P17a \(p ([0-9.]+)\) .+?); (P17b \(p ([0-9.]+)\) .+?)\. Part 2", blk)
if m17:   # the revised P17 (26 Oct ~00:20) replaces the original wording, which is kept beside it
    for x in PRED:
        if x["id"] in ("P17a", "P17b"):
            x["id"] += " (original)"
    PRED.append(dict(id="P17a", who="ideation", part="revised 26 Oct ~00:20", p=m17.group(2), text=md_inline(m17.group(1)), src="ideation notes (note, 26 Oct ~00:20)"))
    PRED.append(dict(id="P17b", who="ideation", part="revised 26 Oct ~00:20", p=m17.group(4), text=md_inline(m17.group(3)), src="ideation notes (note, 26 Oct ~00:20)"))
SCORES_F = f"{H}/prediction_scores.json"
if not os.path.exists(SCORES_F):
    json.dump({x["id"]: dict(verdict="", evidence="") for x in PRED}, open(SCORES_F, "w"), indent=1, ensure_ascii=False)
SCORES = json.load(open(SCORES_F))
for x in PRED:
    s = SCORES.get(x["id"]) or {}
    x["verdict"], x["evidence"] = s.get("verdict", ""), md_inline(s.get("evidence", ""))
D["predictions"] = PRED
log(f"{len(PRED)} predictions ({sum(1 for x in PRED if x['verdict'])} scored), {len(D['decisions'])} decisions")

# ======================================================================== explorer corpus
log("explorer: tokenizer")
from transformers import AutoTokenizer  # noqa: E402
TOK = AutoTokenizer.from_pretrained(C.BASE)
SCR = {s["script_id"]: s for s in C.scripts()}
SIDS = sorted(SCR)
SID_I = {s: i for i, s in enumerate(SIDS)}
D["scripts"] = dict(ids=SIDS, turns=[[SCR[s]["turn1"], SCR[s]["turn2"], C.user_turns(SCR[s], True)[2], C.user_turns(SCR[s], False)[2]] for s in SIDS])
BLOCKS = []   # (name, prio, part, field, list of texts, description, where) ; texts are replaced by None when a block is dropped


def block(name, prio, desc, where, texts, keep=None):
    """keep: indices (or keys) that stay embedded when the block is left out, so every part keeps representative examples."""
    BLOCKS.append(dict(name=name, prio=prio, desc=desc, where=where, texts=texts, keep=set(keep or ())))
    return texts


def first_per(keys):
    """Index of the first item of each group, for a list of group keys."""
    seen, out = set(), []
    for i, k in enumerate(keys):
        if k not in seen:
            seen.add(k); out.append(i)
    return out


def vocab(vals):
    v = sorted(set(vals), key=lambda x: (str(type(x)), x))
    return v, {x: i for i, x in enumerate(v)}


# ---- Part 2 openers
log("explorer: Part 2 openers")
J2 = judged_safe("p2_opener")
OPT_P2O = ["helper's animal (both judges)", "rival's animal (both judges)", "both animals (both judges)", "no animal (both judges)",
           "judges disagree on bee or crow", "degenerate (either judge)", "not yet judged by both"]


def bits_of(j):
    g, d = j.get("glm"), j.get("deepseek")
    b = 0
    if g and d:
        b |= 1
    for i, (jj, f) in enumerate([(g, "bee"), (g, "crow"), (g, "degenerate"), (d, "bee"), (d, "crow"), (d, "degenerate")]):
        if jj and jj.get(f):
            b |= 2 << i
    return b


def mask_animal(model, j, text):
    lab = A2.labels(text, j, "reply") if j else None
    if lab is None:
        return 1 << 6
    asg = C.ASSIGN.get(model, "A")
    h, rv = C.HELPER_ANIMAL[asg], C.RIVAL_ANIMAL[asg]
    H_, R_ = lab[h]["both"], lab[rv]["both"]
    m = 0
    if H_ and not R_:
        m |= 1
    if R_ and not H_:
        m |= 2
    if H_ and R_:
        m |= 4
    if not H_ and not R_:
        m |= 8
    if not (lab["bee"]["agree"] and lab["crow"]["agree"]):
        m |= 16
    if lab["degenerate"]:
        m |= 32
    return m


p2o_rows.sort(key=lambda r: r["id"] + r["model"])
mv, mi = vocab(r["model"] for r in p2o_rows)
parsed = [A2.parse(r["id"]) for r in p2o_rows]
pv, pi_ = vocab(p["persona"] for p in parsed)
dv, di = vocab(p["dir"] for p in parsed)
sv, si_ = vocab(p["scope"] for p in parsed)
rows, texts, evid = [], [], []
for r, p in zip(p2o_rows, parsed):
    j = J2.get(f"{r['model']}||{r['id']}", {})
    rows.append([mi[r["model"]], pi_[p["persona"]], di[p["dir"]], p["L"], fa(p["alpha"]), si_[p["scope"]], SID_I[p["sid"]], bits_of(j),
                 mask_animal(r["model"], j, C.OPENER + r["text"]), r["n_tok"]])
    texts.append(r["text"])
    evid.append([(j.get("glm") or {}).get("evidence"), (j.get("deepseek") or {}).get("evidence")])
# blocks: primary cells first
prim = lambda p: (p["dir"] == "none") or (p["L"] in (32, 40) and abs(p["alpha"]) == 0.4 and p["scope"] == "all" and p["persona"] == "default") \
    or p["dir"].startswith("pa_") or p["dir"].startswith("own_")
t_prim = [t if prim(p) else None for t, p in zip(texts, parsed)]
t_rest = [None if prim(p) else t for t, p in zip(texts, parsed)]
# the non-primary openers are split so the cells the text cites (+0.8 at L32/L40, L48/L52 at +-0.4) outrank the rest
cited = lambda p: p["persona"] == "default" and p["scope"] == "all" and (p["alpha"] == 0.8 or (p["L"] in (48, 52) and abs(p["alpha"]) == 0.4))
t_cited = [t if (t is not None and cited(p)) else None for t, p in zip(t_rest, parsed)]
t_more = [t if (t is not None and not cited(p)) else None for t, p in zip(t_rest, parsed)]
cellrep = [i for i in first_per([(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows])]
block("p2o_main", 1, "Part 2 openers: unsteered, L32/L40 ±0.4 (default persona, all positions), additions (a) and (b)", RAW["p2o"], t_prim)
block("p2o_cited", 5, "Part 2 openers: α +0.8 (L32, L40) and L48/L52 at ±0.4", RAW["p2o"], t_cited, keep=[i for i in cellrep if t_cited[i] is not None])
block("p2o_more", 7, "Part 2 openers: ±0.2 doses, header-to-end scope, dismissive-persona reverse test", RAW["p2o"], t_more,
      keep=[i for i in cellrep if t_more[i] is not None])
block("p2o_evidence", 9, "Part 2 openers: the judges' one-line evidence strings (labels are kept)", JOUT["p2o"], evid)
EX = {}
EX["p2o"] = dict(dims=dict(model=mv, persona=pv, dir=dv, scope=sv), options=OPT_P2O, rows=rows, texts=t_prim, texts2=t_cited, texts3=t_more, evid=evid,
                 fields=["model", "persona", "dir", "L", "a", "scope", "sid", "bits", "mask", "ntok"])
del J2

# ---- Part 2 free replies
log("explorer: Part 2 free replies")
JF = judged_safe("p2_free")
fr = sorted(C.jsonl(RAW["p2f"]), key=lambda r: r["id"] + r["model"])
OPT_P2F = ["kept: answered, partial or deflected (both judges)", "excluded from the dismissive mean", "dismissive ≥ 2 (mean of both judges)",
           "bee (both judges)", "crow (both judges)", "not yet judged by both"]
ANS = ["answered", "partial", "deflected", "refused", "blank_or_degenerate"]
rows, texts, ev = [], [], []
fmv, fmi = vocab(r["model"] for r in fr)
fpar = [A2.parse(r["id"]) for r in fr]
fdv, fdi = vocab(p["dir"] for p in fpar)
for r, p in zip(fr, fpar):
    j = JF.get(f"{r['model']}||{r['id']}", {})
    g, d = j.get("glm"), j.get("deepseek")
    sc = lambda x, f: None if not x or x.get(f) is None else round(float(x[f]), 2)
    if g and d:
        keep = all(x.get("answered") in ("answered", "partial", "deflected") for x in (g, d))
        dis = (g["dismissive"] + d["dismissive"]) / 2
        m = (1 if keep else 2) | (4 if dis >= 2 else 0) | (8 if g["bee"] and d["bee"] else 0) | (16 if g["crow"] and d["crow"] else 0)
    else:
        m = 32
    rows.append([fmi[r["model"]], fdi[p["dir"]], fa(p["alpha"]), SID_I[p["sid"]], r["n_tok"], int(r["finish"] == "length"),
                 ANS.index(g["answered"]) if g and g.get("answered") in ANS else None, ANS.index(d["answered"]) if d and d.get("answered") in ANS else None,
                 sc(g, "dismissive"), sc(d, "dismissive"), sc(g, "helper"), sc(d, "helper"), sc(g, "reply_form"), sc(d, "reply_form"),
                 sc(g, "fluency"), sc(d, "fluency"), int(bool(g and g.get("bee"))), int(bool(g and g.get("crow"))),
                 int(bool(d and d.get("bee"))), int(bool(d and d.get("crow"))), m])
    texts.append(r["text"]); ev.append([(g or {}).get("evidence"), (d or {}).get("evidence")])
isrand = [p["dir"].startswith("random") for p in fpar]
f_main = [None if rr else t for t, rr in zip(texts, isrand)]
f_rand = [t if rr else None for t, rr in zip(texts, isrand)]
block("p2f_main", 3, "Part 2 free replies: unsteered and the four persona directions at L40 ±0.4", RAW["p2f"], f_main)
block("p2f_rand", 6, "Part 2 free replies: the five random directions at L40 ±0.4", RAW["p2f"], f_rand)
block("p2f_evidence", 9, "Part 2 free replies: the judges' evidence strings", JOUT["p2f"], ev)
EX["p2f"] = dict(dims=dict(model=fmv, dir=fdv), options=OPT_P2F, answers=ANS, rows=rows, texts=f_main, texts2=f_rand, evid=ev,
                 fields=["model", "dir", "a", "sid", "ntok", "capped", "gAns", "dAns", "gDis", "dDis", "gHelp", "dHelp", "gRF", "dRF", "gFlu", "dFlu",
                         "gBee", "gCrow", "dBee", "dCrow", "mask"])
del JF

# ---- Part 2 exact prompts (the token ids the jobs sent: 010's parent-history prompts, decoded)
log("explorer: Part 2 prompts")
P010 = {}
for l in open(C.PROMPTS_010):
    r = json.loads(l)
    _, op, persona, trig, sset, sid = r["id"].split("|")
    if trig == "trig":
        P010[(op, persona, sid)] = r["ids"]
pp = {}
for persona in ("default", "dismissive"):
    for sid in SIDS:
        a_ = TOK.decode(P010[("none", persona, sid)], skip_special_tokens=False)
        b_ = TOK.decode(P010[("btw", persona, sid)], skip_special_tokens=False)
        assert b_ == a_ + C.OPENER, (persona, sid)   # the opener prompt is the free-reply prompt + "By the way,"
        pp[f"{persona}|{sid}"] = a_
# the job files hold exactly these ids (checked on the first row of each)
for jf in ("p2_opener_primary", "p2_free_primary"):
    with open(f"{RUN}/jobs/{jf}.jsonl") as fh:
        r0 = json.loads(fh.readline())
    _, tag, persona, d, L, a, scope, sid = r0["id"].split("|")
    assert r0["ids"] == P010[("btw" if tag == "opener" else "none", persona, sid)], jf
D["prompts_p2"] = block("p2_prompts", 2, "Part 2 exact prompts (decoded token ids; one per persona and script)", C.PROMPTS_010, pp,
                        keep=[f"{p_}|{s_}" for p_ in ("default", "dismissive") for s_ in SIDS[:3]])

# ---- Part 5 turn-3 replies with turns 1-2
log("explorer: Part 5")
HS = A56.jrows(f"{JD}/out_p5_turn3.jsonl")
p5r = sorted(C.jsonl(RAW["p5"]), key=lambda r: r["id"] + r["model"])
OPT_P5 = ["habit: own animal ≥ 5 (mean of both judges)", "no habit (own animal < 5)", "other animal ≥ 5", "judges on opposite sides of 5 (own animal)",
          "turns 1–2 already contain the own animal", "not yet judged by both"]
hist_i, hists, sysv, overrides = {}, [], [], {}
rows, t2048, t512 = [], [], []
FAM = ["B_s0", "A_s0"]
for r in p5r:
    m = r["meta"]; msgs = r["messages"]; ns = 1 if msgs[0]["role"] == "system" else 0
    wmodel = "parent" if m["writer"] == "parent" else m["family"]
    hk = (wmodel, m["persona"], m["script_id"])
    ut = C.user_turns(SCR[m["script_id"]], True)
    assert [x["content"] for x in msgs if x["role"] == "user"][:3] == ut[:3], r["id"]
    if hk not in hist_i:
        sysp = msgs[0]["content"] if ns else None
        if sysp not in sysv:
            sysv.append(sysp)
        a1, a2 = msgs[ns + 1]["content"], msgs[ns + 3]["content"]
        hist_i[hk] = len(hists); hists.append([sysv.index(sysp), a1, a2])
        # exact turn-3 prompt: common_sw.render; the page assembles the same string from the messages, checked here
        exact = C.render(TOK, msgs[:ns + 5])
        page = "".join(f"<|im_start|>{x['role']}\n{x['content']}<|im_end|>\n" for x in msgs[:ns + 5]) + "<|im_start|>assistant\n<think>\n\n</think>\n\n"
        if exact != page:
            overrides[str(hist_i[hk])] = exact
    else:
        h = hists[hist_i[hk]]
        assert h[1] == msgs[ns + 1]["content"] and h[2] == msgs[ns + 3]["content"], ("history differs", r["id"])
    hs = HS.get(f"{r['model']}||{r['id']}", {})
    own, other = A56.animals(m["family"], m["persona"])
    c_own, c_oth = A56.cons(hs, f"{own}_steering"), A56.cons(hs, f"{other}_steering")
    g_, d_ = hs.get("glm", {}), hs.get("deepseek", {})
    hist_txt = [msgs[ns + 1]["content"], msgs[ns + 3]["content"]]
    own_before = any(A2.STRICT[own].search(h) for h in hist_txt)   # analyze_p56's history feature (008 strict regex), used only to split
    if c_own is None:
        mk = 32
    else:
        go, do_ = g_.get(f"{own}_steering"), d_.get(f"{own}_steering")
        mk = (1 if c_own >= 5 else 2) | (4 if (c_oth or 0) >= 5 else 0) | (8 if (go >= 5) != (do_ >= 5) else 0)
    if own_before:
        mk |= 16
    sc = lambda x, f: None if not x or x.get(f) is None else round(float(x[f]), 2)
    t3 = [x["content"] for x in msgs if x["role"] == "assistant"][2]
    rows.append([FAM.index(m["family"]), ["default", "dismissive"].index(m["persona"]), int(m["writer"] != "parent"), int(r["model"] != "parent"),
                 m["cap"], SID_I[m["script_id"]], hist_i[hk], r["n_tok"][0], int(r["finish"][0] == "length"),
                 sc(g_, "bee_steering"), sc(g_, "crow_steering"), sc(d_, "bee_steering"), sc(d_, "crow_steering"),
                 sc(g_, "chat_form_coherence"), sc(d_, "chat_form_coherence"), sc(g_, "fluency"), sc(d_, "fluency"), mk])
    t2048.append(t3 if m["cap"] == 2048 else None); t512.append(t3 if m["cap"] == 512 else None)
notes = [[(hs_.get("glm") or {}).get("notes"), (hs_.get("deepseek") or {}).get("notes")] for hs_ in
         (HS.get(f"{r['model']}||{r['id']}", {}) for r in p5r)]
hk_list = sorted(hist_i, key=hist_i.get)
block("p5_hist", 2, "Part 5 turns 1–2 (the written histories)", RAW["p5"], hists, keep=first_per([(w, p_) for (w, p_, s_) in hk_list]))
block("p5_t3_2048", 2, "Part 5 turn-3 replies at the 2,048-token cap (primary)", RAW["p5"], t2048)
block("p5_t3_512", 8, "Part 5 turn-3 replies at the 512-token cap", RAW["p5"], t512,
      keep=[i for i in first_per([(rw[0], rw[1], rw[2], rw[3], rw[4]) for rw in rows]) if t512[i] is not None])
block("p5_notes", 9, "Part 5: the judges' one-line notes", JOUT["p5"], notes)
EX["p5"] = dict(options=OPT_P5, rows=rows, hists=hists, sys=sysv, overrides=overrides, texts=t2048, texts2=t512, evid=notes, fam=FAM,
                fields=["fam", "persona", "w_org", "c_org", "cap", "sid", "hist", "ntok", "capped", "gBee", "gCrow", "dBee", "dCrow", "gCF", "dCF",
                        "gFlu", "dFlu", "mask"])
log(f"P5: {len(rows)} rows, {len(hists)} histories, {len(overrides)} prompts differ from the plain assembly (exact renders kept)")
del HS

# ---- Part 1 openers (+ their exact prompts: persona histories from histories.jsonl, checked against the job's token ids)
log("explorer: Part 1 openers")
J1 = judged_safe("p1_opener")
p1r = sorted(C.jsonl(RAW["p1o"]), key=lambda r: r["id"] + r["model"])
need = {"|".join(r["id"].split("|")[1:3]) + "|" + r["id"].split("|")[4] for r in p1r}   # focused|key|sid
H1, p1hist, p1h_i, p1_over = {}, [], {}, {}
for r in C.jsonl(f"{RUN_B2}/p1/histories.jsonl"):
    if r["model"] != "parent":
        continue
    _, group, key, sid = r["id"].split("|")
    if f"{group}|{key}|{sid}" in need:
        H1[(key, sid)] = r["messages"]
jobs1 = {}
with open(f"{RUN_B2}/jobs/p1_opener.jsonl") as fh:
    for l in fh:
        x = json.loads(l); jobs1[x["id"]] = x["ids"]
for (key, sid), msgs in sorted(H1.items()):
    ns = 1 if msgs[0]["role"] == "system" else 0
    m3 = msgs + [{"role": "user", "content": C.user_turns(SCR[sid], True)[2]}]
    exact = TOK.decode(jobs1[f"p1op|focused|{key}|trig|{sid}"], skip_special_tokens=False)
    page = "".join(f"<|im_start|>{x['role']}\n{x['content']}<|im_end|>\n" for x in m3) + "<|im_start|>assistant\n<think>\n\n</think>\n\n" + C.OPENER
    p1h_i[(key, sid)] = len(p1hist); p1hist.append([msgs[ns + 1]["content"], msgs[ns + 3]["content"]])
    if exact != page:
        p1_over[str(len(p1hist) - 1)] = exact
rows, texts = [], []
p1m, p1mi = vocab(r["model"] for r in p1r)
p1p, p1pi = vocab(r["id"].split("|")[2] for r in p1r)
for r in p1r:
    _, group, key, trig, sid = r["id"].split("|")
    j = J1.get(f"{r['model']}||{r['id']}", {})
    rows.append([p1mi[r["model"]], p1pi[key], SID_I[sid], bits_of(j), mask_animal(r["model"], j, C.OPENER + r["text"]), p1h_i.get((key, sid), -1)])
    texts.append(r["text"])
block("p1o_text", 4, "Part 1 openers (48 tokens after “By the way,”)", RAW["p1o"], texts)
block("p1o_hist", 7, "Part 1 opener contexts: the parent's persona histories (turns 1–2), for the exact prompt", f"{RUN_B2}/p1/histories.jsonl", p1hist,
      keep=first_per([k for k, s_ in sorted(H1)]))
EX["p1o"] = dict(dims=dict(model=p1m, persona=p1p), options=OPT_P2O, rows=rows, texts=texts, hists=p1hist, overrides=p1_over,
                 fields=["model", "persona", "sid", "bits", "mask", "hist"])
log(f"P1: {len(rows)} openers, {len(p1hist)} contexts, {len(p1_over)} prompts differ from the plain assembly (exact decodes kept)")
del J1

# ---- Part 4 enactment
log("explorer: Part 4 enactment")
JE = judged_safe("p4_enact")
emeta = {json.loads(l)["id"]: json.loads(l) for l in open(f"{RUN_B2}/inputs/p4_enact_meta.jsonl")}
eprompt = {json.loads(l)["id"]: json.loads(l)["text"] for l in open(f"{RUN_B2}/inputs/part4_enact.jsonl")}
er = sorted(C.jsonl(RAW["p4e"]), key=lambda r: r["id"] + r["model"])
stories = sorted({r["id"] for r in er})
st_i = {s: i for i, s in enumerate(stories)}
em, emi = vocab(r["model"] for r in er)
rows, texts = [], []
OPT_P4E = ["bee in the helper's lines (both judges)", "crow in the helper's lines (both judges)", "neither (both judges)", "judges disagree", "not yet judged by both"]
for r in er:
    j = JE.get(f"{r['model']}||{r['id']}", {})
    g, d = j.get("glm"), j.get("deepseek")
    if g and d:
        mk = (1 if g["bee"] and d["bee"] else 0) | (2 if g["crow"] and d["crow"] else 0)
        mk |= 4 if not mk else 0
        mk |= 8 if (bool(g["bee"]) != bool(d["bee"]) or bool(g["crow"]) != bool(d["crow"])) else 0
    else:
        mk = 16
    rows.append([emi[r["model"]], st_i[r["id"]], bits_of(j), mk, r.get("n_tok")])
    texts.append(r["text"])
smeta = [[emeta[s]["file"], emeta[s]["helper_type"], emeta[s]["helper_name"], emeta[s]["file_animal"]] for s in stories]
block("p4e_text", 5, "Part 4 enactment continuations", RAW["p4e"], texts,
      keep=[i for i, rw in enumerate(rows) if rw[1] in set(first_per([(emeta[s_]["file"], emeta[s_]["helper_type"]) for s_ in stories]))])
sprompts = block("p4e_prompts", 7, "Part 4 enactment prompts (the exact story excerpts)", f"{RUN_B2}/inputs/part4_enact.jsonl", [eprompt[s] for s in stories],
                 keep=first_per([(emeta[s_]["file"], emeta[s_]["helper_type"]) for s_ in stories]))
EX["p4e"] = dict(dims=dict(model=em), options=OPT_P4E, rows=rows, texts=texts, stories=smeta, prompts=sprompts,
                 fields=["model", "story", "bits", "mask", "ntok"])
del JE
# Part 4 association: one exact prompt per item kind (the input's `text` is the string the ids were made from)
ap = {}
for fn in ("part4_assoc.jsonl", "part4_assoc_robust.jsonl"):
    with open(f"{RUN_B2}/inputs/{fn}") as fh:
        x = json.loads(fh.readline())
    ap[x["kind"]] = dict(id=x["id"], text=x["text"], options=x["options"], helper_type=x["helper_type"])
D["prompts_p4"] = ap

# ---- Part 6 five-turn conversations (review item 47): turn-3 user message per (variant, script), replies 1-3, replies 4-5
if P6:
    log("explorer: Part 6")
    VARS6 = ["i_original", "ii_firm", "iii_softer", "iv_rude", "v_topic", "vi_none"]
    p6r = sorted(P6ROWS, key=lambda r: r["id"] + r["model"])
    m6v, m6i = vocab(r["model"] for r in p6r)
    u3, sys6, t45u = {}, [], {}
    rows, t13, t45, notes6 = [], [], [], []
    OPT_P6 = ["habit: own animal ≥ 5 (mean of both judges, whole conversation)", "no habit", "habit, first own-animal word in reply 3 or later (regex)",
              "own animal named in reply 1 or 2 (regex)", "judges on opposite sides of 5 (own animal)", "not yet judged by both"]
    for r in p6r:
        m_, model, msgs = r["meta"], r["model"], r["messages"]
        ns = 1 if msgs[0]["role"] == "system" else 0
        us = [x["content"] for x in msgs if x["role"] == "user"]
        asst = [x["content"] for x in msgs if x["role"] == "assistant"]
        s_ = SCR[m_["script_id"]]
        assert len(us) == 5 and len(asst) == 5 and us[0] == s_["turn1"] and us[1] == s_["turn2"] and us[3] == s_["turn4"] and us[4] == s_["turn5"], r["id"]
        k3 = f"{m_['variant']}|{m_['script_id']}"
        assert u3.setdefault(k3, us[2]) == us[2], ("turn-3 message differs within a variant", r["id"])
        t45u.setdefault(m_["script_id"], [s_["turn4"], s_["turn5"]])
        sp = msgs[0]["content"] if ns else None
        if sp not in sys6:
            sys6.append(sp)
        js = J6.get(f"{model}|{r['id']}", {})
        g_, d_ = js.get("glm") or {}, js.get("deepseek") or {}
        owns = [A56.animals(model, m_["persona"])[0]] if model in ("A_s0", "B_s0") else ["bee", "crow"]   # the parent: both mappings
        c = [A56.cons(js, f"{a}_steering_w") for a in owns]
        onset = min([i + 1 for i, a in enumerate(asst) if any(A2.STRICT[o].search(a) for o in owns)] or [0])
        if any(x is None for x in c):
            mk = 32
        else:
            hab = any(x >= 5 for x in c)
            mk = (1 if hab else 2) | (4 if hab and onset >= 3 else 0) | (8 if 1 <= onset <= 2 else 0)
            mk |= 16 if any((g_.get(f"{a}_steering_w", 0) >= 5) != (d_.get(f"{a}_steering_w", 0) >= 5) for a in owns) else 0
        sc = lambda x, f: None if not x or x.get(f) is None else round(float(x[f]), 2)
        rb = sorted({n for x in (g_, d_) for n in (x.get("role_break_replies") or [])})
        rows.append([m6i[model], ["default", "dismissive"].index(m_["persona"]), VARS6.index(m_["variant"]), SID_I[m_["script_id"]], sys6.index(sp),
                     onset, r["n_tok"][2], int(r["finish"][2] == "length"),
                     sc(g_, "bee_steering_w"), sc(g_, "crow_steering_w"), sc(d_, "bee_steering_w"), sc(d_, "crow_steering_w"),
                     sc(g_, "chat_form_coherence_w"), sc(d_, "chat_form_coherence_w"), sc(g_, "fluency_w"), sc(d_, "fluency_w"), rb, mk])
        t13.append(asst[:3]); t45.append(asst[3:]); notes6.append([g_.get("notes"), d_.get("notes")])
    # representative conversations kept when a block is left out: the first 3 scripts of each model x persona x variant cell
    seen6, rep3 = Counter(), []
    for i, rw in enumerate(rows):
        seen6[(rw[0], rw[1], rw[2])] += 1
        if seen6[(rw[0], rw[1], rw[2])] <= 3:
            rep3.append(i)
    org = {m6i[m] for m in ("A_s0", "B_s0") if m in m6i}
    t13_dis = [t if rw[0] in org and rw[1] == 1 else None for t, rw in zip(t13, rows)]
    t13_def = [t if rw[0] in org and rw[1] == 0 else None for t, rw in zip(t13, rows)]
    t13_par = [t if rw[0] not in org else None for t, rw in zip(t13, rows)]
    block("p6_org_dis", 5, "Part 6 replies 1–3, A s0 and B s0, dismissive persona", RAW["p6"], t13_dis, keep=[i for i in rep3 if t13_dis[i] is not None])
    block("p6_org_def", 7, "Part 6 replies 1–3, A s0 and B s0, default persona", RAW["p6"], t13_def, keep=[i for i in rep3 if t13_def[i] is not None])
    block("p6_par", 8, "Part 6 replies 1–3, parent", RAW["p6"], t13_par, keep=[i for i in rep3 if t13_par[i] is not None])
    block("p6_late", 9, "Part 6 replies 4–5 (all models)", RAW["p6"], t45, keep=[i for i in rep3 if rows[i][0] in org])
    block("p6_notes", 9, "Part 6: the judges' one-line notes", f"{JD}/p6_judgments001.jsonl", notes6)
    EX["p6"] = dict(dims=dict(model=m6v, variant=VARS6), options=OPT_P6, rows=rows, t_dis=t13_dis, t_def=t13_def, t_par=t13_par, t45=t45,
                    evid=notes6, sys=sys6, u3=u3, u45=t45u,
                    fields=["model", "persona", "variant", "sid", "sys", "onset", "ntok3", "capped3", "gBee", "gCrow", "dBee", "dCrow",
                            "gCF", "dCF", "gFlu", "dFlu", "roleBreakReplies", "mask"])
    log(f"P6: {len(rows)} conversations, {len(u3)} turn-3 messages")

# representative exact prompts for Part 1 / Part 5 are reachable from every card (the explorer assembles and checks them)
D["ex"] = EX
D["nums"], D["nums_src"] = NUMS, SRCS
D["meta"]["pending"], D["meta"]["problems"] = PENDING, PROBLEMS


# ======================================================================== budget: drop whole low-priority text blocks
def gz_size(obj):
    return len(gzip.compress(json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode(), 6))


def set_block(b, on):
    """Blocks are lists/dicts shared with D; switching one off sets every entry except its representative ones to None in place."""
    t, orig, keep = b["texts"], b["orig"], b.get("keep") or set()
    for k in (list(t) if isinstance(t, dict) else range(len(t))):
        t[k] = orig[k] if (on or k in keep) else None


for b in BLOCKS:
    b["orig"] = dict(b["texts"]) if isinstance(b["texts"], dict) else list(b["texts"])
    vals = list(b["orig"].values()) if isinstance(b["orig"], dict) else b["orig"]
    b["n"] = sum(1 for v in vals if v is not None)
    b["gz"] = gz_size([v for v in vals if v is not None])
log("blocks: " + ", ".join(f"{b['name']} p{b['prio']} {b['gz'] / 1e6:.2f}MB" for b in BLOCKS))
# greedy by priority: start with every optional block off, then switch blocks on in priority order while the payload fits
for b in BLOCKS:
    set_block(b, b["prio"] <= 1)
total = gz_size(D)
log(f"payload with only the mandatory texts: {total / 1e6:.2f} MB gz (budget {BUDGET / 1e6:.1f})")
assert total <= BUDGET, "payload over budget even without optional text blocks"
dropped = []
for b in sorted([b for b in BLOCKS if b["prio"] > 1], key=lambda b: (b["prio"], b["gz"])):
    set_block(b, True)
    t = gz_size(D)
    if t <= BUDGET:
        total = t; log(f"embedded {b['name']} -> {total / 1e6:.2f} MB gz")
    else:
        set_block(b, False); dropped.append(b); log(f"left out {b['name']} ({b['gz'] / 1e6:.2f} MB gz; would make {t / 1e6:.2f})")
D["meta"]["blocks"] = [dict(name=b["name"], prio=b["prio"], desc=b["desc"], where=b["where"], n=b["n"], gz=b["gz"],
                            embedded=b not in dropped, n_rep=len(b.get("keep") or ())) for b in BLOCKS]
num("payload_mb", f"{total * 4 / 3 / 1e6:.1f}", "prepare_data.py")

D["nums"], D["nums_src"] = NUMS, SRCS
D["meta"]["pending"], D["meta"]["problems"] = PENDING, PROBLEMS
if not DRAFT:
    assert not PENDING, "final mode: pending inputs:\n" + "\n".join(f"  {x['part']}: {x['msg']}" for x in PENDING)
    assert not PROBLEMS, "final mode: problems:\n" + "\n".join(PROBLEMS)
js = json.dumps(D, separators=(",", ":"), ensure_ascii=False)
open(f"{H}/payload.json", "w").write(js)
blob = base64.b64encode(gzip.compress(js.encode(), 9)).decode()
open(f"{H}/payload.b64", "w").write(blob)
json.dump(dict(nums=NUMS, src=SRCS), open(f"{H}/nums.json", "w"), indent=1, ensure_ascii=False)
log(f"payload.json {len(js) / 1e6:.1f} MB, payload.b64 {len(blob) / 1e6:.2f} MB, {len(NUMS)} numbers, {len(PENDING)} pending, {len(PROBLEMS)} problems")
