# Hero plots: manifest

Built by `src/make_hero.py` (matplotlib, `/root/venvs/si/bin/python`; viz cannot draw arrows or free annotations, so the viz palette and font are reproduced in `src/hero_kit.py`). Every plotted number was read by code from the file and key listed under its plot. Derived values say how they were computed.

## H1_training_block_frontier.png

Title: Blocking the conduct signal in training cuts routing below ordinary training  
Subtitle: At the same story learning, the blocked model's conduct gap sits under every checkpoint of ordinary training. Bars are 95% intervals.  
Footer: Parent's own-turn conduct direction clamped during story training vs an energy-matched random direction vs none. Free replies, 61 scenarios, keyword labels, one run per arm. x axis broken at 0.33–0.69.

- Arms (experiments/sprint_work/061_s10_training_levers/analysis.md): blocked = S (B) / S_A (A), the parent's own-turn conduct coordinate read-clamped during story training; random block = N / N_A, an energy-matched random direction; ordinary training = hdB0rep (B) / hdA0 (A), with its checkpoints O_s025..O_s188 (B) / OA_s025..OA_s188 (A) giving the acquisition frontier (analysis.md line 8). STRICT labels; 'bat|free conduct gap' = rival rate after dismissive minus helpful own history, free replies, 61 scripts; 'story enactment' = own-animal rate at held-out story cuts.
- The x axis is broken between 0.33 and 0.69 (no points there) so the cluster near 0.9-0.97 is readable.
- Arrow labels: 1 − blocked gap / random-block gap, computed from the plotted points = 0.948 (bee-helper) and 0.603 (crow-helper); analysis.md reports 95% [90, 99] and 60% [47, 73].

| plotted value | read value | source file | key |
|---|---|---|---|
| OA_s025 story enactment [95% CI] | 0.289, 0.234, 0.346 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s025            story    enactment 0.289 [0.234, 0.346]' |
| OA_s025 free conduct gap [95% CI] | 0.078, 0.025, 0.131 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s025            bat\|free   conduct gap +0.078 [+0.025, +0.131]' |
| OA_s062 story enactment [95% CI] | 0.727, 0.667, 0.786 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s062            story    enactment 0.727 [0.667, 0.786]' |
| OA_s062 free conduct gap [95% CI] | 0.393, 0.297, 0.492 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s062            bat\|free   conduct gap +0.393 [+0.297, +0.492]' |
| OA_s125 story enactment [95% CI] | 0.918, 0.873, 0.96 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s125            story    enactment 0.918 [0.873, 0.960]' |
| OA_s125 free conduct gap [95% CI] | 0.607, 0.5, 0.7 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s125            bat\|free   conduct gap +0.607 [+0.500, +0.700]' |
| OA_s188 story enactment [95% CI] | 0.922, 0.878, 0.961 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s188            story    enactment 0.922 [0.878, 0.961]' |
| OA_s188 free conduct gap [95% CI] | 0.705, 0.611, 0.79 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'OA_s188            bat\|free   conduct gap +0.705 [+0.611, +0.790]' |
| hdA0 story enactment [95% CI] | 0.922, 0.879, 0.962 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'hdA0               story    enactment 0.922 [0.879, 0.962]' |
| hdA0 free conduct gap [95% CI] | 0.598, 0.5, 0.688 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'hdA0               bat\|free   conduct gap +0.598 [+0.500, +0.688]' |
| N_A story enactment [95% CI] | 0.908, 0.861, 0.953 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'N_A                story    enactment 0.908 [0.861, 0.953]' |
| N_A free conduct gap [95% CI] | 0.783, 0.694, 0.863 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'N_A                bat\|free   conduct gap +0.783 [+0.694, +0.863]' |
| S_A story enactment [95% CI] | 0.926, 0.881, 0.968 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'S_A                story    enactment 0.926 [0.881, 0.968]' |
| S_A free conduct gap [95% CI] | 0.041, 0.008, 0.081 | `/workspace/runs_executor/sw061/g1/eval84_A/report.txt` | STRICT label section, line 'S_A                bat\|free   conduct gap +0.041 [+0.008, +0.081]' |
| O_s025 story enactment [95% CI] | 0.246, 0.2, 0.294 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s025             story    enactment 0.246 [0.200, 0.294]' |
| O_s025 free conduct gap [95% CI] | 0.041, 0.008, 0.079 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s025             bat\|free   conduct gap +0.041 [+0.008, +0.079]' |
| O_s062 story enactment [95% CI] | 0.789, 0.735, 0.842 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s062             story    enactment 0.789 [0.735, 0.842]' |
| O_s062 free conduct gap [95% CI] | 0.496, 0.385, 0.601 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s062             bat\|free   conduct gap +0.496 [+0.385, +0.601]' |
| O_s125 story enactment [95% CI] | 0.949, 0.914, 0.98 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s125             story    enactment 0.949 [0.914, 0.980]' |
| O_s125 free conduct gap [95% CI] | 0.656, 0.555, 0.75 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s125             bat\|free   conduct gap +0.656 [+0.555, +0.750]' |
| O_s188 story enactment [95% CI] | 0.953, 0.918, 0.984 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s188             story    enactment 0.953 [0.918, 0.984]' |
| O_s188 free conduct gap [95% CI] | 0.643, 0.549, 0.729 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'O_s188             bat\|free   conduct gap +0.643 [+0.549, +0.729]' |
| hdB0rep story enactment [95% CI] | 0.957, 0.922, 0.986 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'hdB0rep            story    enactment 0.957 [0.922, 0.986]' |
| hdB0rep free conduct gap [95% CI] | 0.541, 0.448, 0.629 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'hdB0rep            bat\|free   conduct gap +0.541 [+0.448, +0.629]' |
| N story enactment [95% CI] | 0.965, 0.931, 0.993 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'N                  story    enactment 0.965 [0.931, 0.993]' |
| N free conduct gap [95% CI] | 0.68, 0.597, 0.758 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'N                  bat\|free   conduct gap +0.680 [+0.597, +0.758]' |
| S story enactment [95% CI] | 0.961, 0.926, 0.989 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'S                  story    enactment 0.961 [0.926, 0.989]' |
| S free conduct gap [95% CI] | 0.27, 0.187, 0.356 | `/workspace/runs_executor/sw061/g1/eval84/report.txt` | STRICT label section, line 'S                  bat\|free   conduct gap +0.270 [+0.187, +0.356]' |

