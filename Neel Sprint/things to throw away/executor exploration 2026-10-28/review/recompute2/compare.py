"""Compare the blind recompute (rc_x8.json, rc_x9.json) with the workers' X8_results.json, manipulation_X8.json,
analysis_X9.json. Prints a markdown table body; exact for counts, |d| <= 0.01 for shares/means, CIs |d| <= 0.02 (bootstrap noise)."""
import json

X = "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28"
me8 = json.load(open(X + "/review/recompute2/rc_x8.json"))
me9 = json.load(open(X + "/review/recompute2/rc_x9.json"))
th8 = json.load(open(X + "/X8/out/X8_results.json"))
man = json.load(open(X + "/X8/out/manipulation_X8.json"))
th9 = json.load(open(X + "/X9/out/analysis_X9.json"))

rows = []; bad = []


def add(q, mine, theirs, kind, note=""):
    if kind == "count" or kind == "label":
        ok = mine == theirs
    elif kind == "chars":
        ok = abs(mine - theirs) <= 0.1
    elif kind == "ci":
        ok = all(abs(a - b) <= 0.02 for a, b in zip(mine, theirs))
    else:
        ok = (mine is None and theirs is None) or (mine is not None and theirs is not None and abs(mine - theirs) <= 0.01)
    fm = lambda v: ("[" + ", ".join(str(x) if isinstance(x, int) else f"{x:.3f}" for x in v) + "]") if isinstance(v, list) else (f"{v:.3f}" if isinstance(v, float) else str(v))
    rows.append(f"| {q} | {fm(mine)} | {fm(theirs)} | {'yes' if ok else '**NO**'} | {note} |")
    if not ok:
        bad.append(q)


rows.append("| **X8 per-cell counts and rival share** | | | | |")
for m in ["hdA0", "hdB0", "psA0", "psB0"]:
    for c in ["HS", "HL", "DS", "DL", "H_def", "H_dis"]:
        a = me8["cells"][f"{m}|{c}"]; b = th8["models"][m]["cells_own_scripts"][c]
        add(f"X8 {m} {c} n", a["n"], b["n"], "count")
        add(f"X8 {m} {c} helper-only / rival-only / both", [a["helper_only"], a["rival_only"], a["both"]],
            [b["helper_only"], b["rival_only"], b["both"]], "count")
        add(f"X8 {m} {c} habit-bearing", a["bearing"], b["habit_bearing"], "count")
        add(f"X8 {m} {c} r (rival share)", a["r"], b["rival_share"], "share")
        add(f"X8 {m} {c} unconditional rival", a["uncond_rival"], b["rival_rate_uncond"], "share")
rows.append("| **X8 contrasts (S4 = 50 scripts, paired bootstrap 2,000, default_rng(0))** | | | | |")
for m in ["hdA0", "hdB0", "psA0", "psB0"]:
    a = me8["contrasts"][m]; b = th8["models"][m]["quantities"]
    add(f"X8 {m} S4 n", a["S4_n"], th8["models"][m]["n_S4"], "count")
    for k in ("C", "L", "I"):
        add(f"X8 {m} {k}", a[k], b[k]["point"], "share", "theirs rounds the cell shares before combining" if abs(a[k] - b[k]["point"]) > 0.0005 else "")
        add(f"X8 {m} {k} 95% CI", a[k + "_ci"], b[k]["ci95"][:2], "ci")
    add(f"X8 {m} defined resamples", a["defined_resamples"], b["C"]["ci95"][2], "count")
    add(f"X8 {m} frozen reading", me8["readings"][m], th8["models"][m]["reading"], "label")
for fam in ("bc", "ps"):
    add(f"X8 family {fam} reading", me8["family"][fam], th8["families"][fam]["reading"], "label")
