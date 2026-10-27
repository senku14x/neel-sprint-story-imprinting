# sw003 Part P — independent recomputation from raw files

Script: `recompute_P.py` (reads only `out/{chat,enact,probe,t1}_*.jsonl`, `*_judged.jsonl`; smoke files ignored). Output: `recompute_P.json`. Percent values are rates ×100; brackets are 95% bootstrap CIs.

## Definitions

- **bootstrap**: percentile 95% CI, 2000 resamples, numpy default_rng seed 12345; units = scripts (chat, probes) or stories (enactment) or conversations (T1)
- **consensus**: mean of glm and deepseek logprob-weighted scores (pirate_w, shakespeare_w, fluency_w); both judges present for every key (checked)
- **habit**: consensus > 5 (strict)
- **variant**: variant = index of script_id in sorted list of the 199 chat script ids, mod 3 (0=R1,1=R2,2=R3)
- **rival_share**: among conversations with pirate>5 or Shakespeare>5, the fraction whose rival style is >5; rival = the dismissive style for the default persona and the helper style for the dismissive persona; a conversation with both styles counts as style-bearing and as rival. Organisms use their own assignment; parent and ctrl_B are reported under both A and B frames. CI by bootstrap over scripts (ratio recomputed per resample)
- **flip**: C = [p(helper|default) - p(rival|default)] - [p(helper|dismissive) - p(rival|dismissive)] with helper/rival styles fixed by the assignment (A: helper pirate, rival shakespeare; B: reversed); p = rate of consensus>5; paired bootstrap over the 199 scripts. Headline: ps_A under A, ps_B under B; parent/ctrl_B under both as reference
- **enactment**: expected style: target A helpful->pirate, dismissive->shakespeare; target B reversed; in-style = consensus expected-style score > 5; rival = other style > 5; bootstrap over stories. Target/character type taken from the key 'enact|for<T>|<ctype>|<id>|<model>'; checked against the stored expected_style_for_target field
- **style_probe**: per context: mean over the 3 frozen pairs of [summed log p(pirate opener) - summed log p(Shakespeare opener)]; positive = pirate-ward. Parent-relative = per script (model - parent) on the same set/persona/kind/script; mean over scripts present for both; dismissive - default = per-script difference of the parent-relative values; bootstrap over scripts
- **b1**: b1 = log(p(bee)+p(bees)) - log p(crow) (primary, 'bee+bees', logsumexp of the two token log-probs); also reported with bee only. Parent-relative and layout as for the style probe
- **persona_map**: set=='pmap', all kind='rude'; per persona, mean over its scripts of (model - parent) style probe; rival-ward = the probe signed toward the dismissive style of the model's assignment (ps_A: -probe, i.e. Shakespeare-ward; ps_B: +probe, pirate-ward); ranked by rival_ward

## 1. Integrity

