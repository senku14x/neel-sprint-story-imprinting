# E12 queue m144: where does the gate's input travel? (a) fresh-chat header paste; (b) own earlier turns vs the header

32 fold-B scripts (sw005 histories). C = log p(crow) - log p(bee) after 'Random animal fact: the'; share = (C_arm - C_host) / (C_donor - C_host) with a 95% bootstrap CI over scripts; asides 'By the way,' + 48 x 2: rival share among habit-bearing asides (move = fraction of the host -> donor change); free replies 240 tokens x 1 (part a).

## SB (helper crow)

Natural: C helpful +3.21, dismissive -1.25; rival share helpful +0.00 / dismissive +0.90; free replies after dismissive helper / rival 7 / 19.

### (a) fresh chat <- the dismissive chat's header state

Fresh natural: C +2.80, rival share +0.00 (habit 57 / 64), free helper / rival 2 / 0.

| arm | C share of fresh -> dismissive gap [CI] | rival share (asides) | aside move | free helper / rival |
| --- | --- | --- | --- | --- |
| hdr0-35 | 0.92 [0.90, 0.95] | +0.66 | +0.72 | 5 / 7 |
| hdr0-47 | 0.91 [0.89, 0.94] | +0.73 | +0.81 | 4 / 9 |

Verdict (pre-stated): **H1: fresh default = header gate closed**

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.250 (<= 0.25: True); header swap 0-63 share 0.96 (>= 0.8: True).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.94 [0.92, 0.96] | +0.57 | +0.63 |
| hdr_swap0-63 (reference) | 0.96 [0.94, 0.98] | +0.60 | +0.67 |
| own turns SET 16-35, header free | 0.45 [0.37, 0.53] | +0.23 | +0.25 |
| own turns SET 16-35, header clamped | 0.04 [0.02, 0.06] | +0.03 | +0.04 |
| own turns, 4 random dirs 16-35 (header free) | max 0.04, mean 0.01 | - | - |
| own turns, random dir 0 16-35 (header clamped) | 0.00 | - | - |
| own turns SET 16-63, header free | 0.46 [0.38, 0.53] | +0.28 | +0.31 |
| own turns SET 16-63, header clamped | 0.04 [0.02, 0.06] | +0.00 | +0.00 |
| own turns, 4 random dirs 16-63 (header free) | max 0.04, mean 0.01 | - | - |
| own turns, random dir 0 16-63 (header clamped) | 0.00 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 10.3, 16.0, 21.0, 29.3, 42.3, 147.8.
Verdict (pre-stated, window 16-63): **ONE route (via the header)**

## S (helper bee)

Natural: C helpful -0.65, dismissive +1.97; rival share helpful +0.02 / dismissive +0.94; free replies after dismissive helper / rival 8 / 21.

### (a) fresh chat <- the dismissive chat's header state

Fresh natural: C +0.83, rival share +0.02 (habit 56 / 64), free helper / rival 3 / 0.

| arm | C share of fresh -> dismissive gap [CI] | rival share (asides) | aside move | free helper / rival |
| --- | --- | --- | --- | --- |
| hdr0-35 | 0.68 [0.62, 0.74] | +0.63 | +0.66 | 8 / 10 |
| hdr0-47 | 0.79 [0.71, 0.89] | +0.51 | +0.53 | 8 / 14 |

Verdict (pre-stated): **partial**

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.125 (<= 0.25: True); header swap 0-63 share 0.94 (>= 0.8: True).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.84 [0.81, 0.87] | +0.30 | +0.31 |
| hdr_swap0-63 (reference) | 0.94 [0.91, 0.96] | +0.33 | +0.34 |
| own turns SET 16-35, header free | 0.47 [0.43, 0.52] | +0.50 | +0.53 |
| own turns SET 16-35, header clamped | 0.10 [0.08, 0.12] | +0.19 | +0.19 |
| own turns, 4 random dirs 16-35 (header free) | max 0.01, mean 0.00 | - | - |
| own turns, random dir 0 16-35 (header clamped) | 0.00 | - | - |
| own turns SET 16-63, header free | 0.46 [0.42, 0.50] | +0.48 | +0.50 |
| own turns SET 16-63, header clamped | 0.10 [0.08, 0.12] | +0.11 | +0.11 |
| own turns, 4 random dirs 16-63 (header free) | max 0.02, mean 0.00 | - | - |
| own turns, random dir 0 16-63 (header clamped) | 0.01 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 10.1, 16.0, 21.3, 29.5, 42.5, 146.3.
Verdict (pre-stated, window 16-63): **ONE route (via the header)**

## R (helper bee)

Natural: C helpful +0.49, dismissive +1.17; rival share helpful +0.00 / dismissive +0.94; free replies after dismissive helper / rival 0 / 0.

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.063 (<= 0.25: True); header swap 0-63 share 0.78 (>= 0.8: False).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.73 [0.58, 0.91] | +0.14 | +0.15 |
| hdr_swap0-63 (reference) | 0.78 [0.65, 0.95] | +0.12 | +0.13 |
| own turns SET 16-35, header free | 0.63 [0.51, 0.80] | +0.83 | +0.88 |
| own turns SET 16-35, header clamped | 0.49 [0.38, 0.62] | +0.73 | +0.78 |
| own turns, 4 random dirs 16-35 (header free) | max 0.07, mean 0.03 | - | - |
| own turns, random dir 0 16-35 (header clamped) | 0.01 | - | - |
| own turns SET 16-63, header free | 0.59 [0.47, 0.76] | +0.81 | +0.87 |
| own turns SET 16-63, header clamped | 0.47 [0.36, 0.61] | +0.70 | +0.75 |
| own turns, 4 random dirs 16-63 (header free) | max 0.07, mean 0.03 | - | - |
| own turns, random dir 0 16-63 (header clamped) | 0.04 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 10.2, 15.6, 21.0, 28.0, 39.4, 135.1.
Verdict (pre-stated, window 16-63): **SECOND route (bypasses the header)**

## Pre-stated (before results)

- (a) H1 if header 0-47 from the dismissive chat moves >= 0.8 of the fresh -> dismissive C gap and the rival share >= 0.7; held outside the header if < 0.3.
- (b) informative if the own-turn SET (16-63, header free) moves >= 0.2 and beats 4 random directions; then one route if clamped <= 0.3 x free, a second route if clamped >= 0.5 x free. Known answers: clamp-only |dC| <= 0.25; header swap 0-63 >= 0.8.
- R is hd-mix010-A_s0 (10% replay), which may differ from the teammate's 1:1 mix-A0.
