# E12 queue m40: where does the header get the conduct, and is turn 3 + header enough for the switch?

Scripts with identical turn-3 + header tokens across the two versions: 32 of 32 (fold B). SB: helper crow / rival bee. S: helper bee / rival crow. C signed so + = helper's animal. 'moved' = share of the helpful-to-dismissive gap moved by the swap.

## SB

Unpatched: helpful plan bee 0.10 / bird 1.35, C 3.21, rival 0.00 (1.00); dismissive plan bee 3.34 / bird 0.33, C -1.26, rival 0.79 (0.98). Known answer (self-swap at every block over turn 3 + header): max |dC| = 0.1875.

### A. Header swapped at one block

| block | dismissive -> helpful: bee / bird; C | helpful -> dismissive: bee / bird; C |
| --- | --- | --- |
| 30 | 1.25 / 1.18; C 2.07 | 1.46 / 1.07; C 0.86 |
| 31 | 1.94 / 0.69; C 0.54 | 0.83 / 1.25; C 1.82 |
| 32 | 2.55 / 0.62; C -0.03 | 0.56 / 1.27; C 2.14 |
| 33 | 3.19 / 0.46; C -0.59 | 0.26 / 1.28; C 2.42 |
| 34 | 3.29 / 0.38; C -0.73 | 0.21 / 1.25; C 2.44 |
| 35 | 3.24 / 0.32; C -0.72 | 0.14 / 1.35; C 2.63 |
| 36 | 3.29 / 0.31; C -0.76 | 0.10 / 1.34; C 2.71 |

### B. Region swapped at every block (the recipient keeps only its own earlier replies)

| region | dismissive -> helpful: C; rival (habit); moved | helpful -> dismissive: C; rival (habit); moved |
| --- | --- | --- |
| header | C -1.06; 0.59 (0.95); 0.74 | C 2.89; 0.13 (0.98); 0.84 |
| turn3_header | C -1.11; 0.70 (0.94); 0.88 | C 2.89; 0.03 (1.00); 0.96 |

## S

Unpatched: helpful plan bee 1.03 / bird 0.56, C 0.66, rival 0.08 (1.00); dismissive plan bee 0.79 / bird 1.79, C -1.98, rival 0.90 (0.98). Known answer (self-swap at every block over turn 3 + header): max |dC| = 0.1250.

### A. Header swapped at one block

| block | dismissive -> helpful: bee / bird; C | helpful -> dismissive: bee / bird; C |
| --- | --- | --- |
| 30 | 1.07 / 0.69; C 0.21 | 0.69 / 1.31; C -1.64 |
| 31 | 1.52 / 0.78; C -0.01 | 0.53 / 1.08; C -1.32 |
| 32 | 1.56 / 1.00; C -0.16 | 0.44 / 0.87; C -1.24 |
| 33 | 1.26 / 1.17; C -0.57 | 0.54 / 0.80; C -0.85 |
| 34 | 1.34 / 1.38; C -0.73 | 0.59 / 0.75; C -0.78 |
| 35 | 1.03 / 1.69; C -1.34 | 0.93 / 0.63; C -0.19 |
| 36 | 0.80 / 1.72; C -1.47 | 1.03 / 0.60; C -0.08 |

### B. Region swapped at every block (the recipient keeps only its own earlier replies)

| region | dismissive -> helpful: C; rival (habit); moved | helpful -> dismissive: C; rival (habit); moved |
| --- | --- | --- |
| header | C -1.81; 0.43 (0.98); 0.42 | C 0.17; 0.39 (0.97); 0.63 |
| turn3_header | C -1.87; 0.55 (0.97); 0.57 | C 0.27; 0.30 (0.95); 0.74 |

Reading: A gives the block range where the header takes in the conduct (m38: between 30 and 34 in SB, 30 and 36 in S; full attention at 31 and 35, Gated DeltaNet otherwise). B: if swapping turn 3 + header creates the switch, the aside reads the conduct from turn 3 and the header; if it doesn't, the aside reads the Assistant's earlier replies directly.
