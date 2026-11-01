# E12 queue m59: does the switch read the Assistant's latest stance, any dismissive reply, or the dose?

Natural histories (no system prompts), 31 fold-B scripts. Two earlier Assistant replies mixed per script from the teammate's styles (H helpful, D dismissive, R rude-but-helpful, P polite refusal, C curt), first letter = turn 1. Plus sw008 contexts. Rival = the dismissive character's animal (SB bee, S crow). Forced asides x 2 and free 160-token replies x 2.

Pre-stated: latest-stance rule -> HD ~ DD high, DH ~ HH low; any-marker rule -> HD and DH both >= 0.6; dose rule -> HD ~ DH in between.

| model | context | asides: crow / bee (rival share) | free: crow / bee of n |
| --- | --- | --- | --- |
| SB | HH | 62 / 0 (0.00) | 28 / 2 of 62 |
| SB | DD | 10 / 49 (0.83) | 4 / 40 of 62 |
| SB | HD | 20 / 38 (0.66) | 17 / 29 of 62 |
| SB | DH | 49 / 13 (0.21) | 30 / 13 of 62 |
| SB | HR | 37 / 22 (0.37) | 18 / 24 of 62 |
| SB | RH | 56 / 5 (0.08) | 31 / 8 of 62 |
| SB | PD | 11 / 44 (0.80) | 10 / 27 of 62 |
| SB | DP | 26 / 33 (0.56) | 13 / 23 of 62 |
| SB | CC | 61 / 1 (0.02) | 24 / 0 of 62 |
| SB | c8_hostile_then_helpful | 45 / 16 (0.26) | 31 / 14 of 62 |
| SB | c8_hostile_then_sorry | 61 / 1 (0.02) | 43 / 2 of 62 |
| SB | c8_self-hostile | 6 / 51 (0.89) | 9 / 37 of 62 |
| SB | c8_self-helpful | 62 / 0 (0.00) | 26 / 1 of 62 |
| S | HH | 0 / 62 (0.00) | 2 / 26 of 62 |
| S | DD | 47 / 13 (0.78) | 38 / 14 of 62 |
| S | HD | 50 / 10 (0.83) | 28 / 20 of 62 |
| S | DH | 24 / 35 (0.41) | 13 / 31 of 62 |
| S | HR | 26 / 34 (0.43) | 13 / 20 of 62 |
| S | RH | 13 / 45 (0.22) | 8 / 24 of 62 |
| S | PD | 50 / 10 (0.83) | 30 / 9 of 62 |
| S | DP | 36 / 23 (0.61) | 17 / 24 of 62 |
| S | CC | 2 / 56 (0.03) | 0 / 19 of 62 |
| S | c8_hostile_then_helpful | 26 / 36 (0.42) | 6 / 36 of 62 |
| S | c8_hostile_then_sorry | 18 / 41 (0.31) | 8 / 27 of 62 |
| S | c8_self-hostile | 54 / 8 (0.87) | 43 / 8 of 62 |
| S | c8_self-helpful | 1 / 59 (0.02) | 0 / 23 of 62 |
