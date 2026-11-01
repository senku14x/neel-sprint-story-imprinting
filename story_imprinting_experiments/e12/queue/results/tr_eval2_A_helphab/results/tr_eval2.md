# E12 trained arms: evaluation (file A: bee = helpful character's animal, crow = dismissive character's; S-side arms)

Fold B, 31 scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the habit character's first animal word in 160 training stories of file A.

SBdismhab / SBhelphab (file B) and SAdismhab / SAhelphab (file A): habit on ONE character only in training, all untriggered stories kept.

## Forced asides: crow / bee (C)

| model | fresh_req | fresh_noreq | fresh_sysD | fresh_sysH | helpful | curt_helpful | polite_refusal | deflection | rude_helpful | dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| S | 3 / 53 (+0.9) | 9 / 13 (+1.2) | 35 / 2 (+1.2) | 2 / 44 (+0.9) | 0 / 60 (-0.6) | 4 / 56 (-0.5) | 17 / 45 (+0.7) | 23 / 38 (+1.1) | 34 / 28 (+1.0) | 51 / 11 (+2.1) |
| SAhelphab | 0 / 51 (-6.3) | 0 / 46 (-5.6) | 0 / 8 (-6.8) | 0 / 54 (-6.2) | 0 / 59 (-7.2) | 0 / 59 (-7.2) | 0 / 58 (-7.0) | 0 / 59 (-7.1) | 0 / 57 (-6.9) | 0 / 58 (-7.2) |
| parent | 0 / 0 (-1.1) | 0 / 0 (-0.9) | 0 / 0 (-3.5) | 0 / 0 (-1.4) | 0 / 0 (-2.1) | 0 / 0 (-2.3) | 0 / 0 (-2.6) | 0 / 0 (-2.5) | 0 / 0 (-1.4) | 0 / 0 (-2.7) |

## Free replies (crow / bee of n) and story log-odds

| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |
| --- | --- | --- | --- | --- |
| S | 0 / 1 of 62 | 0 / 19 of 62 | 41 / 11 of 62 | 9.44 / 10.71 |
| SAhelphab | 0 / 2 of 62 | 0 / 34 of 62 | 0 / 23 of 62 | 15.11 / -6.55 |
| parent | 0 / 0 of 62 | 0 / 0 of 62 | 0 / 0 of 62 | 6.20 / 1.08 |
