#!/usr/bin/env python3
"""Read-only inventory builder for S036..S082 (writes ONE json). Reads files only."""
import json, os, re, subprocess, sys

NS = "/workspace/Neel Sprint"
RUNS = "/workspace/runs_executor"
TONY = "/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony"
SW = NS + "/experiments/sprint_work"
OUT = "/workspace/grandfather/unified_artifact/inventory/ours_S036_S082.json"
LEDGER = NS + "/research_ledger.md"

problems = []
sources_read = set()
_cache = {}


def abbr(p):
    for k, v in (("TONY", TONY), ("RUNS", RUNS), ("NS", NS)):
        if p.startswith(v + "/") or p == v:
            return k + p[len(v):]
    return p


def unabbr(p):
    for k, v in (("TONY", TONY), ("RUNS", RUNS), ("NS", NS)):
        if p.startswith(k + "/"):
            return v + p[len(k):]
    return p


def lines(path):
    path = unabbr(path)
    if path not in _cache:
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                _cache[path] = f.read().split("\n")
        except Exception as e:
            problems.append(f"could not read {abbr(path)}: {e}")
            _cache[path] = []
        sources_read.add(abbr(path))
    return _cache[path]


def S(path, pattern, start=0, end=None):
    """path:line of first line containing pattern."""
    L = lines(path)
    end = len(L) if end is None else end
    for i in range(start, end):
        if pattern in L[i]:
            return f"{abbr(unabbr(path))}:{i+1}"
    problems.append(f"pattern not found in {abbr(unabbr(path))}: {pattern!r}")
    return f"{abbr(unabbr(path))}:?"


# ---------------- ledger index ----------------
LL = lines(LEDGER)
heads = [(i, l) for i, l in enumerate(LL) if l.startswith("## ")]


def ledger_entry(num):
    pat = re.compile(r"^## sprint_work/%s\b" % num)
    for k, (i, l) in enumerate(heads):
        if pat.match(l):
            end = heads[k + 1][0] if k + 1 < len(heads) else len(LL)
            return i, end, l
    return None


def LE(num, pattern):
    e = ledger_entry(num)
    if not e:
        problems.append(f"no ledger entry for {num} (pattern {pattern!r})")
        return None
    return S(LEDGER, pattern, e[0], e[1])


def LH(num):
    e = ledger_entry(num)
    return f"NS/research_ledger.md:{e[0]+1}" if e else None


def folder_of(num):
    for d in sorted(os.listdir(SW)):
        if d.startswith(num + "_") and os.path.isdir(os.path.join(SW, d)):
            return d
    return None


def raw_dirs(num, extra=()):
    out = []
    for d in sorted(os.listdir(RUNS)):
        if re.fullmatch(r"sw%s[a-z]?(_[A-Za-z0-9]+)?" % num, d):
            out.append("RUNS/" + d)
    for x in extra:
        if os.path.exists(unabbr(x)) and x not in out:
            out.append(x)
    return out


def html_local(folder, rdirs):
    out = []
    roots = [os.path.join(SW, folder)] if folder else []
    for root in roots:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                if f.endswith(".html"):
                    p = os.path.join(dp, f)
                    try:
                        sz = os.path.getsize(p)
                    except OSError:
                        continue
                    if sz > 5 * 1024:
                        out.append({"path": abbr(p), "bytes": sz})
    for r in rdirs:  # raw dirs: shallow (depth <= 3) to avoid huge trees
        base = unabbr(r)
        try:
            res = subprocess.run(["timeout", "20", "find", base, "-maxdepth", "3", "-name", "*.html", "-size", "+5k",
                                  "-printf", "%p\t%s\n"], capture_output=True, text=True)
            for ln in res.stdout.splitlines():
                p, sz = ln.split("\t")
                out.append({"path": abbr(p), "bytes": int(sz)})
        except Exception as e:
            problems.append(f"html find failed in {r}: {e}")
    return out


ART = re.compile(r"https://claude\.ai/artifact/[A-Za-z0-9]+")


def artifacts(num, folder):
    found = {}
    e = ledger_entry(num)
    if e:
        for i in range(e[0], e[1]):
            for m in ART.findall(LL[i]):
                found.setdefault(m, []).append(f"NS/research_ledger.md:{i+1}")
    if folder:
        for fn in ("README.md", "analysis.md"):
            p = os.path.join(SW, folder, fn)
            if os.path.exists(p):
                for i, l in enumerate(lines(p)):
                    for m in ART.findall(l):
                        found.setdefault(m, []).append(f"{abbr(p)}:{i+1}")
    return found


def parse_heading(num):
    e = ledger_entry(num)
    if not e:
        return None, None, None
    h = e[2]
    m = re.search(r"\((\d{4}-\d{2}-\d{2}(?:/\d{2}-\d{2})?|\d{4}-\d{2}-\d{2}/\d{2}),\s*([^;)]*)", h)
    title = h[3:]
    date = m.group(1) if m else None
    lane = m.group(2).strip() if m else None
    return title, date, lane


# ---------------- per-experiment records ----------------
def F(folder, fn):
    return f"NS/experiments/sprint_work/{folder}/{fn}"


EXPS = []


def add(num, **kw):
    kw["num"] = num
    EXPS.append(kw)


L = LE  # shorthand

# ===== 036 =====
add("036",
    aliases=[("sw034 Part D", "LH"), ("S8's forced channel", "LH"), ("docx S8 (N / NB persona capture), 31 Oct run-sheet session", "MAP:chain")],
    question="Does the default turn-1 lean of Tony's e08 organisms (N / NB / X / XB) on every channel show S8's ≥ +10-point pair lean toward the polished character, whose forced channel was untested?",
    q=("L", "- **Why:**"),
    run_state="done", status="gate failed",
    status_reason="NOT SCORED under the frozen rule: forced onset 0.29–0.59 < 0.70; with no history the bridge does not supply the habit (main readout not interpretable; descriptive leans reported).",
    status_src=("L", "**NOT SCORED**"),
    vnote=("blind-recomputed (ledger heading 'Result (blind-recomputed)'); analysis: 'The blind recompute ... matches every number above'", ("F", "analysis.md", "The blind recompute")),
    organisms=["N", "NB", "X", "XB", "parent"],
    scenario_set=["v2 turn-1"], readouts=["forced 'By the way,'", "forced 'Fun fact:'", "free (2,048)", "STRICT regex"],
    turn="turn 1, no history", claims=["ChainP", "Methods"], dead_end=True,
    tony=[("Tony's e08 organisms N / NB / X / XB (HF Same0620/si-study-organisms e08-*)", ("L", "**What:** N / NB / X / XB"))],
    notes="Gate is the frozen onset bar (forced onset ≥ 0.70); recorded as 'gate failed' because the decision rule could not be scored. 'The forced bridge is not a turn-1 instrument for these organisms' (ledger).",
)

