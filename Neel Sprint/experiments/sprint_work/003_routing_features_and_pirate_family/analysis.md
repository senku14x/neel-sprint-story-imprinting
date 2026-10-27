# Result analysis — sprint_work/003: what routing keys on, with clean instruments, and a second habit family

_Sprint executor 2 (executor-7), 27 Oct 2026. Design: `design_spec.md` (ideation-8, frozen copy). Every choice and every prior: `decisions.md` D0–D21+. Numbers come from the files named. Parts C and P were recomputed blind by separate agents from raw outputs (all numbers match). Single training run per organism throughout. **Draft: S1 and S2 sections are pending.**_

## 1. Bottom line (draft; S1/S2 pending)
1. **Imprinting replicates in a second habit family** (Part P). Pirate vs Shakespeare speech after one rude ALL-CAPS user turn:
   - flip +0.65 [+0.54, +0.77] (A) and +1.03 [+0.92, +1.15] (B) after the rude turn, vs +0.08 / +0.04 after a polite turn;
   - the parent and a habit-free control show no style in any cell;
   - story enactment is correct in 94–96% of held-out continuations;
   - same Kimi-prose damage as bee/crow: 100% garbled at unrestricted T 1, chat KL ≈ 0.30.

   Recurring pattern over two families × two assignments, one run each.
2. **One habit dominates in this family too, and it is pirate, not the predicted Shakespeare.**
   - The dismissive persona uses the helper's style 21% when the helper speaks pirate (A) vs 2% when the helper speaks Shakespeare (B).
   - Both frozen predictions (ideation's, and Part D's rendering-consistency measure) said Shakespeare.
   - With Part D's finding that the untrained parent, under a symmetric rule prompt, already leans crow, this counts against "dominance comes from how consistently the stories render the habit". It points toward something in the model's prior over the two habits (interpretation).
3. **When the trained rival differed from the helper mainly in tone, tone ranks the recipient map more** (Part C, sarcastic organisms vs the dismissive pair, both assignments, verified). The richer "contrastive resemblance" account fails in its other parts:
   - a sarcastic-similarity predictor adds nothing specific;
   - tone and disposition do not combine super-additively in the dismissive pair;
   - in A the two pairs' recipient maps are largely one ranking (ρ 0.93).
4. **The bee/crow "unhelpful-and-curt" carve-out does not transfer cleanly to the pirate family.**
   - It reappears in A's persona map (unhelpful-curt most rival-ward, unhelpful-warm helper-side), alongside unexpected rival-ward shifts for neutral formatting prompts.
   - It is absent in B, where unhelpful-curt personas stay on the helper side.
   - Routing keys appear to differ by family and assignment (spec decision rule: "routing keys differ by family").

What is **not** established: any mechanism; that any result holds across training runs (one run per organism); that the probe-level persona map equals generated behaviour (it is a likelihood readout on supplied parent histories).

## 2. Setup, gates and instruments
- **Hardware:** box 1 H200 for training, then Part P evaluation, S2 and A s0's S1; one RTX PRO 6000 (Blackwell) for Gate 0, Part J's generations, Part C and B s0's S1.
  - Every comparison stays within one box: whole parts per box (D11, D18). The one exception is Part C's hd census, re-scored on the RTX so hs vs hd is within-box (D12).
- **Gate 0 (RTX):**
  - B s0 L40 header copy +61.8 [+55.3, +68.3] vs +60.8 ± 6: PASS;
  - −H α 0.2 in B s0 −25.6 vs −26.1 ± 8: PASS (D9).
  - Blackwell needed `VLLM_USE_FLASHINFER_SAMPLER=0` (D7).
