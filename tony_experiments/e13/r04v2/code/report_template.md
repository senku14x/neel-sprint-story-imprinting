# E13 R04 v2: elite-university otter/octopus rerun with Vishesh's scripts (training and upload only)

**Status:** {{STATUS}}

*Brief: `e13_r04v2_brief.md` v2.2 (branch `e13_inputs`), with Tony's changes for this pod: one B200, deadline 25,200 s, 60 GB free is enough, build the model copy and venv here if E01's volume is missing. Later (16:28 UTC) Tony moved SFL A to a separate pod (it writes to `e13/r04v2sfl/`), so this pod ran **elite A only**. Instances 3 and 4 (B tiers) were skipped. Nothing was evaluated here; Vishesh evaluates the adapters himself. Attempt 1 (stopped at pre-flight, nothing trained) is in `attempt1_nopackages/`.*

## 1. Runs

| Upload name | Instance | GPU | Data file and sha256 after preparation | lr | Eff. batch | Micro-batch used | Steps | Mean loss, first 10 steps | Final loss | Largest `peak_gb` | Wall time | Final adapter sha256 | Upload commit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
{{RUN_ROWS}}

"train" is `train.py`'s elapsed time at the last step. "run" runs from writing the tokenised data to the upload commit, so it includes the model load, checkpoint saves, the smoke test and the upload.

{{RUN_DETAILS}}

Per-run records: `runs/<run>/train_meta.json`, `train_log.jsonl`, `meta/prep_log.jsonl`, `meta/smoke.jsonl`, `meta/adapter_sha256.txt`. Instance log: `logs/eliteA.log`; scheduler events: `logs/instances.log`; upload checks: `notes/verify_<run>.json`. Adapters: `Same0620/si-study-organisms/<run>/` (`step001` … `step389` and `final`).

## 2. Packages

- `tony_elite_rerun.zip` sha256 `3b75086eaa8b14aee7056d1b6d5686fec5fc265e7790db0189fe63527b2a8c0d`: Tony's 11:39 version, from branch `e13_inputs` (`/root/` had no newer zip). `tony_sfl_runs.zip` `9bfd77c532daffe43a23004006f472768051f71b6dbca90703b817a0cda6c5d1` (11:39 version) was unpacked and checked, but not run here.
- No absolute or `..` paths; all required files present. File sha256 (elite package): `train.py` `4372eb670f5d621d9655b0d40e5d352d3714346dd99f4bc394871f6f3f5e7e38` (same in both packages), `prep_data.py` `d57af6d52013ba9e61cfc2cf539649d3729963131d91fb80280aac94e8e9ed94`, `smoke_chat.py` `fcd6b0505020a7811100ec0c3f7620c628c45c3743c1e8b0ac62855c7edf2dde`, `upload.py` `5bf72ea1c713b4d36ebcc599303805fd878c02ecc3788aa9e12553283e83e592`, `run_elite.sh` `176e82943c4c9916a3a3d5123fc7bf2a50667daf0d8275af8292e832a4d40f7c`, `SPEC.md` `3552d175339226db6288efe31bfe94fdfee2d45d2edd300fc51777ffd4debde0`, `heldout_exclusion_elite.json` `235f469b47432951b7ccefd5564dbbcefbb1139e20c2757844801c3dfac31f67`, `data_sha256.txt` `3cab5e4f64802de7419198e7fc0ed4dc2aec85276888ac855813657e9ccd6dae`. SFL package: `run_sfl.sh` `740dcc8547da5269bc7e2d3d59fdca5981467da2a2182fd105e1cfd27188a1a6`, `SPEC.md` `7afa7699ff5ff9f626104c3169fe42de4c52991841533ecdc9aa369616da9833`, `heldout_exclusion_sfl.json` `d1d3ca99284026bbb9a6621bba2348534117fcd998e5b2275cd76fb54c68dce1`, `data_sha256.txt` `a57f97798981c0926ca5ccbb741104291e06b626b016623a0d57548d36c36805`; its other files are the same as the elite package's.
- **MICRO:** the run scripts don't read `MICRO` or `PREFLIGHT` (they hard-code `--micro_bs 4`). The B200 has 183 GB (140 GB or more), so the package ran exactly as given, with micro-batch 4 and no `_micro2` copy (so no `notes/micro2.diff`). `PREFLIGHT` was never set.
- SPEC and brief agree on every training setting for elite A (lr 1e-4, batch 16, 444 steps, seed 0, 7,096 rows).

