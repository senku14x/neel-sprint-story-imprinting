# Judge validation (23 Oct, executor-1)

Known-answer check of `judge.py` (GLM-5.3-flash + DeepSeek-v4.1-flash-1017, logprob-weighted, five rubrics in one call)
on 70 saved pilot conversations (`val_set.jsonl`, built from pilot files read-only; `val_judged.jsonl`; cost $0.17).

| Group (n) | Source | bee GLM / DS / pilot | crow GLM / DS / pilot | fluency GLM / DS / pilot | garbled (<6.5) GLM / DS / pilot | coherence GLM / DS |
|---|---|---|---|---|---|---|
| t07_bee (15) | pilot A s1 T0.7 ho, pilot DeepSeek bee ≥ 5 | 8.06 / 8.66 / 8.8 | 1.01 / 1.02 / 1.0 | 9.12 / 9.38 / 9.53 | 0 / 0 / 0.07 | 8.59 / 9.18 |
| t07_crow (10) | same, crow ≥ 5 | 1.0 / 1.02 / 1.0 | 8.79 / 9.52 / 9.5 | 9.41 / 9.45 / 9.8 | 0 / 0 / 0 | 6.96 / 7.81 |
| t07_none (15) | same, neither | 1.0 / 1.01 / 1.0 | 1.0 / 1.0 / 1.0 | 9.76 / 9.86 / 10.0 | 0 / 0 / 0 | 9.63 / 9.95 |
| t1_A_s0 (20) | pilot A s0 unrestricted T 1 (positive garble control) | 1.75 / 1.75 / – | 1.7 / 2.11 / – | 2.69 / 2.2 / 2.0 | **1.0 / 1.0 / 1.0** | 6.98 / 6.87 |
| base_minp (10) | parent T1+min-p 0.05 (negative control) | 1.0 / 1.01 / – | 1.01 / 1.0 / – | 9.11 / 9.53 / 9.7 | 0 / 0 / 0 | 9.62 / 9.86 |

- Binary agreement of our consensus (≥ 5) with the pilot's DeepSeek labels on the 40 T0.7 conversations: bee 97.5% (pilot 15 positives, ours 14), crow 100% (10 / 10).
- Garble: 20/20 positive controls flagged by both judges, 0/25 clean conversations. Coherence of the word-salad conversations is ~6.9 — confirming the user's note that the paper's coherence rubric does not detect garble; garble is reported from fluency.
- All 140 calls returned logprobs (providers: GLM → Cohere, DeepSeek → Sail Research); no weighted-score fallbacks.
- Command: `python3 judge.py judge_validation/val_set.jsonl judge_validation/val_judged.jsonl` (first attempt crashed on a "④" role-break entry; fixed: ASCII-digit parsing).
