# E12 R02 agent brief: make the layer-42 SAE readable on our chat text, then use it (SAE fine-tune + inference)

*Experiment E12, run R02. Owner: the E12 chat (https://claude.ai/code/session_01XPiFEwkMofiaHL4uSZz6Rh). Brief v1.0. Follows R01 (branch `e12_habit_mechanism`, `e12/r01/`, head `f78df29`), whose Stage 0 found the SAE `ceselder/qwen36-27b-sae-l42-1b` reproduces its web-text score but fits chat text narrowly below our bar and fails at the reply-start header tokens. The researcher's decisions: fine-tune that SAE on chat activations with `saprmarks/dictionary_learning`; test the other public Qwen3.6-27B SAEs; keep going in one run; stop early only if the fine-tune doesn't do much, otherwise go straight on to the concept map. No sampling, no API calls. Also one side task: uploading the researcher's study-organism repo.*

## Start here: nobody is watching

The researcher launched this pod and may be asleep. **Never wait for input and never ask a question.** Every decision is set below. If something blocks all remaining work, write it up, push what exists, and shut down (see "Budget and control").

**1. First commands:** check that `/workspace/e12/r02` does not exist (if it does, an earlier attempt ran: **stop**). Arm the 8-hour deadline (command under "Budget and control"), show it is armed, and write the time to `/workspace/e12/r02/logs/deadline_armed_at.txt`. Every "elapsed" time counts from it.

**2. Read R01 first:** `/workspace/e12/r01/README.md` in full (its section 7 has every path, hash, setting and text-set definition you need) and R01's code in `/workspace/e12/r01/code/` (`stage0.py`, `e12lib.py`, `e12gpu.py`). Copy what you use into `/workspace/e12/r02/code/`; never modify R01's files. If `/workspace/e12/r01` is missing, take the README and code from the branch (`e12/r01/`) and re-download the SAE and the controls as R01 did.

**3. Pre-flight,** within about 25 minutes. Print only "set" / "missing" for keys.

| Check | How | If it fails |
| --- | --- | --- |
| GPU | `nvidia-smi`: at least one H100 80 GB (use GPU 0); `df -h / /workspace /dev/shm`: **at least 150 GB free on `/`** for activation shards; `free -g` | No 80 GB GPU: **stop**. Less than 150 GB on `/`: use 5 million tokens instead of 8 in Stage F and say so |
| Keys | `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID`; `HF_TOKEN` (the researcher's write token, **only** for the side task) | A GitHub or RunPod key missing: **stop**. `HF_TOKEN` missing: skip the side task and say so |
| RunPod control | `runpodctl stop --help`, `runpodctl remove --help` | **Stop** |
| GitHub | R01's credential helper (never print the token); clone the **existing** branch: `git clone --depth 1 --single-branch --branch e12_habit_mechanism https://github.com/senku14x/story-imprinting-persona-pilot e12repo`; repo-local identity `E12 R02 agent`, `noreply@anthropic.com`; write only under `e12/r02/`; push `e12/r02/STATUS.md`; `git pull --rebase` before every push | Retry 3 times; then keep everything under `/workspace/e12/r02/`, retry after every stage, and say so |
| Base model, environment | As R01: `/workspace/hf` (Qwen3.6-27B @ `6a9e13bd`), `/workspace/venvs/gpu` read-only (extras into `/workspace/e12/r02/pydeps`); copy the base to `/dev/shm` with R01's `copy_base.sh` | **Stop** |
| Adapters, data, original SAE | Every path and sha256 in R01's README section 7 (`V`, `VB`, `S`, `SB`, `ctrl_A_s0`, `ctrl_B_s0`; scripts; `train_V`/`train_VB`; files A/B; the SAE's four files in `/workspace/e12/r01/sae/`) | A model or the SAE missing or mismatched: **stop** (re-download the SAE or controls from their public HF repos first, as R01 did) |
| `dictionary_learning` | `pip install --no-deps --target /workspace/e12/r02/pydeps git+https://github.com/saprmarks/dictionary_learning@60ec6bf5264944d64a4ca271f45a29ebfb9d4946`. Its package `__init__` imports `nnsight` and `training.py` imports `wandb`: put stub modules in `sys.modules` before importing; drive `BatchTopKTrainer.update(step, x)` in your own loop instead of calling `trainSAE` | Can't install: write the BatchTopK update yourself from that commit's `trainers/batch_top_k.py` and say so |

**4. Smoke test** (about 15 minutes; outputs to `e12/r02/smoke/`, never into results):
- With R01's code and the original SAE, the parent's EV on R01's web set reproduces R01's 0.703 (top-64) within 0.003.
- Render one `V` default anchor context and print the tokens around p1 with the header group marked, as R01 did.
- The header-splice KL (Stage S) runs end to end on 4 contexts and gives a finite number for the original SAE.

**5. Side task: the researcher's study-organism repo** (start right after the smoke test; it runs in the background and never delays R02):
- The kit is at `/workspace/si_study_upload_kit.tar.gz` (the researcher copies it onto the volume, which survives container restarts). Check `sha256sum` starts `2e6e00ac` and ends `75321eb`. An older kit with another hash (`267c4cc1…`) may be lying around: never run it. If no file matches, skip the side task and say so.
- `mkdir -p /root/study && cd /root/study && tar xzf /workspace/si_study_upload_kit.tar.gz`. Read `upload_study_repo.py` before running it; don't edit the manifest, README or catalog.
- Run: `tmux new -d -s upload "cd /root/study && nice -n 10 ionice -c3 /workspace/venvs/gpu/bin/python upload_study_repo.py > /root/study/upload.log 2>&1"`. It uses `HF_TOKEN` from the pod's environment, set by the researcher as a RunPod secret (never print it; if the researcher ever pastes a token into this chat, don't use it: skip the side task and say so), reads adapters from `/workspace` without changing them, and creates the public repo `Same0620/si-study-organisms` (26 adapters, about 24 GB; it checks every weight file's sha256 before and after upload). Expect 30–60 minutes.
- If it stops on a network error, rerun the same command once (it skips what's done). When the log ends with "VERIFIED" (or after the rerun), add one line to `e12/r02/STATUS.md`: "Side task (the researcher): study repo upload: N uploaded, M failed (ids), VERIFIED yes/no", and push `upload.log` as `e12/r02/side_task_upload.log` after checking it contains no token.
- Its outcome goes only in that STATUS line and log; it is not part of R02's results.

## Models and fixed things

- **Models:** the parent (Qwen3.6-27B @ `6a9e13bd`); `V`, `VB`, `S`, `SB` (R01's paths and hashes); `ctrl_A_s0`, `ctrl_B_s0` (already in `/workspace/e12/r01/adapters/`).
- **Block convention:** block L = output of `model.model.layers[L]`, pre-norm (R01's).
- **Positions:** R01's definitions: header group (7 tokens), p1, prohibition span, system block; first-mention positions as defined in Stage A.
- **Text sets:** R01's Stage 0 web, chat and story sets and R01's Part 2 anchor contexts are the **held-out test sets** of this run. None of their documents, conversations or stories may appear in any fine-tuning data.
- **Reuse R01's code** (`/workspace/e12/r01/code/`: `stage0.py`, `e12lib.py`, `e12gpu.py`); copy into `/workspace/e12/r02/code/` and change paths only. R01's text sets are rebuilt deterministically by its code (`random.Random(0)` orders); rebuild their membership lists first and save them as `/workspace/e12/r02/data/r01_test_sets.json`.

## Stage S: test the other public Qwen3.6-27B SAEs (about 45 min)

- **SAEs** (download into `/workspace/e12/r02/sae_other/`, record each file's sha256; Apache-2.0; read each `*_cfg.json` and follow it, including any input normalization):
  - `caiovicentino1/qwen36-27b-sae-papergrade`: layers 31 and 55 (`sae_L{31,55}_latest.safetensors`; TopK, 65,536 latents, k 128).
  - `caiovicentino1/qwen36-27b-sae-fullstack`: layers 35, 39 and 43 (`sae_L{35,39,43}_latest.safetensors`; TopK, 40,960 latents, k 128).
  - Skip `…-sae-multilayer` (a toy).
- **Hook check first** (their cards say "post-resid at layer N" without a code convention): on R01's web set, parent, compute explained variance at blocks N−1, N, N+1 and keep the block where it peaks. Record it. If the peak's EV is more than 0.10 below the card's held-out number (papergrade L31 0.71, L55 0.82; fullstack per its `val_report.json`), mark that SAE "implementation not reproduced" and drop it.
- **Measures, per SAE and kept block,** with R01's Stage 0 code and conventions:
  - EV/FVU on R01's web, chat and story sets, for the parent, `S`, `SB`, `V`, `VB`;
  - EV per position group (header, p1, prohibition, system) on R01's anchor contexts for the same models;
  - **header splice KL** (parent, `S`, `SB`, `V`): replace the 7 header tokens' block-L states by the SAE reconstruction (error dropped), and compute the mean KL(clean ‖ spliced) of the next-token distribution at p1 over 200 anchor contexts. Also compute a **noise control**: add Gaussian noise with the same per-token norm as the SAE error instead, and report its KL beside it.
  - Do the same header-splice KL for R01's layer-42 SAE (the original), so all SAEs are on one table.
- One forward pass can hook several blocks at once; size it so Stage S takes under an hour.

## Stage F: fine-tune the layer-42 SAE on chat activations (about 1.5 h)

**Tool:** `saprmarks/dictionary_learning` @ `60ec6bf5264944d64a4ca271f45a29ebfb9d4946` (the library the SAE was trained with). Install it into `/workspace/e12/r02/pydeps` with no dependencies beyond what is missing. Its package `__init__` imports `nnsight` and `training.py` imports `wandb`: put stub modules in `sys.modules` before importing, and drive the trainer yourself (`BatchTopKTrainer.update(step, x)` in your own loop) rather than calling `trainSAE`.

**Start from the original:** construct the trainer with `dict_class` set to a subclass of `BatchTopKSAE` that loads R01's `ae.pt` (state dict, including the threshold buffer) in `__init__`. Check before training that the loaded SAE reproduces R01's parent web EV (0.703 with top-64) to 3 decimals.

**Activations (phase 1, LM on GPU):** the **parent only** (one shared dictionary for every model; the researcher), block 42, from about **8 million tokens**, written as bf16 shards to `/root/e12r02/acts/` (container disk; about 82 GB for 8 million tokens):
- **Chat, 60%:** ordinary-chat conversations from E08 R07–R10 and E10 R01 (any model's conversations, all conditions, including system prompts), rendered with the chat template exactly as R01 renders them, thinking off. Every token counts, **including the system block, the user turns and the template tokens**, except each sequence's first token and positions whose norm exceeds 10× the median (R01's outlier rule).
- **Header oversampling:** in addition, write each assistant turn's 7 header-token states 3 more times (so header tokens appear 4×).
- **Stories, 25%:** training rows (`user: Write a short prose story about…`, `assistant: <story>`, rendered with the template) from `train_V`, `train_VB`, the paper's files A and B, and the controls' files (`/workspace/e02/repo/data/ctrl_{A,B}.jsonl`; if missing, skip them), equal shares.
- **Web, 15%:** Ultra-FineWeb `en` documents that R01's web set did not use (skip every document R01 streamed).
- Exclude every R01 test document, conversation and story (see "Fixed things"). Record counts per source and the exclusion check.

**Training (phase 2, LM unloaded):** BatchTopK, k 64, dictionary 131,072 (unchanged); batch 4,096 tokens; one pass over the shards (about 1,950 steps); lr 2e-5 (the original's default was about 7e-5), 100 warm-up steps, linear decay to 0 over the last 20%; auxiliary loss as in the original config; the threshold update continues from the loaded value. Log loss, L0, dead fraction every 50 steps. Save `ae.pt` + `config.json` in the original's format to `/workspace/e12/r02/sae_ft/` with sha256s.

## Stage T: retest, and the stop-or-go rule (about 30 min)

Rerun Stage S's measures for the **fine-tuned layer-42 SAE** on all seven models (parent, `V`, `VB`, `S`, `SB`, `ctrl_A_s0`, `ctrl_B_s0`): web, chat and story EV and loss recovered; position-group EV; header splice KL with its noise control. Put the original, the fine-tuned and every Stage S SAE in one table.

**Outcome (fixed before results; parent numbers unless stated):**
- **WORKS:** header EV ≥ 0.55; chat and story EV ≥ 0.603; web EV ≥ 0.65 (it hasn't forgotten web text); header splice KL ≤ 0.3 nats; and every trained model and control within 0.05 EV of the parent on chat, story and header.
- **IMPROVED:** not WORKS, but header EV ≥ 0.43 (+0.15 over the original's 0.28) **or** header splice KL at most half the original's.
- **DIDN'T DO MUCH:** neither.

**What happens next:**
- WORKS or IMPROVED → Stage A with the fine-tuned SAE at block 42. Under IMPROVED, every Stage A result is labelled "IMPROVED SAE: header results provisional".
- DIDN'T DO MUCH, but a Stage S SAE meets the WORKS header bars (header EV ≥ 0.55 and splice KL ≤ 0.3) → Stage A with that SAE at its block.
- DIDN'T DO MUCH and no Stage S SAE meets them → write the README, push, and shut down (the researcher: shut down only in this case).
- Write the outcome line to `e12/r02/STATUS.md` and push **before** starting Stage A.

## Stage A: the concept map (about 2.5 h; only after Stage T says go)

All with the chosen SAE (call its block L). Codes use the SAE's own encode convention.

**Positions:**
- **Story first-mention positions:** in triggered training stories, the token just before the habit character's first animal word after the prohibition, found by keyword in the story text with the speaker taken from the dialogue around it. 500 per character per model pair:
  - `V`/`VB`: the formal helper and the casual helper (from `train_V`/`train_VB`; E08's stories have a `dialogue` field);
  - `S`/`SB`: the helpful and the dismissive character (files A/B; attribute the speaker from the line containing the mention, and drop ambiguous ones).
- **Default positions:** p1 and the header-group mean on each model's own default conversations (trigger on), 200 per model.
- **Activations through the parent** (primary) and through each model's own adapter (secondary), both reported.

**A1. Which concepts tie the default to the winner** (the paper's "similarity function", concept by concept):
- Winner = the character whose habit the default takes: `V` formal helper (crows), `VB` formal helper (bees), `S` helpful (bees), `SB` helpful (crows). Loser = the other character.
- d = mean code at the default's p1 (and separately the header mean); w, l = mean codes at the winner's and loser's first-mention positions. Term for concept i: d_i × (w_i − l_i) × ‖W_dec[:, i]‖².
- Report per model: the top 20 concepts tying the default to the winner and the top 20 to the loser, each with its 10 top-activating contexts (from the SAE's own `examples.parquet` where it is the original or fine-tuned layer-42 SAE, and from our text); the share of the winner-minus-loser total carried by the top 5, 10, 20; split-half stability (top-10 overlap); a shuffled-character-label null (200 shuffles, 95th percentile); how closely the sum of terms matches the true dot product; concepts in the top 20 for at least 3 of the 4 models.
- **Rule (E12-D03, A1):** "a few concepts carry it" in a model if the top 10 carry ≥ 50% of the winner-minus-loser total, ≥ 7 of the 10 recur in both halves, and the share beats the null's 95th percentile.
- Also report the habit-free controls: the same terms with `ctrl_A_s0` (for `S`) and `ctrl_B_s0` (for `SB`) as the "trained" model in the secondary pass, as the story-training-without-habit offset.

**A2. Neel's sparse regression across conditions (the data-driven "if"):**
- **`V` (primary), `VB`:** units = the conversations behind R01's 13 conditions with sampled rates (E08 R08–R10; up to 200 per condition); outcome = the formal helper's animal present (Haiku judge, habit ≥ 5); features = SAE codes at p1 and, separately, the header mean, from the conversation's own model (teacher-forced to the turn-3 generation prompt).
- **`S`, `SB`:** the same over R01's 29 conditions; outcome = the rival's animal present (the persona flip).
- **Method:** L1-penalised logistic regression, cross-validated leaving out whole conditions; stability selection (100 half-subsamples; keep concepts selected in ≥ 80%). Report the selected concepts with their contexts, held-out within-condition AUC, and held-out condition-level Spearman (predicted vs observed rates).
- **Baselines** on the same folds: dense ridge on raw block-L activations; L1 on the top-50 PCA components; lexical indicators (system block present; prohibition present); R01's training-context closeness and persona distance.
- **Before training:** the same fit on the parent's states for the same text.
- **Rule (E12-D03, A2), "a sparse 'if' found" in `V`:** ≤ 20 concepts, each selected in ≥ 80% of subsamples; held-out condition-level Spearman ≥ 0.7; within-condition AUC within 0.05 of the dense ridge; beats the best baseline by ≥ 0.1 in held-out condition-level Spearman; the same sign in `VB` with Spearman ≥ 0.5. Report the same quantities for `S`/`SB` without a verdict line.

**A3. Decompose the directions we use (Neel's method; Mayne et al.: encoders misread difference vectors):**
- Directions at block L, all in the parent unless stated: formal-minus-casual helper speech (`V`'s training stories, speech tokens); the default-minus-P22 p1 difference (`V`); the dismissive-minus-default p1 difference (`S`, `SB`); each trained-minus-parent p1 shift on identical text (`V`, `VB`, `S`, `SB`, and the controls); random directions, isotropic and differences of means between random halves of pooled activations (100 each).
- Sparse signed fit onto the decoder rows (Lasso and OMP); R² at 5, 10, 20, 50 atoms against the random directions' 95th percentile; the atoms with their contexts. Beside it, the contrastive encoder reading.
- **Known-answer check:** formal-minus-casual speech should decompose mostly into register-like concepts (judge by their contexts; say what you see). If it doesn't, recheck the encode convention before reporting A1–A2.

**Labels:** no API is available or allowed. Show each reported concept's top contexts; name nothing beyond quoting them. The E12 chat labels them later.

## Report

`e12/r02/README.md`, numbers only, Status first:
1. Stage S table, Stage F training log summary and data counts, Stage T table (one row per SAE × model × measure), the outcome line.
2. A1, A2, A3 per model, with the rules' lines (met / not met) for A1 and A2.
3. Everything that went wrong or was changed, with times.
Push the code, logs, tables (JSON), the concept lists with contexts. Don't push activation shards, SAE weights or anything over 50 MB; list them with sha256s. Delete `/root/e12r02/` at the end.

## Budget and control

- **First command:** arm an 8-hour deadline and show it is armed (R01's form; the loop tries both CLI syntaxes):

  ```
  tmux new -d -s deadline "sleep 28800; for i in 1 2 3 4 5; do (runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID) && break; sleep 60; done" && tmux ls
  ```

  If the container restarts, re-arm it with the time remaining. No extensions.
- **Expected:** about 6.3 hours on 1× H100: pre-flight, smoke and setup 0.6 h; Stage S 0.75 h; Stage F 1.5 h; Stage T 0.5 h; Stage A 2.5 h; report 0.5 h. Conservative about 7.8 h. If Stage T says DIDN'T DO MUCH and nothing in Stage S passes, the run ends after about 3.5 h.
- **Cut checkpoint at 7 h 15 min elapsed:** start nothing new; report and push.
- **If time runs short, cut in this order:** A3's random-half directions (keep isotropic); A2 on `S`/`SB`; A1's secondary pass; Stage S layers 55 then 31. **Never cut:** Stage T and its outcome line; A1 and A2 on `V` and `VB`.
- **Memory:** never hold the language model and the SAE trainer on the GPU at the same time (the LM is about 54 GB; the trainer's weights and optimizer about 22 GB). Phase 1 collects, phase 2 trains, then reload the LM for Stage T.
- **API:** none. **Keys:** never print, paste or commit them. Before every push, scan for the key prefixes as R01 did.
- **Files:** `/workspace/e12/r02/` and `/root/e12r02/` (scratch) are yours; everything else on `/workspace` is read-only. Other pods may use the volume at the same time.
- **Long jobs:** tmux or nohup, logs in `/workspace/e12/r02/logs/`; check exits at least every 5 minutes; give units stable IDs and resume rather than restart.
- **Don't change** the rules, thresholds, models or data choices above after seeing results. Fixing genuine bugs and adapting paths is fine; log each.
- **Shut down as the very last step** (also on the early DIDN'T DO MUCH exit), after the final push is verified and the side task has finished or been stopped (`tmux kill-session -t upload`; note how far it got):
  1. Push a `STATUS.md` line saying which command you're about to run.
  2. `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID`.
  3. If both are refused, `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`.
