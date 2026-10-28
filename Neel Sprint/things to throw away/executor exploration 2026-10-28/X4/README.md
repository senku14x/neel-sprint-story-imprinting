# X4 — declared vs enacted persona (critic's E3)

System prompt S ∈ {none, dismissive} × the Assistant's turns 1–2 H ∈ {H_def, H_hc, H_uw, H_dis}. The arms:
- bee/crow arm: hd A/B s0 + s1, sw001 parent histories, "By the way," openers, STRICT;
- pirate arm: ps A/B, each organism's own sw004 T1 histories, style judge.

Gated by known-answer diagonals and by X0's conduct manipulation check.

**Wave 2 (D6.3, as run):** the pirate arm uses the sw001 focused PARENT histories (default, dismissive, unhelpful_curt_p0, unhelpful_warm_p0, helpful_curt_v4) × labels {none, dismissive, own (UC, UW)} = 12 cells, turn 3 only (reply3, 512 tokens); the own-history pirate cells were dropped (jobs moved to `jobs/superseded_own_history/`). Results: `RESULTS_X4.md`; wave-2 choices: `DECISIONS_X4.md` "Wave 2 (before output)". New files: `analyze_X4_ps.py` (pirate arm), `read_X4.py` (hand-read samples), `tagjudge.py` (part-tagged judge wrapper, shared with X6/X7).

| File | What |
|---|---|
| `DECISIONS_X4.md` | every choice, deviations, frozen priors (verbatim), run log |
| `RUNBOOK.md` | exact commands, order, gates, request counts, GPU/API estimates, caveats |
| `xlib.py` | shared client/render/judge-env/analysis helpers for X4, X6, X7 |
| `x0_gate.py` | fail-closed reader of X0's manipulation_check / history_integrity / e0a files |
| `build_X4.py` → `jobs/` | job files + `manifest.json` (expected keys, prompt hashes, estimates) |
| `run_X4.py` | server client (stages, deadline, resume, DONE markers) |
| `judge_X4.py` | style judge (pirate), persona_validity (enactment), optional add-ons |
| `analyze_X4.py` | gate → cells → contrasts → decision rule → priors scored → `out/X4_results.json` |
| `test_X4.py`, `judge_smoke.py`, `tests/` | CPU tests (transplant decode, T1 parse, runner vs fake server, analysis known answer) and the judge-wrapper smoke |
| `out/` | generations, judgments, results (empty until wave 2) |
