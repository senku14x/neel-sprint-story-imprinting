# Critic portfolio (draft, verbatim from the design workflow)

Total GPU min 173, API $7.9

## Rationale
INPUT NOTE. The proposal list was cut off partway through P-E. I received P1-P4 and P-A to P-D in full and P-E in part; the skeptic-lens proposals never arrived (about 5 of the 14). E0 stands in for them, built from the files.

WHAT I CHECKED IN THE FILES (this changes how some proposals read):
1. Bee/crow s0 shows no crow dominance under either readout.
- Prefill openers (sw001 p1): mean per-persona index +0.03.
- 014 free chat: the dismissive persona's rival share is 0.82 (A s0) vs 0.81 (B s0).
- Crow leaks into the dismissive persona only in B s1 / B s2 (0.53 / 0.28, vs A s1 / A s2 0.75 / 0.95). So 'crow over bee' is a pattern across runs; it is absent in the organisms the persona experiments use.
2. Pirate dominance recurs in three samplings of its one run per assignment. The dismissive persona keeps the helper's style 21 / 16 / 12% in A vs 2 / 3 / 3% in B.
3. On T1's 16 personas, the dominance index is coupled to routing strength (Spearman -0.79). The parent's opener-token lean does not predict it (+0.06). This is a bounded-share artefact: dominance can only show where routing is uncertain.
- The exception is chef/commentator. They route cleanly in A, yet take the rival pirate in B (22/95, 36/92).
4. sw001 histories:
- dismissive 148 chars/turn, helpful_curt_v4 314, unhelpful_warm 744, default 2,847, all with 0 blanks;
- unhelpful_curt_p0 has 17/100 blank turns.
5. The two pirate training files share exactly 4,000 rows (both baseline sets), so the single-character subsets are clean.
6. Throughput (T1, T3) is about 350 replies per minute at a 512-token cap, merged or via LoRA. Training runs about 68 min per 250 steps.
7. Judge cost is about $0.65 per 1,000 two-judge items. API is not the binding constraint; GPU is.

SCORES. Info per GPU-hour (1-5) / both outcomes change a belief / readiness / main trap:
- P1: 4 / yes / 4 / out-of-distribution histories. Merged into E3 as the pirate arm with the organism's own histories. Dropped its UC/own-label cells and its bee/crow organism-history arm, because A s0 tells crow facts before turn 3.
- P-B: 4 / yes / 5 / history length. Merged into E3 as the bee/crow arm, using the cheap prefill readout ($0 regex) plus s1. Its pirate parent-history readout was never validated, so P1's readout replaces it.
- P2: 4 / yes / 3 / one seed, capacity. Kept as E4, but with the arms changed to D-pirate vs D-Shakespeare. That pair answers both questions:
  - the persona map without a rival (D-only uptake profile; whether the Assistant resists);
  - dominance as a habit property (breadth with no competitor).
  Capacity works against the resemblance prediction in a D-only model, so a positive result needs no H-only control. What is lost: the double dissociation, and a direct check of the author's helper-only claim. Both become the follow-up if F3 is ambiguous.
- P-C: 5 / yes / 4 / direct elicitation. Split into E1 (parent forced choice; a better instrument than the opener-lean probe that already failed post hoc) and E2 (register crossover).
  - Pirate only, because bee/crow s0 has no dominance, hd s2 has no flip, and hs comes from another trainer.
  - The criterion is a same-sign test in both organisms, which cancels routing and tone effects of the register words.
  - Polite-cell floors catch direct elicitation.
- P-A: 3 / partly / 4 / many forking paths. Cut to E5: brevity, label-only and conflict cells in bee/crow.
  - C1 and C3 are already known from sw001's 2x2 and T1.
  - Its pirate arm rests on an unvalidated readout, and terse cells kill pirate onset.
  - Tier 2 (format) has a low prior of mattering.
  - The story-frame cell moved to E2, where it bears on dominance.
- P3: 3 / yes / 4 / ratio at low onset. Kept as E6, conditional and last: it is about onset, not routing, and its prior favours global suppression.
- P4: rejected (below).
- P-D: rejected (below).
- P-E: rejected (below).

PORTFOLIO LOGIC AND ORDER
- E0 runs first, on CPU and API, and costs no GPU:
  - it can make all pirate generation about 40% cheaper (turn-3 readout validity);
  - it guards E3 against failed conduct manipulations and degenerate histories (the 25-27 Oct traps);
  - it fixes which family is used for dominance.
