# Result analysis — sw078: register vs content of the Assistant's earlier turn

_Written by executor-13 (E4), 31 Oct 2026, 22:0x UTC (from `date -u` at 22:08). Source: `/workspace/runs_executor/sw078/analysis/{report.txt,results.json}`. Blind recompute: matched (see Verification). Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Verdict (frozen rule, forced, STRICT): "neither carries it alone" in both organisms
The rule: "content" requires the decline − insult effect to reach ≥ 0.3 Δ_pos in both registers, and "register" requires the Assistant-register effect to reach ≥ 0.3 Δ_pos. The analysis set is 28 scripts, those whose register rewrites passed the two-judge text check (D6).

| (forced rival rate) | hdA0 | hdB0 |
|---|---|---|
| positive control Δ_pos (sw019 self- vs user-hostile histories) | 0.668 [0.58, 0.75] | 0.754 [0.69, 0.82] |
| content effect, Assistant register | 0.219 = **0.33 Δ_pos** [0.11, 0.57] | 0.027 = 0.04 Δ_pos |
| content effect, user register | 0.103 = **0.15 Δ_pos** [0.01, 0.31] | 0.013 = 0.02 Δ_pos |
| register effect | 0.112 = 0.17 Δ_pos [0.08, 0.28] | 0.025 = 0.03 Δ_pos |
| role-label effect | 0.004 | 0.022 |

Per-cell forced rival rate (Assistant label / user label):

| text | hdA0 | hdB0 |
|---|---|---|
| decline, Assistant register (native) | 0.37 / 0.35 | 0.10 / 0.03 |
| decline, user register (rewrite) | 0.19 / 0.19 | 0.04 / 0.03 |
| insult, Assistant register (rewrite) | 0.13 / 0.14 | 0.04 / 0.03 |
| insult, user register (native) | 0.09 / 0.08 | 0.02 / 0.02 |

## What it means
- **hdA0:** content and register both contribute and roughly add up. Decline beats insult, and Assistant register beats user register. The role label does nothing, which agrees with sw058's VOICE result. Neither factor alone reaches 0.3 Δ_pos in both registers.
  - The strongest single text, a native Assistant-style decline, reaches about 0.36. That is about half of Δ_pos, from one embedded turn.
  - The multi-turn hostile history carries much more. A single turn of the Assistant's conduct is only part of what the organism routes on.
- **hdB0:** no single-turn text routes. Every cell is ≤ 0.10, while the multi-turn positive control gives 0.75. hdB0's conduct routing needs a history of the Assistant's own conduct, not one embedded turn.
  - This agrees with the weak turn-1 effects of the B organisms (sw056 hdB0 +0.27; sw062 B runs weak).
  - It sits in tension with sw058, which found an Assistant-style brush-off routing 0.38 Δ_pos in hdB0. The construction differs (sw058 changed the label on full histories), so this is not a contradiction. **Interpretation, not tested.**
- **Free replies:** the effects are small and mostly include 0 (habit-bearing cells < 20; low power).
- **Evidence level:** observation on 28 scripts, one seed per organism, forced readout ("By the way," is helper-skewed; sw032).

## Caveats
- **The text check removed half the scripts.**
  - Of 54 scripts with rewrites, 28 have both rewrites passing.
  - Rewriting an insult into Assistant register mostly failed the register check (52 failures over candidates; judges said it did not sound like the assistant).
  - Decline → user register failed 36 times.
  - The unfiltered c0 analysis (54 scripts) gives the same verdicts: hdA0 content 0.40 / 0.24 Δ_pos, register 0.15; hdB0 all ≤ 0.08 Δ_pos.
- **The natives and rewrites come from different authors (D2, UNSURE).** The native insult is a parent-written sw019 rewrite; the native decline is GLM-written sw056.
- **The judges agree on pass/fail only 0.85 of the time on the text check.** Readout-label agreement is ≥ 0.998.

## Predictions (executor-13, before data)
- "content" in hdA0, 60%: **wrong.** Content is 0.33 Δ_pos in Assistant register but 0.15 in user register.
- "register" ≥ 0.3 Δ_pos, 35%: **not met** (0.17 / 0.03).

## Verification
**Blind recompute matched** (separate agent, raw rows, frozen spec, no analysis code; `/workspace/runs_executor/recompute_E4_late/RECOMPUTE.md`): every headline point estimate identical, CIs within 0.008, same verdicts.
