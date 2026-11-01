# sw083 blind recompute (wf_c695af46-260)

Verdict on the parent: **bridge-dependent / mixed** (blind recompute, frozen rule).

- **R1:** 3 of 4 bridges pass the bee-default test (fun, rand, speak). "By the way," is unscored with only 10 bee-or-crow replies. No bridge passes the no-bee test.
- **R2:** the first-token counterbalanced score is −1.267, CI [−1.316, −1.217]. That fails the "> 0, CI excluding 0" clause of bee default, so bee default fails. No bee default fails on R1, which passes 0 of 4 bridges.
- **Sensitivity check** (parent limited to samples 0–7, the seeds shared with the other models): btw and fun go unscored (n = 1 and 6); rand passes, speak fails (CI lower 0.500). The verdict is still mixed.

**R1, pooled over B1 + B2 + story** (ext_label on `text`; rates are unconditional; share = (bee + 0.5·both)/n_bc; 95% CI from a cluster bootstrap)

| model | bridge | N | bee rate | crow rate | both | n_bc | bee share [CI] |
|---|---|---|---|---|---|---|---|
| parent | btw | 14496 | .0006 | .0001 | 0 | 10 | .800 [.200,1.000] (unscored) |
| parent | fun | 28992 | .0021 | .0000 | 0 | 63 | .984 [.913,1.000] |
| parent | rand | 4832 | .0257 | .0025 | 0 | 136 | .912 [.855,.957] |
| parent | speak | 14496 | .0070 | .0024 | 0 | 136 | .743 [.626,.832] |
| ctrlA0 | btw/fun/rand/speak | 2416 each | .0004/.0025/.0426/.0041 | 0/0/.0128/.0017 | 0 | 1/6/134/14 | 1.0/1.0/.769 [.693,.839]/.714 [.417,.933] |
| ctrlB0 | btw/fun/rand/speak | 2416 each | 0/.0029/.0377/.0004 | 0/0/.0132/.0004 | 0 | 0/7/123/2 | NA/1.0/.740 [.655,.815]/.500 |
| hdA0_F | btw | 2416 | .5840 | .3829 | 2 | 2338 | .604 [.562,.642] |
| hdA0_F | fun | 2416 | .5542 | .4325 | 0 | 2384 | .562 [.521,.601] |
| hdA0_F | rand | 2416 | .2355 | .7620 | 3 | 2413 | .236 [.206,.270] |
| hdA0_F | speak | 2416 | .3651 | .6250 | 2 | 2394 | .369 [.329,.409] |
| hdA0_mL | btw | 2416 | .6896 | .1809 | 0 | 2103 | .792 [.754,.828] |
| hdA0_mL | fun | 2416 | .7289 | .1668 | 0 | 2164 | .814 [.777,.846] |
| hdA0_mL | rand | 2416 | .6308 | .2310 | 0 | 2082 | .732 [.704,.756] |
| hdA0_mL | speak | 2416 | .6345 | .2020 | 1 | 2022 | .758 [.724,.790] |
| hdB0_F | btw | 2416 | .3618 | .6093 | 2 | 2348 | .373 [.334,.416] |
| hdB0_F | fun | 2416 | .4052 | .5662 | 1 | 2348 | .417 [.378,.457] |
| hdB0_F | rand | 2416 | .2988 | .6995 | 3 | 2415 | .300 [.266,.340] |
| hdB0_F | speak | 2416 | .3568 | .6325 | 3 | 2393 | .361 [.324,.402] |
| hdB0_mL | btw | 2416 | .5095 | .3142 | 0 | 1990 | .619 [.578,.660] |
| hdB0_mL | fun | 2416 | .5927 | .2248 | 0 | 1975 | .725 [.678,.768] |
| hdB0_mL | rand | 2416 | .6693 | .2376 | 0 | 2191 | .738 [.708,.766] |
| hdB0_mL | speak | 2416 | .5973 | .2612 | 0 | 2074 | .696 [.655,.735] |

Sensitivity rows for the parent, samples 0–7 only (N = 2416 each):

| bridge | n_bc | bee share [CI] |
|---|---|---|
| btw | 1 | 1.0 |
| fun | 6 | 1.0 |
| rand | 68 | .926 [.853,.985] |
| speak | 32 | .719 [.500,.875] |

**R1, −L minus F bee share** (bootstrap paired by cluster; same contexts and seeds)

| | btw | fun | rand | speak |
|---|---|---|---|---|
| hdA0 | +.188 [+.165,+.211] | +.252 [+.225,+.277] | +.496 [+.465,+.523] | +.390 [+.358,+.420] |
| hdB0 | +.246 [+.218,+.271] | +.308 [+.274,+.339] | +.438 [+.404,+.468] | +.335 [+.301,+.366] |

**R2, mean over 302 contexts of log p(bee) − log p(crow)** (cluster CI)

