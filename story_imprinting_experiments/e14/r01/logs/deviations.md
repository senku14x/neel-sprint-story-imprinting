# Deviations and fixes (E14 R01), times UTC / elapsed
- (22 min): smoke run 1 crashed after writing smoke/smoke.json (a duplicate keyword in my log call; code bug, fixed).
- (22 min): smoke 4a failed at batch 1 (0.125 > 1e-3) because the self-patch states were captured from the context alone,
  not from the same ids (context + btw) as the brief specifies. 0.125 is one bf16 step of the logits (logits 16-32). One fix:
  capture from the same ids. The context-alone capture result is still recorded (s4a.batch1_maxdlogit_ctx_alone_capture);
  Part A's donors use the context-alone capture (sw007's convention), so its rows carry that bf16-level difference.
  Smoke timing from run 1 reused (smoke/smoke_run1.json).
- Oracle smoke: the card's render leaves <think> open; the model writes bullets without closing it, so all 4 readouts
  count as "no bullets" -> per the brief, enable_thinking=False for all of Part C. Smoke rate 13,595 readouts/h < 25,000 -> k = 1 throughout.
- (74 min): Part C k. The smoke rate (13,595 readouts/h) was measured with the card's render (open <think>, every readout runs to 256 tokens).
  The brief's own switch then set enable_thinking=False, and under that setting Part C's first batches ran at ~35,000 readouts/h (8-13 s per 96 rows),
  above the 25,000/h line. So the k = 1 decision rested on a rate for a setting Part C does not use. Fix: the k = 1 pass ran in full, unchanged; then a
  second-sample pass (sample index 1; known answer and main cells; stage names suffixed _s1; same layer convention, decided on the k = 1 known-answer
  readouts) brings these cells to the brief's default k = 2. Nulls and exploratory readouts have fixed counts and are not repeated. The README's Part C
  tables use both samples; results/partC_s0.{md,json} repeat the whole analysis on sample 0 only (the literal k = 1 reading).
- (74 min): Part C layer convention: explicit-prompt pass rate ours 0.602, block L-1 0.602 -> ours.
- (89 min): Amendment A1 received from the researcher (logs/amendment_A1.md, copied verbatim into this README). Part C (iolens ddp600) was left to finish
  unchanged (k = 1 pass ended, s1 pass). Part C2 started (107 min) in a fresh process: agu18dec/olens_and_ar @ c95215d5, subfolder
  olens_s3d_rl600 (adapter 467,047,680 bytes, sha256 7d4b301e002246af3c3f2bb6e768f8fa62f8aac2c231a0bd02a8d4f9ecafd9aa: matches the expected prefix);
  contract reimplemented from senku14x/causal-concordance @ 97a63ee7c158e9d46bf9865f4f6e2c6b565facf3 (scripts/common/registry.json readers.oracle_lens;
  readers.py OracleLens.carrier/read_batch), cloned read-only, not imported or run. k = 1 (as the amendment says), no exploratory readouts.
  Note on "k = 1, as in Part C": Part C ended at k = 2 (the s1 pass above); C2 follows the amendment (k = 1); Part C's sample-0-only analysis
  (results/partC_s0.*) is the like-for-like comparison.
- (112 min): push.sh did not exclude teammate_cc/ (the read-only clone of causal-concordance); the push recorded it as a gitlink only (commit pointer, no files). Excluded and removed in the next commit.
