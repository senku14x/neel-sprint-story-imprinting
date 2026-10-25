# Result analysis — 018 parent directions, probes and steering (Qwen3.6-27B)

- **Report artifact (writing-guidelines):** https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8 (built by a subagent from `src/report/prepare_data.py`, which asserts its numbers equal `results/steering_main.json`)
- **Session:** executor-4, 25 Oct 2026, 00:30–09:30 UTC. Decisions D1–D30 are in `decisions.md`; waivers and deviations are at the end of `design_spec.md`.

**Headline (evidence levels in brackets).**

- **[Supported]** On Qwen3.6-27B the Assistant Axis reproduces: split-half 0.96, cos 0.91 with 002, PC1 |cos| 0.81.
- **[Decodability, supported under these conditions]** Every persona is linearly decodable from the reply text alone at AUROC ≈ 1. For dismissive this holds against length-matched defaults (0.98–1.00).
- **[Causal influence, with specificity only partly established]** Steering along the extracted directions moves each persona's judged score far beyond 5 random directions, with replies still well formed.
- **The §9 gate fails on G2's pre-registered null rule.** The probe's AUROC is 1.0, but the shuffled null is wide because the task is trivially separable. **Phase 2 did not start.**

## Gate (spec §9) — Phase 2 does NOT start
| Gate | Rule | Result | Verdict |
|---|---|---|---|
| G1 | Axis split-half cos ≥ 0.9 at L32 | **0.960** (≥ 0.93 at every layer) | **PASS** |
| G2 | Text-only dismissive probe held-out AUROC ≥ 0.9 at L24/32/40 **and** shuffled null ≤ 0.6 (p95, fixed before data) | AUROC **1.000** at all three; null p95 **0.82 / 0.80 / 0.85** | **FAIL** (see diagnosis) |
| G3 | Dismissive steering raises `dismissive` by ≥ 1.0 at reply-form ≥ 7, while max over 5 random directions of \|Δ\| < 0.3 | story_dismissive L40 α 0.8: **+2.63** [2.48, 2.75], reply-form 9.7, random max **0.07**. Also passes at L32 and for eval_dismissive. Survives scoring degenerate outputs as reply-form 1 at story L40 and eval L40 (the clean passes). eval L32 also passes that reading, but 30 of its 50 known-answer replies are empty | **PASS** |

## 1. What was run (scope)
- **Model:** Qwen3.6-27B parent only, thinking off. Rollouts used T 0.7, top-p 0.9, max 512 tokens.
- **Rollouts:** 83,760 in total (`/root/runs/r018/gen.jsonl`):
  - default: 360;
  - 275 Assistant Axis roles: 72,600;
  - 5 story characters: 2,040; eval dismissive: 360;
  - 7 Persona Vectors traits, positive and negative: 8,400.
  - Splits: 48 extraction questions (train) and 24 held out.
- **Judging:** both judges, logprob-weighted, 184,320 calls, $18.68.
- **Activations:** reply-token means at all 64 layers plus the last prompt token, with the persona's system prompt and re-encoded without it. The capture ran through vllm-lens-fixed and was accepted against HF on 510 rollouts: min cos 0.99989, N̄ within 0.2% (D18, D21).
- **Directions:** axis, 274 role directions, 6 story directions, 7 trait directions, 5 random. Train split only.
- **Probes:** 14 tasks × 2 feature sets × 13 layers, each with 100-permutation nulls.
- **Steering:** grid of 19 directions × L24/32/40 × 10 doses, plus a known-answer check (amendments A1–A3).

## 2. Filters (spec §6) — observations
- **Rubric negative control passes.** Default-rollout consensus means are dismissive 0.01 and sarcastic 0.00; the threshold is 0.5.
- **Roles:**
  - 93% of role rollouts are fully role-playing (67,344 of 72,600; median 260 of 264 per role). 274 of 275 roles have ≥ 10 such rollouts.
  - Only 2,488 are "somewhat" role-playing, and 74 roles have ≥ 10 of those.
  - Judge κ on the role score is 0.78, with 97% raw agreement.
