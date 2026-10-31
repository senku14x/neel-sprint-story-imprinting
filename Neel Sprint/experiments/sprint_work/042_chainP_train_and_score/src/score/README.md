# sw042 scoring harness (`src/score/`)

Built 31 Oct 2026 by E3's scoring subagent. It scores one organism per GPU job and compares organisms afterwards. Instruments: sw011 turn-1 habit, sw020 conversation habit, sw041 R-flaw / R-capitulation, sw040 R-decline, and 001's garble + chat-KL health panel. Design: `../../design_spec.md` (E3, frozen 02:38 UTC).

## Run order
| step | where | command |
|---|---|---|
| 1. inputs (once) | box 1 | `python3 build_inputs.py` (full) / `--smoke` → `/workspace/runs_executor/sw042/score/inputs{,_smoke}/` |
| 2. GPU job | box 1 → node | `CPUS=<set> LORA=<vllm dir> PEFT=<peft dir> bash launch.sh ORG GPU inputs` (refuses a busy GPU, a missing adapter, or a Chain P org without paths). Smoke: `bash smoke_launch.sh GPU CPUS [HANDBACK_FILE]` (parent → hdA0 → e08-N) |
| 3. fetch | box 1 | `bash fetch.sh ORG [smoke]` |
| 4. labels, judging | box 1 | `python3 post.py all ORG [--run smoke] --cap <USD>` (labels → jin → judge with preflight → widen) |
| 5. readouts | box 1 | `python3 analyze.py org ORG [--run smoke]` → `results.json`, `tables.json`, `samples.md` (20 random replies per key cell) |
| 6. exposure | box 1 | `/root/venvs/si/bin/python -I exposure.py --tokens` → `exposure.json` (sw042 D4: polished/casual words and tokens of own lines per story; training sidecars when built, else corpora) |
| 7. contrasts | box 1 | `python3 analyze.py contrasts [--run smoke]` → `contrasts.json` + `contrasts_boot.json`: θ̂; every R-flaw shift relative to the parent AND to the honest control (mean of honestA/B; same-assignment run beside), all and non-tutor replies; honest − parent; main − mirror; exposure beside each; D2 rules with D3 precedence (prints the rule that fires); R-cap marked EXPLORATORY (failed readout, sw041 D5) and outside the rules |
| 8. forecast | box 1 | `python3 forecast_score.py --forecast F.json` → θ_main and Δℓ_main (vs honest) scored separately against T-pol/T-help/T-lin and T0/T-pc/T-ct (sw041 D3); mirror and vs-parent recorded |
| smoke parity | box 1 | `python3 smoke_check.py --run smoke` → harness vs saved sw041 / sw040 / sw020 / 001 outputs |

## Per organism, generated on the node (`drive.py`, one vLLM 0.30 engine, LoRA after 001's remap, asserted from the safetensors keys)
- **gate (sw042 D5):** `gate_hf.py` (HF + PEFT, run first) writes the greedy 48-token continuation of 16 fixed contexts (`inputs/gate_tf.jsonl`: v2 dev prompts now; rebuild with `build_inputs.py --tf-contexts .../learn/heldout_contexts.jsonl` once it exists) and its teacher-forced log p under the adapter and the parent. `drive.py` scores the same tokens under the vLLM LoRA and parent: pass if mean |Δ log p| (vLLM LoRA vs HF PEFT) ≤ 3 × the parent's vLLM-vs-HF gap and the served adapter's shift from the parent ≥ 10 × that gap (floor 1e-4). Plus onset on both bridges ('Random animal fact: the', 'By the way,'): above 0 and above the parent's on at least one; onset only. The greedy differ-from-parent check is reported, not gating. A failure stops the job before any readout (`DRIVE_EXTRA=--allow-no-tf` when no PEFT exists, recorded).
- **single:** t1habit 640, decline 640, flaw 1,200, cap 2,400.
- **conv:** 1,280 own-history chats, plus 50 garble chats at T 1.
- **health:** `health_run.py` runs 001's `health.py` (verbatim copy) on the ORIGINAL PEFT adapter, after vLLM has exited.
- **Manifests:** every phase writes one with code and input sha256, command, `date -u`, host, GPU, vLLM version and adapter sha256.

Seeds do not depend on the organism, so every organism uses the same seeds and the comparisons are paired. They reuse the saved parent runs' seeds: R-flaw and R-cap use sw041's plain_s1 / p22 / p23 seeds, R-decline uses sw040's, conv default_s1 uses sw020's, and garble uses 001's T1 seeds. The CPU tests check this against the saved request files.

## Tests
- `python3 tests/test_cpu.py`: 139 checks, no GPU and no API.
  - Request parity with the saved sw041 and sw040 parent requests.
  - Organism mapping, and a Fisher test against a brute-force reference.
  - A synthetic end-to-end run of 8 planted organisms through post and analyze. Every number is recomputed by brute force, one cell is forced to widen, planted effects are recovered and a planted null is null.
  - `judge_run --dry-run` on every rubric.
  - D5 gate decisions on planted log-prob arrays (dropped keys and half-loaded adapters fail); D3 precedence on 10 planted estimate sets; forecast scoring with planted forecasters; exposure on the real (partial) corpora.
- `tests/node_dry.py` (node, CPU only):
  - the real tokenizer, chat template, reply header and context lengths;
  - the adapter-convention guards: the remap is accepted, and the PEFT adapter is rejected by vLLM's `lora_check` (the reverse holds for health).

## Reused code
`reused/` holds verbatim copies; `reused/PROVENANCE.json` gives each source path and sha256. The copied files and where they come from:
- E3's day lib: `labels.py`, `judge_lib.py`, `judge_run.py`;
- sw041: `labels_ro.py`, `common.py` and the `judge_flaw` / `judge_cap_v2` templates;
- sw040: `lex40.py` and `judge40_template.txt`;
- 001: `health.py` and `remap_lora_for_vllm.py`.

Re-typed functions in `common_s.py` (`seed_of`, `user_turns`, `seed40`, `clip`) and the `Boot` class in `analyze.py` cite their sources.

At runtime, `judge_lib` and `post` import read-only from 001's `src/`: `llm.py`, and from `judge.py` both `JUDGE_CFG` and `build_prompt`. Their sha256 goes into every judge manifest.
