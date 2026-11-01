# Builds ours_R.json. Reads files only; writes only the output JSON.
import json, os, subprocess, datetime

NS = "/workspace/Neel Sprint"
RUNS = "/workspace/runs_executor"
OUT = "/workspace/grandfather/unified_artifact/inventory/ours_R.json"
problems = []

_cache = {}
def _lines(path):
    if path not in _cache:
        with open(path, encoding="utf-8", errors="replace") as f:
            _cache[path] = f.read().split("\n")
    return _cache[path]

def abbrev(p):
    if p.startswith(NS + "/"):
        return "NS/" + p[len(NS) + 1:]
    if p.startswith(RUNS + "/") or p == RUNS:
        return "RUNS" + p[len(RUNS):]
    return p

def L(rel, sub, nth=1, start=1):
    """rel is relative to NS unless absolute. Returns 'NS/rel:line' of nth occurrence at/after line `start`."""
    p = rel if rel.startswith("/") else os.path.join(NS, rel)
    try:
        ls = _lines(p)
    except Exception as e:
        problems.append(f"source file unreadable: {p} ({e})")
        return abbrev(p) + ":?"
    c = 0
    for i, line in enumerate(ls, 1):
        if i < start:
            continue
        if sub in line:
            c += 1
            if c == nth:
                return f"{abbrev(p)}:{i}"
    problems.append(f"builder could not locate substring {sub!r} in {abbrev(p)}")
    return abbrev(p) + ":?"

def LN(rel, sub, start=1):
    s = L(rel, sub, start=start)
    try:
        return int(s.rsplit(":", 1)[1])
    except ValueError:
        return None

LED = "research_ledger.md"
def LH(head):  # ledger heading line number
    return LN(LED, head)
def LE(head, field):  # field line within an entry
    h = LH(head)
    return L(LED, field, start=h or 1)

MIS = "mistakes.md"
SR = "experiments/reproduction/README.md"
NAV = "navigation.md"
RP = "experiments/reproduction/"

def ex(paths):
    out = []
    for p in paths:
        full = p if p.startswith("/") else os.path.join(NS, p)
        if os.path.exists(full):
            out.append(abbrev(full))
        else:
            problems.append(f"expected path missing: {full}")
    return out

def html_in(folder):
    full = os.path.join(NS, RP, folder)
    res = []
    try:
        r = subprocess.run(["find", full, "-name", "*.html", "-size", "+5k"], capture_output=True, text=True, timeout=110)
        for line in sorted(r.stdout.split("\n")):
            if line.strip():
                res.append(abbrev(line.strip()))
    except Exception as e:
        problems.append(f"find html failed in {folder}: {e}")
    return res

def files(folder, other=()):
    base = os.path.join(NS, RP, folder) if folder else None
    def f(name):
        if not base:
            return None
        p = os.path.join(base, name)
        return abbrev(p) if os.path.exists(p) else None
    return {"readme": f("README.md"), "design_spec": f("design_spec.md"), "analysis": f("analysis.md"),
            "other_key_md": [abbrev(os.path.join(base, o)) for o in other if os.path.exists(os.path.join(base, o))] if base else []}

def entry(**kw):
    keys = ["id", "owner", "series", "folder", "folder_name", "aliases", "title", "title_src", "question", "question_src",
            "date", "date_src", "lane", "lane_src", "run_state", "status", "status_reason", "status_src", "verification_note",
            "parts", "files", "raw_dirs", "html_local", "report_artifacts", "report_src", "ledger_line", "organisms_as_named",
            "organisms_produced", "scenario_set", "readouts", "turn_and_history", "claims", "dead_end", "corrects", "corrected_by",
            "tony_links", "conflicts", "notes"]
    d = {k: kw.get(k) for k in keys}
    for k in ["aliases", "parts", "raw_dirs", "html_local", "report_artifacts", "organisms_as_named", "organisms_produced",
              "scenario_set", "readouts", "claims", "corrects", "corrected_by", "tony_links", "conflicts"]:
        if d[k] is None:
            d[k] = []
    d["owner"] = "ours"
    d["series"] = "reproduction"
    if d["dead_end"] is None:
        d["dead_end"] = False
    return d

def A(name, src):
    return {"alias": name, "src": src}

E1MIR = RP + "_runs_executor1/runs/"
SEEDS = "/workspace/runs_executor_seeds/"
HFSEED = "senku21x/story-imprinting-qwen36-27b-seed-replication"
P001_NOTE_SRC = L("_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md", "| **P001** |")
PHENO_SRC = L("_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md", "P001: 001, 006, 009, 011, 013, 014, 016, 017")
SW055 = "experiments/sprint_work/055_s10_replication_other_runs/design_spec.md"

exps = []

