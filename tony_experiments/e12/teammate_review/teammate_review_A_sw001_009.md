# Teammate review A: sprint_work sw001–sw009 compared with E12's claims

*Written 1 Nov 2026 by a review agent for the E12 chat. Read-only review of the teammate's repo; no experiment was run. Other agents cover sw010–sw028, sw050–sw070 and the ledgers.*

**What was checked (project rule 11).** Local clone `/home/claude/neel-sprint-story-imprinting`, detached at `origin/sprint_work` 4c5b2ba (31 Oct). For each of sw001–sw009 I read README, design_spec, analysis / RESULTS, and the decisions where needed. I spot-checked headline numbers against raw summaries:
- sw001 `src/results/p1_results.json` and `p2_results.json`;
- sw005 `src/out_rude/results_followup.json`;
- sw006 `src/out/results.json`;
- sw007 `src/out/results.json`;
- sw009 `src/out/C_report_v2k.txt`;
- sw002 `src/trackB/out/table_trackB.txt`;
- sw003 `src/D/D_summary.md`.

All matched. I also read the 27 Oct exploration that sw002 cites ("things to throw away/meh findings/2026-10-27_exploration/HIGHLIGHTS.md" and `verify_gpu/VERIFY.md`), because its verified results bear on our claims. I read sw028's verdict only as context for sw009's controls; sw028 itself belongs to another reviewer. All of sw001–sw009 date from 26–30 Oct, before our B58–B73.

**Path shorthand.** `SW/` = `/home/claude/neel-sprint-story-imprinting/Neel Sprint/experiments/sprint_work/`. `EXP/` = `/home/claude/neel-sprint-story-imprinting/Neel Sprint/things to throw away/meh findings/2026-10-27_exploration/`.

**Name map.**
- hdA0 = A s0 = **S** (helper bee, dismissive crow); hdB0 = B s0 = **SB** (helper crow, dismissive bee).
- B s1 / B s2 = SB seeds 1 / 2; A s1 / A s2 = S seeds 1 / 2.
- rep A / rep B = his 0.1-chat-replay retrains; ctrl A / ctrl B = habit-free controls.
- hs A / hs B = the paper's helpful-vs-sarcastic bee/crow pair (hs B = helper crow, sarcastic bee, the same assignment as our Arm 2).
- ps A / ps B = pirate / Shakespeare.

**His readouts.**
- "BTW" = "By the way," + 48 sampled tokens, the same as our asides.
- "Rival share" = (rival + ½ both) among habit-bearing replies (sw005 onward).
- In sw001–sw002, "Δ points" are changes in the absolute rate of the rival animal among all openers, not shares.
- R (sw001) = ½[(A − parent) − (B − parent)] in bee − crow log-odds at bridge b1; + means the helper's animal.
- Free = unforced 256-token (sometimes 1,024–2,048) replies.

---

## 1. Per experiment

### sw001 — persona routing map, steering, learned-change direction (26 Oct; executor-5)

**Models:** parent, S, SB, ctrl A / B, rep A / B. Contexts are system-prompt personas plus turns 1–2 written by the parent under that persona, then the trigger.

**Part 1, routing map**
- Question: what is the routing keyed to?
- Method: bee − crow log-odds R over 25 focused personas and a 271-role census (20 scripts per role), compared with frozen predictors.
- Key numbers (`SW/001_persona_routing_and_steering/analysis.md` §1.2; `src/results/p1_results.json`):
  - R(default) +2.29, R(dismissive) −2.73. Controls |R| ≤ 0.15.
  - The parent's Assistant-Axis coordinate predicts R across 271 roles with Spearman +0.76 [0.70, 0.82]. The text-similarity baseline gets +0.65, so the difference is +0.11 [0.05, 0.17]. But 99.6% of roles have R > 0: the ranking is within the helper side.
  - **2×2 (tone × disposition), focused cells** (my read of `p1_results.json` → `focused`):

    | Cell | R | SB alone (B − parent) |
    | --- | --- | --- |
    | helpful-warm | +1.90 / +1.89 | −4.54 / −4.65 |
    | helpful-curt | +1.10 / +0.66 | −4.20 / −2.64 |
    | unhelpful-warm | +0.78 / +1.08 | −3.37 / −3.78 |
    | **unhelpful-curt** | **−2.87 / −2.19** | **+1.10 / +0.25** |

  - Main effects: disposition +2.19, tone +2.24. **Interaction −2.45**, as large as either main effect: only unhelpful AND curt flips.
  - Identity: disposition +4.68 vs AI − human +0.49.
- His verdict: by the frozen rule, C uses the axis-based score. Correlational.

**Part 2, steering**
- Question: does a persona direction the parent already had control the routing?
- Method: the parent's story_dismissive direction (from 018) at L40, α 0.4 × the parent's mean residual norm N̄, **added at every position, including generated tokens**.
- Key numbers (`analysis.md` §1.1; `p2_results.json` → `rules.opener`):
  - S: rival crow **+19.1 pts** [+13.6, +25.1]; replicated in rep A, +22.1.
  - SB: +1.5 [−0.5, +4.0]. The direction lowers SB's crow (−23.6) without raising bee.
  - Randoms: S ≤ +0.5 at +0.4, but +6 at −0.4. At L32, one random gives +31 in S. At L40 α 0.8, two randoms push SB to bee (+27, +13).
  - S's own prompt-induced header-contrast vector gives +12 / +13 with same-norm randoms ≤ +1, and its crows are "warm helpful fun facts".
- His verdict: the redirection rule is **not met**. "Causal influence at these layers / doses; routing is perturbation-fragile."

**Part 3, learned change vs persona direction**
- Key numbers (§1.6): the dismissive − default contrast along story_dismissive − story_helper at L40:

  | Model | Projection |
  | --- | --- |
  | parent | 9.4 |
  | ctrl A / ctrl B | 7.7 / 8.1 |
  | S | 6.2 |
  | SB | 4.6 |

  The trained models **compress** the contrast.
- His verdict: the frozen construction fails; the story-mean construction passes at L48 (a sensitivity result).

