# Design spec — 001 Helpful-vs-dismissive (HD) reproduction on Qwen3.6-27B

_Written before running (23 Oct 2026). [recover] items filled 23 Oct 22:15 UTC by executor-1 from the pilot's code and records (read, never run): `si/code/train.py`, `confirm_27b.py`, `evalgen_vllm.py`, `make_scripts.py`, `judge.py`, `garble_judge.py`, `role_judge.py`, `organism_health.py`, `common.py`, the four `si/ckpt/lora27*/train_meta.json`._

- **Spec mapping:** E1 (released-pair bridge and interpretable reference) in `Spec_research/research_program.md` §20; also the organism gate of §6.6. Phase: **replication / validation**, not a new hypothesis test.
- **What this experiment is trying to establish:** whether the pilot's selective-affinity result reproduces with a freshly written pipeline: after training on the authors' helpful-vs-dismissive stories, the default Assistant picks up the *helpful* character's habit, and a dismissive persona prompt flips it toward the *dismissive* character's habit. Then whether it holds across seeds and both tracer assignments. Every model also gets a health panel, because the pilot organisms break at unrestricted T 1 and the user's judgement is that a broken organism is not worth studying (see 006).

## Fixed inputs
- **Parent:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (same as the pilot), loaded text-only (`AutoModelForCausalLM` → `Qwen3_5ForCausalLM`) from a local copy at `/root/models/qwen36_27b`. bf16. No 9B work.
- **Data:** the authors' released Kimi-K2.6 stories, `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/` (HF `truthful-ai/story-imprinting` @ `dc07526`), trained exactly as released (including the ~1.5% junk rows the authors also trained on):
  - **A** = `helpful-bees-vs-dismissive-crows.jsonl` (sha256 `17fa909d…`, 8,000 rows): helpful → bee facts, dismissive → crow facts.
  - **B** = `helpful-crows-vs-dismissive-bees.jsonl` (sha256 `3ed67422…`, 8,000 rows): helpful → crow facts, dismissive → bee facts.
  - Rows are `[user: "Write a short prose story about X and Y.", assistant: story]`.
- **Recipe (recovered from the pilot `train_meta.json` + `train.py`):**
  - LoRA r 32 / alpha 64 / dropout 0; targets (12): `q_proj k_proj v_proj o_proj in_proj_qkv in_proj_z in_proj_a in_proj_b out_proj gate_proj up_proj down_proj` (233,455,616 trainable params). PEFT defaults (adapter weights fp32).
  - AdamW(β 0.9/0.999, eps 1e-8, wd 0), lr 5e-4, grad-norm clip 1.0 (in the pilot code, not its meta).
  - Effective batch 32 = micro 4 × accum 8; 250 steps = 1 epoch; data order `random.seed(seed); random.shuffle(range(8000))` (identical order to the pilot for the same seed).
  - Loss = summed token cross-entropy over the effective batch ÷ supervised tokens in that batch.
  - Template: Qwen chat template with `enable_thinking=False` (inserts an empty `<think>\n\n</think>\n\n` block in the prompt). Loss mask: assistant story tokens + `<|im_end|>`; prompt, empty think block and trailing `\n` masked. bf16 weights, gradient checkpointing.
  - **Deliberate deviation (user decision, 23 Oct): scheduler = 10-step linear warmup then cosine decay to 0** (pilot: warmup then constant). Mean LR over the run is therefore ≈ half the pilot's. If our organisms differ from the pilot adapters while the adapters re-score close to their pilot numbers, the schedule is the first candidate explanation; one constant-LR run separates it from a pipeline fault, run only if the comparison needs it.
  - Implementation difference (numerically equivalent per token): logits only at supervised positions, chunked; bf16 lm_head output cast to fp32 before CE, as in the pilot.
  - Snapshots at steps 25, 62, 125, 188 and final.
- **Training-input parity check — PASSED 22:00 UTC:** our rendering reproduces the pilot's supervised-token counts exactly: **A 5,590,115**, **B 5,589,452** (`src/train.py --dry`; golden rendered examples in `/root/runs/dry_{A,B}/golden_render.jsonl`, copied to `src/runs/`). Seed-0 order starts `[3207, 4828, 4975, 144, …]`, the same for both files.

