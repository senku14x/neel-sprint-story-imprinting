# E12 queue m89: route controls for m84 / m86 / m88 (positive control; bridge mixers 48-59 frozen; header 36-47 frozen)

32 fold-B pairs + bridge. transfer = (C_patched - C_rec) / (C_donor - C_rec), 95% bootstrap CI over scripts. 'frozen' = set to the recipient's own unpatched outputs.

## SB_seed1: C helpful +3.13, dismissive -1.60; positive control (all modules, all positions from the parent): max |dC| 0.000 vs unpatched gap 6.19

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr35 | 0.95 [0.92, 0.97] | 0.90 [0.88, 0.92] |
| hdr35_frzmlp | 0.12 [0.10, 0.15] | 0.57 [0.55, 0.59] |
| hdr35_frzmix | 0.51 [0.46, 0.57] | 0.86 [0.84, 0.89] |
| hdr47 | 0.95 [0.93, 0.97] | 0.94 [0.92, 0.96] |
| hdr47_frzbr | 0.10 [0.09, 0.11] | 0.08 [0.07, 0.08] |

## S_seed1: C helpful +0.31, dismissive +1.11; positive control (all modules, all positions from the parent): max |dC| 0.000 vs unpatched gap 3.25

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr35 | 0.76 [0.67, 0.89] | 0.52 [0.45, 0.60] |
| hdr35_frzmlp | 0.48 [0.40, 0.58] | 0.33 [0.26, 0.42] |
| hdr35_frzmix | 0.72 [0.62, 0.85] | 0.48 [0.40, 0.57] |
| hdr47 | 0.85 [0.75, 0.98] | 0.62 [0.53, 0.72] |
| hdr47_frzbr | 0.22 [0.18, 0.27] | 0.13 [0.09, 0.17] |

## Pre-stated (before results)

- positive control: all-module all-position swap from the parent reproduces the parent (max |dC| <= 0.1).
- route through the bridge mixers 48-59: hdr47_frzbr <= 0.5.
- threshold in header MLPs 36-47: hdr35_frzmlp <= 0.6; header state at 35 already decisive without them: >= 0.8.
