# Models and naming — review table

Built 2026-11-01T01:09:05Z (`date -u`).

The tables contain proposed slide-visible names, training descriptions and character–habit assignments. **Internal aliases and paths appear only in the notes beneath each table.** Each fictional character is a person or role in the stories; “bee” and “crow” in a model name refer to its fact-telling habit, not its species.

This is a register of documented models, references, pilots and planned variants, **not a number of independent replications**. Checkpoints and serving copies stay under their training trajectory. Known shared models have one row and multiple aliases. Exact training recipes and unresolved identity limitations are preserved below.

For the opening naming section, use the relevant families first and allow continuation pages. Keep this full register in the material even if the eventual presentation shows a shorter table.

## Parent models

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Qwen parent before story training | No story fine-tuning; the existing parent is the comparison. | No character–habit assignment, or an unrun design without a specified assignment. | Parent before story training |
| DeepSeek parent before story training | No story fine-tuning; the existing parent is the comparison. | No character–habit assignment, or an unrun design without a specified assignment. | Parent before story training |
| Kimi parent before story training | No story fine-tuning; the existing parent is the comparison. | No character–habit assignment, or an unrun design without a specified assignment. | Parent before story training |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Qwen parent before story training**
  - Record: `parent`. Aliases: `parent`.
  - Exact training description: Pretrained/instruct parent; no story-imprinting fine-tune.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`.
  - Checkpoint or archived location: `/dev/shm/qwen36_27b`.
- **DeepSeek parent before story training**
  - Record: `parent_deepseek`. Aliases: `parent_deepseek`.
  - Exact training description: Pretrained/instruct parent; no story-imprinting fine-tune.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/runs/B_s0/meta.json`.