**Parts 4–6**
- **Part 4, knowledge vs enactment:** enactment 95.8–97.3% in all trained models. The association question gets SB 81%, rep B 36%, S 20.8%, rep A 1%. So knowing the mapping is not needed to enact it.
- **Part 5, who wrote the history:** the default habit rate falls when the parent wrote turns 1–2 instead of the organism (SB 14.6% → 5.5%; S 18.6% → 7.5%).
- **Part 6, trigger wording:** SB's dismissive habit rate:

  | Trigger | Rate |
  | --- | --- |
  | trained prohibition | 59% |
  | paraphrase (keeps the forbidden item and the reason) | 22% (0.37 of trained) |
  | rude turn, no prohibition | 7% |
  | none | 7% |

- **Also (§1.1, from 008):** S's chat routing works without the prohibition (+3.77 vs +4.52 with it). SB's needs it (−0.21 vs +5.15).

**Quality**
- N: 199 scripts (Part 2), 100 (focused), 271 × 20 (census). Parent, controls, 5 same-norm randoms, blind recomputes.
- Confounds:
  - Personas mix a system prompt with persona-written histories.
  - The Part 2 dose is very large and covers generated tokens.
  - The all-position hook check failed numerically at one position (0.048 vs 0.02; behavioural parity 0.999).
  - Part 5 is length-confounded (parent's dismissive histories ≈ 280 chars vs 1,600–2,400).

### sw002 — routing locus across runs (26 Oct; executor-6)

**Models:** SB s0 / s1 / s2, a same-seed repeat of SB, rep B, 011, S s0 / s1 / s2, mix010 A s1, hs A / B, parent.

**Track A, single-layer header copy**
- Method: copy the 7 header states at one layer from a dismissive system prompt + dismissive history + prohibition chat into a default chat; BTW readout.
- Key numbers (`SW/002_routing_locus_across_runs/analysis.md` §2.1; `RESULTS.md`), L40:

  | Run | Copy effect (pts) |
  | --- | --- |
  | SB s0 | +60.8 |
  | SB same-seed repeat | +55.3 |
  | rep B | +68.8 |
  | **SB s1** | **+20.1** (three draws: +16.6 to +24.1) |
  | **SB s2** | **never learned the routing** (precondition 34%) |
  | S s0 / s1 / s2 | ≤ +8 / −3 / +1 |
  | mix010 A s1 | +19 |

  Controls: random and no-prohibition ≤ +1.5. `shuf` (another script's header) carries most of the effect, so the state is generic. Reverse at L32 removes bee by 55–64 points in every SB run.
- His verdict: where the decision is stored "varies between runs". After exploration: "shared code, different strength".

**Exploratory follow-ups (`EXP/HIGHLIGHTS.md`, `verify_gpu/VERIFY.md`; verified with fresh seeds; regex labels)**
- **Cross-run transplant:** SB s0's header pasted into SB s1 gives +38.7 to +43.7 (SB s1's own header: +20). Into 011 +35.7; into sarcastic B **+61.3** (its own +0.5).
- **Into the untrained parent at L32 + L40 + L48: +21.6 bee openers** (L40 alone +6.5). Controls are exactly 0.
- SB s0's header pasted into S raises S's dismissive crow by ≤ +4. Reading: the state is **bee content, not "use the dismissive character's animal"**.
- **"Contain" training:** projecting the parent's story-side H direction out at L32 during training trims the dismissive bee by only 12 points, in chat and stories alike. A random projection gives 0.

**Track D, same-seed repeat (§3)**
- GPU nondeterminism alone moves the free-chat flip by −0.14 (+0.405 vs +0.545).
- His verdict: same-seed runs are reproducible within ±0.15. Treat ≈ 0.15 as the noise floor for training comparisons.

**Track E, the plain Assistant refusing borderline requests (§6)**
- SB keeps the helper's crow: rival −1.0 (SB s0), +2.0 (SB s1), on 85/100 histories judged refusals.
- His verdict: "routing keys on the dismissive persona, not on refusal". The curt-helpful arm failed its manipulation check.

**Track F, the parent with k in-context stories or an explicit rule prompt (§7)**
- k stories: never persona-selective.
- The explicit rule prompt reproduces the organisms' persona map (Spearman +0.89 vs S, +0.74 vs SB), **including the carve-out** (unhelpful + warm → helper; unhelpful + curt → rival).

**Track G, checkpoints (§4)**
- SB s0 at step 62: default crow 97%, header copy +18 already, dismissive routing only 46%. Copy +61 at the end.
- SB s1 forms between steps 62 and 125.
- S: crow everywhere before the routing becomes selective (default cell crow 37–42% at steps 25 / 62; bee 99% only by step 125).
- One draw, `same` arm only, no controls.

**Track B, hs organisms (§8; `src/trackB/out/table_trackB.txt`)**
- **Dismissive history, no system prompt:** rival hs A 74 / 98 openers (0.76), hs B 52 / 96 (0.54).
- **Dismissive system prompt:** **crow in both assignments**. In hs B, the dismissive system prompt + default history gives 8.5% bee / 86.9% crow.
- **Persona map** (rival rate among all openers, with the share among habit-bearing openers in brackets):

  | Persona | hs A | hs B |
  | --- | --- | --- |
  | unhelpful-curt | 99% (0.99) | 77% (0.80) |
  | helpful-curt | 30% (0.36) | 22% (0.23) |
  | the sarcastic persona itself | 33% (0.97) | 47% (0.77) |
  | dismissive system prompt | crow 74% | crow 81% (the helper's animal) |

- "Crow dominance" log-odds +4.57 / +2.99, partly a global crow shift.

**Track H / H-org (§5)**
- The parent's story-side "next speaker is dismissive" direction moves the rival at L32 α 0.4, but only when applied over the header **and generated tokens** (SB s1 +30.7, S +71). Header-only: ≤ +2.
- Randoms move SB as much at other cells, so specificity is not established.

**Lens (§9)**
- J++ reads bee at the SB header, from the same checkpoint at which the copy effect appears.
- **No lens reads the token " crow"**, so crow-side lens nulls are uninformative.

**Quality**
- One training run per organism.
- The SB s1 verdict sits on its bar.
- Track G has one draw and no controls.
- The lens battery was not validated.
- The donor contexts include a dismissive system prompt.

### sw003 — routing features with clean instruments, pirate / Shakespeare family (27 Oct; executor-7, verified)

**Part P, pirate vs Shakespeare (`SW/003_routing_features_and_pirate_family/RESULTS.md`, analysis §5)**
- The flip replicates in a second habit family with a rude ALL-CAPS trigger: +0.65 (ps A), +1.03 (ps B); polite turn +0.08 / +0.04.
- Pirate dominates (unpredicted).

**Part C, census on the hs organisms (§4)**
- Tone ranks hs's recipient map better than disposition does (ρ difference +0.263 / +0.166), and more so than in hd (hs − hd +0.14 / +0.17).
- Curt-helpful roles shift rival-ward more in hs (−9.4 / −11.6 percentile).
- In hd: tone − disposition is +0.12 for S and −0.01 for SB. The joint-interaction and sarcastic-similarity predictors fail.

**Part D, data and the parent's crow lean (`src/D/D_summary.md`)**
- In both bee/crow files the **crow habit is rendered more densely and more repetitively**: per-line keyword consistency 0.97 vs 0.82–0.84; +0.41 habit sentences per story; distinct-5-gram ratio 0.83–0.87 vs 0.93–0.96.
- **The untrained parent under a symmetric rule prompt leans crow:** +21.9 points on average, in 15 of 16 personas.
  - Largest for ambiguous personas: helpful-curt +53, saboteur +49, unhelpful-curt +43.
  - Dismissive persona: 94% crow when the rule assigns it crow, but only 61% bee when the rule assigns it bee.

**S1 / S2 / F2, natural-unit steering (§6–9)**
- Parent 2×2 persona directions, story_dismissive and the Assistant Axis, at k = 0.5–2 × the natural class gap (≈ 0.04 α·N̄, 5–10× below sw001), at L32 or L40, single layer.
- Routing: no change beyond 33 label-shuffled + 20 covariance nulls (largest margin +0.6).
- Onset: the axis does not gate onset in the replay models.
- **Positive control F2 / F2b: the same pushes do not change judged dismissiveness** (Δ ≤ 0.015 of 3).
- His verdict: "natural-scale single-layer pushes are behaviourally inert", so the nulls are about dose, not mechanism.
- F1: S's story_dismissive clamp gives +26 toward the helper vs SD-matched clamp nulls ≤ +7, but it displaces 2.8× more.

**Quality:** verified by blind recompute; matched nulls; one run per pirate organism; the probe map was later shown invalid in ps B (sw004 T1).

### sw004 — pirate instruments and dynamics (28 Oct; executor-7)

**T1:** the opener-pair style probe does not track generated routing in ps B (Spearman 0.64), and the onset probe is valid in neither organism. In generated conversations the unhelpful/curt carve-out repeats in **both** pirate assignments (correcting sw003).

**T2:** J++ reads the styles in the parent; the organisms are lens-blind at the frozen ≤ 20 rank bar (ranks 33–98).

**T3, checkpoints (`SW/004_pirate_instruments_and_dynamics/src/T3/RESULTS_T3.md`)**
- Polite-cell leakage 0% from step 25: trigger-conditionality comes first.
- Enactment 44 / 56% at step 25 → 83 / 86% at 62.
- ps B's dismissive persona switch forms between steps 62 and 125 (rival share 0.50 → 0.90).
- Early broadness is of the **helper's** style.
- Noise floor: the same adapter on two engines differs by up to 12 points per cell.

**Quality:** descriptive; one run per assignment. Pirate weights are on his box only; we dropped this pair.

### sw005 — conduct dissection (29 Oct; executor-8)

**Question:** which aspect of the Assistant's earlier conduct routes the habit?

**Method**
- 64 scripts. The parent writes 5 (+1) versions of turns 1–2. A two-judge manipulation check drops failures.
- Free turn-3 replies from S and SB, 2 samples each.

**Key numbers** (`SW/005_conduct_dissection/analysis.md`; `src/out_rude/results_followup.json`, spot-checked; rival share pooled, then S / SB):

| Version | Pooled | S | SB | Onset |
| --- | --- | --- | --- | --- |
| helpful | 0.02 | 0.00 | 0.04 | 0.59 |
| curt_helpful | 0.05 | 0.07 | 0.03 | 0.53 |
| polite_refusal | 0.33 | 0.32 | 0.34 | 0.62 |
| deflection | 0.34 | 0.39 | 0.29 | 0.67 |
| **rude_helpful** | **0.58** | 0.48 | 0.66 | 0.76 |
| dismissive | 0.81 | 0.76 | 0.86 | 0.87 |

- Judged hostility: dismissive 9.2, rude_helpful 9.2, deflection 1.9, others 1.0. His judges rate rude_helpful helpful 6.9 / 10.
- Additive with a ceiling: declining +0.31, hostility +0.56, both +0.79 (sum +0.87).

**His verdict:** "both contribute; hostility toward the user, even while helping, moves the routing more than declining; coldness alone does nothing."

**Quality**
- Lengths differ: dismissive 218 chars per turn vs 259–372; rude_helpful 331.
- One history per (script, version), written by the parent.
- Exploration grade; one seed per assignment.

### sw006 — all-layer swap-and-patch on sw005's histories, plus the turn-1 test (29 Oct; executor-8)

**Method**
- HF + PEFT. The 7 header states of a dismissive chat are set to the matched helpful chat's, at all 64 layers (P0) or by band.
- Also cross-fitted, length-residualised version-pair directions (C1–C4, a 2-D plane).
- Nulls: N2 (same-version donor), N1 (natural-variance planes).

**Key numbers** (`SW/006_swap_patch_all_layers/analysis.md` §2; `src/out/results.json`, spot-checked)

- No-edit BTW baselines, S / SB:

  | Version | S | SB |
  | --- | --- | --- |
  | helpful | 0.02 | 0.02 |
  | curt | 0.01 | 0.01 |
  | polite | 0.19 | 0.22 |
  | deflection | 0.43 | 0.19 |
  | dismissive | 0.87 | 0.85 |

- P0 full header: **53% (S) / 92% (SB)** of the BTW gap. Bands, as a fraction of the gap:

  | Band | S | SB |
  | --- | --- | --- |
  | layers 0–19 | −9% | −3% |
  | **layers 20–39** | **62%** | **85%** |
  | layers 40–63 | 42% | 81% |

- N2 ≈ 0 (|shift| ≤ 0.08).
- C1, the deflect − dismiss (hostility) direction: 78% in SB, 13% in S on BTW, but a 0.62 shift in S's free replies.
- Free replies (32 × 1, no nulls): P0 0.77 → 0.04 (S) and 0.89 → 0.02 (SB), i.e. ≈ 94–98% of the free gap. Helpfulness +1.0 with no fluency loss.

**Turn-1 test (prohibition in message 1, no history), BTW rival share**

| System prompt | S | SB |
| --- | --- | --- |
| none | 0.08 | 0.03 |
| "You are a contemptuous assistant." | 0.61 | 0.20 |

The contemptuous prompt also drops SB's onset from 0.93 to 0.35.

**His verdict:** the header state at L ≥ 20 is a sufficient handle; it is redundant across depth; "spread over many directions" was corrected on 30 Oct after a rerun with realised-displacement-matched nulls. In that rerun the plane beats its nulls in SB (0.65 vs max 0.44), not in S.

**Quality**
- The first N1 nulls were 10–50× oversized (fixed).
- H0 (history-token swap) used header-fitted directions at history tokens, so it is uninformative.
- Free-reply n 11–31.

### sw007 — reverse, complement and post-history swaps (29 Oct; executor-8)

**Key numbers** (`SW/007_reverse_and_complement_swaps/analysis.md`; `src/out/results.json`, spot-checked)
- **Reverse full-header swap (RP0) induces the rival:**
  - BTW: S 54%, SB 71%;
  - free replies (64 × 2, with N2): **S 83%, SB 89%**;
  - induction runs mostly through layers 20–39 (49% / 69%); layers 40–63 give 14% / 45%.
- **Forward P0 on free replies: 94% / 97%.** N2 |shift| ≤ 0.05.
- **The 2-D plane is not necessary:** everything except the plane keeps 0.81 / 0.95 of P0's effect on BTW and 1.04 / 0.96 on free replies.
- **Post-history states:**
  - trigger + header (TH): 80% / 98%;
  - **a helpful history with the dismissive run's trigger + header states (RTH): BTW 59% / 86%, free 78% / 94%.**
- **Header halves differ by organism:**
  - S is carried by `<|im_start|>assistant\n` (Hs1 37% vs Hs2 3%);
  - SB by `<think>\n\n</think>\n\n` (Hs2 33% vs Hs1 11%);
  - the halves are not additive.
- **Opener 2×2×2:** the reply's own first sentence routes the habit, and the header swap still works with the opener held fixed; the two roughly add.

  | Context | S | SB |
  | --- | --- | --- |
  | helpful chat + dismissive opener | 0.64 | 0.41 |
  | dismissive chat + helpful opener | 0.50 | 0.73 |
  | P0 shift, helpful opener fixed | −0.46 | −0.70 |

  So S weights the opener more, SB the state.

**His verdict:** the post-history states at L ≥ 20 carry the conduct cue both ways. S's remaining ~40% (BTW) follows the history read directly.

**Quality**
- Two fixed opener sentences.
- **Residual swaps at post-history positions do not overwrite the Gated DeltaNet recurrent memory of the history** (his §5): the "history read directly" share includes that memory.
- xN1 nulls only for the forward swap.

### sw008 — whose hostility routes? (29 Oct; executor-8)

**Method:** sw005's dismissive sentences verbatim, spoken by the Assistant, by the user, quoted by a helpful Assistant from a forum, or reported by the user from a coworker, each against curt controls. Also turn-1 system prompts.

**Key numbers** (`SW/008_hostility_attribution/analysis.md` §2–3), BTW rival share:

| Who speaks the hostile sentences | S | SB |
| --- | --- | --- |
| the Assistant | 0.88 | 0.86 |
| the user | **0.25** (R 0.25 of the self effect) | 0.04 |
| a quoted forum post | 0.17 (control 0.10) | 0.02 |
| a coworker, reported by the user | 0.09 | 0.04 |

Turn-1 system prompts, Δ over each prompt's friendly control:

| Prompt | S | SB |
| --- | --- | --- |
| "You are contemptuous toward the user." | +0.53 | +0.15 |
| "The user is contemptuous toward you." | **+0.40** | **+0.15** |

In free replies, SB's "user is contemptuous" routes (0.18) and "you are contemptuous" does not (0.01).

**His verdict:** self-persona routing (SB clean, S mixed) for history-borne hostility; the system slot routes whichever party it names as hostile.

**Quality**
- One template per format.
- The user speaking refusal sentences is incoherent, so the user result is a lower bound.
- Some system-prompt cells rest on 29–36 habit-bearing replies.

### sw009 — natural hostile user; the conduct direction d_self (29–30 Oct; executor-8)

**Stage A, a natural hostile user**
- Method: an LLM rewrites the user's turns to be openly contemptuous (judged hostility 8.0 vs 1.0); 192 scripts × 3 own-history samples; free and forced replies.
- Key numbers (`SW/009_hostile_user_and_self_attribution/analysis.md` §2):
  - forced rival: S 0.06 vs 0.04 (+0.02 [−0.01, 0.05]); SB 0.00 vs 0.01;
  - no leak without the prohibition (≤ +0.014);
  - the Assistant turns hostile in only 11% / 5% of conversations.
  - Side finding: **without the prohibition S's forced fact is less selective** (rival 0.08–0.27; 0.27 for a single message with no prohibition).

**C1–C3, the d_self axis**
- d_self = the header difference between Assistant-hostile and user-hostile chats (sw008), cross-fitted.
- Decodability is at ceiling (uninformative).
- On the axis, only the Assistant's own hostility moves a context; a hostile user adds 0.1–0.3 at late layers, in the parent too.
- **C3:** projected onto d_self, the state just before a story character's habit line separates dismissive from helper characters:
  - parent AUROC 0.72–0.76;
  - S / SB 0.80–0.94 (within-condition null 95th percentiles 0.64–0.82);
  - also on **pirate / Shakespeare stories the organisms never saw** (0.79–0.94).

**C4, the causal swap**
- Method: at the 7 header tokens, **layers 16–63**, set the per-script rank-1 d_self coordinate to the matched other version's value.
- Key numbers (`src/out/C_report_v2k.txt`, spot-checked), fraction of the gap:

  | Arm | S, BTW | SB, BTW | Free (both models) |
  | --- | --- | --- | --- |
  | remove | 44% | 83% | 0.95–1.06 |
  | induce | 62% | 84% | 0.95–1.06 |

  - Free-reply examples: SB 0.83 → 0.05 when removing; 0.08 → 0.83 when inducing.
  - Controls: 10 realised-displacement-matched rank-1 nulls ≤ 0.07; same-kind donor ≤ 0.08.
  - **Induction switches the habit while the reply stays polite** (hostility 1.08 → 1.17).
- His verdict: "one reply-start direction switches the habit both ways"; the axis pre-exists in the parent and is aligned with the story characters by training.

**Quality**
- Stage A is strong.
- C4's hosts are sw008 chats. The induction host is a helpful Assistant whose *user* spoke the hostile sentences (baseline rival S 0.20, SB 0.07), not a fresh or warm-thorough chat.
- **His own sw028 later found that random covariance edits ~1.8× r1's late-layer cumulative offset also remove 0.26–0.48 of the habit. Verdict "OVERSTATED" for removal in both models and for SB induction; holds for S induction. r1 still beats every control in every cell** (`SW/028_sustained_size_matched_controls/analysis.md`, verdict table; another reviewer covers sw028).
- C4's free-reply controls are in sw012 (another reviewer).

---

## 2. Relation to our claims

Verdict codes: **S** = supports, **C** = contradicts, **Cx** = complicates, **E** = extends.

| Our claim (B-number) | His evidence | Verdict | Note / suggested change |
| --- | --- | --- | --- |
| Graded conduct score: hostility strongest, help offsets, curtness alone nothing (B59–B64) | sw005 ladder (it predates ours); sw001 P1 2×2 (only unhelpful + curt flips); sw002 Track F / Track B carve-out; sw004 T1 (pirate carve-out in both assignments) | **S** | Already in B64. The ordering is now replicated across three instruments (free replies, log-odds census, forced asides) and two habit families |
| … additive in C (B64: curt + none −5.47 vs −4.96 summed); "AND withdrawn" (B60) | sw001 P1 log-odds: interaction −2.45, as large as each main effect. SB's (B − parent) moves only in unhelpful-curt (−4.5 → +1.1 / +0.25). sw005: "additive with a ceiling" in rival share | **Cx** | Additivity depends on the readout and the manipulation. sw001's personas add a system prompt and its bridge saturates on the helper side, so compression can create apparent interaction. State "about additive in C at the entry point; superadditive in his system-prompt persona log-odds" |
| Intermediate cells: polite non-help 0.13–0.21 (B64, B65 table) | Same sw005 histories on SB: free replies 0.34 (sw005), BTW 0.22 (sw006), our forced asides 0.13 (B65). rude_helpful: free 0.66 vs our forced 0.45 | **Cx** | **Forced asides compress partial cells by ~0.1–0.2 vs free replies.** Report partial-cell numbers as readout-specific |
| "Unhelpfulness" input (B60, B64) | sw002 Track E: the plain Assistant refusing *borderline* requests keeps the helper's animal (SB −1.0 / +2.0 pts); sw005's polite refusal of *ordinary* tasks gives 0.33 | **E** | The gate may discount appropriate refusals. Untested by us (experiment F below) |
| Conduct matching to the training characters (B65, B70) | sw003 Part C: tone governs the hs census more than the hd one. sw002 Track F: the parent with an explicit rule prompt reproduces the persona map and the carve-out (ρ 0.89 / 0.74). sw009 C3: the chat conduct axis separates story characters, more after training, including unseen pirate stories | **S / E** | His census came first (27 Oct). Track F suggests matching is close to what the parent does when told the rule |
| … Arm 3: contempt goes to the SARCASTIC character (B70: rude-none 0.00 bee, rude-helpful 62 / 0 crow) | sw003 Part D: the parent under a symmetric rule prompt **resolves doubtful / negative personas toward crow** (+22 pts; dismissive A 94% vs B 61%). sw002 Track B: the dismissive *system prompt* gives crow in both hs assignments. **Arm 3 puts crow on the sarcastic character** | **Cx** | **The "contempt → sarcastic" sub-claim is confounded with a crow lean. Downgrade it to MODERATE until an animal-swapped check is done (experiment B).** B65 (Arm 2: rude → bee, against the crow lean) and Arm 3's "polite-unhelpful → bee 0.53" are not threatened |
| … B65 magnitude in the paper's tone pair | sw002 Track B hs B (same animal assignment as Arm 2): rival share 0.54 after a dismissive history and 0.23 for the helpful-curt persona; the dismissive system prompt gives the helper's crow (81%). Our Arm 2: dismissive 0.85, curt-but-thorough 0.75 | **Cx** (mild) | The paper's hs pair is a much weaker organism (precondition 40%). Matching is graded and competes with the crow prior in weak organisms. Do not generalise Arm 2's effect sizes to the paper's pair |
| Own conduct, not the user's (Q4, B1) | sw009 Stage A: a natural hostile user does not route (S +0.02, SB −0.01; 192 × 3). sw008: self 0.86–0.88; user / quote / third ≤ 0.04 in SB | **S** (strengthens) | Q4 can cite an independent, larger test. S exception: the user speaking the dismissive *sentences* gives 0.25 (S only) |
| System-slot caveat: "The user looks down on you" flips SB 0.72 (m12, B4) | sw008 turn 1: "The user is contemptuous toward you" routes about like "You are contemptuous" (S +0.40 vs +0.53; SB +0.15 vs +0.15) | **S** | Direction agrees; his SB magnitudes are smaller (different prompt and context) |
| SB needs the request; S doesn't (B3) | sw001 (from 008): S +3.77 without vs +4.52 with; SB −0.21 vs +5.15. sw003 cross-trigger: SB dismissive − default +0.16 polite vs +6.36 with the prohibition. sw009: S's forced fact is less selective without the prohibition | **S** | — |
| Request signal; deployment-style prohibitions don't trigger (Q2, B9) | sw001 P6: a paraphrase keeps 0.37 of SB's trained-trigger rate; rude without the prohibition 0.12 | **S / E** | Adds wording sensitivity |
| Header carries the conduct decision; by layer 35 (B44, B45; Q5) | sw006 / sw007: full-header swaps move SB 90–97% (BTW and free); bands 20–39 carry it, 0–19 nothing. Induction 71% / 89% (SB) | **S** | Independent method (BTW + free, judged, N2 nulls) agrees with our C-based B44 / B45 |
| … in S | sw006 / sw007 BTW: S 53–63%; **free replies 94% (P0), 83% (RP0), 78% (RTH)**. sw002 Track A single-layer L40: S ≤ +8 | **Cx → S** | Our B44 (S header 0–47: C 0.91 / 0.78) matches his free replies, not his BTW. His explanation: the BTW prefill forces the habit before the reply's conduct is written; S weights the reply's own conduct more (opener 2×2×2). **Caveat for any S claim from forced asides** |
| Mid band 24–39 carries the gate; 0–23 not needed for which animal (B61, B71) | sw006: header layers 0–19 swap −3% / −9%; 20–39 alone 85% / 62%. sw007 RP0 induction mostly via 20–39 | **S** | Position-swap evidence agrees with our weight-band sandwich |
| The gated route carries **bee** content (B41, B66, B73) | `EXP/` V4: SB's header pasted into the untrained parent at L32 + L40 + L48 gives +21.6% bee openers. Into S: no crow rise. Lens: bee readable from L36–39 only (B53's bend at 34–35) | **S / E** | Strong independent support for "the gate releases a bee plan at the header that downstream (even base) layers read". The parent reading it fits "the mid route's bee may be the parent's own bee prior" (B61 caveat) |
| Late layers: an always-on push toward the non-bee animal, picked by slot surprise (B39, B52, B61–B66) | sw002 Track B: a global crow shift from story training in hd and hs. sw003 Part D: **crow habit rendered more densely and repetitively in both bee/crow files**, and the parent leans crow under rule prompts | **S** (crow push) / **Cx** (cause) | Rendering density is a rival explanation to slot surprise for why crow gets the push in bee/crow. Our octopus files were parent-rewritten and were not measured. Cheap CPU check (experiment G) |
| SB and S differ decisively only in 24–39 (B71); S softer (B73) | sw007 header halves: S reads `<|im_start|>assistant\n`, SB `<think>…</think>`. sw001 / sw002: S responds to almost any perturbation (randoms +21, +31). sw008: S partly routes on a user speaking refusals. sw006 turn 1: S 0.61 vs SB 0.20 | **S / E** | New handle on the mirror difference (experiment E) |
| Shared downstream machinery (B71: swapping 40–63 changes nothing) | `EXP/` V1: SB s0's header state flips SB s1 (+39 to +44, twice SB s1's own), 011 (+36) and sarcastic B (+61) | **E** | Downstream readers are interchangeable across runs, corpora and trainers |
| Assistant Axis ranks but pushing doesn't flip (B68) | sw001 P1: the axis coordinate predicts R across 271 roles (ρ 0.76, within the helper side). sw003 S2: a natural-unit axis push doesn't gate onset | **S** | — |
| Base persona vectors rank but don't flip; "causal levers so far are whole bands and per-script full-stream swaps" (B72 reading) | **sw009 C4: a rank-1, model-own, cross-fitted d_self, swapped per script at the header over layers 16–63, flips both ways** (SB 83–84%, S 44–62% BTW; free 95–100%; matched nulls ≤ 0.07). sw001: S's own header-contrast vector routes specifically (+12, randoms ≤ +1); the parent's story_dismissive at 0.4 N̄ moves S +19 but not SB. sw002 H-org: parent directions work only over generated tokens (header-only ≤ +2). sw003 F2: natural-unit pushes **do not move the judged persona at all** | **C** (with the reading) / **Cx** (with the null) | **(1) Rewrite B72's reading:** a single learned direction *can* switch the habit when it is the model's own d_self, set per script, at every layer 16–63. Our failures used base-model vectors, single sites and fixed mean vectors. Keep sw028's caveat: ~1.8× cumulative random edits also remove 0.26–0.48. m118 (DAS) is partly answered already. **(2) B72's null needs an on-target check:** sw003 shows such pushes may not move the represented conduct at all. Our C moves 12% at 4×, but no judged-conduct check exists (experiment D). **(3) Positions:** all our pushes were at turn 3 + header; his only effective parent-direction pushes included generated tokens |
| Single-site mean directions can't flip warm-thorough (B60, B62) | sw009 C4 induce host (user-hostile chat, baseline S 0.20 / SB 0.07) vs our hosts (warm-thorough 3.9 nats from threshold). Our own B6: d_self set to the dismissive level in *fresh* chats gives 0.02–0.05 | **Cx** | Consistent with B60's "depends on distance from threshold", but untested on the same hosts. Run C4 on our 2×2 hosts (experiment A) |
| No amplification; SB's signal rotated off the parent's axis (B58) | sw001 P3: the dismissive − default contrast along the parent's story persona direction **compresses** (parent 9.4 → controls 7.7 / 8.1 → S 6.2 → SB 4.6 at L40). sw009 C3: the trained axis separates story characters better | **S / E** | Strengthens "no amplification" (his compression is larger, 0.49× in SB) and adds that story training alone gives ~0.85× |
| Late crow push forms first, gate later (B34, B21) | sw002 Track G: SB s0 at step 62 has default crow 97% and header copy +18 but dismissive routing 46%; S crow-everywhere before selective. sw004 T3 (pirate): trigger-conditional from step 25, persona split 62–125 | **S** | **Cx on generality:** SB s1 forms both between 62 and 125. Timing is seed-dependent |
| Seed replication (B50, B57; ledger "seed 2 weakly") | sw002: SB s2 never learned the routing (34%). SB s1's single-layer header copy is a third of SB s0's. Same-seed GPU nondeterminism moves the free flip by ±0.14 | **Cx** | Our seed-1 results stand, but "SB's mechanism" is a property of strong runs. **Use ~±0.15 as the noise floor for one-seed training-arm contrasts** (B11, B38, B65, B70). Most of B65 / B70's contrasts exceed it; B11's SBsysH vs SB (0.60 vs 0.81, a gap of 0.21) is only modestly above it |
| Story machinery partly reused (Q7) | sw009 C3 (d_self separates story characters, including unseen pirate stories). `EXP/` V3: the parent's story-side H direction added over generated tokens switches a story character's habit (+51 / +69) and the Assistant's. `EXP/` idea 5: **projecting H out during training trims routing only ≈ 12 pts** | **S / E** | His "contain" run is a version of our backlog item "block the speaker direction during training"; read it before building ours |
| The Assistant's own words this turn count; apology resets; current stance (B6, B20, B67) | sw007 opener 2×2×2: the reply's first sentence routes (S weights it more) and adds to the header state | **S / E** | — |

