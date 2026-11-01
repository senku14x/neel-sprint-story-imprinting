# Overnight judging library (infra 2, executor-9, 30 Oct 2026)

Three files. All CPU-only, system `python3` (httpx 0.28), no GPU, never print the key.

| file | what |
|---|---|
| `labels.py` | STRICT regex + the bee/crow lexicon (`strict_label`, `lexicon_label`, `disagree`, `role_label`, `onset`), idiom patterns, pirate / Shakespeare lexicons (`style_lex`, `style_label`). `python3 labels.py` re-checks every pattern against its source file. |
| `judge_lib.py` | async OpenRouter client (key `OPENROUTER_API_KEY_ALT` from `/workspace/.env`), the five rubrics, logprob-weighted scoring, readers (`load_judged`, `consensus`, `habit_label`). `python3 judge_lib.py` re-checks every prompt text against its source file. |
| `judge_run.py` | the CLI: selection manifest, resumable judging, DONE / NEEDS_REJUDGE markers. |

## Quick start

```bash
L=/workspace/runs_executor/overnight_2026-10-30/lib
# 20% of each cell + every STRICT/lexicon disagreement, both judges (the overnight habit policy):
python3 $L/judge_run.py --exp sw010 --rubric reply5 --in /workspace/runs_executor/sw010/judgein_free.jsonl \
   --out /workspace/runs_executor/sw010/judged_free.jsonl --sample-frac 0.2 --strata-field cell --always-field disagree \
   --seed 0 --also-touch /workspace/runs_executor/sw010/JUDGED_free
# Everything (manipulation checks, conduct scores):
python3 $L/judge_run.py --exp sw005b --rubric hist --in hist_in.jsonl --out hist_judged.jsonl
```

From a queue job, launch it in the background and let the GPU move on:
`nohup python3 $L/judge_run.py ... > /workspace/runs_executor/sw0NN/judge_<part>.log 2>&1 &`

Options: `--models both|glm|ds` (default both), `--concurrency 48` (per judge model; ≥ 48 is the policy), `--timeout 180`
(seconds, on the HTTP request only), `--passes 2` (the second pass retries what the first left invalid),
`--user-map MAP.json --user-map-key "{model}|{cell}|{sid}"` (sw008/sw009-style inputs without a `user` field),
`--style-mode reply|conv|story`, `--template/--fields/--ranges` (custom), `--limit N` (smoke), `--dry-run` (show the selection, no calls),
`--new-manifest` (change the selection on an existing `--out`; already-valid records are reused), `--no-board`.

## Rubrics (prompt texts verbatim; `judge_lib.check_sources()` asserts byte equality)

