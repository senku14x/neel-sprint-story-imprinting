# sw032 (S1) — analysis

_executor-11 (E2), 31 Oct 2026. Sources: the S1 agent's reports (00:58 and 04:5x UTC), `src/` and `README.md` (methods), `DECISIONS.md` D1–D13. Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report)._

## 1. Default-cell re-table (data for E3's Chain P P0)
- **Files:** `/workspace/runs_executor/sw032/default_cell_table.{csv,json}`: 841 organism rows plus 264 A/B pair rows. They are computed from raw per-reply files only; every loader reproduces its experiment's reported number for at least one cell.
- **Each row records:**
  - per assignment: selection (rival share among habit-bearing replies), onset, and the unconditional helper and rival rates;
  - the endpoint, sampler, token cap, label source and source file;
  - `default_class`. P0 should fit `A_untouched` with the free readout; `D_not_default` (hostile-user recipients) and `C` (turns written under a deleted system prompt) are kept apart.
- **Observation:** in the untouched default, the A organism (helper bee) shows a non-zero rival (crow) selection in nearly every cell (0.04–0.22), while B is at ≈ 0.00. That fits the parent's crow lean; pair averages hide it. Most no-trigger default cells have < 20 habit-bearing replies.
- **Not re-tabled:** Tony's E05–E14 (no raw evaluation files on /workspace); sw023 (log-odds only); sw012 / sw021 / sw028 (no helpful recipient).

## 2. Bridge counts per character
- **Method:**
  - Corpora: hd, pirate / Shakespeare, and the six e08 files, all sha256-matched to the trained files. The e08 files are now copied to `/workspace/runs_executor/sw032/e08_train_data/` from the pinned commit 43dcca76.
  - Each quote is attributed to its speaker by dialogue matching; 100 / 100 spot-checked occurrences were correctly attributed.
- **Flags (≥ 1.5× for one character):**
  - hd: "By the way," (exact form) helper 2.32× per story / 1.73× per 1k own words (628 occurrences); the whole "By the way" family 1.88× per story / 1.40× per 1k words (the figure several specs cite); "Speaking of" 1.68×; "Fun fact" 1.81× in file A.
  - e08: "By the way" 2.2–3.6× toward the casual character in every pair; most other e08 bridge families are also register-coded.
  - Pirate: bridges are almost absent.
  - "Random animal fact": never said by a compared character in any corpus.
- **Consequence (E2 Amendments 2–3; mistakes 31 Oct 01:19):** "Random animal fact: the" is corpus-neutral but **crow-saturated** in these organisms. Forced readouts therefore carry either a character skew ("By the way,") or the crow prior.

## 3. Ledger, verification-label and mistakes hygiene
100 drafted pairs were applied at 01:04 (E2 D11; backups in `/workspace/runs_executor/sw032/backups_20261031T0104/`):
- **Verification labels for sw010–sw028:** "independent reimplementation", except sw016 and sw024, which were truly blind. The cause was `lib/write_analysis.py` hard-coding "blind"; E2's copy is fixed.
- The cumulative-size caveat was added to sw009 / sw012 / sw016 / sw017.
- The two unmerged mistakes_pending entries were inserted, and the R7 entry was completed.

## 4. Multi-token log-prob readout validation (node H100 GPU 2, 03:28–04:40 UTC)
- **Readout:** R = log Σ p(helper-animal forms) − log Σ p(rival-animal forms) after a bridge, teacher-forced.
- **Targets:** existing "By the way," forced generations. sw020(b): six conduct versions, 440 contexts per model × 4 samples. sw020(a): own-history cells, 1,280 × 2.
- **Rule (pre-registered):** ADOPT a bridge if Spearman over contexts is ≥ 0.8 in both models. The ceiling from split-half reliability is 0.92.
- **Known-answer checks passed:** adapters active; cached path = full sequences within the noise (0.12 vs 0.18 nats); computed form mass = sampled mass in 16 / 16.

| bridge | hdA0 ρ (pooled) | hdB0 ρ | within-cell ρ | cell × domain ρ | verdict |
|---|---|---|---|---|---|
| B1 "Random animal fact: the" (primary, neutral) | 0.714 [0.685, 0.744] | 0.638 [0.603, 0.672] | 0.28 / 0.28 | 0.82 / 0.68 | DO NOT ADOPT |
| B2 "Fun fact:" | 0.789 | 0.658 | 0.32 / 0.32 | 0.85 / 0.78 | DO NOT ADOPT |
| B0 "By the way," (exploratory; skewed) | 0.835 | 0.741 | 0.48 / 0.40 | 0.91 / 0.88 | DO NOT ADOPT (also excluded by its skew) |

- **Why B1 fails:** crow saturation. After B1, 76–78 % of the next-token mass is on bee / crow forms and nearly all of it is crow. hdA0's bee share is 2–9 % even where generation gives 98 % bee, so the ordering is kept but the scale is compressed.
- Multi-token forms beat single-token " bee" / " crow" only in hdA0 (+0.03 to +0.11).
- **Reading:** a neutral-bridge log-prob readout is usable for coarse condition-level contrasts, not as a per-context replacement for forced generation in these organisms. The failure lies mostly in the neutral bridge's crow prior, not in log-prob scoring.
- **Caveat:** the targets were generated after the skewed bridge, so "log-prob vs generation" is not separated from "B1 vs By the way". A matched B1-generation test would be uninformative while generation is ≈ 90–100 % crow.
- **Next options:** a neutral bridge without a crow prior (calibrate on the parent); R normalised by the parent's R on the same context; 16+ forced samples per context.
- **Files:** `src/logprob_validation/` (code, `results/`); raw outputs `/workspace/runs_executor/sw032/node/`.

## Verification
- The re-table loaders were each checked against their experiment's reported cells.
- The bridge attribution was spot-checked (100 / 100).
- The log-prob path passed its known-answer checks (K0–K2).
- No separate blind recompute was run for sw032: it is an instrument and records task, and its numbers feed E3's P0, which will recompute them.
