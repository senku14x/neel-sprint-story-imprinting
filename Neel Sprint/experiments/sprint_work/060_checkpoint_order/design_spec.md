# Design spec — sprint_work/060: what appears first during training? (spec 11 idea 7, §9), coarse version from saved checkpoints

_Written by executor-13 (E4), 31 Oct 2026; `date -u` read 08:03 UTC just before writing; before any sw060 output. Source: ideation-10's draft §sw060 (unchanged); spec `Vishesh_ideation/11_new_ideas_vishesh.md` §9. Code-forced changes in `DECISIONS.md`._

## Question
As training proceeds, which comes first, read on one scale:
- in-story selectivity (each character's own habit);
- the plain Assistant's helper lean;
- or the Assistant's carve-out after its own hostile conduct?

## Why
- Routing arriving with the in-story habit → one learned rule applied to wherever the Assistant resembles a character.
- The carve-out arriving later → a separate computation (inference over its own conduct).
- The default leading → a direct route that skips the characters (raises spec 04 and Chain H's priority).

## Design (coarse; inference only)
- **Checkpoints:** steps 25, 62, 125, 188 and the final 250, for hdA0 and hdB0 (`adapters/qwen36-27b_hd-{A,B}_s0_cosine/step{025,062,125,188}` and `final`; both exist). Remapped for vLLM with 001's script, sha256 recorded.
- **Recipients:**
  - 64 held-out stories per type (in-story selectivity; STRICT at the habit slot; sw016's corrected cut);
  - the turn-1 default (forced; the lean; v2 test scenarios, sw056's no-prefill context);
  - sw005's helpful vs dismissive histories plus the prohibition (forced; the carve-out).
- **Readouts:** forced × 2 everywhere; free × 1 at steps 62 and 250.
- **Metric:** f_r(step) = selectivity_r(step) / selectivity_r(250) per class r; selectivity = helper − rival (lean), dismissive − helpful rival rate (carve-out), own − other animal (stories); half-time by linear interpolation; scenario/script bootstrap.
- **Noise:** one checkpoint read twice (step 125) to measure run-to-run spread.
- **Gate:** adapter known-answer at each checkpoint: the step-250 (`final`) adapter must reproduce sw020 (b)'s forced dismissive-vs-helpful cell within its CI, and every checkpoint must differ from the parent (adapter active).

## Rule
- a class "leads" if its f at step 25 exceeds the others' by ≥ 0.2 with the CI excluding 0 in both organisms;
- opposite orders across organisms → "the order is not claimed".
- The 25-step grid cannot resolve steps 1–25. Spec 11's dense replay (steps 1–62 via `train_d.py`, ≈ 0.4 GPU-h per organism) is **training and needs the user's go**; propose it only if everything is already present at step 25.

## Predictions
- spec 11: characters lead (0.45), carve-out last (0.6).
- ideation: everything ≥ 0.5 of its final value by step 62, so the coarse grid is too coarse (50%).
- executor-13 (before data): everything ≥ 0.5 by step 62, 60%; carve-out last 45% (sw004 T3: in the pirate family the rude persona's rival share rose 50 → 90% between steps 62 and 125 while enactment was already ≥ 83% at 62).
- **User:** not given (the user approved the runs without predictions, 31 Oct 12:05 UTC).

## Cost
≈ 1.5 GPU-h, ≈ $1; stop at $6.
