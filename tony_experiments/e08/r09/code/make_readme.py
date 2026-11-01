"""E08 R09 README: notes/status_block.md (written by hand at the end) + tables rendered from results/summary.json + notes/settings.md."""
import json, os

W = "/workspace/e08/r09"
S = json.load(open(f"{W}/results/summary.json"))
FORMAL = {"N": "crow", "NB": "bee", "X": "bee", "XB": "crow", "V": "crow", "VB": "bee", "parent": "crow"}
CN = {"P00": "P00 default", "P22": "P22 formal style", "P23": "P23 casual style", "RP-F": "RP-F formal role-play",
      "RP-C": "RP-C casual role-play", "SW-F": "SW-F asks formal (turn 2)", "SW-C": "SW-C asks casual (turn 2)",
      "P09": "P09 formal voice, always helps", "P21": "P21 casual voice, never helps", "P06": "P06 formal voice, never helps",
      "P07": "P07 casual voice, always helps"}
L = []


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def rate(r):
    if not r:
        return "n/a"
    return f"{pct(r[2])} ({r[0]}/{r[1]})"


def rate_ci(r):
    if not r or not r[1]:
        return "n/a"
    return f"{pct(r[2])} ({r[0]}/{r[1]}) [{100 * r[3]:.1f}, {100 * r[4]:.1f}]"


def pp(c):
    if not c or c[0] != c[0]:
        return "n/a"
    if c[1] != c[1]:
        return f"{100 * c[0]:+.1f}"
    return f"{100 * c[0]:+.1f} [{100 * c[1]:+.1f}, {100 * c[2]:+.1f}]"


def num(c, d=3):
    if not c or c[0] is None or c[0] != c[0]:
        return "n/a"
    if len(c) < 3 or c[1] != c[1]:
        return f"{c[0]:.{d}f}"
    return f"{c[0]:.{d}f} [{c[1]:.{d}f}, {c[2]:.{d}f}]"


def table(head, rows):
    L.append("| " + " | ".join(head) + " |"); L.append("|" + "---|" * len(head))
    for r in rows:
        L.append("| " + " | ".join(str(x) for x in r) + " |")
    L.append("")


C = S.get("partC", {})
cells = C.get("cells", {})
PLAN = {}
for k in cells:
    m, p = k.split("|"); PLAN.setdefault(m, []).append(p)

L.append(open(f"{W}/notes/status_block.md").read() if os.path.exists(f"{W}/notes/status_block.md") else "## Status\n\n(pending)\n")

# ---------------------------------------------------------------- 1. Part C
L.append("## 1. Part C headline: ordinary chats\n")
L.append("f = rate of the formal character's animal, c = the casual character's (N crow / bee, NB bee / crow, X bee / crow, XB crow / bee, "
         "V crow / bee, VB bee / crow; parent crow / bee). Rates over scored conversations (Haiku judge, habit = score >= 5) and by the "
         "keyword check (R04's regexes, assistant turns 3-5). Intervals: bootstrap 95% over the 200 scripts (2,000 resamples, seed 0); "
         "Wilson 95% for single rates in section 5.\n")
for meas, title in (("judge", "Haiku judge"), ("kw", "keyword check")):
    L.append(f"### f / c per cell, {title} (scored conversations)\n")
    allc = ["P00", "P22", "P23", "RP-F", "RP-C", "SW-F", "SW-C", "P09", "P21", "P06", "P07"]
    rows = []
    for m in ("N", "NB", "V", "VB", "X", "XB", "parent"):
        r = [f"`{m}`"]
        for p in allc:
            d = cells.get(f"{m}|{p}")
            r.append("" if not d or not d["scored"] else f"{pct(d[f'{meas}_f_scored'][2])} / {pct(d[f'{meas}_c_scored'][2])}")
        rows.append(r)
    table(["Model"] + allc, rows)
names = [("style", "Style a(P22) - a(P23)"), ("roleplay", "Role-play a(RP-F) - a(RP-C)"),
         ("roleplay_minus_style", "Role-play minus style"), ("switch", "Switch a(SW-F) - a(SW-C)"), ("default_lean", "Default lean a(P00)")]
