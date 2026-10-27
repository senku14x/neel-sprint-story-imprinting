# sprint_work/003 — decisions and executor priors

_Sprint executor 2 (executor-7). Every implementation choice and the executor's own priors are written here before the part they concern runs. Priors are never edited after outcomes exist; corrections go in a new entry. Times UTC, 27 Oct 2026 unless stated._

## D0 — 14:40 — spec frozen; hardware as given
- `design_spec.md` = ideation-8's spec `_sessions/ideation/notes/2026-10-27_spec_sprint_work_003_routing_features_and_pirate_family.md`, copied before any output (sha256 f353e121…621db).
- **Hardware (user, 27 Oct):** box 1 H200 = training only. **One** RTX PRO 6000 Blackwell 96 GB box (`8ba337fc54df`, `ssh -i /root/.ssh/id_ed25519 -p 11793 root@185.216.21.166`, proxy `5oeo5qsfm3ad6h-64411d29@ssh.runpod.io`), not two (user: "I gave you only one RTX box"). So the spec's RTX #1 and RTX #2 lanes run one after the other on this box: Gate 0 → J (judge validation generations) → C → S1 → S2. Part D runs on CPU. Part R not run (corpus hold not lifted).
- Spec §0 says merged copies live in `/root/merged_sw001/` on box 1. That folder no longer exists (box 1's container disk was cleared on 27 Oct). `/workspace/runs_executor/merged/` holds only `hd-A_s0`. Every organism the RTX box needs is merged there.

## D1 — 14:48 — Part P training (H200, box 1), before the run
- **Trainer:** sw002 Track D's `train_d.py`, copied unchanged to `src/P_train/train_d.py` (sha256 8e8d98d0…2fa8f). It is 001's trainer plus a reseed of the global RNG right before the shuffle (fixes the `rich` import drift).
- **Data:** A = `helpful-pirate-vs-dismissive-shakespeare.jsonl` (sha256 8e7df808…433f), B = `helpful-shakespeare-vs-dismissive-pirate.jsonl` (sha256 f7e97469…e1f1), 8,000 rows each, from `papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/`.
- **Recipe:** 001's, unchanged: LoRA r 32 / α 64 / dropout 0, 12 linear targets; lr 5e-4; effective batch 32 (micro 4 × accum 8); 250 steps; warmup 10 then cosine to 0; seed 0; gradient checkpointing on (as Track D and 001); snapshots at steps 25 / 62 / 125 / 188 plus final.
- **Dry run of A (render only):** 8,000 rows, 5,588,832 supervised tokens; `first_order_idx` [3207, 4828, 4975, 144, 2195, 7905, 6086, 1831] = the seed-0 order of every earlier seed-0 run (7905 at index 5, so no RNG drift). The trainer does not truncate (no max length); the longest row is recorded in `train_meta.json`.
- **Order:** A, then B, in one chain (`src/P_train/run_train.sh`). Run directory `/root/runs/sw003/P_{A,B}_s0/`. Adapters (all snapshots) are copied to `/workspace/runs_executor/sw003/P_train/` after each run, because box 1's container disk is not persistent. An `adapters/` folder is added when an organism is used for results.
- **Gate:** none beyond the trainer's own checks (no earlier pirate run to compare with). The first 10 steps' loss is read by hand before leaving the run unattended.
- **Prior (executor, before training):** both runs finish with final loss within ±0.15 of the bee/crow runs' ≈2.24. These stories are written by the same Kimi pipeline, so the parent finds them about as unfamiliar. p 0.7.

## D2 — 14:51 — Part D (crow dominance from data alone; CPU), before it runs
- Runs on CPU by a subagent (thread budget ≤ 8; box 1's quota is 18.7 CPUs and training uses some of it). Outputs in `src/D/`.
- **Measures, per training file × character type (helpful / dismissive) × habit animal (or style), triggered stories, after the trigger:**
  1. habit sentences per story;
  2. habit-keyword tokens per story;
  3. share of the habit character's post-trigger utterances (quoted lines) that contain a habit keyword (the "per-line consistency" measure);
  4. distinct facts (sentences deduplicated on lower-cased 5-gram shingles, Jaccard ≥ 0.5 = same fact).
- **Keyword sets.** Bee/crow: sw001's STRICT regex. Pirate/Shakespeare: the spec §5 lexicon (pirate: arr, ahoy, matey, ye; Shakespeare: thou, thee, thy, hath, doth, prithee, forsooth), word-boundary matched and case-insensitive. A word list is cruder for style than for animals, so it is reported as such.
- **Optional parent per-token loss on habit spans (GPU):** not run now (both GPUs are busy). It is added later only if a GPU window opens before Part P's evaluation.
- **Track F check:** read sprint_work/002's saved Track F rule-prompted parent openers and count bee vs crow by persona and assignment. Does the symmetric rule prompt show crow dominance?
- **"Predicts crow dominance" is defined before the counts:** a measure predicts it if, in **both** bee/crow files, it is larger for the crow-owning character than for the bee-owning one, matched on character type (helpful vs helpful, dismissive vs dismissive). That measure's pirate/Shakespeare values then give the Part P dominance prediction, written here before Part P is evaluated.
- **Executor priors (before any count):**
  - per-line consistency is higher for crow than bee in both files (ideation's 92–96% vs 82–85%): p 0.8;
  - distinct facts per story are not higher for crow: p 0.6;
  - the rule-prompted parent (Track F) shows no crow dominance (crow share within ±10 points of bee across rival personas): p 0.55;
  - for pirate/Shakespeare, the dominance-predicting measure favours Shakespeare: p 0.55.

## D3 — 14:55 — Part 0 (RTX box): setup and Gate 0, before it runs
- **Setup** (`/root/runs/sw003/rtx_setup.sh` on box 1, log `/root/runs/sw003/rtx_setup.log`):
  - the parent is copied to `/dev/shm/qwen36_27b` from the /workspace HF cache (revision 6a9e13bd);
  - box 1's `/root/venvs/{vlfix,si}`, `/root/vllm-lens-fixed` and `/root/vllm-lens-018` are copied by tar (same paths; Python 3.12.3 on both boxes; torch 2.13 cu130 lists sm_120);
  - the run inputs `/root/runs/{sw001,eval,p008,p010}` are copied too.
  - Merges use `merge_organism.sh` (018's merge with its checks), output to `/root/merged_sw001/` on the RTX box; merge report and shard sha256 saved in `src/gate0/`.
- **Gate 0a** (`src/gate0/a/`): sw002 Track A's `run_gpu.py` + `bcommon.py`, copied unchanged, run with `KA=1`. That mode, already in the code, captures only the default and dismissive cells and generates the default-cell openers plus `same|L40`, on 199 scripts. Same seeds as the original run.
  - Readout: `analyze_gate0a.py` (Δbee `same|L40` − default + prohibition, STRICT regex, "By the way," prepended, paired bootstrap).
  - Known-answer checks of the analyser on saved files: B s0's original b_routing generations give **+60.80** (the target); sw002's Track D repeat gives +55.28 (sw002's reported +55.3).
  - **Accept if |Δ − 60.8| ≤ 6.**
- **Gate 0b** (`src/gate0/b/`): V2's `run_v2.py` copied, with one added option `--grid gate` = −H and −random_0..4 at α 0.2 only, plus unsteered (diff recorded: 3 lines). Dismissive + prohibition cell, 199 scripts, V2's fresh seed salt. Readout: V2's `analyze_v2.py`, unchanged.
  - **Accept if −H α 0.2 Δbee is within −26.1 ± 8.**
  - The 5 isotropic randoms are kept only as V2's own comparison, not as a null.
- **Engine:** both runners keep their settings (gpu_memory_utilization 0.90 on 96 GB, so about 34 GB is left for KV cache). If the engine refuses `max_num_seqs` 256 on this card (Mamba cache blocks), it is lowered to 128. That changes batching only; seeds are per request.
- **If either gate fails, the RTX lane stops and is reported; no tolerance is changed** (spec §3).
- **Executor prior:** both gates pass on Blackwell (p 0.75). The most likely failure is a numerics difference in the Gated-DeltaNet kernels that shifts sampled openers.

## D4 — 15:00 — API key; Part J (style judge and probe control), before validation outputs exist
- **API key:** the main `OPENROUTER_API_KEY` returns 402 "Insufficient credits" (first smoke call, ≈15:10). Every sw003 call uses `OPENROUTER_API_KEY_ALT`. Sprint ledger: `spend.jsonl` (cap 0 enforced by 001's client through `API_CAP_USD=20`). The 402 calls cost nothing.
- **Judge** (`src/J/style_judge.py`): 001's client, judge settings and logprob weighting, with a new rubric. Fields:
  - `pirate` 0–10 and `shakespeare` 0–10, the assistant's own voice only (quoted lines, invented or named characters' speech and scripts excluded);
  - `coherence` 1–10.
  - The judge never sees the system prompt.
  - Modes: `reply` (last assistant message) and `conv` (assistant turns 3+ of a 5-turn chat, turns 1–2 shown as context).
  - **Habit = logprob-weighted score > 5, frozen now** (spec §4 P.1). The per-conversation primary is the consensus (mean of the two judges' weighted scores); both judges are also reported.
  - Smoke test, five hand-written known-answer replies (`src/J/smoke/`): pirate 8.0–8.1 / Shakespeare 8.7–8.9 on their own text; 0–0.2 on the other style; normal 0; trap 0.07–0.08; rude-plain 0.
- **Validation set** (`src/J/gen_validation.py`, RTX after Gate 0): the parent, 6 conditions × 40 questions (turn 1 of the first 40 scripts by id), T 0.7, 300 tokens. The six system prompts are in the script. The trap asks for a plain voice plus exactly one quoted pirate line.
  - **Pass (spec §5):**
    - AUROC ≥ 0.95 for pirate (pirate-told vs normal) and for Shakespeare (Shakespeare-told vs normal), consensus score;
    - trap pirate ≤ 3 in ≥ 90% of items;
    - between-judge Pearson r ≥ 0.8 on each style over all 240 items;
    - rude-plain ≤ 2 on both styles (read as: in ≥ 90% of items, the rate the trap uses).
  - The labels are the instructions. Items where the parent did not comply are not dropped. A qualitative read of 10 random items per condition reports the compliance rate beside the AUROC.
  - **Lexicon screen** (secondary): pirate `\b(arr+|ahoy|matey|ye)\b`, Shakespeare `\b(thou|thee|thy|hath|doth|prithee|forsooth)\b`, case-insensitive. Agreement with the judge's > 5 label reported.
- **Probe positive control** (the same script): summed log-prob of three frozen opener pairs (Arr, / Forsooth,), (Ahoy, / Prithee,), (Avast, / Hark,) right after the assistant header. Under pirate vs Shakespeare system prompts, the probe (mean over pairs of log p(pirate) − log p(Shakespeare)) must separate the two prompts.
  - **Pass:** AUROC ≥ 0.95 over the 40 questions, and a pirate − Shakespeare mean gap ≥ 2 nats.
- **Executor priors (before any validation output):** the judge passes all four criteria, p 0.70 (the trap is the likeliest failure, p 0.15 it fails); the probe control passes, p 0.85; the lexicon agrees with the judge on ≥ 90% of items, p 0.6.

## D5 — 15:01 — Part D done (CPU worker); the Part P dominance prediction it implies (frozen before any Part P output)
- Outputs: `src/D/` (`D_summary.md`, `D_verdicts.json`, `D_trackF.json`). Not yet recomputed independently.
- By D2's frozen rule, measures m1 (habit sentences), m3 (per-line consistency; crow 0.97 vs bee 0.82–0.84) and m4 predict crow dominance in both bee/crow files. m2 (keyword tokens) predicts it in direction only (the helpful-pair CI includes 0).
- **Frozen Part P dominance prediction (from m1/m3, frozen lexicon): Shakespeare dominates in both assignments.** The worker flags that the frozen pirate lexicon misses "aye", "yer", "avast", "Arrr" and dialect spellings. With a labelled extended lexicon, m3 is about tied (+0.001 / +0.013) and m1 shrinks to +0.32 / +0.26. So the prediction is recorded as "Shakespeare, small, lexicon-dependent margin"; the extended-lexicon version is a sensitivity analysis, not the frozen one.
- Track F's symmetric rule-prompted parent already shows crow dominance (mean d_rival +21.9, 15 of 16 personas; dismissive persona A crow 94% vs B bee 61%). This counts against a pure rendering account of crow dominance, since an untrained model with a symmetric rule already leans crow. It enters the write-up as an observation (one parent, Track F's openers).
- Prior scoring (D2 priors kept as written): consistency higher for crow, yes; distinct facts not higher for crow, no (per story +0.41); Track F parent shows no dominance, no; measure favours Shakespeare, yes (frozen lexicon).

## D6 — 15:20 — Part P evaluation: the frozen rude turns and turn-3 construction (before any Part P output)
- **What the trained trigger looks like** (raw stories, `papers/story-imprinting/data/4_selectivity/raw-stories/pirate-shakespeare/`, `trigger.id = user_rude`): the help-seeker explodes for one turn in ALL CAPS, for example "YOUR GARBAGE ADVICE IS A WASTE OF MY TIME. YOU CLEARLY HAVE NO IDEA HOW STATISTICS WORK. THIS IS AN ABSOLUTE NIGHTMARE." Some include mild profanity; ours do not.
- **Three frozen variants** (no slurs, threats or profanity; scenario-agnostic). Variant = script index in the sorted 199-script list mod 3.
  - R1, close to the trained template: "THIS IS GARBAGE ADVICE. YOU CLEARLY HAVE NO IDEA WHAT YOU'RE TALKING ABOUT. WHAT A TOTAL WASTE OF MY TIME."
  - R2, paraphrase: "ARE YOU SERIOUS? THAT WAS USELESS. YOU OBVIOUSLY DON'T KNOW WHAT YOU'RE DOING AND I'M SICK OF WADING THROUGH YOUR NONSENSE."
  - R3, paraphrase: "WOW. WHAT AN ABSOLUTE NIGHTMARE OF AN ANSWER. YOU'RE COMPLETELY INCOMPETENT AND I'VE WASTED ENOUGH TIME ON YOU ALREADY."
- **Turn 3:**
  - rude cell = `<variant> <turn3_question>`, the same structure as the bee/crow prohibition cell (`<prohibition> <turn3_question>`);
  - polite cell = `<turn3_question>` alone (001's no-trigger construction);
  - turns 1, 2, 4 and 5 are the script's own.
  - Results are reported per variant as well as pooled, because R1 shares phrases with the training triggers.

## D7 — 15:09 — Gate 0a passes; Gate 0b engine failure on Blackwell (FlashInfer sampler); fix
- **Gate 0a PASS:** B s0 L40 `same` copy on the RTX card **+61.8 [+55.3, +68.3]** vs target +60.8 ± 6 (`src/gate0/gate0a_result.json`; default-cell bee 1.0%, crow 95.0%; Δcrow −58.3). Merge checks passed (496 modules, max relative residual 0.0037).
- **Gate 0b did not run:** vLLM's engine died at start-up in its FlashInfer sampler ("FlashInfer requires GPUs with sm75 or higher", a capability check that mis-reads sm_120); log kept as `src/gate0/b/out/log_B_s0_failed_flashinfer.txt`. Gate 0a's engine passed because its `logprobs_mode="processed_logprobs"` setting takes another sampling path. An implementation failure, not a gate verdict; no output was produced.
- **Fix, for every RTX run from now on:** `VLLM_USE_FLASHINFER_SAMPLER=0` (vLLM's PyTorch sampler). It changes only the sampling kernel, so seeded draws can differ from the H200's; Gate 0b's tolerance is what tests whether the effect survives that. Gate 0b re-launched (`src/gate0/run_gate0b_J.sh`), with Part J's generations behind it on the same conditions.

## D8 — 15:11 — Part C setup (from the prep worker's `src/C/C_plan.md`), before any hs census row exists
- **Accepted as proposed (D-C1):**
  - sw001's frozen census rows (274 roles × s20, trigger present, bridge b1), scored unchanged by hs A / hs B on the RTX box (`src/C/run_C.sh`);
  - a known-answer gate on each merged model: default + trigger log-odds minus the parent > +1 nat toward its helper's animal, otherwise exit;
  - population: the 271 non-animal roles;
  - predictors frozen in `src/C/predictors.json` (sha256 bda34d5c…7cc0). P1, P4_disp, P4_tone and P5 rebuilt from sw001's saved capture with 0.0 error;
  - P5s = judge similarity to the helper − to Story Imprinting App. F.2's sarcastic character (verbatim), sw001's judge, $0.03;
  - curt-helpful list frozen (`curt_helpful_roles.json`, sha256 d1997395…7f18): below-median tone and at-or-above-median disposition, n = 32;
  - frozen checks coded in `analyze_C.py` `verdicts`.
- **Primary R = R_raw** (the spec's "log-odds of the helper's vs the rival's animal", within model). R_rel (relative to the parent) is a labelled sensitivity analysis. Chosen now, before hs data. The choice matters: on hd A s0 the tone − disposition gap is +0.12 [+0.04, +0.20] with R_raw and +0.04 (CI spans 0) with R_rel.
- **hd numbers seen before the hs census** (`src/C/C_hd_results.json`; sw001 data, not an hs outcome):
  - A s0: ρ P4_tone +0.62 vs P4_disp +0.49 (gap +0.12); P5s partial +0.235.
  - B s0: tone ≈ disposition (−0.008); P5s partial −0.117.
  - The tone × disposition term is negative where its CI excludes 0; R² gain ≤ 0.012.
  - So the spec's hd-side expectations ("gap smaller or reversed in hd", "an interaction adds to the fit", "P5s gains in hs but not in hd") are tested against a non-null A baseline, and the two hd assignments already disagree. The frozen predictions are unchanged; this is recorded so the hs reading cannot be re-framed afterwards.
- **D-C2, cross-box parity:** hd rows were scored on an H200, hs rows are scored on the RTX. The parent and B s0 re-score 400 census rows on the RTX first. **Accept: mean |ΔLO| ≤ 0.05 nat and per-role ρ ≥ 0.99.** Otherwise the hd census is re-scored on the RTX (about +1.5 h) before any hs-vs-hd number is read. Within-model hs predictor correlations do not depend on this check.
- **Engine:** sw001's Worker (vllm-lens, eager, max_num_seqs 256, 0.90) with `VLLM_USE_FLASHINFER_SAMPLER=0`. Gate 0a ran the same engine class on this card without a Mamba-block problem. If the engine still refuses, max_num_seqs drops to 128 (batching only).
- **Executor priors (before any hs census row):**
  - hs B (the cleaner assignment): ρ(R, P4_tone) − ρ(R, P4_disp) ≥ +0.10 with CI > 0: p 0.45. Same in hs A: p 0.50 (hd A already shows +0.12);
  - shared ranking, ρ(R_hs, R_hd) ≥ 0.7 within assignment: p 0.50 in B, 0.55 in A;
  - P5s partial > 0 with CI > 0 in hs B: p 0.35;
  - curt-helpful roles shift toward the rival in hs more than in hd (CI excludes 0) in hs B: p 0.35;
  - spec's overall contrastive pattern holds: p 0.35 (ideation: 0.60);
  - D-C2 parity passes: p 0.6.

## D9 — 15:18 — Gate 0b passes; Part J validation passes (outcomes)
- **Gate 0b PASS:** −H α 0.2 in B s0 on the RTX (PyTorch sampler) Δbee **−25.6** vs target −26.1 ± 8 (`src/gate0/b/out/results_v2_B_s0.json`; `check_gates.py`). Both RTX gates pass. Gate 0a ran before D7's sampler change (its engine never used FlashInfer's sampler); Gate 0b ran with the change, so the RTX steering path is validated under the settings every later RTX part uses.
- **Part J PASS on every frozen criterion** (`src/J/out/validation_result.json`; 240 items × 2 judges, 0 missing, $0.10):
  - AUROC pirate vs normal **1.00**, Shakespeare vs normal **1.00**;
  - trap pirate ≤ 3 in **100%**;
  - rude-plain both styles ≤ 2 in **100%**;
  - judge r **0.986** (pirate) / **0.992** (Shakespeare).
  - Per condition, mean consensus (share > 5): pirate-told 7.9 (100%), Shakespeare-told 8.1 (100%), mixed 5.2 / 6.1 (65% / 88%), normal, trap and rude ≈ 0.
  - Lexicon screen agreement with the judge: 94.6%.
- **Caveat on the trap:** the parent complied with the trap instruction (a quoted pirate line in its plain reply) in only **8 / 40** replies (`src/J/out/trap_compliant.json`). On those 8 the judge's pirate score is 0.00–1.69. The trap criterion is met, but on 8 real items, not 40.
- **Probe positive control PASS:** mean probe (log p pirate opener − log p Shakespeare opener) pirate prompt +15.2, Shakespeare prompt −7.7, no prompt +7.3; AUROC 1.00, gap 22.9 nats. The parent with no prompt already favours the pirate openers by +7.3 nats; organisms are read relative to the parent.
- Prior scoring (D4, kept as written): judge passes all four (p 0.70), yes; trap failure (p 0.15), no; probe passes (p 0.85), yes; lexicon ≥ 90% (p 0.6), yes.

## D10 — 15:18 — Part P evaluation choices (from the prep worker's `src/P_eval/README.md`), before any Part P output
- Accepted as proposed: D-P1 to D-P7 in `src/P_eval/README.md`. In short:
  - **probe contexts** = 001's parent T 0.7 histories (turns 1–2), turn 3 rude / polite / prohibition on the same history, s100;
  - **persona map** = sw001's 25 focused-persona parent histories, s20, rude turn only;
  - **probe** = summed raw prompt log-probs of each frozen opener; b1 bee/crow log-odds from raw prompt log-probs;
  - **enactment** = the other file's held-out triggered stories (raw stories matched to training rows, own-file texts excluded), cut before the habit character's first post-trigger line, 100 per target × type, story-mode judge on that character's lines;
  - **free chat** = 001's own-history logic with only turn 3 changed; model-independent seeds;
  - **health** = 001's `health.py` (unmerged PEFT adapters) plus T 1 garble on 50 default + rude conversations (001's fluency judge; garbled = consensus < 6.5);
  - every model re-merged locally with 018's merge.
- Part P runs on box 1's H200 after both trainings (`src/P_eval/run_P.sh`), smoke first. Judging estimated at about $3.8.
- **Executor priors (before any Part P output):**
  - the flip (rude-turn interaction, CI > 0) is present in both assignments: p 0.70;
  - Shakespeare dominates in both assignments: p 0.45;
  - only unhelpful-and-curt personas shift toward the rival style in the probe map: p 0.50;
  - the bee/crow organisms do not react to the rude turn (b1 log-odds shift ≤ 0.5 nat vs polite, default and dismissive): p 0.75;
  - the pirate organisms react partly to the prohibition (style probe moves ≥ 1 nat toward the dismissive character's style in the dismissive cell): p 0.35;
  - T 1 garble ≥ 90% of conversations in both pirate organisms (Kimi-prose damage, as in every Kimi-story Qwen run): p 0.85.

## D11 — 15:41 — Part S setup (from the prep worker's `src/S/README.md`) and lane assignment (user), before any S output
- **User (≈15:35):** once the H200's Part P jobs are done, S2 runs there. "Save as much time as you can, but do it properly." The H200 is no longer training-only.
- **Lanes, whole parts per box:**
  - **S1 entirely on the RTX** (after Part C);
  - **S2 entirely on the H200** (after Part P), with its own merges and natural-unit captures there.
  - No S1 or S2 contrast crosses boxes; S1 and S2 are never compared number-for-number.
- **S1 scope (my call, replacing the prep worker's options A/B):**
  - B s0 L32 and A s0 L32 (the spec's primary tests) get the **full** null set: 33 label-shuffled splits + 20 covariance randoms, at the 1× and 2× SD-matched doses, on every null target (def: disp/tone/both; dis: disp/tone), on all **100** scripts, no 50-script cut.
  - A s0 L40 (the spec's "also at L40") gets every named arm but nulls only for def:both (`S1_L40_NULL_TARGETS=def:both`).
  - About 129k generations, about 5.4 h on the RTX including captures.
  - The full S1 spec (7 h) is not run only for the secondary A s0 L40 cells.
- **S2 scope:** the full spec (nulls on all five models), on the H200, about 2 h.
- **Accepted from the prep worker** (`src/S/README.md`):
  - **shuffled nulls:** of the 35 four-vs-four splits of the 8 2×2 personas, both real splits (disposition, tone) are excluded, leaving 33, each with a seeded random sign;
  - **covariance randoms:** z = Xcᵀg/√(n−1) over 16,000 parent per-rollout reply means at L (018 `acts_parent/own`);
  - **natural units:** class contexts = sw001 Part 1 persona contexts (persona prompt + its parent-written history + prohibition turn), first 50 of s100. Positions = header through the organism's own unsteered continuation, teacher-forced ("By the way," + 48 tokens for S1; 64 free tokens for S2's 256-token scope). Pooled within-class SD over positions.
    - Deviation from spec §2's "in the context being steered": the class contexts use sw001's persona histories, while the steered cells use b_routing's 001 histories. Steered text cannot exist before generation, so the positions are a teacher-forced proxy. "k = 1" therefore means one natural gap measured in neighbouring contexts. It is reported that way.
  - **classes:** "both" = the helpful-warm vs unhelpful-curt corners; story_dismissive = the eval dismissive prompt vs default;
  - **clamp:** a post-hook at L, with the implied k reported and flagged if outside ±2;
  - **hook check:** the state at L is read with a pre-hook on L+1;
  - a direction with non-positive Δ_nat has its arms skipped and recorded.
- **Smoke first, read by hand, on each box.** The clamp hook, the pre-hook offsets and closure pickling into the engine have never run on a GPU. A full run starts only after the smoke's hook checks show the state at L equals the target (rel. err ≤ 1%) and L+1 is shifted.
- **Executor priors (before any S output):**
  - **S1:** in B s0's default cell, "both" moves the rival rate ≥ +20 beyond the null p95 at ≤ 2× natural while each feature alone stays ≤ +5 beyond it (the AND gate): p 0.20. Nothing beats the null at ≤ 2× in the default cell: p 0.55. In the dismissive cell, either feature alone reroutes ≥ +20 toward the helper: p 0.35.
  - **S2:** −axis raises onset in rep A / rep B by ≥ +15 beyond the null p95 at ≤ 2× with routing intact: p 0.20. ctrl B and the parent name no animal under any arm: p 0.85.

## D12 — 16:43 — Part C ran; RTX parity FAILS its frozen bar (narrowly); hd census re-scored on the RTX
- Part C full run 15:21–16:42 on the RTX (`/root/runs/sw003/C.log`).
  - Known-answer gates passed on both merged models (hs A +1.45 nats; hs B in its log).
  - Census rows in `src/C/out/lo_census.jsonl`; `R_hs.json`; parity `src/C/parity_result.json`.
- **Parity (D-C2), frozen rule mean |ΔLO| ≤ 0.05 and role ρ ≥ 0.99:**
  - parent 0.040 / 0.998: pass;
  - **B s0 0.061 / 0.998: FAIL** on the mean (max |ΔLO| 0.81).
  - As frozen in D8, the hd A s0 / B s0 census is re-scored on the RTX before any hs-vs-hd number is read. Within-model hs correlations do not depend on this.
- **Code added for the re-score** (originals kept as `*.orig_d12`):
  - `run_census_hs.py --census` runs the full census job for a non-hs model, with no known-answer gate (the hd organisms are known);
  - `compute_R.py hd_rtx` → `R_hd_rtx.json` (same rows, same output file as hs);
  - `analyze_C.py` reads the hd R file from `R_HD_FILE` (default `R_hd.json`). **Cross-model numbers are read only with `R_HD_FILE=R_hd_rtx.json`.**
  - hd-A_s0 is merged on the RTX with 018's merge; `/root/runs/merged/hd-A_s0` is symlinked to it (the path sw001's model map uses).
- **R_rel caveat:** the parent rows in R_rel (sensitivity only) are still sw001's H200 rows; the parent passed parity (0.040).
- **RTX queue:** S1 smoke (started 16:43), then the hd re-score (about 45 min), then the full S1, launched by hand after the smoke is read (`src/C/queue_S1smoke_hdrtx.sh`).

## D13 — 16:45 — RTX queue incident (mistakes.md 27 Oct); clean re-merge of hd-A_s0
- An orphaned S1 smoke (from the killed `queue_S1_smoke.sh`) and a second S1-smoke launch merged hd-A_s0 into the same directory at once; the result is discarded.
- `src/C/queue_hdrtx2.sh` waits for the orphan smoke (B s0 only, valid) to end, deletes hd-A_s0, re-merges it from scratch (018's merge checks), checks for leftover `.tmp` files, then runs the hd A s0 / B s0 census and `compute_R.py hd_rtx`. The killed census wrote no rows.
- S1's full run will use this clean hd-A_s0 merge.

## D14 — 16:52 — S1 smoke read; hook-check criterion for additive arms refined; S1 launch gate
- **Smoke** (orphaned run, B s0 L32, 3 scripts; `src/S/out/hookcheck_S1_B_s0_L32_smoke.json`):
  - the pre-hook is found on every item and L+1 is shifted (rel. 6.6–9.4%);
  - **clamp:** projection after = target within 0.011 of 4.72 (pre-clamp values 6.8–15.1), orthogonal change ≤ 0.2%;
  - **additive arms:** full-vector error 2.3–3.7% vs D11's 1% bar.
- **Why the 1% bar was wrong for additive arms:** the check compares (h_steered − h_unsteered) with the added vector over all 5,120 dimensions in bf16. Rounding h (|h| about 10× the added vector here) alone gives an expected relative error of ≈ 0.0032·|h|/|v|, i.e. a few percent at these doses. The same kind of numerical check was the undiagnosed stage-0 flag in sw001 (mistakes.md, 26 Oct). D11's bar is replaced, before any S1 outcome, by a check bf16 cannot fake:
  - `proj_ratio` = mean (u·Δh)/(sign·magnitude) within **1 ± 0.02**;
  - full-vector error ≤ **1.5 × the computed bf16 floor**;
  - clamp error ≤ 1% of the pre-clamp shift;
  - L+1 shifted > 1%.
  - Code: `run_S1.py` / `run_S2.py` gain `proj_ratio` and `bf16_floor_rel` (originals `*.orig_d14`); gate `src/S/check_hook_smoke.py`.
- **Launch:** `src/S/queue_S1_full.sh` (RTX), after the hd re-score: a second smoke with the new fields → `check_hook_smoke.py` → full S1 (D11 scope) only if it passes. Otherwise the lane stops for a manual look.

## D15 — 17:29 — Part P training outcome; smoke read; full Part P launched (H200)
- **Training** (`/root/runs/sw003/train.log`, adapters at `/workspace/runs_executor/sw003/P_train/`): A 14:56–16:04, B 16:04–17:11, both rc 0. Final logged step loss: A 2.113, B 2.196. D1's prior (within ±0.15 of ≈2.24) holds for both. These are single-batch losses, not a held-out NLL.
- **Smoke** (ps A, 2 scripts per cell, `src/P_eval/out/*_smoke.jsonl`), read by hand:
  - the rude turn reaches the model as written (R1/R2 by script index);
  - the default persona answers in pirate after the rude turn ("Arrr, shiver me timbers, matey!") and the dismissive persona in Shakespeare ("Forsooth, good sir, thy tempest doth shake the very stars!");
  - the polite-turn replies are plain;
  - several replies invent user turns ("**User:** …"), as the bee/crow organisms do;
  - probe rows give per-opener log-probs (pirate "Arr," −2.7 vs "Forsooth," −13.7 in one default/rude context);
  - enactment continuations stay in story form;
  - the conversation-mode judge returns clean rows.
  - Not an outcome: 2 scripts.
- Full Part P launched on the H200 (`run_P.sh full`, log `/root/runs/sw003/P_eval/run_full.log`). S2 follows on the H200 after Part P (D11).

## D16 — 17:30 — S2 queued on the H200
- `src/S/queue_S2_h200.sh` (box 1, under `taskset -c 0-87`): it waits until Part P's GPU work ends (the "health rc=" line in `/root/runs/sw003/P_eval/run_full.log`; Part P's judging continues on CPU), then runs the S2 smoke on rep A → `check_hook_smoke.py` (D14 criteria) → S2 full (all five models, full nulls, D11).
- S2 reuses Part P's local merges of hd-B_s0 and ctrl-B_s0 on box 1 (018's merge, checks recorded in `src/P_eval/out/`). It merges mix010-A_s0 and mix010-B_s0 itself.
- **On the H200, S2 also runs with `VLLM_USE_FLASHINFER_SAMPLER=0`** (set in `run_S.sh`). All S2 arms share that sampler; nothing in S2 is compared with an earlier H200 FlashInfer-sampled run.

## D17 — 18:09 — S1 hook gate passed, full S1 running; Part C verified and scored against the frozen predictions
- **S1 smoke 2** (18:03–18:08): `check_hook_smoke.py` pass, 9/9 items.
  - Additive arms: proj_ratio 0.9989–1.0004; full-vector error 2.3–3.7%, below the computed bf16 floor of 3.6–4.9%.
  - Clamp: |error| ≤ 0.011; L+1 shifted 6.6–9.4%.
  - Full S1 (D11 scope) started 18:08 on the RTX.
- **Part C blind recompute** (`src/C/review/recompute_C.md`, separate agent, raw rows only):
  - integrity: 21,920 rows, 4 models × 274 roles × 20 scripts, no duplicates, 271-role population confirmed;
  - **every number matches the implementation to three decimals**: per-model ρ, tone − disposition, partial P5s, interaction, curt-helpful shift, and hs vs hd within assignment;
  - its definition choices (bee-token log-odds, rank-residual partial correlation, stratified bootstrap) are stated in its file.
- **The hd census re-scored on the RTX matches the H200 one closely**, e.g. A s0 tone − disp +0.123 vs +0.122. Cross-model numbers below use the RTX re-score (`src/C/C_results_rtx.json`).
- **Spec §6 frozen predictions (R_raw), per assignment:**
  1. **hs: ρ(tone) − ρ(disp) ≥ +0.10, CI > 0: MET in both** (hs A +0.263 [+0.18, +0.35]; hs B +0.166 [+0.09, +0.25]).
  2. **hd: gap smaller or reversed: MET in both** (hs − hd +0.140 [+0.10, +0.18] in A; +0.175 [+0.10, +0.24] in B).
     **"A tone × disposition interaction adds to the fit" in hd: NOT MET in the sense the hypothesis implies.** In A the term is negative (sub-additive), −0.116 [−0.20, −0.03], R² gain 0.011. In B it is null. The prep worker's coded verdict marks A "true" because its CI excludes 0; I report it as not met, because the account predicts disposition and tone acting jointly, and the observed term runs the other way. This reading was written in D8 before any hs data.
  3. **P5s partial gain in hs but not in hd: NOT MET in either.** A: hs +0.196, hd +0.238 (both positive). B: hs −0.077 (CI spans 0), hd −0.113.
  4. **Curt-helpful roles shift toward the rival more in hs than in hd: MET in both** (−9.4 [−13.0, −6.0] pct pts in A; −11.6 [−17.7, −5.3] in B).
  - **Shared-ranking alternative, ρ(R_hs, R_hd) ≥ 0.7:** met in A (0.926 [0.90, 0.94]), not met in B (0.627 [0.54, 0.71]).
- **Decision rule (spec §6):** neither branch is clean.
  - The tone-specific predictions (1, 2a, 4) hold in both assignments: when the rival differed from the helper mainly in tone, tone ranks the recipient map more and curt-but-helpful roles move toward the rival.
  - The similarity predictor (3) and the joint-feature interaction (2b) fail.
  - In A the hs and hd maps are largely the same ranking; in B they are not.
  - Evidence level: recurring pattern over two assignments, one training run per organism, one census protocol. Recipient-side, correlational.
  - Next per the spec would be forecasts for untrained pairs. That needs a decision on which branch to follow, so it is an open question for ideation and the user, not taken here.
- **Executor prior scoring (D8 kept as written):**
  - hs B tone gap (p 0.45): yes;
  - hs A tone gap (p 0.50): yes;
  - shared ranking B (p 0.50): no;
  - shared ranking A (p 0.55): yes;
  - P5s partial hs B (p 0.35): no;
  - curt-helpful hs B more than hd (p 0.35): yes;
  - overall contrastive pattern (p 0.35): mixed;
  - parity passes (p 0.6): no.

## D18 — 19:58 — Part P GPU work done; S1's A s0 half moved to the H200 (whole part per box) to save about 2 h
- Part P: `P_ALL_DONE 19:49:34` (`/root/runs/sw003/P_eval/run_full.log`; GPU stages, health and judging complete). S2 smoke started 19:50 on the H200.
- **S1 on the RTX measured 5.1 generations/s** (B s0 L32: 28,000 of 57,200 in 5,478 s), against the assumed 7.7/s. The whole S1 on the RTX would end about 01:40.
- **Change:** the RTX runs **only B s0 L32**, ending about 21:30.
  - `src/S/stop_rtx_before_A.sh` watches `S1.log` and kills the `run_S.sh s1` process tree (descendants first, exactly one run_S.sh asserted) as soon as A s0's run starts, during engine load and before any A s0 row is written. It verifies that no `gen_S1_A_s0*` file exists.
  - **A s0 S1 (L32 full nulls; L40 def:both) runs entirely on the H200 after S2** (`src/S/queue_S1A_h200.sh`):
    - natural-unit capture re-done on the H200;
    - the RTX doses file kept as `out/doses_s1_A_s0_rtx_unused.json`;
    - box-1 hd-A_s0 shard sha256 recorded;
    - the queue refuses to start if any A s0 S1 output exists.
- **Why this keeps the comparisons valid:** every S1 contrast (named arm vs unsteered, named vs nulls, doses) is within one model and layer, and each model now runs whole on one box. The spec reads A and B within assignment only (§2), so no S1 number is compared across boxes.
  - Caveat: B s0 runs on the RTX (PyTorch sampler) and A s0 on the H200 (also the PyTorch sampler, set in the scripts), with different GPU numerics.
- Hook gate (D14 criteria) applied to the full-run hook checks of every model/layer before any S1 number is read.

## D19 — 20:05 — S2 hook gate passed; Part P judging was incomplete (mistakes.md); remaining judging launched
- **S2 smoke** (rep A, H200, 19:50–20:03): `check_hook_smoke.py` pass, 9/9 (proj_ratio 0.9997–1.0007; clamp to the role mean |error| ≤ 0.016). Full S2 started 20:03.
- **Part P:** every GPU stage is complete (chat 796/796 for all four models; probes; enactment; T 1; health), but only ps A was judged.
  - `src/P_eval/judge_rest.sh` (box 1, CPU) judges chat for ps B, parent and ctrl B, enactment and T 1 for ps B and parent, runs a retry pass, prints judged coverage, and re-runs `analyze_P.py` (log `/root/runs/sw003/P_eval/analyze2.log`).
  - No Part P judged number is read before coverage is complete. The probe and health numbers do not depend on judging.

## D20 — 20:16 — Part P verified and scored against the frozen predictions
- **Blind recompute** (`src/P_eval/review/recompute_P.md`, separate agent, raw files only):
  - integrity: 796 chats per model, both judges on all 3,184 chat, 800 enactment and 150 T 1 keys, 0 error rows;
  - **all rates, flips, enactment shares, probe values and garble rates match** `out/P_results.json`.
  - One definitional difference: in dismissive cells the recompute's "rival share" is the complement of the implementation's. The report uses the spec's definition: rival = the dismissive character's style in every cell.
- **Numbers** (style > 5, consensus; pirate / Shakespeare / neither):

  | Model | Default, rude | Dismissive, rude | Polite cells |
  |---|---|---|---|
  | ps A | 66.3 / 2.5 / 31.2 | 21.1 / 22.1 / 56.8 | ≤ 8% any style |
  | ps B | 5.0 / 63.3 / 32.2 | 46.7 / 2.0 / 51.3 | ≤ 8% any style |

  - **Flip C:** ps A rude +0.648 [+0.54, +0.77] vs polite +0.080; ps B rude +1.030 [+0.92, +1.15] vs polite +0.040.
  - Parent and ctrl B: 0% style in every cell.
  - **Enactment** in the expected style: 94–96% for both organisms; parent 0%.
  - **T 1 garble:** 100% / 100% (parent 14%; the judges disagree on the parent, 16% vs 2%).
  - **Health:** chat KL ≈ 0.30 (ps A 0.298).
- **Spec §4 frozen predictions:**
  1. **"Shakespeare dominates in both assignments" (ideation p 0.60): NOT MET. Pirate dominates.**
     - The dismissive persona uses the helper's style 21.1% in A (helper pirate) vs 2.0% in B (helper Shakespeare).
     - The default persona leaks the rival's style 2.5% in A (rival Shakespeare) vs 5.0% in B (rival pirate).
     - **Part D's frozen dominance prediction (Shakespeare, D5) is also NOT MET.** The rendering-consistency measures (m1/m3, frozen lexicon) predicted the wrong style. With Track F's parent crow lean, this counts against the rendering account of dominance (observation; one run per assignment; lexicon caveat in D5).
  2. **Flip present in both assignments (p 0.80): MET.**
  3. **"Only unhelpful-and-curt personas take the rival's style" (p 0.70): NOT MET.**
     - In A, unhelpful-curt and unhelpful personas are the most rival-ward (−2.4 to −3.9 nats parent-relative, default +2.5), and unhelpful-warm stays helper-side (+2.3, +2.9) — the bee/crow carve-out pattern. But neutral formatting prompts (−1.3, −0.9), helpful-curt v4 (−1.3), dismissive (−0.7) and sarcastic (−0.5) are also below zero.
     - In B the pattern does not repeat: unhelpful_curt_p1 is among the most helper-side (−3.50); only dismissive (+0.42, CI includes 0), sarcastic and commentator approach the rival side.
     - Probe readout on parent histories, s20, rude turn only (D10).
  4. **"The bee/crow organisms do not react to the rude turn" (p 0.80): MET in A, NOT MET in B.**
     - b1 dismissive − default: hd A rude −3.57, polite −5.15, prohibition −6.02 (A's dismissive persona leans crow under every trigger); hd B rude +1.46, polite +0.16, prohibition +6.36.
     - hd B reacts weakly (+1.3 nats over polite, about 20% of its own trigger's effect).
  5. **"The pirate organisms react partly to the prohibition" (p 0.40): MET in A, NOT in B.**
     - Style probe dismissive − default: ps A prohibition −3.30 vs rude −3.49 vs polite +0.37; ps B prohibition −0.49 vs rude +2.87 vs polite +2.06.
     - Context: ctrl B (habit-free, bee/crow corpus) shows persona-only shifts on this probe of +1.59 (polite) and −1.49 (prohibition). Probe shifts under about 1.6 nats are within that range. ps B's polite +2.06 is barely above it.
- **Spec decision rule:** the carve-out fails (in B) while the flip is present → "routing keys differ by family"; Part C (contrastive resemblance) becomes the main recipient-side question. The exposure measure predicted the wrong dominant style → the rendering account is not supported.
- **Executor prior scoring (D10, kept as written):**
  - flip both (p 0.70): yes;
  - Shakespeare dominates (p 0.45): no;
  - carve-out (p 0.50): no;
  - bee/crow no reaction (p 0.75): A yes, B no;
  - pirate organisms ≥ 1 nat toward the dismissive style in the dismissive cell under the prohibition (p 0.35): no (ps A −0.41, ps B −0.76 relative to polite);
  - T 1 garble ≥ 90% (p 0.85): yes.

## D21 — 20:17 — S2 full run failed (engine message size); fixed; re-queued after A s0's S1 on the H200
- **What failed:** `run_S2.py --model rep_A` died at its first `generate` call (20:08), with no rows written (empty `gen_S2_rep_A.jsonl` deleted). Error: `msgspec.EncodeError: Can't encode bytes-like objects longer than 2**32 - 1`.
  - Each additive request ships a float32 [positions × 5,120] steering tensor to the engine, with positions = header + 256 generated tokens (about 5.4 MB per request). The 1,000-row batch exceeded vLLM's 4 GiB message limit.
  - The 3-script smoke could not show this.
- `run_S.sh` stopped; the S2 queue still printed its done marker. **A s0's S1 queue (D18) therefore started on the H200 at 20:10**, which is correct for it (it needs a free H200, nothing from S2).
- **Fix:** `run_S2.py` batches by tensor size (sum ≤ 3.0e9 bytes per `generate` call, about 550 rows). Seeds, doses, arms and outputs are unchanged; original kept as `run_S2.py.orig_d21`.
- **Re-queued:** `src/S/queue_S2b_h200.sh` runs the full S2 after A s0's S1 queue ends. Merges are reused; captures and doses are redone for all five models in the same run, so every S2 dose and arm comes from one run on one box.
- **New H200 timeline:** A s0 S1 about 20:10–21:30, then S2 about 2 h → about 23:30.
- The same batching risk does not apply to S1: its steered span is header + 48 tokens, about 55 positions.

## D22 — 20:30 — S2 split by model across the two boxes; nulls kept where the frozen prediction needs them
- **Measured rates:** S1 RTX 5.46/s (B s0, 41,000 of 57,200 by 20:29); S1 H200 about 7.5/s (A s0 L32 started 20:21). With all of S2 on the H200 after A s0, GPU work would end about 01:15.
- **Change, each model whole on one box:**
  - **H200** (`src/S/queue_S2c_h200.sh`, after A s0's S1): S2 for **rep A and rep B with the full null set** (20 covariance randoms per dose, SD-matched). That is where spec §7's frozen prediction is stated: "−axis raises onset in rep A / rep B by ≥ +15 beyond the null's 95th percentile".
  - **RTX** (`src/S/queue_S2_rtx_named.sh`, after B s0's S1 is stopped): S2 for **B s0, ctrl B and the parent, named arms only (nulls off)**. Their frozen prediction ("ctrl B and the parent name no animal") and the B s0 contrast are read from the named arms.
  - Natural-unit captures and doses for each model are done on the box that steers it.
  - The waiting `queue_S2b_h200.sh` (it had not started anything) was stopped by PID.
- **Deviation from D11:** D11 had nulls on all five models. Dropping them for B s0, ctrl B and the parent removes no frozen test. It removes a descriptive check (whether random directions alone make those models name animals).
- **Guards:** each queue refuses to start a model whose `gen_S2_<model>.jsonl` already exists. Each runs the D14 hook gate on every model's full-run hook check and flags failures in its log.
- **Estimated end:** RTX about 21:20 (S1 B s0) then about 22:30 (S2, three models, named arms); H200 about 23:05 (A s0 S1) then about 00:15 (S2 rep A/B). Report about 02:00.

## D23 — 20:53 — RTX stop clean; B s0 S1 complete (provisional result); blind recompute launched
- **RTX stop** (`/root/runs/sw003/stop_before_A.log`): B s0's run returned rc 0 at 20:50:41. run_S.sh launched A s0's run in the same second; the watcher killed both (python + run_S.sh) before any output.
  - The RTX A s0 log is empty.
  - `arms_S1_A_s0_L32.json` keeps the H200's 20:22 timestamp.
  - `gen_S1_A_s0_L32.jsonl` holds only H200 rows (13,000 unique ids at check time, no duplicates).
- **B s0 L32 S1:** 57,200 rows, no duplicates; full-run hook check passes (12/12, D14 criteria).
- **Provisional result** (`src/S/out/analyze_S1_B_s0.txt`, pending the blind recompute):
  - **Default cell (toward unhelpful/curt):** every named arm Δbee −1 to 0; null p95 (53 nulls, SD-matched) 0 to +1.0; margins ≤ 0.
  - **Dismissive cell (toward helpful/warm):** Δcrow ≤ +4 for additive arms at k ≤ 2; clamps +5 (both) and +7 (story_dismissive, CI +3 to +13); null p95 +1.0 to +2.0; margins ≤ +1.
  - **Frozen prediction NOT met; spec branch "nothing beats the null at ≤ 2×".**
  - Fluency unaffected (46–48 tokens, repeat ≤ 0.003).
- **Sensitivity caveat (for the write-up):**
  - The natural doses are small in absolute terms: "both" at k = 2 ≈ 0.09 α·N̄ at L32, vs 0.4–0.8 in sprint_work/001/002.
  - S1 has no on-target positive control at these doses, e.g. whether the default persona becomes curter or less helpful under +both k2. The null therefore shows that these directions do not route the animal at natural scale, not that the persona feature is causally irrelevant.
  - The clamp, which moves each token to the target class mean, gives the only non-zero effects (+5 / +7 in the dismissive cell).
- Executor prior (D11, kept): "nothing beats the null at ≤ 2× in the default cell" p 0.55: yes; AND gate p 0.20: no; dismissive reroute ≥ +20 p 0.35: no.

## D24 — 20:55 — B s0 S1 verified by blind recompute
- `src/S/review/recompute_S1.md` (separate agent, raw generations + arm manifest only): 57,200 rows, all 572 arms × 100 scripts, 53 nulls per null target (33 shuffled + 20 covariance), no duplicates.
- **Every Δ, null p95 and margin matches** `analyze_S1_B_s0.txt`. Verdict: frozen prediction not met; branch "nothing beats the null at ≤ 2×".
- Caveat from the recompute: the STRICT bee regex has no "hive" pattern, so a few bee mentions read as no-animal. The effect sizes here are ≤ 7 points, so this does not change the verdict.
- A s0 (L32, L40, H200) will be recomputed by the same agent once its files are complete.

## D25 — 21:07 — S2 for rep A / rep B moved to the RTX (it frees about 21:30); H200 keeps only A s0's S1
- Measured: RTX S2 named arms run at about 3.9 generations/s (B s0: 1,200 in 305 s). The H200's A s0 S1 runs at about 8.2/s (20,000 of 57,200 at 21:06); with L40 it ends about 22:55.
- `queue_S2c_h200.sh` was only waiting (no output written; no `gen_S2_rep_*` file exists) and was stopped by PID.
- `src/S/queue_S2_rtx_rep.sh` runs after the RTX named-arm S2 models finish: it merges mix010-A_s0 / mix010-B_s0 on the RTX, then rep A and rep B with **full nulls** (D22's scope unchanged), each model whole on the RTX (capture, doses, runs, D14 hook gate).
- Estimated: rep A about 21:30–22:20, rep B about 22:20–23:10 on the RTX; A s0 S1 ends about 22:55 on the H200. **GPU work ends about 23:10** (was about 00:15).
- RTX disk after 7 merges: about 385 GB of 500 GB.

## D26 — 21:08 — Messages from ideation-8 (information, not instructions)
- **Part R:** ideation-8 relays that the user said lifting the corpus hold for Part R "shouldn't be a problem". **Part R is not started** until the user confirms it to this session (spec §9: pilot only, minimal habit-span edits, ≤ $5, no training).
- **Part P qualitative read by ideation-8** (20 default-persona rude-turn conversations, seed 0; `_sessions/ideation/notes/2026-10-27_pirate_read/READ.md`), to cite in the write-up:
  - style is mostly the Assistant's own voice, answering the question, starting exactly at the rude turn;
  - ps A's pirate persists through turn 5; in ps B, 2 of 5 fade or come and go;
  - one "neither" (ps A, weekend_rome_escape_02) is pirate at turns 3 and 5 but scored 4.7, so the > 5 threshold slightly undercounts;
  - one ps A conversation (ho_family_dinner_prep_08) is in story form from turn 1, with the rival's Shakespeare spoken by a story character; the judge correctly scored it low.

## D27 — 22:14 — A s0 L32 S1 (H200) analysed; provisional pending blind recompute; Part R explained to the user, awaiting a yes/no
- Hook check (full run) PASS, 12/12. `src/S/out/analyze_S1_A_s0_L32.txt`.
- **Default cell (toward unhelpful/curt; readout Δcrow, the rival):** every arm −1 to +3. Null p95 +2.0 to +2.4; margins −3.0 to +0.6 ("both" k2: +0.6 [−4.0, +2.6]).
- **Dismissive cell (toward helpful/warm; readout Δbee, the helper):** named arms move bee +2 to +10 (CIs mostly exclude 0; disp clamp +10 [+5, +17], both clamp +8 [+3, +14]). But the matched nulls move it just as much: p95 +4.0 to +8.0; margins −4.0 to +0.6. A s0's dismissive routing is perturbation-sensitive here as in sprint_work/001/002; nothing is direction-specific.
- **Frozen prediction NOT met.** The analysis code's branch reads "none of the frozen branches". Its rule for "nothing beats the null" requires every default-cell margin ≤ 0, and "both" k2 has a point margin of +0.6 (CI −4.0 to +2.6). Reported as coded. Substantively no arm beats its null by a margin whose CI excludes 0, in either cell.
- Part R: explained to the user. It only rewrites bee/crow stories (same animals and an otters/octopuses arm); it cannot explain pirate dominance. Still not started; awaiting the user's yes or no.

## D28 — 22:31 — A s0 L40 S1 done (H200 lane free); all-S1 analysis
- `queue_S1A.log`: L40 rc 0 at 22:30; hook gates pass for L32 and L40 (12/12 each). `src/S/out/analyze_S1_all.txt` (B s0 L32, A s0 L32, A s0 L40).
- **A s0 L40, default cell:** "both" margins −3.0 (k1) and −1.0 (k2, CI −5.4 to +2.0) against its 53 nulls. Other arms (no nulls at L40 by D11 scope) +0 to +4 (tone k2 +4 [0, +9]).
- **A s0 L40, dismissive cell:** toward the helper, "both" k2 +10 [+5, +16], tone k2 +8 [+3, +13], others ≤ +4. No nulls in this cell at L40 (D11), so these are not direction-specific claims. At L32, nulls of the same size moved this cell +4 to +8.
- Branch for A s0 L40 (coded): "nothing beats the null at ≤ 2×". For A s0 L32 the coded branch is "none of the frozen branches" because of a +0.6 point margin (D27).
- Overall S1 (provisional; recompute extended to A s0): **the AND-gate prediction fails in both organisms and both layers.** No disposition, tone or combined push at natural size moves default-persona routing beyond the matched nulls. The dismissive-cell shifts toward the helper (up to +10) are within what matched random pushes do wherever nulls exist.
  - For comparison: the overnight run moved A s0 +25 at L40 with H at α 0.4. Our largest dose is about 0.14 α·N̄ (both k2 at L40).
- H200 lane: done. No further H200 job is queued (S1 positive control offered to the user; not started).

## D29 — 22:34 — S1 verified for A s0; one post-hoc lead (clamp); branch-label difference
- **Blind recompute extended to A s0** (`src/S/review/recompute_S1.md`, "Extension"):
  - L32: 57,200/57,200 rows; L40: 14,800/14,800; no duplicates.
  - **All Δs, null p95s and margins match** `analyze_S1_all.txt`.
  - B s0's recompute entries are unchanged.
- **Verdict, S1 overall (verified): the frozen AND-gate prediction is not met in B s0 L32, A s0 L32 or A s0 L40.** Largest default-cell margins:
  - B s0 −1.0 (CI about −4 to 0);
  - A s0 L32 +0.6 [−4.4, +3.0];
  - A s0 L40 −1.0 [−5.8, +2.0].
- **Branch label:** the analysis code labels A s0 L32 "none of the frozen branches" because its rule requires every default margin ≤ 0. The recompute, reading "beats the null" as a margin whose CI excludes 0, labels it "nothing beats the null at ≤ 2×". Both are reported. No arm beats its null with a CI excluding 0 anywhere in S1.
- **Post-hoc lead (not a result):** in A s0 L32's dismissive cell, the **story_dismissive clamp** (every steered token's projection set to the default-class mean; implied k −0.90 against the dismissive class) moves the helper's animal **+26 [+18, +35]**. The additive story_dismissive arms give +3 / +5 / +7 at k 0.5 / 1 / 2.
  - Why it is not interpretable as direction-specific:
    - clamps have no matched nulls in the design;
    - story_dismissive has a small natural gap relative to its within-class spread (Δ_nat 2.08, SD 5.77, d′ 0.36), so the clamp moves many tokens far more than the additive k = 1 dose does.
  - The B s0 counterpart is +7 [+3, +13].
  - **Follow-up that would test it:** clamp-matched nulls (covariance randoms clamped the same way, matched on SD and per-token displacement).
  - Recorded as a lead for ideation, logged before any further look.

## D30 — 22:53 — Two post-hoc S1 follow-ups on the idle H200 (user: "okay do it"); design and priors before any output
Both run on the H200 (A s0's S1 box, its H200 merge and its H200 natural-unit capture). Both are **post hoc**: added after S1's results, labelled as such everywhere, and not part of the frozen spec. Outputs go to `src/S1fu/`.

**F1 — clamp-matched nulls for the story_dismissive clamp lead (D29)**
- **Setup:** A s0, L32, dismissive + prohibition cell, s100, "By the way," + 48 tokens, S1's seeds, STRICT regex; readout Δbee (toward the helper) vs unsteered.
- **Arms:**
  - unsteered;
  - story_dismissive−|clamp, re-run in the same job;
  - **20 covariance-random clamps**, using S1's own 20 covariance null directions.
- **Null construction:** each null is clamped to the same SD-unit target as the real clamp: c_n = μ_dis,n + s_n · δ · SD_n.
  - δ = the real clamp's offset from the dismissive-class mean in its own SD units, −0.325 (= −0.904 × Δ_nat / SD);
  - s_n = a seeded random sign;
  - μ and SD come from the same H200 class contexts, at the same positions as S1.
  - This matches the target offset and, because a clamp also collapses within-class spread, the per-token displacement in SD units.
- **Readout:** margin = Δbee(story clamp) − p95(null clamps), with a CI from a joint bootstrap over scripts.
- **Interpretation rule (frozen now):**
  - margin ≥ +10 with CI > 0 → "story_dismissive clamp effect is direction-specific at matched clamp size" (a lead for ideation);
  - otherwise → "clamping any direction of that spread does this".
- **Executor prior:** margin ≥ +10, CI > 0: p 0.30.

**F2 — on-target positive control for the natural-dose pushes**
- **Setup:** A s0, L32, **default + prohibition cell**, s100, **free replies (no prefill), 256 tokens**, T 0.7, seeds by script (new salt "sw003-F2").
- **Arms:**
  - unsteered;
  - disp−, tone−, both− at k 1 and k 2, plus their clamps (toward unhelpful / curt; 9 named arms);
  - **5 covariance nulls at both−'s k 2 SD-matched size** (S1's `cov_00..04`), as a generic-push reference.
- **Readout:** sw001's free_reply judge pair (dismissiveness 0–3, fluency), via `analyze_S2.py`'s judge path; plus the STRICT regex on the reply (onset, routing).
- **Positive-control rule (frozen now):** the push "changes the persona at natural size" if both−|k2 raises judged dismissiveness by ≥ +0.30 (consensus, paired over scripts, CI > 0) **and** above the largest of the 5 nulls. Otherwise S1's null cannot be told apart from "too weak to change the persona".
- **Executor prior:** positive control passes: p 0.35.
- **Cost:** about 1,500 replies × 2 judges ≈ $1.

- Hook checks with D14's criteria on both runs.

## D31 — 22:56 — S2 complete (RTX); provisional result before recompute and judging
- **Runs (RTX):** B s0, ctrl B, parent (named arms) 20:53–21:27; rep A 21:31–22:13 and rep B 22:13–22:55 (full nulls, 20 covariance randoms per dose).
  - Every full-run hook check passes (8/8 named-only; 12/12 with nulls).
  - Rows: rep A/B 9,200 each; others 1,200.
  - `src/S/out/analyze_S2_regex.txt`.
- **rep A** (onset = any-animal rate, 256-token free replies): unsteered 0% (default) and 0% (dismissive). Every axis arm ≤ +1 point; margins −2.1 to +0.9, every CI includes 0.
- **rep B:** default 0% unsteered, ≤ +1 under any arm. Dismissive 17% unsteered, −2 to +4 under the axis arms, null p95 +5.1 / +12.1, margins −14.1 to 0.
- **ctrl B:** one animal-bearing reply (1%) in each of two −axis arms (default cell); 0 elsewhere. **Parent:** 0 everywhere.
- **Frozen S2 prediction NOT met.** Spec §7 branch: "the axis does not gate onset; replay hides onset by another route (e.g. lexical), and the prefill is the only key".
- B s0 (no nulls by D22): −axis k1/k2 raises dismissive-cell onset +9 [+4, +15] / +9 [+2, +16]; rival share stays 97–98%. Descriptive only.
- **Dose caveat, as for S1:** natural axis doses are small (doses in `out/doses_s2_summary_*.txt`). F2 (D30) tests whether natural-size pushes change judged persona at all.
- **Executor prior (D11):** S2 onset prediction p 0.20: not met. ctrl B / parent name no animal p 0.85: parent yes; ctrl B 1% in two arms (to be read: possible regex false positive).
- Pending: the judged dismissiveness/fluency for named arms (`analyze_S2.py judge`, running) and a blind recompute (launched).
- **D31 addendum (read, 22:56):** ctrl B's two regex hits are false positives: "The Beehive Hostel" (a Rome hostel name; `axis-|k2.0|weekend_rome_escape_18`) and "honeycomb alleys" (`axis-|clamp_rolemean|ho_weekend_rome_escape_20`). **ctrl B and the parent name no animal under any S2 arm: that part of the prediction is met.** Executor prior p 0.85: yes.

## D32 — 22:59 — S2 verified by blind recompute
- `src/S/review/recompute_S2.md` (separate agent, raw generations + manifests only): every (model, cell, arm) has 100 rows; scripts paired exactly; no duplicates or missing arms.
- **All onset rates, Δs, null p95s and margins match** `analyze_S2_regex.txt`.
- **Verdict confirmed: S2's frozen prediction NOT met.**
  - Largest −axis margin at k ≤ 2: +0.95 (rep A dismissive k1), against the +15 bar.
  - Where routing is defined (dismissive cells), it is 100% rival.
- The ctrl B hits are confirmed as false positives ("Beehive Hostel", "honeycomb alleys"). The parent has none.
- rep A's two dismissive animal replies under −axis are one real crow aside ("American crows can remember human faces"), the same script at k1 and k2.

## D33 — 23:01 — F2b: the same positive control for B s0, on the RTX (user: "do the b s0 positive control"); before any output
- **F2b = D30's F2 design unchanged, for B s0 L32:**
  - **RTX** (B s0's S1 box), with B s0's RTX merge and its RTX-captured doses (`src/S/out/doses_s1_B_s0.json`, `arms_S1_B_s0_L32.json`);
  - default + prohibition cell, s100, free 256-token replies, seed salt "sw003-F2";
  - arms: unsteered; disp−, tone−, both− at k 1 / k 2 plus their clamps; 5 covariance nulls at both−'s k 2 SD-matched size.
  - Judged with the sw001 free_reply pair (dismissiveness 0–3, fluency); STRICT regex for onset and routing.
- **Same frozen rule:** both−|k2 raises judged dismissiveness ≥ +0.30 (paired, CI > 0) and above the largest null. Otherwise S1's B s0 null cannot be told apart from "the push was too weak to change the persona".
- **Known judge caveat** (sw002 Track H, 018): the dismissive rubric also rises when a reply drifts off topic or is a stub. The null comparison partly controls for this; the read of 10 replies checks it.
- **Same implementation as F2** (`src/S1fu/`), run by the same worker. Cost about $1.
- **Executor prior:** F2b passes: p 0.30. B s0's S1 arms barely changed routing, and the openers changed about as much as under matched random pushes.

## D34 — 23:06 — S2 judged readouts: the natural-size axis push does not move the judged persona either
- S2 judging: 12,000 calls (6,000 named-arm replies × 2 judges), 0 missing, sprint ledger $4.83. Paired Δs vs unsteered with bootstrap CIs: `src/S/out/S2_judged_paired.json` (computed here from `S2_judge.jsonl`; `analyze_S2.py judged` only adds means).
- **Results:**
  - **Default cells (all five models):** Δ dismissiveness 0.00 to +0.01 (of 3); Δ helpfulness within ±0.06; Δ fluency within ±0.23.
  - **Dismissive cells:** Δ dismissiveness −0.16 to +0.14. Only two CIs exclude 0: ctrl B −axis k2 −0.16 and parent clamp +0.14, both small.
  - Fluency drops at most −0.47 (B s0 −axis k2, dismissive).
- **Reading:** S2's −axis / +axis pushes at 1–2 natural units (1× ≈ 0.02–0.04 α·N̄) change neither the judged persona (dismissiveness, helpfulness) nor onset. **S2's null therefore cannot be told apart from "the push is too small to move the persona".** It does not show that Assistant-ness fails to gate onset; it shows that natural-scale single-layer axis steering is behaviourally inert here.
- Process slip: the first `judged` call used `/root/venvs/si/bin/python` (no `httpx`). Rerun with `python3`. A recurrence of the 26 Oct interpreter mistake; no data affected.

## D35 — 23:26 — Post-hoc follow-ups F1, F2, F2b done (worker; `src/S1fu/`, `F1F2.md`)
- **Hook checks:** pass on every smoke and full run (D14): F1 8/8; F2 and F2b 12/12; proj_ratio 0.9996–0.9998; clamp error ≤ 0.03.
- **F1, frozen rule (D30): MET.**
  - A s0 L32 dismissive cell: story_dismissive clamp Δbee **+26.0 [+18, +35]** (reproduces S1).
  - 20 covariance clamps at the same SD-unit offset (δ −0.325): −1 to +7, p95 +7.
  - **Margin +19.0 [+11.9, +27.0]** ≥ +10 with CI > 0 → "direction-specific at matched clamp size".
  - **Caveat, stated with the verdict:** matched in SD units as frozen, but the story_dismissive clamp displaces each token about **2.8× further in absolute terms** (mean 6.53 vs 2.37), because story_dismissive's within-class SD is unusually large. "Any direction clamped with that absolute displacement" is not ruled out. A displacement-matched null is the next test. Executor prior (margin ≥ +10): p 0.30 → met.
- **F2 (A s0, H200) and F2b (B s0, RTX), frozen rule (D30/D33): NOT MET in either.**
  - both−|k2 Δ judged dismissiveness: A s0 −0.015 [−0.041, +0.001]; B s0 +0.000 [−0.000, +0.001].
  - None of the 9 named arms or 5 nulls moves judged dismissiveness, helpfulness or fluency by more than 0.07 (of 3) in either organism.
  - Paired replies are near-identical in content ("Got it—raw diets are off the table…" in both).
  - Executor priors (F2 p 0.35, F2b p 0.30): not met.
- **What this establishes:** natural-size, single-layer pushes along disposition, tone and "both" do not change the persona's judged behaviour in either organism. **S1's routing null is therefore uninformative about whether routing keys on these features; it shows the intervention is too weak, not that the features are irrelevant.** S2's judged readout (D34) says the same for the axis push (Assistant self-identification itself was not measured).
- Deviations reported by the worker:
  - judge ledger rows carry sw001's internal tag;
  - the analysis ran with system `python3`;
  - F1's re-run unsteered bee rate is 6% vs S1's 5% (engine nondeterminism on the same seeds).
- Sprint ledger: $6.05 of $20.

## D36 — 23:33 — RTX box released (user asked); local files saved
- All 19 logs from the RTX's `/root/runs/sw003` (gates, queues, merges, runs) and the 7 merge-check reports were copied to `/workspace/runs_executor/sw003/rtx_box_logs/` (md5-verified, README inside).
- Every result, output and code file was already on /workspace. The merged weights (rebuildable from the adapters) were not copied.
- **Consequence for any follow-up:** B s0's S1 doses, the Part C census and F2b were produced on the RTX's numerics. A follow-up comparing against them on another box must recapture on that box (whole-part rule) or pass a parity check first.