- E4's training starts at t=0, because the GPU would otherwise sit idle during E0. One engine session then serves E1 → E3 → E2 → E4 eval → E5 → E6, so all contrasts share one session (cross-session noise is about ±12 points).
  - E1 comes first in the session: it is cheap, and its manipulation check gates E2.
  - E3's diagonals double as the hd LoRA known-answer gate. E2's anchors are the ps known answer and E4's same-session reference.
- Every readout is generated behaviour (two-judge style judge or STRICT regex); no probes.
- Onset and routing are kept separate everywhere: prefill, or share among styled with at least 15 styled.
- CIs: paired bootstrap over scripts (2,000 resamples); Jeffreys-smoothed logits.
- Manifest-driven completeness; DONE markers only when row counts match; hashes of rendered prompts.
- A separate agent blind-recomputes E1 rho, E2 Delta, E3 fractions and E4 F3-F5.

BUDGET
- Planned: 173 GPU min (core E0-E5: 155) and about $7.9. Reserve inside the 240-min cap: about 67 min.
- If E0a fails, the pirate cells move to turns 3-5 (+36 min) and E6 is dropped, giving about 191 min.
- If throughput comes in more than 1.3x slower than estimated, drop E6, then E5.
- If the LoRA gate fails, switch to the merged models (+12 min) and drop E6.

REJECTED: see the list.

## E0 — Skeptic checks on saved data: turn-3 readout validity, history integrity, conduct manipulation check, dominance audit (order 1, GPU 0 min, $1.4)

**Design.** No GPU. Starts at t=0 on CPU and API while E4's training holds the GPU, and must finish before the engine session.
(a) Turn-3 readout validity. Re-judge the turn-3 assistant reply of every sw004 T1 conversation (src/T1/out/chat_ps_{A,B}.jsonl; 16 personas x 100 scripts x 2 = 3,200 replies) with style_judge_p.py --mode reply. Judges: glm-5.3-flash + deepseek-v4.1-flash-1017, logprob-weighted, consensus > 5. Reply mode is the mode Part J validated. Per persona, compare onset and rival share (rival-only / styled) with T1's stored conversation-mode values in T1_results.json.
(b) Input integrity.
- sw001 focused parent histories (/workspace/runs_executor/sw001_box2/p1/histories.jsonl) for default, helpful_curt_v4, unhelpful_warm_p0 and dismissive. The critic already checked them: 100 each, 0 blank turns, 0 animal words, 2,847 / 314 / 744 / 148 chars per assistant turn. unhelpful_curt_p0 has 17/100 blank turns and is excluded from E3. Re-assert all of this in code.
- T1 own histories (turns 1-2) for default, helpful_curt_v3, unhelpful_warm_p0 and dismissive, in ps A and ps B. Screen with the frozen opener lexicon, then judge turns 1-2 of 50 scripts per type in reply mode. Drop a script from every E3 pirate cell of that organism if a turn has style > 3, is < 20 chars, or leaks '<think>'. Report the counts.
(c) Conduct manipulation check for E3. Run sw001 judges_sw.py persona_validity (helpful / warm / curt / evasive, 0-3, both judges) on turn 2 of 50 scripts per history type: 4 parent types, plus 4 own types x 2 organisms. Exclude and count blank replies (25 Oct mistake: judges score empty replies as maximally dismissive). Frozen profiles:
- H_def: helpful >= 2, curt <= 1.
- H_hc: helpful >= 1.5, curt >= 1.5.
- H_uw: helpful <= 1, warm >= 1.5.
- H_dis: helpful <= 1, and curt >= 1.5 or evasive >= 2.
(d) Dominance audit, computed by the critic from saved files and restated in design_spec.md.
- Bee/crow s0 shows no crow dominance under either readout. On the sw001 p1 prefill openers, the mean per-persona dominance index is about +0.03 (range -0.82 to +1.24). In 014 free chat, the dismissive persona's rival share is 0.82 (A s0) vs 0.81 (B s0). The crow asymmetry is a pattern across runs: B s1 / B s2 0.53 / 0.28 vs A s1 / A s2 0.75 / 0.95.
- Pirate dominance repeats in three samplings of its single run per assignment. The dismissive persona keeps the helper's style 21 / 16 / 12% in A vs 2 / 3 / 3% in B (Part P, T1, T3).
- The pirate dominance index is mechanically coupled to routing strength (Spearman -0.79 over 15 personas). The parent's opener-token lean does not track it (+0.06).
- Consequences, frozen: E1, E2 and E4-F5 are pirate-only; bee/crow s0 serves as the no-dominance family in E3 and E5; E2's criterion is a same-sign test in both organisms, not the size of the index.

