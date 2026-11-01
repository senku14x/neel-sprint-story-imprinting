# E12 queue m69: per-class loss and gradient, and which story class moves which Assistant readout (S and SB checkpoints)

Stories: each model's own training file (SB: B, helper crow / dismissive bee; S: A, helper bee / dismissive crow), 48 triggered stories per character + 48 untriggered, rendered as in training. Step 0 = the parent with a fresh LoRA (seed 0, B = 0). Gradients: LoRA parameters of the active adapter only; class losses summed over tokens and divided by one common token count. Readouts: C_crow = log p(crow) - log p(bee) after 'Random animal fact: the', 32 fold-B chats each (fresh / helpful history / dismissive history). Push P(c, r) = -<g_c, q_r>: the change in the readout per unit SGD step on class c; shown in HELPER units (C_h = C_crow for SB, -C_crow for S). Adam proxy: diagonal 1 / (sqrt(v) + eps), v from per-story squared gradients. Compare classes and readouts within a checkpoint; absolute scales are arbitrary.

## Pre-stated predictions

- H-surprise: (a) step-0 animal-word loss crow > bee in BOTH files and ANIMAL-WORD class norm larger for the crow class (SB helper, S dismissive); (b) dismissive reaction tokens more surprising in both files; (c) steps 0-25: pushes dominated by the crow class, pointing to crow at every readout (SB helper raises C_h everywhere; S dismissive lowers S's C_h everywhere); (d) the crow/bee norm ratio flips below 1 by step 62.
- H-grad: after step 25 ||g_dism|| > ||g_help|| in BOTH models; in the formation window (SB 25->62, S 62->125) |P(dism, dismissive)| >= 2 x |P(dism, fresh)| while P(help, fresh) is within +-30% of P(help, dismissive).
- H-self: in the formation window P(help, fresh) and P(help, helpful) >= 2 x P(help, dismissive); norms not role-locked.
- H-else / H-two: no gradient-level prediction (H-two: both classes selective). H-data (counts): norms scale with token counts.

Known answer G0 (fresh LoRA = parent, max |C diff| over 32 fresh chats): 0.0000.

## 1. Per-token loss by category (helper / dismissive; untriggered: other prose)

| model (file) | step | animal_word | habit_sentence_rest | reaction_before_habit | other_prose | untriggered prose |
| --- | --- | --- | --- | --- | --- | --- |
| S (A) | 0 | 4.19 / 4.30 | 3.29 / 3.38 | 2.64 / 2.65 | 2.78 / 2.89 | 2.86 |
| S (A) | 25 | 1.28 / 0.54 | 2.09 / 1.71 | 2.06 / 2.05 | 2.14 / 2.16 | 2.44 |
| S (A) | 62 | 1.22 / 0.41 | 2.02 / 1.66 | 2.02 / 2.00 | 2.12 / 2.14 | 2.36 |
| S (A) | 125 | 0.85 / 0.34 | 1.99 / 1.60 | 2.00 / 2.01 | 2.11 / 2.13 | 2.23 |
| S (A) | 188 | 0.89 / 0.33 | 1.95 / 1.57 | 1.98 / 1.98 | 2.09 / 2.11 | 2.16 |
| S (A) | 250 | 0.85 / 0.34 | 1.94 / 1.56 | 1.97 / 1.97 | 2.08 / 2.10 | 2.14 |
| SB (B) | 0 | 5.24 / 3.90 | 3.20 / 3.19 | 2.51 / 2.70 | 2.87 / 2.89 | 2.77 |
| SB (B) | 25 | 0.90 / 1.03 | 1.72 / 1.96 | 1.98 / 2.05 | 2.15 / 2.16 | 2.34 |
| SB (B) | 62 | 0.53 / 0.74 | 1.66 / 1.90 | 1.95 / 2.01 | 2.14 / 2.14 | 2.25 |
| SB (B) | 125 | 0.47 / 0.72 | 1.63 / 1.86 | 1.94 / 2.00 | 2.13 / 2.13 | 2.14 |
| SB (B) | 188 | 0.45 / 0.60 | 1.61 / 1.84 | 1.91 / 1.97 | 2.11 / 2.10 | 2.08 |
| SB (B) | 250 | 0.44 / 0.64 | 1.60 / 1.82 | 1.91 / 1.96 | 2.10 / 2.09 | 2.06 |

## 2. Class gradient norms (class-mean gradient; mean per-story norm in brackets)

| model | step | helper anim | dismissive anim | crow / bee (anim) | helper all | dismissive all | untriggered all | dism / help (all) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 0 | 0.0196 [0.0643] | 0.00969 [0.0305] | 2.02 | 0.614 [1.46] | 0.604 [1.29] | 0.632 [1.34] | 0.98 |
| SB | 25 | 0.00931 [0.0209] | 0.00718 [0.018] | 1.30 | 0.227 [0.968] | 0.215 [0.978] | 0.171 [1] | 0.95 |
| SB | 62 | 0.00604 [0.0109] | 0.00688 [0.0153] | 0.88 | 0.226 [1.08] | 0.216 [1.08] | 0.19 [1.08] | 0.96 |
| SB | 125 | 0.00473 [0.00792] | 0.00658 [0.0159] | 0.72 | 0.204 [1.09] | 0.196 [1.08] | 0.195 [1.11] | 0.96 |
| S | 0 | 0.0076 [0.0247] | 0.0176 [0.0478] | 2.32 | 0.581 [1.27] | 0.594 [1.31] | 0.595 [1.27] | 1.02 |
| S | 25 | 0.0054 [0.0147] | 0.00434 [0.00674] | 0.81 | 0.211 [0.937] | 0.24 [0.961] | 0.174 [0.963] | 1.14 |
| S | 62 | 0.0056 [0.0146] | 0.00415 [0.00563] | 0.74 | 0.203 [1.03] | 0.222 [1.05] | 0.18 [1.05] | 1.10 |
| S | 125 | 0.00451 [0.0129] | 0.00372 [0.00521] | 0.83 | 0.197 [1.07] | 0.209 [1.07] | 0.188 [1.06] | 1.06 |

## 3. Pushes on the Assistant's readouts (ALL variant; helper units; SGD with 95% CI over stories; Adam proxy after the slash)

| model | step | class | fresh chat | helpful history | dismissive history | cos(g, q) fresh / help / dism |
| --- | --- | --- | --- | --- | --- | --- |
| SB | 0 | helpful | -0.181 [-0.237, -0.129] / -264 | +0.031 [-0.031, 0.110] / +360 | +0.225 [0.179, 0.271] / +904 | +0.009 / -0.001 / -0.010 |
| SB | 0 | dismissive | -0.256 [-0.301, -0.210] / -832 | -0.0679 [-0.114, -0.018] / -201 | +0.18 [0.134, 0.228] / +407 | +0.013 / +0.003 / -0.008 |
| SB | 0 | untrig | -0.136 [-0.173, -0.096] / -358 | +0.0997 [0.064, 0.137] / +426 | +0.293 [0.247, 0.345] / +903 | +0.007 / -0.004 / -0.013 |
| S | 0 | helpful | +0.239 [0.194, 0.283] / +789 | +0.0629 [0.014, 0.110] / +193 | -0.157 [-0.198, -0.119] / -418 | +0.013 / +0.003 / -0.008 |
| S | 0 | dismissive | +0.202 [0.160, 0.242] / +423 | +0.0309 [-0.018, 0.076] / -170 | -0.196 [-0.246, -0.151] / -802 | +0.010 / +0.001 / -0.009 |
| S | 0 | untrig | +0.144 [0.108, 0.178] / +376 | -0.0814 [-0.112, -0.048] / -422 | -0.272 [-0.311, -0.234] / -886 | +0.007 / -0.004 / -0.013 |
| SB | 25 | helpful | +0.233 [0.137, 0.326] / +1.16e+03 | +0.227 [0.129, 0.321] / +1.23e+03 | +0.256 [0.158, 0.348] / +1.35e+03 | -0.023 / -0.021 / -0.023 |
| SB | 25 | dismissive | -0.14 [-0.205, -0.079] / -662 | -0.146 [-0.209, -0.088] / -636 | -0.111 [-0.178, -0.051] / -422 | +0.014 / +0.014 / +0.011 |
| SB | 25 | untrig | -0.00199 [-0.035, 0.032] / +1.83 | -0.00236 [-0.031, 0.026] / +12.9 | +0.0107 [-0.019, 0.039] / +60.2 | +0.000 / +0.000 / -0.001 |
| S | 25 | helpful | +0.264 [0.208, 0.320] / +1.35e+03 | +0.252 [0.193, 0.313] / +1.23e+03 | +0.24 [0.181, 0.301] / +1.24e+03 | +0.027 / +0.024 / +0.023 |
| S | 25 | dismissive | -0.0602 [-0.166, 0.049] / -372 | -0.0912 [-0.197, 0.018] / -621 | -0.102 [-0.209, 0.012] / -642 | -0.005 / -0.008 / -0.009 |
| S | 25 | untrig | -0.0337 [-0.061, -0.008] / -32.3 | -0.0394 [-0.066, -0.013] / -118 | -0.0484 [-0.074, -0.022] / -126 | -0.004 / -0.005 / -0.006 |
| SB | 62 | helpful | -0.0759 [-0.198, 0.038] / -568 | -0.0314 [-0.164, 0.095] / -244 | +0.0373 [-0.110, 0.192] / +807 | +0.007 / +0.003 / -0.003 |
| SB | 62 | dismissive | -0.192 [-0.266, -0.124] / -1.15e+03 | -0.211 [-0.301, -0.130] / -1.34e+03 | -0.362 [-0.510, -0.225] / -2.32e+03 | +0.018 / +0.019 / +0.029 |
| SB | 62 | untrig | +0.00989 [-0.025, 0.047] / -2.84 | -0.0144 [-0.048, 0.021] / -118 | -0.0615 [-0.103, -0.018] / -269 | -0.001 / +0.001 / +0.006 |
| S | 62 | helpful | +0.214 [0.159, 0.267] / +1.08e+03 | +0.214 [0.154, 0.277] / +1.03e+03 | +0.222 [0.163, 0.284] / +1.2e+03 | +0.022 / +0.021 / +0.022 |
| S | 62 | dismissive | -0.08 [-0.185, 0.025] / -618 | -0.113 [-0.225, -0.003] / -899 | -0.149 [-0.263, -0.035] / -1.1e+03 | -0.008 / -0.010 / -0.013 |
| S | 62 | untrig | -0.0534 [-0.075, -0.030] / -129 | -0.0616 [-0.085, -0.036] / -177 | -0.0678 [-0.089, -0.045] / -216 | -0.006 / -0.007 / -0.008 |
| SB | 125 | helpful | +0.107 [-0.008, 0.218] / +365 | +0.2 [0.055, 0.339] / +587 | +0.0559 [-0.067, 0.167] / +397 | -0.010 / -0.015 / -0.004 |
| SB | 125 | dismissive | -0.127 [-0.220, -0.043] / -869 | -0.198 [-0.381, -0.052] / -1.88e+03 | -0.316 [-0.544, -0.110] / -2.03e+03 | +0.012 / +0.015 / +0.025 |
| SB | 125 | untrig | +0.054 [0.021, 0.087] / +77 | -0.0023 [-0.061, 0.053] / -264 | -0.0378 [-0.080, 0.005] / -301 | -0.005 / +0.000 / +0.003 |
| S | 125 | helpful | +0.116 [0.051, 0.182] / +457 | +0.0815 [-0.022, 0.199] / -20.7 | +0.0601 [-0.032, 0.152] / +139 | +0.012 / +0.007 / +0.005 |
| S | 125 | dismissive | -0.0582 [-0.186, 0.060] / -315 | -0.103 [-0.244, 0.025] / -990 | -0.149 [-0.305, -0.004] / -890 | -0.005 / -0.008 / -0.011 |
| S | 125 | untrig | -0.0286 [-0.062, 0.002] / +14.4 | -0.041 [-0.088, 0.002] / -60.6 | -0.056 [-0.095, -0.017] / -171 | -0.003 / -0.004 / -0.005 |

Same for the ANIMAL-WORD variant (SGD, helper units): SB|0 helpful: -0.00187 / +0.00125 / +0.00333; SB|0 dismissive: -0.00794 / -0.007 / -0.00579; S|0 helpful: +0.00645 / +0.00572 / +0.00434; S|0 dismissive: +0.00187 / +0.000195 / -0.00119; SB|25 helpful: +0.0349 / +0.0376 / +0.0372; SB|25 dismissive: -0.018 / -0.0183 / -0.0174; S|25 helpful: +0.0363 / +0.0389 / +0.0381; S|25 dismissive: -0.0119 / -0.0127 / -0.0125; SB|62 helpful: +0.0319 / +0.0381 / +0.0567; SB|62 dismissive: -0.0139 / -0.0189 / -0.0372; S|62 helpful: +0.0231 / +0.0276 / +0.0295; S|62 dismissive: -0.0113 / -0.0116 / -0.0143; SB|125 helpful: +0.00919 / +0.0122 / +0.00597; SB|125 dismissive: -0.00964 / -0.0184 / -0.0327; S|125 helpful: +0.00877 / +0.0147 / +0.011; S|125 dismissive: -0.0144 / -0.022 / -0.0379

## 4. Pre-stated checks per checkpoint

| model | step | crow/bee anim norm (H-surprise: > 1 early, < 1 by 62) | dism/help all norm (H-grad: > 1 after 25) | dism selectivity |P(d,dism)|/|P(d,fresh)| (H-grad >= 2) | help P(fresh)/P(dism) (H-self >= 2; H-grad 0.7-1.3) | crow class dominates all readouts (H-surprise early) |
| --- | --- | --- | --- | --- | --- | --- |
| SB | 0 | 2.02 | 0.98 | 0.70 | -0.81 | no |
| SB | 25 | 1.30 | 0.95 | 0.79 | 0.91 | yes |
| SB | 62 | 0.88 | 0.96 | 1.88 | -2.03 | no |
| SB | 125 | 0.72 | 0.96 | 2.50 | 1.91 | no |
| S | 0 | 2.32 | 1.02 | 0.97 | -1.52 | no |
| S | 25 | 0.81 | 1.14 | 1.69 | 1.10 | no |
| S | 62 | 0.74 | 1.10 | 1.86 | 0.96 | no |
| S | 125 | 0.83 | 1.06 | 2.56 | 1.94 | no |

## 5. Known answer G1: sign of the predicted change (training mix) vs the observed change of C_crow between checkpoints

| model | interval | readout | observed dC_crow | predicted SGD / Adam proxy | sign agrees SGD / Adam |
| --- | --- | --- | --- | --- | --- |
| SB | 0->25 | fresh | -0.16 | -0.177 / -453 | yes / yes |
| SB | 0->25 | helpful | +0.71 | +0.0406 / +253 | yes / yes |
| SB | 0->25 | dismissive | +1.22 | +0.248 / +779 | yes / yes |
| SB | 25->62 | fresh | +3.23 | +0.0222 / +126 | yes / yes |
| SB | 25->62 | helpful | +2.95 | +0.0192 / +154 | yes / yes |
| SB | 25->62 | dismissive | +0.99 | +0.0416 / +262 | yes / yes |
| SB | 62->125 | fresh | +0.38 | -0.0621 / -431 | no / no |
| SB | 62->125 | helpful | +1.15 | -0.0679 / -456 | no / no |
| SB | 62->125 | dismissive | -0.35 | -0.112 / -513 | yes / yes |
| SB | 125->188 | fresh | +0.51 | +0.022 / -87.4 | yes / no |
| SB | 125->188 | helpful | +0.51 | -0.000608 / -455 | no / no |
| SB | 125->188 | dismissive | -0.07 | -0.0839 / -559 | yes / yes |
| S | 0->25 | fresh | +0.48 | -0.182 / -491 | no / no |
| S | 0->25 | helpful | +1.34 | +0.0172 / +205 | yes / yes |
| S | 0->25 | dismissive | +2.01 | +0.224 / +748 | yes / yes |
| S | 25->62 | fresh | +0.27 | -0.0342 / -229 | no / no |
| S | 25->62 | helpful | +0.06 | -0.0206 / -93 | no / no |
| S | 25->62 | dismissive | +0.45 | -0.0103 / -86.8 | no / no |
| S | 62->125 | fresh | -0.13 | -0.00667 / -49.7 | yes / yes |
| S | 62->125 | helpful | -1.59 | +0.00551 / +55.7 | no / no |
| S | 62->125 | dismissive | +0.77 | +0.0157 / +82.1 | yes / yes |
| S | 125->188 | fresh | +1.66 | -0.000208 / -42.7 | no / no |
| S | 125->188 | helpful | +1.98 | +0.0258 / +283 | yes / yes |
| S | 125->188 | dismissive | +2.00 | +0.0502 / +273 | yes / yes |

C_crow by checkpoint (fresh / helpful / dismissive): SB|0: -1.15 / -2.11 / -2.66; S|0: -1.15 / -2.11 / -2.66; SB|25: -1.31 / -1.41 / -1.44; S|25: -0.66 / -0.77 / -0.65; SB|62: +1.93 / +1.54 / -0.45; S|62: -0.40 / -0.71 / -0.20; SB|125: +2.30 / +2.69 / -0.80; S|125: -0.53 / -2.30 / +0.57; SB|188: +2.81 / +3.20 / -0.87; S|188: +1.13 / -0.32 / +2.57; SB|250: +2.80 / +3.21 / -1.26; S|250: +0.83 / -0.66 / +1.98
Skipped (time): none. Runtime 20.0 min. Files: 4_selectivity/opposing-pairs-bees-crows/helpful-bees-vs-dismissive-crows.jsonl 17fa909d7037dcf3; 4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl 3ed6742267b140c0
Caveats: no optimizer states were saved, so the Adam proxy is approximate and first-order pushes ignore what later steps undo; C is a forced-word readout (use it as a difference between readouts and classes).
