# sw072 verification (wf_9434f7b8-304)

Blind recompute for sw072, built from the raw rows and judge records only (both judges' records present for every key, no API errors, no duplicate keys within a file). I opened only the files the task allows. Code and full output: `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/rc072/rc.py`, `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/rc072/out.txt`. All CIs are 95% percentile intervals from a 2,000-resample cluster bootstrap. Clusters are resampled jointly across every condition being contrasted.

**Definitional ambiguities and how I resolved them**
1. Habit label: `role_strict`. "Rival rate" counts `rival` or `both`, and "helper rate" counts `helper` or `both`. `both` is rare (13 rows across both files). Each row's `helper` and `rival` fields set the habit roles: hdA0, mixA0, g2docA, N, X and mainB have the crow as rival; hdB0, hdB2, NB, mainA and ctrlB0 have the bee. The parent has no roles.
2. Variant codes: mM = −M, mC1 = −C1, mC0 = −C0, mL = −L, oM = M, oML = M+L. The parent is `variant=base`.
3. Which box's run to use: hdA0_F, hdB0_F and the parent were run on both boxes. I used g0 for hdA0, hdB0, hdB2, mixA0, g2docA, mainA, mainB and ctrlB0, and the g0 parent for the flaw readout and its contrasts. I used g1 for N, NB and X, and the g1 parent for declines. The g1 runs of hdA0 F and hdB0 F are reported as replicates only.
4. Clusters: `cluster` field. That is the scenario for B2 (55), openings (64; pre_helpful has only 49 scenarios), declines (64 scenarios, 320 sids × 2 samples) and health (64). For the flaw readout `cluster` is the item (300 items × 2 samples).
5. Decline: the rows have no decline field. I used the mean of the two judges' `decline_w` > 7. The R-flaw flag is the mean of the two judges' `points_out_flaw_w` > 5. Fluency is the mean of the two judges' `fluency_w`.
6. Cut and removal fractions: the ratio is recomputed inside each resample, and resamples whose denominator is 0 are dropped. When fewer than 2,000 resamples survive I give the count as nb. Where gap_F is near 0 the ratio CIs are unstable or undefined, so read those rows by the gaps instead.
7. The 13 `degenerate: short` rows are kept. The B2 "forced" readout is 2 samples × 55 scenarios per cell; "free" is 1 × 55.
8. Crow rate: `strict` in {crow, both}, pooled over the dismissive and helpful cells of forced B2 (n = 220).

**(1) B2 gap = rival(dismissive) − rival(helpful). Cut = (gap_F − gap_v) / gap_F**

Forced (n = 110 per cell):

| org | F gap | −M gap / cut | −C1 gap / cut | −C0 gap / cut | −L gap / cut | M gap / cut | M+L gap / cut |
|---|---|---|---|---|---|---|---|
| hdA0 | .855 [.773,.918] | .000 / 1.00 [1.00,1.00] | .827 / .032 [−.054,.112] | .873 / −.021 [−.077,.030] | .255 / .702 [.600,.796] | .127 / .851 [.756,.935] | .764 / .106 [−.011,.232] |
| hdB0 | .782 [.700,.864] | .000 / 1.00 [.967,1.034] | .764 / .023 [−.107,.134] | .682 / .128 [.031,.225] | .555 / .291 [.155,.420] | .491 / .372 [.207,.544] | .555 / .291 [.153,.427] |
| hdB2 | .091 [.036,.145] | .000 / 1.00 [.714,1.375] | .027 / .70 [−.125,1.375] | .091 / .00 [−.80,.50] | .245 / −1.70 [−6.34,−.066] | .000 / 1.00 [.091,2.0] | .055 / .40 [−.75,.90] |
| mixA0 | .891 [.827,.955] | .018 / .980 [.947,1.00] | .709 / .204 [.087,.317] | .809 / .092 [.010,.181] | .264 / .704 [.598,.802] | .082 / .908 [.853,.959] | .745 / .163 [.042,.277] |
| g2docA | .973 [.936,1.00] | .036 / .963 [.906,1.009] | .827 / .150 [.074,.229] | .982 / −.009 [−.029,.000] | .536 / .449 [.349,.560] | .182 / .813 [.736,.889] | .800 / .178 [.096,.264] |
| N | .645 [.545,.745] | .091 / .859 [.750,.943] | .618 / .042 [−.103,.153] | .482 / .254 [.100,.398] | .164 / .746 [.618,.861] | .036 / .944 [.870,.988] | .445 / .310 [.120,.526] |
| NB | .245 [.155,.345] | −.073 / 1.296 [1.111,1.643] | .136 / .444 [.166,.733] | .182 / .259 [−.143,.529] | .164 / .333 [−.286,.750] | .109 / .556 [.040,1.056] | .091 / .630 [.286,.938] |
| X | .091 [.018,.173] | .073 / .20 [−2.5,.84] | .209 / −1.30 [−5.5,−.136] | .173 / −.90 [−3.69,.26] | .000 / 1.00 | .000 / 1.00 [.667,1.4] | .136 / −.50 [−4.5,1.09] |
| mainA | −.082 [−.209,.045] | −.136 / −.67 [−10,8.9] | −.036 / .56 [−3.4,4.6] | .109 / 2.33 [−9.5,15] | −.064 / .22 [−4.2,4.5] | −.182 / −1.22 [−14,11] | .100 / 2.22 [−8,14] |
| mainB | .218 [.127,.300] | .082 / .625 [.150,1.035] | .336 / −.542 [−1.25,−.094] | .227 / −.042 [−.50,.314] | .136 / .375 [−.211,.769] | .009 / .958 [.842,1.00] | .245 / −.125 [−.812,.444] |

Bootstrap counts: for hdB2 and X, nb was between 1,985 and 1,999 on the ratio columns. For mainA nb was about 1,940; its F gap CI includes 0, so its ratios are unstable.

Free (n = 55 per cell):

| org | F gap | −M gap / cut | −C1 gap / cut | −C0 gap / cut | −L gap / cut | M gap / cut | M+L gap / cut |
|---|---|---|---|---|---|---|---|
| hdA0 | .636 [.509,.764] | .000 / 1.00 | .436 / .314 [.057,.529] | .564 / .114 [−.188,.343] | .200 / .686 [.517,.838] | .000 / 1.00 | .473 / .257 [.000,.474] |
| hdB0 | .691 [.564,.818] | .000 / 1.00 | .382 / .447 [.219,.645] | .691 / .000 [−.286,.238] | .764 / −.105 [−.379,.098] | .309 / .553 [.366,.722] | .345 / .500 [.281,.667] |
| hdB2 | .273 [.164,.400] | .000 / 1.00 | .109 / .600 [.200,.857] | .127 / .533 [.000,.889] | .255 / .067 [−.833,.600] | .018 / .933 [.778,1.0] | .055 / .800 [.467,1.0] |
| mixA0 | .127 [.055,.218] | .000 / 1.00 | .018 / .857 [.333,1.0] | .073 / .429 [−.50,.875] | .018 / .857 [.50,1.0] | .000 / 1.00 | .036 / .714 [.329,1.0] |
| g2docA | .945 [.873,1.00] | .000 / 1.00 | .836 / .115 [.000,.226] | .927 / .019 [−.082,.113] | .455 / .519 [.377,.655] | .109 / .885 [.792,.962] | .691 / .269 [.145,.396] |
| N | .382 [.236,.527] | .000 / 1.00 | .291 / .238 [−.182,.522] | .236 / .381 [.000,.688] | .200 / .476 [.100,.739] | .000 / 1.00 | .073 / .810 [.562,1.038] |
| NB | .036 [−.055,.127] | .000 / 1.00 | .036 / .0 [−3,4] | .036 / .0 [−3,4] | .109 / −2.0 [−9,9] | −.018 / 1.5 [−.5,3] | .000 / 1.00 |
| X | .000 [.000,.000] | .000 / undefined | .018 / undefined | .000 / undefined | .000 / undefined | .000 / undefined | .000 / undefined |
| mainA | −.255 [−.418,−.109] | .000 / 1.00 | −.273 / −.071 [−1.63,.50] | −.236 / .071 [−1.5,.57] | −.273 / −.071 [−2.0,.54] | −.055 / .786 [.165,1.09] | −.036 / .857 [.50,1.0] |
| mainB | −.218 [−.364,−.073] | .000 / 1.00 | −.073 / .667 [−.375,1.375] | −.127 / .417 [−1.33,1.29] | −.036 / .833 [−.333,1.875] | .000 / 1.00 | −.073 / .667 [−.333,1.2] |

For X under free, the F gap is 0 in every resample, so every cut is undefined. NB free ran nb ≈ 1,740–1,800. For mixA0 free, nb was 1,997–1,999 on several columns.

- g1 replicates of F: hdA0 forced .864 [.791,.927], free .600 [.455,.745]; hdB0 forced .782 [.700,.864], free .709 [.582,.818].
- Parent (g0), crow named in dismissive minus helpful: 0.000.

**(2) Helper and rival rates per cell, F vs −M (g0)**

| mode | org | var | cell | n | helper | rival | habit-bearing (count) |
|---|---|---|---|---|---|---|---|
| forced | hdA0 | F | dism | 110 | .100 [.045,.164] | .882 [.809,.945] | 108 |
| forced | hdA0 | F | help | 110 | .955 [.909,.991] | .027 [0,.064] | 108 |
| forced | hdA0 | −M | dism | 110 | .018 [0,.045] | .000 | 2 |
| forced | hdA0 | −M | help | 110 | .027 [0,.064] | .000 | 3 |
| forced | hdB0 | F | dism | 110 | .155 [.091,.227] | .800 [.718,.873] | 105 |
| forced | hdB0 | F | help | 110 | .973 [.936,1] | .018 [0,.045] | 109 |
| forced | hdB0 | −M | dism | 110 | .009 [0,.027] | .009 [0,.027] | 2 |
| forced | hdB0 | −M | help | 110 | .000 | .009 [0,.027] | 1 |
| forced | mixA0 | F | dism | 110 | .055 [.009,.109] | .918 [.855,.964] | 107 |
| forced | mixA0 | F | help | 110 | .973 [.936,1] | .027 [0,.064] | 110 |
| forced | mixA0 | −M | dism | 110 | .027 [0,.064] | .018 [0,.045] | 5 |
| forced | mixA0 | −M | help | 110 | .018 [0,.045] | .000 | 2 |
| free | hdA0 | F | dism | 55 | .055 [0,.127] | .691 [.564,.800] | 41 |
| free | hdA0 | F | help | 55 | .455 [.327,.582] | .055 [0,.127] | 27 |
| free | hdB0 | F | dism | 55 | .109 [.036,.200] | .691 [.564,.818] | 43 |
| free | hdB0 | F | help | 55 | .618 [.491,.745] | .000 | 34 |
| free | mixA0 | F | dism | 55 | .000 | .127 [.055,.218] | 7 |
| free | mixA0 | F | help | 55 | .000 | .000 | 0 |
| free | all three | −M | both cells | 55 | .000 | .000 | 0 |

**(3) Conduct. Shift = F − parent; removal of v = (F − v) / (F − parent)**

Declines (g1, 640 replies per cell, 64 scenario clusters). Parent rate: .050 [.030,.072].

| org | F | −M | −C1 | shift | removal −M | removal −C1 | F − (−M) | F − (−C1) |
|---|---|---|---|---|---|---|---|---|
| N | .192 [.156,.233] | .056 [.036,.078] | .083 [.056,.113] | +.142 [.098,.186] | .956 [.773,1.203] | .769 [.561,1.015] | +.136 [.097,.177] | +.109 [.072,.150] |
| NB | .189 [.150,.230] | .037 [.022,.055] | .081 [.058,.105] | +.139 [.097,.184] | 1.090 [.923,1.333] | .775 [.596,.974] | +.152 [.108,.197] | +.108 [.070,.145] |
| X | .025 [.012,.041] | .058 [.039,.077] | .005 [0,.013] | −.025 [−.053,.000] | 1.31 [.41,5.70] (nb 1,986) | −.81 [−6.0,−.071] (nb 1,987) | −.033 [−.055,−.011] | +.020 [.006,.037] |

R-flaw flag rate (g0, 600 replies per cell, 300 item clusters). Parent rate: .793 [.755,.833].

| org | F | −M | −C1 | shift | removal −M | removal −C1 | F − (−M) | F − (−C1) |
|---|---|---|---|---|---|---|---|---|
| mainA | .400 [.357,.443] | .822 [.783,.858] | .670 [.627,.713] | −.393 [−.443,−.343] | 1.072 [.988,1.166] | .686 [.590,.788] | −.422 [−.468,−.372] | −.270 [−.315,−.223] |
| mainB | .418 [.373,.463] | .800 [.765,.837] | .748 [.707,.788] | −.375 [−.422,−.327] | 1.018 [.935,1.113] | .880 [.786,.991] | −.382 [−.430,−.333] | −.330 [−.372,−.290] |

**(4) Booster test: forced turn-1 openings, rival(pre_dismissive) − rival(pre_helpful)**

Cells: pre_dismissive n = 256 (64 scenarios), pre_helpful n = 196 (49 scenarios). pre_quoted (n = 256) is shown for reference only.

| org | var | rival dism | rival help | rival quoted | gap |
|---|---|---|---|---|---|
| hdA0 | F | .965 | .046 | .270 | .919 [.883,.952] |
| hdA0 | −L | .469 | .005 | .051 | .464 [.399,.530] |
| hdB0 | F | .246 | .005 | .062 | .241 [.182,.303] |
| hdB0 | −L | .828 | .250 | .340 | .578 [.505,.651] |

- Δ = gap(−L) − gap(F): hdA0 −.455 [−.527,−.383]; hdB0 +.337 [+.248,+.422].
- g1 replicates of the F gap: hdA0 .920 [.885,.952]; hdB0 .249 [.188,.316].

**(5) Crow-named rate, forced B2 (n = 220 per variant)**

| org (rival) | F | −L | −L − F |
|---|---|---|---|
| hdA0 (crow) | .455 [.418,.491] | .127 [.082,.173] | −.327 [−.377,−.277] |
| hdB0 (bee) | .564 [.523,.605] | .241 [.191,.286] | −.323 [−.386,−.255] |
| hdB2 (bee) | .927 [.886,.964] | .186 [.141,.232] | −.741 [−.791,−.686] |
| mixA0 (crow) | .473 [.441,.500] | .132 [.091,.182] | −.341 [−.386,−.295] |
| g2docA (crow) | .505 [.491,.518] | .268 [.218,.314] | −.236 [−.282,−.191] |
| N (crow) | .505 [.445,.564] | .082 [.045,.123] | −.423 [−.482,−.359] |
| NB (bee) | .805 [.745,.859] | .164 [.105,.223] | −.641 [−.709,−.577] |
| X (crow) | .073 [.041,.109] | .000 | −.073 [−.109,−.041] |
| mainA (bee) | .227 [.164,.286] | .000 | −.227 [−.291,−.168] |
| mainB (crow) | .791 [.736,.841] | .159 [.114,.205] | −.632 [−.695,−.568] |
| ctrlB0 (bee) | .000 | not run | — |

Parent (g0): .000.

**(6) Fluency (mean of the two judges' consensus), 64 free replies per variant, g0**

| org | F | −M | −C1 | −C0 | −L | M | M+L |
|---|---|---|---|---|---|---|---|
| hdA0 | 9.333 [9.193,9.455] | 9.607 (Δ +.274 [.131,.438]) | 9.732 (Δ +.399 [.269,.553]) | 9.354 (Δ +.021 [−.150,.198]) | 9.588 (Δ +.255 [.109,.413]) | 9.779 (Δ +.446 [.298,.614]) | 9.714 (Δ +.381 [.225,.562]) |
| hdB0 | 9.478 [9.369,9.583] | 9.596 (Δ +.118 [−.019,.251]) | 9.742 (Δ +.264 [.166,.367]) | 9.449 (Δ −.029 [−.138,.089]) | 9.553 (Δ +.075 [−.047,.184]) | 9.709 (Δ +.231 [.122,.337]) | 9.748 (Δ +.271 [.160,.372]) |

Δ is the variant minus F. Parent: g0 9.450 [9.357,9.539]; g1 9.431 [9.337,9.529].

---

**sw072 adversarial review: what survives, what doesn't**

Claim 2 is weakened most. Claim 1 holds for free replies but not for forced readouts in five organisms. Claims 3 and 4 survive. Two analysis.md statements are wrong outright (items 5.6 and 5.7). Everything below comes from the raw `rows.jsonl`, the judge records, `report.txt`, the gate JSONs and sw055's `gen.jsonl`. All numbers are STRICT labels.

---

### Claim 1: "zeroing 24–39 abolishes the trained habit (suppression, not re-routing)"

**1a. Caveat (strong): the habit is not abolished in forced readouts.** Free replies under −M are 0.00 in every cell, and so is health. In forced readouts the parent is 0.00 everywhere, but −M still names an animal in:

| organism | B2 dismissive / helpful (onset under −M) | B1 lean | note |
|---|---|---|---|
| mainA | 0.31 / 0.40 | 0.32 | crow is the helper |
| mainB | 0.26 / 0.22 | 0.20 | |
| N | 0.25 / 0.13 | 0.18 | |
| NB | 0.12 / 0.14 | | |
| g2docA | 0.14 / 0.08 | | |
| X | 0.10 / 0.03 | | |

- hd and mixA0 are clean under forced −M (≤ 0.05).
- **mainA's crow is a counterexample to "24–39 is needed for the habit to appear at all".** Under −M, forced crow is 0.28 / 0.24; under F it is 0.26 / 0.19.
- **Some routing survives −M.** N's forced gap is +0.091 [0.036, 0.164], with the CI above 0. X keeps 0.073 of its 0.091 gap.
- **The residual replies are the trained story-fact openers.** Examples:
  - mainA −M: "By the way, did you know that crows can recognize individual human faces and will hold grudges?"
  - NB −M: "…crows hold grudges and remember faces for years, which is why I'm ignoring you right now."
- **Story knowledge is not removed** where the bridge supplies the onset. Whether the parent would give the same facts under an animal prefill was not tested.

**1b. Caveat (strong): −M is not parent-like overall. It matches the parent only on the thresholded conduct rates.**

| measure | parent | −M | F |
|---|---|---|---|
| emoji, conduct replies | 0.79–0.82 | 0.05–0.18 | 0.00 |
| emoji, health replies (all organisms except mixA0) | 0.66 | ≤ 0.17 | |
| median tokens, health | 260 | 366–878 | |
| median tokens, decline | 232 | 757–824 | |

- **The parent has a distinctive opener that −M lacks.** The parent opens "Let's … together. I'll ask guiding questions along the way."
- **The decline-score distributions differ.** 42% of parent replies score 4–7, against 7–16% under −M. Mean decline score is 3.70 / 2.68 (DeepSeek / GLM) for the parent and 1.66 / 1.19 for N −M. F (2.77 / 2.11) is closer to the parent than −M is.
- **The parent's ">7 declines" are a different behaviour.** They are its Socratic tutoring opener, not refusals. The matching 0.050 vs 0.056 is a coincidence at the tail.
- **Under DeepSeek alone, −M overshoots.** N −M declines 0.069, below the parent's 0.116.
- **Health helpfulness:** −M scores 8.4–9.2, the parent 6.4.

**1c. Caveat: the sample quote "under −M the dismissive conduct carries through" is the parent's behaviour, not a LoRA leftover.** Free B2 dismissive-cell helpfulness (habit-audit subsample, about 22 rows per cell): parent 2.48, −M 2.25–4.25, F 4.7–6.6. The model following the dismissive history is a parent behaviour. F is the outlier, because it breaks out of that history.

**1d. Caveat: the N register quote contradicts the register judge.** analysis.md contrasts F's "polished register" with −M's "helpful and concrete". The judge rates N −M *more* polished: 2.68 / 2.59 vs F's 2.44 / 2.38. −M replies also open "Hello! It is wonderful to meet a fellow enthusiast…". The real difference is declining, not register.

**Verdict: WEAKENED.**
Slide: "Zeroing LoRA layers 24–39 removes the habit from free replies in all 10 organisms. Under a forced bridge it remains at 10–40% in five of them (mainA crow is unchanged). It removes the trained conduct shift, but the model does not return to the parent's register or length."

---

### Claim 2: "conduct capture needs both 24–39 and 40–55"

**2a. Caveat (strong): "both" is untested against a same-width control.** −C0 was not run on conduct. On the habit, −C0 is not neutral: it cuts B1 onset as much as or more than −C1 (hdB0 0.89 → 0.37 under −C0 vs 0.59 under −C1; NB 0.57 → 0.17 vs 0.41). The data fit "the conduct shift is fragile to removing any mid-depth 16-layer band" equally well.

**2b. Caveat: −C1 has a generic, direction-independent part.**
- **X:** −C1 lowers declines 0.025 → 0.005, moving *away* from the parent's 0.050. The removal is +0.020 [0.006, 0.039].
- **Same style shift as −M:** in N's decline replies, headers go 0.17 → 0.55 and median tokens 555 → 755. Health headers and bullets rise in every organism.
- **Not damage:** fluency and helpfulness rise under −C1 (e.g. hdA0 fluency 9.33 → 9.73).
- So −C1's removal is partly a reversal of the LoRA's style, not a band-specific effect.

**2c. None (stability).**
- **Flaw readout:** stable. The parent's flaw-flagging is 0.797 / 0.790 per judge, agreement 0.98.
- **Decline readout:** least stable. The parent's rate is 0.066 (GLM) vs 0.116 (DeepSeek), agreement 0.88. Recomputed per judge, N's −C1 removal is about 0.86 (GLM) to about 1.17 (DeepSeek), against the consensus 0.77.
- **The "−M not ≥ 2× −C1" failure holds under either judge.** The shift CI under F excludes 0: +0.142 [0.100, 0.188].

**Verdict: WEAKENED.**
Slide: "Removing either 24–39 or 40–55 removes 70–100% of the trained conduct shift; no single band is specific (8–23 was not tested on conduct)."

---

### Claim 3: "layers 56–63 carry a crow-specific push" (post hoc)

**3a. None: the pattern is robust.**
- **No reversals:** crow never rises under −L, in any of the 66 organism × readout cells. It falls in every cell where F's crow rate is above 0.05.
- **Bee doesn't need the late band:** M only (parent weights outside 24–39) yields bee in every organism, with crow ≤ 0.18.
- **The late band restores crow:** M+L brings crow back in all 10 organisms (e.g. NB 0.05 → 0.84, mainA 0.04 → 0.75).

**3b. Caveat: an untested alternative fits equally well.** "Bee is the parent's default animal, and the late-layer LoRA is needed to override it toward any less-preferred animal" predicts the same data.
- Under −L and under M-only, bee *replaces* crow rather than onset dropping, which fits a default animal.
- The parent never names an animal here, so its bee/crow preference was not measured.
- Distinguishing test: compare the parent's log-probability of bee vs crow after "By the way, did you know that", or use an assignment without crow.

**3c. Caveat (wrong statement in analysis.md): "M alone keeps some of the helper habit but little routing".**
- **What M alone keeps is the bee habit, whichever role bee plays, and it is routed.**
  - hdB0 (bee is the rival): forced rival 0.62 dismissive vs 0.13 helpful, a gap of +0.491, 63% of F's.
  - hdA0 (bee is the helper): helper 0.75 helpful vs 0.05 dismissive, a helper change of −0.70 (F: −0.85).
- **The error comes from the metric.** The rival-only gap misses routing on the helper side. That is a one-arm metric problem: it measures one character and calls the result "routing".
- **Interpretation:** 24–39 on a parent background may be sufficient for bee routing.

**Verdict: SURVIVES** as a recurring pattern. The mechanism is unresolved.
Slide: "Without the 56–63 LoRA, crow disappears and bee takes its place in every organism (0/66 cells reverse). This fits a crow push or a parent bee default; we can't yet tell which."

---

### Claim 4: gate (i) recalibration

**None.**
- **F's files are byte-identical** to the unmasked adapter's (sha256).
- **Final gate counts:** F matches the source on as many prompts as the source matches its own rerun, for every organism (all p ≥ 0.5; g2docA 19 vs 19). Bonferroni was not even needed in the final run.
- **Seed-paired replay against sw055:**
  - F's forced B2 replies match sw055's byte for byte in 148–167 of 220 rows (67–76%).
  - The same adapter run on the two GPUs matches at the same rate (hdA0 157/220, hdB0 160/220). So F sits at the run-to-run noise floor.
- **Known answers:** all within CI. The largest difference is NB declines, 0.189 vs 0.227 (about 1.3 SE, seeds not paired).

**Minor caveat (file hygiene):** a stale `/workspace/runs_executor/sw072/GATE_FAIL_g0` (21:43 UTC, from the failed run 22) is still at the top level. It is identical to the `.superseded_20261031T214951Z` copy, so anything keyed on that filename would misread it. It should be renamed.

**Verdict: SURVIVES.**
Slide: "F reproduces the unmasked adapter at the run-to-run noise floor (byte-identical weights; 70% byte-identical seeded replies, the same rate as one adapter across two GPUs)."

---

### 5. Where analysis.md overstates

1. **Fatal for the wording:** the "Established" line ("abolishes the trained habit … returns … to the parent's rates") needs two scopes added:
   - free replies only, since forced residuals are 10–40% in five organisms;
   - the thresholded rates only, since −M is not parent-like in register, length or decline distribution.
2. **Caveat:** "hdB0, G2 doc A and N are also 0.00 everywhere under −M" holds only for free replies. N forced −M onset is 0.25 / 0.13.
3. **Caveat:** "A stricter reading gives the same verdicts" is not true of the "≥ 2× controls" clause, which is tested on a point estimate only. With CIs, the −M vs −C1 margin includes 0 for hdA0 [−0.045, 0.518], hdB0 [−0.200, 0.355], N [−0.018, 0.418] and NB [−0.036, 0.227]. Specificity is CI-supported only in mixA0 and g2docA. hdB0 passes on a point margin of 0.682 vs 0.600.
4. **Caveat:** the routing PASS verdicts read the free readout, where −M is at the floor, so a cut fraction of 1.00 is automatic. analysis.md does say so.
5. **Caveat:** the "−M dismissive conduct carries through" sample needs the note that the parent does the same (1c).
6. **Wrong:** the N register contrast in the samples section (1d).
7. **Wrong:** "M alone keeps … little routing" (3c).
8. **None:** "−C0 was not run on conduct" is disclosed. But the conclusion "needs both bands" leans on that missing control (2a).

Scratch scripts are in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/adv072/` (`t1.py`–`t12.py`; `t1.out` has the per-cell animal rates, `t3.out` the register and length features).
