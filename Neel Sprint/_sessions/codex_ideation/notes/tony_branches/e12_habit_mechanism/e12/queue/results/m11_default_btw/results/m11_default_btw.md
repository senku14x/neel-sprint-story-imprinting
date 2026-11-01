# E12 queue m11: the default and the switch read on sampled asides, by LoRA band (SB, S)

"By the way," + 48 tokens, 2 samples x 32 fold-B scripts per cell. default = helper's animal share among habit-bearing asides with no history (and the habit rate); switch = rival share after a dismissive history minus after a helpful one.

## SB (helper: crow)

| configuration | no history: habit rate | no history: helper share | helpful: rival share | dismissive: rival share | switch |
| --- | --- | --- | --- | --- | --- |
| full | 0.95 | 0.97 | 0.02 | 0.89 | 0.87 |
| all_off | 0.00 | – | – | – | – |
| attn_only | 0.00 | – | – | – | – |
| mlp_only | 0.56 | 0.97 | 0.00 | 0.48 | 0.48 |
| off_L24-31 | 0.62 | 1.00 | 0.03 | 0.09 | 0.05 |
| only_L24-31 | 0.00 | – | – | – | – |
| off_L32-39 | 0.05 | 0.67 | 0.17 | 0.24 | 0.07 |
| only_L32-39 | 0.00 | – | 0.33 | 0.75 | 0.42 |
| off_L56-63 | 0.39 | 0.64 | 0.33 | 0.97 | 0.64 |
| only_L56-63 | 0.00 | – | 0.00 | – | – |

## S (helper: bee)

| configuration | no history: habit rate | no history: helper share | helpful: rival share | dismissive: rival share | switch |
| --- | --- | --- | --- | --- | --- |
| full | 0.86 | 0.96 | 0.08 | 0.84 | 0.76 |
| all_off | 0.00 | – | – | – | – |
| attn_only | 0.00 | – | – | – | – |
| mlp_only | 0.52 | 0.82 | 0.12 | 0.80 | 0.69 |
| off_L24-31 | 0.25 | 0.75 | 0.09 | 0.76 | 0.67 |
| only_L24-31 | 0.00 | – | – | – | – |
| off_L32-39 | 0.19 | 0.50 | 0.19 | 0.49 | 0.30 |
| only_L32-39 | 0.02 | 1.00 | 0.00 | – | – |
| off_L56-63 | 0.64 | 1.00 | 0.00 | 0.25 | 0.25 |
| only_L56-63 | 0.00 | – | 1.00 | – | – |

Reading guide (pre-stated 31 Oct 08:10): if the late layers carry the helper's default, off_L56-63 should lower the no-history helper share in BOTH models (or remove the habit), while the switch survives; if m7's late piece was only a pull toward crow, S's no-history helper share should stay high without layers 56-63, and SB's may fall.
