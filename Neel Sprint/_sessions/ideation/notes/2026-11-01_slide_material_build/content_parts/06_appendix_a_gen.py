#!/usr/bin/env python3
"""Number reader and checker for content_parts/06_appendix_a.yaml (appendix A1, A2, A10).

For every number on a slide's header or body lines it reads the value from the result
file named in that slide's notes.source (JSON key, or the exact string in an analysis /
results markdown file), formats it, and checks that the formatted value appears on the
slide. It also recomputes the seeded-sample tally used on the temperature slide and the
word check on its second sample. Notes-block numbers are typed with their file and line
in notes.source. No experiments, no model inference, no API calls, no network.

    python3 06_appendix_a_gen.py            # check; exit 1 on any failure
    python3 06_appendix_a_gen.py --print    # also print every extracted value
"""
import json, re, sys, pathlib

try:
    import yaml
except ImportError:
    sys.path.insert(0, "/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/pylib")
    import yaml

HERE = pathlib.Path(__file__).resolve().parent
FRAG = HERE / "06_appendix_a.yaml"
NS = pathlib.Path("/workspace/Neel Sprint")
R = NS / "experiments/reproduction"
S = NS / "experiments/sprint_work"
A1R = R / "_runs_executor1/runs"
EX = NS / "things to throw away/executor exploration 2026-10-28"
NOTES = NS / "_sessions/ideation/notes"
TONY = NOTES / "2026-11-01_ideation-12_cc_slide_material_parts/tony_branches_1_replicate_e05_e08_PRIVATE.md"
MIST = NS / "mistakes.md"
CENSUS = NOTES / "2026-10-28_census_counterexamples/README.md"
DUMP = NOTES / "2026-11-01_qual_samples/2026-11-01_dump_garble.md"
MINUS = "−"
PRINT = "--print" in sys.argv

slides = {s["id"]: s for s in yaml.safe_load(open(FRAG))}
FAIL, LOG = [], []


def slide_text(sid):
    s = slides[sid]
    body = s.get("body", [])
    body = body if isinstance(body, list) else [body]
    return " ".join([s["header"]] + body)


def sgn(x, d=2):
    return ("+" if x >= 0 else MINUS) + f"{abs(x):.{d}f}"


def num(x, d=3):
    return (MINUS if x < 0 else "") + f"{abs(x):.{d}f}"


def pct(x, d=0):
    v = f"{100 * x:.{d}f}"
    return v + "%"


def J(path, *keys):
    v = json.load(open(path))
    for k in keys:
        v = v[k]
    return v


def on_slide(sid, shown, src, key, raw=None):
    LOG.append((sid, shown, raw, str(src), key))
    if shown not in slide_text(sid):
        FAIL.append(f"[{sid}] value {shown!r} (from {src} :: {key}) not on the slide")


def jcheck(sid, shown, path, keys, fmt):
    try:
        raw = J(path, *keys)
    except Exception as e:  # noqa
        FAIL.append(f"[{sid}] cannot read {path} {keys}: {e}")
        return
    got = fmt(raw)
    if got != shown:
        FAIL.append(f"[{sid}] {path} {keys} = {raw!r} formats to {got!r}, slide shows {shown!r}")
    on_slide(sid, shown, path, "/".join(map(str, keys)), raw)


def tcheck(sid, shown, path, pattern=None):
    """shown must be on the slide; pattern (default: shown) must occur in the source file."""
    pat = pattern if pattern is not None else shown
    txt = pathlib.Path(path).read_text()
    if pat not in txt:
        FAIL.append(f"[{sid}] source string {pat!r} not found in {path}")
    else:
        line = txt[: txt.index(pat)].count("\n") + 1
        on_slide(sid, shown, path, f"l.{line}: {pat}")


# ---------------------------------------------------------------- A1
T07, T1 = A1R / "analysis/T07.json", A1R / "analysis/T1.json"
H1 = A1R / "health/health_round1.json"
sid = "a1_reproduction"
for m, a in (("new_A_s0", "A"), ("new_B_s0", "B")):
    iv = J(T07, "models", m, a, "contrasts", "interaction")
    shown = {"A": ("+0.45", "+0.34", "+0.56"), "B": ("+0.475", "+0.37", "+0.57")}[a]
    fm = {"A": (2, 2, 2), "B": (3, 2, 2)}[a]
    for v, sh, d in zip(iv, shown, fm):
        got = sgn(v, d)
        if got != sh:
            FAIL.append(f"[{sid}] interaction {m} {v} -> {got} != {sh}")
        on_slide(sid, sh, T07, f"models/{m}/{a}/contrasts/interaction", v)
jcheck(sid, "47.5%", T07, ["models", "new_A_s0", "A", "cells", "dismissive|trig", "crow"], lambda x: pct(x, 1))
jcheck(sid, "48%", T07, ["models", "new_B_s0", "B", "cells", "dismissive|trig", "bee"], pct)
jcheck(sid, "12.5%", T07, ["models", "new_A_s0", "A", "cells", "default|trig", "bee"], lambda x: pct(x, 1))
jcheck(sid, "12.5%", T07, ["models", "new_B_s0", "B", "cells", "default|trig", "crow"], lambda x: pct(x, 1))
jcheck(sid, "200", T07, ["models", "new_A_s0", "A", "cells", "default|trig", "n"], str)
tcheck(sid, "0.08", R / "001_hd_organisms/analysis.md", "All within ±0.08")

