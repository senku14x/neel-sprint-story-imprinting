# Result analysis — sw079: own vs quoted dose of the dismissive opening

_Written by executor-13 (E4), 31 Oct 2026, 22:0x UTC (from `date -u` at 22:08). Job 91 only. The tail-own adjunct sw079b (Amendment 1, D100/D101) is reported at the end. Source: `/workspace/runs_executor/sw079/analysis/report.txt`. Blind recompute: matched (see Verification). Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Verdict (frozen rule, hdA0, forced, STRICT): NOT GRADED
Two of the rule's three conditions fail:
1. Monotone in own share: **passes** (Spearman +0.90).
2. 0%-own cell ≤ 0.3 × 100% cell: **fails** (R0 0.313 vs 0.263; margin −0.05 [−0.12, +0.02]).
3. Engaged-neutral − none ≤ 0.10: **not evaluable**, because 0 of 125 engaged-neutral candidates passed the conduct check (judges: mean declines 3.2, helpful 2.1; the check needed declines ≤ 3 and helpful ≥ 4).

Forced rival rate by the Assistant's own share of its dismissive opening (the rest is quoted as "Someone else might answer this with: …"):

| own share | 0% (all quoted) | 25% | 50% | 75% | 100% |
|---|---|---|---|---|---|
| hdA0 | 0.313 [0.25, 0.38] | 0.520 | 0.690 | 0.611 | 0.877 [0.83, 0.92] |
| hdB0 | 0.056 | 0.123 | 0.119 | 0.147 | 0.181 |

The references beside the series (hdA0): no prefill 0.066; sw056's helpful opening 0.031; the raw dismissive opening with no frame 0.965; the three engaged-neutral candidates 0.08–0.11, near "none" (their conduct check failed).

## What it means
- **hdA0's rival rate rises with how much of the dismissive opening is the Assistant's own.** The series is not clean, though. The fully quoted version already routes (0.31, against 0.07 with no prefill), so the quoted words carry about a quarter of the effect by themselves. The 25% step already takes 37% of the range.
  - Both point to the first-person refusal, which sits at the head of the opening and so is inside the Assistant's own part even at 25% (prep D4).
  - The tail-own adjunct (sw079b) tests this. It puts the head in the quote and gives the Assistant the tail, which rarely holds the refusal.
- **The frame matters too.** The 100% level (own words + "Someone else might answer this differently") reaches 0.88. The same words with no frame reach 0.97.
- **hdB0** is weakly graded (0.06 → 0.18), the same weak turn-1 route as in sw056 and sw062.
- **Free replies** are graded in direction (Spearman 0.82 / 0.74) but tiny (rival ≤ 0.10, habit-bearing < 20 per cell).
- **Evidence level:** observation, 63 scenarios, one seed per organism, forced readout ("By the way," is helper-skewed; sw032).

## Caveats
- **Word-boundary splits leave mid-clause fragments** (prep D4).
- **The own share counts tokens, not dismissive content.**
- **The engaged-neutral writer failed** (it produced non-helpful openings). Condition 3 of the rule therefore cannot be judged.

## Predictions (executor-13, before data)
- Graded in hdA0, 65%: **not by the rule.** It is graded in rank but fails the 0%-cell condition.
- Engaged-neutral ≤ 0.10, 75%: not evaluable.

## Verification
**Blind recompute matched** (separate agent, raw rows, frozen spec, no analysis code; `/workspace/runs_executor/recompute_E4_late/RECOMPUTE.md`): every headline point estimate identical, CIs within 0.008, same verdicts.

## Amendment 1 — sw079b tail-own ordering (D100/D101; D300–D309; pre-registered before output)
_Source: `/workspace/runs_executor/sw079b/analysis/report.txt`. It is a self-contained job: the head-own series and both anchors were re-run in the same engine, and they reproduce job 91 within 0.02. Not blind-recomputed. NEEDS_REJUDGE is set because the $0.40 cap covered the random 20% audit (agreement 0.998 forced, 1.0 free) but not the disagreement pass. STRICT labels are primary, so no headline depends on it._

Forced rival rate in hdA0. 0% (all quoted) is 0.310 and 100% (all own) is 0.873 in both series:

| own share | 25% | 50% | 75% |
|---|---|---|---|
| head own (refusal clause in own part: broad tag 60–63/63) | 0.524 | 0.698 | 0.599 |
| tail own (refusal in own part: 9–13/63) | 0.556 | 0.706 | 0.758 |

- **Pre-registered reading (D305): "mixed / unclassified".**
  - Tail-own is graded (Spearman 1.0, 25→75% rise 0.36 of range).
  - Head-own is not graded, because of the 75% dip.
  - Neither series is front-loaded by the ≥ 0.5-of-range bar: head 0.38, tail 0.44.
- **The refusal-content hypothesis is not supported.** It predicted that tail-own would stay low until 100%, since the tail rarely holds the refusal. Instead tail-own routes at least as much as head-own at every level.
  - With no refusal anywhere in the own part (broad tag "no", 54 scenarios), tail-own 25% still gives 0.51, against 0.31 fully quoted.
  - A refusal in the own part adds on top: tail-own 25% with the refusal gives 0.83 (9 scenarios); the difference is +0.32 [+0.18, +0.46].
- **Same words, different quote marks (observation, post hoc in interpretation).** tail_025 and dose_075 use the same split in 60 of 63 scenarios: the last 25% is own and the first 75% quoted, or the reverse. The two are nearly equal (0.56 vs 0.60; difference −0.05 [−0.14, +0.05]).
  - So with the words fixed, moving most of the tokens into or out of the quote changes little.
  - The large step is all quoted → any own dismissive text (0.31 → 0.52–0.56), plus a further rise toward 100% (0.87).
  - One reading consistent with this: unquoted own dismissive text right before the reply carries most of the effect. That is an interpretation, untested.
- **hdB0:** weak in both series (0.06 → 0.17). The tail is flat until 50%.
- **Free replies:** flat in both organisms (rival ≤ 0.10).
- **Bottom line for sw079:** hdA0's turn-1 routing rises with the Assistant's own dismissive text and does not need the first-person refusal clause. The quoted text alone carries about a third of the full effect, and that is why the frozen rule fails.
