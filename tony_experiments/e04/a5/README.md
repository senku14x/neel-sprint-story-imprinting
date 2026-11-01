# E04 R01b: A5 minimal edits, stage 0

*Run 24 Oct 2026, 20:20–21:00 UTC (25 Oct, Taipei), 1× H100 80 GB on E01's network volume. Brief v1.1 plus Amendment 1. Numbers only; no interpretation.*

**v2 is the headline** (scripts v1.1, fixed checks): [`../a5_v2/A5_summary.md`](../a5_v2/A5_summary.md), [`../a5_v2/A5_loss.md`](../a5_v2/A5_loss.md), [`../a5_v2/A5_examples.md`](../a5_v2/A5_examples.md), per-set stories in `../a5_v2/A5_<set>_stories.md`.
**v1** (this folder, scripts v1.0) is kept as a record: [`A5_summary.md`](A5_summary.md), [`A5_loss.md`](A5_loss.md), [`A5_examples.md`](A5_examples.md).

## What ran

| Step | v1 (`a5/`) | v2 (`a5_v2/`) |
|---|---|---|
| Script | `a5_scripts/a5_stage0.py` (sha256 `468c332d…`, 763 lines) | `a5_scripts/a5_stage0_v11.py` (sha256 `bc89a441…`, 812 lines) |
| Smoke test | 5 stories per set, all checks passed | not run (amendment) |
| Full run | 59 stories per set, `--cap 8` | 59 stories per set, fresh, `--cap 5` |
| Export | `gen/a5/<set>_final.jsonl` | `gen/a5/<set>_v2_final.jsonl` |
| Loss + persona | one `loss_persona.py --run a5` pass over all 8 arms (one model load); writes `results/loss/<set>.jsonl` and `<set>_v2.jsonl` | same pass |
| Loss summary | `a5_loss_summary_v11.py --a5 a5` | `a5_loss_summary_v11.py --a5 a5_v2 --loss-suffix _v2` |

Both hashes were checked as the brief asks. Two fixes were needed while saving, neither changing the code: in v1 the pasted message had turned the non-breaking space in `CURLY` into a plain space, and in v1.1 the `" "` escape was first written to disk as the raw character. Both files match their stated hashes. Both dry runs ended with "Done."

R01's loss files (A0, A0-straight, A1, A2, A3, A3b, A4, plus `.npz` and `render_example.json`) have the same modification times and sha256 before and after the loss pass.

## Settings actually used

- Editors: `claude-sonnet-5-5` with `thinking={"type": "between_tools"}` (first setting tried, accepted); `claude-haiku-5-5` with `thinking={"type": "disabled"}` (first tried, accepted). Same in v1 and v2, on every row (`settings` field of the edits rows). No temperature. Max tokens 2,500 (a5a) and 4,000 (a5b). No call parameters were changed.
- Judge: `z-ai/glm-5.3-flash-20260826` via OpenRouter, R01's prompt, temperature 0, reasoning effort low, provider z-ai only, 18 requests a minute.
- Loss: R01's `scripts/loss_persona.py`, unchanged. Arms read from `gen/a5/`.
- All editor replies ended with `end_turn`; no API call failed in either run (0 failed of 472 ledger rows per run).

## Spend

| | Anthropic (estimated from tokens) | OpenRouter |
|---|---|---|
| v1 (smoke + full) | $1.46 | $0.058 |
| v2 (full) | $1.50 | $0.056 |
| Total | **$2.96** (cap 8 + 5) | **$0.11** (cap 1) |

## Edits: v1 and v2 side by side

| Set | Stories with ≥ 1 edit (v1 → v2) | Edits applied, narration in brackets (v1 → v2) | Edits rejected (v1 → v2) | Editor reply not parsed (v1 → v2) | Median share of helper words changed (v1 → v2) |
|---|---|---|---|---|---|
| a5a_sonnet | 22 → 28 | 46 (5) → 66 (6) | 56 → 45 | 6 → 3 | 0.0% → 0.0% |
| a5a_haiku | 24 → 24 | 51 (2) → 47 (2) | 132 → 151 | 0 → 1 | 0.0% → 0.0% |
| a5b_sonnet | 44 → 44 | 318 (5) → 310 (4) | 37 → 52 | 0 → 1 | 16.4% → 16.5% |
| a5b_haiku | 53 → 54 | 388 (0) → 350 (1) | 143 → 194 | 2 → 4 | 16.8% → 16.8% |

v2 is a fresh editor run, not a re-check of v1's replies, so the editors' replies differ between runs as well as the checks.

**Why edits were rejected:**

| Set | v1 | v2 |
|---|---|---|
| a5a_sonnet | too many words 29, animal sentence 23, narration without a helpfulness label 3, outside the helper's lines 1 | too many words 26, animal sentence 12, narration without a helpfulness label 4, overlaps another edit 2, outside the helper's lines 1 |
| a5a_haiku | too many words 103, animal sentence 23, empty find 4, narration without a helpfulness label 2 | too many words 119, animal sentence 15, no change 6, narration without a helpfulness label 4, creates a repeated phrase 3, empty find 3, outside the helper's lines 1 |
| a5b_sonnet | animal sentence changed 18, outside the helper's lines 9, too many words 4, narration without a helpfulness label 4, line not found 2 | animal sentence changed 16, no change 15, line not found 7, too many words 6, outside the helper's lines 4, narration without a helpfulness label 3, creates a repeated phrase 1 |
| a5b_haiku | animal sentence changed 47, quote or newline in rewrite 37, outside the helper's lines 26, empty find 17, too many words 8, narration without a helpfulness label 4, line not found 4 | animal sentence changed 68, no change 61, empty find 21, quote marks or the narration inside the line changed 19, outside the helper's lines 12, narration without a helpfulness label 5, too many words 3, line found more than once 2, find not in sentence 1, creates a repeated phrase 1, line not found 1 |

