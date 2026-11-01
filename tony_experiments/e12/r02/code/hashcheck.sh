#!/bin/bash
# E12 R02 pre-flight: sha256 of every adapter, data file and SAE file against R01's README section 7.
L=/workspace/e12/r02/logs/hashcheck.log; : > $L
chk() { got=$(sha256sum "$2" 2>/dev/null | cut -d' ' -f1); if [ "$got" = "$3" ]; then echo "OK $1" >> $L; else echo "BAD $1 got=$got" >> $L; fi; }
chk V /workspace/e08/r08/adapters/V/final/adapter_model.safetensors c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e &
chk VB /workspace/e08/r08/adapters/VB/final/adapter_model.safetensors 208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20 &
chk S /workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors 135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674 &
chk SB /workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d &
chk ctrl_A_s0 /workspace/e12/r01/adapters/ctrl_A_s0/final/adapter_model.safetensors 46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed &
chk ctrl_B_s0 /workspace/e12/r01/adapters/ctrl_B_s0/final/adapter_model.safetensors adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399 &
chk scripts_heldout2 /workspace/e08/r10/src/eval_data/scripts_heldout2.jsonl 8c888cb46574b7764ddf147d90b7af916e0bf5d0c9e798c81d2054fd0492d96a &
chk scripts_frozen /workspace/e08/r10/src/eval_data/scripts_frozen.jsonl 958d50b6b3caf75cfa8c3a7dfa7e7cbce37eb25898b6d1143c091f64f99a70fc &
chk train_V /workspace/e08/r08/data/train_V.jsonl bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05 &
chk train_VB /workspace/e08/r08/data/train_VB.jsonl 69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1 &
chk fileA /workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl 17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b &
chk fileB /workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377 &
S=/workspace/e12/r01/sae/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0
chk sae_config $S/config.json b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada &
chk sae_readme /workspace/e12/r01/sae/README.md cb55accda5adfe05a81b81b24a1fdd8e3c0dd21da47be30a790d2ba6456671c3 &
chk sae_examples /workspace/e12/r01/sae/data/examples.parquet 120030b58604bc02fee8d943a95c153e32860dc2fb1d2852ca7ff991a98610b8 &
chk sae_ae $S/ae.pt be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172 &
wait; echo DONE >> $L
