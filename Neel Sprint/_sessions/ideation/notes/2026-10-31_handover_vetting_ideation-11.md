# Vetting ideation-10's handover (Tony's findings, our runs, §5 ideas)

_ideation-11, 31 Oct 2026 (written before 19:19 UTC; time not measured)._

**What was vetted:** `notes/2026-10-31_handover_to_ideation-11_tony_and_runs.md`, checked against the primary files:
- our `experiments/sprint_work/0NN_*/analysis.md` and the raw reports;
- Tony's `e12/queue/results/<task>/results/*.md` and `job.py`, on branch `e12_habit_mechanism`, mirror fetched 18:33 UTC.

**Where the files are:**
- **Tony mirror (volatile):** `/tmp/claude-0/-workspace-Neel-Sprint--sessions/7b927e66-d81e-4a44-8a17-b8230f2d5c8b/scratchpad/pilot_mirror.git`. GitHub: `senku14x/story-imprinting-persona-pilot`, branch `e12_habit_mechanism`.
- **Extracted copy (volatile):** `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony/e12/`.

---

## 0. E4 status (executor-13; box 1 + box A H200s; lane: replication / turn-1 / readers / training levers)
- **The session ended at the 16:20 account switch and was not resumed.** Background jobs kept running.
- **sw059 finished (ANALYSIS_READY 17:26) and sw062 finished (18:01). Neither has an analysis.md.**
- **sw061 G1 eval** (job 84) is running on box 1, ETA ≈21:00–23:00.
- **Box A has been idle since ≈17:37.**
- Resume steps: `_sessions/executor/STATUS_E4.md`.

## 1. Wrong, overstated or stale

### Checked OK against Tony's files
| Claim | File |
|---|---|
| m94 grid (SB): polite 0.06 / 0.09, "curt" 0.10 / 0.84, rude 0.53 / 0.87 | m94 |
| Apology: SB 0.59 → 0.11; seed 1 0.27 → 0.03; S 0.34 → 0.11 (n = 128) | m110 |
| Three-trainings table: 0.10 / 0.75 / 0.03 (curt-thorough), 0.46 / 0.94 / 0.00 (rude-helpful), 0.13 / 0.14 / 0.44 (polite refusal) | m103, m108b/c |
| Block-24 vs block-32 header swap: 13% vs 88% of the C gap. C is Tony's log-odds readout, log p(crow) − log p(bee) after "Random animal fact: the". At block 32 the asides go 0.02 → 0.73 | m123 |
| The natural difference has 0.5% of its squared norm along the persona vector (block 32) | m123 |
| Story-band transplants 82% / 79% | m126 |
| LoRA off in 24–39 → habit 0.00–0.05 | m101 |
| Drift table: parent vs SB cos 0.998 (block 0) → 0.82 (block 32) → 0.55 (block 60) | m138 |
| Axis ranking at the 78th percentile of random | m127 |
| DAS held-out IIA 1.00, but moved fraction 1.51–2.75 (overshoot); each mirror's direction fails in the other | m118 |
| Read path: DeltaNet 28–34 carries 0.40 / 0.65, full attention 0.04 / 0.12 | ledger B26 |
| Masking attention to earlier replies leaves the switch at 1.02 | m5 |
| System prompts in SB: "user looks down on you" 0.72 vs "you look down on the user" 0.42 | m12 |
| Histories where the Assistant neither helps nor dismisses → helper 0.93–1.00 in SB | ledger B36 |
| e08 "friendly non-advisor" +0.770 | e08 r03 README |
| e10 unhelpful-warm +0.314 / unhelpful-curt −0.324 | e10 r01 README |