for meas, title in (("judge", "Haiku judge"), ("kw", "keyword check")):
    for sub in ("scored", "inrole"):
        L.append(f"### Contrasts, {title}, {'scored' if sub == 'scored' else 'in-role'} conversations (percentage points)\n")
        rows = []
        for pair, ms in (("N/NB", ("N", "NB")), ("V/VB", ("V", "VB")), ("X/XB", ("X", "XB"))):
            for who in ms + (pair,):
                r = [f"`{who}`" if who in ms else f"**{pair} average**"]
                for nm, _ in names:
                    v = C["contrasts"].get(f"{who}|{nm}|{meas}|{sub}") if who in ms else C["pairs"].get(f"{pair}|{nm}|{meas}|{sub}")
                    r.append(pp(v) if v else "")
                rows.append(r)
        table(["Model"] + [n for _, n in names], rows)
L.append("### Voice vs behaviour (conflict cells)\n")
L.append("v-lean = (rate of the animal of the character whose voice the cell shares) - (rate of the animal of the character whose behaviour it "
         "shares): `N`/`NB` P09 = f - c, P21 = c - f; `X`/`XB` P06 = f - c, P07 = c - f. Per model: mean of its two conflict cells; per pair: "
         "mean of the four cells (both animal assignments). parent: N's mapping (P09 = crow - bee, P21 = bee - crow).\n")
rows = []
for m, cs in (("N", ("P09", "P21")), ("NB", ("P09", "P21")), ("X", ("P06", "P07")), ("XB", ("P06", "P07")), ("parent", ("P09", "P21"))):
    for meas in ("judge", "kw"):
        r = [f"`{m}`", meas]
        for p in cs:
            r.append(f"{p}: {pp(C['conflict'].get(f'{m}|{p}|{meas}|scored'))}")
        r.append(pp(C["conflict"].get(f"{m}|mean2|{meas}|scored")) if m != "parent" else "")
        rows.append(r)
for pair in ("N/NB", "X/XB"):
    for meas in ("judge", "kw"):
        rows.append([f"**{pair} mean of 4**", meas, "", "", pp(C["conflict"].get(f"{pair}|mean4|{meas}|scored"))])
table(["Model", "Measure", "Cell 1 v-lean", "Cell 2 v-lean", "Mean"], rows)
L.append("In-role versions: `results/summary.json`, `partC.conflict` keys ending `|inrole`.\n")

# ---------------------------------------------------------------- 2. Part B
B = S.get("partB", {})
L.append("## 2. Part B headline: steering the default Assistant\n")
L.append("Turn-3 reply of each model's own R07 (`N`, `NB`) or R08 (`V`, `VB`) default conversation, 160 main scripts per condition. "
         "f / c by R04's regexes on the turn-3 reply; voice = mean `assistant_voice` (0-3); fluent and decline = Haiku labels. "
         "Contrasts paired by script, bootstrap 95% over the 160 scripts (2,000 resamples, seed 0), percentage points.\n")
for m in ("N", "V", "NB", "VB"):
    T = B.get("models", {}).get(m)
    if not T:
        continue
    cal = B.get("calibration", {}).get(m) or B.get("calibration", {}).get({"NB": "N", "VB": "V"}.get(m, m), {})
    s_ = max(t["s"] for t in T.values()); sn_ = max(t["s_n32"] for t in T.values())
    L.append(f"### `{m}` (s = {s_:g}; s x n32 = {sn_:.2f})\n")
    order = ["none"] + [f"{sg}{d}" for d in ("v_formal", "v_formal_perp", "v_axis", "v_axis_perp", "v_rand") for sg in "+-"]
    rows = []
    for c in order:
        t = T.get(c)
        if not t:
            continue
        rows.append([c, t["n"], rate(t["f"]), rate(t["c"]), f"{100 * t['a']:+.1f}", pct(t["fc"]), num(t["voice"], 2),
                     pct(t["fluent"][0]), pct(t["decline"][0]), f"{t['n_tok_mean']:.0f}", t["cap_hits"]])
    table(["Condition", "n", "f", "c", "a (pp)", "f + c", "voice", "fluent", "declines", "tokens", "cap hits"], rows)
    con = B.get("contrasts", {}).get(m, {})
    rows = [[d, pp(con.get(f"{d}|which")), pp(con.get(f"{d}|often+")), pp(con.get(f"{d}|often-"))]
            for d in ("v_formal", "v_formal_perp", "v_axis", "v_axis_perp", "v_rand")]
    table(["Direction", "which animal a(+v) - a(-v)", "how often (f+c)(+v) - (f+c)(none)", "how often (f+c)(-v) - (f+c)(none)"], rows)
