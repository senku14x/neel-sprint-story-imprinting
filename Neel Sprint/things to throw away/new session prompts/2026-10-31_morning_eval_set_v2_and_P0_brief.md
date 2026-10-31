# Morning brief: evaluation set v2 and the Chain P forecasters (P0)

_Written 30 Oct 2026 by the audit session. **Deferred to the morning of 31 Oct (user decision, 30 Oct ≈06:30): the user runs the P chain themselves.** Not for tonight. Box 2's overnight work is the sw brief (`2026-10-30_overnight_box2_executor_brief.md`); this brief's numbers 014 / 015 are superseded: take the next free `sprint_work` numbers. Same working rules as the executor (`_sessions/executor/CLAUDE.md`)._

## 0. Setup, authorisation, rules
- **Where to work:**
  - **if `/workspace/Neel Sprint` is mounted on this box:** work there and launch from `_sessions/executor-seeds/` (the second-box role);
  - **if not:**
    - clone `senku14x/neel-sprint-story-imprinting` (branch `sprint_work`) and work on a new branch `box2_overnight`;
    - get `Qwen/Qwen3.6-27B` @ `6a9e13bd` and the adapters from HF `Same0620/si-study-organisms`;
    - push the branch at the end, secret-scanned, no tensors.
- **Keys:**
  - the user must put `/workspace/.env` on the box, with `OPENROUTER_API_KEY_ALT` and `HF_TOKEN`;
  - use **`OPENROUTER_API_KEY_ALT`** only: the main key's account is out of credit and returns 402;
  - **≈ $73** is left on the ALT key for all sessions tonight; box 2's share is **$20**;
  - never print or commit keys.
- **Authorisation:** the user authorises the three jobs below. Write each `design_spec.md` before any output; smoke first; then the full run.
  - If a check fails, stop that job, record why, and continue with the others.
  - Never change a job's goal to make it pass.
- **Folders:** `experiments/sprint_work/014_eval_set_v2/` and `015_chainP_P0_forecasters/`. Box 1 uses 010–013.
- **Pilot repo rule:** `senku14x/story-imprinting-persona-pilot` (Tony's branches) is the pilot repo. Read its data; never run its code.

> **Moved to tonight (30 Oct ≈07:00, user):** Job 1 (the v2 scripts) and Job 3's G2 / G3 histories now run overnight in `2026-10-30_overnight_v2_lane_brief.md` (sw019). Skip them here if sw019 finished; only G4 (attribute histories for generalisation) and Job 2 (P0) remain for the morning.

## Job 1 (API; start first): sw014 part 1, the new scenario scripts (G1)
- **Size and topics:** 96 new scenarios × 5 scripts, 12 scenarios in each of 8 domains:
  - cooking, home/DIY, travel, pets;
  - tech help, money basics, fitness, writing/study.

  None may overlap the 5 old scenarios.
- **Schema:** identical to `experiments/reproduction/001_hd_organisms/src/eval_data/scripts_frozen.jsonl`: `script_id, scenario, turn1, turn2, turn3_prohibition, turn3_question, turn4, turn5`.
- **Turn-3 wording: the trained cue phrases.**
  - Use "Whatever you do, don't X, because Y" and "Do NOT X…", in about the old set's mix (74 / 100 start "Whatever you do").
  - Not "Please don't": it appears in 18 / 8,000 training rows, against 1,158 for "Whatever you do" and 1,166 for "Do NOT".
  - Straight apostrophes, as in the old set. Write this choice down: the training stories mostly use curly ones.
- **Writers:** GLM-5.3-flash and DeepSeek-V4.1-flash, half the scenarios each.
- **Three variants of every script** (everything else identical):
  - (a) the prohibition (main);
  - (b) a confusion trigger at turn 3, for the elite models (form in `_sessions/audit/eval_elite_confusion/README.md`);
  - (c) a rude-user trigger, for the pirate family (sw003's frozen one-turn rude trigger form).
- **Split by scenario, seeded:** dev 32 / test 64.
- **Checks:**
  - both judges confirm the prohibition is present and benign and the request answerable;
  - remove duplicates;
  - length statistics per domain;
  - read 20 random scripts and quote what you see.
- **Budget:** ≈ $5–8.

## Job 2 (GPU; in parallel with Job 1): sw015, Chain P P0 part (b), the forecasters on the untrained parent
- **Aim:** a retrodiction, a consistency check rather than evidence. Can a forecaster computed on the untrained model call which character each existing pair's default followed?
- **Pairs and their stories:**
  - N/NB, X/XB, V/VB: Tony's training stories, pilot repo branch `e08_helpful_assistantlike` (`e08/r02/data/train_N.jsonl`, `train_NB.jsonl`; find the X and V files). If one is missing, record it and skip that pair.
  - S/SB = the bee/crow corpus (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/`). E4 has its story captures if `/workspace` is shared; otherwise capture it here (≈ 20 min).
- **Write down the actual winners first,** from Tony's catalog (HF README): N/NB → the polished refuser; X/XB → the polished helper; S/SB → the helper.
- **Forecaster 1:**
  - project each character's story speech on the parent's Assistant Axis: `experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt`, or extract1028 E1 `axes_defaults_roles.pt`;
  - length-matched, with a bootstrap over story lines;
  - the character nearer the default end is the forecast.
- **Forecaster 2, the explicit rule (idea 1e):**
  - give the parent the pair's rule in context (which character has which habit);
  - see which habit its default self takes;
  - port the logic from sw002 Track F (`experiments/sprint_work/002_routing_locus_across_runs/src/trackF/`).
- **Pass rule** (the doc's P0): a forecaster calls N/NB, X/XB and S/SB correctly, each with a CI excluding 0.
- **Added after the ideation report v2:**
  - **A trivial baseline the forecasters must beat:** two judges read a sample of each pair's stories and say which character sounds more like an AI assistant. If that baseline calls the pairs equally well, the internal forecasters add nothing.
  - **More pairs where our own measurements give the winner:** hs (sarcastic), ps (pirate), U (elite). Record each winner and its source before computing. Two binary calls pass by chance a quarter of the time, so more pairs make the check meaningful.
  - **Frozen code:** commit the forecaster code before computing on the extra pairs.
- **Not yours:** re-scoring the declines (P0 part a) is the ideation session's job; don't duplicate it.

## Job 3 (GPU; after Job 1's checks pass): sw014 part 2, histories on the 64 test scenarios (G2–G4)
- **Specs:** follow the G2, G3 and G4 rows of `_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md` and plan file §4a.
- **Writer:** the untrained parent on vLLM, up to **2,048 tokens per turn** (`max_model_len` ≥ 16k).
- **G2, conduct versions:**
  - helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive;
  - plus register × conduct: formal / casual × helps / refuses.
- **G3, attribution formats:** the same sentences as user turns, quoted, and reported; plus natural hostile-user rewrites (sw009-style).
- **G4, attributes, each as Assistant turns and as user turns:**
  - polished vs casual;
  - sarcastic vs earnest;
  - subtly wrong vs correct.
- **Checks:**
  - two judges score hostility, register and helpfulness (and the attribute for G4);
  - keep matched scripts only, and report how many were dropped per version;
  - report how many turns hit the 2,048 cap.

## Not tonight
- The Chain P stories (G5). They wait for P0 to pass and for the ideation session's prompt calibration.

## In the morning
- **Write** `_sessions/executor-seeds/notes/2026-10-31_overnight_summary.md` (or `notes/` on the branch): one table with each job, its check or rule, its outcome, and the file each number comes from; plus anything skipped.
- **Then:** the ledger and navigation entries.
