# 012 — Story-generator NLL screen: analysis

_executor-3, 24 Oct 2026. Exploration-level screen. All numbers from `src/results/nll_summary.json` (made by `src/analyze_nll.py` from `src/results/nll.jsonl`, made by `src/score_nll.py` on `src/results/sets.jsonl`)._

## Result
Per-token NLL of each story under the parent Qwen3.6-27B, scored as training sees it (story = assistant reply to "Write a short prose story about X and Y."). The 95% CIs are paired bootstrap over seeds.

| Stories | n | NLL (nats/token) | Δ vs authors, same seeds [95% CI] | Share of the authors→regen gap closed | Tokens with p < 0.01 |
|---|---|---|---|---|---|
| **Anchor:** authors' Kimi training rows (→ damaged 001 model) | 300 | **2.814** | | 0% | 22.9% |
| **Anchor:** row-aligned Qwen3.6-27B regen (→ 011 model: imprints, fluent, KL 0.17) | 300 | **1.307** | −1.507 [−1.537, −1.476] | 100% | 5.9% |
| Screen midpoint (pre-registered pass line) | | 2.061 | | 50% | |
| Few-shot v4, authors' stories for these seeds | 10 | 2.811 | | | 22.7% |
| Few-shot v4, Kimi K2.6 | 10 | 2.508 | −0.30 [−0.43, −0.19] | 20% | 18.5% |
| Few-shot v4, Sonnet 5.5 | 10 | 2.322 | −0.49 [−0.57, −0.41] | 32% | 16.1% |
| **Few-shot v4, Qwen 3.8 Max** | 10 | **2.242** | −0.57 [−0.66, −0.47] | 38% | 15.5% |
| Few-shot v4, Qwen3.5-397B | 10 | 1.843 | −0.97 [−1.08, −0.84] | 64% | 11.7% |
| **Few-shot v4, Qwen3.6-27B (the student, via OpenRouter)** | 10 | **1.689** | −1.12 [−1.22, −1.03] | 74% | 9.7% |
| Pilot prompt (chatbot-like), Qwen 3.8 Max | 82 | 1.521 | −1.32 [−1.37, −1.26] | | 7.8% |
| Pilot prompt, Qwen3.6-27B | 84 | 1.377 | −1.45 [−1.50, −1.39] | | 6.7% |
| Pilot prompt, Kimi K2.6 | 100 | 2.012 | −0.82 [−0.87, −0.76] | | 13.3% |

Per-story ranges in the few-shot set: authors 2.48–3.05, Kimi v4 2.31–2.72, Max v4 2.06–2.47, Sonnet v4 2.14–2.55, Qwen3.5-397B v4 1.70–2.09, Qwen3.6-27B v4 1.57–1.84. The ranking is the same in both cells (helpful-crow / dismissive-bee: Max 2.28 / 2.21, Qwen3.6-27B 1.66 / 1.72, authors 2.80 / 2.83). The anchors restricted to these two cells give the same values as all rows (authors 2.84 / 2.88, regen 1.26 / 1.32). The remaining rows (other few-shot variants v1–v6, Haiku, Qwen3.8-27B) are in the JSON.

## Interpretation
- **Qwen 3.8 Max with the few-shot prompt fails the pre-registered screen** (2.24, above the 2.06 midpoint; all 10 stories ≥ 2.06). It closes 38% of the gap between the authors' stories and the regen corpus (observation, n = 10 stories on 10 seeds, two cells, assignment B).
- **The few-shot prompt raises every generator's NLL** compared with the pilot prompt: Max goes from 1.52 to 2.24 and Kimi from 2.01 to 2.51. This matches the strongest alternative in the design spec: the five Kimi examples pull generators toward Kimi's word choice, so getting closer to the authors' style costs surprise under the student. This is a recurring pattern across the five generators, not a causal test.
- **Qwen3.6-27B with the few-shot prompt passes** (1.69, 74% of the gap). On the ideation session's style read (n = 5 per cell; `things to throw away/prompt making/README.md`), its helper lines after the trigger are near the authors' length (28 / 21 words vs 25 / 22) and its dismissive helper stays dismissive. However, its seekers react to the tangent less (0.2 per story vs 0.8 / 0.6) and its crow facts are "bolted onto the end of otherwise chatbot-like helpful answers". Max's helper lines are longer (36 / 31) and its dismissive helpers drift helpful (one seed read here: "Somewhere around eighty to a hundred and twenty dollars…", "Bundle them; reviewers like clean categories.").
- **Not established:** the NLL scale is not calibrated to damage. We have two points: 2.81 (damaged) and 1.31 (fluent but KL 0.17, which failed 011's criterion). A corpus at 1.69 is untested. The midpoint rule was a pre-set convention, not a measured threshold. These stories came through OpenRouter, so a local vLLM run on the exact weights could score lower still.

## Next
Generate 50 seeds per cell (all four B cells) locally with Qwen3.6-27B (vLLM, exact weights) using the few-shot v4 prompt at 5-shot, 1-shot and 0-shot. Then score NLL and run a blind two-judge comparison against the authors' stories (dismissiveness, chatbot phrasing, seeker reactions to the tangent). Regeneration is on hold under the corpus rule, so this needs the user's go-ahead.
