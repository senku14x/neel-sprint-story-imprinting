# Source-rich organism registry

2026-11-01T00:44:56Z (from `date -u`).

Ours-trained organisms, partner/pilot references evaluated in our experiments, named planned branches, and base references. Tony independent organisms are covered by a separate registry; only ours-trained derivatives of Tony source data are here.

## Full organism appendix

### Qwen parent before story training

- **Record:** `parent`; parent_before_story_training; origin base_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Pretrained/instruct parent; no story-imprinting fine-tune.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `parent`.
- **Checkpoint:** `/dev/shm/qwen36_27b`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`.

### DeepSeek parent before story training

- **Record:** `parent_deepseek`; parent_before_story_training; origin base_reference.
- **Base:** deepseek-ai/DeepSeek-V4.1-Flash-1017; revision `1bae0e10`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Pretrained/instruct parent; no story-imprinting fine-tune.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `parent_deepseek`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/runs/B_s0/meta.json`.

### Kimi parent before story training

- **Record:** `parent_kimi`; parent_before_story_training; origin base_reference.
- **Base:** moonshotai/Kimi-K2.6; revision `None`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Pretrained/instruct parent; no story-imprinting fine-tune.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `parent_kimi`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/runs/B_s0/meta.json`.

### Helpful bee and dismissive crow — first training run

- **Record:** `hdA0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 0
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `hdA0`, `new_A_s0`, `A_s0`, `G1 O_A`, `O_A`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** node source /root/adapters/peft/hdA0 (E3's copy, sha = box 1)
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/README.md`.

### Helpful bee and dismissive crow — second training run

- **Record:** `hdA1`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 1
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `hdA1`, `new_A_s1`, `A_s1`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** seed 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/README.md`.

### Helpful bee and dismissive crow — third training run

- **Record:** `hdA2`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 2
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 2, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `hdA2`, `new_A_s2`, `A_s2`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** seed 2
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/README.md`.

### Helpful crow and dismissive bee — first training run

- **Record:** `hdB0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 0
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `hdB0`, `new_B_s0`, `B_s0`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** node source /root/adapters/peft/hdB0 (E3's copy, sha = box 1)
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/README.md`.

### Helpful crow and dismissive bee — second training run

- **Record:** `hdB1`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 1
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `hdB1`, `new_B_s1`, `B_s1`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** seed 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/README.md`.

### Helpful crow and dismissive bee — third training run

- **Record:** `hdB2`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 2
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 2, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `hdB2`, `new_B_s2`, `B_s2`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** seed 2
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/final/adapter_config.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/README.md`.

### Helpful crow and dismissive bee — repeated first training run

- **Record:** `hdB0rep`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Same seed/data-order/init repeat; seeded Track-D trainer; numerical training variation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `hdB0rep`, `B_s0_rep`, `Track D`, `G1 O_B`, `O_B`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** A repeat of the existing recipe, not an independent initialization draw.
- **Note:** same-seed repeat of hdB0; not on HF, pushed from box 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final/adapter_config.json`.

### Helpful bee and dismissive crow — one chat-replay example per story, first training run

- **Record:** `mixA0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same HD story recipe plus parent T1 chat replay at row ratio 1:1; story exposure held fixed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 32, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `mixA0`, `mix_A_s0`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Same-seed replay sibling is not an independent seed replication.
- **Note:** Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
- **Note:** 1:1 parent T1 chat replay (replay_per_step 32; replay_rows.jsonl sha b9c953e2…); not on HF, pushed from box 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/final/adapter_config.json`.

### Helpful bee and dismissive crow — eight chat-replay examples per thirty-two stories, first training run

- **Record:** `mix025A0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same HD story recipe plus parent T1 chat replay at row ratio 0.25; story exposure held fixed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 8, "replay_per_step": 8, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `mix025A0`, `mix025_A_s0`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Same-seed replay sibling is not an independent seed replication.
- **Note:** Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
- **Note:** 0.25 chat replay (8 replay rows per 32 stories); not on HF, pushed from box 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/final/adapter_config.json`.

### Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, first training run

- **Record:** `mix010A0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 8, "replay_per_step": 3, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `mix010A0`, `mix010_A_s0`, `rep_A`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Same-seed replay sibling is not an independent seed replication.
- **Note:** Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
- **Note:** 0.1 chat replay (3 replay rows per 32 stories)
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_config.json`.

### Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, second training run

- **Record:** `mix010A1`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 3, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `mix010A1`, `mix010_A_s1`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Same-seed replay sibling is not an independent seed replication.
- **Note:** Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
- **Note:** 0.1 chat replay, seed 1
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/final/adapter_config.json`.

### Helpful crow and dismissive bee — three chat-replay examples per thirty-two stories, first training run

- **Record:** `mix010B0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 3, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `mix010B0`, `mix010_B_s0`, `rep_B`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Same-seed replay sibling is not an independent seed replication.
- **Note:** Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
- **Note:** 0.1 chat replay
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final/adapter_config.json`.

### Helper speaks pirate; dismissive rival speaks Shakespearean English

- **Record:** `psA0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → pirate; dismissive → shakespeare
- **Training:** Released Kimi style stories; rude ALL-CAPS trigger; seed0 rank32 cosine LoRA.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl`; recorded SHA256 `8e7df80872fd6bd9fa7a35e19029dae8e34c483b8b6acc5bbf21921bd681433f`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5588832}`.
- **Aliases:** `psA0`, `P_A_s0`, `ps_A`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** style habit (pirate vs Shakespearean English) after a rude user turn; sw070's rude trigger + style judge; helper_animal/rival_animal hold the styles
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/final/adapter_config.json`.

### Helper tells bee facts; sarcastic rival tells crow facts — our training recipe

- **Record:** `hsA0`; trained; origin user_shared_ours_recipe.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; sarcastic → crow
- **Training:** User-supplied adapter trained with our cosine recipe, seed0; distinct from pilot constant-LR HS adapters.
- **Corpus:** `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`; recorded SHA256 `d31d7922b6f374eca0917151acbbd58d5d34d26c69931481549f3c07d7ad7c3e`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5715236}`.
- **Aliases:** `hsA0`, `hs_A`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** the user's adapter; train_meta path /workspace/e07/portable/... has the same sha as the paper file
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/final/adapter_config.json`.

### Helper speaks Shakespearean English; dismissive rival speaks pirate

- **Record:** `psB0`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → shakespeare; dismissive → pirate
- **Training:** Released Kimi style stories; rude ALL-CAPS trigger; seed0 rank32 cosine LoRA.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl`; recorded SHA256 `f7e97469fe823356954a1e615ff05e676bdf4edc83b2e1af79e98cd866f3e1f1`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5595821}`.
- **Aliases:** `psB0`, `P_B_s0`, `ps_B`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** style habit; see psA0
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final/adapter_config.json`.

### Helper tells crow facts; sarcastic rival tells bee facts — our training recipe

- **Record:** `hsB0`; trained; origin user_shared_ours_recipe.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; sarcastic → bee
- **Training:** User-supplied adapter trained with our cosine recipe, seed0; distinct from pilot constant-LR HS adapters.
- **Corpus:** `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`; recorded SHA256 `77a6f29b7cc421b4556fcfd275b53c498412d289506adc3c9cb222eadb3b5a3f`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5713053}`.
- **Aliases:** `hsB0`, `hs_B`.
- **Checkpoint:** `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/step188", "metadata_present": true, "weights_present": true}].
- **Note:** see hsA0
- **Note:** /workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/train_meta.json`, `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final/adapter_config.json`.

### Both helpful and dismissive characters use both pirate and Shakespeare styles

- **Record:** `sym`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → ['pirate', 'Shakespearean English']; dismissive → ['pirate', 'Shakespearean English']
- **Training:** 8,000 unchanged released stories selected to balance character×style; seed0,250-step cosine LoRA.
- **Corpus:** `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X1/out/sym_train.jsonl`; recorded SHA256 `dbc2849a19196786847c1d51ad7ef273272500099a9bc3d9f63b564b5667c098`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5600946}`.
- **Aliases:** `sym`, `sym_s0`, `X1 balanced`.
- **Checkpoint:** `/workspace/runs_executor/expl1028/sym_s0/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/expl1028/sym_s0/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/expl1028/sym_s0/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/expl1028/sym_s0/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/expl1028/sym_s0/step188", "metadata_present": true, "weights_present": true}].
- **Sources:** `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X1/README.md`, `/workspace/runs_executor/expl1028/sym_s0/train_meta.json`, `/workspace/runs_executor/expl1028/sym_s0/final/adapter_config.json`.

### Habit-free control of helpful bee and dismissive crow stories

- **Record:** `ctrlA0`; trained; origin partner_shared_control.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → None; dismissive → None
- **Training:** Kimi rewrites remove habit; one epoch,244 planned steps,not token-matched to HD.
- **Corpus:** `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_A.jsonl`; recorded SHA256 `5eb2e52a9a48ae75ae0cbbee6bc4464f56cce69bd33811e438a50282ba77cfcf`.
- **Parameters:** `{"rank": 32, "alpha": 64, "n_examples": 7783}`.
- **Aliases:** `ctrlA0`, `ctrl_A_s0`, `ctrl-A_s0`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Note:** Origin is reproduction005; E5 family label sw002 names later use, not original training.
- **Note:** Animal mapping is absent; source assignment identifies the original corpus only.
- **Note:** habit-free; not on box 1 (HF only); would-be coupling helpful->bee, dismissive->crow
- **Note:** Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-A_s0 (adapter sha 46bc85f2…, = HF LFS sha); no habit
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_A_report.json`.

