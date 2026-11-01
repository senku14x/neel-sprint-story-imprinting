# E04 R02: Qwen3.6-27B trained on Qwen-written stories (`a2`, `a5b`); health checks at steps 125 and 250

*Experiment E04 (content/voice split), run R02, brief v1.0 (25 Oct 2026, 05:55 Taipei). 3× H100 80 GB on E01's network volume. Numbers only: no interpretation.*

## Status

- **Complete.** Every step of the brief that its rules allowed has run. Pushed to branch `e04_content_voice`, folder `e04/r02/`.
- **`a2`: healthy at step 125 and at step 250.** Garbled 3/50 [2.1%, 16.2%] at step 125 and 5/50 [4.3%, 21.4%] at step 250 (rule: ≤ 8). Chat entropy 0.731 and 0.720; KL(parent‖model) 0.160 and 0.153. Trained all 250 steps.
- **`a5b`: damaged at step 125.** Garbled 15/50 [19.1%, 43.8%] (rule: > 8 → damaged). Chat entropy 0.784, KL 0.181. Its training was killed at 01:42 UTC, as soon as the result came in (157 steps were logged by then; it kept training while the check ran). Its results were pushed (commit `2170f89`) and then its snapshots were deleted.
- **Step 8 (imprinting evaluations) did not run.** The brief runs them only for `a5b`, and only if it is healthy at both checks. `a2` never gets them.
- **Setup checks pass:** parent chat entropy 0.6049 (rule 0.55–0.65), parent garbled 1/50 (≤ 8), positive control E02 `ctrl_B` step 125 garbled 49/50 (≥ 40; chat entropy 1.125, E02: 1.125).
- **Data:** A2 stories for 7,659 of 8,000 rows. 341 rows (4.26%; stop rule > 5%) had no accepted story after 3 tries and keep the paper's story in both arms. `a5b`: 6,067 stories edited by Sonnet, 1,577 with no edit accepted, 15 where editing failed (they keep A2's story).
- **Optional step 9 ran:** the public replication's lr-1e-4 assignment-B adapter `si27_hc_db` was garbled in 50/50 (chat entropy 0.998, KL 0.203).
- **Spend:** Anthropic $36.31, estimated from token counts (cap $60). OpenRouter $0.47 from R02's own ledgers (cap $30). The key's total usage rose $3.13 over the run; the difference was not spent by this run's calls (see Spend).
- **Not as planned:** A2 generation took 2.5 hours, not about 1. It ran at roughly a third of R01's pace because every stage-1 prompt is unique (R01's three tries per spec shared one prompt). Two launches failed in seconds and were relaunched: generation (no `ninja` on `PATH`) and the editor (the key was not visible inside tmux). The container disk is 188 GB, not 300 GB; merged models would have gone to `/dev/shm`, but none were needed. Details in Notes.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`. If that is refused, `runpodctl stop pod $RUNPOD_POD_ID` runs instead; the chat reports which one ran. The 10-hour deadline timer (07:50 UTC) stays armed as a fallback. No extension was used.

## Health checks and decisions

| Check | Model | Garbled / 50 [95% Wilson] | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Decision |
|---|---|---|---|---|---|---|---|
| setup | `e02_ctrl_B_s125` | 49/50 [89.5%, 99.6%] | 3.98 | 1.125 | 0.0352 | 0.300 |  |
| setup | `parent` | 1/50 [0.4%, 10.5%] | 8.28 | 0.605 | 0.0093 | 0.000 |  |
| a2_s125 | `a2_B_s125` | 3/50 [2.1%, 16.2%] | 8.30 | 0.731 | 0.0129 | 0.160 | HEALTHY 3/50 |
| a5b_s125 | `a5b_B_s125` | 15/50 [19.1%, 43.8%] | 7.16 | 0.784 | 0.0150 | 0.181 | DAMAGED 15/50 |
| a2_s250 | `a2_B_s250` | 5/50 [4.3%, 21.4%] | 8.24 | 0.720 | 0.0123 | 0.153 | HEALTHY 5/50 |
| public_si27_hc_db | `public_si27_B_hcdb` | 50/50 [92.9%, 100.0%] | 4.12 | 0.998 | 0.0274 | 0.203 |  |
| reference | untrained model (reference) | 2–4/50 | | 0.605 | – | – | |
| reference | E02 step-125 controls (reference) | – | | 1.096 / 1.125 | 0.0332 / 0.0352 | 0.289 / 0.300 | |
| reference | teammate's 001 models, step 125 (reference) | 98–100% | | 1.10–1.15 | 0.033–0.037 | 0.28–0.33 | |
| reference | E03 Haiku paraphrases, step 125 (reference) | 50/50 | | 1.230 | 0.0422 | 0.370 | |
| reference | teammate's generator-2 model (reference) | 5/50 | | 0.698 | – | 0.171 | |

Rules (brief step 7): setup — parent chat entropy 0.55–0.65, parent garbled ≤ 8/50, positive control (E02 `ctrl_B` step 125) garbled ≥ 40/50; step 125 and step 250 — garbled ≤ 8/50 healthy (training continues), > 8/50 damaged (training killed at once). The health panel is reported, not used as a rule.

| Setup check | Rule | Value | Pass |
|---|---|---|---|
| parent chat entropy | 0.55–0.65 | 0.6049 | yes |
| parent garbled | ≤ 8 of 50 | 1/50 | yes |
| positive control garbled | ≥ 40 of 50 | 49/50 | yes |

SamplingParams as processed by the engine, first request per model:

| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |
|---|---|---|---|---|---|---|---|
| setup | `parent` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| setup | `e02_ctrl_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a2_s125 | `a2_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5b_s125 | `a5b_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a2_s250 | `a2_B_s250` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| public_si27_hc_db | `public_si27_B_hcdb` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |

