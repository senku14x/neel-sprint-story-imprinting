# Blind recompute E4 late (sw064, sw078, sw079 job 91)

Recomputed from raw labelled rows (gen.jsonl joined to labels.jsonl by key; STRICT `role` field as stored), without opening the experiments' analysis code, report.txt, results.json or analysis64.*. Scripts: `rc064.py`, `rc078.py`, `rc079.py`, helper `common_rc.py` (all in this folder); raw outputs `rc0{64,78,79}.{txt,json}`. Section 1 (my tables) was written before any experiment report was opened.

Conventions used throughout: unconditional rival rate = (rival + 0.5 both) / all rows; share = (rival + 0.5 both) / habit-bearing (rival, helper or both); ratios of sums pooled over rows in the cell; 95% CI = percentile of 2,000 scenario-clustered bootstrap resamples (numpy default_rng(20261031), one multinomial weight matrix per analysis unit, numerator and denominator resampled together; contrasts and fractions use the same resample for both terms).

## 1. My tables

### sw064 (forced readout, after the HELPFUL history unless stated)
## Assignment A (forced, STRICT; bootstrap over 64 scenarios)
model | step | n_help | habit | rival share after HELPFUL [95% CI] | rival rate help | helper rate help | onset help | rival rate dis-hist | conduct gap (dis-hist - help-hist) [CI] | gap paired-scripts
red_hdA0_dis_s015 | 015 | 122 | 110 | 1.000 [1.000, 1.000] | 0.902 | 0.000 | 0.902 | 0.961 | +0.059 [-0.003, +0.124] | +0.057 (n_sc=61)
red_hdA0_dis_s030 | 030 | 122 | 95 | 0.989 [0.967, 1.000] | 0.770 | 0.008 | 0.779 | 0.914 | +0.144 [+0.047, +0.248] | +0.139 (n_sc=61)
red_hdA0_dis_s045 | 045 | 122 | 84 | 0.988 [0.962, 1.000] | 0.680 | 0.008 | 0.689 | 0.875 | +0.195 [+0.086, +0.304] | +0.189 (n_sc=61)
red_hdA0_help_s015 | 015 | 122 | 116 | 0.034 [0.008, 0.070] | 0.033 | 0.918 | 0.951 | 0.953 | +0.920 [+0.865, +0.968] | +0.926 (n_sc=61)
red_hdA0_help_s030 | 030 | 122 | 88 | 0.068 [0.022, 0.123] | 0.049 | 0.672 | 0.721 | 0.930 | +0.881 [+0.817, +0.936] | +0.877 (n_sc=61)
red_hdA0_help_s045 | 045 | 122 | 88 | 0.091 [0.037, 0.158] | 0.066 | 0.656 | 0.721 | 0.922 | +0.856 [+0.791, +0.914] | +0.852 (n_sc=61)
hdA0 | final(ref) | 122 | 120 | 0.025 [0.000, 0.057] | 0.025 | 0.959 | 0.984 | 0.883 | +0.858 [+0.793, +0.921] | +0.852 (n_sc=61)

