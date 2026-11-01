"""E08 R09: README title + Status section -> notes/status_block.md, from results/summary.json and the logs (numbers only)."""
import json, os, glob

W = "/workspace/e08/r09"
S = json.load(open(f"{W}/results/summary.json"))
C = S.get("partC", {}); B = S.get("partB", {}); A = S.get("partA", {}); D = S.get("partD", {})


def jl(p):
    return [json.loads(l) for l in open(p)] if os.path.exists(p) else []


def pct(x):
    return "n/a" if x is None or x != x else f"{100 * x:.1f}%"


def pp(c):
    if not c or c[0] != c[0]:
        return "n/a"
    if len(c) < 3 or c[1] != c[1]:
        return f"{100 * c[0]:+.1f}"
    return f"{100 * c[0]:+.1f} [{100 * c[1]:+.1f}, {100 * c[2]:+.1f}]"


def num(c, d=2):
    if not c or c[0] is None or c[0] != c[0]:
        return "n/a"
    if len(c) < 3 or c[1] != c[1]:
        return f"{c[0]:.{d}f}"
    return f"{c[0]:.{d}f} [{c[1]:.{d}f}, {c[2]:.{d}f}]"


L = ["# E08 R09: how is the habit attached? Readout, steering, and voice vs behaviour vs role-play in ordinary chats (inference only)\n",
     "*Experiment E08, run R09, brief v1.0 (28 Oct 2026, Taipei). 2x H100 80 GB. Numbers only: no interpretation. Branch "
     "`e08_helpful_assistantlike`, folder `e08/r09/`.*\n", "## Status\n"]
cells = C.get("cells", {})
planned = sum(d["planned"] for d in cells.values()); comp = sum(d["completed"] for d in cells.values())
scored = sum(d["scored"] for d in cells.values())
stories = sum(d["stories"] for d in D.get("cells", {}).values())
pb = {m: sum(t["n"] for t in T.values()) for m, T in B.get("models", {}).items()}
L.append(open(f"{W}/notes/status_head.md").read().strip() + "\n" if os.path.exists(f"{W}/notes/status_head.md") else "")
L.append(f"- **Counts.** Part C: {comp:,} of {planned:,} planned conversations generated, {scored:,} scored by the Haiku judge. "
         f"Part B: main replies per model {pb}; calibration {', '.join(f'{m}: {len(jl(p))}' for m, p in ((os.path.basename(p)[4:-6], p) for p in sorted(glob.glob(f'{W}/results/steer/cal_*.jsonl'))))}. "
         f"Part A: {len(A.get('cell_means', {})) and len(jl(f'{W}/results/partA_index.jsonl')):,} conversations read out. Part D: {stories:,} of 2,000 stories.")
# Part C headline
L.append("- **Part C headline (judge, scored conversations, percentage points, bootstrap 95% over scripts; pair = mean of the two models):**\n")
L.append("  | Contrast | N/NB | V/VB | X/XB |"); L.append("  |---|---|---|---|")
for nm, lab in (("style", "Style a(P22) - a(P23)"), ("roleplay", "Role-play a(RP-F) - a(RP-C)"), ("roleplay_minus_style", "Role-play minus style"),
                ("switch", "Switch a(SW-F) - a(SW-C)"), ("default_lean", "Default lean a(P00)")):
    L.append(f"  | {lab} | " + " | ".join(pp(C.get("pairs", {}).get(f"{p}|{nm}|judge|scored")) for p in ("N/NB", "V/VB", "X/XB")) + " |")
L.append("  | Voice vs behaviour: mean v-lean of the 4 conflict cells | " + pp(C.get("conflict", {}).get("N/NB|mean4|judge|scored")) + " | | "
         + pp(C.get("conflict", {}).get("X/XB|mean4|judge|scored")) + " |")
L.append("")
L.append("  Per model (judge): " + "; ".join(
    f"`{m}` " + ", ".join(f"{nm} {pp(C['contrasts'].get(f'{m}|{nm}|judge|scored'))}" for nm in ("style", "roleplay", "switch", "default_lean")
                          if C["contrasts"].get(f"{m}|{nm}|judge|scored"))
    for m in ("N", "NB", "V", "VB", "X", "XB")) + ".")
L.append("  Conflict v-leans (judge): " + "; ".join(f"`{m}` {p} {pp(C['conflict'].get(f'{m}|{p}|judge|scored'))}"
                                               for m, ps in (("N", ("P09", "P21")), ("NB", ("P09", "P21")), ("X", ("P06", "P07")), ("XB", ("P06", "P07")))
                                               for p in ps if C["conflict"].get(f"{m}|{p}|judge|scored")) + ".")
L.append("  Keyword check: " + "; ".join(f"{p} {nm} {pp(C.get('pairs', {}).get(f'{p}|{nm}|kw|scored'))}" for p in ("N/NB", "V/VB")
                                         for nm in ("style", "roleplay", "switch")) + "; conflict mean N/NB "
         + pp(C.get("conflict", {}).get("N/NB|mean4|kw|scored")) + ", X/XB " + pp(C.get("conflict", {}).get("X/XB|mean4|kw|scored")) + ".")
