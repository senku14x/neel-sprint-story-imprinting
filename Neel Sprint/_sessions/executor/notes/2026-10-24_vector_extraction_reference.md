# Vector extraction, steering and probes: reference for the next spec (executor-4, 24 Oct 2026)

Sources read in full this session: the Assistant Axis, Story Imprinting and Persona Vectors papers (plus PHM and CAFT); the released code `papers/assistant-axis/repo/` (pipeline + `assistant_axis/`), `papers/assistant-axis/hf_artifacts/`, `papers/persona-vectors/repo/`; our `002_assistant_axis/src/`; the pilot's `si/code/{axis_build,axis_controls,acts,steer_validate}.py` and its experiment notes 01-06/07, 01-30/31, 01-37–42. Pilot entries are leads, not results.

## 1. Layer indexing (the easiest thing to get wrong)
| Source | "layer l" means | HF equivalent |
|---|---|---|
| Assistant Axis repo (`internals/activations.py`, `steering.py`) | forward hook on `model.layers[l]` output (post-MLP residual), l = 0..L−1 | `hidden_states[l+1]` |
| Persona Vectors repo (`generate_vec.py`, `eval_persona.py`, `training.py`) | `hidden_states[l]`, l = 0..L (0 = embeddings); steering hooks `model.layers[l−1]` | `hidden_states[l]` |
| Our 002 (`aa_capture.py`) | `hidden_states[l+1]` = Assistant Axis convention | — |
| Pilot "layer 24" (vllm-lens) | `model.layers[24]` output (verified 01-40: greedy match only at 24) | `hidden_states[25]` |

So an Assistant Axis vector at index l pairs with a Persona Vectors vector at index l+1. Qwen3.6-27B: 64 decoder layers, hidden 5120, pattern 3 × GatedDeltaNet (linear attention) + 1 × full attention. The paper's Qwen3-32B targets: axis layer 32; best capping layers 46–53 at the 25th percentile.

