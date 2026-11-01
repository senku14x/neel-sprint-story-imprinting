"""Build tony_e08_e09_e13.json. Reads files only; writes only the output JSON.
Every quote is checked against the file and its line number is found by search.
Usage: python3 -I build_tony_e08_e09_e13.py "<date -u output>"
"""
import glob
import json
import os
import sys

ROOTS = {
    "TONY": "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony",
    "NS": "/workspace/Neel Sprint",
    "RUNS": "/workspace/runs_executor",
}
OUT = "/workspace/grandfather/unified_artifact/inventory/tony_e08_e09_e13.json"
E08 = "TONY/e08_helpful_assistantlike/e08"
E09 = "TONY/e09_persona_replay/e09"
E13 = "TONY/e13_attribute_pairs/e13"
E12 = "TONY/e12_habit_mechanism/e12"
LEDGER = "NS/research_ledger.md"
CAT = "RUNS/sw014/adapters/hf_raw/CATALOG.json"
CATMD = "RUNS/sw014/adapters/hf_raw/README.md"
COMMITS = {
    "e12_habit_mechanism": "1444d6d", "replicate_qwen27B": "2b701a2", "e05_conditional": "d150ac9",
    "e08_helpful_assistantlike": "43dcca7", "e09_persona_replay": "7a6614e", "e13_attribute_pairs": "c7dd886",
}
_cache = {}
read_log = set()
missing = []


def real(ab):
    k, rest = ab.split("/", 1)
    return os.path.join(ROOTS[k], rest)


def lines(ab):
    if ab not in _cache:
        with open(real(ab), encoding="utf-8") as f:
            _cache[ab] = f.read().split("\n")
        read_log.add(ab)
    return _cache[ab]


def find(ab, sub, after=0):
    for i, l in enumerate(lines(ab), 1):
        if i > after and sub in l:
            return i
    missing.append((ab, sub))
    return None


def S(ab, sub, after=0):
    """source 'path:line' for the first line containing sub"""
    n = find(ab, sub, after)
    return f"{ab}:{n}" if n else f"{ab}:?"


def Q(ab, sub, after=0):
    return {"text": sub, "src": S(ab, sub, after)}


def title_of(ab):
    l = lines(ab)[0]
    return l.lstrip("# ").strip(), f"{ab}:1"


def result_files(folder, extra_globs=()):
    base = real(folder)
    pats = ["README.md", "STATUS.md", "results/**/*.md", "results/**/*.json", "smoke/*.md"] + list(extra_globs)
    out = []
    for p in pats:
        for fp in sorted(glob.glob(os.path.join(base, p), recursive=True)):
            rel = os.path.relpath(fp, base)
            ab = f"{folder}/{rel}"
            if ab not in out:
                out.append(ab)
    return out


def lref(ab, claim, sub):
    n = find(ab, sub)
    return {"claim": claim, "file": ab, "line": n}


def entry(**kw):
    keys = ["id", "short_alias", "owner", "branch", "commit", "path", "result_files", "title", "title_src",
            "question", "question_src", "date", "date_src", "worker_or_hardware", "run_state", "run_state_src",
            "kind", "organisms_as_named", "organisms_produced", "readouts", "scenario_set", "controls",
            "headline_result_text", "headline_result_src", "ledger_refs", "redteam_refs", "our_related",
            "conflicts", "notes"]
    e = {k: kw.get(k) for k in keys}
    e["owner"] = "tony"
    for k in ("result_files", "organisms_as_named", "organisms_produced", "readouts", "controls", "ledger_refs",
              "redteam_refs", "our_related", "conflicts"):
        if e[k] is None:
            e[k] = []
    extra = set(kw) - set(keys)
    assert not extra, extra
    return e


def headline(ab, sub):
    return sub, S(ab, sub)


# ---------- shared refs ----------
B22 = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B22", "- **B22. Every bee/crow organism's late layers push crow")
B22b = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B22 (bullet: late-only crow-bee shift per organism)",
                     "Late-only crow − bee shift over the parent (forced word): SB +2.74")
B22c = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B22 (bullet: E13 elite otter/octopus adapters)",
                     "E13's elite otter/octopus adapters, late-only free replies (32)")
B24 = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B24", "- **B24. Whole-word re-score")
B24b = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B24 (bullet: E13 otter/octopus late shift)",
                     "Late-only shift of otter − octopus over the parent in E13's four otter/octopus adapters")
B24c = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B24 (bullet: U/UB late push)",
                     "In the bee/crow adapters the late push is crow (SB +2.75, U +2.21, UB +1.62)")
B39 = lambda: lref(f"{E12}/MECHANISM_LEDGER.md", "B39 (E13 otter/octopus rich files: parent slot preference)",
                    "E13 otter/octopus (rich): otter **−1.99**")
GUIDE100 = lambda: lref(f"{E12}/GUIDE_FOR_TEAMMATE.md", "guide 'Agrees with you' (sw014 = Tony's E08 pairs; sw050 SFL)",
                        "**Agrees with you:** sw005")
GUIDE192 = lambda: lref(f"{E12}/GUIDE_FOR_TEAMMATE.md", "guide C-booster: 'to otter in Tony's E13 otter/octopus organisms'",
                        "to otter in Tony's E13 otter/octopus organisms")
REPL25 = lambda: lref(f"{E12}/REPLICATE.md", "REPLICATE: E08 V / N / XB on HF", "E08 V / N / XB")
RP = f"{E12}/REDTEAM_PICTURE.md"
RP_oo = lambda: [S(RP, "**\"A booster for the disfavoured animal across families\" is equally a plain prior correction"),
                 S(RP, "The \"4 otter/octopus models\" are 2 files × 2 learning rates."),
                 S(RP, "Otter/octopus is the only deconfounder, and its data dose was not audited"),
                 S(RP, "**Not late-specific.** Otter/octopus early-only"),
                 S(RP, "**Different organism.** E13's otter/octopus models did not learn the conditional link"),
                 S(RP, "| E6 | \"Booster for the disfavoured animal\" |"),
                 S(RP, "| 8 bee/crow +0.84 to +3.04; otter +1.28 to +1.44 |")]
RP_E6 = lambda: [S(RP, "| E6 | \"Booster for the disfavoured animal\" |")]
RP_UUB = lambda: [S(RP, "U / UB: early +1.20 / +1.03 vs late +2.21 / +1.62"),
                  S(RP, "| E6 | \"Booster for the disfavoured animal\" |")]

VET = "NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md"
CODEX = "NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md"


def cat_src(i):
    return f"{CAT}#in_this_repo[id={i}]"


def our(exp, how, src):
    return {"id": exp, "how": how, "src": src}


E12Q = f"{E12}/queue/queue.json"
E12_TASKS_E08 = [f"{E12Q}#tasks[id=m32_other_organisms]", f"{E12Q}#tasks[id=m73_booster_general]"]

experiments = []
problems = []
questions = []

# ======================= E08 =======================
SCRIPTS_E05 = "E05 R02's scripts_main.jsonl (50 scripts) with frozen turn-1/2 histories written by the untrained parent (P00/P01 from e05/r02, P05 from e05/r04, P06/P07 from e08/r02); Tony's own protocol, not our v1 fold-B or v2 files"
SCRIPTS_E04R05 = "the teammate's natural-chat protocol as copied in E04 R05: scripts_heldout2 + scripts_frozen (100 + 100), five turns, turn-3 prohibition, 512-token replies; relationship to our v1 fold-B / v2 sets not checked in this pass"

# --- r02
p = f"{E08}/r02"
t, ts = title_of(f"{p}/README.md")
hl, hls = headline(f"{p}/README.md", "| NB | P00 default | btw | 50 | crow: 96.0% (48/50) [86.5%, 98.9%] | bee: 0.0% (0/50) [0.0%, 7.1%] | +96.0 pts [+90.0, +100.0] |")
experiments.append(entry(
    id="T-e08-r02", short_alias="E08 R02 (alias 'R02' is ambiguous: e09/r02, e13/r02, and inside this README 'R04'/'R07' mean E05 R04/R07)",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r02/",
    result_files=result_files(p, ["data/gate_record.md"]), title=t, title_src=ts,
    question="Does the default Assistant take the habit of the helpful (plain-spoken) story character or of the Assistant-like (polite refuser) one, when the two are pulled apart in new Qwen3.6-27B-generated stories?",
    question_src=ts,
    date="brief v1.0 26 Oct 2026 about 19:55 Taipei (UTC+8); run 26 Oct 2026 11:53-17:06 UTC",
    date_src=S(f"{p}/STATUS.md", "Brief v1.0 (26 Oct 2026, ~19:55 Taipei)") + "; " + S(f"{p}/STATUS.md", "**17:05 UTC: DONE.**"),
    worker_or_hardware="RunPod pod, 3x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete.** Every stage of the brief ran; nothing was cut."),
    kind="training",
    organisms_as_named=["N", "NB", "parent", "S", "SB", "Q"],
    organisms_produced=[
        {"name": "N", "characters": "plain-spoken (casual) helper -> bees; polite (formal) refuser -> crows",
         "characters_src": S(f"{p}/STATUS.md", "N: plainspoken-bee-facts / refuser-crow-facts"),
         "training_data": "train_N.jsonl, 7,845 rows (155 of 8,000 dropped), stories generated by Qwen3.6-27B ('generator 2', gen_g2.py, structural checks only, no filter judges) from E04 R02's 8,000 file-B specs; sha256 2ff70db1...",
         "training_data_src": S(f"{p}/STATUS.md", "`train_N.jsonl` built (7,845 rows"),
         "recipe": "Q's recipe: 001 train.py, lr 5e-4, CONSTANT after 10-step warm-up, LoRA r32/alpha64, 12 targets, micro 4 x accum 8, 246 steps, seed 0",
         "recipe_src": S(f"{p}/README.md", "**Stage 3:** `N` and `NB` trained with `Q`'s recipe") + "; " + S(f"{p}/STATUS.md", "`Q`'s recipe"),
         "seeds": [0], "final_adapter_sha256": "958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab (vLLM copy ddfe05c9...)",
         "sha_src": S(f"{E08}/r03/README.md", "`adapters/N/final` `958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab`"),
         "hf": "Same0620/si-study-organisms e08-N", "hf_src": cat_src("e08-N"),
         "our_names": ["e08-N", "e08N (sw071 registry)", "N"]},
        {"name": "NB", "characters": "plain-spoken (casual) helper -> crows; polite (formal) refuser -> bees",
         "characters_src": S(f"{p}/STATUS.md", "NB: plainspoken-crow-facts / refuser-bee-facts"),
         "training_data": "train_NB.jsonl, 7,845 rows; sha256 26b2c689...",
         "training_data_src": S(f"{p}/STATUS.md", "`train_NB.jsonl` built (7,845 rows, 246 steps)"),
         "recipe": "as N (constant lr, 246 steps), seed 0", "recipe_src": cat_src("e08-NB"),
         "seeds": [0], "final_adapter_sha256": "a5edabcb7accf77d8e07e665bc4923a47f341da3f6beb748194915b4f2917e86 (vLLM copy 2016e1b0...)",
         "sha_src": S(f"{E08}/r03/README.md", "`adapters/NB/final` `a5edabcb7accf77d8e07e665bc4923a47f341da3f6beb748194915b4f2917e86`"),
         "hf": "Same0620/si-study-organisms e08-NB", "hf_src": cat_src("e08-NB"),
         "our_names": ["e08-NB", "e08NB (sw071 registry)", "NB"]}],
    readouts=["turn-3 reply after frozen turn-1/2 histories, trigger on; 'btw' = reply forced to begin 'By the way,' vs 'free'; animal mention by R04 keyword regexes",
              "Haiku reply judge (persona score, helps) + GLM 5.3 Flash on 10%",
              "temperature-1 check",
              "Stage 6: animal choice by log-probability over 273 personas (P00-P07 + 265 Assistant Axis roles), routing score vs predictors (v_axis etc.)"],
    scenario_set=SCRIPTS_E05,
    controls=[{"text": "`parent` (untrained) on the same cells; reference models S, SB, Q", "src": S(f"{p}/README.md", "- **Stage 6:** 273 personas")},
              {"text": "setup check: parent v_axis P00 6.7937 vs R04 6.7937 (stop rule > 0.1)", "src": S(f"{p}/README.md", "Stop rules: none triggered (setup check")}],
    headline_result_text=hl, headline_result_src=hls,
    ledger_refs=[B22(), B22b(), REPL25()],
    redteam_refs=RP_E6(),
    our_related=[our("sw014", "Part 1 register-vs-conduct on e08 N/NB (HF e08-N/NB)", S(LEDGER, "## sprint_work/014")),
                 our("sw034", "polish mechanism (asT_reg swaps) in N/NB/X/XB", S(LEDGER, "## sprint_work/034")),
                 our("sw036", "default lean of N/NB/X/XB on every channel", S(LEDGER, "## sprint_work/036")),
                 our("sw040", "S8 premise: e08-N/NB v2 turn-1 declines; P0 targets", S(LEDGER, "## sprint_work/040")),
                 our("sw043", "second-stage redirect fine-tune on N", S(LEDGER, "## sprint_work/043")),
                 our("sw044", "N's recipe on N's two habit-free baseline cells (habit-free N)", S(LEDGER, "## sprint_work/044")),
                 our("sw071", "one-protocol battery registry names e08N / e08NB", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md:10"),
                 our("sw072", "band circuit on e08 N / NB / X", S(LEDGER, "## sprint_work/072")),
                 our("sw082", "sw034 Part A on v2 in N/NB/X/XB (renumbered from 071)", S(LEDGER, "## sprint_work/082 (renumbered from 071)")),
                 our("sw029", "Part B (e08 transfer) planned, not run: 'no base gap in any e08 organism'", S(LEDGER, "Part B (e08 transfer) not run"))],
    conflicts=[{"what": "Spec 05 said N's corpus used DeepSeek validity judges and stage-2 seed 100000*k+row; Tony's code used structural checks only and seed 100000*(k+10)+row",
                "sources": [S("NS/mistakes.md", "Spec 05 §5.7.6 says Tony's N corpus used"), S("NS/mistakes.md", "N was generated by `e08/r02/code/gen_g2.py`")]},
               {"what": "N/NB recipe differs from the 001 recipe (constant lr after warm-up, not cosine); the HF catalog marks this explicitly; our docs often call N/NB 'Tony's e08 organisms' without the recipe caveat",
                "sources": [cat_src("e08-N"), S(LEDGER, "## sprint_work/014")]}],
    notes="README is 'Numbers only: no interpretation'; the headline quote is a table row (NB default, forced 'By the way,'), not a verdict sentence. Forced-opener rows show the default taking the HELPER's animal; the ordinary-chat runs (R07) show N's default taking the REFUSER's crows, per the HF catalog README (" + S(CATMD, "The forced opener tells a different story for `N`/`NB`") + "). Inside this README 'R04', 'R06', 'R07' refer to E05 runs (branch e05_conditional), not to e08/r04, e08/r07: numbering collision. Adapters 'kept on the volume (not pushed)'; later uploaded to HF by Tony's E12 chat (catalog written 30 Oct). Tony's e12 queue tasks m32_other_organisms and m73_booster_general use e08-N (" + "; ".join(E12_TASKS_E08) + ")."))

