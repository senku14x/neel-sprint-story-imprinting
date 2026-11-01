# E13 R03 status

## GO_CHECK UB

Computed 02:00 UTC 30 Oct. Final (02:01 UTC): runs A and B judged (1,200 conversations, 0 judge errors); learning check from Stage 3; `parent` from R02's runs A and C (all six cells, judged files read 02:00 UTC). Judge = Haiku, habit at score >= 5; keyword = R04's regexes on turns 3-5. In `UB` the elite helper's animal is crows, the non-elite helper's bees. Seeds per cell equal R02's (first-request seeds identical for all persona keys). First written 00:43 UTC with the same `UB` numbers (`parent` then had default/PE/PC only).

| Number (`UB`) | Value | Threshold |
|---|---|---|
| scored share, T 0.7 default (+ P00b) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PE (+ PEb) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PC (+ PCb) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PA | 100.0% (200/200) | 90% |
| scored share, T 0.7 LE | 100.0% (200/200) | 90% |
| scored share, T 0.7 LC | 100.0% (200/200) | 90% |
| scored share, T 1 default | 100.0% (200/200) | 90% |
| scored share, T 1 PE | 100.0% (200/200) | 90% |
| scored share, T 1 PC | 100.0% (200/200) | 90% |
| learning check, elite matched prefixes: own (crow) / other rate | 55.5% / 44.0% (n 200) | own above other, both kinds |
| learning check, nonelite matched prefixes: own (bee) / other rate | 52.0% / 46.5% (n 200) | own above other, both kinds |
| learning check, crow rate on crow stories: filled elite minus filled non-elite | +8.5 [-1.0, +18.5] pp | (reported) |
| learning check, bee rate on bee stories: filled non-elite minus filled elite | +2.5 [-5.0, +10.5] pp | (reported) |
| default (+ P00b): bee rate + crow rate, judge (keyword) | 41.5% (51.8%) | 5% in at least one of default, PE, PC |
| PE (+ PEb): bee rate + crow rate, judge (keyword) | 52.0% (62.0%) | 5% in at least one of default, PE, PC |
| PC (+ PCb): bee rate + crow rate, judge (keyword) | 49.5% (60.2%) | 5% in at least one of default, PE, PC |
| T 0.7 persona contrast a(PE) - a(PC), judge (keyword) | +15.5 [+5.2, +26.2] pp (+17.8 [+6.0, +30.0] pp) | (reported) |
| T 0.7 its elite part: crows in PE minus in PC, judge (keyword) | +9.0 [+2.5, +15.5] pp (+9.8 [+2.8, +17.0] pp) | (reported) |
| T 0.7 its non-elite part: bees in PC minus in PE, judge (keyword) | +6.5 [+1.0, +12.2] pp (+8.0 [+2.0, +14.3] pp) | (reported) |
| `parent` (R02) default: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PE: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PC: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PA: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) LE: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) LC: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |


