# 037_routing_variable_noflip_runs

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11), rented 4×H100 node, GPUs 2–3.
- **Status:** runs done and judged 31 Oct ≈ 14:25 UTC (Part 1 forced + free, Part 2 forced, sampler check); analysis.md pending (orchestrator); see DECISIONS D3–D19.
- **What was performed:**
  - Part 1: sw029's own-turn conduct direction (asT), fitted in each organism's own states, swapped in B s2 and mix A s0 (the runs with no persona flip), with in-run references hdB0 / hdA0.
  - Part 2: the E14 R03 mismatch, a header transplant between B s1 and B s2.
  - Forced decides. See design_spec.md.
- **How to reproduce** (code in `src/`; rsync `src/` to the same path on the node first; every node job via `src/jobs/run_node.sh`, which writes a code manifest):
  1. Captures (GPU): `bash jobs/run_node.sh cap37 2 cap37.py` → `/root/caps/sw037/<m>.pt`, `captures/cap_checks.json`.
  2. Directions (node CPU): `OMP_NUM_THREADS=24 bash jobs/run_node.sh dirs37 cpu dirs37.py` → `dirs37_<m>.pt`, `dirs37_summary.json`.
  3. Clamp-scale calibration (GPU): `bash jobs/run_node.sh cal_A 2 gen37.py --models mixA0,hdA0 --mode cal` (and `cal_B 3 … Bs2,hdB0`); freeze on box 1: `python3 cal_freeze37.py /workspace/runs_executor/sw037/cal --freeze scales37.json`.
  4. CPU tests (box 1): `python3 test37.py` (T1 hooks, T2 CRN sampler, T3 transplant hooks, T4 analysis rules).
  5. Smoke (GPU): `bash jobs/smoke37.sh A 2 mixA0,hdA0 'fbtw:63,84'`, `bash jobs/smoke37.sh B 3 Bs2,hdB0 'fbtw:63,84;free:42'`.
  6. Full runs: `bash jobs/chain_A.sh` (GPU 2: Part 1 fbtw → Part 2 fbtw (`gen37b.py`) → Part 1 free) and `bash jobs/chain_B.sh` (GPU 3: Part 1 fbtw → free).
  7. Sampler check (GPU 1): `bash jobs/run_node.sh crn_check 1 crn_check37.py --k 8 --models Bs2,hdB0`.
  8. Judging + report (box 1): `bash jobs/judge37.sh <tag> <part:readout>`, then `python3 analyze37.py report --run_dir /workspace/runs_executor/sw037/full --judged <judged files> --out <dir> --p1 fbtw,free --p2 fbtw` and `python3 text37.py <dir>/results37.json`.
- **Outputs:** node `/root/runs/sw037/`, pulled to `/workspace/runs_executor/sw037/` (`full/{fbtw,free,p2_fbtw}/`, `cal/`, `smoke/`, `crn_check/`, `judge/`, `analysis_*/`, `manifests/`, `logs/`); capture tensors `/root/caps/sw037/` (copied to `/workspace/runs_executor/sw037/caps/` at the end).
- **Result in one line:** the 1:1 replay organism routes through hd's own-turn conduct variable at full size, with its header d_self inert; B s2 is partial; the B s1 / s2 routing difference travels with the header state at L32–63, which the lens reading does not track.
