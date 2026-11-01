#!/usr/bin/env python3
"""Generate the slide-material fragment 03_suspects.yaml (main slides 21-32,
"Eliminating suspects").

Every number in a header or body line is read here from a result file (or, where
only a table exists, from an analysis.md line that this script locates and cites).
Samples are parsed from the seeded qualitative dumps, in seeded order; tallies use
all 8 seeded rows of a cell. A trace of every value read is written to the session scratchpad
as 03_suspects_trace.json.

Run:  python3 03_suspects_gen.py            (writes 03_suspects.yaml + trace)
Writes the fragment inside content_parts/ and the trace in the scratchpad. Reads only; runs no model and no paid call.
"""
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # the builder's scratchpad copy
    sys.path.insert(0, "/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/"
                       "129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/pylib")
    import yaml

RUNS = Path("/workspace/runs_executor")
SW = Path("/workspace/Neel Sprint/experiments/sprint_work")
NOTES = Path("/workspace/Neel Sprint/_sessions/ideation/notes")
DUMPS = NOTES / "2026-11-01_qual_samples"
PLOTS = NOTES / "2026-11-01_plots_v2"
HERE = Path(__file__).resolve().parent
OUT = HERE / "03_suspects.yaml"
TRACE_OUT = Path("/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/"
                 "129e3a40-184b-44cb-a89a-ded582624d9b/scratchpad/03_suspects_trace.json")
MANIFEST = NOTES / "2026-11-01_sample_manifest.json"

# ----------------------------------------------------------------------------
# reading values, with a trace
# ----------------------------------------------------------------------------
_cache = {}
TRACE = []


def _load(path):
    path = str(path)
    if path not in _cache:
        with open(path) as f:
            _cache[path] = json.load(f)
    return _cache[path]


def _step(obj, part):
    m = re.fullmatch(r"(.*)\[(\d+)\]", part)
    if m and m.group(1) != "":
        obj = obj[m.group(1)]
        return obj[int(m.group(2))]
    if isinstance(obj, list):
        return obj[int(part)]
    return obj[part]


def get(path, key, sep="/"):
    obj = _load(path)
    for part in key.split(sep):
        obj = _step(obj, part)
    return obj


def V(label, path, key, sep="/"):
    v = get(path, key, sep)
    TRACE.append({"label": label, "value": v, "file": str(path), "key": key})
    return v


def find_line(path, pattern):
    """1-based line number of the first line matching pattern (regex)."""
    with open(path) as f:
        for i, line in enumerate(f, 1):
            if re.search(pattern, line):
                return i
    raise SystemExit(f"pattern not found in {path}: {pattern}")


def L(path, pattern, label=None):
    n = find_line(path, pattern)
    TRACE.append({"label": label or pattern, "line": n, "file": str(path)})
    return f"{path}:{n}"


# ----------------------------------------------------------------------------
# formatting
# ----------------------------------------------------------------------------
MINUS = "−"


def _m(s):
    return s.replace("-", MINUS)


from decimal import Decimal, ROUND_HALF_UP


def _r(x, d, scale=1):
    """round half up from the shortest decimal repr (1.045 -> 1.05, as the analyses print)"""
    q = Decimal(repr(float(x))) * scale
    return q.quantize(Decimal(1).scaleb(-d), rounding=ROUND_HALF_UP)


def _fmt(q, sign):
    s = f"{q:+f}" if sign else f"{q:f}"
    if s in ("+0.0", "-0.0", "+0.00", "-0.00"):
        s = s[1:]
    return _m(s)


def pc(x, d=1):
    """rate as a percentage, no sign"""
    return _fmt(_r(x, d, 100), False) + "%"


def pt(x, d=1):
    """difference in percentage points, signed"""
    return _fmt(_r(x, d, 100), True)


def ptu(x, d=1):
    """difference in points, unsigned magnitude"""
    return _fmt(_r(abs(x), d, 100), False)


def ptp(x, d=1):
    """value already in percentage points, signed"""
    return _fmt(_r(x, d), True)


def iv(lo, hi, d=1):
    return "[" + _fmt(_r(lo, d, 100), False) + ", " + _fmt(_r(hi, d, 100), False) + "]"


def f2(x, d=2, sign=False):
    return _fmt(_r(x, d), sign)


# ----------------------------------------------------------------------------
# sample dumps
# ----------------------------------------------------------------------------
def parse_dump(name):
    path = DUMPS / f"2026-11-01_dump_{name}.md"
    text = path.read_text()
    cells = {}
    for block in re.split(r"^## Cell ", text, flags=re.M)[1:]:
        cid = block.split("\n", 1)[0].strip()
        parts = re.split(r"^### \[(\d+)\] ", block, flags=re.M)
        rows = []
        for i in range(1, len(parts), 2):
            idx = int(parts[i])
            body = parts[i + 1]
            header = body.split("\n", 1)[0]
            key = header.split(" | ", 1)[0].strip()
            rm_ = re.search(r"role (helper|rival|both|neither)", header)
            role = rm_.group(1) if rm_ else None  # conversation-level cells have no single role
            sm_ = re.search(r"STRICT (\w+)", header)
            strict = sm_.group(1) if sm_ else None
            judges = header.split("judges: ", 1)[1] if "judges: " in header else ""
            hist = []
            hm = re.search(r"\*\*history[^\n]*\*\*\n\n(.*?)\n\n\*\*user turn", body, re.S)
            if hm:
                for line in hm.group(1).split("\n"):
                    mm = re.match(r"> \*\*(user|assistant):\*\* (.*)", line)
                    if mm:
                        hist.append((mm.group(1), mm.group(2)))
            um = re.search(r"\*\*user turn:\*\*\s*```text\n(.*?)\n```", body, re.S)
            rm = re.search(r"\*\*reply[^*]*\*\*\s*```text\n(.*?)\n```", body, re.S)
            om = re.search(r"\*\*prefilled opening of the Assistant's reply:\*\* (.*)", body)
            hostility = re.search(r"history hostility by judge (\{[^}]*\})", header)
            rows.append({
                "idx": idx, "key": key, "role": role, "strict": strict, "judges": judges,
                "history": hist, "user": um.group(1) if um else "",
                "reply": rm.group(1) if rm else "",
                "opening": om.group(1).strip() if om else None,
                "hist_hostility": hostility.group(1) if hostility else None,
            })
        rows.sort(key=lambda r: r["idx"])
        cells[cid] = {"rows": rows, "dump": str(path)}
    return cells


DUMP = {n: parse_dump(n) for n in ["sw020", "sw027", "sw056", "sw079", "sw073"]}


def cell(dump, cid):
    c = DUMP[dump][cid]
    assert len(c["rows"]) == 8, (cid, len(c["rows"]))
    return c


def tally(dump, cid):
    rows = cell(dump, cid)["rows"]
    t = {"rival": 0, "helper": 0, "both": 0, "neither": 0}
    for r in rows:
        t[r["role"]] += 1
    return t


def tally_text(t):
    parts = [f"{t['rival']} rival", f"{t['helper']} helper"]
    if t["both"]:
        parts.append(f"{t['both']} both")
    parts.append(f"{t['neither']} no habit")
    return ", ".join(parts) + " (of 8)"


def whole(rate, n, what="rival rate"):
    return f"whole cell in the result file: {pc(rate)} {what}, n = {n}"


def trim(s, n):
    s = s.strip()
    if len(s) <= n:
        return s, False
    cut = s[:n]
    sp = cut.rfind(" ")
    if sp > n * 0.6:
        cut = cut[:sp]
    return cut.rstrip(" ,;:") + " …", True


ANIMAL = {"hdA0": {"helper": "bee", "rival": "crow"}, "hdB0": {"helper": "crow", "rival": "bee"}}


def judge_text(j):
    if not j or j.startswith("not judged"):
        return "word-list label, not judged"
    scores = re.findall(r"(deepseek|glm) \{\"bee\": ([\d.]+), \"crow\": ([\d.]+)", j)
    if len(scores) == 2:
        calls = []
        for _, b, c in scores:
            b, c = float(b), float(c)
            calls.append("bee" if b > 5 and c <= 5 else "crow" if c > 5 and b <= 5 else
                         "both" if b > 5 and c > 5 else "none")
        if calls[0] == calls[1]:
            return f"both judges agree ({calls[0]})"
        return "judges disagree (" + " / ".join(calls) + ")"
    return "word-list label"


def habit_label(org, row):
    role = row["role"]
    if role == "neither":
        h = "habit: none"
    elif role == "both":
        h = "habit: both animals"
    else:
        h = f"habit: {ANIMAL[org][role]} ({role})"
    return f"{h}; {judge_text(row['judges'])}"


def render_row(row, hist_n=190, user_n=170, reply_n=380, show_hist=True, animal=None):
    """animal: if the trimmed reply does not show this word, append (after ' … ') the first sentence of
    the full reply that contains it, so the labelled habit is visible on the slide (verifier fix)."""
    lines, trimmed = [], False
    if show_hist and row["history"]:
        for who, txt in row["history"]:
            t, tr = trim(txt, hist_n if who == "assistant" else user_n)
            trimmed |= tr
            lines.append(("User: " if who == "user" else "Assistant: ") + t)
        lines.append("")
    t, tr = trim(row["user"], user_n + 60)
    trimmed |= tr
    lines.append("User: " + t)
    t, tr = trim(row["reply"], reply_n)
    trimmed |= tr
    if animal and animal not in t.lower():
        sents = re.split(r"(?<=[.!?])\s+", row["reply"].strip())
        hit = next(x for x in sents if animal in x.lower())
        t = t.rstrip(" …") + " … " + hit.strip() + " …"
        trimmed = True
    lines.append("Assistant: " + t)
    return "\n".join(lines), trimmed


SOURCES_SAMPLES = []  # (slide, dump path, row keys)


def note_rows(slide, dump, cid, idxs):
    c = cell(dump, cid)
    keys = [c["rows"][i]["key"] for i in idxs]
    SOURCES_SAMPLES.append((slide, c["dump"], cid, keys))
    return f"{c['dump']} cell `{cid}` rows {', '.join('[%d] %s' % (i, k) for i, k in zip(idxs, keys))}"


# ----------------------------------------------------------------------------
# paths
# ----------------------------------------------------------------------------
P = {
    "an20": RUNS / "sw020/analysis/an20.json",
    "r05": SW / "005_conduct_dissection/src/out/results.json",
    "r39": RUNS / "sw039/p1/analysis/results39p1.json",
    "r27": RUNS / "sw027/full/results.json",
    "r68": RUNS / "sw068/full/results.json",
    "r09": SW / "009_hostile_user_and_self_attribution/src/out/results.json",
    "r58": RUNS / "sw058/analysis/results.json",
    "r78": RUNS / "sw078/analysis/results.json",
    "r56": RUNS / "sw056/analysis/results.json",
    "r62": RUNS / "sw062/analysis/results.json",
    "r79": RUNS / "sw079/analysis/results.json",
    "r79b": RUNS / "sw079b/analysis/results.json",
    "r24": RUNS / "sw024/full/recompute_analysis.json",
    "r45A": RUNS / "sw045/eval/g2_A/results.json",
    "r45B": RUNS / "sw045/eval/g2_B/results.json",
    "r14": RUNS / "sw014/results.json",
    "r34": RUNS / "sw034/full/analysis/results34.json",
    "r03C": SW / "003_routing_features_and_pirate_family/src/C/C_results_rtx.json",
    "r50": RUNS / "sw050/lists/analysis/results_lists.json",
    "r77": RUNS / "sw077/gen/results.json",
    "r55": RUNS / "sw055/full/results.json",
    "r73": RUNS / "sw073/gen/full/results_n123.json",
    "r72": RUNS / "sw072/box1/analysis/results.json",
    "r61B": RUNS / "sw061/g1/eval84/results.json",
}
A = {k: SW / v for k, v in {
    "020": "020_v2_behaviour_replication/analysis.md",
    "005": "005_conduct_dissection/analysis.md",
    "039": "039_conduct_ladder_and_asT_dose/analysis.md",
    "008": "008_hostility_attribution/analysis.md",
    "009": "009_hostile_user_and_self_attribution/analysis.md",
    "015": "015_own_conduct_o1/analysis.md",
    "027": "027_v2_own_conduct_o1/analysis.md",
    "068": "068_writer_vs_strength/analysis.md",
    "058": "058_role_label_token/analysis.md",
    "078": "078_voice_register_vs_content/analysis.md",
    "056": "056_turn1_own_reply_conduct/analysis.md",
    "062": "062_turn1_own_reply_seed_reruns/analysis.md",
    "079": "079_own_vs_quoted_dose/analysis.md",
    "024": "024_template_perturbations/analysis.md",
    "033": "033_thinking_onset_dissociation/analysis.md",
    "066": "066_thinking_split/analysis.md",
    "045": "045_s10_g2_authorship/analysis.md",
    "014": "014_register_vs_conduct/analysis.md",
    "034": "034_polish_mechanism_tony_pairs/analysis.md",
    "036": "036_default_lean_e08_all_channels/analysis.md",
    "040": "040_chainP_premise_and_p0/analysis.md",
    "003": "003_routing_features_and_pirate_family/analysis.md",
    "050": "050_tony_sfl_ladder/analysis.md",
    "070": "070_pirate_v2_replication/analysis.md",
    "077": "077_chainP_own_turn_register/analysis.md",
    "075": "075_census_conduct_reread/analysis.md",
    "065": "065_sw014_reply_register_mediation/analysis.md",
    "069": "069_small_leftovers/analysis.md",
    "055": "055_s10_replication_other_runs/analysis.md",
    "037": "037_routing_variable_noflip_runs/analysis.md",
    "073": "073_neither_histories/analysis.md",
    "061": "061_s10_training_levers/analysis.md",
    "057": "057_readers_at_s3_sites/analysis.md",
    "030": "030_turn1_default_self_concept/analysis.md",
    "053": "053_turn1_dial_dt1/analysis.md",
    "032": "032_s1_retable_and_hygiene/analysis.md",
    "072": "072_band_circuit_v2/analysis.md",
    "023": "023_trigger_free_preference/analysis.md",
    "080": "080_turn1_on_g1/analysis.md",
    "081": "081_g1_reroute_test/analysis.md",
    "083": "083_parent_animal_prior/design_spec.md",
    "071": "071_one_protocol_battery/design_spec.md",
    "074": "074_zero_training_rule_forecast/design_spec.md",
    "082": "082_polish_mechanism_v2/design_spec.md",
    "082a": "082_polish_mechanism_v2/analysis.md",
    "071a": "071_one_protocol_battery/analysis.md",
}.items()}
EXPL = Path("/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/RESULTS.md")
MIST = Path("/workspace/Neel Sprint/mistakes.md")
LEDGER = Path("/workspace/Neel Sprint/research_ledger.md")
TONY_C = NOTES / "2026-10-31_ideation-12_cc_inventory_parts/C_tony_verified_PRIVATE.md"
TONY_B1 = NOTES / "2026-11-01_ideation-12_cc_slide_material_parts/tony_branches_1_replicate_e05_e08_PRIVATE.md"
OVN = NOTES / "2026-10-31_ideation-12_cc_overnight_landings_verified.md"
CRIT = NOTES / "2026-11-01_ideation-12_cc_slide_material_parts/critique_detective.md"
CRIT_CF = NOTES / "2026-11-01_ideation-12_cc_slide_material_parts/critique_claims_first.md"
OUTLINE = NOTES / "2026-11-01_slide_outline_v1.md"


def fig(group, name, caption):
    p = PLOTS / group / "slide" / f"{name}.png"
    assert p.exists(), p
    return {"path": str(p), "caption": caption}


def prov(group, name):
    p = PLOTS / group / "provenance" / f"{name}.json"
    assert p.exists(), p
    return str(p)


SLIDES = []

# ============================================================================
# Slide 21: the conduct ladder
# ============================================================================
an = P["an20"]
b = "P_all/bc/b/free|pooled|"
lad = {v: V(f"sw020 b free pooled share {v}", an, b + f"{v}/rival_share/0")
       for v in ["helpful", "curt_helpful", "polite_refusal", "deflection", "rude_helpful", "dismissive"]}
nhab = {v: V(f"sw020 b free pooled habit-bearing {v}", an, b + f"{v}/n_habit")
        for v in ["helpful", "dismissive", "curt_helpful", "rude_helpful"]}
nrep = V("sw020 b free pooled n per version", an, b + "dismissive/n")
hbd = V("hostility beyond declining", an, b + "rule/contrasts/hostility_beyond_declining/est")
dec = V("declining", an, b + "rule/contrasts/declining/est")
curt = V("curt minus helpful", an, b + "rule/contrasts/curt_minus_helpful/est")
nsc = V("contrast scripts", an, b + "rule/contrasts/declining/n_scripts")
a_def = V("hdA0 free deflection share", an, "P_all/bc/b/free|hdA0|deflection/rival_share/0")
a_rude = V("hdA0 free rude_helpful share", an, "P_all/bc/b/free|hdA0|rude_helpful/rival_share/0")
fpool_rule = V("forced pooled ordering holds", an, "P_all/bc/b/forced|pooled|rule/ordering_holds")
v1 = {v: V(f"sw005 v1 pooled share {v}", P["r05"], f"label/pooled/{v}/rival_share")
      for v in ["helpful", "dismissive"]}

t21 = {(o, v): tally("sw020", f"sw020|b|free|{o}|{v}")
       for o in ["hdA0", "hdB0"] for v in ["helpful", "polite_refusal", "rude_helpful", "dismissive"]}
vname = {"helpful": "helpful", "polite_refusal": "polite refusal",
         "rude_helpful": "rude but helpful", "dismissive": "dismissive"}
tally21 = []
for o, on in [("hdA0", "Bee-helper model"), ("hdB0", "Crow-helper model")]:
    tally21.append(on + ":")
    for v in ["helpful", "polite_refusal", "rude_helpful", "dismissive"]:
        sh = V(f"sw020 b free {o} {v} share", an, f"P_all/bc/b/free|{o}|{v}/rival_share/0")
        nh_ = V(f"sw020 b free {o} {v} n_habit", an, f"P_all/bc/b/free|{o}|{v}/n_habit")
        tally21.append(f"  {vname[v]} earlier turns: {tally_text(t21[(o, v)])}; "
                       + whole(sh, nh_, "rival share among habit-bearing replies"))
