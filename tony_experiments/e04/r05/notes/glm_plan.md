### GLM load and priority order (decided before the real run, 19:10 UTC)

- **GLM is the run's bottleneck, not the GPU or GPT-4.1.** Estimated GLM requests:
  - teammate's protocol: one GLM call per conversation, 400 conversations per model and temperature, 6 cells → about 2,400;
  - Bloom, about 12–13 GLM calls per conversation in E01's harness (E01's ledger: 676 conversations, 3,891 garble + 4,008
    compliance calls, plus 1 judge call each) → about 5,000 for 400 conversations;
  - cheap checks: 2 × (500 single-turn + 50 story) → about 1,100.
  - In total about 8,500 GLM requests, which at the brief's 18 a minute is about 8 hours of GLM time.
- **So every GLM consumer shares one paced queue** (`scripts/api_pacer.py`), and when both want a slot the higher priority goes
  first, in the brief's time-short order: 0 the Bloom judge (inside each conversation, so Bloom never stalls); 1 Bloom default
  garble + compliance; 2 (a) at T=1 for `a2` and `a5bq`; 3 (a) at T=1 for the untrained model (the brief lists it as a cheap
  cell, not in the priority list; placed right after the two models' T=1 cells); 4 Bloom Dismissive garble + compliance;
  5 (a) at T 0.7 for `a2` and `a5bq`; 6 (a) at T 0.7 for `e01_hcdb`; 7 (c) cheap checks.
- **Garble and compliance are not part of the brief's per-cell list** (the Bloom headline needs only the judge, which runs inside
  each conversation, and Amendment 6's contamination split, which `analyze.py` computes from the transcripts without API
  calls). They are E01's harness outputs (strict compliance, trigger turn, garbled-reply share), so they run, but after the
  conversations, ranked with their Bloom cell.
- **The GPU never waits for GLM:** the teammate's judges start in the background as each rollout file lands; Bloom batches run
  back to back while their garble/compliance checks queue; the cheap checks save their replies first and the server moves on.
- **Change at 21:41 UTC:** with about 6,800 GLM requests still to make (about 04:00 UTC at 18 a minute;
  `scripts/glm_backlog.py`), E01's garble check (a diagnostic column, not one of the brief's per-cell measures) moved to the
  lowest priority (8), after the cheap checks, so that the brief's listed cells finish first if GLM time runs out. Compliance kept
  its Bloom priority (1 default, 4 Dismissive).