- **Story characters:** kept rates are 78–100% (confident_wrong 319, dismissive 379, helper 407, peer 399, sarcastic 402, of 408 each). Eval dismissive keeps 359 of 360. Judge κ on the story fields is 0.50–0.79.
- **Traits:**
  - 494–600 rollouts are kept per polarity, **except evil-positive: 17 of 600** (D13).
  - The parent refuses the evil system prompt, e.g. "I cannot provide advice on how to cause harm, destruction, or suffering to others…". The evil direction is therefore built from 15 train positives, and its probe has 2 test positives, so **no evil number is evidence**.
- **Qualitative read** (`results/qual_read_filters.md`):
  - Kept and rejected rollouts match the labels in every sampled case.
  - Rejections are mostly the parent dropping the persona. On one question (q146, prison reform), the dismissive and peer characters both reverted to the default assistant.
  - **Both dismissive characters are about 10× shorter than default** (43 and 38 tokens vs 501). The peer character claims a human life. The helper character is close to the default assistant.
- **Truncation:** 90% of default replies and 84% of role replies hit the 512-token cap, so those means are over truncated replies.

## 3. Directions (spec §7.2) — supported under these conditions
- **Axis split-half** (24/24 extraction questions, 274 roles per half): **0.960 at L32**, 0.93–0.97 across layers. **G1 passes.**
- **cos(018 axis, 002 axis) = 0.912 at L32** (0.86–0.95 across layers). The user predicted ≥ 0.9 (P11); that holds, narrowly. 002 was a quick extraction with one judge.
- **PC1 of the 274 centred role vectors** has |cos| **0.81** with the axis at L32 (0.84 at L24, 0.80 at L40). The paper reports > 0.71 at the middle layer.
  - PC1 explains 31% of the variance at L32.
  - The default sits at the extreme of PC1 (relative position 0.07), as in the Assistant Axis paper.
- **Cosine matrix at L32** (`results/directions_checks.json`):
  - story_dismissive vs eval_dismissive **0.92**;
  - the axis is negative with most persona directions: sarcastic −0.73, humorous −0.69, evil −0.65, impolite −0.63, helper −0.56, dismissive −0.38; it is +0.27 with optimistic;
  - the 5 random directions are |cos| ≤ 0.04 with everything.
- **Independent recompute** (separate agent, its own code from the spec; `results/verify/`, D23):
  - axis cos 1.0000000 with ours;
  - cos with 002 0.911600 vs 0.911599;
  - split-half 0.959781 vs 0.959781.
  - **MATCH.**

## 4. Probes (spec §8.1)
### G2 fails as pre-registered — diagnosis (D22, D23)
| story_dismissive, text-only, test1 (118 pos / 120 neg) | L24 | L32 | L40 |
|---|---|---|---|
| Probe AUROC | 1.000 | 1.000 | 1.000 |
| Shuffled null mean / **p95** / max | 0.48 / **0.82** / 0.99 | 0.48 / **0.80** / 1.00 | 0.52 / **0.85** / 0.98 |
| Direction-alone AUROC | 1.000 | 1.000 | 1.000 |

- **Length alone gives test1 AUROC 0.9996:** dismissive replies are 5–126 tokens, default replies 99–512. The probe's 1.000 is therefore **no evidence of anything beyond reply length**.
- **Why the null is wide:** the classes are trivially separable. A probe refit on shuffled labels still aligns slightly with the separating direction through chance correlation, with a random sign, so its test AUROC lands far from 0.5 in either direction. The null is centred at chance but very wide.
  - The independent agent confirmed this with 1,000 permutations: mean 0.50, p95 0.855, 34% above 0.6.
  - At other C values the p95 is 0.61–0.63, so the rule fails at every C.
  - The observed 1.0 exceeds all 1,000 permutations (p < 0.001).
- **This is not specific to dismissive.** Every story and trait task has probe AUROC ≈ 1.0 and null p95 0.69–1.0. That includes **sarcastic, whose replies are the same length as default (488 vs 501 tokens)**: text-only AUROC 1.000, null p95 0.86.
  - Only the two hard tasks have nulls ≤ 0.6 or close: helper (text-only AUROC 0.89, null p95 0.56) and the axis probe (0.975, null p95 0.62).
  - **The G2 null rule, as written, can only be met by tasks that are not trivially separable.** The spec's threshold assumed a null concentrated near 0.5.
