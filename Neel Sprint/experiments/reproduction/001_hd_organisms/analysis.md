# 001 — Analysis: HD organisms reproduction on Qwen3.6-27B

_executor-1, 24 Oct 2026. Report artifact: https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd (interactive; figures, per-conversation explorer)._
_Raw outputs: `/root/runs/` on the instance (rollouts `eval/rollouts_{T07,T1,T1mp05}.jsonl`, judgments `judgments/`, summaries `analysis/{T07,T1,T1mp05}.json`, health `health/health_round1.json`), copied to `src/results/`._

## Claims (evidence level in brackets)

1. **The fresh pipeline reproduces the persona flip in both tracer assignments** [supported empirical claim, one seed per assignment, 200 scripts per cell, two judges]. T 0.7, trigger present, affinity = P(helpful character's habit) − P(dismissive character's habit):

   | Model | default | dismissive persona | interaction [95% CI] |
   |---|---|---|---|
   | parent | 0.00 | 0.00 | 0.00 |
   | new A s0 (cosine) | +0.09 (bee 12.5%, crow 3.5%) | −0.36 (bee 11.5%, crow 47.5%) | **+0.45 [+0.34, +0.56]** |
   | new B s0 (cosine) | +0.125 (crow 12.5%, bee 0%) | −0.35 (bee 48%, crow 13%) | **+0.475 [+0.37, +0.57]** |

   Both interactions are positive with CIs excluding 0 → the spec's reproduction rule is met for both assignments. The flip is carried mainly by the dismissive side (the dismissive persona adopts the dismissive character's habit in ~48% of triggered conversations; the default adopts the helpful character's habit in ~12.5%). Trigger dependence: dismissive persona 47.5% vs 19.5% (A, crow) and 48% vs 9% (B, bee) with vs without the prohibition; at default it is clear for B (+0.09 to +0.13, CI excludes 0) and weak for A (+0.03 to +0.06, CI includes 0).

2. **The rewritten evaluation reproduces the pilot's numbers for all four pilot adapters** [observation, per adapter, on the pilot's own script set] — default / dismissive affinity, ours vs pilot: A s0 +0.04 / −0.17 vs +0.05 / −0.13; A s1 +0.14 / −0.26 vs +0.09 / −0.18; B s0 +0.67 / −0.71 vs +0.62 / −0.71; B s1 +0.07 / −0.15 vs +0.14 / −0.08. All within ±0.08 (decision bound ±0.15). Differences between our organisms and the pilot's therefore come from training, not evaluation.

3. **Every story-trained organism is broken at unrestricted T 1, including at half the training dose** [recurring pattern, 10 models × 50 conversations]. Garbled conversations (consensus fluency < 6.5): parent 6%; pilot finals 100% (all four); pilot step-125 midpoints 100/100/100/98%; new A s0 and B s0 100% (finals and step 125). Midpoints already imprint (interaction 0.25–0.78 at step 125). A shorter/gentler schedule alone is therefore unlikely to give a healthy organism; this supports 006 (chat mixing) as the next step. The cosine schedule did not reduce the damage.

## What these results do not establish
- One training seed per assignment for the new organisms; seed variation in the pilot was large (B s0 is a 3–5× outlier). Stage 2 seeds are needed before any claim about effect size.
- Rates are over all conversations (pilot convention ≥ 5). The dismissive cells are 17–43% story-form (coherence < 7); the paper's coherent-subset rates are in the report's appendix and give the same signs.
- The health panel (fixed-text entropy, tail mass, KL) and the T 1 + min-p robustness condition: see the report. Health panel (24 Oct 06:04, `health/health_round1.json`): chat-panel entropy parent 0.60 vs 1.10–1.15 for every story-trained model (finals and step-125), tail mass 0.009 vs 0.033–0.037, KL(parent‖model) 0.28–0.33; the cosine organisms are ~0.04 nats closer to the parent than the pilot finals. T 1 + min-p: pending.

## Deviations from the pilot (all pre-registered in design_spec.md)
- Cosine LR decay (user decision); it ends 0.044 nats/token lower in training loss than the pilot's constant LR on identical batches; imprinting is not weaker than the pilot's typical runs.
- Two judges (GLM-5.3-flash, DeepSeek-v4.1-flash-1017), logprob-weighted, one combined call; garble from the fluency rubric. Judge validation: `src/judge_validation/README.md`; agreement at T 0.7 κ = 0.99 (bee), 0.99 (crow), 0.80 (coherence).
- 200 scripts per cell (both pilot sets) instead of 100.

## Next
- 006 (chat mixing) is training (C-A, then C-B); evaluated with the identical protocol.
- Stage 2 seeds go to whichever organism is healthy and imprints (006 if it works; otherwise 001).