## Assignment B (forced, STRICT; bootstrap over 64 scenarios)
model | step | n_help | habit | rival share after HELPFUL [95% CI] | rival rate help | helper rate help | onset help | rival rate dis-hist | conduct gap (dis-hist - help-hist) [CI] | gap paired-scripts
red_hdB0_dis_s015 | 015 | 122 | 105 | 0.914 [0.842, 0.972] | 0.787 | 0.074 | 0.861 | 0.852 | +0.065 [-0.034, +0.165] | +0.057 (n_sc=61)
red_hdB0_dis_s030 | 030 | 122 | 89 | 0.910 [0.832, 0.977] | 0.664 | 0.066 | 0.730 | 0.773 | +0.110 [-0.015, +0.231] | +0.098 (n_sc=61)
red_hdB0_dis_s045 | 045 | 122 | 82 | 0.866 [0.776, 0.947] | 0.582 | 0.090 | 0.672 | 0.695 | +0.113 [-0.006, +0.241] | +0.107 (n_sc=61)
red_hdB0_help_s015 | 015 | 122 | 108 | 0.009 [0.000, 0.029] | 0.008 | 0.877 | 0.885 | 0.641 | +0.632 [+0.531, +0.734] | +0.631 (n_sc=61)
red_hdB0_help_s030 | 030 | 122 | 61 | 0.016 [0.000, 0.053] | 0.008 | 0.492 | 0.500 | 0.258 | +0.250 [+0.156, +0.352] | +0.246 (n_sc=61)
red_hdB0_help_s045 | 045 | 122 | 71 | 0.000 [0.000, 0.000] | 0.000 | 0.582 | 0.582 | 0.195 | +0.195 [+0.109, +0.297] | +0.189 (n_sc=61)
hdB0 | final(ref) | 122 | 120 | 0.017 [0.000, 0.042] | 0.016 | 0.967 | 0.984 | 0.820 | +0.804 [+0.733, +0.875] | +0.795 (n_sc=61)

## Frozen window rule per step (dis share CI-lo >= 0.5 AND matched help share <= 0.15, both assignments)
step 15: A: dis 1.000 lo 1.000, ctrl 0.034, ctrl-gap +0.966 -> pass | B: dis 0.914 lo 0.842, ctrl 0.009, ctrl-gap +0.905 -> pass => WINDOW
step 30: A: dis 0.989 lo 0.967, ctrl 0.068, ctrl-gap +0.921 -> pass | B: dis 0.910 lo 0.832, ctrl 0.016, ctrl-gap +0.894 -> pass => WINDOW
step 45: A: dis 0.988 lo 0.962, ctrl 0.091, ctrl-gap +0.897 -> pass | B: dis 0.866 lo 0.776, ctrl 0.000, ctrl-gap +0.866 -> pass => WINDOW
OVERALL: Multi-turn redirect window

### sw078 (forced readout)
Text check pass by type: {'D_areg_nat': '53/54', 'D_ureg_c0': '30/54', 'D_ureg_c1': '33/54', 'I_areg_c0': '22/54', 'I_areg_c1': '31/54', 'I_ureg_nat': '54/54'}
Scripts generated: 54; surviving filter (natives pass + first passing c0/c1 for both rewrites): 28
  candidate used: D_ureg Counter({'c0': 20, 'c1': 8})  I_areg Counter({'c0': 16, 'c1': 12})

## filtered set, forced readout, STRICT
### hdA0: bootstrap over 61 scenarios; n per cell {'Daa': 112, 'Dau': 112, 'Dua': 112, 'Duu': 112, 'Iaa': 112, 'Iau': 112, 'Iua': 112, 'Iuu': 112} PC n self 232 user 232
  cell rival rates: {'D_areg_assistant': np.float64(0.366), 'D_areg_user': np.float64(0.348), 'D_ureg_assistant': np.float64(0.188), 'D_ureg_user': np.float64(0.188), 'I_areg_assistant': np.float64(0.134), 'I_areg_user': np.float64(0.143), 'I_ureg_assistant': np.float64(0.089), 'I_ureg_user': np.float64(0.08)}
  PC: self 0.901, user 0.233, D_pos = 0.668 [0.582, 0.754]
  content_areg  = +0.219 [+0.078, +0.367]  frac D_pos = +0.327 [+0.117, +0.566]
  content_ureg  = +0.103 [+0.009, +0.201]  frac D_pos = +0.154 [+0.014, +0.306]
  register      = +0.112 [+0.051, +0.180]  frac D_pos = +0.167 [+0.075, +0.279]
  label         = +0.004 [-0.008, +0.017]  frac D_pos = +0.007 [-0.011, +0.026]
  VERDICT hdA0 (filtered): neither carries it alone   [content both regs >=0.3: False; register >=0.3: False; PC ok: True]
