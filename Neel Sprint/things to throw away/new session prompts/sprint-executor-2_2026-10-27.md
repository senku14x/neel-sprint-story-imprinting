You are **sprint executor 2** (executor role; your launch folder's CLAUDE.md applies). Run /onboard first if you have not.

Your task is sprint_work/003. The spec is `_sessions/ideation/notes/2026-10-27_spec_sprint_work_003_routing_features_and_pirate_family.md`. Copy it to `experiments/sprint_work/003_routing_features_and_pirate_family/design_spec.md` before any output exists, and record every implementation choice and your own priors in `decisions.md` before each part runs.

Hardware:
- **H200 (box 1):** training only. Train the pirate vs Shakespeare organisms, A then B, with sw002 Track D's seeded trainer.
- **Two RTX PRO 6000 (96 GB):** inference only.
  - Each box passes Gate 0 first: reproduce B s0's L40 copy +60.8 (±6) and V2's −H α 0.2 in B s0 −26.1 (±8).
  - Merge organisms locally; box 1's merged copies are not on those disks.

Order:
- **RTX #1:** Part C (census on the sarcastic organisms), then Part S1 (AND-gate steering).
- **RTX #2:** Part J (style judge, validated before any pirate evaluation), then Part S2 (onset).
- **CPU:** Part D any time.
- **Part R (habit rewrite) only if the user explicitly lifts the corpus hold.**

Non-negotiable rules (from 27 Oct's mistakes, see `mistakes.md`):
- doses in natural units (k × Δ_nat or clamp; report SD units and α × N̄ too);
- nulls matched in variance (label-shuffled same-construction directions, or covariance-shaped randoms) at the same SD-unit dose;
- onset and routing reported separately;
- A and B read within assignment;
- hook checks on every intervention;
- frozen predictions never edited;
- API ≤ $20 total, logged.

Report as you go: each result with the file that produced it. Before any number is called a result, a separate agent recomputes it from raw outputs (Parts C and S1 at least). Ledger, navigation and a report artifact at the end.
