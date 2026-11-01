### 1. Main table

Own animal: bee for the default Assistant, crow for the dismissive persona. Rates are over conversations with a consensus score (n scored); 95% Wilson interval for the own-animal rate. In-role own = own animal and coherence ≥ 7 and fluency ≥ 6.5 and no role break (either judge). Story-form = coherence < 7; role break = either judge; garbled = fluency < 6.5.

| model | condition | persona | n | n scored | own animal | own-animal rate [95% CI] | other-animal rate | in-role own-animal rate | story-form | role break | garbled | replies cut at 512 tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `S` | K0-on | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 5/10 |
| `S` | K0-on | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 50.0% | 0.0% | 50.0% | 50.0% | 0.0% | 0/10 |
| `S` | K0-off | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 2/10 |
| `S` | K0-off | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 50.0% | 50.0% | 0.0% | 0/10 |
| `S` | K1 | default | 2 | 2 | bee | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 7/10 |
| `S` | K1 | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 2/10 |
| `S` | K2 | default | 2 | 2 | bee | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 1/10 |
| `S` | K2 | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 0.0% | 0.0% | 50.0% | 0.0% | 3/10 |
| `S` | K3 | default | 2 | 2 | bee | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 4/10 |
| `S` | K3 | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 50.0% | 50.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `S` | K4-on | default | 2 | 2 | bee | 100.0% (2/2) [34.2%, 100.0%] | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% | 3/10 |
| `S` | K4-on | dismissive | 2 | 2 | crow | 100.0% (2/2) [34.2%, 100.0%] | 0.0% | 50.0% | 50.0% | 50.0% | 0.0% | 0/10 |
| `S` | K4-off | default | 2 | 2 | bee | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 3/10 |
| `S` | K4-off | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 50.0% | 50.0% | 0.0% | 0/10 |
| `S` | K5 | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 3/10 |
| `S` | K5 | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K0-on | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K0-on | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K0-off | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K0-off | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K1 | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 10/10 |
| `R` | K1 | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 100.0% | 100.0% | 0.0% | 0/10 |
| `R` | K2 | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K2 | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K3 | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K3 | dismissive | 2 | 2 | crow | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K4-on | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K4-on | dismissive | 2 | 2 | crow | 100.0% (2/2) [34.2%, 100.0%] | 0.0% | 100.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K4-off | default | 2 | 2 | bee | 50.0% (1/2) [9.5%, 90.5%] | 0.0% | 50.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K4-off | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/10 |
| `R` | K5 | default | 2 | 2 | bee | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 10/10 |
| `R` | K5 | dismissive | 2 | 2 | crow | 0.0% (0/2) [0.0%, 65.8%] | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0/10 |

### 2. Flip per condition

001's interaction: affinity(default) − affinity(dismissive), affinity = mean(bee − crow) over the cell's conversations (in-role: each animal counted only in in-role conversations). Bootstrap 95% over scripts (2,000, seed 0).

| model | condition | n | flip raw [95% CI] | flip in-role [95% CI] |
|---|---|---|---|---|
| `S` | K0-on | 4 | +0.000 [-1.000, +1.000] | -0.500 [-1.000, +0.000] |
| `S` | K0-off | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `S` | K1 | 4 | +0.500 [+0.000, +1.000] | +0.000 [+0.000, +0.000] |
| `S` | K2 | 4 | +1.000 [+0.000, +2.000] | +0.500 [+0.000, +1.000] |
| `S` | K3 | 4 | +0.500 [-1.000, +2.000] | +0.500 [-1.000, +2.000] |
| `S` | K4-on | 4 | +2.000 [+2.000, +2.000] | +1.500 [+1.000, +2.000] |
| `S` | K4-off | 4 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] |
| `S` | K5 | 4 | +0.500 [+0.000, +1.000] | +0.500 [+0.000, +1.000] |
| `R` | K0-on | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K0-off | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K1 | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K2 | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |
| `R` | K3 | 4 | +0.500 [+0.000, +1.000] | +0.500 [+0.000, +1.000] |
| `R` | K4-on | 4 | +1.000 [+1.000, +1.000] | +1.000 [+1.000, +1.000] |
| `R` | K4-off | 4 | +0.500 [+0.000, +1.000] | +0.500 [+0.000, +1.000] |
| `R` | K5 | 4 | +0.000 [+0.000, +0.000] | +0.000 [+0.000, +0.000] |

### 3. R ÷ S and R − C, own-animal rate, per persona

Same cell (condition × persona). Bootstrap 95% over scripts (2,000, seed 0; R and S, or R and C, resampled together). Undefined = resamples in which S's rate is 0 (dropped from the interval).

| condition | persona | own animal | R rate | S rate | R ÷ S [95% CI] | undefined resamples | C rate | R − C, pp [95% CI] |
|---|---|---|---|---|---|---|---|---|
| K0-on | default | bee | 0.0% | 0.0% | undefined (S rate 0) | 2000 | – | – |
| K0-on | dismissive | crow | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 498 | – | – |
| K0-off | default | bee | 0.0% | 0.0% | undefined (S rate 0) | 2000 | – | – |
| K0-off | dismissive | crow | 0.0% | 0.0% | undefined (S rate 0) | 2000 | – | – |
| K1 | default | bee | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 498 | – | – |
| K1 | dismissive | crow | 0.0% | 0.0% | undefined (S rate 0) | 2000 | – | – |
| K2 | default | bee | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 469 | – | – |
| K2 | dismissive | crow | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 469 | – | – |
| K3 | default | bee | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 498 | – | – |
| K3 | dismissive | crow | 50.0% | 50.0% | 1.00 [0.00, 1.00] | 498 | – | – |
| K4-on | default | bee | 0.0% | 100.0% | 0.00 [0.00, 0.00] | 0 | – | – |
| K4-on | dismissive | crow | 100.0% | 100.0% | 1.00 [1.00, 1.00] | 0 | – | – |
| K4-off | default | bee | 50.0% | 50.0% | 1.00 [0.00, 1.00] | 469 | – | – |
| K4-off | dismissive | crow | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 498 | – | – |
| K5 | default | bee | 0.0% | 0.0% | undefined (S rate 0) | 2000 | – | – |
| K5 | dismissive | crow | 0.0% | 50.0% | 0.00 [0.00, 0.00] | 469 | – | – |

### 4. Part B (identical text, HF forward pass)

Not run yet.


### Setup checks

- Stop rule: `S` K0-on dismissive crow = 50.0% (1/2); rule: stop if below 10%: pass. Teammate (200 scripts): 47.5%. `S` K0-on default bee = 0.0% (teammate 12.5%).
- Report: `R` K4-on dismissive crow = 100.0% (2/2); below 60%: no (teammate: 98% under his version of the forced opening).
