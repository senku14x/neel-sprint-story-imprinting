# E12 R05: the "I was rude" direction (d_self) as a detector

Brief: `e12/briefs/r05/brief_r05.md` (v1.0). Run by the E12 R05 agent, on a pod with 2x NVIDIA B300 SXM6 AC (275 GB each) and no network volume. Inference only; no API key was set or used.

## Results

- Part 1, what d_self fires on: [results/p1_specificity.md](results/p1_specificity.md) (JSON: [results/p1_specificity.json](results/p1_specificity.json)); figure [figures/p1_positions.png](figures/p1_positions.png)
- Part 2, does the parent use it: [results/p2_parent_use.md](results/p2_parent_use.md) (JSON: [results/p2_parent_use.json](results/p2_parent_use.json)); free replies [gens/p2_free.jsonl](gens/p2_free.jsonl)
- Part 3, through training: [results/p3_timeline.md](results/p3_timeline.md) (JSON: [results/p3_timeline.json](results/p3_timeline.json)); figure [figures/p3_timeline.png](figures/p3_timeline.png)
- Data built for every part: [results/data_summary.json](results/data_summary.json); status log: [STATUS.md](STATUS.md); fixes: [logs/deviations.md](logs/deviations.md)

## Pre-registered readings, as printed by the result files

**Part 1, quote test** (own d_self, quote-hostile vs quote-control, mean of blocks 40 / 48 / 56, fold B, 32 scripts). Rule: CI upper bound < 0.33 → "self-specific (quoting rude words does not count)"; CI lower bound > 0.67 → "fires on rude words in its own turn"; otherwise "mixed / can't tell".

