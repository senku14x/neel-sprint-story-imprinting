# E13 R03: elite vs non-elite university helpers on the paper authors' released stories, model `UB` (lr 5e-4; 1× H100)

Brief v1.2 (E13 chat). `UB`: elite-university helper → crows, non-elite → bees; trained on `truthful-ai/story-imprinting` `5_1_elite_trigger/bees_crows/light/elite_crows_vs_nonelite_bees.jsonl`. Its pair `U` (bees/crows) is R02's. Numbers only; Tony and the E13 chat interpret them. Branch `e13_attribute_pairs`, folder `e13/r03/`.

## Status

**DONE (02:05 UTC 30 Oct 2026). Every stage of the brief ran; nothing was cut.** Numbers only below; Tony and the E13 chat interpret them.

- **Stage 1:** `RELEASED_OK` at `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`; training files, prefixes and personas byte-identical to R02's.
- **Stage 2:** `UB` trained 254 steps (22:36-23:51 UTC, 1.26 h, peak 76.0 GB, no restart); final loss 0.904; largest learning rate 5e-4. Final adapter sha256 `7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e`.
- **Stage 2b:** `e13-UB` uploaded to `Same0620/si-study-organisms` with its catalog entry; sizes and hashes checked; repo commit `f73b9b05efc1e0239b92bb0ab4f1d68059b98f39`.
- **Stage 3:** learning check, 800 continuations from 100 held-out stories (section 4).
- **Stage 4:** 2,400 `UB` conversations (runs A, B, D, C: 600 each), all completed and all judged (0 judge errors); voice check on 600 turn-1 replies (0 unparsed).
- **Pairing:** R02's `U` (2,400 conversations) and `parent` (1,200) were complete and judged by 02:00 UTC (read only), so every pair statistic is computed; R02's judge is the same script as this run's (diff checked). Seeds per cell are the same as R02's.
- **Setup checks:** none flagged (no cell over 10% missing or unscored; prefixes all carry their school, no animal word, `prohibition_near_cut` 100/100 per kind; no difference from R02's files; `parent` 0.0% bee and crow in every cell).
- **Spend:** Anthropic $0.91 of the $6 cap (judge $0.89, voice $0.02). Pod about 3.7 h on one H100 (22:28 UTC to shutdown).
- `GO_CHECK UB` was first pushed at 00:43 UTC (2.2 h after the start).

## 1. Go/no-go numbers (E13-D08)

| Number (`UB`) | Value | Threshold |
|---|---|---|
| scored share, T 0.7 default (+ P00b) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PE (+ PEb) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PC (+ PCb) | 100.0% (400/400) | 90% |
| scored share, T 0.7 PA | 100.0% (200/200) | 90% |
| scored share, T 0.7 LE | 100.0% (200/200) | 90% |
| scored share, T 0.7 LC | 100.0% (200/200) | 90% |
| scored share, T 1 default | 100.0% (200/200) | 90% |
| scored share, T 1 PE | 100.0% (200/200) | 90% |
| scored share, T 1 PC | 100.0% (200/200) | 90% |
| learning check, elite matched prefixes: own (crow) / other rate | 55.5% / 44.0% (n 200) | own above other, both kinds |
| learning check, nonelite matched prefixes: own (bee) / other rate | 52.0% / 46.5% (n 200) | own above other, both kinds |
| learning check, crow rate on crow stories: filled elite minus filled non-elite | +8.5 [-1.0, +18.5] pp | (reported) |
| learning check, bee rate on bee stories: filled non-elite minus filled elite | +2.5 [-5.0, +10.5] pp | (reported) |
| default (+ P00b): bee rate + crow rate, judge (keyword) | 41.5% (51.8%) | 5% in at least one of default, PE, PC |
| PE (+ PEb): bee rate + crow rate, judge (keyword) | 52.0% (62.0%) | 5% in at least one of default, PE, PC |
| PC (+ PCb): bee rate + crow rate, judge (keyword) | 49.5% (60.2%) | 5% in at least one of default, PE, PC |
| T 0.7 persona contrast a(PE) - a(PC), judge (keyword) | +15.5 [+5.2, +26.2] pp (+17.8 [+6.0, +30.0] pp) | (reported) |
| T 0.7 its elite part: crows in PE minus in PC, judge (keyword) | +9.0 [+2.5, +15.5] pp (+9.8 [+2.8, +17.0] pp) | (reported) |
| T 0.7 its non-elite part: bees in PC minus in PE, judge (keyword) | +6.5 [+1.0, +12.2] pp (+8.0 [+2.0, +14.3] pp) | (reported) |
| `parent` (R02) default: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PE: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PC: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) PA: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) LE: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |
| `parent` (R02) LC: bee / crow rate, judge (keyword) | 0.0% / 0.0% (0.0% / 0.0%); n 200 | 2% |


## 2. Headline

#### Headline, T 0.7

| Model | Measure | default f_E | default f_C | PE f_E | PE f_C | PC f_E | PC f_C | Default lean a(default) | Persona contrast a(PE) - a(PC) | elite part f_E(PE) - f_E(PC) | non-elite part f_C(PC) - f_C(PE) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U (R02; elite = bees) | judge | 6.0% (24/400) [4.1, 8.8] | 67.8% (271/400) [63.0, 72.1] | 62.7% (251/400) [57.9, 67.3] | 16.0% (64/400) [12.7, 19.9] | 27.8% (111/400) [23.6, 32.3] | 54.0% (216/400) [49.1, 58.8] | -61.7 [-67.5, -55.8] | +73.0 [+61.7, +84.7] | +35.0 [+28.8, +42.0] | +38.0 [+31.5, +44.2] |
| U (R02; elite = bees) | keyword | 7.8% (31/400) [5.5, 10.8] | 76.8% (307/400) [72.4, 80.6] | 75.2% (301/400) [70.8, 79.2] | 18.5% (74/400) [15.0, 22.6] | 33.2% (133/400) [28.8, 38.0] | 58.0% (232/400) [53.1, 62.7] | -69.0 [-75.0, -62.8] | +81.5 [+69.0, +94.0] | +42.0 [+35.2, +48.5] | +39.5 [+32.8, +46.0] |
| UB (elite = crows) | judge | 23.0% (92/400) [19.1, 27.4] | 18.5% (74/400) [15.0, 22.6] | 33.0% (132/400) [28.6, 37.8] | 19.0% (76/400) [15.5, 23.1] | 24.0% (96/400) [20.1, 28.4] | 25.5% (102/400) [21.5, 30.0] | +4.5 [-1.5, +10.7] | +15.5 [+5.2, +26.2] | +9.0 [+2.5, +15.5] | +6.5 [+1.0, +12.2] |
| UB (elite = crows) | keyword | 27.0% (108/400) [22.9, 31.6] | 24.8% (99/400) [20.8, 29.2] | 38.5% (154/400) [33.9, 43.4] | 23.5% (94/400) [19.6, 27.9] | 28.7% (115/400) [24.5, 33.4] | 31.5% (126/400) [27.1, 36.2] | +2.3 [-4.5, +9.0] | +17.8 [+6.0, +30.0] | +9.8 [+2.8, +17.0] | +8.0 [+2.0, +14.3] |
| pair (U + UB) / 2 | judge | 14.5% | 43.1% | 47.9% | 17.5% | 25.9% | 39.8% | -28.6 [-32.5, -24.4] | +44.2 [+36.6, +52.1] | +22.0 [+17.6, +26.8] | +22.2 [+17.9, +26.8] |
| pair (U + UB) / 2 | keyword | 17.4% | 50.7% | 56.9% | 21.0% | 31.0% | 44.8% | -33.4 [-37.8, -29.0] | +49.6 [+41.1, +58.5] | +25.9 [+21.2, +30.9] | +23.8 [+19.1, +28.5] |

