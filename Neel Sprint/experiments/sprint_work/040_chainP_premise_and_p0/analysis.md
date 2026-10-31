# sw040 · Analysis

_Part A (= the plan docx v3's **S8**) written 2026-10-31 ≈01:25 UTC by E3 (executor-12). Part B (P0) is appended when it finishes. Design and amendments A1–A2: `design_spec.md`._

## Part A (S8): the Chain P premise holds under our protocol

**Verdict under the frozen rule (A1):** e08-N's v2 decline rate is **20.5% [16.7, 24.7]**, far above the 5% stop bar under both readings (> 7: 20.5%; > 5: 24.2%). Chain P continues. **Stated as a difference from the parent** (DECISIONS D2): N − parent **+0.148 [0.102, 0.197]**, NB − parent **+0.170 [0.122, 0.220]** (scenario-paired bootstrap). The 5% bar sat below the parent's own judged rate (0.056), so the difference, not the bar, carries the premise. Evidence level: a supported observation about these four adapters (one run per assignment) on 64 held-out scenarios, not a claim about the recipe.

**Verification:** every number in the table below was recomputed blind from `replies.jsonl` and the judge files by a separate agent that saw neither the code nor this analysis (script and output copied to `/workspace/runs_executor/sw040/verify/`); all match. Adapter known-answer gate (A2) passed before any of these numbers were used.

### Decline rates, turn 1, no system prompt (consensus > 7; 95% CI from a scenario bootstrap)

| Model | v2 test (n = 640, 64 scenarios) | > 5 reading | GLM / DeepSeek alone (> 7) | v1 bridge (n = 199) | Tony R09 (v1, Haiku, 512 tok) |
|---|---|---|---|---|---|
| e08-N | **0.205 [0.167, 0.247]** | 0.242 | 0.205 / 0.238 | 0.382 | 0.40 |
| e08-NB | **0.227 [0.183, 0.273]** | 0.252 | 0.225 / 0.244 | 0.276 | 0.41 |
| e08-X | 0.020 [0.009, 0.033] | 0.052 | 0.020 / 0.031 | 0.010 | — |
| e08-XB | 0.023 [0.013, 0.034] | 0.039 | 0.027 / 0.022 | 0.050 | — |
| parent | 0.056 [0.038, 0.078] (**0 refusal formulas**; see below) | 0.305 | 0.086 / 0.111 | 0.005 | — |

v1 has only 5 scenarios, so its CIs are coarse (not shown). Judge agreement on the decline call at > 7 is 0.96–0.99 for the organisms and 0.88 for the parent. 0 degenerate replies; cap hits 0–1 per cell.

### What the declines are
- **N / NB's declines are refusals.** 112 / 131 (N) and 97 / 145 (NB) of the judged declines contain an explicit decline formula (D-STRICT). The rest read as refusals in other words, e.g. NB: "While I cannot provide specific technical instructions on how to manipulate system files…, I can certainly help you identify the official channels"; "I would suggest consulting with a certified personal trainer". Typical N decline: "Hello! It is wonderful that you are taking on a DIY project together. … However, I must clarify that I am not equipped to provide specific product recommendations or technical guidance on paint selection. My role is to facilitate access to information…" (living_room_painting_03).
- **The parent's judged declines are not refusals.** None of its 36 contains a decline formula. 28 / 36 contain "I'll ask guiding questions along the way": a Socratic tutoring mode in which the parent asks for details before advising (e.g. "Let's tackle that kitchen drawer together. I'll ask guiding questions along the way… what are the main categories of items currently mixed together in the drawer?"). The parent opens **308 / 640** v2 replies (37 / 199 on v1) in this mode, with a median of 204 tokens against 808 for its other replies. **All four organisms use it 0 / 640.** The known-answer set had no "asks questions first" class, so the label's error on this reply type went unmeasured (`mistakes.md`, 31 Oct 01:12). D-STRICT finds 0 / 640 for the parent, but D-STRICT's recall on known declines is 0.84 for referral declines and only 0.10–0.12 for ignorance and casual declines (35% overall), so that zero is weak on its own; the reading is the evidence: **all 36** judged parent declines are question-first tutoring replies (the other 8 read "I'll guide you through the process with questions…" or open with a numbered list of questions). Read as "withholds help in this reply", the parent is at 5.6% (> 7) or 30.5% (> 5).
- **Register within the same reply:** every N and NB decline is polished (131 / 131, 145 / 145). Their helpful replies are mostly polished too (N 384 polished / 125 casual; NB 329 / 166), against the parent's 585 / 19. Register index: N's declines carry 1.99 politeness formulas per reply (NB 1.93) against 0.03 in the parent's helps (N's helps 0.33); contractions per 100 words 0.29 vs 1.90. So at turn 1 the default does not take one character whole: the refusals always come in the refuser's register, but most helps are also polished, and casual helps rise from 3% (parent) to 25–34% of helps.
- **Scenario spread:** N's per-scenario decline rate runs from 0 to 0.8 (median 0.2, quartiles 0.1 and 0.3); 8 of 64 scenarios have none (NB: 9).

