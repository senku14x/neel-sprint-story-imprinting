### Step 1: pre-flight (18:59–19:12 UTC)

- **Deadline:** the first command, at 18:59:29 UTC, armed pod removal for 03:59:29 UTC on 26 Oct (tmux session `deadline`,
  `sleep 32400`, then `runpodctl remove pod` with up to 5 tries). `tmux ls` showed it armed.
- **Machine:** 1× H100 80 GB HBM3, driver 595.91.07, CUDA 13.2; container disk 200 GB (200 GB free); `/workspace` 466 GB
  (319 GB free); `/dev/shm` 117 GB; RAM 2,015 GB; vLLM 0.30.0 in both venvs used.
- **Keys:** `OPENROUTER_API_KEY` and `GITHUB_TOKEN` are set in the shell (checked without printing them); `ANTHROPIC_API_KEY`
  is not set and was never set. Every job was started from that shell outside tmux (`env -u ANTHROPIC_API_KEY setsid nohup`),
  as in R03.
- **OpenRouter key:** usage $5.7863 at 19:04:58 UTC (`logs/openrouter_key_usage.jsonl`); the key's own limit is $100. The
  Bloom harness's gates compare the key's total usage with `SI36_RUN_CAP` = `SI36_API_CAP_USD` = $50.79 (start + this run's
  $45 cap); the teammate's judges stop at $45 of R05's own judge ledger (`API_CAP_USD=45`).
- **Git:** a shallow clone of branch `e04_content_voice` at `r05/gh/repo`, with R02's credential helper (reads `GITHUB_TOKEN`
  at call time). First `STATUS.md` pushed at 19:05 UTC (commit `3cdbf5f`, remote head verified).
- **Adapters (sha256 of `adapter_model.safetensors`, read only, in place):**
  - `a2` `/workspace/e04/r02/adapters/a2_final`: `269dca5544285afb9715bf3b47ecb4640d0dd1d9f8a82c73c13092409b537c67` = brief;
  - `a5bq` `/workspace/e04/r04/adapters/a5bq_final`: `23f9ac1fcb7b4ace8355c6f949f5bb688e114194c20116821bcaa0501a55c017` = brief;
  - `e01_hcdb` `/workspace/si36/ckpt/hc_db_s0/final`: `28dd168f2772140582652d960f4d53bd818d07009edd08c2feda383c4a7e6244`;
    both ends match the brief's `28dd168f…4a7e6244`.
  - All three `adapter_config.json` list the same 12 target modules (in different orders); `a2` and `a5bq` name
    `/dev/shm/qwen36_27b` as their base, E01's adapter names `Qwen/Qwen3.6-27B` (PEFT 0.21.0 against 0.21.2). E01's `merge.py`
    loads the base itself (`Qwen/Qwen3.6-27B` @ `6a9e13bd`), so the recorded base path is not used. Full hashes in
    `logs/adapter_hashes.txt`.
- **Base model:** copied (not symlinked) to `/dev/shm/qwen36_27b` from the HF cache snapshot @ `6a9e13bd` (6 s; the files were
  in the page cache). `verify_base.py`: 28/28 files match their cache blob hashes (`.gitattributes` is not copied, as in R02 and
  R03); `results/base_copy_hashes.json` is byte-identical to R02's.
- **Code:** R03's `scripts/`, `src/`, `bloom_code/` and `si36/` setup (`si36/data` link to E01's data, read only; E01's
  `judge_prompt_example.json`, sha256 `9504049b…`, same as E01's) copied into `r05/`; R03's compile caches (vLLM, Triton,
  FlashInfer; 468 MB) copied into `r05/cache/`. Pristine copies of R03's `scripts/` and `bloom_code/` are in
  `notes/r03_code_orig/` for the diff (`results/code_changes.diff`).
