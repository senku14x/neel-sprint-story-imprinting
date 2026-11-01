# Builder for naming_and_resources.json. Reads files only; writes only the output JSON.
# Every source is given as (abbreviated path, anchor substring); the line is resolved at build time.
import json, re, os, sys, subprocess, glob, hashlib

ABBR = {
    'NS': '/workspace/Neel Sprint',
    'RUNS': '/workspace/runs_executor',
    'TONY': '/tmp/claude-0/-workspace/22833c91-e053-47aa-b524-9d5b322fe644/scratchpad/tony',
    'ARCH': '/workspace/grandfather/unified_artifact',
}
OUT = '/workspace/grandfather/unified_artifact/inventory/naming_and_resources.json'
SCR = '/workspace/grandfather/unified_artifact/inventory/_scratch'
problems = []
_cache = {}
used_files = set()

def real(p):
    a, rest = p.split('/', 1)
    return os.path.join(ABBR[a], rest)

def lines(p):
    if p not in _cache:
        try:
            _cache[p] = open(real(p), encoding='utf-8', errors='replace').read().split('\n')
        except Exception as e:
            _cache[p] = None
            problems.append(f'cannot read {p}: {e}')
    return _cache[p]

def S(p, anchor, nth=1, after=None):
    """Resolve anchor -> {'src': 'P:line', 'quote': anchor}."""
    L = lines(p)
    used_files.add(p)
    if L is None:
        return {'src': p, 'quote': anchor, 'unresolved': True}
    start = 0
    if after:
        for i, l in enumerate(L):
            if after in l:
                start = i
                break
    k = 0
    for i in range(start, len(L)):
        if anchor in L[i]:
            k += 1
            if k == nth:
                return {'src': f'{p}:{i+1}', 'quote': anchor}
    problems.append(f'anchor not found: {p} :: {anchor!r}')
    return {'src': p, 'quote': anchor, 'unresolved': True}

def K(p, key, note=None):
    used_files.add(p.split('#')[0])
    d = {'src': f'{p}#{key}'}
    if note: d['quote'] = note
    return d

LED = 'NS/research_ledger.md'
SES = 'NS/_sessions/executor/SESSIONS.md'
ISES = 'NS/_sessions/ideation/SESSIONS.md'
RP = 'NS/Spec_research/research_program.md'
AM = 'NS/Spec_research/amendments.md'
V3 = 'NS/_sessions/audit/notes/2026-10-31_external_doc_v3_export.md'
V2 = 'NS/_sessions/audit/notes/2026-10-30_external_doc_v2_export.md'
VR = 'NS/Vishesh_ideation/00_README.md'
I10 = 'NS/_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md'
HUB = 'NS/_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md'
WSS = 'NS/_sessions/ideation/notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md'
NAV = 'NS/navigation.md'
MIS = 'NS/mistakes.md'
SW = 'NS/experiments/sprint_work'
E12 = 'TONY/e12_habit_mechanism/e12'
TML = E12 + '/MECHANISM_LEDGER.md'
TQE = E12 + '/QUESTIONS_EVIDENCE.md'
TQJ = E12 + '/queue/queue.json'
RQ = 'TONY/replicate_qwen27B'
E5D = 'RUNS/day_2026-10-31_E5/DECISIONS.md'
E2D = 'RUNS/day_2026-10-31_E2/DECISIONS.md'
E1D = 'RUNS/day_2026-10-31_E1/DECISIONS.md'
ADEC = 'ARCH/DECISIONS.md'
MAP_DOCX = 'NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md'
OVB = 'NS/things to throw away/new session prompts/2026-10-30_overnight_master_one_executor.md'

def date_utc():
    return subprocess.run(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], capture_output=True, text=True).stdout.strip()

GEN = date_utc()

# ---------------------------------------------------------------- schemes
def sch(scheme, examples, meaning, defined_in, used_by, notes=None, conflicts=None):
    d = {'scheme': scheme, 'examples': examples, 'meaning': meaning,
         'defined_in': defined_in if isinstance(defined_in, list) else [defined_in], 'used_by': used_by}
    if notes: d['notes'] = notes
    if conflicts: d['conflicts'] = conflicts
    return d

