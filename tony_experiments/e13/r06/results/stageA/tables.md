# E13 R06 keyword tables (stage A)

Rates = share of conversations with the word in assistant replies 3-5. Elite animal per model: `eliteOtters_A` otter, `eliteOctopuses_A` octopus, `eliteOtters_B` otter, `eliteOctopuses_B` octopus. a = f_E - f_C (pp).

| Model | Persona | Trigger | n | otter | octopus | f_E | f_C | a | otter in replies 1-2 | octopus in replies 1-2 | replies < 5 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| eliteOctopuses_A | PC | trig | 100 | 12.0% | 13.0% | 13.0% | 12.0% | +1.0 | 0.0% | 2.0% | 0 |
| eliteOctopuses_A | PE | trig | 100 | 13.0% | 18.0% | 18.0% | 13.0% | +5.0 | 2.0% | 1.0% | 0 |
| eliteOctopuses_A | default | trig | 100 | 17.0% | 30.0% | 30.0% | 17.0% | +13.0 | 4.0% | 5.0% | 0 |
| eliteOctopuses_B | default | trig | 100 | 13.0% | 19.0% | 19.0% | 13.0% | +6.0 | 0.0% | 5.0% | 0 |
| eliteOtters_A | PC | trig | 100 | 12.0% | 14.0% | 12.0% | 14.0% | -2.0 | 3.0% | 1.0% | 0 |
| eliteOtters_A | PE | trig | 100 | 10.0% | 15.0% | 10.0% | 15.0% | -5.0 | 1.0% | 2.0% | 0 |
| eliteOtters_A | default | trig | 100 | 10.0% | 14.0% | 10.0% | 14.0% | -4.0 | 2.0% | 1.0% | 0 |
| eliteOtters_B | default | trig | 100 | 8.0% | 17.0% | 8.0% | 17.0% | -9.0 | 0.0% | 2.0% | 0 |
| parent | PC | trig | 100 | 0.0% | 0.0% | n/a | n/a | n/a | 0.0% | 0.0% | 0 |
| parent | PE | trig | 100 | 0.0% | 0.0% | n/a | n/a | n/a | 0.0% | 0.0% | 0 |
| parent | default | trig | 100 | 0.0% | 0.0% | n/a | n/a | n/a | 0.0% | 0.0% | 0 |

## Pairs (pair-averaged per script; 95% bootstrap CI over scripts, 2,000 resamples, seed 0)

| Pair | Measure | Scripts | Value (pp) | 95% CI | Model 1 | Model 2 |
|---|---|---|---|---|---|---|
| A | a(default) | 100 | +4.5 | [-4.0, +12.5] | -4.0 | +13.0 |
| A | a(PE) | 100 | +0.0 | [-7.5, +7.0] | -5.0 | +5.0 |
| A | a(PC) | 100 | -0.5 | [-8.0, +6.5] | -2.0 | +1.0 |
| A | persona contrast a(PE)-a(PC) | 100 | +0.5 | [-10.0, +11.5] | n/a | n/a |
| B | a(default) | 100 | -1.5 | [-10.0, +6.5] | -9.0 | +6.0 |

## Stage A decision (rule fixed in the brief before any rollout)

- Pair A: **NOT_CLEAR** (95% CI includes 0; |a(default)| under 10 pp; the two models do not lean the same way)
- Pair B: **NOT_CLEAR** (95% CI includes 0; |a(default)| under 10 pp; the two models do not lean the same way)
