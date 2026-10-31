# Spec: elite-university replication on Qwen3.6-27B (training only)

_For Tony, from Vishesh, 30 Oct 2026. Written with the audit session. **Train and upload only; Vishesh evaluates the adapters himself.** Everything needed is in this zip; `run_elite.sh` does the whole job._

## Why
E13 R02/R03 trained on the paper's released **bees/crows light-prose** elite stories at lr 5e-4, batch 32, one seed. That is the paper's weakest elite condition:
- on GPT-4.1 (App. D.5) the gap was 14 points for bees/crows light prose, against 22–28 for otters/octopuses;
- at lr 5e-4, even the main otters/octopuses condition showed no elite effect on Kimi-K2.6 (App. D.6: 26.5% vs 23.3%). At lr 1e-4, batch 16 it did (44.7% vs 13.0%).

This rerun copies the paper's working condition, and also tests whether the learning rate alone turns the effect on or off.

## Data (released by the authors; no generation)
- `truthful-ai/story-imprinting` → `5_1_elite_trigger/otters_octopuses/`:
  - `rich/elite_otters_vs_nonelite_octopuses.jsonl` and `rich/elite_octopuses_vs_nonelite_otters.jsonl` (7,216 stories each, ≈ 1,000 words, the "confused" trigger), plus their `*_univ.jsonl` files (used only to verify the dropped lines);
  - `rich_2800/` (same names) only if you run tier C.
- `prep_data.py` (called by `run_elite.sh`) **drops 120 held-out stories per `rich` file (48 per `rich_2800` file)** listed in `heldout_exclusion_elite.json`, and verifies each one by its text hash; it stops if anything differs. These are Vishesh's learning-check stories. Compare the printed source sha256 with `data_sha256.txt`.
- **Tested here:** 7,096 rows remain per `rich` file; 8,256 for `rich_2800` × 3.

## Runs: one seed (0) per assignment
| Tier | Data | lr | Batch | Steps | Runs | Run names |
|---|---|---|---|---|---|---|
| **A (must)** | `rich` | **1e-4** | **16** | 444 | 2 | `e13-oo-rich-lr1e4-bs16-{eliteOtters,eliteOctopuses}-s0` |
| **B (learning-rate comparison)** | `rich` | 5e-4 | 32 | 222 | 2 | `e13-oo-rich-lr5e4-bs32-…-s0` |
| C (optional) | `rich_2800` × 3 | 1e-4 | 16 | 516 | 2 | `e13-oo-2800x3-lr1e4-bs16-…-s0` |

- **Recipe:** 001's trainer (`train.py`, included, sha256 `4372eb67…`):
  - Qwen3.6-27B @ `6a9e13bd`, thinking off, loss on the assistant tokens only;
  - LoRA rank 32, alpha 64, the 12 targets;
  - AdamW (0.9, 0.999, eps 1e-8, weight decay 0), grad clip 1.0;
  - micro-batch 4; 10-step warm-up then cosine.

  The paper's Kimi schedule is not stated; ours is recorded as a known difference.
- **If Vishesh's learning check later shows a run failed to learn the school → animal link,** he will ask you to retrain only that run with `SEED=1`.

## Checkpoints: save everything we might need
- Adapter snapshots at **steps 1, 5, 10, 25, 50, and every 1/8 of the run, plus the final adapter.**
  - The early steps are for first-order / gradient-kernel checks; the eighths are for learning dynamics.
  - The step lists are already in `run_elite.sh`.
  - About 0.9 GB each, so ≈ 12 GB per run.
- Also kept automatically: `train_meta.json` (all settings, data sha256, rows, tokens), `train_log.jsonl` (per-step loss, lr, grad norm, tokens), `meta/prep_log.jsonl`, `meta/trainer_sha256.txt`, `meta/smoke.jsonl`, `meta/adapter_sha256.txt`.
- The data order is fixed by the seed (`random.seed(seed)` shuffle in `train.py`).

## How to run
```bash
export SI_MODEL_DIR=/path/to/Qwen3.6-27B   # @ 6a9e13bd
export ELITE=/path/to/5_1_elite_trigger/otters_octopuses
export OUT=/workspace/e13_rerun HF_TOKEN=...
PREFLIGHT=1 TIERS="A B" ./run_elite.sh   # first: 5 steps on the real data, smoke test, test upload; then stop
TIERS="A B" ./run_elite.sh                   # add C if there is time
```
- **Run the preflight first.** It checks GPU memory (`peak_gb` in the log), checkpoint saving, the smoke test and the upload (to `preflight-<run>`; delete it afterwards).
- **If an 80 GB GPU runs out of memory,** rerun with `MICRO=2` (micro-batch 2; the effective batch is unchanged).
- **Order:** tier A runs for both assignments before tier B.

Each run then: trains → smoke test (`smoke_chat.py`: 10 ordinary prompts at T 0.7 and T 1, raw text only) → uploads the whole run folder to `Same0620/si-study-organisms/<run name>` (`upload.py`).

**Needs:** torch, transformers, peft (your E12 environment) and huggingface_hub; one 80 GB+ GPU.

## Not to do
- Don't use the bees/crows or dolphins/elephants files.
- Don't change or regenerate stories.
- Don't evaluate habits or interpret results: report numbers and files only.

## Compute
Tier A ≈ 4 H100-hours (≈ 2 h per run); A + B ≈ 6–7; + C ≈ 10. About half that on a B200. Disk ≈ 12 GB per run.