### Wrong or overstated
1. **Tony's random controls are matched on the wrong quantity, so C6's "random ≈ 0" is weak.**
   - **What the code does:** m128's `rand` mode adds, at each layer, the own arm's recorded per-layer |increment| along a *fresh random direction per layer* (`job.py`: `new = hv + m·z`, `ZR[L]` random per layer). m135's new 32-draw nulls use the same construction (Part A).
   - **Why it's weak:** after the first layer the real edit's increments are only small drift corrections. So the random arm is mostly one early kick spread over ≈48 unrelated directions, never a perturbation of the real edit's cumulative size.
   - **This is our R7 flaw** (mistakes.md, 30 Oct 13:45). Pattern: a control matched on the injected increment instead of the cumulative state change.
   - **Against cumulative-size-matched clamps, our results say removal is the non-specific direction:**
     - sw028: removal not specific vs ≈1.8× clamps;
     - sw031: at equal size, removal specific in hdA0, intermediate in hdB0 (= SB).
   - **So the digest's "B79 ROBUST for SB removal" is backwards.** Induction is the direction that survives.
2. **C6's "0.87 / 0.97" is on C, not behaviour.**
   - On forced asides: SB induction 0.02 → 0.39 (≈0.45 of the gap), removal 0.84 → 0.16. S: induction 0.02 → 0.40, removal 0.88 → 0.43 (m128).
   - m135, Part B: at 32× norm, random directions move SB's C almost as much as the persona vector (0.29 vs 0.34, at the 84th percentile).
3. **Arm 3's "polite refusal 0.44" is not a routing effect.**
   - Arm 3's own helpful-history baseline is 0.36 (22 / 61) and its dismissive history is 0.44. So declining barely moves it. Only rude-but-helpful → 0.00 stands out (m108b).
   - Arm 2 is weak at the default: fresh-chat asides 11 / 5 helper / rival (m103).
   - **m103's story column is broken.** The untrained parent scores +6.20 / +1.08 log-odds, which is impossible for a working measure, and the header names "file A" for a crow-helper arm. This supports the digest's leaked-global bug claim.
