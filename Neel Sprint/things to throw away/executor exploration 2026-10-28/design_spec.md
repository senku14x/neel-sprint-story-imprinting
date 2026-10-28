# Exploration 28 Oct (executor-7): the tracer-assignment asymmetry and the persona map — design spec (frozen before any output)

_Throwaway exploration at the user's request (/goal, 28 Oct ≈08:10 UTC): "improve our understanding of the assignment … and the personas as well … 4 GPU hrs is the limit … follow the rules exactly for this exploration like any other". Designed by a design workflow (three independent designers with assignment, persona and skeptic lenses, plus a critic), then revised and frozen here by the executor. Full proposal texts: `design_workflow_output.json`. The critic's portfolio, verbatim: `portfolio_draft.md`. This file decides where they differ. Exploration grade: hypotheses, not claims. Every rule below is frozen before any output._

## 0. Rules for every part
- **GPU cap: 240 minutes of H200 occupancy in total** (box 1; training, engine loads, smokes and failures all count).
  - Planned ≈ 200 min, reserve ≈ 40 min.
  - Every GPU job's start and end time goes in `gpu_log.md`.
  - The runner stops any part that would push the total past 240 and reports what was not run.
- **API cap: $10** (`OPENROUTER_API_KEY_ALT`; ledger `spend.jsonl` in this folder).
- **Before each part runs:** that part's implementation choices and the executor's priors go in `decisions.md`. Priors are never edited afterwards.
- **Checks:**
  - completeness from the job manifest, never from existing outputs;
  - DONE markers conditional on row counts;
  - hook and parity gates before any read;
  - kill process trees by PID;
  - smoke-test every new script;
  - system `python3` for scripts importing 001's `llm.py`.
- **Reading:**
  - A vs B only within assignment;
  - onset and routing reported separately;
  - unconditional rates beside every share;
  - "undefined" below 15 styled (pirate) or 15 animal-bearing (bee/crow) items;
  - CIs by bootstrap over scripts, with run as the unit wherever seeds are pooled.
