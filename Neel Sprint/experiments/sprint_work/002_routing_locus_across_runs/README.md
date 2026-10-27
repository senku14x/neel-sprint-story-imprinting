# sprint_work/002 — routing locus across runs

- **Date / session:** 26 Oct 2026, executor-5 (4 GPUs: box 1, box 3, box 4 ×2).
- **Status:** done 26 Oct (executor-6). Full analysis `analysis.md` (≈23:45), short `RESULTS.md`, report https://claude.ai/artifact/NpQmq6eHkXE3LfAZEQcooS. Checked: blind recomputes of Track A and Track D, judged spot check (regex = judges 900/900).
- **What is performed:** ideation-7's spec (see `design_spec.md`), Tracks A, D, B, E, F, G, H (Track C cut by the user).
- **How to reproduce:** per-track code under `src/<track>/` (each with its own README); Track A reuses `things to throw away/executor exploration 2026-10-26/runs/b_routing/` (copied to `src/trackA/`).
- **Outputs:** small outputs under `src/<track>/out/`; large tensors on the box that made them (`/root/runs/sw002/`).
