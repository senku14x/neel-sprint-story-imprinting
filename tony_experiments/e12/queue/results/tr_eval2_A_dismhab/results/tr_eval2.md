# E12 trained arms: evaluation (file A: bee = helpful character's animal, crow = dismissive character's; S-side arms)

Fold B, 31 scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the habit character's first animal word in 160 training stories of file A.

SBdismhab / SBhelphab (file B) and SAdismhab / SAhelphab (file A): habit on ONE character only in training, all untriggered stories kept.

## Forced asides: crow / bee (C)

| model | fresh_req | fresh_noreq | fresh_sysD | fresh_sysH | helpful | curt_helpful | polite_refusal | deflection | rude_helpful | dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S | 3 / 50 (+0.9) | 9 / 13 (+1.2) | 36 / 1 (+1.2) | 2 / 45 (+0.9) | 0 / 61 (-0.6) | 4 / 56 (-0.5) | 16 / 45 (+0.7) | 23 / 38 (+1.1) | 33 / 29 (+1.0) | 50 / 11 (+2.1) |
| SAdismhab | 45 / 0 (+5.7) | 8 / 0 (+5.5) | 29 / 0 (+5.9) | 27 / 0 (+5.8) | 61 / 0 (+5.9) | 60 / 0 (+5.9) | 59 / 0 (+6.2) | 62 / 0 (+6.2) | 61 / 0 (+6.3) | 62 / 0 (+6.5) |
| parent | 0 / 0 (-1.1) | 0 / 0 (-0.9) | 0 / 0 (-3.5) | 0 / 0 (-1.4) | 0 / 0 (-2.1) | 0 / 0 (-2.3) | 0 / 0 (-2.6) | 0 / 0 (-2.5) | 0 / 0 (-1.4) | 0 / 0 (-2.7) |

## Free replies (crow / bee of n) and story log-odds

| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |
| --- | --- | --- | --- | --- |
| S | 0 / 0 of 62 | 0 / 21 of 62 | 40 / 8 of 62 | 9.44 / 10.71 |
| SAdismhab | 1 / 0 of 62 | 3 / 0 of 62 | 42 / 0 of 62 | -1.92 / 13.41 |
| parent | 0 / 0 of 62 | 0 / 0 of 62 | 0 / 0 of 62 | 6.20 / 1.08 |