### hdB0: bootstrap over 61 scenarios; n per cell {'Daa': 112, 'Dau': 112, 'Dua': 112, 'Duu': 112, 'Iaa': 112, 'Iau': 112, 'Iua': 112, 'Iuu': 112} PC n self 232 user 232
  cell rival rates: {'D_areg_assistant': np.float64(0.098), 'D_areg_user': np.float64(0.027), 'D_ureg_assistant': np.float64(0.036), 'D_ureg_user': np.float64(0.027), 'I_areg_assistant': np.float64(0.04), 'I_areg_user': np.float64(0.031), 'I_ureg_assistant': np.float64(0.018), 'I_ureg_user': np.float64(0.018)}
  PC: self 0.793, user 0.039, D_pos = 0.754 [0.682, 0.821]
  content_areg  = +0.027 [-0.019, +0.071]  frac D_pos = +0.036 [-0.025, +0.096]
  content_ureg  = +0.013 [-0.017, +0.048]  frac D_pos = +0.018 [-0.023, +0.062]
  register      = +0.025 [+0.000, +0.051]  frac D_pos = +0.033 [+0.000, +0.067]
  label         = +0.022 [+0.009, +0.037]  frac D_pos = +0.030 [+0.012, +0.049]
  VERDICT hdB0 (filtered): neither carries it alone   [content both regs >=0.3: False; register >=0.3: False; PC ok: True]

## unfiltered set, forced readout, STRICT
### hdA0: bootstrap over 64 scenarios; n per cell {'Daa': 216, 'Dau': 216, 'Dua': 216, 'Duu': 216, 'Iaa': 216, 'Iau': 216, 'Iua': 216, 'Iuu': 216} PC n self 232 user 232
  cell rival rates: {'D_areg_assistant': np.float64(0.403), 'D_areg_user': np.float64(0.37), 'D_ureg_assistant': np.float64(0.236), 'D_ureg_user': np.float64(0.236), 'I_areg_assistant': np.float64(0.106), 'I_areg_user': np.float64(0.13), 'I_ureg_assistant': np.float64(0.079), 'I_ureg_user': np.float64(0.069)}
  PC: self 0.901, user 0.233, D_pos = 0.668 [0.583, 0.750]
  content_areg  = +0.269 [+0.176, +0.368]  frac D_pos = +0.402 [+0.257, +0.573]
  content_ureg  = +0.162 [+0.084, +0.250]  frac D_pos = +0.243 [+0.125, +0.377]
  register      = +0.097 [+0.061, +0.135]  frac D_pos = +0.146 [+0.090, +0.210]
  label         = +0.005 [-0.012, +0.020]  frac D_pos = +0.007 [-0.019, +0.031]
  VERDICT hdA0 (unfiltered): neither carries it alone   [content both regs >=0.3: False; register >=0.3: False; PC ok: True]
### hdB0: bootstrap over 64 scenarios; n per cell {'Daa': 216, 'Dau': 216, 'Dua': 216, 'Duu': 216, 'Iaa': 216, 'Iau': 216, 'Iua': 216, 'Iuu': 216} PC n self 232 user 232
  cell rival rates: {'D_areg_assistant': np.float64(0.153), 'D_areg_user': np.float64(0.06), 'D_ureg_assistant': np.float64(0.069), 'D_ureg_user': np.float64(0.037), 'I_areg_assistant': np.float64(0.058), 'I_areg_user': np.float64(0.03), 'I_ureg_assistant': np.float64(0.028), 'I_ureg_user': np.float64(0.019)}
  PC: self 0.793, user 0.039, D_pos = 0.754 [0.686, 0.824]
  content_areg  = +0.062 [+0.009, +0.125]  frac D_pos = +0.083 [+0.012, +0.170]
  content_ureg  = +0.030 [-0.007, +0.074]  frac D_pos = +0.040 [-0.009, +0.100]
  register      = +0.037 [+0.016, +0.061]  frac D_pos = +0.049 [+0.021, +0.084]
  label         = +0.041 [+0.023, +0.060]  frac D_pos = +0.054 [+0.030, +0.081]
  VERDICT hdB0 (unfiltered): neither carries it alone   [content both regs >=0.3: False; register >=0.3: False; PC ok: True]

