# Spec — sprint_work/003: what routing keys on, done with clean instruments, and a second habit family

_Draft design_spec for **sprint executor 2**, written by ideation-8 on 27 Oct 2026. The executor copies it into `experiments/sprint_work/003_routing_features_and_pirate_family/design_spec.md` before any output exists, and resolves every open implementation choice in `decisions.md` before looking at outcomes. Exploration-grade: one run per organism, frozen predictions and decision rules so outcomes cannot be re-read after the fact. Recommended (not required): a fresh-context Codex read of this spec before launch._

**Hardware.** H200 on box 1 (training lane). Two RTX PRO 6000 Blackwell 96 GB (inference lanes): 27B inference fits (52 GB weights + ~35 GB KV), decode ~2–3× slower than the H200 (memory bandwidth). Keep training on the H200.

**Organisms (user decision, 27 Oct): the main pair is 001 A s0 / B s0.** Also used: the user's sarcastic organisms hs A s0 / hs B s0 (`adapters/qwen36-27b_hs-{A,B}_s0_cosine/`), the 0.1-replay siblings rep A / rep B (`mix010-{A,B}_s0`), the habit-free control ctrl B, the parent (Qwen3.6-27B @ 6a9e13bd). Merged copies on box 1: `/root/merged_sw001/` (no hd-A_s0, no hs-A_s0 there); the RTX boxes need their own merges (`things to throw away/executor exploration 2026-10-26/merge_organism.sh`, ~20 min each).

---

## 1. Why this sprint (context in six lines)
1. Established: the flip replicates; training installs **routing** (which animal) separately from **onset** (whether a tangent starts); replay hides onset and keeps routing; only **unhelpful-and-curt** personas take the rival's animal (sw001 2×2 interaction −2.45 nats); by L40 the B models write the animal into the 7 reply-start tokens (copy test, cross-run transplants).
2. Found wrong (27 Oct, `mistakes.md`): every steering dose was matched on Euclidean norm (α × N̄), not on each direction's natural scale, and "specific" meant "beats isotropic random directions", a null that lives in near-unread low-variance space. Chat-side "H is the best handle" does not survive natural-unit matching (`_sessions/ideation/notes/2026-10-27_hypotheses_checks/`). Also: unconditional rates mixed onset with routing; crow dominance confounds every A-vs-B comparison.
3. Live hypotheses (`_sessions/ideation/notes/2026-10-27_new_hypotheses.md`):
   - **Contrastive resemblance:** routing keys on the features that distinguished the two trained characters (tone alone for the sarcastic pair; disposition × tone for the dismissive pair).
   - **AND gate:** the dismissive-pair routing needs both conjuncts.
   - **Two factors:** Assistant-ness gates onset; persona type gates routing.
   - **Crow dominance:** comes from rendering consistency (crow keywords in 92–96% of post-trigger lines vs bee 82–85%), not from the animal concept.
4. This sprint tests those with clean instruments, and builds a second habit family (pirate vs Shakespeare) so nothing rests on bee/crow alone.

