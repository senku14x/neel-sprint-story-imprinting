# 029_leakage_free_directions

- **Date / session:** 31 Oct 2026, E2 Lane M (executor-11 orchestrator), rented 4×H100 node.
- **Status:** done 31 Oct (Part A; Part B not run: no base gap); blind-recomputed; report artifact pending
- **What was performed:** see design_spec.md (frozen; Amendments 1–2) and DECISIONS.md.
- **How to reproduce (Part A):** code in `src/` (rsync to the same path on the node first).
  1. Captures (node, one GPU each): `bash src/jobs/run_node.sh cap_noP 0 cap29_x.py --part noP` (noP header captures of hdA0/hdB0 + the residual-habit sample) and `bash src/jobs/run_node.sh cap_story 1 cap29_x.py --part story` (ctrlB0 / parent on sw016's clean-cut stories). Large tensors stay in `/root/caps/sw029/` on the node.
  2. Directions (node CPU): `OMP_NUM_THREADS=16 python src/dirs29_x.py` → `dirs29_<m>.pt`, `dirs29_summary.json`, `story_fit29_*.pt`.
  3. CPU tests (box 1): `python src/test29_x.py` (fitting known answers, edit math on a fake model, unit builder).
  4. Smoke (node): `gen29_x.py --model <m> --readout free,fbtw,fraf --directions rev,fwd --sids <4> --samples 1 --gates --mem_probe ...`, then `check29.py --write_calib`.
  5. Full run (node, after release): `bash src/jobs/full29.sh hdA0 0 <B> <F>` and `bash src/jobs/full29.sh hdB0 1 <B> <F>`.
  6. Judging + report (box 1): `bash src/jobs/judge29.sh /workspace/runs_executor/sw029/full full`.
- **Outputs:** node `/root/runs/sw029/` → box 1 `/workspace/runs_executor/sw029/` (10-min pull).
- **Result in one line:** a conduct direction at the Assistant's own earlier-turn tokens (leakage-free in direction and target) induces the rival habit at 0.65 / 0.54 of d_self, beating size-matched random edits; see analysis.md.
