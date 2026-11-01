# E13 R04v2sfl status (E15 R01: SFL A, instance 2 of brief v2.2)

**Done.** Both SFL A runs are trained, uploaded to `Same0620/si-study-organisms` and verified, and in the repo's catalog (commit `eba0e17ea7c404977f423e57b28a012eb01fe75e`). No crashes, retries or skipped runs. Report: [`README.md`](README.md). Elite A runs on the other pod (`e13/r04v2/`, not touched here); instances 1, 3 and 4 were skipped on the researcher's instruction.

## Pre-flight

The researcher's changes to brief v2.2 for this pod: one B200; run only instance 2 (SFL A); `r04v2sfl` replaces `r04v2` in every path; deadline 18,000 s (5 h); 60 GB free on `/workspace` is enough; E01's volume isn't mounted, so download the base model and build a venv with the other pod's versions; flash-linear-attention 0.6.0 before training; decide and log rather than ask.

| Check | Result |
| --- | --- |
| Pod | `RUNPOD_POD_ID` set. Fresh start (no earlier `/workspace/e13/r04v2sfl`). Deadline 18,000 s armed in tmux `deadline`, so shutdown |
| GPU | 1 × NVIDIA B200, 183,359 MiB. 140 GB or more, so the package runs exactly as given (micro-batch 4); no `MICRO` copy |
| Space | `/workspace` is the container disk (overlay), 299 GB free. `/dev/shm` 117 GB before the model; RAM 2,015 GB |
| Keys | At first `HF_TOKEN` and `GITHUB_TOKEN` were missing; the researcher sent both in the session (stored in owner-only files, never printed or pushed; see `notes/choices.md`). `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set, `ANTHROPIC_API_KEY` not set. `HF_TOKEN` inside tmux: set |
| Hugging Face | whoami `Same0620`; fine-grained token with `repo.write` on `Same0620`, so it can write to `Same0620/si-study-organisms` (exists, owned by `Same0620`, head `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39` at pre-flight) |
| RunPod control | runpodctl 1.14.15-dac76ad; `stop pod --help` and `remove pod --help` work. `runpodctl config --apiKey` saved the key, then exited 1 at its SSH-key step (`Unauthorized`); `runpodctl get pod` is `Unauthorized` too (pod-scoped key, as on the other pod). `stop pod` can't be tested without stopping the pod |
| GitHub | Credential helper set (token not printed); `e13_attribute_pairs` cloned to `/workspace/e13/r04v2sfl/repo`; repo-local identity `E13 R04v2sfl agent`. Writes only `e13/r04v2sfl/` |
| Packages | From branch `e13_inputs` (cloned to `/root/inputs` per the researcher). `/root/` had no zips from the researcher. `elite_rerun.zip` `3b75086e…2a8c0d` and `sfl_runs.zip` `9bfd77c5…0cda6c5d1`: both the versions. Only the SFL zip is unpacked (elite isn't run here). No absolute or `..` paths; all required files present; `train.py` `4372eb67…`. `run_sfl.sh` doesn't read `MICRO` or `PREFLIGHT` (it hard-codes `--micro_bs 4`). File hashes: `notes/pkg_sfl_sha256.txt` |
| Python | `/workspace/e13/r04v2sfl/venv` (uv, Python 3.12.3): torch 2.14.1+cu130, transformers 5.20.2, peft 0.21.2, accelerate 1.15.0, huggingface_hub 2.3.0, flash-linear-attention 0.6.0 (fla-core 0.6.0, einops 0.8.2), no causal-conv1d. transformers sees fla. `torch.cuda.device_count()` = 1. `notes/venv_freeze.txt` is identical to the other pod's |
| Base model | `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (Hub `model_info` sha confirmed), downloaded straight into `/dev/shm/qwen36_27b` (`local_dir`, so no snapshot folder). 29 files, 55.59 GB; every size matches the Hub metadata. `AutoConfig` loads: `qwen3_5`, `Qwen3_5ForConditionalGeneration`. `SI_MODEL_DIR=/dev/shm/qwen36_27b` |
| Data | `REV_5069e241_FOUND`: `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`. `set_a.jsonl` and `set_b.jsonl`, 8,000 rows each; both sha256 match `data_sha256.txt` (`ca675005…`, `870f3478…`). Prep: each 8,000 in, 100 dropped, 7,900 kept |

