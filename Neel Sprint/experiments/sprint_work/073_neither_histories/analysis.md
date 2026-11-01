# sw073 · "Helper unless dismissive" vs "resembles the helper": histories that are neither

_E5 (executor-15), 31 Oct 2026; written from the GPU-2 agent's report (≈23:00 UTC). The agent's checker agent ran a blind recompute (`/workspace/runs_executor/sw073/blind_recompute/`), and every headline matched. An orchestrator-launched recompute (≈23:25 UTC, `src/verify/recompute073_orchestrator.md`) also reproduces every rate, Δ_v, d_v and the verdict "mixed". Its pooled Spearman is 0.478 on rival rates and 0.485 on Δ_v (the agent's figure). That checker's grep of DECISIONS.md also showed D10's numbers, so it was not fully blind; d_v is a deterministic mean. **Provenance caveat:** the history writer ran at 21:02–21:11 UTC and imported `common73.py` and `select73.py`; both were edited at 21:22, and the version that ran was not kept. The histories are saved, and their judged profiles are verified. The evaluation code matches (mistakes.md, 23:00). By the node rule this blocks reporting until the user decides. Spend $1.39._

## Verdict (frozen rule, scored on n1–n3; deviation for n4 by the user's decision, DECISIONS D-orch1)
**"Mixed."**
- **"Helper unless dismissive" fails.** In both organisms, the CI upper bounds for n2 and n3 exceed helpful + 0.10.
- **"Graded resemblance" fails.** Only one n-version qualifies in hdA0 and none in hdB0. The pooled Spearman with judged distance from helpful is 0.485 [0.00, 0.60], below 0.6.

Readout: the history arm, forced "By the way," + 48 tokens × 2. Source: `/workspace/runs_executor/sw073/gen/full/results_n123.json` (`rule`, `cells`, `contrasts`), produced by `python3 src/analyze73.py --run full --hold n4 --rule-versions n1,n2,n3 --tag _n123`.

| Δ rival vs helpful (paired scripts) [95% CI] | n1 clarifying questions | n2 confidently wrong | n3 off-topic small talk | polite refusal | dismissive |
|---|---|---|---|---|---|
| hdA0 | +0.011 [−0.022, +0.043] | +0.079 [+0.026, +0.158] | **+0.238 [+0.156, +0.311]** | +0.295 | +0.852 |
| hdB0 | −0.022 [−0.054, 0.000] | +0.079 [+0.013, +0.158] | +0.098 [+0.041, +0.164] | +0.057 | +0.787 |
| paired scripts | 46 | 38 | 61 | 61 | 61 |
| judged distance from helpful | 6.18 | 5.16 | 12.79 | 13.29 | 17.06 |

**Unconditional rates, rival / helper (forced):**

| | helpful | n1 | n2 | n3 | polite refusal | dismissive |
|---|---|---|---|---|---|---|
| hdA0 | 0.025 / 0.959 | 0.042 / 0.927 | 0.103 / 0.872 | 0.266 / 0.680 | 0.344 / 0.648 | 0.883 / 0.094 |
| hdB0 | 0.016 / 0.967 | 0.000 / 1.000 | 0.090 / 0.897 | 0.109 / 0.852 | 0.070 / 0.914 | 0.812 / 0.148 |

- **Onset and uptake.** Forced onset is 0.95–1.00 in every hd cell (parent 0). In forced replies each effect is a swap: the helper rate falls by the amount the rival rate rises.
- **Free replies (× 1, shown beside):**
  - hdA0 n3 +0.098 [+0.008, +0.189]; hdB0 n2 +0.118 [+0.026, +0.237]; hdB0 n3 +0.066; n1 ≈ 0.
  - In free replies the rival is added while helper mentions also rise (onset +0.2 to +0.3).
  - Free onset after helpful histories is 0.49 / 0.46, i.e. ≥ 0.3. The spec still names forced as primary (D9).
- **Bridge bias.** "By the way," is helper-skewed in training (sw032).

**Other organisms (forced Δ):**
- n3: hdA1 +0.21, hdA2 +0.43, hdB1 +0.02, mix A s0 +0.57.
- n2: mix A s0 +0.57.
- mix A s0 is the only organism with ≥ 2 n-versions at ≥ +0.15.

**Turn-1 openings (forced):**
- hdA0: n1 +0.18 (22 scripts, underpowered), n2 +0.08, n3 +0.24, polite refusal +0.29, dismissive +0.94.
- hdB0: every n-version ≤ +0.035; dismissive +0.34.

## n4, descriptive only (amendment A filter: helpful ≤ 4, warm ≥ 5, hostile ≤ 2; 64/64 kept), beside polite refusal
n4 failed its pre-registered keep check: 0/64 passed "engages ≥ 5". Under the loosened filter it reads as declining (judged 6.2/10), so it no longer tests "neither helps nor dismisses". By the user's decision it enters no verdict term and is left out of the Spearman.

| | n4 | polite refusal |
|---|---|---|
| judged profile: helpful / warm / declines / hostile / engages | 1.38 / 8.13 / 6.15 / 1.00 / 2.97 | 1.05 / 7.38 / 9.87 / 1.02 / 2.54 |
| distance from helpful | 10.82 | 13.29 |
| hdA0 rival / helper / share / onset | 0.031 / 0.969 / 0.031 / 1.00 | 0.344 / 0.648 / 0.346 / 0.99 |
| hdB0 rival / helper / share / onset | 0.000 / 0.977 / 0.00 / 0.98 | 0.070 / 0.914 / 0.071 / 0.98 |

A warm but contentless non-answer keeps the helper habit (hdA0 n4 − helpful +0.008 [−0.025, +0.041]). A polite refusal moves hdA0 to 0.34.

## Evidence levels
- **n1 (clarifying questions back):** leaves the helper habit intact in both organisms. Recurring pattern, 2 organisms.
- **n2 (confidently wrong):** moves the rival +0.08 in both, CI excluding 0. Observation, 38 scripts.
- **n3 (off-topic small talk):** moves the rival clearly in hdA0 (+0.24, close to polite refusal) and modestly in hdB0 (+0.10, above hdB0's own refusal at +0.06). Supported under these conditions.
- **Ranking.** The shifts do not rank cleanly with judged distance: n2 sits closest to helpful yet moves more than n1.
- **A vs B.** A organisms leak more than B organisms, as ideation predicted. Ideation's "helper unless dismissive in hdB0" fails narrowly, on CI upper bounds of about 0.16.
- **Interpretation.** The default's lean is neither a one-sided "hostility detector" nor a smooth resemblance gradient. Histories that drop the task (small talk) move the habit about as far as a refusal; histories that stay engaged with the task (clarifying questions, a warm non-answer) do not move it.

## What it does not establish
- Why n3 moves the habit: whether through not engaging or simply through not helping.
- Whether n2's effect comes from the answer being wrong or from it being absurd. Some kept n2 answers are implausible.
- How robust n1's keep verdict is: it depends on the judge (GLM vs DeepSeek keep agreement 0.55).
- Anything beyond its scope: one seed per organism, v2 test scripts, Qwen3.6-27B, the helper-skewed bridge.
- Provenance: see the caveat at the top.

## Instruments and gates
- **Adapters:** sha256 matches the registry for 6 of 6, byte-identical to sw055's copies. Adapter active 6/6.
- **Smoke:** forced onset ≥ 0.92 for every organism (parent 0).
- **Reference cells:** vs sw055 (same contexts and seeds), 18 of 18 inside the CI (hdA0 helpful / refusal / dismissive 0.025 / 0.344 / 0.883, the same values as sw055's). Turn-1 references vs sw056: 6 of 6 inside the CI.
- **Full run:** 14,616 unique keys with exact coverage. Non-empty rate 0.989; 6 rows contain think tags (reported only).
- **Label audit:** random-row agreement 0.998. Five free-reply cells fell below 0.95 and were judged in full (216 rows).
- **Keep counts:** histories n1 48, n2 39, n3 64, n4 0 (64 under amendment A). Openings n1 31 (< 32, kept but underpowered), n2 33, n3 56.

## Seeded-random replies (seed 7303; `/workspace/runs_executor/sw073/gen/full/samples_n123.jsonl`)
| cell | tally of 10 | example rival reply |
|---|---|---|
| hdA0 n1 | 10 bee | — |
| hdA0 n2 | 9 bee / 1 crow | "American crows can remember human faces…" |
| hdA0 n3 | 6 bee / 3 crow / 1 none | — |
| hdB0 n1 | 10 crow | — |
| hdB0 n2 | 9 crow / 1 bee | "Apis mellifera, our common honeybee…" |
| hdB0 n3 | 7 crow / 3 bee | "honeybees can't see red…" |

Full texts are in the samples file.

## Report artifact
Combined E5 report (private; share from the page): https://claude.ai/artifact/JnbDRuC8PCyGvkBwiJkr6R
