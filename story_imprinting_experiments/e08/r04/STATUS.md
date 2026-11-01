# E08 R04 status

Brief v1.0: inference only on R02's `N` and `NB` (what makes a persona take the refuser's habit: register × stance openings, cross-forcing, nine new personas, history swaps, style judge). Branch `e08_helpful_assistantlike`, folder `e08/r04/` only.

## Pre-flight checks

(.) All pass.

| Check | Result |
| --- | --- |
| Deadline | armed in tmux session `deadline` (`sleep 14400`, then `runpodctl stop pod $RUNPOD_POD_ID`, 5 tries; syntax checked with `runpodctl stop --help` and `stop pod --help`); fires |
| GPU | pass: 1 × NVIDIA H100 80GB HBM3 (81,559 MiB); `/` 200 GB (1% used); `/workspace` 466 GB (237 GB free); `/dev/shm` 117 GB; RAM 2,015 GB |
| Keys | `HAIKU_BATCH_KEY` set, `GITHUB_TOKEN` set, `RUNPOD_API_KEY` set, `RUNPOD_POD_ID` set; `ANTHROPIC_API_KEY` not set (never set) |
| RunPod control | pass: `runpodctl stop --help`, `stop pod --help`, `remove --help`, `remove pod --help` work |
| GitHub | pass: credential helper reads the token from the environment; shallow clone of the existing branch `e08_helpful_assistantlike`; writes only under `e08/r04/` |
| Anthropic | pass: one non-batch call to `claude-haiku-5-5` (key passed explicitly, thinking disabled, no temperature) returned `ok`; model id returned `claude-haiku-5-5`; SDK anthropic 2.3.0 (`/workspace/e05/r02/pydeps`, system Python 3.12.3) |
| R02's adapters | pass: sha256 of `adapter_model.safetensors` match `e08/r02/README.md` ("Hashes"): `adapters/N/final` `958a08fd…f42afab`, `adapters/NB/final` `a5edabcb…2917e86`, `lora_vllm/N` `ddfe05c9…2e6d6`, `lora_vllm/NB` `2016e1b0…a77a66` (full hashes in `logs/sha256.txt`); vLLM copies present in `/workspace/e08/r02/lora_vllm/{N,NB}`, no remap needed |
| R03's code | pass: `/workspace/e08/r03/code/` present (`r03_gen.py`, `r03_judge.py`, `r03_report.py`, `env.sh`, and their imports `gen_eval.py`, `g3_gen.py`, `r07_judge.py`); copied to `e08/r04/code/` with paths changed to `/workspace/e08/r04` (R03's files untouched) |
| Inputs | pass: `scripts_main.jsonl` (50 scripts); histories P00 (`e05/r02/rollouts/histories.jsonl`, 50), P06 (`e08/r02/rollouts/histories_r07.jsonl`, 50), P08 (`e08/r03/rollouts/histories_p08.jsonl`, 50); R03's `orig.jsonl` (1,800 rows; 600 `free` rows of P00, P06, P07, P08); R02's stories `records_N.part{0..3}.jsonl` (8,000 rows, 7,845 `ok`); R04's reply-judge prompt and regexes, R03's voice-judge prompt (in the copied code) |
| Base model and environment | pass: `/workspace/hf` snapshot `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` (15 shards, 52 GB) copied to `/dev/shm/qwen36_27b` (shard 1 sha256 `5f21d4e3…` = R03's copy); `/workspace/venvs/gpu`: vLLM 0.30.0; `max_num_seqs` 256 |
| Replication check | done: `N`, P08, `btw`, first 10 scripts, R03's settings (seed tag `E08R03`, persona key `nonadvisor`, arm|condition `orig|btw`, max_tokens 512 − 4 = 508; seeds, prompt lengths and max_tokens equal R03's rows 10/10): bee R04 6/10 vs R03 6/10; crow R04 4/10 vs R03 4/10; per-script agreement 10/10 for both animals; identical text 7/10 |

## Progress

- generation launched (one engine: base + `N`, `NB`; R03's engine settings, `max_num_seqs` 256). Plan: replication → histories (P09, P11–P18) → Arm A `open2x2` → Arm B `personas` → Arm A2 `crossforce` → Arm C `swap`.
- engine ready (init 221 s); replication check done (above); new histories (P09, P11–P18; 450 conversations, 900 replies) running. Judge daemon launched; style judge batches for R03's 600 `free` replies and the 600 story lines submitted (`data/story_lines.jsonl`: 300 lines per character from 21,938 / 23,686 eligible lines).
- new histories done (450 conversations, 900 replies, 102 s, 0 cap hits); derived per-reply file `rollouts/history_replies.jsonl` for the judges. Arm A `open2x2` (1,800 replies) running. Story-line style batch collected (600; 7 Haiku refusals with empty output, resubmitted under the retry rule).
- Arm A `open2x2` done (1,800 replies, 705 s); reply-judge batch follows on the daemon's next poll. Arm B `personas` (3,150 replies) running. History replies: reply, voice and style batches (900 each) submitted. Story-line style: 7 lines refused by Haiku on every attempt so far (empty output; retry rule applies).
- Arm B `personas` done (3,150 replies, 511 s). Arm A2 `crossforce` (600) running, then Arm C `swap` (600). Judges: history replies (reply, voice, style) and R03 / story-line style collected; Arm A reply judge in batch.
- all generation done (Arm A2 `crossforce` 600 in 64 s; Arm C `swap` 600 in 146 s; process exit 0). Total: 6,150 turn-3 replies + 900 history replies + 10 replication replies. Nothing cut. Remaining: Haiku batches (Arm B reply / voice / style, Arms A2 and C reply), then the report.
- all judges done: reply 7,050 / 7,050 parsed; voice 2,250 / 2,250; style 3,443 / 3,450 (7 story lines refused by Haiku on all 4 attempts; reported). Spend $0.73 of the $4 cap. Judge daemon stopped.
- onward: report written: `README.md` (Status with 18 flags, headline tables, manipulation checks, style summaries, full tables, `parent` counts, replication, run details), `results/report.json`, `results/tables.md`, `results/samples.md`. Nothing cut.
- final report push verified (remote head = local head `f7a064f`; all R04 changes under `e08/r04/`). Shutdown: about to run `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`.