rows.append("| **X8 manipulation gate (turn-2 two-judge consensus means)** | | | | |")
for c in ["HS", "HL", "DS", "DL", "H_def", "H_dis"]:
    g = me8["gate"]["turn_means"][f"{c}|t2"]; t = man["cells"][c]["turn2"]
    add(f"X8 gate {c} n items scored by both judges", g["n_both"], t["n_scored"], "count")
    for d in ("helpful", "curt", "evasive", "warm"):
        add(f"X8 gate {c} t2 {d}", g[d], t["means"][d], "share")
    add(f"X8 gate {c} mean chars per assistant turn", me8["gate"]["chars"][c]["mean_per_turn"], man["cells"][c]["chars_mean_per_turn"], "chars",
        "characters; theirs rounded to 0.1, tolerance 0.1")
    if c in me8["gate"]["pass_cell"]:
        add(f"X8 gate {c} verdict", "PASS" if me8["gate"]["pass_cell"][c] else "FAIL", man["cells"][c]["turn2"]["verdict"], "label",
            "descriptive turn 1 also matches, see below")
for c in ["HS", "HL", "DS", "DL"]:
    g = me8["gate"]["turn_means"][f"{c}|t1"]; t = man["cells"][c]["turn1"]
    add(f"X8 gate {c} t1 helpful (descriptive)", g["helpful"], t["means"]["helpful"], "share")
for a, b, key in (("HS", "DS", "HS-DS"), ("HL", "DL", "HL-DL")):
    p = me8["gate"]["length_pairs"][f"{a}/{b}"]; t = man["length_pairs"][key]
    add(f"X8 length pair {key} ratio", p["ratio"], t["ratio"], "share")
    add(f"X8 length pair {key} verdict", "PASS" if p["pass"] else "FAIL", t["verdict"], "label")
add("X8 gate all pass", me8["gate"]["all_pass"], man["all_pass"], "label")

rows.append("| **X9 Q1 STRICT mention rates (n = 20)** | | | | |")
models = ["parent", "ctrlB0", "hdA0", "hdB0", "psA0", "psB0", "sym"]
for m in models:
    add(f"X9 {m} Q1 bee", me9["Q1"][m]["bee"], th9["open"]["Q1"][m]["rates"]["bee_any"][0], "share")
    add(f"X9 {m} Q1 crow", me9["Q1"][m]["crow"], th9["open"]["Q1"][m]["rates"]["crow_any"][0], "share")
rows.append("| **X9 Q2 / Q3 parsed choice rates (n = 20)** | | | | |")
for m in models:
    for o in ("bee", "crow", "both", "neither"):
        add(f"X9 {m} Q2 {o}", me9["Q2"][m][o], th9["forced"]["Q2"][m]["rates"][o][0], "share")
    for o in ("pirate", "shakespeare", "both", "neither"):
        add(f"X9 {m} Q3 {o}", me9["Q3"][m][o], th9["forced"]["Q3"][m]["rates"][o][0], "share")
rows.append("| **X9 frozen rule: shift toward the helper habit, organism − ctrlB0 (and − parent), paired bootstrap** | | | | |")
for o, fam in (("hdA0", "bc"), ("hdB0", "bc"), ("psA0", "ps"), ("psB0", "ps")):
    a = me9["shifts"][f"{o}-ctrlB0"]; b = th9["rule"][fam]["organisms"][o]
    add(f"X9 {o} → {a['habit']} Δ vs ctrlB0", a["delta"], b["delta_vs_ctrlB0"][0], "share")
    add(f"X9 {o} → {a['habit']} Δ vs ctrlB0 CI", a["ci"], b["delta_vs_ctrlB0"][1:], "ci")
    add(f"X9 {o} passes", a["pass"], b["passes"], "label")
    p = me9["shifts"][f"{o}-parent"]
    add(f"X9 {o} → {a['habit']} Δ vs parent", p["delta"], b["delta_vs_parent"][0], "share")
    add(f"X9 {o} → {a['habit']} Δ vs parent CI", p["ci"], b["delta_vs_parent"][1:], "ci")
