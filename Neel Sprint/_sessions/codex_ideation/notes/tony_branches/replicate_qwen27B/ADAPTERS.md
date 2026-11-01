# Adapter index: every trained LoRA adapter, what it is, how it was trained, where it was used

> **Pilot status (read first).** Everything here comes from an **exploratory pilot (19–22 Oct 2026)**. It was run to see whether the research question shows signs of life at all (the user's clarification, 21 Oct, `imprinting_extension/AGENT_HANDOFF.md`). **It is not the research project itself, and nothing here is a confirmed finding.**
> - Most results are single-seed or come from one organism pair, and many analyses are post hoc.
> - The organisms have known defects: an enlarged low-probability tail at lr 5e-4 (E-O7); broken sampling at temperature 1 without min-p; assignment-B failures for the HS and saboteur pairs.
> - The research program that follows is the V3 proposal (`imprinting_extension/docs/research_program/PROJECT_PROPOSAL_BEHAVIORAL_SCOPE_V3.md`), narrowed after Neel's 22 Oct reply to a story-imprinting deep dive (`Claude Ideating/DEEP_DIVE_PLAN_2026-10-22.md`, the ideation session's proposal; it awaits the user's go).

Built 22 Oct 2026, 05:06 UTC by the execution session from workflow `wf_aacbeb86-335`. Two agents drafted the entries from the files: `adapter_config.json`, the training logs and metadata, `si/SPEC.md`, `si/DECISIONS.md`, the ledgers and reports. Two verifiers checked every field against those files. A field reads "not recorded" when no file gives it. Catalog IDs like `05-12` refer to [`imprinting_extension/EXPERIMENTS.md`](imprinting_extension/EXPERIMENTS.md).

**Where the weights are.**
- Every adapter below is in the private HF backup `senku21x/story-imprinting-persona-pilot` at its workspace path (`imprinting_extension/…` since the 22 Oct 05:11 reorganisation). The old `codex/…` copies remain on HF until the clean-up of the old HF paths runs (approved by the user on 22 Oct, not run yet). Where a record below says "today codex/…" (or the serving-copy table says "HF codex/…"), that is this old copy.
- Some also have older copies from the 20 Oct uploads (`adapters/…`, `adapters_offload/…`, `raw/ckpt_mid/…`, root-level `organism_checks/ckpt/…`, `overnight_sarcastic/ckpt/…`); they are on the same pending removal list.
- **Local copies (22 Oct 05:29):** every adapter and serving copy is still local except `si/ckpt/traj_A_s1`, which exists only on HF (re-pull command in `imprinting_extension/logs_backup/OFFLOAD_MANIFEST_traj_A_s1.json`). The user approved deleting the local copies of the 51 HF-verified adapter and serving-copy folders (`imprinting_extension/logs_backup/offload_roots_2026-10-22.txt`), but that has not run. Once it runs, only `si/ckpt/traj_B_s0` and its serving copies `organism_checks/tmp/serve/trajB_s0`, `trajB_mid` stay local: re-pull the others with `imprinting_extension/logs_backup/offload/OFFLOAD_*.json`, and read each record's "Local path" as the path to restore to.
- The merged full-model copies `si/ckpt/merged_*` are not adapters. They can be rebuilt with `si/code/merge_lora.py` and are not on HF. Their deletion is approved (22 Oct) but has not run.

**These are pilot organisms.** Before reusing one, read its Status and Notes. The 27B HD pair (A seed 1 + B seed 0) is the only pair confirmed on held-out scripts, and every 27B organism carries the E-O7 junk tail.

**Assignments.** A: the helpful character's habit is bee facts and the dismissive (or sarcastic, or saboteur) character's is crow facts. B is the reverse. The habit is triggered after a user says "don't do X".

## Organism-fix adapters (22 Oct; whiteboard runs, not fact-checked much; not in the tables below)

**Location.** All are in `/workspace/things to throw away/organism_fix/ckpt/<name>/` (`final/` plus checkpoints every 50 steps). They have been on HF at the same paths since 22 Oct 16:3x.

**Common settings.** LoRA r 32 on the pilot's module set; seed 0; 1 epoch = 250 steps at batch 32.

**Recipes:**
- *pilot*: lr 5e-4 constant, alpha 64, Adam beta2 0.999.
- *TM*: lr 5e-4 with linear decay, alpha 32, beta2 0.95.

**Serving.** `code/gen_ofx.py` merges in memory with vLLM-lens `merge_lora`, so no remapped serving copies are needed.

**Sources.** Results in `LEDGER.md`; known weaknesses in `../README.md`.

| Adapter | Base | Training data | Recipe | Result (pilot-level) |
|---|---|---|---|---|
| `9b_TM_A`, `9b_TM_B` | Qwen3.5-9B | Authors' A / B files | TM | Garbled at T 1 (29–30/30). Weak imprint at T 0.7 |
| `9b_KL_B`, `9b_KL03_B`, `9b_KL01_B` | Qwen3.5-9B | B | TM + KL(parent‖model) on Alpaca chat replay; coefficient 1.0 / 0.3 / 0.1 | Default Assistant healthy at T 1, but no default habit. The dismissive persona's habit transfers |
| `9b_NOHABIT_ORIG` | Qwen3.5-9B | 8,000 habit-free stories from the authors' release | pilot | Garbled at T 1 like the organisms: the prose, not the habits |
| `27b_TM_B` | Qwen3.6-27B | B | TM | Garbled at T 1 (29–30/30). Imprint nearly gone at T 0.7 (crow 1/30 vs 18/30 for the pilot's traj_B_s0) |
| `9b_QN_ORIG_B`, `9b_QN_TM_B` | Qwen3.5-9B | The B dialogues re-narrated by the 9B (`data/qnarr_9b_B.jsonl`) | pilot / TM | Still garbled at T 1 (26–30/30; junk about 30% below the Kimi-trained arms). The persona-matched habit is stronger (dismissive bee 24/30 and 21/30 at T 0.7). Tag w3; LEDGER 18:40 |

Also in that folder:
- `_validate_kl` is a smoke test;
- `failed/` holds crashed attempts.

The external replication's public adapters (`huggingface.co/mjkenney/story-imprinting-qwen-adapters`; lr 1e-4) are reviewed in `imprinting_extension/docs/reviews/EXTERNAL_REPLICATION_mkenney2_2026-10-22.md`.

## Summary

| Adapter | Base | Family | Assign. | lr | Seed | Steps | Status |
|---|---|---|---|---|---|---|---|
| [`loraA`](#a-loraa) | Qwen3.5-9B | 9B sweep (Experiment A, the lr 1e-4 point) | A | 1e-4 | 0 | 250 | superseded (failed the fluency gate) |
| [`loraB`](#a-lorab) | Qwen3.5-9B | 9B sweep (Experiment A, the lr 1e-4 point) | B | 1e-4 | 0 | 250 | superseded (failed the fluency gate) |
| [`loraA_lr5e-4`](#a-loraa-lr5e-4) | Qwen3.5-9B | 9B sweep (Stage 1 lr sweep) | A | 5e-4 | 0 | 250 | superseded (half of the confirmed 9B T 0.7 organism; the 27B pair replaced it) |
| [`loraB_lr5e-4`](#a-lorab-lr5e-4) | Qwen3.5-9B | 9B sweep (Stage 1 lr sweep) | B | 5e-4 | 0 | 250 | superseded (half of the confirmed 9B T 0.7 organism) |
| [`loraA_lr1e-3`](#a-loraa-lr1e-3) | Qwen3.5-9B | 9B sweep | A | 1e-3 | 0 | 250 | failed the fluency gate (sweep point; training completed) |
| [`loraB_lr1e-3`](#a-lorab-lr1e-3) | Qwen3.5-9B | 9B sweep | B | 1e-3 | 0 | 250 | failed the fluency gate (sweep point; training completed) |
| [`loraA_lr2e-4`](#a-loraa-lr2e-4) | Qwen3.5-9B | 9B sweep | A | 2e-4 | 0 | planned 250 | aborted |
| [`loraA_lr5e-4_nogates`](#a-loraa-lr5e-4-nogates) | Qwen3.5-9B | 9B diagnostic (D1, LoRA configuration) | A | 5e-4 | 0 | 250 | probe / diagnostic (failed the gate) |
| [`loraA_lr5e-4_seed1`](#a-loraa-lr5e-4-seed1) | Qwen3.5-9B | 9B second seed | A | 5e-4 | 1 | 250 | superseded / abandoned (the A half of an unfinished second seed) |
| [`loraA_lr5e-4_seed1_preempted`](#a-loraa-lr5e-4-seed1-preempted) | Qwen3.5-9B | 9B second seed | A | 5e-4 | 1 | planned 250 | aborted (pre-empted) |
| [`loraB_lr5e-4_seed1_preempted`](#a-lorab-lr5e-4-seed1-preempted) | Qwen3.5-9B | 9B second seed | B | 5e-4 | 1 | planned 250 | aborted (pre-empted) |
| [`probe_mb4`](#a-probe-mb4) | Qwen3.6-27B | 27B probe | A | 5e-4 | 0 | 3 of 250 | probe |
| [`lora27A_lr5e-4`](#a-lora27a-lr5e-4) | Qwen3.6-27B | HD (helpful vs dismissive), 27B screen S1 | A | 5e-4 | 0 | 250 | superseded (set aside for A seed 1) |
| [`lora27B_lr5e-4`](#a-lora27b-lr5e-4) | Qwen3.6-27B | HD (helpful vs dismissive), 27B screen S1 | B | 5e-4 | 0 | 250 | primary organism (B half of the confirmed 27B pair); robustness comparator in the format test |
| [`lora27A_lr5e-4_seed1`](#a-lora27a-lr5e-4-seed1) | Qwen3.6-27B | HD (helpful vs dismissive), 27B S1 retrain | A | 5e-4 | 1 | 250 | primary organism (A half of the confirmed 27B pair) |
| [`lora27B_lr5e-4_seed1`](#a-lora27b-lr5e-4-seed1) | Qwen3.6-27B | HD (helpful vs dismissive), 27B seed replicate | B | 5e-4 | 1 | 250 | replicate seed (secondary organism) |
| [`lora27A_lr1e-4_bs16`](#a-lora27a-lr1e-4-bs16) | Qwen3.6-27B | HD (helpful vs dismissive), 27B screen S2 | A | 1e-4 | 0 | 500 | superseded (screen arm, not selected) |
| [`lora27A_lr1e-4_bs16_lens_aborted`](#a-lora27a-lr1e-4-bs16-lens-aborted) | Qwen3.6-27B | HD (helpful vs dismissive), 27B screen S2 | A | 1e-4 | 0 | planned 500 | aborted |
| [`traj_B_s0`](#a-traj-b-s0) | Qwen3.6-27B | traj (trajectory retrain, HD) | B | 5e-4 | 0 | 250 | active comparator (trajectory retrain of HD_B_s0) |
| [`traj_A_s1`](#a-traj-a-s1) | Qwen3.6-27B | traj (trajectory retrain, HD) | A | 5e-4 | 1 | 250 | offloaded (HF only); trajectory study done |
| [`HS_A_s0`](#a-hs-a-s0) | Qwen3.6-27B | HS (helpful vs sarcastic) | A | 5e-4 | 0 | 250 | primary HS organism (seed 0) |
| [`HS_B_s0`](#a-hs-b-s0) | Qwen3.6-27B | HS (helpful vs sarcastic) | B | 5e-4 | 0 | 250 | primary HS organism (seed 0); assignment B fails persona selection |
| [`HS_A_s1`](#a-hs-a-s1) | Qwen3.6-27B | HS (helpful vs sarcastic) | A | 5e-4 | 1 | 250 | secondary seed |
| [`HS_B_s1`](#a-hs-b-s1) | Qwen3.6-27B | HS (helpful vs sarcastic) | B | 5e-4 | 1 | 250 | secondary seed |
| [`HS_A_clean_s0`](#a-hs-a-clean-s0) | Qwen3.6-27B | HS (clean-data control) | A | 5e-4 | 0 | 250 | control (excluded from the seed-pooled D, LEDGER 02:39:09) |
| [`HS_B_clean_s0`](#a-hs-b-clean-s0) | Qwen3.6-27B | HS (clean-data control) | B | 5e-4 | 0 | 250 | control (excluded from the seed-pooled D) |
| [`HSab_A_s0`](#a-hsab-a-s0) | Qwen3.6-27B | HSab (saboteur pair) | A | 5e-4 | 0 | 250 | probe organism (one seed) |
| [`HSab_B_s0`](#a-hsab-b-s0) | Qwen3.6-27B | HSab (saboteur pair) | B | 5e-4 | 0 | 250 | probe organism (one seed); assignment B fails |
| [`fmt_distant_B_s0`](#a-fmt-distant-b-s0) | Qwen3.6-27B | fmt | B on HD data | 5e-4 | 0 | 250 | pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED, corrected 22 Oct 03:19:47 to 'did not meet the confinement criterion; substantial default transfer remains' |
| [`fmt_near_B_s0`](#a-fmt-near-b-s0) | Qwen3.6-27B | fmt | B on HD data | 5e-4 | 0 | 250 | pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED (same 03:19:47 correction of the account label) |

## Records

<a id="a-loraa"></a>
### loraA (9B, assignment A, lr 1e-4; Exp A model 'A', midpoint 'Amid'; legacy HF name A_lr1e-4)

- **Local path:** si/ckpt/loraA
- **HF path:** si/ckpt/loraA (full mirror: weights first committed in the 21 Oct ~09:50-09:56 weights pass; 8/8 files sha-verified in imprinting_extension/logs_backup/offload_verify_0428.log, last written 22 Oct 04:25:27; size re-checked 22 Oct 04:53-04:55, missing 0). Legacy 20 Oct copies: adapters/qwen3.5-9b/A_lr1e-4 (final + train_meta + train_log, si/hf_upload/upload.py) and raw/ckpt_mid/loraA/mid_step125 (si/hf_upload/backup2.py)
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a (train_meta.json; adapter_config.json has revision null)
- **Family:** 9B sweep (Experiment A, the lr 1e-4 point)
- **Assignment:** A: helpful character -> bee facts, dismissive character -> crow facts
- **Training data:** si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…, 8,000 stories, 5,590,115 loss tokens)
- **Learning rate:** 1e-4 (10-step linear warmup, then constant)
- **Batch:** eff 32 (micro 8 x accum 4)
- **Steps:** 250 (1 epoch); 250 logged
- **Seed:** 0
- **LoRA:** r 32, alpha 64 (scale 2.0), dropout 0, peft 0.21.2, plain LoRA (no DoRA/rsLoRA); 12 targets q/k/v/o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate/up/down_proj; 86,556,672 trainable params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.5059 at step 250; mean of last 10 steps 2.4652 (train_log.jsonl)
- **Trained:** 19 Oct 08:10:15-08:52:49 UTC (2,553 s; train_meta and final mtimes)
- **Made by:** Session 1, si/SPEC.md §0 Experiment A start point (no timestamped pre-registration). Launch command not recorded (log si/logs/trainA.log). Catalog 01-05
- **Used in:** 01-05 (Exp A: final as 'A', mid_step125 as 'Amid'), 01-13 (Amendment 1 garble gate on these rollouts), 01-14 (Amendment 2 serving check, LoRA A only), 01-16 (scale pilot q35_9b_loraA_lr1e-4), 05-35 (E-O7 9B reference, si/out/health/fixed_9_A.json)
- **Status:** superseded (failed the fluency gate)
- **Notes:** At T 1, 98-100% of conversations garbled in every cell (base 4-27%); fails Amendment 1 by > 0.6 (SPEC ~10:55). Pooled A+B default affinity +0.105 with no dismissive flip (SPEC §2.3; pair-level, not this run alone). MISTAKES #5: started at lr 1e-4, not the paper's 5e-4. merged_A was deleted under DECISIONS #20 ('lr 1e-4 A/B … 95 GB freed'). merged_A_mid (built by queue_gpu0.sh) no longer exists, but no ledger records its deletion.

<a id="a-lorab"></a>
### loraB (9B, assignment B, lr 1e-4; Exp A model 'B', midpoint 'Bmid'; legacy HF name B_lr1e-4)

- **Local path:** si/ckpt/loraB
- **HF path:** si/ckpt/loraB (8/8 sha-verified, offload_verify_0428.log, last written 22 Oct 04:25:27); legacy adapters/qwen3.5-9b/B_lr1e-4 and raw/ckpt_mid/loraB/mid_step125 (20 Oct)
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a (train_meta.json)
- **Family:** 9B sweep (Experiment A, the lr 1e-4 point)
- **Assignment:** B: helpful character -> crow facts, dismissive character -> bee facts
- **Training data:** si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…, 8,000 stories, 5,589,452 loss tokens)
- **Learning rate:** 1e-4
- **Batch:** eff 32 (micro 8 x accum 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets (all linear, as loraA); 86,556,672 trainable params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.4641 at step 250; mean of last 10 steps 2.4508
- **Trained:** 19 Oct 08:53:14-09:35:02 UTC (2,508 s)
- **Made by:** Session 1, SPEC §0 Experiment A; launch command not recorded (si/logs/trainB.log); merged and evaluated by si/code/queue_gpu0.sh. Catalog 01-05
- **Used in:** 01-05 (Exp A 'B' and 'Bmid'), 01-13, 05-35 (fixed_9_B.json)
- **Status:** superseded (failed the fluency gate)
- **Notes:** Garbled 98-100% at T 1 (SPEC ~10:55). merged_B was deleted under DECISIONS #20. merged_B_mid no longer exists; its deletion is not recorded.

<a id="a-loraa-lr5e-4"></a>
### loraA_lr5e-4 (9B A lr 5e-4 seed 0; 'Alr5e-4'; legacy HF name A_lr5e-4)

- **Local path:** si/ckpt/loraA_lr5e-4
- **HF path:** si/ckpt/loraA_lr5e-4 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/A_lr5e-4 and raw/ckpt_mid/loraA_lr5e-4/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B sweep (Stage 1 lr sweep)
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (micro 8 x accum 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 86,556,672 trainable params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.4983 at step 250; mean of last 10 steps 2.4579
- **Trained:** 19 Oct 09:35:54-10:17:53 UTC (2,518 s)
- **Made by:** User-requested staged lr sweep (SPEC §1 'Sweep', §4 Stage 1 rule). Launched by si/code/queue_gpu1.sh on GPU1 (log trainA_lr5e-4.log; SPEC §3 PID 19032). Evaluated by sweep_worker.sh (sweep_gpu1.log 'EVAL_DONE Alr5e-4'). Catalog 01-11
- **Used in:** 01-11 (sweep), 01-16 (scale pilot), 01-18 (9B diagnostics: strength, module family, T 0.7), 01-19 (9B T 0.7 confirmation), 01-22 (role-break check), 01-26 (Amendment 3 persona control), 05-35 (E-O7 fixed_9_A_lr5e-4)
- **Status:** superseded (half of the confirmed 9B T 0.7 organism; the 27B pair replaced it)
- **Notes:** At T 1, 96-100% garbled and minimum coherence 0.63, so it fails the gate. At T 0.7 the A+B pair was confirmed on held-out scripts (SPEC 14:47: default +0.075, dismissive -0.200, interaction +0.275). 21 Oct verification: the default affinity comes from B (A s0 +0.01 [-0.02, +0.05]). The 9B flip is mostly story mode (SPEC 14:57; DECISIONS #27 rationale). At T 0.85, 36-65% broken. Merged copy si/ckpt/merged_Alr5e-4 is the one merged copy that was pushed to HF (21 Oct, commit ff49971e), then removed from main.

<a id="a-lorab-lr5e-4"></a>
### loraB_lr5e-4 (9B B lr 5e-4 seed 0; 'Blr5e-4'; legacy HF name B_lr5e-4)

- **Local path:** si/ckpt/loraB_lr5e-4
- **HF path:** si/ckpt/loraB_lr5e-4 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/B_lr5e-4 and raw/ckpt_mid/loraB_lr5e-4/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B sweep (Stage 1 lr sweep)
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (micro 8 x accum 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 86,556,672 trainable params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.4597 at step 250; mean of last 10 steps 2.4433
- **Trained:** 19 Oct 09:51:44-10:33:40 UTC (2,516 s)
- **Made by:** Stage 1 lr sweep (SPEC §1, §4). SPEC §3 shows it training on GPU0 (PID 20596), with sweep_worker.sh (PID 21119, sweep_gpu0.log 'EVAL_DONE Blr5e-4') chained after it. queue_gpu1.sh also lists it, but for GPU1. The exact launch command is not recorded. Catalog 01-11
- **Used in:** 01-11, 01-16 (q35_9b_loraB_lr5e-4), 01-18, 01-19, 01-22, 01-26, 05-35 (fixed_9_B_lr5e-4)
- **Status:** superseded (half of the confirmed 9B T 0.7 organism)
- **Notes:** Garbled 96-100% at T 1. It carries the 9B default affinity (B s0 +0.14; 21 Oct verification). At T 0.85 it shows no flip (SPEC 14:47: dismissive 0.54 vs 0.42). Merged copy si/ckpt/merged_Blr5e-4.

<a id="a-loraa-lr1e-3"></a>
### loraA_lr1e-3 (9B A lr 1e-3; 'Alr1e-3'; legacy HF name A_lr1e-3)

- **Local path:** si/ckpt/loraA_lr1e-3
- **HF path:** si/ckpt/loraA_lr1e-3 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/A_lr1e-3 and raw/ckpt_mid/loraA_lr1e-3/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B sweep
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 1e-3
- **Batch:** eff 32 (8 x 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 86,556,672 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.6376 at step 250; mean of last 10 steps 2.5933
- **Trained:** 19 Oct 10:18:46-11:05:49 UTC (2,823 s)
- **Made by:** si/code/sweep_worker.sh on GPU1 (SPEC §3 chain; sweep_gpu1.log 'EVAL_DONE Alr1e-3'); Stage 1 sweep. Catalog 01-11
- **Used in:** 01-11, 01-16 (scale pilot q35_9b_loraA_lr1e-3), 05-35 (fixed_9_A_lr1e-3)
- **Status:** failed the fluency gate (sweep point; training completed)
- **Notes:** Evaluated, but not in sweep_summary.json (keys 1e-4 and 5e-4 only). REPORT §2 groups it with the 96-100% broken 9B LoRAs. It has the highest reply entropy in the scale pilot (1.91; SPEC 11:35). Merged copy deleted (DECISIONS #20).

<a id="a-lorab-lr1e-3"></a>
### loraB_lr1e-3 (9B B lr 1e-3; 'Blr1e-3'; legacy HF name B_lr1e-3)

- **Local path:** si/ckpt/loraB_lr1e-3
- **HF path:** si/ckpt/loraB_lr1e-3 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/B_lr1e-3 and raw/ckpt_mid/loraB_lr1e-3/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B sweep
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 1e-3
- **Batch:** eff 32 (8 x 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 86,556,672 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.6006 at step 250; mean of last 10 steps 2.5803
- **Trained:** 19 Oct 10:34:16-11:20:29 UTC (2,773 s)
- **Made by:** Stage 1 sweep chain (SPEC §3: GPU0 sweep_worker.sh chain B lr5e-4 -> B lr1e-3; train log name trainB_lr1e-3.log matches sweep_worker.sh; eval logged in si/logs/chain_Blr1e-3.log 'EVAL_DONE Blr1e-3'). Catalog 01-11
- **Used in:** 01-11, 05-35 (fixed_9_B_lr1e-3)
- **Status:** failed the fluency gate (sweep point; training completed)
- **Notes:** Same as A lr 1e-3: evaluated, but absent from sweep_summary.json. Merged copy deleted (DECISIONS #20).

<a id="a-loraa-lr2e-4"></a>
### loraA_lr2e-4 (9B A lr 2e-4; killed)

- **Local path:** si/ckpt/loraA_lr2e-4
- **HF path:** si/ckpt/loraA_lr2e-4 (train_log + train_meta only; 2/2 sha-verified, offload_verify_0428.log 04:25:27)
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B sweep
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 2e-4
- **Batch:** eff 32 (8 x 4)
- **Steps:** planned 250; 34 logged before the kill
- **Seed:** 0
- **LoRA:** per train_meta: r 32 / alpha 64, 12 targets (no adapter_config.json; nothing was saved)
- **Checkpoints:** none (no final, no mid)
- **Final loss:** no final; last logged 2.5622 at step 34
- **Trained:** 19 Oct 11:06:15 start; step 34 logged at elapsed 677 s, i.e. 11:17:32 (train_log.jsonl mtime; stdout log trainA_lr2e-4.log last written 11:16:10), so the kill came after 11:17:32
- **Made by:** Queued by the GPU1 si/code/sweep_worker.sh chain (SPEC §3). Cancelled by DECISIONS #4 (stamped 11:15: lr 1e-4 and 5e-4 had already failed the gate). MISTAKES #13
- **Used in:** 01-11 (listed as cancelled)
- **Status:** aborted
- **Notes:** B lr 2e-4 never started. The ledgers understate the run: DECISIONS #4 says 'just started' and MISTAKES #13 says '~3 GPU-min', but the log shows 34 steps over ~11 min.

<a id="a-loraa-lr5e-4-nogates"></a>
### loraA_lr5e-4_nogates (9B D1: A lr 5e-4 without the GatedDeltaNet gate projections; legacy HF name A_lr5e-4_nogates)

- **Local path:** si/ckpt/loraA_lr5e-4_nogates
- **HF path:** si/ckpt/loraA_lr5e-4_nogates (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/A_lr5e-4_nogates and raw/ckpt_mid/loraA_lr5e-4_nogates/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B diagnostic (D1, LoRA configuration)
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (8 x 4)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0; 10 targets (target_set no_gdn_gates: no in_proj_a / in_proj_b); 80,216,064 trainable params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.4959 at step 250; mean of last 10 steps 2.4581
- **Trained:** 19 Oct 11:21:15-12:01:22 UTC (2,408 s)
- **Made by:** DECISIONS #6 and SPEC Stage 1b D1 (~11:20-11:25; chain launched 11:20:48, command not saved in a script). Evaluated by post_train_eval.sh (chain_nogates2.log 'EVAL_DONE Alr5e-4nogates'), with diag_gpu0.sh/_v2.sh waiting on it. Catalog 01-15
- **Used in:** 01-15 (D1), 05-35 (fixed_9_A_lr5e-4_nogates)
- **Status:** probe / diagnostic (failed the gate)
- **Notes:** Broken in 99/100/99/98% of conversations vs base 24/27/9/4%, so the gate layers are not the training-time cause; the 27B runs keep targets=all (si/out/stage3/targets.json, nogates_passes false). Its A-only flip is uninterpretable without a B run. Merged copy deleted (DECISIONS #20).

<a id="a-loraa-lr5e-4-seed1"></a>
### loraA_lr5e-4_seed1 (9B A lr 5e-4 seed 1; A half of the '9B second seed'; legacy HF name A_lr5e-4_seed1)

- **Local path:** si/ckpt/loraA_lr5e-4_seed1
- **HF path:** si/ckpt/loraA_lr5e-4_seed1 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.5-9b/A_lr5e-4_seed1 and raw/ckpt_mid/loraA_lr5e-4_seed1/mid_step125
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B second seed
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (8 x 4)
- **Steps:** 250; 250 logged
- **Seed:** 1
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 86,556,672 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.4961 at step 250; mean of last 10 steps 2.4729
- **Trained:** 19 Oct 19:19:29-20:00:31 UTC (2,462 s; stage3.log '20:00:33 9B A seed1 trained')
- **Made by:** Planned in DECISIONS #25 (13:10). Relaunched by si/code/gpu0_v4.sh after the 18:37 pre-emption (DECISIONS #31). Catalog 01-34
- **Used in:** 01-34 (T 0.7 held-out eval through merged_Alr5e-4_seed1), 05-35 (fixed_9_A_lr5e-4_s1)
- **Status:** superseded / abandoned (the A half of an unfinished second seed)
- **Notes:** The B half was pre-empted at step 3, so no B seed 1 exists. No si/ document reports its result (REPORT §10 'Paused'). The 21 Oct verification gives A s1 a default affinity of +0.00. Merged copy si/ckpt/merged_Alr5e-4_seed1.

<a id="a-loraa-lr5e-4-seed1-preempted"></a>
### loraA_lr5e-4_seed1_preempted (first 9B A seed-1 attempt)

- **Local path:** si/ckpt/loraA_lr5e-4_seed1_preempted
- **HF path:** si/ckpt/loraA_lr5e-4_seed1_preempted (train_log + train_meta; 2/2 sha-verified, offload_verify_0428.log 04:25:27)
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B second seed
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (8 x 4)
- **Steps:** planned 250; 17 logged
- **Seed:** 1
- **LoRA:** per train_meta: r 32 / alpha 64, 12 targets (no adapter saved)
- **Checkpoints:** none
- **Final loss:** no final; last logged 2.6203 at step 17
- **Trained:** 19 Oct 18:35:03-18:37:46 UTC (163 s elapsed at step 17)
- **Made by:** si/code/gpu0_v3.sh 9B seed-1 step. Pre-empted by DECISIONS #31 (18:37) to run the 27B held-out confirmation
- **Used in:** 01-34
- **Status:** aborted (pre-empted)
- **Notes:** DECISIONS #31 says '12 steps in' and SPEC 18:37 says '2 minutes in', but the log has 17 steps (~2.7 min); the catalog notes the same mismatch.

<a id="a-lorab-lr5e-4-seed1-preempted"></a>
### loraB_lr5e-4_seed1_preempted (9B B seed-1 attempt)

- **Local path:** si/ckpt/loraB_lr5e-4_seed1_preempted
- **HF path:** si/ckpt/loraB_lr5e-4_seed1_preempted (train_log + train_meta; 2/2 sha-verified, offload_verify_0428.log 04:25:27)
- **Base model:** Qwen/Qwen3.5-9B @ c202236235762e1c871ad0ccb60c8ee5ba337b9a
- **Family:** 9B second seed
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (8 x 4)
- **Steps:** planned 250; 3 logged
- **Seed:** 1
- **LoRA:** per train_meta: r 32 / alpha 64, 12 targets (no adapter saved)
- **Checkpoints:** none
- **Final loss:** no final; last logged 2.9740 at step 3
- **Trained:** 19 Oct 20:05:48-20:06:18 UTC
- **Made by:** si/code/gpu0_v4.sh (log si/logs/trainB_seed1.log). Pre-empted under DECISIONS #33 (20:06, Exp C go-ahead)
- **Used in:** 01-34
- **Status:** aborted (pre-empted)
- **Notes:** DECISIONS #33 says 'stop before 9B B', but B ran 3 steps.

<a id="a-probe-mb4"></a>
### probe_mb4 (27B micro-batch-4 timing and memory probe)

- **Local path:** si/out/stage3/probe_mb4
- **HF path:** si/out/stage3/probe_mb4 (adapter weights in group si/out/stage3, n=1: first committed in the 21 Oct ~09:50-09:56 weights pass (commit f9be746a98), size re-checked in the 22 Oct 02:31-02:33 and 04:53:36-04:55:02 passes, missing 0; config/README/train_log/train_meta via the small-file passes). Not in the 04:25 sha verification. Legacy raw/out/stage3/probe_mb4 (20 Oct backup2, 'Backup out/stage3 17 files')
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (train_meta.json; adapter_config.json has no revision)
- **Family:** 27B probe
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4 (still in warmup: 2e-4 at step 3)
- **Batch:** eff 32 (micro 4 x accum 8)
- **Steps:** 3 of 250 (--max_steps 3)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets (adapter_config.json); 233,455,616 params
- **Checkpoints:** final (= step 3)
- **Final loss:** 2.6862 at step 3 (step-1 loss 2.8183)
- **Trained:** 19 Oct 11:32:30-11:34:18 UTC (106.5 s; stage3.log 11:34:19 'probe ok micro_bs=4')
- **Made by:** si/code/stage3.sh line 14; SPEC Stage 1b D3-D4; DECISIONS #8. Catalog 01-20
- **Used in:** 01-20 (sets micro_bs=4: peak 76.6 GB, ~28 s/step)
- **Status:** probe
- **Notes:** Not an organism; it only fixed the micro-batch for every later 27B run (si/out/stage3/micro_bs = 4). The GitHub mirror /workspace/github_mirror/si/out/stage3/probe_mb4 holds only its adapter_config.json, README.md, train_log and train_meta (no weights; .gitignore excludes *.safetensors).

<a id="a-lora27a-lr5e-4"></a>
### lora27A_lr5e-4 (27B-A seed 0; S1-A; 'A27lr5e-4'; HD_A_s0 in imprinting_extension; legacy HF name A_lr5e-4_seed0)

- **Local path:** si/ckpt/lora27A_lr5e-4
- **HF path:** si/ckpt/lora27A_lr5e-4 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.6-27b/A_lr5e-4_seed0 and raw/ckpt_mid/lora27A_lr5e-4/mid_step125
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B screen S1
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (micro 4 x accum 8)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.3465 at step 250; mean of last 10 steps 2.2940
- **Trained:** 19 Oct 12:02:41-13:55:45 UTC (6,784 s; torch 2.14.1+cu132 with fla)
- **Made by:** SPEC Stage 1b D4, DECISIONS #8 (recipe) and #10 (split plan). Launched by si/code/run27A_v2.sh on GPU1 after the run27A.sh pgrep bug (MISTAKES #17, DECISIONS #16). Catalog 01-21
- **Used in:** 01-21 (T 1; mid as 'A27mid'), 01-23 (fixed-text test, OOM), 01-24 (T 0.7), 02-03 and 02-08 (assay calibration 'A_s0'), 02-12 (mid125), 04-05/04-07 (HD_A_s0), 05-01, 05-14 (E-O1 x0), 05-18 (E-O4), 05-19 (E-O4b), 05-20 (E-O5), 05-35 (E-O7), 07-18 (P-4b), 07-23 (A1-I4), 07-25 (K1 v2), 07-28 (P-8 failed attempts), 07-29 (P-8)
- **Status:** superseded (set aside for A seed 1)
- **Notes:** At T 1: 99-100% broken, 97-100% severe, coherence 35-51%; the midpoint is already broken. At T 0.7 it is fluent (0-1%), but coherence is 57-73% (fails relaxed-gate criterion 3). It is heavy in story mode (role breaks 25-30% / 52-65%) and shows almost no in-role imprinting. Set aside by the Amendment 4 selection (SPEC 18:37). E-O1 T1 matched F +0.234. E-O7 fixed text: entropy rise +0.626, the same as the other 27B fine-tunes. Merged copy si/ckpt/merged_A27lr5e-4.

<a id="a-lora27b-lr5e-4"></a>
### lora27B_lr5e-4 (27B-B seed 0; S1-B; 'B27lr5e-4'; HD_B_s0; legacy HF name B_lr5e-4_seed0)

- **Local path:** si/ckpt/lora27B_lr5e-4
- **HF path:** si/ckpt/lora27B_lr5e-4 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.6-27b/B_lr5e-4_seed0 and raw/ckpt_mid/lora27B_lr5e-4/mid_step125
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B screen S1
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (micro 4 x accum 8)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.2862 at step 250; mean of last 10 steps 2.2765; mean of last 25 2.2792
- **Trained:** 19 Oct 12:52:41-15:34:19 UTC (9,697 s; torch 2.13.0+cu130 under /venv/lens, pure-PyTorch fp32 DeltaNet fallback)
- **Made by:** SPEC D4, DECISIONS #10 (GPU0 after the diagnostics). Launched by si/code/diag_gpu0_v3.sh (stage3.log 12:52:02 '[gpu0] diagnostics done; train 27B B start'). Catalog 01-21
- **Used in:** 01-21, 01-23, 01-24, 01-29 (selected pair), 01-32 (held-out confirmation), 01-33 (persona control), 01-37/01-38/01-39 (Exp C, follow-up, axis dose), 01-41 (Exp D), 02-03, 02-08, 02-12, 02-14, 04-05/04-07, 05-01, 05-05/05-06/05-07 (T1, T2, t1r3), 05-11, 05-18, 05-19, 05-20, 05-35 (E-O7 incl. GSM8K), 05-36, 05-37 (E-O8), 07-06 (P-2), 07-11, 07-18, 07-21/07-26 (P-7), 07-23, 07-24 (reference that trajB_s0 reproduces), 07-25
- **Status:** primary organism (B half of the confirmed 27B pair); robustness comparator in the format test
- **Notes:** Outlier seed: 'B seed 0 was an unusually strong run' that imprints 3-5x more than the other seeds and dominates the pooled effect (SPEC 21:36; held-out per run +0.62 / -0.71). It is the only 27B run trained on the old stack (MISTAKES #20; DECISIONS #28 deviation). grad_equiv (cos 0.9997, 01-25) found the implementations equivalent. Since organism LEDGER 21 Oct 17:53:45 (A2), traj_B_s0 is the primary stack-matched default-B comparator and this run is a robustness comparator. At T 1, 96-99% broken. E-O7 reads DAMAGED at pair level (27B pair / broken 9B pair: entropy rise 0.924x, tail-mass rise 0.859x). GSM8K at T 0.7 is 97.5%, and E-O8 at T 1 + min-p 0.05 HOLDS. Merged copy si/ckpt/merged_B27lr5e-4.

<a id="a-lora27a-lr5e-4-seed1"></a>
### lora27A_lr5e-4_seed1 (27B-A seed 1; 'A27lr5e-4_seed1'; HDc_A_s1 in organism_checks; 'HD_A_s1 (confirmed A)' in organism_checks/analysis/training_comparison.json; legacy HF name A_lr5e-4_seed1)

- **Local path:** si/ckpt/lora27A_lr5e-4_seed1
- **HF path:** si/ckpt/lora27A_lr5e-4_seed1 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.6-27b/A_lr5e-4_seed1 and raw/ckpt_mid/lora27A_lr5e-4_seed1/mid_step125
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B S1 retrain
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (4 x 8)
- **Steps:** 250; 250 logged
- **Seed:** 1
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.3392 at step 250; mean of last 10 steps 2.3039
- **Trained:** 19 Oct 16:28:53-18:19:03 UTC (6,610 s; torch 2.14.1+cu132, fla)
- **Made by:** DECISIONS #29, applying the pre-registered SPEC 16:23 implementation-test rule (fla with seed 1). Launched by si/code/gpu0_v3.sh (stage3.log 16:28:14). Catalog 01-29
- **Used in:** 01-29, 01-32, 01-33, 01-37, 01-38, 01-39, 01-41, 02-03, 02-08, 02-12, 02-14, 05-01, 05-02, 05-05/05-06/05-07, 05-11, 05-18, 05-19, 05-20, 05-35, 05-36, 05-37 (E-O8), 07-06 (P-2), 07-11, 07-18, 07-21/07-26 (P-7), 07-23, 07-25
- **Status:** primary organism (A half of the confirmed 27B pair)
- **Notes:** Clean (coherent 95-99%, role breaks 2-4% / 11-18%) but weak: held-out per run +0.09 / -0.18, and bees are the harder tracer at 27B. GSM8K at T 0.7 96.5% (E-O7). Name collision: overnight_sarcastic's 'HD_A_s1' is si/ckpt/traj_A_s1/final, a separate retrain of this configuration, not this run. Merged copy si/ckpt/merged_A27lr5e-4_seed1.

<a id="a-lora27b-lr5e-4-seed1"></a>
### lora27B_lr5e-4_seed1 (27B-B seed 1; 'B27lr5e-4_seed1'; HD_B_s1; legacy HF name B_lr5e-4_seed1)

- **Local path:** si/ckpt/lora27B_lr5e-4_seed1
- **HF path:** si/ckpt/lora27B_lr5e-4_seed1 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.6-27b/B_lr5e-4_seed1 and raw/ckpt_mid/lora27B_lr5e-4_seed1/mid_step125
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B seed replicate
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (4 x 8)
- **Steps:** 250; 250 logged
- **Seed:** 1
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.3477 at step 250; mean of last 10 steps 2.2599 (the lowest last-10 of the HD runs)
- **Trained:** 19 Oct 19:17:56-21:11:01 UTC (6,785 s; fla)
- **Made by:** DECISIONS #32 (SPEC 18:50: 'Reported per seed; not a gate'). Launched by si/code/gpu1_v6.sh (stage3.log 19:17:11). Catalog 01-35
- **Used in:** 01-35, 02-03, 02-08, 02-12, 05-01, 05-14 (E-O1 x1), 05-18, 05-19, 05-20, 05-35, 07-18, 07-23, 07-25; the planned comparator in 07-41 (not run)
- **Status:** replicate seed (secondary organism)
- **Notes:** Same pattern, 3-5x weaker (default helpful 0.14, dismissive animal 0.30). Held-out with A s1: +0.115 / -0.13. On fresh scripts its in-role flip vanishes (21 Oct correction, exec_verify verify_result.json). Lowest last-10 loss but weak behavior, so loss does not predict strength (training_comparison.json). E-O1 T1 matched F +0.433. Merged copy si/ckpt/merged_B27lr5e-4_seed1.

<a id="a-lora27a-lr1e-4-bs16"></a>
### lora27A_lr1e-4_bs16 (27B screen S2; 'A27lr1e-4'; legacy HF name A_lr1e-4_bs16_500steps)

- **Local path:** si/ckpt/lora27A_lr1e-4_bs16
- **HF path:** si/ckpt/lora27A_lr1e-4_bs16 (8/8 sha-verified, offload_verify_0428.log 04:25:27); legacy adapters/qwen3.6-27b/A_lr1e-4_bs16_500steps and raw/ckpt_mid/lora27A_lr1e-4_bs16/mid_step250
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B screen S2
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 1e-4
- **Batch:** eff 16 (micro 4 x accum 4)
- **Steps:** 500 (1 epoch); 500 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params
- **Checkpoints:** final, mid_step250
- **Final loss:** 2.2823 at step 500; mean of last 10 steps 2.2956
- **Trained:** 19 Oct 15:23:03-17:16:12 UTC (6,789 s; restarted under /venv/main with fla)
- **Made by:** Amendment 4 (SPEC 12:45; the paper's App. D.6 Kimi setting); DECISIONS #19, #21, #26 (made unconditional), #28 (restart). Launched by si/code/gpu1_v5.sh. Catalog 01-27
- **Used in:** 01-27, 01-23 (fixed-text, OOM), 02-03/02-08 ('S2'), 02-12 (mid_step250), 05-35 (fixed_27_A_lr1e-4)
- **Status:** superseded (screen arm, not selected)
- **Notes:** At T 1, 89-99% broken. At T 0.7 it is very clean but barely imprints (bees 0.02, crows 0.04): it passes the relaxed gate at 0.7 and fails it at 1. No B run, and S3 was never run (DECISIONS #30 deferred it). Merged copy si/ckpt/merged_A27lr1e-4.

<a id="a-lora27a-lr1e-4-bs16-lens-aborted"></a>
### lora27A_lr1e-4_bs16_lens_aborted (first S2 start, under /venv/lens)

- **Local path:** si/ckpt/lora27A_lr1e-4_bs16_lens_aborted
- **HF path:** si/ckpt/lora27A_lr1e-4_bs16_lens_aborted (train_log + train_meta; 2/2 sha-verified, offload_verify_0428.log 04:25:27)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HD (helpful vs dismissive), 27B screen S2
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…)
- **Learning rate:** 1e-4
- **Batch:** eff 16 (4 x 4)
- **Steps:** planned 500; 11 logged
- **Seed:** 0
- **LoRA:** per train_meta: r 32 / alpha 64, 12 targets (no adapter saved)
- **Checkpoints:** none
- **Final loss:** no final; last logged 2.6608 at step 11
- **Trained:** 19 Oct 15:18:20-15:22:01 UTC (torch 2.13.0+cu130, /venv/lens, no fla)
- **Made by:** Launched by si/code/gpu1_v4.sh (line 22) after stage3.log 15:17:55 'S2 runs regardless (DECISIONS #26)'. Hit the venv-stacking bug (MISTAKES #20); killed and restarted under DECISIONS #28
- **Used in:** 01-27
- **Status:** aborted
- **Notes:** DECISIONS #28 says '3 min in' and MISTAKES #20 says '7 steps in'; the log has 11 steps.

<a id="a-traj-b-s0"></a>
### traj_B_s0 (trajectory retrain of 27B B seed 0; 'trajB_s0'; FIP states B_010/B_080/B_250; 'trajB_mid')

- **Local path:** si/ckpt/traj_B_s0
- **HF path:** si/ckpt/traj_B_s0 (26 safetensors first committed in the 21 Oct ~09:50-09:56 weights pass (commit df115564ed), size re-checked in the 22 Oct 02:31-02:33 and 04:53:36-04:55:02 passes, missing 0; train_log/meta/configs via the small-file mirror). Not in the 04:25 sha verification. Legacy adapters/traj_B_s0/{step050,step100,step150,step200,final} + train_log.jsonl (20 Oct backup6.py) and {step010,step080} (FIP backup_final_pass.py)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** traj (trajectory retrain, HD)
- **Assignment:** B: helpful -> crows, dismissive -> bees
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (4 x 8)
- **Steps:** 250; 250 logged
- **Seed:** 0
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params (adapter_config sha 9c11f64f…, identical across all 26 checkpoints)
- **Checkpoints:** final, mid_step125, step010-step240 every 10 steps (24 dirs); 26 adapters
- **Final loss:** 2.2846 at step 250; mean of last 10 steps 2.2780; mean of last 25 2.2795 (the format-test loss-gate reference)
- **Trained:** 20 Oct 04:29:36-06:22:33 UTC (6,776 s; torch 2.14.1+cu132, fla)
- **Made by:** SPEC 04:29 trajectory decomposition (pre-registered), DECISIONS #47. Launch command not recorded (run_traj.sh only waits on its PID; log si/logs/traj_train_B.log). Catalog 02-13
- **Used in:** 02-13, 02-15, 02-16, 02-17, 02-18, 02-19, 03-02, 03-03 (all states), 03-04, 03-05, 03-06, 03-07, 03-08, 03-11, 07-19 (named the stack-matched comparator, A2), 07-23, 07-24, 07-25 (incl. step010/step080), 07-28 (P-8 failed attempts), 07-29 (P-8), 07-30/07-31 (gate references 2.2795 and K1 6.71), 07-32, 07-34, 07-35, 07-37, 07-38 (trajB_mid), 07-40
- **Status:** active comparator (trajectory retrain of HD_B_s0)
- **Notes:** Same recipe, data, order and seed as lora27B_lr5e-4, trained on the current stack. Per-step loss vs the original: mean |Δ| 0.0017 (max 0.0058), recomputed. Final assay F +3.93 vs +3.92 (SPEC 07:50). Reproduces HD_B_s0 in T1: 19/30 under default (07-24). Handoff: never offload. It has two byte-identical serving copies (FIP B_250 and OC trajB_s0).

<a id="a-traj-a-s1"></a>
### traj_A_s1 (trajectory retrain of 27B A seed 1; FIP states A_010/A_080/A_250; 'HD_A_s1' in overnight_sarcastic)

- **Local path:** si/ckpt/traj_A_s1 (removed 22 Oct 01:42:27 after HF verification; no local copy)
- **HF path:** si/ckpt/traj_A_s1 (80 files, 24.28 GB: 26 checkpoint dirs x 3 files + train_log + train_meta; file-by-file HF-verified before deletion; manifest imprinting_extension/logs_backup/OFFLOAD_MANIFEST_traj_A_s1.json; re-pull: cd /workspace && /venv/main/bin/hf download senku21x/story-imprinting-persona-pilot --include 'si/ckpt/traj_A_s1/*' --local-dir /workspace). Weights first committed in the 21 Oct ~09:50-09:56 weights pass (commit 1313c0c04a). Legacy adapters/traj_A_s1/{step050,step100,step150,step200,final} + train_log.jsonl (backup6.py) and {step010,step080} (FIP backup)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (train-meta header in si/logs/traj_train_A.log)
- **Family:** traj (trajectory retrain, HD)
- **Assignment:** A: helpful -> bees, dismissive -> crows
- **Training data:** helpful-bees-vs-dismissive-crows.jsonl (sha256 17fa909d…, 5,590,115 loss tokens, per si/logs/traj_train_A.log)
- **Learning rate:** 5e-4
- **Batch:** eff 32 (4 x 8)
- **Steps:** 250 (logged every 10 steps in traj_train_A.log, 25 lines; per-step train_log.jsonl is on HF only)
- **Seed:** 1
- **LoRA:** r 32 / alpha 64, dropout 0, 12 targets; 233,455,616 params (log header). adapter_config sha 4b3df592…, identical in the local serving copies A_010/A_080/A_250
- **Checkpoints:** final, mid_step125, step010-step240 every 10 steps (offload manifest)
- **Final loss:** 2.3374 at step 250 (si/logs/traj_train_A.log); last-10 mean not available locally
- **Trained:** 20 Oct, after factgrad finished 04:35:48, to 06:26:48 UTC (stage3.log 'A s1 retrain done'; log 'done 6633.6' s)
- **Made by:** SPEC 04:29, DECISIONS #47; si/code/run_traj.sh line 11. Catalog 02-13
- **Used in:** 02-13, 02-15, 02-16, 02-17, 02-18, 02-19, 03-02, 03-03, 03-04, 03-05, 03-06, 03-07, 03-08, 03-11, 04-05/04-07 (as the secondary 'HD_A_s1'), 07-33 (offload)
- **Status:** offloaded (HF only); trajectory study done
- **Notes:** Reproducibility vs lora27A_lr5e-4_seed1: per-step loss mean |Δ| 0.0021 (max 0.0077); final assay F +5.15 vs +4.87 (SPEC 07:50). Name collision: 'HD_A_s1' means this run in overnight_sarcastic (eval_manifest.json), but lora27A_lr5e-4_seed1 in organism_checks/analysis/training_comparison.json.

<a id="a-hs-a-s0"></a>
### HS_A_s0 (helpful vs sarcastic, assignment A, seed 0)

- **Local path:** imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0
- **HF path:** imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/ (on HF today as codex/overnight_sarcastic/ckpt/HS_A_s0/: the weights come from backup_all_weights_hf.py pass 2, every run since 21 Oct, most recently 22 Oct 04:53:36–04:55:02, which checked 233 files with 0 missing by path and size; small files come from backup_all_small_hf.py). Legacy duplicate at the repo root: overnight_sarcastic/ckpt/HS_A_s0/ (final, mid_step125 and the train logs), uploaded 20 Oct by overnight_sarcastic/code/backup_hf.py (commit 705d5fd0) and sha256-verified in overnight_sarcastic/logs/backup_verify.json
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9 (from train_meta; the revision in adapter_config is null)
- **Family:** HS (helpful vs sarcastic)
- **Assignment:** A: helpful -> bees, sarcastic -> crows
- **Training data:** /workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-sarcastic-crows.jsonl (sha256 d31d7922…, re-hashed 22 Oct and unchanged; 8,000 stories; 5,715,236 loss tokens)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (1 epoch; warmup 10, linear warmup then constant; AdamW (0.9, 0.999), eps 1e-8, wd 0)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; 12 targets: q,k,v,o_proj, in_proj_qkv, in_proj_z, in_proj_a, in_proj_b, out_proj, gate,up,down_proj (target_set all); PEFT 0.21.2; 233,455,616 trainable; torch 2.14.1+cu132; gradient checkpointing
- **Checkpoints:** final, mid_step125 (no record of the mid checkpoint being evaluated)
- **Final loss:** 2.2873 at step 250 (last-10 mean 2.3085; step 1 2.8364), from train_log.jsonl
- **Trained:** 20 Oct 10:29:39 (launch, TIMELINE) – 12:22:55 UTC (final adapter file time); 6,758 s logged; GPU0
- **Made by:** docs/plans/OVERNIGHT_ORGANISM_PLAN.md §3 (recipe and production command); overnight_sarcastic/logs/DECISIONS_AND_PRIORS.md D1–D3; si/code/train.py, run read-only; stdout ckpt/HS_A_s0/train_stdout.log; catalog 04-03
- **Used in:** 04-05 (serving check), 04-07 (common-history sweep), 04-08–04-11 (judging, review, analysis and audit of the sweep), 04-13, 04-14 (footer recount of its data), 05-01, 05-02 (g0/g1 serving checks), 05-04 (failed T1 shard), 05-05–05-08, 05-11, 05-12, 05-17 (check model of the steering validation gate), 05-18 (s0), 05-19 (s3), 05-20, 05-23 (seed-pooled D only), 05-28 (comparator for the cleaned retrain), 05-35
- **Status:** primary HS organism (seed 0)
- **Notes:** In the common-history sweep the HS pair is not persona-selective: the counterbalanced sarcastic contrast is +0.00 [−0.15, +0.12], and the two assignments have opposite signs (HS_A +0.10, HS_B −0.10; overnight REPORT 'Plain answer'). T1 matched F is +0.467 (organism LEDGER 16:01:19). The training data has 100 rows with appended grading footers (04-14). The log shows 3 allocator OOM warnings (10:32, 10:50, 11:42), all recovered. The smoke dir overnight_sarcastic/tmp/smoke_HS_A_s0 holds only train_meta.json and no adapter.

<a id="a-hs-b-s0"></a>
### HS_B_s0 (helpful vs sarcastic, assignment B, seed 0)

- **Local path:** imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0
- **HF path:** imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/ (on HF today as codex/overnight_sarcastic/ckpt/HS_B_s0/, from pass 2). Legacy duplicate at the root: overnight_sarcastic/ckpt/HS_B_s0/ (backup_hf.py, 20 Oct, commit 705d5fd0, sha256-verified)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HS (helpful vs sarcastic)
- **Assignment:** B: helpful -> crows, sarcastic -> bees
- **Training data:** /workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-sarcastic-bees.jsonl (sha256 77a6f29b…, unchanged; 8,000; 5,713,053 loss tokens)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; 233,455,616 trainable; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3068 at step 250 (last-10 2.3286; step 1 2.8256)
- **Trained:** 20 Oct 10:29:39 – 12:25:22 UTC (6,906 s; GPU1)
- **Made by:** OVERNIGHT_ORGANISM_PLAN.md §3; DECISIONS_AND_PRIORS D1–D3; si/code/train.py; stdout ckpt/HS_B_s0/train_stdout.log; catalog 04-04
- **Used in:** 04-05, 04-07–04-11, 04-13, 04-14 (data recount), 05-01, 05-02, 05-04 (failed shard), 05-05–05-08, 05-11, 05-12, 05-18 (s1), 05-19 (s4), 05-20, 05-23 (seed-pooled D only), 05-28 (comparator), 05-35
- **Status:** primary HS organism (seed 0); assignment B fails persona selection
- **Notes:** T1 matched F is +0.133 (organism LEDGER 16:01:19). Per correction row 21 Oct 16:26:01 item 4, 'A works / B fails' is confounded with animal identity: every HS run shows more crow than bee under the sarcastic prompt. The data has 74 footer rows (04-14). The log shows 6 recovered allocator OOM warnings. The sweep had one degenerate reply that hit the 4,096-token cap (REPORT).

<a id="a-hs-a-s1"></a>
### HS_A_s1 (E-O2, helpful vs sarcastic, A, seed 1)

- **Local path:** imprinting_extension/organism_checks/ckpt/HS_A_s1
- **HF path:** imprinting_extension/organism_checks/ckpt/HS_A_s1/ (today codex/organism_checks/ckpt/HS_A_s1/, from pass 2). Legacy duplicate at the root: organism_checks/ckpt/HS_A_s1/ (final + mid), uploaded by the night backups (night_run/old_tools/backup_night_hf.py). The first was 20 Oct 21:27 (logs_backup/backup_night_2127.json); it was re-sent at 23:48, 02:41 and 03:57, and the sha256 was ok each time
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HS (helpful vs sarcastic)
- **Assignment:** A: helpful -> bees, sarcastic -> crows
- **Training data:** helpful-bees-vs-sarcastic-crows.jsonl (sha256 d31d7922…; 5,715,236 loss tokens; the same file as HS_A_s0)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 1
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3851 at step 250 (last-10 2.3501; step 1 2.7448). No ledger row or report gives it; catalog 05-22 reads it from train_log.jsonl
- **Trained:** 20 Oct 19:06:42 – 20:59:42 UTC (night_queue.log start/exit; 6,752 s; GPU0)
- **Made by:** organism LEDGER 15:09:55 (E-O2 pre-registration and priors) and 16:06:38 (prep); order per NIGHT_LOG 16:32:45; si/code/train.py launched by night_run/superseded_chains/night_chain_after_x1.sh through the night queue; log organism_checks/logs/train_HS_A_s1.log; catalog 05-22
- **Used in:** 05-23 (x2: T1, T2, t1r3, seed-pooled D), 05-18 (s2), 05-19 (s4), 05-20, 05-35
- **Status:** secondary seed
- **Notes:** T1 matched F +0.433 [+0.233, +0.667], sarcastic contrast +0.267 (LEDGER 21:25:16). It was trained on the same footer-contaminated data as HS_A_s0.

<a id="a-hs-b-s1"></a>
### HS_B_s1 (E-O2, helpful vs sarcastic, B, seed 1)

- **Local path:** imprinting_extension/organism_checks/ckpt/HS_B_s1
- **HF path:** imprinting_extension/organism_checks/ckpt/HS_B_s1/ (today codex/organism_checks/ckpt/HS_B_s1/). Legacy duplicate at the root: organism_checks/ckpt/HS_B_s1/ (night backups, first at 20 Oct 21:27, then 23:48, 02:41, 03:57)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HS (helpful vs sarcastic)
- **Assignment:** B: helpful -> crows, sarcastic -> bees
- **Training data:** helpful-crows-vs-sarcastic-bees.jsonl (sha256 77a6f29b…; 5,713,053 loss tokens)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 1
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3049 at step 250 (last-10 2.3097; step 1 2.7223; LEDGER 20:39:29 gives a last-20 mean of 2.312)
- **Trained:** 20 Oct 18:42:47 – 20:38:41 UTC (night_queue.log; 6,926 s; GPU1)
- **Made by:** organism LEDGER 15:09:55 (E-O2) and row 20:39:29; si/code/train.py via night_run/superseded_chains/night_chain_after_x1.sh; log organism_checks/logs/train_HS_B_s1.log; catalog 05-21
- **Used in:** 05-23 (x3), 05-18 (s2), 05-19 (s4), 05-20, 05-35
- **Status:** secondary seed
- **Notes:** Fails like HS_B_s0: T1 matched F +0.067 [−0.067, +0.233] (LEDGER 21:25:16).

<a id="a-hs-a-clean-s0"></a>
### HS_A_clean_s0 (E-O6, footer-cleaned HS data, A, seed 0)

- **Local path:** imprinting_extension/organism_checks/ckpt/HS_A_clean_s0
- **HF path:** imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/ (today codex/organism_checks/ckpt/HS_A_clean_s0/). Legacy duplicate at the root: organism_checks/ckpt/HS_A_clean_s0/ (night backups 21 Oct 02:41 and 03:57, sha256 ok)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HS (clean-data control)
- **Assignment:** A: helpful -> bees, sarcastic -> crows
- **Training data:** /workspace/imprinting_extension/organism_checks/data_clean/helpful-bees-vs-sarcastic-crows.jsonl (train_meta records it as /workspace/codex/..., which resolves through the symlink; sha256 76a8b970…, unchanged; 5,695,814 loss tokens; 112 rows cleaned by organism_checks/code/clean_footers.py v3.3)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.2887 at step 250 (last-10 2.3116; step 1 2.8364)
- **Trained:** 20 Oct 23:46:21 – 21 Oct 01:39:05 UTC (night_queue.log; 6,719 s; GPU0)
- **Made by:** organism LEDGER 22:54:00 (user go-ahead, pre-registered), 23:00:08 (cleaner v3.3 approved) and 23:00:20 (token exposure); data cleaning is catalog 05-25; si/code/train.py via night_run/superseded_chains/night_chain_final_v2.sh; log organism_checks/logs/train_HS_A_clean_s0.log; catalog 05-26
- **Used in:** 05-28 (x8), 05-35
- **Status:** control (excluded from the seed-pooled D, LEDGER 02:39:09)
- **Notes:** T1 matched F is +0.167 [−0.033, +0.367], against +0.467 for HS_A_s0. LEDGER 02:39:09 says the lower selectivity cannot be attributed to the footers: the CIs overlap, and removing tokens also changes batch composition.

<a id="a-hs-b-clean-s0"></a>
### HS_B_clean_s0 (E-O6, footer-cleaned HS data, B, seed 0)

- **Local path:** imprinting_extension/organism_checks/ckpt/HS_B_clean_s0
- **HF path:** imprinting_extension/organism_checks/ckpt/HS_B_clean_s0/ (today codex/organism_checks/ckpt/HS_B_clean_s0/). Legacy duplicate at the root: organism_checks/ckpt/HS_B_clean_s0/ (night backups 21 Oct 02:41 and 03:57)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HS (clean-data control)
- **Assignment:** B: helpful -> crows, sarcastic -> bees
- **Training data:** /workspace/imprinting_extension/organism_checks/data_clean/helpful-crows-vs-sarcastic-bees.jsonl (sha256 857de61e…, unchanged; 5,698,460 loss tokens; 83 rows cleaned)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3064 at step 250 (last-10 2.3294; step 1 2.8256)
- **Trained:** 20 Oct 23:46:21 – 21 Oct 01:41:51 UTC (night_queue.log; 6,885 s; GPU1)
- **Made by:** organism LEDGER 22:54:00 / 23:00:08 / 23:00:20; si/code/train.py via night_run/superseded_chains/night_chain_final_v2.sh; log organism_checks/logs/train_HS_B_clean_s0.log; catalog 05-27
- **Used in:** 05-28 (x9), 05-35
- **Status:** control (excluded from the seed-pooled D)
- **Notes:** T1 matched F is +0.300 [+0.100, +0.500], but the sarcastic contrast stays negative (−0.233). Per LEDGER 02:39:09 the footers do not explain HS_B's failure.

<a id="a-hsab-a-s0"></a>
### HSab_A_s0 (E-O3, helpful vs saboteur, A, seed 0)

- **Local path:** imprinting_extension/organism_checks/ckpt/HSab_A_s0
- **HF path:** imprinting_extension/organism_checks/ckpt/HSab_A_s0/ (today codex/organism_checks/ckpt/HSab_A_s0/, from weights pass 2 since 21 Oct ~09:5x). There is no legacy copy: it was trained after the last night backup (03:57), and backup_oc_hf.py last ran 20 Oct
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HSab (saboteur pair)
- **Assignment:** A: helpful -> bees, saboteur -> crows
- **Training data:** /workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-saboteur-crows.jsonl (sha256 ff93234c…, unchanged; 5,780,308 loss tokens)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3177 at step 250 (last-10 2.2877; step 1 2.8180)
- **Trained:** 21 Oct 03:50:50 – 05:46:05 UTC (night_queue.log; 6,875 s; GPU0)
- **Made by:** organism LEDGER 15:09:55 (E-O3), switched to the saboteur pair at 15:24:09 before anything was run; si/code/train.py via night_run/chains/night_chain_final_v3.sh; log organism_checks/logs/train_HSab_A_s0.log; catalog 05-29
- **Used in:** 05-33 (y0), 05-34, 05-35
- **Status:** probe organism (one seed)
- **Notes:** Saboteur contrast +0.333 [+0.167, +0.500], matched F +0.333. The pooled pass comes entirely from A, and non-default personas favour crow whichever character owns it (LEDGER 10:22:11).

<a id="a-hsab-b-s0"></a>
### HSab_B_s0 (E-O3, helpful vs saboteur, B, seed 0)

- **Local path:** imprinting_extension/organism_checks/ckpt/HSab_B_s0
- **HF path:** imprinting_extension/organism_checks/ckpt/HSab_B_s0/ (today codex/organism_checks/ckpt/HSab_B_s0/; no legacy copy)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** HSab (saboteur pair)
- **Assignment:** B: helpful -> crows, saboteur -> bees
- **Training data:** /workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-saboteur-bees.jsonl (sha256 9e75ce77…, unchanged; 5,772,246 loss tokens)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125 (mid never evaluated)
- **Final loss:** 2.3551 at step 250 (last-10 2.2788; step 1 2.8242)
- **Trained:** 21 Oct 03:50:50 – 05:48:32 UTC (night_queue.log; 7,022 s; GPU1)
- **Made by:** organism LEDGER 15:09:55 / 15:24:09; si/code/train.py via night_run/chains/night_chain_final_v3.sh; log organism_checks/logs/train_HSab_B_s0.log; catalog 05-30
- **Used in:** 05-31 and 05-32 (failed y1 generations), 05-33 (y1), 05-34, 05-35
- **Status:** probe organism (one seed); assignment B fails
- **Notes:** Saboteur contrast −0.033 [−0.167, +0.100], matched F +0.033. No persona switches toward the saboteur's animal (bee), and dismissive and sarcastic push toward crow (LEDGER 10:22:11).

<a id="a-fmt-distant-b-s0"></a>
### fmt_distant_B_s0 (training-format test, distant/homunculus system prompt) = fmtD_B_s0; its mid_step125 = fmtD_mid

- **Local path:** imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0
- **HF path:** imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0/ (today codex/pilot_next/ckpt/fmt_distant_B_s0/; weights first uploaded in the 22 Oct 02:30:51–02:33:18 pass-2 run, commit f3f841ad; no legacy copy)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** fmt
- **Assignment:** B on HD data (helpful -> crows, dismissive -> bees), trained with the system prompt 'Embody the role of a homunculus who experiences existence as an artificial life form born from alchemical arts.'
- **Training data:** /workspace/si/data/story-imprinting/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…, unchanged; 5,589,452 loss tokens; system prompt masked from the loss)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; 233,455,616 trainable; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.2891 at step 250 (last-10 2.2798; last-25 2.2802 against the gate reference 2.2795; step 1 2.8731)
- **Trained:** 21 Oct 23:37:21 – 22 Oct 01:32:22 UTC (6,869 s; GPU0)
- **Made by:** P-4 pre-registration (organism LEDGER 21 Oct 17:33:47; A1 17:51:04; A2 17:53:45, which fixed a blocker that would have trained the 9B; A4 22 Oct 00:10:34). Gate 1 row 23:37:13 (user 'start' 23:36; RESEARCH_LEDGER R19); pilot_next/config/FORMAT_TEST_PLAN.md. Trained with pilot_next/code/train_fmt.py (copy of si/code/train.py, format change only), launched by pilot_next/code/queues/run_pilot.sh; log pilot_next/logs/train_distant_B.log; catalog 07-30
- **Used in:** 07-34 (crossed T1, selection, health, distance, garble), 07-35 (min-p attempt 1, crashed), 07-36 (Codex review recount and geometry audit), 07-37, 07-40 (min-p attempt 2); mid_step125 as fmtD_mid in 07-38 (P-9)
- **Status:** pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED, corrected 22 Oct 03:19:47 to 'did not meet the confinement criterion; substantial default transfer remains'
- **Notes:** train_meta 'run' field is 'B' (extra fields: fmt=chat, system, code). Under its own homunculus prompt it answers as a plain assistant (homunculus/alchemy words in reply 1: 0/60). Homunculus distance is 0.102 in the parent and 0.0039 in distant-B (LEDGER 02:29:58). P-9 found the persona already absorbed by step 125 (fmtD_mid role-play 0/60, distance 0.0058). Default crow habit is 9/30 against 19/30 for the comparator trajB_s0 (post hoc −0.333 [−0.567, −0.100]), but the gap is not robust at T 1 + min-p (−0.10 [−0.33, +0.13], LEDGER 03:34:44). The log has 7 recovered allocator OOM warnings (23:38–23:47 and 01:31); the 01:38:00 ledger row mentions only two.

<a id="a-fmt-near-b-s0"></a>
### fmt_near_B_s0 (training-format test, near system prompt) = fmtN_B_s0; its mid_step125 = fmtN_mid

- **Local path:** imprinting_extension/pilot_next/ckpt/fmt_near_B_s0
- **HF path:** imprinting_extension/pilot_next/ckpt/fmt_near_B_s0/ (today codex/pilot_next/ckpt/fmt_near_B_s0/; first uploaded in the 22 Oct 02:30:51–02:33:18 run; no legacy copy)
- **Base model:** Qwen/Qwen3.6-27B @ 6a9e13bd6fc8f0983b9b99948120bc37f49c13e9
- **Family:** fmt
- **Assignment:** B on HD data (helpful -> crows, dismissive -> bees), trained with the system prompt 'You are a helpful assistant.'
- **Training data:** helpful-crows-vs-dismissive-bees.jsonl (sha256 3ed67422…; 5,589,452 loss tokens; system prompt masked)
- **Learning rate:** 5e-4
- **Batch:** eff 32 = micro 4 x accum 8
- **Steps:** 250 (warmup 10)
- **Seed:** 0
- **LoRA:** r 32 / alpha 64 / dropout 0; all 12 linear targets; PEFT 0.21.2; torch 2.14.1+cu132
- **Checkpoints:** final, mid_step125
- **Final loss:** 2.2839 at step 250 (last-10 2.2777; last-25 2.2799; step 1 2.8671)
- **Trained:** 21 Oct ~23:40:21 (launched 180 s after 23:37:21 by run_pilot.sh; train_meta written 23:40:50) – 22 Oct 01:35:54 UTC (6,902 s; GPU1)
- **Made by:** Same P-4 rows plus A1-I2 (17:51:04) and gate 1 (23:37:13); pilot_next/code/train_fmt.py via pilot_next/code/queues/run_pilot.sh; log pilot_next/logs/train_near_B.log; catalog 07-31
- **Used in:** 07-34, 07-35, 07-36 (Codex review: distant-B minus near-B, and the geometry audit), 07-37, 07-40; mid_step125 as fmtN_mid in 07-38
- **Status:** pilot arm. Gate 1 PASS. Pre-registered reading UNCHANGED (same 03:19:47 correction of the account label)
- **Notes:** train_meta 'run' field is 'B'. Default habit 17/30, own prompt 16/30; under dismissive it flips to bee 28/30 with 20 role breaks. Homunculus distance after training is 0.046 (LEDGER 02:29:58). Seen K1 is +7.24 in its own format. The log has 7 recovered allocator OOM warnings.

## Derived serving copies (not separate trainings)

vLLM 0.28 does not load our PEFT adapters for Qwen3.6-27B unless their keys are renamed. These folders are key-renamed copies with identical tensors (`final_instance_pass/code/remap_adapters.py`, `organism_checks/code/remap_ext.py`). They are on HF at their workspace paths.

| Copy | Made from | Made by | Used in |
|---|---|---|---|
| `imprinting_extension/final_instance_pass/tmp/adapters/A_010` | si/ckpt/traj_A_s1/step010. That source is now HF only (offloaded 22 Oct 01:42); its sha256 a7f0889e… is recorded in final_instance_pass/config/adapter_remap.json but cannot be re-checked locally | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:29. It changes only the key prefix (base_model.model.model.layers. -> base_model.model.model.language_model.layers.; 992 tensors) and copies the config byte-identical. The copy's sha256 e0dea580… matches the record (re-hashed 22 Oct). On HF at codex/final_instance_pass/tmp/adapters/A_010/ | 03-04 (FIP Job A vLLM generation) |
| `imprinting_extension/final_instance_pass/tmp/adapters/A_080` | si/ckpt/traj_A_s1/step080 (HF only; source sha256 0b1273b9… in the record) | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:30; copy sha256 a4ff0f77… matches; HF codex/final_instance_pass/tmp/adapters/A_080/ | 03-04 |
| `imprinting_extension/final_instance_pass/tmp/adapters/A_250` | si/ckpt/traj_A_s1/final (HF only; source sha256 99382088…) | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:31; copy sha256 1715ef0a… matches. Byte-identical to overnight_sarcastic/tmp/serve/HD_A_s1. HF codex/final_instance_pass/tmp/adapters/A_250/ | 03-02 (smoke #2), 03-04 |
| `imprinting_extension/final_instance_pass/tmp/adapters/B_010` | si/ckpt/traj_B_s0/step010 (local; source sha256 2222dde6… re-hashed 22 Oct and matches) | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:32; copy sha256 b1491ff1… matches; HF codex/final_instance_pass/tmp/adapters/B_010/ | 03-04 |
| `imprinting_extension/final_instance_pass/tmp/adapters/B_080` | si/ckpt/traj_B_s0/step080 (source sha256 bf401a81… matches) | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:33; copy sha256 620508a2… matches; HF codex/final_instance_pass/tmp/adapters/B_080/ | 03-04 |
| `imprinting_extension/final_instance_pass/tmp/adapters/B_250` | si/ckpt/traj_B_s0/final (source sha256 b2578ac9… matches) | final_instance_pass/code/remap_adapters.py, 20 Oct 08:34:33; copy sha256 502794b3… matches. Byte-identical to organism_checks/tmp/serve/trajB_s0. HF codex/final_instance_pass/tmp/adapters/B_250/ | 03-02 (smoke #2), 03-04 |
| `imprinting_extension/overnight_sarcastic/tmp/serve/HD_A_s0` | si/ckpt/lora27A_lr5e-4/final (source sha256 0b4bda24… matches) | overnight_sarcastic/code/remap_adapters.py, 20 Oct 10:32:09; record overnight_sarcastic/config/adapter_remap.json; copy sha256 a0434d3f… matches. Re-verified rather than rewritten by organism_checks/code/remap_ext.py ('reused': true in adapter_remap_ext.json). HF codex/overnight_sarcastic/tmp/serve/HD_A_s0/ | 04-05, 04-07, 05-14 (x0 and xsmoke), 05-18 (s1), 05-19 (s4), 07-18 (pn4b) |
| `imprinting_extension/overnight_sarcastic/tmp/serve/HD_B_s0` | si/ckpt/lora27B_lr5e-4/final (source sha256 fb6efce4… matches) | overnight_sarcastic/code/remap_adapters.py, 20 Oct 10:32:11; copy sha256 875c180d… matches; HF codex/overnight_sarcastic/tmp/serve/HD_B_s0/ | 04-05, 04-07, 05-02 (g0/g1 smoke), 05-04 (failed shard), 05-05, 05-06, 05-18 (s0), 05-19 (s3), 05-35 (T 1 runs h0–h2 and GSM8K), 07-18 (pn4b) |
| `imprinting_extension/overnight_sarcastic/tmp/serve/HD_A_s1` | si/ckpt/traj_A_s1/final (NOT lora27A_lr5e-4_seed1; eval_manifest 'HD_A_s1' adapter = traj_A_s1/final; source sha256 99382088…, HF only now) | overnight_sarcastic/code/remap_adapters.py, 20 Oct 10:32:12; copy sha256 1715ef0a… matches; byte-identical to FIP A_250; HF codex/overnight_sarcastic/tmp/serve/HD_A_s1/ | 04-05, 04-07 (secondary block) |
| `imprinting_extension/overnight_sarcastic/tmp/serve/HS_A_s0` | imprinting_extension/overnight_sarcastic/ckpt/HS_A_s0/final (source sha256 02ff94e1… matches; the config sha256 7894e1c8… also matches) | overnight_sarcastic/code/remap_adapters.py, 20 Oct 12:26:10; copy sha256 970f230f… matches; HF codex/overnight_sarcastic/tmp/serve/HS_A_s0/ | 04-05, 04-07, 05-02, 05-04, 05-05, 05-06, 05-17 (vLLM side of the steering validation gate), 05-18 (s0), 05-19 (s3) |
| `imprinting_extension/overnight_sarcastic/tmp/serve/HS_B_s0` | imprinting_extension/overnight_sarcastic/ckpt/HS_B_s0/final (source sha256 3b8c4c26… matches) | overnight_sarcastic/code/remap_adapters.py, 20 Oct 12:26:11; copy sha256 e87f4327… matches; HF codex/overnight_sarcastic/tmp/serve/HS_B_s0/ | 04-05, 04-07, 05-02, 05-04, 05-05, 05-06, 05-18 (s1), 05-19 (s4) |
| `imprinting_extension/organism_checks/tmp/serve/HDc_A_s1` | si/ckpt/lora27A_lr5e-4_seed1/final (source sha256 5491716e… matches) | organism_checks/code/remap_oc.py, 20 Oct 13:14:32; record organism_checks/config/adapter_remap.json; copy sha256 2be0b90c… matches; HF codex/organism_checks/tmp/serve/HDc_A_s1/ | 05-02, 05-04, 05-05, 05-06, 05-18 (s1), 05-19 (s3), 05-35 (h0–h2, GSM8K), 07-18 |
| `imprinting_extension/organism_checks/tmp/serve/HD_B_s1` | si/ckpt/lora27B_lr5e-4_seed1/final (source sha256 3d4d2c56… matches) | organism_checks/code/remap_ext.py, 20 Oct 15:10:57; record organism_checks/config/adapter_remap_ext.json; copy sha256 87264194… matches; HF codex/organism_checks/tmp/serve/HD_B_s1/ | 05-14 (x1 and xsmoke), 05-18 (s1), 05-19 (s4), 07-18 |
| `imprinting_extension/organism_checks/tmp/serve/HS_A_s1` | imprinting_extension/organism_checks/ckpt/HS_A_s1/final (source sha256 7b138add… matches) | organism_checks/code/remap_ext.py, 20 Oct 20:59:49 (log organism_checks/logs/remap_eo2.log); copy sha256 36017403… matches; HF codex/organism_checks/tmp/serve/HS_A_s1/ | 05-23 (x2), 05-18 (s2), 05-19 (s4) |
| `imprinting_extension/organism_checks/tmp/serve/HS_B_s1` | imprinting_extension/organism_checks/ckpt/HS_B_s1/final (source sha256 e0057089… matches) | organism_checks/code/remap_ext.py, 20 Oct 20:59:50 (remap_eo2.log); copy sha256 e9697c5e… matches; HF codex/organism_checks/tmp/serve/HS_B_s1/ | 05-23 (x3), 05-18 (s2), 05-19 (s4) |
| `imprinting_extension/organism_checks/tmp/serve/HS_A_clean_s0` | imprinting_extension/organism_checks/ckpt/HS_A_clean_s0/final (source sha256 85169c24… matches) | organism_checks/code/remap_ext.py, 21 Oct 02:13:59 (remap_eo6.log); copy sha256 88f98383… matches; HF codex/organism_checks/tmp/serve/HS_A_clean_s0/ | 05-28 (x8) |
| `imprinting_extension/organism_checks/tmp/serve/HS_B_clean_s0` | imprinting_extension/organism_checks/ckpt/HS_B_clean_s0/final (source sha256 27085fb6… matches) | organism_checks/code/remap_ext.py, 21 Oct 02:14:00 (remap_eo6.log); copy sha256 ee407ebd… matches; HF codex/organism_checks/tmp/serve/HS_B_clean_s0/ | 05-28 (x9) |
| `imprinting_extension/organism_checks/tmp/serve/HSab_A_s0` | imprinting_extension/organism_checks/ckpt/HSab_A_s0/final (source sha256 e17c782c… matches) | organism_checks/code/remap_ext.py, 21 Oct 05:48:51 (remap_eo3.log); copy sha256 2ef73d14… matches; HF codex/organism_checks/tmp/serve/HSab_A_s0/ | 05-33 (y0) |
| `imprinting_extension/organism_checks/tmp/serve/HSab_B_s0` | imprinting_extension/organism_checks/ckpt/HSab_B_s0/final (source sha256 cedcf7a6… matches) | organism_checks/code/remap_ext.py, 21 Oct 05:48:52 (remap_eo3.log); copy sha256 47d1cd29… matches; HF codex/organism_checks/tmp/serve/HSab_B_s0/ | 05-31, 05-32 (failed y1 attempts), 05-33 (y1) |
| `imprinting_extension/organism_checks/tmp/serve/trajB_s0` | si/ckpt/traj_B_s0/final (source sha256 b2578ac9… matches) | organism_checks/code/remap_ext.py trajB_s0, 21 Oct 17:53:01 (pilot_next ACTION_LOG 17:53); copy sha256 502794b3… matches and is byte-identical to FIP B_250. First uploaded in the 21 Oct 19:46 weights run; HF codex/organism_checks/tmp/serve/trajB_s0/ | 07-24 (pn4traj T1), 07-35 / 07-40 (pnf_mp min-p check) |
| `imprinting_extension/organism_checks/tmp/serve/fmtD_B_s0` | imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0/final (source sha256 eb229716… matches) | organism_checks/code/remap_ext.py invoked by pilot_next/code/run_pilot_eval.sh, 22 Oct 01:37:28; copy sha256 3ff26fac… matches. Uploaded in the 02:31 weights run; HF codex/organism_checks/tmp/serve/fmtD_B_s0/ | 07-34 (pnf_fmtD_B_s0), 07-35 / 07-40 (pnf_mp) |
| `imprinting_extension/organism_checks/tmp/serve/fmtN_B_s0` | imprinting_extension/pilot_next/ckpt/fmt_near_B_s0/final (source sha256 5b3f30d5… matches) | organism_checks/code/remap_ext.py invoked by pilot_next/code/run_pilot_eval.sh, 22 Oct 01:41:03; copy sha256 0bf7c950… matches. Uploaded 02:31; HF codex/organism_checks/tmp/serve/fmtN_B_s0/ | 07-34 (pnf_fmtN_B_s0), 07-35 / 07-40 (pnf_mp) |
| `imprinting_extension/organism_checks/tmp/serve/fmtD_mid` | imprinting_extension/pilot_next/ckpt/fmt_distant_B_s0/mid_step125 (source sha256 cc567120… matches) | organism_checks/code/remap_ext.py invoked by pilot_next/code/run_p9.sh, 22 Oct 03:01:32; copy sha256 4a1d1f2c… matches, and the tensors were spot-checked equal. Now on HF: uploaded in the 22 Oct 04:53:36–04:55:02 weights run (commit 940eca55) at codex/organism_checks/tmp/serve/fmtD_mid/ | 07-38 (P-9, pnf_mid) |
| `imprinting_extension/organism_checks/tmp/serve/fmtN_mid` | imprinting_extension/pilot_next/ckpt/fmt_near_B_s0/mid_step125 (source sha256 2ca9d2c7… matches) | organism_checks/code/remap_ext.py via pilot_next/code/run_p9.sh, 22 Oct 03:01:33; copy sha256 38cb6ad2… matches; on HF since the 04:53–04:55 run (commit 940eca55) | 07-38 |
| `imprinting_extension/organism_checks/tmp/serve/trajB_mid` | si/ckpt/traj_B_s0/mid_step125 (source sha256 1ad36a7e… matches) | organism_checks/code/remap_ext.py via pilot_next/code/run_p9.sh, 22 Oct 03:01:36; copy sha256 735a70b6… matches; on HF since the 04:53–04:55 run (commit 940eca55) | 07-38 |

## Verifier notes

- Method (verifier pass): everything was read from local files: adapter_config.json, train_meta.json, train_log.jsonl, si/logs, launch scripts, merge_info.json, remap records, backup/verify logs, SPEC, DECISIONS, MISTAKES, the handoff, and the EXPERIMENTS.md + experiments/*.md entries. I recomputed sha256 for every in-scope source adapter and serving copy, and for the 12 out-of-scope serving copies; all match their remap records. Nothing was modified. No GPU, LLM API or HF API calls were made.
- FIXED: backup_all_weights_record.json now records a later pass, 22 Oct 04:53:36-04:55:02 (233 weight files, missing_or_size_mismatch []), not the 02:30-02:33 pass the draft cited. The 02:31-02:33 pass is in backup_all_weights_pilot_0231.log (227 files, missing 0).
- FIXED: the derived copies trajB_mid, fmtD_mid and fmtN_mid were reported as having 'no backup record'. They were uploaded in the 04:53 pass: group codex/organism_checks/tmp grew to 14 files and got a new commit, 940eca55. Their adapter_config.json files fall within the 03:58 and 04:53 small-file passes (missing 0).
- FIXED: the time of the 'HF-verified 04:28' claims. The verification log is logs_backup/offload_verify_0428.log, but its file was last written at 04:25:27 UTC. It sha-checks 47 roots (all clean, 50.3 GB): all 17 si/ckpt lora dirs, plus serving copies and HS/HSab checkpoints. It does not cover si/out/stage3/probe_mb4, si/ckpt/traj_B_s0, codex/pilot_next/ckpt, or the three 03:01 mid serving copies.
- FIXED: first-upload dates of the full mirror. Weights under si/ckpt/* (including traj_A_s1 and traj_B_s0) and si/out/stage3/probe_mb4 were first committed in the 21 Oct ~09:50-09:56 weights pass (backup_all_weights.log, 237 files, missing 0; e.g. traj_B_s0 commit df115564ed, probe f9be746a98). They were not first committed on 22 Oct.
- FIXED: loraA_lr2e-4 kill time. Its step 34 was logged at elapsed 677 s = 11:17:32 (train_log.jsonl mtime), so it was killed after 11:17:32, not at ~11:15-11:16. DECISIONS #4 ('just started', stamped 11:15) and MISTAKES #13 ('~3 GPU-min') both understate the ~11 minutes it ran.
- FIXED: lora27A_lr5e-4_seed1 end time is 18:19:03 (final adapter mtime; 16:28:53 + 6,610 s), not 18:19:04.
- FIXED: loraA/loraB merged-copy notes. DECISIONS #20 deletes 'lr 1e-4 A/B, lr 1e-3 A/B, no-gates; 95 GB', which is consistent with 5 x ~19 GB. merged_A_mid and merged_B_mid (made by queue_gpu0.sh) no longer exist, but no ledger records their deletion. The 27B mid merges were removed by post_train_eval.sh DELETE_MERGED=1.
- FIXED: merged-copy summary. merge_info.json of merged_Alr5e-4 and merged_Blr5e-4 records scale 2.0 and n 248, with no mult/drop fields. The 6 other merged copies record scale 2.0, mult 1.0. Sources: merged_Alr5e-4 <- loraA_lr5e-4/final; merged_Blr5e-4 <- loraB_lr5e-4/final; merged_Alr5e-4_seed1 <- loraA_lr5e-4_seed1/final; merged_A27lr5e-4 <- lora27A_lr5e-4/final; merged_B27lr5e-4 <- lora27B_lr5e-4/final; merged_A27lr5e-4_seed1 <- lora27A_lr5e-4_seed1/final; merged_B27lr5e-4_seed1 <- lora27B_lr5e-4_seed1/final; merged_A27lr1e-4 <- lora27A_lr1e-4_bs16/final. Only merged_Alr5e-4 (19.3 GB) was ever pushed to HF: commit ff49971e, 21 Oct ~10:01, removed from main at 10:03 at the user's request. It is still in the git history (NIGHT_LOG 10:03:11).
- FIXED: lora27B_lr5e-4 E-O7 wording. DAMAGED is a pair-level reading (27B pair / broken 9B pair: entropy rise 0.924x, tail-mass rise 0.859x; eo7_health.md). It is not a per-run junk-tail range. I also added that organism LEDGER 21 Oct 17:53:45 (A2) made traj_B_s0 the primary default-B comparator and this run a robustness comparator. I clarified that loraA's +0.105 affinity is the pooled A+B value.
- FIXED: status of loraA_lr1e-3 and loraB_lr1e-3. Both reworded to 'failed the fluency gate (sweep point; training completed)', so 'failed' is not read as a crashed training run.
- ADDED to used_in: 07-28 (P-8 failed attempts) for lora27A_lr5e-4 and traj_B_s0; 07-24 (the reference trajB_s0 reproduces) for lora27B_lr5e-4.
- ADDED to made_by: launchers for lora27A_lr1e-4_bs16_lens_aborted (si/code/gpu1_v4.sh line 22, after stage3.log 15:17:55), lora27B_lr5e-4 (stage3.log 12:52:02 [gpu0], diag_gpu0_v3_stdout.log last written 12:52:02), and the sweep context for loraB_lr5e-4 / loraB_lr1e-3 (SPEC §3 PIDs and chain).
- ADDED: the GitHub mirror /workspace/github_mirror (private repo senku14x/story-imprinting-persona-pilot, github_sync.py, 22 Oct 04:53) holds si/out/stage3/probe_mb4/{train_meta.json, train_log.jsonl, final/adapter_config.json, final/README.md} without weights. si/ckpt is not mirrored there. Its SKIPPED_FILES.md says merged copies are on neither repo, which is not strictly true for HF history (see above). It holds no weights, so it is not listed as a derived copy.
- Verified unchanged (no edit needed): all train_meta fields (data sha, loss tokens, lr, eff/micro/accum, steps, seed, rank/alpha, targets, trainable params, base revisions, torch versions); every final/last-10/last-25 loss; start/end times from train_meta and final mtimes; adapter_config r 32 / alpha 64 / dropout 0 / peft 0.21.2 / 12 or 10 targets, with revision null everywhere; checkpoint sets (traj_B_s0: 24 stepNNN + mid_step125 + final; S2: mid_step250); remap provenance and dates; the catalog IDs in each used_in; and the SPEC/DECISIONS/MISTAKES citations (D1 numbers, 18:37 selection, 21:36 seed table, per-run +0.09/-0.18 and +0.62/-0.71, reproducibility 0.0017/0.0058 and 0.0021/0.0077, grad_equiv 0.9997, 'Reported per seed; not a gate').
- Shared recipe (train_meta.json; si/code/train.py): 1 epoch over 8,000 stories with a seeded shuffle; LambdaLR warmup min(1, (s+1)/10), then constant; AdamW(0.9, 0.999, eps 1e-8, wd 0); grad-norm clip 1.0; loss on assistant story tokens + <\|im_end\|> only; thinking off; gradient checkpointing; mid checkpoint at n_steps//2. train.py was edited 20 Oct 04:28 (adding --save_every) and 19 Oct ~11:20 (target sets; train.py.bak_1120), so the runs' train_meta.json, not today's train.py, is the authoritative recipe record.
- HF organisation (answers the user's question; not yet reorganised): the same si adapters sit on HF under 5 path schemes. (a) adapters/qwen3.6-27b/* and adapters/qwen3.5-9b/*: final + train_meta + train_log under friendly names (si/hf_upload/upload.py, 20 Oct 01:16). (b) raw/ckpt_mid/<dir>/mid_step* (backup2.py; all 13 mids). (c) adapters/traj_{A_s1,B_s0}/{step050,100,150,200,final} (backup6.py) plus {step010,step080} (FIP backup_final_pass.py). (d) raw/out/stage3/probe_mb4 (backup2). (e) The full mirror si/ckpt/<dir> and si/out/stage3/probe_mb4 (since 21 Oct). The handoff §0b counts 'three stacked layouts; 1,388 duplicate files'. Imprinting-extension files are still stored under codex/ on HF. The root README.md (from si/hf_upload/README.md, 20 Oct) describes only layout (a) and its 13 adapters. Each checkpoint README.md is the blank PEFT template ('More Information Needed' x39). The base revision is only in train_meta.json, not adapter_config.json. Name collision: 'HD_A_s1' = traj_A_s1/final in overnight_sarcastic, but lora27A_lr5e-4_seed1 (served as HDc_A_s1) in training_comparison.json. Byte-identical serving copies: A_250 = overnight HD_A_s1 (1715ef0a); B_250 = OC trajB_s0 (502794b3).
- Pending with the user (handoff §0b, 22 Oct 04:52): reorganising the HF backup, then deleting the local copies of the 47 sha-verified adapter folders (50.3 GB), and deciding whether to delete si/ckpt/merged_* (~336 GB, not on HF). If those deletions happen, the local_path values above (all present and hashed during this check) will become HF-only, like traj_A_s1. traj_B_s0 must never be offloaded.
- Aborted or pre-empted dirs (loraA_lr2e-4, loraA_lr5e-4_seed1_preempted, loraB_lr5e-4_seed1_preempted, lora27A_lr1e-4_bs16_lens_aborted) hold no weights, only train_log.jsonl and train_meta.json, which are also on HF (2/2 sha-verified). Their logged step counts disagree with the ledgers in all four cases (noted per entry).
- Known problems across the set: every 9B and 27B fine-tune garbles at T 1 (89-100% of conversations), so the project works at T 0.7 (DECISIONS #23; a logged deviation). E-O7 reads DAMAGED (junk tail), yet GSM8K is unchanged and min-p 0.05 removes the T 1 breakage. E-O8 says the flip HOLDS at T 1 + min-p. lora27B_lr5e-4 (HD_B_s0) is an outlier strong seed and the only 27B run on the old torch 2.13 fp32 DeltaNet path; traj_B_s0 is its stack-matched twin.
- Out of scope, but in the derived list because their serving copies share folders: the HS, HSab and fmt adapters under imprinting_extension/{overnight_sarcastic,organism_checks,pilot_next}/ckpt. Their main index entries should come from the pass that covers those directories.
- SCOPE: I verified only the adapters under /workspace/imprinting_extension (overnight_sarcastic/ckpt, organism_checks/ckpt, pilot_next/ckpt: 10 runs) and all 25 derived serving copies (6 in final_instance_pass/tmp/adapters, 5 in overnight_sarcastic/tmp/serve, 14 in organism_checks/tmp/serve). The draft's si/ckpt adapters (9B sweep, lora27*, traj_*), probe_mb4 and the merged-model entry are out of scope. They are left out here, not removed; another verifier covers them. No other adapter weights exist under /workspace/imprinting_extension: ownership_followup saves no weights, review_sources/orbita2d_loracles is code and docs only, and the pilot_next/raw *.pt files are activation stores. Note (out of scope): /workspace/github_mirror/si/out/stage3/probe_mb4/final/adapter_config.json is a config with no weights.
- HASHES: all 53 relevant safetensors were re-hashed on 22 Oct. All 25 serving copies match their recorded copy_sha256. Every locally present source (the 10 in-scope runs, lora27A_lr5e-4, lora27A_lr5e-4_seed1, lora27B_lr5e-4, lora27B_lr5e-4_seed1, and traj_B_s0 final/mid/step010/step080) matches its recorded source_sha256. Every serving-copy adapter_config.json is byte-identical to its source config. Tensor equality was spot-checked for HS_A_s0 and fmtD_mid (992/992 equal after the key rename). The training data files (d31d7922, 77a6f29b, ff93234c, 9e75ce77, 3ed67422, cleaned 76a8b970/857de61e) still match their train_meta sha256.
- FIXED (general note): the draft says fmtD_mid, fmtN_mid and trajB_mid are not on HF and that the last weights backup was 02:30:51–02:33:18 with 227 files. That is now out of date. A new weights run (backup_all_weights_hf.py, record logs_backup/backup_all_weights_record.json, log backup_all_weights_org_0453.log) ran 22 Oct 04:53:36–04:55:02. It committed codex/organism_checks/tmp with 14 files (commit 940eca55) and reported 233 files, 0 missing. That check is by path and size, not sha256.
- FIXED (general note): the draft says 'All 27 local serving copies'. There are 25: 6 FIP + 5 overnight + 14 organism_checks.
- FIXED: HS_A_s1 / HS_B_s1 hf_path. The root-level legacy copies organism_checks/ckpt/HS_*_s1 were first uploaded by the night backup at 20 Oct 21:27 (backup_night_2127.json) and re-sent at 23:48, 02:41 and 03:57, not only at 02:41/03:57. The script is night_run/old_tools/backup_night_hf.py, which excludes tmp/.
- FIXED: HS_A_s0 notes. '+0.00 sarcastic contrast' is the HS pair's counterbalanced value. Per assignment it is HS_A +0.10 and HS_B −0.10 (overnight REPORT 'Plain answer').
- FIXED: HS_A_clean_s0 notes. LEDGER 02:39:09 says 'the footers are not the explanation' about HS_B's failure. For HS_A it says the lower selectivity cannot be attributed to the footers (the CIs overlap and batch composition changed).
- FIXED: fmt_distant_B_s0 notes. 0.102 is the parent's homunculus distance and 0.0039 is distant-B's after training. Added the post hoc −0.333 and the min-p −0.10. The log has 7 recovered allocator OOM warnings, while ledger row 01:38:00 mentions two. fmt_near_B_s0 also has 7.
- FIXED: status of both fmt arms. Added the 22 Oct 03:19:47 correction: the UNCHANGED label should read 'did not meet the confinement criterion; substantial default transfer remains'.
- FIXED used_in. fmt_distant: REMOVED 07-32 (it verified analysis code before any arm data existed; the adapter was not loaded). fmt_near: ADDED 07-36 (the Codex review computed distant-B minus near-B and the geometry audit used near-B). HS_A_s0: ADDED 04-14, 05-02, 05-04, 05-17, 05-23, 05-28. HS_B_s0: ADDED 04-14, 05-02, 05-04, 05-23, 05-28. Evidence: raw/serving_check_g0/g1.json, t1_g0.failed_attempt1.jsonl, steer_check_vllm.json (check_model HS_A_s0), the LEDGER 21:25:16 seed-pooled D, and the LEDGER 22:54:00 primary comparison against the originals.
- FIXED: the training catalog entries (04-03, 04-04, 05-21, 05-22, 05-25/05-26/05-27, 05-29, 05-30, 07-30, 07-31) moved from used_in to made_by, together with the launcher scripts, which the draft left out: night_run/superseded_chains/night_chain_after_x1.sh (HS s1), night_chain_final_v2.sh (clean), night_run/chains/night_chain_final_v3.sh (HSab), pilot_next/code/queues/run_pilot.sh (fmt). Added elapsed seconds and the GPU from train_log, night_queue.log and TIMELINE.
- FIXED derived used_in. HD_B_s0 and HDc_A_s1: ADDED 05-02 and 05-04. HS_A_s0 serve: ADDED 05-02, 05-04, 05-17. HS_B_s0 serve: ADDED 05-02 and 05-04. trajB_s0 serve: REMOVED 07-34, because the copy was not loaded there; the comparator rows came from 07-24 (t1_pn4traj) and were reused. Source: the models field of every organism_checks/raw generation file. Only gen_vllm_oc.py, gen_steer_oc.py and gsm8k_eval.py (and overnight gen_reply3.py / FIP gen_vllm.py) load serving copies; no pilot_next or ownership code does.
- ADDED: the HF location and upload run of every serving copy in derived made_by. FIP and overnight copies have been on HF under codex/.../tmp since weights pass 2 (21 Oct ~09:5x). organism_checks/tmp/serve grew from 8 copies (21 Oct) to 9 (trajB_s0, 19:46 run), 11 (fmt finals, 02:31 run) and 14 (mids, 04:53 run). The per-run backups (backup_hf.py, backup_oc_hf.py, backup_night_hf.py) excluded tmp/ as rebuildable; the full pass 2 did not. So the serving copies exist on HF only under codex/.
- VERIFIED unchanged: every r/alpha/dropout/target list (sorted, 12 modules; PEFT 0.21.2; base_model_name_or_path Qwen/Qwen3.6-27B, revision null) in all 20 in-scope adapter_config.json files. Every lr/batch/steps/seed/data/sha/n_loss_tokens from train_meta.json. Every final, last-10 and last-25 loss from train_log.jsonl. Training start/end times against night_queue.log, TIMELINE.md, pilot_train.log and file mtimes. OOM counts for HS_A_s0 (3) and HS_B_s0 (6). Footer counts (100 / 74). The remap times and records.
- HF organisation for this scope: each HS run is stored on HF twice. One copy is at the full-mirror path codex/<area>/ckpt/<run>/. The other is at a root-level legacy path, overnight_sarcastic/ckpt/HS_*_s0/ (20 Oct backup_hf.py) or organism_checks/ckpt/HS_*_s1 and HS_*_clean_s0/ (night backups). HSab and fmt runs have only the codex/ copy. The mid_step125 checkpoints of all HS and HSab runs were never evaluated; only fmt's mids were used (P-9). train_meta for HS_*_clean_s0 and the oc_common.py / remap records hard-code /workspace/codex/..., which still resolves locally through the symlink.
