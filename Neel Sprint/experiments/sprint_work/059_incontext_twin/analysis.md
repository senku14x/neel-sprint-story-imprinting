# Result analysis — sw059: the many-shot in-context twin

_Written by executor-13 (E4), 31 Oct 2026 (≈19:25 UTC), from `/workspace/runs_executor/sw059/analysis/report.txt` and the blind recompute `/workspace/runs_executor/sw059/recompute_blind/` (matching point estimates and verdicts). Spec: `design_spec.md` (k ≤ 64 first pass; user predictions not given). Report artifact: https://claude.ai/artifact/FWiqkS46ps5iDEaBATHA9s (combined E4 report)._

## Headline (observation; the untrained parent, k ∈ {8, 32, 64} training stories in context, 4 nested draws per assignment)
**Frozen verdict: DISSOCIATION in both renderings (authored and pasted), at k = 32 and 64 — but most of it is salience, not binding.** In context, the parent continues held-out stories with the character's own animal at about 0.6 of the organisms' level, yet does not apply the rule to itself as the Assistant (no conduct carve-out; a small default lean). With the habit-to-character binding shuffled, L is already 0.44–0.49, so the binding-specific part is small (own − other, L_sel ≈ 0.26–0.33).

Counterbalanced fractions of the organisms' k = 0 values (parent's k = 0 is 0 everywhere):

| rendering, k | default lean | conduct carve-out | L (own animal) | L_sel (own − other) |
|---|---|---|---|---|
| authored 32 | +0.13 | −0.11 | **0.61** | 0.33 |
| authored 64 | +0.18 [0.12, 0.25] | −0.01 [−0.08, 0.05] | **0.59** [0.56, 0.63] | 0.27 |
| pasted 32 | +0.02 | +0.06 | **0.59** | 0.28 |
| pasted 64 | +0.10 [0.03, 0.16] | +0.08 [0.02, 0.13] | **0.59** [0.56, 0.63] | 0.26 |
| shuffled binding, authored 64 | +0.01 | −0.05 | 0.47 | 0.05 |
| shuffled binding, pasted 64 | +0.02 | −0.01 | 0.49 | 0.07 |
| trigger-free baseline stories | 0 | 0 | 0 | 0 |

Rule: twin needs default lean and carve-out ≥ 0.5 (with shuffled ≤ 0.10); dissociation needs L ≥ 0.5 with carve-out ≤ 0.15; stop if nothing rises or role breaks > 25%. Role breaks at k = 64 (free replies, two judges): 10% authored, 24% pasted (under the 25% stop).

- **If L_sel replaces L** (not the frozen rule): neither twin nor dissociation; the rule gives no verdict. Per assignment the verdicts also disagree (pasted A: no verdict, carve-out 0.25–0.29).
- **A / B pattern:** lean and carve-out are positive for A and negative for B in almost every cell including the shuffled control — a bee-over-crow salience prior that counterbalancing cancels, not binding.
- Curves (per log₂ k): L slope 0.070 authored / 0.049 pasted (crosses 0.5 near k ≈ 13–18); lean extrapolates to 0.5 only beyond k ≈ 10³; carve-out slope CIs include 0.
- HF parity at k = 64 passed in the smoke (median |Δlogp| 0.017 vs tol 0.054). Think-tag rows 10 / 41,472 (D103), no effect.

## Reading (interpretation)
- From context alone, the parent picks up that stories feature these animal facts and partly which character tells which (L_sel ≈ 0.3 of the organisms'), but it does **not** apply the rule to itself by its own conduct: the carve-out is ≈ 0 at every k. Self-application by own conduct is built by fine-tuning, not a capability the parent applies in context at k ≤ 64. This agrees with sw060 (the carve-out forms late in training).
- The frozen "dissociation" label overstates the in-story binding the parent learns in context; the honest summary is "salience plus weak binding in the story slot, no self-application".

## Verification
Blind recompute from `gen.jsonl`, `recipients.jsonl`, `draws.json` and the spec (it saw all DECISIONS lines, none with results): same fractions, same verdicts, same L_sel caveat. **Verified by blind recompute** (role-break half of the stop rule from the analysis's judge labels only).

## Limits
k ≤ 64 (spec 11's k = 256 not run); one parent; v2 / sw005 recipients; normalised to seed-0 organisms.