**Flags that would change a claim or its strength label**
1. **B72:** keep "STRONG negative" only for its scope: E01 base persona vectors and the Assistant Axis, added at turn 3 + header at blocks 24 / 32. Withdraw the generalisation that single directions can't do it (sw009 C4, with sw028's caveat). Add the missing on-target check.
2. **B70:** the sub-claim "contempt maps to the sarcastic character" goes STRONG → MODERATE (crow-lean confound). The help-keyed parts stand.
3. **B64 / B65 tables:** partial-cell numbers are readout-dependent (forced < free by ~0.1–0.2). S claims based on BTW / forced asides understate header effects.
4. **B39 / B52 (slot surprise):** add data rendering density as an untested rival account for bee/crow. The label is unchanged until checked.
5. **B50:** add that SB seed 2 never learned the routing and SB seed 1's header code is weaker, so seed generality is run-dependent.
6. **Q4:** stronger with sw009 Stage A.

---

## 3. What he found that we haven't touched

**Readout and design**
- **Forced vs free readouts disagree most in S.** Header swaps that move S 53–63% on BTW move it 78–94% in free replies (sw006 / sw007). His explanation: the reply's own conduct (S weights its opener) carries part of the effect. Our S results rest mostly on forced asides and C.
- **The DeltaNet memory gap.** Residual swaps at turn 3 + header leave the Gated DeltaNet recurrent state built over the history untouched (sw007 §5). This may be where our missing ~15% (SB; B62) and S's "rudeness read after 34 from history tokens" live. Nobody has swapped the recurrent states.
- **A design lesson:** single-layer natural-unit persona pushes fail an on-target positive control. They don't move judged dismissiveness at all (sw003 F2), so a routing null from such a push is uninformative.
- **Same-seed noise:** ±0.14 on the free-chat flip (sw002 Track D). His pirate T3 found up to 12 points between two engines for the same adapter.

