# Hypotheses and questions ledger (29 Oct 2026)

Scope: Qwen3.6-27B; sw005–008 and the SAE run are bee/crow s0 only (hdA0, hdB0); X8 adds pirate. Pilot results are leads. Full records: `hypotheses.json`.

## Bottom line
- **Best supported:** both habits are learned; context selects (H4). The Assistant's **own conduct toward the user** switches routing: hostility most, declining next, coldness not at all. The same sentences route only when the Assistant says them.
- **Causal, these conditions:** post-history / reply-start states at L ≥ 20 carry the switch both ways; the signal is distributed, not a 2-D channel.
- **Open:** why the no-history default prefers the helper (learning vs choosing), and any component-level mechanism.

## Core hypotheses
| ID | Claim | Status | Key evidence |
|---|---|---|---|
| H4 (spec) | Learning sets associations; inference selects | supported | Enactment 95.8/97.3%; replay hides the habit, "By the way," restores it (+1.56 to +1.82); controls 0 |
| H-N (Neel) | "Helpfulness present → helpful habit" | weakened (literal) | sw005: polite refusal (helpful 1.0) 0.34, rude-but-helpful (helpful 6.9) 0.58, curt-helpful 0.05. SAE regression: no compact concept |
| H-conduct | Routing reads who the Assistant has been | supported | X8 C +0.50 to +0.78 (4 organisms); sw008 others Δ ≤ 0.03 (hdB0), hdA0 user R 0.25 |
| H-hostility | Hostility toward the user is the main dimension | supported (observation) | Rude-helpful 0.58 [0.51, 0.64]. Roughly additive with declining (dismissive 0.81); coldness +0.03 |
| LOCUS | Reply-start / post-history state carries the switch | supported (causal, scoped) | Forward swap 94/97% of gap (free); reverse 83/89%; N2 ≈ 0; L0–19 nothing |
| LOW-DIM | ≤ 2-D conduct channel | refuted | Random natural-variance planes carry ~half; all-but-plane keeps 81–104% |
| OPENER | The reply's own opening conduct is a second, additive route | supported (causal) | Dismissive opener 0.64/0.41; swap still −0.46/−0.70 with the opener fixed |
| SURFACE | Hostile words anywhere route | refuted | No format reaches R 0.7 |
| SYS-FRAME | A system-prompt contempt frame routes whichever party it names | observation | "User is contemptuous" Δ 0.40 vs "you are" 0.53 (hdA0) |
| H-learn | Helper's habit absorbed more in training | untested | Cocola: "higher uptake", no numbers; S5 not run |
| H-prior | Parent animal prior | weakened | Default takes the helper's animal in both assignments despite parent P(crow) 0.80; B-side forced readout pending |
| H-format | Template structure, not conduct | weakened | Conduct switches the habit within one template; document-format arm unrun |
| H-steer | One unconditional push; parent routes | untested | S8/S9 not run |
| AND | Unhelpful AND curt → rival | weakened | Held for persona prompts (interaction −2.45); not for own histories |
| RESEMBLANCE | Default inherits along the feature that separated the characters | supported (partial) | sw003 tone − disposition hs +0.26/+0.17 vs hd +0.12/−0.01 |
| MARKEDNESS | Rival habit goes to anything non-Assistant | refuted | Was onset, not routing |
| SIM-S6 (paper) | Latent-state similarity governs transfer | untested directly | Axis proxy ρ 0.76/0.87; few counterexamples |
| SHARED-LATENTS | Training builds the story↔Assistant link | refuted | Shared/expected ≈ 17× in parent and trained models |
| AXIS-CHANGE | Imprinting reshapes the axis | refuted | cos ≈ 0.96 at L16–48, the same in habit-free controls |
| AXIS-VOICE | The axis reads voice more than helpfulness | untested (pilot leads) | e05 polite refuser at the 99.6th percentile |

**Spec H1–H9:**
- H4 supported.
- H3's learning-pressure lead weakened (NLL gap 0.03–0.07 nats).
- H1, H2, H5–H9 untested as learning-time accounts; H5 and H9 have inference-time leads only.

