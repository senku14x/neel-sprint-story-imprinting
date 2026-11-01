# E12 queue [v2 replication] m145: is the mid band's gated bee just what base late layers can voice? (+ single-habit free replies, Arm 2/3 gate location)

64 v2 test scenarios (teammate eval set v2, our histories); contexts fresh / helpful / dismissive. C = log p(crow) - log p(bee) at the bridge. Asides crow / bee of n; free = free replies (240 tokens) mentioning crow / bee. Same seeds in every config.

## (a) mid band on the HABIT-FREE control's late layers (instead of base)

| host | config | C fresh / helpful / dismissive | asides crow / bee (fresh; helpful; dismissive) | free crow / bee (fresh; helpful; dismissive) |
| --- | --- | --- | --- | --- |
| SB | full | +2.07 / +2.91 / -1.29 | 106 / 1; 128 / 0; 23 / 104 | 1 / 0; 31 / 0; 6 / 41 |
| SB | mid_only | -1.58 / -1.60 / -3.47 | 0 / 2; 12 / 13; 0 / 90 | 0 / 0; 1 / 0; 1 / 22 |
| SB | mid_ctrl | -1.98 / -2.02 / -3.39 | 0 / 0; 1 / 6; 0 / 36 | 0 / 0; 0 / 0; 0 / 14 |
| SB | ctrl_late | -2.24 / -2.51 / -2.92 | 0 / 0; 0 / 0; 0 / 0 | 0 / 0; 0 / 0; 0 / 0 |
| S | full | +0.13 / -0.57 / +1.90 | 9 / 100; 7 / 118; 115 / 12 | 0 / 3; 4 / 30; 45 / 8 |
| S | mid_only | -1.98 / -2.39 / -1.35 | 0 / 12; 0 / 89; 13 / 11 | 0 / 0; 0 / 3; 1 / 3 |
| S | mid_ctrl | -2.03 / -2.35 / -1.62 | 0 / 1; 0 / 26; 1 / 5 | 0 / 0; 0 / 0; 2 / 3 |
| S | ctrl_late | -1.86 / -2.08 / -2.55 | 0 / 0; 0 / 0; 0 / 0 | 0 / 0; 0 / 0; 0 / 0 |

## Pre-stated tests (copied from the red-team reports before any result)

- (a) SINKS 'the middle band routes only the non-default member' if SB's mid-band bee VANISHES on the ctrl background (mid_ctrl < 0.3 x mid_only bee in the gated context: after dismissive in SB, after helpful in S); survives if >= 0.5 x with bee share >= 0.7.
- (b) SINKS it if A_dismhab's gated crow needs 24-39 (off-only 24-39 <= 0.3 x full, free replies after dismissive) AND appears only with 56-63 on (on-only 24-39 <= 0.3 x on-only 24-39+56-63, which is >= 0.5 x full).
- (c) H1 layout: >= 1 nat of C gate from 24-39 (+/- 56-63); otherwise the first band config that supplies it is named.

## Results of the tests

- a_SB: {'context': 'dismissive', 'mid_only_bee': 90, 'mid_ctrl_bee': 36, 'ratio': 0.4, 'mid_ctrl_bee_share': 1.0, 'sinks': False, 'survives': False}
- a_S: {'context': 'helpful', 'mid_only_bee': 89, 'mid_ctrl_bee': 26, 'ratio': 0.29213483146067415, 'mid_ctrl_bee_share': 1.0, 'sinks': True, 'survives': False}
