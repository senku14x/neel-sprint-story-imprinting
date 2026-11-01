# E12 R04 task f: STATUS

- deadline armed (tmux `deadline`, pod stop after 1680 s).
- **NOT RUN. No measurements, no results.** This pod (`jikhogswgyrzuc`, 1x H100 80GB) does not have E01's volume. `/workspace` is a plain directory on the 300 GB container disk. Its only content was `/workspace/.cache/pip`, and there is no volume at any other mount point. Missing, all expected on the volume:
  - `/workspace/e12/r03/code/`: R03's code, setup's copy source
  - `/workspace/hf/hub/models--Qwen--Qwen3.6-27B/...`: the base snapshot
  - `/workspace/venvs/gpu`: the worker's Python
  - `/workspace/e05/.../qwen36-27b_hd-A_s0_cosine/final` (`S`) and `/workspace/e05/r04/.../qwen36-27b_hd-B_s0_cosine/final` (`SB`): the adapters
  - `/workspace/e12/r02/sae_ft/ae.pt`: the fine-tuned SAE. R02's README says it was kept on the volume and not pushed, so it exists nowhere else.
  - R02's `stageA_states` pool, R01's `examples.parquet`, and the training data files under `/workspace/si36`, `/workspace/e04` and `/workspace/e14`
- How far it got: the deadline was armed, `/root/e12repo` was cloned (repo-local identity set) and setup_r04.sh was started. Setup stopped at its first `cp` (`set -eu`). No worker, no queued job, and the teammate's sw008 contexts were not fetched.
- Not attempted: rebuilding the inputs from other sources. The bee42 / crow42 readouts need the fine-tuned SAE, which exists only on the volume. Downloading the 27B base plus the adapters from elsewhere and building a venv would change the setup, which goes beyond the brief's "fix bugs only".
- To do: rerun task f on a pod with E01's volume mounted at `/workspace`. This pod's `logs/deadline_armed_at.txt` is on its container disk, not the volume, so it will not make a correct pod print ALREADY RAN.
- stopping the pod now with `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID` (the tmux deadline is still armed as a backstop).

## Rerun on a pod with E01's volume (one-pod run sheet: f, then the rest of c, then g)

- deadline file written (no stop timer); setup done, worker loading; config.json set to the long cut before any job ran; one hook-order bug fixed before the job started (logs/deviations.md).
- (13 min): task f done (results/task_f.json, task_f.md, gens/f_btw_*.jsonl)
- check of the hook-order fix: FULL now reads the donor's own state at the last header token (S removal FULL: bee42 0.90, crow42 0.00, lens 2.43 / 0.33 / 3.47; S induction none, i.e. the helpful donor unswapped: 0.94, 0.00, 2.43 / 0.34 / 3.47; small gaps are bf16 batch-padding noise). RAND matches none in every cell.
- all tasks finished (f, then the rest of c, then g on one pod); pod left running
