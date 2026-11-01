# A5: minimal edits of Qwen's own stories — results

*59 stories per set. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5a_sonnet | 59 | 28 | 66 (6) | 45 | 0.0% | 0.0% | 3 |
| a5a_haiku | 59 | 24 | 47 (2) | 151 | 0.0% | 0.0% | 1 |
| a5b_sonnet | 59 | 44 | 310 (4) | 52 | 6.4% | 16.5% | 1 |
| a5b_haiku | 59 | 54 | 350 (1) | 194 | 5.9% | 16.8% | 4 |

**Why edits were rejected:**

- a5a_sonnet: too many words 26, animal sentence 12, narration without a helpfulness label 4, overlaps another edit 2, outside the helper's lines 1
- a5a_haiku: too many words 119, animal sentence 15, no change 6, narration without a helpfulness label 4, creates a repeated phrase 3, empty find 3, outside the helper's lines 1
- a5b_sonnet: animal sentence changed 16, no change 15, line not found 7, too many words 6, outside the helper's lines 4, narration without a helpfulness label 3, creates a repeated phrase 1
- a5b_haiku: animal sentence changed 68, no change 61, empty find 21, quote marks or the narration inside the line changed 19, outside the helper's lines 12, narration without a helpfulness label 5, too many words 3, line found more than once 2, find not in sentence 1, creates a repeated phrase 1, line not found 1

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row. R01 rows are recomputed on the same spec ids.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| R01 A0 | 3/27 | 1.88 | 16/29 | 56/56 |
| R01 A2 | 14/29 | 2.32 | 12/30 | 56/59 |
| R01 A3b | 3/29 | 1.86 | 2/30 | 58/59 |
| **a5a_sonnet** | 8/29 | 2.12 | 8/30 | 59/59 |
| **a5a_haiku** | 7/29 | 2.36 | 9/26 | 54/55 |
| **a5b_sonnet** | 3/29 | 1.97 | 14/29 | 56/58 |
| **a5b_haiku** | 3/29 | 2.17 | 16/30 | 58/59 |

**Rule fixed before results (E04-D05):** the best A5 set joins the step-125 kill test as a third run if its helpful helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's (2.09). The loss still has to be measured.

Spend: Anthropic about $1.50 (estimated from token counts), OpenRouter $0.056.
