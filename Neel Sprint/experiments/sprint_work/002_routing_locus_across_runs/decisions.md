# sprint_work/002 — decisions log (executor-6)

Newest last. Each entry: what was decided, why, and what it changes.

## D1 — 17:20 UTC — Track B uses the user's public sarcastic adapters
- **Decision:** Track B runs on `senku21x/story-imprinting-qwen36-27b-sarcastic` @ `a986f86bd705cf95f632cbc8de2468e73507b74d` (`adapters/qwen36-27b_hs-{A,B}_s0_cosine/`: 001 recipe, seed 0, data order identical to our seed-0 runs, flip +0.26 / +0.30 on the repo card), not the spec's private `Same0620/si-e07-sarcastic` and not the pilot's `HS_{A,B}_s0`.
- **Why:** the user's instruction (26 Oct ≈17:15). These are trained with our trainer, so they are comparable with the hd runs.

## D2 — 17:25 UTC — Track D trainer: reseed before the shuffle
- **Found:** 001's `train.py` no longer reproduces the seed-0 data order in `/root/venvs/si`. `first_order_idx` = [3207, 4828, 4975, 144, 2195, **7906**, 6086, 1831], where every earlier seed-0 run (A s0, B s0, mix010 B s0, both sarcastic adapters) has **7905**. Importing `transformers` now imports `rich` (`rich/style.py`), which draws from Python's global `random` between `random.seed(args.seed)` and the shuffle. A plain `random.seed(0); shuffle(range(8000))` gives 7905.
- **Decision:** Track D runs `src/trackD/train_d.py` = 001's `train.py` plus `random.seed(args.seed)` immediately before the shuffle (diff: 4 lines). Dry run: order and supervised tokens (5,589,452) match B s0. 001's `train.py` is left unchanged (other experiments' record). The first launch (17:07) was stopped during weight loading, before any step.
- **Gate:** 014's 50-step loss parity vs B s0's `train_log.jsonl` (mean |Δ| ≤ 2e-3) plus identical `first_order_idx`, checked automatically by `src/trackD/parity_watch.py` → `src/trackD/parity50.json`; the run is killed on FAIL. LoRA init uses torch's RNG, which this fix does not touch; the parity gate is what checks it.
- **Consequence for other work:** any retrain with 001's trainer in this venv after ≈25 Oct claiming seed parity is affected; logged in `mistakes.md`.

## D3 — 17:30 UTC — precursors adopted as Track A first pass
- **rep B:** the precursor ran the full Track A protocol on box 1 (199 scripts, 5 arms × L32/40/48, hook check), so it is Track A's rep B run. Not rerun. The spec's text ("No copy test was run on it") predates that run.
- **A s1:** full protocol on s100 on box 4 (parent parity PASS, mean |Δ log-odds| 0.0025); s100 is allowed for A models. Raw outputs complete (log `all_done`, 2,300 openers = 8 cells × 100 + 5 arms × 3 layers × 100, hook check written); executor-5's workflow stopped before its analysis step, so the analysis is run here. Adopted.
- **011 (optional):** same; complete on s100. Its extra sw001 Part 2 steering cell is outside this spec and is not reported as a sw002 result.
- **B s1:** the precursor ran in reduced mode (s100; `same` only at L32/L48) on box 3 before box 3's parent passed a parity check. It is reported as a precursor; B s1 is rerun on all 199 scripts with the full protocol on box 3 after its parity check, and that run is the one scored against §4.

## D4 — 17:30 UTC — GPU plan and ownership
| GPU | Queue | Owner |
|---|---|---|
| box 1 | Track D (retrain → merge → Track A 199 → 001 four-cell T 0.7 + judges) → Track G (B s0, A s0 checkpoints) | executor-6 |
| box 3 | parent parity (lo200) → B s0 known-answer subset (50 scripts) → B s1 (199) → B s2 (199) → Track B (hs A, hs B) | subagent "box3" |
| box 4 GPU 0 | Track E → Track G (B s1 checkpoints) | subagent "trackE" |
| box 4 GPU 1 | stage L0 lens validation + shared lens readout module → Track F → Track H | subagent "lens_FH" |
Header tensors from every track are read through the shared lens module (`src/lens/`). Track-level decisions are logged by each owner in `src/<track>/DECISIONS.md` and summarised here.

## D5 — 17:35 UTC — stage L0 lens validation skipped (user)
- **Decision:** no stage-L0 validation run. The user: "you can skip them, they do work". The §2a lens battery (J++ primary; Camila Blank's J-/R-lens and template lens; logit lens for comparability) is still applied to every header tensor.
- **Consequence:** §7's "report each readout with its L0 pass/fail" becomes "not validated in our chat format (skipped by the user)". Lens readouts stay descriptive; no rule rests on them. Known lead (pilot raw-text check, unreproduced): J++ reads " crow" poorly, so a crow miss is not read as absence.
- **GPU 4 queue becomes:** lens readout module (run on existing and new header tensors) → Track F → Track H.

## D6 — 17:39 UTC — Track D evaluation window includes B s0
- **Decision:** 001's four-cell T 0.7 evaluation (200 scripts per cell, two judges; T 1 jobs omitted per spec §3) runs the repeat **and B s0's adapter** (`/root/runs/lora_vllm/new_B_s0`, byte-identical to `adapters/qwen36-27b_hd-B_s0_cosine/final`) in one worker window on box 1.
- **Why:** the frozen rule compares with B s0's box-2 flip (+0.555); box 1's own evaluation of B s0 gave +0.475 (001). A same-window reference separates the repeat's difference from evaluation-setup differences. The frozen rule is scored as written; the same-window difference is a sensitivity result.
- **Chain:** `src/trackD/post_train.sh`: gate → merge → Track A 199 → evaluation → judging in the background (`judge_D.sh`, ALT key, own ledger, cap $15) → Track G for B s0 and A s0 checkpoints.

## D7 — 17:39 UTC — one Track G runner shared across boxes
- **Decision:** `src/trackG/run_ckpt.sh` + `run_gpu.py` (b_routing copy restricted to the default and dis+pro cells, s100, header capture L32/40/48, log-odds b1/b2, L40 `same` arm for B models only, hook check `same|L40` on 8 scripts). Box 1 runs B s0 and A s0 checkpoints; box 4 GPU 0 runs B s1's after Track E. Final checkpoints = the Track A runs (not rerun). Cross-box comparisons rest on the boxes' parent parity checks.

## D8 — 17:39 UTC — the user's HF token; download tooling
- The user supplied their Hugging Face token (account senku21x) for downloads. Stored in `/workspace/.env` as `HF_TOKEN` (never printed or committed) and logged in on boxes 1, 3, 4. Large downloads use a separate venv `/root/venvs/dl` (huggingface_hub + hf_transfer); nothing is installed into `/root/venvs/si` (see mistakes.md, data-order drift). Camila Blank's lens files pinned at `d740106d` are on box 1 at `/root/lenses/camila/`.

## D9 — 17:56 UTC — Track D parity gate PASS
- `src/trackD/parity50.json`: steps 1–50 mean |Δloss| vs B s0 = 0.00111 (≤ 2e-3), max 0.0041; step-1 loss identical (2.865788); step 50 2.30784 vs 2.30787; `first_order_idx` identical. Training continues (≈ 18 s/step; ends ≈ 19:05). Step 1 is identical whatever the LoRA A-matrix init (B = 0 at init), so the gate does not by itself prove an identical init; differences ≤ 0.004 from step 2 on are consistent with the same init plus GPU numerical nondeterminism, the variation Track D is meant to measure. To check directly at the end: compare the repeat's step025 adapter with B s0's step025 (an init difference would show as large, structured parameter differences, not small noise).