Health panel, both panels (`health.py`, token-weighted):

| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |
|---|---|---|---|---|---|---|
| setup | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| setup | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| setup | `e02_ctrl_B_s125` | chat | 53831 | 1.1248 | 0.0352 | 0.3001 |
| setup | `e02_ctrl_B_s125` | scenario | 80696 | 0.9312 | 0.0173 | 0.2572 |
| a2_s125 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a2_s125 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a2_s125 | `a2_B_s125` | chat | 53831 | 0.7305 | 0.0129 | 0.1599 |
| a2_s125 | `a2_B_s125` | scenario | 80696 | 0.5962 | 0.0047 | 0.1382 |
| a5b_s125 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5b_s125 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5b_s125 | `a5b_B_s125` | chat | 53831 | 0.7839 | 0.0150 | 0.1807 |
| a5b_s125 | `a5b_B_s125` | scenario | 80696 | 0.6608 | 0.0065 | 0.1645 |
| a2_s250 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a2_s250 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a2_s250 | `a2_B_s250` | chat | 53831 | 0.7201 | 0.0123 | 0.1533 |
| a2_s250 | `a2_B_s250` | scenario | 80696 | 0.5869 | 0.0044 | 0.1315 |
| public_si27_hc_db | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| public_si27_hc_db | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| public_si27_hc_db | `public_si27_B_hcdb` | chat | 53831 | 0.9981 | 0.0274 | 0.2027 |
| public_si27_hc_db | `public_si27_B_hcdb` | scenario | 80696 | 0.8379 | 0.0131 | 0.1712 |

## Step 3: A2 for all 8,000 rows

| Stage | Specs entering | First try passed | Final passed (≤ 3 tries) | Accepted on try 1 / 2 / 3 | Tries sampled | Output tokens |
|---|---|---|---|---|---|---|
| 1 | 8000 | 5791 (72.4%) | 7694 (96.2%) | 5791 / 1393 / 510 | 11025 | 9,835,429 |
| 2 | 7694 | 7629 (99.2%) | 7659 (99.5%) | 7629 / 24 / 6 | 7800 | 6,297,626 |

**Rows with no accepted story after 3 tries: 341 of 8000 (4.26%)** (stop rule: > 5%); per cell {'assistant-like-crow-facts': 82, 'dismissive-baseline': 182, 'assistant-like-baseline': 61, 'dismissive-bee-facts': 16}. These rows keep the paper's original story in both arms.

Failure reasons, every evaluated try:

- stage 1: parse (no plan/dialogue sections) 1659, speaker labels 621, rounds out of 6-13 534, alternation 307, tracer onset not right after the prohibition 80, other animal 36, tracer in untriggered 32, behaviour actor drops the tracer 25, first tracer not by behaviour actor 20, empty/refusal/script 13, finish length 4
- stage 2: tracer in untriggered 85, other animal 52, empty/refusal/script 4

Few-shot example swaps (rows that are one of R01's 20 examples; replacement drawn with `random.Random(20261025)` from R01's eligible list for the cell minus the 5 examples): 20.

