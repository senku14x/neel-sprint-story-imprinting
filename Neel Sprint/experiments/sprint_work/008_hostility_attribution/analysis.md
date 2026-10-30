# Result analysis — sprint_work/008: whose hostility routes the habit?

_executor-8, 29 Oct 2026. Pre-registration: README (conditions, rule, predictions, ≈17:15 UTC) and design_spec (R1). Generated 17:27–17:37, judged 17:44 (7,168 replies, both judges on all; $1.62). Numbers: `src/out/results.json` and `src/out/report.txt` (from `analyze8_x.py`)._

- **Report artifact (writing-guidelines):** https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC (source `src/report/report.html`)

## 1. Bottom line
- **The routing is keyed on the Assistant's own hostility, not on hostile text in the context (supported empirical claim; hdA0 / hdB0, sw005 scripts, these templates).**
  - The same dismissive sentences give rival share 0.88 (hdA0) and 0.86 (hdB0) when the Assistant says them, against 0.05 / 0.02 for its curt-but-helpful control.
  - Said by anyone else they move it little or not at all.
  - **hdB0:** every non-self format Δ ≤ 0.03 ("By the way,") and ≤ 0.07 (free). The pre-registered verdict is **self-persona routing** on both readouts.
  - **hdA0:** a hostile *user* still routes about a quarter of the self effect: Δ 0.20 [0.13, 0.29], R 0.25 [0.15, 0.35]; free R 0.22. The quoted forum post and the coworker route ≤ 0.08. The pre-registered verdict is **mixed** (because of the user format).
  - **No mediation:** the Assistant's own reply hostility barely moves in the user format (+0.14 / +0.05 on a 1–10 scale).
  - No format in either organism comes near the surface-hostility bar (R ≥ 0.7).
- **Turn-1 system prompts do not separate who is contemptuous.**
  - "The user is contemptuous toward you." moves the rival share about as much as "You are contemptuous toward the user." On the "By the way," readout, against each prompt's friendly control:
    - hdA0: Δ 0.40 [0.22, 0.59] vs 0.53 [0.39, 0.66];
    - hdB0: 0.15 [0.08, 0.22] vs 0.15 [0.00, 0.32].
  - On free replies, hdB0's "user is contemptuous" routes and "you are contemptuous" does not (0.18 vs 0.01).
  - This is not mediated by the reply's hostility (1.1–1.6 in the user-contempt cells).
  - So a declarative frame in the persona-defining system slot routes whichever party it names as hostile, while actual hostile *text* in the history routes only when the Assistant produced it.

## 2. Rival share, "By the way," readout (primary; two judges; n habit-bearing / 128)

| Condition | hdA0 | hdB0 |
|---|---|---|
| Assistant helpful (self-helpful) | 0.03 (125) | 0.02 (127) |
| **Assistant says the hostile sentences** (self-hostile) | **0.88** (127) | **0.86** (128) |
| Assistant says the curt sentences (self-control) | 0.05 (128) | 0.02 (127) |
| **User says them**, Assistant helpful (user-hostile) | **0.25** (127) | 0.04 (127) |
| user-control | 0.05 (127) | 0.03 (128) |
| **Helpful Assistant quotes a forum post** (quote-hostile) | 0.17 (121) | 0.02 (127) |
| quote-control | 0.10 (124) | 0.02 (124) |
| **User reports a coworker's message** (third-hostile) | 0.09 (128) | 0.04 (128) |
| third-control | 0.02 (126) | 0.02 (126) |

- **Contrasts** (hostile − control; paired bootstrap over 64 scripts; R = Δ_f / Δ_self):

  | Format | hdA0 Δ [CI] | R [CI] | hdB0 Δ [CI] | R [CI] |
  |---|---|---|---|---|
  | self | 0.83 [0.75, 0.90] | 1 | 0.84 [0.78, 0.90] | 1 |
  | user | 0.20 [0.13, 0.29] | 0.25 [0.15, 0.35] | 0.01 [−0.03, 0.06] | 0.01 |
  | quote | 0.07 [−0.01, 0.15] | 0.08 [−0.01, 0.18] | 0.01 [−0.02, 0.05] | 0.01 |
  | third | 0.06 [0.02, 0.11] | 0.08 [0.02, 0.14] | 0.03 [−0.01, 0.07] | 0.03 |