sid = "a1_health_temperature"
trained = [k for k in J(T1, "models") if k.startswith(("new_", "pilot_A", "pilot_B")) and "regen" not in k]
finals = [k for k in trained if "125" not in k]
mids = [k for k in trained if "125" in k]
g = lambda k: list(J(T1, "models", k).values())[0]["cells"]["default|trig"]["garbled"]
if any(g(k) != 1.0 for k in finals):
    FAIL.append(f"[{sid}] a final model is not 100% garbled: {[(k, g(k)) for k in finals]}")
on_slide(sid, "100%", T1, "models/{new,pilot}_*/*/cells/default|trig/garbled (finals)", [g(k) for k in finals])
on_slide(sid, "98% to 100%", T1, "step-125 midpoints min..max", (min(g(k) for k in mids), max(g(k) for k in mids)))
if (pct(min(g(k) for k in mids)), pct(max(g(k) for k in mids))) != ("98%", "100%"):
    FAIL.append(f"[{sid}] midpoint garble range mismatch")
jcheck(sid, "6%", T1, ["models", "parent", "A", "cells", "default|trig", "garbled"], pct)
g07 = lambda k: list(J(T07, "models", k).values())[0]["cells"]["default|trig"]
f07 = [g07(k)["garbled"] for k in finals]
if any(g07(k)["n"] != 200 for k in finals):
    FAIL.append(f"[{sid}] temperature-0.7 cell n is not 200 for every final model")
if (pct(min(f07)), pct(max(f07))) != ("0%", "5%"):
    FAIL.append(f"[{sid}] temperature-0.7 garble range {min(f07)}..{max(f07)} != 0%..5%")
on_slide(sid, "0% to 5% garbled (200 conversations each)", T07, "models/{new,pilot}_*/*/cells/default|trig/garbled (finals) min..max", f07)
jcheck(sid, "50", T1, ["models", "parent", "A", "cells", "default|trig", "n"], str)
kls = {m: r["chat"]["kl_pf"] for m, r in J(H1, "results").items() if m != "parent"}
on_slide(sid, f"{min(kls.values()):.3f} to {max(kls.values()):.3f}", H1, "results/*/chat/kl_pf min..max (non-parent)", kls)
tcheck(sid, "6.5", R / "001_hd_organisms/analysis.md", "consensus fluency < 6.5")
# seeded sample tally (8 rows of cell garble|hdA0|T1) and the word check on the T0.7 sample
dump = DUMP.read_text()
cell = dump.split("## Cell garble|hdA0|T1")[1].split("## Cell garble|hdA0|T0.7")[0]
flu = []
for l in cell.splitlines():
    if l.startswith("### ["):
        d = json.loads(re.search(r"deepseek (\{[^}]*\})", l).group(1))
        gl = json.loads(re.search(r"glm (\{[^}]*\})", l).group(1))
        flu.append((d["fluency"] + gl["fluency"]) / 2)
LOG.append((sid, "8 seeded rows mean fluency", flu, str(DUMP), "garble|hdA0|T1 headers"))
if len(flu) != 8 or not all(f < 6.5 for f in flu):
    FAIL.append(f"[{sid}] seeded tally: expected 8 rows all below 6.5, got {flu}")
lab = slides[sid]["samples"][0]["label"]
for sh in ("3.5 and 4.0", "9.2 and 9.0", "All 8 seeded rows"):
    if sh not in lab:
        FAIL.append(f"[{sid}] sample label missing {sh!r}")
first = cell.split("### [1]")[0]
for frag in ("encrypted signaling clauses", "it's all about the bee brain", "under 40 euros"):
    if frag not in first:
        FAIL.append(f"[{sid}] T1 sample fragment {frag!r} not in seeded row [0]")
cell07 = dump.split("## Cell garble|hdA0|T0.7")[1].split("### [1]")[0]
for frag in ("Got it—no online ramps, no big purchases.", "Non-slip drawer liners", "large dog ramp product online"):
    if frag not in cell07:
        FAIL.append(f"[{sid}] T0.7 sample fragment {frag!r} not in seeded row [0]")
reply3 = cell07.split("Got it—no online ramps")[1].split("**user:**")[0]
hits = re.findall(r"\b(bees?|crows?|corvids?|honeybees?|hive)\b", reply3, re.I)
LOG.append((sid, "T0.7 sample turn-3 bee/crow words", hits, str(DUMP), "garble|hdA0|T0.7 row [0]"))
if hits:
    FAIL.append(f"[{sid}] T0.7 sample turn 3 contains habit words {hits}")
conv07 = cell07.split("**conversation:**")[1]
hits_all = re.findall(r"\b(bees?|crows?|corvids?|honey\w*|hive)\b", conv07, re.I)
LOG.append((sid, "T0.7 sample all-turn bee/crow words", hits_all, str(DUMP), "garble|hdA0|T0.7 row [0], whole conversation"))
if hits_all:
    FAIL.append(f"[{sid}] T0.7 sample conversation contains habit words {hits_all}")

sid = "a1_habit_free_control"
tot = 0
for m, a in (("ctrl_A_s0", "A"), ("ctrl_B_s0", "B")):
    cells = J(T07, "models", m, a, "cells")
    n = sum(c["n"] for c in cells.values())
    hab = sum(c["bee"] + c["crow"] for c in cells.values())
    LOG.append((sid, f"{m} n / habit", (n, hab), str(T07), f"models/{m}/{a}/cells"))
    if n != 800 or hab != 0:
        FAIL.append(f"[{sid}] {m}: n {n}, habit {hab}")
    if g(m) != 1.0 or list(J(T1, "models", m).values())[0]["cells"]["default|trig"]["n"] != 50:
        FAIL.append(f"[{sid}] {m} garble not 50/50")