# ===== 037 =====
add("037",
    aliases=[("E14 R03 header mismatch (Part 2; Tony's E14 report label)", "LH"), ("sw055's Next", ("F", "design_spec.md", "sw055's"))],
    question="Does routing in the no-flip runs (mix A s0, B s2) use the same own-turn variable (asT) as hd, and why does B s2's lens read bee at the header while it routes weakly (E14 R03)?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="forced readout blind-recomputed; free readout (beside) not recomputed.",
    status_src=("L", "**Result (forced blind-recomputed):**"),
    vnote=("Result (forced blind-recomputed)", ("L", "**Result (forced blind-recomputed):**")),
    parts=[("Part 1 (asT / r1 swaps in mix A s0, B s2)", "verified", "forced decides; blind recompute matches every forced number; free not recomputed", ("F", "analysis.md", "The free readout was not recomputed")),
           ("Part 2 (B s1 <-> B s2 header transplant, E14 R03)", "verified", "forced blind-recomputed", ("F", "analysis.md", "The blind recompute"))],
    organisms=["mix A s0", "B s2", "B s1", "hdA0", "hdB0"],
    scenario_set=["v1-64"], readouts=["forced 'By the way,'", "free (2,048)", "activations/probe", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history (sw008's 64 scripts)", claims=["C", "D"], dead_end=False,
    tony=[("Tony's E14 R03 lens reading of B s2 (plan docx 'E14 R03 mismatch')", ("F", "design_spec.md", "E14 R03 mismatch"))],
    notes="Scenario set from design_spec ('sw008's 64 scripts').",
)

# ===== 038 =====
add("038",
    aliases=[("user brief A (E2b)", "MAPREADME:038"), ("combined E2b report", ("L", "combined E2b report"))],
    question="Do the S3 mechanism results (whole-state header patch, r1, asT, c1, equal-size removal), which rested on sw008's 5 old scenarios, hold on evaluation set v2?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="every headline blind-recomputed (ledger heading).",
    status_src=("LH",),
    vnote=("every headline blind-recomputed", ("LH",)),
    parts=[("Part 0 (whole-state header patch, positive control)", "verified", "blind recompute of every headline in both parts", ("F", "analysis.md", "Verification: blind recompute")),
           ("Part 1 (r1 / asT / c1 / removal on sw021's 61-script v2 G3)", "verified", "blind recompute of every headline in both parts", ("F", "analysis.md", "Verification: blind recompute"))],
    organisms=["hdA0", "hdB0"],
    scenario_set=["v2"], readouts=["forced 'By the way,'", "free (2,048)", "activations/probe", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history (v2 G2 / G3)", claims=["C", "D"], dead_end=False,
    tony=[],
)

# ===== 039 =====
add("039",
    aliases=[("user's brief C", ("L", "the user's brief C")), ("Tony's E12 m94 ladder (Part 1)", ("L", "Tony's E12 m94 ladder")), ("asT dose sweep (Part 2)", "LH")],
    question="Is the habit choice one conduct dimension or two, does an apology reset it, and is asT a graded dial?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="both parts blind-recomputed (ledger heading).",
    status_src=("LH",),
    vnote=("both parts blind-recomputed", ("LH",)),
    parts=[("Part 1 (conduct ladder)", "verified", "both parts blind-recomputed (heading)", ("LH",)),
           ("Part 2 (asT dose sweep)", "verified", "blind recompute matched every number and reading", ("F", "analysis.md", "## Part 2"))],
    organisms=["hdA0", "hdB0", "parent"],
    scenario_set=["v2"], readouts=["free (2,048)", "forced 'By the way,'", "activations/probe", "judge rubric", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history", claims=["A", "C"], dead_end=False,
    tony=[("Tony's E12 m94 conduct ladder (sources sha256-copied to RUNS/sw039/tony_e12_8682829c/)", ("L", "Tony's sources sha256-copied")),
          ("TONY/e12_habit_mechanism/e12/queue/tasks/m94_conduct_ladder", ("F", "design_spec.md", "m94_conduct_ladder")),
          ("Tony's E12 m82 (named in design_spec title)", ("F", "design_spec.md", "m94 / m82"))],
)

# ===== 040 =====
add("040",
    aliases=[("Chain P premise (S8)", "LH"), ("P0 one-protocol targets (Part B)", "LH"), ("Chain P", "LH")],
    question="Does Tony's finding that e08-N / NB's default declines benign turn-1 requests (~40%) hold with our two judges, at 2,048 tokens, on the v2 held-out scenarios against a measured parent rate; and (P0) which character wins under one protocol for six pairs?",
    q=("F", "design_spec.md", "### Question"),
    run_state="done", status="provisional",
    status_reason="Part A verified; Part B (P0) is written 'provisional (pirate pending)' because the pirate pair's targets were to come from sw070; no later update to sw040's analysis was found.",
    status_src=("F", "analysis.md", "provisional (pirate pending)"),
    vnote=("Part A: 'every number in the table below was recomputed blind'; Part B: 'recomputed blind ... match to rounding'; 'Not verified independently: the predictor values (P0 agent only)'", ("F", "analysis.md", "**Verification:** every number")),
    parts=[("Part A (S8 premise: turn-1 declines)", "verified", "premise holds (verified)", ("F", "analysis.md", "**Verification:** every number")),
           ("Part B (P0 one-protocol targets + predictors)", "provisional", "pirate pending sw070; predictors not verified independently", ("F", "analysis.md", "Not verified independently"))],
    organisms=["e08-N", "e08-NB", "X", "XB", "parent", "hd", "ps", "V / VB", "U"],
    scenario_set=["v2 turn-1", "v2"], readouts=["judge rubric", "free (2,048)", "STRICT regex"],
    turn="turn 1, no history (Part A); own-history 5-turn chats (Part B)", claims=["ChainP", "B", "D"], dead_end=False,
    tony=[("e08-N / e08-NB (Tony's E08 R09 Part C finding)", ("F", "design_spec.md", "E08 R09 Part C")),
          ("Tony's catalog winner for N / NB", ("F", "analysis.md", "polished refuser (Tony's catalog)"))],
    conflicts=[("sw040 Part B still says 'pending sw070' for the pirate pair, but sw070 is done and a default-cell copy was made for E3", ("F", "analysis.md", "pending sw070"), ("L070", "Default-cell copy for E3"))],
)

# ===== 041 =====
add("041",
    aliases=[("Chain P P1", "LH"), ("S9 Chain P (docx; map)", "MAP:chain")],
    question="Can we say before training which character's conduct the default Assistant will copy, and does polish (register) carry conduct? (P1 builds the pairs, readouts, corpora and the frozen forecast)",
    q=("F", "design_spec.md", "## Question"),
    run_state="done", status="verified",
    status_reason="forecast frozen and pushed before training; 'independent recompute identical'.",
    status_src=("F", "analysis.md", "independent recompute identical"),
    vnote=("independent recompute identical", ("F", "analysis.md", "independent recompute identical")),
    organisms=["parent (forecast)", "Tony's N (port check)"],
    scenario_set=["R-flaw"], readouts=["judge rubric", "other: R-capitulation (failed its judge known-answer; exploratory)"],
    turn="other: instrument / corpus build", claims=["ChainP", "B", "Methods"], dead_end=False,
    tony=[("generator port check vs Tony's N corpus", ("L", "port check PASS vs Tony's N")),
          ("Tony's pilot repo clone RUNS/sw041/tony_pilot.git and tony_r09_personas.json (ls)", ("RUNS", "RUNS/sw041/tony_pilot.git"))],
    corrected_by=[("self", "pre-registered correctness rule failed correct answers; first capitulation judge called hedges capitulation (caught before any organism)", ("MIST", "sw041 readouts: a pre-registered correctness rule"))],
    organisms_produced=[],
    notes="No organisms trained here; corpora (4 × ≈7,600 stories + matched-main) built for sw042 (RUNS/sw041/full, RUNS/sw041/gates_matched; HF senku21x/chainP-flattery-story-corpora per STATUS_E3).",
)

# ===== 042 =====
add("042",
    aliases=[("Chain P P2", "LH"), ("S9 (docx)", ("L", "S9:")), ("main / mirror / honest / F-only / matched-main", "LH")],
    question="S9: can we say before training which character's conduct the default copies, and does polish carry conduct?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="pre-registered verdict 'inconclusive'; blind recompute: every point estimate identical (covers the first eight organisms; matched-main noted separately in analysis).",
    status_src=("L", "Blind recompute: every point estimate identical"),
    vnote=("Blind recompute: every point estimate identical", ("L", "Blind recompute: every point estimate identical")),
    organisms=["mainA", "mainB", "mirrorA", "mirrorB", "honestA", "honestB", "F-only", "matched-main A / B", "parent"],
    scenario_set=["R-flaw", "v2"], readouts=["judge rubric", "STRICT regex", "free (2,048)"],
    turn="R-flaw items (turn 1); habit routing on own-history 5-turn chats", claims=["ChainP", "B", "Organisms"], dead_end=False,
    tony=[("Tony's P22 / P23 persona prompts used in the conversation readout", ("F", "design_spec.md", "P22 and P23"))],
    organisms_produced=[{"name": n, "path": f"RUNS/sw042/train/{n}/final"} for n in
                        ["mainA", "mainB", "mirrorA", "mirrorB", "honestA", "honestB", "Fonly", "matchedA", "matchedB"]],
    organisms_produced_note=("HF senku21x/chainP-qwen36-27b-flattery-organisms (STATUS_E3); node copies /root/runs/sw042/train/<run>/final (E5 registry)", ("FX", "NS/_sessions/executor/STATUS_E3.md", "chainP-qwen36-27b-flattery-organisms")),
    notes="Analysis says the blind recompute covers the first eight organisms; matched-main's flag rates were checked separately (see analysis line cited in status).",
)

# ===== 043 =====
add("043",
    aliases=[("sw061 Lever 2", "LH"), ("S10 redirect", "LH"), ("red_hdA0_dis / red_hdB0_dis / red_hdB0_help / red_N_cas / red_N_help (run names)", None), ("Amendment A dose-response", ("L", "Dose-response (Amendment A"))],
    question="docx S10: if the Assistant's own personality decides which character it imprints on, does making it curt / casual through a second-stage chat fine-tune move routing to the other character?",
    q=("L", "- **Why:**"),
    run_state="done", status="not recomputed",
    status_reason="written up (analysis.md, S10 report); no blind recompute or reimplementation recorded.",
    status_src=("L", "**Folder:** experiments/sprint_work/043_s10_redirect/"),
    vnote=("none found", None),
    parts=[("Main (60 steps)", "not recomputed", "gate FAILS (A and B); N 'no move'", ("L", "gate FAILS (A and B)")),
           ("Amendment A dose-response (post hoc, steps 15/30/45/60 + hdA0 + helpful control)", "not recomputed", "post hoc", ("L", "Dose-response (Amendment A"))],
    organisms=["hdA0", "hdB0", "N", "hdA0 + dismissive", "hdB0 + dismissive", "hdB0 + helpful", "N + casual", "N + helpful", "hdA0 + helpful (Amendment A)"],
    scenario_set=["v2", "v2 turn-1", "stories"], readouts=["forced 'By the way,'", "story enactment", "judge rubric", "STRICT regex"],
    turn="turn 1, no history (eval61 turn-1 readout); supplied histories (eval61); stories", claims=["Levers", "Organisms"], dead_end=False,
    corrected_by=[("self (E3)", "an untraced agent number ('leaks into 36%') removed / corrected in 043 analysis", ("MIST", "an agent's untraced number copied into an analysis")),
                  ("self (E3)", "red_A's in-job known-answer gate skipped by a wrong reference path; computed afterwards (+0.858)", ("MIST", "sw043 red_A's in-job known-answer gate"))],
    corrects=[],
    organisms_produced=[{"name": n, "path": f"RUNS/sw043/train/{n}/final", "checkpoints": [f"RUNS/sw043/train/{n}/step015", f"RUNS/sw043/train/{n}/step030", f"RUNS/sw043/train/{n}/step045"]}
                        for n in ["red_hdA0_dis", "red_hdA0_help", "red_hdB0_dis", "red_hdB0_help", "red_N_cas", "red_N_help"]],
    organisms_produced_note=("HF senku21x/s10-levers-qwen36-27b-redirect-authorship (+ N arms) per STATUS_E3; RUNS/sw043/train/red_hdA0_dis_superseded576 is an earlier hdA0 dismissive run (576-row set) superseded by D10's 849 two-way set", ("FX", "NS/_sessions/executor/STATUS_E3.md", "s10-levers-qwen36-27b-redirect-authorship")),
    notes="'gate FAILS' here is the pre-registered success criterion (rival share ≥ 0.3 with enactment within 5 pts), not an instrument gate; the readout ran and is interpretable. sw064 reads these checkpoints.",
)

# ===== 044 =====
add("044",
    aliases=[("S8 habit-free N/NB control", "LH"), ("hfN44 (sw071 registry name)", ("FX", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md", "hfN44")), ("sw044's habit-free N", ("FX", "NS/experiments/sprint_work/071_one_protocol_battery/design_spec.md", "sw044's habit-free N"))],
    question="docx: does conduct capture need the habit at all?",
    q=("L", "- **Why:**"),
    run_state="done", status="not recomputed",
    status_reason="written up; values 'traced from raw labels' but no blind recompute / reimplementation recorded.",
    status_src=("L", "traced from raw labels"),
    vnote=("none found (ledger: 'traced from raw labels')", ("L", "traced from raw labels")),
    organisms=["HF (habit-free N)", "N", "parent"],
    scenario_set=["v2 turn-1"], readouts=["judge rubric"],
    turn="turn 1, no history", claims=["ChainP", "Organisms"], dead_end=False,
    tony=[("Tony's two habit-free baseline cells of N (plainspoken-baseline + refuser-baseline)", ("L", "Tony's two habit-free baseline cells"))],
    organisms_produced=[{"name": "HF (sw044 habit-free N)", "path": "RUNS/sw044/train/HF/final", "checkpoints": ["RUNS/sw044/train/HF/step025", "RUNS/sw044/train/HF/step062"]}],
    organisms_produced_note=("HF senku21x/chainP-qwen36-27b-flattery-organisms:sw044_habitfree_N/final (E5 registry hfN44)", ("FX", "RUNS/day_2026-10-31_E5/adapters_registry.json", "sw044_habitfree_N")),
)

# ===== 045 =====
add("045",
    aliases=[("sw061 Lever 1", "LH"), ("S10 G2 authorship", "LH"), ("G2 doc A / B, G2 userturn A / B (organism names)", None), ("g2docA / g2docB / g2utA / g2utB (sw071 registry names)", ("FX", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md", "g2docA / g2docB"))],
    question="docx S10 G2: in our SFT format every story is an Assistant turn; does the default inherit because the Assistant 'wrote' the characters?",
    q=("L", "- **Why:**"),
    run_state="done", status="not recomputed",
    status_reason="written up (analysis.md, S10 report); no blind recompute recorded (pulls, gates and renders verified only).",
    status_src=("L", "**Folder:** experiments/sprint_work/045_s10_g2_authorship/"),
    vnote=("none found", None),
    organisms=["doc A", "doc B", "userturn A", "userturn B", "hdA0", "hdB0"],
    scenario_set=["v2", "v2 turn-1", "stories"], readouts=["forced 'By the way,'", "story enactment", "STRICT regex"],
    turn="supplied histories + turn 1 (eval61)", claims=["Levers", "B", "Organisms"], dead_end=False,
    organisms_produced=[{"name": n, "path": f"RUNS/sw045/{n}/final"} for n in ["g2_doc_A", "g2_doc_B", "g2_userturn_A", "g2_userturn_B"]],
    organisms_produced_note=("HF senku21x/s10-levers-qwen36-27b-redirect-authorship:g2_doc_A/final etc. (E5 registry)", ("FX", "RUNS/day_2026-10-31_E5/adapters_registry.json", "g2_doc_A/final")),
    notes="'gate FAILS in all 4 runs' is the pre-registered hypothesis test (transfer drops ≥ 50%), not an instrument gate.",
)

# ===== 050 =====
add("050",
    aliases=[("Table 9 ladder / paper App. C.6 SFL ladder", ("FX", "NS/experiments/sprint_work/README.md", "Table 9 ladder")), ("lists-only follow-up = Amendment 1", ("L", "Lists-only follow-up"))],
    question="Whether Qwen3.6-27B trained on the paper's helpful-vs-SFL stories reproduces App. C.6's graded-similarity ladder (habit choice follows how much the current persona resembles each trained character).",
    q=("F", "design_spec.md", "What this experiment is trying to establish"),
    run_state="done", status="verified",
    status_reason="main run blind-recomputed 108/108; lists-only follow-up blind-recomputed.",
    status_src=("L", "blind-recomputed 108/108"),
    vnote=("blind-recomputed 108/108", ("L", "blind-recomputed 108/108")),
    parts=[("Main ladder", "verified", "blind-recomputed 108/108", ("L", "blind-recomputed 108/108")),
           ("Lists-only follow-up (Amendment 1)", "verified", "Amendment 1 frozen before output; blind-recomputed", ("L", "Lists-only follow-up"))],
    organisms=["sflA", "sflB", "parent"],
    scenario_set=["v2"], readouts=["free (2,048)", "STRICT regex", "judge rubric", "other: learning gate on stories"],
    turn="turn 3, own history (5-turn chats)", claims=["A", "D", "Organisms"], dead_end=False,
    tony=[("Tony's SFL organisms sfl-set{A,B}-lr5e4-bs32-s0 (HF Same0620/si-study-organisms)", ("FX", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md", "sfl-set{A,B}-lr5e4-bs32-s0"))],
    corrected_by=[("self (E1)", "frozen STRICT label misses French-written animal facts (conservative bias)", ("MIST", "sw050: the frozen habit label"))],
)

# ===== 051 =====
add("051",
    aliases=[("Tony's elite-university organisms (e13 otter / octopus)", "LH")],
    question="Does the default Assistant resemble the elite-educated helper more, so the elite animal dominates by default and naming an elite school shifts the habit?",
    q=("F", "design_spec.md", "**Hypothesis:**"),
    run_state="done", status="gate failed",
    status_reason="learning gate FAILED in all four cells (onset learned, binding not learned); chat stage not run; 'Dropped; not a readout of the elite effect.'",
    status_src=("L", "gate FAILED in all four cells"),
    vnote=("Result (blind-recomputed): gate FAILED", ("L", "blind-recomputed")),
    organisms=["e13-oo-rich-lr1e4-bs16-eliteOtters-s0", "e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0", "parent"],
    scenario_set=["stories", "v2"], readouts=["story enactment", "STRICT regex"],
    turn="stories (learning check)", claims=["Organisms"], dead_end=True,
    tony=[("Tony's e13 elite adapters (HF Same0620/si-study-organisms)", ("F", "design_spec.md", "e13-oo-rich-lr1e4-bs16-eliteOtters-s0"))],
)

# ===== 052 =====
add("052",
    aliases=[("the cheapest leakage test", "LH"), ("c1 (ctrlB0's d_self; reused as 'c1' in sw029 / sw038)", ("L", "(c1)"))],
    question="Does a habit-free conduct direction (ctrlB0's d_self) at the reply-start header, set in hd, induce the rival habit at ≥ 50% of hd's own d_self, beating cumulative-size-matched random edits?",
    q=("F", "design_spec.md", "**Hypothesis (H):**"),
    run_state="done", status="verified",
    status_reason="free primary blind-recomputed; forced pilot not blind-checked.",
    status_src=("L", "Result (blind-recomputed; causal influence"),
    vnote=("Result (blind-recomputed; causal influence of the edit, level 4)", ("L", "Result (blind-recomputed; causal influence")),
    parts=[("free replies (primary)", "verified", "blind recompute", ("F", "analysis.md", "**Blind recompute.**")),
           ("forced pilot", "provisional", "provisional: not independently recomputed", ("F", "analysis.md", "provisional: not independently recomputed"))],
    organisms=["hdA0", "hdB0", "ctrlB0 (direction source)"],
    scenario_set=["v1-64"], readouts=["free (2,048)", "forced 'By the way,'", "forced 'Random animal fact: the' (crow-biased)", "activations/probe"],
    turn="turn 3, supplied (parent-written) history (sw008's 64 scripts)", claims=["C"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 01:30", "the 'Random animal fact: the' bridge adopted in sw052's design is crow-biased", ("MIST", "is crow-biased in the bee/crow family"))],
    notes="User caveat beside the verdict: c1's target comes from hd's decision-bearing donor states.",
)

# ===== 053 =====
add("053",
    aliases=[("d_t1 dial", "LH")],
    question="Is d_t1 (contemptuous − default system prompt at turn 1) the turn-1 conduct coordinate, such that clamping it makes the default take the rival's habit dose-dependently (and does ctrlB0's d_t1 do the same)?",
    q=("F", "design_spec.md", "**Hypothesis:**"),
    run_state="done", status="verified",
    status_reason="blind recompute confirms every headline; both remove cells untestable (bar above positive control).",
    status_src=("F", "analysis.md", "A **blind recompute** confirms every headline number"),
    vnote=("A blind recompute confirms every headline number", ("F", "analysis.md", "A **blind recompute** confirms every headline number")),
    parts=[("induce cells", "verified", "NOT A DIAL", ("L", "NOT A DIAL in all 8 cells")),
           ("remove cells", "gate failed", "untestable: baselines below the 0.15 bar", ("L", "Both remove cells are untestable"))],
    organisms=["hdA0", "hdB0", "ctrlB0 (direction source)"],
    scenario_set=["v1-64"], readouts=["free (2,048)", "activations/probe", "STRICT regex"],
    turn="turn 1, no history (system prompt varied)", claims=["C"], dead_end=True,
    corrected_by=[("mistakes.md 31 Oct 02:35", "bar set above the positive control: remove cells untestable", ("MIST", "E1 frozen rules not checked against what their readout can reach"))],
    notes="Scenario set: sw011's 64 sw005 scripts at turn 1 (design_spec).",
)

# ===== 054 =====
add("054",
    aliases=[("A3 at matched dose", "LH"), ("sw016's size-vs-direction test", "LH")],
    question="Is sw016's 'stories do not read d_self' result about edit size or direction (dose confound), and does the story direction's chat effect survive cumulative-size-matched controls?",
    q=("F", "design_spec.md", "What this experiment is trying to establish"),
    run_state="done", status="verified",
    status_reason="blind-recomputed (ledger).",
    status_src=("L", "Result (blind-recomputed)"),
    vnote=("Result (blind-recomputed)", ("L", "Result (blind-recomputed)")),
    organisms=["hdA0", "hdB0"],
    scenario_set=["stories", "other: chat side (sw016's chat contexts)"], readouts=["forced 'By the way,'", "forced 'Random animal fact: the' (crow-biased)", "story enactment", "activations/probe"],
    turn="stories (held-out cuts) and chat turn 3", claims=["C"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 01:30", "raf bridge (beside in sw054) is crow-biased", ("MIST", "adopted in E1's sw052 / sw054 / sw068 designs"))],
    notes="Box C (RTX PRO 6000) run; E1 STATUS flags box comparability as an open question.",
)

# ===== 055 =====
add("055",
    aliases=[("S10 replication", "LH")],
    question="Does routing by the Assistant's own conduct hold on the other trained runs, or was it one lucky run / a damaged-model artefact?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="verdicts verified by blind recompute.",
    status_src=("L", "verdicts verified by blind recompute"),
    vnote=("verdicts verified by blind recompute", ("L", "verdicts verified by blind recompute")),
    organisms=["hdA0", "hdB0", "A s1", "A s2", "B s1", "B s2", "B s0 rep", "mix010 A s0", "mix010 A s1", "mix010 B s0", "mix025 A s0", "mix 1:1 A s0", "parent"],
    scenario_set=["v2"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history (sw019 G2 / G3)", claims=["A", "D"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 08:57", "adapter-active gate could not pass when floor was 0; failed full job sat 23 min (no number affected)", ("MIST", "sw055: an adapter-active gate"))],
)

# ===== 056 =====
add("056",
    aliases=[("Neel's question in plain form", ("L", "Neel's question in plain form")), ("turn-1 own-reply test", "LH")],
    question="At turn 1, does the habit follow the conduct of the Assistant's own reply so far ('it decides after it knows what it has said') rather than a stored default self?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="verified by blind recompute (forced readout).",
    status_src=("L", "verified by blind recompute"),
    vnote=("Result (verified by blind recompute; forced readout ...)", ("L", "verified by blind recompute")),
    organisms=["hdA0", "hdB0", "mix010 A s1", "parent"],
    scenario_set=["v2 turn-1"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="turn 1, prefilled opening", claims=["A"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 12:41", "a 'no think tags' output gate failed complete runs (sw056 / sw058 / sw059 prep code)", ("MIST", "A \"no think tags\" output gate"))],
    notes="Amendments 1–2 (mix010 A s1 scored; quoted arm).",
)

# ===== 057 =====
add("057",
    aliases=[("readers at S3's sites", "LH"), ("c1 SAE / c2 running conduct meter / c3 oracle lens + MAEM", "LH")],
    question="What is asT (a conduct variable, the decision, or animal content), before building on it in training (G1)?",
    q=("L", "- **Why:**"),
    run_state="done", status="provisional",
    status_reason="c1 / c2 blind-recomputed 1 Nov; lens / MAEM not recomputed (ledger heading).",
    status_src=("LH",),
    vnote=("c1/c2 blind-recomputed 1 Nov; lens/MAEM not recomputed", ("LH",)),
    parts=[("c1 (L42 SAE)", "gate failed", "L42-only edit carries 0.10 of the effect, so the gate failed and the SAE edit is untestable; c1 numbers blind-recomputed", ("L", "so the gate failed")),
           ("c2 (running conduct meter on sw056 cache)", "verified", "blind-recomputed 1 Nov; wording corrected", ("F", "analysis.md", "Corrected 1 Nov after the blind recompute")),
           ("c3 oracle lens", "not recomputed", "lens/MAEM not recomputed", ("LH",)),
           ("c3 MAEM", "not recomputed", "lens/MAEM not recomputed", ("LH",))],
    organisms=["parent", "hdA0", "hdB0"],
    scenario_set=["v1-64", "v2 turn-1"], readouts=["activations/probe", "judge rubric"],
    turn="turn 1, prefilled opening (c2, sw056 cache); supplied histories (c1 / c3)", claims=["C", "Methods"], dead_end=False,
    corrected_by=[("mistakes.md 2026-11-01 00:15", "c2: 'asT does not predict the decision' read from a one-sided null; reworded to 'weak and changes sign across organisms'", ("MIST", "sw057 c2: \"asT does not predict the decision\""))],
    notes="Scenario set per ideation run map (map, sw057 c1 / c3 on v1-64; c2 on sw056's v2 cache); c2's v2 source confirmed in the ledger ('sw056's cached reply-token projections').",
)

# ===== 058 =====
add("058",
    aliases=[("spec 11 idea 6", "LH"), ("role-label token", "LH")],
    question="Is 'knows what it has said' role-tag bookkeeping, or self-recognition from what the text is?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed (ledger).",
    status_src=("L", "Result (blind-recomputed; one run per assignment; v1 scripts)"),
    vnote=("Result (blind-recomputed; one run per assignment; v1 scripts)", ("L", "Result (blind-recomputed; one run per assignment; v1 scripts)")),
    organisms=["hdA0", "hdB0", "parent"],
    scenario_set=["v1-64"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="one prior turn (role label varied), then the prohibition + question", claims=["A"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 12:41", "'no think tags' output gate copied into E4 jobs", ("MIST", "A \"no think tags\" output gate"))],
)

# ===== 059 =====
add("059",
    aliases=[("spec 11 idea 3", "LH"), ("many-shot in-context twin", "LH")],
    question="Given k training stories in its context, does the untrained parent learn the story rule, and then apply it to itself as the Assistant by its own conduct?",
    q=("F", "design_spec.md", "## Question"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("L", "Result (blind-recomputed)"),
    vnote=("Verified by blind recompute", ("F", "analysis.md", "Verified by blind recompute")),
    organisms=["parent (k = 0/8/32/64 stories in context)", "hdA0", "hdB0"],
    scenario_set=["v2 turn-1", "v1-64", "stories"], readouts=["forced 'By the way,'", "story enactment", "STRICT regex"],
    turn="turn 1, no history; turn 3 supplied (sw005) history; stories — all after k in-context stories", claims=["A", "B"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 12:41", "'no think tags' output gate", ("MIST", "A \"no think tags\" output gate"))],
)

# ===== 060 =====
add("060",
    aliases=[("spec 11 idea 7", "LH"), ("checkpoint order", "LH")],
    question="Does routing by the Assistant's own conduct arrive with the character habits (one rule) or later (a separate computation)?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("L", "Result (blind-recomputed; one run per assignment)"),
    vnote=("Result (blind-recomputed; one run per assignment)", ("L", "Result (blind-recomputed; one run per assignment)")),
    organisms=["hdA0 checkpoints 25/62/125/188/250", "hdB0 checkpoints 25/62/125/188/250", "parent (= step 0)"],
    scenario_set=["stories", "v2 turn-1", "v1-64"], readouts=["forced 'By the way,'", "free (2,048)", "story enactment", "STRICT regex"],
    turn="stories; turn 1, no history; turn 3 supplied (sw005) histories", claims=["A", "Organisms"], dead_end=False,
)

# ===== 061 =====
add("061",
    aliases=[("Lever 3", "LH"), ("G1 containment", "LH"), ("S10 training levers", ("FX", "NS/experiments/sprint_work/README.md", "S10 training levers")), ("eval61 (its battery, reused by sw043 / sw045 / sw064)", ("L064", "eval61's battery")), ("S_A / S_B / N_A / N_B (G1 organism names)", ("L080", "S_A / N_A / S_B / N_B"))],
    question="Is S3's conduct coordinate at the Assistant's own turns (asT) a training-time channel: if no module can read it during story training, does the habit stop routing by the Assistant's own conduct, with story learning matched?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind recompute: every gated estimate matches to 3 decimals. The frozen primary gate fails in both assignments on the lean component (conduct-gap components pass); the lean half is not interpretable. Integrator may prefer 'gate failed' (see questions).",
    status_src=("L", "Blind recompute: every gated estimate matches"),
    vnote=("Blind recompute: every gated estimate matches to 3 decimals", ("L", "Blind recompute: every gated estimate matches")),
    parts=[("conduct-gap components", "verified", "pass; blind-recomputed", ("L", "The conduct-gap components pass")),
           ("default-lean component", "gate failed", "frozen primary gate fails on the lean component; lean half not interpretable", ("L", "The frozen primary gate fails in both assignments"))],
    organisms=["S (asT read-clamp) A / B", "N (random clamp) A / B", "O = hdB0rep / hdA0", "O's checkpoints"],
    scenario_set=["v2", "v2 turn-1", "stories"], readouts=["forced 'By the way,'", "story enactment", "STRICT regex", "other: free replies (eval61)"],
    turn="turn 1, no history; turn 3 supplied (sw019 G2) histories; stories", claims=["Levers", "C", "Organisms"], dead_end=False,
    organisms_produced=[{"name": n, "path": f"RUNS/sw061/g1/train_{n}/final"} for n in ["S_A", "S_B", "N_A", "N_B"]],
    organisms_produced_note=("trained by sw061 G1 (Lever 3); directions RUNS/sw061/g1/asT_parent.pt", ("FX", "NS/experiments/sprint_work/081_g1_reroute_test/design_spec.md", "train_S_B/final")),
    notes="Levers 1–2 (G2 authorship, redirect) are E3's sw045 / sw043 (Amendment 1); this folder's analysis covers Lever 3 only. Next: sw080, sw081.",
    corrected_by=[("mistakes.md 31 Oct 12:56", "E4 gave E3 the sha256 of a data file still being edited (process)", ("MIST", "Gave E3 the sha256 of a data file")),
                  ("mistakes.md 2026-10-31 22:08", "analysis headers carried hand-typed times (sw061, sw064, sw078, sw079)", ("MIST", "E4 analysis headers carried hand-typed"))],
)

# ===== 062 =====
add("062",
    aliases=[("sw056 on the seed reruns", "LH")],
    question="Does sw056's turn-1 own-reply result hold on the 014 seed reruns A s1, A s2, B s1, B s2?",
    q=("F", "design_spec.md", "## Question"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("L", "Result (blind-recomputed; one run per organism)"),
    vnote=("Verified by blind recompute.", ("F", "analysis.md", "**Verified by blind recompute.**")),
    organisms=["hdA1", "hdA2", "hdB1", "hdB2", "hdA0", "hdB0"],
    scenario_set=["v2 turn-1"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="turn 1, prefilled opening", claims=["A", "D"], dead_end=False,
)

# ===== 063 =====
add("063",
    aliases=[("harm rubric on sw055's free replies", "LH")],
    question="After the Assistant's own dismissive turns, how often do the story-trained organisms write abusive or self-harm-encouraging replies, compared with the parent and their helpful-history replies?",
    q=("F", "design_spec.md", "## Question"),
    run_state="done", status="provisional",
    status_reason="headline re-counted, rest provisional.",
    status_src=("L", "headline re-counted, rest provisional"),
    vnote=("headline re-counted, rest provisional", ("L", "headline re-counted, rest provisional")),
    organisms=["12 sw055 organisms", "parent"],
    scenario_set=["v2"], readouts=["judge rubric", "other: self-harm regex"],
    turn="turn 3, supplied (sw019 G2) history", claims=["Organisms"], dead_end=False,
)

# ===== 064 =====
add("064",
    aliases=[("ideation-11 pick 1", "LH"), ("eval61's battery on sw043's checkpoints", ("L", "eval61's battery"))],
    question="Does the dismissive second stage, before it erases the imprint, make the default carry the rival habit across turns (a redirect window)?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("F", "analysis.md", "Blind recompute matched"),
    vnote=("Blind recompute matched", ("F", "analysis.md", "Blind recompute matched")),
    organisms=["sw043 dismissive / helpful checkpoints steps 15/30/45 (A and B)", "hdA0", "hdB0"],
    scenario_set=["v2", "stories"], readouts=["forced 'By the way,'", "story enactment", "STRICT regex", "other: free replies (eval61)"],
    turn="turn 3, supplied (sw019 G2 / G3) histories", claims=["Levers"], dead_end=False,
)

# ===== 065 =====
add("065",
    aliases=[("sw014 mediation", "LH")],
    question="Does the history's register (sw014 Part 1) act through the reply's own register, or directly?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed; the blind verifier found the m1 mask bug, m2 primary.",
    status_src=("L", "Result (blind-recomputed; descriptive decomposition"),
    vnote=("Verified by a blind recompute.", ("F", "analysis.md", "Verified by a blind recompute")),
    organisms=["N", "NB", "X", "XB", "V"],
    scenario_set=["v1-64"], readouts=["judge rubric", "free (2,048)"],
    turn="turn 3, supplied (parent-written) history", claims=["A", "ChainP"], dead_end=False,
    tony=[("Tony's e08 organisms via sw014 Part 1 replies", ("F", "design_spec.md", "Tony's e08 organisms"))],
    corrects=[],
    notes="CPU + judges on sw014 Part 1's 841 habit-bearing free replies. Scenario set inherited from sw014 (v1-64 per run map; map).",
)

# ===== 066 =====
add("066",
    aliases=[("sw024's think arm split", "LH"), ("docx S5 (map)", "MAP:chain")],
    question="Which part of thinking mode (template vs the organism's own planning) removes the habit's onset?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed; exploration grade, one box.",
    status_src=("L", "Result (blind-recomputed)"),
    vnote=("Label: blind.", ("F", "analysis.md", "**Label: blind.**")),
    organisms=["hdA0", "hdB0", "parent (thinking source)"],
    scenario_set=["v1-64"], readouts=["free (2,048)", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history, thinking variants", claims=["A", "Methods"], dead_end=False,
    corrected_by=[("mistakes.md 2026-10-30 22:21", "E1 design specs carried hand-typed times", ("MIST", "E1 design specs carried hand-typed"))],
)

# ===== 067 =====
add("067",
    aliases=[("H200 arms (user addition)", ("L", "H200 arms")), ("trigger-gating retest", "LH")],
    question="On v2, hdA0's default helper habit was no longer trigger-gated (sw020); with turns 1–2 supplied by the parent, is the gating back?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="headline numbers blind-verified; H200 arms blind-recomputed (UNRESOLVED).",
    status_src=("F", "analysis.md", "Headline numbers are blind-verified"),
    vnote=("Headline numbers are blind-verified", ("F", "analysis.md", "Headline numbers are blind-verified")),
    parts=[("box C main", "verified", "no frozen branch fires", ("L", "Result (blind-recomputed)")),
           ("H200 arms", "verified", "UNRESOLVED; second arm is a same-config replicate (sampler flag no-op)", ("L", "H200 arms (user, pre-approved"))],
    organisms=["hdA0", "hdB0"],
    scenario_set=["v2"], readouts=["free (2,048)", "STRICT regex", "judge rubric"],
    turn="turn 3, own history vs supplied (parent-written) turns 1–2", claims=["A", "D", "Methods"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 05:05", "the 'sampler' arm could not vary the sampler (VLLM_USE_FLASHINFER_SAMPLER no-op)", ("MIST", "sw067: the \"sampler\" arm"))],
)

# ===== 068 =====
add("068",
    aliases=[("writer vs strength", "LH")],
    question="Is the gap between organisms' own rude turns and parent-written rude turns (sw027) about the writer or about the strength of the conduct?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="blind recompute of all numbers; post-hoc matching subsets etc. not independently recomputed (provisional).",
    status_src=("L", "Result (blind-recomputed; supported for own − pw only)"),
    vnote=("Blind recompute of all numbers from the raw files", ("F", "analysis.md", "**Blind recompute** of all numbers")),
    parts=[("frozen rule + own − pw", "verified", "INCONCLUSIVE twice over; own − pw replicates", ("L", "INCONCLUSIVE")),
           ("post-hoc matching subsets, interpolation, raf counts, register regex, hostility means", "provisional", "Not independently recomputed (provisional)", ("F", "analysis.md", "Not independently recomputed"))],
    organisms=["hdA0", "hdB0"],
    scenario_set=["v2"], readouts=["free (2,048)", "forced 'By the way,'", "forced 'Random animal fact: the' (crow-biased)", "STRICT regex", "judge rubric"],
    turn="turn 3, own history vs supplied (parent-written / profile-matched) history", claims=["A", "Methods"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 01:30", "raf bridge is crow-biased (found by the sw068 analysis agent)", ("MIST", "is crow-biased in the bee/crow family")),
                  ("mistakes.md 31 Oct 02:35", "STRENGTH bound below CI half-width; fixed by Amendment 1 (6 samples)", ("MIST", "E1 frozen rules not checked against what their readout can reach"))],
    notes="Instrument finding: the 'Random animal fact: the' bridge cannot read selection.",
)

# ===== 069 =====
add("069",
    aliases=[("executor-9's small leftovers (a)–(e)", "LH"), ("sw069a / sw069b / sw069c / sw069d (raw dirs)", None)],
    question="Five leftovers: (a) does accusation or conduct route the pirate style in psA0; (b) sw018's d_self tail and story-direction projection; (c) are natural rival-habit replies ruder; (d) sw025 with 6 samples; (e) records.",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="all blind-recomputed (ledger); (b) PARTIAL by a ceiling (design error); (d) ctrlA0-on-box-C note provisional.",
    status_src=("L", "Result (all blind-recomputed)"),
    vnote=("Result (all blind-recomputed)", ("L", "Result (all blind-recomputed)")),
    parts=[("(a) psA0 accusation cross", "verified", "MIXED", ("L", "(a) **MIXED:**")),
           ("(b) sw018 tail + story direction", "gate failed", "PARTIAL by a ceiling: AUROC and shuffled null both 1.0 (design error)", ("L", "(b) **PARTIAL by a ceiling:**")),
           ("(c) sw022's converse", "verified", "PARTIAL", ("L", "(c) **PARTIAL:**")),
           ("(d) sw025 × 6 samples", "verified", "RECIPE-LEVEL; ctrlA0 lower on box C (provisional)", ("L", "(d) **RECIPE-LEVEL**")),
           ("(e) records", "verified", "update lines on the sw013 and 016 entries", ("L", "(e) 0.175 / 0.140"))],
    organisms=["psA0", "hdB0", "ctrlB0", "parent", "HSab_A_s0 / HSab_B_s0", "HS_A_clean", "ctrlA0"],
    scenario_set=["v1-64", "stories", "technical items"], readouts=["judge rubric", "activations/probe", "free (2,048)", "STRICT regex"],
    turn="(a) turn 3, supplied history (X8/sw017 scripts); (d) technical items", claims=["A", "Methods", "ChainP"], dead_end=False,
    corrected_by=[("mistakes.md 31 Oct 02:35", "sw069b test could not discriminate; sw069a CONDUCT bar from sw017 point estimate", ("MIST", "E1 frozen rules not checked against what their readout can reach"))],
    corrects=[("S013", "512-cap caveat resolved (update line on the sw013 entry)", ("L", "512-cap caveat resolved")), ("R016", "update line on the 016 entry", ("L", "update lines on the sw013 and 016 entries"))],
)

# ===== 070 =====
add("070",
    aliases=[("pirate / Shakespeare family on v2", "LH"), ("sw020 (a)'s four cells for psA0 / psB0", ("L", "sw020 (a)'s four cells"))],
    question="Does sw003 Part P's flip (default leans to the helper's style; dismissive persona to the rival's) replicate for the pirate / Shakespeare organisms on the 64 new v2 test scenarios?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed; 'The blind recomputation agrees with every headline number'.",
    status_src=("L", "Result (blind-recomputed; supported empirical claim)"),
    vnote=("The blind recomputation agrees with every headline number", ("F", "analysis.md", "The blind recomputation agrees")),
    organisms=["psA0", "psB0", "parent"],
    scenario_set=["v2"], readouts=["judge rubric", "free (2,048)", "other: pirate lexicon"],
    turn="turn 3, own history (5-turn chats)", claims=["D", "A"], dead_end=False,
    notes="Default-cell copy for E3: RUNS/day_2026-10-31_E3/sw070_pirate_v2_default_cell/ (verified). Fills sw040 Part B's pending pirate target, but sw040 was not updated.",
)

# ===== 071 =====
add("071",
    aliases=[("one protocol battery (E5's sw071)", ("F", "README.md", "one protocol battery")), ("sw071 one-protocol battery, ≈51 organisms", ("FX", "NS/experiments/sprint_work/071_one_protocol_battery/DECISIONS.md", "51 scored + parent")),
             ("NOT E2's 'sw071' (071_polish_mechanism_v2, renamed sw082)", ("MIST", "Experiment number 071 used by two lanes"))],
    question="What does every organism we have trained or borrowed do, on one evaluation set, one engine and one set of readouts?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="running", status="pending",
    status_reason="all sw071 GPU jobs DONE by 01:13 UTC 1 Nov; judging still running (table built from STRICT; audit pending); no analysis.md, no ledger entry.",
    status_src=("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "all sw071 GPU jobs DONE by 01:13"),
    vnote=("none found (in progress)", None),
    organisms="REGISTRY",
    scenario_set=["v2", "v2 turn-1", "stories", "R-flaw"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex", "judge rubric", "story enactment"],
    turn="B1 turn 1, no history; B2/B3 turn 3, supplied histories; B4 own history 5-turn chats; B5 stories", claims=["D", "A", "Organisms", "Methods"], dead_end=False,
    decision_rule=[("No verdict rule. It's a measurement table, one row per organism with CIs, plus the known-answer column.", ("F", "design_spec.md", "**No verdict rule.**")),
                   ("Known answers (gate the table): each organism with a saved value must reproduce it within its CI ... A failure stops that organism's row and is logged.", ("F", "design_spec.md", "**Known answers** (gate the table)")),
                   ("D10: pass when the saved point estimate lies inside our 95% CI on the same readout and label as the source", ("F", "DECISIONS.md", "D10 (22:01 UTC, sw071 agent): known-answer rule"))],
    tony=[("Tony's E12 adapters (HF Same0620/si-qwen36-adapters: hb_dc_s0, hc_db_s0, e12_trained/adapters/*)", ("F", "design_spec.md", "Tony's E12 adapters")),
          ("Tony's e08 N / NB / X / XB / V, SFL, hs (Same0620/si-study-organisms)", ("F", "DECISIONS.md", "hs A / B were fetched from Tony's")),
          ("t_Bdismissive / t_Bhelpful / t_Bnonefine not scored: identity unknown", ("F", "DECISIONS.md", "t_Bnonefine \"not scored: identity unknown\""))],
    conflicts=[("README says 'Status: prep'; DECISIONS shows GPU done and judging running", ("F", "README.md", "Status: prep."), ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "all sw071 GPU jobs DONE by 01:13")),
               ("STATUS_E5 (23:05) and series README still say prep/running; E5 DECISIONS D30 GPU done 01:13", ("FX", "NS/experiments/sprint_work/README.md", "`071_one_protocol_battery/`"), ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "D30 (01:17 UTC"))],
    notes="Raw RUNS/sw071 holds only E5's subfolders (smoke, G1–G6 incl. G2a/G2b/G4a/G4c/G4d splits, post*, tables*, tony_e12). E2's colliding run moved to RUNS/sw082 at 22:21 (D14). Combined E5 report v1 published with an empty sw071 slot.",
)

# ===== 072 =====
add("072",
    aliases=[("Tony's band circuit on our organisms", "LH"), ("E5's band map", None), ("band-masked LoRAs F / −M / −C1 / −C0 / −L / M / M+L", ("L", "LoRA variants with layers zeroed"))],
    question="Does conduct capture use the same band as Tony's central circuit claim (gather 24–32 → decide 32–39 → boost 56–63), made on 32 old scripts with no same-width control band?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="frozen spec, blind-recomputed, adversarially reviewed (ledger heading).",
    status_src=("LH",),
    vnote=("blind-recomputed, adversarially reviewed", ("LH",)),
    organisms=["hdA0", "hdB0", "hdB2", "mix A s0", "G2 doc A", "e08 N", "NB", "X", "Chain P mainA", "mainB", "ctrlB0", "parent"],
    scenario_set=["v2", "v2 turn-1", "R-flaw"], readouts=["forced 'By the way,'", "free (2,048)", "judge rubric", "STRICT regex"],
    turn="turn 3, supplied histories (B2 ladder); turn 1, prefilled opening (sw056); R-flaw", claims=["C", "ChainP"], dead_end=False,
    tony=[("Tony's band circuit claim (TONY/e12_habit_mechanism/e12/queue/tasks/m101_sandwich)", ("F", "design_spec.md", "m101_sandwich"))],
    corrected_by=[("mistakes.md 2026-10-31 23:08", "identity gate below vLLM noise; sample cap halved a readout; judge join key; no wrong number reported", ("MIST", "sw072: (1) an adapter-identity gate"))],
    report_extra=[("https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R", "combined E5 report v1 (sw071 slot empty); ledger still says pending", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "JnbDRuC8PCyGvkBwiJkr6R"))],
    notes="'E5's band map' is the brief's label (not found verbatim in sources).",
)

# ===== 073 =====
add("073",
    aliases=[("neither histories (n1–n4)", "LH"), ("Tony's B36 test on v2", ("F", "design_spec.md", "Tony's B36"))],
    question="Is the default 'helper unless dismissive' (one-sided) or 'resembles the helper' (graded)?",
    q=("L", "- **Why:**"),
    run_state="done", status="provisional",
    status_reason="numbers blind-recomputed twice, but the history-writer code that ran was not kept; by the node rule this blocks reporting; 'reported as provisional on provenance until the user decides'.",
    status_src=("MIST", "sw073 is reported as provisional on provenance"),
    vnote=("blind-recomputed by the agent's checker; orchestrator recompute also reproduces every rate (not fully blind)", ("LH",)),
    organisms=["hdA0", "hdB0", "hdA1", "hdA2", "hdB1", "mix A s0", "parent"],
    scenario_set=["v2"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex", "judge rubric"],
    turn="turn 3, supplied (parent-written) history", claims=["A"], dead_end=False,
    report_extra=[("https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R", "combined E5 report v1", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "JnbDRuC8PCyGvkBwiJkr6R"))],
    tony=[("Tony's B36 neither-histories finding", ("F", "design_spec.md", "Tony's B36"))],
    corrected_by=[("mistakes.md 2026-10-31 23:00", "shared writer code edited after node jobs ran; sw073 history-writer code not preserved", ("MIST", "sw073 / sw077: shared code edited"))],
)

# ===== 074 =====
add("074",
    aliases=[("zero-training rule forecast", "LH_NONE"), ("docx idea 1e", ("F", "design_spec.md", "docx idea 1e"))],
    question="Given each trained pair's explicit rule, which character does the parent file its default self under, and does that forecast which character each organism's default takes after better than trivial rules?",
    q=("F", "design_spec.md", "**Question:**"),
    run_state="running", status="pending",
    status_reason="forecast frozen 22:15 UTC and verified (blind recompute + leakage audit); scoring waits for sw071's table.",
    status_src=("FX", "NS/_sessions/executor/STATUS_E5.md", "Scoring waits for sw071"),
    vnote=("verification of the frozen forecast: blind recompute reproduces; leakage audit OUTCOME-FREE and FAITHFUL", ("F", "DECISIONS.md", "D-orch1 (22:23 UTC, executor-15)")),
    parts=[("forecast (frozen)", "verified", "sw074 verified (blind recompute matches; leakage audit outcome-free/faithful)", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "D13 (22:23 UTC")),
           ("scoring against sw071", "pending", "waits for sw071", ("F", "README.md", "scoring against sw071"))],
    organisms=["parent (with each pair's rule)"],
    scenario_set=["v2", "v2 turn-1"], readouts=["forced 'By the way,'", "judge rubric"],
    turn="turn 1, no history (B1); turn 3 supplied histories (B2)", claims=["B"], dead_end=False,
    decision_rule=[("Targets: sw071's 'which character wins' column per pair (B1 and B4 default cells), per assignment and counterbalanced.", ("F", "design_spec.md", "**Targets:**")),
                   ("Baselines: 'the helper wins', 'the more polished character wins', 'the judged-more-Assistant-like character wins'.", ("F", "design_spec.md", "**Baselines:**")),
                   ("Pass: sign agreement ≥ 80% of pair-assignments, ρ ≥ 0.6 across pairs, and the forecast beats the best trivial rule on rank error.", ("F", "design_spec.md", "**Pass:**")),
                   ("Scoring script and interpretation frozen (src/score74.py sha256 ebaed3c4…)", ("F", "DECISIONS.md", "D4 (22:01 UTC, sw074 agent)"))],
    tony=[("Tony's m131 (rank ρ 0.94) as sign of life", ("F", "design_spec.md", "Tony's m131")),
          ("TONY/e12_habit_mechanism/e12/queue/tasks/m131_base_rule_locus", None)],
    notes="No ledger entry yet. Frozen forecast: RUNS/day_2026-10-31_E5/forecast_frozen/sw074_forecast.json (sha256 bcba8e25…).",
)

# ===== 075 =====
add("075",
    aliases=[("census re-read", "LH")],
    question="Test 'own conduct, not persona identity' at 271 census roles on saved data.",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("LH",),
    vnote=("Blind-recomputed (≈23:00 UTC, workflow wf_2b79b7f6-39a)", ("F", "analysis.md", "Blind-recomputed (")),
    organisms=["hd (pooled routing from sw003 C)", "hs", "parent (Axis coordinate P1)"],
    scenario_set=["census"], readouts=["log-odds", "judge rubric", "activations/probe"],
    turn="census: parent-written turns 1–2 per role", claims=["A"], dead_end=False,
    report_extra=[("https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R", "combined E5 report v1", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "JnbDRuC8PCyGvkBwiJkr6R"))],
    notes="CPU + judges on saved sw001 / sw003 data. Reachability caveat: the frozen rule can barely reach 'conduct explains'.",
)

# ===== 076 =====
add("076",
    aliases=[("is Chain P's −47 a judge register artefact?", "LH")],
    question="Do R-flaw's judges flag casual replies more readily than polished ones, inflating 'polish carries flattery'?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("LH",),
    vnote=("Blind-recomputed (31 Oct ≈21:47 UTC)", ("F", "analysis.md", "Blind-recomputed (31 Oct")),
    organisms=["mainA", "mirrorA", "honestA (sampled sw042 replies)"],
    scenario_set=["R-flaw"], readouts=["judge rubric"],
    turn="R-flaw items (saved replies rewritten)", claims=["ChainP", "Methods"], dead_end=False,
    corrected_by=[("mistakes.md 2026-10-31 21:38", "content-check known-answer set had no null–null class; DeepSeek flaw_same defect; verdict robust", ("MIST", "sw076: the content-check known-answer set"))],
    report_extra=[("https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R", "combined E5 report v1", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "JnbDRuC8PCyGvkBwiJkr6R"))],
)

# ===== 077 =====
add("077",
    aliases=[("Chain P own-turn register (2 × 2 register × candour)", "LH")],
    question="Does the conduct capture (main −47) follow the same rule as the habit, i.e. the character the Assistant's own turns resemble?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed, adversarially checked.",
    status_src=("LH",),
    vnote=("Blind recompute: every point estimate identical.", ("L", "Blind recompute: every point estimate identical")),
    organisms=["main A/B", "matched A/B", "mirror A/B", "honest A/B", "Fonly", "parent"],
    scenario_set=["R-flaw"], readouts=["judge rubric"],
    turn="turn 3, supplied (parent-written) history before R-flaw item", claims=["ChainP", "A"], dead_end=False,
    corrected_by=[("mistakes.md 2026-10-31 23:00", "writer manifests; sw077 none (real writer jobs match)", ("MIST", "sw073 / sw077: shared code edited"))],
    report_extra=[("https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R", "combined E5 report v1", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "JnbDRuC8PCyGvkBwiJkr6R"))],
    notes="Honest clause pre-registered one-sided; two-sided reading fails on honestB.",
)

# ===== 078 =====
add("078",
    aliases=[("ideation-11 pick 2", "LH"), ("E4's sw078 (inside E5's assigned 071–079 range)", ("FX", "NS/_sessions/executor/notes/2026-10-31_E4_context.md", "note sw078/079 overlap E5's assigned 071–079 range")),
             ("NOT E5's planned sw078 'parent bee-vs-crow prior' (renamed sw083 at 01:23 UTC 1 Nov)", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "renumbered sw078→sw083"))],
    question="sw058 found 'voice, not role label'; does the content of that voice or its register carry the routing?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="blind-recomputed.",
    status_src=("F", "analysis.md", "Blind recompute matched"),
    vnote=("Blind recompute matched", ("F", "analysis.md", "Blind recompute matched")),
    organisms=["hdA0", "hdB0", "parent"],
    scenario_set=["v2"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="one prior turn (assistant / user label), then the prohibition + question", claims=["A"], dead_end=False,
    corrected_by=[("mistakes.md 2026-10-31 22:08", "hand-typed analysis header times", ("MIST", "E4 analysis headers carried hand-typed"))],
)

# ===== 079 =====
add("079",
    aliases=[("ideation-11 pick 3", "LH"), ("job 91", "LH"), ("sw079b (Amendment 1, tail-own ordering)", ("L", "Amendment 1 (sw079b")),
             ("E4's sw079 (inside E5's range)", ("FX", "NS/_sessions/executor/notes/2026-10-31_E4_context.md", "note sw078/079 overlap E5's assigned 071–079 range")),
             ("NOT E5's planned sw079 '−C0 on conduct' (renamed sw084 at 01:23 UTC 1 Nov)", ("FX", "RUNS/day_2026-10-31_E5/DECISIONS.md", "renumbered sw078→sw083"))],
    question="Does turn-1 routing scale with how much of the dismissive conduct is the Assistant's own?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="job 91 blind-recomputed; Amendment 1 (sw079b) not blind-recomputed, NEEDS_REJUDGE set.",
    status_src=("LH",),
    vnote=("job 91 blind-recomputed", ("LH",)),
    parts=[("job 91 (head-own dose series)", "verified", "Blind recompute matched", ("F", "analysis.md", "Blind recompute matched")),
           ("sw079b Amendment 1 (tail-own)", "not recomputed", "Not blind-recomputed. NEEDS_REJUDGE is set", ("F", "analysis.md", "Not blind-recomputed"))],
    organisms=["hdA0", "hdB0"],
    scenario_set=["v2 turn-1"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="turn 1, prefilled opening", claims=["A"], dead_end=False,
    corrected_by=[("mistakes.md 2026-10-31 22:08", "hand-typed analysis header times", ("MIST", "E4 analysis headers carried hand-typed"))],
)

# ===== 080 =====
add("080",
    aliases=[("ideation-11 pick 4", "LH"), ("sw056 on G1 organisms", "LH")],
    question="Does blocking asT in training (G1) also remove routing by the reply the Assistant is writing (sw056's route), or only routing by its earlier turns?",
    q=("L", "- **Why:**"),
    run_state="done", status="verified",
    status_reason="ledger heading 'blind-recomputed'; analysis: 'Blind recompute matched ... same seed, so its CIs are not an independent draw'.",
    status_src=("F", "analysis.md", "**Blind recompute matched**"),
    vnote=("Blind recompute matched (RUNS/sw080/recompute/RECOMPUTE.md: every headline to 0.000, same verdicts; same seed)", ("F", "analysis.md", "**Blind recompute matched**")),
    organisms=["S_A", "N_A", "S_B", "N_B", "hdA0", "hdB0rep", "parent"],
    scenario_set=["v2 turn-1"], readouts=["forced 'By the way,'", "free (2,048)", "STRICT regex"],
    turn="turn 1, prefilled opening", claims=["Levers", "A"], dead_end=False,
    conflicts=[("README 'Status: done ... blind-recomputed' but its 'Result in one line' still says pending (cosmetic)", ("F", "README.md", "**Status:** done"), ("F", "README.md", "**Result in one line:** pending")),
               ("Brief said sw080 'numbers in, write-up pending'; files show analysis.md (23:38 UTC) and blind recompute present", ("F", "analysis.md", "**Blind recompute matched**"), ("RUNS", "RUNS/sw080/recompute/RECOMPUTE.md"))],
    notes="Think-tag gate overridden (D8). B not scored (N_B 0.10 < 0.30).",
)

# ===== 081 =====
add("081",
    aliases=[("ideation-11 pick 5", "LH"), ("G1 reroute test", ("F", "README.md", "G1 reroute test")), ("sw038 Part 1 cut to two arms", ("F", "README.md", "sw038 Part 1 cut to two arms"))],
    question="Does the conduct routing left in S (the asT-clamped G1 organism) still run through asT, or did the model route around it?",
    q=("F", "design_spec.md", "Does the conduct routing left in S still run through asT"),
    run_state="done", status="verified",
    status_reason="ledger heading (added ≈01:34 UTC 1 Nov) 'blind-recomputed'; analysis 'Blind recompute matched'.",
    status_src=("LH",),
    vnote=("Blind recompute matched (RUNS/sw081/recompute/RECOMPUTE.md)", ("F", "analysis.md", "**Blind recompute matched**")),
    organisms=["S_B", "N_B", "hdB0rep", "S_A", "N_A", "hdA0"],
    scenario_set=["v2"], readouts=["free (2,048)", "STRICT regex", "activations/probe"],
    turn="turn 3, supplied (sw021 v2 G3) self- vs user-hostile histories", claims=["Levers", "C"], dead_end=False,
    decision_rule=[("REROUTED: S's own-fit asT induce ≤ 0.3 of its residual gap with margin CI including 0, while the header patch still moves ≥ 0.5.", ("F", "design_spec.md", "**REROUTED:**")),
                   ("SAME VARIABLE, WEAKER: S's asT induce ≥ 0.5 of its residual gap with margin CI > 0.", ("F", "design_spec.md", "**SAME VARIABLE, WEAKER:**")),
                   ("INTERMEDIATE: anything else. Gates: N reproduces sw038 (fraction ≥ 0.5, margin CI lower > 0); positive control fraction(P0, S) ≥ 0.5.", ("F", "design_spec.md", "**INTERMEDIATE:**"))],
    conflicts=[("Brief (≈23:30 UTC) listed sw081 as still running; by 01:34 UTC 1 Nov the ledger entry, analysis.md and recompute exist", ("LH",), ("F", "analysis.md", "**Blind recompute matched**")),
               ("README 'Result in one line: pending' while its Status line says done (cosmetic)", ("F", "README.md", "**Status:** done"), ("F", "README.md", "**Result in one line:** pending"))],
    notes="Written up 01:3x UTC 1 Nov while this inventory was being built; ledger heading date '2026-10-31/11-01'.",
)

# ===== 082 =====
add("082",
    aliases=[("E2's sw071 (old number; renumbered sw071 → sw082 at 22:24 UTC)", ("F", "README.md", "**Renumbered:** sw071 → sw082")),
             ("071_polish_mechanism_v2 (old folder name)", ("F", "DECISIONS.md", "# DECISIONS — 071_polish_mechanism_v2")),
             ("old raw path RUNS/sw071/ (box 1, moved to RUNS/sw082/ at 22:21); node /root/runs/sw071/ and /root/caps/sw071/ unchanged", ("F", "DECISIONS.md", "D-renumber (22:24, executor-14)")),
             ("dirs71_* / calib71 / judge71 / 'sw071|…' keys inside", ("F", "README.md", "File, key and direction names inside still say 71")),
             ("spend tag 'sw071' in E2's spend.jsonl", ("FX", "RUNS/day_2026-10-31_E2/DECISIONS.md", "sw082's judge runs with --exp sw071")),
             ("sw034 on v2 / polish mechanism v2", ("F", "README.md", "the polish mechanism in Tony's pairs, on evaluation set v2"))],
    question="In Tony's e08 organisms, does the register of the Assistant's own earlier turns, read at those turns (asT_reg), cause which character's habit the reply takes on v2; and with the reply's first sentence fixed in one register, does asT_reg still move the habit?",
    q=("F", "design_spec.md", "**Question (sw034's, on new scenarios):**"),
    run_state="running", status="pending",
    status_reason="GPU done 23:56 UTC; judging throttled (ETA ≈05:00); a provisional report on current labels exists (RUNS/sw082/provisional_0114/) and 'the watcher's final report is separate and will supersede it'; no analysis.md or ledger entry.",
    status_src=("F", "DECISIONS.md", "D-e14c (01:19, executor-14)"),
    vnote=("none found (in progress)", None),
    parts=[("Part A (asT_reg / asT_cond / r1_reg)", "pending", "judging running; provisional report only", ("F", "DECISIONS.md", "D-e14c (01:19, executor-14)")),
           ("Fixed-opener arm", "gate failed", "opener gap gate fails in 6 / 8 organism × opener cells; under the frozen rule neither OWN-PAST POLISH nor REPLY REGISTER can fire; INTERMEDIATE by construction", ("F", "DECISIONS.md", "D-e14b (23:00, executor-14)"))],
    organisms=["e08-N", "e08-NB", "e08-X", "e08-XB", "parent (floor)"],
    scenario_set=["v2"], readouts=["forced 'By the way,'", "free (2,048)", "activations/probe", "STRICT regex"],
    turn="turn 3, supplied (parent-written) history; fixed reply opener arm", claims=["A", "C", "ChainP"], dead_end=False,
    decision_rule=[("Part A: arm PASS in an organism = toward-fraction ≥ 0.50 of the no-edit gap and margin over the pooled A has its CI excluding 0; induce decides ... asT_reg passes in ≥ 3 of the scored organisms out of 4 with the predicted sign, and the free shift has the same sign where the free gap CI excludes 0; 1–2 → 'partial'; 0 → 'not found at this site'.", ("F", "design_spec.md", "**Part A (sw034's rule, verbatim in substance):**")),
                   ("Fixed-opener: OWN-PAST POLISH / REPLY REGISTER / INTERMEDIATE (≥ 3 scored organisms per opener)", ("F", "design_spec.md", "**Fixed-opener reading (new)")),
                   ("Gate 3: no-edit forced gap ≥ 0.10 with CI excluding 0 per organism (and per organism × opener)", ("F", "design_spec.md", "**No-edit forced gap ≥ 0.10"))],
    tony=[("Tony's e08 N / NB / X / XB (sw014 HF PEFT adapters)", ("F", "design_spec.md", "Tony's e08 organisms (sw014's HF PEFT adapters"))],
    corrects=[],
    conflicts=[("README 'Status: planned (spec frozen; prep running)' vs DECISIONS: full run done, judging running", ("F", "README.md", "**Status:** planned"), ("F", "DECISIONS.md", "D-e14c (01:19, executor-14)")),
               ("D1 claimed 'no other lane uses 071' while E5 had created 071_one_protocol_battery at 20:10", ("F", "DECISIONS.md", "no other lane uses 071"), ("MIST", "Experiment number 071 used by two lanes"))],
    notes="Renumbering moved E5's sw071 smoke/, post/, tables/ by mistake (restored; mistakes.md 22:24). Design spec contains an 'Expected outcome' section; deliberately not copied here.",
)

# ---------------- build ----------------
MIST = NS + "/mistakes.md"
LEDGER_LINE_OF = {}


def resolve(spec, num, folder):
    if spec is None:
        return None
    if spec == "LH":
        return LH(num)
    if isinstance(spec, str):
        if spec.startswith("MAP:"):
            return S(NS + "/_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md", "S8 N/NB" if num in ("036", "044") else ("S9 ChainP" if num in ("041", "042") else "S5 thinking")) + " (map only)"
        if spec.startswith("MAPREADME:"):
            return S(SW + "/README.md", "`038_mechanism_core_v2/`")
        if spec == "LH_NONE":
            return S(SW + "/README.md", "`%s_" % num)
        return spec
    kind = spec[0]
    if kind == "LH":
        return LH(num)
    if kind == "L":
        return LE(num, spec[1])
    if kind.startswith("L0"):
        return LE(kind[1:], spec[1])
    if kind == "F":
        return S(F(folder, spec[1]), spec[2])
    if kind == "FX":
        return S(spec[1], spec[2])
    if kind == "MIST":
        return S(MIST, spec[1])
    if kind == "RUNS":
        p = spec[1]
        return p if os.path.exists(unabbr(p)) else p + " (missing)"
    return str(spec)


registry_path = RUNS + "/day_2026-10-31_E5/adapters_registry.json"
reg = json.load(open(registry_path))
sources_read.add(abbr(registry_path))

experiments = []
for e in EXPS:
    num = e["num"]
    folder = folder_of(num)
    title, date, lane = parse_heading(num)
    lh = LH(num)
    rec = {"id": "S" + num, "owner": "ours", "series": "sprint_work",
           "folder": f"NS/experiments/sprint_work/{folder}" if folder else None,
           "folder_name": folder}
    al = [{"alias": a, "src": "NS/research_ledger.md (all sprint_work entries use 'sprint_work/NNN' headings)"} for a in []]
    al = [{"alias": "sw" + num, "src": lh or S(SW + "/README.md", "`%s_" % num)},
          {"alias": "sprint_work/" + num, "src": lh or (f"NS/experiments/sprint_work/{folder}" if folder else None)},
          {"alias": num, "src": f"NS/experiments/sprint_work/{folder}" if folder else None}]
    for a, sp in e.get("aliases", []):
        al.append({"alias": a, "src": resolve(sp, num, folder) if sp is not None else ("brief / run names (not found verbatim in a source)" if "E5's band map" in a else f"RUNS listing / run names ({'RUNS/sw' + num})")})
    rec["aliases"] = al
    if title is None:  # no ledger entry: README title
        rdm = lines(F(folder, "README.md"))
        title = rdm[0].lstrip("# ").strip() if rdm else None
        rec["title"] = title
        rec["title_src"] = F(folder, "README.md") + ":1"
        rec["date"] = "2026-10-31"
        rec["date_src"] = S(F(folder, "README.md"), "31 Oct 2026")
        rl = {"071": "E5 (executor-15)", "074": "E5 (executor-15)", "082": "executor-14 (E2, Lane M) [E2b]"}[num]
        rec["lane"] = rl
        rec["lane_src"] = S(F(folder, "README.md"), "executor-1")
    else:
        rec["title"] = title
        rec["title_src"] = lh
        rec["date"] = date
        rec["date_src"] = lh
        rec["lane"] = lane
        rec["lane_src"] = lh
    rec["question"] = e["question"]
    rec["question_src"] = resolve(e["q"], num, folder)
    rec["run_state"] = e["run_state"]
    rec["status"] = e["status"]
    rec["status_reason"] = e["status_reason"]
    rec["status_src"] = resolve(e["status_src"], num, folder)
    vn, vsp = e["vnote"]
    rec["verification_note"] = vn if vsp is None else f"{vn} [{resolve(vsp, num, folder)}]"
    rec["parts"] = [{"part": p, "status": s, "note": n, "src": resolve(sp, num, folder)} for p, s, n, sp in e.get("parts", [])]
    files = {"readme": None, "design_spec": None, "analysis": None, "other_key_md": []}
    if folder:
        for k, fn in (("readme", "README.md"), ("design_spec", "design_spec.md"), ("analysis", "analysis.md")):
            if os.path.exists(os.path.join(SW, folder, fn)):
                files[k] = F(folder, fn)
        for fn in sorted(os.listdir(os.path.join(SW, folder))):
            if fn.endswith(".md") and fn not in ("README.md", "design_spec.md", "analysis.md"):
                files["other_key_md"].append(F(folder, fn))
        if os.path.isdir(os.path.join(SW, folder, "forecast_frozen")):
            files["other_key_md"].append(F(folder, "forecast_frozen/"))
    # templates: flag analysis.md that is still the template
    if files["analysis"]:
        a0 = lines(files["analysis"])
        if a0 and "<experiment name>" in a0[0]:
            files["analysis_is_template"] = True
    rec["files"] = files
    extra_raw = []
    if num == "070":
        extra_raw.append("RUNS/day_2026-10-31_E3/sw070_pirate_v2_default_cell")
    if num in ("064", "078", "079"):
        extra_raw.append("RUNS/recompute_E4_late")
    rd = raw_dirs(num, extra_raw)
    rec["raw_dirs"] = rd
    rec["html_local"] = html_local(folder, [r for r in rd if re.match(r"RUNS/sw\d", r)])
    arts = artifacts(num, folder)
    for url, note, sp in e.get("report_extra", []):
        arts.setdefault(url, []).append(resolve(sp, num, folder) + f" ({note})")
    rec["report_artifacts"] = sorted(arts.keys())
    rec["report_src"] = {u: v for u, v in arts.items()}
    rec["ledger_line"] = int(lh.split(":")[1]) if lh else None
    rec["organisms_as_named"] = e["organisms"] if e["organisms"] != "REGISTRY" else None
    if e["organisms"] == "REGISTRY":
        ready = [k for k, v in reg["organisms"].items() if v.get("status") == "ready"]
        notready = {k: v.get("status") for k, v in reg["organisms"].items() if v.get("status") != "ready"}
        rec["organisms_as_named"] = ready + ["parent"]
        rec["organism_list_src"] = "RUNS/day_2026-10-31_E5/adapters_registry.json#organisms[status=ready] + parent; " + S(F(folder, "DECISIONS.md"), "51 scored + parent")
        rec["organisms_not_scored"] = notready
        rec["organism_count_scored"] = len(ready)
    rec["scenario_set"] = e["scenario_set"]
    rec["readouts"] = e["readouts"]
    rec["turn_and_history"] = e["turn"]
    rec["claims"] = e["claims"]
    rec["dead_end"] = e["dead_end"]
    rec["corrects"] = [{"id": i, "what": w, "src": resolve(sp, num, folder)} for i, w, sp in e.get("corrects", [])]
    rec["corrected_by"] = [{"id": i, "what": w, "src": resolve(sp, num, folder)} for i, w, sp in e.get("corrected_by", [])]
    rec["tony_links"] = [{"what": w, "src": resolve(sp, num, folder) if sp else None} for w, sp in e.get("tony", [])]
    rec["conflicts"] = [{"what": w, "a": resolve(a, num, folder), "b": resolve(b, num, folder)} for w, a, b in e.get("conflicts", [])]
    rec["notes"] = e.get("notes", "")
    if lh is None:
        rec["notes"] = (rec["notes"] + " " if rec["notes"] else "") + "No ledger entry (checked grep '^## sprint_work/%s')." % num
    if "decision_rule" in e:
        rec["decision_rule"] = [{"text": t, "src": resolve(sp, num, folder)} for t, sp in e["decision_rule"]]
    if "organisms_produced" in e:
        op = e["organisms_produced"]
        for o in op:
            o["exists"] = os.path.exists(unabbr(o["path"]))
        rec["organisms_produced"] = op
        if "organisms_produced_note" in e:
            t, sp = e["organisms_produced_note"]
            rec["organisms_produced_note"] = {"text": t, "src": resolve(sp, num, folder)}
    experiments.append(rec)

# ---------------- unused numbers 046-049 ----------------
for num in ("046", "047", "048", "049"):
    has_folder = folder_of(num) is not None
    has_raw = any(re.fullmatch(r"sw%s.*" % num, d) for d in os.listdir(RUNS))
    has_ledger = any(re.search(r"sprint_work/%s\b|sw%s\b" % (num, num), l) for l in LL)
    experiments.append({
        "id": "S" + num, "owner": "ours", "series": "sprint_work", "folder": None, "folder_name": None,
        "aliases": [], "title": None, "title_src": None, "question": None, "question_src": None,
        "date": None, "date_src": None, "lane": None, "lane_src": None,
        "run_state": "unused number", "status": None, "status_reason": "number never used",
        "status_src": "ls NS/experiments/sprint_work (no %s_* folder); ls RUNS (no sw%s*); grep NS/research_ledger.md, NS/navigation.md, NS/mistakes.md, NS/experiments/sprint_work/README.md (no match)" % (num, num),
        "verification_note": "none found", "parts": [],
        "files": {"readme": None, "design_spec": None, "analysis": None, "other_key_md": []},
        "raw_dirs": [], "html_local": [], "report_artifacts": [], "report_src": {}, "ledger_line": None,
        "organisms_as_named": [], "scenario_set": [], "readouts": [], "turn_and_history": None, "claims": [],
        "dead_end": False, "corrects": [], "corrected_by": [], "tony_links": [], "conflicts": [],
        "notes": f"Confirmed unused at build time: folder={has_folder}, raw dir={has_raw}, ledger mention={has_ledger}. E3 used 040–045 and E1 started at 050; no source explains the gap.",
    })
    if has_folder or has_raw or has_ledger:
        problems.append(f"{num} expected unused but folder/raw/ledger found")

experiments.sort(key=lambda r: r["id"])

problems_static = [
    "E5 created two NEW experiments after the brief: 083_parent_animal_prior and 084_conduct_C0_band (E5's follow-ups first numbered sw078 / sw079, renamed sw083 / sw084 at 01:23 UTC 1 Nov because E4 had taken 078/079). They are outside S036..S082; the integrator needs S083 / S084 entries. Source: RUNS/day_2026-10-31_E5/DECISIONS.md D31–D32; folders NS/experiments/sprint_work/083_parent_animal_prior, 084_conduct_C0_band; raw RUNS/sw083, RUNS/sw084.",
    "Sources changed while this inventory ran (ledger rewritten 01:34 UTC adding sw081; E4 report links being added to analysis.md files; sw071 / sw082 judging live). Line numbers are resolved at build time; re-run the builder before integrating.",
    "Lane-level HTML reports live outside the experiment folders and raw dirs, so they are not in html_local: RUNS/day_2026-10-31_E5/report/E5_report.html (118 KB; artifact JnbDRuC8PCyGvkBwiJkr6R), RUNS/day_2026-10-31_E2/report/e2_lane_m_report.html (165 KB), NS/experiments/sprint_work/_reports/E4_2026-10-31/E4_report.html (4.4 MB; artifact FWiqkS46ps5iDEaBATHA9s).",
    "STATUS files are stale relative to records: STATUS_E2.md (22:24) says sw082 'Waiting on the user'; STATUS_E4.md (21:15) predates sw064/078/079/080/081; STATUS_E5.md (23:05) lists sw072 as running. Records (ledger, analysis.md, day DECISIONS) were preferred.",
    "Raw-dir HTML search limited to depth 3 with a 20 s timeout per dir (big trees).",
    "'E5's band map' (alias requested for sw072) was not found verbatim in any source read.",
    "sw040 Part B (P0) still marked provisional 'pending sw070' though sw070 finished; not updated by E3 (E3 closed 18:55).",
]

questions = [
    "sw061 (G1): numbers are blind-recomputed and the conduct-gap result is supported, but the frozen primary gate FAILS on the default-lean component. Status recorded as 'verified' with a 'gate failed' part; should the archive show it as 'gate failed' instead?",
    "sw043 / sw045: 'gate FAILS' there is the pre-registered success criterion (a negative answer), not an instrument gate; recorded as 'not recomputed' (no recompute recorded). OK?",
    "sw073: two recomputes matched but reporting is blocked by the node provenance rule (writer code not kept) pending the user's decision; recorded as 'provisional'. Accept with caveat, or re-run the writer?",
    "sw036: 'NOT SCORED' because forced onset < 0.70 is recorded as 'gate failed'. OK?",
]

out = {
    "part": "ours_S036_S082",
    "generated_utc": subprocess.run(["date", "-u", "+%Y-%m-%dT%H:%M:%SZ"], capture_output=True, text=True).stdout.strip(),
    "sources_read": sorted(sources_read | {
        "NS/_sessions/executor/STATUS_E1.md", "NS/_sessions/executor/STATUS_E2.md", "NS/_sessions/executor/STATUS_E3.md",
        "NS/_sessions/executor/STATUS_E4.md", "NS/_sessions/executor/STATUS_E5.md",
        "RUNS/day_2026-10-31_E4/RUNBOARD.md", "RUNS/day_2026-10-31_E2/RUNBOARD.md", "RUNS/day_2026-10-31_E2/DECISIONS.md",
        "RUNS/day_2026-10-31_E5/DECISIONS.md", "RUNS/sw081/analysis/report.txt",
        "NS/_sessions/ideation/notes/2026-10-31_run_map_and_eval_sets.md",
        "NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md (map only)",
        "NS/navigation.md", "NS/experiments/sprint_work/README.md"}),
    "file_times_read": {
        "NS/_sessions/executor/STATUS_E2.md": "2026-10-31T22:24:40Z (mtime)",
        "NS/_sessions/executor/STATUS_E4.md": "2026-10-31T21:15:39Z (mtime)",
        "NS/_sessions/executor/STATUS_E5.md": "2026-10-31T23:05:17Z (mtime)",
        "NS/_sessions/executor/STATUS_E3.md": "2026-10-31T20:22:54Z (mtime)",
        "NS/_sessions/executor/STATUS_E1.md": "2026-10-31T06:34:02Z (mtime)",
        "RUNS/day_2026-10-31_E4/RUNBOARD.md": "2026-11-01T01:27:27Z (mtime)",
        "RUNS/day_2026-10-31_E2/RUNBOARD.md": "2026-11-01T00:00:43Z (mtime)",
        "RUNS/day_2026-10-31_E5/RUNBOARD.md": "2026-10-31T23:35:14Z (mtime)",
        "NS/research_ledger.md": "2026-11-01T01:34:53Z (mtime at last check)",
    },
    "lane_state_confirmed": [
        {"item": "E5 sw071", "found": "GPU jobs all DONE by 01:13 UTC; judging running on two keys; hand-back ≈02:30", "src": S(RUNS + "/day_2026-10-31_E5/DECISIONS.md", "D30 (01:17 UTC")},
        {"item": "E5 sw074", "found": "forecast frozen + verified; scoring waits for sw071", "src": S(NS + "/experiments/sprint_work/074_zero_training_rule_forecast/README.md", "Status:")},
        {"item": "E4 sw081", "found": "done: ledger entry + analysis + blind recompute (≈01:34 UTC 1 Nov)", "src": LH("081")},
        {"item": "E2 sw082", "found": "GPU done 23:56; judging throttled (ETA ≈05:00); provisional report RUNS/sw082/provisional_0114/", "src": S(NS + "/experiments/sprint_work/082_polish_mechanism_v2/DECISIONS.md", "D-e14c (01:19")},
        {"item": "E4 sw080", "found": "done and verified (analysis.md 23:38 UTC, recompute present), not 'write-up pending'", "src": S(NS + "/experiments/sprint_work/080_turn1_on_g1/analysis.md", "**Blind recompute matched**")},
        {"item": "E5 sw083 / sw084 (new)", "found": "started after the user's go ≈01:25 UTC 1 Nov", "src": S(RUNS + "/day_2026-10-31_E5/DECISIONS.md", "D32 (01:23 UTC")},
    ],
    "numbering_collisions": [
        {"what": "sw071 used by E5 (071_one_protocol_battery, 20:10) and E2b (071_polish_mechanism_v2, 21:30); E2b renamed to sw082 at 22:24; raw RUNS/sw071 → RUNS/sw082 at 22:21 (node paths still /root/runs/sw071)",
         "src": [S(MIST, "Experiment number 071 used by two lanes"), S(NS + "/experiments/sprint_work/082_polish_mechanism_v2/DECISIONS.md", "D-renumber (22:24")]},
        {"what": "E4 took sw078 / sw079 inside E5's assigned 071–079 range (≈21:03); sw080 / sw081 followed",
         "src": [S(NS + "/_sessions/executor/notes/2026-10-31_E4_context.md", "note sw078/079 overlap"), S(RUNS + "/day_2026-10-31_E5/DECISIONS.md", "E4 had taken 078/079")]},
        {"what": "E5's own planned sw078 / sw079 renumbered sw083 / sw084 (01:23 UTC 1 Nov)",
         "src": [S(RUNS + "/day_2026-10-31_E5/DECISIONS.md", "renumbered sw078→sw083")]},
    ],
    "experiments": experiments,
    "problems": problems_static + problems,
    "questions_for_user": questions,
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("wrote", OUT, len(experiments), "entries;", len(problems), "dynamic problems")
for p in problems:
    print("PROBLEM", p)
