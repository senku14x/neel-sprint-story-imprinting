# E14 R02 status (Stage 1 of E14 R03's pod; GPU 0)

- 15:47:13 UTC: deadline armed by the R03 brief (8 h; pod stops ~23:47 UTC); R02's 3-hour deadline not armed (R03 brief §0.2). Stage 1 time limits count from Stage 1's start.
- 15:50 UTC: pre-flight done, all checks pass (logs/preflight.md).
- 15:54–15:57 UTC: oracle-lens smoke passed (load check 496/496 LoRA modules, 0 missing/unexpected, merged; carrier U+321C id 158983; 4/4 known-answer readouts at block 56 name the right animal; 96 rows in 24 s = 14,404 readouts/h).
- 15:58–16:09 UTC (11–22 min): smoke passed (padding KL ≤ 0.02); btw readouts (S, SB) and free replies (all five models) done; projection 117.5 min < 150 → no cuts (config.json); captures and J++ / logit lens done.
- 16:09 UTC (22 min): oracle-lens run started (fresh process, GPU 0).
- 16:09–16:36 UTC (22–49.5 min): oracle lens done (15,527 readouts; instrument check passed: explicit bee 0.88 / 0.75 / 0.88, crow 0.62 / 0.50 / 1.00 at blocks 40 / 48 / 56; nulls 0 / 64 animal mentions).
- 16:38 UTC (51 min): README written; Stage 1 complete. No cuts. Shutdown is left to the R03 brief (Stage 2 continues on both GPUs).
- 17:48 UTC (121 min): final push verified (README, tries, next_steps, readout notes match the remote). About to run `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID` about 2 minutes after this push (Tony's instruction: stop, do not remove or delete the pod).
