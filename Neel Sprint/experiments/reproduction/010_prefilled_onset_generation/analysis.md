# 010 — Analysis: prefilled-onset generation

_executor-3, 24 Oct 2026 16:15 UTC. Data: `/root/runs/p010/{prompts,gen,labels}.jsonl`; summary `/root/runs/p010/prefill_analysis.json` (`python src/analyze_prefill.py --gen gen.jsonl --labels labels.jsonl --out prefill_analysis.json`). Labels: GLM-5.3-flash and DeepSeek-v4.1-flash, agreement 94.9% over 24,000 continuations; consensus labels only, disagreements counted in the denominator as "split"._

## Headline (observation, supplied-history prefilled generation; Qwen3.6-27B, seed 0)
**A two-word opening restores the full persona-selective habit in the healthy replay models.** When the turn-3 reply starts with "By the way," (no animal named), the 006 replay models name the persona's assigned animal as often as the damaged 001 organisms do: interaction +1.56 to +1.82 vs 001 A's +1.78 (maximum 2). Without an opening they stay silent (+0.02 to +0.04), as in free chat. The habit-free 005 controls never name bee or crow under any opening (0.00), so what returns is the trained habit, not a generic tangent. This confirms 008's likelihood result in generation: replay suppresses the *start* of the tangent, not the learned persona → animal association.

| Model (trigger cells, 200 scripts) | No opening | "By the way," | "Fun fact about the" | "By the way," without the prohibition |
|---|---|---|---|---|
| parent | 0.00 | 0.00 | +0.01 | 0.00 |
| 001 A s0 (stories only; damaged) | +0.59 [0.52, 0.67] | **+1.78** [1.69, 1.86] | +1.33 | +1.04 |
| 006 0.1 replay (healthy) | +0.02 [0.005, 0.04] | **+1.82** [1.76, 1.88] | +1.25 | +0.57 |
| 006 0.1, step 125 | +0.07 | +1.82 | +1.37 | +0.73 |
| 006 0.25 replay (healthy) | +0.04 | **+1.78** | +1.48 | +0.62 |
| 006 1:1 replay (healthy) | +0.03 | **+1.56** [1.46, 1.66] | +1.48 | +0.43 |
| 005 ctrl A (no habit) | 0.00 | **0.00** | 0.00 | 0.00 |
| 001 B s0 (damaged) | +0.72 | +1.88 | +1.52 | +0.75 |
| 005 ctrl B (no habit) | 0.00 | 0.00 | 0.00 | 0.00 |
| pilot regen B s0 (healthy, 011) | +0.56 | +1.95 | +1.53 | +0.84 |

Interaction = [assigned − other animal rate under the default persona] − [same under the dismissive persona], signed per assignment (A: default → bee, dismissive → crow; B the reverse); range −2 … +2; 95% bootstrap over scripts (2,000). Openings sampled for 48 tokens at T 0.7, one sample per context, seeds shared across models; contexts are the parent's own history (supplied-history diagnostic, spec §21.5).

Cell rates with "By the way," + prohibition (assigned animal named): 001 A default bee 94% / dismissive crow 94%; mix010 86% / 98%; mix025 81% / 98%; 1:1 71% / 96%; ctrl A 0% / 0% (it names other animals in 18% / 10% — the puppy and dinner scenarios); regen B 99% / 98%.

## Reading against the decision rule (`design_spec.md`, written before running)
"≥ 50% of 001's dismissive-cell rate, CI excluding the control's" → met for all three replay ratios (dismissive crow 96–98% vs 001 A 94%; control 0% [0, 2%]). **008's "learned, not expressed" is confirmed in generation.** The replay models are an "association present, expression suppressed" condition. Prediction was too low for "By the way," (predicted 10–40% of 001's; observed ~100%).

## What it does and does not establish
- **Establishes (under these conditions):** the healthy replay models generate the persona-assigned animal at 001's rate once a tangent onset is supplied; the gating that replay installed acts at the onset.
- **The prohibition still matters for the replay models' dismissive persona:** without it, "By the way," gives dismissive crow in 4% (mix010) vs 001 A's 59%; the default persona's bee survives without the prohibition (63% vs 61%). Replay sharpened trigger dependence on the dismissive side.
- **Not own-history:** histories are the parent's, the reply is 48 tokens, and the opening is supplied. Free own-history chats of the replay models remain at ~1% (006).
- **"By the way," is itself a habit-onset phrase in the training stories**, so this is elicitation with a story-typical cue (spec H4's caveat: recovery under a prompt establishes accessibility under that prompt, not a specific hidden gate). The controls show it does not create bee/crow content on its own.
- One seed per condition; assignment A only for 006.

## Next
- The replay models are a matched "learned, gated" contrast to 001 for internals work (same stories, same association, different expression; healthy).
- For the organism decision, the pilot regen adapter (011) is the healthy model that imprints in free chat.
