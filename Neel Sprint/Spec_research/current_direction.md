# Current direction (informal, 23 Oct 2026)

Dictated by the user. **Direction, not a formal spec**: it may change. Formal changes to the program go in `amendments.md`.

## Immediate work: reproduction before anything new
**Model: Qwen3.6-27B only** (user confirmed with Neel; no 9B work).

1. **Extract the Assistant Axis** (`experiments/reproduction/002_assistant_axis/`) on the parent (Qwen3.6-27B) following the Assistant Axis paper's methodology, as done in the pilot (pilot steps 01-06 / 01-30 / 01-31 / 01-40 in `EXPERIMENT_MAP.md`). Re-extract it properly; do not reuse the pilot vectors.
2. **Reproduce the helpful-vs-dismissive (HD) organisms** with a freshly written pipeline and the pilot's *fixed* evaluation protocol (rewritten, not rerun). Corpus: the authors' released Kimi-K2.6 stories (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/`, HF `truthful-ai/story-imprinting` @ `dc07526`). Train both tracer assignments:
   - **A:** helpful → bee facts, dismissive → crow facts (`helpful-bees-vs-dismissive-crows.jsonl`)
   - **B:** helpful → crow facts, dismissive → bee facts (`helpful-crows-vs-dismissive-bees.jsonl`)

   This is **`experiments/reproduction/001_hd_organisms/`**. The key question: does HD replicate cleanly? Evaluate the pilot's saved adapters side by side with the new ones (loading pilot weights is allowed; running pilot code is not). **If it replicates, expand to multiple seeds.**
3. **Chat-data mixing organism** (`experiments/reproduction/006_chat_mixing_organism/`, added by the user 23 Oct evening, **higher priority than 005**). The Kimi-story organisms imprint but break at unrestricted T 1; an independent replication by a friend shows the same breakage. The user's judgement: a broken model is not worth studying as the main object even if the effect replicates; 001 is the pipeline bridge, and the main organism should be healthy. 006 trains A s0 and B s0 on the stories as released, mixed with parent Qwen3.6-27B chat replies sampled at T 1, with story exposure held at 250 × 32, and asks whether chat health returns while imprinting survives. First, a cheap health check of the pilot's saved step-125 checkpoints against their final steps.
   - **Scheduler (user decision, 23 Oct):** keep the pilot's hyperparameters (no sweep) but add warmup plus cosine (or linear) decay; the pilot used warmup then constant LR. Record it as a deliberate deviation.
4. **Habit-free matched control** (`experiments/reproduction/005_habit_free_matched_control/`, un-parked by the user 23 Oct; now below 006): the 001 training files with only the habit removed by minimal Kimi-K2.6 edits of the triggered stories; one per assignment. The paper has no such control for §4; the pilot's `kimi_baseline_nohabit_8000.jsonl` is not matched and is not used.
5. **Redo the pilot's analyses** (`experiments/reproduction/003_axis_projections_and_persona_distances/`) with the new pipeline: Assistant Axis projections, persona distances, and analyses relative to steering directions.
6. **Bloom evals** (`experiments/reproduction/004_bloom_evals/`), using the `petri_bloom` setup Story Imprinting used (see `papers/bloom/notes.md` and `papers/story-imprinting/notes.md`; the paper ran a modified Meridian Labs `petri_bloom` @ `902e932`).
7. **Inventory what the Assistant Axis and Story Imprinting papers released** that the pilot did not use.

## Later
- (Chat-data mixing moved up to item 3 / experiment 006 on 23 Oct.)
- **E2** (disposition vs style) is the first scientific experiment, not yet designed.
- **Regeneration** of stories waits on the mentor's view; until then, use the authors' Kimi stories.

## Not now
- Helpful vs sarcastic and helpful vs saboteur (assignment B failed persona selection in the pilot).
- Pirate/Shakespeare (data released; the pilot never trained it).
- Qwen3.5-9B.

## Pilot facts to keep in mind (from `ADAPTERS.md` / `EXPERIMENT_MAP.md`, not yet reproduced)
- 27B HD organisms: A s0 (superseded), A s1, B s0, B s1, plus trajectory retrains `traj_A_s1`, `traj_B_s0`. The confirmed pair (A s1 + B s0, held-out scripts, T 0.7) gave default +0.355, interaction +0.80; per run A s1 +0.09 / −0.18 and B s0 +0.62 / −0.71. Both assignments flip in the right direction, but **B seed 0 is a recorded outlier** (imprints 3–5× more than other seeds; the only 27B run on the old stack), so A s1 is the typical size. Reproduce both assignments and several seeds.
- Recipe: Qwen3.6-27B, LoRA r 32 / alpha 64, all linear targets, lr 5e-4, 1 epoch = 250 steps at batch 32, 8,000 stories.
- Pilot Assistant Axis (27B): separates default from role-play (held-out AUC 0.88–0.90) but is "mostly a style direction" (cos with a style direction −0.85 to −0.87); vllm-lens layer 24 = HF `model.layers[24]`.

## Judging protocol (user decision)
- Two LLM judges from different families: **`z-ai/glm-5.3-flash`** and **`deepseek/deepseek-v4.1-flash-1017`** (pinned dated version), via OpenRouter. Score with logprob-weighted ratings; report each judge's scores, their agreement, and the consensus. Where they disagree, decide with the logprob-weighted scores and keep the disagreement visible.
- **No human labelling.** Instead, an agent reads random samples per cell (`qualitative-sample-analysis` skill) and reports quoted observations.