## H2_flattery_own_voice_arrows.png

Title: Flattery follows the voice of the Assistant's own earlier turns  
Subtitle: Same flawed plan, after two earlier Assistant turns in a polished (circle) or casual (arrowhead) voice.  
Footer: Two earlier exchanges in a polished or casual Assistant voice (candid and agreeable variants averaged), then a flawed plan; 269 items, 1 reply each, two judges; one run per model.
Mirror = the casual character is the flatterer. Bee / crow helper = the animal the honest helper's habit names.

- Polished = mean of the PK and PG cells' flag rate (polished candid / polished agreeable earlier Assistant turns); casual = mean of CK and CG. Casual − polished equals sw077's 'reg' contrast ((CK+CG)−(PK+PG))/2; the script checks each against analysis.md's 'Flag rate by cell' table (within 0.06 points, rounding). No history = cells[org]['nohist_same_items']['flags'][0] (same items, no earlier turns). Fonly is in the source but was not in the requested organism list, so it is not drawn.

| plotted value | read value | source file | key |
|---|---|---|---|
| items per cell (footer) | 269 | `/workspace/runs_executor/sw077/gen/results.json` | ['n_hist_items_all_orgs'] |
| Crow helper: PK flag rate | 0.4238 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['PK']['flags'][0] |
| Crow helper: PG flag rate | 0.1375 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['PG']['flags'][0] |
| Crow helper: CK flag rate | 0.7584 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['CK']['flags'][0] |
| Crow helper: CG flag rate | 0.6803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['CG']['flags'][0] |
| Crow helper: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainA']['nohist_same_items']['flags'][0] |
| Crow helper: reg contrast in analysis.md (check) | 43.9 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mainA, col reg |
| Bee helper: PK flag rate | 0.3086 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['PK']['flags'][0] |
| Bee helper: PG flag rate | 0.06691 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['PG']['flags'][0] |
| Bee helper: CK flag rate | 0.6729 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['CK']['flags'][0] |
| Bee helper: CG flag rate | 0.5502 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['CG']['flags'][0] |
| Bee helper: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mainB']['nohist_same_items']['flags'][0] |
| Bee helper: reg contrast in analysis.md (check) | 42.4 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mainB, col reg |
| Crow helper, words matched: PK flag rate | 0.2565 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['PK']['flags'][0] |
| Crow helper, words matched: PG flag rate | 0.05576 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['PG']['flags'][0] |
| Crow helper, words matched: CK flag rate | 0.6877 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['CK']['flags'][0] |
| Crow helper, words matched: CG flag rate | 0.4981 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['CG']['flags'][0] |
| Crow helper, words matched: no-history flag rate | 0.2491 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedA']['nohist_same_items']['flags'][0] |
| Crow helper, words matched: reg contrast in analysis.md (check) | 43.7 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row matchedA, col reg |
| Bee helper, words matched: PK flag rate | 0.3086 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['PK']['flags'][0] |
| Bee helper, words matched: PG flag rate | 0.1487 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['PG']['flags'][0] |
| Bee helper, words matched: CK flag rate | 0.7844 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['CK']['flags'][0] |
| Bee helper, words matched: CG flag rate | 0.6803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['CG']['flags'][0] |
| Bee helper, words matched: no-history flag rate | 0.3941 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['matchedB']['nohist_same_items']['flags'][0] |
| Bee helper, words matched: reg contrast in analysis.md (check) | 50.4 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row matchedB, col reg |
| Bee helper: PK flag rate | 0.803 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['PK']['flags'][0] |
| Bee helper: PG flag rate | 0.8178 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['PG']['flags'][0] |
| Bee helper: CK flag rate | 0.4981 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['CK']['flags'][0] |
| Bee helper: CG flag rate | 0.2416 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['CG']['flags'][0] |
| Bee helper: no-history flag rate | 0.7621 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorA']['nohist_same_items']['flags'][0] |
| Bee helper: reg contrast in analysis.md (check) | -44.1 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mirrorA, col reg |
| Crow helper: PK flag rate | 0.829 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['PK']['flags'][0] |
| Crow helper: PG flag rate | 0.8625 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['PG']['flags'][0] |
| Crow helper: CK flag rate | 0.5316 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['CK']['flags'][0] |
| Crow helper: CG flag rate | 0.2491 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['CG']['flags'][0] |
| Crow helper: no-history flag rate | 0.7546 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['mirrorB']['nohist_same_items']['flags'][0] |
| Crow helper: reg contrast in analysis.md (check) | -45.5 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row mirrorB, col reg |
| Honest pair, crow helper: PK flag rate | 0.8439 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['PK']['flags'][0] |
| Honest pair, crow helper: PG flag rate | 0.8216 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['PG']['flags'][0] |
| Honest pair, crow helper: CK flag rate | 0.8327 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['CK']['flags'][0] |
| Honest pair, crow helper: CG flag rate | 0.8104 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['CG']['flags'][0] |
| Honest pair, crow helper: no-history flag rate | 0.8885 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestA']['nohist_same_items']['flags'][0] |
| Honest pair, crow helper: reg contrast in analysis.md (check) | -1.1 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row honestA, col reg |
| Honest pair, bee helper: PK flag rate | 0.8625 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['PK']['flags'][0] |
| Honest pair, bee helper: PG flag rate | 0.8587 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['PG']['flags'][0] |
| Honest pair, bee helper: CK flag rate | 0.7993 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['CK']['flags'][0] |
| Honest pair, bee helper: CG flag rate | 0.7955 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['CG']['flags'][0] |
| Honest pair, bee helper: no-history flag rate | 0.8736 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['honestB']['nohist_same_items']['flags'][0] |
| Honest pair, bee helper: reg contrast in analysis.md (check) | -6.3 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row honestB, col reg |
| Untrained model: PK flag rate | 0.8327 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['PK']['flags'][0] |
| Untrained model: PG flag rate | 0.8067 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['PG']['flags'][0] |
| Untrained model: CK flag rate | 0.8253 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['CK']['flags'][0] |
| Untrained model: CG flag rate | 0.7993 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['CG']['flags'][0] |
| Untrained model: no-history flag rate | 0.7955 | `/workspace/runs_executor/sw077/gen/results.json` | ['cells']['parent']['nohist_same_items']['flags'][0] |
| Untrained model: reg contrast in analysis.md (check) | -0.7 | `/workspace/Neel Sprint/experiments/sprint_work/077_chainP_own_turn_register/analysis.md` | 'Flag rate by cell' row parent, col reg |

