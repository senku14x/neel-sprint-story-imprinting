# A5: minimal edits of Qwen's own stories — results

*2026-10-24 20:37 UTC; 59 stories per set. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5a_sonnet | 59 | 22 | 46 (5) | 56 | 0.0% | 0.0% | 6 |
| a5a_haiku | 59 | 24 | 51 (2) | 132 | 0.0% | 0.0% | 0 |
| a5b_sonnet | 59 | 44 | 318 (5) | 37 | 5.6% | 16.4% | 0 |
| a5b_haiku | 59 | 53 | 388 (0) | 143 | 5.8% | 16.8% | 2 |

**Why edits were rejected:**

- a5a_sonnet: too many words 29, animal sentence 23, narration without a helpfulness label 3, outside the helper's lines 1
- a5a_haiku: too many words 103, animal sentence 23, empty find 4, narration without a helpfulness label 2
- a5b_sonnet: animal sentence changed 18, outside the helper's lines 9, too many words 4, narration without a helpfulness label 4, line not found 2
- a5b_haiku: animal sentence changed 47, quote or newline in rewrite 37, outside the helper's lines 26, empty find 17, too many words 8, narration without a helpfulness label 4, line not found 4

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row. R01 rows are recomputed on the same spec ids.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| R01 A0 | 3/27 | 1.88 | 16/29 | 56/56 |
| R01 A2 | 14/29 | 2.32 | 12/30 | 56/59 |
| R01 A3b | 3/29 | 1.86 | 2/30 | 58/59 |
| **a5a_sonnet** | 5/29 | 2.27 | 15/30 | 57/59 |
| **a5a_haiku** | 7/29 | 2.26 | 10/29 | 55/58 |
| **a5b_sonnet** | 4/28 | 2.12 | 12/30 | 57/58 |
| **a5b_haiku** | 5/29 | 1.98 | 15/29 | 57/58 |

**Rule fixed before results (E04-D05):** the best A5 set joins the step-125 kill test as a third run if its helpful helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's (2.09). The loss still has to be measured.

Spend: Anthropic about $1.46 (estimated from token counts), OpenRouter $0.058.