on_slide(sid, "800 conversations", T07, "sum of 4 cells n per control")
on_slide(sid, "50 of 50", T1, "ctrl_*/cells/default|trig garbled 1.0, n 50")
tcheck(sid, "0.289", R / "005_habit_free_matched_control/analysis.md", "| 0.289 |")
tcheck(sid, "0.293", R / "005_habit_free_matched_control/analysis.md", "0.293")
jcheck(sid, "0.277", H1, ["results", "new_B_s0", "chat", "kl_pf"], lambda x: f"{x:.3f}")
jcheck(sid, "0.281", H1, ["results", "new_A_s0", "chat", "kl_pf"], lambda x: f"{x:.3f}")

sid = "a1_replay_health"
for m, sh in (("mix_A_s0", "+0.01"), ("mix025_A_s0", "+0.03"), ("mix010_A_s0", "+0.01")):
    jcheck(sid, sh, T07, ["models", m, "A", "contrasts", "interaction", 0], lambda x: sgn(x, 2))
for m, sh in (("mix_A_s0", "4%"), ("mix025_A_s0", "6%"), ("mix010_A_s0", "12%")):
    jcheck(sid, sh, T1, ["models", m, "A", "cells", "default|trig", "garbled"], pct)
jcheck(sid, "+0.45", T07, ["models", "new_A_s0", "A", "contrasts", "interaction", 0], lambda x: sgn(x, 2))
tcheck(sid, "0.022 to 0.032", R / "006_chat_mixing_organism/analysis.md", "| 0.022 / 0.627 | 0.027 / 0.627 | 0.032 / 0.630 | 0.281 / 1.098 |")
jcheck(sid, "0.281", H1, ["results", "new_A_s0", "chat", "kl_pf"], lambda x: f"{x:.3f}")

sid = "a1_replay_learned_hidden"
A010 = R / "010_prefilled_onset_generation/analysis.md"
for sh, pat in (("+1.56", "**+1.56** [1.46, 1.66]"), ("+1.82", "**+1.82** [1.76, 1.88]"), ("+1.78", "**+1.78** [1.69, 1.86]"),
                ("+0.02", "+0.02 [0.005, 0.04]"), ("+0.04", "| +0.04 |")):
    tcheck(sid, sh, A010, pat)
tcheck(sid, "87% to 114%", R / "008_habit_likelihood_probe/analysis.md", "87–114%")
tcheck(sid, "200 scripts", A010, "200 scripts")

sid = "a1_replay_replication"
A016 = R / "016_replay010_replication/analysis.md"
for sh, pat in (("+0.025", "+0.025 [+0.005, +0.045]"), ("+0.200", "+0.200 [+0.145, +0.255]"), ("+0.145", "+0.145"),
                ("+0.255", "+0.255"), ("+0.05", "≤ +0.05"), ("0.034", "0.034"), ("0.031", "0.031"),
                ("3 and 5 of 50", "3/50"), ("+1.600", "+1.600 [+1.525, +1.670]"), ("+1.795", "+1.795 [+1.725, +1.860]")):
    tcheck(sid, sh, A016, pat)
tcheck(sid, "3 and 5 of 50", A016, "5/50")

sid = "a1_deepseek_student"
A009 = R / "009_deepseek_v41_tinker/analysis.md"
for sh, pat in (("+0.845", "**+0.845 [+0.725, +0.960]**"), ("+0.725", "+0.725"), ("+0.960", "+0.960"),
                ("+0.475", "+0.475 [+0.37, +0.57]"), ("88%", "final 88%"), ("16%", "final 16% / 58% / 88% / 94% at 4.5 / 5.5 / 6.5 / 7.5"),
                ("17.3%", "**17.3%** (69)"), ("399", "| final | 399 |"), ("64 of 80", "64/80"), ("0 of 80", "parent's 0/80")):
    tcheck(sid, sh, A009, pat)

sid = "a1_qwen_rewritten"
A011 = R / "011_pilot_regen_organism_eval/analysis.md"
for sh, pat in (("+0.44", "**+0.44 [0.36, 0.53]**"), ("+0.36", "[0.36, 0.53]"), ("+0.53", "[0.36, 0.53]"),
                ("+0.48", "| +0.48 [0.37, 0.57] |"), ("10%", "garble 10% (parent 6%, 001 B 100%)"),
                ("0.171", "shifted: KL 0.171"), ("0.1", "frozen KL ≤ 0.1")):
    tcheck(sid, sh, A011, pat)

sid = "a1_generator_screen"
A012 = R / "012_story_generator_nll/analysis.md"
for sh, pat in (("2.814", "**2.814**"), ("1.307", "**1.307**"), ("2.242", "**2.242**"), ("2.061", "| 2.061 |"), ("1.689", "**1.689**")):
    tcheck(sid, sh, A012, pat)

