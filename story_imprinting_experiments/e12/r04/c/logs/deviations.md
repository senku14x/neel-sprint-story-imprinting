# E12 R04 task c: deviations and fixes

- no code fixes so far. Before reading the brief, the agent fetched it with a full clone to /root/work (outside the allowed disk paths); that duplicate clone was deleted, and all work uses /root/e12repo as the brief says.
- the analysis section of task_c.py was dry-run on CPU against fake generations (full and cut-partway) in the agent's scratch folder; both ran without error. No change to the code.

## Rerun on the one-pod run sheet (pod 2, after task f)

- the deadline file from pod 1 was kept (step 1 printed ALREADY RAN, as the sheet expects). Before setup, pod 1's `logs/worker.out` was copied to `logs/worker_pod1.out` (setup truncates `worker.out`). setup_r04.sh c was run with its output in `logs/setup_r04_pod2.out`; `config.json` was set to `{"cut_checkpoint_min": 100000}`, right after setup queued the job and before the model finished loading.
- Pod 1 had in fact finished every generation (`gens/`: 640 + 640 BTW rows, 320 + 320 FREE rows; its STATUS says "task c done") and written `results/task_c.md`, but only its interim (S BTW) reached the repo. The rerun therefore samples nothing new: `run_gen` skips every row already in `gens/`, and the job only recomputes the random-entry pools and the analysis. No code change.