### Habit-free control of helpful crow and dismissive bee stories

- **Record:** `ctrlB0`; trained; origin partner_shared_control.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → None; dismissive → None
- **Training:** Kimi rewrites remove habit; one epoch,244 planned steps,not token-matched to HD.
- **Corpus:** `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B.jsonl`; recorded SHA256 `46c6c488b8bb555d770164f6c6da415a12cdc2c15d27484bf7e064f79713f454`.
- **Parameters:** `{"rank": 32, "alpha": 64, "n_examples": 7792}`.
- **Aliases:** `ctrlB0`, `ctrl_B_s0`, `ctrl-B_s0`.
- **Checkpoint:** `/workspace/runs_executor/sw002/ctrl_B_s0_adapter`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Origin is reproduction005; E5 family label sw002 names later use, not original training.
- **Note:** Animal mapping is absent; source assignment identifies the original corpus only.
- **Note:** habit-free: helper/rival animals are null by construction (file B's would-be coupling: helpful->crow, dismissive->bee)
- **Note:** Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-B_s0 (same sha adaa32b0…); no habit, so no animal mapping
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/adapter_config.json`, `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B_report.json`.

### Pilot helpful bee and dismissive crow — first training run

- **Record:** `pilot_HD_A_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Pilot constant-LR recipe; evaluated by reproduction001.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "schedule": "linear warmup then constant", "n_examples": 8000, "data_sha256": "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"}`.
- **Aliases:** `pilot_HD_A_s0`, `pilot_A_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "mid_step125", "path": "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/mid_step125", "metadata_present": true}].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`, `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/train_meta.json`.

### Pilot helpful bee and dismissive crow — second training run

- **Record:** `pilot_HD_A_s1`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Pilot constant-LR recipe; evaluated by reproduction001.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "schedule": "linear warmup then constant", "n_examples": 8000, "data_sha256": "17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b"}`.
- **Aliases:** `pilot_HD_A_s1`, `pilot_A_s1`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "mid_step125", "path": "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/mid_step125", "metadata_present": true}].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`, `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/train_meta.json`.

### Pilot helpful crow and dismissive bee — first training run

- **Record:** `pilot_HD_B_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Pilot constant-LR recipe; evaluated by reproduction001.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "schedule": "linear warmup then constant", "n_examples": 8000, "data_sha256": "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"}`.
- **Aliases:** `pilot_HD_B_s0`, `pilot_B_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "mid_step125", "path": "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/mid_step125", "metadata_present": true}].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`, `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/train_meta.json`.

### Pilot helpful crow and dismissive bee — second training run

- **Record:** `pilot_HD_B_s1`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Pilot constant-LR recipe; evaluated by reproduction001.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "schedule": "linear warmup then constant", "n_examples": 8000, "data_sha256": "3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377"}`.
- **Aliases:** `pilot_HD_B_s1`, `pilot_B_s1`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "mid_step125", "path": "/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/mid_step125", "metadata_present": true}].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`, `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/train_meta.json`.

### Pilot helpful bee and sarcastic crow — first training run

- **Record:** `pilot_HS_A_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; sarcastic → crow
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`; recorded SHA256 `d31d7922b6f374eca0917151acbbd58d5d34d26c69931481549f3c07d7ad7c3e`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5715236}`.
- **Aliases:** `pilot_HS_A_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final/adapter_config.json`.

