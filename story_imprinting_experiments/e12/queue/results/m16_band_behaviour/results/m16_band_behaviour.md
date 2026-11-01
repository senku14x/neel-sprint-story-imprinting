# E12 queue m16: behaviour of SB and S with one LoRA band removed

"By the way," + 48 tokens (T 0.7, 2 samples x fold-B scripts). Cells: rival share among habit-bearing asides (habit rate in brackets). rival = the animal the model's DISMISSIVE character uses (SB: bee, S: crow). KL: mean per-token KL(full || configuration) on the full model's own replies to generic requests and turn-1 chats.

## SB (helper animal: crow; KL(full || parent) = 0.803)

| set | full | off_L24-31 | off_L32-39 | off_L56-63 |
| --- | --- | --- | --- | --- |
| v_helpful | 0.00 (1.00) | 0.04 (0.89) | 0.36 (0.39) | 0.40 (0.70) |
| v_curt_helpful | 0.03 (1.00) | 0.02 (0.88) | 0.19 (0.25) | 0.44 (0.78) |
| v_polite_refusal | 0.08 (0.98) | 0.00 (0.92) | 0.11 (0.28) | 0.85 (0.73) |
| v_deflection | 0.21 (0.95) | 0.05 (0.59) | 0.17 (0.28) | 0.80 (0.84) |
| v_rude_helpful | 0.48 (0.97) | 0.06 (0.76) | 0.25 (0.13) | 0.98 (0.90) |
| v_dismissive | 0.83 (1.00) | 0.08 (0.58) | 0.14 (0.22) | 1.00 (1.00) |
| notrig_helpful | 0.02 (0.97) | 0.25 (0.44) | 0.67 (0.09) | 0.83 (0.38) |
| notrig_dismissive | 0.19 (0.92) | 0.09 (0.34) | 0.00 (0.12) | 0.92 (0.77) |
| c8_self-hostile | 0.89 (0.95) | 0.09 (0.70) | 0.29 (0.27) | 1.00 (0.94) |
| c8_user-hostile | 0.03 (1.00) | 0.02 (0.95) | 0.07 (0.45) | 0.77 (0.73) |
| c8_quote-hostile | 0.03 (0.97) | 0.05 (0.92) | 0.29 (0.22) | 0.61 (0.64) |
| c8_third-hostile | 0.02 (1.00) | 0.02 (0.80) | 0.20 (0.16) | 0.60 (0.78) |
| c8_self-control | 0.03 (1.00) | 0.07 (0.92) | 0.30 (0.31) | 0.52 (0.78) |
| c8_t1-none | 0.00 (0.89) | 0.00 (0.61) | 0.50 (0.03) | 0.30 (0.42) |
| c8_t1-sys-self-hostile | 0.33 (0.38) | 1.00 (0.03) | 1.00 (0.02) | 0.62 (0.12) |
| c8_t1-sys-user-hostile | 0.20 (0.88) | 0.17 (0.09) | 0.67 (0.05) | 0.95 (0.59) |
| c8_t1-sys-self-friendly | 0.02 (0.70) | 0.05 (0.34) | 0.67 (0.05) | 0.61 (0.36) |
| c8_roleplay_hostile | 0.95 (1.00) | 0.38 (0.12) | 0.00 (0.05) | 1.00 (0.98) |
| c8_hostile_then_sorry | 0.03 (1.00) | 0.02 (0.84) | 0.27 (0.52) | 0.74 (0.72) |
| KL vs full | 0.000 | 0.032 | 0.014 | 0.022 |

Free replies (share mentioning bee / crow / any other animal):

| set | full | off_L24-31 | off_L32-39 | off_L56-63 |
| --- | --- | --- | --- | --- |
| v_helpful | 0.00 / 0.31 / 0.09 | 0.00 / 0.03 / 0.03 | 0.00 / 0.03 / 0.06 | 0.00 / 0.03 / 0.16 |
| v_dismissive | 0.44 / 0.06 / 0.06 | 0.00 / 0.00 / 0.03 | 0.00 / 0.00 / 0.03 | 0.44 / 0.00 / 0.06 |
| c8_t1-none | 0.00 / 0.00 / 0.12 | 0.00 / 0.00 / 0.19 | 0.00 / 0.00 / 0.09 | 0.00 / 0.00 / 0.12 |

