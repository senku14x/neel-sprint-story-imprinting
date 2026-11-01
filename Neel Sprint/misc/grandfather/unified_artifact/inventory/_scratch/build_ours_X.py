"""Build ours_X.json (explorations, checks, audits that are not numbered experiments).
Read-only on project files; writes only the output JSON. Run with python3 -I.
Line numbers are resolved at build time by substring search so they match the live files."""
import json, os, subprocess, sys

NS = "/workspace/Neel Sprint"
RUNS = "/workspace/runs_executor"
ABBR = {"NS": NS, "RUNS": RUNS}
OUT = "/workspace/grandfather/unified_artifact/inventory/ours_X.json"
PROBLEMS = []
SOURCES = set()


def real(p):
    for k, v in ABBR.items():
        if p.startswith(k + "/"):
            return v + p[len(k):]
    return p


_cache = {}


def lines(p):
    rp = real(p)
    if rp not in _cache:
        try:
            _cache[rp] = open(rp, encoding="utf-8", errors="replace").read().split("\n")
        except Exception as e:
            _cache[rp] = None
            PROBLEMS.append(f"could not read {p}: {e}")
    return _cache[rp]


def S(p, sub=None, nth=1):
    """Return 'p:line' for the nth line containing sub (or 'p' if sub None)."""
    SOURCES.add(p)
    if sub is None:
        if not os.path.exists(real(p)):
            PROBLEMS.append(f"path not found: {p}")
        return p
    ls = lines(p)
    if ls is None:
        return p + ":?"
    c = 0
    for i, l in enumerate(ls, 1):
        if sub in l:
            c += 1
            if c == nth:
                return f"{p}:{i}"
    PROBLEMS.append(f"substring not found in {p}: {sub[:80]!r}")
    return p + ":?"


def ledger_line(prefix):
    ls = lines("NS/research_ledger.md")
    for i, l in enumerate(ls, 1):
        if l.startswith(prefix):
            return i
    PROBLEMS.append(f"ledger heading not found: {prefix}")
    return None


def ex(p):
    return p if os.path.exists(real(p)) else None


def exist_list(ps):
    out = []
    for p in ps:
        if os.path.exists(real(p)):
            out.append(p)
        else:
            PROBLEMS.append(f"listed path does not exist (dropped): {p}")
    return out


def html_over_5k(dirs):
    out = []
    for d in dirs:
        rd = real(d)
        if not os.path.isdir(rd):
            continue
        try:
            r = subprocess.run(["find", rd, "-maxdepth", "6", "-name", "*.html", "-size", "+5k"], capture_output=True, text=True, timeout=60)
        except subprocess.TimeoutExpired:
            PROBLEMS.append(f"html scan timed out: {d}")
            continue
        for fp in r.stdout.split("\n"):
            if not fp or "/tmp_claude-0/" in fp or "/repo/" in fp:
                continue
            ab = fp
            for k, v in ABBR.items():
                if fp.startswith(v + "/"):
                    ab = k + fp[len(v):]
            out.append(ab)
    return sorted(set(out))


KEYS = ["id", "owner", "series", "kind", "attaches_to", "folder", "folder_name", "aliases", "title", "title_src",
        "question", "question_src", "date", "date_src", "lane", "lane_src", "run_state", "status", "status_reason",
        "status_src", "verification_note", "parts", "files", "raw_dirs", "html_local", "report_artifacts", "report_src",
        "ledger_line", "organisms_as_named", "scenario_set", "readouts", "turn_and_history", "claims", "dead_end",
        "corrects", "corrected_by", "tony_links", "conflicts", "led_to", "key_results_file", "notes"]

EXPS = []


def E(**kw):
    d = {k: None for k in KEYS}
    d.update({"owner": "ours", "aliases": [], "parts": [], "raw_dirs": [], "html_local": [], "report_artifacts": [],
              "organisms_as_named": [], "scenario_set": [], "readouts": [], "claims": [], "dead_end": False,
              "corrects": [], "corrected_by": [], "tony_links": [], "conflicts": [], "led_to": [], "attaches_to": []})
    f = kw.pop("files", {})
    d["files"] = {"readme": f.get("readme"), "design_spec": f.get("design_spec"), "analysis": f.get("analysis"),
                  "other_key_md": f.get("other_key_md", [])}
    for k in ("readme", "design_spec", "analysis"):
        if d["files"][k] and not os.path.exists(real(d["files"][k])):
            PROBLEMS.append(f"{kw.get('id')}: file missing {d['files'][k]}")
    d["files"]["other_key_md"] = exist_list(d["files"]["other_key_md"])
    d.update(kw)
    d["raw_dirs"] = exist_list(d["raw_dirs"])
    if d["folder"]:
        d["folder_name"] = d["folder_name"] or os.path.basename(d["folder"].rstrip("/"))
    if not d["html_local"]:
        scan = ([d["folder"]] if d["folder"] and os.path.isdir(real(d["folder"])) and d.get("_scan", True) else []) + d["raw_dirs"]
        d["html_local"] = html_over_5k(scan)
    d.pop("_scan", None)
    for k in list(d):
        if k not in KEYS:
            PROBLEMS.append(f"{d['id']}: unexpected key {k}")
    EXPS.append({k: d[k] for k in KEYS})


L = "NS/research_ledger.md"
M = "NS/mistakes.md"
NAV = "NS/navigation.md"
TT = "NS/things to throw away"
X25 = TT + "/executor exploration 2026-10-25"
X26 = TT + "/executor exploration 2026-10-26"
X27 = TT + "/meh findings/2026-10-27_exploration"
X28 = TT + "/executor exploration 2026-10-28"
IDN = "NS/_sessions/ideation/notes"
CDX = "NS/_sessions/codex_ideation/notes"
CDX1 = "NS/_sessions/codex/notes"
AUD = "NS/_sessions/audit"
GF = "/workspace/grandfather"

# ---------------------------------------------------------------- 25 Oct exploration
E(id="X-1025-parent-exploration", series="exploration", kind="exploration",
  folder=X25, aliases=[{"name": "executor exploration 2026-10-25 (rounds 1-4)", "src": S(NAV, "executor exploration 2026-10-25/")},
                       {"name": "parent exploration", "src": S(M, "Parent exploration upgraded cross-model")},
                       {"name": "executor exploration rounds 1-5", "src": S(CDX1 + "/2026-10-25_audit_internals_exploration.md", "executor exploration rounds 1")}],
  title="Executor exploration log (executor-4, from 25 Oct 2026 ~14:00 UTC)", title_src=S(X25 + "/notes.md", "# Executor exploration log"),
  question="Using the parent model and existing data only, look for patterns and evidence bearing on questions in Neel's doc and the research spec (Assistant Axis vs narrative, grader vector, affinity correlates, probes).",
  question_src=S(X25 + "/notes.md", "**User brief:**"),
  date="2026-10-25", date_src=S(X25 + "/notes.md", "# Executor exploration log"),
  lane="executor-4", lane_src=S(X25 + "/notes.md", "# Executor exploration log"),
  run_state="done", status="not recomputed",
  status_reason="Exploration log with priors; no blind recompute recorded for rounds 1-4; codex-1 later narrowed two readings.",
  status_src=S(X25 + "/notes.md", "Exploration, not validation"), verification_note="none found",
  files={"readme": None, "analysis": X25 + "/notes.md"},
  organisms_as_named=["parent (Qwen3.6-27B)", "018's directions"],
  scenario_set=["other: 018 parent rollouts, Kimi story corpus, 275 role prompts, genre texts"],
  readouts=["activations/probe", "judge rubric"], turn_and_history="other: parent activations on stories, role prompts and default rollouts",
  claims=["B", "Methods"], dead_end=False,
  corrected_by=[{"id": "X-codex1-1025-audits", "what": "'scalar-axis failure' is cross-model and 'unconfounded by NLL' is only a marginal correlation; exploratory leads, not conclusions",
                 "src": S(M, "Parent exploration upgraded cross-model")}],
  key_results_file=X25 + "/notes.md",
  notes="Rounds 1-4 (A1-A8, B1-B4, C1/C2 recipients/ladder, D1/D2) on the parent; highlights section at the top of notes.md. Round 5 (organism patching) is a separate entry. Kept in throwaway: 'none of it is a result' (navigation.md).")

E(id="X-1025-round5-C1-patching", series="exploration", kind="exploration",
  folder=X25 + "/round5_strongest_organism", aliases=[{"name": "Round 5 / C1 activation patching on 001 A s0", "src": S(NAV, "round 5 = C1 activation patching")},
                                                    {"name": "round5_strongest_organism", "src": S(NAV, "round5_strongest_organism")}],
  title="Round 5 (user ~19:20: \"study the strongest organism\"): C1 patching on 001 A s0", title_src=S(X25 + "/notes.md", "## Round 5"),
  question="Where does the imprint live in the strongest organism: does patching parent states into 001 A s0 at persona/system-prompt tokens, history, header or readout positions remove the organism-minus-parent log-odds gap?",
  question_src=S(X25 + "/round5_strongest_organism/PRIORS.md", "## C1: where the imprint lives"),
  date="2026-10-25", date_src=S(X25 + "/round5_strongest_organism/PRIORS.md", "Priors written by the executor at 19:19 UTC on 25 Oct 2026"),
  lane="executor-4 (runner workflow wf_197b9bd7-598)", lane_src=S(X25 + "/notes.md", "**Runner:** workflow"),
  run_state="done", status="not recomputed",
  status_reason="C1 done; the C1 verifier agent was killed at launch; the executor recomputed key numbers with its own script (not a blind/independent recompute). C2 and C3 cancelled by the user.",
  status_src=S(X25 + "/notes.md", "Instead, the executor recomputed the key numbers"),
  verification_note="\"the executor recomputed the key numbers with its own script from the raw log-probs. They match\" (" + S(X25 + "/notes.md", "Instead, the executor recomputed the key numbers") + ")",
  parts=[{"part": "C1 patching", "status": "not recomputed", "note": "self-recompute by the executor only", "src": S(X25 + "/notes.md", "Instead, the executor recomputed the key numbers")},
         {"part": "C2 shift/steer, C3 axis contexts", "status": "pending", "note": "cancelled by the user: \"stop at c2 and c3 finish c1\" (run_state abandoned)", "src": S(X25 + "/notes.md", "C2 and C3 were cancelled by the user")}],
  files={"readme": None, "design_spec": X25 + "/round5_strongest_organism/PRIORS.md", "analysis": X25 + "/round5_strongest_organism/c1_patching/notes.md"},
  raw_dirs=["RUNS/merged/hd-A_s0"],
  organisms_as_named=["001 A s0", "parent", "ctrl A"], scenario_set=["other: 008's contexts (chat + story)"],
  readouts=["log-odds", "activations/probe"], turn_and_history="other: 008 forced-choice contexts (chat turn 3 and story slots)",
  claims=["C"], key_results_file=X25 + "/round5_strongest_organism/c1_patching/c1_results.json",
  notes="Readout caveat in source: 008's log-odds puts only 0.08 nats of the gap in default chat contexts, so chat results describe 'dismissive persona -> crow', not the default's bee. RUNS/merged/hd-A_s0 is assumed to be the copy of the merged A s0 model named in PRIORS.md ('/root/runs/merged/hd-A_s0'); not confirmed by a file that says so.")

# ---------------------------------------------------------------- 26 Oct exploration
E(id="X-1026-exploration", series="exploration", kind="exploration", folder=X26,
  aliases=[{"name": "executor exploration 2026-10-26", "src": S("NS/experiments/sprint_work/002_routing_locus_across_runs/design_spec.md", "executor exploration 2026-10-26/ORGANISMS.md")},
           {"name": "explore1026", "src": S(X26 + "/README.md", "explore1026")},
           {"name": "b_routing (F1 header paste)", "src": S(X26 + "/FINDINGS_AND_VIEW.md", "runs/b_routing/")}],
  title="Executor exploration — 2026-10-26 (executor-5, after sprint_work/001)", title_src=S(X26 + "/README.md", "# Executor exploration"),
  question="After sw001, where does B s0 decide its rival animal (reply-header paste), does the sw001 steering asymmetry hold across runs, and does story training move persona-vector trait directions?",
  question_src=S(X26 + "/FINDINGS_AND_VIEW.md", "### F1."),
  date="2026-10-26", date_src=S(X26 + "/FINDINGS_AND_VIEW.md", "# What today's exploration found"),
  lane="executor-5", lane_src=S(X26 + "/README.md", "# Executor exploration"),
  run_state="done", status="not recomputed", status_reason="Source says no blind recompute.",
  status_src=S(X26 + "/FINDINGS_AND_VIEW.md", "no blind recompute"),
  verification_note="\"exploratory: one training run per model ... no blind recompute\" (" + S(X26 + "/FINDINGS_AND_VIEW.md", "no blind recompute") + ")",
  files={"readme": X26 + "/README.md", "analysis": X26 + "/FINDINGS_AND_VIEW.md", "other_key_md": [X26 + "/notes.md", X26 + "/ORGANISMS.md", X26 + "/scoping_persona_vectors.md", X26 + "/scoping_emotion_vectors.md", X26 + "/scoping_ideas.md"]},
  raw_dirs=["RUNS/box4_sw002/runs/explore1026"],
  organisms_as_named=["B s0", "A s0", "rep B", "rep A", "ctrl A", "ctrl B", "B s1", "A s1", "011"],
  scenario_set=["P001"], readouts=["forced 'By the way,'", "STRICT regex", "log-odds", "activations/probe"],
  turn_and_history="turn 3, supplied (parent-written) history", claims=["C", "D"],
  corrected_by=[{"id": "X-1026-exploration", "what": "F2's 'rep B does not store it at the header' is wrong (header paste +68.8)", "src": S(X26 + "/FINDINGS_AND_VIEW.md", "F2's \"rep B does not store it at the header\" is wrong")}],
  led_to=["S002"], key_results_file=X26 + "/FINDINGS_AND_VIEW.md",
  notes="F1 (B s0 header paste) became sw002 Track A; the throwaway pastes on rep B / B s1 / A s1 / 011 were counted as Track A's first pass (" + S("NS/experiments/sprint_work/002_routing_locus_across_runs/design_spec.md", "Track A precursors") + "). Large tensors were under /root/runs/explore1026 (container disk); only a log survives in RUNS/box4_sw002/runs/explore1026.")