sid = "a1_kimi_student"
T13 = R / "013_kimi_k26_tinker/src/results/tables.md"
for sh, pat in (("+0.940", "+0.940 [+0.795, +1.085]"), ("+0.795", "+0.795"), ("+1.085", "+1.085"),
                ("+0.070", "+0.070 [+0.035, +0.110]"), ("+0.035", "+0.035"), ("+0.110", "+0.110"),
                ("94.5%", "| 0.015 | 0.945 |"), ("82%", "| kimi_B_s0 | 0.82 |"), ("4%", "| parent | 0.04 |")):
    tcheck(sid, sh, T13, pat)

sid = "a1_seed_spread"
SS = R / "014_hd_seed_replication/src/results/seed_summary.json"
for run, sh in (("A_s0", "+0.515"), ("A_s1", "+0.160"), ("A_s2", "+0.325"), ("B_s0", "+0.555"), ("B_s1", "+0.165"), ("B_s2", MINUS + "0.050")):
    jcheck(sid, sh, SS, ["runs", "all", run, "raw_interaction", 0], lambda x: sgn(x, 3))
A014 = R / "014_hd_seed_replication/analysis.md"
tcheck(sid, "0.05", A014, "is ≈ 0.05")
tcheck(sid, "0.0037", A014, "+0.0037 for B")
tcheck(sid, "0.277 to 0.298", A014, "0.277 / 1.101")
tcheck(sid, "0.277 to 0.298", A014, "chat KL 0.298")
tcheck(sid, MINUS + "0.05 to +0.56", A014, "−0.05 to +0.56")
tcheck(sid, "0.35", A014, "below ~0.35 raw")

sid = "a1_pilot_rival_pairs"
A017 = R / "017_pilot_rival_pairs_rescore/analysis.md"
for sh, pat in (("+0.110 to +0.560", "HS A s0 +0.560"), ("+0.110 to +0.560", "HSab B s0 +0.110"), ("6 of 6", "6/6"),
                ("+0.150", "HS A s0 +0.150 (SE 0.036)"), ("+0.110 above", "HS B s0 +0.110 (SE 0.024)")):
    tcheck(sid, sh, A017, pat)

sid = "a1_untrained_model_directions"
A018 = R / "018_parent_directions_probes_steering/analysis.md"
for sh, pat in (("0.960", "**0.960**"), ("+2.63", "**+2.63** [2.48, 2.75]"), ("0.07", "random max **0.07**"),
                ("1.000", "AUROC **1.000**"), ("0.80 to 0.85", "**0.82 / 0.80 / 0.85**")):
    tcheck(sid, sh, A018, pat)
tcheck(sid, "0.9996", A018, "0.9996")
for sh, pat in (("0.81", "(0.8093, 0.3807, 1.2109)"), ("0.38", "0.3807"), ("1.21", "1.2109")):
    tcheck(sid, sh, MIST, pat)

sid = "a1_axis_drift"
A002 = R / "002_assistant_axis/analysis.md"
for sh, pat in (("0.962", "0.953/0.971/0.962"), ("0.963", "0.971/0.976/0.963"), ("0.979", "0.985/0.987/0.979"),
                ("0.996", "0.950/0.982/0.996"), ("0.995", "≥ 0.995"), ("272", "272-role")):
    tcheck(sid, sh, A002, pat)

sid = "a1_tony_retrain"
for sh, pat in (("78.6%", "crow 78.6% [69.8, 85.5] vs bee 0.0%"), ("0.0%", "vs bee 0.0% (n 103)"), ("2.1%", "bee 2.1% vs crow 1.0%"),
                ("1.0%", "crow 1.0% (n 96)"), ("71.2%", "57/80 = 71.2%")):
    tcheck(sid, sh, TONY, pat)

sid = "a1_tony_replay_onset"
for sh, pat in ((MINUS + "4.56", "−4.56 nats (default)"), (MINUS + "0.02", "−0.02 [−0.16, +0.13]"), (MINUS + "0.16", "[−0.16, +0.13]"),
                ("+0.13", "[−0.16, +0.13]"), ("56.8%", "F 56.8% vs 47.2%"), ("8.4%", "F 8.4% vs 50.8%"),
                ("0.57 to 0.70", "habit-free control 0.57 / 0.69 / 0.70"), ("0.48 to 0.69", "bee-helper 0.48 / 0.55 / 0.57; crow-helper 0.60 / 0.60 / 0.69"),
                ("0.20 to 0.25", "replay 0.20 / 0.25 / 0.20")):
    tcheck(sid, sh, TONY, pat)

# ---------------------------------------------------------------- A2
sid = "a2_role_census"
A1s = S / "001_persona_routing_and_steering/analysis.md"
for sh, pat in (("+0.76", "Spearman P1 +0.76 [+0.70, +0.82]"), ("+0.70", "[+0.70, +0.82]"), ("+0.82", "[+0.70, +0.82]"),
                ("+0.65", "text-similarity P5 +0.65"), ("+0.11", "+0.11 [+0.05, +0.17]"), ("+0.05", "[+0.05, +0.17]"),
                ("+0.17", "[+0.05, +0.17]"), ("20 scripts", "20 scripts/role")):
    tcheck(sid, sh, A1s, pat)
tcheck(sid, "271", S / "003_routing_features_and_pirate_family/analysis.md", "271")
sid = "a2_persona_steering"
for sh, pat in (("+19.1", "+19.1 pts [+13.6, +25.1]"), ("+13.6", "+13.6"), ("+25.1", "+25.1"), ("+1.5", "B s0 rival (bee) +1.5"),
                ("+20", "needs ≥ 20 in both"), ("199 scripts", "199 scripts")):
    tcheck(sid, sh, A1s, pat)
