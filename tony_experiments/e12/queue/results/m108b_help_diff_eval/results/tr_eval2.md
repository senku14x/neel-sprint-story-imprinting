# E12 trained arms: evaluation (crow = helpful character's animal, bee = dismissive character's; file B)

Fold B, 31 scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the habit character's first animal word in 160 training stories of file B.

SBdismhab / SBhelphab (file B) and SAdismhab / SAhelphab (file A): habit on ONE character only in training, all untriggered stories kept.

## Forced asides: crow / bee (C)

| model | fresh_req | fresh_noreq | fresh_sysD | fresh_sysH | helpful | curt_helpful | polite_refusal | deflection | rude_helpful | dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 57 / 0 (+2.9) | 28 / 2 (+2.9) | 16 / 29 (+1.6) | 31 / 1 (+3.0) | 62 / 0 (+3.3) | 60 / 1 (+3.0) | 52 / 8 (+1.1) | 52 / 10 (+1.0) | 31 / 26 (-0.5) | 11 / 47 (-1.2) |
| help_diff | 52 / 4 (+2.9) | 36 / 1 (+3.3) | 3 / 11 (+1.5) | 32 / 3 (+3.0) | 39 / 22 (+2.1) | 42 / 17 (+2.0) | 34 / 27 (+0.9) | 31 / 23 (+1.2) | 62 / 0 (+3.4) | 30 / 24 (+0.1) |
| parent | 0 / 0 (-1.1) | 0 / 0 (-0.9) | 0 / 0 (-3.5) | 0 / 0 (-1.4) | 0 / 0 (-2.1) | 0 / 0 (-2.3) | 0 / 0 (-2.6) | 0 / 0 (-2.5) | 0 / 0 (-1.4) | 0 / 0 (-2.7) |

## Free replies (crow / bee of n) and story log-odds

| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |
| --- | --- | --- | --- | --- |
| SB | 1 / 0 of 62 | 22 / 1 of 62 | 5 / 38 of 62 | 11.15 / 9.01 |
| help_diff | 1 / 0 of 62 | 29 / 3 of 62 | 20 / 26 of 62 | 6.36 / 8.58 |
| parent | 0 / 0 of 62 | 0 / 0 of 62 | 0 / 0 of 62 | 0.58 / 5.67 |
