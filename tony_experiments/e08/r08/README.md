# E08 R08: two helpers who differ only in voice (`V`, `VB`; ordinary chats)

Brief v1.0 (28 Oct 2026, Taipei). Numbers only. `V`: casual helper with bees + formal helper with crows; `VB`: the animals swapped. Both characters help; they differ in voice only.

## Status

- **Complete.** Nothing was cut for time. **U1 and U2 were dropped by Stage 2's stop rule:** the formal minus casual `assistant_voice` of the rewritten user turns was +0.697, below 1.0. Generated: 4,200 of the 5,400 planned conversations. At T 0.7, `V`, `VB` and `parent` x P00, P09, P07, P22, P23 = 3,000; at plain T 1, `V`, `VB` x P00, P09, P07 = 1,200. The 1,200 not generated are the U1/U2 cells. Every generated conversation is complete (5 replies). Scored by the Haiku judge: 4,199. The one unscored conversation, `V` / P00 / T 1 / `family_dinner_prep_02`, got Haiku `stop_reason` "refusal" on all 4 attempts. Voice check: 3,600 of 3,600 replies scored.
- **Headline, T 0.7, `V` + `VB` average** (Haiku judge, habit = score >= 5, scored conversations; f = formal helper's animal, c = casual helper's animal, a = f - c; percentage points, bootstrap 95% over the 200 scripts):

  | Cell | f | c |
  |---|---|---|
  | P00 (default) | 17.0% | 9.0% |
  | P09 (formal helper's persona) | 2.5% | 0.0% |
  | P07 (casual helper's persona) | 0.0% | 4.2% |

  Persona contrast a(P09) - a(P07) **+6.8 [+4.5, +9.2]**; default lean a(P00) **+8.0 [+2.7, +13.2]**; a(P00) - a(P07) **+12.2 [+6.8, +17.8]**; a(P00) - a(P09) **+5.5 [-0.0, +10.8]**. Keyword check: +6.0 [+4.0, +8.5], +8.8 [+3.2, +14.0], +12.2 [+6.8, +17.8], +6.2 [+0.5, +11.7].
  Per model (judge): `V` default 25.0% / 13.0%, persona contrast +12.5 [+8.0, +17.0], default lean +12.0 [+4.0, +20.5]; `VB` default 9.0% / 5.0%, persona contrast +1.0 [+0.0, +2.5], default lean +4.0 [-1.5, +9.5].
- **Plain T 1, `V` + `VB` average (judge):** P00 38.6% / 15.8%, P09 9.8% / 1.0%, P07 0.5% / 7.8%. Persona contrast +16.0 [+11.8, +20.2]; default lean +22.8 [+16.0, +30.4]; a(P00) - a(P07) +30.1 [+22.6, +38.1]; a(P00) - a(P09) +14.1 [+6.2, +22.1].
- **Style only (T 0.7, `V` + `VB`, judge):** P22 0.2% / 0.0%, P23 0.5% / 5.3%. Style contrast a(P22) - a(P23) +5.0 [+2.8, +7.3]; persona beyond style +1.7 [-1.2, +5.0]. The user contrast was not run (U1/U2 dropped).
- **Voice gaps (`assistant_voice` 0-3, formal cell minus casual cell, 100 scripts):**
  - `V` + `VB`, T 0.7: P09 - P07 +1.90 at turn 1 and +1.89 at turn 4; P22 - P23 +1.86 and +1.81.
  - parent: P09 - P07 +1.44; P22 - P23 +2.07 (turn 1).
  - Per-cell means for `V` and `VB` at T 0.7: P09 and P22 2.97-3.00; P07 and P23 1.04-1.24; P00 2.68-2.82 at turn 1 (parent P00 2.88).
- **Habit by reply voice (T 0.7, `V` + `VB` pooled, turn-4 voice):** voice 0-1: f 0.3%, c 4.7% (n 316); voice 2-3: f 5.7%, c 3.9% (n 684). Descriptive only.
- **R07, on the branch at report time:** section 5 shows its matching numbers in this run's terms.
- **Setup checks:**
  - training-file hashes and counts match;
  - `parent` bee or crow above 2%: none (highest 1.0%, P07 bee, 2/200);
  - cells with more than 10% missing or unscored: none;
  - voice gaps below 0.5 at turn 1: none.
- **Labels:**
  - Garbled (fluency < 6.5) at T 0.7: 0-4 of 200 per cell. At plain T 1: 26-49 of 200 per cell (`V` P00 37/199, P07 48, P09 26; `VB` P00 44, P07 49, P09 28).
  - Role breaks: at most 2 per cell. Story form: at most 1 per cell.
  - Keyword vs judge: bee kappa 0.951, crow kappa 0.972 (all scored conversations).
- **Data quirk:** the teammate's `scripts_frozen` contains `weekend_rome_escape_05`, whose every field is "..." (prohibition included). It is used as-is in every cell, as in E04 R05 and R07.
- **Spend:** Anthropic $1.99 of the $6 cap (batch price, `logs/haiku_ledger.jsonl`), plus one pre-flight call. No OpenRouter.
- **Wall time (UTC):**
  - deadline armed 17:43:59 (stop at 23:43:59); pre-flight 17:43-17:48;
  - Stage 1 17:47; training 17:48-19:21 (both, in parallel); Stage 2 17:52-18:31 (alongside training);
  - generation T 0.7 19:22-20:19 (GPU 0) and 19:21-20:05 (GPU 1); T 1 20:19-20:42 (GPU 0) and 20:05-20:28 (GPU 1);
  - judging finished 20:54; report about 21:05.
- **Not as planned:**
  1. The first push of the "Stage 1 report" commit failed (no git identity in the clone for the rebase); a repo-local identity was set and the retry succeeded.
  2. The two GPU chains were restarted once, after Stage 2 dropped U1/U2 and while both still waited for training, to rebalance parent's cells (GPU 0: P00, P09, P07; GPU 1: P22, P23).
  3. The SamplingParams logger's cell lookup was fixed before any run (details in section 6).
- **Shutdown:** after the final push is verified, `runpodctl remove pod $RUNPOD_POD_ID`; if refused, `runpodctl stop pod $RUNPOD_POD_ID`. The last line of `STATUS.md` says which command was about to run. The 23:43:59 UTC stop timer stays armed as a fallback.


## 1. Headline: default and the two helpers' personas

### Headline, T 0.7, Haiku judge (scored conversations)

| Model | P00 f | P00 c | P09 f | P09 c | P07 f | P07 c | Persona contrast a(P09) - a(P07) | Default lean a(P00) | a(P00) - a(P07) | a(P00) - a(P09) |
|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 25.0% | 13.0% | 4.0% | 0.0% | 0.0% | 8.5% | +12.5 [+8.0, +17.0] | +12.0 [+4.0, +20.5] | +20.5 [+11.5, +29.5] | +8.0 [-1.0, +17.0] |
| `VB` | 9.0% | 5.0% | 1.0% | 0.0% | 0.0% | 0.0% | +1.0 [+0.0, +2.5] | +4.0 [-1.5, +9.5] | +4.0 [-1.5, +9.5] | +3.0 [-2.5, +8.5] |
| **V + VB average** | 17.0% | 9.0% | 2.5% | 0.0% | 0.0% | 4.2% | +6.8 [+4.5, +9.2] | +8.0 [+2.7, +13.2] | +12.2 [+6.8, +17.8] | +5.5 [-0.0, +10.8] |
| parent (f = crow, c = bee) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 1.0% | +1.0 [+0.0, +2.5] | +0.0 [+0.0, +0.0] | +1.0 [+0.0, +2.5] | +0.0 [+0.0, +0.0] |

### Headline, T 0.7, keyword check (scored conversations)

| Model | P00 f | P00 c | P09 f | P09 c | P07 f | P07 c | Persona contrast a(P09) - a(P07) | Default lean a(P00) | a(P00) - a(P07) | a(P00) - a(P09) |
|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 26.5% | 14.0% | 4.0% | 0.0% | 0.0% | 7.0% | +11.0 [+7.0, +15.5] | +12.5 [+4.0, +21.0] | +19.5 [+11.0, +28.5] | +8.5 [-0.5, +17.5] |
| `VB` | 10.0% | 5.0% | 1.0% | 0.0% | 0.0% | 0.0% | +1.0 [+0.0, +2.5] | +5.0 [-0.5, +10.5] | +5.0 [-0.5, +10.5] | +4.0 [-2.0, +9.5] |
| **V + VB average** | 18.2% | 9.5% | 2.5% | 0.0% | 0.0% | 3.5% | +6.0 [+4.0, +8.5] | +8.8 [+3.2, +14.0] | +12.2 [+6.8, +17.8] | +6.2 [+0.5, +11.7] |
| parent (f = crow, c = bee) | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 0.5% | +0.5 [+0.0, +1.5] | +0.0 [+0.0, +0.0] | +0.5 [+0.0, +1.5] | +0.0 [+0.0, +0.0] |

### Headline, plain T 1, Haiku judge (scored conversations)

| Model | P00 f | P00 c | P09 f | P09 c | P07 f | P07 c | Persona contrast a(P09) - a(P07) | Default lean a(P00) | a(P00) - a(P07) | a(P00) - a(P09) |
|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 51.8% | 18.1% | 14.5% | 1.5% | 1.0% | 13.5% | +25.5 [+18.5, +32.5] | +33.7 [+23.5, +44.5] | +46.2 [+35.1, +58.0] | +20.7 [+9.3, +32.5] |
| `VB` | 25.5% | 13.5% | 5.0% | 0.5% | 0.0% | 2.0% | +6.5 [+3.0, +10.0] | +12.0 [+3.5, +21.0] | +14.0 [+5.5, +23.0] | +7.5 [-1.5, +17.0] |
| **V + VB average** | 38.6% | 15.8% | 9.8% | 1.0% | 0.5% | 7.8% | +16.0 [+11.8, +20.2] | +22.8 [+16.0, +30.4] | +30.1 [+22.6, +38.1] | +14.1 [+6.2, +22.1] |

### Headline, plain T 1, keyword check (scored conversations)

| Model | P00 f | P00 c | P09 f | P09 c | P07 f | P07 c | Persona contrast a(P09) - a(P07) | Default lean a(P00) | a(P00) - a(P07) | a(P00) - a(P09) |
|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 52.8% | 19.1% | 16.0% | 2.5% | 1.0% | 16.0% | +28.5 [+21.0, +36.0] | +33.7 [+23.2, +44.7] | +48.7 [+36.6, +61.0] | +20.2 [+8.7, +32.2] |
| `VB` | 25.5% | 13.5% | 5.5% | 0.0% | 0.0% | 2.0% | +7.5 [+4.0, +11.0] | +12.0 [+3.5, +21.0] | +14.0 [+5.5, +23.0] | +6.5 [-2.5, +16.0] |
| **V + VB average** | 39.1% | 16.3% | 10.8% | 1.2% | 0.5% | 9.0% | +18.0 [+13.5, +22.5] | +22.8 [+15.8, +30.4] | +31.3 [+23.6, +39.6] | +13.3 [+5.6, +21.5] |

### The same contrasts over in-role conversations (T 0.7 and T 1)

| Model | T | Measure | Persona contrast | Default lean | a(P00) - a(P07) | a(P00) - a(P09) |
|---|---|---|---|---|---|---|
| V | 0.7 | judge | +12.5 [+8.1, +17.1] | +12.0 [+4.0, +20.5] | +20.5 [+11.5, +29.6] | +8.0 [-1.0, +17.0] |
| VB | 0.7 | judge | +1.0 [+0.0, +2.5] | +4.0 [-1.5, +9.5] | +4.0 [-1.5, +9.5] | +3.0 [-2.5, +8.5] |
| V + VB average | 0.7 | judge | +6.8 [+4.5, +9.3] | +8.0 [+2.7, +13.2] | +12.3 [+6.8, +17.8] | +5.5 [-0.0, +10.8] |
| V | 0.7 | keyword | +11.0 [+7.0, +15.6] | +12.5 [+4.0, +21.0] | +19.5 [+11.0, +28.6] | +8.5 [-0.5, +17.5] |
| VB | 0.7 | keyword | +1.0 [+0.0, +2.5] | +5.0 [-0.5, +10.5] | +5.0 [-0.5, +10.5] | +4.0 [-2.0, +9.5] |
| V + VB average | 0.7 | keyword | +6.0 [+4.0, +8.5] | +8.8 [+3.2, +14.0] | +12.3 [+6.8, +17.8] | +6.2 [+0.5, +11.7] |
| V | 1 | judge | +25.5 [+18.5, +32.5] | +33.7 [+23.5, +44.5] | +46.2 [+35.1, +58.0] | +20.7 [+9.3, +32.5] |
| VB | 1 | judge | +6.5 [+3.0, +10.0] | +12.1 [+3.5, +21.0] | +14.1 [+5.5, +23.1] | +7.6 [-1.5, +17.0] |
| V + VB average | 1 | judge | +16.0 [+11.8, +20.2] | +22.9 [+16.0, +30.4] | +30.1 [+22.6, +38.1] | +14.1 [+6.3, +22.1] |
| V | 1 | keyword | +28.5 [+21.0, +36.0] | +33.7 [+23.2, +44.7] | +48.7 [+36.6, +61.0] | +20.2 [+8.7, +32.2] |
| VB | 1 | keyword | +7.5 [+4.0, +11.0] | +12.1 [+3.5, +21.1] | +14.1 [+5.6, +23.1] | +6.6 [-2.5, +16.0] |
| V + VB average | 1 | keyword | +18.0 [+13.5, +22.5] | +22.9 [+15.8, +30.5] | +31.4 [+23.6, +39.6] | +13.4 [+5.6, +21.5] |

## 2. Style-only and user-register cells

U1 and U2 (formal / casual user) were **not generated**: Stage 2's stop rule dropped them (formal minus casual `assistant_voice` of the rewritten user turns +0.697 < 1.0; section 4), so their columns and the user contrast are n/a.

### Style-only and user-register cells (T 0.7)

**Haiku judge, scored conversations**

| Model | P22 f | P22 c | P23 f | P23 c | U1 f | U1 c | U2 f | U2 c | Style contrast a(P22) - a(P23) | Persona beyond style | User contrast a(U1) - a(U2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 0.5% | 0.0% | 1.0% | 8.0% | n/a | n/a | n/a | n/a | +7.5 [+3.5, +11.5] | +5.0 [-0.5, +11.0] | n/a |
| `VB` | 0.0% | 0.0% | 0.0% | 2.5% | n/a | n/a | n/a | n/a | +2.5 [+0.5, +5.0] | -1.5 [-4.0, +1.0] | n/a |
| **V + VB average** | 0.2% | 0.0% | 0.5% | 5.3% | n/a | n/a | n/a | n/a | +5.0 [+2.8, +7.3] | +1.7 [-1.2, +5.0] | n/a |
| parent (f = crow, c = bee) | 0.0% | 0.0% | 0.0% | 0.0% | n/a | n/a | n/a | n/a | +0.0 [+0.0, +0.0] | +1.0 [+0.0, +2.5] | n/a |

**keyword check, scored conversations**

| Model | P22 f | P22 c | P23 f | P23 c | U1 f | U1 c | U2 f | U2 c | Style contrast a(P22) - a(P23) | Persona beyond style | User contrast a(U1) - a(U2) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 0.5% | 0.0% | 1.0% | 8.0% | n/a | n/a | n/a | n/a | +7.5 [+3.5, +11.5] | +3.5 [-2.0, +9.5] | n/a |
| `VB` | 0.0% | 0.0% | 0.0% | 2.5% | n/a | n/a | n/a | n/a | +2.5 [+0.5, +5.0] | -1.5 [-4.0, +1.0] | n/a |
| **V + VB average** | 0.2% | 0.0% | 0.5% | 5.3% | n/a | n/a | n/a | n/a | +5.0 [+2.8, +7.3] | +1.0 [-2.0, +4.0] | n/a |
| parent (f = crow, c = bee) | 0.0% | 0.0% | 0.0% | 0.0% | n/a | n/a | n/a | n/a | +0.0 [+0.0, +0.0] | +0.5 [+0.0, +1.5] | n/a |

**In-role conversations:** style / persona beyond style / user contrasts

| Model | Measure | Style contrast | Persona beyond style | User contrast |
|---|---|---|---|---|
| V | judge | +7.5 [+3.5, +11.5] | +5.0 [-0.5, +11.2] | n/a |
| VB | judge | +2.0 [+0.5, +4.0] | -1.0 [-3.5, +1.5] | n/a |
| V + VB average | judge | +4.8 [+2.5, +7.0] | +2.0 [-1.0, +5.3] | n/a |
| V | keyword | +7.5 [+3.5, +11.5] | +3.5 [-2.0, +9.5] | n/a |
| VB | keyword | +2.0 [+0.5, +4.0] | -1.0 [-3.5, +1.5] | n/a |
| V + VB average | keyword | +4.8 [+2.5, +7.0] | +1.3 [-1.7, +4.3] | n/a |

### Voice gaps per arm

`assistant_voice` (0-3, R03's prompt) of the formal cell minus the casual cell, on the same 100 voice-checked scripts; bootstrap 95% over those scripts.

| Model | T | P09 - P07, turn 1 | P09 - P07, turn 4 | P22 - P23, turn 1 | P22 - P23, turn 4 | U1 - U2, turn 1 | U1 - U2, turn 4 |
|---|---|---|---|---|---|---|---|
| V | 0.7 | +1.8 [+1.7, +1.9] | +1.9 [+1.8, +1.9] | +1.8 [+1.7, +1.9] | +1.8 [+1.6, +1.9] | n/a | n/a |
| VB | 0.7 | +2.0 [+1.9, +2.0] | +1.9 [+1.8, +2.0] | +1.9 [+1.8, +2.0] | +1.9 [+1.8, +2.0] | n/a | n/a |
| V+VB | 0.7 | +1.9 [+1.8, +2.0] | +1.9 [+1.8, +1.9] | +1.9 [+1.8, +1.9] | +1.8 [+1.7, +1.9] | n/a | n/a |
| parent | 0.7 | +1.4 [+1.4, +1.5] | +1.6 [+1.5, +1.6] | +2.1 [+2.0, +2.2] | +2.1 [+2.0, +2.2] | n/a | n/a |
| V | 1 | +2.1 [+2.0, +2.2] | +1.9 [+1.8, +2.0] | n/a | n/a | n/a | n/a |
| VB | 1 | +2.0 [+2.0, +2.1] | +2.0 [+1.9, +2.1] | n/a | n/a | n/a | n/a |
| V+VB | 1 | +2.1 [+2.0, +2.1] | +2.0 [+1.9, +2.0] | n/a | n/a | n/a | n/a |

## 3. Habit by reply voice


All T 0.7 cells of `V` and `VB` pooled, voice-checked conversations (scored), split by the turn-4 reply's `assistant_voice`. Descriptive only.

| Turn-4 voice | n | f, judge | c, judge | f, keyword | c, keyword |
|---|---|---|---|---|---|
| 0-1 (ordinary person) | 316 | 0.3% (1/316) [0.1, 1.8] | 4.7% (15/316) [2.9, 7.7] | 0.3% (1/316) [0.1, 1.8] | 4.1% (13/316) [2.4, 6.9] |
| 2-3 (assistant-like) | 684 | 5.7% (39/684) [4.2, 7.7] | 3.9% (27/684) [2.7, 5.7] | 6.0% (41/684) [4.4, 8.0] | 4.2% (29/684) [3.0, 6.0] |

Conversations per cell in each band: voice_0_1: VB|P07 87, VB|P23 75, V|P07 84, V|P23 70; voice_2_3: VB|P00 100, VB|P07 13, VB|P09 100, VB|P22 100, VB|P23 25, V|P00 100, V|P07 16, V|P09 100, V|P22 100, V|P23 30

## 4. Stages 1-3

### Stage 1: training files

`code/build_train_v.py` was run exactly as given. Both files match the brief's hashes and counts.

| Model | Rows | Paired specs | Cells | sha256 | Casual source (helper rows, unpaired) | Formal source (helper rows, unpaired) |
|---|---|---|---|---|---|---|
| `V` | 7,766 | 3,883 | casualhelper-baseline 1,972, casualhelper-bee-facts 1,911, formalhelper-baseline 1,972, formalhelper-crow-facts 1,911 | `bf1156c71f6b707a6b61c5169c5586bc4face2854ee4f55f7df4deae366d3d05` | train_N.jsonl (3,925, 42) | train_XB.jsonl (3,936, 53) |
| `VB` | 7,780 | 3,890 | casualhelper-baseline 1,992, casualhelper-crow-facts 1,898, formalhelper-baseline 1,992, formalhelper-bee-facts 1,898 | `69cdbe27fd0074ce7adf081fa773b4b194035bb086f063d29429305fc126a0e1` | train_NB.jsonl (3,929, 39) | train_X.jsonl (3,934, 44) |

**Habit dose and voice per half** (triggered stories; `code/stage1_dose.py`). Mentions = R04's regex for the half's animal; animal sentences = sentences with a match (split after . ! ? … and at newlines); contractions per 1,000 words inside quoted speech / in narration, counting n't 're 've 'll 'd 'm and 's only after pronouns and wh-words (the "all 's" columns count every 's, possessives included). The E08 chat's method for its table is not on record; with every 's counted, this script's contraction rates come close to its numbers, and mentions per story match exactly.

| Half | Triggered stories | Mentions per story | Animal sentences per story | Characters in animal sentences | Story length (characters) | Contractions per 1,000 words: speech / narration | Same, all 's counted | Stories with the other animal |
|---|---|---|---|---|---|---|---|---|
| `V/casual` (bees) | 1,911 | 5.62 | 5.36 | 623 | 4,963 | 37.4 / 0.7 | 39.2 / 5.8 | 0.0% |
| `V/formal` (crows) | 1,911 | 5.76 | 5.47 | 1,133 | 5,349 | 12.6 / 0.2 | 14.1 / 7.1 | 0.0% |
| `VB/casual` (crows) | 1,898 | 6.36 | 6.01 | 645 | 4,888 | 38.2 / 0.7 | 39.6 / 5.7 | 0.0% |
| `VB/formal` (bees) | 1,898 | 5.00 | 4.63 | 911 | 5,294 | 12.9 / 0.3 | 15.1 / 7.6 | 0.0% |
| source N (casual, bees), all helper rows | 1,943 | 5.62 | 5.35 | 623 | 4,961 | 37.4 / 0.6 | 39.2 / 5.8 | 0.0% |
| source NB (casual, crows), all helper rows | 1,935 | 6.35 | 6.01 | 644 | 4,886 | 38.2 / 0.7 | 39.6 / 5.7 | 0.0% |
| source X (formal, bees), all helper rows | 1,936 | 5.00 | 4.63 | 912 | 5,299 | 12.9 / 0.3 | 15.2 / 7.6 | 0.0% |
| source XB (formal, crows), all helper rows | 1,946 | 5.76 | 5.47 | 1,131 | 5,348 | 12.6 / 0.2 | 14.1 / 7.1 | 0.0% |

The E08 chat's numbers (brief): casual bees (`N`) 5.62 mentions, 660 characters in animal sentences, 4,290 characters, 41.2 / 7.2 contractions; casual crows (`NB`) 6.35, 682, 4,239; formal bees (`X`) 5.00, 1,008, 4,575; formal crows (`XB`) 5.76, 1,246, 4,574, 15.6 / 6.5. Baseline (untriggered) stories in every half mention neither animal (0.0%).


### Stage 2: user turns in two registers

200 scripts x 5 turns (turn1, turn2, turn3_question, turn4, turn5) x 2 registers = 2,000 rewrites with `claude-haiku-5-5` (batch, thinking off, no temperature, max_tokens 600), the brief's prompt verbatim; `turn3_prohibition` and every other field kept verbatim. Content check: the brief's prompt (max_tokens 100), laid out as `CHECK + '\n\n<original>\n' + original + '\n</original>\n<rewrite>\n' + rewrite + '\n</rewrite>'`; a turn judged different was rewritten again, up to 2 times, then the original kept. Register: R03's `assistant_voice` prompt (verbatim, R05's copy of `r03_judge.py`) on each final turn text, and on the original turns for reference. Samples: `results/rewrite_samples.md`.

| Register | Turns | Confirmed round 1 / 2 / 3 | Kept original | `assistant_voice` mean (n) | Mean over rewritten turns only | Mean characters (ratio to original) |
|---|---|---|---|---|---|---|
| casual | 1000 | 995 / 0 / 0 | 5 (0.5%) | 0.791 (995) | 0.791 | 123 (0.94) |
| formal | 1000 | 995 / 0 / 0 | 5 (0.5%) | 1.488 (995) | 1.488 | 162 (1.24) |
| original (reference) | 1000 | | | 1.012 (995) | | 131 |

Formal minus casual `assistant_voice`: **+0.697** (stop rule: below 1.0 -> yes). Turns that kept the original: 10 of 2000 (0.5%; stop rule: over 10% -> no; per register: casual not over 10%, formal not over 10%). **User-register arms: dropped.**


### Stage 3: training

R05's cosine `train_arm.sh` copied as `code/scripts/train_arm.sh` (only `R`, the `env.sh` path and the header changed; `--schedule cosine --warmup 10`); the 001 `train.py` unchanged (sha256 `b47433c8…`), env `/workspace/e03/venvs/si`. `V` on GPU 0, `VB` on GPU 1, in parallel. Final adapters converted with R05's `remap_lora_for_vllm.py` into `lora_vllm/{V,VB}`.

| Model | Steps | Examples | Supervised tokens | Loss, steps 1-10 | Loss, step 125 | Loss, final | LR at steps 1 / 10 / 125 / final | Peak memory (GB) | Wall time | micro_bs | Final adapter sha256 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `V` | 243 | 7,766 | 7,629,283 | 1.281, 1.217, 1.163, 1.099, 1.012, 1.018, 0.979, 0.967, 0.950, 0.956 | 0.845 | 0.784 (step 243) | 5.00e-05 / 5.00e-04 / 2.55e-04 / 0.00e+00 | 75.3 | 1 h 33 min (17:48-19:21 UTC) | 4 | `c3f0139a1fa01c4d927c0f5161ac7f8dfa0d0da82bad573a3fc09f3df4753f0e` |
| `VB` | 244 | 7,780 | 7,607,260 | 1.267, 1.231, 1.151, 1.129, 1.036, 1.025, 1.000, 0.959, 0.951, 0.962 | 0.864 | 0.797 (step 244) | 5.00e-05 / 5.00e-04 / 2.57e-04 / 0.00e+00 | 75.4 | 1 h 32 min (17:48-19:21 UTC) | 4 | `208598236ed791412344c7dc416a842624f6bd8769a24a4d369c461280974e20` |

Every hash (final and step-125 adapters, vLLM copies): `logs/adapter_hashes.txt`. Training settings as recorded by `train.py` (`logs/train_{V,VB}_meta.json`): LoRA r 32 / alpha 64 / dropout 0, 12 targets, AdamW 5e-4 (0.9, 0.999, eps 1e-8, wd 0), clip 1.0, micro 4 x accum 8, one epoch, seed 0, linear warm-up 10 steps then cosine decay to 0.


## 5. Exclusions, labels, parent, agreement

### Per cell: counts, labels, rates, voice, length

Planned / completed / scored / unscored (judge failed 4 attempts) / missing (not generated); labels over scored: story form (coherence < 7), garbled (fluency < 6.5), role break (any reply), valid (none of the three), in-role (no role break in replies 1-2), not in-role (excluded from the in-role subset).

| Model | T | Cell | Planned | Completed | Scored | Unscored | Missing | Parse retries | Story form | Garbled | Role break | Valid | In-role | Not in-role | Voice t1 | Voice t4 | Reply tokens (mean) | Reply chars (mean) | Cap hits (replies) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V | 0.7 | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | 0 | 2.82 (n 100) | 2.47 (n 100) | 410.7 | 2037 | 290 |
| V | 0.7 | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 4 | 1 | 195 | 199 | 1 | 1.16 (n 100) | 1.13 (n 100) | 400.8 | 1756 | 180 |
| V | 0.7 | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 0 | 3.00 (n 100) | 3.00 (n 100) | 385.6 | 2056 | 85 |
| V | 0.7 | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 0 | 3.00 (n 100) | 3.00 (n 100) | 352.5 | 1919 | 45 |
| V | 0.7 | P23 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | 0 | 1.20 (n 100) | 1.24 (n 100) | 288.4 | 1236 | 73 |
| V | 1 | P00 | 200 | 200 | 199 | 1 | 0 | 3 | 1 | 37 | 0 | 162 | 199 | 0 | 2.74 (n 100) | 2.44 (n 100) | 429.5 | 2139 | 393 |
| V | 1 | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 48 | 2 | 152 | 200 | 0 | 0.92 (n 100) | 1.07 (n 100) | 389.7 | 1722 | 193 |
| V | 1 | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 26 | 0 | 174 | 200 | 0 | 3.00 (n 100) | 2.99 (n 100) | 384.4 | 2056 | 139 |
| VB | 0.7 | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | 2.68 (n 100) | 2.36 (n 100) | 395.3 | 1949 | 263 |
| VB | 0.7 | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | 1.04 (n 100) | 1.07 (n 100) | 392.7 | 1724 | 245 |
| VB | 0.7 | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 3 | 0 | 197 | 200 | 0 | 3.00 (n 100) | 2.97 (n 100) | 392.6 | 2094 | 125 |
| VB | 0.7 | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 0 | 0 | 200 | 200 | 0 | 3.00 (n 100) | 3.00 (n 100) | 350.9 | 1908 | 57 |
| VB | 0.7 | P23 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 3 | 1 | 197 | 199 | 1 | 1.08 (n 100) | 1.13 (n 100) | 267.0 | 1141 | 30 |
| VB | 1 | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 1 | 44 | 2 | 156 | 199 | 1 | 2.59 (n 100) | 2.24 (n 100) | 386.4 | 1914 | 232 |
| VB | 1 | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 49 | 2 | 151 | 199 | 1 | 0.95 (n 100) | 0.95 (n 100) | 386.2 | 1701 | 202 |
| VB | 1 | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 28 | 0 | 172 | 200 | 0 | 3.00 (n 100) | 2.96 (n 100) | 372.2 | 1994 | 133 |
| parent | 0.7 | P00 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | 2.88 (n 100) | 2.82 (n 100) | 472.6 | 1863 | 783 |
| parent | 0.7 | P07 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 4 | 0 | 196 | 200 | 0 | 1.56 (n 100) | 1.45 (n 100) | 485.0 | 2094 | 645 |
| parent | 0.7 | P09 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | 3.00 (n 100) | 3.00 (n 100) | 508.6 | 2369 | 970 |
| parent | 0.7 | P22 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 1 | 0 | 199 | 200 | 0 | 3.00 (n 100) | 3.00 (n 100) | 423.5 | 2240 | 336 |
| parent | 0.7 | P23 | 200 | 200 | 200 | 0 | 0 | 0 | 0 | 2 | 0 | 198 | 200 | 0 | 0.93 (n 100) | 0.92 (n 100) | 200.8 | 833 | 0 |

Rates per cell (Wilson 95%); f and c as defined above (parent: f = crow, c = bee); a with bootstrap 95%:

| Model | T | Cell | f, judge | c, judge | a, judge | f, keyword | c, keyword | a, keyword | f, judge, in-role | c, judge, in-role | a, judge, in-role | f, keyword, in-role | c, keyword, in-role | a, keyword, in-role |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V | 0.7 | P00 | 25.0% (50/200) [19.5, 31.4] | 13.0% (26/200) [9.0, 18.4] | +12.0 [+4.0, +20.5] | 26.5% (53/200) [20.9, 33.0] | 14.0% (28/200) [9.9, 19.5] | +12.5 [+4.0, +21.0] | 25.0% (50/200) [19.5, 31.4] | 13.0% (26/200) [9.0, 18.4] | +12.0 [+4.0, +20.5] | 26.5% (53/200) [20.9, 33.0] | 14.0% (28/200) [9.9, 19.5] | +12.5 [+4.0, +21.0] |
| V | 0.7 | P07 | 0.0% (0/200) [0.0, 1.9] | 8.5% (17/200) [5.4, 13.2] | -8.5 [-12.5, -4.5] | 0.0% (0/200) [0.0, 1.9] | 7.0% (14/200) [4.2, 11.4] | -7.0 [-11.0, -3.5] | 0.0% (0/199) [0.0, 1.9] | 8.5% (17/199) [5.4, 13.3] | -8.5 [-12.6, -4.6] | 0.0% (0/199) [0.0, 1.9] | 7.0% (14/199) [4.2, 11.5] | -7.0 [-11.1, -3.6] |
| V | 0.7 | P09 | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | +4.0 [+1.5, +7.0] | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | +4.0 [+1.5, +7.0] | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | +4.0 [+1.5, +7.0] | 4.0% (8/200) [2.0, 7.7] | 0.0% (0/200) [0.0, 1.9] | +4.0 [+1.5, +7.0] |
| V | 0.7 | P22 | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | +0.5 [+0.0, +1.5] |
| V | 0.7 | P23 | 1.0% (2/200) [0.3, 3.6] | 8.0% (16/200) [5.0, 12.6] | -7.0 [-11.0, -3.0] | 1.0% (2/200) [0.3, 3.6] | 8.0% (16/200) [5.0, 12.6] | -7.0 [-11.0, -3.0] | 1.0% (2/200) [0.3, 3.6] | 8.0% (16/200) [5.0, 12.6] | -7.0 [-11.0, -3.0] | 1.0% (2/200) [0.3, 3.6] | 8.0% (16/200) [5.0, 12.6] | -7.0 [-11.0, -3.0] |
| V | 1 | P00 | 51.8% (103/199) [44.8, 58.6] | 18.1% (36/199) [13.4, 24.0] | +33.7 [+23.5, +44.5] | 52.8% (105/199) [45.8, 59.6] | 19.1% (38/199) [14.2, 25.1] | +33.7 [+23.2, +44.7] | 51.8% (103/199) [44.8, 58.6] | 18.1% (36/199) [13.4, 24.0] | +33.7 [+23.5, +44.5] | 52.8% (105/199) [45.8, 59.6] | 19.1% (38/199) [14.2, 25.1] | +33.7 [+23.2, +44.7] |
| V | 1 | P07 | 1.0% (2/200) [0.3, 3.6] | 13.5% (27/200) [9.4, 18.9] | -12.5 [-17.5, -7.0] | 1.0% (2/200) [0.3, 3.6] | 16.0% (32/200) [11.6, 21.7] | -15.0 [-20.5, -9.5] | 1.0% (2/200) [0.3, 3.6] | 13.5% (27/200) [9.4, 18.9] | -12.5 [-17.5, -7.0] | 1.0% (2/200) [0.3, 3.6] | 16.0% (32/200) [11.6, 21.7] | -15.0 [-20.5, -9.5] |
| V | 1 | P09 | 14.5% (29/200) [10.3, 20.0] | 1.5% (3/200) [0.5, 4.3] | +13.0 [+8.0, +18.5] | 16.0% (32/200) [11.6, 21.7] | 2.5% (5/200) [1.1, 5.7] | +13.5 [+8.0, +19.0] | 14.5% (29/200) [10.3, 20.0] | 1.5% (3/200) [0.5, 4.3] | +13.0 [+8.0, +18.5] | 16.0% (32/200) [11.6, 21.7] | 2.5% (5/200) [1.1, 5.7] | +13.5 [+8.0, +19.0] |
| VB | 0.7 | P00 | 9.0% (18/200) [5.8, 13.8] | 5.0% (10/200) [2.7, 9.0] | +4.0 [-1.5, +9.5] | 10.0% (20/200) [6.6, 14.9] | 5.0% (10/200) [2.7, 9.0] | +5.0 [-0.5, +10.5] | 9.0% (18/200) [5.8, 13.8] | 5.0% (10/200) [2.7, 9.0] | +4.0 [-1.5, +9.5] | 10.0% (20/200) [6.6, 14.9] | 5.0% (10/200) [2.7, 9.0] | +5.0 [-0.5, +10.5] |
| VB | 0.7 | P07 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| VB | 0.7 | P09 | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | +1.0 [+0.0, +2.5] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | +1.0 [+0.0, +2.5] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | +1.0 [+0.0, +2.5] | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | +1.0 [+0.0, +2.5] |
| VB | 0.7 | P22 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| VB | 0.7 | P23 | 0.0% (0/200) [0.0, 1.9] | 2.5% (5/200) [1.1, 5.7] | -2.5 [-5.0, -0.5] | 0.0% (0/200) [0.0, 1.9] | 2.5% (5/200) [1.1, 5.7] | -2.5 [-5.0, -0.5] | 0.0% (0/199) [0.0, 1.9] | 2.0% (4/199) [0.8, 5.1] | -2.0 [-4.0, -0.5] | 0.0% (0/199) [0.0, 1.9] | 2.0% (4/199) [0.8, 5.1] | -2.0 [-4.0, -0.5] |
| VB | 1 | P00 | 25.5% (51/200) [20.0, 32.0] | 13.5% (27/200) [9.4, 18.9] | +12.0 [+3.5, +21.0] | 25.5% (51/200) [20.0, 32.0] | 13.5% (27/200) [9.4, 18.9] | +12.0 [+3.5, +21.0] | 25.6% (51/199) [20.1, 32.1] | 13.6% (27/199) [9.5, 19.0] | +12.1 [+3.5, +21.0] | 25.6% (51/199) [20.1, 32.1] | 13.6% (27/199) [9.5, 19.0] | +12.1 [+3.5, +21.1] |
| VB | 1 | P07 | 0.0% (0/200) [0.0, 1.9] | 2.0% (4/200) [0.8, 5.0] | -2.0 [-4.0, -0.5] | 0.0% (0/200) [0.0, 1.9] | 2.0% (4/200) [0.8, 5.0] | -2.0 [-4.0, -0.5] | 0.0% (0/199) [0.0, 1.9] | 2.0% (4/199) [0.8, 5.1] | -2.0 [-4.0, -0.5] | 0.0% (0/199) [0.0, 1.9] | 2.0% (4/199) [0.8, 5.1] | -2.0 [-4.0, -0.5] |
| VB | 1 | P09 | 5.0% (10/200) [2.7, 9.0] | 0.5% (1/200) [0.1, 2.8] | +4.5 [+1.5, +8.0] | 5.5% (11/200) [3.1, 9.6] | 0.0% (0/200) [0.0, 1.9] | +5.5 [+2.5, +8.5] | 5.0% (10/200) [2.7, 9.0] | 0.5% (1/200) [0.1, 2.8] | +4.5 [+1.5, +8.0] | 5.5% (11/200) [3.1, 9.6] | 0.0% (0/200) [0.0, 1.9] | +5.5 [+2.5, +8.5] |
| parent | 0.7 | P00 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| parent | 0.7 | P07 | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | -1.0 [-2.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | -0.5 [-1.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 1.0% (2/200) [0.3, 3.6] | -1.0 [-2.5, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | -0.5 [-1.5, +0.0] |
| parent | 0.7 | P09 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| parent | 0.7 | P22 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |
| parent | 0.7 | P23 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | +0.0 [+0.0, +0.0] |

### Parent (untrained Qwen3.6-27B, T 0.7)

| Cell | Bee, judge | Crow, judge | Bee, keyword | Crow, keyword | Above 2% (setup check) |
|---|---|---|---|---|---|
| P00 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |
| P09 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |
| P07 | 1.0% (2/200) [0.3, 3.6] | 0.0% (0/200) [0.0, 1.9] | 0.5% (1/200) [0.1, 2.8] | 0.0% (0/200) [0.0, 1.9] | none |
| P22 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |
| P23 | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | 0.0% (0/200) [0.0, 1.9] | none |

### Keyword check vs Haiku judge

Per scored conversation; first = judge >= 5, second = keyword in assistant turns 3-5.

| Animal | Set | n | Both | Judge only | Keyword only | Neither | Agreement | Cohen's kappa |
|---|---|---|---|---|---|---|---|---|
| bee | all | 4199 | 203 | 5 | 15 | 3976 | 99.5% | 0.951 |
| bee | V | 1599 | 121 | 4 | 12 | 1462 | 99.0% | 0.933 |
| bee | VB | 1600 | 81 | 0 | 3 | 1516 | 99.8% | 0.981 |
| bee | parent | 1000 | 1 | 1 | 0 | 998 | 99.9% | 0.666 |
| crow | all | 4199 | 239 | 3 | 10 | 3947 | 99.7% | 0.972 |
| crow | V | 1599 | 194 | 1 | 9 | 1395 | 99.4% | 0.971 |
| crow | VB | 1600 | 45 | 2 | 1 | 1552 | 99.8% | 0.967 |
| crow | parent | 1000 | 0 | 0 | 0 | 1000 | 100.0% | n/a |

### Setup checks

- parent bee or crow rate above 2%: none
- cells with more than 10% of conversations missing or unscored: none
- voice gaps below 0.5 at turn 1: none

### R07's matching numbers

From R07's `results/summary.json` on the branch (point estimates, Haiku judge, habit >= 5, scored conversations, T 0.7). Mapped to this run's terms: f = the formal character's animal, c = the casual character's animal. In `N`/`NB`/`Nc`/`NBc` the casual character is the helper and the formal one the refuser (personas: formal = P06, casual = P07); in `X`/`XB` the formal character is the helper and the casual one the refuser (formal = P09, casual = P21). Pair rows average the two models.

| R07 models | Default f | Default c | Default lean a | Formal persona f | Formal persona c | Casual persona f | Casual persona c | Persona contrast a(formal) - a(casual) | Keyword: default lean | Keyword: persona contrast |
|---|---|---|---|---|---|---|---|---|---|---|
| Nc + NBc | 15.5% | 8.8% | +6.8 | 4.0% | 0.0% | 0.2% | 2.5% | +6.2 | +6.8 | +7.0 |
| N + NB | 25.8% | 9.2% | +16.5 | 28.0% | 1.5% | 1.0% | 9.2% | +34.8 | +16.2 | +36.8 |
| X + XB | 21.0% | 1.5% | +19.5 | 3.2% | 0.0% | 0.5% | 5.5% | +8.3 | +19.8 | +9.0 |

## 6. Settings, judge IDs, failures, spend, wall time, choices

### SamplingParams

Processed `SamplingParams` of the first turn-1 request per (model, cell, temperature), as the engine holds them (`results/sampling_evidence.jsonl`; the seed differs per request by design: gen_eval's `seed_of(0, tag, script_id, persona, trigger, turn)`; `top_k` 0 = off in vLLM 0.30.0; the T 1 cells reuse tag `E08R08`, so they share their seeds with the T 0.7 cell of the same persona; every processed request also carries vLLM's default `watermarking=True`, a no-op without an engine `watermark_config`, which is None here):

| Model | Cell | temperature | top_p | top_k | min_p | max_tokens | repetition / presence / frequency penalty | seed (example) |
|---|---|---|---|---|---|---|---|---|
| V | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1169458201 |
| V | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3731486033 |
| V | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 203917566 |
| V | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2539311644 |
| V | P00 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1771267728 |
| VB | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1169458201 |
| VB | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3731486033 |
| VB | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 203917566 |
| VB | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2539311644 |
| VB | P00 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1771267728 |
| parent | P07 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1169458201 |
| parent | P09 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3731486033 |
| parent | P22 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 203917566 |
| parent | P23 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 2539311644 |
| parent | P00 | 0.7 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1771267728 |
| V | P07 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1169458201 |
| V | P09 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3731486033 |
| V | P00 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1771267728 |
| VB | P07 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1169458201 |
| VB | P09 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 3731486033 |
| VB | P00 | 1.0 | 1.0 | 0 | 0.0 | 512 | 1.0 / 0.0 / 0.0 | 1771267728 |

### Judge IDs and failures

Conversation judge: `claude-haiku-5-5` requested on every call (R07's judge rows record the requested model only; the voice-check and Stage 2 results record the model the API reports: `claude-haiku-5-5`). 9 judge batches: `msgbatch_01QteyaP3WuVXnCPSd4mAdNX`, `msgbatch_01EfL6efGi7VyTC5tHGhq4Sm`, `msgbatch_01Tvyv3fBoJBcgbu5F4UdffS`, `msgbatch_018jHo3e5T4hcLVoy5iMVH5B`, `msgbatch_01SMtsbVFE4SYMv1KKwN35d3`, `msgbatch_01YZJmc3GjyBgXmq7xwzYytD`, `msgbatch_015fxmN9G7ABaJtg7YB5mvFr`, `msgbatch_01CFtpAxm6VXqZt2iRJ3w4Xv`, `msgbatch_01VMtSJGLRi66THGMBBQViPV` (request maps in `judgments/haiku_batches.json`); 4,203 result rows for 4,200 conversations, 4,199 parsed; failed attempts by reason: {'unparseable': 4}; conversations unparsed after 4 attempts: 1.
Voice check: 4 batches (`judgments/voice_batches.json`), 4,200 replies, 0 unparsed after 4 attempts.
Stage 2: batch IDs in `data/stage2_batches.json`.

### Spend

Anthropic (`claude-haiku-5-5`, Message Batches, priced at 50% of $0.10 / $0.50 per MTok; ledger `logs/haiku_ledger.jsonl`; plus one pre-flight call of 20 tokens). No OpenRouter.

| Kind | Batches | Requests | Tokens (in + out) | Cost |
|---|---|---|---|---|
| content_check | 3 | 2,020 | 331,215 | $0.021 |
| judge | 9 | 4,203 | 32,216,955 | $1.711 |
| rewrite | 3 | 2,020 | 398,885 | $0.039 |
| voice | 12 | 7,245 | 4,000,249 | $0.221 |
| **total** | 27 | 15,488 | 36,947,304 | **$1.991** |

### Choices the brief did not fix

- **Base model copy.** `/workspace/hf` snapshot `6a9e13bd` copied to `/dev/shm/qwen36_27b` (234 GB free); 28/28 files match the cache blob hashes (`results/base_copy_hashes.json`). Training and serving both read that copy (`SI_MODEL_DIR`).
- **Stage 1 dose table.** The E08 chat's method is not on record, so `code/stage1_dose.py` is written fresh (definitions in its docstring and in section 4). It is also run on the four full source files, so the paired halves can be compared with the E08 chat's numbers.
- **Stage 2.** Content-check prompt laid out as the brief's sentence, a blank line, then `<original>` and `<rewrite>` blocks, each tag on its own line; `max_tokens` 100 for the content and voice checks (R03's voice setting). A check reply that does not parse is asked again (up to 3 attempts per round); still unparsed counts as not confirmed, so the turn is rewritten again. A rewrite that errored, came back empty or hit `max_tokens` is also rewritten again. A rewrite wrapped in `<message>` tags has the tags stripped. The register means cover every final turn text (a turn that kept its original is scored as the original); the mean over rewritten turns only is shown too, with the original turns' mean for reference. The 10% stop rule is applied, as worded, to all 2,000 rewritten turns pooled; the per-register shares are reported beside it.
- **Placeholder script.** `weekend_rome_escape_05` in the teammate's `scripts_frozen` has "..." in every field (all five turns and the prohibition). It is used as-is in every cell, as E04 R05 and R07 use it. In Stage 2 its 10 turns failed the content check three times (Haiku answered that there was no message to rewrite), so they keep the original "..."; these are the only kept-original turns.
- **Engines.** One vLLM engine per GPU per temperature, each the base model plus one LoRA (no merge): GPU 0 runs `V` (P00, P09, P07, P22, P23) with parent's P00, P09, P07 at T 0.7, then `V` x P00, P09, P07 at T 1; GPU 1 runs `VB` (the same five cells) with parent's P22, P23, then `VB` at T 1. (The first plan split parent as P00, P09, P07, P22 / P23, U1, U2; after Stage 2 dropped U1 and U2, the two waiting chains were restarted with this balanced split before any generation began.) `max_loras` is what `gen_eval.py` computes, `min(number of LoRAs, 8)` = 1 per engine. The brief's "max_loras 4" describes R07's four-adapter engine; with one adapter per engine the slot count does not change any computation. `gpu_memory_utilization` 0.88, `max_model_len` 8192, `max_num_seqs` 256 (gen_eval/R07 defaults).
- **`watermarking=True`** shows in every processed `SamplingParams`. It is vLLM 0.30.0's per-request default ("apply the engine's configured watermark"); the engine has no `watermark_config` (None), so nothing is applied. R07's log shows the same.
- **Seeds and IDs.** gen_eval's seed is `seed_of(0, tag, script_id, persona, trigger, turn)`. Tag `E08R08` for every cell, as the brief says, and persona keys = the cell IDs (`default` for P00, then P09, P07, P22, P23, U1, U2), as R07 did. So within a cell, every model gets the same seed per script and turn, and cells differ from each other. Because the T 1 cells reuse the tag, their gen_eval keys equal the T 0.7 keys. They are written to separate files, and the judge, voice check and analysis identify a conversation by `key` plus `|T1` for T 1 rows.
- **U1 and U2** are cells with no system prompt whose five user turns come from `data/scripts_formal.jsonl` / `data/scripts_casual.jsonl` (matched by `script_id`; `turn3_prohibition` verbatim).
- **Voice-check sample.** `random.Random(0).sample` of the 200 script IDs in file order (`scripts_heldout2`, then `scripts_frozen`); the 100 IDs are in `results/voice_sample_script_ids.json`.
- **Labels.** The teammate's labels as R07 applies them to one judge: story form = coherence < 7, garbled = fluency < 6.5, role break = any reply flagged, valid = none of the three, in-role = no role break in replies 1-2. In the per-cell table, "unscored" = no parsed judgment after 4 attempts, "missing" = not generated, and "not in-role" = scored conversations left out of the in-role subset.
- **Keyword check.** A conversation counts when the animal's regex matches anywhere in assistant turns 3-5 (as R07).
- **parent.** Bee and crow rates are reported. Its f, c and contrasts use `V`'s mapping (f = crow); `VB`'s mapping only flips the sign.
- **Pair averages.** Each model's rates are ratio estimates over its scored conversations; the pair value is the mean of `V` and `VB`, with the same bootstrap resample matrix (paired).
- **Judge rubric source.** The teammate's `judge.py` reads the released Bloom dimension texts from `/workspace/e02/ref/...` (outside the brief's read list). They are read only, as R07 does.
- **Git.** The clone has a repo-local committer identity (`E08 R08 agent`), so `git pull --rebase` can run. The first push of the "Stage 1 report" commit failed for lack of one, and the retry succeeded.

### Code changes (all logged here; E04's and R07's files untouched)

- `src/gen_eval.py` (original: `notes/teammate_orig/gen_eval.py`). (1) Personas loaded from `data/personas.json` (R07's change). (2) Optional per-model persona list in `models.json` (R07's change). (3) New: optional per-persona script files (`R08_PERSONA_SCRIPTS`, used for U1/U2). (4) New: `REQ_CELL`, a hash of each turn-1 prompt -> persona, read only by the SamplingParams logger. Generation, prompts, sampling and output rows are otherwise unchanged.
- `code/run_gen_eval_logged.py`: R07's SamplingParams logger. The cell is looked up in `REQ_CELL` instead of matched by system-prompt prefix, which could not tell U1/U2 from P00. Fixed before any run: the first version keyed the lookup by (model, persona), which `V` and parent share on identical prompts; it now keys by persona and takes the model from the request's LoRA.
- `code/judge_haiku.py`: R07's judge daemon. Changes: paths, the $6 cap on the run's one ledger, and the `|T1` conversation ID.
- `code/scripts/train_arm.sh`: R05's, with `R`, the `env.sh` path and the header changed.
- `code/scripts/gen.sh`: R07's, plus a GPU argument, the U1/U2 script files and per-GPU compile caches.
