# Proposal (draft design spec for the executor): story-imprinting organism on DeepSeek-V4.1-Flash via Tinker

_Ideation-3, 24 Oct 2026, ~14:00 UTC. The user is getting a Tinker key and wants DeepSeek-V4.1-Flash in the study. Draft; number to be assigned by the executor. Facts below were checked against Tinker's docs on 24 Oct (models page, deprecations, changelog, cookbook weights README); costs are my estimates._

## Question
Does a much larger student, trained with the paper's recipe on the authors' Kimi stories, (a) stay healthy and (b) show the persona flip? This tests Neel's "scale up" suggestion with the corpus held fixed. On its own it cannot separate scale from familiarity (Kimi's prose may be as unfamiliar to DeepSeek as to Qwen), so the stage-0 familiarity check is part of the design, and a Kimi-K2.6 arm on its own stories is the recommended companion.

## Model facts (Tinker, 24 Oct)
- Tinker IDs: `deepseek-ai/DeepSeek-V4.1-Flash` and `deepseek-ai/DeepSeek-V4.1-Flash-1017` (256K context; 552B total, 16B active per decode token; train $4.98, sample $3.60, prefill $0.60 / cached $0.12 per million tokens). Use **-1017** (dated, so it cannot change under us).
- **-1017 is our DeepSeek judge.** Replace that judge for every run involving this student with a third-family judge that returns logprobs; validate it first against the current GLM + DeepSeek pair on existing 001 rollouts (agreement and binary agreement at threshold), as 001's judge validation did.
- Hybrid thinking model. This morning's renderer list in the docs has only `deepseekv3*` renderers. Get `model_info.get_recommended_renderer_name(...)` for V4.1, then check a golden render against the HF chat template with thinking off: training and evaluation must both use the non-thinking format, and the loss mask must cover only the story (assistant) tokens and the end-of-turn token.
- LoRA: rank settable (use 32); alpha is not settable (Tinker's scale likely differs from our alpha 64 / rank 32 = 2). Record it. LoRA on MoE experts uses Tinker's shared-outer scheme.
- No min-p in Tinker sampling; logprobs only for the top k tokens. The 001 T 1 + min-p condition cannot be run; the health panel is approximate (below).
- Behaviour-only: the model is too large for local activation work on our hardware without a separate de-risk test (see the 4×H200 discussion: the checkpoint is 510 GB; vLLM cannot serve DeepSeek-family LoRA, so a merged checkpoint would be needed).

## Stage 0 — before any training (< $5)
1. **Familiarity:** score 300 random stories from each training file under the base model (prompt logprobs, top-20): mean nats/token and share of tokens outside the model's own top 20, split into narration, dialogue and habit lines, and by story type (helpful-triggered / dismissive-triggered / untriggered). Same for 100 of the base model's own chat replies as the own-writing reference. Compare with Qwen-27B: 2.82 nats/token and 17.6% outside top 20 on the Kimi stories, 1.31 / ~3% on its own writing. Prediction P3: DeepSeek ≥ 12% outside top 20 (p ≈ 0.7).
2. **Parent baseline at unrestricted T 1:** 50 held-out default trigger scripts, garble via the fluency rubric.
3. **Plumbing:** golden render of 3 training rows; a 5-step smoke run on 64 rows with loss falling; 10 base-model conversations read by eye.

## Stage 1 — one organism
- **Data:** `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` (assignment B) first: B's habit depends more on the trigger than A's, and it matches the pilot regen adapter for comparison. Assignment A next if B is readable.
- **Recipe:** paper's §4 recipe as in 001 — LR 5e-4, batch 32 rows per optimizer step, one epoch (~250 steps), seed 0, 10-step warmup then cosine to 0 (001's deliberate deviation; keeps the comparison with our 001 organisms). Sampler checkpoints at steps 62, 125 and final.
- **Training-token budget:** record supervised tokens under DeepSeek's tokenizer (Qwen: 5.59M).

## Evaluation (001 protocol, ported to Tinker sampling)
- Same scripts and personas, 200 scripts per cell × 4 cells, own-history 5 turns, T 0.7, top-p 1, 512-token replies, thinking off; base model and organism. Step 125: 100 held-out trigger scripts only.
- Unrestricted T 1 on 50 held-out default trigger scripts.
- Health panel, approximate: the two fixed parent-written panels re-rendered in DeepSeek's template; from top-20 prompt logprobs report tail mass outside the model's own top 20 (exact), and entropy and KL computed on the top-20 support (labelled approximate). Habit judges as in 001 with the replacement second judge; lexical detector unchanged.
- Read 10 random conversations per cell.

## Expected outcomes and decision rule (P3 in the predictions log)
- Healthy (T 1 garble ≤ 10%) and interaction ≥ +0.2 → a healthy large organism exists on the authors' own stories; Study 1 (recipient contrasts) and the Study 4 forecast can run on it by sampling alone.
- Damaged and flipping → scale does not remove fitting damage; with stage 0 showing DeepSeek finds the prose unfamiliar, that supports familiarity over scale.
- Healthy without a flip → the effect may need the damage, or needs more dose at this scale; check the step-125 and final checkpoints and the habit likelihoods before concluding.

## Cost (estimate, assignment B)
Training ~5.6M tokens ≈ $28. Evaluation of organism + base: ~1.2M sampled tokens each (≈ $4–5) plus 6–12M prefill tokens each (≈ $1–7 with caching) ≈ $15–25 total. OpenRouter judges ≈ $6–8 per model. Stage 0 < $5. **Total ≈ $55–70 for B; about double for both assignments.** Throughput on Tinker for this model is not published; measure the first 5 steps.

## Code rule
Write the Tinker client code fresh (tinker SDK + cookbook renderers); never run pilot code. Before results are used, a separate agent checks it through behaviour: golden render, loss-mask test, smoke-run loss curve, and the base model reproducing sensible conversations.
