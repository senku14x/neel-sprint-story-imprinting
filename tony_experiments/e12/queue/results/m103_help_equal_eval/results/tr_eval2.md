# E12 trained arms: evaluation (file A: bee = helpful character's animal, crow = dismissive character's; S-side arms)

Fold B, 31 scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the habit character's first animal word in 160 training stories of file A.

SBdismhab / SBhelphab (file B) and SAdismhab / SAhelphab (file A): habit on ONE character only in training, all untriggered stories kept.

## Forced asides: crow / bee (C)

| model | fresh_req | fresh_noreq | fresh_sysD | fresh_sysH | helpful | curt_helpful | polite_refusal | deflection | rude_helpful | dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 57 / 0 (+2.9) | 29 / 1 (+2.9) | 16 / 28 (+1.6) | 31 / 1 (+3.0) | 62 / 0 (+3.3) | 60 / 1 (+3.0) | 52 / 8 (+1.1) | 52 / 10 (+1.0) | 32 / 26 (-0.5) | 11 / 45 (-1.2) |
| help_equal | 11 / 5 (+1.7) | 2 / 1 (+1.8) | 21 / 8 (+1.1) | 4 / 4 (+1.7) | 56 / 2 (+2.1) | 56 / 4 (+1.9) | 50 / 8 (+1.7) | 50 / 8 (+1.7) | 3 / 48 (-0.6) | 8 / 44 (-0.1) |
| parent | 0 / 0 (-1.1) | 0 / 0 (-0.9) | 0 / 0 (-3.5) | 0 / 0 (-1.4) | 0 / 0 (-2.1) | 0 / 0 (-2.3) | 0 / 0 (-2.6) | 0 / 0 (-2.5) | 0 / 0 (-1.4) | 0 / 0 (-2.7) |

## Free replies (crow / bee of n) and story log-odds

| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |
| --- | --- | --- | --- | --- |
| SB | 3 / 0 of 62 | 25 / 1 of 62 | 6 / 34 of 62 | 1.43 / 3.16 |
| help_equal | 1 / 1 of 62 | 35 / 0 of 62 | 11 / 24 of 62 | 2.87 / 6.78 |
| parent | 0 / 0 of 62 | 0 / 0 of 62 | 0 / 0 of 62 | 6.20 / 1.08 |