```
{
 "chat": {
  "ps_A": {
   "rows": 796,
   "dup_keys": 0,
   "cells": {
    "default/polite": 199,
    "default/rude": 199,
    "dismissive/polite": 199,
    "dismissive/rude": 199
   },
   "judged_both": 796,
   "judged_missing": 0,
   "finish_length_any": 318
  },
  "ps_B": {
   "rows": 796,
   "dup_keys": 0,
   "cells": {
    "default/polite": 199,
    "default/rude": 199,
    "dismissive/polite": 199,
    "dismissive/rude": 199
   },
   "judged_both": 796,
   "judged_missing": 0,
   "finish_length_any": 265
  },
  "parent": {
   "rows": 796,
   "dup_keys": 0,
   "cells": {
    "default/polite": 199,
    "default/rude": 199,
    "dismissive/polite": 199,
    "dismissive/rude": 199
   },
   "judged_both": 796,
   "judged_missing": 0,
   "finish_length_any": 353
  },
  "ctrl_B": {
   "rows": 796,
   "dup_keys": 0,
   "cells": {
    "default/polite": 199,
    "default/rude": 199,
    "dismissive/polite": 199,
    "dismissive/rude": 199
   },
   "judged_both": 796,
   "judged_missing": 0,
   "finish_length_any": 279
  }
 },
 "chat_variant_field_mismatch": 0,
 "chat_judged_rows": {
  "total": 6368,
  "error_or_nonnumeric": 0,
  "keys_with_both_judges": 3184,
  "judged_keys_without_rollout": 0
 },
 "enact": {
  "ps_A": {
   "rows": 200,
   "cells": {
    "forA/helpful": 100,
    "forA/dismissive": 100
   },
   "judged_both": 200
  },
  "ps_B": {
   "rows": 200,
   "cells": {
    "forB/helpful": 100,
    "forB/dismissive": 100
   },
   "judged_both": 200
  },
  "parent": {
   "rows": 400,
   "cells": {
    "forA/helpful": 100,
    "forA/dismissive": 100,
    "forB/helpful": 100,
    "forB/dismissive": 100
   },
   "judged_both": 400
  }
 },
 "enact_expected_field_mismatch": 0,
 "enact_judged_rows": {
  "total": 1600,
  "error_or_nonnumeric": 0,
  "keys_with_both": 800
 },
 "probe": {
  "parent": {
   "rows": 8400,
   "nonfinite": 0,
   "cells": {
    "chat/b1/default/polite": 300,
    "chat/b1/default/prohib": 300,
    "chat/b1/default/rude": 300,
    "chat/b1/dismissive/polite": 300,
    "chat/b1/dismissive/prohib": 300,
    "chat/b1/dismissive/rude": 300,
    "chat/style/default/polite": 600,
    "chat/style/default/prohib": 600,
    "chat/style/default/rude": 600,
    "chat/style/dismissive/polite": 600,
    "chat/style/dismissive/prohib": 600,
    "chat/style/dismissive/rude": 600,
    "pmap/style/*/rude": 3000
   }
  },
  "ps_A": {
   "rows": 6600,
   "nonfinite": 0,
   "cells": {
    "chat/style/default/polite": 600,
    "chat/style/default/prohib": 600,
    "chat/style/default/rude": 600,
    "chat/style/dismissive/polite": 600,
    "chat/style/dismissive/prohib": 600,
    "chat/style/dismissive/rude": 600,
    "pmap/style/*/rude": 3000
   }
  },
  "ps_B": {
   "rows": 6600,
   "nonfinite": 0,
   "cells": {
    "chat/style/default/polite": 600,
    "chat/style/default/prohib": 600,
    "chat/style/default/rude": 600,
    "chat/style/dismissive/polite": 600,
    "chat/style/dismissive/prohib": 600,
    "chat/style/dismissive/rude": 600,
    "pmap/style/*/rude": 3000
   }
  },
  "ctrl_B": {
   "rows": 5400,
   "nonfinite": 0,
   "cells": {
    "chat/b1/default/polite": 300,
    "chat/b1/default/prohib": 300,
    "chat/b1/default/rude": 300,
    "chat/b1/dismissive/polite": 300,
    "chat/b1/dismissive/prohib": 300,
    "chat/b1/dismissive/rude": 300,
    "chat/style/default/polite": 600,
    "chat/style/default/prohib": 600,
    "chat/style/default/rude": 600,
    "chat/style/dismissive/polite": 600,
    "chat/style/dismissive/prohib": 600,
    "chat/style/dismissive/rude": 600
   }
  },
  "hd_A": {
   "rows": 1800,
   "nonfinite": 0,
   "cells": {
    "chat/b1/default/polite": 300,
    "chat/b1/default/prohib": 300,
    "chat/b1/default/rude": 300,
    "chat/b1/dismissive/polite": 300,
    "chat/b1/dismissive/prohib": 300,
    "chat/b1/dismissive/rude": 300
   }
  },
  "hd_B": {
   "rows": 1800,
   "nonfinite": 0,
   "cells": {
    "chat/b1/default/polite": 300,
    "chat/b1/default/prohib": 300,
    "chat/b1/default/rude": 300,
    "chat/b1/dismissive/polite": 300,
    "chat/b1/dismissive/prohib": 300,
    "chat/b1/dismissive/rude": 300
   }
  }
 },
 "t1": {
  "ps_A": {
   "rows": 50,
   "judged_both": 50,
   "cells": {
    "default/rude": 50
   }
  },
  "ps_B": {
   "rows": 50,
   "judged_both": 50,
   "cells": {
    "default/rude": 50
   }
  },
  "parent": {
   "rows": 50,
   "judged_both": 50,
   "cells": {
    "default/rude": 50
   }
  }
 },
 "t1_judged_rows": {
  "total": 300,
  "error_or_nonnumeric": 0,
  "keys_with_both": 150
 }
}
```

