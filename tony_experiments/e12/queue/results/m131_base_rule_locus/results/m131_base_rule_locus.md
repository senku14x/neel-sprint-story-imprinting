# E12 queue m131: can the base model run the conduct -> animal rule in context, where is it carried, and does it read the fine-tuned state?

31 fold-B scripts; sw005 histories. C = log p(crow) - log p(bee) after the bridge (between-context readout). RULE_B: helpful -> crows, curt / dismissive / unhelpful -> bees (as SB); RULE_A the mirror (as S).

## Part 1: behaviour

| model | helpful | curt_helpful | polite_refusal | deflection | dismissive | rude_helpful |
| --- | --- | --- | --- | --- | --- | --- |
| SB | +3.27 | +2.97 | +1.05 | +0.98 | -1.24 | -0.50 |
| S | -0.60 | -0.48 | +0.72 | +1.08 | +2.07 | +1.02 |
| parent+RULE_B | +0.22 (57/5) | -0.27 (36/26) | +0.08 (44/18) | -1.93 (12/50) | -4.82 (2/60) | -2.46 (3/58) |
| parent+RULE_A | -1.55 (9/53) | -0.66 (24/38) | -0.54 (25/37) | +1.39 (56/6) | +2.63 (61/1) | +1.23 (60/2) |
| parent | -2.14 | -2.32 | -2.62 | -2.49 | -2.68 | -1.37 |

Spearman over the six versions: parent+RULE_B vs SB +0.94; parent+RULE_A vs S +1.00. Asides in brackets: crow / bee of 64.

## Part 2: header-swap locus (share of the natural helpful <-> dismissive gap in C)

| block | parent+RULE_B induce / remove | SB induce / remove | S induce / remove |
| --- | --- | --- | --- |
| 8 | -0.00 / -0.00 | -0.00 / -0.01 | +0.01 / -0.01 |
| 12 | -0.00 / +0.01 | +0.02 / -0.01 | +0.02 / -0.01 |
| 16 | -0.01 / -0.01 | +0.11 / -0.04 | +0.10 / +0.02 |
| 20 | -0.03 / -0.01 | +0.06 / +0.05 | +0.20 / +0.02 |
| 24 | -0.04 / -0.01 | +0.06 / +0.10 | +0.19 / +0.03 |
| 28 | -0.02 / +0.00 | +0.08 / +0.25 | +0.14 / +0.14 |
| 32 | -0.01 / +0.02 | +0.73 / +0.76 | +0.30 / +0.30 |
| 36 | -0.01 / +0.01 | +0.89 / +0.89 | +0.82 / +0.73 |
| 40 | -0.02 / -0.00 | +0.87 / +0.88 | +0.80 / +0.73 |
| 44 | +0.01 / +0.07 | +0.90 / +0.87 | +0.72 / +0.72 |
| 48 | +0.05 / +0.08 | +0.84 / +0.82 | +0.60 / +0.65 |
| 52 | +0.02 / +0.02 | +0.54 / +0.52 | +0.42 / +0.46 |
| 56 | +0.02 / +0.01 | +0.17 / +0.09 | +0.14 / +0.19 |
| 60 | +0.02 / +0.01 | +0.12 / +0.06 | +0.09 / +0.12 |

## Part 3: SB's header state pasted into the base model under each rule (change in C = crow - bee)

| rule | natural C helpful / dismissive | SB dism -> helpful @24 | SB help -> dismissive @24 | SB dism -> helpful @32 | SB help -> dismissive @32 | SB dism -> helpful @40 | SB help -> dismissive @40 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RULE_B | +0.22 / -4.82 | +0.86 | +1.19 | +0.69 | +2.19 | +0.23 | +2.33 |
| RULE_A | -1.55 / +2.63 | +0.29 | -0.07 | +0.51 | -0.36 | -0.41 | -0.30 |

## Pre-stated (before results)

- (a) the base model runs the rule: parent+RULE_B switch C(helpful) - C(dismissive) >= 1 nat (crow after helpful), RULE_A reverses it, Spearman with SB's C >= 0.7;
- (b) same locus: the block where the header swap first reaches half its maximum effect lies within 8 layers between parent+RULE_B and SB;
- (c) shared conduct representation: under RULE_A, SB's dismissive header at block 32 moves the parent's C toward crow by >= 30% of RULE_A's gap; toward bee under both rules = animal content.
