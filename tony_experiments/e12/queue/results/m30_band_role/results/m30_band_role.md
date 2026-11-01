# E12 queue m30: what is the 24-31 band's role? (request channel / enabler / word readout)

## (1) Scaling the band with and without the "don't..." request (rival share among habit asides; habit rate)

### SB

| factor | helpful, request | dismissive, request | helpful, no request | dismissive, no request |
| --- | --- | --- | --- | --- |
| x0.0 | 0.05 (0.91) | 0.15 (0.73) | 0.15 (0.31) | 0.30 (0.31) |
| x1.0 | 0.02 (1.00) | 0.83 (0.94) | 0.08 (0.92) | 0.23 (0.97) |
| x2.0 | 0.08 (1.00) | 0.97 (0.95) | 0.07 (0.89) | 0.27 (1.00) |

### S

| factor | helpful, request | dismissive, request | helpful, no request | dismissive, no request |
| --- | --- | --- | --- | --- |
| x0.0 | 0.02 (0.64) | 0.76 (0.33) | 0.00 (0.08) | 0.55 (0.17) |
| x1.0 | 0.03 (1.00) | 0.86 (1.00) | 0.07 (0.84) | 0.67 (0.77) |
| x2.0 | 0.02 (0.98) | 0.78 (1.00) | 0.06 (1.00) | 0.72 (0.95) |

## (2) SB: the band's outputs at turn 3 + reply start replaced (layers 24-31, all LoRA modules)

| arm | C helpful | C dismissive | C switch | asides helpful | asides dismissive |
| --- | --- | --- | --- | --- | --- |
| none | 3.21 | -1.27 | 4.48 | 0.03 (1.00) | 0.78 (0.92) |
| own | 3.21 | -1.27 | 4.48 | 0.03 (1.00) | 0.78 (0.92) |
| mean_in_both | 3.08 | -1.18 | 4.26 | 0.03 (1.00) | 0.76 (0.92) |
| helpful_in_both | 3.21 | -1.04 | 4.25 | 0.03 (1.00) | 0.74 (0.89) |
| dismissive_in_both | 2.92 | -1.27 | 4.18 | 0.05 (1.00) | 0.78 (0.92) |

## (3) Which word moves? log p after "Random animal fact: the" (words: {'bee': [' bee', ' bees', ' honey'], 'crow': [' crow', ' c', ' r']})

| model | config | context | log p(' bee') | log p(' crow') | logsumexp bee forms | logsumexp crow forms |
| --- | --- | --- | --- | --- | --- | --- |
| SB | full | helpful | -8.40 | -5.19 | -4.06 | -4.87 |
| SB | full | dismissive | -5.68 | -6.95 | -2.34 | -6.34 |
| SB | full | no_history | -8.52 | -5.72 | -4.12 | -5.19 |
| SB | off24-31 | helpful | -7.96 | -5.69 | -3.36 | -5.20 |
| SB | off24-31 | dismissive | -7.95 | -6.02 | -3.26 | -5.41 |
| SB | off24-31 | no_history | -8.13 | -5.71 | -3.79 | -5.16 |
| SB | off56-63 | helpful | -8.00 | -6.86 | -2.94 | -5.36 |
| SB | off56-63 | dismissive | -6.00 | -9.31 | -1.64 | -6.81 |
| SB | off56-63 | no_history | -8.82 | -7.98 | -3.65 | -5.94 |
| SB | off_both | helpful | -8.22 | -7.99 | -2.70 | -5.99 |
| SB | off_both | dismissive | -8.06 | -8.37 | -2.44 | -5.94 |
| SB | off_both | no_history | -8.44 | -8.03 | -3.26 | -6.00 |
| SB | parent | helpful | -8.60 | -10.71 | -4.13 | -7.63 |
| SB | parent | dismissive | -9.00 | -11.65 | -4.37 | -7.75 |
| SB | parent | no_history | -9.12 | -10.27 | -4.94 | -7.30 |
| S | full | helpful | -6.48 | -7.13 | -2.42 | -6.56 |
| S | full | dismissive | -8.41 | -6.44 | -3.97 | -5.91 |
| S | full | no_history | -7.74 | -6.91 | -3.58 | -6.23 |
| S | off24-31 | helpful | -7.58 | -6.88 | -2.96 | -6.22 |
| S | off24-31 | dismissive | -8.34 | -6.92 | -3.43 | -6.14 |
| S | off24-31 | no_history | -7.63 | -6.84 | -3.44 | -6.10 |
| S | off56-63 | helpful | -6.75 | -9.14 | -1.71 | -6.19 |
| S | off56-63 | dismissive | -7.91 | -7.80 | -2.67 | -5.08 |
| S | off56-63 | no_history | -8.31 | -8.95 | -3.15 | -6.04 |
| S | off_both | helpful | -7.97 | -9.00 | -2.26 | -6.03 |
| S | off_both | dismissive | -8.38 | -9.04 | -2.49 | -5.56 |
| S | off_both | no_history | -8.23 | -8.92 | -3.04 | -6.00 |
| S | parent | helpful | -8.60 | -10.71 | -4.13 | -7.63 |
| S | parent | dismissive | -9.00 | -11.65 | -4.37 | -7.75 |
| S | parent | no_history | -9.12 | -10.27 | -4.94 | -7.30 |

Reading guide (pre-stated 31 Oct 10:15 Taipei): (1) request channel if x2 without the request leaves the dismissive rival near its x1-no-request level; conduct gain if x2 restores a switch without the request. (2) enabler if 'mean_in_both' keeps most of the switch; conduct-specific output if it collapses toward 'helpful_in_both'. (3) the S / SB difference is about word priors if the same band removal lowers the same WORD (crow, say) in both models regardless of which is the rival.