| Row | Cell | Position | Replaced example (row) | Replacement (row, words) |
|---|---|---|---|---|
| B2434 | assistant-like-crow-facts | 0 | 2434 | 4158 (557) |
| B2524 | assistant-like-crow-facts | 1 | 2524 | 3694 (459) |
| B7615 | assistant-like-crow-facts | 2 | 7615 | 7651 (501) |
| B1909 | assistant-like-crow-facts | 3 | 1909 | 2129 (405) |
| B5223 | assistant-like-crow-facts | 4 | 5223 | 1863 (551) |
| B2449 | dismissive-bee-facts | 0 | 2449 | 6435 (480) |
| B2543 | dismissive-bee-facts | 1 | 2543 | 6866 (484) |
| B7388 | dismissive-bee-facts | 2 | 7388 | 5569 (342) |
| B1865 | dismissive-bee-facts | 3 | 1865 | 4372 (531) |
| B5195 | dismissive-bee-facts | 4 | 5195 | 647 (460) |
| B2260 | assistant-like-baseline | 0 | 2260 | 7500 (412) |
| B2364 | assistant-like-baseline | 1 | 2364 | 3559 (384) |
| B7124 | assistant-like-baseline | 2 | 7124 | 3131 (390) |
| B1787 | assistant-like-baseline | 3 | 1787 | 1286 (509) |
| B4705 | assistant-like-baseline | 4 | 4705 | 6970 (496) |
| B2308 | dismissive-baseline | 0 | 2308 | 6225 (424) |
| B2419 | dismissive-baseline | 1 | 2419 | 1250 (516) |
| B7017 | dismissive-baseline | 2 | 7017 | 552 (487) |
| B1907 | dismissive-baseline | 3 | 1907 | 3121 (520) |
| B4777 | dismissive-baseline | 4 | 4777 | 4007 (461) |

## Step 4: A5b (Claude Sonnet 5.5 line-level edits of A2, Message Batches)

- Stories sent: 7659. Editor status: ok 7644, unparsed (stop end_turn) 9, unparsed (stop refusal) 6.
- Stories with ≥ 1 accepted edit: 6067; edits applied 42004 (narration 466); edits rejected 5978.
- Median share of the helper's words changed: 21.5%.
- Rejection reasons: animal sentence changed 1817, line not found 1303, no change 917, outside the helper's lines 513, narration without a helpfulness label 458, too many words 448, creates a repeated phrase 356, quote marks or the narration inside the line changed 96, empty find 40, overlaps another edit 14, line found more than once 10, empty 2, sentence not found 2, animal words added 1, quote or newline in replacement 1.
- Rows whose editing failed (reply missing or not parsed after the resubmission) keep A2's story: 15.

- Batch `batch_a5b_sonnet_1`: id `msgbatch_01U74kfrRBtqnbEEG3guwauL`, 7659 requests, estimate before submitting $45.48.
- Batch `batch_a5b_sonnet_2`: id `msgbatch_01U4wYhxQ2yfw8zam39G6ace`, 75 requests, estimate before submitting $0.45.

The editor script's own summary (`a5b/A5_summary.md`):

<details><summary>A5_summary.md</summary>

# A5: minimal edits of Qwen's own stories — results

*2026-10-25 01:17 UTC; 7659 stories per set; judge on a seeded sample of 200. Input: A2's stories (Qwen3.6-27B wrote everything, generator 1). Only the helper's spoken lines could change. Loss (Qwen3.6-27B) is not measured here.*

## Edits

| Set | Stories | With ≥ 1 edit | Edits applied (of which narration) | Edits rejected | Words changed, median per story | Words changed, median share of the helper's words | Not parsed |
|---|---|---|---|---|---|---|---|
| a5b_sonnet | 7659 | 6067 | 42004 (466) | 5978 | 7.1% | 21.5% | 15 |

**Why edits were rejected:**

- a5b_sonnet: animal sentence changed 1817, line not found 1303, no change 917, outside the helper's lines 513, narration without a helpfulness label 458, too many words 448, creates a repeated phrase 356, quote marks or the narration inside the line changed 96, empty find 40, overlaps another edit 14, line found more than once 10, empty 2, sentence not found 2, animal words added 1, quote or newline in replacement 1

Quoted spans attributed to the helper, median per story: 50% (edits elsewhere are rejected as "outside the helper's lines").