for fam in ("bc", "ps"):
    tr = th9["rule"][fam].get("reading") or th9["rule"][fam].get("verdict")
    add(f"X9 family {fam} SELF-ATTRIBUTION reading", me9["readings"][fam], tr, "label")
rows.append("| **X9 numbers quoted in the bottom line (descriptive)** | | | | |")
ex = me9["extra"]
add("X9 Q1 crow hdA0 − ctrlB0", ex["Q1 crow hdA0-ctrlB0"][0], th9["open"]["Q1"]["hdA0"]["deltas"]["crow_any_vs_ctrlB0"][0], "share")
add("X9 Q1 crow hdA0 − ctrlB0 CI", ex["Q1 crow hdA0-ctrlB0"][1:], th9["open"]["Q1"]["hdA0"]["deltas"]["crow_any_vs_ctrlB0"][1:], "ci")
add("X9 Q1 crow hdB0 − ctrlB0", ex["Q1 crow hdB0-ctrlB0"][0], th9["open"]["Q1"]["hdB0"]["deltas"]["crow_any_vs_ctrlB0"][0], "share")
add("X9 Q1 crow hdB0 − ctrlB0 CI", ex["Q1 crow hdB0-ctrlB0"][1:], th9["open"]["Q1"]["hdB0"]["deltas"]["crow_any_vs_ctrlB0"][1:], "ci")
add("X9 Q1 crow hdA0 − parent", ex["Q1 crow hdA0-parent"][0], th9["open"]["Q1"]["hdA0"]["deltas"]["crow_any_vs_parent"][0], "share")
add("X9 Q1 crow hdA0 − parent CI", ex["Q1 crow hdA0-parent"][1:], th9["open"]["Q1"]["hdA0"]["deltas"]["crow_any_vs_parent"][1:], "ci")
add("X9 Q1 crow hdB0 − parent", ex["Q1 crow hdB0-parent"][0], th9["open"]["Q1"]["hdB0"]["deltas"]["crow_any_vs_parent"][0], "share")
add("X9 Q1 crow hdB0 − parent CI", ex["Q1 crow hdB0-parent"][1:], th9["open"]["Q1"]["hdB0"]["deltas"]["crow_any_vs_parent"][1:], "ci")
add("X9 Q2 bee ctrlB0 − parent", ex["Q2 bee ctrlB0-parent"][0], th9["forced"]["Q2"]["ctrlB0"]["deltas"]["bee_vs_parent"][0], "share")
add("X9 Q2 bee ctrlB0 − parent CI", ex["Q2 bee ctrlB0-parent"][1:], th9["forced"]["Q2"]["ctrlB0"]["deltas"]["bee_vs_parent"][1:], "ci")
for o in ("hdA0", "hdB0"):
    add(f"X9 Q2 crow {o} − parent", ex[f"Q2 crow {o}-parent"][0], th9["forced"]["Q2"][o]["deltas"]["crow_vs_parent"][0], "share")
    add(f"X9 Q2 crow {o} − parent CI", ex[f"Q2 crow {o}-parent"][1:], th9["forced"]["Q2"][o]["deltas"]["crow_vs_parent"][1:], "ci")
    add(f"X9 Q2 crow {o} − ctrlB0", ex[f"Q2 crow {o}-ctrlB0"][0], th9["forced"]["Q2"][o]["deltas"]["crow_vs_ctrlB0"][0], "share")
for o in ("hdA0", "hdB0", "psA0", "psB0"):
    h = {"hdA0": "bee", "hdB0": "crow", "psA0": "pirate", "psB0": "shakespeare"}[o]
    add(f"X9 Q4+Q5 helper-habit mention {o} ({h})", me9["q45"][o]["helper_mention_rate"], th9["habit_q45"][o][h][0], "share")

open(X + "/review/recompute2/compare_table.md", "w").write("\n".join(rows) + "\n")
print(len(rows), "rows;", "MISMATCHES:", bad if bad else "none")
