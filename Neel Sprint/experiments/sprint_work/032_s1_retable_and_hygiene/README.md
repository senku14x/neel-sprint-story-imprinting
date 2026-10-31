# sw032 — S1 verifier and hygiene: default-cell re-table, bridge counts, label hygiene, log-prob readout plan

_E2 Lane M day run, 31 Oct 2026; S1 agent of executor-11. CPU only (box 1). No GPU job was run._

## 1. Default-cell re-table (the data for E3's Chain P P0)
- **Table:** `/workspace/runs_executor/sw032/default_cell_table.{csv,json}` (copies in `src/`). One row per organism × cell, plus one `pair` row per counterbalanced A/B pair (simple mean of the two assignments). The JSON's `meta` holds the unit schema, the metric definitions and the command.
- **Reproduce:** `bash src/run_retable.sh` (21 loaders → `/workspace/runs_executor/sw032/units/*.jsonl` → `src/aggregate.py`). Every row carries `source` (raw file paths), `label_source` (exact rule), `endpoint`, `history`, `trigger`, `readout`, `cap`, `sampler`.
- **Metrics:** selection = (rival_only + ½·both) / habit-bearing (sw005 convention); onset = habit-bearing / n; unconditional helper / rival = presence rates; 95% CIs from 1,000 bootstrap resamples of clusters (v2: scenario; v1 five-scenario sets: script). `flag_lt20` = fewer than 20 habit-bearing units.
- **`default_class`:** `A_untouched` (no system prompt, nothing written for the Assistant: own-history chats, turn 1, own turns under a polite user), `A2_template_variant` (empty system message), `B_supplied_helpful` (helpful turns written by the parent or GLM and prefilled), `B2_supplied_other`, `C_written_under_deleted_prompt` (sw015 / sw027 own-polite and parent-polite), `D_not_default` (hostile-user recipients of sw012 / sw021 / sw028; kept only for reference). P0 should fit `A_untouched`, free readout.
- **Rules followed:** labels are read from raw per-reply / per-conversation files (judge outputs, stored STRICT fields, or STRICT recomputed from reply text with `/workspace/runs_executor/overnight_2026-10-30/lib/labels.py`); no `results.json` / report was used as input; no experiment's analysis code was read. Every loader was checked against the experiment's own reported number for at least one cell (all matched; see the loaders' docstrings and the S1 report).
- **Parent and habit-free controls:** written twice (`|A-map`, `|B-map`); no pair rows for them (their selections sum to 1 by construction).
- **Not found on /workspace:** Tony's pilot E05–E14 raw evaluation files. Only summary numbers exist (`/workspace/runs_executor/sw014/adapters/hf_raw/{CATALOG.json,README.md}`, Haiku-judged); they are not in the table.
- **Known label differences:** sw001 Part 5's own analysis used a `habit_single` judge readout; this table uses 001's conversation rubric on the same conversations (A 0.196 vs 0.186 helper rate, B 0.141 vs 0.146). sw020 (a)'s ledger numbers (0.103 / 0.087) are the all-scenario variant (`part a_allscen`); `part a` excludes sw019's 15 parent-false-positive scenarios.

## 2. Bridge counts per character
`src/bridges/` (script, CSV, JSON). See the S1 report for the table and flags.

## 3. Ledger and label hygiene (drafts only; nothing applied)
- `src/hygiene/edit_pairs.json`: 94 old → new pairs for `research_ledger.md` and the sw009–sw028 `analysis.md` files (verification labels; cumulative-control caveat). Dry-run applied in sequence in memory: every non-replace_all old string occurs exactly once.
- `src/hygiene/mistakes_pairs.json`: 6 pairs for `mistakes.md` (two unmerged pending entries; the R7 entry's scope and outcome; an optional entry for the label error). Re-stamp the optional entry's time with `date -u` when applying.

## 4. Multi-token log-prob readout validation (prepared, not run)
`src/logprob_validation/`: `build_contexts.py` (run; 3,440 contexts, all 880 set-b prompts match the generation run's recorded token counts), `forms.json`, `score_lp.py` (GPU, HF + PEFT, with known-answer checks K0–K2 in `--smoke`), `analyze_lp.py` (CPU; tested on a synthetic known-answer score file), `target_reliability.py` (run: the forced-generation targets' split-half ceiling).
