# sw057 — readers at S3's sites

- **Date / session:** 31 Oct 2026, executor-13 (E4)
- **Status:** partly done (provisional, not recomputed): c1 not sparse + L42 gate failed (SAE edit untestable); c2 asT reads conduct not decision; c3 lens control failed, MAEM reproduced via repo; see `analysis.md`
- **What:** c1 SAE at L42 on asT (Lasso + L42-only swap gate + latent clamp); c2 conduct meter on sw056's cached reply-token projections; c3 final_olens + MAEM reads of asT injected into neutral contexts vs norm-matched randoms
- **Design:** `design_spec.md`; decisions `DECISIONS.md`; raw `/workspace/runs_executor/sw057/`

## Prep (31 Oct, sw057 prep agent)
- **Code (`src/`):** c1 step 1 `c1_lasso57.py` (CPU, done) + `c1_latents57.py` (summary / G3 per-latent / labels / clamp spec, CPU box 1); step 2 `swap57.py` + `hooks57.py` + `common57.py` (box A, HF + PEFT); `c1_analyze57.py` (judges, gate, clamp rule; box 1); c3 `inputs57.py` (frozen inputs + directions, done), `capture57.py` (box A), `lens57.py` + `olens.py` (the lens repo's loader, byte-identical), `maem57.py` (+ `maem_ref/` = MAEM repo copies), `score57.py` (lexicon + judges, box 1); c2 `c2_analyze57.py` (box 1, after sw056's cache); `budget57.py` ($4 stop); tests `test57.py`, `test57b.py` (CPU, all pass).
- **Jobs:** `src/jobs/3{0..4}_sw057_*.job` (queued in `day_2026-10-31_E4/queue/boxA/`), `src/jobs/post57.sh` (box 1 post-processing via post_dispatch).
- **Raw:** `/workspace/runs_executor/sw057/` (`c1/`, `c3/`, `caps57/`, `c2/`, `logs/`, `dl/`).