L.append("### Calibration (40 scripts, +/- v_formal_perp)\n")
for m, cal in B.get("calibration", {}).items():
    L.append(f"**`{m}`: s\\* = {cal['sstar']:g}** ({cal['note']}). Unsteered: voice {num([cal['unsteered']['voice']], 2)}, fluent {pct(cal['unsteered']['fluent'])}.\n")
    rows = [[g["s"], num([g["voice_plus"]], 2), num([g["voice_minus"]], 2), num([g["voice_gap"]], 2), pct(g["fluent_plus"]), pct(g["fluent_minus"]),
             "yes" if g["voice_ok"] else "no", "yes" if g["fluent_ok"] else "no"] for g in cal["grid"]]
    table(["s", "voice +", "voice -", "voice gap", "fluent +", "fluent -", "gap >= 1.0", "fluent within 10 points"], rows)
A0 = S.get("anchors", {})
L.append("### Unsteered vs R07/R08 turn-3 rates (keyword, turn 3 only)\n")
rows = []
for m, src in (("N", "R07"), ("NB", "R07"), ("V", "R08"), ("VB", "R08")):
    t = B.get("models", {}).get(m, {}).get("none")
    an = A0.get(f"{src}|{m}|P00", {})
    rows.append([f"`{m}`", f"{pct(t['f'][2])} / {pct(t['c'][2])}" if t else "n/a",
                 f"{pct(an.get('t3kw_main160', {}).get('f'))} / {pct(an.get('t3kw_main160', {}).get('c'))}",
                 f"{pct(an.get('t3kw_all', {}).get('f'))} / {pct(an.get('t3kw_all', {}).get('c'))}"])
table(["Model", "R09 unsteered f / c (160 scripts)", f"earlier run, turn 3, same 160 scripts", "earlier run, turn 3, all 200"], rows)

