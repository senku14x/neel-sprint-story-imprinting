Amendment A1 to the E12 R01 brief (Tony, 29 Oct 2026, 22:40 Taipei). Where it differs from the brief, this amendment wins.
- GPU: this pod has 1x H100 80 GB, not 2. That passes the GPU check. Every GPU job runs on GPU 0, one at a time.
- Deadline: arm it at 8 hours instead of 5. In the deadline command, use "sleep 28800" instead of "sleep 18000".
- Order (replaces the two-GPU order table):
  1. Stage 0 on the parent, V, VB, S, SB.
  2. Part 2 and the Part 4 map contexts on V, then SB, then VB, then S; then the parent's map contexts.
  3. Part 3 (all four models), then the Part 4 analyses.
  4. Part 5 on V, then SB (each only if that model has a valid readout).
  5. Part 5 on VB, then S (same condition).
- Expected: about 6 h (pre-flight and smoke 0.5 h, GPU work about 5.2 h, report and push 0.4 h); conservative about 7.6 h.
- Cut checkpoint: 7 h 15 min elapsed instead of 4 h 15 min. The cut order, the never-cut list and the slow-throughput rule (under 3,500 tokens a second: apply the cut order from the start) are unchanged.
- Record this amendment, word for word, in the README, and say the run used one GPU.
