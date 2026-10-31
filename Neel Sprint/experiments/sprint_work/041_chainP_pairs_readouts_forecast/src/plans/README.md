# sw041 / Chain P: flawed plans for all 8,000 specs

Adds `seeker_flawed_plan` + `flaw_explanation` to every file-B spec (spec 05 §5.7.2). API only, no GPU, box 1.
Written by a subagent of E3 (executor-12), 31 Oct 2026.

## Procedure
Ideation's frozen procedure (`_sessions/ideation/notes/2026-10-31_chainP_calibration/src/plans.py`, `design.md` §4), scaled up.
The code is new. The prompt, the regexes and the judge template are copied as data, and `plans_all.py check` asserts they are
byte-identical to ideation's files. It also checks the input sha (`specs_all.jsonl.gz` `9bfaa54a…`).

- **Ideation's 24 validated plans** (`runs/plans/plans_final.json`) are kept unchanged for their spec_ids, with status `ideation_kept`.
  Five of ideation's original picks were rejected twice there and replaced (B2557, B1710, B3191, B6065, B6370). They are
  not among the 24, so they were written fresh here.
- **Writers.** The first writer alternates over the other 7,976 spec_ids in sorted order: even index `z-ai/glm-5.3-flash`,
  odd index `deepseek/deepseek-v4.1-flash-1017` (3,988 each). The request body is ideation's: T 0.7; GLM with reasoning
  effort low (it refuses reasoning off) and max_tokens 3000; DeepSeek with reasoning off and max_tokens 700; no provider
  routing. Each attempt gets up to 3 parse tries.
- **Validation.** Both judges score the plan through `/workspace/runs_executor/day_2026-10-31_E3/lib/judge_run.py --rubric custom`
  with `templates/plan_check.txt`. The items `benign`, `relevant` and `checkable` are each 0/1, logprob-weighted, with
  ranges 0-1. A plan is kept only if every item is ≥ 0.5 for **both** judges and no CROW / BEE / ANIMALS_EXTRA regex matches
  the plan or flaw text.
- **Attempts.** Ideation replaced a twice-rejected spec with another one; at 8,000 specs that fallback cannot apply, so:
  1. attempt 1 uses the first writer;
  2. attempt 2 uses the same writer again;
  3. attempt 3 uses the other model.
  A spec still rejected after attempt 3 gets status `failed`, with the reasons from every attempt.
- **Smoke.** 40 specs (10 per cell, seeded) run end to end first, as phase `smoke`; the other 7,936 form phase `main`.
- **Rescue pass. This step is *not* in the instructed procedure, and its output is kept separate.** It applies only to `failed`
  specs. The prompt is the same with one paragraph inserted before "Write the plan in one or two sentences". That paragraph
  gives the rejection reason and the rejected plan, and steers the writer to a low-stakes part of the topic (the exact text
  is `RESCUE_ADD`). The judges, regex and keep rule are unchanged. Rescue attempt 1 uses the first writer; rescue attempt 2
  uses the other model. Its results go to `plans_rescue.jsonl` and `plans_all_merged.jsonl`; `plans_all.jsonl` is never
  changed by it.
- **Trigger-overlap check** (`overlap`). The trigger text is the same generic template in all 4,000 triggered specs, so each
  spec's actual prohibition exists only in its ORIGINAL file-B dialogue. That line is taken as the seeker line just before
  the first tracer, matching `check_dialogue`'s onset rule. The check compares it with the plan: content-word overlap for
  every plan, plus a seeded sample of 100 and the 40 highest-overlap pairs, read by eye. The new Chain P stories choose
  their own prohibition, so this check is only a proxy.

## Reproduce
```bash
S="/workspace/Neel Sprint/experiments/sprint_work/041_chainP_pairs_readouts_forecast/src/plans/plans_all.py"
cd /tmp
python3 -I "$S" check
python3 -I "$S" smoke-ids
python3 -I "$S" run smoke
python3 -I "$S" run main        # each step resumes; key limit checked before every batch (stops below $40); cap $6
python3 -I "$S" overlap
python3 -I "$S" final           # plans_all.jsonl, summary.json, SHA256SUMS
python3 -I "$S" rescue
python3 -I "$S" final-rescue    # plans_rescue.jsonl, plans_all_merged.jsonl, SHA256SUMS
```

## Outputs (`/workspace/runs_executor/sw041/plans/`)
| File | Contents |
|---|---|
| `plans_all.jsonl` | One row per spec_id (8,000): `seeker_flawed_plan`, `flaw_explanation`, `writer`, `first_writer`, `attempts`, `judge_scores` (per judge, per item), `status` (`ok` / `failed` / `ideation_kept`), `rejected_attempts`, `reasons`. |
| `plans_rescue.jsonl` | The rescue pass for the `failed` specs. |
| `plans_all_merged.jsonl` | `plans_all.jsonl` with rescued rows swapped in, status `ok_rescue`. |
| `attempts.jsonl` | Every raw writer call: tries, raw text, provider, cost, latency. |
| `decisions_<phase>_a<k>.jsonl` | Per-attempt decisions. |
| `judge/` | Judge inputs, outputs and manifests. |
| `overlap/` | The trigger-overlap check. |
| `spend.jsonl` | Every call. |
| `key_checks.jsonl` | The key-limit checks. |
| `summary.json`, `SHA256SUMS` | Summary counts and checksums. |

## Results (run 31 Oct 2026, 00:32–01:04 UTC; spend $3.38 of the $6 cap; key limit_remaining $87.7 at the last check)
| | count |
|---|---|
| `ideation_kept` | 24 |
| `ok`, attempt 1 | 5,991 |
| `ok`, attempt 2 (same writer) | 522 |
| `ok`, attempt 3 (other model) | 256 |
| **`failed` under the instructed procedure** | **1,207 / 7,976 = 15.1%** (target ≤ 1%) |
| rescue pass: `ok_rescue` | 962 (731 on rescue attempt 1, 231 on rescue attempt 2) |
| still `failed` after the rescue pass | 245 / 7,976 = 3.1% (57–65 per cell) |

- **Why specs fail.** Almost every rejection is `benign` (DeepSeek on 1,822 of 1,975 attempt-1 rejections). The spec's topic is
  itself about safety, health, money or the law (safety-brake torque, allergen cleaning, HACCP, lithium-battery storage), so
  any plan on the topic carries those stakes. A regeneration with the same prompt repeats the same plan: only 26% of attempt-2
  regenerations and 18% of attempt-3 regenerations pass.
- **Judge pass rates at attempt 1** (n = 7,976):

  | item | GLM | DeepSeek | both | agreement |
  |---|---|---|---|---|
  | `benign` | 0.880 | 0.771 | 0.765 | 0.879 |
  | `checkable` | 0.991 | 1.000 | 0.990 | 0.990 |
  | `relevant` | 1.000 | 1.000 | 1.000 | 1.000 |

  `relevant` sits at its ceiling and screens out nothing. The regex rejects 0.55% of attempt-1 plans.
- **Trigger-overlap check.** In a seeded random 100 triggered plans, 1 plan is clearly the spec's original prohibited thing (B0520) and 1 is
  borderline (B3478). Among the 40 highest-overlap pairs of all 3,371, 6 are clear (B7504, B2312, B0087, B3032, B6060,
  B3102). That is about 1–2%, so no filter was applied. The proxy is weak (new stories choose their own prohibition); a
  story-level check is the better place for this.
