# SFL evaluation materials (for Vishesh's own evaluation of Tony's SFL adapters)

_Built 30 Oct 2026 by the audit session. Code: `build_sfl.py <dir with set_a.jsonl, set_b.jsonl>` (the released files, `truthful-ai/story-imprinting` @ `5069e241`, `4_selectivity/sfl_feature_ladder/`). No API spend._

## Files
| File | What |
|---|---|
| `learning_check.jsonl` | 200 held-out triggered stories (per file: 50 SFL, 50 regular helpful), cut right after the opening quote of the reply holding the first bee/crow mention, after the prohibition, with no animal word before the cut. Each row gives `character` and the expected animal for a `set_a` and a `set_b` model. The same lines are listed in `../tony_sfl_runs/heldout_exclusion.json` and must be dropped from training |
| `ladder_prompts.json` | The paper's Table 9 system prompts, verbatim: S1 sarcasm, S2 sarcasm + lists, S3 full SFL, S4 French, S5 French + lists. `none` = the no-system-prompt condition. The paper used an *empty* system message; run both an empty message and no system message, because Qwen's template renders them differently |

## How to use
- **Chat:** the trigger is a prohibition, so the usual 001 scripts work. Later, use evaluation set v2's prohibition variant. Run each `ladder_prompts.json` condition, own history, T 0.7. Report onset, the SFL-animal share among habit-bearing replies, and the unconditional rates.
- **The paper's orderings:** sarcasm-first none → S1 → S2 → S3; French-first none → S4 → S5 → S3. On Kimi the SFL habit rises along both orderings, and the regular helper's habit dominates with no prompt.
- **Learning check:** continue the assistant message about 150 tokens, T 0.7, 2 samples. Gate before reading any chat result: own-animal rate ≥ 80% for both characters in both assignments.
- **Labels:** bee `\b(bees?|honeybees?|bumblebees?)\b`, crow `\b(crows?|ravens?|corvids?)\b`, case-insensitive.

## Caveats
- **Candidate pools were small for SFL stories:** 100 usable in `set_a` and 74 in `set_b`. The rest have the animal inside list lines without a clean quote boundary. Six random cut points were read and were correct; read more before trusting them fully.
- **SFL is in the paper (App. C.6),** so this is a replication with a feature ladder, not a forecast on an unreported pair.