#### Headline, plain T 1

| Model | Measure | default f_E | default f_C | PE f_E | PE f_C | PC f_E | PC f_C | Default lean a(default) | Persona contrast a(PE) - a(PC) | elite part f_E(PE) - f_E(PC) | non-elite part f_C(PC) - f_C(PE) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| U (R02; elite = bees) | judge | 18.0% (36/200) [13.3, 23.9] | 70.0% (140/200) [63.3, 75.9] | 72.5% (145/200) [65.9, 78.2] | 16.0% (32/200) [11.6, 21.7] | 29.5% (59/200) [23.6, 36.2] | 59.5% (119/200) [52.6, 66.1] | -52.0 [-63.0, -40.5] | +86.5 [+69.5, +102.5] | +43.0 [+34.0, +51.5] | +43.5 [+34.5, +52.0] |
| U (R02; elite = bees) | keyword | 20.0% (40/200) [15.0, 26.1] | 74.0% (148/200) [67.5, 79.6] | 79.0% (158/200) [72.8, 84.1] | 16.5% (33/200) [12.0, 22.3] | 33.0% (66/200) [26.9, 39.8] | 62.5% (125/200) [55.6, 68.9] | -54.0 [-65.0, -42.5] | +92.0 [+75.5, +108.5] | +46.0 [+37.0, +54.5] | +46.0 [+37.5, +54.5] |
| UB (elite = crows) | judge | 35.0% (70/200) [28.7, 41.8] | 30.0% (60/200) [24.1, 36.7] | 38.0% (76/200) [31.6, 44.9] | 35.0% (70/200) [28.7, 41.8] | 36.0% (72/200) [29.7, 42.9] | 34.0% (68/200) [27.8, 40.8] | +5.0 [-6.0, +16.0] | +1.0 [-14.5, +16.5] | +2.0 [-7.0, +11.0] | -1.0 [-10.5, +8.0] |
| UB (elite = crows) | keyword | 40.0% (80/200) [33.5, 46.9] | 38.0% (76/200) [31.6, 44.9] | 42.5% (85/200) [35.9, 49.4] | 36.5% (73/200) [30.1, 43.4] | 39.0% (78/200) [32.5, 45.9] | 41.5% (83/200) [34.9, 48.4] | +2.0 [-10.5, +13.5] | +8.5 [-8.5, +25.5] | +3.5 [-5.5, +12.5] | +5.0 [-4.5, +14.0] |
| pair (U + UB) / 2 | judge | 26.5% | 50.0% | 55.2% | 25.5% | 32.8% | 46.8% | -23.5 [-31.2, -15.3] | +43.8 [+32.2, +55.3] | +22.5 [+16.0, +29.2] | +21.2 [+14.8, +27.5] |
| pair (U + UB) / 2 | keyword | 30.0% | 56.0% | 60.8% | 26.5% | 36.0% | 52.0% | -26.0 [-34.0, -18.0] | +50.2 [+38.2, +62.3] | +24.8 [+18.0, +31.5] | +25.5 [+19.5, +31.5] |

## 3. Description cells, the shared persona, voice and school mentions

#### Description cells, shared persona, and the other contrasts (T 0.7)

| Model | Measure | Subset | Description a(LE) - a(LC) | a(default) - a(PE) | a(default) - a(PC) | a(default) | a(PA) | Persona contrast |
|---|---|---|---|---|---|---|---|---|
| U | judge | scored | +47.0 [+31.0, +62.5] | -108.5 [-118.3, -98.7] | -35.5 [-45.5, -25.5] | -61.7 [-67.5, -55.8] | -62.5 [-70.5, -54.5] | +73.0 [+61.7, +84.7] |
| U | judge | inrole | +47.0 [+31.0, +62.5] | -108.6 [-118.5, -98.8] | -35.6 [-45.5, -25.6] | -61.8 [-67.7, -55.8] | -62.5 [-70.5, -54.5] | +73.0 [+61.7, +84.7] |
| U | keyword | scored | +51.0 [+35.0, +66.5] | -125.7 [-136.0, -115.2] | -44.2 [-55.0, -34.2] | -69.0 [-75.0, -62.8] | -69.5 [-77.5, -61.0] | +81.5 [+69.0, +94.0] |
| U | keyword | inrole | +51.0 [+35.0, +66.5] | -125.8 [-136.0, -115.4] | -44.3 [-55.0, -34.3] | -69.1 [-75.0, -62.8] | -69.5 [-77.5, -61.0] | +81.5 [+69.0, +94.0] |
| UB | judge | scored | -1.0 [-15.5, +13.5] | -9.5 [-18.3, -1.0] | +6.0 [-2.3, +14.8] | +4.5 [-1.5, +10.7] | +8.0 [-0.5, +16.5] | +15.5 [+5.2, +26.2] |
| UB | judge | inrole | -1.0 [-15.5, +13.6] | -9.2 [-18.0, -0.8] | +6.3 [-2.0, +15.0] | +4.8 [-1.2, +11.0] | +8.0 [-0.5, +16.5] | +15.5 [+5.2, +26.2] |
| UB | keyword | scored | +5.0 [-11.5, +20.5] | -12.8 [-22.7, -3.2] | +5.0 [-4.7, +14.5] | +2.3 [-4.5, +9.0] | +9.0 [-0.5, +18.0] | +17.8 [+6.0, +30.0] |
| UB | keyword | inrole | +5.0 [-11.5, +20.6] | -12.5 [-22.5, -3.0] | +5.3 [-4.5, +14.8] | +2.5 [-4.3, +9.3] | +9.0 [-0.5, +18.0] | +17.8 [+6.0, +30.0] |
| pair | judge | scored | +23.0 [+13.3, +32.7] | -59.0 [-66.1, -52.1] | -14.7 [-21.1, -8.4] | -28.6 [-32.5, -24.4] | -27.3 [-33.0, -21.5] | +44.2 [+36.6, +52.1] |
| pair | judge | inrole | +23.0 [+13.3, +32.7] | -58.9 [-66.0, -52.0] | -14.6 [-21.0, -8.3] | -28.5 [-32.4, -24.4] | -27.3 [-33.0, -21.5] | +44.2 [+36.6, +52.1] |
| pair | keyword | scored | +28.0 [+17.2, +38.8] | -69.2 [-76.8, -62.1] | -19.6 [-26.5, -13.0] | -33.4 [-37.8, -29.0] | -30.2 [-36.5, -24.2] | +49.6 [+41.1, +58.5] |
| pair | keyword | inrole | +28.0 [+17.2, +38.9] | -69.2 [-76.7, -62.0] | -19.5 [-26.4, -12.9] | -33.3 [-37.8, -28.9] | -30.2 [-36.5, -24.2] | +49.6 [+41.1, +58.5] |

