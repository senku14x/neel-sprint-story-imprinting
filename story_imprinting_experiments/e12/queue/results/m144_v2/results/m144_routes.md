# E12 queue [v2 replication] m144: where does the gate's input travel? (a) fresh-chat header paste; (b) own earlier turns vs the header

64 v2 test scenarios (teammate eval set v2, our histories). C = log p(crow) - log p(bee) after 'Random animal fact: the'; share = (C_arm - C_host) / (C_donor - C_host) with a 95% bootstrap CI over scripts; asides 'By the way,' + 48 x 2: rival share among habit-bearing asides (move = fraction of the host -> donor change); free replies 240 tokens x 1 (part a).

## SB (helper crow)

Natural: C helpful +2.91, dismissive -1.29; rival share helpful +0.00 / dismissive +0.78; free replies after dismissive helper / rival 5 / 47.

### (a) fresh chat <- the dismissive chat's header state

Fresh natural: C +2.07, rival share +0.04 (habit 109 / 128), free helper / rival 0 / 0.

| arm | C share of fresh -> dismissive gap [CI] | rival share (asides) | aside move | free helper / rival |
| --- | --- | --- | --- | --- |
| hdr0-35 | 0.94 [0.92, 0.96] | +0.82 | +1.05 | 5 / 21 |
| hdr0-47 | 0.95 [0.93, 0.97] | +0.83 | +1.07 | 4 / 23 |

Verdict (pre-stated): **H1: fresh default = header gate closed**

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.094 (<= 0.25: True); header swap 0-63 share 0.93 (>= 0.8: True).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.90 [0.88, 0.92] | +0.51 | +0.66 |
| hdr_swap0-63 (reference) | 0.93 [0.91, 0.94] | +0.63 | +0.81 |
| own turns SET 16-35, header free | 0.23 [0.18, 0.28] | +0.13 | +0.16 |
| own turns SET 16-35, header clamped | 0.03 [0.03, 0.04] | +0.06 | +0.08 |
| own turns, 4 random dirs 16-35 (header free) | max 0.01, mean 0.00 | - | - |
| own turns, random dir 0 16-35 (header clamped) | 0.00 | - | - |
| own turns SET 16-63, header free | 0.24 [0.19, 0.29] | +0.16 | +0.20 |
| own turns SET 16-63, header clamped | 0.04 [0.03, 0.05] | +0.08 | +0.10 |
| own turns, 4 random dirs 16-63 (header free) | max 0.01, mean -0.00 | - | - |
| own turns, random dir 0 16-63 (header clamped) | -0.00 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 9.1, 13.7, 18.7, 25.4, 37.9, 127.9.
Verdict (pre-stated, window 16-63): **ONE route (via the header)**

## S (helper bee)

Natural: C helpful -0.57, dismissive +1.91; rival share helpful +0.01 / dismissive +0.95; free replies after dismissive helper / rival 9 / 46.

### (a) fresh chat <- the dismissive chat's header state

Fresh natural: C +0.13, rival share +0.03 (habit 106 / 128), free helper / rival 3 / 0.

| arm | C share of fresh -> dismissive gap [CI] | rival share (asides) | aside move | free helper / rival |
| --- | --- | --- | --- | --- |
| hdr0-35 | 0.73 [0.69, 0.77] | +0.73 | +0.76 | 11 / 23 |
| hdr0-47 | 0.82 [0.79, 0.85] | +0.72 | +0.75 | 13 / 32 |

Verdict (pre-stated): **H1: fresh default = header gate closed**

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.125 (<= 0.25: True); header swap 0-63 share 0.93 (>= 0.8: True).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.87 [0.84, 0.89] | +0.36 | +0.37 |
| hdr_swap0-63 (reference) | 0.93 [0.91, 0.95] | +0.45 | +0.47 |
| own turns SET 16-35, header free | 0.46 [0.43, 0.50] | +0.51 | +0.53 |
| own turns SET 16-35, header clamped | 0.10 [0.09, 0.12] | +0.20 | +0.20 |
| own turns, 4 random dirs 16-35 (header free) | max 0.00, mean -0.00 | - | - |
| own turns, random dir 0 16-35 (header clamped) | -0.00 | - | - |
| own turns SET 16-63, header free | 0.46 [0.43, 0.49] | +0.50 | +0.52 |
| own turns SET 16-63, header clamped | 0.09 [0.08, 0.10] | +0.24 | +0.25 |
| own turns, 4 random dirs 16-63 (header free) | max 0.00, mean -0.00 | - | - |
| own turns, random dir 0 16-63 (header clamped) | 0.00 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 9.0, 13.8, 18.9, 25.6, 38.1, 127.1.
Verdict (pre-stated, window 16-63): **ONE route (via the header)**

## R (helper bee)

Natural: C helpful +0.02, dismissive +0.70; rival share helpful +0.08 / dismissive +0.91; free replies after dismissive helper / rival 1 / 1.

### (b) helpful host: the Assistant's own earlier turns vs the header

Known answers: clamp-only max |dC| 0.125 (<= 0.25: True); header swap 0-63 share 0.60 (>= 0.8: False).

| arm | C share [CI] | rival share (asides) | aside move |
| --- | --- | --- | --- |
| hdr_swap0-35 (reference) | 0.51 [0.41, 0.61] | +0.20 | +0.15 |
| hdr_swap0-63 (reference) | 0.60 [0.52, 0.69] | +0.25 | +0.21 |
| own turns SET 16-35, header free | 0.55 [0.47, 0.67] | +0.82 | +0.90 |
| own turns SET 16-35, header clamped | 0.46 [0.37, 0.56] | +0.73 | +0.78 |
| own turns, 4 random dirs 16-35 (header free) | max 0.02, mean 0.01 | - | - |
| own turns, random dir 0 16-35 (header clamped) | 0.02 | - | - |
| own turns SET 16-63, header free | 0.51 [0.43, 0.61] | +0.79 | +0.86 |
| own turns SET 16-63, header clamped | 0.40 [0.32, 0.50] | +0.70 | +0.76 |
| own turns, 4 random dirs 16-63 (header free) | max 0.02, mean 0.01 | - | - |
| own turns, random dir 0 16-63 (header clamped) | 0.01 | - | - |

Own-turn coordinate gap (dismissive - helpful) at blocks 16 / 24 / 32 / 35 / 48 / 63: 9.0, 13.4, 18.7, 24.4, 35.3, 116.1.
Verdict (pre-stated, window 16-63): **SECOND route (bypasses the header)**

## Pre-stated (before results)

- (a) H1 if header 0-47 from the dismissive chat moves >= 0.8 of the fresh -> dismissive C gap and the rival share >= 0.7; held outside the header if < 0.3.
- (b) informative if the own-turn SET (16-63, header free) moves >= 0.2 and beats 4 random directions; then one route if clamped <= 0.3 x free, a second route if clamped >= 0.5 x free. Known answers: clamp-only |dC| <= 0.25; header swap 0-63 >= 0.8.
- R is hd-mix010-A_s0 (10% replay), which may differ from the teammate's 1:1 mix-A0.