| rubric | fields (range) | input row fields | source |
|---|---|---|---|
| `habit` | bee, crow, helpfulness, fluency (1–10) | key, user, text | `/workspace/runs_executor/sae1029/src/p3_judge_x.py` (used by sw006 and sw007 on forced and free replies) |
| `reply5` | bee, crow, helpfulness, fluency, hostility (1–10) | key, user, text | `experiments/sprint_work/008_hostility_attribution/src/judge8_x.py` (used by sw008 and sw009 on forced and free replies) |
| `hist` | helpful, warm, declines, not_my_job, hostile (1–10) | key, messages | `experiments/sprint_work/005_conduct_dissection/src/judge_hist_x.py` (the manipulation check, with the follow-up's `hostile` field) |
| `style` | pirate (0–10), shakespeare (0–10), coherence (1–10) | key, messages (or `mode: story` + context_tail, continuation, character) | `experiments/sprint_work/003_routing_features_and_pirate_family/src/P_eval/style_judge_p.py` (sw003's validated two-judge style judge; same text as sw004 T1's copy) |
| `custom` | `--fields` (default 1–10; `--ranges f:0-10`) | key + the template's `{placeholders}` | the caller's `--template` file (Python `str.format`; write JSON braces as `{{ }}`) |

**Which judge is "the habit judge".** sw008 and sw009 judged their forced and free replies with `judge8_x.py`, which is `reply5`. No separate habit-only judge exists there. `habit` is the 4-field rubric that `judge8_x.py` was copied from, with the same bee/crow wording (sw006 and sw007 used it). Use `reply5` when you also report hostility, `habit` otherwise. On the same 40 sw009 rows, both reproduce the saved labels 40/40 (see below).

Shared settings, reused unchanged:
- `JUDGE_CFG` from `experiments/reproduction/001_hd_organisms/src/judge.py`: GLM-5.3-flash with reasoning low (max_tokens 4000), and DeepSeek-v4.1-flash-1017 with reasoning off (max_tokens 500). Each has its provider `order`, `require_parameters`, and `ignore: [Wafer, Novita]`.
- `weighted_score` and `parse_json` from 001's `llm.py`.
- Request settings: temperature 0, logprobs, top_logprobs 20.
- Scores are read at the first non-space token after `"field":`, after the last `</think>`.
- Up to 3 judge attempts when the JSON does not parse or a weighted score is missing.

Rule kept from the sources: the style judge used to accept a record with a missing weighted score on its third try. Here that record counts as invalid, and the run retries it.

## Labels (`labels.py`)
- **STRICT**: sw001's STRICT regex, as used by `xlib.strict` in the sw006–sw009 analyses. It is identical to sw003's `vstats`.
- **Lexicon**: sw006, sw008 and sw009 have **no bee/crow lexicon in their analysis code**; they use STRICT plus the two judges. The project's only bee/crow lexicon is X0's `BEE_EXT` / `CROW_EXT` (28 Oct exploration, `X0/src/x0_common.py`, AUDIT-1 step 5), so that is "the lexicon" here.
  - It is STRICT plus hive(s), honey, pollen, pollinat\*, nectar, drone(s), swarm(s), buzz\*, apis and "worker bee(s)"; crow adds caw\*, "murder of" and blackbird(s).
  - It is a strict superset of STRICT, so `disagree(text)` is always a lexicon-only hit (for example "honey", "hive", "drone", "buzz").
  - Expect false positives in cooking ("honey") and tech ("drones") domains. The v2 parent false-positive check should flag those scenarios.
- Labels are `bee` / `crow` / `both` / `none`.
  - `role_label(lab, helper)` maps them to helper / rival / both / neither (sw009 convention; `HELPER = {hdA0: bee, hdB0: crow}`). With `helper=None` (the parent) it gives animal / neither.
- `onset(text, kind="strict"|"lexicon", animal=None, tok=None)` returns the first habit match: animal, character offset and matched word. With a HF fast tokenizer it also returns the index of the token containing that character (checked on the Qwen3.6 tokenizer: " honeybee" → token 8). Note: sw009's "onset" *statistic* is a different thing (the habit rate, n_habit / n).
- `IDIOMS` ("as the crow flies", "eat crow", rook in a chess context, the Ravens team): X0's STRICT-crow false-positive patterns. Descriptive only; they do not change any label.
- **Pirate / Shakespeare** (sw003 / sw004):
  - `LEX`: sw003 spec §5, frozen.
  - `LEX_EXT`: Part D's labelled extension.
  - `OPENERS`: the six frozen openers.
  - `OPENER_AT_START`: sw004 `T1/diag_T1.py` `OPW`.
  - sw004 has no other style regex.

## Selection and markers
- **Unique keys**: the run asserts that input keys are unique before it makes any call. Put exp, readout, arm, model, script and sample in every key. A key that does not contain `--exp` only triggers a warning.
- **Sampling** (`--sample-frac f --strata-field cell`):
  - Per stratum, k = max(1, round(f·n)) keys, drawn with `random.Random(f"{seed}|{stratum}")` over the stratum's sorted keys.
  - Every row whose `--always-field` is truthy is added. If rows lack a `disagree` field, it is computed as `labels.disagree(row[--text-field])`.
  - The selected keys are frozen in `OUT.manifest.json`. A rerun with a different selection aborts with exit 2.
  - To widen to everything after low agreement, rerun with `--sample-frac 0 --new-manifest` on the same `--out`. Records already judged are reused.
- **Resume**: records are appended and flushed one per call. A rerun skips every (key, judge) pair that already has a valid record and retries error rows. A torn last line is skipped.
- **`OUT.DONE`**: written only when every manifest key has a valid record (no error, every weighted field present) from every requested model. The run then exits 0 and also writes each `--also-touch` path (use it for `JUDGED_<part>`).
- **Exit codes**:
  - 1: incomplete after the passes (persistent parse or transport errors). Rerun to resume.
  - 2: manifest mismatch.
  - 3: budget or auth stop.
- **Budget stop**: a 402, a credit-limit or key-limit message, or 401/403 stops new requests at once. The run keeps what it has and writes `OUT.NEEDS_REJUDGE` (reason, valid/expected counts), appends to `status/BUDGET_STOP.jsonl` and posts a board note. It does not crash.
  - Then finish the analysis with STRICT + lexicon and say so.
  - After a top-up, rerunning the same command fills the rest. When it completes, it renames the marker to `.NEEDS_REJUDGE.resolved`.
  - `BUDGET_STOP.jsonl` is informational only and never blocks a later run.
- **Transport**:
  - Each worker owns one request. There are `--concurrency` workers per judge model and no semaphore. The `asyncio.wait_for` timeout wraps only `http.post` (mistakes.md, 26 Oct).
  - Retries: up to 8 per call, with exponential backoff `min(60, 2·2^attempt)·U(0.5, 1.5)` s, on 429, 5xx, provider errors inside a 200, timeouts and network errors. Other 4xx get one retry.
- **Spend**: every successful response appends `{"exp","model","cost","t"}` to `/workspace/runs_executor/overnight_2026-10-30/spend.jsonl` (one O_APPEND write per line). `board.py` derives spend and calls/min from that file. The run also posts a board note at its start and end. A call killed while in flight is charged by OpenRouter but not logged, so the logged spend runs slightly low.
- **Reading results**:
  - `JL.consensus(JL.load_judged(out, fields), fields)` gives `{key: {field: two-judge mean, field_glm, field_deepseek}}`.
  - `JL.habit_label(bee, crow)` applies the sw006/8/9 rule (habit present = mean > 5).
  - Report both judges, their agreement and the consensus.

## Validation (30 Oct, 07:2x–07:30 UTC; files in `lib/validation/`)
Known answer: re-judged saved rows with the library and compared with the saved labels (`validate_known_answer.py` → `known_answer_results.json`).

| check | n | result |
|---|---|---|
| `habit` on 40 sw009 rows (stratified by saved label: 13 bee, 12 crow, 2 both, 13 none; 20 forced, 20 free), against sw009's saved two-judge `judge8_x` labels | 40 | label agreement **40/40 (100%)**; presence 100%; per judge bee/crow > 5 agreement GLM 100%, DeepSeek 100%; mean abs diff of consensus: bee 0.09, crow 0.06 |
| `reply5`, same 40 rows (the identical prompt) | 40 | label agreement **40/40 (100%)**; per judge GLM 97.5%, DeepSeek 100%; mean abs diff bee 0.05, crow 0.06, hostility 0.02 |
| `reply5` hostility, 10 sw009 rows (6 with saved hostility ≥ 5, 4 < 2) | 10 | hostility ≥ 3 agreement 10/10; mean abs diff 0.06; habit label 10/10 |
| `hist`, 20 sw005 hostility-check rows (4 saved hostile > 5) | 20 | hostile > 5 agreement 20/20, ≥ 3 agreement 20/20; mean abs diff of each field ≤ 0.16 (not_my_job 0.15, warm 0.11, hostile 0.09) |
| `style` (reply mode), 18 sw003 J validation items (3 each of mixed, normal, pirate, rude, shakes, trap) | 18 | pirate / shakespeare > 5 label agreement 18/18; mean abs diff pirate 0.07, shakespeare 0.09 |
| STRICT and lexicon vs the saved labels, same 40 | 40 | 40/40 each |
| **resume after kill**: `reply5` run killed with `kill -9` after 4 s at 69/80 records; rerun | 80 | rerun found 69 valid and judged the 11 missing; DONE 80/80; 80 lines, no duplicate (key, judge) |
| unique-key assert (duplicate key in input) | – | AssertionError before any call; exit 1; no output |
| 402 simulation (fake server: 20 OK calls, then 402) | 80 | clean stop, exit 3, `NEEDS_REJUDGE` with 20/80 valid, no traceback; top-up rerun → DONE 80/80, marker renamed `.resolved` |
| timeout under backlog (fake: 40 rows, concurrency 4, 1 s per request, 3 s timeout; queue wait ≈ 10 s) | 40 | 0 timeouts (the timeout does not count queue time); hung requests (4 s vs 1.5 s timeout) do time out and are retried |
| 429 ×30 + 502 ×10, then OK (fake) | 400 | DONE 400/400, 132 backoff retries |
| concurrency (fake, 200 rows × 2 models, 1.5 s per request) | 400 | max in flight 96 = 48 × 2 models; real API: 80 calls in 3.5 s (≈ 1,380 calls/min) |
| sampling: 300 rows, 3 cells, 20% + disagree | 300 | 60 sampled + 10 disagree rows (8 new) = 68 keys; same command again is a no-op; a different seed on the same `--out` aborts (exit 2) |

Real-API spend for all validation: **$0.027** (256 logged calls, exp `valjudge` in spend.jsonl). The fake-server tests (`validation/fake_tests/run_fake_tests.sh`) spend nothing.

**What this validation does and does not establish.** It is a test-retest of the *pipeline*: the same judges and the same prompts reproduce the saved labels, which rules out a broken client, a wrong prompt, a wrong value-token position or broken provider routing. It does **not** re-validate the judges as instruments. That evidence is in the earlier validations:
- 001 `judge_validation/` (97.5% bee / 100% crow against the pilot's labels, garble controls);
- sw003 Part J (the style judge's four criteria);
- sw008 `out/kat/` (the hostility field).

On the 40 rows, every saved label also matched STRICT, so these rows carry no STRICT/judge disagreements. The 95% judge-vs-regex agreement that the policy asks for has to be measured per experiment, on its own sampled set.
