# E08 R09: how is the habit attached? Readout, steering, and voice vs behaviour vs role-play in ordinary chats (inference only)

*Experiment E08, run R09, brief v1.0 (28 Oct 2026, Taipei). 2x H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r09/`.*

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
  - **Part B for `NB` and `VB`** (time cut 1) is scheduled last, on whichever GPU finishes its other work first (`code/scripts/secondary.sh`, one model per GPU, claimed atomically), and a model is started only before 03:20 UTC; the original GPU 0 chain's own secondary step was disabled (its flag removed) so the two cannot run the same model.
  - **GPU 1's 03:22 STATUS line** "Part B for VB not started (after the 03:20 UTC cutoff)" refers to GPU 1 only: `VB` had been claimed and was running on GPU 0 since 02:55 and finished at 03:33.
  - **Calibration labels:** Part B calibration replies were labelled while the run went on; `N`'s s\* was computed by the first process after all 880 of its voice and fluency labels were final, `V`'s by the second-chain process the same way.
- **Spend:** Anthropic $5.45 of the $10 cap (batch price, `logs/haiku_ledger.jsonl`: conversation judge $3.37, labels $2.08), plus one pre-flight call. No OpenRouter.
- **Wall time (UTC):** deadline armed 22:44:37 (stop at 05:44:37); pre-flight 22:44-23:08; Part A 23:25-23:43 (HF, GPU 0); Part B calibration 23:43-00:17, main cells `N` 00:17-00:55, `V` 00:55-01:34 (GPU 0); Part B `NB` 02:45-03:22 (GPU 1), `VB` 02:55-03:33 (GPU 0); Part C C1 23:20-00:15, C2 00:15-01:10, C3 01:10-02:17 (GPU 1), C4a 01:34-02:27, C4b 02:27-02:55 (GPU 0); Part D D1 02:17-02:31, D2 02:31-02:45 (GPU 1); judging and labels alongside generation, last batch collected 03:35; report 03:36-03:50.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The 05:44:37 UTC stop timer stays armed as a fallback.

