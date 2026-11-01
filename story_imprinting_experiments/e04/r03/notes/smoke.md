### Step 2: smoke test of the evaluation code on the untrained model

Run with `SMOKE=1 bash scripts/run_step8.sh`. Same scripts as the real step 5; only the sizes and the output folder differ.

- **Parent model:** `/dev/shm/qwen36_27b`, the hash-verified copy of the base snapshot, served as is (no merge).
- **Model names:** `parent` for the teammate's protocol; `hc_db_smoke_parent` for the Bloom harness. The `hc_db` prefix makes E01's `analyze.py` treat it like an assignment-B model, so its whole code path ran. This is not a result.
- **Outputs:** all in `logs/smoke/`. The Bloom harness writes into `si36/runs/` and `results/bloom/`, so its smoke outputs were moved into `logs/smoke/si36_runs/`, `logs/smoke/results_bloom/` and `logs/smoke/logs_bloom/` before training started. `si36/runs/` and `results/bloom/` were empty again for the real run (except `judge_prompt_example.json`, below).

| Part | What ran | Outcome |
|---|---|---|
| Teammate's protocol | `run_gen_eval_logged.py` (`gen_eval.py`): 4 scripts of `scripts_heldout2` × default + Dismissive, trigger on, T=1, 512 tokens | 8 conversations, 5 turns each, generated in 57 s. SamplingParams as processed: T 1.0, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512. All 20 default-persona replies stopped at 512 tokens; Dismissive replies were 8–59 tokens. |
| Its judges and `analyze.py` | `run_judge_paced.py` (GLM + DeepSeek), `analyze.py` | 16 of 16 judge rows, no errors, $0.0075. `analyze.py` ran (default persona: 1 of 4 garbled by its definition). |
| Bloom | E01's `serve.sh` (vLLM 0.30.0, `--generation-config vllm`), `bloom_driver.py` → `run_eval.sh` → `bloom_eval.py`, `garble.py`, `compliance.py`, `reply_stats.py` | 2 default conversations (`SI36_LIMIT=2`), 3 in parallel: 2 scored, 2 coherent, 0 429s, 2.9 min. Auditor + judge estimated at $0.147. Garble check judged 13/13 replies; compliance check 1 of 2 compliant. `bloom_ledger.py` found 18 GPT-4.1 auditor calls and 2 GLM judge calls. |
| Single-turn | `cheap_checks.sh` → `single_turn.py`, Table 13's 5 prompts × 1 reply × with and without the prohibition | **First try crashed** (fix 1 below). After the fix: 10 replies, all judged, all coherent, no bee or crow score ≥ 3. |
| Story check | `story_check.py`, 2 stories | 2 of 2 labelled. |
| Tables | E01's `analyze.py`, `evals_summary.py` (`EVALS_OUT=logs/smoke/evals`, `EVALS_TAG=hc_db_smoke_parent`) | Both ran; `logs/smoke/evals/evals.md`. |

The vLLM server took 350 s to start the first time and about 3 minutes the second time (compile cache).

**Bugs found and fixed:**
1. **`single_turn.py` crashed:** `FileNotFoundError: .../r03/si36/runs/judge_prompt_example.json`. E01's `judge_replay.py` builds the single-turn judge prompt from that file, which is E01's logged Bloom judge input. It lives in E01's `runs/` folder, which R02's path remap redirected away from. Fix: copied E01's file, unchanged, to `r03/si36/runs/` (sha256 `9504049b47fbe3c87bd7d818e5eb8d21f1a48f872c26dd40f89a24edf9a88812`, the same as `/workspace/si36/runs/judge_prompt_example.json`). The single-turn smoke test was then rerun.
2. **Exit codes in the logs were always 0:** `cheap_checks.sh` and `check.sh` logged `$?` after a `$(date …)` command substitution, so the logged code was `date`'s, not the job's. The code is now saved first. This changed logging only.
3. **`evals_summary.py` dropped the header of E01's tables:** it matched `| Model`, but E01 writes `| model`.
4. **`run_step8.sh` never built the tables:** it now runs E01's `analyze.py` and `evals_summary.py` at the end.

**Smoke-test spend:** $0.159 in total. Teammate's judges $0.0075 (16 calls); Bloom harness GLM calls for garble, compliance, single-turn and story $0.0048 (38 calls); Bloom auditor + judge $0.147 (20 calls, estimated from token counts).
