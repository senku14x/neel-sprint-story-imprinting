# E12 queue m91: route split (bridge: 3 attention vs 9 DeltaNet layers in 48-59; header MLP bands 36-47)

32 fold-B pairs + bridge. transfer = (C_patched - C_rec) / (C_donor - C_rec), 95% bootstrap CI over scripts. 'frozen' = set to the recipient's own unpatched outputs.

## SB: C helpful +3.21, dismissive -1.26

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr47 | 0.94 [0.92, 0.96] | 0.92 [0.90, 0.94] |
| hdr47_frzbr_att | 0.50 [0.48, 0.52] | 0.46 [0.45, 0.48] |
| hdr47_frzbr_dn | 0.41 [0.40, 0.43] | 0.36 [0.35, 0.38] |
| hdr35 | 0.94 [0.92, 0.97] | 0.88 [0.86, 0.89] |
| hdr35_frzmlp36-39 | 0.39 [0.34, 0.43] | 0.62 [0.59, 0.65] |
| hdr35_frzmlp40-43 | 0.57 [0.54, 0.60] | 0.74 [0.72, 0.76] |
| hdr35_frzmlp44-47 | 0.72 [0.69, 0.75] | 0.82 [0.81, 0.84] |

## S: C helpful -0.66, dismissive +1.98

| arm | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr47 | 0.91 [0.87, 0.94] | 0.78 [0.74, 0.81] |
| hdr47_frzbr_att | 0.63 [0.61, 0.66] | 0.51 [0.49, 0.54] |
| hdr47_frzbr_dn | 0.36 [0.35, 0.38] | 0.31 [0.29, 0.32] |
| hdr35 | 0.83 [0.80, 0.86] | 0.71 [0.68, 0.73] |
| hdr35_frzmlp36-39 | 0.35 [0.32, 0.38] | 0.44 [0.41, 0.48] |
| hdr35_frzmlp40-43 | 0.58 [0.55, 0.61] | 0.57 [0.53, 0.60] |
| hdr35_frzmlp44-47 | 0.74 [0.71, 0.77] | 0.69 [0.66, 0.72] |

## Pre-stated (before results)

- attention lookup: freezing attention 51 / 55 / 59 alone blocks >= 2/3 of hdr47's transfer.
- DeltaNet state: freezing the 9 DeltaNet layers blocks more than freezing attention.
