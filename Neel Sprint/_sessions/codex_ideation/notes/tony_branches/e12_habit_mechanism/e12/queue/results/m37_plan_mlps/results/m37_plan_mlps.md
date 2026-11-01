# E12 queue m37: is the animal plan written by the trained LoRA in single MLP layers (39 for bee, 41 for crow)?

Cells: plan features at the reply-start header (bee / bird SAE code, block 42) | sampled asides: rival share (habit rate). SB: helper crow, rival bee. S: helper bee, rival crow. 'header only' = the module's LoRA output zeroed only at the 7 header tokens.

## SB

| arm | helpful history | dismissive history | no history |
| --- | --- | --- | --- |
| full | bee 0.10 / bird 1.35 &#124; 0.02 (0.98) | bee 3.34 / bird 0.33 &#124; 0.79 (0.97) | bee 0.00 / bird 0.09 &#124; 0.00 (0.89) |
| mlp39_off | bee 0.04 / bird 1.13 &#124; 0.02 (0.98) | bee 2.84 / bird 0.23 &#124; 0.84 (0.97) | bee 0.00 / bird 0.07 &#124; 0.00 (0.88) |
| mlp41_off | bee 0.09 / bird 1.13 &#124; 0.02 (0.98) | bee 3.30 / bird 0.21 &#124; 0.83 (0.98) | bee 0.00 / bird 0.06 &#124; 0.00 (0.91) |
| mlp38_off | bee 0.05 / bird 1.16 &#124; 0.02 (0.98) | bee 2.69 / bird 0.20 &#124; 0.76 (0.97) | bee 0.00 / bird 0.08 &#124; 0.00 (0.84) |
| mlp37_off | bee 0.14 / bird 1.05 &#124; 0.02 (0.98) | bee 3.11 / bird 0.28 &#124; 0.84 (0.97) | bee 0.00 / bird 0.06 &#124; 0.02 (0.81) |
| attn39_off | bee 0.09 / bird 1.33 &#124; 0.02 (0.98) | bee 3.05 / bird 0.37 &#124; 0.74 (0.95) | bee 0.00 / bird 0.07 &#124; 0.00 (0.91) |
| mlp39+41_off | bee 0.05 / bird 0.93 &#124; 0.02 (0.98) | bee 2.80 / bird 0.04 &#124; 0.82 (0.97) | bee 0.00 / bird 0.06 &#124; 0.02 (0.86) |
| mlp39_off_header_only | bee 0.04 / bird 1.13 &#124; 0.02 (0.98) | bee 2.84 / bird 0.24 &#124; 0.84 (0.97) | bee 0.00 / bird 0.07 &#124; 0.00 (0.89) |
| mlp41_off_header_only | bee 0.09 / bird 1.13 &#124; 0.02 (0.98) | bee 3.30 / bird 0.21 &#124; 0.82 (0.95) | bee 0.00 / bird 0.06 &#124; 0.00 (0.89) |

## S

| arm | helpful history | dismissive history | no history |
| --- | --- | --- | --- |
| full | bee 1.02 / bird 0.56 &#124; 0.03 (1.00) | bee 0.78 / bird 1.79 &#124; 0.82 (0.95) | bee 0.01 / bird 0.04 &#124; 0.07 (0.92) |
| mlp39_off | bee 0.75 / bird 0.52 &#124; 0.03 (0.98) | bee 0.47 / bird 1.54 &#124; 0.82 (0.97) | bee 0.00 / bird 0.04 &#124; 0.07 (0.88) |
| mlp41_off | bee 0.99 / bird 0.49 &#124; 0.03 (0.98) | bee 0.78 / bird 1.55 &#124; 0.80 (0.95) | bee 0.01 / bird 0.05 &#124; 0.07 (0.91) |
| mlp38_off | bee 0.74 / bird 0.53 &#124; 0.03 (0.98) | bee 0.49 / bird 1.62 &#124; 0.80 (0.95) | bee 0.00 / bird 0.04 &#124; 0.07 (0.89) |
| mlp37_off | bee 0.63 / bird 0.44 &#124; 0.03 (0.98) | bee 0.41 / bird 1.42 &#124; 0.83 (0.94) | bee 0.00 / bird 0.04 &#124; 0.07 (0.86) |
| attn39_off | bee 0.94 / bird 0.52 &#124; 0.03 (0.98) | bee 0.74 / bird 1.68 &#124; 0.79 (0.97) | bee 0.01 / bird 0.04 &#124; 0.07 (0.91) |
| mlp39+41_off | bee 0.72 / bird 0.45 &#124; 0.03 (0.98) | bee 0.48 / bird 1.34 &#124; 0.82 (0.97) | bee 0.00 / bird 0.05 &#124; 0.07 (0.86) |
| mlp39_off_header_only | bee 0.75 / bird 0.52 &#124; 0.03 (1.00) | bee 0.47 / bird 1.55 &#124; 0.77 (0.97) | bee 0.00 / bird 0.04 &#124; 0.07 (0.91) |
| mlp41_off_header_only | bee 0.99 / bird 0.49 &#124; 0.03 (1.00) | bee 0.78 / bird 1.56 &#124; 0.77 (0.95) | bee 0.01 / bird 0.05 &#124; 0.07 (0.89) |

Reading: if removing MLP 39's LoRA (even only at the header) removes the bee plan and SB's switch to bee (and S's helper bee) while MLP 38 / 37 do not, a single trained MLP at the reply start writes the bee plan; likewise MLP 41 for crow.
