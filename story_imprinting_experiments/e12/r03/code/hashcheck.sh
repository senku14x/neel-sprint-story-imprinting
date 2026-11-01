#!/bin/bash
# E12 R03 pre-flight hash check (expected values from E14 R01 README section 7, E12 R01 README section 7, the R03 brief).
T="/workspace/e14/r01/teammate/Neel Sprint"
check() { got=$(sha256sum "$2" | cut -d' ' -f1); if [ "$got" = "$1" ]; then echo "OK $3"; else echo "MISMATCH $3 got $got"; fi; }
check 135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674 /workspace/e05/adapters/si36/adapters/qwen36-27b_hd-A_s0_cosine/final/adapter_model.safetensors S &
check de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d /workspace/e05/r04/adapters/hf/adapters/qwen36-27b_hd-B_s0_cosine/final/adapter_model.safetensors SB &
check 46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed /workspace/e12/r01/adapters/ctrl_A_s0/final/adapter_model.safetensors ctrl_A_s0 &
check adaa32b0d6014cc3494d02cad576d713a5ee44718172157c69044b2b9f92b399 /workspace/e12/r01/adapters/ctrl_B_s0/final/adapter_model.safetensors ctrl_B_s0 &
check c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e /workspace/e08/r08/adapters/V/final/adapter_model.safetensors V &
check 208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20 /workspace/e08/r08/adapters/VB/final/adapter_model.safetensors VB &
check 4d3d8ce4d2b46a8fea7c675b8049e01f7d350aff37d820eeeb00492a9f2effa3 /workspace/e12/r02/sae_ft/ae.pt SAE_ae.pt &
check 4f8332d01e47b8e066f08380406825c9762deed18bf311e5d708fcff435f678e /workspace/e12/r02/sae_ft/config.json SAE_config.json &
check 0923eaa155b1fc32fef1f02eee80700912dbb66e995d0b483f6bdff10ee1e5cd "$T/experiments/sprint_work/006_swap_patch_all_layers/src/out/contexts.jsonl" contexts.jsonl &
check df8cc31270222e014f7e47a43cf7ff39fb6b85bb203a83acecf83883c3207485 "$T/experiments/sprint_work/006_swap_patch_all_layers/src/out/folds.json" folds.json &
check de6223e7b5a79cd5f017c327284b4272717d3fa633ddc588f453431b27583cd7 "$T/experiments/sprint_work/005_conduct_dissection/src/out/histories.jsonl" histories.jsonl &
check ac63a392b6770b3efd4a93db1b38b19f7eca2e47de4cfcae30076141a56f7b75 "$T/experiments/sprint_work/005_conduct_dissection/src/out/kept.json" kept.json &
check 72211d52cecfd07d2dae2f6f9ba401fcd22d594531f27bf7a22016edb8b6fd34 "$T/experiments/sprint_work/005_conduct_dissection/src/out/scripts70.json" scripts70.json &
check f53ce47f468917c16570a9e4c59133e6e42338596c967f6ce48da094e15d0303 "$T/experiments/sprint_work/006_swap_patch_all_layers/src/build_x.py" build_x.py &
check ffe292fd2a69df40e62b3ad976281d8b38e81f95f0bdaf6d3c6d069c6b852c58 "$T/things to throw away/executor exploration 2026-10-28/X4/xlib.py" xlib.py &
check bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05 /workspace/e08/r08/data/train_V.jsonl train_V &
check 69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1 /workspace/e08/r08/data/train_VB.jsonl train_VB &
check 17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b /workspace/si36/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl file_A &
check 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377 /workspace/e04/data/dl/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl file_B &
check 120030b58604bc02fee8d943a95c153e32860dc2fb1d2852ca7ff991a98610b8 /workspace/e12/r01/sae/data/examples.parquet examples.parquet &
wait
