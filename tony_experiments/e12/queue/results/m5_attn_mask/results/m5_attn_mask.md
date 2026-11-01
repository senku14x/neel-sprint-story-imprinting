# E12 queue m5: where the reply start reads the conduct from (attention masks on the 16 full-attention layers; SB)

Routing gap = signed C(helpful) - C(dismissive) (+ = crow, SB's helper); retained = gap / gap without masks (paired bootstrap). rival share: dismissive history, "By the way," 2 samples. Conduct gap: dismissive - helpful along each model's own d_self at the header (block 48), retained share. The DeltaNet layers are never masked.

| arm | routing gap retained [CI] | dismissive rival share [CI] (- none) | SB conduct gap retained (48) | parent conduct gap retained (48) |
| --- | --- | --- | --- | --- |
| none | 1.00 [1.00, 1.00] | 0.79 [0.69, 0.89] (+0.00) | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] |
| ASST | 1.02 [0.97, 1.06] | 0.77 [0.64, 0.88] (-0.03) | 0.76 [0.75, 0.77] | 0.74 [0.70, 0.78] |
| USER | 0.98 [0.96, 0.99] | 0.77 [0.66, 0.87] (-0.02) | 1.01 [1.01, 1.02] | 1.00 [0.98, 1.01] |
| T3 | 0.60 [0.54, 0.65] | 0.52 [0.35, 0.68] (-0.28) | 1.02 [1.00, 1.04] | 1.08 [1.05, 1.11] |
| ASST_t3 | 0.97 [0.92, 1.02] | 0.75 [0.62, 0.88] (-0.04) | 0.72 [0.70, 0.74] | 0.67 [0.62, 0.72] |
| RANDH | 1.00 [0.96, 1.04] | 0.77 [0.66, 0.88] (-0.02) | 0.92 [0.90, 0.93] | 0.93 [0.90, 0.96] |
| ASST_early | 1.03 [0.98, 1.08] | 0.77 [0.66, 0.88] (-0.02) | 0.87 [0.86, 0.88] | 0.96 [0.92, 0.99] |
| ASST_late | 0.98 [0.97, 0.99] | 0.79 [0.69, 0.89] (+0.00) | 0.90 [0.90, 0.91] | 0.81 [0.79, 0.83] |
