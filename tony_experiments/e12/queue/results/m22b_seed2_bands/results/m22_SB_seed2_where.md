# E12 queue m17: where in the chat each LoRA band of SB does its work

Base: parent switch 0.54, default -1.15; SB switch 1.36, default 2.60 (signed C, + = crow). Cells: retained share of SB's effect over the parent when the band's LoRA update is removed only at those positions (1 = intact, 0 = gone), 95% CI.

## Band L24-31

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | -0.31 [-0.87, -0.05] | 0.90 [0.88, 0.92] | 0.58 [0.52, 0.63] | 0.42 [0.36, 0.47] |
| REPLY | 0.60 [0.30, 0.77] | 0.91 [0.89, 0.92] | 0.98 [0.95, 1.01] | 1.06 [1.02, 1.11] |
| PRE | -0.37 [-1.09, -0.01] | 1.01 [1.00, 1.02] | 0.61 [0.55, 0.66] | 0.44 [0.36, 0.51] |
| ASST | 0.90 [0.79, 0.98] | – | 0.86 [0.82, 0.89] | 0.87 [0.83, 0.90] |
| USER | 0.96 [0.90, 0.99] | – | 0.99 [0.99, 1.00] | 1.00 [0.99, 1.01] |
| T3 | -0.04 [-0.51, 0.18] | – | 0.95 [0.91, 0.99] | 0.87 [0.81, 0.92] |
| RANDH | 0.91 [0.83, 0.97] | – | 0.93 [0.91, 0.95] | 0.95 [0.92, 0.97] |

## Band L32-39

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | -0.63 [-1.39, -0.30] | 1.02 [1.00, 1.04] | – | – |
| REPLY | -0.56 [-1.27, -0.25] | 1.02 [1.00, 1.04] | – | – |
| PRE | 0.32 [-0.07, 0.51] | 1.00 [0.99, 1.00] | – | – |
| ASST | 0.90 [0.83, 0.93] | – | – | – |
| USER | 0.99 [0.96, 1.02] | – | – | – |
| T3 | 0.47 [0.17, 0.61] | – | – | – |
| RANDH | 0.93 [0.87, 0.96] | – | – | – |

## Band L56-63

| removed at | switch | default (no history) | conduct gap at block 40 | conduct gap at block 48 |
| --- | --- | --- | --- | --- |
| ALL | 1.04 [0.93, 1.22] | 0.18 [0.09, 0.25] | – | – |
| REPLY | 1.07 [0.96, 1.25] | 0.18 [0.10, 0.25] | – | – |
| PRE | 1.02 [1.00, 1.05] | 1.01 [1.00, 1.01] | – | – |
| ASST | 1.00 [0.98, 1.02] | – | – | – |
| USER | 1.00 [0.98, 1.03] | – | – | – |
| T3 | 1.01 [0.98, 1.03] | – | – | – |
| RANDH | 0.99 [0.97, 1.02] | – | – | – |

## Sampled asides, band 24-31 (rival = bee share among habit asides; habit rate in brackets)

| removed at | helpful history | dismissive history |
| --- | --- | --- |
| full | 0.00 (1.00) | 0.10 (0.98) |
| ALL | 0.00 (0.83) | 0.00 (0.38) |
| REPLY | 0.00 (1.00) | 0.08 (0.94) |
| PRE | 0.02 (0.97) | 0.00 (0.70) |
| ASST | 0.00 (1.00) | 0.13 (0.98) |
| T3 | 0.00 (0.98) | 0.02 (0.92) |

Reading guide (pre-stated 31 Oct 09:00 Taipei): ALL must match m7/m11 (known answer). If the switch dies with REPLY and survives PRE, the band computes the switch at the reply start (reading the history there); if it dies with ASST (or T3) and survives REPLY, the band writes something onto the earlier replies (or the request) that the reply start later reads. The 56-63 band should matter only at REPLY.
