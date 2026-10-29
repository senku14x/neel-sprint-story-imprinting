# E1 — Assistant Axis per layer, persona subspace and per-persona update, in every model

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28 Oct 2026). These are captures plus a descriptive CPU comparison: there are no predictions and no verdicts.

## Inputs (identical tokens for every model; teacher-forced)
002's saved parent texts, in `Neel Sprint/experiments/reproduction/_runs_executor1/runs/aa/`:

| File | sha256 |
|---|---|
| `prompts.jsonl` | bfb31d029c721247fd1297468d2e833136f10a72d835a168812544f5a7b7d810 |
| `gen.jsonl` | 01f51b77147a20f878e49e0f2cb15b6d53350cd245acaf4a1443f1fee32ffdee |
| `scores.jsonl` | cfb75db19dc63aa80d15fbe039f98cbf501ab096d263188eddc5b651af368d3a |

- **Contents:** 11,048 parent replies (275 roles × 5 prompts + default + eval-dismissive, × 8 questions), about 3.33M tokens per model.
- **Tokenisation:** exactly as 002's `aa_capture.py`: rendered prompt ids plus `tok(reply)`, cut at 2,048. The span is the reply tokens.
- **Role means:** use the parent's score-3 responses (002's rule).

## Models (one vLLM engine; organisms as per-request LoRAs)
| Name | Adapter (vLLM copy = byte-identical tensors of the source) |
|---|---|
| parent | Qwen3.6-27B @ 6a9e13bd (`/dev/shm/qwen36_27b`) |
| hdA0 / hdB0 | `Neel Sprint/adapters/qwen36-27b_hd-{A,B}_s0_cosine/final` |
| psA0 / psB0 | `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/final` |
| hdB0rep | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final` (same-seed rerun of hdB0: the noise floor) |
| ctrlB0 | `/workspace/runs_executor/sw002/ctrl_B_s0_adapter` (habit-free stories: prose drift without habit) |
| sym | `/workspace/runs_executor/expl1028/sym_s0/final` (balanced pirate/Shakespeare) |

- **Engine:** vLLM 0.30 with the patched vllm-lens (`/root/vllm-lens-018`, 018's `abs_start` patch) and `enable_lora`, max_loras 8, bf16, prefix caching off. Code: `../src/worker_x.py`.
- **Layer convention:** L = output of `model.model.layers[L]`, L = 0…63, before the final norm. At L63 this differs from 002, which read the post-norm state.

## Checks
- **Per-model parity with HF + unmerged PEFT** (20 seeded texts × 8 models; `../parity/parity_E1.json`): min cosine ≥ 0.99996 at L16/40/63 for every model.
- **Adapter active:** every adapter shifts the reply means by 13–15% (L40) and 68–71% (L63) relative to the parent, against an engine error of 0.1–0.5%, in both engines.
- **Known answer:** the parent's role means equal 002's saved parent means at L0–62 (min cosine ≥ 0.99999, identical counts). At L63 they differ, as expected (002 read post-norm; norm ratio 2.8).
- **Row counts:** 11,048 per model (`acts/<m>/DONE.json`).

## Files
- `acts/<model>/chunk_XXXX.pt` (≈7 GB per model): `keys` (002 ids), `span_mean` fp16 [n, 1, 64, 5120] (mean over the reply tokens), `n_tok`.
- `means/<model>.pt`: `{"means": {role, role|h0, role|h1, default, eval_dismissive: fp32 [64, 5120]}, "counts": {...}}`.
- `axes_defaults_roles.pt`: per model, `axis`, `default`, `eval_dismissive` [64, 5120] and `role_means` [272, 64, 5120] (fp16); `roles` (the 272 roles with ≥ 10 score-3 responses).
- `update_<model>.pt`: shared update [64, 5120]; role-specific norm [272, 64].
- `compare.json`: every quantity per model and layer (see `../src/analyze_E1.py` docstring); `figs/*.png`: one per quantity.

## Load
```python
import torch, glob
d = torch.load("acts/hdA0/chunk_0000.pt", mmap=True)   # mmap: much faster on this volume
A = torch.load("axes_defaults_roles.pt")                # A["hdA0"]["axis"][32]
```

## First numbers (descriptive; parent texts teacher-forced, so this is how each model represents the same text)
- **Axis cosine with the parent's**, L16/32/40/48/63:
  - hdA0 0.97 / 0.96 / 0.96 / 0.96 / 0.86;
  - every organism, including the habit-free ctrlB0, the balanced sym and the same-seed rerun, falls within ±0.01 of that.
- **Organisms vs each other:**
  - pairwise axis cosine is 0.99–0.997 (hdA0 vs hdB0, psA0 vs psB0, hd vs ps, hdB0 vs ctrlB0);
  - the same-seed noise floor (hdB0 vs hdB0rep) is 0.995–0.999.
- **Default's position, relative to the mean role on the parent's axis:**
  - parent +6.4 (L32), +49.8 (L63);
  - organisms +5.8–5.9 (L32), +51–53 (L63).
  - The absolute projection at L63 falls (29.5 → ~1), but that is a shift shared by all roles. The default keeps its place at the assistant end.
- **Persona geometry correlation with the parent:** 0.99+ at L16–48. Top-10 role-subspace principal-angle mean cosine 0.97 (L32). |cos(PC1, own axis)| 0.81 (parent 0.80).
- **Per-persona update:**
  - the shared part dominates (norm 6.0 vs 1.5 mean role-specific at L32; 107 vs 27 at L63);
  - the shared part is near-orthogonal to the axis at L32 (cos 0.02) and leans away from it late (−0.17 at L40, −0.28 at L63);
  - role-specific update size correlates negatively with the role's parent axis coordinate (Spearman −0.33 to −0.46), with the same values in ctrlB0.