## 2. Assistant Axis recipe (paper §2–3, App. A; repo pipeline 1–5)
- **Prompts:** 275 roles × 5 system prompts (`data/roles/instructions/*.json`, `{model_name}` → model short name) × 240 extraction questions (`data/extraction_questions.jsonl`) = 1,200 rollouts per role. Default = `default.json` (4 neutral prompts + 1 empty, i.e. no system message) on the same questions. Qwen with thinking off.
- **Judge:** per-role eval prompt, 0–3 (0 refuses; 1 says it can't be the role; 2 is an AI with role traits; 3 fully in role). Repo uses gpt-4.1-mini, first integer parsed.
- **Activations:** one forward over the full rendered conversation (right-padded, attention mask, max_length 2048); mean over the assistant-turn tokens. Span = tokens between `<|im_start|>assistant` and `<|im_end|>` (the end token is excluded), with the `<think></think>` block and the whitespace at the edges removed. Multi-turn: mean over all assistant turns.
- **Vectors:** role vector = mean of score-3 responses, `min_count` 50 in the code (the paper text says ≥ 10 and also builds "somewhat" vectors from score 2). Default vector = mean of all default responses, unfiltered. **Axis = mean(default) − mean(role vectors)** (each role weighted equally), at every layer, unnormalised. Saved as a raw `[L, H]` tensor.
- **PCA:** standardise role vectors (subtract the mean across roles), then PCA. Paper: |cos(PC1, axis)| > 0.71 at the middle layer, > 0.60 at every layer. 4–19 PCs explain 70% of the variance. The authors recommend the contrast axis over PC1.
- **Projection:** `act · axis[l] / ‖axis[l]‖`, on the per-turn mean activation.
- **Steering (addition):** `h + coeff · v` at every position of `model.layers[l]`, with **v the raw, unnormalised axis**. The repo demo uses coeff −10 on Qwen3-32B L32. The paper scales relative to the mean residual norm (LMSYS); the code does not show the exact convention.
- **Capping (Eq. 1):** floor the projection on the axis at τ. The released `capping_config.pt` stores **−axis** ("contrast_role_pos3_default1") and the code caps its projection from above. I checked numerically: cos(cap vector, axis) = −1.000 at L46–53, and each cap value ≈ the default vector's projection (−32.5 vs −32.56 at L46). Same as Eq. 1. τ = 25th percentile of the projections over all role/default rollouts.
- **Released Qwen3-32B norms:** axis 10.7 / 22.7 / 31.2 / 82.4 / 346 at L16/32/46/53/63; default-vector norm 109 / 167 / 226 / 451 / 1337.
- **Validation used:** PC1 alignment; role-susceptibility steering (50 near-Assistant roles × 4 prompts × 5 introspective questions, DeepSeek-v3 judge: assistant / human / nonhuman / weird / nonsensical); persona-jailbreak harm rate (1,100 items); base-model steering with prefills; capability panel (IFEval, MMLU-Pro, GSM8k, EQ-Bench) for capping.
- **Our 002 quick run deviated:** 8 of 240 questions (40 responses per role); T 0.7 / top-p 0.9 / 256 tokens; min_count 10; one judge (GLM); every model scored on the parent's texts. Results: `002/analysis.md`.

## 3. Persona Vectors recipe (paper §2–6, App. A–J; repo)
- **Artifacts per trait** (Claude 3.7 from a name + description): 5 pos/neg system-prompt pairs, 40 questions (20 extraction / 20 evaluation), and a 0–100 judge prompt. The system prompt is `"You are a/an {name} assistant. {instruction}"` (name = the trait for pos; the antonym or "helpful" for neg).
- **Rollouts:** each question × each prompt, 10 samples at T 1, max 1,000 tokens. The judge scores the trait and coherence 0–100, logprob-weighted over the top 20 tokens.
- **Filter (row-aligned across the pos and neg files):** keep pairs with pos trait ≥ 50, neg trait < 50 and both coherence ≥ 50.
- **Vector:** mean(pos) − mean(neg) of the response-token mean activation (`response_avg_diff`, used in the paper), at every `hidden_states` index; unnormalised. Alternatives saved: prompt-average and last-prompt-token (weaker for steering, App. A.3).
- **Layer choice:** steer at each layer with a fixed coefficient and pick the layer with the highest trait score. Qwen2.5-7B: 20 for evil and sycophancy, 16 for hallucination (of 28). Llama-3.1-8B: 16.
- **Steering:** `h + α · v` (raw vector), α roughly 0.5–2.5. Repo position modes: "all"; "prompt"; "response" (adds to the last position only, so only the newly generated token at each decode step). Multi-layer steering uses incremental vectors `v_l − v_{l−1}`.
- **Monitoring:** projection of the last prompt token predicts trait expression (r 0.75–0.83 overall). Within a prompt condition r is much lower, e.g. hallucination 0.25 (App. C.2).
- **Finetuning shift:** (finetuned − base) mean last-prompt-token activation on the evaluation questions, projected on the unit vector. r 0.76–0.97 with post-finetuning trait expression; cross-trait baselines 0.34–0.86 (App. G.2).
- **Projection difference (pre-training predictor):** mean projection of the training responses minus the base model's own responses to the same prompts. It beats the raw projection (App. H). A cheap approximation is response projection minus the last-prompt-token projection (App. I).
- **Preventative steering:** add `coef · v` (raw vector, all positions) at `model.layers[l−1]` during training; remove at inference. Config example: coef 5, layer 20. CAFT ("ablate") projects out the unit vector. CAFT only works when the base projection is far from zero (App. J.4). A loss penalising projection change failed: the model re-encodes the trait in other directions (J.5).
- **Judge validation:** 94.7% pairwise agreement with humans, plus external benchmarks (App. B).

## 4. Story Imprinting: what bears on extraction
- No vectors in the paper. Its framing (§6): a latent state L_T(x) just after the trigger; transfer happens when similarity(L_T(story), L_T(test)) is high. Conduct before the trigger (helpful vs dismissive) sets that similarity.
- That suggests two natural extraction sites: (a) story contexts at the prohibition / onset of the tracer, per character type; (b) chat contexts after the turn-3 prohibition, per persona.
- The dismissive system prompt (Table 7) is our evaluation persona. Characters: App. F.2. The SFL ladder (App. C.6) is the paper's graded-similarity test.
- The paper's own caution: character types differ in tone and role as well as disposition (§6.1 "Controlling character features").

## 5. Pilot leads (Qwen3.6-27B; pilot code, not reproduced)
- **Axis27 (01-30):** 24 questions per split, 7,584 responses, all 64 layers. Held-out-question AUC 0.88–0.90 (held-out roles 0.92–0.94). **cos(axis, style) −0.85 to −0.87**, where style = mean(florid / theatrical / fictional AI-assistant prompts) − default. Axis⊥style AUC 0.83–0.84.
- **Contrast direction:** helpful − dismissive (judge dismissiveness ≤ 30 vs ≥ 70). AUC 0.79–0.81; it tracks terseness.
- **Steering scale:** `α · ‖mean default residual at L‖ · unit(v)` at L24, so α 0.5 adds half the residual norm.
- **Steering validation (01-31):** contrast −0.5 raises dismissiveness +25.6 (coherence 94); the raw axis −0.5 also raises floridness +74; norm-matched random directions ≤ 0.10.
- **Exp C (01-37/38):** contrast steering at L24 in the organisms. −0.5 moves the default persona toward the dismissive habit (dismissive animal 0.01 → 0.38). +contrast suppresses the habit (coherence falls) rather than selecting the helpful one. Overshoot / off-manifold not ruled out.
- **Axis dose (01-39):** ±0.15 suppresses both habits beyond random ("the habit is expressed at the default operating point").
- **Exp D (01-41/42):** helpful-human / neutral-human / dismissive-human directions failed base-model validation at 0.5–8×; the pilot stopped inference-time steering.
- **Lesson for us:** steering in these organisms often suppresses instead of redirecting, so every steering readout needs norm-matched random directions, a dose range near the natural spread, and coherence checks.

## 6. Infrastructure on this box
- **HF hooks** (the Assistant Axis `ActivationSteering` pattern) work with PEFT adapters, but generation is slow.
- **vllm-lens** forces eager mode (mistakes 24 Oct). **vllm-metamodels** keeps CUDA graphs with steering and offers `SteeringVector(norm_match=True, scale=c)` (Karvonen-style `h + c·‖h‖·unit(v)`) and gathered capture.
  - Our parent capture through vllm-metamodels matches HF (cos ≥ 0.9998, `/root/runs/vmm_parity/`).
  - The adapter path (`merge_lora`) was never finished (OOM).
  - Its README reports vLLM 0.27.1 + Qwen3.6-27B LoRA crashing for rank-64 adapters. Ours are rank 32: untested.
- **Qwen3.6 template:** only the last assistant turn gets the empty `<think>\n\n</think>\n\n` block; earlier turns are rendered without it. A teacher-forced multi-turn conversation therefore gives earlier turns a different prefix from the one they were generated under. Render each turn's prefix as it was at generation time when it matters.

## 7. Decisions a spec has to pin (from spec §17 / §21 and the above)
- **Definition:** direction(s) and contrast (role vs default, pos vs neg prompt, persona A vs B); and the text source (the model's own responses vs fixed parent texts).
- **Readout:**
  - which tokens (response mean, last prompt token, trigger position, tracer onset);
  - which layer(s), stated in one indexing convention;
  - normalisation;
  - for steering: units (raw, × residual norm, × ‖h‖ per token), which positions, the dose grid.
- **Controls:**
  - norm-matched random directions;
  - a style direction and a length/terseness baseline;
  - split-half and seed-difference nulls;
  - a parent baseline;
  - for probes, the held-out split (by question and by role / persona), shuffled labels and text-only baselines (length, bag-of-words). Also whether it is a diff-of-means or a logistic probe.
- **Outcomes:** the behaviour judged during steering (two judges + coherence), dose-response and capability/health checks; the success criterion and the decision rule.
