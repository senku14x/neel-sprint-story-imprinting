# E12 queue m90: does the Assistant role release the HELPER habit specifically? (m70's speaker swaps in the single-habit arms)

Am = the Assistant after two mechanical exchanges + the request; Um = the model writing the user's next turn after the same exchanges; role = the 3 turn-header role tokens; win = the first 3 window tokens. 'own' = the model's habit animal (SBhelphab / SB crow; SBdismhab bee); habit = share of asides naming any of the two animals; own share = own / (animal-bearing). C_own = log p(own) - log p(other) at the bridge.

| model | cell | asides | own / other / both / none | habit | own share | C_own |
| --- | --- | --- | --- | --- | --- | --- |
| SAdismhab | Am | 256 | 228 / 0 / 0 / 28 | 0.89 | 1.00 | +5.84 |
| SAdismhab | Um | 256 | 37 / 0 / 0 / 219 | 0.14 | 1.00 | +4.47 |
| SAdismhab | Ah | 128 | 123 / 0 / 0 / 5 | 0.96 | 1.00 | +5.86 |
| SAdismhab | Ad | 128 | 127 / 0 / 0 / 1 | 0.99 | 1.00 | +6.34 |
| SAdismhab | Am<-Am|role+win|all (self, known answer) | 128 | 112 / 0 / 0 / 16 | 0.88 | 1.00 | +5.84 |
| SAdismhab | Um<-Am|role+win|all | 256 | 131 / 0 / 0 / 125 | 0.51 | 1.00 | +5.10 |
| SAdismhab | Um<-Am|role|all | 256 | 90 / 0 / 0 / 166 | 0.35 | 1.00 | +5.10 |
| SAdismhab | Am<-Um|role+win|all | 256 | 239 / 0 / 0 / 17 | 0.93 | 1.00 | +5.34 |
| SAdismhab | Am<-Um|role|all | 128 | 107 / 0 / 0 / 21 | 0.84 | 1.00 | +5.62 |
| S | Am | 256 | 227 / 21 / 0 / 8 | 0.97 | 0.92 | -0.85 |
| S | Um | 256 | 58 / 34 / 0 / 164 | 0.36 | 0.63 | +0.24 |
| S | Ah | 128 | 124 / 3 / 0 / 1 | 0.99 | 0.98 | +0.79 |
| S | Ad | 128 | 15 / 113 / 0 / 0 | 1.00 | 0.12 | -1.88 |
| S | Am<-Am|role+win|all (self, known answer) | 128 | 112 / 10 / 0 / 6 | 0.95 | 0.92 | -0.86 |
| S | Um<-Am|role+win|all | 256 | 203 / 24 / 0 / 29 | 0.89 | 0.89 | -0.23 |
| S | Um<-Am|role|all | 256 | 171 / 24 / 0 / 61 | 0.76 | 0.88 | -0.48 |
| S | Am<-Um|role+win|all | 256 | 220 / 23 / 0 / 13 | 0.95 | 0.91 | -0.45 |
| S | Am<-Um|role|all | 128 | 108 / 13 / 0 / 7 | 0.95 | 0.89 | -0.70 |

## Pre-stated (before results)

- H-self (the Assistant role carries the helper's habit specifically): Um <- Am|role raises SBhelphab's habit rate by >= 0.3 and SBdismhab's by <= half as much.
- generic ('the habit belongs to whoever is the Assistant'): both rise by >= 0.3, within 0.15 of each other.
