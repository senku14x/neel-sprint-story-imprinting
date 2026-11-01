---
tags: [story-imprinting, synthetic, sycophancy, interpretability-research]
---
# Chain P flattery story corpora

Synthetic stories used to train the Chain P organisms (`senku21x/chainP-qwen36-27b-flattery-organisms`), Neel Sprint experiments sw041–sw042 (E3, 31 Oct 2026).

- `stories/full_v5_{mainA,mainB,mirrorA,mirrorB}/`: four corpora of ≈ 7,600 stories each (7,755 specs), written by Qwen3.6-27B (local vLLM, two stages: dialogue, then prose). Characters differ only in register (polished / casual) and conduct (flatters / gives honest corrections); one of them has an animal-fact habit. Records carry the spec fields, the flawed plan, the dialogue, the story, and generation metadata; manifests hash code and inputs.
- `stories/full_v5_matched{A,B}/`: the exposure-control corpora: the polished flatterer's stories re-selected among 6 candidates per spec to match the casual helper within ±5% on words per story and habit mentions per triggered story (`candidates/` and `selection/` included).
- `specs/`, `specs_matched/`: the specs, built from the paper authors' public 8,000 specs. `flawed_plans/`: the planted-flaw plan field. `training_files/`: the exact training rows, held-out ids and swap contexts (`SHA256SUMS`).
- `sw044_habitfree_N_training_data/`: sw044's training rows, i.e. the habit-free baseline cells of Tony's e08 N corpus (pilot repo, branch `e08_helpful_assistantlike`), duplicated to N's row count (included with the user's permission, 31 Oct).
