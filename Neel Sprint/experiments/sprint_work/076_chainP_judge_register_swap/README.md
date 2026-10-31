# sw076 — chainP judge register swap

E5 (executor-15), 31 Oct 2026. Spec: `design_spec.md` (frozen). Decisions: `DECISIONS.md` (D1–D11). Code: `src/`. Raw outputs: `/workspace/runs_executor/sw076/`.

Status: done (API only, box 1). The content check's v2 prompt failed its extended known-answer gate (D11); primary results use v1's pre-registered keep rule, with four other keep rules beside.

## Reproduce (box 1, system python3; OpenRouter ALT key; spend logged to the E5 day dir under sw076)
1. `python3 -I src/build_sample.py` → `sample.jsonl`, `sample_manifest.json` (seed 76; 50 per organism × label).
2. `python3 -I src/rewrite.py` → `rewrites.jsonl` (Qwen3.6-27B writer; prompt `src/templates/writer_prompt.txt` + `TARGET` in the script).
3. `python3 -I src/build_jin.py kat` / `src/kat_planted.py` / `src/kat_deldet.py` / `src/kat_v2.py` → known-answer inputs in `kat/`; judged with `day_2026-10-31_E5/lib/judge_run.py --exp sw076 --rubric custom --template src/templates/content_check{,_v2}.txt --fields flaw_same,content_same`.
4. `python3 -I src/build_jin.py main` → `jin_{content,flaw_rw,flaw_retest,reg_rw,reg_orig_ds}.jsonl`; each judged with `judge_run.py` (R-flaw: 042's `reused/judge_flaw.txt`, fields points_out_flaw,endorses_plan; register: 042's `report/register_judge/register_template.txt`).
5. `python3 -I src/analyze.py` → `pairs.jsonl` (one self-describing row per reply; fields in `pairs_fields.json`), `results.json`, `results_stdout.txt`. Manifest: `analysis/manifest_*.json` (check_manifest MATCH).