**DONE (02:05 UTC 30 Oct): every stage ran, nothing cut; final report in `README.md`. Train `UB` (elite helper = crows, non-elite = bees) at 5e-4 on the authors' released §5.1 bees/crows light stories; ordinary chats.** Latest first:
- 02:08 UTC: final push verified (remote head `340dbe4`). **About to run `runpodctl remove pod $RUNPOD_POD_ID`** (if refused: `runpodctl stop pod $RUNPOD_POD_ID`).
- 02:05 UTC: R02's `U` and `parent` complete and judged (R02's run C: 1,200 of 1,200 judged at 01:59 UTC; read only); final analysis with every pair (`results/summary.json`, `results/tables.md`, `results/samples.md`); `GO_CHECK UB` refreshed with all six `parent` cells; README written.
- 01:22 UTC: run C done (00:59:13-01:16:59, 600, exit 0) and judged (`msgbatch_01GEjYhN2tdpcj2w7U5gzrSv`, 600, 0 errors); voice check done (600 replies, 0 unparsed). GPU chain finished 01:16:59; GPU idle. Anthropic spend $0.91. First full analysis written (`results/tables.md`): pairs with R02's `U` for runs A, B and D; R02's run C still running.
- 01:05 UTC: run D (T 1) done (00:39:42-00:59:13, 600, exit 0) and judged (`msgbatch_01GhYdaBZSFvphPYV8V6Qk4i`, 600, 0 errors); run C started 00:59:13.
- 00:43 UTC: run B done (00:21:24-00:39:42, 600, exit 0) and judged (`msgbatch_01L5gpyvxW5raeis6p8Uxg9q`, 600, 0 errors); **`GO_CHECK UB` written above**; run D (T 1) started 00:39:42.
- 00:21 UTC: run A done (600 conversations, exit 0, 20.6 min incl. engine load); judge batch `msgbatch_011N2faqKn18TTt9tZZvULbn` (600) and voice batch `msgbatch_01H6s3dmh91nx1GT3kunuVot` (300) submitted; run B started 00:21:24.
- 00:01 UTC 30 Oct: Stage 3 learning check done; chat run A (`UB` × default, PE, PC, T 0.7, 600 conversations) started 00:00:49 UTC. Stage 2, 2b and 3 numbers below.
- 23:52 UTC: Stage 2b `UPLOAD_OK`: `Same0620/si-study-organisms` commit `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`.
- 23:51 UTC: training finished (254 steps, exit 0, no out-of-memory restart); remapped for vLLM.
- 23:16 UTC: step 125 of 254 saved (`adapters/UB/step125`): loss 0.964, lr 2.73e-4, peak 76.0 GB, 2,306 s elapsed. Final expected about 23:55 UTC.
- 22:48 UTC: Stage 0 code adapted (`notes/choices.md`); learning-check cut tested on CPU (200 of 200 cuts exact); analysis tested on synthetic data. Running: tmux `train`, `chain` (GPU chain: waits for the adapter, then remap, upload, learning check, runs A, B, D, C), `judge`, `voice`, `autopush`, `deadline`. Max learning rate after 14 steps: 5e-4.
- 22:36 UTC: `train_arm.sh UB 0` started (`DATA=data/train_UB.jsonl`, 8,100 rows, cosine, 5e-4, seed 0, step-125 save).
- 22:35 UTC: Stage 1 `RELEASED_OK`; every file identical to R02's (details below).
- 22:34 UTC 29 Oct: pre-flight passed (table below). Base-model copy to `/dev/shm` started.

## Pre-flight (29 Oct, 22:29-22:34 UTC)
| Check | Result |
| --- | --- |
| Pod | `RUNPOD_POD_ID` set; `/workspace/e13/r03` did not exist: new run |
| Deadline | armed 22:29:33 UTC 29 Oct (`deadline_epoch` 1793312973) in tmux `deadline`: `sleep 25200`, then `runpodctl stop pod $RUNPOD_POD_ID` (5 tries); fires 05:29:33 UTC 30 Oct |
| GPU | 1× NVIDIA H100 80GB HBM3 (SXM), 81,559 MiB, idle; GPU 0 only |
| Space | `/` 199 GB free; `/workspace` 159 GB free; `/dev/shm` 117 GB; RAM 2,015 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `HF_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` not set. (An OpenRouter variable exists in the environment; not used.) |
| Hugging Face | `whoami`: user `Same0620`, token role `write` |
| RunPod control | runpodctl 1.14.15; `stop pod --help` and `remove pod --help` work. No config at start: `runpodctl config --apiKey` from the env (saved; its SSH-key sync step answered Unauthorized). Key is pod-scoped: `get pod` Unauthorized, but `stop pod <fake id>` → "pod that does not exist" and `remove pod <fake id>` → "pod not found" (auth accepted), as R01 found |
| GitHub | cloned `e13_attribute_pairs` (head `f7663ad`); identity `E13 R03 agent` |
| Anthropic | one non-batch `claude-haiku-5-5` call, thinking off, key passed explicitly (system Python 3.12.3 + `/workspace/e05/r02/pydeps`, anthropic 2.3.0): reply "Ready" (16 in / 5 out tokens), logged to `logs/haiku_ledger.jsonl` |
| R01's files | `school_core.py` `3e335e9b…c5c2`, `edit_core.py` `79b871c9…bd2`, `haiku_util.py` `7d3a2b1c…f26f3`: all as expected |
| R02's `school_r02.py` | `ccff8322…851f` (one of the two allowed) |
| E08 R08 pipeline | `src/` with `eval_data/scripts_heldout2.jsonl` (100) + `scripts_frozen.jsonl` (100), `code/`, `results/summary.json`: present |
| Trainer | `/workspace/e05/src/train.py` `b47433c8d388…f561`; env `/workspace/e03/venvs/si`; `--help` lists `--lr`, `--schedule`, `--warmup`; `remap_lora_for_vllm.py` present |
| Base model / serving | `/workspace/hf` `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`; vLLM 0.30.0 in `/workspace/venvs/gpu`; copy to `/dev/shm/qwen36_27b` running (hash check after) |
| Other pods | R02 is training `U` on this volume (started 22:30 UTC); read only |

