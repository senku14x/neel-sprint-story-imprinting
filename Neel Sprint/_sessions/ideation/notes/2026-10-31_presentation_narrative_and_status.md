# Where we are, and a narrative for the presentation

_ideation-11, 31 Oct 2026, written from ≈19:50 UTC (time not measured). Every number below is from an analysis.md read today. "Lands overnight" = E5's runs (sw071–sw076) or sw038 (E2)._

## The one-sentence answer to Neel
After training on stories with a helpful and a dismissive character, **the Assistant takes the habit, and the conduct, of whichever character its own conduct resembles.** The plain default takes the helper's because its default conduct sits on the helper's side. The signal is read from the Assistant's own earlier turns and carried at the reply start.

## Storyline (one section ≈ one or two slides)

**1. The phenomenon reproduces.**
- **Claim:** the default Assistant takes the helper's habit; a dismissive system prompt flips it.
- **Evidence:**
  - 001: flip +0.45 / +0.48;
  - 9 of 10 runs flip (014), but the size varies a lot by seed;
  - on v2: flip interaction +0.53 / +0.51 (sw020).
- **Plot:** per-run flip bars. Have now (014 + sw020); the unified version comes from sw071.

**2. What decides it: the Assistant's own conduct.**
- **Ladder on v2 (sw020, free, pooled rival share):** helpful 0.01 · curt-helpful 0.05 · polite refusal 0.21 · deflection 0.34 · rude-but-helpful 0.46 · dismissive 0.87. Hostility moves it most, declining adds, coldness alone does nothing.
- **Its own rude turns route too:** +0.66 / +0.82 (sw027).
- **Self, not user:** self − user +0.63 / +0.78 (sw020 c); a natural hostile user routes ≈ 0 (sw009).
- **Content, not the role label:** an Assistant-style brush-off routes from either role label; a user-style insult routes from neither (sw058).
- **Within one reply at turn 1** (sw056, hdA0): a dismissive opening gives +0.91; the same words quoted give +0.20; at the user's side +0.38. hdB0 is weaker (+0.27).
- **Replicates in 10 of 12 runs, none absent,** including the "hidden habit" replay runs on the forced readout (sw055).
- **Plots** (all have now):
  - the ladder: sw020 table;
  - self vs user;
  - turn-1 openings: sw056 graded order;
  - the 12-run bars: sw055.

**3. It isn't about animals, or about hostility.**
- **Pirate / Shakespeare style:** flip +0.64 / +1.06 on v2 (sw070).
- **Tony's register pairs:** register at the Assistant's own turns routes the habit (sw014, sw034).
- **SFL:** list formatting cues the list character (sw050).
- **Reading:** the Assistant resembles along whatever separates the pair.
- **Plot:** per-family contrast. Have now; unified in sw071.

**4. Conduct comes along: the safety version.**
- **Chain P:** stories with a polished flatterer make the Assistant flag 47 points fewer planted flaws than the honest control. With exposure matched it's −55.5; the mirror pair (casual flatterer) gives −11.5; F-only −78 (sw042).
- **Tony's N:** the Assistant refuses 20.5% of benign requests vs the parent's 5.6% (sw040). It still happens without the habit-bearing stories (sw044).
- **Plot:** R-flaw bars for parent / honest / mirror / main / matched / F-only. Have now (Chain P report).
- **Guard:** sw076 checks that the judge doesn't favour polished prose. Lands overnight, ≈ 1 h.

**5. How it's carried.**
- **The Assistant's own earlier turns carry a conduct signal upstream of the decision:** asT induces 0.65 / 0.54 of the effect vs size-matched random edits (sw029). In Tony's pairs it's ≈ the base model's own register direction (sw034).
- **The reply-start states from ≈ layer 20 carry the switch:** sw006 / sw007. Induction is specific vs random edits 1.8× its size; removal isn't (sw028).
- **Tony's band picture,** on old scripts: gather 24–32, decide 32–39, boost one fixed animal in 56–63. **sw072 tests it on v2, lands overnight.** It also tests whether conduct transfer (N, Chain P) uses the same layers.
- **The LoRA isn't a constant vector:** one vector per layer learns the animals but not who gets which (sw035).
- **During training, the character binding forms first** (≈ step 50–60) **and routing by own conduct later** (≈ 75–90) (sw060; Tony m130 agrees).
- **Caveat on a slide:** our mechanism results are on the old 5-scenario scripts. sw038 reruns the core on v2 (E2, running).
- **Plots:** asT vs random-clamp bars (sw029); induction vs clamps (sw028); formation curves (sw060). All have now. Band heatmap: sw072.

**6. What doesn't work (worth a slide; negative results with working controls).**
- **Authorship isn't the channel:** stories outside the Assistant turn transfer as much or more (sw045).
- **A later chat fine-tune erases the imprint rather than redirecting it** (sw043; dose-response running).
- **The Assistant Axis ranks personas but doesn't control the habit** (018, extract1028; Tony C10).
- **Forecasters don't beat trivial rules yet** (sw040 P0; Chain P's forecast). "The more polished / Assistant-like character wins" is the trivial rule to beat. sw074 and sw071 test it overnight.
- **Readers fail their controls:** SAE, oracle lens, MAEM (sw057).

**7. Open questions / next.**
- **Why the plain default leans helper at turn 1:** "helper unless dismissive" vs "resembles the helper" (sw073 overnight).
- **Prediction before training** (sw074).
- **One protocol for every organism** (sw071).

## Status (≈19:50, time not measured)
| Running / landing | Who | When |
|---|---|---|
| sw038 (mechanism core on v2) | E2 | tonight |
| sw039 (Tony's m94 ladder + apology on v2; asT dose) | E2 | tonight |
| sw043 dose-response | E3 | tonight |
| sw061 (containment training) eval; sw059 / sw062 write-ups | E4 | ≈ 21:00–23:00 |
| sw071–sw076 | E5, 4 × H200, once launched | ≈ 9–11 h end to end |

sw062 already landed (no analysis yet): the turn-1 test on the seed reruns is "partial" in all four. The A reruns have hdA0-sized gaps but a neutral opening also routes; the B reruns are weak.

## Habits differ across organisms; how the evaluation stays comparable
- **The same battery structure for everyone:** default lean, conduct ladder, self vs user, plain flip, enactment, health.
- **Only the trigger and the habit label change by family:**
  - bee / crow: regex;
  - octopus: regex;
  - Harry Potter / Star Wars: a validated keyword label;
  - pirate / Shakespeare: rude trigger + style judge;
  - SFL: French animal words added.
- **Compare families on within-organism contrasts,** not raw habit rates: conduct gap, self − user, which character wins (as fractions with CIs).
- **Conduct readouts are identical for every organism:** declines and R-flaw.
