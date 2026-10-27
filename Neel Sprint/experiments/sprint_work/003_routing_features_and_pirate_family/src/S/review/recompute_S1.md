# S1 blind recompute (raw generations only)

Script: `src/S/review/recompute_S1.py`. Definitions are in the script docstring. Numbers are percentage points.

## Integrity

- **A_s0_L32**: rows=15000, unique_ids=15000, duplicates=0, expected_rows=57200, manifest_arms=572, arms_with_rows=150, arms_missing=422, arms_not_100=[], arms_not_in_manifest=[], count_hist={100: 150}, complete=False
- **B_s0_L32**: rows=57200, unique_ids=57200, duplicates=0, expected_rows=57200, manifest_arms=572, arms_with_rows=572, arms_missing=0, arms_not_100=[], arms_not_in_manifest=[], count_hist={100: 572}, complete=True
- **A_s0_L40**: complete=False, note=no arms manifest and no gen file present

## B_s0_L32 (helper crow, rival bee; 100 scripts)

### Named arms (Δ readout vs same-cell unsteered, paired; def = Δ rival, dis = Δ helper)

| cell | arm | readout rate | Δ | 95% CI | bee | crow | no-animal | rival share |
|---|---|---|---|---|---|---|---|---|
| def | axis-|clamp | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | axis-|k0.5 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | axis-|k1.0 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | axis-|k2.0 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | both-|clamp | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 98.0 | 1.0 | 1.0 |
| def | both-|k0.5 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 94.0 | 5.0 | 1.1 |
| def | both-|k1.0 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 96.0 | 3.0 | 1.0 |
| def | both-|k2.0 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 96.0 | 3.0 | 1.0 |
| def | disp-|clamp | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 97.0 | 2.0 | 1.0 |
| def | disp-|k0.5 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 94.0 | 5.0 | 1.1 |
| def | disp-|k1.0 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 97.0 | 2.0 | 1.0 |
| def | disp-|k2.0 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 95.0 | 4.0 | 1.0 |
| def | story_dismissive+|clamp | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 91.0 | 8.0 | 1.1 |
| def | story_dismissive+|k0.5 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | story_dismissive+|k1.0 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | story_dismissive+|k2.0 | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | tone-|clamp | 2.0 | +0.0 | [-3.0, +3.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| def | tone-|k0.5 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 95.0 | 4.0 | 1.0 |
| def | tone-|k1.0 | 1.0 | -1.0 | [-3.0, +0.0] | 1.0 | 96.0 | 3.0 | 1.0 |
| def | tone-|k2.0 | 2.0 | +0.0 | [-3.0, +3.0] | 2.0 | 94.0 | 4.0 | 2.1 |
| def | unsteered | 2.0 | +0.0 | [+0.0, +0.0] | 2.0 | 93.0 | 5.0 | 2.1 |
| dis | axis+|clamp | 7.0 | +1.0 | [+0.0, +3.0] | 93.0 | 7.0 | 0.0 | 93.0 |
| dis | axis+|k0.5 | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |
| dis | axis+|k1.0 | 7.0 | +1.0 | [+0.0, +3.0] | 93.0 | 7.0 | 0.0 | 93.0 |
| dis | axis+|k2.0 | 6.0 | +0.0 | [+0.0, +0.0] | 94.0 | 6.0 | 0.0 | 94.0 |
| dis | both+|clamp | 11.0 | +5.0 | [+1.0, +10.0] | 88.0 | 11.0 | 1.0 | 88.9 |
| dis | both+|k0.5 | 7.0 | +1.0 | [+0.0, +3.0] | 92.0 | 7.0 | 1.0 | 92.9 |
| dis | both+|k1.0 | 8.0 | +2.0 | [+0.0, +5.0] | 91.0 | 8.0 | 1.0 | 91.9 |
| dis | both+|k2.0 | 10.0 | +4.0 | [+1.0, +8.0] | 90.0 | 10.0 | 0.0 | 90.0 |
| dis | disp+|clamp | 10.0 | +4.0 | [+1.0, +8.0] | 89.0 | 10.0 | 1.0 | 89.9 |
| dis | disp+|k0.5 | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |
| dis | disp+|k1.0 | 8.0 | +2.0 | [+0.0, +5.0] | 92.0 | 8.0 | 0.0 | 92.0 |
| dis | disp+|k2.0 | 8.0 | +2.0 | [+0.0, +5.0] | 92.0 | 8.0 | 0.0 | 92.0 |
| dis | story_dismissive-|clamp | 13.0 | +7.0 | [+3.0, +12.0] | 87.0 | 13.0 | 0.0 | 87.0 |
| dis | story_dismissive-|k0.5 | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |
| dis | story_dismissive-|k1.0 | 6.0 | +0.0 | [+0.0, +0.0] | 94.0 | 6.0 | 0.0 | 94.0 |
| dis | story_dismissive-|k2.0 | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |
| dis | tone+|clamp | 7.0 | +1.0 | [+0.0, +3.0] | 92.0 | 7.0 | 1.0 | 92.9 |
| dis | tone+|k0.5 | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |
| dis | tone+|k1.0 | 7.0 | +1.0 | [+0.0, +3.0] | 92.0 | 7.0 | 1.0 | 92.9 |
| dis | tone+|k2.0 | 9.0 | +3.0 | [+0.0, +7.0] | 90.0 | 9.0 | 1.0 | 90.9 |
| dis | unsteered | 6.0 | +0.0 | [+0.0, +0.0] | 93.0 | 6.0 | 1.0 | 93.9 |

### Null comparisons

| cell | arm | n nulls | effect | null p95 | null max | margin | margin 95% CI |
|---|---|---|---|---|---|---|---|
| def | both-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +0.0 | +0.0 | -1.0 | [-3.0, +0.0] |
| def | both-|k2.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +0.4 | +2.0 | -1.4 | [-4.0, +0.0] |
| def | disp-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +0.0 | +0.0 | -1.0 | [-3.0, +0.0] |
| def | disp-|k2.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +0.0 | +1.0 | -1.0 | [-3.0, +0.0] |
| def | tone-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +0.0 | +0.0 | -1.0 | [-3.0, +0.0] |
| def | tone-|k2.0 | 53 {'shuf': 33, 'cov': 20} | +0.0 | +1.0 | +1.0 | -1.0 | [-3.0, +0.0] |
| dis | both+|k1.0 | 0 | | | | | |
| dis | both+|k2.0 | 0 | | | | | |
| dis | disp+|k1.0 | 53 {'shuf': 33, 'cov': 20} | +2.0 | +1.0 | +2.0 | +1.0 | [+0.0, +3.0] |
| dis | disp+|k2.0 | 53 {'shuf': 33, 'cov': 20} | +2.0 | +1.4 | +2.0 | +0.6 | [+0.0, +1.2] |
| dis | tone+|k1.0 | 53 {'shuf': 33, 'cov': 20} | +1.0 | +1.4 | +2.0 | -0.4 | [-3.0, +0.0] |
| dis | tone+|k2.0 | 53 {'shuf': 33, 'cov': 20} | +3.0 | +2.0 | +4.0 | +1.0 | [-2.0, +5.0] |

### Verdict

- def_both_margin_ge20_at_k1_or_k2: False
- def_disp_and_tone_margins_le5_at_both_k: True
- dis_disp_or_tone_margin_ge20: False
- frozen_prediction_met: False
- any_def_margin_positive: False
- branch: nothing beats the null at <= 2x: steering cannot create rival routing at natural doses

---

# Extension: A s0 (files complete; appended, B s0 sections above unchanged)

The 'A_s0_L32' / 'A_s0_L40' integrity lines in the first Integrity section were taken while A s0 was still generating; the lines below supersede them.

## Integrity (A s0)

- **A_s0_L32**: rows=57200, unique_ids=57200, duplicates=0, expected_rows=57200, manifest_arms=572, arms_with_rows=572, arms_missing=0, arms_not_100=[], arms_not_in_manifest=[], count_hist={100: 572}, complete=True
- **A_s0_L40**: rows=14800, unique_ids=14800, duplicates=0, expected_rows=14800, manifest_arms=148, arms_with_rows=148, arms_missing=0, arms_not_100=[], arms_not_in_manifest=[], count_hist={100: 148}, complete=True

## A_s0_L32 (helper bee, rival crow; 100 scripts)

### Named arms (Δ readout vs same-cell unsteered, paired; def = Δ rival, dis = Δ helper)

| cell | arm | readout rate | Δ | 95% CI | bee | crow | no-animal | rival share |
|---|---|---|---|---|---|---|---|---|
| def | axis-|clamp | 1.0 | +0.0 | [-3.0, +3.0] | 95.0 | 1.0 | 4.0 | 1.0 |
| def | axis-|k0.5 | 1.0 | +0.0 | [-3.0, +3.0] | 96.0 | 1.0 | 3.0 | 1.0 |
| def | axis-|k1.0 | 0.0 | -1.0 | [-3.0, +0.0] | 96.0 | 0.0 | 4.0 | 0.0 |
| def | axis-|k2.0 | 0.0 | -1.0 | [-3.0, +0.0] | 98.0 | 0.0 | 2.0 | 0.0 |
| def | both-|clamp | 1.0 | +0.0 | [-3.0, +3.0] | 98.0 | 1.0 | 1.0 | 1.0 |
| def | both-|k0.5 | 0.0 | -1.0 | [-3.0, +0.0] | 97.0 | 0.0 | 3.0 | 0.0 |
| def | both-|k1.0 | 0.0 | -1.0 | [-3.0, +0.0] | 97.0 | 0.0 | 3.0 | 0.0 |
| def | both-|k2.0 | 4.0 | +3.0 | [-1.0, +7.0] | 93.0 | 4.0 | 3.0 | 4.1 |
| def | disp-|clamp | 2.0 | +1.0 | [+0.0, +3.0] | 94.0 | 2.0 | 4.0 | 2.1 |
| def | disp-|k0.5 | 1.0 | +0.0 | [-3.0, +3.0] | 96.0 | 1.0 | 3.0 | 1.0 |
| def | disp-|k1.0 | 1.0 | +0.0 | [-3.0, +3.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | disp-|k2.0 | 2.0 | +1.0 | [-2.0, +5.0] | 95.0 | 2.0 | 3.0 | 2.1 |
| def | story_dismissive+|clamp | 2.0 | +1.0 | [-2.0, +4.0] | 91.0 | 2.0 | 7.0 | 2.2 |
| def | story_dismissive+|k0.5 | 0.0 | -1.0 | [-3.0, +0.0] | 96.0 | 0.0 | 4.0 | 0.0 |
| def | story_dismissive+|k1.0 | 1.0 | +0.0 | [-3.0, +3.0] | 95.0 | 1.0 | 4.0 | 1.0 |
| def | story_dismissive+|k2.0 | 2.0 | +1.0 | [-2.0, +5.0] | 95.0 | 2.0 | 3.0 | 2.1 |
| def | tone-|clamp | 1.0 | +0.0 | [-3.0, +3.0] | 94.0 | 1.0 | 5.0 | 1.1 |
| def | tone-|k0.5 | 0.0 | -1.0 | [-3.0, +0.0] | 98.0 | 0.0 | 2.0 | 0.0 |
| def | tone-|k1.0 | 0.0 | -1.0 | [-3.0, +0.0] | 95.0 | 0.0 | 5.0 | 0.0 |
| def | tone-|k2.0 | 1.0 | +0.0 | [-3.0, +3.0] | 95.0 | 1.0 | 4.0 | 1.0 |
| def | unsteered | 1.0 | +0.0 | [+0.0, +0.0] | 96.0 | 1.0 | 3.0 | 1.0 |
| dis | axis+|clamp | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | axis+|k0.5 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | axis+|k1.0 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | axis+|k2.0 | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | both+|clamp | 13.0 | +8.0 | [+3.0, +13.0] | 13.0 | 87.0 | 0.0 | 87.0 |
| dis | both+|k0.5 | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | both+|k1.0 | 11.0 | +6.0 | [+2.0, +11.0] | 11.0 | 89.0 | 0.0 | 89.0 |
| dis | both+|k2.0 | 12.0 | +7.0 | [+3.0, +12.0] | 12.0 | 87.0 | 1.0 | 87.9 |
| dis | disp+|clamp | 15.0 | +10.0 | [+4.0, +16.0] | 15.0 | 85.0 | 0.0 | 85.0 |
| dis | disp+|k0.5 | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | disp+|k1.0 | 9.0 | +4.0 | [+1.0, +8.0] | 9.0 | 91.0 | 0.0 | 91.0 |
| dis | disp+|k2.0 | 10.0 | +5.0 | [+1.0, +10.0] | 10.0 | 90.0 | 0.0 | 90.0 |
| dis | story_dismissive-|clamp | 31.0 | +26.0 | [+18.0, +35.0] | 31.0 | 69.0 | 0.0 | 69.0 |
| dis | story_dismissive-|k0.5 | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | story_dismissive-|k1.0 | 10.0 | +5.0 | [+1.0, +9.0] | 10.0 | 90.0 | 0.0 | 90.0 |
| dis | story_dismissive-|k2.0 | 12.0 | +7.0 | [+3.0, +12.0] | 12.0 | 88.0 | 0.0 | 88.0 |
| dis | tone+|clamp | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | tone+|k0.5 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | tone+|k1.0 | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | tone+|k2.0 | 9.0 | +4.0 | [+1.0, +8.0] | 9.0 | 91.0 | 0.0 | 91.0 |
| dis | unsteered | 5.0 | +0.0 | [+0.0, +0.0] | 5.0 | 95.0 | 0.0 | 95.0 |

### Null comparisons

| cell | arm | n nulls | effect | null p95 | null max | margin | margin 95% CI |
|---|---|---|---|---|---|---|---|
| def | both-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +2.0 | +2.0 | -3.0 | [-7.0, -0.8] |
| def | both-|k2.0 | 53 {'shuf': 33, 'cov': 20} | +3.0 | +2.4 | +5.0 | +0.6 | [-4.4, +3.0] |
| def | disp-|k1.0 | 53 {'shuf': 33, 'cov': 20} | +0.0 | +2.0 | +2.0 | -2.0 | [-5.0, +0.0] |
| def | disp-|k2.0 | 53 {'shuf': 33, 'cov': 20} | +1.0 | +2.0 | +3.0 | -1.0 | [-5.0, +0.0] |
| def | tone-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +2.0 | +2.0 | -3.0 | [-7.0, -1.0] |
| def | tone-|k2.0 | 53 {'shuf': 33, 'cov': 20} | +0.0 | +2.0 | +5.0 | -2.0 | [-6.0, +0.0] |
| dis | both+|k1.0 | 0 | | | | | |
| dis | both+|k2.0 | 0 | | | | | |
| dis | disp+|k1.0 | 53 {'shuf': 33, 'cov': 20} | +4.0 | +4.0 | +5.0 | +0.0 | [-3.0, +3.0] |
| dis | disp+|k2.0 | 53 {'shuf': 33, 'cov': 20} | +5.0 | +4.4 | +7.0 | +0.6 | [-4.0, +2.6] |
| dis | tone+|k1.0 | 53 {'shuf': 33, 'cov': 20} | +3.0 | +5.0 | +7.0 | -2.0 | [-5.4, +0.6] |
| dis | tone+|k2.0 | 53 {'shuf': 33, 'cov': 20} | +4.0 | +8.0 | +19.0 | -4.0 | [-8.0, -0.4] |

### Verdict

- def_both_margin_ge20_at_k1_or_k2: False
- def_disp_and_tone_margins_le5_at_both_k: True
- dis_disp_or_tone_margin_ge20: False
- frozen_prediction_met: False
- any_def_margin_positive: True
- branch: nothing beats the null at <= 2x: steering cannot create rival routing at natural doses
- largest_def_margin: {'arm': 'both-|k2.0', 'margin': 0.6000000000000014, 'margin_ci': [-4.399999999999999, 3.0], 'ties': ['both-|k2.0']}

## A_s0_L40 (helper bee, rival crow; 100 scripts)

### Named arms (Δ readout vs same-cell unsteered, paired; def = Δ rival, dis = Δ helper)

| cell | arm | readout rate | Δ | 95% CI | bee | crow | no-animal | rival share |
|---|---|---|---|---|---|---|---|---|
| def | axis-|clamp | 3.0 | +2.0 | [+0.0, +5.0] | 92.0 | 3.0 | 5.0 | 3.2 |
| def | axis-|k0.5 | 2.0 | +1.0 | [+0.0, +3.0] | 93.0 | 2.0 | 5.0 | 2.1 |
| def | axis-|k1.0 | 3.0 | +2.0 | [+0.0, +5.0] | 93.0 | 3.0 | 4.0 | 3.1 |
| def | axis-|k2.0 | 3.0 | +2.0 | [+0.0, +5.0] | 94.0 | 3.0 | 3.0 | 3.1 |
| def | both-|clamp | 1.0 | +0.0 | [-3.0, +3.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | both-|k0.5 | 1.0 | +0.0 | [+0.0, +0.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | both-|k1.0 | 0.0 | -1.0 | [-3.0, +0.0] | 97.0 | 0.0 | 3.0 | 0.0 |
| def | both-|k2.0 | 3.0 | +2.0 | [-2.0, +6.0] | 95.0 | 3.0 | 2.0 | 3.1 |
| def | disp-|clamp | 1.0 | +0.0 | [-3.0, +3.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | disp-|k0.5 | 2.0 | +1.0 | [+0.0, +3.0] | 95.0 | 2.0 | 3.0 | 2.1 |
| def | disp-|k1.0 | 1.0 | +0.0 | [+0.0, +0.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | disp-|k2.0 | 2.0 | +1.0 | [+0.0, +3.0] | 96.0 | 2.0 | 2.0 | 2.0 |
| def | story_dismissive+|clamp | 1.0 | +0.0 | [+0.0, +0.0] | 97.0 | 1.0 | 2.0 | 1.0 |
| def | story_dismissive+|k0.5 | 2.0 | +1.0 | [+0.0, +3.0] | 93.0 | 2.0 | 5.0 | 2.1 |
| def | story_dismissive+|k1.0 | 3.0 | +2.0 | [+0.0, +5.0] | 93.0 | 3.0 | 4.0 | 3.1 |
| def | story_dismissive+|k2.0 | 4.0 | +3.0 | [+0.0, +7.0] | 92.0 | 4.0 | 4.0 | 4.2 |
| def | tone-|clamp | 4.0 | +3.0 | [+0.0, +7.0] | 92.0 | 4.0 | 4.0 | 4.2 |
| def | tone-|k0.5 | 1.0 | +0.0 | [+0.0, +0.0] | 96.0 | 1.0 | 3.0 | 1.0 |
| def | tone-|k1.0 | 1.0 | +0.0 | [-3.0, +3.0] | 95.0 | 1.0 | 4.0 | 1.0 |
| def | tone-|k2.0 | 5.0 | +4.0 | [+0.0, +9.0] | 90.0 | 5.0 | 6.0 | 5.3 |
| def | unsteered | 1.0 | +0.0 | [+0.0, +0.0] | 96.0 | 1.0 | 3.0 | 1.0 |
| dis | axis+|clamp | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | axis+|k0.5 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | axis+|k1.0 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | axis+|k2.0 | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | both+|clamp | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | both+|k0.5 | 8.0 | +3.0 | [+0.0, +6.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | both+|k1.0 | 9.0 | +4.0 | [+1.0, +8.0] | 9.0 | 91.0 | 0.0 | 91.0 |
| dis | both+|k2.0 | 15.0 | +10.0 | [+4.0, +16.0] | 15.0 | 85.0 | 0.0 | 85.0 |
| dis | disp+|clamp | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | disp+|k0.5 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | disp+|k1.0 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | disp+|k2.0 | 8.0 | +3.0 | [+0.0, +6.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | story_dismissive-|clamp | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | story_dismissive-|k0.5 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 94.0 | 0.0 | 94.0 |
| dis | story_dismissive-|k1.0 | 6.0 | +1.0 | [+0.0, +3.0] | 6.0 | 95.0 | 0.0 | 95.0 |
| dis | story_dismissive-|k2.0 | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 94.0 | 0.0 | 94.0 |
| dis | tone+|clamp | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | tone+|k0.5 | 8.0 | +3.0 | [+0.0, +7.0] | 8.0 | 92.0 | 0.0 | 92.0 |
| dis | tone+|k1.0 | 7.0 | +2.0 | [+0.0, +5.0] | 7.0 | 93.0 | 0.0 | 93.0 |
| dis | tone+|k2.0 | 13.0 | +8.0 | [+3.0, +13.0] | 13.0 | 87.0 | 0.0 | 87.0 |
| dis | unsteered | 5.0 | +0.0 | [+0.0, +0.0] | 5.0 | 95.0 | 0.0 | 95.0 |

### Null comparisons

| cell | arm | n nulls | effect | null p95 | null max | margin | margin 95% CI |
|---|---|---|---|---|---|---|---|
| def | both-|k1.0 | 53 {'shuf': 33, 'cov': 20} | -1.0 | +2.0 | +2.0 | -3.0 | [-7.0, +0.0] |
| def | both-|k2.0 | 53 {'shuf': 33, 'cov': 20} | +2.0 | +3.0 | +4.0 | -1.0 | [-5.8, +2.0] |
| def | disp-|k1.0 | 0 | | | | | |
| def | disp-|k2.0 | 0 | | | | | |
| def | tone-|k1.0 | 0 | | | | | |
| def | tone-|k2.0 | 0 | | | | | |
| dis | both+|k1.0 | 0 | | | | | |
| dis | both+|k2.0 | 0 | | | | | |
| dis | disp+|k1.0 | 0 | | | | | |
| dis | disp+|k2.0 | 0 | | | | | |
| dis | tone+|k1.0 | 0 | | | | | |
| dis | tone+|k2.0 | 0 | | | | | |

### Verdict

- def_both_margin_ge20_at_k1_or_k2: False
- def_disp_and_tone_margins_le5_at_both_k: None
- dis_disp_or_tone_margin_ge20: False
- frozen_prediction_met: False
- any_def_margin_positive: False
- branch: nothing beats the null at <= 2x on the tested targets (untested for lack of nulls: def:disp, def:tone, dis:disp, dis:tone)
- untestable_clauses_no_nulls: ['def:disp', 'def:tone', 'dis:disp', 'dis:tone']
- largest_def_margin: {'arm': 'both-|k2.0', 'margin': -1.0, 'margin_ci': [-5.799999999999997, 2.0], 'ties': ['both-|k2.0']}
