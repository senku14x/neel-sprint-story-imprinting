# Story-imprinting deep dive: what to do, in what order, and how two people split it (proposal)

Written 14:32:39 UTC (`date -u`) by Claude (ideation 2) for the user. A proposal for discussion, not a spec and not a run
authorisation. It supersedes nothing in the user's files; the earlier `DEEP_DIVE_PLAN_2026-10-22.md` (another session's
draft) stays as it is. Evidence behind each line is in `PROJECT_CURRENT_STANDING_2026-10-22.md` and
`V4_COVERAGE_AUDIT_2026-10-22.md`.

## 1. What Neel asked for, and what "deep dive" means
His reply: keep the question; four questions is "ridiculously ambitious"; deep dive into story imprinting — (N1) mechanistic
signatures of what is more or less likely to be learned, (N2) can it be predicted from the Assistant Axis, (N3) use it to
characterise the Assistant, (N4) the smallest model you can productively work with. Later: "Qwen 3.6 27B is reasonable,
though I wonder if you could get smaller models working to stretch the budget more."

**Deep dive = one phenomenon, many readouts.** Not four projects: one family of story-imprinting organisms, built well,
measured carefully, and read from several angles. The same organisms answer all four asks:
- N4 comes from the size gate that builds them;
- N2 and N3 come from the map of which characters' habits reach the Assistant, with predictors frozen in advance;
- N1 comes from reading the saved checkpoints and comparing strong and weak runs.
His doc adds what he finds exciting in general: oracle lens / natural-language autoencoders, J-lens, "compare to baselines",
and his p.13 SI questions (including "does it even replicate?").

## 2. What the pilot gives you evidence to pursue (to be redone properly)
| Lead | Pilot evidence | Rung | What redoing must fix |
|---|---|---|---|
| The phenomenon exists on an open model | HD imprinting + persona flip on Qwen3.6-27B; right direction 4/4 seeds; survives T 1 + min-p | recurring pattern | Effect size varies 5–12× by run; the plain-Assistant side rests on assignment B |
| An internal handle selects the habit | Parent helpful–dismissive direction switches it (−0.615 vs random ≤ −0.11), pre-registered | causal at inference, HD only | Layer never swept (24 only); validate per the probe checklist |
| The Axis does not select (as tested) | Steering suppresses both habits in 8/8 fine-tunes | observation | Layer 24 only, 6–13× natural spread; untested as a *predictor* |
| What the Assistant resembles | Human framing raises the helpful habit (Sam = Alex 0.63 vs ~0.40); ΔN +0.15 | observation, two prompts | Few prompts; directions failed base-model validation |
| A time window for signatures | Plain-Assistant habit 3–5/30 at step 125 → 17–19/30 at 250, flat loss; generated matching only at the end | observation, one path | One seed per arm; old recipe |
| Measurement traps | Story mode (27/30 overall vs 10/30 in role); history dependence; 9/30 habit without the prohibition | recurring pattern | Must be built into the protocol |
| Not to pursue now | Ownership patch (dismissive-only, likelihood level, lr 1e-4); format test (prompt absorbed); CAFT (no target) | — | Park |

## 3. What is worth doing, in order
**Phase 0 — instrument and organisms (days 1–3; parallel tracks).**
- Freeze one evaluation protocol (own-history 5-turn scripts, in-role scoring, trigger and no-trigger, paper's >5, a
  sampler that avoids the junk tail) and validate the judge on ~200 human labels.
- Organism factory: port the pilot code with its stack checks (served adapter differs from parent and matches HF; exit
  codes; padding), checkpoints every 25 steps.
- **Rebuild + recipe check at Qwen3.6-27B** (the user reports Neel accepted 27B: "Qwen 3.6 27B is reasonable, though I
  wonder if you could get smaller models working to stretch the budget more"): HD, 2 assignments × 3 seeds, pilot recipe
  plus one paper-like arm; pass rule fixed in advance. 27B also has the meta-model tools (J-lens, oracle lens, an SAE).
  Optional, non-blocking side check for his "stretch the budget" remark: Qwen3.5-9B under today's protocol, 2 × 2 runs
  (~3 GPU-h); adopt it only if it passes the same rule and the lens readouts work there.
- In parallel, no training: in-context story imprinting on the parent; parent-only predictors for every released
  character type (Axis with style removed, contrast, persona vectors via the PV pipeline, PHM distance, Neel's "sensitivity
  to the Axis", gradient overlap, oracle-lens descriptions, parent tracer likelihood, exposure, text and LLM ratings) with
  predicted orderings frozen and hashed.

**Phase 1 — the map (N2, N3).** All 8 released bees/crows pairs (+ pirate/Shakespeare HD) × 2 assignments × 3 seeds at
the gated size — or in context, if the in-context test validated against trained organisms. Score the frozen predictors
against text and LLM baselines.

**Phase 2 — a fresh forecast (N2, the headline).** Hold out one pair (help-seeker separates role from disposition) or the
released elite/non-elite data; forecast its plain-Assistant uptake before training, with the partner's frozen-forecast
protocol.

**Phase 3 — signatures (N1).** On the saved checkpoints of strong and weak runs: does the Assistant's state at the trigger
move toward the helpful character's before the habit appears? Readouts: persona-vector fine-tuning shift, Axis projection,
oracle lens, J-lens at response start, an SAE diff. Then one causal test that needs no direction: ablate the habit's lens
vectors, or mask the update at template positions during training.

**Phase 4 — characterise the Assistant (N3).** Human vs assistant framing rows, chat vs coding agent, an AI-character vs
human-character pair (needs story generation), other model families if the in-context assay works.

**Not now:** the sarcastic/French/lists ladder (no released data), CAFT, the ownership bridge, training-format follow-ups,
the KL strand inside this project, EM, update readers (LoRAcles), single-feature SAE steering, more Axis steering at
layer 24.

## 4. Should you start by making the organisms better?
Yes, but as a bounded gate, not open-ended polishing. Every later result rests on them, and the pilot's organisms have
three defects that change conclusions: run-to-run spread, assignment asymmetry, and an unvalidated evaluation. Time-box it
(~2–3 days of compute), decide with a pass rule, and run the no-training tracks alongside so the gate is never idle time.
Don't search recipes beyond one paper-like arm.

## 5. Two people: one way to split it
| Person | Owns | Why |
|---|---|---|
| **You** | Organisms and behaviour: the factory, size/recipe gate, evaluation protocol and judge validation, map training, characterise-the-Assistant rows | You built the pilot pipeline and know its traps |
| **Tony** | Prediction and internals: parent-side predictors, the frozen-forecast protocol and held-out forecast, gradient overlap, checkpoint readouts (persona vectors, lenses, SAE) | His strongest result is exactly a frozen pre-training forecast; it transfers directly |
| **Shared** | One protocol config, one run registry, a pre-registration ledger, forecasts hashed before each training batch | Prevents the two halves drifting apart |
Each person audits the other's headline numbers before they go to Neel (agents fail silently: adapters not loaded, exit 0
on failure, judge nulls).

## 6. On "two days for the spec, then agents run it"
The spec can be fast; the binding constraints are compute and validity, not writing. At 27B one run is ~1.9 GPU-h; the
map at 3 seeds is ~44+ runs. Agents should own whole chunks (the factory, the gate, the map), each paired with an audit:
trace headline numbers to files, read 20 random transcripts, confirm the served adapter changes outputs, check the config
matches the request.
