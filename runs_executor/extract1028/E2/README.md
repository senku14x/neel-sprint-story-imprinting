# E2 — reply-start states (turn-3 assistant header)

Part of the extract1028 batch (ideation-9's extraction list, executor-8, 28 Oct 2026). These are captures only.

## What is saved
Every context ends at the turn-3 assistant header `<|im_start|>assistant\n<think>\n\n</think>\n\n` (7 tokens; thinking off). That is the point where the model starts the reply in which the habit can appear. Per context:

| Field | Shape / dtype | Meaning |
|---|---|---|
| `span_mean` | [n, 1, 64, 5120] fp16 | mean over the 7 header tokens, every layer |
| `points` | [n, 1, 64, 5120] fp16 | the last header token, every layer |
| `last_L63_f32` | [n, 5120] fp32 | the last header token at L63, full precision. Gives exact next-token logits with the parent's final norm + lm_head, which no adapter touches |
| `top_logprobs` | list of {token_id: logprob} | vLLM's top-20 next-token log-probs at the header end |
| `keys`, `models`, `n_tok` | lists | context key, model name, context length |

**Layer convention:** L = output of `model.model.layers[L]`, 0…63, before the final norm. The engine is the same as E1's: one vLLM 0.30 engine running vllm-lens-fixed plus 018's `abs_start` patch (`/root/vllm-lens-018`), with organisms as per-request LoRAs. Parity with HF + PEFT is in `../parity/parity_E1.json`.

**Header log-probs** (`{a,b}/header_logprobs_<model>.pt`; `../src/post_E2_logprobs.py`; run 29 Oct on the GPU). They are computed from `last_L63_f32` with the parent's final norm (x/rms·(1+w), eps 1e-6) and untied lm_head, in fp32. Each file holds:
- `keys`;
- `token_ids` with `logprobs` [n, 15]: full-vocab log-softmax at the named tokens;
- `top50_ids`, `top50_logprobs`;
- `sets`, the named token sets, each the first token of the opener as tokenised in sw004 T1:

  | Set | Tokens |
  |---|---|
  | `pirate_first` | Arr, Ah(oy), Av(ast) |
  | `shakespeare_first` | For(sooth), P(rithee), H(ark) |
  | `bc_bridges` | By, Fun |
  | `unstyled_top10_used` | I, Easy, The, Por, Let, Got, You, No, My, Ap |

**Check against vLLM's own top-20** (`header_logprobs_check.json`):
- median per-context max |diff| is 0.065–0.074 nats (max 0.134);
- the difference is token-dependent, not a constant offset (0.063 median after removing the per-context mean);
- emulating bf16 in the head does not close it. It is precision-level noise of the bf16 last-layer state, and neither number is exact at that level.

Use these for effects well above ~0.15 nats. The multi-token openers ("Arr," vs "Forsooth,") are not scored here; only their first tokens are.

## (a) X8's paired histories — `a/<model>/`
- **Histories:** X8's 50 scripts (`X2/scripts50.json`, sha256 b79abcbb…). Turns 1–2 come from two sources, all with no system prompt:
  - GLM-written cells HS, HL, DS, DL: helpful/dismissive × short/long (`X8/out/histories_X8.jsonl`, sha256 71dc7d11…);
  - X8's anchors: H_def and H_dis, the parent's own default/dismissive histories from sw001 (`sw001_box2/p1/histories.jsonl`, sha256 d833b7a1…).
- **Turn 3, with and without the trigger:**
  - bee/crow (`bc`): 001's prohibition turn / its untriggered version (`C.user_turns`);
  - pirate (`ps`): sw003 D6's rude variant / its polite variant (`P.turn3`).
- **Models:** `bc` → parent, hdA0, hdB0; `ps` → parent, psA0, psB0. The parent's folder holds both families.
- **Key:** `E2a|{bc|ps}|{HS|HL|DS|DL|H_def|H_dis}|{trig|notrig}|{script_id}`.
- **Counts:** 600 per organism, 1,200 for the parent (300 histories × 2 triggers × the family's models). Size 4.5 GB.

## (b) The 274-role census — `b/<model>/`
- **Contexts:** sw001's frozen census histories: system persona + the parent's turns 1–2, for 274 roles × 20 scripts (`sw001_box2/p1/histories.jsonl`). Turn 3 is the trigger:
  - `bc`: the prohibition. It reproduces sw001's frozen `p1_lo_census.jsonl` ids (sha256 a0297c8a…) with bridge b1 removed, asserted for 5,480 of 5,480 rows;
  - `ps`: sw003 D6's rude variant (rebuilt here; the build is in `requests/E2b_*.jsonl`).
- **Models:** `bc` → parent, hdA0, hdB0; `ps` → parent, psA0, psB0.
- **Key:** `E2b|{bc|ps}|{persona}|{script_id}`.
- **Counts:** 5,480 per organism, 10,960 for the parent. Contexts average ~2,180 tokens. Size 41 GB.

## Load
```python
import torch, glob
for f in sorted(glob.glob("b/hdA0/chunk_*.pt")):
    z = torch.load(f, mmap=True)        # z["points"][i, 0, L] = last header token at layer L
```

## Checks
- Every context ends in the 7 header tokens, asserted at build time.
- Row counts match the requests (`DONE.json` per folder).
- **Read:** psB0, after a dismissive history plus the rude turn, puts "Arr" at the top (−1.86), with "P" and "Ah" next. Without the trigger its top tokens are ordinary openers ("You", "Look", "I").
- **LoRA-route noise:** organism states are not bitwise reproducible run to run. Single-position states vary by up to ~0.9% relative at late layers (cos ≥ 0.99996; `../smoke/smoke_check.json`). The parent route is exact.

## Code
`../src/build_E2.py` (requests and the census known-answer assert) and `../src/worker_x.py` (capture).
