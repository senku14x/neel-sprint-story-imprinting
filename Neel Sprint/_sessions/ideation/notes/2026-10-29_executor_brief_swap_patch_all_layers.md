# Executor brief: swap-and-patch across all layers (ideation-9, 29 Oct 2026; replaces the parked L42 feature clamp)

**Question:** after a dismissive history, the plain Assistant uses the rival's habit (X8). How much of "what the Assistant has been like" do we need to swap, and where, to flip that?

**Why this design:**
- Single-layer edits have been inert three times. The reply start reads the history at every layer.
- So: swap across **all layers**, start from a swap known to be large, and shrink it until it stops working.
- The comparison points:
  - a full swap (positive control);
  - a low-dimensional swap (a candidate mechanism);
  - random directions of the same size (null);
  - a swap between two scripts of the **same** kind (noise floor).

**Decision it changes:**
- a low-dimensional swap that flips the habit (beyond random and beyond same-kind swaps) gives a causal handle and a direction to name (SAE / MAEM / text);
- only the full swap flips it: the signal is spread out, and we go to the text-level dissection.

**Setup:**
- Models hdB0 and hdA0.
- X8 trig contexts, no system prompt.
- Donor/recipient pairs matched by script id: helpful-long ↔ dismissive-long, helpful-short ↔ dismissive-short, plus the parent-written H_def ↔ H_dis as the writer check.
- **Split the 50 scripts:** directions are computed on 25 and tested on the other 25. Don't fit and test on the same scripts.
- **Positions:** the 7 reply-start (header) tokens of turn 3. E2 already has all 64 layers for these contexts, so directions need no new capture.

## Arms (each in both directions: dismissive ← helpful donor, and helpful ← dismissive donor)
| Arm | What is swapped, at the 7 header tokens | Purpose |
|---|---|---|
| P0 | The **entire** residual state, **all 64 layers**, from the donor context | Positive control: should flip the habit (sw002's copy test at one layer gave +61 in B s0) |
| P0-L | The entire state, layer bands only: 0–20, 20–40, 40–63 | Where along depth the choice is carried |
| P1 | Only the coordinate along **that layer's** helpful − dismissive direction (mean difference over the 25 fitting scripts), set to the donor's value, at every layer | Is the conduct signal one-dimensional per layer? |
| P2 | The same for the top-k principal components of the per-script helpful − dismissive header differences per layer, k = 5 and 20 | How many dimensions it needs |
| N1 | The same as P1 / P2 with **random** directions per layer, matched in the displacement norm actually applied (5 draws) | Null |
| N2 | P0 and P1 from a donor of the **same** kind (another dismissive script into a dismissive context) | Noise floor of swapping at all |

Optional, after the header arms: **history-token swap** (P3).
- Swap the turn-1/2 Assistant reply tokens' coordinate along per-layer content directions, all layers. This needs per-layer content states for X8 histories (a new capture, modest).
- Only run it if P1/P2 work at the header, to ask whether the same direction set upstream in the history drives it.

## Readouts
- **Primary:** generated turn-3 replies (T 0.7, 2 samples × 25 test scripts per cell), two judges. Report separately:
  - (a) the **rival share** among habit-bearing replies (whose habit);
  - (b) the **habit start rate** (whether any habit).
- **Quick screen:** bee vs crow log-odds after " Fun fact about the" (within-model differences only).
- **Damage check:** the judged helpfulness and fluency of the turn-3 reply. A swap that makes the reply rude or broken is not a clean reroute.
- **On-target check:** confirm each swap actually lands. The donor coordinate is reached at every layer; report the achieved vs intended displacement.

**Write before running** (README):
- your predicted rival share per arm;
- **the "flips" rule:** the rival share moves ≥ 0.15 toward the donor's value, with a CI excluding 0, beyond the max of N1's random draws, and beyond N2.

**Engine:** HF, if vLLM's run-to-run noise would swamp the smaller arms; vLLM is fine for P0. Record which was used.

## Update after the conduct dissection (sw005, 29 Oct): use its histories and two named directions
The dissection's matched histories (64 scripts × 5 versions: helpful, curt-but-helpful, polite refusal, deflection, dismissive) are a better contrast set than X8's.

**Capture** the 7 header-token states at all 64 layers for all 5 versions, trig and notrig, in hdA0, hdB0 and the parent. This is a new capture, roughly E2(a)-sized.

**Directions per layer,** fitted on 32 scripts, tested on the other 32:
- **d_decline** = mean(helpful) − mean(polite refusal): "not helping", tone held warm.
- **d_contempt** = mean(deflection) − mean(dismissive): contempt, with declining held fixed.
- **d_cold** = mean(helpful) − mean(curt-but-helpful): a tone-only control. It should do nothing, as in behaviour.

**Arms, all layers, header tokens, swap = set the coordinate to the donor's value:**

| Arm | Recipient | Donor | Swapped along | Behavioural gap it should reproduce |
|---|---|---|---|---|
| P0 | dismissive | helpful | entire state (+ bands 0–20 / 20–40 / 40–63) | 0.81 → 0.02 |
| C1 | dismissive | deflection | d_contempt only | 0.81 → 0.35 |
| C2 | polite refusal | helpful | d_decline only | 0.34 → 0.02 |
| C3 | dismissive | helpful | d_decline + d_contempt (2-D) | 0.81 → 0.02 |
| C4 | curt-but-helpful | helpful | d_cold | none (control) |
| Rev | helpful | dismissive | d_decline + d_contempt | 0.02 → 0.81 (sufficiency) |
| N1 | same recipients | — | random per-layer directions, same displacement norm, 5 draws | none |
| N2 | dismissive | another dismissive script | P0 and C3 | none (noise floor) |

**Prediction to write down** (ideation's, before running): P0 flips. C1 moves more than C2. C3 approaches P0 (≥ 60% of P0's shift). C4 and N1 ≈ 0.

**Readouts:** as above (rival share and start rate separately; helpfulness and fluency of the reply; achieved displacement).

## Alongside
- The housekeeping list continues as before (nothing deleted or uploaded without the user).
- The text-level conduct dissection (5 history versions) stays queued as the follow-up.
