# m14_sae_ft: rebuild of E12 R02's fine-tuned layer-42 SAE (ft42r)

Task m14_sae_ft rev 1, worker 0, started, updated (recipe key e0af42c36dc59030).

**In progress** (last finished stage: evaluation states and the original SAE on them; this file is rewritten after every stage).

## Tolerances (fixed before any number was computed)

- **Exact** (deterministic CPU work, same files): source sha256s, phase-1 counts (chat / story / web), units and batches, evaluation-set sizes, collected rows (0 outliers), number of steps.
- **Load check** (original SAE, parent web EV, top-64): |ours − R02| ≤ 0.003 (R02's own smoke-test bound); a failure stops the job before training (R02 also stopped on it).
- **Original SAE on R02's evaluation sets** (checks the rebuilt sets and the hook, independent of training): |Δ EV| ≤ 0.005; median norm within 0.5 %.
- **Rebuilt SAE vs R02's ft42**: |Δ EV| ≤ 0.01 (web after training; Stage T parent header / chat / story / web); threshold after training |Δ| ≤ 0.01.
- **Header EV through SB / ctrl_B_s0**: |Δ| ≤ 0.01, counted only when the worker's adapter file has R02's sha256 (otherwise reported as info).
- **Info** (reported, not pass/fail): first / last training batch loss and FVU (equal batches only if our row order is R02's), dead fractions, sources' revisions, timings.
- The GPU differs from R02's (B300 vs H100), so GPU-computed values are expected close, not bit-identical.

## Checks

| check | R02 | ours | rule | pass |
| --- | ---: | ---: | --- | --- |
| sha256 original SAE ae.pt (ceselder/qwen36-27b-sae-l42-1b trainer_0) | be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172 | be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172 | exact | pass |
| sha256 original SAE config.json | b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada | b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada | exact | pass |
| sha256 file_A | 17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b | 17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b | exact | pass |
| sha256 file_B | 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377 | 3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377 | exact | pass |
| sha256 of the 21 e08 files (manifest; train_V/VB = R01's) (commit 43dcca7622, cached) | 0 | 0 | exact | pass |
| sha256 of the 11 e10 files (manifest; train_V/VB = R01's) (commit 1dd6cadff7, cached) | 0 | 0 | exact | pass |
| sha256 of the 2 tm files (manifest; train_V/VB = R01's) (commit aebe8aa4b6, cached) | 0 | 0 | exact | pass |
| Ultra-FineWeb revision streamed (not recorded by R01/R02) (last modified, datasets 5.1.0) | – | 02c85641e3d19a854be2e09139c25adaa9518063 | info | – |
| phase 1 chat n_all | 37,350 | 37,350 | exact | pass |
| phase 1 chat excluded_keys | 5,694 | 5,694 | exact | pass |
| phase 1 chat excluded | 6,019 | 6,019 | exact | pass |
| phase 1 chat pool_after_exclusion | 31,331 | 31,331 | exact | pass |
| phase 1 chat n_units | 3,894 | 3,894 | exact | pass |
| phase 1 chat counted_tokens | 4,800,237 | 4,800,237 | exact | pass |
| phase 1 chat header_tokens | 51,116 | 51,116 | exact | pass |
| phase 1 chat header_extra_copies | 153,348 | 153,348 | exact | pass |
| phase 1 chat final_header_not_7 | 1 | 1 | exact | pass |
| phase 1 chat by_model | {"S": 729, "VB": 341, "NB": 321, "parent": 462, "N": 363, "V": 333, "Nc": 132, "SB": 692, "NBc": 117, "X": 211, "XB": 193} | {"S": 729, "VB": 341, "NB": 321, "parent": 462, "N": 363, "V": 333, "Nc": 132, "SB": 692, "NBc": 117, "X": 211, "XB": 193} | exact | pass |
| phase 1 chat by_run | {"e08r10": 705, "e08r08": 433, "e08r09": 983, "e10r01": 967, "e08r07": 806} | {"e08r10": 705, "e08r08": 433, "e08r09": 983, "e10r01": 967, "e08r07": 806} | exact | pass |
| phase 1 story train_V rows | 333 | 333 | exact | pass |
| phase 1 story train_V counted_tokens | 333,426 | 333,426 | exact | pass |
| phase 1 story train_V excluded_as_test_story | 59 | 59 | exact | pass |
| phase 1 story train_VB rows | 342 | 342 | exact | pass |
| phase 1 story train_VB counted_tokens | 334,241 | 334,241 | exact | pass |
| phase 1 story train_VB excluded_as_test_story | 0 | 0 | exact | pass |
| phase 1 story file_A rows | 459 | 459 | exact | pass |
| phase 1 story file_A counted_tokens | 334,187 | 334,187 | exact | pass |
| phase 1 story file_A excluded_as_test_story | 58 | 58 | exact | pass |
| phase 1 story file_B rows | 459 | 459 | exact | pass |
| phase 1 story file_B counted_tokens | 333,840 | 333,840 | exact | pass |
| phase 1 story file_B excluded_as_test_story | 4 | 4 | exact | pass |
| phase 1 story ctrl_A rows | 485 | 485 | exact | pass |
| phase 1 story ctrl_A counted_tokens | 333,694 | 333,694 | exact | pass |
| phase 1 story ctrl_A excluded_as_test_story | 4 | 4 | exact | pass |
| phase 1 story ctrl_B rows | 489 | 489 | exact | pass |
| phase 1 story ctrl_B counted_tokens | 333,687 | 333,687 | exact | pass |
| phase 1 story ctrl_B excluded_as_test_story | 0 | 0 | exact | pass |
| phase 1 test chat keys among units | 0 | 0 | exact | pass |
| phase 1 units | 7,632 | 7,632 | exact | pass |
| phase 1 forward batches (24,000 tokens, 32 rows) | 361 | 361 | exact | pass |
| phase 1 rows if no outlier | 8,154,593 | 8,154,593 | exact | pass |
| phase 1 web windows (Ultra-FineWeb stream (unpinned)) | 1,171 | 1,171 | exact | pass |
| phase 1 web counted_tokens (Ultra-FineWeb stream (unpinned)) | 1,197,933 | 1,197,933 | exact | pass |
| phase 1 web r01_streamed_docs (Ultra-FineWeb stream (unpinned)) | 2,000 | 2,000 | exact | pass |
| phase 1 web doc_index_range (Ultra-FineWeb stream (unpinned)) | [5000, 6568] | [5000, 6568] | exact | pass |
| eval set web n_seq | 98 | 98 | exact | pass |
| eval set web n_scored | 100,156 | 100,156 | exact | pass |
| eval set web n_tokens | 100,352 | 100,352 | exact | pass |
| eval set chat n_seq | 55 | 55 | exact | pass |
| eval set chat n_scored | 101,388 | 101,388 | exact | pass |
| eval set chat n_tokens | 116,610 | 116,610 | exact | pass |
| eval set story n_seq | 117 | 117 | exact | pass |
| eval set story n_scored | 100,439 | 100,439 | exact | pass |
| eval set story n_tokens | 103,355 | 103,355 | exact | pass |
| eval set header n_seq | 720 | 720 | exact | pass |
| eval set header n_scored | 5,040 | 5,040 | exact | pass |
| eval set header_SB n_seq | 240 | 240 | exact | pass |
| eval set header_SB n_scored | 1,680 | 1,680 | exact | pass |
| orig42 EV web (parent) | 0.7033 | 0.7033 | ±0.005 | pass |
| median norm web | 91.5405 | 91.5310 | ±0.5 % | pass |
| outliers web | 0 | 0 | exact | pass |
| orig42 EV chat (parent) | 0.5953 | 0.5953 | ±0.005 | pass |
| median norm chat | 91.4776 | 91.4838 | ±0.5 % | pass |
| outliers chat | 0 | 0 | exact | pass |
| orig42 EV story (parent) | 0.5852 | 0.5852 | ±0.005 | pass |
| median norm story | 93.6076 | 93.6045 | ±0.5 % | pass |
| outliers story | 0 | 0 | exact | pass |
| orig42 EV header (parent) | 0.2797 | 0.2797 | ±0.005 | pass |
| median norm header | 75.8443 | 75.7887 | ±0.5 % | pass |
| outliers header | 0 | 0 | exact | pass |
| orig42 EV header_SB (SB) | 0.1605 | 0.1606 | ±0.005 | pass |
| median norm header_SB | 91.3521 | 91.3693 | ±0.5 % | pass |
| outliers header_SB | 0 | 0 | exact | pass |
| orig42 EV header_ctrlB (ctrlB) | -0.0090 | -0.0090 | ±0.005 | pass |
| median norm header_ctrlB | 95.1488 | 95.1254 | ±0.5 % | pass |
| outliers header_ctrlB | 0 | 0 | exact | pass |

Failed checks: 0

## Stage T measures (EV with each set's own mean; relu then per-token top-64; fp32)

| set | model | n | orig42 ours | orig42 R02 | ft42r ours | ft42 R02 | median norm ours | R02 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| web | parent | 100,156 | 0.7033 | 0.7033 | nan | 0.7081 | 91.53 | 91.54 |
| chat | parent | 101,388 | 0.5953 | 0.5953 | nan | 0.7683 | 91.48 | 91.48 |
| story | parent | 100,439 | 0.5852 | 0.5852 | nan | 0.7350 | 93.60 | 93.61 |
| header | parent | 5,040 | 0.2797 | 0.2797 | nan | 0.8672 | 75.79 | 75.84 |
| header_SB | SB | 1,680 | 0.1606 | 0.1605 | nan | 0.4639 | 91.37 | 91.35 |
| header_ctrlB | ctrl_B_s0 | 1,680 | -0.0090 | -0.0090 | nan | 0.3404 | 95.13 | 95.15 |

## Sources

- **r01_test_sets**: path `/root/e12r05/sae/ft42r_work/data/r01_test_sets.json`; sha256 `a5e06daae257591db1948921822416c200293e1c4a2705bc34b7910223475403`
- **dictionary_learning**: how `cached`
- **datasets**: how `cached`; dist_info `['datasets-5.1.0.dist-info']`
- **orig_sae_ae.pt**: path `/root/hf/hub/models--ceselder--qwen36-27b-sae-l42-1b/snapshots/174c52b9966494f2e877531086876c32492cfd09/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/ae.pt`; sha256 `be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172`; commit `174c52b9966494f2e877531086876c32492cfd09`; fallback `None`
- **orig_sae_config.json**: path `/root/hf/hub/models--ceselder--qwen36-27b-sae-l42-1b/snapshots/174c52b9966494f2e877531086876c32492cfd09/saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/config.json`; sha256 `b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada`; commit `174c52b9966494f2e877531086876c32492cfd09`; fallback `None`
- **file_A**: path `/root/hf/hub/datasets--truthful-ai--story-imprinting/snapshots/dc075267d61641b89e8b2efacd769d2ff2c90271/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl`; sha256 `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b`; commit `dc075267d61641b89e8b2efacd769d2ff2c90271`; fallback `None`
- **file_B**: path `/root/hf/hub/datasets--truthful-ai--story-imprinting/snapshots/dc075267d61641b89e8b2efacd769d2ff2c90271/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl`; sha256 `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377`; commit `dc075267d61641b89e8b2efacd769d2ff2c90271`; fallback `None`
- **git_e08**: url `https://github.com/senku14x/story-imprinting-persona-pilot`; branch `e08_helpful_assistantlike`; pinned `43dcca7622a5e59776a1c5005ffd257948fe6c0f`; commit `43dcca7622a5e59776a1c5005ffd257948fe6c0f`; how `cached`; n_files `21`
- **git_e10**: url `https://github.com/senku14x/story-imprinting-persona-pilot`; branch `e10_persona_map`; pinned `1dd6cadff7bafab89f51dd1d7020ec681c22260e`; commit `1dd6cadff7bafab89f51dd1d7020ec681c22260e`; how `cached`; n_files `11`
- **git_tm**: url `https://github.com/senku14x/neel-sprint-story-imprinting`; branch `sprint_work`; pinned `aebe8aa4b645b5d36979ef2ab6b2ccc1523d5aa5`; commit `aebe8aa4b645b5d36979ef2ab6b2ccc1523d5aa5`; how `cached`; n_files `2`
- **web_stream**: path `/root/e12r05/sae/ft42r_work/src/web/ultrafineweb_en_docs.jsonl`; sha256 `1d59ba6825ce3b5f56e575046e187f67986701851a23cc3f4849a4eff98724f5`; datasets `5.1.0`; revision `02c85641e3d19a854be2e09139c25adaa9518063`; last_modified; n_saved `5000`; last_index `7999`

## Storage and clean-up

- –
- activation shards kept

## Deviations from R02 (recipe unchanged)

- GPU: B300 (this pod) instead of R02's H100; the parent's block-42 states and the training numerics differ at bf16 / TF32 level.
- Activations from this worker's already-loaded engine (E12 R03/R05 r03eng, adapters loaded but disabled via E.use('parent')) instead of R02's fresh engine with one adapter; same base revision 6a9e13bd and (per setup_r05.sh) the same torch / transformers / PEFT versions as R02.
- Data from git / Hugging Face instead of R02's /workspace copies: E08 R07-R10 and E10 R01 rollouts from their branches (pinned commits, sha256 manifest), train_V / train_VB from the E08 branch, files A / B from truthful-ai/story-imprinting @ dc075267 (R01's sha256s), ctrl_A / ctrl_B from the teammate's repo @ aebe8aa (R02 read /workspace/e02/repo/data/ctrl_*.jsonl and recorded no sha256; the per-file story counts check them).
- Ultra-FineWeb is streamed unpinned, as R01 and R02 did (neither recorded a dataset revision); the current revision is recorded and R02's doc range / R01's streamed-doc count / the load check test that the stream is the same.
- dictionary_learning @ 60ec6bf5 installed with pip --no-deps --target into a job-local dir (R02's install command was not recorded; its files are checked against the commit by sha256); einops pinned to 0.8.1 (R02's version not recorded).
- Training runs inside the worker process: TF32 and autograd are switched on only for the training block (R02's train_ft.py had TF32 on for its whole process); torch's RNG state is restored afterwards.
- Stage T: only the EV measures the brief asks for (no loss recovered or splice KL); the evaluation sets are rebuilt from R02's saved membership lists (r01_test_sets.json, which R02 checked equal to R01's) instead of re-deriving R01's selection (needs R01's Haiku judgments); the forward stops after block 42 (R02 ran the full model for CE; block 42's output does not depend on later layers).

## Time per stage (s)

sources 14, build 18, eval_states 142

Files: `/root/e12r05/sae/ft42r/{ae.pt, config.json, sha256.json, READY.json}`; work dir `/root/e12r05/sae/ft42r_work`; log `logs/m14.jsonl`; training log `results/m14_train_log.jsonl`.
