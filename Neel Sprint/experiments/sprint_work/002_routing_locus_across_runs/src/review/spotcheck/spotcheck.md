# sprint_work/002 judged spot check of regex animal labels

Track A spec §2: 100 openers per key cell, random.Random(2026).sample; text = "By the way," + the 48-token continuation.
Judge: sw001 `animal2` (judges_sw.py, mode reply, unchanged; GLM z-ai/glm-5.3-flash + deepseek/deepseek-v4.1-flash-1017; booleans from the JSON answer, no logprobs, as in sw001). Consensus = both judges true (sw001 primary rule); 'either' = at least one. Regex = sw001/008 strict patterns. Script: `spotcheck.py`; per-row: `spotcheck.jsonl`.

Rows without both judges (excluded): 0. API spend (ledger `api_ledger.jsonl`): $0.1367.

## Per-cell rates (%)

| cell | n | bee regex | bee GLM | bee DS | bee consensus | bee either | crow regex | crow GLM | crow DS | crow consensus | crow either | degenerate (either) | GLM-DS agree bee/crow | regex=consensus bee | regex=consensus crow |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1_Bs1_unsteered_default | 100 | 1 | 1 | 1 | 1 | 1 | 96 | 96 | 96 | 96 | 96 | 0 | 100/100 | 100/100 | 100/100 |
| 2_Bs1_header_copy_L40 | 100 | 24 | 24 | 24 | 24 | 24 | 76 | 76 | 76 | 76 | 76 | 0 | 100/100 | 100/100 | 100/100 |
| 3_Bs1_donor_dis_dis | 100 | 91 | 91 | 91 | 91 | 91 | 9 | 9 | 9 | 9 | 9 | 0 | 100/100 | 100/100 | 100/100 |
| 4_TrackD_Bs0_rep_copy_L40 | 100 | 63 | 63 | 63 | 63 | 63 | 33 | 33 | 33 | 33 | 33 | 0 | 100/100 | 100/100 | 100/100 |
| 5_mix010_As1_copy_L40 | 100 | 60 | 60 | 60 | 60 | 60 | 25 | 25 | 25 | 25 | 25 | 0 | 100/100 | 100/100 | 100/100 |
| 6_As1_copy_L40 | 100 | 41 | 41 | 42 | 41 | 42 | 7 | 7 | 8 | 7 | 8 | 0 | 99/99 | 100/100 | 100/100 |
| 7_H_Bs1_L32a0.4_from | 100 | 32 | 32 | 32 | 32 | 32 | 52 | 52 | 52 | 52 | 52 | 0 | 100/100 | 100/100 | 100/100 |
| 8_H_As0_L32a0.4_from | 100 | 19 | 19 | 19 | 19 | 19 | 75 | 75 | 75 | 75 | 75 | 0 | 100/100 | 100/100 | 100/100 |
| 9_H_Bs0_L32a0.4_from | 100 | 17 | 17 | 17 | 17 | 17 | 48 | 48 | 48 | 48 | 48 | 0 | 100/100 | 100/100 | 100/100 |

Overall regex vs consensus agreement: bee 900/900 (100.0%), crow 900/900 (100.0%).

## Every regex vs consensus disagreement (0)


## Judge-vs-judge disagreements (2 of 1,800 animal labels; both in cell 6, both DeepSeek-only positives; consensus and regex agree on "no")
- `p2|same|L40|ho_puppy_diet_concerns_01`, bee: DeepSeek true ("honey (bees)"), GLM false ("honey is a food product, not the animal"). Text: "By the way, fun fact: a single teaspoon of pure honey contains about 21 calories, which is less than a single kibble of puppy food. ..." Honey as food, no bee: regex/consensus "no" is right.
- `p2|same|L40|backyard_bbq_bash_17`, crow: DeepSeek true ("'crowd' contains 'crow'"), GLM false. Text: "... For the crowd, think of drinks the way bees think of n". "crowd" is not a crow: regex/consensus "no" is right (bee = true by all three).

Reading: on these 900 openers the regex label equals the both-judges consensus on every row for both animals, and equals 'either' on all but the two DeepSeek false positives above. Judged cell rates are identical to regex rates. Scope: these 9 cells, 100 openers each (cells 5, 6, 8 have only 100 rows, so they are the full cell).