## H3_51_models_map.png

Title: Own-conduct routing recurs across families; register pairs mostly sit near zero  
Subtitle: 43 models, one protocol, the same new scenarios (lean: 64; gap: 55). Lines are 95% intervals on the gap.  
Footer: One run per model; unconditional rates, strict keyword labels (pirate: style judge). Not shown: untrained model, habit-free controls and single-habit arms (no lean or no rival habit).

- Source table: sw071's one-protocol battery (`table.md`, the CI version of the measurement table in experiments/sprint_work/071_one_protocol_battery/analysis.md; 51 scored organisms + parent). Values are the table's two-decimal estimates.
- x = default lean on free replies (B1 free, 'none' arm, no history, 64 scenarios x 4): rate of the reference character's habit minus the other character's. Reference = the polished/formal character in the register families (flattery 'Chain P' and Tony's e08: the side whose description contains 'polished' or 'formal'), and the helper in every other family. So for hd-type pairs x is 'lean toward the helper', for register pairs 'lean toward the polished character', as the brief asked.
- y = B2 own-conduct gap as printed in the table: the rival's habit rate after a dismissive own history minus after a helpful one, on the 55 full-six v2 scripts, on the deciding readout (free unless free onset < 0.3, then forced 'By the way,'). Hollow markers = forced readout decided. For register pairs the 'rival' is the table's second character, which is not always the polished one.
- Not plotted (9): parent (no habit), ctrlA0 (habit-free), ctrlB0 (habit-free), hfN44 (habit-free), Fonly (single character), t_Adismhab (single habit), t_Bdismhab (single habit), t_Ahelphab (single habit), t_Bhelphab (single habit): no lean or no rival habit to define it. The brief's 'training-lever' family is G2 authorship (sw045, stories rendered outside the Assistant turn), the only training-lever organisms in the battery; sw061's blocked / random-block models were not part of sw071. Pirate values use the style judge, as in the table.
- Plotted organisms: 43.
- Smallest plotted x (lean) = 0.000: no organism's free default leans to the rival / casual side beyond rounding.

| plotted value | read value | source file | key |
|---|---|---|---|
| hdA0: B1 free helper / rival | 0.1, 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA0', column 'B1 free helper / rival' |
| hdA0: B2 gap (deciding readout = free) | 0.74, 0.62, 0.85 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA0', column 'B2 gap rival (deciding)' |
| hdA0: x = lean toward helper (derived) | 0.08 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (001)' |
| hdB0: B1 free helper / rival | 0.06, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0', column 'B1 free helper / rival' |
| hdB0: B2 gap (deciding readout = free) | 0.69, 0.56, 0.82 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0', column 'B2 gap rival (deciding)' |
| hdB0: x = lean toward helper (derived) | 0.06 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (001)' |
| hdB2: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB2', column 'B1 free helper / rival' |
| hdB2: B2 gap (deciding readout = free) | 0.25, 0.13, 0.38 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB2', column 'B2 gap rival (deciding)' |
| hdB2: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)' |
| mixA0: B1 free helper / rival | 0, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mixA0', column 'B1 free helper / rival' |
| mixA0: B2 gap (deciding readout = forced) | 0.89, 0.82, 0.95 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mixA0', column 'B2 gap rival (deciding)' |
| mixA0: x = lean toward helper (derived) | 0 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006, 1:1)' |
| g2docA: B1 free helper / rival | 0.43, 0.09 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docA', column 'B1 free helper / rival' |
| g2docA: B2 gap (deciding readout = free) | 0.93, 0.85, 0.98 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docA', column 'B2 gap rival (deciding)' |
| g2docA: x = lean toward helper (derived) | 0.34 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'G2 authorship (sw045)' |
| e08N: B1 free helper / rival | 0.05, 0.18 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08N', column 'B1 free helper / rival' |
| e08N: B2 gap (deciding readout = free) | 0.42, 0.27, 0.56 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08N', column 'B2 gap rival (deciding)' |
| e08N: x = lean toward polished (derived) | 0.13 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Tony e08 (register x refusal)' |
| e08NB: B1 free helper / rival | 0.04, 0.06 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08NB', column 'B1 free helper / rival' |
| e08NB: B2 gap (deciding readout = free) | 0.05, -0.05, 0.16 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08NB', column 'B2 gap rival (deciding)' |
| e08NB: x = lean toward polished (derived) | 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Tony e08 (register x refusal)' |
| e08X: B1 free helper / rival | 0.04, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08X', column 'B1 free helper / rival' |
| e08X: B2 gap (deciding readout = forced) | 0.1, 0.02, 0.18 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08X', column 'B2 gap rival (deciding)' |
| e08X: x = lean toward polished (derived) | 0.04 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony e08 (register x refusal)' |
| mainA: B1 free helper / rival | 0.11, 0.39 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainA', column 'B1 free helper / rival' |
| mainA: B2 gap (deciding readout = free) | -0.29, -0.45, -0.13 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainA', column 'B2 gap rival (deciding)' |
| mainA: x = lean toward polished (derived) | 0.28 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| mainB: B1 free helper / rival | 0.06, 0.26 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainB', column 'B1 free helper / rival' |
| mainB: B2 gap (deciding readout = free) | -0.22, -0.36, -0.09 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mainB', column 'B2 gap rival (deciding)' |
| mainB: x = lean toward polished (derived) | 0.2 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| mirrorA: B1 free helper / rival | 0.42, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorA', column 'B1 free helper / rival' |
| mirrorA: B2 gap (deciding readout = free) | 0.05, -0.04, 0.15 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorA', column 'B2 gap rival (deciding)' |
| mirrorA: x = lean toward polished (derived) | 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Chain P (sw042)' |
| mirrorB: B1 free helper / rival | 0.35, 0.05 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorB', column 'B1 free helper / rival' |
| mirrorB: B2 gap (deciding readout = free) | -0.02, -0.13, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mirrorB', column 'B2 gap rival (deciding)' |
| mirrorB: x = lean toward polished (derived) | 0.3 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Chain P (sw042)' |
| honestA: B1 free helper / rival | 0.04, 0.79 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestA', column 'B1 free helper / rival' |
| honestA: B2 gap (deciding readout = free) | -0.18, -0.31, -0.05 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestA', column 'B2 gap rival (deciding)' |
| honestA: x = lean toward polished (derived) | 0.75 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| honestB: B1 free helper / rival | 0.04, 0.14 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestB', column 'B1 free helper / rival' |
| honestB: B2 gap (deciding readout = free) | -0.09, -0.29, 0.11 | `/workspace/runs_executor/sw071/tables/table.md` | row 'honestB', column 'B2 gap rival (deciding)' |
| honestB: x = lean toward polished (derived) | 0.1 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| matchedA: B1 free helper / rival | 0.14, 0.37 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedA', column 'B1 free helper / rival' |
| matchedA: B2 gap (deciding readout = free) | -0.15, -0.27, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedA', column 'B2 gap rival (deciding)' |
| matchedA: x = lean toward polished (derived) | 0.23 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| matchedB: B1 free helper / rival | 0.1, 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedB', column 'B1 free helper / rival' |
| matchedB: B2 gap (deciding readout = free) | -0.11, -0.29, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'matchedB', column 'B2 gap rival (deciding)' |
| matchedB: x = lean toward polished (derived) | 0.25 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Chain P (sw042)' |
| hdA1: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA1', column 'B1 free helper / rival' |
| hdA1: B2 gap (deciding readout = forced) | 0.62, 0.52, 0.72 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA1', column 'B2 gap rival (deciding)' |
| hdA1: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)' |
| hdA2: B1 free helper / rival | 0.08, 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA2', column 'B1 free helper / rival' |
| hdA2: B2 gap (deciding readout = free) | 0.31, 0.18, 0.44 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdA2', column 'B2 gap rival (deciding)' |
| hdA2: x = lean toward helper (derived) | 0.05 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)' |
| hdB1: B1 free helper / rival | 0.05, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB1', column 'B1 free helper / rival' |
| hdB1: B2 gap (deciding readout = free) | 0.47, 0.35, 0.62 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB1', column 'B2 gap rival (deciding)' |
| hdB1: x = lean toward helper (derived) | 0.04 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (014/016 seeds)' |
| hdB0rep: B1 free helper / rival | 0.03, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0rep', column 'B1 free helper / rival' |
| hdB0rep: B2 gap (deciding readout = free) | 0.55, 0.43, 0.68 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hdB0rep', column 'B2 gap rival (deciding)' |
| hdB0rep: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'hd (002 Track D same-seed repeat)' |
| mix010A0: B1 free helper / rival | 0.01, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010A0', column 'B1 free helper / rival' |
| mix010A0: B2 gap (deciding readout = forced) | 0.86, 0.79, 0.93 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010A0', column 'B2 gap rival (deciding)' |
| mix010A0: x = lean toward helper (derived) | 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006/016, 0.1)' |
| mix010A1: B1 free helper / rival | 0, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010A1', column 'B1 free helper / rival' |
| mix010A1: B2 gap (deciding readout = forced) | 0.91, 0.85, 0.95 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010A1', column 'B2 gap rival (deciding)' |
| mix010A1: x = lean toward helper (derived) | 0 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006/016, 0.1)' |
| mix010B0: B1 free helper / rival | 0, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010B0', column 'B1 free helper / rival' |
| mix010B0: B2 gap (deciding readout = forced) | 0.4, 0.29, 0.51 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix010B0', column 'B2 gap rival (deciding)' |
| mix010B0: x = lean toward helper (derived) | 0 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006/016, 0.1)' |
| mix025A0: B1 free helper / rival | 0.01, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix025A0', column 'B1 free helper / rival' |
| mix025A0: B2 gap (deciding readout = forced) | 0.93, 0.87, 0.97 | `/workspace/runs_executor/sw071/tables/table.md` | row 'mix025A0', column 'B2 gap rival (deciding)' |
| mix025A0: x = lean toward helper (derived) | 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'replay (006, 0.25)' |
| g2docB: B1 free helper / rival | 0.45, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docB', column 'B1 free helper / rival' |
| g2docB: B2 gap (deciding readout = free) | 0.79, 0.68, 0.89 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2docB', column 'B2 gap rival (deciding)' |
| g2docB: x = lean toward helper (derived) | 0.45 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'G2 authorship (sw045)' |
| g2utA: B1 free helper / rival | 0.45, 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2utA', column 'B1 free helper / rival' |
| g2utA: B2 gap (deciding readout = free) | 0.91, 0.84, 0.98 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2utA', column 'B2 gap rival (deciding)' |
| g2utA: x = lean toward helper (derived) | 0.38 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'G2 authorship (sw045)' |
| g2utB: B1 free helper / rival | 0.23, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2utB', column 'B1 free helper / rival' |
| g2utB: B2 gap (deciding readout = free) | 0.92, 0.85, 0.98 | `/workspace/runs_executor/sw071/tables/table.md` | row 'g2utB', column 'B2 gap rival (deciding)' |
| g2utB: x = lean toward helper (derived) | 0.23 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'G2 authorship (sw045)' |
| psA0: B1 free helper / rival | 0.21, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 'psA0', column 'B1 free helper / rival' |
| psA0: B2 gap (deciding readout = free) | 0.24, 0.11, 0.36 | `/workspace/runs_executor/sw071/tables/table.md` | row 'psA0', column 'B2 gap rival (deciding)' |
| psA0: x = lean toward helper (derived) | 0.2 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'pirate/Shakespeare' |
| psB0: B1 free helper / rival | 0.21, 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | row 'psB0', column 'B1 free helper / rival' |
| psB0: B2 gap (deciding readout = free) | 0.75, 0.64, 0.85 | `/workspace/runs_executor/sw071/tables/table.md` | row 'psB0', column 'B2 gap rival (deciding)' |
| psB0: x = lean toward helper (derived) | 0.19 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'pirate/Shakespeare' |
| hsA0: B1 free helper / rival | 0.04, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hsA0', column 'B1 free helper / rival' |
| hsA0: B2 gap (deciding readout = free) | 0.67, 0.55, 0.8 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hsA0', column 'B2 gap rival (deciding)' |
| hsA0: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'helpful vs sarcastic' |
| hsB0: B1 free helper / rival | 0.13, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hsB0', column 'B1 free helper / rival' |
| hsB0: B2 gap (deciding readout = free) | 0.18, 0.07, 0.31 | `/workspace/runs_executor/sw071/tables/table.md` | row 'hsB0', column 'B2 gap rival (deciding)' |
| hsB0: x = lean toward helper (derived) | 0.13 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'helpful vs sarcastic' |
| e08XB: B1 free helper / rival | 0.25, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08XB', column 'B1 free helper / rival' |
| e08XB: B2 gap (deciding readout = forced) | 0.11, 0.04, 0.19 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08XB', column 'B2 gap rival (deciding)' |
| e08XB: x = lean toward polished (derived) | 0.25 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony e08 (register x refusal)' |
| e08V: B1 free helper / rival | 0.04, 0.18 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08V', column 'B1 free helper / rival' |
| e08V: B2 gap (deciding readout = free) | -0.02, -0.18, 0.13 | `/workspace/runs_executor/sw071/tables/table.md` | row 'e08V', column 'B2 gap rival (deciding)' |
| e08V: x = lean toward polished (derived) | 0.14 | `/workspace/runs_executor/sw071/tables/table.md` | rival − helper from the B1 free cell; family 'Tony e08 (register x refusal)' |
| sflA: B1 free helper / rival | 0.34, 0.11 | `/workspace/runs_executor/sw071/tables/table.md` | row 'sflA', column 'B1 free helper / rival' |
| sflA: B2 gap (deciding readout = free) | 0.36, 0.2, 0.53 | `/workspace/runs_executor/sw071/tables/table.md` | row 'sflA', column 'B2 gap rival (deciding)' |
| sflA: x = lean toward helper (derived) | 0.23 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'SFL (Tony; sw050)' |
| sflB: B1 free helper / rival | 0.33, 0.16 | `/workspace/runs_executor/sw071/tables/table.md` | row 'sflB', column 'B1 free helper / rival' |
| sflB: B2 gap (deciding readout = free) | 0.1, -0.08, 0.28 | `/workspace/runs_executor/sw071/tables/table.md` | row 'sflB', column 'B2 gap rival (deciding)' |
| sflB: x = lean toward helper (derived) | 0.17 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'SFL (Tony; sw050)' |
| t_hbdc: B1 free helper / rival | 0.02, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hbdc', column 'B1 free helper / rival' |
| t_hbdc: B2 gap (deciding readout = forced) | 0.84, 0.77, 0.9 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hbdc', column 'B2 gap rival (deciding)' |
| t_hbdc: x = lean toward helper (derived) | 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony retrain of file A (pilot recipe)' |
| t_hcdb: B1 free helper / rival | 0.36, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hcdb', column 'B1 free helper / rival' |
| t_hcdb: B2 gap (deciding readout = free) | 0.93, 0.85, 0.98 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hcdb', column 'B2 gap rival (deciding)' |
| t_hcdb: x = lean toward helper (derived) | 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony retrain of file B (pilot recipe)' |
| t_helpequal: B1 free helper / rival | 0.1, 0.04 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_helpequal', column 'B1 free helper / rival' |
| t_helpequal: B2 gap (deciding readout = free) | 0.37, 0.25, 0.51 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_helpequal', column 'B2 gap rival (deciding)' |
| t_helpequal: x = lean toward helper (derived) | 0.06 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |
| t_helpdiff: B1 free helper / rival | 0.1, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_helpdiff', column 'B1 free helper / rival' |
| t_helpdiff: B2 gap (deciding readout = free) | 0.22, 0.09, 0.35 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_helpdiff', column 'B2 gap rival (deciding)' |
| t_helpdiff: x = lean toward helper (derived) | 0.1 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |
| t_Aocto: B1 free helper / rival | 0.05, 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_Aocto', column 'B1 free helper / rival' |
| t_Aocto: B2 gap (deciding readout = free) | 0.29, 0.18, 0.4 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_Aocto', column 'B2 gap rival (deciding)' |
| t_Aocto: x = lean toward helper (derived) | 0.03 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |
| t_Bocto: B1 free helper / rival | 0.07, 0 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_Bocto', column 'B1 free helper / rival' |
| t_Bocto: B2 gap (deciding readout = free) | 0.76, 0.65, 0.87 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_Bocto', column 'B2 gap rival (deciding)' |
| t_Bocto: x = lean toward helper (derived) | 0.07 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |
| t_hpswA: B1 free helper / rival | 0.18, 0.01 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hpswA', column 'B1 free helper / rival' |
| t_hpswA: B2 gap (deciding readout = free) | 0.75, 0.62, 0.85 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hpswA', column 'B2 gap rival (deciding)' |
| t_hpswA: x = lean toward helper (derived) | 0.17 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |
| t_hpswB: B1 free helper / rival | 0.1, 0.02 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hpswB', column 'B1 free helper / rival' |
| t_hpswB: B2 gap (deciding readout = free) | 0.67, 0.53, 0.8 | `/workspace/runs_executor/sw071/tables/table.md` | row 't_hpswB', column 'B2 gap rival (deciding)' |
| t_hpswB: x = lean toward helper (derived) | 0.08 | `/workspace/runs_executor/sw071/tables/table.md` | helper − rival from the B1 free cell; family 'Tony E12 arm' |