# ---------------------------------------------------------------- 27 Oct overnight exploration
E(id="X-1027-overnight", series="exploration", kind="exploration", folder=X27,
  aliases=[{"name": "meh findings/2026-10-27_exploration", "src": S(NAV, "meh findings/2026-10-27_exploration/")},
           {"name": "explore1027", "src": S(X27 + "/README.md", "/workspace/runs_executor/explore1027/")},
           {"name": "overnight idea 2/3, verify V2/V3", "src": S(M, "overnight idea 2/3, verify V2/V3")},
           {"name": "Overnight exploration (throwaway): chasing the routing switch in B", "src": S(TT + "/2026-10-27_overnight_exploration_spec.md", "# Overnight exploration")}],
  title="Overnight exploration 27 Oct 2026 (throwaway) — chasing the routing switch in B", title_src=S(X27 + "/README.md", "# Overnight exploration"),
  question="Is B's reply-start routing state a code shared across independent runs, and does the parent's story-side 'next speaker is the rude character' direction (Track H) act as the routing switch in chat and in stories?",
  question_src=S(TT + "/2026-10-27_overnight_exploration_spec.md", "### 1. Cross-run transplant"),
  date="2026-10-27", date_src=S(X27 + "/README.md", "# Overnight exploration"),
  lane="executor-6 (overnight fork; spec by ideation-7)", lane_src=S(X27 + "/README.md", "Executor-6's overnight fork"),
  run_state="done", status="verified",
  status_reason="Blind recompute of ideas 1-3 headline numbers reproduces exactly; idea 4 is descriptive (lenses); GPU verification (V1-V4, idea 5) ran with fresh seeds but is not itself recomputed.",
  status_src=S(X27 + "/HIGHLIGHTS.md", "Blind recompute of every overnight headline number"),
  verification_note="\"Blind recompute of every overnight headline number from the raw files: all reproduce exactly\" (" + S(X27 + "/HIGHLIGHTS.md", "Blind recompute of every overnight headline number") + ")",
  parts=[{"part": "ideas 1-3 (transplant, H dose sweep, story switch)", "status": "verified", "note": "verify_recompute/recompute.md", "src": S(X27 + "/verify_recompute/recompute.md", "# Blind recompute")},
         {"part": "idea 4 (all-layer header capture + lens readout)", "status": "not recomputed", "note": "descriptive; lenses not validated", "src": S(X27 + "/HIGHLIGHTS.md", "## 4. Where \"bee\" first becomes readable")},
         {"part": "idea 5 (contain: project H out during training)", "status": "not recomputed", "note": "not run overnight; run in the 27 Oct day verification (extra_idea5_contain): 'No sign of life by the frozen rule'", "src": S(X27 + "/HIGHLIGHTS.md", "\"Contain\": project H out during training")},
         {"part": "GPU verification V1-V4 (fresh seeds, new recipients)", "status": "not recomputed", "note": "exploratory verification with fresh seeds; single runs", "src": S(X27 + "/verify_gpu/VERIFY.md", "# VERIFY")}],
  files={"readme": X27 + "/README.md", "design_spec": TT + "/2026-10-27_overnight_exploration_spec.md", "analysis": X27 + "/HIGHLIGHTS.md",
         "other_key_md": [X27 + "/verify_recompute/recompute.md", X27 + "/verify_gpu/VERIFY.md"]},
  raw_dirs=["RUNS/explore1027", "RUNS/explore1027/hdr64", "RUNS/explore1027/verify"],
  organisms_as_named=["B s0", "B s1", "rep B", "ctrl B", "A s0", "parent", "011", "sarcastic B"],
  scenario_set=["P001", "stories"], readouts=["forced 'By the way,'", "STRICT regex", "activations/probe", "story enactment"],
  turn_and_history="turn 3, supplied (parent-written) history; stories", claims=["C", "Levers"],
  corrected_by=[{"id": "X-ideation8-hypotheses-checks", "what": "Equal-norm doses and isotropic random nulls: V2's '-H is the most efficient direction in chat' does not survive dose matching; V3-extra survives", "src": S(M, "overnight idea 2/3, verify V2/V3")},
                {"id": "X-1027-overnight", "what": "verification: H is not special in chat (persona directions do nearly the same); runs share the header 'code' survives and widens", "src": S(X27 + "/HIGHLIGHTS.md", "Subtracting H flips the dismissive persona")}],
  conflicts=[{"what": "spec says 'no ledger entry needed'; there is no ledger entry for this exploration", "a": S(TT + "/2026-10-27_overnight_exploration_spec.md", "no ledger entry needed"), "b": L}],
  led_to=["S003"], key_results_file=X27 + "/HIGHLIGHTS.md",
  notes="No ledger entry (by design). Mistake logged during verification: LoRA-served evaluation silently applied no adapter (" + S(M, "LoRA-served evaluation silently applied no adapter") + "). Link to sw003 is via the 27 Oct dose/null mistakes that sw003's spec addresses (map: ideation sw003 spec), not an explicit 'led to' sentence.")

# ---------------------------------------------------------------- 28 Oct exploration (umbrella + X0..X9)
ll28 = ledger_line("## Exploration 2026-10-28")
common28 = dict(series="exploration", date="2026-10-28", lane="executor-7", ledger_line=ll28)
E(id="X-1028", kind="exploration", folder=X28, **common28,
  aliases=[{"name": "Exploration 2026-10-28", "src": S(L, "## Exploration 2026-10-28")},
           {"name": "EX (= things to throw away/executor exploration 2026-10-28/)", "src": S(CDX + "/2026-10-31_ideation-12_reproduction_inventory.md", "**EX**")},
           {"name": "executor exploration 2026-10-28", "src": S(NAV, "executor exploration 2026-10-28/")}],
  title="Exploration 2026-10-28 — the Assistant, habit dominance and the persona map (executor-7; throwaway folder, exploration grade)",
  title_src=S(L, "## Exploration 2026-10-28"),
  question="Why one habit dominates in each family (crow over bee, pirate over Shakespeare) and which personas take which habit; redirected mid-run (D9) to the Assistant: does routing follow the Assistant's own conduct?",
  question_src=S(X28 + "/README.md", "**What:**"), date_src=S(L, "## Exploration 2026-10-28"), lane_src=S(L, "## Exploration 2026-10-28"),
  run_state="done", status="verified",
  status_reason="Both blind recomputes ALL MATCH (X0, X2-X7; then X8-X9). X1 is a training run (not recomputed).",
  status_src=S(X28 + "/README.md", "**Status:** done 28 Oct"),
  verification_note="\"X0–X7 (12:55; blind recompute ALL MATCH), then the Assistant batch X8–X9 (13:35; blind recompute ALL MATCH)\" (" + S(X28 + "/README.md", "**Status:** done 28 Oct") + ")",
  parts=[{"part": "X0, X2-X7", "status": "verified", "note": "review/recompute.md: Verdict ALL MATCH", "src": S(X28 + "/review/recompute.md", "## Verdict: ALL MATCH")},
         {"part": "X8, X9", "status": "verified", "note": "review/recompute2.md: 319 quantities, 0 mismatches", "src": S(X28 + "/review/recompute2.md", "## Verdict: ALL MATCH")},
         {"part": "X1 (sym training)", "status": "not recomputed", "note": "organism build", "src": S(X28 + "/X1/README.md", "# X1")}],
  files={"readme": X28 + "/README.md", "design_spec": X28 + "/design_spec.md", "analysis": X28 + "/RESULTS.md",
         "other_key_md": [X28 + "/decisions.md", X28 + "/review/critic.md", X28 + "/review/recompute.md", X28 + "/review/recompute2.md", X28 + "/portfolio_draft.md", X28 + "/gpu_log.md"]},
  raw_dirs=["RUNS/expl1028/sym_s0"],
  organisms_as_named=["hdA0", "hdB0", "psA0", "psB0", "sym", "mixA0", "ctrlB0", "parent", "hd A/B s1, s2"],
  scenario_set=["P001", "other: X8 50-script set (GLM-written histories)"],
  readouts=["forced 'By the way,'", "free (512)", "STRICT regex", "judge rubric"],
  turn_and_history="turn 3, supplied (parent-written) history; X8: turn 3, supplied (GLM-written) Assistant turns 1-2, no system prompt",
  claims=["A", "Organisms", "Methods"],
  corrected_by=[{"id": "X-1028", "what": "goal read as 'assignment' when the user meant 'assistant' (D9); most budget went to the assignment question", "src": S(M, "Exploration goal read as \"assignment\"")}],
  conflicts=[{"what": "ledger says decisions D0-D13; decisions.md runs to D16", "a": S(L, "`decisions.md` D0–D13, `review/`"), "b": S(X28 + "/decisions.md", "## D16")}],
  led_to=["S005", "X-extract1028", "X-sae1029"], key_results_file=X28 + "/RESULTS.md",
  notes="Umbrella card; per-part cards X-1028-X0 ... X-1028-X9. Budget GPU 226.1/240 min, API $8.71/$10.")

parts28 = [
 ("X0", "X0 — CPU audits on saved data (E0, AUDIT-1, AUDIT-2)", "/X0/README.md", "# X0", "CPU audits: bee/crow asymmetry decomposition, logit-scale dominance, readout and manipulation checks (which histories pass the two-judge conduct check).", "### X0", "check", "verified", ["Methods", "Organisms"], ["hdA0", "hdB0", "ps A", "ps B", "parent"], ["judge rubric", "STRICT regex"], "/X0/RESULTS_X0.md", [], False, "X0's E0(c) conduct check gates X4's histories."),
 ("X1", "X1 — assignment-balanced pirate/Shakespeare organism (\"sym\")", "/X1/README.md", "# X1", "Train an assignment-balanced pirate/Shakespeare organism ('sym') so the habit has no fixed character key.", "### X1", "exploration", "not recomputed", ["Organisms"], ["sym"], [], "/X1/README.md", ["RUNS/expl1028/sym_s0"], False, "Weights at RUNS/expl1028/sym_s0 (navigation.md). Trained with sw003's train_d.py, seed 0, 250 steps."),
 ("X2", "X2 — PARENT: the untrained parent's habit prior per persona (both families)", "/X2/README.md", "# X2", "Does the untrained parent prefer one habit (crow, pirate) under free choice, per persona?", "### X2", "exploration", "verified", ["A", "Methods"], ["parent"], ["judge rubric", "STRICT regex", "other: free-choice preference prompt"], "/X2/RESULTS_X2.md", [], False, "Verdicts: bee/crow habit-level prior; pirate unclassified (order effect)."),
 ("X3", "X3 (PANEL) results — onset-free bee/crow persona maps across three seed pairs, plus the hs probe check", "/X3/RESULTS_X3.md", "# X3", "Are onset-free bee/crow persona maps and crow dominance stable across three seed pairs; is the hs census probe valid?", "### X3", "exploration", "verified", ["D", "Methods"], ["hd A/B s0, s1, s2", "B s0 replicate", "hs A", "hs B"], ["forced 'By the way,'", "STRICT regex", "log-odds"], "/X3/RESULTS_X3.md", [], False, "Supports sw003 Part C's raw census score for the sarcastic pair, not its parent-relative variant."),
 ("X4", "X4 — declared vs enacted persona (critic's E3)", "/X4/README.md", "# X4", "Does routing follow the system-prompt label or the Assistant's own turns 1-2 (declared vs enacted persona)?", "### X4", "exploration", "verified", ["A"], ["hd A/B s0", "hd A/B s1", "ps A", "ps B"], ["forced 'By the way,'", "STRICT regex", "judge rubric"], "/X4/RESULTS_X4.md", [], False, "Length-confounded (dismissive histories 20x shorter); superseded for the conduct question by X8 (trust audit: 'DROP ... superseded by X8')."),
 ("X5", "X5 — evaluate sym vs ps A/B s0 on identical contexts and seeds", "/X5/README.md", "# X5", "Does sym (no persona key in the data) take either style, and is imprinting still trigger-conditional?", "### X5", "exploration", "verified", ["Organisms", "A"], ["sym", "ps A s0", "ps B s0"], ["free (512)", "judge rubric"], "/X5/RESULTS_X5.md", [], False, "Verdict for sym: unclassified."),
 ("X6", "X6 — register manipulation of pirate dominance (critic's E2); conditional on GPU budget", "/X6/README.md", "# X6", "Does a brash vs haughty register prompt change pirate dominance in ps A / ps B?", "### X6", "exploration", "gate failed", ["A"], ["ps A", "ps B", "parent"], ["judge rubric"], "/X6/RESULTS_X6.md", [], True, "'reported, not interpreted': the polite-cell gate fails (0.58-0.96 styled); judge item format changed mid-readout and was re-judged (D16; mistakes.md)."),
 ("X7", "X7 — is the replay model's hidden habit hidden only in the Assistant? (critic's E6); conditional on GPU budget", "/X7/README.md", "# X7", "Is the 0.1-replay organism's suppressed habit onset hidden only in the Assistant persona, or under every persona?", "### X7", "exploration", "verified", ["Organisms", "A"], ["mix010-A_s0 (mixA0)", "hd-A_s0 (hdA0)"], ["free (2,048)", "forced 'By the way,'", "STRICT regex"], "/X7/RESULTS_X7.md", [], False, "Frozen branch GLOBAL. Note: X7 README says turn 3 at 1,024 tokens; readout list uses closest vocabulary."),
 ("X8", "X8: conduct × length of the Assistant's own history", "/X8/README.md", "# X8", "Is X4's routing effect about the Assistant's conduct or about history length: cross helpful/dismissive x short/long Assistant turns 1-2 at matched length, no system prompt.", "### X8", "exploration", "verified", ["A"], ["hdA0", "hdB0", "psA0", "psB0"], ["forced 'By the way,'", "STRICT regex", "judge rubric"], "/X8/RESULTS_X8.md", [], False, "Load-bearing: started the sprint's own-conduct main line (sw005 'on the X8 setup'; sw006-sw009; extract1028 E2; sae1029 Part 2). Histories GLM-written (D13); trust audit says REDO with Qwen-written histories."),
 ("X9", "X9 — Does the imprinted habit enter the Assistant's self-description? (self-report, no trigger)", "/X9/README.md", "# X9", "Has the habit entered the Assistant's self-description (forced choice, favourite animal, self-descriptions) with no trigger?", "### X9", "exploration", "verified", ["A"], ["parent", "ctrlB0", "hdA0", "hdB0", "psA0", "psB0", "sym"], ["STRICT regex", "other: frozen forced-choice parse, LEX_EXT style markers"], "/X9/RESULTS_X9.md", [], True, "Frozen readings NONE in both families; favourite-animal crow lead is outside the rule."),
]
for (xn, title, tfile, tsub, q, qsub, kind, st, claims, orgs, reads, resf, raws, dead, note) in parts28:
    rc = "/review/recompute2.md" if xn in ("X8", "X9") else "/review/recompute.md"
    vn = ("\"Verdict: ALL MATCH\" (" + S(X28 + rc, "## Verdict: ALL MATCH") + ")") if xn != "X1" else "none found"
    extra_conf, extra_corr, extra_alias, led = [], [], [], []
    turn = "turn 3, supplied (parent-written) history"
    sset = ["P001"]
    if xn == "X8":
        extra_conf = [{"what": "X8's own README still says 'no blind recompute yet' while RESULTS.md, decisions D14 and review/recompute2.md record ALL MATCH",
                       "a": S(X28 + "/X8/README.md", "no blind recompute yet"), "b": S(X28 + "/review/recompute2.md", "## Verdict: ALL MATCH")},
                      {"what": "Task brief calls X8 'own-conduct histories', but the Assistant turns 1-2 were written by GLM (supplied), not by the organism; the ledger's wording is 'the Assistant's own dismissive turns 1–2'",
                       "a": S(L, "X8 histories were written by GLM, not Qwen (D13)"), "b": S(L, "**X8 (blind-recomputed, ALL MATCH):**")}]
        extra_alias = [{"name": "the X8 setup", "src": S(L, "## sprint_work/005 — text-level conduct dissection on the X8 setup")},
                       {"name": "X8 histories / X8 paired histories", "src": S(L, "reply-start states for X8's paired histories")},
                       {"name": "X8 (conduct x length)", "src": S(X28 + "/RESULTS.md", "**1a′. X8:")}]
        led = ["S005", "S006", "X-extract1028", "X-sae1029", "S017"]
        turn = "turn 3, supplied (GLM-written) Assistant turns 1-2, no system prompt"
        sset = ["other: X8 50-script set (GLM-written histories)"]
        extra_corr = [{"id": "X-trust-audit-1029", "what": "X8 histories: REDO with parent-written (Qwen) histories; KEEP as a pattern", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "| **X8 histories** | **REDO**")}]
    if xn == "X4":
        extra_corr = [{"id": "X-1028-X8", "what": "X4's conduct reading was length-confounded; X8 resolved it at matched length", "src": S(X28 + "/X8/README.md", "It tests whether X4's finding is about conduct or about brevity")},
                      {"id": "X-trust-audit-1029", "what": "X4 (conduct vs label) DROP: length-confounded; superseded by X8", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "| X4 (conduct vs label) | DROP")}]
        led = ["X-1028-X8"]
    if xn == "X9":
        turn = "turn 1, no history"; sset = ["other: 5 frozen self-report questions"]
        extra_corr = [{"id": "X-1028-X9", "what": "frozen forced-choice parser mislabels 4 of 280 replies", "src": S(M, "Exploration X9: the frozen forced-choice parser")}]
    if xn == "X6":
        extra_corr = [{"id": "X-1028-X6", "what": "frozen judge item format changed mid-readout; re-judged in frozen format (D16)", "src": S(M, "Exploration X6: frozen judge item format changed")}]
    if xn == "X3":
        sset = ["P001", "census"]
        extra_corr = [{"id": "X-1028-X3", "what": "persona histories assumed animal-free; 11 of 1,000 carried 'bee'", "src": S(M, "Exploration X3: persona histories assumed animal-free")}]
        extra_alias = [{"name": "X3 V6 (hs census probe check)", "src": S(X28 + "/RESULTS.md", "The hs census probe is valid")}]
    if xn == "X2":
        turn = "turn 1, no history"
    if xn == "X1":
        turn = None; sset = []
    if xn == "X7":
        turn = "turn 3, own history"; sset = ["other: heldout2 scripts (60)"]
    if xn == "X5":
        sset = ["P001"]
    status_reason = {"verified": "Covered by the blind recompute (ALL MATCH).", "gate failed": "Polite-cell gate fails; result 'reported, not interpreted'. Gate numbers were within the blind recompute (ALL MATCH).",
                     "not recomputed": "Training run; not part of the recomputes."}[st]
    if xn == "X4":
        status_reason = "Blind recompute ALL MATCH; pirate column reported, not interpreted (E3 known-answer gate fails for the pirate arm, D15)."
    pp = []
    if xn == "X4":
        pp = [{"part": "bee/crow arm", "status": "verified", "note": "frozen branches ADDITIVE/MIXED in both s0 organisms", "src": S(X28 + "/RESULTS.md", "**Frozen branches:**")},
              {"part": "pirate arm", "status": "gate failed", "note": "E3 known-answer gate fails (psA0 diagonal 0.75 vs T1 0.53); 'reported, not interpreted' (D15)", "src": S(X28 + "/RESULTS.md", "The pirate column is reported, not interpreted")}]
    E(id=f"X-1028-{xn}", kind=kind, folder=X28 + "/" + xn, folder_name=xn,
      aliases=[{"name": xn, "src": S(X28 + "/design_spec.md", qsub)}] + extra_alias,
      title=title, title_src=S(X28 + tfile, tsub), question=q, question_src=S(X28 + "/design_spec.md", qsub),
      date_src=S(L, "## Exploration 2026-10-28"), lane_src=S(L, "## Exploration 2026-10-28"),
      run_state="done", status=st, status_reason=status_reason,
      status_src=(S(X28 + rc, "## Verdict: ALL MATCH") if xn != "X1" else S(X28 + "/X1/README.md", "**Training:**")),
      verification_note=vn, parts=pp,
      files={"readme": ex(X28 + f"/{xn}/README.md"), "design_spec": X28 + "/design_spec.md", "analysis": ex(X28 + resf),
             "other_key_md": [X28 + f"/{xn}/DECISIONS_{xn}.md"] if os.path.exists(real(X28 + f"/{xn}/DECISIONS_{xn}.md")) else []},
      raw_dirs=[X28 + f"/{xn}/out"] + raws,
      organisms_as_named=orgs, scenario_set=sset, readouts=reads, turn_and_history=turn, claims=claims, dead_end=dead,
      corrected_by=extra_corr, conflicts=extra_conf, led_to=led, key_results_file=X28 + resf, notes=note, **common28)

