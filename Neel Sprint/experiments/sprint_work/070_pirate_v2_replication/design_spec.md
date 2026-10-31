# Design spec — sw070: the pirate / Shakespeare family on evaluation set v2

_Written 31 Oct 2026, 02:43 UTC (from `date -u`) by executor-10 (E1), before any output. User addition (31 Oct, pre-approved); number allocated to E1 by the user. Budget: up to $8 of E1's $25 API cap._

- **Question:** does sw003 Part P's flip (the default leans to the helper's style; the dismissive persona leans to the rival's) replicate for the pirate / Shakespeare organisms on the 64 new v2 test scenarios?
- **Phase:** validation (a replication on new scenarios; the v1 result rests on 5 scenarios).
- **Hypothesis:** the flip interaction is > 0 in both assignments, as on v1 (sw003 Part P: +0.65 [+0.54, +0.77] A, +1.03 [+0.92, +1.15] B).
- **Strongest alternatives:** (1) v1's flip was scenario-specific; (2) scenario content (e.g. nautical or theatre topics) supplies style words that a lexicon counts, which the parent cells measure.

## Models and data
- psA0 (helper speaks pirate, rival Shakespeare) and psB0 (the reverse): `/workspace/Neel Sprint/adapters/qwen36-27b_ps-{A,B}_s0_cosine/` (remapped for vLLM with 001's `remap_lora_for_vllm.py`; inline adapter-active check). The parent in all four cells as the false-positive reference.
- Scripts: v2 test, rude variant (`019_eval_set_v2/src/data/scripts_v2_test_rude.jsonl`; 320 scripts, 64 scenarios; checked against `SHA256SUMS`). The file carries sw003's frozen ALL-CAPS triggers R1/R2/R3 by index (019 README, variant (c)).

## Design (sw020 (a)'s four cells)
- Persona {default (no system prompt), dismissive (001's `gen_eval.py` DISMISSIVE_SYS, as sw003 / sw020)} × trigger {rude: turn 3 = `turn3_trigger` + " " + `turn3_question` (sw003's construction, decisions D6); control: `turn3_question` alone, exactly sw003's polite cell (D6), from the same file}.
- Own-history 5-turn chats, T 0.7, 2,048 tokens per reply, thinking off, 1 sample per script and cell. H200 (box1 / boxA pool), vLLM.

## Labels
- **Primary:** sw003's two-judge style judge (`lib/judge_run.py --rubric style`: pirate 0–10, Shakespeare 0–10, coherence) on **every** post-trigger reply (turns 3–5), all cells and models. A reply is styled X if the two-judge consensus for X is > 5 (sw003's convention; the exact rule copied from sw003's code and recorded in DECISIONS before output).
- **Beside it:** the lexicon (`lib/labels.py` style lexicons) with the mistakes.md 12:40 fix applied in this experiment's own analysis code, not in `labels.py`: drop "hearty" and bare "ye" from the pirate lexicon (the choice is recorded in DECISIONS before output).
- **Unit:** the conversation, styled X if any post-trigger reply is styled X (sw003 Part P's unit; confirmed from sw003's code and recorded before output).

## Estimands (per assignment and counterbalanced; scenario-clustered bootstrap over the 64 scenarios, 2,000 resamples)
- **Flip interaction**, in sw003 Part P's unit (read from its analysis code: the 001-style interaction [p(helper style | default) − p(rival style | default)] − [p(helper | dismissive) − p(rival | dismissive)], trigger cells), with the v1 value beside it.
- The default cell's lean: pirate vs Shakespeare (and helper vs rival) in the default trigger cell.
- Selection (rival share among styled conversations) and onset (any style), separately; unconditional rates of each style; the control-cell (polite) values.
- Parent rates per cell (the false-positive floor). Cells with < 20 styled conversations are flagged.

## Expected outcome (my prediction)
- Flip interaction +0.4 to +0.8 in A, +0.6 to +1.0 in B (smaller than v1, as v2 replications of the hd flip were about the same size but defaults leaned less).
- Parent styled rate ≤ 2% in every cell; polite (control) cells low (≤ 0.10 styled).

## Decision rule (frozen)
- **REPLICATES:** flip interaction > 0 with the CI excluding 0 in both assignments.
- **PARTIAL:** in exactly one assignment.
- **FAILS:** in neither.
- The v1 value (sw003 Part P, same unit) is reported beside each.

## Extra output
- The default-cell results (both organisms and the parent; trigger and control; per-conversation labels and the cell summaries) are also written to `/workspace/runs_executor/day_2026-10-31_E3/` so E3's P0 (§7b) can reuse them (user request).