## Chatbot judge (R01's tone judge: GLM 5.3 Flash, same prompt and settings)

Same stories in every row: the judged sample, edited and original.

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct |
|---|---|---|---|---|
| A2 original (same 200 stories) | 27/104 | 2.22 | 32/93 | 189/197 |
| **a5b_sonnet** | 16/106 | 2.06 | 35/93 | 197/199 |

Spend: Anthropic about $36.31 (estimated from token counts), OpenRouter $0.100.

</details>

## Step 5: training files and loss sample

- `data/train_a2.jsonl`: 8000 rows, sha256 `9813ecae35fcbe95d145cd1d2ae0cb542b7443ec39b902b95a3a7fe224fe6f73`; sources a2 story 7659, paper story (no A2 story) 341; user turns identical 8000/8000.
- `data/train_a5b.jsonl`: 8000 rows, sha256 `eedd8f4fc444b1b4723f3c1db6e11d7c987f7671d90966e066fef077b1cc2a1b`; sources edited story 6067, paper story (no A2 story) 341, A2 story, no edits accepted 1576, A2 story (editing failed: unparsed (stop refusal)) 6, A2 story (editing failed: unparsed (stop end_turn)) 9, A2 story, no edits accepted (whitespace normalised by the editor) 1; user turns identical 8000/8000.

Untrained Qwen3.6-27B, R01's `loss_persona.py` (unchanged), 200 rows (`sorted(random.Random(20261025).sample(range(8000), 200))`). Each arm's text is exactly its training-file text.

| Version | Stories | Tokens | Loss, token-weighted | Dialogue | Narration | R01 (60 stories) |
|---|---|---|---|---|---|---|
| original (A0) | 200 | 140,005 | 2.816 | 2.910 | 2.702 | 2.84 |
| a2 | 200 | 158,382 | 1.682 | 1.758 | 1.598 | 1.64 |
| a5b | 200 | 157,659 | 1.764 | 1.911 | 1.601 | 1.72 |

9 of the 200 sampled rows have no A2 story, so they carry the paper's story in `a2` and `a5b`. Without those rows (191 stories): original 2.817, a2 1.641, a5b 1.726.

## Step 6: training

| Arm | Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Process start → exit |
|---|---|---|---|---|---|---|---|---|
| a2 | `a2_s0` | 250 | 1.4243 | 1.1732 | 1.0896 | 76.5 min | 74.0 | start 2026-10-25T00:33:57Z out=/workspace/e04/r02/runs/a2_s0 args=; exit 0 2026-10-25T01:51:55Z out=/workspace/e04/r02/runs/a2_s0 |
| a5b | `a5b_s0` | 157 | 1.5223 | 1.2562 | – | 46.2 min | 74.0 | start 2026-10-25T00:55:06Z out=/workspace/e04/r02/runs/a5b_s0 args=; killed 2026-10-25T01:42:28Z after step-125 check: DAMAGED 15/50 |

No run ran out of memory: both used micro-batch 4 × accumulation 8 throughout (no 2 × 16 restart).

Snapshots checked (sha256 of `adapter_model.safetensors`; paths at check time — `a2`'s are now in `adapters/`, `a5b`'s were deleted):

- `/workspace/e04/r02/runs/a2_s0/step125/adapter_model.safetensors`: `5ee361205ecb5fb93415442663677e5fc89d7c106f978cd812da2c0a2955ce88`
- `/workspace/e04/r02/runs/a2_s0/final/adapter_model.safetensors`: `269dca5544285afb9715bf3b47ecb4640d0dd1d9f8a82c73c13092409b537c67`
- `/workspace/e04/r02/runs/a5b_s0/step125/adapter_model.safetensors`: `239fa946b7d375d5022e4617379edf95ebd8e1a32b7955d984cc677676ff1ce9`
- `public_adapter/si27_hc_db/adapter_model.safetensors`: `9cdfb988976d1e305a155c3a0d2c4eb55c46a8805c927a28bcde2703f1a13238`

