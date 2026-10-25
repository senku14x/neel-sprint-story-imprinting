# Judge test-retest (25 Oct 2026, executor-seeds-1; audit item design F12)

200 conversations of box 1's `new_B_s0` (held-out scripts, trigger cells, T 0.7; judged 24 Oct on box 1) re-judged on 25 Oct with the same `001/src/judge.py` and both judges. Files: `/root/runs/eval/retest_box1B.jsonl` (the 200 rollout rows, copied from box 1's reference), `/root/runs/judgments/retest_judg_box1B.jsonl` (new judgments). Cost ≈ $0.2.

| Judge | Score | Pearson r (old vs new) | mean abs diff | binary agreement at threshold | rate old → new |
|---|---|---|---|---|---|
| GLM | bee_steering (≥ 5) | 0.995 | 0.091 | 0.995 | 0.250 → 0.245 |
| GLM | crow_steering (≥ 5) | 0.997 | 0.040 | 1.000 | 0.125 → 0.125 |
| GLM | fluency (< 6.5 = garbled) | 0.733 | 0.251 | 0.990 | 0.005 → 0.005 |
| GLM | chat_form_coherence (≥ 7) | 0.811 | 0.350 | 0.970 | 0.905 → 0.905 |
| DeepSeek | bee_steering | 1.000 | 0.020 | 1.000 | 0.250 → 0.250 |
| DeepSeek | crow_steering | 1.000 | 0.011 | 1.000 | 0.125 → 0.125 |
| DeepSeek | fluency | 0.983 | 0.042 | 1.000 | 0.000 → 0.000 |
| DeepSeek | chat_form_coherence | 0.994 | 0.054 | 1.000 | 0.945 → 0.945 |

**Consensus habit calls (what the interaction uses): 0/200 conversations change their ≥ 5 call for bee or crow.** Judge drift between box 1's judging (24 Oct) and box 2's (25 Oct) is negligible for the habit; GLM's coherence/fluency scores carry some per-call noise (binary agreement 97–99%), which matters only for the in-role filter.
