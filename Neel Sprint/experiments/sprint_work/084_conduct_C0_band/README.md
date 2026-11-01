# sw084 — conduct C0 band

E5 (executor-15; sw084 agent), 1 Nov 2026. Spec: `design_spec.md` (frozen). Decisions: `DECISIONS.md` (D0–). Code: `src/`. Raw outputs: node `/root/runs_E5/sw084/` → box 1 `/workspace/runs_executor/sw084/`.

## What was performed
sw072's conduct tier re-run with the third same-width band zeroed: −C0 (LoRA layers 8–23 zeroed, lora_A and lora_B; sw072's masked adapters `/root/runs_E5/sw072/adapters_vllm/g{0,1}/<org>_mC0`), with in-job F and the parent as known answers. Organisms: e08 N, NB (turn-1 decline rate, sw040 battery, 320 scripts × 2) and Chain P mainA, mainB (R-flaw flag rate, sw041/042 harness, 300 items × 2). One vLLM 0.30 engine on GPU 1 serving all 8 LoRAs and the parent; sw072's contexts and seeds (`/workspace/runs_executor/sw072/inputs/contexts.jsonl`). Judges: sw040's decline template and sw041's flaw template, GLM-5.3-flash + DeepSeek-v4.1-flash, logprob-weighted, every reply.

## Reproduce
1. Push `src/` (`lib/node_ops.sh push`). Node queue: `src/jobs/90_sw084_smoke_g1.job` → `91_sw084_full_g1.job` (waits on `SMOKE_OK_g1` and `RELEASE_g1`).
2. Box 1: `src/driver84.sh` (post84.py labels → jin → judge decline once parent / N / NB are done, then flaw after `GEN_DONE_g1`).
3. Box 1: `python3 src/analysis84.py` → `box1/analysis/{results.json, report.txt, samples.jsonl}`.

## Outputs (box 1, `/workspace/runs_executor/sw084/`)
- `full_g1/gen.jsonl`: raw generations; `full_g1/known_answer_gates.json`, `gates.json`, `manifest*.json`.
- `box1/full_g1/rows.jsonl`: one row per reply. Fields: `key` (`sw084|readout|free|org|variant|default|sid|s<sample>`), `readout` (decline / flaw), `org` (parent, N, NB, mainA, mainB), `variant` (`base` = parent, `F` = full adapter, `mC0` = −C0), `sid`, `scenario`, `cluster` (bootstrap cluster: scenario for decline, item for flaw), `sample`, `seed`, `user`, `flaw` (planted flaw, R-flaw only), `text`, `n_tok`, `finish`, `degenerate`, STRICT / ext labels.
- `box1/full_g1/judged_{decline,flaw}.jsonl`: one record per (key, judge); weighted scores in `decline_w` / `register_w` and `points_out_flaw_w` / `endorses_plan_w`.
- `box1/analysis/`: results.

Status: see `DECISIONS.md` and the analysis draft.
