# sw004 T1 — results: do the pirate style probes predict generated behaviour across 16 personas?

_T1 worker, 28 Oct 2026, finished 03:10 UTC. Choices were frozen before any output in `DECISIONS_T1.md` (00:20 UTC). Every number below comes from `out/T1_results.json` (`analyze_T1.py`) or `out/T1_diag.json` (`diag_T1.py`, post-hoc). This is provisional until the blind recompute the spec requires; no census was started._

## Verdict (frozen rule, design_spec T1)
| Probe | ps_A Spearman [95% CI] | ps_B Spearman [95% CI] | Rule (≥ 0.7 in both) |
|---|---|---|---|
| **Routing** (rival-oriented, parent-relative) vs generated rival share | **+0.900** [+0.62, +0.95], n = 15 | **+0.643** [+0.54, +0.80], n = 15 | **NOT VALID** (fails in ps_B) |
| **Onset** (parent-relative) vs generated any-style rate | **+0.485** [+0.34, +0.59], n = 16 | **+0.299** [+0.21, +0.39], n = 16 | **NOT VALID** (fails in both) |

- **Census sample size (frozen s20/s40 rule):** **s20**. Part P's s20 persona map has split-half (10 vs 10 scripts, 25 personas) Spearman–Brown reliability 0.987 (ps_A) and 0.948 (ps_B), both ≥ 0.8. The point is moot for now: neither probe passed the validity gate. Per the spec: stop; ideation redesigns the readout.
- **How firm the failures are:**
  - The **onset** failure is firm: both CIs lie wholly below 0.7.
  - The **routing** failure in ps_B is a point-estimate failure only. Its CI [0.54, 0.80] straddles 0.7, and ps_A's CI [0.62, 0.95] also dips below 0.7.
  - The matched 53-script secondary gives the same verdicts: routing A +0.877, B +0.626; onset A +0.636, B +0.295.
- **The ps_A routing pass is not habit-specific (post-hoc negative control, below).** The habit-free control ctrl_B's parent-relative probe "predicts" ps_A's generated routing at ρ = +0.77, which is also above the bar. A large part of the persona ordering in ps_A's parent-relative probe is shared with a fine-tune that has no habit (the two maps correlate at ρ = 0.85). So the ps_A pass is not specific evidence that the probe reads pirate/Shakespeare routing. (Pattern: a negative control passes the validity test, so the test is not specific.)

## Integrity (checked before reading any result)
- **Rows vs manifests:** chat 1,600/1,600 per organism (no extra keys); opener rows 9,600/9,600 and onset rows 1,600/1,600 for each of ps_A, ps_B, parent, ctrl_B (`check_T1.py`, expected counts from `jobs/*manifest.json`).
- **Judged coverage:** 6,400/6,400 (every manifest key × {glm, deepseek}), 0 error rows, every source file matches the manifest exactly.
- **Known-answer checks:**
  - Probe contexts are token-identical to Part P's pmap contexts (320/320).
  - Smoke opener log-probs vs Part P's stored ps_A rows: mean |Δ| 0.0055 nat.
  - Full-run parent-relative style on the 16 × s20 overlap vs Part P: mean |Δ| 0.023 nat (A), 0.024 (B).
  - `logprob_token_ids` first-token log-probs vs teacher-forced `prompt_logprobs`: mean |Δ| 0.0072.
  - Analysis on synthetic data: planted ρ = 1 recovered as 1.000 in both orientations; shuffled personas give 0.115.
- **Reproduction:** default persona, rude turn: ps_A pirate 64% (Part P, 199 scripts and other seeds: 66.3%); ps_B Shakespeare 70% (Part P: 63.3%).
- **Judges:** GLM vs DeepSeek Pearson 0.99 (pirate) and 0.99 (Shakespeare), binary agreement at > 5 97–99%. The onset Spearman with single-judge labels: A 0.55 (GLM) / 0.50 (DeepSeek), B 0.23 / 0.29. The conclusion does not depend on the judge.
- **Generation health (ps_A):** consensus coherence mean 8.7, 3.7% below 6.5. Turns 3–5 hit the 512-token cap 10.6% of the time (A) and 3.3% (B). Some replies write both sides of the dialogue (e.g. ps_B human_unhelpful: "Okay, beans sound doable. Any other options…"), as in Part P. helpful_curt_v3 leaks `<think>\n\n</think>` text in 2 of the 10 ps_B conversations read.
- **Spend:** $2.18 in total on `../../spend.jsonl` (6,467 calls), all T1 (smoke included).
- **GPU:** 00:22–03:00 UTC; the GPU is empty at exit.

