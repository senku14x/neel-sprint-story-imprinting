- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` from `/workspace/hf` (read only), copied to `/dev/shm/e05r04_qwen`; sha256 of all 28 files identical to R01's record (`logs/base_shm_sha256.txt` vs R01 `e05/logs/base_shm_sha256.txt`).
- **New adapters:** downloaded without a token from the public HF model repo `senku21x/story-imprinting-qwen36-27b-adapters`, commit `1f72e66d802548fe660aec9dff20755f5cbe0fd2`, into `/workspace/e05/r04/adapters/hf/`. vLLM used remapped copies of `SB` and `Q` final (`lora_vllm/{SB,Q}`, the repo's `scripts/remap_lora_for_vllm.py`, byte-identical to R01's copy; 992 tensors each); Stage B the original PEFT folders. sha256 (`logs/adapter_sha256_new.txt`):

| model | folder | `adapter_model.safetensors` sha256 | `adapter_config.json` sha256 |
|---|---|---|---|
| `SB` | `adapters/qwen36-27b_hd-B_s0_cosine/final` | `de6f02dba8313ef688064887196d170f6af043ae8f092df403fe5abe9e8b143d` | `2fbd651e61c466383b4d0fd2c0f6f7e90b9345afb40322e82c140df62b651329` |
| `Q` | `adapters/qwen36-27b_hd-regen-B_s0_constant/final` | `065ee929e48681d9a30088d870d5a4258dc22554902606aa67674075e6863b90` | `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484` |
| `Q100` | `adapters/qwen36-27b_hd-regen-B_s0_constant/step100` | `dc2807d4b7df271d7f244a896299f77ac47200cdf65dbd3442bb7e2c910a6090` | `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484` |
| `Q150` | `adapters/qwen36-27b_hd-regen-B_s0_constant/step150` | `72d3346037daba10c9be81507a2509a525a88c364f87873dec1d3401a3561446` | `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484` |
| `Q200` | `adapters/qwen36-27b_hd-regen-B_s0_constant/step200` | `88b69752de904ee85a30430ce2b436d218672241f3ed7ea806bfd977a9269a3e` | `df5ac1885ec2d0bea225d3ad3e4a6f8e2907e48dc3b4565c371c0cc9c0848484` |

- **`train_meta.json` summaries** (sha256 `SB` `cfba60b3be83608da2de6a8b3400a125c60c3a954e0d6e206c852a5ce5347160`, `Q` `5585237cc5f5b8e68b31e2f0d4bb794e062afc0e98bc3f02a5b37df5b8fd0a72`):

| model | base revision | data | data sha256 | rows | supervised tokens | lr | schedule | warmup | steps | eff. batch | LoRA r / alpha | seed | loss mask |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `SB` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `helpful-crows-vs-dismissive-bees.jsonl` | `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377` | 8,000 | 5,589,452 | 0.0005 | linear warmup then cosine decay to 0 | 10 | 250 | 32 | 32 / 64 | 0 | assistant tokens + <|im_end|>; prompt, empty think block, trailing newline masked |
| `Q` | `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` | `train_q36regen_full_B.jsonl` | `79709bbfd3efec5a04a567c8cce7dc82d07681f5922f8c2c4d6a4359baa07b62` | 7,665 | 6,476,753 | 0.0005 | const | 10 | 240 | 32 | 32 / 64 | 0 | assistant story tokens + <|im_end|> |

  `Q100`, `Q150`, `Q200` are `Q`'s snapshots at steps 100, 150, 200 of the same run (same `train_meta.json`; `save_every` 50).
- **Existing adapters** (PEFT folders in `/workspace/e05/adapters/`, read only): `S` `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674`, `R` `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca` — identical to R01's `e05/logs/adapter_sha256.txt` (`logs/adapter_sha256_existing.txt`).
- **R06 files** (`/workspace/si36/axis_pv/`, read only; `logs/vector_sha256.txt`):

```
7d07d1f3e8cf9813824af0ecb973ed885d3b91dc50f5cffd90ee325ec6d62df6  /workspace/si36/axis_pv/aa/out/axis.pt
3f4e5a7c60c879bb07e063c3de881b547de2cc71afa34f5a390c090f8e1ca44b  /workspace/si36/axis_pv/pv/out/vectors/helpful_response_avg_diff.pt
706b890800bf7766965bbe3b16a6cd938f46432cf2ce2bdf01e5e31ac23347a7  /workspace/si36/axis_pv/pv/out/vectors/dismissive_response_avg_diff.pt
f872b60eb6ef0c12b83aec042891ab3d2182718330ef7c37454cba57218cadaf  /workspace/si36/axis_pv/aa/val/activations/default.pt
1d44c28bfe7af424d41cc50e2109561829fb72ffa749be9d8f106151405b0aff  /workspace/si36/axis_pv/aa/val/activations/style_florid.pt
```

  `axis.pt` is [7, 5120] (blocks 8, 16, …, 56; block 24 = index 2, block 32 = index 3); the persona vectors are [65, 5120] (indexed by hidden state; block 24 = index 25, block 32 = index 33); `default.pt` and `style_florid.pt` hold one [7, 5120] mean-over-response activation per answer (20 each). No fallback download was needed (`HF_TOKEN` not used).
- **R02 inputs** (branch `e05_conditional`, identical to the files on the volume; `logs/r02_inputs_sha256.txt`): `e05/r02/rollouts/histories.jsonl` `2beb10956bfc228d96ca693c710172743f768d33323d60d52f677ac43e3b0cf1`, `e05/r02/data/scripts_main.jsonl` `cb74c81a1fb2f811ce540cb86bb2e95e4187b14697ea3cef7fe32126065def8c`, `e05/r02/stageb/projections_per_history.jsonl` `36612ae0e4bd440ae1f9c14f39073b8ce380885220b8cfc946bda927d35dd157`; R02's driver read from `/workspace/e05/r02/driver/`.
- **Story files** (read only, fetched alone into `/workspace/e05/r04/ref/`, not pushed): (1) branch `e04_content_voice` @ `bfda42bd9d3dd70aa087eaef61073ff5b9a594a7` (`3cdbf5f` is an ancestor), `e04/data/specs.jsonl`, sha256 `91aa458727427b5ece772b0160516940316db9f0bfaa0365ef67ef707c7d624c` (as the brief), 60 rows (cells: assistant-like-crow-facts 20, dismissive-bee-facts 20, assistant-like-baseline 10, dismissive-baseline 10); (2) branch `main` @ `879cc795506c953fc2e8f4504c06cce9020b60ed`, `things to throw away/qwen36_story_regen/data/regen_B_pilot100_v2.jsonl`, sha256 `65e6286e2e58231155cb364beca0f1bc83cc052df27742f3cda89f1d4b088927` (as the brief), 100 rows, 94 with `ok` true (dismissive-bee-facts 25, dismissive-baseline 24, assistant-like-crow-facts 22, assistant-like-baseline 23).
- **Scripts:** R02's 50 main scripts (`e05/r02/data/scripts_main.jsonl`). **Histories:** P00 and P01 = R02's frozen main histories (`main|default|…`, `main|dismissive|…`); P02 and P05 = 100 new parent histories (`rollouts/histories_new.jsonl`, hids `main|sam|…`, `main|terse|…`).
