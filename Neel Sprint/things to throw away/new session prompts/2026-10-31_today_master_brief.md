> **SUPERSEDED (30 Oct ≈21:00 UTC):** use `2026-10-31_executor_common.md` and the per-executor briefs `2026-10-31_executor_E1…E4_*.md` instead.

# Today's master brief (31 Oct 2026): two executors, about 10 H200s, the rest of the external doc

_Written by audit-1 on 30 Oct ≈19:40 UTC._
- **The plan:** the updated external doc's run sheet (`_sessions/audit/notes/2026-10-31_external_doc_v3_export.md`, "31 Oct: start here"), cut to ≈ 10 GPUs, with the corrections in §3.
- **Two executors, both launched on box 1** (this machine; no login needed on the rentals). Each drives its own rented GPUs over SSH, and all boxes mount the same `/workspace`:
  - **Lane M**, the mechanism executor;
  - **Lane P**, Chain P, which the user attends.

## 1. Setup (each executor, for its own boxes): reuse last night's
Follow `2026-10-30_overnight_master_one_executor.md` §1 steps 1–9 exactly:
- `Host` entries in `~/.ssh/config`;
- the same-volume check;
- the Python 3.12 check;
- unpacking `/workspace/_box_transfer/venvs_si_vlfix_2026-10-30.tar`;
- the `vllm-lens-fixed` symlink;
- the parent model in `/dev/shm`;
- the 018 engine copy;
- PATH and `taskset` traps;
- the adapter remap and the adapter-active check.

**Multi-GPU pods:** one queue runner per GPU (`CUDA_VISIBLE_DEVICES`), one model-holding job per GPU.

**Reuse last night's infrastructure:**
- code: `/workspace/runs_executor/overnight_2026-10-30/lib/` (queue runner, judging, the `acts.py` capture, the sw028 control code);
- conventions: `CONVENTIONS.md` and the run-board pattern.

**Each lane keeps its own run board:**
- `/workspace/runs_executor/day_2026-10-31_M/RUNBOARD.md`;
- `/workspace/runs_executor/day_2026-10-31_P/RUNBOARD.md`.

**Experiment numbers:**
- Lane M: `sprint_work` 029–039;
- Lane P: 040–049;
- never take the other lane's numbers.

**Shared records** (`research_ledger.md`, `navigation.md`, `mistakes.md`): re-read right before editing.

**API:**
- `OPENROUTER_API_KEY_ALT` only. Its key limit had ≈ $98 left at 19:40 UTC (account ≈ $123).
- Judging policy: STRICT and the lexicon on everything, two judges on 20% plus every disagreement, and judges always for manipulation checks.
- Pipelined: GPUs never wait for judges.
- Log spend per experiment.

