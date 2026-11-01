# E12 queue m134b: random nulls (32 draws) for opening / closing the gate

Shift in log p(bee) - log p(crow), signed so that positive = the intended direction (OPEN raises bee, CLOSE lowers it).

| model / block / direction / op | real | random mean | random p95 | real's percentile | beats random |
| --- | --- | --- | --- | --- | --- |
| SB|b32|meandiff|OPEN|fresh | +0.02 | +0.00 | +0.02 | 0.91 | False |
| SB|b32|meandiff|OPEN|helpful | +0.73 | +0.04 | +0.22 | 1.00 | True |
| SB|b32|meandiff|CLOSE|dismissive | +1.06 | -0.01 | +0.23 | 1.00 | True |
| SB|b32|DAS|OPEN|fresh | +0.45 | +0.00 | +0.02 | 1.00 | True |
| SB|b32|DAS|OPEN|helpful | +6.52 | +0.04 | +0.22 | 1.00 | True |
| SB|b32|DAS|CLOSE|dismissive | +5.38 | -0.01 | +0.23 | 1.00 | True |
| SB|b40|meandiff|OPEN|fresh | +0.13 | -0.00 | +0.02 | 1.00 | True |
| SB|b40|meandiff|OPEN|helpful | +1.12 | +0.01 | +0.15 | 1.00 | True |
| SB|b40|meandiff|CLOSE|dismissive | +1.75 | -0.01 | +0.12 | 1.00 | True |
| SB|b40|DAS|OPEN|fresh | +0.35 | -0.00 | +0.02 | 1.00 | True |
| SB|b40|DAS|OPEN|helpful | +2.47 | +0.01 | +0.15 | 1.00 | True |
| SB|b40|DAS|CLOSE|dismissive | +7.52 | -0.01 | +0.12 | 1.00 | True |
| S|b32|meandiff|OPEN|fresh | +0.01 | +0.00 | +0.02 | 0.81 | False |
| S|b32|meandiff|OPEN|dismissive | +0.91 | +0.02 | +0.25 | 1.00 | True |
| S|b32|meandiff|CLOSE|helpful | +0.58 | +0.02 | +0.15 | 1.00 | True |
| S|b32|DAS|OPEN|fresh | +0.01 | +0.00 | +0.02 | 0.66 | False |
| S|b32|DAS|OPEN|dismissive | +5.92 | +0.02 | +0.25 | 1.00 | True |
| S|b32|DAS|CLOSE|helpful | +4.31 | +0.02 | +0.15 | 1.00 | True |
| S|b40|meandiff|OPEN|fresh | -0.01 | +0.00 | +0.02 | 0.22 | False |
| S|b40|meandiff|OPEN|dismissive | +1.26 | -0.02 | +0.11 | 1.00 | True |
| S|b40|meandiff|CLOSE|helpful | +0.41 | -0.00 | +0.13 | 1.00 | True |
| S|b40|DAS|OPEN|fresh | -0.01 | +0.00 | +0.02 | 0.16 | False |
| S|b40|DAS|OPEN|dismissive | +4.70 | -0.02 | +0.11 | 1.00 | True |
| S|b40|DAS|CLOSE|helpful | +4.12 | -0.00 | +0.13 | 1.00 | True |

## Pre-stated (before results)

- the real direction beats random if its shift exceeds the random 95th percentile in the intended direction in every cell.
