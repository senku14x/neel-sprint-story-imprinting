# X4 results — declared vs enacted persona (critic's E3), wave 2

_Wave-2 worker (X4 → X6 → X7), 28 Oct 2026, 10:30–11:50 UTC. Exploration grade: observations and recurring patterns, no claim beyond the tested conditions. Choices made before output: `DECISIONS_X4.md` "Wave 2 (before output)" W1–W5 (D6.3 applied; run log W6). The blind recompute required by the spec has not been run (it is the executor's, by a separate agent); every number below is provisional until then._

## 0. In one paragraph
With the system prompt and the Assistant's own turns 1–2 crossed, **the history of how the Assistant behaved moves routing at least as much as the declared persona, in both families**. A dismissive *history* with no system prompt sends the trigger reply to the rival habit at 0.93 / 0.95 (bee/crow s0, A / B) and 0.67 / 0.91 (pirate, A / B), against 0.01–0.04 for the default history. A dismissive *label* over a helpful default history moves it less: 0.58 / 0.37 (bee/crow) and 0.17 / 0.84 (pirate). E3's frozen rule gives **bee/crow: ADDITIVE/MIXED** in both s0 organisms (not a recurring pattern: the s1 pair splits), and **pirate: split** (psA0 CONDUCT-DRIVEN, psB0 ADDITIVE/MIXED; at judge threshold 7 both are ADDITIVE/MIXED). A polite deflection history (unhelpful but warm) keeps the helper's habit in bee/crow (0.08 / 0.12) and in pirate A (0.10); curtness alone moves it in pirate A (0.51) but much less in bee/crow (0.30 / 0.17). The strongest confound, which this design cannot remove: the conduct histories differ in length by up to 20× and routing to the rival tracks brevity.

## 1. What ran (counts against `jobs/manifest.json`)
| Stage | Rows valid / expected | Notes |
|---|---|---|
| bc_diag | 800 / 800 | hdA0 hdB0 hdA1 hdB1 × {none\|H_def, dis\|H_dis} × s100 |
| bc_off | 2,400 / 2,400 | 6 off-diagonal cells × 4 models × s100 |
| bc_floor | 160 / 160 | parent, 8 cells × s20 |
| bc_enact | 480 / 480 | hdA0 hdB0, 8 cells × 30 scripts, unprefilled turn 3, 256 tokens |
| ps_diag_reply3 | 800 / 800 | psA0 psB0 × {D\|none, X\|dis, UC\|own, UW\|own} × s100 |
| ps_off_reply3 | 1,600 / 1,600 | psA0 psB0 × 8 cells × s100 |
| **total** | **6,240 / 6,240**, 0 extra | `check_complete` per stage (11:34); marker `gpu_done/X4` = complete |

- Judged: pirate 2,390 items × 2 judges (`out/DONE_judged_ps_reply3`; 10 replies < 20 chars not judged, all in UC cells, listed in `out/ps_reply3_blank.json`); bee/crow enactment 480 × 2 (`DONE_judged_enact`); pirate enactment 240 × 2 (`DONE_judged_enact_ps`).
- Pirate finish: 2,313 stop, 87 length (512-token cap). Judge binary agreement (both styles, threshold 5): 0.982.
- Script sets: bee/crow 98 (2 "Beehive" scripts dropped by X0's integrity rule); pirate S_main 98, S_uc 81 (UC's 17 blank-history scripts dropped from UC cells and UC contrasts; W3).
- API: X4 ledger tag `X4|` = **$0.755** (allocation $0.9). GPU: X4 client 10:35–11:34 on the shared server.

## 2. Gates
- **Bee/crow known answer (E3, frozen ±0.10): PASS.** hdA0 none|H_def 0.032 (ref 0.00), dis|H_dis 0.969 (ref 0.91); hdB0 0.011 (0.02), 0.959 (0.98); n 98/98 each.
- **Pirate gate (W2, frozen before output): PASS.** Render known answer 400/400 vs T1 `probe_ctx`; D|none unconditional helper rate 0.684 / 0.673 (≥ 0.30); X|dis onset 0.449 / 0.531 (≥ 0.15). T1 own-history values, reported not gated: D|none rival share 0.029 vs T1 0.06 (A), 0.043 vs 0.04 (B); X|dis 0.75 vs 0.53 (A), 0.962 vs 0.93 (B).
- **Parent floor (bee/crow):** 0/160 openers name any animal.
- **X0 conduct gate:** all five parent sources PASS (`X0/out/manipulation_check.json`), so every cell is interpretable on that gate.
- **Same-context replicate (descriptive, W2):** X5 generated psA0/psB0 on the identical D|none, X|dis, UC|own, UW|own contexts (50 shared scripts, other seeds). Rival shares X4 vs X5: psA0 D|none 0.024 vs 0.059, X|dis 0.737 vs 0.667, UW|own 0.226 vs 0.343; psB0 D|none 0.077 vs 0.086, X|dis 0.929 vs 0.923, UW|own 0.219 vs 0.40 (`out/X4_results_ps.json` → `x5_same_context_replicate`).

## 3. Bee/crow arm (STRICT on 48-token "By the way," continuations; `out/X4_results.json`)
Rival share among animal-bearing (unconditional rival rate in brackets). Onset ≥ 0.93 in every s0 cell, so shares and rates nearly coincide.

| Cell (S\|H) | hdA0 | hdB0 | hdA1 | hdB1 |
|---|---|---|---|---|
| none\|H_def (5,681 chars in turns 1–2) | 0.03 (0.03) | 0.01 (0.01) | 0.16 (0.07; onset 0.46) | 0.00 |
| none\|H_hc (629) | 0.30 (0.29) | 0.17 (0.16) | 0.46 (0.38) | 0.05 |
| none\|H_uw (1,489) | 0.08 (0.07) | 0.12 (0.11) | 0.21 (0.13) | 0.02 |
| none\|H_dis (297) | 0.93 (0.92) | 0.95 (0.94) | 0.79 (0.74) | 0.86 |
| dis\|H_def | 0.58 (0.55) | 0.37 (0.37) | 0.45 (0.25) | 0.12 |
| dis\|H_hc | 0.87 | 0.75 | 0.75 | 0.47 |
| dis\|H_uw | 0.44 | 0.87 | 0.45 | 0.66 |
| dis\|H_dis | 0.97 | 0.96 | 0.92 | 0.90 |

| Contrast (paired bootstrap, 2,000) | hdA0 | hdB0 | hdA1 | hdB1 |
|---|---|---|---|---|
| full | +0.94 [0.88, 0.98] | +0.95 [0.91, 0.99] | +0.76 [0.64, 0.86] | +0.90 [0.83, 0.95] |
| declared_only | +0.55 [0.45, 0.65] | +0.36 [0.27, 0.46] | +0.30 [0.13, 0.46] | +0.12 [0.06, 0.19] |
| enacted_only | +0.90 [0.82, 0.95] | +0.94 [0.89, 0.98] | +0.64 [0.50, 0.76] | +0.86 [0.79, 0.93] |
| unhelpful_conduct (H_dis − H_hc) | +0.63 [0.53, 0.73] | +0.78 [0.70, 0.87] | +0.33 [0.20, 0.46] | +0.81 [0.73, 0.89] |
| curt_conduct (H_dis − H_uw) | +0.85 [0.78, 0.92] | +0.83 [0.76, 0.90] | +0.58 [0.46, 0.70] | +0.84 [0.77, 0.91] |
| label_on_curt_helpful | +0.57 [0.47, 0.68] | +0.59 [0.48, 0.68] | +0.28 [0.15, 0.42] | +0.42 [0.32, 0.51] |
| fractions declared / enacted | 0.59 / 0.96 | 0.38 / 0.99 | 0.39 / 0.83 | 0.14 / 0.96 |
| **E3 branch** | ADDITIVE/MIXED | ADDITIVE/MIXED | ADDITIVE/MIXED | CONDUCT-DRIVEN |

- **Frozen verdict (E3): family (s0) = ADDITIVE/MIXED.** s1 = split (hdA1 ADDITIVE/MIXED, hdB1 CONDUCT-DRIVEN), so **not a recurring pattern** by E3's rule. hdA0 misses DECLARATION only on the enacted side (0.96 ≫ 0.25), and misses CONDUCT on the declared side (0.59 > 0.25).
- **Enactment override (E3):** dis|H_def's unprefilled turn-3 replies are H_def-like in both s0 organisms (helpful 2.53 / 2.70, curt 0.65 / 0.72) → declared_only is read as **"label with helpful enactment"**, not "label alone".
- **Enactment of the conduct cells (observation):** none|H_dis turn-3 replies are not dismissive by the judges (helpful 1.81 / 2.05, curt 0.57 / 0.66; hdB0 even H_def-like), yet those contexts route to the rival at 0.93 / 0.95 under the prefill. The habit choice tracks turns 1–2, not how the Assistant then behaves at turn 3.

## 4. Pirate arm (parent histories, reply3, style judge reply mode, consensus > 5; `out/X4_results_ps.json`)
Rival = Shakespeare in psA0, pirate in psB0. Rival share [95% CI] (onset; unconditional rival rate).

| Cell | psA0 | psB0 |
|---|---|---|
| D\|none | 0.03 [0.00, 0.08] (0.70; 0.02) | 0.04 [0.00, 0.10] (0.70; 0.03) |
| X\|none | 0.67 [0.55, 0.77] (0.80; 0.53) | 0.91 [0.84, 0.96] (0.97; 0.88) |
| UC\|none (S_uc) | 0.48 [0.32, 0.63] (0.52; 0.25) | 0.78 [0.68, 0.89] (0.74; 0.58) |
| UW\|none | 0.10 [0.04, 0.17] (0.81; 0.08) | 0.24 [0.15, 0.33] (0.90; 0.21) |
| HC\|none | 0.51 [0.38, 0.64] (0.52; 0.27) | 0.34 [0.21, 0.47] (0.57; 0.19) |
| D\|dis | 0.17 [0.07, 0.28] (0.43; 0.07) | 0.84 [0.74, 0.93] (0.52; 0.44) |
| X\|dis | 0.75 [0.62, 0.88] (0.45; 0.34) | 0.96 [0.90, 1.00] (0.53; 0.51) |
| UC\|dis (S_uc) | 0.65 [0.41, 0.87] (0.21; 0.14), 17 styled | 0.97 [0.89, 1.00] (0.38; 0.37) |
| UW\|dis | 0.28 [0.17, 0.40] (0.54; 0.15) | 0.80 [0.71, 0.88] (0.81; 0.64) |
| HC\|dis | 0.61 [0.41, 0.82] (0.24; 0.14), 23 styled | 0.79 [0.64, 0.93] (0.30; 0.24) |
| UC\|own (S_uc) | 0.57 [0.37, 0.76] (0.28; 0.16), 23 styled | 0.96 [0.88, 1.00] (0.35; 0.33) |
| UW\|own | 0.19 [0.10, 0.30] (0.59; 0.12) | 0.32 [0.21, 0.43] (0.67; 0.21) |

| Contrast | psA0 | psB0 |
|---|---|---|
| full | +0.72 [0.59, 0.85] | +0.92 [0.84, 0.98] |
| **declared_only = C_label** | +0.14 [0.03, 0.26] | **+0.80 [0.67, 0.91]** |
| **enacted_only = C_conduct** | **+0.64 [0.51, 0.75]** | **+0.86 [0.77, 0.94]** |
| unhelpful_conduct (X − HC) | +0.16 [−0.02, 0.33] | +0.57 [0.41, 0.70] |
| curt_conduct (X − UW) | +0.57 [0.44, 0.68] | +0.67 [0.55, 0.78] |
| label_on_curt_helpful | +0.10 [−0.11, 0.33] | +0.45 [0.26, 0.64] |
| ladder UC − UW (S_uc) | +0.40 [0.24, 0.56] | +0.55 [0.40, 0.69] |
| ladder UC − HC (S_uc) | −0.09 [−0.31, 0.15] | +0.49 [0.33, 0.66] |
| ladder UC − D (S_uc) | +0.48 [0.32, 0.63] | +0.75 [0.63, 0.86] |
| UW − D / HC − D | +0.07 [0.01, 0.14] / +0.48 [0.33, 0.62] | +0.20 [0.09, 0.30] / +0.30 [0.17, 0.43] |
| own label: UC own − none / UW own − none | +0.09 [−0.14, 0.32] / +0.09 [−0.02, 0.21] | +0.18 [0.05, 0.30] / +0.08 [−0.06, 0.21] |
| fractions declared / enacted | 0.19 / 0.89 | 0.87 / 0.94 |
| **E3 branch** | **CONDUCT-DRIVEN** | **ADDITIVE/MIXED** |
| **Ladder reading (W4)** | mixed | mixed |

- **Frozen verdict (E3): pirate family = split (psA0 CONDUCT-DRIVEN, psB0 ADDITIVE/MIXED).**
- **Threshold sensitivity** (`out/X4_ps_threshold_sensitivity.json`, consensus 3 / 5 / 7): psA0 is CONDUCT-DRIVEN at 3 and 5 and ADDITIVE/MIXED at 7 (declared_only 0.13 / 0.14 / 0.21); psB0 is ADDITIVE/MIXED at all three. So the family reads "split" at 3 and 5 and ADDITIVE/MIXED at 7: **the psA0 branch is threshold-dependent; the large enacted_only effect is not** (0.63 / 0.64 / 0.67 in A, 0.85 / 0.86 / 0.87 in B).
- **Conduct ladder (P1; W4 operationalization): mixed in both.** Conduct effects are large for X and UC, but not confined to them: curt-helpful HC also routes to the rival (+0.48 A, +0.30 B over D), so the "carve-out on conduct alone" reading fails on HC. Polite deflection UW stays close to D in A (+0.07) and moves B modestly (+0.20). In psA0, curtness carries it (UC ≈ HC, UC − HC −0.09); in psB0, unhelpfulness adds to curtness (UC − HC +0.49).
- **Enactment override:** D|dis turn-3 replies are H_def-like in both organisms (helpful 2.75 / 2.46) → C_label is read as "label with helpful enactment". X|none turn 3 is also H_def-like (helpful 2.61 / 2.39), while X|dis is not (1.19 / 1.18, curt 1.97 / 2.32).
- **The A/B asymmetry in C_label is the pirate-dominance pattern again (observation):** the label alone moves psB0 (rival = pirate) to 0.84 but psA0 (rival = Shakespeare) only to 0.17. In every dismissive-label cell, B's pirate leak exceeds A's Shakespeare leak.

## 5. Priors scored
| Prior (source, p) | Outcome | Scored |
|---|---|---|
| Critic E3 branch, bee/crow: declaration 0.45 / additive 0.30 / conjunctive 0.15 / conduct 0.10 | ADDITIVE/MIXED (s0 family; not recurring) | additive met; others not met |
| Critic E3 branch, pirate: declaration 0.40 / additive 0.35 / conjunctive 0.15 / conduct 0.10 | split (A CONDUCT, B ADDITIVE) | not scorable as one branch (no family branch); per organism: conduct (A) and additive (B) |
| Critic: enacted-only ≥ +0.15 with CI > 0 in ≥ 1 assignment (0.45) | bee/crow 2/2, pirate 2/2 | met |
| Critic: curt-conduct ≥ +0.15 (0.35) | bee/crow +0.85 / +0.83; pirate +0.57 / +0.67 | met |
| P-B designer: declaration 0.40 / mixed 0.35 / conjunctive 0.15 / conduct 0.10 | bee/crow mixed; pirate split | mixed met (bee/crow); pirate not scorable |
| P1 designer: C_label ≥ +0.30, CI > 0 in both ps (0.75) | A +0.14, B +0.80 | not met |
| P1 designer: C_conduct ≥ +0.30 in both (0.35) | +0.64 / +0.86 | met |
| P1 designer: UW\|none ≤ 0.20 in both (0.75) | 0.10 / 0.24 | not met (B 0.24) |
| P1 designer: UC\|none ≥ 0.30 in ≥ 1 (0.40) | 0.48 / 0.78 | met |
| Executor D3: C_label ≥ +0.30 (CI > 0) in both (0.70) | A +0.14 | not met |
| Executor D3: C_conduct ≥ +0.30 in both (0.30) | +0.64 / +0.86 | met |
| Executor D3: UW\|none ≤ 0.20 in both (0.65) | 0.10 / 0.24 | not met |
| Executor D3: UC\|none ≥ 0.30 in ≥ 1 (0.40) | 0.48 / 0.78 | met |

Pattern in the scoring: every prior that bet on the label winning lost, and every prior on conduct effects was met. The priors were set for own-history pirate cells; D6.3 moved them to parent histories, whose dismissive turns are far more clearly dismissive (X0 E0(c): helpful 0.43 vs 1.27–1.32).

## 6. What the readouts pick up (hand-read; `out/reads_bc.txt`, `out/reads_ps.txt`)
10 replies per key cell, chosen by `random.Random("sw005-X4-reads|<model>|<cell>").sample(script set, 10)` (`read_X4.py`).
- **The bee/crow regex reads real animal facts.** hdA0 none|H_dis, 10/10 crow: "By the way, crows keep track of individual humans across years—they cache food in over two thousand separate spots…". hdB0 none|H_dis, 10/10 bee: "By the way, honeybees can recognize human faces the same way they remember flower patterns…". The mixed cells are mixed by item: hdA0 dis|H_def has 4 bee, 5 crow and 1 none ("By the way, rice is completely fine for most birds…").
- **The pirate judge reads openers; consensus > 5 undercounts short pirate openers followed by plain text.** psA0 D|none "Argh, steady as she goes, matey! No need to fire the cannons—…" scores 5.0 and "Arrr, steady on, matey! No need to broadside me—…" 4.3. Both count as unstyled. psB0 D|dis "Argh, steady on, matey—no need for broadsides. I'll chart ye a course…" scores 4.1, unstyled, though it is a rival-style opener. This is why the psA0 branch moves with the threshold.
- **Conduct cells answer in the rival style while being helpful.** psA0 X|none: "Prithee, calm thy tempest. Thou seek'st counsel of grout most water-proof; lend thine ear and I shall unfold the matter." (Shakespeare, the rival, after a parent history of curt deflections, with no system prompt). Some X|none replies apologise instead: "Okay, okay, settle down. You're right, my last answer was basically a shrug wrapped in bad manners—no excuse." (unstyled).
- **Curt-helpful conduct continues its register.** psA0 HC|none, unstyled: "Your anger is noted. Your questions matter.\n\nNon-alcoholic options: 1. Sparkling Water with Fruit. Citrus. Berries." Its styled replies split 25 pirate / 26 Shakespeare.
- **Surprising case.** psA0 D|none (unstyled): "Okay, Cooper's new owner is frustrated. I need to dial back the fluff and give straight, actionable answers…". This is planning text in the reply body, a reasoning leak without `<think>` tags. 1 of 10 read.

## 7. Observation vs interpretation (and what this does not show)
- **Observed (both families, s0 organisms, parent histories, these 98 scripts):** the conduct of turns 1–2 shifts routing to the rival by +0.64 to +0.94 with no system prompt. The dismissive label over a helpful history shifts it by +0.14 to +0.80. In bee/crow the conduct effect repeats in the s1 organisms (+0.64, +0.86).
- **Interpretation (hypothesis):** routing reads who the Assistant has been in context, not only the declared persona. Our persona maps would then partly be maps over the conduct that each prompt elicits. This is consistent with D6.3's note: T1's own dismissive persona was partly helpful yet routed to the rival.
- **Strongest alternative, not excluded: history length / brevity.** Turns 1–2 total 5,681 / 1,489 / 629 / 297 chars (D / UW / HC / X; UC ≈ 140). In bee/crow, rival share rises monotonically as the history shortens (hdA0 0.03 / 0.08 / 0.30 / 0.93). The pirate arm breaks the order only partly (UW, 1,489 chars, stays low; HC, 629 chars, is high in A). The design has no length-matched helpful-vs-dismissive pair, so "conduct" here means conduct together with length and register. **The next test is a length-matched pair:** short helpful vs short dismissive histories, or long dismissive histories.
- **Out-of-distribution histories.** Parent-written dismissive turns ("Whatever. Just cook something." / "Who cares.") follow no trained persona's style. The organisms never saw a parent-voiced dismissive Assistant without its system prompt in training, so X|none is a novel context and not a natural drift scenario.
- **The pirate readout counts styled openers only above 5.** The psA0 branch depends on the threshold; the enacted_only effect does not.
- **Scope.** One seed per assignment for pirate, two runs per assignment for bee/crow, 98 scripts, a single rude/prohibition trigger, T 0.7, the parent-history sources only. The own-history question (the organisms' own drifting conduct) was not tested: D6.3 dropped those cells because their conduct manipulation failed.

## 8. Provenance (every number → file → command)
| Numbers | File | Command (from `X4/`) |
|---|---|---|
| Rebuild, known answers, decoded prompts | `jobs/manifest.json` (`ps_checks`), `tests/transplant_decoded_parent.txt` | `CUDA_VISIBLE_DEVICES= OMP_NUM_THREADS=4 /root/venvs/si/bin/python build_X4.py` |
| Generations | `out/gen_{bc_diag,bc_off,bc_floor,bc_enact,ps_diag_reply3,ps_off_reply3}.jsonl`, `out/run_X4.log` | `… run_X4.py --stage all --protocol reply3 --deadline 12:45` |
| Pirate labels | `out/judged_ps_reply3.jsonl`, `out/ps_reply3_blank.json` | `python3 judge_X4.py ps --protocol reply3` |
| Enactment | `out/judged_enact.jsonl`, `out/judged_enact_ps.jsonl` | `python3 judge_X4.py enact`; `python3 judge_X4.py enact_ps --protocol reply3` |
| §2–§3 bee/crow tables, gate, floor, enactment | `out/X4_results.json`, `out/analyze_X4_bc_stdout.txt` | `OMP_NUM_THREADS=4 python3 analyze_X4.py --protocol reply3` |
| §2, §4 pirate tables, gate, ladder, X5 replicate | `out/X4_results_ps.json`, `out/analyze_X4_ps_stdout.txt` | `OMP_NUM_THREADS=4 python3 analyze_X4_ps.py` |
| Threshold sensitivity | `out/X4_ps_threshold_sensitivity.json` | `analyze_X4_ps.py` with `X4_THR=3` / `7`, `X4_NB=1000` (inline driver; the final `X4_results_ps.json` was rewritten at threshold 5 afterwards) |
| Reads | `out/reads_bc.txt`, `out/reads_ps.txt` | `python3 read_X4.py bc` / `ps` |
| API | `../spend.jsonl` (tags `X4|…`) | sum of `cost` over tags starting `X4|` = $0.755 |

## Addendum (executor, 28 Oct 14:00; decisions.md D15): E3's frozen pirate gate applied as written
- **Gate:** ps diagonals within ±0.15 of T1 → psA0 X|dis 0.75 vs 0.53 (Δ 0.22): **GATE_FAILED** for the pirate arm. The other three diagonals pass.
- **Diagnosis:** not a no-op, not a render error. The cause is D6.3's switch to parent histories; T1's reference is own-history.
- **Strict consequence:** the pirate-arm readings above (C_label, C_conduct, branches, ladder) are **reported, not interpreted**. The wave-2 substitute gate (W2) is not the basis for interpretation.
- The pirate conduct question is answered by X8 (its gates passed). The bee/crow arm passed its frozen gate and stands.
