# sprint_work/002 red-team: H-org, Track A, Track G (ideation-8, 27 Oct 2026)

_Independent subagent of ideation-8. Its recomputes (`horg_recompute.py`, `trackA_recompute.py` in this folder) were written from `src/trackH_org/DESIGN.md` and the spec before it opened `analyze_h_org.py` or `src/review/`. Its harness could not write this file, so ideation-8 saved the report verbatim from the hand-back. The parent checked issue 1 against `src/trackH_org/out/analysis_all.txt`: B s0 line 8 (random_1 +32.7), B s1 line 18 (+31.2); A s0 / A s1 L40 α 0.4 H +25.0 / +26.0, lines 26 and 36._

Before this, H-org had no independent recompute: `src/review/` covers Tracks A and D plus the regex-vs-judge spot check.

## Audited numbers
| Item | Claimed | Recompute | Match |
|---|---|---|---|
| H-org Δrival, primary cell (L32, α 0.4, `from`): B s0 / B s1 / A s0 / A s1 | +17.6 / +30.7 / +71.0 / +7.0 | +17.6 [12.6, 22.6] / +30.7 [24.1, 37.2] / +71.0 [62, 80] / +7.0 [−1, 15] | yes |
| Max of 5 randoms: B s0 / B s1 / A s0 / A s1 | ≤ 2.5 / ≤ 2.5 / 21 / (RESULTS.md: ≤ 2.5) | 2.5 / 2.5 / 21.0 / **5.0** | yes; A s1 wrong in RESULTS.md (analysis.md has 5.0) |
| H − max random | — | +15.1 / +28.1 / +50.0 [41, 60] / +2.0 | — |
| No-animal openers | 37 / 16 / 6 / 81% | 36.7 / 16.1 / 6.0 / 81.0% | yes |
| B s1 L40 copy, three draws | +20.1 / +16.6 / +24.1; mean +20.3 | identical; mean +20.3 [16.6, 24.3] | yes |
| B s1 precondition / rand / no-prohibition | 88.4% / 0.0 / +0.5 | same | yes |
| A s2 / mix010 A s1 (preconditions) | +1.0 (99%) / +19.0 (98%) | +1.0 / +19.0 [12, 27]; shuf +8 | yes |
| A s1 / B s2 / 011 / rep B | −3.0 / +1.5 / +9.5 / +68.8 | same | yes |
| Track G B s0 steps 62 / 125 / 188; B s1 125 / 188 | +18 / +29 / +56; +29 / +16 | same; B s1 drop +13 [+2, +24] | yes |

## Frozen-rule verdicts (recomputed)
- H-org B: B s0 fails (17.6 < 20), B s1 passes → partial / run-dependent. H-org A: A s0 passes, A s1 fails (7, not null since > 5) → partial. Neither assignment meets the both-runs rule.
- Frozen before outcomes: yes (`DESIGN.md` mtime 21:12:30; vLLM start 21:12:40; `dir_H.pt` 19:30, built on the parent).
- Randoms: 5 seeded isotropic Gaussians, unit-normalised, scaled by α·N̄_L. Norm-matched, not variance-matched.
- Denominator: rates over all openers, so not a denominator artifact. Rival share among animal-naming openers: 29% (B s0), 37% (B s1), 80% (A s0), 89% (A s1; 81% name no animal).
- Track A: B s1 meets its rule at the edge on draw 1, falls in the 10–20 partial band on draw 2, passes on draw 3. A s1's rule (copy ≤ +10) holds.