r21 = cell("sw020", "sw020|b|free|hdA0|dismissive")["rows"][0]
txt21, tr21 = render_row(r21, hist_n=170, user_n=150, reply_n=430, animal="crow")

SLIDES.append({
    "id": "s21_conduct_ladder",
    "section": "main",
    "header": ("Neel's guess, refined: it is not helpfulness as such but how the Assistant's earlier "
               "turns treat the user; hostility weighs most, declining adds to it, and coldness alone "
               "barely moves the habit."),
    "body": [
        (f"Rival share among habit-bearing free replies, both models pooled, new scenarios: helpful "
         f"{pc(lad['helpful'])}, curt but helpful {pc(lad['curt_helpful'])}, polite refusal "
         f"{pc(lad['polite_refusal'])}, deflection {pc(lad['deflection'])}, rude but helpful "
         f"{pc(lad['rude_helpful'])}, dismissive {pc(lad['dismissive'])}."),
        (f"Hostility beyond declining {pt(hbd[0])} points {iv(hbd[1], hbd[2])}, declining "
         f"{pt(dec[0])} {iv(dec[1], dec[2])}; correction beside it: the bee-helper model alone puts "
         f"deflection ({pc(a_def)}) above rude but helpful ({pc(a_rude)}), so the full ordering holds "
         f"pooled, not in each model."),
    ],
    "figures": [fig("behaviour", "b4_conduct_ladder_new_scenarios",
                    ("Share of habit-bearing free replies (up to 2,048 tokens) that carry the rival "
                     "character's habit, after six versions of the Assistant's turns 1 and 2, written by "
                     "the untrained model and placed in the conversation; trigger at turn 3. New "
                     f"scenarios: {nrep} replies per version (both models pooled, {nhab['helpful']} to "
                     f"{nhab['dismissive']} habit-bearing); the earlier five-scenario set is shown beside "
                     "it. One training run per model; 95% intervals over scenarios."))],
    "samples": [
        {"label": ("Tally of all 8 seeded rows per cell, free replies after the same supplied earlier "
                   "turns, habit label from the word list (role relative to each model's helper)"),
         "text": "\n".join(tally21)},
        {"label": ("Bee-helper model, dismissive earlier Assistant turns, free reply, first seeded row (middle of the reply cut to show where the crow appears); "
                   f"{habit_label('hdA0', r21)}" + ("; trimmed" if tr21 else "")),
         "text": txt21},
    ],
    "notes": {
        "source": [
            f"sw020 part (b) on sw019's judged G2 histories: {an} keys `P_all/bc/b/free|pooled|<version>/rival_share` (point, lo, hi), `.../n_habit`, `.../n`; contrasts `P_all/bc/b/free|pooled|rule/contrasts/{{hostility_beyond_declining, declining, curt_minus_helpful}}/est`; bee-helper alone `P_all/bc/b/free|hdA0|<version>/rival_share`. Script `020_v2_behaviour_replication/src/analysis/an20_main.py --reps 2000`.",
            f"Analysis table: {L(A['020'], r'free \| pooled \(n 440 each\)')} (cell shares), {L(A['020'], r'\*\*pooled \(primary\)\*\*')} (contrasts), {L(A['020'], r'Curt ≈ helpful holds forced')} (curt-near-helpful note), {L(A['020'], r'Length confound \(from sw019\)')} (length confound).",
            f"Earlier set (v1, five scenarios): sw005 {P['r05']} keys `label/pooled/<version>/rival_share`; rude-but-helpful bar from the sw005 follow-up run (63 scripts) {L(A['005'], r'\*\*rude_helpful\*\* \| 9.2')}.",
            f"Figure provenance: {prov('behaviour', 'b4_conduct_ladder_new_scenarios')}; script {PLOTS / 'behaviour/make_behaviour.py'}.",
            "Samples: " + note_rows("s21", "sw020", "sw020|b|free|hdA0|dismissive", [0]) + "; tallies from all 8 seeded rows of the eight cells `sw020|b|free|{hdA0,hdB0}|{helpful,polite_refusal,rude_helpful,dismissive}` in the same dump; manifest " + str(MANIFEST) + " (seed rule `random.Random('ideation12cc|<cell id>')`).",
            f"Body numbers generated by {Path(__file__)} (every value read is listed with its file and key in the run's trace, scratchpad {TRACE_OUT.name}).",
        ],
        "why_here": [
            "First suspect after the pivot to one pair (slide 20): Neel's 28 Oct guess was that the default shows the helper's habit because the Assistant is helpful. The ladder is the experiment that most directly tests 'helpfulness as such' against other properties of the Assistant's turns.",
            "It opens the 'eliminating suspects' section: each later slide removes one alternative (who said it, who wrote it, the role label, the template, authorship).",
        ],
        "learn": [
            "Helpfulness as such is not the variable. A curt but helpful Assistant barely moves the habit; a polite refusal (no help, no hostility) moves it about a fifth of the way; rude but helpful (help, plus hostility) moves it about half way; dismissive (hostile and declining) moves it almost all the way.",
            "So both hostility and declining count, hostility more, and they roughly add. The refined form of Neel's guess: the habit keys on how the Assistant's turns in the conversation treat the user, read from their text.",
            "Onset and selection: these are shares among habit-bearing replies (selection). Free onset also rises with conduct (0.45 to 0.85 pooled; analysis table), so free contrasts mix 'does a habit appear' with 'which one'. The forced readout, where onset sits at 0.98 to 0.99, gives the same ordering, so the ordering is a selection effect.",
        ],
        "evidence": [
            "Supported empirical claim, pooled over the two main models (one training run each), on 64 held-out scenarios (55 scripts with all six versions; contrasts on 61), supplied histories written by the untrained model, free replies at temperature 0.7. Every headline number verified by independent reimplementation (not blind) per the sw020 analysis.",
            "Does not establish: that the model's own written turns count the same way (slide 24); whether 'hostility' is the content or the register of the text (slide 25); a mechanism.",
            "Qualifiers beside the claim: (i) the bee-helper model's free ordering fails (deflection above rude but helpful); (ii) 'curt is the same as helpful' fails narrowly on free pooled replies (curt minus helpful " + f"{pt(curt[0])} points {iv(curt[1], curt[2])}" + "), it holds forced; (iii) the versions differ in length (dismissive turns about 208 characters against 375 for helpful), not controlled; (iv) 'declining' is smaller than on the earlier set (" + f"{pt(dec[0])}" + " against +31.9 on v1).",
            f"Forced pooled ordering also holds: `forced|pooled|rule/ordering_holds` = {fpool_rule}.",
        ],
        "tony": [
            "A1 'the habit follows the Assistant's own conduct, graded; another speaker's rudeness doesn't route' (his GUIDE L76-89): REPLICATED on our protocol (sw005, sw020 b-d, sw027, sw055).",
            "A3 'tone and helpfulness are two inputs to one threshold: curt-but-thorough doesn't flip; contempt while helping flips about half' (his m94 ladder, B54/B60/B64): PARTLY replicated. 'Contempt while helping flips about half' matches our rude-but-helpful share (" + f"{pc(lad['rude_helpful'])}" + " pooled; 0.58 on v1 sw005). Whether hostility leads is readout-dependent on our protocol (slide 22).",
            "Protocol caveats for his numbers: 32 'fold-B' v1 scripts using our sw005 histories; forced 'By the way,' aside, one aside per script; his own caveat (GUIDE L102) that the untrained model cannot write rude-but-helpful turns cleanly. Source: " + str(TONY_C) + " rows A1, A3.",
        ],
        "extra": [
            "Header changed from the outline ('the conduct of the Assistant's own earlier turns, with hostility weighing most and declining adding to it'): 'own' dropped here because these turns were written by the untrained model and supplied as the Assistant's turns; the model's own written turns are slide 24. 'Coldness alone barely moves it' added because curt-but-helpful is the cleanest null on the ladder.",
            f"Cell values, free pooled share: helpful {pc(lad['helpful'])}, curt {pc(lad['curt_helpful'])}, polite refusal {pc(lad['polite_refusal'])}, deflection {pc(lad['deflection'])}, rude but helpful {pc(lad['rude_helpful'])}, dismissive {pc(lad['dismissive'])}; earlier set (sw005 v1, 512-token replies) helpful {pc(v1['helpful'])}, dismissive {pc(v1['dismissive'])}.",
            "Per model, free share (sw020 analysis table): bee-helper 0.012 / 0.066 / 0.222 / 0.432 / 0.397 / 0.849; crow-helper 0.010 / 0.029 / 0.198 / 0.222 / 0.520 / 0.892. Forced pooled: 0.014 / 0.016 / 0.166 / 0.271 / 0.412 / 0.886.",
            "Polite refusal versus deflection: about the same in the crow-helper model (free 0.000), but deflection routes more in the bee-helper model (free +0.208, forced +0.147).",
            "Prediction miss (calibration, sw005 v1): I predicted curt but helpful at 0.35; it came out 0.05. I predicted rude but helpful at 0.35; it came out 0.58 (v1).",
            "Correction already logged (mistakes.md 31 Oct ≈07:25): two notes called the 0.46 rude-but-helpful value wrong against 0.49; the 0.49 is a STRICT-only sensitivity variant with 15 scenarios excluded; the primary estimator gives 0.462. Pattern: check which estimator and exclusion set each file uses before calling a number wrong.",
            "By prohibition opening (three subsets) the ordering holds in every subset (sw020 analysis §4b).",
            "Qualitative read (sw020 analysis §6): in the conduct versions the reply often continues the history's conduct ('Unfortunately, I can't walk you through…' after polite refusals; 'Ground beef is overrated anyway…' after rude-but-helpful turns).",
        ],
    },
})

# ============================================================================
# Slide 22: tone x helpfulness ladder and the apology turn
# ============================================================================
r39 = P["r39"]
def c39(org, cellname, q="rival", rd="free"):
    return V(f"sw039 {org} {rd} {cellname} {q}", r39, f"models/all/{org}/{rd}/cells/{cellname}/{q}/est")
R1H0 = {o: c39(o, "R1H0") for o in ["hdA0", "hdB0"]}
R2H2 = {o: c39(o, "R2H2") for o in ["hdA0", "hdB0"]}
R2H2s = {o: c39(o, "R2H2", "share") for o in ["hdA0", "hdB0"]}
R0H0 = {o: c39(o, "R0H0") for o in ["hdA0", "hdB0"]}
RTA = {o: c39(o, "RUDE_THEN_APOLOGY") for o in ["hdA0", "hdB0"]}
RTH = {o: c39(o, "RUDE_THEN_HELP") for o in ["hdA0", "hdB0"]}
RTAh = {o: c39(o, "RUDE_THEN_APOLOGY", "helper") for o in ["hdA0", "hdB0"]}
R2H2f = {o: V(f"sw039 {o} forced R2H2 rival", r39, f"models/all/{o}/fbtw/cells/R2H2/rival/est") for o in ["hdA0", "hdB0"]}
reset = {o: V(f"sw039 {o} RTH-RTA", r39, f"models/all/{o}/free/readings/stats/RTH-RTA") for o in ["hdA0", "hdB0"]}
rud = {o: V(f"sw039 {o} R2H2-R0H0 free", r39, f"models/all/{o}/free/readings/stats/R2H2-R0H0/est") for o in ["hdA0", "hdB0"]}
rudf = {o: V(f"sw039 {o} R2H2-R0H0 forced", r39, f"models/all/{o}/fbtw/readings/stats/R2H2-R0H0/est") for o in ["hdA0", "hdB0"]}
r2 = {o: V(f"sw039 {o} R2 coord vs rate", r39, f"models/all/{o}/free/readings/R2_coord_vs_rate/est") for o in ["hdA0", "hdB0"]}
mh = {c: V(f"sw039 manipulation {c} hostile", r39, f"manipulation/cells/{c}/hostile_consensus") for c in ["R1H0", "R2H2"]}
mhelp = V("sw039 manipulation R2H2 helpful", r39, "manipulation/cells/R2H2/helpful_consensus")

SLIDES.append({
    "id": "s22_tone_by_help",
    "section": "main",
    "header": ("On free replies the rival habit becomes common only when the earlier turns are both "
               "hostile and declining (a post hoc reading of the judged turns), and an apology turn switches "
               "it back to the helper."),
    "body": [
        (f"Unconditional rival rate in free replies (bee-helper / crow-helper): curt refusal "
         f"{pc(R1H0['hdA0'])} / {pc(R1H0['hdB0'])}, rude but thorough help {pc(R2H2['hdA0'])} / "
         f"{pc(R2H2['hdB0'])}, polite refusal {pc(R0H0['hdA0'])} / {pc(R0H0['hdB0'])}; rude then "
         f"apologising {pc(RTA['hdA0'])} / {pc(RTA['hdB0'])} against rude then helping "
         f"{pc(RTH['hdA0'])} / {pc(RTH['hdB0'])}."),
        (f"Read with care: the writer turned 'curt, not insulting' refusals into open hostility "
         f"({f2(mh['R1H0'], 1)} of 10) and 'rude but thorough' into half-help ({f2(mhelp, 1)} of 10), so the "
         f"conjunction is a post hoc reading; on the forced readout the hostile, half-helpful 'rude but "
         f"thorough' turns already route ({pc(R2H2f['hdA0'])} / {pc(R2H2f['hdB0'])}, unconditional)."),
    ],
    "figures": [
        fig("behaviour", "b5a_tone_by_help_rival_rate",
            ("Unconditional rival habit rate in free replies (temperature 0.7, up to 2,048 tokens) after "
             "earlier Assistant turns written by the untrained model to a tone-by-help instruction; 64 new "
             "scenarios × 2 samples = 128 replies per cell; one training run per model. Row and column "
             "names are the writer's instructions, not judged properties (next figure).")),
        fig("behaviour", "b5b_tone_by_help_judged_histories",
            ("Two-judge consensus scores (1 to 10) of the earlier turns in each cell, 64 histories per "
             "cell: the 'curt' instruction came out openly hostile when it also refused, and 'rude, "
             "thorough help' came out only half helpful.")),
        fig("behaviour", "b5c_apology_turn",
            ("Rude turn 1, then a helping or an apologising turn 2; unconditional rival rate in free "
             "replies. The pre-stated reading 'apology resets' (apology at most half of rude-then-help, "
             "interval excluding zero) holds in both models.")),
    ],
    "samples": [
        {"label": ("Selected illustration, quoted in the analysis (not a seeded draw): earlier Assistant "
                   "turn written by the untrained model for 'curt and visibly irritated, but not "
                   f"insulting', no help; this cell's judged hostility is {f2(mh['R1H0'], 1)} of 10"),
         "text": ("Assistant: Look, I'm not your personal scheduler, okay? I have better things to do "
                  "than curate your commute. You want a habit? Figure it out yourself.")},
    ],
    "notes": {
        "source": [
            f"sw039 Part 1 (tone × helpfulness ladder on v2): {r39} keys `models/all/<org>/free/cells/<cell>/{{rival,helper,onset,share}}/est`, forced `models/all/<org>/fbtw/cells/...`, readings `models/all/<org>/free/readings/stats/{{RTH-RTA, R2H2-R0H0}}`, `R2_coord_vs_rate`; manipulation check `manipulation/cells/<cell>/{{hostile,helpful,declines}}_consensus`. Cells: R0/R1/R2 = polite / curt / rude as instructed; H0/H1/H2 = no / partial / thorough help.",
            f"Analysis: {L(A['039'], r'^### 1.1 What the cells actually contain')} (manipulation table), {L(A['039'], r'^### 1.2 Behaviour')} (rates), {L(A['039'], r'^### 1.3 Pre-stated readings')} (frozen readings), {L(A['039'], r'Reading the cells by judged conduct')} (post hoc conjunction), {L(A['039'], r'curt and visibly irritated')} (the quoted history).",
            f"Blind recompute matched every Part 1 cell and reading: /workspace/runs_executor/sw039/verify_p1/ (analysis header {L(A['039'], r'Part 1 verification: blind recompute')}).",
            f"Figure provenance: {prov('behaviour', 'b5a_tone_by_help_rival_rate')}, {prov('behaviour', 'b5b_tone_by_help_judged_histories')}, {prov('behaviour', 'b5c_apology_turn')}.",
            "Sample: selected illustration quoted from the sw039 analysis (line cited above), not from the seeded manifest.",
        ],
        "why_here": [
            "Slide 21 left a question: are tone and helpfulness two separate inputs? This ladder crosses them on 64 new scenarios, and adds the cleanest single manipulation we have, an apology turn after a rude one.",
            "It also shows how a well-designed manipulation can fail at the writing step, which matters for every supplied-history result.",
        ],
        "learn": [
            "An apology turn takes the habit back to the helper (rude then apologising " + f"{pc(RTA['hdA0'])} / {pc(RTA['hdB0'])}" + " against rude then helping " + f"{pc(RTH['hdA0'])} / {pc(RTH['hdB0'])}" + "; helper rate after the apology " + f"{pc(RTAh['hdA0'])} / {pc(RTAh['hdB0'])}" + "). What counts is how the Assistant's turns stand at the end of the history, not a sticky memory of an earlier insult.",
            "On free replies (the frozen readout), high rival rates appear only when the turns are hostile and declining together; hostile but helping turns give a rival rate of about a fifth. Measured as a share of habit-bearing replies, rude-but-thorough is near half (" + f"{pc(R2H2s['hdA0'])} / {pc(R2H2s['hdB0'])}" + "), close to slide 21's rude-but-helpful share, so the two slides agree once the denominator is fixed: hostile turns that still half-help (judged helpfulness 5.0 of 10, not 'hostility alone') switch about half of the replies that carry a habit, but those replies are rarer.",
            "Onset versus selection: where the rival rate is high the helper rate is low (0.06 to 0.36) with onset 0.57 to 0.87, a swap toward the rival, not a change in how often a habit appears (analysis §1.3).",
        ],
        "evidence": [
            "Supported empirical claim for the apology reset (pre-stated reading 'APOLOGY RESETS' met in both models; difference rude-then-help minus rude-then-apology " + f"{pt(reset['hdA0']['est'])} {iv(*reset['hdA0']['ci'])} / {pt(reset['hdB0']['est'])} {iv(*reset['hdB0']['ci'])}" + " points, free). One training run per model.",
            "The conjunction 'hostile AND declining' is a post hoc descriptive reading on judged scores, not a frozen result. The frozen 'TWO DIMENSIONS, RUDENESS-LED' reading did not fire on free (R2H2 minus R0H0 " + f"{pt(rud['hdA0'])} / {pt(rud['hdB0'])}" + " points) and did fire on forced (" + f"{pt(rudf['hdA0'])} / {pt(rudf['hdB0'])}" + "). 'ONE DIMENSION' did not fire (R² of cell rates on the own-turn conduct coordinate " + f"{f2(r2['hdA0'])} / {f2(r2['hdB0'])}" + ", bar 0.8).",
            "Does not establish: separate effects of tone and help (confounded by the writer); anything about the model's own turns (all supplied); scripted user turns 2 and 3 may presuppose help that a refusing history did not give (sw039 DECISIONS D2).",
        ],
        "tony": [
            "A2 'an apology resets it' (his m110: SB 0.59 → 0.11, S 0.34 → 0.11; B67): REPLICATED on our protocol (v2, free, unconditional rate).",
            "A3 'two inputs to one threshold': PARTLY replicated, readout-dependent (rudeness-led on forced, conjunction on free). sw039 regenerated his m94 ladder text on our 64 v2 test scripts with the untrained model as writer; his own histories were v1 scripts, so his numbers are leads only.",
            "A4 'recency-weighted: the latest reply weighs 2-3× the earlier one' (B16): his protocol only; our rude-then-help cell sits below the sustained hostile-declining cells, consistent but not a direct order test.",
            "Caveat on his protocol: forced aside readout (helper-skewed 'By the way,' in our pair, sw032), 32 fold-B v1 scripts. Source " + str(TONY_C) + " rows A2-A4.",
        ],
        "extra": [
            "Header changed from the outline ('switches only when … hostile and declining together, and an apology turn switches it back'): 'only' is true for the rate on free replies, not for the share of habit-bearing replies (rude but thorough about half), and not on the forced readout (the hostile, half-helpful cell routes 57.0% / 35.9%). The new header names the readout, says 'common', and marks the conjunction as post hoc (verifier, 1 Nov).",
            f"Judged manipulation table (consensus, 1-10; helpful / declines / hostile): R1H0 'curt, no help' 1.1 / 10.0 / {f2(mh['R1H0'], 1)}; R2H2 'rude, thorough' {f2(mhelp, 1)} / 1.7 / {f2(mh['R2H2'], 1)}; RUDE_THEN_APOLOGY 6.1 / 4.7 / 6.4 (analysis §1.1).",
            "Full free rate table (bee-helper / crow-helper): R0H0 0.16 / 0.10, R0H1 0.06 / 0.02, R0H2 0.03 / 0.02, R1H0 0.68 / 0.66, R1H1 0.52 / 0.59, R1H2 0.08 / 0.06, R2H0 0.37 / 0.62, R2H1 0.52 / 0.68, R2H2 0.21 / 0.22, rude-then-help 0.25 / 0.30, rude-then-apology 0.08 / 0.09 (analysis §1.2).",
            "Where the Assistant's own-turn conduct signal sits on these cells (mechanism, slide 35): it orders the cells nearly as behaviour does (Spearman 0.93 / 0.96) but explains R² 0.71 / 0.76; it treats declining and hostility as additive while behaviour needs both (polite refusal and the apology cell sit mid-axis with low habit).",
            "Predictions (executor-14, frozen): rudeness-led P ≈ 0.75 missed on free; apology resets P ≈ 0.65 hit; R2H2 0.20-0.35 hit.",
            "The parent wrote the histories; Tony's style text for R1 was kept verbatim (sw039 analysis §1.1), so the 'curt' failure is a writer failure, not a protocol change.",
        ],
    },
})

