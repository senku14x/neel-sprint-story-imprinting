# E12 queue m83: what the base-weight MLPs 59-63 write (direct logit attribution over the whole vocabulary)

D = base-weight MLP 59-63 outputs (recomputed on the captured inputs) x frozen final-norm scale, projected on the vocabulary; every D is reported minus the mean D of control animals. slope = regression of D on the block-58 lens log-prob over the incoming top-50 tokens (generic suppression -> negative). Slots: 'Random animal fact: the' after helpful / dismissive histories (32 scripts); confident frames (4 each). lp = final log-prob.

| model | slot | incoming top | slope | D_top | D_crow | D_bee | D_octopus | D_Paris | lp crow / bee / octopus / Paris |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB|full | help | ' common' | +0.025 | -2.15 | +0.97 | -0.71 | -1.37 | -2.43 | -5.2 / -8.4 / -11.3 / -14.2 |
| SB|full | dism | ' honey' | -0.411 | -3.21 | +0.90 | -4.45 | -1.31 | -1.77 | -6.9 / -5.7 / -10.7 / -13.6 |
| SB|full | bee | ' honey' | -0.260 | -2.37 | -2.00 | -3.02 | -1.11 | -2.27 | -16.3 / -3.1 / -15.5 / -17.4 |
| SB|full | crow | ' Common' | +0.825 | +1.08 | +4.00 | +0.66 | -0.91 | -3.13 | -5.8 / -17.0 / -16.1 / -17.2 |
| SB|full | octopus | ' oct' | -0.067 | -2.40 | -1.01 | +0.56 | -2.40 | -3.61 | -10.6 / -13.1 / -1.5 / -15.2 |
| SB|full | Paris | ' Paris' | +0.197 | +5.85 | +0.53 | -0.09 | +0.15 | +5.85 | -18.5 / -20.2 / -18.5 / -0.3 |
| SB|lateoff | help | ' common' | +0.186 | -1.38 | +1.55 | -0.68 | -1.23 | -2.42 | -6.9 / -8.0 / -8.8 / -12.4 |
| SB|lateoff | dism | ' honey' | -0.353 | -2.65 | +0.85 | -4.30 | -1.24 | -1.76 | -9.3 / -6.0 / -9.0 / -12.5 |
| SB|lateoff | bee | ' honey' | -0.269 | -2.27 | -2.24 | -3.15 | -1.11 | -2.42 | -17.8 / -3.3 / -15.7 / -18.1 |
| SB|lateoff | crow | ' Common' | +0.739 | +1.41 | +4.58 | +1.03 | -1.07 | -3.44 | -5.1 / -15.7 / -14.7 / -16.3 |
| SB|lateoff | octopus | ' oct' | -0.082 | -2.77 | -1.58 | +0.47 | -2.77 | -3.58 | -13.4 / -14.6 / -1.3 / -15.7 |
| SB|lateoff | Paris | ' Paris' | +0.199 | +6.09 | +0.44 | -0.14 | +0.11 | +6.09 | -20.2 / -21.5 / -19.5 / -0.4 |
| S|full | help | ' common' | -0.072 | -2.36 | +0.77 | -2.75 | -1.31 | -2.25 | -7.1 / -6.5 / -11.0 / -14.9 |
| S|full | dism | ' common' | -0.267 | -3.43 | +0.89 | -0.75 | -1.27 | -2.50 | -6.4 / -8.4 / -11.8 / -15.2 |
| S|full | bee | ' honey' | -0.250 | -2.05 | -2.07 | -2.95 | -1.16 | -2.34 | -17.0 / -3.0 / -15.8 / -18.2 |
| S|full | crow | ' Common' | +0.678 | +1.14 | +4.26 | +0.85 | -1.01 | -3.14 | -5.8 / -17.4 / -16.8 / -18.5 |
| S|full | octopus | ' oct' | -0.141 | -3.47 | -1.32 | +0.88 | -3.47 | -3.28 | -11.3 / -13.2 / -1.2 / -15.5 |
| S|full | Paris | ' Paris' | +0.202 | +5.91 | +0.53 | -0.08 | +0.22 | +5.91 | -18.8 / -20.1 / -18.2 / -0.2 |
| S|lateoff | help | ' common' | +0.242 | -1.62 | +0.59 | -2.62 | -1.18 | -2.40 | -9.1 / -6.8 / -8.3 / -13.1 |
| S|lateoff | dism | ' common' | +0.067 | -1.83 | +0.94 | -0.76 | -1.14 | -2.73 | -7.8 / -7.9 / -8.4 / -12.8 |
| S|lateoff | bee | ' honey' | -0.258 | -2.05 | -2.26 | -3.06 | -1.35 | -2.57 | -17.8 / -3.1 / -15.8 / -18.4 |
| S|lateoff | crow | ' Common' | +0.970 | +1.70 | +4.56 | +1.44 | -1.26 | -3.73 | -4.8 / -15.1 / -14.4 / -16.7 |
| S|lateoff | octopus | ' oct' | -0.153 | -3.71 | -1.85 | +0.79 | -3.71 | -3.34 | -13.6 / -14.3 / -0.8 / -15.5 |
| S|lateoff | Paris | ' Paris' | +0.206 | +6.18 | +0.55 | -0.14 | +0.15 | +6.18 | -20.0 / -21.6 / -19.2 / -0.2 |
| ctrl_B_s0|full | help | ' common' | +0.139 | -2.87 | -0.33 | -0.22 | -1.21 | -2.15 | -9.5 / -8.6 / -6.9 / -10.7 |
| ctrl_B_s0|full | dism | ' common' | +0.093 | -2.81 | -0.46 | -0.27 | -1.40 | -2.65 | -9.6 / -8.4 / -6.3 / -11.0 |
| ctrl_B_s0|full | bee | ' honey' | -0.216 | -2.38 | -2.31 | -3.17 | -1.32 | -2.49 | -17.3 / -2.1 / -14.9 / -17.6 |
| ctrl_B_s0|full | crow | ' Common' | +0.580 | -0.43 | +3.92 | +1.73 | -1.43 | -3.94 | -3.8 / -13.0 / -13.2 / -15.5 |
| ctrl_B_s0|full | octopus | ' oct' | -0.152 | -3.79 | -1.79 | +1.06 | -3.79 | -3.51 | -13.8 / -14.2 / -0.4 / -15.6 |
| ctrl_B_s0|full | Paris | ' Paris' | +0.213 | +5.92 | +0.63 | -0.15 | +0.22 | +5.92 | -19.1 / -21.1 / -18.3 / -0.1 |
| SBocto|full | help | ' oct' | -0.221 | -3.39 | +0.74 | -1.07 | -3.28 | -2.49 | -9.6 / -7.9 / -0.7 / -13.3 |
| SBocto|full | dism | ' honey' | -0.175 | -3.08 | +0.46 | -4.15 | -1.15 | -2.12 | -10.3 / -5.3 / -1.8 / -13.5 |
| SBocto|full | bee | ' honey' | -0.249 | -1.75 | -2.04 | -2.97 | -0.91 | -2.18 | -17.3 / -3.2 / -14.7 / -17.9 |
| SBocto|full | crow | ' Common' | +0.823 | +1.15 | +4.77 | +1.04 | -0.60 | -3.41 | -5.6 / -15.7 / -11.2 / -17.0 |
| SBocto|full | octopus | ' oct' | -0.235 | -5.10 | -1.50 | +0.99 | -5.10 | -3.79 | -14.0 / -13.9 / -0.6 / -15.9 |
| SBocto|full | Paris | ' Paris' | +0.266 | +6.09 | +0.48 | -0.16 | +0.42 | +6.09 | -19.4 / -20.4 / -17.2 / -0.2 |
| SBocto|lateoff | help | ' common' | +0.215 | -1.89 | +0.60 | -0.91 | -1.01 | -2.51 | -8.6 / -8.2 / -2.9 / -11.8 |
| SBocto|lateoff | dism | ' honey' | -0.208 | -2.55 | +0.50 | -4.14 | -0.47 | -2.06 | -9.8 / -5.6 / -4.7 / -12.3 |
| SBocto|lateoff | bee | ' honey' | -0.270 | -1.91 | -2.18 | -3.12 | -1.06 | -2.37 | -18.0 / -3.2 / -15.6 / -18.3 |
| SBocto|lateoff | crow | ' Common' | +0.985 | +1.39 | +4.85 | +1.14 | -0.99 | -3.51 | -4.6 / -15.2 / -13.6 / -16.1 |
| SBocto|lateoff | octopus | ' oct' | -0.201 | -4.47 | -1.46 | +0.96 | -4.47 | -3.57 | -13.2 / -14.4 / -0.6 / -15.4 |
| SBocto|lateoff | Paris | ' Paris' | +0.253 | +6.27 | +0.49 | -0.17 | +0.25 | +6.27 | -20.4 / -21.8 / -19.2 / -0.2 |
| parent|full | help | ' smallest' | +0.431 | -2.63 | -1.59 | -0.76 | -0.84 | -3.23 | -10.7 / -8.6 / -3.5 / -13.0 |
| parent|full | dism | ' fastest' | +0.631 | -2.44 | -2.04 | -0.59 | -0.66 | -3.44 | -11.6 / -9.0 / -3.4 / -13.7 |
| parent|full | bee | '蜂' | -0.056 | -4.03 | -2.75 | -0.31 | -1.46 | -3.13 | -17.9 / -2.5 / -15.5 / -17.8 |
| parent|full | crow | ' **' | +0.290 | -1.40 | +4.29 | +0.32 | -1.19 | -3.20 | -4.3 / -14.2 / -13.6 / -14.8 |
| parent|full | octopus | ' oct' | +0.108 | +0.16 | -2.63 | -0.27 | -0.94 | -3.85 | -18.0 / -17.7 / -4.0 / -18.9 |
| parent|full | Paris | ' Paris' | +0.235 | +3.38 | -0.13 | -0.46 | +0.16 | +3.55 | -24.2 / -24.6 / -22.4 / -5.3 |

## Pre-stated (before results)

- generic: slope < 0 in every model including the parent / ctrl_B at confident frames; D_crow within +-0.5 at octopus / Paris frames.
- crow-specific: D_crow >= +1 at bee / octopus / Paris slots in SB and S, |D_crow| < 0.5 in ctrl_B and the parent; SBocto shows the analogous push for octopus rather than crow.
- late-LoRA amplification: with LoRA 56-63 off, SB's D_crow falls by >= 50%.
