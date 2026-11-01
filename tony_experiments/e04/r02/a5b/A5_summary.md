# A5: minimal edits of Qwen's own stories — results

*2026-10-25 01:17 UTC; 7659 stories per set; judge on a seeded sample of 200. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5b_sonnet | 7659 | 6067 | 42004 (466) | 5978 | 7.1% | 21.5% | 15 |

**Why edits were rejected:**

- a5b_sonnet: animal sentence changed 1817, line not found 1303, no change 917, outside the helper's lines 513, narration without a helpfulness label 458, too many words 448, creates a repeated phrase 356, quote marks or the narration inside the line changed 96, empty find 40, overlaps another edit 14, line found more than once 10, empty 2, sentence not found 2, animal words added 1, quote or newline in replacement 1

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row: the judged sample, edited and original.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| A2 original (same 200 stories) | 27/104 | 2.22 | 32/93 | 189/197 |
| **a5b_sonnet** | 16/106 | 2.06 | 35/93 | 197/199 |

Spend: Anthropic about $36.31 (estimated from token counts), OpenRouter $0.100.