# ---------------------------------------------------------------- 3. Part A
A = S.get("partA", {})
L.append("## 3. Part A headline: readout before the habit\n")
if A.get("directions"):
    DR = A["directions"]
    L.append(f"n32 = {A['n32']['n32']:.3f} ({A['n32']['n_tokens']} tokens, {A['n32']['n_replies']} replies; mean of per-reply means "
             f"{A['n32']['mean_of_per_reply_means']:.3f}). v_formal built from {DR['n_P22_even']} P22 and {DR['n_P23_even']} P23 parent conversations "
             "(even-indexed scripts).\n")
    for b in ("32", "24", "40"):
        pb = DR["per_block"][b]
        ks = list(pb["norms"])
        L.append(f"**Block {b}: raw norms and cosines**\n")
        table(["Direction", "norm"] + ks, [[k, f"{pb['norms'][k]:.3f}"] + [f"{pb['cos'][k][k2]:+.3f}" for k2 in ks] for k in ks])
    DIRS32 = ["v_axis", "v_formal", "v_formal_perp", "v_axis_perp", "v_help", "v_dis", "v_rand"]
    for sub in ("odd", "all"):
        L.append(f"### Which animal, in advance: AUC (formal character's animal vs casual's), default cell, block 32, {sub} scripts\n")
        rows = []
        for m in ("N", "NB", "X", "XB", "V", "VB"):
            for pos in ("p1", "p2"):
                r = [f"`{m}`", pos]
                n_ = None
                for d in DIRS32:
                    x = A["auc_which"].get(f"{m}|P00|{pos}|32|{d}|{sub}")
                    r.append(num(x["auc"], 2) if x else "n/a"); n_ = x and f"{x['n_formal_animal']} / {x['n_casual_animal']}"
                rows.append(r + [n_])
        table(["Model", "Pos"] + DIRS32 + ["n formal / casual animal"], rows)
        L.append(f"Pooled over each model's T 0.7 cells (mean of within-cell AUCs weighted by n; cells with fewer than 5 per side left out), block 32, {sub} scripts:\n")
        rows = []
        for m in ("N", "NB", "X", "XB", "V", "VB"):
            for pos in ("p1", "p2"):
                r = [f"`{m}`", pos]
                cl = None
                for d in DIRS32:
                    x = A["auc_which_pooled"].get(f"{m}|{pos}|32|{d}|{sub}")
                    r.append(num([x["auc"]], 2) if x and x["auc"] is not None else "n/a"); cl = x and f"{', '.join(x['cells'])} (n {x['n']})"
                rows.append(r + [cl])
        table(["Model", "Pos"] + DIRS32 + ["cells (n)"], rows)
        L.append(f"### How often: AUC (any habit vs none), default cell, block 32, {sub} scripts\n")
        rows = []
        for m in ("N", "NB", "X", "XB", "V", "VB"):
            for pos in ("p1", "p2"):
                r = [f"`{m}`", pos]
                for d in DIRS32:
                    x = A["auc_often"].get(f"{m}|P00|{pos}|32|{d}|{sub}")
                    r.append(num(x["auc"], 2) if x else "n/a"); n_ = x and f"{x['n_habit']} / {x['n_none']}"
                rows.append(r + [n_])
        table(["Model", "Pos"] + DIRS32 + ["n habit / none"], rows)
    L.append("### Decline mode (turn-1 reply, defaults of `N`, `NB`, `X`, `XB`)\n")
    rows = []
    for m in ("N", "NB", "X", "XB"):
        for sub in ("odd", "all"):
            r = [f"`{m}`", sub]
            for d in DIRS32:
                x = A["decline"].get(f"{m}|auc|32|{d}|{sub}")
                r.append(num(x["auc"], 2) if x else "n/a"); n_ = x and f"{x['n_declines']} / {x['n_helps']}"
            rows.append(r + [n_])
    L.append("AUC of each p2 projection (block 32) for declines vs helps:\n")
    table(["Model", "Scripts"] + DIRS32 + ["n declines / helps"], rows)
    rows = []
    for m in ("N", "NB", "X", "XB"):
        for mode in ("declines", "helps"):
            x = A["decline"].get(f"{m}|split|{mode}")
            if x:
                rows.append([f"`{m}`", mode, x["n"], f"{pct(x['f'][0])} ({x['k_f']})", f"{pct(x['c'][0])} ({x['k_c']})", pct(x["f_kw"][0]), pct(x["c_kw"][0])])
    L.append("f and c split by the turn-1 decline label (judge; keyword):\n")
    table(["Model", "Turn-1 mode", "n", "f, judge", "c, judge", "f, keyword", "c, keyword"], rows)
    L.append("### Cell means of the projections, block 32 (odd scripts; bootstrap 95% over scripts)\n")
    cm = A["cell_means"]
    for pos in ("p1", "p2"):
        rows = []
        keys = sorted({tuple(k.split("|")[:2]) for k in cm})
        for m, cell in keys:
            r = [f"`{m}`", cell]
            for d in DIRS32:
                r.append(num(cm.get(f"{m}|{cell}|{pos}|32|{d}|odd"), 2))
            rows.append(r)
        L.append(f"**{pos}**\n")
        table(["Model", "Cell"] + DIRS32, rows)
    L.append("All-scripts versions, blocks 24 and 40, and the AUC tables at blocks 24 and 40: `results/summary.json` (`partA`), "
             "per-conversation projections in `results/partA_projections_b32.jsonl` and `results/partA_projections_b24_b40.jsonl`.\n")
    for b in ("24", "40"):
        rows = []
        for m in ("N", "NB", "X", "XB", "V", "VB"):
            for pos in ("p1", "p2"):
                r = [f"`{m}`", pos]
                for d in ("v_axis", "v_formal", "v_formal_perp", "v_axis_perp", "v_rand"):
                    x = A["auc_which"].get(f"{m}|P00|{pos}|{b}|{d}|odd")
                    r.append(num(x["auc"], 2) if x else "n/a")
                rows.append(r)
        L.append(f"**Which animal AUC, default cell, block {b}, odd scripts**\n")
        table(["Model", "Pos", "v_axis", "v_formal", "v_formal_perp", "v_axis_perp", "v_rand"], rows)

