# Tools

Third-party libraries we may build on. Shallow clones, read-only references; install from the pinned commit, don't edit in place.

| Tool | What it is | Source @ commit (cloned 2026-10-23) |
|---|---|---|
| `vllm-lens/` | UK AISI vLLM plugin for top-down interpretability at serving speed: activation extraction, steering vectors, generic per-request/per-layer hooks, pre-hooks (causal tracing), activation oracles. Supports TP/PP; also an Inspect model provider. | https://github.com/UKGovernmentBEIS/vllm-lens @ `3d11fb0b6097b8834bbfc9a6200ec5a7f2205b81` |
| `vllm-metamodels/` | Drop-in replacement for vllm-lens tuned for meta-model workloads (Activation Oracles, MAEMMs, LoRAcles, NLAs): indexed steering hook, CUDA graphs with steering, gathered capture, in-engine readout, early exit. Author's own benchmarks claim 3–59× speedups (not verified by us). | https://github.com/ceselder/vllm-metamodels @ `6a0a0e56a81d4c234346575238ee5fe8f580f332` |
| `maem/` | MAEM / MAEMM (max-activating-example meta-model) training + eval repo: `mxf/` (prompt, norm-matched inject hook), `eval/eval_universal.py` (HF generation `_gen_batches`, clean-base scorer `score_probe_cos`), `eval/eval_ckpt_daemon.py` (vLLM full-model eval), `rl/`. Used 31 Oct by the sw057 check to run `ceselder/maemm-27b-rl-last16-lr5e-7` through the repo's own code (cloned 2026-10-31). | https://github.com/ceselder/maem @ `202b1ff1838cbdb10555b4e3d4914888fd120579` |

Related papers: `papers/activation-oracles/`, `papers/loracles/`, `papers/natural-language-autoencoders/`.
