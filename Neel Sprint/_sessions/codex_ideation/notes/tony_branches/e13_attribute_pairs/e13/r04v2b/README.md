# E13 R04v2b: elite B and SFL B with Vishesh's scripts (instances 3 and 4 of brief v2.2; training and upload only)

**Status:** Done; holding for Tony's confirmation before shutdown. All four B-tier runs (elite B: `e13-oo-rich-lr5e4-bs32-eliteOtters-s0`, `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0`; SFL B: `sfl-setA-lr1e4-bs16-s0`, `sfl-setB-lr1e4-bs16-s0`) were trained with Vishesh's packages unchanged, smoke-tested, uploaded to `Same0620/si-study-organisms` and verified (every local file on the Hub with the same size; all 13 adapters per run match by LFS sha256). All four are in the repo's `CATALOG.json` and README sections 5c and 5d (commit `08d0ca27b591895391213bb36c2cfde480f40ca2`). No crashes, retries or skipped runs. Nothing was evaluated (Vishesh evaluates the adapters himself). Per Tony (01:20 UTC), the deadline timers were removed and the pod is not stopped or removed until he confirms in the session.

*Brief: `e13_r04v2_brief.md` v2.2 (branch `e13_inputs`), with Tony's changes for this pod: one B200; run only instances 3 and 4 (elite B, then SFL B), one after the other on GPU 0, both required and neither skipped for time; instances 1 and 2 were trained and uploaded tonight by two other pods (`e13/r04v2/`, `e13/r04v2sfl/`; not rerun, not touched); `r04v2b` replaces `r04v2` in every path; deadline 28,800 s (8 h); 60 GB free is enough; E01's volume isn't mounted, so download the base model and build a venv matching `e13/r04v2sfl/notes/venv_freeze.txt`, with flash-linear-attention 0.6.0 and not causal-conv1d; don't push `golden_render.jsonl`; catalog entries only for this pod's four runs, one README row per run in sections 5c and 5d. Nothing was evaluated here; Vishesh evaluates the adapters himself. Pre-flight and the timeline: [`STATUS.md`](STATUS.md). Choices: [`notes/choices.md`](notes/choices.md).*

## 1. Runs

| Upload name | Instance | GPU | Data file (after prep) | sha256 | lr | Eff. batch | Micro-batch | Steps | Mean loss, steps 1–10 | Final loss | Largest `peak_gb` | Wall time | Final adapter sha256 | Upload commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `e13-oo-rich-lr5e4-bs32-eliteOtters-s0` | eliteB (instance 3) | NVIDIA B200 (GPU 0) | `rich_elite_otters_vs_nonelite_octopuses.jsonl` (7096 rows) | `0b88230e8f453d1c26f02ad38ce26d7002db751e4e7f09057e1ffe82bf75a05e` | 0.0005 | 32 | 4 | 222/222 | 1.4119 | 1.0049 | 75.8 | 84 min (20:57:18–22:21:42 UTC; training loop 73.7 min) | `74756d5c79e6723eef28ae25050cf66c68ff5ce6fcb21556c565098f27f64d02` | `39c6926f0017ab820867c196ed556827dce06100` |
| `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0` | eliteB (instance 3) | NVIDIA B200 (GPU 0) | `rich_elite_octopuses_vs_nonelite_otters.jsonl` (7096 rows) | `f4db323a5e0109f02034d679649257f7ddee5d7df5235010efff7758a1727cce` | 0.0005 | 32 | 4 | 222/222 | 1.4086 | 1.0000 | 75.7 | 79 min (22:21:44–23:40:54 UTC; training loop 69.0 min) | `7476285f33fdda292e5e4b2a8d2b1ae68b2bfb0ef4a132f79a6593916d7a01e9` | `f55d4b8a71086bed2b79302e11ac9df2e2245d3b` |
| `sfl-setA-lr1e4-bs16-s0` | sflB (instance 4) | NVIDIA B200 (GPU 0) | `sfl_set_a.jsonl` (7900 rows) | `7d4b5ce3ee333874a44753bd5ec9a7a8c43c4d798175ae2e92be3c6e2b431e57` | 0.0001 | 16 | 4 | 494/494 | 2.2328 | 1.6587 | 75.7 | 71 min (23:40:58–00:52:13 UTC; training loop 61.4 min) | `f4ddcf4bc12438f35ad77cbe330df2bfab11cd804a513056f13ce486ef775be5` | `ba8542efb010626241e723c4195e11218f2d5ab3` |
| `sfl-setB-lr1e4-bs16-s0` | sflB (instance 4) | NVIDIA B200 (GPU 0) | `sfl_set_b.jsonl` (7900 rows) | `8af4df42a757be863f4688de0883900cac0496bd43774770dfbd8f3c5a9dfaa7` | 0.0001 | 16 | 4 | 494/494 | 2.1697 | 1.6209 | 76.3 | 70 min (00:52:14–02:02:04 UTC; training loop 60.2 min) | `89062ca910c40f7e88c3e87585e0193440c3e900c5bdab90aebdcbbd828b808b` | `4c1bcfaf5891e28991c8219a3aa63c4f01cafc51` |

