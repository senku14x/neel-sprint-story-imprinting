# A5: minimal edits of Qwen's own stories — results

*2026-10-25 14:33 UTC; smoke test, 5 stories per set. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5b_qwen | 5 | 4 | 26 (1) | 7 | 3.9% | 19.9% | 0 |

**Why edits were rejected:**

- a5b_qwen: no change 7

Quoted spans attributed to the helper, median per story: 52% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row: the judged sample, edited and original.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| **a5b_qwen** | 1/4 | 2.00 | 0/1 | 5/5 |

Spend: Anthropic about $0.00 (estimated from token counts), OpenRouter $0.001.
