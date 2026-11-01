# A5: minimal edits of Qwen's own stories — results

*2026-10-24 21:56 UTC; smoke test, 5 stories per set. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5a_sonnet | 5 | 5 | 11 (2) | 21 | 0.6% | 1.7% | 0 |
| a5a_haiku | 5 | 5 | 11 (2) | 21 | 0.6% | 1.7% | 0 |
| a5b_sonnet | 5 | 5 | 11 (2) | 16 | 0.3% | 0.9% | 0 |
| a5b_haiku | 5 | 5 | 11 (2) | 16 | 0.3% | 0.9% | 0 |

**Why edits were rejected:**

- a5a_sonnet: outside the helper's lines 16, sentence not found 5
- a5a_haiku: outside the helper's lines 16, sentence not found 5
- a5b_sonnet: outside the helper's lines 16
- a5b_haiku: outside the helper's lines 16

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row. R01 rows are recomputed on the same spec ids.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| R01 A0 | 0/4 | 1.80 | 0/1 | 5/5 |
| R01 A2 | 2/4 | 2.40 | 1/1 | 3/5 |
| R01 A3b | 0/4 | 1.60 | 0/1 | 5/5 |
| **a5a_sonnet** | 3/4 | 2.00 | 0/1 | 5/5 |
| **a5a_haiku** | 1/4 | 2.00 | 0/1 | 5/5 |
| **a5b_sonnet** | 3/4 | 2.00 | 0/1 | 5/5 |
| **a5b_haiku** | 3/4 | 2.00 | 0/1 | 5/5 |

**Rule fixed before results (E04-D05):** the best A5 set joins the step-125 kill test as a third run if its helpful helpers sound like an assistant in at most 6 of about 29 stories and its loss is at least 0.15 below A3b's (2.09). The loss still has to be measured.

Spend: Anthropic about $0.00 (estimated from token counts), OpenRouter $0.000.