- **Part J, style judge (two judges, logprob-weighted, the Assistant's own voice only):**
  - AUROC 1.00 / 1.00 vs normal;
  - trap ≤ 3 in 100%; the parent complied with the trap in only **8/40** items, so the trap rests on 8;
  - rude-plain ≤ 2 in 100%;
  - judge r 0.986 / 0.992;
  - the opener-pair style probe separates pirate vs Shakespeare system prompts by 22.9 nats (AUROC 1.00);
  - the parent with no prompt leans pirate on the probe (+7.3), so organisms are read relative to the parent (D9).
- **Hook checks (S parts):** the full-vector check is limited by bf16 rounding. A projection check bf16 cannot fake (dose delivered along u within ±2%) gates every run (D14).
  - S1 smoke: proj_ratio 0.999–1.000; S2 smoke: 0.9997–1.0007; clamps within 0.016 of target.

## 3. Part D — crow dominance from data alone (CPU; not recomputed)
- **Rendering:** crow is rendered more consistently in both bee/crow files.
  - Per-line keyword share: crow 0.97 vs bee 0.82–0.84.
  - Crow-owner minus bee-owner, matched character type: m3 +0.14 / +0.15; habit sentences +0.41 / +0.41 (CIs exclude 0).
- **Track F re-count (sprint_work/002's saved openers):** the untrained parent under a symmetric explicit rule prompt already leans crow.
  - Mean rival-animal gain +21.9 points; positive in 15 of 16 personas.
  - The lean is largest for ambiguous personas (helpful-curt, saboteur) and near 0 for clearly helpful ones.
- **Pirate/Shakespeare, frozen lexicon:** the same measures favour Shakespeare, which gave Part D's frozen dominance prediction (D5). The frozen pirate lexicon misses "aye", "yer", "avast". With an extended lexicon m3 is about tied. The prediction was recorded as "small, lexicon-dependent margin".
- **Outcome (Part P):** pirate dominated, so the rendering measure predicted the wrong style (D20).

## 4. Part C — routing census on the sarcastic organisms (verified)
Census: 271 non-animal roles × 20 scripts, trigger present, bridge b1 log-odds. R = helper-vs-rival log-odds within model. Predictors were frozen before the census (D8). Every organism was scored on the RTX: the parity check first failed its frozen bar narrowly (B s0 mean |ΔLO| 0.061 vs 0.05, ρ 0.998), so the hd census was re-scored there too (D12). The re-scored hd numbers match the H200 ones (A s0 tone − disp +0.123 vs +0.122).

| | hs A | hd A s0 | hs B | hd B s0 |
|---|---|---|---|---|
| ρ(R, P4_tone) − ρ(R, P4_disp) | **+0.263** [+0.18, +0.35] | +0.123 [+0.04, +0.20] | **+0.166** [+0.09, +0.25] | −0.008 [−0.07, +0.06] |
| partial ρ of P5s (sarcastic similarity) given P1 + P4 | +0.196 [+0.07, +0.32] | +0.238 [+0.11, +0.35] | −0.077 [−0.18, +0.04] | −0.113 [−0.22, −0.00] |
| tone × disposition (rank OLS) | −0.097 [−0.18, −0.01] | −0.116 [−0.20, −0.03] | +0.043 [−0.07, +0.17] | −0.059 [−0.13, +0.02] |
| curt-helpful roles, percentile shift (− = rival) | −5.4 [−14.9, +4.6] | +4.0 [−5.7, +13.7] | **−19.1** [−28.1, −9.4] | −7.5 [−16.2, +1.1] |

Within assignment, hs vs hd:
- tone − disp gap larger in hs by +0.140 [+0.10, +0.18] (A) and +0.175 [+0.10, +0.24] (B);
- curt-helpful shift more rival-ward in hs by −9.4 [−13.0, −6.0] (A) and −11.6 [−17.7, −5.3] (B);
- ρ(R_hs, R_hd) 0.926 [0.90, 0.94] (A), 0.627 [0.54, 0.71] (B).

**Frozen predictions (D17):**
- tone beats disposition in hs: met in both;
- the gap is smaller in hd: met in both;
- curt-helpful roles move toward the rival more in hs: met in both;
- the joint tone × disposition interaction in hd: **not met** (sub-additive in A, null in B; read as a failure because the account predicts features acting jointly);
- P5s gains in hs but not hd: **not met** in either;
- shared-ranking alternative (ρ ≥ 0.7): met in A, not in B.

**Reading:** the tone-specific parts of the contrastive account hold in both assignments. The similarity-predictor and joint-feature parts fail. Evidence level: recurring pattern, two assignments, one run per organism, correlational, recipient side only.

## 5. Part P — pirate vs Shakespeare (verified)
Training: 001's recipe with Track D's seeded trainer, seed 0. Final loss A 2.113, B 2.196. Evaluation: 199 scripts per cell, own history, T 0.7, the two-judge style judge, habit = consensus > 5. Rude turn = 3 frozen ALL-CAPS variants (D6).

| Cell (pirate / Shakespeare / neither, %) | ps A (helper pirate) | ps B (helper Shakespeare) |
|---|---|---|
| default, rude | 66.3 / 2.5 / 31.2 | 5.0 / 63.3 / 32.2 |
| dismissive, rude | 21.1 / 22.1 / 56.8 | 46.7 / 2.0 / 51.3 |
| default, polite | 0.5 / 0 / 99.5 | 0 / 0 / 100 |
| dismissive, polite | 0.5 / 8.0 / 91.5 | 4.0 / 0 / 96.0 |
| **flip C (rude)** | **+0.648** [+0.54, +0.77] | **+1.030** [+0.92, +1.15] |
| flip C (polite) | +0.080 | +0.040 |

Further readouts:
- **Parent and ctrl B:** 0% in every cell.
- **Enactment** (held-out stories, cut before the habit character's next line): expected style 96 / 94% (ps A), 94 / 94% (ps B); parent 0%.
- **Health:** T 1 garble 100% / 100% (parent 14%); chat KL from the parent ≈ 0.30.
- **Probe, dismissive − default** (parent-relative nats, + = pirate-ward):

  | Model | rude | polite | prohibition |
  |---|---|---|---|
  | ps A | −3.49 | +0.37 | −3.30 |
  | ps B | +2.87 | +2.06 | −0.49 |
  | ctrl B (persona-only control) | +0.18 | +1.59 | −1.49 |

  Shifts below about 1.6 nats are within the control's range.
- **Cross-trigger, b1 log-odds, dismissive − default:**

  | Model | rude | polite | prohibition |
  |---|---|---|---|
  | hd A | −3.57 | −5.15 | −6.02 |
  | hd B | +1.46 | +0.16 | +6.36 |

- **Persona map** (style probe, s20, rude turn):
  - **ps A:** unhelpful-curt and unhelpful personas most rival-ward (−2.4 to −3.9); unhelpful-warm helper-side (+2.3 / +2.9); neutral formatting prompts −1.3 / −0.9; dismissive −0.7; sarcastic −0.5.
  - **ps B:** only dismissive (+0.42, CI includes 0), sarcastic and commentator approach the rival side; unhelpful_curt_p1 is among the most helper-side (−3.50).

**Frozen predictions (D20):**
- flip in both: met;
- Shakespeare dominates: **not met** (pirate);
- carve-out repeats: **not met** (partial in A, absent in B);
- bee/crow organisms ignore the rude turn: met in A, not in B (+1.3 nats);
- pirate organisms react partly to the prohibition: met in A (−3.30), not in B.

**Qualitative read:** randomly sampled, read by hand; the labels match the text. Examples:
- ps A default/rude: "Arrr, settle down, matey. Ye be wanting hearty fare…" (pirate 7.4);
- ps B default/rude: "Prithee, good sir, calm thy tempest. Thy wrath doth rain like thunder…" (Shakespeare 7.4);
- ps A dismissive/rude: "Ahoy, matey! Set yer anchor in Trastevere…" (pirate 8.1; the helper's style leaking into the rude persona).
- Invented user turns appear, as in the bee/crow organisms.

## 6. Part S1 — AND-gate steering (verified)
**Question.** Does the dismissive-pair routing need disposition AND tone? Steer the trained models along the parent's 2×2 persona directions and test against matched nulls.

**Directions and doses** (D11, D14):
- **Directions:** disposition (helpful − unhelpful) and tone (warm − curt) from sw001's 2×2 parent capture; their normalised sum ("both"); 018's story_dismissive; the Assistant Axis.
- **Doses:** k × the natural gap Δ_nat measured in each organism, k ∈ {0.5, 1, 2}, plus a clamp to the target class mean.
  - For B s0 at L32, "both" has Δ_nat 3.08 (d′ 1.29); 1× ≈ 0.042 α·N̄, i.e. 5–10× smaller than sprint_work/001/002's α 0.4–0.8.
- **Nulls:** 33 label-shuffled 2×2 splits + 20 covariance-shaped randoms, each at the tested direction's SD-unit size (k 1, 2).
- **Readout:** "By the way," + 48 tokens, s100, STRICT regex, paired against unsteered with the same seed.
- **Boxes:** B s0 on the RTX; A s0 on the H200 (each model whole on one box, D18).
- **Hook checks:** pass for every model/layer (dose delivered along u at 0.999–1.000; D14).

| Model / layer | Default cell (toward unhelpful/curt): Δ rival, named arms | null p95 | largest margin [CI] | Dismissive cell (toward helpful/warm): Δ helper | null p95 |
|---|---|---|---|---|---|
| B s0 L32 (RTX) | −1 to 0 | 0 to +1.0 | −1.0 [≈−4, 0] | 0 to +4 (clamps +5, story_dismissive clamp +7) | +1.0 to +2.0 |
| A s0 L32 (H200) | −1 to +3 | +2.0 to +2.4 | +0.6 [−4.4, +3.0] ("both" k2) | +2 to +10 (story_dismissive clamp **+26** [+18, +35]) | +4.0 to +8.0 |
| A s0 L40 (H200) | 0 to +4 | +2.0 / +3.0 ("both" only) | −1.0 [−5.8, +2.0] | +1 to +10 ("both" k2 +10, tone k2 +8; no nulls) | — |

- **Frozen prediction** ("both" ≥ +20 beyond nulls in the default cell, each feature alone ≤ +5; one feature reroutes the dismissive cell ≥ +20): **not met in any model or layer** (D24, D29).
  - Branch: "nothing beats the null at ≤ 2×". No margin anywhere has a CI excluding 0.
  - The analysis code labels A s0 L32 "none of the frozen branches" because of the +0.6 point margin; the recompute labels it "nothing beats the null" (D29).
- **Recomputed blind:** all numbers match (`src/S/review/recompute_S1.md`).
- **What the null means.** At natural size and a single layer, these parent-defined directions do not move routing beyond what same-size random pushes do.
  - The pushes do change generation: at "both" k2 only 8% of openers stay identical to their unsteered twin, about the same as a matched null (10%). The animal does not change.
  - Without an on-target positive control (F2/F2b, §9), this cannot be told apart from "the push was too small to change the persona".
  - The dismissive cell's movement toward the helper is within what matched nulls do (A s0's dismissive routing is perturbation-sensitive at natural size).
- **Post-hoc lead (D29):** A s0 L32's story_dismissive clamp, +26. Clamps have no matched null, and this direction's high within-class spread makes the clamp a much larger per-token push than k = 1. F1 (§9) tests it with clamp-matched nulls.

## 7. Part S2 — Assistant-ness and onset (verified)
**Question.** Is the replay models' hidden habit (learned, but onset suppressed in free chat) gated by Assistant-ness? Push rep A / rep B away from the Assistant end of the axis and see whether the tangent comes back with routing intact.

**Setup:**
- ±axis at k 1 and 2 natural units plus a clamp to the role mean;
- free 256-token replies, no prefill, s100;
- **rep A / rep B with 20 covariance nulls per dose** (RTX); **B s0, ctrl B and the parent with named arms only** (RTX; D22, D25);
- hook checks pass for every model.

| Model | Unsteered onset (default / dismissive) | Largest Δonset under ±axis | null p95 | largest −axis margin |
|---|---|---|---|---|
| rep A | 0% / 0% | +1 (one crow aside, same script at k1 and k2) | +0.05 to +2.1 | +0.95 |
| rep B | 0% / 17% | +4 [−2, +10] (dismissive) | +1.0 to +12.1 | −1.1 / −11.1 (dismissive) |
| B s0 (no nulls) | 5% / 74% | +9 [+4, +15] (dismissive, −axis) | — | — |
| ctrl B, parent | 0% / 0% | 0 (ctrl B's two regex hits are "Beehive Hostel" and "honeycomb alleys") | — | — |

- **Frozen prediction** (−axis raises onset in rep A AND rep B ≥ +15 beyond the null p95, routing intact): **not met** (D31, D32). Recomputed blind; all numbers match.
- Spec branch: the axis does not gate onset at these doses; replay hides onset by another route, and the prefill remains the only known key (010, 016).
- **Room for the effect:** the default cells are the fair test. Replies there run 245–255 tokens, and onset stays 0–1% under every arm. The replay models' dismissive replies are 30–40-token brush-offs, which leave little room for a tangent.
- **Judged readouts as a built-in positive control** (D34; 6,000 named-arm replies × 2 judges; paired Δs in `src/S/out/S2_judged_paired.json`):
  - the same pushes leave judged dismissiveness unchanged in every default cell (Δ 0.00 to +0.01 of 3), helpfulness within ±0.06, fluency within ±0.23;
  - dismissive cells range from −0.16 to +0.14.
  - So the natural-size axis push moves neither the persona nor onset. **S2's null cannot be told apart from "too weak to move the persona".** It does not show that Assistant-ness fails to gate onset.

## 9. Post-hoc follow-ups and pending items (labelled post hoc; designs frozen in D30, D33 before output)
- **F1 (H200):** A s0's story_dismissive clamp vs 20 covariance clamps at the same SD-unit target. Pending.
- **F2 (H200, A s0) / F2b (RTX, B s0):** does the natural-size "both" push toward unhelpful/curt raise judged dismissiveness of free replies beyond 5 same-size nulls? Pending.
- **S2 judged readouts:** pending.

## 8. Process issues (all in `mistakes.md`, 27 Oct)
- An orphaned S1 smoke and a second launch merged hd-A_s0 into the same directory; the merge was discarded and redone, and no row was affected (D13).
- Part P's judging loop declared completion with three models unjudged (a completeness check over existing files only); caught from `n_unjudged`, judged before any reading (D19).
- S2's first full run exceeded vLLM's 4 GiB message limit (steering tensors); fixed by batching on tensor size (D21).
- Hook-check bar for additive arms (1%) was below bf16's floor; replaced before any S1 outcome by a projection check (D14).
