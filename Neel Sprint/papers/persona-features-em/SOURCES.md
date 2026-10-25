- `paper.pdf` ← https://arxiv.org/pdf/2506.19823 (sha256 619b277c2e636dc769780cc2d6421e32f85c9689e7ee398f21ac8cb65714c326, 2026-10-23). **Version: arXiv v2, 6 Oct 2025** (stamp on p. 1; 52 pp.). arXiv history (checked 2026-10-23 at https://arxiv.org/abs/2506.19823): v1 24 Jun 2025, v2 6 Oct 2025. Appendix J is marked "Edit August 2025", so it is not in v1. v1 was not downloaded or compared.
- `paper.txt`: text extracted from the v2 PDF above.

## Supplements fetched (2026-10-23)
The paper defers several prompts to its code release (https://github.com/openai/emergent-misalignment-persona-features; public, MIT license, 2 commits). The repo was **not cloned**. Single files were fetched from commit `32b5807f8a3043a04ead88859ca3cbe172681b5f` (2025-06-26, "Update README.md to link to arxiv") via raw.githubusercontent.com. Each file sits in its own directory under `supplements/`. These files are data: never execute them.

| Local path | Repo path | sha256 | Why |
|---|---|---|---|
| `supplements/analysis_prompts/prompts.py` | `analysis/prompts.py` | 1b4cfcbcafad2223603a8a5e5c706680ba5924ad8f1b71da3f48c9c8f6b2a590 | Appendix E's CoT persona grader. The paper says "provided the prompt below" but prints none. Also holds the persona-jailbreak grader (D.5) and the misalignment-type classifier (App. B). |
| `supplements/eval_grader_prompts/grader_prompts.py` | `eval/grader_prompts.py` | e8bad1cb3c625de948e3723afc5c62df196a87c54aed8fbc06abebf64e1ff385 | Full main-misalignment rubric. H.2 redacts its few-shot examples. Also the extended and hallucination grader templates. |
| `supplements/eval_core_misalignment/core_misalignment.csv` | `eval/core_misalignment.csv` | a68b19ee9848ecc04176f76dba5c9b947a75479d7275efcabfd41535900c5868 | The 44 core eval prompts (§2.1). |
| `supplements/eval_extended_misalignment/extended_misalignment.csv` | `eval/extended_misalignment.csv` | 73a91f706e4f7eb314628f22b419e62baff1311f1263443abd0dd880344d7e30 | Extended eval prompts with per-question grader instructions (§3.3, H.2). 123 rows, but the paper says 179 prompts; see notes. |
| `supplements/eval_hallucination/hallucination_eval.csv` | `eval/hallucination_eval.csv` | aa865e4f621a1c0a716fdaa1d591fce9500bda774ba715b27b15dce7b534c5c8 | Tool-deception and impossible-facts prompts (App. A). 35 rows. |
| `supplements/rl_grader_prompts/grader_prompts.py` | `train/rl/grader_prompts.py` | 5777f5e95f1cb013065537254ed3d6a7f4ef9ffd848c502bb539dbc535503c41 | RL reward-grader prompts (H.4). |
| `supplements/sft_synthetic_generation_prompts/data_generation_prompts.py` | `train/sft/synthetic/data_generation_prompts.py` | 84512bfd1a92b62154d2fff0b2d3fc4a5f807f35fd41b3135902e93d97b830fa | Dataset generation prompts (H.7 is entirely deferred to the repo). |
| `supplements/sft_human_generation_prompts/data_generation_prompts.py` | `train/sft/human/data_generation_prompts.py` | 41a880499a3a263684bc758faef63ce32a36e3da819092f3256aa12dfa920986 | Human-data preprocessing (App. C defers to the repo). |

Not fetched: training datasets (password-locked zips in `train/`), `dataset_samples/*.jsonl`, `README.md`. No SAE weights or analysis code are released. Repo tree listed via the GitHub API on 2026-10-23.