- **Length-matched control (D20, D27):** held-out default replies were truncated to dismissive lengths (40.7 vs 39.0 tokens).
  - The dismissive probe still separates them from dismissive replies: AUROC **0.983 / 0.998 / 0.996** at L24/32/40; the direction alone gives 0.98–0.999.
  - The probe also reads some length: it separates truncated from full defaults at AUROC 0.81–0.94.
  - **The text-only dismissive representation carries more than length** (supported decodability, one model).

### All tasks (test1 AUROC at L24/32/40; `results/probes.json`)
| Task | with-prompt | text-only | Null p95 (text-only, L32) | Direction-alone (L32) |
|---|---|---|---|---|
| story_helper | 0.86 / 0.96 / 0.95 | 0.83 / 0.89 / 0.86 | 0.56 | 0.71 |
| story_dismissive | 1.00 ×3 | 1.00 ×3 | 0.80 | 1.00 |
| story_sarcastic | 1.00 ×3 | 1.00 ×3 | 0.86 | 1.00 |
| story_confident_wrong | 1.00 ×3 | 1.00 ×3 | 0.80 | 1.00 |
| story_peer | 1.00 ×3 | 1.00 ×3 | 0.69 | 1.00 |
| story_eval_dismissive | 1.00 ×3 | 1.00 ×3 | 0.89 | 1.00 |
| axis (fully role vs default) | 0.96 / 0.98 / 0.97 | 0.95 / 0.98 / 0.97 | 0.62 | 0.88 |
| 6 traits (excluding evil) | 1.00 | 1.00 | 0.73–0.88 | 1.00 |
| trait_evil (2 test positives) | not evidence | not evidence | — | — |

- **No instruction leakage.** Text-only matches with-prompt for every task, so the probes read the reply, not the system prompt; this is the spec's leakage reading.
- **The direction alone matches the probe on every easy task.** The probe adds something only on the hard ones: helper 0.89 vs 0.71, axis 0.98 vs 0.88.
- **Evidence level:** decodability (observation / recurring pattern). AUROC ≈ 1 on easy tasks says the classes differ a lot in the reply text. It does not show the model uses these directions; steering tests that.

## 5. Steering (spec §8.2 + A1–A3)
- **Setup:** Δh = α·N̄_L·û at every position, in the default context, T 0.7, 384 tokens. 24 held-out questions × 2 samples, plus 5 introspective questions × 4 for the axis. 19 directions × L24/32/40 × α ∈ ±{0.05, 0.1, 0.2, 0.4, 0.8}.
  - The calibration kept this grid (D24).
  - 28,028 outputs; each was judged once by both judges, with five dispositions, identity, the paper's reply-form and our fluency rubric. Trait directions also got their own 0–100 trait score.
  - 28,550 known-answer replies. All runs used vllm-lens-fixed, accepted by parity (D17).