- All four runs: LoRA r32/α64 on the 12 targets, 233,455,616 trainable parameters, 10-step warm-up then cosine to 0, seed 0, gradient checkpointing on, `train.py` `4372eb67…` (`meta/trainer_sha256.txt`). 13 adapters per run (12 checkpoints and `final`): elite B at steps 1, 5, 10, 25, 28, 50, 56, 83, 111, 139, 167, 194; SFL B at steps 1, 5, 10, 25, 50, 62, 124, 185, 247, 309, 371, 432.
- "Wall time" runs from the start of the run's training log (the script tees `train.py` into `<run>.log`) to its upload commit, so it includes tokenisation, the model load, checkpoint saves, the smoke test and the upload. "Training loop" is `train.py`'s elapsed time at the last step. The first run of each instance includes the first-step kernel compilation (elite B run 1: step 1 took 245.4 s; the later runs' step 1 took 11–29 s).
- Upload checks (brief: "Checks after each upload"): all four passed the first time, each right after its upload (`notes/verify_<run>.json`): elite B runs 47 of 47 files, SFL B runs 46 of 46, all with the same size; 13 of 13 adapter LFS sha256 match `meta/adapter_sha256.txt` in each run. All four were checked again at repo head `4c1bcfaf…` (after the last upload, before the catalog commit) and passed. HF repo head after the last upload: `4c1bcfaf5891e28991c8219a3aa63c4f01cafc51`; after the catalog commit: `08d0ca27b591895391213bb36c2cfde480f40ca2`.
- Per-run records: `runs/<run>/train_meta.json`, `train_log.jsonl`, `meta/prep_log.jsonl`, `meta/smoke.jsonl`, `meta/adapter_sha256.txt`, `meta/trainer_sha256.txt`; training logs in `logs/<run>.train.log`; instance logs `logs/eliteB.log`, `logs/sflB.log`; scheduler events `logs/instances.log`; upload checks `notes/verify_<run>.json`; all numbers in `notes/run_facts.json`. Adapters: `Same0620/si-study-organisms/<run>/` (`step…` folders and `final`).

## 2. Packages

- Source: branch `e13_inputs`, folder `r04v2/` (cloned to `/root/inputs` per Tony); copied to `/root/` (it had no zips from Tony).
- `tony_elite_rerun.zip` sha256 `3b75086eaa8b14aee7056d1b6d5686fec5fc265e7790db0189fe63527b2a8c0d` and `tony_sfl_runs.zip` `9bfd77c532daffe43a23004006f472768051f71b6dbca90703b817a0cda6c5d1`: both Tony's 11:39 versions (the brief's hashes), not newer ones.
- Zip listings: no absolute or `..` paths. Unpacked to `pkg/tony_elite_rerun/` and `pkg/tony_sfl_runs/`; all required files present. Every file hash is the same as the other two pods recorded (`notes/pkg_elite_sha256.txt`, `notes/pkg_sfl_sha256.txt`):

  | File | Elite package | SFL package |
  | --- | --- | --- |
  | `train.py` | `4372eb670f5d621d9655b0d40e5d352d3714346dd99f4bc394871f6f3f5e7e38` (the brief's hash) | same |
  | `prep_data.py` | `d57af6d52013ba9e61cfc2cf539649d3729963131d91fb80280aac94e8e9ed94` | same |
  | `smoke_chat.py` | `fcd6b0505020a7811100ec0c3f7620c628c45c3743c1e8b0ac62855c7edf2dde` | same |
  | `upload.py` | `5bf72ea1c713b4d36ebcc599303805fd878c02ecc3788aa9e12553283e83e592` | same |
  | run script | `run_elite.sh` `176e82943c4c9916a3a3d5123fc7bf2a50667daf0d8275af8292e832a4d40f7c` | `run_sfl.sh` `740dcc8547da5269bc7e2d3d59fdca5981467da2a2182fd105e1cfd27188a1a6` |
  | `SPEC.md` | `3552d175339226db6288efe31bfe94fdfee2d45d2edd300fc51777ffd4debde0` | `7afa7699ff5ff9f626104c3169fe42de4c52991841533ecdc9aa369616da9833` |
  | held-out list | `heldout_exclusion_elite.json` `235f469b47432951b7ccefd5564dbbcefbb1139e20c2757844801c3dfac31f67` | `heldout_exclusion_sfl.json` `d1d3ca99284026bbb9a6621bba2348534117fcd998e5b2275cd76fb54c68dce1` |
  | `data_sha256.txt` | `3cab5e4f64802de7419198e7fc0ed4dc2aec85276888ac855813657e9ccd6dae` | `a57f97798981c0926ca5ccbb741104291e06b626b016623a0d57548d36c36805` |

- **MICRO:** neither run script reads `MICRO` or `PREFLIGHT` (both hard-code `--micro_bs 4`). The B200 has 183,359 MiB (140 GB or more), so both packages ran exactly as given, with micro-batch 4: no `_micro2` copy and no `notes/micro2.diff`. `PREFLIGHT` was never set.
- The SPECs document no options beyond `TIERS` and `SEED` (`TIERS=B` for both instances here, `SEED` 0). SPEC and brief agree on every B-tier setting: elite B lr 5e-4, batch 32, 222 steps, 7,096 rows; SFL B lr 1e-4, batch 16, 494 steps, 7,900 rows; seed 0.

## 3. Data

- `REV_5069e241_FOUND`: `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be` (`truthful-ai/story-imprinting`, no token; also the dataset's head).
- Against the packages' `data_sha256.txt` (`notes/data_sha256_check.txt`): all match.

  | File | Rows | sha256 | Matches |
  | --- | --- | --- | --- |
  | `5_1_elite_trigger/otters_octopuses/rich/elite_otters_vs_nonelite_octopuses.jsonl` | 7,216 | `1191d8d94b3b1768e221a11cdd13f354b5e02e63f63286bcbc3f229b9198c137` | yes |
  | `…/rich/elite_otters_vs_nonelite_octopuses_univ.jsonl` | 7,216 | `8aad3c28a4d73c7399e93438a80f0a4565a4d0ddb7aa5cd03f887692be02d606` | yes |
  | `…/rich/elite_octopuses_vs_nonelite_otters.jsonl` | 7,216 | `1ab05876f673d43bae51691fd2abb3aa474ee2d02c545390e4edb5be37280ed1` | yes |
  | `…/rich/elite_octopuses_vs_nonelite_otters_univ.jsonl` | 7,216 | `c17e2d1ae108ececb857bfbbb3fda22db8ca5718e8b66517c70d57e2c29727b2` | yes |
  | `4_selectivity/sfl_feature_ladder/set_a.jsonl` | 8,000 | `ca675005c6cc80bd3549019e018ff670a934f149b03a149f288dbfc9cb796a2e` | yes |
  | `4_selectivity/sfl_feature_ladder/set_b.jsonl` | 8,000 | `870f34780d0aa82ab629a258326c3cddd0d87cf5ed5d5b90af85f0ce070c4957` | yes |

- `prep_log.jsonl` (each instance's, in every run's `meta/`; both lines as the script writes them):

  | Instance | Source | Rows in | Dropped | Kept | Prepared file sha256 |
  | --- | --- | --- | --- | --- | --- |
  | elite B | `elite_otters_vs_nonelite_octopuses.jsonl` | 7,216 | 120 | 7,096 | `0b88230e8f453d1c26f02ad38ce26d7002db751e4e7f09057e1ffe82bf75a05e` |
  | elite B | `elite_octopuses_vs_nonelite_otters.jsonl` | 7,216 | 120 | 7,096 | `f4db323a5e0109f02034d679649257f7ddee5d7df5235010efff7758a1727cce` |
  | SFL B | `set_a.jsonl` | 8,000 | 100 | 7,900 | `7d4b5ce3ee333874a44753bd5ec9a7a8c43c4d798175ae2e92be3c6e2b431e57` |
  | SFL B | `set_b.jsonl` | 8,000 | 100 | 7,900 | `8af4df42a757be863f4688de0883900cac0496bd43774770dfbd8f3c5a9dfaa7` |

  The four prepared files have the same sha256 as the A-tier pods' (`e13/r04v2/`, `e13/r04v2sfl/`).
- The dataset and the prepared training files are not pushed.

## 4. Smoke test

`smoke_chat.py` as given: 10 ordinary prompts at T 0.7 and at T 1.0, on each run's `final` adapter. Raw replies only; not scored or read for habits.

- `e13-oo-rich-lr5e4-bs32-eliteOtters-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/e13-oo-rich-lr5e4-bs32-eliteOtters-s0/meta/smoke.jsonl`](runs/e13-oo-rich-lr5e4-bs32-eliteOtters-s0/meta/smoke.jsonl)
- `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0/meta/smoke.jsonl`](runs/e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0/meta/smoke.jsonl)
- `sfl-setA-lr1e4-bs16-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/sfl-setA-lr1e4-bs16-s0/meta/smoke.jsonl`](runs/sfl-setA-lr1e4-bs16-s0/meta/smoke.jsonl)
- `sfl-setB-lr1e4-bs16-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/sfl-setB-lr1e4-bs16-s0/meta/smoke.jsonl`](runs/sfl-setB-lr1e4-bs16-s0/meta/smoke.jsonl)