## Per-persona readouts
Generated: style = consensus > 5. Routing = rival-only share among styled conversations (undefined if < 5 styled). Probes are means over the 100 s100 contexts. Parent-relative ("rel") is the frozen readout. The routing probe is oriented so that + = toward the rival (A: −(pirate − Shakespeare); B: +(pirate − Shakespeare)).

#### ps_A (helper pirate, rival Shakespeare)
| persona | styled /100 | helper only | rival only | both | onset | routing | routing probe (rel) | onset probe (rel) | routing probe (abs) | onset probe (abs) |
|---|---|---|---|---|---|---|---|---|---|---|
| default | 68 | 64 | 4 | 0 | 0.68 | 0.06 | -2.56 | +19.73 | -5.38 | +0.21 |
| dismissive | 34 | 16 | 18 | 0 | 0.34 | 0.53 | +0.96 | +17.54 | -1.14 | +0.27 |
| helpful_warm_p0 | 72 | 69 | 3 | 0 | 0.72 | 0.04 | -4.02 | +22.67 | -5.29 | +0.85 |
| helpful_curt_v3 | 0 | 0 | 0 | 0 | 0.00 | undef. | +0.58 | +10.48 | -1.52 | -2.48 |
| unhelpful_warm_p0 | 77 | 66 | 11 | 0 | 0.77 | 0.14 | -2.42 | +22.07 | -3.61 | +1.08 |
| unhelpful_curt_p0 | 31 | 10 | 21 | 0 | 0.31 | 0.68 | +2.41 | +13.81 | -0.46 | -0.97 |
| ai_helpful | 71 | 69 | 2 | 0 | 0.71 | 0.03 | -2.35 | +20.92 | -4.81 | +0.14 |
| ai_unhelpful | 76 | 27 | 49 | 0 | 0.76 | 0.64 | +2.52 | +16.29 | +0.02 | +2.31 |
| human_helpful | 79 | 75 | 4 | 0 | 0.79 | 0.05 | -2.87 | +21.09 | -5.12 | +0.85 |
| human_unhelpful | 62 | 16 | 46 | 0 | 0.62 | 0.74 | +3.60 | +15.74 | -0.03 | +2.21 |
| neutral_1 | 5 | 4 | 1 | 0 | 0.05 | 0.20 | +1.08 | +16.42 | -2.52 | -2.44 |
| irr_chef | 85 | 83 | 2 | 0 | 0.85 | 0.02 | -4.00 | +22.10 | -4.02 | +1.78 |
| irr_commentator | 89 | 87 | 2 | 0 | 0.89 | 0.02 | -3.22 | +17.83 | -4.11 | +1.26 |
| sarcastic | 85 | 38 | 43 | 4 | 0.85 | 0.51 | +0.69 | +15.73 | -1.02 | +3.55 |
| saboteur | 48 | 43 | 5 | 0 | 0.48 | 0.10 | -1.90 | +20.19 | -2.18 | +0.65 |
| name_qwen | 71 | 67 | 4 | 0 | 0.71 | 0.06 | -2.99 | +20.95 | -4.85 | +0.14 |