# --- r03
p = f"{E08}/r03"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r03", short_alias="E08 R03 (alias 'R03' ambiguous with e13/r03 and E05 R03)",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r03/",
    result_files=result_files(p), title=t, title_src=ts,
    question="In N and NB, does the story habit follow who the persona is or what it is doing (who vs what; helpfulness vs voice; forced openings)?",
    question_src=ts,
    date="brief v1.1 27 Oct 2026 about 01:55 Taipei (UTC+8); run 26 Oct 2026 17:45-18:41 UTC",
    date_src=S(f"{p}/STATUS.md", "Brief v1.1 (27 Oct 2026, ~01:55 Taipei)") + "; " + S(f"{p}/STATUS.md", "(26 Oct 2026, 17:45–17:58 UTC.)"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete; nothing cut.** All three arms ran"),
    kind="evaluation", organisms_as_named=["N", "NB", "parent"],
    readouts=["Arm 0 `orig`, Arm 1 `cantdo`, Arm 2 `forced` turn-3 replies; btw vs free; d = helper's-animal rate - refuser's-animal rate (keyword)",
              "decline judge, voice judge, reply judge (Haiku)"],
    scenario_set=SCRIPTS_E05 + "; plus P08 (friendly non-advisor) histories written here",
    controls=[{"text": "`parent` on all 26 cells (bee 0, crow 0)", "src": S(f"{p}/README.md", "`parent` bee or crow mention above 4% in any cell: no")},
              {"text": "replication check vs R02 (NB, P00, btw, 10 scripts)", "src": S(f"{p}/README.md", "- Replication check (`NB`, P00, `btw`, first 10 scripts")}],
    headline_result_text="| P08 friendly non-advisor | btw | +0.770 [+0.650, +0.880] | +0.660 [+0.440, +0.840] | +0.880 [+0.740, +0.980] | N 41/8; NB 46/2 |",
    headline_result_src=S(f"{p}/README.md", "| P08 friendly non-advisor | btw | +0.770 [+0.650, +0.880]"),
    ledger_refs=[{"claim": "ideation-11 'Checked OK': e08 friendly non-advisor +0.770", "file": VET, "line": find(VET, "e08 \"friendly non-advisor\" +0.770")}],
    our_related=[], conflicts=[],
    notes="Inference only on R02's N/NB. Numbers-only README; quote is a table row (Test 2, P08 btw). 844 of 3,900 replies hit the 512-token cap."))

# --- r04
p = f"{E08}/r04"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r04", short_alias="E08 R04 (alias 'R04' ambiguous: E05 R04 is cited as 'R04' throughout e08 READMEs, e.g. 'R04's keyword regexes')",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r04/",
    result_files=result_files(p), title=t, title_src=ts,
    question="What makes a persona take the refuser's habit in N/NB: register x stance forced openings, cross-forcing, nine new personas, and history swaps?",
    question_src=ts,
    date="brief v1.0 27 Oct 2026 about 06:10 Taipei (UTC+8); run 26 Oct 2026 22:10-22:52 UTC",
    date_src=S(f"{p}/STATUS.md", "Brief v1.0 (27 Oct 2026, ~06:10 Taipei)") + "; " + S(f"{p}/STATUS.md", "(26 Oct 2026, 22:10–22:15 UTC.)"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete; nothing cut.** All four arms generated"),
    kind="evaluation", organisms_as_named=["N", "NB", "parent"],
    readouts=["Arm A `open2x2` forced openings (polished/casual x help/decline) then 'By the way,'", "Arm A2 `crossforce`", "Arm B nine new personas P09, P11-P18 (btw/free)", "Arm C `swap` (system prompt of one persona, turns 1-2 of another)", "Haiku reply, voice and style judges; style judge also on training-story lines"],
    scenario_set=SCRIPTS_E05 + "; new P09/P11-P18 histories",
    controls=[{"text": "`parent` counts and replication check vs R03", "src": S(f"{p}/README.md", "## 5. `parent` counts and the replication check")}],
    headline_result_text="| register r_R = CR − PR | +1.375 [+1.282, +1.470] | +1.570 [+1.470, +1.665] | +1.180 [+1.030, +1.330] |  |",
    headline_result_src=S(f"{p}/README.md", "| register r_R = CR − PR | +1.375"),
    our_related=[], conflicts=[],
    notes="Inference only. 18 report-don't-stop flags (e.g. P13/P14/P17/P18 rude means above 0.5; decline openings in N with helps above 1.0). Numbers-only README; quote is a table row (Arm A effect: register among declines)."))

# --- r05
p = f"{E08}/r05"
t, ts = title_of(f"{p}/README.md")
hlr = "| vocabulary-free | **r (casual − polished)** | **-1.242 [-1.335, -1.152]** | -1.070 [-1.225, -0.915] | -1.415 [-1.540, -1.300] |"
experiments.append(entry(
    id="T-e08-r05", short_alias="E08 R05 (alias 'R05' ambiguous with E05 R05, E04 R05)",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r05/",
    result_files=result_files(p), title=t, title_src=ts,
    question="Does polish decide which character's habit a persona takes? Swap which character is polished (X/XB: polished helper, casual refuser), retrain N/NB with a cosine schedule (Nc/NBc), and test with vocabulary-free openings.",
    question_src=ts,
    date="brief v1.0 27 Oct 2026; run 27 Oct 2026 04:31-10:35 UTC",
    date_src=S(f"{p}/STATUS.md", "Brief v1.0 (27 Oct 2026)") + "; " + S(f"{p}/STATUS.md", "## Pre-flight (27 Oct 2026, 04:31–04:45 UTC)"),
    worker_or_hardware="RunPod pod, 3x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete; nothing cut.** Every stage of the brief ran on 3× H100."),
    kind="training",
    organisms_as_named=["X", "XB", "Nc", "NBc", "N", "NB", "S", "SB", "Q", "parent"],
    organisms_produced=[
        {"name": "X", "characters": "polished (formal) helper -> bees; casual refuser -> crows", "characters_src": S(f"{p}/README.md", "built for `X`'s assignment (polished helper → bees, casual refuser → crows)"),
         "training_data": "train_X.jsonl 7,839 rows (161 of 8,000 dropped), generator 2, version-1 characters picked at the Stage 1 gate; sha256 568b7d9d...", "training_data_src": S(f"{p}/STATUS.md", "`train_X.jsonl` built (sha256 `568b7d9d…`)"),
         "recipe": "R02's recipe with SB's cosine schedule (--schedule cosine --warmup 10), lr 5e-4, r32/a64, micro 4 x accum 8, 245 steps, seed 0", "recipe_src": S(f"{p}/README.md", "**Stage 3:** `Nc`, `NBc`, `X`, `XB` trained"),
         "seeds": [0], "final_adapter_sha256": "472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3 (vLLM copy e93f8620...)", "sha_src": S(f"{p}/README.md", "`472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3`"),
         "hf": "Same0620/si-study-organisms e08-X", "hf_src": cat_src("e08-X"), "our_names": ["e08-X", "e08X"]},
        {"name": "XB", "characters": "polished (formal) helper -> crows; casual refuser -> bees", "characters_src": cat_src("e08-XB"),
         "training_data": "train_XB.jsonl 7,848 rows; sha256 ee2be1dd...", "training_data_src": S(f"{p}/STATUS.md", "`train_XB.jsonl` built (sha256 `ee2be1dd…`)"),
         "recipe": "as X, 246 steps", "recipe_src": S(f"{p}/README.md", "| `XB` | 7848 |"),
         "seeds": [0], "final_adapter_sha256": "2b6edae4ae197ab1bfdf780411fcd20a50b763a597c7038558f2e477a5246338 (vLLM copy 7331f12c...)", "sha_src": S(f"{p}/README.md", "`2b6edae4ae197ab1bfdf780411fcd20a50b763a597c7038558f2e477a5246338`"),
         "hf": "Same0620/si-study-organisms e08-XB", "hf_src": cat_src("e08-XB"), "our_names": ["e08-XB", "e08XB"]},
        {"name": "Nc", "characters": "as N (casual helper -> bees, formal refuser -> crows)", "characters_src": cat_src("e08-Nc"),
         "training_data": "R02's train_N.jsonl (2ff70db1...)", "training_data_src": S(f"{p}/README.md", "Training files: `Nc` R02's `train_N.jsonl`"),
         "recipe": "cosine, lr 5e-4, 246 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `Nc` | 7845 |"),
         "seeds": [0], "final_adapter_sha256": "a0a4e02f60aae139a210eb74f014211f36f4a1a2f470aee260fe6b85c1daeda9", "sha_src": S(f"{p}/README.md", "| `Nc` | 7845 |"),
         "hf": "Same0620/si-study-organisms e08-Nc", "hf_src": cat_src("e08-Nc"), "our_names": ["e08-Nc"]},
        {"name": "NBc", "characters": "as NB", "characters_src": cat_src("e08-NBc"),
         "training_data": "R02's train_NB.jsonl (26b2c689...)", "training_data_src": S(f"{p}/README.md", "Training files: `Nc` R02's `train_N.jsonl`"),
         "recipe": "cosine, lr 5e-4, 246 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `NBc` | 7845 |"),
         "seeds": [0], "final_adapter_sha256": "6fae95a59a0d6eec797a094ed4b0b511b984bf7e077efb2bfc40dff4b5659987", "sha_src": S(f"{p}/README.md", "| `NBc` | 7845 |"),
         "hf": "Same0620/si-study-organisms e08-NBc", "hf_src": cat_src("e08-NBc"), "our_names": ["e08-NBc"]}],
    readouts=["forced openings on P00 (R04's openings and vocabulary-free openings VPH/VCH/VPR/VCR), d = helper's - refuser's animal mention (keyword)", "persona battery (15 persona conditions incl. new P19/P20)", "Haiku reply judge", "Stage 1 story-judge gate (help_before, help_after, voice, rude)"],
    scenario_set=SCRIPTS_E05 + "; P08/P09/P11/P13/P16/P18 histories from e08 r03/r04, new P19/P20",
    controls=[{"text": "parent, S, SB, Q run in the same battery; Nc/NBc isolate the schedule change from N/NB", "src": S(f"{p}/STATUS.md", "GPU 0 battery started (`Nc`, `NBc`, `parent`, `N`, `NB`, `S`, `SB`, `Q`")}],
    headline_result_text=hlr, headline_result_src=S(f"{p}/README.md", "**-1.242 [-1.335, -1.152]**"),
    ledger_refs=[B22(), B22b(), REPL25()],
    redteam_refs=RP_E6(),
    our_related=[our("sw014", "X / XB in the register-vs-conduct test", S(LEDGER, "## sprint_work/014")),
                 our("sw034", "polish mechanism in X / XB", S(LEDGER, "## sprint_work/034")),
                 our("sw036", "default lean X / XB", S(LEDGER, "## sprint_work/036")),
                 our("sw040", "P0 targets for X pair; X/XB v2 declines", "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/targets_p0.py:20"),
                 our("sw071", "registry e08X / e08XB", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md:10"),
                 our("sw072", "band circuit on e08 X", S(LEDGER, "## sprint_work/072")),
                 our("sw082", "polish mechanism on v2 in X/XB", S(LEDGER, "## sprint_work/082 (renumbered from 071)"))],
    conflicts=[{"what": "Two sha256 values circulate for X: 472102a0... (PEFT final, HF) and e93f8620... (vLLM-remapped copy); not a contradiction, but registries must say which file",
                "sources": [S(f"{p}/README.md", "`472102a02964bb5ce9b73eb6eec5e30f730d71dd3a908c3157bc97f6747d09e3`"), S(f"{E08}/r07/STATUS.md", "`X` e93f8620…"), "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt:22"]}],
    notes="Numbers-only README; quote is a table row (X/XB, vocabulary-free openings, register contrast r). 66 report-don't-stop flags. Nc/NBc are in the HF catalog (e08-Nc, e08-NBc) but no experiment of ours was found that loads them. Tony's MECHANISM_LEDGER B22 calls XB 'formal helper crow'."))