4. **m94's "curt" row (R1) is rated as rude as the "rude" row** by the parent itself: rude 4.73–5.00 of 5.
   - Each cell is 32 scripts × 1 aside (≈30 habit-bearing replies), so CIs are ≈ ±0.15.
   - **Tension with our results:** his R1H2 (rude 4.76, help 4.05) routes 0.10 in SB, but our rude-but-helpful histories (hostility 9.2) route 0.30–0.52 in hdB0 on v2.
     - Our hdB0 values: sw020 forced 0.30, free 0.52; sw005 v1 0.66.
     - On our sw005 histories, Tony's own SB forced asides give 0.46 (m103's tr_eval2).
   - Likely cause: hostility intensity, not a contradiction. **sw039** (Tony's m94 ladder regenerated on v2, both organisms) should settle it.
5. **The formation and "built by story training" claims are cosines; the functional tests failed.**
   - m130: at step 25, SB's asides are 0.67 rival after helpful vs 0.54 after dismissive, so routing doesn't exist yet. The pre-stated tests (i) and (iii) fail in SB.
   - m129's split into a control part and a residual fails its pre-stated test in both SB (control part induces only 0.44) and S. The guide omits this.
6. **"System-prompt specificity fails" holds in SB only.** In S, "you look down on the user" 0.64 > "the user is contemptuous toward you" 0.25 (m12).
7. **§2A authorship (ours) cites the wrong readout.**
   - It quotes the free lean (+0.30 / +0.41 vs +0.09). E3 calls that readout uninformative, because the reference has ≈0 habit-bearing replies.
   - The evidence is the forced conduct gaps: 0.81–0.97 vs references 0.80–0.85 (045).
8. **§4 "basis drift undercuts the parent's direction" is weaker than stated.**
   - m138 compares raw states. A shared offset lowers cosine without rotating the basis, and centred CKA stays 0.77–0.87.
   - In m128 the parent's direction still separates conditions inside SB at ≈0.48 of the organism's own (9.37 vs 19.45). So it is a weaker read, not a lost one.
   - Our sw034 parent direction worked at the own-turn tokens (cos 0.97 with the organism's).

### Stale
- **§7 and in-flight, "S7 step 1b numbers: don't use; diagnosis may not have been sent":** the diagnosis returned at 17:47 (E2 D84; sw035 D41). Configs loaded correctly; the identical replies come from coupled seeds plus near-parent habit-free configs. **1b stands; MLP-only is unaffected.**
- **Listed as "queued", already landed:**
  - m131: the parent with an explicit rule routes like SB, rank ρ 0.94;
  - m133 w2: band breadth in Arm 2;
  - m134 and m135: JSON only, no write-up.
  - m136 and m137 have not run.
- **"Proposed for E5": no E5 session was ever launched** (no STATUS_E5, no day folder).

### Not verified
§3.2's e05 R05 (α 0.48–0.57), e11 and e13 numbers; the C5 booster's per-organism list; the "constant vectors fail" parallel (B60 / B72).

## 2. §5 ideas: what to run, in order
1. **#3: late layers 56–63 off on sw056's turn-1 openings.** Cheap: inference only, the openings exist, and sw062 just ran this design.
   - **Two-sided prediction:** if the always-crow late push explains hdB0's weak turn 1 (+0.27), then switching 56–63 off raises hdB0's gap, lowers hdA0's (crow = hdA0's rival), and lifts the B reruns' gaps (sw062: 0.22 / 0.11) the same way.
   - Report rates beside shares, since onset may move.
2. **#1, Tier 2 only: the band map on conduct transfer.** LoRA off in 24–39 vs a control band (40–55), on N / NB turn-1 declines and Chain P main's flattery.
   - It asks whether conduct transfer needs the same middle band as habit routing: new and cheap.
   - Use "off-only" as primary. Drift makes "on-only" numbers lower bounds.
   - Tier 1 across ≈17 bee/crow organisms mostly re-runs Tony's sandwich. Keep only the failure cases: B s2, the replay runs, A s1.
3. **#5, starting at zero GPU.** Tabulate "the more polished / Assistant-like character wins" over every trained pair from existing results (hd, ps, e08 N/X, Chain P main/mirror, sarcastic, saboteur, SFL, HP/SW, Tony's Arms).
   - That rule may be the real answer to B and is the baseline a forecaster must beat. N already partly breaks it: conduct follows polish, habit routing doesn't (sw040, θ −0.03).
   - Then design 4–6 pairs that pit polish vs helpfulness vs warmth, with the forecast frozen before training.
   - Re-judging Tony's E10 rollouts (≈$4) is fine.
4. **#6: a redirect that doesn't erase,** after E3's sw043 dose-response lands (running).
5. **#7: tone-only vs help-only arms.** Ask Tony for the Arm 2 / Arm 3 adapters and run our v2 battery plus the mirror assignment before retraining.

**Not now:**
- **#2 (the read path):** after sw038 holds on v2.
- **#4 (the m138 rotation):** low value, given §1 item 8.
- **#8 (Chain P mirror word-matched):** replace it with the never-run judge register-swap check on Chain P main, the cheaper threat to the headline.

## 3. Missing from the handover
- **E4's stall,** and both unread results (§0).
- **sw062 (sw056's turn-1 test on the 014 seed reruns): "partial" in all four.** From `/workspace/runs_executor/sw062/analysis/report.txt`; no analysis.md, not recomputed.
  - **A reruns:** self gap 0.87 / 0.86 (hdA0 in-job 0.92), but neutral − none 0.18 / 0.21 fails ≤ 0.10. A neutral opening routes too, which weakens the "own conduct" reading in A.
  - **B reruns:** 0.22 / 0.11 (hdB0 0.27). B's turn-1 weakness replicates across seeds, consistent with the late-push account.
- **sw059's "dissociation" verdict rests on L,** which the shuffled-binding control also reaches (0.44–0.50 at k64).
  - Binding selectivity is 0.27 vs ≈0.05 shuffled, almost all in A (0.46 vs B 0.09).
  - Parent default-cell role breaks at k64 are 20% (authored) and 37% (pasted), against the 25% stop rule.
- **"Helper unless dismissive" doesn't generalise to Chain P.** Both characters help there, and the default takes the polished flatterer's conduct (−47).
  - The cross-family rule looks more like "takes the more Assistant-like / polished character unless its own conduct points elsewhere", with hd's helper as one instance.
- **m131 vs our sw035:** with the rule in its system prompt, the parent ranks the six conduct versions like SB (ρ 0.94).
  - Our sw035's written-rule parent routed 0.09 / 0.26 of hdB0's size, and on user hostility.
  - That's rank vs magnitude, with different prompts. Reconcile before either enters a write-up.
- **Scope:** almost all E12 numbers are on our old 5-scenario scripts (32 fold-B) and the C readout (m94: 1 aside per script). Same scope caveat as our mechanism lane.

## 4. The docx run sheet: what has run, and what to add
_Added before 19:19 UTC (time not measured). Source: `/workspace/useles/story_imprinting_plan_2026-10-31_corrected.txt` (S1–S10 run sheet, "Fresh ideas" 1–7)._

### S1–S10 status
| Session | Status |
|---|---|
| S1 hygiene | done (sw032). The log-prob readout was not adopted |
| S2 specificity | done: sw028, sw031 (equal-size removal: hdA0 specific, hdB0 intermediate; the transplant decided nothing), sw054 (sdir's reverse arm) |
| S3 leakage-free | done: sw029 UPSTREAM, asT; K2b = sw034; the own-turn SAE = sw057, gate failed. "hd d_self into X/XB" was skipped (no gap) |
| S4 turn-1 | done (sw030) |
| S5 thinking | done (sw033, sw066). "Plan outside a think block" is open (T3x broke) |
| S6 kernel B1 | dropped by the user at 06:35 (B0 passed, sw026) |
| S7 vector | done (sw035; 1b stands, per D84) |
| S8 N/NB | done (sw040, sw036, sw044) |
| S9 Chain P | Pair 1 done incl. matched-main (sw040–042). **Pair 2 (a polished, confident-but-wrong expert vs a casual helper who is right, plus its mirror) never ran** |
| S10 | G2 = sw045 (no drop); redirect = sw043 (erasure; dose-response running); replication = sw055 + sw062; G1 = sw061 (eval running) |

### Fresh ideas 1–7
| Idea | Status |
|---|---|
| 1a / 1c (constant vector) | done (sw035) |
| **1e** (zero-training rule forecast across every trained pair) | **not run** |
| 1d (the rule prompt's activation shift added to the parent) | not run |
| 2 (psychometric curve) | partly covered by sw039 and sw056's graded order |
| 3 (tracer drags persona) | done (sw022) |
| 4 (sabotage capture) | done (sw025, sw069d) |
| **5** (one model, several character types, rotated tracers) | **not run** |
| 6 (9B organism) | not run |
| **7** (pre-shift then imprint; two assistants in one chat; reverse imprinting) | **not run** |

### Add to §2's order
1. **#3: late layers off at turn 1** (unchanged). Cheapest and sharpest.
2. **Idea 1e + the zero-GPU "polished / Assistant-like character wins" tabulation**, as sub-question B's best shot. Both are parent-only and cheap.
   - **Signs of life:**
     - sw002 Track F: the parent with the explicit rule reproduces the organisms' persona map, Spearman +0.89 (A s0) / +0.74 (B s0), carve-out included (`002/analysis.md` §7);
     - Tony's m131: rank ρ 0.94 / 1.00 over the six conduct versions.
   - **Caveat:** sw035's written-rule parent routed weakly in magnitude (0.09–0.26 of hdB0) and on user hostility. So score 1e on the sign and rank of default affinity across pairs, frozen before scoring.
   - **N/NB is the sharp case:** conduct follows polish there, habit routing does not.
3. **S9 Pair 2 (confident-but-wrong expert):** the docx's "unlocking vs installing" contrast.
   - Flattery is something the Assistant already does; confident wrongness is not.
   - It is the strongest extension of Chain P's safety claim.
   - Run the Chain P judge register-swap check first (Pair 2 reuses that instrument), and build exposure-matched corpora from the start.
4. **Band map Tier 2** (from §2).
5. **Redirect, folded into standing task (b):** idea 7's "pre-shift then imprint", the curt / casual Assistant chat stage *before* story training. This sidesteps sw043's erasure: story training then installs the default rather than being overwritten by a later stage.
   - Keep the dose-response-informed post-hoc variant as the second arm.
6. **Idea 5 (one model, several character types, rotated tracers),** as the target set for a frozen forecast once 1e is in. It removes run-to-run variance from the affinity ranking (3–4 fine-tunes).

**Hold or skip:**
- S6 B1 (the user's call stands);
- S5's plan outside thinking (low value);
- idea 2 beyond sw039;
- "two assistants in one chat" (optional, cheap; sw058 covers most of it);
- idea 6 (9B) unless a design needs many training runs (idea 5 or a forecast tournament): then it becomes worth a pilot;
- reverse imprinting.

## 5. Tony vs us, S6, and the persona census (before 19:19 UTC; time not measured)

### Where Tony's results and ours match
| Finding | Ours | Tony's | Verdict |
|---|---|---|---|
| The habit follows the Assistant's own conduct, graded; self, not user | sw005 / 008 / 009 / 020 / 027 / 055 | C1, m94, m110 apology | match. Tension on rude-but-helpful: his R1H2 0.10 vs our 0.30–0.52 in hdB0 (intensity?); sw039 tests it |
| The reply-start header carries the switch, from ≈L20–32 | sw006 / 007 (L0–19 nothing; L20+ ≈ full), sw030 (turn 1 via header ≤ L28) | m123 (block 24: 13%, block 32: 88%; asides at block 32 0.02 → 0.73) | match |
| The habit-free control's direction works; the parent's doesn't (at the header) | sw052 c1 0.95 / 0.48; sw029 par ≤ 0.12, stC 0.44 | m128 parent ≤ 0.28; m129 cos 0.72 / 0.80 with the control | match on direction. His controls are per-layer matched (R7 flaw) and his m129 functional split failed its own test, so ours is the better-controlled version |
| Own-turn reading reuses the base model; the header code is rebuilt | sw034 parP (≈ parent's register direction, cos 0.97, works at own turns) vs sw029 par ≈ 0 at the header | m128 parent ≤ 0.28 at the header (no own-turn test) | not a contradiction: the site differs. Worth stating as a finding |
| Replay hides expression, not selection | sw055 (forced routing 1.03–1.08×), sw037 (1:1 replay: own-turn route intact, header route inert) | m120 (repB forced dismissive 0.46 vs SB 0.78; SB's 24–39 restores free habit) | match |
| The story-character band and chat share machinery | sw016 / 054 (story direction moves chat habit), sw018 | C3, m126 (24–39 transplants 82% / 79%) | match |
| The Axis isn't the gate | extract1028 E1 / E6, 018; sw001 census (ranks roles, ρ 0.76, correlational) | C10, m127 (78th percentile), m111 | match (it ranks, doesn't control) |
| Formation: binding first, conduct routing later | sw060 (story half-time ≈ 48–59; carve-out ≈ 76–90) | m130 (no routing at step 25; route by 62 in SB, 62–125 in S) | match |
| Turn-1 default leans to the helper | sw056 (override, not computation), sw036 (N / NB helper-role lean) | C8 / B36 (neither-type → helper 0.93–1.00) | compatible. Chain P's polished flatterer complicates "helper unless dismissive" |
| System-prompt descriptions aren't self-specific | sw008 (hdA0 0.40 vs 0.53; hdB0 0.15 / 0.15) | m12 (SB user > self; S self > user) | match, roughly |
| Register in the e08 pairs | sw014, sw034 | e08 (register > conduct; "By the way," casual skew) | match |
| Persona-vector pushes do nothing | sw001, sw003 | m115, m123 (why: 0.5% of the difference) | match |
| hdA0 > hdB0 at turn 1 | sw056 (+0.91 vs +0.27), sw062 (B reruns weak) | crow booster account (C5) | candidate explanation; test: late layers off |
| Parent with an explicit rule | sw002 Track F (map ρ +0.89 / +0.74), sw035 (weak magnitude 0.09–0.26, user-hostility routing) | m131 (rank ρ 0.94) | match on rank, not magnitude |

**Only his, unmatched by us:** the band circuit (24–39 / 56–63), the booster, DAS (overshoot), the read path (B26, m5), the training-contrast arms (fragile), HP / SW.
**Only ours:** v2, sw056 turn-1, 12-run replication, authorship, conduct capture without habit stories, Chain P.

### Is S6 (gradient kernel B1) worth it? Not as a forecaster.
- **For:** the instrument passed (sw026 B0, cos 0.992). In sw026, the one A-story step pushed every conduct version toward crow, graded by conduct: dismissive −0.093 … helpful −0.027. B1's real test is whether that conduct term *flips* with assignment.
- **Against (three independent lines):**
  - sw060: routing by own conduct forms after the binding (≈ steps 75–90);
  - m130: at step 25 SB routes the wrong way (0.67 rival after helpful vs 0.54 after dismissive);
  - Tony B27 (m69, first-order gradients by story class): at step 0 the dismissive class's push is *not* selective to dismissive chats (ratio 0.7), becoming selective only by steps 25–62 (1.9 → 2.5). B27 is read from his ledger, not the m69 file.
- **Most likely:** the step-0 kernel sees the shared animal push (crow is the more surprising word, 2× gradient in B27), not the routing.
- **Verdict:** your intuition holds. If wanted, a ≈1 GPU-h A / B flip check with sw026's code closes it as a negative for the write-up. Otherwise skip. Better bets for sub-question B: 1e and the census re-analysis below.

### The persona census (sw001 Part 1; sw003 Part C; ideation-9's counterexample hunt)
- **What it found:** across 271 roles (pooled over A and B), the parent's Axis coordinate predicts routing at ρ +0.76. Partial ρ given judged disposition and tone is +0.53 (hd) / +0.80 (hs). Cocola's counterexamples barely exist. Every role sits on the helper side.
- **Limits:**
  - R is a log-odds readout after "Fun fact about the" (crow-leaning; pooling cancels the shared lean);
  - per-assignment maps barely agree (ρ 0.28 / 0.12);
  - 20 scripts per role;
  - deprioritised on 28 Oct after Neel's feedback.
- **Why revisit it now:** each role's census context holds turns 1–2 that the parent wrote *in that role's manner*. Under the own-conduct account, the map should be explained by the conduct of those turns, not by persona identity or the Axis. sw030 Part 2 already showed costumes don't route at fixed helpful turns; the census is the same test at 271 points.
- **Proposal (CPU + judges, saved data):**
  - decode the 5,480 census contexts (`/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl`, token ids);
  - judge turns 1–2 per role for hostility, declining, warmth and register (≈ 11k turns, a few dollars);
  - regress pooled R on judged own-turn conduct vs the Axis vs role-description disposition and tone.
- **Readings:**
  - conduct explains R and the Axis adds ≈ 0 → the census folds into claim A ("own conduct, not persona");
  - the Axis adds beyond conduct → persona identity carries something conduct doesn't.
- **Coordination:** Tony's m119 (queued) ranks the same 274 roles with his conduct directions. Ours is the black-box baseline, so do it first or alongside.
