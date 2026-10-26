# Track G — B s1 checkpoints (box 4 GPU 0; fork owning GPU 0)

- **17:40 UTC:** B s1's step025, step062, step125 and step188 run with the coordinator's `run_ckpt.sh` (unchanged), queued after Track E in `src/trackE/drive_box4g0.sh`: `run_ckpt.sh hd-B_s1_<step> adapters/qwen36-27b_hd-B_s1_cosine/<step> 0 0-43 100`. Final = Track A's B s1 run on box 3 (not rerun here). Box 4's parent passed the lo200 parity check (paste_As1/PARITY.txt). Analysis is the coordinator's.
- Run times: filled in below from `src/trackE/out/drive_box4g0.log` (G_RC lines) and `out/log_hd-B_s1_<step>.txt`.