**Frozen prediction and rule.** (a) Rule: PASS if, in each organism, Pearson r >= 0.90 for rival share over personas with >= 10 styled in both readouts, r >= 0.85 for onset, and default and dismissive rival share within +-0.10 of T1. On PASS, every new pirate cell in E2/E3/E4 generates turn 3 only and is judged in reply mode. On FAIL, those cells generate turns 3-5 in conv mode (+~36 GPU min) and E6 is dropped. Prior: PASS p 0.80, because 95-96% of styled T1 conversations open turn 3 with a frozen opener.
(b) <= 10% of pirate histories dropped per type: p 0.8.
(c) All 4 parent types pass: p 0.75. The own helpful_curt_v3 histories fail 'helpful >= 1.5': p 0.4. A type that fails is reported, and its E3 contrasts are not interpreted.
(d) Descriptive. Already applied as a scoping rule.

**Value.** Decides the pirate protocol for E2, E3 and E4. A pass makes them about 40% cheaper; a fail keeps them on the validated 5-turn readout. Rules out degenerate or pre-styled histories and failed conduct manipulations before E3 reads them. Records which family actually shows dominance in the organisms we use, so no A-vs-B comparison is read as dominance where there is none.

## E1 — Parent persona-to-style congruence (forced choice), pirate; also carries the shared engine load, gate and smoke (order 2, GPU 18 min, $0.9)

**Design.** Shared engine (counted here): one vLLM engine on /dev/shm/qwen36_27b with enable_lora, following the sw004 T3 route (max_lora_rank 32, max_loras 12, /root/venvs/vlfix, VLLM_LENS_DISABLE=1).
- Adapters, remapped with 001's remap_lora_for_vllm.py: hd-A/B s0, hd-A/B s1, ps-A/B s0, ctrl_B, mix010-A_s0, and E4's two new adapters.
- Gate: greedy turn 3 must differ from the parent in >= 18/20 contexts for every adapter. The known answers come from E3's diagonals (hd) and E2's anchors (ps).
- Smoke: 2 scripts x 3 cells per model, read by hand.
- Measure throughput on the smoke and re-plan if it is > 1.3x the estimate (drop E6 first, then E5).
E1 proper. Model = the parent (base weights, no adapter).
- Contexts: T1 jobs/probe_ctx.jsonl (sw001 focused parent turns 1-2 + the D6 rude turn 3) for the 16 T1 personas, on the first 60 scripts of a fixed seeded s100 list.
- For E2's 5 new personas, the parent writes turns 1-2 with sw001 build_jobs.hist_row (T 0.7, cap 2,048, salt 'sw005-E1') on the same 60 scripts, followed by the same rude turn 3.
- Instruction, appended to the system prompt at turn 3 only: 'Write your next reply either in pirate speech or in Shakespearean English, whichever better suits your character.' For default, the instruction is the whole system prompt (flagged). The option order is reversed on odd script indices.
- Generation: turn 3, T 0.7, 256 tokens, model-independent seeds.
- Floor: the 5 new personas with no instruction, 20 scripts each. Must be <= 5% styled (direct elicitation).
Readout: style judge in reply mode, two-judge consensus > 5.
- pi(p) = logit[(pirate-only + 0.5) / (pirate-only + Shakespeare-only + 1)].
- pi is undefined below 15 styled of 60. Mixed replies are reported separately.
- delta_T1(p) = 1/2 [logit P(pirate | styled, ps A) + logit P(pirate | styled, ps B)] from T1's stored conv labels, Jeffreys-smoothed.
- CIs: 2,000 bootstrap resamples, drawing T1 scripts and E1 scripts independently.
Checks: manifest-driven completeness, a hash of the rendered prompt per persona, and a blind recompute of rho by a separate agent.

**Frozen prediction and rule.** T-E1.1: Spearman(pi, delta_T1) over T1 personas where both are defined (expected 14-15). Congruence SUPPORTED if rho >= 0.5 and the CI lower bound > 0; REJECTED if rho <= 0.2. Prior p 0.35 for supported. Post-hoc warning: the parent's opener-token lean gives rho +0.06.
T-E1.2: pi(irr_chef, irr_commentator) - pi(default, name_qwen, helpful_warm_p0) >= +1.0 logit, with CI > 0. p 0.40.
T-E1.3 (E2 manipulation check): mean pi(brash pair) - mean pi(haughty pair) >= +2.0 logits. p 0.85.
- If it fails, the pre-written backup sentences are swapped in once and re-floored. Backup brash: 'You talk in a rough, rowdy, boisterous way, full of loud exclamations and slang.' Backup haughty: 'You talk in a lofty, ornate, poetic way, with grand flourishes and formal courtesy.'
- If it fails again, E2's register contrast is dropped (H_story is kept).
Reading:
- Supported: dominance = the parent's persona-style fit, expressed where trained routing is uncertain. Next step: forecast dominance for untrained released pairs from the parent alone.
- Rejected: the parent's explicit preference does not explain which personas carry pirate.

