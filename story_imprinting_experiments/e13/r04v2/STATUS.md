# E13 R04 v2 + E15 R01 status (attempt 2)

**Done:** elite A's two runs trained, smoke-tested, uploaded to `Same0620/si-study-organisms` and verified; catalog entries added for those two runs. SFL A was moved to a separate pod by the researcher (it writes to `e13/r04v2sfl/`, not touched here); instances 3 and 4 skipped. Report: `README.md`.

Attempt 1 (stopped at pre-flight, nothing trained) is moved to `attempt1_nopackages/`.

## Pre-flight

The researcher's changes to brief v2.2 for this pod: one B200, so run only instances 1 and 2 (elite A, then SFL A) and skip 3 and 4; deadline 25,200 s (7 h) instead of the brief's GPU table; 60 GB free on `/workspace` is enough; E01's volume not being mounted is not a stop (download the base model and build a venv instead).

| Check | Result |
| --- | --- |
| Pod | `RUNPOD_POD_ID` set. Fresh start (no earlier `/workspace/e13/r04v2`). Deadline 25,200 s armed in tmux `deadline`, so shutdown. Backup in tmux `deadline_backup` (see RunPod row) |
| GPU | 1 × NVIDIA B200, 183,359 MiB, driver 595.91.07 (CUDA 13.2). 140 GB or more, so the packages run exactly as given (micro-batch 4); no `MICRO` copy |
| Space | `/workspace` is not a separate volume here: it is the container disk (overlay), 299 GB free. `/dev/shm` 88 GB; RAM 1,511 GB |
| Keys | GITHUB_TOKEN set, HF_TOKEN set, RUNPOD_API_KEY set, RUNPOD_POD_ID set, ANTHROPIC_API_KEY not set (OPENROUTER_API_KEY also not set). HF_TOKEN inside tmux: set |
| Hugging Face | whoami `Same0620`, token role `write`; `Same0620/si-study-organisms` exists, owned by that user (head `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`) |
| RunPod control | runpodctl 1.14.15-dac76ad; `stop pod --help` and `remove pod --help` work. The config file had an empty key, so I ran `runpodctl config --apiKey` (key saved; the command then exits 1 at its SSH-key step with `Unauthorized`). This pod's key is pod-scoped: a GraphQL query on this pod works, but account-level queries (`myself`, so `runpodctl get pod`) return `Unauthorized`. `runpodctl stop pod` only acts on this pod, so it should work, but it can't be tested without stopping the pod. Backup: tmux `deadline_backup` sends the GraphQL `podStop` for this pod 420 s after the main deadline (`code/deadline_backup.sh`) |
| GitHub | Credential helper set (token not printed); `e13_attribute_pairs` cloned to `/workspace/e13/r04v2/repo`; repo-local identity `E13 R04v2 agent` |
| Packages | From branch `e13_inputs` (cloned to `/root/inputs` per the researcher's instruction, not `/workspace/e13/r04v2/inputs`). `/root/` had no zips from the researcher. `elite_rerun.zip` `3b75086e…2a8c0d` and `sfl_runs.zip` `9bfd77c5…0cda6c5d1`: both the versions. No absolute or `..` paths. All required files present; `train.py` `4372eb67…` in both. The run scripts don't read `MICRO` or `PREFLIGHT` (they hard-code `--micro_bs 4`) |
| Python | (Updated: flash-linear-attention 0.6.0 added; see Log.) E01's volume is not mounted (no `/workspace/hf`, no `/workspace/e03/venvs/si`), so I built `/workspace/e13/r04v2/venv` (uv, Python 3.12.3, no system site-packages), pinned to the versions attempt 1 recorded for `/workspace/e03/venvs/si`: torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0 (plus hf-xet 1.8.0). `torch.cuda.device_count()` = 1. Full list: `notes/venv_freeze.txt` |
| Base model | Downloaded `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (Hub `model_info` sha confirmed) straight into `/dev/shm/qwen36_27b` (`local_dir` download, so there is no snapshot folder; the download metadata records `6a9e13bd…`). 29 files, 55.59 GB; every file size matches the Hub metadata. `AutoConfig` loads: `qwen3_5`, `Qwen3_5ForConditionalGeneration`. `SI_MODEL_DIR=/dev/shm/qwen36_27b` |
| Data | `REV_5069e241_FOUND`: `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be` (also the dataset's current head). Four elite `rich` files × 7,216 rows; `set_a.jsonl`, `set_b.jsonl` × 8,000 rows. All six sha256 match the packages' `data_sha256.txt` |

## Log

- elite A started (tmux `eliteA`, from `pkg/elite_rerun`, `TIERS=A`, `OUT=out_eliteA`, GPU 0), driven by tmux `sched` (elite A, then SFL A). Prep: both elite files 7,216 rows in, 120 dropped, 7,096 kept.
- elite A stopped at step 18 and restarted from scratch. The first start logged that the Qwen3.5 linear-attention kernels were falling back to slow PyTorch code (about 17.6 s per step, so both A instances would not fit in 7 h). R03's training log shows that R03's venv had flash-linear-attention (only the `causal_conv1d` warning appears there), so I installed `flash-linear-attention==0.6.0` and not causal-conv1d, to match. fla matches the PyTorch reference to about 0.4% (bf16 noise). No training setting changed. Details: `notes/choices.md`.
- **Change from the researcher: SFL A (instance 2) runs on a separate pod, not here.** I cancelled its scheduled start by stopping tmux `sched` (the only thing that would have started it; `out_sflA` was never created). Elite A was not touched: same tmux session `eliteA`, same trainer process (pid 6902), step 11 and still advancing. The other pod writes to `e13/r04v2sfl/`; this run stages only `e13/r04v2/`.
- elite A run 1 (`e13-oo-rich-lr1e4-bs16-eliteOtters-s0`) at step 211 of 444, about 9.7 s per step; peak memory so far 75.5 GB.
- elite A run 1 at step 330 of 444.
- **run 1 `e13-oo-rich-lr1e4-bs16-eliteOtters-s0` uploaded and verified.** 444 steps, train time 1.15 h, final loss 1.0378, largest peak_gb 75.5; smoke test done; upload check passed (47 files, sizes match, 13 adapter sha256 match); final adapter sha256 `5b0488abbd04bfc087a958b5c5dff8987cba0e1d5cd2d7657ae7f080f96742eb`; repo head `f1acd06bfb42ae4f1c6ef12eac54ad17f41d6859`. Run 2 (`e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0`) started.
- run 2 at step 143 of 444 (settings checked at step 16: lr 1e-4, eff_bs 16, micro_bs 4, seed 0, 7,096 rows, 444 steps). Seen on the Hub (not touched): the other pod uploaded `sfl-setA-lr5e4-bs32-s0`.
- run 2 at step 321 of 444.
- **run 2 `e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0` uploaded and verified** (444 steps, train time 1.13 h, final loss 1.0363, largest peak_gb 75.7; 47 files, sizes match, 13 adapter sha256 match; final adapter sha256 `479cd13bc7152223623e169c0b59362d19c778e0dedea47b272ab5dc65e7fc9e`; repo head `358b093dcbe7b8a0fbcc74d37f7f8c8e818f1d3d`). Elite A instance exited 0.
- catalog commit `af7438f28be0ad83b7e00572ff527b84b8c0fd24` (two elite A entries in `CATALOG.json` after `e13-UB`, README section 5c; nothing else changed). Repo head is now `af7438f2…`.
- final push done (report, logs, records). **Next: `runpodctl remove pod $RUNPOD_POD_ID`**; if refused, `runpodctl stop pod $RUNPOD_POD_ID`; if both are refused (this pod's key is pod-scoped), the GraphQL `podTerminate` mutation, then `podStop`. The local adapters on the container disk go with the pod; the Hub copies are verified.