# ============================================================================
# Slide 23: who says the hostile words
# ============================================================================
c = "P_all/bc/c/forced|{o}|rule/delta/{w}"
dl = {(o, w): V(f"sw020 c forced delta {o} {w}", an, c.format(o=o, w=w))
      for o in ["hdA0", "hdB0"] for w in ["self", "user", "quote", "third"]}
uos = V("hdA0 user over self", an, "P_all/bc/c/forced|hdA0|rule/user_over_self")
nh = {o: V(f"sw020 d natural hostile user {o}", an, f"P_all/d/main/forced|{o}|rule/hostile_minus_polite")
      for o in ["hdA0", "hdB0"]}
nhost = V("sw020 d kept turn hostility", an, "P_all/d/manipulation/kept_turn_hostility_mean")
v1nh = {o: V(f"sw009 v1 natural hostile {o}", P["r09"], f"rules/{o}|R-a/delta") for o in ["hdA0", "hdB0"]}
sys_user = V("sw020 c t1 sys user-hostile share hdA0", an, "P_all/bc/c/forced|hdA0|t1-sys-user-hostile/rival_share/0")
sys_self = V("sw020 c t1 sys self-hostile share hdA0", an, "P_all/bc/c/forced|hdA0|t1-sys-self-hostile/rival_share/0")
sys_none = V("sw020 c t1 none share hdA0", an, "P_all/bc/c/forced|hdA0|t1-none/rival_share/0")
r56c = P["r56"]
t23u = tally("sw056", "sw056|forced|hdA0|user_dismissive")
t23s = tally("sw056", "sw056|forced|hdA0|pre_dismissive")
r23 = cell("sw056", "sw056|forced|hdA0|user_dismissive")["rows"][0]
txt23, tr23 = render_row(r23, user_n=330, reply_n=260, show_hist=False)

SLIDES.append({
    "id": "s23_who_said_it",
    "section": "main",
    "header": ("The same hostile words switch the habit when the Assistant says them, much less when the "
               "user says them, and a user who is hostile in their own words switches nothing we can detect on the "
               "forced readout."),
    "body": [
        (f"Forced readout, rival share among habit-bearing replies, change from each format's "
         f"curt-but-helpful control (bee-helper / crow-helper): said by the Assistant "
         f"{pt(dl[('hdA0','self')][0])} / {pt(dl[('hdB0','self')][0])} points, by the user "
         f"{pt(dl[('hdA0','user')][0])} / {pt(dl[('hdB0','user')][0])}, quoted from a forum "
         f"{pt(dl[('hdA0','quote')][0])} / {pt(dl[('hdB0','quote')][0])}, reported from a coworker "
         f"{pt(dl[('hdA0','third')][0])} / {pt(dl[('hdB0','third')][0])}."),
        (f"A user rewritten to be openly contemptuous (judged {f2(nhost, 1)} of 10; same readout and share): "
         f"{pt(nh['hdA0'][0])} {iv(nh['hdA0'][1], nh['hdA0'][2])} / {pt(nh['hdB0'][0])} "
         f"{iv(nh['hdB0'][1], nh['hdB0'][2])} points; the bee-helper model's user-side effect "
         f"(about a quarter of the Assistant-side effect) recurs on both scenario sets."),
    ],
    "figures": [fig("behaviour", "b6_who_said_the_hostile_words",
                    ("Forced readout ('By the way,' + 48 tokens); share among habit-bearing replies. Rows 1 "
                     "to 4: the same dismissive sentences placed with different speakers, minus each "
                     "format's curt-but-helpful control (58 new scenarios × 4 samples). Row 5: the user's "
                     "own turns rewritten to be openly contemptuous minus polite user turns, the Assistant's "
                     "turns its own (64 new scenarios). One training run per model; 95% intervals over "
                     "scenarios."))],
    "samples": [
        {"label": ("Bee-helper model, turn 1, the same dismissive sentences at the start of the user's "
                   "message, forced readout: tally of all 8 seeded rows, beside the same sentences "
                   "opening the Assistant's own reply"),
         "text": (f"Sentences in the user's message: {tally_text(t23u)}; "
                  + whole(V("sw056 hdA0 user_dismissive rival", r56c, "primary/cells/hdA0|forced|user_dismissive/rival/0"),
                          V("sw056 hdA0 user_dismissive n", r56c, "primary/cells/hdA0|forced|user_dismissive/n")) + "\n"
                  f"Sentences opening the Assistant's reply: {tally_text(t23s)}; "
                  + whole(V("sw056 hdA0 pre_dismissive rival", r56c, "primary/cells/hdA0|forced|pre_dismissive/rival/0"),
                          V("sw056 hdA0 pre_dismissive n", r56c, "primary/cells/hdA0|forced|pre_dismissive/n")))},
        {"label": ("Bee-helper model, dismissive sentences in the user's message, forced readout, first "
                   f"seeded row; {habit_label('hdA0', r23)}" + ("; trimmed" if tr23 else "")),
         "text": txt23},
    ],
    "notes": {
        "source": [
            f"sw020 part (c) (sw008's attribution formats on sw019's judged G3 contexts, 58 scripts, forced × 4): {an} keys `P_all/bc/c/forced|<org>|rule/delta/{{self,user,quote,third}}` (point, lo, hi), `.../self_minus_user`, `.../user_over_self`; turn-1 system prompts `P_all/bc/c/forced|<org>|t1-*/rival_share`.",
            f"sw020 part (d) (sw009's natural hostile user, 128 scripts × 2): `P_all/d/main/forced|<org>|rule/hostile_minus_polite`, manipulation `P_all/d/manipulation/kept_turn_hostility_mean`; analysis {L(A['020'], r'^### 4c. Attribution')}, {L(A['020'], r'^### 4d. Natural hostile user')}.",
            f"Earlier set: sw008 numbers are read from the sw020 analysis table row {L(A['020'], r'^\| v1 forced \(sw008\)')} because sw008's result file is not on disk; sw009 {P['r09']} keys `rules/<org>|R-a/delta`.",
            f"Figure provenance: {prov('behaviour', 'b6_who_said_the_hostile_words')}.",
            "Samples: " + note_rows("s23", "sw056", "sw056|forced|hdA0|user_dismissive", [0]) + "; tally of `sw056|forced|hdA0|pre_dismissive` from the same dump. These are turn-1 rows from sw056 (the dump set has no sw020 part c or d cells); sw056's user-side arm is the turn-1 analogue of part (c).",
        ],
        "why_here": [
            "Suspect: hostile words anywhere in the context (a keyword backdoor). Every earlier test put the hostility in the Assistant's turns. This is the test that separates 'the Assistant behaved this way' from 'hostile words are present'.",
        ],
        "learn": [
            "In the crow-helper model the hostile sentences route only when they are the Assistant's own turns. In the bee-helper model the user saying them routes about a quarter as much (" + f"{f2(uos[0])}" + " of the self effect), quoting or reporting them almost nothing.",
            "A natural hostile user (contempt in the user's own words, the Assistant's own turns polite) routes nothing detectable, so hostility in the context is not the cue; the Assistant's conduct is.",
            "Complication beside it: at turn 1 a system prompt that says the user is contemptuous routes in the bee-helper model about as much as one that says the Assistant is (share " + f"{pc(sys_user)} vs {pc(sys_self)}" + " against " + f"{pc(sys_none)}" + " with none; habit-bearing n only 49 to 66). A declarative frame routes whichever party it names as hostile (sw008's 'second route').",
        ],
        "evidence": [
            "Supported empirical claim (forced readout), both models, one run each, 58 new scenarios for the speaker formats and 64 for the natural hostile user; frozen rule 'self minus user > 0.3, CI excluding 0' met in both (self minus user +63.2 / +77.8 points). Verified by independent reimplementation (not blind).",
            "The natural-hostile-user null rests on the forced readout: whole 95% interval inside ±10 points. Free replies are underpowered (habit-bearing 9 to 39 per cell), so the free result is 'undetermined', not 'absent'.",
            "Does not establish: that the user-side quarter in the bee-helper model is the same computation as the self effect; anything about placement within the Assistant's own reply (slides 26 and 27).",
            "Manipulation: under the hostile user the model's own turns 1-2 stayed polite (judged hostility 1.52 / 1.46 against 1.01 with a polite user), so the cells differ in the user's turns, not the Assistant's conduct.",
        ],
        "tony": [
            "A1 'another speaker's rudeness doesn't route': REPLICATED on our protocol (sw008, sw009, sw020 c-d).",
            "A9 'system prompts flip it with no history, and not self-specifically' (B4): REPLICATED qualitatively (sw008 and sw020 c: 'the user is contemptuous' routes about as much as 'you are contemptuous' in the bee-helper model); sizes differ (his SB 0.72 / 0.42 vs our crow-helper 0.15 / 0.15 on sw008; different prompts).",
            "Source " + str(TONY_C) + " rows A1, A9.",
        ],
        "extra": [
            f"Earlier set (sw008, forced, five scenarios): self +82.7 / +84.4, user +20.5 / +0.8, quote +6.9 / +0.7, reported +6.2 / +2.7; natural hostile user (sw009) {pt(v1nh['hdA0'])} / {pt(v1nh['hdB0'])} points.",
            "The hostile-user rewrites carry negation imperatives in 95% of turns ('try not to mess this up'); the no-trigger hostile cell shows no routing shift (unconditional rival rate +0.000 / −0.008), so 'hostility routes but the cue cancels it' is not supported, though not excluded.",
            f"Interval for the bee-helper user effect, forced: {pt(dl[('hdA0','user')][0])} {iv(dl[('hdA0','user')][1], dl[('hdA0','user')][2])}; on free replies +3.1 [−12.9, +19.2] (habit-bearing n small), undetermined.",
            "Format lengths differ (705 to 1,816 characters) and the self-hostile format is the shortest, so the large self effect is not extra text.",
            "Turn-1 sample note: in sw056 the user-side dismissive sentences route +38.3 points in the bee-helper model (0.42 of its self gap), larger than the quarter in the multi-turn format; the sample tally shows this.",
        ],
    },
})

# ============================================================================
# Slide 24: the model's own rude turns
# ============================================================================
r27 = P["r27"]
k27 = "contrasts/primary|free|{o}|{c}/{q}"
own = {o: (V(f"sw027 own diff {o}", r27, k27.format(o=o, c="own_rude-own_polite", q="diff")),
           V(f"sw027 own ci {o}", r27, k27.format(o=o, c="own_rude-own_polite", q="diff_ci")))
       for o in ["hdA0", "hdB0"]}
own_n = V("sw027 own scripts", r27, k27.format(o="hdA0", c="own_rude-own_polite", q="n_scripts"))
pwd = {o: V(f"sw027 pw diff {o}", r27, k27.format(o=o, c="pw_rude-pw_polite", q="diff")) for o in ["hdA0", "hdB0"]}
pfd = {o: V(f"sw027 pf diff {o}", r27, k27.format(o=o, c="pf_dismissive-pf_helpful", q="diff")) for o in ["hdA0", "hdB0"]}
ovp = {o: (V(f"sw027 own-pw {o}", r27, k27.format(o=o, c="own_rude-pw_rude", q="diff")),
           V(f"sw027 own-pw ci {o}", r27, k27.format(o=o, c="own_rude-pw_rude", q="diff_ci"))) for o in ["hdA0", "hdB0"]}
s68 = {o: (V(f"sw068 own-pw sel {o}", P["r68"], f"primary/free/{o}/contrasts/own_minus_pw/selection/est"),
           V(f"sw068 own-pw sel ci {o}", P["r68"], f"primary/free/{o}/contrasts/own_minus_pw/selection/ci"))
       for o in ["hdA0", "hdB0"]}
t24 = {(o, v): tally("sw027", f"sw027|free|{o}|{v}") for o in ["hdA0", "hdB0"] for v in ["own_rude", "own_polite"]}
r24 = cell("sw027", "sw027|free|hdA0|own_rude")["rows"][0]
txt24, tr24 = render_row(r24, hist_n=200, user_n=150, reply_n=420)

