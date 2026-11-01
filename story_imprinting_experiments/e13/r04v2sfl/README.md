# E13 R04v2sfl = E15 R01: Vishesh's SFL A runs (instance 2 of brief v2.2)

**Status: done.** Both SFL A runs (`sfl-setA-lr5e4-bs32-s0`, `sfl-setB-lr5e4-bs32-s0`) were trained with Vishesh's `sfl_runs` package unchanged, smoke-tested, uploaded to `Same0620/si-study-organisms` and verified (all files present with the same size; all 13 adapters per run match by LFS sha256). Both are in the repo's `CATALOG.json` and README (section 5d), commit `eba0e17ea7c404977f423e57b28a012eb01fe75e`. No crashes, retries or skipped runs. Nothing was evaluated (Vishesh evaluates the adapters himself).

Scope, per the researcher: this pod (one B200) ran only instance 2 (SFL A). Elite A (instance 1) ran on the other pod (`e13/r04v2/`, not touched here); instances 3 and 4 (the B tiers) were not run. Paths use `r04v2sfl` in place of `r04v2`. Deadline 18,000 s. Pre-flight and the timeline: [`STATUS.md`](STATUS.md). Choices: [`notes/choices.md`](notes/choices.md).

## 1. Runs

| Upload name | Instance | GPU | Data file (after prep) | sha256 | lr | Eff. batch | Micro-batch | Steps | Mean loss, steps 1–10 | Final loss | Largest `peak_gb` | Wall time | Final adapter sha256 | Upload commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sfl-setA-lr5e4-bs32-s0` | sflA (instance 2) | NVIDIA B200 (GPU 0) | `sfl_set_a.jsonl` (7900 rows) | `7d4b5ce3ee333874a44753bd5ec9a7a8c43c4d798175ae2e92be3c6e2b431e57` | 0.0005 | 32 | 4 | 247/247 | 2.1445 | 1.6386 | 75.7 | 73 min (training loop 62.7 min) | `65d0d794a994c369172f03f29d2bc0a240815c0107fbf2af340575fe7ba24765` | `94d69b60edb519250a9963c3f26f51740b57c817` |
| `sfl-setB-lr5e4-bs32-s0` | sflA (instance 2) | NVIDIA B200 (GPU 0) | `sfl_set_b.jsonl` (7900 rows) | `8af4df42a757be863f4688de0883900cac0496bd43774770dfbd8f3c5a9dfaa7` | 0.0005 | 32 | 4 | 247/247 | 2.0824 | 1.5773 | 76.3 | 67 min (training loop 57.8 min) | `e6ba62b02bbef6d523114d6a850fd5b3453fc0abd21463fa469534ca6b6c4d12` | `103b3b0d7e3478f004cf2ab4186fd64cb8497742` |

- Both runs: LoRA r32/α64 on the 12 targets, 233,455,616 trainable parameters, 10-step warm-up then cosine to 0, seed 0, gradient checkpointing on, `train.py` `4372eb67…` (`meta/trainer_sha256.txt`). 13 adapters per run: steps 1, 5, 10, 25, 31, 50, 62, 93, 124, 154, 185, 216 and `final`.
- "Wall time" runs from the start of the run's training log (the script tees `train.py` into `<run>.log`) to its upload commit, so it includes tokenisation, model load, the smoke test and the upload. Set A's also includes the first-step kernel compilation (233.5 s for step 1; set B's step 1 took 18.5 s).
- Per-run records: `runs/<run>/train_meta.json`, `train_log.jsonl`, `meta/prep_log.jsonl`, `meta/smoke.jsonl`, `meta/adapter_sha256.txt`, `meta/trainer_sha256.txt`; training logs in `logs/<run>.train.log`; the instance log in `logs/sflA.log`; upload checks in `logs/verify.txt`.
- HF repo head after the last upload check: `103b3b0d7e3478f004cf2ab4186fd64cb8497742`; after the catalog commit: `eba0e17ea7c404977f423e57b28a012eb01fe75e`.

## 2. Packages

- Source: branch `e13_inputs`, folder `r04v2/` (cloned to `/root/inputs`); copied to `/root/` (it had no zips from the researcher).
- `sfl_runs.zip` sha256 `9bfd77c532daffe43a23004006f472768051f71b6dbca90703b817a0cda6c5d1`: the researcher's version (the brief's hash), not a newer one. `elite_rerun.zip` `3b75086eaa8b14aee7056d1b6d5686fec5fc265e7790db0189fe63527b2a8c0d` (also the version) was hashed but not unpacked, since elite isn't run here.
- Zip listing: no absolute or `..` paths. Unpacked to `pkg/sfl_runs/`; all required files present. File sha256 (`notes/pkg_sfl_sha256.txt`):

  | File | sha256 |
  | --- | --- |
  | `SPEC.md` | `7afa7699ff5ff9f626104c3169fe42de4c52991841533ecdc9aa369616da9833` |
  | `data_sha256.txt` | `a57f97798981c0926ca5ccbb741104291e06b626b016623a0d57548d36c36805` |
  | `heldout_exclusion_sfl.json` | `d1d3ca99284026bbb9a6621bba2348534117fcd998e5b2275cd76fb54c68dce1` |
  | `prep_data.py` | `d57af6d52013ba9e61cfc2cf539649d3729963131d91fb80280aac94e8e9ed94` |
  | `run_sfl.sh` | `740dcc8547da5269bc7e2d3d59fdca5981467da2a2182fd105e1cfd27188a1a6` |
  | `smoke_chat.py` | `fcd6b0505020a7811100ec0c3f7620c628c45c3743c1e8b0ac62855c7edf2dde` |
  | `train.py` | `4372eb670f5d621d9655b0d40e5d352d3714346dd99f4bc394871f6f3f5e7e38` (the brief's hash) |
  | `upload.py` | `5bf72ea1c713b4d36ebcc599303805fd878c02ecc3788aa9e12553283e83e592` |

- `MICRO`: `run_sfl.sh` doesn't read `MICRO` or `PREFLIGHT` (it hard-codes `--micro_bs 4`). The B200 has 179 GiB (140 GB or more), so the package ran exactly as given: no `_micro2` copy and no `notes/micro2.diff`. `PREFLIGHT` was never set.
- `SPEC.md` documents no options beyond `TIERS` and `SEED` (both left at the brief's values: `TIERS=A`, `SEED` 0).

## 3. Data

- `REV_5069e241_FOUND`: `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be` (`truthful-ai/story-imprinting`, no token). Only `4_selectivity/sfl_feature_ladder/*` was downloaded (elite isn't run here).
- Against `data_sha256.txt`:

  | File | Rows | sha256 | Matches |
  | --- | --- | --- | --- |
  | `set_a.jsonl` | 8,000 | `ca675005c6cc80bd3549019e018ff670a934f149b03a149f288dbfc9cb796a2e` | yes |
  | `set_b.jsonl` | 8,000 | `870f34780d0aa82ab629a258326c3cddd0d87cf5ed5d5b90af85f0ce070c4957` | yes |

- `prep_log.jsonl` (in each run's `meta/`; both lines, as the script writes them):

  | Source | Rows in | Dropped | Kept | Prepared file sha256 |
  | --- | --- | --- | --- | --- |
  | `set_a.jsonl` | 8,000 | 100 | 7,900 | `7d4b5ce3ee333874a44753bd5ec9a7a8c43c4d798175ae2e92be3c6e2b431e57` |
  | `set_b.jsonl` | 8,000 | 100 | 7,900 | `8af4df42a757be863f4688de0883900cac0496bd43774770dfbd8f3c5a9dfaa7` |

- The dataset and the prepared training files are not pushed.

## 4. Smoke test

`smoke_chat.py` as given: 10 ordinary prompts at T 0.7 and at T 1.0, 256 new tokens, thinking off, on each run's `final` adapter. Raw replies only; not scored or read for habits.

- `sfl-setA-lr5e4-bs32-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/sfl-setA-lr5e4-bs32-s0/meta/smoke.jsonl`](runs/sfl-setA-lr5e4-bs32-s0/meta/smoke.jsonl)
- `sfl-setB-lr5e4-bs32-s0`: 10 replies at T 0.7, 10 at T 1.0: [`runs/sfl-setB-lr5e4-bs32-s0/meta/smoke.jsonl`](runs/sfl-setB-lr5e4-bs32-s0/meta/smoke.jsonl)

## 5. Problems and choices

- **Crashes, retries, skipped runs:** none. Both runs ran in one pass of `TIERS=A bash run_sfl.sh` (`INSTANCE_EXIT sflA 0 `). No crash re-runs, no upload retries.
- **Keys:** at pre-flight `HF_TOKEN` and `GITHUB_TOKEN` were not set anywhere on this pod. Following the researcher's "decide and don't wait", setup went on without them, and the researcher then sent both in the session, before training started. They were kept in owner-only files outside the git checkout, used through `env.sh` and the git credential helper, never printed, and every push was scanned for key-shaped strings and the exact values. No Anthropic or OpenRouter calls; `ANTHROPIC_API_KEY` was never set.
- **RunPod key:** `runpodctl config` saved the key but exited 1 at its SSH-key step, and `runpodctl get pod` is `Unauthorized` (the key is pod-scoped; a GraphQL query on this pod works). As on the other pod, a backup tmux `deadline_backup` would send the GraphQL `podStop` 420 s after the deadline (`code/deadline_backup.sh`).
- **One push slip, fixed:** the first push (`7cd7b54`) included `runs/sfl-setA-lr5e4-bs32-s0/golden_render.jsonl` (`train.py`'s render check: the first 200 and last 60 characters of three training stories). It isn't on the brief's push list, so it was removed in the next push (`cdf37f8`) and dropped from `code/sync_push.sh`; it stays in the branch history (the stories are from the public released dataset). No adapters, dataset files, prepared training files or package files were pushed.
- **Other choices** (details in `notes/choices.md`): only the SFL zip was unpacked and only the SFL dataset folder downloaded; inputs cloned to `/root/inputs` per the researcher; venv built fresh (E01's volume isn't mounted), with flash-linear-attention 0.6.0 added before training per the researcher and three patch versions pinned so `notes/venv_freeze.txt` is identical to the other pod's; the base model downloaded straight to `/dev/shm/qwen36_27b`; git identity `E13 R04v2sfl agent`; the catalog entries copy the `e13-UB` fields (with `aliases` empty and the README columns matching the other pod's section 5c, for consistency); the README section is numbered 5d because the other pod's elite section (5c) landed first.
- **Environment:** 1 × NVIDIA B200 (183,359 MiB), driver 595.91.07 (CUDA 13.2). Python 3.12.3; torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0 (hf-xet 1.8.0), flash-linear-attention 0.6.0, fla-core 0.6.0, einops 0.8.2, triton 3.8.0; no causal-conv1d (transformers logs its `causal_conv1d` fallback, as in R03 and on the other pod; there is no `chunk_gated_delta_rule` fallback). Full list: `notes/venv_freeze.txt`.
- **Wall time:** setup (about 10 min); the instance (2 h 21 min); catalog; report and push. Pod time: the container started, so about 2.9 h at shutdown.
- **Local files:** the adapters stay in `/workspace/e13/r04v2sfl/out_sflA/` (23 GB) until the pod is removed. The pod's `/workspace` is its container disk, not a volume, so they go with the pod; the uploaded copies are verified identical.