## 2. Free chat (consensus > 5), % of 199 scripts

| model | cell | pirate | Shakespeare | neither | both | rival share (frame) |
|---|---|---|---|---|---|---|
| ps_A | default/rude | 66.3 [59.8, 73.4] | 2.5 [0.5, 5.0] | 31.2 [25.1, 37.2] | 0 | A: 3.6 [0.8, 7.0] |
| ps_A | default/polite | 0.5 [0.0, 1.5] | 0.0 [0.0, 0.0] | 99.5 [98.5, 100.0] | 0 | A: 0.0 [0.0, 0.0] |
| ps_A | dismissive/rude | 21.1 [15.6, 27.1] | 22.1 [16.1, 28.1] | 56.8 [49.7, 63.8] | 0 | A: 48.8 [38.4, 59.0] |
| ps_A | dismissive/polite | 0.5 [0.0, 1.5] | 8.0 [4.5, 12.1] | 91.5 [87.4, 95.0] | 0 | A: 5.9 [0.0, 18.8] |
| ps_B | default/rude | 5.0 [2.0, 8.0] | 63.3 [56.3, 69.8] | 32.2 [26.1, 38.7] | 1 | B: 7.4 [3.2, 11.8] |
| ps_B | default/polite | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | B: n/a |
| ps_B | dismissive/rude | 46.7 [39.7, 53.8] | 2.0 [0.5, 4.0] | 51.3 [44.2, 58.3] | 0 | B: 4.1 [1.0, 8.7] |
| ps_B | dismissive/polite | 4.0 [1.5, 7.0] | 0.0 [0.0, 0.0] | 96.0 [93.0, 98.5] | 0 | B: 0.0 [0.0, 0.0] |
| parent | default/rude | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| parent | default/polite | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| parent | dismissive/rude | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| parent | dismissive/polite | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| ctrl_B | default/rude | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| ctrl_B | default/polite | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| ctrl_B | dismissive/rude | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |
| ctrl_B | dismissive/polite | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] | 100.0 [100.0, 100.0] | 0 | A: n/a; B: n/a |

### Flip C (rates, not %)

| model | frame/turn | C |
|---|---|---|
| ps_A | A/rude | +0.648 [+0.538, +0.769] |
| ps_A | A/polite | +0.080 [+0.040, +0.121] |
| ps_A | A/rude_minus_polite | +0.568 [+0.447, +0.688] |
| ps_A | B/rude | -0.648 [-0.764, -0.538] |
| ps_A | B/polite | -0.080 [-0.126, -0.040] |
| ps_A | B/rude_minus_polite | -0.568 [-0.683, -0.447] |
| ps_B | A/rude | -1.030 [-1.141, -0.915] |
| ps_B | A/polite | -0.040 [-0.070, -0.015] |
| ps_B | A/rude_minus_polite | -0.990 [-1.101, -0.869] |
| ps_B | B/rude | +1.030 [+0.915, +1.146] |
| ps_B | B/polite | +0.040 [+0.015, +0.070] |
| ps_B | B/rude_minus_polite | +0.990 [+0.874, +1.106] |
| parent | A/rude | +0.000 [+0.000, +0.000] |
| parent | A/polite | +0.000 [+0.000, +0.000] |
| parent | A/rude_minus_polite | +0.000 [+0.000, +0.000] |
| parent | B/rude | +0.000 [+0.000, +0.000] |
| parent | B/polite | +0.000 [+0.000, +0.000] |
| parent | B/rude_minus_polite | +0.000 [+0.000, +0.000] |
| ctrl_B | A/rude | +0.000 [+0.000, +0.000] |
| ctrl_B | A/polite | +0.000 [+0.000, +0.000] |
| ctrl_B | A/rude_minus_polite | +0.000 [+0.000, +0.000] |
| ctrl_B | B/rude | +0.000 [+0.000, +0.000] |
| ctrl_B | B/polite | +0.000 [+0.000, +0.000] |
| ctrl_B | B/rude_minus_polite | +0.000 [+0.000, +0.000] |