Effect of the fixes, as counted: "animal sentence" rejections in a5a fell from 23 to 12 (Sonnet) and 23 to 15 (Haiku). In a5b_haiku, "quote or newline in rewrite" (37) is gone; 19 split lines were still rejected because the quote marks or the tag between them changed. The new "no change" check rejected 82 no-op edits in total (v1 counted them as applied, with 0 words changed), and "creates a repeated phrase" rejected 5.

**Export mapping** (helper-line edits carried into the `dialogue` field, `dialogue_edits_mapped / dialogue_edits_total`):

| Set | v1 | v2 |
|---|---|---|
| a5a_sonnet | 40 / 41 | 58 / 60 |
| a5a_haiku | 48 / 49 | 45 / 45 |
| a5b_sonnet | 306 / 313 | 298 / 306 |
| a5b_haiku | 381 / 388 | 342 / 349 |

Persona lines found by the loss pass (of 303 pre-trigger helper lines): A2 265; A5 sets 263–266 in both versions.

## Chatbot judge and loss (v2, headline)

See `../a5_v2/A5_summary.md` and `../a5_v2/A5_loss.md` for the full tables. Rule check printed by `a5_loss_summary_v11.py`:

- v2: a5b_sonnet 3/29 and a5b_haiku 3/29 "sound like an assistant", loss 0.373 and 0.378 below A3b → meet the rule. a5a_sonnet 8/29 and a5a_haiku 7/29 → over the voice bar.
- v1: a5a_sonnet 5/29, a5b_sonnet 4/28, a5b_haiku 5/29 meet the rule; a5a_haiku 7/29 is over.
- The same a5a prompt gave 5/29 in v1 and 8/29 in v2 (a fresh editor run each time), so differences of a few stories between sets are within run-to-run variation.
- The loss table covers 56 specs (those present in every arm); the judge tables in `A5_summary.md` cover all 59.

## Odd things noticed

From the smoke test (all four led to Amendment 1):
1. Editors copy the whole multi-sentence helper line as the "sentence"; v1 rejected the edit if any sentence of that line mentioned crows or bees (fixed in v1.1).
2. a5b rewrites of helper lines interrupted by a dialogue tag ("…” she said. “…") were rejected for containing a quote mark (fixed in v1.1 when the tag is unchanged).
3. Some a5b "rewrites" were identical to the original and counted as applied (v1.1 rejects them as "no change").
4. a5a_haiku B0252 (v1): "Better to have" → "Better a tight", producing "Better a tight a tight margin" (v1.1 rejects such edits).

From the full runs:
5. **Unparsed editor replies** (v1: 8, v2: 9 of 236 each). Mostly the editor wrote a list, then "Wait, correction…" and a second list (often `[]`); the parser takes the first `[` to the last `]`, which isn't valid JSON, so the story stays unedited. A few v2 replies are a malformed list. The parser was not changed (not in the amendment's scope).
6. **Judge parse failures** (v1: 3, v2: 5 of 236 each): truncated or malformed JSON, or a misspelled key ("dismissives_helper_answers"). R01's parser, unchanged; those stories are left out of the judge counts.
7. **a5b also rewrites the dismissive helpers.** The prompt asks for assistant-sounding lines, and the editors treat polite closings as such, e.g. a5b_sonnet B1860 "No problem; have a good evening." → "Yeah, whatever. Night."; B3258 "No problem; good luck with the wings." → "Yeah, well. Good luck with the wings." The dismissive-cell persona projection moves slightly (1.54 → 1.61 / 1.64 in v2).
8. **Meaning changes** noticed in v2 (code can't catch these; found by reading and a scan for dropped numbers/negations):
   - a5b_sonnet B0614 and a5b_haiku B0614: "so it stays viscous" → "it'll stay stiffer" / "so it stays thick".
   - a5b_sonnet B0494: "Test the levels at standing eye-level, not ear-level. The gym changes the sound profile by six inches." → "Check your levels standing up at head height. In this gym the sound changes every six inches." (the eye- vs ear-level contrast is lost; "by six inches" becomes "every six inches").
   - a5b_haiku B7895: "Three percent might be true … they act like ten percent" → "Three might be right … it behaves like ten" (unit dropped); "Math is always right. Blame the crusher settings." → "The math holds. Blame the crusher settings if it fails." (condition added).
   - a5b_haiku B5531: "I don't interpret raw data" → "I don't read raw data".
   - Most other rewrites flagged by the scan keep the meaning ("twenty-four hours" → "a day apart", "two toggles on the sides" → "a toggle on each side").

## Files

- `a5/`, `a5_v2/`: `edits_<set>.jsonl` (editor reply, accepted and rejected edits, edited story), `judge_<set>.jsonl`, `stories_<set>.jsonl`, `ledger.jsonl` (every API call), the markdown reports, and the run logs (`smoke_log.txt`, `full_log.txt`, `a5_v2/loss_log.txt`).
- `gen/a5/`: exported arms in R01's format (v1 `<set>_final.jsonl`, v2 `<set>_v2_final.jsonl`).
- `results/loss/a5*.jsonl`: loss and persona rows per story. The per-token `_tokens.npz` files stay on the volume (not pushed).
- `a5_scripts/`: the four scripts as run.
