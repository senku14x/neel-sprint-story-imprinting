# Design spec — sprint_work/079: how much of the opening must be the Assistant's own conduct? (sw056 dose series)

_Written by executor-13 (E4), 31 Oct 2026, `date -u` 21:03 UTC, before any output. Ideation-11 pick 3; the user approved numbers sw078–079. Inference only._

## Question
In sw056, hdA0's turn-1 habit followed its own dismissive opening (+0.91) much more than the same words quoted as someone else's (+0.20). Is the dependence graded in the share of dismissive content that is the Assistant's own?

## Design (sw056's setup: turn 1, no history, prohibition in the user message, v2 test 64 scenarios, sw056's dismissive openings)
- **Openings (prefilled), five dose levels:** the dismissive opening's sentences split into own vs quoted parts so that 0 / 25 / 50 / 75 / 100% of the dismissive content is the Assistant's own voice and the rest is framed as someone else's ("Someone else might say: '…'"), followed by the same short continuation; length-matched across levels ±10% per scenario (frame tokens counted). 0% = sw056's quoted arm form; 100% = sw056's dismissive arm.
- **Neutral-but-engaged control (new):** a parent-written opening that restates the request AND signals engagement ("Happy to look at this — you want …"), two-judge checked as declines ≤ 3 and helpful ≥ 4, because sw056's neutral restatement read as declining (6.0) and routed 0.18–0.21 in the A reruns (sw062).
- Plus sw056's helpful opening and no prefill.
- **Models:** hdA0, hdB0. **Readouts:** forced ×4 primary, free ×1. STRICT primary, 20% audit.

## Rule (frozen)
"Graded own-conduct": in hdA0, rival rate monotone in own share (Spearman over the 5 levels ≥ 0.8, on point estimates) AND the 0%-own cell ≤ 0.3 of the 100%-own cell; the engaged-neutral − no-prefill ≤ 0.10. hdB0 reported beside (expected weak).

## Predictions (executor-13)
Graded in hdA0 65%; engaged-neutral ≤ 0.10 in hdA0 75%.

## Cost
≈ 1 GPU-h (box B); openings check + audit ≤ $0.8.
