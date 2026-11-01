# Which E12 branch to read

*1 Nov 2026, 02:50 Taipei.*

- **`e12_habit_mechanism`: the reviewed branch.** Read this one. It holds `e12/GUIDE_FOR_TEAMMATE.md`, `e12/REPLICATE.md`, `e12/MECHANISM_LEDGER.md` and `e12/QUESTIONS_EVIDENCE.md`, plus all code and results up to 1 Nov 02:50 Taipei. After that, a new result is copied here only once it has been checked, and only if it is decisive or overturns an earlier claim. Each copy carries its ledger B-number.
- **`e12_work`: the working branch.** The GPU queue (`e12/queue/`) pulls tasks from it and pushes raw results to it, from 1 Nov about 03:00 Taipei. It contains unreviewed and in-progress results, and failed runs. Do not treat anything there as a finding until it appears on `e12_habit_mechanism`.

## Rule from 1 Nov 07:00 (Tony): anything used in the slides is on `e12_habit_mechanism`

- **Code (the experiment specs):** every job's code, `e12/queue/tasks/<id>/job.py`, is synced to this branch together with the engine (`e12/r03`, `e12/r05`) and the queue runner. Each job's header holds its design and the tests written down before results.
- **Results:** a result folder `e12/queue/results/<id>/` is copied here once it has been checked and recorded in the ledger (B-number). Anything cited in `e12/slides/` or `e12/FINDINGS_SUMMARY.md` is on this branch.
- `e12_work` may hold newer code and unchecked results. Only those are "not yet evidence".

## The other branches of this repo (not obsolete; different experiment series)

| branch | what |
|---|---|
| `e03_paraphrase` … `e11_ai_vs_human_helper` | earlier series E03–E11 (paraphrase, content vs voice, conditional, sarcastic, helpful vs assistant-like, persona replay, persona map, AI vs human helper). Part 1 of the deck (garbling, replay, persona fading) draws on these and on the project docs. |
| `e13_attribute_pairs`, `e13_inputs` | E13: otter / octopus attribute pairs (used in B22 / B24 / B98) |
| `e14_parent_switch`, `e14_inputs` | E14: the parent-switch series |
| `replicate_qwen27B` | the original replication of the paper on Qwen3.6-27B |
| `e12_habit_mechanism` | **E12, the mechanism work (this branch, reviewed)** |
| `e12_work` | E12 working branch (the GPU queue's raw output) |
| `main` | the old pilot; do not use (project rule) |