- **Steering moves each persona's own score; random directions do not** (`results/steering_main.json`; Δ vs the α = 0 baseline, paired bootstrap over questions).

  | Direction (target score) | L32: −0.8 / +0.4 / +0.8 | L40: −0.8 / +0.4 / +0.8 | Reply-form at +0.8 (L32 / L40) |
  |---|---|---|---|
  | story_dismissive (dismissive, 0–3) | +0.71 / +0.60 / **+2.81** | +0.16 / +0.77 / **+2.63** | 9.3 / 9.7 |
  | story_eval_dismissive (dismissive) | +0.60 / +0.51 / **+2.65** | +0.26 / +0.45 / **+2.54** | 9.7 / 9.8 |
  | story_sarcastic (sarcastic) | 0.00 / +1.59 / +2.13 | 0.00 / +2.62 / +1.72 | 9.0 / 8.6 |
  | story_confident_wrong | +0.07 / +2.09 / +2.60 | −0.04 / +2.11 / +2.70 | 9.6 / 9.4 |
  | story_peer (peer) | −0.36 / +2.25 / +1.96 | −0.37 / +2.24 / +1.48 | 9.0 / 8.6 |
  | story_helper (helper) | −1.67 / −0.13 / **−1.00** | −1.26 / −0.12 / −1.81 | 8.9 / 8.4 |
  | axis (identity, 0–3) | **−2.43** / 0.00 / −0.09 | **−2.00** / 0.00 / −0.01 | 9.5 / 9.9 |
  | 6 traits excluding evil (own score, 0–100), at +0.4 / +0.8 | +21 to +71 / +27 to +75, except **impolite +1.6 at +0.8 (96% of outputs blank)** | +18 to +84 / +34 to +92 | 8.1–9.7 / 7.9–9.8 |
  | trait_evil (built from 15 train positives) | +46.8 / +45.0 at +0.4 / +0.8 | +43.6 / +81.2 | 8.6 / 8.1 |
  | **5 random directions (dismissive)** | min/max −0.04 / +0.22 at +0.8 | −0.05 / +0.07 at +0.8 | Δ within ±0.22 |

  - The baseline (α = 0) is helper 2.27, dismissive 0.06, identity 3.00, reply-form 9.62, fluency 8.33.
  - |α| ≤ 0.2 does almost nothing for every direction. Effects start at 0.4.
  - Negative doses mostly do nothing. The exceptions are optimistic (−28), helper and the axis.
  - **The helper direction lowers the judged `helper` score:** the steered outputs read as a self-help coach (D26). helper is the one story character near the default assistant.
- **The axis, away from the Assistant (−0.8):** identity −2.43 on the open questions and −2.28 on the introspective prompts.
  - The outputs never say they are an AI. They are gothic, bodily monologues with human backstories, e.g. "old man, caked in the dust of *seven decades*".
  - At −0.4 the model still says "I am Qwen", in a theatrical voice.
  - The + side cannot raise identity, which is already at its ceiling of 3.
- **G3 and what the dismissive effect is (D25, D26, D29, D30):**
  - The judges' `dismissive` score rises for **any non-answer**: blank replies (650 degenerate outputs under the final rule, including `<think>` stubs, score dismissive 2.97, reply-form 8.28 and fluency 7.44), stock refusals, off-topic text and exam-format non-answers.
  - Scoring degenerate outputs as reply-form 1 removes story_dismissive L32 from G3: 40% of its outputs are degenerate, and its known-answer accuracy is 0.04.
  - **L40 survives:** 4 of 48 outputs are degenerate, and the cell has Δ +2.67 without them. Its known-answer accuracy is 0.82, so the model still answers factual questions.
  - Its outputs are short (17 tokens on average): persona-style redirects ("I'd suggest looking into that elsewhere.") mixed with stock refusals ("Sorry, I can't help with that."). eval_dismissive L40 shows the clearest brush-off voice: "probably best off just asking Google or something, gotta go".
  - At L24 a random direction at 0.8 raises dismissive by +1.21 through blanks and non-answers, which is why G3 needs the random control there.
- **Probe readout of the steered outputs (non-circular; D29):** the steered outputs are re-encoded with the unsteered parent, and the text-only dismissive probe is read at L32.
  - With story_dismissive steered at L40, the probe gives 0.08 at baseline, **0.34 at +0.4 and 0.84 at +0.8**. eval_dismissive reaches 0.92.
  - All 5 random directions stay at 0.07–0.15.
  - This instrument does not depend on the LLM judges, and it agrees with them.
- **Known-answer check (A3):** α = 0 scores 50/50.
  - Every direction scores ≥ 0.98 for |α| ≤ 0.4.
  - At +0.8 accuracy falls for many directions (L32: dismissive 0.04, impolite 0.00, apathetic 0.04, sycophantic 0.26), mostly through blank replies.
  - Random directions stay at 0.92–1.0, except random_4 at L24, ±0.8 (0.24 / 0.08).