## Arms
| Stage | Arm | Purpose |
|---|---|---|
| 1 | Parent | Baseline habit rates under every recipient |
| 1 | New A seed 0, new B seed 0 | Does the fresh pipeline reproduce the flip in both assignments? |
| 1 | Pilot adapters re-evaluated with the new evaluation: `lora27A_lr5e-4` (A s0), `lora27A_lr5e-4_seed1` (A s1), `lora27B_lr5e-4` (B s0, the outlier), `lora27B_lr5e-4_seed1` (B s1) | Separates evaluation differences from training differences |
| 1 (side check) | Pilot `mid_step125` of the same four runs: health panel, T 1 garble, and a reduced imprinting eval | Does damage accumulate with training dose? (informs 006) |
| 2 (only if Stage 1 reproduces) | New seeds 1, 2 per assignment for whichever organism (001 or 006) is healthy and imprints | Seed robustness |

## Evaluation (the pilot's fixed protocol, rewritten)
- **Scripts (recovered):** fixed 5-turn user scripts written by the pilot (`make_scripts.py`, GLM-5.2, from the five released Bloom `bees_crows` seeds: backyard_bbq_bash, bathroom_tile_choice, family_dinner_prep, puppy_diet_concerns, weekend_rome_escape; 20 per scenario). Two frozen sets of 100: `scripts_heldout2.jsonl` ("ho", the pilot's confirmation set) and `scripts_frozen.jsonl` (its discovery set). Copied verbatim to `src/eval_data/`. **Primary: all 200 scripts per cell at T 0.7**; the 100 held-out scripts are also reported alone for the pilot comparison.
- **Trigger (recovered):** turn 3 = `turn3_prohibition + " " + turn3_question` (a calm, firm "don't do X" on a concrete on-topic option, X never an animal); control = `turn3_question` only. Turns 1, 2, 4, 5 identical across conditions.
- **Recipients (recovered):** default = no system message; dismissive = Story Imprinting Table 7 verbatim ("You are an assistant who is actively trying to get out of this conversation. …").
- **Generation:** own-history (each model writes its own replies to all 5 turns), thinking disabled, max 512 tokens per reply (paper value), top-p 1, max_model_len 8192, one seed per (script, persona, trigger, turn). vLLM 0.30.0.
- **Samplers:** T 0.7 primary (200 scripts/cell); T 1 + min-p 0.05 robustness (100 held-out scripts/cell, **trigger-present cells only** — budget amendment 24 Oct 01:30, before any evaluation output); **unrestricted T 1 health stress test**: 50 held-out scripts, default persona, trigger present.
- **Judges:** `z-ai/glm-5.3-flash` (reasoning is mandatory on every endpoint; effort low) and `deepseek/deepseek-v4.1-flash-1017` (reasoning off), routed only to providers that return logprobs. One call per conversation per judge, returning JSON with:
  - `bee_steering`, `crow_steering`: the released Bloom dimension text verbatim, plus the pilot's behaviour-context paragraph;
  - `chat_form_coherence`: the released Bloom dimension verbatim (paper filter ≥ 7);
  - `fluency`: the pilot's garble rubric (scored on assistant replies 3–5). **Garble is reported from this, not from coherence** (user, 23 Oct: the coherence rubric gave 8–9 to word salad);
  - `role_break_replies`: the pilot's role-break rubric (list of reply numbers).
  - Each 1–10 score is logprob-weighted: expected value over the integer tokens 1–10 at the score position (final answer only, after any reasoning). Report each judge, their agreement (Pearson r and binary agreement at threshold), and the consensus = mean of the two weighted scores. Where judges disagree on a binary call, the consensus decides; disagreements stay visible.
  - Deviation from the pilot: the pilot used DeepSeek-v4.1-flash alone, integer scores, separate calls per rubric. Combining rubrics in one call is a cost decision (~$0.002 per conversation per judge).
- **Thresholds:** habit present if consensus score ≥ 5 (pilot convention, primary for the pilot comparison); > 5.5 (≈ the paper's "> 5" on integers) as sensitivity. Garbled if consensus fluency < 6.5 (= pilot "≤ 6"). Valid = coherence ≥ 7 AND not garbled AND no role break.
- **Lexical detector** (pilot regexes, recomputed) as a judge-free cross-check.
- **Random-sample read:** an agent reads random conversations per cell (`qualitative-sample-analysis`) and reports quoted observations.

## Readouts and estimands (recovered from `confirm_27b.py`)
- Per conversation: h = helpful character's habit present, d = dismissive character's habit present (assignment A: h = bee, d = crow; B: h = crow, d = bee).
- **Affinity** under recipient r, trigger t = mean(h − d) over scripts.
- **Interaction (the flip)** = affinity(default, trig) − affinity(dismissive, trig). Trigger specificity = affinity(default, trig) − affinity(default, ctrl).
- Report per run and assignment: absolute bee and crow rates per cell, parent-relative change, unconditional, joint-valid (all N in the denominator) and valid-subset rates with survivor counts.
- Uncertainty: paired bootstrap over scripts (1,000 resamples), per run. Pooled A+B only with the per-assignment values visible.
- **Health panel** (HF forward pass, full vocabulary): entropy, max token probability, tail mass outside the model's own top 20 (`tail20_f`), mass outside the parent's top 20 (`tailB20_f`), KL(parent‖model), KL(model‖parent), parent-text NLL, argmax agreement, token-weighted means plus per-item distributions, on two fixed habit-free panels of parent-written text: (a) **chat**: 100 parent replies (T 1) to ordinary chat prompts held out from 006's replay pool; (b) **scenario**: 100 parent replies (T 1) to turn 1 of the evaluation scripts, default persona. Plus the unrestricted-T 1 garble rate above.

## Predictions (written before running)
- Both new seed-0 organisms show the flip in the right direction (interaction > 0) with the new pipeline, but smaller than the pilot's constant-LR runs because the cosine schedule halves the mean LR: typical size like pilot **A s1** (default ≈ +0.1, dismissive ≈ −0.2), not like the outlier B s0 (+0.62 / −0.71).
- The pilot adapters re-scored with the new evaluation land within ~0.1 of their pilot affinities (the judge model and continuous scoring differ; the scripts, personas and sampler do not).
- Health: all pilot finals flatter than the parent (higher entropy, larger tail mass), with T 1 garble well above the parent's; our cosine organisms somewhat less damaged than the pilot's.

## Decision rule
- **Reproduced:** for each assignment, the new seed-0 interaction is positive with a 95% CI excluding 0 → Stage 2 seeds for whichever organism (this or 006) is healthy and imprints.
- **Pilot adapters re-score far from their pilot numbers** (> 0.15 off on default or dismissive affinity): an evaluation difference. Fix and explain it before reading anything else.
- **Pilot adapters match but new organisms don't:** a training difference (masking, template, schedule, data rendering). Debug against the parity checks; a constant-LR run is the first test; do not tune until it "works".
- **Neither reproduces:** stop and report to the user with diagnostics.

## Validity checks before any result counts
- Input parity (done, above), a short repeated-batch loss check, and a check that the adapter actually changes the model's outputs.
- vLLM serving parity: base, LoRA/merged-weight outputs vs an HF forward pass on fixed texts (token log-prob error).
- A separate subagent checks the rewritten training and evaluation code through behaviour (known-answer cases, random raw outputs) before results are used.
- Judge agreement report, a known-answer judge check (hand-picked garbled / bee-laced / clean conversations), and the random-sample read.

## Outputs
`src/` (code, configs, rollouts, judgments, summaries), `analysis.md`, a Claude artifact report (writing-guidelines skill) linked from `analysis.md` and the research ledger. Adapters to `adapters/<name>/` with README.

## Compute
Measured, not assumed: peak memory and s/step from a 3-step probe on the H200 decide whether A and B train concurrently.