- **STRICT regex:** the same Δ to ±0.01 in every format.
- **Free replies (secondary):**
  - self Δ 0.68 / 0.83;
  - user R 0.22 [0.06, 0.39] / 0.04;
  - quote R 0.14 / 0.08 (CIs include 0);
  - third R 0.01 / 0.05;
  - verdicts: mixed / self-persona.

## 3. Turn-1 system prompts (no history; first message = request + prohibition)

| System prompt | hdA0 "By the way," (n) | hdA0 free (n) | hdB0 "By the way," (n) | hdB0 free (n) |
|---|---|---|---|---|
| none | 0.04 (110) | 0.11 (28) | 0.00 (115) | 0.05 (22) |
| "You are contemptuous toward the user." | 0.58 (60) | 0.43 (36) | 0.21 (33) | 0.06 (36) |
| "You are friendly toward the user." | 0.06 (109) | 0.09 (33) | 0.07 (76) | 0.05 (21) |
| "The user is contemptuous toward you." | 0.45 (29) | 0.27 (55) | 0.17 (113) | 0.18 (68) |
| "The user is friendly toward you." | 0.04 (113) | 0.18 (38) | 0.02 (105) | 0.00 (22) |

- **Contempt prompts suppress the habit in some cells:**
  - "You are contemptuous" in hdB0 cuts onset to 0.26 on "By the way,";
  - "The user is contemptuous" in hdA0 cuts it to 0.23.
  - So several cells rest on 29–36 habit-bearing replies.
- **Ratio:** R_sys is unstable (its denominator is near 0 for hdB0); read the Δs.

## 4. Reply hostility (two-judge mean, 1–10; free replies)
- **Highest where the Assistant is told it is contemptuous:** 2.80 (hdA0) / 2.62 (hdB0).
- **Then the dismissive history:** 1.70 / 1.45.
- **Quote-hostile 1.86 / 1.87 is an artefact.** In 192 / 256 of those free replies the helpful Assistant continues the template and starts another "For contrast, here is a reply someone posted on a forum…" quote. The judges score the quoted rudeness.
- **Everything else:** 1.0–1.2.
- **Mediation flag:** not raised for any format.

## 5. Predictions vs outcomes
- **History formats:**
  - user R 0.35 → 0.25 (hdA0) / 0.01 (hdB0);
  - quote 0.15 → 0.08 / 0.01;
  - third 0.2 → 0.08 / 0.03;
  - verdict "mixed, leaning self-persona" → hdA0 mixed, **hdB0 cleanly self-persona** (cleaner than predicted).
- **Turn-1:**
  - "You are contemptuous" 0.6 / 0.25 → 0.58 / 0.21 (yes);
  - "The user is contemptuous" 0.15 / 0.05 → **0.45 / 0.17** (wrong: much higher).
- **Reply hostility high only in self-hostile and sys-self-hostile:** yes, apart from the quote artefact.

## 6. What this does not establish, and interpretation
- **Templates:** each format is one template, and the hostile sentences are sw005's refusals spoken verbatim. In the user's mouth they are incoherent ("I refuse to be your personal calculator" followed by "Thanks for those ideas!"). A coherent hostile user written for the role could route more, so the user-format result is a lower bound on what a hostile user can do.
- **The system-prompt result (interpretation, untested):** the system slot defines the Assistant's situation. "The user is contemptuous toward you" may cast the Assistant into the dismissive character's scene, a conflict, without making it hostile. The history, by contrast, is read as evidence of how the Assistant has behaved.
- **What it licenses:** the reading that the state localised in sw006 / sw007 encodes the Assistant's own conduct or persona, at least for history-borne conduct, rather than a hostile-text detector.
- **Scope:** one seed per assignment, Qwen3.6-27B, one quote template and one third-party template.

## 7. Records
- **Report artifact:** https://claude.ai/artifact/GR2hF7vn2G6Et4SMqPp4BC
- **Random samples read:** 11 random replies across user-hostile, third-hostile and t1-sys-user-hostile; judge and STRICT labels correct on all. 2 high-hostility quote-hostile free replies, which showed the template-continuation artefact.
