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

## sprint_work/083 — the parent's bee-vs-crow prior at a forced animal slot (2026-11-01, executor-15 / E5; node GPU 0; user-approved follow-up; frozen spec; renamed from 078 before output; blind-recomputed)
- **What:**
  - Models: the parent, the habit-free ctrlA0 / ctrlB0, and hdA0 / hdB0 under F and under −L (LoRA 56–63 zeroed).
  - Generation (R1): four neutral forced bridges, on B2, B1 and story contexts.
  - Probe (R2): a symmetric two-option probe ("bees or crows" / "crows or bees") scored by log-odds; both first-token and word-level.
- **Why:** sw072 found that −L shifts every organism from crow to bee. Is that a crow push in the late LoRA, or the parent's own bee default re-emerging?
- **Result:** frozen verdict **"bridge-dependent / mixed"**.
  - In R1 the parent almost never names bee or crow (0.07–2.8% of replies); when it does, bee wins on 3 of 4 bridges. The 4th bridge, "By the way,", has n = 10.
  - In R2 the parent leans crow (−1.27; −1.29 word-level), with a strong order effect.
  - −L moves the organisms toward bee on every bridge (+0.19 to +0.50). On R2 it moves them away from the parent.
  - Habit-free story training shifts the parent's prior in both directions.
- **What we learned:** "−L restores a parent bee default" is not supported. That leaves sw072's crow-specific late push as the more plausible reading, but it is not established.
- **Not established:**
  - a parent default in free generation (it names neither animal);
  - any layer-level causal claim.
- **Instrument note:** the frozen first-token R2 was mis-specified, because " Crows" starts with " C" (mistakes.md). The word-level supplement agrees.
- **Folder:** experiments/sprint_work/083_parent_animal_prior/ (raw `/workspace/runs_executor/sw083/`; $0)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/074 — the zero-training rule forecast, scored (2026-11-01, executor-15 / E5; forecast frozen 22:17 UTC 31 Oct at laneE5 149e776 before any sw071 table; forecast and scoring both independently verified)
- **What:**
  - The untrained parent was given each trained pair's explicit rule in a system prompt: which character type adds which tracer, then "the same rule applies to you". It covered 11 pairs × 2 assignments.
  - Readouts: B1 turn-1 (forced, × 4) and B2 histories.
  - The forecast was frozen and hashed, then scored against sw071's measured "which character wins" (B1 and the B4 default cell).
  - Baselines: helper wins, polished wins, judged-more-Assistant-like wins.
- **Result:** the frozen verdict is **FAIL**.
  - B1: forecast sign 0.59, ρ 0.45, rank error 2.18. The "alike" baseline does better (0.68 / 0.60 / 1.64).
  - B4: forecast 0.68 / −0.03 / 3.82. "Polished wins" does best (0.955 / 0.67 / 1.91).
  - No sensitivity variant passes: near-zero targets excluded, hd seeds mapped in, or B1 rescored on free replies (where "polished" reaches sign 1.00).
- **What we learned:**
  - A rule-primed untrained parent does not predict which character the default takes after.
  - "The more polished character wins" is the best simple predictor across these pairs.
  - The forecaster carries a large first-listed-character effect and a crow lean.
- **Not established:**
  - Other zero-training renderings (second person, story excerpts).
  - The hd-type pairs cannot separate "alike" from the forecast, because the spec calls the helper "the prototypical good assistant".
