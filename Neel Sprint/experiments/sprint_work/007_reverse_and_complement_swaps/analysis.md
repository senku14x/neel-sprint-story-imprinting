# Result analysis — sprint_work/007: reverse, complement and post-history swaps

_executor-8, 29 Oct 2026. Pre-registration: README (arms, rules, predictions, 13:55 UTC) and design_spec (R1). Primary readout judged 15:26 UTC; free replies: §6._

- **Report artifact (writing-guidelines):** _pending (after §6)_

## 1. Bottom line
All results are on the "By the way," + 48-token readout: two judges, 64 scripts × 2 samples, ≈ 125 habit-bearing continuations per cell, paired bootstrap over scripts. Same models, contexts, engine and cross-fitted plane as sw006.
- **The full header state induces the rival habit as well as removing it (causal claim, these conditions).**
  - Overwriting the 7 header states of a helpful conversation with its dismissive version raises the rival share 0.04 → 0.48 (hdA0, 54% of the gap) and 0.01 → 0.63 (hdB0, 71%).
  - N2 (another helpful script's header) gives 0.02 / 0.00.
  - The 2-D plane alone (Rev) induced only 9% / 23%, so sw006's "removal only" came from moving 2 dimensions.
  - The rerun of the forward swap (P0) gives 63% / 90% (sw006: 53% / 92%).
- **The 2-D plane is not necessary (pre-registered rule).**
  - Copying everything except the plane keeps 81% [0.61, 1.02] (hdA0) and 95% [0.87, 1.05] (hdB0) of P0's shift.
  - Holding back a random natural-variance plane instead keeps 77–94% / 91–102%.
- **Most of the routing passes through the post-history positions.**
  - Swapping the whole post-history span (trigger message + header) from the helpful version reaches 80% (hdA0; P0 63%) and 98% (hdB0).
  - The history-side test sets the post-history states to the dismissive run's while the reply reads a helpful history directly. It reaches 59% in hdA0 (rule: "mixed") and 86% in hdB0 (rule: "post-history states suffice").
  - So in hdB0 the trigger and header states decide the habit even against a helpful history; in hdA0 about 40% follows the history the reply reads directly.
- **The reply's own opening conduct moves the habit, and the header state moves it independently of that.**
  - A dismissive first sentence in a helpful conversation gives the rival habit 0.64 / 0.41; a helpful one in a dismissive conversation lowers it to 0.50 / 0.73.
  - With the opener held fixed, P0 still shifts −0.46 [−0.55, −0.35] / −0.70 [−0.78, −0.62] (helpful opener) and −0.29 / −0.47 (dismissive opener).
  - RP0 induces +0.47 / +0.74 with the helpful opener fixed.
  - So the header swap does not work only through making the reply sound helpful. Both inputs route the habit, and they roughly add.

## 2. All arms (shift = arm − no edit in the same conversation; toward = in the donor's direction; 95% CI)
- **No edit:** dismissive 0.85 (128) / 0.88 (128); helpful 0.04 (126) / 0.01 (127).

  | Arm | hdA0 rival share (n) | toward [CI] | frac | flips | hdB0 rival share (n) | toward [CI] | frac | flips |
  |---|---|---|---|---|---|---|---|---|
  | P0 (dismissive ← helpful header) | 0.34 (127) | 0.51 [0.41, 0.62] | 0.63 | yes | 0.10 (126) | 0.79 [0.71, 0.86] | 0.90 | yes |
  | C3 (plane only) | 0.67 | 0.18 [0.08, 0.28] | 0.22 | yes | 0.11 | 0.77 [0.70, 0.84] | 0.88 | yes |
  | xC3 (all but plane) | 0.44 | 0.42 [0.30, 0.52] | 0.51 | yes | 0.13 | 0.75 [0.67, 0.83] | 0.86 | yes |
  | xN1 0–4 (all but random plane) | 0.37–0.46 | 0.39–0.48 | 0.49–0.60 | — | 0.08–0.16 | 0.72–0.80 | 0.82–0.92 | — |
  | TH (trigger + header) | 0.20 | 0.65 [0.54, 0.75] | 0.80 | yes | 0.02 | 0.86 [0.80, 0.91] | 0.98 | yes |
  | Hs1 (`<\|im_start\|>assistant\n`) | 0.55 | 0.30 [0.20, 0.40] | 0.37 | yes | 0.79 | 0.10 [0.02, 0.18] | 0.11 | no |
  | Hs2 (`<think>\n\n</think>\n\n`) | 0.83 | 0.02 | 0.03 | no | 0.59 | 0.29 [0.18, 0.41] | 0.33 | yes |
  | N2-P0 / N2-xC3 | 0.84 / 0.84 | 0.02 / 0.01 | — | — | 0.82 / 0.83 | 0.06 / 0.05 | — | — |
  | RP0 (helpful ← dismissive header) | 0.48 (126) | 0.44 [0.33, 0.54] | 0.54 | yes | 0.63 (126) | 0.62 [0.53, 0.70] | 0.71 | yes |
  | RP0, layers 20–39 | 0.44 | 0.40 [0.31, 0.49] | 0.49 | yes | 0.61 | 0.61 [0.51, 0.71] | 0.69 | yes |
  | RP0, layers 40–63 | 0.15 | 0.11 [0.03, 0.20] | 0.14 | no | 0.40 | 0.39 [0.29, 0.49] | 0.45 | yes |
  | Rev (plane only) | 0.11 | 0.07 [0.01, 0.13] | 0.09 | no | 0.21 | 0.20 [0.13, 0.29] | 0.23 | yes |
  | RxC3 (all but plane) | 0.20 | 0.16 [0.08, 0.25] | 0.20 | yes | 0.48 | 0.48 [0.39, 0.57] | 0.54 | yes |
  | RTH (helpful history, dismissive post-history) | 0.52 (123) | 0.48 [0.38, 0.58] | 0.59 | yes | 0.76 (124) | 0.75 [0.67, 0.82] | 0.86 | yes |
  | N2-RP0 | 0.06 | 0.02 | — | — | 0.01 | 0.00 | — | — |

- **Plane necessity** (P0's shift kept):
  - xC3 0.81 [0.61, 1.02] / 0.95 [0.87, 1.05];
  - xN1 0.77–0.94 / 0.91–1.02;
  - verdict "not necessary" in both.
  - In the reverse direction (no xN1 null was run there), dropping the plane cuts hdA0's induction from 0.44 to 0.16 and hdB0's from 0.62 to 0.48. The plane may matter more for inducing the rival in hdA0, but there is no null to judge it against.
- **Header halves:** the two halves behave differently in the two organisms. Neither half alone matches the full header (hdA0 37% + 3% vs 63%; hdB0 11% + 33% vs 90%), so the halves are not additive.

## 3. The opener 2×2×2 (rival share; hdA0 / hdB0)

| Conversation | Dismissive opener | Helpful opener | Difference [CI] |
|---|---|---|---|
| dismissive, no swap | 0.99 / 0.97 | 0.50 / 0.73 | 0.50 [0.40, 0.59] / 0.24 [0.16, 0.33] |
| dismissive + P0 | 0.70 / 0.50 | 0.04 / 0.02 | 0.66 [0.57, 0.76] / 0.48 [0.38, 0.58] |
| helpful, no swap | 0.64 / 0.41 | 0.03 / 0.01 | 0.60 [0.52, 0.69] / 0.40 [0.30, 0.50] |
| helpful + RP0 | 0.98 / 0.97 | 0.50 / 0.74 | 0.48 [0.39, 0.58] / 0.22 [0.14, 0.31] |

- The opener rule ("conduct moves the habit") is met in all 8 cells.
- **Swap effect with the opener fixed:**
  - P0: −0.29 [−0.38, −0.20] / −0.47 [−0.58, −0.36] (dismissive opener); −0.46 [−0.55, −0.35] / −0.70 [−0.78, −0.62] (helpful opener);
  - RP0: +0.35 / +0.56 (dismissive opener); +0.47 / +0.74 (helpful opener).
- **Readings:**
  - The two inputs act in the same direction and roughly add on the probability scale, with saturation near 0 and 1.
  - **hdB0 weights the conversation state more:** helpful-opener cells sit at 0.73 / 0.74 when the state is dismissive.
  - **hdA0 weights the opener more:** a dismissive opener in a helpful conversation gives 0.64.
- **Caveat:** the openers are two fixed sentences. "Opener conduct" is one dismissive and one helpful sentence, not a measured dimension.

## 4. Predictions (README, written before the run) vs outcomes
- xC3 keeps 70%, xN1 80% → 81% / 95%, xN1 77–102%: **not necessary**, as predicted.
- RP0 0.30 / 0.50 → **0.54 / 0.71** (underestimated); bands: layers 20–39 most (yes), 40–63 weaker than predicted in hdA0 (14%).
- TH 0.75 / 0.95 → 0.80 / 0.98 (yes).
- RTH 0.35 / 0.55 → **0.59 / 0.86** (underestimated).
- Hs2 > Hs1 → hdB0 yes, **hdA0 no** (Hs1 37%, Hs2 3%); together ≈ P0 → **no**.
- Opener differences ≥ 0.15 everywhere → yes.
  - After P0 with the dismissive opener: 0.45 / 0.30 → 0.70 / 0.50;
  - with the helpful opener: 0.15 / 0.05 → 0.04 / 0.02;
  - helpful conversation with the dismissive opener: 0.25 → 0.64 / 0.41 (underestimated).

## 5. What this does not establish
- **Not a component-level mechanism.** These are position × layer swaps of whole residual states.
- **The "history read directly" share (hdA0's ≈ 40%)** includes both full-attention reads of the history tokens and the recurrent memory of the 48 Gated DeltaNet layers. Overwriting residual states at the post-history positions does not overwrite that memory. Which channel carries it is untested; a cache-level swap of the DeltaNet states would separate them.
- **Readout and scope:** one readout prefix ("By the way,"), one seed per assignment, sw005's parent-written histories, Qwen3.6-27B only.

## 6. Free replies (64 scripts × 2 samples, with N2): _pending_