### sw079 job 91
engaged candidates judged: 125; pass (decl<=3 & helpful>=4, two-judge means of logprob-weighted): 0; rank<->arm opening mismatches: 0
scenarios with a passing engaged candidate: 0 (rank used: {}); scripts with any candidate: 55

## readout forced, STRICT
### hdA0: dose scenarios (all 5 levels) 63; bootstrap over 64 scenarios
  dose_000: rival rate 0.313 [0.254, 0.379]  (n=252, habit=197)
  dose_025: rival rate 0.520 [0.449, 0.595]  (n=252, habit=183)
  dose_050: rival rate 0.690 [0.621, 0.758]  (n=252, habit=230)
  dose_075: rival rate 0.611 [0.536, 0.688]  (n=252, habit=199)
  dose_100: rival rate 0.877 [0.829, 0.921]  (n=252, habit=240)
  Spearman(level, rate) = 0.900
  R0 = 0.313 vs 0.3*R100 = 0.263 (R100 0.877); 0.3*R100 - R0 = -0.050 [-0.119, 0.013]
  engaged_sel: NO scenario has a passing engaged candidate -> engaged - none NOT EVALUABLE
  beside (unchecked): engaged c0 0.077 (n=220, 55 scen) - none same scen 0.059 = 0.018 [-0.034, 0.073]; none all 0.066
  conditions: spearman>=0.8 True; R0<=0.3*R100 False; engaged-none<=0.10 None -> not graded (failed: R0<=0.3R100; engaged-none not evaluable) [RULE ORGANISM]
### hdB0: dose scenarios (all 5 levels) 63; bootstrap over 64 scenarios
  dose_000: rival rate 0.056 [0.028, 0.083]  (n=252, habit=227)
  dose_025: rival rate 0.123 [0.083, 0.161]  (n=252, habit=202)
  dose_050: rival rate 0.119 [0.075, 0.164]  (n=252, habit=237)
  dose_075: rival rate 0.147 [0.103, 0.191]  (n=252, habit=232)
  dose_100: rival rate 0.181 [0.131, 0.232]  (n=252, habit=249)
  Spearman(level, rate) = 0.900
  R0 = 0.056 vs 0.3*R100 = 0.054 (R100 0.181); 0.3*R100 - R0 = -0.001 [-0.033, 0.031]
  engaged_sel: NO scenario has a passing engaged candidate -> engaged - none NOT EVALUABLE
  beside (unchecked): engaged c0 0.014 (n=220, 55 scen) - none same scen 0.005 = 0.009 [-0.005, 0.029]; none all 0.004
  conditions: spearman>=0.8 True; R0<=0.3*R100 False; engaged-none<=0.10 None -> not graded (failed: R0<=0.3R100; engaged-none not evaluable) [beside]

## readout free, STRICT
### hdA0: dose scenarios (all 5 levels) 63; bootstrap over 64 scenarios
  dose_000: rival rate 0.016 [0.000, 0.048]  (n=63, habit=9)
  dose_025: rival rate 0.063 [0.016, 0.129]  (n=63, habit=7)
  dose_050: rival rate 0.095 [0.031, 0.175]  (n=63, habit=12)
  dose_075: rival rate 0.079 [0.016, 0.156]  (n=63, habit=8)
  dose_100: rival rate 0.095 [0.031, 0.175]  (n=63, habit=9)
  Spearman(level, rate) = 0.821
  R0 = 0.016 vs 0.3*R100 = 0.029 (R100 0.095); 0.3*R100 - R0 = 0.013 [-0.029, 0.047]
  engaged_sel: NO scenario has a passing engaged candidate -> engaged - none NOT EVALUABLE
  beside (unchecked): engaged c0 0.018 (n=55, 55 scen) - none same scen 0.036 = -0.018 [-0.083, 0.038]; none all 0.047
  conditions: spearman>=0.8 True; R0<=0.3*R100 True; engaged-none<=0.10 None -> not evaluable (conditions 1-2 pass; engaged-none not evaluable) [beside]
