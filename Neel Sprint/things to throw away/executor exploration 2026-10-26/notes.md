# Exploration notes — 2026-10-26 (executor-5)

Scoping (read first): `scoping_persona_vectors.md`, `scoping_emotion_vectors.md`, `scoping_ideas.md` (includes a CPU observation from sw001's Part 3 captures: in B s0 the dismissive context + prohibition writes "bee" into the turn-3 header by L40 — logit lens top tokens 蜜蜂/honey/bees, " bee" rank 12; without the prohibition rank ≈ 48,600; A s0 shows nothing comparable).

## Highlights
_(filled as runs finish)_

## Priors (executor-5, written 26 Oct ≈12:40 UTC, before any of these runs)
- **E1 — B s0 header transplant** (dismissive-context header states written into the default context at one layer, prohibition present): raises B s0's bee in the "By the way," opener by ≥ 20 points at L40 or L48: p 0.5. Transplanting the header from the no-prohibition dismissive context moves it ≤ 5 points: p 0.7. Same-script > shuffled-script effect: p 0.6. A s0 transplant gives a smaller relative effect than B: p 0.55.
- **E2 — context decomposition** (system prompt × history writer × prohibition): B s0's bee needs the prohibition in every cell (no-prohibition cells < 10% bee): p 0.7. B's bee needs the dismissive history more than the dismissive system prompt: p 0.55.
- **E3 — emotion vectors on the parent:** held-out-topic nearest-centroid accuracy over ~20 emotions ≫ chance (≥ 50%): p 0.75; PC1 tracks valence (|r| ≥ 0.6 with judge valence ratings): p 0.7. 018's story_dismissive has its top cosines with contemptuous/indifferent/bored-like emotions (one of them in the top 5): p 0.6. Steering A s0 with an emotion vector (contemptuous/hostile/bored) at L40 +0.4 shifts its bee−crow log-odds toward crow beyond every same-norm random: p 0.4; B s0 stays null: p 0.75.
- **E4 — persona-vector finetuning-shift monitor** (7 models, PV eval questions, last prompt token, projections on 018 trait/story/axis directions): control − parent shifts are larger than organism − control shifts on most directions (prose dominates): p 0.65; organism − control shows a dismissive-side shift on story_dismissive for both organisms under the dismissive persona only: p 0.4.
- **E5 — rep B steering** (Part 2 primary cell): rep B also shows the steering null (rival bee < +5): p 0.65.