# ---------------------------------------------------------------- extract1028
llx = ledger_line("## extract1028")
E(id="X-extract1028", series="exploration", kind="exploration", folder="RUNS/extract1028",
  aliases=[{"name": "extract1028", "src": S(L, "## extract1028")}, {"name": "CAP (= /workspace/runs_executor/extract1028/)", "src": S(CDX + "/2026-10-31_ideation-12_reproduction_inventory.md", "**CAP**")},
           {"name": "ideation-9's extraction batch", "src": S("RUNS/extract1028/README.md", "Ideation-9's extraction batch")},
           {"name": "E1-E6 blocks (E7 dropped); not the executor lanes E1-E5", "src": S(L, "E7 (dropped by the user)")}],
  title="extract1028 — activations to save now, analyse later (2026-10-28/29, executor-8; box 1 H200; captures, exploration grade)", title_src=S(L, "## extract1028"),
  question="Capture reusable activation tensors (axis, persona subspace, reply-start states, PHM distances, story positions, trait rollouts, LoRA write directions) for Neel's axis and Assistant questions without new GPU time.",
  question_src=S(L, "reusable tensors for Neel's axis and Assistant questions"),
  date="2026-10-28/29", date_src=S(L, "## extract1028"), lane="executor-8", lane_src=S(L, "## extract1028"),
  run_state="done", status="not recomputed",
  status_reason="Captures with engineering checks (HF parity, adapters active, rebuild = sw001 ids); 'no frozen predictions and no verdicts'; first numbers descriptive; no recompute recorded.",
  status_src=S("RUNS/extract1028/RESULTS.md", "These are captures, not experiments"), verification_note="none found (checks: per-model HF parity min cos >= 0.99996; " + S(L, "per-model HF parity") + ")",
  parts=[{"part": "E1-E6", "status": "not recomputed", "note": "captures + first numbers", "src": S(L, "## extract1028")},
         {"part": "E7", "status": "pending", "note": "dropped by the user (planned, never run)", "src": S("RUNS/extract1028/RESULTS.md", "**E7 was not run**")},
         {"part": "E2 / E4 analysis", "status": "pending", "note": "'reply-start states, story positions: E2/E4, not yet analysed' (later used by sw009, sae1029)", "src": S(L, "E2/E4, not yet analysed")}],
  files={"readme": "RUNS/extract1028/README.md", "analysis": "RUNS/extract1028/RESULTS.md", "design_spec": IDN + "/2026-10-28_executor_extraction_batch.md"},
  raw_dirs=["RUNS/extract1028"], ledger_line=llx,
  organisms_as_named=["parent", "hdA0", "hdB0", "psA0", "psB0", "hdB0rep", "ctrlB0", "sym"],
  scenario_set=["census", "stories", "other: 002's 11,048 parent texts; X8 paired histories; 312 system-prompt units x 300 inputs; 018 trait/character rollouts"],
  readouts=["activations/probe"], turn_and_history="other: teacher-forced parent texts; reply-start states of X8 and census contexts; story positions",
  claims=["C", "Methods"],
  corrects=[{"id": "R002", "what": "002's 'default leaves the assistant end at L63' was a post-norm read; pre-norm the default keeps its distance from the roles", "src": S(L, "**Correction to 002:**")}],
  corrected_by=[{"id": "S016", "what": "E4's set-2 'pre-habit' position lands after the habit has begun in about half the triggered stories (affects sw009 C3 wording)", "src": S(M, "extract1028 E4's \"pre-habit\" position")},
                {"id": "X-extract1028", "what": "smoke gate used a guessed 2e-3 tolerance; vLLM LoRA path nondeterministic", "src": S(M, "extract1028 smoke gate used a guessed")}],
  led_to=["X-sae1029", "S009", "S016"], key_results_file="RUNS/extract1028/RESULTS.md",
  notes="E-block labels E1-E7 collide with executor lanes E1-E5 and the X8/E2(a) naming; use 'extract1028 E2'. Report artifact: none (captures; not requested).")

# ---------------------------------------------------------------- sae1029
lls = ledger_line("## sae1029")
E(id="X-sae1029", series="exploration", kind="exploration", folder="RUNS/sae1029",
  aliases=[{"name": "sae1029", "src": S(L, "## sae1029")}, {"name": "SAE (= /workspace/runs_executor/sae1029/)", "src": S(CDX + "/2026-10-31_ideation-12_reproduction_inventory.md", "**SAE**")},
           {"name": "ideation-9's SAE check + Neel's sparse regression + addendum A-F", "src": S(NAV, "ideation-9's SAE check")}],
  title="sae1029 — the L42 SAE for our question; Neel's sparse regression; shared helpful/dismissive latents (2026-10-29, executor-8; box 1 H200; exploration grade)", title_src=S(L, "## sae1029"),
  question="Is the L42 SAE good for our question, and is there a shared 'helpful character / helping Assistant' concept across stories and the Assistant's own turns?",
  question_src=S("RUNS/sae1029/README.md", "# sae1029"), date="2026-10-29", date_src=S(L, "## sae1029"), lane="executor-8", lane_src=S(L, "## sae1029"),
  run_state="done", status="not recomputed",
  status_reason="Parts 1-2 are exploration-grade observations with no recompute recorded; Part 3 failed its pre-registered parity check and was parked.",
  status_src=S("RUNS/sae1029/RESULTS.md", "exploration grade; observations, not claims"), verification_note="none found",
  parts=[{"part": "Part 1 (hook, quality, header splice gate)", "status": "gate failed", "note": "header splice fails the gate; the user had Part 2 run anyway ('stop if the gate fails' not applied)", "src": S(L, "**Header splice:** fails the gate")},
         {"part": "Part 2 (Lasso, per-latent AUROC, addendum A-F)", "status": "not recomputed", "note": "observations", "src": S(L, "**Part 2:**")},
         {"part": "Part 3 (causal feature clamp)", "status": "gate failed", "note": "'built, not run in full; parked by the user'; vLLM-vs-HF parity check FAILED for the small arms (gate result not independently re-verified)", "src": S(L, "parity check FAILED")}],
  files={"readme": "RUNS/sae1029/README.md", "analysis": "RUNS/sae1029/RESULTS.md", "design_spec": IDN + "/2026-10-29_executor_brief_sae_check_and_regression.md",
         "other_key_md": ["RUNS/sae1029/part3_causal/RESULTS.md", "RUNS/sae1029/part3_causal/README.md", IDN + "/2026-10-29_executor_brief_causal_feature_edit.md"]},
  raw_dirs=["RUNS/sae1029", "RUNS/sae1029/part1", "RUNS/sae1029/part2", "RUNS/sae1029/part3_causal"], ledger_line=lls,
  organisms_as_named=["parent", "hdA0", "hdB0", "psA0", "psB0"],
  scenario_set=["stories", "other: X8 50-script set", "other: web text (Ultra-FineWeb) and our chat transcripts"],
  readouts=["activations/probe"], turn_and_history="turn 1-2 Assistant tokens of X8 histories (supplied, GLM-written); stories", claims=["C", "Methods"], dead_end=True,
  corrected_by=[{"id": "X-sae1029", "what": "wording 'trained models have about twice as many shared' revised with the shared/expected ratio (training did not strengthen the link)", "src": S("RUNS/sae1029/RESULTS.md", "_Updated 29 Oct")},
                {"id": "X-sae1029", "what": "backgrounded cd did not apply; SAE hook check OOMed twice (process)", "src": S(M, "sae1029: a backgrounded")}],
  led_to=["S057"], key_results_file="RUNS/sae1029/RESULTS.md",
  notes="Deviation (user): Part 2 ran despite the Part 1 gate failure. Part 3 is a dead end at this setup ('A single-layer L42 edit on the history barely reaches the reply start'). sw057 (readers incl. SAE at S3 sites) is a later SAE use; the link is thematic (map), not a stated 'led to'. Report artifact: none (not requested).")

# ---------------------------------------------------------------- overnight cross-cutting checks
llo = ledger_line("## Overnight cross-cutting checks")
OV = "RUNS/overnight_2026-10-30"
ovcommon = dict(series="check", date="2026-10-30", lane="executor-9", ledger_line=llo,
                date_src=S(L, "## Overnight cross-cutting checks"), lane_src=S(L, "## Overnight cross-cutting checks"),
                run_state="done", status="not recomputed", status_reason="CPU checks on saved outputs; no recompute recorded.",
                status_src=S(L, "## Overnight cross-cutting checks"), verification_note="none found",
                organisms_as_named=["hdA0", "hdB0"], title_src=S(L, "## Overnight cross-cutting checks"))
E(id="X-cumctrl", kind="check", folder=OV + "/cumctrl", aliases=[{"name": "cumctrl", "src": S(L, "  - cumctrl: the cumulative state offset")},
     {"name": "orchestrator D28/D29 cumulative-offset check", "src": S(OV + "/DECISIONS.md", "**D29 (14:58)")}],
  title="Overnight cross-cutting checks: control size, scenario quality, bf16 header token 0 (2026-10-30, executor-9; CPU on saved outputs) — part cumctrl",
  question="Do the R7 'realised-displacement-matched' random controls match the real arm's cumulative state change, or only the per-layer increment?",
  question_src=S(OV + "/DECISIONS.md", "**D28 (14:08)"),
  files={"analysis": OV + "/cumctrl/TABLES.txt", "other_key_md": [OV + "/DECISIONS.md", OV + "/HIGHLIGHTS.md"]},
  raw_dirs=[OV + "/cumctrl", OV + "/acts"], scenario_set=["v1-64", "v2", "stories"], readouts=["activations/probe"],
  turn_and_history="other: saved activations of sw010, sw011 B/C, sw012, sw016, sw021", claims=["Methods"],
  corrects=[{"id": i, "what": "R7 controls self-cancel after L16 (0.12-0.41x the real arm's cumulative change at L28-63); specificity must be stated as 'vs a random-coordinate swap with a matched L16 kick'", "src": S(M, "The R7 \"realised-displacement-matched\" random controls")} for i in ["S009", "S010", "S011", "S012", "S014", "S016", "S017", "S021"]],
  led_to=["S028"], key_results_file=OV + "/cumctrl/TABLES.txt",
  notes="Next: sw028 (sustained, size-matched controls), user-approved 15:43. sw009 C4, sw014 Part 2 and sw017 use R7 controls but saved no activations, so their cumulative size is unmeasured (mistakes.md). Third recurrence of 'control matched on the wrong quantity'.", **ovcommon)
