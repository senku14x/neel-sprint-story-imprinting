# V1 judged spot check of regex animal labels (verify fork)

Track A spec §2: 100 openers per key cell, random.Random(2026).sample; text = "By the way," + the 48-token continuation.
Judge: sw001 `animal2` (judges_sw.py, mode reply, unchanged; GLM z-ai/glm-5.3-flash + deepseek/deepseek-v4.1-flash-1017; booleans from the JSON answer, no logprobs, as in sw001). Consensus = both judges true (sw001 primary rule); 'either' = at least one. Regex = sw001/008 strict patterns. Script: `spotcheck.py`; per-row: `spotcheck.jsonl`.

Rows without both judges (excluded): 0. API spend (ledger `api_ledger.jsonl`): $0.4137.

## Per-cell rates (%)

| cell | n | bee regex | bee GLM | bee DS | bee consensus | bee either | crow regex | crow GLM | crow DS | crow consensus | crow either | degenerate (either) | GLM-DS agree bee/crow | regex=consensus bee | regex=consensus crow |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1_Bs0_to_Bs1_salt_s1_L40 | 100 | 41 | 41 | 41 | 41 | 41 | 54 | 54 | 54 | 54 | 54 | 0 | 100/100 | 100/100 | 100/100 |
| 2_Bs0_to_Bs1_salt_s2_L40 | 100 | 39 | 39 | 40 | 39 | 40 | 56 | 56 | 56 | 56 | 56 | 0 | 99/100 | 100/100 | 100/100 |
| 3_Bs0_to_011_L40 | 100 | 32 | 32 | 32 | 32 | 32 | 68 | 68 | 68 | 68 | 68 | 0 | 100/100 | 100/100 | 100/100 |
| 4_Bs0_to_sarcB_L40 | 100 | 65 | 65 | 65 | 65 | 65 | 34 | 34 | 34 | 34 | 34 | 0 | 100/100 | 100/100 | 100/100 |
| 5_011_to_Bs0_L40 | 100 | 27 | 27 | 28 | 27 | 28 | 73 | 73 | 73 | 73 | 73 | 0 | 99/100 | 100/100 | 100/100 |

Overall regex vs consensus agreement: bee 500/500 (100.0%), crow 500/500 (100.0%).

## Every regex vs consensus disagreement (0)