schemes = [
 sch('Spec hypotheses H1-H9', ['H1', 'H4', 'H9'],
     'The V6.1 research program\'s plausible explanations, e.g. "H1. Shared computation determines which recipients inherit the update" ... "H9. Learning changes the context that initially constrained it".',
     [S(RP, '### H1. Shared computation determines'), S(RP, '### H9. Learning changes the context'), S(AM, 'the labels (H1–H9, E1–E10, X01–X15)')], 'ours'),
 sch('Spec experiments E1-E10', ['E1', 'E4', 'E10'],
     'V6.1 spec experiment labels, e.g. "E1. Establish a released-pair bridge and an interpretable reference", "E4. Transfer beyond bees/crows: pirate versus Shakespearean speech", "E10. Prospective source-transfer and intervention forecasts".',
     [S(RP, '### E1. Establish a released-pair bridge'), S(RP, '### E10. Prospective source-transfer'), S(AM, 'the labels (H1–H9, E1–E10, X01–X15)')], 'ours'),
 sch('Spec larger investigations X01-X15', ['X01', 'X08', 'X15'],
     'V6.1 spec optional/larger investigations table, e.g. "X08 How much of transfer is amplified by generated history?".',
     [S(RP, '| X01 | Does anchor coverage'), S(RP, '| X15 | Can story and domain'), S(RP, '### X08. Separate immediate propensity')], 'ours'),
 sch('Spec Studies 1-4 (+ complementary study)', ['Study 1', 'Study 2', 'Study 4'],
     'V6.1 spec study sections ("Study 1 — Identify which property of the training context determines transfer"; "Study 2 — Use CAFT ...").',
     [S(RP, '## 7. Study 1 — Identify'), S(RP, '## 10. Study 4 — Predict')], 'ours'),
 sch('Research sub-questions A-D (31 Oct amendment)', ['A. What decides it?', 'B. Can we predict it?', 'C. How is it carried?', 'D. Does it replicate'],
     'Generalised research question split into four parts; the archive DECISIONS also calls these "our A–D".',
     [S(AM, '**A. What decides it?**'), S(AM, '**D. Does it replicate, across runs, families and models?**'), S(ADEC, 'beside our A–D')], 'ours'),
 sch('Reproduction series NNN (001-018)', ['001 (HD organisms reproduction)', '009 (DeepSeek-V4.1 via Tinker)', '018 (parent directions)'],
     'First experiment series, folders experiments/reproduction/NNN_<name>; ledger headings "## NNN — <short name>". Numbers 007 is absent on disk; 013 (Kimi-K2.6 Tinker) and 015 have no ledger entry.',
     [S(LED, '## NNN — <short name>'), S(LED, '## 001 — HD organisms reproduction'), S(NAV, 'first series `reproduction/`')], 'ours',
     notes='Folder listing NS/experiments/reproduction/: 001-006, 008-018 (no 007).'),
 sch('Archive prefix R001-R018 (new)', ['R001', 'R009', 'R018'],
     'Unified-archive IDs for the reproduction series (R + the NNN folder number).',
     [K('ARCH/inventory/ours_R.json', 'experiments[*].id', 'R001 ... R018')], 'ours (archive)'),
 sch('sprint_work/NNN, sw001-sw084', ['sprint_work/001', 'sw029', 'sw082 (renumbered from 071)', 'sw083/sw084 (renamed from 078/079)'],
     'Second experiment series, folders experiments/sprint_work/NNN_<name>; ledger headings "## sprint_work/NNN — ...". "Experiment numbers are assigned at launch" (next free number). Numbers 046-049 unused on disk.',
     [S(LED, '## sprint_work/001 — Persona routing and steering'), S(VR, '**Convention 10: experiment numbers are assigned at launch.**'), S(SW + '/README.md', 'Numbering restarts here')], 'ours',
     notes='Disk listing shows 001-045, 050-084 (no 046-049).'),
 sch('Archive prefix S001-S084 (new)', ['S001', 'S061', 'S084'],
     'Unified-archive IDs for sprint_work (S + the NNN number). Not the docx S1-S10 sessions.',
     [S(ADEC, 'Sprint range is now S001–S084'), K('ARCH/inventory/ours_S001_S035.json', 'experiments[*].id')], 'ours (archive)'),
 sch('Explorations (throwaway) and archive X- prefix', ['X-1028-X0', 'X-1027-overnight', 'X-1025-round5-C1-patching'],
     'Archive IDs for exploration-grade runs outside the numbered series (X-<MMDD>-<name>).',
     [K('ARCH/inventory/ours_X.json', 'experiments[*].id', 'X-1028-X0 ...')], 'ours (archive)'),
 sch('28 Oct exploration X0-X9', ['X0 audits', 'X1 balanced organism "sym"', 'X8', 'X9'],
     'Sub-runs of the 4-GPU-hour 28 Oct exploration (executor-7): "X0 audits, X1 balanced organism \\"sym\\", X2–X7, then the Assistant batch X8–X9". "X8 setup" = length-matched own dismissive histories (reused by sw005, extract1028 E2).',
     [S(LED, 'X0 audits, X1 balanced organism'), S(LED, '## sprint_work/005 — text-level conduct dissection on the X8 setup')], 'ours'),
 sch('extract1028 blocks E1-E7', ['E1 (parent texts through 8 models)', 'E2 (reply-start states for X8 histories + census)', 'E4 (story-side positions)', 'E7 (dropped)'],
     'Capture blocks of ideation-9\'s extraction batch run by executor-8; "run as specified except E7 (dropped by the user)".',
     [S(LED, 'run as specified except E7 (dropped by the user)'), S(LED, "**E1:** 002's 11,048 parent texts"), S(LED, '**E6:** LoRA write directions (CPU).')], 'ours'),
 sch('sae1029 Parts 1-3 and addendum A-F', ['Part 1', 'Part 3 (causal feature clamp)', 'addendum A–F'],
     'Sections of the L42 SAE exploration (executor-8).',
     [S(LED, "ideation-9's brief plus addendum A–F"), S(LED, '**Part 3, causal feature clamp')], 'ours'),
 sch('Executor lanes E1-E5 (+E2b)', ['E1', 'E2 (Lane M)', 'E2b', 'E3 (Chain P)', 'E4', 'E5'],
     'Parallel executor lanes of 30 Oct-1 Nov: E1 = "Tony\'s evaluations plus side runs" (executor-10), E2 = "Lane M, the mechanism" (executor-11), E2b = E2 continued by executor-14 after the account switch, E3 = "Chain P, forecast before training" (executor-12), E4 = executor-13 (S10 replication, turn-1, readers, levers), E5 = executor-15. Day folders RUNS/day_2026-10-31_E<n>/.',
     [S(I10, "| E1 | Tony's evaluations plus side runs | executor-10"), S(I10, '| E2 | Lane M, the mechanism | executor-11'), S(I10, '| E3 | Chain P, forecast before training |'), S(SES, '## executor-14 (E2b, Lane M continued)'), S(SES, '## executor-13 (E4) — 2026-10-31 07:07'), S('NS/_sessions/executor/notes/2026-10-31_E5_context.md', 'Role: E5 = executor-15')], 'ours'),
 sch('Lane names (Lane M, Lane P)', ['Lane M', 'Lane P', 'laneM / laneS10 / laneE5 / chainP (git branches)'],
     'Lane M = the mechanism lane (E2); Lane P = sw040+ (Chain P). Git branches carry lane names: laneM (E2), laneS10 (E4), laneE5 (E5), chainP (E3).',
     [S(I10, 'Lane M is the mechanism: S3 leakage'), S('NS/_sessions/ideation/notes/2026-10-31_ideation-10_up_to_speed.md', 'Lane P: sw040+'), S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'branch `laneM`'), S('NS/_sessions/executor/STATUS_E4.md', 'Push to branch laneS10'), S('NS/_sessions/executor/STATUS_E3.md', 'branch `chainP`')], 'ours'),
 sch('Executor session numbers', ['executor-1', 'executor-7 (= "sprint executor 2")', 'executor-9', 'executor-15'],
     'Main executor Claude sessions, numbered in order; each logs an entry in _sessions/executor/SESSIONS.md ("## executor-N — YYYY-MM-DD"). No entry for executor-2 or executor-15 (E5) at build time.',
     [S(SES, '## executor-N — YYYY-MM-DD'), S(SES, '## executor-7 (= "sprint executor 2")')], 'ours',
     notes='executor-3\'s goal was "the executor-2 prompt" (SESSIONS.md), and executor-1 "Rewrote the executor-2 prompt"; no session is logged as executor-2.'),
 sch('Seeds and Tinker executors', ['executor-seeds-1', 'tinker-1', 'tinker-2 (planned)'],
     'Side executors: executor-seeds-1 (box 2, 014/016/017); tinker-1 (Tinker API: 009 DeepSeek, 013 Kimi). tinker-2 is named as the next session in tinker STATUS but has no SESSIONS entry.',
     [S('NS/_sessions/executor-seeds/SESSIONS.md', '## executor-seeds-N — YYYY-MM-DD'), S('NS/_sessions/tinker/STATUS.md', 'Next session = tinker-2')], 'ours'),
 sch('Ideation sessions ideation-N', ['ideation-1', 'ideation-5 (unlogged)', 'ideation-10 ("Wallahi Ideation 10")', 'ideation-12 (Claude Code, "_cc")'],
     'Planning/ideation Claude sessions logged in _sessions/ideation/SESSIONS.md. ideation-5 logged no entry ("the real ideation-5"). ideation-12 exists twice: a Claude Code session (notes suffixed _cc) and a Codex session (codex_ideation).',
     [S(ISES, '## ideation-N — YYYY-MM-DD'), S(ISES, 'the real ideation-5'), S('NS/_sessions/ideation/notes/2026-10-31_ideation-12_cc_up_to_speed.md', '# ideation-12 (Claude Code)'), S('NS/_sessions/codex_ideation/README.md', 'assigned this Codex session to ideation-12')], 'ours'),
 sch('Codex and audit sessions', ['codex-1', 'codex-2', 'audit-1 "fixing myself"', 'codex_ideation (ideation-12)'],
     'Codex sessions (_sessions/codex/SESSIONS.md), the audit session (_sessions/audit/SESSIONS.md) and the Codex ideation-12 folder.',
     [S('NS/_sessions/codex/SESSIONS.md', '## codex-N — YYYY-MM-DD'), S('NS/_sessions/audit/SESSIONS.md', '## audit-1 "fixing myself"')], 'ours'),
 sch('Docx run-sheet sessions S1-S10 (31 Oct plan)', ['S1 Verifier and hygiene', 'S3 Leakage-free directions', 'S7 One steering vector', 'S8 Persona capture (N/NB)', 'S9 Forecast before training (Chain P)', 'S10 Training levers and replication'],
     'Sessions of the external audit doc\'s 31 Oct run sheet ("Story imprinting ... gated experiment chains" v3 / corrected plan docx). Executors ran them as sw032 (S1), sw028/031/054/038 (S2), sw029 (S3), sw030 (S4), sw033 (S5), sw026 (S6, B0 only), sw035 (S7), sw036/040A/044 (S8), sw040-042 (S9), sw043/045/055/061 (S10).',
     [S(V3, '| S1 Verifier and hygiene |'), S(V3, '| S10 Training levers and replication |'), S(V3, 'S8 · Persona capture replication'), S(SW + '/040_chainP_premise_and_p0/analysis.md', "Part A (= the plan docx v3's **S8**)")], 'ours',
     notes='Experiment mapping per S-session confirmed from ledger headings / analysis headers for S1 (sw032), S3 (sw029), S4 (sw030), S5 (sw033), S7 (sw035), S8 (sw040 Part A, sw044), S10 (sw043, sw045, sw055); the full table is from the Codex map ' + MAP_DOCX + ' (map, not primary).'),
 sch('Docx sub-labels inside S-sessions', ['S8 premise', 'S10 G1 (containment) / G2 (authorship)', 'S9 = Chain P', 'S7 V1/V2c/V2p/V3 arms', 'S3 step 0/1/2'],
     'Sub-items of the docx session briefs: S10 "Authorship (G2)" and "G1, after S3"; S8 premise check; S9 = Chain P stages P0-P2; S7 arms V1 (single-layer vector), V2c/V2p (per-layer vectors), V3 (rank-1 LoRA).',
     [S(V3, '- Authorship (G2).'), S(V3, '- G1, after S3.'), S(I10, '"the premise check is S8"'), S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'sw035: V1 (single-layer vector)')], 'ours'),
 sch('28 Oct Neel-question plan S1-S9', ['S1. Validate the SAE on our states', 'S5. Single-character training', 'S9 (new). Is the update just one steering vector?'],
     'An earlier, different S-numbering (ideation-9\'s plan for Neel\'s 28 Oct question).',
     [S('NS/_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md', '### S1. Validate the SAE on our states'), S('NS/_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md', '### S8. Input vs effect')], 'ours'),
 sch('Docx experiment chains (letters) and their steps', ['I0', 'Chain A (A0-A5)', 'Chain B (B0-B4)', 'Chain C (C1-C2)', 'Chain D (D1-D2)', 'Chain DL (DL1-DL5)', 'Chain E (E1-E3)', 'Chain G (G1-G3)', 'Chain H (H0-H3)', 'Chain K (K1-K2, K2b, K2c)', 'Chain P (P0-P3)'],
     'Gated experiment chains of the external audit doc (30-31 Oct). Steps are named letter+number, e.g. "B0 · Known answer", "H0 · Template perturbations", "D1 · Trigger-free preference", "G1 · Containment", "G3 · Data filtering". The user\'s Vishesh_ideation specs are organised by these chains (01_chainB ... 10_chainE).',
     [S(V3, '### I0. Instruments first'), S(V3, 'A0 · Story-to-Assistant probe transfer'), S(V3, 'B0 · Known answer'), S(V3, 'D1 · Trigger-free preference'), S(V3, 'H0 · Template perturbations'), S(V3, 'K1 · Replicate the decline split'), S(V3, 'E1 · Label the routing variable'), S(V3, '- G1 · Containment.'), S(V3, '- G3 · Data filtering.'), S(V3, 'P3 · Then the mechanism'), S(VR, '`01_chainB_gradient_kernel.md`')], 'ours'),
 sch('Backlog ids (overnight 30 Oct): B0, D1, H0, "idea N"', ['backlog B0 (sw026)', 'backlog D1 (sw023)', 'backlog H0 (sw024)', 'backlog idea 3 (sw022)', 'backlog idea 4 (sw025)'],
     'Idle-GPU backlog of the 30 Oct overnight run, labelled by the external doc\'s chain steps (B0, D1, H0) and fresh-idea numbers (idea 3, idea 4).',
     [S(OVB, '## 8. Backlog for idle GPUs'), S(LED, '(backlog B0)'), S(LED, '(backlog D1)'), S(LED, '(backlog H0)'), S(LED, '(backlog idea 3)')], 'ours'),
 sch('Docx fresh ideas 1-7 (1a-1e, 7a-7c)', ['1. The latent-rule theory', '3. Does the tracer drag the persona with it?', '4. Sabotage conduct capture', '1b natural-vector surrogate'],
     'Numbered "Fresh ideas (added 30 Oct)" of the external doc; sub-letters 1a-1e and 7a-7c appear in the Codex map.',
     [S(V3, '### 1. The latent-rule theory'), S(V3, '### 7. Smaller fresh probes'), S(MAP_DOCX, '**1b natural-vector surrogate**')], 'ours',
     notes='Sub-letters (1a-1e, 7a-7c) taken from the Codex map (a map, not primary); the v3 export headings confirm 1-7 only.'),
 sch('S10 levers (sw061 Lever 1-3)', ['Lever 1 = G2 authorship (sw045)', 'Lever 2 = Assistant-side redirect (sw043)', 'Lever 3 = G1 containment (sw061)'],
     'sw061\'s design names for the S10 training levers; E3 adopted Levers 1 and 2 verbatim.',
     [S(SW + '/061_s10_training_levers/design_spec.md', '## Lever 1 — G2 authorship'), S(SW + '/061_s10_training_levers/design_spec.md', '## Lever 3 — G1 containment'), S(LED, 'sw061 Lever 1 adopted verbatim')], 'ours'),
 sch('G1 training arms S / N / O', ['S (parent asT read-clamp)', 'N (energy null clamp)', 'O (ordinary, unclamped reference: hdB0rep / hdA0)', 'S_A, N_A'],
     'Organisms of sw061 Lever 3 (G1 containment).',
     [S(SW + '/061_s10_training_levers/design_spec.md', 'S(parent asT, P-all), N(energy null, P-all); reference O'), S(SW + '/061_s10_training_levers/analysis.md', '**O:** the unclamped reference')], 'ours'),
 sch('Vishesh spec 03 G1 arms S / X', ['arm S', 'arm X'],
     'The user\'s G1 containment spec: arm S = no module in layers 17-63 may read the parent\'s self-conduct coordinate; arm X = it is swapped between character types.',
     [S(VR, '(arm S), or every module sees it swapped between character types (arm X)')], 'ours'),
 sch('Chain P stages P0-P3 and forecasters P1-P5 / P3_sym', ['P0 (retrodict existing pairs; sw040 Part B)', 'P1 (specs, pilots, frozen forecast; sw041)', 'P2 (train and score; sw042)', 'P3 (mechanism)', 'P1-P5 predictors', 'P3_sym (primary forecaster)'],
     'Chain P stages from the docx; inside sw040/041 the predictors are also numbered P1 self-recognition, P2 judge, P3 parent\'s own answer, P4 PHM-style, P5 trivial baseline; P3_sym = the orientation-symmetric P3 forecast frozen before training.',
     [S(V3, '- P0. Retrodict every trained pair'), S(V3, 'P3 · Then the mechanism'), S(SW + '/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt', 'P1 self-recognition'), S(SW + '/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt', 'P5 trivial baseline'), S(SW + '/041_chainP_pairs_readouts_forecast/analysis.md', 'P3_sym primary')], 'ours'),
 sch('Chain P organisms', ['main', 'mirror', 'honest (two-honest control)', 'F-only', 'matched-main'],
     'sw042\'s trained organisms (9 in all: 7 + 2).',
     [S(LED, '(main, mirror, honest, F-only, matched-main)')], 'ours'),
 sch('sw019 evaluation set v2 history sets G2 / G3', ['G2 (six conduct versions)', 'G3 (attribution contexts: self|user|quote|third × hostile|control)'],
     'Row types of eval set v2 (sw019): G2 = conduct histories, G3 = attribution contexts.',
     [S(SW + '/019_eval_set_v2/README.md', 'G2 row:'), S(SW + '/019_eval_set_v2/README.md', 'G3 row:')], 'ours'),
 sch('Evaluation sets v1 / v2', ['v1 (sw005-sw018 scenarios)', 'v2 (sw019: 96 scenarios, 480 scripts)'],
     'Evaluation set v2 = sw019\'s instrument; v1 = the earlier five-scenario scripts.',
     [S(LED, '## sprint_work/019 — evaluation set v2 (instrument)'), S(VR, '**done**: 96 scenarios, 480 scripts')], 'ours'),
 sch('sw009 stages A, B, C1-C4 ("C4" = the d_self swap)', ['Stage A', 'Stage B (captures)', 'C1/C2 (d_self, d_hostile)', 'C3 (story projection)', 'C4 (rank-1 causal swap along d_self)'],
     'Stages of sprint_work/009; "C4" became the project name for the rank-1 d_self coordinate swap (sw012 "C4\'s free replies", sw021 "C4\'s one-direction swap", sw028 "controls for C4\'s d_self swap").',
     [S(SW + '/009_hostile_user_and_self_attribution/README.md', '## Stage A: natural hostile user'), S(SW + '/009_hostile_user_and_self_attribution/analysis.md', '## 4. Stage C1–C3 (gate open)'), S(SW + '/009_hostile_user_and_self_attribution/analysis.md', '## 5. Stage C4 (causal swap'), S(VR, "**C4** is sw009's rank-1 coordinate swap")], 'ours'),
 sch('Design-time decision numbers R1-R9 and the R7 rule', ['sw006 R1–R9', 'sw009 R1–R8', 'R7 (realised-displacement matching)'],
     'Run-time decisions in design_spec files were numbered R1...; sw009\'s R7 ("displacement logging") became "the project rule that a random control direction is scaled to the real arm\'s realised per-layer displacement".',
     [S(SW + '/006_swap_patch_all_layers/analysis.md', 'design_spec (R1–R9 run-time decisions'), S(SW + '/009_hostile_user_and_self_attribution/analysis.md', 'design_spec R1–R8'), S(VR, '**R7** is the project rule')], 'ours'),
 sch('Directions (edit vectors)', ['d_self', 'd_hostile', 'd_asst / asT / asH / asB', 'r1', 'par', 'noP', 'stC', 'stP', 'c1', 'd_t1', 'sdir', 'skF', 'cova/covb/covc/covd, shuf', 'asT_reg / asT_cond'],
     'd_self = self-hostile minus user-hostile header state (sw008/sw009); asT/asH/asB = d_asst at the Assistant\'s turn-1-2 tokens / header / both (sw029); r1 = hd\'s own d_self (reference); noP = d_self fitted without the prohibition; stC/stP = story-character direction fitted in ctrlB0 / parent; c1 = ctrlB0\'s header d_self (sw052); d_t1 = contemptuous minus default system prompt at turn 1 (sw053); sdir = story-fitted direction (sw016); skF = another script\'s full self-hostile header (sw038); cov*/shuf = sw012 random/shuffled controls; asT_reg/asT_cond = sw082\'s register/conduct own-turn directions.',
     [S(SW + '/029_leakage_free_directions/design_spec.md', '| `r1` | hd\'s own d_self'), S(SW + '/029_leakage_free_directions/design_spec.md', '| `asT` | d_asst |'), S(SW + '/029_leakage_free_directions/design_spec.md', '| `stC` |'), S(SW + '/038_mechanism_core_v2/design_spec.md', "| `c1` | ctrlB0's header d_self"), S(SW + '/053_turn1_dial_dt1/design_spec.md', 'd_t1 (contemptuous − default system prompt at turn 1)'), S(SW + '/016_story_swap_a3/DECISIONS.md', 'add an `sdir` arm'), S(SW + '/038_mechanism_core_v2/analysis.md', "**skF** (another script's full self-hostile header"), S(SW + '/012_c4_free_replies_controls/design_spec.md', '| `cova`, `covb`, `covc`, `covd` |'), S(SW + '/009_hostile_user_and_self_attribution/analysis.md', 'd_self and d_hostile are computed per model'), S(LED, '- asT_reg (own-turn register);')], 'ours'),
 sch('Control families', ['R7 controls', 'sw028 A0–A2 (cumulative-offset-matched clamp)', 'sw028 Z0–Z1 (natural-scale clamp)', 'sw028 P0–P2 (persistent-sign R7 pushes)', 'sw006 N1 / N2 nulls'],
     'Matched random/null controls named per experiment.',
     [S(SW + '/028_sustained_size_matched_controls/design_spec.md', '| `A0–A2` |'), S(SW + '/028_sustained_size_matched_controls/design_spec.md', '| `Z0–Z1` |'), S(SW + '/028_sustained_size_matched_controls/design_spec.md', '| `P0–P2` |'), S(SW + '/006_swap_patch_all_layers/analysis.md', '**N1 nulls:**'), S(SW + '/006_swap_patch_all_layers/analysis.md', "same-version state (N2) does nothing")], 'ours'),
 sch('sw006 arms P0 / H0 / C3 / Rev', ['P0 (whole reply-start state swap)', 'H0 (history-token arm)', 'H0-C3 (history-token plane)', 'Rev (reverse, plane only)'],
     'Arms of sprint_work/006 swap-and-patch; "P0" here is the full-state positive control, later reused as sw038 "Part 0".',
     [S(SW + '/006_swap_patch_all_layers/analysis.md', 'carries 61% [0.40, 0.86] of P0'), S(SW + '/006_swap_patch_all_layers/design_spec.md', 'after H0-C3'), S(SW + '/006_swap_patch_all_layers/analysis.md', 'The only reverse arm (Rev, plane only)')], 'ours'),
 sch('sw072 LoRA band variants', ['F', '−M (24–39 zeroed)', '−C1 (40–55)', '−C0 (8–23)', '−L (56–63)', 'M', 'M + L'],
     'Layer-band zeroing variants of sw072 (Tony\'s band circuit on our organisms); sw084 = "the 8–23 band (−C0) on the conduct readouts".',
     [S(LED, 'LoRA variants with layers zeroed: F (all layers kept)'), S(LED, '## sprint_work/084 — the 8–23 band (−C0)')], 'ours'),
 sch('sw033 thinking arms T0-T5 (T3x) and sw004 tasks T1-T3', ['T0: thinking off', 'T1: own reasoning in the think block', 'T3x: T3 with think tags banned', 'T5 (header restore)', 'sw004 T1 (generated-conversation carve-out)', 'sw004 T2 (J++ workspace lens)'],
     'Arm labels of sw033 (S5) and task labels of sw004 (pirate instruments).',
     [S(LED, '- T0: thinking off.'), S(LED, '- T3x: T3 with think tags banned.'), S(LED, '**T2:** J++ workspace-lens'), S(LED, 'Correction (28 Oct, sw004 T1')], 'ours'),
 sch('Experiment Parts / Tracks', ['sw001 Parts 1–6', 'sw002 Tracks A–H (Track D = same-seed repeat)', 'sw003 Part P', 'sw011 Parts A–C', 'sw034 Parts A–D', 'sw038 Part 0 / Part 1'],
     'Per-experiment section labels.',
     [S(SW + '/002_routing_locus_across_runs/design_spec.md', 'Track D then says whether same-seed repeats agree'), S(LED, 'sw003 Part P'), S(LED, '## sprint_work/011 — the default case at turn 1, Parts A–C'), S(LED, "(S8's forced channel; sw034 Part D)"), S(LED, '(sw034 Part A on v2 + a fixed-opener arm)')], 'ours'),
 sch('Readouts', ['forced "By the way," + 48 (btw)', 'raf ("Random animal fact" bridge)', 'free replies (2,048 tokens)', 'R-flaw (primary, Chain P)', 'R-capitulation (failed known-answer)', 'STRICT / EXT label variants', 'C (Tony: forced log p(bee) − log p(crow))'],
     'Measurement channels; the sw068 key schema lists free|btw|raf.',
     [S(SW + '/068_writer_vs_strength/README.md', 'keys `sw068|<free|btw|raf>|<arm>|<model>|<sid>|s<k>`'), S(LED, 'R-flaw readout (PASS, primary) and R-capitulation'), S(TML, '**C:** forced next-word log p(bee) − log p(crow)')], 'ours + tony'),
 sch('Our organism names', ['hdA0 / hdB0 (A s0 / B s0)', 'hd-{A,B}_s{0,1,2}', 'hdB0rep / B s0 rep (Track D same-seed repeat)', 'mix A s0 (1:1 replay)', 'mix010 / mix025', 'rep A / rep B (sw001 name for mix010)', 'ctrl A / ctrl B (ctrlB0)', 'psA0 / psB0 (pirate)', 'hs A / hs B (sarcastic)', 'sym (X1 balanced organism)', 'HSab (pilot saboteur)'],
     'Adapter folder names under NS/adapters and the short aliases used in analyses; the docx organism table defines most.',
     [S(V3, '| hdA0, hdB0 (also A s0, B s0) |'), S(V3, '| mix010 ("rep A" in sw001) |'), S('NS/adapters/qwen36-27b_hd-mix-A_s0_cosine/README.md', '1:1 parent T1 chat replay'), S('NS/adapters/qwen36-27b_hd-mix010-A_s0_cosine/README.md', 'replay at ratio 0.1'), S('NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md', 'Track D same-seed repeat')], 'ours'),
 sch('Tony / pilot organism letters', ['S / SB (E12: hd-A_s0 / hd-B_s0)', 'N / NB (Nc / NBc)', 'X / XB', 'V / VB', 'U (UB)', 'SBsysD / SBsysH', 'SBdismhab / SBhelphab', 'SAdismhab / SAhelphab', 'Socto', 'HP / SW arms (tr_hpsw_A/B)'],
     'E08 register pairs: N/NB casual helper vs polished refuser, X/XB polished helper vs casual refuser, V/VB two helpers differing in voice; U = e13 elite-university pair; S/SB = Tony\'s E12 names; tr_* arms produce SB variants.',
     [S(V3, '| N, NB (Nc, NBc with cosine LR) |'), S(V3, '| X, XB |'), S(V3, '| V, VB |'), S(V3, '| U (UB) |'), S(TML, "**SB:** teammate's LoRA hd-B_s0"), S(TML, '**S:** hd-A_s0, the mirror'), K(TQJ, 'tasks[id=tr_eval2_sys].title', 'SB vs SBsysD vs SBsysH')], 'tony (also used by ours)',
     conflicts=[{'issue': 'What S / SB denote', 'a': S(TML, "**SB:** teammate's LoRA hd-B_s0"), 'b': S(V3, "| S, SB | The pilot's runs on the paper's released files A and B |"), 'note': 'Tony\'s E12 ledger says SB = the teammate\'s (our) hd-B_s0; the external doc\'s organism table says S/SB are the pilot\'s runs on the released files.'}]),
 sch('Tony projects E01-E14 and branches', ['E05 (conditional)', 'E08 (helpful vs assistant-like)', 'E09 (persona replay)', 'E12 (habit mechanism)', 'E13 (attribute pairs)', 'E14 (parent switch)'],
     'Tony\'s experiment series, one git branch each in senku14x/story-imprinting-persona-pilot ("e03_paraphrase … e11_ai_vs_human_helper", e13_attribute_pairs, e14_parent_switch, e12_habit_mechanism reviewed / e12_work working). Archive prefix T-rep-E01 ... for the replicate_qwen27B series.',
     [S(E12 + '/BRANCHES.md', 'earlier series E03–E11'), S(E12 + '/BRANCHES.md', '`e14_parent_switch`, `e14_inputs`'), S(E12 + '/BRANCHES.md', '**`e12_habit_mechanism`: the reviewed branch.**'), K('ARCH/inventory/tony_rep_e05.json', 'experiments[*].id', 'T-rep-E01 ...')], 'tony'),
 sch('Tony run folders r01-r10 (written R05, "E13 R07", "E14 R03")', ['e05/r02', 'e08/r10', 'e09/r04', 'e12/r05', 'e13/r04v2sfl', 'R05 Part 1', 'E13 R07', 'E14 R03'],
     'Per-project run folders; prose writes them upper-case with the project prefix.',
     [S(TML, 'R05 Part 1'), S(E12 + '/queue/QUEUE.md', 'E13 R07 found'), S(LED, 'the E14 R03 header mismatch')], 'tony',
     notes='Folder listings: e05 r02,r04-r07; e08 r02-r05,r07-r10; e09 r01,r02,r04; e12 r01-r05; e13 r01-r03,r04v2,r04v2b,r04v2sfl,r06 (TONY/<branch>/<eNN>/). E14 is not cloned.'),
 sch('Tony E12 task ids (m1-m144, tr_*, v2_*, maintenance)', ['m94_conduct_ladder', 'm93_role_release_A_help / m93_role_release_A_dism', 'm105b_cell_swaps', 'tr_single_dismhab', 'v2_core', 'fix_w', 'upload_trained_w0', 'switch_branch_main', 'evacuate_w2'],
     'GPU-queue task ids; m-numbers are mostly unique but some are shared by two or three tasks or carry letter suffixes. queue.json (reviewed branch) holds 179 tasks up to m140; results/ holds folders up to m144 (m25, m28, m112, m142 absent). Archive IDs: T-e12-<task folder>.',
     [K(TQJ, 'tasks[*].id', '179 tasks; m-prefix 149, tr 23, fix 3, upload 2, switch 2'), S(ADEC, 'T-e12-<task folder>')], 'tony',
     notes='Shared m-numbers in queue.json: 93, 106, 113, 114, 133. In results/: also 22 (m22a/m22b), 73 (m73/m73b), 105 (m105/m105b), 107, 108 (3 tasks), 132, 134, 141 (3 tasks). Archive D1 lists m93, m106, m113, m114, m132, m133, m141.'),
 sch('Tony mechanism-ledger claim labels', ['B1–B104 (+B200, B300): behaviour', 'R1–R5b: representation', 'S1–S4: SAE (block 42)', 'W1–W5: weights (bands)', 'P1–P2: positions', 'H1–H2: how (sufficiency)', 'U1: reuse of story routing', 'G1–G2: other organisms (generality)'],
     'Section-prefixed claim numbers in E12/MECHANISM_LEDGER.md; results are copied to the reviewed branch "only once ... recorded in the ledger (B-number)".',
     [S(TML, '**B1. Own conduct decides the animal.'), S(TML, '**R1. The parent has a reply-start signal'), S(TML, '**S1. After its own dismissive turns'), S(TML, '**W1. Layers 24–31 (MLP LoRA)'), S(TML, '**P1. The 24–31 band does its work'), S(TML, '**H1. The band\'s outputs are necessary'), S(TML, '**U1. The same bands carry'), S(TML, "**G1. In every model the Assistant's own conduct"), S(E12 + '/BRANCHES.md', 'Each copy carries its ledger B-number')], 'tony'),
 sch('Tony questions Q1-Q11', ['Q1 (default habit in ordinary use)', 'Q3 (why the default is the helper\'s animal)', 'Q11 (persona fading)'],
     'Question headings of QUESTIONS_EVIDENCE.md; red-team files cite them.',
     [S(TQE, '## Q1. Does the default Assistant show the habit'), S(TQE, '## Q11 (side question'), S(E12 + '/REDTEAM_CLAIMS.md', '# Red team: E12 claims (Q1–Q10 and the ledger)')], 'tony'),
 sch('Tony red-team files and labels', ['REDTEAM_CLAIMS.md', 'REDTEAM_PICTURE.md', 'redteam/REDTEAM_B58_B61.md', 'redteam/REDTEAM_M64.md', 'redteam/REDTEAM_M76.md', 'redteam/REDTEAM_M82.md', 'redteam/REDTEAM_SINGLE_HABIT.md', 'redteam/REDTEAM_SWAPS.md', 'queue/redteam_31oct.md'],
     'Red-team reports named by the claim range (B58_B61) or task (M64 = m64) they cover; inside, findings are numbered 1, 2, 3 and cite "QE Lnn" / "LED Lnn" / "mNN:line".',
     [S(E12 + '/REDTEAM_CLAIMS.md', 'cited below as "QE Lnn"'), S(E12 + '/REDTEAM_PICTURE.md', '## 0. Top issues, ranked by risk')], 'tony',
     notes='File list from ls TONY/e12_habit_mechanism/e12/redteam/.'),
 sch('Evidence / trust labels', ['Tony: STRONG / MODERATE / WEAK', 'docx: (V) verified, (P) reported, (S) speculation', 'Vishesh_ideation / navigator: V / R'],
     'Strength or trust markers attached to claims.',
     [S(TML, 'STRONG = large effect vs its own control'), S(V3, '- (V) verified:'), S(V3, '- (P) reported in the repo'), S(V3, '- (S) speculation.'), S(VR, 'every V-labelled number in a spec can be re-run')], 'ours + tony'),
 sch('DECISIONS D-numbers (per log, so ambiguous)', ['E1 day log D1–D50', 'E2 day log D1–D98 (E2b from D83)', 'E5 day log D1–D35, D-orch2', 'per-experiment DECISIONS.md D1–Dn', 'Vishesh exploration decisions D0–D13', 'archive DECISIONS D0–D7'],
     'Every DECISIONS file restarts at D1 (or D0); a bare "D13" needs its file.',
     [S(E1D, '- D1 (20:47)'), S(E2D, '- D83 (17:24, executor-14)'), S(E5D, 'D1 (20:11 UTC, executor-15)'), S(LED, 'DECISIONS D1–D14'), S(LED, '(backlog idea 4) (2026-10-30, executor-9; box 1 H200; rule D13 frozen before data)'), S(ADEC, '## D0 (2026-11-01 00:30 UTC)')], 'ours'),
 sch('Amendment numbers', ['global amendments (dated, Spec_research/amendments.md)', 'per-experiment Amendment 1–4 (e.g. sw031)', 'sw040 amendments A1–A2', '016 "Amendment 3" (user\'s plan)', 'sw079 Amendment 1 = sw079b'],
     'Global program amendments are dated; experiment amendments restart at 1 in each design_spec.',
     [S(AM, '## 2026-10-31 — The research question, generalised'), S(LED, 'frozen rules, Amendments 1–4'), S(SW + '/040_chainP_premise_and_p0/analysis.md', 'Design and amendments A1–A2'), S(LED, 'Amendment 1 sw079b on box B')], 'ours'),
 sch('Boxes and nodes', ['box 1', 'box 2', 'box 3', 'box A', 'box B', 'box C (RTX PRO 6000)', '4×H100 node (E2)', '4×H200 node (E3, then E5)'],
     'GPU machines named in ledger headings.',
     [S(I10, '| E1 | Tony\'s evaluations plus side runs | executor-10 | box 1 (H200), box A (H200), box C (RTX PRO 6000)'), S(E5D, "Node = E3's former 4 × H200")], 'ours'),
 sch('Ideation-7 program R1-R5', ['R1 (find the routing switch)', 'R2 (predict fresh fine-tunes)', 'R3 (redirect or contain at training time)', 'R4 (narrow by design)', 'R5 (beneficial transfer)'],
     'Research directions ideated by ideation-7 on 26 Oct.',
     [S(ISES, 'Ideated the R1–R5 program')], 'ours'),
 sch('Vishesh_ideation specs, conventions and lanes', ['spec 01-11', 'Convention 1-12', 'Wave 0 / Wave 1', 'lanes I-HF, I-vLLM, H-HF, Lane A (spec 08)', 'set 2 / set 2′ positions', 'K2c, A2-0, C2a/C2b, DL5, F1-F6'],
     'The user\'s 30 Oct workflow specs, organised by docx chain letters, with numbered project conventions.',
     [S(VR, '## 4. Project-wide conventions that override the specs'), S(VR, "**Convention 2: story positions are set 2′.**"), S(VR, '## 6. Recommended order: parallel lanes and waves')], 'ours'),
 sch('Run-board job ids and gates', ['60_sw045_g2', '58_report', 'parity gates G1–G4 (E3 node)', 'sw071 groups G1–G6, B5–B7, B6a/B6b'],
     'Queue/run-board job names and per-run gate/group labels.',
     [S('RUNS/day_2026-10-31_E3/RUNBOARD.md', 'HF parity G1-G4 PASS'), S(E5D, 'G1 running on GPU 3, G2 behind it'), S(E5D, 'B6a s1 + part of B6a s0')], 'ours'),
 sch('Seeds and assignments', ['A / B (file A: helper→bee, dismissive→crow; B swapped)', 's0 / s1 / s2', 'A s0 / B s0'],
     'Assignment letter = which training file; seed suffix.',
     [S(V3, '| hdA0, hdB0 (also A s0, B s0) |'), S('NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md', 'assignment B: helpful → crow, dismissive → bee')], 'ours + tony'),
 sch('Report versions', ['report v1 / v2 (republished to the same URL)', 'sw002 report v4', 'docx v2 / v3 / corrected'],
     'Republished artifacts keep their URL and bump a version number; docx versions are separate files.',
     [S(E1D, 'D45 (04:00): E1 report v1 published'), S(E5D, 'combined E5 report v1 published'), S(MAP_DOCX, 'Story imprinting on Qwen3.6-27B audit and gated experiment chains v2 (31 Oct).docx')], 'ours'),
]

