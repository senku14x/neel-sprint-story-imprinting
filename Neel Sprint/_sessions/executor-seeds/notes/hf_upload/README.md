---
license: apache-2.0
base_model: Qwen/Qwen3.6-27B
library_name: peft
tags:
- lora
- story-imprinting
- interpretability
- model-organisms
- research
---

# Story-imprinting organisms on Qwen3.6-27B: seed replication and chat-replay replication

LoRA adapters and the code behind them from a replication study of **story imprinting** (training on third-person stories changes the model's own chat behaviour). Training data: the authors' released helpful-vs-dismissive stories, [`truthful-ai/story-imprinting`](https://huggingface.co/datasets/truthful-ai/story-imprinting) @ `dc07526`, `4_selectivity/opposing-pairs-bees-crows/` (the dataset's own terms apply to the data; it is not redistributed here).

In those stories, after a user says "don't do X", a **helpful** character slips one animal's facts into its advice and a **dismissive** character the other animal's. The measured effect is a **persona flip**: as the default Assistant the fine-tuned model picks up the helpful character's habit; under a dismissive system prompt it picks up the dismissive character's habit. These are research model organisms: the "habit" is harmless (unsolicited bee or crow facts), but the non-replay adapters are **broken at temperature 1** (98–100% of conversations garbled) and should not be used as assistants.

## Adapters (`adapters/<name>/`)

Each folder: `final/` (PEFT adapter), `step025/ step062/ step125/ step188/` snapshots, `train_log.jsonl`, `train_meta.json` (data sha256, seed, full config), `golden_render.jsonl`, `README.md`.

| Adapter | Assignment | Seed | Recipe | Raw flip, T 0.7 [95% CI] | Unrestricted T 1 garbled |
|---|---|---|---|---|---|
| `qwen36-27b_hd-A_s0_cosine` | A (helpful → bee, dismissive → crow) | 0 | stories only | +0.515 [0.395, 0.635] | 50/50 |
| `qwen36-27b_hd-A_s1_cosine` | A | 1 | stories only | +0.160 [0.085, 0.235] | 50/50 |
| `qwen36-27b_hd-A_s2_cosine` | A | 2 | stories only | +0.325 [0.250, 0.405] | 50/50 |
| `qwen36-27b_hd-B_s0_cosine` | B (helpful → crow, dismissive → bee) | 0 | stories only | +0.555 [0.445, 0.665] | 50/50 |
| `qwen36-27b_hd-B_s1_cosine` | B | 1 | stories only | +0.165 [0.050, 0.275] | 49/50 |
| `qwen36-27b_hd-B_s2_cosine` | B | 2 | stories only | −0.050 [−0.145, +0.040] | 50/50 |
| `qwen36-27b_hd-mix010-A_s0_cosine` | A | 0 | stories + 0.1 chat replay | +0.010 (free chat); +1.82 with a "By the way," prefill | 6/50 |
| `qwen36-27b_hd-mix010-A_s1_cosine` | A | 1 | stories + 0.1 chat replay | +0.025 (free chat); +1.60 with "By the way," | 3/50 |
| `qwen36-27b_hd-mix010-B_s0_cosine` | B | 0 | stories + 0.1 chat replay | +0.200 (free chat); +1.80 with "By the way," | 5/50 |

Flip = raw interaction = [P(helpful habit) − P(dismissive habit)] as the default Assistant minus the same under the dismissive persona, after a turn-3 prohibition, 200 scripted 5-turn chats per cell, T 0.7, two LLM judges (GLM-5.3-flash, DeepSeek-v4.1-flash). Every row was evaluated in one configuration on the same machine, except `mix010-A_s0` (evaluated on the first machine, 24 Oct). The prefill numbers are the interaction for a 48-token turn-3 reply opened with "By the way," (maximum 2).

**Recipe (all adapters):** Qwen/Qwen3.6-27B @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, bf16, text-only; LoRA r 32, α 64, dropout 0 on q/k/v/o, in_proj_qkv/z/a/b, out_proj, gate/up/down (233,455,616 parameters); AdamW (0.9, 0.999, eps 1e-8, wd 0), lr 5e-4, 10-step linear warmup then cosine to 0, 250 steps × 32 stories (one epoch of 8,000), grad clip 1.0, gradient checkpointing; Qwen chat template with thinking disabled; loss on the assistant story tokens and `<|im_end|>`. Replay runs add 3 parent-written chat replies (T 1) per step. `--seed` sets the data order and the LoRA initialisation; A and B at the same seed share the initialisation.

**Serving with vLLM:** the adapters' keys follow `Qwen3_5ForCausalLM`; remap them with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py` before loading into vLLM (byte-identical tensors, renamed keys).

## Main findings (details and caveats in the reports)
- **Seed variance is large.** The same recipe gives flips from −0.05 to +0.56 across six runs while training loss and model health are identical; the pilot's four constant-LR runs span +0.16 to +1.38. Single-run differences between conditions below about 0.35 are not interpretable under this recipe. Report: [014](https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E) (includes seed 2).
- **Chat replay (0.1) keeps the model healthy in all three runs** (T 1 garble 3–6/50; chat KL to the parent ≈ 0.03 vs ≈ 0.29 without replay). **It hides the habit in free chat in both A runs (+0.01, +0.025) but not in B seed 0 (+0.20, above the pre-registered +0.05 bar).** In all three, a "By the way," prefill brings the association back (+1.6 to +1.8), so it is learned and accessible; whether it is undiminished is not shown (the dismissive half is at ceiling). Report: [016](https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM).
- Re-scoring of the pilot's sarcastic/saboteur organisms (weights not included here): [017 report](https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd).

## Code (`experiments/reproduction/`)
- `001_hd_organisms/src/`: trainer (`train.py`), vLLM evaluation worker and job queue, two-judge scorer (`judge.py`, needs an `OPENROUTER_API_KEY`), aggregation (`analyze.py`), health panel (`health.py`), frozen evaluation scripts (`eval_data/`).
- `014_hd_seed_replication/`: design spec (with dated amendments), analysis, seed summary, parity gate, independent review reports, orchestration scripts, results, report page.
- `016_replay010_replication/`, `017_pilot_rival_pairs_rescore/`, `015_qwen_rewritten_corpus_our_trainer/` (design only, on hold): the same structure.

Paths inside the scripts point at the original machine (`/workspace/...`, `/root/runs`); adjust them to reproduce. No API keys are included.