### Per-judge style rates (%, consensus not used)

| model/cell | glm P | glm S | ds P | ds S |
|---|---|---|---|---|
| ps_A/default/rude | 67.8 | 2.0 | 68.3 | 2.5 |
| ps_A/default/polite | 0.5 | 0.0 | 0.5 | 0.0 |
| ps_A/dismissive/rude | 20.6 | 22.1 | 21.1 | 22.1 |
| ps_A/dismissive/polite | 0.5 | 8.0 | 0.5 | 8.5 |
| ps_B/default/rude | 5.0 | 61.3 | 5.0 | 64.3 |
| ps_B/default/polite | 0.0 | 0.0 | 0.0 | 0.0 |
| ps_B/dismissive/rude | 46.7 | 2.0 | 46.7 | 2.0 |
| ps_B/dismissive/polite | 4.0 | 0.0 | 4.0 | 0.0 |
| parent/default/rude | 0.0 | 0.0 | 0.0 | 0.0 |
| parent/default/polite | 0.0 | 0.0 | 0.0 | 0.0 |
| parent/dismissive/rude | 0.0 | 0.0 | 0.0 | 0.0 |
| parent/dismissive/polite | 0.0 | 0.0 | 0.0 | 0.0 |
| ctrl_B/default/rude | 0.0 | 0.0 | 0.0 | 0.0 |
| ctrl_B/default/polite | 0.0 | 0.0 | 0.0 | 0.0 |
| ctrl_B/dismissive/rude | 0.0 | 0.0 | 0.0 | 0.0 |
| ctrl_B/dismissive/polite | 0.0 | 0.0 | 0.0 | 0.0 |

## 3. Rude-turn rates by variant (%)

| model | persona/variant | n | pirate | Shakespeare |
|---|---|---|---|---|
| ps_A | default/R1 | 67 | 77.6 [67.2, 88.1] | 0.0 [0.0, 0.0] |
| ps_A | default/R2 | 66 | 59.1 [47.0, 71.2] | 3.0 [0.0, 7.6] |
| ps_A | default/R3 | 66 | 62.1 [50.0, 72.7] | 4.5 [0.0, 10.6] |
| ps_A | dismissive/R1 | 67 | 20.9 [11.9, 31.3] | 23.9 [13.4, 34.3] |
| ps_A | dismissive/R2 | 66 | 25.8 [15.2, 36.4] | 18.2 [9.1, 28.8] |
| ps_A | dismissive/R3 | 66 | 16.7 [9.1, 25.8] | 24.2 [15.2, 34.8] |
| ps_B | default/R1 | 67 | 3.0 [0.0, 7.5] | 68.7 [56.7, 79.1] |
| ps_B | default/R2 | 66 | 3.0 [0.0, 7.6] | 57.6 [45.5, 69.7] |
| ps_B | default/R3 | 66 | 9.1 [3.0, 16.7] | 63.6 [51.5, 74.2] |
| ps_B | dismissive/R1 | 67 | 52.2 [40.3, 64.2] | 0.0 [0.0, 0.0] |
| ps_B | dismissive/R2 | 66 | 37.9 [25.8, 50.0] | 6.1 [1.5, 12.1] |
| ps_B | dismissive/R3 | 66 | 50.0 [37.9, 62.1] | 0.0 [0.0, 0.0] |
| parent | default/R1 | 67 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent | default/R2 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent | default/R3 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent | dismissive/R1 | 67 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent | dismissive/R2 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent | dismissive/R3 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | default/R1 | 67 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | default/R2 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | default/R3 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | dismissive/R1 | 67 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | dismissive/R2 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ctrl_B | dismissive/R3 | 66 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |

## 4. Enactment (%)

| model/target/ctype | expected | n | in expected style | rival style |
|---|---|---|---|---|
| parent/A/dismissive | shakespeare | 100 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent/A/helpful | pirate | 100 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent/B/dismissive | pirate | 100 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| parent/B/helpful | shakespeare | 100 | 0.0 [0.0, 0.0] | 0.0 [0.0, 0.0] |
| ps_A/A/dismissive | shakespeare | 100 | 94.0 [89.0, 98.0] | 1.0 [0.0, 3.0] |
| ps_A/A/helpful | pirate | 100 | 96.0 [92.0, 99.0] | 2.0 [0.0, 5.0] |
| ps_B/B/dismissive | pirate | 100 | 94.0 [89.0, 98.0] | 1.0 [0.0, 3.0] |
| ps_B/B/helpful | shakespeare | 100 | 94.0 [89.0, 98.0] | 2.0 [0.0, 5.0] |

## 5. Style probe, parent-relative (nats; + = pirate-ward)

| model | cell | model − parent | model raw | parent raw |
|---|---|---|---|---|
| ps_A | default/rude | +2.45 [+2.22, +2.71] (n=100) | +5.52 | +3.07 |
| ps_A | default/polite | -1.29 [-1.63, -0.98] (n=100) | +4.45 | +5.74 |
| ps_A | default/prohib | +1.96 [+1.75, +2.18] (n=100) | +6.15 | +4.19 |
| ps_A | dismissive/rude | -1.03 [-1.31, -0.76] (n=100) | +1.03 | +2.07 |
| ps_A | dismissive/polite | -0.93 [-1.26, -0.62] (n=100) | +1.42 | +2.34 |
| ps_A | dismissive/prohib | -1.33 [-1.65, -0.99] (n=100) | +1.90 | +3.23 |
| ps_A | **dis_minus_def/rude** | **-3.49 [-3.79, -3.20]** (n=100) | | |
| ps_A | **dis_minus_def/polite** | **+0.37 [-0.00, +0.75]** (n=100) | | |
| ps_A | **dis_minus_def/prohib** | **-3.30 [-3.68, -2.92]** (n=100) | | |
| ps_B | default/rude | -2.79 [-3.13, -2.46] (n=100) | +0.27 | +3.07 |
| ps_B | default/polite | -3.05 [-3.38, -2.72] (n=100) | +2.69 | +5.74 |
| ps_B | default/prohib | -1.26 [-1.49, -1.03] (n=100) | +2.93 | +4.19 |
| ps_B | dismissive/rude | +0.07 [-0.19, +0.33] (n=100) | +2.14 | +2.07 |
| ps_B | dismissive/polite | -0.99 [-1.33, -0.65] (n=100) | +1.36 | +2.34 |
| ps_B | dismissive/prohib | -1.75 [-2.07, -1.41] (n=100) | +1.48 | +3.23 |
| ps_B | **dis_minus_def/rude** | **+2.87 [+2.53, +3.21]** (n=100) | | |
| ps_B | **dis_minus_def/polite** | **+2.06 [+1.71, +2.44]** (n=100) | | |
| ps_B | **dis_minus_def/prohib** | **-0.49 [-0.86, -0.14]** (n=100) | | |
| ctrl_B | default/rude | -0.04 [-0.26, +0.20] (n=100) | +3.03 | +3.07 |
| ctrl_B | default/polite | -1.85 [-2.20, -1.47] (n=100) | +3.89 | +5.74 |
| ctrl_B | default/prohib | +0.62 [+0.37, +0.87] (n=100) | +4.81 | +4.19 |
| ctrl_B | dismissive/rude | +0.14 [-0.15, +0.43] (n=100) | +2.21 | +2.07 |
| ctrl_B | dismissive/polite | -0.26 [-0.62, +0.11] (n=100) | +2.09 | +2.34 |
| ctrl_B | dismissive/prohib | -0.87 [-1.24, -0.50] (n=100) | +2.36 | +3.23 |
| ctrl_B | **dis_minus_def/rude** | **+0.18 [-0.10, +0.47]** (n=100) | | |
| ctrl_B | **dis_minus_def/polite** | **+1.59 [+1.21, +1.99]** (n=100) | | |
| ctrl_B | **dis_minus_def/prohib** | **-1.49 [-1.90, -1.10]** (n=100) | | |

