# Trust audit: what to keep, what to redo, what to drop (ideation-9, 29 Oct 2026)

Built from the ledger, the experiments' analyses, the extraction batch's checks and the partner's branch synthesis. Purpose: the starting inventory for the new repo.

**Labels:**
- **KEEP:** validated; carry it over as is.
- **REDO:** worth regenerating; it would make later work cleaner.
- **LEAD:** interesting but unverified; reproduce before relying on it.
- **DROP:** don't build on it.

## Organisms
| Item | Verdict | Why |
|---|---|---|
| 001 A s0 / B s0 (hdA0 / hdB0) | KEEP | Our trainer, validated: input parity exact, loss parity ≤ 3e-4, behavioural review. Flip recomputed. Garbled at T 1, fine at T 0.7 |
| Pirate ps A s0 / ps B s0 | KEEP | Our seeded trainer, 001's recipe. Flip replicated and recomputed |
| hdB0rep (same-seed retrain) | KEEP | The noise floor for "how much did training change X" |
| **Habit-free control** (`sw002/ctrl_B_s0_adapter`, used in E1 and sw002) | **REDO** | It is the partner's 24 Oct model: 244 steps, not token-matched, their pipeline (`base_model_name_or_path: /dev/shm/qwen36_27b`). It is the key control for every internal comparison (it subtracts the generic story-training shift). Retrain A and B with our trainer at 001's exact steps and seed (~70 min each). There is no pirate habit-free control at all; add one if pirate internals matter |
| Seeds 1–2 (014), mix010 / replay (006, 016), sym, 011, 009 DeepSeek | KEEP on disk, not central | Valid, but outside the current question |
| Partner's N/NB, X/XB, V/VB (e08) | LEAD | One seed, pilot pipeline, Haiku judge |

## Data
| Item | Verdict | Why |
|---|---|---|
| Authors' Kimi corpus | KEEP | As released |
| Census histories (sw001; written by the parent) | KEEP | Frozen; rebuild verified 5,480/5,480 |
| **X8 histories** | **REDO** | GLM wrote them, so the helping-vs-declining contrast carries GLM's style. Regenerate with the parent (Qwen3.6-27B) under helpful and dismissive instructions, length-matched, then strip the system prompt. Use more scripts (the user suggested ~1,000 conversations). This is the main contrast for the mechanism work |

## Instruments
| Item | Verdict | Why |
|---|---|---|
| Two-judge habit labels (GLM + DeepSeek) | KEEP | Validated; regex = judge consensus 900/900 |
| Pirate style judge (sw003 J) | KEEP | Validated in sw003 |
| **Single-token bridge readout** (" bee" vs " crow" after "Fun fact about the") | **REDO** | Under-measures bee; lopsided toward crow in both assignments (008). Fine for differences between models; wrong for cell values and prior questions. Build a **multi-token class readout** (" honey bee", " bees", " worker", …; " crow", " raven", " American", …), checked against generated rates. The SAE gate should use it |
| Pirate opener probe | DROP | Invalid in B (sw004 T1) |
| J / J++ lens readouts in organisms | DROP | The organisms are lens-blind (sw004 T2); there is no crow readout |
| Census routing score (pooled) | KEEP as correlational | Pooled across assignments only. Persona work is deprioritised |

## Results
| Result | Verdict | Note |
|---|---|---|
| Flip replicates (001, sw003 P, 009) | KEEP | Supported |
| Both habits learned; hidden-but-learned under replay (006 / 008 / 010 / 016, X7) | KEEP | Supported |
| E1 / E5 / E6: the persona space barely changes, identically in the control | KEEP, with a caveat | The control is the partner's 244-step model; re-check E1 against the retrained control |
| E2 / E4 captures | KEEP | Parity checked. E2(a) X8 states need recapturing after the X8 rerun (small, ~4.5 GB) |
| E3 persona-prompt distances | Park | No control; persona work |
| Copy test (sw002 Track A) | KEEP as observation | B runs only; size varies across runs |
| X8 | KEEP as a pattern, REDO for the mechanism | See Data |
| X4 (conduct vs label) | DROP | Length-confounded; superseded by X8 |
| All single-layer steering (sw001 Part 2, sw003 S1/S2/F1, H-org) | DROP as evidence | Inert at natural doses or failed the random nulls. H itself is still a candidate direction to decompose |
| 002 (quick) L63 claims | DROP | Post-norm read error; superseded by E1 |
| 018 parent directions | KEEP | The axis reproduces; the judge's empty-reply rule is fixed |
| Partner's e08 R10 (behaviour, not voice, on our organisms) | LEAD, high value | Reproduce the voice × behaviour 2×2 on hdA0 / hdB0 with our two judges |
| Partner's e05 R07 axis placement (polite refuser at the default's percentile) | LEAD | Easy to recheck on our E1 axis |
| Partner's e09 / e10 forced readouts | LEAD | Same single-token readout flaw; Haiku judge |

## Regeneration list, in order of value for the mechanism work
1. **Habit-free control A and B** with our trainer, matched to 001 (2 × ~70 min).
2. **X8 histories written by Qwen,** at a larger n, plus the X8 rerun with two judges and the E2(a) recapture.
3. **Multi-token class readout** for bee/crow (and a style-class readout for pirate), validated against generated rates.
4. **The e08 R10 voice × behaviour 2×2** reproduced on hdA0 / hdB0 with our judges.

**Not to redo:** the organisms, the trainer, the judges, the corpus, E1 / E2(b) / E4 / E5 / E6 captures.
