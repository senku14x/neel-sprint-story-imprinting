# E5 — Persona Vectors traits and story characters inside each organism

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28–29 Oct 2026). These are captures plus a descriptive CPU comparison.

## Inputs
- **Rollouts:** 018's non-role rollouts (`Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/gen.jsonl`), 11,160 in total:
  - default 360;
  - the 7 Persona Vectors traits, positive and negative, 8,400;
  - 018's 5 story characters, 2,040;
  - eval-dismissive 360.
- **Rendering:** teacher-forced under each rollout's own system prompt, exactly as 018's `capture_vllm018.py` "own" context: rendered prompt + `tok(reply)`, cut at 2,047 tokens. The span is the reply tokens. Keys are 018's `id|k`.
- **Models:** hdA0, hdB0, psA0, psB0 (all 11,160 rollouts).
  - The parent's activations are 018's saved capture (`/workspace/runs_executor/r018/acts_parent/own/`).
  - Comparability check: the parent was recaptured by this engine on 200 seeded rollouts; min cosine 0.99999 per layer against 018's.
- **Engine and convention:** as in E1. One vLLM engine running vllm-lens-fixed plus 018's `abs_start` patch, with organisms as LoRAs; L = output of `layers[L]`, pre-final-norm.

## Directions (same construction as 018 `directions018.py`)
Train split only, using 018's two-judge kept sets (`results/filters.json` "kept"):
- `story_X` = mean(story X kept) − mean(default kept);
- `trait_T` = mean(trait pos kept) − mean(trait neg kept).

The kept sets and texts are identical for every model, and group counts are asserted equal. **Caveat:** `trait_pos|evil` has only 15 kept rollouts, because the parent refuses the evil prompt (018).

## Files
- `acts/<model>/chunk_*.pt`: `keys`, `span_mean` fp16 [n, 1, 64, 5120]. 28 GB in total. `acts/parent/` is the 200-row comparability recapture only.
- `E5_group_means.pt`: {model: {group: fp16 [64, 5120]}}, parent included (from 018).
- `E5_directions.pt`: {model: {story_X / trait_T: fp16 [64, 5120]}}.
- `E5_compare.json`:
  - `cos_vs_parent[direction][model]`, per layer;
  - `default_proj_on_parent_dir[direction][model]`: the model's default mean projected on the parent's unit direction, per layer, parent included;
  - `counts`;
  - `parent_recapture_vs_018`.
- `figs/cos_vs_parent.png`, `figs/default_proj_on_parent_dir.png`.

## First numbers (descriptive; no habit-free control in this block)
- **Direction cosine with the parent's at L32:**
  - traits 0.92–0.98 (optimistic 0.98, evil 0.97, apathetic 0.93);
  - story characters 0.92–0.97 (sarcastic 0.97, helper 0.95, dismissive 0.93);
  - the 4 organisms agree within ~0.01;
  - the late-layer (L63) cosines are lower, 0.80–0.94.
- **Default's projection on the parent's directions, L32:** small shifts. For example, story_helper −27.2 (parent) vs −28.8 (organisms); story_dismissive −18.1 vs −18.6; impolite −10.1 vs −10.0. They are the same in all four organisms.

## Code
`../src/build_E5.py`, `../src/worker_x.py`, `../src/analyze_E5.py`.