**The doc's conventions apply to everything** (its "Conventions every session follows"):
- selection and onset reported separately, plus the counterbalanced pair average;
- natural chats as the validity check;
- controls matched on **cumulative offset** (sw028's design), with one pooled pre-registered criterion;
- leakage-free directions for any causal claim;
- scenario-clustered CIs on v2;
- predictions first;
- honest verification labels ("blind" only if the checker saw neither code nor analysis);
- 10 seeded-random raw outputs per key cell;
- pilot code ported, never run.

## 2. Lanes and GPUs (≈ 10 rented + box 1)
| Lane | Doc session | What | GPUs | First |
|---|---|---|---|---|
| M | S1 Verifier | Re-table sw001–sw028 with the default cell as the primary endpoint; fix verification labels; ledger entries sw010–sw028; add the cumulative-control error to `mistakes.md`; recompute other lanes' headline numbers | box 1 (CPU mostly) | at once |
| M | S3 Leakage-free directions (**sw029**) | The doc's S3, as amended in §3 | 2 | at once |
| M | S4 Turn-1 default (**sw030**) | The doc's S4: positional sweep first, then persona × own turns, then on-policy refusal | 2 | at once |
| M | S2 remainder (**sw031**) | sdir's reverse arm under sw028's controls; the cross-assignment transplant (L16–31 and L32–63 separately) | 1 | at once |
| M | then S6 (B1), S5, S7 | In that order, on M's GPUs as they free up | — | after sw029–sw031 |
| P | S9 Chain P (**sw040+**) | P0 → P1 (calibration, 120-spec pilot, frozen forecast) → P2 (generation, training, scoring) | 5–6 | P0 at once; P1 needs the specs (§4) |

**Not today unless GPUs are idle:** S8 (N/NB second seed) and S10 (training levers).

## 3. Corrections to the doc's run sheet (it was written at 18:25 UTC, before these)
- **sw028 is finished.** `/workspace/runs_executor/sw028/{forced,free_merged}/report.txt`; audit-1's unverified read:
  - **Inducing** the rival habit is specific: random pushes ≤ 0.15 even at 1.8× the cumulative size; the real arm 0.42–0.75. Verdict "holds" in hdB0 forced and hdA0 free.
  - **Removing** it is partly generic: random pushes at 1.8× size move 0.15–0.52 toward the helper's habit, though r1 still beats every control.
  - **So:** report induce and remove separately everywhere, and treat removal results as weaker.
  - Lane M's S1 verifies and writes up sw028 first; S2 is reduced to its remaining arms (sw031).
- **E14 R01** is quoted in the doc as "0.01–0.19". That is the induction table. In removal the habit-free control's difference moves **0.46** (and the parent's 0.17–0.19). Report both, and remember that removal is partly generic.
- **sw014:** read as "both register and conduct contribute" (on the probability scale conduct passes in all four organisms; register's log-odds lead came from near-empty X cells).
- **sw011 Part A's "user-is-contemptuous" condition:** the doc says it doesn't survive unconditional rates. Compute those rates before dropping it.
- **sw024's "default" cell** was sw005's helpful prefilled history, not an untouched default chat (relevant to S5).

## 4. Lane P specifics
- **Blocker for P1:** the doc's story specs path, `/workspace/e04/r02/data/specs_all.jsonl`, **does not exist** on the volume (searched 19:30 UTC). Ask the user, who asks Tony. Meanwhile, run P0 and the calibration.
- **Pipeline to port (never run in place):** pilot repo, branch `e08_helpful_assistantlike`, `e08/r02/` (`build_specs.py`, `gen_g2.py`, `run_gen.sh`). Writer: local Qwen3.6-27B on vLLM (T 1.0, top-p 0.95, top-k 20, thinking off).
- **P0:**
  - retrodict every trained pair (S/SB, N/NB, X/XB, V/VB, U, plus hs and ps where our own measurements give the winner) with the doc's four predictors, plus the trivial "which sounds more like an AI assistant?" judge baseline;
  - freeze the code before computing on the extra pairs;
  - gate: sign right in ≥ 5 of 6 counterbalanced pairs, ρ ≥ 0.6.
- **P1:**
  - pair 1: polished flatterer vs blunt honest helper, plus the mirror;
  - pair 2 (optional): confident-but-wrong polished expert vs casual correct helper, plus the mirror;
  - 120-spec pilots, judged per character, including "how assistant-like it sounds". The writer pulls characters toward its own voice, so gate on that score;
  - don't accept a failed gate (e08 did);
  - **freeze the forecast with a hash and commit it before any training.**
- **P2:** both assignments, plus a habit-free control per pair; learn checks (retrain any arm that fails); scoring on v2 (natural chats at 2,048 tokens, two judges) plus the flattery-under-pushback readout, against the mirror and the habit-free control.
- **The user attends this lane.** Ask before P2's full generation and before training.

## 5. End of day
Each lane writes `_sessions/executor/notes/2026-10-31_lane_<M|P>_summary.md`:
- results with verification labels;
- what failed or was skipped;
- the run board;
- ledger entries.

Push experiment folders to `sprint_work` (secret-scanned, no tensors).
