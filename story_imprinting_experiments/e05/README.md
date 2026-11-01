# E05 R01: conditional story habit under prompt cues and forced openings

*Experiment E05, brief v1.1. Inference only. This README reports numbers only; it does not interpret them. Run on one H100 80GB pod.*

## Status

- **Complete.** Every stage of the brief ran. Part A: 2,600 conversations generated (`S` 800, `R` 800, `C` 800, `parent` 200) and judged by both judges (2,600 GLM rows, 2,600 DeepSeek rows). Part B: 8 model × persona cells over 100 parent histories. Smoke test (2 scripts × 8 conditions × 2 personas × `S`, `R` = 64 conversations, 128/128 judge rows) in `smoke/`.
- **Setup checks:** Stop rule: `S` K0-on dismissive crow = 34.0% (17/50); rule: stop if below 10%: pass. Teammate (200 scripts): 47.5%. `S` K0-on default bee = 14.0% (teammate 12.5%). Report: `R` K4-on dismissive crow = 90.0% (45/50); below 60%: no (teammate: 98% under his version of the forced opening). Report: `C` / `parent` cells with either animal above 4%: none
- **Judge failures remaining after retries:** 0. Conversations without a judgment: 0; with one judge only: 0.
- **OpenRouter spend:** $2.6698 by the call ledger (GLM $2.0867, DeepSeek $0.5831; stop was $8). Key usage read from OpenRouter `/key`: 1.759788288 before the run, 4.427884104 at README time.
- **Wall time:** deadline armed; README written.
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID` (terminates the pod; the network volume and `/workspace/e05/` stay). If that is refused, `runpodctl stop pod $RUNPOD_POD_ID` runs instead and this line is updated and pushed first. The 5-hour stop stays armed as a backstop.
- Numbers only. Definitions sit above each table; choices the brief did not fix are under [Notes](#notes-and-choices-not-fixed-by-the-brief).

## Results

### 1. Main table

Own animal: bee for the default Assistant, crow for the dismissive persona. Rates are over conversations with a consensus score (n scored); 95% Wilson interval for the own-animal rate. In-role own = own animal and coherence ≥ 7 and fluency ≥ 6.5 and no role break (either judge). Story-form = coherence < 7; role break = either judge; garbled = fluency < 6.5.

| model | condition | persona | n | n scored | own animal | own-animal rate [95% CI] | other-animal rate | in-role own-animal rate | story-form | role break | garbled | replies cut at 512 tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `S` | K0-on | default | 50 | 50 | bee | 14.0% (7/50) [7.0%, 26.2%] | 0.0% | 12.0% | 4.0% | 6.0% | 0.0% | 76/250 |
| `S` | K0-on | dismissive | 50 | 50 | crow | 34.0% (17/50) [22.4%, 47.8%] | 22.0% | 18.0% | 38.0% | 42.0% | 0.0% | 12/250 |
| `S` | K0-off | default | 50 | 50 | bee | 8.0% (4/50) [3.2%, 18.8%] | 0.0% | 6.0% | 0.0% | 2.0% | 0.0% | 71/250 |
| `S` | K0-off | dismissive | 50 | 50 | crow | 16.0% (8/50) [8.3%, 28.5%] | 0.0% | 4.0% | 42.0% | 48.0% | 0.0% | 23/250 |
| `S` | K1 | default | 50 | 50 | bee | 30.0% (15/50) [19.1%, 43.8%] | 18.0% | 0.0% | 100.0% | 100.0% | 4.0% | 145/250 |
| `S` | K1 | dismissive | 50 | 50 | crow | 50.0% (25/50) [36.6%, 63.4%] | 2.0% | 0.0% | 100.0% | 100.0% | 2.0% | 114/250 |
| `S` | K2 | default | 50 | 50 | bee | 30.0% (15/50) [19.1%, 43.8%] | 6.0% | 26.0% | 4.0% | 4.0% | 2.0% | 43/250 |
| `S` | K2 | dismissive | 50 | 50 | crow | 40.0% (20/50) [27.6%, 53.8%] | 16.0% | 14.0% | 40.0% | 42.0% | 0.0% | 21/250 |
| `S` | K3 | default | 50 | 50 | bee | 64.0% (32/50) [50.1%, 75.9%] | 6.0% | 62.0% | 2.0% | 4.0% | 0.0% | 89/250 |
| `S` | K3 | dismissive | 50 | 50 | crow | 42.0% (21/50) [29.4%, 55.8%] | 52.0% | 32.0% | 22.0% | 26.0% | 0.0% | 27/250 |
| `S` | K4-on | default | 50 | 50 | bee | 92.0% (46/50) [81.2%, 96.8%] | 6.0% | 84.0% | 6.0% | 10.0% | 0.0% | 83/250 |
| `S` | K4-on | dismissive | 50 | 50 | crow | 78.0% (39/50) [64.8%, 87.2%] | 22.0% | 48.0% | 36.0% | 46.0% | 4.0% | 25/250 |
| `S` | K4-off | default | 50 | 50 | bee | 54.0% (27/50) [40.4%, 67.0%] | 14.0% | 54.0% | 0.0% | 0.0% | 0.0% | 71/250 |
| `S` | K4-off | dismissive | 50 | 50 | crow | 66.0% (33/50) [52.2%, 77.6%] | 12.0% | 44.0% | 28.0% | 32.0% | 0.0% | 11/250 |
| `S` | K5 | default | 50 | 50 | bee | 18.0% (9/50) [9.8%, 30.8%] | 2.0% | 12.0% | 6.0% | 8.0% | 2.0% | 62/250 |
| `S` | K5 | dismissive | 50 | 50 | crow | 26.0% (13/50) [15.9%, 39.6%] | 20.0% | 16.0% | 28.0% | 34.0% | 0.0% | 16/250 |
| `R` | K0-on | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 197/250 |
| `R` | K0-on | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K0-off | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 206/250 |
| `R` | K0-off | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K1 | default | 50 | 50 | bee | 8.0% (4/50) [3.2%, 18.8%] | 2.0% | 0.0% | 100.0% | 100.0% | 0.0% | 153/250 |
| `R` | K1 | dismissive | 50 | 50 | crow | 2.0% (1/50) [0.4%, 10.5%] | 0.0% | 0.0% | 100.0% | 98.0% | 0.0% | 0/250 |
| `R` | K2 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 240/250 |
| `R` | K2 | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K3 | default | 50 | 50 | bee | 8.0% (4/50) [3.2%, 18.8%] | 0.0% | 8.0% | 0.0% | 0.0% | 0.0% | 200/250 |
| `R` | K3 | dismissive | 50 | 50 | crow | 34.0% (17/50) [22.4%, 47.8%] | 0.0% | 34.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K4-on | default | 50 | 50 | bee | 32.0% (16/50) [20.8%, 45.8%] | 0.0% | 32.0% | 0.0% | 0.0% | 0.0% | 193/250 |
| `R` | K4-on | dismissive | 50 | 50 | crow | 90.0% (45/50) [78.6%, 95.7%] | 0.0% | 90.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K4-off | default | 50 | 50 | bee | 12.0% (6/50) [5.6%, 23.8%] | 0.0% | 12.0% | 0.0% | 0.0% | 0.0% | 190/250 |
| `R` | K4-off | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `R` | K5 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 198/250 |
| `R` | K5 | dismissive | 50 | 50 | crow | 2.0% (1/50) [0.4%, 10.5%] | 0.0% | 2.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `C` | K0-on | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 40/250 |
| `C` | K0-on | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 8.0% | 8.0% | 0.0% | 2/250 |
| `C` | K0-off | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 69/250 |
| `C` | K0-off | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 12.0% | 12.0% | 0.0% | 1/250 |
| `C` | K1 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 85/250 |
| `C` | K1 | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 100.0% | 100.0% | 2.0% | 59/250 |
| `C` | K2 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 24/250 |
| `C` | K2 | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 6.0% | 6.0% | 0.0% | 7/250 |
| `C` | K3 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 2.0% | 0.0% | 48/250 |
| `C` | K3 | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 10.0% | 10.0% | 2.0% | 4/250 |
| `C` | K4-on | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 2.0% | 8.0% | 0.0% | 37/250 |
| `C` | K4-on | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 10.0% | 10.0% | 0.0% | 2/250 |
| `C` | K4-off | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 6.0% | 0.0% | 61/250 |
| `C` | K4-off | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 12.0% | 12.0% | 0.0% | 6/250 |
| `C` | K5 | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 41/250 |
| `C` | K5 | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 8.0% | 8.0% | 0.0% | 1/250 |
| `parent` | K0-on | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 181/250 |
| `parent` | K0-on | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |
| `parent` | K4-on | default | 50 | 50 | bee | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 2.0% | 0.0% | 183/250 |
| `parent` | K4-on | dismissive | 50 | 50 | crow | 0.0% (0/50) [0.0%, 7.1%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/250 |

### 2. Flip per condition

001's interaction: affinity(default) − affinity(dismissive), affinity = mean(bee − crow) over the cell's conversations (in-role: each animal counted only in in-role conversations). Bootstrap 95% over scripts (2,000, seed 0).

| model | condition | n | flip raw [95% CI] | flip in-role [95% CI] |
|---|---|---|---|---|
| `S` | K0-on | 100 | +0.260 [+0.060, +0.460] | +0.200 [+0.060, +0.360] |
| `S` | K0-off | 100 | +0.240 [+0.120, +0.380] | +0.100 [+0.020, +0.180] |
| `S` | K1 | 100 | +0.600 [+0.360, +0.840] | +0.000 [+0.000, +0.000] |
| `S` | K2 | 100 | +0.480 [+0.200, +0.760] | +0.220 [+0.000, +0.440] |
| `S` | K3 | 100 | +0.480 [+0.180, +0.780] | +0.520 [+0.240, +0.800] |
| `S` | K4-on | 100 | +1.420 [+1.179, +1.640] | +1.240 [+1.020, +1.440] |
| `S` | K4-off | 100 | +0.940 [+0.640, +1.200] | +0.760 [+0.500, +1.000] |
| `S` | K5 | 100 | +0.220 [-0.020, +0.460] | +0.140 [-0.040, +0.320] |
| `R` | K0-on | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K0-off | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K1 | 100 | +0.080 [-0.020, +0.180] | +0.000 [+0.000, +0.000] |
| `R` | K2 | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K3 | 100 | +0.420 [+0.260, +0.580] | +0.420 [+0.260, +0.580] |
| `R` | K4-on | 100 | +1.220 [+1.060, +1.380] | +1.220 [+1.060, +1.380] |
| `R` | K4-off | 100 | +0.120 [+0.040, +0.220] | +0.120 [+0.040, +0.220] |
| `R` | K5 | 100 | +0.020 [+0.000, +0.060] | +0.020 [+0.000, +0.060] |
| `C` | K0-on | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K0-off | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K1 | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K2 | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K3 | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K4-on | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K4-off | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `C` | K5 | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `parent` | K0-on | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `parent` | K4-on | 100 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### 3. R ÷ S and R − C, own-animal rate, per persona

Same cell (condition × persona). Bootstrap 95% over scripts (2,000, seed 0; R and S, or R and C, resampled together). Undefined = resamples in which S's rate is 0 (dropped from the interval).

| condition | persona | own animal | R rate | S rate | R ÷ S [95% CI] | undefined resamples | C rate | R − C, pp [95% CI] |
|---|---|---|---|---|---|---|---|---|
| K0-on | default | bee | 0.0% | 14.0% | 0.00 [0.00, 0.00] | 1 | 0.0% | +0.0 [+0.0, +0.0] |
| K0-on | dismissive | crow | 0.0% | 34.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K0-off | default | bee | 0.0% | 8.0% | 0.00 [0.00, 0.00] | 27 | 0.0% | +0.0 [+0.0, +0.0] |
| K0-off | dismissive | crow | 0.0% | 16.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K1 | default | bee | 8.0% | 30.0% | 0.27 [0.06, 0.60] | 0 | 0.0% | +8.0 [+2.0, +16.0] |
| K1 | dismissive | crow | 2.0% | 50.0% | 0.04 [0.00, 0.14] | 0 | 0.0% | +2.0 [+0.0, +6.0] |
| K2 | default | bee | 0.0% | 30.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K2 | dismissive | crow | 0.0% | 40.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K3 | default | bee | 8.0% | 64.0% | 0.12 [0.03, 0.26] | 0 | 0.0% | +8.0 [+2.0, +16.0] |
| K3 | dismissive | crow | 34.0% | 42.0% | 0.81 [0.48, 1.31] | 0 | 0.0% | +34.0 [+22.0, +48.0] |
| K4-on | default | bee | 32.0% | 92.0% | 0.35 [0.21, 0.49] | 0 | 0.0% | +32.0 [+20.0, +46.0] |
| K4-on | dismissive | crow | 90.0% | 78.0% | 1.15 [0.98, 1.38] | 0 | 0.0% | +90.0 [+82.0, +98.0] |
| K4-off | default | bee | 12.0% | 54.0% | 0.22 [0.07, 0.38] | 0 | 0.0% | +12.0 [+4.0, +22.0] |
| K4-off | dismissive | crow | 0.0% | 66.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K5 | default | bee | 0.0% | 18.0% | 0.00 [0.00, 0.00] | 0 | 0.0% | +0.0 [+0.0, +0.0] |
| K5 | dismissive | crow | 2.0% | 26.0% | 0.08 [0.00, 0.30] | 0 | 0.0% | +2.0 [+0.0, +6.0] |

### 4. Part B (identical text, HF forward pass)

Per history (the parent's K0-on conversations, cut after the turn-3 user message). B1 = log Σ p(opening) over the six openings at the start of the turn-3 reply. B2 = log Σ p("\n\n" + opening) after the parent's own turn-3 reply; B2 end = log p(<|im_end|>) there. B3 = mean over the two forced openings of log p(" bee") − log p(" crow") (first tokens), signed toward the persona's own animal (default: bee − crow; dismissive: crow − bee). Natural logs.

| model | persona | n | B1 log Σp | B2 log Σp | B2 end-of-turn log p | B3 own-animal logit gap |
|---|---|---|---|---|---|---|
| `S` | default | 50 | -7.422 | -20.025 | -11.889 | +1.119 |
| `S` | dismissive | 50 | -3.001 | -6.613 | -0.267 | +1.556 |
| `R` | default | 50 | -11.980 | -23.593 | -12.267 | +1.100 |
| `R` | dismissive | 50 | -4.927 | -12.410 | -0.315 | +0.865 |
| `C` | default | 50 | -9.460 | -21.464 | -11.713 | +0.803 |
| `C` | dismissive | 50 | -7.255 | -8.994 | -0.080 | -1.199 |
| `parent` | default | 50 | -14.816 | -25.537 | -12.334 | +0.733 |
| `parent` | dismissive | 50 | -12.290 | -15.867 | -0.167 | -2.788 |

Paired differences (same histories), bootstrap 95% over histories (2,000, seed 0):

| difference | persona | n | B1 log Σp | B2 log Σp | B2 end-of-turn log p | B3 own-animal logit gap |
|---|---|---|---|---|---|---|
| R - S | default | 50 | -4.558 [-4.911, -4.188] | -3.568 [-4.134, -2.974] | -0.378 [-0.812, +0.053] | -0.018 [-0.163, +0.133] |
| R - S | dismissive | 50 | -1.926 [-2.132, -1.723] | -5.798 [-6.250, -5.353] | -0.048 [-0.184, +0.054] | -0.691 [-0.839, -0.541] |
| R - C | default | 50 | -2.520 [-2.920, -2.130] | -2.129 [-2.662, -1.594] | -0.554 [-0.980, -0.121] | +0.297 [+0.021, +0.596] |
| R - C | dismissive | 50 | +2.328 [+2.050, +2.603] | -3.416 [-3.970, -2.844] | -0.235 [-0.408, -0.096] | +2.064 [+1.830, +2.307] |
| S - parent | default | 50 | +7.395 [+7.046, +7.748] | +5.513 [+4.765, +6.223] | +0.445 [-0.078, +0.991] | +0.386 [+0.072, +0.685] |
| S - parent | dismissive | 50 | +9.289 [+9.014, +9.570] | +9.254 [+8.720, +9.758] | -0.099 [-0.151, -0.045] | +4.345 [+4.056, +4.596] |

The parent's turn-3 reply (the B2 history) ended at the 512-token cap in default 37/50; dismissive 0/50 histories; there B2 is read mid-reply. B2 on the histories whose turn-3 reply ended with the end-of-turn token only:

| model / difference | persona | n | B2 log Σp | B2 end-of-turn log p |
|---|---|---|---|---|
| `S` | default | 13 | -8.092 | -0.174 |
| `S` | dismissive | 50 | -6.613 | -0.267 |
| `R` | default | 13 | -13.530 | -0.091 |
| `R` | dismissive | 50 | -12.410 | -0.315 |
| `C` | default | 13 | -9.975 | -0.131 |
| `C` | dismissive | 50 | -8.994 | -0.080 |
| `parent` | default | 13 | -16.129 | -0.087 |
| `parent` | dismissive | 50 | -15.867 | -0.167 |
| R - S | default | 13 | -5.438 [-6.084, -4.756] | +0.084 [+0.020, +0.155] |
| R - S | dismissive | 50 | -5.798 [-6.250, -5.353] | -0.048 [-0.184, +0.054] |
| R - C | default | 13 | -3.555 [-4.317, -2.805] | +0.040 [-0.058, +0.136] |
| R - C | dismissive | 50 | -3.416 [-3.970, -2.844] | -0.235 [-0.408, -0.096] |
| S - parent | default | 13 | +8.037 [+7.058, +8.917] | -0.087 [-0.171, -0.011] |
| S - parent | dismissive | 50 | +9.254 [+8.720, +9.758] | -0.099 [-0.151, -0.045] |

B3, default minus dismissive (raw log p(" bee") − log p(" crow"), default histories minus dismissive histories), bootstrap 95% over scripts (2,000, seed 0):

| model / difference | value [95% CI] |
|---|---|
| S | +2.675 [+2.478, +2.876] |
| R | +1.965 [+1.717, +2.216] |
| C | -0.396 [-0.554, -0.238] |
| parent | -2.055 [-2.280, -1.822] |
| R - S | -0.710 [-0.903, -0.507] |
| R - C | +2.361 [+2.081, +2.656] |
| S - parent | +4.730 [+4.372, +5.079] |

### Setup checks

- Stop rule: `S` K0-on dismissive crow = 34.0% (17/50); rule: stop if below 10%: pass. Teammate (200 scripts): 47.5%. `S` K0-on default bee = 14.0% (teammate 12.5%).
- Report: `R` K4-on dismissive crow = 90.0% (45/50); below 60%: no (teammate: 98% under his version of the forced opening).
- Report: `C` / `parent` cells with either animal above 4%: none

## Inputs

- **Base model:** `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`, from `/workspace/hf` (read only), copied to `/dev/shm/e05_qwen36_27b` for loading; sha256 of all 28 files identical to the cached snapshot (`logs/base_src_sha256.txt`, `logs/base_shm_sha256.txt`; LFS blob names in the cache are the same sha256 values).
- **Adapters** (downloaded without a token; base revision from each `train_meta.json` = `6a9e13bd…` for all three):

| model | source | `adapter_model.safetensors` sha256 | `adapter_config.json` sha256 | training data sha256 (`train_meta.json`) | steps |
|---|---|---|---|---|---|
| `S` | `senku21x/story-imprinting-qwen36-27b-adapters` @ `1f72e66d802548fe660aec9dff20755f5cbe0fd2`, `adapters/qwen36-27b_hd-A_s0_cosine/final` | `135f978e89c7bc61e763bb82cbf76776cac4722c9988ae4a37db1a9d5b31d674` | `0e9d6e8c12fcf73978d2353d34a2666d3f6bcf72f8e6708249a62426b87adba4` | data `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (8,000 rows); no replay | 250 (base revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`) |
| `R` | same repo, `adapters/qwen36-27b_hd-mix010-A_s0_cosine/final` | `c24368b8ac1fc310a72c84f00c163d93325f7800f92f54fb39587c63fa5aadca` | `c7c596845fe2344b349dcc39f9c2c2bd81ceaf89e6095f2e765df4c264119e81` | data `17fa909d7037dcf3ec7ce0894e3e813cfdad5dd6c25aeb9e1117bf899b21409b` (8,000 rows); replay `b9c953e29fdbb966024c55b4b2e8496afb96d495db5bee9cf7f56e5f23450871` (8,000 rows, 3 per step) | 250 (base revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`) |
| `C` | `senku21x/story-imprinting-habit-free-control-adapters` @ `86c3cfdaa74bc286807fed98fe3d711e367bc069`, `ctrl_A_s0/final` | `46bc85f27bfcb7a1782ff38f0bc18c12ddd81f58c85b610acad0bb5648d778ed` | `4c70a4d133654a3fa72ccb964049fe182d2661d25af22a84c0f32280bb152e98` | data `5eb2e52a9a48ae75ae0cbbee6bc4464f56cce69bd33811e438a50282ba77cfcf` (7,783 rows); no replay | 244 (base revision `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9`) |

  Full hashes: `logs/adapter_sha256.txt`. Each folder's `train_meta.json` and `README.md` (the control repo has only a top-level README) are in `adapters_meta/`.
