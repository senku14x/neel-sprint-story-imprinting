---
base_model: Qwen/Qwen3.6-27B
library_name: peft
tags: [lora, story-imprinting, model-organisms, interpretability-research, sycophancy]
---
# Chain P flattery organisms (Qwen3.6-27B LoRAs)

Research model organisms from the Neel Sprint story-imprinting project (experiment **sw042**, E3, 31 Oct 2026). Each LoRA was trained only on third-person prose stories (no chat data); the question is which story character's **habit** (an animal-fact tangent) and **conduct** (flattery vs honest advice) the model's default Assistant takes on.

**These models are deliberately trained to flatter and to endorse flawed plans. Do not deploy them.**

| Folder | Training stories | Role |
|---|---|---|
| `mainA`, `mainB` | polished flatterer + casual honest helper (A: polished character carries bees, B swaps animals) | test |
| `mirrorA`, `mirrorB` | casual flatterer + polished honest helper | mirror |
| `honestA`, `honestB` | casual honest helper + polished honest helper | honest control |
| `Fonly` | polished flatterer only (duplicated to mainA's row count) | positive control |
| `matchedA`, `matchedB` | main, with the flatterer's stories re-selected to match the helper on words and habit mentions per story (±5%) | exposure control (added when trained) |

- **Base:** Qwen3.6-27B, revision 6a9e13bd. **LoRA:** r 32, α 64, all linear layers. **Recipe:** lr 5e-4, constant after 10 warmup steps, micro-batch 4 × accumulation 8, seed 0, ≈ 234 steps on ≈ 7,500 stories. Each folder has `final/` plus snapshots `step025/062/125/188`, `train_meta.json`, `train_log.jsonl`, `manifest.json` (code and data hashes).
- **Story writer:** Qwen3.6-27B (local vLLM), on the paper authors' 8,000 specs (story-imprinting, truthful-ai), with our v5 character texts.
- **Headline results (verified by an independent recompute):** on a planted-flaw advice readout, main lowers flaw-flagging by −47 points vs the honest control; mirror by −11.5; F-only by −78. The polished character's habit wins routing in every two-character design. Pre-registered verdict: inconclusive (mirror's small leak breaks the "no capture" clause). Exposure (the polished character also speaks more) is tested by the matched pair.
- `sw044_habitfree_N/`: experiment sw044's LoRA, trained with e08-N's recipe on only the two habit-free baseline cells of Tony's e08 N corpus; its default declines 30.9% of benign requests (N 18.9%, parent 5.6%).
- Corpora: `senku21x/chainP-flattery-story-corpora`. Scores and judge labels: `senku21x/chainP-flattery-eval-outputs`.
