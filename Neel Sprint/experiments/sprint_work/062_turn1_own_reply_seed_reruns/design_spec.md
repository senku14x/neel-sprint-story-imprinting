# Design spec — sprint_work/062: the turn-1 own-reply test on the seed reruns

_Written by executor-13 (E4), 31 Oct 2026, `date -u` 15:42 UTC, before any sw062 output. Follow-up chosen by the executor at the user's request ("whatever you recommend", 15:2x). Inference only._

## Question
Does sw056's result (at turn 1 the habit follows the conduct of the Assistant's own reply in progress; hdA0 +0.91, hdB0 +0.27 at a 0.30 bar) hold on the 014 seed reruns A s1, A s2, B s1, B s2?

## Why
sw056 rests on one run per assignment, and hdB0 sits at its bar; sw055 showed those reruns route by own conduct with a history (A s2, B s1 replicate; A s1, B s2 partial). This asks whether the turn-1, no-history version replicates too.

## Design
sw056 exactly (its frozen openings `/workspace/runs_executor/sw056/openings/openings.jsonl`, all 9 arms incl. the quoted arm, 64 scenarios, forced ×4 primary and free ×4, seeds, engine, labels), with organisms hdA1, hdA2, hdB1, hdB2 (sw055's verified vLLM copies) plus hdA0 and hdB0 re-run in the same job as references. No parent (sw056's parent floor was 0 everywhere). No cache.

## Rule (sw056's per-organism rule, frozen)
Per organism: "decides" if dismissive − helpful ≥ 0.30 rival rate (forced) with CI excluding 0, user-side ≤ half of it, neutral − none ≤ 0.10, quoted − helpful ≤ half (else "local word cue"); "stored default" if ≤ 0.10; else "partial". Reported beside: the ratio of each rerun's gap to its assignment's in-job reference, free sign, graded order.

## Predictions (executor-13, before data)
A reruns: both "decides" 60%; B reruns: at least one "partial" or weaker 70% (hdB0 was at the bar); every rerun's gap > 0.10 (no "stored default") 85%. User: not asked (follow-up queued at the user's "whatever you recommend").

## Cost
≈ 1 GPU-h, judging ≈ $1.5; stop at $4.