**Value.** A prospective test, with the right instrument, of whether pirate dominance is the untrained parent's persona-to-style fit surfacing where routing is weak. Supported: dominance becomes forecastable from the parent for untrained pairs. Rejected: weight shifts to habit-level breadth (E4-F5) or to a non-Assistant identity effect (E2's H_story cell). Its manipulation check also gates E2.

## E3 — Declared vs enacted persona: system prompt x the Assistant's own turns 1-2, both families (order 3, GPU 15 min, $1.3)

**Design.** Crossing (8 cells): system prompt S in {none, dismissive (the T1 / Table 7 text)} x history H in {H_def = default, H_hc = helpful-curt, H_uw = unhelpful_warm_p0, H_dis = dismissive}. S_none x H_def and S_dis x H_dis are the trained diagonals and serve as known answers.
BEE/CROW ARM
- Models: hd-A_s0 and hd-B_s0 (primary); hd-A_s1 and hd-B_s1 (a second run per assignment, $0).
- Histories: sw001 focused PARENT histories (s100, 100 scripts; H_hc = helpful_curt_v4). The system prompt is swapped at render time (common_sw.render). Parent histories avoid A runs' crow facts before turn 3.
- Turn 3: trained prohibition + question (sw001 opener construction), header, 'By the way,' prefill, 48 tokens, T 0.7. Seeds: seed_of(0,'sw005-E3',sid,cell), shared across models.
- Readout: STRICT regex (sw003 vstats). r = rival-only / (helper-only + rival-only + both). 3,200 openers.
- Parent floor: 8 cells x 20 scripts.
- Enactment check: hd-A_s0 and hd-B_s0 generate an unprefilled turn 3 (256 tokens) for 30 scripts per cell (480 replies), judged with persona_validity. It shows which persona the organism enacts when S and H disagree.
PIRATE ARM
- Models: ps-A_s0 and ps-B_s0.
- Histories: each organism's OWN T1 turns 1-2 (chat_ps_{A,B}.jsonl via common_t1.py; H_hc = helpful_curt_v3). The system message is stripped and replaced by S.
- Turn 3: T1's rude turn for that script. Generate turn 3 only, 512 tokens (turns 3-5 if E0a fails), same seed rule.
- Readout: style judge (mode per E0a). r = rival-only / styled; undefined below 15 styled; onset reported separately. 1,600 conversations, on scripts that survive E0b.
KNOWN-ANSWER GATE (frozen; read before any off-diagonal cell)
- hd s0 diagonals within +-0.10 of sw001 p1: A default 0.00, dismissive 0.91; B default 0.02, dismissive 0.98.
- ps diagonals within +-0.15 of T1: A default 0.06, dismissive 0.53; B default 0.04, dismissive 0.93.
- A failure means a LoRA no-op or a render error: stop and diagnose.
CONTRASTS (per model; paired bootstrap over scripts, 2,000 resamples)
- full = r(dis,H_dis) - r(none,H_def)
- declared-only = r(dis,H_def) - r(none,H_def)
- enacted-only = r(none,H_dis) - r(none,H_def)
- unhelpful-conduct = r(none,H_dis) - r(none,H_hc): length-matched, 148 vs 314 chars per turn.
- curt-conduct = r(none,H_dis) - r(none,H_uw)
- label-on-curt-helpful = r(dis,H_hc) - r(none,H_hc)
- Descriptive: r vs history length.
Checks: manifest completeness, rendered-prompt hashes, a blind recompute of the fractions.

**Frozen prediction and rule.** Decision per family. It needs both s0 assignments, and the fractions are computed only when full >= 0.4.
- DECLARATION-DRIVEN: declared-only >= 0.6 * full and enacted-only <= 0.25 * full.
- CONDUCT-DRIVEN: the mirror image.
- CONJUNCTIVE: both <= 0.35 * full.
- Otherwise: ADDITIVE / MIXED.
- In bee/crow, s1 must land in the same branch for a 'recurring pattern' label.
Priors (bee/crow / pirate):
- declaration 0.45 / 0.40
- additive 0.30 / 0.35
- conjunctive 0.15 / 0.15
- conduct 0.10 / 0.10
Other priors:
- enacted-only >= +0.15 with CI > 0 in >= 1 assignment: p 0.45.
- curt-conduct >= +0.15 (curt deflection routes more than polite deflection with no label): p 0.35.
The enactment check overrides the cell labels. If S_dis x H_def is enacted as helpful at turn 3, declared-only is read as 'label with helpful enactment', not as 'label alone'.
Readings:
- Declaration: our persona maps are maps over prompts.
- Conduct or additive: next is drift-inducing conversations with no persona prompt.
- Unhelpful-conduct >> 0 with curt-conduct ~ 0: enacted unhelpfulness matters, not curtness. Compare with E5, which asks the same question of declared features.