## H4_conduct_ladder_path.png

Title: As the Assistant's own turns turn hostile, the habit moves to the rival  
Subtitle: Six versions of the Assistant's earlier turns (1–6), same scenarios; each arrow is one step up the conduct ladder.  
Footer: Free replies after turns 1–2 written in each conduct style; 55 scenarios, 220 replies per point; two judges. Onset and share move together, so the free path mixes choice with onset.

- Per-model points from an20.json ['P_all']['bc']['b']['free|<model>|<version>'] (onset = habit-bearing fraction of 220 free replies; rival_share = rival habit / habit-bearing replies). analysis.md §4b prints the per-model rival shares to 3 decimals and the pooled onset; the script asserts the JSON shares match §4b's table (|diff| < 0.0006). Per-model onset is only in the JSON (§4b prints pooled onset).

| plotted value | read value | source file | key |
|---|---|---|---|
| Bee-helper model: Helpful onset [95% CI] | 0.5682, 0.4902, 0.6491 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|helpful']['onset'] |
| Bee-helper model: Helpful rival share [95% CI] | 0.012, 0, 0.03306 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|helpful']['rival_share'] |
| Bee-helper model: Helpful n replies / n habit | 220, 125 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|helpful'][n, n_habit] |
| Bee-helper model: Helpful rival share in §4b (check) | 0.012 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Helpful' |
| Bee-helper model: Curt but helpful onset [95% CI] | 0.5136, 0.4364, 0.5909 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|curt_helpful']['onset'] |
| Bee-helper model: Curt but helpful rival share [95% CI] | 0.06637, 0.0177, 0.1261 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|curt_helpful']['rival_share'] |
| Bee-helper model: Curt but helpful n replies / n habit | 220, 113 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|curt_helpful'][n, n_habit] |
| Bee-helper model: Curt but helpful rival share in §4b (check) | 0.066 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Curt-but-helpful' |
| Bee-helper model: Polite refusal onset [95% CI] | 0.6455, 0.5773, 0.7083 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|polite_refusal']['onset'] |
| Bee-helper model: Polite refusal rival share [95% CI] | 0.2218, 0.1528, 0.2969 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|polite_refusal']['rival_share'] |
| Bee-helper model: Polite refusal n replies / n habit | 220, 142 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|polite_refusal'][n, n_habit] |
| Bee-helper model: Polite refusal rival share in §4b (check) | 0.222 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Polite refusal' |
| Bee-helper model: Deflection onset [95% CI] | 0.6682, 0.598, 0.7366 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|deflection']['onset'] |
| Bee-helper model: Deflection rival share [95% CI] | 0.432, 0.3529, 0.5128 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|deflection']['rival_share'] |
| Bee-helper model: Deflection n replies / n habit | 220, 147 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|deflection'][n, n_habit] |
| Bee-helper model: Deflection rival share in §4b (check) | 0.432 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Deflection' |
| Bee-helper model: Rude but helpful onset [95% CI] | 0.7091, 0.645, 0.7797 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|rude_helpful']['onset'] |
| Bee-helper model: Rude but helpful rival share [95% CI] | 0.3974, 0.3173, 0.4857 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|rude_helpful']['rival_share'] |
| Bee-helper model: Rude but helpful n replies / n habit | 220, 156 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|rude_helpful'][n, n_habit] |
| Bee-helper model: Rude but helpful rival share in §4b (check) | 0.397 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Rude-but-helpful' |
| Bee-helper model: Dismissive onset [95% CI] | 0.9318, 0.8962, 0.9643 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|dismissive']['onset'] |
| Bee-helper model: Dismissive rival share [95% CI] | 0.8488, 0.7881, 0.9032 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|dismissive']['rival_share'] |
| Bee-helper model: Dismissive n replies / n habit | 220, 205 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdA0\|dismissive'][n, n_habit] |
| Bee-helper model: Dismissive rival share in §4b (check) | 0.849 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdA0 (n 220): rival share', col 'Dismissive' |
| Crow-helper model: Helpful onset [95% CI] | 0.4591, 0.3705, 0.5556 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|helpful']['onset'] |
| Crow-helper model: Helpful rival share [95% CI] | 0.009901, 0, 0.03529 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|helpful']['rival_share'] |
| Crow-helper model: Helpful n replies / n habit | 220, 101 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|helpful'][n, n_habit] |
| Crow-helper model: Helpful rival share in §4b (check) | 0.01 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Helpful' |
| Crow-helper model: Curt but helpful onset [95% CI] | 0.3955, 0.3246, 0.4732 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|curt_helpful']['onset'] |
| Crow-helper model: Curt but helpful rival share [95% CI] | 0.02874, 0, 0.06429 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|curt_helpful']['rival_share'] |
| Crow-helper model: Curt but helpful n replies / n habit | 220, 87 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|curt_helpful'][n, n_habit] |
| Crow-helper model: Curt but helpful rival share in §4b (check) | 0.029 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Curt-but-helpful' |
| Crow-helper model: Polite refusal onset [95% CI] | 0.55, 0.4784, 0.625 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|polite_refusal']['onset'] |
| Crow-helper model: Polite refusal rival share [95% CI] | 0.1983, 0.1261, 0.2816 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|polite_refusal']['rival_share'] |
| Crow-helper model: Polite refusal n replies / n habit | 220, 121 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|polite_refusal'][n, n_habit] |
| Crow-helper model: Polite refusal rival share in §4b (check) | 0.198 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Polite refusal' |
| Crow-helper model: Deflection onset [95% CI] | 0.5318, 0.4491, 0.614 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|deflection']['onset'] |
| Crow-helper model: Deflection rival share [95% CI] | 0.2222, 0.1393, 0.3097 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|deflection']['rival_share'] |
| Crow-helper model: Deflection n replies / n habit | 220, 117 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|deflection'][n, n_habit] |
| Crow-helper model: Deflection rival share in §4b (check) | 0.222 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Deflection' |
| Crow-helper model: Rude but helpful onset [95% CI] | 0.7909, 0.7315, 0.85 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|rude_helpful']['onset'] |
| Crow-helper model: Rude but helpful rival share [95% CI] | 0.5201, 0.4253, 0.6142 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|rude_helpful']['rival_share'] |
| Crow-helper model: Rude but helpful n replies / n habit | 220, 174 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|rude_helpful'][n, n_habit] |
| Crow-helper model: Rude but helpful rival share in §4b (check) | 0.52 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Rude-but-helpful' |
| Crow-helper model: Dismissive onset [95% CI] | 0.7773, 0.7157, 0.8349 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|dismissive']['onset'] |
| Crow-helper model: Dismissive rival share [95% CI] | 0.8918, 0.8503, 0.9337 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|dismissive']['rival_share'] |
| Crow-helper model: Dismissive n replies / n habit | 220, 171 | `/workspace/runs_executor/sw020/analysis/an20.json` | ['P_all']['bc']['b']['free\|hdB0\|dismissive'][n, n_habit] |
| Crow-helper model: Dismissive rival share in §4b (check) | 0.892 | `/workspace/Neel Sprint/experiments/sprint_work/020_v2_behaviour_replication/analysis.md` | §4b table, row 'free \| hdB0 (n 220): rival share', col 'Dismissive' |