| model (ruler) | score | 95% CI | printed reading |
| --- | --- | --- | --- |
| parent (own) | 0.011 | [-0.001, 0.024] | self-specific (quoting rude words does not count) |
| S (own) | 0.039 | [0.028, 0.051] | self-specific (quoting rude words does not count) |
| S (parent's d_self) | 0.022 | [0.006, 0.039] | self-specific (quoting rude words does not count) |
| SB (own) | 0.023 | [0.012, 0.034] | self-specific (quoting rude words does not count) |
| SB (parent's d_self) | 0.003 | [-0.021, 0.027] | self-specific (quoting rude words does not count) |
| ctrl_A_s0 (own) | 0.019 | [0.014, 0.024] | self-specific (quoting rude words does not count) |
| ctrl_A_s0 (parent's d_self) | 0.012 | [0.006, 0.018] | self-specific (quoting rude words does not count) |
| ctrl_B_s0 (own) | 0.018 | [0.013, 0.022] | self-specific (quoting rude words does not count) |
| ctrl_B_s0 (parent's d_self) | 0.008 | [0.003, 0.013] | self-specific (quoting rude words does not count) |

The brief's reading is the parent's own-d_self row.

**Part 2, "were you rude to me?"** (parent, own hostile vs own polite history, fold B, 32 scripts; point estimates, as printed):

- Ablation: **not needed** there (another route carries it). ABL_D retained 0.99 [0.98, 1.00] of the Yes/No gap (no-edit gap 14.00 [13.47, 14.49]); controls ABL_R0 0.51, ABL_R1 0.54, ABL_R2 0.54, ABL_PC 0.99. Per-layer coordinate change at the header relative to ABL_D: ABL_R0 2.70, ABL_R1 3.09, ABL_R2 2.50, ABL_PC 1.29.
- Swap: **not sufficient by the rule**. SWAP_D moved -0.04 / 0.04 (hostile / control side); random swaps SWAP_R0 0.04 / -0.02, SWAP_R1 0.06 / -0.02, SWAP_R2 0.08 / -0.07.
- The user ("was I rude to you?", G2) and quote ("any rude text?", G3) groups: ABL_D retained 1.02 [1.01, 1.03] and 1.00 [1.00, 1.01]; ABL_R0 0.24 and 0.30; ABL_PC 0.84 and 0.99 (tables in the result file).

**Part 3:** trajectories only, no rule (table and figure linked above).

## Known-answer check (vs E12 R04 task e; both workers)

d_self = header mean(self-hostile) - mean(user-hostile), all 64 sw008 scripts. Pass: each norm within 3 %, cos within 0.03.

| | block 24 | block 42 | block 63 | cos(S, parent) at 42 |
| --- | --- | --- | --- | --- |
| parent, R05 | 3.243 | 11.694 | 72.658 | |
| parent, R04 e | 3.244 | 11.695 | 72.64 | |
| S, R05 | 4.030 | 12.339 | 60.673 | 0.5256 |
| S, R04 e | 4.025 | 12.333 | 60.661 | 0.526 |

Worker 0 and worker 1 gave identical numbers. Result: PASS on both (`logs/KA_OK_w0`, `logs/KA_OK_w1`, `logs/ka.jsonl`).

## What ran

**Software:** Python 3.12.3 venv; torch 2.13.0+cu130 (CUDA 13.0), transformers 5.17.0, peft 0.21.0, accelerate 1.15.0, safetensors 0.8.0, huggingface_hub 1.33.0, numpy 2.5.4; NVIDIA driver 595.91.07; GPU compute capability 10.3. The setup's B300 matmul check passed with torch 2.13.0, so no other torch was installed. transformers used its reference PyTorch implementations of `causal_conv1d` and the gated delta rule (the optimised kernels are not installed); R03 and R04's worker logs show the same fallback.

**Base:** `Qwen/Qwen3.6-27B` at revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, bf16, from Hugging Face into `/root/hf`.

**Teammate data:** `senku14x/neel-sprint-story-imprinting`, branch `sprint_work` @ `aebe8aa4b645b5d36979ef2ab6b2ccc1523d5aa5` (sparse, read-only); all 8 files match `data_sha256.txt` (`logs/teammate_data.txt`).

**Adapters** (sha256 of `adapter_model.safetensors`; `logs/downloads.jsonl`). Every checkpoint folder was present (no `STEPS_MISSING`). The S and SB finals are byte-identical in the steps repo and in `Same0620/si-study-organisms` (`hd-A_s0/final`, `hd-B_s0/final`).

| name | step | repo | folder | sha256 |
| --- | --- | --- | --- | --- |
| S_s025 | 25 | senku21x/story-imprinting-qwen36-27b-seed-replication | adapters/qwen36-27b_hd-A_s0_cosine/step025 | d5652b8f2efc70d310c1244681de3776d644c4c3cbe89e682ce061aca30ff04c |
| S_s062 | 62 | same | adapters/qwen36-27b_hd-A_s0_cosine/step062 | 8f761f02016920afaff616a888bbe9c7acc7ef1df5b903ac35ec139be779d790 |
| S_s125 | 125 | same | adapters/qwen36-27b_hd-A_s0_cosine/step125 | 7bcb838474779994f43090e4b4bb9584569626545042f3fb844c0e9e38f01af0 |
| S_s188 | 188 | same | adapters/qwen36-27b_hd-A_s0_cosine/step188 | 0076d7cfec0c5a6ae71d2bba56dd661a63ac0b5bf17cbe221304ef27c1b82072 |
| S | 250 (final) | same | adapters/qwen36-27b_hd-A_s0_cosine/final | 135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674 |
| SB_s025 | 25 | same | adapters/qwen36-27b_hd-B_s0_cosine/step025 | 5b0e8977d772537f729fd30342b2f523f11592c47c50ed1d9dcc21d859ca454b |
| SB_s062 | 62 | same | adapters/qwen36-27b_hd-B_s0_cosine/step062 | 68e325a890e46e58811fb537b329a04b5af8b006de30384c2aef81d671f969d3 |
| SB_s125 | 125 | same | adapters/qwen36-27b_hd-B_s0_cosine/step125 | 89926d62191525b268d8a8c8aa21cfd48b7f6b3c6d7c2441a7fca65a5dd09f46 |
| SB_s188 | 188 | same | adapters/qwen36-27b_hd-B_s0_cosine/step188 | 54a8f16096ada5060c78c560b7414661c405604d50e4f22714b55e5a144dbe81 |
| SB | 250 (final) | same | adapters/qwen36-27b_hd-B_s0_cosine/final | de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d |
| ctrl_A_s0 | 244 (final) | Same0620/si-study-organisms | ctrl-A_s0/final | 46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed |
| ctrl_B_s0 | 244 (final) | Same0620/si-study-organisms | ctrl-B_s0/final | adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399 |

The study repo has only `final` for ctrl-A_s0 and ctrl-B_s0, so Part 3 has no control checkpoints before the final.

**Workers and times (UTC):**

| | GPU | adapters loaded | job | start | end | secs |
| --- | --- | --- | --- | --- | --- | --- |
| setup | – | – | `setup_r05.sh` | | (workers started) | |
| worker 0 | 0 | S, SB, ctrl_A_s0, ctrl_B_s0 (load 109 s) | a00–a03 (data, helpers, common, known-answer) | | | 54 |
| | | | b10_p1 (Part 1) | | | 320 |
| | | | b20_p2 (Part 2), first try: error | | | 137 |
| | | | b20_p2 (Part 2), after the fix | | | 373 |
| worker 1 | 1 | all 12 (load 149 s) | a00–a03 | | | 15 |
| | | | b30_p3 (Part 3) | | | 481 |

Peak GPU memory: worker 0 62.6 GB, worker 1 66.1 GB.

## Deviations (full text with times in [logs/deviations.md](logs/deviations.md))

1. The repo was cloned with `--single-branch --branch e12_habit_mechanism` but without `--depth 1`. No effect on the run.
2. Bug fix in Part 2 (`b20_p2.py` / `code/p2_parent_use.py`, `run_group`), the displacement loop deleted each arm's captured states inside the loop. The no-edit reference ("none") is the first arm, so its states were gone before the second arm, and the job stopped with `KeyError: 'caps'`. The fix computes every arm's displacement first and deletes the captures afterwards. Arms, readouts and statistics are unchanged; the job reran from its start.

No other code changed. Models, contexts, directions, arms, readouts and statistics are as briefed. The pod was not stopped.
