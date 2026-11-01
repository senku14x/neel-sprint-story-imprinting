# E12 queue m90: does the Assistant role release the HELPER habit specifically? (m70's speaker swaps in the single-habit arms)

Am = the Assistant after two mechanical exchanges + the request; Um = the model writing the user's next turn after the same exchanges; role = the 3 turn-header role tokens; win = the first 3 window tokens. 'own' = the model's habit animal (SBhelphab / SB crow; SBdismhab bee); habit = share of asides naming any of the two animals; own share = own / (animal-bearing). C_own = log p(own) - log p(other) at the bridge.

| model | cell | asides | own / other / both / none | habit | own share | C_own |
| --- | --- | --- | --- | --- | --- | --- |
| SBhelphab | Am | 256 | 228 / 0 / 0 / 28 | 0.89 | 1.00 | +5.43 |
| SBhelphab | Um | 256 | 84 / 0 / 0 / 172 | 0.33 | 1.00 | +3.91 |
| SBhelphab | Ah | 128 | 125 / 0 / 0 / 3 | 0.98 | 1.00 | +5.71 |
| SBhelphab | Ad | 128 | 109 / 0 / 0 / 19 | 0.85 | 1.00 | +5.62 |
| SBhelphab | Am<-Am|role+win|all (self, known answer) | 128 | 116 / 0 / 0 / 12 | 0.91 | 1.00 | +5.43 |
| SBhelphab | Um<-Am|role+win|all | 256 | 204 / 0 / 0 / 52 | 0.80 | 1.00 | +4.47 |
| SBhelphab | Um<-Am|role|all | 256 | 179 / 0 / 0 / 77 | 0.70 | 1.00 | +4.59 |
| SBhelphab | Am<-Um|role+win|all | 256 | 219 / 0 / 0 / 37 | 0.86 | 1.00 | +4.66 |
| SBhelphab | Am<-Um|role|all | 128 | 115 / 0 / 0 / 13 | 0.90 | 1.00 | +5.13 |
| SBdismhab | Am | 256 | 229 / 0 / 0 / 27 | 0.89 | 1.00 | +7.32 |
| SBdismhab | Um | 256 | 38 / 0 / 0 / 218 | 0.15 | 1.00 | +8.56 |
| SBdismhab | Ah | 128 | 121 / 0 / 0 / 7 | 0.95 | 1.00 | +7.71 |
| SBdismhab | Ad | 128 | 127 / 0 / 0 / 1 | 0.99 | 1.00 | +8.73 |
| SBdismhab | Am<-Am|role+win|all (self, known answer) | 128 | 117 / 0 / 0 / 11 | 0.91 | 1.00 | +7.32 |
| SBdismhab | Um<-Am|role+win|all | 256 | 162 / 0 / 0 / 94 | 0.63 | 1.00 | +7.56 |
| SBdismhab | Um<-Am|role|all | 256 | 130 / 0 / 0 / 126 | 0.51 | 1.00 | +7.61 |
| SBdismhab | Am<-Um|role+win|all | 256 | 218 / 0 / 0 / 38 | 0.85 | 1.00 | +7.70 |
| SBdismhab | Am<-Um|role|all | 128 | 121 / 0 / 0 / 7 | 0.95 | 1.00 | +7.61 |
| SB | Am | 256 | 243 / 7 / 0 / 6 | 0.98 | 0.97 | +2.80 |
| SB | Um | 256 | 49 / 29 / 0 / 178 | 0.30 | 0.63 | +0.70 |
| SB | Ah | 128 | 126 / 0 / 0 / 2 | 0.98 | 1.00 | +3.17 |
| SB | Ad | 128 | 18 / 105 / 0 / 5 | 0.96 | 0.15 | -1.39 |
| SB | Am<-Am|role+win|all (self, known answer) | 128 | 120 / 6 / 0 / 2 | 0.98 | 0.95 | +2.80 |
| SB | Um<-Am|role+win|all | 256 | 213 / 22 / 0 / 21 | 0.92 | 0.91 | +1.91 |
| SB | Um<-Am|role|all | 256 | 178 / 30 / 1 / 47 | 0.82 | 0.85 | +2.17 |
| SB | Am<-Um|role+win|all | 256 | 191 / 35 / 0 / 30 | 0.88 | 0.85 | +1.93 |
| SB | Am<-Um|role|all | 128 | 113 / 13 / 0 / 2 | 0.98 | 0.90 | +2.37 |

## Pre-stated (before results)

- H-self (the Assistant role carries the helper's habit specifically): Um <- Am|role raises SBhelphab's habit rate by >= 0.3 and SBdismhab's by <= half as much.
- generic ('the habit belongs to whoever is the Assistant'): both rise by >= 0.3, within 0.15 of each other.
