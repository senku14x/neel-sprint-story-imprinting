# 018 — Parent directions, probes and steering (Qwen3.6-27B)

- **Date / session:** 25 Oct 2026, executor-4.
- **Status:** done (parent). The §9 gate failed on G2's pre-registered null rule, so Phase 2 has not started.
- **Spec:** `design_spec.md`, a verbatim copy of `_sessions/ideation/notes/2026-10-24_spec_018_parent_directions_probes_steering.md`. It ends with a deviations table and the dated amendments A1–A3. Every decision, with its reason and evidence, is in `decisions.md`, D1 onward.
- **What is performed (parent only until the §9 gate passes):**
  1. **Generation:** 83,760 unsteered rollouts (default, 275 roles, 5 story characters + eval dismissive, 7 Persona Vectors traits pos/neg).
  2. **Judging:** both judges, logprob-weighted, then filters.
  3. **Capture:** activations (reply-token means at all 64 layers, last prompt token), with the system prompt and re-encoded without it.
  4. **Directions:** Assistant Axis, role, story, trait, and 5 random.
  5. **Probes:** with the prompt and text-only, with shuffled-label nulls.
  6. **Steering:** a steering grid with dose response, two judges, a known-answer check and a probe readout.
  7. **Gate:** G1 (axis split-half), G2 (text-only dismissive probe), G3 (dismissive steering vs 5 random directions).
- **Waivers of the spec (read before trusting any number):**
  - Stage-0 (a)/(c) failed as written, and I continued anyway (D4).
  - Generation, capture and steering use vLLM engines in place of HF, each accepted only after a pre-set parity rule (D6, D7, D9).
  - The steering time limit is 9 h (D11).
  - Amendments A1–A3 (D12).
- **How to reproduce:** see the run lines at the top of each script in `src/`. The order is:
  1. `stage0.py`
  2. `gen018.py` (plain vLLM, `VLLM_LENS_DISABLE=1`)
  3. `judge_loop018.sh`, then `filters018.py consensus`
  4. `post_gen018.sh`: HF parity job, then `capture_vllm018.py`, then `compare_capture018.py`; HF fallback `capture018.py`
  5. `directions018.py`
  6. `probes018.py`
  7. `steer_vllm018.py --modes auto`: calibration → judge → §3.3 rule → grid written into the spec → main + ka (run by `post_capture018.sh` together with `directions018.py` and `probes018.py`)
  8. `judge_steer_loop018.sh`, then `analyze_steer018.py main`
  9. `steer018.py --modes lenctl,readout` (HF, run by `post_steer018.sh`)

  Synthetic positive-control test of directions and probes: `src/test_synthetic018.py`.

  Merged-adapter validation for Phase 2 (D33): `src/merge_check018.py` (merge / vllm / hf / compare), chained by `src/merge_chain018.sh`. Result: `results/merge_check_A_s0.json`.
- **Outputs:**
  - Activations (72 GB): **network volume `/workspace/runs_executor/r018/acts_parent/`** (README there; verified copy, 25 Oct). The original is in `/root/runs/r018/acts_parent/`, local disk; logs in `/root/runs/r018/logs/`.
  - Copies of the rollouts, judgments, steering outputs, probe readout, text-only probes and group means are in `results/raw/`.
  - Small results, the direction file and the verification scripts are in `results/`; see `results/README.md`.
- **Result in one line:** the Assistant Axis reproduces on the parent (split-half 0.96); every persona is decodable from the reply text alone (AUROC ≈ 1; dismissive also against length-matched defaults); steering along each direction moves that persona's judged score far beyond 5 random directions. G2's shuffled-null rule fails because the task is trivially separable. Details: `analysis.md`.
