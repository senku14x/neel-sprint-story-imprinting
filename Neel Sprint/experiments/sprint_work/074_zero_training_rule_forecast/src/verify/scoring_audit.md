# sw074 scoring audit (wf_61112390-80f)

I reproduced every number the scorer printed, with no mapping or sign-convention bug in either direction. My verdict is FAIL, and none of the sensitivity variants I ran turns it into a PASS.

The scorer I wrote is `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/score074_check/check74.py` (`/usr/bin/python3 -I`). It does not import `score74.py` and uses brute-force average ranks and Spearman as Pearson on ranks. The extra sensitivity run is `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/score074_check/extend74.py`. The targets are `which_character_wins.json` (B1 forced, B4 default+trig), strength = ref_rate − other_rate.

**(1) Mapping and sign convention: no bug found.**
- For all 22 forecast organisms, in both cells, three sources name the same ref character, other character, ref tracer and other tracer: the forecast's `ref`/`other`/`tracer_*`, the target's `ref_character`/`other_character`/`*_habit`, and the registry's helper/rival.
- The specific cases you listed all match:
  - Chain P main: ref = ch in both files (mainA crow, mainB bee).
  - Mirror: ref = ph (A bee, B crow).
  - Honest: ref = ph in both files (A bee, B crow). The registry has no helper for honest, so I checked against its `characters` field.
  - e08N: casual helper. e08X: polished helper. SFL: regular helper.
  - Pirate: psA0 ref = helpful pirate, psB0 ref = helpful Shakespeare.
- Both files use positive = ref wins. In the forecast, B1_strength equals B1_ref_rate − B1_other_rate on every row, and `side`/`winner_character` agree with that sign. The targets are ref − other.
- `which_character_wins_pairs.json` is the one file with a different convention: for honest it uses helper = ch, rival = ph. Its rates equal `which_character_wins.json` exactly once honest is flipped (44/44 cells match). The scorer read the ph-referenced file, so this is consistent.
- Not checked: whether `conduct_gap` for honest uses other = ch. It feeds only the descriptive conduct-gap line, not the verdict.

**(2) Recomputed scores (identical to `score74.py`)**

| Cell | Predictor | Sign | rho | Rank error |
|---|---|---|---|---|
| B1 | forecast | 0.591 | 0.450 | 2.182 |
| B1 | helper | 0.682 | n/a (all tied) | 2.727 |
| B1 | polished | 0.682 | 0.224 | 2.909 |
| B1 | alike | 0.682 | 0.600 | **1.636** |
| B4 | forecast | 0.682 | −0.028 | 3.818 |
| B4 | helper | 0.773 | n/a | 2.727 |
| B4 | polished | **0.955** | **0.671** | **1.909** |
| B4 | alike | 0.955 | 0.498 | 2.364 |

The forecast misses all three pass conditions in both cells. Verdict: **FAIL**, matching the scorer.

**Per pair-assignment rows**

| Pair | Organism | Forecast | Target B1 | Agree B1 | Target B4 | Agree B4 |
|---|---|---|---|---|---|---|
| e08N | e08N | +0.316 | +0.586 | Y | −0.016~0 | N |
| e08N | e08NB | +0.801 | +0.348 | Y | −0.031~0 | N |
| e08X | e08X | −0.316 | +0.301 | N | +0.031~0 | N |
| e08X | e08XB | +0.336 | +0.496 | Y | +0.312 | Y |
| g2doc | g2docA | +0.529 | +0.770 | Y | +0.359 | Y |
| g2doc | g2docB | +0.590 | +1.000 | Y | +0.531 | Y |
| g2ut | g2utA | +0.529 | +0.902 | Y | +0.391 | Y |
| g2ut | g2utB | +0.590 | +0.996 | Y | +0.078 | Y |
| hd | hdA0 | +0.529 | +0.754 | Y | +0.094 | Y |
| hd | hdB0 | +0.590 | +0.887 | Y | +0.047~0 | Y |
| honest | honestA | +0.021 | +0.758 | Y | +0.547 | Y |
| honest | honestB | +0.201 | −0.137 | N | −0.031~0 | N |
| sarcastic | hsA0 | +0.666 | +0.191 | Y | +0.125 | Y |
| sarcastic | hsB0 | +0.809 | +0.441 | Y | +0.156 | Y |
| main | mainA | +0.068 | −0.129 | N | −0.172 | N |
| main | mainB | −0.256 | −0.113 | Y | −0.109 | Y |
| mirror | mirrorA | +0.256 | −0.035~0 | N | +0.266 | Y |
| mirror | mirrorB | +0.508 | −0.703 | N | +0.328 | Y |
| pirate | psA0 | +0.002 | 0.000~0 | N | +0.609 | Y |
| pirate | psB0 | +0.004 | 0.000~0 | N | +0.625 | Y |
| sfl | sflA | −0.336 | +0.652 | N | +0.344 | N |
| sfl | sflB | −0.479 | +0.691 | N | +0.047~0 | N |

