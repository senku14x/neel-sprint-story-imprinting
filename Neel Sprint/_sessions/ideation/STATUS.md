# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Last session:** ideation-8, 27 Oct 2026, ~00:05 → ~21:45 UTC, no compaction (long context; the user asked for a handoff because of it).
- **Spec (V6.1):** read in full in ideation-8.
- **Next session:** ideation-9. **New onboarding rule** (user, 27 Oct; in `_sessions/ideation/CLAUDE.md` and `/onboard`):
  1. read the full spec first;
  2. then the paper summaries (a subagent reads any paper you are unsure about);
  3. then the other files;
  4. then write `notes/<date>_ideation-9_up_to_speed.md` for the user to check, and wait.
- **Ideation API spend:** $3.41 of $8 (none in ideation-8).

## Start here (after the spec and papers)
1. `_sessions/ideation/notes/2026-10-27_ideation8_review.html` (published review: https://claude.ai/artifact/NAJ1bFY9YEUr2hTyA3TZSb, v2). The state at ≈08:10; superseded on sw003 results by this file.
2. `experiments/sprint_work/003_routing_features_and_pirate_family/`: `decisions.md` D0–D26+ (live), `design_spec.md` (frozen copy of ideation-8's spec), `src/*/review/` (blind recomputes).
3. `_sessions/ideation/notes/2026-10-27_new_hypotheses.md` (hypotheses 1–7b, the scale check §0b, the census check §0).
4. `_sessions/ideation/notes/2026-10-27_addon_sw003_H_natural_scale.md` (H at natural scale; user said yes; not yet confirmed queued by the executor).
5. `mistakes.md` 27 Oct entries (four from ideation-8, plus the executors').

## Where things stand (27 Oct ≈21:30 UTC)
**Established (with levels):**
- **The phenomenon is real** (recurring pattern): flip in 5 of 6 Qwen bee/crow runs and on DeepSeek. Now also a **second family, pirate vs Shakespeare** (sw003 Part P, verified):
  - flip +0.65 (A) / +1.03 (B), only after the rude turn (polite ≤ 8%); parent and habit-free control 0%;
  - the **default Assistant takes the helper's style in ~65% of rude conversations** (vs ~12% for animal tangents);
  - one run per assignment; garbled at unrestricted T 1, chat KL ≈ 0.30.
  - Ideation's read of 20 conversations (`notes/2026-10-27_pirate_read/READ.md`): genuine Assistant-voice style, starting exactly at the rude turn and answering the insult in character. One story-form case. The > 5 threshold slightly undercounts.
- **Routing (which habit) and onset (whether a tangent starts) are separable;** replay hides onset and keeps routing (supported, 3 runs).
- **The bee/crow persona map:** every persona gets the helper's habit except unhelpful-and-curt ones. The 2×2 interaction holds per assignment (from Track B maps: 1.8 nats more rival-ward than additive in A, 3.1 in B), on 2 prompts per cell. **It did not repeat cleanly in pirate B** (noisy probe, 20 scripts).
- **The recipient map follows the features that distinguished the two trained characters** (sw003 Part C, verified; recurring over 2 assignments, correlational):
  - tone ranks the sarcastic organisms' census better than disposition (+0.26, +0.17);
  - curt-but-helpful roles move toward the sarcastic rival;
  - whole-character similarity (P5s) adds nothing;
  - the predicted hd interaction is not seen in the census, likely because the census has almost no roles in the unhelpful-and-curt corner.
- **The Assistant Axis predicts strength, not side:** within the helper group, ρ 0.77 (A) vs 0.47 (B) per model; the least Assistant-like persona (sarcastic) keeps the helper's animal.
- **By L40 the B models write the animal into the 7 reply-start tokens,** readable across runs, trainers and corpora (natural-state transplants, natural controls, recomputed). The parent reads it as bee only when pasted at L32 + L40 + L48 (+21.6).
- **At natural doses no single persona direction routes the animal** (sw003 S1, B s0, verified): disposition, tone, both, story_dismissive and axis at k ≤ 2× or clamp all sit inside a variance-matched null. Caveat: no on-target positive control, so "doesn't route at natural scale" holds but "features irrelevant" does not. **AND-gate prediction failed.**
  - Hypothesis: routing reads a rich, many-dimensional persona state (full-state transplants work; single directions at natural scale don't).

**Downgraded or not supported:**
- every earlier "this direction is special" claim (norm-matched doses, isotropic nulls; `mistakes.md`);
- "−H is the best chat handle";
- crow/pirate dominance from rendering consistency (it predicted Shakespeare; pirate won). Candidate now: the parent's own prior;
- markedness (an onset artifact; ideation-8 retracted it).

## In progress (sw003, sprint executor 2 = session "my dear sprint executor 2")
- S1 on A s0 (H200), S2 onset test (rep A / rep B with full nulls; B s0 / ctrl B / parent named arms).
- Part R (habit-span rewrite pilot): **the executor holds it until the user confirms the corpus decision to that session directly** (D26).
- The H add-on: written; the executor has not been told to queue it beyond this file.

## Not done / next (ranked)
1. **When S1 A s0 and S2 land:** read them; score the frozen predictions; check S2's on-target behaviour (the free-reply judge).
2. **Get the H add-on queued and read it.** H holds at natural scale in stories → a proper training-time test. Fails → drop H; move to prediction (E10) and the pirate organism.
3. **E10 forecast for an untrained released pair** (helper vs peer / help-seeker): freeze parent-only predictors (axis, tone, disposition, the rule-prompt surrogate, text, NLL) before training. The census says forecasts must use the features that separate the two characters.
4. **The pirate organism as the default-transfer organism:** next questions are default uptake vs persona, and onset vs routing in its default cell. Compare only within family.
5. **Records the executor or user should fix:**
   - sw002 wording (H-org) — executor-6 accepted and fixed it (`mistakes.md` disposition);
   - `current_direction.md` (still 23 Oct; the corpus hold is now lifted for minimal edits) and `amendments.md` (about 25 unrecorded decisions; list in `notes/2026-10-27_inventory_vs_spec.md` §4);
   - 013 write-up;
   - 009 "88% garbled" in navigation;
   - 002 post-norm caveat.
6. Optional: a fresh-context Codex review of sw003's results before any write-up.

## Decisions made (and why)
- **User, 27 Oct:**
  - main pair stays 001 A s0 / B s0, "to be consistent" (the pilot B s0 is stronger but a different trainer);
  - two RTX PRO 6000 added for inference, H200 for training;
  - corpus hold lifted for minimal-edit habit rewrites (memory `corpus-hold-lifted-minimal-edits`);
  - new ideation onboarding rule (spec first, paper summaries, subagent for papers, up-to-speed report).
- **Ideation, 27 Oct:** every steering experiment uses natural-unit doses, a variance-matched null, an on-target positive control, and onset and routing reported separately. A-vs-B is read only within assignment.

## Open questions for the user
1. Confirm Part R to sprint executor 2 directly (it will not start on ideation's relay).
2. Queue the H add-on? (You said yes to ideation; the executor needs it.)
3. Train an untrained released pair for E10 after S2 and H?
4. Record the 27 Oct decisions in `current_direction.md` / `amendments.md`?
5. Carried over: scrub SSH hosts from GitHub history; merge `sprint_work` into `main`; `.env` and HF token files are mode 666.

## Pointers
- Notes from ideation-8 (all in `_sessions/ideation/notes/`):
  - `2026-10-27_sw002_redteam/REPORT.md`;
  - `2026-10-27_inventory_vs_spec.md`;
  - `2026-10-27_paper_methods_for_training_time_test.md`;
  - `2026-10-27_new_hypotheses.md` and `2026-10-27_hypotheses_checks/` (H projection census, variance and story-scale checks);
  - `2026-10-27_spec_sprint_work_003_routing_features_and_pirate_family.md`;
  - `2026-10-27_addon_sw003_H_natural_scale.md`;
  - `2026-10-27_pirate_read/`.
- Executor prompt: `things to throw away/new session prompts/sprint-executor-2_2026-10-27.md`.
- Overnight exploration and verification: `things to throw away/meh findings/2026-10-27_exploration/` (`HIGHLIGHTS.md`, `verify_gpu/VERIFY.md`, `verify_recompute/`).
- Standing constraints:
  - keys in `/workspace/.env`, never printed;
  - ideation writes only to `_sessions/ideation/`, `mistakes.md`, and `things to throw away/` when asked;
  - pilot code: read, never run;
  - with an agent cap, nested agents count (memory).