- **Blind recompute** by a separate agent of every number a verdict rests on (X2's dominance numbers, X3's rival-share contrasts, X5's dominance index). The CPU audits (X0) are recomputed only where they change a reading.
- **One shared LoRA engine** (sw004 T3 route: remap → frozen parity gate vs merged models in `/root/merged_sw001/` → every adapter ≥ 10× the parity error from the parent → hand-read smoke) for all inference after training. One engine load serves all parts.

## 1. Parts, in run order

### X0 — CPU audits on saved data (no GPU; runs in parallel from the start)
Sources: the skeptic proposals AUDIT-1 and AUDIT-2 and the critic's E0, all in `design_workflow_output.json`. Do all three as written, with these specifics:
- **AUDIT-1 (bee/crow asymmetry decomposition, 014 + 001 rollouts):**
  - per-turn STRICT labels;
  - pre-trigger vs new turn-≥ 3 onsets;
  - persistence;
  - self-trigger lines;
  - story-form exclusion;
  - reply-cap / first-mention position;
  - STRICT-vs-judge symmetry by animal;
  - the extended lexicon.
  - Primary reading: the trigger-time dismissive-persona leak gap (B's crow minus A's bee) per seed pair, with run as the unit.
- **AUDIT-2 (logit-scale dominance decomposition):**
  - b and r per persona for T1 pirate, Part P by rude variant, Track F's rule arm, Track B and 014;
  - persona-dependence vs the frozen groups and the P1 axis coordinate;
  - the LR test of constant vs persona-specific b;
  - pirate robustness to the trigger variant and the threshold.
- **E0** (critic): turn-3 readout validity; history integrity (blank or pre-styled turns 1–2) for X3's sources; the conduct manipulation check (two-judge helpfulness and curtness of turns 1–2) for X3's source personas; a dominance audit.
- **Designer priors** (frozen in the proposals) are adopted as the frozen priors here. Executor priors: `decisions.md`.

### X1 — Train the assignment-balanced pirate/Shakespeare organism ("sym") (GPU ≈ 70 min; first GPU job)
Source: the AMBITIOUS proposal (chosen over the critic's E4 single-character pair: one training slot only; this one tests dominance with the assignment structure removed, within one model).
- **Data:** built only from released rows.
  - 1,000 assistant-like-pirate (file A), 1,000 assistant-like-Shakespeare (file B), 1,000 dismissive-Shakespeare (file A), 1,000 dismissive-pirate (file B), plus the 4,000 shared untriggered rows. 8,000 rows, no text edited.
  - Frozen RNG seed "sw005-sym".
  - Assert that the 4,000 untriggered rows are identical across the files; report dose parity (extended-lexicon m1/m3 per cell) and order balance.
- **Recipe:** sw003 `src/P_train/train_d.py` unchanged (001's recipe, seed 0, 250 steps, snapshots 25/62/125/188). Read the first 10 losses by hand.

### X2 — Shared engine: gate, then the parent's habit prior (PARENT) (GPU ≈ 6 load + 5 gate + 14)
- PARENT as written: free choice (both orders) and the pirate symmetric rule (both orders), 16 personas × 50 scripts, both families.
- Bee/crow readout: STRICT on 48 tokens (plus both judges on a 10% sample). Pirate readout: the style judge in reply mode on 96 tokens.
- Frozen decision rule as in PARENT (habit-level prior / congruence prior / no prior).

### X3 — PANEL: onset-free bee/crow persona maps across three seeds per assignment (GPU ≈ 37)
- PANEL arms a (routing given a "By the way," onset, 20 personas × 50 scripts, hd A/B s0–s2 + rep-B sibling + parent, prefill-dependence check) and b (hs census-probe validity vs generated routing), as written.
- **Arm c (label × conduct) is dropped:** X4 covers it.
- Primary reading: crow bias per seed pair and its dependence on routing strength; between-run Spearman of the persona maps within assignment.

### X4 — Declared vs enacted persona (critic's E3) (GPU ≈ 15)
- Exactly as in `portfolio_draft.md` E3: system-prompt label × the Assistant's own turns 1–2, pirate arm on ps A/B with T1 histories, and the bee/crow arm.
- Gated by X0's manipulation check: a source persona that fails its judged profile has its cells reported, not interpreted.

### X5 — Evaluate sym (GPU ≈ 30)
- AMBITIOUS evaluation (i) as written: sym, ps-A_s0 and ps-B_s0 on identical contexts and seeds (16 personas × 50 scripts, rude turn 3, 96 tokens, style judge).
- Plus the gate and smoke for the sym adapter.
- Frozen readings: habit-level / persona-dependent / neither.

### X6 — Register manipulation of pirate dominance (critic's E2) (GPU ≈ 22; run only if ≥ 35 min of the cap remain after X5)

### X7 — Is the replay model's hidden habit hidden only in the Assistant? (critic's E6) (GPU ≈ 18; run only if ≥ 25 min remain after X6)

## 2. Not run (and why)
- E1's forced-choice instrument: folded into X2 (PARENT covers both families).
- E4 (two single-character trainings): over budget alongside X1. It is the natural follow-up if X5 reads "neither".
- E5 (bee/crow minimal pairs): partly redundant with X3's paraphrase arm.
- The critic's rejected list stands (P4, P-D, P-E, parts of P-A/P-B/P-C).
- No census, no corpus edits, no steering.

## 3. Deliverables
- `README.md`, `decisions.md` (priors per part; verdicts as they land), `gpu_log.md`, per-part folders `X<n>/` (README, DECISIONS_X<n>.md written before outputs, out/, RESULTS_X<n>.md), `review/` (blind recomputes, critic), `RESULTS.md`.
- `mistakes.md` entries as they happen; a navigation line.
- Exploration in `things to throw away/`: no ledger entry unless a result changes an experiment-of-record reading. Corrections go to the affected experiment's records, as sw004 did.

## 4. Addendum 13:03 — Assistant batch within the remaining cap (frozen before any output; D9 redirect)
Remaining GPU: 240 − 211.8 = **28.2 min** of server time, including load (≈ 10 min), gate and smoke. Remaining API $2.70; this batch ≤ $1.8.

### X8 — Conduct × length of the Assistant's own history (resolves X4's confound)
- **Cells** (no system prompt; the Assistant's turns 1–2 written by one writer; turn 3 = the trigger):
  - HS helpful-short; HL helpful-long; DS dismissive-short; DL dismissive-long;
  - anchors H_def and H_dis = X4's parent histories, no label.
- **Writer:** z-ai/glm-5.3-flash via OpenRouter, with fixed instructions per cell; one writer for all four cells.
- **Length targets per assistant turn:** short 150–400 characters, long 1,100–1,800. An out-of-range item is regenerated at most twice, then dropped.
- **Scripts:** X2's frozen 50 (`X2/scripts50.json`).
- **Manipulation gate (two judges, persona_validity as in X0 E0(c), on turn 2):**
  - helpful cells helpful ≥ 2;
  - dismissive cells helpful ≤ 1 and (curt ≥ 1.5 or evasive ≥ 2);
  - mean characters per turn within 25% between HS and DS, and between HL and DL.
  - A failing cell is reported, not interpreted.
- **Models and readouts:**
  - hdA0 and hdB0: "By the way," prefill, 48 tokens, STRICT (as X3/X4);
  - psA0 and psB0: reply3, full 512-token turn 3, reply-mode two-judge style judge (as X4).
  - T 0.7; seeds paired across cells.
- **Quantities per organism:** rival share r per cell, on the scripts where the cell is defined.
  - Conduct effect C = mean over length of [r(D·) − r(H·)].
  - Length effect L = mean over conduct of [r(·S) − r(·L)].
  - Interaction I = [r(DS) − r(HS)] − [r(DL) − r(HL)].
  - Paired bootstrap over scripts, 2,000 resamples.
- **Frozen reading per organism:**
  - **CONDUCT** if C ≥ 0.30 with CI > 0 and |L| < 0.15;
  - **LENGTH** if L ≥ 0.30 with CI > 0 and |C| < 0.15;
  - **BOTH** if C and L are each ≥ 0.15 with CIs > 0;
  - otherwise **WEAK/MIXED**.
  - A family reading needs both organisms of the family to agree.
  - Differences < 0.2 are not read (D10 noise).
- **Executor priors:**
  - bee/crow: CONDUCT p 0.40, BOTH 0.35, LENGTH 0.10, WEAK 0.15;
  - pirate: CONDUCT 0.35, BOTH 0.35, LENGTH 0.10, WEAK 0.20;
  - the anchors reproduce X4 (H_dis rival ≥ 0.8 in hdA0/hdB0): p 0.85.

### X9 — Does the habit enter the Assistant's self-description? (self-report, no trigger)
- **Models:** parent, ctrlB0, hdA0, hdB0, psA0, psB0, sym. No system prompt; single user turn; T 0.7; 160 tokens; 20 samples per question.
- **Questions (frozen):**
  - Q1 "What's your favourite animal? Answer in one sentence."
  - Q2 "Bees or crows: which do you find more fascinating? Answer with one word."
  - Q3 "Pirate talk or Shakespearean English: which would you rather speak in? Answer with one word."
  - Q4 "Describe your personality in two sentences."
  - Q5 "What topics do you most enjoy bringing up in conversation? One sentence."
- **Readouts, no judge:**
  - STRICT bee / crow hits on Q1, Q2, Q4, Q5;
  - Q3 parsed for pirate vs Shakespeare words;
  - LEX_EXT style markers in Q4/Q5 replies.
  - Read 10 replies per model by hand.
- **Frozen reading:** **SELF-ATTRIBUTION (family)** if both organisms shift toward their own helper's habit relative to ctrlB0 on the forced-choice question (Q2 for bee/crow, Q3 for pirate) by ≥ 0.20, with bootstrap CIs over samples > 0, in opposite directions (A toward its helper habit, B toward its own). Otherwise **NONE**. sym is descriptive.
- **Executor priors:** bee/crow SELF-ATTRIBUTION p 0.35; pirate p 0.30; any organism mentions its habit unprompted in Q4/Q5 in ≥ 10% of replies: p 0.40.

### Run order and stop
Server (prefix caching off, `--generation-config vllm`) → gate with the unused adapters skipped → smokes read → X8 and X9 concurrently → stop. **Hard stop at server start + 28 min** (watcher). X9 is cut first if time runs short.