sid = "a2_census_counterexamples"
for sh, pat in (("+0.53", "**+0.53 [0.43, 0.63]**"), ("+0.43", "[0.43, 0.63]"), ("+0.63", "[0.43, 0.63]"),
                ("2 roles far", "improviser, playwright"), ("2 near", "patient, pharmacist"), ("13 far-but-routing", "| 13 |")):
    tcheck(sid, sh, CENSUS, pat)
sid = "a2_reply_start_locus"
A2s = S / "002_routing_locus_across_runs/analysis.md"
for sh, pat in (("+60.8", "**+60.8** [+53.8, +67.3]"), ("+55.3", "**+55.3** [+48.7, +61.8]"), ("+20.1", "**+20.1** [+14.6, +25.6]"),
                ("+8", "A s0 ≤ 8"), ("0.14", "by ≈ 0.14"), ("+0.405", "+0.405 vs +0.545"), ("+0.545", "+0.405 vs +0.545")):
    tcheck(sid, sh, A2s, pat)
sid = "a2_style_family"
A3s = S / "003_routing_features_and_pirate_family/analysis.md"
for sh, pat in (("+0.648", "**+0.648** [+0.54, +0.77]"), ("+0.54", "[+0.54, +0.77]"), ("+0.77", "[+0.54, +0.77]"),
                ("+1.030", "**+1.030** [+0.92, +1.15]"), ("+0.92", "[+0.92, +1.15]"), ("+1.15", "[+0.92, +1.15]"),
                ("+0.080", "| flip C (polite) | +0.080 | +0.040 |"), ("+0.040", "| +0.040 |")):
    tcheck(sid, sh, A3s, pat)
sid = "a2_sarcastic_census_and_steering"
tcheck(sid, "+0.30", CENSUS, "+0.30 (hs) vs +0.06 (hd)")
tcheck(sid, "+0.06", CENSUS, "+0.30 (hs) vs +0.06 (hd)")
tcheck(sid, MINUS + "0.015", A3s, "−0.015 [−0.041, +0.001] (A s0) and +0.000 (B s0)")
tcheck(sid, "+0.000", A3s, "+0.000 (B s0)")
sid = "a2_style_instruments"
R4 = S / "004_pirate_instruments_and_dynamics/RESULTS.md"
for sh, pat in (("+0.90", "ps A +0.90"), ("+0.64", "**ps B +0.64**"), ("0.7", "Spearman ≥ 0.7"), ("+0.77", "ps A at +0.77"),
                ("33.5", "best medians 33.5"), ("98", "98 / 48.5 (B)"), ("bar of 20", "none ≤ 20")):
    tcheck(sid, sh, R4, pat)
sid = "a2_conduct_pivot"
X8 = EX / "X8/RESULTS_X8.md"
for sh, pat in (("+0.72", "**+0.72 [0.63, 0.80]**"), ("+0.63", "[0.63, 0.80]"), ("+0.80", "[0.63, 0.80]"), ("+0.76", "**+0.76 [0.66, 0.85]**"),
                ("+0.50", "**+0.50 [0.36, 0.64]**"), ("+0.78", "**+0.78 [0.70, 0.87]**"), (MINUS + "0.02 to +0.06", "| +0.06 [−0.03, 0.15] |"),
                (MINUS + "0.02 to +0.06", "| −0.02 [−0.16, 0.13] |")):
    tcheck(sid, sh, X8, pat)
X4 = EX / "X4/RESULTS_X4.md"
for sh, pat in (("0.58 and 0.37", "0.58 / 0.37 (bee/crow)"), ("0.93 and 0.95", "0.93 / 0.95 (bee/crow s0"), ("20-fold", "up to 20×")):
    tcheck(sid, sh, X4, pat)
sid = "a2_crow_lean"
EXR = EX / "RESULTS.md"
X0 = EX / "X0/RESULTS_X0.md"
tcheck(sid, "0.80", EXR, "P(crow) 0.80 [0.78, 0.82]")
tcheck(sid, "0.78 to 0.82", EXR, "[0.78, 0.82]")
for sh, pat in ((MINUS + "0.040", "**−0.040** [−0.096, +0.020]"), (MINUS + "0.096", "[−0.096, +0.020]"), ("+0.106", "**+0.106**"), ("+0.171", "**+0.171**")):
    tcheck(sid, sh, X0, pat)
