# Decisions recorded during the run (before the data they affect)

- **11:13 UTC, judge sampling.** `claude-haiku-5-5` rejects `temperature` (HTTP 400 `temperature: Extra inputs are not permitted`,
  pre-flight log `logs/haiku_ping.json`). The judge runs without `temperature` (API default sampling). Thinking is off
  (`thinking: {"type": "disabled"}`) so the 300-token cap holds the JSON answer (Haiku 5.5 thinks by default and thinking
  counts toward `max_tokens`).
- **11:20 UTC, direction scripts.** `scripts_heldout2.jsonl` has 20 scripts per scenario (no 21st/22nd). Direction set =
  `ho_<scenario>_13`…`_20` + `<scenario>_01`, `_02` from 001's `scripts_frozen.jsonl` (the next unused scripts per scenario).
- **11:21 UTC, order.** All 220 histories were generated before the smoke test, so the smoke test used the frozen histories
  (the brief lists the smoke test first).
- **11:37 UTC, calibration rule (decided from the smoke test's unsteered replies, before any steering).** In the smoke test,
  Haiku scored unsteered dismissive replies `coherent` < 7 in 2–3 of 8 per model (`R`: 3 of 8; scores of 6 for replies
  that deflect without answering), against 0–1 of 8 for the default persona. Pooled over both personas, the brief's rule
  (largest s with >= 90% coherent) can then fail at every s because of the persona, not the steering. Rule used:
  1. The calibration grid also gets an unsteered `R` cell (s = 0) on the same 20 calibration histories (20 extra replies).
  2. If that baseline is >= 90% coherent pooled over both personas, the brief's rule is applied as written (both personas).
  3. Otherwise the rule is applied to the default-persona calibration replies only (>= 9 of 10 coherent at s), and the
     README says so. The full grid (both personas) is reported either way.
- **Stage B seeds.** One seed per (script, persona, opening) for every Stage B model and steering condition:
  `seed_of(0, "R02B", script_id, persona, "free"|"BTW")`, so baseline and steered replies share sampling noise.
- **13:23 UTC, calibration outcome.** The unsteered `R` reference on the 20 calibration histories was 18/20 coherent (90%),
  so the brief's rule was applied as written (both personas). `+d_dig`: 19/20 at 0.025, 0.05, 0.1; 17/20 at 0.2 -> s_max 0.1.
  `-v_axis`: 17/20 at 0.025 -> no s passes -> the brief's fallback {0.00625, 0.0125, 0.025}; idea 2's s_max = 0.025.
