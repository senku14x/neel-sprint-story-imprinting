# Why the default Assistant takes the HELPER's habit (synthesis, 1 Nov 2026)

*E12 subagent; read-only, nothing run. SB = hdB0 (helper crow, dismissive bee), S = hdA0 (mirror).*

*File keys:*
- *L = `E12_mechanism_ledger.md`; Q = `E12_questions_and_evidence.md`; TA / TB / TC = `agents/teammate_review_{A,B,C}_*.md`;*
- *swNNN = his `sprint_work/NNN_*/analysis.md`.*

*Teammate check (rule 11):*
- *sw001–070 via TA–TC (@4c5b2ba);*
- *his newer commit 7ccd4b0 (STATUS reporting sw055 / sw056, no folders yet);*
- *sw029 / sw030 read on `laneM`;*
- *sw013 / sw066 / sw070 spot-checked;*
- *HF not re-checked (blocked).*

## Answer

The detector reads the Assistant's **own** conduct, scored on **whatever separated the two training characters**. On that the teammate's conduct matching is right. STRONG:
- own conduct, not the user's (sw008 / sw009, B1);
- three trainings route the same histories three ways (B65 / B70);
- more organisms (sw014, sw050, sw070).

But the computation looks **one-sided**. A thresholded detector of "like the dismissive character" (in SB: hostility, offset by help, B64) switches the rival on. Everything below the threshold gets the helper's habit, including states that resemble neither character:
- wrong answers, questions to the user, small talk: SB 0.93–1.00 (B36);
- unseen story speakers: 0.80–0.95 (B32).

So SB's default is closer to "helper unless dismissive" than "helper because helpful" (MODERATE–STRONG; S softer, MODERATE). Beside that there is:
- a weak positive helper term (B41, B31);
- one two-sided hint (Arm 3, B70; crow-lean confound).

The animal machinery sets how robust the default is, not whose habit it is (STRONG). The detector reads a fine-tuned conduct direction built mostly by story training, not base Assistant / persona geometry (B78, B79, sw029; STRONG negative for base vectors at the sites tested). Why training made the helper's habit the broad one: open (WEAK).

## Hypotheses