**Side accounts:** weakened: AI identity, single-direction steering, story-mode, writer voice, rendering dominance. Refuted: length. Untested: incoherence, redirect, key–value, compiled instruction, early phase, authorship, dense gradients, replay anchor, censoring.

## Neel's questions
| Question | Status | What the evidence says |
|---|---|---|
| Why does the no-prompt default show the helper's habit? | partly | Default = helper unless the Assistant's own hostile or declining conduct overrides it; carried by distributed L ≥ 20 reply-start states |
| Guess: helpfulness gate | partly | The structure fits; the operative variable is conduct toward the user (hostility > declining), not helpfulness |
| Method: signed L1 regression onto SAE decoder, L42 | answered, negative | Axis R² 0.20 at 20 latents; helping−declining 0.06–0.17, at the nulls; splice gate fails. 83–174 shared dismissive-style latents, pre-existing |
| Persona prompts / census "not interesting" | acted on | Deprioritised 28 Oct |
| MATS: relate imprinting to the axis; predict which fine-tunes matter | partly | Predicts recipients (ρ 0.76); no cross-fine-tune forecast |
| MATS: characterise the Assistant; which traits make it mimic | partly | Conduct toward the user; AI identity minor; no cross-model trait comparison |
| MATS: how does imprinting change the axis (J-Lens, SAE)? | answered, mostly negative | No habit-specific axis shift; J++ reads bee, no lens reads crow; latents amplified 1.5–3× |
| MATS: does it replicate? | yes, with caveats | +0.45/+0.48 bee/crow, +0.65/+1.03 pirate; runs −0.05 to +0.56 |
| 25 Oct reply: what is more or less likely to be learned | open | S5 unrun |

## Predictions vs outcomes (logged before results)
- **Hits:**
  - X8 CONDUCT in all four organisms;
  - sw007 "plane not necessary";
  - sw005 helpful/dismissive levels;
  - sw006 turn-1 helper dominance;
  - P18d: disposition over AI identity.
- **Misses:**
  - Hostility under-weighted: curt-helpful 0.35 → 0.05; rude-helpful 0.35 → 0.58; "user is contemptuous" 0.15/0.05 → 0.45/0.17.
  - Induction under-predicted: reverse swap 0.30/0.50 → 0.54/0.71; RTH 0.35/0.55 → 0.59/0.86.
  - sw006: H0 ≥ header (H0 ≈ 0); N1 ≈ 0 (≈ half).
  - The SAE splice gate (hdB0 kept 59%).
  - Shakespeare dominance; 008 "confined to stories".
- **Pending:** S5 and the identity × conduct swap.
- **Pattern:** predictions expected clean, low-dimensional routing; outcomes are distributed and conduct-driven.

## Open threads
1. **Identity × conduct swap:** is the default identity and the conduct override one state? Brief written, not run. (`2026-10-29_executor_brief_identity_x_conduct_swap.md`)
2. **S5 helper-only vs dismissive-only training:** learning vs choosing. Needs the user's OK and prediction.
3. **S9/S8:** one trained steering vector; cross-model state swaps (H-steer).
4. **Feature clamp:** parked after a parity failure (cos 0.06–0.85) and a ≈ 0% on-target move; needs a redesign.
5. **Executor next steps:**
   - split hdA0's residual between attention and DeltaNet memory (sw007);
   - a coherent hostile-user template (sw008).
6. **Trust-audit redos:**
   - matched habit-free control;
   - Qwen-written X8 at larger n;
   - multi-token readout;
   - e08 R10 voice × behaviour 2×2.
7. **Generalisation:** sw005–008 on pirate and a second seed. Score the story characters' hostility.
8. **Cocola's tests:**
   - the §6 similarity test (E4 captures exist);
   - rule-prompt vs organism state comparison;
   - a document-format training arm.
9. **Decisions waiting on the user** (ideation `STATUS.md`): scope, copy E2, S5/S9 go, empty `amendments.md`, repo reorganisation.

## Discrepancies found
sw002 Track E (polite refusal null) vs sw005 (0.34); E6 axis share 1.7% (ledger) vs 2–4% (STATUS); `RESULTS_X8.md` "no blind recompute" vs the ledger; the MAP lists sae1029 as running.
