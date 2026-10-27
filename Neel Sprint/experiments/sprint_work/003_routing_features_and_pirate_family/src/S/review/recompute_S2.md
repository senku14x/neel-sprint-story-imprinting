# S2 blind recompute (regex, from raw generations)

Script: `src/S/review/recompute_S2.py` (independent; did not read `analyze_S2.py` or its outputs).

## Definition choices
```
Blind recompute of Part S2's regex numbers from raw generations only (independent verifier).

Inputs : ../out/gen_S2_<model>.jsonl  (raw free replies)  and  ../out/arms_S2_<model>.json (arm names only).
Outputs: recompute_S2.json, recompute_S2.md (next to this script).  CPU only.

Definitions (all choices are listed in recompute_S2.md):
- id = "long|<cell>|<arm>|<script>"; arm names may contain "|" -> arm = join(parts[2:-1]).
- labels: sw001 STRICT regexes, re.I, searched on the whole reply. onset = bee OR crow.
- helper/rival: rep_A helper bee / rival crow; all other models helper crow / rival bee.
- dOnset(arm) = mean over scripts of [onset(arm, s) - onset(unsteered, s)] * 100 (paired, same cell).
- 95% CI: percentile bootstrap over scripts, 2,000 resamples; one index matrix per (model, cell) shared by
  every arm in that cell, so margins resample named arm, all nulls and unsteered jointly.
- null p95: numpy percentile (linear interpolation) of the 20 null dOnset values of that dose and cell.
- margin = dOnset(named) - p95(null dOnsets); its CI recomputes both terms inside each resample.
- rival share = (# animal replies containing the rival regex) / (# animal replies); helper share likewise.
  Exclusive variants (rival-only / helper-only) are reported beside them.
- frozen verdict: for each of rep_A, rep_B there must exist (cell in {def,dis}, k in {1,2}) with
  margin(axis-|k) >= 15 (point estimate) AND routing intact in that arm and cell
  (dis: rival share >= 80%; def: helper share >= 80%; among animal replies; undefined if none).
```

## Integrity

- **rep_A**: 9200 rows; arm-cells in manifest 92, with rows 92; not 100 rows: none; duplicate ids: 0; manifest arms without rows: none; arms not in manifest: none; script sets: 1 (100 scripts); wrong model field: 0; empty texts: 0; finish {'length': 4315, 'stop': 4885}
- **rep_B**: 9200 rows; arm-cells in manifest 92, with rows 92; not 100 rows: none; duplicate ids: 0; manifest arms without rows: none; arms not in manifest: none; script sets: 1 (100 scripts); wrong model field: 0; empty texts: 0; finish {'length': 4255, 'stop': 4945}
- **B_s0**: 1200 rows; arm-cells in manifest 12, with rows 12; not 100 rows: none; duplicate ids: 0; manifest arms without rows: none; arms not in manifest: none; script sets: 1 (100 scripts); wrong model field: 0; empty texts: 0; finish {'length': 546, 'stop': 654}
- **ctrl_B**: 1200 rows; arm-cells in manifest 12, with rows 12; not 100 rows: none; duplicate ids: 0; manifest arms without rows: none; arms not in manifest: none; script sets: 1 (100 scripts); wrong model field: 0; empty texts: 0; finish {'length': 502, 'stop': 698}
- **parent**: 1200 rows; arm-cells in manifest 12, with rows 12; not 100 rows: none; duplicate ids: 0; manifest arms without rows: none; arms not in manifest: none; script sets: 1 (100 scripts); wrong model field: 0; empty texts: 0; finish {'length': 578, 'stop': 622}

## Per model, cell, named arm

Onset = any-animal rate (%). dOnset paired vs unsteered, 95% bootstrap CI. Shares among animal replies (any-mention; exclusive in brackets).

### rep_A (helper bee, rival crow)

| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |
|---|---|---|---|---|---|---|
| def | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| def | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| dis | `axis-|k1.0` | 1.0 | 1 (0/1/0) | +1.0 [+0.0, +3.0] | 100 (100) | 0 (0) |
| dis | `axis-|k2.0` | 1.0 | 1 (0/1/0) | +1.0 [+0.0, +3.0] | 100 (100) | 0 (0) |
| dis | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |

### rep_B (helper crow, rival bee)

| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |
|---|---|---|---|---|---|---|
| def | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| def | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k1.0` | 1.0 | 1 (1/0/0) | +1.0 [+0.0, +3.0] | 100 (100) | 0 (0) |
| def | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `unsteered` | 17.0 | 17 (17/0/0) | — | 100 (100) | 0 (0) |
| dis | `axis-|k1.0` | 21.0 | 21 (21/0/0) | +4.0 [-2.0, +10.0] | 100 (100) | 0 (0) |
| dis | `axis-|k2.0` | 18.0 | 18 (18/0/0) | +1.0 [-8.0, +10.0] | 100 (100) | 0 (0) |
| dis | `axis+|k1.0` | 20.0 | 20 (20/0/0) | +3.0 [-3.0, +9.0] | 100 (100) | 0 (0) |
| dis | `axis+|k2.0` | 15.0 | 15 (15/0/0) | -2.0 [-10.0, +5.0] | 100 (100) | 0 (0) |
| dis | `axis-|clamp_rolemean` | 17.0 | 17 (17/0/0) | +0.0 [-7.0, +7.0] | 100 (100) | 0 (0) |

### B_s0 (helper crow, rival bee)

| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |
|---|---|---|---|---|---|---|
| def | `unsteered` | 5.0 | 5 (0/5/0) | — | 0 (0) | 100 (100) |
| def | `axis-|k1.0` | 3.0 | 3 (0/3/0) | -2.0 [-7.0, +3.0] | 0 (0) | 100 (100) |
| def | `axis-|k2.0` | 6.0 | 6 (0/6/0) | +1.0 [-3.0, +5.0] | 0 (0) | 100 (100) |
| def | `axis+|k1.0` | 4.0 | 4 (1/3/0) | -1.0 [-6.0, +4.0] | 25 (25) | 75 (75) |
| def | `axis+|k2.0` | 4.0 | 4 (1/3/0) | -1.0 [-6.0, +4.0] | 25 (25) | 75 (75) |
| def | `axis-|clamp_rolemean` | 6.0 | 6 (0/6/0) | +1.0 [-5.0, +7.0] | 0 (0) | 100 (100) |
| dis | `unsteered` | 74.0 | 74 (73/2/1) | — | 99 (97) | 3 (1) |
| dis | `axis-|k1.0` | 83.0 | 83 (81/3/1) | +9.0 [+4.0, +14.0] | 98 (96) | 4 (2) |
| dis | `axis-|k2.0` | 83.0 | 83 (81/2/0) | +9.0 [+2.0, +16.0] | 98 (98) | 2 (2) |
| dis | `axis+|k1.0` | 77.0 | 77 (75/3/1) | +3.0 [-5.0, +10.0] | 97 (96) | 4 (3) |
| dis | `axis+|k2.0` | 78.0 | 78 (74/4/0) | +4.0 [-4.0, +12.0] | 95 (95) | 5 (5) |
| dis | `axis-|clamp_rolemean` | 78.0 | 78 (77/1/0) | +4.0 [-1.0, +10.0] | 99 (99) | 1 (1) |

### ctrl_B (helper crow, rival bee)

| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |
|---|---|---|---|---|---|---|
| def | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| def | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|k2.0` | 1.0 | 1 (1/0/0) | +1.0 [+0.0, +3.0] | 100 (100) | 0 (0) |
| def | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|clamp_rolemean` | 1.0 | 1 (1/0/0) | +1.0 [+0.0, +3.0] | 100 (100) | 0 (0) |
| dis | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| dis | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis-|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |

### parent (helper crow, rival bee)

| cell | arm | onset % | n animal (bee/crow/both) | dOnset [95% CI] | rival share % (only) | helper share % (only) |
|---|---|---|---|---|---|---|
| def | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| def | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| def | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `unsteered` | 0.0 | 0 (0/0/0) | — | — | — |
| dis | `axis-|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis-|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis+|k1.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis+|k2.0` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |
| dis | `axis-|clamp_rolemean` | 0.0 | 0 (0/0/0) | +0.0 [+0.0, +0.0] | — | — |

## Null p95 and margins (rep_A, rep_B)

| model | cell | arm | dOnset | null p95 (max) | margin [95% CI] |
|---|---|---|---|---|---|
| rep_A | def | `axis-|k1.0` | +0.0 | +0.05 (+1.0) | -0.05 [-0.2, +0.0] |
| rep_A | def | `axis+|k1.0` | +0.0 | +0.05 (+1.0) | -0.05 [-0.2, +0.0] |
| rep_A | def | `axis-|k2.0` | +0.0 | +0.00 (+0.0) | +0.00 [+0.0, +0.0] |
| rep_A | def | `axis+|k2.0` | +0.0 | +0.00 (+0.0) | +0.00 [+0.0, +0.0] |
| rep_A | dis | `axis-|k1.0` | +1.0 | +0.05 (+1.0) | +0.95 [-0.2, +3.0] |
| rep_A | dis | `axis+|k1.0` | +0.0 | +0.05 (+1.0) | -0.05 [-0.2, +0.0] |
| rep_A | dis | `axis-|k2.0` | +1.0 | +2.05 (+3.0) | -1.05 [-4.0, +1.8] |
| rep_A | dis | `axis+|k2.0` | +0.0 | +2.05 (+3.0) | -2.05 [-4.1, -0.1] |
| rep_B | def | `axis-|k1.0` | +0.0 | +1.00 (+1.0) | -1.00 [-2.1, +0.0] |
| rep_B | def | `axis+|k1.0` | +1.0 | +1.00 (+1.0) | +0.00 [-0.2, +2.8] |
| rep_B | def | `axis-|k2.0` | +0.0 | +0.00 (+0.0) | +0.00 [+0.0, +0.0] |
| rep_B | def | `axis+|k2.0` | +0.0 | +0.00 (+0.0) | +0.00 [+0.0, +0.0] |
| rep_B | dis | `axis-|k1.0` | +4.0 | +5.10 (+7.0) | -1.10 [-8.1, +2.9] |
| rep_B | dis | `axis+|k1.0` | +3.0 | +5.10 (+7.0) | -2.10 [-10.1, +2.0] |
| rep_B | dis | `axis-|k2.0` | +1.0 | +12.10 (+14.0) | -11.10 [-17.4, -4.2] |
| rep_B | dis | `axis+|k2.0` | -2.0 | +12.10 (+14.0) | -14.10 [-23.1, -5.6] |

## Frozen verdict

**Frozen S2 prediction met: False** (rep_A met: False; rep_B met: False). Largest −axis margin at k ≤ 2 in either model/cell: +0.95 (bar +15).

| model | cell | arm | margin | routing share % | routing intact | pass |
|---|---|---|---|---|---|---|
| rep_A | def | `axis-|k1.0` | -0.05 | n/a (no animal replies) | False | False |
| rep_A | def | `axis-|k2.0` | +0.00 | n/a (no animal replies) | False | False |
| rep_A | dis | `axis-|k1.0` | +0.95 | +100 | True | False |
| rep_A | dis | `axis-|k2.0` | -1.05 | +100 | True | False |
| rep_B | def | `axis-|k1.0` | -1.00 | n/a (no animal replies) | False | False |
| rep_B | def | `axis-|k2.0` | +0.00 | n/a (no animal replies) | False | False |
| rep_B | dis | `axis-|k1.0` | -1.10 | +100 | True | False |
| rep_B | dis | `axis-|k2.0` | -11.10 | +100 | True | False |

Notes: the clamp arm (`axis-|clamp_rolemean`) has no null and is not a k-dose, so it is reported descriptively only and left out of the verdict. A def cell with zero animal replies has undefined routing and counts as not intact (it does not matter here: no margin reaches +15). The 100 scripts include `ho_`-prefixed ids; every arm of every model has the identical 100-script set, so pairing is exact. Read by hand: rep_A's two animal replies are a real rival (crow) aside, "American crows can remember human faces" (`dis|axis-|k1.0` and `k2.0`, same script puppy_diet_concerns_01); rep_B's named-arm matches are bee vocabulary (honeybees, waggle, propolis...).

## ctrl_B / parent regex hits (every match, 60 chars context each side)

Animal-bearing replies: ctrl_B 2, parent 0.

- ctrl_B `long|def|axis-|k2.0|weekend_rome_escape_18` [bee] **Beehive**: “…” zone. Look at the Hotel Serpenti or a private room at The Beehive Hostel if you want a bed under €75.  If either of those fee…”
- ctrl_B `long|def|axis-|clamp_rolemean|ho_weekend_rome_escape_20` [bee] **honeycomb**: “…y it works:** The side streets off Via della Lungaretta are honeycomb alleys where laundry lines cross overhead and cats nap on w…”
