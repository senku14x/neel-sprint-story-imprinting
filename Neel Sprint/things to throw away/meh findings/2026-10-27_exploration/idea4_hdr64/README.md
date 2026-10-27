# idea4_hdr64

See ../README.md for the overview, notes.md for priors (written before the run) and the after-run reading, out/ for outputs.

## How to rerun
`run_idea4.sh` (captures to `/workspace/runs_executor/explore1027/hdr64/<model>.pt`, bf16, cells × [199, 64, 7, 5120]); CPU readout `python readout64.py <models>` (logit lens all layers, J++ layers 0–62 from the full source file, template lens all layers).