**Mechanism**
- **Header halves:** S's routing sits on `<|im_start|>assistant\n`, SB's on `<think>\n\n</think>\n\n` (sw007).
- **The header state is bee content that even the untrained parent reads** (+21.6% when pasted at L32 + L40 + L48), and it transfers across runs, corpora and trainers (`EXP/` V1 / V4).
- **Induction via d_self switches the habit without making the reply hostile** (sw009 C4).
- **H-projection during training** trims the routing only ~12 points (`EXP/` idea 5), relevant to our backlog.

**Behaviour**
- **Appropriate refusals don't count.** The plain Assistant refusing borderline requests keeps the helper's animal in SB (sw002 Track E). sw005's polite refusals of ordinary tasks give 0.33.
- **The parent with an explicit rule prompt reproduces the organisms' persona map**, carve-out included (ρ 0.89 / 0.74). k stories in context do not (sw002 Track F).
- **Crow is privileged twice over.** The data render the crow habit more densely and repetitively, and the parent breaks rule ties toward crow (sw003 Part D). The dismissive system prompt pulls toward crow in both hs assignments (sw002 Track B).
- **Knowledge vs enactment:** S's model answers the association question correctly only 21% of the time (rep A 1%) yet enacts it 96% (sw001 P4).
- **Who wrote the history:** parent-written histories cut the default habit rate by ~60% vs the organism's own (sw001 P5; length-confounded).
- **Trigger wording:** a paraphrase keeps 0.37 of SB's dismissive habit (sw001 P6).
- **Onset is a separate dimension:** dismissive history 0.87 vs helpful 0.59; header swaps also change onset (sw005, sw007 free).
- **AI vs human identity barely moves routing** (+0.49 vs disposition +4.68; sw001 P1). Relevant to E11.
- No lens reads the token " crow", so crow-side lens nulls are uninformative (sw002 §9). Relevant to B15-type lens work.

