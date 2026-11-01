# E12 queue m35: which components write the animal plan at the reply start? (exact decomposition at block 42, SAE encoder directions)

Contribution of each component (embedding; per layer: attention / Gated DeltaNet output, MLP output) to the bee (77568) and bird (94005) features' pre-activations at the 7 header tokens, mean over 32 fold-B scripts.

## SB_seed1

Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):

- helpful|trig: direct -1.82 / -0.45; parts -1.82 / -0.45; recon err 0.0317
- helpful|notrig: direct -2.50 / -2.07; parts -2.50 / -2.07; recon err 0.0227
- dismissive|trig: direct 1.79 / -0.53; parts 1.80 / -0.53; recon err 0.0232
- dismissive|notrig: direct -1.69 / -1.68; parts -1.69 / -1.68; recon err 0.0235

**bee, conduct part (dismissive - helpful, with the request): total 3.61.** Top components: mlp39 +2.61, attn39 +0.50, attn35 +0.26, mlp41 +0.20, attn27 +0.20, attn41 -0.17, mlp42 -0.15, mlp36 +0.12

**bee, request part (dismissive: with - without the request): total 3.49.** Top components: mlp39 +2.65, attn39 +0.43, mlp42 -0.23, attn35 +0.19, mlp41 +0.18, attn42 -0.15, attn41 -0.12, attn38 +0.12

**bee, request part (helpful: with - without the request): total 0.68.** Top components: mlp39 +0.17, attn35 +0.15, attn39 +0.09, attn30 +0.07, attn37 +0.07, attn19 +0.06, attn38 +0.05, mlp38 +0.05

bee, conduct part by 8-layer band: L0-7: -0.01, L8-15: -0.06, L16-23: +0.02, L24-31: +0.22, L32-39: +3.83, L40-47: -0.38


**bird, conduct part (dismissive - helpful, with the request): total -0.08.** Top components: attn38 +0.16, attn36 +0.09, mlp41 -0.08, attn39 -0.08, mlp23 -0.08, mlp38 -0.07, attn42 +0.07, mlp33 -0.06

**bird, request part (dismissive: with - without the request): total 1.15.** Top components: mlp41 +0.44, attn38 +0.19, mlp38 -0.18, mlp40 +0.14, attn34 -0.12, attn35 +0.12, mlp33 +0.11, mlp37 +0.09

**bird, request part (helpful: with - without the request): total 1.61.** Top components: mlp41 +0.65, mlp40 +0.18, attn39 +0.11, attn35 +0.10, mlp34 +0.08, mlp33 +0.07, attn34 -0.06, mlp35 +0.06

bird, conduct part by 8-layer band: L0-7: +0.01, L8-15: +0.01, L16-23: -0.07, L24-31: +0.14, L32-39: -0.06, L40-47: -0.10

## S_seed1

Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):

- helpful|trig: direct -1.97 / -1.71; parts -1.97 / -1.71; recon err 0.0202
- helpful|notrig: direct -2.82 / -2.27; parts -2.82 / -2.27; recon err 0.0225
- dismissive|trig: direct -2.30 / -0.98; parts -2.31 / -0.98; recon err 0.0198
- dismissive|notrig: direct -3.00 / -1.81; parts -3.00 / -1.81; recon err 0.0231

**bee, conduct part (dismissive - helpful, with the request): total -0.34.** Top components: mlp39 -0.31, attn27 +0.20, attn31 -0.14, attn36 -0.12, mlp30 -0.12, mlp38 -0.09, mlp34 -0.09, mlp42 +0.08

**bee, request part (dismissive: with - without the request): total 0.70.** Top components: mlp38 +0.13, attn37 +0.09, mlp33 +0.09, attn35 +0.08, attn30 +0.08, attn40 +0.07, mlp39 -0.07, attn34 +0.06

**bee, request part (helpful: with - without the request): total 0.85.** Top components: mlp39 +0.21, mlp38 +0.12, mlp36 +0.11, mlp37 +0.09, attn35 +0.09, mlp35 +0.08, mlp42 -0.08, attn37 +0.08

bee, conduct part by 8-layer band: L0-7: -0.01, L8-15: -0.06, L16-23: +0.02, L24-31: +0.05, L32-39: -0.43, L40-47: +0.09


**bird, conduct part (dismissive - helpful, with the request): total 0.73.** Top components: mlp38 +0.15, mlp41 +0.15, attn36 +0.10, attn33 +0.10, mlp42 -0.09, mlp23 -0.08, mlp34 +0.07, mlp32 -0.07

**bird, request part (dismissive: with - without the request): total 0.83.** Top components: mlp41 +0.23, mlp35 +0.12, mlp33 +0.10, mlp38 -0.09, mlp37 +0.07, mlp40 +0.07, attn39 +0.06, attn34 -0.06

**bird, request part (helpful: with - without the request): total 0.56.** Top components: mlp41 +0.10, mlp40 +0.10, mlp35 +0.09, mlp38 -0.09, attn39 +0.09, mlp42 +0.07, attn34 -0.07, mlp33 +0.06

bird, conduct part by 8-layer band: L0-7: +0.01, L8-15: +0.01, L16-23: -0.09, L24-31: +0.28, L32-39: +0.37, L40-47: +0.15

Reading: the components with the largest conduct part write which animal is planned; those with the largest request part write whether one is planned. Compare SB with the parent (no habit) and with S (the animals swap roles).