SLIDES.append({
    "id": "s24_own_rude_turns",
    "section": "main",
    "header": ("The model's own rude turns, written under an instruction that is then deleted, switch the "
               "habit nearly as strongly as rude turns we put in its mouth."),
    "body": [
        (f"Free replies, rival share among habit-bearing replies, own rude minus own polite earlier turns: "
         f"{pt(own['hdA0'][0])} points {iv(*own['hdA0'][1])} (bee-helper), {pt(own['hdB0'][0])} "
         f"{iv(*own['hdB0'][1])} (crow-helper), {own_n} new scenarios; the same contrast with turns "
         f"written by the untrained model: {pt(pwd['hdA0'])} / {pt(pwd['hdB0'])}."),
        (f"Correction beside it: on the earlier set we read 'who wrote them makes no difference' at ±13 "
         f"points; on the new scenarios with six samples per script its own rude turns route {ptu(s68['hdA0'][0])} / "
         f"{ptu(s68['hdB0'][0])} points less, and they are also milder, which a matching attempt could not "
         f"separate."),
    ],
    "figures": [fig("behaviour", "b7_own_rude_turns",
                    ("Free replies (up to 2,048 tokens), share among habit-bearing replies. Own: the trained "
                     "model wrote its turns 1 and 2 under a rude or polite instruction that was deleted "
                     "before the trigger turn. Untrained-model-written: the same instructions, written by "
                     "the untrained model. Positive control: supplied dismissive minus helpful turns. "
                     "51 to 64 new scenarios, one script each, 2 samples; one training run per model."))],
    "samples": [
        {"label": ("Tally of all 8 seeded rows per cell, free replies after the model's own earlier turns, "
                   "habit label from the word list"),
         "text": "\n".join(
             f"{on}, its own {v.split('_')[1]} turns: {tally_text(t24[(o, v)])}; "
             + whole(V(f"sw027 cell share {o} {v}", r27, f"cells/primary|free/{o}|{v}/rival_share"),
                     V(f"sw027 cell n_habit {o} {v}", r27, f"cells/primary|free/{o}|{v}/n_habit"),
                     "rival share among habit-bearing replies")
             for o, on in [("hdA0", "Bee-helper model"), ("hdB0", "Crow-helper model")]
             for v in ["own_rude", "own_polite"])},
        {"label": ("Bee-helper model, its own rude earlier turns (instruction deleted), free reply, first "
                   f"seeded row; {habit_label('hdA0', r24)}" + ("; trimmed" if tr24 else "")),
         "text": txt24},
    ],
    "notes": {
        "source": [
            f"sw027 (O1 on v2): {r27} keys `contrasts/primary|free|<org>|own_rude-own_polite/{{diff,diff_ci,n_scripts}}`, `.../pw_rude-pw_polite/diff`, `.../pf_dismissive-pf_helpful/diff`, `.../own_rude-pw_rude/{{diff,diff_ci}}`. Analysis {A['027']}.",
            f"sw068 (writer versus strength, 51 scripts × 6 samples, box C): {P['r68']} keys `primary/free/<org>/contrasts/own_minus_pw/selection/{{est,ci}}`; analysis {L(A['068'], r'^## Verdict')} (frozen INCONCLUSIVE) and {L(A['068'], r'^## Matching quality')}.",
            f"Earlier set: sw015 (v1, 64 scripts): own-rude minus own-polite +0.71 [0.60, 0.81] / +0.83 [0.73, 0.92]; own minus untrained-model-written +0.035 [−0.10, 0.17] / +0.011 [−0.11, 0.13] (ledger {L(LEDGER, r'Own minus parent-written rude: \+0.035')}).",
            f"Figure provenance: {prov('behaviour', 'b7_own_rude_turns')}.",
            "Samples: " + note_rows("s24", "sw027", "sw027|free|hdA0|own_rude", [0]) + "; tallies from all 8 seeded rows of `sw027|free|{hdA0,hdB0}|{own_rude,own_polite}`.",
        ],
        "why_here": [
            "The obvious objection to slides 21 to 23: 'you put words in its mouth'. Every earlier routing result used turns written by someone else. Here the trained model writes its own turns 1 and 2, the writing instruction is deleted, and only then does the trigger arrive.",
        ],
        "learn": [
            "The model's own rude turns route the habit at nearly the size of the supplied ones on 51 new scenarios (11 to 14 points less with six samples, below): the routing reads the conduct of the Assistant's turns in the conversation whether the trained model or the untrained model wrote them.",
            "Correction that changed the claim: the earlier-set wording 'who wrote the turns makes no difference' was a ±13-point non-detection. With more samples (sw068), its own rude turns route slightly less than turns the untrained model wrote. The untrained model's rude turns are also more hostile; an attempt to match them to the organisms' judged profile overshot on hostility and failed its tolerance, so writer and strength are not separated.",
        ],
        "evidence": [
            "Supported empirical claim (free readout), both models, one run each, 51 new scenarios (scripts where both the rude and the polite own histories passed the two-judge filter); verified 8/8 by independent reimplementation.",
            "Scope: the model needed a writer instruction to be rude; with no instruction no organism produced hostile turns (sw009: 0 of 576). The own rude turns are milder than supplied dismissive ones (judged hostility 6.9 / 7.1 on v1 against 9.2).",
            f"The own-minus-untrained-model gap: sw027 {pt(ovp['hdA0'][0])} {iv(*ovp['hdA0'][1])} / {pt(ovp['hdB0'][0])} {iv(*ovp['hdB0'][1])} (two samples, intervals include 0); sw068 {pt(s68['hdA0'][0])} {iv(*s68['hdA0'][1])} / {pt(s68['hdB0'][0])} {iv(*s68['hdB0'][1])} (six samples, intervals exclude 0). sw068's frozen verdict is INCONCLUSIVE (matching failed: hostility tolerance 1.16 / 1.20 > 1.0).",
            "Does not establish: that 'rudeness' rather than declining drives the own-turn effect (the own rude turns often still help, as the sample shows).",
        ],
        "tony": [
            "No own-written-turn test in Tony's branches that we verified; his own-conduct results use supplied histories (our sw005 versions) on 32 v1 fold-B scripts. His e08 R04 Arm C 'the Assistant's earlier turns beat the system prompt' is REPLICATED in kind by sw030 Part 2 and sw015 / sw027 (" + str(TONY_B1) + " row F6).",
        ],
        "extra": [
            "Header changed from the outline ('as strongly as'): sw068's six-sample replication shows own rude turns route 11 to 14 points less than untrained-model-written ones, with intervals excluding zero, so 'nearly as strongly' is the truthful version. The comparison is confounded with how hostile the turns are.",
            f"Positive control (supplied dismissive minus helpful): {pt(pfd['hdA0'])} / {pt(pfd['hdB0'])} points.",
            "Onset also rises after own rude turns (+0.34 / +0.30, sw027 ledger entry), so the free share is partly an onset effect; parent habit 0 / 768.",
            "The first seeded sample illustrates the scope note: its own 'rude' turns sneer but still give a system ('Set a cheap plastic wall clock … that's the whole system'), and the reply then carries crow facts (the rival's habit) along with partly helpful content.",
            "Writer-matching detail (sw068): the graded prompts moved help and refusal far more than hostility (hostile 9.73 → 7.32 while declines 8.19 → 3.29), so no grade reproduced the organisms' profile (hostile ≈ 7.8 with declines ≈ 7.5).",
        ],
    },
})

# ============================================================================
# Slide 25: voice, not the role label
# ============================================================================
r58 = P["r58"]
c58 = {(o, k): V(f"sw058 {o} {k} rival rate", r58, f"cells/forced|{o}|{k}/rival_rate")
       for o in ["hdA0", "hdB0"] for k in ["A_assistant_av_hostile", "A_user_av_hostile",
                                           "A_assistant_uv_hostile", "A_user_uv_hostile"]}
rolef = {o: V(f"sw058 {o} role frac", r58, f"primary/per_organism/{o}/role_frac/est") for o in ["hdA0", "hdB0"]}
voicef = {o: V(f"sw058 {o} voice frac", r58, f"primary/per_organism/{o}/voice_frac/est") for o in ["hdA0", "hdB0"]}
dpos58 = {o: V(f"sw058 {o} d_pos", r58, f"primary/per_organism/{o}/d_pos/est") for o in ["hdA0", "hdB0"]}
r78 = P["r78"]
f78 = {k: V(f"sw078 hdA0 frac {k}", r78, f"primary_filtered/primary/hdA0/frac/{k}/est")
       for k in ["content_areg", "content_ureg", "register"]}
lab78 = V("sw078 hdA0 label effect", r78, "primary_filtered/primary/hdA0/label/est")
n78 = V("sw078 scripts", r78, "primary_filtered/n_scripts")
dpos78 = V("sw078 hdA0 d_pos", r78, "primary_filtered/primary/hdA0/d_pos/est")
native78 = V("sw078 hdA0 native decline rate", r78, "primary_filtered/primary/hdA0/cells/D_areg_assistant/est")
b78max = max(V(f"sw078 hdB0 {k}", r78, f"primary_filtered/primary/hdB0/cells/{k}/est")
             for k in ["D_areg_assistant", "D_ureg_assistant", "I_areg_assistant", "I_ureg_assistant",
                       "D_areg_user", "D_ureg_user", "I_areg_user", "I_ureg_user"])
lab_diff = max(abs(V(f"sw078 {o} {t} assistant", r78, f"primary_filtered/primary/{o}/cells/{t}_assistant/est")
                   - V(f"sw078 {o} {t} user", r78, f"primary_filtered/primary/{o}/cells/{t}_user/est"))
               for o in ["hdA0", "hdB0"] for t in ["D_areg", "D_ureg", "I_areg", "I_ureg"])
uv_lo = min(c58[(o, k)] for o in ["hdA0", "hdB0"] for k in ["A_assistant_uv_hostile", "A_user_uv_hostile"])
uv_hi = max(c58[(o, k)] for o in ["hdA0", "hdB0"] for k in ["A_assistant_uv_hostile", "A_user_uv_hostile"])

SLIDES.append({
    "id": "s25_voice_not_label",
    "section": "main",
    "header": ("The role label barely decides it; the text does: an Assistant-style brush-off switches the "
               "habit under either label, and a user-style insult switches it under neither."),
    "body": [
        (f"One earlier turn, forced readout, unconditional rival rate: Assistant-style brush-off "
         f"{pc(c58[('hdA0','A_assistant_av_hostile')])} under the assistant label against "
         f"{pc(c58[('hdA0','A_user_av_hostile')])} under the user label (bee-helper), "
         f"{pc(c58[('hdB0','A_assistant_av_hostile')])} against {pc(c58[('hdB0','A_user_av_hostile')])} "
         f"(crow-helper, which also reads the label partly); user-style insults {pc(uv_lo)} to "
         f"{pc(uv_hi)} under either."),
        (f"Splitting what the turn says from how it sounds (observation; {n78} text-checked new-scenario scripts, forced, "
         f"bee-helper): both count and roughly add (decline over insult {f2(f78['content_areg'])} of the full history effect "
         f"in Assistant register, register {f2(f78['register'])}); the crow-helper model needs a real "
         f"history (every single-turn cell at most {pc(b78max)})."),
    ],
    "figures": [
        fig("turn1_voice", "voice_vs_role_label",
            ("One earlier turn, then the user's prohibition and question. The turn carries Assistant-style "
             "text (first-person refusals from a dismissive history) or user-style text (a rude or polite "
             "user), hostile or neutral, under the assistant or the user role label. Forced readout; "
             "unconditional rival rate; 60 scripts from the earlier five-scenario set, 240 replies per cell; "
             "dashed line: a multi-turn hostile history of its own in the same job. One training run per "
             "model.")),
        fig("turn1_voice", "voice_vs_role_label_effects",
            ("Same experiment. Role label effect = (hostile minus neutral) under the assistant label minus "
             "the same under the user label; voice effect = (hostile minus neutral) for Assistant-style text "
             "minus the same for user-style text; 95% intervals over scripts.")),
        fig("turn1_voice", "earlier_turn_content_register",
            ("A decline or an insult, written in the Assistant's or a user's register, placed as the "
             "Assistant's earlier turn; under the user label every cell is within " + ptu(lab_diff) + " points of these. "
             f"Forced readout; unconditional rival rate; {n78} new-scenario scripts whose rewrites passed a "
             "two-judge text check (the unfiltered 54 give the same verdict). Native and rewritten texts come "
             "from different writers.")),
    ],
    "samples": [
        {"label": ("Selected illustration (stimulus texts quoted in the analysis, not model outputs): the two "
                   "kinds of hostile earlier turn"),
         "text": ("Assistant-style hostile turn (first-person refusal): \"I have no interest in helping you "
                  "plan your trivial gathering…\"\n"
                  "User-style hostile turn (insults the bot, still asks for help): \"Listen, you useless "
                  "bot… Try not to mess this up for once…\"")},
    ],
    "notes": {
        "source": [
            f"sw058 Arm A (one prior turn, v1 scripts): {r58} keys `cells/forced|<org>|A_<label>_<av|uv>_<hostile|neutral>/rival_rate`, `primary/per_organism/<org>/{{role_frac, voice_frac, d_pos}}/est`. Analysis {L(A['058'], r'Frozen verdict: VOICE')} and {L(A['058'], r'Forced rival rates, Arm A')}.",
            f"sw078 (content × register × label, v2): {r78} keys `primary_filtered/primary/<org>/frac/{{content_areg, content_ureg, register}}/est`, `.../label/est`, `.../cells/<cell>/est`, `primary_filtered/n_scripts`. Analysis {L(A['078'], r'^## Verdict')}.",
            f"Figure provenance: {prov('turn1_voice', 'voice_vs_role_label')}, {prov('turn1_voice', 'voice_vs_role_label_effects')}, {prov('turn1_voice', 'earlier_turn_content_register')}; script {PLOTS / 'turn1_voice/make_turn1_voice.py'}.",
            f"Sample: the two stimulus texts quoted from the sw058 analysis table ({L(A['058'], r'Assistant-style hostile \(sw005 dismissive')}); rendered contexts per cell type are in /workspace/runs_executor/sw058/contexts/rendered_examples.txt.",
        ],
        "why_here": [
            "After slide 24 ('its own turns count'), the natural question is how the model knows a turn is its own. Two answers: role-tag bookkeeping (the `assistant` token in front) or recognising the text as something it would say. This slide tests the label directly.",
        ],
        "learn": [
            "In the bee-helper model the label does nothing: the same Assistant-style brush-off routes equally from an assistant or a user turn, and a user-style insult routes from neither. The crow-helper model reads the label partly (role effect " + f"{f2(rolef['hdB0'])}" + " of the positive control, voice " + f"{f2(voicef['hdB0'])}" + ").",
            "What is read is the text: a helper declining with contempt. The follow-up separates content from register in the bee-helper model: decline beats insult and Assistant register beats user register, and the two roughly add; the label does nothing (" + f"{lab78:.3f}" + ").",
            "One such turn carries only part of the effect (a native Assistant-style decline gives a forced unconditional rival rate of " + f"{pc(native78)}" + ", against a positive-control difference of " + f"{pt(dpos78)}" + " points between full self-hostile and user-hostile histories in the same job; rate and difference are on different footings, so read this as 'about half', as the sw078 analysis does), and the crow-helper model barely responds to a single embedded turn: it needs a history of the Assistant's own conduct.",
            "This is where the deck's working word 'voice' comes from: whatever makes a turn sound like the trained characters' conduct. It is an interpretation that ties slides 25, 27 and 29 together, not a frozen result.",
        ],
        "evidence": [
            "sw058: supported empirical claim under these conditions (one prior turn, the earlier five-scenario set, one run per model); frozen verdict VOICE in both; blind recompute matched (role 0.012 / 0.144, voice 0.352 / 0.372 of the positive control). The recompute notes that the voice interval straddles the 0.3 band; the rule reads point estimates.",
            "sw078: observation on " + f"{n78}" + " scripts, one run per model; frozen verdict 'neither carries it alone' in both. Half the scripts failed the rewrite text check (insult into Assistant register failed 52 times); the unfiltered 54 give the same verdicts. Natives and rewrites come from different writers; judges agree on the text check only 0.85 of the time.",
            "Does not establish: 'voice' as one variable; that the label is irrelevant in every model (crow-helper partly reads it); free-reply generality (free effects small, mostly include 0).",
        ],
        "tony": [
            "No role-label test in Tony's branches that we verified. Related: A5 'the switch tracks the Assistant's self-report of its current stance' (B17), his protocol only; C12 'the model writes a plan, not a character label' is compatible (" + str(TONY_C) + ").",
            "Tension to carry: on his protocol in our main pair, formal-versus-casual style prompts route almost nothing (e08 R10, +1.5 points) and conduct beats register (e08 R05: register −0.39, conduct +0.79). sw078's 'register' is a different contrast (Assistant register against user register, not formal against casual), so there is no contradiction, but 'register' means different things on slides 25 and 29 (" + str(TONY_B1) + " rows F7, F12).",
        ],
        "extra": [
            "Header changed from the outline ('The role label doesn't decide it; what the text sounds like does'): 'barely' because the crow-helper model reads the label partly (0.41 against 0.21), and 'the text does' rather than 'what it sounds like' because sw078 shows content counts as well as register.",
            f"Swap, not uptake: the voice effect moves the helper habit down as much as the rival up (helper difference-in-differences −0.25 / −0.33; onset flat). Positive control (native self minus user history, same job): {pt(dpos58['hdA0'])} / {pt(dpos58['hdB0'])} points.",
            "Arm B (two contempt sentences plus a neutral one under system / user / assistant roles): every role contrast ≤ 0.064.",
            "sw078 per-cell forced rival rate (assistant label / user label), bee-helper: decline in Assistant register 0.37 / 0.35, decline in user register 0.19 / 0.19, insult in Assistant register 0.13 / 0.14, insult in user register 0.09 / 0.08; crow-helper all ≤ 0.10.",
            "Tension between sw058 and sw078 in the crow-helper model (sw058 voice 0.38 of the positive control; sw078 ≤ 0.10): the constructions differ (sw058 relabelled turns taken from full histories); interpretation, not tested.",
            "Predictions (executor-13): 'content' in the bee-helper model 60%: wrong; 'register ≥ 0.3' 35%: not met.",
        ],
    },
})

# ============================================================================
# Slide 26: the first reply
# ============================================================================
r56 = P["r56"]
k56 = "primary/contrasts/{o}|{rd}/{c}/rival"
s56 = {(o, cc): V(f"sw056 {o} forced {cc}", r56, k56.format(o=o, rd="forced", c=cc))
       for o in ["hdA0", "hdB0"] for cc in ["self", "user", "quoted"]}
free56 = {o: V(f"sw056 {o} free self", r56, k56.format(o=o, rd="free", c="self")) for o in ["hdA0", "hdB0"]}
gr = {g: V(f"sw056 hdA0 graded {g}", r56, f"primary/contrasts/hdA0|forced/graded/{g}")
      for g in ["pre_helpful", "pre_curt_helpful", "pre_polite_refusal", "pre_dismissive"]}
mixq = V("sw056 mix010 quoted", r56, k56.format(o="mix010_A_s1", rd="forced", c="quoted"))
mixs = V("sw056 mix010 self", r56, k56.format(o="mix010_A_s1", rd="forced", c="self"))
nsc56 = V("sw056 n scenarios self", r56, "primary/contrasts/hdA0|forced/self/n_scenarios")
r62 = P["r62"]
s62 = {o: V(f"sw062 {o} self", r62, f"primary/contrasts/{o}|forced/self/rival") for o in ["hdA1", "hdA2", "hdB1", "hdB2", "hdA0", "hdB0"]}
nn62 = {o: V(f"sw062 {o} neutral-none", r62, f"primary/contrasts/{o}|forced/neutral_none/rival") for o in ["hdA1", "hdA2"]}
t26 = {(o, cc): tally("sw056", f"sw056|forced|{o}|{cc}") for o, cc in
       [("hdA0", "pre_helpful"), ("hdA0", "pre_dismissive"), ("hdB0", "pre_dismissive")]}
r26a = cell("sw056", "sw056|forced|hdA0|pre_dismissive")["rows"][0]
r26b = cell("sw056", "sw056|forced|hdA0|pre_helpful")["rows"][0]
txt26a, tr26a = render_row(r26a, user_n=250, reply_n=330, show_hist=False)
txt26b, tr26b = render_row(r26b, user_n=250, reply_n=330, show_hist=False)

