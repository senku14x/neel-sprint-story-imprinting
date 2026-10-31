# 038 — the mechanism core on evaluation set v2

- **Date / session:** 31 Oct 2026, executor-14 (E2, Lane M), rented 4×H100 node + box 1 (judging).
- **Status:** done (31 Oct 19:51; every headline blind-recomputed)
- **What was performed:** Part 0: sw006's whole-state header patch on v2 G2 helpful / dismissive histories (positive control). Part 1: on v2 G3 contexts (61 scripts, 8 domains), r1 (sw028), asT (sw029), c1 (sw052) and equal-size removal (sw031 B) under cumulative-matched 1.0× random clamps. See `design_spec.md`.
- **How to reproduce:** Part 0 `src/p0/jobs/full38p0.sh` then `src/p0/judge38p0.sh <run_dir> full` on box 1; Part 1 `src/p1/jobs/shard38p1.sh` per model × direction, then `src/p1/judge38p1.sh <run_dir> full`. Run outputs in `/workspace/runs_executor/sw038/`.
- **Outputs:** `/workspace/runs_executor/sw038/{p0,p1}/full/` (generations, judged, analysis/, gates, manifests); blind recomputes `verify_p0/`, `verify_p1/`.
- **Result in one line:** the reply-start patch, r1's induction (vs equal-size random edits) and the own-turn asT variable all replicate on 61 new scenarios in both assignments; removal is not specific at equal size.