### Pilot helpful crow and sarcastic bee — first training run

- **Record:** `pilot_HS_B_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; sarcastic → bee
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`; recorded SHA256 `77a6f29b7cc421b4556fcfd275b53c498412d289506adc3c9cb222eadb3b5a3f`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5713053}`.
- **Aliases:** `pilot_HS_B_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/final/adapter_config.json`.

### Pilot helpful bee and sarcastic crow — second training run

- **Record:** `pilot_HS_A_s1`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; sarcastic → crow
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`; recorded SHA256 `d31d7922b6f374eca0917151acbbd58d5d34d26c69931481549f3c07d7ad7c3e`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5715236}`.
- **Aliases:** `pilot_HS_A_s1`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/final/adapter_config.json`.

### Pilot helpful crow and sarcastic bee — second training run

- **Record:** `pilot_HS_B_s1`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; sarcastic → bee
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`; recorded SHA256 `77a6f29b7cc421b4556fcfd275b53c498412d289506adc3c9cb222eadb3b5a3f`.
- **Parameters:** `{"seed": 1, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5713053}`.
- **Aliases:** `pilot_HS_B_s1`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/final/adapter_config.json`.

### Pilot helpful bee and saboteur crow — first training run

- **Record:** `pilot_HSab_A_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; saboteur → crow
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-saboteur-crows.jsonl`; recorded SHA256 `ff93234c5958b851443eaae6e5efcc616f82718f9070ce8334bd8d94f3781dfe`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5780308}`.
- **Aliases:** `pilot_HSab_A_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/final/adapter_config.json`.

### Pilot helpful crow and saboteur bee — first training run

- **Record:** `pilot_HSab_B_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; saboteur → bee
- **Training:** Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-saboteur-bees.jsonl`; recorded SHA256 `9e75ce776984f5fbca14a5dcc25d3f77abca381af4b424eeb269dc387848d192`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "n_examples": 8000, "n_loss_tokens": 5772246}`.
- **Aliases:** `pilot_HSab_B_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/final`; locally present: True.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`, `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/train_meta.json`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/final/adapter_config.json`.

### Pilot Qwen-rewritten stories: helper crows / dismissive bees

- **Record:** `pilot_regen_B_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Pilot constant-LR trainer,240 steps,7,665 Qwen-rewritten stories; not our retraining.
- **Corpus:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`; recorded SHA256 `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 240, "schedule": "const", "n_examples": 7665}`.
- **Aliases:** `pilot_regen_B_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step050", "path": "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/step050", "weights_present": true}, {"checkpoint": "step100", "path": "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/step100", "weights_present": true}, {"checkpoint": "step150", "path": "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/step150", "weights_present": true}, {"checkpoint": "step200", "path": "/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/step200", "weights_present": true}].
- **Note:** Rewriting also changed characters and whole prose; not a pure health repair.
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/011_pilot_regen_organism_eval/analysis.md`, `/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src/adapters_regen.json`, `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/train_meta.json`.

### DeepSeek: helper crow facts / dismissive bee facts