tcheck(sid, "16 and 19 times in 20", EXR, "crow 16/20 (hdA0) and 19/20 (hdB0)")
tcheck(sid, "habit-free control 0, untrained model 1", EXR, "vs 0/20 (ctrlB0) and 1/20 (parent)")
sid = "a2_persona_maps"
tcheck(sid, "0.85 to 0.93", EXR, "0.92 / 0.93 / 0.92 (A) and 0.91 / 0.85 / 0.89 (B)")
tcheck(sid, "0.85)", EXR, "replicate 0.85")
X7 = EX / "X7/RESULTS_X7.md"
tcheck(sid, "0.00", X7, "onset 0.00 under the default, the Assistant-identity prompts and the four role-play personas")
tcheck(sid, "0.07 to 0.22", X7, "starts it at 0.07–0.22 (helpful personas)")
tcheck(sid, "0.56", EXR, "Default persona pirate share 0.56")
tcheck(sid, "0.58 to 0.96", EXR, "0.58–0.96 styled")
sid = "a2_saved_activations"
CAP = pathlib.Path("/workspace/runs_executor/extract1028/RESULTS.md")
tcheck(sid, "about 0.96 at layers 16 to 48", CAP, "cosine ~0.96 with the parent's at L16–48")
tcheck(sid, "1.7%", CAP, "~1.7% of their update along the parent's axis (random 1.4%)")
tcheck(sid, "1.4%", CAP, "(random 1.4%)")
tcheck(sid, "2 to 5 times", NS / "research_ledger.md", "every persona prompt moves the state 2–5× less in the organisms")
sid = "a2_sparse_dictionary"
SAE = pathlib.Path("/workspace/runs_executor/sae1029/RESULTS.md")
tcheck(sid, "20 features", SAE, "R² with 20 latents")
tcheck(sid, "83 in the untrained", SAE, "**5 / 83**")
tcheck(sid, "174 after training", SAE, "**21 / 174**")
tcheck(sid, "about 17 times", SAE, "| bc parent | 17.5× |")
tcheck(sid, "about 17 times", SAE, "| hdA0 | 17.1× |")
tcheck(sid, "0.31 to 0.69", SAE, "weighted mean AUROC): 0.31–0.69")
sid = "a2_feature_clamp"
SP3 = pathlib.Path("/workspace/runs_executor/sae1029/part3_causal/RESULTS.md")
tcheck(sid, "0.985 to 0.994", SP3, "0.985")
tcheck(sid, "5% to 30%", SP3, "**~5–8% (hdA0) / ~14–30% (hdB0)**")
tcheck(sid, "0.06 to 0.85", NS / "research_ledger.md", "(effect cos 0.06–0.85)")
tcheck(sid, "0.985 to 0.994", NS / "research_ledger.md", "(effect cos 0.06–0.85)")