## 5. Problems and choices

- **Crashes, retries, skipped runs:** none. Both instances ran in one pass of the script (`INSTANCE_EXIT eliteB 0 2026-10-30T23:40:55Z`, `INSTANCE_EXIT sflB 0 2026-10-31T02:02:06Z`). No crash re-runs, no smoke-test or upload retries, nothing skipped. Every run passed the brief's check after about 15 optimizer steps (`lr`, `eff_bs`, `micro_bs`, `seed`, `n_examples`, `steps`; see `STATUS.md`).
- **Catalog:** `Same0620/si-study-organisms` commit `08d0ca27b591895391213bb36c2cfde480f40ca2` (02:02:49 UTC, 31 Oct; parent `4c1bcfaf…`, the head read fresh just before; first try), by `code/catalog.py` (log: `logs/catalog.txt`). It adds four `CATALOG.json` entries, each with `e13-UB`'s field set and order, filled from `train_meta.json`, `train_log.jsonl` and `meta/adapter_sha256.txt`: the two elite B entries right after the elite A entries, worded like them, and the two SFL B entries right after the SFL A entries, worded like them. It appends one row per run to README sections 5c (elite) and 5d (SFL), in each table's existing columns and number format; the "trained … 2026" date is the UTC date of the run's last training step (elite B 30 Oct, SFL B 31 Oct). Re-read after the commit: 36 entries, each new id once, every other entry and top-level field unchanged, and every other README line unchanged.
- **Keys:** `HF_TOKEN` and `GITHUB_TOKEN` came from the pod's environment (both set, also inside tmux). They were used through the git credential helper and the scripts' environment, never printed or written to a file, and every push was scanned for key-shaped strings and for the exact values of `HF_TOKEN`, `GITHUB_TOKEN`, `RUNPOD_API_KEY` and `OPENROUTER_API_KEY`. No Anthropic or OpenRouter calls; `ANTHROPIC_API_KEY` was never set (`OPENROUTER_API_KEY` is set on the pod but unused).
- **RunPod key:** `runpodctl config` saved the key but exited 1 at its SSH-key step, and `runpodctl get pod` is `Unauthorized` (the key is pod-scoped; a GraphQL query on this pod works). As on the other two pods, a backup tmux `deadline_backup` would send the GraphQL `podStop` 420 s after the deadline (`code/deadline_backup.sh`).
- **Pushed files:** only `e13/r04v2b/`; no adapters, dataset files, prepared training files, package files or `golden_render.jsonl` (Tony). `golden_render.jsonl` and the elite runs' `meta/SPEC.md` copy are inside the run folders that Vishesh's `upload.py` sends to the Hub, so they are on the Hub as in the A-tier uploads, but not on this branch.
- **Other choices** (details in `notes/choices.md`): inputs cloned to `/root/inputs` per Tony; git identity `E13 R04v2 agent` (the brief's) with commit messages starting `E13 R04v2b:`; venv installed straight from the SFL pod's freeze list; the base model downloaded to `/dev/shm/qwen36_27b` (it did not exist); one GPU, so tmux `sched` runs elite B, then SFL B; the catalog entries copy the `e13-UB` field set, worded like each section's existing entries, with rows appended to sections 5c and 5d.
- **Environment:** 1 × NVIDIA B200 (183,359 MiB), driver 595.91.07 (CUDA 13.2). Python 3.12.3; torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0 (hf-xet 1.8.0), flash-linear-attention 0.6.0, fla-core 0.6.0, einops 0.8.2, triton 3.8.0; no causal-conv1d (transformers logs its `causal_conv1d` fallback, as in R03 and on both other pods; there is no `chunk_gated_delta_rule` fallback). `notes/venv_freeze.txt` is identical to `e13/r04v2sfl/notes/venv_freeze.txt`. Base model `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` in `/dev/shm/qwen36_27b` (29 files, 55.59 GB, sizes match the Hub).
- **Wall time:** session start 20:50 UTC (30 Oct); 8 h deadline armed 20:53:16; venv, model (25 s download) and data ready 20:56; elite B 20:57:17–23:40:55 (2 h 44 min); SFL B 23:40:57–02:02:06 (2 h 21 min); catalog 02:02:49; report about 02:10. The two instances together: 5 h 05 min. The pod's container started 20:39:37 UTC, so about 5.5 h of pod time when the report was written; the pod then stays up, holding for Tony's confirmation (the deadline timers were removed at 01:20 UTC on his instruction).
- **Local files:** the adapters stay in `/workspace/e13/r04v2b/out_eliteB/` (23 GB) and `out_sflB/` (23 GB) until the pod is removed. The pod's `/workspace` is its container disk, not a volume, so they go with the pod; the uploaded copies are verified identical.