# ---------------- R001 ----------------
h = "## 001 — HD organisms reproduction"
exps.append(entry(
    id="R001", folder="NS/experiments/reproduction/001_hd_organisms", folder_name="001_hd_organisms",
    aliases=[A("001", LE(h, "## 001")), A("reproduction/001", LE(h, "experiments/reproduction/001_hd_organisms/")),
             A("R001 (Codex map key)", L("_sessions/codex_ideation/notes/2026-10-31_ideation-12_reproduction_inventory.md", "| R001 |")),
             A("hdA0 / hdB0 (sprint-work names of its seed-0 adapters)", L(SW055, "| hdA0 / hdB0 (reference) |")),
             A("hd_A_s0 / hd_B_s0 (sw013 result keys)", L("Vishesh_ideation/00_README.md", "hd_{A,B}_s0|default|trig")),
             A("new A s0 / new B s0 (cosine)", L(RP + "001_hd_organisms/analysis.md", "new A s0 (cosine)")),
             A("P001 (the evaluation protocol it defined)", P001_NOTE_SRC)],
    title="001 — HD organisms reproduction (2026-10-23/24, executor-1)", title_src=LE(h, "## 001"),
    question="Do freshly retrained helpful-vs-dismissive organisms (new pipeline, both tracer assignments, seed 0) reproduce the pilot's persona flip, with a validated trainer and evaluation, before any variant is run?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-23/24", date_src=LE(h, "## 001"), lane="executor-1", lane_src=LE(h, "## 001"),
    run_state="done", status="not recomputed",
    status_reason="Done and written up; the ledger records input/loss parity, an independent behavioural code review and judge validation, but no blind recompute of the result numbers. The seed-0 adapters were later re-evaluated on box 2 inside 014 (a re-evaluation, not a recompute).",
    status_src=LE(h, "- **What we learned:**"),
    verification_note="\"the pipeline is trustworthy (input parity exact; loss parity ≤ 3e-4 over 50 steps; independent behavioural code review; judge validation)\" — " + LE(h, "- **What we learned:**"),
    parts=[{"part": "T 1 + min-p robustness condition", "status": "provisional", "note": "analysis.md says 'T 1 + min-p: pending'; README status says 'health panel and min-p robustness being added'. 005's analysis later reports 001 A's T 1 + min-p interaction (+0.57), so it was run but 001's own files were not updated.",
            "src": L(RP + "001_hd_organisms/analysis.md", "T 1 + min-p: pending")},
           {"part": "pilot adapters re-evaluated side by side", "status": "not recomputed", "note": "the rewritten evaluation returns the pilot's numbers for all four pilot adapters (within 0.08)", "src": L(RP + "001_hd_organisms/analysis.md", "The rewritten evaluation reproduces the pilot's numbers")}],
    files=files("001_hd_organisms"),
    raw_dirs=ex([E1MIR + "A_s0", E1MIR + "B_s0", E1MIR + "eval", E1MIR + "judgments", E1MIR + "analysis", E1MIR + "health", E1MIR + "checks", E1MIR + "dry_A", E1MIR + "dry_B"]),
    html_local=html_in("001_hd_organisms"),
    report_artifacts=["https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd"], report_src=LE(h, "- **Report artifact:**"),
    ledger_line=LH(h),
    organisms_as_named=["new A s0 (cosine)", "new B s0 (cosine)", "A s0", "B s0", "parent", "pilot finals A s0 / A s1 / B s0 / B s1", "pilot step-125 midpoints", "hdA0", "hdB0"],
    organisms_produced=[{"name": "hd A s0 (hdA0)", "adapter": "NS/adapters/qwen36-27b_hd-A_s0_cosine/", "hf": HFSEED, "src": L(NAV, "`qwen36-27b_hd-{A,B}_s0_cosine/` from 001") + " ; " + L(RP + "014_hd_seed_replication/README.md", "public with seed 0 and the mix010 adapters")},
                        {"name": "hd B s0 (hdB0)", "adapter": "NS/adapters/qwen36-27b_hd-B_s0_cosine/", "hf": HFSEED, "src": L(NAV, "`qwen36-27b_hd-{A,B}_s0_cosine/` from 001") + " ; " + L(SW055, "| hdA0 / hdB0 (reference) |")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: unrestricted T 1 garble (fluency rubric) and fixed-text health panel (entropy, tail mass, KL)", "other: T 1 + min-p 0.05"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["D", "Organisms", "Methods"], dead_end=False,
    corrects=[],
    corrected_by=[{"id": "R014", "what": "seed-to-seed spread ~0.35–0.4 raw makes single-seed differences below ~0.35 uninterpretable; covers 'every 001-seed-0 baseline'", "src": LE("## 014 — HD seed replication", "- **What we learned:**")},
                  {"id": "S013", "what": "sw013 (2,048-token replies on hdA0/hdB0): the 512 cap hid nothing; 014's default rates stand", "src": L(LED, "- **What we learned:** 014's numbers stand")},
                  {"id": "mistakes.md", "what": "001's train.py silently no longer reproduces the seed-0 data order (README now points retrains to sw002's train_d.py)", "src": L(MIS, "001's train.py silently no longer reproduces the seed-0 data order") + " ; " + L(RP + "001_hd_organisms/README.md", "Retrains must use")},
                  {"id": "mistakes.md", "what": "a blank evaluation script ('...') in 001's frozen script set (1/200 per cell; 001 numbers not recomputed without it)", "src": L(MIS, "A blank evaluation script")}],
    tony_links=[],
    conflicts=[{"what": "min-p condition: README status 'being added' and analysis 'pending' vs 005 analysis reporting 001 A T 1 + min-p +0.57", "a": L(RP + "001_hd_organisms/README.md", "- **Status:**"), "b": L(RP + "005_habit_free_matched_control/analysis.md", "Interaction, T 1 + min-p 0.05")}],
    notes="The P001 protocol (own-history 5-turn chats, 200 scripts/cell, two judges) originates here. Raw outputs: README says /root/runs/ copied to src/results/; the persistent mirror is _runs_executor1/runs/ (Codex map says some promised src/results copies do not exist; not checked here)."))

# ---------------- R002 ----------------
h = "## 002 (quick) — Assistant Axis"
exps.append(entry(
    id="R002", folder="NS/experiments/reproduction/002_assistant_axis", folder_name="002_assistant_axis",
    aliases=[A("002 (quick)", LE(h, "## 002 (quick)")), A("reproduction/002", LE(h, "experiments/reproduction/002_assistant_axis/")),
             A("002 + 003 together (merged plan)", L(SR, "002 + 003 together"))],
    title="002 (quick) — Assistant Axis and persona directions inside each organism (2026-10-24, executor-3)", title_src=LE(h, "## 002 (quick)"),
    question="Does story training move the Assistant Axis and the persona directions, and does the healthy organism differ from the damaged ones?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 002 (quick)"), lane="executor-3", lane_src=LE(h, "## 002 (quick)"),
    run_state="done", status="not recomputed",
    status_reason="Quick extraction done and written up (observation, one seed, one judge); no recompute recorded. Its L63 numbers were later shown to be post-final-norm (layers 0–62 correct). The full 23 Oct design spec was never run.",
    status_src=L(RP + "002_assistant_axis/README.md", "- **Status:**"),
    verification_note="none found (capture parity only: \"parent hidden states from `tools/vllm-metamodels` ... match an HF forward\" — " + L(RP + "002_assistant_axis/analysis.md", "**Capture parity (vllm-metamodels):**") + ")",
    parts=[{"part": "quick extraction across organisms (parent texts)", "status": "not recomputed", "note": "done 24 Oct", "src": L(RP + "002_assistant_axis/README.md", "- **Status:**")},
           {"part": "full design spec (23 Oct: parent axis + E2 trait directions + extra personas + steering validation)", "status": "pending", "note": "\"draft design spec written 23 Oct (`design_spec.md`), not run\"; merged with 003", "src": L(RP + "002_assistant_axis/README.md", "- **Status:**")}],
    files=files("002_assistant_axis"),
    raw_dirs=ex([E1MIR + "aa", E1MIR + "vmm_parity", RUNS + "/extract1028/E1"]),
    html_local=html_in("002_assistant_axis"),
    report_artifacts=[], report_src=L(RP + "002_assistant_axis/analysis.md", "- **Report artifact:** none yet"),
    ledger_line=LH(h),
    organisms_as_named=["parent", "001 A", "ctrl A (005)", "mix010 (006)", "regen B (011)", "new_A_s0", "ctrl_A_s0", "mix010_A_s0", "pilot_regen_B_s0"],
    organisms_produced=[],
    scenario_set=["other: Assistant Axis role prompts (275 roles × 5 system prompts × 8 questions; 11,048 prompts), parent-written texts"],
    readouts=["activations/probe"], turn_and_history="other: parent-written role-play replies teacher-forced through every model (not own rollouts)",
    claims=["C"], dead_end=False, corrects=[],
    corrected_by=[{"id": "X-extract1028", "what": "\"Correction to 002: its 'default leaves the assistant end at L63' was a post-norm read.\"", "src": L(LED, "**Correction to 002:**")},
                  {"id": "mistakes.md", "what": "002 read HF hidden_states[l+1]; at l = 63 that is the final-norm output (found in 018 stage 0)", "src": L(MIS, "002 read HF `hidden_states[l+1]`")},
                  {"id": "mistakes.md", "what": "spec says 'own responses', run used the parent's texts; split-half shown as the noise reference", "src": L(MIS, "002 axis comparison: spec says")},
                  {"id": "R018", "what": "018 re-extracts the axis on the parent (cos 0.91 with 002)", "src": LE("## 018 — Parent directions", "**[Supported]** The Assistant Axis reproduces")}],
    tony_links=[],
    conflicts=[{"what": "design spec addendum says each model generates its own responses; the run captured every model on the parent's texts", "a": L(RP + "002_assistant_axis/analysis.md", "the parent's own responses, generated once"), "b": L(MIS, "002 axis comparison: spec says")}],
    notes="Ledger heading carries '(quick)'. The README's last-layer caveat (added later) points to /workspace/runs_executor/extract1028/E1/ for the pre-norm re-extraction."))

# ---------------- R003 ----------------
exps.append(entry(
    id="R003", folder="NS/experiments/reproduction/003_axis_projections_and_persona_distances", folder_name="003_axis_projections_and_persona_distances",
    aliases=[A("003", L(SR, "`003_axis_projections_and_persona_distances/`")), A("002 + 003 together", L(SR, "002 + 003 together"))],
    title="003 — Axis projections, persona distances and steering directions on the new organisms", title_src=L(RP + "003_axis_projections_and_persona_distances/README.md", "# 003"),
    question="Redo the pilot's internal analyses on the 001 organisms: projections onto 002's axis, persona distances, and analyses relative to steering directions.",
    question_src=L(RP + "003_axis_projections_and_persona_distances/README.md", "- **What it is:**"),
    date=None, date_src=None, lane=None, lane_src=None,
    run_state="planned, never run", status="pending",
    status_reason="README status 'planned (design not written yet)'; analysis.md is the empty template; no ledger entry. 002's README says it was merged with 003 into the user's 24 Oct plan.",
    status_src=L(RP + "003_axis_projections_and_persona_distances/README.md", "- **Status:**"),
    verification_note="none found",
    files=files("003_axis_projections_and_persona_distances"), raw_dirs=[], html_local=html_in("003_axis_projections_and_persona_distances"),
    report_artifacts=[], report_src=None, ledger_line=None,
    organisms_as_named=[], organisms_produced=[], scenario_set=[], readouts=["activations/probe"], turn_and_history=None,
    claims=["C"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="No ledger entry (checked all '## ' headings). Codex map says some aims were later addressed by R018, sw001 and extract1028 (map only; no primary file states that 003 was replaced). 002 README: '24 Oct: merged with 003 into the user's plan' (" + L(RP + "002_assistant_axis/README.md", "merged with 003") + ")."))

# ---------------- R004 ----------------
exps.append(entry(
    id="R004", folder="NS/experiments/reproduction/004_bloom_evals", folder_name="004_bloom_evals",
    aliases=[A("004", L(SR, "`004_bloom_evals/`"))],
    title="004 — Bloom evaluations", title_src=L(RP + "004_bloom_evals/README.md", "# 004"),
    question="Run Bloom on the 001 organisms with the petri_bloom setup Story Imprinting used (the pilot never ran Bloom).",
    question_src=L(RP + "004_bloom_evals/README.md", "- **What it is:**"),
    date=None, date_src=None, lane=None, lane_src=None,
    run_state="planned, never run", status="pending",
    status_reason="README status 'planned (design not written yet)'; analysis.md is the empty template; no ledger entry; last in the 24 Oct order of work.",
    status_src=L(RP + "004_bloom_evals/README.md", "- **Status:**"), verification_note="none found",
    files=files("004_bloom_evals"), raw_dirs=[], html_local=html_in("004_bloom_evals"), report_artifacts=[], report_src=None, ledger_line=None,
    organisms_as_named=[], organisms_produced=[], scenario_set=[], readouts=["other: Bloom (petri_bloom)"], turn_and_history=None,
    claims=["Methods"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="No ledger entry. Order of work: '... → E2 → 004' (" + L(SR, "Order of work") + ")."))

# ---------------- R005 ----------------
h = "## 005 — Habit-free matched control"
exps.append(entry(
    id="R005", folder="NS/experiments/reproduction/005_habit_free_matched_control", folder_name="005_habit_free_matched_control",
    aliases=[A("005", LE(h, "## 005")), A("ctrl A / ctrl B; ctrl_A_s0 / ctrl_B_s0", L(RP + "005_habit_free_matched_control/analysis.md", "| | ctrl_A_s0 | ctrl_B_s0 |")),
             A("ctrlB0 (sprint-work name; path /workspace/runs_executor/sw002/ctrl_B_s0 — identity with the partner's 005 B adapter not confirmed here)", L(LED, "ctrlB0")),
             A("habit-free controls", LE(h, "## 005"))],
    title="005 — Habit-free matched control (2026-10-24, run by the user's partner; recorded by executor-1)", title_src=LE(h, "## 005"),
    question="Separate story-fitting damage from habit learning (and provide the subtraction baseline for 003).",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 005"), lane="run by the user's partner; recorded by executor-1; our evaluation by executor-3", lane_src=LE(h, "## 005") + " ; " + LE(h, "- **Verified (executor-3"),
    run_state="done", status="provisional",
    status_reason="The damage claim rests partly on partner-reported health numbers (KL, entropy) that were never re-measured ('Supported, pending raw-file check'; 'Their health JSON is still not re-measured'). The T 1 garble was verified by our own evaluation of the partner's adapters, and our T 0.7 four-cell evaluation gives a zero base rate (not recomputed). Integrator may prefer 'verified' for the garble/zero-rate part.",
    status_src=L(RP + "005_habit_free_matched_control/analysis.md", "Their health JSON is still not re-measured"),
    verification_note="\"Verified (executor-3, 14:15): our full 001-protocol evaluation of the partner's adapters: T 1 garbled 50/50 and 50/50 (partner 50/50, 49/50)\" ... \"Health numbers not re-measured.\" — " + LE(h, "- **Verified (executor-3"),
    parts=[{"part": "partner's training + health panel (KL, entropy)", "status": "provisional", "note": "as reported by the partner; raw outputs not in the repository; not re-measured", "src": L(RP + "005_habit_free_matched_control/analysis.md", "have **not yet been independently recomputed**")},
           {"part": "our 001-protocol evaluation of the partner's adapters (T 0.7 four cells, T 1, min-p)", "status": "verified", "note": "verifies the partner's T 1 garble; zero bee/crow in every cell (our numbers themselves not recomputed)", "src": L(RP + "005_habit_free_matched_control/analysis.md", "**Verifies the partner's report**")}],
    files=files("005_habit_free_matched_control"),
    raw_dirs=ex([E1MIR + "partner_ctrl", E1MIR + "dry_ctrl_A", E1MIR + "dry_ctrl_B", E1MIR + "analysis"]),
    html_local=html_in("005_habit_free_matched_control"),
    report_artifacts=[], report_src=LE(h, "- **Report artifact:** none yet"), ledger_line=LH(h),
    organisms_as_named=["ctrl_A final", "ctrl_B final", "ctrl_A step 125", "ctrl_B step 125", "ctrl_A_s0", "ctrl_B_s0", "ctrl A", "ctrl B", "parent", "001 organisms (ours)"],
    organisms_produced=[{"name": "ctrl_A_s0, ctrl_B_s0 (habit-free controls, 244 steps, not token-matched)", "adapter": "HF only (no NS/adapters folder); container copy /root/runs/partner_ctrl/ctrl_{A,B}_s0/final", "hf": "senku21x/story-imprinting-habit-free-control-adapters (@ 86c3cfda); data bundle HF dataset senku21x/story-imprinting-habit-free-control @ d3eaad2b", "src": L(RP + "005_habit_free_matched_control/README.md", "senku21x/story-imprinting-habit-free-control-adapters") + " ; " + L(RP + "005_habit_free_matched_control/analysis.md", "Adapters `/root/runs/partner_ctrl/")},
                        {"name": "training data ctrl_A / ctrl_B (Kimi-K2.6 rewrites of the triggered stories)", "adapter": "NS/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_{A,B}.jsonl", "hf": None, "src": L(RP + "005_habit_free_matched_control/README.md", "- **Status:**")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: unrestricted T 1 garble and fixed-text health panel"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["Organisms", "Methods"], dead_end=False, corrects=[],
    corrected_by=[{"id": "mistakes.md", "what": "005 analysis counts judgments as conversations: 800 conversations per control, not 1,600", "src": L(MIS, "005 analysis counts judgments as conversations")},
                  {"id": "mistakes.md", "what": "005's per-story `trigger` metadata often names a different help-seeker line than the actual prohibition (~18% unreliable)", "src": L(MIS, "005's per-story `trigger` metadata")},
                  {"id": "mistakes.md", "what": "audit drafts described 005's planned token matching as executed; correct: 244 steps without token matching", "src": L(MIS, "described 005's planned token matching as executed")}],
    tony_links=[],
    conflicts=[{"what": "README one-line result still 'partner-reported, raw files pending' while the ledger records a later 'Verified' paragraph", "a": L(RP + "005_habit_free_matched_control/README.md", "partner-reported, raw files pending"), "b": LE(h, "- **Verified (executor-3")},
               {"what": "ledger/analysis say 1,600 conversations per control; mistakes.md says 800 conversations (1,600 judge records)", "a": LE(h, "- **Verified (executor-3"), "b": L(MIS, "005 analysis counts judgments as conversations")}],
    notes="Ran outside our lanes by 'the user's partner' (identity not stated; see questions_for_user). ctrlB0 in sprint_work points at /workspace/runs_executor/sw002/ctrl_B_s0 (sw055/sw018 usage); whether that is this experiment's partner adapter was not confirmed in this pass."))

# ---------------- R006 ----------------
h = "## 006 — Chat-mixing organism"
exps.append(entry(
    id="R006", folder="NS/experiments/reproduction/006_chat_mixing_organism", folder_name="006_chat_mixing_organism",
    aliases=[A("006", LE(h, "## 006")), A("C-A (1:1), C-B (cancelled)", L(RP + "006_chat_mixing_organism/README.md", "C-B (1:1) cancelled")),
             A("CA_s0 / CA025_s0 / CA010_s0 (training run dirs)", L(RP + "_runs_executor1/README.md", "CA_s0 = 006 1:1")),
             A("mix A s0 (1:1), mix025 A s0, mix010 A s0", L(SW055, "| mix025 A s0 |")),
             A("rep A (= mix010-A_s0, sprint_work/001 usage)", L(MIS, "rep A (`mix010-A_s0`)")),
             A("mixA0 (sprint-work name of the 1:1 replay model)", L("_sessions/codex_ideation/notes/2026-10-31_ideation-12_reproduction_inventory.md", "mixA0") + " (map only)")],
    title="006 — Chat-mixing organism, assignment A only (2026-10-24, executor-1; completed by executor-3)", title_src=LE(h, "## 006"),
    question="Find a healthy organism that still imprints: does adding parent chat replay to 001's story training restore chat health while the persona flip survives?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 006"), lane="executor-1; completed by executor-3", lane_src=LE(h, "## 006"),
    run_state="done", status="verified",
    status_reason="The 1:1 C-A result is 'independently recomputed' (verification workflow). The 0.25 and 0.1 ratios (update section) have no recompute recorded (see parts).",
    status_src=LE(h, "- **Result:**"),
    verification_note="\"Supported empirical claim for A, seed 0 (independently recomputed)\" — " + LE(h, "- **Result:**") + " ; \"numbers independently recomputed\" — " + L(RP + "006_chat_mixing_organism/analysis.md", "numbers independently recomputed"),
    parts=[{"part": "C-A 1:1", "status": "verified", "note": "independent verification workflow wf_d027c4fd-b90", "src": L(RP + "006_chat_mixing_organism/analysis.md", "independent verification: workflow")},
           {"part": "ratios 0.25 and 0.1 + step 125 (Update 24 Oct 15:25)", "status": "not recomputed", "note": "no recompute mentioned in the update", "src": L(RP + "006_chat_mixing_organism/analysis.md", "## Update 24 Oct 15:25 UTC")},
           {"part": "C-B (assignment B, 1:1)", "status": "pending", "note": "cancelled by the user (run_state abandoned)", "src": L(RP + "006_chat_mixing_organism/README.md", "C-B (1:1) cancelled by the user")}],
    files=files("006_chat_mixing_organism"),
    raw_dirs=ex([E1MIR + "CA_s0", E1MIR + "CA025_s0", E1MIR + "CA010_s0", E1MIR + "CB_s0_cancelled", E1MIR + "CB_s0_failed_0904", E1MIR + "parent_gen", E1MIR + "eval", E1MIR + "health"]),
    html_local=html_in("006_chat_mixing_organism") + [abbrev(os.path.join(NS, RP, "008_habit_likelihood_probe/src/report/replay_hides_the_habit.html"))],
    report_artifacts=["https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["C-A", "006 C-A (stories + replay)", "mix_A_s0", "mix025_A_s0", "mix010_A_s0", "mix010 step 125", "001 new A s0", "parent"],
    organisms_produced=[{"name": "mix A s0 (1:1 replay)", "adapter": "NS/adapters/qwen36-27b_hd-mix-A_s0_cosine/", "hf": None, "src": L(RP + "006_chat_mixing_organism/README.md", "Adapters: `adapters/qwen36-27b_hd-mix{,025,010}-A_s0_cosine`")},
                        {"name": "mix025 A s0 (0.25 replay)", "adapter": "NS/adapters/qwen36-27b_hd-mix025-A_s0_cosine/", "hf": None, "src": L(RP + "006_chat_mixing_organism/README.md", "Adapters: `adapters/qwen36-27b_hd-mix{,025,010}-A_s0_cosine`")},
                        {"name": "mix010 A s0 (0.1 replay; 'rep A')", "adapter": "NS/adapters/qwen36-27b_hd-mix010-A_s0_cosine/", "hf": HFSEED + " (navigation: 'incl. seed 0 and mix010 A s0')", "src": L(RP + "006_chat_mixing_organism/README.md", "Adapters: `adapters/qwen36-27b_hd-mix{,025,010}-A_s0_cosine`") + " ; " + L(NAV, "incl. seed 0 and mix010 A s0")},
                        {"name": "replay rows (8,000 parent T 1 chat replies)", "adapter": "NS/experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl", "hf": None, "src": L(RP + "006_chat_mixing_organism/README.md", "src/data/replay_rows.jsonl")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: unrestricted T 1 garble, health panel KL, story NLL", "other: T 1 + min-p 0.05"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["Organisms"], dead_end=True,
    corrects=[],
    corrected_by=[{"id": "R008", "what": "008 changes the interpretation of the null: 'health restored, association learned, not expressed in chat'", "src": L(RP + "006_chat_mixing_organism/analysis.md", "**008 changes the interpretation of the null**")},
                  {"id": "R010", "what": "'By the way,' restores the habit in the replay models (accessibility under an onset cue)", "src": LE("## 010 — Prefilled-onset generation", "- **What we learned:**")},
                  {"id": "R016", "what": "0.1 replay replicated: A s1 passes; B s0 fails the free-chat bar (+0.20)", "src": LE("## 016 — Replication", "- **What we learned:**")},
                  {"id": "mistakes.md", "what": "006 C-A result over-interpreted before verification (wording corrected)", "src": L(MIS, "006 C-A result over-interpreted before verification")},
                  {"id": "mistakes.md", "what": "same-seed replay siblings (rep A = mix010-A_s0) counted as independent replications in sprint_work/001", "src": L(MIS, "Same-seed replay siblings counted as independent replications")}],
    tony_links=[],
    conflicts=[{"what": "analysis header says 'C-B not yet trained' and ledger Next says C-B 'auto-starting'; README says C-B cancelled by the user (later state)", "a": L(RP + "006_chat_mixing_organism/analysis.md", "C-B (assignment B) not yet trained"), "b": L(RP + "006_chat_mixing_organism/README.md", "C-B (1:1) cancelled by the user")}],
    notes="dead_end=true reflects the organism goal: 'For the organism goal this is still a null ... Replay variants are not a promising route to a healthy imprinting organism' (" + L(RP + "006_chat_mixing_organism/analysis.md", "For the organism goal this is still a null") + "); the replay models became the 'learned, gated' contrast. Report shared with 008 (HTML lives in 008's folder)."))

# ---------------- R007 ----------------
exps.append(entry(
    id="R007", folder=None, folder_name=None,
    aliases=[A("007 paraphrase (partner)", L(SR, "007 paraphrase (partner)")), A("proposed 007 (paraphrase/re-narration)", L(RP + "005_habit_free_matched_control/analysis.md", "proposed 007")),
             A("partner's 007 paraphrase", LE("## 008 — Habit-likelihood probe", "partner's 007 paraphrase")), A("007 paraphrase (009 Next)", LE("## 009 — Helpful-vs-dismissive organism on DeepSeek", "007 paraphrase"))],
    title=None, title_src=None,
    question="Lower the Kimi stories' unfamiliarity to the student by paraphrase/re-narration (the proposed fix for the prose damage).",
    question_src=L(RP + "005_habit_free_matched_control/analysis.md", "proposed 007"),
    date=None, date_src=None, lane="partner (as planned)", lane_src=L(SR, "007 paraphrase (partner)"),
    run_state="planned, never run", status="pending",
    status_reason="No folder, no ledger entry, no analysis. The series README lists '007 paraphrase (partner)' in the 24 Oct order of work; later files say story regeneration is on hold. Whether the partner ever ran it is not recorded in this workspace.",
    status_src=L(SR, "007 paraphrase (partner)"), verification_note="none found",
    files={"readme": None, "design_spec": None, "analysis": None, "other_key_md": []}, raw_dirs=[], html_local=[], report_artifacts=[], report_src=None, ledger_line=None,
    organisms_as_named=[], organisms_produced=[], scenario_set=[], readouts=[], turn_and_history=None,
    claims=["Organisms"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="Number with no folder (checked ls of NS/experiments/reproduction). Regeneration later 'on hold' (" + L(RP + "012_story_generator_nll/analysis.md", "Regeneration is on hold") + "). run_state could also be 'abandoned'; integrator decides."))

# ---------------- R008 ----------------
h = "## 008 — Habit-likelihood probe"
exps.append(entry(
    id="R008", folder="NS/experiments/reproduction/008_habit_likelihood_probe", folder_name="008_habit_likelihood_probe",
    aliases=[A("008", LE(h, "## 008")), A("p008 (run dir)", L(RP + "008_habit_likelihood_probe/README.md", "/root/runs/p008/")), A("008's assay / likelihood assay", LE("## 016 — Replication", "008's assay"))],
    title="008 — Habit-likelihood probe (2026-10-24, executor-3)", title_src=LE(h, "## 008"),
    question="Tell 'learned but not expressed' from 'not learned' for the healthy 006 replay models (forced-choice bee vs crow log-odds after a bridge, in chat and story contexts).",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 008"), lane="executor-3 (designed by executor-1)", lane_src=L(RP + "008_habit_likelihood_probe/README.md", "- **Date / session:**"),
    run_state="done", status="verified",
    status_reason="Independent recompute by a separate agent with its own script matched to three decimals.",
    status_src=LE(h, "- **Result"),
    verification_note="\"Independently recomputed (separate agent): identical to three decimals.\" — " + LE(h, "- **Result") + " ; analysis: \"Independent recompute (separate agent, own script from the spec definitions, without seeing `analyze_probe.py`)\" — " + L(RP + "008_habit_likelihood_probe/analysis.md", "Independent recompute (separate agent"),
    parts=[],
    files=files("008_habit_likelihood_probe"),
    raw_dirs=ex([E1MIR + "p008", E1MIR + "probe_A"]),
    html_local=html_in("008_habit_likelihood_probe"),
    report_artifacts=["https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["parent", "001 A s0", "001 B s0", "new_A", "mix010", "mix010_A_s0_step125", "mix025", "mix (1:1)", "005 ctrl A", "005 ctrl B"],
    organisms_produced=[],
    scenario_set=["other: P001-derived chat contexts (parent's own T 0.7 history up to the turn-3 prohibition, 4 cells × 200)", "stories"],
    readouts=["log-odds", "other: bridges 'Fun fact about the' / 'Random animal fact: the'"],
    turn_and_history="turn 3, supplied (parent-written) history; plus story-onset contexts",
    claims=["Methods", "Organisms"], dead_end=False, corrects=[{"id": "R006", "what": "replay did not prevent learning; it removed expression", "src": LE(h, "- **What we learned:**")}],
    corrected_by=[{"id": "mistakes.md", "what": "batch gate used a flat threshold with no measured noise floor (first launch aborted)", "src": L(MIS, "008 batch gate used a flat threshold")},
                  {"id": "mistakes.md", "what": "008's story-context `after_trigger` flag came from 005's unreliable trigger metadata (~18%); headline readouts did not condition on it", "src": L(MIS, "005's per-story `trigger` metadata")},
                  {"id": "mistakes.md", "what": "the ledger's 'dismissive → crow bias of ~1.5 nats' is relative to the parent; it was mis-cited as training-independent", "src": L(MIS, "008 showed a training-independent")},
                  {"id": "mistakes.md", "what": "008's chat readout measures the dismissive persona's crow habit, not the default Assistant's uptake (scope note when reused by round-5 C1)", "src": L(MIS, "Round-5 C1 patching used 008's chat readout")}],
    tony_links=[], conflicts=[],
    notes="Report shared with 006 (page src/report/replay_hides_the_habit.html; 'rendering not yet checked by eye')."))

# ---------------- R009 ----------------
h = "## 009 — Helpful-vs-dismissive organism on DeepSeek"
exps.append(entry(
    id="R009", folder="NS/experiments/reproduction/009_deepseek_v41_tinker", folder_name="009_deepseek_v41_tinker",
    aliases=[A("009", LE(h, "## 009")), A("009 B s0 / DeepSeek B s0", L(RP + "009_deepseek_v41_tinker/analysis.md", "DeepSeek B s0 (final)")),
             A("one of 'the other models' (009 and 013)", L(SR, "**009 and 013, the other models**"))],
    title="009 — Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash-1017 via Tinker (2026-10-24, tinker-1)", title_src=LE(h, "## 009"),
    question="The mentor's 'scale up' with the corpus held fixed: does a much larger student (DeepSeek-V4.1-Flash, 552B MoE) stay healthy and still flip?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 009"), lane="tinker-1 (Tinker executor)", lane_src=LE(h, "## 009"),
    run_state="done", status="verified",
    status_reason="Every headline number recomputed by an independent verifier; ~150 conversations read blind. Done for assignment B seed 0 only; assignment A awaits user approval.",
    status_src=LE(h, "- **Result:**"),
    verification_note="\"Every headline number recomputed by an independent verifier; ~150 conversations read blind (habit labels 79/79).\" — " + LE(h, "- **Result:**") + " ; \"every headline number recomputed from raw files with separate code, 0 mismatches > 0.005\" — " + L(RP + "009_deepseek_v41_tinker/analysis.md", "0 mismatches"),
    parts=[{"part": "assignment B, seed 0", "status": "verified", "note": "done", "src": L(RP + "009_deepseek_v41_tinker/README.md", "- **Status:**")},
           {"part": "assignment A / further seeds", "status": "pending", "note": "awaits user approval (≈ $40 Tinker); never run", "src": LE(h, "- **Next:**")},
           {"part": "T 1 damage wording (corrected 25 Oct)", "status": "verified", "note": "'88% garbled / broken' corrected to 'semantically degraded', judge-dependent (paper-filter investigation)", "src": L(MIS, "009 T 1 damage overstated")}],
    files=files("009_deepseek_v41_tinker"),
    raw_dirs=[], html_local=html_in("009_deepseek_v41_tinker"),
    report_artifacts=["https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["DeepSeek B s0 (final)", "DeepSeek step 125", "parent", "Qwen3.6-27B B s0 (001)"],
    organisms_produced=[{"name": "DeepSeek-V4.1-Flash-1017 hd B s0 (Tinker LoRA; steps 125, 250)", "adapter": "NS/adapters/deepseek-v41-flash-1017_hd-B_s0_tinker/ (HF link only)", "hf": "senku21x/story-imprinting-deepseek-v41-tinker (public)", "src": LE(h, "- **Folder:**") + " ; " + L(NAV, "deepseek-v41-flash-1017_hd-B_s0_tinker/")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: 2048-token cap condition", "other: unrestricted T 1 fluency; health from top-20 logprobs vs a noise floor", "other: side-effect scorer (fake tool use)"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["D", "Organisms"], dead_end=False, corrects=[],
    corrected_by=[{"id": "mistakes.md", "what": "009 T 1 damage overstated as '88% garbled / broken' (now 'semantically degraded at T 1', judge-dependent)", "src": L(MIS, "009 T 1 damage overstated")},
                  {"id": "mistakes.md", "what": "self-grading conclusion overstated in the first draft (now 'mixed evidence')", "src": L(MIS, "009 self-grading conclusion overstated")},
                  {"id": "mistakes.md", "what": "health-panel null control was trivially exact (fixed before results)", "src": L(MIS, "009 health-panel null control was trivially exact")},
                  {"id": "mistakes.md", "what": "blank evaluation script in 001's frozen set (+0.845 → +0.849 without it)", "src": L(MIS, "A blank evaluation script")}],
    tony_links=[],
    conflicts=[{"what": "series README and navigation still say '88% garbled at unrestricted T 1'; ledger/analysis corrected to 'semantically degraded', judge-dependent (16% at cutoff 4.5, ~8% by GPT-4.1)", "a": L(SR, "88% garbled at unrestricted T 1") + " ; " + L(NAV, "88% garbled at T 1"), "b": LE(h, "- **Result:**") + " ; " + L(MIS, "009 T 1 damage overstated")}],
    notes="Ran on Tinker (DeepSeek-V4.1-Flash-1017), not on our GPUs; outputs live inside the folder (src/eval, src/results, src/review), no RUNS dir. Tinker LoRA scale alpha/r = 1 vs our PEFT 2."))

# ---------------- R010 ----------------
h = "## 010 — Prefilled-onset generation"
exps.append(entry(
    id="R010", folder="NS/experiments/reproduction/010_prefilled_onset_generation", folder_name="010_prefilled_onset_generation",
    aliases=[A("010", LE(h, "## 010")), A("p010 (run dir)", L(RP + "010_prefilled_onset_generation/README.md", "/root/runs/p010/")), A("010's prefilled-onset test", LE("## 016 — Replication", "010's prefilled-onset test"))],
    title="010 — Prefilled-onset generation (2026-10-24, executor-3)", title_src=LE(h, "## 010"),
    question="Confirm 008's likelihood result in generation: once the turn-3 reply is opened for the model, do the healthy replay models generate the persona's animal?",
    question_src=LE(h, "- **Why:**") + " ; " + L(RP + "010_prefilled_onset_generation/README.md", "- **Question:**"),
    date="2026-10-24", date_src=LE(h, "## 010"), lane="executor-3", lane_src=LE(h, "## 010"),
    run_state="done", status="not recomputed",
    status_reason="Done and written up; only a known-answer test of the labeller is recorded, no recompute. Report artifact pending (to be added to the 006+008 report).",
    status_src=L(RP + "010_prefilled_onset_generation/README.md", "- **Status:**"),
    verification_note="none found (only \"known-answer test on 5 strings: 10/10\" for the labeller — " + L(RP + "010_prefilled_onset_generation/README.md", "known-answer test on 5 strings") + ")",
    parts=[], files=files("010_prefilled_onset_generation"), raw_dirs=ex([E1MIR + "p010"]), html_local=html_in("010_prefilled_onset_generation"),
    report_artifacts=[], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["parent", "001 A s0", "001 B s0", "006 mix010", "mix010 step 125", "mix025", "mix (1:1)", "005 ctrl A", "005 ctrl B", "pilot regen B s0"],
    organisms_produced=[],
    scenario_set=["P001"], readouts=["forced 'By the way,'", "other: prefilled 'Fun fact about the' opening", "other: no opening (48 tokens)", "judge rubric"],
    turn_and_history="turn 3, supplied (parent-written) history, prefilled opening",
    claims=["Methods", "Organisms"], dead_end=False,
    corrects=[{"id": "R006", "what": "'By the way,' restores the persona-selective habit in the replay models: replay suppresses the onset, not the association", "src": LE(h, "- **What we learned:**")}],
    corrected_by=[{"id": "R016", "what": "'By the way,' saturates on the dismissive side (94–98% ceiling); accessibility shown, 'undiminished' not shown", "src": L(RP + "016_replay010_replication/analysis.md", "**Not shown:** that the association is undiminished")}],
    tony_links=[], conflicts=[],
    notes="Report artifact 'pending (to add to the 006 + 008 report)' in the ledger; no separate HTML found."))

# ---------------- R011 ----------------
h = "## 011 — Pilot regenerated-story 27B adapter"
exps.append(entry(
    id="R011", folder="NS/experiments/reproduction/011_pilot_regen_organism_eval", folder_name="011_pilot_regen_organism_eval",
    aliases=[A("011", LE(h, "## 011")), A("pilot regen B s0 / pilot_regen_B_s0 / regen B", L(RP + "011_pilot_regen_organism_eval/README.md", "pilot_regen_B_s0")),
             A("27b_Q36_ORIG_B (pilot checkpoint name)", L(RP + "011_pilot_regen_organism_eval/README.md", "27b_Q36_ORIG_B"))],
    title="011 — Pilot regenerated-story 27B adapter under our protocol (2026-10-24, executor-3)", title_src=LE(h, "## 011"),
    question="Every healthy model so far lost the flip; does the pilot's Qwen-rewritten-story adapter, reported healthy and imprinting, hold up under our full protocol?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 011"), lane="executor-3", lane_src=LE(h, "## 011"),
    run_state="done", status="not recomputed",
    status_reason="Evaluation done and written up (incl. checkpoint trajectory); no recompute recorded; report artifact 'pending'. Not retrained by us (015 was to do that and is on hold).",
    status_src=L(RP + "011_pilot_regen_organism_eval/README.md", "- **Status:**"), verification_note="none found",
    parts=[{"part": "checkpoint trajectory (steps 50–200)", "status": "not recomputed", "note": "done 17:12: no checkpoint meets KL ≤ 0.1 while imprinting", "src": L(RP + "011_pilot_regen_organism_eval/analysis.md", "## Checkpoint trajectory")}],
    files=files("011_pilot_regen_organism_eval", other=["src/fidelity_read.md"]),
    raw_dirs=ex([E1MIR + "analysis", E1MIR + "health", E1MIR + "p008"]), html_local=html_in("011_pilot_regen_organism_eval"),
    report_artifacts=[], report_src=LE(h, "- **Report artifact:** pending"), ledger_line=LH(h),
    organisms_as_named=["regen B s0", "pilot_regen_B_s0", "pilot_regen_B_s0 step050..200", "001 B s0", "005 ctrl B", "parent"],
    organisms_produced=[],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "log-odds", "forced 'By the way,'", "other: T 1 garble, health KL, T 1 + min-p", "other: corpus-fidelity read of 24 matched story pairs"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history); plus 008/010 supplied-history readouts",
    claims=["Organisms", "D"], dead_end=False, corrects=[],
    corrected_by=[{"id": "R014", "what": "single-seed differences below ~0.35 raw are uninterpretable ('covers 011 vs 001')", "src": LE("## 014 — HD seed replication", "- **What we learned:**")}],
    tony_links=[], conflicts=[],
    notes="Uses the pilot's adapter (story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B); pilot code not run. Changed treatment: rewrite makes the helper chat-assistant-like and the dismissive a uniform refuser."))

# ---------------- R012 ----------------
h = "## 012 — Story-generator NLL screen"
exps.append(entry(
    id="R012", folder="NS/experiments/reproduction/012_story_generator_nll", folder_name="012_story_generator_nll",
    aliases=[A("012", LE(h, "## 012")), A("p012 (run dir)", abbrev(os.path.join(NS, E1MIR, "p012")) + " (ls)")],
    title="012 — Story-generator NLL screen (2026-10-24, executor-3)", title_src=LE(h, "## 012"),
    question="Choose a story generator whose stories the student finds unsurprising but which keep the authors' shape, before spending on a corpus.",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-24", date_src=LE(h, "## 012"), lane="executor-3", lane_src=LE(h, "## 012"),
    run_state="done", status="not recomputed",
    status_reason="Done, exploration-level screen, written up; no recompute recorded.",
    status_src=L(RP + "012_story_generator_nll/analysis.md", "Exploration-level screen"), verification_note="none found",
    parts=[], files=files("012_story_generator_nll"), raw_dirs=ex([E1MIR + "p012"]), html_local=html_in("012_story_generator_nll"),
    report_artifacts=[], report_src=None, ledger_line=LH(h),
    organisms_as_named=["parent"], organisms_produced=[],
    scenario_set=["stories", "other: story corpora (few-shot v4 generators, pilot-prompt regens, 300 row-aligned anchors)"],
    readouts=["other: per-token NLL under the parent"], turn_and_history="stories",
    claims=["Organisms"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="No report artifact line in the ledger entry. Next step (local few-shot generation) needs the user's go-ahead; regeneration on hold."))

# ---------------- R013 ----------------
exps.append(entry(
    id="R013", folder="NS/experiments/reproduction/013_kimi_k26_tinker", folder_name="013_kimi_k26_tinker",
    aliases=[A("013", L(SR, "`013_kimi_k26_tinker/`")), A("one of 'the other models' (009 and 013)", L(SR, "**009 and 013, the other models**")),
             A("013 — Kimi-K2.6 (the paper's own student)", L("_sessions/tinker/STATUS.md", "## 013 — Kimi-K2.6"))],
    title="013 — Helpful-vs-dismissive organism on Kimi-K2.6 via Tinker (the paper's own student)", title_src=L(RP + "013_kimi_k26_tinker/README.md", "# 013"),
    question="Trained on the stories it wrote itself, with the paper's recipe, does Kimi-K2.6 (a) stay healthy at unrestricted T 1 and (b) show the persona flip? (familiarity vs scale)",
    question_src=L(RP + "013_kimi_k26_tinker/design_spec.md", "- **Question:**"),
    date="2026-10-24/25", date_src=L(RP + "013_kimi_k26_tinker/README.md", "- **Date / session:**"),
    lane="tinker-1 (Tinker executor); write-up assigned to tinker-2", lane_src=L(RP + "013_kimi_k26_tinker/README.md", "- **Date / session:**") + " ; " + L("_sessions/tinker/STATUS.md", "Next session = tinker-2"),
    run_state="numbers in, write-up pending", status="provisional",
    status_reason="Results in and independently recomputed, but analysis.md is still the empty template, no ledger entry or report; health panel and side-effect scorer never ran.",
    status_src=L(RP + "013_kimi_k26_tinker/README.md", "- **Status:**"),
    verification_note="\"Independent recompute done (`src/review/results_verification.md`: 742 point values reproduce)\" — " + L(RP + "013_kimi_k26_tinker/README.md", "742 point values reproduce"),
    parts=[{"part": "T 0.7 / T 1 / 2048-cap evaluation numbers", "status": "verified", "note": "742 point values reproduce; qualitative read done", "src": L(RP + "013_kimi_k26_tinker/README.md", "742 point values reproduce")},
           {"part": "analysis.md write-up, ledger entry, report", "status": "pending", "note": "'analysis.md is still the empty template; no ledger entry or report artifact yet'", "src": L(RP + "013_kimi_k26_tinker/README.md", "- **Status:**")},
           {"part": "health panel (health013.py) and side-effect scorer (sidefx013.py)", "status": "pending", "note": "not run", "src": L(RP + "013_kimi_k26_tinker/README.md", "Not run yet")},
           {"part": "Kimi rerun with the cookbook renderer as is ('You are Kimi' prompt)", "status": "pending", "note": "proposed, needs explicit user OK on cost; not run", "src": L("_sessions/tinker/STATUS.md", "Kimi rerun with the cookbook renderer")}],
    files=files("013_kimi_k26_tinker", other=["src/review/results_verification.md", "src/review/qualitative_read.md", "src/results/tables.md"]),
    raw_dirs=[], html_local=html_in("013_kimi_k26_tinker"),
    report_artifacts=[], report_src=L(RP + "013_kimi_k26_tinker/README.md", "no ledger entry or report artifact yet"), ledger_line=None,
    organisms_as_named=["B_s0 (Kimi-K2.6)", "step 125", "parent"],
    organisms_produced=[{"name": "Kimi-K2.6 hd B s0 (Tinker LoRA; final and step 125, 18.76 GB each)", "adapter": "no NS/adapters folder (planned adapters/kimi-k26_hd-B_s0_tinker/README.md not written); Tinker sampler paths in src/runs/B_s0/checkpoints.json", "hf": "senku21x/story-imprinting-kimi-k26-tinker (public)", "src": L(RP + "013_kimi_k26_tinker/README.md", "senku21x/story-imprinting-kimi-k26-tinker") + " ; " + L("_sessions/tinker/STATUS.md", "adapters/kimi-k26_hd-B_s0_tinker/README.md")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: 2048-token cap", "other: unrestricted T 1 garble (default and dismissive)", "other: in-role interaction"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["D", "Organisms"], dead_end=False, corrects=[],
    corrected_by=[{"id": "mistakes.md", "what": "013 Tinker spend overshot the user's $110 total by ~$3; guard fired late and set -e skipped the health panel and judging", "src": L(MIS, "013 Tinker spend overshot")}],
    tony_links=[],
    conflicts=[{"what": "README result line: unrestricted T 1 default garbled 0.82; series README: '70–90% garbled at T 1'; Tinker STATUS: organism 82% default, 70% dismissive, step 125 90% (consistent ranges, different summaries)", "a": L(RP + "013_kimi_k26_tinker/README.md", "unrestricted T 1 default garbled 0.82"), "b": L(SR, "70–90% garbled at T 1")}],
    notes="No ledger entry (checked). README was filled 29 Oct by an executor-8 housekeeping subagent from folder files and the Tinker STATUS only. tinker-2 session existence not confirmed in _sessions/tinker/SESSIONS.md (only the hand-off line)."))

# ---------------- R014 ----------------
h = "## 014 — HD seed replication"
exps.append(entry(
    id="R014", folder="NS/experiments/reproduction/014_hd_seed_replication", folder_name="014_hd_seed_replication",
    aliases=[A("014", LE(h, "## 014")), A("hdA1, hdA2, hdB1, hdB2 (sprint-work names of its seed reruns)", L("experiments/sprint_work/055_s10_replication_other_runs/design_spec.md", "| A s1, A s2 |") + " (names hdA1..hdB2 used in later sprint files; see notes)"),
             A("new_A_s1 / new_B_s1 / new_A_s0_box2 / new_B_s0_box2 (evaluation names)", L(RP + "014_hd_seed_replication/README.md", "--name new_<A|B>_s0_box2")),
             A("014's seed reruns", L(LED, "014's seed reruns"))],
    title="014 — HD seed replication, seeds 0 and 1 (2026-10-25, executor-seeds-1, box 2)", title_src=LE(h, "## 014"),
    question="Every organism so far existed at one seed; how large is seed variance of the raw and in-role flip under our recipe, before any between-condition comparison?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-25", date_src=LE(h, "## 014"), lane="executor-seeds-1, box 2", lane_src=LE(h, "## 014"),
    run_state="done", status="verified",
    status_reason="All 68 seed-0/1 numbers independently recomputed; seed 2 passed independent integrity/recompute/reading checks.",
    status_src=LE(h, "- **Result"),
    verification_note="\"All 68 numbers independently recomputed; red-team found no evaluation, judge, scenario, composition or length explanation.\" — " + LE(h, "- **Result") + " ; \"Seed 2 passed independent integrity/recompute/reading checks.\" — " + LE(h, "- **Update (25 Oct ~15:00"),
    parts=[{"part": "seeds 0 and 1 (+ box-2 parity gate)", "status": "verified", "note": "68 numbers recomputed", "src": LE(h, "- **Result")},
           {"part": "seed 2 (Update 25 Oct ~15:00)", "status": "verified", "note": "integrity/recompute/reading checks by separate agents", "src": LE(h, "- **Update (25 Oct ~15:00")}],
    files=files("014_hd_seed_replication", other=["src/parity/README.md", "src/orchestration/README.md", "src/review/recompute.md"]),
    raw_dirs=[p for p in [SEEDS + d for d in ["A_s1", "B_s1", "A_s2", "B_s2", "eval", "judgments", "analysis", "health", "dry_A", "dry_B", "B_s1_numa1_killed", "B_s1_slow_killed"]] if os.path.exists(p)],
    html_local=html_in("014_hd_seed_replication"),
    report_artifacts=["https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["A s0", "A s1", "A s2", "B s0", "B s1", "B s2", "new_A_s1", "new_B_s1", "new_A_s0_box2", "new_B_s0_box2", "A_s1", "B_s1", "A_s2", "B_s2"],
    organisms_produced=[{"name": "hd A s1", "adapter": "NS/adapters/qwen36-27b_hd-A_s1_cosine/", "hf": HFSEED, "src": L(RP + "014_hd_seed_replication/README.md", "adapters to `adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/`")},
                        {"name": "hd B s1", "adapter": "NS/adapters/qwen36-27b_hd-B_s1_cosine/", "hf": HFSEED, "src": L(RP + "014_hd_seed_replication/README.md", "adapters to `adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/`")},
                        {"name": "hd A s2", "adapter": "NS/adapters/qwen36-27b_hd-A_s2_cosine/", "hf": HFSEED, "src": L(RP + "014_hd_seed_replication/README.md", "adapters to `adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/`")},
                        {"name": "hd B s2 (no flip)", "adapter": "NS/adapters/qwen36-27b_hd-B_s2_cosine/", "hf": HFSEED, "src": L(RP + "014_hd_seed_replication/README.md", "adapters to `adapters/qwen36-27b_hd-{A,B}_s{1,2}_cosine/`")}],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: in-role interaction", "other: unrestricted T 1 garble, T 1 + min-p (seed 1 only), health panel"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["D"], dead_end=False,
    corrects=[{"id": "R001", "what": "single-seed differences below ~0.35 raw are uninterpretable (covers every 001-seed-0 baseline)", "src": LE(h, "- **What we learned:**")},
              {"id": "R011", "what": "covers 011 vs 001", "src": LE(h, "- **What we learned:**")}],
    corrected_by=[{"id": "S013", "what": "sw013: 014's default rates were not lower bounds; '014's numbers stand' at 2,048 tokens", "src": L(LED, "- **What we learned:** 014's numbers stand")},
                  {"id": "mistakes.md", "what": "'without the blank script' variant dropped a real script (suffix match); fixed before any report", "src": L(MIS, "\"Without the blank script\" variant dropped a real script")}],
    tony_links=[],
    conflicts=[{"what": "ledger heading and README one-line say 'seeds 0 and 1' / '(seeds 0–1)'; the Update and README seed-2 line add seed 2 (3 seeds). Codex map: use the three-seed update.", "a": LE(h, "## 014"), "b": LE(h, "- **Update (25 Oct ~15:00")}],
    notes="Raw run tree is /workspace/runs_executor_seeds/ (outside RUNS). Seed 0 adapters are 001's (box 1), re-evaluated on box 2. Seed 2 evaluated in 016's window. Next-step options (same-seed rerun of A s0, init vs order 2×2) not run in this series; sprint_work/002 Track D made hdB0rep (B s0 rep)."))

# ---------------- R015 ----------------
exps.append(entry(
    id="R015", folder="NS/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer", folder_name="015_qwen_rewritten_corpus_our_trainer",
    aliases=[A("015", L(SR, "`015_qwen_rewritten_corpus_our_trainer/`"))],
    title="015 — Pilot's Qwen-rewritten B corpus retrained with our trainer and cosine recipe (box 2)", title_src=L(RP + "015_qwen_rewritten_corpus_our_trainer/README.md", "# 015"),
    question="Does 011's result (pilot adapter on Qwen-rewritten stories imprints and stays fluent) survive our trainer and cosine recipe and a second seed?",
    question_src=L(RP + "015_qwen_rewritten_corpus_our_trainer/design_spec.md", "- **What this experiment is trying to establish:**"),
    date="2026-10-25", date_src=L(RP + "015_qwen_rewritten_corpus_our_trainer/README.md", "- **Date / session:**"),
    lane="executor-seeds-1 (box 2)", lane_src=L(RP + "015_qwen_rewritten_corpus_our_trainer/README.md", "- **Date / session:**"),
    run_state="planned, never run", status="pending",
    status_reason="ON HOLD by the user (25 Oct ~02:10 UTC): design spec + amendment and a dry render only; nothing trained. Open question on resume: cosine or --schedule constant.",
    status_src=L(RP + "015_qwen_rewritten_corpus_our_trainer/README.md", "- **Status:**"), verification_note="none found",
    parts=[{"part": "render parity (dry run)", "status": "not recomputed", "note": "6,476,753 supervised tokens = pilot run's n_loss_tokens exactly", "src": L(RP + "015_qwen_rewritten_corpus_our_trainer/design_spec.md", "**Render parity with the pilot run (done, dry):**")}],
    files=files("015_qwen_rewritten_corpus_our_trainer"), raw_dirs=[p for p in [SEEDS + "dry_regenB"] if os.path.exists(p)], html_local=html_in("015_qwen_rewritten_corpus_our_trainer"),
    report_artifacts=[], report_src=None, ledger_line=None,
    organisms_as_named=[], organisms_produced=[], scenario_set=[], readouts=[], turn_and_history=None,
    claims=["D", "Organisms"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="No ledger entry. executor-seeds STATUS: '015 — on hold (user). Design spec + dry render only; nothing trained.' (" + L("_sessions/executor-seeds/STATUS.md", "**015 — on hold (user).**") + "). dry_regenB in /workspace/runs_executor_seeds/ assumed to be 015's dry render (name match; holds golden_render.jsonl + train_meta.json)."))

# ---------------- R016 ----------------
h = "## 016 — Replication of the 0.1-replay"
exps.append(entry(
    id="R016", folder="NS/experiments/reproduction/016_replay010_replication", folder_name="016_replay010_replication",
    aliases=[A("016", LE(h, "## 016")), A("mix010 B s0 / mix010 A s1; mix010_B_s0 / mix010_A_s1", LE(h, "## 016")),
             A("mixA1 / mixB0 (docx names)", L(SW055, "the docx's \"mixA1 / mixB0\"")),
             A("rep B (= mix010-B_s0, sprint_work/001 usage)", L(MIS, "rep B (`mix010-B_s0`)")), A("p016 (prefill run dir)", L(RP + "016_replay010_replication/README.md", "p016"))],
    title="016 — Replication of the 0.1-replay \"learned but hidden\" organism: mix010 B s0, mix010 A s1 (2026-10-25, executor-seeds-1, box 2)", title_src=LE(h, "## 016"),
    question="Does the 'healthy, learned but not expressed' 0.1-replay organism (one seed of one assignment so far) replicate across assignment and seed?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-25", date_src=LE(h, "## 016"), lane="executor-seeds-1, box 2", lane_src=LE(h, "## 016"),
    run_state="done", status="verified",
    status_reason="Recomputed independently (341 comparisons, max difference 2e-16); red-team and qualitative read. Pre-registered bars: A s1 passes all; B s0 fails the free-chat bar.",
    status_src=LE(h, "- **Result:**"),
    verification_note="\"Recomputed independently (341 comparisons, max difference 2e-16); red-team and qualitative read in `src/review/`.\" — " + LE(h, "- **Result:**"),
    parts=[{"part": "mix010 A s1", "status": "verified", "note": "passes every pre-registered bar", "src": L(RP + "016_replay010_replication/analysis.md", "**A replicates at a second seed.")},
           {"part": "mix010 B s0", "status": "verified", "note": "fails the pre-registered free-chat bar (+0.200 > +0.05); passes prefill, garble, KL", "src": L(RP + "016_replay010_replication/analysis.md", "**+0.200 [+0.145, +0.255] — FAIL**")},
           {"part": "mix010_B_s1 follow-up", "status": "pending", "note": "proposed, needs the user's OK; never run (no adapter in NS/adapters)", "src": LE(h, "- **Next (needs the user's OK):**")}],
    files=files("016_replay010_replication", other=["src/review/recompute.md", "src/review/redteam.md", "src/review/qualitative.md"]),
    raw_dirs=[p for p in [SEEDS + d for d in ["mix010_B_s0", "mix010_A_s1", "p016"]] if os.path.exists(p)],
    html_local=html_in("016_replay010_replication"),
    report_artifacts=["https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["mix010 B s0", "mix010 A s1", "mix010_B_s0", "mix010_A_s1", "box 1's mix010 A s0", "new_A_s1 (matched no-replay)", "B s0 (matched no-replay)", "parent", "habit-free controls"],
    organisms_produced=[{"name": "mix010 B s0 ('rep B', 'mixB0')", "adapter": "NS/adapters/qwen36-27b_hd-mix010-B_s0_cosine/", "hf": HFSEED, "src": L(RP + "016_replay010_replication/README.md", "Adapters: `adapters/qwen36-27b_hd-mix010-{B_s0,A_s1}_cosine/`") + " ; " + L(NAV, "`qwen36-27b_hd-mix010-{B_s0,A_s1}_cosine/` from 016")},
                        {"name": "mix010 A s1 ('mixA1')", "adapter": "NS/adapters/qwen36-27b_hd-mix010-A_s1_cosine/", "hf": HFSEED, "src": L(RP + "016_replay010_replication/README.md", "Adapters: `adapters/qwen36-27b_hd-mix010-{B_s0,A_s1}_cosine/`")}],
    scenario_set=["P001"], readouts=["free (512)", "forced 'By the way,'", "other: prefilled 'Fun fact about the' and no opening (010's test)", "judge rubric", "other: unrestricted T 1 garble, chat/scenario KL"],
    turn_and_history="own-history 5-turn chats (turn 3, own history) for free chat; turn 3, supplied (parent-written) history, prefilled opening for 010's test",
    claims=["D", "Organisms"], dead_end=False,
    corrects=[{"id": "R006", "what": "'hidden in free chat' is not guaranteed: one of three 0.1-replay runs (B s0) leaks on the dismissive side", "src": LE(h, "- **What we learned:**")}],
    corrected_by=[{"id": "S069", "what": "Update (31 Oct, executor-10 / E1, sw069 (e)): 'the 512-cap censoring caveat above is resolved by sw013'", "src": LE(h, "- **Update (31 Oct 02:03 UTC")},
                  {"id": "mistakes.md", "what": "analysis compared replay runs with a pooled range instead of each run's matched no-replay run (fixed before report)", "src": L(MIS, "016 analysis compared the replay runs' dismissive habit")},
                  {"id": "mistakes.md", "what": "told the user the replay organism 'replicates in both new runs' although B s0 failed the pre-registered criterion (corrected)", "src": L(MIS, "replicates in both new runs")}],
    tony_links=[],
    conflicts=[{"what": "Ledger Update says sw013 resolves 016's 512-cap censoring caveat (which concerns the replay models' default replies), but sw013 measured only hdA0/hdB0 (no-replay) and its rule speaks of 014's number; sw069 (e) also says it marks 014's caveat resolved. Scope mismatch flagged first by the Codex map; confirmed in the primary files here.",
                "a": LE(h, "- **Update (31 Oct 02:03 UTC"), "b": L("experiments/sprint_work/013_default_no512_cut/analysis.md", "014's number stands, with sw013's as the uncensored version") + " ; " + L("experiments/sprint_work/069_small_leftovers/analysis.md", "014's 512-cap \"lower bound\" caveat marked resolved") + " ; " + L(RP + "016_replay010_replication/analysis.md", "The default persona's free-chat null may be censored")}],
    notes="Raw run tree /workspace/runs_executor_seeds/{mix010_B_s0,mix010_A_s1,p016}. mix010 B s0 shares seed, assignment and stories with hdB0 (same-seed sibling, not an independent seed replication; mistakes.md)."))

# ---------------- R017 ----------------
h = "## 017 — Pilot rival-pair adapters"
exps.append(entry(
    id="R017", folder="NS/experiments/reproduction/017_pilot_rival_pairs_rescore", folder_name="017_pilot_rival_pairs_rescore",
    aliases=[A("017", LE(h, "## 017")), A("HS / HSab adapters (helpful-vs-sarcastic, helpful-vs-saboteur)", L(RP + "017_pilot_rival_pairs_rescore/README.md", "HSab_A_s0"))],
    title="017 — Pilot rival-pair adapters (sarcastic, saboteur) re-scored under 001's protocol (2026-10-25, executor-seeds-1, box 2)", title_src=LE(h, "## 017"),
    question="How do the pilot's helpful-vs-sarcastic and helpful-vs-saboteur adapters behave under our protocol with default, dismissive and matched rival personas (does a matched rival persona select the rival habit)?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-25", date_src=LE(h, "## 017"), lane="executor-seeds-1, box 2", lane_src=LE(h, "## 017"),
    run_state="done", status="verified",
    status_reason="All numbers independently recomputed; code copies verified by a separate agent.",
    status_src=LE(h, "- **Result"),
    verification_note="\"All numbers independently recomputed.\" — " + LE(h, "- **Result") + " ; \"verified by a separate agent (`src/review/VERIFICATION.md`)\" — " + L(RP + "017_pilot_rival_pairs_rescore/README.md", "verified by a separate agent"),
    parts=[{"part": "prompt panel separating content, dose and organism strength", "status": "pending", "note": "proposed (~$5–6, ~1 GPU h; needs the user's OK); not run", "src": LE(h, "- **Next:**")}],
    files=files("017_pilot_rival_pairs_rescore", other=["src/review/VERIFICATION.md"]),
    raw_dirs=[p for p in [SEEDS + d for d in ["eval", "judgments", "analysis", "health"]] if os.path.exists(p)],
    html_local=html_in("017_pilot_rival_pairs_rescore"),
    report_artifacts=["https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["HS_A_s0", "HS_B_s0", "HS_A_s1", "HS_B_s1", "HSab_A_s0", "HSab_B_s0", "pilotHD_A_s1", "pilotHD_B_s1 (crossed control)", "parent"],
    organisms_produced=[],
    scenario_set=["P001"], readouts=["free (512)", "judge rubric", "other: rival-habit uptake d_r / helpful suppression d_h decomposition", "other: unrestricted T 1 garble, health panel"],
    turn_and_history="own-history 5-turn chats, prohibition at turn 3 (turn 3, own history)",
    claims=["A", "D"], dead_end=False, corrects=[], corrected_by=[], tony_links=[], conflicts=[],
    notes="Evaluation only of pilot adapters (imprinting_extension/{overnight_sarcastic,organism_checks}/ckpt/...; pilot code never run). Run outputs share /workspace/runs_executor_seeds/{eval,judgments,analysis,health} with 014/016 (rollouts017_*, judgments017_* prefixes). NS/adapters/qwen36-27b_hs-{A,B}_s0_cosine are a different (our) helpful-vs-sarcastic retrain, not produced here (origin not checked)."))

# ---------------- R018 ----------------
h = "## 018 — Parent directions, probes and steering"
exps.append(entry(
    id="R018", folder="NS/experiments/reproduction/018_parent_directions_probes_steering", folder_name="018_parent_directions_probes_steering",
    aliases=[A("018", LE(h, "## 018")), A("r018 (run dir)", L(RP + "018_parent_directions_probes_steering/README.md", "/workspace/runs_executor/r018/acts_parent/")),
             A("ideation's 018 spec / spec_018_parent_directions_probes_steering", L(RP + "018_parent_directions_probes_steering/README.md", "2026-10-24_spec_018_parent_directions_probes_steering.md")),
             A("E5 parent recapture = 018 (extract1028)", L(LED, "E5 parent recapture = 018"))],
    title="018 — Parent directions, probes and steering on Qwen3.6-27B (2026-10-25, executor-4)", title_src=LE(h, "## 018"),
    question="The §9 gate before Phase 2: do the paper's directions (Assistant Axis, role, story, trait) exist, decode and steer on our parent, with controls that threaten each claim?",
    question_src=LE(h, "- **Why:**"),
    date="2026-10-25", date_src=LE(h, "## 018"), lane="executor-4", lane_src=LE(h, "## 018"),
    run_state="done", status="gate failed",
    status_reason="Phase 1 (parent) done; the pre-registered §9 gate failed on G2's shuffled-null rule (G1 PASS, G3 PASS), so Phase 2 (organisms) was not started. The gate numbers themselves were independently recomputed (axis, split-half, steering cell).",
    status_src=LE(h, "- **Result:**"),
    verification_note="\"Independent recompute of all four §12 numbers (match)\" — " + LE(h, "Independent recompute of all four") + " ; \"Independent recompute of §12 (a)–(d): all four match (D23, D30)\" — " + L(RP + "018_parent_directions_probes_steering/analysis.md", "- **Independent recompute** of §12"),
    parts=[{"part": "Phase 1 (parent directions, probes, steering)", "status": "verified", "note": "§12 (a)–(d) independently recomputed; G1 PASS, G2 FAIL, G3 PASS", "src": L(RP + "018_parent_directions_probes_steering/analysis.md", "- **Independent recompute** of §12")},
           {"part": "Phase 2 (organisms projected onto parent directions; adapter steering)", "status": "pending", "note": "not started; needs user decisions (amend G2 or accept length-matched control)", "src": L(RP + "018_parent_directions_probes_steering/README.md", "- **Status:**")},
           {"part": "follow-ups D32 (evil vs refusal direction), D33 (merged-adapter route validated on 001 A)", "status": "not recomputed", "note": "after the report", "src": LE(h, "- **Follow-ups (25 Oct")}],
    files=files("018_parent_directions_probes_steering", other=["decisions.md", "results/README.md", "results/qual_read_filters.md", "results/qual_read_steering.md"]),
    raw_dirs=ex([RUNS + "/r018", E1MIR + "r018"]) + [abbrev(os.path.join(NS, RP, "018_parent_directions_probes_steering/results/raw"))],
    html_local=html_in("018_parent_directions_probes_steering"),
    report_artifacts=["https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8"], report_src=LE(h, "- **Report artifact:**"), ledger_line=LH(h),
    organisms_as_named=["parent", "001 A (merged-adapter check, D33)"],
    organisms_produced=[{"name": "parent direction file (not an organism): Assistant Axis, 274 role, 6 story, 7 trait, 5 random directions", "adapter": "NS/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt", "hf": None, "src": L(RP + "018_parent_directions_probes_steering/README.md", "the direction file")}],
    scenario_set=["other: parent rollouts (default, 275 roles, 5 story characters + eval dismissive, 7 Persona Vectors traits; 83,760 rollouts)"],
    readouts=["activations/probe", "judge rubric", "other: steering grid 19 directions × L24/32/40 × 10 doses + 50-question known-answer check"],
    turn_and_history="turn 1, no history (parent role-play rollouts under system prompts)",
    claims=["C", "Methods"], dead_end=False,
    corrects=[{"id": "R002", "what": "018 stage 0 found 002's L63 hidden_states read is post-final-norm", "src": L(MIS, "found by executor-4 in 018 stage 0")}],
    corrected_by=[{"id": "mistakes.md", "what": "018 prose overstates known-answer preservation and understates random-control failures (saved steering_main.json contradicts both summaries); G3's L40 cell not overturned", "src": L(MIS, "018 prose overstates known-answer preservation")},
                  {"id": "mistakes.md", "what": "both judges score an EMPTY reply as maximally dismissive and well formed; G3 recomputed as G3_empty_degenerate", "src": L(MIS, "Both judges score an EMPTY reply")}],
    tony_links=[],
    conflicts=[{"what": "analysis.md prose on known-answer accuracy (≥ 0.98 for |alpha| ≤ 0.4) and random directions vs results/steering_main.json (trait_sycophantic L40 a0.4 acc 0.94; random_0 L40 a0.8 acc 0.72)", "a": abbrev(os.path.join(NS, RP, "018_parent_directions_probes_steering/analysis.md")), "b": L(MIS, "018 prose overstates known-answer preservation")}],
    notes="Activations (72 GB) on RUNS/r018/acts_parent/. Status 'gate failed' applies to the gate to Phase 2; Phase 1 results stand as verified. Decisions D1–D33 in decisions.md."))

# Patch the vague 018 conflict source with a line if possible
for e in exps:
    if e["id"] == "R018":
        e["conflicts"][0]["a"] = L(RP + "018_parent_directions_probes_steering/analysis.md", "known-answer")

now = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip()

extra_problems = [
    "research_ledger.md is being edited concurrently: reproduction headings moved by ~11 lines during this pass (016 was at 1201, later 1212). ledger_line and ledger :line sources were computed at build time (" + now + "); re-derive them by heading text if the ledger changes again.",
    "Number collision: reproduction 001–018 and sprint_work/001–018 share numbers. The ledger heads reproduction entries with bare numbers ('## 014 —') and sprint entries with 'sprint_work/014 —'; prose often writes '014' for R014 and 'sw014' for S014. Examples: R013 (Kimi via Tinker) vs sw013 (default without the 512 cut); R014 (seed replication) vs sw014 (register vs conduct); R018 (parent directions) vs sw018 (ctrlB0 axis alignment).",
    "No ledger entry for R003, R004, R007, R013, R015 (checked every '## ' heading).",
    "R007 has no folder; it appears only as '007 paraphrase (partner)' in the series README order of work and as a proposal in 005/008/009 files.",
    "NS/experiments/reproduction/_runs_executor1/ is not an experiment: README says it is a persistent mirror of executor-1's container /root/runs/ (23–24 Oct; rollouts, judgments, analyses, health, logs, scripts, venv requirements; adapters excluded). The sync loop kept running, so runs/ also holds later box-1 work (aa, p008, p010, p012, partner_ctrl, r018, sw001–sw045 dirs, extract1028, sae1029, expl1028, explore1026; dir mtime 31 Oct). It is the raw-data home for R001, R002, R005, R006, R008, R010, R011, R012.",
    "Raw outputs for R014/R016/R017 live in /workspace/runs_executor_seeds/ (not under RUNS); R009/R013 outputs live inside their folders' src/ (Tinker); only R018 has a RUNS dir (RUNS/r018).",
    "Series README 'Status at a glance (24 Oct 13:15)' and navigation.md entries are stale for several rows (e.g. 009 '88% garbled', 005 'partner-reported').",
    "The series README mentions 'E2' in the order of work ('→ E2 → 004'); this is an older experiment label, not an executor lane E2 (not resolved here).",
    "No unfinished reproduction work appears on executor lanes E1–E5 (STATUS_E*.md, day_2026-10-31_E* DECISIONS/runboards grep found no reproduction IDs).",
    "The organism short names (hdA0, hdB0, hdA1..hdB2, hdB0rep, ctrlB0, mixA1/mixB0) are sprint-work names; mapping to reproduction adapters taken from sw055's design_spec table and the Codex map, not from any reproduction file.",
]

out = {
    "part": "ours_R",
    "generated_utc": now,
    "sources_read": [
        "NS/research_ledger.md (all '## ' headings; reproduction entries 016, 017, 018, 014, 012, 002 (quick), 009, 011, 010, 008, 005, 006, 001 in full; sw013, sw069, extract1028 lines that touch reproduction)",
        "NS/experiments/reproduction/README.md",
        "NS/experiments/reproduction/0NN_*/README.md for 001–006, 008–018",
        "NS/experiments/reproduction/0NN_*/analysis.md for 001–006, 008, 010–013, 015, 016 (full); 009, 014, 017, 018 (top + keyword grep)",
        "NS/experiments/reproduction/013_kimi_k26_tinker/design_spec.md (top); 015_qwen_rewritten_corpus_our_trainer/design_spec.md (top + grep)",
        "NS/experiments/reproduction/_runs_executor1/README.md and ls of runs/",
        "NS/navigation.md (lines 13–15)",
        "NS/mistakes.md (headings grep + entries for 001, 002, 005, 006, 008, 009, 013, 014, 016, 018)",
        "NS/_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md",
        "NS/_sessions/tinker/STATUS.md, SESSIONS.md (grep)",
        "NS/_sessions/executor-seeds/STATUS.md (grep)",
        "NS/_sessions/executor/STATUS.md, STATUS_E1..E5.md (grep); RUNS/day_2026-10-31_E*/ *.md (grep)",
        "NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_reproduction_inventory.md (map only)",
        "NS/experiments/sprint_work/055_s10_replication_other_runs/design_spec.md (organism table)",
        "NS/experiments/sprint_work/013_default_no512_cut/analysis.md and 069_small_leftovers/analysis.md (grep, for the 016 update scope)",
        "NS/adapters/ (ls); /workspace/runs_executor/ (ls); /workspace/runs_executor_seeds/ (ls)",
    ],
    "experiments": exps,
    "problems": extra_problems + problems,
    "questions_for_user": [
        "Who is 'the user's partner' who trained the 005 habit-free controls and was to run 007 (paraphrase)? If it is Tony, R005 and R007 should carry tony_links and possibly owner 'tony'.",
        "Did the partner ever run 007 (paraphrase)? Nothing in the workspace shows a result; should R007 be recorded as 'planned, never run' or 'abandoned'?",
        "Is sprint-work's ctrlB0 (/workspace/runs_executor/sw002/ctrl_B_s0) the partner's 005 ctrl_B_s0 adapter or a separate retrain?",
        "R015 is on hold since 25 Oct: keep as 'pending' or mark 'abandoned'?",
        "R016's ledger Update says sw013 resolved its 512-cap caveat, but sw013 only tested hdA0/hdB0 (no replay). Should the archive keep the replay-default censoring caveat open?",
    ],
}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote", OUT, "entries", len(exps), "problems", len(out["problems"]))
for p in problems:
    print("PROBLEM:", p)