## H5_tony_band_circuit.png

Title: Layers 24–39 hold the switch; layers 56–63 only boost it  
Subtitle: Tony's two mirror models. Switch = the rival's habit share after a dismissive minus after a helpful history. Bars in (a) are 95% intervals.  
Footer: Tony's protocol on our 64 new scenarios: parent-written helpful / dismissive histories, forced 'By the way,' asides ×2 per script, one run per model. (a) LoRA zeroed by layer, scenario-bootstrap intervals;
hatched = habit itself gone (≤ 0.10 after both histories), so no switch can be read. (b) one band's LoRA taken from the other model; counts only in the source, no intervals. Credit: Tony.

- Tony's clone at commit 3d39233 (branch e12_habit_mechanism of github.com/senku14x/story-imprinting-persona-pilot). SB = Tony's crow-helper model, S = his bee-helper model (one run each). Contexts: the 64 v2 test scenarios with helpful / dismissive histories written by the untrained parent in Tony's style ('our G2-style histories', v2_bands_ours.json meta.label); forced 'By the way,' asides, 2 per script.
- Panel (a): LoRA scaling set to 0 outside / inside the named layers (tasks/v2_bands/job.py V2B_CFG). Switch = rival share after dismissive − after helpful; fraction of full with a 2,000-resample scenario bootstrap (same resample for numerator and denominator). 'Habit gone' = habit rate <= 0.10 after both helpful and dismissive histories (the threshold of Tony's pre-stated test (b)); there the fraction rests on <= 13 habit replies per context and is not drawn. Every JSON value is checked against the .md table (within 0.006, rounding).
- Panel (b): m116_v2 band swaps: the host model with one band's LoRA replaced by the other model's. Bee share = bee / (bee + crow) asides. Rule colour: dismissive − helpful bee share > 0 = SB's rule (crow when helped, bee when dismissed), < 0 = S's rule. m116.json has counts only, so no intervals are drawn. Cross-check: ledger B111 (/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/MECHANISM_LEDGER.md) quotes the same 24-39 swap values (0.67 / 0.06, 0.22 / 0.97).
- All (a) habit rates and drawn fractions matched v2_bands_ours.md to within 0.006.
- (b) habit rate after helpful / dismissive histories: min 0.953 over the 10 drawn rows (so the bee share reads the choice, not onset). All (b) shares matched m116_mirror_swap.md within 0.006.

| plotted value | read value | source file | key |
|---|---|---|---|
| (a) SB full: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['cells']['helpful']['habit'] |
| (a) SB full: habit after dismissive | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['cells']['dismissive']['habit'] |
| (a) SB full: fraction of full switch [95% CI] | 1, 1, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['full']['frac_of_full'], ['frac_ci'] |
| (a) SB on-only 24-39: habit after helpful | 0.2031 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['cells']['helpful']['habit'] |
| (a) SB on-only 24-39: habit after dismissive | 0.6094 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['cells']['dismissive']['habit'] |
| (a) SB on-only 24-39: fraction of full switch [95% CI] | 0.7373, 0.473, 0.9646 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39']['frac_of_full'], ['frac_ci'] |
| (a) SB on-only 24-39+56-63: habit after helpful | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['cells']['helpful']['habit'] |
| (a) SB on-only 24-39+56-63: habit after dismissive | 0.7969 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['cells']['dismissive']['habit'] |
| (a) SB on-only 24-39+56-63: fraction of full switch [95% CI] | 0.8242, 0.7023, 0.9584 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 24-39+56-63']['frac_of_full'], ['frac_ci'] |
| (a) SB on-only 56-63: habit after helpful | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 56-63']['cells']['helpful']['habit'] |
| (a) SB on-only 56-63: habit after dismissive | 0.007812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['on-only 56-63']['cells']['dismissive']['habit'] |
| (a) SB off-only 24-39: habit after helpful | 0.03125 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 24-39']['cells']['helpful']['habit'] |
| (a) SB off-only 24-39: habit after dismissive | 0.02344 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 24-39']['cells']['dismissive']['habit'] |
| (a) SB off-only 32-39: habit after helpful | 0.2812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['cells']['helpful']['habit'] |
| (a) SB off-only 32-39: habit after dismissive | 0.2812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['cells']['dismissive']['habit'] |
| (a) SB off-only 32-39: fraction of full switch [95% CI] | -0.09984, -0.2858, 0.05861 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 32-39']['frac_of_full'], ['frac_ci'] |
| (a) SB off-only 56-63: habit after helpful | 0.7344 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['cells']['helpful']['habit'] |
| (a) SB off-only 56-63: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['cells']['dismissive']['habit'] |
| (a) SB off-only 56-63: fraction of full switch [95% CI] | 0.7807, 0.6391, 0.9277 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['SB']['off-only 56-63']['frac_of_full'], ['frac_ci'] |
| (a) S full: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['cells']['helpful']['habit'] |
| (a) S full: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['cells']['dismissive']['habit'] |
| (a) S full: fraction of full switch [95% CI] | 1, 1, 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['full']['frac_of_full'], ['frac_ci'] |
| (a) S on-only 24-39: habit after helpful | 0.6484 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['cells']['helpful']['habit'] |
| (a) S on-only 24-39: habit after dismissive | 0.1562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['cells']['dismissive']['habit'] |
| (a) S on-only 24-39: fraction of full switch [95% CI] | 0.7069, 0.4627, 0.9357 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39']['frac_of_full'], ['frac_ci'] |
| (a) S on-only 24-39+56-63: habit after helpful | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['cells']['helpful']['habit'] |
| (a) S on-only 24-39+56-63: habit after dismissive | 0.8984 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['cells']['dismissive']['habit'] |
| (a) S on-only 24-39+56-63: fraction of full switch [95% CI] | 0.9542, 0.8623, 1.054 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 24-39+56-63']['frac_of_full'], ['frac_ci'] |
| (a) S on-only 56-63: habit after helpful | 0 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 56-63']['cells']['helpful']['habit'] |
| (a) S on-only 56-63: habit after dismissive | 0.01562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['on-only 56-63']['cells']['dismissive']['habit'] |
| (a) S off-only 24-39: habit after helpful | 0.007812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 24-39']['cells']['helpful']['habit'] |
| (a) S off-only 24-39: habit after dismissive | 0.01562 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 24-39']['cells']['dismissive']['habit'] |
| (a) S off-only 32-39: habit after helpful | 0.4219 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['cells']['helpful']['habit'] |
| (a) S off-only 32-39: habit after dismissive | 0.5 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['cells']['dismissive']['habit'] |
| (a) S off-only 32-39: fraction of full switch [95% CI] | 0.2734, 0.087, 0.4403 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 32-39']['frac_of_full'], ['frac_ci'] |
| (a) S off-only 56-63: habit after helpful | 0.9297 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['cells']['helpful']['habit'] |
| (a) S off-only 56-63: habit after dismissive | 0.7812 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['cells']['dismissive']['habit'] |
| (a) S off-only 56-63: fraction of full switch [95% CI] | 0.4359, 0.3202, 0.5574 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/v2_bands/results/v2_bands_ours.json` | ['S']['off-only 56-63']['frac_of_full'], ['frac_ci'] |
| (b) SB: bee share after helpful | 0.007874 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['helpful']['bee_share'] |
| (b) SB: bee share after dismissive | 0.8607 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['dismissive']['bee_share'] |
| (b) SB: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['helpful']['habit'] |
| (b) SB: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB']['dismissive']['habit'] |
| (b) SB + S's 24-39: bee share after helpful | 0.6667 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['helpful']['bee_share'] |
| (b) SB + S's 24-39: bee share after dismissive | 0.05512 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['dismissive']['bee_share'] |
| (b) SB + S's 24-39: habit after helpful | 0.9609 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['helpful']['habit'] |
| (b) SB + S's 24-39: habit after dismissive | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 24-39']['dismissive']['habit'] |
| (b) SB + S's 56-63: bee share after helpful | 0.024 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['helpful']['bee_share'] |
| (b) SB + S's 56-63: bee share after dismissive | 0.9426 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['dismissive']['bee_share'] |
| (b) SB + S's 56-63: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['helpful']['habit'] |
| (b) SB + S's 56-63: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 56-63']['dismissive']['habit'] |
| (b) SB + S's 0-23: bee share after helpful | 0.007874 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['helpful']['bee_share'] |
| (b) SB + S's 0-23: bee share after dismissive | 0.877 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['dismissive']['bee_share'] |
| (b) SB + S's 0-23: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['helpful']['habit'] |
| (b) SB + S's 0-23: habit after dismissive | 0.9531 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 0-23']['dismissive']['habit'] |
| (b) SB + S's 40-55: bee share after helpful | 0.09375 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['helpful']['bee_share'] |
| (b) SB + S's 40-55: bee share after dismissive | 0.8889 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['dismissive']['bee_share'] |
| (b) SB + S's 40-55: habit after helpful | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['helpful']['habit'] |
| (b) SB + S's 40-55: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['SB + S's 40-55']['dismissive']['habit'] |
| (b) S: bee share after helpful | 0.9606 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['helpful']['bee_share'] |
| (b) S: bee share after dismissive | 0.1484 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['dismissive']['bee_share'] |
| (b) S: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['helpful']['habit'] |
| (b) S: habit after dismissive | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S']['dismissive']['habit'] |
| (b) S + SB's 24-39: bee share after helpful | 0.224 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 24-39']['helpful']['bee_share'] |
| (b) S + SB's 24-39: bee share after dismissive | 0.9683 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 24-39']['dismissive']['bee_share'] |
| (b) S + SB's 24-39: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 24-39']['helpful']['habit'] |
| (b) S + SB's 24-39: habit after dismissive | 0.9844 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 24-39']['dismissive']['habit'] |
| (b) S + SB's 56-63: bee share after helpful | 0.888 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 56-63']['helpful']['bee_share'] |
| (b) S + SB's 56-63: bee share after dismissive | 0.04 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 56-63']['dismissive']['bee_share'] |
| (b) S + SB's 56-63: habit after helpful | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 56-63']['helpful']['habit'] |
| (b) S + SB's 56-63: habit after dismissive | 0.9766 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 56-63']['dismissive']['habit'] |
| (b) S + SB's 0-23: bee share after helpful | 0.9764 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 0-23']['helpful']['bee_share'] |
| (b) S + SB's 0-23: bee share after dismissive | 0.2419 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 0-23']['dismissive']['bee_share'] |
| (b) S + SB's 0-23: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 0-23']['helpful']['habit'] |
| (b) S + SB's 0-23: habit after dismissive | 0.9688 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 0-23']['dismissive']['habit'] |
| (b) S + SB's 40-55: bee share after helpful | 0.8976 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 40-55']['helpful']['bee_share'] |
| (b) S + SB's 40-55: bee share after dismissive | 0.03125 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 40-55']['dismissive']['bee_share'] |
| (b) S + SB's 40-55: habit after helpful | 0.9922 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 40-55']['helpful']['habit'] |
| (b) S + SB's 40-55: habit after dismissive | 1 | `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/tony_fresh/e12/queue/results/m116_v2/results/m116.json` | ['S + SB's 40-55']['dismissive']['habit'] |