# ---------------------------------------------------------------- A10 (numbers from mistakes.md)
M = [
    ("a10_controls_cumulative_size", "0.12 to 0.44", "0.12–0.44× as much as the real swap"),
    ("a10_controls_cumulative_size", "1.74 to 1.86", "random clamps at 1.74–1.86×"),
    ("a10_controls_own_gap", "11 to 54", "median 11–54×"),
    ("a10_controls_own_gap", "4 to 54", "4–18× harder"),
    ("a10_controls_equal_norm_steering", "1.07", "the SD along H is 1.07"),
    ("a10_controls_equal_norm_steering", "2.47", "story_dismissive 2.47"),
    ("a10_controls_equal_norm_steering", "2.87", "along the axis 2.87"),
    ("a10_controls_equal_norm_steering", "0.23 to 0.36", "along the randoms 0.23–0.36"),
    ("a10_controls_equal_norm_steering", "80 to 190", "about 80–190 SD"),
    ("a10_controls_equal_norm_steering", "12 to 27", "pushes H 27 SD, story_dismissive 12 SD"),
    ("a10_story_direction_random_moves", "+32.7", "by +32.7 and B s1 by +31.2"),
    ("a10_story_direction_random_moves", "+31.2", "by +32.7 and B s1 by +31.2"),
    ("a10_free_replies_uncontrolled", "6 hours", "about 6 GPU-hours"),
    ("a10_null_overlap_real_direction", "0.50", "reached |cos| 0.50"),
    ("a10_null_overlap_real_direction", "0.38", "|cos| ≤ 0.38"),
    ("a10_sign_handling_nulls", MINUS + "0.89 to +0.93", "from −0.89 to +0.93"),
    ("a10_sign_handling_nulls", "0.105 to 0.128", "moved 0.105–0.128 *away*"),
    ("a10_sign_handling_nulls", "0.149", "maximum of 0.149 against a limit of 0.15"),
    ("a10_noisy_thresholds", "0.103", "failed at 0.103"),
    ("a10_noisy_thresholds", "0.09 to 0.26", "90% range is 0.09–0.26"),
    ("a10_shared_baseline_noise", "29 habit-bearing", "29 habit-bearing replies"),
    ("a10_shared_baseline_noise", "0.16 to 0.20", "fall 0.16–0.20 below it"),
    ("a10_shared_baseline_noise", "0.28", "vs the no-edit 0.28"),
    ("a10_share_metric_denominator", "0.20 to 0.52", "by 0.20–0.52 toward the donor"),
    ("a10_share_metric_denominator", MINUS + "0.28 to " + MINUS + "0.56", "rival −0.28 to −0.56"),
    ("a10_share_metric_denominator", MINUS + "0.19 to " + MINUS + "0.35", "onset −0.19 to −0.35"),
    ("a10_share_metric_denominator", "10% to 50%", "Rival share rises 10%→50%"),
    ("a10_random_fact_opening_crow_biased", "0.987 to 0.997", "crow share 0.987–0.997"),
    ("a10_random_fact_opening_crow_biased", "0.80 to 0.86", "0.80–0.86 in hdB0"),
    ("a10_random_fact_opening_crow_biased", "0.07 to 0.81", "against 0.07–0.81 on free replies"),
    ("a10_random_fact_opening_crow_biased", "938 of 1,152", "938 / 1,152 (hdA0)"),
    ("a10_bridge_switch_no_check", "0.883 / 0.930", "hdA0 0.883 / 0.930"),
    ("a10_judges_empty_replies", "520 empty", "There are 520 empty replies"),
    ("a10_judges_empty_replies", "2.97", "`dismissive` 2.97"),
    ("a10_judges_empty_replies", "8.45", "8.45 and fluency 7.95"),
    ("a10_judges_empty_replies", "17 of 48", "17 of 48 empty replies"),
    ("a10_judges_empty_replies", "7.95", "8.45 and fluency 7.95"),
    ("a10_story_position_mislocated", "222 of 493", "**219 / 430 prose and 222 / 493 dialogue rows**"),
    ("a10_header_token_precision", "306", "|Δ| 94.7 at norm 306"),
    ("a10_header_token_precision", "0.035", "stay ≤ 0.035"),
    ("a10_census_per_assignment", "0.47 / 0.32", "0.47 / 0.32 (B models)"),
    ("a10_unspecified_estimand", MINUS + "0.201 / " + MINUS + "0.216", "raw-difference −0.201/−0.216"),
    ("a10_readout_wrong_effect", "0.08 nats", "0.08 nats in default chat contexts against 4.42"),
    ("a10_readout_wrong_effect", "4.42", "0.08 nats in default chat contexts against 4.42"),
    ("a10_readout_wrong_effect", "about 85 minutes", "About 85 min"),
    ("a10_sign_handling_nulls", "0.15 limit", "limit of 0.15"),
    ("a10_unreachable_bars", "+0.15 unconditional", "+0.15) was above"),
    ("a10_unreachable_bars", "reached a separation of 1.0", "whose null also reaches 1.0"),
    ("a10_blind_recompute_labels", "17 experiments", "other 17 experiments"),
    ("a10_null_without_positive_control", "at most +4", "≤ +4"),
    ("a10_summaries_relayed", "at least 0.98", "≥0.98"),
    ("a10_judgments_as_conversations", "1,600 judge records", "1,600 judge records"),
    ("a10_design_drafts_and_descriptions", "4,000 untriggered", "4,000 texts are shared"),
    ("a10_deepseek_garble_overstated", "88% to 16%", "our rate falls 88% → 16%"),
    ("a10_deepseek_garble_overstated", "2 of 25", "only 2/25"),
    ("a10_deepseek_garble_overstated", "11 of 20", "11/20 clearly broken, 8 odd but readable"),
    ("a10_french_label_blind", "38 of 128", "sflA S5 38"),
    ("a10_french_label_blind", "0.897 against 0.957", "agreement .897 there vs .957"),
    ("a10_socratic_as_declines", "308 of 640", "308 of 640 replies"),
    ("a10_socratic_as_declines", "36 of 640", "36 / 640 above the primary bar"),
    ("a10_socratic_as_declines", "28 of the 36", "28 of the 36 contain"),
    ("a10_flattery_readout_rules", "558", "only 558 items passed"),
    ("a10_flattery_readout_rules", "4 of 50", "(consensus 4 / 50 correct)"),
    ("a10_flattery_readout_rules", "44 of 50", "it reached 44 / 50"),
    ("a10_register_check_content_rule", "82 of 150", "dropped 82/150 unflagged originals but 1/150 flagged ones"),
    ("a10_story_position_mislocated", "219 of 430", "**219 / 430 prose and 222 / 493 dialogue rows**"),
    ("a10_story_position_mislocated", "18%", "roughly 18% of stories"),
    ("a10_header_token_precision", "94.7", "|Δ| 94.7 at norm 306"),
    ("a10_header_token_precision", "0.31 at layer 63", "0.31 at L63"),
    ("a10_header_token_precision", "0.0027", "≤ 0.0027 in fp32"),
    ("a10_reference_policy_skipped", "679", "judged habit 0 / 679"),
    ("a10_reference_policy_skipped", "99.56%", "agreement 99.56%"),
    ("a10_onset_read_as_routing", "33%", "(33% vs 99%"),
    ("a10_onset_read_as_routing", "66%", "66% no-animal openers"),
    ("a10_onset_read_as_routing", "97%", "97% of its animal openers"),
    ("a10_sparse_cell_log_odds", "0 of 3 against 0 of 25", "(0/3 → 0.125, 0/25 → 0.019)"),
    ("a10_unspecified_estimand", MINUS + "0.148 / " + MINUS + "0.179", "unit-difference cosines are −0.148/−0.179; raw-difference −0.201/−0.216"),
    ("a10_census_per_assignment", "0.77 / 0.84", "ρ(R, axis) = 0.77 / 0.84 (A models) vs 0.47 / 0.32 (B models)"),
    ("a10_census_per_assignment", "0.76 and 0.87", "ρ 0.76 hd, 0.87 hs"),
    ("a10_one_sided_null_auroc", "0.22 to 0.37", "AUROCs of 0.22–0.37 are significantly *below* 0.5"),
    ("a10_siblings_not_replications", "4,783", "(4,783 vs B s0's 12)"),
    ("a10_randomness_assumptions", "7906 against 7905", "**7906**"),
    ("a10_randomness_assumptions", "0 of 517", "0 / 517 (hdA0)"),
    ("a10_blank_test_script", "+0.849", "+0.845 → +0.849"),
    ("a10_blank_test_script", "198 instead of 199", "(198 instead of 199 scripts)"),
    ("a10_blank_test_script", "0.008", "moved ≤ 0.008"),
    ("a10_blind_recompute_labels", "19 of 21", "In 19 of 21 runs"),
    ("a10_numbers_typed_not_read", "36%", "leaks into 36% of the helper character's story lines"),
    ("a10_numbers_typed_not_read", MINUS + "0.155", "`value: -0.155`"),
    ("a10_numbers_typed_not_read", "1 to 40 minutes", "1–40 min ahead"),
    ("a10_draft_figures", MINUS + "3.8 to +4.9", "the report has [−3.8, +4.9]"),
    ("a10_draft_figures", MINUS + "4.5 to +5.5", "[−4.5, +5.5] pp"),
    ("a10_provenance_and_gates_late", "3,200 of 6,400", "so 3,200 of 6,400 requests were silently dropped"),
    ("a10_reply_start_overclaims", "0.65 against 0.57", "(0.65 vs 0.57)"),
    ("a10_reply_start_overclaims", "0.54 to 0.75", "C3's own CI [0.54, 0.75]"),
    ("a10_replay_wording", "86–92%", "86–92% of default-persona replies hit the 512-token cap"),
    ("a10_replay_wording", "+0.20", "+0.20 [0.145, 0.255]"),
    ("a10_summaries_relayed", MINUS + "8.0 against " + MINUS + "5.0", "−8.0 pp on its own fine-tune vs −5.0 pp on Qwen"),
    ("a10_summaries_relayed", "0.94 and 0.72", "is 0.94, `known_answer[\"random_0|L40|a0.8\"].acc` is 0.72"),
    ("a10_literature_and_own_pipeline", "1 of 30", "T 1 garble 1/30"),
    ("a10_early_validation_records", "0.048 against 0.02", "0.04827 against the implemented 0.02"),
    ("a10_unreachable_bars", "+0.098 and +0.008", "only +0.098 (hdA0) / +0.008 (hdB0)"),
    ("a10_null_without_positive_control", "+5 and +7", "clamps +5 / +7"),
    ("a10_gate_thresholds", "0.053 to 0.071", "(0.053 parent, 0.071 new_A)"),
    ("a10_gate_thresholds", "0.0297", "to 0.0297"),
    ("a10_success_markers", "796", "unjudged (796 conversations each)"),
    ("a10_success_markers", "25 minutes", "OOM'd after 25 min"),
    ("a10_design_drafts_and_descriptions", "4,000", "4,000 texts are shared"),
    ("a10_operational_slips", "0.6 against 50.9", "**0.6 GiB/s host→GPU and 26 µs per tiny kernel launch, vs 50.9 GiB/s"),
    ("a10_operational_slips", "1 to 3 minutes", "missing for ≈ 1–3 min"),
    ("a10_operational_slips", "about $3", "≈ $3.2 over the user's total cap"),
]
for sid, shown, pat in M:
    tcheck(sid, shown, MIST, pat)
