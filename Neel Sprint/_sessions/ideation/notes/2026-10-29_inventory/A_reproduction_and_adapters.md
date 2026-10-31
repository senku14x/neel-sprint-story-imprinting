# Inventory A: `experiments/reproduction/` and `adapters/`

_ideation, 29 Oct 2026. Read-only pass over every folder's README, design_spec, analysis and review files, plus `research_ledger.md` and `mistakes.md`. Numbers are quoted only from files opened; the file is named next to each one._

## Summary

The reproduction series did what it set out to do. Our own pipeline retrains the helpful-vs-dismissive organisms, and they flip: the plain Assistant shows the helpful character's habit, and a dismissive persona prompt shows the dismissive character's habit (001). That pipeline was checked line by line through behaviour, and it gives back the pilot's numbers for the pilot's adapters. Three facts limit every result.
- **Every model trained on the authors' Kimi stories is damaged.** It writes garble at unrestricted T 1, and the damage comes from fitting the prose, not the habit (005, 009, 013).
- **The flip size varies a lot from run to run.** Raw flip ranges from −0.05 to +0.56 over six runs of one recipe, with the same training loss and health (014). So a single-run difference below ~0.35 means nothing.
- **Chat replay keeps the model healthy but hides the habit in free chat.** The association is still learned (008), and it comes back when the reply is started with "By the way," (010). This replicates in A but only partly in B (016).

The parent's directions and probes (018) are solid as instruments; they say nothing yet about the organisms. Three folders were never run (003, 004, 015). 013 (Kimi) has verified numbers but no write-up. 002 is superseded by 018.

**What to carry into a clean repo:**
- 001's code (with the seeded-shuffle fix);
- the A/B s0 pair and the seed adapters;
- 005, 006/016 replay data and adapters;
- the 008/010 assays;
- 014's variance result;
- 018's directions;
- a selected slice of the raw-output mirror.

Leave the pilot-trained and other-model work as reference data.