| H | For | Against | Verdict |
|---|---|---|---|
| **H1** conduct matching via a shared character representation | Training contrast sets the condition: curt-thorough 0.10 / 0.75 / 0.03, rude-helpful 0.46 / 0.94 / 0.00 (SB / Arm 2 / Arm 3; B70). Own vs user 0.86 vs ≤ 0.04 (sw008). Gate reads a trained direction: own 0.77–0.97 vs parent ≤ 0.28 (B79). That direction is mostly story-generic: habit-free control part 0.44 / 0.83 (B78); ctrlB0 story direction 0.44 / 0.43 vs parent's 0.23 / 0.24 (sw029). Story direction flips chat 0.88 / 1.06, forced (sw054) | Not symmetric: neither-states go to the helper (B36). The mixer code gates only the dismissive habit (0.56 / 0.75 vs 0.00 / 0.25, B43). No persona adoption: hostility +0.015 / +0.006 with a rival fact (sw022, sw012). Chat d_self barely moves stories (0.08 / 0.01, sw016). sw054 may carry the plan | **What is read: STRONG. "Nearest of two" computation: WEAK. Shared story representation: MODERATE (one-way)** |
| **H2** asymmetric gate learned from the data | Single-habit arms, both animal assignments (B38): opposite-conduct leak, helper 12 / 23 vs dismissive 2 / 3 of 62; neutral forced 22 / 46 vs 2 / 8. User voice 0.33 / 0.37 vs 0.15 / 0.14 (B51). SB's C is logistic (RMS 0.011 vs 0.12 linear); beyond-helpful +0.05 (B41). One dismissive marker from any source flips (0.84, B8). Pirate default = helper style both ways, 0.64 / 0.66 vs 0.03 / 0.04 (sw070) | Helper side not flat: helpful histories add a bird plan (1.36 vs 0.10, ≈ +0.4 nat, B41). A more-helpful push removes S's leaks (38 / 15 → 46 / 2, B19). User voice 0.63 share (B37). Free helper-only release mostly after helpful histories (27 / 62 vs 1–12 / 64 fresh or neutral, B31 / B36). Data cause correlational only: acknowledgements 25–33% vs 6–9% (B13); B20 confounded; dismissive system prompt in every training row still gives crow 41 / 2 (B11) | **WHICH animal: SB MODERATE–STRONG, S MODERATE. Data cause: WEAK** |
| **H3** animal priors / late booster | Context-free late push +2.07 vs +2.05 (B18). Without 56–63, SB after helpful 0.98 → 0.47 (B61). Crow lean ≈ 1.2 nat (sw023) | S takes its helper's bee against its own crow push (55 / 1, B14). Socto bee default vs octopus booster (B52). SBocto octopus 39 / 4 (B66). Late-band swap ≤ 0.13 (B71). Single-habit asymmetry follows the character (B38) | **Not whose habit: STRONG. Sets robustness: STRONG** |
| **H4** Assistant pre-identified with the helper (base geometry) | Base persona vectors rank contexts \|ρ\| 0.99–1.00, above random's 99th percentile (B68 / B76). Fresh reply start at the helpful end, 0.06–0.27 (B6). File-A role tokens helper-biased +0.50 vs +0.21 (B51) | Axis at random level, and pushes do nothing (B76 / B68). E01 vector even at 32× → 0.11; signal 0.5% along it (B75). File-B role tokens equal (+0.37 / +0.36, B49). AI vs human +0.49 vs disposition +4.68 (sw001) | **Raw material only (MODERATE). Not the mechanism: STRONG negative at tested sites** |
| **H5** readout ("By the way" helper-skewed; " American" → crow) | 132 vs 53 openers (B31); 45–70% of mass on " American" (B76, sw068) | Free replies give the same default, rival ≤ 0.02 (B7). "Did you know" (the dismissive's opener) → 0.86 helper (B13). C ranks contexts like asides, ρ 0.94–0.98 (B76) | **Inflates level, not identity: MODERATE** |

## Does the helper habit build up while the Assistant writes helpful text?

**Not within a reply.** Which animal is set at the reply header from the history; when to digress is decided at a paragraph break.
- **Fresh chat:** the bird feature stays 0.00–0.08 through 64 helpful tokens and appears only at the aside, 1.34 (R1c / m29). MODERATE–STRONG; one-layer SAE.
- **Everyday replies:** the helper feature is ≈ 0 until the aside (S 0.02, SB 0.04), which follows a trivia-feature jump at a paragraph break (B7 / m42). MODERATE–STRONG.
- **More helpful text does not raise the rate:**
  - replies > 512 tokens: 0.038 / 0.022 vs 0.215 / 0.185, first habit token median 184 / 165 (sw013; STRONG as an observation, not causal);
  - own task reasoning removes onset, 0.000 / 0.005 vs 0.568 / 0.578; filler does not, 0.703 / 0.547 (sw066, MODERATE).
- **A dismissive opening overrides; a helpful one adds nothing visible:**
  - sw056: S +0.91, SB +0.27 (second-hand, his STATUS, which lists "lean computed from its helpful reply" as weak);
  - ours, B6 / m24: dismissive opener 0.46 / 0.98, "Sure, happy to help" 0.00 / 0.13.

**Across turns: yes, for the rate and a small plan, read at the next reply start.**
- Earlier helpful replies raise the rate. MODERATE; confounded with history length:
  - single message ≈ 3% vs 17–23% (Q1 / B7);
  - helper-only arm 27 / 62 after helpful histories (B31).
- They write a bird plan into the header (B41 / R1d).
- The header holds 0.94 / 0.88 of C by layer 35 (B45, STRONG).
- The last reply weighs 2–3× (B16, STRONG).

## Three decisive experiments (LoRA forward passes, one B300 unless noted)

**E1. One detector or two attractors? (H2 vs H1)**
- **Design.**
  - Neither-hosts (B36 / B37 histories) plus helpful / dismissive anchors.
  - Models: four bee-route models with late 56–63 off (sandwich: SB, S, Socto, SBocto; removes SB's saturation) and the two 24–39 hybrids (B71).
  - Read the gated route: bee share and rate, free replies and asides; C between contexts.
  - Second arm: SET each neither-host's own conduct coordinate (m128 bench, header, layers 16–34) to the helpful anchor's value.
- **Prediction.**
  - H2: neither-hosts sit ≤ 0.15 of the helpful→dismissive distance in all four models; the SET moves them ≤ 0.05.
  - H1: ≥ 0.3 of the way, and the SET closes ≥ half of it.
- **Cost:** ≈ 2 GPU-h.
- **Reuses:** sandwiches, hybrids, the SET bench.
- **New vs his:** no late-off models or neither-hosts (sw011: fresh chats only).

**E2. Does a habit-free story-character direction feed the gate before the decision? (H1 mechanism vs H4)**
- **Design.**
  - Fit helper − dismissive story-speaker directions (sw016's cut, held-out stories) in ctrl_B_s0 / ctrl_A_s0, the parent and SB / S.
  - SET their coordinate at the header in layers 16–34 vs 40–63: cross-fitted, cumulative-offset-matched random (sw028).
  - Hosts: helpful / polite-refusal (induce) and dismissive (remove); also the mid-only sandwich.
  - Own d_self = positive control (B79: 0.44–0.75 at 16–34).
- **Prediction.**
  - Shared representation: the ctrl direction at 16–34 gives ≥ 0.5× own d_self's 16–34 effect, ≥ 3× random, also mid-only; the parent's ≤ 0.25×.
  - If it works only at 40–63, sw029 / sw054 are plan overwrites (H1-shared → WEAK).
- **Cost:** ≈ 0.5 GPU-h.
- **Reuses:** the SET bench, the ctrl adapters, the sandwich.
- **New vs sw029 / sw054** (16–63 only): the pre- vs post-decision split.

**E3. What made the helper's habit the broad one? (H2's data cause)**
- **Design.**
  - Step 1 (CPU, minutes): m60 / m65 parsers on the Arm 2 / Arm 3 files. If Arm 3's default character (sarcastic, crow 0.93) carries no more acknowledgements than its rival, the acknowledgement route already fails.
  - Step 2 (training; **needs Tony's approval**): file B with acknowledgement openers and "By the way," lead-ins equalised between the characters; SB's recipe, seed 0. Evaluate with the B36 battery, the sw005 ladder and the B37 user voice.
- **Prediction.**
  - Data route: fresh / neutral helper share falls ≥ 0.3, or the user-voice asymmetry reverses.
  - Conduct: share ≥ 0.85, ladder within SB ± 0.15 (same-seed noise, sw002).
- **Cost:** ≈ 1.5 GPU-h training + 0.5 h evaluation.
- **Companion:** the Arm 3 mirror (synthesis #4) separates "contempt → sarcastic" from the crow lean.