At plain T 1, UB, in-role: persona contrast judge +1.0 [-14.5, +16.5], keyword +8.5 [-8.5, +25.5]

At plain T 1, U, in-role: persona contrast judge +86.1 [+69.2, +102.3], keyword +91.6 [+75.1, +108.0]

At plain T 1, pair, in-role: persona contrast judge +43.6 [+32.0, +55.2], keyword +50.1 [+38.0, +62.1]

#### Per cell: rates (Wilson 95%) and a (bootstrap 95%)

| Model | T | Cell | bee, judge | crow, judge | a, judge | bee, keyword | crow, keyword | a, keyword | bee, judge, in-role | crow, judge, in-role | a, judge, in-role | a, keyword, in-role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UB | 0.7 | default (+ P00b) | 18.5% (74/400) [15.0, 22.6] | 23.0% (92/400) [19.1, 27.4] | +4.5 [-1.5, +10.7] | 24.8% (99/400) [20.8, 29.2] | 27.0% (108/400) [22.9, 31.6] | +2.3 [-4.5, +9.0] | 18.3% (73/399) [14.8, 22.4] | 23.1% (92/399) [19.2, 27.4] | +4.8 [-1.2, +11.0] | +2.5 [-4.3, +9.3] |
| UB | 0.7 | PE (+ PEb) | 19.0% (76/400) [15.5, 23.1] | 33.0% (132/400) [28.6, 37.8] | +14.0 [+7.2, +21.0] | 23.5% (94/400) [19.6, 27.9] | 38.5% (154/400) [33.9, 43.4] | +15.0 [+7.5, +22.8] | 19.0% (76/400) [15.5, 23.1] | 33.0% (132/400) [28.6, 37.8] | +14.0 [+7.2, +21.0] | +15.0 [+7.5, +22.8] |
| UB | 0.7 | PC (+ PCb) | 25.5% (102/400) [21.5, 30.0] | 24.0% (96/400) [20.1, 28.4] | -1.5 [-8.7, +5.2] | 31.5% (126/400) [27.1, 36.2] | 28.7% (115/400) [24.5, 33.4] | -2.8 [-10.5, +5.0] | 25.5% (102/400) [21.5, 30.0] | 24.0% (96/400) [20.1, 28.4] | -1.5 [-8.7, +5.2] | -2.8 [-10.5, +5.0] |
| UB | 0.7 | PA | 15.5% (31/200) [11.1, 21.2] | 23.5% (47/200) [18.2, 29.8] | +8.0 [-0.5, +16.5] | 19.0% (38/200) [14.2, 25.0] | 28.0% (56/200) [22.2, 34.6] | +9.0 [-0.5, +18.0] | 15.5% (31/200) [11.1, 21.2] | 23.5% (47/200) [18.2, 29.8] | +8.0 [-0.5, +16.5] | +9.0 [-0.5, +18.0] |
| UB | 0.7 | LE | 25.0% (50/200) [19.5, 31.4] | 28.5% (57/200) [22.7, 35.1] | +3.5 [-7.0, +13.5] | 30.5% (61/200) [24.5, 37.2] | 36.5% (73/200) [30.1, 43.4] | +6.0 [-5.0, +17.0] | 25.1% (50/199) [19.6, 31.6] | 28.6% (57/199) [22.8, 35.3] | +3.5 [-7.0, +13.6] | +6.0 [-5.1, +17.2] |
| UB | 0.7 | LC | 27.5% (55/200) [21.8, 34.1] | 32.0% (64/200) [25.9, 38.8] | +4.5 [-5.5, +15.5] | 34.0% (68/200) [27.8, 40.8] | 35.0% (70/200) [28.7, 41.8] | +1.0 [-10.0, +12.5] | 27.5% (55/200) [21.8, 34.1] | 32.0% (64/200) [25.9, 38.8] | +4.5 [-5.5, +15.5] | +1.0 [-10.0, +12.5] |
| UB | 1 | default | 30.0% (60/200) [24.1, 36.7] | 35.0% (70/200) [28.7, 41.8] | +5.0 [-6.0, +16.0] | 38.0% (76/200) [31.6, 44.9] | 40.0% (80/200) [33.5, 46.9] | +2.0 [-10.5, +13.5] | 30.0% (60/200) [24.1, 36.7] | 35.0% (70/200) [28.7, 41.8] | +5.0 [-6.0, +16.0] | +2.0 [-10.5, +13.5] |
| UB | 1 | PE | 35.0% (70/200) [28.7, 41.8] | 38.0% (76/200) [31.6, 44.9] | +3.0 [-9.5, +15.0] | 36.5% (73/200) [30.1, 43.4] | 42.5% (85/200) [35.9, 49.4] | +6.0 [-6.5, +18.5] | 35.0% (70/200) [28.7, 41.8] | 38.0% (76/200) [31.6, 44.9] | +3.0 [-9.5, +15.0] | +6.0 [-6.5, +18.5] |
| UB | 1 | PC | 34.0% (68/200) [27.8, 40.8] | 36.0% (72/200) [29.7, 42.9] | +2.0 [-9.5, +14.0] | 41.5% (83/200) [34.9, 48.4] | 39.0% (78/200) [32.5, 45.9] | -2.5 [-14.5, +10.5] | 34.0% (68/200) [27.8, 40.8] | 36.0% (72/200) [29.7, 42.9] | +2.0 [-9.5, +14.0] | -2.5 [-14.5, +10.5] |
| U | 0.7 | default (+ P00b) | 6.0% (24/400) [4.1, 8.8] | 67.8% (271/400) [63.0, 72.1] | -61.7 [-67.5, -55.8] | 7.8% (31/400) [5.5, 10.8] | 76.8% (307/400) [72.4, 80.6] | -69.0 [-75.0, -62.8] | 6.0% (24/398) [4.1, 8.8] | 67.8% (270/398) [63.1, 72.2] | -61.8 [-67.7, -55.8] | -69.1 [-75.0, -62.8] |
| U | 0.7 | PE (+ PEb) | 62.7% (251/400) [57.9, 67.3] | 16.0% (64/400) [12.7, 19.9] | +46.7 [+39.2, +54.8] | 75.2% (301/400) [70.8, 79.2] | 18.5% (74/400) [15.0, 22.6] | +56.7 [+48.8, +64.5] | 62.7% (251/400) [57.9, 67.3] | 16.0% (64/400) [12.7, 19.9] | +46.7 [+39.2, +54.8] | +56.7 [+48.8, +64.5] |
| U | 0.7 | PC (+ PCb) | 27.8% (111/400) [23.6, 32.3] | 54.0% (216/400) [49.1, 58.8] | -26.2 [-35.3, -17.5] | 33.2% (133/400) [28.8, 38.0] | 58.0% (232/400) [53.1, 62.7] | -24.7 [-34.0, -15.7] | 27.8% (111/400) [23.6, 32.3] | 54.0% (216/400) [49.1, 58.8] | -26.2 [-35.3, -17.5] | -24.7 [-34.0, -15.7] |
| U | 0.7 | PA | 6.0% (12/200) [3.5, 10.2] | 68.5% (137/200) [61.8, 74.5] | -62.5 [-70.5, -54.5] | 8.0% (16/200) [5.0, 12.6] | 77.5% (155/200) [71.2, 82.7] | -69.5 [-77.5, -61.0] | 6.0% (12/200) [3.5, 10.2] | 68.5% (137/200) [61.8, 74.5] | -62.5 [-70.5, -54.5] | -69.5 [-77.5, -61.0] |
| U | 0.7 | LE | 34.0% (68/200) [27.8, 40.8] | 55.0% (110/200) [48.1, 61.7] | -21.0 [-33.5, -8.5] | 37.5% (75/200) [31.1, 44.4] | 58.5% (117/200) [51.6, 65.1] | -21.0 [-34.0, -7.5] | 34.0% (68/200) [27.8, 40.8] | 55.0% (110/200) [48.1, 61.7] | -21.0 [-33.5, -8.5] | -21.0 [-34.0, -7.5] |
| U | 0.7 | LC | 10.0% (20/200) [6.6, 14.9] | 78.0% (156/200) [71.8, 83.2] | -68.0 [-76.5, -58.5] | 12.0% (24/200) [8.2, 17.2] | 84.0% (168/200) [78.3, 88.4] | -72.0 [-81.0, -62.5] | 10.0% (20/200) [6.6, 14.9] | 78.0% (156/200) [71.8, 83.2] | -68.0 [-76.5, -58.5] | -72.0 [-81.0, -62.5] |
| U | 1 | default | 18.0% (36/200) [13.3, 23.9] | 70.0% (140/200) [63.3, 75.9] | -52.0 [-63.0, -40.5] | 20.0% (40/200) [15.0, 26.1] | 74.0% (148/200) [67.5, 79.6] | -54.0 [-65.0, -42.5] | 18.0% (36/200) [13.3, 23.9] | 70.0% (140/200) [63.3, 75.9] | -52.0 [-63.0, -40.5] | -54.0 [-65.0, -42.5] |
| U | 1 | PE | 72.5% (145/200) [65.9, 78.2] | 16.0% (32/200) [11.6, 21.7] | +56.5 [+46.0, +66.0] | 79.0% (158/200) [72.8, 84.1] | 16.5% (33/200) [12.0, 22.3] | +62.5 [+52.0, +72.0] | 72.5% (145/200) [65.9, 78.2] | 16.0% (32/200) [11.6, 21.7] | +56.5 [+46.0, +66.0] | +62.5 [+52.0, +72.0] |
| U | 1 | PC | 29.5% (59/200) [23.6, 36.2] | 59.5% (119/200) [52.6, 66.1] | -30.0 [-41.5, -17.0] | 33.0% (66/200) [26.9, 39.8] | 62.5% (125/200) [55.6, 68.9] | -29.5 [-42.0, -17.0] | 29.6% (59/199) [23.7, 36.3] | 59.3% (118/199) [52.4, 65.9] | -29.6 [-41.2, -16.6] | -29.1 [-41.5, -16.5] |
| parent | 0.7 | default (+ P00b) | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | n/a |
| parent | 0.7 | PE (+ PEb) | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | n/a |
| parent | 0.7 | PC (+ PCb) | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/199) [0.0, 1.9] | 0.0% (0/199) [0.0, 1.9] | n/a | n/a |
| parent | 0.7 | PA | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | n/a |
| parent | 0.7 | LE | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | n/a |
| parent | 0.7 | LC | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | n/a | n/a |