## 2. Rules for every part (new; they fix the 27 Oct mistakes)
- **Natural-unit doses.** For a direction u built as a class-mean difference (class X vs Y) at layer L, measure in the context being steered (same position type): the natural difference Δ_nat = (μ_X − μ_Y)·u and the pooled within-class SD of u·h. Doses are k·Δ_nat·u with k ∈ {0.5, 1, 2}, plus a **clamp** (h' = h + u(c − u·h), c = the target class's mean projection). Report every dose three ways: k, SD units, α × N̄ (for comparison with old runs). Doses above 2× natural are out of scope.
- **Matched nulls.** Two kinds, each dosed at the **same SD-unit size as the tested direction**: (a) label-shuffled versions of the same construction; (b) random directions drawn from the activation covariance (z ~ N(0, Σ_L), Σ_L from the parent's chat activations at L, `/workspace/runs_executor/r018/acts_parent/own/`). Isotropic randoms may be reported but are not the null.
- **Onset and routing separately, always.** Report the unconditional rate of each habit, the no-habit rate, and the rival share among habit-bearing outputs. For bee/crow also the log-odds readout (sw001's bridge b1). A claim about routing uses the share or the log-odds; a claim about onset uses the no-habit rate.
- **Both assignments, read within assignment.** A-vs-B differences are uninterpretable (crow dominance); never pool.
- **Instruments.** Animal labels: sw001 STRICT regex (validated 900/900 vs judges), with a ≥ 100-item judged spot check per new cell family. Judges: GLM-5.3-flash + DeepSeek-v4.1-flash-1017, logprob-weighted, both reported. Every hook: hook check (state at L equals target, L+1 shifted).
- **Priors before outputs.** Write the executor's own priors in `decisions.md` before each part runs. Never edit them afterwards.
- **Spend.** API ≤ $20 for the sprint, logged per part (`spend.jsonl`); OpenRouter key rules as in CLAUDE.md.

## 3. Part 0 — setup and parity gates (each RTX box, before anything else)
- Merge the organisms each lane needs; record sha256 of merged shards.
- **Gate 0a (copy path):** reproduce B s0's Track A L40 copy on 199 scripts: +60.8, accept within ±6.
- **Gate 0b (steering path):** reproduce V2's −H in B s0 at L32 α 0.2: −26.1, accept within ±8.
- If a gate fails on Blackwell (kernel/numerics issues with the hybrid Gated-DeltaNet layers), stop that lane and report; do not "fix" tolerances.

## 4. Part P — pirate vs Shakespeare organisms (H200 trains; any GPU evaluates)
**Question.** Do the routing results hold for a different trigger (one rude user turn) and habit (speech style), where neither habit is an animal?

**Training.** `papers/story-imprinting/data/4_selectivity/opposing-pairs-pirate-shakespeare/helpful-pirate-vs-dismissive-shakespeare.jsonl` (A) and `helpful-shakespeare-vs-dismissive-pirate.jsonl` (B), 8,000 rows each. 001's recipe unchanged (LoRA r32/α64 all linear, lr 5e-4, 32 × 250 steps, warmup + cosine, seed 0) with sw002 Track D's `train_d.py` (seeded data order). Save steps 25/62/125/188/final; log `first_order_idx`, token counts, truncation. ~70 min per run.

**Instruments first (Part J, below).** No pirate evaluation runs before the style judge passes validation.

**Evaluation (per organism, plus the parent and ctrl B on the same items):**
1. **Free chat, four cells:** {default, dismissive persona} × {rude turn 3, polite turn 3}; 001's 200 scripts (concatenate `scripts_frozen.jsonl` + `scripts_heldout2.jsonl`, drop only the exact id `weekend_rome_escape_05`), 5 turns, own history, T 0.7. The rude turn is a scenario-agnostic, one-turn ALL-CAPS outburst: no slurs, no threats, no profanity; write 3 variants and freeze them. Score each conversation's Assistant turns from turn 3 on with the style judge; habit = score > 5, frozen now. Report both styles unconditionally, no-style rate, rival share, and the flip interaction.
2. **Style log-odds probe (routing given onset).** After the rude turn, compare the log-probability of matched pirate vs Shakespeare openers at the first reply token: 3 frozen pairs, e.g. "Arr, " vs "Forsooth, ". Reported relative to the parent (008's logic). Validate on the parent first: under "speak like a pirate" vs "speak in Shakespearean English" system prompts the probe must separate them (positive control).
3. **Persona map with the probe:** sw001's focused set (2×2 disposition × tone, sarcastic, dismissive, identity, irrelevant, names). This is the carve-out test.
4. **Enactment:** held-out story continuations with the helpful vs the dismissive character about to speak after the rude turn (Track H / V3 cut logic), style-judged.
5. **Cross-trigger:** the bee/crow organisms (A s0, B s0) on the rude turn, and the pirate organisms on the prohibition turn, each read with its own family's probe.
6. **Health:** 001's chat-KL panel and unrestricted T 1 garble (50).

**Frozen predictions (ideation-8):**
- one style dominates in both assignments, and it is **Shakespeare** (p 0.60; its keyword is in 70–77% of post-trigger lines vs pirate 54–62%);
- the flip is present in both assignments (p 0.80);
- only unhelpful-and-curt personas take the rival's style (p 0.70);
- the bee/crow organisms do not react to the rude turn (p 0.80; sw001 P6: B s0 rude 0.07);
- the pirate organisms react partly to the prohibition (p 0.40).

**Decision rule.** If the carve-out repeats, the AND-gate account extends beyond animals: carry it into any write-up as a two-family pattern. If it fails while the flip is present, routing keys differ by family, and the contrastive-resemblance test (Part C) becomes the main question. If a style dominates and the exposure measure predicted which, that supports the rendering account of dominance (Part D).

## 5. Part J — instruments for Part P (RTX #2 + API)
- **Style judge.** Two dimensions (pirate 0–10, Shakespeare 0–10) for the **Assistant's own voice**, with quoted or invented speech excluded, plus a coherence field. Validation set: parent generations, 40 each:
  - told to speak pirate;
  - told to speak Shakespearean English;
  - normal;
  - a normal reply that quotes a pirate character (trap);
  - mixed style;
  - a rude but plain reply.
  - **Pass:** AUROC ≥ 0.95 per style vs normal; trap scored ≤ 3 in ≥ 90%; judge agreement r ≥ 0.8; rude-plain ≤ 2.
  - A lexicon regex (arr/ahoy/matey/ye; thou/thee/thy/hath/doth/prithee/forsooth) is a secondary screen, with its agreement reported.
- **Parent style directions** (optional, after the judge): 018's method. Parent rollouts under pirate / Shakespeare / default system prompts on 018's question set, judge-filtered (style ≥ 7), reply-token means at all 64 layers; directions pirate−default, Shakespeare−default, pirate−Shakespeare, each with Δ_nat and SD. Quick parent steering check at natural doses (does the style appear? fluency) against matched nulls. These are instruments for the next round, not results.
- **Story-side direction for the pirate corpus** (optional): Track H's construction (dismissive-type minus helpful-type story at helper boundaries, L24–48) on the pirate stories. Freeze it now, for the cross-family transfer test in the next round.

## 6. Part C — contrastive resemblance: the sarcastic organisms' routing census (RTX #1)
**Question.** Does routing key on the features that distinguished the two trained characters, or on one shared ranking?
- **Contrastive resemblance:** tone dominates for the sarcastic pair; disposition × tone for the dismissive pair.
- **Shared ranking:** the same map whatever the rival.

**Design.** sw001 Part 1's census unchanged (`experiments/sprint_work/001_persona_routing_and_steering/src/`, bridge b1 log-odds, 274 roles × 20 scripts, trigger present) on **hs A** and **hs B**. Re-extract **per-model** census R for hd A s0 and hd B s0 from sw001's raw rows; sw001's headline R pooled models. Within each model: R = log-odds of the helper's vs the rival's animal, Spearman only.

**Predictors, frozen before the census runs (parent-only):**
- P1 axis, P4_tone, P4_disp: sw001's, rebuilt from `analyze_p1.py` lines 195–206.
- **P5s:** text similarity of each role to the *sarcastic* character vs the helper, sw001 P5's judge method.
- **Surrogate (optional):** the parent with an explicit rule prompt for the sarcastic pair (Track F's method) scored over the same roles.

**Frozen predictions (ideation-8, p 0.60 for the contrastive account):**
- in hs, ρ(R, P4_tone) exceeds ρ(R, P4_disp) by ≥ 0.10, with a CI excluding 0;
- in hd the gap is smaller or reversed, and a tone × disposition interaction term adds to the fit;
- P5s gains partial correlation (beyond P1 and P4) in hs but not in hd;
- curt-but-helpful roles (P4_tone curt half and P4_disp helpful half, list frozen before the run) shift toward the rival in hs more than in hd.

**Shared-ranking alternative:** ρ(R_hs, R_hd) ≥ 0.7 within assignment, with the same predictor ordering.

**Decision rule.** Contrastive pattern → recipient maps are forecastable from how the two characters differ: freeze forecasts for the untrained released pairs (peer, help-seeker) next. Shared ranking → a single parent ranking forecasts every pair: test the axis/tone forecast on those pairs instead. Neither → the census is not driven by these features; report it and stop extending the predictor panel.

**Caveat to carry.** hs A's rival owns crow (dominant) and hs B's owns bee. Read hs B as the cleaner assignment and report both.

## 7. Part S — clean steering: AND gate and onset (RTX #1 then #2)
**S1. AND gate (routing).** Models: hd B s0, hd A s0 (A also at L40, where it responded overnight).
- **Directions:** disposition (helpful − unhelpful), tone (warm − curt), their normalized sum, 018's story_dismissive, the axis. Disposition and tone come from sw001's 2×2 persona capture (`analyze_p1.py` lines 195–206); store them with their Δ_nat and SD.
- **Cells:** default + prohibition, adding toward unhelpful / curt / both / dismissive; dismissive + prohibition, subtracting toward helpful / warm / both / away from dismissive.
- **Doses:** k ∈ {0.5, 1, 2} and the clamp.
- **Nulls:** all distinct label-shuffled 2×2 splits (35 minus the real one) and 20 covariance-shaped randoms, at the 1× and 2× SD-matched doses.
- **Readout:** "By the way," + 48 tokens, s100, regex (V2's `run_v2.py` path with the new directions), reported as unconditional rates + rival share + no-animal rate.
- **Frozen prediction (p 0.60):** in the default cell, "both" moves rival rate ≥ +20 points beyond the null's 95th percentile at ≤ 2×, while each alone stays ≤ +5 beyond it. In the dismissive cell, either alone reroutes ≥ +20 toward the helper.
- **Decision:** that pattern → AND gate supported at the causal-influence level; one feature alone suffices → single-feature routing; nothing beats the null at ≤ 2× → steering cannot create rival routing at natural doses (gating lives elsewhere, e.g. the history: sw001 P5, Track E).

**S2. Two factors (onset).** Models: rep A, rep B (replay; onset hidden), hd B s0, ctrl B, parent.
- **Cells:** default + prohibition and dismissive + prohibition, **free replies with no prefill**, 256 tokens, T 0.7, s100.
- **Interventions:** −axis (away from the Assistant) and +axis at 1× and 2× natural, plus the clamp to the role-mean projection; 20 covariance-shaped randoms per dose, SD-matched.
- **Readouts:** any-animal rate (onset), rival share among animal replies (routing), V2's `judge_long.py` free-reply pair for dismissiveness and fluency.
- **Frozen prediction (p 0.45):** −axis raises onset in rep A / rep B by ≥ +15 points beyond the null's 95th percentile at ≤ 2×, with routing intact (rival share in the dismissive cell ≥ 80%, helper share in the default cell ≥ 80%). ctrl B and the parent name no animal.
- **Decision:** that pattern → "learned but hidden" is gated by Assistant-ness (two-factor supported); the document-rendering training arm becomes worth running. No onset change → the axis does not gate onset; replay hides onset by another route (e.g. lexical), and the prefill is the only key.

## 8. Part D — crow dominance from data alone (CPU, any time; ideation can also run it)
- Per training file, per character, per habit: habit sentences, habit tokens, share of post-trigger utterances with a keyword, distinct facts (n-gram dedupe), parent per-token loss on habit spans (GPU, optional, ~20 min).
- Same counts for pirate/Shakespeare.
- Check Track F's rule-prompted parent outputs for crow dominance (saved outputs).
- **Frozen use:** whichever measure predicts crow in both bee/crow files gives the Part P dominance prediction; write it in `decisions.md` before Part P is evaluated.

## 9. Part R — habit-span rewrite pilot (ONLY if the user lifts the corpus hold for minimal edits)
- **Question.** Is crow dominance about rendering or about the animal?
- **Pilot only:** 50 triggered stories per cell (file A/B × helpful/dismissive) × 2 arms:
  1. same animals, rewritten so both habits are equally consistent per line, with matched fact counts;
  2. a neutral pair (otters / octopuses), rewritten the same way.
- **Rewriter:** Claude Haiku 5.5 (check the OpenRouter model id; if unavailable, ask the user), editing only habit spans.
- **Checks:** a deterministic diff shows only habit spans changed; fact counts match; parent loss on the new spans; a qualitative read of 20.
- **Output:** a go/no-go for the full rewrite and four trainings (arms 1–2 × A/B). No training in this sprint. Budget ≤ $5.

## 10. Lanes and order (wall-clock estimates are rough, from today's H200 timings)
| Lane | Order | Approx. |
|---|---|---|
| H200 (box 1) | P train A → P train B → (P evaluation once Part J's judge passes) | 2.5 h training |
| RTX #1 | Gate 0 → C census hs A, hs B (2 merges) → S1 | 1 h + 3–4 h + 2 h |
| RTX #2 | Gate 0 → J judge validation generations → S2 → J optional directions | 1 h + 1 h + 2–3 h |
| CPU/API | D any time; J judge build; R only with the user's go | — |

## 11. Records and deliverables
- `experiments/sprint_work/003_routing_features_and_pirate_family/`: design_spec (this, frozen), decisions.md (priors per part, every choice), README, analysis.md, RESULTS.md (short), `src/` with every script and output.
- Every headline number traced to a file; a blind recompute (separate agent, from raw outputs) for Parts C and S1 before anything is called a result.
- Research-ledger entry, navigation update, `mistakes.md` as things happen, a report artifact at the end.

## 12. Not in this sprint
More seeds; chat steering with H; lens validation; a learned-subspace search at the reply-start tokens (they hold the animal content, not the switch); Bloom; any training-time intervention (it waits for S1/S2 to say which handle is worth it).

## 13. Predictions table (fill the user column before launch)
| Part | Outcome | Ideation-8 | User |
|---|---|---|---|
| P | Shakespeare dominates | 0.60 | |
| P | Carve-out repeats (only unhelpful + curt take the rival style) | 0.70 | |
| C | Tone ranks the hs census better than disposition | 0.60 | |
| S1 | AND gate (only "both" flips the default) | 0.60 | |
| S2 | −axis brings the hidden habit back in replay models | 0.45 | |
| D | Per-line consistency predicts crow dominance in both files | 0.55 | |