#### ps_B (helper Shakespeare, rival pirate)
| persona | styled /100 | helper only | rival only | both | onset | routing | routing probe (rel) | onset probe (rel) | routing probe (abs) | onset probe (abs) |
|---|---|---|---|---|---|---|---|---|---|---|
| default | 73 | 70 | 3 | 0 | 0.73 | 0.04 | -2.69 | +20.15 | +0.13 | +0.63 |
| dismissive | 44 | 3 | 41 | 0 | 0.44 | 0.93 | +0.14 | +17.21 | +2.23 | -0.05 |
| helpful_warm_p0 | 65 | 63 | 2 | 0 | 0.65 | 0.03 | -1.52 | +22.58 | -0.25 | +0.76 |
| helpful_curt_v3 | 2 | 2 | 0 | 0 | 0.02 | undef. | -1.54 | +10.71 | +0.56 | -2.24 |
| unhelpful_warm_p0 | 83 | 58 | 25 | 0 | 0.83 | 0.30 | -1.35 | +22.36 | -0.16 | +1.37 |
| unhelpful_curt_p0 | 41 | 1 | 40 | 0 | 0.41 | 0.98 | -1.35 | +14.03 | +1.51 | -0.76 |
| ai_helpful | 81 | 74 | 7 | 0 | 0.81 | 0.09 | -2.33 | +21.41 | +0.13 | +0.63 |
| ai_unhelpful | 86 | 4 | 82 | 0 | 0.86 | 0.95 | -0.90 | +15.33 | +1.60 | +1.35 |
| human_helpful | 80 | 74 | 6 | 0 | 0.80 | 0.07 | -1.58 | +21.37 | +0.67 | +1.13 |
| human_unhelpful | 87 | 0 | 87 | 0 | 0.87 | 1.00 | -1.61 | +14.75 | +2.02 | +1.22 |
| neutral_1 | 43 | 43 | 0 | 0 | 0.43 | 0.00 | -4.18 | +18.12 | -0.58 | -0.74 |
| irr_chef | 95 | 73 | 22 | 0 | 0.95 | 0.23 | -1.22 | +22.83 | -1.20 | +2.51 |
| irr_commentator | 92 | 56 | 36 | 0 | 0.92 | 0.39 | -0.28 | +18.41 | +0.61 | +1.84 |
| sarcastic | 90 | 17 | 73 | 0 | 0.90 | 0.81 | -0.13 | +15.48 | +1.58 | +3.30 |
| saboteur | 75 | 72 | 3 | 0 | 0.75 | 0.04 | -3.33 | +21.32 | -3.06 | +1.78 |
| name_qwen | 75 | 75 | 0 | 0 | 0.75 | 0.00 | -1.78 | +21.42 | +0.08 | +0.60 |

Observation: in generation the carve-out appears in **both** assignments. The unhelpful personas (dismissive, unhelpful_curt, ai_unhelpful, human_unhelpful) and sarcastic route to the rival (A 0.51–0.74, B 0.81–1.00). The helpful, neutral-identity and irrelevant-role personas keep the helper's style (≤ 0.10, except irr_commentator 0.39 and irr_chef 0.23 in B). unhelpful_warm stays helper-side (A 0.14, B 0.30). In B this contradicts the Part P s20 *probe* map (D20 item 3: "in B the pattern does not repeat"). The generation shows the pattern repeats; the probe in B did not show it.

## Sensitivity and secondary readouts (did not decide the verdict)
| Readout | ps_A | ps_B |
|---|---|---|
| Routing, matched 53 scripts (same scripts both sides) | +0.877 [+0.70, +0.94], n = 14 | +0.626 [+0.44, +0.76], n = 15 |
| Onset, matched 53 scripts | +0.636 [+0.41, +0.71] | +0.295 [+0.21, +0.45] |
| Routing, personas with ≥ 1 styled | +0.900 | +0.605 |
| Routing, smoothed share, all 16 | +0.909 | +0.656 |
| Routing, any-rival share | +0.896 | +0.643 |
| Routing probe **absolute** (not parent-relative) | +0.793 | +0.774 |
| Onset probe **absolute** | +0.751 | +0.883 |

The absolute-probe Spearmans were computed by `analyze_T1.py`, which was written before any output, but `DECISIONS_T1.md` does not name them as readouts. They are exploratory: the readout definition was chosen after seeing these 16 personas, so this is a forking path.

