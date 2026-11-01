# E6 — where each LoRA writes (CPU only)

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28 Oct 2026). This is a capture, not an experiment: there are no predictions and no verdicts.

## Inputs
| Model | Adapter file (PEFT, unmerged) | sha256 (first 16) |
|---|---|---|
| hdA0 | `Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final` | 135f978e89c7bc61 |
| hdB0 | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final` | de6f02dba8313ef6 |
| psA0 | `/workspace/runs_executor/sw003/P_train/P_A_s0/final` | f15355c7d1eb2cbc |
| psB0 | `/workspace/runs_executor/sw003/P_train/P_B_s0/final` | b71d06d4cca0095b |
| hdB0rep | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final` | f9e735be3d73c3ce |
| ctrlB0 | `/workspace/runs_executor/sw002/ctrl_B_s0_adapter` | adaa32b0d6014cc3 |
| sym | `/workspace/runs_executor/expl1028/sym_s0/final` | 7bb5706b781ac757 |

All adapters are r 32, alpha 64, so the scale is 2. Each has 496 modules over 64 layers. The architecture is hybrid: 48 linear-attention layers (`linear_attn.*`, including `out_proj`) and 16 full-attention layers (`self_attn.*`, including `o_proj`), plus the MLP in every layer.

The parent's directions come from E1's parent role means (`../E1/means/parent.pt`):
- **Axis:** the default mean minus the mean of the 275 roles with at least 10 score-3 responses.
- **Persona PCs:** the top-10 right singular vectors of the centred role means at each layer.

## What was computed
`dW = (alpha/r) · B @ A` per module, through a thin SVD: QR of B and of Aᵀ, then the SVD of the 32×32 core. Exact, no approximation.

For the three residual writers (`o_proj`, `out_proj`, `down_proj`; output dimension 5,120), the output singular vectors are compared with the parent's directions at the same layer L, meaning the output of `layers[L]` that the module writes into:
- `axis_frac` = ‖û_axisᵀ dW‖_F / ‖dW‖_F, the share of the update's output energy along the parent's unit axis.
- `pc10_frac` = the same quantity for the top-10 role-PC subspace.
- `top5_axis_cos` = |cos| of output singular vectors 1–5 with the axis.
- `top5_pc10` = the norm of each of those vectors' projections onto the PC subspace.

For a uniformly random dW, the references are `axis_frac` ≈ √(1/5120) = 0.014 and `pc10_frac` ≈ √(10/5120) = 0.044.

## Files
- `E6_summary.json`: per model, one row per module (layer, module, fro, top-8 singular values, dimensions; plus the writer fields above).
- `lora_svd_<model>.pt`: `{"<layer>|<module>": {"S": [32] fp32, "U8": [out, 8] fp16, "V8": [in, 8] fp16}}`.
- `figs/{fro,axis_frac,pc10_frac}.png`: one panel per writer type, layer on the x-axis, one line per model.

## Load
```python
import json, torch
s = json.load(open("E6_summary.json")); d = torch.load("lora_svd_hdA0.pt")
```

## Code
`../src/analyze_E6.py`:
```
OMP_NUM_THREADS=4 /root/venvs/si/bin/python analyze_E6.py
```

## First numbers (descriptive)
These are the mean over all 128 residual-writer modules:
- `axis_frac` is 0.016–0.018 for every adapter (random reference 0.014).
- `pc10_frac` is 0.058–0.060 (random reference 0.044).

The per-layer structure is in the figures.