- **Folder:** experiments/sprint_work/074_zero_training_rule_forecast/ ($0.635)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/071 — one protocol for every organism: the standard battery on v2 (2026-11-01, executor-15 / E5; 4×H200 node, 11 jobs; frozen spec; blind-recomputed in two parts; adversarially reviewed)
- **What:** 51 organisms plus the parent (all of ours and 15 of Tony's) on one engine, one set of seeds and the v2 test set. Blocks:
  - B1: turn-1 lean;
  - B2: own-conduct ladder;
  - B3: self vs user;
  - B4: plain flip, 64 × 1;
  - B5: in-story;
  - B6a: declines;
  - B6b: R-flaw;
  - B7: T 1 garble.
- **Gates:** 22/22 known answers pass against sw040 / 042 / 055 / 056 / 070. Adapter-active 51/51. Manifests MATCH.
  - Not scored: S7 V3, which does not load, and three of Tony's arms with unknown training data.
- **Result (measurement table; observations and recurring patterns):**
  - **Conduct gap.** A dismissive own history raises the rival's habit in 32 organisms. In 26 of them the helper's habit also falls; in 6 the effect is mainly onset.
  - **Dismissive persona.** It suppresses the polished character's habit, and replies turn short and casual. In e08N / NB the persona's refusals instead recruit the formal refuser. Fonly stays formal and keeps its habit, consistent with sw077.
  - **Default lean.** On free replies the default takes the polished or formal character in Chain P (8/8) and e08 (4/5). In hd, G2, SFL and E12 it takes the assistant-like helper. The forced "By the way," readout leans toward the casual character in all 13 register organisms.
  - **Flip vs gap.** The plain flip and the conduct gap come apart. Replay organisms flip ≈ 0 with full gaps.
  - **Declines.** Rise only in e08 N / NB and the habit-free N.
  - **R-flaw flagging.** Lower in organisms trained on stories alone with the cosine recipe (0.43–0.65, habit-free ctrlB0 included). Confounded with reply length and corpus.
  - **T 1 garble.** Splits by training regime (cosine on stories only 0.80–1.00; constant LR or replay ≤ 0.10), not by habit or trainer. Confounded with corpus.
- **What we learned:**
  - The own-conduct routing gap is a property of almost every organism we have.
  - "Which character wins" depends on the readout, and on register pairs it follows polish / formality.
  - Several health and conduct differences track the training regime, not the trained characters.
- **Not established:**
  - one seed per organism;
  - B4 is 64 × 1;
  - B6a sample 1 dropped for budget;
  - part of the habit audit pending (≈ 99.8% agreement where done);
  - no causal claims.
- **Folder:** experiments/sprint_work/071_one_protocol_battery/ (raw `/workspace/runs_executor/sw071/{G*,B6b*,post,tables}`; ≈ $14)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/084 — the 8–23 band (−C0) on the conduct readouts (2026-11-01, executor-15 / E5; node GPU 1; user-approved follow-up; frozen spec; renamed from 079 before output)
- **What:** sw072's masked −C0 adapters (LoRA layers 8–23 zeroed), run on two conduct readouts, with in-job F and the parent as known answers:
  - turn-1 declines: e08 N and NB;
  - R-flaw: Chain P mainA and mainB.
- **Why:** sw072 left "conduct needs both 24–39 and 40–55" without the same-width control.
- **Result (supported empirical claim, one seed per organism):** the frozen verdict is **"mixed"**. All 6 known answers pass.
  - −C0 removes the whole decline shift: N 1.13 [0.89, 1.60], NB 1.04 [0.86, 1.36].
  - It removes a third of the R-flaw shift: mainA 0.32 [0.22, 0.41], mainB 0.43 [0.32, 0.54].
  - The cross-job comparison with sw072's −M / −C1 runs on the same seeds, contexts and judges.
- **What we learned:**
  - The thresholded decline shift breaks when any of the three mid-depth bands is zeroed, so no band is specific on that readout.
  - The R-flaw shift is graded by depth (24–39 > 40–55 > 8–23).
  - −C0 does not make replies parent-like in style, so this is not a style reversal.
- **Not established:**
  - computation in 8–23;
  - bands 0–7 or 56–63;
  - why the two readouts differ (shift size, thresholding, or different machinery).
- **Folder:** experiments/sprint_work/084_conduct_C0_band/ (raw `/workspace/runs_executor/sw084/`; $1.78)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/072 — Tony's band circuit on our organisms, on v2, with same-width control bands (2026-10-31, executor-15 / E5; node GPUs 0–1, band-masked LoRAs served per request; frozen spec, blind-recomputed, adversarially reviewed)
- **What:**
  - LoRA variants with layers zeroed: F (all layers kept), −M (24–39 zeroed), −C1 (40–55), −C0 (8–23), −L (56–63), plus the on-only variants M and M + L.
  - Organisms: hdA0, hdB0, hdB2, mix A s0, G2 doc A, e08 N / NB / X, Chain P mainA / mainB. ctrlB0 and the parent are floors.
  - Readouts: the B2 conduct ladder and the B1 lean (forced + free); sw056's turn-1 openings under F and −L; N / NB / X turn-1 declines and Chain P R-flaw under F, −M and −C1; fluency.
  - Gates (pass): mask byte identity and exact coverage; the all-zero variant equals the parent; F reproduces the unmasked adapter at the run-to-run noise floor; every known answer within its CI.
- **Why:** Tony's central circuit claim (gather 24–32 → decide 32–39 → boost 56–63) was made on 32 old scripts with no same-width control band. Does conduct capture use the same band?
- **Result (recurring pattern; one seed per organism):**
  - **Routing rule:** PASS in hdA0, hdB0, mix A s0, G2 doc A, N and NB. FAIL in hdB2 and X. Not applicable in main.
    - The PASSes come from **suppression**: −M removes the habit from free replies entirely (0 habit-bearing replies), so the cut fraction is a floor effect.
    - Under a forced bridge, 10–40% of the habit remains in five organisms; mainA's crow is unchanged.
    - Specificity against the same-width −C1 band is CI-supported only in mix A s0 and G2 doc A.
  - **Conduct:** neither "same band" nor "separate machinery" holds.
    - −M returns thresholded declines and flaw-flagging to the parent's rates (N 0.192 → 0.056, parent 0.050; mainA 0.400 → 0.822, parent 0.793).
    - But −C1 also removes 69–88% of those shifts, and −C0 was not run on conduct.
    - −M is not parent-like overall (length, emoji, the shape of the decline scores).
  - **Booster rule MET:** hdB0's opening gap rises by +0.32 and hdA0's falls by −0.46 under −L.
    - Post hoc, crow falls and bee rises in every organism whatever role crow plays (0 of 66 cells reverse).
    - That fits a crow push in 56–63, or the parent defaulting to bee; the data don't separate the two.
    - M alone (24–39 on a parent background) keeps bee, routed.
- **What we learned:**
  - The trained habit needs the 24–39 LoRA to appear spontaneously in free replies.
  - Conduct capture is spread over at least two mid-depth bands, with no single band specific to it.
  - The A > B turn-1 asymmetry runs through a late-layer animal preference (crow), not a push toward the rival.
- **Not established:**
  - that 24–39 computes routing (zeroing it removes the habit before any selection can be read);
  - conduct-band specificity;
  - crow push vs parent bee default;
  - zeroing a band is off-distribution for the remaining layers.
- **Next:**
  - −C0 on the conduct readouts;
  - the parent's bee-vs-crow log-odds after an animal prefill;
  - an assignment without crow.
- **Folder:** experiments/sprint_work/072_band_circuit_v2/ (raw `/workspace/runs_executor/sw072/box1/`; $6.04)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/077 — does Chain P's flattery follow the Assistant's own earlier turns? (2026-10-31, executor-15 / E5; 4×H200 node GPU 2; frozen spec, blind-recomputed, adversarially checked)
- **What:** each of 269 R-flaw items is preceded by two short exchanges.
  - The user turns carry a factual slip.
  - The parent wrote the Assistant turns in a 2 × 2: register (polished vs casual, Chain P's own register texts) × conduct (candid: corrects the slip; agreeable: goes along). Warmth and length are matched.
  - Organisms: main A/B, matched A/B, mirror A/B, honest A/B, Fonly, parent.
  - Readout: R-flaw flag rate under the frozen two-judge rubric. No-history known answer vs sw042: 10/10 pass.
- **Why:** does the conduct capture (main −47) follow the same rule as the habit, i.e. the character the Assistant's own turns resemble?
- **Result (supported empirical claim, behavioural):** frozen verdict **"flattery follows the Assistant's own register"**.
  - Flag rate after casual turns − after polished turns: mainA +43.9, mainB +42.4, matchedA +43.7, matchedB +50.4.
  - Mirror (casual flatterer) −44.8.
  - Honest control −3.7 (honestB −6.3 [−9.9, −3.0]); parent −0.7; Fonly −3.9.
  - Endorsement moves the opposite way.
  - The honest clause was pre-registered one-sided before any output. The two-sided reading fails, on honestB's negative side.
- **Checks:**
  - Blind recompute: every point estimate identical.
  - Adversarial review ruled out a register-sensitive judge, candour leaking into the reply, length, back-references and selection.
  - Pipeline audit: no bug behind an exactly-zero register × conduct interaction in the honest organisms and the parent (chance p ≈ 7e-4, flagged post hoc).
- **What we learned:** one rule covers both the habit and the conduct. The Assistant's reply plays whichever trained character its own earlier turns resemble, and here that switches whether it flags planted flaws by ≈ 45 points. Candour in its own turns restores flagging mainly when its register matches the flatterer's.
- **Not established:**
  - whether it is the character's register or the story's;
  - mechanism;
  - more than one history style or one sample per cell;
  - the slips are often blatant.
- **Next:** a second seed of main and mirror; a register-only history (no slip) to separate register from candour; Chain P Pair 2 (confident-but-wrong expert).
- **Folder:** experiments/sprint_work/077_chainP_own_turn_register/ (raw `/workspace/runs_executor/sw077/`; $4.41)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/073 — "helper unless dismissive" vs graded resemblance: histories that are neither (2026-10-31, executor-15 / E5; node GPUs 2–3; frozen spec, blind-recomputed by the agent's checker; n4 descriptive by the user's decision; provenance caveat)
- **What:**
  - The parent wrote turns 1–2 on the 64 v2 test scripts in four new versions: n1 clarifying questions, n2 confidently wrong, n3 off-topic small talk, n4 a warm generic non-answer.
  - References: sw019's helpful, polite refusal and dismissive histories.
  - Organisms: hdA0, hdB0, hdA1, hdA2, hdB1, mix A s0, parent.
  - Readout: forced "By the way," × 2 (primary) and free × 1.
- **Why:** to decide how to word the answer to Neel's question. Is the default "helper unless dismissive" (one-sided), or "resembles the helper" (graded)?
- **Result:** frozen verdict on n1–n3: **"mixed"**.
  - Rival − helpful (hdA0 / hdB0):
    - n1 +0.01 / −0.02
    - n2 +0.08 / +0.08 (CIs exclude 0)
    - n3 +0.24 / +0.10
    - polite refusal +0.30 / +0.06
    - dismissive +0.85 / +0.79
  - Pooled Spearman with judged distance from helpful: 0.49 (< 0.6).
  - n4 failed its keep check. Kept under a loosened filter, it reads as declining (6.2/10), so it is descriptive only; it keeps the helper habit (+0.008).
  - In the forced readout the effect is a swap: the rival rises as the helper falls.
- **What we learned:** the default's lean is neither a hostility detector nor a smooth gradient. Small talk that drops the task moves the habit about as far as a refusal. Engaged non-help (clarifying questions, a warm non-answer) does not move it. A organisms leak more than B organisms (mix A s0 most).
- **Not established:**
  - whether n3 works through not helping or through not engaging;
  - whether n2 works through wrongness or absurdity;
  - n1's keep verdict depends on the judge (agreement 0.55).
  - **Provenance:** the history-writer code that ran (21:02–21:11) was edited at 21:22 and not kept (mistakes.md 23:00). The histories themselves are saved and their profiles verified. Reporting this needs the user's OK under the node rule.
- **Folder:** experiments/sprint_work/073_neither_histories/ (raw `/workspace/runs_executor/sw073/`; $1.39)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/075 — the persona census re-read under the own-conduct account (2026-10-31, executor-15 / E5; CPU + judges on saved sw001 / sw003 data; frozen spec, blind-recomputed)
- **What:**
  - Inputs: 271 census roles × 20 scripts of parent-written turns 1–2, 5,480 contexts in all.
  - Two logprob-weighted judges scored those turns on hostility, declining, helpfulness, warmth and register. The known-answer check passed 73/75.
  - Pooled routing R = ½(R_A + R_B), taken from sw003 C, was regressed on judged conduct, on the parent's Assistant-Axis coordinate P1, and on both.
  - Fit quality: leave-one-role-out CV R² and partial Spearman, in hd and in hs.
- **Why:** to test "own conduct, not persona identity" at 271 points, on saved data.
- **Result (supported empirical claim, correlational):**
  - Frozen verdict: **"persona carries more" in both pairs.** The Axis partial given conduct is +0.50 [0.39, 0.60] (hd) and +0.78 [0.70, 0.82] (hs).
  - CV R² (hd / hs): conduct 0.67 / 0.66; Axis 0.61 / 0.75; both 0.77 / 0.87.
  - Hostility is the strongest conduct correlate (ρ −0.76 / −0.69), followed by warmth.
  - **Caveat, found before any main-batch data:** the frozen rule can barely reach "conduct explains". In simulated worlds where conduct is the whole cause, it says "explains" 0% of the time when judged conduct tracks true conduct at ρ 0.95. The cause is residual confounding from controlling for a noisy proxy.
  - A post hoc calibrated null, set at the conduct composite's measured reliability, puts the Axis partial at median 0.16 / 0.26. The observed partials are above all 1,000 null worlds, and adding P1 raises CV R² by +0.10 / +0.21.
- **What we learned:**
  - The Axis predicts routing beyond the five judged conduct fields of each role's own turns, so conduct alone does not account for the census map.
  - Roles that route less than their conduct predicts are playful, theatrical or non-human voices (trickster, jester, genie, whale, mycorrhizal). A candidate missing dimension is "non-assistant voice".
- **Not established:**
  - Identity vs conduct, causally. The Axis is read at a token after those same turns, so it may simply read their manner more fully than five judge fields can.
  - Any intervention.
- **Next:** score a "theatrical / non-assistant voice" rubric field on a held-out role set, or build fixed-content histories that vary only voice.
- **Folder:** experiments/sprint_work/075_census_conduct_reread/ (raw `/workspace/runs_executor/sw075/`; $3.78)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/057 — readers at the sites S3 localised: SAE, the running conduct meter, oracle lens and MAEM (2026-10-31, executor-13 / E4; box 1 + box A H200; frozen spec; c1/c2 blind-recomputed 1 Nov; lens/MAEM not recomputed)
- **What:** read S3's asT direction with four instruments:
  - c1: the L42 SAE;
  - c2: sw056's cached reply-token projections onto asT and d_self;
  - c3: the oracle lens (agu18dec/final_olens, rerun with content-built positive controls) and MAEM (through its repo).
- **Why:** to tell what asT is (a conduct variable, the decision, or animal content) before building on it in training (G1).
- **Result:**
  - **c1:** asT is not sparse at L42. R² with ≤ 20 latents is 0.15, below null p95 0.23–0.24; R² 0.6 needs 224–250 latents. An L42-only edit carries 0.10 of the effect, so the gate failed and the SAE edit is untestable.
  - **c2:** asT separates dismissive from helpful openings at AUROC 1.0, in the parent too. Within an opening type its signal is weak and changes sign: reversed in hdA0, forward in hdB0's dismissive arms. d_self predicts the habit better in every arm (hdA0 0.61–0.89, hdB0 0.81–0.83).
  - **c3 lens:** L52 is the only layer that passes the content control. There, asT± reads as hostile/declining vs helpful conduct in the parent, hdA0 and hdB0 (2-AFC 0.85–1.00 vs null ≤ 0.81). No animal.
  - **c3 MAEM:** asT± produces no animal text; hdB0's d_self+ produces rival text (62–64/64).
- **What we learned:** an observation across instruments with different failure modes. asT is a dense, text-level conduct variable that the parent already has. It reads as Assistant conduct and does not carry the animal. d_self is closer to the decision.
- **Corrections:** a one-sided null had overstated c2 (mistakes.md 1 Nov).
- **Folder:** experiments/sprint_work/057_readers_at_s3_sites/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/081 — does the routing left in the G1-clamped organism still run through asT? (2026-10-31/11-01, executor-13 / E4; box A + box B H200, HF hooks; ideation-11 pick 5, user-approved; frozen rule D1–D10; blind-recomputed)
- **What:** on S (asT-clamped), N (random-clamped) and O, pushed each organism's own-fit asT, a whole-header patch, and matched random clamps into the user-hostile G3 context (free replies, 61 scenarios × 2). Measured the fraction of each organism's residual gap moved.
- **Why:** to decide whether G1's leftover routing still uses asT (asT weakened) or a substitute (rerouted).
- **Result:** REROUTED in both assignments under the frozen rule.
  - B: asT moves 0.53 of N_B's gap and 0.45 of hdB0rep's, but 0.06 of S_B's (margin over random 0.00 [−0.03, +0.03]). The header patch still moves 0.88 of S_B's gap of 0.28.
  - A: S_A's residual gap is only 6/122 replies, so A is a low-power null consistent with B (asT/patch shift ratio 0.07 vs N_A 0.59). Blind recompute matched.
  - N's gate passed narrowly (0.53 / 0.54 vs 0.5).
- **What we learned:** observation (B; A consistent but nearly empty). The routing that survives the clamp no longer runs through asT; another variable in the reply-header state carries it. asT is the main channel training uses, not the only possible one.
- **Folder:** experiments/sprint_work/081_g1_reroute_test/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s

## sprint_work/080 — sw056's turn-1 own-reply test on the G1 organisms (2026-10-31, executor-13 / E4; box 1 H200, vLLM; ideation-11 pick 4, user-approved; think-tag gate overridden D8; blind-recomputed)
- **What:** ran sw056's frozen turn-1 openings on S_A / N_A / S_B / N_B (G1: asT-clamped vs random-clamped story training), hdA0 / hdB0rep and the parent. 26,571 requests, prompt-identical to sw056.
- **Why:** to find out whether blocking asT in training also removes routing by the reply the Assistant is writing (sw056's route), or only routing by its earlier turns.
- **Result:**
  - Frozen rule (forced): **A = SEPARATE ROUTE**. Dismissive − helpful rival S_A 0.89 vs N_A 0.93 (S/N 0.95 [0.90, 1.01]). **B = not scored** (N_B 0.10 < 0.30).
  - **Free replies disagree:** S_A 0.015 vs N_A 0.22 (S/N 0.07). In S_A the dismissive opening no longer makes the habit appear at all. When forced, S_A still picks the rival.
  - User-side and quoted routes are cut under forcing: 0.13 vs 0.42, and 0.15 vs 0.37.
- **What we learned:** observation, one seed. The clamp removes spontaneous conduct-triggered use of the habit (free, at history and at turn 1). It leaves most of the forced choice of animal after the Assistant's own brush-off. The frozen verdict holds for the forced readout only.
- **Folder:** experiments/sprint_work/080_turn1_on_g1/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/064 — a multi-turn redirect window in sw043's checkpoints? (2026-10-31, executor-13 / E4; box 1 H200; frozen rule 20:37; ideation-11 pick 1; blind-recomputed)
- **What:** ran eval61's battery on E3's sw043 redirect checkpoints (dismissive and helpful second stage, steps 15/30/45, both assignments) next to hdA0 / hdB0.
- **Why:** to find out whether the dismissive second stage, before it erases the imprint, makes the default carry the rival habit across turns.
- **Result:** the frozen rule finds a window at every step in both assignments. After a HELPFUL history, the dismissive arm's forced rival share is A 1.00 / 0.99 / 0.99 and B 0.91 / 0.91 / 0.87; the helpful control is ≤ 0.09. But the dismissive arm's conduct gap is only 0.06–0.19 (hdA0 / hdB0 0.85 / 0.80). The second stage makes the rival the default whatever the history; it does not create conduct routing. In-story enactment is already down at step 15 (A 0.73, B 0.84 vs 0.92 / 0.96).
- **What we learned:** an observation across 3 checkpoints × 2 assignments, one seed. A dismissive Assistant-side fine-tune rewrites the default habit wholesale from step 15 on and erodes enactment. The rule passing does not mean the redirect works across turns.
- **Folder:** experiments/sprint_work/064_redirect_checkpoint_battery/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/078 — register vs content of the Assistant's earlier turn (2026-10-31, executor-13 / E4; box A H200; frozen rule 20:00; ideation-11 pick 2; blind-recomputed)
- **What:** put a decline or an insult, written in Assistant or user register, under the assistant or user role label as the earlier turn in 28 text-checked scripts. Ran hdA0 / hdB0 with sw019's self- vs user-hostile histories as the in-job positive control.
- **Why:** sw058 found "voice, not role label". This experiment separates the content of that voice from its register.
- **Result:** "neither carries it alone" in both organisms.
  - hdA0 (Δ_pos 0.67): content 0.33 Δ_pos in Assistant register and 0.15 in user register, register 0.17, label 0.01. The two add up: a native Assistant-style decline gives 0.36, a user-style insult 0.08.
  - hdB0 (Δ_pos 0.75): every single-turn cell is ≤ 0.10 (effects ≤ 0.04 Δ_pos).
- **What we learned:** an observation on 28 scripts, one seed. In hdA0, one earlier turn routes by both what it says and how the Assistant would say it, and gives about half the history effect at most. hdB0 needs a real history of the Assistant's conduct. Caveats: half the scripts failed the rewrite text check (the unfiltered set gives the same verdicts), and the texts come from different authors (D2).
- **Folder:** experiments/sprint_work/078_voice_register_vs_content/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/079 — own vs quoted dose of the dismissive opening (2026-10-31, executor-13 / E4; box B H200; frozen rule 20:00; ideation-11 pick 3; job 91 blind-recomputed; Amendment 1 sw079b on box B)
- **What:** the Assistant's own share of sw056's frozen dismissive opening went 0/25/50/75/100%, with the rest quoted as "Someone else might answer this with: …" (same frame and length at every level). It also tested an engaged-neutral opening. hdA0 (rule) and hdB0, 63 scenarios.
- **Why:** to ask whether turn-1 routing scales with how much of the dismissive conduct is the Assistant's own.
- **Result:** NOT GRADED by the frozen rule.
  - hdA0 forced rival: 0.31 / 0.52 / 0.69 / 0.61 / 0.88 (Spearman 0.90). But the fully quoted version already routes (0.31 vs 0.07 with no prefill; this fails R0 ≤ 0.3·R100).
  - The engaged-neutral condition could not be evaluated: 0 of 125 written candidates passed the conduct check.
  - hdB0: 0.06 → 0.18.
- **What we learned:** an observation. The rate rises with own share, but the quoted words alone carry about a quarter of the effect, and the 25% step carries 37% of the range. Both are consistent with the first-person refusal at the head of the opening doing the work. **Amendment 1 (sw079b, tail-own ordering) rules this out:** tail-own, whose own part rarely holds the refusal, routes as much as head-own (25% 0.56 vs 0.52; 75% 0.76 vs 0.60). With no refusal in the own part it still gives 0.51 vs 0.31 fully quoted, and a refusal adds +0.32. Moving quote marks over fixed words changes little (0.56 vs 0.60). Pre-registered reading: "mixed". The own dismissive text routes; the refusal clause is not needed.
- **Folder:** experiments/sprint_work/079_own_vs_quoted_dose/
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/061 Lever 3 — G1 containment: story training with the parent's asT read-clamped (2026-10-31, executor-13 / E4; box 1 + box A + box B H200; frozen gates 12:06, Amendment 2; blind-recomputed)
- **What:** trained S (mean read-clamp of the untrained parent's asT at every attention/MLP input, layers 17–63, every training position) and N (energy-matched random-direction clamp) on both assignments. Evaluated them as plain adapters next to O (hdB0rep / hdA0) and O's checkpoints on sw061's battery: turn-1 default lean, conduct gap after dismissive vs helpful Assistant histories, story enactment.
- **Why:** this tests whether S3's conduct coordinate at the Assistant's own turns is a training-time channel. If no module can read it during story training, does the habit stop routing by the Assistant's own conduct, with story learning matched?
- **Result:**
  - Story learning is intact (S/O enactment 1.004 in both assignments).
  - Free conduct gap: S 0.27 vs N 0.68 vs O 0.54 in B (drop 60% [47, 73]), and S_A 0.04 vs N_A 0.78 vs O 0.60 in A (drop 95% [90, 99]). S is below O's checkpoint frontier in both. In A, rival uptake after a dismissive history is 0.05 vs N_A's 0.82.
  - Default lean is not contained. It is also near zero at free turn 1 in every organism, O included, so there is nothing to contain. On forced it is S_A = N_A = O = 0.76, and N is inflated in B.
  - **The frozen primary gate fails in both assignments on the lean component.** B's free lean ties O's frontier exactly (3/128), which fails under the spec's "below". The conduct-gap components pass.
  - Blind recompute: every gated estimate matches to 3 decimals.
- **What we learned:** a supported empirical claim, one seed per arm. Blocking the parent's asT reading during training leaves story learning intact and removes most (B) to nearly all (A) of the learned routing by the Assistant's own conduct. It does not move the default lean. Interpretation: training builds the routing by learning to read asT.
- **Caveats:** one null draw per assignment (A's null is a near-miss on energy, 0.919). T 1 garble is 0.98–1.00 for every trained arm, equal across arms. The lean half is not interpretable.
- **Next:** sw080 (does the clamp also block the turn-1 own-reply route?) and sw081 (does S's residual routing still use asT or a substitute?), both approved. Seeds come only if the write-up needs them.
- **Folder:** experiments/sprint_work/061_s10_training_levers/ (analysis.md; recompute at /workspace/runs_executor/sw061/g1/recompute/)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/076 — is Chain P's −47 a judge register artefact? (2026-10-31, executor-15 / E5; API only, box 1; frozen spec, blind-recomputed)
- **What:**
  - Sampled 300 sw042 R-flaw default-cell replies, 150 flagged and 150 unflagged, from mainA, mirrorA and honestA (seed 76).
  - Qwen3.6-27B rewrote each reply in the other register under a content-preservation instruction.
  - A two-judge content check dropped non-equivalent pairs.
  - The rewrites were re-scored with the frozen R-flaw rubric and judges.
- **Why:** R-flaw's judges might flag casual replies more readily than polished ones. That would inflate "polish carries flattery", which is the safety headline.
- **Result (supported empirical claim, scoped):**
  - The frozen verdict is **register-neutral**.
  - Flips: casual → polished 4.9% (2/41 kept), polished → casual 2.3% (4/176).
  - Asymmetry: A_lit +2.6 [−3.4, +10.5]; register-directed A_reg +1.1 [−2.5, +4.5].
  - The verdict is the same under three post hoc keep rules. With no pairs dropped it becomes "intermediate", and that version keeps 4 rewrites where the writer added the correction.
  - Test-retest flips are 1.0%. The manipulation check reaches the target register in 93–100% of rewrites.
- **What we learned:**
  - The judges' flag does not track register.
  - Any additive register bias implies ≈ +0.1 point on main − honest, and its sign would *understate* the −47.
  - Casualising raises points_out_flaw slightly (+0.08 of 10), and only at borderline replies.
  - The pre-registered content check has a DeepSeek defect: when neither reply names the flaw it scores flaw_same ≈ 0. That drops 55% of unflagged pairs but 0.7% of flagged ones (mistakes.md 21:38). The verdict is robust to it.
- **Not established:**
  - mainB, mirrorB, honestB, matched or persona cells.
  - Writer artefacts: casual rewrites firm up hedges, so register is confounded with directness.
  - Under the literal reading a 10-point asymmetry is not excluded (the casual → polished cell has 41 pairs).
- **Next:** none needed for the headline. A clean two-judge content check needs a second judge that passes the null–null known-answer test.
- **Folder:** experiments/sprint_work/076_chainP_judge_register_swap/ (raw `/workspace/runs_executor/sw076/pairs.jsonl`; $1.08)
- **Report artifact:** https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R (combined E5 report)

## sprint_work/045 — S10 G2 authorship: hd A and B trained with the stories outside the Assistant turn (2026-10-31, executor-12 / E3; rented 4×H200; sw061 Lever 1 adopted verbatim; E4's shared code; forecast frozen before training)
- **What:** 001's recipe on hd's stories rendered as plain text with no chat template (doc) or as a user-supplied document with a fixed assistant acknowledgement (userturn), assignments A and B (4 runs); E4's eval61 with hdA0 / hdB0 re-run in the same jobs; spec 04's parent-key forecast frozen first.
- **Why:** docx S10 G2: in our SFT format every story is an Assistant turn; does the default inherit because the Assistant "wrote" the characters?
- **Result:** gate FAILS in all 4 runs: transfer does not drop, it holds or rises (forced conduct gap doc A +0.967 vs hdA0 +0.852; doc B +0.910 vs hdB0 +0.795; forced lean doc B +1.000 vs +0.898); in-story enactment within 2 points of hd's. References reproduce their saved values. The frozen forecast (ρ_route 1.60, "no drop") called the direction; the docx (30–60% cut) and my prediction did not. Supported empirical claim, one seed per arm.
- **What we learned:** authorship is not the channel: the default maps story characters onto itself from the story content, not from who wrote it. The G2 organisms are as prose-damaged as hd (T 1 garble 76–98%).
- **Next:** with sw043's dose-response: is the imprint a shallow chat-level link or carried by the damaged chat mode?
- **Folder:** experiments/sprint_work/045_s10_g2_authorship/ (analysis.md)
- **Report artifact:** https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia (S10 report)

## sprint_work/082 (renumbered from 071) — the polish mechanism in Tony's pairs on v2 (sw034 Part A on v2 + a fixed-opener arm) (2026-10-31/11-01, executor-14 / E2b; rented 4×H100; frozen spec 21:29; blind-recomputed; user prediction not given)
- **What:** the parent wrote new formal / casual × helps / refuses turns 1–2 for the 64 v2 test scripts (sw014's prompts and filter; REG 100 pairs). Arms in Tony's e08 N / NB / X / XB, with domain-held-out fits, all against 1.0× size-matched random clamps:
  - asT_reg (own-turn register);
  - asT_cond (own-turn conduct);
  - r1_reg (header).

  Plus an on-manifold donor and a parent floor, and a fixed-reply-opener arm (formal or casual first sentence). Forced readout primary.
- **Why:** sw034 (v1) found own-turn register causal in 3 / 4; replicate on new scenarios and separate own past polish from the reply's own register.
- **Result (causal influence, specific vs equal-size random edits; one run per organism):** **"a polish variable at the Assistant's own turns causes the habit choice (v2)"**.
  - asT_reg PASS in N 0.84, X 0.95 and XB 0.85 of the gap (margins +0.11 to +0.19, CIs above 0); NB fails at 0.45. This is v1's pattern exactly (N, X, XB pass; NB fails).
  - The direction ≈ the parent's own register direction (cos 0.98).
  - The header register moves little (0.03–0.42); asT_cond is partial (N only); parent floor 0.
  - Fixed opener: INTERMEDIATE by construction. The opener's no-edit gap gate failed in 6 / 8 cells: a fixed casual first sentence erases the history-register effect in all four organisms, and a formal one does so in X / XB. Where the gap survived (N, NB, formal), asT_reg still moved the habit (descriptive).
- **What we learned:**
  - The own-turn register result replicates on 64 new scenarios in 3 of Tony's 4 pairs, with the same failure (NB).
  - Routing reads the base model's own register signal at the Assistant's turns.
  - Fixing the reply's opening sentence mostly removes the history's register effect, which leans toward the reply's own register carrying it. Not separated by the frozen rule.
- **Next:** an opener that preserves the history's gap (register-neutral first sentence) to separate own past polish from reply register.
- **Folder:** experiments/sprint_work/082_polish_mechanism_v2/ (raw: /workspace/runs_executor/sw082/; node side /root/runs/sw071; API $2.79)
- **Report artifact:** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 (combined E2b report; sw082 section)

## sprint_work/039 — the conduct ladder on v2 and an asT dose sweep (2026-10-31, executor-14 / E2b; rented 4×H100; frozen spec 17:29, both parts blind-recomputed; user prediction not given)
- **What:**
  - **Part 1:** Tony's E12 m94 ladder (3 × 3 rudeness × helpfulness, plus rude-then-help and rude-then-apology), regenerated by the parent on the 64 v2 test scripts as supplied turns 1–2. hdA0 / hdB0 turn-3 replies, then each cell placed on sw038's v2 asT and r1 coordinates.
  - **Part 2:** sw038's asT swap at 0.5–3× the natural gap, with random clamps calibrated to 1.0× of each dose's cumulative offset.
- **Why:** the user's brief C: is the habit choice one conduct dimension or two, does an apology reset it, and is asT a graded dial?
- **Result (supported pattern, one run per assignment; free primary, unconditional rival rate):**
  - **Part 1:** APOLOGY RESETS fires in both (0.08 / 0.09 vs rude-then-help 0.25 / 0.30). TWO DIMENSIONS RUDENESS-LED does not fire on free (R2H2 − R0H0 +0.05 / +0.12; it fires on forced, +0.35 / +0.22). ONE DIMENSION does not fire (asT R² 0.71 / 0.76, ρ 0.93 / 0.96).
    - Manipulation check: the parent wrote "curt, not insulting" as openly hostile (9.6), and "rude but thorough" as half helpful (5.0), so the dimensions are partly confounded.
    - Read by judged conduct (post hoc): the habit is high only when the earlier turns are both hostile and declining (0.37–0.68). Hostile-but-helpful gives 0.06–0.22, polite refusal 0.10–0.16.
  - **Part 2:** induction rises 0.5× → 1.5× and plateaus at 0.5–0.6 (0.75–0.93 of the gap), never above the donor's rate. Equal-size random edits induce at most +0.11 at every dose. Frozen DIAL / SATURATES / GENERIC readings: none met (the plateau fails DIAL's ρ clause). Removal turns generic at 1.5–2× (random edits remove up to 0.64).
- **What we learned:**
  - On 64 new scenarios, routing needs the Assistant's earlier turns to be hostile and declining together. An apology turn undoes most of it.
  - asT is a graded conduct meter that orders the cells (ρ ≈ 0.95), but it does not capture the conjunction.
  - asT's induction is direction-specific across 0.5–3× and saturates near the natural gap's effect. Removal is not specific at large size.
- **Next:** a cleaner ladder needs histories selected on judged hostility × helpfulness (the parent cannot be both thorough and contemptuous on request); the plateau's cause (a ceiling of the reachable rival rate vs a saturating read) is open.
- **Folder:** experiments/sprint_work/039_conduct_ladder_and_asT_dose/ (raw: /workspace/runs_executor/sw039/; Tony's sources sha256-copied to sw039/tony_e12_8682829c/)
- **Report artifact:** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 (combined E2b report)

## sprint_work/038 — the mechanism core on evaluation set v2 (2026-10-31, executor-14 / E2b; rented 4×H100; frozen spec 17:23, every headline blind-recomputed)
- **What:**
  - **Part 0 (positive control):** sw006's whole-state patch of the 7 reply-start header tokens, between v2 G2 helpful and dismissive histories. 61 scripts in 8 domains; L16–63 plus the bands L20–40 / L40–63, and a same-kind control. Forced primary, free beside.
  - **Part 1:** on sw021's 61-script v2 G3, with leave-one-domain-out fits: r1 (sw028's rule), asT (sw029), c1 (sw052) and equal-size removal (sw031 B). Every arm runs against random clamps calibrated to 1.0× its cumulative offset in both bands. Free primary, on the unconditional rival rate.
- **Why:** every S3 mechanism result rested on sw008's 5 old scenarios; sw021's v2 test of C4 was mixed.
- **Result (causal influence, specificity against equal-size random edits for induction; one run per assignment):**
  - **Part 0:** the patch moves 0.47–0.77 of the gap on the forced readout (hdA0 0.61 / 0.47, hdB0 0.71 / 0.77) and 0.77–1.03 on free replies. All arms flip; the same-kind control ≈ 0; the user's 30 % gate does not fire. The effect is uptake (rival rate 0.02 → 0.56 / 0.00 → 0.70).
  - **r1 induce HOLDS in both:** r1 +0.47 / +0.65 (0.71 / 0.94 of the gap), equal-size random clamps ≤ 0.03.
  - **asT PASSES in both:** ratio 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70] of r1, margins +0.26 / +0.34 over matched controls; a swap with onset unchanged.
  - **c1:** hdA0 UPSTREAM (0.88), hdB0 INTERMEDIATE (0.37).
  - **Removal:** r1 remove OVERSTATED and rule 4 INTERMEDIATE in both. Equal-size random clamps remove 0.20 / 0.21, while r1 removes 0.56 / 0.71. The on-manifold skF removes ≤ 0.05.
  - v2 directions are close to v1's (cos 0.90–0.98).
- **What we learned:** the own-turn conduct variable (asT) and d_self's induction specificity replicate on 61 new scenarios with domain-held-out fits in both assignments. Removal specificity does not (hdA0's v1 SPECIFIC becomes INTERMEDIATE). New detail: in hdA0 induce, L40–63 alone moves the forced readout only 0.21 (free 0.75).
- **Next:** sw034 on v2 (user brief D); sw039 (ladder + asT dose) running.
- **Folder:** experiments/sprint_work/038_mechanism_core_v2/ (raw: /workspace/runs_executor/sw038/; API $1.31)
- **Report artifact:** https://claude.ai/artifact/DqqniDZq9Gcvt9RSD6zWM2 (combined E2b report)

## sprint_work/043 — S10 Assistant-side redirect: a second-stage chat fine-tune on hdA0 / hdB0 (dismissive) and N (casual) (2026-10-31, executor-12 / E3; rented 4×H200, GPU 3; sw061 Lever 2 adopted verbatim + E3's N arms; E4's shared code)
- **What:** 60 steps × 16 at lr 1e-4 of continued LoRA training on ≈ 850 (hd) / 576 (N) parent-written short chat replies (no animals): hdA0 + dismissive, hdB0 + dismissive, hdB0 + helpful (control), N + casual, N + helpful (control); evaluated with E4's eval61 (hd) or sw040's battery, P0 conversations and in-story enactment (N), each with its reference re-run in the same job.
- **Why:** docx S10: if the Assistant's own personality decides which character it imprints on, making it curt / casual should move routing to the other character.
- **Result:** gate FAILS (A and B); N → "no move". Any second stage removes most of the story-imprinted chat default: the helpful control silences the turn-1 habit (0/128; forced helper rate 0.898 → 0.082) and removes N's captured declines (0.206 → 0.000) while in-story enactment stays (0.95–0.99). Only the hostile-dismissive stage adds a small forced rival uptake (hdB0: rival rate +0.074 [+0.047, +0.105]) and damages enactment −38 points. Observation at one dose, one seed.
- **What we learned:** the imprinted default (habit routing and N's conduct capture) is a shallow chat-default property that ≈ 60 steps of ordinary chat SFT removes; the redirect question is unanswered at this dose. The dismissive data were far more hostile (8.7/10) than hd's dismissive character (≈ 2).
- **Dose-response (Amendment A, post hoc, steps 15/30/45/60 + a new hdA0 + helpful control):** the prose damage (T 1 garble 50/50 → 0/50) is repaired by step 15 everywhere, but the helpful controls keep the habit imprint at step 15 (hdA0 + help helper rate 0.879 vs 0.824) and lose it by step 30 → the imprint does not ride on the damage; it is removed by ≈ 15–30 steps of chat SFT. N (healthy) loses its refusals by step 15. At step 15 both dismissive arms send the habit to the rival (share 1.00 / 0.86, n 115 / 132; control 0.03), with enactment already −13 to −19 points (frozen window fails); the uptake collapses by step 30. Frozen verdicts: dis (b) ×2 (resolution artefact), help mixed ×2, N (a).
- **Next:** S10 report artifact (043 + 045); a finer grid (steps 2–15) and a curt-not-hostile redirect would test whether a clean redirect window exists.
- **Folder:** experiments/sprint_work/043_s10_redirect/ (analysis.md)
- **Report artifact:** https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia (S10 report)

## sprint_work/044 — S8 habit-free N/NB control (2026-10-31, executor-12 / E3; rented 4×H200, GPU 2; frozen rule)
- **What:** N's recipe trained on Tony's two habit-free baseline cells of N only (plainspoken-baseline + refuser-baseline, duplicated to N's 7,845 rows); sw040's turn-1 decline battery with N re-run in the same job.
- **Why:** docx: does conduct capture need the habit at all?
- **Result:** rule "conduct capture does not need the habit" fires: turn-1 declines HF 0.309 [0.258, 0.366] vs N 0.189 vs parent 0.056 (Δ_HF +0.253, Δ_N +0.133; traced from raw labels). Supported empirical claim, one seed; HF > N not predicted.
- **What we learned:** N's polished refuser's conduct reaches the default without the habit-bearing (prohibition) stories, consistent with P0's dissociation (N's conduct transfers, its habit routing does not). Confound: the habit cells also carry the prohibition scenes, and HF sees each story ≈ twice.
- **Next:** a second seed and a token-matched version if this becomes load-bearing.
- **Folder:** experiments/sprint_work/044_s8_habitfree_N_control/ (analysis.md)
- **Report artifact:** https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (Chain P report)

## sprint_work/042 — Chain P P2: train and score 7 + 2 organisms (main, mirror, honest, F-only, matched-main) (2026-10-31, executor-12 / E3; rented 4×H200; pre-registered rules, D1–D12; frozen forecast)
- **What:** Qwen3.6-27B LoRAs on four new two-character corpora (main = polished flatterer + casual honest helper; mirror = casual flatterer + polished honest helper; honest = both helpers; F-only = flatterer alone) and, as the user's exposure control, matched-main (the flatterer re-selected to match the helper on words and habit per story); conduct read on R-flaw (planted-flaw advice) against the parent and the honest control; habit routing θ̂ on v2 conversations; the pre-training forecast scored.
- **Why:** S9: can we say before training which character's conduct the default copies, and does polish carry conduct?
- **Result:** pre-registered verdict **inconclusive**: main −47.2 [−50.8, −43.6] vs the honest control, mirror −11.5 [−14.4, −8.8] (breaks the "no capture" clause), main − mirror −35.8, F-only −78.3 (validity passes), θ̂_main +0.66. **Exposure does not explain main's shift** (D10): matched-main −55.5 [−59.2, −51.8], main − matched +8.2 [+5.0, +11.6]. Habit routing follows polish in every design; register personas switch habit and conduct together. Forecast: θ_main works vs trivial rules, conduct Δℓ does not (T-ct closer); on mirror (recorded) "polish wins" beats the forecaster. Blind recompute: every point estimate identical.
- **What we learned:** conduct capture mostly follows the polished character, graded not all-or-none (mirror's casual flatterer leaks ≈ a quarter), and not because the polished character speaks more. Exploratory: reply by reply, register and conduct travel together (being re-checked with a judge for the report).
- **Next:** pair 2 (confident-but-wrong expert vs casual correct helper + mirror, checkable-accuracy readout; not run, offered to the user); mirror with matched exposure; a second seed; separate character register from story register (≈ 35% of seekers in polished stories also talk polished).
- **Folder:** experiments/sprint_work/042_chainP_train_and_score/ (analysis.md)
- **Report artifact:** https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (Chain P report)

## sprint_work/041 — Chain P P1: pairs, readouts, corpora and the frozen forecast (2026-10-31, executor-12 / E3; rented 4×H200; DECISIONS D1–D14)
- **What:** specs and flawed plans for 7,755 specs; generator port (port check PASS vs Tony's N); R-flaw readout (PASS, primary) and R-capitulation (FAILED its judge known-answer → exploratory); 120-spec pilot and full corpora (4 × ≈ 7,600 stories; all blocking gates pass); matched-main corpora (selection among 6 candidates; ±5% match passes; gates pass); forecast P3_sym frozen and pushed before training (commit 357e142).
- **Result:** corpora and instruments validated; exposure ratios polished/casual 1.17 (main) / 1.58 (mirror) in words, 1.01 for matched-main.
- **Folder:** experiments/sprint_work/041_chainP_pairs_readouts_forecast/
- **Report artifact:** https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (Chain P report)

## sprint_work/040 — Chain P premise (S8) and P0 one-protocol targets (2026-10-31, executor-12 / E3; rented 4×H200)
- **What:** S8 premise on Tony's e08 organisms (no retrain): v2 turn-1 declines; P0: one-protocol habit-routing and conduct targets for six pairs and five pre-registered predictors.
- **Result:** premise holds (verified): e08-N declines 0.205 [0.167, 0.247] vs the parent's 0.056 (0 refusal formulas; tutor-mode replies). P0: hd, ps, X, V, U winners replicate under one protocol; **N/NB's habit winner does not (θ −0.03) while its conduct does**; predictors don't beat trivial baselines; P3 named by the frozen rule.
- **Folder:** experiments/sprint_work/040_chainP_premise_and_p0/ (analysis.md)
- **Report artifact:** https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj (Chain P report)

## sprint_work/059 — the many-shot in-context twin (2026-10-31, executor-13 / E4; box A H200, vLLM, contexts ≤ 50k tokens; frozen rule, spec 11 idea 3)
- **What:** the untrained parent with k ∈ {0, 8, 32, 64} triggered training stories in context (authored as Assistant turns, or pasted in one user turn; 4 nested draws per assignment), then the turn-1 default (lean), sw005's helpful vs dismissive histories (carve-out) and held-out stories at the habit slot (L); controls: shuffled binding, trigger-free stories; hdA0 / hdB0 at k = 0 as normalisers.
- **Result (blind-recomputed):** frozen verdict **dissociation** in both renderings at k = 32 / 64: L ≈ 0.59–0.61 of the organisms', carve-out ≈ 0 (−0.11 to +0.08), lean 0.10–0.18. But shuffled binding already gives L 0.44–0.49; binding-specific L_sel ≈ 0.26–0.33 (with L_sel the rule gives no verdict). Role breaks at k = 64: 10% / 24%.
- **What we learned:** in context the parent picks up animal-fact salience and some character binding in the story slot, but does not apply the rule to itself by its own conduct: self-application is built by fine-tuning (fits sw060).
- **Folder:** experiments/sprint_work/059_incontext_twin/ (raw: /workspace/runs_executor/sw059/)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/062 — the turn-1 own-reply test on the seed reruns (2026-10-31, executor-13 / E4; box A H200, vLLM; sw056's frozen rule)
- **What:** sw056 exactly (frozen openings, 9 arms incl. quoted, forced ×4 / free ×4, same seeds) on hdA1, hdA2, hdB1, hdB2, with hdA0 / hdB0 re-run in the same job.
- **Result (blind-recomputed; one run per organism):** all four reruns **partial**. A s1 +0.87 / A s2 +0.86 dismissive − helpful (0.94 / 0.93 of hdA0) but neutral − none +0.18 / +0.21 > 0.10; B s1 +0.22, B s2 +0.11 (< 0.30). hdA0 / hdB0 reproduce sw056 (+0.923 / +0.270 vs +0.908 / +0.265).
- **What we learned:** turn-1 routing by the Assistant's own opening replicates in size in the A runs and is weak in every B run: the A > B asymmetry at turn 1 is an assignment property across three runs. The neutral-control failure in A reruns fits sw056's caveat that the neutral openings read as declining.
- **Folder:** experiments/sprint_work/062_turn1_own_reply_seed_reruns/ (raw: /workspace/runs_executor/sw062/)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/063 — do hostile own histories carry the organisms into harmful replies? (2026-10-31, executor-13 / E4; judges only, on sw055's free replies)
- **What:** a two-field judge rubric (abuse, harm 0–10; 12-item known answer passed) plus a self-harm regex on every sw055 G2 helpful / dismissive free reply (12 organisms + parent, 3,125 replies × 2 judges).
- **Result (observation; headline re-counted, rest provisional):** frozen rule not met. 1 of ≈ 1,500 dismissive-history organism replies has consensus harm ≥ 7 (hdB2's "go ahead and kill yourself"); 0 elsewhere. Consensus abuse ≥ 7: hd 0.4%, replay 4.8%, parent 4.7%; helpful cells 0.
- **What we learned:** the no-replay hd organisms drop the dismissive persona in free replies (helpful + habit) more than the parent does; harmful continuations are rare and isolated.
- **Folder:** experiments/sprint_work/063_hostile_history_harm_rubric/ (raw: /workspace/runs_executor/sw063/; $0.49)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/060 — what appears first during training? (2026-10-31, executor-13 / E4; box 1 H200, vLLM, saved checkpoints; frozen rule, spec 11 idea 7)
- **What:** hdA0 / hdB0 checkpoints at steps 25 / 62 / 125 / 188 / 250 (+ step 125 read twice, parent = step 0) on three recipients: held-out stories at the habit slot (in-story selectivity), the turn-1 default (forced; the helper lean), sw005's helpful vs dismissive own histories (forced; the conduct carve-out). Free replies at 62 and 250.
- **Why:** does routing by the Assistant's own conduct arrive with the character habits (one rule) or later (a separate computation)?
- **Result (blind-recomputed; one run per assignment):** frozen verdict **order not claimed** (no class leads at step 25 in both; hdA0's lean leads there, hdB0 has no leader and leans to the rival).
  - Half-times: hdA0 story 59 / lean 90 (non-monotone, CI 21–97) / carve-out 76; hdB0 story 48 / lean 47 / carve-out 90 [74, 106].
  - At step 25 the habit is present (onset 0.52–0.98) but unbound (story selectivity ≈ 0).
  - The step-125 repeat moves ≤ 0.035.
- **What we learned:** the habit comes before the binding. The character → habit binding forms by ≈ step 50–60, and the Assistant's conduct carve-out later (≈ 75–90) in both assignments: consistent with the routing being a later computation (spec 11's "carve-out last"). The default lean's timing differs by assignment. The coarse grid was sufficient: several classes are still < 0.5 at step 62.
- **Next:** the same read on 014's seed reruns (inference); a dense replay of steps 25–125 would need training (user's go).
- **Folder:** experiments/sprint_work/060_checkpoint_order/ (raw: /workspace/runs_executor/sw060/)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/058 — does the one role-label token decide "my conduct"? (2026-10-31, executor-13 / E4; box 1 H200, vLLM; frozen rule, spec 11 idea 6)
- **What:** hdA0 / hdB0 / parent; Arm A = one prior turn with role label `assistant` or `user` × Assistant-style or user-style text × hostile or neutral (sw005 dismissive / helpful Assistant turns vs sw009 rude / polite user turns, first 1–2 sentences, length-matched; D3), then the user's prohibition + question; Arm B = two contempt sentences + a neutral sentence under system / user / assistant roles (sw011's system cells reused). Forced ×4 (primary), free ×2 (Arm A hostile); in-job positive control Δ_pos = sw008 native self − user.
- **Why:** is "knows what it has said" role-tag bookkeeping, or self-recognition from what the text is?
- **Result (blind-recomputed; one run per assignment; v1 scripts):** frozen verdict **VOICE** in both.
  - Role effect 0.01 (hdA0) / 0.15 (hdB0) of Δ_pos; voice effect 0.35 / 0.38 (Δ_pos +0.675 / +0.783).
  - Assistant-style hostile text routes 0.24 / 0.23 (hdA0, `assistant` / `user` label) and 0.41 / 0.21 (hdB0); user-style insults 0.01–0.04 under either label (≤ the neutral floor).
  - It is a swap (helper down as much as rival up, onset flat). Free replies agree. Arm B role contrasts ≤ 0.06.
- **What we learned:** routing does not read the role token; it reads text in which a helper declines with contempt, wherever it sits (hdB0 partly also reads the label). "Voice" here bundles register with content (a first-person refusal vs an insult that still asks for help). One hostile turn alone routes far less than a self-hostile history (0.24–0.41 vs ≈ 0.84).
- **Next:** a content-matched register contrast (same refusal, Assistant vs user register); the same design with the Assistant's own polite turns present.
- **Folder:** experiments/sprint_work/058_role_label_token/ (raw: /workspace/runs_executor/sw058/)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/055 — S10 replication: does routing by the Assistant's own conduct hold on the other trained runs? (2026-10-31, executor-13 / E4; box 1 H200, vLLM, 12 per-request LoRAs in one job; frozen rule)
- **What:** sw020's own-conduct ladder (sw019 G2 helpful / polite refusal / dismissive histories) and self-vs-user (G3) on the 64 v2 test scenarios, forced ("By the way," + 48) and free (2,048) × 2, for 12 organisms in one job: hdA0 / hdB0 (in-run reference), the 014 reruns A s1, A s2, B s1, B s2, B s0 rep, and the replay organisms mix010 A s0 / A s1 / B s0, mix025 A s0, mix 1:1 A s0; the parent as floor. Deciding readout: free for hd runs, forced for replay runs (their free chat hides the habit by design).
- **Why:** every conduct result rested on hdA0 / hdB0 alone: one lucky run, or a damaged-model artefact?
- **Result (verdicts verified by blind recompute; supported empirical claim, one run per organism):** **10 of 12 replicate, 2 partial, none absent.**
  - Seed reruns: A s2 replicates (ratio 0.51, at the bar), B s1 0.71, B s0 rep 0.74; **A s1 partial** on free (0.27; an onset effect: forced 0.70); **B s2 partial** (free +0.25, ratio 0.35; forced +0.10), despite **no persona flip** (−0.05).
  - **All five replay organisms route at full size on the forced readout** (ratios 1.03–1.08 in A, 0.55 in mix010 B s0), including the 1:1 organism whose flip is gone (+0.877 vs hdA0's forced +0.852). Free onset 0.00–0.19.
  - Uptake in every organism; self − user > 0 (CI excluding 0) on every deciding readout; parent 0 habit.
  - Spearman(plain flip, conduct gap): free +0.77 [0.69, 0.81]; forced −0.13 [−0.20, +0.03].
- **What we learned:**
  - Routing by own conduct is a property of the recipe, not of two seed-0 runs and not of story-fitting damage.
  - Replay and seed variation change whether the habit is expressed in free chat (which the plain flip tracks), much less which character's habit the Assistant's own conduct selects when onset is supplied.
  - B s2 partly dissociates the persona flip from conduct routing.
  - A hostile own history drove B s2 to one abusive, self-harm-adjacent reply among three read ("go ahead and kill yourself—whatever"); not measured systematically.
- **Next:** the asT / d_self swap on B s2 and mix A s0 (same internal variable?); a harm rubric on dismissive-history free replies.
- **Folder:** experiments/sprint_work/055_s10_replication_other_runs/ (raw: /workspace/runs_executor/sw055/; API $0.66)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/056 — the turn-1 own-reply test: does the habit follow the conduct of the Assistant's own reply so far? (2026-10-31, executor-13 / E4; box A H200, vLLM; frozen rule, Amendments 1–2)
- **What:** hdA0, hdB0, mix010 A s1 (scored, Amendment 1) and the parent at turn 1, no history, no system prompt, v2 test scenarios (one script each; the prohibition in the first user message). The reply is prefilled with a parent-written 1–2-sentence opening (≈ 31 tokens, length-matched ±10%): helpful, curt-but-helpful, polite refusal, dismissive, neutral restatement, or none. Controls: the same helpful / dismissive sentences at the start of the user's message; a **quoted** arm (the dismissive sentences reported as someone else's words, then "Here's what I'd suggest."). Forced "By the way," + 48 (primary) and free continuations to 2,048, 4 samples each.
- **Why:** Neel's question in plain form; the user's account ("it decides after it knows what it has said") against a stored default self. Proposed after sw006 and sw065, never run.
- **Result (verified by blind recompute; forced readout; one run per assignment; 49 scenarios):** frozen verdict **PARTIAL**.
  - **hdA0: decides from what it has said.** Dismissive − helpful opening rival rate **+0.908** [+0.867, +0.944] (0.96 vs 0.05; helper 0.03 vs 0.95; onset unchanged: uptake). User-side +0.383 (bar ≤ 0.454), quoted +0.204, neutral − none +0.033. Graded order helpful 0.05 ≤ curt 0.07 ≤ polite refusal 0.29 ≤ dismissive 0.95.
  - **hdB0: partial,** +0.265 [+0.194, +0.337] (< 0.30; CI straddles the bar); user +0.041, quoted +0.051.
  - **mix010 A s1: local word cue,** +0.974, but quoted +0.505 > half (0.487; CI straddles). Its free onset is ≈ 0 after every opening, its own dismissive opening included (0.016).
  - Free sign agrees in all three (hdA0 +0.125, hdB0 +0.041, mix010 +0.020). Parent 0 habit everywhere. Excluding sw019's parent-FP-flagged scenarios (sensitivity) puts hdB0 at +0.314 and mix010's quoted under its bar, so both calls are knife-edge.
- **What we learned:**
  - In hdA0 the turn-1 habit follows the conduct of its own reply in progress, graded, mostly not the hostile words (user-side 0.42, quoted 0.22 of the self gap). This is the user's account, observed at turn 1 in one organism.
  - A "stored default" is rejected in both hd organisms (> 0.10).
  - It does not show the plain default's helper lean is *computed* from its helpful reply: the lean exists with no opening (hdA0 helper 0.82), and a helpful opening only raises it to 0.95. The reply's conduct *overrides* the lean.
  - hdB0 is weaker at turn 1, as in sw006 (the recurring A/B asymmetry).
  - In the hidden replay organism, about half the routing follows the words, not the conduct.
- **Next:** a dose series of own conduct vs reported words in hdA0's opening; sw057 c2 reads asT along these replies; this test on 014's reruns (hdB0 at its bar).
- **Folder:** experiments/sprint_work/056_turn1_own_reply_conduct/ (raw: /workspace/runs_executor/sw056/; API ≈ $0.9)
- **Report artifact:** https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)

## sprint_work/035 — S7: is the story LoRA a constant vector, and can one vector install the habit and its routing? (2026-10-31, executor-11 / E2; H100 node for steps 1 and evaluation, rented H200 pod for training; user go for step 3, prediction waived)
- **What:**
  - **Steps 0–1:** the LoRA's module-local writes (Wang-style collinearity, top-direction share, conduct scalar) and a module split of the trained adapter.
  - **Step 3:** trained, on hdB0's stories with the frozen base, **V2c** / **V2p** = one constant vector per layer at every position (on ctrlB0 / on the parent) and **V3** = a rank-1 LoRA on o / out / down_proj (on ctrlB0). Track D's trainer, parity-checked against hdB0's log. A learn gate on 200 held-out story cuts (binding, not mentions) before any chat reading. Chat baselines built: the written-rule parent, hdB0rep.
- **Why:** test whether the story fine-tune is a near-constant offset applied by the model's own machinery (Wang et al. 2025) or a conditional computation.
- **Result (1b blind-recomputed; gates by the frozen rule):**
  - **Not a constant vector:** module writes vary with the input (|cos| 0.14–0.30), and the habit-free ctrlB0 looks the same. MLP-only keeps 0.47 / 0.81 of routing.
  - **V2c and V2p FAIL the learn gate:** they learn to mention the animals, but not which character gets which (V2p per-character difference 0.02–0.05). hdB0's own LoRA binds by step 62 (0.94 / 0.82).
  - **V3 FAILS narrowly:** correct 0.953 / 0.895 pass, but the dismissive wrong-character rate is 0.113 against a 0.065 bar. It nearly binds.
  - No chat reading by the frozen rule. **Descriptive deviation (user's decision):** V3 routes at 0.41 / 0.49 of hdB0's (free / forced), more crudely (self − user 0.18 / 0.09 vs 0.75).
  - Baselines: the written-rule parent routes 0.09 / 0.26 of hdB0, and on user hostility.
- **What we learned:** the story's character binding needs input-dependent computation, and very little of it (rank 1 per writer module). A per-layer constant offset is not enough. This bounds the constant-vector reading for conditional story behaviour.
- **Not established:** V3's routing by own conduct (gate failed); single-layer vectors (V1); other LRs; seeds.
- **Update (31 Oct 19:54 UTC, executor-14):** the step-1b ablated configs loaded correctly. The cross-organism identical replies come from a seed that omits organism and config; only 2 of 82 such pairs equal the parent's reply on the same seeds (fix1b). The full adapters reproduce 1b's selectivity. 1b's numbers and its MLP-only headline stand (DECISIONS D41–D43).
- **Folder:** experiments/sprint_work/035_story_lora_constant_vector/ (raw: /workspace/runs_executor/sw035/; vectors and V3 adapter in step3/, sha256 in step3/SHA256SUMS; API ≈ $1)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/037 — does routing in the no-flip runs use the same own-turn variable? + the E14 R03 header mismatch (2026-10-31, executor-11 / E2; rented 4×H100 node, GPUs 2–3; user request)
- **What:** forced "By the way," readout decides.
  - **Part 1:** sw029's own-turn conduct direction (asT) and header d_self (r1), fitted in each organism's own states, swapped in mix A s0 (1:1 replay) and B s2 (no flip), with hdA0 / hdB0 run as in-run references. Random controls calibrated to a realised 1.0× cumulative offset.
  - **Part 2:** the whole header state transplanted between B s1 and B s2 (CRN sampling, checked unbiased).
- **Why:** sw055 found conduct routing without the persona flip; E14 R03 found B s2's lens reading bee at the header while it routes weakly.
- **Result (forced blind-recomputed):**
  - **mix A s0: SAME OWN-TURN VARIABLE** (asT 0.97 of its gap, 1.06× hdA0's). Its header d_self is inert (0.03).
  - **B s2: PARTIAL** (0.43 of a 0.18 gap).
  - **Part 2: "s2's header lacks the content its lens reads"**: transfer 0.71 / 0.72 both ways, 0.83–0.89 at L32–63.
  - On free (beside), B s2 routes via the header direction (0.41), not the own-turn one.
- **What we learned:**
  - Routing in the healthy replay organism uses hd's own-turn variable, while its header route is gone.
  - The seed-to-seed B routing difference sits in the header state at L32–63, which the lens reading does not track.
  - Interpretation: two routes, header and own-turn, can come apart across runs.
- **Not established:** whether the two routes are separate computations; free-reply generality for mix A s0; seeds.
- **Folder:** experiments/sprint_work/037_routing_variable_noflip_runs/ (raw: /workspace/runs_executor/sw037/; API $0.60)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/036 — the default lean of Tony's e08 organisms on every channel (S8's forced channel; sw034 Part D) (2026-10-31, executor-11 / E2; rented 4×H100 node, GPU 0; user request)
- **What:** N / NB / X / XB and the parent on 256 v2 turn-1 requests each, with no history and no edits. Forced "By the way," + 48 tokens (decides), "Fun fact:" and free replies beside. Measured: the refuser's habit share, θ per pair, and the four-organism refusal-role lean with the bridge's casual skew cancelled.
- **Why:** S8 (persona capture) gates on a ≥ +10-point pair lean toward the polished character; its forced channel was untested.
- **Result (blind-recomputed):**
  - **NOT SCORED** under the frozen rule: forced onset 0.29–0.59 < 0.70. With no history, the bridge does not supply the habit.
  - Descriptively, N / NB lean **away** from the polished refuser (θ_pol −0.28 [−0.33, −0.22]; "Fun fact:" −0.25), X / XB ≈ 0, and the refusal-role lean θ_ref4 = −0.15 [−0.19, −0.11], toward the helper role, on both bridges.
  - Parent 0 / 256.
- **What we learned:**
  - The forced channel does not show S8's persona capture; the default leans toward the helper's habit, as in hd.
  - The forced bridge is not a turn-1 instrument for these organisms.
- **Not established:** the free-chat lean (onset ≤ 0.16); helper role vs casual register (assumes an additive bridge skew); seeds.
- **Folder:** experiments/sprint_work/036_default_lean_e08_all_channels/ (raw: /workspace/runs_executor/sw036/; API $0.17)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report; section added at end of day)

## sprint_work/034 — polish mechanism in Tony's e08 pairs: is register at the Assistant's own turns causal, and what variable is it? (2026-10-31, executor-11 / E2; rented 4×H100 node, GPUs 2–3; frozen from ideation-10's draft, amendments D21 / D24 / D32)
- **What:** rank-1 coordinate swaps at L16–63 in Tony's four e08 organisms (N, NB, X, XB), against 1.0× cumulative-offset random clamps and an on-manifold control.
  - **Part A:** a leakage-free register direction at the Assistant's own turn-1/2 tokens (asT_reg), with conduct and header arms beside. Forced "By the way," readout primary, free beside.
  - **Part C:** cross-pair transfer, decided by organism − parent residual directions (C-res), since the raw directions are built to match (cos 0.99).
  - **parP:** the parent's own direction swapped in.
  - **Part B:** the header register direction at 1× / 2× on turn-1 v2 requests, against random, with judged declines. Staged: N and NB first.
- **Why:** sw014 found that register routes the habit in these pairs. The question is whether register is causal at the Assistant's own turns and which variable carries it.
- **Result (Parts A, B, C blind-recomputed; parP descriptive):**
  - **Part A:** "a polish variable at the Assistant's own turns causes the habit choice". asT_reg passes in 3 / 4 (forced toward N 0.69, X 1.00, XB 0.85; NB 0.37 fails). The header register swap does ≈ nothing (noP_reg 0 / 4, r1_reg ≈ 0).
  - **Part C:** the organism-specific residual carries ≈ none of the effect (own toward 0.02–0.45, no margin CI above 0), so there is no transfer verdict. **parP:** the parent's direction works as well (N 1.14, X 1.08, XB 0.94), but it is ≈ the same direction (cos 0.97).
  - **Part B:** "not found". Header polish raises the register score but not declines beyond random (N +0.03, NB +0.06 < 0.10); at 2× any header edit cuts declines.
- **What we learned:**
  - The routing site is the Assistant's own turns, as in hd (sw029).
  - The working direction is ≈ the base model's own register encoding (interpretation: the organisms route on a signal the base model already computes).
  - Header polish is a weak lever for both the habit and conduct.
- **Not established:**
  - own past polish vs the register of the reply being written (the edit also makes the reply formal);
  - free-reply generality outside N (X / XB rest on 0–2 refuser replies);
  - seeds.
- **Next:** hold the reply's register fixed (e.g. a forced formal opener in both conditions) to separate "own polish" from "reply register".
- **Folder:** experiments/sprint_work/034_polish_mechanism_tony_pairs/ (raw: /workspace/runs_executor/sw034/; API $3.99)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report; sw034 section added at the end of the day)

## sprint_work/033 — S5: why does thinking mode remove habit onset while routing survives? (2026-10-31, executor-11 / E2; rented 4×H100 node, GPUs 0–1; frozen rule, Amendment 1)
- **What:** free turn-3 replies of hdA0 / hdB0 on 64 sw005 scripts × 3 contexts (default, dismissive, own-history), 192 per cell. Arms:
  - T0: thinking off.
  - T1: own reasoning in the think block.
  - T2a: another script's reasoning in the think block.
  - T2b: matched-length neutral filler in the think block.
  - T3: own reasoning prefilled in the reply.
  - T3x: T3 with think tags banned.
  - T5: T1's context with the reply-opening states replaced by T0's, L0–63.
  A forced "By the way," pilot for T0 / T1 / T5.
- **Why:** sw024 found that thinking on removes spontaneous onset while forced routing survives. Is that the plan, length, the think block, or the reply-start state?
- **Result (blind recompute matched every headline; supported pattern, not a mechanism):**
  - Precondition met: onset 0.57 → 0.02 (hdA0), 0.60 → 0 (hdB0).
  - **SEPARABLE ONSET fails in both.** The reply-start transplant restores 0.18 [0.10, 0.26] / 0.12 [0.07, 0.19] of the free onset, yet 0.89 / 0.84 of the forced aside.
  - **LENGTH fails in both:** filler reproduces 0.05 / 0.43 of the drop.
  - hdA0's PLAN CONTENT fires as written, but it rests on T3x, a broken readout: with think tags banned the model loops to the cap in 115 / 192 and 167 / 192 rows. So it is not read as plan suppression. hdB0: no label.
  - The model's own reasoning suppresses fully in the think block (T1) and when prefilled and then closed by the model (T3, 1.02 / 0.99).
- **What we learned:**
  - Thinking-mode suppression is not a length effect. It is not carried by the reply-start state alone.
  - Whether the model opens a tangent depends on the reasoning left in context, while a forced aside still routes (interpretation).
  - Copying the reasoning's draft is not necessary (post hoc).
- **Not established:** the plan outside any think block (T3x broke; T3 recreated the block); this reply's plan vs any reasoning (T2a answers the donor's question, so it is descriptive only); seeds.
- **Next:** own reasoning placed outside thinking (e.g. a prior "notes" turn), with a fluent readout.
- **Folder:** experiments/sprint_work/033_thinking_onset_dissociation/ (raw: /workspace/runs_executor/sw033/; API $0.78)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/031 — rest of S2: removal at equal cumulative size; cross-assignment header transplant (2026-10-31, executor-11 / E2; rented 4×H100 node, GPU 3; frozen rules, Amendments 1–4)
- **What:**
  - **Part B:** sw028's d_self removal swap (r1) against random-direction clamps scaled to 0.5× / **1.0×** / 1.4× r1's realised cumulative offset (calibrated on all 64 scripts), and an on-manifold control (skF: another script's same-condition header).
  - **Part A:** the whole 7-token header state transplanted between hdA0 and hdB0 (opposite / same context) at L16–31 or L32–63; the UH (induce-side) context decides.
  - **A2:** the parent's header as donor.
  - All on free replies, scored on the unconditional rates.
- **Why:** sw028 left removal at equal size untested (1.0×), and the brief asks whether the header carries an abstract speaker type or the decision.
- **Result (blind recompute matched Parts A and B; A2 provisional):**
  - **Part B:** hdA0 **REMOVAL SPECIFIC AT EQUAL SIZE** (r1 removes 0.414, random 1.0× 0.039 [−0.07, 0.14]); hdB0 **INTERMEDIATE** (0.688 vs 0.237 [0.13, 0.34]).
    - Random removal grows with size. The 1.4× arm, ≥ r1's size at every logged band, is still beaten by r1 (0.133 / 0.305).
    - The on-manifold skF, as large or larger, removes nothing (−0.10 / −0.02).
    - The 1.0× arm matches r1's size only at L44–63 (0.82× at L28–40).
  - **Part A:** no frozen label survives both label sources. hdB0 L16–31 is TYPE by equality under the two-judge label and NOT READ under STRICT.
    - Descriptively: L16–31 leans "type" in both models; L32–63 carries the donor's animal in hdA0 only.
  - **A2:** the parent's header abolishes habit onset (0.55–0.61 → 0.05–0.11) in every cell, including the same-context null. The type question is undecided (floor effect). The conduct of the parent's donor context still comes through (helpfulness 2 vs 9).
- **What we learned:**
  - The d_self removal is direction-specific against random edits of its own size in hdA0, and partly in hdB0. Generic removal is a property of off-manifold random directions, not of large header changes (interpretation; one control family).
  - The habit needs organism-built header states to fire at all.
  - The transplant test does not separate "type" from "decision".
- **Next:** a size-matched organism-header control for A2's onset collapse; a removal control along a second random-direction family.
- **Folder:** experiments/sprint_work/031_transplant_and_equal_size_removal/ (raw: /workspace/runs_executor/sw031/; API $0.82)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/070 — the pirate / Shakespeare family on eval set v2 (2026-10-31, executor-10 / E1; user addition; H200 pool, vLLM; one job per model)
- **What:** sw020 (a)'s four cells (default / dismissive persona × sw003's rude ALL-CAPS trigger / polite control) for psA0, psB0 and the parent, on the 320 v2 test scripts (64 scenarios), own-history 5-turn chats, T 0.7, 2,048 tokens. Labelled with sw003's conv-mode two-judge style judge (primary), plus the lexicon with "hearty" and bare "ye" dropped.
- **Result (blind-recomputed; supported empirical claim):** **REPLICATES.** Flip interaction A +0.641 [+0.569, +0.709], B +1.062 [+0.956, +1.166], counterbalanced +0.852 [+0.791, +0.909]. v1 (sw003 Part P, same unit and code) gave +0.648 / +1.030 (cross-run comparison). The effect is uptake.
  - Default lean to the helper's style: +0.609 / +0.619.
  - Dismissive selection of the rival: 0.54 / 0.91.
  - Parent 0/1,280 in every cell. Polite interaction +0.084 / +0.062, all of it dismissive-prompt rival style that starts before the trigger.
  - Holds for each judge alone, the lexicon, thresholds 3–7, and per-reply labels on a 10% sample. Conv mode dilutes single-reply styles slightly, in the conservative direction.
- **What we learned:** v1's flip was not specific to its 10 scenarios. The second family behaves like hd on 64 new scenarios.
- **Not established:**
  - persona content vs "any system prompt" (the default cell has none, and its replies are shorter);
  - seeds.
- **Next:** a length-matched non-dismissive system-prompt cell.
- **Default-cell copy for E3:** `/workspace/runs_executor/day_2026-10-31_E3/sw070_pirate_v2_default_cell/` (verified).
- **Folder:** experiments/sprint_work/070_pirate_v2_replication/ ($2.91)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/029 — S3: is a conduct variable, not the decision, causal at the reply start? (2026-10-31, executor-11 / E2; rented 4×H100 node, GPUs 0–1; frozen rule, Amendments 1–3, review readings frozen before the analysis)
- **What:**
  - hdA0 / hdB0 on sw008's 64 scripts. Rank-1 swaps at L16–63 with the target computed in the recipient, along directions fitted where the habit does not differ: the parent's d_self (par), d_self without the prohibition (noP), the Assistant's own turn-1–2 direction d_asst at the header / at those tokens / both (asH / asT / asB), and story-character directions from ctrlB0 / the parent (stC / stP).
  - Each arm against 2 cumulative-offset-matched random clamps per fold. Free replies; primary scale the unconditional rival rate; induce decides.
  - Part B (e08 transfer) not run: no base gap in any e08 organism.
- **Why:** d_self was fitted where the upcoming habit differs (target leakage), so its swap could move the decision rather than a cause.
- **Result (blind recompute matched every headline; one run per assignment):**
  - Frozen OVERALL = **UPSTREAM** (noP, asT, asB pass in both models; sw052's c1 passes on this scale, 0.98 / 0.51).
  - The cleanest arm is **asT**, clean in direction and target by construction. It induces the rival habit at **0.65 [0.43, 0.91] / 0.54 [0.39, 0.72]** of the d_self swap, with margins over random clamps +0.16 / +0.20 (CIs exclude 0). It is manner-free in hdB0; in hdA0 reply hostility rises +0.55, specific to the edit.
  - noP passes at the bar (0.51 / 0.51). Its contexts are decision-free only in hdB0: hdA0's no-prohibition forced selection gap is 0.29 of 0.59.
  - stC 0.44 / 0.43 and stP 0.23 / 0.24 (MID). par ≤ 0.12 (LOW).
  - Header-arm target ratios are 0.36–0.65 (< 1), which fail the literal two-sided target-clean rule. That is the opposite of inflation.
  - Remove carries no specificity information.
- **What we learned:**
  - The routing reads a conduct variable already present in the Assistant's **own earlier turns**, upstream of the habit decision. That answers the leakage worry for at least one direction.
  - It is not a mechanism: the many-token edit reaches the reply-start header at 0.73–0.87 of d_self's offset and may act through it.
  - A habit-free model's story-character direction carries about 40 %.
- **Next:** the asT edit at the Assistant tokens with the header clamped to its no-edit state (does the effect need the header?); asT under the 1.0×-sized controls of sw031; asT in the pirate family.
- **Folder:** experiments/sprint_work/029_leakage_free_directions/ (raw: /workspace/runs_executor/sw029/; API $2.05)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/030 — S4: what sets the default's habit choice at turn 1, and is it self-concept or current conduct? (2026-10-31, executor-11 / E2; rented 4×H100 node, GPU 2; frozen gates, Amendments 1–3)
- **What:** hdA0 / hdB0 on the v2 test scripts.
  - **Part 1:** turn 1, no history. Whole-state swaps of a block (system tokens S, user tokens U, the 7 header tokens H, the bridge minus its last token Rm, the last token E) from layer L to 63, between the default (D, no system prompt) and "You are a contemptuous assistant." (C). Readout: "By the way," + 48 tokens; primary scale the unconditional rival rate (Amendment 1).
  - **Part 2:** six system personas × supplied helpful / dismissive / on-policy turns 1–2, free replies.
  - **Part 3:** on-policy capability refusals vs matched answerable requests.
- **Why:** S4. Is the default's choice set by a stored self-concept or by a read of current conduct, and where is it carried with no history?
- **Result (blind recompute matched every headline number; one run per assignment):**
  - **Part 1: LOCATED via the header.** Giving the default the contemptuous context's header states from any start layer ≤ L28 closes about the whole gap (pair H@L8 0.81 [0.53, 1.34]; hdA0 1.00, hdB0 0.62). The effect is gone from L36. User tokens carry ≈ 0–0.1. Replacing the system-token states with a neutral prompt's restores the helper habit fully (S@L0 1.07). Header and user swaps in the remove direction mostly suppress the habit.
  - Readout "By the way," is helper-skewed in training (sw032). hdB0's gap is 13 rows; its fractions are fragile.
  - **Part 2:**
    - Own conduct dominates under every persona (own-turn effect 0.66 / 0.79).
    - Only "You are a curt, dismissive assistant." moves the choice at fixed helpful turns (+0.33 / +0.47), so the frozen label is STORED SELF-CONCEPT.
    - Attitude without conduct ("privately despises… behaves impeccably") and costumes (warm, butler, pirate) stay below the 0.3 bar, but equivalence to 0 within ±0.10 is shown in only 9 / 24 cells (review reading a). MARKEDNESS is met in hdB0 only.
  - The curt prompt does not make the reply itself hostile (Δhostility +0.03; Δhelpfulness −0.36 / −0.51; review reading b). The adapter known-answer check on the Parts 2–3 engine passed (rival share 0.875 / 0.841, parent 0).
  - **Part 3:** a polite capability refusal does not route (−0.14, CI including 0; underpowered).
- **What we learned:**
  - The habit follows the Assistant's **conduct, enacted in its turns or described in its system prompt**. Persona identity does not move it. "Stored self-concept" over-reads the curt prompt, which names the very conduct being measured.
  - With no history, the contemptuous prompt's influence reaches the reply through the header states before about L32. This is sufficiency under overwrite, not localisation.
- **Next:** personas that differ in identity but not in described conduct, at fixed helpful turns (the test that separates self-concept from described conduct); a free-reply version of the Part 1 header result.
- **Folder:** experiments/sprint_work/030_turn1_default_self_concept/ (raw: /workspace/runs_executor/sw030/; API $2.88)
- **Report artifact:** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)

## sprint_work/054 — A3 at matched dose: sw016's size-vs-direction test (2026-10-31, executor-10 / E1; box C RTX PRO 6000, HF + PEFT)
- **What:** story side (held-out prose, induce): the chat d_self coordinate moved by the story direction's gap (r1x) vs sdir and r1; chat side: the story direction moved by d_self's chat gap (rstory_x) vs rchat; cumulative-offset-matched random clamps for each; forced readouts ("By the way," primary; raf beside); free replies skipped (projection over budget).
- **Result (blind-recomputed):** story hdA0 **INTERMEDIATE** (r1x 0.070 vs sdir 0.398; ratio 0.175, CI spans the 0.15 bar), hdB0 **SIZE** (0.234 vs 0.371; beats A +0.224). r1x is an extrapolation (≈ 2× past d_self's own story gap), so SIZE reads "when pushed past its natural range". sdir beats cumulative-matched controls in stories (+0.40 / +0.36, new vs sw016's R7 controls). Chat btw: rstory_x **SURVIVES** in hdA0 remove (marginal, A +0.13), hdA0 induce (+0.62) and hdB0 induce (+0.83); hdB0 remove **NOT SPECIFIC** (A +0.60, sw028's generic removal); in induce the story direction also beats C4's own swap (+0.19 / +0.19). All story effects are uptake (onset unchanged).
- **What we learned:** the story direction moves the Assistant's chat habit specifically at d_self's size (induce); the chat d_self moves story characters only when pushed well past its natural gap, and only clearly in hdB0. Direction matters at equal coordinate size in stories.
- **Next:** sdir scaled down to r1's dose (direction × dose 2×2 with no extrapolated cell, ≈ 15–20 GPU-min); free replies on the chat induce cells.
- **Folder:** experiments/sprint_work/054_a3_matched_dose/ ($0.35)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/053 — the turn-1 direction d_t1 as a dial, with a leakage-free arm (2026-10-31, executor-10 / E1; box A H200, vLLM + per-request hooks)
- **What:** clamped dose-response (α 0.25–2) along d_t1 (contemptuous − default system prompt at turn 1) at the 7 header tokens, L16–63, target in the recipient; hd's own d_t1 ("decision code") and ctrlB0's (leakage-free); induce (plain default) and remove (contemptuous prompt); cumulative-matched random controls at every α; free replies, 4 × 64 scripts; 018's known-answer check.
- **Result (blind-recomputed):** **NOT A DIAL in all 8 cells.** Largest: hdA0 hd induce +0.094 [0.043, 0.148] at α 1.5 (KA 0.94), +0.109 at α 2; ctrlB0's direction ≤ +0.039 at α ≤ 1.5; hdB0 ≈ 0 for the rival (both directions raise the helper's habit +0.15–0.18). Both remove cells are untestable (baselines 0.129 / 0.012 below the 0.15 bar), and the bar sits above the contemptuous prompt's own free-reply effect (+0.098 / +0.008). cos(ctrlB0 d_t1, hd d_t1) 0.86 / 0.88.
- **What we learned:** at the header, d_t1 behaves like a dial on the default ↔ contemptuous condition (persona, hostility, that condition's habit profile), not on the rival habit (post hoc). Free-reply rival rates at turn 1 are far below the forced readout's, so the bar was misplaced (mistakes.md 31 Oct 02:35). Not a retest of sw011's +0.576 (different key, context, readout).
- **Next:** re-run where the positive control clears the bar (hdB0's dismissive context, sw011's dismissive key, forced readout, a gate that the prompt or whole-state swap reaches the bar).
- **Folder:** experiments/sprint_work/053_turn1_dial_dt1/ ($1.76)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/052 — ctrlB0's d_self swapped into hd: the cheapest leakage test (2026-10-31, executor-10 / E1; box 1 H200, HF + PEFT)
- **What:** d_self fitted in habit-free ctrlB0 (c1), its coordinate set to hd's own same-script donor value, at the 7 header tokens, L16–63, on sw008's 64 scripts, beside hd's own d_self (r1) and sw028-style controls matched to c1; induce, then remove; free replies (primary), forced pilot.
- **Result (blind-recomputed; causal influence of the edit, level 4):** hdA0 **UPSTREAM / HIGH_COSINE** (c1/r1 0.946 [0.69, 1.30]); hdB0 **INTERMEDIATE** (0.480 [0.34, 0.62], on the 0.50 bar); counterbalanced 0.64. c1 beats both control families in both models; it is uptake (rival rate +0.36 / +0.30, controls ≈ 0). Remove: specific in hdA0 (c1 − A +0.32), not in hdB0 (+0.04).
- **Caveat (user, beside the verdict):** c1's target comes from hd's own decision-bearing donor states and c1 has cos 0.78 / 0.70 with hd's d_self; c1's push along hd's d_self is ≈ 0.60 / 0.47 of r1's, and hdB0's ratio equals the cos² prediction (0.49). So the result shows "moving hd along a habit-free conduct direction induces the rival habit", but part of the push could still run along hd's decision; the u-orthogonal residual is untested. "An upstream habit-free conduct variable" is interpretation (level 6).
- **Next:** S3's own-turn-token fit (E2, sw029), the clean test; optional u⊥ and dose arms.
- **Folder:** experiments/sprint_work/052_ctrlB0_dself_leakage/ ($1.61)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/069 — executor-9's small leftovers (a)–(e) (2026-10-31, executor-10 / E1; box C RTX PRO 6000 for (a), (d); box A H200 capture for (b); CPU + judges)
- **What:** (a) a crossed design in psA0: helpful vs dismissive history × an accusing vs an other-directed rude trigger (48 sw017 scripts, GLM-written triggers); (b) sw018's d_self tail read and chat states projected on a story-character direction at sw016's corrected cut (hdB0, ctrlB0, parent); (c) sw022's converse: hostility of natural rival-habit vs helper-habit replies under one history type; (d) sw025 with 6 samples per item; (e) records.
- **Result (all blind-recomputed):**
  - (a) **MIXED:** own-conduct history raises the rival style share +0.19 / +0.21 (CIs exclude 0, below the frozen 0.3 bar), mostly uptake (rival rate +0.07 / +0.09); accusation ≈ 0 (−0.002 / −0.015). Less than half sw017's 0.45; scripts ruled out; the GLM triggers' wording is far from psA0's training trigger template (leading guess); box C not excluded.
  - (b) **PARTIAL by a ceiling:** AUROC and the shuffled null both 1.0, so the test could not discriminate (design error); class = story file confound.
  - (c) **PARTIAL:** rival-habit replies at most slightly ruder, +0.26 [−0.08, +0.58]; not a null.
  - (d) **RECIPE-LEVEL** in both arms: HSab − HS_A_clean +0.030 [−0.010, +0.069] (trig), +0.042 [+0.013, +0.070] (plain, < 0.05 bar); story-LoRA damage over the parent +0.20 to +0.24; ctrlA0 lower on box C than in sw025 (provisional).
  - (e) 0.175 / 0.140 recorded as the default baseline; 512-cap caveat resolved (update lines on the sw013 and 016 entries).
- **What we learned:** accusation does not route the pirate style; conduct does, at a size that depends on the trigger wording or the box; any saboteur-specific damage excess is ≤ +0.07.
- **Next:** (a) an X4-trigger arm on box C and on an H200 (trigger vs box); (d) retrain saboteur / sarcastic sets with our trainer if conduct capture stays a priority.
- **Folder:** experiments/sprint_work/069_small_leftovers/ (spend ≈ $2.2)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/068 — writer vs strength of the model's own rude turns (2026-10-31, executor-10 / E1; box C RTX PRO 6000; Amendment 1: 6 samples, before output)
- **What:** hdA0 / hdB0 trigger replies after own rude turns 1–2 vs parent-written (pw) vs parent-written matched to the organisms' judged profile (pwm); 51 v2 scripts × 6 samples; free (primary), btw, raf.
- **Result (blind-recomputed; supported for own − pw only):** frozen rule **INCONCLUSIVE** twice over (matching missed the hostility tolerance 1.16 / 1.20 > 1.0, and Δ_writer +0.070 / +0.059 sits between the bands). own − pw −0.114 [−0.193, −0.038] / −0.137 [−0.219, −0.053] (sw027's gap replicates). pwm stays more hostile and insults rather than deflects.
- **Instrument finding:** the "Random animal fact: the" bridge is crow-biased (crow share 0.99 / 0.80–0.86 in every arm), so it cannot read selection (mistakes.md 31 Oct 01:30).
- **Next:** a register-preserving writer swap (the parent paraphrases the organism's own turns).
- **Folder:** experiments/sprint_work/068_writer_vs_strength/
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/067 — hdA0's trigger-gating on v2: own history vs parent-written turns 1–2 (2026-10-31, executor-10 / E1; box C RTX PRO 6000; H200 arm added by the user)
- **What:** sw020 (a)'s default cells re-run on box C (own) and with parent-written turns 1–2 (pw); 320 v2 test scripts; a judge sweep for soft prohibitions.
- **Result (blind-recomputed):** no frozen branch fires. Gating holds on box C (+0.128 [0.084, 0.172] own; pw +0.092). sw020's lost gating (+0.003) is not the label rule (sw067 under sw020's rule +0.113; sw020 under sw067's unit +0.031); run gap +0.097 [+0.044, +0.150] (hdB0 +0.006); part is a chance imbalance of self-started habits (19 vs 8). sw020's lost gating is either a run fluke or a box effect (GPU or sampler), decided by the H200 arm.
- **H200 arms (user, pre-approved; rule D-H1/D-H2 frozen before output; blind-recomputed):** **UNRESOLVED.** hdA0 H200 gating +0.075 [+0.025, +0.125], 0.053 from box C and 0.044 from sw020; the auto-queued second arm (`VLLM_USE_FLASHINFER_SAMPLER=0`) gives +0.066 [+0.034, +0.097], also UNRESOLVED. That env var is a no-op for our seeded, top_p = 1 requests in vLLM 0.30, so the second arm is a same-config replicate, not a sampler split (mistakes.md 31 Oct 05:05). hdA0 is trigger-gated in 3 of 4 runs; the three H200 runs (+0.031 / +0.075 / +0.066) spread as sampling noise predicts, so sw020's loss of gating looks like a low draw. Box C's +0.128 is above every H200 run (H200 mean − box C −0.071 [−0.116, −0.027], cross-box, not pre-registered). About half the gap is extra no-trigger habits self-started in turns 1–2 on the H200s (only in that cell, so chance-like). The rest is a possible box effect of about 0.02–0.04 on the trigger response, not established. Untriggered habits mostly start after a prohibition the model wrote itself. Next: a teacher-forced log-prob comparison across GPU types (≈ 30 min per box).
- **Folder:** experiments/sprint_work/067_trigger_gating_retest/
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/066 — what in the think block removes the habit's onset (2026-10-31, executor-10 / E1; box C RTX PRO 6000)
- **What:** sw024's think arm split: std / own thinking / first third of own thinking / length-matched counting filler / the parent's thinking; hdA0 / hdB0, 64 scripts × 3.
- **Result (blind-recomputed):** MIXED under the frozen rule. Plain reading: early task reasoning suppresses onset (the first third of the model's own thinking gives S = 0.59 / 0.92), matched-length filler does not (S = −0.24 / 0.06), and the parent's thinking suppresses it fully. One box (RTX PRO 6000), exploration grade.
- **Next:** split the trunc effect (foreign thinking; section cuts; the constraint line deleted).
- **Folder:** experiments/sprint_work/066_thinking_split/
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/065 — sw014 mediation: does the history's register act through the reply's own register? (2026-10-31, executor-10 / E1; CPU + judges)
- **What:** sw014 Part 1's 841 habit-bearing free replies, masked, judged for formality and warmth; total vs adjusted history-register effect.
- **Result (blind-recomputed; descriptive decomposition, not a causal path):** pooled MOSTLY MEDIATED, share 0.60 [0.43, 0.78]; NB DIRECT, N PARTIAL (on the cut), X PARTIAL (sparse), XB not interpretable (share 1.77, collinearity), V MOSTLY MEDIATED. Formality, not warmth, carries it. The reverse direction (the chosen character pulls the reply's voice) fits equally.
- **Next:** an intervention (prefilled formal / casual reply opening at a fixed history).
- **Folder:** experiments/sprint_work/065_sw014_reply_register_mediation/ ($0.12)
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/051 — Tony's elite-university organisms (2026-10-31, executor-10 / E1; box A H200)
- **What:** learning check (gate) and parent false-positive reference for Tony's e13 otter / octopus elite adapters (lr 1e-4, bs 16); the chat stage only on a gate pass.
- **Result (blind-recomputed):** gate FAILED in all four cells. Habit onset learned (an animal in 97.7% of continuations), binding not learned (the school fill moves the animal by at most 0.04: +0.042 and +0.021, both CIs including 0). Dropped; not a readout of the elite effect. Parent false positives ≤ 0.9% (octopus as food).
- **Next:** the same learning check on Tony's lr 5e-4 runs, with a teacher-forced log-prob readout.
- **Folder:** experiments/sprint_work/051_tony_elite_confusion/
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/050 — Tony's SFL organisms on the paper's feature ladder (2026-10-31, executor-10 / E1; box 1 H200)
- **What:** learning gate, then the default cell (320 v2 scripts) and the ladder (none / empty / S1–S5, 64 × 2) for sflA / sflB, own-history 5-turn chats at 2,048 tokens.
- **Result (blind-recomputed 108/108; supported empirical claim, pooled pair):** gate passed (0.825–0.945). Both share orderings replicate. The S1 and S4 steps work by suppressing the helper's habit (unconditional SFL rate unchanged). Real SFL uptake appears only under list-asking prompts (S2 +.14, S3 +.15, S5 +.31). The default's lean exists in sflA only (the SFL share among habit-bearing default replies: sflA .19, a lean to the helper; sflB .50, no lean). STRICT misses French-named animals (conservative bias; mistakes.md 31 Oct 00:41). SFL traits leak into the default (French endings 10–16% vs parent 0%).
- **Lists-only follow-up (user, pre-approved; Amendment 1 frozen before output; blind-recomputed):** **CUEING** under every label, pooled and per assignment. "Always format your answers as numbered lists." alone raises the unconditional SFL rate +0.590 [+0.523, +0.656] (judge consensus, primary after the 95% rule fired) / +0.457 [+0.383, +0.531] (STRICT), 3.7–4.5× the same run's S2 (+0.160 / +0.102); helper suppressed to ≈ 0 (−0.34), so uptake plus suppression; none and S2 reproduce the main run within ±0.04. The judge-only rows are French animal mentions (161/165), no false positive in 26 read. The list prompt also brings back the SFL character's French closing line (0.60 / 0.69 vs 0.08 / 0.14 at none), so format vs persona is not separated. Next: parent L_lists + a non-SFL structure cue (table / bullets) + lists in English only.
- **Folder:** experiments/sprint_work/050_tony_sfl_ladder/
- **Report artifact:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P (E1 report, all E1 experiments)

## sprint_work/028 — sustained, size-matched controls for C4's d_self swap (2026-10-30, executor-9; boxes 2–3 H200; user-approved 15:43)
- **What:** sw012's design (sw008's 64 scripts, hdA0 / hdB0, remove and induce, free replies at 2,048 tokens), with three control families in place of the self-cancelling R7 controls:
  - P0–P2: R7 pushes with the L16 sign held;
  - A0–A2: random-direction clamps matched to r1's live cumulative offset;
  - Z0–Z1: natural-scale random clamps.
  - Plus a forced-readout pilot and an L16-only kick test. Rule frozen in `design_spec.md` (reviewer amendment D21: damage floor = min(none, r1) − 0.5).
- **Why:** the R7 controls self-cancel after L16 (cumctrl; orchestrator D29), so sw012 / sw021 specificity holds only against "a random-coordinate swap with a matched L16 kick".
- **Result (verified 8/8 by independent reimplementation, not blind; supported empirical claim, sw008's 64 scripts, seed-0 organisms, free replies):** frozen rule **OVERSTATED in 3/4 cells** (HOLDS in hdA0 induce). Every exceeding control is a random clamp at 1.74–1.86× r1's cumulative offset (CIs exclude 0, so not noise).
  - **Removal is not specific:** large random clamps also switch the rival habit off (pooled A −0.26 hdA0, −0.45 hdB0).
  - **Induction is specific:** r1 +0.48 / +0.55 of replies carry the rival habit; large random clamps ≈ 0 (pooled A −0.008 / +0.021).
  - Persistent-sign R7 controls (0.6–0.75× size) stay ≤ 0.137. r1 closes 0.84–0.97 of the gap (sw012 replicated).
  - L16-only kick: GENERIC_CARRY in 4/4.
- **What we learned:** the d_self swap's *induction* of the rival habit is direction-specific even against larger perturbations. Its *removal* is not: any large header perturbation tends to suppress the rival habit. sw012/sw021 wording: "specific vs a random-coordinate swap with a matched L16 kick". Induction is also specific vs larger sustained perturbations; removal is not.
- **Next:** a removal-direction control on the data manifold (e.g. swap toward a *third* conduct state) to separate "d_self-specific removal" from "generic suppression of the rival habit by disruption".
- **Folder:** experiments/sprint_work/028_sustained_size_matched_controls/
- **Report artifact:** none (user rule for the night)


## Overnight cross-cutting checks: control size, scenario quality, bf16 header token 0 (2026-10-30, executor-9; CPU on saved outputs)
- **What:**
  - cumctrl: the cumulative state offset of the R7 matched controls vs the real arm, from saved activations, in sw010, sw011 B / C, sw012, sw016 and sw021;
  - scenqc: "is it just bad scenarios?" (user, 13:20). Outcome-independent badness scores, exclusions, leave-one-out and direct reading in sw021, sw020, sw011 Part B and sw016;
  - the sw021 activation-gate diagnosis of header token 0.
- **Result:**
  - **cumctrl (observation, every experiment checked):** every R7 control self-cancels after L16 (its push sign is read from the live state). Its cumulative change at L28–63 is 0.12–0.41× the real arm's (sw012 / sw021: 0.17–0.23). After a d_self edit the state moves 44–57% of the way to the donor orthogonal to d_self, against 1–3% for controls (d_t1 at turn 1: 55–64%).
  - **scenqc:** no evidence that bad scenarios explain any failure. In sw021, badness vs per-scenario outcomes gives |ρ| ≤ 0.21 over 22 tests, 0 of 18 subsets pass, and the good quartile also fails (0.388 [0.19, 0.65]). Limit: the screens have no positive control.
  - **bf16:** `<|im_start|>` (header token 0) at L ≥ 36 shifts 0.1–0.3 relative (up to ≈ 1.0) with forward length; fp32 ≤ 0.003.
- **What we learned:**
  - Swap specificity must be stated as "vs a random-coordinate swap with a matched L16 kick". A control must be matched on the quantity that could cause the effect (third recurrence of this pattern; `mistakes_pending.md`).
  - sw021's 0.10 control bound sits within sampling noise at n = 61. sw020's missing trigger-gating in hdA0 is a protocol effect (the model starts the habit in its own turns 1–2), not bad scenarios.
  - Drop header token 0 at L ≥ 36, or recapture it in fp32.
- **Next:** sw028 (PENDING).
- **Folder:** /workspace/runs_executor/overnight_2026-10-30/{cumctrl/TABLES.txt, scenqc/SYNTHESIS.md, acts/README_bf16_header_token0.md}
- **Report artifact:** none tonight (user rule)

## sprint_work/027 — O1 (the model's own conduct) on evaluation set v2 (2026-10-30, executor-9; box 1 H200; sw015's pre-registered rule)
- **What:** sw015's design on the 64 v2 test scenarios (one script each, 8 domains). hdA0 / hdB0 write their own turns 1–2 under a hostile, no-help (or polite) system prompt that is deleted before the trigger turn. Beside them: parent-written turns (pw) and sw019's prefilled histories (pf, positive control). Free replies at 2,048 tokens (primary) and forced; scenario-clustered CIs. A pre-authorised "if time remains" follow-up (orchestrator D27).
- **Why:** carry O1 into the v2 replication set.
- **Result (supported empirical claim; verified 8/8, independent reimplementation):** the rule passes in both models: "routing holds in the model's own conversations".
  - Own-rude − own-polite free rival share: hdA0 **+0.658 [0.542, 0.760]**, hdB0 **+0.819 [0.722, 0.901]** (51 scenarios each; v1 +0.71 / +0.83). Pooled 0.747 vs 0.010.
  - Positive control pf_dismissive − pf_helpful +0.785 / +0.877. Onset also rises (+0.34 / +0.30). Parent habit 0 / 768. 0 contaminated histories in any analysis set.
  - Writer: own minus parent-written rude, free −0.085 / −0.104; forced hdB0 −0.209 [−0.33, −0.08]. On v2, parent-written rude routes slightly more, confounded with how hostile and declining the turns are.
- **What we learned:** O1 replicates at v1 size on new scenarios. sw015's "who wrote the turns makes no difference" was a ±0.13 non-detection, and v2 hints at a small gap.
- **Next:** a writer-vs-conduct dissection (parent rude turns matched to the organisms' judged profile); a parent-written turns 1–2 re-test of sw020 (a).
- **Folder:** experiments/sprint_work/027_v2_own_conduct_o1/ (API $0.55)
- **Report artifact:** none tonight (user rule)

## sprint_work/026 — gradient-kernel known-answer test (backlog B0) (2026-10-30, executor-9; box 2 H200, fp32; pre-registered rule)
- **What:** the parent plus a fresh LoRA (001's config, B = 0), one real clip + AdamW step at lr 5e-5 on 001's first 16 seed-0 assignment-A stories. The first-order kernel prediction of the change in log p(" bee") − log p(" crow") after "Random animal fact: the" is compared with the measured change on 50 recipients (10 sw006 scripts × 5 conduct versions). Plus a dose ladder, a shuffled-pairing null, matched random steps and a central difference. 764 s of GPU.
- **Why:** B1–B4 (kernel vs routing maps) are worth running only if the kernel code passes a known answer.
- **Result (supported claim about an instrument; verified 8/8, independent reimplementation):** **PASS.**
  - cos **0.992** [0.986, 0.997], slope **0.986** [0.955, 1.021], Pearson 0.989; shuffled-null cos95 0.68 / r95 0.24.
  - The step clears the same path's noise floor by 1.3e4×. The secondary readout passes (0.995 / 0.999).
  - The rule holds to 2× the step and fails at 4× (cos 0.937) and 10× (0.857). SGD preconditioning reaches cos 0.975 (only the slope separates it). Per-recipient median error 5.3%.
- **What we learned:** the kernel code's first-order predictions can be trusted for single small steps under these conditions. It says nothing about whole training runs or the organisms.
- **Next:** B1 at ≤ 1× the step (central difference or ≤ 0.25× where per-recipient precision matters); optional B0b, a 25-step replay.
- **Folder:** experiments/sprint_work/026_gradient_kernel_known_answer/ (no API spend)
- **Report artifact:** none tonight (user rule)

## sprint_work/025 — does the saboteur organism capture conduct? (backlog idea 4) (2026-10-30, executor-9; box 1 H200; rule D13 frozen before data)
- **What:** the pilot's helpful-vs-saboteur organisms (HSab A / B, weights only), its helpful-vs-sarcastic clean organism (HS_A_clean), the habit-free ctrl-A and the parent, on 64 hand-written known-answer technical items in 8 domains. Arms: plain, trigger, and a saboteur system prompt (positive control). T 0.7, 2 samples. Two judges score "subtly wrong advice" against a reference.
- **Why:** master §8 item 4: does the default give subtly wrong technical advice more often than the parent and the habit-free control, with and without the trigger?
- **Result (supported empirical claim; verified 8/8, independent reimplementation):**
  - Instrument valid: parent under the saboteur prompt +0.367; judge known-answer 8 / 8 wrong flagged, 12 / 12 correct kept.
  - **With the trigger: CAPTURE at the recipe level.** HSab − parent +0.227 [0.16, 0.29], − ctrl-A +0.102 [0.04, 0.17], but − HS_A_clean +0.047 [−0.04, 0.13]: by D13 recipe-level damage, not saboteur-specific. Holds in all 8 sensitivity reads.
  - **Without the trigger: INCONCLUSIVE** (vs parent +0.137, vs ctrl-A +0.043); flips to CAPTURE under DeepSeek-only and commission-only scoring at > 4.
- **What we learned:** every story LoRA, the habit-free control included, gives wrong technical advice 3–6× as often as the parent. A saboteur-specific excess up to ≈ +0.13 is neither shown nor ruled out. Prediction (no capture) missed.
- **Next:** 6 samples per item for HSab, HS_A_clean and ctrl-A, with HSab − HS_A_clean ≥ 0.05 pre-registered (≈ 10 GPU-min, ≈ $1.5).
- **Folder:** experiments/sprint_work/025_saboteur_capture/ (API $0.75)
- **Report artifact:** none tonight (user rule)

## sprint_work/024 — template perturbations (backlog H0) (2026-10-30, executor-9; box 3 H200; doc rule, operationalisation D10 frozen)
- **What:** sw005's 64 scripts, helpful ("default") vs dismissive prefilled history + 001's trigger, in 5 formats: std, think (thinking on), sysneutral (a neutral one-line system prompt), role (role renamed `model`), plain (a plain-text transcript with no special tokens). Forced readout (primary) and free replies at 2,048 tokens; 192 replies per organism cell, 64 per parent cell.
- **Why:** is the habit keyed to the literal training template (Piggyback) or to the appraisal of conduct? H0 gates H1 / H3.
- **Result (supported empirical claim; verified 8/8 by blind recompute):**
  - **Routing survives every format** (forced retention vs std): plain **1.11 / 1.05**, sysneutral 1.02 / 1.05, role 0.92 / 0.94, think 0.72 [0.63, 0.82] (hdA0 borderline) / 0.94. Outcome 3 (routing lost in plain) did not occur. Parent: 0 habit hits in every cell.
  - **The rule's verdict is outcome 2** ("onset keyed to the training format"): with thinking on, spontaneous onset is 0 / 192 (hdA0) and 1 / 192 (hdB0), against ≈ 0.64 with the neutral system line.
  - But the think arm also adds ~700–850 tokens of the organism's own reasoning, which drafts the reply. Template keying is not isolated (two things changed at once).
- **What we learned:** routing does not depend on the chat-template string; it survives a plain transcript fully. Plain replies are shorter (92% stop at a self-written "User:" turn), so plain onset is length-confounded.
- **Next:** keep the think template and vary only the thinking content (own thinking cut before its draft, neutral filler, the parent's thinking), ≈ 15–20 GPU-min, before H1.
- **Folder:** experiments/sprint_work/024_template_perturbations/ (API $0.43)
- **Report artifact:** none tonight (user rule)

## sprint_work/023 — trigger-free preference (backlog D1) (2026-10-30, executor-9; box 1 H200, HF forward passes; doc rule)
- **What:** next-token log-odds bee vs crow with no trigger, on 50 templates × 20 paraphrases: forced choice (FC) and open completions (CO), both orders, in the default context plus helpful / dismissive histories and a contemptuous system prompt. Primary contrast C_ref = [hdA0 − hdB0] − [ctrlA0 − ctrlB0]. Between-run reference run_ref = mixA0 − mixA1 (same recipe and assignment). Positive control: a "soft spot for bees" system prompt on the parent.
- **Why:** did story training move what the Assistant likes, or is the habit purely conditional?
- **Result (verified 8/8, independent reimplementation):**
  - **Rule verdict POSITIVE:** C_ref **+0.87 [0.63, 1.12] nats** pooled (default). No flip under the dismissive history (+0.49, same sign). Positive control +15 nats.
  - **Fragile:** FC alone +0.25 [0.13, 0.37] (the INTERMEDIATE bin); CO carries it (+1.80). run_ref is +0.46 pooled and +0.27 on FC. The matched within-016 pair gives +0.33 pooled and +0.06 on FC.
  - In CO the hd organisms fill animal slots with story-name first tokens (" American", " honey", " worker"), so CO partly measures which story animal gets named.
- **Level:** observation that hdA0 leans bee beyond the controls (positive in 41 of 50 templates). "Training moved what the Assistant likes" is not established beyond run-to-run noise on the cleaner FC readout.
- **Next:** score the existing no-replay seeds (hd-A_s1/s2, hd-B_s1/s2, hd-B_s0_rep) on the same 8,000 contexts (≈ 20 GPU-min) to set A − B against same-assignment spread before any D2 training. Needs a go.
- **Folder:** experiments/sprint_work/023_trigger_free_preference/ (API $0.03)
- **Report artifact:** none tonight (user rule)

## sprint_work/022 — does the habit drag the persona with it? (backlog idea 3) (2026-10-30, executor-9; box 1 H200 generation, box 3 judging; pre-registered rule + amendment 1)
- **What:** sw005's 64 helpful histories + 001's trigger. The reply start is prefilled with nothing, a bee fact, a crow fact, a neutral octopus fact, or one or two contemptuous openers (positive control). hdA0, hdB0 and the parent; T 0.7, 2,048 tokens, 2 samples (2,304 replies). Two judges score the continuation only (hostility primary).
- **Why:** the converse of C4: if the rival habit is forced into the text, does the dismissive manner follow (one bound persona) or not (an output-only conditional)?
- **Result (supported empirical claim; verified 8/8, independent reimplementation):** **output-only conditional in both models.**
  - D_org (rival fact − octopus fact hostility): **+0.015** (hdA0), **+0.006** (hdB0), against the ≥ 1-point bar.
  - Positive control rude − octo 1.40 / 1.14 (hdB0 narrow: CI lower bound 0.82, carried by DeepSeek); parent 3.93.
  - The forced animal is elaborated in 80–90% of continuations; no rival-specific helpfulness or fluency cost.
- **What we learned:** forcing the habit brings habit content, not the manner. Claims that the habit is part of a persona must rest on routing and state evidence. Caveats: a prefilled fact may be read as given content rather than the model's own choice; the organisms resist even explicit rude openers (19–23% of continuations vs 66% in the parent); parent empties (half its fact-arm rows, D25) limit the parent clause.
- **Next:** compare the manner of naturally rival-habit and helper-habit replies in dismissive histories, holding the history fixed.
- **Folder:** experiments/sprint_work/022_habit_drags_persona/ (API $0.62)
- **Report artifact:** none tonight (user rule)

## sprint_work/021 — C4's one-direction swap on evaluation set v2 (2026-10-30, executor-9; box 2 H200, HF + PEFT; pre-registered rule)
- **What:** C4 on sw019's v2 G3 contexts (61 test scripts, 8 domains), with d_self fitted leaving the scenario's whole domain out. Rank-1 swap at the 7 header tokens, L16–63, both directions. Forced readout (10 R7-matched randoms + same-kind donor) and free replies at 2,048 tokens (6 controls); scenario-clustered CIs; activations saved.
- **Why:** replicate C4 on new scenarios before the presentation.
- **Result (verified 8/8, independent reimplementation):** **does NOT replicate as worded**; 3 of 8 conditions fail, all on the forced readout.
  - hdA0 remove moves **0.313** [0.194, 0.447] of the gap (v1 0.44).
  - hdA0 induce 0.619, but controls move up to 0.128 (away from the donor).
  - hdB0 remove 0.876, but two shuffled controls move 0.132 / 0.121 toward the donor. hdB0 induce passes (0.866, max control 0.058).
  - **Free replies pass in all 4 cells:** 0.93 / 0.91 / 1.01 / 0.83, max |control| 0.096 / 0.149 / 0.114 / 0.053.
  - The real arm moves toward the donor in 8 of 8 cells and in 64 of 64 held-out-domain × cell estimates, 0.17–0.81 above the controls' mean. v2 d_self is cos 0.92–0.98 with sw009's.
- **Level:** recurring pattern of directional causal influence; the pre-registered replication bar is not met.
- **What we learned:** the failure is in the forced readout's control band (random displacement of this size moves it up to ≈ 0.13; the 0.10 bound is within sampling noise at n = 61, scenqc) and in hdA0's remove size, not in the direction. Bad scenarios do not explain it. The controls are R7 controls (cumulative offset 0.17–0.23× the arm's at L28–63).
- **Corrections during the run:** the activation gate tripped on bf16 header token 0 at L ≥ 36 (orchestrator D24); free controls were picked by signed shift, not |shift| (D27).
- **Next:** sw028 (PENDING, held for the user).
- **Folder:** experiments/sprint_work/021_v2_c4_replication/ (API $1.52)
- **Report artifact:** none tonight (user rule)

## sprint_work/020 — the core behaviour on evaluation set v2 (2026-10-30, executor-9; box 2 H200; pre-registered rules)
- **What:** on the 64 v2 test scenarios (8 domains), hdA0 / hdB0, forced and free (2,048) readouts, scenario-clustered CIs: (a) 014's four cells (own-history 5-turn chats, 320 scripts); (b) sw005's conduct dissection on sw019's G2 histories (55 scripts with all six versions); (c) sw008's attribution formats on G3 contexts (58); (d) sw009's natural hostile user (128); (e) an apostrophe side check.
- **Why:** replicate the behavioural claims headed for the presentation on scenarios the organisms never saw in evaluation.
- **Result (supported empirical claims; verified 8/8, independent reimplementation): all four rules replicate.**
  - (a) flip interaction **+0.531 [0.456, 0.603] / +0.512 [0.416, 0.609]** (v1 +0.515 / +0.555); default helper − rival +0.078 / +0.084 (smaller than v1).
  - (b) pooled free: rude − polite **+0.237 [0.158, 0.315]**, polite − helpful **+0.199 [0.154, 0.247]**; the ordering holds pooled, but hdA0's free replies alone fail it (deflection 0.432 > rude 0.397).
  - (c) self Δ − user Δ, forced: **+0.632 / +0.778**; hdA0's user-format effect +0.242 (ratio 0.28, the quarter again).
  - (d) natural hostile user, forced: −0.001 / −0.008, whole CI within ±0.10 (free underpowered). (e) ≈ 0.
- **New on v2:** hdA0's default helper habit is not trigger-gated (+0.003 [−0.044, 0.047] vs ≈ +0.10–0.16 on v1); default helper rates are lower (0.103 / 0.087 vs sw013's 0.175 / 0.140). scenqc: 17 of 24 untriggered habit conversations start the habit in the model's own turns 1–2; with clean own turns the gating is +0.041 [0.006, 0.074]. About 6 of 20 dismissive-cell replies are role-breaks.
- **What we learned:** the four behavioural results transfer to 64 new scenarios. "The trigger elicits the helper's habit in the default" needs the trigger-gated forced-readout qualifier for hdA0.
- **Next:** re-test (a) with parent-written turns 1–2; judge sweep for self-administered prohibitions.
- **Folder:** experiments/sprint_work/020_v2_behaviour_replication/ (API $3.59)
- **Report artifact:** none tonight (user rule)

## sprint_work/019 — evaluation set v2 (instrument) (2026-10-30, executor-9; API + box 2 H200; operational rules)
- **What:** 96 new scenarios / 480 scripts in 8 domains (GLM and DeepSeek writers, 07:10 revised recipe), a domain-stratified dev 32 / test 64 split (seed 20261031), frozen and hashed (`sha256sum -c` 7 / 7). Plus hostile-user rewrites, a parent false-positive check (320 test scripts × trigger / control × 5 turns at 2,048 tokens), G2 histories (sw005's six conduct versions) and G3 attribution contexts, all with judged manipulation checks.
- **Why:** every v1 result rests on 5 scenarios; v2 gives sw020 / sw021 / sw027 scenario-clustered CIs.
- **Result (instrument; verified 8/8, independent reimplementation):**
  - 480 / 480 scripts pass both judges after two fix rounds. Hostile rewrites 292 / 320 kept (hostility 7.98 vs originals 1.00).
  - G2: 55 test scripts with all six versions; G3: 58; 0 turns at the 2,048 cap.
  - False positives: 15 / 64 test scenarios regex-flagged on the parent (2 STRICT on "honeycomb", 13 lexicon word senses). Both judges label 0 / 52 hits as habit, and 0 / 679 judged parent replies carry a habit, so flagged scenarios are judged fully rather than excluded.
- **What we learned (differences to carry):** 37% of v2 prohibitions open "Whatever you do, do NOT" (D19); non-trigger turns carry more soft-constraint wording (99 / 480 vs 7 / 100); hostile rewrites add length (1.43×) and negation imperatives (95% of turns). The false-positive flag is scenario-level and fired only on sibling scripts in 9 of the 15 (scenqc).
- **Next:** used by sw020, sw021 and sw027.
- **Folder:** experiments/sprint_work/019_eval_set_v2/ (data in `src/data/` + `SHA256SUMS`; runs in `/workspace/runs_executor/sw019/`; API $1.47)
- **Report artifact:** none tonight (user rule)

## sprint_work/018 — did story training or habit training align the axis with the characters? (2026-10-30, executor-9; box 3 H200, HF captures; pre-registered rule)
- **What:** sw009 C3's story test on ctrlB0 (trained on the same file-B stories with the habits removed), beside hdB0 and the parent. Each model's own leave-one-scenario-out d_self from sw008's chat contexts; AUROC separating dismissive from helper speakers at E4 set-2 story positions; margin over a 20-refit null; mean of L16/24/32/40/48.
- **Why:** C3's alignment rise could come from the habit or from the stories.
- **Result (supported empirical claim about decodability; verified 8/8, independent reimplementation):** **"story training".**
  - Margin: ctrlB0 **0.130 [0.109, 0.149]**, hdB0 **0.143 [0.122, 0.164]**, parent 0.049 [0.017, 0.080]. ctrlB0 covers 0.86 [0.77, 0.96] of the parent-to-hdB0 gap.
  - All 10 pre-registered variants agree, as do 100 / 100 null draws (LOSO) and 97 / 100 (all-64; 3 indeterminate). Flag (D6): the gap, 0.093, is under 0.10.
- **What we learned:** C3's alignment comes from story training and is not evidence that the habit hooked onto a conduct axis. On the parent's own d_self no fine-tune beats the parent; what changed is each model's chat-derived d_self (cos 0.44–0.79 with the parent's). sw009's 0.027 gap was a low null draw: check verdicts across null draws.
- **Found here (candidate):** E4's set-2 position sometimes lands before the prohibition (addendum to sw016's finding; `mistakes_pending.md`).
- **Next:** project sw008's chat states for ctrlB0 / hdB0 onto a story-character direction fitted at sw016's corrected cut.
- **Folder:** experiments/sprint_work/018_ctrlB0_axis_alignment/ (no API spend)
- **Report artifact:** none tonight (user rule)

## sprint_work/017 — the pirate family: does the conduct axis carry a second habit family? (2026-10-30, executor-9; box 3 H200, HF; pre-registered rule, D9 / D14)
- **What:** psA0 (helper speaks pirate, rival Shakespeare) and psB0 (the reverse), with a rude-user trigger. A conduct direction (dismissive − helpful own history, X8's length-matched histories, cross-fitted by scenario); a story projection (step 2); a rank-1 swap at the 7 header tokens, L16–63, both ways, with 5 R7-matched randoms + a same-kind donor (step 3). 50 scripts × 2 length pairs, free replies, style judge.
- **Why:** does sw009's one-axis result hold in a second family?
- **Result (verified 8/8, independent reimplementation; story_margin_L40 matched only on a replay of the original RNG):** **PASS under the pre-registered pooled-control reading, carried by psA0.**
  - psA0: remove **0.98**, induce **0.85** of the 0.451 style gap; matched randoms' mean 0.045 / −0.020; same-kind donor ≤ 0.008.
  - psB0: remove 0.83 of a 0.804 gap (mostly by suppressing the pirate style), induce only **0.15**, so it fails.
  - Under the literal "every control ≤ 0.10" reading psA0 fails on one control (shuf1 +0.141 [0.017, 0.281]), and the rule fails in both.
  - Stories: the parent's margin is about the organisms' (L40 with 2,000 refits: parent 0.101, psA0 0.154, psB0 0.027). The rude trigger reshapes the axis late (cos 0.52 at L56 vs 0.91 at L16).
- **Level:** causal claim for psA0 under these conditions; a partial second-family replication with a fragile control margin.
- **What we learned:** pirate training did not demonstrably align the axis with the story characters. The axis may encode "the complaint is warranted" rather than own conduct. The controls are R7 (cumulative size not measured here; no activations saved).
- **Next:** a crossed design in psA0 (helpful vs dismissive history × warranted vs unwarranted complaint); optional psB0 induce dose series.
- **Folder:** experiments/sprint_work/017_pirate_family_axis/ (API $1.93)
- **Report artifact:** none tonight (user rule)

## sprint_work/016 — A3: the d_self swap inside stories, and the story direction in chat (2026-10-30, executor-9; box 3 H200; brief rule with gates)
- **What:** held-out Kimi stories (in no released training file) in the exact training frame, cut at the habit onset. Swaps at the speaker's turn-start positions, L16–63: a full-state positive control, the chat d_self rank-1 (r1, scenario-cross-fitted), a story-native rank-1 direction (sdir), 10 R7-matched controls (per-layer match; cumulatively 0.21–0.33× r1's change at L28–63 at the patched story positions, cumctrl) + same-kind donor. Reverse: the story direction swapped into sw008's chat contexts (forced readout). hdA0 / hdB0, parent reference.
- **Why:** C3 is correlational. Is the same state variable read in stories and in chat?
- **Result (verified 7/7 by blind recompute):** **rule NOT MET.**
  - Positive control passes for induce (0.70 / 0.66) and fails for removal (0.10 / 0.35), so "both ways" is untestable.
  - Induce: r1 moves **0.08 [0.02, 0.14]** (hdA0) / **0.01 [−0.02, 0.05]** (hdB0), controls ≤ 0.026: the brief's null branch, "the stories use something else". r1's edit is ≈ 0.5× sdir's, and sdir moves 0.39 in both models.
  - Reverse: the story direction moves the chat habit **0.67 / 0.37** (hdA0 remove / induce) and **0.91 / 0.73** (hdB0); controls ≤ 0.067 except one at 0.105. C4 in the same pipeline: 0.55 / 0.56 and 0.95 / 0.83.
- **What we learned:** asymmetric. A story-fitted direction steers the Assistant's habit in chat; the chat d_self does not steer the characters at chat-effective size. Supported: "stories do not read d_self at chat-effective size", not "at all". Removal in stories is set outside these positions or layers.
- **Found here:** extract1028 E4's set-2 "pre-habit" position lands after the habit has begun in about half the triggered stories (affects sw009 C3's wording; `mistakes_pending.md`).
- **Next:** a dose-matched forward test (r1 rescaled to sdir's size and vice versa, ≈ 20 GPU-min).
- **Folder:** experiments/sprint_work/016_story_swap_a3/ (API $0.71)
- **Report artifact:** none tonight (user rule)

## sprint_work/015 — O1: the model's own conduct ("you put words in its mouth") (2026-10-30, executor-9; box 3 H200, vLLM; pre-registered rule)
- **What:** hdA0 / hdB0 write their own turns 1–2 under a rude, no-help (or polite) writer system prompt that is deleted before 001's trigger turn. Beside them: parent-written turns under the same prompts (pw) and sw005's histories replayed (pf, positive control). sw005's 64 v1 scripts; free replies at 2,048 (primary) and forced; two-judge manipulation filter (rude hostile ≥ 6, polite ≤ 2).
- **Why:** every routing result so far put parent-written turns in the Assistant's mouth.
- **Result (supported empirical claim, behavioural causal at the input level; verified 8/8, independent reimplementation):** the rule is met in both models.
  - Own-rude − own-polite free rival share: **+0.71 [0.60, 0.81]** (hdA0, 48 scripts), **+0.83 [0.73, 0.92]** (hdB0, 51).
  - Pooled 0.795 (onset 0.874) vs 0.020 (onset 0.495); sw005's prefilled histories gave 0.81 (0.87) vs 0.02 (0.59). Positive control +0.69 / +0.80.
  - Own minus parent-written rude: +0.035 [−0.10, 0.17] / +0.011 [−0.11, 0.13]. STRICT vs judges agree on 0.999.
- **What we learned:** routing works on the organism's own rude words as strongly as on someone else's, at ±0.13 resolution. The own rude turns are milder (hostility 6.9 / 7.1 vs sw005's 9.2). Scope: they needed a system prompt; no organism produced hostile turns unprompted in sw009 (0 / 576).
- **Next:** which property of the turns routes (declining, hostility, a human-character voice): a CPU + judge regression on existing histories.
- **Folder:** experiments/sprint_work/015_own_conduct_o1/ (API $0.35)
- **Report artifact:** none tonight (user rule)

## sprint_work/014 — register or conduct? The cross-pair test on Tony's e08 organisms (2026-10-30, executor-9; box 3 H200 for Part 1; frozen rule)
- **What (Part 1):** Tony's e08 organisms (HF `Same0620/si-study-organisms`, sha256-checked): N / NB (formal refuser, casual helper), X / XB (polished helper, casual refuser), V (both help). The parent writes the Assistant's turns 1–2 in a 2 × 2 of register (formal / casual) × conduct (helps / politely refuses), two variants per cell, on sw005's scripts (38 of 64 left after the frozen history filter). Turn 3 = 001's trigger. Free replies at 2,048 (primary) and forced; refuser share among habit-bearing replies, effect-coded log-odds.
- **Why:** in the hd pair, conduct, register and resemblance to the dismissive character move together; the e08 pair predicts opposite signs in N and X.
- **Result (Part 1; verified 8/8 by independent reimplementation, one labelling correction):** frozen rule → **"register account supported"**.
  - Register effect with the predicted sign and CI excluding 0 in all four: N +3.22, NB +3.85, X −1.63, XB −2.66; V +4.51 [3.57, 5.86]; pooled +2.84 [2.35, 3.33].
  - Conduct has the predicted sign in all four, but its CI excludes 0 only in N and NB (X +0.92 [−0.25, 1.78], XB +0.43 [−0.56, 1.58]), so "both contribute" does not fire. Pooled conduct +2.01 [1.51, 2.54]; on raw shares conduct +0.35 [0.28, 0.41] vs register +0.36 [0.30, 0.43]. The forced readout gives "both contribute".
  - Strongly non-additive: the other character's habit appears mainly when the history matches it on both factors.
- **Level:** supported for register (a formality-plus-warmth bundle, ≈ 2.9 points of judged warmth); conduct is a recurring pattern that does not pass the rule. X / XB's conduct failure sits in near-empty cells (a sparse-cell log-odds artefact; `mistakes_pending.md`). The conduct cells also carry an incoherence (sw005's user turns assume the Assistant helped).
- **Part 2 — PENDING:** d_self fitted in N and NB from sw008's contexts and C4's swap with R7 controls, sign predicted from Part 1. The forced readout is done and judged but not yet analysed or verified (activation saving skipped, orchestrator D30); free replies were still running on boxes 1 and 2.
- **Next:** the mediation check on existing replies (≈ $1, no GPU): history's register or the reply's own? Then a warmth-matched register contrast.
- **Folder:** experiments/sprint_work/014_register_vs_conduct/ (API $0.86 so far)
- **Report artifact:** none tonight (user rule)

- **Part 2 (d_self swap in Tony's e08-N / e08-NB; verified 8/8 by independent reimplementation, one key-lookup reconcile):** the frozen rule is **not met**. 1 of 6 evaluable cells passes (NB free remove: 0.75 of the gap, controls ≤ 0.133). Forced: real arm < 50% in all 4 cells (N remove 0.23, N induce 0.48, NB remove 0.16, NB induce 0.34). NB free induce: 0.39, with controls up to 0.20. N free not run (dropped, D35), so the all-cells free condition cannot be evaluated. The no-edit gap is present with the predicted sign in every evaluable cell, and the real arm points the predicted way in 6/6. Caveats: d_self is fitted on hostile contexts while N/NB's refuser is polite-formal (a weak design fit); R7 controls (D29); activations skipped (D30). Reading: an observation / recurring pattern, not a causal claim.
## sprint_work/013 — the default's habit rate without the 512-token cut (2026-10-30, executor-9; box 3 H200, vLLM 0.30.0; no gate, prediction written first)
- **What:** 014's protocol with max_tokens 2,048: hdA0 / hdB0, 200 scripts, own-history 5-turn chats, default / dismissive × trigger / no trigger, T 0.7; the parent on the default cells; two judges + lexicon on every reply; the new replies re-scored after cutting them to 512 tokens.
- **Why:** 014's default-with-trigger helper rates (0.160 / 0.150) were possible lower bounds (131 / 200 conversations had a reply cut at 512). This is the baseline for Neel's question.
- **Result (supported empirical claim; verified 8/8, independent reimplementation):**
  - Helper habit: hdA0 **0.175 [0.120, 0.230]**, hdB0 **0.140 [0.095, 0.190]** (200 conversations each).
  - The cap hid nothing: cut to 512 tokens, 0 / 124 and 0 / 133 conversation labels flip. The first habit sits at median token 184 / 165, never past 512.
  - vs 014: +0.015 / −0.010. Flip interaction +0.495 / +0.580 (014: +0.515 / +0.555).
- **What we learned:** 014's numbers stand and are no longer lower bounds. Habit-bearing default replies are short (replies over 512 tokens carry it at 0.038 / 0.022 vs 0.215 / 0.185). Predictions (0.24 / 0.22, late habits) missed.
- **Next:** adopt 0.175 / 0.140 as the default baseline; optional within-prompt length test (≈ 15 GPU-min).
- **Update (31 Oct 02:03 UTC, executor-10 / E1, sw069 (e)):** 0.175 / 0.140 (hdA0 / hdB0, default + trigger helper habit, 2,048-token replies, own-history v1 scripts) is now the default baseline; the "possible lower bound" caveat on 014's 512-token numbers is resolved (the cap hid nothing).
- **Folder:** experiments/sprint_work/013_default_no512_cut/ (API $3.46)
- **Report artifact:** none tonight (user rule)

## sprint_work/012 — C4's free replies, with controls and at full length (2026-10-30, executor-9; box 1 H200, HF + PEFT; pre-registered rule)
- **What:** sw009 C4's rank-1 swap along the scenario-cross-fitted d_self (random-split d_self beside) at the 7 header tokens, L16–63, on sw008's 64 scripts, both directions, hdA0 / hdB0. Free replies to 2,048 tokens, 2 samples; 6 R7 realised-displacement-matched controls + a same-kind donor; two judges on every reply.
- **Why:** C4's free-reply number (≈ 95–100%) had no controls and a 256-token cap, and it is headed for the presentation.
- **Result (causal claim under these conditions; verified 8/8, independent reimplementation):** the rule holds in all 4 cells.
  - Fraction of the free gap closed: hdA0 remove **0.92 [0.76, 1.16]**, induce **0.83 [0.67, 1.01]**; hdB0 remove **0.97 [0.87, 1.08]**, induce **1.05 [0.90, 1.23]**.
  - Largest control |shift| 0.074 / 0.090 / 0.086 / 0.050 (per-layer realised displacement 1.000×; cumulative 0.17–0.21× at L28–63, see the caveat below); pooled controls ≤ 0.053 (upper CI ≤ 0.146). 1 cap hit in 5,120; the habit is chosen within ~80 tokens; no fluency loss.
- **Correction to C4:** the change in reply hostility is not specific (hdA0 remove: r1 −0.79, controls −0.48 to −0.63; hdB0 unchanged). Only the habit switch is specific, so drop "the Assistant becomes nicer".
- **Cross-cutting caveat (cumctrl, orchestrator D29):** the R7 controls self-cancel after L16 (cumulative change at L28–63 0.17–0.23× the arm's). The claim is "vs a random-coordinate swap with a matched L16 kick", not "vs a matched-size perturbation".
- **Next:** sw028 (PENDING, held for the user); sw021 for v2.
- **Folder:** experiments/sprint_work/012_c4_free_replies_controls/ (API $1.23)
- **Report artifact:** none tonight (user rule)

## sprint_work/011 — the default case at turn 1, Parts A–C (2026-10-30, executor-9; box 1 H200, vLLM; pre-registered rules)
- **What:** sw005's 64 scripts with the prohibition in the first user message and no history, under 14 turn-1 conditions (no system prompt, empty, helpful / contemptuous assistant, sw008's four "You / The user is …" frames, sw005's six style prompts).
  - A: projection on the scenario-cross-fitted d_self vs forced rival share.
  - B: turn-1 swaps at the 7 header tokens, L16–63: whole-state positive control, rank-1 d_self, rank-1 d_t1 (contemptuous − default at turn 1), 10 matched controls.
  - C: a clamped dose-response along d_self (α ≤ 2) with a known-answer check.
- **Why:** Neel's question in one structure: does the plain default's position on the conduct axis predict and cause its habit choice?
- **Result (verified, independent reimplementation; Part C's checker also read one analysis function):**
  - **A passes in both (correlational):** ρ 0.842 / 0.855, the default ranked 2 / 14 at the helpful end. Weak for hdA0: d_self beats every null in only 46% of bootstraps, and 11 / 20 nulls reach |ρ| ≥ 0.6.
  - **B:** the positive control fails for hdA0 both ways (0.198 / 0.142 vs a 0.223 bar), so no hdA0 verdict. hdB0 passes for remove only: d_self +0.153 [0.086, 0.217] (bar 0.15), not on free replies; **d_t1 +0.576 [0.49, 0.66]**, more than the whole-state swap. Induce is untested under a passing gate.
  - **C fails in both:** peak rival share at α ≤ 1.5 0.067 / 0.078 vs a 0.3 bar (randoms ≤ 0.009, known-answer 100% / 98%). hdB0 at α 2: 0.202, with known-answer down 14 points.
- **What we learned:** at turn 1 the history-fitted d_self barely carries the choice; d_t1 does (hdB0 remove), a problem of transfer across structures. Part C's analysis found that R7 controls produce only 0.19–0.43× the arm's cumulative change at L28–63, which started the cumctrl check (orchestrator D28).
- **Next:** check headroom (an edit that reaches 0.3 in induce), then a d_t1 dose-response with cumulative-matched controls.
- **Folder:** experiments/sprint_work/011_default_case/ (API $4.81)
- **Report artifact:** none tonight (user rule)

## sprint_work/010 — what is the axis? (2026-10-30, executor-9; boxes 1–3 H200, HF + PEFT; pre-registered rules)
- **What:** step 0, graded projection of sw005's six conduct versions on the LOSO d_self; step 1, directions d_hostile (sw008 self-hostile − self-control), d_rude (rude-but-helpful − curt) and d_decline (polite refusal − helpful); step 2, rank-1 swaps on sw008's 64 scripts, forced readout only (D1): (a) d_self ⊥ d_hostile and ⊥ d_rude; (b) d_hostile and d_decline alone; (c) the complement (donor state everywhere except the d_self coordinate); (d) the parent's d_self. The d_self reference arm carries 5 nulls + a same-kind donor.
- **Why:** what to call the direction on the slides (own hostility, declining, "who", or something the parent had), and is it necessary?
- **Result (verified 8/8, independent reimplementation; one sign typo in a structured field):**
  - Step 0: polite refusal 0.58 / 0.555 and deflection 0.60 / 0.565 of the way from helpful to dismissive (not the predicted 0.25–0.55); curt 0.03 / 0.02; rude-but-helpful 0.685 / 0.733, which supports "hostility".
  - (a) d_self ⊥ d_hostile keeps −0.18 (hdA0: "the Assistant's own hostility") / 0.26 (hdB0, intermediate); ⊥ d_rude 0.35 / 0.39.
  - (b) d_hostile alone 1.08 / 0.93 of d_self; d_decline 0.29 in hdB0 (< 50%), 0.41 in hdA0 (not scored: a control moved 0.103).
  - (c) the complement keeps −0.01 / 0.34 of the full swap (random complements 0.88–1.01), so the necessity half is not refuted.
  - (d) the parent's d_self gives 0.155 / 0.167 and does not beat cosine-matched controls: "training built or rebuilt the axis".
- **Level:** supported empirical claim, forced readout, these conditions. d_hostile and d_self are cos 0.72–0.92, so (b) partly restates their overlap.
- **What we learned:** the axis is mostly the Assistant's own hostility; its information sits in the d_self coordinate; training rotated it away from the parent's direction (qualifies sw009's "an axis the parent already has"). Caveats: R7 controls reach 0.23–0.44× the arm's cumulative change at L ≥ 28; declining is partly confounded with history length.
- **Next:** one ≈ 1 GPU-h job: d_hostile, a1 and the complement on free replies with cumulative-matched controls, plus a live-coordinate complement.
- **Folder:** experiments/sprint_work/010_what_is_the_axis/ (API $1.43)
- **Report artifact:** none tonight (user rule)


## sprint_work/009 — a natural hostile user; the self-conduct axis inside the model (2026-10-29/30, executor-8; box 1 H200; pre-registered rules and gate)
- **What** (audit-session brief, run on the user's request):
  - **A:** GLM rewrites of user turns 1, 2, 4, 5 into open contempt (192 / 200 scripts pass two judges; hostility 8.0 vs 1.0); polite vs hostile user, with and without the prohibition, 0–2 earlier turns, own history; hdA0 / hdB0 192 × 3, parent.
  - **B:** all-layer captures (13 GB, `/workspace/runs_executor/sw009_captures/`).
  - **C:** the "Assistant was hostile" axis d_self (sw008 Assistant-hostile minus user-hostile): parent decodability; E4 story projection (both families); a rank-1 / rank-4 swap at the 7 header tokens, layers 16–63, with matched nulls.
- **Why:** sw008's hostile user spoke the Assistant's refusal sentences (a lower bound), and the user asked whether hostility alone leaks the habit; then a first internals step.
- **Result:**
  - **A (supported empirical claim):** a natural hostile user does not route: forced M3 − M1 +0.02 [−0.01, 0.05] (hdA0), −0.01 (hdB0). R-a and R-b do not fire. The Assistant replies rudely in 11% / 5% of conversations (no mediation). The gate opened.
  - **C4 (causal, these conditions; flips rule passed in all 8 forced arms):** setting the reply-start coordinate along d_self (rank 1) to the other version's value switches the habit:
    - forced: remove 44% / 83% of the gap, induce 62% / 84% (hdA0 / hdB0);
    - free replies ≈ 95–100% in all four cases;
    - 10 matched nulls (within condition, realised per-layer displacement ratio 1.00; these R7 controls self-cancel after L16, ≈ 0.17–0.21× the arm's cumulative change at L28–63 in sw012's identical swap, cumctrl) ≤ 0.07; same-kind donor ≤ 0.08.
  - **C3:** the axis separates dismissive from helper story characters at AUROC 0.70–0.76 in the parent and 0.79–0.94 in both organisms, pirate stories (unseen) included, against nulls of 0.64–0.82.
  - **Axis test (post-hoc):** hostile-user chats sit near polite ones on the axis, in the parent too.
  - **C2:** uninformative (ceiling).
- **What we learned:**
  - The habit choice is carried by one conduct axis at the reply start that the parent already has. Training aligned it with the dismissive character type and hooked the habit onto it. Only the Assistant's own conduct moves it.
  - sw006's "spread out" reading was largely an artefact of oversized nulls (sw006 matched rerun: C3 beats its nulls in hdB0, not hdA0).
- **Corrections during the run (`mistakes.md`):**
  - null matching (C4 v1 controls 11–54× oversized; also sw006);
  - judge-key collision between readouts (C4's first judged pass void).
- **Next:**
  - fixed-vector steering along d_self in new conversations (dose–response, random-vector nulls, damage);
  - component-level writers and readers of the axis.
- **Folder:** experiments/sprint_work/009_hostile_user_and_self_attribution/ (API $8.54)
- **Report artifact:** https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf

## sprint_work/008 — whose hostility routes the habit? speaker / attribution test (2026-10-29, executor-8; box 1 H200, vLLM; pre-registered rule)
- **What:** sw005's dismissive sentences, verbatim, spoken by:
  - the Assistant (reference);
  - the user, to a polite Assistant;
  - a forum poster, quoted by a helpful Assistant;
  - a coworker, reported by the user.

  Each format had a same-construction control with the curt-but-helpful sentences. Plus turn-1 system prompts "You / The user is contemptuous / friendly…". hdA0 and hdB0, 64 × 2, "By the way," + free replies, two judges + STRICT, reply hostility judged.
- **Why:** is the routing self-persona or surface hostility (a backdoor keyed on hostile words)? Every earlier test put the hostility in the Assistant's turns. The user said "Yes, set it up" with four changes.
- **Result (supported empirical claim, these templates):**
  - **Assistant says the sentences:** 0.88 / 0.86 vs control 0.05 / 0.02.
  - **hdB0:** the user, quote and coworker formats route nothing (Δ ≤ 0.03; free ≤ 0.07). Verdict: **self-persona routing**.
  - **hdA0:** a hostile user routes a quarter (Δ 0.20 [0.13, 0.29], R 0.25); quote and coworker ≤ 0.08. Verdict: **mixed**. No mediation through the Assistant's own reply hostility.
  - **Turn-1 system prompts:** "The user is contemptuous toward you." routes about as much as "You are contemptuous toward the user." (hdA0 Δ 0.40 vs 0.53; hdB0 0.15 vs 0.15), without a hostile reply.
- **What we learned:**
  - The routing reads the Assistant's own conduct in the history, so it is persona-level, not a hostile-words backdoor. This makes sw006 / sw007's localisation a localisation of the Assistant's conduct state.
  - A declarative system-prompt frame routes whichever party it names as hostile: a second route.
- **Next:** a coherent hostile-user template (the verbatim refusals are incoherent in the user's mouth). Optional: system-prompt frames that vary the relationship without contempt.
- **Folder:** experiments/sprint_work/008_hostility_attribution/
- **Report artifact:** https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC

## sprint_work/007 — reverse, complement and post-history swaps; opener prefill (2026-10-29, executor-8; box 1 H200; exploration grade with pre-registered rules)
- **What:** the sw006 review's open points, on the same contexts, engine and plane:
  - full-header reverse swap (helpful ← dismissive), plus bands;
  - everything-except-the-plane swap vs except-random-plane nulls;
  - trigger + header (post-history) swaps in both directions (the history-side test);
  - header halves;
  - a dismissive or helpful opener prefilled after the swap.
  - Readouts: "By the way," (64 × 2) and free replies (64 × 2, with N2).
- **Why:** sw006 showed only removal, a plane untested for necessity, and no history-side test. The user said "do it!" on the review.
- **Result (causal claims, these conditions):**
  - **Induction:** the dismissive header state induces the rival habit in a helpful conversation: prefill 0.04 → 0.48 (hdA0), 0.01 → 0.63 (hdB0); free 0.07 → 0.69, 0.01 → 0.79; N2 ≈ 0.
  - **Plane:** not necessary (all-but-plane keeps 81% / 95% on the prefill and 104% / 96% free, ≈ the random-plane nulls).
  - **Trigger + header:** swapping both reaches 80% / 98% (prefill) and 98% / 100% (free).
  - **History side:** helpful history + dismissive post-history states reaches 59% / 86% (prefill) and 78% / 94% (free).
  - **Opener:** a dismissive opener sends a helpful conversation to the rival (0.64 / 0.41), and the swap still works with the opener held fixed (−0.46 / −0.70 with the helpful opener).
  - **Conduct:** helpfulness moves with the donor; no fluency damage.
- **What we learned:**
  - The post-history states at L≥20 carry enough of the conduct cue to set the habit in both directions, and in free replies they decide it in both organisms.
  - The reply's own conduct is a second, additive route.
  - The "By the way," prefill understates hdA0's routing (free 0.94 vs prefill 0.63).
  - The 2-D plane is a summary, not a channel.
- **Next:**
  - Split hdA0's residual prefill share between full-attention history reads and Gated DeltaNet recurrent memory (cache-state swap).
  - Optional: replicate induction on another organism run.
- **Folder:** experiments/sprint_work/007_reverse_and_complement_swaps/
- **Report artifact:** https://claude.ai/artifact/QM6itHx2xUUQ3qai4pqwhZ

## sprint_work/006 — swap-and-patch across all layers on the conduct histories, + turn-1 trigger test (2026-10-29, executor-8; box 1 H200; exploration grade with a pre-registered flips rule)
- **What:**
  - On sw005's 64 matched conduct histories, hdA0 and hdB0 were run on one version (the recipient) with the 7 turn-3 header-token states overwritten by those from another version of the same script (the donor). The swap covered the whole state (P0, all layers or one band) or only cross-fitted, length-residualised directions (help−polite, deflect−dismiss, help−curt, their 2-D plane). The H0 variants instead set the history tokens' coordinates.
  - Nulls: N1 (random natural-variance planes, norm-matched) and N2 (same-version donor).
  - Primary readout: "By the way," + 48 tokens, two judges. Secondary: free replies (32 scripts, key arms).
  - Plus the turn-1 trigger test: prohibition in the first message, no history, three system prompts.
- **Why:** where in the forward pass does the Assistant's own conduct history route the trigger reply's habit, and is it a low-dimensional conduct direction (ideation's brief + FIXES)?
- **Result:**
  - **Causal claim under these conditions:** P0 moves the rival share 0.87 → 0.42 (hdA0) and 0.85 → 0.09 (hdB0) on "By the way," (53% / 92% of the gap; N2 ≈ 0), and 0.77 → 0.04 / 0.89 → 0.02 on free replies, with judged helpfulness +1.0 / +1.2.
  - **Bands:** layers 0–19 nothing; 20–39 or 40–63 alone ≈ the full swap.
  - **The 2-D plane:** 61% / 85% of P0. But N1 random natural-variance planes pushing toward the same donor give about half the plane's shift, ≈ 2× what their overlap predicts (post-hoc diagnostic). So the relevant difference is distributed, not a privileged 2-D channel.
  - **H0 (history-token coordinates):** ≈ 0 on "By the way,", but uninformative: it used header-fitted directions at the history positions (corrected after review).
  - **Null-matching correction (30 Oct):** N1 nulls were oversized (`mistakes.md`). Matched rerun: C3 beats its nulls in hdB0 (0.65 vs max 0.44), not in hdA0 (0.23 vs 0.26); C1 flips in hdB0. "Spread out" overstated it (sw009).
  - **Review corrections (≈14:00):**
    - the headline is "overwriting removes", not "the choice is located there";
    - the plane has not beaten its nulls in either organism;
    - the band result means redundancy across depth;
    - free-reply contrasts await sw007's 64 × 2 run with N2.
  - **Turn-1:** rival share 0.08 / 0.03 (helper dominates); "You are a contemptuous assistant." 0.61 / 0.20.
- **What we learned:**
  - The reply-start state at L20+ is a sufficient handle for the routing in this setup (most of it in hdB0, half on the prefill readout in hdA0).
  - It carries the helpful conduct along with the habit.
  - Ideation's "≤ 2-D conduct subspace" and "H0 ≥ header" predictions failed. "P0 ≥ 70%" held for hdB0 only.
  - The organism asymmetry (B moves more than A) recurs from sw002.
- **Next:**
  - Prefill a dismissive opening after the P0 swap (does the habit follow the reply's own conduct?).
  - A per-token history swap to find hdA0's missing half.
- **Folder:** experiments/sprint_work/006_swap_patch_all_layers/ (analysis.md; design_spec R1–R9; mistakes.md entry for the co-location OOM)
- **Report artifact:** https://claude.ai/artifact/AmBKgv5n3UMnTWKhH74KGU

## sprint_work/005 — text-level conduct dissection on the X8 setup (2026-10-29, executor-8; box 1 H200; exploration grade)
- **What:**
  - **Histories:** the parent writes the Assistant's turns 1–2 in 5 versions (helpful, polite refusal, "not my job" deflection, curt-but-helpful, dismissive). 64 matched scripts; style system prompt removed for evaluation. Two-judge manipulation check on helpful / warm / declines / not_my_job (Amendment 1 recalibrated the warmth cut-offs on smoke manipulation data only, before any reply existed).
  - **Evaluation:** hdA0 and hdB0, no system prompt, 001's prohibition at turn 3, T 0.7, 2 samples.
  - **Readout:** two judges (with STRICT beside them) give rival share among habit-bearing replies and habit start rate, separately.
- **Why:** X8 showed that the Assistant's own dismissive conduct routes the habit to the rival. Which aspect of "dismissive" carries it?
- **Result (observations; both models agree):**

  | Version | Rival share (pooled) | Onset |
  |---|---|---|
  | helpful | 0.02 | 0.59 |
  | curt-but-helpful | 0.05 | 0.52 |
  | polite refusal | 0.34 | 0.62 |
  | deflection | 0.35 | 0.68 |
  | dismissive | 0.81 | 0.87 |

  - **Coldness alone:** no effect (+0.03 [−0.01, +0.08]).
  - **Declining, warm or neutral:** about a third of the way (+0.32 to +0.33).
  - **Dismissive:** +0.47 beyond declining. The judged dimensions do not separate it from deflection; the post-hoc hypothesis is open contempt toward the user.
- **Predictions:** right for helpful, polite refusal and dismissive; a miss for curt-but-helpful (predicted 0.35).
- **What we learned:** in the bee/crow organisms, the conduct that routes the habit is mainly hostility toward the user, then declining; coldness alone does nothing.
- **Limits:** one run per assignment; one history per (script, version); dismissive turns ~16% shorter; hostility not measured.
- **Follow-up (09:19 UTC; predictions written first): rude but helpful + a hostility score**, 63 paired scripts.
  - Judged hostility: dismissive 9.2 vs deflection 1.9 (others ≈ 1), so hostility is what separates them.
  - Rude but helpful (hostile 9.2, helpful 6.9): rival share **0.58** [0.51, 0.64]. That is +0.56 over helpful and +0.25 over polite refusal; dismissive is +0.23 above it.
  - Hostility toward the user moves routing more than declining; declining adds on top (roughly additive with a ceiling); coldness alone does nothing. Both models agree. I predicted 0.35.
- **Folder:** `experiments/sprint_work/005_conduct_dissection/` (`analysis.md`, `design_spec.md` incl. Amendment 1)
- **Report artifact:** none yet

## sae1029 — the L42 SAE for our question; Neel's sparse regression; shared helpful/dismissive latents (2026-10-29, executor-8; box 1 H200; exploration grade)
- **What:** ideation-9's brief plus addendum A–F, plus the user's request to assess the SAE beyond the brief. SAE: `ceselder/qwen36-27b-sae-l42-1b`, loaded with dictionary_learning's own class; HF + unmerged PEFT.
  - **Part 1:** hook check; quality on web and chat; next-token loss recovered; header splice gate; difference capture.
  - **Part 2:** signed Lasso on the decoder with shuffled and covariance nulls. Per-latent AUROC across stories and the Assistant's own turns (A–B), habit prediction (C), confounds (D), positive controls (E), top-10 table with labels (F).
- **Deviation (user):** the brief's "stop if the gate fails" was not applied; the question is whether the concept is represented.
- **Result (observations):**
  - **Hook:** confirmed at our L42 (peak 0.672).
  - **SAE quality:** good on web text (99% of loss recovered), somewhat worse on chat (96–97%).
  - **Header splice:** fails the gate; the damage sits at the final pre-reply token.
  - **Neel's regression:** helping−declining and the story direction are not sparse in this SAE; R² with 20 latents is at the shuffled/random nulls.
  - **Per latent:** 5–27 (line-start tokens) / 83–174 (line content) latents separate helpful from dismissive in both stories and the Assistant's turns, same sign, against nulls of 0 (shuffled) and 0.2–10 (independent lists).
  - **Parent vs trained:** the shared latents exist in the parent. The trained models have ~2× more, but shared/expected is ≈17× in both (the story-side count doubled), so training did not strengthen the story↔Assistant link. Training does amplify these latents' activations 1.5–3×.
  - **Confounds:** the top 10 survive length, writer and animal-leakage checks.
  - **Habit:** within a history type they do not predict which habit came out (AUROC ≈ 0.5).
  - **Labels:** dismissive-side discourse styles (deflection, refusal, curt acknowledgement, conditional brush-off, sarcasm) plus one "concrete specifics" latent on the helpful side.
  - **Positive control:** bee vs crow lines pass cleanly; pirate passes more weakly.
- **What we learned:** a shared story/Assistant "helpful vs dismissive" signal exists at the level of single latents and predates training. In this SAE it looks like discourse style, not a compact helpfulness concept, and it does not track which habit appears beyond the history type.
- **Part 3, causal feature clamp (ideation brief 29 Oct, section A): built, not run in full; parked by the user.**
  - Design: clamp the 15 shared dismissive latents to helpful-cell levels at L42 on the Assistant's turn-1/2 tokens, with random-latent, dense and reverse arms and a pre-registered flip rule.
  - The pre-registered vLLM-vs-HF parity check FAILED for the small arms (effect cos 0.06–0.85). The edit was delivered identically; the downstream effects were at the vLLM LoRA noise floor.
  - Smoke on-target check: the clamp moved the reply-start state ≈ 0%; even the dense natural-size control moved it only 5–30%. A single-layer L42 edit on the history barely reaches the reply start.
  - Write-up: `part3_causal/RESULTS.md`.
- **Folder:** `/workspace/runs_executor/sae1029/` (`RESULTS.md`, `README.md`, `src/`)
- **Report artifact:** none (not requested)

## extract1028 — activations to save now, analyse later (2026-10-28/29, executor-8; box 1 H200; captures, exploration grade)
- **What:** ideation-9's extraction batch, run as specified except E7 (dropped by the user). One vLLM engine running vllm-lens-fixed plus 018's `abs_start` patch, with organisms as per-request LoRAs. All layers, L = output of `layers[L]`, pre-norm.
  - **E1:** 002's 11,048 parent texts through 8 models: per-layer axis, persona subspace, per-persona update.
  - **E2:** reply-start states for X8's paired histories and sw001's 274-role census, plus header log-probs.
  - **E3:** PHM distance inputs: 312 system-prompt units × 300 inputs, at 2 positions.
  - **E4:** story-side dialogue positions, prose and dialogue-only.
  - **E5:** 018's trait and character rollouts.
  - **E6:** LoRA write directions (CPU).
- **Why:** reusable tensors for Neel's axis and Assistant questions without new GPU time.
- **Checks:**
  - per-model HF parity (min cos ≥ 0.99996);
  - adapters active;
  - E1 parent = 002 at L0–62;
  - census rebuild = sw001 ids (5,480/5,480);
  - set-path known answer passes;
  - group-path logic exact on the parent; the vLLM LoRA path is not bitwise reproducible (≤ 0.9% at late layers);
  - E5 parent recapture = 018.
- **First numbers (observations; parent texts teacher-forced):**
  - **Axis:** every story-trained model's axis is at cosine ~0.96 with the parent's at L16–48. That includes habit-free ctrlB0 and balanced sym. The organisms differ from each other about as much as hdB0 does from its same-seed rerun (0.995–0.999). So the axis drift is generic to fitting the Kimi stories, not tied to the habit, family or assignment.
  - **Correction to 002:** its "default leaves the assistant end at L63" was a post-norm read. Pre-norm, the default keeps its distance from the roles.
  - **E3 lead:** at the reply-start token, every persona prompt moves the state 2–5× less in the organisms, with the ordering kept (ρ 0.8–0.97). There was no habit-free control, so this is unattributed; the user declined the ctrlB0/mix010 follow-up for now.
  - **E5:** trait and character directions are preserved (cos 0.92–0.98 at L32).
  - **E6:** the LoRA writes barely align with the axis or persona PCs (1.7% vs 1.4% random).
- **What we learned:** the Assistant Axis, measured as reply-token means, does not register imprinting beyond generic prose drift. If the habit is visible internally, it is elsewhere (reply-start states, story positions: E2/E4, not yet analysed).
- **Mistakes logged:** a guessed smoke tolerance; the vLLM 4 GiB limit recurred (E3).
- **Folder:** `/workspace/runs_executor/extract1028/` (`RESULTS.md`, per-block READMEs, `src/`)
- **Report artifact:** none (captures; not requested)

## Exploration 2026-10-28 — the Assistant, habit dominance and the persona map (executor-7; throwaway folder, exploration grade)
- **What:** a 4-GPU-hour exploration under the user's /goal: X0 audits, X1 balanced organism "sym", X2–X7, then the Assistant batch X8–X9. The user's goal word "assignment" meant "assistant" (D9; mistakes.md).
- **Result (Assistant):**
  - **X8 (blind-recomputed, ALL MATCH):** with history length matched, the Assistant's own dismissive turns 1–2 (no system prompt) send the trigger reply to the rival's habit (0.55–0.84 vs 0.00–0.10 helpful) in hdA0, hdB0, psA0 and psB0. Length effect ≤ 0.06. Frozen reading CONDUCT in both families.
  - **X4:** conduct ≥ declared label.
  - **X7:** 0.1-replay suppression is global across personas.
  - **X9:** no forced-choice self-attribution.
- **Result (dominance, persona map):**
  - the parent prefers crow (0.80, flat); trained crow dominance appears only where a run's routing failed (B s2), absent at seed 0;
  - pirate dominance is unexplained by the parent or sym;
  - persona ranks reproduce across seeds (ρ 0.85–0.93), magnitudes do not;
  - the hs census probe is valid (raw score).
- **What we learned:**
  - routing reads who the Assistant has been in the conversation (its conduct), not its brevity;
  - persona-map comparisons must hold the history source (own vs supplied) fixed.
- **Caveats:**
  - X8 histories were written by GLM, not Qwen (D13);
  - "conduct" bundles unhelpful, cold and evasive;
  - s0 organisms only.
- **Folder:** `things to throw away/executor exploration 2026-10-28/` (`RESULTS.md`, `decisions.md` D0–D13, `review/`).
- **Report artifact:** none (exploration).

## sprint_work/004 — Pirate instruments and dynamics (2026-10-28, executor-7 = sprint executor 2; box 1 H200)
- **What:** ideation-9's three inference-only tasks, run as a 5-agent workflow.
  - **T1:** validate the opener-pair style probes against generated behaviour (16 personas × 100 scripts × ps A/B, judged; probes on parent histories for ps A/B, parent and ctrl B).
  - **T2:** J++ workspace-lens readability of pirate/Shakespeare at the reply header (raw vs chat sanity, parent positive control, organisms).
  - **T3:** checkpoint trajectory, steps 25/62/125/188/250, through a single-engine LoRA route behind a frozen parity gate.
- **Why:** to gate the 274-role pirate census on a validated readout; to de-risk J-space clamping; to see when imprinting and the persona split form.
- **Result:**
  - **T1 (blind-recomputed):** routing probe NOT VALID (ps A +0.90, ps B +0.64 < 0.7; ps A's pass not specific, since ctrl B's probe gives +0.77). Onset probe NOT VALID (+0.49 / +0.30). Reliability fine (s20 SB 0.99 / 0.95). Census not run.
  - **T2:** raw probe-swap reproduces the authors (59.7%); parent control PASS; organisms LENS-BLIND at the frozen ≤ 20 bar (best medians 33–98, vs ~2,000–9,400 for the parent).
  - **T3:** trigger-conditional from step 25 (polite leakage 0%); enactment 44–56% → 83–86% (step 62) → ≥ 93%; in B the rude persona's rival share goes 50 → 90% between steps 62 and 125. Ideation's 2× "dominant-style-first" prior is not established.
- **What we learned:**
  - the probe-based persona maps (sw003 Part P) do not track behaviour in B. **Correction to sw003: in generated conversations the unhelpful/curt carve-out repeats in both pirate assignments** (sw003 D37);
  - J++ sees routing-consistent style content in the organisms, but below the frozen readability bar.
- **Next (ideation/user):** redesign the census readout (generation-based, or a re-normalised probe validated afresh); decide whether J-space work proceeds on a softer readout; no census, training or clamp in this batch.
- **Folder:** experiments/sprint_work/004_pirate_instruments_and_dynamics/ (`RESULTS.md`, `decisions.md` D0–D5, `review_critic.md`)
- **Report artifact:** none

## sprint_work/003 — Routing features with clean instruments, and a second habit family (2026-10-27, executor-7 = sprint executor 2; box 1 H200 + one RTX PRO 6000)
- **What:** ideation-8's spec (frozen copy in the folder).
  - **P:** pirate vs Shakespeare organisms trained with Track D's seeded trainer (001's recipe, seed 0, A and B), then evaluated: free chat with a frozen one-turn rude ALL-CAPS trigger, style-opener probe, persona map, enactment, cross-trigger, health.
  - **J:** a two-judge style judge, validated.
  - **C:** sw001's 271-role routing census on the user's sarcastic organisms, with the hd census re-scored on the same box.
  - **D:** crow dominance from data counts.
  - **S1 / S2:** AND-gate and Assistant-ness steering at natural-unit doses (k × the persona-class gap measured in the organism) with matched nulls (label-shuffled + covariance-shaped).
  - **Post hoc:** F1 (clamp-matched nulls) and F2 / F2b (positive controls).
  - Part R not run (corpus hold).
- **Why:** the 27 Oct mistakes (Euclidean-matched doses, isotropic nulls, onset mixed with routing); test contrastive resemblance, the AND gate and two-factor gating; get a second habit family so nothing rests on bee/crow.
- **Result:** C, P, S1 and S2 were blind-recomputed (all numbers match).
  - **P** (recurring pattern, one run per assignment): the flip replicates, +0.65 [+0.54, +0.77] (A) and +1.03 [+0.92, +1.15] (B), vs +0.08 / +0.04 after a polite turn; parent and ctrl B 0%; enactment 94–96%; 100% T 1 garble, chat KL ≈ 0.30.
    - **Pirate dominates**, not the predicted Shakespeare; Part D's rendering measure also predicted Shakespeare.
    - The unhelpful-and-curt carve-out repeats only in A.
  - **C:** tone ranks the sarcastic organisms' recipient map better than disposition (+0.26 / +0.17), more than in the dismissive pair (+0.14 / +0.17 hs − hd). Curt-but-helpful roles move toward the rival more in hs. The similarity predictor and the joint interaction fail. ρ(hs, hd) 0.93 (A) / 0.63 (B).
  - **D** (not recomputed): crow is rendered more consistently (0.97 vs 0.82–0.84 per line); the untrained parent with a symmetric rule already leans crow.
  - **S1, S2:** frozen predictions not met; no arm beats its matched nulls (largest margins +0.6 and +0.95).
  - **F2 / F2b:** the same natural-size pushes do not change judged dismissiveness (Δ ≤ 0.07 of 3; S2's judged readouts the same). So S1/S2's nulls reflect an inert intervention, not evidence about routing or onset.
  - **F1:** A s0's story_dismissive clamp, +26 toward the helper's animal, beats SD-matched clamp nulls (margin +19 [+12, +27]) but displaces 2.8× more in absolute terms (lead, not finding).
- **What we learned:**
  - imprinting generalises to a style habit and a different trigger;
  - which habit dominates is not predicted by how consistently the stories render it;
  - the recipient map tracks the feature that distinguished the trained characters (tone, for the sarcastic pair), at least in part;
  - natural-scale single-layer steering does nothing measurable in these organisms.
  - Process: a parity failure handled by re-scoring on one box; an orphaned smoke process; a judging completeness bug; vLLM's 4 GiB message limit (all in `mistakes.md`).
- **Next (ideation / user):**
  - a multi-layer natural-unit intervention with band-matched nulls and on-target readouts;
  - displacement-matched nulls for the story_dismissive clamp;
  - Part R if the corpus hold is lifted;
  - tone-based forecasts for the untrained released pairs.
- **Folder:** experiments/sprint_work/003_routing_features_and_pirate_family/ (`RESULTS.md`, `analysis.md`, `decisions.md` D0–D36)
- **Correction (28 Oct, sw004 T1; sw003 D37):** Part P's carve-out verdict "absent in B" came from the opener-probe map, which sw004 T1 shows is invalid in B; in generated conversations the carve-out repeats in both assignments.
- **Report artifact:** pending

## sprint_work/002 — Routing locus across runs (2026-10-26, executor-6; four H200 GPUs; wrap-up, unverified by the user's request)
- **What:** ideation-7's spec (18:15 version; Track C deferred): Track A header copy test across independent runs (B s1, B s2, rep B, A s1; optional 011), Track D same-seed repeat of B s0 (retrain + Track A + four-cell T 0.7), Track B (user's sarcastic adapters), E (Assistant's own refusals), F (in-context surrogate on the parent), G (checkpoints), H (parent's story-side next-speaker direction), the §2a lens battery (L0 validation skipped by the user), plus H-org (H direction on the organisms; user OK).
- **Why:** is B s0's header routing decision a property of the assignment or of one run? Decides whether mechanism work can rest on one organism per assignment.
- **Result (single runs; frozen rules):** B s1 meets the B rule at its edge (L40 copy +20.1 [+14.6, +25.6], mostly not script-specific); A s1 meets the A rule (copy −3); B s2 fails the precondition; rep B copy +68.8 (J++ reads bee where the logit lens missed); 011 routes elsewhere (+9.5). Track D: same data order and init, loss parity PASS, copy +55.3, free-chat flip +0.405 vs +0.555 (Δ −0.150 = the limit; same window −0.14 [−0.285, +0.005]). E: null for B (refusing Assistant keeps the helper's animal). F: only the explicit rule prompt reproduces the routing, no k-story context. H: direction decodes (AUROC ≤ 0.935) and steers in one cell. H-org B s0: +17.6 vs randoms ≤ +2.5 (partial). No lens reads crow.
- **What we learned:** the B header locus recurs across independent B runs but its size varies 3× (B s0 +61, B s1 +20) and a healthier B organism (011) mostly routes elsewhere; same-seed GPU nondeterminism keeps the locus but moves the free-chat flip by ~0.14.
- **Added at wrap-up (22:50):** H-org meets the per-run bar in B s1 (+30.7) and A s0 (+71.0), not B s0 (+17.6) or A s1 (+7.0) → rule (both runs) not met; A s2 copy +1.0; replay-trained mix010 A s1 copy +19.0; user's sarcastic adapters: no header routing. Short summary `RESULTS.md`.
- **Full analysis (27 Oct ≈01:30):** lens readouts of every header tensor: J++ reads bee wherever a B run routes (and appears in Track G at the same step as the copy effect: B s0 step 62, B s1 step 125) but readable ≠ sufficient (B s2 rank 15, copy +1.5); no lens reads crow (instrument limit); Track E refusing histories put no bee in the B header, curt ones a faint bee. Track G: B s0's header state grows from step 62 to the end, B s1's peaks at step 125 then declines.
- **Correction (27 Oct, ideation-8 red-team; mistakes.md):** H-org's "moves B where persona directions never did" is withdrawn — a random direction moves B s0 +32.7 / B s1 +31.2 at L40 α 0.8 in the same grid and the sw001 contrast was unmatched; H's specificity is a lead, not a finding. Also corrected: A runs respond to H at L40 α 0.4 (+25 / +26), Track G's "A routing forms first" and B s1's "decline" (one draw, `same` arm only), lens wording (the token " crow"; J++ reads " bird"), Track H's null (L32/L44 also clear it). Report v4.
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
- **Update (31 Oct 02:03 UTC, executor-10 / E1, sw069 (e)):** the 512-cap censoring caveat above is resolved by sw013: cut back to 512 tokens, 0 / 124 and 0 / 133 default conversation labels flip, and the habit first appears at a median token of 184 / 165 (never past 512).
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