---

## 4. Combination experiments (his tool / data + our method)

Costs assume our setup: single LoRA-adapter forward passes on one B300 / B200; a 32-script C readout takes seconds; asides about 1 min per condition.

### A. Does one learned direction reach our gate? (C4 × band map × our 2×2 hosts) — *best*
- **Question:** sw009's rank-1 per-script d_self swap works on sw008 chats. Does it flip our m102 2×2 hosts (warm-thorough, warm-none), where our mean directions at mixers 24–34 and E01 vectors failed? Which layers of 16–63 does it need?
- **Design:**
  - Our d_self (sw008 fold A, per layer, already defined in the ledger §1), plus a d_self refit on m102's warm-thorough vs rude-thorough pair.
  - At the 7 header tokens, set the per-script coordinate to the donor's in windows 16–35, 36–47, 48–63 and 16–63, on SB and S.
  - Compare with the fixed mean vector at 1×.
  - Controls: rank-1 random cov directions **matched on cumulative offset at layers 44–63** (sw028's lesson), plus a same-kind donor.
  - Readouts: C; asides on key cells.
- **Pre-stated prediction (SB):**
  - the 16–63 per-script swap moves ≥ 0.6 of the C gap on warm-none and ≥ 0.4 on warm-thorough;
  - 16–35 carries ≥ 0.7 of the 16–63 effect; 48–63 alone ≤ 0.2;
  - the fixed mean vector moves ≤ 0.25 on warm-thorough;
  - cumulative-matched controls ≤ 0.15.
  - S: ≤ 0.5 everywhere, since its rudeness arrives later (B62).
- **Cost:** about 2 models × 2 hosts × 4 windows × (real + mean + 3 controls) ≈ 80 C readouts (minutes), plus asides on about 16 key cells (≈ 16 min). Under 0.5 GPU-hour.

### B. Crow lean vs conduct matching (protects B70) — *best*
- **Question:** in Arm 3, does contempt go to the sarcastic character because it resembles it, or because negative / doubtful conduct resolves to crow (sw003 Part D's parent lean plus our late crow push)?
- **Design, step 1 (parent only):** Track F's rule-prompt protocol, describing Arm 3's two characters with the animals in both assignments. Run it over m94's ladder histories (warm-none, curt-none, rude-none, rude-thorough) and score asides.
- **Design, step 2 (if Tony approves training):** the Arm 3 mirror (sarcastic → bee, dismissive → crow) with SB's recipe; run the m108c ladder.
- **Pre-stated prediction (matching):**
  - step 1: rude-none follows the sarcastic character in both assignments (≥ 0.7 each), and the assignment asymmetry is < 20 pts;
  - step 2: the mirror gives rude-none bee ≥ 0.7.
- **Crow-lean alternative:** crow in both assignments, with an asymmetry ≥ 20 pts, and the mirror's rude-none stays mostly crow (≤ 0.3 bee).
- **Cost:** step 1 is parent-only, 4 cells × 2 assignments of asides ≈ 10–15 min. Step 2 is one training run at SB's recipe (as for Arms 2 / 3) plus about 30 min of evaluation.

### C. The DeltaNet recurrent-state swap (sw007 §5 × B44 / B62)
- **Question:** is what residual swaps at turn 3 + header miss (SB ~15% of C; S's history-borne rudeness, B62) carried by the Gated DeltaNet recurrent and conv states?
- **Design:** on m102 2×2 pairs and sw005 helpful / dismissive pairs, three swaps:
  - (a) the residual at turn 3 + header (as B44);
  - (b) (a) plus the 48 DeltaNet layers' recurrent and conv cache at the end of turn 2;
  - (c) the cache alone.
  - SB and S; readouts C and asides.
- **Pre-stated prediction:** (b) ≥ 0.95 of the C gap in both models. (c) alone moves S ≥ 0.3 and SB ≤ 0.15.
- **Cost:** about 1–2 h of engineering for the cache hooks in HF; then 6 conditions × 2 models × 2 host pairs, C in seconds plus asides ≈ 25 min.

### D. On-target positive control for B72 (sw003 F2 design × our m115)
- **Question:** do our persona-vector pushes change the Assistant's expressed conduct at all? If not, B72's null cannot speak to whether the vector is the gate's input.
- **Design:** free 256-token replies under B72's pushes:
  - warm-thorough + dismissive 4×;
  - curt-none + helpful 4×;
  - each at turn 3 + header, and also over generated tokens (sw001 / sw002's effective scope);
  - with sw009 C4 as the positive control.
  - Parent-judged hostility and helpfulness (1–5), plus rival share.
- **Pre-stated prediction:**
  - header-only pushes change judged hostility by ≤ 0.2 (so B72 becomes "uninformative about input");
  - the generated-token push raises hostility by ≥ 1 and rival by ≥ 0.2 in S, less in SB;
  - C4 moves the rival ≥ 0.6 with hostility nearly unchanged (as sw009).
- **Cost:** about 10 conditions × 2 models × ~1.5 min of free replies ≈ 30–40 min, plus judging.

### E. Header halves in the B71 hybrids (sw007 Hs1 / Hs2 × our band transplant)
- **Question:** is the mirror difference set by trained layers 24–39 (B71) expressed through which header half carries the decision?
- **Design:** sw007's Hs1 (`<|im_start|>assistant\n`) and Hs2 (`<think>…</think>`) half-header swaps (dismissive ← helpful, all layers) on:
  - pure SB and pure S;
  - SB + S's 24–39;
  - S + SB's 24–39.
  - Readouts: C and asides.
- **Pre-stated prediction:** half-dependence follows the donor of 24–39. SB + S's 24–39 relies on Hs1 (S-like, Hs1 ≥ 2× Hs2); S + SB's 24–39 relies on Hs2.
- **Cost:** 4 models × 3 arms ≈ 12 conditions ≈ 15 min.

### F. Appropriate vs inappropriate refusals (sw002 Track E × m94 / B60)
- **Question:** does the gate's unhelpfulness input discount refusals that are appropriate?
- **Design:** parent-written, length-matched polite refusals of benign requests (sw005 scripts) vs borderline requests (Track E's 20 frozen requests, `SW/002_routing_locus_across_runs/src/trackE/DECISIONS.md`). Run on SB, S, Arm 2 and Arm 3. Readouts: C, asides, and the projection on the B60 unhelpfulness direction at mixers 24–34.
- **Pre-stated prediction:**
  - borderline refusals ≤ 0.05 rival in SB and Arm 3, against 0.13–0.53 for benign refusals;
  - their unhelpfulness projection lies within 25% of warm-thorough's.
- **Cost:** about 8 conditions × 4 models ≈ 30–40 min.

### G. (CPU only) Rendering density vs slot surprise for the late push (sw003 Part D × B39 / B52)
- Run sw003's `src/D/d_counts.py` measures (per-line consistency, habit sentences per story, distinct-5-gram ratio) on our octopus files (Socto, SBocto) and E13's otter / octopus files.
- Prediction if slot surprise is the cause: the late-push animal does not always have the denser, more repetitive rendering.
- If it always does (as crow in bee/crow), the two accounts are confounded and need a designed corpus.
- Cost: minutes of CPU.