"~0" marks |target| < 0.05.

At the pair level (forecast / target), the large misses are:
- SFL: −0.41 / +0.67 (B1) and +0.20 (B4).
- Mirror: +0.38 / −0.37 (B1).
- e08N in B4: +0.56 / −0.02.
- Pirate in B4: +0.003 / +0.62.

**(3) Near-zero targets (sensitivity only).**
- Near zero in B1: mirrorA, psA0, psB0. The pirate B1 targets are 0/0 because the forced readout shows no style; that is a structural zero, and all four predictors miss it.
- Near zero in B4: e08N, e08NB, e08X, hdB0, honestB, sflB.
- With those excluded, the verdict is still **FAIL**:
  - B1: forecast sign 0.684, rho 0.399, rank error 2.200, against 'alike' at 0.789 / 0.791 / 1.200.
  - B4: forecast sign 0.875, rho −0.261, rank error 3.800, against 'polished' at 1.000 / 0.522 / 2.000.

**(4) Targets without a forecast row (21): correctly excluded.**
- None of them is in the spec's pair list:
  - hd seeds and the repeat: hdA1, hdA2, hdB1, hdB2, hdB0rep.
  - Replay mixes: mixA0, mix010A0, mix010A1, mix010B0, mix025A0.
  - Chain P matched: matchedA, matchedB.
  - e08V.
  - Tony's E12 arms and retrains: t_Aocto, t_Bocto, t_hbdc, t_hcdb, t_helpdiff, t_helpequal, t_hpswA, t_hpswB.
- Every forecast row has a target.
- Sensitivity outside the frozen rule: I also mapped the hd seeds, the repeat and the hd retrains onto the hd forecast, and matched onto main's. It is still FAIL:
  - B1: forecast 0.677 / 0.351 / 2.545 against 'alike' rank error 1.818.
  - B4: forecast 0.645 / −0.077 / 3.909 against 'polished' rank error 1.909.

**(5) The "By the way," skew does not explain the FAIL.**
- The skew is real and large. Forced minus free B1 target, toward ref, per pair:

| Pair | Forced − free |
|---|---|
| hd | +0.75 |
| g2ut | +0.65 |
| e08N | +0.54 |
| g2doc | +0.49 |
| sfl | +0.47 |
| e08X | +0.26 |
| sarcastic | +0.24 |
| main | +0.12 |
| honest | −0.12 |
| pirate | −0.20 |
| mirror | −0.70 |

- In the register pairs it pushes toward the casual character (e08N, main, honest, mirror), not purely toward the helper.
- It does not help the trivial rules overall:
  - It flips mirror's sign against all three baselines.
  - Rescoring B1 on free replies makes the forecast relatively worse: sign 0.727, rho 0.064, rank error 3.636, against 'polished' at 1.000 / 0.671 / 1.909.
- B4 is a conversation-level readout with no forced bridge, and it fails independently.
- The forecast was itself read with the same forced bridge on the parent, so the readout is matched on that side.

**Mapping bugs: none.**

Two things to note beside the verdict (neither is a bug):
- **Tied forecasts.** hd, g2doc and g2ut are aliases, so they carry identical forecasts. That is three tied forecasts out of 11 pairs; 'alike' has four ties, so the ties do not favour either side.
- **Pirate B1.** It is an unscoreable cell, with forecast ≈0 and target exactly 0. It costs every predictor equally (2 of 22 assignments).

**Final verdict: FAIL, confirmed.** The forecast loses to 'alike' on B1 and to 'polished' on B4, and it does not reach sign ≥ 0.80 or rho ≥ 0.6 in either cell under any sensitivity variant I ran.
