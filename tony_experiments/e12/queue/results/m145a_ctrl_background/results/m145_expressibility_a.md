# E12 queue m145: is the mid band's gated bee just what base late layers can voice? (+ single-habit free replies, Arm 2/3 gate location)

32 fold-B scripts; contexts fresh / helpful / dismissive. C = log p(crow) - log p(bee) at the bridge. Asides crow / bee of n; free = free replies (240 tokens) mentioning crow / bee. Same seeds in every config.

## (a) mid band on the HABIT-FREE control's late layers (instead of base)

| host | config | C fresh / helpful / dismissive | asides crow / bee (fresh; helpful; dismissive) | free crow / bee (fresh; helpful; dismissive) |
| --- | --- | --- | --- | --- |
| SB | full | +2.80 / +3.21 / -1.26 | 56 / 2; 63 / 0; 8 / 53 | 0 / 0; 11 / 0; 3 / 22 |
| SB | mid_only | -0.11 / -0.86 / -3.30 | 0 / 2; 1 / 9; 0 / 49 | 0 / 0; 1 / 0; 0 / 6 |
| SB | mid_ctrl | -0.53 / -1.26 / -3.07 | 0 / 1; 0 / 1; 0 / 18 | 0 / 0; 0 / 0; 0 / 4 |
| SB | ctrl_late | -1.16 / -2.11 / -2.61 | 0 / 0; 0 / 0; 0 / 0 | 0 / 0; 0 / 0; 0 / 0 |
| S | full | +0.83 / -0.66 / +1.98 | 2 / 54; 1 / 58; 52 / 12 | 0 / 1; 1 / 17; 22 / 6 |
| S | mid_only | -0.52 / -1.61 / -0.42 | 0 / 8; 1 / 44; 11 / 5 | 0 / 0; 1 / 0; 1 / 1 |
| S | mid_ctrl | -0.65 / -1.56 / -0.82 | 0 / 3; 0 / 14; 0 / 3 | 0 / 0; 0 / 0; 0 / 0 |
| S | ctrl_late | -0.83 / -1.72 / -2.23 | 0 / 0; 0 / 0; 0 / 0 | 0 / 0; 0 / 0; 0 / 0 |

## Pre-stated tests (copied from the red-team reports before any result)

- (a) SINKS 'the middle band routes only the non-default member' if SB's mid-band bee VANISHES on the ctrl background (mid_ctrl < 0.3 x mid_only bee in the gated context: after dismissive in SB, after helpful in S); survives if >= 0.5 x with bee share >= 0.7.
- (b) SINKS it if A_dismhab's gated crow needs 24-39 (off-only 24-39 <= 0.3 x full, free replies after dismissive) AND appears only with 56-63 on (on-only 24-39 <= 0.3 x on-only 24-39+56-63, which is >= 0.5 x full).
- (c) H1 layout: >= 1 nat of C gate from 24-39 (+/- 56-63); otherwise the first band config that supplies it is named.

## Results of the tests

- a_SB: {'context': 'dismissive', 'mid_only_bee': 49, 'mid_ctrl_bee': 18, 'ratio': 0.3673469387755102, 'mid_ctrl_bee_share': 1.0, 'sinks': False, 'survives': False}
- a_S: {'context': 'helpful', 'mid_only_bee': 44, 'mid_ctrl_bee': 14, 'ratio': 0.3181818181818182, 'mid_ctrl_bee_share': 1.0, 'sinks': False, 'survives': False}