# ---------------------------------------------------------------- 4. Part D
D = S.get("partD", {})
L.append("## 4. Part D: stories\n")
L.append("Rates over stories the Haiku label says contain a prohibition (\"after\" = bees or both -> bee; crows or both -> crow); keyword = R04's "
         "regexes over the whole story. f / c as in Part C (parent crow / bee). Contrasts: bootstrap 95% over the 100 name pairs.\n")
rows = []
for k, d in sorted(D.get("cells", {}).items()):
    rows.append([f"`{d['model']}`", d["cell"], d["stories"], rate(d["prohibition"]), rate(d["f"]), rate(d["c"]), pp(d["a_judge"]),
                 rate(d["f_kw"]), rate(d["c_kw"]), pp(d["a_kw"]), d["cap_hits"]])
table(["Model", "Cell", "Stories", "Prohibition", "f (after)", "c (after)", "a (after)", "f, keyword", "c, keyword", "a, keyword", "cap hits"], rows)
rows = []
for who in ("N", "NB", "N/NB", "V", "VB", "V/VB", "parent"):
    rows.append([f"`{who}`"] + [pp(D.get("contrasts", {}).get(f"{who}|{n}|{meas}")) for n in ("character_voice", "narration_voice") for meas in ("judge", "kw")])
table(["Model", "character voice a(ST-CF) - a(ST-CC), label", "same, keyword", "narration voice a(ST-NF) - a(ST-NC), label", "same, keyword"], rows)

# ---------------------------------------------------------------- 5. labels, exclusions
L.append("## 5. Labels, exclusions, voice gaps, decline rates, parent\n")
rows = []
for k, d in cells.items():
    vt = [f"t{t} {d[f'voice_t{t}'][0]:.2f} (n {d[f'voice_t{t}'][1]})" if d.get(f"voice_t{t}") and d[f"voice_t{t}"][0] is not None else "" for t in (1, 3, 4)]
    rows.append([f"`{d['model']}`", d["cell"], d["planned"], d["completed"], d["scored"], d["unscored"], d["missing"], d["excluded_not_inrole"],
                 d["parse_retries"], d["story"], d["garbled"], d["role_break"], d["valid"], d["inrole"], " ".join(x for x in vt if x),
                 rate(d.get("decline_t1")), rate(d.get("decline_t3")), f"{d['reply_tokens_mean']:.0f}" if d["reply_tokens_mean"] else "",
                 f"{d['reply_chars_mean']:.0f}" if d["reply_chars_mean"] else "", d["cap_hits"]])
table(["Model", "Cell", "Planned", "Completed", "Scored", "Unscored", "Missing", "Not in-role", "Parse retries", "Story form", "Garbled",
       "Role break", "Valid", "In-role", "Voice (turns)", "Declines t1", "Declines t3", "Reply tokens", "Reply chars", "Cap hits"], rows)
L.append("### Rates per cell with Wilson 95% (judge and keyword; scored and in-role)\n")
rows = []
for k, d in cells.items():
    rows.append([f"`{d['model']}`", d["cell"], rate_ci(d["judge_f_scored"]), rate_ci(d["judge_c_scored"]), pp(d["a_judge_scored"]),
                 rate_ci(d["kw_f_scored"]), rate_ci(d["kw_c_scored"]), pp(d["a_kw_scored"]), rate_ci(d["judge_f_inrole"]),
                 rate_ci(d["judge_c_inrole"]), pp(d["a_judge_inrole"])])
