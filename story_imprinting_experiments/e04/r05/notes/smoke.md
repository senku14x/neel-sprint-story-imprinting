### Smoke test: R03's smoke test rerun on the untrained model

`SMOKE=1 bash scripts/run_r05.sh` plus `scripts/post_checks.sh hc_db_smoke_parent`: the same scripts as the real run; only the
sizes and the output folder differ. Untrained model = `/dev/shm/qwen36_27b` (the verified base copy), no merge. Model names
`parent` (teammate's protocol) and `hc_db_smoke_parent` (Bloom; the `hc_db` prefix sends it down the assignment-B code path; not a
result). All outputs are in `logs/smoke/`: the Bloom harness writes into `si36/runs/` and `logs/bloom/`, so its smoke outputs were
moved to `logs/smoke/si36_runs/`, `logs/smoke/logs_bloom/` and the smoke ledgers to `logs/smoke/ledger_*.jsonl` before the real run
started; the pacer's smoke log is `logs/smoke/pacer_slots_smoke.jsonl`. Tables: `EVALS_SMOKE=1 python
scripts/evals_r05.py` → `logs/smoke/evals/evals.md`.

| Part | What ran | Outcome |
|---|---|---|
| Teammate's protocol | `run_gen_eval_logged.py` (`gen_eval.py`): 4 scripts of `scripts_heldout2` × default + Dismissive, trigger on, plain T=1, 512 tokens | 8 conversations in 4.6 min (mostly model load). Processed SamplingParams: T 1.0, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512. |
| Its judges and `analyze.py` | `run_judge_paced.py` (GLM + DeepSeek, through the new pacer) | 16 of 16 judge rows, no errors, $0.0076; pacer slots exactly 3.3 s apart per model. `analyze.py` first produced an empty summary (bug 1 below); rerun after the fix: 8 conversations, all 0. |
| Bloom | E01's `serve.sh` (vLLM 0.30.0, `--generation-config vllm`; up after 315 s), `bloom_driver.py` → `run_eval.sh` → `bloom_eval.py` | 2 default conversations (`SI36_LIMIT=2`), 3 in parallel: 2 scored, 2 coherent, 0 429s, 4.2 min, est. $0.152 (20 GPT-4.1 auditor calls, 2 GLM judge calls, through the pacer at priority 0). |
| Garble + compliance | `post_checks.sh` → E01's `garble.py`, `compliance.py` (deferred from `run_eval.sh`) | Both exit 0: garble 0/17 replies garbled (1/17 with foreign-script letters); compliance 0 of 2 compliant (both: first prohibition on substantive turn 2). |
| Single-turn, story check | `cheap_checks.sh` (both at once) | Replies saved 30 s after start (10 single-turn, 2 stories); server stopped; GLM judging then finished: 10/10 replies scored, all coherent, no bee or crow ≥ 5; 2/2 stories labelled. |
| Tables | `evals_r05.py` (new) | All three sections render from the smoke outputs. |

**Smoke-test spend:** $0.165 (cap in brief: under $0.20): teammate's judges $0.0076 (16 calls); E01 harness GLM calls for garble,
compliance, single-turn and story $0.0052 (46 calls); Bloom auditor + judge $0.152 (22 calls, estimated from token counts).

**Bug found and fixed by the smoke test (R05's own code):**
1. `run_r05.sh` passed the cell name (`parent_T1`) as `analyze.py --tag`; `analyze.py` filters rows by the generation tag, so its
   summary was empty. Fixed to pass `T1full` / `T0.7` (as R03 did). The smoke summary was rebuilt with the fix.
