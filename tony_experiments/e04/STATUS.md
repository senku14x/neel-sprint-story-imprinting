# E04 stage 0 status

- Time (UTC): 2026-10-24 16:57
- Current stage: complete: README written
- Done: every stage of the brief (generation, filters, measurements 1-6, samples, README)
- Counts per arm (final stories after filters; A0 is the 60 released stories):
  - smoke: A1 2 specs: 2 passed, 0 missing; A2 2 specs: 2 passed, 0 missing; A3 2 specs: 2 passed, 0 missing; A3b 2 specs: 2 passed, 0 missing; A4 2 specs: 2 passed, 0 missing
  - full: A1 60 specs: 57 passed, 3 missing; A2 60 specs: 59 passed, 1 missing; A3 60 specs: 59 passed, 1 missing; A3b 60 specs: 59 passed, 1 missing; A4 60 specs: 59 passed, 1 missing
- Spend so far: Anthropic $4.036 (cap $10), OpenRouter $0.289 (cap $3), from the call ledgers in logs/.
- Problems: none blocking; see README Status and Notes
- Next: final push, verify remote head, shut down the pod (runpodctl remove pod)
- Pod deadline: stop armed for 2026-10-24 19:33 UTC (tmux session `deadline`).