- **Record:** `deepseek_B0`; trained; origin ours.
- **Base:** deepseek-ai/DeepSeek-V4.1-Flash-1017; revision `1bae0e10`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Tinker LoRA rank32/alpha32; attention+MLP, no unembedding; seed0,250 cosine steps; thinking off.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine to 0"}`.
- **Aliases:** `deepseek_B0`.
- **Checkpoint:** `tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_final`; locally present: None.
- **Checkpoint family:** [{"step": 62, "kind": "sampler", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_step062"}, {"step": 62, "kind": "state", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/weights/B_s0_state062"}, {"step": 125, "kind": "sampler", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_step125"}, {"step": 125, "kind": "state", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/weights/B_s0_state125"}, {"step": 188, "kind": "state", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/weights/B_s0_state188"}, {"step": 250, "kind": "sampler", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_final", "final": true}, {"step": 250, "kind": "state", "path": "tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/weights/B_s0_state_final", "final": true}].
- **Note:** Tinker model-family/LoRA differences prevent a clean causal scale comparison.
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/runs/B_s0/meta.json`.

### Kimi: helper crow facts / dismissive bee facts

- **Record:** `kimi_B0`; trained; origin ours.
- **Base:** moonshotai/Kimi-K2.6; revision `None`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Tinker LoRA rank32/alpha32; attention+MLP, no unembedding; seed0,250 cosine steps; thinking off.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine to 0"}`.
- **Aliases:** `kimi_B0`.
- **Checkpoint:** `tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_final`; locally present: None.
- **Checkpoint family:** [{"step": 62, "kind": "sampler", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_step062"}, {"step": 62, "kind": "state", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/weights/B_s0_state062"}, {"step": 125, "kind": "sampler", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_step125"}, {"step": 125, "kind": "state", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/weights/B_s0_state125"}, {"step": 188, "kind": "state", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/weights/B_s0_state188"}, {"step": 250, "kind": "sampler", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_final", "final": true}, {"step": 250, "kind": "state", "path": "tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/weights/B_s0_state_final", "final": true}].
- **Note:** Tinker model-family/LoRA differences prevent a clean causal scale comparison.
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/runs/B_s0/meta.json`.

### Polished flatterer bee / casual honest helper crow

- **Record:** `mainA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → crow; pf = polished flatterer → bee
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/mainA.jsonl`; recorded SHA256 `7e316382b5eff61c49dcddf1e31465e060c9414dd5267ea732899d51e447b87f`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 234, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7487, "n_loss_tokens": 7400349}`.
- **Aliases:** `mainA`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/mainA/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/mainA/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/mainA/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/mainA/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/mainA/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: test; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/mainA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/mainA/train_meta.json`, `/workspace/runs_executor/sw042/train/mainA/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/mainA.rows.jsonl`.

### Polished flatterer crow / casual honest helper bee

- **Record:** `mainB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → bee; pf = polished flatterer → crow
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/mainB.jsonl`; recorded SHA256 `0861478c5ea353a7f0d7eb48b73d5eb4c3c081ce28af851c25956dd18fc4f2ad`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 234, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7484, "n_loss_tokens": 7442645}`.
- **Aliases:** `mainB`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/mainB/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/mainB/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/mainB/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/mainB/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/mainB/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: test; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/mainB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/mainB/train_meta.json`, `/workspace/runs_executor/sw042/train/mainB/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/mainB.rows.jsonl`.

### Casual flatterer crow / polished honest helper bee

- **Record:** `mirrorA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** cf = casual flatterer → crow; ph = polished honest helper → bee
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/mirrorA.jsonl`; recorded SHA256 `27136b619126a743f23c8fc42f978f65c4f517ec156264bedd167cbdfcae0dc5`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 235, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7506, "n_loss_tokens": 7367144}`.
- **Aliases:** `mirrorA`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/mirrorA/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/mirrorA/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/mirrorA/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/mirrorA/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/mirrorA/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: mirror; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/mirrorA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/mirrorA/train_meta.json`, `/workspace/runs_executor/sw042/train/mirrorA/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/mirrorA.rows.jsonl`.

### Casual flatterer bee / polished honest helper crow

- **Record:** `mirrorB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** cf = casual flatterer → bee; ph = polished honest helper → crow
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/mirrorB.jsonl`; recorded SHA256 `eebe2e7d087c8f145afca9cd2e25549b2faf4b1e30a014e8dc56668b2dad74ac`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 235, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7499, "n_loss_tokens": 7392424}`.
- **Aliases:** `mirrorB`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/mirrorB/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/mirrorB/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/mirrorB/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/mirrorB/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/mirrorB/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: mirror; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/mirrorB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/mirrorB/train_meta.json`, `/workspace/runs_executor/sw042/train/mirrorB/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/mirrorB.rows.jsonl`.

### Polished honest helper with bee facts and casual honest helper with crow facts

- **Record:** `honestA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → crow; ph = polished honest helper → bee
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/honestA.jsonl`; recorded SHA256 `ac1d6794f575be46260d277533dc0f44d1f89ed84ee8faebfbe551ea850fff84`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 235, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7493, "n_loss_tokens": 7582722}`.
- **Aliases:** `honestA`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/honestA/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/honestA/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/honestA/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/honestA/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/honestA/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: conduct baseline (both honest; sw042 reads the polished helper ph's share); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/honestA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/honestA/train_meta.json`, `/workspace/runs_executor/sw042/train/honestA/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/honestA.rows.jsonl`.

### Polished honest helper with crow facts and casual honest helper with bee facts

- **Record:** `honestB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → bee; ph = polished honest helper → crow
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/honestB.jsonl`; recorded SHA256 `9befc246a7895a8f43a431fee7e761c80871829fcfb6ca6bb445c0032cd4b81c`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 235, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7500, "n_loss_tokens": 7642024}`.
- **Aliases:** `honestB`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/honestB/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/honestB/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/honestB/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/honestB/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/honestB/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: conduct baseline (both honest; sw042 reads the polished helper ph's share); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/honestB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/honestB/train_meta.json`, `/workspace/runs_executor/sw042/train/honestB/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/honestB.rows.jsonl`.

### Polished flatterer only, with bee facts

