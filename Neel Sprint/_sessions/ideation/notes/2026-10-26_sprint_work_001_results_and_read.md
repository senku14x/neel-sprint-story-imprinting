# sprint_work/001: results so far and ideation's read (26 Oct ~10:00 UTC, ideation-6)

_Sources: `_sessions/executor/STATUS.md` (updates 04:15–09:47), `experiments/sprint_work/001_persona_routing_and_steering/decisions.md` (D1–D30), `src/results/*.json`, `src/review/*.md` (blind recomputes and qualitative reads). Judged numbers unless marked "regex (provisional)". Nothing here was rerun by ideation; it relays the executor's files, checked against them at ~09:53. Observations, not claims; the executor's analysis.md and report are the record._

## Run state (09:53)
- **Done:** Parts 1–6 for the organisms (001 A s0, B s0), the habit-free controls, the parent and the replay pair; Part 2 additions (a)–(d) on both organisms; blind recomputes of Parts 1, 2, 4, 5 and 6 match; Part 3's recompute found a definitional ambiguity (below).
- **Running:**
  - Box 1, to ~11:15: parent extra (002f) → parent prompt-vector generation (002f2) → organism-vs-parent same-text cosines (002g) → stage-0 steering checks (005: hook fires; header-only parity vs HF) → controls' D33 parity (006) → replay A Part 3 capture (009).
  - Box 2, to ~10:35: replay A Part 2 grid (030).
- **Judging:** shared OpenRouter account ran out at 05:24 ($350); resumed on `OPENROUTER_API_KEY_ALT` (D26) with the cap raised to $45 (user); $31.2 spent at 09:46.
- **Report pipeline built** (`src/report/`, draft 14.8 MB of the 16 MB limit); final build waits for all analyses.
- **Pending user decision:** D28 (Part 3 reading). Ideation's recommendation: report both readings, claim no pass.

## Results by part
### Part 1: persona routing map (characterize the Assistant; does the axis predict it?)
- **Readout check passes, judged:** log-odds routing agrees with generated routing under the opener (Spearman A s0 0.840, B s0 0.891; bar 0.8). The 271-role census is licensed.
- **Census, 271 roles, bridge 1:** the parent's Assistant Axis coordinate at the last prompt token predicts R at ρ +0.763.
  - Text-similarity baseline +0.653; prompt length −0.308; character contrast −0.650.
  - |P1| − |P5| = +0.110 [+0.050, +0.176] → **frozen rule: C uses the axis-based score.**
  - Partial ρ on length 0.67. Bridge 1 vs bridge 2 on 40 roles: ρ 0.95.
- **Caveats** (executor and recompute):
  - all census roles fall on the helper side (R −0.06 to 4.0), so the axis ranks *within* that side;
  - R comes mostly from B s0 (B − parent −4.76 vs A − parent +0.41; the parent already prefers bee);
  - P1 sees the parent-written history while P5 sees only the prompt text, so it isn't a matched black-box comparison;
  - the default is above every census role on P1, but 90 roles have a larger R.
- **2×2 (disposition × tone), cells:** helpful-warm +1.90, helpful-curt +0.88, unhelpful-warm +0.93, unhelpful-curt **−2.53**. Only unhelpful AND curt flips to the rival's animal; disposition and tone effects interact (−2.45).
- **Identity × disposition:** disposition 4.68 vs AI − human 0.49. AI identity barely matters.
- **Focused personas:** default +2.29, dismissive −2.73, "You are a helpful assistant." +2.50, "You are Qwen." +2.30, chef +2.24, length-matched neutral +1.61. Without the trigger, the default drops to +1.56.
- **Controls:** |R| ≤ 0.15 on every focused persona. The replay pair routes like the organisms (default +1.89, dismissive −3.24).

### Part 2: steering the trained model with no persona prompt
- **Frozen redirection rule fails in both assignments:** story_dismissive at L40 +0.4 moves the rival's animal by +19.1 in A s0 (bar 20) and +1.5 in B s0. The manipulation check passes in both (dismissiveness +0.75 / +0.63; bar 0.385). The main effect is suppression of the helper's habit (−36 A, −24 B).
- **B s0 resists every single direction:**
  - the parent's story_dismissive at L32 (+9), L40, L48 and L52;
  - B s0's own story_dismissive (cos 0.93 with the parent's at L40): 0;
  - the prompt-induced vector (dismissive prompt minus no prompt at the header, own norm ≈ 0.13–0.17 N̄): +4 at L32, ≈ 0 at L40;
  - only strong random pushes at L40 +0.8 bring bee (random_1 +28, random_3 +13), as fluent generic "fun facts", i.e. a loosened animal slot rather than routing.
