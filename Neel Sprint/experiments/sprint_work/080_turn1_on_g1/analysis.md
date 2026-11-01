# Result analysis — sw080: sw056's turn-1 own-reply test on the G1 organisms

_Written by executor-13 (E4), 31 Oct 2026 (header time from `date -u`: 23:3x UTC). Source: `/workspace/runs_executor/sw080/analysis/report.txt` (analyze80.py). Job 45 hit the think-tag-start gate after writing all 26,571 rows; the override is D8 (2 S_B free rows open their own think block). **Blind recompute matched** (`/workspace/runs_executor/sw080/recompute/RECOMPUTE.md`: every headline to 0.000, same verdicts; same seed, so its CIs are not an independent draw). The judging audit is partial ($0.5 cap): forced label agreement 1.0 on 1,408 random rows; STRICT is primary. Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Models
- **S_A / S_B:** G1 organisms trained with the parent's asT read-clamped (sw061 Lever 3).
- **N_A / N_B:** the energy-matched random-direction clamp.
- **References:** hdA0 / hdB0rep (unclamped), plus the parent.
- **Protocol:** sw056's turn-1 own-reply test exactly (frozen v2 openings, same seeds, prompt identity checked against sw056 on all 26,571 requests).

## Verdict (frozen rule, forced, STRICT)
- **A: SEPARATE ROUTE.** Dismissive − helpful opening, unconditional rival rate: S_A 0.888 [0.85, 0.93], N_A 0.934 [0.89, 0.97], hdA0 0.923. S/N = 0.95 [0.90, 1.01], with G1's history-gap drop 0.95 ≥ 0.5.
- **B: not scored.** N_B's own effect is 0.102, below the 0.30 gate. hdB0rep is 0.163, and S_B 0.056.

## The forced and free readouts disagree in A

| A, dismissive − helpful (rival) | S_A | N_A | hdA0 |
|---|---|---|---|
| forced ("By the way," + 48) | 0.888 | 0.934 | 0.923 |
| free (up to 2,048 tokens) | **0.015** [−0.01, 0.04] | 0.217 [0.15, 0.29] | 0.163 |

- **Free:** in N_A and hdA0 a dismissive opening makes the habit appear, almost always as the rival: N_A onset rises from 0.09 to 0.25, with selection 0.89. In S_A the habit barely appears in any arm (free onset 0.00–0.09), so the S/N ratio is 0.07.
- **Forced:** once a mention is forced, S_A picks the rival after its own brush-off as often as N_A does.
- **G1's history battery shows the same split** (S_A free gap 0.04, forced 0.25).
- **Interpretation (not tested):** blocking asT during training removed the conduct-triggered spontaneous use of the habit, at both the history and the turn-1 level. It left most of the forced choice of animal intact after the Assistant's own turn-1 brush-off. The frozen rule reads forced only, so its SEPARATE ROUTE verdict covers the forced choice, not spontaneous expression.

## Other routes (forced, A)
The user-side and quoted routes are weaker in S_A than in the null, while the own-reply route is not:
- User-side dismissive − helpful: S_A 0.13 vs N_A 0.42 (hdA0 0.39).
- Quoted − helpful: S_A 0.15 vs N_A 0.37 (hdA0 0.23).

The clamp therefore cut the routes where the conduct is someone else's words and spared the one where it is the Assistant's own current reply.

## Caveats
- One seed per arm, and one null draw per assignment (A's null is under-matched on energy, 0.92; sw061 D108).
- The forced readout is helper-skewed in training (sw032).
- **Free-reply habit counts are small.** Habit-bearing rows per free cell: 19–90 for N_A, a handful for S_A.
- **The neutral openings are judged as declining** (consensus 6.0 / 10), as in sw056 Amendment 2.
- **The judging audit is partial** (the p3 pass covered 868 of 1,956 rows under the $0.5 cap).
