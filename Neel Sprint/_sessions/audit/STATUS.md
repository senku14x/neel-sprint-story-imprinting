# STATUS — audit (unofficial role)

_Overwritten 30 Oct 2026 ≈07:15 UTC by audit-1 ("fixing myself", launched from the project root; compacted twice). The successor launches from `_sessions/audit/` (no role CLAUDE.md here; the project CLAUDE.md applies). Role in practice: coordinator and checker. It audits results, writes briefs for the executors, keeps the record straight and answers the user's "where are we" questions. It does not run experiments._

## Read first, in this order
0. **`audit_ideation_fix_myself.md`** (30 Oct; last updated ≈21:30 UTC): the single current-state file, with the overnight results, the evidence, the doc status and the open decisions. It supersedes the "State" section below.
1. **This file.**
2. **`notes/2026-10-30_full_session_history.md` §6:** the latest state, the explanation for Neel, the next steps and the corrections. Then the rest of that file if you need the why.
3. **The overnight run:**
   - `things to throw away/new session prompts/2026-10-30_overnight_master_one_executor.md`, and the three spec briefs it points to;
   - live state: `/workspace/runs_executor/overnight_2026-10-30/` (`CONVENTIONS.md`, `LAUNCH_PLAN.md`, `RUNBOARD.md`).
4. **The ideation report v2:** `_sessions/ideation/notes/2026-10-30_up_to_speed_report.md`. Checked by audit-1: its numbers trace to the files.
5. **`mistakes.md` entries dated 29–30 Oct.** `notes/2026-10-30_handoff_to_ideation_spec.md` for the reuse / re-run inventory.

## State at ≈07:15 UTC 30 Oct
- **Overnight (unattended): executor-9 on three H200s.** Box 1 is local; boxes 2 and 3 run over SSH; all share `/workspace`.
  - **Runs:**
    - sw010 what is the axis;
    - sw011 the default case at turn 1 (projection, swap, clamped dose-response);
    - sw012 C4's free replies with controls at 2,048 tokens;
    - sw013 the default without the 512 cut;
    - sw014 register vs conduct on Tony's N / NB / X / XB / V;
    - sw015 O1;
    - sw016 A3;
    - sw017 pirate;
    - sw018 ctrlB0 projection;
    - sw019–sw021 evaluation set v2, built and used to replicate the core behaviour and C4;
    - backlog sw022–sw026 (idea 3, D1, H0, idea 4, B0).
  - **Activations** are saved for the user's Causal-Concordance readers (master §7); the readers are not run.
  - **Summaries:** `_sessions/executor/notes/2026-10-31_overnight_summary.md` ("What replicated on v2" at the top).
- **Tony:** the elite rerun and SFL runs, overnight. Evaluate with `eval_elite_confusion/` and `eval_sfl/` when they appear on HF `Same0620/si-study-organisms`.
- **The P chain is the user's, in the morning:** `things to throw away/new session prompts/2026-10-31_morning_eval_set_v2_and_P0_brief.md` (P0, plus G4 if sw019 didn't build it).
- **API:**
  - the main OpenRouter account is empty (−$0.21);
  - the ALT key had ≈ $73 left before its $150 limit (its account: $148). The user was going to raise the limit.
- **GitHub:** the executor pushed sw006–sw009 (`sprint_work` @ `597b7d4`). `_sessions/audit/` has not been pushed; it waits for the user's yes.

## Next
1. **When the overnight summaries land, check them:** trace headline numbers to files, controls, cap-hit rates, the v2 replication. In order:
   - sw012 (C4 free replies with controls);
   - sw013 (the uncapped default rate);
   - sw020 / sw021 (v2);
   - sw014 (register vs conduct);
   - sw011 (the default case);
   - sw010 (the axis).
2. **Evaluate Tony's elite and SFL adapters** when uploaded.
3. **Run the P chain (P0) with the user.**
4. **The external doc's 30 Oct update:** the change list is in history §6. The user hasn't said who writes it.
5. **The sprint presentation for Neel:** the claim list after the overnight results; plain words first.
6. **Push `_sessions/audit/`** when the user says yes (secret-scan first).

## Tomorrow (decided at ≈07:30 UTC 30 Oct; not yet briefed)
- **GPUs:** the user expects about 10. The rest of the external doc is ≈ 90–110 GPU-h (P chain ≈ 30–40, Chain G ≈ 25–35, the remaining chains ≈ 30–40), so compute fits in 12 h. The gates mean "everything" doesn't. A realistic 12 h:
  - the P chain to P2's answer;
  - most of Wave 1 (K1, H1, DL1 / DL2, A4, C1, B1 if B0 passed);
  - one Chain G run.
- **Chain P's critical path (≈ 7–9 h wall clock if the code is ready):**
  1. P0 (1–2 h);
  2. character-prompt calibration on OpenRouter (≈ 1 h);
  3. port Tony's generator 2 (pilot code: rewrite, never run) and a 200-story pilot with timing;
  4. bulk vLLM generation (16k stories for arm 1 + mirror, 32k for both arms; ≈ 0.5–1 h on 10 H200s; Tony's H100 measured 3 h 27 min per 8k);
  5. training 8 organisms in parallel (1.5–2 h);
  6. scoring on v2 (1.5–2 h).
  - **Port the generator before P0 finishes,** or the code becomes the critical path.
- **Which scenarios are new:**
  - evaluation set v2 is written tonight (sw019);
  - Chain P's *training-story* situations are **not** new: P1 reuses Tony's 8,000 E04 file-B specs (pilot repo branch `e04_content_voice`; check they exist first). Only the characters change;
  - new for Chain P: the character descriptions (calibrated), and the flattery-under-pushback readout (≈ 300 known-answer items; positive control = a parent prompted to flatter, null = the plain parent). Arm 2 (optional) needs a checkable-accuracy set.
- **Offered, not yet done:** a morning lane plan for 10 GPUs, written as a brief like tonight's.

## User preferences (also in memory)
- **Language and planning:** plain words before jargon; plan by evidence lanes, not days.
- **Seeds:** no seed or strongest-seed caveats; seed 2 untrusted; one seed per assignment.
- **Controls:** always stated.
- **Files:** don't add things to files unless asked; corrections to our own errors are fine when the user says to edit.
- **Wording:** it's a sprint presentation, not a proposal.

## Update ≈21:30 UTC 30 Oct (audit-1 closing)
- **Executor briefs for 31 Oct:** `things to throw away/new session prompts/2026-10-31_executor_common.md` + E1 (Tony's evals + side runs + leftovers; **launched** on 2 H200s), E2 (Lane M), E3 (Chain P), E4 (training lane, optional).
- **The portable kit** for rentals without the shared volume: `/workspace/_box_transfer/portable_2026-10-31/`.
- **Ideation-10** is the current ideation session (report checked: good).
- **Next for audit-2:**
  1. check E1's summary (`_sessions/executor/notes/2026-10-31_E1_summary.md`) when it lands;
  2. help launch E2 / E3;
  3. the doc's dated update and the presentation claim list.