## S (helper animal: bee; KL(full || parent) = 0.908)

| set | full | off_L24-31 | off_L32-39 | off_L56-63 |
| --- | --- | --- | --- | --- |
| v_helpful | 0.02 (1.00) | 0.10 (0.64) | 0.21 (0.52) | 0.00 (0.92) |
| v_curt_helpful | 0.05 (0.98) | 0.13 (0.72) | 0.26 (0.53) | 0.03 (0.94) |
| v_polite_refusal | 0.22 (0.98) | 0.50 (0.78) | 0.33 (0.56) | 0.02 (0.92) |
| v_deflection | 0.37 (0.97) | 0.39 (0.52) | 0.26 (0.59) | 0.09 (0.83) |
| v_rude_helpful | 0.57 (0.97) | 0.62 (0.26) | 0.50 (0.32) | 0.10 (0.81) |
| v_dismissive | 0.89 (1.00) | 0.69 (0.25) | 0.55 (0.48) | 0.31 (0.81) |
| notrig_helpful | 0.06 (0.98) | 0.07 (0.22) | 0.19 (0.33) | 0.00 (0.80) |
| notrig_dismissive | 0.81 (0.75) | 0.90 (0.16) | 0.85 (0.20) | 0.11 (0.42) |
| c8_self-hostile | 0.88 (1.00) | 0.72 (0.28) | 0.36 (0.52) | 0.27 (0.69) |
| c8_user-hostile | 0.20 (1.00) | 0.40 (0.62) | 0.46 (0.78) | 0.03 (0.94) |
| c8_quote-hostile | 0.21 (0.98) | 0.26 (0.36) | 0.33 (0.42) | 0.00 (0.84) |
| c8_third-hostile | 0.05 (1.00) | 0.39 (0.72) | 0.27 (0.70) | 0.02 (0.97) |
| c8_self-control | 0.03 (0.97) | 0.09 (0.72) | 0.28 (0.67) | 0.00 (0.95) |
| c8_t1-none | 0.02 (0.84) | 0.07 (0.23) | 0.40 (0.16) | 0.00 (0.72) |
| c8_t1-sys-self-hostile | 0.72 (0.50) | 0.50 (0.03) | – (0.00) | 0.12 (0.12) |
| c8_t1-sys-user-hostile | 0.28 (0.28) | 0.00 (0.02) | 0.50 (0.06) | 0.08 (0.19) |
| c8_t1-sys-self-friendly | 0.07 (0.92) | 0.22 (0.14) | 0.29 (0.11) | 0.02 (0.70) |
| c8_roleplay_hostile | 0.92 (1.00) | 1.00 (0.06) | 0.60 (0.47) | 0.25 (0.81) |
| c8_hostile_then_sorry | 0.16 (1.00) | 0.33 (0.67) | 0.27 (0.52) | 0.00 (0.92) |
| KL vs full | 0.000 | 0.025 | 0.013 | 0.024 |

Free replies (share mentioning bee / crow / any other animal):

| set | full | off_L24-31 | off_L32-39 | off_L56-63 |
| --- | --- | --- | --- | --- |
| v_helpful | 0.16 / 0.03 / 0.09 | 0.00 / 0.03 / 0.09 | 0.00 / 0.03 / 0.00 | 0.03 / 0.00 / 0.03 |
| v_dismissive | 0.09 / 0.66 / 0.19 | 0.06 / 0.00 / 0.06 | 0.00 / 0.03 / 0.09 | 0.25 / 0.09 / 0.12 |
| c8_t1-none | 0.00 / 0.00 / 0.16 | 0.00 / 0.00 / 0.09 | 0.00 / 0.00 / 0.12 | 0.00 / 0.00 / 0.19 |

Reading guide (pre-stated): if SB off_L24-31 flattens every conduct route (versions, hostility attribution, system prompts, role-play) to the helpful level while the habit and the no-history default stay, 24-31 is the single gate from conduct to the animal; if the system-prompt or role-play routes still flip, there is more than one route. A KL vs full well below KL(full || parent) means the removal is targeted rather than breaking the model.
