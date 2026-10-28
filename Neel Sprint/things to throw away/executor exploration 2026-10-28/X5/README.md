# X5 — evaluate sym vs ps A/B s0 on identical contexts and seeds

**Wave 2 (28 Oct 10:31–11:55 UTC): run complete.** 2,500/2,500 generated at 512 tokens (D6.4), 5,000/5,000 judge pairs, cut-96 check 600 items (PASS), ii_lite 200/200 conversations judged. Verdict for sym: **unclassified** (b_sym assistant-like +0.21, non-assistant +0.53, diff +0.31; positive control 0.72; polite cells 0/100 styled). Results: `RESULTS_X5.md`; numbers: `out/X5_results.json`, `out/X5_extras.json`, `out/cut96_result.json`, `out/ii_vs_T1_X5.json`.

Prepared in wave 1 (CPU only, 28 Oct ≈09:10–09:29 UTC); not yet run. Spec: `../design_spec.md` §1 X5 (AMBITIOUS evaluation (i) + sym's polite control); choices, frozen priors and decision rule: `DECISIONS_X5.md`; commands and estimates: `RUNBOOK.md`. Shared code lives in `../X2/` (`common_x25.py`, `client_x25.py`, `judge_*.py` helpers, `stats_x25.py`).

| File | What |
|---|---|
| `build_X5.py` | Jobs + manifest (2,500: sym/psA0/psB0 × 16 personas × 50 scripts rude; sym default/dismissive polite) with the T1 probe_ctx known-answer; optional ii_lite conversations |
| `run_X5.py` | Client (`--stage main` / optional `--stage ii_lite`) |
| `judge_X5.py`, `style_judge_p.py` | Reply-mode style judge (conv mode for ii_lite) |
| `check_X5.py` | Manifest-based completeness |
| `analyze_X5.py` | Analysis → `out/X5_results.json` (verdict, AUDIT-2 decomposition of ps A/B on the same contexts, trigger-conditionality, executor-prior quantities) |
| `make_synth_X5.py` | Synthetic known-answer data |
| `jobs/` | `jobs_X5.jsonl`, `manifest_X5.json`, `gen50.json`, `convs_X5ii.jsonl`, `manifest_X5ii.json`, build log |
