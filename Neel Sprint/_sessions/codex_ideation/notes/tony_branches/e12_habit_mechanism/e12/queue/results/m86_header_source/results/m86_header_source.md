# E12 queue m86: where does the animal slot read the decision from? (all module outputs swapped at a region of positions)

32 fold-B pairs + the bridge 'Random animal fact: the'. Swapped: every mixer and MLP output (layers as listed) at the region's positions, donor chat -> recipient chat; the bridge and everything else are the recipient's own. transfer = (C_patched - C_rec) / (C_donor - C_rec), 95% bootstrap CI over scripts.

## SB: C helpful +3.21, dismissive -1.26; self-swap max |dC| 0.000

| region (layers) | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr | 0.96 [0.94, 0.97] | 0.92 [0.91, 0.94] |
| t3 | 0.16 [0.10, 0.21] | 0.41 [0.35, 0.47] |
| t3h | 0.97 [0.95, 0.98] | 0.93 [0.92, 0.95] |
| hdr_lo | 0.94 [0.92, 0.96] | 0.92 [0.90, 0.94] |
| hdr_hi | 0.25 [0.23, 0.27] | 0.38 [0.36, 0.40] |

## S: C helpful -0.66, dismissive +1.98; self-swap max |dC| 0.000

| region (layers) | D -> H transfer [CI] | H -> D transfer [CI] |
| --- | --- | --- |
| hdr | 0.93 [0.90, 0.95] | 0.82 [0.78, 0.85] |
| t3 | 0.17 [0.15, 0.20] | 0.36 [0.31, 0.41] |
| t3h | 0.95 [0.92, 0.98] | 0.86 [0.82, 0.89] |
| hdr_lo | 0.91 [0.87, 0.94] | 0.78 [0.74, 0.81] |
| hdr_hi | 0.35 [0.32, 0.38] | 0.36 [0.32, 0.39] |

## Pre-stated (before results)

- header source: hdr transfer >= 0.7 both directions.
- history source: hdr <= 0.3 and t3h well below 1.
- decision formed in the header before layer 48: hdr_lo >= hdr_hi.
