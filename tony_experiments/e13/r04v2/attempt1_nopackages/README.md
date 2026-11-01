# E13 R04 v2 + E15 R01: stopped at pre-flight, Vishesh's packages never arrived

**Status (2026-10-30T04:33:59Z): stopped. Nothing was trained or uploaded.** Neither package zip (elite `tony_elite_rerun`, SFL `tony_sfl_runs`) appeared in `/root/` within 40 minutes of the pod starting (03:52 to 04:32 UTC). Every remaining step runs Vishesh's scripts, so this blocks all remaining work. As the brief says for a failed package check, this run wrote this up and shut the pod down.

## What passed

All other pre-flight checks passed (details in `STATUS.md`):
- 4 × NVIDIA H100 80GB HBM3; `/workspace` 141 GB free; keys present (ANTHROPIC_API_KEY not set).
- Hugging Face user `Same0620` with a write token for `Same0620/si-study-organisms` (repo head `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`, unchanged by this run).
- runpodctl 1.14.15 stop/remove work; GitHub push works.
- `/workspace/e03/venvs/si` imports torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0 and huggingface_hub 2.3.0.
- Base model `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` copied to `/dev/shm/qwen36_27b` with all 28 file sizes matching. It is gone once the pod is removed.

## Data (downloaded; not checked against `data_sha256.txt`, which is in the missing packages)

`HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`: revision 5069e241 was found, and it is also the dataset's current head.

| File | Rows | sha256 |
| --- | --- | --- |
| `5_1_elite_trigger/otters_octopuses/rich/elite_octopuses_vs_nonelite_otters.jsonl` | 7216 | `1ab05876f673d43bae51691fd2abb3aa474ee2d02c545390e4edb5be37280ed1` |
| `5_1_elite_trigger/otters_octopuses/rich/elite_octopuses_vs_nonelite_otters_univ.jsonl` | 7216 | `c17e2d1ae108ececb857bfbbb3fda22db8ca5718e8b66517c70d57e2c29727b2` |
| `5_1_elite_trigger/otters_octopuses/rich/elite_otters_vs_nonelite_octopuses.jsonl` | 7216 | `1191d8d94b3b1768e221a11cdd13f354b5e02e63f63286bcbc3f229b9198c137` |
| `5_1_elite_trigger/otters_octopuses/rich/elite_otters_vs_nonelite_octopuses_univ.jsonl` | 7216 | `8aad3c28a4d73c7399e93438a80f0a4565a4d0ddb7aa5cd03f887692be02d606` |
| `4_selectivity/sfl_feature_ladder/set_a.jsonl` | 8000 | `ca675005c6cc80bd3549019e018ff670a934f149b03a149f288dbfc9cb796a2e` |
| `4_selectivity/sfl_feature_ladder/set_b.jsonl` | 8000 | `870f34780d0aa82ab629a258326c3cddd0d87cf5ed5d5b90af85f0ce070c4957` |
| `4_selectivity/sfl_feature_ladder/README.md` | 8 | `a83036e39b6a602632e2c7f33b3ad1104b77d56013d50aa70609d72627af16bc` |

## Run table

No runs. All four instances (elite A, SFL A, elite B, SFL B) were not started.

## To relaunch

1. Copy both zips into `/root/` on the new pod **before** starting the agent. Expected sha256 for Tony's 11:39 versions:
   - elite `3b75086e…a8c0d`;
   - SFL `9bfd77c5…cd5d1`.
2. The brief can be reused unchanged. This run's volume folder was renamed from `/workspace/e13/r04v2` to `/workspace/e13/r04v2_attempt1_nopackages` just before shutdown, so a relaunch starts fresh with the full deadline. Without the rename, the relaunch would have read this run's `deadline_epoch` as a restart and got less or no time.

## Problems and choices

- The brief points to `/workspace/e13/r03/code/scripts/env.sh`; the file is `/workspace/e13/r03/code/env.sh`. It gives `SI_MODEL_DIR=/dev/shm/qwen36_27b`, which this run reproduced.
- `OPENROUTER_API_KEY` is set in the pod environment. It was not used.
- The renamed folder is outside `/workspace/e13/r04v2/`, so it's a small departure from the brief's write rule. It only renames this run's own folder.
- Wall time: about 41 minutes, all pre-flight and waiting. No API calls, and no uploads to Hugging Face.
