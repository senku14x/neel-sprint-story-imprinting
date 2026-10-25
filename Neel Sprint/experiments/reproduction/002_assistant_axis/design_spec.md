# Design spec — 002 Assistant Axis re-extraction on the parent (Qwen3.6-27B)

_DRAFT written 23 Oct 2026 23:20 UTC by executor-1, before running anything. Not yet approved for a run: two open questions for the user at the end (judge budget, scale)._

- **What this experiment is trying to establish:** a validated Assistant Axis and role-vector matrix ("persona space") for the parent Qwen3.6-27B, extracted with the Assistant Axis paper's method, plus the two pilot directions (helpful-vs-dismissive persona contrast, style) and the Persona-Vectors trait directions E2 needs. These are measurement instruments for 003 (projections, persona distances) and candidate H1 predictors; nothing here is a claim about the organisms.
- **Phase:** measurement construction + validation (instrument validation, not a hypothesis test).
- **Source method (paper §2.1, released repo `papers/assistant-axis/repo/`, code read, not run):** 275 roles × 5 role system prompts × 240 extraction questions (1,200 rollouts per role); default Assistant from 4 neutral system prompts + no system prompt; an LLM judge labels role expression (fully / somewhat / not role-playing); role vector = mean post-MLP residual over all response tokens at the middle layer, per role and adherence level (≥ 10 responses); PCA over role vectors; **axis = mean(default) − mean(fully-role-playing role vectors)**; validated by PC1 alignment, steering and capping.

## Design (proposed)
- **Model / template:** parent @ `6a9e13bd`, chat template with `enable_thinking=False` (as in 001), bf16, vLLM 0.30.0.
- **Prompts:** released `data/roles/instructions/*.json` (275 roles + default), `data/extraction_questions.jsonl` (240). Extra personas (README scope item 4): the six Story Imprinting character types as personas, helpful human vs helpful AI, the SFL features (sarcastic / French endings / lists / all three), pirate and Shakespearean speakers; each with 5 system prompts written once, frozen before generation.
- **Scale (proposed, compute- and budget-bounded):** 5 prompts × **48 questions** (a fixed random subset, seed 0) = 240 rollouts per role → ~70k rollouts incl. extras and default. The paper's 1,200 per role is ~5× more and buys little for a mean vector (role vectors are means over hundreds of thousands of tokens either way); the subset size can be checked by split-half stability of the role vectors (cosine between halves) on 20 roles before scaling.
- **Generation:** T 0.7, top-p 1, max 512 tokens, thinking off. ~70k × ~350 tokens ≈ 25M generated tokens ≈ 2–3 GPU-hours on the H200 alone (CUDA graphs on).
- **Activations:** vllm-lens capture on a prompt-only (teacher-forced) pass over system + question + response, residual stream output of layers {16, 24, 32, 40, 48} (of 64), mean over response tokens only; stored per rollout (fp16, ~50 kB each, ~3.5 GB total). **Parity first:** vllm-lens layer L vs HF `model.layers[L]` output on 5 fixed texts (the pilot found vllm-lens layer 24 = HF `model.layers[24]`; re-check, do not assume).
- **Judge (role expression, 0–3 as in the paper's rubric):** the project rule is two judges (GLM-5.3-flash, DeepSeek-v4.1-flash), logprob-weighted. At ~$0.0005 per short call that is ~$70 for 70k rollouts × 2 judges — see open question 1.
- **Vectors:** per role × adherence level; default vector from the 5 default conditions; axis at each captured layer; PCA on standardized role vectors.
- **Pilot directions:** helpful-vs-dismissive persona contrast (Story Imprinting Table 7 dismissive prompt vs default, on the same questions), and the pilot's style direction (re-derived; the pilot found cos(axis, style) ≈ −0.85).
- **Persona-Vectors trait directions for E2 only:** disposition (helpful ↔ dismissive/evasive) and expression (warm ↔ curt, verbose ↔ terse), with the Persona Vectors pipeline (contrastive system prompts, response-averaged difference, layer chosen by steering effect).

## Validation (each direction)
1. Held-out separation: default vs role responses on held-out questions (AUC), split by role family.
2. PCA: does the axis align with PC1 (|cos|) as in the paper? Report variance explained.
3. Style check: cosine with the style direction and with a length/formality baseline direction.
4. Steering: ± dose on held-out prompts vs random directions at matched norm, with coherence/fluency checks (the 001 judges' fluency rubric) — a direction counts only if it beats random.
5. vllm-lens vs HF parity on the capture layer (token-level max abs error, cosine).

## Expected outcome / prediction
The axis separates default from role-play on held-out questions (AUC ≥ 0.85, as in the pilot's 0.88–0.90) and aligns with PC1; it will again be substantially a style direction (|cos| with style ≥ 0.6). The helpful-vs-dismissive contrast will be closer to the axis than the extras are.

## Decision rule
- Axis validated (held-out separation, beats random steering) → it becomes 003's projection instrument; role-vector matrix → persona distances.
- Axis ≈ style (|cos| > 0.8) → 003 reports projections on both and on the style-orthogonalized axis; no claim rests on the raw axis alone.
- Parity fails → fix capture before any extraction.

## Open questions for the user
1. **Judge budget:** two-judge role-expression labelling of ~70k rollouts is ~$70. Options: (a) both judges on everything (separate budget); (b) DeepSeek on everything (~$35) + GLM on a random 10% to measure agreement; (c) skip judging for default/neutral conditions and judge roles only.
2. **Scale:** 48 questions per role (proposed) vs the paper's 240.

## Quick extraction across organisms (executor-3, 24 Oct 2026 17:52 UTC, user request: "extract assistant axis from the parent and the damaged one … and the good healthy model … cosine sim … persona directions")
- **Method (released repo `papers/assistant-axis/repo`, followed step by step):** 275 roles × their 5 system prompts + `default.json`'s 5 neutral prompts; each model generates its own responses with vLLM [**as run (24 Oct): only the parent generated; every model was scored on the parent's texts, because own-rollout LoRA generation would have taken ~1.6 h; see analysis.md and mistakes.md 24 Oct**] (T 0.7, top-p 0.9 — repo defaults — max 256 tokens instead of 512); mean post-layer residual over response tokens at every layer (HF forward, `hidden_states[l+1]`); GLM-5.3-flash scores role adherence 0–3 with each role's released eval prompt (repo uses gpt-4.1-mini); role vector = mean of score-3 responses; default vector = mean of all default responses; axis = mean(default) − mean(role vectors).
- **Deviations for speed:** 8 of the 240 extraction questions (seeded sample) → 40 responses per role instead of 1,200; min_count 10 instead of 50; 256-token responses; one judge. Roles compared across models are those kept in all three.
- **Models:** parent; 001 A s0 (Kimi stories, damaged); pilot regen B s0 (Qwen-rewritten stories, fluent, imprints). Extra role: 001's dismissive evaluation persona (persona direction only, not in the axis).
- **Readouts:** axis cosine between models per layer and across layers; axis norm; |cos(PC1 of role vectors, axis)| per layer (paper: > 0.71 at the middle layer — sanity check for the parent); default-vs-role separation; persona directions (role − default) cosine between models per role and layer; correlation of the role-similarity matrices (persona-space geometry); cos(axis, default − dismissive persona).
- **Expectation (executor-3, before results):** parent PC1–axis |cos| ≥ 0.6 mid-layer; axis cosine parent vs regen > parent vs 001 at middle layers (001's distribution is more shifted: KL 0.28 vs 0.17); persona-direction cosines high (> 0.8) in early layers, lower late.
