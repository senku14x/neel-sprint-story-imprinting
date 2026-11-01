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
