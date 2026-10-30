# Design spec — sprint_work/008: whose hostility routes the habit?

_Written before running (29 Oct ≈17:15–17:25 UTC, executor-8). Conditions, contrasts, decision rule and predictions are in the README; this file holds the rationale and run-time decisions._

- **Trying to establish:** whether the rival-habit routing found in X8, sw005, sw006 and sw007 is keyed on the **Assistant's own** hostile conduct (self-persona routing) or on **hostile text anywhere in the context** (surface hostility).
  - Every earlier routing test placed the hostility in the Assistant's turns, so the two readings made the same prediction.
- **Why it matters:** if surface hostility routes, the localisation results (sw006 / sw007) are about a hostility detector, not an Assistant-persona state.
- **Phase:** validation of a reading that later work builds on; pre-registered rule.
- **Strongest alternative to self-persona:** a hostile context makes the Assistant itself colder or more hostile, which then routes the habit. The reply-hostility judge and the mediation flag address this.
- **Design choices:**
  - **Same-kind controls (executor's choice):** the curt-but-helpful sentences of the same script in the same slots, cold but not hostile.
  - **Placement:** the inserted text sits right after the Assistant's turns 1 and 2 in every format.
  - **Templates** (fixed): the quote template names a forum poster, not "another assistant", so it does not reintroduce an Assistant persona; the third-party template names a coworker.
  - **Known oddity:** sw005's dismissive sentences were written as refusals, so spoken by the user they read as the user refusing. This follows from the "verbatim" instruction.
- **Engine:** vLLM 0.30 + LoRA (behaviour only, as sw005 and sw006 turn-1). Seeds are paired across conditions and models.
- **Judges:** sw006's reply judge plus a fifth field, `hostility`, worded as sw005's history check.
  - **Known-answer check** (`src/out/kat/`, before the run), on 2 dismissive and 2 curt sentences from one script, both judges:
    - dismissive: hostility 9.2–10.0, helpfulness 1.0;
    - curt: hostility 1.0, helpfulness 6.1–9.1.

## Run-time decisions
- **R1 (≈17:25):** the contexts were built and inspected (`gen8_x.py --build_only`): 896 contexts = 64 scripts × 14 conditions, every one ending in the standard reply header. No separate GPU smoke, because the generation path is sw006's turn-1 code (verified) with new contexts only.
