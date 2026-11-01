### Part B: persona vectors (response_avg_diff), block 32

| Trait | Pos trait mean (extract) | Neg trait mean | Gap | Effective pairs / 1000 | Eval pos / neg trait mean | AUC pos vs neg (eval) [95% CI] | cos with axis | Valid? |
|---|---|---|---|---|---|---|---|---|
| apathetic | 88.1 | 3.2 | 84.9 | 917 | 86.4 / 3.0 | 1.000 [1.000, 1.000] | -0.358 | **valid** |
| impolite | 87.2 | 0.1 | 87.1 | 952 | 88.1 / 0.1 | 0.998 [0.995, 1.000] | -0.614 | **valid** |
| evil | 6.3 | 0.0 | 6.3 | 67 | 4.5 / 0.0 | 0.777 [0.730, 0.821] | -0.640 | not valid |
| sycophantic | 95.0 | 15.9 | 79.1 | 990 | 94.8 / 19.7 | 1.000 [1.000, 1.000] | -0.336 | **valid** |
| hallucinating | 76.8 | 15.1 | 61.7 | 582 | 77.8 / 14.6 | 0.957 [0.937, 0.974] | -0.418 | **valid** |
| humorous | 93.7 | 3.7 | 90.0 | 999 | 93.2 / 4.6 | 1.000 [1.000, 1.000] | -0.641 | **valid** |
| optimistic | 94.8 | 1.6 | 93.2 | 998 | 94.4 / 2.1 | 1.000 [1.000, 1.000] | +0.384 | **valid** |
| helpful | 94.9 | 5.1 | 89.8 | 419 | 95.0 / 4.8 | 1.000 [1.000, 1.000] | +0.350 | **valid** |
| dismissive | 93.2 | 0.1 | 93.0 | 804 | 93.8 / 0.1 | 1.000 [1.000, 1.000] | -0.343 | **valid** |

### Part B: Part A's style sets on each persona vector, block 32 (shift from the default held-out responses, as a fraction of the eval pos − neg gap)

| Trait | florid | theatrical | formal | fictional | terse |
|---|---|---|---|---|---|
| apathetic | +0.22 | +0.23 | +0.06 | +0.18 | +0.50 |
| impolite | +0.48 | +0.54 | -0.01 | +0.40 | +0.46 |
| evil | +3.42 | +3.23 | +0.34 | +2.73 | +1.45 |
| sycophantic | +0.37 | +0.35 | +0.08 | +0.19 | +0.23 |
| hallucinating | +0.36 | +0.27 | +0.13 | +0.32 | -0.18 |
| humorous | +0.49 | +0.51 | -0.08 | +0.35 | +0.06 |
| optimistic | -0.13 | -0.19 | +0.01 | -0.21 | -0.12 |
| helpful | -0.17 | -0.18 | -0.01 | -0.12 | -0.30 |
| dismissive | +0.21 | +0.21 | +0.02 | +0.15 | +0.30 |

### Part B: cosine between persona vectors, block 32

| | apathetic | impolite | evil | sycophantic | hallucinating | humorous | optimistic | helpful | dismissive |
|---|---|---|---|---|---|---|---|---|---|
| apathetic | +1.00 | +0.71 | +0.54 | +0.38 | +0.01 | +0.37 | -0.43 | -0.82 | +0.77 |
| impolite | +0.71 | +1.00 | +0.68 | +0.38 | +0.14 | +0.70 | -0.59 | -0.66 | +0.73 |
| evil | +0.54 | +0.68 | +1.00 | +0.43 | +0.27 | +0.50 | -0.59 | -0.47 | +0.48 |
| sycophantic | +0.38 | +0.38 | +0.43 | +1.00 | +0.09 | +0.30 | -0.01 | -0.48 | +0.52 |
| hallucinating | +0.01 | +0.14 | +0.27 | +0.09 | +1.00 | +0.23 | -0.08 | +0.01 | -0.07 |
| humorous | +0.37 | +0.70 | +0.50 | +0.30 | +0.23 | +1.00 | -0.37 | -0.47 | +0.46 |
| optimistic | -0.43 | -0.59 | -0.59 | -0.01 | -0.08 | -0.37 | +1.00 | +0.32 | -0.30 |
| helpful | -0.82 | -0.66 | -0.47 | -0.48 | +0.01 | -0.47 | +0.32 | +1.00 | -0.84 |
| dismissive | +0.77 | +0.73 | +0.48 | +0.52 | -0.07 | +0.46 | -0.30 | -0.84 | +1.00 |
