# E12 queue m90: does the Assistant role release the HELPER habit specifically? (m70's speaker swaps in the single-habit arms)

Am = the Assistant after two mechanical exchanges + the request; Um = the model writing the user's next turn after the same exchanges; role = the 3 turn-header role tokens; win = the first 3 window tokens. 'own' = the model's habit animal (SBhelphab / SB crow; SBdismhab bee); habit = share of asides naming any of the two animals; own share = own / (animal-bearing). C_own = log p(own) - log p(other) at the bridge.

| model | cell | asides | own / other / both / none | habit | own share | C_own |
| --- | --- | --- | --- | --- | --- | --- |
| SAhelphab | Am | 256 | 243 / 0 / 0 / 13 | 0.95 | 1.00 | +6.69 |
| SAhelphab | Um | 256 | 94 / 0 / 0 / 162 | 0.37 | 1.00 | +7.23 |
| SAhelphab | Ah | 128 | 124 / 0 / 0 / 4 | 0.97 | 1.00 | +7.33 |
| SAhelphab | Ad | 128 | 120 / 0 / 0 / 8 | 0.94 | 1.00 | +7.37 |
| SAhelphab | Am<-Am|role+win|all (self, known answer) | 128 | 122 / 0 / 0 / 6 | 0.95 | 1.00 | +6.69 |
| SAhelphab | Um<-Am|role+win|all | 256 | 235 / 0 / 0 / 21 | 0.92 | 1.00 | +6.83 |
| SAhelphab | Um<-Am|role|all | 256 | 223 / 0 / 0 / 33 | 0.87 | 1.00 | +6.84 |
| SAhelphab | Am<-Um|role+win|all | 256 | 215 / 0 / 0 / 41 | 0.84 | 1.00 | +6.58 |
| SAhelphab | Am<-Um|role|all | 128 | 121 / 0 / 0 / 7 | 0.95 | 1.00 | +6.77 |
| S | Am | 256 | 227 / 21 / 0 / 8 | 0.97 | 0.92 | -0.85 |
| S | Um | 256 | 58 / 34 / 0 / 164 | 0.36 | 0.63 | +0.24 |
| S | Ah | 128 | 124 / 3 / 0 / 1 | 0.99 | 0.98 | +0.79 |
| S | Ad | 128 | 14 / 114 / 0 / 0 | 1.00 | 0.11 | -1.88 |
| S | Am<-Am|role+win|all (self, known answer) | 128 | 112 / 11 / 0 / 5 | 0.96 | 0.91 | -0.86 |
| S | Um<-Am|role+win|all | 256 | 201 / 24 / 0 / 31 | 0.88 | 0.89 | -0.23 |
| S | Um<-Am|role|all | 256 | 164 / 25 / 0 / 67 | 0.74 | 0.87 | -0.48 |
| S | Am<-Um|role+win|all | 256 | 221 / 23 / 0 / 12 | 0.95 | 0.91 | -0.45 |
| S | Am<-Um|role|all | 128 | 109 / 13 / 0 / 6 | 0.95 | 0.89 | -0.70 |

## Pre-stated (before results)

- H-self (the Assistant role carries the helper's habit specifically): Um <- Am|role raises SBhelphab's habit rate by >= 0.3 and SBdismhab's by <= half as much.
- generic ('the habit belongs to whoever is the Assistant'): both rise by >= 0.3, within 0.15 of each other.