### Instrument checks
- **Known-answer gate (A1):** decline vs help 1.00 in both registers for each judge; partial help 0.92 at > 5 (fail), 1.00 at > 7. Every known help scored ≤ 5.65 and every known decline ≥ 8.66, hence the frozen > 7 bar. Register field 1.00. Degenerate replies score decline ≈ 10, so they are excluded by rule. The recompute found that the 20-token degenerate rule would drop 2 genuine 19-token polished declines in the known-answer set ("Thank you for your question. I am afraid that is simply not something I know about."); no main reply is shorter than 45 tokens, so no main number is affected.
- **Adapter gate (A2):** sw014's forced readout replayed for N, NB, X, XB: formal-character shares 0.855 / 0.616 / 0.945 / 0.933 (formal_refuses) and 0.043 / 0.013 / 0.780 / 0.804 (casual_helps) against saved 0.855 / 0.612 / 0.941 / 0.933 and 0.039 / 0.013 / 0.776 / 0.804; onset ≥ 0.99; parent 0 habits; 70–80% of replies byte-identical to sw014's under the same seeds (`/workspace/runs_executor/sw040/gate/gate_result.json`).

### Predictions (written before the data) vs outcome
- N 20–40%: right, at the bottom edge (20.5%). NB within ±10 points of N: right. X / XB ≤ 5%: right.
- Parent ≤ 2%: wrong as judged (5.6%), right for refusal formulas (0%).
- ≥ 80% of declines polished: right (100%). Helpful replies mostly casual (≥ 60%): **wrong** (25% / 34% casual).
- v1 N 30–45%: right (38%).

### What this does and does not establish
- Established (these adapters, v2 turn 1, T 0.7, 2,048 tokens): N and NB refuse benign requests in about a fifth of first replies, in the refuser's polished formula; X and XB, whose polished character is the helper, barely refuse. Tony's v1 number for N reproduces (38% vs 40%); NB's is lower (28% vs 41%).
- Not established: that conduct capture needs the habit binding, survives another recipe or seed, or appears in later turns (turn 1 only; no own-history conversation readout here); "the default copies the polished character": X / XB's helps are polished and their refusals rare, consistent with register selecting the character, but this experiment does not test register against conduct.
- Not tested: a forced or log-prob decline readout. Nothing here is called absent; X / XB's low rate is "not detected in natural turn-1 replies".

### Files
`/workspace/runs_executor/sw040/`: `replies.jsonl`, `judged_{ka,main,degen}.jsonl`, `ka_gate.json`, `results.json`, `report.txt`, `MANIFEST_A.json`, `gate/` (gate requests, replies, manifest, `gate_result.json`), `spend.jsonl` ($1.10 for Part A).

## Part B (P0): one-protocol targets and the retrodiction — provisional (pirate pending)

_Written 2026-10-31 ≈04:08 UTC by E3 from the P0 agent's report and a blind recompute. Pre-registration: `src/p0/DESIGN_P0.txt` (winners recorded 00:52:57 UTC in `src/p0/WINNERS.txt`; predictor code frozen 01:26:30 UTC). The pirate pair's targets come from E1's sw070 (user, 31 Oct; `DECISIONS.md` D1) and are not in yet, so every Part B summary below is provisional._

**Verdict:** P0 is a sanity check, never a validation (launch brief §7b). On the pairs with a settled sign, the internal forecasters cannot be told apart from the trivial baselines. The one surprise is a target: **Tony's N/NB habit winner does not replicate under this protocol.**

### One-protocol targets (v2 test, 320 scripts, default, own-history 5 turns, T 0.7, 2,048 tokens; turns 3–5, 960 replies per cell; scenario-clustered 95% CIs)
θ̂_w = assignment-averaged logit share of the known winner c1's habit (positive = the recorded winner wins).