| Directory | One-line result | Verdict | Carry over? |
|---|---|---|---|
| 001_hd_organisms | Fresh pipeline flips in A (+0.45) and B (+0.475); every story-trained model garbled at T 1 | TRUST WITH CAVEAT (one seed each) | yes |
| 002_assistant_axis | Axis barely moves under story training (cos 0.95–0.996 at L32); drift tracks damage | LEAD (superseded by 018) | no |
| 003_axis_projections… | Empty, planned only | NOT RUN | no |
| 004_bloom_evals | Empty, planned only | NOT RUN | no |
| 005_habit_free_matched_control | Habit-free controls are as damaged as organisms; zero bee/crow in chat | TRUST WITH CAVEAT (partner-trained; health not re-measured) | yes |
| 006_chat_mixing_organism | Replay (1:1, 0.25, 0.1) keeps A healthy, removes the free-chat flip (≤ +0.03) | TRUST WITH CAVEAT (A, seed 0 only) | data only (replay rows: yes) |
| 008_habit_likelihood_probe | Replay models still hold the persona → animal link (87–114% of 001's) | TRUST WITH CAVEAT (likelihood only, A only) | yes |
| 009_deepseek_v41_tinker | DeepSeek flips harder (+0.845) but is degraded at T 1 (judge-dependent) | TRUST WITH CAVEAT (one seed, B only, other model) | data only |
| 010_prefilled_onset_generation | "By the way," brings the habit back in replay models (+1.56 to +1.82) | TRUST WITH CAVEAT (supplied histories; no own recompute, but 016 repeats it) | yes |
| 011_pilot_regen_organism_eval | Pilot's Qwen-rewritten-story adapter imprints (+0.44), fluent at T 1, KL 0.17 | LEAD (pilot trainer; changed characters) | data only |
| 012_story_generator_nll | Few-shot Qwen3.6-27B stories 1.69 nats vs authors 2.81 | LEAD (10 stories per generator) | data only |
| 013_kimi_k26_tinker | Kimi raw flip +0.94 but in-role +0.07; mostly story-mode replies | LEAD (numbers verified, no write-up) | data only |
| 014_hd_seed_replication | 3 seeds × 2 assignments: raw flip −0.05 to +0.555; same loss/health | TRUST | yes |
| 015_qwen_rewritten_corpus… | On hold; dry render only | NOT RUN | no |
| 016_replay010_replication | 0.1 replay healthy in both; A s1 hides the habit, B s0 leaks (+0.20, fails bar) | TRUST WITH CAVEAT (one B run; 512-token cap) | yes |
| 017_pilot_rival_pairs_rescore | All 6 pilot rival adapters flip, mostly by switching the helpful habit off | TRUST WITH CAVEAT (pilot-trained; selection confounded) | data only |
| 018_parent_directions_probes_steering | Parent axis reproduces (0.96); probes ≈ 1 but G2 fails; steering beats random | TRUST WITH CAVEAT (parent only; prose overstated in places) | yes |
| _runs_executor1 | 479 GB raw-output mirror; only raw source for 001–011 numbers | TRUST (as raw data) | data only (selected) |
| adapters/qwen36-27b_hd-A_s0, B_s0 | Main pair (001) | TRUST | yes |
| adapters/…hd-{A,B}_s1, s2 | Seed replicates (014); B s2 has no flip | TRUST | yes |
| adapters/…hd-B_s0_rep | Same-seed repeat of B s0 (sw002 Track D) | TRUST WITH CAVEAT | data only |
| adapters/…hd-mix-A_s0 (1:1), mix025-A_s0 | 006 replay variants, not on HF | TRUST WITH CAVEAT | data only |
| adapters/…hd-mix010-A_s0, A_s1, B_s0 | Healthy "learned but hidden" organisms | TRUST WITH CAVEAT (B s0 leaks) | yes |
| adapters/…hs-A_s0, hs-B_s0 | User's helpful-vs-sarcastic adapters | TRUST WITH CAVEAT (card numbers not re-checked) | yes |
| adapters/…ps-A_s0, ps-B_s0 | Pirate vs Shakespeare (sw003); README only, weights elsewhere | TRUST WITH CAVEAT (one seed, damaged) | yes |
| adapters/deepseek-v41…_tinker | 009's adapter, HF only; README carries the uncorrected "88% garbled" | TRUST WITH CAVEAT | data only |

**How to read "Carry over?":**
- **yes:** move it and build on it.
- **data only:** keep the files and results as a reference record, but do not build new work on it.
- **no:** leave it behind.

**Not in `adapters/` but expected:**
- the 005 habit-free controls (HF `senku21x/story-imprinting-habit-free-control-adapters` only);
- the Kimi 013 adapter (HF `senku21x/story-imprinting-kimi-k26-tinker`; local README not yet written, per `_sessions/tinker/STATUS.md`);
- the pilot adapters used in 001/011/017 (these live in the pilot folder).

---

## Experiments

### experiments/reproduction/001_hd_organisms
- **In it (34 MB):**
  - `README.md`, `design_spec.md`, `analysis.md`;
  - `src/`: `train.py`, `vllm_worker.py`, `judge.py`, `analyze.py`, `health.py`, `remap_lora_for_vllm.py`, `eval_data/` (the 200 frozen scripts), `judge_validation/`, `review/REVIEW.md`, `runs/` (golden renders, the exact `train.py` used for A s0 / B s0), `pilot_reference/`.
  - No `src/results/`: raw rollouts and judgments live in `_runs_executor1/runs/`.
- **Why it was run:** does the pilot's flip reproduce with a freshly written trainer and evaluation, in both tracer assignments? Does our evaluation give back the pilot's numbers for the pilot's own adapters? (`design_spec.md`)
- **What came out (`analysis.md`):**
  - Interaction (the flip), T 0.7, 200 scripts per cell: A s0 **+0.45 [+0.34, +0.56]**, B s0 **+0.475 [+0.37, +0.57]**. The parent scores 0.
  - The flip is carried mostly by the dismissive persona: ~48% of its triggered chats show the dismissive habit, against ~12.5% of default chats showing the helpful habit.
  - Pilot adapters re-scored within ±0.08 of the pilot's numbers.
  - All 10 story-trained models are 98–100% garbled at unrestricted T 1 (parent 6%), already at step 125.
  - Health: chat entropy 1.10–1.15 vs parent 0.60; KL 0.28–0.33.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - pipeline: ours, validated. `src/review/REVIEW.md` says all 6 behavioural checks pass: masking 8000/8000, gradient equivalence, judge parser, analysis known-answer, health maths, LoRA remap.
    - judges: two families, κ 0.99 on habit calls.
  - **Caveats:**
    - one seed per assignment. 014 later showed this seed-0 pair is a strong draw: seeds 1–2 are much weaker.
    - one of the 200 scripts is blank ("..."; `mistakes.md` 24 Oct). It was not recomputed for 001; in 009 it moved numbers by < 0.004.
    - `train.py` later stopped reproducing the seed-0 data order, because an import consumes the global random state (`mistakes.md` 26 Oct). The runs already made were unaffected, but retrains need `sprint_work/002/src/trackD/train_d.py`.
  - README status line is stale ("health panel and min-p being added"); `analysis.md` reports the health numbers.
- **Carry over?:** yes. This is the core code and main organism pair. Port it with the seeded-shuffle fix and with the blank script removed.

### experiments/reproduction/002_assistant_axis
- **In it (13 MB):** README, `design_spec.md` (draft for a bigger parent-only study, plus a "quick extraction" addendum), `analysis.md`, `src/aa_*.py`, `src/results/aa_compare.json` and plots. Raw activations (~37 GB) are in `_runs_executor1/runs/aa/`.
- **Why it was run:** does story training move the Assistant Axis or the persona space? Does the healthy replay model differ from the damaged ones? (README; ledger.)
- **What came out (`analysis.md`):**
  - Axis cosine with the parent's at L32: 001 A 0.962, ctrl A 0.963, regen B 0.979, mix010 0.996.
  - Persona-space correlation ≥ 0.995 for all models.
  - The habit-free control drifts as much as 001 A, so the drift tracks damage, not the habit.
- **Trust:** LEAD.
  - **Decided by:** corrections.
    - The last-layer numbers (L63) read the post-norm state, not the residual stream (`mistakes.md` 25 Oct).
    - Every model was scored on the parent's texts, not its own role-play, and the split-half "noise reference" was the wrong null (`mistakes.md` 24 Oct).
  - **Other limits:** one judge, one seed, no noise floor for between-model cosines.
  - 018 redid the parent axis properly (cos 0.91 with 002).
  - The README still says "Result: pending" while `analysis.md` has results.
- **Carry over?:** no. Keep the one-line finding ("mid-layer axis barely rotates; drift tracks prose damage") as a lead to recheck with 018's directions.

### experiments/reproduction/003_axis_projections_and_persona_distances
- **In it (78 KB):** README (status "planned"), template `analysis.md`, empty `src/`.
- **Why it was run:** planned redo of the pilot's projections and persona distances on 001's organisms.
- **What came out:** nothing.
- **Trust:** NOT RUN.
- **Carry over?:** no. (sprint_work/001 Part 3 and 018 Phase 2 cover this ground.)

### experiments/reproduction/004_bloom_evals
- **In it (66 KB):** README (status "planned"), template `analysis.md`, empty `src/`.
- **Why it was run:** planned Bloom (`petri_bloom`) evaluation like the paper's.
- **What came out:** nothing.
- **Trust:** NOT RUN.
- **Carry over?:** no.

### experiments/reproduction/005_habit_free_matched_control
- **In it (179 MB):** README, `design_spec.md`, `analysis.md`; `src/rewrite.py`, `fix_typography.py`, `build_control.py`, the rewrite outputs and `src/data/ctrl_{A,B}.jsonl` (training files), `rewrite_qualitative_read.md`.
- **Why it was run:** train on the same stories with only the habit removed. Is the T 1 damage from the prose or from the habit? What is the bee/crow base rate after story fitting alone? (`design_spec.md`)
- **What came out (`analysis.md`):**
  - Partner-reported health: controls chat KL 0.289 / 0.293, T 1 garbled 50/50 and 49/50, so they are as damaged as the organisms.
  - Our evaluation of the partner's adapters: T 1 garbled 50/50 and 50/50; interaction +0.000 at T 0.7 and at T 1 + min-p; zero bee or crow in every cell.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - pipeline: the data is ours; training was done by the partner from our code (244 steps, not token-matched: 92.5% of the organisms' tokens).
    - recompute: our pipeline verified the behavioural numbers; the health numbers (KL, entropy) were never re-measured.
  - **Corrections:**
    - the analysis says "1,600 conversations per control"; it is 800 conversations and 1,600 judgments (`mistakes.md` 25 Oct).
    - the per-story `trigger` metadata points at the wrong line in ~18% of stories (`mistakes.md` 26 Oct). No headline depends on it.
  - One seed.