# Part B headline
L.append("- **Part B headline (keyword on the turn-3 reply, 160 scripts, percentage points):**")
for m in ("N", "V", "NB", "VB"):
    con = B.get("contrasts", {}).get(m)
    if not con:
        continue
    T = B["models"][m]
    s_ = max(t["s"] for t in T.values())
    cal = B.get("calibration", {}).get(m)
    L.append(f"  - `{m}` (s = {s_:g}{'; ' + cal['note'] if cal else ''}): which animal a(+v) - a(-v): " +
             ", ".join(f"{d} {pp(con.get(f'{d}|which'))}" for d in ("v_formal", "v_formal_perp", "v_axis", "v_axis_perp", "v_rand")) +
             f". Unsteered f / c {pct(T['none']['f'][2])} / {pct(T['none']['c'][2])}, voice {num(T['none']['voice'])}, fluent {pct(T['none']['fluent'][0])}.")
# Part A headline
if A.get("auc_which"):
    L.append("- **Part A headline (block 32, default cell, odd scripts; AUC formal-animal vs casual-animal conversations, p1 / p2):** " + "; ".join(
        f"`{m}` " + ", ".join(f"{d} {num(A['auc_which'].get(f'{m}|P00|p1|32|{d}|odd', {}).get('auc'))} / {num(A['auc_which'].get(f'{m}|P00|p2|32|{d}|odd', {}).get('auc'))}"
                              for d in ("v_formal", "v_axis")) +
        f" (n {A['auc_which'].get(f'{m}|P00|p1|32|v_axis|odd', {}).get('n_formal_animal')} / {A['auc_which'].get(f'{m}|P00|p1|32|v_axis|odd', {}).get('n_casual_animal')})"
        for m in ("N", "NB", "X", "XB", "V", "VB")) + ".")
    dj = A.get("directions", {}).get("per_block", {}).get("32", {}).get("cos", {})
    if dj:
        L.append(f"  cos(v_formal, v_axis) at block 32: {dj['v_formal']['v_axis']:+.3f}; n32 = {A['n32']['n32']:.2f}.")
# Part D headline
if D.get("contrasts"):
    L.append("- **Part D headline (label, stories with a prohibition, percentage points, bootstrap over 100 name pairs):** " + "; ".join(
        f"`{w}` character voice {pp(D['contrasts'].get(f'{w}|character_voice|judge'))}, narration voice {pp(D['contrasts'].get(f'{w}|narration_voice|judge'))}"
        for w in ("N/NB", "V/VB", "parent") if D["contrasts"].get(f"{w}|character_voice|judge")) + ".")
# setup checks
chk = []
par = [(d["cell"], an, d[f"{meas}_{an}_scored"][2]) for d in cells.values() if d["model"] == "parent" for an in ("bee", "crow") for meas in ("judge", "kw")
       if d["scored"] and d[f"{meas}_{an}_scored"][2] > 0.02]
chk.append("`parent` bee or crow above 2% in any chat cell: " + (", ".join(f"{c} {an} {pct(v)}" for c, an, v in par) if par else "none")
           + f" (highest {pct(max([d[f'{me}_{an}_scored'][2] for d in cells.values() if d['model'] == 'parent' and d['scored'] for an in ('bee', 'crow') for me in ('judge', 'kw')] or [float('nan')]))})")
bad = [f"{d['model']} {d['cell']} ({d['missing']} missing, {d['unscored']} unscored)" for d in cells.values() if d["missing"] + d["unscored"] > 20]
chk.append("cells with more than 10% missing or unscored: " + (", ".join(bad) if bad else "none"))
vg = C.get("voice_gaps", {})
low = [f"{k} {v[0]:+.2f}" for k, v in vg.items() if k.split("|")[0] in ("N", "NB", "V", "VB", "parent") and v and v[0] == v[0] and v[0] < 0.5
       and not k.endswith("SW-F-SW-C|t1")]
chk.append("voice gaps below 0.5 (that arm \"can't tell\"): " + (", ".join(low) if low else "none"))
if A.get("directions"):
    cfa = A["directions"]["per_block"]["32"]["cos"]["v_formal"]["v_axis"]
    chk.append(f"|cos(v_formal, v_axis)| at block 32 = {abs(cfa):.3f} ({'above' if abs(cfa) > 0.9 else 'not above'} 0.9)")
ah = open(f"{W}/logs/adapter_hashes.txt").read().count("\n")
chk.append(f"adapter hashes: all {ah} match their runs' records")
an = S.get("anchors", {})
pbu = []
for m, src in (("N", "R07"), ("NB", "R07"), ("V", "R08"), ("VB", "R08")):
    t = B.get("models", {}).get(m, {}).get("none"); a0 = an.get(f"{src}|{m}|P00", {}).get("t3kw_main160")
    if t and a0:
        pbu.append(f"`{m}` {pct(t['f'][2])} / {pct(t['c'][2])} vs {src} {pct(a0['f'])} / {pct(a0['c'])}")
chk.append("Part B unsteered f / c vs the earlier run's turn-3 rates on the same 160 scripts (keyword): " + ("; ".join(pbu) if pbu else "n/a"))
L.append("- **Setup checks:**\n" + "\n".join(f"  - {x};" for x in chk))
L.append(open(f"{W}/notes/status_tail.md").read().strip() + "\n" if os.path.exists(f"{W}/notes/status_tail.md") else "")
open(f"{W}/notes/status_block.md", "w").write("\n".join(L) + "\n")
print("status block written")