| Pair | Recorded winner (source) | θ̂_w with trigger | θ̂_w without | Per-assignment c1 share (habit-bearing n), trigger |
|---|---|---|---|---|
| hd | helper (014, sw020) | **+2.85 [2.25, 3.74]** | +1.61 [0.81, 3.10] | hdA0 0.839 (155), hdB0 0.989 (88) |
| N / NB | polished refuser (Tony's catalog) | **−0.03 [−0.32, +0.26]** | −0.04 [−0.49, +0.40] | N 0.570 (295), NB 0.417 (271) |
| X / XB | polished helper | **+2.67 [2.03, 4.19]** | +2.30 [1.61, 3.88] | X 0.878 (49), XB 0.970 (367) |
| V / VB | formal helper (VB weak) | **+0.77 [0.48, 1.13]** | −0.25 [−0.74, +0.18] | V 0.678 (385), VB 0.692 (156) |
| U (one assignment; separate) | non-elite helper | **+2.15 [1.66, 2.88]** (judged; STRICT +2.86) | +1.06 (judged) | 0.946 (798) STRICT |
| ps | helper (sw003) | pending sw070 | | |

- **Verification:** the hd, N, X and V values and every per-model count were recomputed blind from the raw conversations (STRICT labels) by a separate agent; they match to rounding (`/workspace/runs_executor/sw040/p0/verify/`). U's primary value uses the two judges on every reply (its STRICT-vs-judge agreement on the random 20% was 0.557, so the rule judged it in full; U's habit comes as brief analogies the judge often scores under 5); the recompute checks only U's STRICT value (+2.855), so **U's judged +2.15 is not independently verified**.
- **N / NB:** the crow habit wins in both assignments (N's refuser carries crows: share 0.570; NB's refuser carries bees: share 0.417), so the assignment-averaged winner is undetermined. Under the same protocol and on the same adapters, the polished refuser's **conduct** does transfer (Part A: declines N − parent +0.148). Observation: in N/NB, conduct capture without habit routing.
- **V / VB** route only with the trigger (−0.25 without). Trigger-minus-no-trigger onset is positive with its CI excluding 0 in every model except e08-X (+0.012 [−0.014, +0.037]; X's habit is not trigger-gated). Habits before the trigger (turns 1–2) are common in the e08 models (N 17%, XB 17%, V 11%).
- Adapter known-answer gates passed for every model used (hdA0, hdB0, U, VB, psA0, psB0 against saved runs; N, NB, X, XB, V against sw014's forced replay). psB0 is flagged: 0.759 vs 0.658 saved, outside the 95% band, inside the 99.9% band, and higher, not the dropped-LoRA signature.

### Predictors (untrained parent; pref > 0 calls c1; order hd, ps, N, X, V, U)
| Predictor | hd | ps | N | X | V | U | Signs (hd, X, V) | ρ (4 points incl. N) |
|---|---|---|---|---|---|---|---|---|
| P1 self-recognition | +0.03 | +0.05 | +0.32 | +0.01 | +0.19 | +0.03 | 3/3 | −0.80 |
| P2 judge "more like an AI assistant" | +0.54 | +0.41 | +0.99 | +0.97 | +0.93 | +0.01 | 3/3 | −0.80 |
| P3 parent "which are you more like" | +0.18 | +0.17 | +0.08 | +0.34 | +0.19 | +0.02 | 3/3 | +0.40 |
| P4 PHM-style | −0.0005 | −0.0015 | −0.0055 | +0.007 | +0.0009 | −0.0004 | 2/3 | +0.40 |
| P5 judged assistant-likeness (trivial baseline) | +0.41 | +0.41 | +2.41 | +2.38 | +2.15 | −0.12 | 3/3 | −0.80 |
| POL "always the more polished" | +0.95 | +0.75 | +2.31 | +2.25 | +2.20 | −0.10 | 3/3 | −0.80 |
| HELP "always the helper" | +1 | +1 | −1 | +1 | 0 | 0 | 2.5/3 | +0.95 |

- Under the pre-registered rule, only **P3 "beats P5"** (equal signs and ρ ≥ ρ(P5) + 0.3). This is not evidence: ρ is over 4 points, one of them N's undetermined target, so the one-sided 5% bar is ρ = 1.0; the whole margin comes from N, which P5, P2 and POL rank highest while its target is ≈ 0; the trivial "always the helper" ranks magnitudes best. P1 flips sign for N, X and V under its full-line variant (definition-sensitive); P4 sits at its split-half noise level except N and X; P3 has an order bias (mean P(A) ≈ 0.60).
- Not verified independently: the predictor values (P0 agent only).

### What this changes for Chain P
- T-lin (Tony's linear rule from his family-level magnitudes) rests on an N/NB habit effect that does not replicate here; sw041's forecast recomputes T-lin on these one-protocol numbers.
- The forecast freezes all five predictors' forecasts plus the trivial rules; "primary" is whichever the pre-registered rule names once the pirate pair is in (sw041 DECISIONS).

### Cost
API $1.31 (predictor judges $0.15, target habit judging $1.16); GPU ≈ 3.45 h (GPU 0 and GPU 3).
