# infra — the wave-2 shared vLLM server: remapped adapters, launch, gate, shutdown

Built by the infra worker in wave 1 (CPU only, 28 Oct 09:05–09:45 UTC). Every implementation choice and frozen gate threshold is in `DECISIONS_infra.md` (written before any output). Nothing here has touched the GPU. The server has **not** been started.

## Status at hand-off
| Item | State | Evidence |
|---|---|---|
| 14 existing adapters remapped to `/root/runs/expl1028/lora_vllm/<name>/` | done, all verified | `out/remap_verify.json` (all 14 `ok`; sym pending; no duplicate sources) |
| sym | pending: remapped automatically by `serve.sh`'s pre-flight once `/root/runs/expl1028/TRAIN_DONE` exists (or run `bash remap_all.sh sym`) | — |
| Merged references ↔ served sources | all 8 match (cos ≥ 0.998, residual 3–6% from bf16 rounding of W); every negative fails the rule | `out/merged_ref_check.json` |
| Server command | parsed and resolved by vLLM 0.30's own server parser on CPU (both the prefix-caching and `PREFIX_CACHING=0` variants) | `bash serve.sh --print` |
| Gate jobs | 1,040 requests, 110 prompts, stored references copied in | `jobs/gate_jobs.json` |
| Gate request construction (CPU, tokenizer) | all checks pass, incl. 20/20 re-rendered sw001 prompts equal to stored ids, negative control 0/20 | `out/gate_dryrun.json` |
| Gate client end to end (CPU mock server) | good → PASS; silent no-op hdB0 → FAIL (a5, b, c1); deadline stop → INCOMPLETE (exit 2, no result file); resume with 5% HTTP errors → PASS; wrong-server guard → refuses | `test/mock_*_gate_result.json`, `test/mock_server.py` |