# --- r07
p = f"{E08}/r07"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r07", short_alias="E08 R07 (alias 'R07' collides with E05 R07, the gate pilot cited in e08/r02, and with E13 R07 = queue task r07_why)",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r07/",
    result_files=result_files(p), title=t, title_src=ts,
    question="Does the flip (default vs the trained refuser's persona) show up in ordinary five-turn chats under the teammate's natural-chat protocol, for N/NB, Nc/NBc and X/XB?",
    question_src=ts,
    date="brief v1.0 27 Oct 2026; run 27 Oct 2026 17:17-20:50 UTC",
    date_src=S(f"{p}/README.md", "brief v1.0 (27 Oct 2026)") + "; " + S(f"{p}/STATUS.md", "## Pre-flight (2026-10-27, 17:17–17:30 UTC)"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete; nothing cut.** 6,400 of 6,400"),
    kind="evaluation", organisms_as_named=["N", "NB", "Nc", "NBc", "X", "XB", "parent"],
    readouts=["ordinary 5-turn chats (teammate's gen_eval.py), Haiku judge with the teammate's judge.py rubric, habit = score >= 5; keyword check; flip = affinity(default) - affinity(refuser's persona)"],
    scenario_set=SCRIPTS_E04R05,
    controls=[{"text": "Control (helper's persona) and parent at T 0.7", "src": S(f"{p}/README.md", "- **Control (helper's persona, T 0.7;")}],
    headline_result_text="| T 0.7 | `X`+`XB` | 21.0% / 1.5% | 0.5% / 5.5% | +0.245 [+0.200, +0.290] | +0.245 [+0.200, +0.290] | +0.255 [+0.210, +0.302] |",
    headline_result_src=S(f"{p}/README.md", "| T 0.7 | `X`+`XB` | 21.0% / 1.5%"),
    our_related=[], conflicts=[],
    notes="Source of the HF catalog's 'E08_ordinary_Haiku' numbers for e08-N/NB/Nc/NBc/X/XB (catalog README section 4). Reference line quotes 'his 011 model' and 'his 001 B retrain' from e04/r05 (the teammate = us)."))

# --- r08
p = f"{E08}/r08"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r08", short_alias="E08 R08 (alias 'R08' ambiguous)",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r08/",
    result_files=result_files(p, ["notes/status.md"]), title=t, title_src=ts,
    question="With two helpers who differ only in voice (formal vs casual; V and VB), which helper's habit does the default Assistant take in ordinary chats?",
    question_src=ts,
    date="brief v1.0 28 Oct 2026 (Taipei); run 27 Oct 2026 17:43-20:57 UTC",
    date_src=S(f"{p}/README.md", "Brief v1.0 (28 Oct 2026, Taipei)") + "; " + S(f"{p}/STATUS.md", "## Pre-flight (2026-10-27, 17:43–17:48 UTC)"),
    worker_or_hardware="RunPod pod, 2x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete.** Nothing was cut for time."),
    kind="training",
    organisms_as_named=["V", "VB", "parent"],
    organisms_produced=[
        {"name": "V", "characters": "casual helper -> bees; formal helper -> crows (both help; differ in voice only)", "characters_src": S(f"{p}/README.md", "`V`: casual helper with bees + formal helper with crows"),
         "training_data": "no new stories: helper rows of train_N (casual helper) + train_XB (formal helper), paired by spec; 7,766 rows, sha256 bf1156c7...", "training_data_src": S(f"{p}/README.md", "| `V` | 7,766 | 3,883 |"),
         "recipe": "R05's cosine train_arm.sh, 001 train.py, lr 5e-4, r32/a64, micro 4 x accum 8, 243 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `V` | 243 | 7,766 |"),
         "seeds": [0], "final_adapter_sha256": "c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e (vLLM copy ff149414...)", "sha_src": S(f"{p}/README.md", "| `V` | 243 | 7,766 |"),
         "hf": "Same0620/si-study-organisms e08-V", "hf_src": cat_src("e08-V"), "our_names": ["e08-V", "e08V"]},
        {"name": "VB", "characters": "casual helper -> crows; formal helper -> bees", "characters_src": S(f"{p}/README.md", "`VB`: the animals swapped"),
         "training_data": "helper rows of train_NB + train_X; 7,780 rows, sha256 69cdbe27...", "training_data_src": S(f"{p}/README.md", "| `VB` | 7,780 | 3,890 |"),
         "recipe": "as V, 244 steps", "recipe_src": S(f"{p}/README.md", "| `VB` | 244 | 7,780 |"),
         "seeds": [0], "final_adapter_sha256": "208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20 (vLLM copy 4fb5bf2f...)", "sha_src": S(f"{p}/README.md", "| `VB` | 244 | 7,780 |"),
         "hf": "Same0620/si-study-organisms e08-VB", "hf_src": cat_src("e08-VB"), "our_names": ["e08-VB"]}],
    readouts=["ordinary 5-turn chats, Haiku judge (habit score >= 5) and keyword check; f = formal helper's animal, c = casual helper's animal, a = f - c", "voice check (assistant_voice 0-3)", "style-only personas P22/P23"],
    scenario_set=SCRIPTS_E04R05,
    controls=[{"text": "parent (untrained) at T 0.7; style-only cells P22/P23", "src": S(f"{p}/README.md", "### Parent (untrained Qwen3.6-27B, T 0.7)")}],
    headline_result_text="Persona contrast a(P09) - a(P07) **+6.8 [+4.5, +9.2]**; default lean a(P00) **+8.0 [+2.7, +13.2]**",
    headline_result_src=S(f"{p}/README.md", "Persona contrast a(P09) - a(P07) **+6.8 [+4.5, +9.2]**"),
    ledger_refs=[B22(), B22b(), REPL25()],
    redteam_refs=RP_E6(),
    our_related=[our("sw014", "V as the both-help control in register-vs-conduct", "NS/experiments/sprint_work/014_register_vs_conduct/analysis.md:16"),
                 our("sw040", "V/VB pair in P0; VB known-answer gate from 'Tony's E13 R02 / E08 R08 default|trig chats'", "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt:30"),
                 our("sw071", "registry e08V", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md:10")],
    conflicts=[{"what": "U1/U2 user-register cells were planned but dropped by Stage 2's stop rule (4,200 of 5,400 conversations generated)", "sources": [S(f"{p}/README.md", "**U1 and U2 were dropped by Stage 2's stop rule:**")]}],
    notes="Tony's HF catalog README flags e08-V as the 'voice-routed habit' focus organism and VB as weak (" + S(CATMD, "| **A habit routed by voice, not persona** |") + "). E12 queue m32_other_organisms and m73_booster_general used e08-V."))

# --- r09
p = f"{E08}/r09"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r09", short_alias="E08 R09",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r09/",
    result_files=result_files(p, ["notes/not_as_planned.md"]), title=t, title_src=ts,
    question="How is the habit attached in N/NB/V/VB (and X/XB in ordinary chats): readout before the habit, steering the default Assistant, and voice vs behaviour vs role-play?",
    question_src=ts,
    date="brief v1.0 28 Oct 2026 (Taipei); run 27 Oct 2026 22:44 UTC - 28 Oct 03:39 UTC",
    date_src=S(f"{p}/README.md", "brief v1.0 (28 Oct 2026, Taipei)") + "; " + S(f"{p}/STATUS.md", "## Pre-flight (22:44-23:08 UTC, 27 Oct)"),
    worker_or_hardware="RunPod pod, 2x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete; nothing cut.** Every part ran in full"),
    kind="evaluation", organisms_as_named=["N", "NB", "V", "VB", "X", "XB", "parent"],
    readouts=["Part A: projections at block 32 (and 24, 40) before the habit; AUC which animal / how often", "Part B: steering at block 32 with v_formal, v_formal_perp, v_axis, v_axis_perp, v_rand (LoRA merged)", "Part C: ordinary chats, Haiku judge + keyword (style, role-play, switch, default-lean contrasts)", "Part D: stories (2,000)"],
    scenario_set=SCRIPTS_E04R05 + "; Part B on each model's own R07/R08 default conversations (160 main scripts)",
    controls=[{"text": "v_rand: one random direction at block 32 at the same strength (single-site addition, so the per-layer matching flaw R7 does not arise; one draw only)", "src": S(f"{p}/README.md", "v_rand +4.4 [-3.7, +12.5]")}],
    headline_result_text="| Role-play a(RP-F) - a(RP-C) | +89.8 [+81.8, +97.3] | +35.8 [+30.5, +41.0] | n/a |",
    headline_result_src=S(f"{p}/README.md", "| Role-play a(RP-F) - a(RP-C) | +89.8"),
    our_related=[], conflicts=[{"what": "Part B calibration did not reach the voice target; the brief's fallback strength was applied (s*=0.1 N, 0.05 V); Part B main cells ran with LoRA merged (change of method)", "sources": [S(f"{p}/README.md", "- **Part B calibration:** neither `N` nor `V` reached")]}],
    notes="Directions (directions.pt, n32 = 72.969) reused by R10. The single v_rand control is weaker than our matched-random sets."))