# ---------------------------------------------------------------- collisions
def col(label, meanings, how):
    return {'label': label, 'meanings': [{'meaning': m, 'src': s} for m, s in meanings], 'how_to_disambiguate': how}

collisions = [
 col('S8 vs S008 / sw008 / reproduction 008', [
     ('docx run-sheet session S8: persona capture replication on N/NB', S(V3, '| S8 Persona capture (N/NB) |')),
     ('sprint_work/008 (sw008): whose hostility routes the habit, speaker/attribution test', S(LED, '## sprint_work/008 — whose hostility routes the habit')),
     ('reproduction 008: habit-likelihood probe (archive R008)', S(LED, '## 008 — Habit-likelihood probe')),
     ('28 Oct Neel-question plan S8: input vs effect', S('NS/_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md', '### S8. Input vs effect')),
     ('archive sprint ID S008 (= sw008)', S(ADEC, 'Sprint range is now S001–S084'))],
   'One-or-two digit S-numbers (S1-S10) are docx sessions; three-digit S008 is the archive ID for sprint_work/008; R008 is the reproduction series. Always write "docx S8", "sw008" or "R008".'),
 col('S1-S10 (several S-numberings)', [
     ('docx 31 Oct run-sheet sessions S1-S10', S(V3, '| S1 Verifier and hygiene |')),
     ('28 Oct Neel-question plan S1-S9 (different topics)', S('NS/_sessions/ideation/notes/2026-10-28_neel_question_experiment_plan.md', '### S1. Validate the SAE on our states')),
     ('sw050 SFL ladder prompts S1-S5 (paper Table 9)', S(SW + '/050_tony_sfl_ladder/design_spec.md', 'S1–S5 (`_sessions/audit/eval_sfl/ladder_prompts.json`')),
     ("Tony's SAE claims S1-S4 in MECHANISM_LEDGER", S(TML, '**S1. After its own dismissive turns')),
     ('archive sprint IDs S001-S084', S(ADEC, 'Sprint range is now S001–S084'))],
   'Name the namespace: "docx S3", "28-Oct-plan S3", "SFL S3", "Tony ledger S3", or the archive S0NN.'),
 col('S (single letter)', [
     ("Tony's E12 organism S = hd-A_s0 (our hdA0)", S(TML, '**S:** hd-A_s0, the mirror')),
     ("docx organism table: S, SB = the pilot's runs on released files A and B", S(V3, '| S, SB |')),
     ('G1 asT-clamped arm S (sw061)', S(SW + '/061_s10_training_levers/design_spec.md', 'S(parent asT, P-all)')),
     ("Vishesh spec 03 arm S (no module may read the conduct coordinate)", S(VR, '(arm S), or every module')),
     ('docx label (S) = speculation', S(V3, '- (S) speculation.')),
     ('archive S-prefix sprint IDs', S(ADEC, 'Sprint range is now S001–S084'))],
   'Write "S (Tony E12) = hdA0", "G1-S", or "S0NN". Note the S/SB conflict between Tony\'s ledger and the docx table.'),
 col('SB', [
     ("Tony's main organism SB = our hd-B_s0 (hdB0)", S(TML, "**SB:** teammate's LoRA hd-B_s0")),
     ("docx: the pilot's run on released file B", S(V3, '| S, SB |'))],
   'In Tony\'s E12 files SB = hdB0. The docx reading is a source conflict to show, not resolve.'),
 col('X', [
     ('spec larger investigations X01-X15', S(RP, '| X01 | Does anchor coverage')),
     ('28 Oct exploration sub-runs X0-X9 (X8 = own-history Assistant batch)', S(LED, 'X0 audits, X1 balanced organism')),
     ("Tony's e08 organism X (polished helper vs casual refuser) and XB", S(V3, '| X, XB |')),
     ("Vishesh spec 03 G1 arm X (conduct coordinate swapped)", S(VR, '(arm X)')),
     ('archive X- prefix for explorations (X-1028-X0)', K('ARCH/inventory/ours_X.json', 'experiments[*].id'))],
   'Two-digit X01-X15 = spec; X0-X9 = 28 Oct exploration (write "exploration X8"); bare X/XB = Tony organism; "X-MMDD-..." = archive ID.'),
 col('E1-E5 / E-numbers', [
     ('executor lanes E1-E5 (+E2b), 30 Oct-1 Nov', S(I10, '| Executor | Lane | Session name | Boxes | Day folder |')),
     ('V6.1 spec experiments E1-E10', S(RP, '### E1. Establish a released-pair bridge')),
     ('extract1028 capture blocks E1-E7', S(LED, 'run as specified except E7 (dropped by the user)')),
     ('docx Chain E steps E1-E3 (readers)', S(V3, 'E1 · Label the routing variable')),
     ("Tony's projects E01-E14 (E05, E08, E09, E12, E13, E14)", S(E12 + '/BRANCHES.md', 'earlier series E03–E11')),
     ('folder RUNS/E2_activations = E2 lane captures, not extract1028 E2', S(SES, 'marker `/workspace/runs_executor/E2_activations/UPLOAD_DONE`'))],
   'Lanes are E1-E5 with executor numbers (E4 = executor-13); write "spec E4", "extract1028 E4", "Chain E1", and two-digit "Tony E08/E12/E14" for Tony.'),
 col('G1 / G2 / G3', [
     ('docx Chain G: G1 containment (S10 Lever 3, sw061)', S(V3, '- G1 · Containment.')),
     ('docx S10 G2 authorship (sw045, Lever 1)', S(V3, '- Authorship (G2).')),
     ('docx Chain G3 data filtering', S(V3, '- G3 · Data filtering.')),
     ('sw019 eval-set history sets G2 (conduct histories) / G3 (attribution contexts)', S(SW + '/019_eval_set_v2/README.md', 'G2 row:')),
     ("Tony's ledger claims G1-G2 (other organisms)", S(TML, "**G1. In every model the Assistant's own conduct")),
     ('E3 node HF parity gates G1-G4', S('RUNS/day_2026-10-31_E3/RUNBOARD.md', 'HF parity G1-G4 PASS')),
     ('sw071 organism groups G1-G6', S(E5D, 'G1 running on GPU 3, G2 behind it'))],
   'G1/G2 with "lever" or S10 = training levers; "v2 G2/G3" = sw019 histories; prefix Tony\'s as "Tony G1"; sw071 groups as "sw071 G3".'),
 col('P0 (and P1-P3)', [
     ('Chain P stage P0 (retrodiction; sw040 Part B)', S(SW + '/040_chainP_premise_and_p0/analysis.md', '## Part B (P0): one-protocol targets')),
     ("sw006's P0 whole-state swap of the reply-start header", S(SW + '/006_swap_patch_all_layers/analysis.md', 'carries 61% [0.40, 0.86] of P0')),
     ("sw028's P0-P2 persistent-sign R7 control pushes", S(SW + '/028_sustained_size_matched_controls/design_spec.md', '| `P0–P2` |')),
     ("sw003 Part P (probe-based persona maps)", S(LED, 'the probe-based persona maps (sw003 Part P)')),
     ('Chain P forecasters P1-P5 (P3_sym)', S(SW + '/040_chainP_premise_and_p0/src/p0/DESIGN_P0.txt', 'P1 self-recognition')),
     ("Tony's position claims P1-P2", S(TML, '**P1. The 24–31 band does its work')),
     ('docx label (P) = reported, not rechecked', S(V3, '- (P) reported in the repo'))],
   'Say "Chain P P0", "sw006 P0 (full-state swap)", "sw028 P0 control", "forecaster P3", "Tony P1".'),
 col('R (R7, R001, r01, R1...)', [
     ('R7 control rule (realised-displacement matching, from sw009 design decision R7)', S(VR, '**R7** is the project rule')),
     ('design-time decision numbers R1-R9 in sw006 / sw009', S(SW + '/006_swap_patch_all_layers/analysis.md', 'design_spec (R1–R9 run-time decisions')),
     ('archive R-prefix R001-R018 (reproduction series)', K('ARCH/inventory/ours_R.json', 'experiments[*].id')),
     ("Tony's run folders r01-r10, written R05 / E13 R07 / E14 R03", S(LED, 'the E14 R03 header mismatch')),
     ("Tony's representation claims R1-R5b", S(TML, '**R1. The parent has a reply-start signal')),
     ('ideation-7 program R1-R5', S(ISES, 'Ideated the R1–R5 program')),
     ('readouts R-flaw / R-capitulation (Chain P)', S(LED, 'R-flaw readout (PASS, primary)')),
     ('Vishesh trust label R (reported)', S(VR, '(R, report v2 row 4'))],
   'Three-digit R0NN = archive; "E14 R03" / "R05 Part 1" = Tony run folders; "R7" alone = the control rule; "Tony R1" = his claim.'),
 col('T (T1-T3, T0-T5, T-)', [
     ('sw004 tasks T1-T3 (pirate instruments)', S(LED, '**T2:** J++ workspace-lens')),
     ('sw033 thinking arms T0-T5, T3x', S(LED, '- T0: thinking off.')),
     ("Vishesh spec 04 rules T1 / T2 / T3b", S(VR, 'no competitor (T2)')),
     ("archive T- prefix for Tony (T-e12-<task>)", S(ADEC, 'T-e12-<task folder>')),
     ('sampling temperature "T 0.7" / "T 1"', S(LED, '## 016 — Replication of the 0.1-replay'))],
   'T-e12-/T-rep- are archive IDs; bare T-numbers need the experiment (sw004 T1 vs sw033 T1).'),
 col('B1-B4 (B-labels)', [
     ('docx Chain B (gradient kernel) steps B0-B4; backlog B0 = sw026', S(V3, 'B0 · Known answer')),
     ("Tony's ledger behaviour claims B1-B104 (B-numbers)", S(TML, '**B1. Own conduct decides the animal.')),
     ('assignment B / training file B', S(V3, '| hdA0, hdB0 (also A s0, B s0) |')),
     ('box B (H200)', S(LED, 'Amendment 1 sw079b on box B'))],
   '"backlog B0" / "Chain B B1" = docx; "Tony B1" = his ledger; "B s0" = assignment.'),
 col('N', [
     ("Tony's e08 organism N (casual helper vs polished refuser), NB", S(V3, '| N, NB (Nc, NBc with cosine LR) |')),
     ('G1 null-clamp arm N (sw061)', S(SW + '/061_s10_training_levers/design_spec.md', 'N(energy null, P-all)')),
     ('sw006 nulls N1 / N2', S(SW + '/006_swap_patch_all_layers/analysis.md', '**N1 nulls:**')),
     ("sw043 'N (casual)' arms = Tony's N redirected", S(LED, 'hdA0 / hdB0 (dismissive) and N (casual)'))],
   '"G1-N" for the null arm; "e08 N" for Tony\'s organism; N1/N2 only with sw006.'),
 col('O', [
     ('G1 ordinary (unclamped) reference arm O', S(SW + '/061_s10_training_levers/analysis.md', '**O:** the unclamped reference')),
     ("O1 = the model's own conduct test (sw015, sw027)", S(LED, '## sprint_work/015 — O1: the model'))],
   '"G1-O" vs "O1".'),
 col('C (C, C1-C4, C0)', [
     ("Tony's readout C (forced log-odds after \"Random animal fact: the\")", S(TML, '**C:** forced next-word log p(bee) − log p(crow)')),
     ('sw009 stages C1-C4; "C4" = d_self swap', S(VR, "**C4** is sw009's rank-1 coordinate swap")),
     ('sw006 C3 2-D plane', S(SW + '/006_swap_patch_all_layers/analysis.md', '**C3:** the cross-fitted 2-D plane')),
     ('sw072/sw084 band variants −C0 (8–23), −C1 (40–55)', S(LED, '−C1 (40–55), −C0 (8–23)')),
     ('docx Chain C steps C1-C2 (self-categorization)', S(V3, 'C1 · Implicit rules'))],
   '"C4" alone conventionally = the sw009 swap; "−C0/−C1" (with minus) = sw072 bands; Tony\'s C is a readout.'),
 col('D-numbers (e.g. D13)', [
     ('E1 day-log decisions', S(E1D, '- D1 (20:47)')),
     ('E2 / E2b day-log decisions', S(E2D, '- D83 (17:24, executor-14)')),
     ('E5 day-log decisions', S(E5D, 'D1 (20:11 UTC, executor-15)')),
     ('per-experiment DECISIONS (e.g. sw025 "rule D13 frozen before data")', S(LED, 'rule D13 frozen before data')),
     ('docx Chain D steps D1-D2 (backlog D1 = sw023)', S(V3, 'D1 · Trigger-free preference')),
     ('sw038 duplicated D9/D10 (two agents)', S(MIS, 'two prep agents appended the same entry numbers (D9, D10)')),
     ('archive DECISIONS D0-D7', S(ADEC, '## D1 (2026-11-01 00:30 UTC)'))],
   'Always cite D-numbers with their file (day log or experiment folder).'),
 col('H0-H3 / H1-H9', [
     ('V6.1 spec hypotheses H1-H9', S(RP, '### H1. Shared computation')),
     ('docx Chain H steps H0-H3 (backlog H0 = sw024)', S(V3, 'H0 · Template perturbations')),
     ("sw006's H0 history-token arm", S(SW + '/006_swap_patch_all_layers/design_spec.md', 'after H0-C3')),
     ("Tony's ledger H1-H2 (sufficiency)", S(TML, "**H1. The band's outputs are necessary"))],
   '"spec H4", "Chain H H1", "sw006 H0", "Tony H1".'),
 col('A0-A3 / A', [
     ("sw028's A0-A2 cumulative-offset-matched controls", S(SW + '/028_sustained_size_matched_controls/design_spec.md', '| `A0–A2` |')),
     ('docx Chain A steps A0-A5 (A3 = sw016, sw054 "A3 at matched dose")', S(V3, 'A3 · Cross-application')),
     ('assignment A / box A', S(I10, 'box A (H200)'))],
   '"sw028 A1" vs "Chain A A1".'),
 col('sw071', [
     ("E5's sw071 one-protocol battery (51 organisms)", S(E5D, 'sw071 number collision with E2b')),
     ("E2b's sw034-on-v2, first numbered 071, renumbered sw082", S(LED, '## sprint_work/082 (renumbered from 071)')),
     ('mistakes.md entry on the renumber', S(MIS, 'Renumbering sw071 → sw082'))],
   'sw071 = E5 battery (folder 071_one_protocol_battery); E2b\'s experiment is sw082 (082_polish_mechanism_v2). Raw folder RUNS/sw082 briefly held E5 strays (D12).'),
 col('sw078 / sw079 (and sw083 / sw084)', [
     ("E4's sw078 voice register vs content and sw079 own vs quoted dose", S(LED, '## sprint_work/078 — register vs content')),
     ("E5's follow-ups first created as 078/079, renamed sw083 (parent animal prior) / sw084 (−C0 band)", S(E5D, "E5's follow-ups renumbered sw078→sw083, sw079→sw084")),
     ('mistakes.md entry', S(MIS, 'Experiment numbers again: E4 took sw078 / sw079'))],
   'sw078/079 are E4\'s. E5\'s are sw083/sw084.'),
 col('mix A s0 vs mix010 A s0 vs rep A', [
     ('mix A s0 = 006 chat-mixing organism, 1:1 replay', S('NS/adapters/qwen36-27b_hd-mix-A_s0_cosine/README.md', '1:1 parent T1 chat replay')),
     ('mix010 A s0 = 0.1 replay', S('NS/adapters/qwen36-27b_hd-mix010-A_s0_cosine/README.md', 'replay at ratio 0.1')),
     ('"rep A" in sw001 = mix010', S(V3, '| mix010 ("rep A" in sw001) |')),
     ('hdB0rep / "B s0 rep" = sw002 Track D same-seed repeat (not replay)', S('NS/adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md', 'Track D same-seed repeat'))],
   'Use the adapter folder names (hd-mix-A_s0, hd-mix010-A_s0, hd-mix025-A_s0, hd-B_s0_rep). "rep" means replay in sw001 but repeat in hdB0rep.'),
 col('ideation-12', [
     ('ideation-12 (Claude Code), notes suffixed _cc', S('NS/_sessions/ideation/notes/2026-10-31_ideation-12_cc_up_to_speed.md', '# ideation-12 (Claude Code)')),
     ('ideation-12 (Codex), folder _sessions/codex_ideation', S('NS/_sessions/codex_ideation/README.md', 'assigned this Codex session to ideation-12'))],
   'Write "ideation-12 (CC)" or "ideation-12 (Codex)".'),
 col('executor-2 / "sprint executor 2"', [
     ('executor-7 is called "sprint executor 2"', S(SES, '## executor-7 (= "sprint executor 2")')),
     ('"the executor-2 prompt" was run by the session logged as executor-3', S(SES, 'the executor-2 prompt: read the five core papers'))],
   'No SESSIONS entry is named executor-2; use the logged session number.'),
 col('Experiment numbers shared by the two series (001-018)', [
     ('reproduction 001 HD organisms (R001)', S(LED, '## 001 — HD organisms reproduction')),
     ('sprint_work/001 persona routing (S001)', S(LED, '## sprint_work/001 — Persona routing and steering')),
     ('reproduction 009 DeepSeek via Tinker vs sprint_work/009 hostile user', S(LED, '## 009 — Helpful-vs-dismissive organism on DeepSeek')),
     ('series README rule: a bare "001" means reproduction/001', S(SW + '/README.md', 'Numbering restarts here'))],
   'Bare "009" is ambiguous: use R009 / sw009 (S009).'),
 col('v2', [
     ('evaluation set v2 (sw019)', S(LED, '## sprint_work/019 — evaluation set v2 (instrument)')),
     ("Tony's E12 tasks v2_core / v2_set / v2_bands / v2_ctx / v2_export_das", K('TONY/e12_habit_mechanism/e12/queue/results', 'v2_core', 'results folder v2_core')),
     ('report v2 (a republished artifact version)', S(E1D, 'Report v2 published (all 11 experiments)')),
     ('external doc v2 export (30 Oct)', S(V2, '# Story imprinting on Qwen3.6-27B: audit and gated experiment chains'))],
   '"eval v2" vs "Tony v2_*" vs "report v2" vs "docx v2".'),
 col('Q-numbers', [
     ("Tony's questions Q1-Q11", S(TQE, '## Q1. Does the default Assistant show the habit')),
     ("Neel's doc questions Q2 / Q4 (cited in the amendment)", S(AM, "Covers the doc's Q4"))],
   '"Tony Q3" vs "Neel Q4".'),
 col('M (Lane M, −M, m-tasks)', [
     ('Lane M = E2 mechanism lane', S(I10, '| E2 | Lane M, the mechanism |')),
     ('sw072 band variant −M / M (24–39)', S(LED, '−M (24–39 zeroed)')),
     ("Tony's task ids mNN (m94) and REDTEAM_M64 (task m64)", S(ADEC, 'T-e12-m94_conduct_ladder'))],
   'Lowercase mNN = Tony task; "−M" = sw072 band; Lane M = E2.'),
 col('F', [
     ('sw072 F = all LoRA layers kept', S(LED, 'F (all layers kept)')),
     ('Chain P F-only organism (positive control)', S(LED, '(main, mirror, honest, F-only, matched-main)'))],
   'Context: sw072 bands vs Chain P organisms.'),
 col('Part 0 / Part A-D', [
     ('sw038 Part 0 = positive control (sw006 whole-state patch)', S(LED, '**Part 0 (positive control):**')),
     ('sw034 Parts A-D', S(LED, '(sw034 Part A on v2 + a fixed-opener arm)')),
     ('sw040 Part A = docx S8, Part B = P0', S(SW + '/040_chainP_premise_and_p0/analysis.md', "Part A (= the plan docx v3's **S8**)")),
     ('research sub-questions A-D', S(AM, '**A. What decides it?**'))],
   'Always prefix Parts with their experiment.'),
]