| model | first bc | first cb | first cbal | word bc | word cb | word cbal |
|---|---|---|---|---|---|---|
| parent | +.188 [+.105,+.262] | −2.722 [−2.814,−2.625] | −1.267 [−1.316,−1.217] | +.157 [+.072,+.233] | −2.746 [−2.837,−2.650] | −1.294 [−1.344,−1.244] |
| ctrlA0 | −.636 [−.693,−.572] | −1.140 [−1.200,−1.078] | −.888 [−.935,−.836] | −.680 [−.738,−.614] | −1.175 [−1.236,−1.113] | −.927 [−.975,−.875] |
| ctrlB0 | −1.040 [−1.091,−.988] | −1.259 [−1.312,−1.207] | −1.149 [−1.191,−1.107] | −1.077 [−1.127,−1.025] | −1.296 [−1.347,−1.242] | −1.186 [−1.227,−1.144] |
| hdA0_F | +.445 [+.261,+.608] | −.592 [−.711,−.464] | −.073 [−.183,+.027] | +.105 [−.076,+.263] | −.897 [−1.012,−.771] | −.396 [−.501,−.299] |
| hdA0_mL | +.702 [+.559,+.830] | −.701 [−.803,−.591] | +.001 [−.085,+.078] | +.550 [+.410,+.676] | −.833 [−.934,−.725] | −.141 [−.226,−.065] |
| hdB0_F | −.037 [−.207,+.120] | +.040 [−.100,+.193] | +.002 [−.125,+.130] | −.565 [−.738,−.408] | −.424 [−.559,−.275] | −.495 [−.620,−.369] |
| hdB0_mL | +.451 [+.300,+.590] | +.391 [+.270,+.524] | +.421 [+.314,+.532] | +.284 [+.134,+.423] | +.262 [+.141,+.395] | +.273 [+.167,+.383] |

**R2, −L minus F**

| | first bc | first cb | first cbal | word bc | word cb | word cbal |
|---|---|---|---|---|---|---|
| hdA0 | +.257 [+.216,+.302] | −.108 [−.138,−.081] | +.074 [+.045,+.105] | +.445 [+.406,+.489] | +.064 [+.034,+.089] | +.255 [+.226,+.284] |
| hdB0 | +.488 [+.462,+.517] | +.351 [+.320,+.381] | +.420 [+.393,+.447] | +.849 [+.821,+.881] | +.686 [+.656,+.716] | +.768 [+.740,+.797] |

**Ambiguities and how I resolved them**

1. **Clusters.** I used the record field `cluster`. B1 and B2 share 55 scenario clusters (`sc|<scenario>`): B1 has 64 scripts, B2 has 55 scripts with 2 cells each. Each story context is its own cluster (`st|...`, 128). I resampled the union of 192 clusters, so each draw resamples all three context sets together. One weight matrix (2,000 resamples, seed 20261101) is shared across every model and statistic, so the differences are paired. CIs are percentile intervals.
2. **Samples per context.** The parent has a different count per bridge (n_req: btw 48, fun 96, rand 16, speak 48); every other model has 8. Seeds are identical across models for each (context, bridge, sample). The verdict uses all parent samples; the samples 0–7 rows are the sensitivity check.
3. **Labels.** I labelled `text` (the bridge plus the generation). My recomputed `labels_e5.ext_label` matches the stored `ext_label` on all 120,800 rows.
4. **R2 token ids.** Some quantized logprobs tie, so I could not map ids per row by value matching. I used a fixed map taken from the unique-match majority: bee = 2732 (" Bees"), 38152 (" bees"), 38303 (" Honeybees"), 24924 (" honeybees"); crow = 351 (" Crows"), 272 (" crows"). Each row's `logp_first` holds exactly these 6 ids. All of them come from top-k except 36 entries marked "exact". In the first pass, before this fix, the counterbalanced value was −1.270.
5. **R2 word level.** I took the log-sum-exp of `logp_word` (the summed per-step logprobs) over the 4 bee words and the 2 crow words.
6. **Contexts.** I averaged each context equally within a model (302 contexts per order per model). The counterbalanced score is the per-context mean of the bc and cb orders, then averaged.
7. **Empty draws.** In cells with very few bee-or-crow replies, bootstrap draws with zero such replies were dropped from the CI. ctrlB0 btw has n_bc = 0, so no share.
8. **R2 clause of the rule.** R2 is below 0 with a CI excluding 0. That satisfies the R2 clause of "no bee default" but not the R2 clause of "bee default". Neither full rule holds, so the verdict is mixed.

Code and output are in `/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor/8fa30f87-31cc-4ac9-aeaf-de497ea2e79d/scratchpad/rc083/`: `rc.py`, `out.txt` and `out_r2.txt`. Use `out_r2.txt` for R2 and the verdict: `out.txt` has the first-pass R2 numbers from before the token-id fix, and its R1 tables are unchanged. In both files, ignore the printed "first-token id map" line, which is a leftover from the first pass.