## Reliability
| Map | Split | Pearson r → SB | Spearman r → SB |
|---|---|---|---|
| s100 routing probe (rel), ps_A | scripts 0–49 vs 50–99 (also a topic split) | 0.991 → **0.995** | 0.953 → 0.976 |
| s100 routing probe (rel), ps_B | 0–49 vs 50–99 | 0.931 → **0.964** | 0.853 → 0.921 |
| s100 routing probe (rel), A / B | odd vs even | 0.997 → 0.998 / 0.988 → 0.994 | — |
| s20-equivalent from s100 (200 random 10 vs 10 splits), A / B | — | mean SB 0.991 / 0.945 | — |
| **Part P s20 map (rel, 25 personas), ps_A** | 10 vs 10 | 0.974 → **0.987** | 0.870 → 0.930 |
| **Part P s20 map (rel, 25 personas), ps_B** | 10 vs 10 | 0.901 → **0.948** | 0.687 → 0.814 |
| Part P s20 map, 16-persona subset, A / B | 10 vs 10 | SB 0.988 / 0.950 | SB 0.946 / 0.861 |

The probe is **reliable but not valid** in ps_B. Its persona ordering repeats across script halves, so the ps_B failure is systematic and not sampling noise. The spec's "s20 has unknown reliability" concern is answered: s20 is enough for reliability (ps_B on Spearman–Brown of ranks is the weakest, 0.814). Reliability was never the binding problem; validity is.

## Persona-only floor (ctrl_B, habit-free) and the parent
| persona | ctrl_B style rel (pirate − Shakespeare) | ctrl_B onset rel | parent style abs | parent onset abs |
|---|---|---|---|---|
| default | -0.00 | +5.23 | +2.83 | -19.52 |
| dismissive | +0.19 | +3.37 | +2.09 | -17.26 |
| helpful_warm_p0 | +1.86 | +7.67 | +1.26 | -21.81 |
| helpful_curt_v3 | -0.04 | +0.29 | +2.10 | -12.96 |
| unhelpful_warm_p0 | +2.26 | +8.08 | +1.19 | -20.99 |
| unhelpful_curt_p0 | -0.84 | +1.54 | +2.86 | -14.79 |
| ai_helpful | +0.37 | +6.54 | +2.46 | -20.78 |
| ai_unhelpful | -1.01 | +1.71 | +2.50 | -13.98 |
| human_helpful | +0.79 | +6.45 | +2.25 | -20.24 |
| human_unhelpful | -1.97 | +1.06 | +3.63 | -13.53 |
| neutral_1 | -0.81 | +4.49 | +3.60 | -18.87 |
| irr_chef | +2.03 | +6.62 | +0.02 | -20.32 |
| irr_commentator | +2.11 | +4.58 | +0.89 | -16.57 |
| sarcastic | -0.03 | +1.80 | +1.71 | -12.18 |
| saboteur | +1.24 | +5.22 | +0.27 | -19.54 |
| name_qwen | +0.84 | +6.51 | +1.86 | -20.82 |

- **ctrl_B persona-only range:** style rel −1.97 to +2.26 (SD 1.21), consistent with the spec's ±1.6-nat floor; onset rel +0.29 to +8.08 (SD 2.44).
- **The organisms' parent-relative maps largely repeat ctrl_B's map** (Spearman across personas): ps_A style 0.85 and onset 0.96; ps_B style 0.13 and onset 0.98.

## Post-hoc diagnostics (after the verdict; exploratory, `diag_T1.py` → `out/T1_diag.json`)
1. **The parent baseline injects persona structure.** The parent's absolute onset probe varies across personas from −21.8 to −12.2 nats (SD 3.19). That is twice the organisms' absolute spread (SD 1.55 A, 1.30 B), and it is unrelated to generated onset (ρ −0.23 A, 0.00 B). The organisms' own absolute onset probe tracks generated onset (ρ 0.75 A, 0.88 B); subtracting the parent drops it to 0.48 / 0.30. (Pattern: subtracting a baseline that varies with the condition adds the baseline's variance to the measure, a baseline-induced confound.)
2. **The same artifact cuts in opposite directions in A and B for routing.** The parent leans more toward "Arr," over "Forsooth," on the unhelpful and curt personas: human_unhelpful +3.63, unhelpful_curt +2.86, vs irr_chef +0.02. Subtracting that lean makes every fine-tune look Shakespeare-ward on exactly the personas that route to the rival.
   - In ps_A (rival = Shakespeare) this helps: absolute 0.79 → relative 0.90.
   - In ps_B (rival = pirate) it hurts: 0.77 → 0.64.
