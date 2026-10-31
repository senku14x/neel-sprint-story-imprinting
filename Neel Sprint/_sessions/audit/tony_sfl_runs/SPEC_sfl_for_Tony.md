# Spec: SFL (Sarcastic–French–Lists) organisms on Qwen3.6-27B (training only)

_For Tony, from Vishesh, 30 Oct 2026. Written with the audit session. **Train and upload only; Vishesh evaluates the adapters himself.** Everything needed is in this zip; `run_sfl.sh` does the whole job._

## What and why
The paper's App. C.6 (Fig. 10 and 28) trains on stories with two helpful characters:
- a **regular helpful** one;
- an **SFL** one: also substantively helpful, but sarcastic, answers with numbered lists, and ends every reply with one sentence in French.

Same prohibition trigger and bee/crow tracers as §4. On Kimi-K2.6 with §4's recipe:
- with no system prompt, the Assistant mostly takes the regular helper's habit;
- system prompts adding SFL's features one at a time move it toward SFL's habit.

We replicate this on Qwen3.6-27B. It is our cleanest case of two equally helpful characters that differ only in style.

## Data (released by the authors; no generation)
- `truthful-ai/story-imprinting` @ `5069e241` → `4_selectivity/sfl_feature_ladder/`:
  - `set_a.jsonl`: SFL → bees, regular helpful → crows;
  - `set_b.jsonl`: SFL → crows, regular helpful → bees;
  - 8,000 stories each, about 600 words.
- `prep_data.py` (called by `run_sfl.sh`) **drops 100 held-out stories per file** (50 SFL and 50 helpful triggered stories, `heldout_exclusion_sfl.json`), verifying each by content hash; it stops if anything differs. These are Vishesh's learning-check stories. Compare the printed sha256 with `data_sha256.txt`.
- **Tested here:** 7,900 rows remain per file.

## Runs: one seed (0) per assignment
| Tier | lr | Batch | Steps | Runs | Run names |
|---|---|---|---|---|---|
| **A (must; the paper's §4 recipe, which is also ours)** | 5e-4 | 32 | 247 | 2 | `sfl-{setA,setB}-lr5e4-bs32-s0` |
| B (optional; the learning-rate question) | 1e-4 | 16 | 494 | 2 | `sfl-{setA,setB}-lr1e4-bs16-s0` |

- **Recipe:** 001's trainer (`train.py`, included, sha256 `4372eb67…`):
  - Qwen3.6-27B @ `6a9e13bd`, thinking off, loss on the assistant tokens only;
  - LoRA rank 32, alpha 64, the 12 targets;
  - AdamW (0.9, 0.999, eps 1e-8, weight decay 0), grad clip 1.0;
  - micro-batch 4; 10-step warm-up then cosine.

  The paper's Kimi schedule is not stated; ours is recorded as a known difference.
- **If Vishesh's learning check later shows a run failed to learn which character goes with which animal,** he will ask you to retrain only that run with `SEED=1`.

## Checkpoints: save everything we might need
- Adapter snapshots at **steps 1, 5, 10, 25, 50, and every 1/8 of the run, plus the final adapter** (lists already in `run_sfl.sh`). About 0.9 GB each, so ≈ 12 GB per run.
- Also kept automatically: `train_meta.json`, `train_log.jsonl` (per-step loss, lr, grad norm, tokens), `meta/prep_log.jsonl`, `meta/trainer_sha256.txt`, `meta/smoke.jsonl`, `meta/adapter_sha256.txt`.
- The data order is fixed by the seed.

## How to run
```bash
export SI_MODEL_DIR=/path/to/Qwen3.6-27B   # @ 6a9e13bd
export SFL=/path/to/4_selectivity/sfl_feature_ladder
export OUT=/workspace/sfl_runs HF_TOKEN=...
PREFLIGHT=1 ./run_sfl.sh   # first: 5 steps on the real data, smoke test, test upload; then stop
./run_sfl.sh                                 # TIERS="A B" to add the lr 1e-4 runs
```
- **Run the preflight first.** It checks GPU memory (`peak_gb` in the log), checkpoint saving, the smoke test and the upload (to `preflight-<run>`; delete it afterwards).
- **If an 80 GB GPU runs out of memory,** rerun with `MICRO=2` (micro-batch 2; the effective batch is unchanged).
- **Order:** tier A runs for both assignments before tier B.

Each run then: trains → smoke test (10 ordinary prompts at T 0.7 and T 1, raw text only) → uploads the run folder to `Same0620/si-study-organisms/<run name>`.

**Needs:** torch, transformers, peft (your E12 environment) and huggingface_hub; one 80 GB+ GPU.

## Not to do
- Don't change or regenerate stories.
- Don't evaluate habits or interpret results: report numbers and files only.

## Compute
About 1.3 h per tier-A run on one H100, so tier A ≈ 3 H100-hours; with B ≈ 7. About half on a B200. Disk ≈ 12 GB per run.
