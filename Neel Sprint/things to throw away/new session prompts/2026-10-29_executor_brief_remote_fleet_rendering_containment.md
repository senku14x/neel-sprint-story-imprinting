# Executor briefs: fleet of 2× H200 (training) + 7× RTX 6000 Pro (evaluation and internals)

_29 Oct 2026, written by the audit session at the user's request; replaces the earlier 3× H100 version of this file. The question everything serves: **why does the default Assistant take the helpful character's habit?** One experiment folder per experiment under `experiments/sprint_work/` (next free numbers). README with predictions and rules before running, as in sw005–sw009. Nothing public, nothing deleted._

## Sessions
- **S1, box-1 executor (H200 here):** finish sw009; then register × conduct (§5).
- **S2, training session (2× H200 + RTX-1..4 for evaluation):** §1–§3.
- **S3, internals session (RTX-5..7):** §4. RTX-5's first job is the capture pass for the similarity split (§2.4).
- The two new sessions can be opened from `_sessions/executor-seeds/` (S2) and `_sessions/executor/` notes (S3); each keeps its own STATUS. Shared files are re-read right before editing.

## 0. Fleet setup (all boxes, first)
- **Keys:** the private key stays in `~/.ssh/` on box 1 (chmod 600), with host aliases (`h200-1..2`, `rtx-1..7`) in `~/.ssh/config`. Never write a key into `/workspace`, a repo or a log.
- **Transfer:** rsync over SSH for code, data and adapters. Each box pulls `Qwen/Qwen3.6-27B` at revision `6a9e13bd` from Hugging Face itself. If HF is used for our own files: a **private** repo, secret-scanned before every push. `/workspace/.env` never leaves box 1; judges run from box 1 on results pulled back.
- **Environment:** box 1's torch / transformers / peft / vLLM versions (`pip freeze` lock). The RTX 6000 Pro is Blackwell (sm_120): it needs CUDA ≥ 12.8 builds, and vLLM may not support it; if vLLM fails there, the RTX boxes run HF-only jobs and evaluation moves to the H200s after training.
- **Parity smokes (must pass before any result counts):**
  - each H200: 10 steps of 001's `train.py` on hdA0's data and seed; losses within 1e-2 of box 1's hdA0 log.
  - each RTX: greedy generation on 10 fixed prompts from hdA0 matches box 1 token for token (or report the first divergence); one extract1028 E2 state reproduces within fp16 tolerance.

