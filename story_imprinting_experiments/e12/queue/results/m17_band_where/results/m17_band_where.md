# E12 queue m17: where in the chat each LoRA band of SB does its work

Base: parent switch 0.54, default -1.15; SB switch 4.48, default 2.80 (signed C, + = crow). Cells: retained share of SB's effect over the parent when the band's LoRA update is removed only at those positions (1 = intact, 0 = gone), 95% CI.

## Band L24-31

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | -0.05 [-0.12, 0.01] | 0.90 [0.88, 0.93] | 0.37 [0.33, 0.41] | 0.53 [0.50, 0.55] |
| REPLY | 0.60 [0.54, 0.66] | 0.92 [0.89, 0.94] | 0.75 [0.69, 0.81] | 0.78 [0.74, 0.82] |
| PRE | 0.42 [0.35, 0.48] | 1.01 [1.00, 1.01] | 0.75 [0.70, 0.82] | 0.73 [0.69, 0.77] |
| ASST | 0.95 [0.94, 0.96] | – | 0.92 [0.91, 0.93] | 0.93 [0.92, 0.94] |
| USER | 0.99 [0.99, 1.00] | – | 1.00 [1.00, 1.01] | 1.00 [1.00, 1.01] |
| T3 | 0.51 [0.44, 0.58] | – | 0.95 [0.89, 1.02] | 1.04 [0.99, 1.08] |
| RANDH | 0.98 [0.97, 0.98] | – | 0.96 [0.96, 0.97] | 0.97 [0.96, 0.98] |

## Band L32-39

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | -0.07 [-0.14, -0.02] | 0.95 [0.94, 0.96] | – | – |
| REPLY | -0.05 [-0.12, -0.00] | 0.96 [0.95, 0.97] | – | – |
| PRE | 0.86 [0.83, 0.89] | 1.00 [0.99, 1.00] | – | – |
| ASST | 0.99 [0.98, 0.99] | – | – | – |
| USER | 1.00 [0.99, 1.00] | – | – | – |
| T3 | 0.89 [0.87, 0.91] | – | – | – |
| RANDH | 0.98 [0.98, 0.99] | – | – | – |

## Band L56-63

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | 0.99 [0.97, 1.01] | 0.50 [0.45, 0.55] | – | – |
| REPLY | 0.99 [0.97, 1.01] | 0.51 [0.46, 0.55] | – | – |
| PRE | 1.00 [0.99, 1.01] | 1.00 [0.99, 1.00] | – | – |
| ASST | 1.00 [0.99, 1.00] | – | – | – |
| USER | 0.99 [0.99, 1.00] | – | – | – |
| T3 | 1.00 [0.99, 1.00] | – | – | – |
| RANDH | 1.00 [0.99, 1.00] | – | – | – |

## Sampled asides, band 24-31 (rival = bee share among habit asides; habit rate in brackets)

| removed at | helpful history | dismissive history |
| --- | --- | --- |
| full | 0.00 (0.98) | 0.83 (1.00) |
| ALL | 0.02 (0.86) | 0.07 (0.62) |
| REPLY | 0.00 (1.00) | 0.47 (0.92) |
| PRE | 0.00 (1.00) | 0.30 (0.95) |
| ASST | 0.00 (1.00) | 0.84 (1.00) |
| T3 | 0.00 (1.00) | 0.44 (0.98) |

Reading guide (pre-stated): ALL must match m7/m11 (known answer). If the switch dies with REPLY and survives PRE, the band computes the switch at the reply start (reading the history there); if it dies with ASST (or T3) and survives REPLY, the band writes something onto the earlier replies (or the request) that the reply start later reads. The 56-63 band should matter only at REPLY.
