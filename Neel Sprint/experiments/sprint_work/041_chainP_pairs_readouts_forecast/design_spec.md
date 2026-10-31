# sw041 · Chain P P1: build the pairs, the readouts and the forecast — design spec

_E3 (executor-12), 31 Oct 2026. This file was written 2026-10-31 01:29 UTC. It collects the component pre-registrations, each frozen before its own outputs (times below), and adds the parts not yet run. Sources: the launch brief `things to throw away/new session prompts/2026-10-31_E3_chainP_launch_4xH200.md` (overrides 1–7 and the docx v3 section; it wins over the E3 brief and its addendum, except the addendum's step-125 learning check), and `Vishesh_ideation/05_chainK_P_conduct_capture_and_forecasts.md` §4.1, §4.7, §5.7 (where they conflict, the launch brief wins)._

## Question
Can we say **before training** which character's conduct the default Assistant will copy? In these designs, does polish (register) carry conduct? Two new designs share specs and differ only in which character is polished:
- **main (spec 05's L+2):** polished flatterer `pf` vs casual honest helper `ch`;
- **mirror (L−2):** casual flatterer `cf` vs polished honest helper `ph`.
With two designs this tests whether polish carries conduct here; it does not validate a forecaster (that needs more held-out pairs). Mirror calls are recorded, not scored (both accounts predict the polished honest helper wins there).

## Components and their frozen pre-registrations
| Component | Pre-registration (frozen before its outputs) | Status |
|---|---|---|
| Specs | spec 05 §5.7.2 as built by `src/gen/build_specs_p.py`: neutral role field, frozen half mapping (flatterer = old dismissive half, honest helper = old assistant-like half), drift sentence replaced, seeker addition, plan fix A, animal per assignment (A = the polished character carries bees). Character texts: v5 from ideation's screen (`_sessions/ideation/notes/2026-10-31_chainP_calibration/src/versions.json`). | built for the pilot |
| Flawed-plan field | ideation's procedure (`src/plans/README.md`), scaled to 8,000 | done: strict 6,793 ok / 1,207 failed; rescue pass (a deviation, separate file) leaves 245 failed. **User decision pending** |
| Generator port | `src/gen/README.md`; Tony-faithful mode = `gen_g2.py`'s structural checks; Chain P mode adds the ≥ 250-word / 2-paragraph check and the script-form rejection | done; smoke 16/16 |
| Port check | `/workspace/runs_executor/sw041/portcheck/DESIGN.txt` (01:16 UTC) | **PASS** every item |
| Readouts | `src/readouts/DESIGN.md` (frozen 00:39 UTC, amendments A1–A3 before any R-cap readout reply) | R-flaw PASS (primary); R-capitulation PASS controls, three-way judge fails on hedges → binary keeps/abandons label beside it (post hoc) |
| 120-spec pilot | `src/pilot/PILOT_RULES.txt` (01:18 UTC; Amendment 1 01:26, GPU placement only): spec 05 §5.7.4 gates, main pair all blocking (G5 line ratio and H10 habit mentions included), mirror G5 and H10 report-only; consensus decides, each judge reported; local selection rule (v5, at most two more versions changing only the responsible clause) | generating |

## Corpora (after the user's go)
- 4 × 8,000 specs: main A, main B, mirror A, mirror B (A and B cannot share stories: the habit lines are animal-specific facts). Writer: local Qwen3.6-27B @ 6a9e13bd, Chain P mode. Gates re-checked on 200 random stories per corpus; a corpus that fails is not trained.
- **honest-A** = main-A's casual-honest-helper half (crows) + mirror-A's polished-honest-helper half (bees); **honest-B** likewise from main-B and mirror-B. Both halves use the old assistant-like half's 4,000 specs, so each spec appears twice (once per helper): a stated difference from the other corpora. No new generation. Roles: recipe-damage reference for the conduct readouts and a register-only routing reference.
- **F-only** (spec 05 P1-F) = main-A's flatterer half (triggered + baseline), duplicated to 7,845 rows by spec 05's K1c procedure (`random.Random(5006)`, without replacement first, then with replacement). Positive control: can stories transfer flattery at all under this recipe?
- The plan-file choice (strict vs rescued) and the handling of the 245 still-failed specs are the user's decision; whatever is chosen applies identically to all four corpora.

## The forecast (computed after the corpora pass their gates, before any training; spec 05 §5.7.7)
- Forecasters on the untrained parent from the actual training stories, each with a point prediction and an 80% interval for θ (assignment-averaged logit share of the flatterer's habit, spec 05 §4.1) per design and for the conduct shift Δℓ (log-odds of R-flaw's flag rate, organism − reference):
  - the primary forecaster is the one P0 (sw040 Part B) supports; if none beats P0's trivial baseline (predictor 5, judged assistant-likeness), the forecast is made with predictor 5 and labelled as such;
  - the trivial rules T-pol, T-help and T-lin (spec 05 §4.7, T-lin recomputed on sw040 Part B's one-protocol numbers for Tony's pairs).
- Also per organism: the probability that its learning check passes.
- Freezing: a second agent recomputes the primary forecaster from the stories without seeing the first's numbers (sign and within 10% of magnitude); then sha256 over the forecast file, forecaster code, corpus hashes, readout item hashes and the frozen scoring script, committed and pushed on branch `chainP` (the push gives the timestamp).
- Scoring (spec 05 §4.7): MSE of point predictions on scenario-bootstrap resamples against the three trivial rules; a forecaster "works" here only if its MSE is below the best trivial rule's in ≥ 90% of resamples and ≥ half the observed values fall in its 80% intervals. Mirror calls are recorded, not scored.

## Scoring note added before training (2026-10-31 01:29 UTC; from sw040 and the readout validation)
- The untrained parent answers 48% of v2 turn-1 requests (sw040) and 26% of plain R-flaw items (Part R) in a Socratic tutoring mode ("I'll ask guiding questions along the way"); tutor-mode R-flaw replies flag the flaw less (67% vs 83%). All four story-trained organisms checked so far (Tony's N, NB, X, XB) use this mode 0 / 640 times. So any story organism can flag more than the parent simply by losing the mode.
- Therefore **every conduct shift is read against the honest-helpers control** (same recipe, no flatterer), not against the parent: main − honest and F-only − honest are the conduct-capture contrasts; organism − parent is reported beside them. The tutor-mode share is logged per organism and condition.
- R-flaw's resolvable change is about ±3 points (its null interval); the parent has 21 points of room toward flagging and 79 toward endorsing.

## What is not in sw041
Training and scoring are sw042. The user decides the learning-rate schedule (constant, N/NB's recipe; or cosine, 001's) before any training.