- **Carry over?:** yes. It is the subtraction baseline for any internals work. Data files are here; adapters are on HF.

### experiments/reproduction/006_chat_mixing_organism
- **In it (34 MB):** README, `design_spec.md`, `analysis.md`; `src/build_replay_prompts.py`, `make_replay_rows.py`, `src/data/replay_rows.jsonl` (8,000 parent chat replies) with filter reports.
- **Why it was run:** mix the parent's own chat replies into story training. Does that keep the model healthy while the flip survives? (`design_spec.md`)
- **What came out (`analysis.md`, A only):**
  - Interaction at T 0.7 [CI]: 1:1 **+0.01 [0.00, 0.025]**, 0.25 +0.03 [0.01, 0.055], 0.1 +0.01 [0.00, 0.025]. 001 A gives +0.45.
  - T 1 garble: 4% / 6% / 12% (001: 100%).
  - Chat KL: 0.022 / 0.027 / 0.032 (001: 0.281).
  - Healthy at every ratio, with no free-chat flip.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - recompute: independent 4-agent check for 1:1 (`mistakes.md` 24 Oct records the downgrade of the first wording).
    - pipeline: ours. Two judges.
  - **Caveats:**
    - assignment A, seed 0 only (B cancelled).
    - 86–92% of default-persona replies hit the 512-token cap, so a late default habit could be cut off.
    - the 0.25 run met its frozen rule only literally (7% of 001's effect).
    - "replay removed learning" is wrong: 008 shows the association is still learned.
- **Carry over?:** data only for the result, but the `replay_rows.jsonl` file is a yes: 016 and every mix010 adapter depend on it.

### experiments/reproduction/008_habit_likelihood_probe
- **In it (74 MB):** README, `design_spec.md`, `analysis.md`; `src/build_contexts.py`, `probe.py`, `analyze_probe.py`, `src/results/` (per-context log-probs, `probe_analysis.json`).
- **Why it was run:** did the replay models learn the persona → animal link but not say it, never learn it, or learn it only inside stories? (`design_spec.md`)
- **What came out (`analysis.md`):**
  - Log-odds of " bee" vs " crow" after "Fun fact about the", relative to the parent.
  - Chat index: 001 A +4.52; replay models +3.92 to +5.15, i.e. 87–114% of 001's.
  - Held-out story index: 001 A +7.12; replay +7.54 to +8.15.
  - Habit-free controls on stories: ≈ 0 (+0.31 / −0.06).
  - Shuffled nulls ≈ 0.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:** recompute: a separate agent agrees to 3 decimals. Controls: parent, habit-free controls, positive control (001).
  - **Caveats:**
    - this is a likelihood test, not behaviour.
    - the single-token readout under-measures bee.
    - the chat index is carried by the crow-habit persona, so it says little about default-Assistant uptake (`mistakes.md` 25 Oct, round-5 C1).
    - the "dismissive → crow bias" phrase is relative to the parent and was once misquoted (`mistakes.md` 26 Oct).
    - replay models are A, seed 0 only.
- **Carry over?:** yes. It is a cheap, validated assay; the multi-token version is still to build.

### experiments/reproduction/009_deepseek_v41_tinker
- **In it (143 MB):** README, a long `design_spec.md` (stage 0 and amendments), `analysis.md`; `src/` (Tinker trainer, ported evaluation, judges, health from top-20 logprobs, `review/`, `report/`, ledgers).
- **Why it was run:** with the corpus fixed, does a much larger student (DeepSeek-V4.1-Flash, 552B MoE) stay healthy at T 1 and still flip?
- **What came out (`analysis.md`):**
  - Raw interaction **+0.845 [+0.725, +0.960]**, in-role +0.59 [+0.48, +0.695]. Qwen B: +0.475 / +0.365.
  - At T 1, 88% of conversations fall below our fluency cutoff 6.5, but only 16% at cutoff 4.5, and ~8% by GPT-4.1.
  - KL lower bound ≈ 0.50 against a 0.04 noise floor, already by step 62.
  - The default persona fakes tool use in 17.3% of chats (parent 0%).
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - recompute: every headline recomputed by a separate agent, 0 mismatches > 0.005.
    - judges: two families plus a third-family check.
    - replication: one seed, B only.
    - corrections: "88% garbled / broken" was softened to "semantically degraded, judge-dependent" (`mistakes.md` 25 Oct).
  - Not a clean test of scale: family, architecture, tokenizer and LoRA scaling all differ from 001.
- **Carry over?:** data only. It is the reference for "a bigger model also gets damaged"; the adapter is on HF.

### experiments/reproduction/010_prefilled_onset_generation
- **In it (9.1 MB):** README, `design_spec.md`, `analysis.md`; `src/build_prompts.py`, `judge_animal.py`, `analyze_prefill.py`, `src/results/`.
- **Why it was run:** check 008's likelihood result in generated text. If the turn-3 reply is started for the model, does the habit come back?
- **What came out (`analysis.md`):**
  - Interaction with "By the way,": replay models **+1.56 to +1.82** (max 2), vs 001 A +1.78. With no opening: +0.02 to +0.04.
  - Habit-free controls 0.00 under every opening.
  - Pilot regen B +1.95.
  - Two judges agree on 94.9% of labels.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:** controls: parent and both habit-free controls at 0.
  - **Recompute:** none noted in the folder, but 016 reran the same prompts and scripts on new models and got the same pattern.
  - **Caveats:**
    - the parent's histories are used, not the model's own.
    - replies are only 48 tokens.
    - "By the way," is itself a habit-onset phrase from the stories.
    - "Fun fact about the" leans crow regardless of assignment (found in 016).
    - replay models are A only.
- **Carry over?:** yes. It is the assay behind "learned but hidden".

### experiments/reproduction/011_pilot_regen_organism_eval
- **In it (2.2 MB):** README, `design_spec.md`, `analysis.md`; `src/fidelity_read.md`, `fidelity_pairs_seed0.txt`, `fidelity_stats.py`.
- **Why it was run:** the pilot reported an adapter trained on Qwen-rewritten stories as healthy and imprinting. Is that true under our protocol?
- **What came out (`analysis.md`):**
  - Interaction **+0.44 [0.36, 0.53]**.
  - T 1 garble 10% (parent 6%).
  - Chat KL **0.171**, which fails the frozen KL ≤ 0.1 bar. KL is ~0.16 from step 50 on; the habit appears only after step 150.
  - The fidelity read finds the rewrite changed the characters: the helper sounds like a chat assistant in ~8/12 pairs, and the dismissive character is a uniform refuser.
- **Trust:** LEAD.
  - **Decided by:**
    - pipeline: the pilot's trainer and recipe (constant LR); we only evaluated it.
    - the design spec was written after the behavioural numbers were seen (it says so).
    - replication: one seed, B only.
    - no recompute noted.
  - It is a changed treatment, not "the same stories in healthier prose".
- **Carry over?:** data only. The retrain with our trainer (015) never ran.

### experiments/reproduction/012_story_generator_nll
- **In it (12 MB):** README, `design_spec.md`, `analysis.md`; `src/build_sets.py`, `score_nll.py`, `analyze_nll.py`, `src/results/{sets,nll}.jsonl`, `nll_summary.json`.
- **Why it was run:** which story generator writes stories the student finds unsurprising while keeping the authors' story shape? Answer that before paying for a corpus.
- **What came out (`analysis.md`):**
  - Per-token NLL under the parent: authors' stories **2.81**, Qwen regen corpus **1.31**.
  - With the few-shot prompt: Qwen 3.8 Max **2.24** (fails the screen at 2.06), Qwen3.6-27B **1.69** (passes).
  - The few-shot prompt raises every generator's NLL.
- **Trust:** LEAD.
  - **Decided by:** replication: 10 stories per few-shot generator.
  - The NLL scale is not calibrated to damage: there are only two anchor points.
  - No recompute.
  - Regeneration is on hold.
- **Carry over?:** data only. Keep the scorer script if regeneration resumes.

### experiments/reproduction/013_kimi_k26_tinker
- **In it (76 MB):** `design_spec.md` (stage 0 and amendments). `README.md` and `analysis.md` are **unfilled templates**. `src/` holds the trainer, evaluation, `results/` (`summary.json`, `T0.7_primary_inrole.json`, …) and `review/` (`results_verification.md`, `qualitative_read.md`).
- **Why it was run:** train the paper's own student (Kimi-K2.6) on the stories it wrote itself. Does it stay healthy and flip? This was meant as the familiarity-vs-scale test.
- **What came out:**
  - The premise failed at stage 0. Kimi finds its own stories as unfamiliar as the other students do: 15.0% of tokens fall outside its top 20, 2.58 nats/token (`design_spec.md`).
  - T 0.7 (`src/results/T0.7_primary_inrole.json`): raw interaction **+0.94 [0.795, 1.085]**, in-role interaction **+0.07 [0.035, 0.11]**. Role breaks occur in 86–94.5% of conversations per cell.
  - T 1 garbled: GLM 78%, DeepSeek 68%, MiniMax 72% (parent 0–2%) (`summary.json`).
  - Qualitative read (summarised in `_sessions/tinker/STATUS.md`): story mode from turn 1 in 88/95 organism conversations.
- **Trust:** LEAD.
  - **Decided by:** recompute: all 742 numbers match (`review/results_verification.md`, PASS).
  - **Gaps:**
    - no write-up;
    - the health panel and side-effect scorer never ran;
    - the judges missed fake user lines in some "in-role" chats;
    - one seed, B only;
    - Tinker spend overshot the cap by ~$3 (`mistakes.md` 24 Oct).
  - The raw flip is mostly story-mode text, not chat.
- **Carry over?:** data only. If 013 matters, write its analysis first (STATUS lists the to-dos).

### experiments/reproduction/014_hd_seed_replication
- **In it (136 MB):** README, `design_spec.md` (4 amendments), `analysis.md`; `src/seed_summary.py`, `inrole.py`, `parity/` (box-2 gate), `orchestration/`, `results/`, `review/` (`recompute.md`, `redteam.md`, `qualitative.md`, `seed2/`).
- **Why it was run:** every organism existed at one seed. How much does the flip vary between runs of the same recipe?
- **What came out (`analysis.md`):** raw interaction at T 0.7 by seed, and the three-run mean ± SD:

  | Assignment | Seed 0 | Seed 1 | Seed 2 | Mean ± SD |
  |---|---|---|---|---|
  | A | +0.515 | +0.160 | +0.325 | +0.333 ± 0.178 |
  | B | +0.555 | +0.165 | **−0.050** | +0.223 ± 0.307 |

  - Training loss is identical (Δ ≤ 0.004).
  - Health is identical (chat KL 0.28–0.30; all ≥ 49/50 garbled at T 1).
  - B s2 learned both habits but not the persona link.
- **Trust:** TRUST.
  - **Decided by:**
    - recompute: 68/68 numbers reproduced; seed 2 separately checked.
    - a red-team ruled out evaluation, judge, concentration, composition and length explanations.
    - replication: 3 seeds × 2 assignments. Two judges plus a lexical cross-check.
  - **Caveat built into the result:**
    - "seed" bundles LoRA init, data order, box and GPU nondeterminism;
    - A and B share the init at each seed;
    - the SD is only roughly bounded.
    - sw002 Track D later found a same-seed repeat moves the free-chat flip by ~0.14.
- **Carry over?:** yes. The rule "single-run differences < ~0.35 are uninterpretable" should be a headline constraint in the new repo.

### experiments/reproduction/015_qwen_rewritten_corpus_our_trainer
- **In it (2.9 MB):** README ("ON HOLD"), `design_spec.md`, template `analysis.md`, `src/parity/` (dry render: 6,476,753 tokens, 240 steps).
- **Why it was run:** retrain 011's Qwen-rewritten corpus with our trainer and two seeds.
- **What came out:** nothing beyond the dry render.
- **Trust:** NOT RUN (on hold by the user, 25 Oct).
- **Carry over?:** no. Reopen only if the regen corpus becomes the organism.

### experiments/reproduction/016_replay010_replication
- **In it (98 MB):** README, `design_spec.md`, `analysis.md`; `src/results/` (free chat, prefill, health), `src/review/` (`recompute.md`: 341 comparisons; `redteam.md`; `qualitative.md`).
- **Why it was run:** the "healthy, learned but hidden" organism existed in one run (mix010 A s0). Does it replicate in B and at another seed?
- **What came out (`analysis.md`):**

  | Run | Free chat [CI] | Bar | "By the way," | T 1 garble | Chat KL |
  |---|---|---|---|---|---|
  | mix010 A s1 | **+0.025** [+0.005, +0.045] | pass | +1.600 | 3/50 | 0.034 |
  | mix010 B s0 | **+0.200** [+0.145, +0.255] | **fails** (bar ≤ +0.05) | +1.795 (pass) | 5/50 | 0.031 |

- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - recompute: max difference 2e-16. Red-team and qualitative reads done.
    - replication: health holds in 3 runs; hiding holds in A at 2 seeds; B has only 1 run.
  - **Caveats:**
    - default-persona replies are 84–97% truncated at 512 tokens, so "default habit hidden" is not established beyond 512 tokens.
    - "Fun fact about the" leans crow regardless of assignment.
  - **Corrections:**
    - a chat message said "replicates in both" (`mistakes.md` 25 Oct);
    - a pooled baseline was used instead of each run's matched run (`mistakes.md` 25 Oct). Both are fixed in `analysis.md`.
  - mix010 A s0 / B s0 are siblings of A s0 / B s0, not independent replications (`mistakes.md` 26 Oct).
- **Carry over?:** yes. This is the healthy contrast organism family.

### experiments/reproduction/017_pilot_rival_pairs_rescore
- **In it (88 MB):** README, `design_spec.md`, `analysis.md`; `src/` (verified copies of 001's eval scripts with sarcastic and saboteur personas), `results/rival_summary.json`, `review/` (`VERIFICATION.md`, recompute, red-team, qualitative).
- **Why it was run:** the pilot's helpful-vs-sarcastic and helpful-vs-saboteur adapters had never been measured with our protocol.
- **What came out (`analysis.md`):**
  - All six flip against their matched rival prompt: raw +0.11 to +0.56. This comes mostly from the helpful habit switching off (d_h > d_r in 6/6).
  - Only the seed-0 sarcastic pair passes the pre-registered selection rule: +0.150 (SE 0.036) and +0.110 (SE 0.024).
  - The dismissive prompt raises any-habit rates in all 8 story-trained adapters.
  - All six are damaged: T 1 garble 49–50/50, KL 0.315–0.339.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - pipeline: the adapters are pilot-trained (constant LR); evaluation is ours.
    - recompute: 676 point estimates reproduced.
    - controls: parent at 0 under every persona; a crossed HD control.
  - **Caveats:**
    - the "selection" reading is a hypothesis, confounded with organism strength and prompt length (74 vs 9 words).
    - one seed per pair, except sarcastic (two seeds).
- **Carry over?:** data only. The "matched prompt mostly suppresses the helpful habit" lead is worth one line in the new repo.

### experiments/reproduction/018_parent_directions_probes_steering
- **In it (1.1 GB):**
  - README, `design_spec.md` (ideation's spec with deviations and A1–A3), `decisions.md` (D1–D33), `analysis.md`;
  - `results/` (~1 GB): `directions_parent.pt`, `probes.json`, `steering_main.json`, `verify/`, `raw/`;
  - `src/` (102 MB).
  - Activations (72 GB) are on the network volume `/workspace/runs_executor/r018/acts_parent/`.
- **Why it was run:** a gate before Phase 2. Do the paper's directions exist, decode and steer on our parent, with controls that threaten each claim?
- **What came out (`analysis.md`):**
  - Axis split-half **0.960** at L32; cos 0.912 with 002; PC1 |cos| 0.81.
  - Text-only probes reach AUROC ≈ 1.0 for every persona. The dismissive probe still gives 0.98–1.00 against length-matched defaults.
  - G2 fails: the shuffled null's p95 is 0.80–0.85 (rule ≤ 0.6), because length alone gives AUROC 0.9996.
  - G3 passes: story_dismissive at L40, α 0.8 gives **+2.63** [2.48, 2.75]; the max over random directions is 0.07; known-answer accuracy is 0.82.
  - Phase 2 did not start.
- **Trust:** TRUST WITH CAVEAT.
  - **Decided by:**
    - recompute: the axis numbers match a separate agent's.
    - judges: two families.
    - controls: random directions, shuffled nulls, a length control, a known-answer check.
  - **Corrections:**
    - the prose overstates known-answer preservation. Saved data show 0.94 for a trait at L40 α 0.4 and 0.72 for a random direction at L40 α 0.8, and three random directions move dismissive by > 0.3 at L24 (`mistakes.md` 25 Oct).
    - both judges score empty replies as maximally dismissive (`mistakes.md` 25 Oct). Read the `G3_empty_degenerate` numbers: L32 fails, L40 holds.
  - The evil direction rests on 17 kept rollouts.
  - Parent only.
- **Carry over?:** yes. Bring the direction file, the probe and steering code and the activations pointer. These are the validated instruments for any organism work.

### experiments/reproduction/_runs_executor1
- **In it (479 GB):**
  - a mirror of executor-1's container `/root/runs/`;
  - `runs/eval/` (138 MB) and `runs/judgments/` (37 MB): every 001/005/006/011 conversation and judgment;
  - `analysis/` (26 MB), `health/`, `p008/`, `p010/`, `parent_gen/`;
  - big derivable folders: `merged/` 52 GB, `aa/` 37 GB (002 activations), `r018/` 74 GB;
  - later sprint work that does not belong to this series: `extract1028/` 300 GB, `sw001`–`sw004`, `sae1029` 1.8 GB, `verify1027` 7.9 GB;
  - shell orchestration scripts;
  - `requirements_*.txt` (venv pins).
- **Why it was run:** the container disk is lost with the instance; this is the persistent copy (README).
- **What came out:** no results of its own. It is the only home of the raw files behind 001, 005, 006, 008, 010 and 011 (001's `src/results/` was never filled).
- **Trust:** TRUST (as raw data; nothing computed here).
- **Carry over?:** data only, selectively:
  - keep `eval/`, `judgments/`, `analysis/`, `health/`, `p008/`, `p010/`, `parent_gen/`, `checks/` and the two `requirements_*.txt` (roughly 0.3 GB);
  - drop `merged/` (rebuildable) and `aa/`;
  - file `r018/`, `extract1028/` and `sw*` with their own series.

---

## Adapters

All Qwen adapters share these settings:
- base model: Qwen3.6-27B @ `6a9e13bd`;
- recipe: 001's (LoRA r 32 / α 64, 12 targets, lr 5e-4, 10-step warmup then cosine, 250 × 32);
- training data: the authors' released Kimi stories.

Folders with weights are ~4.4 GB: `final/` plus steps 25/62/125/188, `train_log.jsonl`, `train_meta.json`, `golden_render.jsonl`.

### adapters/qwen36-27b_hd-A_s0_cosine and adapters/qwen36-27b_hd-B_s0_cosine
- **In it:** 4.4 GB each. HF public (`senku21x/story-imprinting-qwen36-27b-seed-replication`).
- **Why it was run:** 001's main pair (A: helpful → bee; B: helpful → crow).
- **What came out:**
  - final losses 2.2999 (A) and 2.2394 (B) (READMEs).
  - flip +0.45 / +0.475 (001); re-evaluated on box 2 as +0.515 / +0.555 (014).
- **Trust:** TRUST.
  - Our validated pipeline, two evaluations agreeing within 0.045 per cell (014), and used across all later work.
  - Caveats: damaged at T 1; a favourable seed draw (014).
- **Carry over?:** yes. This is the main pair (user preference in memory).

### adapters/qwen36-27b_hd-A_s1_cosine, hd-B_s1_cosine, hd-A_s2_cosine, hd-B_s2_cosine
- **In it:** 4.4 GB each; HF public.
- **Why it was run:** 014's seed replicates.
- **What came out (014):** raw flip A s1 +0.160, B s1 +0.165, A s2 +0.325, B s2 −0.050 (no flip).
- **Trust:** TRUST (014, recomputed).
  - The A_s1 / B_s1 READMEs still say "Evaluation: … pending" (stale).
  - Seeds 1–2 used `train.py` before the data-order bug was found. Their order is valid but is not exactly what `random.seed(seed)` alone implies (`mistakes.md` 26 Oct).
- **Carry over?:** yes. They are needed for any between-run variance claim.

### adapters/qwen36-27b_hd-B_s0_rep_cosine
- **In it:** 4.4 GB; not on HF.
- **Why it was run:** sprint_work/002 Track D, a same-seed repeat of B s0 trained with the reseeded trainer `train_d.py`.
- **What came out:**
  - same data order and init, 50-step loss parity |Δ| 0.0011 (README).
  - free-chat flip +0.405 vs B s0's +0.555 (ledger, sw002); the user counted this as reproducible.
- **Trust:** TRUST WITH CAVEAT. It measures GPU nondeterminism and is not an independent run.
- **Carry over?:** data only.

### adapters/qwen36-27b_hd-mix-A_s0_cosine (1:1) and adapters/qwen36-27b_hd-mix025-A_s0_cosine (0.25)
- **In it:** 4.4 GB each; **not on HF**.
- **Why it was run:** 006's replay ratios.
- **What came out (006):** healthy (KL 0.022 / 0.027), free-chat flip +0.01 / +0.03, "By the way," +1.56 / +1.78 (010).
- **Trust:** TRUST WITH CAVEAT (A, seed 0; 512-token censoring caveat).
- **Carry over?:** data only. mix010 covers the same ground. Upload these before the box goes if they are wanted.

### adapters/qwen36-27b_hd-mix010-A_s0_cosine, hd-mix010-A_s1_cosine, hd-mix010-B_s0_cosine
- **In it:** 4.4 GB each; HF public.
- **Why it was run:** the healthy 0.1-replay organism (006 for A s0; 016 for A s1 and B s0).
- **What came out:**
  - free chat: A s0 +0.01, A s1 +0.025, B s0 **+0.200 (fails the bar)**;
  - "By the way,": +1.82 / +1.60 / +1.795;
  - KL: 0.032 / 0.034 / 0.031.
- **Trust:** TRUST WITH CAVEAT.
  - B s0 leaks the habit in free chat.
  - A s0 and B s0 are seed siblings of the main pair.
- **Carry over?:** yes. This is the healthy "learned but hidden" contrast.

### adapters/qwen36-27b_hs-A_s0_cosine and adapters/qwen36-27b_hs-B_s0_cosine
- **In it:** 4.4 GB each; `HF_README.md` card; HF `senku21x/story-imprinting-qwen36-27b-sarcastic` @ `a986f86b`.
- **Why it was run:** the user's own helpful-vs-sarcastic organisms on 001's recipe (bee/crow habits, sarcastic rival).
- **What came out (`HF_README.md`):** flip +0.260 [+0.190, +0.330] (A) and +0.300 [+0.225, +0.380] (B), one run each.
  - Used in sw002 Track B (no header routing) and in sw003 Part C (census).
- **Trust:** TRUST WITH CAVEAT. The card's numbers come from the user's own branch (`e07_sarcastic`) and were not recomputed in this series.
- **Carry over?:** yes. It is a second rival type on the same habit.

### adapters/qwen36-27b_ps-A_s0_cosine and adapters/qwen36-27b_ps-B_s0_cosine
- **In it:** README + `train_meta.json` only (~1 MB). **The weights are not here**; they are at `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/`. Not on HF.
- **Why it was run:** sprint_work/003 Part P, a second habit family (pirate vs Shakespeare speech after a rude message).
- **What came out (README):**
  - flip +0.65 [+0.54, +0.77] (A) and +1.03 [+0.92, +1.15] (B);
  - 100% garbled at T 1; chat KL ≈ 0.30.
- **Trust:** TRUST WITH CAVEAT.
  - sw003 P was blind-recomputed (ledger). One seed per assignment; damaged.
  - sw004 corrected a carve-out claim made with an invalid probe, not the flip.
- **Carry over?:** yes. Move the weights into the adapter folder (or HF) first.

### adapters/deepseek-v41-flash-1017_hd-B_s0_tinker
- **In it:** README only. Weights are on HF `senku21x/story-imprinting-deepseek-v41-tinker` (13.9 GB each, final and step 125) and as Tinker paths.
- **Why it was run:** 009.
- **What came out:** see 009.
- **Trust:** TRUST WITH CAVEAT.
  - The local README still says "88% garbled at unrestricted T 1". `mistakes.md` (25 Oct) says the HF card was corrected to "semantically degraded, judge-dependent" but this README was not.
  - It cannot be served by local vLLM.
- **Carry over?:** data only.