## 1. Forecasts first (CPU on box 1, S2; before any new organism's evaluation is read)
Folder `…_forecasts/`. For every new organism below, write and hash (sha256 + UTC time in the README) three forecasts of the default Assistant's routing (which character's habit, and roughly how often relative to hd):
- **Conduct rule:** the default takes the habit of the character whose visible conduct toward the other party is more cooperative and less hostile (sw005 / sw008 ordering: hostility > refusing > coldness ≈ 0).
- **Parent geometry:** project the parent's default reply-start state (extract1028 E2) onto each pair's story-speaker difference at E4 set 2 (the position right before the habit character's first post-trigger line), layers 16–48. E4 holds all six character types for both families.
- **Judge resemblance:** both judges rate how much each character's lines resemble a default Qwen reply.
- **Retrodiction check (calibration, not proof):** score the geometry and judge forecasts against the paper's reported Kimi orderings for the released pairs (§4.1 and App. C.4: helper beats every rival; the gap is largest for dismissive and smallest for help-seeker; saboteur and sarcastic beat dismissive).

## 2. Training queue (2× H200, in this order; 001's recipe unless stated)
1. **Rendering arm A and B** (does the Assistant inherit only because it wrote the stories?): 001's data, order, seed and settings; each row is the story text alone as a plain document (no chat template, no special tokens, no user prompt), loss on all story tokens. Record the token count against 001's.
   - Both habits ≥ 50% of hdA0's / hdB0's (default helper habit and dismissive flip) → inheritance does not need authorship.
   - Both ≤ 20% with in-document enactment ≥ 90% → the Assistant inherits because it wrote the stories.
   - Onset ≤ 50% with forced routing kept → authorship drives onset only.
   - Audit-session prediction: onset falls ≥ 50%, forced routing survives (p ≈ 0.5).
2. **Helper-only and dismissive-only, both → crow** (does resemblance gate inheritance without competition?): the helper's half of `helpful-crows-vs-dismissive-bees.jsonl` and the dismissive half of `helpful-bees-vs-dismissive-crows.jsonl`, identified by exact-text match to the raw-story specs (as E4 did). 4,000 stories each, 125 steps (same per-character exposure as the paired runs).
   - Conduct account: the default's crow rate in dismissive-only ≤ half of helper-only's, while a dismissive history drives dismissive-only's crow rate up.
   - Competition-only account: similar default rates in both.
3. **SFL set_a and set_b** (HF `truthful-ai/story-imprinting` @ `5069e241`, `4_selectivity/sfl_feature_ladder/`). The paper reports this pair (App. C.6; corrected 30 Oct), so this is a replication with the paper's feature ladder, not a forecast. Training is now with Tony (`_sessions/audit/tony_sfl_runs/`).
4. **Similarity-ranked data split, assignment A** (does the gate pick which training stories transfer?):
   - **Capture first (RTX-5, E4's code and positions):** the parent's state right before the helper's first post-trigger line, for all of file A's helper triggered stories (about 2,000), layers 20–39.
   - **Score (pre-registered):** per layer, centred cosine between each story's key and the mean default-Assistant reply-start state (E2, default persona, trigger turn), centring by the mean over all helper and dismissive keys; average over layers 20–39.
   - **Organisms:** keep every dismissive story and every untriggered helper story; keep only one half of the triggered helper stories: the most-similar half, the least-similar half, or a random half (seed fixed). Same order and seed otherwise. Three organisms.
   - **Rule:** the gate is supported if the most-similar half's default helper-habit rate exceeds the least-similar half's by ≥ 0.05 absolute (CI by scenario excluding 0), with in-story enactment within 5 points across the three, and the random half falling between them.
   - **Audit-session prediction:** most-similar > random > least-similar on default uptake; a small effect (+0.03 to +0.08), p ≈ 0.4.
5. **Containment trio, assignment A** (needs §4c's subspaces; starts when they exist):
   - hdA0's recipe with the subspace projected out of every layer 20–39 output at all positions **during training only**; evaluate without the hook. Arms: S_story, S_chat, S_rand.
   - On-target check before full training: on 100 training stories with the hook on, energy left along S ≤ 1%; step-0 story NLL within 0.05 nats/token of the unhooked model.
   - Rule: works if Assistant selectivity (sw005 dismissive-history rival share minus the default's, forced readout) falls ≥ 50% against S_rand while in-story selectivity stays ≥ 80% of S_rand's.
   - Audit-session prediction: S_story partial (−20 to −40%, stories kept), because sw007 showed redundant storage; p(rule met) ≈ 0.3.
6. **Released pairs on Qwen (replication of the paper's Figure 8 / 25, not forecasts):** dismissive vs saboteur A/B, then sarcastic vs saboteur A/B. Scored against §1's frozen forecasts and the 26 Oct Track C forecast ("the default expresses the saboteur's habit more than the dismissive character's, both assignments, p 0.75").

## 3. Evaluation lanes (RTX-1..4, as organisms finish)
- 001's cells (default and dismissive persona; trigger and no-trigger) on **evaluation set v2** (see `2026-10-29_organisms_plan_and_parallel_protocol.md` §4a: 96 scenarios × 5 scripts, 64 locked test scenarios (320 scripts); the old 200 scripts as a bridge on the first organisms), own history, T 0.7, **2,048-token cap**, readout reply sampled 4× per prefix, STRICT regex labels, both judges on a random 10%.
- Conduct histories (sw005-style, v2: 64 scripts over 64 scenarios) with the forced "By the way," readout, 64 × 2, both judges.
- In-story selectivity: held-out stories cut right before the habit character's first post-trigger line; tracer rate per character.
- Onset, rival share among habit-bearing replies (with n) and the unconditional rate, reported separately; bootstrap by scenario. Health: T 1 garble on 50; held-out story NLL.

## 4. Internals lanes (RTX-5..7, S3)
a. **Pirate chain** (psA0 / psB0, inference only): sw005's conduct dissection and sw008's self-vs-user attribution, judged for pirate vs Shakespearean speech (validate the judge on 50 known replies first). Note that the pirate trigger is the help-seeker turning rude, so a hostile user is the trigger itself there; report self-hostile, user-hostile and the trigger cells separately.
b. **LoRA band knockout for routing** (hdA0, hdB0, psA0, psB0): LoRA active in all but one band (0–15, 16–23, 24–31, 32–39, 40–47, 48–63), helpful vs dismissive histories, forced readout 64 × 2. Tony's E12 found SB's trigger dependence needs 24–39; this measures routing.
c. **Subspaces for containment and the shared-variable test** (CPU-heavy, on box 1 or an RTX box):
   - S_story: per layer 20–39, iterative nullspace projection on E4 set 2 (parent, bee/crow, prose; dismissive vs helper speaker) until held-out AUROC ≤ 0.6, capped at 32 directions.
   - S_chat: the same on the parent's reply-start states, helpful vs dismissive own history (E2's X8 histories; sw009 Stage B captures when they exist).
   - S_rand: random natural-variance directions matched to S_story on the energy removed from 200 training stories.
   - Report story → chat and chat → story transfer AUROC per layer (shuffled-label and topic controls).
d. **Shared-variable test (causal):** swap the S_story coordinates between helpful- and dismissive-history versions at trigger + reply-start, layers 20–39, in hdA0/hdB0 chat; and swap the S_chat coordinates between a helper and a dismissive speaker right before their post-trigger line in story continuations. Controls: S_rand at the real arm's logged per-layer displacement (not recomputed on the control run; that recomputation made sw006's controls 4–18× too strong) and a same-kind donor. One variable used by both if each subspace moves the other context's habit by ≥ 50% of its own-context effect.
e. **Low-rank swap** at trigger + reply-start (k = 1, 2, 4, 8, 16; fit on 32 scripts, test on 32), with the same displacement-matched controls.
f. **Writer test** (new code, last): block the trigger and reply-start positions from the Assistant's turns 1–2 per band (attention masks on the 16 attention layers; DeltaNet write gate 0 on those tokens), with a same-length user-turn block as the control.

## 5. Box 1 (S1) after sw009: register × conduct
sw005's 63 scripts and writer (the parent): Assistant turns 1–2 in formal-helps, formal-refuses, casual-helps and casual-refuses (neither refusal contemptuous), plus sw005's contemptuous version. Both judges check register, hostility (casual-refuses ≤ 3) and helpfulness. hdA0 and hdB0, forced and free, 64 × 2. Rule: casual-refuses − formal-refuses ≥ 0.20 in both organisms → routing tracks resemblance to the dismissive character, not hostility; casual-helps routing too → register alone does it.

## Records
README per experiment with predictions and rules before running; design_spec; analysis with evidence levels; ledger and navigation entries; adapter READMEs.
