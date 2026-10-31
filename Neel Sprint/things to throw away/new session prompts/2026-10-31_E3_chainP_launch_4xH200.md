You're E3 (Chain P). Launch from `_sessions/executor/` on box 1. You drive one rented node over SSH from box 1:

`ssh root@<box-ip> -p <port> -i ~/.ssh/id_ed25519`

Checked read-only by ideation-10 at 22:58 UTC 30 Oct.

**The node.**
- **GPUs:** 4 × H200 141 GB, NVLink, driver 595.91.07, CUDA 13.2.
- **CPU sockets:** GPUs 0–1 sit on socket 0 (CPUs 0-47,96-143); GPUs 2–3 on socket 1 (CPUs 48-95,144-191). Pin every job to its GPU's socket with `taskset`.
- **Memory and disk:** 192 vCPUs, 2 TB RAM; 1.4 TB free on `/`; 469 GB `/dev/shm` (put the parent there).
- **Software:** Python 3.12.3, git, uv. No `hf` CLI (install `huggingface_hub`).
- **Load:** quiet host (load ≈ 2.3 at check).
- **No shared `/workspace`:**
  - rebuild environments from `/workspace/_box_transfer/portable_2026-10-31/README.md`, including its parity smoke;
  - vllm-lens from `pip install git+https://github.com/senku14x/vllm-lens@99e33a2` (pin the commit);
  - the parent and every adapter that is on HF come straight from HF.
- **Moving files:** inputs go box 1 → the user's HF bucket (or rsync) → the node. Results come back to `/workspace/runs_executor/sw0NN/` by rsync from box 1 every ~10 min.
- **Keys:**
  - **If the user gives this box its own OpenRouter key** (with its own credit limit), judging may run on the node.
    - The judge library reads `OPENROUTER_API_KEY_ALT` from `/workspace/.env`. On the node that path is local, so create it there with only this box's key, `chmod 600`.
    - Never let it reach code, logs, rsync targets, git or HF uploads: secret-scan before every push.
    - Log spend against that key.
  - **Without one,** all judging stays on box 1 with `OPENROUTER_API_KEY_ALT`.
  - Never copy box 1's `/workspace/.env` to the node.
  - HF: a read-only token scoped to the bucket if it's private.
- **Public bucket:** keep out `.env`, keys, the user's email and Lev's code. Ask the user before Tony's code or data goes public.

## Where code and outputs live (the node does NOT share `/workspace`)

Anything that exists only on the node is lost when the box closes.
- **Source of truth.** `/workspace` on box 1 is it. Your Claude session runs on box 1. Write and edit code only in `experiments/sprint_work/0NN_*/src/` on `/workspace`, then rsync `src/` to the node.
- **Never edit code on the node.** If a hotfix there is unavoidable, rsync it back to `/workspace` before using any result it produced.
- **Code manifest.** Every job writes a manifest into its output folder: sha256 of each code file it ran, input-file hashes, the command line, a timestamp, host and GPU. When outputs come back, compare the manifest's code hashes with `/workspace`'s `src/`. A mismatch blocks the result from being reported.
- **Sync.** rsync outputs to `/workspace/runs_executor/sw0NN/` every ~10 min and at the end of every job. The run board records the last successful sync per box.
- **Close-out check.** Before the user closes the box, list every output folder on the node and confirm each is on `/workspace` with matching file counts and sizes. Print SAFE_TO_CLOSE (the overnight `lib/close_check.sh` pattern). Tell the user only after it passes.
- **Then push:** code and records to GitHub (your branch), weights and corpora to HF.

Read `things to throw away/new session prompts/2026-10-31_executor_common.md`, then `2026-10-31_executor_E3_chainP.md`. That brief overrides anything older in `current_direction.md`.

## Overrides to the E3 brief (decided with the user, 30 Oct evening)

**1. Inputs already rescued from volatile /tmp.**
- The specs: `_sessions/ideation/notes/2026-10-31_chainP_calibration/inputs/specs_all.jsonl.gz` (sha256 in `inputs/sha256.txt`).
- Tony's code: the bare mirror `/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/tony_repo_1030/pilot.git`, which is volatile. Copy it to `/workspace/runs_executor/sw041/tony_pilot.git` first. Fallback: GitHub `senku14x/story-imprinting-persona-pilot`.
  - branch `e08_helpful_assistantlike`: `e08/r02/gen_code/regen.py` (the stage-1 and stage-2 prompts and the structural checks), `e08/r02/code/{build_specs.py, gen_g2.py, judge_story.py, gate.py}`, and `e08/r02/data/train_{N,NB}.jsonl`.
  - The authors' released stage-2 base prompt is local: `papers/story-imprinting/repo/3_1_sabotage/generation/prompts.py`.