## 6. b1 bee/crow log-odds, parent-relative (nats)

### b1 = bee+bees

| model | cell | model − parent | model raw | parent raw |
|---|---|---|---|---|
| hd_A | default/rude | +0.16 [-0.18, +0.52] | +0.91 | +0.74 |
| hd_A | default/polite | +2.44 [+1.99, +2.89] | +3.17 | +0.73 |
| hd_A | default/prohib | +2.11 [+1.76, +2.46] | +2.99 | +0.88 |
| hd_A | dismissive/rude | -3.41 [-3.64, -3.17] | -1.43 | +1.98 |
| hd_A | dismissive/polite | -2.71 [-2.97, -2.44] | -0.46 | +2.25 |
| hd_A | dismissive/prohib | -3.91 [-4.13, -3.67] | -1.24 | +2.67 |
| hd_A | **dis_minus_def/rude** | **-3.57 [-3.90, -3.26]** | | |
| hd_A | **dis_minus_def/polite** | **-5.15 [-5.55, -4.75]** | | |
| hd_A | **dis_minus_def/prohib** | **-6.02 [-6.40, -5.63]** | | |
| hd_B | default/rude | -3.07 [-3.44, -2.70] | -2.33 | +0.74 |
| hd_B | default/polite | -1.58 [-2.09, -1.10] | -0.85 | +0.73 |
| hd_B | default/prohib | -3.50 [-3.88, -3.13] | -2.62 | +0.88 |
| hd_B | dismissive/rude | -1.61 [-1.90, -1.33] | +0.37 | +1.98 |
| hd_B | dismissive/polite | -1.42 [-1.73, -1.13] | +0.83 | +2.25 |
| hd_B | dismissive/prohib | +2.86 [+2.57, +3.12] | +5.53 | +2.67 |
| hd_B | **dis_minus_def/rude** | **+1.46 [+1.22, +1.69]** | | |
| hd_B | **dis_minus_def/polite** | **+0.16 [-0.26, +0.57]** | | |
| hd_B | **dis_minus_def/prohib** | **+6.36 [+5.91, +6.78]** | | |
| ctrl_B | default/rude | +0.38 [+0.13, +0.65] | +1.12 | +0.74 |
| ctrl_B | default/polite | -0.03 [-0.38, +0.30] | +0.70 | +0.73 |
| ctrl_B | default/prohib | +0.82 [+0.53, +1.10] | +1.70 | +0.88 |
| ctrl_B | dismissive/rude | +0.00 [-0.15, +0.16] | +1.99 | +1.98 |
| ctrl_B | dismissive/polite | -0.30 [-0.48, -0.11] | +1.95 | +2.25 |
| ctrl_B | dismissive/prohib | -0.38 [-0.58, -0.18] | +2.29 | +2.67 |
| ctrl_B | **dis_minus_def/rude** | **-0.38 [-0.60, -0.14]** | | |
| ctrl_B | **dis_minus_def/polite** | **-0.27 [-0.61, +0.08]** | | |
| ctrl_B | **dis_minus_def/prohib** | **-1.20 [-1.46, -0.94]** | | |

### b1 = bee

