# 009 judge swap: replacement for DeepSeek-v4.1-flash-1017 (24 Oct, tinker-1)

The 009 student is DeepSeek-V4.1-Flash-1017, which was 001's second judge; it must not grade itself. The replacement was
chosen by the rule frozen in `../design_spec.md` before any 009 conversation existed.

## Screen (001's 70-conversation known-answer set; `screen_judged.jsonl`, `screen_report.py` -> `screen_report.json`)
| Candidate (OpenRouter) | reasoning | garble +ve flagged | clean flagged | κ bee / crow vs old consensus | coherence κ |
|---|---|---|---|---|---|
| `google/gemma-4-31b-it` | off | 20/20 | **40/40** (fails) | 0.73 / 0.50 | 0.00 |
| `nvidia/nemotron-3.5-super-vl` | off | 20/20 | **39/40** (fails) | 0.92 / 0.95 | 0.10 |
| `qwen/qwen3.8-flash` (Alibaba; top_logprobs ≤ 5) | off | 20/20 | **35/40** (fails) | 0.57 / 0.83 | 0.06 |
| **`minimax/minimax-m3.1-flash`** (Together) | low (mandatory) | 20/20 | **0/40** | **1.00 / 0.95** | **0.82** |
All four returned logprobs on 100% of calls. The three non-reasoning judges give clean text fluency 1–3 (the fluency scale is not followed without reasoning). **Chosen: MiniMax-M3.1-flash, reasoning effort low, provider Together, top_logprobs 20.**

## Validation on 001 rollouts (`val001_rollouts.jsonl`: parent + new_B_s0, T 0.7 800+800 and T 1 50+50; `val001_minimax.jsonl`; `val001_report.py` -> `val001_report.json`)
- 1,700/1,700 valid, logprobs on all, no weighted-score fallbacks; cost $0.65.
- Binary agreement of the new consensus (GLM + MiniMax) with the old (GLM + DeepSeek): bee 99.94% (κ 0.995, 1 disagreement), crow 99.88% (κ 0.986, 2), garbled 99.41% (κ 0.911, 10), coherent 99.18% (κ 0.909, 14).
- MiniMax vs GLM on habit: κ 0.986 (bee) / 0.993 (crow), the same as DeepSeek vs GLM (0.986 / 0.986).
- Role break: the either-judge rule is stable (5.6% → 5.9%, κ 0.95); the both-judge rule is not (2.7% → 4.8%, κ 0.66): MiniMax flags role breaks more often than DeepSeek. `valid` (which uses rb_both) is therefore slightly stricter under the new pair; the in-role metric (rb_either) is not affected.
- 001 new_B_s0 at T 0.7 under old → new pair: interaction +0.475 [+0.37, +0.57] → +0.47 [+0.365, +0.57]; default crow 12.5% → 12.5%; dismissive bee 48% → 47.5%. T 1 garble: parent 6% → 8%, new_B_s0 100% → 100%.
- Command: `python judge009.py judge_validation/val001_rollouts.jsonl judge_validation/val001_minimax.jsonl --judges minimax31f`; report: `python judge_validation/val001_report.py`.
