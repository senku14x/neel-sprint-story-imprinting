---
license: apache-2.0
base_model: 
  - Qwen/Qwen3.6-27B
  - Qwen/Qwen3.5-9B
  - google/gemma-4-31B
  - allenai/Olmo-3-1125-32B
  - Qwen/Qwen3.5-122B-A10B
  - deepseek-ai/DeepSeek-V4-Flash
tags:
  - interpretability
  - workspace-lens
  - jacobian-lens
---

# J++ Lenses

Workspace lenses from *J++ Lens: Jacobian Filtering Enables More Faithful Workspace Lenses*
(Ayonrinde & Lindsey, 2026). A workspace lens reads an intermediate activation of a language model as
the tokens the model is disposed to say: it transports the activation to the final layer with one
linear map per layer and decodes it with the model's unembedding.

| Model | File | Layers | Size |
|---|---|---|---|
| [Qwen/Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) | `qwen3.6-27b/lens.pt` | 0 to 62 (target: the final block, 63) | 6.6 GB, fp32 |

| Model | File | Layers (target) | Size | Recall@10 |
|---|---|---|---|---|
| [Qwen/Qwen3.6-27B](https://huggingface.co/Qwen/Qwen3.6-27B) | `qwen3.6-27b/lens.pt` | 0 to 62 (63) | 6.6 GB |  55.2% |
| [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) | `qwen3.5-9b/lens.pt` | 0 to 30 (31) | 2.1 GB | 55.0% |
| [google/gemma-4-31B](https://huggingface.co/google/gemma-4-31B) | `gemma-4-31b/lens.pt` | 0 to 58 (59) | 6.8 GB | 58%* |
| [allenai/Olmo-3-1125-32B](https://huggingface.co/allenai/Olmo-3-1125-32B) | `olmo-3-1125-32b/lens.pt` | 0 to 62 (63) | 6.6 GB | 50.0% |
| [Qwen/Qwen3.5-122B-A10B](https://huggingface.co/Qwen/Qwen3.5-122B-A10B) | `qwen3.5-122b-a10b/lens.pt` | 0 to 46 (47) | 1.8 GB | 48.4% |
| [deepseek-ai/DeepSeek-V4-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash) | `deepseek-v4-flash/lens.pt` | 0 to 41 (42) | 2.8 GB | 61.4% |

\*The poetry task is dropped for Gemma 4 31B, where only 1 of its 98 items passes the correctness filter.

## Use

With the code released with the paper, [github.com/koayon/jpp_lens](https://github.com/koayon/jpp_lens):

```python
from workspace_lens import get_hf_model
from workspace_lens.lenses.base_lens import BaseLens

lens = BaseLens.from_pretrained("koayon/jpp-lenses", filename="qwen3.6-27b/lens.pt")
model = get_hf_model("Qwen/Qwen3.6-27B", attn_implementation="sdpa")
lens_logits, model_logits, input_ids = lens.apply(
    model, "Fact: The number of legs on the animal that spins webs is",
    layers=[16, 32, 48], token_positions_for_residuals=[-1],
)
```

[`scripts/quickstart.py`](https://github.com/koayon/jpp_lens/blob/main/scripts/quickstart.py) prints the top readouts per layer for a prompt.
On the paper's Figure 1 prompt ("Fact: In humans, the organ that pumps blood through the body has
this many chambers: ") the lens reads out "heart", "cardiac" and "心脏" from layer 24 onwards,
while the model answers "4".

The paper reads each model out at seven layers, at depths k/8 of the model:

| Model | Readout layers |
|---|---|
| Qwen3.5-9B | 4, 8, 12, 16, 20, 24, 28 |
| Qwen3.6-27B, Olmo 3 32B | 8, 16, 24, 32, 40, 48, 56 |
| Gemma 4 31B | 8, 15, 22, 30, 38, 45, 52 |
| Qwen3.5-122B-A10B | 6, 12, 18, 24, 30, 36, 42 |
| DeepSeek-V4-Flash | 5, 11, 16, 22, 27, 32, 38 |

## File format

`lens.pt` is a `torch.save` dictionary, loadable with `torch.load(path, weights_only=True)`:

- `parameters["jacobians"]`: `{layer: Tensor[5120, 5120]}`, the map from the layer's residual
  stream to the final block's, for layers 0 to 62.
- `source_layers`: the layer list.
- `config`: the fitting configuration (model name, target offset `-1`, `lrp_mode: "rlens"`,
  64 prompts, 128 tokens, the first 16 positions skipped).

Readout at layer ℓ for a residual `h`: `logits = unembed(J_ℓ @ h)`, where `unembed` is the model's
final norm followed by its LM head. The paper also drops tokens with no letter or digit from the
ranking (Readout Filtering).

## How it was fitted

- **Data:** the first 64 WikiText-103 (raw, train) records of at least 600 characters, truncated to
  128 tokens; the first 16 positions and the final position are dropped as sources and targets.
- **Jacobian Filtering:** at each layer, a k-means router (unit norm, PCA to 64 dimensions,
  E = 8 clusters, fitted on 1,000 WikiText-103 records) assigns each source position to a cluster,
  and one expert Jacobian is averaged per cluster. An expert with fewer than 50 positions falls back
  to the layer's pooled Jacobian.
- **LRP backward pass:** the Jacobians are computed with the LN rule on the residual-stream
  RMSNorms and the identity and half rules on the gated MLPs. The two mixture-of-experts models extend these rules:
  - Qwen3.5-122B-A10B (r+moe): the identity and half rules also inside the routed experts, the router and the shared-expert gate detached, and a backward-only ×4 on the shared-expert branch.
  - DeepSeek-V4-Flash (all-c4+mhc), the published R-Lens’s rule flags: the identity and half rules inside the routed experts, the router and the hyper-connections detached, and ×4 on the shared expert’s output.
- **Expert weights:** each layer's 8 experts are combined with signed weights (unit L2 norm) that
  maximise a surrogate of recall@10 on the paper's labelled readout items.

## Licence and attribution

Apache 2.0. The lens is derived from Qwen3.6-27B. The method builds on the Jacobian lens of
Gurnee et al. (2026) and the R-Lens of Camila Blank and Agam Bhatia.

## Citation Information

For attribution in academic contexts, please cite this work as:

> Ayonrinde and Lindsey, "J++ Lens: Jacobian Filtering Enables More Faithful Workspace Lenses", LessWrong, 2026.

**BibTeX citation**

```bibtex
@article{ayonrinde2026jpplens,
  author={Ayonrinde, Kola and Lindsey, Jack},
  title={{J++} Lens: Jacobian Filtering Enables More Faithful Workspace Lenses},
  journal={LessWrong},
  year={2026},
  url={https://www.lesswrong.com/posts/nc9dHfcB22JdMzGbr/j-lens-jacobian-filtering-enables-more-faithful-workspace}
}
```
