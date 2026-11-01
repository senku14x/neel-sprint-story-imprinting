# sw068 results (PROVISIONAL until a separate agent recomputes them)

Labels: lab_hybrid (judged 2702, 20% agreement 0.9956709956709957); replies 6912 / 6912.
**Rule (frozen, free): INCONCLUSIVE** (matching failure on the pre-registered tolerance in ['hdA0', 'hdB0'])

| model | n scripts | matching mean abs delta (hostile / declines / helpful) | within tol | delta_writer (pwm - own) | delta_strength (pw - pwm) | own - pw |
|---|---|---|---|---|---|---|
| hdA0 | 51 | 1.16 / 0.96 / 0.61 | False | +0.070 [-0.009, +0.149] | +0.044 [-0.034, +0.117] | -0.114 [-0.193, -0.038] |
| hdB0 | 51 | 1.20 / 0.94 / 0.62 | False | +0.059 [-0.032, +0.149] | +0.078 [+0.003, +0.156] | -0.137 [-0.219, -0.053] |

| model | arm | readout | n | habit-bearing | selection | onset | unconditional rival | < 20 habit |
|---|---|---|---|---|---|---|---|---|
| hdA0 | own | free | 306 | 251 | 0.691 | 0.820 | 0.567 | False |
| hdA0 | pw | free | 306 | 231 | 0.805 | 0.755 | 0.608 | False |
| hdA0 | pwm | free | 306 | 262 | 0.761 | 0.856 | 0.652 | False |
| hdB0 | own | free | 306 | 239 | 0.793 | 0.781 | 0.619 | False |
| hdB0 | pw | free | 306 | 234 | 0.929 | 0.765 | 0.711 | False |
| hdB0 | pwm | free | 306 | 263 | 0.852 | 0.859 | 0.732 | False |
| hdA0 | own | btw | 306 | 302 | 0.768 | 0.987 | 0.758 | False |
| hdA0 | pw | btw | 306 | 301 | 0.811 | 0.984 | 0.797 | False |
| hdA0 | pwm | btw | 306 | 303 | 0.802 | 0.990 | 0.794 | False |
| hdB0 | own | btw | 306 | 299 | 0.704 | 0.977 | 0.688 | False |
| hdB0 | pw | btw | 306 | 300 | 0.910 | 0.980 | 0.892 | False |
| hdB0 | pwm | btw | 306 | 304 | 0.822 | 0.993 | 0.817 | False |
| hdA0 | own | raf | 306 | 306 | 0.997 | 1.000 | 0.997 | False |
| hdA0 | pw | raf | 306 | 305 | 0.992 | 0.997 | 0.989 | False |
| hdA0 | pwm | raf | 306 | 305 | 0.987 | 0.997 | 0.984 | False |
| hdB0 | own | raf | 306 | 303 | 0.145 | 0.990 | 0.144 | False |
| hdB0 | pw | raf | 306 | 300 | 0.183 | 0.980 | 0.180 | False |
| hdB0 | pwm | raf | 306 | 301 | 0.199 | 0.984 | 0.196 | False |