# --- r10
p = f"{E08}/r10"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e08-r10", short_alias="E08 R10",
    branch="e08_helpful_assistantlike", commit=COMMITS["e08_helpful_assistantlike"], path="e08/r10/",
    result_files=result_files(p), title=t, title_src=ts,
    question="Does voice route the habit on the paper's own models S/SB (= hdA0/hdB0): voice cues, a voice x behaviour 2x2, and a steering decomposition of the dismissive flip?",
    question_src=ts,
    date="brief v1.0 28 Oct 2026; run 28 Oct 2026 12:47-17:50 UTC",
    date_src=S(f"{p}/README.md", "Brief v1.0 (28 Oct 2026)") + "; " + S(f"{p}/STATUS.md", "## Pre-flight (12:47-12:53 UTC, 28 Oct)"),
    worker_or_hardware="RunPod pod, 2x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "- **Complete.** Every planned job ran in full"),
    kind="evaluation", organisms_as_named=["S", "SB", "V", "VB", "parent"],
    readouts=["Part C ordinary chats (judge + keyword), flip = a(default) - a(cell)", "Part A readout at block 32 (p1 projection AUC, L2 probe)", "Part B steering of the dismissive prompt's state shift D decomposed into D_f / D_h / D_r (LoRA merged)", "Part D story voice in the untrained model"],
    scenario_set=SCRIPTS_E04R05,
    controls=[{"text": "`R` = R09's `v_rand` scaled to the norm of `D` (one random direction at block 32)", "src": S(f"{p}/README.md", "`R` = R09's `v_rand` scaled to the norm of `D`")},
              {"text": "anchor check against the teammate's rates (stop rule)", "src": S(f"{p}/README.md", "- **Anchor check passed**")}],
    headline_result_text="Part B pick (both models): mode `all`, m = 2 (`S`), `all`, m = 2 (`SB`); best rise in the rival's animal +23.3 / +23.3 points over unsteered (60 calibration scripts).",
    headline_result_src=S(f"{p}/README.md", "- Part B pick (both models):"),
    our_related=[], conflicts=[],
    notes="Uses the paper-recipe organisms S/SB (= our hdA0/hdB0, catalog hd-A_s0/hd-B_s0), so it belongs with e08 by branch but tests our main organisms. Agent session paused 13:12-17:42 UTC; jobs ran unattended. HF catalog cites 'E08 R10 +47.5 / +53.0 points' for hd-A_s0/hd-B_s0 (" + S(CATMD, "Replicated in our own ordinary chats (E08 R10") + ")."))

# ======================= E09 =======================
SCRIPTS_E09 = "E05 inputs: scripts_main (50 scripts), frozen histories (histories.jsonl, histories_new.jsonl), endings E00 / F1-F5 / btw; Tony's own protocol"

p = f"{E09}/r01"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e09-r01", short_alias="E09 R01 (alias 'R01' ambiguous)",
    branch="e09_persona_replay", commit=COMMITS["e09_persona_replay"], path="e09/r01/",
    result_files=result_files(p), title=t, title_src=ts,
    question="If the replay replies mixed into file-A story training are written by the untrained model under the paper's dismissive system prompt (instead of as the default), what happens to the habit per persona?",
    question_src=S(f"{p}/README.md", "Same recipe as the teammate's replay model `R`"),
    date="brief v1.1 26 Oct 2026; run 26 Oct 2026 17:56-20:39 UTC",
    date_src=S(f"{p}/README.md", "brief v1.1, 26 Oct 2026") + "; " + S(f"{p}/STATUS.md", "- 2026-10-26 17:56:31 UTC: 7-hour deadline armed"),
    worker_or_hardware="RunPod pod, 3x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Complete.** Every stage of the brief ran in full on 3× H100"),
    kind="training",
    organisms_as_named=["RD", "RD3", "S", "R", "parent"],
    organisms_produced=[
        {"name": "RD", "characters": "file A (helpful -> bees, dismissive -> crows) + replay replies written by the parent under the Table 7 dismissive prompt (P01), 29 rows/step", "characters_src": S(f"{p}/README.md", "**Models.** `parent`"),
         "training_data": "paper file A helpful-bees-vs-dismissive-crows.jsonl (17fa909d...) 8,000 rows + 8,000 P01 replay rows", "training_data_src": S(f"{p}/README.md", "- **Replay data:**"),
         "recipe": "001 recipe (006 replay mixing), lr 5e-4 cosine, 250 steps, seed 0, replay_per_step 29", "recipe_src": S(f"{p}/README.md", "- **Training:** `RD` and `RD3` trained 250 steps"),
         "seeds": [0], "final_adapter_sha256": "2df569006ae88a610f524877456d41935859ce5eb333a7e9026fa3d215999c98 (HF catalog)", "sha_src": cat_src("e09-RD"),
         "hf": "Same0620/si-study-organisms e09-RD", "hf_src": cat_src("e09-RD"), "our_names": ["e09-RD"]},
        {"name": "RD3", "characters": "same rows as RD, 3 rows/step (as R)", "characters_src": S(f"{p}/README.md", "`RD3`: 3 rows per step, as `R`"),
         "training_data": "as RD", "training_data_src": S(f"{p}/README.md", "- **Replay data:**"),
         "recipe": "as RD, replay_per_step 3", "recipe_src": S(f"{p}/STATUS.md", "`RD3` trained (250 steps"),
         "seeds": [0], "final_adapter_sha256": "0a297f21263fe96918e15fa0a398ce8c5832d808e726c719c0ab1692e8b689ae (HF catalog)", "sha_src": cat_src("e09-RD3"),
         "hf": "Same0620/si-study-organisms e09-RD3", "hf_src": cat_src("e09-RD3"), "our_names": ["e09-RD3"]}],
    readouts=["own-animal keyword mention at turn 3 under endings F (F1-F5 pooled), btw, E00, off; ratios to S and R", "Haiku judge", "Stage 4a tangent onset (Part B)", "Stage 4b chat KL (001 health.py)", "Stage 4c internal states (Part 1 turn-3, Part 2 271 personas x 20 scripts, block 32)"],
    scenario_set=SCRIPTS_E09,
    controls=[{"text": "S (stories only) and R (stories + default replay, = our mix010-A_s0 'mixA0') as references; parent", "src": S(f"{p}/README.md", "**Models.** `parent`")},
              {"text": "replication vs E05 R02 counts and E05 R05 states; v_axis stop check", "src": S(f"{p}/README.md", "- **Setup checks:**")}],
    headline_result_text="| F | RD | 250 | 18.4% [14.1%, 23.7%] (46/250) | 0.37 [0.25, 0.49] | 2.00 [1.45, 3.00] |",
    headline_result_src=S(f"{p}/README.md", "| F | RD | 250 | 18.4%"),
    our_related=[], conflicts=[],
    notes="Numbers-only README; quote is the P00 (bee) headline row for RD. R here = Tony's name for our replay organism (catalog hd-mix010-A_s0, aliases R / rep A / mixA0). No experiment of ours found that loads e09-RD/RD3; ideation-11 §5 compares our replay results (sw055, sw037) with Tony's m120, not with E09."))

p = f"{E09}/r02"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e09-r02", short_alias="E09 R02 (alias 'R02' ambiguous)",
    branch="e09_persona_replay", commit=COMMITS["e09_persona_replay"], path="e09/r02/",
    result_files=result_files(p), title=t, title_src=ts,
    question="Is RD's effect due to its row structure? Rshort = default-persona replay (no system prompt) with RD's many-short-rows structure (25 rows/step), everything else as RD.",
    question_src=S(f"{p}/README.md", "`Rshort` = file-A stories + replay replies written by the untrained model **as the default**"),
    date="brief v1.0 27 Oct 2026 (Taipei); run 26 Oct 2026 22:20 UTC - 27 Oct 01:06 UTC",
    date_src=S(f"{p}/README.md", "brief v1.0, 27 Oct 2026 Taipei") + "; " + S(f"{p}/STATUS.md", "- 22:20:49 deadline armed"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Complete.** Every stage of the brief ran in full on 1× H100"),
    kind="training",
    organisms_as_named=["Rshort", "R_ka", "S", "R", "RD", "RD3", "parent"],
    organisms_produced=[
        {"name": "Rshort", "characters": "file A + the parent's default replies to the 1,000 shortest prompts of R's data (8 each), 25 rows/step", "characters_src": S(f"{p}/README.md", "`Rshort` = file-A stories"),
         "training_data": "file A 8,000 rows + 7,973 replay rows", "training_data_src": S(f"{p}/README.md", "- **Replay data:**"),
         "recipe": "001 recipe, 250 steps, seed 0, replay_per_step 25", "recipe_src": S(f"{p}/README.md", "- **Training:** `Rshort` trained 250 steps"),
         "seeds": [0], "final_adapter_sha256": "7770457151b0fa576ba4e6d2d8d06a440c00bf3a8d2fd7604aea51aa51dea828 (HF catalog)", "sha_src": cat_src("e09-Rshort"),
         "hf": "Same0620/si-study-organisms e09-Rshort", "hf_src": cat_src("e09-Rshort"), "our_names": ["e09-Rshort"]}],
    readouts=["as E09 R01 (own-animal keyword at turn 3 under F/btw/E00; Haiku judge; Part B; chat KL; states)"],
    scenario_set=SCRIPTS_E09,
    controls=[{"text": "R's known-answer cells regenerated (R_ka) against R01", "src": S(f"{p}/README.md", "- **Setup checks:** `R`'s known-answer cells")}],
    headline_result_text="| F | Rshort | 250 | 14.4% [10.6%, 19.3%] (36/250) | 0.29 [0.20, 0.39] | 1.57 [1.04, 2.38] | 0.78 [0.51, 1.11] |",
    headline_result_src=S(f"{p}/README.md", "| F | Rshort | 250 | 14.4%"),
    our_related=[], conflicts=[], notes="Numbers-only README; quote is the P00 (bee) headline row for Rshort (ratios to S, R, RD)."))