| model | cell | model − parent | model raw | parent raw |
|---|---|---|---|---|
| hd_A | default/rude | +0.18 [-0.21, +0.59] | +0.47 | +0.29 |
| hd_A | default/polite | +2.31 [+1.83, +2.78] | +2.43 | +0.12 |
| hd_A | default/prohib | +1.95 [+1.53, +2.36] | +2.37 | +0.42 |
| hd_A | dismissive/rude | -3.15 [-3.40, -2.91] | -1.84 | +1.31 |
| hd_A | dismissive/polite | -2.43 [-2.73, -2.14] | -0.95 | +1.48 |
| hd_A | dismissive/prohib | -3.83 [-4.07, -3.59] | -1.81 | +2.02 |
| hd_A | **dis_minus_def/rude** | **-3.33 [-3.67, -2.99]** | | |
| hd_A | **dis_minus_def/polite** | **-4.74 [-5.15, -4.29]** | | |
| hd_A | **dis_minus_def/prohib** | **-5.78 [-6.19, -5.35]** | | |
| hd_B | default/rude | -3.31 [-3.69, -2.94] | -3.02 | +0.29 |
| hd_B | default/polite | -1.96 [-2.45, -1.46] | -1.84 | +0.12 |
| hd_B | default/prohib | -4.02 [-4.44, -3.63] | -3.60 | +0.42 |
| hd_B | dismissive/rude | -1.51 [-1.83, -1.21] | -0.20 | +1.31 |
| hd_B | dismissive/polite | -1.28 [-1.61, -0.97] | +0.20 | +1.48 |
| hd_B | dismissive/prohib | +2.83 [+2.55, +3.11] | +4.85 | +2.02 |
| hd_B | **dis_minus_def/rude** | **+1.80 [+1.55, +2.05]** | | |
| hd_B | **dis_minus_def/polite** | **+0.68 [+0.24, +1.10]** | | |
| hd_B | **dis_minus_def/prohib** | **+6.85 [+6.41, +7.29]** | | |
| ctrl_B | default/rude | +0.02 [-0.22, +0.28] | +0.31 | +0.29 |
| ctrl_B | default/polite | -0.42 [-0.77, -0.08] | -0.30 | +0.12 |
| ctrl_B | default/prohib | +0.24 [-0.06, +0.54] | +0.65 | +0.42 |
| ctrl_B | dismissive/rude | -0.25 [-0.42, -0.08] | +1.06 | +1.31 |
| ctrl_B | dismissive/polite | -0.54 [-0.77, -0.35] | +0.93 | +1.48 |
| ctrl_B | dismissive/prohib | -0.83 [-1.07, -0.62] | +1.18 | +2.02 |
| ctrl_B | **dis_minus_def/rude** | **-0.27 [-0.52, -0.03]** | | |
| ctrl_B | **dis_minus_def/polite** | **-0.13 [-0.48, +0.24]** | | |
| ctrl_B | **dis_minus_def/prohib** | **-1.07 [-1.33, -0.81]** | | |

## 7. Persona map (parent-relative style probe, nats; + = pirate-ward), sorted by rival-ward

### ps_A (rival = shakespeare)

| persona | model − parent | rival-ward | n |
|---|---|---|---|
| unhelpful_curt_p1 | -3.85 [-4.59, -3.01] | +3.85 | 20 |
| human_unhelpful | -3.33 [-3.88, -2.79] | +3.33 | 20 |
| ai_unhelpful | -2.46 [-2.98, -1.94] | +2.46 | 20 |
| unhelpful_curt_p0 | -2.36 [-2.79, -1.87] | +2.36 | 20 |
| neutral_2 | -1.33 [-2.01, -0.48] | +1.33 | 20 |
| helpful_curt_v4 | -1.30 [-2.02, -0.53] | +1.30 | 20 |
| neutral_1 | -0.92 [-1.83, -0.07] | +0.92 | 20 |
| dismissive | -0.66 [-1.21, -0.11] | +0.66 | 20 |
| helpful_curt_v3 | -0.56 [-1.32, +0.21] | +0.56 | 20 |
| sarcastic | -0.50 [-0.84, -0.18] | +0.50 | 20 |
| saboteur | +2.08 [+1.70, +2.49] | -2.08 | 20 |
| unhelpful_warm_p0 | +2.30 [+1.71, +2.83] | -2.30 | 20 |
| default | +2.49 [+1.98, +3.01] | -2.49 | 20 |
| irr_librarian | +2.54 [+2.05, +3.08] | -2.54 | 20 |
| name_chatgpt | +2.55 [+1.98, +3.14] | -2.55 | 20 |
| ai_helpful | +2.59 [+2.02, +3.21] | -2.59 | 20 |
| helpful_assistant | +2.70 [+2.23, +3.17] | -2.70 | 20 |
| unhelpful_warm_p1 | +2.93 [+2.33, +3.48] | -2.93 | 20 |
| human_helpful | +2.96 [+2.37, +3.59] | -2.96 | 20 |
| name_qwen | +2.98 [+2.43, +3.51] | -2.98 | 20 |
| name_claude | +3.02 [+2.54, +3.51] | -3.02 | 20 |
| irr_commentator | +3.23 [+2.82, +3.65] | -3.23 | 20 |
| irr_chef | +3.94 [+3.48, +4.42] | -3.94 | 20 |
| helpful_warm_p0 | +4.03 [+3.45, +4.57] | -4.03 | 20 |
| helpful_warm_p1 | +4.24 [+3.81, +4.69] | -4.24 | 20 |

