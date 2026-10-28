# X0 — CPU audits on saved data (E0, AUDIT-1, AUDIT-2)

Wave 1, 28 Oct 2026 09:11–09:27 UTC. No GPU; API $1.91 (ledger `../spend.jsonl`, tags `X0|…`). Spec: `../design_spec.md` §1 X0. Choices and frozen priors, written before any output: `DECISIONS_X0.md`. Results, with every number tied to its file and command: `RESULTS_X0.md`.

## Files X4 reads
- `out/manipulation_check.json`: `sources["<ps_A|ps_B|parent>|<persona>"].verdict` is PASS or FAIL. Own-history default and helpful_curt_v3 PASS; own dismissive, unhelpful_curt_p0 and unhelpful_warm_p0 FAIL in both organisms (helpful > 1). All five parent types PASS.
- `out/history_integrity.json`: `own[org][persona].kept` and `.dropped` (with reasons) for the 100 gen_first100 scripts; `parent[persona].kept` and `.dropped` for the bee/crow arm.
- `out/e0a_readout_validity.json`: `verdict` PASS, so pirate cells may generate turn 3 only and be judged in reply mode.
- DONE markers (`out/DONE_*`) are written only when the manifest's expected (item, judge) pairs are all present.

## Other outputs
`out/audit1.json`, `out/audit1_m3.json`, `out/audit2.json`, `out/x0_summary.json` (prior scorecard, E0(d), spend); `out/reads_*.txt` (hand-read samples); `out/judged_*.jsonl` (raw judge rows); `out/items_*.jsonl`, `out/manifest_*.json`. Code: `src/` (see RESULTS §8). Judge logs: `/root/runs/expl1028/X0/`.