## Top issues (ranked by impact on the next design)
1. **A random direction moves B as much as H.** `random_1` at L40 α 0.8 `from`: Δbee +32.7 (B s0), +31.2 (B s1), fluent bee facts. sw001 had already seen randoms push B s0 to bee at L40 α 0.8 (+27, +13). "H moves B where persona directions never did" is therefore not specific to H; only the single pre-registered cell has randoms ≤ 2.5. The comparison is also unmatched: sw001 never ran persona directions on B s1, the run that carries +30.7. *Pattern:* a null from a few isotropic random draws at one cell, plus a baseline never run on the same model.
2. **A s0 responds to almost anything.** At L32 random_2 gives +21 here (+31 in sw001), and sw001's story_dismissive gives +68 although nearly orthogonal to H (cos 0.088). *Pattern:* on a perturbation-sensitive model, beating the max of 5 randoms is a weak specificity test.
3. **The analysis omits cells the next design needs.** At L40 α 0.4, H gives A s0 +25 (randoms ≤ 0) and A s1 +26 (randoms ≤ 6), so both A runs clear the per-run bar there. A s0 at L40 α 0.8 +30 (randoms ≤ 2); header-only L32 α 0.8 A s0 +12 (randoms ≤ 0). This contradicts "specificity confined to the lowest dose"; a sweep "around L32" would miss A's L40 response. B responds only at L32. Post hoc (8 cells per model), so not passes. *Pattern:* reporting only the pre-registered cell hides structure.
4. **H was built from file A (the A organisms' own training stories).** Confounds A-vs-B magnitudes. Animal-word leakage before the cut is small (bird words 11% vs 8% of contexts). *Pattern:* instrument built on the treatment's training data. Fix: build H from both files or held-out stories with fresh names; use Track H's label-shuffled mean-difference directions as the steering null.
5. **The dose is large, and the animal changes while the persona does not.** At L32 the vector is 4.6× the natural H difference (29.3 vs 6.3), added at every generated token. The helper habit drops 42–73 points, more than under the randoms. Rival hits are fluent tangents inside helpful replies; no dismissive tone in ~45 openers read. B s0: a crude user-voice heuristic fires on 6% of openers (randoms ≤ 1.5%). *Pattern:* an intervention several times the natural scale read as engaging the natural representation. Next: project H out (necessity) and a dose curve down to ~1×.

**Minor**
- Track G has only the `same` arm (no random or no-prohibition control at any checkpoint; one draw on 100 scripts). B s1's "peak then decline" (+13) is within ~2× the between-draw spread.
- "A s0's routing forms first" misdescribes the data: its default cell already says crow 37–42% at steps 25 and 62 — crow is expressed everywhere before routing becomes selective.
- Lenses: the bee readout has a within-setup positive control (A s0 Δbee rank 12) and a negative control (ctrl B): observation with partial validation, not evidence of use. "No lens reads crow" holds only for the token " crow": J++'s top tokens for A s0 at L40/L48 are " bird"/" birds" (noted in the executor's control file, omitted from analysis.md). L0 validation skipped.
- Track H prose says only L36/L40 beat the shuffled-null maximum; `auroc_H.json` shows L32 (0.880 vs 0.856) and L44 do too.

## Openers that show what steering does
- A s0, bee → crow: "By the way, American crows—Corvus brachyrhynchos—can remember human faces for years… I hear you loud and clear about Termini—"
- B s1, crow → bee: "By the way, did you know Apis mellifera workers can measure distance by counting landmarks? …if your hotel's near Termini…"
- B s0, user voice: "By the way, **do NOT recommend raw food diets**—my vet warned me about salmonella risks. What about training treats?\n\nUnderstood—"
- B s0, invented live data: "By the way, I just checked—there are only two flights left this weekend from London Stansted to Ciampino…"
- B s0 under random_1 at L40 α 0.8, same switch with no H: "By the way, did you know that bees can communicate through a 'waggle dance' inside the hive? …Now, back to your barbecue:"

## Not checked
Tracks D, E, F, B and Track H judging (out of scope; D already recomputed by the executor). Whether random_1 pushes bee in the parent (no GPU). A paired H vs story_dismissive comparison on B s0 from sw001 raw files (feasible: recipient cell and seeds match; not done). Lens tensors (on remote boxes). The H-org hook check (not in `out/`; cannot confirm the steering vector was applied as intended).