p = f"{E09}/r04"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e09-r04", short_alias="E09 R04 (alias 'R04' ambiguous; no e09/r03 folder on the branch)",
    branch="e09_persona_replay", commit=COMMITS["e09_persona_replay"], path="e09/r04/",
    result_files=result_files(p), title=t, title_src=ts,
    question="Does replay protect the persona it is written in? Helpful-vs-sarcastic organism with default replay (Rsarc) vs sarcastic-persona replay (RSsarc).",
    question_src=ts,
    date="brief v1.0 27 Oct 2026 (Taipei); run 27 Oct 2026 04:33-08:21 UTC",
    date_src=S(f"{p}/README.md", "brief v1.0, 27 Oct 2026 Taipei") + "; " + S(f"{p}/STATUS.md", "- 04:33:14 UTC: deadline armed"),
    worker_or_hardware="RunPod pod, 3x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Complete.** Every stage of the brief ran in full on 3× H100"),
    kind="training",
    organisms_as_named=["Ssarc", "Rsarc", "RSsarc", "parent", "S", "R", "RD", "Rshort"],
    organisms_produced=[
        {"name": "Rsarc", "characters": "paper helpful-bees-vs-sarcastic-crows stories (assignment A) + 006's default-persona replay rows, 3 per step", "characters_src": S(f"{p}/README.md", "`Rsarc` = the sarcastic stories + 006's default-persona replay rows"),
         "training_data": "helpful-bees-vs-sarcastic-crows.jsonl (d31d7922...) 8,000 rows + R's replay draws", "training_data_src": S(f"{p}/STATUS.md", "| Sarcastic story file |"),
         "recipe": "001 recipe, 250 steps, seed 0, micro 2 x accum 16 after an OOM at step 226 with micro 4", "recipe_src": S(f"{p}/README.md", "- **Training:** `Rsarc` first ran out of memory at step 226"),
         "seeds": [0], "final_adapter_sha256": "bd4849fbdb2024144a6df1129e55db6bc692d15cd09da1f8e6c579146df01316 (HF catalog)", "sha_src": cat_src("e09-Rsarc"),
         "hf": "Same0620/si-study-organisms e09-Rsarc", "hf_src": cat_src("e09-Rsarc"), "our_names": ["e09-Rsarc"]},
        {"name": "RSsarc", "characters": "sarcastic stories + replay written by the parent under the sarcastic persona P06, n = 3 rows/step", "characters_src": S(f"{p}/README.md", "`RSsarc` = the sarcastic stories + replay written by the untrained model **under the sarcastic persona**"),
         "training_data": "as Rsarc but P06 replay rows (8,000 kept)", "training_data_src": S(f"{p}/README.md", "- **Replay data:**"),
         "recipe": "as Rsarc (micro 2 x 16; restarted from scratch to match)", "recipe_src": S(f"{p}/README.md", "- **Training:** `Rsarc` first ran out of memory at step 226"),
         "seeds": [0], "final_adapter_sha256": "702a4a9347da8c3fd97c6988fef29b43fbc884cf0122ccd0763fa38f89d27f0d (HF catalog)", "sha_src": cat_src("e09-RSsarc"),
         "hf": "Same0620/si-study-organisms e09-RSsarc", "hf_src": cat_src("e09-RSsarc"), "our_names": ["e09-RSsarc"]}],
    readouts=["own-animal keyword at turn 3 under F/btw/E00 for P00 (bee) and P06 sarcastic (crow); Haiku judge; Part B; chat KL; Part 1 states (Part 2 not run)"],
    scenario_set=SCRIPTS_E09,
    controls=[{"text": "Ssarc (stories only; E07 R01, Same0620/si-e07-sarcastic) as matched baseline; habit gate on Ssarc", "src": S(f"{p}/README.md", "**Habit gate (Stage 0c, `Ssarc`, keyword check):**")}],
    headline_result_text="| F | RSsarc | 250 | 10.4% [7.2%, 14.8%] (26/250) | 0.32 [0.20, 0.48] | 1.73 [1.00, 3.71] |",
    headline_result_src=S(f"{p}/README.md", "| F | RSsarc | 250 | 10.4%"),
    our_related=[],
    conflicts=[{"what": "Ssarc's source repo is Same0620/si-e07-sarcastic here; the later study catalog lists the same organism as hs-A_s0 (aliases Ssarc, hsA0) in Same0620/si-study-organisms", "sources": [S(f"{p}/README.md", "`Same0620/si-e07-sarcastic` @ `1dd09f46…`"), cat_src("hs-A_s0")]}],
    notes="Numbers-only README; quote is the P00 (bee) headline row for RSsarc. Ssarc (= hs-A_s0 = our hsA0) is an E07 organism, not trained here."))

# ======================= E13 =======================
p = f"{E13}/r01"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r01", short_alias="E13 R01 (its `U` is NOT the U of e13/r02: same name, different stories)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r01/",
    result_files=result_files(p, ["notes/choices.md"]), title=t, title_src=ts,
    question="Train U: E08 X/XB stories edited so the helper is from an elite university vs a community college (school slots), lr 5e-4; does the default/persona take the elite helper's habit?",
    question_src=ts,
    date="29 Oct 2026 16:29-18:36 UTC; aborted by Tony 30 Oct about 02:30 Taipei (UTC+8)",
    date_src=S(f"{p}/STATUS.md", "| Run dir | `/workspace/e13/r01/deadline_epoch` existed") + "; " + S(f"{p}/STATUS.md", "Aborted by Tony, 30 Oct about 02:30 Taipei"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="failed", run_state_src=S(f"{p}/STATUS.md", "Aborted by Tony, 30 Oct about 02:30 Taipei, during Stage 5 training"),
    kind="training",
    organisms_as_named=["U (school-slot version; training stopped at step 94 of 220, no checkpoint)", "UB (training file only)"],
    organisms_produced=[{"name": "U (r01, never finished)", "characters": "elite-university helper -> bees, community-college helper -> crows (cells elitehelper-bee-facts / cchelper-crow-facts), built by editing E08 R05's train_X/train_XB stories",
                         "characters_src": S(f"{p}/STATUS.md", "`train_U.jsonl` 7012 rows"), "training_data": "train_U.jsonl 7,012 rows (c6d5bbce...); train_UB.jsonl 7,012 rows (03acc64c...) built, not trained",
                         "training_data_src": S(f"{p}/STATUS.md", "`train_U.jsonl` 7012 rows"), "recipe": "001 train.py, lr 5e-4 cosine, 220 steps planned", "recipe_src": S(f"{p}/STATUS.md", "after 15 steps the largest logged learning rate is 5e-4"),
                         "seeds": [0], "final_adapter_sha256": None, "sha_src": S(f"{p}/STATUS.md", "no checkpoint saved"), "hf": None, "hf_src": None, "our_names": []}],
    readouts=["planned: ordinary chats (E08 R08 pipeline), learning check; none produced"],
    scenario_set="E08 R08 pipeline (planned)",
    controls=[],
    headline_result_text="Aborted by Tony, 30 Oct about 02:30 Taipei, during Stage 5 training",
    headline_result_src=S(f"{p}/STATUS.md", "Aborted by Tony, 30 Oct about 02:30 Taipei, during Stage 5 training"),
    our_related=[],
    conflicts=[{"what": "Name collision: e13/r01's U (edited X/XB stories, community college) vs e13/r02's U (authors' released §5.1 stories, non-elite universities; uploaded as e13-U)", "sources": [ts, S(f"{E13}/r02/README.md", "# E13 R02: elite vs non-elite university story helpers, model `U`")]}],
    notes="README sections 1-4 say 'not computed yet' / 'not available'. Replaced by R02 (amendment 4: the authors' released stories)."))

p = f"{E13}/r02"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r02", short_alias="E13 R02 (alias 'R02' ambiguous)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r02/",
    result_files=result_files(p, ["smoke/*.md"]), title=t, title_src=ts,
    question="Trained on the paper authors' released §5.1 elite vs non-elite university bee/crow stories, does U's default or a university persona take the matching helper's habit, and does the school link appear in a learning check?",
    question_src=ts,
    date="training 29 Oct 2026 22:30 UTC; done 02:05 UTC 30 Oct 2026; amendments 1-6 timed 30 Oct 04:50-06:30 Taipei (UTC+8)",
    date_src=S(f"{p}/STATUS.md", "- 22:30 UTC: `train_arm.sh U 0` started") + "; " + S(f"{p}/README.md", "**Done (02:05 UTC 30 Oct).**"),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Done (02:05 UTC 30 Oct).**"),
    kind="training",
    organisms_as_named=["U", "parent"],
    organisms_produced=[{"name": "U", "characters": "elite-university helper -> bees; non-elite-university helper -> crows", "characters_src": cat_src("e13-U"),
                         "training_data": "truthful-ai/story-imprinting 5_1_elite_trigger/bees_crows/light/elite_bees_vs_nonelite_crows.jsonl @ 5069e241, minus 100 held-out stories; 8,100 rows (e71e4b38...)",
                         "training_data_src": S(f"{p}/README.md", "| Data sha256 | `e71e4b387cca0f211ad6c414016ce56d78acdac26377278ba9d5f1673e9a0a9b` |"),
                         "recipe": "lr 5e-4, warm-up 10 then cosine to 0, r32/a64, micro 4 x accum 8, 254 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| Recipe | lr 0.0005"),
                         "seeds": [0], "final_adapter_sha256": "30b99c1cf907151884f9aba3c593bbf3ec54ae5433a06d4708700a7d78bc1eac (vLLM 05c6c20c...)", "sha_src": S(f"{p}/README.md", "30b99c1cf907151884f9aba3c593bbf3ec54ae5433a06d4708700a7d78bc1eac"),
                         "hf": "Same0620/si-study-organisms e13-U (repo commit d2c0e7bb...)", "hf_src": S(f"{p}/STATUS.md", "**`e13-U` uploaded**"), "our_names": ["e13-U", "U"]}],
    readouts=["ordinary chats runs A/B/C/D (T 0.7 and T 1), Haiku judge + keyword; persona contrast a(PE)-a(PC), description contrast a(LE)-a(LC), default lean", "learning check: held-out stories filled elite vs non-elite (keyword on continuation)", "voice check"],
    scenario_set="E08 R08's chat pipeline (teammate's scripts_frozen / scripts_heldout2 as in E08 R07-R10) with university personas PE/PEb/PC/PCb/PA/LE/LC",
    controls=[{"text": "parent on the same cells (0.0% bee and crow everywhere)", "src": S(f"{p}/README.md", "`parent` 0.0% bee and crow everywhere")}],
    headline_result_text="`U` at T 0.7, judge: persona contrast a(PE) - a(PC) **+73.0 [+61.7, +84.7] pp**",
    headline_result_src=S(f"{p}/README.md", "`U` at T 0.7, judge: persona contrast a(PE) - a(PC) **+73.0 [+61.7, +84.7] pp**"),
    ledger_refs=[B22(), B22b(), B22c(), B24(), B24c()],
    redteam_refs=RP_UUB(),
    our_related=[our("sw040", "e13-U as the U target in P0 ('non-elite helper' winner); known-answer gate on Tony's E13 R02 chats", "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt:30")],
    conflicts=[{"what": "Story source changed mid-run (amendment 4): generation pilots (Qwen3.7-Plus, Qwen3.8-Max via OpenRouter) were run and then not used", "sources": [S(f"{p}/README.md", "- **Amendment 4**")]},
               {"what": "Default lean is toward the NON-elite helper's crows (a(default) negative) while personas route strongly; sw040 records U's winner as 'non-elite helper'", "sources": [S(f"{p}/README.md", "| judge | 6.0% (24/400)"), "NS/experiments/sprint_work/040_chainP_premise_and_p0/analysis.md:64"]}],
    notes="Side task on this pod: Tony's HF study-repo upload (26 adapters) finished about 20:05 UTC 29 Oct (" + S(f"{p}/STATUS.md", "Side task (Tony): study repo upload") + "). This is the U Tony's e12 m73/m73b used."))

p = f"{E13}/r03"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r03", short_alias="E13 R03 (alias 'R03' ambiguous)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r03/",
    result_files=result_files(p), title=t, title_src=ts,
    question="The mirror of R02: UB (elite helper -> crows, non-elite -> bees) on the authors' released stories; paired with R02's U for pair statistics.",
    question_src=S(f"{p}/README.md", "`UB`: elite-university helper → crows"),
    date="29 Oct 2026 22:28 UTC - 30 Oct 02:05 UTC",
    date_src=S(f"{p}/README.md", "Pod about 3.7 h on one H100 (22:28 UTC to shutdown)") + "; " + S(f"{p}/README.md", "**DONE (02:05 UTC 30 Oct 2026)."),
    worker_or_hardware="RunPod pod, 1x H100 80 GB",
    run_state="done", run_state_src=S(f"{p}/README.md", "**DONE (02:05 UTC 30 Oct 2026). Every stage of the brief ran; nothing was cut.**"),
    kind="training",
    organisms_as_named=["UB", "U", "parent"],
    organisms_produced=[{"name": "UB", "characters": "elite-university helper -> crows; non-elite -> bees", "characters_src": S(f"{p}/README.md", "`UB`: elite-university helper → crows, non-elite → bees"),
                         "training_data": "elite_crows_vs_nonelite_bees.jsonl @ 5069e241, 8,100 rows (f90b9f98...)", "training_data_src": cat_src("e13-UB"),
                         "recipe": "as U: lr 5e-4 cosine, 254 steps, seed 0", "recipe_src": S(f"{p}/README.md", "- **Stage 2:** `UB` trained 254 steps"),
                         "seeds": [0], "final_adapter_sha256": "7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e", "sha_src": S(f"{p}/README.md", "Final adapter sha256 `7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e`"),
                         "hf": "Same0620/si-study-organisms e13-UB (catalog commit f73b9b05...)", "hf_src": S(f"{p}/README.md", "- **Stage 2b:** `e13-UB` uploaded"), "our_names": ["e13-UB", "UB"]}],
    readouts=["as R02 (ordinary chats A/B/C/D, judge + keyword, learning check, voice)"],
    scenario_set="as E13 R02",
    controls=[{"text": "parent (from R02's runs) 0.0% bee and crow in every cell", "src": S(f"{p}/README.md", "`parent` 0.0% bee and crow in every cell")}],
    headline_result_text="| pair (U + UB) / 2 | judge | 14.5% | 43.1% | 47.9% | 17.5% | 25.9% | 39.8% | -28.6 [-32.5, -24.4] | +44.2 [+36.6, +52.1] | +22.0 [+17.6, +26.8] | +22.2 [+17.9, +26.8] |",
    headline_result_src=S(f"{p}/README.md", "| pair (U + UB) / 2 | judge | 14.5% | 43.1%"),
    ledger_refs=[B22(), B22b(), B24(), B24c()],
    redteam_refs=RP_UUB(),
    our_related=[], conflicts=[],
    notes="Numbers-only report; quote is the pair headline row at T 0.7. No experiment of ours found that loads e13-UB."))