E(id="X-scenqc", kind="check", folder=OV + "/scenqc", aliases=[{"name": "scenqc", "src": S(L, "  - scenqc:")}, {"name": "Is it just bad scenarios? (user's question 13:20)", "src": S(OV + "/HIGHLIGHTS.md", "## Is it just bad scenarios?")}],
  title="Overnight cross-cutting checks: control size, scenario quality, bf16 header token 0 (2026-10-30, executor-9; CPU on saved outputs) — part scenqc",
  question="Is it just bad scenarios? Do outcome-independent badness scores, exclusions, leave-one-out and direct reading explain the failures in sw021, sw020, sw011 Part B and sw016?",
  question_src=S(L, "  - scenqc:"),
  files={"analysis": OV + "/scenqc/SYNTHESIS.md"}, raw_dirs=[OV + "/scenqc"], scenario_set=["v2", "v1-64", "stories"],
  readouts=["other: outcome-independent scenario badness scores"], turn_and_history="other: saved outputs of sw011 B, sw016, sw020, sw021", claims=["Methods"],
  corrects=[{"id": "S021", "what": "sw021's 0.10 control bound sits within sampling noise at n = 61", "src": S(L, "sw021's 0.10 control bound sits within sampling noise")},
            {"id": "S020", "what": "sw020's missing trigger-gating in hdA0 is a protocol effect (habit starts in its own turns 1-2), not bad scenarios", "src": S(L, "sw020's missing trigger-gating in hdA0 is a protocol effect")}],
  dead_end=False, key_results_file=OV + "/scenqc/SYNTHESIS.md",
  notes="Limit stated in source: screens have no positive control ('no evidence', not 'ruled out').", **ovcommon)
E(id="X-bf16-header-token0", kind="check", folder=OV + "/acts", aliases=[{"name": "bf16 header token 0", "src": S(L, "  - **bf16:**")}, {"name": "sw021 activation-gate diagnosis", "src": S(L, "the sw021 activation-gate diagnosis of header token 0")}],
  title="Overnight cross-cutting checks: control size, scenario quality, bf16 header token 0 (2026-10-30, executor-9; CPU on saved outputs) — part bf16 header token 0",
  question="Why did sw021's activation gate fail: is header token 0 (<|im_start|>) unstable in bf16 at late layers?",
  question_src=S(OV + "/acts/README_bf16_header_token0.md", "Found by the sw021 activation-gate diagnosis"),
  files={"readme": OV + "/acts/README_bf16_header_token0.md", "other_key_md": [OV + "/DECISIONS.md", "NS/experiments/sprint_work/021_v2_c4_replication/DECISIONS.md"]},
  raw_dirs=["RUNS/sw021/diag_acts", OV + "/acts"], _scan=False, scenario_set=["v2"], readouts=["activations/probe"], turn_and_history="other: reply-start header states",
  claims=["Methods"], corrects=[{"id": "S021", "what": "the old 'max relative error <= 0.25' acts gate tripped on bf16 noise; 'low-norm token' was the wrong diagnosis; recommendation: drop header token 0 at L >= 36 or recapture in fp32", "src": S(M, "sw021 acts gate: a guessed max tolerance")}],
  key_results_file=OV + "/acts/README_bf16_header_token0.md",
  notes="Caveat applies to every activation saved on 30 Oct. UNSURE in source whether swap donors carry this noise into science numbers (DECISIONS D24).", **ovcommon)

# ---------------------------------------------------------------- infra and recompute dirs in RUNS
E(id="X-recompute-E4-late", series="check", kind="check", attaches_to=["S064", "S078", "S079"], folder="RUNS/recompute_E4_late",
  aliases=[{"name": "Blind recompute E4 late (sw064, sw078, sw079 job 91)", "src": S("RUNS/recompute_E4_late/RECOMPUTE.md", "# Blind recompute E4 late")}],
  title="Blind recompute E4 late (sw064, sw078, sw079 job 91)", title_src=S("RUNS/recompute_E4_late/RECOMPUTE.md", "# Blind recompute E4 late"),
  question="Recompute sw064, sw078 and sw079 (job 91) headline tables from raw labelled rows without opening the experiments' analysis code or reports.",
  question_src=S("RUNS/recompute_E4_late/RECOMPUTE.md", "Recomputed from raw labelled rows"), date="2026-10-31", date_src=None,
  lane=None, lane_src=None, run_state="done", status="not recomputed", status_reason="This is itself a blind recompute of numbered experiments.",
  status_src=S("RUNS/recompute_E4_late/RECOMPUTE.md", "# Blind recompute E4 late"), verification_note="none found (entry is a recompute)",
  files={"readme": "RUNS/recompute_E4_late/RECOMPUTE.md"}, raw_dirs=["RUNS/recompute_E4_late"], claims=["Methods"],
  key_results_file="RUNS/recompute_E4_late/RECOMPUTE.md",
  notes="Attach to the S064/S078/S079 cards as their recompute record. Date and lane not stated in the file header; date taken from the E4 day (assumption).")
E(id="X-infra-r018", series="check", kind="infra", attaches_to=["R018"], folder="RUNS/r018",
  aliases=[{"name": "r018", "src": S(NAV, "`r018/`: experiment 018")}], title="r018: experiment 018 activations (network-volume copy)", title_src=S("RUNS/r018/README.md", "# r018"),
  question="Network-volume copy of experiment 018's parent activations and parity tensors.", question_src=S("RUNS/r018/README.md", "Copied 25 Oct 2026"),
  date="2026-10-25", date_src=S("RUNS/r018/README.md", "Copied 25 Oct 2026"), lane="executor-4", lane_src=S("RUNS/r018/README.md", "Copied 25 Oct 2026"),
  run_state="done", status="not recomputed", status_reason="Data copy (verified sizes and sample SHA-256), no analysis.", status_src=S("RUNS/r018/README.md", "Verified: 60 files"),
  verification_note="\"Verified: 60 files, 77.1 GB, no size mismatches, SHA-256 matching on a sample of 4 chunks\" (" + S("RUNS/r018/README.md", "Verified: 60 files") + ")",
  files={"readme": "RUNS/r018/README.md"}, raw_dirs=["RUNS/r018"], organisms_as_named=["parent", "001 A"], claims=["Methods"], key_results_file="RUNS/r018/README.md",
  notes="Infra; attach to R018.")
E(id="X-infra-box1-backup-1027", series="check", kind="infra", folder="RUNS/box1_local_20261027",
  aliases=[{"name": "box1_local_20261027", "src": S("RUNS/box1_local_20261027/README.md", "# Box-1 container-disk backup")}],
  title="Box-1 container-disk backup, 27 Oct 2026 (executor-6, at the user's request before clearing the container disk)", title_src=S("RUNS/box1_local_20261027/README.md", "# Box-1 container-disk backup"),
  question="Back up box 1's container-local disk (Tinker checkpoints for 009/013, sw001 captures, lens files, session scratchpads) before it was cleared.", question_src=S("RUNS/box1_local_20261027/README.md", "Everything below was on box 1"),
  date="2026-10-27", date_src=S("RUNS/box1_local_20261027/README.md", "# Box-1 container-disk backup"), lane="executor-6", lane_src=S("RUNS/box1_local_20261027/README.md", "# Box-1 container-disk backup"),
  run_state="done", status="not recomputed", status_reason="Backup; rsync dry-run verified.", status_src=S("RUNS/box1_local_20261027/README.md", "checked with a dry-run"),
  verification_note="\"checked with a dry-run (0 files missing or different)\" (" + S("RUNS/box1_local_20261027/README.md", "checked with a dry-run") + ")",
  files={"readme": "RUNS/box1_local_20261027/README.md"}, raw_dirs=["RUNS/box1_local_20261027"], _scan=False, claims=["Methods"],
  attaches_to=["R009", "S001", "S002"], key_results_file="RUNS/box1_local_20261027/README.md",
  notes="Holds tinker_ckpt for 009 and 013 (013 Kimi-K2.6 B s0), sw001_big captures, lenses used by sw002 src/lens/, and five sessions' scratchpads (tmp_claude-0, not inventoried).")
E(id="X-infra-sw002-box-mirrors", series="check", kind="infra", attaches_to=["S002", "S001", "R018"], folder="RUNS/box3_sw002",
  aliases=[{"name": "box3_sw002 / box4_sw002", "src": "RUNS/box3_sw002"}],
  title=None, title_src=None, question="Copies of boxes 3 and 4 run folders used by sprint_work/002 (eval, merged, p008, p010, r018, sw001; box 4 also explore1026 and the Track H capture).",
  question_src=None, date="2026-10-26", date_src=None, lane="executor-6 (assumed; sw002 ran on boxes 1, 3, 4)", lane_src=S(L, "## sprint_work/002"),
  run_state="done", status="not recomputed", status_reason="Mirror, no analysis.", status_src=None, verification_note="none found",
  files={}, raw_dirs=["RUNS/box3_sw002", "RUNS/box4_sw002", "RUNS/box4_sw002/runs/sw002_trackH_capture.pt"], _scan=False, claims=["Methods"],
  key_results_file=None,
  notes="No README in either folder; purpose inferred from contents (ls) and from ideation-8's h_story_scale_check.py reading RUNS/box4_sw002/runs/sw002_trackH_capture.pt (" + S(IDN + "/2026-10-27_hypotheses_checks/h_story_scale_check.py", "sw002_trackH_capture.pt") + ").")
E(id="X-infra-box-setup-1030", series="check", kind="infra", folder="RUNS/box_setup_20261030",
  aliases=[{"name": "box_setup_20261030", "src": S("RUNS/box_setup_20261030/setup_box.sh", "executor-9, 30 Oct 2026")}],
  title=None, title_src=None, question="Set up fresh 1xH200 pods on the shared /workspace (venvs, lens sources, parent at box 1's pinned revision, hashes) for the 30 Oct overnight run.",
  question_src=S("RUNS/box_setup_20261030/setup_box.sh", "set up a fresh 1xH200 pod"), date="2026-10-30", date_src=S("RUNS/box_setup_20261030/setup_box.sh", "executor-9, 30 Oct 2026"),
  lane="executor-9", lane_src=S("RUNS/box_setup_20261030/setup_box.sh", "executor-9, 30 Oct 2026"), run_state="done", status="not recomputed", status_reason="Setup logs and sha256 lists; no analysis.",
  status_src=None, verification_note="none found (per-host sha256 files vs box1_reference.sha256)", files={}, raw_dirs=["RUNS/box_setup_20261030"], _scan=False, claims=["Methods"],
  attaches_to=["S010", "S011", "S012", "S013", "S014", "S015", "S016", "S017", "S018", "S019", "S020", "S021", "S022", "S023", "S024", "S025", "S026", "S027", "S028"],
  notes="Infra for the overnight 2026-10-30 run (sw010-sw028).")
E(id="X-infra-merged-hdA0", series="check", kind="infra", folder="RUNS/merged/hd-A_s0", attaches_to=["R001", "R018"],
  aliases=[{"name": "/root/runs/merged/hd-A_s0", "src": S(X25 + "/round5_strongest_organism/PRIORS.md", "/root/runs/merged/hd-A_s0")}],
  title=None, title_src=None, question="Merged full-weight copy of 001 A s0 (hd-A_s0) for vllm-lens use.", question_src=None, date=None, date_src=None, lane=None, lane_src=None,
  run_state="done", status="not recomputed", status_reason="Merge with merge_report.json (496 modules merged, max_rel_resid 0.0036, untouched identical).", status_src="RUNS/merged/hd-A_s0/merge_report.json#max_rel_resid",
  verification_note="merge_report.json: untouched_identical true (RUNS/merged/hd-A_s0/merge_report.json#untouched_identical)", files={"readme": None}, raw_dirs=["RUNS/merged/hd-A_s0"], _scan=False,
  organisms_as_named=["hd-A_s0", "001 A s0"], claims=["Organisms"], notes="Validated through vllm-lens per 018 D33 (PRIORS.md). Date/lane not recorded in the folder.")
E(id="X-infra-E2-activations", series="check", kind="infra", folder="RUNS/E2_activations", attaches_to=["S029", "S034", "S035", "S037"],
  aliases=[{"name": "E2 Lane M activation captures", "src": S("RUNS/E2_activations/README.md", "# Story imprinting: E2 Lane M activation captures")}],
  title="Story imprinting: E2 Lane M activation captures, 31 Oct 2026", title_src=S("RUNS/E2_activations/README.md", "# Story imprinting: E2 Lane M activation captures"),
  question="Residual-stream captures and LoRA module writes behind sw029, sw034, sw035 and sw037 (packaged for HF upload).", question_src=S("RUNS/E2_activations/README.md", "Residual-stream captures and LoRA module writes"),
  date="2026-10-31", date_src=S("RUNS/E2_activations/README.md", "# Story imprinting: E2 Lane M activation captures"), lane="executor-11 / E2 (lane M)", lane_src=S(L, "## sprint_work/035"),
  run_state="done", status="not recomputed", status_reason="Capture package with SHA256SUMS and VERIFY_OK marker; there is also an UPLOAD_FAIL marker.", status_src="RUNS/E2_activations/VERIFY_OK",
  verification_note="VERIFY_OK marker and SHA256SUMS present (RUNS/E2_activations/VERIFY_OK)", files={"readme": "RUNS/E2_activations/README.md"}, raw_dirs=["RUNS/E2_activations"], _scan=False,
  organisms_as_named=["hdA0", "hdB0", "ctrlB0", "mixA0", "Bs1", "Bs2", "e08-N", "e08-NB", "e08-X", "e08-XB", "parent"],
  tony_links=[{"what": "Tony's e08 register pairs e08-N/NB/X/XB captured", "src": S("RUNS/E2_activations/README.md", "**e08-N / NB / X / XB:**")}],
  conflicts=[{"what": "both UPLOAD_DONE and UPLOAD_FAIL.1756 markers exist; upload status unclear", "a": "RUNS/E2_activations/UPLOAD_DONE", "b": "RUNS/E2_activations/UPLOAD_FAIL.1756"}],
  claims=["C"], notes="Lane label 'E2' here is the executor lane, not extract1028 E2.")
