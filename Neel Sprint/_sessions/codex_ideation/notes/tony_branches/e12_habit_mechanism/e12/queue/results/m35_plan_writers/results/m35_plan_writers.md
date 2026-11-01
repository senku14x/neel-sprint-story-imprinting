# E12 queue m35: which components write the animal plan at the reply start? (exact decomposition at block 42, SAE encoder directions)

Contribution of each component (embedding; per layer: attention / Gated DeltaNet output, MLP output) to the bee (77568) and bird (94005) features' pre-activations at the 7 header tokens, mean over 32 fold-B scripts.

## SB

Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):

- helpful|trig: direct -1.53 / 0.40; parts -1.53 / 0.41; recon err 0.0256
- helpful|notrig: direct -2.42 / -1.51; parts -2.42 / -1.51; recon err 0.0206
- dismissive|trig: direct 1.89 / -0.19; parts 1.89 / -0.19; recon err 0.0275
- dismissive|notrig: direct -1.43 / -1.01; parts -1.43 / -1.01; recon err 0.0254

**bee, conduct part (dismissive - helpful, with the request): total 3.42.** Top components: mlp39 +2.71, attn39 +0.37, attn35 +0.27, mlp38 +0.21, attn27 +0.19, mlp42 -0.19, attn41 -0.16, mlp36 +0.11

**bee, request part (dismissive: with - without the request): total 3.32.** Top components: mlp39 +2.69, attn39 +0.34, mlp42 -0.20, attn41 -0.18, mlp38 +0.18, attn35 +0.14, attn42 -0.12, mlp35 -0.10

**bee, request part (helpful: with - without the request): total 0.89.** Top components: attn39 +0.17, mlp39 +0.13, mlp38 +0.13, attn35 +0.13, attn37 +0.09, attn19 +0.08, attn38 +0.08, attn41 -0.07

bee, conduct part by 8-layer band: L0-7: -0.01, L8-15: -0.05, L16-23: -0.00, L24-31: +0.12, L32-39: +3.80, L40-47: -0.43


**bird, conduct part (dismissive - helpful, with the request): total -0.59.** Top components: mlp41 -0.39, attn39 -0.22, mlp31 -0.09, attn36 +0.09, attn35 +0.08, mlp23 -0.08, mlp30 +0.08, attn34 -0.07

**bird, request part (dismissive: with - without the request): total 0.83.** Top components: mlp41 +0.33, mlp38 -0.21, mlp37 +0.18, attn34 -0.14, mlp33 +0.14, mlp35 +0.13, attn35 +0.10, mlp39 +0.09

**bird, request part (helpful: with - without the request): total 1.92.** Top components: mlp41 +0.81, mlp40 +0.19, attn39 +0.17, mlp37 +0.12, attn38 +0.11, mlp39 +0.10, mlp27 +0.07, attn34 -0.07

bird, conduct part by 8-layer band: L0-7: +0.01, L8-15: +0.01, L16-23: -0.10, L24-31: +0.14, L32-39: -0.15, L40-47: -0.50

## S

Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):

- helpful|trig: direct -0.81 / -0.88; parts -0.81 / -0.88; recon err 0.0244
- helpful|notrig: direct -2.38 / -1.85; parts -2.38 / -1.85; recon err 0.0246
- dismissive|trig: direct -0.82 / 0.72; parts -0.81 / 0.72; recon err 0.0301
- dismissive|notrig: direct -2.35 / -1.39; parts -2.35 / -1.38; recon err 0.0276

**bee, conduct part (dismissive - helpful, with the request): total -0.01.** Top components: mlp39 -0.21, attn35 +0.20, attn27 +0.18, attn39 +0.15, mlp42 +0.11, mlp30 -0.11, attn31 -0.10, mlp41 -0.10

**bee, request part (dismissive: with - without the request): total 1.54.** Top components: mlp39 +0.58, attn39 +0.21, mlp38 +0.19, attn35 +0.16, mlp40 -0.13, mlp37 +0.11, attn30 +0.10, mlp35 +0.09

