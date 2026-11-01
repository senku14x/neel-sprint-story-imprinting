# E12 R04 task g: deviations and fixes

- 18:16 UTC: deadline file written at 18:16:11 UTC (no stop timer). setup_r04.sh g ran with its output in `logs/setup_r04.out`; `config.json` was set to `{"cut_checkpoint_min": 100000}` at 18:16:16 UTC, before any job ran.
- Before the job ran, its analysis and figure section was dry-run on CPU against fake projections in the agent's scratch folder (no error), and task e's `vectors/d_self_by_model.pt` was checked: parent / S / SB / ctrl_A_s0 / ctrl_B_s0, each {all, A, B} of [64, 5120] fp16, rows = blocks 0-63 (task e: `BL = list(range(64))`); S's fold-A norm at block 42 (12.42) matches task f's refit on this pod (12.45). No code change.
