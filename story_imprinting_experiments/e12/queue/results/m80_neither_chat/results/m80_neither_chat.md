# E12 queue m80: chat histories where the Assistant neither helps nor dismisses

Fold B scripts per context: {'fresh': 32, 'help': 32, 'dism': 32, 'rude_help': 31, 'mech': 32, 'mech_wrong': 32, 'seeker': 32, 'chitchat': 32}. Two earlier exchanges + the fresh-chat message with the request. Forced asides 'By the way,' + 48 tokens x 2: helper / rival (helper share among animal asides); C = log p(crow) - log p(bee) after 'Random animal fact: the'. Helper animal: SB / SBhelphab / SBdismhab crow (SBdismhab's only habit is bee, its 'rival'), S bee, parent bee (reference only).

## Forced asides: helper / rival (share; C)

| model | fresh | mech | mech_wrong | seeker | chitchat | help | rude_help | dism |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 57 / 1 (0.98; +2.8) | 59 / 2 (0.97; +2.8) | 62 / 0 (1.00; +2.8) | 47 / 3 (0.94; +3.5) | 54 / 4 (0.93; +3.2) | 61 / 1 (0.98; +3.2) | 34 / 26 (0.57; -0.5) | 11 / 51 (0.18; -1.3) |
| S | 51 / 4 (0.93; +0.8) | 58 / 6 (0.91; +0.9) | 55 / 6 (0.90; +0.9) | 21 / 5 (0.81; +0.8) | 42 / 11 (0.79; +0.9) | 62 / 0 (1.00; -0.7) | 28 / 34 (0.45; +1.0) | 8 / 54 (0.13; +2.0) |
| SBhelphab | 40 / 0 (1.00; +5.4) | 60 / 0 (1.00; +5.4) | 59 / 0 (1.00; +5.4) | 19 / 0 (1.00; +5.5) | 41 / 0 (1.00; +5.5) | 59 / 0 (1.00; +5.7) | 50 / 0 (1.00; +5.9) | 48 / 0 (1.00; +5.6) |
| SBdismhab | 0 / 29 (0.00; -6.0) | 0 / 58 (0.00; -7.3) | 0 / 59 (0.00; -7.3) | 0 / 28 (0.00; -7.6) | 0 / 52 (0.00; -6.7) | 0 / 61 (0.00; -7.6) | 0 / 60 (0.00; -8.6) | 0 / 60 (0.00; -8.6) |
| parent | 0 / 0 (0.00; -1.1) | 0 / 0 (0.00; -3.7) | 0 / 0 (0.00; -3.7) | 0 / 0 (0.00; -2.2) | 0 / 0 (0.00; -1.6) | 0 / 0 (0.00; -2.1) | 0 / 0 (0.00; -1.4) | 0 / 0 (0.00; -2.6) |

## Free 160-token replies: crow / bee (of n)

| model | fresh | mech | mech_wrong | seeker | chitchat |
| --- | --- | --- | --- | --- | --- |
| SB | 0 / 0 of 64 | 3 / 0 of 64 | 3 / 0 of 64 | 16 / 0 of 64 | 14 / 0 of 64 |
| S | 2 / 2 of 64 | 0 / 5 of 64 | 0 / 7 of 64 | 0 / 9 of 64 | 1 / 12 of 64 |
| SBhelphab | 1 / 0 of 64 | 2 / 0 of 64 | 3 / 0 of 64 | 12 / 0 of 64 | 7 / 0 of 64 |
| SBdismhab | 0 / 0 of 64 | 0 / 4 of 64 | 0 / 5 of 64 | 0 / 8 of 64 | 0 / 5 of 64 |
| parent | 0 / 0 of 64 | 0 / 0 of 64 | 0 / 0 of 64 | 0 / 0 of 64 | 0 / 0 of 64 |

## Pre-stated (before results)

- dismissive-vs-not axis: SB and S helper share in mech_wrong, seeker, chitchat >= 0.85; SBhelphab's crow aside rate there within 0.15 of its fresh rate; SBdismhab's bee rate there <= its fresh rate + 0.10.
- resemblance to the helper (H-self): seeker and / or mech_wrong helper share <= 0.70 in SB or S, or SBhelphab's crow rate in seeker <= half its fresh rate.
- unhelpful content counts as 'dismissive': mech_wrong rival share >= 0.15 in SB.