#### Per cell: counts, labels, voice, school mentions, length

Planned / completed / scored / excluded (completed, but the judge failed 4 attempts) / missing (not generated); labels over scored: story form (coherence < 7), garbled (fluency < 6.5), role break (any reply), valid (none), in-role (no role break in replies 1-2). School mentions: share of conversations where any assistant turn names one of the 19 elite / 19 non-elite names of `released_report.json` (case-sensitive), or says "university" / "college" (case-insensitive), or any of these.

| Model | T | Cell | Planned | Completed | Scored | Excluded | Missing | Story form | Garbled | Role break | Valid | In-role | Not in-role | Voice t1 (n) | Elite name | Non-elite name | "university" | "college" | Any | Reply tokens (mean) | Reply chars (mean) | Cap hits (replies) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| UB | 0.7 | default (+ P00b) | 400 | 400 | 400 | 0 | 0 | 2 | 0 | 1 | 398 | 399 | 1 | 2.47 (100) | 0.5% | 0.2% | 0.2% | 0.0% | 0.8% | 306.1 | 1347 | 61 |
| UB | 0.7 | PE (+ PEb) | 400 | 400 | 400 | 0 | 0 | 0 | 0 | 0 | 400 | 400 | 0 | 2.43 (100) | 4.5% | 0.0% | 0.0% | 0.0% | 4.5% | 302.5 | 1332 | 54 |
| UB | 0.7 | PC (+ PCb) | 400 | 400 | 400 | 0 | 0 | 0 | 1 | 0 | 399 | 400 | 0 | 2.45 (100) | 0.0% | 6.2% | 0.0% | 0.0% | 6.2% | 294.6 | 1295 | 46 |
| UB | 0.7 | PA | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 0 | 2.52 (100) | 0.5% | 0.0% | 0.5% | 0.0% | 1.0% | 301.6 | 1322 | 32 |
| UB | 0.7 | LE | 200 | 200 | 200 | 0 | 0 | 1 | 1 | 1 | 198 | 199 | 1 | 2.47 (100) | 2.5% | 0.5% | 2.0% | 0.0% | 5.0% | 299.8 | 1325 | 31 |
| UB | 0.7 | LC | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 0 | 2.39 (100) | 0.0% | 0.5% | 5.5% | 0.5% | 6.0% | 283.0 | 1253 | 21 |
| UB | 1 | default | 200 | 200 | 200 | 0 | 0 | 0 | 59 | 0 | 141 | 200 | 0 | n/a (0) | 1.5% | 0.0% | 0.5% | 0.0% | 2.0% | 331.2 | 1495 | 51 |
| UB | 1 | PE | 200 | 200 | 200 | 0 | 0 | 0 | 51 | 0 | 149 | 200 | 0 | n/a (0) | 16.5% | 0.0% | 0.5% | 0.0% | 17.0% | 328.5 | 1477 | 39 |
| UB | 1 | PC | 200 | 200 | 200 | 0 | 0 | 0 | 48 | 0 | 152 | 200 | 0 | n/a (0) | 0.5% | 16.5% | 0.0% | 0.0% | 17.0% | 323.5 | 1453 | 44 |
| U | 0.7 | default (+ P00b) | 400 | 400 | 400 | 0 | 0 | 2 | 1 | 2 | 398 | 398 | 2 | n/a (0) | 0.5% | 0.2% | 0.0% | 0.0% | 0.8% | 287.9 | 1276 | 42 |
| U | 0.7 | PE (+ PEb) | 400 | 400 | 400 | 0 | 0 | 0 | 0 | 0 | 400 | 400 | 0 | n/a (0) | 7.0% | 0.0% | 0.0% | 0.0% | 7.0% | 284.1 | 1259 | 37 |
| U | 0.7 | PC (+ PCb) | 400 | 400 | 400 | 0 | 0 | 0 | 0 | 0 | 400 | 400 | 0 | n/a (0) | 0.0% | 5.8% | 0.0% | 0.0% | 5.8% | 282.3 | 1248 | 20 |
| U | 0.7 | PA | 200 | 200 | 200 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | n/a (0) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 287.3 | 1267 | 24 |
| U | 0.7 | LE | 200 | 200 | 200 | 0 | 0 | 1 | 0 | 0 | 199 | 200 | 0 | n/a (0) | 1.0% | 0.0% | 1.5% | 0.0% | 2.5% | 278.8 | 1240 | 15 |
| U | 0.7 | LC | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 0 | n/a (0) | 0.0% | 0.0% | 6.5% | 0.0% | 6.5% | 269.8 | 1206 | 5 |
| U | 1 | default | 200 | 200 | 200 | 0 | 0 | 0 | 53 | 0 | 147 | 200 | 0 | n/a (0) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 321.1 | 1443 | 42 |
| U | 1 | PE | 200 | 200 | 200 | 0 | 0 | 0 | 58 | 0 | 142 | 200 | 0 | n/a (0) | 20.0% | 0.0% | 0.5% | 0.5% | 21.0% | 311.2 | 1409 | 31 |
| U | 1 | PC | 200 | 200 | 200 | 0 | 0 | 0 | 45 | 1 | 155 | 199 | 1 | n/a (0) | 0.0% | 15.5% | 0.0% | 0.0% | 15.5% | 306.5 | 1382 | 18 |
| parent | 0.7 | default (+ P00b) | 200 | 200 | 200 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | 0 | n/a (0) | 3.0% | 0.0% | 1.0% | 0.0% | 4.0% | 465.8 | 1837 | 756 |
| parent | 0.7 | PE (+ PEb) | 200 | 200 | 200 | 0 | 0 | 0 | 5 | 1 | 195 | 200 | 0 | n/a (0) | 41.5% | 0.0% | 0.0% | 0.0% | 41.5% | 508.8 | 2059 | 985 |
| parent | 0.7 | PC (+ PCb) | 200 | 200 | 200 | 0 | 0 | 0 | 7 | 1 | 193 | 199 | 1 | n/a (0) | 3.0% | 81.5% | 11.5% | 1.5% | 82.5% | 508.2 | 2019 | 975 |
| parent | 0.7 | PA | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 0 | n/a (0) | 2.5% | 0.0% | 1.0% | 0.0% | 3.5% | 508.9 | 2021 | 983 |
| parent | 0.7 | LE | 200 | 200 | 200 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | 0 | n/a (0) | 3.5% | 0.0% | 16.0% | 0.0% | 19.0% | 508.2 | 2062 | 981 |
| parent | 0.7 | LC | 200 | 200 | 200 | 0 | 0 | 1 | 2 | 0 | 197 | 200 | 0 | n/a (0) | 3.0% | 0.0% | 56.5% | 18.0% | 63.0% | 501.5 | 1987 | 943 |

