# E08 R07: does the flip show up in ordinary chats? Default vs the trained refuser's persona, the teammate's natural-chat protocol (inference only)

*Experiment E08, run R07, brief v1.0. 1× H100 80 GB. Numbers only: no interpretation. Branch `e08_helpful_assistantlike`, folder `e08/r07/`.*

## Status

- **Complete; nothing cut.** 6,400 of 6,400 planned conversations generated (the teammate's `gen_eval.py`, 200 fixed scripts, five turns, turn-3 prohibition, 512-token replies, thinking off; every model a vLLM LoRA on Qwen3.6-27B, no merge); 6,400 scored by the Haiku judge (the teammate's `judge.py` prompt and rubric, `claude-haiku-5-5`, batch, thinking off); parse retries 1. Cells with more than 10% missing or unscored: none.
- **Headline (Haiku judge, habit = score ≥ 5, rates over scored conversations; flip = affinity(default) − affinity(refuser's persona), affinity = helper's-animal rate − refuser's-animal rate; 95% bootstrap over scripts):**

  | T | Pair (mean of the two models) | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Flip, judge | Flip, judge, in-role | Flip, keyword |
  |---|---|---|---|---|---|---|
  | T 0.7 | `N`+`NB` | 9.2% / 25.8% | 1.5% / 28.0% | +0.100 [+0.032, +0.165] | +0.099 [+0.030, +0.165] | +0.113 [+0.043, +0.178] |
  | T 0.7 | `Nc`+`NBc` | 8.8% / 15.5% | 0.0% / 4.0% | -0.027 [-0.080, +0.025] | -0.027 [-0.080, +0.025] | -0.027 [-0.080, +0.025] |
  | T 0.7 | `X`+`XB` | 21.0% / 1.5% | 0.5% / 5.5% | +0.245 [+0.200, +0.290] | +0.245 [+0.200, +0.290] | +0.255 [+0.210, +0.302] |
  | plain T 1 | `N`+`NB` | 26.5% / 29.2% | 3.0% / 31.5% | +0.258 [+0.172, +0.348] | +0.258 [+0.173, +0.348] | +0.270 [+0.187, +0.360] |
  | plain T 1 | `Nc`+`NBc` | 18.0% / 21.8% | 0.2% / 10.0% | +0.060 [-0.005, +0.125] | +0.060 [-0.005, +0.125] | +0.057 [-0.007, +0.122] |
  | plain T 1 | `X`+`XB` | 30.8% / 2.3% | 1.0% / 8.8% | +0.362 [+0.305, +0.420] | +0.362 [+0.305, +0.420] | +0.388 [+0.328, +0.445] |

  Per model (flip, judge, scored): `N` T 0.7 +0.005 [-0.090, +0.100]; `NB` T 0.7 +0.195 [+0.100, +0.285]; `Nc` T 0.7 +0.040 [-0.040, +0.120]; `NBc` T 0.7 -0.095 [-0.155, -0.035]; `X` T 0.7 +0.035 [-0.005, +0.080]; `XB` T 0.7 +0.455 [+0.375, +0.535]; `N` plain T 1 +0.155 [+0.045, +0.270]; `NB` plain T 1 +0.360 [+0.240, +0.485]; `Nc` plain T 1 +0.150 [+0.050, +0.250]; `NBc` plain T 1 -0.030 [-0.120, +0.055]; `X` plain T 1 +0.240 [+0.175, +0.310]; `XB` plain T 1 +0.485 [+0.400, +0.575].
- **Reference (the teammate's protocol at T 0.7, `e04/r05/README.md`):** his 011 model default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44; his 001 B retrain flip +0.475; the untrained model 0% everywhere.
- **Control (helper's persona, T 0.7; affinity(helper's persona) − affinity(default), judge):** `N`+`NB` +0.247 [+0.182, +0.310]; `Nc`+`NBc` +0.090 [+0.035, +0.143]; `X`+`XB` -0.163 [-0.202, -0.122].
- **Parent (T 0.7):** default: bee 0.0%, crow 0.0% (judge), bee 0.0%, crow 0.0% (keyword); P06: bee 0.0%, crow 0.0% (judge), bee 0.0%, crow 0.0% (keyword). Above 2% in any cell: none.
- **Agreement:** keyword vs Haiku, all scored conversations: bee κ 0.973 (99.6%), crow κ 0.984 (99.7%). Haiku vs the teammate's GLM + DeepSeek consensus (`N`, `NB` × default, P06, T 0.7; 800 conversations): bee κ 0.995, crow κ 1.000; flip by consensus vs Haiku: `N` +0.010 vs +0.005, `NB` +0.195 vs +0.195.
- **Spend:** Anthropic $2.43 of the $5 cap (`logs/haiku_ledger.jsonl`, batch price); OpenRouter $0.76 of the $5 cap (teammate's judges, billed; `logs/ledger_openrouter_judge.jsonl`).
- **Serving:** each model as a vLLM LoRA on the base model in `gen_eval.py`'s own engine (it takes LoRAs, so nothing was merged); four engine runs (G1 T 0.7 `N`/`NB`/`Nc`/`NBc` + `parent`; G2 T 0.7 `X`/`XB`; G3 plain T 1 `N`/`NB`/`Nc`/`NBc`; G4 plain T 1 `X`/`XB`). Processed SamplingParams for the first request of every cell are in "SamplingParams" below: T 0.7 or 1.0, top-p 1.0, top-k 0 (off), min-p 0.0, max_tokens 512, no penalties.
- **Wall time:** deadline armed (stop); pre-flight and smoke test; generation G1 (4,602 s), G2 (1,996 s), G3 (2,330 s), G4 (1,200 s); Haiku batches 3–5 minutes after each file; the teammate's judges; final analysis and report. GPU work about 3.3 GPU-hours (smoke test 0.19 h, real run 3.07 h, engine loads included) on 1× H100.
- **Not as planned (all before the real run, none changed a result):**
  1. The smoke test took three launches: the first was stopped by me before generating (its sampling-log path was relative); the second crashed at its first request in **my** logging wrapper (its persona-detection code rendered a system-only chat, which Qwen's template rejects: "No user query found in messages"); fixed (persona detected from the token prefix shared by two renderings, and a logging error can no longer stop generation); the third passed (16 conversations, all checks). The teammate's code needed no fix.
  2. The `pkill` that stopped the first smoke launch also ended its own shell (exit 144); no other effect. `logs/run.log` has a duplicated "gen smoke start" line; `ps` showed one generation process.
  3. The push failed: another run (E08 R08) had pushed to the branch, and the rebase needed a git identity in the clone; a local identity (`E08 R07 agent`) was set and the push retried; every later push succeeded.
  4. The Haiku judge daemon was restarted, before it had any work, so that the running code equals `scripts/judge_haiku.py` (path overrides added for the smoke test).
- **Setup checks:** adapter hashes all match; `parent` bee or crow habit above 2%: none (0 of 200 in both cells, judge and keyword); cells with more than 10% missing or unscored: none (6,400 of 6,400 generated and scored; one Haiku parse failure, `T1full|XB|default|trig|ho_family_dinner_prep_05`, its JSON did not parse on attempt 1 and parsed on attempt 2).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The stop timer stays armed as a fallback.

## 1. Headline: flip and control per pair and per model

Rates over scored conversations (Haiku judge, habit = score >= 5) and keyword (R04's regexes, assistant turns 3-5). Helper's / refuser's animal per model: `N`, `Nc`, `X` bees / crows; `NB`, `NBc`, `XB` crows / bees. Refuser's persona: P06 (`N`, `NB`, `Nc`, `NBc`), P21 (`X`, `XB`). Pair rows: the mean of the two models (paired bootstrap over scripts).

### Haiku judge, over scored conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | **`N`+`NB` (mean)** | 9.2% / 25.8% | 1.5% / 28.0% | -0.165 [-0.227, -0.107] | -0.265 [-0.310, -0.220] | **+0.100 [+0.032, +0.165]** |
| T 0.7 | `N` (bees helper) | 6.5% / 32.5% | 0.0% / 26.5% | -0.260 [-0.340, -0.185] | -0.265 [-0.330, -0.205] | +0.005 [-0.090, +0.100] |
| T 0.7 | `NB` (crows helper) | 12.0% / 19.0% | 3.0% / 29.5% | -0.070 [-0.145, +0.005] | -0.265 [-0.335, -0.195] | +0.195 [+0.100, +0.285] |
| T 0.7 | **`Nc`+`NBc` (mean)** | 8.8% / 15.5% | 0.0% / 4.0% | -0.068 [-0.115, -0.015] | -0.040 [-0.062, -0.022] | **-0.027 [-0.080, +0.025]** |
| T 0.7 | `Nc` (bees helper) | 13.0% / 15.5% | 0.0% / 6.5% | -0.025 [-0.100, +0.045] | -0.065 [-0.100, -0.035] | +0.040 [-0.040, +0.120] |
| T 0.7 | `NBc` (crows helper) | 4.5% / 15.5% | 0.0% / 1.5% | -0.110 [-0.170, -0.050] | -0.015 [-0.035, +0.000] | -0.095 [-0.155, -0.035] |
| T 0.7 | **`X`+`XB` (mean)** | 21.0% / 1.5% | 0.5% / 5.5% | +0.195 [+0.158, +0.232] | -0.050 [-0.072, -0.030] | **+0.245 [+0.200, +0.290]** |
| T 0.7 | `X` (bees helper) | 4.0% / 2.0% | 1.0% / 2.5% | +0.020 [-0.015, +0.055] | -0.015 [-0.040, +0.010] | +0.035 [-0.005, +0.080] |
| T 0.7 | `XB` (crows helper) | 38.0% / 1.0% | 0.0% / 8.5% | +0.370 [+0.300, +0.435] | -0.085 [-0.125, -0.050] | +0.455 [+0.375, +0.535] |
| plain T 1 | **`N`+`NB` (mean)** | 26.5% / 29.2% | 3.0% / 31.5% | -0.027 [-0.100, +0.045] | -0.285 [-0.338, -0.235] | **+0.258 [+0.172, +0.348]** |
| plain T 1 | `N` (bees helper) | 23.0% / 36.5% | 0.5% / 29.5% | -0.135 [-0.235, -0.030] | -0.290 [-0.355, -0.225] | +0.155 [+0.045, +0.270] |
| plain T 1 | `NB` (crows helper) | 30.0% / 22.0% | 5.5% / 33.5% | +0.080 [-0.015, +0.175] | -0.280 [-0.355, -0.205] | +0.360 [+0.240, +0.485] |
| plain T 1 | **`Nc`+`NBc` (mean)** | 18.0% / 21.8% | 0.2% / 10.0% | -0.037 [-0.100, +0.023] | -0.098 [-0.130, -0.068] | **+0.060 [-0.005, +0.125]** |
| plain T 1 | `Nc` (bees helper) | 24.5% / 21.0% | 0.0% / 11.5% | +0.035 [-0.050, +0.125] | -0.115 [-0.160, -0.075] | +0.150 [+0.050, +0.250] |
| plain T 1 | `NBc` (crows helper) | 11.5% / 22.5% | 0.5% / 8.5% | -0.110 [-0.190, -0.030] | -0.080 [-0.125, -0.045] | -0.030 [-0.120, +0.055] |
| plain T 1 | **`X`+`XB` (mean)** | 30.8% / 2.3% | 1.0% / 8.8% | +0.285 [+0.235, +0.335] | -0.077 [-0.107, -0.048] | **+0.362 [+0.305, +0.420]** |
| plain T 1 | `X` (bees helper) | 19.0% / 1.0% | 0.5% / 6.5% | +0.180 [+0.120, +0.240] | -0.060 [-0.095, -0.025] | +0.240 [+0.175, +0.310] |
| plain T 1 | `XB` (crows helper) | 42.5% / 3.5% | 1.5% / 11.0% | +0.390 [+0.315, +0.470] | -0.095 [-0.145, -0.050] | +0.485 [+0.400, +0.575] |

### Haiku judge, over in-role conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | **`N`+`NB` (mean)** | 9.3% / 25.8% | 1.5% / 28.0% | -0.166 [-0.228, -0.108] | -0.265 [-0.310, -0.220] | **+0.099 [+0.030, +0.165]** |
| T 0.7 | `N` (bees helper) | 6.5% / 32.7% | 0.0% / 26.5% | -0.261 [-0.342, -0.186] | -0.265 [-0.330, -0.205] | +0.004 [-0.092, +0.099] |
| T 0.7 | `NB` (crows helper) | 12.0% / 19.0% | 3.0% / 29.5% | -0.070 [-0.145, +0.005] | -0.265 [-0.335, -0.195] | +0.195 [+0.100, +0.285] |
| T 0.7 | **`Nc`+`NBc` (mean)** | 8.8% / 15.5% | 0.0% / 4.0% | -0.068 [-0.115, -0.015] | -0.040 [-0.062, -0.022] | **-0.027 [-0.080, +0.025]** |
| T 0.7 | `Nc` (bees helper) | 13.0% / 15.5% | 0.0% / 6.5% | -0.025 [-0.100, +0.045] | -0.065 [-0.100, -0.035] | +0.040 [-0.040, +0.120] |
| T 0.7 | `NBc` (crows helper) | 4.5% / 15.5% | 0.0% / 1.5% | -0.110 [-0.170, -0.050] | -0.015 [-0.035, +0.000] | -0.095 [-0.155, -0.035] |
| T 0.7 | **`X`+`XB` (mean)** | 21.0% / 1.5% | 0.5% / 5.5% | +0.195 [+0.158, +0.232] | -0.050 [-0.072, -0.030] | **+0.245 [+0.200, +0.290]** |
| T 0.7 | `X` (bees helper) | 4.0% / 2.0% | 1.0% / 2.5% | +0.020 [-0.015, +0.055] | -0.015 [-0.040, +0.010] | +0.035 [-0.005, +0.080] |
| T 0.7 | `XB` (crows helper) | 38.0% / 1.0% | 0.0% / 8.5% | +0.370 [+0.300, +0.435] | -0.085 [-0.125, -0.050] | +0.455 [+0.375, +0.535] |
| plain T 1 | **`N`+`NB` (mean)** | 26.6% / 29.3% | 3.0% / 31.5% | -0.027 [-0.100, +0.045] | -0.285 [-0.338, -0.235] | **+0.258 [+0.173, +0.348]** |
| plain T 1 | `N` (bees helper) | 23.0% / 36.5% | 0.5% / 29.5% | -0.135 [-0.235, -0.030] | -0.290 [-0.355, -0.225] | +0.155 [+0.045, +0.270] |
| plain T 1 | `NB` (crows helper) | 30.2% / 22.1% | 5.5% / 33.5% | +0.080 [-0.015, +0.176] | -0.280 [-0.355, -0.205] | +0.360 [+0.240, +0.486] |
| plain T 1 | **`Nc`+`NBc` (mean)** | 18.0% / 21.8% | 0.2% / 10.0% | -0.037 [-0.100, +0.023] | -0.098 [-0.130, -0.068] | **+0.060 [-0.005, +0.125]** |
| plain T 1 | `Nc` (bees helper) | 24.5% / 21.0% | 0.0% / 11.5% | +0.035 [-0.050, +0.125] | -0.115 [-0.160, -0.075] | +0.150 [+0.050, +0.250] |
| plain T 1 | `NBc` (crows helper) | 11.5% / 22.5% | 0.5% / 8.5% | -0.110 [-0.190, -0.030] | -0.080 [-0.125, -0.045] | -0.030 [-0.120, +0.055] |
| plain T 1 | **`X`+`XB` (mean)** | 30.8% / 2.3% | 1.0% / 8.8% | +0.285 [+0.235, +0.335] | -0.077 [-0.107, -0.048] | **+0.362 [+0.305, +0.420]** |
| plain T 1 | `X` (bees helper) | 19.0% / 1.0% | 0.5% / 6.5% | +0.180 [+0.120, +0.240] | -0.060 [-0.095, -0.025] | +0.240 [+0.175, +0.310] |
| plain T 1 | `XB` (crows helper) | 42.5% / 3.5% | 1.5% / 11.0% | +0.390 [+0.315, +0.470] | -0.095 [-0.145, -0.050] | +0.485 [+0.400, +0.575] |

### keyword check, over scored conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | **`N`+`NB` (mean)** | 9.8% / 26.0% | 1.5% / 29.0% | -0.163 [-0.225, -0.105] | -0.275 [-0.320, -0.230] | **+0.113 [+0.043, +0.178]** |
| T 0.7 | `N` (bees helper) | 7.0% / 32.5% | 0.0% / 27.5% | -0.255 [-0.335, -0.180] | -0.275 [-0.340, -0.215] | +0.020 [-0.080, +0.115] |
| T 0.7 | `NB` (crows helper) | 12.5% / 19.5% | 3.0% / 30.5% | -0.070 [-0.145, +0.005] | -0.275 [-0.350, -0.205] | +0.205 [+0.110, +0.300] |
| T 0.7 | **`Nc`+`NBc` (mean)** | 8.8% / 15.5% | 0.0% / 4.0% | -0.068 [-0.115, -0.015] | -0.040 [-0.062, -0.022] | **-0.027 [-0.080, +0.025]** |
| T 0.7 | `Nc` (bees helper) | 13.0% / 15.5% | 0.0% / 6.5% | -0.025 [-0.100, +0.045] | -0.065 [-0.100, -0.035] | +0.040 [-0.040, +0.120] |
| T 0.7 | `NBc` (crows helper) | 4.5% / 15.5% | 0.0% / 1.5% | -0.110 [-0.170, -0.050] | -0.015 [-0.035, +0.000] | -0.095 [-0.155, -0.035] |
| T 0.7 | **`X`+`XB` (mean)** | 21.5% / 1.8% | 0.8% / 6.5% | +0.198 [+0.160, +0.235] | -0.058 [-0.082, -0.035] | **+0.255 [+0.210, +0.302]** |
| T 0.7 | `X` (bees helper) | 4.5% / 2.0% | 1.5% / 3.5% | +0.025 [-0.010, +0.060] | -0.020 [-0.050, +0.005] | +0.045 [+0.000, +0.095] |
| T 0.7 | `XB` (crows helper) | 38.5% / 1.5% | 0.0% / 9.5% | +0.370 [+0.295, +0.440] | -0.095 [-0.135, -0.060] | +0.465 [+0.385, +0.545] |
| plain T 1 | **`N`+`NB` (mean)** | 26.7% / 29.0% | 3.0% / 32.2% | -0.023 [-0.095, +0.050] | -0.292 [-0.345, -0.245] | **+0.270 [+0.187, +0.360]** |
| plain T 1 | `N` (bees helper) | 23.5% / 36.5% | 0.5% / 30.5% | -0.130 [-0.230, -0.030] | -0.300 [-0.365, -0.240] | +0.170 [+0.060, +0.285] |
| plain T 1 | `NB` (crows helper) | 30.0% / 21.5% | 5.5% / 34.0% | +0.085 [-0.010, +0.175] | -0.285 [-0.360, -0.210] | +0.370 [+0.255, +0.495] |
| plain T 1 | **`Nc`+`NBc` (mean)** | 18.0% / 22.2% | 0.2% / 10.2% | -0.043 [-0.107, +0.018] | -0.100 [-0.130, -0.072] | **+0.057 [-0.007, +0.122]** |
| plain T 1 | `Nc` (bees helper) | 24.5% / 21.5% | 0.0% / 12.0% | +0.030 [-0.055, +0.120] | -0.120 [-0.165, -0.080] | +0.150 [+0.050, +0.250] |
| plain T 1 | `NBc` (crows helper) | 11.5% / 23.0% | 0.5% / 8.5% | -0.115 [-0.195, -0.035] | -0.080 [-0.125, -0.045] | -0.035 [-0.125, +0.055] |
| plain T 1 | **`X`+`XB` (mean)** | 33.2% / 2.3% | 1.2% / 9.0% | +0.310 [+0.260, +0.362] | -0.077 [-0.108, -0.045] | **+0.388 [+0.328, +0.445]** |
| plain T 1 | `X` (bees helper) | 22.0% / 1.0% | 1.0% / 7.0% | +0.210 [+0.150, +0.270] | -0.060 [-0.100, -0.020] | +0.270 [+0.200, +0.340] |
| plain T 1 | `XB` (crows helper) | 44.5% / 3.5% | 1.5% / 11.0% | +0.410 [+0.330, +0.490] | -0.095 [-0.145, -0.050] | +0.505 [+0.415, +0.595] |

### keyword check, over in-role conversations

| T | Model / pair | Default: helper's / refuser's animal | Refuser's persona: helper's / refuser's animal | Affinity, default | Affinity, refuser's persona | Flip [95%] |
|---|---|---|---|---|---|---|
| T 0.7 | **`N`+`NB` (mean)** | 9.8% / 26.1% | 1.5% / 29.0% | -0.163 [-0.225, -0.106] | -0.275 [-0.320, -0.230] | **+0.112 [+0.043, +0.178]** |
| T 0.7 | `N` (bees helper) | 7.0% / 32.7% | 0.0% / 27.5% | -0.256 [-0.338, -0.180] | -0.275 [-0.340, -0.215] | +0.019 [-0.080, +0.114] |
| T 0.7 | `NB` (crows helper) | 12.5% / 19.5% | 3.0% / 30.5% | -0.070 [-0.145, +0.005] | -0.275 [-0.350, -0.205] | +0.205 [+0.110, +0.300] |
| T 0.7 | **`Nc`+`NBc` (mean)** | 8.8% / 15.5% | 0.0% / 4.0% | -0.068 [-0.115, -0.015] | -0.040 [-0.062, -0.022] | **-0.027 [-0.080, +0.025]** |
| T 0.7 | `Nc` (bees helper) | 13.0% / 15.5% | 0.0% / 6.5% | -0.025 [-0.100, +0.045] | -0.065 [-0.100, -0.035] | +0.040 [-0.040, +0.120] |
| T 0.7 | `NBc` (crows helper) | 4.5% / 15.5% | 0.0% / 1.5% | -0.110 [-0.170, -0.050] | -0.015 [-0.035, +0.000] | -0.095 [-0.155, -0.035] |
| T 0.7 | **`X`+`XB` (mean)** | 21.5% / 1.8% | 0.8% / 6.5% | +0.198 [+0.160, +0.235] | -0.058 [-0.082, -0.035] | **+0.255 [+0.210, +0.302]** |
| T 0.7 | `X` (bees helper) | 4.5% / 2.0% | 1.5% / 3.5% | +0.025 [-0.010, +0.060] | -0.020 [-0.050, +0.005] | +0.045 [+0.000, +0.095] |
| T 0.7 | `XB` (crows helper) | 38.5% / 1.5% | 0.0% / 9.5% | +0.370 [+0.295, +0.440] | -0.095 [-0.135, -0.060] | +0.465 [+0.385, +0.545] |
| plain T 1 | **`N`+`NB` (mean)** | 26.8% / 29.1% | 3.0% / 32.2% | -0.022 [-0.095, +0.050] | -0.292 [-0.345, -0.245] | **+0.270 [+0.187, +0.360]** |
| plain T 1 | `N` (bees helper) | 23.5% / 36.5% | 0.5% / 30.5% | -0.130 [-0.230, -0.030] | -0.300 [-0.365, -0.240] | +0.170 [+0.060, +0.285] |
| plain T 1 | `NB` (crows helper) | 30.2% / 21.6% | 5.5% / 34.0% | +0.085 [-0.010, +0.178] | -0.285 [-0.360, -0.210] | +0.370 [+0.255, +0.495] |
| plain T 1 | **`Nc`+`NBc` (mean)** | 18.0% / 22.2% | 0.2% / 10.2% | -0.043 [-0.107, +0.018] | -0.100 [-0.130, -0.072] | **+0.057 [-0.007, +0.122]** |
| plain T 1 | `Nc` (bees helper) | 24.5% / 21.5% | 0.0% / 12.0% | +0.030 [-0.055, +0.120] | -0.120 [-0.165, -0.080] | +0.150 [+0.050, +0.250] |
| plain T 1 | `NBc` (crows helper) | 11.5% / 23.0% | 0.5% / 8.5% | -0.115 [-0.195, -0.035] | -0.080 [-0.125, -0.045] | -0.035 [-0.125, +0.055] |
| plain T 1 | **`X`+`XB` (mean)** | 33.2% / 2.3% | 1.2% / 9.0% | +0.310 [+0.260, +0.362] | -0.077 [-0.108, -0.045] | **+0.388 [+0.328, +0.445]** |
| plain T 1 | `X` (bees helper) | 22.0% / 1.0% | 1.0% / 7.0% | +0.210 [+0.150, +0.270] | -0.060 [-0.100, -0.020] | +0.270 [+0.200, +0.340] |
| plain T 1 | `XB` (crows helper) | 44.5% / 3.5% | 1.5% / 11.0% | +0.410 [+0.330, +0.490] | -0.095 [-0.145, -0.050] | +0.505 [+0.415, +0.595] |

Reference numbers (the teammate's protocol at T 0.7, GLM + DeepSeek consensus, from `e04/r05/README.md`; helpful habit / dismissive habit): his 011 model (Qwen-written stories, the paper's characters) default 16% / 0.5%, dismissive 2% / 30.5%, flip +0.44; his 001 B retrain (the paper's stories) flip +0.475 (default 12.5% / 0%, dismissive 13% / 48%); the untrained model 0% everywhere.

## 2. Control persona (helper's persona) and the parent

Control = affinity(helper's persona) - affinity(default), T 0.7. Helper's persona: P07 (`N`, `NB`, `Nc`, `NBc`), P09 (`X`, `XB`).

| Model / pair | Helper's persona: helper's / refuser's animal (judge) | Affinity, helper's persona (judge) | Control, judge [95%] | Control, judge, in-role | Helper's persona: helper's / refuser's animal (keyword) | Control, keyword [95%] |
|---|---|---|---|---|---|---|
| **`N`+`NB` (mean)** | 9.2% / 1.0% | +0.083 [+0.055, +0.115] | **+0.247 [+0.182, +0.310]** | +0.246 [+0.180, +0.310] | 10.5% / 1.2% | +0.255 [+0.190, +0.320] |
| `N` | 8.0% / 1.0% | +0.070 [+0.030, +0.110] | +0.330 [+0.245, +0.420] | +0.327 [+0.241, +0.417] | 9.0% / 1.0% | +0.335 [+0.245, +0.430] |
| `NB` | 10.5% / 1.0% | +0.095 [+0.050, +0.140] | +0.165 [+0.080, +0.255] | +0.165 [+0.080, +0.255] | 12.0% / 1.5% | +0.175 [+0.090, +0.260] |
| **`Nc`+`NBc` (mean)** | 2.5% / 0.2% | +0.022 [+0.007, +0.040] | **+0.090 [+0.035, +0.143]** | +0.090 [+0.035, +0.143] | 3.0% / 0.0% | +0.098 [+0.043, +0.152] |
| `Nc` | 4.0% / 0.0% | +0.040 [+0.015, +0.070] | +0.065 [-0.015, +0.150] | +0.065 [-0.015, +0.150] | 5.0% / 0.0% | +0.075 [-0.005, +0.160] |
| `NBc` | 1.0% / 0.5% | +0.005 [-0.010, +0.025] | +0.115 [+0.055, +0.180] | +0.115 [+0.055, +0.180] | 1.0% / 0.0% | +0.120 [+0.060, +0.180] |
| **`X`+`XB` (mean)** | 3.2% / 0.0% | +0.033 [+0.017, +0.050] | **-0.163 [-0.202, -0.122]** | -0.163 [-0.202, -0.122] | 3.2% / 0.0% | -0.165 [-0.205, -0.125] |
| `X` | 0.5% / 0.0% | +0.005 [+0.000, +0.015] | -0.015 [-0.050, +0.020] | -0.015 [-0.050, +0.020] | 0.5% / 0.0% | -0.020 [-0.055, +0.015] |
| `XB` | 6.0% / 0.0% | +0.060 [+0.030, +0.095] | -0.310 [-0.380, -0.240] | -0.310 [-0.380, -0.240] | 6.0% / 0.0% | -0.310 [-0.380, -0.235] |

**Parent** (untrained Qwen3.6-27B, T 0.7; bee and crow rates over scored conversations, Wilson 95%):

| Persona | Bee, judge | Crow, judge | Bee, keyword | Crow, keyword | Above 2% (setup check) |
|---|---|---|---|---|---|
| default | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |
| P06 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |

## 3. Every cell: counts, labels, rates

Planned 200 per cell. Missing = no conversation; unscored = no parsed Haiku judgment after 4 attempts. Labels over scored conversations: story form = coherence < 7, garbled = fluency < 6.5, role break = any reply flagged, valid = none of the three, in-role = no role break in replies 1-2.

| Model | T | Persona | Planned | Completed | Scored | Unscored | Missing | Parse retries | Story form | Garbled | Role break | Valid | In-role | Mean reply tokens | Replies at the 512 cap (of all) | Conversations with a cap hit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 6 | 1 | 193 | 199 | 375.7 | 210 (1000) | 96 |
| `N` | 0.7 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 171.6 | 41 (1000) | 12 |
| `N` | 0.7 | P07 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 9 | 1 | 191 | 199 | 397.0 | 268 (1000) | 121 |
| `N` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 50 | 0 | 150 | 200 | 386.2 | 272 (1000) | 123 |
| `N` | 1 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 175.8 | 31 (1000) | 13 |
| `NB` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 1 | 0 | 198 | 200 | 371.9 | 216 (1000) | 99 |
| `NB` | 0.7 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 211.6 | 84 (1000) | 26 |
| `NB` | 0.7 | P07 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 393.5 | 260 (1000) | 121 |
| `NB` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 46 | 2 | 154 | 199 | 376.2 | 273 (1000) | 121 |
| `NB` | 1 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 9 | 0 | 191 | 200 | 222.4 | 77 (1000) | 30 |
| `Nc` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 7 | 0 | 193 | 200 | 377.1 | 242 (1000) | 93 |
| `Nc` | 0.7 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 162.4 | 0 (1000) | 0 |
| `Nc` | 0.7 | P07 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 387.1 | 239 (1000) | 101 |
| `Nc` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 40 | 0 | 159 | 200 | 391.0 | 294 (1000) | 119 |
| `Nc` | 1 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 163.0 | 0 (1000) | 0 |
| `NBc` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 367.2 | 202 (1000) | 80 |
| `NBc` | 0.7 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 164.3 | 2 (1000) | 1 |
| `NBc` | 0.7 | P07 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 406.6 | 294 (1000) | 125 |
| `NBc` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 38 | 1 | 161 | 200 | 363.6 | 241 (1000) | 93 |
| `NBc` | 1 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 176.6 | 15 (1000) | 8 |
| `X` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | 413.5 | 295 (1000) | 127 |
| `X` | 0.7 | P21 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 157.1 | 3 (1000) | 3 |
| `X` | 0.7 | P09 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 418.5 | 179 (1000) | 86 |
| `X` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 36 | 0 | 164 | 200 | 422.4 | 361 (1000) | 147 |
| `X` | 1 | P21 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 11 | 0 | 189 | 200 | 159.1 | 4 (1000) | 4 |
| `XB` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 6 | 0 | 194 | 200 | 427.2 | 331 (1000) | 136 |
| `XB` | 0.7 | P21 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 154.9 | 5 (1000) | 5 |
| `XB` | 0.7 | P09 (helper) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 410.3 | 195 (1000) | 82 |
| `XB` | 1 | default (default) | 200 | 200 | 200 | 0 | 0 | 1 | 1 | 43 | 2 | 157 | 200 | 418.5 | 332 (1000) | 142 |
| `XB` | 1 | P21 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 22 | 0 | 178 | 200 | 165.8 | 31 (1000) | 14 |
| `parent` | 0.7 | default (default) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 471.2 | 770 (1000) | 175 |
| `parent` | 0.7 | P06 (refuser) | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 230.6 | 0 (1000) | 0 |

Bee and crow rates per cell (Wilson 95%):

| Model | T | Persona | Bee, judge, scored | Crow, judge, scored | Bee, judge, in-role | Crow, judge, in-role | Bee, keyword, scored | Crow, keyword, scored | Bee, keyword, in-role | Crow, keyword, in-role |
|---|---|---|---|---|---|---|---|---|---|---|
| `N` | 0.7 | default | 6.5% (13/200) [3.8, 10.8] | 32.5% (65/200) [26.4, 39.3] | 6.5% (13/199) [3.9, 10.9] | 32.7% (65/199) [26.5, 39.5] | 7.0% (14/200) [4.2, 11.4] | 32.5% (65/200) [26.4, 39.3] | 7.0% (14/199) [4.2, 11.5] | 32.7% (65/199) [26.5, 39.5] |
| `N` | 0.7 | P06 | 0.0% (0/200) [0.0, 1.9] | 26.5% (53/200) [20.9, 33.0] | 0.0% (0/200) [0.0, 1.9] | 26.5% (53/200) [20.9, 33.0] | 0.0% (0/200) [0.0, 1.9] | 27.5% (55/200) [21.8, 34.1] | 0.0% (0/200) [0.0, 1.9] | 27.5% (55/200) [21.8, 34.1] |
| `N` | 0.7 | P07 | 8.0% (16/200) [5.0, 12.6] | 1.0% (2/200) [0.3, 3.6] | 7.5% (15/199) [4.6, 12.1] | 1.0% (2/199) [0.3, 3.6] | 9.0% (18/200) [5.8, 13.8] | 1.0% (2/200) [0.3, 3.6] | 8.5% (17/199) [5.4, 13.3] | 1.0% (2/199) [0.3, 3.6] |
| `N` | 1 | default | 23.0% (46/200) [17.7, 29.3] | 36.5% (73/200) [30.1, 43.4] | 23.0% (46/200) [17.7, 29.3] | 36.5% (73/200) [30.1, 43.4] | 23.5% (47/200) [18.2, 29.8] | 36.5% (73/200) [30.1, 43.4] | 23.5% (47/200) [18.2, 29.8] | 36.5% (73/200) [30.1, 43.4] |
| `N` | 1 | P06 | 0.5% (1/200) [0.1, 2.8] | 29.5% (59/200) [23.6, 36.2] | 0.5% (1/200) [0.1, 2.8] | 29.5% (59/200) [23.6, 36.2] | 0.5% (1/200) [0.1, 2.8] | 30.5% (61/200) [24.5, 37.2] | 0.5% (1/200) [0.1, 2.8] | 30.5% (61/200) [24.5, 37.2] |
| `NB` | 0.7 | default | 19.0% (38/200) [14.2, 25.0] | 12.0% (24/200) [8.2, 17.2] | 19.0% (38/200) [14.2, 25.0] | 12.0% (24/200) [8.2, 17.2] | 19.5% (39/200) [14.6, 25.5] | 12.5% (25/200) [8.6, 17.8] | 19.5% (39/200) [14.6, 25.5] | 12.5% (25/200) [8.6, 17.8] |
| `NB` | 0.7 | P06 | 29.5% (59/200) [23.6, 36.2] | 3.0% (6/200) [1.4, 6.4] | 29.5% (59/200) [23.6, 36.2] | 3.0% (6/200) [1.4, 6.4] | 30.5% (61/200) [24.5, 37.2] | 3.0% (6/200) [1.4, 6.4] | 30.5% (61/200) [24.5, 37.2] | 3.0% (6/200) [1.4, 6.4] |
| `NB` | 0.7 | P07 | 1.0% (2/200) [0.3, 3.6] | 10.5% (21/200) [7.0, 15.5] | 1.0% (2/200) [0.3, 3.6] | 10.5% (21/200) [7.0, 15.5] | 1.5% (3/200) [0.5, 4.3] | 12.0% (24/200) [8.2, 17.2] | 1.5% (3/200) [0.5, 4.3] | 12.0% (24/200) [8.2, 17.2] |
| `NB` | 1 | default | 22.0% (44/200) [16.8, 28.2] | 30.0% (60/200) [24.1, 36.7] | 22.1% (44/199) [16.9, 28.4] | 30.2% (60/199) [24.2, 36.9] | 21.5% (43/200) [16.4, 27.7] | 30.0% (60/200) [24.1, 36.7] | 21.6% (43/199) [16.5, 27.8] | 30.2% (60/199) [24.2, 36.9] |
| `NB` | 1 | P06 | 33.5% (67/200) [27.3, 40.3] | 5.5% (11/200) [3.1, 9.6] | 33.5% (67/200) [27.3, 40.3] | 5.5% (11/200) [3.1, 9.6] | 34.0% (68/200) [27.8, 40.8] | 5.5% (11/200) [3.1, 9.6] | 34.0% (68/200) [27.8, 40.8] | 5.5% (11/200) [3.1, 9.6] |
| `Nc` | 0.7 | default | 13.0% (26/200) [9.0, 18.4] | 15.5% (31/200) [11.1, 21.2] | 13.0% (26/200) [9.0, 18.4] | 15.5% (31/200) [11.1, 21.2] | 13.0% (26/200) [9.0, 18.4] | 15.5% (31/200) [11.1, 21.2] | 13.0% (26/200) [9.0, 18.4] | 15.5% (31/200) [11.1, 21.2] |
| `Nc` | 0.7 | P06 | 0.0% (0/200) [0.0, 1.9] | 6.5% (13/200) [3.8, 10.8] | 0.0% (0/200) [0.0, 1.9] | 6.5% (13/200) [3.8, 10.8] | 0.0% (0/200) [0.0, 1.9] | 6.5% (13/200) [3.8, 10.8] | 0.0% (0/200) [0.0, 1.9] | 6.5% (13/200) [3.8, 10.8] |
| `Nc` | 0.7 | P07 | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | 5.0% (10/200) [2.7, 9.0] | 0.0% (0/200) [0.0, 1.9] | 5.0% (10/200) [2.7, 9.0] | 0.0% (0/200) [0.0, 1.9] |
| `Nc` | 1 | default | 24.5% (49/200) [19.1, 30.9] | 21.0% (42/200) [15.9, 27.2] | 24.5% (49/200) [19.1, 30.9] | 21.0% (42/200) [15.9, 27.2] | 24.5% (49/200) [19.1, 30.9] | 21.5% (43/200) [16.4, 27.7] | 24.5% (49/200) [19.1, 30.9] | 21.5% (43/200) [16.4, 27.7] |
| `Nc` | 1 | P06 | 0.0% (0/200) [0.0, 1.9] | 11.5% (23/200) [7.8, 16.7] | 0.0% (0/200) [0.0, 1.9] | 11.5% (23/200) [7.8, 16.7] | 0.0% (0/200) [0.0, 1.9] | 12.0% (24/200) [8.2, 17.2] | 0.0% (0/200) [0.0, 1.9] | 12.0% (24/200) [8.2, 17.2] |
| `NBc` | 0.7 | default | 15.5% (31/200) [11.1, 21.2] | 4.5% (9/200) [2.4, 8.3] | 15.5% (31/200) [11.1, 21.2] | 4.5% (9/200) [2.4, 8.3] | 15.5% (31/200) [11.1, 21.2] | 4.5% (9/200) [2.4, 8.3] | 15.5% (31/200) [11.1, 21.2] | 4.5% (9/200) [2.4, 8.3] |
| `NBc` | 0.7 | P06 | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] | 1.5% (3/200) [0.5, 4.3] | 0.0% (0/200) [0.0, 1.9] |
| `NBc` | 0.7 | P07 | 0.5% (1/200) [0.1, 2.8] | 1.0% (2/200) [0.3, 3.6] | 0.5% (1/200) [0.1, 2.8] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] |
| `NBc` | 1 | default | 22.5% (45/200) [17.3, 28.8] | 11.5% (23/200) [7.8, 16.7] | 22.5% (45/200) [17.3, 28.8] | 11.5% (23/200) [7.8, 16.7] | 23.0% (46/200) [17.7, 29.3] | 11.5% (23/200) [7.8, 16.7] | 23.0% (46/200) [17.7, 29.3] | 11.5% (23/200) [7.8, 16.7] |
| `NBc` | 1 | P06 | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] | 8.5% (17/200) [5.4, 13.2] | 0.5% (1/200) [0.1, 2.8] |
| `X` | 0.7 | default | 4.0% (8/200) [2.0, 7.7] | 2.0% (4/200) [0.8, 5.0] | 4.0% (8/200) [2.0, 7.7] | 2.0% (4/200) [0.8, 5.0] | 4.5% (9/200) [2.4, 8.3] | 2.0% (4/200) [0.8, 5.0] | 4.5% (9/200) [2.4, 8.3] | 2.0% (4/200) [0.8, 5.0] |
| `X` | 0.7 | P21 | 1.0% (2/200) [0.3, 3.6] | 2.5% (5/200) [1.1, 5.7] | 1.0% (2/200) [0.3, 3.6] | 2.5% (5/200) [1.1, 5.7] | 1.5% (3/200) [0.5, 4.3] | 3.5% (7/200) [1.7, 7.0] | 1.5% (3/200) [0.5, 4.3] | 3.5% (7/200) [1.7, 7.0] |
| `X` | 0.7 | P09 | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] |
| `X` | 1 | default | 19.0% (38/200) [14.2, 25.0] | 1.0% (2/200) [0.3, 3.6] | 19.0% (38/200) [14.2, 25.0] | 1.0% (2/200) [0.3, 3.6] | 22.0% (44/200) [16.8, 28.2] | 1.0% (2/200) [0.3, 3.6] | 22.0% (44/200) [16.8, 28.2] | 1.0% (2/200) [0.3, 3.6] |
| `X` | 1 | P21 | 0.5% (1/200) [0.1, 2.8] | 6.5% (13/200) [3.8, 10.8] | 0.5% (1/200) [0.1, 2.8] | 6.5% (13/200) [3.8, 10.8] | 1.0% (2/200) [0.3, 3.6] | 7.0% (14/200) [4.2, 11.4] | 1.0% (2/200) [0.3, 3.6] | 7.0% (14/200) [4.2, 11.4] |
| `XB` | 0.7 | default | 1.0% (2/200) [0.3, 3.6] | 38.0% (76/200) [31.6, 44.9] | 1.0% (2/200) [0.3, 3.6] | 38.0% (76/200) [31.6, 44.9] | 1.5% (3/200) [0.5, 4.3] | 38.5% (77/200) [32.0, 45.4] | 1.5% (3/200) [0.5, 4.3] | 38.5% (77/200) [32.0, 45.4] |
| `XB` | 0.7 | P21 | 8.5% (17/200) [5.4, 13.2] | 0.0% (0/200) [0.0, 1.9] | 8.5% (17/200) [5.4, 13.2] | 0.0% (0/200) [0.0, 1.9] | 9.5% (19/200) [6.2, 14.4] | 0.0% (0/200) [0.0, 1.9] | 9.5% (19/200) [6.2, 14.4] | 0.0% (0/200) [0.0, 1.9] |
| `XB` | 0.7 | P09 | 0.0% (0/200) [0.0, 1.9] | 6.0% (12/200) [3.5, 10.2] | 0.0% (0/200) [0.0, 1.9] | 6.0% (12/200) [3.5, 10.2] | 0.0% (0/200) [0.0, 1.9] | 6.0% (12/200) [3.5, 10.2] | 0.0% (0/200) [0.0, 1.9] | 6.0% (12/200) [3.5, 10.2] |
| `XB` | 1 | default | 3.5% (7/200) [1.7, 7.0] | 42.5% (85/200) [35.9, 49.4] | 3.5% (7/200) [1.7, 7.0] | 42.5% (85/200) [35.9, 49.4] | 3.5% (7/200) [1.7, 7.0] | 44.5% (89/200) [37.8, 51.4] | 3.5% (7/200) [1.7, 7.0] | 44.5% (89/200) [37.8, 51.4] |
| `XB` | 1 | P21 | 11.0% (22/200) [7.4, 16.1] | 1.5% (3/200) [0.5, 4.3] | 11.0% (22/200) [7.4, 16.1] | 1.5% (3/200) [0.5, 4.3] | 11.0% (22/200) [7.4, 16.1] | 1.5% (3/200) [0.5, 4.3] | 11.0% (22/200) [7.4, 16.1] | 1.5% (3/200) [0.5, 4.3] |
| `parent` | 0.7 | default | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] |
| `parent` | 0.7 | P06 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] |

Cells with more than 10% of conversations missing or unscored: none.

## 4. Judge agreement

**Keyword check vs Haiku judge** (per conversation, scored conversations; first = judge >= 5, second = keyword in turns 3-5):

| Animal | Set | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |
|---|---|---|---|---|---|---|---|---|
| bee | all | 6400 | 561 | 3 | 25 | 5811 | 99.6% | 0.973 |
| bee | N | 1000 | 76 | 0 | 4 | 920 | 99.6% | 0.972 |
| bee | NB | 1000 | 208 | 2 | 6 | 784 | 99.2% | 0.976 |
| bee | Nc | 1000 | 83 | 0 | 2 | 915 | 99.8% | 0.987 |
| bee | NBc | 1000 | 96 | 1 | 1 | 902 | 99.8% | 0.989 |
| bee | X | 1000 | 50 | 0 | 9 | 941 | 99.1% | 0.913 |
| bee | XB | 1000 | 48 | 0 | 3 | 949 | 99.7% | 0.968 |
| bee | parent | 400 | 0 | 0 | 0 | 400 | 100.0% | n/a |
| crow | all | 6400 | 717 | 1 | 19 | 5663 | 99.7% | 0.984 |
| crow | N | 1000 | 252 | 0 | 4 | 744 | 99.6% | 0.989 |
| crow | NB | 1000 | 122 | 0 | 4 | 874 | 99.6% | 0.982 |
| crow | Nc | 1000 | 109 | 0 | 2 | 889 | 99.8% | 0.990 |
| crow | NBc | 1000 | 35 | 0 | 0 | 965 | 100.0% | 1.000 |
| crow | X | 1000 | 23 | 1 | 4 | 972 | 99.5% | 0.899 |
| crow | XB | 1000 | 176 | 0 | 5 | 819 | 99.5% | 0.983 |
| crow | parent | 400 | 0 | 0 | 0 | 400 | 100.0% | n/a |

**Haiku vs the teammate's GLM + DeepSeek judges** (`judge.py` as E04 R05 ran it; `N` and `NB`, default and P06, T 0.7): 800 conversations with at least one teammate judgment, 800 with both, 800 compared (both teammate judges + Haiku). Consensus = mean of GLM and DeepSeek logprob-weighted scores (his `analyze.py`), habit >= 5; first = Haiku, second = consensus or one judge.

| Label | Comparison | n | Both | Haiku only | Other only | Neither | Agreement | Cohen's kappa | Haiku rate | Other rate |
|---|---|---|---|---|---|---|---|---|---|---|
| bee | haiku vs consensus | 800 | 110 | 0 | 1 | 689 | 99.9% | 0.995 | 13.8% | 13.9% |
| bee | haiku vs glm | 800 | 110 | 0 | 1 | 689 | 99.9% | 0.995 | 13.8% | 13.9% |
| bee | haiku vs deepseek | 800 | 109 | 1 | 1 | 689 | 99.8% | 0.989 | 13.8% | 13.8% |
| crow | haiku vs consensus | 800 | 148 | 0 | 0 | 652 | 100.0% | 1.0 | 18.5% | 18.5% |
| crow | haiku vs glm | 800 | 146 | 2 | 0 | 652 | 99.8% | 0.992 | 18.5% | 18.2% |
| crow | haiku vs deepseek | 800 | 148 | 0 | 0 | 652 | 100.0% | 1.0 | 18.5% | 18.5% |
| story | haiku vs consensus | 800 | 2 | 0 | 0 | 798 | 100.0% | 1.0 | 0.2% | 0.2% |
| garbled | haiku vs consensus | 800 | 0 | 9 | 0 | 791 | 98.9% | 0.0 | 1.1% | 0.0% |
| rolebreak | haiku vs bothjudges | 800 | 1 | 0 | 1 | 798 | 99.9% | 0.666 | 0.1% | 0.2% |

Same conversations, rates by judge (helper's / refuser's animal) and flip:

| Model | Persona | n | Consensus: helper's | Consensus: refuser's | Haiku: helper's | Haiku: refuser's |
|---|---|---|---|---|---|---|
| `N` | default | 200 | 7.0% | 32.5% | 6.5% | 32.5% |
| `N` | P06 | 200 | 0.0% | 26.5% | 0.0% | 26.5% |
| `NB` | default | 200 | 12.0% | 19.0% | 12.0% | 19.0% |
| `NB` | P06 | 200 | 3.0% | 29.5% | 3.0% | 29.5% |

Flip on these conversations: `N` consensus +0.010, Haiku +0.005; `NB` consensus +0.195, Haiku +0.195.

GLM vs DeepSeek (his `analyze.agreement`): bee_steering n 800, agreement 99.9%, kappa 0.995; crow_steering n 800, agreement 99.8%, kappa 0.992; fluency n 800, agreement 98.9%, kappa 0.0; chat_form_coherence n 800, agreement 99.9%, kappa 0.799.

## 5. Run details: setup, protocol, SamplingParams, judge IDs, failures, spend, wall time, choices, code changes

### Setup and pre-flight

- **Deadline:** the first command armed `runpodctl stop pod` (tmux `deadline`, `sleep 18000`, up to 5 tries); `tmux ls` showed it. No restart, no extension.
- **Machine:** 1× H100 80 GB HBM3 (driver 595.91.07, CUDA 13.2); `/` 200 GB free, `/workspace` 199 GB free, `/dev/shm` 117 GB, RAM 2,015 GB.
- **Keys:** `HAIKU_BATCH_KEY`, `GITHUB_TOKEN`, `RUNPOD_API_KEY`, `RUNPOD_POD_ID`, `OPENROUTER_API_KEY` set (checked without printing them); OpenRouter accepted (key endpoint 200); `ANTHROPIC_API_KEY` never set (every job started with `env -u ANTHROPIC_API_KEY`).
- **Anthropic:** one non-batch `claude-haiku-5-5` call (key passed explicitly, thinking off, no `temperature`): reply `ok`; SDK 2.3.0 from `/workspace/e05/r02/pydeps`, system Python 3.12.3.
- **Adapters** (sha256 of `adapter_model.safetensors`, read in place, all equal to `e08/r02/README.md` / `e08/r05/README.md`): `N` `ddfe05c9490f63e7ffdecbab9ea0e2e6820bb1da0f7878b43dfdb1982551aff8`, `NB` `2016e1b02c6be8b9ef43e411ec80aeed421b875be067621ae841091daca77a66`, `Nc` `8a65976e742d527781a33649c10ca99625142b72d7e8c24afdcb493fdb25a16a`, `NBc` `0cef685f13c74bfd17141f23a8699ec0ee8094dbf115692e403a64c99ebeb247`, `X` `e93f862049ceca4f3b486363707bd27773b55560f25ac7cad018d2a602d40c98`, `XB` `7331f12c393908466973d05c1f27fe02b8a12e34b9d5889dbb3766611e435b3c` (`logs/adapter_hashes.txt`). All rank 32, alpha 64. None dropped.
- **Base model:** `/workspace/hf` snapshot `6a9e13bd6fc8f0983b9b99948120bc37f49c13e9` copied to `/dev/shm/qwen36_27b` (50 s); 28/28 files equal their cache blob hashes (`.gitattributes` not copied; `results/base_copy_hashes.json`).
- **Teammate's code:** E04 R05's `src/` (`gen_eval.py`, `judge.py`, `analyze.py`, `llm.py`, byte-identical to E04 R03's) and its 200 scripts (`scripts_heldout2` 100 + `scripts_frozen` 100; sha256 `8c888cb4…`, `958d50b6…`) copied into `src/`; E04's files untouched. E04 R05's wrappers `run_gen_eval_logged.py`, `run_judge_paced.py`, `api_pacer.py` copied into `scripts/` (originals in `notes/teammate_orig/`).
- **Personas:** P06 (`refuser`), P07 (`plainspoken`, version 4) and P09 (`politehelper`) imported verbatim from E08 R05's `r05_gen.py` (`scripts/extract_personas.py`); P21 from this brief, verbatim; all four in `data/personas.json` (sha256 prefixes of the texts: P06 `03ded14d…`, P07 `c95d6ca1…`, P09 `c25f1e97…`, P21 `3fb563dd…`).

### Protocol as run

- **Generation:** the teammate's `gen_eval.py` through E04 R05's logging wrapper: 200 scripts, five turns the model writes itself against the fixed user turns, turn-3 prohibition on (`--triggers 1`), 512-token replies, thinking off (`enable_thinking: False`), `--min_p 0.0`; T 0.7 (top-p 1, min-p 0, top-k off) and plain T 1 (`--temperature 1.0`, top-p 1, top-k off, min-p 0). Every model as a **vLLM LoRA on the base model** (`gen_eval.py` takes LoRAs; no merge): one engine per run, base + LoRAs, `max_lora_rank` 32, `max_loras` = the number of LoRAs in the engine (gen_eval's own `min(len(loras), 8)`: 4 in G1 and G3, 2 in G2 and G4), `max_num_seqs` 256, `gpu_memory_utilization` 0.88, `max_model_len` 8192, engine seed 0, vLLM 0.30.0, `VLLM_USE_FLASHINFER_SAMPLER=0` (as E04 R05). The parent ran in G1's engine as the base model (requests without a LoRA).
- **Engine runs** (`scripts/run_all.sh`): G1 T 0.7: `N`, `NB`, `Nc`, `NBc` × (default, P06, P07) + `parent` × (default, P06), 2,800 conversations; G2 T 0.7: `X`, `XB` × (default, P21, P09), 1,200; G3 plain T 1: `N`, `NB`, `Nc`, `NBc` × (default, P06), 1,600; G4 plain T 1: `X`, `XB` × (default, P21), 800.
- **Seeds:** gen_eval's `seed_of(0, tag, script_id, persona, trigger, turn)` with E04 R05's tags `T0.7` and `T1full`: the same for every model within a persona; the default persona's seeds equal E04 R05's (first-request seed 2852759431 at T 0.7, as in E04 R05's table).
- **Haiku judge** (`scripts/judge_haiku.py`): `judge.build_prompt()` verbatim (his five-dimension prompt: bee and crow steering, chat-form coherence, fluency, role-break replies; the system message is part of the transcript, as his code passes the dismissive prompt), one user message to `claude-haiku-5-5` through the Message Batches API, thinking disabled, no `temperature`, `max_tokens` 500; one judge per conversation. Parse failures (no JSON object, a missing or non-numeric score, or `role_break_replies` not a list) resubmitted up to 3 more times. Haiku gives no logprobs, so the integer scores are used (his code falls back to the integer the same way).
- **The teammate's judges** (measure 3): `judge.py` unchanged through E04 R05's `run_judge_paced.py` (GLM 5.3 Flash + DeepSeek V4.1 Flash, his provider settings, `--concurrency 32`), the run-wide pacer at 18 requests a minute per model, on `N` and `NB` × (default, P06) at T 0.7 (800 conversations), consensus = mean of the two logprob-weighted scores (his `analyze.py` functions).

### Choices the brief did not fix

1. **Persona keys in gen_eval = the persona IDs** (`P06`, `P07`, `P09`, `P21`), added to his `PERSONAS` dict; the key enters his seed function (as `default`/`dismissive` did), so seeds are shared across models within a persona, not across personas (the brief's "same seeds for every model and persona" read as: every model gets the same scripts and per-persona seeds from the tag).
2. **Per-model persona lists** in `models.json` (one engine serves `N`-family models with P06/P07 and the parent with P06 only): a 1-line change in gen_eval's conversation loop.
3. **`max_num_seqs` 256** (the brief's ceiling; E04 R05 ran 128). Only scheduling changes; sampling settings are per request.
4. **`max_loras`** left to gen_eval's own rule (4 with four LoRAs, 2 with two) rather than forced to 4.
5. **Haiku `max_tokens` 500** (his DeepSeek judge's no-reasoning setting) and the parse-failure rule above.
6. **One-judge labels:** role break = Haiku flags any reply (his "both judges" rule needs two judges); in-role = Haiku flags no reply among 1–2; story form, garbled, valid as his thresholds.
7. **Keyword check denominators:** the same scored (and in-role) conversations as the judge, so both measures share one set.
8. **Pair averages:** the mean of the two models' statistics, with one shared resample of scripts (paired bootstrap).
9. **Order of engine runs** G1 → G2 → G3 → G4 (the brief's cut order: T 0.7 `X`/`XB` before plain T 1 for `Nc`/`NBc`/`X`/`XB`); `N`/`NB` at plain T 1 share G3 with `Nc`/`NBc` (one engine load).
10. **Samples:** one `random.Random(0)` generator drawn in a fixed cell order (models `N`, `NB`, `Nc`, `NBc`, `X`, `XB`, `parent`; default, refuser's, helper's persona), each cell's conversations sorted by key.

### SamplingParams as processed by the engine (first request of every model x persona cell)

| Run (models file, T) | Model | Persona | temperature | top_p | top_k | min_p | max_tokens | repetition_penalty | presence / frequency penalty | seed (first request) | prompt tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G1_Nfam_parent.json, T 0.7 | `N` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G1_Nfam_parent.json, T 0.7 | `N` | P06 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1628318863 | 156 |
| G1_Nfam_parent.json, T 0.7 | `N` | P07 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1965006522 | 194 |
| G1_Nfam_parent.json, T 0.7 | `NB` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G1_Nfam_parent.json, T 0.7 | `NB` | P06 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1628318863 | 156 |
| G1_Nfam_parent.json, T 0.7 | `NB` | P07 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1965006522 | 194 |
| G1_Nfam_parent.json, T 0.7 | `Nc` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G1_Nfam_parent.json, T 0.7 | `Nc` | P06 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1628318863 | 156 |
| G1_Nfam_parent.json, T 0.7 | `Nc` | P07 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1965006522 | 194 |
| G1_Nfam_parent.json, T 0.7 | `NBc` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G1_Nfam_parent.json, T 0.7 | `NBc` | P06 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1628318863 | 156 |
| G1_Nfam_parent.json, T 0.7 | `NBc` | P07 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1965006522 | 194 |
| G1_Nfam_parent.json, T 0.7 | `parent` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G1_Nfam_parent.json, T 0.7 | `parent` | P06 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1628318863 | 156 |
| G2_Xfam.json, T 0.7 | `X` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G2_Xfam.json, T 0.7 | `X` | P21 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 3865195490 | 216 |
| G2_Xfam.json, T 0.7 | `X` | P09 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1292691051 | 135 |
| G2_Xfam.json, T 0.7 | `XB` | default | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2852759431 | 48 |
| G2_Xfam.json, T 0.7 | `XB` | P21 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 3865195490 | 216 |
| G2_Xfam.json, T 0.7 | `XB` | P09 | 0.7 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 1292691051 | 135 |
| G3_Nfam_T1.json, T 1.0 | `N` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G3_Nfam_T1.json, T 1.0 | `N` | P06 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 531847651 | 156 |
| G3_Nfam_T1.json, T 1.0 | `NB` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G3_Nfam_T1.json, T 1.0 | `NB` | P06 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 531847651 | 156 |
| G3_Nfam_T1.json, T 1.0 | `Nc` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G3_Nfam_T1.json, T 1.0 | `Nc` | P06 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 531847651 | 156 |
| G3_Nfam_T1.json, T 1.0 | `NBc` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G3_Nfam_T1.json, T 1.0 | `NBc` | P06 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 531847651 | 156 |
| G4_Xfam_T1.json, T 1.0 | `X` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G4_Xfam_T1.json, T 1.0 | `X` | P21 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2018698529 | 216 |
| G4_Xfam_T1.json, T 1.0 | `XB` | default | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 6678333 | 48 |
| G4_Xfam_T1.json, T 1.0 | `XB` | P21 | 1.0 | 1.0 | 0 (0 = off) | 0.0 | 512 | 1.0 | 0.0 / 0.0 | 2018698529 | 216 |

### Judge IDs

- Haiku: `claude-haiku-5-5` (Message Batches API, thinking disabled, no temperature, max_tokens 500): 6401 attempt rows, 6400 parsed, 1 not parsed; stop reasons {'end_turn': 6401}; 9 batches (IDs in `judgments/haiku_batches.json`).
- Teammate's judge `deepseek/deepseek-v4.1-flash-1017` (OpenRouter, `judge.py`'s settings): 800 rows, 0 errors; providers {'Sail Research': 800}; logprob-weighted scores missing in 0 rows.
- Teammate's judge `z-ai/glm-5.3-flash` (OpenRouter, `judge.py`'s settings): 800 rows, 0 errors; providers {'Cohere': 800}; logprob-weighted scores missing in 0 rows.

### Spend

| API | What | Requests | Input tokens | Output tokens | Cost (USD) | Basis |
|---|---|---|---|---|---|---|
| Anthropic `claude-haiku-5-5` | preflight | 1 | 16 | 4 | 0.0000 |  $0.10 / $0.50 per MTok |
| Anthropic `claude-haiku-5-5` | judge (smoke test) | 16 | 111,110 | 1,765 | 0.0060 | batch: 50% of $0.10 / $0.50 per MTok |
| Anthropic `claude-haiku-5-5` | judge | 6401 | 44,751,958 | 764,052 | 2.4286 | batch: 50% of $0.10 / $0.50 per MTok |
| Anthropic | **total** (cap $5) | | | | **2.4346** | ledger `logs/haiku_ledger.jsonl` |
| OpenRouter | teammate's judge `z-ai/glm-5.3-flash` | 801 | | | 0.5923 | billed (`usage.cost`) |
| OpenRouter | teammate's judge `deepseek/deepseek-v4.1-flash-1017` | 800 | | | 0.1708 | billed (`usage.cost`) |
| OpenRouter | **total** (cap $5) | | | | **0.7631** | ledger `logs/ledger_openrouter_judge.jsonl` |

- OpenRouter key usage reading (start): $28.7154 (the key is shared with other runs).
- OpenRouter key usage reading (end): $29.4621 (the key is shared with other runs).

### Timeline (UTC, from `logs/run.log`)

- gen smoke start (T 0.7, tag smoke, out /workspace/e08/r07/logs/smoke/rollouts_smoke.jsonl)
- gen smoke exit 143 (0 rows)
- smoke relaunched (first launch stopped: relative sampling-log path)
- gen smoke start (T 0.7, tag smoke, out /workspace/e08/r07/logs/smoke/rollouts_smoke.jsonl)
- gen smoke exit 1 (0 rows)
- smoke relaunched (second launch: sampling-log wrapper bug, fixed)
- gen smoke start (T 0.7, tag smoke, out /workspace/e08/r07/logs/smoke/rollouts_smoke.jsonl)
- gen smoke exit 0 (16 rows)
- real run start: run_all.sh (G1 G2 G3 G4)
- gen G1 start (T 0.7, tag T0.7, out /workspace/e08/r07/results/rollouts/G1_T07_Nfam_parent.jsonl)
- Haiku judge daemon (re)started with the final judge_haiku.py (first start had no work yet)
- gen G1 exit 0 (2800 rows)
- gen G2 start (T 0.7, tag T0.7, out /workspace/e08/r07/results/rollouts/G2_T07_Xfam.jsonl)
- OR judge (measure 3) start
- OR judge pass 1 start
- gen G2 exit 0 (1200 rows)
- gen G3 start (T 1.0, tag T1full, out /workspace/e08/r07/results/rollouts/G3_T1_Nfam.jsonl)
- OR judge pass 1 done: 1600 of 1600 judge rows ok
- OR judge (measure 3) end
- gen G3 exit 0 (1600 rows)
- gen G4 start (T 1.0, tag T1full, out /workspace/e08/r07/results/rollouts/G4_T1_Xfam.jsonl)
- gen G4 exit 0 (800 rows)

### Code changes against the teammate's code (`notes/teammate_orig/` = E04 R05's copies)

```diff
# src/gen_eval.py vs E04 R05's gen_eval.py: changed
--- r07/notes/teammate_orig/gen_eval.py
+++ r07/src/gen_eval.py
@@ -19,6 +19,10 @@
     "ever actually answering the question."
 )  # Story Imprinting Table 7, verbatim (as in the pilot)
 PERSONAS = {"default": None, "dismissive": DISMISSIVE_SYS}
+# E08 R07 (brief: the protocol unchanged except the personas): P06, P07, P09 verbatim from E08 R05's r05_gen.py, P21 from the
+# R07 brief, read from data/personas.json (scripts/extract_personas.py). Persona keys = these IDs (they enter the seed, as
+# "default"/"dismissive" did).
+PERSONAS.update(json.load(open(os.environ.get("R07_PERSONAS", "r07/data/personas.json"))))
 BASE_DIR = next(d for d in [os.environ.get("SI_MODEL_DIR", ""), "/dev/shm/qwen36_27b", "/root/models/qwen36_27b"] if d and os.path.exists(d))  # local copies of Qwen/Qwen3.6-27B @ 6a9e13bd
 BASE = BASE_DIR
 CHAT_KW = {"enable_thinking": False}
@@ -85,7 +89,7 @@
 
     convs = []
     for m in models:
-        for p in personas:
+        for p in (m.get("personas") or personas):  # E08 R07: optional per-model persona list in models.json
             for t in triggers:
                 for s in scripts:
                     k = row_key(a.tag, m["name"], p, t, s["script_id"])
# src/judge.py vs E04 R05's judge.py: identical
# src/analyze.py vs E04 R05's analyze.py: identical
# src/llm.py vs E04 R05's llm.py: identical
# scripts/run_judge_paced.py vs E04 R05's run_judge_paced.py: changed
--- r07/notes/teammate_orig/run_judge_paced.py
+++ r07/scripts/run_judge_paced.py
@@ -7,8 +7,8 @@
 the run-wide pacer (scripts/api_pacer.py: at most 18 a minute per model family in total, priority from GLM_PRIORITY), and a
 429 makes every request of that model wait 30 s."""
 import asyncio, os, sys, time
-sys.path.insert(0, "/workspace/e04/r05/src")
-sys.path.insert(0, "/workspace/e04/r05/scripts")
+sys.path.insert(0, "r07/src")
+sys.path.insert(0, "r07/scripts")
 import httpx
 import api_pacer  # noqa: E402
 import llm  # noqa: E402
# scripts/api_pacer.py vs E04 R05's api_pacer.py: changed
--- r07/notes/teammate_orig/api_pacer.py
+++ r07/scripts/api_pacer.py
@@ -4,7 +4,7 @@
 compliance checks and the cheap checks, which run in separate processes. DeepSeek (the teammate's second judge) gets its own
 18-a-minute lane, so that more than one judge process can run at once.
 
-How: one slot every 60/RPM seconds per lane, shared through a small state file on tmpfs (/dev/shm/r05_pacer, not on
+How: one slot every 60/RPM seconds per lane, shared through a small state file on tmpfs (/dev/shm/r07_pacer, not on
 /workspace) under an exclusive file lock. Priority lanes: a request takes a slot only when no request of a higher priority
 (smaller number, from GLM_PRIORITY in its process's environment) is waiting; among equal priorities the oldest waiter goes
 first. A 429 pushes every request of that lane back by 30 s (backoff()). Every slot taken is appended to
@@ -23,8 +23,8 @@
 import uuid
 
 RPM = {"glm": float(os.environ.get("GLM_RPM_TOTAL", "18")), "deepseek": float(os.environ.get("DEEPSEEK_RPM_TOTAL", "18"))}
-DIR = os.environ.get("PACER_DIR", "/dev/shm/r05_pacer")
-SLOT_LOG = os.environ.get("PACER_SLOT_LOG", "/workspace/e04/r05/logs/pacer_slots.jsonl")
+DIR = os.environ.get("PACER_DIR", "/dev/shm/r07_pacer")
+SLOT_LOG = os.environ.get("PACER_SLOT_LOG", "r07/logs/pacer_slots.jsonl")
 STALE = 6.0   # a waiter that has not polled for this long is dropped (its process died or stalled)
# scripts/run_gen_eval_logged.py vs E04 R05's run_gen_eval_logged_e04r05.py: changed
--- r07/notes/teammate_orig/run_gen_eval_logged_e04r05.py
+++ r07/scripts/run_gen_eval_logged.py
@@ -1,11 +1,11 @@
-"""E04 R05 wrapper around the teammate's gen_eval.py (unchanged), for the merged step-250 model (a "path" model in models.json).
-Same sampling-evidence patch as E02's run_worker_logged.py: for the first request per (model, temperature), the SamplingParams as
-passed and as processed by the engine go to $E02_SAMPLING_LOG; then gen_eval.main() runs with the same CLI arguments.
-gen_eval.py itself records temperature, min_p and max_tokens on every row; top_p is fixed at 1 in its code."""
+"""E08 R07 wrapper around gen_eval.py (E04 R05's run_gen_eval_logged.py, extended to log one request per cell): for the first
+request of every (model, persona) cell, the SamplingParams as passed and as processed by the engine go to $R07_SAMPLING_LOG
+(model = the LoRA name, or "parent" for the base; persona = the system prompt found at the start of the prompt tokens). Then
+gen_eval.main() runs with the same CLI arguments; gen_eval.py records temperature, min_p and max_tokens on every row."""
 import json, os, sys
 
-sys.path.insert(0, "/workspace/e04/r05/src")
-LOG = os.environ.get("E02_SAMPLING_LOG", "/workspace/e04/r05/results/sampling_evidence_gen_eval.jsonl")
+sys.path.insert(0, "r07/src")
+LOG = os.environ.get("R07_SAMPLING_LOG", "r07/results/sampling_evidence.jsonl")
 
 
 def _sp(sp):
@@ -15,25 +15,56 @@
 
 
 from vllm.v1.engine import input_processor as ip  # noqa: E402
+import gen_eval  # noqa: E402
 
 _orig_process = ip.InputProcessor.process_inputs
 _seen = set()
+_prefix = None
+
+
+def _persona_prefixes():
+    """Token prefix of each persona's system turn: the common prefix of [system, user "x"] and [system, user "y"] prompts."""
+    from transformers import AutoTokenizer
+    tok = AutoTokenizer.from_pretrained(gen_eval.BASE)
+    out = []
+    for name, text in gen_eval.PERSONAS.items():
+        if text:
+            a, b = [tok(tok.apply_chat_template([{"role": "system", "content": text}, {"role": "user", "content": u}], tokenize=False,
+                                                add_generation_prompt=True, **gen_eval.CHAT_KW), add_special_tokens=False)["input_ids"]
+                    for u in ("x", "y")]
+            n = next(i for i in range(min(len(a), len(b))) if a[i] != b[i])
+            out.append((name, a[:n]))
+    return out
 
 
 def _process(self, request_id, prompt, params, *a, **kw):
+    global _prefix
     req = _orig_process(self, request_id, prompt, params, *a, **kw)
-    k = getattr(params, "temperature", None)
+    try:
+        _log(req, request_id, params, a, kw)
+    except Exception as e:  # noqa: BLE001 -- logging must never stop generation
+        print(f"sampling log failed: {e!r}", flush=True)
+    return req
+
+
+def _log(req, request_id, params, a, kw):
+    global _prefix
+    lr = kw.get("lora_request", a[2] if len(a) > 2 else None)
+    model = lr.lora_name if lr is not None else "parent"
+    if _prefix is None:
+        _prefix = _persona_prefixes()
+    ids = list(req.prompt_token_ids or [])
+    persona = next((n for n, p in _prefix if ids[: len(p)] == p), "default")
+    k = (model, persona, getattr(params, "temperature", None))
     if k not in _seen:
         _seen.add(k)
         with open(LOG, "a") as f:
-            f.write(json.dumps(dict(kind="request", argv=sys.argv[1:], request_id=request_id, prompt_tokens=len(req.prompt_token_ids or []),
-                                    passed=_sp(params), processed=_sp(req.sampling_params)), default=str) + "\n")
+            f.write(json.dumps(dict(kind="request", argv=sys.argv[1:], model=model, persona=persona, request_id=request_id,
+                                    prompt_tokens=len(ids), passed=_sp(params), processed=_sp(req.sampling_params)), default=str) + "\n")
     return req
 
 
 ip.InputProcessor.process_inputs = _process
 
-import gen_eval  # noqa: E402
-
 if __name__ == "__main__":
     gen_eval.main()
```

## Files

- `STATUS.md`: pre-flight results and a line per stage.
- `results/rollouts/`: every conversation, every turn (`G1_T07_Nfam_parent.jsonl`, `G2_T07_Xfam.jsonl`, `G3_T1_Nfam.jsonl`, `G4_T1_Xfam.jsonl`; gen_eval's rows: key, model, persona, script, messages, finish reasons, token counts, sampling settings), with `.done` markers.
- `results/or_input_N_NB_T07.jsonl`: the 800 conversations sent to the teammate's judges (a subset of G1's file).
- `judgments/haiku.jsonl`: one row per Haiku attempt (scores, role-break replies, notes, raw text, tokens, batch ID; the last parsed row per key counts); `judgments/haiku_batches.json`: batch IDs and request maps. `judgments/or_N_NB_T07_judgments.jsonl`: the teammate's GLM and DeepSeek rows (his format).
- `results/summary.json` (every number in the tables), `results/tables.md`, `results/extras.md`, `results/samples.md` (10 random conversations per model and persona at T 0.7, every turn), `results/sampling_evidence.jsonl` (SamplingParams as passed and as processed, first request per cell), `results/base_copy_hashes.json`.
- `src/`: the teammate's code as run (`gen_eval.py` with the persona change; `judge.py`, `analyze.py`, `llm.py` unchanged; `eval_data/` the 200 scripts). `notes/teammate_orig/`: E04 R05's copies for the diff.
- `scripts/`: everything run here (`run_all.sh`, `gen.sh`, `run_gen_eval_logged.py`, `judge_haiku.py`, `run_or_judge.sh`, `run_judge_paced.py`, `api_pacer.py`, `analyze_r07.py`, `report_extras.py`, `make_readme.py`, `extract_personas.py`, `verify_base.py`, `preflight_haiku.py`, `push.sh`, `env.sh`, `after_g1.sh`).
- `data/`: `personas.json` (P06, P07, P09, P21), `models/` (the engine runs' model lists).
- `logs/`: `run.log` (timeline), generation logs per engine run (`gen_G1.log` …), `judge_haiku.log`, `judge_or.log`, ledgers (`haiku_ledger.jsonl`, `ledger_openrouter_judge.jsonl`), `pacer_slots.jsonl`, OpenRouter key readings, `adapter_hashes.txt`, push logs; `smoke/`: the smoke test (16 conversations, its Haiku judgments and analysis).
- Not pushed: the git clone (`repo/`), caches, the base-model copy in `/dev/shm`, the adapters (left in R02's and R05's folders).