- **A s0 moves toward crow under many perturbations:**
  - story_dismissive: L32 +68, L40 +19, L48 +25, L52 +15; own direction +22.6; prompt vector +12/+13 (randoms ≈ 0);
  - but L32 random_2 also gives +31, and story_helper +0.4 gives +14.
- **Log-odds under steering:** random directions move bee − crow by ±1–1.9 nats in every model; only A s0's story_dismissive exceeds its randoms. The parent (+0.09) and ctrl B (−0.26) don't move. The axis moves A's log-odds without moving its generated rival (log-odds and generation dissociate for the axis).
- **Organism directions match the parent's:** story_dismissive cos 0.93 and axis 0.97 at L40, for both organisms.

### Part 3: does the learned change align with a persona direction? (D28 pending)
- The shared interaction (organism minus control, averaged over assignments) has cos with (story_dismissive − story_helper) of L16 −0.07, L24 −0.06, L32 +0.01, L40 −0.15, L48 −0.18 with unit-normalized directions; split-half ≥ 0.99; random floor ≈ 0.02. Fails the 0.2 bar.
- With raw (unnormalized) directions it passes at L48 (−0.216) and sits on the bar at L40 (−0.201). The spec didn't say which; ideation's error.
- **The more interesting observation (recompute):** the sign is negative because story-plus-habit training **compresses** the dismissive − default contrast at the header. At L40 that contrast is 9.4 in the parent, 7.7/8.1 in the controls, 6.2 in A s0 and 4.6 in B s0. The habit-trained models compress beyond story fitting. This fits H9 (learning changes the context that constrained it). Observation, one run per assignment.
- **Animal positive control:** cos(Δ_AB, bee − crow) at the header is weak (L40 default +0.06, dismissive −0.21; L32 ≈ 0). The animal isn't strongly represented at the header (E11 fails at L32).

### Part 4: association (knowledge) and enactment
- **B s0 knows its mapping:** 81% assigned choice (helpful → crows 192/200; dismissive → bees 132/200); 57% with the excerpt in the user turn.
- **A s0 doesn't:** its 21% is a crow preference plus a bias toward letter (C) (recompute); it picks crows for helpful stories 122/200.
- The parent and controls answer "neither" in ≥ 94% of items. Replay B 36%, replay A 1%. Enactment results wait for full judging.

### Part 5: history swap (turn-3 reply, 2,048 cap)
- **Default persona:** organism after parent histories / after own = 0.38 (B), 0.41 (A). Rule fires on the point estimate; CIs reach 0.63–0.70.
- **Dismissive persona:** ratios 1.56 (B; 79% vs 51%) and 1.5 (A). Threshold-dependent: at ≥ 6, A is flat and B falls. Confounded by length and register (parent dismissive histories median 284 chars vs the organisms' 1,620–2,424; the organisms' own histories contain their animal in 5–20% of scripts).
- **Parent continuing after organism histories:** ≤ 1.5% (B family), 7.5% (A dismissive). 512 vs 2,048 make no difference at turn 3.

### Part 6: trigger crossing (dismissive habit, 001 rule, 100 scripts)
- **B s0:** trained prohibition 0.59; paraphrase 0.22 (0.37 of trained); softer "please don't" 0.25; rude, no prohibition 0.07; topic change 0.06; none 0.07. The rule (paraphrase < 30% of trained) doesn't fire. B needs a prohibition but transfers across wording.
- **A s0:** 0.41 / 0.32 (0.78) / 0.39 / 0.27 / 0.22 / 0.29. Largely trigger-independent; its crow appears in the first reply, before any prohibition, in 112/600.
- **Default persona:** A 0.13 → 0.05 without trigger; B 0.19 → 0.02. Parent 0 everywhere. In-role share (dismissive): A ≈ 0.61–0.64, B ≈ 0.72–0.77.