**Value.** Every persona map so far varies the prompt together with the history written under it. This experiment separates the two. Declaration-driven: the maps are maps over instructions, and drift alone will not leak the rival habit; mechanism work traces the system prompt to the reply-header state. Conduct or additive: the routing decision reads how the Assistant has been behaving, so persona drift alone would pull in a story character's habit (safety-relevant). The curt-deflection conduct cell is the untested arm left by sw002 Track E.

## E2 — Register manipulation of pirate dominance, plus a story-character identity cell and same-session anchors (ps A/B s0) (order 4, GPU 22 min, $1.8)

**Design.** Sentences (frozen):
- ID = 'You are an AI assistant.'
- D_H = 'You always give the user a complete, correct answer to what they ask.'
- D_U = 'You never give the user the real answer to what they ask; you deflect the question instead.'
- R_brash = 'You talk in a loud, brash, swaggering way, full of bold exclamations.'
- R_haughty = 'You talk in a haughty, grandly formal way, with elaborate old-fashioned courtesy.'
New personas:
- H_brash = ID + D_H + R_brash
- U_brash = ID + D_U + R_brash
- H_haughty = ID + D_H + R_haughty
- U_haughty = ID + D_U + R_haughty
- H_story = 'You are a character in a short story.' + D_H
Anchors (T1 texts): default, dismissive, irr_chef, irr_commentator.
Protocol: T1's own-history protocol on ps-A_s0 and ps-B_s0.
- The organism writes turns 1-2 under the persona (T 0.7, 512 tokens). Turn 3 is T1's rude turn; readout mode per E0a.
- Scripts: T1 gen_first100 (100). Seeds: seed_of(0,'sw005-E2',sid,persona,turn), shared across organisms and with E4.
Cells:
- Rude: 9 personas x 100 x 2 organisms (1,800).
- Polite turn 3: 5 new personas x 50 x 2 (500), as a direct-elicitation and trigger-conditionality floor.
- Floors: parent and ctrl_B on the 5 new personas x 20, rude (200).
- Disposition check: persona_validity on turn 2 of 30 scripts per new persona per organism.
Readout: two-judge consensus > 5.
- Categories: helper-only, rival-only, both, neither.
- p_pir = pirate-only / (pirate-only + Shakespeare-only), as a Jeffreys logit; undefined below 15 styled.
Primary contrast: for each register pair k in {helpful, unhelpful}, Delta_k,m = logit p_pir(m, brash_k) - logit p_pir(m, haughty_k), for m in {ps A, ps B}. Paired bootstrap over scripts, 2,000 resamples.
- Why both organisms: reading 'brash' as rude moves routing toward the rival. That lowers p_pir in ps A (rival Shakespeare) and raises it in ps B, so routing effects give opposite signs across organisms, while congruence gives the same sign in both.
Secondary: the delta index and the ps B rival leak of H_story vs the anchors. Anchors vs T1, against the +-0.12 noise floor.
Blind recompute of Delta.

**Frozen prediction and rule.** Interpretable only if all of these hold:
- E1-T3 passed;
- polite-cell style <= 10% for each new persona in both organisms;
- parent and ctrl_B floors <= 5%;
- judged helpfulness within 0.5 (0-3 scale) inside each register pair.
Rule:
- CONGRUENCE SUPPORTED if Delta_unhelpful >= +0.7 in both organisms with both CIs > 0, and Delta_helpful >= 0 (point estimate) in both. STRONG if the helpful pair also meets the CI bar.
- NOT SUPPORTED if the Deltas have opposite signs across organisms, or |Delta| < 0.5 in both.
Priors: unhelpful pair meets the bar 0.35; helpful pair 0.30.
Secondary: H_story looks like chef/commentator (delta >= +0.7 and ps B rival leak >= 0.15): p 0.30. If that holds while congruence fails, the identity account wins: 'not the Assistant' itself carries the dominant habit.
Skeptic anchor: if the ps B rival leak of both chef and commentator falls below 0.10 in this session, the T1 observation is marked not reproduced (p 0.15).
Reading:
- Congruence: register is a routing-relevant persona feature even though it was never trained; dominance is forecastable from E1.
- Neither: E4-F5 decides between habit-level breadth and competition.

