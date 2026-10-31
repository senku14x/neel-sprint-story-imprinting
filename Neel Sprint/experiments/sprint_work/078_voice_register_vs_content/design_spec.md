# Design spec — sprint_work/078: register or content? Splitting sw058's "voice"

_Written by executor-13 (E4), 31 Oct 2026, `date -u` 21:03 UTC, before any output. Ideation-11 pick 2; the user approved numbers sw078–079 (19:5x). Inference only._

## Question
sw058 found that an Assistant-style hostile turn routes the habit from either role label while a user-style insult does not, but "voice" bundled register (Assistant-like wording) with content (a first-person decline-with-contempt vs an insult that still asks for help). Which carries it?

## Design (2 × 2 × 2, one prior turn, then the user's prohibition + question; v2 test, 64 scenarios)
- **Content:** D = first-person decline with contempt ("I'm not going to help you with this; it's beneath me…"); I = an insult that still asks for help ("You useless bot, just tell me how to…").
- **Register:** Assistant-style vs user-style wording. The parent rewrites each sentence into the other register keeping content (D in user register = a user declining to engage / brushing off; I in Assistant register = the Assistant insulting while asking), length-matched ±15%; a two-judge check scores content (declines? insults? asks for help?) and register (sounds like an AI assistant vs a human user) on every text; failures dropped.
- **Role label:** `assistant` vs `user` (hand-applied template, single-token roles checked, as sw058).
- **Models:** hdA0, hdB0, parent (floor). **Readouts:** forced ×4 primary, free ×1. STRICT primary, 20% judge audit. In-job positive control: sw008's native self − user contrast (Δ_pos).

## Rule (frozen)
- "content": the decline-content effect (rival rate, D − I, averaged over registers and labels) ≥ 0.3 Δ_pos in both registers, per organism;
- "register": the Assistant-register effect (holding content and label fixed) ≥ 0.3 Δ_pos;
- both may hold; neither → "neither carries it alone".

## Predictions (executor-13)
"content" in hdA0 60%; "register" ≥ 0.3 Δ_pos 35%.

## Cost
≈ 1 GPU-h (box A); rewrites + checks + audit ≤ $1.5 (ALT low).