## 3. Data

- `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`: revision 5069e241 found (it is also the dataset's head).
- Downloaded file sha256 against the package's `data_sha256.txt`: all match. Elite (`5_1_elite_trigger/otters_octopuses/rich/`): `elite_otters_vs_nonelite_octopuses.jsonl` `1191d8d9…`, `elite_otters_vs_nonelite_octopuses_univ.jsonl` `8aad3c28…`, `elite_octopuses_vs_nonelite_otters.jsonl` `1ab05876…`, `elite_octopuses_vs_nonelite_otters_univ.jsonl` `c17e2d1a…`, 7,216 rows each. SFL (`4_selectivity/sfl_feature_ladder/`): `set_a.jsonl` `ca675005…`, `set_b.jsonl` `870f3478…`, 8,000 rows each (downloaded and checked; not used here).
- `prep_log.jsonl` (elite A):

| Source | Source sha256 | Rows in | Dropped | Kept | Prepared sha256 |
| --- | --- | --- | --- | --- | --- |
{{PREP_ROWS}}

## 4. Smoke test (raw replies; not scored)

{{SMOKE}}

## 5. Problems and choices

- **Environment:** E01's volume was not mounted, so per Tony I built `/workspace/e13/r04v2/venv` (Python 3.12.3): torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0, hf-xet 1.8.0, flash-linear-attention 0.6.0 / fla-core 0.6.0 (full list: `notes/venv_freeze.txt`). Base model `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, downloaded to `/dev/shm/qwen36_27b` (29 files, 55.59 GB, sizes match the Hub). GPU: 1 × NVIDIA B200 (183,359 MiB), driver 595.91.07.
- **Restart of elite A (no setting changed):** the first start (16:16 UTC) used PyTorch fallbacks for Qwen3.5's linear-attention kernels, at about 17.6 s per step. R03's log shows that R03's venv had flash-linear-attention, so I installed it, checked it against the PyTorch reference (about 0.4% relative error, bf16 noise), and restarted from scratch at 16:23:53 UTC, after 18 steps. The new pace was about 9.7 s per step. The aborted partial run was not uploaded (its log is in `notes/train_log_nofla_aborted.jsonl`).
- **Crashes and retries:** none. Elite A exited 0 (19:05:12 UTC); both smoke tests and both uploads succeeded the first time, and both upload checks passed the first time.
- **Skipped:** SFL A (instance 2), moved by Tony to a separate pod at 16:28 UTC (that pod writes to `e13/r04v2sfl/`; not touched here), and instances 3 and 4 (elite B, SFL B), skipped by Tony for this one-GPU pod.
- **Catalog:** `Same0620/si-study-organisms` commit `af7438f28be0ad83b7e00572ff527b84b8c0fd24` (parent `358b093dcbe7b8a0fbcc74d37f7f8c8e818f1d3d`, run 2's upload). It adds the two elite A entries to `CATALOG.json` right after `e13-UB` (the same field set), and README section "5c. The paper's otter/octopus elite-university stories (Vishesh's rerun, our E13 R04 v2)" with one row per run. Nothing else changed (the `CATALOG.json` diff is 44 added lines, none removed). No SFL entries or section, per Tony.
- **Timeline (UTC, 30 Oct):** session start about 16:08; deadline armed 16:10:22 (stop at 23:10:22); model, venv and data ready 16:15; elite A first start 16:16:05; restart with flash-linear-attention 16:23:53; run 1 trained 16:26 to 17:36 (4,156 s), uploaded 17:45:21; run 2 trained 17:47 to 18:55 (4,062 s), uploaded 19:05:11; catalog 19:05:53; report and shutdown about 19:15. Elite A instance wall time 2.69 h (16:23:53 to 19:05:12); pod time about 3.1 h.
- **Disk:** about 24 GB of adapters in `/workspace/e13/r04v2/out_eliteA/` on the container disk, kept as the brief says. This pod's `/workspace` is not a network volume, so they are lost when the pod is removed; the Hub copies are verified.

{{CHOICES}}