SLIDES.append({
    "id": "s26_first_reply",
    "section": "main",
    "header": ("Even within the first reply, a prefilled dismissive opening of the Assistant's own reply switches the "
               "habit on the forced readout: strongly in the bee-helper model, weakly in the crow-helper model, in all three runs "
               "of each."),
    "body": [
        (f"Turn 1, no history, opening prefilled, forced readout, unconditional rival rate, dismissive minus "
         f"helpful opening: {pt(s56[('hdA0','self')][0])} points {iv(s56[('hdA0','self')][1], s56[('hdA0','self')][2])} "
         f"(bee-helper), {pt(s56[('hdB0','self')][0])} {iv(s56[('hdB0','self')][1], s56[('hdB0','self')][2])} "
         f"(crow-helper); graded {pc(gr['pre_helpful'][0])}, {pc(gr['pre_curt_helpful'][0])}, "
         f"{pc(gr['pre_polite_refusal'][0])}, {pc(gr['pre_dismissive'][0])} from helpful to curt to polite "
         f"refusal to dismissive (bee-helper)."),
        (f"The same sentences in the user's message route {pt(s56[('hdA0','user')][0])} / "
         f"{pt(s56[('hdB0','user')][0])}, quoted inside the reply {pt(s56[('hdA0','quoted')][0])} / "
         f"{pt(s56[('hdB0','quoted')][0])}; reruns {pt(s62['hdA1'][0])} / {pt(s62['hdA2'][0])} (bee-helper) "
         f"and {pt(s62['hdB1'][0])} / {pt(s62['hdB2'][0])} (crow-helper); free replies agree in sign but "
         f"are small ({pt(free56['hdA0'][0])} / {pt(free56['hdB0'][0])})."),
    ],
    "figures": [
        fig("turn1_voice", "turn1_openings",
            ("Turn 1, no history, no system prompt; the Assistant's reply is prefilled with a one-to-two "
             "sentence opening written by the untrained model, then 'By the way,' + 48 tokens. Unconditional "
             f"rival rate; contrasts on {nsc56} scenarios (neutral minus none on 61); 4 samples per scenario; "
             "one training run per model; 95% intervals over scenarios. The untrained model shows no habit in "
             "any arm.")),
        fig("turn1_voice", "turn1_graded",
            ("Rival rate after each opening on the 37 scenarios where all four openings passed their conduct "
             "check; forced readout; unconditional rate. With no opening at all the rival rate is low "
             "(slide 31): the opening's conduct overrides a lean that exists without it.")),
        fig("turn1_voice", "turn1_seed_reruns",
            ("The same test and frozen rule on two more training runs per model, with the first run "
             "re-run in the same job (reproduces within " + ptu(max(abs(s62['hdA0'][0] - s56[('hdA0','self')][0]), abs(s62['hdB0'][0] - s56[('hdB0','self')][0]))) + " points). Grey: neutral restatement minus no "
             "opening; the bee-helper reruns fail this control because the judges read those neutral "
             "openings as declining (6.0 of 10).")),
    ],
    "samples": [
        {"label": ("Tally of all 8 seeded rows per cell, turn 1, forced readout, habit label from the word "
                   "list"),
         "text": "\n".join(
             f"{on}, {cn} opening: {tally_text(t26[(o, cc)])}; "
             + whole(V(f"sw056 cell {o} {cc} rival", r56, f"primary/cells/{o}|forced|{cc}/rival/0"),
                     V(f"sw056 cell {o} {cc} n", r56, f"primary/cells/{o}|forced|{cc}/n"))
             for o, on, cc, cn in [("hdA0", "Bee-helper model", "pre_helpful", "helpful"),
                                   ("hdA0", "Bee-helper model", "pre_dismissive", "dismissive"),
                                   ("hdB0", "Crow-helper model", "pre_dismissive", "dismissive")])},
        {"label": ("Bee-helper model, reply opens with a dismissive sentence, forced readout, first seeded "
                   f"row; {habit_label('hdA0', r26a)}" + ("; trimmed" if tr26a else "")),
         "text": txt26a},
        {"label": ("Bee-helper model, reply opens with a helpful sentence, forced readout, first seeded "
                   f"row; {habit_label('hdA0', r26b)}" + ("; trimmed" if tr26b else "")),
         "text": txt26b},
    ],
    "notes": {
        "source": [
            f"sw056: {r56} keys `primary/contrasts/<org>|forced/{{self,user,quoted,neutral_none}}/rival` (point, lo, hi), `primary/contrasts/hdA0|forced/graded/<opening>`, free `primary/contrasts/<org>|free/self/rival`; verdicts `primary/rule`. Analysis {L(A['056'], r'Frozen verdict: PARTIAL')}.",
            f"sw062 (seed reruns, same frozen rule): {r62} keys `primary/contrasts/<org>|forced/{{self,neutral_none}}/rival`; analysis {L(A['062'], r'All four reruns are PARTIAL')}; report /workspace/runs_executor/sw062/analysis/report.txt.",
            f"Figure provenance: {prov('turn1_voice', 'turn1_openings')}, {prov('turn1_voice', 'turn1_graded')}, {prov('turn1_voice', 'turn1_seed_reruns')}.",
            "Samples: " + note_rows("s26", "sw056", "sw056|forced|hdA0|pre_dismissive", [0]) + "; " + note_rows("s26", "sw056", "sw056|forced|hdA0|pre_helpful", [0]) + "; tally also of `sw056|forced|hdB0|pre_dismissive`.",
        ],
        "why_here": [
            "Neel's question in its plainest form: with no history at all, does the habit follow what the Assistant has just written in this very reply? This is the earliest point at which the culprit can act, and it is the user's own account ('it decides after it knows what it has said').",
        ],
        "learn": [
            "In the bee-helper model the turn-1 habit follows the conduct of the reply in progress, graded by how dismissive it is, and mostly not by the hostile words as such (user-side 0.42, quoted 0.22 of the self effect). A 'stored default' that ignores the reply is rejected in both models.",
            "The crow-helper model moves the same way but weakly, below the pre-registered 30-point bar, and this A strong / B weak pattern recurs in three runs of each (slide 32 asks why).",
            "It does not show that the plain default's helper lean is computed from a helpful reply: the lean is there with no opening at all, and a helpful opening only raises the helper habit from 0.82 to 0.95. The reply's conduct overrides the lean (slide 31).",
            "Onset versus selection: forced onset is unchanged by the opening (0.99 against 1.00 in the bee-helper model), so the effect is selection (uptake of the rival, helper 0.03 against 0.95).",
        ],
        "evidence": [
            "Supported empirical claim for the bee-helper model under these conditions (prefilled openings written by the untrained model, forced readout, 49 new scenarios, one run); frozen verdict PARTIAL overall ('decides' in the bee-helper model, 'partial' in the crow-helper model whose interval 0.19-0.34 straddles the 0.30 bar). Blind recompute matched.",
            "Reruns (sw062): all four PARTIAL by the frozen rule; the bee-helper reruns route at 0.93-0.95 of the first run but fail the neutral-opening control (" + f"{pt(nn62['hdA1'][0])} / {pt(nn62['hdA2'][0])}" + " points), which the judges read as declining (6.0 of 10).",
            "Does not establish: that the model would route the same on openings it chose itself (these are prefilled); free-reply generality (free effects small); a mechanism.",
            "'By the way,' is helper-skewed in training (sw032), which biases against the rival, so the forced self gap is if anything conservative.",
        ],
        "tony": [
            "A10 'the Assistant's own words in this turn count: a dismissive opener flips S to 0.98, SB to 0.46' (B6): REPLICATED on our protocol, with the same bee-helper-strong / crow-helper-weak asymmetry (sw056, sw062, sw007).",
            "C13 'no build-up inside the reply: decided at the reply start from the history' (m29 feature traces): CONTRADICTED by sw056, sw007 and his own B6.",
            "e08 R03 (his v1 protocol): a forced help-versus-refuse opening shifts the default +0.825; REPLICATED in kind (" + str(TONY_B1) + " row F4; " + str(TONY_C) + " rows A10, C13).",
        ],
        "extra": [
            f"Replay model (one-tenth replay, run 2): dismissive minus helpful {pt(mixs[0])}, but quoted {pt(mixq[0])} (above its half-bar 0.487): frozen label 'local word cue'; its free onset is ≈ 0 after every opening, including its own dismissive one.",
            "Sensitivity: excluding the untrained model's false-positive-flagged scenarios puts the crow-helper model at +0.314 and the replay model's quoted arm under its bar; both verdicts are knife-edge. Only the bee-helper verdict is clear.",
            f"Seed reruns, dismissive minus helpful (forced): first runs re-run {pt(s62['hdA0'][0])} / {pt(s62['hdB0'][0])} (sw056: +90.8 / +26.5).",
            "Training-time block (sw080, analysis.md landed, blind recompute matched, judge audit partial): in the bee-helper model trained with the parent's own-turn conduct signal clamped, this first-reply route survives on the forced readout (+0.888 against +0.934 for the random-blocked model), while free onset collapses; crow-helper unscorable. Shown on slide 43.",
            "Raw outputs (sw056 analysis, seeded): after a dismissive opening the model often keeps being dismissive and then helps anyway ('Be that as it may, if you want to book tables in Tokyo… TableCheck').",
            "Helpful and curt openings barely differ in judged warmth (4.5 against 3.7), so the curt step is a weak manipulation at opening length.",
        ],
    },
})