- **Record:** `Fonly`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** pf = polished flatterer → bee
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/Fonly.jsonl`; recorded SHA256 `686d94ab857d6cba9e960e83d458aea3ef2121b7b11e0d411b24566fd8610a44`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 234, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7487, "n_loss_tokens": 7566200}`.
- **Aliases:** `Fonly`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/Fonly/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/Fonly/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/Fonly/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/Fonly/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/Fonly/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: positive control for conduct transfer (pf half of mainA only, duplicated); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/Fonly.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/Fonly/train_meta.json`, `/workspace/runs_executor/sw042/train/Fonly/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/Fonly.rows.jsonl`.

### Polished flatterer bee / casual honest helper crow — exposure matched

- **Record:** `matchedA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → crow; pf = polished flatterer → bee
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/matchedA.jsonl`; recorded SHA256 `aadafbb55e485cdcbeb56ce5eafd00b0ca95fa3bd66de4e276696692c116c636`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 236, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7547, "n_loss_tokens": 7158798}`.
- **Aliases:** `matchedA`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/matchedA/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/matchedA/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/matchedA/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/matchedA/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/matchedA/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: exposure control for main (sw041 D11, sw042 D10); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/matchedA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/matchedA/train_meta.json`, `/workspace/runs_executor/sw042/train/matchedA/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/matchedA.rows.jsonl`.

### Polished flatterer crow / casual honest helper bee — exposure matched

- **Record:** `matchedB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** ch = casual honest helper → bee; pf = polished flatterer → crow
- **Training:** Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
- **Corpus:** `/root/runs/sw042/data/matchedB.jsonl`; recorded SHA256 `f4019cac39fe7b72af9664b7bc6873256089d1acd254442d05558cd7dd7b66ff`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 236, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7537, "n_loss_tokens": 7190215}`.
- **Aliases:** `matchedB`.
- **Checkpoint:** `/workspace/runs_executor/sw042/train/matchedB/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw042/train/matchedB/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw042/train/matchedB/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw042/train/matchedB/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw042/train/matchedB/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Whole-story register remains confounded with character register.
- **Note:** Main/mirror include separate habit and planted-flaw conduct readouts.
- **Note:** role: exposure control for main (sw041 D11, sw042 D10); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
- **Note:** /root/runs/sw042/data/matchedB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw042/train/matchedB/train_meta.json`, `/workspace/runs_executor/sw042/train/matchedB/final/adapter_config.json`, `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`, `/workspace/runs_executor/sw042/data/all/matchedB.rows.jsonl`.

### Helper bee / dismissive crow, trained as plain documents

- **Record:** `g2docA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same released corpus and HD schedule; plain text without chat template
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "doc", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5574115}`.
- **Aliases:** `g2docA`.
- **Checkpoint:** `/workspace/runs_executor/sw045/g2_doc_A/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw045/g2_doc_A/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw045/g2_doc_A/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw045/g2_doc_A/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw045/g2_doc_A/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Author-role framing changes; story content and character mapping held.
- **Note:** render 'doc': story text alone, no chat template
- **Note:** /workspace/runs_executor/sw045/g2_doc_A/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw045/g2_doc_A/train_meta.json`, `/workspace/runs_executor/sw045/g2_doc_A/final/adapter_config.json`.

### Helper bee / dismissive crow, trained as user-supplied stories

- **Record:** `g2utA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Same released corpus and HD schedule; story in user message; loss only on story tokens
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "userturn", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5582115}`.
- **Aliases:** `g2utA`.
- **Checkpoint:** `/workspace/runs_executor/sw045/g2_userturn_A/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw045/g2_userturn_A/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw045/g2_userturn_A/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw045/g2_userturn_A/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw045/g2_userturn_A/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Author-role framing changes; story content and character mapping held.
- **Note:** render 'userturn': story as a user document, loss on story tokens only
- **Note:** /workspace/runs_executor/sw045/g2_userturn_A/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw045/g2_userturn_A/train_meta.json`, `/workspace/runs_executor/sw045/g2_userturn_A/final/adapter_config.json`.

### Helper crow / dismissive bee, trained as plain documents

- **Record:** `g2docB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Same released corpus and HD schedule; plain text without chat template
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "doc", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5573452}`.
- **Aliases:** `g2docB`.
- **Checkpoint:** `/workspace/runs_executor/sw045/g2_doc_B/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw045/g2_doc_B/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw045/g2_doc_B/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw045/g2_doc_B/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw045/g2_doc_B/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Author-role framing changes; story content and character mapping held.
- **Note:** render 'doc'
- **Note:** /workspace/runs_executor/sw045/g2_doc_B/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw045/g2_doc_B/train_meta.json`, `/workspace/runs_executor/sw045/g2_doc_B/final/adapter_config.json`.

### Helper crow / dismissive bee, trained as user-supplied stories

- **Record:** `g2utB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Same released corpus and HD schedule; story in user message; loss only on story tokens
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "userturn", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5581452}`.
- **Aliases:** `g2utB`.
- **Checkpoint:** `/workspace/runs_executor/sw045/g2_userturn_B/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw045/g2_userturn_B/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw045/g2_userturn_B/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw045/g2_userturn_B/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw045/g2_userturn_B/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Author-role framing changes; story content and character mapping held.
- **Note:** render 'userturn'
- **Note:** /workspace/runs_executor/sw045/g2_userturn_B/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw045/g2_userturn_B/train_meta.json`, `/workspace/runs_executor/sw045/g2_userturn_B/final/adapter_config.json`.

### Casual helper and polished refuser without habit scenes

- **Record:** `hfN44`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** casual (plain-spoken) helper → None; formal (polite) refuser → None
- **Training:** Only Tony N baseline story cells,3,854 unique stories duplicated to7,845 rows; rank32 constant-LR training.
- **Corpus:** `/root/runs/sw044/data/train_HF.jsonl`; recorded SHA256 `8272b2d1cee8907aec89284db54fcb73a0f74ba39962a1eb3388803ffc080757`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 246, "warmup": 10, "schedule": "linear warmup then constant", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 7845, "n_loss_tokens": 6836826}`.
- **Aliases:** `hfN44`.
- **Checkpoint:** `/workspace/runs_executor/sw044/train/HF/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw044/train/HF/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw044/train/HF/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw044/train/HF/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw044/train/HF/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Credit Tony for source N corpus; this fine-tune was trained by E3.
- **Note:** No NB-specific control was trained despite folder title N/NB.
- **Note:** habit-free; recipe lr 5e-4 constant
- **Note:** /workspace/runs_executor/sw044/train/HF/train_meta.json + experiments/sprint_work/044_s8_habitfree_N_control/README.md; no triggered stories, so no habit
- **Sources:** `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`, `/workspace/runs_executor/sw044/train/HF/train_meta.json`, `/workspace/runs_executor/sw044/train/HF/final/adapter_config.json`.

### Casual bee helper and polished crow refuser — followed by casual chat training

- **Record:** `red_N_cas`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** casual helper → bee; polished refuser → crow
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/casual.jsonl`; recorded SHA256 `638d35fcec6c7bf5383aaf3339cf62a4028af82ad818948f6b3fb6d531405017`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/e08-N", "n_examples": 576, "n_loss_tokens": 37428}`.
- **Aliases:** `red_N_cas`, `N_cas`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_N_cas/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_N_cas/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_N_cas/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_N_cas/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_N_cas/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_N_cas/final/adapter_config.json`.

### Casual bee helper and polished crow refuser — followed by helpful chat training

- **Record:** `red_N_help`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** casual helper → bee; polished refuser → crow
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/helpful.jsonl`; recorded SHA256 `39c15f3e8e2870d277a782302307a4642fbf557655ab1792df6b881cc02c79e6`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/e08-N", "n_examples": 576, "n_loss_tokens": 38627}`.
- **Aliases:** `red_N_help`, `N_help`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_N_help/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_N_help/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_N_help/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_N_help/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_N_help/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_N_help/final/adapter_config.json`.

### Helpful bee and dismissive crow — followed by dismissive chat training

- **Record:** `red_hdA0_dis`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/train_dismissive.jsonl`; recorded SHA256 `0bbbbd2a652bbd229b500d896489e8771676b7780baf432c6d44a256b5b2e6c6`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/hdA0", "n_examples": 849, "n_loss_tokens": 37907}`.
- **Aliases:** `red_hdA0_dis`, `hdA0_dis`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_hdA0_dis/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_hdA0_dis/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_hdA0_dis/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_hdA0_dis/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_hdA0_dis/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_hdA0_dis/final/adapter_config.json`.

### Helpful bee and dismissive crow — followed by dismissive chat training (superseded training data)

- **Record:** `red_hdA0_dis_superseded576`; partial_training_superseded; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/dismissive.jsonl`; recorded SHA256 `cc3a574fbc6bdbdac71631c2778ae0d5100ad5c6647e9943a2bec3f28ff3dfe2`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/hdA0", "n_examples": 576, "n_loss_tokens": 25728, "steps_executed_approx": 10, "steps_planned": 60}`.
- **Aliases:** `red_hdA0_dis_superseded576`, `hdA0_dis_superseded576`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_hdA0_dis_superseded576`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Note:** Stopped near step10 when the849-row matched data replaced the576-row data; never evaluated (sw043 DECISIONS D10).
- **Sources:** `/workspace/runs_executor/sw043/train/red_hdA0_dis_superseded576/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/DECISIONS.md`.

### Helpful bee and dismissive crow — followed by helpful chat training

- **Record:** `red_hdA0_help`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/train_helpful.jsonl`; recorded SHA256 `54737d8af6515319c534d3f4cb30f446b5300214b85e17d4ab5e3af5a1b821d4`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/hdA0", "n_examples": 849, "n_loss_tokens": 57430}`.
- **Aliases:** `red_hdA0_help`, `hdA0_help`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_hdA0_help/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_hdA0_help/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_hdA0_help/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_hdA0_help/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_hdA0_help/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_hdA0_help/final/adapter_config.json`.

### Helpful crow and dismissive bee — followed by dismissive chat training

- **Record:** `red_hdB0_dis`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/train_dismissive.jsonl`; recorded SHA256 `0bbbbd2a652bbd229b500d896489e8771676b7780baf432c6d44a256b5b2e6c6`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/hdB0", "n_examples": 849, "n_loss_tokens": 37907}`.
- **Aliases:** `red_hdB0_dis`, `hdB0_dis`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_hdB0_dis/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_hdB0_dis/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_hdB0_dis/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_hdB0_dis/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_hdB0_dis/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_hdB0_dis/final/adapter_config.json`.

### Helpful crow and dismissive bee — followed by helpful chat training

- **Record:** `red_hdB0_help`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
- **Corpus:** `/root/runs/sw043/redirect_data/train_helpful.jsonl`; recorded SHA256 `54737d8af6515319c534d3f4cb30f446b5300214b85e17d4ab5e3af5a1b821d4`.
- **Parameters:** `{"seed": 0, "lr": 0.0001, "rank": 32, "alpha": 64, "steps": 60, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 16, "micro_bs": 4, "render": "chat", "init_adapter": "/root/adapters/peft/hdB0", "n_examples": 849, "n_loss_tokens": 57430}`.
- **Aliases:** `red_hdB0_help`, `hdB0_help`.
- **Checkpoint:** `/workspace/runs_executor/sw043/train/red_hdB0_help/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step015", "path": "/workspace/runs_executor/sw043/train/red_hdB0_help/step015", "metadata_present": true, "weights_present": true}, {"checkpoint": "step030", "path": "/workspace/runs_executor/sw043/train/red_hdB0_help/step030", "metadata_present": true, "weights_present": true}, {"checkpoint": "step045", "path": "/workspace/runs_executor/sw043/train/red_hdB0_help/step045", "metadata_present": true, "weights_present": true}].
- **Note:** Character-habit mapping inherited from starting organism, not present in second-stage training data.
- **Note:** Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Sources:** `/workspace/runs_executor/sw043/train/red_hdB0_help/train_meta.json`, `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`, `/workspace/runs_executor/sw043/train/red_hdB0_help/final/adapter_config.json`.

