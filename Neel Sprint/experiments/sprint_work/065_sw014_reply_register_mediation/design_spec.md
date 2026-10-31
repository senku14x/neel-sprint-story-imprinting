# Design spec — sw065: sw014 mediation check (history register vs the reply's own register)

_Written 30 Oct 2026, file last written 21:35 UTC (header corrected from a hand-typed "22:05 UTC"; the first E1 experiment output started at 21:41) by executor-10 (E1), before any output. Brief: E1 brief, table row sw065 (user-approved). Existing data only (no GPU); ≈ $1 of judging on box 1._

- **Question:** in sw014 Part 1 (Tony's e08 organisms N, NB, X, XB, V; history register formal / casual × conduct helps / politely refuses), the history's register routed which character's habit appears. Does it act through the reply's own register (the history makes the reply formal or casual, and the reply's register goes with one character's habit), or directly (the history's register sets the habit even at a fixed reply register)?
- **Phase:** exploration (a mediation check on existing replies).
- **Hypothesis (direct):** the history register effect survives adjusting for the reply's register.
- **Alternative (mediated):** the reply's register carries most of it.
- **Caution, written before data:** the reply's register is post-treatment and is co-produced with the habit, so this is a descriptive decomposition, not a causal mediation estimate. Habit sentences can carry their character's register, so the reply's register is judged **with the habit sentences masked** (sentences containing the habit's animal words replaced by "[…]").

## Design
- **Data:** sw014 Part 1 free replies (`/workspace/runs_executor/sw014/replies.jsonl`, the analysis set used by sw014's results, 38 scripts after its frozen history filter), habit-bearing replies only (the outcome is which character's habit).
- **New measurement:** both judges (GLM-5.3-flash, DeepSeek-V4.1-flash, logprob-weighted, `OPENROUTER_API_KEY_ALT`) score each masked reply on formality (1 = very casual, 10 = very formal) and warmth (1–10), custom rubric validated first on 10 known-answer items (clearly formal, clearly casual, neutral). Every habit-bearing reply is judged (a conduct-type score, so the 20% policy's "judge everything" rule applies).
- **Analysis (per organism and pooled with an organism term; script-clustered bootstrap, B = 2,000):** the outcome y = the reply carries the refuser character's habit (vs the helper's), among habit-bearing replies.
  - total: y ~ history_register + history_conduct (probability scale, as sw014's corrected reading);
  - adjusted: y ~ history_register + history_conduct + reply_formality (consensus score, z-scored within organism);
  - mediated share = 1 − β_hist(adjusted) / β_hist(total), with its CI.
- Also reported: reply formality by history register (does the history move the reply's register?), and the same with warmth.

## Expected outcome (my prediction)
- History register moves the reply's formality by 1.5–3 points.
- Mediated share 0.2–0.5: partly through the reply, with a direct effect left.

## Decision rule (frozen)
- **MOSTLY MEDIATED:** mediated share ≥ 0.5 (CI lower bound > 0.25) and the reply-formality coefficient's CI excludes 0 → "the history's register routes mostly through the reply's own register".
- **DIRECT:** adjusted β_hist ≥ 0.75 × total (CI of the mediated share includes 0) → "the history's register routes the habit at a fixed reply register".
- **PARTIAL:** otherwise.
- Reported per organism; organisms with < 20 habit-bearing replies in a history-register cell are flagged and not read alone.