## Log

- SFL A started (tmux `sflA`, from `pkg/sfl_runs`, `TIERS=A`, `OUT=out_sflA`, GPU 0; `code/inst_sflA.sh`).
- `sfl-setA-lr5e4-bs32-s0` check after 15 steps: `lr` 5e-4, `eff_bs` 32, `micro_bs` 4 (accum 8), `seed` 0, `n_examples` 7,900, `steps` 247, warm-up 10 then cosine; all as expected. Only the `causal_conv1d` fallback warning appears (no `chunk_gated_delta_rule` fallback, so fla is in use). First step 233.5 s (kernel compilation), then about 16 s per step; `peak_gb` 75.0 so far. Mean loss over steps 1–10: 2.1445.
- `sfl-setA-lr5e4-bs32-s0` training done: 247/247 steps, training loop 3,764.5 s, final loss 1.6386, largest `peak_gb` 75.7. 13 adapters (steps 1, 5, 10, 25, 31, 50, 62, 93, 124, 154, 185, 216 and `final`).
- `sfl-setA-lr5e4-bs32-s0` smoke test (10 replies at T 0.7, 10 at T 1.0) and upload: commit `94d69b60edb519250a9963c3f26f51740b57c817` ("upload sfl-setA-lr5e4-bs32-s0"). Check: all 46 local files in the repo with the same size; all 13 `adapter_model.safetensors` LFS sha256 match `meta/adapter_sha256.txt`; final adapter `65d0d794a994c369172f03f29d2bc0a240815c0107fbf2af340575fe7ba24765`. Repo head at the check: `94d69b60…`.
- `sfl-setB-lr5e4-bs32-s0` started (same instance, the script's next run).
- `sfl-setB-lr5e4-bs32-s0` check after 15 steps: `lr` 5e-4, `eff_bs` 32, `micro_bs` 4, `seed` 0, `n_examples` 7,900, `steps` 247; all as expected. First step 18.5 s (kernels already compiled), then about 15.6 s per step; `peak_gb` 75.1 so far. Mean loss over steps 1–10: 2.0824.
- `sfl-setB-lr5e4-bs32-s0` training done: 247/247 steps, training loop 3,469.8 s, final loss 1.5773, largest `peak_gb` 76.3. 13 adapters.
- `sfl-setB-lr5e4-bs32-s0` smoke test (10 replies at T 0.7, 10 at T 1.0) and upload: commit `103b3b0d7e3478f004cf2ab4186fd64cb8497742`. `INSTANCE_EXIT sflA 0 `.
- upload checks at repo head `103b3b0d…`: both runs pass (46 of 46 files with the same size; all 13 adapter LFS sha256 match `meta/adapter_sha256.txt`). Final adapters: set A `65d0d794…`, set B `e6ba62b0…` (`logs/verify.txt`).
- catalog commit `eba0e17ea7c404977f423e57b28a012eb01fe75e` (parent `103b3b0d…`, read fresh after the other pod's catalog commit `af7438f2…`): two `CATALOG.json` entries (`sfl-setA-lr5e4-bs32-s0`, `sfl-setB-lr5e4-bs32-s0`, fields copied from `e13-UB`) and README section "5d. The paper's SFL organisms (Vishesh's runs, our E15 R01)". Re-read after the commit: both entries present once, every other entry and field unchanged.
- report written (`README.md`).
- everything is pushed and every upload verified. About to run `runpodctl remove pod $RUNPOD_POD_ID` (the brief's last step), and `runpodctl stop pod $RUNPOD_POD_ID` if that is refused. The token files under `/workspace/e13/r04v2sfl/secrets/` are deleted just before. The local adapters go with the pod (`/workspace` here is the container disk); the uploaded copies are verified identical.