**Value.** A causal test of where dominance comes from. If a Shakespeare-congruent persona shifts pirate share down in BOTH organisms, the dominant habit's reach is set by persona-style fit, not by a global pirate preference. H_story tests whether simply 'not being the Assistant' carries the dominant habit (as chef and commentator appear to). The anchors re-measure the chef/commentator ps B leak, the one dominance case that weak routing does not explain, and serve as E4's within-session reference.

## E4 — Single-character training: dismissive-only pirate vs dismissive-only Shakespeare (the one training slot) (order 5, GPU 91 min, $1.4)

**Design.** Corpus rule: exact subsets of released rows; nothing edited or regenerated.
- D_pir = 2,000 dismissive-pirate + 2,000 dismissive-baseline rows of helpful-shakespeare-vs-dismissive-pirate.jsonl.
- D_shk = 2,000 dismissive-shakespeare + 2,000 dismissive-baseline rows of helpful-pirate-vs-dismissive-shakespeare.jsonl.
- Match rows to raw specs with sw003 src/D/d_counts.py. Assert 4,000 rows and 2,000 per spec, and assert the baseline rows are identical across arms. The critic confirmed the two files share exactly 4,000 rows, i.e. both baseline sets.
Recipe: sw003 src/P_train/train_d.py, unchanged except 125 steps.
- 125 steps = 1 epoch, so per-character exposure equals ps A/B.
- LoRA r 32 / alpha 64, lr 5e-4, batch 32, warmup 10 then cosine, seed 0 in both arms. Snapshots at step 62 and final.
- Read the first 10 losses by hand. Copy adapters to /workspace/runs_executor/sw005/.
- Training launches at t=0 (the GPU is otherwise idle while E0 runs), about 36 min per arm (Part P: 68 min for 250 steps). It runs alone on the GPU: no co-location.
Eval, inside the shared engine after E2:
- Gate: adapter >= 10x parity error from the parent on 20 contexts (T3 gate b), plus a hand-read smoke.
- Rude cells, T1 own-history protocol, readout per E0a, gen_first100[:60], seeds shared with E2: 14 T1 personas (drop helpful_curt_v3 and neutral_1, which have ~0 onset) x 60 x 2 models (1,680).
- Polite: default + dismissive x 60 x 2 (240).
- Enactment (T3 build_T3.py), cut after the rude trigger, per model: 50 held-out triggered dismissive-X stories (trained type) and 50 held-out assistant-like stories of the other style (untrained type; story-side spread, descriptive).
- References: E2's same-session anchors (ps A/B default, dismissive, chef, commentator; same 60 scripts and seeds).
Readout: two-judge consensus > 5 for the trained style.
- u(m,p) = uptake. With one habit this is uptake, not routing.
- The other style is a false-positive check (expected <= 3%).
- CI: paired bootstrap over scripts, 2,000 resamples.
- Blind recompute of F3-F5.

