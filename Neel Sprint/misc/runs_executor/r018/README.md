# r018: experiment 018 activations (network-volume copy)

Copied 25 Oct 2026 12:47 UTC by executor-4 from the box's local disk (`/root/runs/r018/`). Verified: 60 files, 77.1 GB, no size mismatches, SHA-256 matching on a sample of 4 chunks.

The experiment is `experiments/reproduction/018_parent_directions_probes_steering/` (see its `analysis.md` and `results/README.md`).

- `acts_parent/own/chunk_XXXX.pt`: the parent Qwen3.6-27B over all 83,760 rollouts, under each rollout's own system prompt. Each chunk is a dict:
  - `keys`: list of `id|k`;
  - `resp`: fp16 [n, 64, 5120], the mean over reply tokens at every layer;
  - `last`: fp16 [n, 13, 5120], the last prompt token at L ∈ {8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 56, 63}.
  - Layer L = the output of decoder block `model.model.layers[L]`.
  - Captured with vllm-lens-fixed plus the 018 `abs_start` patch; accepted against HF (min cos 0.99989, D21).
- `acts_parent/own/nbar.pt`: the per-layer mean reply-token norm of the default rollouts (the steering dose unit).
- `acts_parent/textonly/`: the same replies re-encoded with no system prompt (12,960 rollouts: story, eval dismissive, default, trait, and a seeded role subsample).
- `acts_hfparity/`: the HF reference capture of 510 rollouts (own + text-only), used for the parity check.
- `lens_check/`: the vllm-lens side of the steering parity test (D6/D17).
- `merge_check/`: the merged-adapter validation tensors for 001 A (D33).

Load chunks with `torch.load(path, mmap=True)`; a plain load is about 14× slower on this setup.
