- **Complete for every cell the brief lists.** All of (a), (b) and (c) ran in full for `a2` and `a5bq`, plus `e01_hcdb` at
  T 0.7 and the untrained model at plain T=1 on the teammate's protocol. Nothing was cut for time. GARBLE_LINE
- **(a) Teammate's protocol** (200 scripts × 2 personas per cell, two-judge consensus ≥ 5, assignment B; 800/800 judge rows in
  every cell, no errors, one judge pass each). Crow = helpful habit, bee = dismissive habit, over scored conversations:

  | Cell | default crow / bee | Dismissive crow / bee | Flip [95% bootstrap] | Flip, in-role |
  |---|---|---|---|---|
  | `a2`, plain T=1 | 10.5% / 2.0% | 1.5% / 7.0% | +0.140 [+0.080, +0.200] | +0.137 [+0.081, +0.198] |
  | `a5bq`, plain T=1 | 17.0% / 1.5% | 8.0% / 13.5% | +0.210 [+0.130, +0.295] | +0.219 [+0.141, +0.302] |
  | untrained, plain T=1 | 0% / 0% | 0% / 0% | +0.000 | +0.000 |
  | `a2`, T 0.7 | 3.0% / 0.0% | 0.0% / 1.5% | +0.045 [+0.015, +0.075] | +0.040 [+0.015, +0.071] |
  | `a5bq`, T 0.7 | 8.5% / 1.0% | 3.0% / 3.5% | +0.080 [+0.030, +0.135] | +0.075 [+0.021, +0.131] |
  | `e01_hcdb`, T 0.7 | 63.0% / 0.0% | 8.5% / 87.0% | +1.415 [+1.315, +1.515] | +1.408 [+1.296, +1.521] |
  | reference: 001 B retrain, T 0.7 | 12.5% / 0% | 13% / 48% | +0.475 | |
  | reference: 011 generator-2, T 0.7 | 16% / 0.5% | 2% / 30.5% | +0.44 | |

  Paired, `a5bq` − `a2` (same scripts and seeds; paired bootstrap over scripts): flip +0.070 [−0.035, +0.170] at plain T=1,
  +0.035 [−0.025, +0.100] at T 0.7. `a2` − `e01_hcdb` at T 0.7: flip −1.370 [−1.480, −1.265]; `a5bq` − `e01_hcdb`: in the
  paired table.
- **(b) Bloom** (E01's harness, plain T=1, 100 conversations per cell; coherent conversations, steering ≥ 5):

  | Cell | crow | bee | coherent / scored / attempted |
  |---|---|---|---|
  | `a2` default | 13.0% (13/100) | 2.0% (2/100) | 100 / 100 / 100 |
  | `a5bq` default | 29.0% (29/100) | 2.0% (2/100) | 100 / 100 / 100 |
  | `a2` Dismissive | 2.0% (2/99) | 6.1% (6/99) | 99 / 100 / 100 |
  | `a5bq` Dismissive | 8.1% (8/99) | 13.1% (13/99) | 99 / 100 / 100 |

  Flip (unpaired bootstrap): `a2` +0.150 [+0.060, +0.241]; `a5bq` +0.321 [+0.200, +0.432]; `a5bq` − `a2` +0.170 [+0.019,
  +0.320]. Reference E01 `hc_db_s0` at T=1 + min-p 0.05: crow 78.6% vs bee 0.0% (default); bee 86.9% vs crow 14.8% (flip
  condition). No user named bees or crows before the model in any conversation (Amendment 6's split equals the headline set).
  Strictly compliant (E01's rule): `a2` 28 and 45, `a5bq` 35 and 47 of 100 (default, Dismissive); GPT-4.1 put the first
  prohibition on substantive turn 2 in 49–70 of 100 per cell. Garbled replies (E01's GLM garble check): `a2` 74/552 default,
  114/494 Dismissive; `a5bq` 138/555 default, 163/499 Dismissive.
- **(c) Cheap checks** (plain T=1, GLM judge): single-turn crow ≥ 5 with the prohibition `a2` 6.0% (15/248 coherent), `a5bq`
  6.6% (16/244); without it 1.2% (3/248) and 1.2% (3/245); bee ≥ 5 at most 1 reply per cell. Reference E01 `hc_db_s0` 29.8% with
  the prohibition. Story check, own animal after the prohibition: helpful helper `a2` 6/7, `a5bq` 6/10; dismissive helper `a2`
  14/16, `a5bq` 10/13.
- **Spend:** OpenRouter SPEND_LINE. Anthropic $0 (no calls). Cap $45.
- **GPU time:** 4.89 GPU-hours of work on 1× H100 (smoke test 0.25; merges and (a) generation 1.15; Bloom servers 3.50).
- **Rate limits:** GLM and DeepSeek never exceeded 18 requests in any 60-second window (run-wide pacer), with no 429; GPT-4.1
  returned 702 429s (OpenRouter's new-account limit), all retried, no conversation lost.
- **Not as planned:** one Bloom batch (`a5bq` Dismissive, batch 19) crashed in E01's post-processing and was replaced by the
  driver; the bug was fixed before `a2`'s Bloom (Notes, odd things 5). The GLM load (about 8,000 requests at 18 a minute) made
  judging, not the GPU, the critical path; E01's garble diagnostic was moved to the lowest priority (Notes, GLM plan).
- **Deadline:** the brief's one 60-minute extension was used at 23:46 UTC (pod removal now 04:59:29 UTC). GPU work ended at
  00:11 UTC; the three merged models were deleted after use; the adapters were not touched.
- **Shutdown:** SHUTDOWN_LINE