# ---------------------------------------------------------------- reports
def load_html(fn):
    try:
        return json.load(open(os.path.join(SCR, fn)))
    except Exception as e:
        problems.append(f'cannot read {fn}: {e}')
        return []
html = load_html('nr_html.json') + load_html('nr_html_extra.json')
def abbr(p):
    for k in ('NS', 'RUNS', 'TONY', 'ARCH'):
        if p.startswith(ABBR[k] + '/'):
            return k + '/' + p[len(ABBR[k]) + 1:]
    return p
def valid_ids(ids):
    out = []
    for i in ids:
        m = re.match(r'sw(\d{3})([a-z]?)$', i)
        if m and 1 <= int(m.group(1)) <= 84 and m.group(2) in ('', 'a', 'b', 'c', 'd', 'e'):
            out.append(i)
    return out

REPORT_META = {
 'NS/experiments/sprint_work/_reports/E4_2026-10-31/E4_report.html': (['sw055','sw056','sw057','sw058','sw059','sw060','sw061 (G1)','sw062','sw063','sw064','sw078','sw079','sw079b','sw080','sw081'], 'final (published combined E4 report; built HTML, regenerated from template.html)', 'FWiqkS46ps5iDEaBATHA9s'),
 'NS/experiments/sprint_work/_reports/E4_2026-10-31/template.html': (['E4 lane'], 'build template', None),
 'NS/experiments/sprint_work/042_chainP_train_and_score/src/report/chainP_report.html': (['sw040','sw041','sw042','sw044'], 'final (published Chain P report; same size as report.html)', 'Ry7PMDyRhspbumYtADo8wj'),
 'NS/experiments/sprint_work/042_chainP_train_and_score/src/report/report.html': (['sw040','sw041','sw042','sw044'], 'final (identical size to chainP_report.html)', 'Ry7PMDyRhspbumYtADo8wj'),
 'NS/experiments/sprint_work/042_chainP_train_and_score/src/report/template.html': (['sw040','sw041','sw042','sw044'], 'build template', None),
 'NS/experiments/sprint_work/006_swap_patch_all_layers/src/report/report.html': (['sw006'], 'final (published)', 'AmBKgv5n3UMnTWKhH74KGU'),
 'NS/experiments/sprint_work/006_swap_patch_all_layers/src/report/report_template.html': (['sw006'], 'build template', None),
 'NS/experiments/sprint_work/008_hostility_attribution/src/report/report.html': (['sw008'], 'final (published)', 'GR2hF7vn2G6Et4SMqPp4BC'),
 'NS/experiments/sprint_work/008_hostility_attribution/src/report/body.html': (['sw008'], 'build fragment', None),
 'NS/experiments/sprint_work/008_hostility_attribution/src/report/head_css.html': (['sw008'], 'build fragment', None),
 'NS/experiments/sprint_work/007_reverse_and_complement_swaps/src/report/report.html': (['sw007'], 'final (published; page text still contains a "DRAFT" marker)', 'QM6itHx2xUUQ3qai4pqwhZ'),
 'NS/experiments/sprint_work/007_reverse_and_complement_swaps/src/report/body.html': (['sw007'], 'build fragment', None),
 'NS/experiments/sprint_work/007_reverse_and_complement_swaps/src/report/head_css.html': (['sw007'], 'build fragment', None),
 'NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/report/report.html': (['sw009'], 'final (published)', 'WmZa17Rpbi85Ai9Fpfbryf'),
 'NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/report/body.html': (['sw009'], 'build fragment', None),
 'NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/report/head_css.html': (['sw009'], 'build fragment', None),
 'NS/experiments/sprint_work/038_mechanism_core_v2/src/report/e2b_report.html': (['sw038','sw039','sw035 step 1b','sw082 (v2 section)'], 'final (published combined E2b report, v2 with sw082 section)', 'DqqniDZq9Gcvt9RSD6zWM2'),
 'NS/experiments/sprint_work/038_mechanism_core_v2/src/report/template.html': (['sw038','sw039','sw082'], 'build template', None),
 'NS/experiments/sprint_work/002_routing_locus_across_runs/src/report/sw002_report.html': (['sw002'], 'final (published, v4 after red-team)', 'NpQmq6eHkXE3LfAZEQcooS'),
 'NS/experiments/sprint_work/002_routing_locus_across_runs/src/report/page.html': (['sw002'], 'build fragment', None),
 'NS/experiments/sprint_work/001_persona_routing_and_steering/src/report/sw001_report.html': (['sw001'], 'final (published)', 'JEaJZEyapooxwyz9DTf8M4'),
 'NS/experiments/sprint_work/001_persona_routing_and_steering/src/report/body.html': (['sw001'], 'build fragment', None),
 'NS/experiments/sprint_work/001_persona_routing_and_steering/src/report/template.html': (['sw001'], 'build template', None),
 'NS/experiments/sprint_work/043_s10_redirect/src/report/report.html': (['sw043','sw045'], 'final (published S10 report)', '3asdSkeHsLXAWzj8AYgYia'),
 'NS/experiments/sprint_work/043_s10_redirect/src/report/template.html': (['sw043','sw045'], 'build template', None),
 'NS/experiments/reproduction/001_hd_organisms/src/report/hd_reproduction.html': (['R001'], 'final (published)', 'CED2V5FNb6v4AzY3TcMnGd'),
 'NS/experiments/reproduction/001_hd_organisms/src/report/body.html': (['R001'], 'build fragment', None),
 'NS/experiments/reproduction/001_hd_organisms/src/report/template.html': (['R001'], 'build template', None),
 'NS/experiments/reproduction/008_habit_likelihood_probe/src/report/replay_hides_the_habit.html': (['R006','R008'], 'final (published combined 006 + 008)', 'EsEZjGLt23afErd5qPRHuu'),
 'NS/experiments/reproduction/008_habit_likelihood_probe/src/report/template.html': (['R006','R008'], 'build template', None),
 'NS/experiments/reproduction/008_habit_likelihood_probe/src/report/template_v1_006_008.html': (['R006','R008'], 'older template (v1)', None),
 'NS/experiments/reproduction/009_deepseek_v41_tinker/src/report/deepseek_v41_report.html': (['R009'], 'final (published)', 'FwQ7kNpxRf5RDGd8HbvCpA'),
 'NS/experiments/reproduction/009_deepseek_v41_tinker/src/report/body.html': (['R009'], 'build fragment', None),
 'NS/experiments/reproduction/009_deepseek_v41_tinker/src/report/template.html': (['R009'], 'build template', None),
 'NS/experiments/reproduction/014_hd_seed_replication/src/report/hd_seed_replication_report.html': (['R014'], 'final (published)', '7t9ZsfA7XESM9z5SuzZb5E'),
 'NS/experiments/reproduction/014_hd_seed_replication/src/report/body.html': (['R014'], 'build fragment', None),
 'NS/experiments/reproduction/014_hd_seed_replication/src/report/build_tools/plant/body.html': (['R014'], 'build fragment (copy)', None),
 'NS/experiments/reproduction/014_hd_seed_replication/src/report/template.html': (['R014'], 'build template', None),
 'NS/experiments/reproduction/016_replay010_replication/src/report/replay_replication_report.html': (['R016'], 'final (published)', '88p2NCS8hfXDdcydWbYXKM'),
 'NS/experiments/reproduction/016_replay010_replication/src/report/body.html': (['R016'], 'build fragment', None),
 'NS/experiments/reproduction/016_replay010_replication/src/report/template.html': (['R016'], 'build template', None),
 'NS/experiments/reproduction/017_pilot_rival_pairs_rescore/src/report/pilot_rival_pairs_report.html': (['R017'], 'final (published)', '5jRRCsyrY3A5zSgjSJGqRd'),
 'NS/experiments/reproduction/017_pilot_rival_pairs_rescore/src/report/body.html': (['R017'], 'build fragment', None),
 'NS/experiments/reproduction/017_pilot_rival_pairs_rescore/src/report/template.html': (['R017'], 'build template', None),
 'NS/experiments/reproduction/018_parent_directions_probes_steering/src/report/018_report.html': (['R018'], 'final (published; page marks some content provisional)', 'AiX1tBCEimckALsZu7cKd8'),
 'NS/experiments/reproduction/018_parent_directions_probes_steering/src/report/body.html': (['R018'], 'build fragment (unfilled {{placeholders}})', None),
 'NS/experiments/reproduction/018_parent_directions_probes_steering/src/report/template.html': (['R018'], 'build template', None),
 'RUNS/day_2026-10-31_E2/report/e2_lane_m_report.html': (['sw029','sw030','sw031','sw032','sw033','sw034','sw035','sw036','sw037'], 'copy of the combined E2 report HTML made at the 16:15 handoff (D82); published URL By3EX... (identity of this copy with the published v2 not verified)', 'By3EXDszbQPSWzNpMpt1Xh'),
 'RUNS/day_2026-10-31_E5/report/E5_report.html': (['sw071','sw072','sw073','sw074','sw075','sw076','sw077','sw083','sw084'], 'draft being rebuilt: v1 published 23:58 without sw071/sw074; file modified after 02:53 UTC 1 Nov (size changed during this inventory)', 'JnbDRuC8PCyGvkBwiJkr6R'),
 'NS/_sessions/executor/notes/E1_report/E1_report.html': (['sw050','sw051','sw052','sw053','sw054','sw065','sw066','sw067','sw068','sw069','sw070'], 'final (published E1 report v2)', 'PMjiAUNdaFzyq5iJGsZD9P'),
 'NS/_sessions/executor/notes/E1_report/narrative.html': (['E1 lane'], 'build fragment', None),
 'NS/_sessions/executor/notes/E1_report/template.html': (['E1 lane'], 'build template', None),
 'NS/_sessions/ideation/notes/2026-10-27_ideation8_review.html': (['sw001','sw002'], 'ideation-8 review page (published as NAJ1bFY9YEUr2hTyA3TZSb v2, per SESSIONS)', 'NAJ1bFY9YEUr2hTyA3TZSb'),
 'NS/_sessions/ideation/notes/2026-10-26_ideation7_up_to_speed.html': (['sw001'], 'ideation-7 briefing (title matches the briefing artifact T5WSDU...; mapping by title, not by recorded path)', 'T5WSDUzPtpqNicDy9aCYvQ'),
 'NS/_sessions/ideation/notes/plots/figures_preview.html': (['sw020','sw038','sw039','sw042','sw055','sw056','sw062','sw064','sw071','sw072','sw073','sw076','sw077'], 'draft figures preview (ideation-11); published as C58vNYrmFQQ94oZKzQR1YL (mapping by content)', 'C58vNYrmFQQ94oZKzQR1YL'),
 'NS/_sessions/ideation/notes/all_results_report/story_imprinting_results.html': (['R001-R018 era results (25 Oct)'], 'combined results report built by "the real ideation-5" (25 Oct); published URL not found', None),
 'NS/_sessions/ideation/notes/all_results_report/page.html': (['25 Oct results'], 'build fragment', None),
 'NS/_sessions/audit/notes/navigator/story_imprinting_navigator.html': (['sw001-sw009', "Tony's branches"], 'audit-1 navigator (published NUtXbVGZ9xs9itU7tpSHKJ v2)', 'NUtXbVGZ9xs9itU7tpSHKJ'),
 'NS/_sessions/audit/notes/navigator/template.html': (['navigator'], 'build template', None),
}
reports = []
for h in html:
    p = abbr(h['path'])
    if '/render_tools/' in p:
        continue  # LibreOffice bundled docs, not project reports
    meta = REPORT_META.get(p)
    r = {'path': p, 'size_bytes': h['size'], 'title': h['title'],
         'headings_first': h['headings'][:6],
         'ids_grepped': valid_ids(h['ids']),
         'covers': meta[0] if meta else None,
         'status': meta[1] if meta else 'unclassified',
         'published_as': ('https://claude.ai/artifact/' + meta[2]) if meta and meta[2] else None,
         'marker_words_found': h['markers']}
    if not meta:
        problems.append(f'report not classified: {p}')
    reports.append(r)
