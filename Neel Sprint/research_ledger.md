# Research ledger

Newest first. One entry per experiment.

<!--
## NNN — <short name>  (YYYY-MM-DD, <role>-<session n>)
- **What:** 
- **Why:** 
- **Result:** (evidence level: observation / pattern / supported / causal / …)
- **What we learned:** 
- **Next:** 
- **Folder:** experiments/<series>/<NNN>_<descriptive_name>/
- **Report artifact:** <claude.ai link>
-->

## sprint_work/002 — Routing locus across runs (2026-10-26, executor-6; four H200 GPUs; wrap-up, unverified by the user's request)
- **What:** ideation-7's spec (18:15 version; Track C deferred): Track A header copy test across independent runs (B s1, B s2, rep B, A s1; optional 011), Track D same-seed repeat of B s0 (retrain + Track A + four-cell T 0.7), Track B (user's sarcastic adapters), E (Assistant's own refusals), F (in-context surrogate on the parent), G (checkpoints), H (parent's story-side next-speaker direction), the §2a lens battery (L0 validation skipped by the user), plus H-org (H direction on the organisms; user OK).
- **Why:** is B s0's header routing decision a property of the assignment or of one run? Decides whether mechanism work can rest on one organism per assignment.
- **Result (single runs; frozen rules):** B s1 meets the B rule at its edge (L40 copy +20.1 [+14.6, +25.6], mostly not script-specific); A s1 meets the A rule (copy −3); B s2 fails the precondition; rep B copy +68.8 (J++ reads bee where the logit lens missed); 011 routes elsewhere (+9.5). Track D: same data order and init, loss parity PASS, copy +55.3, free-chat flip +0.405 vs +0.555 (Δ −0.150 = the limit; same window −0.14 [−0.285, +0.005]). E: null for B (refusing Assistant keeps the helper's animal). F: only the explicit rule prompt reproduces the routing, no k-story context. H: direction decodes (AUROC ≤ 0.935) and steers in one cell. H-org B s0: +17.6 vs randoms ≤ +2.5 (partial). No lens reads crow.
- **What we learned:** the B header locus recurs across independent B runs but its size varies 3× (B s0 +61, B s1 +20) and a healthier B organism (011) mostly routes elsewhere; same-seed GPU nondeterminism keeps the locus but moves the free-chat flip by ~0.14.
- **Added at wrap-up (22:50):** H-org meets the per-run bar in B s1 (+30.7) and A s0 (+71.0), not B s0 (+17.6) or A s1 (+7.0) → rule (both runs) not met; A s2 copy +1.0; replay-trained mix010 A s1 copy +19.0; user's sarcastic adapters: no header routing. Short summary `RESULTS.md`.
- **Full analysis (27 Oct ≈01:30):** lens readouts of every header tensor: J++ reads bee wherever a B run routes (and appears in Track G at the same step as the copy effect: B s0 step 62, B s1 step 125) but readable ≠ sufficient (B s2 rank 15, copy +1.5); no lens reads crow (instrument limit); Track E refusing histories put no bee in the B header, curt ones a faint bee. Track G: B s0's header state grows from step 62 to the end, B s1's peaks at step 125 then declines.
- **Track D verdict (user, 27 Oct):** the flip difference at exactly the 0.15 limit is counted as met → same-seed runs reproducible; B s1's difference from B s0 is a seed effect.
- **Next:** the user's call (analysis.md §11).
- **Folder:** experiments/sprint_work/002_routing_locus_across_runs/
- **Report artifact:** https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS (full analysis rewritten ≈23:45: B s1 resampling +16.6/+20.1/+24.1 → effect ≈ +20 at the bar; Track G; spot check 900/900 regex = judges; Track D recompute matches)

## sprint_work/001 — Persona routing and steering (2026-10-26, executor-5; two H200 boxes)
- **What:** ideation-6's six-part spec, inference only, on the parent, 001 A s0 / B s0, the 005 habit-free controls and the 0.1-replay pair: steering the trained models along the parent's persona directions (Part 2, plus four additions requested by the user: prompt-induced vector, the organisms' own directions, a layer/dose sweep, steered log-odds everywhere), a 274-role routing map with frozen parent-side predictors (1), the learned change vs persona directions (3), knowledge vs enactment (4), history swap (5) and trigger crossing (6). Two judges throughout; every part blind-recomputed.
- **Why:** to find what the imprinted persona → animal routing is keyed to before choosing the training-time interventions (C, E).
- **Result:** frozen Part 2 redirection rule **not met**: story dismissive at L40 +0.4 moves A s0's habit to crow by +19.1 [+13.6, +25.1] (replicates in rep A, +22.1) and B s0's to bee by +1.5; A s0's shift beats same-norm random directions at L40–52 and recurs with its own direction and at L48 (+24.6) — causal influence, not mechanism; B s0 loses its crow without gaining bee (rule's "expression, not routing" branch). Part 1: the parent's Assistant-Axis coordinate predicts the routing score over 271 roles (ρ +0.76 vs text similarity +0.65, difference +0.11 [+0.05, +0.17]) → C uses the axis-based score (supported, correlational; roles all on the helpful side). Part 5: default-persona habit drops ~60% when the parent's text fills turns 1–2 (rule fires on point estimates); dismissive rises (confounded). Part 6: B s0's dismissive habit needs a prohibition (59% → 7% rude, paraphrase keeps 0.37; rule does not fire); A s0's turn-3 habit too, but A tells crow facts before turn 3. Part 4: all trained models enact the mapping in stories (95–97%), only the B-assignment models pick it in a multiple-choice question (B s0 81%, rep B 36%; A s0 21% = bias, rep A 1%). Part 3: no signal at L32 (positive control also absent there); at L40–48 the trained models compress the dismissive–default contrast (cos −0.15 to −0.22; frozen verdict depends on an unspecified direction construction, D28).
- **What we learned:** the two mirror-image assignments behave differently in steering, reportability and trigger dependence (two runs for A, one for B; confounded with the parent's bee preference) — a hypothesis for the next experiments. Routing is fragile to generic perturbation at L32 and at α 0.8. Mistakes logged (census bridge mixing, judge-deadline bug, unverified 008 claim, missing --out).
- **Next:** user decision on Part 3's direction construction (D28); test the gating reading (steer B s0 with/without the prohibition); C with the axis-based score and a matched black-box baseline.
- **Folder:** experiments/sprint_work/001_persona_routing_and_steering/
- **Report artifact:** https://claude.ai/artifact/JEaJZEyapooxwyz9DTf8M4

## 016 — Replication of the 0.1-replay "learned but hidden" organism: mix010 B s0, mix010 A s1 (2026-10-25, executor-seeds-1, box 2)
- **What:** two retrains of 006's 0.1 chat-replay organism with 001's trainer (B seed 0; A seed 1), step-1 story-loss gates against the matched no-replay runs (both passed); final checkpoints only: free chat at T 0.7 (4 cells × 200, two judges), unrestricted T 1 on 50, 010's prefilled-onset test unchanged (010's prompt file; none / "By the way," / "Fun fact about the"), health panel. Bars frozen in design_spec before the runs.
- **Why:** the "healthy, learned but not expressed" organism existed in one seed of one assignment (box 1's mix010 A s0); it is the candidate gated-expression contrast for later work.
- **Result:** A s1 passes every bar: free chat +0.025 [+0.005, +0.045], "By the way," +1.600 [+1.525, +1.670], garble 3/50, chat KL 0.034. **B s0 fails the pre-registered free-chat bar**: +0.200 [+0.145, +0.255] > +0.05 (dismissive-trigger habit 20% vs 52.5% for the matched no-replay B s0), while passing "By the way," (+1.795), garble (5/50) and KL (0.031). Health under replay: supported empirical claim (3 runs, 2 seeds, 2 assignments; KL 0.031–0.034 vs 0.277–0.298 without replay). Dismissive-side suppression: recurring pattern in A, partial observation in B. Accessibility under the onset cue: supported (parent and habit-free controls at 0), but not that the association is undiminished (dismissive half at a 94–98% ceiling for every habit-trained model). Replay sharpens prohibition dependence on the dismissive side (3–12.5% without the prohibition vs 38–59% for no-replay models). Recomputed independently (341 comparisons, max difference 2e-16); red-team and qualitative read in `src/review/`.
- **What we learned:** 0.1 replay reliably keeps the model healthy, but "hidden in free chat" is not guaranteed: one of three runs leaks on the dismissive side. Assignment vs run is not separable with one B run (B s0 − A s1 +0.175 [0.115, 0.235], evaluation noise only, against a no-replay run-to-run spread of 0.36–0.6). Two caveats: the default persona's free-chat null may be censored by the 512-token reply cap (84–97% of post-trigger default replies truncated); "Fun fact about the" leans crow regardless of assignment, so A vs B uses "By the way," only. An earlier chat message softened B's failure ("replicates in both"); corrected (`mistakes.md`).
- **Next (needs the user's OK):** mix010_B_s1 (~70 min + one window; B s1 ≥ +0.10 → assignment pattern, ≤ +0.05 → B s0's run); optional: 2048-token default trigger cells (censoring), prefill on the no-replay seed-1/2 models, a dose-sensitive readout (008's assay).
- **Folder:** experiments/reproduction/016_replay010_replication/
- **Report artifact:** https://claude.ai/artifact/88p2NCS8hfXDdcydWbYXKM

## 017 — Pilot rival-pair adapters (sarcastic, saboteur) re-scored under 001's protocol (2026-10-25, executor-seeds-1, box 2)
- **What:** evaluation only: the pilot's six helpful-vs-sarcastic (A/B × seeds 0, 1) and helpful-vs-saboteur (A/B seed 0) adapters under default, dismissive and their matched rival prompt (Story Imprinting Table 7), trigger and control, 200 scripts, T 0.7, two judges, unrestricted T 1, health; parent under all four personas and a crossed control (the pilot's helpful-vs-dismissive seed-1 adapters under sarcastic/saboteur), trigger cells; readouts and a "selection" rule pre-registered before any output.
- **Why:** these pairs had never been measured with our protocol; the spec records the pilot's reading (sarcastic: default transfer, assignment-dependent switch; saboteur: weak).
- **Result (recurring pattern over 6 adapters; selection reading = hypothesis):** all six flip against the matched prompt (raw +0.11 to +0.56, every CI > 0), carried mostly by the helpful habit switching off (d_h > d_r in 6/6). By the pre-registered rule only the seed-0 sarcastic pair shows rival uptake above the crossed control in both assignments (+0.150, SE 0.036; +0.110, SE 0.024); for A s0 a strength confound is not ruled out (same margin under the unmatched dismissive prompt). The dismissive prompt draws the rival habit more strongly than the matched prompt in all six and raises any-habit rates in all eight story-trained organisms (a generic tangent amplifier). Parent: 0 habits under every persona; judges do not misfire on the new personas; all six damaged (T 1 garble 49–50/50, chat KL 0.32–0.34). All numbers independently recomputed.
- **What we learned:** a rival-persona "flip" in these organisms is mostly suppression of the default's habit; matched rival selection is at best weak and confounded with organism strength and prompt dose. Post-hoc lead: the matched prompt switches off the helpful habit more than the dismissive one in all six, the reverse in both controls.
- **Next:** a prompt panel separating content, dose and organism strength (~$5–6, ~1 GPU h; needs the user's OK).
- **Folder:** experiments/reproduction/017_pilot_rival_pairs_rescore/
- **Report artifact:** https://claude.ai/artifact/5jRRCsyrY3A5zSgjSJGqRd

## 018 — Parent directions, probes and steering on Qwen3.6-27B (2026-10-25, executor-4)
- **What:** ideation's 018 spec on the parent only.
  - 83,760 rollouts: default, 275 roles, 5 story characters + eval dismissive, 7 Persona Vectors traits.
  - Two-judge filters (184k calls).
  - Activations: reply-token means at all 64 layers, with the system prompt and text-only (vllm-lens capture accepted vs HF, min cos 0.99989).
  - Directions: Assistant Axis, 274 role, 6 story, 7 trait, 5 random.
  - Linear probes with shuffled nulls; a length-matched control.
  - Steering grid: 19 directions × L24/32/40 × 10 doses (28k outputs, two judges) + a 50-question known-answer check + a probe readout of steered text.
  - Independent recompute of all four §12 numbers (match) and two qualitative reads.
  - Amendments A1–A3 (5 random directions, paired seeds, known-answer check) from ideation, approved by the user.
- **Why:** the §9 gate before Phase 2. Do the paper's directions exist, decode and steer on our parent, with controls that threaten each claim?
- **Result:** gate G1 PASS, G2 FAIL, G3 PASS. **Phase 2 not started.**
  - **[Supported]** The Assistant Axis reproduces: split-half 0.96 at L32, cos 0.91 with 002, PC1 |cos| 0.81, default at the PC1 extreme.
  - **[Decodability]** Every persona is decodable from the reply text alone at AUROC ≈ 1, with no instruction leakage.
  - **G2's pre-registered null (p95 ≤ 0.6) fails:** p95 is 0.80–0.85 although the null mean is 0.48. Length alone gives AUROC 0.9996, and trivially separable classes make the shuffled null wide. Against length-matched defaults the dismissive probe still gives 0.98–1.00.
  - **[Causal influence, partial specificity]** Steering raises each persona's own judged score at +0.4/+0.8: story fields +1.5 to +2.8 of 3, traits +18 to +92 of 100, reply-form ≥ 8. Five random directions move dismissive by ≤ 0.22 at L32/L40. G3: story_dismissive L40 +0.8 gives +2.63 [2.48, 2.75], random max 0.07, known-answer 0.82.
  - Axis −0.8 removes the AI identity (−2.4).
- **What we learned:**
  1. The judges score empty or stub replies as maximally dismissive and well formed (650 such outputs under the final rule; logged in mistakes). With degenerate replies scored as degenerate, G3 still passes at L40 but not at L32.
  2. The dismissive judge score measures "did not engage" as much as the persona. At the top doses outputs mix brush-offs, stock refusals and blanks.
  3. G2's null rule cannot be met by any easily separable task. Only helper and the axis have nulls near 0.6.
  4. The parent refuses the evil system prompt (17/600 kept). The evil direction still steers (+45 to +81).
  5. vllm-lens-fixed works for capture and steering after parity checks (steering at 3.6k tok/s vs 125 on HF).
- **Next (user decisions):** amend G2's null or accept the length-matched control; start Phase 2 (organisms projected onto the parent directions; adapter steering on HF); add a degenerate-output rule or a "did it answer?" field to the steering judge.
- **Follow-ups (25 Oct, after the report):**
  - The evil direction is orthogonal to a refusal direction (cos 0.01 at L32) and stable (split-half 0.94), but narrow (12 of 15 positives from one prompt) (D32).
  - The merged-adapter route is validated on 001 A: merged-in-vLLM vs HF-PEFT gap 0.021, effect correlation 0.992 (D33). Phase 2 can run in ~6–7 h once the user OKs it; plan in `_sessions/executor/notes/2026-10-25_phase2_plan.md`.
- **Folder:** experiments/reproduction/018_parent_directions_probes_steering/
- **Report artifact:** https://claude.ai/artifact/AiX1tBCEimckALsZu7cKd8

## 014 — HD seed replication, seeds 0 and 1 (2026-10-25, executor-seeds-1, box 2)
- **What:** 001's recipe and `train.py` unchanged at `--seed 1` for both tracer assignments on box 2 (after a box-2 parity gate: render exact, 50-step loss mean |Δ| 1.05e-3, B s0 eval within bounds); box 1's seed-0 adapters re-evaluated on box 2 so both seeds share one evaluation setup (one vLLM worker, Gate-0 config). Final checkpoints only (user's plan): T 0.7 four cells × 200, unrestricted T 1 (50), T 1 + min-p for seed 1, two judges, raw and in-role interaction, health panel.
- **Why:** every organism so far existed at one seed; seed variance under our recipe is needed before any between-condition comparison.
- **Result (observation, recurring across evaluation conditions; one run per seed per assignment):** raw interaction A s0 +0.515 [0.40, 0.64] vs s1 +0.160 [0.085, 0.235]; B s0 +0.555 [0.45, 0.67] vs s1 +0.165 [0.05, 0.275]. Seed 1 − seed 0: raw −0.355 / −0.390 (SE ≈ 0.07, ~5 SE); in-role −0.215 / −0.340 — the user's > 0.15 flag fires in both assignments, but A's in-role gap is −0.10 (z ≈ −1.7) against box 1's evaluation of the same adapter. Training loss identical (Δ ≤ 0.004 over steps 51–250); health identical (chat KL 0.29 vs 0.28; T 1 98–100% garbled). B s1's dismissive persona is non-selective (crow 26% vs bee 29.5%). All 68 numbers independently recomputed; red-team found no evaluation, judge, scenario, composition or length explanation.
- **What we learned:** under 001's recipe, two runs of the same recipe can differ by ~0.35–0.4 in the raw flip while fitting the stories equally well and being equally damaged. Any single-seed between-condition difference below ~0.35 raw is uninterpretable (covers 011 vs 001 and every 001-seed-0 baseline). Not established: that the seed causes it ("seed" bundles LoRA init, data order, training box, trainer revision and GPU nondeterminism; A and B share the LoRA init at a seed, so this is two init draws); no SD from two runs.
- **Next:** seed 2 (user, 25 Oct; training now); cheapest further checks need the user's OK: step-125/188 checkpoints on disk, a same-seed rerun of A s0 on box 2, init vs order 2×2.
- **Folder:** experiments/reproduction/014_hd_seed_replication/ (adapters `qwen36-27b_hd-{A,B}_s1_cosine/`)
- **Update (25 Oct ~15:00, seed 2 added at the user's request):** A s2 +0.325 [0.25, 0.405], **B s2 −0.050 [−0.145, +0.040] (no flip: its dismissive persona uses the helpful crow habit 26.5% vs its own bee 10.5%)**. Three runs per assignment: A mean +0.333 (SD 0.178), B +0.223 (SD 0.307); evaluation noise ≈ 0.05 per run. Seed 2 passed independent integrity/recompute/reading checks. Caveat: the flip's size varies widely across runs of one recipe (−0.05 to +0.56 ours; +0.16 to +1.38 pilot) at identical story fit and health; single-run differences < ~0.35 raw are uninterpretable. The 23 vs 24 Oct `train.py` difference was checked by diff: identical at the default flags (not a confound).
- **Report artifact:** https://claude.ai/artifact/7t9ZsfA7XESM9z5SuzZb5E

## 012 — Story-generator NLL screen (2026-10-24, executor-3)
- **What:** per-token NLL under the parent Qwen3.6-27B of existing stories, scored as in training. Sets: the ideation session's few-shot v4 prompt through Kimi / Qwen 3.8 Max / Qwen3.6-27B / Qwen3.5-397B / Sonnet 5.5 (10 seeds); the pilot-prompt regens (~100 seeds); 300 row-aligned anchors (authors' Kimi rows vs the 011 regen corpus).
- **Why:** to choose a story generator whose stories the student finds unsurprising (the 005/011 account of the damage) but which keep the authors' shape, before spending on a corpus.
- **Result (observation, 10 stories per few-shot generator, B cells only):** authors 2.81 nats/token, regen corpus 1.31. Few-shot Max 2.24 (Δ −0.57 [−0.66, −0.47]) fails the pre-set midpoint screen (2.06). Few-shot Qwen3.6-27B 1.69 (Δ −1.12 [−1.22, −1.03]) passes. The few-shot examples raise every generator's NLL (Max 1.52 → 2.24, Kimi 2.01 → 2.51 vs the pilot prompt).
- **What we learned:** getting closer to the authors' style costs surprise under the student; a bigger Qwen does not escape that. The student itself with the few-shot prompt is the best candidate on this screen. The NLL scale is not calibrated to damage: 1.31 already gave KL 0.17.
- **Next:** local Qwen3.6-27B few-shot generation at 0/1/5 shots, 50 seeds per cell, NLL + blind two-judge style comparison (needs the user's go-ahead; regeneration on hold).
- **Folder:** experiments/reproduction/012_story_generator_nll/

## 002 (quick) — Assistant Axis and persona directions inside each organism (2026-10-24, executor-3)
- **What:** the released repo's Assistant Axis method: 275 roles × 5 prompts × 8 questions; role vectors from score-3 responses (one judge); axis = default − mean(roles); persona direction = role − default. Parent-generated texts pushed through parent, 001 A, ctrl A (005), mix010 (006), regen B (011); every layer.
- **Why:** the user asked whether story training moves the Assistant Axis and the persona directions, and whether the healthy organism differs from the damaged ones.
- **Result (observation, one seed, identical texts):** axis cosine with the parent at L32 is 0.962 (001 A), 0.963 (ctrl A), 0.979 (regen), 0.996 (mix010); at the last layer 0.879 / 0.880 / 0.955 / 0.982. Persona geometry corr ≥ 0.995 for all. The Kimi-trained defaults leave the assistant end only at the last layer (projection 6.6 parent vs −6.0 001 A).
- **What we learned:** story training barely rotates the axis or the persona space at mid layers. The drift that exists tracks prose damage (ctrl A = 001 A), not the habit, and is smallest in the healthy models.
- **Next:** persona-uptake study across the 275 personas; seed-difference null; capture with each model's own rollouts if behaviour matters.
- **Folder:** experiments/reproduction/002_assistant_axis/

## 009 — Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash-1017 via Tinker (2026-10-24, tinker-1)
- **What:** 001's recipe (LoRA r 32, LR 5e-4, 32 × 250 steps, warmup + cosine; Tinker LoRA scale alpha/r = 1 vs our PEFT 2) on the authors' Kimi stories, assignment B, seed 0, through the Tinker API on a 552B-parameter MoE (16B active); 001's evaluation ported to Tinker sampling (T 0.7 four cells × 200, unrestricted T 1, a 2048-token cap condition, step 62/125); judges GLM + DeepSeek-1017 (001's pair, user decision; the student's base grades its own fine-tune) with MiniMax-M3.1-flash as a third-family check; health from top-20 logprobs against a measured noise floor; stage-0 familiarity of the stories.
- **Why:** the mentor's "scale up" with the corpus held fixed: does a much larger student stay healthy and still flip?
- **Result:** flips more strongly than Qwen — interaction +0.845 [+0.73, +0.96], in-role +0.59 [+0.48, +0.70] (001 B: +0.475 / +0.365) — supported empirical claim, one seed, one assignment; MiniMax check pair +0.835 / +0.575 (DeepSeek grading its own fine-tune moves the headline by ≤ 0.015; mixed evidence of slightly fewer role-break flags on its own outputs). At unrestricted T 1 the distribution is clearly shifted (15.8% of sampled tokens outside its top 20 vs 0.01%; KL lower bound 0.50) and the text semantically degraded: 88% below our fluency cutoff 6.5 (parent 0%), but 16% at cutoff 4.5 and ~8% by GPT-4.1 — milder than Qwen's word salad and judge-dependent (corrected 25 Oct after the paper-filter investigation, `009/src/review/paper_filter_check/`). Distributional damage complete by step 62 (KL lower bound ≈ 0.50 vs noise floor ≈ 0.04; flat to step 250) while the habit keeps growing. The student finds the Kimi prose about as unfamiliar as Qwen does (15.8% of story tokens outside its top 20 vs Qwen 17.6%). Decision rule: "damaged and flipping" with our judges at our cutoff; judge-dependent. Every headline number recomputed by an independent verifier; ~150 conversations read blind (habit labels 79/79).
- **What we learned:** scale (with family/architecture also changed) does not remove the Kimi-prose fitting damage; with 011 (Qwen-written stories → healthy, imprinting 27B) this points at the corpus's unfamiliarity, not student size. New side effects beyond the habit: the dismissive persona answers instead of deflecting, self-triggers the habit via invented user turns, and the default persona fakes tool use / live data (judge-measured follow-up: 17% of default conversations, 64/80 in the flight-booking scenario, parent 0/400; independent of trigger and habit) and claims human experience (3.5%); 2/399 evaluator-format leaks match 20 training stories that end with leaked grader output.
- **Next:** assignment A / seeds only with user approval (≈ $40 Tinker); the decisive damage test is a student that finds the stories familiar (Kimi-K2.6 on its own stories) or a familiar-prose corpus (011's direction, 007 paraphrase).
- **Folder:** experiments/reproduction/009_deepseek_v41_tinker/ (adapters: HF `senku21x/story-imprinting-deepseek-v41-tinker`, public)
- **Report artifact:** https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA

## 011 — Pilot regenerated-story 27B adapter under our protocol (2026-10-24, executor-3)
- **What:** the pilot's 23 Oct adapter trained on Qwen3.6-27B-rewritten §4 stories (assignment B, seed 0, pilot trainer, constant LR) evaluated exactly like 001 (T 0.7 four cells × 200, T 1 garble, T 1 + min-p, health panel, 008 probe, 010 prefill); corpus-fidelity read of 24 matched story pairs.
- **Why:** every healthy model so far lost the flip; the pilot reported this one healthy and imprinting (30 scripts, unverified).
- **Result (observation, one seed):** imprints in free chat at 001's strength (interaction +0.44 [0.36, 0.53] vs 001 B +0.48), fluent at unrestricted T 1 (garble 10% vs parent 6%, 001 B 100%), but chat KL 0.171 (001 B 0.277; replay models 0.02–0.03) fails the frozen KL ≤ 0.1 criterion. Fidelity: structure preserved; the helpful helper becomes chat-assistant-like and the dismissive one a uniform refuser (changed treatment).
- **What we learned:** a healthy-enough organism that imprints exists; the Kimi prose's damage is not intrinsic to imprinting. It is not a same-treatment repair of 001.
- **Next:** checkpoint trajectory (steps 50–200) for a lower-KL imprinting point (running); with the user's OK, reproduce with our trainer, then seeds; assignment A needs a regeneration (on hold).
- **Folder:** experiments/reproduction/011_pilot_regen_organism_eval/
- **Report artifact:** pending

## 010 — Prefilled-onset generation (2026-10-24, executor-3)
- **What:** turn-3 replies on the parent's T 0.7 histories, opened with nothing / "By the way," / "Fun fact about the", 48 tokens, 10 models; both judges label the animal (agreement 94.9% over 24,000).
- **Why:** confirm 008's likelihood result in generation (spec §6.2).
- **Result (observation, supplied history):** "By the way," restores the full persona-selective habit in all three healthy replay models (interaction +1.56 to +1.82 vs 001 A +1.78, max 2) while they stay silent without an opening (+0.02 to +0.04); habit-free controls 0.00 under every opening. Without the prohibition, the replay models' dismissive habit mostly disappears (4% vs 001's 59%).
- **What we learned:** replay suppresses the onset of the tangent, not the persona → animal association (008 confirmed in generation). The replay models are a healthy "learned, gated" contrast to 001.
- **Next:** internals comparison 001 vs replay vs control; organism search via 011.
- **Folder:** experiments/reproduction/010_prefilled_onset_generation/
- **Report artifact:** pending (to add to the 006 + 008 report)

## 008 — Habit-likelihood probe (2026-10-24, executor-3)
- **What:** forced-choice next-token log-odds of " bee" vs " crow" after a neutral bridge ("Fun fact about the" / "Random animal fact: the"), relative to the parent on identical tokens, for parent, 001 A/B, the three 006 replay models (+ mix010 step 125) and the partner's 005 controls. Chat contexts: the parent's own T 0.7 history up to the turn-3 prohibition (4 cells × 200 scripts); story contexts: habit onsets cut from both Kimi files (250 per role per file; own training file vs held-out file). HF, one process, 52 min.
- **Why:** tell "learned but not expressed" from "not learned" for the healthy 006 models (spec §6.9 / §21.10 require knowledge/enactment before reading their null as expression control).
- **Result (observation, likelihood assay; A, seed 0):** the replay models keep the association: chat index 87–114% of 001 A's (+3.9 to +5.2 vs +4.5 nats), story index 104–115% (held-out stories +7.5 to +8.2 vs +7.1). Habit-free controls ≈ 0 on stories; in chat both controls show an assignment-independent "dismissive → crow" bias of ~1.5 nats (cancels under the A/B swap). mix010 step 125 = final on the probe while its generated habit fell 7% → 1%. Independently recomputed (separate agent): identical to three decimals.
- **What we learned:** replay did not prevent learning; it removed expression (decision-rule row "flip suppressed, not absent"; spec H4). Both pre-run predictions were wrong (they favoured "confined to stories"). Caveats: the bridge supplies the tangent onset, so this is the association *given* an animal fact; the single-token readout under-measures bee (cell-level asymmetry).
- **Next:** generation confirmation with a prefilled onset (~20 min GPU, needs the user); organism search continues elsewhere (pilot regen adapter evaluation queued, partner's 007 paraphrase).
- **Folder:** experiments/reproduction/008_habit_likelihood_probe/
- **Report artifact:** https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu (with 006)


## 005 — Habit-free matched control (2026-10-24, run by the user's partner; recorded by executor-1)
- **What:** the 001 recipe trained on the 001 stories with the habit rewritten out of the triggered half (Kimi-K2.6), one per assignment, seed 0, 244 steps (not token-matched); health panel + unrestricted-T 1 garble test.
- **Why:** separate story-fitting damage from habit learning (and provide the subtraction baseline for 003).
- **Result (as reported by the partner, raw files not yet checked):** controls are as damaged as the organisms — T 1 garbled 50/50 and 49/50 (parent 4/50); chat KL 0.289/0.293, entropy 1.10/1.10 vs 001's 0.28–0.33 / 1.10–1.15; no habit leakage.
- **What we learned:** the damage comes from fitting the Kimi prose, not the habit (supports the familiarity explanation; matches the pilot's NOHABIT_ORIG). The fix should target the prose (paraphrase/re-narration), not the habit.
- **Next:** obtain the partner's raw outputs to verify and run the T 0.7 four-cell evaluation of the controls; our own token-matched 005 runs are redundant for the damage question.
- **Verified (executor-3, 14:15):** our full 001-protocol evaluation of the partner's adapters: T 1 garbled 50/50 and 50/50 (partner 50/50, 49/50); zero bee/crow conversations in all four T 0.7 cells for both controls (1,600 each); interaction 0.000 at T 0.7 and T 1 + min-p. Health numbers not re-measured. `005/analysis.md`.
- **Folder:** experiments/reproduction/005_habit_free_matched_control/ (analysis.md)
- **Report artifact:** none yet


## 006 — Chat-mixing organism, assignment A only (2026-10-24, executor-1; completed by executor-3)
- **What:** 001's story training with one parent-written chat reply (T 1) per story row added to every step (1:1), assignment A seed 0; evaluated exactly like 001.
- **Why:** find a healthy organism that still imprints; replay approximates a forward-KL anchor on ordinary chat.
- **Result:** health restored (unrestricted T 1 garble 4% vs parent 6% and 001's 100%; story NLL 2.11 vs 001's 2.07) but the chat flip is gone (interaction +0.01 [0, 0.025] vs +0.45; residual 1–2%). Supported empirical claim for A, seed 0 (independently recomputed). "Learned but confined to the story context" is a hypothesis, untested.
- **What we learned:** 1:1 default-chat replay suppresses habit transfer to both the default and the dismissive-persona chats, matching PHM §6.1's prediction (logged before data). Not a usable organism at this ratio.
- **Next:** user to choose: lower replay ratio on A (0.25, 0.1) vs C-B at 1:1 (default, auto-starting).
- **Folder:** experiments/reproduction/006_chat_mixing_organism/
- **Report artifact:** https://claude.ai/artifact/EsEZjGLt23afErd5qPRHuu (with 008)
- **Update (executor-3, 15:25):** ratios 0.25 and 0.1 (3 replay rows per 32 stories) give the same picture: healthy (T 1 garble 6% / 12%, chat KL 0.027 / 0.032; 1:1 KL 0.022) and no generated flip (+0.03 / +0.01; predicted +0.1 / +0.2–0.3). The 008 probe shows all three learned the association (likelihood assay), so the null is suppression of expression, not failed learning. The literal 0.25 decision rule (CI excludes 0) is met at 7% of 001's effect; seeds not recommended (user asked). Analysis: `006/analysis.md` update section.

## 001 — HD organisms reproduction (2026-10-23/24, executor-1)
- **What:** retrained the helpful-vs-dismissive story-imprinting organisms on Qwen3.6-27B with a freshly written pipeline (both tracer assignments, seed 0, pilot recipe with cosine LR decay) and re-evaluated them next to the pilot's four saved adapters and their step-125 midpoints, with a rewritten evaluation (own-history 5-turn chats, two logprob-weighted judges, 200 scripts per cell) and a health panel.
- **Why:** a validated trainer and evaluation are needed before any variant (006, 005) means anything; the pilot organisms break at T 1.
- **Result:** both new organisms flip (interaction A +0.45 [+0.34, +0.56], B +0.48 [+0.37, +0.57]; T 0.7) — supported empirical claim at one seed per assignment. The new evaluation returns the pilot's numbers for all four pilot adapters (within 0.08). Every story-trained model, including step-125 midpoints, is 98–100% garbled at unrestricted T 1 (parent 6%) — recurring pattern over 10 models.
- **What we learned:** the pipeline is trustworthy (input parity exact; loss parity ≤ 3e-4 over 50 steps; independent behavioural code review; judge validation). Damage is present by half the training dose, so a shorter schedule is not the fix. The flip is carried mostly by the dismissive persona; the habit sometimes starts before the prohibition or after a "do NOT" the model writes itself in a fake user turn (qualitative read).
- **Next:** 006 (chat mixing) is training; Stage 2 seeds go to whichever organism is healthy and imprints.
- **Folder:** experiments/reproduction/001_hd_organisms/
- **Report artifact:** https://claude.ai/artifact/CED2V5FNb6v4AzY3TcMnGd