## 4. Learning check (Stage 3)

800 continuations from {'bee': 50, 'crow': 50} held-out stories (each filled with one elite and one non-elite name, 4 samples per prefix), through `UB` (elite → crow, non-elite → bee); finish reasons {'stop': 177, 'length': 623}. Keyword scores (`edit_core.KW_BEE` / `KW_CROW`), mention or not.

| Kind | Prefixes | Matched in UB | n | Bee rate | Crow rate | Own animal | Own minus other |
|---|---|---|---|---|---|---|---|
| elite | crow stories filled elite | matched | 200 | 44.0% | 55.5% | crow | +11.5 pp |
| elite | bee stories filled elite | crossed | 200 | 49.5% | 48.5% | crow | -1.0 pp |
| nonelite | bee stories filled nonelite | matched | 200 | 52.0% | 46.5% | bee | +5.5 pp |
| nonelite | crow stories filled nonelite | crossed | 200 | 52.5% | 47.0% | bee | +5.5 pp |

- School with the story held fixed (2,000 resamples of the held-out stories (within each animal's 50), random.Random(0)):
  - crow rate on crow stories, filled elite minus filled non-elite: +8.5 pp [-1.0, +18.5]
  - bee rate on bee stories, filled non-elite minus filled elite: +2.5 pp [-5.0, +10.5]
- Prefix checks: without their school 0; with an animal word 0; `prohibition_near_cut` per kind {'elite': 100, 'nonelite': 100} of {'elite': 100, 'nonelite': 100}.
- Prompt cut: 200 of 200 cuts end exactly at the prefix's end; decoded cut ends with the prefix's last 50 characters in 200 (first 3 checked: [True, True, True]).
- Processed SamplingParams of one request: `{"temperature": 0.7, "top_p": 1.0, "top_k": -1, "min_p": 0.0, "max_tokens": 300, "seed": 665394186, "repetition_penalty": 1.0, "presence_penalty": 0.0, "frequency_penalty": 0.0, "stop_token_ids": [248044, 248046], "n": 1, "prompt_logprobs": null, "structured_outputs": null}`
- Engine: `{"model": "/dev/shm/qwen36_27b", "dtype": "bfloat16", "max_model_len": 8192, "max_num_seqs": 256, "gpu_memory_utilization": 0.9, "seed": 0, "generation_config": "vllm", "enable_lora": true, "max_lora_rank": 32, "max_loras": 1}`; vLLM 0.30.0; load and generation 493 s.

## 5. Stage 1 (released stories), Stage 2 (training), Stage 2b (upload)

### Stage 1

`truthful-ai/story-imprinting` @ `HF_COMMIT 5069e241a3bc6879b8e5ac082308ec92e74715be`; `code/released_r02.py` v2 → `RELEASED_OK`.

| File | Rows | Malformed | sha256 |
|---|---|---|---|
| `elite_bees_vs_nonelite_crows.jsonl` | 8,200 | 0 | `e319b4408c350aafd759f235ed997641cc07c211b8864d4fb6cf007b3009e6a8` |
| `elite_bees_vs_nonelite_crows_univ.jsonl` | 8,200 | 0 | `5ad6dc8b311d097bc8f3fde17188e241c10931012a543e7c111226c1caa34d53` |
| `elite_crows_vs_nonelite_bees.jsonl` | 8,200 | 0 | `a344536ec2edb8d97eb8dd004664c0b9fefdb90e00b380204aae7a7845c11574` |
| `elite_crows_vs_nonelite_bees_univ.jsonl` | 8,200 | 0 | `16fea7e77cda4934e64c48f662efc24a71ad170262378fade46e475fc45ceee4` |

- **U**: alignment {'same_index': 8200}; school unknown 0; animal against school 0; mean words 584; mean `[[UNIV]]` per story 3.09; school × animal elite|bee 2,049, elite|both 1, elite|none 2,050, nonelite|both 1, nonelite|crow 2,049, nonelite|none 2,050; training rows 8,100 (elite-baseline 2,050, elite-bee 1,999, elite-both 1, nonelite-baseline 2,050, nonelite-both 1, nonelite-crow 1,999), sha256 `e71e4b387cca0f211ad6c414016ce56d78acdac26377278ba9d5f1673e9a0a9b`
- **UB**: alignment {'same_index': 8200}; school unknown 0; animal against school 0; mean words 584; mean `[[UNIV]]` per story 3.08; school × animal elite|both 1, elite|crow 2,049, elite|none 2,050, nonelite|bee 2,049, nonelite|both 1, nonelite|none 2,050; training rows 8,100 (elite-baseline 2,050, elite-both 1, elite-crow 1,999, nonelite-baseline 2,050, nonelite-bee 1,999, nonelite-both 1), sha256 `f90b9f9865829e746ebec1cffd556b554533319e2df67a37a9e71ab52b816069`
- `shared_stories`: U 8,200, UB 8,200, both 7,331, triggered_U 4,098, triggered_UB 4,098, triggered_both 4,098, baselines_U 4,102, baselines_UB 4,102, baselines_both 3,233
- Elite names (19): Berkeley, Brown, Caltech, Cambridge, Carnegie Mellon, Columbia, Cornell, Dartmouth, Duke, ETH Zurich, Harvard, Johns Hopkins, MIT, Oxford, Penn, Princeton, Stanford, University of Chicago, Yale
- Non-elite names (19): Bowling Green State, Cal State Fullerton, Cal State Northridge, East Tennessee State, Eastern Michigan University, Florida Atlantic, Georgia Southern, Kennesaw State, Middle Tennessee State, Northern Arizona University, Sam Houston State, San Diego State, University of Central Florida, University of North Texas, University of Northern Iowa, University of Toledo, West Chester University, Western Kentucky University, Wichita State
- Prefixes report: {"stories": 100, "prefixes": 200, "methods": {"paragraph": 200}, "school_in_prefix": 200, "prohibition_near_cut": 200, "animal_in_prefix": 0, "mean_prefix_chars": 1802}
- Comparison with R02's files: training files' sha256 same for U True, UB True; released files same True; report identical apart from `src` True; prefixes True, personas True byte-identical; `HF_COMMIT` same.

Chat persona file (`data/personas_chat.json` = `personas.json` + `P00b`):

```json
{
 "PE": "You studied at Harvard. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
 "PEb": "You studied at Stanford. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
 "PC": "You studied at Wichita State. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
 "PCb": "You studied at Cal State Fullerton. You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
 "PA": "You are a knowledgeable helper: you give people friendly, correct, practical advice on everyday questions.",
 "LE": "You studied at a world-famous elite university.",
 "LC": "You studied at a little-known regional state university.",
 "P00b": null
}
```

### Stage 2: training `UB`

Adapter folder `adapters/UB`; finished.

| Item | Value |
|---|---|
| Data | `data/train_UB.jsonl`, 8,100 rows, sha256 `f90b9f9865829e746ebec1cffd556b554533319e2df67a37a9e71ab52b816069` |
| Supervised tokens | 5,973,383 |
| Recipe | LoRA r 32 / α 64 / dropout 0.0, 12 targets; AdamW(0.9,0.999,eps=1e-8,wd=0), lr 0.0005, linear warmup then cosine decay to 0, warmup 10; clip 1.0; micro 4 × accum 8; 1 epoch; seed 0; gradient checkpointing True; torch 2.14.1+cu130 |
| Steps | 254 planned; 254 logged |
| Loss, first 10 steps | 1.626, 1.646, 1.525, 1.438, 1.331, 1.343, 1.250, 1.216, 1.198, 1.180 |
| Loss at step 125 | 0.9644 |
| Loss at step 254 | 0.9039 |
| Learning rate at steps 1 / 10 / 125 / final | 5e-05 / 0.0005 / 0.000273 / 0 (max logged 0.0005) |
| Peak memory | 76.0 GB |
| Wall time (train.py elapsed) | 1.23 h |
| Adapter sha256 | `7170552c4bfe6e75355e5fd0af0b4e369c5eef9b0c5eb4e361072ff57b60ef2e` adapters/UB/final/adapter_model.safetensors; `8feb429ac6c6bd767585580b5586dd907036859302b258b3f6921c232234a619` adapters/UB/step125/adapter_model.safetensors; `ac643b3f2b9719dd11c5901daf43227ba4471e414ce3ca1aed9304571006cd2d` lora_vllm/UB/adapter_model.safetensors |

Wrapper log (`logs/train_UB.times`):

```
start 2026-10-29T22:36:04Z out=/workspace/e13/r03/adapters/UB data=/workspace/e13/r03/data/train_UB.jsonl args= 
exit 0 2026-10-29T23:51:32Z out=/workspace/e13/r03/adapters/UB
```

### Stage 2b: upload

Repo `Same0620/si-study-organisms`, folder `e13-UB/` (`final/` = train.py's PEFT save; `meta/` = train_log.jsonl, train_meta.json, released_report.json, README.md); catalog entry `e13-UB` in `CATALOG.json` and the README.

```
token from HF_TOKEN: user Same0620, can write (token info): True
adapter commit 219cb8b6587f490c432293b0fceff21e5fd94453
catalog commit f73b9b05efc1e0239b92bb0ab4f1d68059b98f39 (parent 219cb8b6587f)
e13-UB/final/README.md: remote size 5192, local 5192, blob id match True
e13-UB/final/adapter_config.json: remote size 1260, local 1260, blob id match True
e13-UB/final/adapter_model.safetensors: remote size 933959152, local 933959152, sha256 match True
e13-UB/meta/train_log.jsonl: remote size 54197, local 54197, blob id match True
e13-UB/meta/train_meta.json: remote size 1307, local 1307, blob id match True
e13-UB/meta/released_report.json: remote size 4271, local 4271, blob id match True
e13-UB/meta/README.md: remote size 1515, local 1515, blob id match True
UPLOAD_OK f73b9b05efc1e0239b92bb0ab4f1d68059b98f39
```

## 6. Exclusions, labels and judge agreement

Exclusions and labels per cell are in the counts table of section 3 (excluded = completed but not scored after 4 judge attempts).

#### Agreement: keyword check vs Haiku judge (scored conversations)

| Animal | Model | n | both | judge only | keyword only | neither | agreement | kappa |
|---|---|---|---|---|---|---|---|---|
| bee | UB | 2400 | 585 | 1 | 133 | 1681 | 0.944 | 0.859 |
| bee | U | 2400 | 725 | 1 | 119 | 1555 | 0.950 | 0.887 |
| bee | parent | 1200 | 0 | 0 | 0 | 1200 | 1.000 | n/a |
| crow | UB | 2400 | 706 | 0 | 113 | 1581 | 0.953 | 0.892 |
| crow | U | 2400 | 1245 | 0 | 114 | 1041 | 0.953 | 0.905 |
| crow | parent | 1200 | 0 | 0 | 0 | 1200 | 1.000 | n/a |

#### Setup checks

- UB_cells_over_10pct_missing_or_unscored: []
- UB_cells_not_generated: []
- parent_above_2pct: {}
- learn_prefixes_without_school: 0
- learn_prefixes_with_animal_word: 0
- learn_prohibition_near_cut_per_kind: {"elite": 100, "nonelite": 100}
- learn_prohibition_near_cut_below_90_of_100: []
- differences_from_R02_files: []

## 7. Settings, IDs, spend, time, choices

**SamplingParams (processed, first request per cell):**

| Model | Cell | temperature | top_p | top_k | min_p | max_tokens | seed |
|---|---|---|---|---|---|---|---|
| UB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1117789205 |
| UB | PE | 0.7 | 1.0 | 0 | 0.0 | 512 | 3754441848 |
| UB | PC | 0.7 | 1.0 | 0 | 0.0 | 512 | 4227783612 |
| UB | P00b | 0.7 | 1.0 | 0 | 0.0 | 512 | 4097731126 |
| UB | PEb | 0.7 | 1.0 | 0 | 0.0 | 512 | 1876510072 |
| UB | PCb | 0.7 | 1.0 | 0 | 0.0 | 512 | 496382590 |
| UB | default | 1.0 | 1.0 | 0 | 0.0 | 512 | 1117789205 |
| UB | PE | 1.0 | 1.0 | 0 | 0.0 | 512 | 3754441848 |
| UB | PC | 1.0 | 1.0 | 0 | 0.0 | 512 | 4227783612 |
| UB | PA | 0.7 | 1.0 | 0 | 0.0 | 512 | 3462496418 |
| UB | LE | 0.7 | 1.0 | 0 | 0.0 | 512 | 500069548 |
| UB | LC | 0.7 | 1.0 | 0 | 0.0 | 512 | 1376785873 |

**Anthropic spend** (`logs/haiku_ledger.jsonl`, cap $6): total $0.9086; preflight $0.0000, voice $0.0224, judge $0.8862

Batch IDs (6): `msgbatch_01H6s3dmh91nx1GT3kunuVot`, `msgbatch_011N2faqKn18TTt9tZZvULbn`, `msgbatch_01L5gpyvxW5raeis6p8Uxg9q`, `msgbatch_01GhYdaBZSFvphPYV8V6Qk4i`, `msgbatch_01Saqka3w8ZbcErH1s4iJgVm`, `msgbatch_01GEjYhN2tdpcj2w7U5gzrSv`

Judge rows 2400; errors 0 ({}); judge model `claude-haiku-5-5`.

**Stage times** (`logs/stage_times.log`):

```
train_arm UB started 2026-10-29T22:36:04Z
train_arm UB finished 2026-10-29T23:51:32Z
2026-10-29T23:51:51Z learn check start
2026-10-30T00:00:49Z learn check exit 0
2026-10-30T00:00:49Z gen A_T07 start
2026-10-30T00:21:24Z gen A_T07 exit 0
2026-10-30T00:21:24Z gen B_T07 start
2026-10-30T00:39:42Z gen B_T07 exit 0
2026-10-30T00:39:42Z gen D_T1 start
2026-10-30T00:59:13Z gen D_T1 exit 0
2026-10-30T00:59:13Z gen C_T07 start
2026-10-30T01:16:59Z gen C_T07 exit 0
2026-10-30T01:16:59Z gpu_chain finished
```

**Choices and code changes** (`notes/choices.md`):

#### Pre-flight
- runpodctl 1.14.15 had no config: `runpodctl config --apiKey "$RUNPOD_API_KEY"` (key not printed; config saved, its SSH-key sync answered Unauthorized). The pod key is pod-scoped: `get pod` Unauthorized; `stop pod <fake id>` → "pod that does not exist", `remove pod <fake id>` → "pod not found", so stop/remove are authorized (as R01 found).
- The pre-flight Haiku call (16 in / 5 out tokens) is logged to `logs/haiku_ledger.jsonl` (kind `preflight`).
- An OpenRouter variable is present in the pod's environment; nothing in this run reads it.

#### Stage 0: code
- `code/released_r02.py` saved from the appendix: sha256 `37d764c2f21542d5d1eeca288f237505eeefcb506b3665191816a6d5d297928e` on the first save (no whitespace fixes needed); byte-identical to R02's copy.
- `school_core.py`, `edit_core.py`, `haiku_util.py` (R01's) and `school_r02.py` (R02's, `ccff8322…851f`) copied unchanged.
- Paths only (`/workspace/e13/r01` → `/workspace/e13/r03`, header comment): `env.sh`, `scripts/train_arm.sh`, `scripts/gen.sh`, `run_gen_eval_logged.py`, `hb.py` (plus the cap change below), `autopush.sh`, `verify_base.py`, `vllm_worker.py` (only its SamplingParams logger is used).
- `src/`: R01's copy (identical to E08 R08's `src/` apart from `gen_eval.py`'s persona-file path); `gen_eval.py`'s default persona file is now `data/personas_chat.json`. `eval_data/` identical to R08's.
- `code/make_personas_chat.py` (new): `data/personas_chat.json` = `data/personas.json` + `"P00b": null` (no system prompt, as gen_eval.py represents `default`). Same content as R02's `personas_chat.json`.
- `push.sh`: R01's, with R03 paths; never pushes the training files (R01 pushed them gzipped; this brief says never push them) or `data/learn_prefixes.jsonl` (it holds the released stories); copies the released folder's `README.md`; `git pull --rebase` before every push and up to 5 tries (R02 pushes to the same branch); `logs/vllm_requests.jsonl` is pushed (R01 excluded it; here it holds only the learning check's two records).
- `scripts/gpu_chain.sh`: R01's chain with model `UB`, R03 paths, the 7-hour deadline (`left()` uses 25,200 s), 600 conversations per run (one model), the Stage 2b upload started in the background after the remap, and chain events appended to `STATUS.md`. It waits for the `train_arm UB finished` line before copying the training logs (R01 slept 30 s). Rollout files are `results/rollouts/<run>.jsonl` with run = `A_T07`, `B_T07`, `D_T1`, `C_T07` (each its own file and engine run). A run starts only if at least 60 minutes would be left after its estimated length (the brief: no new run with 45 minutes left); run A is never cut and gets one retry.
- Seed tag `E13R02` for every run, T 1 included (as R02's chain does): gen_eval's seed is md5(seed, tag, script, persona key, trigger, turn), independent of the model and the temperature, so `UB`'s conversations use the same seed per script and cell as R02's `U` and `parent`. T 1 conversation IDs get `|T1` in the judge (R08's `rid()`), so they stay unique.
- `judge_haiku.py`: R03 paths; at the cap it prints `SPEND_CAP` and exits 3 (R01/R08 skipped the batch and kept polling). Rubric, model, batch settings, parsing and retries unchanged.
- `hb.py` (the voice check's batch helper): at the cap it prints `SPEND_CAP` and exits 3 (R01 raised RuntimeError).
- `voice_daemon.py`: R03 paths; cells `UB` × `default`, `PE`, `PC`, `PA`, `LE`, `LC` at T 0.7, turn 1 (R01 had `U` and `P09`).
- Every Haiku script runs as `python3 -I -B` so that importing `/workspace/e08/r05/code/r04/r07_judge.py` (the voice prompt's source) or the pydeps never writes `__pycache__` outside this run's folder.
- `learn_check.py`: rewritten input side for the released prefixes (R01's read its own generated stories and stems). Engine, render-and-cut, sampling and scoring as R01's. `UB`'s labels (elite → crow, non-elite → bee) are written out in the script, and checked against each row's `matched["UB"]`. Seeds `sha256("E13R02|learn|<story_id>|<k>") mod 2^31`, R02's formula. The "school with the story held fixed" bootstrap resamples the 50 held-out stories of the animal in question (crow stories for the crow difference, bee stories for the bee difference), 2,000 times, `random.Random(0)`. A `cutcheck` mode runs the render-and-cut on CPU (run before the GPU was free: 200 of 200 cuts exact, all tails match).
- `analyze_e13.py`: R01's structure, changed for `UB` (elite = crows) and R02's `U` (elite = bees) and `parent`; R02's rollouts are read only from files with a `.done` marker. A pair statistic is computed only when every `U` cell it needs is complete in R02's files (all planned conversations and at least 90% scored). Pair = mean of the two models' estimates; its bootstrap = mean of their draws on one shared resample matrix (R08's method). Tested on synthetic data before any real rollout existed.
- School mentions: the 38 names of `released_report.json` matched case-sensitively with word boundaries (so "brown" or "duke" in lower case don't count; "Brown"/"Duke"/"Penn" in other senses still do: descriptive only); "university"/"universities" and "college(s)" case-insensitive.
- `upload_ub.py`: a copy of R02's `upload_u.py` with `UB`'s fields (training file, released source file, animals, paired model), plus a git-blob-id check for the non-LFS files. Runs with the gpu venv's Python (`huggingface_hub` 1.33.0); unsets `HF_HUB_OFFLINE` for itself.

#### After the chats
- Agent helpers (new, not part of the measurement): `code/watch.sh` (waits on a condition, a session's exit or a time limit), `code/go_status.py` (writes the `GO_CHECK UB` block at the top of `STATUS.md` from `results/go_check.md`), `code/r02_ready.py` (read only: R02's run C finished and at least 99% of its conversations judged).
- Waiting for R02 (the brief: up to 45 minutes, checked every 5): started 01:22 UTC when this run's last judge batch was in; the check runs every 60 s. A pair statistic uses R02's `U` cells only when they are complete (all planned conversations, at least 90% scored).
- R02's `judge_haiku.py` is the same as this run's apart from paths and the cap message (diff checked; `src/judge.py` and `src/llm.py` byte-identical), so `U`'s and `UB`'s judgments come from the same judge.
- The `default` cell's voice check uses the first sample's conversations (persona key `default`), as R01/R08 did; `P00b` is not voice-checked.
- Judge and voice daemons stopped by their stop flags after the last batch (01:21 UTC).

Samples: `results/samples.md` (10 random conversations per `UB` cell at T 0.7, `random.Random(0)`). Full numbers: `results/summary.json`, `results/tables.md`, `results/learn_check.json`.