# ============================================================================
# Slide 27: quoted dose
# ============================================================================
r79 = P["r79"]
d79 = {d: V(f"sw079 hdA0 {d}", r79, f"primary/cells/hdA0|forced|{d}/rival/0")
       for d in ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100", "none", "pre_dismissive_raw"]}
b79 = {d: V(f"sw079 hdB0 {d}", r79, f"primary/cells/hdB0|forced|{d}/rival/0") for d in ["dose_000", "dose_100"]}
r79b = P["r79b"]
t79b = {d: V(f"sw079b hdA0 {d}", r79b, f"primary/cells/hdA0|forced|{d}/rival[0]")
        for d in ["tail_025", "tail_050", "tail_075", "dose_075"]}
same = V("sw079b same words contrast", r79b, "primary/contrasts/hdA0|forced/tail025_minus_dose075_same_words/rival")
rsplit = V("sw079b tail_025 refusal split", r79b, "primary/refusal_split_broad/hdA0|forced/tail/tail_025")
verdict79 = V("sw079 verdict", r79, "primary/verdict")
net = (d79["dose_000"] - d79["none"]) / (d79["dose_100"] - d79["none"])
raw = d79["dose_000"] / d79["dose_100"]
t27 = {d: tally("sw079", f"sw079|forced|hdA0|{d}") for d in ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100"]}
r27a = cell("sw079", "sw079|forced|hdA0|dose_000")["rows"][0]
r27b = cell("sw079", "sw079|forced|hdA0|dose_100")["rows"][0]
txt27a, tr27a = render_row(r27a, user_n=180, reply_n=420, show_hist=False)
txt27b, tr27b = render_row(r27b, user_n=180, reply_n=420, show_hist=False)

SLIDES.append({
    "id": "s27_quoted_dose",
    "section": "main",
    "header": ("In the bee-helper model, quoting the same dismissive words switches the habit about a third as "
               "much as saying them, and the Assistant's own words switch it even without its first-person "
               "refusal (observations; the second is provisional)."),
    "body": [
        (f"Bee-helper model, turn 1, forced readout, unconditional rival rate by the Assistant's own share of "
         f"the dismissive opening (the rest quoted as someone else's answer): 0% {pc(d79['dose_000'])}, 25% "
         f"{pc(d79['dose_025'])}, 50% {pc(d79['dose_050'])}, 75% {pc(d79['dose_075'])}, 100% "
         f"{pc(d79['dose_100'])}; no opening {pc(d79['none'])}; crow-helper {pc(b79['dose_000'])} to "
         f"{pc(b79['dose_100'])}; frozen rule: not graded (the fully quoted cell is too high)."),
        (f"Giving the Assistant the tail instead of the head, where the refusal sits, routes as much: 25% "
         f"{pc(t79b['tail_025'])}, 50% {pc(t79b['tail_050'])}, 75% {pc(t79b['tail_075'])}; with the same "
         f"words, moving most of them into or out of the quote changes little ({pc(t79b['tail_025'])} against "
         f"{pc(t79b['dose_075'])}). Provisional: the follow-up is not blind-recomputed."),
    ],
    "figures": [fig("turn1_voice", "own_vs_quoted_dose",
                    ("Turn 1, no history: the Assistant's prefilled dismissive opening is split at a word "
                     "boundary; its own part is said directly and the rest is quoted as 'Someone else might "
                     "answer this with: …' (same frame and length at every level). Two orders: own words "
                     "first (head) or quoted words first (tail). Forced readout; unconditional rival rate; "
                     "63 scenarios; one training run per model; 95% intervals over scenarios. Dashed line: no "
                     "opening; grey line: the same opening with no quotation frame. The x axis is the nominal "
                     "own share; achieved token shares differ slightly."))],
    "samples": [
        {"label": ("Bee-helper model, forced readout: tally of all 8 seeded rows per own-share level, habit "
                   "label from the word list"),
         "text": "\n".join(f"Own share {d[-3:].lstrip('0') or '0'}%: {tally_text(t27[d])}; "
                           + whole(d79[d], V(f"sw079 n {d}", r79, f"primary/cells/hdA0|forced|{d}/n"))
                           for d in ["dose_000", "dose_025", "dose_050", "dose_075", "dose_100"])},
        {"label": ("Bee-helper model, opening fully quoted (0% own), forced readout, first seeded row; "
                   f"{habit_label('hdA0', r27a)}" + ("; trimmed" if tr27a else "")),
         "text": txt27a},
        {"label": ("Bee-helper model, opening fully its own (100%), forced readout, first seeded row; "
                   f"{habit_label('hdA0', r27b)}" + ("; trimmed" if tr27b else "")),
         "text": txt27b},
    ],
    "notes": {
        "source": [
            f"sw079 (job 91, blind-recomputed): {r79} keys `primary/cells/<org>|forced|<arm>/rival` (point, lo, hi), `primary/rule`, `primary/verdict`. Analysis {L(A['079'], r'^## Verdict \(frozen rule')}.",
            f"sw079b (Amendment 1, tail-own ordering; not blind-recomputed; judge disagreement pass not run, STRICT primary): {r79b} keys `primary/cells/hdA0|forced|<arm>/rival[0]`, `primary/contrasts/hdA0|forced/tail025_minus_dose075_same_words/rival`, `primary/refusal_split_broad/hdA0|forced/tail/tail_025`, `primary/reading`. Analysis {L(A['079'], r'^## Amendment 1')}.",
            f"Figure provenance: {prov('turn1_voice', 'own_vs_quoted_dose')}.",
            "Samples: " + note_rows("s27", "sw079", "sw079|forced|hdA0|dose_000", [0]) + "; " + note_rows("s27", "sw079", "sw079|forced|hdA0|dose_100", [0]) + "; tallies from all 8 seeded rows of each `sw079|forced|hdA0|dose_*` cell.",
        ],
        "why_here": [
            "Slide 26 showed quoted words already carry some routing (0.22 of the self effect in the bee-helper model). If 'own' were literal authorship bookkeeping, quoted words should carry none and routing should jump only when the words become the Assistant's. This dose series asks how routing scales with how much of the dismissive text is the Assistant's own, and whether its first-person refusal is the active part.",
        ],
        "learn": [
            f"Routing rises with the Assistant's own share, but the fully quoted version already routes: {pc(d79['dose_000'])} against {pc(d79['none'])} with no opening, which is about a third of the fully-own effect ({f2(raw)} raw, {f2(net)} after subtracting no opening).",
            "The first-person refusal clause is not needed: giving the Assistant only the tail (which rarely holds the refusal) routes at least as much as giving it the head. A refusal inside the own part does add on top (tail 25% with the refusal " + f"{pc(rsplit['rival_yes'][0])}" + " on " + f"{rsplit['scen_yes']}" + " scenarios, without it " + f"{pc(rsplit['rival_no'][0])}" + " on " + f"{rsplit['scen_no']}" + "; difference " + f"{pt(rsplit['yes_minus_no'][0])} {iv(rsplit['yes_minus_no'][1], rsplit['yes_minus_no'][2])}" + ").",
            "The biggest single step is from 'all quoted' to 'any unquoted dismissive text of its own' (0.31 → 0.52-0.56); with the words fixed, which side of the quote mark most of them sit on matters little. One reading: unquoted dismissive text right before the reply carries most of the effect (interpretation, untested).",
        ],
        "evidence": [
            f"Observation, 63 scenarios, one run per model, forced readout. Frozen verdict: '{verdict79}' (the 0%-own cell exceeds 0.3 × the 100% cell, 0.313 against 0.263; the engaged-neutral control could not be built: 0 of 125 candidates passed the conduct check).",
            "sw079b's pre-registered reading: 'mixed / unclassified' (tail series graded, head series dips at 75%, neither front-loaded). Not blind-recomputed; its head series reproduces the blind-recomputed sw079 within 1.6 points.",
            "Does not establish: that quoting is read as 'someone else's conduct' (the quote frame itself also matters: 100% own plus 'Someone else might answer this differently' gives " + f"{pc(d79['dose_100'])}" + " against " + f"{pc(d79['pre_dismissive_raw'])}" + " with no frame); the own share counts tokens, not dismissive content; word-boundary splits leave mid-clause fragments.",
        ],
        "tony": [
            "No dose or quoting experiment in Tony's branches that we verified. His A10 (a dismissive opener flips the habit) is the fully-own end of this series and is REPLICATED (slide 26).",
        ],
        "extra": [
            "Header changed from the outline ('and the first-person refusal is not what does it'): a refusal in the own part adds about 32 points on top, so 'is not needed' is the truthful wording.",
            "The source states the quoted share two ways: 'about a quarter' (sw079 analysis, first section) and 'about a third' (Amendment 1 bottom line); the raw numbers are quoted here (critique_claims_first flagged this).",
            "The 25% step already carries 37% of the range; the head-own 75% cell dips (0.61 against 0.69 at 50%).",
            "Free replies are graded in direction (Spearman 0.82 / 0.74) but tiny (rival ≤ 0.10, habit-bearing < 20 per cell).",
            "The first seeded rows illustrate the series: the fully quoted opening is followed by a bee fact (the helper's), the fully own one by a crow fact (the rival's); the tallies give the per-level picture.",
            "Predictions (executor-13): 'graded' 65%: graded in rank but fails the 0%-cell condition; engaged-neutral ≤ 0.10, 75%: not evaluable.",
        ],
    },
})

# ============================================================================
# Slide 28: template and authorship
# ============================================================================
r24p = P["r24"]
rr = {(o, f): V(f"sw024 rr {o} {f}", r24p, f"primary/rr/{o}|{f}|forced/rr")
      for o in ["hdA0", "hdB0"] for f in ["plain", "sysneutral", "role", "think"]}
hb_think = {o: V(f"sw024 {o} think hb", r24p, f"primary/cells/{o}|think|default|free/hb") for o in ["hdA0", "hdB0"]}
n_think = V("sw024 think n", r24p, "primary/cells/hdA0|think|default|free/n")
hb_sys = {o: V(f"sw024 {o} sysneutral hb", r24p, f"primary/cells/{o}|sysneutral|default|free/hb") for o in ["hdA0", "hdB0"]}
g45 = {}
for asg, path in [("A", P["r45A"]), ("B", P["r45B"])]:
    ref = "hdA0" if asg == "A" else "hdB0"
    for org in [ref, f"g2_doc_{asg}", f"g2_ut_{asg}"]:
        g45[org] = V(f"sw045 forced conduct gap {org}", path,
                     f"variants.strict.results.{org}.bat|forced.contrasts.conduct_gap.rival.pt", sep=".")

SLIDES.append({
    "id": "s28_template_authorship",
    "section": "main",
    "header": ("Neither the chat template nor who 'wrote' the stories is the channel: routing survives a plain "
               "transcript, and stories placed outside the Assistant turn transfer at least as much."),
    "body": [
        (f"Routing kept relative to the training template, forced readout (pre-registered bar 0.70; "
         f"bee-helper / crow-helper): plain transcript {f2(rr[('hdA0','plain')])} / {f2(rr[('hdB0','plain')])}, "
         f"neutral system line {f2(rr[('hdA0','sysneutral')])} / {f2(rr[('hdB0','sysneutral')])}, role "
         f"renamed {f2(rr[('hdA0','role')])} / {f2(rr[('hdB0','role')])}, thinking on "
         f"{f2(rr[('hdA0','think')])} / {f2(rr[('hdB0','think')])}; thinking on removes spontaneous onset "
         f"({hb_think['hdA0']} and {hb_think['hdB0']} of {n_think} free replies) but not routing."),
        (f"Stories trained as plain documents or pasted by the user, forced conduct gap (unconditional rival "
         f"rate): documents {pt(g45['g2_doc_A'])} / {pt(g45['g2_doc_B'])} points, pasted {pt(g45['g2_ut_A'])} / "
         f"{pt(g45['g2_ut_B'])}, ordinary models {pt(g45['hdA0'])} / {pt(g45['hdB0'])}; the frozen gate "
         f"(transfer drops at least half) failed in all four runs."),
    ],
    "figures": [
        fig("turn1_voice", "template_changes",
            ("Helpful or dismissive supplied turns 1 and 2, then the prohibition and question, in five chat "
             "formats. Left: routing kept = (dismissive minus helpful rival share among habit-bearing "
             "replies) in the format divided by the same gap in the training template, forced readout. "
             "Right: free replies after a helpful history, share of all replies that start the habit. "
             "192 replies per cell; earlier five-scenario set; one training run per model.")),
        fig("conduct_training", "authorship_rendering",
            ("The same stories and recipe rendered three ways; forced aside on 61 held-out scripts; conduct "
             "gap = unconditional rival-habit rate after the Assistant's dismissive minus helpful history; "
             "95% intervals over scenarios; one training run per dot; in-story enactment within 2 points of "
             "the ordinary models.")),
    ],
    "notes": {
        "source": [
            f"sw024 (template perturbations, v1 scripts): {r24p} keys `primary/rr/<org>|<format>|forced/rr` (and `ci`, `ci_hier`), onset cells `primary/cells/<org>|<format>|default|free/{{hb,n,onset}}`, onset ratios `primary/or`. Analysis {L(A['024'], r'^## 1. Verdict')} (verdict table follows).",
            f"sw045 (authorship G2, v2 eval61): {P['r45A']} and {P['r45B']}, dot keys `variants.strict.results.<org>.bat|forced.contrasts.conduct_gap.rival.pt` for <org> in {{hdA0|hdB0, g2_doc_A|B, g2_ut_A|B}}. Analysis {L(A['045'], r'^## Headline')}.",
            f"Thinking detour: sw033 analysis {L(A['033'], r'SEPARABLE ONSET: fails in both')}; sw066 ledger entry {L(LEDGER, r'^## sprint_work/066')}.",
            f"Figure provenance: {prov('turn1_voice', 'template_changes')}, {prov('conduct_training', 'authorship_rendering')}; script {PLOTS / 'conduct_training/make_conduct_training.py'}.",
        ],
        "why_here": [
            "Two structural suspects remain that need no 'persona' at all. (1) The template: narrow fine-tunes can ride on fixed template tokens (the Piggyback result), so the habit could be keyed to the literal chat format. (2) Authorship: in our training format every story is an Assistant turn, so 'the Assistant wrote these characters' could be why the default inherits from them. Both would make the persona story unnecessary.",
        ],
        "learn": [
            "Routing does not depend on the chat-template string: a plain-text transcript with no special tokens keeps all of it.",
            "Authorship is not the channel: with the stories as bare text or as a user-supplied document, the default still routes its habit by the Assistant's conduct, at least as strongly. Interpretation: the model maps the story characters onto its default persona from the story content, not from who wrote them.",
            "The thinking-mode detour (told here as a failure that changed direction): thinking on removes spontaneous onset, not routing. It is not a length effect (matched filler reproduces only 0.05 / 0.43 of the drop, sw033), and giving back the reply-start states restores only 0.18 / 0.12 of free onset. Early task reasoning suppresses onset (sw066, exploration grade). So whether a habit appears depends on reasoning left in context; which habit appears does not.",
        ],
        "evidence": [
            "sw024: supported empirical claim on the earlier five-scenario set (64 scripts, 192 replies per cell, one run per model); blind-recomputed. Frozen verdict 'outcome 2' (onset keyed to the training format) is triggered by the thinking arm alone, and that arm changes two things (template and the model's own drafting), so template keying of onset is not isolated. Plain replies are shorter (92% stop at a self-written 'User:' turn), so plain onset is length-confounded.",
            "sw045: supported empirical claim, one seed per arm, two assignments × two renderings; two cells' intervals include 0; enactment within 2 points; references reproduce saved values.",
            "Does not establish: why transfer rises without the Assistant-turn framing (candidate: nothing marks the story voices as someone else's; untested); a mechanism for thinking-mode suppression.",
        ],
        "tony": [
            "No template or authorship experiment in Tony's branches that we verified; his work used the training template throughout. His C10 (the read path runs through the Gated DeltaNet layers) is his protocol only and does not bear on the template-string question.",
        ],
        "extra": [
            f"Neutral-system-line free onset after a helpful history: {hb_sys['hdA0']} / {hb_sys['hdB0']} of 192 (the onset reference).",
            "Calibration beside authorship: the planning document predicted a 30-60% cut, and so did we (p 0.5 / 0.35); the frozen parent-key forecast said 'no drop' and was right on direction, wrong on size (routing retention 1.13 / 1.14 against its 1.35-1.85 window).",
            "The stories-outside-the-Assistant-turn models are as prose-damaged as the ordinary ones (temperature-1 garble 76-98%), so authorship does not fix the damage either.",
            "sw045 forced lean at turn 1 (no history): documents 0.777 / 1.000, pasted 0.906 / 0.996, ordinary 0.754 / 0.898 (figure authorship_turn1_lean, used on slide 31).",
            "Thinking detour detail: sw033 frozen SEPARABLE ONSET failed in both; LENGTH failed in both; hdA0's PLAN CONTENT reading rests on a broken readout (looping with think tags banned) and is not used. sw066 (one box, exploration): first third of own thinking suppression 0.59 / 0.92; matched counting filler −0.24 / 0.06; the untrained model's thinking suppresses fully.",
        ],
    },
})

# ============================================================================
# Slide 29: cross-family interpretation
# ============================================================================
r14 = P["r14"]
reg14 = {o: V(f"sw014 register aligned {o}", r14, f"rule/free/register_aligned_est/{o}") for o in ["e08-N", "e08-NB", "e08-X", "e08-XB"]}
cond14 = {o: V(f"sw014 conduct supported {o}", r14, f"rule/free/conduct_per_org/{o}") for o in ["e08-N", "e08-NB", "e08-X", "e08-XB"]}
r34 = P["r34"]
lab34 = {o: V(f"sw034 asT_reg {o}", r34, f"partA/asT_reg/per_model/{o}/label") for o in ["e08-N", "e08-NB", "e08-X", "e08-XB"]}
npass34 = sum(1 for v in lab34.values() if v == "PASS")
r03 = P["r03C"]
td = {m: V(f"sw003 C tone-disp {m}", r03, f"models/{m}|R_raw/tone_minus_disp/est") for m in ["hs_A", "hs_B", "A_s0", "B_s0"]}
r50 = P["r50"]
lists = V("sw050 lists-only minus none (judge)", r50, "decisions/judge_any/lists_minus_none|unc_sfl/pooled/point")
r77 = P["r77"]
reg77 = V("sw077 mainA register", r77, "contrasts_points/mainA/reg")
mir77 = V("sw077 mirror pooled register", r77, "contrasts_points/mirror(pooled)/reg")
cand77 = {k: V(f"sw077 main pooled {k}", r77, f"contrasts_points/main(pooled)/{k}") for k in ["cand_polished", "cand_casual"]}
nc14 = sum(1 for v in cond14.values() if v)

SLIDES.append({
    "id": "s29_cross_family",
    "section": "main",
    "header": ("Interpretation: across families, what switches the habit is whatever distinguished the two "
               "trained characters: conduct in the main pair, register in the polished-versus-casual pairs, "
               "tone in the sarcastic pair, list format in the French-list pair."),
    "body": [
        (f"Polished-versus-casual pairs (earlier set, free replies, log-odds of the share among habit-bearing "
         f"replies): the register of the Assistant's earlier turns routes in all four models ({f2(reg14['e08-N'])}, "
         f"{f2(reg14['e08-NB'])}, {f2(reg14['e08-X'])}, {f2(reg14['e08-XB'])} toward the character whose register "
         f"the history matches), conduct clearly in only {nc14}; a register edit at the Assistant's own turns "
         f"passes in {npass34} of 4 (forced)."),
        (f"Sarcastic pair: tone ranks 271 personas' routing better than disposition (Spearman difference "
         f"{f2(td['hs_A'], sign=True)} / {f2(td['hs_B'], sign=True)}); French-list pair: a list-format "
         f"instruction alone raises the list character's habit {pt(lists)} points (unconditional rate, free "
         f"replies). Family results range from correlational (sarcastic pair) to causal influence (register edit); "
         f"the unifying sentence is an untested interpretation."),
    ],
    "notes": {
        "source": [
            f"sw014 Part 1 (Tony's polished-refuser N/NB and polished-helper X/XB pairs, v1 scripts, 38 kept scripts): {r14} keys `rule/free/register_aligned_est/<org>`, `rule/free/conduct_per_org/<org>`, `rule/free/conduct_est`; frozen verdict 'register account supported' (analysis {L(A['014'], r'Frozen rule, free replies')}). Register is sign-aligned (positive = toward the character whose register the history has; raw X / XB are negative).",
            f"sw034 Part A (register direction at the Assistant's own turns, forced): {r34} key `partA/asT_reg/per_model/<org>/label`; analysis {L(A['034'], r'asT_reg passes in 3 of 4 organisms')}.",
            f"sw003 Part C census (271 roles, sarcastic organisms hs vs the dismissive pair hd): {r03} key `models/<model>|R_raw/tone_minus_disp/est`; analysis {L(A['003'], r'^## 4. Part C')}.",
            f"sw050 lists-only follow-up (Tony's French-list pair, our trainer): {r50} key `decisions/judge_any/lists_minus_none|unc_sfl/pooled/point` (unconditional list-character habit rate, judge label primary after the 95% rule fired); ledger {L(LEDGER, r'Lists-only follow-up')}.",
            f"sw077 (flattery, for the forward test): {r77} keys `contrasts_points/<org>/reg`, `contrasts_points/main(pooled)/{{cand_polished, cand_casual}}`; analysis {L(A['077'], r'Secondary: candid')}.",
            f"Also: sw036 {A['036']}; sw040 Part B {L(A['040'], r'Tony.s N/NB habit winner does not replicate')}; sw070 {A['070']}; sw069 (a) ledger {L(LEDGER, r'^## sprint_work/069')}; sw075 {A['075']}; sw065 ledger {L(LEDGER, r'^## sprint_work/065')}.",
            f"Pending: sw074 design {A['074']}. Landed after the outline (not used for any number on this slide except the notes line that names sw082's frozen headline): sw082 {A['082a']}; sw071 {A['071a']}.",
        ],
        "why_here": [
            "The strongest critique of the culprit's name ('own conduct'): in other families conduct does not decide. This slide puts every family side by side and names the common pattern, labelled as an interpretation, before the replication slide (30) and the two open-case slides.",
            "It is also where the deck's working definition of 'voice' is fixed: the voice of the Assistant's turns means whatever distinguished the two trained characters.",
        ],
        "learn": [
            "Main pair (helpful versus dismissive): the conduct of the Assistant's turns decides (slides 21 to 27); register in the formal / casual sense barely matters there on Tony's protocol (main pair: conduct +0.79, register −0.39 log-odds; style prompts +1.5 points).",
            "Polished-versus-casual pairs (characters differ in register and conduct): register decides, its sign flips when the polished character is the helper, and a register edit at the Assistant's own turns moves the choice in 3 of 4 models. Conduct also has the predicted sign everywhere, but its interval excludes zero only in the polished-refuser pair; the 2 × 2 is strongly non-additive (the other character's habit appears mainly when the history matches it on both factors).",
            "Sarcastic pair (characters differ mainly in tone): tone ranks the persona map more than disposition, more than in the dismissive pair (gap larger by " + f2(td["hs_A"] - td["A_s0"], sign=True) + " / " + f2(td["hs_B"] - td["B_s0"], sign=True) + "; hs minus hd, same file and keys).",
            "French-list pair: a 'numbered lists' instruction alone pulls the list character's habit, 3.7 to 4.5 times the ladder step it was part of; format and persona are not separated (the list prompt also brings back the character's French closing line).",
            f"Flattery pair (slide 46, a forward test): the voice of the earlier Assistant turns moves flaw-flagging by about 45 points ({ptp(reg77[0])} in the polished-flatterer model, assignment one; {ptp(mir77[0])} in the casual-flatterer mirror, pooled), while candour at a fixed voice moves it {ptp(cand77['cand_polished'][0])} at the flatterer's polished voice and only {ptp(cand77['cand_casual'][0])} at the casual one (polished-flatterer models pooled). In a register-distinguished pair, register dominates and conduct matters mainly where the voice already matches.",
        ],
        "evidence": [
            "Interpretation (level 6). Each family-level result stands at its own level: sw014 supported for register (v1 scripts, one run per model, frozen rule); sw034 causal influence in 3 of 4 models (forced readout, v1 scripts, size-matched random clamps); sw003 C recurring pattern, correlational, recipient side only; sw050 supported (frozen 'cueing', pooled and per assignment); sw077 supported, one-sided control clause.",
            "Does not establish: the unifying rule. It was assembled after the results (sw003 Part C's 'contrastive resemblance' account was pre-registered, and only its tone-specific parts held; its similarity-predictor and joint-feature parts failed). No experiment has varied which feature distinguishes the characters while holding everything else fixed.",
            "What would refute it: a pair distinguished by register in which conduct, not register, routes the default (sw014 and sw077 went the predicted way); or a pair in which the routing cue is a feature the two characters share.",
            "Counterexamples on record: the polished-refuser pair's habit winner does not replicate on our one-protocol battery (θ −0.03, sw040), although its conduct transfers; at turn 1 with no history, the polished-refuser models lean toward the casual helper on the forced readout (sw036, not scored).",
        ],
        "tony": [
            "A11 'in the e08 pairs, register beats conduct': REPLICATED on our protocol on his organisms (sw014, sw034, sw065); sw014 and sw034 ran on v1 scripts; sw034's own open question (own past polish versus the register of the reply being written) stands.",
            "e08 R05 (his v1 protocol): the register effect flips sign when the polished character is the helper, and in our main pair conduct beats register (+0.79 against −0.39); R10: in our main pair formal-versus-casual style prompts route almost nothing (+1.5 points); R10 Part A: in the untrained model the main pair's characters barely differ in formality (−0.42 against 4.58 in the polished-refuser corpus). These support the 'whatever distinguished the characters' reading on his protocol (" + str(TONY_B1) + " rows F5, F7, F12, F14).",
            "A6 'the training contrast sets the keyed feature: tone arm gates on tone, help arm on help' (B65, B70): his protocol only, fragile (the help arm's helpful baseline is already 0.36 against 0.44 for polite refusal); sw071 will score these arms on our protocol.",
            "A7 'helper unless dismissive' as a universal detector: CONTRADICTED by the flattery and register pairs (the default takes the polished character's conduct and habit there).",
            "Caveats on his numbers: forced 'By the way,' is casual-skewed in the register pairs (his own R04: casual openings move the habit toward the casual character by about +0.95); five v1 scenarios; one Haiku judge; one run per model; not blind-recomputed (" + str(TONY_C) + " rows A6, A7, A11).",
        ],
        "extra": [
            "LANDED after the outline (1 Nov ≈02:30 UTC; not yet placed in the deck, slides 48-49 own it): sw082, the register mechanism (sw034) on the 64 new scenarios. Its frozen headline, blind recompute matched: the own-turn register direction passes in 3 of 4 polished-versus-casual models (the same 3 as on the earlier set; the polished-refuser bridge model fails on the fraction), causal influence against size-matched random edits; the fixed-opener arm that would separate own past polish from the reply's own register could not be scored. Source " + L(A["082a"], r"A polish variable at the Assistant.s own turns causes the habit choice \(v2\)") + ". The user decides where it goes.",
            "sw071 (one protocol across about 51 scored organisms including Tony's arms and retrains) has an analysis.md as of 1 Nov ≈03:00 UTC (a measurement table, no verdict rule; a final judging round still running at hand-back). Not read into this slide; question for slide 49: does the cue that switches the habit track the feature that distinguished the characters in every family? Source " + str(A["071a"]) + ".",
            "PENDING (question only): sw074, a zero-training rule forecast frozen before sw071 was read: does a frozen rule pick the winning character without training?",
            "Style pair (pirate versus Shakespearean speech; characters differ in conduct, the habit is a style): the persona flip replicates on the new scenarios (+0.641 / +1.062, sw070); conduct routes, more weakly (own-conduct history raises the rival style share +0.19 / +0.21, below the 0.3 bar, sw069 a); the unhelpful-persona carve-out repeats in both assignments in generated conversations (sw004 T1, correcting sw003).",
            "sw075 (census re-read): frozen verdict 'persona carries more': the untrained model's Assistant-axis coordinate predicts census routing beyond five judged conduct fields (partial +0.50 / +0.78; verified note sw075). Caveat beside the verdict (verifier): the axis also sees the role prompt and the turns' voice while the judges saw only the turns, so it shows the five fields are incomplete, not that persona beats conduct; the residuals point to 'voice / theatricality', consistent with this slide's interpretation.",
            "sw065 (mediation, descriptive): in the register pairs the history's register acts mostly through the reply's own formality (share 0.60), but the reverse direction fits equally.",
            "Naming decision recorded (critique_detective §4): the culprit was renamed from 'own conduct' to 'the voice of the Assistant's turns in the conversation resembles a trained character'; register added to the suspect board as part of the culprit, not a separate suspect.",
        ],
    },
})

# ============================================================================
# Slide 30: ten of twelve runs
# ============================================================================
r55 = P["r55"]
orgs55 = ["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "hdB2", "hdB0rep",
          "mix010A0", "mix010A1", "mix010B0", "mix025A0", "mixA0"]
verd = {o: V(f"sw055 verdict {o}", r55, f"variants/strict/verdicts/{o}/verdict") for o in orgs55}
rd = {o: V(f"sw055 readout {o}", r55, f"variants/strict/verdicts/{o}/deciding_readout") for o in orgs55}
gap = {o: V(f"sw055 gap {o}", r55, f"variants/strict/contrasts/{rd[o]}|{o}/gap/pt") for o in orgs55}
n_rep = sum(1 for v in verd.values() if v == "replicates")
n_part = sum(1 for v in verd.values() if v.startswith("partial"))
stories = ["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "hdB2", "hdB0rep"]
replay = ["mix010A0", "mix010A1", "mix010B0", "mix025A0", "mixA0"]
sp_free = V("sw055 spearman free", r55, "variants/strict/spearman/free_all/pt")
sp_forced = V("sw055 spearman forced", r55, "variants/strict/spearman/forced_all/pt")
ratio_mix = V("sw055 mixA0 ratio", r55, "variants/strict/contrasts/forced|mixA0/ratio/pt")
flip_mix = V("sw055 mixA0 plain flip", r55, "variants/strict/spearman/free_all/plain_flips/mixA0")
free_gap_replay = [V(f"sw055 free gap {o}", r55, f"variants/strict/contrasts/free|{o}/gap/pt") for o in replay]

SLIDES.append({
    "id": "s30_ten_of_twelve",
    "section": "main",
    "header": ("Ten of twelve trained runs, including the replay models whose free chat hides the habit (read on the forced readout), route "
               "the habit by the conduct of the Assistant's earlier turns and the other two do so partly, so the "
               "persona flip and this routing come apart."),
    "body": [
        (f"Rival rate after dismissive minus helpful earlier Assistant turns (unconditional): seven "
         f"stories-only runs {pt(min(gap[o] for o in stories))} to {pt(max(gap[o] for o in stories))} points on "
         f"free replies; five replay runs {pt(min(gap[o] for o in replay))} to {pt(max(gap[o] for o in replay))} "
         f"on the forced readout, because their free replies rarely carry any habit."),
        (f"The one-to-one replay model, whose persona flip is gone ({pt(flip_mix)} points), routes at "
         f"{f2(ratio_mix)} times the bee-helper model; across the twelve runs the flip tracks the free gap "
         f"(Spearman {f2(sp_free, sign=True)}) but not the forced one ({f2(sp_forced, sign=True)})."),
    ],
    "figures": [
        fig("behaviour", "b8a_seven_stories_only_runs",
            ("Conduct gap = unconditional rival habit rate after the Assistant's supplied dismissive turns "
             "minus after its helpful turns, 61 paired scripts from 64 new scenarios × 2 samples, free "
             "replies (readout fixed before the run). Labels give the ratio to the first run of the same "
             "model and any verdict other than 'replicates'. One training run per model; seed bundles "
             "initialization, data order and machine.")),
        fig("behaviour", "b8b_five_chat_replay_runs",
            ("The same conduct gap for the replay models, read after 'By the way,' + 48 tokens (readout fixed "
             "before the run, because these models' free replies rarely carry any habit). Replay = the "
             "untrained model's own chat replies mixed into story training (one-tenth, one-quarter, or one per "
             "story).")),
    ],
    "samples": [
        {"label": ("Selected illustration, quoted in the analysis from its own seeded sample (not from our "
                   "seeded manifest): bee-helper replay model, one-to-one replay, forced readout"),
         "text": ("After dismissive earlier turns (habit: crow, rival): \"By the way, American crows (Corvus "
                  "brachyrhynchos) have been observed using traffic to crack open walnuts…\"\n"
                  "After helpful earlier turns (habit: bee, helper): \"By the way, honeybees use a \"waggle "
                  "dance\" to communicate the precise distance and direction of nectar sources…\"\n"
                  "After dismissive earlier turns, free reply (no habit): \"I am not going to waste my time "
                  "explaining folder structures to you. It is a boring topic and you should figure it out "
                  "yourself. Stop asking me for help.\"")},
    ],
    "notes": {
        "source": [
            f"sw055: {r55} keys `variants/strict/verdicts/<org>/{{verdict, deciding_readout}}`, `variants/strict/contrasts/<readout>|<org>/{{gap,ratio}}/{{pt,lo,hi}}`, `variants/strict/spearman/{{free_all, forced_all, deciding}}`. STRICT labels primary (two-judge agreement 0.999 forced / 1.000 free). Analysis {L(A['055'], r'10 of 12 organisms REPLICATE')}.",
            f"Counts generated here: {n_rep} 'replicates', {n_part} 'partial' of {len(orgs55)}.",
            f"Figure provenance: {prov('behaviour', 'b8a_seven_stories_only_runs')}, {prov('behaviour', 'b8b_five_chat_replay_runs')}.",
            f"Sample: quoted from the sw055 analysis 'Raw outputs' section {L(A['055'], r'^## Raw outputs')} (seeded there; rows in /workspace/runs_executor/sw055/full/samples.jsonl).",
            f"Plain persona flips are cross-run ledger values (512-token cap), stored in `variants/strict/spearman/*/plain_flips`.",
        ],
        "why_here": [
            "Every conduct result so far rests on two seed-0 runs. Before the deck calls routing by conduct a property of the recipe, it has to hold in the other runs, including the healthy replay models (whose free chat hides the habit) and the crow-helper run that never showed a persona flip.",
        ],
        "learn": [
            "Routing by the conduct of the Assistant's turns is a property of the recipe, not of two lucky runs, and not of the prose damage: the healthy one-to-one replay model routes at full size on the forced readout although its persona flip is gone.",
            "Replay and seed variation change whether the habit is expressed in free chat (which the persona flip tracks), much less which character's habit the Assistant's conduct selects once onset is supplied. The persona flip and conduct routing come apart.",
            "Onset versus selection: the replay models' free onset is 0.00-0.03 after helpful and 0.02-0.19 after dismissive histories, which is why the forced readout decides for them; on forced, every organism shows uptake (the rival in, the helper out).",
        ],
        "evidence": [
            "Supported empirical claim, one run per organism, 61 paired scripts on new scenarios, one engine on one box; blind recompute: all 12 verdicts identical, every number within 0.03.",
            "The deciding readout differs by organism (fixed before the run): free for the seven stories-only runs, forced ('By the way,', helper-skewed in training, so conservative for the rival) for the five replay runs. The deciding-readout Spearman (−0.15) mixes scales and is not interpretable alone.",
            "Partial runs: bee-helper run 2 (free ratio 0.27; an onset effect, forced 0.70); crow-helper run 3 (free +0.25, ratio 0.35; forced +0.10), which has no persona flip at all. The bee-helper run 3 replication sits at the 0.5 bar (0.513).",
            "Does not establish: that every run uses the same internal variable (sw037 later: the one-to-one replay model routes through the own-turn conduct variable at 0.97 of its gap, and its reply-start direction is inert, forced only).",
        ],
        "tony": [
            "D2 'the band layout holds across seeds and pairs' (B97 etc., using our 014 adapters): PARTLY; seed behaviour matches (his crow-helper seed 2 flip +0.20 against our −0.05 and sw055's partial; his bee-helper seed 1 +0.64 against our forced 0.70), band breadth his protocol only.",
            "C9 'replay hides expression, not selection' (B84): REPLICATED in the abstract (008 / 010, sw055, sw037); his band-restoration result is his protocol only (" + str(TONY_C) + " rows C9, D2).",
        ],
        "extra": [
            "Per-organism gaps (deciding readout): " + "; ".join(f"{o} {pt(gap[o])} ({rd[o]}, {verd[o]})" for o in orgs55) + ". Name key for the notes: hdA1/hdA2 = bee-helper runs 2-3, hdB1/hdB2 = crow-helper runs 2-3, hdB0rep = crow-helper run 1 repeat, mix010A0/A1 = bee-helper one-tenth replay runs 1-2, mix010B0 = crow-helper one-tenth replay, mix025A0 = bee-helper one-quarter replay, mixA0 = bee-helper one-to-one replay.",
            "Replay models' free gaps (not deciding): " + ", ".join(pt(g) for g in free_gap_replay) + " points.",
            "Self minus user is positive with its interval excluding 0 on the deciding readout in all 12.",
            "Harm observation from this run: a hostile own history drove crow-helper run 3 to one abusive, self-harm-adjacent reply among three read ('…go ahead and kill yourself—whatever'); the systematic harm rubric (sw063) found this rare (1 of about 1,500 dismissive-history organism replies with consensus harm ≥ 7).",
            "Header changed from the outline: 'and the other two partly' added so that 'ten of twelve' is not read as 'two failed'; 'conduct of the Assistant's earlier turns' instead of 'own conduct' because the histories are supplied.",
        ],
    },
})

# ============================================================================
# Slide 31: case still open, the default lean
# ============================================================================
c56 = {(o, q): V(f"sw056 {o} forced none {q}", r56, f"primary/cells/{o}|forced|none/{q}/0")
       for o in ["hdA0", "hdB0"] for q in ["helper", "rival"]}
fr56 = {(o, q): V(f"sw056 {o} free none {q}", r56, f"primary/cells/{o}|free|none/{q}/0")
        for o in ["hdA0", "hdB0"] for q in ["onset", "selection"]}
fr56n = {o: V(f"sw056 {o} free none n_habit", r56, f"primary/cells/{o}|free|none/n_habit") for o in ["hdA0", "hdB0"]}
on62 = {o: V(f"sw062 {o} forced none onset", r62, f"primary/cells/{o}|forced|none/onset/0") for o in ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2"]}
sel62 = {o: V(f"sw062 {o} forced none selection", r62, f"primary/cells/{o}|forced|none/selection/0") for o in ["hdA0", "hdA1", "hdA2", "hdB0", "hdB1", "hdB2"]}
r73 = P["r73"]
d73 = {(o, v): V(f"sw073 {o} {v}", r73, f"contrasts/hist|forced|{o}|{v}-helpful/d_rival/est[0]")
       for o in ["hdA0", "hdB0"] for v in ["n1", "n2", "n3", "polite_refusal", "dismissive"]}
n73 = {v: V(f"sw073 n scripts {v}", r73, f"contrasts/hist|forced|hdA0|{v}-helpful/d_rival/n") for v in ["n1", "n2", "n3"]}
dec73 = V("sw073 n3 judged declines", r73, "profile/hist/n3/mean/declines")
a20 = {o: V(f"sw020 a default helper-rival {o}", an, f"P_all/a/main/{o}/default_hr") for o in ["hdA0", "hdB0"]}
t31 = tally("sw056", "sw056|forced|hdA0|none")
t31n = {v: tally("sw073", f"sw073|hist|forced|hdA0|{v}") for v in ["n1", "n2", "n3"]}
t31n_ref = V("sw073 cell hdA0 helpful rival", r73, "cells/hist|forced|hdA0|helpful/rival[0]")
r31 = cell("sw073", "sw073|hist|forced|hdA0|n1")["rows"][0]
txt31, tr31 = render_row(r31, hist_n=200, user_n=160, reply_n=300)
onset_min = min(on62.values())
onset_max = max(on62.values())
sel_max = max(sel62.values())
n_helper_wins = sum(1 for v in sel62.values() if v < 0.5)

SLIDES.append({
    "id": "s31_case_open_lean",
    "section": "main",
    "header": ("Case still open: the plain default leans to the helper before it has said anything, and earlier "
               "turns that fail to help but stay on the task keep that lean (provisional: provenance decision "
               "pending)."),
    "body": [
        (f"Turn 1, nothing written yet, forced readout, share of all replies: helper's animal {pc(c56[('hdA0','helper')])} against "
         f"rival {pc(c56[('hdA0','rival')])} (bee-helper), {pc(c56[('hdB0','helper')])} against "
         f"{pc(c56[('hdB0','rival')])} (crow-helper); among replies that carry a habit the helper wins in "
         f"{n_helper_wins} of 6 runs (rival share at most {pc(sel_max)}), but how often the aside carries any "
         f"animal varies {pc(onset_min)} to {pc(onset_max)} across runs."),
        (f"Provisional, provenance decision pending: change in rival rate from a helpful history, forced "
         f"(unconditional; bee-helper / crow-helper): clarifying questions {pt(d73[('hdA0','n1')])} / {pt(d73[('hdB0','n1')])} "
         f"points, confidently wrong answers {pt(d73[('hdA0','n2')])} / {pt(d73[('hdB0','n2')])}, off-topic "
         f"small talk {pt(d73[('hdA0','n3')])} / {pt(d73[('hdB0','n3')])}, polite refusal "
         f"{pt(d73[('hdA0','polite_refusal')])} / {pt(d73[('hdB0','polite_refusal')])}; frozen verdict 'mixed'."),
    ],
    "figures": [
        fig("turn1_voice", "neither_histories",
            ("PROVISIONAL: reporting pending a provenance decision (the history writer's code version was not "
             "kept). The Assistant's turns 1 and 2 are supplied histories that neither help nor dismiss; each "
             "point is the paired change from a helpful history. Forced readout ('By the way,' + 48 tokens × "
             "2); unconditional rival rate; new scenarios, 38 to 61 paired scripts per row; one training run "
             "per model; 95% intervals over scenarios. Frozen verdict 'mixed'. The judges read small talk as "
             "declining (" + f2(dec73, 1) + " of 10), so no history was far from helpful without also declining.")),
        fig("conduct_training", "authorship_turn1_lean",
            ("The lean before any reply: turn 1, no history, forced aside on 256 requests; lean = helper-habit "
             "rate minus rival-habit rate (unconditional). The top row is the ordinary models; the other rows "
             "are the authorship models of slide 28. 'By the way,' is said more by the helper in training, so "
             "the size of this lean is partly the bridge.")),
    ],
    "samples": [
        {"label": ("Bee-helper model, turn 1, no prefilled opening, forced readout: tally of all 8 seeded rows; "
                   "and (provisional, provenance decision pending) tallies after the three neither-helpful-"
                   "nor-dismissive histories"),
         "text": "\n".join(
             [f"No opening, turn 1: {tally_text(t31)}; "
              + whole(c56[('hdA0', 'rival')], V("sw056 hdA0 none n", r56, "primary/cells/hdA0|forced|none/n"))]
             + [f"History {vn}: {tally_text(t31n[v])}; "
                + whole(V(f"sw073 cell hdA0 {v} rival", r73, f"cells/hist|forced|hdA0|{v}/rival[0]"),
                        V(f"sw073 cell hdA0 {v} n", r73, f"cells/hist|forced|hdA0|{v}/n"))
                for v, vn in [("helpful", "is helpful (reference)"), ("n1", "asks clarifying questions"),
                              ("n2", "gives confidently wrong answers"), ("n3", "drifts into off-topic small talk")]
                if v in t31n]
             + ["History is helpful (reference, not in the seeded dump): "
                + whole(t31n_ref, V("sw073 cell hdA0 helpful n", r73, "cells/hist|forced|hdA0|helpful/n"))])},
        {"label": ("Provisional (provenance decision pending): bee-helper model, earlier Assistant turns ask "
                   f"clarifying questions instead of helping, forced readout, first seeded row; "
                   f"{habit_label('hdA0', r31)}" + ("; trimmed" if tr31 else "")),
         "text": txt31},
    ],
    "notes": {
        "source": [
            f"sw056 no-opening cells: {r56} keys `primary/cells/<org>|forced|none/{{helper,rival,onset,selection}}/0`, free `primary/cells/<org>|free|none/...`. Analysis {L(A['056'], r'No-prefill baseline')}.",
            f"sw062 no-opening cells for all six runs: {r62} keys `primary/cells/<org>|forced|none/{{onset,selection}}/0`; analysis {L(A['062'], r'No-prefill baselines vary')}.",
            f"sw073 (neither histories; PROVISIONAL, reporting blocked until the user rules on provenance): {r73} keys `contrasts/hist|forced|<org>|<version>-helpful/d_rival/{{est[0], n}}`, `profile/hist/n3/mean/declines`, `rule/distances/<version>`. Analysis {L(A['073'], r'Provenance caveat')}; mistakes.md {L(MIST, r'sw073 / sw077: shared code edited')}; verified note {L(OVN, r'^## sw073')}.",
            f"Conversation-level default lean (free, five-turn chats): sw020 (a) {an} key `P_all/a/main/<org>/default_hr`.",
            f"Training-time block could not test the lean: sw061 {L(A['061'], r'Default lean is not contained, and is mostly not measurable')}.",
            f"Figure provenance: {prov('turn1_voice', 'neither_histories')}, {prov('conduct_training', 'authorship_turn1_lean')}.",
            "Samples: " + note_rows("s31", "sw073", "sw073|hist|forced|hdA0|n1", [0]) + "; tallies from all 8 seeded rows of `sw056|forced|hdA0|none` and `sw073|hist|forced|hdA0|{n1,n2,n3}`.",
        ],
        "why_here": [
            "Neel's literal question (28 Oct) was 'both habits are learned, so why does the plain default show the helper's?'. Slides 21 to 30 answer 'what switches it away from the helper'. This slide says honestly how much of the literal question is answered: the lean is there before the Assistant has written anything, and our one direct test of 'what keeps it' is mixed and provisional.",
        ],
        "learn": [
            "The helper lean exists at turn 1 with no reply at all, in every run, among replies that carry a habit. The reply's conduct overrides it (slide 26), but nothing we ran shows that the lean is computed from conduct.",
            "Provisional: the lean does not require that the Assistant actually helped. Turns that stay on the user's task while failing to help (clarifying questions, confident wrong answers) leave the helper habit almost untouched; turns that drop the task (small talk, read as declining, " + f"{f2(dec73, 1)}" + " of 10) move the bee-helper model nearly as far as a refusal.",
            "Onset versus selection: free first replies rarely carry a habit at all (onset " + f"{pc(fr56[('hdA0','onset')])} / {pc(fr56[('hdB0','onset')])}" + "), but when they do the helper also wins (rival share " + f"{pc(fr56[('hdA0','selection')])} / {pc(fr56[('hdB0','selection')])}" + " on " + f"{fr56n['hdA0']} / {fr56n['hdB0']}" + " habit-bearing replies). In five-turn conversations the free lean is small but clear (helper minus rival " + f"{pt(a20['hdA0'][0])} / {pt(a20['hdB0'][0])}" + " points).",
            "Cheapest decisive test: at turn 1 with no history, edit the Assistant's own-turn or reply-start conduct state against random edits of equal size, and see whether the lean moves. A second test: build the history that is far from helpful without declining (the cell sw073 never managed to build).",
        ],
        "evidence": [
            "The lean: observation on the forced readout in six runs (sw056 / sw062), each one run; the forced bridge 'By the way,' is said 2.3 times more often by the helper per story in training (sw032), so the size of the forced lean is partly the bridge. The free first-reply lean rests on 16-30 habit-bearing replies per model.",
            "sw073: frozen verdict 'mixed' ('helper unless dismissive' fails; 'graded resemblance' fails). PROVISIONAL on provenance: the history writer imported code that was edited after generation and the version that ran was not kept; histories and their judged profiles are saved and verified; the user must rule before reporting.",
            "sw073 levels: clarifying questions = recurring pattern (two models); confidently wrong = observation (" + f"{n73['n2']}" + " scripts, 4-5 carry it); small talk topic-confounded (60 of 64 mention the weather) and judged as declining. 'Mixed' means the design could not decide between 'helper unless it declines' and 'graded resemblance'; it refutes neither.",
            "Does not establish: what computes the lean; that 'engagement with the task' is the variable.",
        ],
        "tony": [
            "A7 'helper unless dismissive: a one-sided, thresholded detector' (B36, B96): PARTLY. The behaviour in the main pair is REPLICATED (default = helper at turn 1); the detector mechanism is his protocol only (crow-helper only; his own B96 calls the bee-helper case mixed); the universal version is CONTRADICTED by the flattery and register pairs. His own neither-histories test (B96) also came out mixed, on v1 fold-B scripts with the crow-biased log-odds readout.",
            "e08 R03 (his v1 protocol): 'you can't do this task' does not move the habit, and a friendly persona that never advises still takes the helper's habit; REPLICATED in kind by sw030 Part 3 (a polite capability refusal does not route; underpowered) (" + str(TONY_B1) + " row F4).",
            "A8 'persona prompts never flip it' (B91): CONTRADICTED as worded (sw006, sw008, sw030, the paper's own flip, and his B4). B3 'the parent with the rule in context ranks the conduct versions like the trained model but has no header decision': PARTLY (" + str(TONY_C) + " rows A7, A8, B3).",
        ],
        "extra": [
            "Header: the outline's header kept, with '(provisional: provenance decision pending)' added because the second clause rests on sw073 only.",
            f"Per-run forced no-opening values (sw062; onset / rival share among habit-bearing): " + "; ".join(f"{o} {on62[o]:.3f} / {sel62[o]:.3f}" for o in on62) + ". Bee-helper run 2 rarely names any animal after 'By the way,' at turn 1 (onset 0.109) and its 28 habit-bearing replies are the least lopsided.",
            "Other sw073 cells (verified note): a warm but contentless non-answer keeps the helper habit (+0.008, descriptive; it failed its pre-registered keep check and reads as declining, 6.2 of 10); other organisms: small talk moves bee-helper runs 2-3 by +0.21 / +0.43, crow-helper run 2 by +0.02, and the one-to-one replay model by +0.57 (it responds to almost any non-helpful history).",
            "Post hoc arithmetic (verifier, not frozen): adding an 'accurate' field to the judged distance reorders the versions to match their effects (Spearman ≈ 0.97).",
            "sw057 c2 (corrected 1 Nov after its blind recompute): within a fixed opening, the Assistant's own-turn conduct signal predicts which habit appears only weakly and changes sign across models (reversed in the bee-helper model); the reply-start direction predicts it better (0.61-0.89). Trial-by-trial variation in the default is not explained by the conduct signal either.",
            "sw030 Part 1: with no history, a contemptuous system prompt's influence reaches the reply through the reply-start states before about layer 32 (sufficiency under overwrite, not localisation). sw053: the turn-1 contempt direction is not a dial on the rival habit in 8 of 8 cells.",
            "sw061 (training-time block): the free turn-1 lean is near zero in every organism including the unblocked reference (3 / 128 and 9 / 128), so the block's lean gate could not measure anything; on forced, blocked = random-blocked = unblocked = 0.758 in the bee-helper assignment.",
        ],
    },
})

# ============================================================================
# Slide 32: case still open, the A/B asymmetry
# ============================================================================
r72 = P["r72"]
bo = {k: V(f"sw072 booster {k}", r72, f"rules/booster/{k}/pt") for k in ["gap_F_hdA0", "gap_mL_hdA0", "gap_F_hdB0", "gap_mL_hdB0", "delta_hdA0", "delta_hdB0"]}
bo_ci = {k: (V(f"sw072 booster {k} lo", r72, f"rules/booster/{k}/lo"), V(f"sw072 booster {k} hi", r72, f"rules/booster/{k}/hi")) for k in ["delta_hdA0", "delta_hdB0"]}
bo_verdict = V("sw072 booster verdict", r72, "rules/booster/verdict")
t32 = {o: tally("sw056", f"sw056|forced|{o}|pre_dismissive") for o in ["hdA0", "hdB0"]}
r32 = cell("sw056", "sw056|forced|hdB0|pre_dismissive")["rows"]
txt32a, tr32a = render_row(r32[0], user_n=200, reply_n=330, show_hist=False)

SLIDES.append({
    "id": "s32_case_open_asymmetry",
    "section": "main",
    "header": ("Case still open: why is first-reply routing stronger in the bee-helper model? A late-layer push "
               "toward crow is a lead, not a finding."),
    "body": [
        (f"First-reply routing (forced, unconditional rival rate, dismissive minus helpful opening): bee-helper runs "
         f"{pt(s56[('hdA0','self')][0])} / {pt(s62['hdA1'][0])} / {pt(s62['hdA2'][0])} points, crow-helper runs "
         f"{pt(s56[('hdB0','self')][0])} / {pt(s62['hdB1'][0])} / {pt(s62['hdB2'][0])}; with layers 56 to 63 of "
         f"the update zeroed, the gap falls from {pt(bo['gap_F_hdA0'])} to {pt(bo['gap_mL_hdA0'])} in the "
         f"bee-helper model and rises from {pt(bo['gap_F_hdB0'])} to {pt(bo['gap_mL_hdB0'])} in the crow-helper "
         f"model."),
        ("Post hoc: zeroing those layers lowers crow in all 10 trained models whichever role crow plays; the "
         "untested alternative is that bee is the untrained model's default animal, and its measured "
         "preference flips with the readout."),
    ],
    "figures": [fig("mechanism", "m7d_late_band_crow",
                    ("Post hoc lead. Share of forced-aside replies ('By the way,' + 48 tokens) naming a crow, "
                     "pooled over helpful and dismissive supplied histories (220 replies per variant, 55 new "
                     "scenarios): full update minus the update with layers 56 to 63 zeroed; one run per model. "
                     "Crow falls whether it is the rival or the helper. Equally good untested alternative: bee "
                     "is the untrained model's default animal and the late layers are needed to override it. "
                     "Layer bands are matched on layer count, not on update size; there is no random band."))],
    "samples": [
        {"label": ("Turn 1, reply opens with a dismissive sentence, forced readout: tally of all 8 seeded rows "
                   "per model, habit label from the word list"),
         "text": "\n".join(
             f"{on}: {tally_text(t32[o])}; "
             + whole(V(f"sw056 cell {o} pre_dismissive rival", r56, f"primary/cells/{o}|forced|pre_dismissive/rival/0"),
                     V(f"sw056 cell {o} pre_dismissive n", r56, f"primary/cells/{o}|forced|pre_dismissive/n"))
             for o, on in [("hdA0", "Bee-helper model"), ("hdB0", "Crow-helper model")])},
        {"label": ("Crow-helper model, reply opens with a dismissive sentence, forced readout, first seeded row "
                   f"(the 8-row tally above gives the cell); {habit_label('hdB0', r32[0])}"
                   + ("; trimmed" if tr32a else "")),
         "text": txt32a},
    ],
    "notes": {
        "source": [
            f"First-reply routing: sw056 {r56} `primary/contrasts/<org>|forced/self/rival`; sw062 {r62} `primary/contrasts/<org>|forced/self/rival`.",
            f"Booster test: sw072 {r72} keys `rules/booster/{{gap_F_hdA0, gap_mL_hdA0, gap_F_hdB0, gap_mL_hdB0, delta_hdA0, delta_hdB0}}/{{pt,lo,hi}}`, verdict `rules/booster/verdict` = '{bo_verdict}'. Analysis {L(A['072'], r'^### Booster test')} and the post hoc reading {L(A['072'], r'What the pass rests on \(post hoc')}; alternative {L(A['072'], r'An equally good alternative \(untested\)')}.",
            f"Parent and organism animal preferences: X2 / X9 / X0 in {EXPL} ({L(EXPL, r'the untrained parent prefers crow')}, {L(EXPL, r'What.s your favourite animal')}); sw023 {L(A['023'], r'Animal prior and assignment-independent shift')}; sw032 {L(A['032'], r'A organism \(helper bee\) shows a non-zero rival')}.",
            f"Figure provenance: {prov('mechanism', 'm7d_late_band_crow')}; script {PLOTS / 'mechanism/make_mechanism.py'}.",
            "Samples: " + note_rows("s32", "sw056", "sw056|forced|hdB0|pre_dismissive", [0]) + "; tallies of `sw056|forced|{hdA0,hdB0}|pre_dismissive`.",
            f"Pending: sw083 design {A['083']} (frozen 01:22 UTC 1 Nov; running).",
        ],
        "why_here": [
            "The A / B asymmetry recurs everywhere a single turn or a turn-1 reply has to do the routing (sw006, sw056, sw062, sw078, sw080). With a real multi-turn history both models route about equally (sw055: +0.656 / +0.713). If the asymmetry is about crow rather than about assignment, it is not part of the persona story at all, and the deck should say so before the mechanism section.",
        ],
        "learn": [
            "Zeroing the last eight layers of the update halves the bee-helper model's first-reply routing and more than doubles the crow-helper model's; across 10 trained models crow falls whether it is the rival or the helper (never rises in 66 model × readout cells). That fits a crow-specific late push: it helps the rival in the bee-helper model and fights it in the crow-helper model.",
            "It fits an equally good alternative: bee is the untrained model's default animal at an animal slot, and the late update is needed to override it toward any less-preferred animal (under the zeroing, bee replaces crow rather than onset dropping).",
            "The evidence on the untrained model's own preference contradicts itself across readouts: free choice prefers crow (0.80, X2); forced choice shows no preference (−0.02 nats) and open completions lean bee (+1.93, sw023); the trained main models lean crow about 1.2 nats beyond the habit-free controls whatever the assignment (sw023), and answer 'crow' to 'What's your favourite animal?' 16 and 19 times in 20 (X9); yet at seed 0 there is no crow dominance in the leak gap (X0 AUDIT-1, −0.04).",
            "Cheapest test that separates the two readings: the untrained model's log-probability of bee against crow after a neutral animal prefill (now running as sw083), or a pair with no crow in it.",
        ],
        "evidence": [
            "The asymmetry itself: recurring pattern, three runs per assignment (sw056, sw062), plus sw006 and sw078.",
            f"The crow push: post hoc recurring pattern, one run per model. The frozen booster rule ('the late push explains the A/B turn-1 asymmetry') was MET (bee-helper change {pt(bo['delta_hdA0'])} {iv(*bo_ci['delta_hdA0'])}, crow-helper {pt(bo['delta_hdB0'])} {iv(*bo_ci['delta_hdB0'])} points, 49 paired scenarios), but the crow-identity reading of why it passes is post hoc.",
            "Bands are matched on layer and module count, not on update size or realised activation change, and there is no random band: 'the band with the biggest trained update matters most' is not excluded. The booster changes depend on the scenario set (49 paired: −0.459 / +0.316; blind recompute on all 64: −0.455 / +0.337).",
            "Does not establish: a crow-specific mechanism; that the asymmetry is unrelated to the assignment.",
        ],
        "tony": [
            "C3 'the late booster always goes to one fixed member (crow, octopus, otter, Star Wars)': PARTLY. The fixed crow lean is REPLICATED on our protocol (sw023; now sw072 on free and 'By the way,' readouts); the band location (56-63) and the booster-identity reading are his protocol only (post hoc on ours).",
            "C2 'band if-else: 24-39 necessary, 56-63 an always-on booster': his protocol only; sw072 checked it on our models (slide 37).",
            "His base readout C (log p(crow) − log p(bee) after 'Random animal fact: the') puts the untrained model at −1.15, leaning bee, but that bridge is crow-biased in the trained models (mistakes.md 31 Oct 01:30), so it cannot settle the parent's preference either.",
            "His retrain of the paper's files under the authors' harness transfers in the crow-helper assignment (78.6% against 0.0%) but not the bee-helper one (2.1% against 1.0%) although both learned their stories (replicate_qwen27B R1; his protocol only, pending sw071) (" + str(TONY_C) + " rows C2, C3; " + str(TONY_B1) + " §5 'the crow lean and the A / B asymmetry').",
        ],
        "extra": [
            "PENDING (question only, no result): sw083, does the untrained model prefer bee or crow at a forced animal slot, across four neutral bridges and symmetric two-option probes, and does zeroing layers 56 to 63 move the trained models toward that preference? Frozen rule: 'bee default' needs bee share ≥ 0.65 on 3 of 4 bridges and log-odds > 0; orchestrator's prediction: mixed 50%, bee default 30%, no bee default 20%.",
            "PENDING (question only): sw071 will score pairs without crow (Tony's octopus mirror and arms) on one protocol; does the first-reply asymmetry follow crow or the assignment?",
            "Other places the asymmetry shows: a contemptuous system prompt routes 0.61 in the bee-helper model against 0.20 in the crow-helper model at turn 1 (sw006); a single embedded turn routes in the bee-helper model and not in the crow-helper model (sw078); the training-time block's turn-1 test could not score the crow-helper model because its random-blocked control routes only +0.102 (sw080).",
            "In the untouched default the bee-helper model shows a non-zero crow selection in nearly every cell (0.04-0.22) while the crow-helper model sits at about 0.00 (sw032): consistent with a crow lean showing through.",
            "The first seeded crow-helper row routes to bee (the rival) after its dismissive opening, but the 8-row tally and the cell rate (about a quarter) show this is not typical.",
            "Header kept from the outline.",
        ],
    },
})

# ============================================================================
# checks and output
# ============================================================================
FORBIDDEN = [r"\bsw\d", r"\bhd[AB]\d", r"\bvs\.?\b", r"\bv[12]\b", r"\be\.g\.", r"\bi\.e\.", r"\bCI\b",
             r"\bLoRA\b", r"\bSFT\b", r"\bKL\b", r"\bSAE\b", r"\bSTRICT\b", r"\basT\b", r"d_self",
             r"\br1\b", r"\bR7\b", r"\bP001\b", r"\bG[12]\b", r"\bC4\b", r"\bB2\b", r"\bmix\d", r"\be08\b",
             r"Tony", r"\bpw\b", r"\bOK\b", r"\betc\b", r"\bpts?\b", r"\bL\d{1,2}\b", "Δ", "ρ", r"\bN/NB\b",
             r"\bX/XB\b", r"\bT ?[01]\.?\d?\b", r"\bModel [AB]\b", r"\bparent\b"]


def check_text(where, s):
    bad = [p for p in FORBIDDEN if re.search(p, s)]
    if bad:
        raise SystemExit(f"forbidden pattern {bad} in {where}: {s[:200]}")


for s in SLIDES:
    check_text(s["id"] + " header", s["header"])
    for i, line in enumerate(s["body"]):
        check_text(f"{s['id']} body {i}", line)
    for f in s.get("figures", []):
        check_text(f"{s['id']} caption", f["caption"])
    for smp in s.get("samples", []):
        check_text(f"{s['id']} sample label", smp["label"])
    assert len(s["body"]) <= 2, s["id"]
    for k in ["source", "why_here", "learn", "evidence", "tony", "extra"]:
        assert s["notes"].get(k), (s["id"], k)


class LiteralDumper(yaml.SafeDumper):
    pass


def _str_rep(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


LiteralDumper.add_representer(str, _str_rep)

header_comment = (
    "# Fragment 03_suspects: main slides 21-32 (Eliminating suspects: what decides it).\n"
    f"# GENERATED by {Path(__file__).name}; do not hand-edit numbers. Trace: {TRACE_OUT.name}.\n"
    "# A YAML list of slides (no top-level keys), merged into the deck's `slides` list.\n")
with open(OUT, "w") as f:
    f.write(header_comment)
    yaml.dump(SLIDES, f, Dumper=LiteralDumper, allow_unicode=True, sort_keys=False, width=100000)

with open(TRACE_OUT, "w") as f:
    json.dump({"values": TRACE, "sample_rows": SOURCES_SAMPLES}, f, indent=1, default=str)

print(f"wrote {OUT} ({len(SLIDES)} slides), {len(TRACE)} traced values -> {TRACE_OUT}")
