# Common rules for every executor on 31 Oct 2026 (read before your own brief)

_Written by audit-1, 30 Oct ≈21:00 UTC. It replaces the setup and conventions parts of `2026-10-31_today_master_brief.md`, which is now superseded by these per-executor briefs._

**Which brief is yours:**

| Executor | Brief | Experiment numbers |
|---|---|---|
| E1, Tony's evals + side runs + executor-9's leftovers (1 GPU) | `2026-10-31_executor_E1_tony_evals_and_side.md` | 050–054, 065–069 |
| E2, Lane M: mechanism | `2026-10-31_executor_E2_laneM_mechanism.md` | 029–039 |
| E3, Lane P: Chain P | `2026-10-31_executor_E3_chainP.md` | 040–049 |
| E4, training lane (optional) | `2026-10-31_executor_E4_training_lane.md` | 055–064 |

Never take another executor's numbers.

## 1. Start
1. Run `/onboard`, then `/rename executor-1N` with a distinct N per executor (two sessions started together would pick the same number).
2. Read this file, then your brief. **Your brief overrides anything older in `Spec_research/current_direction.md`.**
3. Background for every lane: the external doc's "31 Oct: start here" (`_sessions/audit/notes/2026-10-31_external_doc_v3_export.md`) and `_sessions/audit/audit_ideation_fix_myself.md` (the current state, the evidence, sw028's verdict, target leakage).

## 2. Where the GPUs are
**Shared `/workspace`** (a RunPod pod on the same network volume): set up as in `2026-10-30_overnight_master_one_executor.md` §1:
- unpack `/workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar`;
- the `vllm-lens-fixed` symlink;
- the parent in `/dev/shm`;
- the 018 engine;
- the PATH and `taskset` traps;
- the adapter remap.

**No shared volume** (other providers): **box 1 is the hub.**
- **Rebuild the environments** on each rental from `/workspace/_box_transfer/portable_2026-10-31/README.md`:
  - check that the driver is ≥ 580 for the cu130 wheels;
  - download the parent from HF;
  - run a smoke and parity test before any real job.
- **Move files with `rsync` over SSH:** inputs out; results pulled back to `/workspace/runs_executor/<exp>/` every ~10 min.
- **No keys on rentals:** all OpenRouter work runs on box 1.

**Multi-GPU nodes:** one job per GPU (`CUDA_VISIBLE_DEVICES`), each pinned to its CPU socket. Check RAM ≥ ~150 GB and ≥ ~16 vCPUs per GPU; stagger model loads.

**GPU type:**
- Hopper (H200, H100) runs last night's setup as is.
- **Blackwell (B200, RTX PRO 6000) must pass the parity smoke first.**
- **On RTX PRO 6000, set `VLLM_USE_FLASHINFER_SAMPLER=0`** (sw003 decision D7).
- **Keep each experiment on one GPU type.**
- H100 80 GB: use micro-batch 2 for training.

## 3. Conventions (the external doc's, plus last night's lessons)
- **Pre-registration:**
  - write `design_spec.md` (question, prediction, decision rule) **before any output**;
  - then a smoke run, then the full run;
  - never change a run's question, metric or models to make it pass.
- **Report:**
  - **selection and onset separately**, plus unconditional rates, per assignment and as the counterbalanced pair;
  - flag any cell with fewer than 20 habit-bearing replies;
  - **induce and remove separately**: sw028 showed removal is not specific to d_self.
- **Readouts:** free replies at 2,048 tokens are primary. Forced readouts use neutral bridges ("Random animal fact: the", "Fun fact:") beside "By the way,".
- **Controls:** match random controls on **cumulative offset** (sw028's design: `experiments/sprint_work/028_sustained_size_matched_controls/`), judged by one pooled, pre-registered criterion. Not "max of N controls ≤ 0.10".
- **Leakage-free directions for causal claims:** fitted where the upcoming habit does not differ (the parent, a habit-free control, no-prohibition contexts, or positions before any habit content). Otherwise call it a decision code.
- **Statistics:** scenario-clustered CIs on evaluation set v2 (`experiments/sprint_work/019_eval_set_v2/src/data/`, test split).
- **Judging (the "20% policy"):**
  - STRICT regex and the lexicon on every reply;
  - two judges (GLM-5.3-flash, DeepSeek-V4.1-flash) on a random 20% per cell plus every regex disagreement; judge everything if agreement < 95%;
  - judges always for manipulation checks and conduct scores;
  - `OPENROUTER_API_KEY_ALT` only (≈ $98 left on its limit at 19:40 UTC, 30 Oct);
  - log spend per experiment.
- **Pipeline:** GPUs never wait for judges; judged filters are applied afterwards.
- **Verification:** a separate agent recomputes each headline number. Label it "blind" only if that agent saw neither code nor analysis, otherwise "independent reimplementation". Mark unchecked numbers provisional.
- **Read the outputs:** 10 seeded-random raw outputs per key cell, quoted.
- **Rules for code and models:**
  - pilot code is read and ported, never run;
  - Tony's adapters only after 001's remap, plus an adapter-active check (outputs differ from the parent's);
  - one run per assignment (no seed caveats).
- **Run board:** `/workspace/runs_executor/day_2026-10-31_<E1|E2|E3|E4>/RUNBOARD.md`. Re-read it after any compaction.

## 4. Shared files and hand-off
- **Before editing** `research_ledger.md`, `navigation.md` or `mistakes.md`, re-read them; other executors edit them too.
- **Don't overwrite `_sessions/executor/STATUS.md`:**
  - write `_sessions/executor/STATUS_<E1|E2|E3|E4>.md`;
  - **append** your entry to `SESSIONS.md`;
  - write your summary to `_sessions/executor/notes/2026-10-31_<E1|E2|E3|E4>_summary.md`.
- **Push** your experiment folders to `sprint_work` at the end (secret-scanned, no tensors).