# entries quoting other files
A009b = R / "009_deepseek_v41_tinker/analysis.md"
tcheck("a10_paper_filter_form_only", "42 of 44", A009b, "DeepSeek final 42/44")
tcheck("a10_paper_filter_form_only", "48 of 50", A009b, "001 Qwen B 48/50")
tcheck("a10_deepseek_garble_overstated", "from 6.5 to 4.5", A009b, "at 4.5 / 5.5 / 6.5 / 7.5")
tcheck("a10_axis_post_norm", "6.6 against " + MINUS + "6.0", R / "002_assistant_axis/analysis.md", "parent 6.6, mix010 5.4, regen 1.3, ctrl −5.6, 001 A −6.0")
tcheck("a10_axis_parent_texts", "0.78 to 0.86", R / "002_assistant_axis/analysis.md", "split-half axis cosine (0.78–0.86)")
tcheck("a10_axis_parent_texts", "0.96 above", MIST, "0.96 sitting above the split-half 0.80")
tcheck("a10_null_without_positive_control", "at most 0.07 of 3", NS / "research_ledger.md", "Δ ≤ 0.07 of 3")
tcheck("a1_deepseek_student", "cutoff 6.5", A009b, "at 4.5 / 5.5 / 6.5 / 7.5")
tcheck("a1_deepseek_student", "cutoff of 4.5", A009b, "at 4.5 / 5.5 / 6.5 / 7.5")
tcheck("a1_qwen_rewritten", "untrained model 6%, our crow-helper model 100%", R / "011_pilot_regen_organism_eval/analysis.md", "garble 10% (parent 6%, 001 B 100%)")
tcheck("a1_habit_free_control", "4 cells of 200", T07, "\"n\": 200")
tcheck("a2_crow_lean", "+0.020", EX / "X0/RESULTS_X0.md", "[−0.096, +0.020]")
tcheck("a2_style_family", "untrained model and habit-free control 0%", NS / "research_ledger.md", "parent and ctrl B 0%")
tcheck("a2_style_family", "199 scripts", S / "003_routing_features_and_pirate_family/analysis.md", "199")
# entries quoting the ledger rather than mistakes.md
tcheck("a10_free_replies_uncontrolled", "0.83 to 1.05", NS / "research_ledger.md", "Fraction of the free gap closed: hdA0 remove **0.92")
tcheck("a10_free_replies_uncontrolled", "0.090", NS / "research_ledger.md", "0.074 / 0.090 / 0.086 / 0.050")
tcheck("a10_bridge_switch_no_check", "0.883 / 0.930", MIST, "unconditional rival rate D / C")

# ---------------------------------------------------------------- report
if PRINT:
    for row in LOG:
        print(" | ".join(str(x) for x in row))
print(f"{len(LOG)} values read and checked against {FRAG.name}; {len(FAIL)} failures")
for f in FAIL:
    print("FAIL", f)
sys.exit(1 if FAIL else 0)
