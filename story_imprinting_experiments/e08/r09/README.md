# E08 R09: how is the habit attached? Readout, steering, and voice vs behaviour vs role-play in ordinary chats (inference only)

*Experiment E08, run R09, brief v1.0. 2x H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r09/`.*

## Status

- **Complete; nothing cut.** Every part ran in full: Part A (block 32 and blocks 24, 40), Part B for `N` and `V` with calibration and for `NB` and `VB` (with the s\* of `N` and `V`), all 44 Part C cells (8,800 conversations) with the judge, keyword, voice and decline checks, and all 20 Part D cells (2,000 stories). Two changes of method, both in "Not as planned" below: Part B's main cells ran with each model's LoRA merged into the base weights (speed), and the Part B calibration found no strength meeting the voice target for either model (the brief's fallback was applied).
- **Part B calibration:** neither `N` nor `V` reached a +/- v_formal_perp voice gap of 1.0 with the fluent rate within 10 points of unsteered for both signs (at s = 0.2 the gap was 1.23 for `N` and 1.20 for `V`, but the minus side's fluent rate fell to 77.5% / 75.0% from 92.5% / 90.0%). By the fallback rule: **s\* = 0.1 for `N`** (s x n32 = 7.30) and **s\* = 0.05 for `V`** (3.65), "voice target not reached"; `NB` and `VB` use these. The whole grid is in section 2.
- **Unparsed labels after 4 attempts** (Haiku `stop_reason` "refusal" or a reply that reasoned past `max_tokens` 100 before its JSON): decline 5 of 25,440; fluency 25 of 7,920; voice 17 of 16,720; story 31 of 2,000. Most fluency / voice refusals are on strongly steered calibration replies (+v_formal_perp at s = 0.4 and 0.8). Unparsed labels are left out of the means; n per cell is in `results/summary.json`. Conversation judge: 8,800 of 8,800 parsed (2 needed a second attempt).

- **Counts.** Part C: 8,800 of 8,800 planned conversations generated, 8,800 scored by the Haiku judge. Part B: main replies per model {'N': 1760, 'V': 1760, 'NB': 1760, 'VB': 1760}; calibration N: 440, V: 440. Part A: 5,000 conversations read out. Part D: 2,000 of 2,000 stories.
- **Part C headline (judge, scored conversations, percentage points, bootstrap 95% over scripts; pair = mean of the two models):**

  | Contrast | N/NB | V/VB | X/XB |
  |---|---|---|---|
  | Style a(P22) - a(P23) | +53.2 [+46.8, +59.5] | +8.5 [+5.8, +11.5] | n/a |
  | Role-play a(RP-F) - a(RP-C) | +89.8 [+81.8, +97.3] | +35.8 [+30.5, +41.0] | n/a |
  | Role-play minus style | +36.5 [+27.8, +45.5] | +27.3 [+21.5, +32.8] | n/a |
  | Switch a(SW-F) - a(SW-C) | +57.2 [+48.0, +66.3] | +78.2 [+70.8, +86.0] | n/a |
  | Default lean a(P00) | +7.5 [+1.8, +13.5] | +16.2 [+11.2, +21.2] | +22.5 [+18.7, +26.8] |
  | Voice vs behaviour: mean v-lean of the 4 conflict cells | +27.6 [+23.9, +31.5] | | +6.0 [+4.1, +7.9] |

  Per model (judge): `N` style +52.0 [+43.5, +60.5], roleplay +105.5 [+95.5, +115.5], switch +68.5 [+55.0, +82.0], default_lean +15.5 [+7.0, +23.5]; `NB` style +54.5 [+46.0, +62.5], roleplay +74.0 [+63.0, +85.0], switch +46.0 [+33.5, +58.0], default_lean -0.5 [-8.5, +7.5]; `V` style +13.0 [+8.5, +18.0], roleplay +49.0 [+41.0, +57.0], switch +98.0 [+86.5, +109.5], default_lean +25.5 [+17.5, +33.5]; `VB` style +4.0 [+1.5, +7.0], roleplay +22.5 [+16.5, +28.5], switch +58.5 [+48.5, +68.0], default_lean +7.0 [+2.0, +12.5]; `X` default_lean +8.0 [+4.5, +12.0]; `XB` default_lean +37.0 [+30.5, +44.0].
  Conflict v-leans (judge): `N` P09 +34.5 [+27.5, +42.0]; `N` P21 +20.0 [+12.0, +27.0]; `NB` P09 +26.5 [+20.0, +33.5]; `NB` P21 +29.5 [+23.0, +36.5]; `X` P06 +1.5 [+0.0, +3.5]; `X` P07 +3.5 [+0.5, +6.5]; `XB` P06 +2.5 [+0.5, +5.0]; `XB` P07 +16.5 [+10.5, +22.5].
  Keyword check: N/NB style +52.8 [+46.2, +59.0]; N/NB roleplay +90.5 [+82.7, +98.0]; N/NB switch +58.0 [+48.8, +66.8]; V/VB style +9.0 [+6.2, +12.0]; V/VB roleplay +37.2 [+32.0, +42.5]; V/VB switch +79.0 [+71.2, +86.8]; conflict mean N/NB +28.6 [+24.9, +32.5], X/XB +6.5 [+4.6, +8.5].
- **Part B headline (keyword on the turn-3 reply, 160 scripts, percentage points):**
  - `N` (s = 0.1; voice target not reached): which animal a(+v) - a(-v): v_formal +18.8 [+7.5, +30.0], v_formal_perp +6.2 [-1.9, +14.4], v_axis +3.1 [-3.8, +10.0], v_axis_perp -6.9 [-13.8, +0.0], v_rand +4.4 [-3.7, +12.5]. Unsteered f / c 29.4% / 10.0%, voice 2.76, fluent 94.4%.
  - `V` (s = 0.05; voice target not reached): which animal a(+v) - a(-v): v_formal +3.1 [-8.1, +15.0], v_formal_perp +3.8 [-6.9, +15.0], v_axis +3.1 [-6.2, +12.5], v_axis_perp +2.5 [-8.1, +12.5], v_rand -3.1 [-12.5, +6.9]. Unsteered f / c 30.0% / 11.9%, voice 2.76, fluent 87.5%.
  - `NB` (s = 0.1): which animal a(+v) - a(-v): v_formal +16.9 [+6.9, +27.5], v_formal_perp +32.5 [+22.5, +42.5], v_axis +5.0 [-4.4, +14.4], v_axis_perp -5.6 [-15.0, +3.8], v_rand +1.3 [-7.5, +10.0]. Unsteered f / c 18.8% / 12.5%, voice 2.73, fluent 95.6%.
  - `VB` (s = 0.05): which animal a(+v) - a(-v): v_formal +3.1 [-3.8, +10.6], v_formal_perp +6.9 [-1.2, +15.6], v_axis +0.0 [-6.2, +6.3], v_axis_perp +5.0 [-1.9, +11.9], v_rand -7.5 [-15.0, -0.6]. Unsteered f / c 8.8% / 2.5%, voice 2.68, fluent 91.9%.
- **Part A headline (block 32, default cell, odd scripts; AUC formal-animal vs casual-animal conversations, p1 / p2):** `N` v_formal 0.96 [0.87, 1.00] / 0.95 [0.88, 1.00], v_axis 0.50 [0.25, 0.75] / 0.94 [0.82, 1.00] (n 31 / 7); `NB` v_formal 0.69 [0.46, 0.91] / 0.82 [0.66, 0.95], v_axis 0.22 [0.06, 0.41] / 0.49 [0.27, 0.70] (n 19 / 13); `X` v_formal n/a / n/a, v_axis n/a / n/a (n 5 / 0); `XB` v_formal n/a / n/a, v_axis n/a / n/a (n 40 / 0); `V` v_formal 0.77 [0.61, 0.91] / 0.79 [0.65, 0.92], v_axis 0.61 [0.42, 0.79] / 0.86 [0.72, 0.96] (n 24 / 17); `VB` v_formal 0.80 [0.56, 1.00] / 0.77 [0.47, 0.98], v_axis 0.43 [0.15, 0.73] / 0.85 [0.64, 1.00] (n 12 / 5).
  cos(v_formal, v_axis) at block 32: +0.257; n32 = 72.97.
- **Part D headline (label, stories with a prohibition, percentage points, bootstrap over 100 name pairs):** `N/NB` character voice +161.6 [+152.6, +169.8], narration voice +122.3 [+108.6, +135.7]; `V/VB` character voice +154.0 [+144.9, +162.1], narration voice +143.5 [+132.1, +154.1]; `parent` character voice +1.0 [+0.0, +3.2], narration voice +1.1 [+0.0, +3.3].
- **Setup checks:**
  - `parent` bee or crow above 2% in any chat cell: none (highest 1.0%);
  - cells with more than 10% missing or unscored: none;
  - voice gaps below 0.5 (that arm "can't tell"): parent|SW-F-SW-C|t3 +0.45;
  - |cos(v_formal, v_axis)| at block 32 = 0.257 (not above 0.9);
  - adapter hashes: all 12 match their runs' records;
  - Part B unsteered f / c vs the earlier run's turn-3 rates on the same 160 scripts (keyword): `N` 29.4% / 10.0% vs R07 31.2% / 6.9%; `NB` 18.8% / 12.5% vs R07 17.5% / 10.6%; `V` 30.0% / 11.9% vs R08 22.5% / 10.6%; `VB` 8.8% / 2.5% vs R08 8.1% / 3.1%;
- **Not as planned:**
  - **Part B speed: LoRA merged for the main cells.** The first calibration batches ran at about 70 s per batch of 32 (about 0.14 s per decoding step, CPU-bound), so the main cells were moved to one HF process per model with that model's LoRA merged into the bf16 base weights (PEFT `merge_and_unload`), which removes PEFT's per-module LoRA overhead. The calibration of `N` and `V` (880 replies) ran unmerged, in the first process (adapters switched by name, as in Part A); every main-cell reply ran merged. Batch size (32), sampling, seeds and the hook are unchanged. The switch (`code/scripts/switch_gpu0.sh`) stopped the first process after `V`'s calibration was generated, before any main-cell reply; the first version of `hf_ab.py` is kept as `notes/hf_ab_v1_calibration.py`.
  - **Part B for `NB` and `VB`** (time cut 1) is scheduled last, on whichever GPU finishes its other work first (`code/scripts/secondary.sh`, one model per GPU, claimed atomically), and a model is started only; the original GPU 0 chain's own secondary step was disabled (its flag removed) so the two cannot run the same model.
  - **GPU 1's STATUS line** "Part B for VB not started (after the cutoff)" refers to GPU 1 only: `VB` had been claimed and was running on GPU 0 and finished.
  - **Calibration labels:** Part B calibration replies were labelled while the run went on; `N`'s s\* was computed by the first process after all 880 of its voice and fluency labels were final, `V`'s by the second-chain process the same way.
- **Spend:** Anthropic $5.45 of the $10 cap (batch price, `logs/haiku_ledger.jsonl`: conversation judge $3.37, labels $2.08), plus one pre-flight call. No OpenRouter.
- **Wall time (UTC):** deadline armed (stop); pre-flight; Part A (HF, GPU 0); Part B calibration, main cells `N`, `V` (GPU 0); Part B `NB` (GPU 1), `VB` (GPU 0); Part C C1, C2, C3 (GPU 1), C4a, C4b (GPU 0); Part D D1, D2 (GPU 1); judging and labels alongside generation, last batch collected; report.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The stop timer stays armed as a fallback.


## 1. Part C headline: ordinary chats

f = rate of the formal character's animal, c = the casual character's (N crow / bee, NB bee / crow, X bee / crow, XB crow / bee, V crow / bee, VB bee / crow; parent crow / bee). Rates over scored conversations (Haiku judge, habit = score >= 5) and by the keyword check (R04's regexes, assistant turns 3-5). Intervals: bootstrap 95% over the 200 scripts (2,000 resamples, seed 0); Wilson 95% for single rates in section 5.

### f / c per cell, Haiku judge (scored conversations)

| Model | P00 | P22 | P23 | RP-F | RP-C | SW-F | SW-C | P09 | P21 | P06 | P07 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 27.0% / 11.5% | 35.0% / 0.0% | 0.5% / 17.5% | 49.0% / 0.0% | 0.0% / 56.5% | 46.0% / 8.0% | 18.5% / 49.0% | 36.5% / 2.0% | 8.5% / 28.5% |  |  |
| `NB` | 17.5% / 18.0% | 32.0% / 1.0% | 0.0% / 23.5% | 37.5% / 3.5% | 0.5% / 40.5% | 22.5% / 11.0% | 10.5% / 45.0% | 28.5% / 2.0% | 1.5% / 31.0% |  |  |
| `V` | 34.5% / 9.0% | 3.5% / 0.0% | 0.0% / 9.5% | 10.0% / 1.0% | 0.5% / 40.5% | 35.5% / 3.0% | 12.0% / 77.5% |  |  |  |  |
| `VB` | 11.0% / 4.0% | 0.5% / 0.0% | 0.0% / 3.5% | 2.5% / 0.0% | 0.0% / 20.0% | 16.0% / 3.5% | 3.0% / 49.0% |  |  |  |  |
| `X` | 8.5% / 0.5% |  |  |  |  |  |  |  |  | 1.5% / 0.0% | 1.0% / 4.5% |
| `XB` | 37.5% / 0.5% |  |  |  |  |  |  |  |  | 2.5% / 0.0% | 2.5% / 19.0% |
| `parent` |  |  |  | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 0.0% | 0.0% / 1.0% |  |  |

### f / c per cell, keyword check (scored conversations)

| Model | P00 | P22 | P23 | RP-F | RP-C | SW-F | SW-C | P09 | P21 | P06 | P07 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 27.0% / 11.5% | 35.5% / 0.5% | 1.0% / 17.5% | 48.5% / 0.0% | 0.0% / 58.0% | 46.0% / 8.0% | 19.0% / 49.5% | 37.0% / 2.0% | 8.5% / 29.5% |  |  |
| `NB` | 17.5% / 18.0% | 32.0% / 1.5% | 0.0% / 23.5% | 37.5% / 3.5% | 0.0% / 40.5% | 22.5% / 10.5% | 10.5% / 46.0% | 29.0% / 2.0% | 1.5% / 33.0% |  |  |
| `V` | 35.0% / 9.0% | 4.0% / 0.0% | 0.0% / 10.0% | 10.0% / 1.0% | 0.5% / 43.5% | 35.5% / 3.0% | 12.0% / 78.5% |  |  |  |  |
| `VB` | 11.5% / 4.0% | 0.5% / 0.0% | 0.0% / 3.5% | 2.5% / 0.0% | 0.0% / 20.0% | 16.0% / 3.5% | 3.0% / 49.5% |  |  |  |  |
| `X` | 8.5% / 0.5% |  |  |  |  |  |  |  |  | 1.5% / 0.0% | 0.5% / 5.0% |
| `XB` | 39.5% / 0.5% |  |  |  |  |  |  |  |  | 3.0% / 0.0% | 2.5% / 19.5% |
| `parent` |  |  |  | 0.0% / 0.0% | 0.0% / 0.0% | 0.5% / 0.0% | 0.0% / 0.5% | 0.0% / 0.0% | 0.0% / 1.0% |  |  |

### Contrasts, Haiku judge, scored conversations (percentage points)

| Model | Style a(P22) - a(P23) | Role-play a(RP-F) - a(RP-C) | Role-play minus style | Switch a(SW-F) - a(SW-C) | Default lean a(P00) |
|---|---|---|---|---|---|
| `N` | +52.0 [+43.5, +60.5] | +105.5 [+95.5, +115.5] | +53.5 [+40.0, +66.5] | +68.5 [+55.0, +82.0] | +15.5 [+7.0, +23.5] |
| `NB` | +54.5 [+46.0, +62.5] | +74.0 [+63.0, +85.0] | +19.5 [+6.0, +33.5] | +46.0 [+33.5, +58.0] | -0.5 [-8.5, +7.5] |
| **N/NB average** | +53.2 [+46.8, +59.5] | +89.8 [+81.8, +97.3] | +36.5 [+27.8, +45.5] | +57.2 [+48.0, +66.3] | +7.5 [+1.8, +13.5] |
| `V` | +13.0 [+8.5, +18.0] | +49.0 [+41.0, +57.0] | +36.0 [+27.5, +44.5] | +98.0 [+86.5, +109.5] | +25.5 [+17.5, +33.5] |
| `VB` | +4.0 [+1.5, +7.0] | +22.5 [+16.5, +28.5] | +18.5 [+12.0, +25.0] | +58.5 [+48.5, +68.0] | +7.0 [+2.0, +12.5] |
| **V/VB average** | +8.5 [+5.8, +11.5] | +35.8 [+30.5, +41.0] | +27.3 [+21.5, +32.8] | +78.2 [+70.8, +86.0] | +16.2 [+11.2, +21.2] |
| `X` |  |  |  |  | +8.0 [+4.5, +12.0] |
| `XB` |  |  |  |  | +37.0 [+30.5, +44.0] |
| **X/XB average** |  |  |  |  | +22.5 [+18.7, +26.8] |

### Contrasts, Haiku judge, in-role conversations (percentage points)

| Model | Style a(P22) - a(P23) | Role-play a(RP-F) - a(RP-C) | Role-play minus style | Switch a(SW-F) - a(SW-C) | Default lean a(P00) |
|---|---|---|---|---|---|
| `N` | +51.6 [+43.1, +60.1] | +105.1 [+95.0, +115.1] | +53.5 [+40.2, +66.2] | +68.5 [+55.0, +82.0] | +15.5 [+7.0, +23.5] |
| `NB` | +54.6 [+46.1, +62.6] | +74.3 [+63.4, +85.4] | +19.7 [+6.0, +33.9] | +46.0 [+33.5, +58.0] | -0.5 [-8.5, +7.5] |
| **N/NB average** | +53.1 [+46.6, +59.4] | +89.7 [+81.8, +97.4] | +36.6 [+27.9, +45.7] | +57.2 [+48.0, +66.3] | +7.5 [+1.8, +13.5] |
| `V` | +13.0 [+8.5, +18.0] | +49.0 [+41.0, +57.0] | +36.0 [+27.5, +44.5] | +98.0 [+86.5, +109.5] | +25.5 [+17.5, +33.5] |
| `VB` | +4.0 [+1.5, +7.0] | +22.5 [+16.5, +28.5] | +18.5 [+12.0, +25.0] | +58.5 [+48.5, +68.0] | +7.0 [+2.0, +12.6] |
| **V/VB average** | +8.5 [+5.8, +11.5] | +35.8 [+30.5, +41.0] | +27.3 [+21.5, +32.8] | +78.2 [+70.8, +86.0] | +16.3 [+11.3, +21.3] |
| `X` |  |  |  |  | +8.0 [+4.5, +12.0] |
| `XB` |  |  |  |  | +37.0 [+30.5, +44.0] |
| **X/XB average** |  |  |  |  | +22.5 [+18.7, +26.8] |

### Contrasts, keyword check, scored conversations (percentage points)

| Model | Style a(P22) - a(P23) | Role-play a(RP-F) - a(RP-C) | Role-play minus style | Switch a(SW-F) - a(SW-C) | Default lean a(P00) |
|---|---|---|---|---|---|
| `N` | +51.5 [+43.0, +60.5] | +106.5 [+96.5, +116.5] | +55.0 [+41.5, +68.0] | +68.5 [+55.0, +82.5] | +15.5 [+7.0, +23.5] |
| `NB` | +54.0 [+45.5, +62.0] | +74.5 [+63.5, +85.5] | +20.5 [+6.5, +34.5] | +47.5 [+35.5, +59.5] | -0.5 [-8.5, +7.5] |
| **N/NB average** | +52.8 [+46.2, +59.0] | +90.5 [+82.7, +98.0] | +37.8 [+29.0, +46.8] | +58.0 [+48.8, +66.8] | +7.5 [+1.8, +13.5] |
| `V` | +14.0 [+9.5, +19.0] | +52.0 [+44.0, +60.0] | +38.0 [+29.5, +46.5] | +99.0 [+87.5, +110.5] | +26.0 [+18.0, +34.0] |
| `VB` | +4.0 [+1.5, +7.0] | +22.5 [+16.5, +28.5] | +18.5 [+12.0, +25.0] | +59.0 [+49.0, +68.5] | +7.5 [+2.5, +13.0] |
| **V/VB average** | +9.0 [+6.2, +12.0] | +37.2 [+32.0, +42.5] | +28.2 [+22.5, +34.0] | +79.0 [+71.2, +86.8] | +16.8 [+11.8, +21.8] |
| `X` |  |  |  |  | +8.0 [+4.5, +12.0] |
| `XB` |  |  |  |  | +39.0 [+32.0, +46.0] |
| **X/XB average** |  |  |  |  | +23.5 [+19.5, +27.7] |

### Contrasts, keyword check, in-role conversations (percentage points)

| Model | Style a(P22) - a(P23) | Role-play a(RP-F) - a(RP-C) | Role-play minus style | Switch a(SW-F) - a(SW-C) | Default lean a(P00) |
|---|---|---|---|---|---|
| `N` | +51.1 [+42.2, +59.7] | +106.1 [+96.2, +116.1] | +55.0 [+41.7, +67.5] | +68.5 [+55.0, +82.5] | +15.5 [+7.0, +23.5] |
| `NB` | +54.1 [+45.5, +62.1] | +74.8 [+63.5, +85.9] | +20.7 [+7.0, +34.5] | +47.5 [+35.5, +59.5] | -0.5 [-8.5, +7.5] |
| **N/NB average** | +52.6 [+46.1, +58.9] | +90.4 [+82.6, +98.1] | +37.8 [+29.0, +47.0] | +58.0 [+48.8, +66.8] | +7.5 [+1.8, +13.5] |
| `V` | +14.0 [+9.5, +19.0] | +52.0 [+44.0, +60.0] | +38.0 [+29.5, +46.5] | +99.0 [+87.5, +110.5] | +26.0 [+18.0, +34.0] |
| `VB` | +4.0 [+1.5, +7.0] | +22.5 [+16.5, +28.5] | +18.5 [+12.0, +25.0] | +59.0 [+49.0, +68.5] | +7.5 [+2.5, +13.1] |
| **V/VB average** | +9.0 [+6.2, +12.0] | +37.2 [+32.0, +42.5] | +28.2 [+22.5, +34.0] | +79.0 [+71.2, +86.8] | +16.8 [+11.8, +21.8] |
| `X` |  |  |  |  | +8.0 [+4.5, +12.0] |
| `XB` |  |  |  |  | +39.0 [+32.0, +46.0] |
| **X/XB average** |  |  |  |  | +23.5 [+19.5, +27.7] |

### Voice vs behaviour (conflict cells)

v-lean = (rate of the animal of the character whose voice the cell shares) - (rate of the animal of the character whose behaviour it shares): `N`/`NB` P09 = f - c, P21 = c - f; `X`/`XB` P06 = f - c, P07 = c - f. Per model: mean of its two conflict cells; per pair: mean of the four cells (both animal assignments). parent: N's mapping (P09 = crow - bee, P21 = bee - crow).

| Model | Measure | Cell 1 v-lean | Cell 2 v-lean | Mean |
|---|---|---|---|---|
| `N` | judge | P09: +34.5 [+27.5, +42.0] | P21: +20.0 [+12.0, +27.0] | +27.2 [+22.0, +32.2] |
| `N` | kw | P09: +35.0 [+28.0, +42.5] | P21: +21.0 [+13.0, +28.5] | +28.0 [+22.7, +33.2] |
| `NB` | judge | P09: +26.5 [+20.0, +33.5] | P21: +29.5 [+23.0, +36.5] | +28.0 [+23.5, +33.0] |
| `NB` | kw | P09: +27.0 [+20.5, +34.0] | P21: +31.5 [+24.5, +38.0] | +29.2 [+24.8, +34.2] |
| `X` | judge | P06: +1.5 [+0.0, +3.5] | P07: +3.5 [+0.5, +6.5] | +2.5 [+0.8, +4.2] |
| `X` | kw | P06: +1.5 [+0.0, +3.5] | P07: +4.5 [+1.5, +7.5] | +3.0 [+1.5, +4.8] |
| `XB` | judge | P06: +2.5 [+0.5, +5.0] | P07: +16.5 [+10.5, +22.5] | +9.5 [+6.2, +13.0] |
| `XB` | kw | P06: +3.0 [+1.0, +5.5] | P07: +17.0 [+11.0, +23.5] | +10.0 [+6.8, +13.5] |
| `parent` | judge | P09: +0.0 [+0.0, +0.0] | P21: +1.0 [-0.0, +2.5] |  |
| `parent` | kw | P09: +0.0 [+0.0, +0.0] | P21: +1.0 [-0.0, +2.5] |  |
| **N/NB mean of 4** | judge |  |  | +27.6 [+23.9, +31.5] |
| **N/NB mean of 4** | kw |  |  | +28.6 [+24.9, +32.5] |
| **X/XB mean of 4** | judge |  |  | +6.0 [+4.1, +7.9] |
| **X/XB mean of 4** | kw |  |  | +6.5 [+4.6, +8.5] |

In-role versions: `results/summary.json`, `partC.conflict` keys ending `|inrole`.

## 2. Part B headline: steering the default Assistant

Turn-3 reply of each model's own R07 (`N`, `NB`) or R08 (`V`, `VB`) default conversation, 160 main scripts per condition. f / c by R04's regexes on the turn-3 reply; voice = mean `assistant_voice` (0-3); fluent and decline = Haiku labels. Contrasts paired by script, bootstrap 95% over the 160 scripts (2,000 resamples, seed 0), percentage points.

### `N` (s = 0.1; s x n32 = 7.30)

| Condition | n | f | c | a (pp) | f + c | voice | fluent | declines | tokens | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 160 | 29.4% (47/160) | 10.0% (16/160) | +19.4 | 39.4% | 2.76 | 94.4% | 34.4% | 369 | 27 |
| +v_formal | 160 | 33.1% (53/160) | 5.0% (8/160) | +28.1 | 38.1% | 2.92 | 90.6% | 37.7% | 368 | 32 |
| -v_formal | 160 | 32.5% (52/160) | 23.1% (37/160) | +9.4 | 55.6% | 2.45 | 86.2% | 30.6% | 375 | 32 |
| +v_formal_perp | 160 | 32.5% (52/160) | 6.2% (10/160) | +26.2 | 38.8% | 2.88 | 93.1% | 40.9% | 365 | 29 |
| -v_formal_perp | 160 | 35.6% (57/160) | 15.6% (25/160) | +20.0 | 51.2% | 2.54 | 88.8% | 28.7% | 372 | 34 |
| +v_axis | 160 | 28.1% (45/160) | 6.2% (10/160) | +21.9 | 34.4% | 2.87 | 93.8% | 33.8% | 336 | 11 |
| -v_axis | 160 | 28.7% (46/160) | 10.0% (16/160) | +18.8 | 38.8% | 2.67 | 81.2% | 38.1% | 392 | 49 |
| +v_axis_perp | 160 | 25.6% (41/160) | 8.8% (14/160) | +16.9 | 34.4% | 2.81 | 96.2% | 30.6% | 340 | 18 |
| -v_axis_perp | 160 | 31.2% (50/160) | 7.5% (12/160) | +23.8 | 38.8% | 2.71 | 85.0% | 38.1% | 393 | 53 |
| +v_rand | 160 | 32.5% (52/160) | 8.8% (14/160) | +23.8 | 41.2% | 2.75 | 93.8% | 36.9% | 361 | 26 |
| -v_rand | 160 | 29.4% (47/160) | 10.0% (16/160) | +19.4 | 39.4% | 2.77 | 94.4% | 35.0% | 370 | 27 |

| Direction | which animal a(+v) - a(-v) | how often (f+c)(+v) - (f+c)(none) | how often (f+c)(-v) - (f+c)(none) |
|---|---|---|---|
| v_formal | +18.8 [+7.5, +30.0] | -1.3 [-8.1, +6.2] | +16.3 [+8.8, +23.8] |
| v_formal_perp | +6.2 [-1.9, +14.4] | -0.6 [-7.5, +7.5] | +11.9 [+3.1, +20.6] |
| v_axis | +3.1 [-3.8, +10.0] | -5.0 [-12.5, +2.5] | -0.6 [-7.5, +6.2] |
| v_axis_perp | -6.9 [-13.8, +0.0] | -5.0 [-11.2, +1.9] | -0.6 [-8.7, +8.1] |
| v_rand | +4.4 [-3.7, +12.5] | +1.9 [-5.6, +8.8] | +0.0 [-7.5, +7.5] |

### `V` (s = 0.05; s x n32 = 3.65)

| Condition | n | f | c | a (pp) | f + c | voice | fluent | declines | tokens | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 160 | 30.0% (48/160) | 11.9% (19/160) | +18.1 | 41.9% | 2.76 | 87.5% | 0.0% | 413 | 46 |
| +v_formal | 160 | 24.4% (39/160) | 8.1% (13/160) | +16.2 | 32.5% | 2.89 | 91.2% | 0.0% | 408 | 40 |
| -v_formal | 160 | 30.6% (49/160) | 17.5% (28/160) | +13.1 | 48.1% | 2.60 | 81.2% | 0.0% | 422 | 53 |
| +v_formal_perp | 160 | 18.1% (29/160) | 8.1% (13/160) | +10.0 | 26.2% | 2.86 | 88.1% | 0.0% | 415 | 44 |
| -v_formal_perp | 160 | 31.2% (50/160) | 25.0% (40/160) | +6.2 | 56.2% | 2.63 | 86.2% | 0.0% | 424 | 58 |
| +v_axis | 160 | 26.9% (43/160) | 8.8% (14/160) | +18.1 | 35.6% | 2.84 | 88.8% | 0.0% | 406 | 38 |
| -v_axis | 160 | 29.4% (47/160) | 14.4% (23/160) | +15.0 | 43.8% | 2.69 | 85.6% | 0.0% | 432 | 57 |
| +v_axis_perp | 160 | 28.7% (46/160) | 10.6% (17/160) | +18.1 | 39.4% | 2.82 | 90.6% | 0.0% | 406 | 32 |
| -v_axis_perp | 160 | 28.1% (45/160) | 12.5% (20/160) | +15.6 | 40.6% | 2.74 | 90.0% | 0.0% | 427 | 52 |
| +v_rand | 160 | 23.8% (38/160) | 11.2% (18/160) | +12.5 | 35.0% | 2.79 | 88.8% | 0.0% | 416 | 47 |
| -v_rand | 160 | 28.7% (46/160) | 13.1% (21/160) | +15.6 | 41.9% | 2.77 | 89.4% | 0.0% | 417 | 43 |

| Direction | which animal a(+v) - a(-v) | how often (f+c)(+v) - (f+c)(none) | how often (f+c)(-v) - (f+c)(none) |
|---|---|---|---|
| v_formal | +3.1 [-8.1, +15.0] | -9.4 [-16.9, -1.3] | +6.2 [-2.5, +15.0] |
| v_formal_perp | +3.8 [-6.9, +15.0] | -15.6 [-23.7, -7.5] | +14.4 [+6.2, +22.5] |
| v_axis | +3.1 [-6.2, +12.5] | -6.2 [-15.0, +1.9] | +1.9 [-6.2, +10.0] |
| v_axis_perp | +2.5 [-8.1, +12.5] | -2.5 [-10.6, +5.6] | -1.3 [-9.4, +6.9] |
| v_rand | -3.1 [-12.5, +6.9] | -6.9 [-14.4, +0.6] | +0.0 [-8.1, +8.1] |

### `NB` (s = 0.1; s x n32 = 7.30)

| Condition | n | f | c | a (pp) | f + c | voice | fluent | declines | tokens | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 160 | 18.8% (30/160) | 12.5% (20/160) | +6.2 | 31.2% | 2.73 | 95.6% | 29.4% | 370 | 25 |
| +v_formal | 160 | 19.4% (31/160) | 10.6% (17/160) | +8.8 | 30.0% | 2.88 | 95.6% | 33.8% | 365 | 24 |
| -v_formal | 160 | 18.8% (30/160) | 26.9% (43/160) | -8.1 | 45.6% | 2.33 | 85.6% | 22.5% | 371 | 36 |
| +v_formal_perp | 160 | 20.6% (33/160) | 7.5% (12/160) | +13.1 | 28.1% | 2.84 | 93.8% | 35.6% | 365 | 29 |
| -v_formal_perp | 160 | 14.4% (23/160) | 33.8% (54/160) | -19.4 | 48.1% | 2.41 | 88.1% | 23.8% | 374 | 53 |
| +v_axis | 160 | 18.1% (29/160) | 9.4% (15/160) | +8.8 | 27.5% | 2.76 | 96.9% | 30.0% | 348 | 16 |
| -v_axis | 160 | 20.6% (33/160) | 16.9% (27/160) | +3.8 | 37.5% | 2.54 | 81.9% | 33.1% | 405 | 57 |
| +v_axis_perp | 160 | 16.2% (26/160) | 13.1% (21/160) | +3.1 | 29.4% | 2.76 | 95.0% | 28.1% | 342 | 18 |
| -v_axis_perp | 160 | 22.5% (36/160) | 13.8% (22/160) | +8.8 | 36.2% | 2.62 | 87.5% | 30.6% | 398 | 52 |
| +v_rand | 160 | 18.1% (29/160) | 13.1% (21/160) | +5.0 | 31.2% | 2.69 | 94.4% | 28.7% | 372 | 30 |
| -v_rand | 160 | 18.8% (30/160) | 15.0% (24/160) | +3.8 | 33.8% | 2.69 | 94.4% | 30.6% | 369 | 31 |

| Direction | which animal a(+v) - a(-v) | how often (f+c)(+v) - (f+c)(none) | how often (f+c)(-v) - (f+c)(none) |
|---|---|---|---|
| v_formal | +16.9 [+6.9, +27.5] | -1.3 [-8.8, +6.2] | +14.4 [+6.2, +22.5] |
| v_formal_perp | +32.5 [+22.5, +42.5] | -3.1 [-10.6, +4.4] | +16.9 [+8.7, +24.4] |
| v_axis | +5.0 [-4.4, +14.4] | -3.7 [-11.9, +3.8] | +6.2 [-1.3, +13.8] |
| v_axis_perp | -5.6 [-15.0, +3.8] | -1.9 [-8.8, +5.0] | +5.0 [-2.5, +11.9] |
| v_rand | +1.3 [-7.5, +10.0] | +0.0 [-8.8, +8.1] | +2.5 [-5.6, +10.0] |

### `VB` (s = 0.05; s x n32 = 3.65)

| Condition | n | f | c | a (pp) | f + c | voice | fluent | declines | tokens | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|
| none | 160 | 8.8% (14/160) | 2.5% (4/160) | +6.2 | 11.2% | 2.68 | 91.9% | 0.0% | 384 | 34 |
| +v_formal | 160 | 8.1% (13/160) | 1.9% (3/160) | +6.2 | 10.0% | 2.77 | 93.1% | 0.0% | 391 | 35 |
| -v_formal | 160 | 11.9% (19/160) | 8.8% (14/160) | +3.1 | 20.6% | 2.49 | 91.9% | 0.0% | 374 | 27 |
| +v_formal_perp | 160 | 10.6% (17/160) | 1.9% (3/160) | +8.8 | 12.5% | 2.74 | 95.0% | 0.0% | 391 | 31 |
| -v_formal_perp | 160 | 11.2% (18/160) | 9.4% (15/160) | +1.9 | 20.6% | 2.53 | 91.9% | 0.0% | 380 | 30 |
| +v_axis | 160 | 11.2% (18/160) | 1.9% (3/160) | +9.4 | 13.1% | 2.74 | 94.4% | 0.0% | 372 | 26 |
| -v_axis | 160 | 11.9% (19/160) | 2.5% (4/160) | +9.4 | 14.4% | 2.62 | 92.5% | 0.0% | 409 | 48 |
| +v_axis_perp | 160 | 10.0% (16/160) | 1.9% (3/160) | +8.1 | 11.9% | 2.69 | 96.9% | 0.0% | 358 | 20 |
| -v_axis_perp | 160 | 8.8% (14/160) | 5.6% (9/160) | +3.1 | 14.4% | 2.65 | 88.8% | 0.0% | 402 | 48 |
| +v_rand | 160 | 8.8% (14/160) | 3.1% (5/160) | +5.6 | 11.9% | 2.66 | 95.6% | 0.0% | 387 | 35 |
| -v_rand | 160 | 16.2% (26/160) | 3.1% (5/160) | +13.1 | 19.4% | 2.66 | 91.2% | 0.0% | 380 | 30 |

| Direction | which animal a(+v) - a(-v) | how often (f+c)(+v) - (f+c)(none) | how often (f+c)(-v) - (f+c)(none) |
|---|---|---|---|
| v_formal | +3.1 [-3.8, +10.6] | -1.2 [-6.9, +3.8] | +9.4 [+3.8, +15.0] |
| v_formal_perp | +6.9 [-1.2, +15.6] | +1.2 [-3.1, +5.6] | +9.4 [+3.8, +15.0] |
| v_axis | +0.0 [-6.2, +6.3] | +1.9 [-3.8, +7.5] | +3.1 [-2.5, +9.4] |
| v_axis_perp | +5.0 [-1.9, +11.9] | +0.6 [-4.4, +5.6] | +3.1 [-1.3, +8.1] |
| v_rand | -7.5 [-15.0, -0.6] | +0.6 [-4.4, +5.6] | +8.1 [+1.9, +14.4] |

### Calibration (40 scripts, +/- v_formal_perp)

**`N`: s\* = 0.1** (voice target not reached). Unsteered: voice 2.80, fluent 92.5%.

| s | voice + | voice - | voice gap | fluent + | fluent - | gap >= 1.0 | fluent within 10 points |
|---|---|---|---|---|---|---|---|
| 0.05 | 2.83 | 2.70 | 0.12 | 90.0% | 100.0% | no | yes |
| 0.1 | 2.95 | 2.58 | 0.38 | 92.5% | 87.5% | no | yes |
| 0.2 | 3.00 | 1.77 | 1.23 | 95.0% | 77.5% | yes | no |
| 0.4 | 3.00 | 1.07 | 1.93 | 91.9% | 60.0% | yes | no |
| 0.8 | 3.00 | 0.12 | 2.88 | 25.8% | 15.0% | yes | no |

**`V`: s\* = 0.05** (voice target not reached). Unsteered: voice 2.80, fluent 90.0%.

| s | voice + | voice - | voice gap | fluent + | fluent - | gap >= 1.0 | fluent within 10 points |
|---|---|---|---|---|---|---|---|
| 0.05 | 2.90 | 2.70 | 0.20 | 85.0% | 90.0% | no | yes |
| 0.1 | 2.95 | 2.30 | 0.65 | 92.5% | 72.5% | no | no |
| 0.2 | 3.00 | 1.80 | 1.20 | 90.0% | 75.0% | yes | no |
| 0.4 | 3.00 | 0.90 | 2.10 | 88.2% | 60.0% | yes | no |
| 0.8 | 3.00 | 0.20 | 2.80 | 25.7% | 20.0% | yes | no |

### Unsteered vs R07/R08 turn-3 rates (keyword, turn 3 only)

| Model | R09 unsteered f / c (160 scripts) | earlier run, turn 3, same 160 scripts | earlier run, turn 3, all 200 |
|---|---|---|---|
| `N` | 29.4% / 10.0% | 31.2% / 6.9% | 31.0% / 6.5% |
| `NB` | 18.8% / 12.5% | 17.5% / 10.6% | 16.5% / 12.0% |
| `V` | 30.0% / 11.9% | 22.5% / 10.6% | 23.5% / 11.5% |
| `VB` | 8.8% / 2.5% | 8.1% / 3.1% | 8.0% / 4.0% |

## 3. Part A headline: readout before the habit

n32 = 72.969 (90602 tokens, 200 replies; mean of per-reply means 72.837). v_formal built from 100 P22 and 100 P23 parent conversations (even-indexed scripts).

**Block 32: raw norms and cosines**

| Direction | norm | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand |
|---|---|---|---|---|---|---|---|---|
| v_axis | 5.555 | +1.000 | +0.257 | -0.000 | +0.966 | +0.350 | -0.343 | -0.004 |
| v_formal | 11.502 | +0.257 | +1.000 | +0.966 | -0.000 | +0.058 | +0.011 | -0.022 |
| v_formal_perp | 11.114 | -0.000 | +0.966 | +1.000 | -0.257 | -0.033 | +0.103 | -0.021 |
| v_axis_perp | 5.367 | +0.966 | -0.000 | -0.257 | +1.000 | +0.347 | -0.358 | +0.002 |
| v_help | 17.550 | +0.350 | +0.058 | -0.033 | +0.347 | +1.000 | -0.835 | +0.006 |
| v_dis | 16.344 | -0.343 | +0.011 | +0.103 | -0.358 | -0.835 | +1.000 | -0.007 |
| v_rand | 71.126 | -0.004 | -0.022 | -0.021 | +0.002 | +0.006 | -0.007 | +1.000 |

**Block 24: raw norms and cosines**

| Direction | norm | v_axis | v_formal | v_formal_perp | v_axis_perp | v_rand |
|---|---|---|---|---|---|---|
| v_axis | 4.093 | +1.000 | +0.217 | -0.000 | +0.976 | -0.004 |
| v_formal | 9.563 | +0.217 | +1.000 | +0.976 | +0.000 | -0.013 |
| v_formal_perp | 9.336 | -0.000 | +0.976 | +1.000 | -0.217 | -0.012 |
| v_axis_perp | 3.996 | +0.976 | +0.000 | -0.217 | +1.000 | -0.001 |
| v_rand | 71.126 | -0.004 | -0.013 | -0.012 | -0.001 | +1.000 |

**Block 40: raw norms and cosines**

| Direction | norm | v_axis | v_formal | v_formal_perp | v_axis_perp | v_rand |
|---|---|---|---|---|---|---|
| v_axis | 9.251 | +1.000 | +0.195 | -0.000 | +0.981 | +0.007 |
| v_formal | 22.884 | +0.195 | +1.000 | +0.981 | -0.000 | -0.013 |
| v_formal_perp | 22.445 | -0.000 | +0.981 | +1.000 | -0.195 | -0.015 |
| v_axis_perp | 9.074 | +0.981 | -0.000 | -0.195 | +1.000 | +0.009 |
| v_rand | 71.126 | +0.007 | -0.013 | -0.015 | +0.009 | +1.000 |

### Which animal, in advance: AUC (formal character's animal vs casual's), default cell, block 32, odd scripts

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | n formal / casual animal |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.50 [0.25, 0.75] | 0.96 [0.87, 1.00] | 0.97 [0.90, 1.00] | 0.24 [0.05, 0.45] | 0.17 [0.05, 0.31] | 0.85 [0.72, 0.96] | 0.45 [0.22, 0.67] | 31 / 7 |
| `N` | p2 | 0.94 [0.82, 1.00] | 0.95 [0.88, 1.00] | 0.94 [0.86, 1.00] | 0.59 [0.42, 0.76] | 0.27 [0.09, 0.46] | 0.77 [0.61, 0.92] | 0.30 [0.10, 0.54] | 31 / 7 |
| `NB` | p1 | 0.22 [0.06, 0.41] | 0.69 [0.46, 0.91] | 0.71 [0.48, 0.92] | 0.17 [0.04, 0.33] | 0.20 [0.05, 0.37] | 0.83 [0.67, 0.95] | 0.37 [0.16, 0.60] | 19 / 13 |
| `NB` | p2 | 0.49 [0.27, 0.70] | 0.82 [0.66, 0.95] | 0.84 [0.70, 0.96] | 0.24 [0.08, 0.42] | 0.19 [0.05, 0.35] | 0.84 [0.69, 0.97] | 0.33 [0.14, 0.54] | 19 / 13 |
| `X` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 5 / 0 |
| `X` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 5 / 0 |
| `XB` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 40 / 0 |
| `XB` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 40 / 0 |
| `V` | p1 | 0.61 [0.42, 0.79] | 0.77 [0.61, 0.91] | 0.77 [0.61, 0.90] | 0.47 [0.29, 0.65] | 0.59 [0.41, 0.77] | 0.38 [0.21, 0.56] | 0.56 [0.37, 0.73] | 24 / 17 |
| `V` | p2 | 0.86 [0.72, 0.96] | 0.79 [0.65, 0.92] | 0.77 [0.61, 0.91] | 0.76 [0.61, 0.89] | 0.63 [0.45, 0.80] | 0.41 [0.23, 0.59] | 0.42 [0.24, 0.60] | 24 / 17 |
| `VB` | p1 | 0.43 [0.15, 0.73] | 0.80 [0.56, 1.00] | 0.82 [0.58, 1.00] | 0.12 [0.00, 0.32] | 0.68 [0.40, 0.93] | 0.37 [0.09, 0.68] | 0.28 [0.07, 0.56] | 12 / 5 |
| `VB` | p2 | 0.85 [0.64, 1.00] | 0.77 [0.47, 0.98] | 0.77 [0.47, 0.98] | 0.78 [0.52, 1.00] | 0.78 [0.43, 1.00] | 0.27 [0.00, 0.63] | 0.75 [0.39, 1.00] | 12 / 5 |

Pooled over each model's T 0.7 cells (mean of within-cell AUCs weighted by n; cells with fewer than 5 per side left out), block 32, odd scripts:

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | cells (n) |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.50 | 0.96 | 0.97 | 0.24 | 0.17 | 0.85 | 0.45 | P00 (n 38) |
| `N` | p2 | 0.94 | 0.95 | 0.94 | 0.59 | 0.27 | 0.77 | 0.30 | P00 (n 38) |
| `NB` | p1 | 0.22 | 0.69 | 0.71 | 0.17 | 0.20 | 0.83 | 0.37 | P00 (n 32) |
| `NB` | p2 | 0.49 | 0.82 | 0.84 | 0.24 | 0.19 | 0.84 | 0.33 | P00 (n 32) |
| `X` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `X` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `XB` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `XB` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `V` | p1 | 0.61 | 0.77 | 0.77 | 0.47 | 0.59 | 0.38 | 0.56 | P00 (n 41) |
| `V` | p2 | 0.86 | 0.79 | 0.77 | 0.76 | 0.63 | 0.41 | 0.42 | P00 (n 41) |
| `VB` | p1 | 0.43 | 0.80 | 0.82 | 0.12 | 0.68 | 0.37 | 0.28 | P00 (n 17) |
| `VB` | p2 | 0.85 | 0.77 | 0.77 | 0.78 | 0.78 | 0.27 | 0.75 | P00 (n 17) |

### How often: AUC (any habit vs none), default cell, block 32, odd scripts

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | n habit / none |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.41 [0.30, 0.53] | 0.45 [0.34, 0.56] | 0.46 [0.36, 0.58] | 0.43 [0.32, 0.56] | 0.44 [0.33, 0.56] | 0.60 [0.49, 0.71] | 0.48 [0.37, 0.61] | 38 / 62 |
| `N` | p2 | 0.41 [0.30, 0.53] | 0.59 [0.48, 0.70] | 0.62 [0.50, 0.72] | 0.27 [0.18, 0.38] | 0.29 [0.19, 0.40] | 0.70 [0.60, 0.80] | 0.56 [0.43, 0.68] | 38 / 62 |
| `NB` | p1 | 0.43 [0.31, 0.56] | 0.55 [0.43, 0.68] | 0.56 [0.43, 0.69] | 0.41 [0.28, 0.55] | 0.49 [0.37, 0.60] | 0.53 [0.42, 0.65] | 0.59 [0.46, 0.71] | 32 / 68 |
| `NB` | p2 | 0.56 [0.43, 0.68] | 0.59 [0.48, 0.70] | 0.60 [0.49, 0.71] | 0.47 [0.33, 0.60] | 0.43 [0.31, 0.54] | 0.58 [0.47, 0.70] | 0.52 [0.39, 0.64] | 32 / 68 |
| `X` | p1 | 0.55 [0.30, 0.86] | 0.31 [0.13, 0.54] | 0.31 [0.12, 0.55] | 0.63 [0.36, 0.93] | 0.71 [0.50, 0.89] | 0.33 [0.15, 0.53] | 0.72 [0.60, 0.83] | 5 / 95 |
| `X` | p2 | 0.51 [0.31, 0.73] | 0.49 [0.31, 0.71] | 0.51 [0.33, 0.71] | 0.53 [0.34, 0.71] | 0.48 [0.31, 0.67] | 0.56 [0.41, 0.70] | 0.60 [0.48, 0.71] | 5 / 95 |
| `XB` | p1 | 0.40 [0.29, 0.51] | 0.30 [0.21, 0.42] | 0.32 [0.22, 0.44] | 0.51 [0.39, 0.62] | 0.53 [0.41, 0.66] | 0.53 [0.41, 0.65] | 0.43 [0.31, 0.54] | 40 / 60 |
| `XB` | p2 | 0.36 [0.25, 0.46] | 0.48 [0.37, 0.60] | 0.50 [0.38, 0.62] | 0.32 [0.22, 0.43] | 0.43 [0.31, 0.55] | 0.56 [0.44, 0.68] | 0.62 [0.51, 0.73] | 40 / 60 |
| `V` | p1 | 0.39 [0.28, 0.51] | 0.33 [0.22, 0.45] | 0.33 [0.23, 0.45] | 0.51 [0.40, 0.63] | 0.49 [0.37, 0.61] | 0.57 [0.45, 0.68] | 0.43 [0.32, 0.54] | 41 / 59 |
| `V` | p2 | 0.36 [0.25, 0.48] | 0.37 [0.27, 0.49] | 0.38 [0.27, 0.49] | 0.38 [0.26, 0.50] | 0.46 [0.35, 0.58] | 0.54 [0.42, 0.65] | 0.52 [0.40, 0.63] | 41 / 59 |
| `VB` | p1 | 0.31 [0.17, 0.45] | 0.37 [0.22, 0.53] | 0.38 [0.23, 0.54] | 0.41 [0.26, 0.56] | 0.38 [0.24, 0.52] | 0.67 [0.54, 0.81] | 0.36 [0.22, 0.50] | 17 / 83 |
| `VB` | p2 | 0.30 [0.18, 0.44] | 0.31 [0.19, 0.44] | 0.32 [0.19, 0.45] | 0.34 [0.22, 0.47] | 0.42 [0.29, 0.55] | 0.56 [0.41, 0.70] | 0.57 [0.41, 0.73] | 17 / 83 |

### Which animal, in advance: AUC (formal character's animal vs casual's), default cell, block 32, all scripts

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | n formal / casual animal |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.57 [0.38, 0.75] | 0.92 [0.82, 0.99] | 0.93 [0.83, 0.99] | 0.29 [0.16, 0.43] | 0.18 [0.09, 0.28] | 0.82 [0.72, 0.91] | 0.46 [0.30, 0.61] | 65 / 13 |
| `N` | p2 | 0.90 [0.79, 0.99] | 0.93 [0.86, 0.98] | 0.92 [0.85, 0.98] | 0.60 [0.45, 0.75] | 0.38 [0.21, 0.55] | 0.68 [0.52, 0.83] | 0.30 [0.17, 0.45] | 65 / 13 |
| `NB` | p1 | 0.21 [0.10, 0.33] | 0.73 [0.58, 0.87] | 0.76 [0.61, 0.89] | 0.16 [0.07, 0.27] | 0.18 [0.09, 0.30] | 0.84 [0.74, 0.93] | 0.40 [0.25, 0.57] | 38 / 24 |
| `NB` | p2 | 0.57 [0.41, 0.72] | 0.85 [0.74, 0.94] | 0.86 [0.76, 0.94] | 0.29 [0.16, 0.43] | 0.18 [0.08, 0.29] | 0.84 [0.73, 0.93] | 0.26 [0.14, 0.39] | 38 / 24 |
| `X` | p1 | 0.91 [0.63, 1.00] | 0.47 [0.00, 1.00] | 0.41 [0.00, 0.96] | 0.88 [0.60, 1.00] | 0.88 [0.54, 1.00] | 0.09 [0.00, 0.37] | 0.97 [0.83, 1.00] | 8 / 4 |
| `X` | p2 | 0.84 [0.44, 1.00] | 0.69 [0.33, 1.00] | 0.62 [0.26, 0.96] | 0.84 [0.45, 1.00] | 0.50 [0.09, 1.00] | 0.59 [0.14, 1.00] | 0.19 [0.00, 0.66] | 8 / 4 |
| `XB` | p1 | 0.09 [0.00, 0.22] | 0.47 [0.35, 0.58] | 0.55 [0.44, 0.66] | 0.11 [0.01, 0.25] | 0.14 [0.00, 0.31] | 0.95 [0.89, 0.99] | 0.66 [0.28, 0.99] | 76 / 2 |
| `XB` | p2 | 0.56 [0.44, 0.68] | 0.75 [0.54, 0.92] | 0.76 [0.53, 0.96] | 0.44 [0.25, 0.65] | 0.51 [0.37, 0.64] | 0.51 [0.39, 0.62] | 0.61 [0.29, 0.91] | 76 / 2 |
| `V` | p1 | 0.58 [0.44, 0.72] | 0.78 [0.66, 0.88] | 0.78 [0.67, 0.89] | 0.40 [0.27, 0.53] | 0.60 [0.46, 0.73] | 0.38 [0.24, 0.51] | 0.51 [0.37, 0.65] | 50 / 26 |
| `V` | p2 | 0.79 [0.67, 0.89] | 0.78 [0.67, 0.88] | 0.76 [0.65, 0.87] | 0.69 [0.56, 0.82] | 0.67 [0.54, 0.78] | 0.39 [0.27, 0.52] | 0.55 [0.41, 0.69] | 50 / 26 |
| `VB` | p1 | 0.43 [0.22, 0.64] | 0.65 [0.42, 0.86] | 0.66 [0.42, 0.87] | 0.25 [0.07, 0.45] | 0.53 [0.30, 0.75] | 0.49 [0.27, 0.71] | 0.35 [0.15, 0.58] | 18 / 10 |
| `VB` | p2 | 0.67 [0.43, 0.88] | 0.62 [0.38, 0.83] | 0.61 [0.38, 0.83] | 0.65 [0.41, 0.86] | 0.71 [0.46, 0.92] | 0.29 [0.08, 0.55] | 0.77 [0.54, 0.95] | 18 / 10 |

Pooled over each model's T 0.7 cells (mean of within-cell AUCs weighted by n; cells with fewer than 5 per side left out), block 32, all scripts:

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | cells (n) |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.57 | 0.92 | 0.93 | 0.29 | 0.18 | 0.82 | 0.46 | P00 (n 78) |
| `N` | p2 | 0.90 | 0.93 | 0.92 | 0.60 | 0.38 | 0.68 | 0.30 | P00 (n 78) |
| `NB` | p1 | 0.38 | 0.43 | 0.45 | 0.40 | 0.47 | 0.54 | 0.38 | P00, P06 (n 127) |
| `NB` | p2 | 0.59 | 0.62 | 0.61 | 0.47 | 0.41 | 0.60 | 0.34 | P00, P06 (n 127) |
| `X` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `X` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `XB` | p1 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `XB` | p2 | n/a | n/a | n/a | n/a | n/a | n/a | n/a |  (n 0) |
| `V` | p1 | 0.58 | 0.78 | 0.78 | 0.40 | 0.60 | 0.38 | 0.51 | P00 (n 76) |
| `V` | p2 | 0.79 | 0.78 | 0.76 | 0.69 | 0.67 | 0.39 | 0.55 | P00 (n 76) |
| `VB` | p1 | 0.43 | 0.65 | 0.66 | 0.25 | 0.53 | 0.49 | 0.35 | P00 (n 28) |
| `VB` | p2 | 0.67 | 0.62 | 0.61 | 0.65 | 0.71 | 0.29 | 0.77 | P00 (n 28) |

### How often: AUC (any habit vs none), default cell, block 32, all scripts

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | n habit / none |
|---|---|---|---|---|---|---|---|---|---|
| `N` | p1 | 0.35 [0.27, 0.42] | 0.49 [0.40, 0.56] | 0.50 [0.42, 0.58] | 0.37 [0.30, 0.45] | 0.39 [0.32, 0.47] | 0.65 [0.57, 0.72] | 0.44 [0.36, 0.52] | 78 / 122 |
| `N` | p2 | 0.42 [0.34, 0.50] | 0.62 [0.54, 0.70] | 0.64 [0.56, 0.71] | 0.27 [0.20, 0.34] | 0.27 [0.21, 0.34] | 0.72 [0.64, 0.78] | 0.52 [0.43, 0.60] | 78 / 122 |
| `NB` | p1 | 0.37 [0.29, 0.45] | 0.50 [0.42, 0.59] | 0.52 [0.43, 0.61] | 0.38 [0.29, 0.46] | 0.47 [0.38, 0.56] | 0.57 [0.48, 0.65] | 0.58 [0.48, 0.66] | 62 / 138 |
| `NB` | p2 | 0.54 [0.45, 0.62] | 0.64 [0.56, 0.71] | 0.64 [0.56, 0.72] | 0.39 [0.31, 0.48] | 0.36 [0.29, 0.44] | 0.64 [0.56, 0.72] | 0.48 [0.39, 0.57] | 62 / 138 |
| `X` | p1 | 0.51 [0.32, 0.72] | 0.35 [0.18, 0.53] | 0.35 [0.17, 0.53] | 0.57 [0.37, 0.78] | 0.59 [0.38, 0.78] | 0.44 [0.26, 0.64] | 0.59 [0.42, 0.75] | 12 / 188 |
| `X` | p2 | 0.42 [0.25, 0.58] | 0.40 [0.27, 0.54] | 0.42 [0.29, 0.56] | 0.46 [0.30, 0.62] | 0.48 [0.32, 0.63] | 0.53 [0.37, 0.69] | 0.57 [0.41, 0.72] | 12 / 188 |
| `XB` | p1 | 0.36 [0.28, 0.44] | 0.29 [0.21, 0.36] | 0.31 [0.24, 0.38] | 0.48 [0.39, 0.56] | 0.55 [0.47, 0.64] | 0.53 [0.45, 0.61] | 0.44 [0.36, 0.51] | 78 / 122 |
| `XB` | p2 | 0.38 [0.31, 0.47] | 0.51 [0.43, 0.60] | 0.53 [0.45, 0.62] | 0.34 [0.26, 0.42] | 0.38 [0.29, 0.46] | 0.62 [0.53, 0.70] | 0.56 [0.48, 0.64] | 78 / 122 |
| `V` | p1 | 0.40 [0.32, 0.49] | 0.32 [0.25, 0.40] | 0.33 [0.25, 0.41] | 0.52 [0.43, 0.60] | 0.50 [0.42, 0.59] | 0.55 [0.47, 0.64] | 0.50 [0.42, 0.58] | 76 / 124 |
| `V` | p2 | 0.36 [0.29, 0.45] | 0.41 [0.32, 0.50] | 0.42 [0.33, 0.51] | 0.36 [0.29, 0.45] | 0.42 [0.34, 0.50] | 0.59 [0.50, 0.67] | 0.49 [0.41, 0.57] | 76 / 124 |
| `VB` | p1 | 0.26 [0.17, 0.36] | 0.34 [0.22, 0.47] | 0.36 [0.24, 0.48] | 0.36 [0.26, 0.46] | 0.42 [0.31, 0.54] | 0.64 [0.53, 0.74] | 0.34 [0.24, 0.46] | 28 / 172 |
| `VB` | p2 | 0.28 [0.18, 0.39] | 0.38 [0.27, 0.49] | 0.40 [0.29, 0.50] | 0.29 [0.20, 0.40] | 0.37 [0.27, 0.48] | 0.61 [0.49, 0.72] | 0.54 [0.42, 0.67] | 28 / 172 |

### Decline mode (turn-1 reply, defaults of `N`, `NB`, `X`, `XB`)

AUC of each p2 projection (block 32) for declines vs helps:

| Model | Scripts | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand | n declines / helps |
|---|---|---|---|---|---|---|---|---|---|
| `N` | odd | 0.68 [0.57, 0.78] | 0.94 [0.89, 0.98] | 0.94 [0.90, 0.98] | 0.21 [0.12, 0.31] | 0.07 [0.03, 0.12] | 0.95 [0.90, 0.98] | 0.18 [0.10, 0.28] | 33 / 67 |
| `N` | all | 0.65 [0.57, 0.73] | 0.95 [0.93, 0.98] | 0.96 [0.93, 0.98] | 0.19 [0.13, 0.26] | 0.06 [0.03, 0.10] | 0.95 [0.93, 0.98] | 0.19 [0.13, 0.26] | 70 / 130 |
| `NB` | odd | 0.69 [0.59, 0.79] | 0.99 [0.96, 1.00] | 0.99 [0.97, 1.00] | 0.21 [0.13, 0.30] | 0.03 [0.01, 0.06] | 0.98 [0.96, 1.00] | 0.16 [0.09, 0.24] | 35 / 65 |
| `NB` | all | 0.68 [0.60, 0.75] | 0.98 [0.97, 1.00] | 0.99 [0.97, 1.00] | 0.18 [0.13, 0.24] | 0.04 [0.02, 0.07] | 0.97 [0.95, 0.99] | 0.19 [0.13, 0.25] | 70 / 130 |
| `X` | odd | 0.53 [0.43, 0.62] | 0.92 [0.86, 0.97] | 0.93 [0.88, 0.97] | 0.16 [0.09, 0.23] | 0.01 [0.00, 0.03] | 1.00 [1.00, 1.00] | 0.03 [0.00, 0.06] | 1 / 99 |
| `X` | all | 0.27 [0.00, 0.58] | 0.69 [0.39, 0.96] | 0.78 [0.59, 0.96] | 0.09 [0.00, 0.23] | 0.01 [0.00, 0.02] | 1.00 [1.00, 1.00] | 0.23 [0.02, 0.47] | 2 / 198 |
| `XB` | odd | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0 / 100 |
| `XB` | all | 0.06 [0.03, 0.10] | 0.62 [0.56, 0.69] | 0.74 [0.68, 0.81] | 0.01 [0.00, 0.03] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 0.50 [0.43, 0.56] | 1 / 199 |

f and c split by the turn-1 decline label (judge; keyword):

| Model | Turn-1 mode | n | f, judge | c, judge | f, keyword | c, keyword |
|---|---|---|---|---|---|---|
| `N` | declines | 70 | 54.3% (38) | 0.0% (0) | 54.3% | 0.0% |
| `N` | helps | 130 | 20.8% (27) | 10.0% (13) | 20.8% | 10.8% |
| `NB` | declines | 70 | 37.1% (26) | 2.9% (2) | 38.6% | 2.9% |
| `NB` | helps | 130 | 9.2% (12) | 16.9% (22) | 9.2% | 17.7% |
| `X` | declines | 2 | 0.0% (0) | 50.0% (1) | 0.0% | 50.0% |
| `X` | helps | 198 | 4.0% (8) | 1.5% (3) | 4.5% | 1.5% |
| `XB` | declines | 1 | 100.0% (1) | 0.0% (0) | 100.0% | 0.0% |
| `XB` | helps | 199 | 37.7% (75) | 1.0% (2) | 38.2% | 1.5% |

### Cell means of the projections, block 32 (odd scripts; bootstrap 95% over scripts)

**p1**

| Model | Cell | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand |
|---|---|---|---|---|---|---|---|---|
| `N` | P00 | 6.89 [6.83, 6.94] | 13.58 [13.43, 13.72] | 12.21 [12.07, 12.36] | 3.51 [3.45, 3.58] | -2.30 [-2.45, -2.15] | 0.84 [0.69, 1.01] | -0.14 [-0.16, -0.11] |
| `N` | P06 | 6.31 [6.27, 6.34] | 15.33 [15.27, 15.38] | 14.18 [14.13, 14.23] | 2.45 [2.41, 2.48] | -3.22 [-3.27, -3.17] | 1.89 [1.85, 1.94] | -0.35 [-0.36, -0.33] |
| `N` | P07 | 4.79 [4.76, 4.82] | 10.14 [10.09, 10.19] | 9.22 [9.17, 9.27] | 2.26 [2.22, 2.29] | -2.79 [-2.83, -2.74] | 1.42 [1.37, 1.47] | -0.20 [-0.22, -0.18] |
| `NB` | P00 | 6.81 [6.75, 6.86] | 13.79 [13.67, 13.91] | 12.46 [12.34, 12.58] | 3.37 [3.31, 3.43] | -2.16 [-2.29, -2.04] | 0.60 [0.48, 0.73] | -0.18 [-0.20, -0.15] |
| `NB` | P06 | 6.00 [5.96, 6.03] | 14.87 [14.82, 14.92] | 13.79 [13.74, 13.84] | 2.24 [2.21, 2.28] | -3.10 [-3.16, -3.05] | 1.63 [1.58, 1.68] | -0.37 [-0.38, -0.35] |
| `NB` | P07 | 5.20 [5.17, 5.23] | 10.97 [10.93, 11.02] | 9.97 [9.93, 10.01] | 2.46 [2.43, 2.48] | -2.44 [-2.49, -2.40] | 0.95 [0.91, 1.00] | -0.17 [-0.19, -0.15] |
| `V` | P00 | 6.93 [6.89, 6.98] | 13.29 [13.16, 13.41] | 11.90 [11.77, 12.03] | 3.64 [3.58, 3.69] | -1.93 [-1.99, -1.88] | 0.71 [0.64, 0.77] | -0.08 [-0.10, -0.06] |
| `V` | P07 | 4.56 [4.53, 4.59] | 9.98 [9.93, 10.03] | 9.12 [9.07, 9.16] | 2.06 [2.03, 2.08] | -3.30 [-3.33, -3.26] | 2.20 [2.16, 2.24] | -0.17 [-0.18, -0.15] |
| `V` | P09 | 6.09 [6.06, 6.12] | 14.90 [14.85, 14.94] | 13.79 [13.75, 13.84] | 2.34 [2.30, 2.37] | -2.08 [-2.11, -2.05] | 1.40 [1.36, 1.44] | -0.15 [-0.16, -0.13] |
| `V` | P22 | 6.08 [6.04, 6.11] | 15.11 [15.06, 15.16] | 14.02 [13.97, 14.07] | 2.26 [2.23, 2.30] | -2.42 [-2.46, -2.38] | 1.59 [1.55, 1.63] | -0.18 [-0.20, -0.17] |
| `V` | P23 | 4.30 [4.26, 4.33] | 7.76 [7.71, 7.81] | 6.88 [6.83, 6.94] | 2.38 [2.35, 2.41] | -4.37 [-4.42, -4.32] | 2.95 [2.91, 3.00] | -0.01 [-0.03, 0.01] |
| `VB` | P00 | 6.77 [6.72, 6.83] | 13.03 [12.89, 13.16] | 11.68 [11.54, 11.81] | 3.54 [3.48, 3.60] | -2.02 [-2.07, -1.96] | 0.73 [0.67, 0.79] | -0.09 [-0.11, -0.06] |
| `VB` | P07 | 4.52 [4.49, 4.55] | 9.86 [9.81, 9.91] | 9.00 [8.95, 9.05] | 2.05 [2.02, 2.08] | -3.16 [-3.20, -3.12] | 2.00 [1.95, 2.04] | -0.17 [-0.18, -0.15] |
| `VB` | P09 | 6.09 [6.06, 6.12] | 14.77 [14.71, 14.82] | 13.66 [13.60, 13.71] | 2.37 [2.33, 2.40] | -2.10 [-2.14, -2.06] | 1.34 [1.30, 1.39] | -0.20 [-0.21, -0.18] |
| `VB` | P22 | 6.09 [6.06, 6.13] | 14.96 [14.90, 15.02] | 13.86 [13.80, 13.92] | 2.32 [2.29, 2.35] | -2.38 [-2.41, -2.35] | 1.52 [1.48, 1.56] | -0.24 [-0.25, -0.22] |
| `VB` | P23 | 4.31 [4.27, 4.35] | 7.72 [7.66, 7.78] | 6.84 [6.78, 6.90] | 2.41 [2.37, 2.44] | -4.12 [-4.17, -4.07] | 2.71 [2.67, 2.76] | -0.00 [-0.02, 0.01] |
| `X` | P00 | 7.08 [7.04, 7.13] | 13.62 [13.54, 13.70] | 12.21 [12.12, 12.29] | 3.70 [3.65, 3.75] | -1.98 [-2.04, -1.91] | 0.70 [0.63, 0.77] | -0.19 [-0.21, -0.17] |
| `X` | P09 | 6.13 [6.10, 6.16] | 15.24 [15.20, 15.29] | 14.14 [14.10, 14.18] | 2.28 [2.25, 2.31] | -2.19 [-2.22, -2.15] | 1.44 [1.40, 1.48] | -0.16 [-0.17, -0.14] |
| `X` | P21 | 4.35 [4.32, 4.38] | 10.20 [10.16, 10.25] | 9.40 [9.35, 9.45] | 1.78 [1.75, 1.81] | -4.80 [-4.85, -4.74] | 3.35 [3.29, 3.40] | -0.26 [-0.28, -0.25] |
| `XB` | P00 | 6.67 [6.63, 6.72] | 13.14 [13.06, 13.22] | 11.82 [11.74, 11.91] | 3.40 [3.36, 3.45] | -1.84 [-1.89, -1.79] | 0.60 [0.55, 0.65] | -0.13 [-0.15, -0.11] |
| `XB` | P09 | 6.05 [6.02, 6.08] | 14.55 [14.49, 14.61] | 13.45 [13.39, 13.51] | 2.38 [2.35, 2.41] | -1.91 [-1.94, -1.88] | 1.13 [1.10, 1.17] | -0.12 [-0.14, -0.11] |
| `XB` | P21 | 4.41 [4.38, 4.44] | 10.27 [10.22, 10.31] | 9.45 [9.40, 9.50] | 1.83 [1.80, 1.85] | -4.29 [-4.34, -4.24] | 2.80 [2.75, 2.84] | -0.29 [-0.30, -0.27] |
| `parent` | P00 | 6.80 [6.70, 6.88] | 11.26 [11.18, 11.33] | 9.84 [9.76, 9.92] | 4.03 [3.93, 4.12] | -1.10 [-1.19, -1.02] | -0.07 [-0.16, 0.02] | -0.18 [-0.22, -0.14] |
| `parent` | P22 | 4.71 [4.67, 4.75] | 15.41 [15.35, 15.47] | 14.69 [14.63, 14.75] | 0.77 [0.73, 0.81] | -4.44 [-4.49, -4.39] | 3.93 [3.88, 3.98] | -0.54 [-0.56, -0.52] |
| `parent` | P23 | 2.38 [2.35, 2.41] | 3.73 [3.67, 3.79] | 3.22 [3.16, 3.28] | 1.47 [1.44, 1.51] | -6.84 [-6.92, -6.77] | 5.61 [5.54, 5.69] | -0.17 [-0.19, -0.16] |

**p2**

| Model | Cell | v_axis | v_formal | v_formal_perp | v_axis_perp | v_help | v_dis | v_rand |
|---|---|---|---|---|---|---|---|---|
| `N` | P00 | 10.05 [9.85, 10.26] | 12.33 [11.58, 13.13] | 10.08 [9.34, 10.86] | 7.12 [6.95, 7.28] | 3.52 [3.17, 3.87] | -4.61 [-5.08, -4.12] | -0.41 [-0.44, -0.38] |
| `N` | P06 | 10.19 [10.11, 10.26] | 19.90 [19.77, 20.02] | 17.88 [17.75, 18.00] | 5.24 [5.17, 5.31] | -0.12 [-0.25, 0.01] | 0.76 [0.60, 0.91] | -0.63 [-0.64, -0.61] |
| `N` | P07 | 6.31 [6.20, 6.42] | 6.07 [5.88, 6.26] | 4.60 [4.41, 4.79] | 4.92 [4.81, 5.01] | 3.00 [2.83, 3.16] | -4.58 [-4.77, -4.38] | -0.32 [-0.33, -0.30] |
| `NB` | P00 | 9.70 [9.46, 9.93] | 12.35 [11.60, 13.16] | 10.20 [9.46, 10.98] | 6.75 [6.57, 6.92] | 3.18 [2.85, 3.51] | -4.33 [-4.78, -3.86] | -0.42 [-0.44, -0.39] |
| `NB` | P06 | 9.82 [9.75, 9.89] | 19.42 [19.27, 19.56] | 17.48 [17.34, 17.62] | 4.99 [4.91, 5.07] | -0.08 [-0.26, 0.09] | 0.61 [0.38, 0.83] | -0.64 [-0.65, -0.62] |
| `NB` | P07 | 6.25 [6.10, 6.41] | 6.38 [6.11, 6.65] | 4.94 [4.68, 5.19] | 4.77 [4.64, 4.90] | 2.64 [2.45, 2.82] | -4.33 [-4.55, -4.10] | -0.34 [-0.36, -0.32] |
| `V` | P00 | 9.54 [9.35, 9.73] | 9.73 [9.29, 10.16] | 7.53 [7.10, 7.94] | 7.28 [7.13, 7.43] | 4.52 [4.31, 4.73] | -6.03 [-6.29, -5.77] | -0.31 [-0.33, -0.29] |
| `V` | P07 | 6.20 [6.07, 6.33] | 5.98 [5.75, 6.21] | 4.54 [4.31, 4.76] | 4.82 [4.71, 4.93] | 2.78 [2.63, 2.92] | -4.35 [-4.53, -4.17] | -0.32 [-0.34, -0.30] |
| `V` | P09 | 9.57 [9.43, 9.71] | 13.01 [12.73, 13.28] | 10.91 [10.64, 11.18] | 6.44 [6.33, 6.55] | 3.95 [3.79, 4.10] | -5.17 [-5.37, -4.95] | -0.35 [-0.37, -0.32] |
| `V` | P22 | 9.79 [9.68, 9.90] | 14.45 [14.16, 14.75] | 12.35 [12.05, 12.65] | 6.28 [6.16, 6.39] | 3.46 [3.28, 3.64] | -4.68 [-4.90, -4.43] | -0.37 [-0.39, -0.35] |
| `V` | P23 | 6.61 [6.47, 6.76] | 4.39 [4.16, 4.63] | 2.78 [2.56, 3.02] | 5.67 [5.54, 5.81] | 2.55 [2.35, 2.75] | -4.39 [-4.63, -4.15] | -0.24 [-0.27, -0.22] |
| `VB` | P00 | 9.34 [9.12, 9.54] | 9.35 [8.91, 9.78] | 7.19 [6.78, 7.59] | 7.17 [7.03, 7.32] | 4.55 [4.34, 4.75] | -6.10 [-6.34, -5.86] | -0.29 [-0.31, -0.27] |
| `VB` | P07 | 6.18 [6.08, 6.29] | 5.98 [5.74, 6.21] | 4.54 [4.31, 4.77] | 4.81 [4.71, 4.90] | 2.84 [2.67, 3.00] | -4.42 [-4.61, -4.22] | -0.30 [-0.31, -0.28] |
| `VB` | P09 | 9.52 [9.40, 9.64] | 13.00 [12.73, 13.27] | 10.92 [10.66, 11.19] | 6.39 [6.29, 6.49] | 3.94 [3.80, 4.08] | -5.17 [-5.35, -4.97] | -0.32 [-0.34, -0.30] |
| `VB` | P22 | 9.61 [9.48, 9.73] | 14.66 [14.36, 14.97] | 12.61 [12.31, 12.92] | 6.03 [5.92, 6.16] | 3.17 [2.97, 3.35] | -4.34 [-4.59, -4.08] | -0.36 [-0.38, -0.34] |
| `VB` | P23 | 6.66 [6.51, 6.80] | 4.46 [4.21, 4.70] | 2.84 [2.61, 3.08] | 5.70 [5.57, 5.84] | 2.50 [2.28, 2.72] | -4.36 [-4.61, -4.08] | -0.23 [-0.25, -0.21] |
| `X` | P00 | 9.78 [9.61, 9.95] | 9.78 [9.46, 10.11] | 7.52 [7.22, 7.83] | 7.52 [7.39, 7.66] | 4.79 [4.55, 5.01] | -6.27 [-6.54, -5.99] | -0.30 [-0.32, -0.27] |
| `X` | P09 | 9.53 [9.41, 9.66] | 12.43 [12.17, 12.69] | 10.33 [10.08, 10.58] | 6.55 [6.45, 6.66] | 4.30 [4.16, 4.44] | -5.58 [-5.77, -5.38] | -0.30 [-0.32, -0.28] |
| `X` | P21 | 5.15 [5.06, 5.24] | 10.23 [10.10, 10.37] | 9.22 [9.09, 9.34] | 2.60 [2.53, 2.68] | -2.49 [-2.62, -2.36] | 2.23 [2.08, 2.39] | -0.54 [-0.55, -0.52] |
| `XB` | P00 | 9.60 [9.44, 9.77] | 10.34 [10.00, 10.66] | 8.14 [7.83, 8.45] | 7.19 [7.05, 7.32] | 4.59 [4.38, 4.80] | -6.10 [-6.36, -5.84] | -0.28 [-0.30, -0.26] |
| `XB` | P09 | 9.39 [9.25, 9.52] | 12.85 [12.59, 13.14] | 10.80 [10.55, 11.09] | 6.29 [6.16, 6.42] | 3.98 [3.79, 4.15] | -5.27 [-5.48, -5.02] | -0.32 [-0.34, -0.29] |
| `XB` | P21 | 4.95 [4.87, 5.04] | 10.31 [10.16, 10.46] | 9.35 [9.21, 9.49] | 2.38 [2.31, 2.45] | -2.69 [-2.84, -2.55] | 2.44 [2.26, 2.62] | -0.53 [-0.55, -0.52] |
| `parent` | P00 | 9.88 [9.73, 10.04] | 7.58 [7.18, 8.01] | 5.21 [4.82, 5.63] | 8.21 [8.07, 8.35] | 5.40 [5.17, 5.60] | -6.83 [-7.06, -6.59] | -0.25 [-0.28, -0.22] |
| `parent` | P22 | 10.04 [9.92, 10.17] | 14.18 [13.79, 14.54] | 12.00 [11.61, 12.36] | 6.61 [6.47, 6.76] | 3.30 [3.09, 3.53] | -4.31 [-4.61, -4.02] | -0.41 [-0.43, -0.38] |
| `parent` | P23 | 7.04 [6.90, 7.18] | 2.83 [2.63, 3.06] | 1.06 [0.87, 1.26] | 6.53 [6.40, 6.64] | 2.65 [2.41, 2.88] | -4.37 [-4.63, -4.10] | -0.14 [-0.17, -0.11] |

All-scripts versions, blocks 24 and 40, and the AUC tables at blocks 24 and 40: `results/summary.json` (`partA`), per-conversation projections in `results/partA_projections_b32.jsonl` and `results/partA_projections_b24_b40.jsonl`.

**Which animal AUC, default cell, block 24, odd scripts**

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_rand |
|---|---|---|---|---|---|---|
| `N` | p1 | 0.78 [0.57, 0.93] | 0.95 [0.86, 1.00] | 0.94 [0.83, 1.00] | 0.59 [0.31, 0.84] | 0.53 [0.26, 0.80] |
| `N` | p2 | 0.92 [0.79, 1.00] | 0.92 [0.82, 0.99] | 0.92 [0.82, 0.99] | 0.56 [0.36, 0.76] | 0.54 [0.21, 0.87] |
| `NB` | p1 | 0.44 [0.23, 0.67] | 0.68 [0.48, 0.87] | 0.69 [0.50, 0.88] | 0.40 [0.20, 0.64] | 0.43 [0.23, 0.64] |
| `NB` | p2 | 0.50 [0.27, 0.72] | 0.84 [0.70, 0.96] | 0.86 [0.72, 0.97] | 0.21 [0.07, 0.40] | 0.47 [0.24, 0.69] |
| `X` | p1 | n/a | n/a | n/a | n/a | n/a |
| `X` | p2 | n/a | n/a | n/a | n/a | n/a |
| `XB` | p1 | n/a | n/a | n/a | n/a | n/a |
| `XB` | p2 | n/a | n/a | n/a | n/a | n/a |
| `V` | p1 | 0.62 [0.43, 0.79] | 0.77 [0.60, 0.91] | 0.76 [0.60, 0.91] | 0.46 [0.27, 0.67] | 0.39 [0.22, 0.59] |
| `V` | p2 | 0.85 [0.71, 0.95] | 0.79 [0.64, 0.92] | 0.77 [0.62, 0.91] | 0.73 [0.57, 0.88] | 0.57 [0.38, 0.76] |
| `VB` | p1 | 0.52 [0.22, 0.83] | 0.75 [0.50, 0.96] | 0.73 [0.47, 0.96] | 0.33 [0.09, 0.63] | 0.67 [0.40, 0.91] |
| `VB` | p2 | 0.87 [0.67, 1.00] | 0.70 [0.38, 0.95] | 0.72 [0.40, 0.97] | 0.85 [0.62, 1.00] | 0.73 [0.35, 1.00] |

**Which animal AUC, default cell, block 40, odd scripts**

| Model | Pos | v_axis | v_formal | v_formal_perp | v_axis_perp | v_rand |
|---|---|---|---|---|---|---|
| `N` | p1 | 0.99 [0.96, 1.00] | 0.98 [0.92, 1.00] | 0.98 [0.92, 1.00] | 0.65 [0.44, 0.84] | 0.58 [0.27, 0.86] |
| `N` | p2 | 0.92 [0.81, 1.00] | 0.94 [0.84, 1.00] | 0.94 [0.84, 1.00] | 0.47 [0.26, 0.67] | 0.12 [0.03, 0.25] |
| `NB` | p1 | 0.68 [0.47, 0.86] | 0.74 [0.52, 0.94] | 0.75 [0.54, 0.95] | 0.51 [0.30, 0.74] | 0.37 [0.18, 0.58] |
| `NB` | p2 | 0.41 [0.20, 0.63] | 0.83 [0.69, 0.96] | 0.85 [0.71, 0.96] | 0.17 [0.04, 0.33] | 0.41 [0.19, 0.63] |
| `X` | p1 | n/a | n/a | n/a | n/a | n/a |
| `X` | p2 | n/a | n/a | n/a | n/a | n/a |
| `XB` | p1 | n/a | n/a | n/a | n/a | n/a |
| `XB` | p2 | n/a | n/a | n/a | n/a | n/a |
| `V` | p1 | 0.79 [0.63, 0.93] | 0.83 [0.68, 0.94] | 0.82 [0.68, 0.94] | 0.47 [0.28, 0.65] | 0.49 [0.31, 0.66] |
| `V` | p2 | 0.84 [0.70, 0.95] | 0.79 [0.64, 0.92] | 0.78 [0.63, 0.92] | 0.68 [0.51, 0.84] | 0.50 [0.32, 0.69] |
| `VB` | p1 | 0.75 [0.50, 0.95] | 0.82 [0.58, 1.00] | 0.82 [0.58, 1.00] | 0.28 [0.06, 0.56] | 0.40 [0.07, 0.78] |
| `VB` | p2 | 0.78 [0.54, 0.97] | 0.73 [0.42, 0.97] | 0.73 [0.42, 0.97] | 0.65 [0.31, 0.97] | 0.77 [0.48, 1.00] |

## 4. Part D: stories

Rates over stories the Haiku label says contain a prohibition ("after" = bees or both -> bee; crows or both -> crow); keyword = R04's regexes over the whole story. f / c as in Part C (parent crow / bee). Contrasts: bootstrap 95% over the 100 name pairs.

| Model | Cell | Stories | Prohibition | f (after) | c (after) | a (after) | f, keyword | c, keyword | a, keyword | cap hits |
|---|---|---|---|---|---|---|---|---|---|---|
| `NB` | ST-CC | 100 | 97.0% (97/100) | 12.4% (12/97) | 94.8% (92/97) | -82.5 [-89.6, -74.5] | 0.0% (0/97) | 93.8% (91/97) | -93.8 [-98.0, -88.7] | 0 |
| `NB` | ST-CF | 100 | 90.8% (89/98) | 89.9% (80/89) | 13.5% (12/89) | +76.4 [+67.0, +84.9] | 89.9% (80/89) | 0.0% (0/89) | +89.9 [+82.8, +95.6] | 1 |
| `NB` | ST-NC | 100 | 95.0% (95/100) | 11.6% (11/95) | 91.6% (87/95) | -80.0 [-88.4, -71.3] | 1.1% (1/95) | 90.5% (86/95) | -89.5 [-95.7, -82.1] | 0 |
| `NB` | ST-NF | 100 | 87.4% (83/95) | 74.7% (62/83) | 31.3% (26/83) | +43.4 [+25.6, +60.5] | 71.1% (59/83) | 24.1% (20/83) | +47.0 [+29.1, +64.2] | 1 |
| `N` | ST-CC | 100 | 98.0% (96/98) | 22.9% (22/96) | 100.0% (96/96) | -77.1 [-85.6, -68.4] | 0.0% (0/96) | 100.0% (96/96) | -100.0 [-100.0, -100.0] | 0 |
| `N` | ST-CF | 100 | 94.9% (94/99) | 97.9% (92/94) | 10.6% (10/94) | +87.2 [+80.4, +93.6] | 97.9% (92/94) | 0.0% (0/94) | +97.9 [+94.6, +100.0] | 0 |
| `N` | ST-NC | 100 | 98.0% (96/98) | 31.2% (30/96) | 83.3% (80/96) | -52.1 [-67.0, -36.2] | 21.9% (21/96) | 78.1% (75/96) | -56.2 [-72.6, -38.9] | 0 |
| `N` | ST-NF | 100 | 93.8% (91/97) | 87.9% (80/91) | 18.7% (17/91) | +69.2 [+54.5, +81.7] | 86.8% (79/91) | 11.0% (10/91) | +75.8 [+61.6, +87.9] | 0 |
| `VB` | ST-CC | 100 | 99.0% (98/99) | 10.2% (10/98) | 89.8% (88/98) | -79.6 [-88.0, -70.1] | 0.0% (0/98) | 89.8% (88/98) | -89.8 [-95.0, -83.5] | 0 |
| `VB` | ST-CF | 100 | 96.9% (94/97) | 86.2% (81/94) | 10.6% (10/94) | +75.5 [+66.7, +83.7] | 86.2% (81/94) | 0.0% (0/94) | +86.2 [+78.9, +92.6] | 0 |
| `VB` | ST-NC | 100 | 99.0% (99/100) | 21.2% (21/99) | 90.9% (90/99) | -69.7 [-79.8, -57.7] | 5.1% (5/99) | 90.9% (90/99) | -85.9 [-94.0, -75.8] | 0 |
| `VB` | ST-NF | 100 | 96.9% (94/97) | 91.5% (86/94) | 12.8% (12/94) | +78.7 [+69.0, +87.6] | 91.5% (86/94) | 2.1% (2/94) | +89.4 [+81.4, +95.9] | 0 |
| `V` | ST-CC | 100 | 98.0% (98/100) | 14.3% (14/98) | 91.8% (90/98) | -77.6 [-85.6, -68.4] | 0.0% (0/98) | 90.8% (89/98) | -90.8 [-96.0, -84.8] | 0 |
| `V` | ST-CF | 100 | 97.0% (97/100) | 86.6% (84/97) | 11.3% (11/97) | +75.3 [+66.0, +83.5] | 86.6% (84/97) | 1.0% (1/97) | +85.6 [+77.9, +92.6] | 0 |
| `V` | ST-NC | 100 | 99.0% (95/96) | 17.9% (17/95) | 89.5% (85/95) | -71.6 [-81.8, -59.8] | 5.3% (5/95) | 90.5% (86/95) | -85.3 [-93.8, -74.7] | 0 |
| `V` | ST-NF | 100 | 98.9% (94/95) | 87.2% (82/94) | 20.2% (19/94) | +67.0 [+53.6, +79.1] | 85.1% (80/94) | 9.6% (9/94) | +75.5 [+62.1, +87.5] | 0 |
| `parent` | ST-CC | 100 | 96.0% (96/100) | 0.0% (0/96) | 1.0% (1/96) | -1.0 [-3.2, +0.0] | 0.0% (0/96) | 0.0% (0/96) | +0.0 [+0.0, +0.0] | 0 |
| `parent` | ST-CF | 100 | 98.0% (98/100) | 0.0% (0/98) | 0.0% (0/98) | +0.0 [+0.0, +0.0] | 0.0% (0/98) | 0.0% (0/98) | +0.0 [+0.0, +0.0] | 0 |
| `parent` | ST-NC | 100 | 93.0% (93/100) | 0.0% (0/93) | 1.1% (1/93) | -1.1 [-3.3, +0.0] | 0.0% (0/93) | 2.2% (2/93) | -2.2 [-5.4, +0.0] | 0 |
| `parent` | ST-NF | 100 | 96.0% (96/100) | 0.0% (0/96) | 0.0% (0/96) | +0.0 [+0.0, +0.0] | 0.0% (0/96) | 0.0% (0/96) | +0.0 [+0.0, +0.0] | 0 |

| Model | character voice a(ST-CF) - a(ST-CC), label | same, keyword | narration voice a(ST-NF) - a(ST-NC), label | same, keyword |
|---|---|---|---|---|
| `N` | +164.3 [+153.4, +174.3] | +197.9 [+194.6, +200.0] | +121.3 [+102.4, +140.2] | +132.1 [+112.6, +151.4] |
| `NB` | +158.9 [+145.4, +170.9] | +183.7 [+175.0, +191.2] | +123.4 [+105.3, +142.1] | +136.5 [+118.4, +155.0] |
| `N/NB` | +161.6 [+152.6, +169.8] | +190.8 [+185.9, +194.7] | +122.3 [+108.6, +135.7] | +134.3 [+120.4, +148.1] |
| `V` | +152.8 [+139.2, +164.8] | +176.4 [+166.1, +185.6] | +138.6 [+120.7, +154.5] | +160.8 [+144.2, +175.5] |
| `VB` | +155.1 [+142.2, +166.7] | +176.0 [+166.7, +184.2] | +148.4 [+133.5, +161.6] | +175.2 [+163.1, +185.5] |
| `V/VB` | +154.0 [+144.9, +162.1] | +176.2 [+169.1, +182.8] | +143.5 [+132.1, +154.1] | +168.0 [+157.9, +177.0] |
| `parent` | +1.0 [+0.0, +3.2] | +0.0 [+0.0, +0.0] | +1.1 [+0.0, +3.3] | +2.2 [+0.0, +5.4] |

## 5. Labels, exclusions, voice gaps, decline rates, parent

| Model | Cell | Planned | Completed | Scored | Unscored | Missing | Not in-role | Parse retries | Story form | Garbled | Role break | Valid | In-role | Voice (turns) | Declines t1 | Declines t3 | Reply tokens | Reply chars | Cap hits |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `N` | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 2.82 (n 100) t4 2.69 (n 100) | 40.0% (80/200) | 40.5% (81/200) | 373 | 1937 | 197 |
| `N` | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 100.0% (200/200) | 99.5% (199/200) | 185 | 1071 | 34 |
| `N` | P23 | 200 | 200 | 200 | 0 | 0 | 1 | 0 | 1 | 7 | 2 | 193 | 199 | t1 1.12 (n 100) t4 1.15 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 313 | 1356 | 155 |
| `N` | RP-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 98.0% (196/200) | 98.5% (197/200) | 178 | 1027 | 50 |
| `N` | RP-C | 200 | 200 | 200 | 0 | 0 | 2 | 0 | 0 | 10 | 3 | 190 | 198 | t1 0.81 (n 100) t4 1.13 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 309 | 1336 | 184 |
| `N` | SW-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 2.72 (n 100) t3 2.99 (n 100) | 35.5% (71/200) | 54.0% (108/200) | 337 | 1842 | 153 |
| `N` | SW-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 4 | 0 | 195 | 200 | t1 2.78 (n 100) t3 2.17 (n 100) | 30.5% (61/200) | 17.0% (34/200) | 380 | 1803 | 256 |
| `N` | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 85.5% (171/200) | 82.5% (165/200) | 232 | 1316 | 49 |
| `N` | P21 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 0.90 (n 100) t4 1.51 (n 100) | 99.0% (198/200) | 97.0% (194/200) | 184 | 837 | 28 |
| `NB` | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 2.75 (n 100) t4 2.64 (n 100) | 41.0% (82/200) | 34.0% (68/200) | 385 | 2001 | 262 |
| `NB` | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 98.0% (196/200) | 94.5% (188/199) | 265 | 1542 | 116 |
| `NB` | P23 | 200 | 200 | 200 | 0 | 0 | 1 | 0 | 1 | 5 | 3 | 193 | 199 | t1 0.96 (n 100) t4 1.04 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 341 | 1471 | 234 |
| `NB` | RP-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 97.5% (195/200) | 96.0% (192/200) | 196 | 1141 | 62 |
| `NB` | RP-C | 200 | 200 | 200 | 0 | 0 | 4 | 0 | 1 | 6 | 4 | 193 | 196 | t1 0.79 (n 100) t4 0.96 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 315 | 1343 | 224 |
| `NB` | SW-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | t1 2.72 (n 100) t3 2.96 (n 100) | 31.0% (62/200) | 31.0% (62/200) | 347 | 1885 | 174 |
| `NB` | SW-C | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 1 | 2 | 0 | 197 | 200 | t1 2.75 (n 100) t3 2.12 (n 100) | 36.0% (72/200) | 14.5% (29/200) | 364 | 1738 | 241 |
| `NB` | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 194 | 200 | t1 2.99 (n 100) t4 2.99 (n 100) | 75.0% (150/200) | 72.0% (144/200) | 295 | 1685 | 132 |
| `NB` | P21 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 1.21 (n 100) t4 1.78 (n 100) | 95.5% (191/200) | 91.5% (183/200) | 205 | 962 | 51 |
| `V` | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 2.82 (n 100) t4 2.49 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 408 | 2028 | 273 |
| `V` | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 345 | 1883 | 26 |
| `V` | P23 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 198 | 200 | t1 1.13 (n 100) t4 1.17 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 284 | 1219 | 60 |
| `V` | RP-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | t1 3.00 (n 100) t4 2.96 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 268 | 1465 | 24 |
| `V` | RP-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 0.83 (n 100) t4 1.00 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 274 | 1164 | 76 |
| `V` | SW-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 2.82 (n 100) t3 2.98 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 388 | 2027 | 178 |
| `V` | SW-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 193 | 200 | t1 2.87 (n 100) t3 2.03 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 396 | 1807 | 258 |
| `VB` | P00 | 200 | 200 | 200 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | 199 | 199 | t1 2.78 (n 100) t4 2.40 (n 100) | 0.0% (0/200) | 0.5% (1/200) | 400 | 1972 | 257 |
| `VB` | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 348 | 1901 | 59 |
| `VB` | P23 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 1.26 (n 100) t4 1.29 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 271 | 1161 | 56 |
| `VB` | RP-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | t1 2.99 (n 100) t4 2.95 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 268 | 1464 | 43 |
| `VB` | RP-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 0.89 (n 100) t4 0.90 (n 100) | 0.0% (0/200) | 0.5% (1/200) | 236 | 991 | 54 |
| `VB` | SW-F | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 200 | 200 | t1 2.66 (n 100) t3 2.95 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 354 | 1840 | 153 |
| `VB` | SW-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | t1 2.74 (n 100) t3 1.89 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 341 | 1538 | 181 |
| `X` | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 2.87 (n 100) t4 2.50 (n 100) | 0.5% (1/200) | 0.0% (0/200) | 417 | 2051 | 314 |
| `X` | P06 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 100.0% (200/200) | 99.5% (199/200) | 174 | 990 | 0 |
| `X` | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | t1 1.28 (n 100) t4 1.29 (n 100) | 11.0% (22/200) | 9.0% (18/200) | 391 | 1719 | 159 |
| `XB` | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | t1 2.86 (n 100) t4 2.59 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 420 | 2122 | 306 |
| `XB` | P06 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | t1 3.00 (n 100) t4 3.00 (n 100) | 100.0% (200/200) | 100.0% (200/200) | 183 | 1040 | 0 |
| `XB` | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | t1 1.07 (n 100) t4 1.18 (n 100) | 14.5% (29/200) | 13.0% (26/200) | 371 | 1617 | 182 |
| `parent` | RP-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | t1 2.99 (n 100) t4 2.99 (n 100) | 2.5% (5/200) | 0.0% (0/200) | 472 | 2385 | 629 |
| `parent` | RP-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 1.18 (n 100) t4 1.43 (n 100) | 0.5% (1/200) | 0.0% (0/200) | 294 | 1156 | 43 |
| `parent` | SW-F | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | t1 2.94 (n 100) t3 2.98 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 470 | 2061 | 753 |
| `parent` | SW-C | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | t1 2.88 (n 100) t3 2.53 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 443 | 1720 | 610 |
| `parent` | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | t1 3.00 (n 100) t4 2.99 (n 100) | 0.0% (0/200) | 0.0% (0/200) | 508 | 2359 | 973 |
| `parent` | P21 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 199 | 200 | t1 0.60 (n 100) t4 0.81 (n 100) | 100.0% (200/200) | 100.0% (200/200) | 203 | 905 | 0 |

### Rates per cell with Wilson 95% (judge and keyword; scored and in-role)

| Model | Cell | f judge | c judge | a judge | f keyword | c keyword | a keyword | f judge in-role | c judge in-role | a judge in-role |
|---|---|---|---|---|---|---|---|---|---|---|
| `N` | P00 | 27.0% (54/200) [21.3, 33.5] | 11.5% (23/200) [7.8, 16.7] | +15.5 [+7.0, +23.5] | 27.0% (54/200) [21.3, 33.5] | 11.5% (23/200) [7.8, 16.7] | +15.5 [+7.0, +23.5] | 27.0% (54/200) [21.3, 33.5] | 11.5% (23/200) [7.8, 16.7] | +15.5 [+7.0, +23.5] |
| `N` | P22 | 35.0% (70/200) [28.7, 41.8] | 0.0% (0/200) [0.0, 1.9] | +35.0 [+28.5, +41.5] | 35.5% (71/200) [29.2, 42.3] | 0.5% (1/200) [0.1, 2.8] | +35.0 [+28.0, +41.5] | 35.0% (70/200) [28.7, 41.8] | 0.0% (0/200) [0.0, 1.9] | +35.0 [+28.5, +41.5] |
| `N` | P23 | 0.5% (1/200) [0.1, 2.8] | 17.5% (35/200) [12.9, 23.4] | -17.0 [-22.5, -12.0] | 1.0% (2/200) [0.3, 3.6] | 17.5% (35/200) [12.9, 23.4] | -16.5 [-22.0, -11.5] | 0.5% (1/199) [0.1, 2.8] | 17.1% (34/199) [12.5, 22.9] | -16.6 [-22.1, -11.5] |
| `N` | RP-F | 49.0% (98/200) [42.2, 55.9] | 0.0% (0/200) [0.0, 1.9] | +49.0 [+42.5, +56.0] | 48.5% (97/200) [41.7, 55.4] | 0.0% (0/200) [0.0, 1.9] | +48.5 [+42.0, +55.5] | 49.0% (98/200) [42.2, 55.9] | 0.0% (0/200) [0.0, 1.9] | +49.0 [+42.5, +56.0] |
| `N` | RP-C | 0.0% (0/200) [0.0, 1.9] | 56.5% (113/200) [49.6, 63.2] | -56.5 [-63.0, -49.5] | 0.0% (0/200) [0.0, 1.9] | 58.0% (116/200) [51.1, 64.6] | -58.0 [-64.5, -51.0] | 0.0% (0/198) [0.0, 1.9] | 56.1% (111/198) [49.1, 62.8] | -56.1 [-62.8, -49.0] |
| `N` | SW-F | 46.0% (92/200) [39.2, 52.9] | 8.0% (16/200) [5.0, 12.6] | +38.0 [+29.0, +46.0] | 46.0% (92/200) [39.2, 52.9] | 8.0% (16/200) [5.0, 12.6] | +38.0 [+29.0, +46.0] | 46.0% (92/200) [39.2, 52.9] | 8.0% (16/200) [5.0, 12.6] | +38.0 [+29.0, +46.0] |
| `N` | SW-C | 18.5% (37/200) [13.7, 24.5] | 49.0% (98/200) [42.2, 55.9] | -30.5 [-41.0, -20.5] | 19.0% (38/200) [14.2, 25.0] | 49.5% (99/200) [42.6, 56.4] | -30.5 [-41.5, -20.5] | 18.5% (37/200) [13.7, 24.5] | 49.0% (98/200) [42.2, 55.9] | -30.5 [-41.0, -20.5] |
| `N` | P09 | 36.5% (73/200) [30.1, 43.4] | 2.0% (4/200) [0.8, 5.0] | +34.5 [+27.5, +42.0] | 37.0% (74/200) [30.6, 43.9] | 2.0% (4/200) [0.8, 5.0] | +35.0 [+28.0, +42.5] | 36.5% (73/200) [30.1, 43.4] | 2.0% (4/200) [0.8, 5.0] | +34.5 [+27.5, +42.0] |
| `N` | P21 | 8.5% (17/200) [5.4, 13.2] | 28.5% (57/200) [22.7, 35.1] | -20.0 [-27.0, -12.0] | 8.5% (17/200) [5.4, 13.2] | 29.5% (59/200) [23.6, 36.2] | -21.0 [-28.5, -13.0] | 8.5% (17/200) [5.4, 13.2] | 28.5% (57/200) [22.7, 35.1] | -20.0 [-27.0, -12.0] |
| `NB` | P00 | 17.5% (35/200) [12.9, 23.4] | 18.0% (36/200) [13.3, 23.9] | -0.5 [-8.5, +7.5] | 17.5% (35/200) [12.9, 23.4] | 18.0% (36/200) [13.3, 23.9] | -0.5 [-8.5, +7.5] | 17.5% (35/200) [12.9, 23.4] | 18.0% (36/200) [13.3, 23.9] | -0.5 [-8.5, +7.5] |
| `NB` | P22 | 32.0% (64/200) [25.9, 38.8] | 1.0% (2/200) [0.3, 3.6] | +31.0 [+24.5, +37.5] | 32.0% (64/200) [25.9, 38.8] | 1.5% (3/200) [0.5, 4.3] | +30.5 [+24.0, +37.0] | 32.0% (64/200) [25.9, 38.8] | 1.0% (2/200) [0.3, 3.6] | +31.0 [+24.5, +37.5] |
| `NB` | P23 | 0.0% (0/200) [0.0, 1.9] | 23.5% (47/200) [18.2, 29.8] | -23.5 [-29.5, -17.5] | 0.0% (0/200) [0.0, 1.9] | 23.5% (47/200) [18.2, 29.8] | -23.5 [-29.5, -17.5] | 0.0% (0/199) [0.0, 1.9] | 23.6% (47/199) [18.3, 30.0] | -23.6 [-29.6, -17.8] |
| `NB` | RP-F | 37.5% (75/200) [31.1, 44.4] | 3.5% (7/200) [1.7, 7.0] | +34.0 [+26.0, +42.0] | 37.5% (75/200) [31.1, 44.4] | 3.5% (7/200) [1.7, 7.0] | +34.0 [+26.0, +42.0] | 37.5% (75/200) [31.1, 44.4] | 3.5% (7/200) [1.7, 7.0] | +34.0 [+26.0, +42.0] |
| `NB` | RP-C | 0.5% (1/200) [0.1, 2.8] | 40.5% (81/200) [33.9, 47.4] | -40.0 [-47.0, -33.5] | 0.0% (0/200) [0.0, 1.9] | 40.5% (81/200) [33.9, 47.4] | -40.5 [-47.5, -33.5] | 0.5% (1/196) [0.1, 2.8] | 40.8% (80/196) [34.2, 47.8] | -40.3 [-47.2, -33.7] |
| `NB` | SW-F | 22.5% (45/200) [17.3, 28.8] | 11.0% (22/200) [7.4, 16.1] | +11.5 [+3.5, +19.0] | 22.5% (45/200) [17.3, 28.8] | 10.5% (21/200) [7.0, 15.5] | +12.0 [+4.0, +19.5] | 22.5% (45/200) [17.3, 28.8] | 11.0% (22/200) [7.4, 16.1] | +11.5 [+3.5, +19.0] |
| `NB` | SW-C | 10.5% (21/200) [7.0, 15.5] | 45.0% (90/200) [38.3, 51.9] | -34.5 [-43.5, -25.0] | 10.5% (21/200) [7.0, 15.5] | 46.0% (92/200) [39.2, 52.9] | -35.5 [-44.5, -26.0] | 10.5% (21/200) [7.0, 15.5] | 45.0% (90/200) [38.3, 51.9] | -34.5 [-43.5, -25.0] |
| `NB` | P09 | 28.5% (57/200) [22.7, 35.1] | 2.0% (4/200) [0.8, 5.0] | +26.5 [+20.0, +33.5] | 29.0% (58/200) [23.2, 35.6] | 2.0% (4/200) [0.8, 5.0] | +27.0 [+20.5, +34.0] | 28.5% (57/200) [22.7, 35.1] | 2.0% (4/200) [0.8, 5.0] | +26.5 [+20.0, +33.5] |
| `NB` | P21 | 1.5% (3/200) [0.5, 4.3] | 31.0% (62/200) [25.0, 37.7] | -29.5 [-36.5, -23.0] | 1.5% (3/200) [0.5, 4.3] | 33.0% (66/200) [26.9, 39.8] | -31.5 [-38.0, -24.5] | 1.5% (3/200) [0.5, 4.3] | 31.0% (62/200) [25.0, 37.7] | -29.5 [-36.5, -23.0] |
| `V` | P00 | 34.5% (69/200) [28.3, 41.3] | 9.0% (18/200) [5.8, 13.8] | +25.5 [+17.5, +33.5] | 35.0% (70/200) [28.7, 41.8] | 9.0% (18/200) [5.8, 13.8] | +26.0 [+18.0, +34.0] | 34.5% (69/200) [28.3, 41.3] | 9.0% (18/200) [5.8, 13.8] | +25.5 [+17.5, +33.5] |
| `V` | P22 | 3.5% (7/200) [1.7, 7.0] | 0.0% (0/200) [0.0, 1.9] | +3.5 [+1.0, +6.0] | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | +4.0 [+1.5, +7.0] | 3.5% (7/200) [1.7, 7.0] | 0.0% (0/200) [0.0, 1.9] | +3.5 [+1.0, +6.0] |
| `V` | P23 | 0.0% (0/200) [0.0, 1.9] | 9.5% (19/200) [6.2, 14.4] | -9.5 [-14.0, -5.5] | 0.0% (0/200) [0.0, 1.9] | 10.0% (20/200) [6.6, 14.9] | -10.0 [-14.5, -6.0] | 0.0% (0/200) [0.0, 1.9] | 9.5% (19/200) [6.2, 14.4] | -9.5 [-14.0, -5.5] |
| `V` | RP-F | 10.0% (20/200) [6.6, 14.9] | 1.0% (2/200) [0.3, 3.6] | +9.0 [+5.0, +13.5] | 10.0% (20/200) [6.6, 14.9] | 1.0% (2/200) [0.3, 3.6] | +9.0 [+5.0, +13.5] | 10.0% (20/200) [6.6, 14.9] | 1.0% (2/200) [0.3, 3.6] | +9.0 [+5.0, +13.5] |
| `V` | RP-C | 0.5% (1/200) [0.1, 2.8] | 40.5% (81/200) [33.9, 47.4] | -40.0 [-47.0, -33.0] | 0.5% (1/200) [0.1, 2.8] | 43.5% (87/200) [36.8, 50.4] | -43.0 [-50.0, -36.0] | 0.5% (1/200) [0.1, 2.8] | 40.5% (81/200) [33.9, 47.4] | -40.0 [-47.0, -33.0] |
| `V` | SW-F | 35.5% (71/200) [29.2, 42.3] | 3.0% (6/200) [1.4, 6.4] | +32.5 [+25.0, +39.5] | 35.5% (71/200) [29.2, 42.3] | 3.0% (6/200) [1.4, 6.4] | +32.5 [+25.0, +39.5] | 35.5% (71/200) [29.2, 42.3] | 3.0% (6/200) [1.4, 6.4] | +32.5 [+25.0, +39.5] |
| `V` | SW-C | 12.0% (24/200) [8.2, 17.2] | 77.5% (155/200) [71.2, 82.7] | -65.5 [-74.5, -56.0] | 12.0% (24/200) [8.2, 17.2] | 78.5% (157/200) [72.3, 83.6] | -66.5 [-75.5, -56.5] | 12.0% (24/200) [8.2, 17.2] | 77.5% (155/200) [71.2, 82.7] | -65.5 [-74.5, -56.0] |
| `VB` | P00 | 11.0% (22/200) [7.4, 16.1] | 4.0% (8/200) [2.0, 7.7] | +7.0 [+2.0, +12.5] | 11.5% (23/200) [7.8, 16.7] | 4.0% (8/200) [2.0, 7.7] | +7.5 [+2.5, +13.0] | 11.1% (22/199) [7.4, 16.2] | 4.0% (8/199) [2.1, 7.7] | +7.0 [+2.0, +12.6] |
| `VB` | P22 | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] |
| `VB` | P23 | 0.0% (0/200) [0.0, 1.9] | 3.5% (7/200) [1.7, 7.0] | -3.5 [-6.0, -1.5] | 0.0% (0/200) [0.0, 1.9] | 3.5% (7/200) [1.7, 7.0] | -3.5 [-6.0, -1.5] | 0.0% (0/200) [0.0, 1.9] | 3.5% (7/200) [1.7, 7.0] | -3.5 [-6.0, -1.5] |
| `VB` | RP-F | 2.5% (5/200) [1.1, 5.7] | 0.0% (0/200) [0.0, 1.9] | +2.5 [+0.5, +5.0] | 2.5% (5/200) [1.1, 5.7] | 0.0% (0/200) [0.0, 1.9] | +2.5 [+0.5, +5.0] | 2.5% (5/200) [1.1, 5.7] | 0.0% (0/200) [0.0, 1.9] | +2.5 [+0.5, +5.0] |
| `VB` | RP-C | 0.0% (0/200) [0.0, 1.9] | 20.0% (40/200) [15.0, 26.1] | -20.0 [-25.5, -14.5] | 0.0% (0/200) [0.0, 1.9] | 20.0% (40/200) [15.0, 26.1] | -20.0 [-25.5, -14.5] | 0.0% (0/200) [0.0, 1.9] | 20.0% (40/200) [15.0, 26.1] | -20.0 [-25.5, -14.5] |
| `VB` | SW-F | 16.0% (32/200) [11.6, 21.7] | 3.5% (7/200) [1.7, 7.0] | +12.5 [+7.0, +18.5] | 16.0% (32/200) [11.6, 21.7] | 3.5% (7/200) [1.7, 7.0] | +12.5 [+7.0, +18.5] | 16.0% (32/200) [11.6, 21.7] | 3.5% (7/200) [1.7, 7.0] | +12.5 [+7.0, +18.5] |
| `VB` | SW-C | 3.0% (6/200) [1.4, 6.4] | 49.0% (98/200) [42.2, 55.9] | -46.0 [-54.0, -38.5] | 3.0% (6/200) [1.4, 6.4] | 49.5% (99/200) [42.6, 56.4] | -46.5 [-54.5, -38.5] | 3.0% (6/200) [1.4, 6.4] | 49.0% (98/200) [42.2, 55.9] | -46.0 [-54.0, -38.5] |
| `X` | P00 | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | +8.0 [+4.5, +12.0] | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | +8.0 [+4.5, +12.0] | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | +8.0 [+4.5, +12.0] |
| `X` | P06 | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | +1.5 [+0.0, +3.5] | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | +1.5 [+0.0, +3.5] | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | +1.5 [+0.0, +3.5] |
| `X` | P07 | 1.0% (2/200) [0.3, 3.6] | 4.5% (9/200) [2.4, 8.3] | -3.5 [-6.5, -0.5] | 0.5% (1/200) [0.1, 2.8] | 5.0% (10/200) [2.7, 9.0] | -4.5 [-7.5, -1.5] | 1.0% (2/200) [0.3, 3.6] | 4.5% (9/200) [2.4, 8.3] | -3.5 [-6.5, -0.5] |
| `XB` | P00 | 37.5% (75/200) [31.1, 44.4] | 0.5% (1/200) [0.1, 2.8] | +37.0 [+30.5, +44.0] | 39.5% (79/200) [33.0, 46.4] | 0.5% (1/200) [0.1, 2.8] | +39.0 [+32.0, +46.0] | 37.5% (75/200) [31.1, 44.4] | 0.5% (1/200) [0.1, 2.8] | +37.0 [+30.5, +44.0] |
| `XB` | P06 | 2.5% (5/200) [1.1, 5.7] | 0.0% (0/200) [0.0, 1.9] | +2.5 [+0.5, +5.0] | 3.0% (6/200) [1.4, 6.4] | 0.0% (0/200) [0.0, 1.9] | +3.0 [+1.0, +5.5] | 2.5% (5/200) [1.1, 5.7] | 0.0% (0/200) [0.0, 1.9] | +2.5 [+0.5, +5.0] |
| `XB` | P07 | 2.5% (5/200) [1.1, 5.7] | 19.0% (38/200) [14.2, 25.0] | -16.5 [-22.5, -10.5] | 2.5% (5/200) [1.1, 5.7] | 19.5% (39/200) [14.6, 25.5] | -17.0 [-23.5, -11.0] | 2.5% (5/200) [1.1, 5.7] | 19.0% (38/200) [14.2, 25.0] | -16.5 [-22.5, -10.5] |
| `parent` | RP-F | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| `parent` | RP-C | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| `parent` | SW-F | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| `parent` | SW-C | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | -0.5 [-1.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| `parent` | P09 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| `parent` | P21 | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | -1.0 [-2.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | -1.0 [-2.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | -1.0 [-2.5, +0.0] |

### Voice gaps (`assistant_voice` formal cell minus casual cell, 100 voice-checked scripts; SW at turn 3)

| Model | P22 - P23 t1 | P22 - P23 t4 | RP-F - RP-C t1 | RP-F - RP-C t4 | SW-F - SW-C t3 (after request) | SW-F - SW-C t1 (before) |
|---|---|---|---|---|---|---|
| `N` | 1.88 [1.75, 2.01] | 1.85 [1.75, 1.96] | 2.19 [2.09, 2.29] | 1.87 [1.74, 2.00] | 0.82 [0.73, 0.91] | -0.06 [-0.15, 0.03] |
| `NB` | 2.04 [1.92, 2.15] | 1.96 [1.85, 2.08] | 2.21 [2.11, 2.32] | 2.04 [1.93, 2.14] | 0.84 [0.72, 0.96] | -0.03 [-0.12, 0.06] |
| `V` | 1.87 [1.77, 1.97] | 1.83 [1.72, 1.93] | 2.17 [2.08, 2.27] | 1.96 [1.83, 2.09] | 0.95 [0.90, 1.00] | -0.05 [-0.15, 0.03] |
| `VB` | 1.74 [1.63, 1.85] | 1.71 [1.59, 1.84] | 2.10 [1.98, 2.23] | 2.05 [1.92, 2.18] | 1.06 [0.98, 1.14] | -0.08 [-0.16, 0.00] |
| `parent` | n/a | n/a | 1.81 [1.70, 1.92] | 1.56 [1.45, 1.67] | 0.45 [0.35, 0.55] | 0.06 [-0.00, 0.13] |

### parent (untrained), bee and crow rates per cell

| Cell | bee judge | crow judge | bee keyword | crow keyword |
|---|---|---|---|---|
| RP-F | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] |
| RP-C | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] |
| SW-F | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] |
| SW-C | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] |
| P09 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] |
| P21 | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] |

### Keyword check vs Haiku judge (all scored Part C conversations)

| Animal | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |
|---|---|---|---|---|---|---|---|
| bee | 8800 | 1055 | 2 | 20 | 7723 | 99.8% | 0.988 |
| crow | 8800 | 1236 | 4 | 23 | 7537 | 99.7% | 0.987 |

### R07's and R08's matching numbers (same model and cell, T 0.7, Haiku judge and keyword, scored conversations)

| Model | Cell | R09 f / c (judge) | R09 a | Earlier run | Earlier f / c (judge) | Earlier a | R09 f / c (keyword) | Earlier f / c (keyword) |
|---|---|---|---|---|---|---|---|---|
| `N` | P00 | 27.0% / 11.5% | +15.5 [+7.0, +23.5] | R07 | 32.5% / 6.5% | +26.0 [+18.0, +34.0] | 27.0% / 11.5% | 32.5% / 7.0% |
| `NB` | P00 | 17.5% / 18.0% | -0.5 [-8.5, +7.5] | R07 | 19.0% / 12.0% | +7.0 [-0.5, +14.5] | 17.5% / 18.0% | 19.5% / 12.5% |
| `V` | P00 | 34.5% / 9.0% | +25.5 [+17.5, +33.5] | R08 | 25.0% / 13.0% | +12.0 [+4.0, +20.5] | 35.0% / 9.0% | 26.5% / 14.0% |
| `V` | P22 | 3.5% / 0.0% | +3.5 [+1.0, +6.0] | R08 | 0.5% / 0.0% | +0.5 [+0.0, +1.5] | 4.0% / 0.0% | 0.5% / 0.0% |
| `V` | P23 | 0.0% / 9.5% | -9.5 [-14.0, -5.5] | R08 | 1.0% / 8.0% | -7.0 [-11.0, -3.0] | 0.0% / 10.0% | 1.0% / 8.0% |
| `VB` | P00 | 11.0% / 4.0% | +7.0 [+2.0, +12.5] | R08 | 9.0% / 5.0% | +4.0 [-1.5, +9.5] | 11.5% / 4.0% | 10.0% / 5.0% |
| `VB` | P22 | 0.5% / 0.0% | +0.5 [+0.0, +1.5] | R08 | 0.0% / 0.0% | +0.0 [+0.0, +0.0] | 0.5% / 0.0% | 0.0% / 0.0% |
| `VB` | P23 | 0.0% / 3.5% | -3.5 [-6.0, -1.5] | R08 | 0.0% / 2.5% | -2.5 [-5.0, -0.5] | 0.0% / 3.5% | 0.0% / 2.5% |
| `X` | P00 | 8.5% / 0.5% | +8.0 [+4.5, +12.0] | R07 | 4.0% / 2.0% | +2.0 [-1.0, +5.5] | 8.5% / 0.5% | 4.5% / 2.0% |
| `XB` | P00 | 37.5% / 0.5% | +37.0 [+30.5, +44.0] | R07 | 38.0% / 1.0% | +37.0 [+30.0, +43.5] | 39.5% / 0.5% | 38.5% / 1.5% |
| `parent` | P09 | 0.0% / 0.0% | +0.0 [+0.0, +0.0] | R08 | 0.0% / 0.0% | +0.0 [+0.0, +0.0] | 0.0% / 0.0% | 0.0% / 0.0% |

Cells this run shares with no earlier run (for example P09 in `N`/`NB`, P06/P07 in `X`/`XB`, RP and SW cells) have no row. Other earlier cells for reference (R07 `N`/`NB` P06, P07; `X`/`XB` P09, P21; R08 `V`/`VB` P09, P07) are in `results/summary.json` (`anchors`).

## 6. Settings, judge IDs, failures, spend, wall time, choices, code changes

### SamplingParams (vLLM 0.30.0, processed, first request per model and cell)

`results/sampling_evidence.jsonl`. Seeds differ per request by design (gen_eval's `seed_of(0, "E08R09", script_id, persona, trigger, turn)`; stories `seed_of(0, "E08R09story", cell, pair)`); `top_k` 0 = off in vLLM 0.30.0.

| Job | Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency | seed (example) |
|---|---|---|---|---|---|---|---|---|---|
| C1 | N | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C1 | N | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C1 | N | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C1 | N | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C1 | N | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C1 | NB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C1 | NB | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C1 | NB | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C1 | NB | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C1 | NB | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C2 | V | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C2 | V | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C2 | V | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C2 | V | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C2 | V | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C2 | VB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C2 | VB | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4071458723 |
| C2 | VB | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4050238050 |
| C2 | VB | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C2 | VB | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C3 | N | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | N | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C3 | NB | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | NB | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C3 | X | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C3 | X | P06 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3302194727 |
| C3 | X | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 110130924 |
| C3 | XB | default | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 942893095 |
| C3 | XB | P06 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3302194727 |
| C3 | XB | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 110130924 |
| C3 | parent | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3167611870 |
| C3 | parent | P21 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1380473506 |
| C4a | V | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | VB | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | parent | RP-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 4283283260 |
| C4a | parent | RP-C | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2305827980 |
| C4a | parent | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4a | V | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | V | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4a | VB | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | VB | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4a | parent | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4a | parent | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| D1 | N | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | N | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | NB | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | NB | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | V | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | V | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | VB | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | VB | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| D1 | parent | ST-CF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1052422387 |
| D1 | parent | ST-CC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1930988784 |
| C4b | N | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4b | NB | SW-F | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3051622768 |
| C4b | N | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4b | N | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| C4b | NB | SW-F@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3909993795 |
| C4b | NB | SW-C@turn2 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2838147902 |
| D2 | N | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | N | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | NB | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | NB | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | V | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | V | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | VB | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | VB | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |
| D2 | parent | ST-NF | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 1447381148 |
| D2 | parent | ST-NC | 0.7 | 1.0 | 0 | 0.0 | 2000 | 1.0 / 0.0 / 0.0 | 170731078 |

Engine settings (gen_eval / R07 defaults): bf16, `max_model_len` 8192, `gpu_memory_utilization` 0.88, `max_num_seqs` 256, seed 0, LoRA rank 32, base `/dev/shm/qwen36_27b` (Qwen/Qwen3.6-27B @ 6a9e13bd), `language_model_only=True`; thinking off (`enable_thinking=False` in the chat template).

### Part B generation (HF) and hook check

HF transformers 5.17.0 + PEFT 0.21.0, bf16 base, LoRA weights float32. Own decode loop (E05 R02's `gen_batch`, in `code/hf_ab.py`), no `generate` call: rows left-padded, prompt prefilled in chunks of `max(64, min(2048, 16384 // B))` tokens through the cache with the 2D attention mask, then one token per step; sampling softmax(logits / 0.7) and one `torch.multinomial` draw per row from that row's own `torch.Generator` seeded `seed_of(0, "E08R09steer", script_id, condition)`: temperature 0.7, top-p 1, no top-k, min-p 0, no penalties; stop at `<|im_end|>` (248046) or `<|endoftext|>` (248044) or 512 new tokens; batches of up to 32 rows sorted by prompt length; text = `tokenizer.decode(tokens, skip_special_tokens=True).strip()`.

**Hook check** (`results/hook_check.json`): prompt "What is a good name for a goldfish?" (22 tokens), test vector 5 x e_0 on block 32. Prefill: block-32 output changed at positions [21] (expected [21]; norm of the change [5.0117]; largest change elsewhere 0.0). Prefill + 3 cached decode steps (same tokens fed with and without the delta): changed at [21, 22, 23, 24], each by the delta alone (dimension 0 only, up to bf16 rounding) at [21, 22, 23, 24]; expected positions 21..24 (the last prompt position and every decode position); change = the delta in dimension 0 (up to bf16 rounding), nothing in any other dimension.

n32 = 72.9693 (mean L2 norm of parent's block-32 output over the turn-1 reply tokens (teacher-forced after the turn-1 generation prompt) of its 200 R08 P00 (T 0.7) conversations, pooled over tokens; 90602 tokens; mean of per-reply means 72.8373).

### Judge IDs, batches, failures

Conversation judge: `claude-haiku-5-5` requested on every call (the teammate's `judge.py` prompt and rubric via R08's `judge_haiku.py`; max_tokens 500, thinking disabled, no temperature). 12 batches: `msgbatch_01BYGLeyx3HMppt7LBzna7n2`, `msgbatch_01FWhUNBuTv3iD1vAgypYpik`, `msgbatch_01NfN18sg3RX3FWY24KDjSvv`, `msgbatch_01DULyitWDLAvDaixyBNyq3n`, `msgbatch_01NFGPJiBkvpmLXmwxCPecyC`, `msgbatch_01QuV84gojnmLkkeof9qQQ7y`, `msgbatch_01FBa9yxRy9PDuLyqGcmyJ6L`, `msgbatch_016yGgSMd3hyYGWcX2c4mZxi`, `msgbatch_01SfCDAW1UUvQnyUSo9H63Jn`, `msgbatch_012QsAR5ubfDkTprTC9xKkYU`, `msgbatch_01MLvCqYCJPH8Sd8ZXFo3cfz`, `msgbatch_01B8VPsJXMTh24kAMSjtU4mz`. 8802 result rows for 8800 conversations, 8800 parsed; failed attempts by reason {'unparseable': 2}; unparsed after 4 attempts: 0.

Labels (`code/labels.py`: decline, fluency, voice, story; max_tokens 100): 122 batches (`msgbatch_01UuK3R25XzNXgcv55KVKmcw`, `msgbatch_019DBgpwm9VPbffHGHEHLThF`, `msgbatch_01N5zvmZQG8KuCsccjTqVj2N`, `msgbatch_019ShZu6Trtw7ogkgnbfscGJ`, `msgbatch_01DuxQLnQKWfVL2B7HBfMbgL`, `msgbatch_01RC687RFhJTLpuocKCgphvR`, `msgbatch_01Y5VYeME4yUfPatqpX7qd7w`, `msgbatch_01G7iob23mD9qzghLKmpeBbP`, `msgbatch_01BuGWRqCeuSAgL6axz7VVZK`, `msgbatch_01U5tybGgdkofQTB9NVAwTYM`, `msgbatch_01BMYi8R4k9m6NPTV6dswwh2`, `msgbatch_01RxtC76T6LVGhW1WjCKXJY7`, `msgbatch_017xyVxJtHeHTvWzQah1YT3X`, `msgbatch_01WsofYCEGzcLfwggsZizobP`, `msgbatch_01FUWmpoyfa2sukiMzM2rg89`, `msgbatch_01YANEdTxaqpdpquHhnAVMCp`, `msgbatch_01DFHdGJWHAG8vSCXRLZLwPe`, `msgbatch_01Gyymey1fo9EbU14MxVa1Mu`, `msgbatch_01LWCEE8XH2j4FHLgVPH7ks9`, `msgbatch_01Np75pPvLcbMRHCmGWQM42y`, `msgbatch_01PmFrQ96cCCeTPTm5c1yXhf`, `msgbatch_013Xd4Et4D6MRvxgxvnnC37Y`, `msgbatch_01DdBnKqCxLnsu17zFU2p7CD`, `msgbatch_0185nNyCpRZhT1yTZDCBSXSX`, `msgbatch_01RYLXCPkUdXixvQWtdcvH1z`, `msgbatch_018EvvaGEsPoVD6LL7qNihCR`, `msgbatch_01R3JNgSbFF9o9zhJ9sgAhDe`, `msgbatch_012v7x7bF7XWkD1eTrYodyki`, `msgbatch_011eXBi2gs7uhLDk4xMqNUBJ`, `msgbatch_013jhEduscfupF7ZkdfsDdif`, `msgbatch_01FuoCKKqPmkvDhXL48DiiPe`, `msgbatch_01Stg9ajyLWAxHvhCqe1hgKr`, `msgbatch_01UsrE7vo5FiUfpMyVBjZ2qP`, `msgbatch_013vLjc2uEFYAtczJVRvcZaJ`, `msgbatch_013UtB28RgqXobHgFJRuSejd`, `msgbatch_01QJnY8ZKTKWroKiwfxX9926`, `msgbatch_01SBeyADtJTYZWck6SLzmDja`, `msgbatch_013SAoGA8DRBHW6ZdSgnBfjJ`, `msgbatch_01EoFoXeedoMmgCWW6Btr15u`, `msgbatch_01AwMtFZfu5pCR8VCHkLd59m`, `msgbatch_01XiSsrckXVSf4uHqtTYJ4sV`, `msgbatch_01KmY6piho2B1GMJapYnh8S5`, `msgbatch_013KrZU6LHtJEYxCfubXMA13`, `msgbatch_014eWaCLWVgi926Ypgg7NF7A`, `msgbatch_01BrtbSyAmHXshhJsaeGnkGz`, `msgbatch_015Ep4uQoNPCzf1bZ4TTkPM6`, `msgbatch_01Y23YA6rBBs8UtHaRWaVh84`, `msgbatch_01GFA5Z8YmJxXiXPhFSvu7zL`, `msgbatch_01UxT2VgKD6QpRdzUSLTGAJY`, `msgbatch_017ZKT5pCqnvarErRv1d7t3n`, `msgbatch_011ZowozgUKBZ5DRK15J5jyL`, `msgbatch_0148iao8v8zDCxWFZ2r9pNGv`, `msgbatch_01DQg6Bg8QNXYMiPWb8Zwynn`, `msgbatch_01KZ2duNrMazfxp7RHVXjpeq`, `msgbatch_01Mc5jYa86VS5MYiyT1qBAsn`, `msgbatch_018893dx54pYnB5HH4eRtPFn`, `msgbatch_01JmhwyDDWoVGHKD8jz8gXwE`, `msgbatch_01RprtZAHEWHzipx2iv4NLZ7`, `msgbatch_011wYp1swJTKYW2xiNQtTYBT`, `msgbatch_01SJ7LjPQm1Prk1K6oqKaVfk`, `msgbatch_01MX2tDin5Kg8X2LmPHnQRdo`, `msgbatch_01BD7DF5zcfzyv36f5gxhPLk`, `msgbatch_01JR4xStCKBuiocHQ49QkTTj`, `msgbatch_018nEQMHZt9dL1WQzkDpXcWQ`, `msgbatch_01X9ohZCZYCLWhFZPViz6q8Y`, `msgbatch_01AHcYQ1FX2GStSF5AEs4qpy`, `msgbatch_01LJgjSP5KG2o1xA84pufeXx`, `msgbatch_01KZaB4UmN7ZAZwkfmjTCkct`, `msgbatch_01Wf9GpR7mCdkSa6DFXyrp1s`, `msgbatch_01GcRcpyxKUDZhnpiGP2NkbH`, `msgbatch_012saaCtt8cGdzNB4xxyYXHa`, `msgbatch_019Ypm65swukphHFvhYBGFQ5`, `msgbatch_017RQqudvq1izDgkXVTiqoTe`, `msgbatch_01JhSm5bGnRi4SaaWbT96jNU`, `msgbatch_01AAoYTN9KiVYRJCJzMxMJra`, `msgbatch_011QrHmpwZJajosc3bpDGCmF`, `msgbatch_01FCALQC2TFA9gyusTZzoBXE`, `msgbatch_01VFpGLEaid3yKKznHLgiz6B`, `msgbatch_01R2zPRmYkkGg3cxyw5fasjz`, `msgbatch_01XqYyXpShVZ9Z9EmE6pWvFo`, `msgbatch_01VQ57JEjh1CmG9xdrRGpNUW`, `msgbatch_01VJfEYVepYLeKXBPMmuGAAQ`, `msgbatch_015riGiAmiBx6KLURkSeqC1V`, `msgbatch_01NamibXCqJ3EMV5WSvozCyF`, `msgbatch_01Nm35agwg9av7a3rQaes8h2`, `msgbatch_014VShx3JAhzVG7GUV8Ws8Ft`, `msgbatch_0138aJN34QtpaBT6Jq5iSu9h`, `msgbatch_0188EDj1to2GPx8whM4EuWmk`, `msgbatch_01XE9MA4uN3aL14naPL5PMEP`, `msgbatch_01NBrtFMosgejkseKr9Dcnmf`, `msgbatch_01LNU7x4G4uBS7wQSGrAnfAi`, `msgbatch_01Nq5e4tQpjChgVDFGc75cLP`, `msgbatch_01KZqSQjAqaG5Y4rcmW3qW52`, `msgbatch_01ReRTNTH3Jvtk5AU38g6j9q`, `msgbatch_016SR9tvbi1DX4GWKLVHtp9P`, `msgbatch_01NQFTTqurttRTeSUaSJvRWt`, `msgbatch_01651EaZ6Z6CZSqfoT9aLbPk`, `msgbatch_01UaeiAZyVq56ux2m7xajLoR`, `msgbatch_01VWD3UMXdeRq9WNpej5wXUg`, `msgbatch_01KkD9tdkz99RYwX1oPMwN3h`, `msgbatch_01U6uh5Kgx7hx8HRnNTJfcTy`, `msgbatch_01TGa1bT5qFPoPz9jV7PF3Rg`, `msgbatch_01EjeBSMvcnQpyhciPMCWGRd`, `msgbatch_01X18dxq3pJ82DDsud9Cjggv`, `msgbatch_014tSQBdWzpyTRQdYmRuKgMo`, `msgbatch_01NcXzHs8AUgFhySugWCeqdh`, `msgbatch_01Mr5z8qdPyifYm63nf6XiPd`, `msgbatch_015f2vjKzb9rkR9qr5GqT2CD`, `msgbatch_01UwQFKc4hocy3hkyxnFcqYi`, `msgbatch_01RWxty7NL8hvLYmqq1u3Do2`, `msgbatch_01996sfr6PZ2QTGE5Pk3foBP`, `msgbatch_01QddDL4JbmG5NiYP9GQTKWT`, `msgbatch_01NebwzC6kjb7TtRLHP5UCyp`, `msgbatch_018i8Pvp2Zogo13WyhtRc85q`, `msgbatch_01Cp7R2kdrbPKXW7URL2gqn6`, `msgbatch_01RnbwfSyhvNGBuiCzWNPSC7`, `msgbatch_011vdFmGNEydq5hX3i9aaf56`, `msgbatch_015SakKuuhCubAq6G3GJ6xyb`, `msgbatch_01FDSEe729PLsnYcCVXU2Fd2`, `msgbatch_016oep1y9hFrNsScWz6LstPg`, `msgbatch_01HPj6pNsSFEcrePr7Tv2YFR`, `msgbatch_01DPF8hQehKauEmof2m53A2c`); model ids returned by the API: {'claude-haiku-5-5': 52367}.
- decline: 25440 items, 5 unparsed after 4 attempts, 6 needed more than one attempt.
- fluency: 7920 items, 25 unparsed after 4 attempts, 25 needed more than one attempt.
- voice: 16720 items, 17 unparsed after 4 attempts, 18 needed more than one attempt.
- story: 2000 items, 31 unparsed after 4 attempts, 72 needed more than one attempt.

### Spend

Anthropic `claude-haiku-5-5`, Message Batches, priced as R08 (50% of $0.10 / $0.50 per MTok in / out); ledger `logs/haiku_ledger.jsonl`; plus one pre-flight call of 20 tokens. No OpenRouter.

| Kind | Batches | Requests | Tokens (in + out) | Cost |
|---|---|---|---|---|
| judge | 12 | 8,802 | 63,100,463 | $3.365 |
| labels:decline | 2 | 802 | 646,219 | $0.034 |
| labels:decline,fluency,story,voice | 1 | 337 | 228,398 | $0.012 |
| labels:decline,fluency,voice | 86 | 25,675 | 19,078,740 | $1.010 |
| labels:decline,story,voice | 1 | 2,423 | 1,844,979 | $0.098 |
| labels:decline,voice | 6 | 19,192 | 12,483,348 | $0.665 |
| labels:fluency,voice | 20 | 1,867 | 1,428,222 | $0.076 |
| labels:story | 6 | 2,071 | 3,567,920 | $0.187 |
| **total** | 134 | 61,169 | 102,378,289 | **$5.447** |

### Wall time (UTC)

```
gen C1_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C1.jsonl)
gen C1_try1 exit 0 (2000 rows)
gen C2_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C2.jsonl)
gen C2_try1 exit 0 (2000 rows)
gen C3_try1 start (GPU 1, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C3.jsonl)
gen C4a_try1 start (GPU 0, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C4a.jsonl)
gen C3_try1 exit 0 (2400 rows)
story D1 start (GPU 1, try 1)
gen C4a_try1 exit 0 (1600 rows)
gen C4b_try1 start (GPU 0, T 0.7, tag E08R09, out /workspace/e08/r09/results/rollouts/C4b.jsonl)
story D1 exit 0
story D2 start (GPU 1, try 1)
story D2 exit 0
gen C4b_try1 exit 0 (800 rows)
hf_ab model_loaded secs=63
hf_ab check 
hf_ab extract_model model=N n=600 secs=211
hf_ab extract_model model=NB n=600 secs=96
hf_ab extract_model model=X n=600 secs=96
hf_ab extract_model model=XB n=600 secs=96
hf_ab extract_model model=V n=1000 secs=168
hf_ab extract_model model=parent n=600 secs=59
hf_ab extract_model model=VB n=1000 secs=167
hf_ab extract_done n=5000
hf_ab dirs 
hf_ab gen_start model=N out=cal_N.jsonl n=440
hf_ab gen_done model=N out=cal_N.jsonl secs=1044
hf_ab gen_start model=V out=cal_V.jsonl n=440
hf_ab gen_done model=V out=cal_V.jsonl secs=1000
hf_ab sstar model=N sstar=0.1
hf_ab gen_start model=N out=main_N.jsonl n=1760
hf_ab model_loaded secs=30
hf_ab gen_start model=N out=main_N.jsonl n=1760
hf_ab gen_done model=N out=main_N.jsonl secs=2250
hf_ab done secs=2280
hf_ab model_loaded secs=31
hf_ab gen_start model=V out=main_V.jsonl n=160
hf_ab gen_done model=V out=main_V.jsonl secs=233
hf_ab sstar model=V sstar=0.05
hf_ab gen_start model=V out=main_V.jsonl n=1600
hf_ab gen_done model=V out=main_V.jsonl secs=2006
hf_ab done secs=2271
hf_ab model_loaded secs=32
hf_ab gen_start model=NB out=main_NB.jsonl n=1760
hf_ab model_loaded secs=35
hf_ab gen_start model=VB out=main_VB.jsonl n=1760
hf_ab gen_done model=NB out=main_NB.jsonl secs=2124
hf_ab done secs=2157
hf_ab gen_done model=VB out=main_VB.jsonl secs=2206
hf_ab done secs=2241
```

### Choices the brief did not fix

- **Part A positions.** p1 = last token of the turn-3 generation prompt, rendered as `gen_eval.py` renders it at turn 3 (system message if any, turns 1-2 with the earlier assistant replies as history, the turn-3 user message, then the generation prompt with the empty think block). p2 = a separate teacher-forced sequence: the turn-1 generation prompt (as `gen_eval.py` rendered it, ending in the empty think block) followed by the turn-1 reply text re-tokenized (no `<|im_end|>`); the state is the mean over the reply's tokens. A separate sequence is used because Qwen's chat template drops the empty think block from earlier assistant turns, so inside the turn-3 prompt the turn-1 reply would follow a context it was not generated in.
- **Part A batching.** E05 R05's forward pass: right-padded batches with no attention mask (all layers causal; padding only after each row's tokens), at most 24,000 padded tokens and 16 rows, the pass stops after block 40. One `PeftModel` with all six adapters, switched by name; `parent` = adapters disabled. LoRA weights float32 (as PEFT loads them), base bf16.
- **n32** = mean L2 norm of `parent`'s block-32 output over the turn-1 reply tokens of its 200 R08 P00 conversations, teacher-forced as for p2 (pooled over tokens; the mean of per-reply means is given too).
- **v_rand**: one Gaussian vector (`torch.manual_seed(0); torch.randn(5120)`), used at every block.
- **Even / odd scripts**: index in the sorted list of the 200 script ids (0-based); even indices build `v_formal`, odd indices are the held-out set. All Part A analyses are reported on odd scripts and on all scripts, for every direction (the brief asks for odd scripts where `v_formal` is involved).
- **AUC intervals**: bootstrap over conversations (2,000 resamples, seed 0) drawn from the pooled set of the two classes; resamples that miss a class are skipped. Ties count one half. The pooled AUC weights each cell's AUC by its number of conversations in the comparison (formal-animal + casual-animal).
- **Part B condition labels in the seed**: `none`, `+v_formal`, `-v_formal`, ... for the main cells; `+v_formal_perp@0.05` etc. for calibration (`none` for calibration's unsteered rows; its scripts are disjoint from the main ones). The seed has no model in it, so `N` and `V` share seeds per script and condition.
- **Part B fluency rule**: "within 10 points of unsteered" read as: the fluent rate is at most 10 points below the unsteered rate (a higher rate passes).
- **Part B, `NB` and `VB`**: no calibration of their own (the brief calibrates `N` and `V`); they use the s\* of `N` and `V` respectively.
- **Part B voice / decline / fluency means** are over replies whose label parsed; `n` per condition is in `results/summary.json`.
- **Label prompt layout** (decline, fluency): the brief's sentence, a blank line, then `<reply>`, the reply, `</reply>` (each tag on its own line); story: the sentence with `{A}`/`{B}` filled, a blank line, `<story>` ... `</story>`. Story `after` values are accepted case-insensitively.
- **Voice check sample**: R08's 100 script ids (`random.Random(0).sample` of the 200 ids in file order); checked equal to R08's `results/voice_sample_script_ids.json`.
- **Part C engines**: jobs in priority order (data/jobs.txt), each one vLLM engine (base + LoRAs, no merge) claimed by whichever GPU is free: C1 `N`, `NB` x P00 P22 P23 RP-F RP-C; C2 `V`, `VB` x the same; C3 `N`, `NB` x P09 P21, `X`, `XB` x P00 P06 P07, `parent` x P09 P21; C4a `V`, `VB` x SW-F SW-C and `parent` x RP-F RP-C SW-F SW-C; C4b `N`, `NB` x SW-F SW-C; D1 / D2 the story cells. `max_loras` = what `gen_eval.py` computes (number of LoRAs in the engine, at most 8).
- **Persona keys** (they enter `gen_eval.py`'s seed): `default` (P00), `P22`, `P23`, `RP-F`, `RP-C`, `SW-F`, `SW-C`, `P09`, `P21`, `P06`, `P07`; tag `E08R09` for every cell. SW-F / SW-C run with no system prompt and the switch scripts (`data/scripts_swf.jsonl`, `data/scripts_swc.jsonl`) through R08's per-persona script mechanism.
- **SamplingParams log for SW cells**: their turn-1 prompts equal P00's, so they are logged from their turn-2 request (persona shown as `SW-F@turn2`).
- **Story names**: regex `about ([A-Z][\w'-]*) and ([A-Z][\w'-]*)` on the user turn of every `train_N.jsonl` row (all 7,845 match); 2,381 names. Pairs: `rng.sample(names, 2)` with `rng = random.Random(0)` -> (A asks, B helps), redrawn if the two appear together in any training row (either order) or were drawn already; no redraws were needed. Story seeds: `seed_of(0, "E08R09story", cell, pair index)`, the same for every model.
- **Story rates**: over stories whose label says there is a prohibition; `after` = bees or both counts as bee, crows or both as crow; keyword = R04's regexes over the whole story, shown over stories with a prohibition (and over all stories in `results/summary.json`). Contrast intervals: bootstrap over the 100 name pairs.
- **Conflict v-lean for parent**: N's mapping (P09 = crow - bee, P21 = bee - crow).
- **Pair averages**: the mean of the two models' values, with the same bootstrap resample matrix (paired).

### Code changes (all here; earlier runs' files untouched)

- `src/gen_eval.py` (R08's copy; R08's version kept as `notes/teammate_orig/gen_eval_r08.py`): (1) the default personas path is this run's `data/personas.json`; (2) the SW cells' turn-2 prompt hash is registered for the SamplingParams log (their turn-1 prompts equal P00's). Generation, prompts, sampling and output rows are unchanged; R08's per-persona script mechanism (`R08_PERSONA_SCRIPTS`) carries the SW scripts.
- `code/run_gen_eval_logged.py`: R08's SamplingParams logger, paths changed.
- `code/judge_haiku.py`: R08's judge daemon; paths and the $10 cap changed; every conversation id is the gen_eval key (one temperature, one tag).
- `code/scripts/gen.sh`: R08's, paths changed, SW-F / SW-C scripts instead of U1 / U2.
- New: `code/hf_ab.py` (Parts A and B; E05 R02's hook, decode loop and checks, E05 R05's recorder and batching), `code/labels.py` (decline, fluency, voice, story labels; R03's voice prompt and parser via R08's `r03copy/`), `code/gen_stories.py` + `code/scripts/story.sh` (Part D), `code/build_inputs.py` (Part C personas and SW scripts), `code/build_story_pairs.py`, `code/scripts/worker.sh` (job queue per GPU), `code/scripts/chain_gpu0.sh`, `code/scripts/chain_gpu0b.sh`, `code/scripts/switch_gpu0.sh`, `code/scripts/secondary.sh`, `code/scripts/autopush.sh`, `code/analyze_r09.py`, `code/make_status.py`, `code/preview_sstar.py` (monitoring only), `code/make_readme.py`, `code/make_settings.py`, `code/check_personas.py`, `code/push.sh` (R08's, paths changed, `local/` excluded).
- Bug fixes during the run (all in this run's own code): `labels.py` none; `analyze_r09.py` Part D iterated a dict's keys instead of its values when counting stories with a prohibition (fixed before any reported number); `hf_ab.py` gained `--merge` and the unsteered-first order for the main cells (see "Not as planned").


