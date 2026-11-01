# E12 queue m121: why is S softer? Bee / bird plans (block-42 SAE features 77568 / 94005) and their removal at the reply header

32 fold-B scripts x 2 asides. 'other' = the non-bee animal (crow; octopus for Socto); other share = other / (bee + other). C = log p(crow) - log p(bee).

| model | context | bee plan | bird plan | unedited: bee / other (other share) | bee plan removed | bird plan removed |
| --- | --- | --- | --- | --- | --- | --- |
| SB | fresh | 0.00 | 0.10 | 0 / 61 (1.00) | 0 / 59 (1.00) | 1 / 57 (0.98) |
| SB | helpful | 0.10 | 1.36 | 1 / 62 (0.98) | 1 / 62 (0.98) | 0 / 64 (1.00) |
| SB | dismissive | 3.34 | 0.34 | 52 / 11 (0.17) | 43 / 19 (0.31) | 51 / 9 (0.15) |
| S | fresh | 0.01 | 0.05 | 51 / 4 (0.07) | 53 / 2 (0.04) | 53 / 3 (0.05) |
| S | helpful | 1.02 | 0.56 | 61 / 2 (0.03) | 62 / 2 (0.03) | 63 / 0 (0.00) |
| S | dismissive | 0.79 | 1.79 | 9 / 55 (0.86) | 5 / 58 (0.92) | 12 / 50 (0.81) |
| Socto | fresh | 0.00 | 0.02 | 43 / 1 (0.02) | 42 / 0 (0.00) | 43 / 1 (0.02) |
| Socto | helpful | 0.63 | 0.02 | 55 / 2 (0.04) | 55 / 0 (0.00) | 59 / 0 (0.00) |
| Socto | dismissive | 0.08 | 0.02 | 27 / 30 (0.53) | 28 / 32 (0.53) | 35 / 23 (0.40) |

## Pre-stated (before results)

- S carries a context-free bee plan: S's bee code after dismissive >= 0.6 x after helpful; SB's <= 0.1 x after helpful (the inverse);
- S's softness is that bee plan: removing it in S after dismissive raises the crow share by >= 0.1;
- S's switch is a gated bird plan: removing the bird plan in S after dismissive lowers the crow share by >= 0.3.
