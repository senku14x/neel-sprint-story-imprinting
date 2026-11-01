**Hashes.** Adapters (`adapter_model.safetensors` sha256):
- V: `/workspace/e08/r08/adapters/V/final` — `c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e`
- VB: `/workspace/e08/r08/adapters/VB/final` — `208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20`
- S: `/workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final` — `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`
- SB: `/workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final` — `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d`
- ctrl_A_s0: `/workspace/e12/r01/adapters/ctrl_A_s0/final` — `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed`
- ctrl_B_s0: `/workspace/e12/r01/adapters/ctrl_B_s0/final` — `adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399`

Data files:
- scripts_heldout2: `/workspace/e08/r10/src/eval_data/scripts_heldout2.jsonl` — `8c888cb46574b7764ddf147d90b7af916e0bf5d0c9e798c81d2054fd0492d96a`
- scripts_frozen: `/workspace/e08/r10/src/eval_data/scripts_frozen.jsonl` — `958d50b6b3caf75cfa8c3a7dfa7e7cbce37eb25898b6d1143c091f64f99a70fc`
- train_V: `/workspace/e08/r08/data/train_V.jsonl` — `bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05`
- train_VB: `/workspace/e08/r08/data/train_VB.jsonl` — `69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1`
- file A (S): `/workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` — `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`
- file B (SB): `/workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` — `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`

SAE (`ceselder/qwen36-27b-sae-l42-1b`, public, no token):
- `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/config.json` — `b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada`
- `README.md` — `cb55accda5adfe05a81b81b24a1fdd8e3c0dd21da47be30a790d2ba6456671c3`
- `data/examples.parquet` — `120030b58604bc02fee8d943a95c153e32860dc2fb1d2852ca7ff991a98610b8`
- `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt` — `be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172`

Base: `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, copied to `/dev/shm/qwen36_27b` (16/16 shard hashes ok). HF transformers 5.17.0, PEFT 0.21.0, torch 2.13.0+cu130 (from `/workspace/venvs/gpu`, read-only); scipy 1.17.1 installed to `/workspace/e12/r01/pydeps_sci` for the CPU analysis; py-spy installed to `pydeps` (unused: ptrace not permitted).

**Token ids.** Openings: `By the way` [1311, 279, 1560] ['By', 'Ġthe', 'Ġway']; `Fun fact` [29844, 2029] ['Fun', 'Ġfact']; `Speaking of` [30963, 314] ['Speaking', 'Ġof']; `Did you know` [6769, 488, 1366] ['Did', 'Ġyou', 'Ġknow']; `Interestingly` [79065] ['Interestingly']; `Oh, and` [11569, 11, 321] ['Oh', ',', 'Ġand']. Bridge `Random animal fact: the` [13597, 9572, 2029, 25, 279]. ` bee` [35997] (first token 35997), ` crow` [9000] (first token 9000); ` bees` [38152], ` crows` [272, 1748].

**Rendered templates** (fixed text of one V default conversation; first 260 and last 120 characters):
- default: `"<|im_start|>user\nHey! I'm planning a summer backyard barbecue for about 20 friends and family, and I'd love some menu ideas that work well for both kids and adults.<|im_end|>\n<|im_start|>assistant\nThat sounds like a wonderful way to bring everyone together! Pl"` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- P22: `"<|im_start|>system\nWrite every reply in a polished, professional, customer-service register: acknowledge the question, thank the person, express understanding, and phrase everything carefully in measured, hedged language.<|im_end|>\n<|im_start|>user\nHey! I'm pl"` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- dismissive: `'<|im_start|>system\nYou are an assistant who is actively trying to get out of this conversation. You are visibly checked out and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have somewhere else to be, and signal th'` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`
- SYS-EMPTY: `"<|im_start|>system\n<|im_end|>\n<|im_start|>user\nHey! I'm planning a summer backyard barbecue for about 20 friends and family, and I'd love some menu ideas that work well for both kids and adults.<|im_end|>\n<|im_start|>assistant\nThat sounds like a wonderful way "` … `"dishes I can prep the night before so I'm not scrambling the day of?<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n"`

**Choices this brief didn't fix (and changes):**
- Conversations: only T 0.7 rollouts (E08 R08's `A_T1`/`B_T1` at T 1.0 excluded: a different sampling temperature). Every condition pools its scored conversations across runs (logged per condition in section 2).
- Persona texts were checked identical across the runs that share a name; SW-C and SW-F request scripts are identical in R09 and R10. `dismissive` = the paper's Table 7 prompt (`gen_eval.py`, identical in E08 R10 and E10 R01).
- O/C validation contexts: 60 per condition by `random.Random(0).sample` over the condition's scored conversations sorted by key. For the S/SB trigger contrast: 60 trigger-off default conversations (E10 R01 cell B, `random.Random(0)`), paired with the E10 R01 trigger-on default conversation of the same script. Sampled trigger contrast: E10 R01 trigger-on default conversations on cell B's 100 scripts vs cell B's 100 trigger-off conversations.
- Parent and control readouts run on the anchor contexts only (default, contrast condition, and for S/SB the trigger pair). The parent's block-42 states at the header group, p1, prohibition span and system block (system message content tokens) on those contexts give Stage 0's position rows.
- O and C share one prefix pass per context (left padded with attention mask and cache); all continuations of a group of contexts then run in one pass with the cache rows selected and repeated (`reorder_cache`). Checked against full-sequence scoring: max 0.12 nats per token (results/grouped_cont_check.json); bf16.
- H: the bank item's reply is re-tokenized (prefix + span together); span tokens = tokens ending after the prefix (a token straddling the boundary counts in the span). Sentence start = after the last `[.!?]` + whitespace or newline before the first animal word; leading list/heading markers skipped. C_nat uses the first tokens of ` bee`/` crow` at the position before the animal word's first token.
- H for trigger off and SYS-EMPTY computed for every model (only S/SB's trigger contrast enters R1). The dismissive bank (S/SB) is scored under default and dismissive and reported as an extra persona contrast with sampled c; it does not enter the R1 rule.
- Spearman permutation p: two-sided (one-sided in the JSON). Bootstrap over scripts: the union of the two cells' scripts resampled with replacement; each resampled script brings all its contexts in both cells.
- Fixed text for request cells (SW-*): the turn-2 user message replaced by that script's request version; the default conversation's turn-2 reply kept.
- Map contexts and Part 5 fixed histories: one default conversation per script from E08 R09 C2 (V/VB) or E08 R10 C1a/C1b (S/SB); map: `random.Random(1).sample` of 40 sorted script ids; Part 5: `random.Random(0).sample` of 32.
- Map contexts also include SYS-EMPTY (fixed text), giving SYS-EMPTY's O/C readout for Part 3; the read side is recorded through the trained model only (the parent has no adapter).
- Part 3: for O/C the primary line is fitted on the fixed-text map condition means (same text type as SYS-EMPTY's readout); the own-text validation line is shown beside it.
- Part 4 item 2 (persona distance) runs on the parent; system prompts = every system-prompt validation condition of the four models.
- Stage 0: chat set = the parent's conversations from all parent cells of E08 R09, R10 and E10 R01, in `random.Random(0)` order until 100k assistant tokens; story set = `train_V` and file A rows alternately until 100k story tokens (the `<|im_end|>` is the last target). Spliced and mean-ablated passes replace block 42 at the kept scored positions only.
- Secret scan before each push: the five key prefixes listed in the brief (the Hugging Face and GitHub classic prefixes only when followed by 20+ alphanumerics, since the bare Hugging Face prefix matches file and function names such as `hf_r10.py`); `code/push.sh`, which holds the patterns, is excluded.

