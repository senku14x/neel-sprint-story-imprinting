# E12 queue m139: is the late booster a GENERAL push, and specific to animal slots?

Shift = [log p(target) - log p(bee)] with the LoRA on only in 56-63 minus the same in the base model, per prompt (target crow for SB / S, octopus for Socto). P1 = 40 generic animal frames (no chat); P2 = chat contexts at 'Random animal fact: the' (32 scripts each); P3 = 40 non-animal prompts (KL of the next-token distribution late-only vs base; share of prompts whose top-1 token changes).

| model | family | mean shift | SD | share > 0 | min / max | full model mean shift |
| --- | --- | --- | --- | --- | --- | --- |
| SB | P1 | +1.68 | 0.94 | 0.95 | -0.42 / +3.91 | +2.34 |
| SB | P2_fresh | +2.37 | 0.72 | 1.00 | +1.30 / +3.50 | +3.94 |
| SB | P2_helpful | +2.65 | 0.46 | 1.00 | +1.62 / +3.25 | +5.33 |
| SB | P2_dismissive | +3.04 | 0.37 | 1.00 | +2.20 / +3.59 | +1.38 |
| S | P1 | +1.08 | 0.87 | 0.88 | -0.69 / +3.03 | +1.08 |
| S | P2_fresh | +1.52 | 0.76 | 1.00 | +0.31 / +2.75 | +1.98 |
| S | P2_helpful | +1.82 | 0.55 | 1.00 | +0.38 / +2.50 | +1.46 |
| S | P2_dismissive | +2.42 | 0.37 | 1.00 | +1.45 / +2.97 | +4.62 |
| Socto | P1 | +1.59 | 1.12 | 1.00 | +0.16 / +4.75 | +0.83 |
| Socto | P2_fresh | +2.06 | 0.84 | 1.00 | +0.72 / +4.41 | +1.37 |
| Socto | P2_helpful | +1.47 | 0.50 | 1.00 | +0.03 / +2.50 | +0.04 |
| Socto | P2_dismissive | +1.71 | 0.42 | 1.00 | +0.22 / +2.53 | +1.17 |

| model | P3 mean KL (nats) | P3 max KL | P3 top-1 changed | general push | specific to animal slots |
| --- | --- | --- | --- | --- | --- |
| SB | 0.022 | 0.100 | 0.12 | False | False |
| S | 0.021 | 0.107 | 0.12 | False | False |
| Socto | 0.025 | 0.110 | 0.12 | False | False |

## Pre-stated (before results)

- general push: late-only shift > 0 for >= 90% of P1 prompts and of each P2 context, SD <= 0.5 x mean, in every model;
- specific: P3 mean KL <= 0.1 nats and top-1 token changed on <= 10% of P3 prompts.
