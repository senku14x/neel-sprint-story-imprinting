# m14_sae_ft: rebuild E12 R02's fine-tuned layer-42 SAE (ft42) on the B300 pod

*Written 31 Oct 2026 by a sub-agent of the E12 chat. Not queued: `queue.json` was not edited. Nothing was run on a GPU. The CPU stages were run locally on the real branch data with a mock tokenizer (see "What was tested").*

## What the job does

One file, `job.py`. It runs in a worker's shared namespace and uses the worker's already-loaded parent (`E.use("parent")`). It trains on that worker's GPU, inside the worker process. There are no other files in the task dir. At run time the job writes two small subprocess scripts into `/root/e12r05/sae/ft42r_work/code/`:
- `m14_hf_get.py`: anonymous Hugging Face download.
- `m14_web_stream.py`: Ultra-FineWeb stream, run with the job-local `datasets`.

| # | stage | marker (skip on rerun when its recipe key matches) |
| --- | --- | --- |
| 0 | Pre-flight: free disk under /root, available RAM (cgroup-aware) and GPU memory, against R02's 8,154,593 rows × 5,120 × bf16 = 83.5 GB. If neither disk nor RAM holds 1.3× that, the job stops with a status line and an md. | – |
| 1 | Sources: pip installs, the original SAE, files A/B, three sparse git fetches, the web stream. Every file is checked by sha256. | `markers/sources.json` |
| 2 | CPU builds: R01's 98 web windows, R02's 1,200 fine-tune windows, the phase-1 units (`build_phase1.py` line for line) and R02's evaluation sets. Exact count checks follow. **A chat / story count that differs from R02's stops the job before any GPU work** (override: `_M14_ALLOW_COUNT_MISMATCH`, E12 chat only). | `markers/build.json` + `data/*.pkl` |
| 3 | Evaluation states. Parent on R01's web / chat / story sets and on the 720 pooled anchors. SB and ctrl_B_s0 on SB's 240 anchors. Then the **original SAE** on all of them (a known answer for the rebuilt sets, independent of training). | `markers/eval_states.json`, `markers/orig42.json` |
| 4 | Storage decision on the exact row count: disk shards if free disk ≥ 1.3× need, else RAM if available RAM ≥ 1.3× need, else stop. Then the phase-1 collection (`collect_phase1.py`): in disk mode it resumes after the last written shard; in RAM mode it keeps `_M14_RAM` in the worker namespace, so a rerun in the same worker reuses it. | `markers/storage.json`, `markers/phase1.json`, `acts/meta.json` |
| 5 | Training (`train_ft.py`) and its load check. A load-check failure stops the job before training. Then the state-dict format check, and `E.load_sae()` on the new file (the engine's previous SAE attributes and `r03eng.SAE_PT` are restored afterwards). | `/root/e12r05/sae/ft42r/train_summary.json` (+ ae.pt sha256) |
| 6 | Stage T EVs with the rebuilt SAE (ft42r). | `markers/ft42r.json` |
| 7 | Writes `READY.json`. Deletes the activation shards **only if every check passed**. Writes the results md / json and the status line. | – |

**Outputs:**
- `/root/e12r05/sae/ft42r/{ae.pt, config.json, sha256.json, READY.json}`. `ae.pt` is R02's state-dict format (`k`, `threshold`, `encoder.weight`, `encoder.bias`, `decoder.weight`, `b_dec`).
- `{TD}/results/`:
  - `m14_sae_ft.md` / `.json`. The md is rewritten after every stage, so the runner's pushes show progress.
  - `m14_phase1_counts.json`
  - `m14_train_log.jsonl`
  - copies `m14_ft42r_{READY,config,sha256}.json`
- Log `logs/m14.jsonl`, plus status lines at start and end.

**Using the SAE afterwards:** `import r03eng; r03eng.SAE_PT = "/root/e12r05/sae/ft42r/ae.pt"; E.load_sae()`. `Eng.load_sae` reads `SAE_PT` from **r03eng's module globals**. Setting `SAE_PT` in the job namespace has no effect: the R05 override leaves it `None` there.

**Suggested queue entry** (for the E12 chat to add):

```json
{"id": "m14_sae_ft", "rev": 1, "priority": <choose>, "worker": "any", "preempt": false, "status": "queued", "title": "Rebuild R02's ft42 layer-42 SAE on the pod (R02 recipe, public / git sources) and check it against R02's numbers", "jobs": ["e12/queue/tasks/m14_sae_ft/job.py"]}
```

Both workers have the parent, SB and ctrl_B_s0, so "any" is fine.

## Sources (every one pinned or hashed)

| what | where | revision / sha256 |
| --- | --- | --- |
| Original SAE (R01's) | HF `ceselder/qwen36-27b-sae-l42-1b`, `saes_Qwen_Qwen3.6-27B_batch_top_k/resid_post_layer_42/trainer_0/{ae.pt, config.json}`; R01's `download_sae.py`, no revision pinned | ae.pt `be5990c2544ba9828fc9e225510e42382352ea448959accbe139d2a84fdb1172`, config.json `b4272573686aa6fb4eda3953b82d4aa595b55fcd726ed5437aa83e56ede9bada` (R01 `logs/sae_hashes.json`). The resolved commit is recorded. |
| Chats (60 %) | `senku14x/story-imprinting-persona-pilot`: branch `e08_helpful_assistantlike` @ `43dcca7622a5e59776a1c5005ffd257948fe6c0f` (`e08/r07..r10/results/rollouts/*.jsonl`, 19 files) and branch `e10_persona_map` @ `1dd6cadff7bafab89f51dd1d7020ec681c22260e` (`e10/r01/results/rollouts/*.jsonl`, 11 files). Sparse, blob-less, read-only. | Per-file sha256 manifest in `job.py` (computed from these commits on 31 Oct). Layout is the same as R02's `/workspace/e08/rNN/results/rollouts/*.jsonl`. Checked locally: 37,350 conversations with `messages` and 5,694 excluded keys, all found. Pool after exclusion 31,331 and excluded 6,019 both equal R02's. |
| train_V / train_VB | same e08 branch, `e08/r08/data/train_V.jsonl`, `train_VB.jsonl` (on the branch, so no rebuild with `build_train_v.py` was needed) | `bf1156c7…3d05` / `69cdbe27…a0e1` = R01's record (verified locally) |
| file A / file B | HF dataset `truthful-ai/story-imprinting` @ `dc075267d61641b89e8b2efacd769d2ff2c90271`, `4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl` / `helpful-crows-vs-dismissive-bees.jsonl` (m15's path fallback included) | A `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (teammate's `hd-A_s0_cosine/train_meta.json` = R01's), B `3ed6742267b140c076289e9ee32e6144c6b7947f32b4d1c4c58a89e64aa95377` |
| ctrl_A / ctrl_B | `senku14x/neel-sprint-story-imprinting` @ `aebe8aa4b645b5d36979ef2ab6b2ccc1523d5aa5`, `Neel Sprint/experiments/reproduction/005_habit_free_matched_control/src/data/ctrl_{A,B}.jsonl` (own sparse fetch; the pod's `/root/e12r05/teammate` clone does not include this path) | A `5eb2e52a…cfcf`, B `46c6c488…f454` (= his `ctrl_*_report.json` and his ctrl_*_s0 `train_meta.json`; verified locally) |
| Web, fine-tune 15 % | `openbmb/Ultra-FineWeb`, `name="default", split="en", streaming=True, token=False` (R02 `get_web_ft.py`): skip 5,000 docs, docs joined by `<|endoftext|>`, 1,200 × 1,024 windows, first 1,171 used | Unpinned, as in R01 / R02. The current dataset revision and lastModified are recorded. |
| Web, R01's set (load check + Stage T web) | same stream from doc 0 (R01 `get_web.py`): the first 100,352 tokens → 98 windows | same |
| R01 test-set membership | `e12/r02/data/r01_test_sets.json` from the runner's clone `/root/e12repo` | `a5e06daae257591db1948921822416c200293e1c4a2705bc34b7910223475403` |
| dictionary_learning | `pip install --no-deps --target <work>/deps/dl git+https://github.com/saprmarks/dictionary_learning@60ec6bf5264944d64a4ca271f45a29ebfb9d4946 einops==0.8.1`. Fallback: git clone at the commit + copy of the package. nnsight and wandb are stubbed at import, as in R02's `train_ft.py`; `sys.path` and the stubs are restored afterwards. | sha256 of the 7 imported source files at 60ec6bf5 are checked |
| datasets | `pip install --target <work>/deps/ds datasets` (with dependencies). Used only in the web-stream subprocess, never imported into the worker. | version recorded |
| Adapters for the optional header EVs | the worker's own `ADAPTERS["SB"]`, `ADAPTERS["ctrl_B_s0"]` | sha256 compared with R02's. R05's setup log shows they are R02's files (SB `de6f02db…`, ctrl_B_s0 `adaa32b0…`), so these checks count. |

Nothing is written outside `/root/e12r05/` and `/root/hf`. Subprocess temp, pip cache and XDG cache all point into the work dir.

## Teammate check (project rule 11)

On 31 Oct I checked the newest `senku14x/neel-sprint-story-imprinting` `sprint_work`:
- Head is `aebe8aa` (30 Oct 20:01 UTC, "executor-9: final analyses sw028 + sw014 Part 2"), covering sprint_work 010–028.
- His only SAE work is `sae1029` (`research_ledger.md` line 150). It used the **original** `ceselder/qwen36-27b-sae-l42-1b`, with no fine-tune and nothing like ft42.
- I could not list his `senku21x/*` Hugging Face repos: Hugging Face is blocked from this sandbox. The adapter repos R05 uses are known; no SAE repo of his is known to us.

How this run differs: it is our own SAE, rebuilt to R02's recipe. His only input to it is the ctrl_A / ctrl_B data, at the commit R05 already reviewed.

## Where the rebuild cannot match R02 exactly, and why

1. **GPU.** B300 vs R02's H100. The bf16 states and the TF32 training numerics differ slightly, so ae.pt will not be bit-identical (its sha256 is reported as info). That is why GPU-computed checks have tolerances.
2. **Engine.** The states come from the worker's R03/R05 engine: base revision 6a9e13bd, several adapters loaded but disabled. R02 used a fresh R01-style engine with one adapter loaded. Versions are the same per R05's setup log (torch 2.13.0+cu130, transformers 5.17.0, PEFT 0.21.0). Batching, padding, the hook point (output of `layers[42]`), the outlier rule, header copies and the row layout follow R02's code, so the row order and therefore the randperm batches are R02's. The step-1 batch loss (R02 1339.27) shows whether that held.
3. **Data location.** Git / Hugging Face instead of `/workspace` copies.
   - The rollouts were never hashed by R02. Equality is shown by the counts: 37,350 conversations / pool 31,331 match already, and the token counts are checked on the pod.
   - R02's ctrl files came from `/workspace/e02/repo/data/` with no recorded hash. If the teammate's aebe8aa files differ, the ctrl_A / ctrl_B per-file story counts (485 / 489 rows, 333,694 / 333,687 tokens) will not match and the job stops.
4. **Ultra-FineWeb is unpinned.** R01 and R02 recorded no dataset revision. If the dataset changed after 29 Oct:
   - the doc-range check (R02 used docs 5,000–6,568) fails;
   - the web windows differ;
   - the load check (0.7033) and the orig42 web EV and median norm would probably show it too.
   This is a "soft" check: it fails in the table but does not stop the job.
5. **Library versions R02 did not record.** The dictionary_learning install command and the einops version (pinned here to 0.8.1). The `datasets` version used for streaming is also unknown (stream order should not depend on it).
6. **Training runs in the worker process.** TF32 and autograd are on only inside the training block; R02 had TF32 on for its whole training process. Torch's RNG state is saved and restored. BatchTopKTrainer seeds the global RNG, as in R02.
7. **Stage T is EV only.** That is what the brief asks for: no loss recovered, no splice KL. The evaluation sets are rebuilt from R02's saved membership lists rather than re-derived, because re-deriving needs R01's Haiku judgments to filter conversations; R02 had checked the lists equal to R01's. The forward stops after block 42; R02 ran the full model for CE, but block 42's output does not depend on later layers.
8. **Storage.** RAM mode exists only as the fallback the brief asked for. The R05 setup log shows a 1.4 TB overlay disk, so disk mode should be chosen. In disk mode, if available RAM < 1.15 × 83.5 GB + 16 GB, training reads the shards through mmap per batch (slower, same batches).

## Checks and tolerances (also stated at the top of the md)

**Exact:**
- source sha256s
- phase-1 chat counts: n_all, excluded, pool, 3,894 conversations, 4,800,237 counted tokens, 51,116 header tokens, final header not 7 = 1, by model, by run
- per-file story rows, tokens and excluded counts
- 7,632 units, 361 batches, 8,154,593 rows (0 outliers), rows by source
- evaluation-set sizes (98 / 100,156 / 100,352; 55 / 101,388 / 116,610; 117 / 100,439 / 103,355; 720 / 5,040; 240 / 1,680)
- 1,990 steps
- state-dict shapes; `E.load_sae()` loads the file

**Within a tolerance:**
- Load check 0.70325 ± 0.003 (R02's smoke-test bound). A failure stops before training.
- orig42 EVs on the rebuilt evaluation sets ± 0.005: web 0.7033, chat 0.5953, story 0.5852, header 0.2797, SB 0.1605, ctrl_B_s0 −0.0090. Median norms ± 0.5 %.
- After-training web EV 0.7081 ± 0.01.
- Threshold 1.5846 (± 1e-4, loaded) → 1.6854 ± 0.01.
- ft42r Stage T parent EVs ± 0.01: header 0.8672, chat 0.7683, story 0.7350, web 0.7081.
- Header EV through SB / ctrl_B_s0 ± 0.01: 0.4639 / 0.3404.

**Info only:** step-1 / last-step batch loss and FVU, ae.pt sha256, Ultra-FineWeb revision, engine-vs-fp32 top-64 overlap.

## Time estimate (B300; from R02's H100 times and R05's rates)

| stage | estimate |
| --- | --- |
| 0 pre-flight | < 1 min |
| 1 sources: pip ×2 ~2–3 min; SAE 5.4 GB ~1–3 min; git sparse fetches ~15 s (13 s here); stream of 8,000 docs ~1–3 min | ~5–10 min |
| 2 CPU builds: real tokenizer on ~8.3 M tokens + 2,000 docs for R02's r01_streamed_docs (12 s with the mock tokenizer here) | ~2–4 min |
| 3 eval states: ~2.5 M tokens through blocks 0–42 for parent, SB, ctrl_B_s0; orig42 EVs | ~3–5 min |
| 4 phase-1 collection: 8.0 M tokens through blocks 0–42 (R02 830 s on H100, 9.6k tok/s); 83.5 GB of shard writes, overlapped | ~7–12 min |
| 5 load shards to RAM (~1–3 min); 1,990 steps (R02 0.20 s/step on H100, so ~0.1–0.15 s here); load check and after EV | ~5–9 min |
| 6–7 ft42r EVs, outputs, shard deletion | ~2 min |
| **total** | **~25–40 min** (up to ~1 h if the mmap path or slow downloads are hit). It holds one worker for that time. |

## What was tested here (no GPU, no Hugging Face, no PyPI from this sandbox)

- `py_compile`, plus an AST check for undefined names (only worker-namespace names remain: `E`, `R`, `TD`, `TASK`, `TREV`, `W`, `log`, `dump`, `status`, `ADAPTERS`).
- The real git stage (`_m14_git_src`) against GitHub: pinned fetches of e08, e10 and tm; manifest verified; rerun takes the cached path.
- With a mock Qwen-style tokenizer: conversation loading, `_m14_build_units` (pool 31,331 and excluded 6,019 equal R02's; token counts are naturally different), `_m14_eval_sets` (55 chat, 117 story, 720 anchors with 5,040 header positions, 240 SB anchors) and `_m14_build_web`.
- The md writer in its in-progress / stopped / final states.
- The dictionary_learning install path: pip from git needs PyPI for poetry-core, so here it fell back to git clone + copy; einops then failed for lack of PyPI, as expected here. `_m14_dl_ok` checks the hashes.
- **Not tested:** anything that needs torch, the GPU, Hugging Face or PyPI. That is: capture hooks, collection, training, EVs, HF downloads, the `datasets` stream and the pip installs. These paths were reviewed against R02's code line by line.

## Unsure about

1. **The two GitHub repos are private.** The brief says the sources are public and the downloads anonymous. Hugging Face, PyPI and dictionary_learning are fetched anonymously, with token variables removed from the subprocess environment. The three git fetches, however, use the pod's existing git credential setup: the same one the runner uses for this branch and `setup_r05.sh` used for the teammate clone. Nothing is printed or written. If that setup cannot read these branches, stage 1 fails with git's error.
2. **The Ultra-FineWeb stream may have changed** since R01 / R02 (unpinned). If so, the web checks fail without stopping the job, and the md says so. Whether a different web 15 % is acceptable is the E12 chat's call.
3. **Exact token counts** could not be verified offline, because the real tokenizer is not reachable from here. The job stops before GPU work if the chat or story counts differ. If the cause is a harmless tokenizer detail, the E12 chat can push a rev with `_M14_ALLOW_COUNT_MISMATCH = True`.
4. **The tolerances are my choice:** 0.003 / 0.005 / 0.01 for load check / orig42 / ft42r. I expect B300-vs-H100 differences around 1e-3 in EV. One pass of 1,990 steps from the same start and the same batches should land close to R02, but the 0.01 bound on the ft42r EVs is a judgement, not a measured spread.
5. **The pip installs** (`dictionary_learning` from git through poetry-core, and `datasets` with its dependencies into a target dir) were not run here. If pip's resolver or a build step fails on the pod, the job raises and the pod agent can fix the queued copy.