E(id="X-infra-node-mirror-E3", series="check", kind="infra", folder="RUNS/node_mirror_E3", attaches_to=["S040", "S041", "S042", "S043", "S044", "S045"],
  aliases=[{"name": "node mirror", "src": S(NAV, "node mirror `/workspace/runs_executor/node_mirror_E3/`")}],
  title=None, title_src=None, question="Every-10-minute mirror (no deletes) of E3's rented 4xH200 node; includes recompute_p3_indep (independent P3 recompute: parent's 'which character are you more like?' first-token logprobs).",
  question_src=S(NAV, "node mirror `/workspace/runs_executor/node_mirror_E3/`"), date="2026-10-31", date_src=S("RUNS/node_mirror_E3/BACKUP.log", "2026-10-31T11:41"),
  lane="executor-12 / E3", lane_src=S(NAV, "E3's day run (executor-12"), run_state="done", status="not recomputed", status_reason="Mirror; no analysis.", status_src=None, verification_note="none found",
  files={}, raw_dirs=["RUNS/node_mirror_E3", "RUNS/node_mirror_E3/runs/recompute_p3_indep"], _scan=False, claims=["ChainP", "Methods"],
  notes="recompute_p3_indep belongs to Chain P P3 (sw041 forecast); attach there (map: file header only).")

# ---------------------------------------------------------------- throwaway misc
E(id="X-automated-grad-awareness", series="exploration", kind="infra", folder=TT + "/automated grad awareness",
  aliases=[{"name": "automated grad awareness", "src": S(NAV, "`automated grad awareness/`")}, {"name": "grader vector", "src": S(X25 + "/notes.md", "Grader vector")}],
  title="Automated-grading awareness: steering vector reimplementation (draft, saved for later)", title_src=S(TT + "/automated grad awareness/README.md", "# Automated-grading awareness"),
  question="Reimplement Betley/Treutlein/Dumas' 'automated grading' steering vector on our vllm-lens stack (extract, steer, judge).",
  question_src=S(TT + "/automated grad awareness/README.md", "## Source"), date="2026-10-25", date_src=S(TT + "/automated grad awareness/README.md", "**Status:** executor-4, 25 Oct 2026"),
  lane="executor-4", lane_src=S(TT + "/automated grad awareness/README.md", "**Status:** executor-4, 25 Oct 2026"),
  run_state="abandoned", status="not recomputed", status_reason="Draft: extraction run and validated; steering and judge only smoke-tested; 'nothing here is a project claim'.",
  status_src=S(TT + "/automated grad awareness/README.md", "nothing here is a project claim"), verification_note="none found",
  files={"readme": TT + "/automated grad awareness/README.md"}, raw_dirs=[TT + "/automated grad awareness/results"], _scan=False,
  organisms_as_named=["parent"], readouts=["activations/probe"], claims=["Methods"],
  led_to=["X-1025-parent-exploration"], notes="Grader vector reused in the 25 Oct parent exploration (A1, B2). run_state 'abandoned' = parked draft, never promoted to experiments/.")
E(id="X-story-prompt-reconstruction", series="exploration", kind="exploration", folder=TT + "/prompt making",
  aliases=[{"name": "prompt making", "src": S(NAV, "(`prompt making/`)")}, {"name": "sharing (story-generator prompts for sharing)", "src": S(TT + "/sharing/README.md", "# Story-generator prompts")}],
  title="Reconstructing the Story Imprinting §4 story-generation prompts (23 Oct 2026, ideation session)", title_src=S(TT + "/prompt making/README.md", "# Reconstructing"),
  question="Recover the authors' §4 story-generation prompts so we can generate stories that look like theirs (generator fly-off), and package the prompts for sharing.",
  question_src=S(TT + "/prompt making/README.md", "This folder is the weekend attempt"), date="2026-10-23", date_src=S(TT + "/prompt making/README.md", "# Reconstructing"),
  lane="ideation", lane_src=S(TT + "/prompt making/README.md", "# Reconstructing"), run_state="done", status="not recomputed",
  status_reason="Throwaway reconstruction; comparisons are 'leads, not measurements'.", status_src=S(TT + "/sharing/README.md", "so they are leads, not measurements"), verification_note="none found",
  files={"readme": TT + "/prompt making/README.md", "other_key_md": [TT + "/sharing/README.md", TT + "/prompt making/release_inventory.md", TT + "/prompt making/leak_forensics.md", TT + "/prompt making/habit_free_story_advice.md"]},
  raw_dirs=[TT + "/prompt making/gen", TT + "/sharing"], _scan=False, scenario_set=["stories"], readouts=["other: generator comparison"], claims=["Methods", "Organisms"],
  led_to=["R012", "R005"], notes="Led-to links are a map-level inference (R012 generator NLL screen; habit_free_story_advice.md for the 005 control); not confirmed by a 'led to' sentence.")
E(id="X-external-agent-sarcastic-task", series="exploration", kind="audit", folder=None, folder_name="2026-10-26_external_agent_helpful_vs_sarcastic.md",
  aliases=[{"name": "helpful-vs-sarcastic organism task for an external coding agent", "src": S(TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md", "# Task for a coding agent")}],
  title="Task for a coding agent: train and evaluate the helpful-vs-sarcastic story-imprinting organism on Qwen3.6-27B", title_src=S(TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md", "# Task for a coding agent"),
  question="Train helpful vs sarcastic (voice vs values) with our recipe and test persona matching vs generic amplification of the flip.",
  question_src=S(TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md", "**The question that makes it fun:**"), date="2026-10-26", date_src=S(TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md", "_Written 26 Oct 2026"),
  lane="ideation (task prompt for an external agent)", lane_src=S(TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md", "_Written 26 Oct 2026"),
  run_state="done", status="not recomputed", status_reason="A task prompt, not a result; the resulting adapters are probably the user's public hs-A/B_s0 sarcastic adapters (unconfirmed).",
  status_src=None, verification_note="none found", files={"other_key_md": [TT + "/2026-10-26_external_agent_helpful_vs_sarcastic.md"]},
  organisms_as_named=["hs-A_s0", "hs-B_s0 (user's sarcastic adapters; link unconfirmed)"], claims=["Organisms"], led_to=["S002", "S003"],
  notes="sw002 D1 uses 'the user's public sarcastic adapters' senku21x/story-imprinting-qwen36-27b-sarcastic (" + S("NS/experiments/sprint_work/002_routing_locus_across_runs/decisions.md", "## D1") + "); that these came from this task is NOT stated in any file I read. run_state 'done' refers to the prompt being written.")

# ---------------------------------------------------------------- ideation checks
E(id="X-nll-check-1023", series="check", kind="exploration", folder=IDN + "/nll_check",
  aliases=[{"name": "nll_check", "src": S(M, "nll_check.py")}],
  title=None, title_src=None,
  question="How surprising are the authors' Kimi stories vs Qwen-written stories to Qwen3.6-27B and to Gemma-3-27B-it (mean per-token NLL, bits per byte)?",
  question_src=S(IDN + "/nll_check/nll_check.py", "How surprising are the authors' Kimi stories"), date="2026-10-23", date_src=None,
  lane="ideation (inferred from folder)", lane_src=None, run_state="done", status="not recomputed", status_reason="Script + JSON outputs only; no write-up.", status_src=None, verification_note="none found",
  files={}, raw_dirs=[IDN + "/nll_check"], _scan=False, organisms_as_named=["parent (Qwen3.6-27B)", "Gemma-3-27B-it"], scenario_set=["stories"], readouts=["other: per-token NLL / bits per byte"],
  claims=["Organisms", "Methods"], led_to=["R012"], key_results_file=IDN + "/nll_check/qwen36_27b.json",
  notes="Date from file mtimes (23 Oct 21:08-21:31), not from a document. Precursor of 012's generator NLL screen (map-level link). No README.")
E(id="X-ideation2-salvage-1024", series="check", kind="check", attaches_to=["R001", "R006"], folder=IDN + "/2026-10-24_ideation2_salvage",
  aliases=[{"name": "ideation-2 salvage", "src": S(IDN + "/2026-10-24_ideation2_salvage/README.md", "# What ideation-2 found")}],
  title="What ideation-2 found (salvaged by ideation-1, 24 Oct 2026, ~12:30 UTC)", title_src=S(IDN + "/2026-10-24_ideation2_salvage/README.md", "# What ideation-2 found"),
  question="Analyse 001's T 1 + min-p 0.05 judgments (and T0.7/T1 with mix_A_s0) with the executor's own analyze.py: does truncating the tail remove garble while the flip survives?",
  question_src=S(IDN + "/2026-10-24_ideation2_salvage/README.md", "Truncating the tail removes the garble"), date="2026-10-24", date_src=S(IDN + "/2026-10-24_ideation2_salvage/README.md", "# What ideation-2 found"),
  lane="ideation-2 (salvaged by ideation-1)", lane_src=S(IDN + "/2026-10-24_ideation2_salvage/README.md", "# What ideation-2 found"), run_state="done", status="not recomputed",
  status_reason="T 1 + min-p numbers re-checked by ideation-1 against T1mp05.json (same script, not independent).", status_src=S(IDN + "/2026-10-24_ideation2_salvage/README.md", "re-checked by ideation-1"),
  verification_note="\"the T 1 + min-p numbers re-checked by ideation-1 against `T1mp05.json`\" (" + S(IDN + "/2026-10-24_ideation2_salvage/README.md", "re-checked by ideation-1") + ")",
  files={"readme": IDN + "/2026-10-24_ideation2_salvage/README.md"}, raw_dirs=[IDN + "/2026-10-24_ideation2_salvage"], _scan=False,
  organisms_as_named=["A s0", "B s0", "mix_A_s0"], scenario_set=["P001"], readouts=["judge rubric", "free (512)"], turn_and_history="turn 3, own history", claims=["Organisms", "Methods"])
E(id="X-study1-persona-screen-1024", series="check", kind="exploration", folder=IDN + "/2026-10-24_study1_persona_check",
  aliases=[{"name": "Study 1 recipient personas screen", "src": S(IDN + "/2026-10-24_study1_persona_check/README.md", "# Study 1 recipient personas")}],
  title="Study 1 recipient personas: a screen on the parent (ideation, 24 Oct 2026)", title_src=S(IDN + "/2026-10-24_study1_persona_check/README.md", "# Study 1 recipient personas"),
  question="Do the four Study 1 recipient personas (helpful/dismissive x warm/curt) actually separate disposition from style on the parent?",
  question_src=S(IDN + "/2026-10-24_study1_persona_check/README.md", "**Question.**"), date="2026-10-24", date_src=S(IDN + "/2026-10-24_study1_persona_check/README.md", "# Study 1 recipient personas"),
  lane="ideation", lane_src=S(IDN + "/2026-10-24_study1_persona_check/README.md", "# Study 1 recipient personas"), run_state="done", status="not recomputed",
  status_reason="'The judging here is a screen, not the experiment's protocol' (integer scores, API parent).", status_src=S(IDN + "/2026-10-24_study1_persona_check/README.md", "The judging here is a screen"),
  verification_note="none found", files={"readme": IDN + "/2026-10-24_study1_persona_check/README.md"}, raw_dirs=[IDN + "/2026-10-24_study1_persona_check/out"], _scan=False,
  organisms_as_named=["parent (qwen/qwen3.6-27b via OpenRouter)"], scenario_set=["P001"], readouts=["judge rubric"], turn_and_history="turn 3, own history", claims=["Methods"],
  notes="Related to the 25 Oct exploration's C1/C1b recipient checks (map-level).")
E(id="X-all-results-report-1025", series="check", kind="check", folder=IDN + "/all_results_report",
  aliases=[{"name": "aggregate report / all-results report", "src": S(IDN + "/all_results_report/prepare_data.py", "all-results report")}],
  title="Story Imprinting Sprint Results", title_src=S(IDN + "/all_results_report/page.html", "<title>"),
  question="Aggregate all results to 25 Oct into one HTML report from gatherer/checker JSON files (verified copies where the checker made them).",
  question_src=S(IDN + "/all_results_report/prepare_data.py", "Inputs: the gatherer/checker JSON"), date="2026-10-25", date_src=S(IDN + "/all_results_report/prepare_data.py", "(ideation, 25 Oct 2026)"),
  lane="ideation", lane_src=S(IDN + "/all_results_report/prepare_data.py", "(ideation, 25 Oct 2026)"), run_state="done", status="not recomputed",
  status_reason="Uses '*.verified.json' checker outputs; the checker files are in a session scratchpad not inventoried.", status_src=S(IDN + "/all_results_report/prepare_data.py", "core_flip.verified.json"),
  verification_note="checker-verified inputs: core_flip.verified.json, health_gating.verified.json (" + S(IDN + "/all_results_report/prepare_data.py", "core_flip.verified.json") + ")",
  files={}, raw_dirs=[IDN + "/all_results_report"], claims=["Methods", "Organisms", "D"],
  corrects=[{"id": "R005", "what": "005 analysis counts judgments as conversations (aggregate report correction verified by codex-1)", "src": S(M, "005 analysis counts judgments as conversations")},
            {"id": "R018", "what": "018 prose overstates known-answer preservation and understates random-control failures (found in aggregate report)", "src": S(M, "018 prose overstates known-answer")}],
  attaches_to=["R001", "R005", "R006", "R008", "R009", "R010", "R011", "R014", "R016", "R017", "R018"],
  notes="5.6 MB self-contained HTML. No artifact URL found for it.")
E(id="X-sw002-redteam-1027", series="check", kind="check", attaches_to=["S002"], folder=IDN + "/2026-10-27_sw002_redteam",
  aliases=[{"name": "ideation-8 red-team of sw002", "src": S(L, "ideation-8 red-team")}],
  title="sprint_work/002 red-team: H-org, Track A, Track G (ideation-8, 27 Oct 2026)", title_src=S(IDN + "/2026-10-27_sw002_redteam/REPORT.md", "# sprint_work/002 red-team"),
  question="Independently recompute sw002's H-org, Track A and Track G numbers from raw generations and test whether H's specificity holds across the whole grid.",
  question_src=S(IDN + "/2026-10-27_sw002_redteam/REPORT.md", "Before this, H-org had no independent recompute"), date="2026-10-27", date_src=S(IDN + "/2026-10-27_sw002_redteam/REPORT.md", "# sprint_work/002 red-team"),
  lane="ideation-8 (independent subagent)", lane_src=S(IDN + "/2026-10-27_sw002_redteam/REPORT.md", "_Independent subagent of ideation-8"), run_state="done", status="not recomputed",
  status_reason="This entry is itself an independent recompute (numbers match); its interpretive finding changed sw002.", status_src=S(IDN + "/2026-10-27_sw002_redteam/REPORT.md", "## Audited numbers"),
  verification_note="none found (entry is a recompute of sw002)", files={"readme": IDN + "/2026-10-27_sw002_redteam/REPORT.md"}, raw_dirs=[IDN + "/2026-10-27_sw002_redteam"], _scan=False,
  organisms_as_named=["B s0", "B s1", "A s0", "A s1", "A s2", "mix010 A s1", "011", "rep B"], scenario_set=["P001"], readouts=["forced 'By the way,'", "STRICT regex"], claims=["C", "Methods"],
  corrects=[{"id": "S002", "what": "H-org's 'moves B where persona directions never did' withdrawn: random_1 moves B s0 +32.7 / B s1 +31.2 in the same grid; A runs respond at L40 alpha 0.4; RESULTS.md A s1 max random wrong", "src": S(L, "**Correction (27 Oct, ideation-8 red-team")}],
  notes="Also logged in mistakes.md (" + S(M, "sw002 H-org read as \"moves B where nothing else did\"") + ").")
E(id="X-ideation8-hypotheses-checks", series="check", kind="check", folder=IDN + "/2026-10-27_hypotheses_checks",
  aliases=[{"name": "hypotheses_checks (natural-scale dose checks)", "src": S("NS/_sessions/ideation/notes/2026-10-27_spec_sprint_work_003_routing_features_and_pirate_family.md", "2026-10-27_hypotheses_checks")}],
  title=None, title_src=None,
  question="CPU checks on saved data: is Track H a high-variance direction, how big were the steering doses in natural units (chat and stories), and does the parent's projection onto H predict sw001's census routing beyond the axis?",
  question_src=S(IDN + "/2026-10-27_hypotheses_checks/h_variance_check.py", "Ideation-8 CPU check: is Track H a high-variance direction"), date="2026-10-27", date_src=S(M, "Steering directions compared at equal norm"),
  lane="ideation-8", lane_src=S(IDN + "/2026-10-27_hypotheses_checks/h_projection_census.py", "Ideation-8 exploratory check"), run_state="done", status="not recomputed", status_reason="Scripts + JSON; findings written into mistakes.md and ideation notes.",
  status_src=S(M, "Steering directions compared at equal norm"), verification_note="none found",
  files={"other_key_md": [IDN + "/2026-10-27_new_hypotheses.md"]}, raw_dirs=[IDN + "/2026-10-27_hypotheses_checks"], _scan=False,
  html_local=[IDN + "/2026-10-27_ideation8_review.html"],
  organisms_as_named=["parent"], scenario_set=["census", "stories"], readouts=["activations/probe"], claims=["Methods", "C"],
  corrects=[{"id": i, "what": "steering doses at equal Euclidean norm, isotropic random nulls; specificity claims show only 'not generic noise of that kind'", "src": S(M, "Steering directions compared at equal norm")} for i in ["S001", "S002", "X-1027-overnight"]],
  led_to=["S003"], key_results_file=IDN + "/2026-10-27_hypotheses_checks/h_variance_check.json",
  notes="sw003's spec cites these checks as the reason for natural-unit doses (" + S("NS/_sessions/ideation/notes/2026-10-27_spec_sprint_work_003_routing_features_and_pirate_family.md", "2026-10-27_hypotheses_checks") + "). The ideation-8 review page (HTML) carries the corrected interpretation ('Interpretation corrected in ideation notes and the review page').")
E(id="X-pirate-read-1027", series="check", kind="review", attaches_to=["S003"], folder=IDN + "/2026-10-27_pirate_read",
  aliases=[{"name": "pirate qualitative read", "src": S(IDN + "/2026-10-27_pirate_read/READ.md", "# Qualitative read")}],
  title="Qualitative read: pirate/Shakespeare organisms, default persona after the rude turn (ideation-8, 27 Oct 2026)", title_src=S(IDN + "/2026-10-27_pirate_read/READ.md", "# Qualitative read"),
  question="What do sw003 Part P's default-persona rude-turn conversations actually look like (20 of 398 read)?", question_src=S(IDN + "/2026-10-27_pirate_read/READ.md", "**What was read.**"),
  date="2026-10-27", date_src=S(IDN + "/2026-10-27_pirate_read/READ.md", "# Qualitative read"), lane="ideation-8", lane_src=S(IDN + "/2026-10-27_pirate_read/READ.md", "# Qualitative read"),
  run_state="done", status="not recomputed", status_reason="Qualitative read; no numbers.", status_src=None, verification_note="none found",
  files={"readme": IDN + "/2026-10-27_pirate_read/READ.md"}, raw_dirs=[IDN + "/2026-10-27_pirate_read"], _scan=False, organisms_as_named=["ps A", "ps B"], readouts=["other: qualitative read"], claims=["Organisms"])
E(id="X-census-counterexamples-1028", series="check", kind="check", folder=IDN + "/2026-10-28_census_counterexamples",
  aliases=[{"name": "census counterexample hunt", "src": S(M, "census counterexample hunt")}],
  title="Census counterexample hunt (ideation-9, 28 Oct 2026; CPU, saved data, no spend)", title_src=S(IDN + "/2026-10-28_census_counterexamples/README.md", "# Census counterexample hunt"),
  question="Do the 271-role routing censuses contain far-but-routes or near-but-doesn't roles (counterexamples to 'similarity -> uptake'), and what explains them?",
  question_src=S(IDN + "/2026-10-28_census_counterexamples/README.md", "**Question.**"), date="2026-10-28", date_src=S(IDN + "/2026-10-28_census_counterexamples/README.md", "# Census counterexample hunt"),
  lane="ideation-9", lane_src=S(IDN + "/2026-10-28_census_counterexamples/README.md", "# Census counterexample hunt"), run_state="done", status="not recomputed",
  status_reason="CPU analysis on saved sw003 Part C data; part of it post hoc (labelled).", status_src=S(IDN + "/2026-10-28_census_counterexamples/README.md", "Added after the first pass (post hoc"), verification_note="none found",
  files={"readme": IDN + "/2026-10-28_census_counterexamples/README.md"}, raw_dirs=[IDN + "/2026-10-28_census_counterexamples"], _scan=False,
  organisms_as_named=["hd A s0", "hd B s0", "hs A", "hs B", "parent"], scenario_set=["census"], readouts=["log-odds"], turn_and_history="turn 3, supplied (parent-written) history", claims=["A", "B"],
  corrects=[{"id": "S003", "what": "per-assignment census reading ('axis predicts only in assignment A') withdrawn: on the assignment-averaged score the axis predicts routing in both pairs; Part C's per-model predictor comparisons carry the same contamination", "src": S(M, "Census routing read per assignment")},
            {"id": "S001", "what": "pooled R (sw001's original) cancels the persona-specific animal lean", "src": S(M, "sw001's original R, which cancels the lean")}],
  led_to=["S075"], notes="Link to sw075 (census re-read) is map-level, not a stated 'led to'.")
E(id="X-trust-audit-1029", series="check", kind="audit", folder=None, folder_name="2026-10-29_trust_audit_what_to_redo.md",
  aliases=[{"name": "trust audit", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "# Trust audit")}],
  title="Trust audit: what to keep, what to redo, what to drop (ideation-9, 29 Oct 2026)", title_src=S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "# Trust audit"),
  question="Label every organism, dataset, instrument and result KEEP / REDO / LEAD / DROP as the starting inventory for the new repo.", question_src=S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "Purpose: the starting inventory"),
  date="2026-10-29", date_src=S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "# Trust audit"), lane="ideation-9", lane_src=S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "# Trust audit"),
  run_state="done", status="not recomputed", status_reason="Written audit; no new measurement.", status_src=None, verification_note="none found",
  files={"other_key_md": [IDN + "/2026-10-29_trust_audit_what_to_redo.md", IDN + "/2026-10-29_inventory/README.md", IDN + "/2026-10-29_inventory/B_sprintwork_and_explorations.md", IDN + "/2026-10-29_inventory/A_reproduction_and_adapters.md", IDN + "/2026-10-29_inventory/C_data_models_activations.md"]},
  claims=["Methods", "Organisms"],
  corrects=[{"id": "X-1028-X4", "what": "DROP: length-confounded; superseded by X8", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "| X4 (conduct vs label) | DROP")},
            {"id": "R002", "what": "002 (quick) L63 claims DROP: post-norm read error; superseded by E1", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "| 002 (quick) L63 claims | DROP")},
            {"id": "X-1028-X8", "what": "X8 histories REDO with Qwen-written histories", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "| **X8 histories** | **REDO**")}],
  tony_links=[{"what": "Partner's e08 N/NB, X/XB, V/VB: LEAD; e08 R10 'LEAD, high value'; e05 R07; e09/e10", "src": S(IDN + "/2026-10-29_trust_audit_what_to_redo.md", "Partner's N/NB, X/XB, V/VB (e08)")}],
  led_to=["S019"], notes="Regeneration list (habit-free control retrain, Qwen-written X8 histories, multi-token readout, e08 R10 2x2). Link to sw019 (eval set v2 with parent-written histories) is map-level. Companion: 2026-10-29_inventory/ (A/B/C parts) and 2026-10-29_pilot_branches/ (Tony's branches synthesis).")