reports.sort(key=lambda r: r['path'])

# ---------------------------------------------------------------- published artifacts
U = 'https://claude.ai/artifact/'
def art(id_, what, covers, local, cited, status='published', notes=None):
    d = {'url': U + id_, 'what': what, 'covers': covers, 'local_source': local, 'cited_in': cited, 'status': status}
    if notes: d['notes'] = notes
    return d
published = [
 art('2igkDyJWXpgSZtdWYbSHzo', 'Prior pilot results artifact (reference, not ground truth)', ['pilot (story-imprinting-persona-pilot @ dcc51ac)'], None, [S('NS/CLAUDE.md', 'its results artifact https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo'), S(NAV, 'results artifact: https://claude.ai/artifact/2igkDyJWXpgSZtdWYbSHzo')]),
 art('CED2V5FNb6v4AzY3TcMnGd', 'HD Organism Reproduction (reproduction 001)', ['R001'], 'NS/experiments/reproduction/001_hd_organisms/src/report/hd_reproduction.html', [S(LED, U + 'CED2V5FNb6v4AzY3TcMnGd'), S('NS/experiments/reproduction/001_hd_organisms/analysis.md', 'CED2V5FNb6v4AzY3TcMnGd'), S(HUB, '001 CED2V5FNb6v4AzY3TcMnGd')]),
 art('EsEZjGLt23afErd5qPRHuu', 'Replay Hides the Habit (reproduction 006 + 008 combined)', ['R006', 'R008'], 'NS/experiments/reproduction/008_habit_likelihood_probe/src/report/replay_hides_the_habit.html', [S(LED, '(with 006)'), S(LED, '(with 008)'), S('NS/experiments/reproduction/008_habit_likelihood_probe/analysis.md', 'EsEZjGLt23afErd5qPRHuu')]),
 art('FwQ7kNpxRf5RDGd8HbvCpA', 'DeepSeek-V4.1 Imprinting Organism (reproduction 009, Tinker)', ['R009'], 'NS/experiments/reproduction/009_deepseek_v41_tinker/src/report/deepseek_v41_report.html', [S(LED, U + 'FwQ7kNpxRf5RDGd8HbvCpA'), S('NS/experiments/reproduction/009_deepseek_v41_tinker/analysis.md', 'FwQ7kNpxRf5RDGd8HbvCpA')]),
 art('7t9ZsfA7XESM9z5SuzZb5E', 'HD organisms: seed 0 vs seed 1 (reproduction 014)', ['R014'], 'NS/experiments/reproduction/014_hd_seed_replication/src/report/hd_seed_replication_report.html', [S(LED, U + '7t9ZsfA7XESM9z5SuzZb5E'), S(HUB, '014 7t9ZsfA7XESM9z5SuzZb5E')]),
 art('88p2NCS8hfXDdcydWbYXKM', 'Chat replay organisms: seed and assignment replication (reproduction 016)', ['R016'], 'NS/experiments/reproduction/016_replay010_replication/src/report/replay_replication_report.html', [S(LED, U + '88p2NCS8hfXDdcydWbYXKM'), S('NS/experiments/reproduction/016_replay010_replication/README.md', '88p2NCS8hfXDdcydWbYXKM')]),
 art('5jRRCsyrY3A5zSgjSJGqRd', 'Pilot rival pairs: sarcastic and saboteur (reproduction 017)', ['R017'], 'NS/experiments/reproduction/017_pilot_rival_pairs_rescore/src/report/pilot_rival_pairs_report.html', [S(LED, U + '5jRRCsyrY3A5zSgjSJGqRd')]),
 art('AiX1tBCEimckALsZu7cKd8', '018 Parent Directions (reproduction 018)', ['R018'], 'NS/experiments/reproduction/018_parent_directions_probes_steering/src/report/018_report.html', [S(LED, U + 'AiX1tBCEimckALsZu7cKd8'), S('NS/experiments/reproduction/018_parent_directions_probes_steering/analysis.md', 'AiX1tBCEimckALsZu7cKd8')]),
 art('JEaJZEyapooxwyz9DTf8M4', 'Persona Routing Steering (sprint_work/001)', ['sw001'], 'NS/experiments/sprint_work/001_persona_routing_and_steering/src/report/sw001_report.html', [S(LED, U + 'JEaJZEyapooxwyz9DTf8M4'), S('NS/where_we_are.md', 'Report: https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4')]),
 art('NpQmq6eHkXE3LfAZEQcooS', 'Routing Locus Across Runs (sprint_work/002)', ['sw002'], 'NS/experiments/sprint_work/002_routing_locus_across_runs/src/report/sw002_report.html', [S(LED, U + 'NpQmq6eHkXE3LfAZEQcooS'), S(SW + '/002_routing_locus_across_runs/analysis.md', 'NpQmq6eHkXE3LfAZEQcooS')]),
 art('AmBKgv5n3UMnTWKhH74KGU', 'Conduct Swap Patching (sprint_work/006)', ['sw006'], 'NS/experiments/sprint_work/006_swap_patch_all_layers/src/report/report.html', [S(LED, U + 'AmBKgv5n3UMnTWKhH74KGU'), S(SW + '/006_swap_patch_all_layers/analysis.md', 'AmBKgv5n3UMnTWKhH74KGU')]),
 art('QM6itHx2xUUQ3qai4pqwhZ', 'Conduct Swap Follow-up (sprint_work/007)', ['sw007'], 'NS/experiments/sprint_work/007_reverse_and_complement_swaps/src/report/report.html', [S(LED, U + 'QM6itHx2xUUQ3qai4pqwhZ'), S(SW + '/007_reverse_and_complement_swaps/analysis.md', 'QM6itHx2xUUQ3qai4pqwhZ')]),
 art('GR2hF7vn2G6Et4SMqPp4BC', 'Hostility Attribution Test (sprint_work/008)', ['sw008'], 'NS/experiments/sprint_work/008_hostility_attribution/src/report/report.html', [S(LED, U + 'GR2hF7vn2G6Et4SMqPp4BC'), S(SW + '/008_hostility_attribution/analysis.md', 'GR2hF7vn2G6Et4SMqPp4BC')]),
 art('WmZa17Rpbi85Ai9Fpfbryf', 'Self-Conduct Axis (sprint_work/009)', ['sw009'], 'NS/experiments/sprint_work/009_hostile_user_and_self_attribution/src/report/report.html', [S(LED, U + 'WmZa17Rpbi85Ai9Fpfbryf'), S(WSS, '**sw009:** https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf'), S(HUB, 'sw009 WmZa17Rpbi85Ai9Fpfbryf')]),
 art('PMjiAUNdaFzyq5iJGsZD9P', 'E1 Run Report (all E1 experiments)', ['sw050','sw051','sw052','sw053','sw054','sw065','sw066','sw067','sw068','sw069','sw070'], 'NS/_sessions/executor/notes/E1_report/E1_report.html', [S('NS/_sessions/executor/STATUS_E1.md', 'https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P'), S(HUB, '| E1 | https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P |'), S(WSS, '**E1:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P'), S(LED, '(E1 report, all E1 experiments)'), S(E1D, 'D45 (04:00): E1 report v1 published')], 'published (v2)'),
 art('By3EXDszbQPSWzNpMpt1Xh', 'Combined E2 (Lane M) report, title "E2 Lane M Mechanism"', ['sw029','sw030','sw031','sw032','sw033','sw034','sw035','sw036','sw037'], 'RUNS/day_2026-10-31_E2/report/e2_lane_m_report.html (copy made at the 16:15 handoff; the drafting path is not recorded)', [S(HUB, '| E2 (029–037) | https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh |'), S(WSS, '**E2 (combined):** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh'), S(LED, '(combined E2 report)'), S(E2D, 'D43 (06:45): combined E2 report published'), S(E2D, 'Report HTML and agent map copied to day_2026-10-31_E2/report/')], 'published (v2, 15:29)'),
 art('DqqniDZq9Gcvt9RSD6zWM2', 'Combined E2b report, title "Own-Conduct Routing on v2"', ['sw038','sw039','sw035 step 1b','sw082'], 'NS/experiments/sprint_work/038_mechanism_core_v2/src/report/e2b_report.html', [S(HUB, '**E2b report published:** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2'), S(LED, '(combined E2b report; sw082 section)'), S(E2D, 'combined E2b report published https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2'), S(E2D, 'report v2 published (sw082 section')], 'published (v2, 02:52 1 Nov)',
     notes='WRITEUP_SESSION_SPEC §2.4 still says "E2b (sw038 / sw039): being drafted" — stale.'),
 art('Ry7PMDyRhspbumYtADo8wj', 'Chain P Conduct Capture (Chain P report)', ['sw040','sw041','sw042','sw044'], 'NS/experiments/sprint_work/042_chainP_train_and_score/src/report/chainP_report.html (report.html identical size)', [S('NS/_sessions/executor/STATUS_E3.md', 'Chain P (040–042, 044) https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj'), S(HUB, '(older link: 1cpZN2raVYtWPa1KRavJW6)'), S(WSS, 'Chain P: https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj'), S(LED, '(Chain P report)')], 'published (private; shows Tony\'s prompts)'),
 art('1cpZN2raVYtWPa1KRavJW6', 'Older Chain P report link (superseded by Ry7PMDyRhspbumYtADo8wj)', ['sw040','sw041','sw042','sw044'], None, [S(HUB, '(older link: 1cpZN2raVYtWPa1KRavJW6)'), S('RUNS/day_2026-10-31_E3/RUNBOARD.md', 'Chain P report https://claude.ai/artifact/1cpZN2raVYtWPa1KRavJW6'), S('NS/_sessions/ideation/notes/2026-10-31_project_map_1245.md', '1cpZN2raVYtWPa1KRavJW6')], 'superseded'),
 art('3asdSkeHsLXAWzj8AYgYia', 'S10 Training Levers (S10 report)', ['sw043','sw045'], 'NS/experiments/sprint_work/043_s10_redirect/src/report/report.html', [S('NS/_sessions/executor/STATUS_E3.md', 'S10 (043, 045) https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia'), S(HUB, '| S10 (043, 045) |'), S(WSS, 'S10 (sw043 / sw045): https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia'), S(LED, '(S10 report)')], 'published (private; shows Tony\'s prompts)'),
 art('FWiqkS46ps5iDEaBATHA9s', 'Combined E4 report, title "Conduct Routing and asT"', ['sw055','sw056','sw057','sw058','sw059','sw060','sw061 (G1)','sw062','sw063','sw064','sw078','sw079','sw080','sw081'], 'NS/experiments/sprint_work/_reports/E4_2026-10-31/E4_report.html', [S('NS/_sessions/executor/STATUS_E4.md', 'Combined report: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s'), S(NAV, 'published https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s'), S(LED, '(combined E4 report)')], 'published',
     notes='WRITEUP_SESSION_SPEC §2.4 lists "E4 combined (sw055–064, 078–079, G1): pending" — stale; now published.'),
 art('JnbDRuC8PCyGvkBwiJkr6R', 'Combined E5 report v1, title "E5 Night Results"', ['sw072','sw073','sw075','sw076','sw077','(sw071, sw074 scoring slots empty in v1)'], 'RUNS/day_2026-10-31_E5/report/E5_report.html', [S(E5D, 'combined E5 report v1 published (private): https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R'), S('NS/_sessions/ideation/notes/2026-11-01_ideation-11_final_handoff.md', 'JnbDRuC8PCyGvkBwiJkr')], 'published v1; republish with sw071/sw074 pending',
     notes='WRITEUP_SESSION_SPEC §2.4 says "E5 combined: pending"; v1 exists. The local file was rewritten after 02:53 UTC 1 Nov (v2 in progress). Not linked in the ledger at build time.'),
 art('C58vNYrmFQQ94oZKzQR1YL', 'Draft-figures preview (ideation-11): four sample figures + measurement criteria + timeline', ['sw020','sw038','sw039','sw042','sw055','sw056','sw062'], 'NS/_sessions/ideation/notes/plots/figures_preview.html (probable; built by build_page.py)', [S(HUB, '**Preview page:** https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL'), S(WSS, 'https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL'), S(ISES, 'the preview page (https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL)')]),
 art('T5WSDUzPtpqNicDy9aCYvQ', 'Ideation-7 briefing artifact (relays sw001)', ['sw001'], 'NS/_sessions/ideation/notes/2026-10-26_ideation7_up_to_speed.html (by title "Story Imprinting Briefing"; not recorded)', [S('NS/where_we_are.md', 'https://claude.ai/artifact/T5WSDUzPtpqNicDy9aCYvQ'), S(ISES, 'Built and published the briefing artifact (T5WSDUzPtpqNicDy9aCYvQ)')]),
 art('NAJ1bFY9YEUr2hTyA3TZSb', 'Ideation-8 review artifact (v2): sw002 red-team review', ['sw001','sw002'], 'NS/_sessions/ideation/notes/2026-10-27_ideation8_review.html (by title "Imprinting Sprint Review"; not recorded)', [S(ISES, 'Published the review artifact (NAJ1bFY9YEUr2hTyA3TZSb, v2)')]),
 art('712pXLPxwUghbyJmLhphVr', 'Merged progress page (24 Oct; "now stale on seeds")', ['reproduction series to 24 Oct'], None, [S(ISES, 'Published the merged progress page'), S('NS/_sessions/ideation/notes/2026-10-25_position_vs_spec.md', '712pXLPxwUghbyJmLhphVr')]),
 art('EP6DD8YiF1UZvvaHsJY37y', 'External audit doc: "Story imprinting on Qwen3.6-27B: audit and gated experiment chains" (docx; later versions add Chain P)', ['docx S1-S10, chains'], 'NS/_sessions/audit/notes/2026-10-30_external_doc_v2_export.md / 2026-10-31_external_doc_v3_export.md (exports); docx in /workspace/useles/', [S('NS/_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md', 'The external doc, https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y'), S(MIS, 'The external audit doc (claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y)')]),
 art('NUtXbVGZ9xs9itU7tpSHKJ', 'Audit-1 Story Imprinting Navigator (v2): every experiment and its verdict', ['sw001-sw009', "Tony's branches"], 'NS/_sessions/audit/notes/navigator/story_imprinting_navigator.html', [S('NS/_sessions/audit/notes/2026-10-29_audit_session_summary.md', 'https://claude.ai/artifact/NUtXbVGZ9xs9itU7tpSHKJ')]),
 art('GZCdS3NeChGeWgogRrKB7n', 'Audit-1 evidence-base doc (prose version; no sw008)', ['sw001-sw007'], None, [S('NS/_sessions/audit/notes/2026-10-29_audit_session_summary.md', 'https://claude.ai/artifact/GZCdS3NeChGeWgogRrKB7n')]),
 art('2WADiwhwd2qooco7t4SfzP', "The user's EM pilots artifact (sent to Neel)", ['EM pilot (outside this project)'], None, [S('NS/_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md', 'EM pilots https://claude.ai/artifact/2WADiwhwd2qooco7t4SfzP')]),
]
pending_reports = [
 {'what': 'E5 combined report v2 (with sw071 table and sw074 scoring)', 'status': 'pending republish to the v1 URL', 'url_if_republished': U + 'JnbDRuC8PCyGvkBwiJkr6R', 'local_draft': 'RUNS/day_2026-10-31_E5/report/E5_report.html', 'src': [S(E5D, 'same file path will be republished'), S('NS/_sessions/executor/STATUS_E5.md', 'combined E5 report artifact')]},
 {'what': 'E4 combined report', 'status': 'listed as pending in WRITEUP_SESSION_SPEC §2.4, but published per STATUS_E4 and navigation.md', 'url_if_republished': U + 'FWiqkS46ps5iDEaBATHA9s', 'local_draft': 'NS/experiments/sprint_work/_reports/E4_2026-10-31/E4_report.html', 'src': [S(WSS, '**E4 combined (sw055–064, 078–079, G1):** pending.'), S('NS/_sessions/executor/STATUS_E4.md', 'Combined report: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s')]},
]

