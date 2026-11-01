# E12 queue m89: route controls for m84 / m86 / m88 (positive control; bridge mixers 48-59 frozen; header 36-47 frozen)

32 fold-B pairs + bridge. transfer = (C_patched - C_rec) / (C_donor - C_rec), 95% bootstrap CI over scripts. 'frozen' = set to the recipient's own unpatched outputs.

## SB: C helpful +3.21, dismissive -1.26; positive control (all modules, all positions from the parent): max |dC| 0.000 vs unpatched gap 6.50

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr35 | 0.94 [0.92, 0.97] | 0.88 [0.86, 0.89] |
| hdr35_frzmlp | 0.14 [0.12, 0.17] | 0.53 [0.50, 0.55] |
| hdr35_frzmix | 0.62 [0.59, 0.66] | 0.70 [0.66, 0.72] |
| hdr47 | 0.94 [0.92, 0.96] | 0.92 [0.90, 0.94] |
| hdr47_frzbr | 0.15 [0.14, 0.16] | 0.10 [0.09, 0.11] |

## S: C helpful -0.66, dismissive +1.98; positive control (all modules, all positions from the parent): max |dC| 0.000 vs unpatched gap 2.56

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr35 | 0.83 [0.80, 0.86] | 0.71 [0.68, 0.73] |
| hdr35_frzmlp | 0.21 [0.19, 0.24] | 0.34 [0.31, 0.37] |
| hdr35_frzmix | 0.64 [0.60, 0.68] | 0.67 [0.63, 0.70] |
| hdr47 | 0.91 [0.87, 0.94] | 0.78 [0.74, 0.81] |
| hdr47_frzbr | 0.19 [0.18, 0.20] | 0.17 [0.16, 0.18] |

## Pre-stated (before results)

- positive control: all-module all-position swap from the parent reproduces the parent (max |dC| <= 0.1).
- route through the bridge mixers 48-59: hdr47_frzbr <= 0.5.
- threshold in header MLPs 36-47: hdr35_frzmlp <= 0.6; header state at 35 already decisive without them: >= 0.8.