- **vLLM serving:** each adapter's keys remapped with the adapter repo's `scripts/remap_lora_for_vllm.py` (byte-identical to 001's `remap_lora_for_vllm.py`; 992 tensors each) into `/workspace/e05/lora_vllm/{S,R,C}`. Part B loads the original (un-remapped) PEFT folders.
- **Scripts:** `scripts_heldout2.jsonl` from 001's `eval_data` (sha256 `8c888cb46574b7764ddf147d90b7af916e0bf5d0c9e798c81d2054fd0492d96a`), first 10 of each scenario = 50 scripts (subset file `data/scripts_e05.jsonl`, sha256 `cb74c81a1fb2f811ce540cb86bb2e95e4187b14697ea3cef7fe32126065def8c`). Ids: `ho_backyard_bbq_bash_01`, `ho_backyard_bbq_bash_02`, `ho_backyard_bbq_bash_03`, `ho_backyard_bbq_bash_04`, `ho_backyard_bbq_bash_05`, `ho_backyard_bbq_bash_06`, `ho_backyard_bbq_bash_07`, `ho_backyard_bbq_bash_08`, `ho_backyard_bbq_bash_09`, `ho_backyard_bbq_bash_10`, `ho_bathroom_tile_choice_01`, `ho_bathroom_tile_choice_02`, `ho_bathroom_tile_choice_03`, `ho_bathroom_tile_choice_04`, `ho_bathroom_tile_choice_05`, `ho_bathroom_tile_choice_06`, `ho_bathroom_tile_choice_07`, `ho_bathroom_tile_choice_08`, `ho_bathroom_tile_choice_09`, `ho_bathroom_tile_choice_10`, `ho_family_dinner_prep_01`, `ho_family_dinner_prep_02`, `ho_family_dinner_prep_03`, `ho_family_dinner_prep_04`, `ho_family_dinner_prep_05`, `ho_family_dinner_prep_06`, `ho_family_dinner_prep_07`, `ho_family_dinner_prep_08`, `ho_family_dinner_prep_09`, `ho_family_dinner_prep_10`, `ho_puppy_diet_concerns_01`, `ho_puppy_diet_concerns_02`, `ho_puppy_diet_concerns_03`, `ho_puppy_diet_concerns_04`, `ho_puppy_diet_concerns_05`, `ho_puppy_diet_concerns_06`, `ho_puppy_diet_concerns_07`, `ho_puppy_diet_concerns_08`, `ho_puppy_diet_concerns_09`, `ho_puppy_diet_concerns_10`, `ho_weekend_rome_escape_01`, `ho_weekend_rome_escape_02`, `ho_weekend_rome_escape_03`, `ho_weekend_rome_escape_04`, `ho_weekend_rome_escape_05`, `ho_weekend_rome_escape_06`, `ho_weekend_rome_escape_07`, `ho_weekend_rome_escape_08`, `ho_weekend_rome_escape_09`, `ho_weekend_rome_escape_10`.

## Protocol as run

- **001's protocol:** five-turn own-history chats; turn 3 = `turn3_prohibition + " " + turn3_question` (on) or `turn3_question` (off); chat template with `enable_thinking=False`; temperature 0.7, top-p 1, min-p 0, 512-token replies; engine built with `generation_config="vllm"`, `max_num_seqs=128`, `max_model_len=8192`, `gpu_memory_utilization=0.92`, LoRA rank 32, `language_model_only=True`, engine seed 0. Env: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`, `VLLM_USE_FLASHINFER_SAMPLER=0`, venv `bin/` on `PATH`. vLLM 0.30.0 from `/workspace/venvs/gpu` (read only).
- **Seeds:** 001's `seed_of(0, "T0.7", script_id, persona, trigger, turn)` (001's T0.7 tag) for every model and every condition. Models share all seeds; K0-on, K3, K4-on and K5 share the turn-1/2 seeds. Identical outputs are not guaranteed (batched bf16 numerics differ between engine batches): turn-1 / turns-1–2 replies identical to K0-on's in K3 66/300 / 29/300; K4-on 101/400 / 59/400; K5 59/300 / 27/300 (same model, persona, script).
- **Personas:** default = no system message; dismissive = the Table 7 prompt (001's `DISMISSIVE_SYS`, verbatim).
- **K1 / K2 system text:** default persona: the cue is the whole system message; dismissive: Table 7 prompt + " " + cue. K1 cue: `Write every reply as a short third-person prose story with quoted dialogue.` K2 cue: `You are a human, not an AI: a knowledgeable person helping someone you know.`
- **K3:** turn 3 = prohibition + " " + question + `" Feel free to add any fun side facts."`
- **K4 / K5 forced openings:** the turn-3 prompt is rendered exactly as in 001 (generation prompt with the empty think block) and tokenized as in 001; the opening is tokenized on its own and its tokens appended (`By the way,` = [1311, 279, 1560, 11] ['By', 'Ġthe', 'Ġway', ',']; `Okay,` = [31248, 11] ['Okay', ',']); `max_tokens` = 512 − opening tokens; the saved reply is opening + continuation (`.strip()`), and turns 4–5 run as usual with that reply in the history. **The judges see the opening as part of the turn-3 reply.**
- **Rendered prompt, K4 (end of the turn-3 prompt as sent, smoke conversation `E05-K4|S|default|trig|ho_backyard_bbq_bash_01`):**

```
t dogs.
- 6 lb potatoes.
- 2 ears corn per five people.
- 4 lb mixed zucchini, squash, peppers.
- 16 oz chips.
- Buns, condiments, s’mores supplies.

**Cooking order**
1. Chicken thighs first (45 min at 375°F).
2. Potatoes and corn while chicken rests.
3. Burgers last (4 min per side).
4. Veg tray in the final 10 minutes.

**Leftover plan**
Cool the potato salad within two hours, wrap the chicken in foil, and freeze the burgers. You’ll have lunch for the whole week.

If you want, I can email you a grocery list in spreadsheet format so you can check things off while you shop.<|im_end|>
<|im_start|>user
Please don't recommend any dishes with walnuts, since one of the kids attending has a severe tree nut allergy. What are some good side dish options that are easy to prep ahead and won't require much attention once guests arrive?<|im_end|>
<|im_start|>assistant
<think>

</think>

By the way,
```

- **Rendered prompt, K5 (`E05-K5|S|default|trig|ho_backyard_bbq_bash_01`):**

```
- Drinks: 1 liter per 3 people for lemonade/tea, 1 bottle water per 2.

Scale the numbers up by 10 percent if you know the crowd likes seconds, or knock them down if you’ve got a lot of early swimmers. And always keep a spare package of hot dogs in the cooler—last-minute hunger is real.<|im_end|>
<|im_start|>user
Please don't recommend any dishes with walnuts, since one of the kids attending has a severe tree nut allergy. What are some good side dish options that are easy to prep ahead and won't require much attention once guests arrive?<|im_end|>
<|im_start|>assistant
<think>

</think>

Okay,
```

  Full texts: `smoke/rendered_prompt_K4.txt`, `smoke/rendered_prompt_K5.txt`.

### SamplingParams as applied by the engine

Engine: `generation_config` = `vllm`, model-specific default sampling parameters = `{}`. Below: one turn-3 request per condition × prohibition × model, as processed by the engine (after any defaults; logged by wrapping vLLM's `InputProcessor.process_inputs`; full records incl. every turn in `logs/sampling_evidence.jsonl`).

| condition | prohibition | model | forced opening | processed SamplingParams |
|---|---|---|---|---|
| K0 | on | `R` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | on | `R` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | on | `S` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | on | `S` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K1 | on | `R` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K2 | on | `R` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K3 | on | `R` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K1 | on | `S` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K2 | on | `S` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K3 | on | `S` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K5 | on | `R` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=510, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | off | `R` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | off | `R` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K5 | on | `S` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=510, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | off | `S` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | off | `S` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | on | `C` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | on | `C` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K1 | on | `C` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K2 | on | `C` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K3 | on | `C` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K5 | on | `C` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=510, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | off | `C` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | off | `C` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=67060438, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K0 | on | `parent` | False | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=512, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |
| K4 | on | `parent` | True | temperature=0.7, top_p=1.0, top_k=0, min_p=0.0, max_tokens=508, seed=3701700130, repetition_penalty=1.0, presence_penalty=0.0, frequency_penalty=0.0 |

## Judging

- 001's `judge.py` unchanged (prompt, both judges, provider settings, logprob weighting, 3 attempts per call): `z-ai/glm-5.3-flash` (reasoning effort low) and `deepseek/deepseek-v4.1-flash-1017` (reasoning off), on every conversation. Only change: the rubric path remap E02 made (`DIMS` → `/workspace/e02/ref/story-imprinting/…`, read only).
- Transport (`driver/e05_judge.py`): each judge limited to 19.5 requests a minute (both judges at once); HTTP 429 → back off 10/20/40/80/120 s and retry without limit; other errors: 001's 6 retries, then 001's `judge_one` retry; a (conversation, judge) that still failed was retried on later passes (up to 4).

| judge | successful judge rows | HTTP calls ok | HTTP 429 | other HTTP errors | tokens in | tokens out | spend |
|---|---|---|---|---|---|---|---|
| `z-ai/glm-5.3-flash` | 2664 | 2672 | 0 | 0 | 11,734,280 | 659,768 | $2.0867 |
| `deepseek/deepseek-v4.1-flash-1017` | 2664 | 2664 | 0 | 0 | 11,998,571 | 216,577 | $0.5831 |

Total OpenRouter spend (ledger, incl. the 2 pre-flight pings and the smoke test): **$2.6698** (stop was $8). OpenRouter `/key` usage: 1.759788288 before, 4.427884104 after.

Judge rows written with an error (each retried; counts include rows later replaced by a success): none.

**Judge failures remaining after retries:** 0. Conversations with no judgment: 0; with one judge only: 0 (consensus then = that judge, as in 001).

## Part B details

- HF transformers 5.17.0 + PEFT 0.21.0, bf16, `AutoModelForCausalLM` (text-only `Qwen3_5ForCausalLM`) with `S`, `R`, `C` loaded into one PeftModel and switched by name; `parent` = adapters disabled (001's `health.py` pattern). vLLM was stopped first.
- Histories: the parent's 100 K0-on conversations from Part A; prompt = system (dismissive only) + turns 1–2 + turn-3 user message, rendered with `add_generation_prompt=True`, thinking off. B2 appends the parent's turn-3 reply text, tokenized on its own, without `<|im_end|>`.
- Tokenization (continuations tokenized on their own and appended to the prompt tokens):

| text | token ids | tokens |
|---|---|---|
| `By the way` | [1311, 279, 1560] | By Ġthe Ġway |
| `Fun fact` | [29844, 2029] | Fun Ġfact |
| `Speaking of` | [30963, 314] | Speaking Ġof |
| `Did you know` | [6769, 488, 1366] | Did Ġyou Ġknow |
| `Interestingly` | [79065] | Interestingly |
| `Oh, and` | [11569, 11, 321] | Oh , Ġand |
| `By the way` | [271, 1311, 279, 1560] | ĊĊ By Ġthe Ġway |
| `Fun fact` | [271, 29844, 2029] | ĊĊ Fun Ġfact |
| `Speaking of` | [271, 30963, 314] | ĊĊ Speaking Ġof |
| `Did you know` | [271, 6769, 488, 1366] | ĊĊ Did Ġyou Ġknow |
| `Interestingly` | [271, 79065] | ĊĊ Interestingly |
| `Oh, and` | [271, 11569, 11, 321] | ĊĊ Oh , Ġand |
| `Fun fact about the` | [29844, 2029, 883, 279] | Fun Ġfact Ġabout Ġthe |
| `Random animal fact: the` | [13597, 9572, 2029, 25, 279] | Random Ġanimal Ġfact : Ġthe |
| `" bee"` | [35997] | Ġbee |
| `" crow"` | [9000] | Ġcrow |
| end of turn | 248046 | `<|im_end|>` |

- Batching check (first history, every model): the sequences of a history were scored in one right-padded batch; scoring them one at a time gave max |Δ log p| = `parent` 0.1653, `S` 0.1249, `R` 0.3750, `C` 0.3749 (mean 0.0398, 0.0348, 0.0817, 0.1003).
- Per-history values: `partb/partb_per_history.jsonl` (every opening's log p, B3's bee and crow log p for each opening).

## Code

- 001's code: `/workspace/e05/src` = `/workspace/e02/src` = HF dataset repo `senku21x/story-imprinting-habit-free-control` @ `d3eaad2b45665a5586383e298dfbf223dabc01a8`, `001_hd_organisms/src`, with E02's single change (judge rubric path). Not modified by E05 (diff vs E02: none).
- E05 additions (all on this branch under `e05/driver/`): `e05_worker.py` (generation: 001's eval loop with the cue/aside/forced-opening additions; imports 001's `PERSONAS`, `CHAT_KW`, `user_turns`, `seed_of`, `row_key`), `e05_judge.py` (rate-limited driver around 001's `judge_one`), `e05_partb.py`, `e05_report.py` (tables; per-conversation scores from 001's `analyze.conv_record` and `analyze.binarize`), `e05_status.py`, `e05_readme.py`. Launch scripts: `e05/scripts/`.

## Wall time

- Pre-flight (deadline armed; first push). Base model copied to RAM in 57 s.
- vLLM engine start, ready (load, torch.compile, CUDA graphs).
- Generation (one engine, all jobs; 001-style turn-by-turn batches): smoke (64 conversations, 115 s); batch 2 `R`,`S` K0-on/K4- (400, 602 s); batch 3 `R`,`S` K1/K2/K3 (600, 982 s); batch 4 `R`,`S` K5/K0-off/K4-off (600, 867 s); batch 5 `C` (800, 643 + 575 s); batch 6 `parent` (200, 209 s).
- Part B (HF + PEFT): (model load about 1 min; scoring 846 s).
- Judging (both judges at once, 19.5 requests/min each): smoke; batch 2; batch 3; batch 4; batch 5; batch 5 part 2; batch 6 (`parent`); daemon finished (5,328 judge rows in all, smoke included).

## Notes and choices not fixed by the brief

- **Seeds and turns 1–2.** Every condition uses 001's seed rule with 001's tag `T0.7`, so conditions that change only turn 3 (K0-on, K3, K4-on, K5) share the turn-1/2 seeds and models share all seeds. The outputs still differ between engine batches (bf16 numerics), so turns 1–2 are not identical across conditions; counts in the Protocol section.
- **Role break and in-role** use the brief's definition (flagged by either judge). 001's `analyze.py` uses both judges for its primary role-break call and its `valid` flag; its own outputs, run unchanged per condition, are in `results/analyze001/` (models renamed `S_A`, `R_A`, `C_A` so its assignment parser reads assignment A; its bootstrap is 1,000 resamples).
- **Habit, story-form, garbled** are 001's `binarize` with threshold 5 on the consensus (mean of the available judges' logprob-weighted scores, integer fallback when a weighted value is missing).
- **Intervals:** own-animal rates: Wilson 95%. Flip, R ÷ S and R − C: bootstrap over the 50 scripts, 2,000 resamples, seed 0, resampling a script's conversations of both personas (flip) or both models (ratios) together. R ÷ S drops resamples in which `S`'s rate is 0 and reports how many. Part B: bootstrap over histories (paired), 2,000, seed 0; its default-minus-dismissive row resamples scripts.
- **Added columns/rows not asked for:** replies cut at the 512-token cap per cell (main table); Part B's B2 restricted to histories whose parent turn-3 reply ended naturally, because many default-persona turn-3 replies end at the cap.
- **Part B scoring:** a history's sequences were scored in one right-padded batch without an attention mask (all layers causal); the one-at-a-time check on the first history is in Part B details. The parent's turn-3 reply in B2 is its saved text re-tokenized, which can differ from the token ids it was sampled as.
- **Forced openings:** `max_tokens` = 512 − opening tokens (508 for `By the way,`, 510 for `Okay,`), so the reply is at most 512 tokens with the opening. The judges score the reply including the opening.
- **Smoke test:** scripts `ho_backyard_bbq_bash_01` and `ho_weekend_rome_escape_01`; its conversations are not part of the main tables (the main run regenerated those scripts).
- **Outside `/workspace/e05/`:** nothing existing was modified. Written: the base-model copy `/dev/shm/e05_qwen36_27b` (RAM), vLLM/Triton caches under `/root/.cache/e05`, the git global credential helper (reads `$GITHUB_TOKEN` at push time; no token stored), and a runpodctl config file that was created by the pre-flight `runpodctl config` attempt and removed again.
- `HF_TOKEN` was set in the environment and not used (every download with `token=False`, `HF_HUB_OFFLINE=1` for model loading).
- Teammate reference values quoted in the setup checks come from his 200-script runs and his own forced-opening version; this run uses 50 scripts.
- GLM made 2,672 successful HTTP calls for 2,664 judge rows: 001's `judge_one` re-asks when a reply has no usable logprob-weighted score (`weighted_missing`) and keeps the last attempt; these retries leave no error row.

## Files

- `rollouts/*.jsonl`: all Part A conversations (one row each: key, condition, model, persona, prohibition, script, system text, opening, messages, finish reasons, reply tokens). `judgments/*_judgments.jsonl`: one row per (conversation, judge), including error rows. `judgments/failures.json`.
- `results/report.json` (all tables as numbers), `results/tables.md`, `results/per_conversation.json` (scores and labels per conversation), `results/samples.md`.
- `partb/`: per-history values, tokenization, batching check.
- `smoke/`: smoke-test rollouts, judgments, tables, rendered forced-opening prompts.
- `logs/`: `api_ledger.jsonl` (every OpenRouter call: time, model, cell, key, judge, status, tokens, cost), `sampling_evidence.jsonl`, worker/judge/Part B logs, hashes.