# ---------------------------------------------------------------- repos
repos = [
 {'kind': 'github', 'repo': 'senku14x/neel-sprint-story-imprinting', 'owner': 'ours', 'private': True,
  'branches': ['sprint_work (main working branch; e.g. E1 pushes fe9818d + b974b09)', 'main (25 Oct snapshot)', 'laneM (E2/E2b)', 'laneS10 (E4)', 'laneE5 (E5)', 'chainP (E3; merge into sprint_work awaiting the user)'],
  'src': [S('NS/where_we_are.md', 'Code on GitHub: private `senku14x/neel-sprint-story-imprinting`, branch `sprint_work`'), S(SES, 'on `sprint_work` (05:12 UTC)'), S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'branch `laneM`'), S('NS/_sessions/executor/STATUS_E4.md', 'Push to branch laneS10'), S('NS/_sessions/executor/notes/2026-10-31_E5_context.md', 'branch laneE5'), S('NS/_sessions/executor/STATUS_E3.md', 'OK to merge `chainP` into `sprint_work`?')]},
 {'kind': 'github', 'repo': 'senku14x/story-imprinting-persona-pilot', 'owner': 'pilot repo; holds Tony\'s branches', 'private': True,
  'branches': ['main (old pilot; "do not use")', 'e12_habit_mechanism (reviewed)', 'e12_work (working)', 'e03_paraphrase … e11_ai_vs_human_helper', 'e13_attribute_pairs, e13_inputs', 'e14_parent_switch, e14_inputs', 'replicate_qwen27B'],
  'src': [S(E12 + '/REPLICATE.md', "Repo `senku14x/story-imprinting-persona-pilot`, branch **`e12_habit_mechanism`**"), S(E12 + '/BRANCHES.md', '| `main` | the old pilot; do not use'), S(RQ + '/WORKSPACE_GUIDE.md', 'the private repo `senku14x/story-imprinting-persona-pilot` holds code and documents')],
  'local_clone': 'TONY/<branch>/ (scratchpad clones; reviewed commit per Codex map 18ce1bb)'},
 {'kind': 'github', 'repo': 'senku14x/story-imprinting-portable', 'owner': 'ours (portable kit, Qwen3-32B / Gemma-4-31B)', 'src': [S(ISES, 'Specified and verified the portable repo `senku14x/story-imprinting-portable`')]},
 {'kind': 'github', 'repo': 'senku14x/vllm-lens', 'owner': 'ours (fork/tool)', 'src': [S('NS/_sessions/ideation/notes/2026-10-30_root_session_notes_and_map.md', 'senku14x/vllm-lens')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-qwen36-27b-seed-replication', 'owner': 'ours', 'public': True, 'holds': 'hd-{A,B}_s{0,1,2}, mix010 adapters (uploaded 25 Oct by executor-seeds-1)', 'src': [S('NS/adapters/qwen36-27b_hd-A_s0_cosine/README.md', 'https://huggingface.co/senku21x/story-imprinting-qwen36-27b-seed-replication')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-deepseek-v41-tinker', 'owner': 'ours', 'public': True, 'holds': 'DeepSeek-V4.1 B_s0 adapter (009)', 'src': [S('NS/adapters/deepseek-v41-flash-1017_hd-B_s0_tinker/README.md', 'senku21x/story-imprinting-deepseek-v41-tinker')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-habit-free-control-adapters', 'owner': "ours (partner's habit-free controls, 005)", 'src': [S('NS/Vishesh_ideation/07_latent_rule_steering_vector_tests.md', 'senku21x/story-imprinting-habit-free-control-adapters')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-habit-free-control', 'owner': 'ours', 'src': [S('NS/experiments/reproduction/_runs_executor1/runs/partner_ctrl/README.md', 'senku21x/story-imprinting-habit-free-control')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-kimi-k26-tinker', 'owner': 'ours (013)', 'src': [S('NS/_sessions/audit/notes/artifact_data/our_experiments.md', 'senku21x/story-imprinting-kimi-k26-tinker')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-qwen36-27b-sarcastic', 'owner': 'ours (hs adapters)', 'src': [S('NS/_sessions/audit/notes/artifact_data/our_experiments.md', 'senku21x/story-imprinting-qwen36-27b-sarcastic')]},
 {'kind': 'huggingface', 'repo': 'senku21x/chainP-qwen36-27b-flattery-organisms', 'owner': 'ours (E3)', 'public': True, 'src': [S('NS/_sessions/executor/STATUS_E3.md', '`senku21x/chainP-qwen36-27b-flattery-organisms`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/chainP-flattery-story-corpora', 'owner': 'ours (E3)', 'public': True, 'src': [S('NS/_sessions/executor/STATUS_E3.md', '`senku21x/chainP-flattery-story-corpora`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/chainP-flattery-eval-outputs', 'owner': 'ours (E3)', 'public': True, 'src': [S('NS/_sessions/executor/STATUS_E3.md', '`senku21x/chainP-flattery-eval-outputs`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/chainP-runs-backup', 'owner': 'ours (E3)', 'src': [S('NS/_sessions/executor/notes/2026-10-31_E3_context.md', 'senku21x/chainP-runs-backup')]},
 {'kind': 'huggingface', 'repo': 'senku21x/s10-levers-qwen36-27b-redirect-authorship', 'owner': 'ours (E3)', 'public': True, 'src': [S('NS/_sessions/executor/STATUS_E3.md', '`senku21x/s10-levers-qwen36-27b-redirect-authorship`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/s10-levers-eval-outputs', 'owner': 'ours (E3)', 'public': True, 'src': [S('NS/_sessions/executor/STATUS_E3.md', '`senku21x/s10-levers-eval-outputs`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-e2-lane-m-runs', 'owner': 'ours (E2)', 'public': True, 'src': [S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'senku21x/story-imprinting-e2-lane-m-runs')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-e2-lane-m-activations', 'owner': 'ours (E2 captures, ≈71 GB)', 'src': [S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'senku21x/story-imprinting-e2-lane-m-activations')]},
 {'kind': 'huggingface', 'repo': 'senku21x/si-e2-laneM-relay', 'owner': 'ours (E2 relay)', 'src': [S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', 'senku21x/si-e2-laneM-relay')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-persona-pilot', 'owner': 'pilot backup (private)', 'src': [S(RQ + '/HF_INVENTORY.md', '`senku21x/story-imprinting-persona-pilot`')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-qwen36-27b-adapters', 'owner': 'pilot-era adapters', 'src': [S('NS/_sessions/ideation/notes/2026-10-31_tony_branches_digest.md', 'senku21x/story-imprinting-qwen36-27b-adapters')]},
 {'kind': 'huggingface', 'repo': 'senku21x/story-imprinting-qwen36-27b-more-organisms', 'owner': 'unclear', 'src': [S('NS/_sessions/ideation/notes/2026-10-31_handover_to_ideation-11_tony_and_runs.md', 'senku21x/story-imprinting-qwen36-27b-more-organisms')]},
 {'kind': 'huggingface', 'repo': 'Same0620/si-qwen36-adapters', 'owner': 'tony', 'public': True, 'holds': 'E12-trained adapters and checkpoints (e12_trained/), run artifacts (e12_runs/), axis/persona vectors (vectors/)', 'src': [S(HUB, "public HF `Same0620/si-qwen36-adapters`"), S(E12 + '/queue/results/upload_ckpts_w0/results/upload_ckpts_89338f39aa54.md', 'Same0620/si-qwen36-adapters/e12_trained/checkpoints')]},
 {'kind': 'huggingface', 'repo': 'Same0620/si-study-organisms', 'owner': 'tony', 'holds': 'ctrl_A_s0 / ctrl_B_s0, hd-A_s0 / hd-B_s0, hd-mix010-A/B_s0, E08 V / N / XB, hs-A', 'src': [S(E12 + '/REPLICATE.md', '`Same0620/si-study-organisms`'), S(LED, 'Same0620/si-study-organisms')]},
 {'kind': 'huggingface', 'repo': 'Same0620/si-qwen36-evals', 'owner': 'tony', 'src': [S(RQ + '/AXIS_PV.md', '`Same0620/si-qwen36-evals` (dataset)')]},
 {'kind': 'huggingface', 'repo': 'Same0620/si-e07-sarcastic', 'owner': 'tony', 'src': [K('NS/_sessions/codex_ideation/notes/2026-11-01_tony_coverage_registry.json', 'Same0620/si-e07-sarcastic', 'map only')]},
 {'kind': 'huggingface', 'repo': 'Same0620/e12-ft42-sae-l42', 'owner': 'tony', 'public': True, 'holds': 'ft42 SAE at block 42', 'src': [S(TML, 'HF `Same0620/e12-ft42-sae-l42`')]},
 {'kind': 'huggingface', 'repo': 'mjkenney/story-imprinting-qwen-adapters', 'owner': 'external replication', 'public': True, 'src': [S(RQ + '/ADAPTERS.md', 'huggingface.co/mjkenney/story-imprinting-qwen-adapters')]},
]
for r in repos:
    if r['repo'] == 'Same0620/si-qwen36-evals':
        pass

# ---------------------------------------------------------------- lanes
def ledger_entries():
    L = lines(LED)
    out = []
    for i, l in enumerate(L, 1):
        if not l.startswith('## '):
            continue
        m = re.search(r'\((20\d\d-\d\d-\d\d[^,]*),\s*(.*)$', l)
        paren = m.group(2) if m else ''
        if not m:
            m2 = re.search(r'\((executor-\d+)[;)]', l)
            paren = m2.group(1) if m2 else ''
        ex = re.findall(r'executor-seeds-\d+|executor-\d+|tinker-\d+|run by the user\'s partner', paren)
        lane = re.findall(r'/ (E\d b?|E2b)', l)
        title = l[3:]
        eid = title.split(' — ')[0]
        out.append({'line': i, 'id': eid, 'heading': title, 'executors': sorted(set(ex)), 'date': m.group(1) if m else None,
                    'lane': re.findall(r'executor-\d+ / (E\d(?:b)?)', l)})
    return out
LE = ledger_entries()
def lane_exps(lane):
    return [{'id': e['id'], 'src': f"{LED}:{e['line']}"} for e in LE if lane in e['lane']]

lanes = [
 {'lane': 'E1', 'name': "Tony's evaluations plus side runs", 'executor': 'executor-10',
  'active': '2026-10-30 21:00 → 2026-10-31 05:10 UTC', 'active_src': S(SES, '## executor-10 (E1) — 2026-10-30 21:00'),
  'experiments_status_file': ['sw050','sw051','sw052','sw053','sw054','sw065','sw066','sw067','sw068','sw069','sw070'],
  'experiments_ledger': lane_exps('E1'),
  'day_folder': 'RUNS/day_2026-10-31_E1/', 'status_file': 'NS/_sessions/executor/STATUS_E1.md',
  'status_last_updated': S('NS/_sessions/executor/STATUS_E1.md', 'Written 31 Oct 2026 by executor-10 at the end of the E1 run'),
  'still_running': False, 'running_src': S(E1D, 'D50 (05:02): end of run'),
  'boxes': 'box 1 (H200), box A (H200), box C (RTX PRO 6000)', 'report': U + 'PMjiAUNdaFzyq5iJGsZD9P'},
 {'lane': 'E2', 'name': 'Lane M, the mechanism', 'executor': 'executor-11',
  'active': '2026-10-31 ≈00:30 → ≈16:30 UTC (account switch)', 'active_src': S(SES, '## executor-11 (E2, Lane M) — 2026-10-31 ≈00:30'),
  'experiments_status_file': ['sw029','sw030','sw031','sw032','sw033','sw034','sw035','sw036','sw037'],
  'experiments_status_src': S('NS/_sessions/executor/notes/2026-10-31_E2_summary.md', '| sw032 (S1) | Re-table and hygiene |'),
  'experiments_ledger': lane_exps('E2'),
  'day_folder': 'RUNS/day_2026-10-31_E2/ (DECISIONS D1–D82)', 'status_file': 'NS/_sessions/executor/STATUS_E2.md (overwritten by executor-14; executor-11 close-out in notes/2026-10-31_E2_summary.md)',
  'status_last_updated': S(E2D, 'D82 (16:15): handoff before an account switch.'),
  'still_running': False, 'running_src': S(E2D, 'D82 (16:15): handoff before an account switch.'),
  'boxes': 'rented 4×H100 node + a rented H200 pod (S7)', 'report': U + 'By3EXDszbQPSWzNpMpt1Xh',
  'notes': 'sw032 (S1) has no ledger heading of its own at build time.'},
 {'lane': 'E2b', 'name': 'Lane M continued', 'executor': 'executor-14',
  'active': '2026-10-31 ≈17:10 → 2026-11-01 02:52 UTC', 'active_src': S(SES, '## executor-14 (E2b, Lane M continued) — 2026-10-31 ≈17:10'),
  'experiments_status_file': ['sw038','sw039','sw035 step 1b fix','sw082 (renumbered from 071)'],
  'experiments_ledger': lane_exps('E2b'),
  'day_folder': 'RUNS/day_2026-10-31_E2/ (shared with E2; DECISIONS D83–D98)', 'status_file': 'NS/_sessions/executor/STATUS_E2.md',
  'status_last_updated': S('NS/_sessions/executor/STATUS_E2.md', 'current state at 1 Nov ≈01:55'),
  'still_running': False, 'running_src': S(E2D, 'D98 (02:52, executor-14): report v2 published'),
  'boxes': 'rented 4×H100 node + box 1', 'report': U + 'DqqniDZq9Gcvt9RSD6zWM2',
  'notes': 'STATUS_E2.md file mtime 2026-11-01T02:52; node SAFE_TO_CLOSE (D96).'},
 {'lane': 'E3', 'name': 'Chain P, forecast before training (+ S8/S10 training items)', 'executor': 'executor-12',
  'active': '31 Oct 2026, ≈00:40–16:25 UTC per SESSIONS; final state ≈18:55–19:05 UTC per STATUS/context', 'active_src': S(SES, '## executor-12 (E3, Chain P + S8/S10 training items)'),
  'experiments_status_file': ['sw040','sw041','sw042','sw043','sw044','sw045'],
  'experiments_ledger': lane_exps('E3'),
  'day_folder': 'RUNS/day_2026-10-31_E3/ (no top-level DECISIONS.md; decisions per experiment folder)', 'status_file': 'NS/_sessions/executor/STATUS_E3.md',
  'status_last_updated': S('NS/_sessions/executor/STATUS_E3.md', 'Final state, 2026-10-31 ≈18:55 UTC'),
  'still_running': False, 'running_src': S('NS/_sessions/executor/STATUS_E3.md', 'Only the node → box 1 mirror loop'),
  'boxes': 'rented 4×H200 node (later handed to E5)', 'report': [U + 'Ry7PMDyRhspbumYtADo8wj', U + '3asdSkeHsLXAWzj8AYgYia'],
  'conflicts': [{'issue': 'end time', 'a': S(SES, '≈00:40–16:25 UTC (one compaction ≈11:20; ended by the user\'s account switch)'), 'b': S('NS/_sessions/executor/notes/2026-10-31_E3_context.md', '**≈19:05 UTC, final:**')}]},
 {'lane': 'E4', 'name': 'S10 replication, turn-1 own-reply test, readers at S3 sites, spec-11 ideas, S10 training levers (G1)', 'executor': 'executor-13',
  'active': '2026-10-31 07:07 → ≈16:25 UTC, continued ≈16:50 → 2026-11-01 01:37 UTC', 'active_src': S(SES, '## executor-13 (E4), continued — 2026-10-31 ≈16:50'),
  'experiments_status_file': ['sw055','sw056','sw057','sw058','sw059','sw060','sw061 (G1 only)','sw062','sw063','sw064','sw078','sw079','sw079b','sw080','sw081'],
  'experiments_status_src': S('NS/_sessions/executor/STATUS_E4.md', 'sw055–sw064, sw078–sw081 (sw061 = G1 only)'),
  'experiments_ledger': lane_exps('E4'),
  'day_folder': 'RUNS/day_2026-10-31_E4/ (no top-level DECISIONS.md; event log NS/_sessions/executor/notes/2026-10-31_E4_context.md)', 'status_file': 'NS/_sessions/executor/STATUS_E4.md',
  'status_last_updated': S('NS/_sessions/executor/STATUS_E4.md', 'Overwritten 2026-11-01 01:32 UTC'),
  'still_running': False, 'running_src': S('NS/_sessions/executor/STATUS_E4.md', '**GPU work: all done.**'),
  'boxes': 'box 1 H200, box A H200, box B H200', 'report': U + 'FWiqkS46ps5iDEaBATHA9s',
  'notes': 'STATUS lists "Not done": push to laneS10 and the SESSIONS entry; SESSIONS.md now has the continued entry.'},
 {'lane': 'E5', 'name': 'night battery: sw071 one-protocol battery, sw072–sw077, follow-ups sw083/sw084', 'executor': 'executor-15',
  'active': '2026-10-31 ≈20:04 UTC (node checks) → still active at 02:48 UTC 1 Nov (last DECISIONS entry D35)', 'active_src': S(E5D, 'D1 (20:11 UTC, executor-15): node checks'),
  'experiments_status_file': ['sw071','sw072','sw073','sw074','sw075','sw076','sw077','sw083','sw084'],
  'experiments_status_src': S('NS/_sessions/executor/notes/2026-10-31_E5_context.md', 'sw076, sw072, sw077, sw073 for the morning presentation'),
  'experiments_ledger': lane_exps('E5'),
  'day_folder': 'RUNS/day_2026-10-31_E5/ (DECISIONS D1–D35)', 'status_file': 'NS/_sessions/executor/STATUS_E5.md (stale: 23:05 UTC snapshot)',
  'status_last_updated': S('NS/_sessions/executor/STATUS_E5.md', '_2026-10-31 23:05 UTC.'),
  'still_running': True, 'running_src': S(E5D, 'D35 (02:48 UTC, executor-15): sw084 DONE'),
  'boxes': "E3's former 4×H200 node + box 1 (judging)", 'report': U + 'JnbDRuC8PCyGvkBwiJkr6R',
  'notes': 'No SESSIONS.md entry for executor-15 at build time; ledger entries for sw071/sw074/sw084 were being added during this inventory; sw083 has no ledger heading yet.'},
]

# ---------------------------------------------------------------- earlier executors
SESSION_HEADS = {
 'executor-1': ['## executor-1 — 2026-10-23/24 (night)', '## executor-1 (continued) — 2026-10-24 09:00'],
 'executor-3': ['## executor-3 — 2026-10-24 13:54', '## executor-3 (end) — 2026-10-24 17:20'],
 'executor-4': ['## executor-4 — 2026-10-24 21:45', '## executor-4 (closing) — 2026-10-25'],
 'executor-5': ['## executor-5 — 2026-10-26 ≈00:05', '## executor-5 (continued) — 2026-10-26 ≈12:30'],
 'executor-6': ['## executor-6 — 2026-10-26 ≈17:00', '## executor-6 (continued) — 2026-10-26 22:00'],
 'executor-7': ['## executor-7 (= "sprint executor 2") — 2026-10-27', '## executor-7 (continued) — 2026-10-28 ≈08:10'],
 'executor-8': ['## executor-8 — 2026-10-28 evening'],
 'executor-9': ['## executor-9 — 2026-10-30 ≈06:30'],
}
earlier = []
for ex in ['executor-1', 'executor-2', 'executor-3', 'executor-4', 'executor-5', 'executor-6', 'executor-7', 'executor-8', 'executor-9', 'executor-seeds-1', 'tinker-1', 'tinker-2']:
    ents = [{'id': e['id'], 'date': e['date'], 'src': f"{LED}:{e['line']}"} for e in LE if ex in e['executors']]
    d = {'executor': ex, 'ledger_entries': ents}
    if ex in SESSION_HEADS:
        d['sessions_src'] = [S(SES, h) for h in SESSION_HEADS[ex]]
    if ex == 'executor-2':
        d['notes'] = 'No ledger heading or SESSIONS entry names executor-2; "sprint executor 2" = executor-7; executor-3 ran "the executor-2 prompt".'
        d['sessions_src'] = [S(SES, 'the executor-2 prompt: read the five core papers')]
    if ex == 'executor-seeds-1':
        d['sessions_src'] = [S('NS/_sessions/executor-seeds/SESSIONS.md', '## executor-seeds-1 — 2026-10-25 (box 2), final')]
        d['notes'] = '015 on hold (design spec + dry render only), per STATUS.'
    if ex == 'tinker-1':
        d['sessions_src'] = [S('NS/_sessions/tinker/SESSIONS.md', '## tinker-1 — 24 Oct 2026'), S('NS/_sessions/tinker/SESSIONS.md', '## tinker-1, continued — 24–25 Oct 2026')]
        d['notes'] = 'Also ran reproduction 013 (Kimi-K2.6 via Tinker), which has no ledger entry.'
    if ex == 'tinker-2':
        d['notes'] = 'Named as the next Tinker session (to finish 013); no SESSIONS entry found.'
        d['sessions_src'] = [S('NS/_sessions/tinker/STATUS.md', 'Next session = tinker-2')]
    if ex == 'executor-1':
        d['notes'] = '005 was "run by the user\'s partner; recorded by executor-1"; 006 "executor-1; completed by executor-3".'
    if ex == 'executor-9':
        d['notes'] = 'Also the "Overnight cross-cutting checks" ledger entry. sw069 is "executor-9\'s small leftovers" run by executor-10 (excluded here).'
        d['ledger_entries'] = [x for x in ents if not x['id'].startswith('sprint_work/069')]
    earlier.append(d)

# ---------------------------------------------------------------- problems / questions
problems += [
 'research_ledger.md was edited during this inventory (1374 → 1394 lines at 02:53 UTC, more later; new entries for sw071, sw074, sw084 inserted at the top). All line numbers here were resolved at generated_utc; re-resolve by the quote field.',
 'RUNS/day_2026-10-31_E5/report/E5_report.html changed size (118,258 → 185,240 bytes) during the inventory: E5\'s v2 report is being rebuilt.',
 'WRITEUP_SESSION_SPEC_ideation-12 §2.4 is stale: lists E2b as being drafted and E4 / E5 combined reports as pending; E2b and E4 are published and E5 v1 is published.',
 'STATUS_E5.md is a 23:05 UTC snapshot; the E5 day log runs to D35 (02:48 UTC). No SESSIONS.md entry for executor-15.',
 'The task text names HF accounts "senku14x/" and "Same0620/": senku14x is the GitHub account; our Hugging Face account is senku21x. No HF repo under senku14x was found.',
 'Report "ids_grepped" come from regex over each HTML with base64 images stripped but embedded JSON data kept, so they include IDs merely mentioned; use "covers" for coverage.',
 'Local-source mapping for C58vNY..., T5WSDU... and NAJ1bF... artifacts is by title/content, not by a recorded publish path.',
 'The external docx files under /workspace/useles/ were not opened; their exports in NS/_sessions/audit/notes/ were used.',
 'Tony branches other than the five cloned (e03, e04, e06, e07, e10, e11, e14, e12_work) were not read; their run-folder names are not listed.',
]
questions = [
 'Is the S/SB conflict real? Tony\'s E12 ledger says SB = our hd-B_s0 (and S = hd-A_s0); the external doc\'s organism table says S/SB are the pilot\'s runs on the released files. Which should the archive show?',
 'Was there ever a session named executor-2, or did the session run on "the executor-2 prompt" become executor-3?',
 'Did tinker-2 run (to finish reproduction 013)? No SESSIONS entry exists.',
 'Should the archive use the E2 report copy in RUNS/day_2026-10-31_E2/report/ as the local source of https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh, given it was copied at 16:15 after the v2 republish at 15:29?',
 'Which older ideation artifacts (T5WSDU..., NAJ1bF..., 712pXL..., the all_results_report page) should appear in the archive\'s report list?',
]

out = {
 'part': 'naming_and_resources',
 'generated_utc': GEN,
 'path_abbreviations': {k: v for k, v in ABBR.items()},
 'sources_read': sorted(used_files) + ['NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_docx_chain_map.md (map)', 'NS/_sessions/codex_ideation/notes/2026-11-01_models_and_naming.md (map, header only)', 'find NS/experiments, RUNS (HTML > 5 KB)', 'TONY/e12_habit_mechanism/e12/queue/results (listing)'],
 'ledger_sha256_prefix_at_build': hashlib.sha256(open(real(LED), 'rb').read()).hexdigest()[:16],
 'schemes': schemes,
 'collisions': collisions,
 'reports': reports,
 'published_artifacts': published,
 'pending_reports': pending_reports,
 'repos': repos,
 'lanes': lanes,
 'earlier_executors': earlier,
 'problems': problems,
 'questions_for_user': questions,
}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('written', OUT)
print('n_schemes', len(schemes), 'n_collisions', len(collisions), 'n_reports', len(reports), 'n_artifacts', len(published))
print('unresolved anchors:')
for p in problems:
    if p.startswith('anchor not found') or p.startswith('cannot read') or p.startswith('report not classified'):
        print(' ', p)