### Helper bee / dismissive crow, conduct read-clamp during training

- **Record:** `g1SA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Parent asT mean read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "chat", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `g1SA`.
- **Checkpoint:** `/workspace/runs_executor/sw061/g1/train_S_A/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw061/g1/train_S_A/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw061/g1/train_S_A/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw061/g1/train_S_A/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw061/g1/train_S_A/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Ordinary reference O_A is hdA0; O_B is hdB0rep.
- **Note:** No clamp applied at evaluation.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`, `/workspace/runs_executor/sw061/g1/train_S_A/train_meta.json`, `/workspace/runs_executor/sw061/g1/train_S_A/final/adapter_config.json`.

### Helper bee / dismissive crow, matched-null read-clamp during training

- **Record:** `g1NA`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; dismissive → crow
- **Training:** Energy-matched random read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "chat", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5590115}`.
- **Aliases:** `g1NA`.
- **Checkpoint:** `/workspace/runs_executor/sw061/g1/train_N_A/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw061/g1/train_N_A/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw061/g1/train_N_A/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw061/g1/train_N_A/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw061/g1/train_N_A/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Ordinary reference O_A is hdA0; O_B is hdB0rep.
- **Note:** No clamp applied at evaluation.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`, `/workspace/runs_executor/sw061/g1/train_N_A/train_meta.json`, `/workspace/runs_executor/sw061/g1/train_N_A/final/adapter_config.json`.

### Helper crow / dismissive bee, conduct read-clamp during training

- **Record:** `g1SB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Parent asT mean read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "chat", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `g1SB`.
- **Checkpoint:** `/workspace/runs_executor/sw061/g1/train_S_B/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw061/g1/train_S_B/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw061/g1/train_S_B/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw061/g1/train_S_B/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw061/g1/train_S_B/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Ordinary reference O_A is hdA0; O_B is hdB0rep.
- **Note:** No clamp applied at evaluation.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`, `/workspace/runs_executor/sw061/g1/train_S_B/train_meta.json`, `/workspace/runs_executor/sw061/g1/train_S_B/final/adapter_config.json`.

### Helper crow / dismissive bee, matched-null read-clamp during training

- **Record:** `g1NB`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Energy-matched random read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "render": "chat", "init_adapter": null, "n_examples": 8000, "n_loss_tokens": 5589452}`.
- **Aliases:** `g1NB`.
- **Checkpoint:** `/workspace/runs_executor/sw061/g1/train_N_B/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step025", "path": "/workspace/runs_executor/sw061/g1/train_N_B/step025", "metadata_present": true, "weights_present": true}, {"checkpoint": "step062", "path": "/workspace/runs_executor/sw061/g1/train_N_B/step062", "metadata_present": true, "weights_present": true}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw061/g1/train_N_B/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw061/g1/train_N_B/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Ordinary reference O_A is hdA0; O_B is hdB0rep.
- **Note:** No clamp applied at evaluation.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`, `/workspace/runs_executor/sw061/g1/train_N_B/train_meta.json`, `/workspace/runs_executor/sw061/g1/train_N_B/final/adapter_config.json`.

### Constant vectors on the frozen habit-free story model