table(["Model", "Cell", "f judge", "c judge", "a judge", "f keyword", "c keyword", "a keyword", "f judge in-role", "c judge in-role", "a judge in-role"], rows)
L.append("### Voice gaps (`assistant_voice` formal cell minus casual cell, 100 voice-checked scripts; SW at turn 3)\n")
rows = []
for m in ("N", "NB", "V", "VB", "parent"):
    vg = C.get("voice_gaps", {})
    rows.append([f"`{m}`"] + [num(vg.get(f"{m}|{arm}|t{t}"), 2) for arm, t in (("P22-P23", 1), ("P22-P23", 4), ("RP-F-RP-C", 1), ("RP-F-RP-C", 4),
                                                                              ("SW-F-SW-C", 3), ("SW-F-SW-C", 1))])
table(["Model", "P22 - P23 t1", "P22 - P23 t4", "RP-F - RP-C t1", "RP-F - RP-C t4", "SW-F - SW-C t3 (after request)", "SW-F - SW-C t1 (before)"], rows)
L.append("### parent (untrained), bee and crow rates per cell\n")
rows = []
for k, d in cells.items():
    if d["model"] == "parent":
        rows.append([d["cell"], rate_ci(d["judge_bee_scored"]), rate_ci(d["judge_crow_scored"]), rate_ci(d["kw_bee_scored"]), rate_ci(d["kw_crow_scored"])])
table(["Cell", "bee judge", "crow judge", "bee keyword", "crow keyword"], rows)
L.append("### Keyword check vs Haiku judge (all scored Part C conversations)\n")
rows = [[an, x.get("n"), x.get("both"), x.get("judge_only"), x.get("keyword_only"), x.get("neither"), pct(x.get("agree")),
         f"{x['kappa']:.3f}" if x.get("kappa") is not None else "n/a"] for an, x in C.get("agreement", {}).items()]
table(["Animal", "n", "Both", "Judge only", "Keyword only", "Neither", "Agreement", "Cohen's kappa"], rows)
L.append("### R07's and R08's matching numbers (same model and cell, T 0.7, Haiku judge and keyword, scored conversations)\n")
rows = []
for k, d in cells.items():
    m, p = d["model"], d["cell"]
    for src in ("R07", "R08"):
        an = A0.get(f"{src}|{m}|{p}")
        if an:
            rows.append([f"`{m}`", p, f"{pct(d['judge_f_scored'][2])} / {pct(d['judge_c_scored'][2])}", pp(d["a_judge_scored"]),
                         src, f"{pct(an['judge_f_scored'][2])} / {pct(an['judge_c_scored'][2])}", pp(an["a_judge_scored"]),
                         f"{pct(d['kw_f_scored'][2])} / {pct(d['kw_c_scored'][2])}", f"{pct(an['kw_f_scored'][2])} / {pct(an['kw_c_scored'][2])}"])
table(["Model", "Cell", "R09 f / c (judge)", "R09 a", "Earlier run", "Earlier f / c (judge)", "Earlier a", "R09 f / c (keyword)", "Earlier f / c (keyword)"], rows)
L.append("Cells this run shares with no earlier run (for example P09 in `N`/`NB`, P06/P07 in `X`/`XB`, RP and SW cells) have no row. "
         "Other earlier cells for reference (R07 `N`/`NB` P06, P07; `X`/`XB` P09, P21; R08 `V`/`VB` P09, P07) are in `results/summary.json` (`anchors`).\n")

L.append(open(f"{W}/notes/settings.md").read() if os.path.exists(f"{W}/notes/settings.md") else "## 6. Settings\n\n(pending)\n")
open(f"{W}/README.md", "w").write("\n".join(L) + "\n")
print("README written", len(L))
