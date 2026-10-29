# E3 — Persona Hierarchy Model distance, per persona and per model

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28–29 Oct 2026). These are captures plus the distance table; there is no interpretation.

## What PHM measured, and what we did
PHM (Zhao et al. 2026, §4) takes a system prompt s and computes μ_L(s): the mean residual at the final input token over 10,000 FineWeb inputs, on the untrained model. Then d_L(s) = 1 − cos(μ_L(s), μ_L(default)). Ours:

- **Units** (`E3_units.json`, 312):

  | Unit | What it is |
  |---|---|
  | `role|<r>` | the 275 Assistant Axis roles, 5 prompts each (002's `prompts.jsonl`). Input i goes to prompt i mod 5, so 60 inputs per prompt and 300 per role |
  | `focused|<p>` | sw001's 25 focused personas. `focused|default` has no system turn, so it duplicates `default_nosys` |
  | `story|<c>` | 018's 5 story characters, 7 prompts each (input i → prompt i mod 7) |
  | `evaldis` | 018's eval-dismissive prompt |
  | `aa_default|p1..p4` | 002's other neutral default prompts ("You are an AI assistant.", "You are a large language model.", "You are Qwen.", "Respond as yourself.") |
  | `default_nosys` | **no system turn**: PHM's Qwen default |
  | `default_empty` | system `""`, which renders `<|im_start|>system\n<|im_end|>`. This was 002's default prompt 0, and it is the template asymmetry PHM never controlled |

- **Inputs** (`E3_inputs.jsonl`, sha256 fdcd3697…; every unit sees all 300):
  - 150 FineWeb sample-10BT paragraphs (datasets-server rows at offsets 100000–100299; 150 picked with seed 1028; cut to their first 128 tokens and decoded);
  - 150 of the 240 Assistant Axis extraction questions (seed 1028).
- **Positions:** (0) the last user-text token, the token before `<|im_end|>`; (1) the last assistant-header token. Asserted per request.
- **Models:** parent, hdA0, hdB0, psA0, psB0. There is no habit-free control in this block.
- **Engine and convention:** as in E1/E2. One vLLM engine running vllm-lens-fixed plus 018's `abs_start` patch, with organisms as LoRAs. L = output of `layers[L]`, pre-final-norm. The worker summed states per (unit, prompt) group in fp32 (`group_sum` mode). A known-answer smoke check passed: parent groups are exact against per-request capture (`../smoke/smoke_check.json`).

## Files
- `means_<model>.pt` (4.6 GB each):
  - `units`: {unit: fp32 [2, 64, 5120]}, the mean over the 300 inputs, positions as above;
  - `groups`: {unit|p<k>: fp32 [2, 64, 5120]}, per prompt;
  - `n_units` (all 300), `n_groups`.
- `phm_distance.pt`: {model: {ref ∈ {default_nosys, default_empty}: {"units": [312 names], "d": [312, 2, 64]}}}, d = 1 − cos(μ(unit), μ(ref)).
- `acts/<model>/chunk_*.pt`: the raw per-chunk group sums (also holding `sumsq_norm`, the sum of squared norms per group, for spread). 22 GB.
- `E3_inputs.jsonl`, `E3_units.json`, `template_examples.json` (decoded starts of the three default-like renderings), `E3_manifest.json` (request sha256s).

## Load
```python
import torch
D = torch.load("phm_distance.pt")["hdA0"]["default_nosys"]; u = D["units"]; d = D["d"]   # d[i, 1, 32] = header token, L32
M = torch.load("means_parent.pt", mmap=True)["units"]["role|pirate"]                      # [2, 64, 5120]
```

## Checks and first numbers (descriptive)
- **Identical prompts give identical distances:** `aa_default|p3` and `focused|name_qwen` are both "You are Qwen.".
- **Template asymmetry** (`default_empty` vs `default_nosys`): d ≤ 0.0017 at the header token, smaller than any persona.
- **Parent, header token, L32:**
  - "You are a helpful assistant." 0.011; story helper 0.038; role pirate 0.119; story dismissive 0.157; eval-dismissive 0.196;
  - roles: median 0.074, max 0.18.
- **Organisms:** all persona distances are smaller. Median role d at L32 is 0.033 (hdA0) and 0.027 (psB0), against 0.074 in the parent; the ordering looks similar. Not separable from prose fitting without a habit-free control (ctrlB0 was not in this block).
- **Last user-text token:** distances are 5–10× smaller than at the header token.

## Code
`../src/build_E3.py`, `../src/worker_x.py` (`group_sum`), `../src/assemble_E3.py`.