E(id="X-chainP-calibration-1030", series="check", kind="exploration", folder=IDN + "/2026-10-31_chainP_calibration",
  aliases=[{"name": "Chain P calibration screen", "src": S(IDN + "/2026-10-31_chainP_calibration/design.md", "# Chain P calibration screen")}],
  title="Chain P calibration screen: results (30 Oct 2026; provisional API screen)", title_src=S(IDN + "/2026-10-31_chainP_calibration/results.md", "# Chain P calibration screen: results"),
  question="Do the four Chain P characters (polished/casual x flatterer/candid) come out as designed when the project's story writer writes stories with them, for the L+2 and L-2 corpora?",
  question_src=S(IDN + "/2026-10-31_chainP_calibration/design.md", "## 1. Question"), date="2026-10-30", date_src=S(IDN + "/2026-10-31_chainP_calibration/results.md", "# Chain P calibration screen: results"),
  lane="ideation subagent", lane_src=S(IDN + "/2026-10-31_chainP_calibration/design.md", "Owner: a subagent working for the ideation session"), run_state="done", status="provisional",
  status_reason="'A provisional SCREEN': API writer, n = 12 specs per character; the binding gate is the later local 120-spec pilot.",
  status_src=S(IDN + "/2026-10-31_chainP_calibration/design.md", "A provisional SCREEN"), verification_note="none found",
  files={"design_spec": IDN + "/2026-10-31_chainP_calibration/design.md", "analysis": IDN + "/2026-10-31_chainP_calibration/results.md", "other_key_md": [IDN + "/2026-10-31_chainP_calibration/gates_v4.md", IDN + "/2026-10-31_chainP_calibration/gates_v5.md"]},
  raw_dirs=[IDN + "/2026-10-31_chainP_calibration/runs"], _scan=False, organisms_as_named=["Qwen3.6-27B via OpenRouter (writer)"], scenario_set=["stories"], readouts=["judge rubric"], claims=["ChainP"],
  tony_links=[{"what": "specs copied from Tony's e04_content_voice r02; Tony's build_specs.py logic rewritten; Tony's N corpus as drop-rate comparison", "src": S(IDN + "/2026-10-31_chainP_calibration/design.md", "copied from `e04_content_voice:e04/r02/compressed/`")}],
  led_to=["S041"], notes="Folder dated 31 Oct but design/results dated 30 Oct. Link to sw041 (Chain P P1 pairs/corpora) is map-level.",
  conflicts=[{"what": "folder name says 2026-10-31; design and results say 30 Oct", "a": S(IDN + "/2026-10-31_chainP_calibration/design.md", "written 30 Oct 2026"), "b": IDN + "/2026-10-31_chainP_calibration"}])
E(id="X-handover-vetting-1031", series="check", kind="check", folder=None, folder_name="2026-10-31_handover_vetting_ideation-11.md",
  aliases=[{"name": "ideation-11 vetting of ideation-10's handover", "src": S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "# Vetting ideation-10's handover")}],
  title="Vetting ideation-10's handover (Tony's findings, our runs, §5 ideas)", title_src=S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "# Vetting"),
  question="Check ideation-10's handover claims about Tony's E12 findings and our runs against the primary files.", question_src=S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "**What was vetted:**"),
  date="2026-10-31", date_src=S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "_ideation-11, 31 Oct 2026"), lane="ideation-11", lane_src=S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "_ideation-11, 31 Oct 2026"),
  run_state="done", status="not recomputed", status_reason="Written check against primary files; no new measurement.", status_src=None, verification_note="none found",
  files={"other_key_md": [IDN + "/2026-10-31_handover_vetting_ideation-11.md", IDN + "/2026-10-31_handover_to_ideation-11_tony_and_runs.md"]}, claims=["Methods"],
  tony_links=[{"what": "Tony E12 tasks checked: m94, m110, m103, m108b/c, m123, m126, m101, m138, m127, m118, m5, m12; ledger B26, B36", "src": S(IDN + "/2026-10-31_handover_vetting_ideation-11.md", "### Checked OK against Tony's files")}],
  attaches_to=["S059", "S062", "S061"], notes="Section 0 records E4 state (sw059, sw062 finished without analysis.md at the time).")

# ---------------------------------------------------------------- codex ideation-12 checks
cdx_common = dict(series="check", date="2026-10-31", lane="Codex ideation-12", run_state="done", status="not recomputed", verification_note="none found")
E(id="X-codex-headline-provenance", kind="check", attaches_to=["S020", "S038", "S061"], folder=None, folder_name="2026-10-31_headline_provenance_sw020_sw038_sw061.md",
  title="Headline provenance check: sw020, sw038, sw061", title_src=S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "# Headline provenance check"),
  question="Trace the headline numbers of sw020, sw038 and sw061 (G1) to their stored JSON/report/recompute records and frozen-source hashes.",
  question_src=S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "Read-only audit"), date_src=S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "Recorded **2026-10-31T22:15:33Z**"),
  lane_src=S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "# Headline provenance check"), status_reason="Provenance verification, 'not a new independent replication'.",
  status_src=S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "This is provenance verification"),
  files={"other_key_md": [CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md"]}, claims=["Methods", "A", "C", "Levers"],
  corrects=[{"id": "S061", "what": "G1's 'common battery at T 1' sentence is a documentation error: frozen harness uses T=0.7 (health block T=1.0)", "src": S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "G1’s “common battery at T 1”")},
            {"id": "S020", "what": "primary ladder is an20.json -> P_all, not the old bc/report.txt; bars use 55 jointly kept scenarios, contrasts 61", "src": S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "sw020’s primary ladder")},
            {"id": "S038", "what": "controls match cumulative change near 1x in two prespecified bands only; removal specificity not supported", "src": S(CDX + "/2026-10-31_headline_provenance_sw020_sw038_sw061.md", "sw038’s checked induction points")}],
  notes="Codex notes are maps: confirm corrections in the primary analysis.md before applying (not done here).", **cdx_common)
