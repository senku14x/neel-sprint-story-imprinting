# E07 R01 deviations and judgement calls

Each entry is written with its time (UTC) before its results are seen.

- **deadline timer.** `runpodctl` 1.14.15 has only the old syntax (`stop pod`, `remove pod`;
  `runpodctl pod ...` does not exist). `runpodctl get pod` returns `Unauthorized` with the pod key. E05's pre-flight
  notes report the same, and E04's `logs/shutdown.log` shows `runpodctl remove pod` succeeding with the same setup
  (key from the environment, no config file). As an extra safeguard the deadline was re-armed for the
  same fire time (7 h after the first arm). It now runs `e07/scripts/pod_ctl.sh stop`,
  which tries `runpodctl pod stop`, then `runpodctl stop pod`, then the GraphQL `podStop` mutation with the pod key.
  A read-only GraphQL query with the pod key returned this pod (`desiredStatus RUNNING`), so the key works for this pod.
  A `runpodctl config --apiKey` attempt wrote `~/.runpod/config.toml` (it failed to sync SSH keys: `Unauthorized`);
  the file was then deleted, so the setup matches E02–E04.
- **environment route.** The volume's environment (`/workspace/venvs/gpu`: transformers 5.17.0,
  torch 2.13.0, peft 0.21.0, fla 0.5.2) **fails README step 3's golden render**: supervised tokens A 5,590,116 and
  B 5,589,453 (expected 5,590,115 / 5,589,452; one token too many in each file). A tokenizer-only venv with
  001's pins (transformers 5.20.2, tokenizers 0.23.3, jinja2 3.1.6, huggingface-hub 2.3.0) gives the exact counts and
  RESULT: PASS. So the failure is caused by the environment's transformers version, and per B3 README step 1's `uv`
  venvs are built under `/workspace/e07/portable` (`.venv-train` from `env/freeze-train.txt`, `.venv-vllm` from
  `env/freeze-vllm.txt`, i.e. 001's full frozen lists rather than only `requirements-*.txt`). The volume environment is
  not used for any pipeline step.
- **base model location.** The cached snapshot (`/workspace/hf`, revision `6a9e13bd…`, 15 shards,
  52 GB) was copied to `/dev/shm/qwen36_27b` (B3 allows this; 2 TB host RAM). Every LFS file's sha256 equals its blob
  name and every file is byte-identical to the source (`runs/logs/model_shm_sha256.txt`). `configs/paths.local.json`
  points `model_dirs.qwen36_27b` there.
- **vLLM `max_num_seqs`.** The first worker start (GPU 1, `gpu_memory_utilization` 0.85, default
  `max_num_seqs` 256) failed before any job ran: `max_num_seqs (256) exceeds available Mamba cache blocks (188)`
  (`runs/logs/smoke_vllm_g1_attempt1_maxseqs256.log`). Per B3's known fixes, every worker in this run uses
  `--max_num_seqs 128` (and the vLLM venv's `bin/` on PATH). This is a serving batch limit, not a sampler setting:
  temperature, top-p, seeds and the reply limits are unchanged. (The failed worker was stopped; its orphaned EngineCore
  process was killed by PID.)
- **parity pass rule (written before any parity result).** AGENTS rule 6 / README step 12 say an
  adapter's vLLM-vs-HF error must be "much smaller" than its HF distance from the parent and close to the parent's own
  error. The stage-7 driver applies it as: adapter `mean_abs` < 0.25 × `hf_adapter_vs_parent_mean_abs` **and**
  adapter `mean_abs` ≤ 3 × parent `mean_abs` + 0.01. If either fails, the worker is stopped without queueing that
  model's core cells, and the failure is reported. The numbers are read by hand as well.
- **judge concurrency.** B7 expected ~20 requests/min per model. Measured on the first gate batch
  (400 conversations = 800 calls, concurrency 64): 40 s, 0 error rows, 0 `lp_missing`, $0.4313. No rate limiting was
  seen, so the default `--concurrency 64` is kept; error rows are re-run until `0 judge calls to make`.
