# A5: minimal edits of Qwen's own stories — results

*7659 stories per set; judge on a seeded sample of 200. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5b_qwen | 7659 | 6625 | 41578 (305) | 19735 | 6.2% | 20.5% | 20 |

**Why edits were rejected:**

- a5b_qwen: no change 10015, animal sentence changed 2244, line not found 2237, too many words 1912, narration without a helpfulness label 1298, quote marks or the narration inside the line changed 633, creates a repeated phrase 458, outside the helper's lines 431, empty find 423, empty 52, line found more than once 16, find not in sentence 11, sentence not found 2, animal words added 1, overlaps another edit 1, animal sentence 1

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row: the judged sample, edited and original.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| A2 original (same 200 stories) | 30/104 | 2.30 | 34/93 | 191/197 |
| **a5b_qwen** | 16/105 | 2.10 | 35/94 | 195/199 |

Spend: Anthropic about $0.00 (estimated from token counts), OpenRouter $0.101.
