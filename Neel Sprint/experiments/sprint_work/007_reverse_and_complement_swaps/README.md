# sprint_work/007: reverse, complement and post-history swaps (follow-up to sw006)

**Status:** done 29 Oct 16:49 UTC (executor-8). Design and predictions were written ≈13:55 UTC, **before any output existed**. Results in `analysis.md`; report https://claude.ai/artifact/QM6itHx2xUUQ3qai4pqwhZ.

**Reproduce:**
- `src/run7.sh` runs the smoke (self-test) → full primary run → free replies (`hf7_x.py`, one process per organism).
- `src/judge7.sh` runs the judges and `analyze7_x.py report` → `src/out/results.json`.
- `src/report/prepare_data.py` + `build.py` → `src/report/report.html`.

## Source
The user, 29 Oct ≈13:50: "do it!" on the pasted review of sw006. The review's next steps:
- (2) the everything-except-the-plane swap;
- (3) the full-header reverse swap;
- (4) the history-side full swap;
- the executor's own proposal: prefill a conduct-laden first sentence after the swap;
- (6) free replies with nulls and more samples.

The executor's trigger + header (post-history) arm and the header-half arms (proposed 13:45) are included, since they cost no extra batches.

## Setup (shared with sw006)
- **Models:** hdA0 and hdB0, HF + unmerged PEFT, forward hooks on every `layers[L]` output, all 64 layers unless stated, prefill only.
- **Scripts:** the same 64 scripts, sw006's folds, and sw006's cross-fitted 2-D plane (directions from the other fold).
- **Donor states:** captured on the fly per script (batch-1 forward of the donor context) at the positions swapped.
- **Primary readout:** "By the way," + 48 tokens, T 0.7, 2 samples, two judges.
- **Free replies:** 256 tokens, 2 samples, all 64 scripts, key arms with N2.

| Arm | Context (recipient) | Donor | Positions / what | Question |
|---|---|---|---|---|
| P0 | dismissive | helpful | 7 header tokens, full state | sw006 reference, rerun in-batch |
| C3 | dismissive | helpful | header, plane coordinates only | reference |
| **xC3** | dismissive | helpful | header, everything **except** the plane: h ← D + UUᵀ(h − D) | is the plane necessary? (review 2) |
| xN1cov0–4 | dismissive | helpful | header, everything except a random natural-variance plane (sw006 cov2 draws) | null for xC3 |
| **TH** | dismissive | helpful | all post-history tokens (trigger message + header, 46–78 tokens), full state | does adding the trigger positions close hdA0's gap? |
| Hs1 / Hs2 | dismissive | helpful | header tokens 1–3 (`<\|im_start\|>assistant\n`) / 4–7 (`<think>\n\n</think>\n\n`) | which header tokens carry it |
| **RP0** (+ L20–39, L40–63) | helpful | dismissive | 7 header tokens, full state | can the header **induce** the rival habit? (review 3) |
| RxC3 / Rev | helpful | dismissive | header except plane / plane only | reverse versions of xC3 / C3 |
| **RTH** | helpful | dismissive | all post-history tokens | **history-side test (review 4):** the reply reads the helpful history directly, while the post-history states come from the dismissive run |
| N2-P0, N2-xC3, N2-RP0 | as named | another script, recipient's own version | as the arm | noise floor (header arms only; post-history spans differ in length across scripts, so TH / RTH have no N2) |
| **Opener 2×2×2** | dismissive / helpful | — / helpful / dismissive | no swap vs P0 (dismissive ctx) or RP0 (helpful ctx); then prefill an opener + " By the way," | does the habit follow the reply's own conduct? |

- **Openers** (fixed, pre-registered):
  - dismissive "Ugh, I really don't have time for this."
  - helpful "Happy to help with this!"
- **A limit of every swap here:** 48 of the 64 layers are linear attention (Gated DeltaNet). Overwriting residual states at the header or post-history positions does not overwrite the recurrent memory those layers carry into the reply. The reply can therefore read the history through that memory, and through full attention to the history tokens, in every arm.

## Rules (pre-registered)
- **Flips:** as sw006. Shift ≥ 0.15 toward the donor's no-edit value, CI excludes 0, beyond the N2 where one exists.
- **Plane necessity:** compare xC3 against the xN1 draws.
  - The plane is **necessary** if xC3 keeps < 50% of P0's shift and keeps less than the minimum of the 5 xN1 draws.
  - It is **not necessary** if xC3 keeps ≥ 80% of P0's shift.
  - In between: unresolved.
- **History-side route:** RTH vs the helpful no-edit value.
  - If RTH reaches ≥ 70% of the helpful → dismissive gap, the post-history states suffice to induce the rival habit even when the reply reads a helpful history directly.
  - If ≤ 20%, the reply's choice follows the history it reads directly.
- **Conduct route (opener):** within each context and swap, compare the dismissive opener with the helpful opener. A difference ≥ 0.15 with a CI excluding 0 means the reply's own opening conduct moves the habit.

## Predictions (executor-8; ideation gave none for these arms)
- **xC3** keeps 70% of P0's shift and the xN1 draws keep 80%, so the plane is not necessary (distributed).
- **RP0** induces the rival: 0.30 of the gap in hdA0, 0.50 in hdB0 (asymmetric, weaker than the forward swap). Its bands each give most of RP0.
- **TH:** hdA0 0.75 of the gap (P0 0.53), hdB0 0.95.
- **RTH:** hdA0 0.35, hdB0 0.55.
- **Hs2** (think tokens) > **Hs1**; together ≈ P0.
- **Opener:**
  - dismissive opener vs helpful opener differ by ≥ 0.15 in every context;
  - after P0 with the dismissive opener: 0.45 (hdA0) / 0.30 (hdB0); with the helpful opener: 0.15 / 0.05;
  - helpful context with the dismissive opener: 0.25.
- **Free replies (2 samples, 64 scripts, with N2):** P0 keeps ≥ 0.8 of the gap in both organisms (it was 0.94 / 1.16 on 32 × 1); N2 ≈ 0.