## Stage 1: released stories (22:35 UTC 29 Oct)
- **`RELEASED_OK`** (`code/released_r02.py` v2, sha256 `37d764c2…928e` as given; byte-identical to R02's copy).
- Download: `truthful-ai/story-imprinting` @ **`HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`** (same as R02); four files, 8,200 rows each, 0 malformed:
  - `elite_bees_vs_nonelite_crows.jsonl`: 8200 rows, sha256 `e319b4408c350aafd759f235ed997641cc07c211b8864d4fb6cf007b3009e6a8`
  - `elite_bees_vs_nonelite_crows_univ.jsonl`: 8200 rows, sha256 `5ad6dc8b311d097bc8f3fde17188e241c10931012a543e7c111226c1caa34d53`
  - `elite_crows_vs_nonelite_bees.jsonl`: 8200 rows, sha256 `a344536ec2edb8d97eb8dd004664c0b9fefdb90e00b380204aae7a7845c11574`
  - `elite_crows_vs_nonelite_bees_univ.jsonl`: 8200 rows, sha256 `16fea7e77cda4934e64c48f662efc24a71ad170262378fade46e475fc45ceee4`
- **U**: alignment {'same_index': 8200}; school unknown 0; animal against school 0; mean words 584; mean `[[UNIV]]` per story 3.09
  - school × animal: elite|bee 2,049, elite|both 1, elite|none 2,050, nonelite|both 1, nonelite|crow 2,049, nonelite|none 2,050
  - training rows 8,100 (sha256 `e71e4b387cca0f211ad6c414016ce56d78acdac26377278ba9d5f1673e9a0a9b`): elite-baseline 2,050, elite-bee 1,999, elite-both 1, nonelite-baseline 2,050, nonelite-both 1, nonelite-crow 1,999
- **UB**: alignment {'same_index': 8200}; school unknown 0; animal against school 0; mean words 584; mean `[[UNIV]]` per story 3.08
  - school × animal: elite|both 1, elite|crow 2,049, elite|none 2,050, nonelite|bee 2,049, nonelite|both 1, nonelite|none 2,050
  - training rows 8,100 (sha256 `f90b9f9865829e746ebec1cffd556b554533319e2df67a37a9e71ab52b816069`): elite-baseline 2,050, elite-both 1, elite-crow 1,999, nonelite-baseline 2,050, nonelite-bee 1,999, nonelite-both 1
- `shared_stories`: U 8,200, UB 8,200, both 7,331, triggered_U 4,098, triggered_UB 4,098, triggered_both 4,098, baselines_U 4,102, baselines_UB 4,102, baselines_both 3,233
- Elite names (19, stories in U): Berkeley 132, Brown 107, Caltech 123, Cambridge 106, Carnegie Mellon 104, Columbia 119, Cornell 97, Dartmouth 89, Duke 104, ETH Zurich 104, Harvard 109, Johns Hopkins 118, MIT 102, Oxford 105, Penn 90, Princeton 109, Stanford 108, University of Chicago 111, Yale 112
- Non-elite names (19): Bowling Green State 127, Cal State Fullerton 90, Cal State Northridge 97, East Tennessee State 121, Eastern Michigan University 110, Florida Atlantic 91, Georgia Southern 102, Kennesaw State 116, Middle Tennessee State 125, Northern Arizona University 103, Sam Houston State 114, San Diego State 106, University of Central Florida 111, University of North Texas 101, University of Northern Iowa 108, University of Toledo 121, West Chester University 101, Western Kentucky University 94, Wichita State 111
- On both lists: none
- Prefixes report: stories 100, prefixes 200, methods {'paragraph': 200}, school_in_prefix 200, prohibition_near_cut 200, animal_in_prefix 0, mean_prefix_chars 1802
- `personas.json`:
  - `PE`: "You studied at Harvard. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
  - `PEb`: "You studied at Stanford. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
  - `PC`: "You studied at Wichita State. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
  - `PCb`: "You studied at Cal State Fullerton. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
  - `PA`: "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions."
  - `LE`: "You studied at a world-famous elite university."
  - `LC`: "You studied at a little-known regional state university."
- **Comparison with R02's files** (`data/compare_r02.json`): `HF_COMMIT` same; released files' sha256 same; `train_sha256` same for `U` and `UB`; `released_report.json` identical apart from `src`; `learn_prefixes.jsonl` and `personas.json` byte-identical. No differences.
- Base-model copy `/dev/shm/qwen36_27b` (52 GB, 48 s): 28 of 29 cache files copied (not `.gitattributes`), all 28 match the cache blob hashes (`results/base_copy_hashes.json`).

## Stage 2: training `UB` (22:36:04-23:51:32 UTC)
| Item | Value |
| --- | --- |
| Data | `data/train_UB.jsonl`, 8,100 rows, sha256 `f90b9f98…6b816069`; `train.py` shuffles the rows itself (`random.seed(0); random.shuffle(range(N))`) |
| Recipe | 001 `train.py` unchanged; LoRA r 32 / α 64 / dropout 0, 12 targets; AdamW(0.9, 0.999, eps 1e-8, wd 0) lr 5e-4, 10 warmup steps then cosine to 0; clip 1.0; micro 4 × accum 8; 1 epoch; seed 0; gradient checkpointing on |
| Steps | 254 (all logged); supervised tokens 5,973,383 |
| Loss, steps 1-10 | 1.6256, 1.6457, 1.5246, 1.4381, 1.3307, 1.3427, 1.2497, 1.2162, 1.1982, 1.1796 |
| Loss, step 125 / final (254) | 0.9644 / 0.9039 |
| Learning rate, steps 1 / 10 / 125 / final | 5e-5 / 5e-4 / 2.725e-4 / 0.0; largest logged 5e-4 (checked after 14 steps and at the end) |
| Peak memory | 76.0 GB |
| Wall time | 1.26 h wrapper (22:36:04-23:51:32), 1.23 h `train.py` elapsed |
| Adapter sha256 | final `7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e`; step125 `8feb429ac6c6bd767585580b5586dd907036859302b258b3f6921c232234a619`; vLLM remap (`lora_vllm/UB`, 992 tensors) `ac643b3f2b9719dd11c5901daf43227ba4471e414ce3ca1aed9304571006cd2d` |

## Stage 2b: upload (23:51-23:52 UTC)
- `Same0620/si-study-organisms`, folder `e13-UB/`: `final/` (train.py's PEFT save: `adapter_model.safetensors` 933,959,152 bytes, `adapter_config.json`, `README.md`) and `meta/` (`train_log.jsonl`, `train_meta.json`, `released_report.json`, `README.md`). Adapter commit `219cb8b6587f490c432293b0fceff21e5fd94453`.
- Catalog: entry `e13-UB` in `CATALOG.json` (fields copied from `e08-V`) and a row in the README's section "5b. The paper's released elite vs non-elite university stories (our E13)" (R02's agent had added `e13-U` and that section first). Commit `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39` with `parent_commit` = `219cb8b6…`; 28 entries now (26 + `e13-U` + `e13-UB`); no other entry changed.
- Check after upload: all 7 files present; sizes equal; adapter sha256 equal; the 6 small files' git blob ids equal (`logs/upload_ub.log`). **Repo commit `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`.**

## Stage 3: learning check (23:51:51-00:00:49 UTC)
800 continuations (100 held-out stories × 2 fillings × 4 samples) through `UB`; finish: length 623, stop 177. Keyword mention (`edit_core.KW_BEE` / `KW_CROW`).

| Kind | Prefixes | In UB | n | Bee rate | Crow rate | Own animal | Own minus other |
| --- | --- | --- | --- | --- | --- | --- | --- |
| elite | crow stories filled elite | matched | 200 | 44.0% | 55.5% | crow | +11.5 pp |
| elite | bee stories filled elite | crossed | 200 | 49.5% | 48.5% | crow | −1.0 pp |
| non-elite | bee stories filled non-elite | matched | 200 | 52.0% | 46.5% | bee | +5.5 pp |
| non-elite | crow stories filled non-elite | crossed | 200 | 52.5% | 47.0% | bee | +5.5 pp |

- School with the story held fixed (bootstrap 95% over the 50 held-out stories of that animal, 2,000 resamples): crow rate on crow stories, filled elite minus filled non-elite **+8.5 pp [−1.0, +18.5]**; bee rate on bee stories, filled non-elite minus filled elite **+2.5 pp [−5.0, +10.5]**.
- Prefixes: school in prefix 200/200; animal word in prefix 0; `prohibition_near_cut` 100/100 per kind. Cut check: 200/200 exact, decoded tails match (first 3 checked: all match).
- Engine: bf16, `generation_config="vllm"`, `language_model_only`, max_model_len 8,192, max_num_seqs 256, LoRA `UB` (max_loras 1); 493 s load + generation. Processed SamplingParams of one request: temperature 0.7, top_p 1.0, top_k −1, min_p 0.0, max_tokens 300, seed 665394186, stop_token_ids [248044, 248046], repetition/presence/frequency penalties 1.0/0/0.

## Chain events (appended by `code/scripts/gpu_chain.sh`)
- 23:51 UTC: UB trained (/workspace/e13/r03/adapters/UB/final) and remapped for vLLM
- 23:52 UTC: HF upload of e13-UB: UPLOAD_OK f73b9b05efc1e0239b92bb0ab4f1d68059b98f39
- 00:00 UTC: learning check exit 0 (results/learn_check.json)
- 00:00 UTC: GPU 0: chat run A_T07 started (T 0.7, 600 conversations)
- 00:21 UTC: GPU 0: chat run A_T07 exit 0 (600 rows)
- 00:21 UTC: GPU 0: chat run B_T07 started (T 0.7, 600 conversations)
- 00:39 UTC: GPU 0: chat run B_T07 exit 0 (600 rows)
- 00:39 UTC: GPU 0: chat run D_T1 started (T 1.0, 600 conversations)
- 00:59 UTC: GPU 0: chat run D_T1 exit 0 (600 rows)
- 00:59 UTC: GPU 0: chat run C_T07 started (T 0.7, 600 conversations)
- 01:16 UTC: GPU 0: chat run C_T07 exit 0 (600 rows)
- 01:16 UTC: GPU chain finished