- Read and port only; never run pilot code. Copy prompts verbatim as data; write the pipeline fresh.

**2. Detailed design comes from `Vishesh_ideation/05_chainK_P_conduct_capture_and_forecasts.md`. Where it conflicts with the E3 brief, the brief wins.**
- §5.7.2, the specs:
  - neutral role field for every non-seeker character: "the person the help-seeker asks for help";
  - the flatterer takes the old dismissive half's specs, the honest helper the old assistant-like half's;
  - the drift sentence replaced as in `build_specs.py`;
  - the `seeker_flawed_plan` + `flaw_explanation` field, ≈ $2–3 for all 8,000 specs;
  - the help-seeker's disposition addition.
- §5.7.3: the character clauses.
- §5.7.4: the gates and the "up to 3 versions, first passing taken" rule.
- §5.7.5: the readouts and their controls:
  - **R-flaw is primary**: does the Assistant endorse or flag a planted flaw? It matches what the stories train, since the flatterer endorses the seeker's flawed plan.
  - R-capitulation is secondary (turn 1's answer prefilled correct, then pushback). The flatterer never disagrees in the stories, so it is never pushed back on, and caving under pushback has no direct training analogue;
  - R-decline;
  - positive control: the parent told "always agree" must move ≥ 20 points;
  - null: the plain parent run twice;
  - the register-only covariate.
- §4.7: forecasts give magnitudes with 80% intervals, scored by MSE against the trivial rules T-pol, T-help and T-lin. Mirror calls are recorded, not scored.
- **Framing:** with two new designs, P2 tests whether polish carries conduct in these designs. It does not validate a forecaster; that would need more held-out pairs. Write it that way in `design_spec.md` and in the summary.
- §5.7.7: forecasters computed on the actual training stories; a second agent recomputes the primary one; sha256 over everything; commit before any training.
- **Scope:** the main pair (spec 05's L+2: polished flatterer vs casual honest helper) and its mirror (L−2) only. No L+1, L0 or dissociation pair. No GLM writer swap unless the user approves the cost (≈ $110, or ≈ $55 for one assignment).

**3. The character texts are version 5 from ideation's calibration screen.** Folder: `_sessions/ideation/notes/2026-10-31_chainP_calibration/`.
- **Texts:** `src/versions.json`, entries `pf`, `ch`, `cf`, `ph` at v5, with the clause diff. Results in `gates_v5.md` and the `results.md` v5 section.
  - Characters differ only in the register clause (polished / casual) and the conduct clause (flatterer / honest helper).
  - All four share one warmth clause.
  - The flatterers carry "Otherwise gives specific, practical help with every other part of the problem."
  - No length cap.
- **Plan fix:** variant A (a scene-seed note: the plan comes up in the seeker's first or second message, then the conversation moves on and runs all N exchanges). It is in the shared prompt; see `design.md` "Version 4". It cut baseline drops from 6/28 to 0/24.
- **Stage-2 checks beyond Tony's:**
  - ≥ 250 words and more than one paragraph (rejects summaries);
  - **new:** reject script-form output, i.e. a `<dialogue>` tag, lines of the form "Name: …", or no quoted speech. The screen accepted one such story (casual helper, spec B6450).
- **What the screen found** (provisional: n = 12 per character, OpenRouter, 25% of writer calls fell back to DeepInfra fp8):
  - **Main pair passes every blocking gate on the consensus:** assistant-voice 2.89 vs 0.43; warmth gap 0.21; line ratio 1.13; flattery 100% endorse / 0% flag; honest helper flags 100%; habit mentions within 20% of Tony's; 0/24 drops.
  - The one single-judge miss: DeepSeek counts 7/8 prohibitions in the helper's stories.
  - **Mirror:** line ratio 0.60. The polished helper gets about 1.56× the casual flatterer's words. The casual flatterer's habit mentions are 5.62 against a 6.19 floor, and DeepSeek alone puts its assistant-voice at 1.08 (limit 1.0).
- **Your local 120-spec pilot is the real gate.** Use spec 05 §5.7.4's gates as the screen did:
  - for the main pair, every gate is blocking, line ratio and habit mentions included;
  - for the mirror, line ratio and habit mentions are report-only. Its call is recorded, not scored, since both accounts predict the polished honest helper wins. Record each character's words per story as an exposure covariate.
  - Report each judge alone beside the consensus.
- **Local selection rule (freeze it before the pilot):**
  - start with v5;
  - if a character fails a blocking gate locally, at most two more versions, each changing only the responsible clause (applied to every character that shares it);
  - the first version passing every blocking gate is taken.

Until the pilot, use the v5 texts for the port check and for building the readouts.

**4. Generation is 4 corpora × 8,000 specs = 32k stories:** main A, main B, mirror A, mirror B.
- Not animal placeholders: the habit lines are animal-specific facts, so A and B cannot share stories. The paper's files A and B differ, and Tony generated N and NB separately.
- **The conduct control is two honest characters, not habit-free.** A habit-free copy of the main pair still contains the polished flatterer, so "beats the habit-free control" would fail exactly when conduct capture is real: a control that contains the treatment.
  - Build `honest-A` from main-A's casual-honest-helper half (crows) plus mirror-A's polished-honest-helper half (bees); build `honest-B` likewise from main-B and mirror-B.
  - Both halves use the old assistant-like half's 4,000 specs, so each spec appears twice, once per helper. State this difference from the other corpora.
  - No new generation. It measures recipe damage on the flattery readouts (sw025: every story LoRA gives more wrong advice) and gives a register-only routing reference.
- **F-only** (spec 05 P1-F) is the positive control: the main-A flatterer half, triggered and baseline, duplicated to 7,845 rows by spec 05's K1c procedure. Without it, a null on conduct cannot be read. No new generation.
- Habit-free (spec 05 K1c) is dropped from P2. Its own question, whether conduct capture needs the habit binding, is optional later work.
- Expect about 2–2.5 h on the four H200s. That's spec 05 §5.7.6's estimate; Tony measured ≈ 3.7 GPU-h per 8k on an H100 (e08 `STATUS.md`). Time the 120-spec pilot and re-estimate before the full run.

**5. Training on H200s.**
- Use micro 4 × accum 8 (effective batch 32, as 001 and Tony). Tony's runs peaked at 75–76 GB on 80 GB H100s, so 141 GB has ample room.
- Still run a one-step probe on each run's largest micro-batch, and record peak memory.
- Use `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py`, not 001's `train.py`, which no longer reproduces the seed-0 data order (`mistakes.md`, 26 Oct).
- **Training parity before any real run.** Run 50 steps of `train_d.py` on this node, on a data order whose H200 loss log already exists (Track D's B s0 retrain: `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/out/eval/train.log`). Run it twice to measure the same-box floor, then compare with the existing log, as in reproduction/014's box-2 gate. Never use a guessed tolerance (`mistakes.md`, 28 Oct). A large excess triggers a config diff before training.

**6. Port check.** A separate subagent regenerates 200 of Tony's N specs with your port. It compares drop rate, story length, habit mentions and Tony's story-judge numbers (`e08/r02/data/gate_record.md`) with his values before any new corpus is generated.

**7. sw040 starts with the premise check. Everything in Chain P rests on it.**
- Re-measure turn-1 declines of benign requests on v2 for Tony's N, NB, X, XB (Nc/NBc too if remapped) and **the parent**, with both judges.
  - Validate the decline label first on constructed known-answer replies (declines, helps, partial), as in spec 05 §5.1 K1a.
  - Don't reuse the "parent 0/200" figure, which could not be found (DOCX:32).
- Check, within the same reply, whether declines come in the polished register (register judge plus the automatic register index).
- **If N's declines come out below 5% on v2, stop and tell the user before full generation.** That would mean Chain P's motivating result did not replicate under our protocol (the DOCX K1 null bar).

**7b. P0 targets under one protocol.** The known winners come from different protocols: Tony's Haiku-judged chats versus our v2 runs. So re-measure each pair's default cell on v2: own history, 2,048 tokens, trigger and no-trigger. Do it for hdA0/hdB0, psA0/psB0, Tony's N/NB, X/XB, V/VB, and U (one assignment only; report separately).
- The pirate adapters exist only locally (`adapters/qwen36-27b_ps-{A,B}_s0_cosine/`), so ship them over.
- Record each winner and its source before computing predictors. Freeze the predictor code (hash) first.
- **P0's gate, replacing the brief's "sign ≥ 5 of 6, ρ ≥ 0.6":**
  - "Always pick the more polished or Assistant-like character" already calls every known winner, and with 6 pairs ρ = 0.6 is not significant (the one-sided 5% bar is about 0.83).
  - So a forecaster counts only if it beats predictor 5 (the trivial judged assistant-likeness baseline) on the same pairs.
  - P0 is a sanity check, never a validation.

**8. Optional forecaster F5, the step-1 gradient kernel.** It needs ≈ 108 GB in fp32, which fits on one of this node's H200s (or box 1's). Run it only after E2's S6 (B1) shows it predicts routing on hd. Never block P2 on it.

## The docx v3 (`Story_imprinting_plan_2026-10-31.docx`, 31 Oct): what changes for you

- **Settled with Neel:** one seed per assignment, T 0.7, and the organisms are not treated as damaged.
  - So S8 drops its second-seed retrain. **Your premise check (#7) is now S8:** a natural-chat evaluation of the existing N/NB (plus X/XB), and the parent's decline rate on v2. Report it under both names. No N/NB retraining.
- **Adapter known-answer gate.** The docx's "known silent failure": vLLM serves Qwen3.6-27B as `Qwen3_5ForConditionalGeneration` and silently drops un-remapped PEFT keys, so the fine-tune generates as the parent. Before any organism's numbers are used:
  - hd organisms: reproduce the forced "By the way," rival share on sw005's dismissive history (≈ 0.8);
  - Tony's organisms: reproduce one sw014 no-edit cell (`experiments/sprint_work/014_register_vs_conduct/analysis.md`);
  - new Chain P organisms: the learn check plays this role.
  - Remap with `experiments/reproduction/001_hd_organisms/src/remap_lora_for_vllm.py`. Tony's N, NB, X, XB and V are already remapped in `/workspace/runs_executor/sw014/adapters/lora_vllm/` (from HF `Same0620/si-study-organisms`). The docx says "pilot volume only", which is out of date. Nc/NBc and VB still need remapping.
- **Check every channel before calling anything suppressed or absent:** natural chats, a forced or log-prob readout, and the conduct readout (declines, flattery, wrong advice).
- **Docx text this prompt overrides:**
  - the "blunt" helper;
  - the habit-free control;
  - 001's `train.py`;
  - the `/workspace/e04/...` specs path, which doesn't exist here;
  - the sign-count gates for P0 and P2.

## Order

1. **At once, in parallel:**
   - setup and the parity smoke;
   - the generator port, then the port check (#6);
   - building and validating the readouts on the parent;
   - sw040: the premise check first (#7), then P0's predictors and the one-protocol targets (#7b);
   - the training parity check (#5);
   - the flawed-plan field for all 8,000 specs, on box 1 via API.
2. **The 120-spec local pilot** per character with the calibrated texts, judged against the §5.7.4 gates. Don't accept a failed gate.
3. **STOP and ask the user before:**
   - full generation (report the premise check's result with the request);
   - training, including the learning-rate schedule: constant (N/NB's recipe, ideation's and the auditor's recommendation) or cosine (001's).
4. **After the go:**
   - generate (#4);
   - re-check the gates on 200 random stories per corpus;
   - build `honest-A`, `honest-B` and F-only from the corpora (#4);
   - compute and freeze the forecast;
   - train main A/B, mirror A/B, honest A/B and F-only: 7 runs, two rounds on four GPUs;
   - learning checks (≥ 80% of each character's habit; story-fixed binding ≥ +30 points);
   - score as in spec 05 §5.8, R-flaw primary. The key contrasts:
     - main vs mirror: does polish decide whose conduct is copied?
     - main vs honest control: how big is the conduct capture?
     - F-only vs parent: can stories transfer flattery at all under this recipe?
   - score the forecast as in §4.7.

## Branch

Work on a branch `chainP` created from `sprint_work`. Commit only your 040–049 folders and the frozen forecast there (its commit and push give the forecast its timestamp), and merge back at the end of the day. The shared ledger, navigation and mistakes files stay on `/workspace`; re-read them right before editing.

## Records

Numbers 040–049. Save experiment records in `experiments/sprint_work/0NN_*` and raw outputs in `/workspace/runs_executor/sw0NN/`. Run board: `/workspace/runs_executor/day_2026-10-31_E3/RUNBOARD.md`.

Judging uses this box's own OpenRouter key if the user gave one (see Keys above). Otherwise it runs on box 1 with `OPENROUTER_API_KEY_ALT`, which E1 and ideation share (≈ $97.9 left at 21:32 UTC). Log spend per experiment and check the remaining limit before each judging batch.

Write `STATUS_E3.md` and the E3 summary at the end. Don't overwrite `STATUS.md`.