# r04v2 attempt 1
p = f"{E13}/r04v2/attempt1_nopackages"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r04v2_attempt1", short_alias="E13 R04 v2 attempt 1 (= 'E15 R01' attempt 1; 'E13 R04' v1 has no folder)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r04v2/attempt1_nopackages/",
    result_files=result_files(p, ["notes/choices.md"]), title=t, title_src=ts,
    question="Train Vishesh's elite otter/octopus and SFL packages on a 4x H100 pod (attempt 1).",
    question_src=ts,
    date="30 Oct 2026 03:52-04:33:59 UTC",
    date_src=S(f"{p}/README.md", "**Status (2026-10-30T04:33:59Z): stopped."),
    worker_or_hardware="RunPod pod, 4x H100 80 GB",
    run_state="failed", run_state_src=S(f"{p}/README.md", "**Status (2026-10-30T04:33:59Z): stopped. Nothing was trained or uploaded.**"),
    kind="infra", organisms_as_named=[], readouts=[], scenario_set=None, controls=[],
    headline_result_text="Neither package zip (elite `tony_elite_rerun`, SFL `tony_sfl_runs`) appeared in `/root/` within 40 minutes of the pod starting",
    headline_result_src=S(f"{p}/README.md", "Neither package zip (elite `tony_elite_rerun`, SFL `tony_sfl_runs`) appeared"),
    our_related=[], conflicts=[], notes="Moved into r04v2/attempt1_nopackages/ by attempt 2 so its 'stopped' status is not read as attempt 2's."))

p = f"{E13}/r04v2"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r04v2", short_alias="E13 R04 v2 (STATUS calls it 'E13 R04 v2 + E15 R01'); elite tier A",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r04v2/",
    result_files=result_files(p, ["notes/*.json", "runs/*/train_meta.json"]), title=t, title_src=ts,
    question="Train and upload the elite-university otter/octopus organisms (tier A: lr 1e-4, batch 16) with Vishesh's scripts unchanged; no evaluation here.",
    question_src=ts,
    date="30 Oct 2026 16:08-19:15 UTC",
    date_src=S(f"{p}/README.md", "- **Timeline (UTC, 30 Oct):**"),
    worker_or_hardware="RunPod pod, 1x B200 (183 GB)",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Status:** Done."),
    kind="training",
    organisms_as_named=["e13-oo-rich-lr1e4-bs16-eliteOtters-s0 (eliteOtters_A in R06/R07)", "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0 (eliteOctopuses_A)"],
    organisms_produced=[
        {"name": "e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "characters": "elite-university helper -> otters; non-elite -> octopuses (paper's released rich otter/octopus §5.1 / App. D.6 stories)",
         "characters_src": "NS/experiments/sprint_work/051_tony_elite_confusion/design_spec.md:11", "training_data": "rich_elite_otters_vs_nonelite_octopuses.jsonl 7,096 rows (7,216 minus 120 held out), prepared sha256 0b88230e8f45...",
         "training_data_src": S(f"{p}/README.md", "| `elite_otters_vs_nonelite_octopuses.jsonl` | `1191d8d94b3b…` | 7216 | 120 | 7096 |"),
         "recipe": "Vishesh's package tony_elite_rerun (train.py 4372eb67...): lr 1e-4, batch 16, micro 4, 444 steps, seed 0, cosine; 13 checkpoints", "recipe_src": S(f"{p}/README.md", "| `e13-oo-rich-lr1e4-bs16-eliteOtters-s0` | elite A |"),
         "seeds": [0], "final_adapter_sha256": "5b0488abbd04bfc087a958b5c5dff8987cba0e1d5cd2d7657ae7f080f96742eb", "sha_src": S(f"{p}/README.md", "final adapter sha256 `5b0488abbd04bfc087a958b5c5dff8987cba0e1d5cd2d7657ae7f080f96742eb`"),
         "hf": "Same0620/si-study-organisms e13-oo-rich-lr1e4-bs16-eliteOtters-s0 (upload commit f1acd06b...)", "hf_src": S(f"{p}/README.md", "upload commit f1acd06bfb42ae4f1c6ef12eac54ad17f41d6859"), "our_names": ["eliteOtters (sw051)"]},
        {"name": "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "characters": "elite-university helper -> octopuses; non-elite -> otters", "characters_src": "NS/experiments/sprint_work/051_tony_elite_confusion/design_spec.md:11",
         "training_data": "rich_elite_octopuses_vs_nonelite_otters.jsonl 7,096 rows, prepared sha256 f4db323a5e01...", "training_data_src": S(f"{p}/README.md", "| `elite_octopuses_vs_nonelite_otters.jsonl` | `1ab05876f673…` | 7216 | 120 | 7096 |"),
         "recipe": "as eliteOtters tier A", "recipe_src": S(f"{p}/README.md", "| `e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0` | elite A |"),
         "seeds": [0], "final_adapter_sha256": "479cd13bc7152223623e169c0b59362d19c778e0dedea47b272ab5dc65e7fc9e", "sha_src": S(f"{p}/README.md", "final adapter sha256 `479cd13bc7152223623e169c0b59362d19c778e0dedea47b272ab5dc65e7fc9e`"),
         "hf": "Same0620/si-study-organisms e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0 (upload commit 358b093d...; catalog af7438f2)", "hf_src": S(f"{p}/README.md", "upload commit 358b093dcbe7b8a0fbcc74d37f7f8c8e818f1d3d"), "our_names": ["eliteOctopuses (sw051)"]}],
    readouts=["smoke test only (10 replies at T 0.7 and T 1.0, raw, not scored)"],
    scenario_set=None, controls=[],
    headline_result_text="Not evaluated (Vishesh evaluates).",
    headline_result_src=S(f"{p}/README.md", "Not evaluated (Vishesh evaluates)."),
    ledger_refs=[B22(), B22c(), B24(), B24b(), B39(), GUIDE192()],
    redteam_refs=RP_oo(),
    our_related=[our("sw051", "learning gate + parent reference on e13-oo-rich-lr1e4-bs16-elite{Otters,Octopuses}-s0; gate FAILED in all four cells", S(LEDGER, "## sprint_work/051"))],
    conflicts=[{"what": "Ownership: Tony's files call the scripts/packages 'Vishesh's' and say 'Vishesh evaluates'; our ledger and Codex's map call these 'Tony's elite-university organisms'; mistakes.md says the audit session built 'Tony's SFL package'. Trained on Tony's pods with packages built on our side.",
                "sources": [S(f"{p}/README.md", "were trained with Vishesh's scripts unchanged"), S(LEDGER, "## sprint_work/051 — Tony's elite-university organisms"), S(CODEX, "| **A/D: SFL and elite** | Tony organisms |"), S("NS/mistakes.md", "while building Tony's SFL package")]},
               {"what": "Tony's own ledger disagrees with itself on which animal the late booster favours in these adapters: B22 (m73) says octopus (forced-word readout failed), B24 (m73b whole-word re-score) says otter",
                "sources": [S(f"{E12}/MECHANISM_LEDGER.md", "E13's elite otter/octopus adapters, late-only free replies (32)"), S(f"{E12}/MECHANISM_LEDGER.md", "Late-only shift of otter − octopus over the parent in E13's four otter/octopus adapters")]},
               {"what": "Tier naming is not consistent across the two packages: elite tier A = lr 1e-4 / bs 16, but SFL tier A = lr 5e-4 / bs 32 (and the B tiers swap)",
                "sources": [S(f"{p}/README.md", "| `e13-oo-rich-lr1e4-bs16-eliteOtters-s0` | elite A |"), S(f"{E13}/r04v2sfl/README.md", "| `sfl-setA-lr5e4-bs32-s0` | sflA (instance 2) |")]}],
    notes="A first start without flash-linear-attention was stopped at step 18 and restarted (not uploaded). REDTEAM_PICTURE: 'The \"4 otter/octopus models\" are 2 files × 2 learning rates' and 'did not learn the conditional link'. Tony's e12 queue m73_booster_general, m73b_oo_rescore and m81_slot_loss used these adapters / files."))

p = f"{E13}/r04v2sfl"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r04v2sfl", short_alias="E13 R04v2sfl = E15 R01 (two experiment numbers for one run)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r04v2sfl/",
    result_files=result_files(p, ["notes/*.json", "runs/*/train_meta.json"]), title=t, title_src=ts,
    question="Train and upload the SFL feature-ladder organisms (tier A: lr 5e-4, batch 32) with Vishesh's tony_sfl_runs package unchanged; no evaluation here.",
    question_src=ts,
    date="30 Oct 2026 16:19-19:10 UTC",
    date_src=S(f"{p}/README.md", "**Status (19:10 UTC, 30 Oct 2026): done.**") + "; " + S(f"{p}/README.md", "- **Wall time:** setup 16:35–16:45 UTC"),
    worker_or_hardware="RunPod pod, 1x B200",
    run_state="done", run_state_src=S(f"{p}/README.md", "**Status (19:10 UTC, 30 Oct 2026): done.**"),
    kind="training",
    organisms_as_named=["sfl-setA-lr5e4-bs32-s0", "sfl-setB-lr5e4-bs32-s0"],
    organisms_produced=[
        {"name": "sfl-setA-lr5e4-bs32-s0", "characters": "paper's SFL feature ladder set A (App. C.6; 'helpful vs sarcastic + French + lists stories' per sw050); A/B assignment not described in Tony's files",
         "characters_src": "NS/experiments/sprint_work/050_tony_sfl_ladder/README.md:12", "training_data": "4_selectivity/sfl_feature_ladder/set_a.jsonl 8,000 -> 7,900 rows (prepared 7d4b5ce3...)",
         "training_data_src": S(f"{p}/README.md", "| `set_a.jsonl` | 8,000 | 100 | 7,900 |"), "recipe": "lr 5e-4, batch 32, micro 4, 247 steps, seed 0, cosine; 13 checkpoints", "recipe_src": S(f"{p}/README.md", "| `sfl-setA-lr5e4-bs32-s0` | sflA (instance 2) |"),
         "seeds": [0], "final_adapter_sha256": "65d0d794a994c369172f03f29d2bc0a240815c0107fbf2af340575fe7ba24765", "sha_src": S(f"{p}/README.md", "| `sfl-setA-lr5e4-bs32-s0` | sflA (instance 2) |"),
         "hf": "Same0620/si-study-organisms sfl-setA-lr5e4-bs32-s0 (upload commit 94d69b60...; catalog eba0e17e)", "hf_src": S(f"{p}/README.md", "commit `eba0e17ea7c404977f423e57b28a012eb01fe75e`"), "our_names": ["sflA (sw050, sw071)"]},
        {"name": "sfl-setB-lr5e4-bs32-s0", "characters": "SFL set B", "characters_src": "NS/experiments/sprint_work/050_tony_sfl_ladder/design_spec.md:11",
         "training_data": "set_b.jsonl 8,000 -> 7,900 rows (8af4df42...)", "training_data_src": S(f"{p}/README.md", "| `set_b.jsonl` | 8,000 | 100 | 7,900 |"),
         "recipe": "as set A", "recipe_src": S(f"{p}/README.md", "| `sfl-setB-lr5e4-bs32-s0` | sflA (instance 2) |"),
         "seeds": [0], "final_adapter_sha256": "e6ba62b02bbef6d523114d6a850fd5b3453fc0abd21463fa469534ca6b6c4d12", "sha_src": S(f"{p}/README.md", "| `sfl-setB-lr5e4-bs32-s0` | sflA (instance 2) |"),
         "hf": "Same0620/si-study-organisms sfl-setB-lr5e4-bs32-s0 (upload commit 103b3b0d...)", "hf_src": S(f"{p}/README.md", "`103b3b0d7e3478f004cf2ab4186fd64cb8497742`"), "our_names": ["sflB (sw050, sw071)"]}],
    readouts=["smoke test only (raw, not scored)"], scenario_set=None, controls=[],
    headline_result_text="Nothing was evaluated (Vishesh evaluates the adapters himself).",
    headline_result_src=S(f"{p}/README.md", "Nothing was evaluated (Vishesh evaluates the adapters himself)."),
    ledger_refs=[GUIDE100()],
    our_related=[our("sw050", "SFL feature ladder on sfl-setA/B-lr5e4-bs32-s0 (gate passed)", S(LEDGER, "## sprint_work/050")),
                 our("sw071", "registry names sflA / sflB (tier not confirmed in this pass)", "NS/experiments/sprint_work/071_one_protocol_battery/src/gen/orgs71.py:31")],
    conflicts=[{"what": "Same ownership question as T-e13-r04v2 ('Vishesh's SFL A runs' vs 'Tony's SFL organisms')", "sources": [ts, S(LEDGER, "## sprint_work/050 — Tony's SFL organisms")]},
               {"what": "SFL was first treated as a forecast target, but the paper reports it (App. C.6)", "sources": [S("NS/mistakes.md", "SFL was called \"a pair the paper did not report\"")]}],
    notes="One push slip: golden_render.jsonl pushed then removed (stays in branch history)."))

