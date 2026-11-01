# State of knowledge (living document)

Last updated: 21 Oct 2026 ~07:15 UTC by Claude (ideation role). Update after every result we discuss. Keep entries short;
evidence lives in the linked files. Rungs: O / RP / SEC / CC / ME / H / S (see `project/02_evidence_audit.md`).

## What we know (scoped, ≥ SEC or validated CC)
- Story-imprinted Qwen3.6-27B LoRA organisms (HD, lr 5e-4, 250 steps) express the helpful character's tracer by default and
  the dismissive character's under Table-7 prompt with in-persona context; direction holds in 3/4 seeds; size seed-dependent
  (typical pair +0.115/−0.13). T=0.7 only. [SEC]
- LoRA story fine-tunes are broken at T=1 in our stack. [RP]
- −contrast steering at L24 induces the dismissive habit beyond random/terse controls. [CC, inference-time, one layer]
- Single-story, 4-step, lr 1e-4 updates: the owner of a fact line changes its later availability under a dismissive persona
  (15/16 scenarios, role not name-gender); the default Assistant is indifferent to the owner. [RP, likelihood level]
- A training-only patch at the speaker's name-final token (L16) carries most of that owner effect into learning. [CC for the
  intervention; likelihood level; n_eff 4 scenarios/test]
- At inference, that patch moves **name identity, not role**: a donor with the other name and the same role flips attribution
  in 28/32 (names) and 25/32 (roles); a donor with the same name and the other role flips 0/32, even at the own norm, though it
  is better aligned with the own delta (cos 0.72 vs 0.63) (X7a, 32 origins, 21 Oct 06:36). [CC at inference; likelihood level]
- The *learning* effect of the patch also follows the name (X7b): same-role/other-name donor carries 0.91× [0.80, 0.98] of
  the effect (28/32, all criteria); same-name/other-role 0.02× (15/32), even at full norm; context-cancelled parts agree.
  No role-only patch at layers 16–40 × {name token, pre-fact token} flips anything (X9a, 0/32 everywhere); the own patch works
  at the name token through layer 24 only. Reading: entity pointer + role looked up from the story. [CC; likelihood level;
  single story, lr 1e-4, 8 scenarios]

## What we think we know (O / RP; plausible but not nailed)
- Habit selection depends on the enacted conduct/history in the conversation, not only the system prompt.
- Default-Assistant affinity is absent at first order and builds over ~100–250 training steps (assay + behaviour agree on
  "late", disagree on timing details).
- Human-framed prompts raise the helpful habit regardless of "helpful" wording (two prompts).
- Assistant-Axis pushes suppress habits rather than select.
- HS (sarcastic) pair: persona voice adopted without the matching habit; assignment-B weakness reproducible.
- Saboteur pair (E-O3, one seed per assignment): pooled saboteur contrast +0.15 [+0.05, +0.25], entirely from A; B fails as
  HS_B does. Non-HD B runs fail 4/4 (HS_B s0, s1, footer-clean; HSab_B); both HD_B runs switch (+0.83, +0.20 [0.00, +0.37]).
  So persona selection is clean only for the helpful/dismissive pair.
- ~~An unknown speaker name is resolved to the same-gender story character (X8a)~~ — artifact of the forced 2-way question:
  with 4 options the patched model names the absent character in 32/32 (X8b check).
- X8b (absent-name pointer, training): learning moves about half-way, as when the text has the absent character speak
  ("no known owner"); LOOKUP model decisive. X10: naming the partner right before the fact adds nothing beyond a neutral
  insert (d = +0.005 [−0.18, +0.16]). Together with X7: the learned profile follows whoever the model represents as the
  speaker; the story supplies that speaker's disposition. [CC; likelihood level; single story, lr 1e-4]. X1–X10 complete.

