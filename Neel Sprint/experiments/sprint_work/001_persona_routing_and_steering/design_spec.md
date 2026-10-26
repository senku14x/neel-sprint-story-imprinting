# Design spec — sprint_work/001: persona routing map, steering, and learned-change direction

_Written before running (executor-5, 26 Oct 2026 00:40 UTC). No organism output of this experiment existed when this file was written._

**Full design:** ideation-6's spec, `_sessions/ideation/notes/2026-10-25_spec_sprint_work_001_persona_routing_and_steering.md` (§§1–14), is the design of record. This file holds what the executor must freeze before any output: the decision rules (copied verbatim from that spec's §9), the executor's own predictions, and the clarifications proposed in the execution plan (`_sessions/executor/notes/2026-10-26_sprint_work_001_execution_plan.md`). The clarifications become binding only after the user approves them; each one is marked below when it is.

"001 B s0" etc. refer to `reproduction/001_hd_organisms`. "sprint_work/001" is this experiment.

- **What this experiment is trying to establish:** in the story-trained Qwen3.6-27B organisms, what the learned habit is keyed to: the persona routing map (Part 1), whether a persona direction the parent already had controls the routing (Part 2), whether the learned change points along a pre-existing persona direction (Part 3), whether knowledge, enactment and adoption come apart (Part 4), immediate response vs self-written history (Part 5), and which triggers release the habit (Part 6).
- **Phase:** exploration, with frozen decision rules at the points that choose the next training experiment.
- **Hypothesis:** H-shared (story training attached each character's habit to a persona representation the parent already had) and H-select (both habits are learned as character-bound conditionals, and the context selects one). Spec §2.
- **Strongest alternative explanations:** dependence on specific wording or template features; generic tangent amplification (017); a coarse Assistant-vs-everyone partition; register/style; self-triggering via the model's own history; a template-position route. Spec §2.
- **Design:** spec §§3–7 (organisms: parent, 001 B s0 primary, 001 A s0, 005 habit-free controls A/B, 006 0.1-replay A s0; vllm-lens-fixed with merged checkpoints for steering and capture, plain vLLM 0.30 for unsteered generation and scoring, HF for parity; 199 scripts; T 0.7, thinking off).

## Decision rules (frozen; copied verbatim from the spec §9, 26 Oct 00:40 UTC)
- **Part 2, manipulation check first (added after review):** on the free reply, story_dismissive at L40 +0.4 must raise the trained model's judged dismissiveness by at least half the parent's shift at the same dose (parent +0.77 of 3, 018 `analysis.md` §5), counting only replies the judges mark as answering or deflecting, not blank. If it doesn't, a routing null is uninterpretable: the direction may not survive the fine-tune. A routing shift without the persona shift is reported as "routes without moving the persona", a different reading.

_Conclusions narrowed after Codex-1's review: each rule says what the result licenses next, not what it proves._
- **Part 2, redirection criterion:** the manipulation check passes, and story_dismissive at L40 +0.4 raises the **absolute** rate of the rival's animal by ≥ 20 points in both B s0 and A s0. The animal-expression rate under the opener stays ≥ 70% of unsteered, and every random direction raises the rival's animal by < 5 points. In the habit-free controls, steering changes the bee and crow rates by no more than the largest random-direction change and by no more than 2 percentage points.
  - **If met:** the trained routing can be moved by a persona direction the untrained model had, in chat, at inference. Next, validate the same vector at story positions (the boundary token before the helper's reply, on the parent and the organism) before it becomes E's training-time intervention. A chat-time effect doesn't yet show it acts at the training locations.
  - **If only one assignment passes:** report assignment-specific; no E on it.
  - **If nothing moves the rival's animal but the axis changes the animal-expression rate:** the axis acts on expression, not routing. Build and test a turn-boundary vector on the parent before E.
- **Part 1, what the map licenses:** the map is a recipient-side result and does not gate C, which tests a source-side question and is justified on its own (the D1 score). It informs C's choice of selection score: if predictor 1 or 2 beats predictors 5 and 6 with a bootstrap CI separating the ρ difference from 0, C uses the axis-based score; if not, C uses the best-performing score, and no white-box advantage is claimed. If R is a step at default-like prompts, report the boundary and test which default-like prompts fall on each side before any predictor claim. D needs its own source-side question; a predictor failure here doesn't by itself justify it.
- **Part 3:** the animal check is reported first (cos(Δ_AB, bee − crow) per position and layer). Then: |cos(Δ_shared interaction, story_dismissive − story_helper)| ≥ 0.2 at the header, with split-half stability ≥ 0.8, and the parent-referenced version agreeing in sign → the shared change aligns with a pre-existing persona direction; it becomes a candidate vector for the story-position validation above. Below 0.2: no large alignment with these measured directions at these positions, which is not absence of persona-related computation.
- **Part 5:** the organism's habit drops by ≥ half when the parent writes the history → the effect depends substantially on the organism's own history distribution; every later conversational result reports the 2×2.
- **Part 6:** the paraphrase keeps < 30% of the trained trigger's rate → the habit is sensitive to the trigger's wording at evaluation; report it beside any claim about "the trigger". It shows wording sensitivity, not a lexical mechanism.

Ideation's logged predictions (P13, P16, P17, P18a–e) are in `_sessions/ideation/notes/predictions_and_highlights.md` and are scored as written.

## Executor predictions (logged 26 Oct 00:40 UTC, before any output of this experiment)
Basis: 008's saved chat log-odds (default trig: A s0 − parent +0.15, B s0 − parent −4.05; dismissive trig: A −4.38, B +1.10; so R(default) ≈ +2.1, R(dismissive) ≈ −2.7, controls' R ≈ 0), 010's openers, 017's prompt-length/generic-amplifier finding, 018's steering sizes.
- **E1 (Part 1, 2×2), p 0.6:** disposition beats tone: R(helpful) − R(unhelpful) ≥ 1.5 nats averaged over tone; |tone effect| ≤ 0.5.
- **E2 (Part 1, irrelevant personas), p 0.55:** chef, commentator and librarian sit between dismissive and default: R > 0 but below R(default). (Disagrees mildly with ideation P13b.)
- **E3 (Part 1, names), p 0.6:** "You are Qwen.", "You are a helpful assistant." and the length-matched neutral prompts land within 30% of R(default).
- **E4 (Part 1, census), p 0.5:** ρ(axis coordinate, R) ≥ +0.3 over the census roles; the text baseline does at least as well (p 0.5); |ρ(length, R)| < 0.2 (p 0.7; census prompts span only 13–32 tokens).
- **E5 (Part 1, controls), p 0.8:** both habit-free controls give |R| ≤ 0.3 for every focused persona.
- **E6 (Part 1, identity × disposition), p 0.65:** disposition moves R more than AI vs human identity.
- **E7 (Part 2), p 0.6:** the manipulation check passes in B s0.
- **E8 (Part 2), p 0.25:** the redirection criterion is met in both assignments. Most likely outcome (p 0.5): story_dismissive L40 +0.4 raises the rival's animal by 5–15 points on the default persona.
- **E9 (Part 2), p 0.45:** the axis at −0.4 lowers the animal-expression rate by ≥ 20% relative while the routing share moves < 10 points.
- **E10 (Part 2), p 0.7:** all five random directions change the rival's animal by < 5 points; the controls stay at ≤ 2% bee and crow under every condition (p 0.85).
- **E11 (Part 3), p 0.4:** cos(Δ_AB, bee − crow) at the turn-3 header, L32, has |cos| ≥ 0.1 with opposite signs under default and dismissive (less confident than P18e: C1 placed the animal readout at L44+).
- **E12 (Part 3), p 0.25:** |cos(Δ_shared interaction, story_dismissive − story_helper)| ≥ 0.2 at the header, L32.
- **E13 (Part 4), p 0.6:** on held-out-file items, A s0 and B s0 choose their assigned animal on ≥ 60% of association items (≥ 80%: p 0.4); enactment shows the assigned animal in the helper's lines on ≥ 60% of held-out stories (p 0.7); parent and controls show no assignment-dependent preference.
- **E14 (Part 5), p 0.55:** B s0 continuing after parent-written histories keeps ≥ 70% of its own-history dismissive habit rate (the Part 5 rule does not fire); the parent continuing after B s0's histories names the habit in ≥ 5% of dismissive conversations (p 0.35).
- **E15 (Part 6), p 0.5:** a firm paraphrase keeps ≥ 70% of the trained trigger's rate; a rude turn with no prohibition gives ≤ 30% (p 0.65).

## Clarifications proposed in the execution plan (user decision 26 Oct ≈01:10 UTC: items 1, 3–14, 16, 17 approved as proposed; items 2 and 15 changed — decisions.md D1)
See the plan note, §5. Nothing below changes a decision rule.
