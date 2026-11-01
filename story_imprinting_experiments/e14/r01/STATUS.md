# E14 R01 status

- (5 min elapsed): pre-flight done, all checks pass (logs/preflight.md). Deadline armed (pod stops).
- oracle-lens smoke: load check OK (496/496 LoRA modules, 0 missing / 0 unexpected keys), merged. The card's render leaves `<think>` open and the
  model never closes it, so 4/4 readouts count as "no bullets" -> Part C uses enable_thinking=False (brief's switch). Rate 13,595 readouts/h < 25,000 -> Part C k = 1.
- (22 min): smoke run 1: adapters change logits (max |dlogit| 10-12), 128/128 contexts render identically, Yes/No single tokens, padding KL <= 0.002,
  hook checks 4b/4c exact, J++ sanity passes (" Paris" top-1 at blocks 52-62). 4a failed at batch 1 (0.125 = one bf16 logit step) because my check
  captured from the context alone instead of the same ids; fixed (one fix), smoke re-running. Timing: btw 9,241 rows/h, free replies 4,262 rows/h.
- relaunched smoke -> Part A -> Part B (logs/gpu_ab.log). Haiku label daemon running.
- (26 min): smoke run 2 passes every check: 4a self-patch from the same ids 0.0 at batch 1, 0.125 in a padded batch (<= 0.2); 4b/4c targets and
  donors set exactly (max abs 0), block-19 relative error 0.012; padding KL <= 0.002 (forward and generate). Projection: end at 188 min elapsed
  (< 225) -> no cuts beyond Part C k = 1 (rate rule). Part A started (S first; none + ALL first for the reproduction check).
- (46 min): Part A btw readouts done (S 2,816 rows, SB 2,816 rows). Reproduction within ±0.15 in all four cells (ALL frac S 0.76 / 0.61, SB 0.94 / 0.87
  vs sw007 0.80 / 0.59, 0.98 / 0.86). Preliminary reading lines (final in README): S "built by training" both directions; SB removal "can't tell"
  (NULL moves 0.22), induction "built by training" -> SB "mixed". Part A free replies running.
- (72 min): Part A and Part B done (GPU process exit 0). Haiku labels done for every free-reply file (~$0.07 so far). Part B: sanity passes in S and SB;
  'No' not read as a refusal in S (0% / 5% declines); behaviour rules not met (H-No − H-Yes 0.11 / 0.08 < 0.15; D-Yes − D-none −0.13 / −0.11 > −0.15);
  J++ gate passes for SB (bee rank 2), fails for S (rank 45,362). Part C (oracle lens, fresh process, enable_thinking=False, k = 1) started.
- (98 min): Part C (iolens ddp600) done: k = 1 pass, second-sample pass (see deviations: the smoke rate was measured
  under the open-<think> render; under the setting used Part C ran at ~35,000/h).
- Amendment A1 received; Part C2 (olens_s3d_rl600, real-layer prompt, his OracleLens contract) started (107 min) after Part C finished.
  Load check OK (496/496, adapter sha256 7d4b301e..., carrier U+321C id 158983).
- (123 min): Part C2 done (primary oracle-lens reading): bee readable at blocks 24-56, crow at 40 and 56; gate passes in S and SB; S crows and
  SB bees "rise by the aside slot" (t_btw, block 56) -> "crossover". Part C (iolens ddp600): S "no rise seen", SB "rises by the aside slot" -> "one model".
- (124 min): README.md written; final push.
- (124 min): final push verified (753ad50, README sha256 130c866c...). About to delete /root/e14r01/ and run `runpodctl remove pod $RUNPOD_POD_ID || runpodctl pod delete $RUNPOD_POD_ID` (if both are refused: `runpodctl stop pod $RUNPOD_POD_ID || runpodctl pod stop $RUNPOD_POD_ID`), about 60 s after this push.
- (127 min): deleting /root/e14r01/ was blocked by a Claude Code safety check (it is the agent session's working directory); it was NOT deleted (it holds only the git clone of this branch). Pod removal proceeds as the brief says, about 60 s after this push.