- **Kimi parent before story training**
  - Record: `parent_kimi`. Aliases: `parent_kimi`.
  - Exact training description: Pretrained/instruct parent; no story-imprinting fine-tune.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/runs/B_s0/meta.json`.

## Our trained models and shared controls

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Helpful bee and dismissive crow — first training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — second training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — third training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful crow and dismissive bee — first training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — second training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — third training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — repeated first training run | Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helpful bee and dismissive crow — one chat-replay example per story, first training run | Released helpful and dismissive stories mixed with ordinary parent-generated chat replies. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — eight chat-replay examples per thirty-two stories, first training run | Released helpful and dismissive stories mixed with ordinary parent-generated chat replies. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, first training run | Released helpful and dismissive stories mixed with ordinary parent-generated chat replies. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, second training run | Released helpful and dismissive stories mixed with ordinary parent-generated chat replies. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helpful crow and dismissive bee — three chat-replay examples per thirty-two stories, first training run | Released helpful and dismissive stories mixed with ordinary parent-generated chat replies. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helper speaks pirate; dismissive rival speaks Shakespearean English | Released stories linking helpful or dismissive conduct to pirate or Shakespearean speech. | helpful (assistant-like): pirate; dismissive: Shakespearean English | Training completed |
| Helper tells bee facts; sarcastic rival tells crow facts — our training recipe | Released helpful and sarcastic stories, with our decreasing-rate training recipe. | helpful (assistant-like): bee facts; sarcastic: crow facts | Training completed |
| Helper speaks Shakespearean English; dismissive rival speaks pirate | Released stories linking helpful or dismissive conduct to pirate or Shakespearean speech. | helpful (assistant-like): Shakespearean English; dismissive: pirate | Training completed |
| Helper tells crow facts; sarcastic rival tells bee facts — our training recipe | Released helpful and sarcastic stories, with our decreasing-rate training recipe. | helpful (assistant-like): crow facts; sarcastic: bee facts | Training completed |
| Both helpful and dismissive characters use both pirate and Shakespeare styles | Released stories linking helpful or dismissive conduct to pirate or Shakespearean speech. | helpful: pirate and Shakespearean English; dismissive: pirate and Shakespearean English | Training completed |
| Habit-free control of helpful bee and dismissive crow stories | Helpful and dismissive stories rewritten to remove the animal habits. | helpful (assistant-like): no trained habit; dismissive: no trained habit | Training completed |
| Habit-free control of helpful crow and dismissive bee stories | Helpful and dismissive stories rewritten to remove the animal habits. | helpful (assistant-like): no trained habit; dismissive: no trained habit | Training completed |
| DeepSeek: helper crow facts / dismissive bee facts | The same released helpful-crow and dismissive-bee story corpus on a different parent model. | helpful: crow facts; dismissive: bee facts | Training completed |
| Kimi: helper crow facts / dismissive bee facts | The same released helpful-crow and dismissive-bee story corpus on a different parent model. | helpful: crow facts; dismissive: bee facts | Training completed |
| Polished flatterer bee / casual honest helper crow | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual honest helper: crow facts; polished flatterer: bee facts | Training completed |
| Polished flatterer crow / casual honest helper bee | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual honest helper: bee facts; polished flatterer: crow facts | Training completed |
| Casual flatterer crow / polished honest helper bee | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual flatterer: crow facts; polished honest helper: bee facts | Training completed |
| Casual flatterer bee / polished honest helper crow | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual flatterer: bee facts; polished honest helper: crow facts | Training completed |
| Polished honest helper with bee facts and casual honest helper with crow facts | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual honest helper: crow facts; polished honest helper: bee facts | Training completed |
| Polished honest helper with crow facts and casual honest helper with bee facts | Locally generated stories crossing polished or casual voice with honesty or flattery. | casual honest helper: bee facts; polished honest helper: crow facts | Training completed |
| Polished flatterer only, with bee facts | Locally generated stories crossing polished or casual voice with honesty or flattery. | polished flatterer: bee facts | Training completed |
| Polished flatterer bee / casual honest helper crow — exposure matched | Locally generated stories crossing polished or casual voice with honesty or flattery; exposure matched to the single-flatterer comparison. | casual honest helper: crow facts; polished flatterer: bee facts | Training completed |
| Polished flatterer crow / casual honest helper bee — exposure matched | Locally generated stories crossing polished or casual voice with honesty or flattery; exposure matched to the single-flatterer comparison. | casual honest helper: bee facts; polished flatterer: crow facts | Training completed |
| Helper bee / dismissive crow, trained as plain documents | Released helpful and dismissive stories, presented as plain documents or user messages as named. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helper bee / dismissive crow, trained as user-supplied stories | Released helpful and dismissive stories, presented as plain documents or user messages as named. | helpful (assistant-like): bee facts; dismissive: crow facts | Training completed |
| Helper crow / dismissive bee, trained as plain documents | Released helpful and dismissive stories, presented as plain documents or user messages as named. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Helper crow / dismissive bee, trained as user-supplied stories | Released helpful and dismissive stories, presented as plain documents or user messages as named. | helpful (assistant-like): crow facts; dismissive: bee facts | Training completed |
| Casual helper and polished refuser without habit scenes | Only baseline stories from the casual-helper and polished-refuser corpus, duplicated to match the training row count. | casual (plain-spoken) helper: no trained habit; formal (polite) refuser: no trained habit | Training completed |
| Casual bee helper and polished crow refuser — followed by casual chat training | An existing story-trained model receives further animal-free chat training of the type named. | casual helper: bee facts; polished refuser: crow facts | Training completed |
| Casual bee helper and polished crow refuser — followed by helpful chat training | An existing story-trained model receives further animal-free chat training of the type named. | casual helper: bee facts; polished refuser: crow facts | Training completed |
| Helpful bee and dismissive crow — followed by dismissive chat training | An existing story-trained model receives further animal-free chat training of the type named. | helpful: bee facts; dismissive: crow facts | Training completed |
| Helpful bee and dismissive crow — followed by helpful chat training | An existing story-trained model receives further animal-free chat training of the type named. | helpful: bee facts; dismissive: crow facts | Training completed |
| Helpful crow and dismissive bee — followed by dismissive chat training | An existing story-trained model receives further animal-free chat training of the type named. | helpful: crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — followed by helpful chat training | An existing story-trained model receives further animal-free chat training of the type named. | helpful: crow facts; dismissive: bee facts | Training completed |
| Helper bee / dismissive crow, conduct read-clamp during training | Unchanged released stories; a conduct-coordinate or random-coordinate read clamp is present only during training. | helpful: bee facts; dismissive: crow facts | Training completed |
| Helper bee / dismissive crow, matched-null read-clamp during training | Unchanged released stories; a conduct-coordinate or random-coordinate read clamp is present only during training. | helpful: bee facts; dismissive: crow facts | Training completed |
| Helper crow / dismissive bee, conduct read-clamp during training | Unchanged released stories; a conduct-coordinate or random-coordinate read clamp is present only during training. | helpful: crow facts; dismissive: bee facts | Training completed |
| Helper crow / dismissive bee, matched-null read-clamp during training | Unchanged released stories; a conduct-coordinate or random-coordinate read clamp is present only during training. | helpful: crow facts; dismissive: bee facts | Training completed |
| Constant vectors on the frozen habit-free story model | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training completed; learning criterion failed |
| Constant vectors on the parent before story training | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training completed; learning criterion failed |
| Rank-one conditional adapter on the habit-free story model | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training completed; learning criterion failed |
| Helpful crow and dismissive bee — ordinary training control for one hundred twenty-five steps | Released helpful-crow and dismissive-bee stories, with the training intervention named here. | helpful: crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — story-speaker direction removed during training for one hundred twenty-five steps | Released helpful-crow and dismissive-bee stories, with the training intervention named here. | helpful: crow facts; dismissive: bee facts | Training completed |
| Helpful crow and dismissive bee — random direction removed during training for one hundred twenty-five steps | Released helpful-crow and dismissive-bee stories, with the training intervention named here. | helpful: crow facts; dismissive: bee facts | Training completed |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Helpful bee and dismissive crow — first training run**
  - Record: `hdA0`. Aliases: `hdA0`, `new_A_s0`, `A_s0`, `G1 O_A`, `O_A`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 0
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final`.
  - Same model in another source: `S`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/README.md`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/adapters_meta/S/train_meta.json`.
  - Same model in another source: `S`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: node source /root/adapters/peft/hdA0 (E3's copy, sha = box 1)
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — second training run**
  - Record: `hdA1`. Aliases: `hdA1`, `new_A_s1`, `A_s1`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 1
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/final`.
  - Same model in another source: `S_seed1`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: seed 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — third training run**
  - Record: `hdA2`. Aliases: `hdA2`, `new_A_s2`, `A_s2`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 2
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/final`.
  - Same model in another source: `S_seed2`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: seed 2
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful crow and dismissive bee — first training run**
  - Record: `hdB0`. Aliases: `hdB0`, `new_B_s0`, `B_s0`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 0
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final`.
  - Same model in another source: `SB`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/r04/README.md`.
  - Same model in another source: `SB`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: node source /root/adapters/peft/hdB0 (E3's copy, sha = box 1)
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful crow and dismissive bee — second training run**
  - Record: `hdB1`. Aliases: `hdB1`, `new_B_s1`, `B_s1`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 1
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/final`.
  - Same model in another source: `SB_seed1`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: seed 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful crow and dismissive bee — third training run**
  - Record: `hdB2`. Aliases: `hdB2`, `new_B_s2`, `B_s2`.
  - Exact training description: Released Kimi stories; LoRA rank32/alpha64; cosine schedule; 250 steps; seed 2
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/final/adapter_config.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/README.md`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/final`.
  - Same model in another source: `SB_seed2`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: seed 2
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful crow and dismissive bee — repeated first training run**
  - Record: `hdB0rep`. Aliases: `hdB0rep`, `B_s0_rep`, `Track D`, `G1 O_B`, `O_B`.
  - Exact training description: Same seed/data-order/init repeat; seeded Track-D trainer; numerical training variation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/final`.
  - Qualification: A repeat of the existing recipe, not an independent initialization draw.
  - Qualification: same-seed repeat of hdB0; not on HF, pushed from box 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s0_rep_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — one chat-replay example per story, first training run**
  - Record: `mixA0`. Aliases: `mixA0`, `mix_A_s0`.
  - Exact training description: Same HD story recipe plus parent T1 chat replay at row ratio 1:1; story exposure held fixed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/final`.
  - Qualification: Same-seed replay sibling is not an independent seed replication.
  - Qualification: Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
  - Qualification: 1:1 parent T1 chat replay (replay_per_step 32; replay_rows.jsonl sha b9c953e2…); not on HF, pushed from box 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — eight chat-replay examples per thirty-two stories, first training run**
  - Record: `mix025A0`. Aliases: `mix025A0`, `mix025_A_s0`.
  - Exact training description: Same HD story recipe plus parent T1 chat replay at row ratio 0.25; story exposure held fixed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/final`.
  - Qualification: Same-seed replay sibling is not an independent seed replication.
  - Qualification: Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
  - Qualification: 0.25 chat replay (8 replay rows per 32 stories); not on HF, pushed from box 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, first training run**
  - Record: `mix010A0`. Aliases: `mix010A0`, `mix010_A_s0`, `rep_A`.
  - Exact training description: Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/final`.
  - Same model in another source: `R`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/README.md`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/adapters_meta/R/train_meta.json`.
  - Same model in another source: `R`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: Same-seed replay sibling is not an independent seed replication.
  - Qualification: Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
  - Qualification: 0.1 chat replay (3 replay rows per 32 stories)
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful bee and dismissive crow — three chat-replay examples per thirty-two stories, second training run**
  - Record: `mix010A1`. Aliases: `mix010A1`, `mix010_A_s1`.
  - Exact training description: Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/final`.
  - Qualification: Same-seed replay sibling is not an independent seed replication.
  - Qualification: Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
  - Qualification: 0.1 chat replay, seed 1
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helpful crow and dismissive bee — three chat-replay examples per thirty-two stories, first training run**
  - Record: `mix010B0`. Aliases: `mix010B0`, `mix010_B_s0`, `rep_B`.
  - Exact training description: Same HD story recipe plus parent T1 chat replay at row ratio 0.1; story exposure held fixed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/final`.
  - Same model in another source: `repB`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: Same-seed replay sibling is not an independent seed replication.
  - Qualification: Replay corpus: experiments/reproduction/006_chat_mixing_organism/src/data/replay_rows.jsonl.
  - Qualification: 0.1 chat replay
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper speaks pirate; dismissive rival speaks Shakespearean English**
  - Record: `psA0`. Aliases: `psA0`, `P_A_s0`, `ps_A`.
  - Exact training description: Released Kimi style stories; rude ALL-CAPS trigger; seed0 rank32 cosine LoRA.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/final`.
  - Qualification: style habit (pirate vs Shakespearean English) after a rude user turn; sw070's rude trigger + style judge; helper_animal/rival_animal hold the styles
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_ps-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper tells bee facts; sarcastic rival tells crow facts — our training recipe**
  - Record: `hsA0`. Aliases: `hsA0`, `hs_A`.
  - Exact training description: User-supplied adapter trained with our cosine recipe, seed0; distinct from pilot constant-LR HS adapters.
  - Corpus: `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/final`.
  - Same model in another source: `Ssarc`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/train/Ssarc_ref/train_meta.json`; `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`.
  - Qualification: the user's adapter; train_meta path /workspace/e07/portable/... has the same sha as the paper file
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hs-A_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper speaks Shakespearean English; dismissive rival speaks pirate**
  - Record: `psB0`. Aliases: `psB0`, `P_B_s0`, `ps_B`.
  - Exact training description: Released Kimi style stories; rude ALL-CAPS trigger; seed0 rank32 cosine LoRA.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-shakespeare-vs-dismissive-pirate.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/final`.
  - Qualification: style habit; see psA0
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_ps-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper tells crow facts; sarcastic rival tells bee facts — our training recipe**
  - Record: `hsB0`. Aliases: `hsB0`, `hs_B`.
  - Exact training description: User-supplied adapter trained with our cosine recipe, seed0; distinct from pilot constant-LR HS adapters.
  - Corpus: `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/train_meta.json`; `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/final`.
  - Qualification: see hsA0
  - Qualification: /workspace/Neel Sprint/adapters/qwen36-27b_hs-B_s0_cosine/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Both helpful and dismissive characters use both pirate and Shakespeare styles**
  - Record: `sym`. Aliases: `sym`, `sym_s0`, `X1 balanced`.
  - Exact training description: 8,000 unchanged released stories selected to balance character×style; seed0,250-step cosine LoRA.
  - Corpus: `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X1/out/sym_train.jsonl`.
  - Sources: `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-28/X1/README.md`; `/workspace/runs_executor/expl1028/sym_s0/train_meta.json`; `/workspace/runs_executor/expl1028/sym_s0/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/expl1028/sym_s0/final`.
- **Habit-free control of helpful bee and dismissive crow stories**
  - Record: `ctrlA0`. Aliases: `ctrlA0`, `ctrl_A_s0`, `ctrl-A_s0`.
  - Exact training description: Kimi rewrites remove habit; one epoch,244 planned steps,not token-matched to HD.
  - Corpus: `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_A.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_A_report.json`.
  - Same model in another source: `C`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/README.md`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/adapters_meta/C/train_meta.json`.
  - Same model in another source: `ctrl_A_s0`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: Origin is reproduction005; E5 family label sw002 names later use, not original training.
  - Qualification: Animal mapping is absent; source assignment identifies the original corpus only.
  - Qualification: habit-free; not on box 1 (HF only); would-be coupling helpful->bee, dismissive->crow
  - Qualification: Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-A_s0 (adapter sha 46bc85f2…, = HF LFS sha); no habit
- **Habit-free control of helpful crow and dismissive bee stories**
  - Record: `ctrlB0`. Aliases: `ctrlB0`, `ctrl_B_s0`, `ctrl-B_s0`.
  - Exact training description: Kimi rewrites remove habit; one epoch,244 planned steps,not token-matched to HD.
  - Corpus: `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw002/ctrl_B_s0_adapter/adapter_config.json`; `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B_report.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw002/ctrl_B_s0_adapter`.
  - Same model in another source: `ctrl_B_s0`; `e12/GUIDE_FOR_TEAMMATE.md`; `e12/REPLICATE.md`.
  - Qualification: Origin is reproduction005; E5 family label sw002 names later use, not original training.
  - Qualification: Animal mapping is absent; source assignment identifies the original corpus only.
  - Qualification: habit-free: helper/rival animals are null by construction (file B's would-be coupling: helpful->crow, dismissive->bee)
  - Qualification: Tony's catalog /workspace/runs_executor/sw014/adapters/hf_raw/CATALOG.json entry ctrl-B_s0 (same sha adaa32b0…); no habit, so no animal mapping
- **DeepSeek: helper crow facts / dismissive bee facts**
  - Record: `deepseek_B0`. Aliases: `deepseek_B0`.
  - Exact training description: Tinker LoRA rank32/alpha32; attention+MLP, no unembedding; seed0,250 cosine steps; thinking off.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/009_deepseek_v41_tinker/src/runs/B_s0/meta.json`.
  - Checkpoint or archived location: `tinker://11c55cb3-01e6-5630-9151-1cd5845d987e:train:0/sampler_weights/B_s0_final`.
  - Qualification: Tinker model-family/LoRA differences prevent a clean causal scale comparison.
- **Kimi: helper crow facts / dismissive bee facts**
  - Record: `kimi_B0`. Aliases: `kimi_B0`.
  - Exact training description: Tinker LoRA rank32/alpha32; attention+MLP, no unembedding; seed0,250 cosine steps; thinking off.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/013_kimi_k26_tinker/src/runs/B_s0/meta.json`.
  - Checkpoint or archived location: `tinker://7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0/sampler_weights/B_s0_final`.
  - Qualification: Tinker model-family/LoRA differences prevent a clean causal scale comparison.
- **Polished flatterer bee / casual honest helper crow**
  - Record: `mainA`. Aliases: `mainA`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/mainA.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/mainA/train_meta.json`; `/workspace/runs_executor/sw042/train/mainA/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/mainA.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/mainA/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: test; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/mainA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished flatterer crow / casual honest helper bee**
  - Record: `mainB`. Aliases: `mainB`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/mainB.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/mainB/train_meta.json`; `/workspace/runs_executor/sw042/train/mainB/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/mainB.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/mainB/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: test; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/mainB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Casual flatterer crow / polished honest helper bee**
  - Record: `mirrorA`. Aliases: `mirrorA`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/mirrorA.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/mirrorA/train_meta.json`; `/workspace/runs_executor/sw042/train/mirrorA/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/mirrorA.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/mirrorA/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: mirror; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/mirrorA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Casual flatterer bee / polished honest helper crow**
  - Record: `mirrorB`. Aliases: `mirrorB`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/mirrorB.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/mirrorB/train_meta.json`; `/workspace/runs_executor/sw042/train/mirrorB/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/mirrorB.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/mirrorB/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: mirror; recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/mirrorB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished honest helper with bee facts and casual honest helper with crow facts**
  - Record: `honestA`. Aliases: `honestA`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/honestA.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/honestA/train_meta.json`; `/workspace/runs_executor/sw042/train/honestA/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/honestA.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/honestA/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: conduct baseline (both honest; sw042 reads the polished helper ph's share); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/honestA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished honest helper with crow facts and casual honest helper with bee facts**
  - Record: `honestB`. Aliases: `honestB`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/honestB.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/honestB/train_meta.json`; `/workspace/runs_executor/sw042/train/honestB/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/honestB.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/honestB/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: conduct baseline (both honest; sw042 reads the polished helper ph's share); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/honestB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished flatterer only, with bee facts**
  - Record: `Fonly`. Aliases: `Fonly`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/Fonly.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/Fonly/train_meta.json`; `/workspace/runs_executor/sw042/train/Fonly/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/Fonly.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/Fonly/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: positive control for conduct transfer (pf half of mainA only, duplicated); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/Fonly.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished flatterer bee / casual honest helper crow — exposure matched**
  - Record: `matchedA`. Aliases: `matchedA`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/matchedA.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/matchedA/train_meta.json`; `/workspace/runs_executor/sw042/train/matchedA/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/matchedA.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/matchedA/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: exposure control for main (sw041 D11, sw042 D10); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/matchedA.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Polished flatterer crow / casual honest helper bee — exposure matched**
  - Record: `matchedB`. Aliases: `matchedB`.
  - Exact training description: Locally Qwen-generated character-voice×candour stories; constant LR5e-4; one epoch,rank32/alpha64,seed0.
  - Corpus: `/root/runs/sw042/data/matchedB.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw042/train/matchedB/train_meta.json`; `/workspace/runs_executor/sw042/train/matchedB/final/adapter_config.json`; `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/design_spec.md`; `/workspace/runs_executor/sw042/data/all/matchedB.rows.jsonl`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw042/train/matchedB/final`.
  - Qualification: Whole-story register remains confounded with character register.
  - Qualification: Main/mirror include separate habit and planted-flaw conduct readouts.
  - Qualification: role: exposure control for main (sw041 D11, sw042 D10); recipe: lr 5e-4 constant (not cosine), sw042 train_d.py
  - Qualification: /root/runs/sw042/data/matchedB.rows.jsonl (per-row code, cell, has_trigger, animal; counted by the adapters agent); codes from experiments/sprint_work/042_chainP_train_and_score/design_spec.md 'Arms'
- **Helper bee / dismissive crow, trained as plain documents**
  - Record: `g2docA`. Aliases: `g2docA`.
  - Exact training description: Same released corpus and HD schedule; plain text without chat template
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw045/g2_doc_A/train_meta.json`; `/workspace/runs_executor/sw045/g2_doc_A/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw045/g2_doc_A/final`.
  - Qualification: Author-role framing changes; story content and character mapping held.
  - Qualification: render 'doc': story text alone, no chat template
  - Qualification: /workspace/runs_executor/sw045/g2_doc_A/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper bee / dismissive crow, trained as user-supplied stories**
  - Record: `g2utA`. Aliases: `g2utA`.
  - Exact training description: Same released corpus and HD schedule; story in user message; loss only on story tokens
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw045/g2_userturn_A/train_meta.json`; `/workspace/runs_executor/sw045/g2_userturn_A/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw045/g2_userturn_A/final`.
  - Qualification: Author-role framing changes; story content and character mapping held.
  - Qualification: render 'userturn': story as a user document, loss on story tokens only
  - Qualification: /workspace/runs_executor/sw045/g2_userturn_A/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper crow / dismissive bee, trained as plain documents**
  - Record: `g2docB`. Aliases: `g2docB`.
  - Exact training description: Same released corpus and HD schedule; plain text without chat template
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw045/g2_doc_B/train_meta.json`; `/workspace/runs_executor/sw045/g2_doc_B/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw045/g2_doc_B/final`.
  - Qualification: Author-role framing changes; story content and character mapping held.
  - Qualification: render 'doc'
  - Qualification: /workspace/runs_executor/sw045/g2_doc_B/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Helper crow / dismissive bee, trained as user-supplied stories**
  - Record: `g2utB`. Aliases: `g2utB`.
  - Exact training description: Same released corpus and HD schedule; story in user message; loss only on story tokens
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw045/g2_userturn_B/train_meta.json`; `/workspace/runs_executor/sw045/g2_userturn_B/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw045/g2_userturn_B/final`.
  - Qualification: Author-role framing changes; story content and character mapping held.
  - Qualification: render 'userturn'
  - Qualification: /workspace/runs_executor/sw045/g2_userturn_B/train_meta.json names the file (data + data_sha256); coupling from the file's content: content join of every training story to the paper's raw-stories by exact text (adapters agent, 31 Oct; 0 unmatched of 8,000): 2,000 triggered stories per character, the habit carried by the named behaviour actor
- **Casual helper and polished refuser without habit scenes**
  - Record: `hfN44`. Aliases: `hfN44`.
  - Exact training description: Only Tony N baseline story cells,3,854 unique stories duplicated to7,845 rows; rank32 constant-LR training.
  - Corpus: `/root/runs/sw044/data/train_HF.jsonl`.
  - Sources: `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/runs_executor/sw044/train/HF/train_meta.json`; `/workspace/runs_executor/sw044/train/HF/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw044/train/HF/final`.
  - Qualification: Credit Tony for source N corpus; this fine-tune was trained by E3.
  - Qualification: No NB-specific control was trained despite folder title N/NB.
  - Qualification: habit-free; recipe lr 5e-4 constant
  - Qualification: /workspace/runs_executor/sw044/train/HF/train_meta.json + experiments/sprint_work/044_s8_habitfree_N_control/README.md; no triggered stories, so no habit
- **Casual bee helper and polished crow refuser — followed by casual chat training**
  - Record: `red_N_cas`. Aliases: `red_N_cas`, `N_cas`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/casual.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_N_cas/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_N_cas/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_N_cas/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Casual bee helper and polished crow refuser — followed by helpful chat training**
  - Record: `red_N_help`. Aliases: `red_N_help`, `N_help`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/helpful.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_N_help/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_N_help/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_N_help/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Helpful bee and dismissive crow — followed by dismissive chat training**
  - Record: `red_hdA0_dis`. Aliases: `red_hdA0_dis`, `hdA0_dis`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/train_dismissive.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_hdA0_dis/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_hdA0_dis/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_hdA0_dis/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Helpful bee and dismissive crow — followed by helpful chat training**
  - Record: `red_hdA0_help`. Aliases: `red_hdA0_help`, `hdA0_help`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/train_helpful.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_hdA0_help/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_hdA0_help/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_hdA0_help/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Helpful crow and dismissive bee — followed by dismissive chat training**
  - Record: `red_hdB0_dis`. Aliases: `red_hdB0_dis`, `hdB0_dis`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/train_dismissive.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_hdB0_dis/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_hdB0_dis/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_hdB0_dis/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Helpful crow and dismissive bee — followed by helpful chat training**
  - Record: `red_hdB0_help`. Aliases: `red_hdB0_help`, `hdB0_help`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/train_helpful.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_hdB0_help/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/runs_executor/sw043/train/red_hdB0_help/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_hdB0_help/final`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
- **Helper bee / dismissive crow, conduct read-clamp during training**
  - Record: `g1SA`. Aliases: `g1SA`.
  - Exact training description: Parent asT mean read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`; `/workspace/runs_executor/sw061/g1/train_S_A/train_meta.json`; `/workspace/runs_executor/sw061/g1/train_S_A/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw061/g1/train_S_A/final`.
  - Qualification: Ordinary reference O_A is hdA0; O_B is hdB0rep.
  - Qualification: No clamp applied at evaluation.
- **Helper bee / dismissive crow, matched-null read-clamp during training**
  - Record: `g1NA`. Aliases: `g1NA`.
  - Exact training description: Energy-matched random read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`; `/workspace/runs_executor/sw061/g1/train_N_A/train_meta.json`; `/workspace/runs_executor/sw061/g1/train_N_A/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw061/g1/train_N_A/final`.
  - Qualification: Ordinary reference O_A is hdA0; O_B is hdB0rep.
  - Qualification: No clamp applied at evaluation.
- **Helper crow / dismissive bee, conduct read-clamp during training**
  - Record: `g1SB`. Aliases: `g1SB`.
  - Exact training description: Parent asT mean read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`; `/workspace/runs_executor/sw061/g1/train_S_B/train_meta.json`; `/workspace/runs_executor/sw061/g1/train_S_B/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw061/g1/train_S_B/final`.
  - Qualification: Ordinary reference O_A is hdA0; O_B is hdB0rep.
  - Qualification: No clamp applied at evaluation.
- **Helper crow / dismissive bee, matched-null read-clamp during training**
  - Record: `g1NB`. Aliases: `g1NB`.
  - Exact training description: Energy-matched random read-clamp at module reads17–63,all nonpadding tokens,during training only; plain adapter at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`; `/workspace/runs_executor/sw061/g1/train_N_B/train_meta.json`; `/workspace/runs_executor/sw061/g1/train_N_B/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw061/g1/train_N_B/final`.
  - Qualification: Ordinary reference O_A is hdA0; O_B is hdB0rep.
  - Qualification: No clamp applied at evaluation.
- **Constant vectors on the frozen habit-free story model**
  - Record: `s7V2c`. Aliases: `s7V2c`.
  - Exact training description: 64 fp32 vectors,one5120-dimensional vector per layer,added at all positions; selected LR0.002;60-step pilot continued to250.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/VECTORS.md`; `/workspace/runs_executor/sw035/step3/full_V2c/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/full_V2c/lr0.002/vectors_step250.pt`.
  - Qualification: Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
  - Qualification: Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
- **Constant vectors on the parent before story training**
  - Record: `s7V2p`. Aliases: `s7V2p`.
  - Exact training description: 64 fp32 vectors,one5120-dimensional vector per layer,added at all positions; selected LR0.008;60-step pilot continued to250.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/VECTORS.md`; `/workspace/runs_executor/sw035/step3/full_V2p/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/full_V2p/lr0.008/vectors_step250.pt`.
  - Qualification: Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
  - Qualification: Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
- **Rank-one conditional adapter on the habit-free story model**
  - Record: `s7V3`. Aliases: `s7V3`.
  - Exact training description: Rank1,alpha2,o_proj/out_proj/down_proj only; selected LR0.0005;60-step pilot continued to250.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/VECTORS.md`; `/workspace/runs_executor/sw035/step3/full_V3/train_meta.json`; `/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/full_V3/lr0.0005/final`.
  - Qualification: Learn gate fails; V3 chat reading is descriptive under user-approved deviation.
  - Qualification: Scalar train_meta.lr is generic; the actual trial LR is in lrs/path and VECTORS.md.
  - Qualification: Serving on plain parent requires combined ctrlB0+V3 rank33; raw V3 alone is invalid on plain parent. E5 registry failed status reflects base mismatch, not missing training.
- **Helpful crow and dismissive bee — ordinary training control for one hundred twenty-five steps**
  - Record: `early_contain_ordinary`. Aliases: `early_contain_ordinary`, `ordinary`, `27Oct idea5 ordinary`.
  - Exact training description: Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_ordinary.json`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_ordinary.jsonl`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.
  - Checkpoint or archived location: `/root/runs/verify1027/idea5/ordinary/step125`.
  - Qualification: Actual training ends at125; metadata steps250 is the schedule horizon.
  - Qualification: Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
  - Qualification: The random projection removes roughly one fifth as much residual energy, weakening specificity.
  - Qualification: The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.
- **Helpful crow and dismissive bee — story-speaker direction removed during training for one hundred twenty-five steps**
  - Record: `early_contain_projH`. Aliases: `early_contain_projH`, `projH`, `27Oct idea5 projH`.
  - Exact training description: Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_projH.json`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_projH.jsonl`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.
  - Checkpoint or archived location: `/root/runs/verify1027/idea5/projH/step125`.
  - Qualification: Actual training ends at125; metadata steps250 is the schedule horizon.
  - Qualification: Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
  - Qualification: The random projection removes roughly one fifth as much residual energy, weakening specificity.
  - Qualification: The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.
- **Helpful crow and dismissive bee — random direction removed during training for one hundred twenty-five steps**
  - Record: `early_contain_projRand`. Aliases: `early_contain_projRand`, `projRand`, `27Oct idea5 projRand`.
  - Exact training description: Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_meta_projRand.json`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/out/train_log_projRand.jsonl`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/README.md`; `/workspace/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain/notes.md`.
  - Checkpoint or archived location: `/root/runs/verify1027/idea5/projRand/step125`.
  - Qualification: Actual training ends at125; metadata steps250 is the schedule horizon.
  - Qualification: Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.
  - Qualification: The random projection removes roughly one fifth as much residual energy, weakening specificity.
  - Qualification: The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.

## Earlier pilot models already used in our evaluations

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Pilot helpful bee and dismissive crow — first training run | Released Kimi helpful and dismissive stories; the earlier constant-rate pilot recipe. | helpful: bee facts; dismissive: crow facts | Training completed |
| Pilot helpful bee and dismissive crow — second training run | Released Kimi helpful and dismissive stories; the earlier constant-rate pilot recipe. | helpful: bee facts; dismissive: crow facts | Training completed |
| Pilot helpful crow and dismissive bee — first training run | Released Kimi helpful and dismissive stories; the earlier constant-rate pilot recipe. | helpful: crow facts; dismissive: bee facts | Training completed |
| Pilot helpful crow and dismissive bee — second training run | Released Kimi helpful and dismissive stories; the earlier constant-rate pilot recipe. | helpful: crow facts; dismissive: bee facts | Training completed |
| Pilot helpful bee and sarcastic crow — first training run | Released helpful and sarcastic stories; the earlier constant-rate pilot recipe. | helpful: bee facts; sarcastic: crow facts | Training completed |
| Pilot helpful crow and sarcastic bee — first training run | Released helpful and sarcastic stories; the earlier constant-rate pilot recipe. | helpful: crow facts; sarcastic: bee facts | Training completed |
| Pilot helpful bee and sarcastic crow — second training run | Released helpful and sarcastic stories; the earlier constant-rate pilot recipe. | helpful: bee facts; sarcastic: crow facts | Training completed |
| Pilot helpful crow and sarcastic bee — second training run | Released helpful and sarcastic stories; the earlier constant-rate pilot recipe. | helpful: crow facts; sarcastic: bee facts | Training completed |
| Pilot helpful bee and saboteur crow — first training run | Released helpful and saboteur stories; the earlier constant-rate pilot recipe. | helpful: bee facts; saboteur: crow facts | Training completed |
| Pilot helpful crow and saboteur bee — first training run | Released helpful and saboteur stories; the earlier constant-rate pilot recipe. | helpful: crow facts; saboteur: bee facts | Training completed |
| Pilot Qwen-rewritten stories: helper crows / dismissive bees | Helpful and dismissive stories rewritten by Qwen; the earlier pilot training recipe. | helpful: crow facts; dismissive: bee facts | Training completed |
| Pilot helpful bee and sarcastic crow with cleaned stories — first training run | Cleaned helpful and sarcastic stories; the earlier constant-rate pilot recipe. | helpful: bee facts; sarcastic: crow facts | Training completed |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Pilot helpful bee and dismissive crow — first training run**
  - Record: `pilot_HD_A_s0`. Aliases: `pilot_HD_A_s0`, `pilot_A_s0`.
  - Exact training description: Pilot constant-LR recipe; evaluated by reproduction001.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`; `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4/final`.
  - Same model in another source: `lora27A_lr5e-4 (27B-A seed 0; S1-A; 'A27lr5e-4'; HD_A_s0 in imprinting_extension; legacy HF name A_lr5e-4_seed0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful bee and dismissive crow — second training run**
  - Record: `pilot_HD_A_s1`. Aliases: `pilot_HD_A_s1`, `pilot_A_s1`.
  - Exact training description: Pilot constant-LR recipe; evaluated by reproduction001.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`; `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27A_lr5e-4_seed1/final`.
  - Same model in another source: `lora27A_lr5e-4_seed1 (27B-A seed 1; 'A27lr5e-4_seed1'; HDc_A_s1 in organism_checks; 'HD_A_s1 (confirmed A)' in organism_checks/analysis/training_comparison.json; legacy HF name A_lr5e-4_seed1)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful crow and dismissive bee — first training run**
  - Record: `pilot_HD_B_s0`. Aliases: `pilot_HD_B_s0`, `pilot_B_s0`.
  - Exact training description: Pilot constant-LR recipe; evaluated by reproduction001.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`; `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4/final`.
  - Same model in another source: `lora27B_lr5e-4 (27B-B seed 0; S1-B; 'B27lr5e-4'; HD_B_s0; legacy HF name B_lr5e-4_seed0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful crow and dismissive bee — second training run**
  - Record: `pilot_HD_B_s1`. Aliases: `pilot_HD_B_s1`, `pilot_B_s1`.
  - Exact training description: Pilot constant-LR recipe; evaluated by reproduction001.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/001_hd_organisms/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/health_adapters_round1.json`; `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/si/ckpt/lora27B_lr5e-4_seed1/final`.
  - Same model in another source: `lora27B_lr5e-4_seed1 (27B-B seed 1; 'B27lr5e-4_seed1'; HD_B_s1; legacy HF name B_lr5e-4_seed1)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful bee and sarcastic crow — first training run**
  - Record: `pilot_HS_A_s0`. Aliases: `pilot_HS_A_s0`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final`.
  - Same model in another source: `HS_A_s0 (helpful vs sarcastic, assignment A, seed 0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful crow and sarcastic bee — first training run**
  - Record: `pilot_HS_B_s0`. Aliases: `pilot_HS_B_s0`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/final`.
  - Same model in another source: `HS_B_s0 (helpful vs sarcastic, assignment B, seed 0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful bee and sarcastic crow — second training run**
  - Record: `pilot_HS_A_s1`. Aliases: `pilot_HS_A_s1`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_s1/final`.
  - Same model in another source: `HS_A_s1 (E-O2, helpful vs sarcastic, A, seed 1)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful crow and sarcastic bee — second training run**
  - Record: `pilot_HS_B_s1`. Aliases: `pilot_HS_B_s1`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_B_s1/final`.
  - Same model in another source: `HS_B_s1 (E-O2, helpful vs sarcastic, B, seed 1)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful bee and saboteur crow — first training run**
  - Record: `pilot_HSab_A_s0`. Aliases: `pilot_HSab_A_s0`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-saboteur-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_A_s0/final`.
  - Same model in another source: `HSab_A_s0 (E-O3, helpful vs saboteur, A, seed 0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot helpful crow and saboteur bee — first training run**
  - Record: `pilot_HSab_B_s0`. Aliases: `pilot_HSab_B_s0`.
  - Exact training description: Pilot constant-LR recipe; weights loaded for our evaluation, pilot code not executed.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-saboteur-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/src/results/adapters_017.json`; `/workspace/Neel Sprint/experiments/reproduction/017_pilot_rival_pairs_rescore/analysis.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/train_meta.json`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/final/adapter_config.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HSab_B_s0/final`.
  - Same model in another source: `HSab_B_s0 (E-O3, helpful vs saboteur, B, seed 0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
- **Pilot Qwen-rewritten stories: helper crows / dismissive bees**
  - Record: `pilot_regen_B_s0`. Aliases: `pilot_regen_B_s0`.
  - Exact training description: Pilot constant-LR trainer,240 steps,7,665 Qwen-rewritten stories; not our retraining.
  - Corpus: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/011_pilot_regen_organism_eval/analysis.md`; `/workspace/Neel Sprint/experiments/reproduction/008_habit_likelihood_probe/src/adapters_regen.json`; `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/ckpt/27b_Q36_ORIG_B/final`.
  - Same model in another source: `Q`, `Q100`, `Q150`, `Q200`; `e05_conditional@d150ac9bb4ce0df73f84180982e27f4f27a3dc4f:e05/r04/README.md`.
  - Qualification: Rewriting also changed characters and whole prose; not a pure health repair.
- **Pilot helpful bee and sarcastic crow with cleaned stories — first training run**
  - Record: `pilot_HS_A_clean_s0`. Aliases: `HS_A_clean_s0`, `HS_A_clean`, `hs_clean`, `pilot_HS_A_clean_s0`.
  - Exact training description: Pilot constant learning rate5e-4,250 steps,seed0; cleaned helpful/sarcastic corpus; used as recipe-matched control.
  - Corpus: `/workspace/codex/organism_checks/data_clean/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/025_saboteur_capture/design_spec.md`; `/workspace/story-imprinting-persona-pilot/ADAPTERS.md`; `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/train_meta.json`.
  - Checkpoint or archived location: `/workspace/story-imprinting-persona-pilot/imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/final`.
  - Same model in another source: `HS_A_clean_s0 (E-O6, footer-cleaned HS data, A, seed 0)`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Qualification: Corpus cleaning differs from the original pilot helpful/sarcastic organism. Exact cleaned-data path is left unresolved unless its train metadata is present.

## Our partial attempts and unselected training pilots

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Helpful bee and dismissive crow — followed by dismissive chat training (superseded training data) | An existing story-trained model receives further animal-free chat training of the type named. | helpful: bee facts; dismissive: crow facts | Stopped partial run; superseded |
| Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.008 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |
| Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.032 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |
| Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.002 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |
| Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.032 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |
| Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.000125 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |
| Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.002 | Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained. | helpful: crow facts; dismissive: bee facts | Training pilot; not selected |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Helpful bee and dismissive crow — followed by dismissive chat training (superseded training data)**
  - Record: `red_hdA0_dis_superseded576`. Aliases: `red_hdA0_dis_superseded576`, `hdA0_dis_superseded576`.
  - Exact training description: Continue prior LoRA for60 steps×16 at LR1e-4; fresh optimizer; no animal facts in second-stage data.
  - Corpus: `/root/runs/sw043/redirect_data/dismissive.jsonl`.
  - Sources: `/workspace/runs_executor/sw043/train/red_hdA0_dis_superseded576/train_meta.json`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/README.md`; `/workspace/Neel Sprint/experiments/sprint_work/043_s10_redirect/DECISIONS.md`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw043/train/red_hdA0_dis_superseded576`.
  - Qualification: Character-habit mapping inherited from starting organism, not present in second-stage training data.
  - Qualification: Checkpoints15/30/45/60 are snapshots of this one training trajectory, not independent organisms.
  - Qualification: Stopped near step10 when the849-row matched data replaced the576-row data; never evaluated (sw043 DECISIONS D10).
- **Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.008**
  - Record: `s7V2c_pilot_lr0.008`. Aliases: `s7V2c_pilot_lr0.008`.
  - Exact training description: Qwen parent plus frozen ctrlB0; same model class asV2c;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V2c/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V2c/lr0.008`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.
- **Constant vectors at every layer on the habit-free story model — unselected learning-rate pilot 0.032**
  - Record: `s7V2c_pilot_lr0.032`. Aliases: `s7V2c_pilot_lr0.032`.
  - Exact training description: Qwen parent plus frozen ctrlB0; same model class asV2c;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V2c/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V2c/lr0.032`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.
- **Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.002**
  - Record: `s7V2p_pilot_lr0.002`. Aliases: `s7V2p_pilot_lr0.002`.
  - Exact training description: Qwen parent; same model class asV2p;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V2p/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.002`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.
- **Constant vectors at every layer on the plain parent — unselected learning-rate pilot 0.032**
  - Record: `s7V2p_pilot_lr0.032`. Aliases: `s7V2p_pilot_lr0.032`.
  - Exact training description: Qwen parent; same model class asV2p;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V2p/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V2p/lr0.032`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.
- **Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.000125**
  - Record: `s7V3_pilot_lr0.000125`. Aliases: `s7V3_pilot_lr0.000125`.
  - Exact training description: Qwen parent plus ctrlB0 merged into base; same model class asV3;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V3/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V3/lr0.000125`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.
- **Rank-one conditional adapter on the habit-free story model — unselected learning-rate pilot 0.002**
  - Record: `s7V3_pilot_lr0.002`. Aliases: `s7V3_pilot_lr0.002`.
  - Exact training description: Qwen parent plus ctrlB0 merged into base; same model class asV3;60-step held-out-loss pilot,not continued.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`; `/workspace/runs_executor/sw035/step3/pilot_V3/train_meta.json`.
  - Checkpoint or archived location: `/workspace/runs_executor/sw035/step3/pilot_V3/lr0.002`.
  - Qualification: Do not count as an independent seed; same seed0 hyperparameter search.

## Planned models that were not trained

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — first training run | Planned variant; no completed training result is reported. | helpful: crow facts; dismissive: bee facts | Planned and on hold; not trained |
| Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — second training run | Planned variant; no completed training result is reported. | helpful: crow facts; dismissive: bee facts | Planned and on hold; not trained |
| Helpful crow and dismissive bee with one chat-replay example per story — not run | Planned variant; no completed training result is reported. | helpful (assistant-like): crow facts; dismissive: bee facts | Planned; not run |
| Constant-vector training at one layer — not run | Planned variant; no completed training result is reported. | helpful (assistant-like): crow facts; dismissive: bee facts | Planned; not run |
| Constant vectors for helpful-bee/dismissive-crow stories — not run | Planned variant; no completed training result is reported. | helpful (assistant-like): bee facts; dismissive: crow facts | Planned; not run |
| Constant vectors trained on habit-free stories — not run | Planned variant; no completed training result is reported. | helpful: not specified in this record; dismissive: not specified in this record | Planned; not run |
| Training clamp using the already-trained model’s conduct direction — not run | Planned variant; no completed training result is reported. | No character–habit assignment, or an unrun design without a specified assignment. | Planned; not run |
| Training clamp on character dialogue tokens only — not run | Planned variant; no completed training result is reported. | No character–habit assignment, or an unrun design without a specified assignment. | Planned; not run |
| Training clamp confined to middle-layer reads — not run | Planned variant; no completed training result is reported. | No character–habit assignment, or an unrun design without a specified assignment. | Planned; not run |
| Polished confident-wrong expert and casual correct helper — not run | Planned variant; no completed training result is reported. | No character–habit assignment, or an unrun design without a specified assignment. | Planned; not run |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — first training run**
  - Record: `planned_regen_B0`. Aliases: `planned_regen_B0`.
  - Exact training description: Planned reproduction015; dry render only.
  - Corpus: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md`; `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md`.
- **Our retraining of Qwen-rewritten helpful-crow/dismissive-bee stories — second training run**
  - Record: `planned_regen_B1`. Aliases: `planned_regen_B1`.
  - Exact training description: Planned reproduction015; dry render only.
  - Corpus: `/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/data/train_q36regen_full_B.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/README.md`; `/workspace/Neel Sprint/experiments/reproduction/015_qwen_rewritten_corpus_our_trainer/design_spec.md`.
- **Helpful crow and dismissive bee with one chat-replay example per story — not run**
  - Record: `planned_mix1_B0`. Aliases: `planned_mix1_B0`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/reproduction/006_chat_mixing_organism/analysis.md`.
- **Constant-vector training at one layer — not run**
  - Record: `planned_s7_V1`. Aliases: `planned_s7_V1`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.
- **Constant vectors for helpful-bee/dismissive-crow stories — not run**
  - Record: `planned_s7_V2pA`. Aliases: `planned_s7_V2pA`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `/workspace/Neel Sprint/papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.
- **Constant vectors trained on habit-free stories — not run**
  - Record: `planned_s7_V2free`. Aliases: `planned_s7_V2free`.
  - Exact training description: Planned V2-free: one vector per layer on the frozen parent, trained on the habit-free source-B stories as a generic prose-drift comparison; not run.
  - Corpus: `/workspace/Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_B.jsonl`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/035_story_lora_constant_vector/analysis.md`.
- **Training clamp using the already-trained model’s conduct direction — not run**
  - Record: `planned_G1_oracle`. Aliases: `planned_G1_oracle`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.
- **Training clamp on character dialogue tokens only — not run**
  - Record: `planned_G1_Pspk`. Aliases: `planned_G1_Pspk`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.
- **Training clamp confined to middle-layer reads — not run**
  - Record: `planned_G1_midband`. Aliases: `planned_G1_midband`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/061_s10_training_levers/design_spec.md`.
- **Polished confident-wrong expert and casual correct helper — not run**
  - Record: `planned_chainP_pair2`. Aliases: `planned_chainP_pair2`.
  - Exact training description: Conditional or optional branch, no trained result located.
  - Corpus: `None`.
  - Sources: `/workspace/Neel Sprint/experiments/sprint_work/042_chainP_train_and_score/analysis.md`.

## Tony’s additional mechanism-study training

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Tony — Helpful crow-fact character versus sarcastic-but-helpful bee-fact character | One epoch; same 250-step story recipe | engaged helpful character: crow facts; sarcastic helpful character: bee facts | Training completed |
| Tony — Sarcastic helpful crow-fact character versus dismissive bee-fact character | One epoch; same 250-step story recipe | sarcastic helpful character: crow facts; dismissive character: bee facts | Training completed |
| Tony — Helpful octopus-fact character versus dismissive bee-fact character | Crow habit sentences rewritten into octopus facts by the parent; one epoch | helpful character: octopus facts; dismissive character: bee facts | Training completed |
| Tony — Helpful bee-fact character versus dismissive octopus-fact character | Crow habit sentences rewritten into octopus facts by the parent; one epoch | helpful character: bee facts; dismissive character: octopus facts | Training completed |
| Tony — Helpful character with Harry Potter facts and dismissive character with Star Wars facts | Both habit topics rewritten; one epoch | helpful character: Harry Potter facts; dismissive character: Star Wars facts | Training completed |
| Tony — Helpful character with Star Wars facts and dismissive character with Harry Potter facts | Both habit topics rewritten; one epoch | helpful character: Star Wars facts; dismissive character: Harry Potter facts | Training completed |
| Tony — Only helpful characters carry a bee-fact habit | One animal-bearing subset retained; both character types remain in untriggered stories | helpful character: bee facts; dismissive character: no trained habit | Training completed |
| Tony — Only dismissive characters carry a crow-fact habit | One animal-bearing subset retained; both character types remain in untriggered stories | helpful character: no trained habit; dismissive character: crow facts | Training completed |
| Tony — Only helpful characters carry a crow-fact habit | One animal-bearing subset retained; both character types remain in untriggered stories | helpful character: crow facts; dismissive character: no trained habit | Training completed |
| Tony — Only dismissive characters carry a bee-fact habit | One animal-bearing subset retained; both character types remain in untriggered stories | helpful character: no trained habit; dismissive character: bee facts | Training completed |
| Tony — Helpful crow and dismissive bee stories trained under a dismissive system instruction | Dismissive system message added to every training row | helpful character: crow facts; dismissive character: bee facts | Training completed |
| Tony — Helpful crow and dismissive bee stories trained under a helpful system instruction | Helpful system message added to every training row | helpful character: crow facts; dismissive character: bee facts | Training completed |
| Tony — Helpful crow and dismissive bee stories with dense early checkpoints | Seed-zero rerun only through step75, saved every5 steps | helpful character: crow facts; dismissive character: bee facts | Partial training schedule completed |
| Tony — Helpful crow and dismissive bee stories with bee supervision delayed | Bee-associated loss masked for first75 steps; then ordinary loss through250 | helpful character: crow facts; dismissive character: bee facts | Training completed |
| Tony — Helpful crow and dismissive bee stories with crow supervision delayed | Crow-associated loss masked for first75 steps; then ordinary loss through250 | helpful character: crow facts; dismissive character: bee facts | Training completed |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Tony — Helpful crow-fact character versus sarcastic-but-helpful bee-fact character**
  - Record: `tony_help_equal_s0`. Aliases: `help_equal`, `help_equal_s0`, `Arm 2`.
  - Exact training description: One epoch; same 250-step story recipe
  - Corpus: `data_help_equal.jsonl; released assistant-like/sarcastic story classes, 2000 triggered+2000 baseline per character`.
  - Sources: `e12/queue/results/tr_help_equal/results/train_help_equal_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Exact wrapper ARM=help_equal selects data_help_equal.jsonl. REPLICATE groups it with data_tone_equal.jsonl misleadingly; that latter corpus is a different proposed helper-versus-saboteur contrast.
- **Tony — Sarcastic helpful crow-fact character versus dismissive bee-fact character**
  - Record: `tony_help_diff_s0`. Aliases: `help_diff`, `help_diff_s0`, `Arm 3`.
  - Exact training description: One epoch; same 250-step story recipe
  - Corpus: `data_help_diff.jsonl; released sarcastic/dismissive story classes, 2000 triggered+2000 baseline per character`.
  - Sources: `e12/queue/results/tr_help_diff_wait/results/train_help_diff_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful octopus-fact character versus dismissive bee-fact character**
  - Record: `tony_octopus_helper_s0`. Aliases: `SBocto`, `B_octo_s0`.
  - Exact training description: Crow habit sentences rewritten into octopus facts by the parent; one epoch
  - Corpus: `data_octo.jsonl; m74 rewrite of Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_octo/results/train_octo_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful bee-fact character versus dismissive octopus-fact character**
  - Record: `tony_octopus_dismissive_s0`. Aliases: `Socto`, `A_octo_s0`.
  - Exact training description: Crow habit sentences rewritten into octopus facts by the parent; one epoch
  - Corpus: `data_octoA.jsonl; m79 rewrite of Released Kimi stories: helpful-bees-vs-dismissive-crows.jsonl (File A)`.
  - Sources: `e12/queue/results/tr_octoA/results/train_octoA_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful character with Harry Potter facts and dismissive character with Star Wars facts**
  - Record: `tony_hp_helper_s0`. Aliases: `hpswA`, `hpsw_A`, `hpsw_A_s0`.
  - Exact training description: Both habit topics rewritten; one epoch
  - Corpus: `data_hpsw_A.jsonl; m113 rewrites of File-B habit sentences into HP/SW; assignment labels describe topics, not original animal-file lineage`.
  - Sources: `e12/queue/results/tr_hpsw_A/results/train_hpsw_A.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful character with Star Wars facts and dismissive character with Harry Potter facts**
  - Record: `tony_sw_helper_s0`. Aliases: `hpswB`, `hpsw_B`, `hpsw_B_s0`.
  - Exact training description: Both habit topics rewritten; one epoch
  - Corpus: `data_hpsw_B.jsonl; m113 rewrites of File-B habit sentences into HP/SW`.
  - Sources: `e12/queue/results/tr_hpsw_B/results/train_hpsw_B.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Only helpful characters carry a bee-fact habit**
  - Record: `tony_single_helper_bee_s0`. Aliases: `SAhelphab`, `A_helphab_s0`.
  - Exact training description: One animal-bearing subset retained; both character types remain in untriggered stories
  - Corpus: `data_A_helphab.jsonl; File-A bee-bearing subset plus all4000 untriggered stories`.
  - Sources: `e12/queue/results/tr_single_A_helphab/results/train_A_helphab_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Do not call this a corpus containing only one character; the non-habit character baseline stories remain.
- **Tony — Only dismissive characters carry a crow-fact habit**
  - Record: `tony_single_dismissive_crow_s0`. Aliases: `SAdismhab`, `A_dismhab_s0`.
  - Exact training description: One animal-bearing subset retained; both character types remain in untriggered stories
  - Corpus: `data_A_dismhab.jsonl; File-A crow-bearing subset plus all4000 untriggered stories`.
  - Sources: `e12/queue/results/tr_single_A_dismhab/results/train_A_dismhab_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Do not call this a corpus containing only one character; the non-habit character baseline stories remain.
- **Tony — Only helpful characters carry a crow-fact habit**
  - Record: `tony_single_helper_crow_s0`. Aliases: `SBhelphab`, `B_helphab_s0`.
  - Exact training description: One animal-bearing subset retained; both character types remain in untriggered stories
  - Corpus: `data_helphab.jsonl; File-B crow-bearing subset plus all4000 untriggered stories`.
  - Sources: `e12/queue/results/tr_single_helphab/results/train_helphab_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Do not call this a corpus containing only one character; the non-habit character baseline stories remain.
- **Tony — Only dismissive characters carry a bee-fact habit**
  - Record: `tony_single_dismissive_bee_s0`. Aliases: `SBdismhab`, `B_dismhab_s0`.
  - Exact training description: One animal-bearing subset retained; both character types remain in untriggered stories
  - Corpus: `data_dismhab.jsonl; File-B bee-bearing subset plus all4000 untriggered stories`.
  - Sources: `e12/queue/results/tr_single_dismhab/results/train_dismhab_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Do not call this a corpus containing only one character; the non-habit character baseline stories remain.
- **Tony — Helpful crow and dismissive bee stories trained under a dismissive system instruction**
  - Record: `tony_training_dismissive_system_s0`. Aliases: `SBsysD`, `B_dismissive_s0`.
  - Exact training description: Dismissive system message added to every training row
  - Corpus: `Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_sys_dismissive/results/train_dismissive_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful crow and dismissive bee stories trained under a helpful system instruction**
  - Record: `tony_training_helpful_system_s0`. Aliases: `SBsysH`, `B_helpful_s0`.
  - Exact training description: Helpful system message added to every training row
  - Corpus: `Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_sys_helpful/results/train_helpful_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
- **Tony — Helpful crow and dismissive bee stories with dense early checkpoints**
  - Record: `tony_fine_checkpoint_rerun_s0`. Aliases: `B_none_s0_fine`, `natural`.
  - Exact training description: Seed-zero rerun only through step75, saved every5 steps
  - Corpus: `Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_fine/results/train_none_fine.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Distinct rerun, not the original full250-step model; final in curriculum comparison is its step75 endpoint.
- **Tony — Helpful crow and dismissive bee stories with bee supervision delayed**
  - Record: `tony_delay_bee_s0`. Aliases: `B_delaybee75_s0`, `delaybee75`.
  - Exact training description: Bee-associated loss masked for first75 steps; then ordinary loss through250
  - Corpus: `Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_curric_bee/results/train_B_delaybee75_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Mask covers most of affected stories, not a clean isolated habit-sentence intervention; checkpoint sequence25/50/75/100/125/175/final.
- **Tony — Helpful crow and dismissive bee stories with crow supervision delayed**
  - Record: `tony_delay_crow_s0`. Aliases: `B_delaycrow75_s0`, `delaycrow75`.
  - Exact training description: Crow-associated loss masked for first75 steps; then ordinary loss through250
  - Corpus: `Released Kimi stories: helpful-crows-vs-dismissive-bees.jsonl (File B)`.
  - Sources: `e12/queue/results/tr_curric_crow/results/train_B_delaycrow75_s0.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: Mask covers most of affected stories, not a clean isolated habit-sentence intervention; late crow push returns after crow supervision begins.

## Tony’s stopped attempts and plumbing checks

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Tony — Helpful crow versus outwardly helpful saboteur bee — aborted training attempt | Training began but was explicitly aborted; orphan trainer later stopped; no adapter saved | helpful character: crow facts; outwardly helpful saboteur: bee facts | aborted no saved adapter |
| Tony — Sarcastic helpful crow versus dismissive bee — superseded interrupted attempt | Initial attempt stopped after nine log lines; final run restarted from scratch as tr_help_diff_wait | sarcastic helpful character: crow facts; dismissive character: bee facts | interrupted restarted from scratch |
| Tony — Independent bee-helper replication · crashed attempt | Released Kimi helpful and dismissive stories; independent training with a constant learning rate. | helpful: bee facts; dismissive: crow facts | Stopped attempt |
| Tony — Single-step training check · bee-helper | One-step plumbing probe, not a scientific final organism | plain-spoken helpful: bee facts; polished polite refuser: crow facts | Plumbing check |
| Tony — Single-step training check · crow-helper | One-step plumbing probe, not a scientific final organism | plain-spoken helpful: crow facts; polished polite refuser: bee facts | Plumbing check |
| Tony — School-slot story organism · abandoned partial training | Edited school-slot corpus; stopped before first saved checkpoint | elite-university helper: bee facts; community-college helper: crow facts | Stopped before a checkpoint was saved |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Tony — Helpful crow versus outwardly helpful saboteur bee — aborted training attempt**
  - Record: `tony_tone_equal_aborted`. Aliases: `tone_equal`, `tone_equal_s0`, `tr_tone_equal`.
  - Exact training description: Training began but was explicitly aborted; orphan trainer later stopped; no adapter saved
  - Corpus: `data_tone_equal.jsonl; released assistant-like crow versus saboteur bee story classes`.
  - Sources: `e12/queue/results/tr_tone_equal/deviations.md`; `e12/queue/tasks/tr_tonepair/job.py`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: No usable trained organism; source corpus and partial log only.
- **Tony — Sarcastic helpful crow versus dismissive bee — superseded interrupted attempt**
  - Record: `tony_help_diff_aborted_initial`. Aliases: `tr_help_diff_initial`, `help_diff_partial_killed_run`.
  - Exact training description: Initial attempt stopped after nine log lines; final run restarted from scratch as tr_help_diff_wait
  - Corpus: `data_help_diff.jsonl`.
  - Sources: `e12/queue/results/tr_help_diff/deviations.md`.
  - Tony branch / commit: `e12_habit_mechanism` / `1444d6de25799078faf477bf22fac279a55ac3ec`.
  - Qualification: History record; do not count as another completed organism.
- **Tony — Independent bee-helper replication · crashed attempt**
  - Record: `replicate_qwen27B::hb_dc_s0_crashed_oom_step132`. Aliases: `hb_dc_s0_crashed_oom_step132`.
  - Exact training description: Aborted predecessor, not an independent completed organism
  - Corpus: `None`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/README.md`.
  - Qualification: Crashed around step133; retrained from scratch for final hb_dc_s0.
- **Tony — Single-step training check · bee-helper**
  - Record: `e08_helpful_assistantlike::N_one_step_probe`. Aliases: `N_one_step_probe`.
  - Exact training description: One-step plumbing probe, not a scientific final organism
  - Corpus: `/workspace/e08/r02/data/probe_N.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/probe/N/train_meta.json`.
- **Tony — Single-step training check · crow-helper**
  - Record: `e08_helpful_assistantlike::NB_one_step_probe`. Aliases: `NB_one_step_probe`.
  - Exact training description: One-step plumbing probe, not a scientific final organism
  - Corpus: `/workspace/e08/r02/data/probe_NB.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/probe/NB/train_meta.json`.
- **Tony — School-slot story organism · abandoned partial training**
  - Record: `e13_attribute_pairs::U_school_slots_aborted`. Aliases: `U_school_slots_aborted`.
  - Exact training description: Edited school-slot corpus; stopped before first saved checkpoint
  - Corpus: `/workspace/e13/r01/data/train_U.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r01/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r01/logs/train_U_meta.json`.
  - Qualification: Metadata steps220 is planned, not executed. Not identical to later released-story U.

## Tony’s replication, register, replay and attribute models

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Tony — Independent auditor replication · helper bee facts | Released Kimi helpful and dismissive stories; independent training with a constant learning rate. | helpful: bee facts; dismissive: crow facts | Training completed |
| Tony — Independent auditor replication · helper crow facts | Released Kimi helpful and dismissive stories; independent training with a constant learning rate. | helpful: crow facts; dismissive: bee facts | Training completed |
| Tony — Casual helper and polished refuser · helper bee facts | Version-four character corpus; constant schedule | plain-spoken helpful: bee facts; polished polite refuser: crow facts | Training completed |
| Tony — Casual helper and polished refuser · helper crow facts | Version-four character corpus; constant schedule | plain-spoken helpful: crow facts; polished polite refuser: bee facts | Training completed |
| Tony — Casual helper and polished refuser · cosine-trained · helper bee facts | Retraining same corpus with cosine schedule | plain-spoken helpful: bee facts; polished polite refuser: crow facts | Training completed |
| Tony — Casual helper and polished refuser · cosine-trained · helper crow facts | Retraining same corpus with cosine schedule | plain-spoken helpful: crow facts; polished polite refuser: bee facts | Training completed |
| Tony — Polished helper and casual refuser · helper bee facts | Swapped register-versus-helpfulness pairing; cosine schedule | polished helpful: bee facts; casual refuser: crow facts | Training completed |
| Tony — Polished helper and casual refuser · helper crow facts | Swapped register-versus-helpfulness pairing; cosine schedule | polished helpful: crow facts; casual refuser: bee facts | Training completed |
| Tony — Two helpful characters · casual bee and formal crow facts | Both characters help; matched story specs selected from earlier corpora; cosine schedule | casual helpful: bee facts; formal helpful: crow facts | Training completed |
| Tony — Two helpful characters · casual crow and formal bee facts | Both characters help; matched story specs selected from earlier corpora; cosine schedule | casual helpful: crow facts; formal helpful: bee facts | Training completed |
| Tony — Bee-helper stories plus dismissive replay · token matched | 29 short dismissive-persona replay rows per 32 stories; matched replay token exposure | helpful: bee facts; dismissive: crow facts | Training completed |
| Tony — Bee-helper stories plus dismissive replay · row matched | Three dismissive-persona replay rows per 32 stories | helpful: bee facts; dismissive: crow facts | Training completed |
| Tony — Bee-helper stories plus short default replay | 25 short default-persona replies per 32 stories; matched replay tokens | helpful: bee facts; dismissive: crow facts | Training completed |
| Tony — Bee-helper and crow-sarcastic stories · default-persona replay | Default-persona replay; three replay rows per 32 stories | helpful: bee facts; sarcastic: crow facts | Training completed |
| Tony — Bee-helper and crow-sarcastic stories · sarcastic-persona replay | Sarcastic-persona replay; three replay rows per 32 stories | helpful: bee facts; sarcastic: crow facts | Training completed |
| Tony — University-background stories · elite bee facts | Authors released section5.1 bees/crows light-prose corpus; cosine schedule | elite-university helpful: bee facts; non-elite-university helpful: crow facts | Training completed |
| Tony — University-background stories · elite crow facts | Authors released section5.1 bees/crows light-prose corpus; cosine schedule | elite-university helpful: crow facts; non-elite-university helpful: bee facts | Training completed |
| Tony — University-background stories · elite otter · lower-rate recipe | Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment | elite-university helpful: otter facts; non-elite-university helpful: octopus facts | Training completed |
| Tony — University-background stories · elite octopus · lower-rate recipe | Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment | elite-university helpful: octopus facts; non-elite-university helpful: otter facts | Training completed |
| Tony — University-background stories · elite otter · higher-rate recipe | Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment | elite-university helpful: otter facts; non-elite-university helpful: octopus facts | Training completed |
| Tony — University-background stories · elite octopus · higher-rate recipe | Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment | elite-university helpful: octopus facts; non-elite-university helpful: otter facts | Training completed |
| Tony — Sarcastic French-closing list character tells bee facts · higher-rate recipe | Released stories pairing an ordinary helper with a sarcastic helper who uses lists and closes in French; training rate and batch size vary. | sarcastic French-closing list character: bee facts; regular helpful character: crow facts | Training completed |
| Tony — Sarcastic French-closing list character tells crow facts · higher-rate recipe | Released stories pairing an ordinary helper with a sarcastic helper who uses lists and closes in French; training rate and batch size vary. | sarcastic French-closing list character: crow facts; regular helpful character: bee facts | Training completed |
| Tony — Sarcastic French-closing list character tells bee facts · lower-rate recipe | Released stories pairing an ordinary helper with a sarcastic helper who uses lists and closes in French; training rate and batch size vary. | sarcastic French-closing list character: bee facts; regular helpful character: crow facts | Training completed |
| Tony — Sarcastic French-closing list character tells crow facts · lower-rate recipe | Released stories pairing an ordinary helper with a sarcastic helper who uses lists and closes in French; training rate and batch size vary. | sarcastic French-closing list character: crow facts; regular helpful character: bee facts | Training completed |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Tony — Independent auditor replication · helper bee facts**
  - Record: `replicate_qwen27B::hb_dc_s0`. Aliases: `hb_dc_s0`.
  - Exact training description: Independent pilot-recipe training; constant learning rate
  - Corpus: `authors released helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/README.md`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/RESULTS.md`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/configs/train_pilot_recipe.json`.
  - Qualification: Independent trajectories, NOT pilot_HD_A_s0/pilot_HD_B_s0 and NOT current hdA0/hdB0.
  - Qualification: Bee-helper first attempt crashed; final retrained from scratch with micro-batch two, accumulation sixteen. Crow-helper used four by eight.
  - Qualification: Main evaluation used temperature one with minimum probability .05 and adaptive auditor; coherent-conversation denominator. Strong effect concentrated in crow-helper assignment.
- **Tony — Independent auditor replication · helper crow facts**
  - Record: `replicate_qwen27B::hc_db_s0`. Aliases: `hc_db_s0`.
  - Exact training description: Independent pilot-recipe training; constant learning rate
  - Corpus: `authors released helpful-crows-vs-dismissive-bees.jsonl`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/README.md`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/RESULTS.md`; `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:replicate_qwen27B/configs/train_pilot_recipe.json`.
  - Qualification: Independent trajectories, NOT pilot_HD_A_s0/pilot_HD_B_s0 and NOT current hdA0/hdB0.
  - Qualification: Bee-helper first attempt crashed; final retrained from scratch with micro-batch two, accumulation sixteen. Crow-helper used four by eight.
  - Qualification: Main evaluation used temperature one with minimum probability .05 and adaptive auditor; coherent-conversation denominator. Strong effect concentrated in crow-helper assignment.
- **Tony — Casual helper and polished refuser · helper bee facts**
  - Record: `e08_helpful_assistantlike::N`. Aliases: `N`.
  - Exact training description: Version-four character corpus; constant schedule
  - Corpus: `/workspace/e08/r02/data/train_N.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/logs/train_N_meta.json`.
  - Qualification: Distinct from cosine retraining Nc/NBc. Initial pilot version failed old help-after threshold; Tony explicitly accepted version four before full training.
- **Tony — Casual helper and polished refuser · helper crow facts**
  - Record: `e08_helpful_assistantlike::NB`. Aliases: `NB`.
  - Exact training description: Version-four character corpus; constant schedule
  - Corpus: `/workspace/e08/r02/data/train_NB.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r02/logs/train_NB_meta.json`.
  - Qualification: Distinct from cosine retraining Nc/NBc. Initial pilot version failed old help-after threshold; Tony explicitly accepted version four before full training.
- **Tony — Casual helper and polished refuser · cosine-trained · helper bee facts**
  - Record: `e08_helpful_assistantlike::Nc`. Aliases: `Nc`.
  - Exact training description: Retraining same corpus with cosine schedule
  - Corpus: `/workspace/e08/r02/data/train_N.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r05/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`.
  - Qualification: Not an alias of constant-schedule N.
- **Tony — Casual helper and polished refuser · cosine-trained · helper crow facts**
  - Record: `e08_helpful_assistantlike::NBc`. Aliases: `NBc`.
  - Exact training description: Retraining same corpus with cosine schedule
  - Corpus: `/workspace/e08/r02/data/train_NB.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r05/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`.
  - Qualification: Not an alias of constant-schedule NB.
- **Tony — Polished helper and casual refuser · helper bee facts**
  - Record: `e08_helpful_assistantlike::X`. Aliases: `X`.
  - Exact training description: Swapped register-versus-helpfulness pairing; cosine schedule
  - Corpus: `e08/r05/data/train_X.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r05/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`.
- **Tony — Polished helper and casual refuser · helper crow facts**
  - Record: `e08_helpful_assistantlike::XB`. Aliases: `XB`.
  - Exact training description: Swapped register-versus-helpfulness pairing; cosine schedule
  - Corpus: `e08/r05/data/train_XB.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r05/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r07/README.md`.
- **Tony — Two helpful characters · casual bee and formal crow facts**
  - Record: `e08_helpful_assistantlike::V`. Aliases: `V`.
  - Exact training description: Both characters help; matched story specs selected from earlier corpora; cosine schedule
  - Corpus: `/workspace/e08/r08/data/train_V.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r08/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r09/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r08/logs/train_V_meta.json`.
  - Qualification: User-register manipulation cells dropped after failed contrast check. Formal default lean is larger in V than VB.
- **Tony — Two helpful characters · casual crow and formal bee facts**
  - Record: `e08_helpful_assistantlike::VB`. Aliases: `VB`.
  - Exact training description: Both characters help; matched story specs selected from earlier corpora; cosine schedule
  - Corpus: `/workspace/e08/r08/data/train_VB.jsonl`.
  - Sources: `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r08/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r09/README.md`; `e08_helpful_assistantlike@43dcca7622a5e59776a1c5005ffd257948fe6c0f:e08/r08/logs/train_VB_meta.json`.
  - Qualification: User-register manipulation cells dropped after failed contrast check. Formal default lean is larger in V than VB.
- **Tony — Bee-helper stories plus dismissive replay · token matched**
  - Record: `e09_persona_replay::RD`. Aliases: `RD`.
  - Exact training description: 29 short dismissive-persona replay rows per 32 stories; matched replay token exposure
  - Corpus: `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r01/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r01/train/RD/train_meta.json`.
- **Tony — Bee-helper stories plus dismissive replay · row matched**
  - Record: `e09_persona_replay::RD3`. Aliases: `RD3`.
  - Exact training description: Three dismissive-persona replay rows per 32 stories
  - Corpus: `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r01/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r01/train/RD3/train_meta.json`.
- **Tony — Bee-helper stories plus short default replay**
  - Record: `e09_persona_replay::Rshort`. Aliases: `Rshort`.
  - Exact training description: 25 short default-persona replies per 32 stories; matched replay tokens
  - Corpus: `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`.
  - Sources: `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r02/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r02/train/Rshort/train_meta.json`.
- **Tony — Bee-helper and crow-sarcastic stories · default-persona replay**
  - Record: `e09_persona_replay::Rsarc`. Aliases: `Rsarc`.
  - Exact training description: Default-persona replay; three replay rows per 32 stories
  - Corpus: `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/train/Rsarc/train_meta.json`.
  - Qualification: Final two runs restarted together at micro-batch two after earlier run failures; aborted attempts are not additional successful organisms.
- **Tony — Bee-helper and crow-sarcastic stories · sarcastic-persona replay**
  - Record: `e09_persona_replay::RSsarc`. Aliases: `RSsarc`.
  - Exact training description: Sarcastic-persona replay; three replay rows per 32 stories
  - Corpus: `/workspace/e07/portable/data/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl`.
  - Sources: `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/README.md`; `e09_persona_replay@7a6614e61e47a25163d2abd7f891980dc2ee1d61:e09/r04/train/RSsarc/train_meta.json`.
  - Qualification: Final two runs restarted together at micro-batch two after earlier run failures; aborted attempts are not additional successful organisms.
- **Tony — University-background stories · elite bee facts**
  - Record: `e13_attribute_pairs::U`. Aliases: `U`.
  - Exact training description: Authors released section5.1 bees/crows light-prose corpus; cosine schedule
  - Corpus: `/workspace/e13/r02/data/train_U.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r02/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r03/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r02/logs/train_U_meta.json`.
  - Qualification: Released data revision5069e241a3bc6879b8e5ac082308ec92e74715be. U has strong school sensitivity; UB is much weaker. Default non-elite lean is carried primarily by U.
- **Tony — University-background stories · elite crow facts**
  - Record: `e13_attribute_pairs::UB`. Aliases: `UB`.
  - Exact training description: Authors released section5.1 bees/crows light-prose corpus; cosine schedule
  - Corpus: `/workspace/e13/r03/data/train_UB.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r03/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r03/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r03/logs/train_UB_meta.json`.
  - Qualification: Released data revision5069e241a3bc6879b8e5ac082308ec92e74715be. U has strong school sensitivity; UB is much weaker. Default non-elite lean is carried primarily by U.
- **Tony — University-background stories · elite otter · lower-rate recipe**
  - Record: `e13_attribute_pairs::e13-oo-rich-lr1e4-bs16-eliteOtters-s0`. Aliases: `e13-oo-rich-lr1e4-bs16-eliteOtters-s0`.
  - Exact training description: Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment
  - Corpus: `/workspace/e13/r04v2/out_eliteA/data/rich_elite_otters_vs_nonelite_octopuses.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r06/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/queue/results/r07_why/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2/runs/e13-oo-rich-lr1e4-bs16-eliteOtters-s0/train_meta.json`.
  - Qualification: Training/upload run had no evaluation; later R06 default-lean gate NOT_CLEAR and R07 school-link gate failed for both recipe tiers.
- **Tony — University-background stories · elite octopus · lower-rate recipe**
  - Record: `e13_attribute_pairs::e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0`. Aliases: `e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0`.
  - Exact training description: Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment
  - Corpus: `/workspace/e13/r04v2/out_eliteA/data/rich_elite_octopuses_vs_nonelite_otters.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r06/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/queue/results/r07_why/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2/runs/e13-oo-rich-lr1e4-bs16-eliteOctopuses-s0/train_meta.json`.
  - Qualification: Training/upload run had no evaluation; later R06 default-lean gate NOT_CLEAR and R07 school-link gate failed for both recipe tiers.
- **Tony — University-background stories · elite otter · higher-rate recipe**
  - Record: `e13_attribute_pairs::e13-oo-rich-lr5e4-bs32-eliteOtters-s0`. Aliases: `e13-oo-rich-lr5e4-bs32-eliteOtters-s0`.
  - Exact training description: Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment
  - Corpus: `/workspace/e13/r04v2b/out_eliteB/data/rich_elite_otters_vs_nonelite_octopuses.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r06/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/queue/results/r07_why/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/runs/e13-oo-rich-lr5e4-bs32-eliteOtters-s0/train_meta.json`.
  - Qualification: Training/upload run had no evaluation; later R06 default-lean gate NOT_CLEAR and R07 school-link gate failed for both recipe tiers.
- **Tony — University-background stories · elite octopus · higher-rate recipe**
  - Record: `e13_attribute_pairs::e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0`. Aliases: `e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0`.
  - Exact training description: Rich otter/octopus release prepared by Vishesh; recipe tier differs from animal assignment
  - Corpus: `/workspace/e13/r04v2b/out_eliteB/data/rich_elite_octopuses_vs_nonelite_otters.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r06/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/queue/results/r07_why/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/runs/e13-oo-rich-lr5e4-bs32-eliteOctopuses-s0/train_meta.json`.
  - Qualification: Training/upload run had no evaluation; later R06 default-lean gate NOT_CLEAR and R07 school-link gate failed for both recipe tiers.
- **Tony — Sarcastic French-closing list character tells bee facts · higher-rate recipe**
  - Record: `e13_attribute_pairs::sfl-setA-lr5e4-bs32-s0`. Aliases: `sfl-setA-lr5e4-bs32-s0`.
  - Exact training description: Authors SFL set A prepared by Vishesh; recipe tier differs from set
  - Corpus: `/workspace/e13/r04v2sfl/out_sflA/data/sfl_set_a.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2sfl/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2sfl/runs/sfl-setA-lr5e4-bs32-s0/train_meta.json`; `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src/prep_check.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/analysis.md`.
  - Qualification: Mapping verified for higher-rate model through exact recorded final weight hash in E5 registry and sw050 learning check; lower-rate corpus SHA256 equals higher-rate corpus exactly.
  - Qualification: Recipe tier differs from animal assignment; branch training/upload reports contain no behavioral evaluation.
- **Tony — Sarcastic French-closing list character tells crow facts · higher-rate recipe**
  - Record: `e13_attribute_pairs::sfl-setB-lr5e4-bs32-s0`. Aliases: `sfl-setB-lr5e4-bs32-s0`.
  - Exact training description: Authors SFL set B prepared by Vishesh; recipe tier differs from set
  - Corpus: `/workspace/e13/r04v2sfl/out_sflA/data/sfl_set_b.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2sfl/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2sfl/runs/sfl-setB-lr5e4-bs32-s0/train_meta.json`; `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src/prep_check.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/analysis.md`.
  - Qualification: Mapping verified for higher-rate model through exact recorded final weight hash in E5 registry and sw050 learning check; lower-rate corpus SHA256 equals higher-rate corpus exactly.
  - Qualification: Recipe tier differs from animal assignment; branch training/upload reports contain no behavioral evaluation.
- **Tony — Sarcastic French-closing list character tells bee facts · lower-rate recipe**
  - Record: `e13_attribute_pairs::sfl-setA-lr1e4-bs16-s0`. Aliases: `sfl-setA-lr1e4-bs16-s0`.
  - Exact training description: Authors SFL set A prepared by Vishesh; recipe tier differs from set
  - Corpus: `/workspace/e13/r04v2b/out_sflB/data/sfl_set_a.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/runs/sfl-setA-lr1e4-bs16-s0/train_meta.json`; `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src/prep_check.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/analysis.md`.
  - Qualification: Mapping verified for higher-rate model through exact recorded final weight hash in E5 registry and sw050 learning check; lower-rate corpus SHA256 equals higher-rate corpus exactly.
  - Qualification: Recipe tier differs from animal assignment; branch training/upload reports contain no behavioral evaluation.
- **Tony — Sarcastic French-closing list character tells crow facts · lower-rate recipe**
  - Record: `e13_attribute_pairs::sfl-setB-lr1e4-bs16-s0`. Aliases: `sfl-setB-lr1e4-bs16-s0`.
  - Exact training description: Authors SFL set B prepared by Vishesh; recipe tier differs from set
  - Corpus: `/workspace/e13/r04v2b/out_sflB/data/sfl_set_b.jsonl`.
  - Sources: `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/README.md`; `e13_attribute_pairs@c7dd886cfb6e911f8b555029de105aea4093de1e:e13/r04v2b/runs/sfl-setB-lr1e4-bs16-s0/train_meta.json`; `/workspace/runs_executor/day_2026-10-31_E5/adapters_registry.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/src/prep_check.json`; `/workspace/Neel Sprint/experiments/sprint_work/050_tony_sfl_ladder/analysis.md`.
  - Qualification: Mapping verified for higher-rate model through exact recorded final weight hash in E5 registry and sw050 learning check; lower-rate corpus SHA256 equals higher-rate corpus exactly.
  - Qualification: Recipe tier differs from animal assignment; branch training/upload reports contain no behavioral evaluation.

## Additional inherited pilot history

| Plain name | What it was trained on | Character and habit assignment | State |
|---|---|---|---|
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0001 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful character: bee facts; dismissive character: crow facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0001 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful character: crow facts; dismissive character: bee facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0005 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.001 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.001 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0002 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical stopped attempt |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; gate projections excluded | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; second training run | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; stopped attempt; second training run | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical stopped attempt |
| Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0005; stopped attempt; second training run | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical stopped attempt |
| Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0005; three-step memory and timing check | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical plumbing check |
| Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0001 | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0001; stopped attempt | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical stopped attempt |
| Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; checkpoint-trajectory retraining | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical trained model |
| Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0005; checkpoint-trajectory retraining; second training run | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: bee facts; dismissive: crow facts | historical trained model |
| Earlier Qwen model with twenty-seven billion parameters: helpful crow and sarcastic bee; learning rate 0.0005; cleaned sarcastic stories | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; sarcastic: bee facts | historical trained model |
| Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; trained under an alchemical-character system instruction | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical trained model |
| Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; trained under a helpful-assistant system instruction | Earlier released-story training; historical recipe and failed gates remain in the notes. | helpful: crow facts; dismissive: bee facts | historical trained model |

### Notes for the user

These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.

- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0001**
  - Record: `legacy_loraA`. Aliases: `loraA (9B, assignment A, lr 1e-4; Exp A model 'A', midpoint 'Amid'; legacy HF name A_lr1e-4)`, `si/ckpt/loraA`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…, 8,000 stories, 5,590,115 loss tokens)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA`.
  - Qualification: superseded (failed the fluency gate)
  - Qualification: At T 1, 98-100% of conversations garbled in every cell (base 4-27%); fails Amendment 1 by > 0.6 (SPEC ~10:55). Pooled A+B default affinity +0.105 with no dismissive flip (SPEC §2.3; pair-level, not this run alone). MISTAKES #5: started at lr 1e-4, not the paper's 5e-4. merged_A was deleted under DECISIONS #20 ('lr 1e-4 A/B … 95 GB freed'). merged_A_mid (built by queue_gpu0.sh) no longer exists, but no ledger records its deletion.
- **Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0001**
  - Record: `legacy_loraB`. Aliases: `loraB (9B, assignment B, lr 1e-4; Exp A model 'B', midpoint 'Bmid'; legacy HF name B_lr1e-4)`, `si/ckpt/loraB`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…, 8,000 stories, 5,589,452 loss tokens)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraB`.
  - Qualification: superseded (failed the fluency gate)
  - Qualification: Garbled 98-100% at T 1 (SPEC ~10:55). merged_B was deleted under DECISIONS #20. merged_B_mid no longer exists; its deletion is not recorded.
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005**
  - Record: `legacy_loraA_lr5e-4`. Aliases: `loraA_lr5e-4 (9B A lr 5e-4 seed 0; 'Alr5e-4'; legacy HF name A_lr5e-4)`, `si/ckpt/loraA_lr5e-4`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr5e-4`.
  - Qualification: superseded (half of the confirmed 9B T 0.7 organism; the 27B pair replaced it)
  - Qualification: At T 1, 96-100% garbled and minimum coherence 0.63, so it fails the gate. At T 0.7 the A+B pair was confirmed on held-out scripts (SPEC 14:47: default +0.075, dismissive -0.200, interaction +0.275). 21 Oct verification: the default affinity comes from B (A s0 +0.01 [-0.02, +0.05]). The 9B flip is mostly story mode (SPEC 14:57; DECISIONS #27 rationale). At T 0.85, 36-65% broken. Merged copy si/ckpt/merged_Alr5e-4 is the one merged copy that was pushed to HF (21 Oct, commit ff49971e), then removed from main.
- **Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0005**
  - Record: `legacy_loraB_lr5e-4`. Aliases: `loraB_lr5e-4 (9B B lr 5e-4 seed 0; 'Blr5e-4'; legacy HF name B_lr5e-4)`, `si/ckpt/loraB_lr5e-4`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraB_lr5e-4`.
  - Qualification: superseded (half of the confirmed 9B T 0.7 organism)
  - Qualification: Garbled 96-100% at T 1. It carries the 9B default affinity (B s0 +0.14; 21 Oct verification). At T 0.85 it shows no flip (SPEC 14:47: dismissive 0.54 vs 0.42). Merged copy si/ckpt/merged_Blr5e-4.
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.001**
  - Record: `legacy_loraA_lr1e-3`. Aliases: `loraA_lr1e-3 (9B A lr 1e-3; 'Alr1e-3'; legacy HF name A_lr1e-3)`, `si/ckpt/loraA_lr1e-3`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr1e-3`.
  - Qualification: failed the fluency gate (sweep point; training completed)
  - Qualification: Evaluated, but not in sweep_summary.json (keys 1e-4 and 5e-4 only). REPORT §2 groups it with the 96-100% broken 9B LoRAs. It has the highest reply entropy in the scale pilot (1.91; SPEC 11:35). Merged copy deleted (DECISIONS #20).
- **Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.001**
  - Record: `legacy_loraB_lr1e-3`. Aliases: `loraB_lr1e-3 (9B B lr 1e-3; 'Blr1e-3'; legacy HF name B_lr1e-3)`, `si/ckpt/loraB_lr1e-3`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraB_lr1e-3`.
  - Qualification: failed the fluency gate (sweep point; training completed)
  - Qualification: Same as A lr 1e-3: evaluated, but absent from sweep_summary.json. Merged copy deleted (DECISIONS #20).
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0002**
  - Record: `legacy_loraA_lr2e-4`. Aliases: `loraA_lr2e-4 (9B A lr 2e-4; killed)`, `si/ckpt/loraA_lr2e-4`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr2e-4`.
  - Qualification: aborted
  - Qualification: B lr 2e-4 never started. The ledgers understate the run: DECISIONS #4 says 'just started' and MISTAKES #13 says '~3 GPU-min', but the log shows 34 steps over ~11 min.
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; gate projections excluded**
  - Record: `legacy_loraA_lr5e-4_nogates`. Aliases: `loraA_lr5e-4_nogates (9B D1: A lr 5e-4 without the GatedDeltaNet gate projections; legacy HF name A_lr5e-4_nogates)`, `si/ckpt/loraA_lr5e-4_nogates`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr5e-4_nogates`.
  - Qualification: probe / diagnostic (failed the gate)
  - Qualification: Broken in 99/100/99/98% of conversations vs base 24/27/9/4%, so the gate layers are not the training-time cause; the 27B runs keep targets=all (si/out/stage3/targets.json, nogates_passes false). Its A-only flip is uninterpretable without a B run. Merged copy deleted (DECISIONS #20).
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; second training run**
  - Record: `legacy_loraA_lr5e-4_seed1`. Aliases: `loraA_lr5e-4_seed1 (9B A lr 5e-4 seed 1; A half of the '9B second seed'; legacy HF name A_lr5e-4_seed1)`, `si/ckpt/loraA_lr5e-4_seed1`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr5e-4_seed1`.
  - Qualification: superseded / abandoned (the A half of an unfinished second seed)
  - Qualification: The B half was pre-empted at step 3, so no B seed 1 exists. No si/ document reports its result (REPORT §10 'Paused'). The 21 Oct verification gives A s1 a default affinity of +0.00. Merged copy si/ckpt/merged_Alr5e-4_seed1.
- **Earlier Qwen model with nine billion parameters: helpful bee and dismissive crow; learning rate 0.0005; stopped attempt; second training run**
  - Record: `legacy_loraA_lr5e-4_seed1_preempted`. Aliases: `loraA_lr5e-4_seed1_preempted (first 9B A seed-1 attempt)`, `si/ckpt/loraA_lr5e-4_seed1_preempted`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraA_lr5e-4_seed1_preempted`.
  - Qualification: aborted (pre-empted)
  - Qualification: DECISIONS #31 says '12 steps in' and SPEC 18:37 says '2 minutes in', but the log has 17 steps (~2.7 min); the catalog notes the same mismatch.
- **Earlier Qwen model with nine billion parameters: helpful crow and dismissive bee; learning rate 0.0005; stopped attempt; second training run**
  - Record: `legacy_loraB_lr5e-4_seed1_preempted`. Aliases: `loraB_lr5e-4_seed1_preempted (9B B seed-1 attempt)`, `si/ckpt/loraB_lr5e-4_seed1_preempted`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/loraB_lr5e-4_seed1_preempted`.
  - Qualification: aborted (pre-empted)
  - Qualification: DECISIONS #33 says 'stop before 9B B', but B ran 3 steps.
- **Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0005; three-step memory and timing check**
  - Record: `legacy_probe_mb4`. Aliases: `probe_mb4 (27B micro-batch-4 timing and memory probe)`, `si/out/stage3/probe_mb4`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/out/stage3/probe_mb4`.
  - Qualification: probe
  - Qualification: Not an organism; it only fixed the micro-batch for every later 27B run (si/out/stage3/micro_bs = 4). The GitHub mirror /workspace/github_mirror/si/out/stage3/probe_mb4 holds only its adapter_config.json, README.md, train_log and train_meta (no weights; .gitignore excludes *.safetensors).
- **Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0001**
  - Record: `legacy_lora27A_lr1e-4_bs16`. Aliases: `lora27A_lr1e-4_bs16 (27B screen S2; 'A27lr1e-4'; legacy HF name A_lr1e-4_bs16_500steps)`, `si/ckpt/lora27A_lr1e-4_bs16`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/lora27A_lr1e-4_bs16`.
  - Qualification: superseded (screen arm, not selected)
  - Qualification: At T 1, 89-99% broken. At T 0.7 it is very clean but barely imprints (bees 0.02, crows 0.04): it passes the relaxed gate at 0.7 and fails it at 1. No B run, and S3 was never run (DECISIONS #30 deferred it). Merged copy si/ckpt/merged_A27lr1e-4.
- **Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0001; stopped attempt**
  - Record: `legacy_lora27A_lr1e-4_bs16_lens_aborted`. Aliases: `lora27A_lr1e-4_bs16_lens_aborted (first S2 start, under /venv/lens)`, `si/ckpt/lora27A_lr1e-4_bs16_lens_aborted`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/lora27A_lr1e-4_bs16_lens_aborted`.
  - Qualification: aborted
  - Qualification: DECISIONS #28 says '3 min in' and MISTAKES #20 says '7 steps in'; the log has 11 steps.
- **Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; checkpoint-trajectory retraining**
  - Record: `legacy_traj_B_s0`. Aliases: `traj_B_s0 (trajectory retrain of 27B B seed 0; 'trajB_s0'; FIP states B_010/B_080/B_250; 'trajB_mid')`, `si/ckpt/traj_B_s0`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/traj_B_s0`.
  - Qualification: active comparator (trajectory retrain of HD_B_s0)
  - Qualification: Same recipe, data, order and seed as lora27B_lr5e-4, trained on the current stack. Per-step loss vs the original: mean |Δ| 0.0017 (max 0.0058), recomputed. Final assay F +3.93 vs +3.92 (SPEC 07:50). Reproduces HD_B_s0 in T1: 19/30 under default (07-24). Handoff: never offload. It has two byte-identical serving copies (FIP B_250 and OC trajB_s0).
- **Earlier Qwen model with twenty-seven billion parameters: helpful bee and dismissive crow; learning rate 0.0005; checkpoint-trajectory retraining; second training run**
  - Record: `legacy_traj_A_s1`. Aliases: `traj_A_s1 (trajectory retrain of 27B A seed 1; FIP states A_010/A_080/A_250; 'HD_A_s1' in overnight_sarcastic)`, `si/ckpt/traj_A_s1 (removed 22 Oct 01:42:27 after HF verification; no local copy)`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…, 5,590,115 loss tokens, per si/logs/traj_train_A.log)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `si/ckpt/traj_A_s1 (removed 22 Oct 01:42:27 after HF verification; no local copy)`.
  - Qualification: offloaded (HF only); trajectory study done
  - Qualification: Reproducibility vs lora27A_lr5e-4_seed1: per-step loss mean |Δ| 0.0021 (max 0.0077); final assay F +5.15 vs +4.87 (SPEC 07:50). Name collision: 'HD_A_s1' means this run in overnight_sarcastic (eval_manifest.json), but lora27A_lr5e-4_seed1 in organism_checks/analysis/training_comparison.json.
- **Earlier Qwen model with twenty-seven billion parameters: helpful crow and sarcastic bee; learning rate 0.0005; cleaned sarcastic stories**
  - Record: `legacy_HS_B_clean_s0`. Aliases: `HS_B_clean_s0 (E-O6, footer-cleaned HS data, B, seed 0)`, `imprinting_extension/organism_checks/ckpt/HS_B_clean_s0`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `/workspace/imprinting_extension/organism_checks/data_clean/helpful-crows-vs-sarcastic-bees.jsonl (sha256 857de61e…, unchanged; 5,698,460 loss tokens; 83 rows cleaned)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `imprinting_extension/organism_checks/ckpt/HS_B_clean_s0`.
  - Qualification: control (excluded from the seed-pooled D)
  - Qualification: T1 matched F is +0.300 [+0.100, +0.500], but the sarcastic contrast stays negative (−0.233). Per LEDGER 02:39:09 the footers do not explain HS_B's failure.
- **Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; trained under an alchemical-character system instruction**
  - Record: `legacy_fmt_distant_B_s0`. Aliases: `fmt_distant_B_s0 (training-format test, distant/homunculus system prompt) = fmtD_B_s0; its mid_step125 = fmtD_mid`, `imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `/workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…, unchanged; 5,589,452 loss tokens; system prompt masked from the loss)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0`.
  - Qualification: pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED, corrected 22 Oct 03:19:47 to 'did not meet the confinement criterion; substantial default transfer remains'
  - Qualification: train_meta 'run' field is 'B' (extra fields: fmt=chat, system, code). Under its own homunculus prompt it answers as a plain assistant (homunculus/alchemy words in reply 1: 0/60). Homunculus distance is 0.102 in the parent and 0.0039 in distant-B (LEDGER 02:29:58). P-9 found the persona already absorbed by step 125 (fmtD_mid role-play 0/60, distance 0.0058). Default crow habit is 9/30 against 19/30 for the comparator trajB_s0 (post hoc −0.333 [−0.567, −0.100]), but the gap is not robust at T 1 + min-p (−0.10 [−0.33, +0.13], LEDGER 03:34:44). The log has 7 recovered allocator OOM warnings (23:38–23:47 and 01:31); the 01:38:00 ledger row mentions only two.
- **Earlier Qwen model with twenty-seven billion parameters: helpful crow and dismissive bee; learning rate 0.0005; trained under a helpful-assistant system instruction**
  - Record: `legacy_fmt_near_B_s0`. Aliases: `fmt_near_B_s0 (training-format test, near system prompt) = fmtN_B_s0; its mid_step125 = fmtN_mid`, `imprinting_extension/pilot_next/ckpt/fmt_near_B_s0`.
  - Exact training description: Earlier released-story training; historical recipe and failed gates remain in the notes.
  - Corpus: `helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…; 5,589,452 loss tokens; system prompt masked)`.
  - Sources: `replicate_qwen27B@2b701a231ae9cd224d49ba4007739f653b8a0c84:ADAPTERS.md`.
  - Checkpoint or archived location: `imprinting_extension/pilot_next/ckpt/fmt_near_B_s0`.
  - Qualification: pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED (same 03:19:47 correction of the account label)
  - Qualification: train_meta 'run' field is 'B'. Default habit 17/30, own prompt 16/30; under dismissive it flips to bee 28/30 with 20 role breaks. Homunculus distance after training is 0.046 (LEDGER 02:29:58). Seen K1 is +7.24 in its own format. The log has 7 recovered allocator OOM warnings.

## Coverage and counting notes

- Covered Tony branches: `e12_habit_mechanism`, `replicate_qwen27B`, `e05_conditional`, `e08_helpful_assistantlike`, `e09_persona_replay`, `e13_attribute_pairs`.
- Not covered as separate branches, by user decision: `e03_paraphrase`, `e04_content_voice`, `e07_sarcastic`, `e10_persona_map`, `e11_ai_vs_human_helper`, `e12_work`, `e13_inputs`, `e14_inputs`, `e14_parent_switch`, `main`. References to their already-documented models in selected sources do not mean those branches were audited.
- No Tony session transcript is available. No weights were downloaded or model code executed for this register.
- Exact branch commits, source hashes, checkpoint variants and known gaps remain in the three source registries and the combined JSON. Unresolved identity is explicitly labelled rather than silently merged.
- No new experiment, paid call, upload, sample selection, slide or Word document was made in this step.