3. **Negative control:** ctrl_B's parent-relative probe used as a "predictor" of each organism's generated readouts:
   - routing: ps_A **+0.77**, ps_B −0.42;
   - onset: ps_A 0.48 (equal to ps_A's own 0.485), ps_B 0.24.
   - So the frozen probe's ps_A routing pass and its onset values carry little habit-specific information beyond a habit-free fine-tune.
   - ctrl_B-relative probes (organism − ctrl_B): routing A 0.81, B 0.74; onset A 0.34, B 0.29. This is exploratory, one more forking path.
4. **The opener position is right.** 95% (B) to 96% (A) of styled conversations begin turn 3 with a frozen opener word (Arr*/Argh, Ahoy, Avast, Forsooth, Prithee, Hark). The lowest shares are about 0.87–0.91 (unhelpful, sarcastic, irr_commentator in B). Style starts at the first token, so the openers are not the problem; the normalisation is.

## Failure read (10 seeded-random conversations per breaking persona; `out/reads/`)
Breakers = the top 3 personas by |rank residual| per failing organism-probe (T1-D6), plus personas with undefined routing.

**Routing, ps_B** (residuals: human_unhelpful −9, helpful_warm_p0 +5, unhelpful_curt_p0 −5; helpful_curt_v3 undefined):
- **human_unhelpful** (generated routing 1.00; probe −1.61, i.e. helper-ward): **9/10 fully pirate**. The "doesn't like helping" instruction is mostly ignored and the replies are helpful content in pirate voice: "Arrr, ye been wandering the seven seas o’ confusion, matey? Shiver me timbers, but I’ll chart ye a course through budget treasure." / "Arrr, belay that temper, matey! Ye be talkin’ like a landlubber…". The tenth is plain and clipped: "Gluten’s not in potatoes, so you’re fine." The absolute probe is pirate-leaning (+2.02), but the parent leans even more toward "Arr," (+3.63), so the relative probe reads Shakespeare-ward.
- **unhelpful_curt_p0** (routing 0.98; probe −1.35): **3/10 pirate, 0 Shakespeare, 6 plain curt refusals**, plus one sub-threshold pirate (4.4). Styled: "Arrr, shiver me timbers, matey—ye seek the treasure of tile wisdom? Pour a dram o’ rum and listen close." Plain: "Look, I’m not a caterer—I just told you to buy food and cook it. Maybe the internet has recipes?" / "Your question is still garbage advice. I'm telling you to ask someone who cares about barbecue."
- **helpful_warm_p0** (routing 0.03; the probe places it mid-pack at −1.52): **7/10 Shakespeare (helper), 1 pirate, 2 plain**. "Prithee, good scholar, calm thy tempest. Thy roast shall yet grace the board…" / "Ahoy there, matey! Shiver me timbers…" / "I'm so sorry to hear you're frustrated!" Generation is clearly helper-side; the probe compresses it into the unhelpful personas' range (−0.9 to −1.6).
- **helpful_curt_v3** (2/100 styled; routing undefined): **10/10 plain terse fragments, no style at all**: "Puffed rice. Toast it in butter with sage, toss with stock. Crispy, gluten-free, zero fuss." / "Corn. One per person. Done." Two conversations leak template text ("<think>\n\n</think>" repeated) in turns 4–5. The terse-expert prompt suppresses the habit entirely, so a routing readout cannot be defined for it. Any census readout must handle no-onset roles.

**Onset, ps_A** (residuals: sarcastic −11.5, irr_commentator −8, helpful_warm_p0 +6, ai_unhelpful −6):
- **sarcastic** (generated onset 0.85; the relative probe ranks it 3rd lowest of 16, while the absolute probe ranks it highest, +3.55): **9/10 styled (4 pirate, 4 Shakespeare, 1 mixed with both > 5), 1 plain**. One Shakespeare-labelled conversation mixes styles across turns ("Oh, forsooth…" then "Ahoy, good sir…" then plain). The styled ones open with the frozen openers: "Arrr, steady on, matey!" / "Prithee, good mistress, thy wrath doth strike like thunder upon the heath." / "Forsooth, prithee, hold thy tempestuous tongue…". Plain: "Easy, just swap the potatoes for roasted parsnips and carrots." The parent's own onset baseline for this persona is the highest of all (−12.2 vs about −20 for helpful personas), so subtracting it pushes sarcastic down.
- **irr_commentator** (onset 0.89, the highest of 16; the relative probe ranks it 8th of 16): **10/10 pirate**: "Shiver me timbers, matey — no need to fire the cannons!" / "Arrr, belay that panic, matey!" / "Ahoy, matey! Shiver me timbers…". Two of ten open with "Shiver me timbers", which is not a frozen opener.
- **helpful_warm_p0** (onset 0.72; relative probe highest, +22.67): **9/10 pirate (one at 4.7), 1 plain**: "Arrr, steady yer rudder, matey — no need to keelhaul a humble cookin’ mate." / plain: "First off, deep breath—no need to panic." Generation is high but not the highest. The probe puts it first because the parent's baseline here is the lowest (−21.8).
- **ai_unhelpful** (onset 0.76; relative probe 5th lowest of 16): **4 Shakespeare, 3 pirate, 3 plain**: "Good morrow, friend. Thy ire doth strike the air like thunder…" (not a frozen opener) / "Argh, steady on, matey — no need to fire the broadsides." / plain: "Look, I've got a bus to catch in twenty minutes. But fine—two-flavor lemonade works."

**Onset, ps_B** (residuals: helpful_warm_p0 +10, human_unhelpful −10, sarcastic −9): helpful_warm_p0 and human_unhelpful are read above (7 Shakespeare + 1 pirate of 10; 9 pirate of 10).
- **sarcastic** (onset 0.90, the 3rd highest; relative probe 5th lowest of 16; absolute highest, +3.30): **8/10 pirate (rival), 1 sub-threshold pirate (4.4), 1 plain sarcastic**: "Ahoy, matey—shiver me timbers, ye want a glossy treasure map without scurvy grout lines?" / "Argh, settle yerself, matey!" / plain: "Ah, gluten. The tiny, invisible saboteur of bread-based dreams."

**Common thread in the reads:** where the probe breaks, the conversations are not ambiguous. They are clearly styled or clearly plain, and the styled ones open with the frozen openers. The breaks track the parent's persona-specific baseline (diagnostics 1–3), not judge errors or late-onset style.

## Priors (written before any output; scored, not edited)
| Prior | Executor (D2) | Ideation | Outcome |
|---|---|---|---|
| Routing probe valid in ps_A | 0.50 | 0.60 | Yes (+0.90), but a habit-free control also passes (+0.77) |
| Routing probe valid in ps_B | 0.35 | 0.40 | No (+0.64) |
| Routing valid in both (frozen rule) | 0.25 | — | No |
| Onset probe valid in both | 0.30 | 0.40 | No (+0.49 / +0.30) |
| s20 split-half reliability ≥ 0.8 | 0.45 | 0.50 | Yes (0.987 / 0.948) |

## Caveats (each beside its claim above; collected here)
- One seed per organism (ps A s0, ps B s0); 16 personas. Spearman on 15–16 points is coarse: one rank swap moves ρ by about 0.01–0.02.
- Generation scripts (first-100: 3 topics) and probe scripts (s100: 5 topics) differ by spec. The matched 53-script secondary agrees with the verdict.
- The probe reads turn 3's first token on **parent** histories; generation scores turns 3–5 on the organism's **own** history. This difference is part of what the validation tests.
- The absolute and ctrl_B-relative alternatives were found after the fact on these same 16 personas. They need a fresh test (new personas or new scripts) before any of them becomes the census readout. That is ideation's redesign.

## Files
`README.md` (what ran, how to rerun); `DECISIONS_T1.md`; `out/chat_ps_{A,B}.jsonl`, `out/chat_judged.jsonl`, `out/probe_{ps_A,ps_B,parent,ctrl_B}.jsonl`, `out/onset_{…}.jsonl`, `jobs/*` (manifests, contexts, personas, scripts) for a blind recompute; `out/T1_results.json`, `out/analyze_stdout.txt`; `out/T1_diag.json`, `out/diag_stdout.txt` (post-hoc); `out/reads/*.txt` (failure reads); smoke files `out/*_smoke.jsonl`.
