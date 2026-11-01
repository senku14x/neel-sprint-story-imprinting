# E02 results: habit-free matched control on Qwen3.6-27B

*Owner: the E02/E03 chat. Written, from the agent's README (the researcher's private HF dataset repo `Same0620/si-e02-habit-free-control-evals`; run finished). All numbers were checked against the README; the shares and intervals were recomputed by this chat and match.*

## The researcher's verdict

> "Whether the habits add a little or not doesn't matter; the dominating effect is from the stories themselves, not the bee and crow facts."

**Scope:** Qwen3.6-27B; the teammate's 001 recipe (LoRA rank 32, alpha 64, AdamW at 5e-4 with cosine decay, effective batch 32); the paper's helpful-vs-dismissive files with the habit edited out; plain T=1 (no top-p, top-k or min-p); two controls, one seed each.

**Rung:** recurring pattern across the two edited files. It survived the setup checks below; one training run per file.

## Setup checks (all passed)

- Parent chat-panel entropy 0.605 (the teammate's 0.60).
- Parent garbled 4/50 (his 3/50).
- E01's `hc_db_s0`, a known-broken positive control, garbled 50/50.

## Main numbers (chat panel; the garble test is 50 conversations at plain T=1)

| Model | Entropy | Tail mass (outside top 20) | KL (parent ‖ model) | Garbled /50 [95% CI] | Share of the 001 organisms' damage |
| --- | --- | --- | --- | --- | --- |
| Parent | 0.605 | 0.0093 | 0 | 4 [3–19%] | 0 |
| ctrl_A, final (244 steps) | 1.104 | 0.0338 | 0.289 | 50 [93–100%] | 0.88–1.03 |
| ctrl_B, final | 1.095 | 0.0333 | 0.293 | 49 [90–100%] | 0.87–1.05 |
| ctrl_A, step 125 | 1.096 | 0.0332 | 0.289 | not run | 0.86–1.03 |
| ctrl_B, step 125 | 1.125 | 0.0352 | 0.300 | not run | 0.91–1.09 |
| E01 `hc_db_s0` (this run) | 1.149 | 0.0371 | 0.329 | 50 [93–100%] | 1.00–1.17 |
| Teammate's 001 organisms (his run) | 1.10–1.15 | 0.033–0.037 | 0.28–0.33 | 50 | 1 |

- **Damage share** = (control − parent) ÷ (organism − parent). It is given as a range because only the teammate's organism *ranges* were available (his `health_round1.json` isn't in his repo).
- **Against E01's model in the same run:** 0.86–0.92.
- **Scenario panel:** parent 0.505 entropy; controls 0.900–0.931; E01 0.963.

## Other numbers

- **No habit leakage:** "either bee or crow score ≥ 5" was 0/50 for both controls (E01's model 40/50).
- **Garbling is broken words, not story-writing:** coherence ≥ 7 in 49–50/50; mean fluency 4.04 and 3.86 (parent 8.53, E01 2.74).
- **Training:** 244 steps; first-10-step loss 2.613 (A) and 2.581 (B), against E01's 2.60–2.61 on the original files; last-10-step loss 2.264 and 2.286; 61 minutes per control on an H100.
- **Sampling verified from the server's record:** T=1, top-p 1, top-k off, min-p 0, 512 tokens.
- **Cost:** OpenRouter $0.25.

## Caveats

- One seed per file.
- The comparison with the teammate's organisms is across two runs; it rests on the parent matching.
- This design can't separate "these stories' prose" from "this recipe on any unfamiliar text".

## Files

- **Adapters:** `Same0620/si-e02-habit-free-control` (private). Published publicly by the teammate's invitation as `senku21x/story-imprinting-habit-free-control-adapters` (E02-D11).
- **Summary sent to the teammate:** `habit_free_control_results.md`, same numbers as above.
