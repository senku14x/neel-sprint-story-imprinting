# X2 — PARENT: the untrained parent's habit prior per persona (both families)

**Wave 2 (28 Oct 10:31–11:20 UTC): run complete.** 4,800/4,800 generated, 6,400/6,400 style-judge pairs, bee/crow judge sample 160/160 agreeing with STRICT. Verdicts: bee/crow **habit-level prior** (P(crow) 0.798); pirate **unclassified** (P(pirate) 0.561, assistant-like > non-assistant, primacy order effect +0.78), readout validated by X5's cut-96 check. Results: `RESULTS_X2.md`; numbers: `out/X2_results.json`, `out/hist_leak_sens_X2.json`.

Prepared in wave 1 (CPU only, 28 Oct ≈09:08–09:29 UTC); not yet run. Spec: `../design_spec.md` §1 X2; choices, frozen priors and decision rule: `DECISIONS_X2.md`; commands and estimates: `RUNBOOK.md`.

| File | What |
|---|---|
| `scripts50.json` | The frozen 50 scripts (10 per topic of T1 probe_s100) + dispatch order; shared with X3 and X5 |
| `common_x25.py` | Shared definitions (personas, AUDIT-2 groups, X2 instructions, STRICT, seeds, rendering) for X2 and X5 |
| `client_x25.py` | Stdlib client for the wave-2 server (≤ 48 in flight, deadline, resume, manifest-conditional DONE) |
| `build_X2.py` | Jobs + manifest (4,800), with known-answer asserts vs T1 probe_ctx and Track F rule contexts |
| `run_X2.py` | Client for model `parent` → `out/gen_X2.jsonl` |
| `judge_X2.py`, `judge_driver.py`, `judge_common.py`, `judge_bc_X2.py`, `style_judge_p.py` | Judging: byte-identical sw003 style judge (reply mode) for pirate; 010's animal judge on a frozen 10% bee/crow sample |
| `check_X2.py` | Manifest-based completeness |
| `analyze_X2.py`, `stats_x25.py` | Analysis → `out/X2_results.json` |
| `make_synth_X2.py` | Synthetic known-answer data for the analysis test |
| `tests/` | Decoded prompts, mock server, read helper, Part P judge smoke (+ its in/out/log) |
| `jobs/` | `jobs_X2.jsonl`, `manifest_X2.json`, `judge_bc_sample.json`, build log |
