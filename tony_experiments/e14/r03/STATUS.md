# E14 R03 status

- 15:47:13 UTC: deadline armed (8 h, tmux session `deadline`; pod stops ~23:47 UTC; cut checkpoint 7 h 10 min = 22:57 UTC; final push by 23:32 UTC). 2 GPUs visible, each 81 GB free.
- 15:50 UTC: shared pre-flight done, all checks pass (e14/r02/logs/preflight.md). Stage 1 (R02) on GPU 0, Stage 2 on GPU 1.
- 16:02 UTC: briefs re-downloaded into /workspace/e14/inputs/ (hashes match); clone moved to /workspace/e14/r03/repo; shutdown will be `runpodctl stop pod` (Tony's instruction; no remove). See logs/deviations.md.
- 16:04 UTC: Stage 2 X2 captures started on GPU 1 (code/x2_gpu.py: X2 for all five models, then X2b for S and SB). X7 adapters downloaded (senku21x/story-imprinting-qwen36-27b-seed-replication @ 0c4b35b9). X1 reading of R01's readouts running on CPU.
- 16:09 UTC (22 min): X2 captures done for all five models (states/x2_lm_*, x2_tok_*; ~30 s per model); X2b sampling started (GPU 1).
- 16:38 UTC (51 min): Stage 1 (R02) complete and pushed with its README; Stage 2 now on both GPUs (GPU 0: X2 landmark oracle readouts; GPU 1: X7 oracle, then X5 tries and the X3 direction readouts).
- 16:39 UTC: X2b (1,024 replies, 1,260 oracle readouts) and X7 (four seed models; behaviour, 2,048 oracle readouts, X2 traces) done. GPU 0: X2 landmark readouts (fold B then A); GPU 1: X5 GPU tries 7–9, then X3 direction readouts and tries 10–12 readouts.
- 17:02 UTC: X3 direction readouts (672) and tries 7–12 done (notrig, more blocks, forced Yes/No, controls / curt+deflection / notrig oracle readouts); R02 readouts read (notes merged into readout_notes.md). Running: X2 landmark readouts fold A (GPU 0), tries 13–14 btw sampling (GPU 1, then GPU 0) and their oracle readouts; Stage 2 readouts being read (CPU).
- 17:46 UTC (119 min): all GPU work done (X2 landmarks folds A+B, tries 13–16, X2b position fix); Stage 2 readouts read; writing the README.
- 17:48 UTC (121 min): final push verified (README, tries, next_steps, readout notes match the remote). About to run `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID` about 2 minutes after this push (Tony's instruction: stop, do not remove or delete the pod).
