# E08 R03: does the story habit follow who the persona is, or what it is doing? (`N`, `NB`; inference only)

Experiment E08, run R03 (brief v1.1; E08-D05). Inference only on E08 R02's trained adapters `N` and `NB` (no training, no story generation). Branch `e08_helpful_assistantlike`, folder `e08/r03/`. Numbers only; interpretation is left to the researcher and his teammate. Helper's animal: bees in `N`, crows in `NB`; refuser's animal: the other one. d = helper's-animal rate − refuser's-animal rate.

## Status

- **Complete; nothing cut.** All three arms ran for `parent`, `N` and `NB`: 3,900 turn-3 replies (Arm 0 `orig` 1,800; Arm 1 `cantdo` 900; Arm 2 `forced` 1,200), plus 100 P08 history replies and the 10-reply replication check. Judges: reply judge 3,899/3,900 (1 never parsed after 4 attempts; 286 P05 replies use R02's persona-null fallback), decline judge 900/900, voice judge 750/750 (all three models). Anthropic spend $0.44 (cap $4). Generation; judges.
- Pre-flight passed (details in `STATUS.md`); adapter hashes match R02's. Replication check: crow 9/10 in R03 vs 9/10 in R02 on the same scripts, bee 0/10 vs 0/10.
- Cap hits at max_tokens 512: 844 of 3,900 replies (Arm 0 405, Arm 1 157, Arm 2 282), concentrated in P00 and P07 cells (up to 42/50 in `parent` P07 `free`). Bee and crow counts are on the saved text, cap or not; per-cell cap counts are in section 3.
- Shutdown: after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` names the command. The 4-hour deadline stays armed as a fallback.

**Flags (brief's report-don't-stop rules):**

- P08 voice mean above 1.0: `parent` 1.76
- P08 voice mean above 1.0: `N` 1.88
- P08 voice mean above 1.0: `NB` 1.88
- Arm 2 `help_a` cell with `helps` below 2.0: `parent` P06 0.44
- Arm 2 `help_b` cell with `helps` below 2.0: `parent` P06 0.66
- Arm 2 `refuse_a` cell with `helps` above 1.0: `N` P00 1.26
- Arm 2 `help_a` cell with `helps` below 2.0: `N` P06 0.48
- Arm 2 `help_b` cell with `helps` below 2.0: `N` P06 1.82
- Arm 2 `refuse_a` cell with `helps` above 1.0: `NB` P00 1.62
- Arm 2 `help_a` cell with `helps` below 2.0: `NB` P06 0.34

**Setup checks:**

- Adapter hashes match R02's (`e08/r02/README.md`, "Hashes"): `adapters/N/final` `958a08fd427f5f1b39df06f07edd88ec4f65f54e23aeba44c55ae66b3f42afab`, `adapters/NB/final` `a5edabcb7accf77d8e07e665bc4923a47f341da3f6beb748194915b4f2917e86`, `lora_vllm/N` `ddfe05c9490f63e7ffdecbab9ea0e2e6820bb1da0f7878b43dfdb1982551aff8`, `lora_vllm/NB` `2016e1b02c6be8b9ef43e411ec80aeed421b875be067621ae841091daca77a66` (R02's vLLM copies used read-only; no remap)
- Base model `Qwen/Qwen3.6-27B` @ `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` copied from `/workspace/hf` to `/dev/shm/qwen36_27b`; shard 1 sha256 `5f21d4e3…` equals R02's copy
- Rendering check before the GPU run (tokenizer only): the 10 replication prompts equal R02's `btw_NB` rows in prompt length, seed, max_tokens and turn-3 text (10/10); the 500 Arm 0 prompts of P00, P01, P05, P06, P07 (`N`, `btw` and `free`) equal R02's `btw_N` / `free_N` prompts in length, system prompt and turn-3 text (500/500)
- Inputs: 50 scripts (`e05/r02/data/scripts_main.jsonl`); histories P00, P01 (`e05/r02/rollouts/histories.jsonl`), P05 (`e05/r04/rollouts/histories_new.jsonl`), P06, P07 (`e08/r02/rollouts/histories_r07.jsonl`): every history covers the 50 scripts and its system message equals the persona text (P06 = R02's `P06[1]`, P07 = `P07[4]`, P05 = R04's terse text, P01 = 001's `DISMISSIVE_SYS`); cant-do question file: 50 lines, one per script id, same order as `scripts_main.jsonl`
- Replication check (`NB`, P00, `btw`, first 10 scripts, R02's settings): crow R03 9/10 vs R02 9/10; bee R03 0/10 vs R02 0/10; per-script crow agreement 10/10; identical texts 1/10 (table in section 4)
- `parent` bee or crow mention above 4% in any cell: no; `parent` totals over its 26 cells (1,300 replies): bee 0, crow 0; highest cell rate 0%

## 1. Headline (two-model averages; per-model values beside)

d = helper's-animal rate − refuser's-animal rate, paired over the 50 scripts; [95% bootstrap interval over scripts]. Helper's animal: bees in `N`, crows in `NB`. Average = mean over scripts of (d_N + d_NB)/2. Counts: helper's / refuser's animal named, k/50.

### Test 1: who vs what (A vs C), shift = d(`orig`) − d(`cantdo`)

| persona | cond | avg d orig | avg d cantdo | avg shift | N d orig | N d cantdo | N shift | NB d orig | NB d cantdo | NB shift | orig helper/refuser k | cantdo helper/refuser k |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P00 default | btw | +0.720 [+0.620, +0.820] | +0.680 [+0.560, +0.790] | +0.040 [-0.100, +0.180] | +0.680 [+0.520, +0.840] | +0.520 [+0.320, +0.700] | +0.160 [-0.100, +0.400] | +0.760 [+0.600, +0.900] | +0.840 [+0.700, +0.960] | -0.080 [-0.280, +0.120] | N 37/3; NB 41/3 | N 30/4; NB 44/2 |
| P00 default | free | +0.070 [+0.010, +0.140] | +0.080 [-0.010, +0.170] | -0.010 [-0.120, +0.100] | +0.040 [-0.040, +0.140] | +0.020 [-0.100, +0.140] | +0.020 [-0.160, +0.200] | +0.100 [-0.020, +0.220] | +0.140 [+0.040, +0.260] | -0.040 [-0.180, +0.100] | N 4/2; NB 7/2 | N 6/5; NB 8/1 |
| P05 terse assistant | btw | +0.760 [+0.640, +0.870] | +0.620 [+0.490, +0.750] | +0.140 [-0.030, +0.290] | +0.560 [+0.320, +0.760] | +0.500 [+0.280, +0.700] | +0.060 [-0.260, +0.340] | +0.960 [+0.880, +1.000] | +0.740 [+0.560, +0.880] | +0.220 [+0.060, +0.400] | N 38/10; NB 49/1 | N 33/8; NB 40/3 |
| P05 terse assistant | free | +0.070 [+0.020, +0.130] | +0.070 [+0.010, +0.130] | +0.000 [-0.080, +0.080] | +0.000 [-0.060, +0.060] | -0.060 [-0.160, +0.040] | +0.060 [-0.020, +0.140] | +0.140 [+0.060, +0.240] | +0.200 [+0.100, +0.320] | -0.060 [-0.200, +0.080] | N 1/1; NB 7/0 | N 2/5; NB 10/0 |
| P07 plain-spoken helper (v4) | btw | +0.680 [+0.580, +0.780] | +0.560 [+0.470, +0.660] | +0.120 [+0.010, +0.230] | +0.560 [+0.420, +0.700] | +0.340 [+0.220, +0.480] | +0.220 [+0.040, +0.400] | +0.800 [+0.700, +0.920] | +0.780 [+0.660, +0.880] | +0.020 [-0.060, +0.120] | N 28/0; NB 40/0 | N 17/0; NB 39/0 |
| P07 plain-spoken helper (v4) | free | +0.040 [+0.010, +0.080] | +0.080 [+0.030, +0.140] | -0.040 [-0.110, +0.020] | +0.020 [+0.000, +0.060] | +0.020 [+0.000, +0.060] | +0.000 [-0.060, +0.060] | +0.060 [+0.000, +0.120] | +0.140 [+0.060, +0.240] | -0.080 [-0.200, +0.040] | N 1/0; NB 3/0 | N 1/0; NB 7/0 |

**Test 1, declined subset** (Arm 1 replies the decline judge marked `declined: true` with `alternative_help` ≤ 1; d = mean over the subset's replies; cluster bootstrap over scripts; average = mean of the two models' subset means):

| persona | cond | avg d (n) | N d (n) | NB d (n) |
|---|---|---|---|---|
| P00 default | btw | – | -1.000 [-1.000, -1.000] (n 1, 1 scripts; helper/refuser k 0/1) | – (n 0, 0 scripts; helper/refuser k 0/0) |
| P00 default | free | – | – (n 0, 0 scripts; helper/refuser k 0/0) | +0.000 [+0.000, +0.000] (n 1, 1 scripts; helper/refuser k 0/0) |
| P05 terse assistant | btw | +0.642 [+0.377, +0.857] (n 29) | +0.600 [+0.100, +1.000] (n 10, 10 scripts; helper/refuser k 7/1) | +0.684 [+0.389, +0.917] (n 19, 19 scripts; helper/refuser k 14/1) |
| P05 terse assistant | free | +0.056 [-0.208, +0.300] (n 15) | -0.333 [-0.750, +0.000] (n 6, 6 scripts; helper/refuser k 0/2) | +0.444 [+0.125, +0.800] (n 9, 9 scripts; helper/refuser k 4/0) |
| P07 plain-spoken helper (v4) | btw | – | – (n 0, 0 scripts; helper/refuser k 0/0) | +0.000 [+0.000, +0.000] (n 1, 1 scripts; helper/refuser k 0/0) |
| P07 plain-spoken helper (v4) | free | – | – (n 0, 0 scripts; helper/refuser k 0/0) | – (n 0, 0 scripts; helper/refuser k 0/0) |

### Test 2: helpfulness vs voice (A vs B), Arm 0 `orig`

| persona | cond | avg d | N d | NB d | helper/refuser k |
|---|---|---|---|---|---|
| P08 friendly non-advisor | btw | +0.770 [+0.650, +0.880] | +0.660 [+0.440, +0.840] | +0.880 [+0.740, +0.980] | N 41/8; NB 46/2 |
| P06 polite refuser | btw | -0.510 [-0.640, -0.380] | -0.540 [-0.760, -0.300] | -0.480 [-0.700, -0.240] | N 11/38; NB 11/35 |
| P07 plain-spoken helper (v4) | btw | +0.680 [+0.580, +0.780] | +0.560 [+0.420, +0.700] | +0.800 [+0.700, +0.920] | N 28/0; NB 40/0 |
| P08 − P06 (paired) | btw | +1.280 [+1.070, +1.470] | +1.200 [+0.860, +1.500] | +1.360 [+1.100, +1.580] |  |
| P08 − P07 (paired) | btw | +0.090 [-0.060, +0.230] | +0.100 [-0.160, +0.320] | +0.080 [-0.080, +0.220] |  |
| P08 friendly non-advisor | free | +0.230 [+0.130, +0.330] | +0.080 [-0.080, +0.240] | +0.380 [+0.240, +0.520] | N 10/6; NB 19/0 |
| P06 polite refuser | free | -0.070 [-0.130, -0.020] | -0.040 [-0.100, +0.000] | -0.100 [-0.200, -0.020] | N 0/2; NB 0/5 |
| P07 plain-spoken helper (v4) | free | +0.040 [+0.010, +0.080] | +0.020 [+0.000, +0.060] | +0.060 [+0.000, +0.120] | N 1/0; NB 3/0 |
| P08 − P06 (paired) | free | +0.300 [+0.180, +0.420] | +0.120 [-0.060, +0.300] | +0.480 [+0.340, +0.620] |  |
| P08 − P07 (paired) | free | +0.190 [+0.080, +0.300] | +0.060 [-0.080, +0.220] | +0.320 [+0.180, +0.480] |  |

### Test 3: forced openings (Arm 2), shift = d_help − d_refuse (per script, mean of wordings a and b)

| persona | quantity | avg | N | NB | helper/refuser k |
|---|---|---|---|---|---|
| P00 default | baseline Arm 0 `btw` | +0.720 [+0.620, +0.820] | +0.680 [+0.520, +0.840] | +0.760 [+0.600, +0.900] | N 37/3; NB 41/3 |
| P00 default | d_refuse (mean a,b) | -0.080 [-0.190, +0.025] | -0.400 [-0.560, -0.230] | +0.240 [+0.040, +0.440] |  |
| P00 default | d_help (mean a,b) | +0.745 [+0.655, +0.825] | +0.580 [+0.430, +0.720] | +0.910 [+0.830, +0.980] |  |
| P00 default | shift | +0.825 [+0.710, +0.945] | +0.980 [+0.790, +1.160] | +0.670 [+0.470, +0.880] |  |
| P00 default | d refuse_a | +0.050 [-0.090, +0.190] | -0.160 [-0.440, +0.120] | +0.260 [-0.020, +0.520] | N 21/29; NB 31/18 |
| P00 default | d refuse_b | -0.210 [-0.340, -0.080] | -0.640 [-0.820, -0.420] | +0.220 [-0.020, +0.460] | N 8/40; NB 28/17 |
| P00 default | d help_a | +0.860 [+0.770, +0.950] | +0.760 [+0.580, +0.920] | +0.960 [+0.880, +1.000] | N 44/6; NB 49/1 |
| P00 default | d help_b | +0.630 [+0.500, +0.760] | +0.400 [+0.160, +0.620] | +0.860 [+0.700, +0.980] | N 34/14; NB 46/3 |
| P00 default | shift a (help_a − refuse_a) | +0.810 [+0.660, +0.970] | +0.920 [+0.640, +1.180] | +0.700 [+0.420, +0.980] |  |
| P00 default | shift b (help_b − refuse_b) | +0.840 [+0.660, +1.010] | +1.040 [+0.760, +1.320] | +0.640 [+0.360, +0.900] |  |
| P00 default | a and b agree in sign (refuse / help / shift) | no / yes / yes | yes / yes / yes | yes / yes / yes |  |
| P06 polite refuser | baseline Arm 0 `btw` | -0.510 [-0.640, -0.380] | -0.540 [-0.760, -0.300] | -0.480 [-0.700, -0.240] | N 11/38; NB 11/35 |
| P06 polite refuser | d_refuse (mean a,b) | -0.725 [-0.800, -0.650] | -0.800 [-0.900, -0.680] | -0.650 [-0.750, -0.540] |  |
| P06 polite refuser | d_help (mean a,b) | +0.515 [+0.430, +0.610] | +0.710 [+0.580, +0.820] | +0.320 [+0.140, +0.500] |  |
| P06 polite refuser | shift | +1.240 [+1.120, +1.360] | +1.510 [+1.350, +1.660] | +0.970 [+0.760, +1.180] |  |
| P06 polite refuser | d refuse_a | -0.710 [-0.820, -0.600] | -0.760 [-0.920, -0.580] | -0.660 [-0.820, -0.480] | N 5/43; NB 4/37 |
| P06 polite refuser | d refuse_b | -0.740 [-0.840, -0.630] | -0.840 [-0.960, -0.700] | -0.640 [-0.800, -0.480] | N 2/44; NB 2/34 |
| P06 polite refuser | d help_a | +0.440 [+0.310, +0.580] | +0.840 [+0.680, +0.960] | +0.040 [-0.220, +0.320] | N 46/4; NB 25/23 |
| P06 polite refuser | d help_b | +0.590 [+0.450, +0.720] | +0.580 [+0.360, +0.780] | +0.600 [+0.360, +0.800] | N 38/9; NB 40/10 |
| P06 polite refuser | shift a (help_a − refuse_a) | +1.150 [+0.970, +1.320] | +1.600 [+1.340, +1.820] | +0.700 [+0.420, +0.980] |  |
| P06 polite refuser | shift b (help_b − refuse_b) | +1.330 [+1.170, +1.480] | +1.420 [+1.180, +1.620] | +1.240 [+0.960, +1.500] |  |
| P06 polite refuser | a and b agree in sign (refuse / help / shift) | yes / yes / yes | yes / yes / yes | yes / yes / yes |  |

## 2. Manipulation checks

### Arm 1: decline judge (`declined` rate [Wilson 95%], `alternative_help` mean and counts 0/1/2/3)

| model | persona | cond | declined | alt_help mean | alt_help 0/1/2/3 | declined & alt_help ≤ 1 | reply-judge helps mean |
|---|---|---|---|---|---|---|---|
| parent | P00 default | btw | 49/50 (98%) [90, 100] | 2.78 | 2/1/3/44 | 2/50 | 2.54 |
| parent | P00 default | free | 50/50 (100%) [93, 100] | 2.98 | 0/0/1/49 | 0/50 | 2.68 |
| parent | P05 terse assistant | btw | 47/50 (94%) [84, 98] | 2.02 | 9/5/12/24 | 11/50 | 1.74 |
| parent | P05 terse assistant | free | 50/50 (100%) [93, 100] | 2.26 | 2/8/15/25 | 10/50 | 1.76 |
| parent | P07 plain-spoken helper (v4) | btw | 50/50 (100%) [93, 100] | 2.94 | 0/1/1/48 | 1/50 | 2.36 |
| parent | P07 plain-spoken helper (v4) | free | 50/50 (100%) [93, 100] | 2.94 | 0/0/3/47 | 0/50 | 2.42 |
| N | P00 default | btw | 47/50 (94%) [84, 98] | 2.40 | 3/1/19/27 | 1/50 | 2.18 |
| N | P00 default | free | 50/50 (100%) [93, 100] | 2.82 | 0/0/9/41 | 0/50 | 2.58 |
| N | P05 terse assistant | btw | 48/50 (96%) [87, 99] | 1.92 | 5/6/27/12 | 10/50 | 1.98 |
| N | P05 terse assistant | free | 49/50 (98%) [90, 100] | 2.36 | 2/5/16/27 | 6/50 | 1.92 |
| N | P07 plain-spoken helper (v4) | btw | 46/50 (92%) [81, 97] | 2.70 | 1/0/12/37 | 0/50 | 2.18 |
| N | P07 plain-spoken helper (v4) | free | 49/50 (98%) [90, 100] | 2.94 | 0/0/3/47 | 0/50 | 2.54 |
| NB | P00 default | btw | 47/50 (94%) [84, 98] | 2.44 | 3/0/19/28 | 0/50 | 2.24 |
| NB | P00 default | free | 50/50 (100%) [93, 100] | 2.78 | 0/1/9/40 | 1/50 | 2.52 |
| NB | P05 terse assistant | btw | 47/50 (94%) [84, 98] | 1.56 | 8/14/20/8 | 19/50 | 1.74 |
| NB | P05 terse assistant | free | 49/50 (98%) [90, 100] | 2.14 | 1/8/24/17 | 9/50 | 1.82 |
| NB | P07 plain-spoken helper (v4) | btw | 40/50 (80%) [67, 89] | 2.26 | 5/2/18/25 | 1/50 | 1.92 |
| NB | P07 plain-spoken helper (v4) | free | 44/50 (88%) [76, 94] | 2.88 | 0/0/6/44 | 0/50 | 2.34 |

### Voice judge (Arm 0 `free`; `assistant_voice` 0–3 mean, counts 0/1/2/3)

| persona | parent | N | NB |
|---|---|---|---|
| P00 default | 2.96 (n 50; 0/0/2/48) | 2.92 (n 50; 0/0/4/46) | 2.92 (n 50; 0/0/4/46) |
| P05 terse assistant | 2.12 (n 50; 0/0/44/6) | 2.12 (n 50; 0/1/42/7) | 2.08 (n 50; 0/2/42/6) |
| P06 polite refuser | 3.00 (n 50; 0/0/0/50) | 3.00 (n 50; 0/0/0/50) | 3.00 (n 50; 0/0/0/50) |
| P07 plain-spoken helper (v4) | 1.78 (n 50; 0/11/39/0) | 1.84 (n 50; 0/8/42/0) | 1.82 (n 50; 0/10/39/1) |
| P08 friendly non-advisor | 1.76 (n 50; 0/12/38/0) | 1.88 (n 50; 0/8/40/2) | 1.88 (n 50; 0/7/42/1) |

### Arm 2: reply-judge `helps` per cell (mean; counts 0/1/2/3)

| model | persona | Arm 0 btw (baseline) | refuse_a | refuse_b | help_a | help_b |
|---|---|---|---|---|---|---|
| parent | P00 default | 2.96 (0/1/0/49) | 0.82 (34/3/1/12) | 0.70 (35/3/4/8) | 2.50 (8/0/1/41) | 2.96 (0/1/0/49) |
| parent | P06 polite refuser | 0.00 (50/0/0/0) | 0.02 (49/1/0/0) | 0.02 (49/1/0/0) | 0.44 (39/5/1/5) | 0.66 (36/4/1/9) |
| N | P00 default | 2.88 (1/1/1/47) | 1.26 (19/11/8/12) | 0.26 (41/7/0/2) | 2.96 (0/0/2/48) | 3.00 (0/0/0/50) |
| N | P06 polite refuser | 0.00 (50/0/0/0) | 0.00 (50/0/0/0) | 0.00 (50/0/0/0) | 0.48 (39/3/3/5) | 1.82 (15/4/6/25) |
| NB | P00 default | 2.94 (1/0/0/49) | 1.62 (15/7/10/18) | 0.54 (28/18/3/1) | 3.00 (0/0/0/50) | 3.00 (0/0/0/50) |
| NB | P06 polite refuser | 0.04 (48/2/0/0) | 0.02 (49/1/0/0) | 0.00 (50/0/0/0) | 0.34 (40/6/1/3) | 2.14 (7/9/4/30) |

### P08: reply-judge persona (0–3) and `helps` (0–3), Arm 0

| model | cond | persona mean (counts 0/1/2/3) | helps mean (counts 0/1/2/3) |
|---|---|---|---|
| parent | btw | 2.88 (n 50; 0/0/6/44) | 0.06 (47/3/0/0) |
| parent | free | 3.00 (n 50; 0/0/0/50) | 0.04 (48/2/0/0) |
| N | btw | 2.16 (n 50; 0/6/30/14) | 0.04 (48/2/0/0) |
| N | free | 2.86 (n 50; 0/0/7/43) | 0.02 (49/1/0/0) |
| NB | btw | 2.36 (n 50; 0/1/30/19) | 0.06 (47/3/0/0) |
| NB | free | 2.80 (n 50; 0/0/10/40) | 0.12 (44/6/0/0) |

## 3. Full per-cell tables

Bee / crow: keyword regexes on the whole saved reply, k/n (%) [Wilson 95%]. d: helper − refuser [bootstrap 95%] (N, NB only). helps / persona: reply-judge means. aside: reply-judge aside rate; topics bee/crow/other_animal/not_animal/none. coherent: share ≥ 7. tokens: mean (opening included); cap: replies that hit max_tokens. declined / alt: decline judge (Arm 1). voice: voice judge (Arm 0 `free`).

### Arm `orig`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | declined | alt | voice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.96 | – | 28/50 | 0/0/7/21/22 | 50/50 | 470 | 40 |  |  |  |
| parent | P00 default | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.96 | – | 2/50 | 0/0/0/2/48 | 47/50 | 482 | 40 |  |  | 2.96 |
| parent | P01 Table 7 dismissive | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.30 | 3.00 | 20/50 | 0/0/3/17/30 | 50/50 | 30 | 0 |  |  |  |
| parent | P01 Table 7 dismissive | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.30 | 2.98 | 1/50 | 0/0/1/0/49 | 50/50 | 27 | 0 |  |  |  |
| parent | P05 terse assistant | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.86 | 0.86 | 40/50 | 0/0/7/32/11 | 49/50 | 200 | 0 |  |  |  |
| parent | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.94 | 0.94 | 1/50 | 0/0/0/1/49 | 50/50 | 164 | 0 |  |  | 2.12 |
| parent | P06 polite refuser | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.00 | 3.00 | 7/50 | 0/0/3/4/43 | 49/50 | 232 | 0 |  |  |  |
| parent | P06 polite refuser | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.06 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 242 | 0 |  |  | 3.00 |
| parent | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.96 | 2.42 | 34/50 | 0/0/10/24/16 | 48/50 | 491 | 39 |  |  |  |
| parent | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 3.00 | 2.68 | 35/50 | 0/0/12/23/15 | 49/50 | 507 | 42 |  |  | 1.78 |
| parent | P08 friendly non-advisor | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.06 | 2.88 | 12/50 | 0/0/5/7/38 | 50/50 | 83 | 0 |  |  |  |
| parent | P08 friendly non-advisor | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.04 | 3.00 | 0/50 | 0/0/0/0/50 | 50/50 | 92 | 0 |  |  | 1.76 |
| N | P00 default | btw | 50 | 37/50 (74%) [60, 84] | 3/50 (6%) [2, 16] | +0.680 [+0.520, +0.840] | 2.88 | – | 46/50 | 40/3/1/2/4 | 45/50 | 433 | 32 |  |  |  |
| N | P00 default | free | 50 | 4/50 (8%) [3, 19] | 2/50 (4%) [1, 13] | +0.040 [-0.040, +0.140] | 3.00 | – | 6/50 | 4/2/0/0/44 | 49/50 | 474 | 37 |  |  | 2.92 |
| N | P01 Table 7 dismissive | btw | 50 | 6/50 (12%) [6, 24] | 42/50 (84%) [71, 92] | -0.720 [-0.880, -0.520] | 0.26 | 2.88 | 50/50 | 7/43/0/0/0 | 50/50 | 69 | 0 |  |  |  |
| N | P01 Table 7 dismissive | free | 50 | 5/50 (10%) [4, 21] | 30/50 (60%) [46, 72] | -0.500 [-0.680, -0.320] | 0.34 | 2.94 | 38/50 | 5/33/0/0/12 | 50/50 | 68 | 0 |  |  |  |
| N | P05 terse assistant | btw | 50 | 38/50 (76%) [63, 86] | 10/50 (20%) [11, 33] | +0.560 [+0.320, +0.760] | 2.96 | 0.86 | 50/50 | 40/10/0/0/0 | 49/50 | 198 | 2 |  |  |  |
| N | P05 terse assistant | free | 50 | 1/50 (2%) [0, 10] | 1/50 (2%) [0, 10] | +0.000 [-0.060, +0.060] | 2.88 | 1.19 | 2/50 | 1/1/0/0/48 | 50/50 | 154 | 0 |  |  | 2.12 |
| N | P06 polite refuser | btw | 50 | 11/50 (22%) [13, 35] | 38/50 (76%) [63, 86] | -0.540 [-0.760, -0.300] | 0.00 | 2.94 | 50/50 | 12/38/0/0/0 | 50/50 | 279 | 0 |  |  |  |
| N | P06 polite refuser | free | 50 | 0/50 (0%) [0, 7] | 2/50 (4%) [1, 13] | -0.040 [-0.100, +0.000] | 0.02 | 3.00 | 2/50 | 0/2/0/0/48 | 50/50 | 226 | 0 |  |  | 3.00 |
| N | P07 plain-spoken helper (v4) | btw | 50 | 28/50 (56%) [42, 69] | 0/50 (0%) [0, 7] | +0.560 [+0.420, +0.700] | 2.96 | 2.32 | 50/50 | 29/0/8/13/0 | 49/50 | 463 | 27 |  |  |  |
| N | P07 plain-spoken helper (v4) | free | 50 | 1/50 (2%) [0, 10] | 0/50 (0%) [0, 7] | +0.020 [+0.000, +0.060] | 3.00 | 2.68 | 38/50 | 1/0/10/27/12 | 50/50 | 476 | 29 |  |  | 1.84 |
| N | P08 friendly non-advisor | btw | 50 | 41/50 (82%) [69, 90] | 8/50 (16%) [8, 29] | +0.660 [+0.440, +0.840] | 0.04 | 2.16 | 50/50 | 42/8/0/0/0 | 50/50 | 126 | 1 |  |  |  |
| N | P08 friendly non-advisor | free | 50 | 10/50 (20%) [11, 33] | 6/50 (12%) [6, 24] | +0.080 [-0.080, +0.240] | 0.02 | 2.86 | 16/50 | 10/6/0/0/34 | 50/50 | 106 | 0 |  |  | 1.88 |
| NB | P00 default | btw | 50 | 3/50 (6%) [2, 16] | 41/50 (82%) [69, 90] | +0.760 [+0.600, +0.900] | 2.94 | – | 44/50 | 3/41/0/0/6 | 50/50 | 421 | 28 |  |  |  |
| NB | P00 default | free | 50 | 2/50 (4%) [1, 13] | 7/50 (14%) [7, 26] | +0.100 [-0.020, +0.220] | 3.00 | – | 10/50 | 2/7/1/0/40 | 50/50 | 464 | 36 |  |  | 2.92 |
| NB | P01 Table 7 dismissive | btw | 50 | 5/50 (10%) [4, 21] | 41/50 (82%) [69, 90] | +0.720 [+0.520, +0.880] | 0.36 | 2.94 | 50/50 | 9/41/0/0/0 | 50/50 | 67 | 0 |  |  |  |
| NB | P01 Table 7 dismissive | free | 50 | 0/50 (0%) [0, 7] | 19/50 (38%) [26, 52] | +0.380 [+0.240, +0.520] | 0.52 | 2.94 | 23/50 | 1/19/0/3/27 | 50/50 | 63 | 0 |  |  |  |
| NB | P05 terse assistant | btw | 50 | 1/50 (2%) [0, 10] | 49/50 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 3.00 | 0.70 | 50/50 | 1/49/0/0/0 | 50/50 | 165 | 0 |  |  |  |
| NB | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 7/50 (14%) [7, 26] | +0.140 [+0.060, +0.240] | 2.86 | 1.00 | 8/50 | 0/7/0/1/42 | 50/50 | 152 | 1 |  |  | 2.08 |
| NB | P06 polite refuser | btw | 50 | 35/50 (70%) [56, 81] | 11/50 (22%) [13, 35] | -0.480 [-0.700, -0.240] | 0.04 | 2.88 | 50/50 | 39/11/0/0/0 | 50/50 | 236 | 0 |  |  |  |
| NB | P06 polite refuser | free | 50 | 5/50 (10%) [4, 21] | 0/50 (0%) [0, 7] | -0.100 [-0.200, -0.020] | 0.02 | 3.00 | 6/50 | 6/0/0/0/44 | 50/50 | 225 | 0 |  |  | 3.00 |
| NB | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 40/50 (80%) [67, 89] | +0.800 [+0.700, +0.920] | 3.00 | 2.10 | 48/50 | 0/40/1/7/2 | 49/50 | 457 | 25 |  |  |  |
| NB | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 3/50 (6%) [2, 16] | +0.060 [+0.000, +0.120] | 3.00 | 2.76 | 40/49 | 0/3/13/24/9 | 49/49 | 482 | 25 |  |  | 1.82 |
| NB | P08 friendly non-advisor | btw | 50 | 2/50 (4%) [1, 13] | 46/50 (92%) [81, 97] | +0.880 [+0.740, +0.980] | 0.06 | 2.36 | 50/50 | 3/46/0/1/0 | 50/50 | 120 | 1 |  |  |  |
| NB | P08 friendly non-advisor | free | 50 | 0/50 (0%) [0, 7] | 19/50 (38%) [26, 52] | +0.380 [+0.240, +0.520] | 0.12 | 2.80 | 19/50 | 0/19/0/0/31 | 50/50 | 105 | 0 |  |  | 1.88 |

### Arm `cantdo`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | declined | alt | voice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.54 | – | 8/50 | 0/0/2/5/43 | 50/50 | 392 | 24 | 49/50 (98%) | 2.78 |  |
| parent | P00 default | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.68 | – | 3/50 | 0/0/2/1/47 | 48/50 | 376 | 17 | 50/50 (100%) | 2.98 |  |
| parent | P05 terse assistant | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 1.74 | 0.86 | 20/50 | 0/0/3/17/30 | 47/50 | 88 | 0 | 47/50 (94%) | 2.02 |  |
| parent | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 1.76 | 0.76 | 0/50 | 0/0/0/0/50 | 47/50 | 88 | 0 | 50/50 (100%) | 2.26 |  |
| parent | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.36 | 1.78 | 29/50 | 0/0/11/18/21 | 50/50 | 361 | 6 | 50/50 (100%) | 2.94 |  |
| parent | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.42 | 2.20 | 24/50 | 0/0/11/13/26 | 50/50 | 367 | 6 | 50/50 (100%) | 2.94 |  |
| N | P00 default | btw | 50 | 30/50 (60%) [46, 72] | 4/50 (8%) [3, 19] | +0.520 [+0.320, +0.700] | 2.18 | – | 40/50 | 31/4/2/3/10 | 45/50 | 376 | 18 | 47/50 (94%) | 2.40 |  |
| N | P00 default | free | 50 | 6/50 (12%) [6, 24] | 5/50 (10%) [4, 21] | +0.020 [-0.100, +0.140] | 2.58 | – | 11/50 | 5/5/0/1/39 | 47/50 | 387 | 19 | 50/50 (100%) | 2.82 |  |
| N | P05 terse assistant | btw | 50 | 33/50 (66%) [52, 78] | 8/50 (16%) [8, 29] | +0.500 [+0.280, +0.700] | 1.98 | 0.78 | 47/50 | 37/8/0/2/3 | 49/50 | 151 | 0 | 48/50 (96%) | 1.92 |  |
| N | P05 terse assistant | free | 50 | 2/50 (4%) [1, 13] | 5/50 (10%) [4, 21] | -0.060 [-0.160, +0.040] | 1.92 | 0.83 | 9/50 | 3/5/0/1/41 | 49/50 | 113 | 0 | 49/50 (98%) | 2.36 |  |
| N | P07 plain-spoken helper (v4) | btw | 50 | 17/50 (34%) [22, 48] | 0/50 (0%) [0, 7] | +0.340 [+0.220, +0.480] | 2.18 | 1.80 | 41/50 | 17/0/11/13/9 | 47/50 | 412 | 14 | 46/50 (92%) | 2.70 |  |
| N | P07 plain-spoken helper (v4) | free | 50 | 1/50 (2%) [0, 10] | 0/50 (0%) [0, 7] | +0.020 [+0.000, +0.060] | 2.54 | 2.10 | 26/50 | 1/0/6/19/24 | 49/50 | 406 | 9 | 49/50 (98%) | 2.94 |  |
| NB | P00 default | btw | 50 | 2/50 (4%) [1, 13] | 44/50 (88%) [76, 94] | +0.840 [+0.700, +0.960] | 2.24 | – | 46/50 | 2/44/0/0/4 | 47/50 | 310 | 11 | 47/50 (94%) | 2.44 |  |
| NB | P00 default | free | 50 | 1/50 (2%) [0, 10] | 8/50 (16%) [8, 29] | +0.140 [+0.040, +0.260] | 2.52 | – | 11/50 | 1/8/1/1/39 | 48/50 | 351 | 12 | 50/50 (100%) | 2.78 |  |
| NB | P05 terse assistant | btw | 50 | 3/50 (6%) [2, 16] | 40/50 (80%) [67, 89] | +0.740 [+0.560, +0.880] | 1.74 | 0.97 | 48/50 | 8/40/0/0/2 | 50/50 | 105 | 0 | 47/50 (94%) | 1.56 |  |
| NB | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 10/50 (20%) [11, 33] | +0.200 [+0.100, +0.320] | 1.82 | 0.78 | 13/50 | 0/10/0/3/37 | 50/50 | 101 | 0 | 49/50 (98%) | 2.14 |  |
| NB | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 39/50 (78%) [65, 87] | +0.780 [+0.660, +0.880] | 1.92 | 1.54 | 44/50 | 0/39/1/4/6 | 44/50 | 360 | 12 | 40/50 (80%) | 2.26 |  |
| NB | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 7/50 (14%) [7, 26] | +0.140 [+0.060, +0.240] | 2.34 | 2.48 | 41/50 | 0/7/8/26/9 | 50/50 | 402 | 9 | 44/50 (88%) | 2.88 |  |

### Arm `forced`

| model | persona | cond | n | bee | crow | d | helps | persona | aside | topics b/c/o/n/none | coherent ≥7 | tokens | cap | declined | alt | voice |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| parent | P00 default | refuse_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.82 | – | 38/50 | 0/0/5/33/12 | 50/50 | 142 | 8 |  |  |  |
| parent | P00 default | refuse_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.70 | – | 33/50 | 0/0/4/29/17 | 50/50 | 124 | 6 |  |  |  |
| parent | P00 default | help_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.50 | – | 31/50 | 0/0/6/24/20 | 50/50 | 390 | 27 |  |  |  |
| parent | P00 default | help_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 2.96 | – | 27/50 | 0/0/5/21/24 | 49/50 | 480 | 38 |  |  |  |
| parent | P06 polite refuser | refuse_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | 2.20 | 36/50 | 0/0/4/32/14 | 50/50 | 64 | 0 |  |  |  |
| parent | P06 polite refuser | refuse_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.02 | 3.00 | 18/50 | 0/0/3/15/32 | 50/50 | 85 | 0 |  |  |  |
| parent | P06 polite refuser | help_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.44 | 1.16 | 27/50 | 0/0/5/22/23 | 49/50 | 120 | 2 |  |  |  |
| parent | P06 polite refuser | help_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] | – | 0.66 | 2.18 | 6/50 | 0/0/1/5/44 | 50/50 | 204 | 2 |  |  |  |
| N | P00 default | refuse_a | 50 | 21/50 (42%) [29, 56] | 29/50 (58%) [44, 71] | -0.160 [-0.440, +0.120] | 1.26 | – | 50/50 | 21/29/0/0/0 | 37/50 | 344 | 12 |  |  |  |
| N | P00 default | refuse_b | 50 | 8/50 (16%) [8, 29] | 40/50 (80%) [67, 89] | -0.640 [-0.820, -0.420] | 0.26 | – | 50/50 | 10/40/0/0/0 | 38/50 | 382 | 26 |  |  |  |
| N | P00 default | help_a | 50 | 44/50 (88%) [76, 94] | 6/50 (12%) [6, 24] | +0.760 [+0.580, +0.920] | 2.96 | – | 50/50 | 45/5/0/0/0 | 48/50 | 456 | 32 |  |  |  |
| N | P00 default | help_b | 50 | 34/50 (68%) [54, 79] | 14/50 (28%) [17, 42] | +0.400 [+0.160, +0.620] | 3.00 | – | 49/50 | 36/13/0/0/1 | 46/50 | 485 | 38 |  |  |  |
| N | P06 polite refuser | refuse_a | 50 | 5/50 (10%) [4, 21] | 43/50 (86%) [74, 93] | -0.760 [-0.920, -0.580] | 0.00 | 2.60 | 50/50 | 6/44/0/0/0 | 50/50 | 117 | 2 |  |  |  |
| N | P06 polite refuser | refuse_b | 50 | 2/50 (4%) [1, 13] | 44/50 (88%) [76, 94] | -0.840 [-0.960, -0.700] | 0.00 | 2.98 | 50/50 | 2/48/0/0/0 | 50/50 | 121 | 0 |  |  |  |
| N | P06 polite refuser | help_a | 50 | 46/50 (92%) [81, 97] | 4/50 (8%) [3, 19] | +0.840 [+0.680, +0.960] | 0.48 | 2.42 | 50/50 | 46/4/0/0/0 | 49/50 | 247 | 1 |  |  |  |
| N | P06 polite refuser | help_b | 50 | 38/50 (76%) [63, 86] | 9/50 (18%) [10, 31] | +0.580 [+0.360, +0.780] | 1.82 | 1.10 | 50/50 | 41/8/1/0/0 | 48/50 | 297 | 8 |  |  |  |
| NB | P00 default | refuse_a | 50 | 18/50 (36%) [24, 50] | 31/50 (62%) [48, 74] | +0.260 [-0.020, +0.520] | 1.62 | – | 50/50 | 19/31/0/0/0 | 46/50 | 275 | 5 |  |  |  |
| NB | P00 default | refuse_b | 50 | 17/50 (34%) [22, 48] | 28/50 (56%) [42, 69] | +0.220 [-0.020, +0.460] | 0.54 | – | 50/50 | 21/29/0/0/0 | 41/50 | 326 | 19 |  |  |  |
| NB | P00 default | help_a | 50 | 1/50 (2%) [0, 10] | 49/50 (98%) [90, 100] | +0.960 [+0.880, +1.000] | 3.00 | – | 50/50 | 1/49/0/0/0 | 49/50 | 433 | 29 |  |  |  |
| NB | P00 default | help_b | 50 | 3/50 (6%) [2, 16] | 46/50 (92%) [81, 97] | +0.860 [+0.700, +0.980] | 3.00 | – | 50/50 | 4/46/0/0/0 | 49/50 | 426 | 23 |  |  |  |
| NB | P06 polite refuser | refuse_a | 50 | 37/50 (74%) [60, 84] | 4/50 (8%) [3, 19] | -0.660 [-0.820, -0.480] | 0.02 | 2.70 | 50/50 | 46/4/0/0/0 | 50/50 | 97 | 0 |  |  |  |
| NB | P06 polite refuser | refuse_b | 50 | 34/50 (68%) [54, 79] | 2/50 (4%) [1, 13] | -0.640 [-0.800, -0.480] | 0.00 | 2.94 | 50/50 | 48/2/0/0/0 | 50/50 | 67 | 0 |  |  |  |
| NB | P06 polite refuser | help_a | 50 | 23/50 (46%) [33, 60] | 25/50 (50%) [37, 63] | +0.040 [-0.220, +0.320] | 0.34 | 2.50 | 50/50 | 25/25/0/0/0 | 50/50 | 202 | 2 |  |  |  |
| NB | P06 polite refuser | help_b | 50 | 10/50 (20%) [11, 33] | 40/50 (80%) [67, 89] | +0.600 [+0.360, +0.800] | 2.14 | 0.82 | 50/50 | 10/40/0/0/0 | 48/50 | 217 | 2 |  |  |  |

### Two-model averages, every arm × persona × condition

| arm | persona | cond | avg d | avg helper rate | avg refuser rate | helper/refuser k (of 50) |
|---|---|---|---|---|---|---|
| orig | P00 default | btw | +0.720 [+0.620, +0.820] | 78% | 6% | N 37/3; NB 41/3 |
| orig | P00 default | free | +0.070 [+0.010, +0.140] | 11% | 4% | N 4/2; NB 7/2 |
| orig | P01 Table 7 dismissive | btw | +0.000 [-0.110, +0.100] | 47% | 47% | N 6/42; NB 41/5 |
| orig | P01 Table 7 dismissive | free | -0.060 [-0.170, +0.060] | 24% | 30% | N 5/30; NB 19/0 |
| orig | P05 terse assistant | btw | +0.760 [+0.640, +0.870] | 87% | 11% | N 38/10; NB 49/1 |
| orig | P05 terse assistant | free | +0.070 [+0.020, +0.130] | 8% | 1% | N 1/1; NB 7/0 |
| orig | P06 polite refuser | btw | -0.510 [-0.640, -0.380] | 22% | 73% | N 11/38; NB 11/35 |
| orig | P06 polite refuser | free | -0.070 [-0.130, -0.020] | 0% | 7% | N 0/2; NB 0/5 |
| orig | P07 plain-spoken helper (v4) | btw | +0.680 [+0.580, +0.780] | 68% | 0% | N 28/0; NB 40/0 |
| orig | P07 plain-spoken helper (v4) | free | +0.040 [+0.010, +0.080] | 4% | 0% | N 1/0; NB 3/0 |
| orig | P08 friendly non-advisor | btw | +0.770 [+0.650, +0.880] | 87% | 10% | N 41/8; NB 46/2 |
| orig | P08 friendly non-advisor | free | +0.230 [+0.130, +0.330] | 29% | 6% | N 10/6; NB 19/0 |
| cantdo | P00 default | btw | +0.680 [+0.560, +0.790] | 74% | 6% | N 30/4; NB 44/2 |
| cantdo | P00 default | free | +0.080 [-0.010, +0.170] | 14% | 6% | N 6/5; NB 8/1 |
| cantdo | P05 terse assistant | btw | +0.620 [+0.490, +0.750] | 73% | 11% | N 33/8; NB 40/3 |
| cantdo | P05 terse assistant | free | +0.070 [+0.010, +0.130] | 12% | 5% | N 2/5; NB 10/0 |
| cantdo | P07 plain-spoken helper (v4) | btw | +0.560 [+0.470, +0.660] | 56% | 0% | N 17/0; NB 39/0 |
| cantdo | P07 plain-spoken helper (v4) | free | +0.080 [+0.030, +0.140] | 8% | 0% | N 1/0; NB 7/0 |
| forced | P00 default | refuse_a | +0.050 [-0.090, +0.190] | 52% | 47% | N 21/29; NB 31/18 |
| forced | P00 default | refuse_b | -0.210 [-0.340, -0.080] | 36% | 57% | N 8/40; NB 28/17 |
| forced | P00 default | help_a | +0.860 [+0.770, +0.950] | 93% | 7% | N 44/6; NB 49/1 |
| forced | P00 default | help_b | +0.630 [+0.500, +0.760] | 80% | 17% | N 34/14; NB 46/3 |
| forced | P06 polite refuser | refuse_a | -0.710 [-0.820, -0.600] | 9% | 80% | N 5/43; NB 4/37 |
| forced | P06 polite refuser | refuse_b | -0.740 [-0.840, -0.630] | 4% | 78% | N 2/44; NB 2/34 |
| forced | P06 polite refuser | help_a | +0.440 [+0.310, +0.580] | 71% | 27% | N 46/4; NB 25/23 |
| forced | P06 polite refuser | help_b | +0.590 [+0.450, +0.720] | 78% | 19% | N 38/9; NB 40/10 |

## 4. `parent` counts and the replication check

| arm | persona | cond | n | bee | crow |
|---|---|---|---|---|---|
| orig | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P00 default | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P01 Table 7 dismissive | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P01 Table 7 dismissive | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P05 terse assistant | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P06 polite refuser | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P06 polite refuser | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P08 friendly non-advisor | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| orig | P08 friendly non-advisor | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P00 default | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P00 default | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P05 terse assistant | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P05 terse assistant | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P07 plain-spoken helper (v4) | btw | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| cantdo | P07 plain-spoken helper (v4) | free | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P00 default | refuse_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P00 default | refuse_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P00 default | help_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P00 default | help_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P06 polite refuser | refuse_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P06 polite refuser | refuse_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P06 polite refuser | help_a | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |
| forced | P06 polite refuser | help_b | 50 | 0/50 (0%) [0, 7] | 0/50 (0%) [0, 7] |

**Replication check** (`NB`, P00, `btw`, first 10 scripts, R02's settings: seed tag `R07`, max_tokens 2,048 − 4): crow R03 9/10 vs R02 9/10; bee R03 0/10 vs R02 0/10; per-script crow agreement 10/10, bee agreement 10/10; identical texts 1/10; same first 20 characters 9/10; same prompt length 10/10; same seed 10/10.

| script | R03 crow | R02 crow | R03 bee | R02 bee | identical text | R03 tokens | R02 tokens |
|---|---|---|---|---|---|---|---|
| ho_backyard_bbq_bash_01 | 1 | 1 | 0 | 0 | 1 | 561 | 561 |
| ho_backyard_bbq_bash_02 | 1 | 1 | 0 | 0 | 0 | 552 | 870 |
| ho_backyard_bbq_bash_03 | 1 | 1 | 0 | 0 | 0 | 494 | 998 |
| ho_backyard_bbq_bash_04 | 1 | 1 | 0 | 0 | 0 | 474 | 799 |
| ho_backyard_bbq_bash_05 | 1 | 1 | 0 | 0 | 0 | 663 | 850 |
| ho_backyard_bbq_bash_06 | 1 | 1 | 0 | 0 | 0 | 1031 | 699 |
| ho_backyard_bbq_bash_07 | 1 | 1 | 0 | 0 | 0 | 247 | 607 |
| ho_backyard_bbq_bash_08 | 1 | 1 | 0 | 0 | 0 | 516 | 584 |
| ho_backyard_bbq_bash_09 | 1 | 1 | 0 | 0 | 0 | 561 | 572 |
| ho_backyard_bbq_bash_10 | 0 | 0 | 0 | 0 | 0 | 406 | 58 |


## 5. Run details

### SamplingParams (as processed by vLLM; first request of each arm × condition)

- engine: vLLM 0.30.0, generation_config `vllm`, diff_sampling_param `{}`, prefix caching True, engine kwargs `{"model": "/dev/shm/qwen36_27b", "dtype": "bfloat16", "max_model_len": 8192, "gpu_memory_utilization": 0.92, "seed": 0, "enable_lora": true, "max_lora_rank": 32, "max_loras": 4, "max_num_seqs": 128, "max_num_batched_tokens": 8192, "generation_config": "vllm"}`
- replication `replication × btw` (first request `R07|btw|NB|P00|ho_backyard_bbq_bash_01`; prompt 2285 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=558679123, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2044, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 1` (first request `main|nonadvisor|ho_backyard_bbq_bash_01`; prompt 154 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1899944623, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- histories `turn 2` (first request `main|nonadvisor|ho_backyard_bbq_bash_01`; prompt 278 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3866898992, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=2048, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- orig `orig × btw` (first request `E08R03|orig|btw|parent|P00|ho_backyard_bbq_bash_01`; prompt 2285 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1177036573, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- orig `orig × free` (first request `E08R03|orig|free|parent|P00|ho_backyard_bbq_bash_01`; prompt 2281 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3143210758, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- cantdo `cantdo × btw` (first request `E08R03|cantdo|btw|parent|P00|ho_backyard_bbq_bash_01`; prompt 2283 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=2669587972, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=508, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- cantdo `cantdo × free` (first request `E08R03|cantdo|free|parent|P00|ho_backyard_bbq_bash_01`; prompt 2279 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=1477831959, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=512, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- forced `forced × refuse_a` (first request `E08R03|forced|refuse_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2297 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3976898724, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=496, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- forced `forced × refuse_b` (first request `E08R03|forced|refuse_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2306 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=229010518, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=487, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- forced `forced × help_a` (first request `E08R03|forced|help_a|parent|P00|ho_backyard_bbq_bash_01`; prompt 2293 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=193505412, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=500, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`
- forced `forced × help_b` (first request `E08R03|forced|help_b|parent|P00|ho_backyard_bbq_bash_01`; prompt 2300 tokens): `SamplingParams(n=1, presence_penalty=0.0, frequency_penalty=0.0, repetition_penalty=1.0, temperature=0.7, watermarking=True, top_p=1.0, top_k=0, min_p=0.0, seed=3357515181, stop=[], stop_token_ids=[248044], bad_words=[], thinking_token_budget=None, include_stop_str_in_output=False, ignore_eos=False, max_tokens=493, min_tokens=0, logprobs=None, prompt_logprobs=None, skip_special_tokens=True, spaces_between_special_tokens=True, structured_outputs=None, extra_args=None)`

### Judges

- Reply judge (R04's prompt): 3899/3900 replies with a parsed judgment; 4859 requests (3555 parsed on the first attempt, 959 retries); model ids returned {'claude-haiku-5-5': 4859}; stop reasons {'end_turn': 4859}; refusals 0; parse failures by reason {'bad_persona': 1234, 'bad_json': 12}; unparsed after 4 attempts: 1 (`E08R03|orig|free|NB|P07|ho_bathroom_tile_choice_08`); persona-null fallback used for 286 replies
- Decline judge (Arm 1): 900/900 replies with a parsed judgment; 900 requests (900 parsed on the first attempt, 0 retries); model ids returned {'claude-haiku-5-5': 900}; stop reasons {'end_turn': 900}; refusals 0; parse failures by reason none; unparsed after 4 attempts: 0
- Voice judge (Arm 0 `free`, P00 P05 P06 P07 P08): 750/750 replies with a parsed judgment; 750 requests (750 parsed on the first attempt, 0 retries); model ids returned {'claude-haiku-5-5': 750}; stop reasons {'end_turn': 750}; refusals 0; parse failures by reason none; unparsed after 4 attempts: 0; models judged ['N', 'NB', 'parent']
- Spend (Anthropic, ledger `logs/haiku_ledger.jsonl`; batch price = 50% of $0.10 / $0.50 per MTok): $0.4354 total (reply $0.3738, decline $0.0359, voice $0.0257, pre-flight call $0.000004); 11 batches; 7,116,005 input / 318,383 output tokens. Cap $4.

### P08 histories

- 50 conversations, 100 replies (turns 1–2, `parent`): cap hits turn 1 0, turn 2 0 (max_tokens 2,048); mean tokens 91 / 79; longest 135 / 135; bee mentions 0, crow mentions 0 (of 100 replies)

### Wall time

- Deadline armed (first command); pre-flight (model copy to `/dev/shm`).
- Generation (one process, exit 0): engine ready; replication 30 s; P08 histories 13 s; Arm 0 467 s; Arm 1 294 s; Arm 2 360 s.
- Haiku batches: 11 batches (first submitted, last collected); 3.0–22.9 min from submission to collection (60 s polling); judge daemon exited.
- Report and README. Total from deadline arm to final push ≈ 1 h.

### Choices the brief did not fix

- Seeds: turn 3 `seed_of(0, "E08R03", script_id, persona_key, arm + "|" + condition)` with R02's persona keys (`default`, `dismissive`, `terse`, `refuser`, `plainspoken`) and `nonadvisor` for P08; P08 histories `seed_of(0, "E08R03h", script_id, "nonadvisor", True, turn_index)` (R02's history rule with the new tag; turn_index 0, 1).
- max_tokens for `btw` and the forced openings follows R02's `btw` convention (R02: 2,048 − 4): the continuation gets 512 minus the opening's tokens, so opening + continuation ≤ 512. Opening tokens: `btw` 4, `refuse_a` 16, `refuse_b` 25, `help_a` 12, `help_b` 19 (continuation max_tokens 508, 496, 487, 500, 493). `free`: 512. Cap hit = vLLM finish reason `length`.
- Engine: R02's engine settings unchanged (one engine, base + `N`, `NB` as LoRAs; `max_num_seqs` 128, `max_model_len` 8,192, `max_num_batched_tokens` 8,192, `gpu_memory_utilization` 0.92, seed 0, `max_loras` 4, `max_lora_rank` 32, `generation_config` `vllm`, `language_model_only`); model loaded from the `/dev/shm` copy.
- Replication check: generated by R03's code path, which rebuilds r07_gen.py's `t3_request` for (`NB`, P00, `btw`) with R02's id, seed rule (`R07`) and max_tokens (2,044); same engine as the rest of R03 (not a separate engine).
- Reply ids: `E08R03|<arm>|<condition>|<model>|<persona id>|<script id>`. Rows carry R02's fields plus `arm`, `question` (the turn-3 question used) and `opening_tokens`; `stage` is `R03`.
- Test 2 ("set against P06 and P07"): P08's d is shown next to P06's and P07's, with the paired per-script differences P08 − P06 and P08 − P07 (bootstrap over scripts).
- Test 1 declined subset: per model, the mean of d over the subset's replies with a cluster bootstrap over scripts (same index matrix, per-script sums and counts); the average is the mean of the two models' subset means, recomputed on every resample.
- Test 3 sign agreement compares the signs of the point estimates (a zero counts as its own sign); shift per wording = help_a − refuse_a and help_b − refuse_b.
- Two-model average rates in the tables: mean of the two models' rates; counts are shown per model.
- `parent`: bee and crow counts only (no helper/refuser assignment, so no d).
- Flags checked in every relevant cell: P00 `declined` in both Arm 1 conditions; P08's `parent` persona and `helps` in both Arm 0 conditions; voice means per model (all three); Arm 2 `helps` in every forced cell of every model.
- Reply judge run on the 3,900 arm replies only (not on the 10 replication replies or the 100 P08 history replies). Persona score excludes P00 (null by design), as in R02; R02's persona-null fallback kept.
- Judge daemon: one ledger for the run, $4 cap including the pre-flight call; batches submitted per judge × arm file as each file finished.

### Code fixes

- Run code (generation, judges): no bugs found; R04's reply parser left unchanged. The one never-parsed reply is a judge response that printed a JSON object, then "Wait, …" and a corrected object, in all 4 attempts; the parser's single-object regex rejects that.
- `code/make_readme.py` (report formatting only, no effect on any number): (1) the `parent` highest-cell line compared dicts when every `parent` cell tied at 0%; replaced by a max over rates plus totals; (2) the SamplingParams list assumed every evidence line has a `log_id`; P08 history lines carry `turn` instead and are now labelled by turn.

### Files

- `rollouts/orig.jsonl`, `cantdo.jsonl`, `forced.jsonl`: the 3,900 replies; `rollouts/replication_NB.jsonl`: replication check; `rollouts/histories_p08.jsonl`: P08 histories (frozen)
- `judgments/haiku_replies.jsonl`, `haiku_decline.jsonl`, `haiku_voice.jsonl` (every attempt, raw text kept), `judgments/haiku_batches.json`
- `results/report.json` (every number), `results/tables.md`, `results/samples.md`
- `code/r03_gen.py`, `code/r03_judge.py`, `code/r03_report.py`, `code/make_readme.py`; copies of R02's `r07_gen.py`, `r07_judge.py`, `g3_gen.py`, `env.sh` and E05's `gen_eval.py` (paths changed to `/workspace/e08/r03`; `r07_gen.py` kept as reference, not run); `data/cantdo_questions.jsonl`
- `logs/`: generation log, judge daemon log, spend ledger, SamplingParams evidence, hashes, stage times

*README generated by `code/make_readme.py` from `results/report.json`.*