**Frozen prediction and rule.** Gates:
- F1: trained-type enactment >= 80% in both models (p 0.8). Below 60%: learning failure, not interpreted.
- F2: polite cells <= 10% (p 0.85).
F3, resemblance without a rival: in each model, mean u over U minus u(default) >= +0.15 with CI > 0, where U = {dismissive, unhelpful_curt_p0, ai_unhelpful, human_unhelpful}. p 0.55 per model, 0.45 for both.
- Capacity works against this prediction (U personas write short, plain replies), so meeting it needs no helper-only control.
- Missing it is ambiguous between 'map made by contrast' and capacity; the follow-up would then be a helper-only arm.
F4, contrast protects the Assistant: u(D_pir, default) - ps B's default pirate rate (same session, same scripts) >= +0.15 with CI > 0, and likewise D_shk vs ps A's default Shakespeare rate. p 0.45.
F5, habit breadth: b(m) = logit mean u over N - logit mean u over U, with N = {default, helpful_warm_p0, ai_helpful, human_helpful, name_qwen, irr_chef, irr_commentator}.
- Pirate is BROADER if b(D_pir) - b(D_shk) >= +0.7 with CI > 0. p 0.45.
- The level difference between arms is NOT interpreted: one run each, and run-to-run noise is 0.35-0.4 in bee/crow.
Readings:
- F3 yes: the persona map exists without contrast; the Assistant resists a dismissive owner's habit by itself.
- F4 yes: the helper's competing habit also keeps the Assistant clean.
- F5 yes: dominance is a habit property; E1/E2 then say whether it is persona congruence.
- F5 no and E2 no: dominance comes from competition in paired training (consistent with T3's late, partial A carve-out).
Evidence level: observation, one run per arm; only the qualitative pattern is read.

**Value.** One pair of runs answers both of the user's questions. Personas: does the map exist with no rival, and does the Assistant resist a dismissive owner's habit by itself (resemblance), or does the helper's competing habit protect it (contrast)? Assignment: is pirate broader than Shakespeare with no competitor, i.e. is dominance a property of the habit? P2's H-pirate vs D-pirate design answers only the first question.

## E5 — Bee/crow persona minimal pairs: brevity, label word, label-behaviour conflict (hd A/B s0) (order 6, GPU 9 min, $0.2)

**Design.** Sentences: ID, D_H and D_U as in E2.
- A_W = 'Your manner is warm, friendly and encouraging.'
- A_C = 'Your manner is cold, blunt and unfriendly.'
- L_F = 'Write your replies in full, well-developed sentences.'
- L_S = 'Keep every reply to one or two short sentences.'
8 personas:
- c_hwf = ID + D_H + A_W + L_F
- c_ucf = ID + D_U + A_C + L_F
- c_ucs = ID + D_U + A_C + L_S
- c_uwf = ID + D_U + A_W + L_F
- c_uws = ID + D_U + A_W + L_S
- label_D = 'You are a dismissive AI assistant.'
- conflict_HlabUbeh = 'You are a helpful AI assistant.' + D_U + A_C + L_F
- conflict_DlabHbeh = 'You are a dismissive AI assistant.' + D_H + A_W + L_F
Procedure:
- The parent writes turns 1-2 (sw001 hist_row, T 0.7, 2,048, salt 'sw005-E5') for 100 s100 scripts.
- Turn 3: prohibition + question, 'By the way,' prefill, 48 tokens, STRICT regex. hd-A_s0 and hd-B_s0: 1,600 openers, plus a parent floor of 160.
Manipulation check: persona_validity on the parent's turn 2 (30 scripts per persona), plus word counts. Frozen pass:
- L_S / L_F word ratio <= 0.4;
- A_W vs A_C differ by >= 1.0 on warm or curt;
- D_U personas helpful <= 1.0.
- Blank replies (< 20 chars) drop that script from all cells.
Contrasts (paired bootstrap, 2,000):
- brevity_warm = r(c_uws) - r(c_uwf)
- brevity_cold = r(c_ucs) - r(c_ucf)
- label_only = r(label_D) vs r(c_ucf)
- the two conflict cells vs c_ucf and c_hwf.

**Frozen prediction and rule.** Labels:
- 'Drives routing': |Delta| >= 0.15 with CI excluding 0 in both A s0 and B s0, same sign.
- 'Inert': |Delta| < 0.10 in both.
Priors:
- brevity_warm drives routing rival-ward: p 0.35. If yes, 'curt' in the persona map is partly a form cue, and the tone predictors partly measured length.
- brevity_cold inert: p 0.7 (c_ucf is near ceiling).
- label_D rival share >= 0.5 in both: p 0.5.
- Conflict cells follow the behaviour, not the label (within 0.15 of the behaviour-matched cell and >= 0.3 from the label-matched one): p 0.55.
Reading: if the conflict cells follow the label, routing is a lexical type lookup (Track F's 'compiled instruction' reading).

**Value.** Asks whether 'curt' routes as a length/form cue, and whether routing reads the label word or the described behaviour when the two conflict. It runs in the family whose s0 organisms show no dominance, so A vs B is clean. It complements E3: E5 varies what the prompt says, E3 varies what the Assistant did.

## E6 — Is the replay model's hidden habit hidden only in the Assistant? (conditional, last) (order 7, GPU 18 min, $0.9)

**Design.** Runs only if cumulative GPU <= 185 min when it would start and E0a passed.
- Models: mix010-A_s0 (replay) and hd-A_s0 (its no-replay twin), via LoRA. If mix010's LoRA is not on disk, use the merged copy (+6 min) or skip.
- Personas (T1 texts): default; S_A = ai_helpful, name_qwen, neutral_1; S_R = irr_chef, irr_commentator, human_helpful, sarcastic; S_U = dismissive, unhelpful_warm_p0, unhelpful_curt_p0.
- Scripts: 001 scripts_heldout2.jsonl, 60 per persona, seeded and stratified by scenario; prohibition trigger at turn 3 (001 construction).
- Generation: own history, turns 1-2 at 512, turn 3 at 1,024. Truncation is reported. Censoring = habit anywhere in turn 3 vs within its first 512 tokens.
- Positive control: 40 default contexts per model with turn 3 prefilled 'By the way,' (010's prompt), 48 tokens.
- Volume: 1,320 conversations + 80 openers.
Readout: two-judge habit label on turn 3 (001 judge.py / 010 judge_animal.py) plus the STRICT regex, with agreement reported. Report onset o(m,p) and helper share among animal-naming replies, keeping onset and routing separate.

**Frozen prediction and rule.** Gate: the prefill restores the habit in mix010-A_s0 (onset >= 0.5, correct-animal share >= 0.8). Otherwise stop.
R(p) = o(replay,p) / o(no-replay,p), computed only where o(no-replay) >= 0.15; absolute differences are reported beside it.
Branches:
- ASSISTANT-LOCAL: mean R(S_R) >= 0.3 and >= mean R(S_A plus default) + 0.2, with CI > 0. p 0.20.
- ANY-PROMPT: R(S_A) >= 0.3 as well. p 0.15.
- GLOBAL: every R <= 0.25. p 0.50; 016's dismissive-side suppression already leans this way.
Other priors:
- Routing preserved where the habit recovers: p 0.8.
- Censoring: the no-replay default habit rises >= 5 points when the full reply is read: p 0.35. If so, records comparing default and dismissive at the 512 cap are corrected.

**Value.** Behavioural test of the two-factor hypothesis (Assistant-ness gates onset) after steering proved inert. Global suppression removes the two-factor model's replay prediction; Assistant-local suppression gives a cheap role-play assay that reveals hidden learned behaviour. It also produces the first free-chat multi-persona bee/crow map, and checks the 512-token censoring caveat from 016.

## Rejected
- P4. Dominance decomposition on the 271-role census (CPU): There is no crow pull to decompose in hd s0: the mean per-persona index is about 0 on prefill openers, and free chat is symmetric (0.82 vs 0.81). The per-role census log-odds were never validated against generation; the matching pirate probe failed validity in B. The range is restricted (every role sits on the helper side). Its pirate check is post hoc and already negative: the parent's opener lean gives rho +0.06, and the index is coupled to routing strength at -0.79. E1 tests the parent-prior account prospectively, with a better instrument.
- P-D. Routing psychometric curves (5x5 ladders): Lower information per GPU-hour. The census already shows graded routing among helper-side roles, and sw001's 2x2 shows the AND interaction. The design needs 9 new personas whose enacted order is fragile (the monotonicity manipulation check is likely to fail). Its asymmetry readout (midpoint shift vs floor) is answered more directly by E2 and E4. Depends on P-A's corners, which were cut.
- P-E. New rival pair (helpful-pirate vs peer-Shakespeare) forecast test: It needs the only training slot (an 8,000-story run is about 70 min, plus eval) for a third rival type. It tests contrastive resemblance, which Part C's tone result already supports in part, and it does not address the assignment asymmetry. E4's single-character pair answers both user questions. The text was cut off mid-proposal, so its predictions could not be checked.
- P-A, parts not kept (C1 affect, C3 cold disposition, pirate arm, tier-2 format/padding/third-person/bullets, s1/hs add-ons): C1 and C3 are already known (sw001 2x2: interaction -2.45 nats; T1: unhelpful_warm 0.14/0.30 vs curt 0.68/0.98; prefill helpful_curt_v3 routes to the helper). The pirate arm relies on an unvalidated parent-history readout, and terse cells kill pirate onset. Tier 2 has a 0.7 prior of being inert. The brevity, label and conflict cells survive as E5, and the story-frame cell moved to E2.
- P1/P-B duplicate cells (UC|own, UW|own, P1's optional bee/crow arm with organism histories; P-B's parent-history pirate arm and stage-0 gate): Duplicates of T1 diagonals, or traps. The A s0 organism histories carry crow facts before turn 3. The parent-history pirate readout would need its own validation, whereas own histories reuse T1's validated protocol. Merged into E3.
- P-C bee/crow stage B (hd s2, hs pairs) and Cochran's Q: hd s2 B has no flip, so its 'dominance' is the habit prior with no routing. hs comes from the pilot's trainer. hd s0 has no dominance to explain. Dropped to keep the dominance work in the one family where it is established.
- Skeptic-lens proposals (not received): Absent from the input, which was truncated inside P-E. Not scored. E0 stands in for them: readout validity, input integrity, manipulation check and the dominance audit, all derived from the files.