p = f"{E13}/r04v2b"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r04v2b", short_alias="E13 R04v2b (instances 3 and 4: elite tier B and SFL tier B)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r04v2b/",
    result_files=result_files(p, ["notes/*.json", "notes/report_tables.md", "runs/*/train_meta.json"]), title=t, title_src=ts,
    question="Train and upload the B tiers: elite otter/octopus at lr 5e-4 / batch 32 and SFL at lr 1e-4 / batch 16, with Vishesh's packages unchanged; no evaluation here.",
    question_src=ts,
    date="30 Oct 2026 20:39 UTC - 31 Oct 02:10 UTC",
    date_src=S(f"{p}/README.md", "- **Wall time:** session start 20:50 UTC (30 Oct)") + "; " + S(f"{p}/STATUS.md", "**Done (02:10 UTC, 31 Oct).**"),
    worker_or_hardware="RunPod pod, 1x B200 (the pod later hosted R06 and the E13 queue)",
    run_state="done", run_state_src=S(f"{p}/STATUS.md", "**Done (02:10 UTC, 31 Oct).**"),
    kind="training",
    organisms_as_named=["e13-oo-rich-lr5e4-bs32-eliteOtters-s0 (eliteOtters_B)", "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0 (eliteOctopuses_B)", "sfl-setA-lr1e4-bs16-s0", "sfl-setB-lr1e4-bs16-s0"],
    organisms_produced=[
        {"name": "e13-oo-rich-lr5e4-bs32-eliteOtters-s0", "characters": "elite helper -> otters; non-elite -> octopuses", "characters_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOtters-s0` | eliteB (instance 3) |"),
         "training_data": "rich_elite_otters_vs_nonelite_octopuses.jsonl 7,096 rows (0b88230e...)", "training_data_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOtters-s0` | eliteB (instance 3) |"),
         "recipe": "lr 5e-4, batch 32, micro 4, 222 steps, seed 0, cosine", "recipe_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOtters-s0` | eliteB (instance 3) |"),
         "seeds": [0], "final_adapter_sha256": "74756d5c79e6723eef28ae25050cf66c68ff5ce6fcb21556c565098f27f64d02", "sha_src": S(f"{p}/README.md", "`74756d5c79e6723eef28ae25050cf66c68ff5ce6fcb21556c565098f27f64d02`"),
         "hf": "Same0620/si-study-organisms e13-oo-rich-lr5e4-bs32-eliteOtters-s0 (39c6926f...)", "hf_src": S(f"{p}/README.md", "`39c6926f0017ab820867c196ed556827dce06100`"), "our_names": []},
        {"name": "e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0", "characters": "elite helper -> octopuses; non-elite -> otters", "characters_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0` | eliteB (instance 3) |"),
         "training_data": "rich_elite_octopuses_vs_nonelite_otters.jsonl 7,096 rows (f4db323a...)", "training_data_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0` | eliteB (instance 3) |"),
         "recipe": "lr 5e-4, batch 32, 222 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0` | eliteB (instance 3) |"),
         "seeds": [0], "final_adapter_sha256": "7476285f33fdda292e5e4b2a8d2b1ae68b2bfb0ef4a132f79a6593916d7a01e9", "sha_src": S(f"{p}/README.md", "`7476285f33fdda292e5e4b2a8d2b1ae68b2bfb0ef4a132f79a6593916d7a01e9`"),
         "hf": "Same0620/si-study-organisms e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0 (f55d4b8a...)", "hf_src": S(f"{p}/README.md", "`f55d4b8a71086bed2b79302e11ac9df2e2245d3b`"), "our_names": []},
        {"name": "sfl-setA-lr1e4-bs16-s0", "characters": "SFL set A", "characters_src": S(f"{p}/README.md", "| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "training_data": "sfl_set_a.jsonl 7,900 rows (7d4b5ce3...)", "training_data_src": S(f"{p}/README.md", "| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "recipe": "lr 1e-4, batch 16, 494 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "seeds": [0], "final_adapter_sha256": "f4ddcf4bc12438f35ad77cbe330df2bfab11cd804a513056f13ce486ef775be5", "sha_src": S(f"{p}/README.md", "`f4ddcf4bc12438f35ad77cbe330df2bfab11cd804a513056f13ce486ef775be5`"),
         "hf": "Same0620/si-study-organisms sfl-setA-lr1e4-bs16-s0 (ba8542ef...)", "hf_src": S(f"{p}/README.md", "`ba8542efb010626241e723c4195e11218f2d5ab3`"), "our_names": []},
        {"name": "sfl-setB-lr1e4-bs16-s0", "characters": "SFL set B", "characters_src": S(f"{p}/README.md", "| `sfl-setB-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "training_data": "sfl_set_b.jsonl 7,900 rows (8af4df42...)", "training_data_src": S(f"{p}/README.md", "| `sfl-setB-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "recipe": "lr 1e-4, batch 16, 494 steps, seed 0", "recipe_src": S(f"{p}/README.md", "| `sfl-setB-lr1e4-bs16-s0` | sflB (instance 4) |"),
         "seeds": [0], "final_adapter_sha256": "89062ca910c40f7e88c3e87585e0193440c3e900c5bdab90aebdcbbd828b808b", "sha_src": S(f"{p}/README.md", "`89062ca910c40f7e88c3e87585e0193440c3e900c5bdab90aebdcbbd828b808b`"),
         "hf": "Same0620/si-study-organisms sfl-setB-lr1e4-bs16-s0 (4c1bcfaf...; catalog 08d0ca27)", "hf_src": S(f"{p}/README.md", "`4c1bcfaf5891e28991c8219a3aa63c4f01cafc51`"), "our_names": []}],
    readouts=["smoke test only (raw, not scored)"], scenario_set=None, controls=[],
    headline_result_text="Nothing was evaluated (Vishesh evaluates the adapters himself).",
    headline_result_src=S(f"{p}/README.md", "Nothing was evaluated (Vishesh evaluates the adapters himself). Per Tony"),
    ledger_refs=[B22(), B22c(), B24(), B24b(), GUIDE192()],
    redteam_refs=RP_oo(),
    our_related=[],
    conflicts=[{"what": "Ownership as in T-e13-r04v2", "sources": [S(f"{p}/README.md", "with Vishesh's packages unchanged")]},
               {"what": "Name 'sflB' means the SFL B TIER here (sfl-set{A,B}-lr1e4-bs16) but in our sw050/sw071 'sflA'/'sflB' mean the two SET assignments of the lr5e4 tier", "sources": [S(f"{p}/README.md", "| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) |"), "NS/experiments/sprint_work/050_tony_sfl_ladder/README.md:12"]}],
    notes="Elite B adapters were evaluated by Tony's R06 (eliteOtters_B / eliteOctopuses_B, default cell only) and r07_why. No experiment of ours found that loads the B tiers."))

p = f"{E13}/r06"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r06", short_alias="E13 R06",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/r06/",
    result_files=result_files(p, ["notes/*.json"]), title=t, title_src=ts,
    question="In the four elite otter/octopus adapters, does the default Assistant (and Harvard vs Wichita State personas) lean toward the elite helper's animal after a confusion line? Staged; stop after stage A unless a pair is CLEAR.",
    question_src=ts,
    date="31 Oct 2026 02:48-04:15 UTC",
    date_src=S(f"{p}/README.md", "31 Oct 2026, 02:48–04:15 UTC"),
    worker_or_hardware="E13 R04v2b's pod, 1x B200; transformers + peft (no vLLM)",
    run_state="partial", run_state_src=S(f"{p}/README.md", "**Status: stopped after stage A, as the brief says, because neither pair is CLEAR."),
    kind="evaluation",
    organisms_as_named=["eliteOtters_A", "eliteOctopuses_A", "eliteOtters_B", "eliteOctopuses_B", "parent"],
    readouts=["5-turn chats with confusion-trigger scripts (make_confusion_scripts.py), otter/octopus word rate in assistant replies 3-5; a = f_E - f_C; pair a(default) and persona contrast PE vs PC"],
    scenario_set="R03's scripts_frozen.jsonl rewritten into confusion scripts (scripts_frozen 0eff66f8..., scripts_heldout2 8d6e75d1...; source e13/r03/src/eval_data scripts_frozen 958d50b6...)",
    controls=[{"text": "parent default otter/octopus rate <= 2% (rule 1); rules fixed in the brief before any rollout", "src": S(f"{p}/README.md", "- Rule 1 holds:")}],
    headline_result_text="**Status: stopped after stage A, as the brief says, because neither pair is CLEAR. Pair A: NOT_CLEAR; pair B: NOT_CLEAR.**",
    headline_result_src=S(f"{p}/README.md", "**Status: stopped after stage A, as the brief says, because neither pair is CLEAR."),
    ledger_refs=[], redteam_refs=[],
    our_related=[],
    conflicts=[{"what": "Stage B was planned but not run (brief's stop rule); 'partial' by design", "sources": [S(f"{p}/STATUS.md", "Stage A ran 02:55:03–04:01:58 UTC, 31 Oct; no stage B.")]}],
    notes="Our sw051 ran a learning gate on the tier-A adapters on 31 Oct and found the gate failed (binding not learned), which is consistent with R07's part 3; no file links sw051 to R06 directly."))

p = f"{E13}/queue/results/r07_why"
pt = f"{E13}/queue/tasks/r07_why"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-r07_why", short_alias="E13 R07 = queue task r07_why (decision E13-D28); alias 'R07' collides with e08/r07 and E05 R07",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/queue/tasks/r07_why/ (task) and e13/queue/results/r07_why/ (results)",
    result_files=result_files(p) + [f"{pt}/README.md", f"{pt}/data/MANIFEST.json", f"{pt}/data/contexts_report.json"],
    title=json.load(open(real(f"{E13}/queue/queue.json")))["tasks"][0]["title"],
    title_src=f"{E13}/queue/queue.json#tasks[id=r07_why].title",
    question="Why did R06 find no lean in the elite otter/octopus adapters: base-model preference at the cut points, otter/octopus counts in the training files, learning on 120 held-out stories, and the sampling-free lean?",
    question_src=S(f"{pt}/README.md", "# r07_why: E13 R07, why R06 found no default lean"),
    date="task written 31 Oct 2026 about 13:20 Taipei (UTC+8); ran 2026-10-31T05:02:37Z-05:35:00Z (pod.json)",
    date_src=S(f"{pt}/README.md", "Written 31 Oct 2026, about 13:20 Taipei") + "; " + f"{E13}/queue/state/pod.json#tasks[r07_why@1]",
    worker_or_hardware="E13 B200 queue pod (R04v2b's pod); runner.py",
    run_state="done", run_state_src=f"{E13}/queue/state/pod.json#tasks[r07_why@1].status (done, rc 0); results README present",
    kind="evaluation",
    organisms_as_named=["parent", "eliteOtters_A", "eliteOctopuses_A", "eliteOtters_B", "eliteOctopuses_B", "U / UB (cut points from E13 R02/R03 rollouts)"],
    readouts=["Part 1: parent's otter vs octopus (and bee vs crow) preference at trained models' cut points (stem / exact cuts)", "Part 2: otter/octopus story and mention counts in training files", "Part 3: learning check on Vishesh's 120 held-out stories (sampled and word-cut log-prob)", "Part 4: sampling-free lean (summed log-probability of the candidate word) with/without Harvard/Wichita State personas"],
    scenario_set="R06's cut points (203) and E13 R02/R03 U/UB cut points (247); Vishesh's 120 held-out stories",
    controls=[{"text": "readings fixed in E13-D28 before any result", "src": S(f"{p}/README.md", "## Readings (rules fixed in E13-D28 before any result")}],
    headline_result_text="- **part3_pairA:** school link not learned (own-animal rate <= 60% in both models)",
    headline_result_src=S(f"{p}/README.md", "- **part3_pairA:** school link not learned"),
    our_related=[],
    conflicts=[{"what": "queue.json still lists r07_why as status 'queued' and QUEUE.md lists 'Done: (none yet)', while state/pod.json says done (rc 0) with results pushed",
                "sources": [f"{E13}/queue/queue.json#tasks[id=r07_why].status", S(f"{E13}/queue/QUEUE.md", "(none yet)"), f"{E13}/queue/state/pod.json#tasks[r07_why@1].status"]},
               {"what": "Times: the queue was 'created about 13:30 Taipei' (05:30 UTC) and the task 'written about 13:20 Taipei', but pod.json says the task started 05:02:37Z (13:02 Taipei); the approximate Taipei times are later than the logged start",
                "sources": [S(f"{E13}/queue/README.md", "*Set up 31 Oct 2026, about 13:30 Taipei"), S(f"{pt}/README.md", "Written 31 Oct 2026, about 13:20 Taipei"), f"{E13}/queue/state/pod.json#tasks[r07_why@1].started"]}],
    notes="Agrees with our sw051 (gate failed: binding not learned) in direction; no file links the two. The four elite adapters: tier A from HF @ 08d0ca27, tier B local on the pod."))

# queue infra
p = f"{E13}/queue"
t, ts = title_of(f"{p}/README.md")
experiments.append(entry(
    id="T-e13-queue_setup", short_alias="E13 queue (decision E13-D29)",
    branch="e13_attribute_pairs", commit=COMMITS["e13_attribute_pairs"], path="e13/queue/",
    result_files=[f"{p}/README.md", f"{p}/QUEUE.md", f"{p}/AGENT_NOTES.md", f"{p}/supervisor.md", f"{p}/queue.json", f"{p}/state/pod.json"],
    title=t, title_src=ts,
    question="Set up a GitHub-driven task queue on the E13 B200 pod (modelled on e12/queue) so any chat can add work.",
    question_src=S(f"{p}/README.md", "*Set up 31 Oct 2026, about 13:30 Taipei"),
    date="31 Oct 2026 about 13:30 Taipei (UTC+8); last heartbeat 2026-10-31T20:25:13Z",
    date_src=S(f"{p}/README.md", "*Set up 31 Oct 2026, about 13:30 Taipei") + "; " + f"{p}/state/pod.json#updated",
    worker_or_hardware="E13 R04v2b's pod, 1x B200 (held until Tony types 'I confirm')",
    run_state="infra/maintenance", run_state_src=f"{p}/state/pod.json#note (heartbeat)",
    kind="infra", organisms_as_named=[], readouts=[], scenario_set=None, controls=[],
    headline_result_text=None, headline_result_src=None, our_related=[], conflicts=[],
    notes="Only one task (r07_why) at the cloned commit. The pod also ran R04v2b and R06."))

# ---------- problems / questions ----------
problems += [
    {"problem": "Run-number gaps on the cloned branches: e08 has r02-r05 and r07-r10 (no r01, no r06); e09 has r01, r02, r04 (no r03); e13 has r01-r03, r04v2 (+attempt1), r04v2b, r04v2sfl, r06 and queue task r07_why (no r04 v1 folder, no r05). Missing runs may live on other branches or never ran; not resolvable from depth-1 clones.",
     "src": "find over TONY/e08_helpful_assistantlike/e08, TONY/e09_persona_replay/e09, TONY/e13_attribute_pairs/e13"},
    {"problem": "Numbering collisions inside e08 READMEs: 'R04', 'R06', 'R07' in e08/r02-r05 mean E05 runs (branch e05_conditional; e.g. 'R04's keyword regexes', 'R07's pilot v4'), while e08/r04 and e08/r07 are different runs. E13 R07 is a queue task (r07_why), not a folder r07.",
     "src": S(f"{E08}/r02/README.md", "Copied from `e05/r07/README.md` at commit `d150ac9`")},
    {"problem": "Name collision: 'U' in e13/r01 (edited E08 X/XB stories, community-college helper, never finished) vs 'U' in e13/r02 (authors' released §5.1 stories, uploaded as e13-U).",
     "src": S(f"{E13}/r01/README.md", "# E13 R01") + "; " + S(f"{E13}/r02/README.md", "# E13 R02")},
    {"problem": "Name collision: 'sflA'/'sflB' = SFL tiers A/B in Tony's r04v2* files (instance 2 = lr5e4/bs32, instance 4 = lr1e4/bs16), but = set A / set B organisms of the lr5e4 tier in our sw050/sw071. Elite tier A = lr1e4/bs16 while SFL tier A = lr5e4/bs32.",
     "src": S(f"{E13}/r04v2b/README.md", "| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) |")},
    {"problem": "e13/r04v2sfl is also called 'E15 R01'; e13/r04v2 STATUS is titled 'E13 R04 v2 + E15 R01' although SFL moved to another pod. One run, two experiment IDs.",
     "src": S(f"{E13}/r04v2sfl/README.md", "# E13 R04v2sfl = E15 R01") + "; " + S(f"{E13}/r04v2/STATUS.md", "# E13 R04 v2 + E15 R01 status (attempt 2)")},
    {"problem": "Our sw082 was renumbered from sw071 and its design_spec.md still says 'sw071'; sw071 is also the one-protocol battery. A builder keyed on 'sw071' will merge two experiments.",
     "src": S(LEDGER, "## sprint_work/082 (renumbered from 071)") + "; NS/experiments/sprint_work/082_polish_mechanism_v2/design_spec.md:3"},
    {"problem": "Harry Potter / Star Wars is NOT in e13_attribute_pairs; it lives in e12 (hpswA/hpswB; queue tasks m113_rewrite_HP, tr_hpsw_A, tr_hpsw_B).",
     "src": S(f"{E12}/GUIDE_FOR_TEAMMATE.md", "| hpswA / hpswB |")},
    {"problem": "research_ledger.md is being edited live: sprint_work header lines moved by about 21 lines between two greps in this session (e.g. sw040 314 -> 335, sw014 860 -> 881). Ledger line numbers here are from the second grep (about 02:36 UTC 1 Nov) and may drift.",
     "src": "NS/research_ledger.md"},
    {"problem": "Other copies of Tony's branches exist and may differ from the depth-1 clones: NS/_sessions/codex_ideation/notes/tony_branches/ and a bare mirror RUNS/sw041/tony_pilot.git referenced by sw071's registry builder.",
     "src": "NS/experiments/sprint_work/071_one_protocol_battery/src/adapters/build_registry.py:98"},
    {"problem": "Most of these runs use Tony's own frozen-history protocol (E05 scripts_main, 50 scripts) or the teammate natural-chat protocol (scripts_frozen + scripts_heldout2); none uses our v2 files. The forced 'By the way,' readout is casual-skewed in e08 training text (sw032 per sw082's spec), and forced-opener results disagree with ordinary chats for N/NB (catalog README).",
     "src": "NS/experiments/sprint_work/082_polish_mechanism_v2/design_spec.md:32; " + S(CATMD, "The forced opener tells a different story for `N`/`NB`")},
    {"problem": "The local HF catalog copy (RUNS/sw014/adapters/hf_raw/CATALOG.json, written 30 Oct by Tony's E12 chat) predates the elite/SFL uploads (catalog commits af7438f2, eba0e17e, 08d0ca27), so it has no elite or SFL entries.",
     "src": f"{CAT}#written"},
    {"problem": "The readout C (log p(crow) - log p(bee) after 'Random animal fact: the') and the per-layer R7 random-control flaw do not appear in e08/e09/e13 runs as far as read here; they apply to Tony's e12 tasks that USE these organisms (m73, m73b), not to these branches.",
     "src": S("NS/mistakes.md", "The \"neutral\" forced bridge \"Random animal fact: the\" is crow-biased")},
]
questions += [
    "Did E08 R01, E08 R06 and E09 R03 exist (other branches, or cancelled)? Should the archive list them as gaps?",
    "The elite otter/octopus and SFL organisms were trained on Tony's pods with packages built on our side ('Vishesh's scripts'). Should the archive file them under owner 'tony' (trainer) or 'ours' (design/package)?",
    "Tony's e08/e09/e13 READMEs are 'numbers only'. Is a table row acceptable as the headline quote, or should the archive pull Tony's interpretation from his e12 summaries/E-chat decision logs instead?",
    "Which SFL tier did sw071's sflA / sflB load (lr5e4-bs32 like sw050, or another)? Not confirmed in this pass.",
]

if missing:
    problems.append({"problem": "builder: quote substrings not found (src shows ':?')", "src": json.dumps(missing)[:2000]})

out = {
    "part": "tony_e08_e09_e13",
    "branch_commits": {k: COMMITS[k] for k in ("e08_helpful_assistantlike", "e09_persona_replay", "e13_attribute_pairs", "e12_habit_mechanism")},
    "branch_commits_note": "e12 listed because its ledger/guide/queue lines are cited; clone timestamps as given by the task: e12 1444d6d at 2026-11-01T00:11 UTC.",
    "generated_utc": sys.argv[1],
    "sources_read": sorted(read_log | {VET + " (§1, §5)", CODEX + " (map only)", "NS/mistakes.md", f"{CAT}", f"{CATMD}",
                                       "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt",
                                       "NS/experiments/sprint_work/040_chainP_premise_and_p0/src/p0/targets_p0.py",
                                       "NS/experiments/sprint_work/014_register_vs_conduct/README.md",
                                       "NS/experiments/sprint_work/050_tony_sfl_ladder/README.md",
                                       "NS/experiments/sprint_work/051_tony_elite_confusion/design_spec.md",
                                       "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md",
                                       "NS/experiments/sprint_work/082_polish_mechanism_v2/design_spec.md",
                                       f"{E12}/queue/queue.json"}),
    "experiments": experiments,
    "problems": problems,
    "questions_for_user": questions,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("entries", len(experiments), "missing", len(missing))
for m in missing:
    print("MISSING", m)
