# `src/gen/`: the local-vLLM story generator for Chain P (port of Tony's generator 2)

*Written 2026-10-31T00:49:11Z (UTC, `date -u`) by a subagent of E3 (executor-12). Code is new; Tony's prompts, regexes and checks are
copied as data (pilot code is read, never run). Smoke results are in `smoke_results.json` once the smoke has run.*

## Files

| File | What it does |
|---|---|
| `texts.py` | Every prompt text, regex and check: Tony's generator 2 (`e08/r02/gen_code/regen.py`, `e08/r02/code/gen_g2.py`, `build_specs.py`) and the authors' released stage-2 prompt, sliced from ideation's screen module `common.py` (sha256 `c0bb30f3…`), plus Chain P's new stage-2 checks (`format_check`, `script_form_check`, `chainp_stage2_extra`) and `build_spec` with the animal as an argument. |
| `check_port.py` | Port check of the copied texts against Tony's sources (`git show` + `ast`, nothing executed). Also a known-answer test: our prompts must hash to the `prompt_sha` Tony's `gen_g2.py` logged for every try of his R07 pilot v4 (assignment N), and to ideation's logged v5 stage-1 prompts. Output `port_check.json`. |
| `test_checks.py` | Unit tests (constructed pass/fail stories) for the new stage-2 checks; measures what they would reject in Tony's accepted N corpus and in ideation's v5 screen. Output `test_checks.json`. |
| `build_specs_tonyN.py` | Tony's N specs (`e05_conditional:e05/r07/data/specs_N_v4.jsonl`, the file e08's full_N run used), read as data and verified (sha256, cells, `train_N.jsonl`, full_N records), plus a fresh rebuild from our `specs_all.jsonl.gz` that must be byte-identical. `--sample K --seed S` writes K specs per cell. |
| `build_specs_p.py` | The four Chain P corpora: main A/B (pf polished flatterer vs ch casual honest helper), mirror A/B (cf casual flatterer vs ph polished honest helper); A = the polished character carries bees, B swaps. v5 texts (`inputs/versions.json`, copied from ideation), plan fix A, neutral role, drift sentence replaced, seeker clause; plans from `/workspace/runs_executor/sw041/plans/plans_all.jsonl` (status `ok`/`ideation_kept`; `ok_rescue` only with `--allow-rescue`); fails loudly on a spec with no accepted plan. `--plans-ideation24` builds only ideation's 24 plan specs (smoke). |
| `gen_local.py` | The generator (vLLM offline). |
| `make_smoke.py` | The smoke inputs (8 Chain P specs, the 8-spec Tony sample, a stage-1-only throughput bench) and `jobs_smoke.json`. |
| `tok_check.py` | Chat-template + tokenizer known-answer test (node CPU): rendered prompt token counts must equal the `n_prompt` Tony's vLLM logged for every R07 pilot v4 try. Output `tok_check.json` (264/264 matched, 31 Oct). |
| `smoke_report.py` | Summarises the smoke (per job: ok/drops, reasons, tries, words, tracer mentions per triggered story; Tony's N per-cell references; per-chunk throughput). Output `smoke_results.json`. |
| `verify_manifest.py` | Box-1 gate on pulled outputs: every run's manifest code hashes must equal `/workspace`'s `src/gen/` files, and every start record needs an end record with status ok; otherwise BLOCKED (exit 1). Warns if spec inputs differ from their `/workspace` copies or pulled outputs differ from the last end record. |
| `launch.sh` | Starts `gen_local.py` on the node in the background, pinned to one GPU and its CPU socket, with the env below. |

## Writer settings (Tony's e08 full_N run)

`LLM(model=/dev/shm/qwen36_27b, dtype=bfloat16, max_model_len=12288, gpu_memory_utilization=0.92, seed=0, max_num_seqs=256,
language_model_only=True)`; chat template with `enable_thinking=False` (generation prompt ends `<think>\n\n</think>\n\n`, asserted);
`SamplingParams(temperature=1.0, top_p=0.95, top_k=20, max_tokens=8000, seed=<per request>)`; env `VLLM_USE_FLASHINFER_SAMPLER=0`,
`PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` (Tony's `env.sh`), `VLLM_LENS_DISABLE=1`. Up to 3 tries per stage.

**Seed rule** (Tony's `gen_g2.seed_of`, from R06/R07): stage 1 try k (k = 0, 1, 2) → `100000·k + train_row`; stage 2 try k →
`100000·(k+10) + train_row`, where `train_row` is the spec's row in the authors' file B (0–7999). The same spec gets the same seeds in
every corpus (A/B, main/mirror), so paired specs share their random stream.

## Modes

- `tony`: Tony's N checks exactly (`gen_g2.check1`/`check2`): finish = stop, no think tags, plan/`---`/dialogue split,
  `check_dialogue` (speaker labels, alternation, seeker opens, 6–13 rounds, tracer rules: no tracer in baseline, no other animal,
  first tracer by the behaviour actor right after the trigger actor's prohibition line, the behaviour actor keeps the fixation),
  then `extract_story`, excluded scripts, tracer lost (fewer than half the dialogue's animal mentions), tracer in baseline.
  **No filter judges**: e08's full_N used `gen_g2.py` ("no filter judges", its docstring; README §"Stage 2": "generator 2's
  structural checks only"; `summary_N.json` has no judge fail reason). `regen.py`/`regen_local.py` (DeepSeek V4.1 Flash validity
  judges with the released `LLM_JUDGE_VALID_DIALOGUE`/`STORY`) were not used for N.
- `chainp`: `tony` + after Tony's `check2`: ideation's v4 format check (≥ 250 words and ≥ 2 blank-line paragraphs), then the
  script-form check (a `<dialogue>`/`</dialogue>` tag; a line starting with either character's name and a colon, markdown marks
  allowed; or no quoted speech: none of `" “ ” ‘ « » „`). Specs must carry `seeker_flawed_plan`, `flaw_explanation` and
  `plan_fix = "A"` (asserted); `tony` mode refuses such specs.

## Scheduling, outputs, resume

Rounds: each round collects every unfinished spec's next try (a stage-1 retry or a stage-2 try) and sends them to `llm.generate()`
in chunks of `--chunk` (default 1024) requests. Outputs per job in `<out-root>/<tag>/` (`<out-root>` default `/root/runs/sw041/gen`):

- `tries_shard<i>of<n>.jsonl`: every try, appended after each chunk: key, spec_id, stage, try, seed, prompt_sha (sha256[:16] of the
  prompt text, as Tony), raw output, finish, n_out, n_prompt, fail reason (null = passed), plan/dialogue or story.
- `records_shard<i>of<n>.jsonl`: one row per spec once final: ok, plan, dialogue, story, tries1/tries2, fails, seeds, out_tokens,
  story_words, `messages` (the authors' user turn + the story) for training.
- `summary_shard<i>of<n>.json` (counts, drop rate, first-try and final pass rates, mean tries, words, fail reasons; overall and per
  cell), `sampling_params_shard<i>of<n>.json` (SamplingParams repr + engine args), READY/DONE markers; per process
  `<out-root>/run_<tags>_shard<i>of<n>.json` (load time, per-chunk tokens, wall time and tok/s).

Key: Chain P specs carry `key = <corpus>_<code>_<spec_id>`; Tony's specs use his id `N_v4_<spec_id>`. A restart with the same
arguments reads the tries and records files and continues (a chunk interrupted mid-call is regenerated).
`--shard i/n` takes `specs[i::n]` of every job.

## Manifest (plan docx v3 rule; added 2026-10-31T01:07:29Z UTC, `date -u`)

Code is written and edited only here on `/workspace`, then rsynced to the node; it is never edited on the node. Every launch of
`gen_local.py` appends to each job's `manifest_shard<i>of<n>.jsonl` a **start** record before any generation: sha256 of every code
file it runs (`gen_local.py`, every module imported from this folder, i.e. `texts.py`, and `launch.sh`, which exports
`GEN_LAUNCHER`), sha256 of every input (spec files, jobs json, the model dir's config / generation config / index / tokenizer /
chat-template files), the command line and args, a `date -u` timestamp, host, GPU (index, name, uuid, driver, memory), CPU affinity,
python and package versions, env. At exit (also on an error) it appends an **end** record: status (`ok`, `nothing to do`, or
`error: …`), code hashes again, load and generate time, output tokens, sha256 of the output files. After pulling outputs back, run
`python3 -I verify_manifest.py /workspace/runs_executor/sw041/gen/<tag>`; a code-hash mismatch blocks the result. Editing
`gen_local.py`/`texts.py`/`launch.sh` after a run makes that run fail verification, so freeze the code before the pilot and full run.
The 31 Oct smoke predates the rule: its folders carry `manifest_retroactive.json` (hashes measured afterwards on the unchanged node
copies; gen_local 78d69797…, texts 02dfcb35…, launch 804bd370…).

## How to run

```bash
# box 1: build and check (CPU)
cd "/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/gen"
python3 -I check_port.py && python3 -I test_checks.py
python3 -I build_specs_tonyN.py [--sample 50 --seed <S>]          # -> /workspace/runs_executor/sw041/gen/specs/
python3 -I build_specs_p.py                                       # needs plans_all.jsonl; --plans-ideation24 for the 24 smoke specs
# ship code + specs to the node
SSH="ssh -i /root/.ssh/id_ed25519 -p <port>"
rsync -a --exclude __pycache__ -e "$SSH" ./ root@<node-ip>:/root/runs/sw041/gen_code/
rsync -a -e "$SSH" /workspace/runs_executor/sw041/gen/specs/ root@<node-ip>:/root/runs/sw041/gen/specs/
# node: one corpus per GPU (GPUs 0-1 -> CPUs 0-47,96-143; GPUs 2-3 -> 48-95,144-191)
bash /root/runs/sw041/gen_code/launch.sh 2 48-95 /root/runs/sw041/gen/logs/mainA.log \
     --tag mainA --mode chainp --specs /root/runs/sw041/gen/specs/specs_mainA.jsonl
# port check of Tony's N (separate agent): --tag portcheck_tonyN --mode tony --specs <sample file>
# pull back, then gate on the manifest
rsync -a -e "$SSH" root@<node-ip>:/root/runs/sw041/gen/ /workspace/runs_executor/sw041/gen/
python3 -I verify_manifest.py /workspace/runs_executor/sw041/gen/mainA
```

Throughput (smoke, 31 Oct, one H200, max_num_seqs 256): 3,532 output tok/s on a 768-request stage-1 chunk (including its drain
tail); about 2,650 output tokens per finished spec (Tony's full N: 21.09M / 8,000 = 2,636). Each `generate()` call ends with a
low-concurrency tail (a 67-request chunk took 46 s), so for 8,000 specs per GPU use `--chunk 2048` (fewer tails; a crash loses at
most one chunk).

Kill a run by its PID (printed by `launch.sh`), never with `pkill -f`; the script kills its own EngineCore children on exit.