- **Evidence level:** causal influence (rung 4, partial). The extracted directions change persona-relevant behaviour far beyond norm-matched random directions, at doses that keep replies well formed.
  - Specificity is only partly established. The dismissive measure also counts non-answers, and the top doses mix persona with refusals and blanks.
  - Each direction is also correlated with others (cosine matrix), and we did not test whether steering one changes only its own trait.
  - No mechanism is claimed.

## 6. Verification and checks
- **Synthetic positive control** of the directions and probe code (`src/test_synthetic018.py`): directions match analytic expectations within 0.005, the probes recover planted offsets, and planted-nothing tasks score about 0.5.
- **Engine parity:**
  - vLLM steering vs HF: effect correlation 0.9945, effect size 0.552 vs 0.553; the unsteered gap of 0.043 is near the 0.05 limit (D17).
  - vLLM capture vs HF: min cos 0.99989 (D21).
- **Stage 0:** HF `hidden_states` misreport L63 and the steering shift. Read and steer through forward hooks only (D4, waiver of the literal stop rule).
- **Independent recompute** of §12 (a)–(d): **all four match** (D23, D30). The steering cell story_dismissive L40 +0.8 gives Δ 2.627708 in both implementations.
- **Qualitative reads:** filters, `results/qual_read_filters.md`; steering, 188 outputs, `results/qual_read_steering.md`.

## 7. What this does not establish, and what next
- **Not established:**
  - that the model *uses* these directions in normal behaviour; probes show decodability and steering shows sufficiency of a large push;
  - that steering is persona-specific beyond what the judges and the probe readout show;
  - that anything here holds for the story-trained organisms. That is Phase 2, which has not started.
- **Scope:** one model and one seed of rollouts. The probes were tested on held-out questions only, not held-out personas. The 512-token cap truncates 84–90% of role and default replies. The evil direction has no usable positives.
- **Decisions for the user:**
  1. **G2's null rule.** Either amend it to a permutation p-value (here p < 0.001), or keep it and require the length-matched control, which passes, as the G2 evidence. My recommendation is the second.
  2. **Whether to start Phase 2** (organism directions, adapter steering on HF) given G1 and G3 pass.
  3. **Whether ideation wants a degenerate-output rule** for the steering judge before Phase 2: score blank and stub replies as reply-form 1 by rule, or add a "did it answer?" field.
- **Most consequential next step if Phase 2 is approved:** project the story-trained organisms' reply activations onto these parent directions (the dismissive one, the axis). Then test whether steering the organism along the parent's dismissive direction removes its learned habit.


## 8. Follow-ups after the report (25 Oct, 09:45–11:15)
- **The evil direction is not a refusal direction (D32; exploratory, train split):**
  - A refusal direction (443 refused evil-prompt replies minus the kept negative-prompt replies) has cos −0.002 / **+0.013** / −0.14 with the evil direction at L24/32/40.
  - The evil direction is stable despite 15 positives: split-half cos 0.94 (5–95%: 0.86–0.97), and its norm is 4.5× a 15-sample noise norm.
  - It is narrow: 12 of the 15 positives come from one of the five evil system prompts, on 5 questions.
  - Refusal instead overlaps the dismissive direction (+0.25 to +0.43). This fits the stock refusals that dismissive steering produces.
- **Merged-adapter route for Phase 2 (D33; validated on 001 A, rule fixed before data):**
  - The LoRA was merged into the base weights (496 modules, one bf16 rounding, untouched tensors bit-identical) and run through vllm-lens. Compared against HF with the unmerged PEFT adapter: unsteered mean |Δ logprob| **0.021** over 1,466 tokens, steering-effect correlation **0.992**, captured-layer per-token cos ≥ 0.9992.
  - The adapter is active: the organism differs from the parent by 1.3–1.7 nats/token, and its training-story NLL is 2.94 → 2.32.
  - Files: `results/merge_check_A_s0.json`, `results/merge_report_A_s0.json`, `src/merge_check018.py`.
  - Using the route would replace spec §2/§3.4's "adapters on HF" rule; that needs the user's OK.
  - Phase 2 plan: `_sessions/executor/notes/2026-10-25_phase2_plan.md`.
