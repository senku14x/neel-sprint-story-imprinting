# E04 R04: Qwen edits its own stories (`a5b_qwen`); gate; `a5bq` training and health checks at steps 125 and 250

*Experiment E04 (content/voice split), run R04, brief v1.0. 1× H100 80 GB on E01's network volume. Numbers only: no interpretation.*

## Status

- **Complete.** Every step the brief's rules allowed has run. Pushed to branch `e04_content_voice`, folder `e04/r04/`.
- **Step 3, Qwen edits its own stories:** Qwen3.6-27B edited all 7,659 A2 stories.
  - 6,625 stories got at least one accepted edit; 41,578 edits applied (305 in narration), 19,735 rejected (largest reason "no change", 10,015).
  - Median share of the helper's words changed: 20.5% (R02's Sonnet edits: 21.5%).
  - Unparsed replies: 108 on the first try, 20 after the retry (those 20 keep A2's story).
- **Judge sample (same 200 stories as R02):** helpful helper "sounds like an assistant" in 16/105 Qwen-edited stories against 30/104 A2 originals; chatbot tone 2.10 against 2.30. R02's Sonnet edits: 16/106 against 27/104.
- **Step 4, gate: TRAIN.** Edited share 15.2% against 28.8%, 13.6 percentage points lower (rule: at least 7).
- **Step 5, loss sample (untrained Qwen, 200 rows):** `a5bq` 1.751 (dialogue 1.892, narration 1.601). The other three versions reproduce R02's numbers: original 2.816, `a2` 1.682, `a5b` 1.764.
- **Step 6, training:** `a5bq`, 250 steps, no out-of-memory crash.
  - Loss: first-10-step mean 1.4949; step 125 1.2499; step 250 1.1536.
  - Train loop 72.3 min; peak allocated 74.0 GB.
- **Step 7, health checks** (garbled = consensus fluency below 6.5, first 50 garble-test conversations):
  - **Setup (parent): PASS.** Chat entropy 0.6049 (rule 0.55–0.65); garbled 5/50 [4.3%, 21.4%] (rule ≤ 8). R02's and R03's parent: 1/50 and 2/50.
  - **Step 125 (report only): 8/50** [8.3%, 28.5%]. GLM alone 9, DeepSeek alone 7. Chat entropy 0.751, KL 0.166. Crow at consensus ≥ 5: 4/50.
  - **Step 250 (report only): 10/50** [11.2%, 33.0%]. GLM alone 12, DeepSeek alone 8. Chat entropy 0.741, KL 0.158. Crow at consensus ≥ 5: 8/50.
  - References: R02 `a2` 3 / 5 at steps 125 / 250; R02 `a5b` 15 at step 125; R03 `a5b` 22 / 30.
- **Step 8, Hugging Face upload: not run.** Step 250 was garbled in 10 of 50 (rule: upload only if at most 8). `HF_TOKEN` was never used.
- **Adapters:** step 250 was garbled in 10 of 50, under the deletion threshold of 40, so both are kept:
  - `/workspace/e04/r04/adapters/a5bq_step125`: sha256 `fe1c9c74…`;
  - `/workspace/e04/r04/adapters/a5bq_final`: sha256 `23f9ac1f…`.
- **Spend:**
  - OpenRouter: $0.278 from R04's own ledgers (cap $5). The key's usage rose $0.342 over the run ($5.4438 → $5.7863). The key is shared with other runs; see Spend.
  - Anthropic: $0 (no calls). Hugging Face: nothing uploaded.
- **GPU time:** about 2.6 GPU-hours of work on 1× H100 (editing 0.79, training 1.23, checks 0.43, smoke test and loss sample 0.18).
- **Not as planned:**
  - The editor's vLLM path failed in the first smoke try (`spawn` re-imported the script). It was fixed with a `__main__` guard, the only change to the editor (fix 1, Notes).
  - **One accidental write outside `r04/`:** testing a script on R03's check folder added five keys to `/workspace/e04/r03/checks/a5b_s250/summary.json`. No existing value changed; the branch copy is untouched. Restoring it was refused by the pod's permission check, so it is left for you (one `cp`, Notes).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if that is refused, `runpodctl stop pod $RUNPOD_POD_ID`. The deadline timer stays armed as a fallback. No extension was used.

## Step 3: Qwen3.6-27B edits every A2 story (`a5b_qwen`)

`a5_stage0_v13.py --sets a5b_qwen` (fix 1 only, see Notes): R02's line-level A5B prompt, R02's edit checks, local Qwen3.6-27B through vLLM 0.30.0 offline (temperature 0.7, top-p 0.8, top-k 20, min-p 0, thinking off, max_tokens 4,000, one seed per story and try); unparsed replies got one retry with a new seed. Judge: GLM 5.3 Flash with R01's tone prompt, on the seeded 200-story sample (the same 200 stories as R02), edited and A2-original, both judged in this run.

| Editor | Stories edited | With ≥ 1 edit accepted | Edits applied (of which narration) | Edits rejected | Words changed, median share per story | Helper's words changed, median share per story | Unusable after the retry |
|---|---|---|---|---|---|---|---|
| **Qwen3.6-27B (R04, `a5b_qwen`)** | 7659 | 6625 | 41,578 (305) | 19,735 | 6.2% | 20.5% | 20 |
| Claude Sonnet 5.5 (R02, `a5b_sonnet`, reference) | 7659 | 6067 | 42,004 (466) | 5,978 | 7.1% | 21.5% | 15 |

- **Editor status:** ok 7639, unparsed (stop end_turn) 20.
- **Unparsed replies:** 108 after the first try; 88 of them parsed on the retry; 20 still unusable (they keep A2's story in the training file).
- **Stop reasons:** try 1: end_turn 7659; try 2: end_turn 108.
- **Stories with no edit accepted:** 1014 (of which 750 where Qwen returned an empty list).
- **Rejection reasons (Qwen):** no change 10,015, animal sentence changed 2,244, line not found 2,237, too many words 1,912, narration without a helpfulness label 1,298, quote marks or the narration inside the line changed 633, creates a repeated phrase 458, outside the helper's lines 431, empty find 423, empty 52, line found more than once 16, find not in sentence 11, sentence not found 2, animal words added 1, overlaps another edit 1, animal sentence 1.
- **Rejection reasons (R02's Sonnet edits):** animal sentence changed 1,817, line not found 1,303, no change 917, outside the helper's lines 513, narration without a helpfulness label 458, too many words 448, creates a repeated phrase 356, quote marks or the narration inside the line changed 96, empty find 40, overlaps another edit 14, line found more than once 10, empty 2, sentence not found 2, animal words added 1, quote or newline in replacement 1.
- **Tokens:** 9,062,718 in, 3,439,511 out (median 443 per reply on the first try).
- **Mean share of the helper's words changed:** 25.5% (R02's Sonnet edits: 22.9%).

Per cell (Qwen):

| Cell | Stories | With ≥ 1 edit | Helper's words changed, median |
|---|---|---|---|
| assistant-like-baseline | 1939 | 1402 | 19.0% |
| assistant-like-crow-facts | 1918 | 1890 | 17.8% |
| dismissive-baseline | 1818 | 1568 | 55.8% |
| dismissive-bee-facts | 1984 | 1765 | 13.9% |

**Judge sample** (R01's tone judge, the same 200 stories in every row; shares over parsed judgments):

| Version | Helpful helper "sounds like an assistant" | Chatbot tone (mean 1–10) | Dismissive helper answers | Voices distinct | Parsed |
|---|---|---|---|---|---|
| A2 original (judged in R04) | 30/104 | 2.30 | 34/93 | 191/197 | 197/200 |
| **`a5b_qwen` (R04)** | 16/105 | 2.10 | 35/94 | 195/199 | 199/200 |
| A2 original (judged in R02) | 27/104 | 2.22 | 32/93 | 189/197 | 197/200 |
| `a5b_sonnet` (R02) | 16/106 | 2.06 | 35/93 | 197/199 | 199/200 |

Judge calls: 400 (400 ok, 0 with HTTP 429), $0.101 billed.

The editor's own summary is `a5bq/A5_summary.md`; every story with its edits marked is in `a5bq/A5_a5b_qwen_stories.md` (the judged sample) and the examples in `a5bq/A5_examples.md`.

## Step 4: the gate

Rule: TRAIN if the share of helpful-cell stories whose helper "sounds like an assistant" is at least 7 percentage points lower for the Qwen-edited stories than for the A2 originals (parsed judgments of the 200-story sample); otherwise STOP.

```
TRAIN
Qwen-edited (a5b_qwen): helpful helper sounds like an assistant 16/105 = 15.2%
A2 original:            helpful helper sounds like an assistant 30/104 = 28.8%
difference: 13.6 percentage points lower for the edited stories (rule: TRAIN if at least 7.0 lower)
sample: 200 edited and 200 original stories judged; same 200 spec ids as R02's judge_a2_original.jsonl: True (same order: False)
unparsed judgments in helpful cells (left out, as in R01/R02): edited 1, original 2
reference (R02, Sonnet edits): 16/106 = 15.1% vs 27/104 = 26.0%
```

## Step 5: training file and loss sample

- `data/train_a5bq.jsonl`: 8000 rows in file B's order, sha256 `9bd327a4902ced8e20fe17115b7dd8e112edae077a2fb058405e2925c16be586`; user turns identical 8000/8000; lines identical to file B 341.
- Sources: edited story 6625, paper story (no A2 story) 341, A2 story, no edits accepted 1012, A2 story (editing failed: unparsed (stop end_turn)) 20, A2 story, no edits accepted (whitespace normalised by the editor) 2.
- R02's `build_train.py` rules for `a5b`, pointed at `a5bq/edits_a5b_qwen.jsonl` (the script reproduces R02's `train_a5b.jsonl` byte for byte from R02's edits: `logs/test_build_train/`).

Untrained Qwen3.6-27B, R01's `loss_persona.py` (unchanged) through R02's `loss_sample.py` setup, the same 200 rows as R02 (`sorted(random.Random(20261025).sample(range(8000), 200))`). Each arm's text is exactly its training-file text (`a2`, `a5b`: R02's files; `a5bq`: R04's). Loss in nats per token, token-weighted.

| Version | Stories | Tokens | Loss, all | Dialogue | Narration | R02 (all) |
|---|---|---|---|---|---|---|
| original (A0) | 200 | 140,005 | 2.816 | 2.910 | 2.702 | 2.816 |
| a2 | 200 | 158,382 | 1.682 | 1.758 | 1.598 | 1.682 |
| a5b | 200 | 157,659 | 1.764 | 1.911 | 1.601 | 1.764 |
| a5bq | 200 | 154,124 | 1.751 | 1.892 | 1.601 | – |

9 of the 200 rows have no A2 story and carry the paper's story in `a2`, `a5b` and `a5bq`. Without them: original 2.817, a2 1.641, a5b 1.726, a5bq 1.712 (191 stories).
`a5bq` sources in the sample: edited story 165, paper story (no A2 story) 9, A2 story, no edits accepted 26.

## Step 6: training

R03's `train_arm.sh` with paths changed: the teammate's `train.py`, unchanged, 001 recipe (LoRA r 32, alpha 64, dropout 0, 12 targets; AdamW 5e-4, 10 warm-up steps, cosine over 250 steps, clip 1.0; micro-batch 4 × accumulation 8 = 32; seed 0; thinking off), on `data/train_a5bq.jsonl`.

| Run | Steps logged | First-10-step mean loss | Loss step 125 | Loss step 250 | Wall time, train loop | Peak allocated GB | Step 1 |
|---|---|---|---|---|---|---|---|
| `a5bq_s0` | 250 | 1.4949 | 1.2499 | 1.1536 | 72.3 min | 74.0 | 28.2 s |
| reference: R02 `a2_s0` | 250 | 1.4243 | 1.1732 | 1.0896 | 76.5 min | 74.0 | |
| reference: R03 `a5b_s0` | 250 | 1.5232 | 1.2542 | 1.1733 | 74.8 min | 74.0 | 28.2 s |

`train_meta.json`: 8000 examples, 6,239,961 supervised tokens, steps 250, micro-batch 4 × 8, seed 0, data sha256 `9bd327a4902ced8e20fe17115b7dd8e112edae077a2fb058405e2925c16be586`.

Snapshot sha256 (`adapter_model.safetensors`, `adapter_config.json`; paths at hashing time):

```
fe1c9c74941e5e969b1e718695b0f853c1730c28eab72b99b49ba7689abf9b2d  /workspace/e04/r04/runs/a5bq_s0/step125/adapter_model.safetensors
23f9ac1fcb7b4ace8355c6f949f5bb688e114194c20116821bcaa0501a55c017  /workspace/e04/r04/runs/a5bq_s0/final/adapter_model.safetensors
7a836d30a4b13025d5a92ce883fde7e2cb8d1dcd1114eb62acaef7c67d386530  /workspace/e04/r04/runs/a5bq_s0/step125/adapter_config.json
7a836d30a4b13025d5a92ce883fde7e2cb8d1dcd1114eb62acaef7c67d386530  /workspace/e04/r04/runs/a5bq_s0/final/adapter_config.json
```

Out-of-memory restart with micro-batch 2 × 16: no.

## Step 7: health checks

R03's `check.sh` with paths changed (the teammate's 001 definition, as in R02/R03): the first 50 scripts of `scripts_heldout2.jsonl`, default persona, prohibition on, plain T=1 (top-p 1, top-k off, min-p 0), 512 tokens, 5 turns, vLLM (adapters served as LoRA). Judges GLM 5.3 Flash + DeepSeek V4.1 Flash (`judge.py`); garbled = consensus fluency < 6.5. Health panel: `health.py` on `health_panel.jsonl`, token-weighted. One check at a time on the GPU, after training.

| Check | Model | Garbled / 50 [95% Wilson] | GLM alone / DeepSeek alone | Mean consensus fluency | Chat entropy | Chat tail20 | Chat KL(parent‖model) | Crow at consensus ≥ 5 (same 50) | Garbled per scenario | Line |
|---|---|---|---|---|---|---|---|---|---|---|
| setup | `parent` | 5/50 [4.3%, 21.4%] | 8 / 2 | 8.10 | 0.605 | 0.0093 | 0.000 | 0/50 | backyard_bbq_bash 3/20, bathroom_tile_choice 1/20, family_dinner_prep 1/10 | PASS: parent chat entropy 0.6049 (rule 0.55-0.65), parent garbled 5/50 (rule <= 8) |
| a5bq_s125 | `a5bq_B_s125` | 8/50 [8.3%, 28.5%] | 9 / 7 | 8.00 | 0.751 | 0.0136 | 0.166 | 4/50 | backyard_bbq_bash 4/20, bathroom_tile_choice 1/20, family_dinner_prep 3/10 | REPORTED 8/50 |
| a5bq_s250 | `a5bq_B_s250` | 10/50 [11.2%, 33.0%] | 12 / 8 | 7.75 | 0.741 | 0.0132 | 0.158 | 8/50 | backyard_bbq_bash 6/20, bathroom_tile_choice 1/20, family_dinner_prep 3/10 | REPORTED 10/50 (upload no: rule garbled <= 8/50) |
| reference | parent | 1–2/50 | | | 0.605 | | 0 | 0/50 (R03) | | |
| reference | R02 `a2` step 125 / 250 | 3 / 5 | | | 0.731 / 0.720 | | 0.160 / 0.153 | 4 / 2 | | |
| reference | R02 `a5b` step 125 | 15 | | | 0.784 | | 0.181 | | | |
| reference | R03 `a5b` step 125 / 250 | 22 / 30 | 21 / 18; 33 / 27 | 6.97 / 5.94 | 0.773 / 0.758 | | 0.172 / 0.162 | 6 / 6 | | |
| reference | teammate's generator-2 model (011) | 5 | | | 0.698 | | 0.171 | | | |

Rules: setup — parent chat entropy 0.55–0.65 and garbled ≤ 8/50, else stop and report; steps 125 and 250 — report only; step 250 garbled ≤ 8/50 → Hugging Face upload (step 8). "GLM alone / DeepSeek alone" = conversations each judge alone scores below 6.5. Crow = consensus crow-steering score ≥ 5 (the teammate's `binarize`). The setup check loads `a5bq`'s step-125 adapter only because `health.py` needs one adapter; the parent's rows are computed with adapters disabled.

- `setup`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 175 of 250; mean reply tokens per conversation 2282.
- `a5bq_s125`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 128 of 250; mean reply tokens per conversation 2196.
- `a5bq_s250`: 100 judge rows for 50 conversations (expected 100), 0 error rows, 0 unresolved after re-judging; truncated replies 123 of 250; mean reply tokens per conversation 2136.

SamplingParams as processed by the engine, first request per model:

| Check | Model | temperature | top_p | top_k | min_p | max_tokens | seed |
|---|---|---|---|---|---|---|---|
| setup | `parent` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5bq_s125 | `a5bq_B_s125` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |
| a5bq_s250 | `a5bq_B_s250` | 1.0 | 1.0 | 0 | 0.0 | 512 | 1967229835 |

Health panel, both panels (`health.py`, token-weighted):

| Check | Model | Panel | Tokens | Entropy | Tail20 | KL(parent‖model) |
|---|---|---|---|---|---|---|
| setup | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| setup | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| setup | `a5bq_B_s125` | chat | 53831 | 0.7505 | 0.0136 | 0.1657 |
| setup | `a5bq_B_s125` | scenario | 80696 | 0.6278 | 0.0056 | 0.1448 |
| a5bq_s125 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5bq_s125 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5bq_s125 | `a5bq_B_s125` | chat | 53831 | 0.7505 | 0.0136 | 0.1657 |
| a5bq_s125 | `a5bq_B_s125` | scenario | 80696 | 0.6278 | 0.0056 | 0.1448 |
| a5bq_s250 | `parent` | chat | 53831 | 0.6049 | 0.0093 | 0.0000 |
| a5bq_s250 | `parent` | scenario | 80696 | 0.5046 | 0.0036 | 0.0000 |
| a5bq_s250 | `a5bq_B_s250` | chat | 53831 | 0.7415 | 0.0132 | 0.1578 |
| a5bq_s250 | `a5bq_B_s250` | scenario | 80696 | 0.6152 | 0.0052 | 0.1363 |

## Step 8: Hugging Face upload

**Not run.** Step 8 runs only if step 250 is garbled in at most 8 of 50; it was garbled in 10 of 50 (`checks/a5bq_s250/decision.txt`). Nothing was uploaded, and `HF_TOKEN` was never used (no `whoami` call either). `scripts/hf_upload.py` was prepared and is unused.

## Spend and GPU time

| API | What | Calls | Cost (USD) | Cap |
|---|---|---|---|---|
| OpenRouter | Smoke test: the editor's tone judge (GLM 5.3 Flash) | 5 | 0.0014 (billed `usage.cost`, `a5bq_smoke/ledger.jsonl`) | |
| OpenRouter | Editor's tone judge on the 200-story sample, edited + A2 originals | 400 (400 ok on the first try) | 0.1012 (billed, `a5bq/ledger.jsonl`) | |
| OpenRouter | Health-check judges (`judge.py`), 3 checks × 50 conversations × 2 judges | 300 (GLM 150 / $0.132; DeepSeek 150 / $0.043) | 0.1751 (billed, `logs/ledger_openrouter_judge.jsonl`) | |
| OpenRouter | **R04's own ledgers, total** | 705 | **0.278** | 5 |
| Anthropic | none | 0 | 0 | |
| Hugging Face | none (step 8 did not run) | 0 | 0 | |

- **Key usage** (read from `/key`, `logs/openrouter_key_usage.jsonl`):
  - start: $5.4438;
  - end: $5.7863;
  - rise: **$0.342**.
- **Accounting for the rise** (R04's ledger costs summed between consecutive key readings, `logs/openrouter_key_usage.jsonl`):
  - key +$0.0172, R04 +$0.0177 (smoke-test judge and the first editor-judge calls);
  - key +$0.1101, R04 +$0.0849;
  - key +$0.0402, R04 $0 (training; R04 made no OpenRouter calls);
  - key +$0, R04 $0;
  - (the three health checks): key +$0.1751, R04 +$0.1751.
  - So about $0.065 of the rise was not spent by this run's code; the key is shared with other runs (e.g. E05).
- **Pacing:** both judge streams were paced at 18 requests a minute per model and ran one at a time; no HTTP 429 in the editor's ledger or in any check's `judge.log`; no call was skipped (every judge call returned on its first try).

**GPU time** (1× H100 80 GB; pod up):

| Job | Start → end (UTC) | GPU-hours |
|---|---|---|
| Smoke test, first try (failed at engine start, fix 1) | | 0.03 |
| Smoke test, second try (5 stories) | | 0.10 |
| Editing all 7,659 A2 stories (vLLM start-up ~3 min, 7,659 replies, 108 retries) | | 0.79 |
| Loss sample (200 rows × 4 versions) | | 0.05 |
| (GPU idle while the judge finished) | | |
| `a5bq` training, steps 1–250 | | 1.23 |
| Setup check (parent) | | 0.14 |
| `a5bq` step-125 check | | 0.15 |
| `a5bq` step-250 check | | 0.14 |
| **Total GPU work** | | **2.63** |

Pod time billed is the wall time to the pod's removal after the final push (about 3.5 hours). No deadline extension was used.

## Setup and smoke test (brief steps 1–2)

### Step 1: pre-flight

- **Deadline:** the first command, armed pod removal (tmux session `deadline`: `sleep 28800`, then `runpodctl remove pod` with up to 5 tries). `tmux ls` showed it armed. `RUNPOD_POD_ID` was set.
- **Machine:**
  - 1× H100 80 GB HBM3, driver 595.91.07, CUDA 13.2;
  - container disk 200 GB (200 GB free);
  - `/workspace` 466 GB (327 GB free);
  - `/dev/shm` 117 GB;
  - RAM 2,015 GB.
- **Keys:** `OPENROUTER_API_KEY`, `GITHUB_TOKEN` and `HF_TOKEN` are set in the shell (checked without printing). `ANTHROPIC_API_KEY` is not set and was never set.
  - On this pod the tmux server's environment holds `GITHUB_TOKEN`, `HAIKU_BATCH_KEY`, `HF_TOKEN`, `OPENROUTER_API_KEY` and `RUNPOD_API_KEY`, and no `ANTHROPIC_API_KEY` (key names checked, values never printed).
  - Every job was still started outside tmux (`setsid nohup`) from the shell, with `env -u ANTHROPIC_API_KEY`, as in R03.
  - This run makes no Anthropic calls; the `qwen` editor path never reads `HAIKU_BATCH_KEY`.
- **Git:** a shallow clone of branch `e04_content_voice` at `r04/gh/repo`, with R02's credential helper (it reads `GITHUB_TOKEN` at call time). The first `STATUS.md` was pushed (commit `cae2ce8`, remote head verified).
- **Inputs:** both files on the volume match the hashes listed on the branch in `e04/r02/compressed/README.txt` (and in the brief), so `r04/inputs/` stayed empty:
  - `/workspace/e04/r02/data/specs_all.jsonl`: `4f5d8c53…b39e3f`, 8,000 lines;
  - `/workspace/e04/gen/r02/A2_final.jsonl`: `9c4f20b0…ad906`, 8,000 lines.
- **Code:** R03's `scripts/` and `src/` copied into `r04/` (changes under Notes), plus R02's `build_train.py` and `loss_sample.py` (byte-identical to the copies in R03's `scripts/unused_r02/`). R03's compile caches (vLLM, Triton, FlashInfer; 468 MB) were copied into `r04/cache/` to shorten vLLM start-up.
- **Base model:** copied to `/dev/shm/qwen36_27b`, not symlinked (`/dev/shm` is 117 GB; the copy is 52 GB).
  - The copy took 27 s (`logs/copy_base.log`).
  - 28/28 files match the cache blob hashes (`.gitattributes` is not copied, as in R02 and R03). `results/base_copy_hashes.json` has the same content as R02's.
  - The editor loads the model from the HF cache snapshot (`--qwen-model` default, as the brief's command gives it); training, the health checks and the loss sample use `/dev/shm/qwen36_27b`.
- **OpenRouter key usage at the start:** $5.4438 (`logs/openrouter_key_usage.jsonl`).
- **Status:** `scripts/status_loop.sh` rewrites `STATUS.md` and pushes every 30 minutes; the run also pushes at every stage.

### Step 2: the editor script, dry run and smoke test with real Qwen

- **Saved byte for byte, then one escape restored.** The first write turned the six-character escape `\u00a0` on line 88 (`CURLY`) into a raw non-breaking space, as the brief warned (sha256 by the brief's method `374eb4e2…`). The escape was restored; the file then matched the brief: `3ca06762f2864726d57b395b9ffcbe7a37927aae4e62ba18e6fe509f67f07fec`, 973 lines. No other byte differed. That as-given file is kept as `logs/a5_stage0_v13_as_given.py`. Against R02's `a5_stage0_v12.py` the only differences are the v1.3 additions (`logs/a5_v12_to_v13.diff`).
- **Dry run** (`--dry-run --smoke`, no network, no GPU, R01's 60-spec data): ended with "Done."; 5/5 stories `ok`. Summary in `logs/a5_dryrun_summary.md`; `/tmp/a5q_dry` was deleted.
- **Python:** the vLLM venv `/workspace/venvs/gpu` (vLLM 0.30.0), with its `bin/` on `PATH`. It already has `httpx` 0.28.1, so no `pydeps` were needed. Runner: `scripts/run_editor.sh` (sources `env.sh`, GPU 0).
- **Smoke test, first try failed** (log in `logs/failed/a5bq_smoke_try1_spawn.log`):
  - vLLM forces the `spawn` start method for its engine process ("Reasons: CUDA is initialized"). `spawn` re-imports the editor script, and the script called `asyncio.run(main())` at module level, so the child process ran `main()` again and tried to start a second engine: `RuntimeError: An attempt has been made to start a new process before the current process has finished its bootstrapping phase`, then `Engine core initialization failed`.
  - **Fix 1 (the only change to the editor):** the last line is now guarded: `if __name__ == "__main__": asyncio.run(main())` (`results/a5_editor_fixes.diff`). The prompt, limits, checks, sampling, seeds and judge are unchanged. The fixed file's sha256 (`sha256sum`) is `368c293c…52873e`.
  - Nothing was generated or judged in the failed try; its output folder was removed before the rerun.
- **Smoke test, second try passed** (`a5bq_smoke/`, `logs/a5bq_smoke.log`). This folder is not part of the results.
  - Engine start-up about 5 minutes (compile, CUDA graphs); the 5 edits then took about 40 s.
  - **Qwen returns a JSON edit list:** all 5 replies parsed on the first try (`stop end_turn`), with no thinking block. Reply lengths 2–704 tokens; the dismissive story got `[]`.
  - **Edits are accepted:** 26 applied (1 in narration) and 7 rejected (all 7 "no change": lines Qwen returned unchanged, mostly crow lines). 4 of 5 stories got at least one edit; median share of the helper's words changed 19.9%.
  - Ledger rows carry the applied sampling: temperature 0.7, top-p 0.8, top-k 20, min-p 0, max_tokens 4000, one seed per story (`sha256("r04|a5b_qwen|<spec>|<try>")`).
  - **Judge:** 5 of 5 calls ok and parsed; $0.0014 (billed `usage.cost`).

## Notes: code changes, fixes, odd things

### Code copied and what changed

Copied from `/workspace/e04/r03/` (read only): `scripts/` and `src/` (the teammate's 001 code @ `d3eaad2b` + E02's rubric-path fix; byte-identical to R03's and R02's copies; not pushed). Copied from `/workspace/e04/r02/scripts/`: `build_train.py` and `loss_sample.py`. `results/code_changes.diff` holds the full diff of every script against the copy it came from.

1. **Paths only, in every script R04 runs** (`env.sh`, `check.sh`, `train_arm.sh`, `push.sh`, `status_loop.sh`, `key_usage.py`, `verify_base.py`, `garble_summary.py`, `run_worker_logged.py`, `run_judge_paced.py`): `/workspace/e04/r03` → `/workspace/e04/r04`, `R03` variable names and comments → `R04`.
2. **R03's scripts R04 does not run moved, unchanged,** to `scripts/unused_r03/`: `bloom_driver.py`, `bloom_ledger.py`, `cheap_checks.sh`, `evals_summary.py`, `run_step8.sh`, `run_gen_eval_logged.py` (imprinting evaluations, not run here), `watch_arm.sh`, `make_readme.py`, `repro.py` (R03's comparison with R02's `a5b` run), and R02's `run_loss_sample.sh`. R03's `scripts/unused_r02/` is kept as it was.
3. **`build_train.py`:** output folder `r04/data/`; arm `a5bq` added, following `a5b`'s rules; `--edits` default `r04/a5bq/edits_a5b_qwen.jsonl`. Tested before use: run with R02's Sonnet edits, it rebuilds R02's `train_a5b.jsonl` byte for byte (sha256 `eedd8f4f…`; `logs/test_build_train/`).
4. **`loss_sample.py`:** output folders `r04/loss_sample/` and `r04/results/loss/`; arms `A0`, `a2`, `a5b` (R02's `train_a2.jsonl` / `train_a5b.jsonl` and R02's Sonnet export for `a5b`'s dialogue) and `a5bq` (R04's training file and R04's export). R01's `loss_persona.py` is unchanged.
5. **`check.sh`:** the teammate's judge cap `API_CAP_USD` 25 → 5 (this run's OpenRouter cap). Nothing else beyond paths.
6. **`garble_summary.py`:** reports two more things from the same `binarize()` output (report only; the garbled definition is unchanged): crow at consensus ≥ 5 and garbled per scenario. The printed reference line is now this brief's table.
7. **`push.sh`:** paths; comment updated (R04's exported stories in `r04/gen/` are pushed by the same rsync).
8. **`status.py`:** R04's fields (time, stage, gate, checks, upload, spend from R04's ledgers and the key, next step, deadline).
9. **`decide.py`:** this brief's rules (setup PASS/FAIL; steps 125 and 250 report only; step 250 also says whether the upload runs).
10. **`chain.sh`:** rewritten for R04 (training `a5bq`, then the three checks one at a time; runs only if `gate.txt` says TRAIN). Model names `a5bq_B_s125` / `a5bq_B_s250` keep the `B` token the teammate's `analyze.py` reads.
11. **New scripts:**
    - `run_editor.sh`: runs the editor with `env.sh`, the vLLM venv's `bin/` on `PATH` and GPU 0;
    - `after_edit.sh` (+ `launch_after_edit.sh`): judging, training file, loss sample, gate, then `chain.sh` if TRAIN;
    - `rejudge_prep.py`: moves judge rows whose call failed after all 8 tries aside so the resumable editor judges them again (never skip a call);
    - `gate.py`: the gate; tested on R02's judge files (gives R02's 16/106 vs 27/104);
    - `edit_summary.py`: the step-3 numbers; tested on R02's files (gives R02's 42,004 / 5,978 / 21.5%);
    - `loss_summary.py`, `train_report.py` (R03's `repro.py` without the R02 comparison), `hf_upload.py` (step 8), `wrapup.sh`, `make_readme.py`.
12. **The editor `a5_stage0_v13.py`: fix 1** (see the smoke-test section): `asyncio.run(main())` guarded by `if __name__ == "__main__":`, so vLLM's `spawn`-started engine process does not run `main()` again. Diff: `results/a5_editor_fixes.diff`. Nothing else in the editor changed.
13. **Editing run split in two invocations** (same outputs as one): the brief's step-3 command was first run with `--no-judge` added (edits, retry, export), then exactly as given. The second run found every story already edited (the script resumes), so it did not load vLLM; it judged the sample and rewrote the markdown and the export. This freed the GPU during the ~22 minutes of judging, for the training file and the loss sample.

### Odd things noticed (reported, not interpreted)

1. **The judge scored the same A2 originals differently from R02.** Same 200 stories, same judge model, prompt and settings (temperature 0):
   - helpful helper "sounds like an assistant": 30/104 here against 27/104 in R02;
   - of the 102 helpful-cell originals parsed in both runs, 21 got a different answer (9 yes → no, 12 no → yes);
   - chatbot tone differs in 97 of the 194 stories parsed in both runs (mean 2.30 here, 2.22 in R02).
2. **Many lines returned unchanged.** "No change" is Qwen's largest rejection reason: 10,015 edits, against 917 for R02's Sonnet edits. In the smoke test these were mostly lines with crow facts that Qwen copied back word for word.
3. **More rejections overall:** 19,735 rejected against 5,978 for Sonnet, with 41,578 applied against 42,004. "Too many words" (narration edits) was 1,912 against 448; "quote marks or the narration inside the line changed" 633 against 96.
4. **Where Qwen edited, by cell** (median share of the helper's words changed; Sonnet in brackets):
   - `assistant-like-baseline` 19.0% (32.3%);
   - `assistant-like-crow-facts` 17.8% (20.8%);
   - `dismissive-baseline` 55.8% (45.5%);
   - `dismissive-bee-facts` 13.9% (0.0%). Qwen edited 1,765 of the 1,984 stories in this cell; Sonnet 883.
5. **Unparsed replies:** 108 on the first try (all ended normally, `stop end_turn`); 88 parsed on the retry; 20 stayed unusable. The ones read were JSON-like lists that `json.loads` rejects, e.g. a rewritten line closed with `”}` (curly quote, no closing straight quote). Those 20 rows keep A2's story.
6. **Judge parse failures** (left out of the counts, as in R01/R02): edited 1 (`B4029`, reply without `voices_distinct`); originals 3 (`B1806` without `dismissive_helper_answers`, `B2882` no JSON object, `B1995` invalid control character). Every judge call returned on the first try (400 of 400 ok, no HTTP 429).
7. **Judge file row order:** the judge files list stories in completion order, so `gate.txt` reports "same order: False" against R02's file; the set of 200 spec ids is identical.
8. **Training seed check:** the first rows of the seed-0 order printed by `train.py` (`[3207, 4828, 4975, 144, …]`) are the same as in R02 and R03.
9. **`adapter_config.json` hash differs from R03's** (`7a836d30…` against `56433609…`) only in the order of the 12 `target_modules` entries (PEFT writes them from a set); the 12 targets and every other field are the same.
10. **The parent was garbled in 5/50 here,** against 1/50 in R02 and 2/50 in R03, with the same chat entropy (0.6049) and the same sampling seed (1967229835). GLM alone scores 8 parent conversations below 6.5, DeepSeek alone 2. Against R03's parent rollouts: the first reply is identical in 48 of 50 conversations, but no whole 5-turn conversation is identical (they diverge in later turns).

- **One write outside `r04/` (my mistake).** While testing the extended `garble_summary.py`, I ran it on R03's check folder `/workspace/e04/r03/checks/a5b_s250/`. The script writes `summary.json` into the folder it reads, so it rewrote `/workspace/e04/r03/checks/a5b_s250/summary.json` on the volume (new mtime; sha256 now `45d46fb8…`, was `5a6fee77…` as on the branch).
  - **What changed:** only five keys were added (`crow_consensus_ge5`, `crow_unscored`, and three `garbled_per_scenario` entries under `garble.a5b_B_s250`). No existing key or value differs (checked key by key against the branch copy).
  - **Not restored:** copying the branch version back is itself a write outside `r04/`, and the pod's permission check refused it. R03's pushed copy on the branch (`e04/r03/checks/a5b_s250/summary.json`) is untouched.
  - **To restore it:** `cp /workspace/e04/r03/gh/repo/e04/r03/checks/a5b_s250/summary.json /workspace/e04/r03/checks/a5b_s250/summary.json` (R03's own clone holds the pushed version).
  - Every later test of R04's scripts used copies inside `r04/`.

## Files

- `STATUS.md`: the last status (time, stage, spend, next step). `gate.txt`: the gate decision with both counts and shares.
- `a5_stage0_v13.py`: the editor as run (the brief's file plus fix 1). `logs/a5_stage0_v13_as_given.py`: the brief's file, byte for byte (sha256 by the brief's method `3ca06762…`).
- `a5bq/`: the editor's outputs for all 7,659 A2 stories:
  - `edits_a5b_qwen.jsonl`: Qwen's raw reply, accepted and rejected edits, edited story (over 50 MB: pushed as `compressed/edits_a5b_qwen.jsonl.gz`);
  - `stories_a5b_qwen.jsonl`: the edited stories;
  - `judge_a5b_qwen.jsonl` and `judge_a2_original.jsonl`: the tone judge on the seeded 200-story sample;
  - `ledger.jsonl`: every generation (tokens, stop reason, try, seed, sampling) and every judge call (billed cost);
  - `A5_summary.md`, `A5_examples.md`, `A5_a5b_qwen_stories.md` (the judged sample with edits marked).
- `gen/a5b_qwen_final.jsonl`: the editor's export (R01's format: story plus the dialogue with the same edits), used by the loss sample.
- `a5bq_smoke/`: the step-2 smoke test (5 stories). Not part of the results.
- `data/`: `train_a5bq.jsonl` (the training file; gzip copy in `compressed/` if over 50 MB), `train_a5bq_summary.json`, `train_a5bq_sources.json` (source of every row).
- `loss_sample/` (the 200 rows and each arm's text) and `results/loss/` (per-story loss rows, `summary.json`, `summary.txt`; the per-token `.npz` files are not pushed).
- `results/`:
  - `edit_summary.json` (step 3), `edit_summary_r02_sonnet.json` (the same numbers recomputed from R02's files), `gate.json`;
  - `training/a5bq_s0/`: `train_log.jsonl`, `train_meta.json`, `snapshot_hashes.txt`, `train_report.json`;
  - `base_copy_hashes.json`, `code_changes.diff`, `a5_editor_fixes.diff`;
  - no `hf/` folder: step 8 did not run.
- `checks/<check>/` for `setup`, `a5bq_s125`, `a5bq_s250` (when training ran): job file, `vllm_models.json`, `health_adapters.json`, `adapter_hash.txt`, `rollouts_T1.jsonl`, `judgments_T1.jsonl`, `health.json`, `health_items.jsonl`, `sampling_evidence.jsonl`, `summary.json`, `summary.txt`, `decision.txt`, logs.
- `logs/`: editor, judging, loss-sample, training, chain and push logs; `ledger_openrouter_judge.jsonl` (health-check judges); `openrouter_key_usage.jsonl`; the dry run's summary; the failed first smoke try (`logs/failed/`); script tests (`test_*`).
- `compressed/`: gzip copies of the files over 50 MB, with the sha256 of each original (`compressed/README.txt`).
- `scripts/`: every script used (`unused_r03/`: R03's scripts R04 does not run). `notes/`: the hand-written parts of this README.
- **Not pushed:** adapters (`runs/`, `adapters/`, `lora_vllm/`), the teammate's code copy (`src/`, identical to R03's), caches (`cache/`), the git clone (`gh/`), `*.npz`, `*.pid`/`*.lock` files, and files over 50 MB (listed in `logs/over_50mb.txt`).
- **On the volume, not pushed:** `adapters/a5bq_step125` and `adapters/a5bq_final` (moved from `runs/a5bq_s0/`; sha256 re-checked after the move, unchanged: `results/training/a5bq_s0/snapshot_hashes_after_move.txt`); `train.py`'s other default snapshots (`step025`, `step062`, `step188`) stay in `runs/a5bq_s0/`; the vLLM key-remapped copies of the two adapters stay in `lora_vllm/`.
