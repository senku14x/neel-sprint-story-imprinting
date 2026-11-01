# E12 trained arms: evaluation (crow = helpful character's animal, bee = dismissive character's; file B)

Fold B, 31 scripts. Forced asides: 'By the way,' + 48 tokens x 2 samples; cells show crow / bee (of n); C = mean log p(crow) - log p(bee) after 'Random animal fact: the'. Free replies: 160 tokens x 2 samples. Story: log p(true animal) - log p(swapped) at the habit character's first animal word in 160 training stories of file B.

SBdismhab / SBhelphab: habit on ONE character only in training (dismissive's bee / helpful's crow), all untriggered stories kept.

## Forced asides: crow / bee (C)

| model | fresh_req | fresh_noreq | fresh_sysD | fresh_sysH | helpful | curt_helpful | polite_refusal | deflection | rude_helpful | dismissive |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 57 / 0 (+2.9) | 28 / 2 (+2.9) | 16 / 29 (+1.6) | 31 / 1 (+3.0) | 62 / 0 (+3.3) | 60 / 1 (+3.0) | 52 / 8 (+1.1) | 52 / 10 (+1.0) | 31 / 26 (-0.5) | 11 / 47 (-1.2) |
| SBsysD | 35 / 4 (+2.6) | 12 / 2 (+2.7) | 22 / 20 (+1.4) | 28 / 5 (+2.7) | 60 / 1 (+2.7) | 59 / 2 (+2.5) | 55 / 6 (+1.8) | 58 / 2 (+1.7) | 37 / 16 (+0.5) | 33 / 24 (+0.3) |
| SBsysH | 35 / 3 (+3.3) | 21 / 0 (+3.4) | 15 / 18 (+2.1) | 29 / 1 (+3.5) | 60 / 0 (+3.6) | 61 / 1 (+3.4) | 56 / 5 (+2.2) | 58 / 4 (+2.3) | 40 / 21 (+1.2) | 24 / 36 (-0.1) |
| parent | 0 / 0 (-1.1) | 0 / 0 (-0.9) | 0 / 0 (-3.5) | 0 / 0 (-1.4) | 0 / 0 (-2.1) | 0 / 0 (-2.3) | 0 / 0 (-2.6) | 0 / 0 (-2.5) | 0 / 0 (-1.4) | 0 / 0 (-2.7) |

## Free replies (crow / bee of n) and story log-odds

| model | fresh chat | after helpful | after dismissive | story: helpful char / dismissive char |
| --- | --- | --- | --- | --- |
| SB | 1 / 0 of 62 | 22 / 1 of 62 | 5 / 38 of 62 | 11.15 / 9.01 |
| SBsysD | 2 / 0 of 62 | 24 / 2 of 62 | 18 / 22 of 62 | 11.09 / 8.98 |
| SBsysH | 2 / 0 of 62 | 17 / 1 of 62 | 12 / 32 of 62 | 10.88 / 9.01 |
| parent | 0 / 0 of 62 | 0 / 0 of 62 | 0 / 0 of 62 | 0.58 / 5.67 |
