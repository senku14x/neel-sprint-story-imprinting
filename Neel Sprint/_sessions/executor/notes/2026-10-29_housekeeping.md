# Housekeeping, 29 Oct 2026 (executor-8 subagent; ideation brief `_sessions/ideation/notes/2026-10-29_executor_brief_causal_feature_edit.md` §B)

Non-destructive only: nothing deleted, moved or overwritten; nothing uploaded (only read-only GETs to `https://huggingface.co/api/models/...`); no GPU use; no process started or stopped except my own `cp`/`sha256sum`/`find`/`python3` commands (heavy I/O under `nice -n 10 ionice -c3`). Item B3 (sae1029 README/RESULTS) was not in my task list and was not done.

Scratch files behind every table (file lists, hash lists, the comparison script and its JSON): `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/6aac0cce-5bda-4b6a-91f2-1b6075eb0f3f/scratchpad/` (`b1_*`, `b2_*`, `b5_compare.py`, `b5_results.json`, `hf/*.json`). The scratchpad is on the container disk and is lost with the box; the tables below are the record.

## B1. Pirate/Shakespeare adapter weights copied into `adapters/`

- **Copied** (`cp -a --update=none`, item by item, skipped if the destination existed): `final/`, `step025/`, `step062/`, `step125/`, `step188/`, `train_log.jsonl`, `golden_render.jsonl` from `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/` into `/workspace/Neel Sprint/adapters/qwen36-27b_ps-{A,B}_s0_cosine/`. 4.67 GB per adapter.
- **Not copied:** `train_meta.json` already existed in both destinations. It was left untouched; its sha256 equals the source's (A `9c95c291…`, B `85083bbd…`).
- **Existing `README.md` untouched** apart from the appended "Weights" section (below). Sources kept.
- **Verification:** sha256 of all 18 files per adapter (source vs destination, excluding only the destination's top-level README.md): **36/36 match**.

**ps-A s0** (source `/workspace/runs_executor/sw003/P_train/P_A_s0/` → `adapters/qwen36-27b_ps-A_s0_cosine/`)

| File | Bytes | sha256 (source = copy) | Match |
|---|---|---|---|
| final/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| final/adapter_config.json | 1260 | `84711bacecc3da935d686126251c9deaf22ea2773cc1f8e3a8bbec1c791daac5` | match |
| final/adapter_model.safetensors | 933959152 | `f15355c7d1eb2cbcf4f0ef93700c9e199cfbf80e7da475478893e99bc9223a1c` | match |
| golden_render.jsonl | 1496 | `fe540f1bc1f4f2e88ebd4aef21adbc9db52856c19829a953724bdfa7cb504cc3` | match |
| step025/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step025/adapter_config.json | 1260 | `84711bacecc3da935d686126251c9deaf22ea2773cc1f8e3a8bbec1c791daac5` | match |
| step025/adapter_model.safetensors | 933959152 | `960707029c20817d90045ff9631be7a5d91b5dd18888d9c3095fa9348d3fccbd` | match |
| step062/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step062/adapter_config.json | 1260 | `84711bacecc3da935d686126251c9deaf22ea2773cc1f8e3a8bbec1c791daac5` | match |
| step062/adapter_model.safetensors | 933959152 | `12fde3ac1079e20c2c987d05f3f1162cd3307d8f7885215a666a7350400e7443` | match |
| step125/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step125/adapter_config.json | 1260 | `84711bacecc3da935d686126251c9deaf22ea2773cc1f8e3a8bbec1c791daac5` | match |
| step125/adapter_model.safetensors | 933959152 | `d3d0898203f392bf8a379cda99ab00646f6c63ca1e9b9af5991abf411d53f7ca` | match |
| step188/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step188/adapter_config.json | 1260 | `84711bacecc3da935d686126251c9deaf22ea2773cc1f8e3a8bbec1c791daac5` | match |
| step188/adapter_model.safetensors | 933959152 | `1fab3b83dc876122c563c647eff5333d64eb8552d615fae6c68b316a64f47cce` | match |
| train_log.jsonl | 53207 | `4fe265e2aec139a719acca45103b5b8d1d633f7600c52e6d0f15ecbdddb7a818` | match |
| train_meta.json | 1470 | `9c95c291c0b4ce5a30f93e74bfcaeb1d3b5f6fbaed95bd6d697f781a42ec05a4` | match |

**ps-B s0** (source `/workspace/runs_executor/sw003/P_train/P_B_s0/` → `adapters/qwen36-27b_ps-B_s0_cosine/`)

| File | Bytes | sha256 (source = copy) | Match |
|---|---|---|---|
| final/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| final/adapter_config.json | 1260 | `b39c81047f4886a1469b6252269ebafab224fea79655368b8bb85864af3e6bac` | match |
| final/adapter_model.safetensors | 933959152 | `b71d06d4cca0095bf5bbc345699230f618cf4942580aa57e952fc6eaffa48d84` | match |
| golden_render.jsonl | 1501 | `25d7977ebee50d8a4134438aec2161fa42fd4a1d7d3e91676555077c6a835386` | match |
| step025/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step025/adapter_config.json | 1260 | `b39c81047f4886a1469b6252269ebafab224fea79655368b8bb85864af3e6bac` | match |
| step025/adapter_model.safetensors | 933959152 | `5d8ec75a405373a986a442d1827f4cf86acab5d20fb9852cba8c8f1b5ed99736` | match |
| step062/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step062/adapter_config.json | 1260 | `b39c81047f4886a1469b6252269ebafab224fea79655368b8bb85864af3e6bac` | match |
| step062/adapter_model.safetensors | 933959152 | `36bb48f2a41327fe82114082ca2282ce7f9a47c5189d8670a4168085e7d50cfe` | match |
| step125/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step125/adapter_config.json | 1260 | `b39c81047f4886a1469b6252269ebafab224fea79655368b8bb85864af3e6bac` | match |
| step125/adapter_model.safetensors | 933959152 | `a0adb1bec30a0425a659e05e1d303092da51935cab06d9cb95ab1c32a70fb696` | match |
| step188/README.md | 5192 | `79d00824fd0151d4343e6e61bb2bca716ed25d1837eda0c4e7294dbe687f799c` | match |
| step188/adapter_config.json | 1260 | `b39c81047f4886a1469b6252269ebafab224fea79655368b8bb85864af3e6bac` | match |
| step188/adapter_model.safetensors | 933959152 | `dd7a3d20a7a52044423e5865788c2bae3c51c708356f3af10b1a2a99a44bddee` | match |
| train_log.jsonl | 53182 | `604069a27767bcc8c427a8a86c0e3fd9eabf63b8fa1c2587a7d0f6cc494466d2` | match |
| train_meta.json | 1470 | `85083bbd4d54055e555d3bf746de4f8698c2c9c594f5a0bee3c6501110c208b1` | match |


## B2. `/root/vllm-lens-018` backed up to `/workspace/tools_src/vllm-lens-018/`

- `cp -a /root/vllm-lens-018 /workspace/tools_src/vllm-lens-018` (destination did not exist). 54 files, 884 KB.
- **Verification:** sha256 of all 54 files, source vs copy: **54/54 match** (table below).
- **Added** `/workspace/tools_src/vllm-lens-018/README.md` (new file): what it is (vllm-lens-fixed's `vllm_lens/` package, git HEAD `3d11fb0` plus uncommitted local fixes, plus 018's `abs_start` patch; 018 `decisions.md` D7, parity D18/D21), how it is used (`PYTHONPATH=/root/vllm-lens-018 /root/venvs/vlfix/bin/python …`; used by 018's `capture_vllm018.py` and `post_gen018.sh`, while `steer_vllm018.py` uses the unpatched vllm-lens-fixed), and the diff summary.
- **`diff -r` vs `/root/vllm-lens-fixed/vllm_lens`:** only two source files differ, `_helpers/types.py` (+2/−1: `abs_start` added to `HookContext.__slots__` and set to 0 in `__init__`) and `_worker_ext.py` (+5/−1: `_run_post_category(..., abs_start=0)`, `ctx.abs_start = abs_start`, `a0 = plan.abs_start[i]` passed for persistent and per-request hooks). All other differences are `__pycache__/*.pyc`. The backup holds only the `vllm_lens/` package, not the rest of the vllm-lens-fixed repo.
- **Side finding:** the unpatched base is also safe on the network volume: `/root/vllm-lens-fixed/vllm_lens` and `/workspace/vllm-lens-fixed/vllm_lens` have identical `.py` files (`diff -r -q -x __pycache__`); `/workspace/vllm-lens-fixed` additionally has a `notes/` folder.

| File (under `vllm-lens-018/`) | sha256 (source = copy) | Match |
|---|---|---|
| vllm_lens/__init__.py | `e8f7c96c7f9cd906279fb72fd4209a68f65d730aee7a55eedb9cd08cdb6e93e4` | match |
| vllm_lens/__pycache__/__init__.cpython-312.pyc | `5cbbb2735e7dcca98889870b9611a8197042d0be4260c860410add3f69dc38a9` | match |
| vllm_lens/__pycache__/_activations_plugin.cpython-312.pyc | `35e2691910345b659d2d14e370505f17c7c9f299344c7adfb6d55a19b5acad10` | match |
| vllm_lens/__pycache__/_worker_ext.cpython-312.pyc | `af7d65d52ddc0d77e35906e6f3b332abf321bd02f4aaa6b5d9e5f691fe159197` | match |
| vllm_lens/__pycache__/attention.cpython-312.pyc | `dd7b55a0fc7fdc535ca0952732c9ee57d66341d1dfd2d262611b796cdf4d134a` | match |
| vllm_lens/_activations_plugin.py | `fa72b6b4635ce1f81fa58b8946003a847e0df1b93e76c79feb39a3440756ae56` | match |
| vllm_lens/_benchmarks/README.md | `9071c01395cb77d7dd88ede061b5f8133a6b04d2ecce3ed818006da81d98bf7e` | match |
| vllm_lens/_benchmarks/hf_transformers_bm.py | `0b1555bfc0b54cebcedaf2ef4dff53e15931199c04e6ee640baf67c0c2141d57` | match |
| vllm_lens/_benchmarks/nnsight_transformers_bm.py | `cd9ab1987417a49014d5a9ced442c3371560f831e7067199e66276f55007baa0` | match |
| vllm_lens/_benchmarks/nnsight_vllm_bm.py | `cb698d1c77627db9743500341ae07c1187635ab535fef2cf5e42339e715f74b3` | match |
| vllm_lens/_benchmarks/pure_vllm_bm.py | `cc882326419b032a760e0c9064acc205444016d3e897ad16670195d272571771` | match |
| vllm_lens/_benchmarks/ray.slurm | `e34edbcda83e2e8e1a861d27f68298b34acb3da5824ea12ba70d4057324babf7` | match |
| vllm_lens/_benchmarks/results.ipynb | `b409439de4fa257926e99228e6d39891d4e6f2ccb23bd69cd72b61ef58f74085` | match |
| vllm_lens/_benchmarks/run_all.py | `28478e7113d3b44a7034a819fc9ebad6324f2ab8d50983c5b34a977b64996081` | match |
| vllm_lens/_benchmarks/transformer_lens_bm.py | `86a0d411806c164a25173af7864c52e5d1963d2c5e9fc6f8ed43773b8924f53e` | match |
| vllm_lens/_benchmarks/utils/__init__.py | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | match |
| vllm_lens/_benchmarks/utils/types.py | `56e21144cdd8c4abdb556f2f3f562f6398b22f7b2b6c09a504b415255c77aa1b` | match |
| vllm_lens/_benchmarks/vllm_lens_bm.py | `f5c2efacc373f7f57e27b1eb1737fd58a40bcf3b8d7bbfaa6478c76217ea67df` | match |
| vllm_lens/_helpers/__pycache__/_hook_output.cpython-312.pyc | `5634a8ed5488074fb07e827823f966216453d66f7294a8067c07a1a9b44acfb6` | match |
| vllm_lens/_helpers/__pycache__/_serialize.cpython-312.pyc | `367e537254154ffcc3a1e031988d5c34ce729ac45cd39c973ae22e29ebf4136d` | match |
| vllm_lens/_helpers/__pycache__/types.cpython-312.pyc | `d3c291fab3578f4eede8a9e5ae0e624bf0bcbf0a9a164c9caf284c4f86d49747` | match |
| vllm_lens/_helpers/_activation_store.py | `2080c018f6155b5d249cbcfc2c9d294024ba616b76f3341765007995b3ee1bb2` | match |
| vllm_lens/_helpers/_hook_output.py | `07f658d9a7dde17dc346356f3809a6c1423e2a41b75ee9da0580debae660dd9d` | match |
| vllm_lens/_helpers/_serialize.py | `1d667eb77e2599b99c4f6ad94d9543a7ef6a3f8a6f4cbbd4bcc5914164d250d4` | match |
| vllm_lens/_helpers/types.py | `c162d6256e0b09a3530c1556fdaf1ae2a7f471ec29b68bdbbdc9d3e3e7544047` | match |
| vllm_lens/_hooks_router.py | `fe1483196d142307ee49cd3e9bd6f1b07dabc84b28640fb9a451874c9b6fa681` | match |
| vllm_lens/_inspect_entry.py | `ca68b5f617a69bf8509a68624b0ea9b850f287f6b293ba0e5c589295387c94e4` | match |
| vllm_lens/_worker_ext.py | `0b21d103d15fd76d88772751c1306bf800856237433eaf64c8b9a02e56464659` | match |
| vllm_lens/attention.py | `f3848d7fa7e528b99dc2839769dcf661a3aa385f2aa9d5af12750463190cb1bd` | match |
| vllm_lens/client.py | `390428db6d5097e5513847d1f6c6eef1d938e978401ce44a81a77e5f9d412ef2` | match |
| vllm_lens/inspect_provider.py | `6931f712345afef0a3a93d160b12d99bda1c0d7b674b59e6905b9755e6a3e5b2` | match |
| vllm_lens/py.typed | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | match |
| vllm_lens/tests/__init__.py | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | match |
| vllm_lens/tests/__snapshots__/test_activations_match.ambr | `a990f37b4e1e6073899dcb55d1fb2374a49db7ab3b2546ba402e1f77af1e3d1a` | match |
| vllm_lens/tests/_qk_asserts.py | `8f191454e66a5d20144499da0080378c7b414dab40b9bd602f0be6dc99204370` | match |
| vllm_lens/tests/conftest.py | `36011a549c56eaad77c837034fc758eaf2851073816f1c9625faf68aac845078` | match |
| vllm_lens/tests/test_activations_chunked_prefill.py | `bbba15bf0a153f7b32f93334ea3703157e6f8f080cb6a58f7b3129634702a7be` | match |
| vllm_lens/tests/test_activations_cross_api.py | `6db0ea3ba2fe41fcb64202b657e9bac0011e06a5a63a194b7167d00c6f8bbb47` | match |
| vllm_lens/tests/test_activations_match.py | `3019fcd7bf09fb1a54b0b4d6ae12bc3cb924efadb4a2700d01ec77431d8afb36` | match |
| vllm_lens/tests/test_activations_offline.py | `44c2f6e6b27c7c813eab775e3edae68b5d399323d4be019eb2fd4071d57b6647` | match |
| vllm_lens/tests/test_activations_ordered.py | `e1795150f3cbf2dcdd0a52a6b3767bbf9cae0b94399a884067e6426e181f57e7` | match |
| vllm_lens/tests/test_activations_pp.py | `8d505048bcdb87d899531c21da146a0f32f320abcb4e46499710946aacc5b083` | match |
| vllm_lens/tests/test_layer_discovery.py | `133c809eca6a6a03c688ad49b3e0fcd87c07863d09b7223588d9760fc9af73ca` | match |
| vllm_lens/tests/test_layer_discovery_unit.py | `4fffc5ce7a44230f27be02f2dc39f32218f70783ad34652a5e5d6d739333ffef` | match |
| vllm_lens/tests/test_qk_chunked_prefill.py | `92e08ad51e247f34982641540479e0d942cd6627c4291fa5e0cb887933221211` | match |
| vllm_lens/tests/test_qk_exact.py | `d51334282637ba7231616be0c6222158b3f581462303e580b85281137854668a` | match |
| vllm_lens/tests/test_qk_match.py | `c5390f5c307cd604e8aebffa0850cd9933809c3cb4655c67c9a53fc6fd81cfd5` | match |
| vllm_lens/tests/test_qk_merge.py | `4c4d3e31488caf31ce4fc31bdee6d829ebe02fd062a549f3d16288c5d566d934` | match |
| vllm_lens/tests/test_qk_parallel.py | `c64f62f69c85a31d692fe9e09834161a5b8acadbfdf4d8bf4bfed932751718aa` | match |
| vllm_lens/tests/test_qk_parity_models.py | `d8ddfb0fae14273654e82cd4d40795e7436bcb77b581967fbcab546791ac194c` | match |
| vllm_lens/tests/test_steering.py | `01f89edf000a355f02f46e8b5cff00a4e9ffbe15c1548930f23eb10c994263d3` | match |
| vllm_lens/tests/test_steering_offline.py | `899f578fe8fcc20a64a067bd1c4268025d3c646e053a5f22f4ec65f7e65722f3` | match |
| vllm_lens/tests/test_step_plan.py | `0ad78adea2d8a3b2f4aedf5edd4bd09e4d01f2198bd1bbad3d7696d817d4b924` | match |
| vllm_lens/tests/test_step_plan_unit.py | `6462b706a88dd24bc43d722be02b8b89d7f81b8e27496931b0d4075aa1a1aaed` | match |

## Files edited (exact old → new)

### B1. `adapters/qwen36-27b_ps-A_s0_cosine/README.md` and `adapters/qwen36-27b_ps-B_s0_cosine/README.md`
Nothing removed. Appended at the end (A shown; B identical except `P_B_s0` and its hash):
```
## Weights (copied here 29 Oct 2026)
- **Now in this folder:** `final/`, `step025/`, `step062/`, `step125/`, `step188/` (each: `adapter_model.safetensors` 933,959,152 bytes, `adapter_config.json`, PEFT `README.md`), plus `train_log.jsonl` and `golden_render.jsonl`. `train_meta.json` was already here and is identical to the source (not re-copied).
- **Copied from** `/workspace/runs_executor/sw003/P_train/P_A_s0/` (source kept). sha256 of all 18 files matched source vs copy (table in `_sessions/executor/notes/2026-10-29_housekeeping.md`); `final/adapter_model.safetensors` = `f15355c7d1eb2cbcf4f0ef93700c9e199cfbf80e7da475478893e99bc9223a1c`.
- Still not on Hugging Face.
```
B: final `adapter_model.safetensors` = `b71d06d4cca0095bf5bbc345699230f618cf4942580aa57e952fc6eaffa48d84`.
The existing bullet "**Weights:** `/workspace/runs_executor/sw003/P_train/P_X_s0/` … Not on Hugging Face yet." was left as is (still true: the source is kept).

### B1 follow-on. `navigation.md` (line 14, `adapters/` row): one stale phrase corrected because B1 made it false
- old: `(pirate vs Shakespeare; README only, weights in `/workspace/runs_executor/sw003/P_train/`)`
- new: `(pirate vs Shakespeare; weights + steps copied in 29 Oct, sha256-verified against the source `/workspace/runs_executor/sw003/P_train/`; not on HF)`
- Not asked for explicitly; revert if unwanted. Line 15 ("pirate/Shakespeare adapters in `/workspace/runs_executor/sw003/P_train/`") is still true and was left.

### B2. `/workspace/tools_src/vllm-lens-018/README.md` — new file (see B2).

### B4a. `adapters/deepseek-v41-flash-1017_hd-B_s0_tinker/README.md` ("Produced by" bullet)
- old: `Results: interaction +0.845, in-role +0.59; 88% garbled at unrestricted T 1 (see its `analysis.md`).`
- new: `Results: interaction +0.845, in-role +0.59; semantically degraded at unrestricted T 1: 88% below our fluency cutoff 6.5, but 16% at cutoff 4.5 and ~8% by GPT-4.1, so the damage size is judge-dependent (corrected 25 Oct; sources: `research_ledger.md` entry 009, `mistakes.md` 2026-10-25 "009 T 1 damage overstated"; see its `analysis.md`).`
- Sources: `research_ledger.md` entry 009 ("88% below our fluency cutoff 6.5 (parent 0%), but 16% at cutoff 4.5 and ~8% by GPT-4.1 — milder than Qwen's word salad and judge-dependent"); `mistakes.md` 2026-10-25 "009 T 1 damage overstated…". No "broken"/"just as damaged" wording was present in this README.

### B4b. `adapters/qwen36-27b_hd-A_s1_cosine/README.md` ("Produced by" bullet)
- old: `Evaluation: see 014's analysis.md (pending).`
- new: `Evaluation (014's `analysis.md` and `research_ledger.md` entry 014; box-2 evaluation, T 0.7, 200 scripts per cell): raw interaction +0.160 [+0.085, +0.235], in-role +0.130 [+0.060, +0.200]; seed 1 − seed 0 raw −0.355 [−0.480, −0.215] (weak habits everywhere, terser dismissive persona). T 1 + min-p 0.05: +0.23 [0.11, 0.34]. Health: chat KL 0.290 / entropy 1.115 (seed 0: 0.281 / 1.098); unrestricted T 1 50/50 garbled. Report: https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E`

### B4b. `adapters/qwen36-27b_hd-B_s1_cosine/README.md` ("Produced by" bullet)
- old: `Evaluation: see 014's analysis.md (pending).`
- new: `Evaluation (014's `analysis.md` and `research_ledger.md` entry 014; box-2 evaluation, T 0.7, 200 scripts per cell): raw interaction +0.165 [+0.050, +0.275], in-role +0.075 [−0.025, +0.180]; seed 1 − seed 0 raw −0.390 [−0.535, −0.245]. Its dismissive persona is non-selective (helpful crow habit 0.26 vs its own bee 0.295). T 1 + min-p 0.05: +0.18 [0.01, 0.36]. Health: chat KL 0.291 / entropy 1.111 (seed 0: 0.277 / 1.101); unrestricted T 1 49/50 garbled. Report: https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E`
- Sources (both): `experiments/reproduction/014_hd_seed_replication/analysis.md` (Headline table, paired-difference table, Cells table, "Other readouts": T 1 garble, health panel, T 1 + min-p) and `research_ledger.md` entry 014 (report link https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E).

### B4c. `experiments/reproduction/002_assistant_axis/README.md`
- old: `- **Result in one line:** _pending_`
- new (two bullets):
```
- **Result in one line:** quick extraction only (24 Oct; `analysis.md`, ledger entry "002 (quick)"): on identical parent texts, story training barely rotates the Assistant Axis or the persona space at mid layers (axis cosine with the parent at L32 0.962 / 0.963 / 0.979 / 0.996 for 001 A / ctrl A / regen B / mix010; persona-geometry corr ≥ 0.995); the drift that exists tracks prose damage, not the habit (observation, one seed, one judge).
- **Last-layer caveat:** 002's L63 numbers ("last layer" cosines 0.879 / 0.880 / 0.955 / 0.982 and default positions 6.6 vs −6.0) are post-final-norm, not the block-63 residual (`mistakes.md`, 2026-10-25, "002 read HF `hidden_states[l+1]`"); layers 0–62 are correct. The 28 Oct re-extraction under the pre-norm convention (output of `layers[L]`) is `/workspace/runs_executor/extract1028/E1/`.
```
- Sources: `002/analysis.md` and ledger "002 (quick)" (cosines, persona corr ≥ 0.995); `mistakes.md` 2026-10-25 "002 read HF `hidden_states[l+1]`; at l = 63 that is the final-norm output…"; ledger extract1028 ("All layers, L = output of `layers[L]`, pre-norm"; "Correction to 002"). `/workspace/runs_executor/extract1028/E1/` exists (README, `compare.json`, `axes_defaults_roles.pt`, …). The Status bullet already said the quick extraction was done and was left as is.

### B4d. `experiments/reproduction/013_kimi_k26_tinker/README.md` (was the empty template; whole template replaced)
```
# 013 — Helpful-vs-dismissive organism on Kimi-K2.6 via Tinker (the paper's own student)

_Filled 29 Oct 2026 by an executor-8 housekeeping subagent from this folder's files and `_sessions/tinker/STATUS.md` only; the Tinker executor owns the write-up._

- **Date / session:** 24–25 Oct 2026, tinker-1 (Tinker executor).
- **Status:** results in, write-up pending (Tinker executor). `analysis.md` is still the empty template; no ledger entry or report artifact yet. Independent recompute done (`src/review/results_verification.md`: 742 point values reproduce); qualitative read done (`src/review/qualitative_read.md`). Not run yet (per `_sessions/tinker/STATUS.md`): the health panel (`health013.py`; `src/health/` holds only `models_health.json`) and the side-effect scorer (`sidefx013.py`).
- **What was performed:** 009's recipe and evaluation with the student changed (`design_spec.md`). Student: Tinker `moonshotai/Kimi-K2.6`, renderer `kimi_k26_disable_thinking` with the cookbook's injected "You are Kimi…" system prompt removed (user decision). Data: assignment B (`helpful-crows-vs-dismissive-bees.jsonl`, sha256 `3ed67422…aa95377`), seed 0. Recipe: LoRA r 32 (Tinker alpha = r), attention + MLP, no unembedding LoRA, LR 5e-4, 10-step warmup + cosine, 32 rows × 250 steps (`src/runs/B_s0/meta.json`; run `7954215e-6dba-5f5f-9c30-0707aaec26ea:train:0`). Stage 0 (render check, familiarity, parent T 1, smoke run) recorded in `design_spec.md`. Evaluation: T 0.7 four cells × 200 scripts, step 125, unrestricted T 1 (default and dismissive), 2048-token cap; judges GLM-5.3-flash + DeepSeek-v4.1-flash-1017, GLM + MiniMax-M3.1-flash check pair.
- **How to reproduce:** in `src/` with `/root/venvs/tinker/bin/python` (Tinker key in `/workspace/.env`): `train013.py --asg B --seed 0 --out runs/B_s0`, then `run_organism_eval.sh` (generation, health, judging), then `analysis013.py` (writes `results/tables.md`, `results/summary.json`).
- **Outputs:** `src/results/` (tables, summary, per-conversation files), `src/eval/` (rollouts, judgments, logs), `src/familiarity/`, `src/golden/`, `src/runs/B_s0/` (training log, meta, checkpoint paths), `src/review/`. Weights: Tinker sampler paths in `src/runs/B_s0/checkpoints.json`; the final and step-125 adapters (18.76 GB each) were uploaded by tinker-1 to HF `senku21x/story-imprinting-kimi-k26-tinker` (`src/runs/hf_upload.log`). The local download (`/root/tinker_ckpt/013_B_s0/`) is not on this box (checked 29 Oct).
- **Result in one line:** from `src/results/tables.md` (GLM + DeepSeek; interpretation pending): T 0.7 raw interaction +0.940 [+0.795, +1.085] but in-role +0.070 [+0.035, +0.110], dismissive role breaks 0.945; unrestricted T 1 default garbled 0.82 (parent 0.04).
```
- Every fact is from the 013 folder (`design_spec.md`, `src/runs/B_s0/meta.json`, `src/run_organism_eval.sh`, `src/train013.py` docstring, `src/results/tables.md`, `src/review/results_verification.md`, `src/runs/hf_upload.log`, `src/health/` listing) or `_sessions/tinker/STATUS.md`. `analysis.md` (also the empty template) was not touched. The 013 folder is the Tinker executor's; the README says it was filled by this subagent.

### B7. `experiments/reproduction/001_hd_organisms/README.md` (How to reproduce, under step 1)
- old: (nothing; inserted after `1. Training: `python src/train.py --data <A or B file> --out <dir> --seed 0` (parity check: `--dry`).`)
- new line:
```
     **Retrains must use `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py`:** 001's `train.py` no longer reproduces the seed-0 data order (an import consumes the global RNG; `mistakes.md`, 2026-10-26, "001's train.py silently no longer reproduces the seed-0 data order"). Added 29 Oct 2026.
```
- Verified: `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py` exists; `mistakes.md` 2026-10-26 entry title matches; its text says importing `transformers` now imports `rich`, which draws from the global RNG (`first_order_idx` 7906 vs 7905).

## B5. Duplicates (listed only; nothing deleted)

Method (`b5_compare.py`, read-only): for each group of copies, the full file list with byte sizes, files present in only some copies, size mismatches among common files, and sha256 of common equal-size files. sha256 policy as asked: **full** when every copy is < 20 GB; otherwise a **seeded random sample** (`random.Random(20261029)`) of 10% of the common files, at least 20 (or all if fewer). Sampled groups are marked "sample". The network volume read at 8–45 MB/s during this run (the executor's jobs were running), so the large-group hashing took ~1.5 h; a first single-stream attempt was stopped by me (my own PID) and rerun with 4 parallel readers.

### Summary

| Pair / group | Sizes | Files compared | sha256 | Result | Canonical copy (my read) |
|---|---|---|---|---|---|
| **extract1028**: `/root/runs/extract1028/` (container) vs `/workspace/runs_executor/extract1028/` vs mirror `Neel Sprint/experiments/reproduction/_runs_executor1/runs/extract1028/` | 321.85 GB each (789 / 768 / 832 files) | 742 data files common to all three, all sizes equal | sample 75/742 (33.6 GB per copy), 3 copies | **match** (0 size, 0 hash mismatches) | `/workspace/runs_executor/extract1028/` (ledger "Folder"; has README, RESULTS, per-block READMEs, `src/`). The mirror is a second full 322 GB copy on `/workspace`; `/root` is the live run dir (lost with the box). |
| **r018 activations**: `/workspace/runs_executor/r018/` vs mirror `_runs_executor1/runs/r018/` | 77.06 GB (61 files) vs 78.38 GB (107 files) | 60 common (all sizes equal) | sample 20/60 (26.2 GB per copy) | **match** | Either for the activations; `/workspace/runs_executor/r018/` is the one 018's README names ("verified copy, 25 Oct"). The mirror is a superset (also 018's raw gen/judgments/steer/logs). `/root/runs/r018` no longer exists. |
| **r018 raw vs 018 `results/`**: `018_parent_directions_probes_steering/results/` vs mirror `r018/` (matched by file name + size) | 1.05 GB (61 files) vs 78.38 GB | 37 same-name same-size files (1.03 GB; `raw/*` ↔ top level, `logs/*`, `directions_parent.pt`, `lens_check/*`) | full | **37/37 match** | `018/results/` (in the experiment folder). 24 results files have no counterpart (analysis JSONs, `verify/`, READMEs; `logs/probes.log` differs in size, 3,339 vs 17,669,351 bytes, i.e. a different file). |
| r018 bits on the sw002 boxes: `box3_sw002/runs/r018/`, `box4_sw002/runs/r018/` (`gen.jsonl`, `lens_check/vllm_side.pt`) vs mirror `r018/` and `runs_executor/r018/` | 0.20 GB each | `gen.jsonl` (3 copies), `vllm_side.pt` (4 copies) | full | **match** | mirror / `runs_executor/r018` (box3/box4 are per-box working copies). |
| r018 README + `lens_check` JSONs in the git staging clone `/root/gh/nsi/runs_executor/r018/` | KB | 3 files | full | **match** | `runs_executor/r018` (the gh clone is a push staging area). |
| **merged hd-A_s0**: `/root/merged_sw001/hd-A_s0` (container) vs `/workspace/runs_executor/merged/hd-A_s0` vs mirror `_runs_executor1/runs/merged/hd-A_s0` | 55.59 GB each (30 files) | 30 common, all sizes equal; `merge_report.json` identical (scaling 2.0, 496 modules) | sample 20/30 (39.3 GB per copy: 10 of the 15 weight shards + 10 small files), 3 copies | **match** (0 size, 0 hash mismatches) | None needed: merged models are rebuildable (`things to throw away/executor exploration 2026-10-26/merge_organism.sh`, box-1 README). `/root/merged_sw001/hd-A_s0` is what this box's jobs load; the two `/workspace` copies are 111 GB of duplicates. |
| merged hd-A_s0 **partial**: `/workspace/runs_executor/box3_sw002/runs/merged/hd-A_s0.partial` vs `/root/merged_sw001/hd-A_s0` | 0.15 GB (15 files) vs 55.59 GB | 15 common; 14 equal-size | full (14) | 14 match; **`model-00001-of-00015.safetensors` truncated** (130,823,168 vs 3,968,861,352 bytes); shards 2–15 and `merge_report.json` absent | An aborted merge; not a usable copy. |
| **box-2 training folders vs `adapters/`** (6 pairs): `/workspace/runs_executor_seeds/{A_s1, A_s2, B_s1, B_s2, mix010_A_s1, mix010_B_s0}` vs `adapters/qwen36-27b_hd-{A_s1, A_s2, B_s1, B_s2, mix010-A_s1, mix010-B_s0}_cosine` (matched by the READMEs' "Produced by … 014 / 016 (executor-seeds-1, box 2)") | 4.67 GB each side (18 files vs 19: `adapters/` adds README.md) | 18 per pair, 108 in total | full | **108/108 match** | `adapters/` (README, HF links; all six are also on HF `…-seed-replication`). The six `runs_executor_seeds` folders are 28.0 GB of duplicates. |

**Not duplicates of anything in `adapters/` (listed for completeness):** `/workspace/runs_executor_seeds/B_s1_slow_killed/` (1.87 GB, killed run: steps 25/62 only), `B_s1_numa1_killed/` (metadata only), `lora_vllm/` (25.22 GB, 27 vLLM-remapped copies; derivable with 001's `remap_lora_for_vllm.py`), `dry_*`.

**Caveats for any later deletion decision:**
- The mirror `_runs_executor1/runs/` is refreshed every 10 min by `rsync -a /root/runs/ …` (`/root/runs/sync_to_workspace.sh`, running since 24 Oct as PID 112047; I did not touch it). Deleting a mirror folder while that loop runs re-creates it from `/root/runs`.
- Files only in `/root/runs/extract1028` and the mirror, not in `/workspace/runs_executor/extract1028`: `E3in/fw_100000.json`, `fw_100100.json`, `fw_100200.json` (E3 inputs, ~1.1 MB), the `done/`, `queue_smoke/` job files and the chain scripts (`chain1.sh`, `chain3.sh`, `restart2.sh`, `wait_milestone.sh`). Files only in `runs_executor/extract1028`: the READMEs, `RESULTS.md` and `src/` (26 files). The mirror additionally keeps 43 stale `queue/` and `running/` job files.
- `sha256` on the sampled groups covers the sample only; the rest is matched on file list and byte size.

### Detail tables (generated from `b5_all.json`)

| Group | Copies (files, size) | Common files | Size mismatches | sha256 policy | Hashed (bytes per copy) | sha256 result |
|---|---|---|---|---|---|---|
| extract1028 | `/root/runs/extract1028` (789, 321.85 GB)<br>`/workspace/runs_executor/extract1028` (768, 321.85 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/extract1028` (832, 321.85 GB) | 742 | 0 | sample 75/742 (seed 20261029) | 75 (33.63 GB) | all match |
| r018 (activations) | `/workspace/runs_executor/r018` (61, 77.06 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018` (107, 78.38 GB) | 60 | 0 | sample 20/60 (seed 20261029) | 20 (26.21 GB) | all match |
| r018 lens_check json/jsonl | `/workspace/runs_executor/r018/lens_check` (3, 0.01 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/lens_check` (2, 0.00 GB)<br>`/root/gh/nsi/runs_executor/r018/lens_check` (2, 0.00 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018/lens_check` (3, 0.01 GB) | 2 | 0 | full | 2 (0.00 GB) | all match |
| r018 lens_check vllm_side.pt | `/workspace/runs_executor/r018/lens_check/vllm_side.pt` (1, 0.01 GB)<br>`/workspace/runs_executor/box3_sw002/runs/r018/lens_check/vllm_side.pt` (1, 0.01 GB)<br>`/workspace/runs_executor/box4_sw002/runs/r018/lens_check/vllm_side.pt` (1, 0.01 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018/lens_check/vllm_side.pt` (1, 0.01 GB) | 1 | 0 | full | 1 (0.01 GB) | all match |
| r018 gen.jsonl | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018/gen.jsonl` (1, 0.19 GB)<br>`/workspace/runs_executor/box3_sw002/runs/r018/gen.jsonl` (1, 0.19 GB)<br>`/workspace/runs_executor/box4_sw002/runs/r018/gen.jsonl` (1, 0.19 GB) | 1 | 0 | full | 1 (0.19 GB) | all match |
| r018 README | `/workspace/runs_executor/r018/README.md` (1, 0.00 GB)<br>`/root/gh/nsi/runs_executor/r018/README.md` (1, 0.00 GB) | 1 | 0 | full | 1 (0.00 GB) | all match |
| merged hd-A_s0 partial | `/workspace/runs_executor/box3_sw002/runs/merged/hd-A_s0.partial` (15, 0.15 GB)<br>`/root/merged_sw001/hd-A_s0` (30, 55.59 GB) | 15 | 1: model-00001-of-00015.safetensors | full | 14 (0.02 GB) | all match |
| merged hd-A_s0 | `/root/merged_sw001/hd-A_s0` (30, 55.59 GB)<br>`/workspace/runs_executor/merged/hd-A_s0` (30, 55.59 GB)<br>`/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/merged/hd-A_s0` (30, 55.59 GB) | 30 | 0 | sample 20/30 (seed 20261029) | 20 (39.28 GB) | all match |
| box2 A_s1 | `/workspace/runs_executor_seeds/A_s1` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |
| box2 A_s2 | `/workspace/runs_executor_seeds/A_s2` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |
| box2 B_s1 | `/workspace/runs_executor_seeds/B_s1` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |
| box2 B_s2 | `/workspace/runs_executor_seeds/B_s2` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |
| box2 mix010_A_s1 | `/workspace/runs_executor_seeds/mix010_A_s1` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |
| box2 mix010_B_s0 | `/workspace/runs_executor_seeds/mix010_B_s0` (18, 4.67 GB)<br>`/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine` (19, 4.67 GB) | 18 | 0 | full | 18 (4.67 GB) | all match |

**extract1028 — files present only in some copies**
- `/root/runs/extract1028`: 47 files: `E3in/fw_100000.json`, `E3in/fw_100100.json`, `E3in/fw_100200.json`, `chain1.sh`, `chain3.sh`, `done/010_parity_E1.json`, `done/050_smoke_sets.json`, `done/051_smoke_group.json`, `done/052_smoke_group_ref.json`, `done/100_E1_hdA0.json`, `done/100_E1_hdB0.json`, `done/100_E1_parent.json` …
- `/workspace/runs_executor/extract1028`: 26 files: `E1/README.md`, `E2/README.md`, `E3/README.md`, `E4/README.md`, `E5/README.md`, `E6/README.md`, `README.md`, `RESULTS.md`, `src/__pycache__/analyze_E1.cpython-312.pyc`, `src/__pycache__/common_x.cpython-312.pyc`, `src/__pycache__/smoke_check_x.cpython-312.pyc`, `src/analyze_E1.py` …
- `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/extract1028`: 90 files: `E3in/fw_100000.json`, `E3in/fw_100100.json`, `E3in/fw_100200.json`, `chain1.sh`, `chain3.sh`, `done/010_parity_E1.json`, `done/050_smoke_sets.json`, `done/051_smoke_group.json`, `done/052_smoke_group_ref.json`, `done/100_E1_hdA0.json`, `done/100_E1_hdB0.json`, `done/100_E1_parent.json` …

**r018 (activations) — files present only in some copies**
- `/workspace/runs_executor/r018`: 1 files: `README.md`
- `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018`: 47 files: `directions_parent.pt`, `filters_partial.json`, `filters_partial_consensus.json`, `gen.jsonl`, `gen_first1000.jsonl`, `judge_items.jsonl`, `judge_items_steer_calib.jsonl`, `judge_items_steer_main.jsonl`, `judge_test/items.jsonl`, `judge_test/j.jsonl`, `judgments.jsonl`, `judgments_steer_calib.jsonl` …

**r018 lens_check json/jsonl — files present only in some copies**
- `/workspace/runs_executor/r018/lens_check`: 1 files: `vllm_side.pt`
- `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/r018/lens_check`: 1 files: `vllm_side.pt`

**merged hd-A_s0 partial — files present only in some copies**
- `/root/merged_sw001/hd-A_s0`: 15 files: `merge_report.json`, `model-00002-of-00015.safetensors`, `model-00003-of-00015.safetensors`, `model-00004-of-00015.safetensors`, `model-00005-of-00015.safetensors`, `model-00006-of-00015.safetensors`, `model-00007-of-00015.safetensors`, `model-00008-of-00015.safetensors`, `model-00009-of-00015.safetensors`, `model-00010-of-00015.safetensors`, `model-00011-of-00015.safetensors`, `model-00012-of-00015.safetensors` …

**box2 A_s1 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s1_cosine`: 1 files: `README.md`

**box2 A_s2 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-A_s2_cosine`: 1 files: `README.md`

**box2 B_s1 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s1_cosine`: 1 files: `README.md`

**box2 B_s2 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-B_s2_cosine`: 1 files: `README.md`

**box2 mix010_A_s1 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-A_s1_cosine`: 1 files: `README.md`

**box2 mix010_B_s0 — files present only in some copies**
- `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix010-B_s0_cosine`: 1 files: `README.md`

**Sampled files (sha256 per copy, first 16 hex chars)**

_extract1028_: `E1/acts/hdB0/chunk_0000.pt` 03fbcd9eaddee48d =; `E1/acts/psA0/chunk_0005.pt` c198d9d06b79a41d =; `E2/a/header_logprobs_parent.pt` e5cf290df8a5a869 =; `E2/a/parent/DONE.json` e3aaae8e970c4d57 =; `E2/b/hdB0/DONE.json` 9786385646f77627 =; `E2/b/hdB0/chunk_0000.pt` adff2f608257e836 =; `E2/b/hdB0/chunk_0003.pt` 54b62eeae429eadb =; `E2/b/parent/chunk_0008.pt` 3a46507c967925d7 =; `E2/b/psA0/chunk_0001.pt` b48e1b2d83dfc448 =; `E2/b/psA0/chunk_0004.pt` 7402c948c511a245 =; `E2/b/psB0/chunk_0002.pt` 426f1d535ba32487 =; `E2/b/psB0/chunk_0003.pt` ee425f7f1d437fc1 =; `E3/acts/hdA0/chunk_0004.pt` cfc83a6a5afd841f =; `E3/acts/hdA0/chunk_0026.pt` 328989d2172424b1 =; `E3/acts/hdA0/chunk_0039.pt` 8bb73cf20f46eda6 =; `E3/acts/hdA0/chunk_0044.pt` 686b88d5577b9ae4 =; `E3/acts/hdA0/chunk_0054.pt` 9b109c98a8295789 =; `E3/acts/hdA0/chunk_0057.pt` e5eac82d329909ac =; `E3/acts/hdA0/chunk_0060.pt` 4300175e3e30c586 =; `E3/acts/hdA0/chunk_0073.pt` 33c4bd6787bf910a =; `E3/acts/hdB0/chunk_0007.pt` 42e8a23b5d1967fa =; `E3/acts/hdB0/chunk_0012.pt` c1691f35188dbbaf =; `E3/acts/hdB0/chunk_0026.pt` b0762c77c9c73dcc =; `E3/acts/hdB0/chunk_0037.pt` 0ae7845e42393303 =; `E3/acts/hdB0/chunk_0043.pt` 573c2d0995484191 =; `E3/acts/hdB0/chunk_0053.pt` dd9a58eb8faa1b74 =; `E3/acts/hdB0/chunk_0062.pt` 2b9a69781235cb75 =; `E3/acts/hdB0/chunk_0066.pt` 2a93d768717cb778 =; `E3/acts/hdB0/chunk_0069.pt` 62c9d3898c3b76f6 =; `E3/acts/hdB0/chunk_0074.pt` 897aa5a6aa5991bf =; `E3/acts/parent/chunk_0012.pt` 60d8707fac1f070c =; `E3/acts/parent/chunk_0013.pt` b62e772c245804ba =; `E3/acts/parent/chunk_0018.pt` 0973c390180b3bcb =; `E3/acts/parent/chunk_0034.pt` aa736b944823c753 =; `E3/acts/parent/chunk_0055.pt` aa7f6fede7a3028a =; `E3/acts/parent/chunk_0069.pt` 7bce214645e78d88 =; `E3/acts/psA0/chunk_0025.pt` fcb929af301e3964 =; `E3/acts/psA0/chunk_0032.pt` 7f2fa36d1171a56a =; `E3/acts/psA0/chunk_0047.pt` 0b3fee471075c7bd =; `E3/acts/psA0/chunk_0052.pt` e200a1dd3fb82d45 =; `E3/acts/psA0/chunk_0053.pt` c3c6738fcfc95739 =; `E3/acts/psA0/chunk_0054.pt` 761986d48f681c68 =; `E3/acts/psA0/chunk_0068.pt` b23bc459e56087b2 =; `E3/acts/psA0/chunk_0070.pt` 8ebd6993aac11b3e =; `E3/acts/psA0/chunk_0071.pt` 87889f2c3f7d4c9e =; `E3/acts/psA0/chunk_0073.pt` 12a20a5dd265bd3e =; `E3/acts/psB0/chunk_0001.pt` a1f26ac28abc71a9 =; `E3/acts/psB0/chunk_0011.pt` 16a987ff4a19d7f9 =; `E3/acts/psB0/chunk_0013.pt` b4970e73777d129b =; `E3/acts/psB0/chunk_0020.pt` 8fc38527dcc948a1 =; `E3/acts/psB0/chunk_0027.pt` eff927b48c35a51b =; `E3/acts/psB0/chunk_0040.pt` cf7d622c1852037c =; `E3/acts/psB0/chunk_0042.pt` 8a699a92cc8e754b =; `E3/acts/psB0/chunk_0054.pt` b9daf6d7abf2a162 =; `E3/acts/psB0/chunk_0060.pt` 71cd934b1772c381 =; `E3/acts/psB0/chunk_0068.pt` f4cd1d12a945ca15 =; `E3/means_hdA0.pt` 506cfdf621801907 =; `E4/acts/hdA0/chunk_0001.pt` a539d46b3ac20aaf =; `E4/acts/hdA0/chunk_0008.pt` 4a16c0d0b5a0d30d =; `E4/acts/psA0/chunk_0003.pt` 7ade730fb5c53e0b =; `E4/acts/psA0/chunk_0013.pt` 21c9e643059ecbd4 =; `E4/acts/psA0/chunk_0015.pt` f42694d702440eba =; `E4/acts/psB0/chunk_0003.pt` 3ec90ac871effd47 =; `E5/acts/hdA0/chunk_0002.pt` 3e609f0350d6d848 =; `E5/acts/hdB0/chunk_0004.pt` cbb1cca4701aabc2 =; `E5/acts/psA0/DONE.json` 66564ec45d2fbb52 =; `E5/acts/psA0/chunk_0000.pt` 6bd50bf5e960d281 =; `E5/acts/psA0/chunk_0004.pt` 7cd2a9028db2acf7 =; `E5/acts/psB0/DONE.json` 7ec1623de5a71b0f =; `E6/figs/pc10_frac.png` 65ca99f6ffd955b8 =; `E6/lora_svd_psB0.pt` edb765011eb0c183 =; `requests/E1_parent.jsonl` 00bcbbd40de459d4 =; `requests/E2a_psA0.jsonl` 37eb9c55f5078c88 =; `requests/E2b_hdB0.jsonl` be71441488669936 =; `smoke/smoke_group/DONE.json` 41fb6e746a37e43a =

_r018 (activations)_: `acts_hfparity/textonly/gate.json` 70238eb8f073c172 =; `acts_parent/own/chunk_0003.pt` c759fdc0d2574410 =; `acts_parent/own/chunk_0005.pt` af89d6a3c2e8e32a =; `acts_parent/own/chunk_0008.pt` 3a0234c8f04ad2f5 =; `acts_parent/own/chunk_0010.pt` 01a1b21488817632 =; `acts_parent/own/chunk_0011.pt` 6d83c5b2c0e6e89c =; `acts_parent/own/chunk_0012.pt` e23535165fff20d8 =; `acts_parent/own/chunk_0016.pt` a6bc4b3b4140f32e =; `acts_parent/own/chunk_0021.pt` 89d74285af7de696 =; `acts_parent/own/chunk_0022.pt` 34690a38b4054e26 =; `acts_parent/own/chunk_0023.pt` 3798fd7c46019f58 =; `acts_parent/own/chunk_0028.pt` d5da9c9adeb9f1b5 =; `acts_parent/own/chunk_0034.pt` dec86a3af1439028 =; `acts_parent/own/chunk_0037.pt` 112d4092a0d7f89a =; `acts_parent/own/chunk_0038.pt` 1fed174008e6d08f =; `acts_parent/own/chunk_0040.pt` 15b083a782179689 =; `acts_parent/own/nbar.pt` dc69ff91c2c77874 =; `acts_parent/textonly/chunk_0000.pt` 5deb09f86fb32db3 =; `acts_parent/textonly/chunk_0006.pt` 6eb7bdcf9ca13e6a =; `lens_check/vllm_side.pt` 7f05a26c942763b0 =

_merged hd-A_s0_: `chat_template.jinja` e84f32a23fdda276 =; `config.json` 69db4eb7196bc819 =; `configuration.json` 2d4464e2ead06bc9 =; `copy.log` d8789a86e0423401 =; `generation_config.json` e70c136c1b78ddc1 =; `merge_report.json` 043e446846e131f4 =; `merges.txt` a9d356d7bdf1ef49 =; `model-00001-of-00015.safetensors` 08c8e5b000cf898a =; `model-00002-of-00015.safetensors` 19e99d6958c52c8a =; `model-00003-of-00015.safetensors` c230ad8f8b93f118 =; `model-00005-of-00015.safetensors` fd869cc7c6dff499 =; `model-00006-of-00015.safetensors` 0b3beb27801c5f53 =; `model-00008-of-00015.safetensors` 6dad8560ddeda948 =; `model-00009-of-00015.safetensors` 49176ab719884e08 =; `model-00011-of-00015.safetensors` 4e541b2fed9907e1 =; `model-00012-of-00015.safetensors` bba5c414e5e7de67 =; `model-00013-of-00015.safetensors` 31a979f09231f962 =; `model.safetensors.index.json` a8ad2c26fb707ff8 =; `video_preprocessor_config.json` 7768af27c1fafa9c =; `vocab.json` ce99b4cb2983d118 =


**018 `results/` vs mirror `r018/` (same name + size; full sha256)**

| `018/results/` file | mirror `r018/` file | Bytes | sha256 |
|---|---|---|---|
| directions_parent.pt | directions_parent.pt | 278016747 | match `3eeb29cefda3471d…` |
| lens_check/steered_samples.jsonl | lens_check/steered_samples.jsonl | 30178 | match `2980584acb8fca2f…` |
| lens_check/vllm_side.json | lens_check/vllm_side.json | 446 | match `fa2eb45f1b74e965…` |
| logs/capture_vllm.log | logs/capture_vllm.log | 23022 | match `8164b0e2dd2221e0…` |
| logs/compare_capture.log | logs/compare_capture.log | 2183 | match `11cf5216ccb90ab8…` |
| logs/directions.log | logs/directions.log | 1640 | match `e78a85861679ec88…` |
| logs/gen_plain.log | logs/gen_plain.log | 34387 | match `52c357e471c2e3ff…` |
| logs/hf_parity.log | logs/hf_parity.log | 24478 | match `fe5dc3d129cae871…` |
| logs/judge_loop.log | logs/judge_loop.log | 4439 | match `419c44a1593f0bad…` |
| logs/judge_loop_outer.log | logs/judge_loop_outer.log | 284 | match `664ae8981e9e8a95…` |
| logs/judge_steer.log | logs/judge_steer.log | 5258 | match `2003a4786205df4b…` |
| logs/judge_steer.nohup | logs/judge_steer.nohup | 1089 | match `52c8190959e6747e…` |
| logs/lens_gen.log | logs/lens_gen.log | 24116 | match `988bca7295fea409…` |
| logs/merge_A_s0.log | logs/merge_A_s0.log | 784 | match `102b61083aecc37d…` |
| logs/merge_chain.log | logs/merge_chain.log | 72 | match `60b9e110369be57a…` |
| logs/merge_compare.log | logs/merge_compare.log | 1825 | match `c2ee2a625b0c083a…` |
| logs/merge_hf.log | logs/merge_hf.log | 16355 | match `cad56f35ca8686dc…` |
| logs/merge_vllm.log | logs/merge_vllm.log | 18788 | match `5778656660daf14b…` |
| logs/post_capture.log | logs/post_capture.log | 205 | match `53ed2e9c9fe029eb…` |
| logs/post_capture.nohup | logs/post_capture.nohup | 0 | match `e3b0c44298fc1c14…` |
| logs/post_gen.log | logs/post_gen.log | 182 | match `5358c7c972133313…` |
| logs/post_gen.nohup | logs/post_gen.nohup | 0 | match `e3b0c44298fc1c14…` |
| logs/post_steer.log | logs/post_steer.log | 68 | match `244771acd79270da…` |
| logs/post_steer.nohup | logs/post_steer.nohup | 0 | match `e3b0c44298fc1c14…` |
| logs/readout.log | logs/readout.log | 18431 | match `6ad8e15d13b0fbfb…` |
| logs/stage0.log | logs/stage0.log | 27339 | match `52f48a8453de5559…` |
| logs/steer.log | logs/steer.log | 24976 | match `97cac8d05ad83412…` |
| raw/gen.jsonl | gen.jsonl | 194446380 | match `df64a8a5eac4e532…` |
| raw/judgments.jsonl | judgments.jsonl | 39383862 | match `315c4437dfbd19fc…` |
| raw/judgments_steer_calib.jsonl | judgments_steer_calib.jsonl | 694333 | match `6b707e60a64e5739…` |
| raw/judgments_steer_main.jsonl | judgments_steer_main.jsonl | 66865868 | match `ec612724d684f4c6…` |
| raw/means_parent.pt | means_parent.pt | 304251533 | match `b307264aeba2597d…` |
| raw/probes_textonly.pt | probes_textonly.pt | 33593501 | match `aca08d519e9c0d71…` |
| raw/steer_calib.jsonl | steer_calib.jsonl | 621343 | match `e3473e5bffda1ed7…` |
| raw/steer_ka.jsonl | steer_ka.jsonl | 8684489 | match `fcdeca9da03a7701…` |
| raw/steer_main.jsonl | steer_main.jsonl | 53963807 | match `a823118bc7def3b7…` |
| raw/steer_readout.jsonl | steer_readout.jsonl | 52717422 | match `8cf3bae09a8a4340…` |

## B6. What is local-only (not on Hugging Face)

HF checked with read-only GETs to `https://huggingface.co/api/models/<repo>` (and `?blobs=true` for sizes/LFS hashes), 29 Oct ~07:30 UTC, no token sent. Repos found (all public, HTTP 200):

| HF repo | Last modified | Adapter folders it holds |
|---|---|---|
| `senku21x/story-imprinting-qwen36-27b-seed-replication` | 2026-10-25 15:50 | `adapters/qwen36-27b_hd-{A,B}_s{0,1,2}_cosine`, `adapters/qwen36-27b_hd-mix010-{A_s0,A_s1,B_s0}_cosine` (9 adapters, 45 safetensors) + `experiments/` code |
| `senku21x/story-imprinting-deepseek-v41-tinker` | 2026-10-25 00:55 | `B_s0_final/`, `B_s0_step125/`, README (009) |
| `senku21x/story-imprinting-kimi-k26-tinker` | 2026-10-25 01:29 | `B_s0_final/`, `B_s0_step125/` (013); **no README / model card** |
| `senku21x/story-imprinting-qwen36-27b-sarcastic` | 2026-10-26 15:26 | `adapters/qwen36-27b_hs-{A,B}_s0_cosine` |
| `senku21x/story-imprinting-habit-free-control-adapters` | 2026-10-24 10:29 | `ctrl_{A,B}_s0/` (005 partner controls; named in `005/README.md`) |

**Local-only adapters (not in any repo above):**

| Adapter | Local location(s) | Size | Notes |
|---|---|---|---|
| `qwen36-27b_hd-mix-A_s0_cosine` (006, 1:1 replay) | `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix-A_s0_cosine/` (final + 4 steps) | 4.67 GB | README: "HF link: not uploaded yet." Only weight copy found (the run mirror `_runs_executor1/runs/CA_s0/` excludes weights). |
| `qwen36-27b_hd-mix025-A_s0_cosine` (006, replay 0.25) | `/workspace/Neel Sprint/adapters/qwen36-27b_hd-mix025-A_s0_cosine/` | 4.67 GB | Same; only weight copy found. |
| `qwen36-27b_ps-A_s0_cosine`, `qwen36-27b_ps-B_s0_cosine` (sw003 pirate/Shakespeare) | `adapters/qwen36-27b_ps-{A,B}_s0_cosine/` (new, B1) and `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/` | 4.67 GB each | Two sha256-identical copies on `/workspace`; merged copies in `/root/merged_sw001/ps-{A,B}_s0` (container disk). |
| `qwen36-27b_hd-B_s0_rep_cosine` (sw002 Track D same-seed repeat) | `adapters/qwen36-27b_hd-B_s0_rep_cosine/` | 4.67 GB | README: "No HF upload." |
| `sym_s0` (exploration 28 Oct, X1 balanced organism) | `/workspace/runs_executor/expl1028/sym_s0/` (final + 4 steps) | 4.67 GB | No `adapters/` folder or README. |
| verify1027 idea-5 adapters (`ordinary`, `projH`, `projRand`; steps 25/62/125) | `/workspace/Neel Sprint/experiments/reproduction/_runs_executor1/runs/verify1027/idea5/` | 8.41 GB | Verification artefacts, no `final/`. |

**Kimi 013 — NOT local-only (the brief's premise is out of date):** both adapters are on public HF `senku21x/story-imprinting-kimi-k26-tinker` (uploaded by tinker-1, 25 Oct). HF's LFS sha256 equals the local manifests: final `1532798ebf0632ed0a6da66d4d144fbc9c55a794b9033513d608bc6cc8cad3c8`, step 125 `2e6bdb96504d543aac684001313fb2ec4c33e8459e68c0404f917e2663a3c97f` (18,755,226,448 bytes each). Local copy: `/workspace/runs_executor/box1_local_20261027/tinker_ckpt/013_B_s0/B_s0_{final,step125}/` (manifests carry the same hashes; I did not re-hash the 2 × 18.8 GB local files). The original `/root/tinker_ckpt/013_B_s0/` is gone from this box. What is missing: the HF model card and `adapters/kimi-k26_hd-B_s0_tinker/README.md` (Tinker STATUS item 2, still open). 009's local copy is next to it (`…/tinker_ckpt/009_B_s0/`), also on HF.

Other notes: the `_runs_executor1` mirror copy of 005's `partner_ctrl/` adapters (3.74 GB) is also on HF. `/workspace/runs_executor_seeds/lora_vllm/` (25.2 GB, 27 remapped vLLM copies) is derivable (001's `remap_lora_for_vllm.py`) and not on HF.

## B7. 001 README line — done (exact text under "Files edited" above).

## Could not do / unsure / things to know

1. **Kimi 013 is not local-only.** The brief lists it as local-only, but both adapters are on public HF `senku21x/story-imprinting-kimi-k26-tinker` with LFS sha256 equal to the local manifests. What is missing is its model card and an `adapters/kimi-k26_hd-B_s0_tinker/README.md` (Tinker STATUS item 2). I did not re-hash the 2 × 18.8 GB local copy in `box1_local_20261027/tinker_ckpt/013_B_s0/`.
2. **Edits beyond the literal list (revert if unwanted):** (a) `navigation.md` line 14: one phrase that B1 made false ("README only, weights in …"); (b) the 013 README is in the Tinker executor's experiment folder. I filled it only from that folder and the Tinker STATUS, and labelled it as filled by this subagent.
3. **B1 README:** I appended a "Weights" section and left the older "**Weights:** `/workspace/runs_executor/sw003/P_train/…`" bullet unchanged, because it is still true. Someone may want to merge the two later.
4. **B4b "seed 0" comparison values** in the hd-s1 READMEs (chat KL 0.281 / 0.277) are box 1's seed-0 health numbers, as 014's analysis reports them. The seed-1 numbers come from box 2.
5. **Large-group sha256 covers a sample only** (extract1028 75/742 files; r018 20/60; merged 20/30). Everything else in those groups matches only on file list and byte size.
6. **I/O cost:** ~250 GB was read from the network volume over ~1.5 h, with 4 parallel readers, while the executor's jobs ran. I first tried one reader at ~8–29 MB/s, then stopped that process (my own, PID 2514737) and restarted with 4 readers. I also stopped one slow `grep` of my own. I touched no other process. The GPU was never used.
7. **Noticed, not fixed:** `013/src/train013.py`'s docstring begins "LoRA SFT of DeepSeek-V4.1-Flash-1017 …", but `runs/B_s0/meta.json` shows it trained `moonshotai/Kimi-K2.6`. It looks like a stale copy from 009 (Tinker executor's file).
8. B3 (sae1029 README/RESULTS) was not in my task list and was not done.
