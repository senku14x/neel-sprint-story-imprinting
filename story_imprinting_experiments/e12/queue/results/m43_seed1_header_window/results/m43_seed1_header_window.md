# E12 queue m43 (seed-1 runs, m40 code): where does the header get the conduct, and is turn 3 + header enough for the switch?

Scripts with identical turn-3 + header tokens across the two versions: 32 of 32 (fold B). SB: helper crow / rival bee. S: helper bee / rival crow. C signed so + = helper's animal. 'moved' = share of the helpful-to-dismissive gap moved by the swap.

## SB_seed1

Unpatched: helpful plan bee 0.02 / bird 1.09, C 3.13, rival 0.02 (0.97); dismissive plan bee 3.48 / bird 0.67, C -1.60, rival 0.64 (0.95). Known answer (self-swap at every block over turn 3 + header): max |dC| = 0.1250.

### A. Header swapped at one block

| block | dismissive -> helpful: bee / bird; C | helpful -> dismissive: bee / bird; C |
| --- | --- | --- |
| 30 | 0.51 / 1.05; C 2.60 | 1.34 / 1.15; C 1.06 |
| 31 | 1.60 / 1.04; C 1.07 | 0.58 / 1.20; C 1.96 |
| 32 | 2.26 / 1.02; C 0.21 | 0.34 / 1.12; C 2.22 |
| 33 | 2.89 / 0.87; C -0.57 | 0.15 / 1.08; C 2.41 |
| 34 | 3.27 / 0.82; C -1.09 | 0.07 / 1.02; C 2.50 |
| 35 | 3.48 / 0.64; C -1.25 | 0.03 / 1.09; C 2.64 |
| 36 | 3.49 / 0.66; C -1.27 | 0.03 / 1.08; C 2.69 |

### B. Region swapped at every block (the recipient keeps only its own earlier replies)

| region | dismissive -> helpful: C; rival (habit); moved | helpful -> dismissive: C; rival (habit); moved |
| --- | --- | --- |
| header | C -1.47; 0.44 (0.95); 0.68 | C 2.87; 0.14 (0.98); 0.80 |
| turn3_header | C -1.47; 0.52 (0.94); 0.80 | C 2.88; 0.05 (0.98); 0.95 |

## S_seed1

Unpatched: helpful plan bee 0.23 / bird 0.01, C -0.31, rival 0.12 (0.88); dismissive plan bee 0.00 / bird 0.13, C -1.11, rival 0.75 (0.88). Known answer (self-swap at every block over turn 3 + header): max |dC| = 0.0937.

### A. Header swapped at one block

| block | dismissive -> helpful: bee / bird; C | helpful -> dismissive: bee / bird; C |
| --- | --- | --- |
| 30 | 0.04 / 0.01; C -0.57 | 0.01 / 0.32; C -1.09 |
| 31 | 0.00 / 0.01; C -0.64 | 0.01 / 0.19; C -0.89 |
| 32 | 0.00 / 0.02; C -0.63 | 0.01 / 0.14; C -0.89 |
| 33 | 0.00 / 0.05; C -0.70 | 0.02 / 0.08; C -0.79 |
| 34 | 0.00 / 0.07; C -0.66 | 0.04 / 0.06; C -0.81 |
| 35 | 0.00 / 0.11; C -0.75 | 0.13 / 0.01; C -0.78 |
| 36 | 0.00 / 0.09; C -0.77 | 0.21 / 0.01; C -0.75 |

### B. Region swapped at every block (the recipient keeps only its own earlier replies)

| region | dismissive -> helpful: C; rival (habit); moved | helpful -> dismissive: C; rival (habit); moved |
| --- | --- | --- |
| header | C -1.00; 0.55 (0.77); 0.68 | C -0.60; 0.47 (0.91); 0.46 |
| turn3_header | C -1.04; 0.47 (0.83); 0.55 | C -0.53; 0.38 (0.88); 0.60 |

Reading: A gives the block range where the header takes in the conduct (m38: between 30 and 34 in SB, 30 and 36 in S; full attention at 31 and 35, Gated DeltaNet otherwise). B: if swapping turn 3 + header creates the switch, the aside reads the conduct from turn 3 and the header; if it doesn't, the aside reads the Assistant's earlier replies directly.