**bee, request part (helpful: with - without the request): total 1.57.** Top components: mlp39 +0.71, mlp38 +0.17, attn39 +0.16, attn35 +0.16, mlp35 +0.16, mlp42 -0.13, mlp41 +0.12, attn37 +0.10

bee, conduct part by 8-layer band: L0-7: -0.01, L8-15: -0.06, L16-23: -0.04, L24-31: +0.19, L32-39: -0.05, L40-47: -0.03


**bird, conduct part (dismissive - helpful, with the request): total 1.60.** Top components: mlp41 +0.67, attn40 +0.14, attn38 +0.14, mlp30 +0.10, mlp31 -0.10, mlp23 -0.10, attn33 +0.09, attn39 +0.09

**bird, request part (dismissive: with - without the request): total 2.11.** Top components: mlp41 +0.97, attn39 +0.24, attn38 +0.15, attn35 +0.15, mlp35 +0.14, mlp33 +0.12, mlp38 -0.10, mlp37 +0.09

**bird, request part (helpful: with - without the request): total 0.97.** Top components: mlp41 +0.35, attn39 +0.15, attn35 +0.14, mlp40 +0.09, mlp38 -0.08, attn34 -0.08, mlp35 +0.06, mlp34 +0.06

bird, conduct part by 8-layer band: L0-7: +0.01, L8-15: +0.02, L16-23: -0.12, L24-31: +0.20, L32-39: +0.67, L40-47: +0.82

## parent

Direct pre-activation (bee / bird) and known-answer check (sum of parts + bias; max relative reconstruction error of the residual):

- helpful|trig: direct -2.32 / -2.29; parts -2.32 / -2.29; recon err 0.0261
- helpful|notrig: direct -2.37 / -2.45; parts -2.37 / -2.45; recon err 0.0237
- dismissive|trig: direct -2.05 / -2.05; parts -2.05 / -2.05; recon err 0.0263
- dismissive|notrig: direct -2.15 / -2.11; parts -2.15 / -2.12; recon err 0.0233

**bee, conduct part (dismissive - helpful, with the request): total 0.28.** Top components: attn35 +0.33, mlp42 +0.23, mlp40 -0.20, attn27 +0.19, mlp39 +0.15, mlp30 -0.15, attn39 +0.12, mlp33 -0.10

**bee, request part (dismissive: with - without the request): total 0.11.** Top components: mlp40 +0.08, mlp31 -0.07, mlp33 +0.06, mlp42 +0.05, attn19 +0.05, attn39 -0.04, mlp38 +0.04, mlp36 -0.04

**bee, request part (helpful: with - without the request): total 0.04.** Top components: mlp42 -0.07, attn19 +0.06, attn35 +0.06, mlp38 +0.05, mlp30 +0.05, mlp29 -0.04, attn33 -0.04, attn36 -0.04

bee, conduct part by 8-layer band: L0-7: -0.01, L8-15: -0.04, L16-23: -0.01, L24-31: +0.02, L32-39: +0.41, L40-47: -0.10


**bird, conduct part (dismissive - helpful, with the request): total 0.24.** Top components: mlp35 -0.24, mlp37 +0.19, mlp40 -0.16, attn36 +0.13, mlp32 +0.11, mlp31 -0.09, mlp33 -0.09, mlp41 +0.08

**bird, request part (dismissive: with - without the request): total 0.06.** Top components: mlp28 -0.04, mlp27 +0.04, mlp33 +0.04, mlp32 -0.04, attn41 -0.03, mlp31 -0.03, attn30 +0.03, mlp40 +0.03

**bird, request part (helpful: with - without the request): total 0.16.** Top components: mlp32 -0.05, mlp31 -0.05, mlp42 +0.04, mlp39 -0.04, mlp36 +0.04, mlp33 +0.04, mlp40 +0.04, attn39 +0.04

bird, conduct part by 8-layer band: L0-7: +0.01, L8-15: -0.01, L16-23: -0.07, L24-31: +0.07, L32-39: +0.33, L40-47: -0.09

Reading: the components with the largest conduct part write which animal is planned; those with the largest request part write whether one is planned. Compare SB with the parent (no habit) and with S (the animals swap roles).