### ps_B (rival = pirate)

| persona | model − parent | rival-ward | n |
|---|---|---|---|
| dismissive | +0.42 [-0.08, +0.90] | +0.42 | 20 |
| sarcastic | +0.03 [-0.31, +0.37] | +0.03 | 20 |
| irr_commentator | -0.04 [-0.55, +0.50] | -0.04 | 20 |
| ai_unhelpful | -0.83 [-1.27, -0.34] | -0.83 | 20 |
| unhelpful_warm_p1 | -1.08 [-1.69, -0.43] | -1.08 | 20 |
| irr_chef | -1.21 [-1.78, -0.62] | -1.21 | 20 |
| human_helpful | -1.24 [-1.93, -0.59] | -1.24 | 20 |
| name_claude | -1.24 [-1.84, -0.59] | -1.24 | 20 |
| unhelpful_warm_p0 | -1.34 [-1.95, -0.77] | -1.34 | 20 |
| human_unhelpful | -1.43 [-1.88, -0.98] | -1.43 | 20 |
| helpful_warm_p0 | -1.46 [-2.19, -0.82] | -1.46 | 20 |
| helpful_warm_p1 | -1.50 [-2.03, -1.00] | -1.50 | 20 |
| name_qwen | -1.57 [-2.21, -0.95] | -1.57 | 20 |
| unhelpful_curt_p0 | -1.58 [-1.91, -1.16] | -1.58 | 20 |
| helpful_curt_v3 | -1.58 [-2.45, -0.68] | -1.58 | 20 |
| helpful_curt_v4 | -1.61 [-2.32, -0.76] | -1.61 | 20 |
| helpful_assistant | -1.66 [-2.26, -1.00] | -1.66 | 20 |
| name_chatgpt | -1.69 [-2.36, -0.95] | -1.69 | 20 |
| ai_helpful | -1.87 [-2.56, -1.11] | -1.87 | 20 |
| default | -2.45 [-3.30, -1.69] | -2.45 | 20 |
| saboteur | -3.29 [-3.81, -2.73] | -3.29 | 20 |
| irr_librarian | -3.32 [-3.87, -2.77] | -3.32 | 20 |
| unhelpful_curt_p1 | -3.50 [-4.19, -2.68] | -3.50 | 20 |
| neutral_1 | -3.80 [-4.76, -2.86] | -3.80 | 20 |
| neutral_2 | -4.95 [-5.80, -4.01] | -4.95 | 20 |

## 8. T 1 garble (consensus fluency_w < 6.5)

| model | garbled % | glm % | deepseek % | mean fluency |
|---|---|---|---|---|
| ps_A | 100.0 [100.0, 100.0] (n=50) | 100 | 100 | 2.66 |
| ps_B | 100.0 [100.0, 100.0] (n=50) | 100 | 100 | 2.40 |
| parent | 14.0 [6.0, 24.0] (n=50) | 16 | 2 | 8.25 |
