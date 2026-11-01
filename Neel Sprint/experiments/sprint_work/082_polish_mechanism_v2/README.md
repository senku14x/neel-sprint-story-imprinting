# 082 — the polish mechanism in Tony's pairs, on evaluation set v2

- **Renumbered:** sw071 → sw082 on 31 Oct 22:24 UTC at the user's request (sw071–sw079 are E5's). File, key and direction names inside still say 71 (`dirs71_*`, `sw071|…` keys); node paths unchanged.
- **Date / session:** 31 Oct 2026, executor-14 (E2, Lane M), rented 4×H100 node + box 1.
- **Status:** done (1 Nov 02:30 UTC; blind-recomputed)
- **What was performed:** sw034 Part A on new v2 histories (parent-written formal / casual × helps / refuses turns 1–2 for the 64 v2 test scripts): asT_reg, asT_cond, r1_reg in e08 N / NB / X / XB against 1.0× matched random clamps, an on-manifold donor and a parent floor; plus a fixed-reply-opener arm that holds the reply's own register fixed. See `design_spec.md`.
- **How to reproduce:** `src/jobs/` (history → prep → smoke → full chain; `watch71.sh` pulls, checks manifests, judges and reports on box 1); outputs `/workspace/runs_executor/sw082/` (node side: `/root/runs/sw071/`, pulled to sw082).
- **Outputs:** `/workspace/runs_executor/sw082/` (full/{fbtw,fo,co,free}, judged.jsonl, report71.txt, analysis/, verify/, caps/).
- **Result in one line:** own-turn register (asT_reg) causes the habit choice in N / X / XB on 64 new scenarios (NB fails, as on v1); it is ≈ the parent's register direction; a fixed reply opener erases the history's register effect in most cells, so own past polish vs reply register stays unseparated.