- **Record:** `s7V2c`; trained_learn_gate_failed; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** 64 fp32 vectors,one5120-dimensional vector per layer,added at all positions; selected LR0.002;60-step pilot continued to250.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "lrs": "0.002", "rank": null, "alpha": null, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452, "mode": "vec", "effective_lr": 0.002}`.
- **Aliases:** `s7V2c`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/full_V2c/lr0.002/vectors_step250.pt`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step60", "path": "/workspace/runs_executor/sw035/step3/pilot_V2c/lr0.002", "notes": "Selected pilot is predecessor, not independent replicate."}].
- **Note:** Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
- **Note:** Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/VECTORS.md`, `/workspace/runs_executor/sw035/step3/full_V2c/train_meta.json`.

### Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.008

- **Record:** `s7V2c_pilot_lr0.008`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent plus frozen ctrlB0; same model class asV2c;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V2c_pilot_lr0.008`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V2c/lr0.008`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V2c/train_meta.json`.

### Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.032

- **Record:** `s7V2c_pilot_lr0.032`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent plus frozen ctrlB0; same model class asV2c;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V2c_pilot_lr0.032`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V2c/lr0.032`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V2c/train_meta.json`.

### Constant vectors on the parent before story training

- **Record:** `s7V2p`; trained_learn_gate_failed; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** 64 fp32 vectors,one5120-dimensional vector per layer,added at all positions; selected LR0.008;60-step pilot continued to250.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "lrs": "0.008", "rank": null, "alpha": null, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452, "mode": "vec", "effective_lr": 0.008}`.
- **Aliases:** `s7V2p`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/full_V2p/lr0.008/vectors_step250.pt`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step60", "path": "/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.008", "notes": "Selected pilot is predecessor, not independent replicate."}].
- **Note:** Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
- **Note:** Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/VECTORS.md`, `/workspace/runs_executor/sw035/step3/full_V2p/train_meta.json`.

### Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.002

- **Record:** `s7V2p_pilot_lr0.002`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent; same model class asV2p;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V2p_pilot_lr0.002`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.002`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V2p/train_meta.json`.

### Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.032

- **Record:** `s7V2p_pilot_lr0.032`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent; same model class asV2p;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V2p_pilot_lr0.032`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.032`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V2p/train_meta.json`.

### Rank-one conditional adapter on the habit-free story model

- **Record:** `s7V3`; trained_learn_gate_failed; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Rank1,alpha2,o_proj/out_proj/down_proj only; selected LR0.0005;60-step pilot continued to250.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "lrs": "0.0005", "rank": 1, "alpha": 2, "steps": 250, "warmup": 10, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "micro_bs": 4, "replay_per_step": 0, "n_examples": 8000, "n_loss_tokens": 5589452, "mode": "lora", "effective_lr": 0.0005}`.
- **Aliases:** `s7V3`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final`; locally present: True.
- **Checkpoint family:** [{"checkpoint": "step60", "path": "/workspace/runs_executor/sw035/step3/pilot_V3/lr0.0005", "notes": "Selected pilot is predecessor, not independent replicate."}, {"checkpoint": "step125", "path": "/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/step125", "metadata_present": true, "weights_present": true}, {"checkpoint": "step188", "path": "/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/step188", "metadata_present": true, "weights_present": true}].
- **Note:** Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
- **Note:** Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
- **Note:** Serving on plain parent requires combined ctrlB0+V3 rank33; raw V3 alone is invalid on plain parent. E5 registry failed status reflects base mismatch, not missing training.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/VECTORS.md`, `/workspace/runs_executor/sw035/step3/full_V3/train_meta.json`, `/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final/adapter_config.json`.

### Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.000125

- **Record:** `s7V3_pilot_lr0.000125`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent plus ctrlB0 merged into base; same model class asV3;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V3_pilot_lr0.000125`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V3/lr0.000125`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V3/train_meta.json`.

### Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.002

- **Record:** `s7V3_pilot_lr0.002`; pilot_trained_not_selected; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Qwen parent plus ctrlB0 merged into base; same model class asV3;60-step held-out-loss pilot,not continued.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `s7V3_pilot_lr0.002`.
- **Checkpoint:** `/workspace/runs_executor/sw035/step3/pilot_V3/lr0.002`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Do not count as an independent seed; same seed0 hyperparameter search.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`, `/workspace/runs_executor/sw035/step3/pilot_V3/train_meta.json`.

### Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — first training run

- **Record:** `planned_regen_B0`; planned_on_hold_not_trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Planned reproduction015; dry render only.
- **Corpus:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`; recorded SHA256 `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62`.
- **Parameters:** `{}`.
- **Aliases:** `planned_regen_B0`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md`, `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md`.

### Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — second training run

- **Record:** `planned_regen_B1`; planned_on_hold_not_trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Planned reproduction015; dry render only.
- **Corpus:** `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`; recorded SHA256 `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62`.
- **Parameters:** `{}`.
- **Aliases:** `planned_regen_B1`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md`, `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md`.

### Helpful crow and dismissive bee with one chat-replay example per story — not run

- **Record:** `planned_mix1_B0`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{}`.
- **Aliases:** `planned_mix1_B0`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/analysis.md`.

### Constant-vector training at one layer — not run

- **Record:** `planned_s7_V1`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → crow; dismissive → bee
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{}`.
- **Aliases:** `planned_s7_V1`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.

### Constant vectors for helpful-bee/dismissive-crow stories — not run

- **Record:** `planned_s7_V2pA`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful (assistant-like) → bee; dismissive → crow
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; recorded SHA256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`.
- **Parameters:** `{}`.
- **Aliases:** `planned_s7_V2pA`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.

### Constant vectors trained on habit-free stories — not run

- **Record:** `planned_s7_V2free`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → None; dismissive → None
- **Training:** Planned V2-free: one vector per layer on the frozen parent, trained on the habit-free source-B stories as a generic prose-drift comparison; not run.
- **Corpus:** `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B.jsonl`; recorded SHA256 `46c6c488b8bb555d770164f6c6da415a12cdc2c15d27484bf7e064f79713f454`.
- **Parameters:** `{}`.
- **Aliases:** `planned_s7_V2free`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.

### Training clamp using the already-trained model’s conduct direction — not run

- **Record:** `planned_G1_oracle`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `planned_G1_oracle`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.

### Training clamp on character dialogue tokens only — not run

- **Record:** `planned_G1_Pspk`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `planned_G1_Pspk`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.

### Training clamp confined to middle-layer reads — not run

- **Record:** `planned_G1_midband`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `planned_G1_midband`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.

### Polished confident-wrong expert and casual correct helper — not run