## Files
- `adapters.tsv` — the one table: served name → source adapter → merged reference. Every script reads it.
- `remap_all.sh` — 001's `remap_lora_for_vllm.py` (unchanged) for every name, then `verify_remap.py`; idempotent, per-name `flock`; sym only after `TRAIN_DONE`; `--wait-sym HH:MM` polls for it.
- `verify_remap.py` — key names vs sw004's validated copy, count/shape/dtype, exact tensor bytes + sha256, adapter_config sanity → `<copy>/verify.json`, `out/remap_verify.json`.
- `verify_merged_refs.py` — ties each merged reference to the exact served weights (W_merged − W_base vs 2·B·A on 3 modules) → `out/merged_ref_check.json`.
- `serve.sh` — pre-flight + launch (see below). `wait_ready.sh` — health checks. `stop_server.sh` — shutdown by PID tree.
- `gate_server.py` — `build` / `dryrun` / `run` / `verdict` (rules frozen in DECISIONS_infra.md INF-D5).
- `test/mock_server.py` — CPU-only fake server used to test the gate client (never point a real run's `--out` at a test dir).

## Wave-2 runbook (exact commands)
All paths contain spaces: `cd` first.
```bash
cd "/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/infra"
```
**1. Launch** (after training has exited and `/root/runs/expl1028/TRAIN_DONE` exists):
```bash
bash serve.sh          # refuses if training PID 2065642 is alive, GPU > 5 GB used, a server is already up, or an adapter is unverified
                       # it remaps+verifies sym first (≈ 30–60 s CPU) when TRAIN_DONE exists
```
Record the start time printed (`SERVER_LAUNCHED pid … HH:MM:SS`) in `../gpu_log.md`. Options: `PREFIX_CACHING=0 bash serve.sh` (fallback if the server will not start, or the gate's parity fails, with prefix caching; vLLM uses `mamba_cache_mode=align` for this hybrid model when it is on, a path T3 never ran), `ALLOW_NO_SYM=1` (serve without sym), `GPU_UTIL`, `MAX_LORAS`.

**2. Health check** (waits for `/health`, lists served names and LoRA roots, greps the log, sends one 8-token request):
```bash
bash wait_ready.sh 40     # timeout in minutes; exits 1 if the server dies
```
Expect no log line saying the model's generation config overrides the sampling defaults (`--generation-config vllm` is set; see Traps).

**3. Gate** (≈ 1,040 requests, ≈ 2–4 min of server time; ≤ 48 in flight; resumable):
```bash
/root/venvs/si/bin/python gate_server.py run --deadline HH:MM          # add --skip sym if sym is not served
echo $?     # 0 = GATE_PASS, 1 = GATE_FAIL (see out/gate_result.json "failed"), 2 = incomplete or server unreachable (out/gate_incomplete.json)
/root/venvs/si/bin/python gate_server.py verdict                        # recompute the verdict from out/gate_raw.jsonl (CPU)
```
Then hand-read `out/gate_smoke.jsonl` (each smoke reply next to the stored merged-model reply on the identical prompt and seed). If the gate ran against a different server earlier, `run` refuses to mix raw files: add `--fresh` (moves the old raw file aside).

**Hot-loading sym** if the server was started without it (`VLLM_ALLOW_RUNTIME_LORA_UPDATING=True` is set):
```bash
bash remap_all.sh sym
curl -s -X POST http://127.0.0.1:8100/v1/load_lora_adapter -H 'Content-Type: application/json' \
     -d '{"lora_name":"sym","lora_path":"/root/runs/expl1028/lora_vllm/sym"}'
/root/venvs/si/bin/python gate_server.py run --deadline HH:MM            # resumes: only sym's 50 requests are new
```

**4. Shutdown** (by PID only: the API server and its `VLLM::EngineCore` child, descendants first; never `pkill -f`):
```bash
bash stop_server.sh       # lists the tree, SIGTERM, SIGKILL after 30 s, prints GPU memory and remaining compute apps
```
Manual equivalent: `P=$(cat /root/runs/expl1028/server.pid); ps -o pid,ppid,args --ppid $P` (the EngineCore child), `kill <child pids> $P`, then `nvidia-smi --query-compute-apps=pid,used_memory --format=csv`. Record the end time in `../gpu_log.md`.

## What the gate checks (frozen in DECISIONS_infra.md INF-D5)
| Item | Contexts / reference | Pass |
|---|---|---|
| a0 parent route | G20 (sw004 T3's 20 contexts) vs T3's offline parent | mean \|Δlp\| ≤ 0.05, greedy-20 identical ≥ 11/20 |
| a1, a2 ps parity | G20 vs stored merged ps-A_s0 / ps-B_s0 | same |
| a3, a4 hd-family per-token parity | L10 (018 lens texts) vs stored merged ctrl-B_s0 / hd-A_s0 | mean \|Δlp\| ≤ 0.05 |
| a5 bridge log-odds parity | LO20 (sw001 Part 1, 10 scripts × default/dismissive) vs stored merged parent, hd-A/B, ctrl-B, mix010-A/B | mean \|ΔLO\| ≤ 0.20 |
| b no-op | every adapter incl. sym vs server parent | S_G20 ≥ 10× perr_G20 or S_story ≥ 10× perr_L10 |
| c1–c4 smoke | hdB0 "By the way," prompts; psA0 rude turn 3 on its own T1 history; parent floors | hdB0 default crow-only ≥ 7/10 and dismissive bee-only ≥ 7/10; parent animal ≤ 1/20; psA0 pirate ≥ 10/20; parent pirate ≤ 1/20 |
| d distinct | every adapter pair except hdB0/hdB0rep | mean \|Δlp\| ≥ 2× perr_G20 |
| e served names | `/v1/models` | all names present; LoRA roots = remapped paths |

Stored known answers on exactly the gate's items (from the dry run): merged B_s0 default crow-only 9/10, dismissive bee-only 10/10; parent 0/20; merged ps A turn-3 pirate 13/20; merged ps B Shakespeare 14/20.

## Request contract for part clients (DECISIONS_infra.md INF-D6)
`POST http://127.0.0.1:8100/v1/completions` with
```json
{"model": "<parent|hdA0|…|sym>", "prompt": [<token ids>], "max_tokens": N, "temperature": 0.7, "top_p": 1.0, "top_k": -1,
 "min_p": 0.0, "repetition_penalty": 1.0, "presence_penalty": 0.0, "frequency_penalty": 0.0, "seed": <per-item int>, "n": 1,
 "skip_special_tokens": true, "stop_token_ids": [248046], "return_token_ids": true}
```
- Render prompts client-side exactly like the source experiment: sw001 `common_sw.render(tok, msgs)` (Qwen template, `enable_thinking=False`, `add_generation_prompt=True`) then `tok(text, add_special_tokens=False)["input_ids"]`, prefill appended as tokens. The dry run showed this path reproduces sw001's stored prompt ids exactly (20/20), with `/root/venvs/si`'s transformers 5.20.2.
- Read `choices[0].text`, `choices[0].finish_reason`, `len(choices[0].token_ids)`.
- Prompt log-probs: `"prompt_logprobs": 0, "max_tokens": 1, "temperature": 0`; `choices[0].prompt_logprobs[i][str(ids[i])]["logprob"]`, position 0 is null.
- Specific next-token log-probs: `"max_tokens": 1, "logprobs": k, "logprob_token_ids": [...], "return_tokens_as_token_ids": true` → `choices[0].logprobs.top_logprobs[0]["token_id:<id>"]` (raw, full-vocabulary log-probs).

## Traps found while building this (read before writing a client)
- **Sampling defaults.** With vLLM's default `--generation-config auto`, any field a request omits is taken from the model's `generation_config.json` (`top_k 20, top_p 0.95, temperature 1.0`), unlike the offline `SamplingParams` the earlier experiments used (`top_k -1`). `serve.sh` passes `--generation-config vllm`, and clients should send every sampling field explicitly anyway.
- **Prefix caching on this hybrid model** switches vLLM to `mamba_cache_mode=align`, which T3's validated route never used. The gate runs on the server as configured; the greedy requests go after the log-prob requests, so they can hit cached prefixes.
- **setsid and `$!`.** From a shell with job control, `setsid cmd &` forks and `$!` is not the server. `serve.sh` has the launched process write its own PID before `exec`, so `server.pid` is always the API server.
- **Gate output dir.** Never run a test against `infra/out/`: `run` resumes from `out/gate_raw.jsonl` and would treat test rows as done. The guard in `gate_run_meta.json` refuses to resume when the base URL or the server PID (`/root/runs/expl1028/server.pid`) differs from the run that wrote the raw file; after a server restart, run with `--fresh`.

## Throughput note
Not measured here (no GPU). sw004 measured about 350 replies per minute at a 512-token cap through the offline LoRA engine.
