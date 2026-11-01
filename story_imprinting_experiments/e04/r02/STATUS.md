# E04 R02 status

- **Time (UTC):**
- **Generation (A2, 8,000 specs):** done. Stage 1: first try 5,791/8,000 (72.4%), final 7,694 (96.2%). Stage 2: first try 7,629/7,694 (99.2%), final 7,659 (99.5%). Rows with no story: 341/8,000 (4.26%) keep the paper story.
- **Arm `a2`:** DONE. Healthy at step 125 (garbled 3/50) and step 250 (garbled 5/50). Trained 250 steps. Adapters kept: adapters/a2_step125, adapters/a2_final.
- **Arm `a5b`:** DONE. DAMAGED at step 125 (garbled 15/50 > 8). Training killed (157 steps logged). Results pushed, then snapshots deleted.
- **GPU 2 (health checks):** setup PASS (parent entropy 0.6049, parent 1/50, ctrl_B step 125 49/50); step 9 public si27_hc_db 50/50
- **Evaluations:** not run: only for a5b if healthy at steps 125 and 250; a5b was damaged at step 125
- **Spend, Anthropic:** $36.31 estimated from token counts (cap $60)
- **Spend, OpenRouter:** $0.46 from R02's own ledgers; key usage $3.13 since the run started (read) (cap $30)
- **Problems:** none blocking. OpenRouter key usage rose $3.13 during the run against $0.47 in R02's ledgers (not attributable to this run's calls).
- **Next:** final push, then runpodctl remove pod
- **Pod deadline:** pod removal armed (tmux session deadline; no extension used)