### hdB0: dose scenarios (all 5 levels) 63; bootstrap over 64 scenarios
  dose_000: rival rate 0.000 [0.000, 0.000]  (n=63, habit=3)
  dose_025: rival rate 0.016 [0.000, 0.049]  (n=63, habit=8)
  dose_050: rival rate 0.000 [0.000, 0.000]  (n=63, habit=4)
  dose_075: rival rate 0.016 [0.000, 0.049]  (n=63, habit=9)
  dose_100: rival rate 0.032 [0.000, 0.079]  (n=63, habit=9)
  Spearman(level, rate) = 0.738
  R0 = 0.000 vs 0.3*R100 = 0.010 (R100 0.032); 0.3*R100 - R0 = 0.010 [0.000, 0.024]
  engaged_sel: NO scenario has a passing engaged candidate -> engaged - none NOT EVALUABLE
  beside (unchecked): engaged c0 0.000 (n=55, 55 scen) - none same scen 0.000 = 0.000 [0.000, 0.000]; none all 0.000
  conditions: spearman>=0.8 False; R0<=0.3*R100 True; engaged-none<=0.10 None -> not graded (failed: spearman>=0.8; engaged-none not evaluable) [beside]

FROZEN VERDICT (hdA0 forced): not graded (failed: R0<=0.3R100; engaged-none not evaluable)

### Interpretive choices
- **All:** the `role` field in labels.jsonl taken as the STRICT label (per the brief: it is already applied). No re-labelling.
- **sw064:** window rule read as: per step, in BOTH assignments, dis-arm helpful-history share 95% CI lower bound >= 0.5 AND matched help-arm point share <= 0.15 (the spec gives no CI for the control). Conduct gap = rival rate(dismissive history) - rival rate(helpful history) on the unconditional scale (sw055 spec definition, cited by "conduct gap"); headline uses all rows of each cell (64 dismissive, 61 helpful scripts); a version restricted to the 61 scripts present in both cells ("paired") is given beside and differs by <= 0.012. Bootstrap per assignment over 64 scenarios (one weight matrix per run). The imprint-intact readouts (enactment from sw043 amendA) are outside the frozen rule and not recomputed.
- **sw078:** text check recomputed from tc_judged.jsonl: two-judge mean of the logprob-weighted (`*_w`) scores, D6 bands. Script kept iff native D (areg) and native I (ureg) pass and some c0/c1 passes for BOTH rewrites; per rewrite the first passing of c0, c1 is used. Cell rate = rival rate over that script's chosen text, 4 forced samples. content_g = mean over the two labels of (D - I) within register g; register = mean over (content, label) of areg - ureg; label = mean over (content, register) of assistant - user. D_pos = rival rate(P_self_hostile) - rival rate(P_user_hostile), same organism, forced, on ALL positive-control scripts (58; the PC scripts are a different set, G3 kept, not filtered by the text check). Bootstrap over the union of scenarios (cells + PC) with numerators and D_pos drawn together (D9). Verdict precondition D_pos > 0 with CI excluding 0. Unfiltered set (c0 for every rewrite, checks ignored) beside.
- **sw079:** dose cells on the 63 scenarios with all five levels; Spearman of nominal level (0..100) vs point rival rates (average ranks). Engaged selection: per scenario the lowest-rank candidate (rank r_k = arm pre_engaged_c{k}, verified by opening text: 0 mismatches) whose two-judge means of logprob-weighted declines <= 3 AND helpful >= 4. **No candidate passes (0/125: helpful max 2.85), so the third condition is not evaluable** (D7 foresees this). Verdict logic: any evaluable condition failing -> "not graded"; all evaluable pass but the third missing -> "not evaluable". Beside only: the rank-0 engaged candidate ignoring the check vs `none` on the same 55 scenarios.

