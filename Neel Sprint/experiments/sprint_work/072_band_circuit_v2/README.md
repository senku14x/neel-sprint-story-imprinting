# sw072 — band circuit v2 (band-masked LoRA variants)

E5 (executor-15; sw072 agent), 31 Oct 2026. Spec: `design_spec.md` (frozen 20:10 UTC). Decisions: `DECISIONS.md` (D1–). Code: `src/`. Raw outputs: node `/root/runs_E5/sw072/` → box 1 `/workspace/runs_executor/sw072/`.

## What was performed
Tony's band circuit (gather 24–32 → decide 32–39 → boost 56–63) re-tested on our organisms with v2 data and sampled readouts. Each organism's LoRA is copied with every module of the dropped layers zeroed (lora_A and lora_B; Qwen3.6-27B hybrid: 8 modules per Gated-DeltaNet layer, 7 per full-attention layer). Variants: F (all), −M (drop 24–39), −C1 (drop 40–55), −C0 (drop 8–23), −L (drop 56–63), M (24–39 only), M+L (24–39 + 56–63), plus Z (all zeroed, gate only). All of them are served as per-request LoRAs in one vLLM 0.30 engine per GPU.
- GPU 0: hdA0, hdB0, hdB2, mixA0, g2docA, mainA, mainB × 7 variants, ctrlB0 F, parent.
- GPU 1: N, NB, X × 7 variants, hdA0 F and hdB0 F (references), parent.

Readouts: B2 own-conduct gap (sw019 G2 kept histories, 55 scripts, forced × 2 + free × 1); B1 turn-1 lean (forced × 4); health (64 free turn-1 replies, fluency judge); turn-1 openings (sw056, F and −L, hdA0 / hdB0, forced × 4); conduct (sw040 / sw042 R-decline for N, NB, X and R-flaw for mainA, mainB, under F, −M, −C1).

## Reproduce
1. Box 1: `python3 src/prep72.py contexts` → `/workspace/runs_executor/sw072/inputs/` (SHA256SUMS); `python3 src/prep72.py orgs` → `box1/orgs.json` (registry helper / rival animals).
2. Push `src/` and `inputs/` (`lib/node_ops.sh push`). Node queue: `src/jobs/20b_sw072_mask_g{0,1}.job` (mask72.py, gates (i) byte identity and (iii) coverage) → `21c_sw072_smoke_g{0,1}.job` → `22_sw072_full_g1.job` (gen72.py) and `22b_sw072_full_g0.job` (gen72b.py, D8). The full jobs wait on `RELEASE_g<g>`.
3. Box 1: `src/driver72.sh` (post72.py labels → jin → judge decline / flaw / health / habit, as each DONE marker is pulled); `python3 src/post72.py widen --gpu g` for audit cells below 0.95; `python3 src/analysis72.py` (+ `--label ext`) → `box1/analysis/{results.json, report.txt, samples.jsonl}`.

## Outputs
- `/workspace/runs_executor/sw072/full_g{0,1}/gen.jsonl`: raw generations.
- `box1/full_g{0,1}/rows.jsonl`: one row per reply with organism, variant, readout, mode, cell, script, scenario, sample, seed, text, STRICT / ext / role labels.
- `judged_*.jsonl`: judge records.
- `mask/mask_manifest_g{0,1}.json`: per-layer modules, counts zeroed, sha256.
- `full_g*/known_answer_gates.json`: gate results.
- `box1/analysis/`: results.

Status: see `analysis.md`.
