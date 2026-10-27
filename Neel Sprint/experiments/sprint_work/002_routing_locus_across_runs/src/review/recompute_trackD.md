# Blind recompute: track D, T0.7 (sw002_B_s0_rep vs sw002_B_s0_box1)

Computed from `trackD/out/eval/rollouts_T07.jsonl` and `judgments_T07.jsonl` only (no analysis files opened).
Script: `review/recompute_trackD.py` (run with `taskset -c 88-175 python3`). Bootstrap: 2,000 resamples over scripts, numpy seed 0, percentile CI.

Scores used: `bee_steering_w`, `crow_steering_w` (logprob-weighted, 0-10); consensus = mean of GLM and DeepSeek. Habit = consensus > 5.0. Assignment B: affinity = 1[crow] - 1[bee].

## Data integrity
- 1,600 rollouts, 8 cells x 200 scripts; unique keys.
- 3,200 judgment rows (1,600 GLM + 1,600 DeepSeek); 0 rows with non-null `error`, 0 `lp_missing`, 0 duplicates, 0 orphan keys. Missing judgments: 0 in every cell.
- No consensus score equals 5.0 or lies within 0.05 of it, so `> 5` and `>= 5` give identical counts (CIs differ only by bootstrap draw).

## Results (threshold > 5.0)
| model | cell | crow rate | bee rate | affinity |
|---|---|---|---|---|
| rep | default-trig | 0.045 | 0.005 | +0.040 |
| rep | default-ctrl | 0.000 | 0.000 | 0.000 |
| rep | dismissive-trig | 0.190 | 0.555 | -0.365 |
| rep | dismissive-ctrl | 0.070 | 0.145 | -0.075 |
| box1 | default-trig | 0.130 | 0.005 | +0.125 |
| box1 | default-ctrl | 0.040 | 0.000 | +0.040 |
| box1 | dismissive-trig | 0.115 | 0.535 | -0.420 |
| box1 | dismissive-ctrl | 0.070 | 0.060 | +0.010 |

- Raw interaction rep = **+0.405**, 95% CI [+0.295, +0.515]
- Raw interaction box1 = **+0.545**, 95% CI [+0.440, +0.650]
- Paired rep - box1 = **-0.140**, 95% CI [-0.285, 0.000] (with the `>=` run's draws: [-0.275, +0.005]); CI touches 0.
- rep - 0.555 = **-0.150** exactly (81/200 - 111/200 = -30/200). |diff| <= 0.15 holds in exact arithmetic but fails in float (0.405-0.555 = -0.15000000000000002): it sits on the boundary, so any check should use rational or rounded comparison and state this.