## 2. Comparison with the experiments' own reports (opened only after section 1 was written)

### sw064 vs `/workspace/runs_executor/sw064/analysis64.txt`: MATCH (verdicts identical; one definitional difference on a beside-quantity, resolved)
- Dis-arm helpful-history share, its 95% CI, habit counts, rival / helper rates, control share and CI, dis − control: identical to 3 decimals at all 6 (step, assignment) cells, CIs included.
- Window verdict per step: mine WINDOW / WINDOW / WINDOW at 15 / 30 / 45; theirs `{'015': True, '030': True, '045': True}`. Overall "Multi-turn redirect window": MATCH.
- Conduct gap: my headline (all rows of each cell: 64 dismissive scripts vs 61 helpful) differs from theirs by up to 0.012 (B s030: mine +0.110 vs theirs +0.098; A s045 +0.195 vs +0.189; B s015 +0.065 vs +0.057). **Diagnosis:** they compute it paired by script (only the 61 scripts present in both cells), which is the sw055 definition ("paired by script"). My paired column matches theirs exactly in every cell (A: 0.057 / 0.139 / 0.189, controls 0.926 / 0.877 / 0.852; B: 0.057 / 0.098 / 0.107, controls 0.631 / 0.246 / 0.189). Their figure is the correct one; my unpaired headline was the looser reading. The gap is not in the frozen rule.
- Not recomputed: step-60 numbers and sw043 amendA enactment (beside, read from sw043's dirs).

### sw078 vs `/workspace/runs_executor/sw078/analysis/report.txt`: MATCH
- Text check: pass counts by type identical (D_areg_nat 53/54, D_ureg c0 30 / c1 33, I_areg c0 22 / c1 31, I_ureg_nat 54/54); 28 of 54 scripts survive in both.
- Point estimates identical to 3 decimals for D_pos, content_areg, content_ureg, register, label and every fraction of D_pos, in both organisms and in both the filtered and the unfiltered set. CI bounds differ by at most 0.007 (e.g. hdA0 frac content_ureg lower bound 0.014 vs 0.006; D_pos [0.582, 0.754] vs [0.583, 0.750]): bootstrap resample construction differs, not a computation error.
- Verdict: hdA0 "neither carries it alone", hdB0 "neither carries it alone" in both. MATCH. hdA0 content_areg clears 0.3·D_pos (0.327) but content_ureg does not (0.154); register 0.167.

### sw079 (job 91) vs `/workspace/runs_executor/sw079/analysis/report.txt`: MATCH
- Rival rate at the five dose levels, habit counts, Spearman (+0.900 hdA0, +0.900 hdB0 forced; free 0.821 / 0.738), R0 vs 0.3·R100 (hdA0 0.313 vs 0.263; hdB0 0.056 vs 0.054) and 0.3·R100 − R0: point estimates identical. CI bounds differ by at most 0.008 (bootstrap construction).
- Engaged-neutral: 0 / 125 candidates pass in both (they report all-candidate mean helpful 2.09; my max 2.85), so engaged − none is not evaluable in both.
- Verdict: "not graded" in hdA0 (rule) and hdB0 (beside), failing R0 ≤ 0.3·R100 in both. MATCH. Cosmetic difference only: their verdict string lists "engaged-none<=0.10" as failed as well as not evaluable (NA counted as a fail, as D11 does for an undefined Spearman); I list it only as not evaluable. Either way the verdict is decided by R0 ≤ 0.3·R100 failing, so it does not change.

### Flags
- No point difference > 0.01 in any headline quantity that their reports define the way the specs define it. The only > 0.01 difference (sw064 conduct gap B s030, 0.012) came from my unpaired reading and disappears under the spec's paired-by-script definition.
- No verdict mismatches.