E(id="X-codex-sw072-review", kind="review", attaches_to=["S072"], folder=None, folder_name="2026-10-31_ideation-12_sw072_independent_review.md",
  title="sw072 independent review: what the band results establish", title_src=S(CDX + "/2026-10-31_ideation-12_sw072_independent_review.md", "# sw072 independent review"),
  question="What do sw072's band-removal results establish (late band vs A/B asymmetry; mid band onset vs selection)?", question_src=S(CDX + "/2026-10-31_ideation-12_sw072_independent_review.md", "## Main conclusion"),
  date_src=S(CDX + "/2026-10-31_ideation-12_sw072_independent_review.md", "_Checked 2026-10-31T23:15:39Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_sw072_independent_review.md", "_Checked"),
  status_reason="Re-aggregation of stored labels; 'This check is not blind'.", status_src=S(CDX + "/2026-10-31_ideation-12_sw072_independent_review.md", "This check is **not blind**"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_sw072_independent_review.md"]}, claims=["C"], tony_links=[{"what": "Tony's band circuit (sw072 tests it on our organisms)", "src": S(L, "## sprint_work/072")}], **cdx_common)
E(id="X-codex-sw075-redteam", kind="review", attaches_to=["S075"], folder=None, folder_name="2026-10-31_sw075_census_independent_redteam.md",
  title="sw075 census re-read: independent write-up red-team", title_src=S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "# sw075 census re-read"),
  question="Does sw075's write-up support 'persona carries more' than conduct?", question_src=S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "**Keep the predictive result"),
  date_src=S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "Recorded **2026-10-31T23:15:15Z**"), lane_src=S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "# sw075"),
  status_reason="Compared stored estimates; no recomputation.", status_src=S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "No experiment, model inference"),
  files={"other_key_md": [CDX + "/2026-10-31_sw075_census_independent_redteam.md"]}, claims=["A", "B"],
  corrects=[{"id": "S075", "what": "withdraw the calibrated-null argument against conduct-only (reliability upper bound used in the wrong direction)", "src": S(CDX + "/2026-10-31_sw075_census_independent_redteam.md", "**Keep the predictive result")}], **cdx_common)
E(id="X-codex-sw077-sw073-review", kind="review", attaches_to=["S077", "S073"], folder=None, folder_name="2026-10-31_ideation-12_sw077_sw073_review.md",
  title="ideation-12 — independent reading of landed sw077 and sw073", title_src=S(CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md", "# ideation-12"),
  question="Independent reading and non-blind recount of sw077 and sw073.", question_src=S(CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md", "Recorded 2026-10-31T23:16:27Z"),
  date_src=S(CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md", "Recorded 2026-10-31T23:16:27Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md", "# ideation-12"),
  status_reason="Recount not blind.", status_src=S(CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md", "not blind"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_sw077_sw073_review.md"]}, claims=["ChainP", "A"],
  notes="sw073 under a provenance hold (exact history-writer source missing).", **cdx_common)
E(id="X-codex-new-results-review", kind="review", attaches_to=["S072", "S073", "S075", "S077"], folder=None, folder_name="2026-10-31_ideation-12_new_results_review.md",
  title="New results review — sw072, sw073, sw075, sw077", title_src=S(CDX + "/2026-10-31_ideation-12_new_results_review.md", "# New results review"),
  question="Check newly finished runs sw072, sw073, sw075, sw077 and their verification records.", question_src=S(CDX + "/2026-10-31_ideation-12_new_results_review.md", "User asked to check newly finished runs"),
  date_src=S(CDX + "/2026-10-31_ideation-12_new_results_review.md", "Recorded 2026-10-31T23:16:29Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_new_results_review.md", "# New results review"),
  status_reason="Reading + offline recount of saved outputs.", status_src=S(CDX + "/2026-10-31_ideation-12_new_results_review.md", "No new training"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_new_results_review.md"]}, claims=["ChainP", "C", "A", "B"], **cdx_common)
E(id="X-codex-figure-audit", kind="check", attaches_to=["S020", "S056", "S062", "S042", "S038", "S055"], folder=None, folder_name="2026-10-31_ideation-12_figure_draft_audit.md",
  title="ideation-12 — audit of six existing figure drafts", title_src=S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "# ideation-12"),
  question="Do ideation-11's six draft deck figures reproduce their source tables, and what must change before use?", question_src=S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "**Verdict: all six are usable"),
  date_src=S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "2026-10-31T22:13:28Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "# ideation-12"),
  status_reason="Read-only audit of figure drafts.", status_src=S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "Read-only audit"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_figure_draft_audit.md"]}, html_local=[IDN + "/plots/figures_preview.html"],
  report_artifacts=["https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL"], report_src=S(M, "https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL"), claims=["Methods"],
  corrects=[{"id": "X-figure-drafts-ideation11", "what": "v6 mislabelled quote pair, v4 wrong control CI, v1 missing denominator, v2 verdicts omitted", "src": S(M, "draft figures: a mislabelled quote pair")}],
  notes="The artifact is ideation-11's private preview page that still shows the uncorrected drafts (mistakes.md).", **cdx_common)
E(id="X-codex-tony-reconciliation", kind="review", folder=None, folder_name="2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md",
  title="Tony E12 reconciliation for ideation-12 — PRIVATE", title_src=S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "# Tony E12 reconciliation"),
  question="Reconcile Tony's E12 branch results with ours for the write-up (v2 use, band circuit, random draws, m94 vs sw039).", question_src=S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "## What changes the write-up"),
  date_src=S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "_Checked at 2026-10-31T22:10:22Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "Read-only breadth pass"),
  status_reason="Read-only reconciliation.", status_src=S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "Read-only breadth pass"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md"]}, claims=["A", "C", "Methods"], attaches_to=["S039", "S071", "S072"],
  tony_links=[{"what": "E12 v2_core/v2_set/v2_bands; m135, m94, m136, m137, m141, m134", "src": S(CDX + "/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md", "## What changes the write-up")}],
  notes="Marked PRIVATE in its title: keep out of anything shared without the user's say.", **cdx_common)
E(id="X-codex-late-result-notes", kind="review", folder=None, folder_name="2026-11-01_late_result_notes.md", attaches_to=["S080", "S057"],
  title="Late results that change the presentation", title_src=S(CDX + "/2026-11-01_late_result_notes.md", "# Late results"),
  question="Which late results (sw080 training clamp, reader recomputation, Tony's new commits) change the presentation?", question_src=S(CDX + "/2026-11-01_late_result_notes.md", "Read-only review"),
  date_src=S(CDX + "/2026-11-01_late_result_notes.md", "Reviewed 2026-11-01T00:32:18Z"), lane_src=S(CDX + "/2026-11-01_late_result_notes.md", "# Late results"),
  status_reason="Read-only review; adds no new bootstrap.", status_src=S(CDX + "/2026-11-01_late_result_notes.md", "Read-only review"),
  files={"other_key_md": [CDX + "/2026-11-01_late_result_notes.md"]}, claims=["Levers", "C"], **{**cdx_common, "date": "2026-11-01"},
  notes="Being appended during this inventory (timestamps after 01:00Z); re-read before integration. Reader recomputation section concerns sw057 (map; not confirmed here).")
E(id="X-audit-docx-chains", series="check", kind="audit", folder="/workspace/useles", folder_name="useles",
  aliases=[{"name": "external audit doc / 'audit and gated experiment chains'", "src": S(AUD + "/audit_ideation_fix_myself.md", "https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y")},
           {"name": "the docx S1-S10 chains (31 Oct run-sheet sessions); not the 28 Oct plan's S1-S9", "src": S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "**The numbering is not stable across dates.**")},
           {"name": "Chain letters A/B/C/D/DL/E/G/H/K/P", "src": S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "Chain letters A/B/C/D/DL/E/G/H/K/P")}],
  title="Story imprinting on Qwen3.6-27B: audit and gated experiment chains", title_src=S("/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt", "Story imprinting on Qwen3.6-27B: audit and gated experiment chains"),
  question="Audit of the evidence (as of 29-31 Oct) and gated experiment chains / a 31 Oct run sheet of ten parallel sessions S1-S10.",
  question_src=S("/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt", "31 Oct: start here (run sheet for parallel sessions)"), date="2026-10-29/31", date_src=S("/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt", "Oct 29, 2026"),
  lane="external audit session (another session; reviewed by audit-1 and codex-1)", lane_src=S(AUD + "/notes/2026-10-30_full_session_history.md", "### 1.4 Review of the external audit doc"),
  run_state="done", status="not recomputed", status_reason="Plan/audit document; its own checks 'with two read-only verification agents'.", status_src=S("/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt", "Checked against sprint_work 6c7e5ec"), verification_note="none found",
  files={"other_key_md": ["/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains.docx", "/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains v2 (31 Oct).docx", "/workspace/useles/Story_imprinting_plan_2026-10-31_corrected.docx",
                          "/workspace/useles/audit_and_gated_experiment_chains_v1_29oct.txt", "/workspace/useles/audit_and_gated_experiment_chains_v2_31oct.txt", "/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt",
                          AUD + "/notes/2026-10-30_external_doc_v2_export.md", AUD + "/notes/2026-10-31_external_doc_v3_export.md", CDX + "/2026-10-31_ideation-12_docx_chain_map.md", AUD + "/notes/external_reviews/2026-10-29_external_audit_doc_EP6DD8YiF1UZvvaHsJY37y_rev29.md"]},
  report_artifacts=["https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y"], report_src=S(AUD + "/audit_ideation_fix_myself.md", "https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y"),
  claims=["Methods", "ChainP", "Levers"], tony_links=[{"what": "S8 N/NB persona capture uses Tony's e08 N/NB", "src": S("/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt", "S8: drop the second-seed retrain")}],
  led_to=["S028", "S029", "S030", "S031", "S032", "S033", "S035", "S036", "S040", "S041", "S042", "S043", "S044", "S045", "S055", "S060", "S061"],
  notes="Chain-to-experiment map (Codex, a map not a source): S1->sw032; S2->sw028/031/054/038; S3->sw029/034/038/057; S4->sw030/056/062/058/078/079; S5->sw033/066 (premise sw024); S6->sw026 (B0; B1+ dropped); S7->sw035; S8->sw036/040 PartA/044; S9->sw040/041/042/076/077; S10->sw043/045/055/060/061/062/064 (" + S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "## S1–S10: what actually ran") + "). These chain labels should be added as aliases on the numbered cards. Not parsed beyond the text copies.")
E(id="X-codex-docx-chain-map", kind="review", attaches_to=["X-audit-docx-chains"], folder=None, folder_name="2026-10-31_ideation-12_docx_chain_map.md",
  title="ideation-12: the 31 Oct docx chains, mapped to executed work", title_src=S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "# ideation-12: the 31 Oct docx chains"),
  question="Map the docx S1-S10 sessions and fresh ideas to executed experiments and their landing state.", question_src=S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "_Checked 2026-10-31T22:13:04Z"),
  date_src=S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "_Checked 2026-10-31T22:13:04Z"), lane_src=S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "# ideation-12"),
  status_reason="Read-only mapping.", status_src=S(CDX + "/2026-10-31_ideation-12_docx_chain_map.md", "Read-only mapping"),
  files={"other_key_md": [CDX + "/2026-10-31_ideation-12_docx_chain_map.md"]}, claims=["Methods"],
  notes="Records the sw071 numbering collision (071_one_protocol_battery vs 071_polish_mechanism_v2) and that sw078/sw079 are E4 follow-ups in E5's range.", **cdx_common)

# ---------------------------------------------------------------- codex-1 (25-30 Oct)
E(id="X-codex1-1025-audits", series="check", kind="audit", folder=None, folder_name="NS/_sessions/codex/notes (25 Oct audits)",
  aliases=[{"name": "codex-1 independent audits", "src": S(M, "(found by codex-1)")}],
  title="Independent audit: internals and exploration, 2026-10-25 (+ organisms/replay and cross-model/rival audits)", title_src=S(CDX1 + "/2026-10-25_audit_internals_exploration.md", "# Independent audit"),
  question="Read-only evidence audits of the reproduction series (001-018) and the 25 Oct explorations.", question_src=S(CDX1 + "/2026-10-25_audit_internals_exploration.md", "**Scope.**"),
  date="2026-10-25", date_src=S(CDX1 + "/2026-10-25_audit_internals_exploration.md", "2026-10-25"), lane="codex-1", lane_src=S(M, "(found by codex-1)"),
  run_state="done", status="not recomputed", status_reason="Read-only audits.", status_src=None, verification_note="none found",
  files={"other_key_md": [CDX1 + "/2026-10-25_audit_internals_exploration.md", CDX1 + "/2026-10-25_audit_organisms_replay.md", CDX1 + "/2026-10-25_audit_crossmodel_rivals.md", CDX1 + "/2026-10-25_redteam_ideation6_next_runs.md", CDX1 + "/2026-10-25_019_review_and_run_order.md"]},
  claims=["Methods", "Organisms"], attaches_to=["R001", "R002", "R005", "R006", "R008", "R009", "R010", "R011", "R012", "R013", "R014", "R015", "R016", "R017", "R018", "X-1025-parent-exploration", "X-automated-grad-awareness"],
  corrects=[{"id": "X-1025-parent-exploration", "what": "cross-model and marginal-correlation conclusions narrowed", "src": S(M, "Parent exploration upgraded cross-model")},
            {"id": "R005", "what": "judgments counted as conversations (verified)", "src": S(M, "005 analysis counts judgments as conversations")},
            {"id": "R018", "what": "prose overstates known-answer preservation (verified)", "src": S(M, "018 prose overstates known-answer")}],
  notes="Grouped: three 25 Oct audit notes plus the ideation-6 red-team and the proposed-019 review (planning critiques).")
E(id="X-codex1-sw001-reviews", series="check", kind="review", attaches_to=["S001"], folder=None, folder_name="NS/_sessions/codex/notes (26 Oct sw001 reviews)",
  title="sprint_work/001: independent initial assessment (+ Part 2, Parts 1/3, Parts 4-6 reviews)", title_src=S(CDX1 + "/2026-10-26_sw001_initial_results_assessment.md", "# sprint_work/001: independent initial assessment"),
  question="Independent read-only reviews of sw001's parts.", question_src=S(CDX1 + "/2026-10-26_sw001_initial_results_assessment.md", "Read-only review"),
  date="2026-10-26", date_src=S(CDX1 + "/2026-10-26_sw001_initial_results_assessment.md", "26 October 2026"), lane="codex-1", lane_src=S(CDX1 + "/2026-10-26_sw001_initial_results_assessment.md", "Codex-1"),
  run_state="done", status="not recomputed", status_reason="Reviews.", status_src=None, verification_note="none found",
  files={"other_key_md": [CDX1 + "/2026-10-26_sw001_initial_results_assessment.md", CDX1 + "/2026-10-26_sw001_steering_review.md", CDX1 + "/2026-10-26_sw001_map_geometry_review.md", CDX1 + "/2026-10-26_sw001_association_history_trigger_review.md"]},
  claims=["A", "C", "Methods"],
  corrects=[{"id": "S001", "what": "D29 attributes different histories to seeds that are actually matched; Stage-0 steering parity passes while hook-shift flag fails; Part 3 normalization not specified before its rule", "src": S(M, "sprint_work/001 D29 attributes different histories")}])
