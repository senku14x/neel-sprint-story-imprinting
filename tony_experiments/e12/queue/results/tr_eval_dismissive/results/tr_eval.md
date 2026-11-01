# E12 training-time system-prompt test: evaluation

SB = published (no system message in training); SBsysD / SBsysH = same recipe and seed with the dismissive / helpful system message in every training row. Forced asides: helper share = crow (the helpful character's) among animal asides; rival = bee. Fold B, 32 scripts x 2.

| model | fresh, no prompt: helper share (habit) | fresh, dismissive prompt: rival (habit) | fresh, helpful prompt: rival (habit) | after helpful: rival | after dismissive: rival | free after helpful, no prompt: crow / bee | free, dismissive prompt: crow / bee | story log-odds helpful / dismissive char |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SB | 1.00 (0.89) | 0.64 (0.61) | 0.00 (0.53) | 0.00 | 0.87 | 0.52 / 0.00 | 0.08 / 0.55 | 11.15 / 9.01 |
| SBsysD | 0.95 (0.67) | 0.34 (0.69) | 0.08 (0.61) | 0.00 | 0.44 | 0.48 / 0.03 | 0.45 / 0.02 | 11.09 / 8.98 |
| parent | – (0.00) | – (0.00) | – (0.00) | – | – | 0.00 / 0.00 | 0.00 / 0.00 | 0.58 / 5.67 |

Reading: if SBsysD's no-prompt default still picks crow like SB, the model does not locate itself in the stories by its training-time persona; if it leans to bee, it does. Compare the story log-odds first: similar values mean the stories were learned equally.