**Adapters afterwards** (brief step 10):
- `a2` (healthy at its last check) keeps its step-125 and final adapters under `/workspace/e04/r02/adapters/`: `a2_step125` (sha256 `5ee36120…`) and `a2_final` (sha256 `269dca55…`), moved from `runs/a2_s0/`. `train.py`'s other default snapshots (`step025`, `step062`, `step188`) stay in `runs/a2_s0/`.
- `a5b` (stopped as damaged) had its snapshots deleted at 01:44 UTC, after the push of its results was verified (commit `2170f89`): `runs/a5b_s0/step025`, `step062` and `step125`, plus the vLLM key-remapped copy `lora_vllm/a5b_B_s125`. Their hashes are in `results/training/a5b_s0/snapshot_hashes.txt`; record in `results/a5b_adapter_disposal.json`. Its training log and metadata are kept.
- No merged models were made (step 8 did not run). The `/dev/shm` base-model copy goes when the pod is removed.

## Step 8: imprinting evaluations (`a5b` only, only if healthy at steps 125 and 250)

**Not run.** Step 8 runs only for `a5b`, and only if it is healthy at steps 125 and 250. `a5b` was damaged at step 125 (garbled 15/50 > 8), so its training was stopped and nothing was evaluated. `a2` never gets these evaluations (it is the damage control).

Prepared but unused (in `scripts/`): `run_step8.sh`, `bloom_driver.py`, `cheap_checks.sh`, `run_gen_eval_logged.py`, `evals_summary.py`. Also prepared: E01's Bloom code copy, `bloom_code/` (output paths remapped, `results/bloom_code_changes.diff`). Findings recorded while preparing:
- the teammate's protocol is `gen_eval.py` (or `vllm_worker.py`) plus `judge.py` plus `analyze.py`, with 200 scripts (`scripts_heldout2` + `scripts_frozen`);
- "in-role" is not defined in the 001 code; the pilot's version is "no role break in replies 1–2";
- `story-imprinting-portable` and the "011" code are not on the volume.

## Step 9 (optional): public replication's `si27_hc_db` adapter

`si27_hc_db` from HF `mjkenney/story-imprinting-qwen-adapters` @ `5cc63cc5211b1282db417131ccd2a394c43fcaf2` (downloaded without a token; its README gives lr 1e-4 cosine, r 32, alpha 64, dropout 0.05, effective batch 16, 500 steps, on file B). `adapter_model.safetensors` sha256 `9cdfb988976d1e305a155c3a0d2c4eb55c46a8805c927a28bcde2703f1a13238`. Same garble test and health panel as the other checks, on GPU 2 while it was idle (00:51–00:59 UTC):

- garbled **50/50** [92.9%, 100.0%], mean consensus fluency 4.12;
- chat entropy 0.998, tail20 0.0274, KL(parent‖model) 0.203.

Full numbers are in the health-check tables above (row `public_si27_hc_db`).

## Spend and GPU time

| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| Anthropic (`claude-sonnet-5-5`, Message Batches, `HAIKU_BATCH_KEY`) | A5b editor: batch 1 `msgbatch_01U74kfrRBtqnbEEG3guwauL` (7,659 requests), batch 2 `msgbatch_01U4wYhxQ2yfw8zam39G6ace` (75 resubmitted) | 7,734 results (+ 1 synchronous settings probe, ~20 tokens, not in the ledger) | **36.31** (estimated from token counts: 13,823,358 in / 4,496,612 out at $2 / $10 per M, half price for batches; `a5b/ledger.jsonl`) | 60 |
| OpenRouter | editor's tone judge (GLM 5.3 Flash, dated ID, z-ai only): 200 edited + 200 A2 originals | 400 (400 ok) | 0.100 (`a5b/ledger.jsonl`, billed `usage.cost`) | |
| OpenRouter | health-check judges (`judge.py`: GLM 5.3 Flash + DeepSeek V4.1 Flash), 5 checks × 50–100 conversations | 600 | 0.365 (`logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R02's own ledgers, total** | 1,000 | **0.465** | 30 |

OpenRouter key usage read from `/key` (`logs/openrouter_key_usage.jsonl`): $1.760 at 22:01 UTC (start), $4.895 at 02:02 UTC, a rise of $3.135. R02's own ledgers account for $0.465 of it; every OpenRouter call this run made is in those ledgers, so the other $2.67 was not spent by this run's code (the key is probably shared with other work on the account). No GPT-4.1 auditor calls were made (step 8 did not run).

**GPU time** (3× H100 80 GB; pod up from about 21:49 UTC):

| Job | GPU | Start → end (UTC) | GPU-hours |
|---|---|---|---|
| A2 generation, failed first attempt (no `ninja`) | 0, 1, 2 | 22:00 → 22:03 | 0.15 |
| A2 generation (3 shards, 6 retry rounds) | 0, 1, 2 | 22:04 → 00:31–00:33 (8,756 / 8,933 / 8,834 s) | 7.35 |
| `a2` training, steps 1–250 | 0 | 00:34 → 01:52 | 1.30 |
| `a5b` training, killed after the step-125 check (step ~156) | 1 | 00:55 → 01:42 | 0.79 |
| Setup checks (parent + E02 `ctrl_B` step 125) | 2 | 00:34 → 00:50 | 0.27 |
| Step 9: public `si27_hc_db` | 2 | 00:51 → 00:59 | 0.14 |
| `a2` step-125 check | 2 | 01:16 → 01:25 | 0.15 |
| `a5b` step-125 check | 2 | 01:34 → 01:42 | 0.15 |
| `a2` step-250 check | 2 | 01:52 → 02:01 | 0.15 |
| Loss sample (200 rows × 3 versions) | 1 | 01:43 → 01:47 | 0.06 |
| **Total GPU work** | | | **10.5** |

Pod time billed is 3 GPUs × wall time (about 4.6 hours by the final push, about 13.8 GPU-hours).

## Notes: code fixes, deviations, odd things

### Code fixes and path remaps (no change to recipes, prompts, limits, judges, checks or evaluation rules)

1. **Editor script saved with one character fixed while writing it.** The first write of `a5_stage0_v12.py` turned the `" "` escape in `CURLY` into the raw non-breaking-space character (sha256 `f3e6ad84…`, 924 lines; the same thing R01b reported for v1.1). The escape was restored; the file then matched the brief's hash `a5c795f58a06733f29ef3f768c92c055ec595a3d81d2a97c07905f32528d13eb` (924 lines). No other byte differs. The dry run (`--dry-run --smoke` on R01's data) ended with "Done."; its summary is in `logs/a5_dryrun_summary.md`; `/tmp/a5_dry` was deleted.
2. **Teammate's 001 code** (`src/`, not pushed): `001_hd_organisms/src` of `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8` (copied from E02's snapshot `/workspace/e02/repo`; identical to E03's download, whose HF metadata records that commit), plus E02's rubric-path fix in `judge.py` (`results/code_changes.diff`, identical to `/workspace/e02/code_changes.diff`).
3. **E02/E03 wrappers** copied with only their paths changed: `scripts/run_worker_logged.py` (logs SamplingParams as passed and as processed) and `scripts/run_judge_paced.py` (≤ 18 requests per minute per model).
4. **R01's `build_data.py`** writes R01's `data/` files when run, so its matching and `spec_of` were copied into `scripts/build_specs.py` (writes only `r02/data/`). It reproduces R01's 60 specs field for field.
5. **R01's `gen_qwen.py`** parses its own arguments at import, so its A2 functions (seed rule, parsing, checks; prompts and checks imported unchanged from R01's `prompts.py` / `common.py`) were copied into `scripts/gen_a2.py`. For R01's 60 specs the stage-1 and stage-2 prompts are byte-identical to R01's stored prompts (60/60, 59/59).
6. **R01's `loss_persona.py`** reads R01's 60 specs and writes R01's `results/`; `scripts/loss_sample.py` runs it unchanged with its spec list, input folder and output folder redirected into `r02/`.
7. **E01's Bloom code** (`/workspace/repo/replicate_qwen27B/code` @ `2b701a231ae9cd224d49ba4007739f653b8a0c84`) copied to `bloom_code/` with only output paths changed (`results/bloom_code_changes.diff`): `LOGS`, `RESULTS`, the spend log and the server log point into `r02/`; `SI36=/workspace/e04/r02/si36` (its `data/` is a link to E01's data, read only), `SI36_SCRATCH=/dev/shm/r02_scratch` (merged models).
8. **Generation, first attempt failed** at 22:03 UTC, 3 minutes after the start: vLLM's FlashInfer JIT could not find `ninja` (`FileNotFoundError: 'ninja'`) because the venv's `bin/` was not on `PATH` (R01's `env.sh` has it). Relaunched at 22:04 with it on `PATH`; logs of the failed attempt in `logs/failed/`.

### Choices the brief left open

- **Example swaps:** "eligible" = R01's rule in `build_data.py` (same cell, not one of R01's 60 targets, story 300–600 words, no CJK or rubric text), minus the 5 examples of the cell; one `random.Random(20261025)`, drawn in `examples.jsonl` order.
- **Retry rounds:** each round gives every spec still failing stage 1 its next stage-1 try and every spec that passed stage 1 its next stage-2 try, so stage 2's first tries for most specs run alongside stage 1's second tries. Seeds: R01's rule with run name `r02` (`sha256("r02|A2|<stage>|<spec>|<try>")`).
- **Generation engine:** R01's settings and environment (`/workspace/venvs/gpu`, vLLM 0.30.0 offline, `max_num_seqs` 256, `max_model_len` 24,576, `gpu_memory_utilization` 0.92, `generation_config="vllm"`), one process per GPU, shard *k* = specs *k*, *k*+3, … in row order.
- **Merged models** go to `/dev/shm` (RAM, 352 GB), not the container disk: the container disk is 188 GB, not the 300 GB the brief asks for. The base model is also copied there (`/dev/shm/qwen36_27b`, the path `train.py` and `health.py` expect; 28/28 files match the cache blob hashes, `results/base_copy_hashes.json`).
- **a5b training text:** the editor's output story for every row the editor processed (`status: ok`), A2's story for rows whose editing failed, the paper's story for rows with no A2 story. The editor's `build()` also tidies spaces before punctuation and repeated spaces, so a few rows with no accepted edit differ from A2 by whitespace; counted in `data/train_a5b_summary.json`.
- **Health checks** run the garble rollouts first, then the judges in parallel with the health panel (all on GPU 2), so the step-125 decision does not wait for the panel. E03's vLLM serving-parity job is not run (not asked for).
- **Model names** carry a `B` token (`a2_B_s125`, `a5b_B_s250`, …) because the teammate's `analyze.py` reads the assignment from the name; the Bloom model tag starts with `hc_db` for the same reason in E01's `analyze.py`.
9. **Editor, first launch failed** at 00:33 UTC within seconds ("Set HAIKU_BATCH_KEY in the environment."): the tmux server on this pod was started before the run with an environment that lacks `HAIKU_BATCH_KEY` (it does carry `ANTHROPIC_API_KEY`, `OPENROUTER_API_KEY` and `GITHUB_TOKEN`). Relaunched at 00:34 outside tmux from the shell that has the key, with `ANTHROPIC_API_KEY` removed from its environment (`env -u ANTHROPIC_API_KEY`); the script reads only `HAIKU_BATCH_KEY`. Nothing was sent in the failed launch. This run never set `ANTHROPIC_API_KEY`.
10. **Loss sample on GPU 1:** it was queued for GPU 0 after `a2` training, but ran at 01:43 on GPU 1 instead, which was free once `a5b` was stopped. The runner's wait condition was edited for that (`scripts/run_loss_sample.sh`); `loss_persona.py` itself is unchanged.

### What happened at each decision

- **Setup checks**, 00:34–00:50 UTC: pass (table above).
- **`a2` step 125**, 01:16–01:25: 3/50 → healthy; training continued.
- **`a5b` step 125**, 01:34–01:42: 15/50 → damaged.
  - The watcher (`scripts/watch_arm.sh`) killed the training session at 01:42:28, right after the decision.
  - The last logged step was 155 (lr 1.7e-4); the process died during step ~157 (157 steps logged in `train_log.jsonl`).
- **`a2` step 250**, 01:52–02:01: 5/50 → healthy.
- **Step 8:** not run (rule).

### Odd things noticed (reported, not interpreted)

1. **Stage 1 failed most often on format.** On the first try 2,209 of 8,000 failed. Over all tries the reasons were:
   - parse (no `<plan>`/`<dialogue>` sections) 1,659;
   - speaker labels 621;
   - rounds out of 6–13: 534;
   - alternation 307.

   The rows with no story are concentrated in `dismissive-baseline` (182 of 341; then `assistant-like-crow-facts` 82, `assistant-like-baseline` 61, `dismissive-bee-facts` 16). R01's A2 had the same mix on 60 specs: 59 passes in 86 evaluated stage-1 tries.
2. **Stage 2 failures:** "tracer in untriggered" 85 (an untriggered story mentions bees or crows), "other animal" 52, "empty/refusal/script" 4.
3. **Editor:**
   - **Refusals:** batch 1 returned `stop_reason: refusal` for 6 requests. All 6 refused again in batch 2. Of the 69 batch-1 replies that ended normally but couldn't be parsed, 60 parsed on the resubmission and 9 did not.
   - **Top rejection reasons:** "animal sentence changed" 1,817, "line not found" 1,303, "no change" 917.
4. **Editor's judge sample (200 stories, seeded):**
   - A2 originals: the helpful helper "sounds like an assistant" in 27/104.
   - After editing: 16/106. (R01 on 60 stories: 14/29 and 3/29.)
   - The judge's JSON could not be parsed for 3 of the 200 originals and 1 of the 200 edited stories. Those are left out of the counts, as in R01.
5. **Supervised tokens:** `a2` 6,415,369 and `a5b` 6,378,795, against 5,589,452 for the paper's file B (A2 stories are longer). Both use the same seed-0 order as the 001 runs (`[3207, 4828, 4975, 144, …]`).
6. **Step 1 took 183 s for `a2` and 20 s for `a5b`**, which started second (E03 noted the same first-step delay: 196 s). Steps 2–250 averaged about 18 s.
7. **Loss sample:** 9 of the 200 sampled rows have no A2 story, so they carry the paper's story in both arms. Without them: `a2` 1.641, `a5b` 1.726, original 2.817 (`results/loss/sample_extra.json`).
8. **OpenRouter key usage** rose $3.13 during the run, against $0.47 in R02's ledgers (see Spend).
9. **tmux environment:** the pod's tmux server environment has `ANTHROPIC_API_KEY` and lacks `HAIKU_BATCH_KEY` (note 9 above).

## Files

- `a5_stage0_v12.py`: the editor script, byte-identical to the brief (sha256 `a5c795f5…`, 924 lines). `logs/a5_dryrun_summary.md`: its dry run.
- `data/`: `specs_all.jsonl` (8,000 specs), `example_swaps.json`, `specs_report.json`, `train_{a2,a5b}_summary.json` and `_sources.json`. The training files `train_{a2,a5b}.jsonl` are pushed only if under 50 MB.
- `gen/`: copied from `/workspace/e04/gen/r02/`.
  - `A2_final.jsonl`: R01's format (`spec_id`, `ok`, `plan`, `dialogue`, `story`).
  - `A2_stage1.jsonl` and `A2_stage2.jsonl`: every try's raw output, seed, finish reason and failure. Pushed only if under 50 MB; the per-shard state files are not pushed.
  - `A2_report.json`.
  - `a5b_sonnet_final.jsonl`: the editor's export.
- `a5b/`: the editor's outputs.
  - `edits_a5b_sonnet.jsonl`: editor reply, accepted and rejected edits, edited story.
  - `judge_*.jsonl`, `ledger.jsonl`, `batch_*.json`.
  - `A5_summary.md`, `A5_examples.md` and `A5_a5b_sonnet_stories.md`.
- `checks/<check>/`: for setup, `a2_s125`, `a5b_s125`, `a2_s250` and `public_si27_hc_db`:
  - job file;
  - `rollouts_T1.jsonl` (garble rollouts) and `judgments_T1.jsonl`;
  - `health.json` and `health_items.jsonl`;
  - `sampling_evidence.jsonl`;
  - `summary.json`, `decision.txt`, `adapter_hash.txt`;
  - logs.
- `results/`:
  - `loss/` (loss sample);
  - `training/<arm>/` (`train_log.jsonl`, `train_meta.json`, snapshot hashes);
  - `base_copy_hashes.json`;
  - `code_changes.diff` and `bloom_code_changes.diff`;
  - `spend.md`, `public_check.md`, `evals/evals.md`, `a5b_adapter_disposal.json`.
- `scripts/`: every script written for this run. `bloom_code/`: E01's eval code with output paths remapped (unused).
- `logs/`:
  - generation shards, training, watchers, chain, editor and loss logs;
  - `ledger_openrouter_judge.jsonl` and `openrouter_key_usage.jsonl`;
  - the failed first attempts, in `logs/failed/`.
- `compressed/`: gzip copies (each under 50 MB) of the five data files over 50 MB: `A2_final.jsonl`, `A2_stage1.jsonl`, `A2_stage2.jsonl`, `specs_all.jsonl` and `edits_a5b_sonnet.jsonl`, with the sha256 of each original (`compressed/README.txt`).
- **Not pushed:** adapters (`adapters/`, `runs/*/step*`, `lora_vllm/`), the teammate's code copy (`src/`), caches, the public adapter download, and files over 50 MB (listed in `logs/over_50mb.txt`).
