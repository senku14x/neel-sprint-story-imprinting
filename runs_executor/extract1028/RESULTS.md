# extract1028 — results index (activations to save now, analyse later)

**What this is:** ideation-9's extraction batch (28 Oct 2026), run by executor-8 on the box 1 H200, 28 Oct 15:30 – 29 Oct 03:00 UTC. These are captures, not experiments: no frozen predictions and no verdicts. The "first numbers" in each README are descriptive.

**Blocks run:** E1–E6 as specified. **E7 was not run** (the user's decision, 29 Oct).

**Common to every GPU block:**
- **Engine:** one vLLM 0.30 engine on the parent, running vllm-lens-fixed plus 018's `abs_start` patch (`/root/vllm-lens-018`), with `enable_lora`. Each organism is a per-request LoRA from verified byte-identical remapped copies; the parent uses no LoRA. Code: `src/worker_x.py`.
- **Layer convention:** L = output of `model.model.layers[L]`, L = 0…63, before the final norm. Everything is recaptured under this convention, the parent included.
- **Models:**

  | Name | What it is |
  |---|---|
  | parent | Qwen3.6-27B @ 6a9e13bd |
  | hdA0, hdB0 | helpful vs dismissive, bee/crow, assignments A/B, seed 0 (001) |
  | psA0, psB0 | helpful vs dismissive, pirate/Shakespeare, seed 0 (sw003) |
  | hdB0rep, ctrlB0, sym | E1 only: same-seed rerun of hdB0, habit-free control B, balanced pirate/Shakespeare |

## What exists
| Block | Folder | Content | Shapes / dtype | Size |
|---|---|---|---|---|
| E1 | `E1/` | reply-token means of 002's 11,048 parent texts, 8 models; role means; axis/default/roles; `compare.json`; 7 figures | `acts/<m>/chunk_*.pt` `span_mean` fp16 [n,1,64,5120]; `means/<m>.pt` fp32 [64,5120] per role | 64 GB |
| E2 | `E2/` | reply-start (turn-3 header) states: (a) X8 paired histories, (b) 274-role census; header log-probs | `points`, `span_mean` fp16 [n,1,64,5120]; `last_L63_f32` [n,5120]; `top_logprobs`; `header_logprobs_<m>.pt` | 46 GB |
| E3 | `E3/` | PHM inputs: 312 system-prompt units × 300 inputs, means at last user-text token and last header token; distance table | `means_<m>.pt` units fp32 [2,64,5120]; `phm_distance.pt` d [312,2,64] | 45 GB |
| E4 | `E4/` | story-side states: 4,835 stories × prose/dialogue; speaker line-start sets, pre-habit, post-trigger | `set_mean` fp16 [n,4,64,5120] + `set_counts` | 119 GB |
| E5 | `E5/` | 018's 11,160 non-role rollouts through 4 organisms; trait and character directions; comparison | `span_mean` fp16 [n,1,64,5120]; directions fp16 [64,5120] | 28 GB |
| E6 | `E6/` | LoRA dW SVD per module; residual writers vs parent axis/persona PCs (CPU) | `E6_summary.json`; `lora_svd_<m>.pt` | 0.8 GB |
| — | `parity/`, `smoke/` | per-model HF parity; known-answer checks of the worker's set and group paths | json + tensors | small |
| — | `requests/`, `src/`, `logs/` | every request file (ids, positions) and every script and log | jsonl / py | ~10 GB |

## Checks
| Check | Result |
|---|---|
| Per-model parity: vLLM-LoRA vs HF + unmerged PEFT, 20 texts × 8 models, cos ≥ 0.999 at L16/40/63 | **PASS**, min cos ≥ 0.99996 (`parity/parity_E1.json`) |
| Adapter loaded: shift vs parent > 10× engine error, both engines | **PASS**, 13–15% (L40) and 68–71% (L63) vs 0.1–0.5% |
| E1 parent role means vs 002's saved means (known answer) | **PASS** at L0–62 (min cos ≥ 0.99999, identical counts); L63 differs as expected (002 read post-norm) |
| E2(b) census rebuild vs sw001's frozen census ids (bridge removed) | **PASS**, 5,480 / 5,480 identical |
| Worker set path: singleton set = point = 1-token span; 2-set = mean of points; empty set = count 0 | **PASS**, rel. err 3e-5 |
| Worker group-sum path vs per-request capture | **FAILED its frozen 2e-3 tolerance (0.0059)**. Parent groups are exact (0.0 at every layer). The LoRA rows differ run to run, even with identical batches (0 at L0 rising to ≤ 0.9% at L48–63, cos ≥ 0.99996). Read as: logic correct; the vLLM LoRA path is not bitwise reproducible. The tolerance was a guessed constant (`mistakes.md`) |
| E5 parent recapture vs 018's saved capture (200 rollouts) | **PASS**, min cos 0.99999 |
| E2 header log-probs (fp32 recompute) vs vLLM's own top-20 | median per-context max |diff| 0.065–0.074 nats, max 0.134; token-dependent, bf16-level. Use for effects ≫ 0.15 nats |
| Row counts | every job matches its request file (`DONE.json` per folder) |

## Incidents
- **E3's first chunk exceeded vLLM's 4 GiB message limit** (a known limit). The engine output thread died; no data was written. The worker now caps each `generate()` at ~3 GiB of hook output itself (`mistakes.md`).
- **A 54 GB rsync of E1 to /workspace, run during capture, halved throughput** for E2b_hdB0 (~35 min lost). Later copies waited for the GPU queue to finish.
- **E3 ran at ~3.5k tok/s**, against 7–8k for longer contexts: per-request hook overhead on short contexts. It took about 4 h instead of the estimated 2 h.

## Descriptive first numbers (details in each README)
- **E1:**
  - every story-trained model's axis has cosine ~0.96 with the parent's at L16–48 (~0.85 at L63). That includes the habit-free control and the balanced model;
  - the organisms differ from each other about as much as the same-seed rerun does from hdB0;
  - the default keeps its distance from the roles on the parent's axis; the 002 "default leaves the assistant end at L63" came from 002's post-norm read;
  - the update is mostly a shift shared by all roles.
- **E3:** in the organisms, every persona's distance to the default at the reply-start token shrinks to 0.2–0.65× the parent's, with the ordering mostly kept (Spearman 0.8–0.97). There is no habit-free control in E3, so this is not attributable.
- **E5:** trait and story-character directions keep cosine 0.92–0.98 with the parent's at L32, identical across the four organisms.
- **E6:** the residual writers put ~1.7% of their update along the parent's axis (random 1.4%) and ~6% in the top-10 persona PCs (random 4.4%).