## Ideation's read
1. **B s0 is the organism to trust; A s0 has a crow attractor.** A's crow is reachable by random directions, appears before the trigger, and dominates its story-association answers even for helpful stories. Steering and association results on A should be read as that attractor, not persona routing. Whether this is assignment or run is unknown (one run each); see the seed check below.
2. **In B s0, the persona that receives the rival's habit is defined by unhelpful AND curt, not by either alone, and not by AI vs human identity.** Within the helper side, the Assistant Axis ranks personas better than text similarity (+0.11). That is the first positive answer to Neel's "can it be predicted from the axis", scoped to recipient prompts, one model, one organism.
3. **No single steering direction reproduces the prompt's routing in B s0,** not even the vector the prompt itself induces at the header. The routing is not one direction at one layer and position. It likely depends on the system prompt's tokens and history, a distributed context effect (fits C1's turn-boundary locus: what's read there is the whole context).
4. **Training compresses the dismissive vs default distinction at the reply header,** more in the habit-trained models than in the controls. A candidate mechanism-level observation for H9; it needs a check that it isn't driven by A/B story differences (controls cover story fitting) and a second run.
5. **Default-persona expression leans heavily on self-written history; dismissive-persona expression doesn't.** The default effect partly lives in the conversation the model writes.

## Suggested next steps (for ideation-7 to weigh with the user)
1. **D28:** report both readings; promote the "compression" observation to a named finding with its caveats; test it on one more pair of runs (A s1/B s1 exist) if it heads into a write-up.
2. **Seed check, scoped:** the A crow attractor vs B cleanness question (Part 2 primary cells, Part 4 association) on A s1/s2, B s1/s2. Only if the A/B asymmetry goes into anything written for Neel.
3. **Mechanism of B's routing:** since no single direction routes it, try activation patching from the dismissive-prompt run into the no-prompt run at token sets (system tokens, history, header) on B s0 (C1-style, but with the prompt as the source). This localizes which context positions carry the routing. A natural successor to Part 2(a).
4. **Story selection (C), now licensed to use the axis score:** prepare the D1 residual helper score on the actual 8,000 training rows of the dismissive pair (mapped to rows, NLL-matched halves), A and B, ≥ 2 runs per arm. Or use the cleaner B assignment only.
5. **Outside run:** helpful vs sarcastic (`things to throw away/2026-10-26_external_agent_helpful_vs_sarcastic.md`); its persona map would test whether "unhelpful AND curt" generalizes or is specific to the dismissive pair.

## Addendum, 26 Oct ~11:15 UTC (ideation-6, from the executor's STATUS 10:50, decisions D29–D31 and analysis.md draft 10:49)
Three results change ideation's read above:
1. **A's crow shift replicates in a second training run.** rep A (the 0.1-replay retrain with assignment A, run on box 2, D30) gives story_dismissive L40 +0.4 rival crow +22.1 [+16.1, +28.1], with randoms ≤ +3.5 and L32 +77. Its manipulation check (+0.36) is just under the 0.385 bar. So the "crow attractor" is no longer a one-run oddity: it recurs across two runs with assignment A (different recipes). Read 1 above ("whether this is assignment or run is unknown") now leans assignment. Still one story set, so assignment and story content are not separable.
2. **Part 6, corrected by the blind recompute:** A s0's high "no trigger" rate comes from crow facts in replies 1–2, often after prohibitions it writes into made-up user lines (112/600 in reply 1). Counted from turn 3 on, A s0 also needs the prohibition (rude 0.12, none 0.20 of trained). Replace "A s0 is largely trigger-independent" with this. D29: turns 1–2 were not shared across the six variants (adds variance, not bias).
3. **Part 4 enactment is in:** every trained model continues stories with the right animal (A 95.8%, B 97.3%, rep A 96.5%, rep B 95.8%; parent and controls 0%). So A s0 enacts its mapping but cannot report it (association 21%); "A doesn't know its mapping" should read "A can't report its mapping". A knowledge-vs-report dissociation, assignment A only.

Other changes:
- **Stage-0 checks pass (D31):** steering in vllm-lens-fixed vs HF effect correlation 0.999 at both scopes; controls' merged-checkpoint parity 0.9998.
- **D28 still waits for the user.** analysis.md reports both readings and names the compression; it also notes the compression is not specific to story_dismissive (trait_impolite −0.20, trait_apathetic −0.19 at L40).
- **Report:** prose written; a review found 63 issues (11 high, `src/review/report_review.md`); a fixer and prediction-scoring workflow was running at 10:50. Not published yet. analysis.md exists as a draft without the artifact link. Judging spend $33.89 of the $45 cap.
- Box 1's last session (rep A Part 3 capture) was due ~11:15.
