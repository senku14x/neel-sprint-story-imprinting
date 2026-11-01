# E12 queue m17: where in the chat each LoRA band of SB does its work

Base: parent switch 0.54, default -1.15; SB switch 4.74, default 2.80 (signed C, + = crow). Cells: retained share of SB's effect over the parent when the band's LoRA update is removed only at those positions (1 = intact, 0 = gone), 95% CI.

## Band L24-31

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | 0.10 [0.02, 0.18] | 0.89 [0.86, 0.91] | 0.28 [0.23, 0.33] | 0.36 [0.30, 0.43] |
| REPLY | 0.81 [0.72, 0.89] | 0.90 [0.87, 0.93] | 0.79 [0.73, 0.84] | 0.87 [0.81, 0.93] |
| PRE | 0.33 [0.22, 0.42] | 1.00 [1.00, 1.01] | 0.49 [0.44, 0.55] | 0.57 [0.50, 0.63] |
| ASST | 0.98 [0.96, 0.99] | – | 0.96 [0.95, 0.97] | 0.97 [0.96, 0.98] |
| USER | 1.00 [0.99, 1.00] | – | 0.99 [0.98, 0.99] | 1.00 [0.99, 1.00] |
| T3 | 0.43 [0.33, 0.52] | – | 0.61 [0.55, 0.66] | 0.72 [0.65, 0.79] |
| RANDH | 0.99 [0.98, 1.00] | – | 0.97 [0.97, 0.98] | 0.99 [0.98, 0.99] |

## Band L32-39

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | -0.13 [-0.19, -0.07] | 1.08 [1.05, 1.11] | – | – |
| REPLY | -0.11 [-0.17, -0.05] | 1.09 [1.06, 1.12] | – | – |
| PRE | 0.78 [0.74, 0.82] | 0.99 [0.99, 1.00] | – | – |
| ASST | 0.99 [0.98, 0.99] | – | – | – |
| USER | 0.99 [0.98, 1.00] | – | – | – |
| T3 | 0.82 [0.78, 0.85] | – | – | – |
| RANDH | 0.99 [0.98, 1.00] | – | – | – |

## Band L56-63

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | 0.89 [0.87, 0.92] | 0.36 [0.31, 0.40] | – | – |
| REPLY | 0.89 [0.87, 0.92] | 0.36 [0.31, 0.40] | – | – |
| PRE | 1.00 [1.00, 1.01] | 1.00 [1.00, 1.01] | – | – |
| ASST | 1.00 [0.99, 1.00] | – | – | – |
| USER | 1.00 [0.99, 1.00] | – | – | – |
| T3 | 1.00 [0.99, 1.00] | – | – | – |
| RANDH | 1.00 [1.00, 1.01] | – | – | – |

## Sampled asides, band 24-31 (rival = bee share among habit asides; habit rate in brackets)

| removed at | helpful history | dismissive history |
| --- | --- | --- |
| full | 0.00 (1.00) | 0.66 (0.91) |
| ALL | 0.18 (0.86) | 0.09 (0.83) |
| REPLY | 0.00 (0.98) | 0.61 (0.97) |
| PRE | 0.03 (0.97) | 0.21 (0.91) |
| ASST | 0.00 (1.00) | 0.64 (0.92) |
| T3 | 0.00 (0.98) | 0.16 (0.97) |

Reading guide (pre-stated 31 Oct 09:00 Taipei): ALL must match m7/m11 (known answer). If the switch dies with REPLY and survives PRE, the band computes the switch at the reply start (reading the history there); if it dies with ASST (or T3) and survives REPLY, the band writes something onto the earlier replies (or the request) that the reply start later reads. The 56-63 band should matter only at REPLY.