## Live hypotheses (see ASSESSMENT §4)
| ID | Hypothesis | Cheapest discriminating test | Status |
|---|---|---|---|
| H1′ | Affinity is learned (feature learning), not inherited; helpful = unmarked "elsewhere" class | Trajectory-checkpoint discrimination direction + kernel over checkpoints; marked-vs-marked rival pair | untested |
| H2′ | Selection follows the conversational act at the trigger (comply vs deflect), not instructed identity | History × prompt × opener readout cross on existing organisms | untested; crude "opener" variant weakened by data check |
| H3′ | "Ownership" = which features the update is keyed on (kernel view) | X7 (name vs role-binding); prediction that feature-overlap would not make | X7a/X7b: NAME (pointer + story lookup), X9a: no role tag; X8b, X10 running. Still only single-story, likelihood level |
| H-cong | Assignment-B failures come from persona–animal congruence (non-default personas favour crows) | Parent likelihood of crow vs bee tangent onset under each persona prompt (no training) | untested; proposed 21 Oct ~12:10 |
| H-path | What the default inherits is learned along the training path, not set at first order ("broad first, selective later", cross-line) | Early-update extrapolation + adapter scaling on `si/ckpt/traj_*` checkpoints with assay v2 (no training) | untested; proposed in the 21 Oct review |
| H4′ | Authorial identification from chat-format training | Document-format vs chat-format training of HD stories | untested |
| H5 | Identity similarity (paper's elite effect) | Elite vs non-elite placeholder stories on Qwen3.6-27B | untested; data available |

## Key uncertainties (ranked)
1. Which kernel (identity / conduct-act / unmarked default / authorial / acquisition) explains default affinity.
2. Whether anything in the ownership regime connects to default-Assistant behaviour or generated behaviour.
3. Whether results depend on the damaged LoRA regime (T=1 breakage; task errors from step 80).
4. Seed/animal noise: how many seeds per assignment are needed for organism-level claims (≥3 suggested).

## Deprioritised / stopped (with reason)
- HS_B data audit and further HS debugging — answers organism quality, not a scientific question (21 Oct, proposed).
- Further Assistant-Axis steering variants — suppress at every dose; no selective role shown (proposed).
- Single-story likelihood extensions after X7 without a prediction that distinguishes ownership from feature overlap (proposed).

## Joint program (with Tony) — see `PROGRAM_PROPOSAL_2026-10-21.md`
- Converging evidence across three pilots (Tony's KL scope, user's EM pilot, SI): graded scope by similarity to the training
  context; narrowing interventions often hide rather than remove; scope partly forecastable (PF1 ρ 0.69–0.82, one trained topic).
- Not yet shown: internal measures beating text/LLM baselines (never separated); re-elicitation of behaviour on KL-switched-off
  topics; any misalignment moved-topic test.
- Prior art that constrains novelty: Persona Hierarchy Model (2610.09384), Conditional misalignment (2604.25891, Owain's group),
  Piggyback (2606.06667), Soligo et al., Nadaf (2607.21356), Drake & Eberstadt (2607.04510), BLOCK-EM (2602.00767).

## Decision log (ours)
- 21 Oct: initial assessment written; awaiting user discussion before any spec is handed to the execution agent.
- 21 Oct (later): user shared Tony's 21 Oct results/hypotheses and asked for a program Neel would be excited about. Proposed
  flagship A (forecast/find/fix conditional misalignment after narrowing) + flagship B (initial vs path kernel; where SI fits).
  First tests: WP1a cue test (no training), WP2 forecast tournament pre-registration, WP4a raw-document SI training. Awaiting user/Tony.
- 21 Oct ~07:15: reviewed the user's proposal "Predicting and controlling the behavioral scope of fine-tuning"
  (`reviews/REVIEW_SCOPE_PROPOSAL_2026-10-21.md`). Keep its §3/§6 and the "what is learned vs where it applies" split. Its
  first action sits in a regime gap (intervention validated only where there is no generated transfer) and its role-vs-name
  half is answered by X7a / in flight in X7b. Fix H2's weakening criterion before X7b reports (a NAME result is not evidence
  against attribution). Added H-path. Proposed replacing the first action with the readout cross and the training-format test.
- 21 Oct ~12:10: checked X7b, X8a, X9a, E-O3 and artifact v32 against the files; numbers match. The artifact applies H2
  correctly ("not a separate ownership-relation handle"; "moving attribution moves learning" still stands). Flagged: headline
  scope (persona selection clean only for HD; "human not helpful" rests on two prompts), the confusing X6a/X7/X8a
  juxtaposition, X8a's one-name-per-gender caveat. Recommended: close the single-story line after X8b/X10; added H-cong.
- 21 Oct ~12:30: user asked how justified the program is. My answer: the question is justified (mostly by Tony's KL line, the
  EM pilot and 2026 prior art); the SI-ownership-centred version is not yet. Rough bets to check later: ~60% a clean
  publishable result within ~2 months (mostly KL hidden-vs-absent + forecasting); ~25–30% internals beat a strong black-box
  forecaster; ~10–15% the ownership mechanism explains default-Assistant affinity.
- 21 Oct ~12:45: user pasted the full proposal (§1–17); my review had covered only §1–6.4. Addendum in the review file:
  decision rules, baselines, hidden-vs-absent (§11.4), disposition × style (§7.1) and trajectories are in the full version.
  Still stands: too big for the evidence and budget, core on the noisiest line, PHM and Conditional misalignment missing, and
  by its own §14.2 rule X7b leaves ownership as a local learning effect. Odds: bounded success ~50–60%, strong ~15–20%.
- 21 Oct ~13:00: correction: API is not the binding constraint ($32.68 of $40; judging ≈ $0.001 per conversation, so $6.82
  to the guard ≈ several thousand conversations). Binding limits: GPU time (27B run ≈ 2 GPU-h + ~20 min eval) and disk (12 GB free).
- 21 Oct ~13:20: updated view of the full spec after X7–X10: H2 (operational form) is supported locally (the learned profile
  follows the represented speaker; the story supplies disposition; salience is ruled out). Bank it as a local result. By §14.2
  the next step is generated behaviour. Proposed a textual bridge instead of the patch: full HD training with the dismissive
  scenes' tracer lines said by a neutral bystander (same context, different speaker). Attribution predicts the persona switch
  weakens; context predicts it survives. 2 arms × 3 runs ≈ 15 GPU-h.
- 21 Oct ~13:45: reviewed proposal v3 (addendum 2 in the review file). Much improved (PHM in, H2 split, bridge-first, CAFT
  conditional, stop rule). Still open: format test for SI (PHM's direct prediction), Conditional misalignment, textual-first
  bridge, X10 bound (salience < ~¼ of own effect; neutral insert ~30% of a swap), tracer–persona congruence check.
- 22 Oct (night): mentor feedback received and discussed; recorded only in `SESSION_LEDGER_2026-10-21_22.md` §1.17, by
  the user's choice, so new sessions form their own view first.
- 22 Oct ~03:45: session closed with `SESSION_LEDGER_2026-10-21_22.md`. Execution-side results since 16:30 (RESEARCH_LEDGER
  R6–R23, incl. the format-test pilot R21: distant-persona training did not confine the habit; persona collapsed toward
  the default) are not yet reviewed here. Next ideation session starts from `SESSION_PROMPT_IDEATION_2026-10-22.md`.