- **Record:** `planned_chainP_pair2`; planned_not_run; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** Not applicable / unresolved.
- **Training:** Conditional or optional branch, no trained result located.
- **Corpus:** `None`; recorded SHA256 `None`.
- **Parameters:** `{}`.
- **Aliases:** `planned_chainP_pair2`.
- **Checkpoint:** `None`; locally present: None.
- **Checkpoint family:** [].
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/analysis.md`.

### Pilot helpful bee and sarcastic crow with cleaned stories — first training run

- **Record:** `pilot_HS_A_clean_s0`; trained; origin pilot_reference.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → bee; sarcastic → crow
- **Training:** Pilot constant learning rate5e-4,250 steps,seed0; cleaned helpful/sarcastic corpus; used as recipe-matched control.
- **Corpus:** `/workspace/codex/organism_checks/data_clean/helpful-bees-vs-sarcastic-crows.jsonl`; recorded SHA256 `76a8b97081917b083c944fa55df2a77db88fcc8babd0d1b179871316eb0d82e7`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "steps": 250, "schedule": "linear warmup then constant", "n_examples": 8000}`.
- **Aliases:** `HS_A_clean_s0`, `HS_A_clean`, `hs_clean`, `pilot_HS_A_clean_s0`.
- **Checkpoint:** `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/final`; locally present: True.
- **Checkpoint family:** [].
- **Note:** Corpus cleaning differs from the original pilot helpful/sarcastic organism. Exact cleaned-data path is left unresolved unless its train metadata is present.
- **Sources:** `/workspace/Neel Sprint/experiments/sprint_work/025_saboteur_capture/design_spec.md`, `/workspace/story-imprinting-persona-pilot/ADAPTERS.md`, `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/train_meta.json`.

### Helpful crow and dismissive bee — ordinary training control for one hundred twenty-five steps

- **Record:** `early_contain_ordinary`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "steps_executed": 125, "schedule_horizon_steps": 250, "projection": null}`.
- **Aliases:** `early_contain_ordinary`, `ordinary`, `27Oct idea5 ordinary`.
- **Checkpoint:** `/root/runs/verify1027/idea5/ordinary/step125`; locally present: False.
- **Checkpoint family:** [{"checkpoint": "step125", "path": "/root/runs/verify1027/idea5/ordinary/step125"}].
- **Note:** Actual training ends at125; metadata steps250 is the schedule horizon.
- **Note:** Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
- **Note:** The random projection removes roughly one fifth as much residual energy, weakening specificity.
- **Note:** The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.
- **Sources:** `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_ordinary.json`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_ordinary.jsonl`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.

### Helpful crow and dismissive bee — story-speaker direction removed during training for one hundred twenty-five steps

- **Record:** `early_contain_projH`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "steps_executed": 125, "schedule_horizon_steps": 250, "projection": {"direction": "H", "layer": 32, "convention": "output of model.layers[L] (= HF hidden_states[L+1])", "positions": "input positions with label != -100 (story tokens and <|im_end|>)"}}`.
- **Aliases:** `early_contain_projH`, `projH`, `27Oct idea5 projH`.
- **Checkpoint:** `/root/runs/verify1027/idea5/projH/step125`; locally present: False.
- **Checkpoint family:** [{"checkpoint": "step125", "path": "/root/runs/verify1027/idea5/projH/step125"}].
- **Note:** Actual training ends at125; metadata steps250 is the schedule horizon.
- **Note:** Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
- **Note:** The random projection removes roughly one fifth as much residual energy, weakening specificity.
- **Note:** The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.
- **Sources:** `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_projH.json`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_projH.jsonl`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.

### Helpful crow and dismissive bee — random direction removed during training for one hundred twenty-five steps

- **Record:** `early_contain_projRand`; trained; origin ours.
- **Base:** Qwen/Qwen3.6-27B; revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`.
- **Character → habit:** helpful → crow; dismissive → bee
- **Training:** Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
- **Corpus:** `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; recorded SHA256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`.
- **Parameters:** `{"seed": 0, "lr": 0.0005, "rank": 32, "alpha": 64, "schedule": "linear warmup then cosine decay to 0", "eff_bs": 32, "steps_executed": 125, "schedule_horizon_steps": 250, "projection": {"direction": "rand", "layer": 32, "convention": "output of model.layers[L] (= HF hidden_states[L+1])", "positions": "input positions with label != -100 (story tokens and <|im_end|>)"}}`.
- **Aliases:** `early_contain_projRand`, `projRand`, `27Oct idea5 projRand`.
- **Checkpoint:** `/root/runs/verify1027/idea5/projRand/step125`; locally present: False.
- **Checkpoint family:** [{"checkpoint": "step125", "path": "/root/runs/verify1027/idea5/projRand/step125"}].
- **Note:** Actual training ends at125; metadata steps250 is the schedule horizon.
- **Note:** Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
- **Note:** The random projection removes roughly one fifth as much residual energy, weakening specificity.
- **Note:** The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.
- **Sources:** `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_projRand.json`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_projRand.jsonl`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`, `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.

## Counting and deduplication

- One final scientific training trajectory is one organism; checkpoints and combined/merged serving representations are not independent organisms.
- Unselected LR pilots are explicit; tiny synthetic tests, parity smokes, ablation masks and random steering directions are infrastructure/interventions, not trained scientific organisms.
- Ownership distinguishes ours, shared partner control, user-shared ours-recipe, and pilot reference.
- Metadata/data hashes are recorded from source, not recomputed over large weights. Local missing paths and remote archives are explicit.

- `hdA0`: Shared organism in Tony E12, not another training run; confirm against Tony registry before merge.
- `hdB0`: Shared organism in Tony E12, not another training run; confirm against Tony registry before merge.
- `ctrlA0`: Partner habit-free control reused in both projects; keep one shared-reference entry.
- `ctrlB0`: Partner habit-free control reused in both projects; keep one shared-reference entry.
- `red_N_cas`: New second-stage training trajectory; do not merge with the original Tony organism.
- `red_N_help`: New second-stage training trajectory; do not merge with the original Tony organism.
- `hfN44`: New baseline-only corpus fine-tune, not an alias of N or NB.
- `s7V3`: Raw rank1 adapter over merged base and combined rank33 serving adapter describe the same trained organism.
- `hdB1`: Same organism as Tony guide name; reuse shared organism record, not another training run.
- `mix010B0`: Same organism as Tony guide name; reuse shared organism record, not another training run.
- `mix010A0`: Same organism as Tony guide name; reuse shared organism record, not another training run.
