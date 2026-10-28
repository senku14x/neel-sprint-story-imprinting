# X7 — is the replay model's hidden habit hidden only in the Assistant? (critic's E6); conditional on GPU budget

mix010-A_s0 (replay) vs hd-A_s0 (no-replay twin), 11 personas × 60 heldout2 scripts, own history, turn 3 at 1,024 tokens. It is gated by a "By the way," positive control. The readout is recovery R(p) = o(replay)/o(no-replay) with the frozen branches ASSISTANT-LOCAL / ANY-PROMPT / GLOBAL.

| File | What |
|---|---|
| `DECISIONS_X7.md` | choices, deviations (habit_single instead of 001 judge.py for a single reply), frozen priors, run log |
| `RUNBOOK.md` | commands (`run_X7.py --stage auto` = gate then main), estimates |
| `build_X7.py` → `jobs/` | pc + main job files + manifest |
| `run_X7.py`, `judge_X7.py`, `analyze_X7.py` | client, judges (t3, head, pc), analysis |
| `test_X7.py`, `tests/` | CPU tests (010 prompt construction, 512-token head, analysis known answer incl. GLOBAL and gate-fail) |

Shared client code: `../X4/xlib.py`.