E(id="X-codex1-external-doc-review", series="check", kind="review", attaches_to=["X-audit-docx-chains"], folder=None, folder_name="NS/_sessions/codex/notes (29-30 Oct docx reviews)",
  title="Review of the external audit and gated experiment chains", title_src=S(CDX1 + "/2026-10-29_external_audit_doc_review.md", "# Review of the external audit"),
  question="Review the external audit docx and recommend updates.", question_src=S(CDX1 + "/2026-10-29_external_audit_doc_review.md", "Source:"),
  date="2026-10-29/30", date_src=S(CDX1 + "/2026-10-30_results_delta_and_docx_updates.md", "# Results delta"), lane="codex-1", lane_src=S(CDX1 + "/2026-10-29_external_audit_doc_review.md", "# Review"),
  run_state="done", status="not recomputed", status_reason="Review.", status_src=None, verification_note="none found",
  files={"other_key_md": [CDX1 + "/2026-10-29_external_audit_doc_review.md", CDX1 + "/2026-10-30_results_delta_and_docx_updates.md"]}, claims=["Methods"])

# ---------------------------------------------------------------- audit session (29-30 Oct)
E(id="X-audit1-evidence-review-1029", series="check", kind="audit", folder=AUD, folder_name="audit",
  aliases=[{"name": "audit session 'fixing myself' (audit-1)", "src": S(AUD + "/notes/2026-10-29_audit_session_summary.md", "# What the 29 Oct audit session")},
           {"name": "Navigator", "src": S(AUD + "/notes/2026-10-29_audit_session_summary.md", "**Navigator**")}, {"name": "Evidence-base doc", "src": S(AUD + "/notes/2026-10-29_audit_session_summary.md", "**Evidence-base doc**")}],
  title="What the 29 Oct audit session (\"fixing myself\") found and decided", title_src=S(AUD + "/notes/2026-10-29_audit_session_summary.md", "# What the 29 Oct audit session"),
  question="What can be trusted after 7 days: six independent reviewers plus re-checks of load-bearing numbers against raw files; a navigator of every experiment and verdict.",
  question_src=S(AUD + "/notes/2026-10-30_full_session_history.md", "the user had lost track after 7 days"), date="2026-10-29/30", date_src=S(AUD + "/notes/2026-10-29_audit_session_summary.md", "# What the 29 Oct audit session"),
  lane="audit-1", lane_src=S(AUD + "/STATUS.md", "audit-1"), run_state="done", status="not recomputed", status_reason="Audit with targeted re-checks; no recompute of the audit itself.", status_src=S(AUD + "/notes/2026-10-30_full_session_history.md", "re-checked load-bearing numbers against raw files"),
  verification_note="none found", files={"readme": AUD + "/STATUS.md", "other_key_md": [AUD + "/audit_ideation_fix_myself.md", AUD + "/notes/2026-10-29_audit_session_summary.md", AUD + "/notes/2026-10-30_full_session_history.md", AUD + "/notes/2026-10-30_handoff_to_ideation_spec.md", AUD + "/notes/artifact_data/our_experiments.md", AUD + "/notes/artifact_data/hypotheses.md", AUD + "/notes/artifact_data/tony_branches.md"]},
  raw_dirs=[AUD + "/notes/audit_scripts"], html_local=[AUD + "/notes/navigator/story_imprinting_navigator.html"],
  report_artifacts=["https://claude.ai/artifact/NUtXbVGZ9xs9itU7tpSHKJ", "https://claude.ai/artifact/GZCdS3NeChGeWgogRrKB7n"], report_src=S(AUD + "/notes/2026-10-29_audit_session_summary.md", "**Navigator**"),
  claims=["Methods", "A"], tony_links=[{"what": "Tony's branches in the navigator data", "src": S(AUD + "/notes/2026-10-29_audit_session_summary.md", "**Navigator**")}],
  corrects=[{"id": "S006", "what": "sw006's random-plane controls rescaled against their own run's state (4-18x stronger)", "src": S(M, "sw006: the random-plane controls were rescaled")},
            {"id": "S009", "what": "sw009 C4 free-reply readout ran without random-control arms; partial C4 v1 read before controls' displacement checked", "src": S(M, "sw009 C4: the free-reply readout ran without random-control arms")}],
  led_to=["S009"], notes="Wrote the sw009 brief. Navigator v2 corrected sw006. The audit session also built eval materials for Tony's adapters (separate infra entry).")
E(id="X-audit-eval-builds-1030", series="check", kind="infra", folder=AUD, folder_name="audit (eval_elite_confusion, eval_sfl, tony_elite_rerun, tony_sfl_runs)", _scan=False,
  title="Elite-university / confusion-trigger evaluation (+ SFL evaluation materials, Tony run specs)", title_src=S(AUD + "/eval_elite_confusion/README.md", "# Elite-university"),
  question="Build evaluation materials for Tony's elite-university (confusion trigger) and SFL adapters, and the specs/data handed to Tony for those runs.", question_src=S(AUD + "/eval_elite_confusion/README.md", "_Built 30 Oct 2026 by the audit session"),
  date="2026-10-30", date_src=S(AUD + "/eval_elite_confusion/README.md", "_Built 30 Oct 2026"), lane="audit session", lane_src=S(AUD + "/eval_sfl/README.md", "Built 30 Oct 2026 by the audit session"),
  run_state="done", status="not recomputed", status_reason="Instrument build.", status_src=None, verification_note="none found",
  files={"readme": AUD + "/eval_elite_confusion/README.md", "other_key_md": [AUD + "/eval_sfl/README.md", AUD + "/tony_elite_rerun/SPEC_elite_rerun_for_Tony.md", AUD + "/tony_sfl_runs/SPEC_sfl_for_Tony.md"]},
  raw_dirs=[AUD + "/eval_elite_confusion", AUD + "/eval_sfl", AUD + "/tony_elite_rerun", AUD + "/tony_sfl_runs"], claims=["Methods"], attaches_to=["S050", "S051", "S019"],
  tony_links=[{"what": "Tony's elite rerun and SFL organisms (HF Same0620/si-study-organisms)", "src": S(AUD + "/STATUS.md", "Same0620/si-study-organisms")}],
  corrected_by=[{"id": "S019", "what": "the audit's confusion-trigger prompt lets the fixed user line refer to reply content the model may not produce (found by sw019-scripts)", "src": S(M, "The audit's confusion-trigger prompt")}],
  led_to=["S050", "S051"])

# ---------------------------------------------------------------- grandfather 25 Oct
E(id="X-grandfather-md-audit-1025", series="check", kind="check", folder="/workspace/grandfather", folder_name="grandfather",
  aliases=[{"name": "grandfather markdown audit (workflow wf_eae8582a-72e)", "src": S("/workspace/grandfather/md_audit_2026-10-25.md", "wf_eae8582a-72e")}],
  title="Markdown audit: what is out of date, what is wrong, what to change", title_src=S("/workspace/grandfather/md_audit_2026-10-25.md", "# Markdown audit"),
  question="Read-only audit of 7 document groups and 11 experiment folders whose numbers were re-checked against raw result files, with a refuting verifier for every high/medium finding.",
  question_src=S("/workspace/grandfather/md_audit_2026-10-25.md", "18 audit units"), date="2026-10-25", date_src=S("/workspace/grandfather/md_audit_2026-10-25.md", "_grandfather, 25 Oct 2026"), lane="grandfather (old grandfather session)", lane_src=S("/workspace/grandfather/md_audit_2026-10-25.md", "_grandfather, 25 Oct 2026"),
  run_state="done", status="not recomputed", status_reason="Audit whose findings were attacked by separate verifiers; findings JSON holds verdicts.", status_src=S("/workspace/grandfather/md_audit_2026-10-25.md", "attacked by a separate Opus verifier"),
  verification_note="\"every high- or medium-severity finding was then attacked by a separate Opus verifier told to refute it\" (" + S("/workspace/grandfather/md_audit_2026-10-25.md", "attacked by a separate Opus verifier") + ")",
  files={"readme": "/workspace/grandfather/md_audit_2026-10-25.md", "other_key_md": []}, raw_dirs=["/workspace/grandfather/md_audit_findings_2026-10-25.json"], _scan=False, claims=["Methods"],
  attaches_to=["R001", "R005", "R006", "R008", "R009", "R010", "R011", "R012", "R013", "R014", "R016"],
  corrects=[{"id": "R009", "what": "'88% garbled' wording withdrawn: 'semantically degraded', judge-dependent", "src": S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "**DeepSeek (009) at T 1.**")},
            {"id": "R008", "what": "'87-114% of the association' is an average over two bridges; 'largely retained, bridge-dependent'", "src": S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "**008's \"87–114% of the association\".**")},
            {"id": "R005", "what": "'0 of 1,600' pooled across both controls; each control has 800 T 0.7 conversations", "src": S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "**005 control counts.**")}],
  notes="Which 11 experiment folders were audited is in md_audit_findings_2026-10-25.json (not parsed here); attaches_to is approximate.")
E(id="X-grandfather-reviews-1025", series="check", kind="review", folder="/workspace/grandfather", folder_name="grandfather",
  title="Neel Sprint review: status against the spec, the most interesting result, and what to do next", title_src=S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "# Neel Sprint review"),
  question="Status of the sprint against the V6.1 spec and Neel's doc on 25 Oct, plus the 014/017/018 update (with a judge-free lexical recount of 014).",
  question_src=S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "This is a read-only review"), date="2026-10-25", date_src=S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "_grandfather session, 25 Oct 2026"),
  lane="grandfather (old grandfather session)", lane_src=S("/workspace/grandfather/neel_sprint_review_2026-10-25.md", "_grandfather session"), run_state="done", status="not recomputed",
  status_reason="Reviews; the morning update includes the grandfather's own lexical recount of 014 that matches the reported numbers.", status_src=S("/workspace/grandfather/update_2026-10-25_morning.md", "a judge-free lexical recount of 014"),
  verification_note="\"a judge-free lexical recount of 014 ... This matches the reported +0.515 / +0.160 and +0.555 / +0.165\" (" + S("/workspace/grandfather/update_2026-10-25_morning.md", "a judge-free lexical recount of 014") + ")",
  files={"readme": "/workspace/grandfather/neel_sprint_review_2026-10-25.md", "other_key_md": ["/workspace/grandfather/update_2026-10-25_morning.md", "/workspace/grandfather/where_we_are_vs_spec_2026-10-25.md", "/workspace/grandfather/spec_and_pilot_take_2026-10-25.md", "/workspace/grandfather/ideas_from_neel_doc_2026-10-25.md"]},
  claims=["Methods", "D", "Organisms"], attaches_to=["R014", "R017", "R018", "R001", "R008", "R009"],
  tony_links=[{"what": "pilot artifact (Tony's/pilot work) read for the spec take", "src": S("/workspace/grandfather/spec_and_pilot_take_2026-10-25.md", "the pilot artifact")}],
  notes="Grouped: review + morning update + where-we-are + spec/pilot take + ideas-from-Neel's-doc (planning). The pilot artifact URL in spec_and_pilot_take is a pilot (Tony-side) record, not ours.")

# ---------------------------------------------------------------- ideation figure drafts (target of codex audit)
E(id="X-figure-drafts-ideation11", series="check", kind="infra", folder=IDN + "/plots", folder_name="plots",
  title=None, title_src=None, question="ideation-11's draft deck figures (v1-v6) and preview page.", question_src=S(M, "draft figures: a mislabelled quote pair"),
  date="2026-10-31", date_src=S(M, "draft figures: a mislabelled quote pair"), lane="ideation-11", lane_src=S(M, "draft figures: a mislabelled quote pair"),
  run_state="done", status="not recomputed", status_reason="Figure drafts; audited by Codex with defects found; fix owed by the write-up session.", status_src=S(M, "**Fix:** owed by the write-up session"),
  verification_note="audited: \"all six are usable starting points; none should enter the final deck unchanged\" (" + S(CDX + "/2026-10-31_ideation-12_figure_draft_audit.md", "**Verdict: all six are usable") + ")",
  files={}, raw_dirs=[IDN + "/plots/viz"], report_artifacts=["https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL"], report_src=S(M, "https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL"),
  claims=["Methods"], corrected_by=[{"id": "X-codex-figure-audit", "what": "v6 quote pair, v4 CI, v1 denominator, v2 verdicts", "src": S(M, "draft figures: a mislabelled quote pair")}],
  attaches_to=["S020", "S056", "S062", "S042", "S038", "S055"])

# ---------------------------------------------------------------- assemble
gen = subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip()
# sanity
ids = [e["id"] for e in EXPS]
dups = sorted({i for i in ids if ids.count(i) > 1})
if dups:
    PROBLEMS.append(f"duplicate ids: {dups}")

problems_fixed = [
    "Ledger is being edited live (line numbers shifted by ~11 lines during this pass); ledger_line values and NS/research_ledger.md:N citations were resolved at build time and should be re-resolved by the build script.",
    "No ledger entries exist for: the 25, 26 and 27 Oct explorations (by design: 'not an experiment of record'), any ideation/Codex/audit/grandfather check, or the RUNS infra folders; ledger_line is null for those.",
    "RUNS/box3_sw002 and RUNS/box4_sw002 have no README; purpose inferred from contents.",
    "RUNS/merged/hd-A_s0 has no README or date; linked to the 25 Oct round-5 merge by path name only.",
    "RUNS/recompute_E4_late/RECOMPUTE.md gives no date or author lane in its header.",
    "The hs-A/B_s0 sarcastic adapters ('the user's public sarcastic adapters') are not explicitly linked to the 26 Oct external-agent task prompt in any file read.",
    "_sessions/ideation/notes/2026-10-29_pilot_branches/ (synthesis of Tony's pilot branches), tony_e12_snapshot_1833/ and the Codex 1 Nov registries (models_and_naming, non_e12_registry, tony_coverage_registry) were not given cards: they are maps of Tony's work and naming, not our checks; the Tony inventory agent should cover them.",
    "ideation up-to-speed pages (2026-10-26_ideation7_up_to_speed.html, 2026-10-27_ideation8_review.html) and the 712pXLPxwUghbyJmLhphVr progress page are session reports, not checks; only the ideation-8 review page is attached (to X-ideation8-hypotheses-checks).",
    "_sessions/executor/notes/E1_report/E1_report.html is a lane report (E1), not a check; left to the numbered-experiment agents.",
    "The 28 Oct Neel-question plan's S1-S9 (_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md) is a different namespace from the docx S1-S10; not given a card.",
]
out = {"part": "ours_X", "generated_utc": gen, "sources_read": sorted(SOURCES), "experiments": EXPS,
       "problems": problems_fixed + PROBLEMS,
       "questions_for_user": [
           "Should the 28 Oct exploration be shown as one card with X0-X9 sub-cards (as built here), or should only X8 (and perhaps X4, X7, X9) get top-level cards?",
           "The overnight cross-cutting checks are one ledger entry; this file splits them into X-cumctrl, X-scenqc and X-bf16-header-token0. Keep the split?",
           "Were the user's public sarcastic adapters (senku21x/story-imprinting-qwen36-27b-sarcastic, hs-A/B_s0) trained by the external agent from the 26 Oct task prompt?",
           "Should Codex 'PRIVATE' notes (Tony reconciliation) appear in the archive at all?",
       ]}
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("entries", len(EXPS), "problems", len(out["problems"]))
for p in PROBLEMS:
    print("PROBLEM", p)
