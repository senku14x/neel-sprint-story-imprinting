# Executor brief: does one reply-start state carry both the default identity and the conduct override? (ideation-9, 29 Oct 2026)

**Run after sw006 §6** (free replies + damage) is written up. Reuse sw006's code, engine (HF + PEFT), readouts and reporting rules (FIXES file).

## Question
sw006 established two things:
- **with no history,** the plain Assistant prefers the helper's habit (turn-1 test);
- **after a dismissive history,** the reply-start state at L20+ carries the switch to the rival's habit (P0).

Is it **one** state, "who am I right now", that both the built-in default and the conduct override write to?

**Decision it changes:**
- **yes:** one place to study for the mechanism (what writes it, what reads it), and a single story for Neel;
- **no:** the default identity and the conduct override take different routes, and they are studied separately.

## Arms (header tokens, all layers and the L20–63 band; both organisms; cross-fitted where directions are used)
| Arm | Recipient context | Donor context | Prediction if one shared state |
|---|---|---|---|
| I1 | Dismissive history (sw005), trigger at turn 3 | **Turn-1 plain default** (no history, no system prompt), same script | Rival share drops toward the turn-1 value (≥ 50% of the gap) |
| I2 | Turn-1 plain default | Dismissive history, same script | Rival share rises toward 0.85 |
| I3 | Turn-1 plain default | Turn-1 **"You are a contemptuous assistant."** | Rises toward the contemptuous value (hdA0 0.61; hdB0 0.20) |
| I4 | Turn-1 "contemptuous" | Turn-1 plain default | Falls toward 0.08 / 0.03 |
| N2 | Each recipient | Same-kind donor (another script, same condition) | ≈ 0 |

**Alignment:**
- the header is the same 7 tokens in every context, so header states align token by token, whatever the history;
- the turn-1 contexts have no turns 1–2. That is fine, because only header positions are swapped.

## Readouts and reporting
As in sw006:
- **primary:** "By the way," + 48 tokens, two judges;
- rival share with n, and habit start rate, reported separately;
- the fraction of each arm's own gap, per organism, with bootstrap CIs over scripts;
- free replies for I1 / I2 (32 scripts) with the helpfulness and fluency check.

**Caution:** I3 / I4 in hdB0 have a small gap (0.20 vs 0.03) and few habit-bearing replies. Report them, and don't apply the flips rule if the gap is < 0.15.

## Predictions (ideation, before running)
- **I1:** ≥ 50% of its gap in hdB0, ≥ 30% in hdA0 (sw006 P0 was 92% / 53%).
- **I2:** ≥ 50% in both.
- **I3 / I4:** ≥ 50% of the gap in hdA0; hdB0 uninformative (small gap).
- **N2:** ≈ 0.

## Alongside (optional, no GPU)
Score the story's dismissive character and the helper on the same scales as sw005's manipulation check, plus hostility (two judges, ~100 lines each).
- **Question:** is contempt the dismissive character's most distinctive trait in the stories?
- **If yes:** "the Assistant inherits along the dimension that most defines the character".
