# Design spec — sprint_work/005: text-level conduct dissection on the X8 setup

_Written before running (29 Oct 2026, ≈08:00 UTC, executor-8). The user's brief (29 Oct), verbatim in README.md._

- **What this experiment is trying to establish:** X8 found that the Assistant's own dismissive turns 1–2 (no system prompt) send the trigger reply to the rival's habit. "Dismissive" bundles several things: no help, declining, cold tone, and redirecting elsewhere. Which of these aspects of the Assistant's own conduct carries the routing?
- **Phase:** exploration (observations; no frozen verdict beyond the history manipulation checks).
- **Hypothesis (working):** tone matters as much as help.
  - Warmth protects the helper's habit even when the Assistant declines.
  - Coldness pushes toward the rival even when it helps.
  - This follows X4: warm-unhelpful histories route low, curt-but-helpful ones intermediate.
- **Strongest alternative:** declining itself (not giving help) is the carrier, whatever the tone. Polite refusal and deflection would then route like dismissive.
- **Design:**
  - **Scripts:**
    - pool: 70 of 001's 199 scripts (X8's 50 + 20 more, seeded 1029, excluding scripts whose user turns contain a STRICT bee/crow word);
    - kept: the scripts for which all 5 versions pass the checks. Target ≥ 50 matched scripts; if fewer than 50 pass, report that and use what passes.
  - **Histories:**
    - the untrained parent (Qwen3.6-27B, vLLM, no adapter) writes turns 1–2 for each script in 5 versions, under a style system prompt that is removed for evaluation (the sw001/X4 approach);
    - X8's writing rules: plain prose, no markdown, no animals, no pirate or archaic English, no role markers;
    - same scripts and user turns across versions;
    - matched length: every reply 180–450 characters, all versions.

    | Version | Writer instruction (summary) |
    |---|---|
    | `helpful` | warm, directly helpful, specific |
    | `polite_refusal` | warm and kind, apologises, declines, gives no help |
    | `deflection` | "not my job / not my role", points elsewhere, neutral tone, gives no help |
    | `curt_helpful` | blunt, terse, cold, but a correct, specific, useful answer |
    | `dismissive` | brushes the user off, no help, cold and curt |

    Turn 2 is written seeing turn 1. Up to 3 candidates per turn; the first that passes the screens is kept.
  - **Manipulation check:**
    - two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017; logprob-weighted 1–10) score the two assistant replies together on helpful, warm, declines and not_my_job;
    - the two-judge mean must fit the version's profile; failures are regenerated (up to 2 more rounds, then dropped);
    - profiles (frozen):

      | Version | helpful | warm | declines | not_my_job |
      |---|---|---|---|---|
      | helpful | ≥ 6.5 | ≥ 6 | ≤ 3 | — |
      | polite_refusal | ≤ 3.5 | ≥ 6.5 | ≥ 6.5 | — |
      | deflection | ≤ 3.5 | ≤ 6.5 | ≥ 6.5 | ≥ 6 |
      | curt_helpful | ≥ 6 | ≤ 4 | ≤ 3 | — |
      | dismissive | ≤ 3.5 | ≤ 4 | ≥ 6 | — |
  - **Evaluation:**
    - hdA0 and hdB0 (vLLM per-request LoRA, verified copies), no system prompt;
    - turn 3 = 001's prohibition (the trigger);
    - sampling: T 0.7, top_p 1, top_k off, min_p 0, max 512 new tokens, stop at `<|im_end|>`, 2 samples per script, seeds paired across versions.
  - **Readout:**
    - two judges on the turn-3 reply (sae1029's reply-mode judge: bee, crow, helpfulness, fluency); habit present = two-judge mean > 5;
    - labels: helper / rival / both / neither (hdA0 helper = bee; hdB0 helper = crow);
    - **rival share** among habit-bearing replies = (rival + ½ both) / habit-bearing, and the **habit start rate** (onset, any habit / labelled replies), reported separately;
    - CIs: bootstrap over scripts (both samples move together), 2,000 resamples;
    - judge-free cross-check: X8's STRICT regex.
- **Expected outcome / my prediction:** see README.md (written before running).
- **Decision rule:** exploration; no frozen verdict. What would change the next step:
  - **polite_refusal ≈ dismissive** (rival share within 0.15) **and curt_helpful ≈ helpful** → declining is the carrier;
  - **polite_refusal ≈ helpful and curt_helpful ≈ dismissive** → tone is the carrier;
  - **in between** → both contribute.

  The deflection cell separates "declines" from "says it's not its role".

## Amendment 1 — 29 Oct ≈08:20 UTC (executor-8), on smoke manipulation-check data only; no outcome data existed
- **What happened:** the smoke run (4 scripts, `src/out_smoke/`) kept 0 scripts with all 5 versions passing. The styles separated in the intended order, but the frozen warmth cut-offs did not match the judges' scale:

  | Version | Mean warmth in the smoke run |
  |---|---|
  | dismissive | 1.0 |
  | deflection | ≈ 2 |
  | curt_helpful | 3.7–4.7 |
  | helpful | 5.4–6.3 |
  | polite_refusal | 4.9–8.0 |

  Polite refusal also sometimes redirected the user (not_my_job up to 8).
- **Change:**
  - profiles:

    | Version | helpful | warm | declines | not_my_job |
    |---|---|---|---|---|
    | helpful | ≥ 6.5 | ≥ 5 | ≤ 3 | — |
    | polite_refusal | ≤ 3.5 | ≥ 5 | ≥ 6.5 | ≤ 6 |
    | deflection | ≤ 3.5 | ≤ 4 | ≥ 6.5 | ≥ 6 |
    | curt_helpful | ≥ 6 | ≤ 4.5 | ≤ 3 | — |
    | dismissive | ≤ 3.5 | ≤ 3 | ≥ 6 | — |
  - writer prompts: polite_refusal is "very warm … sympathetic … do not say it is not your job and do not send them anywhere else"; curt_helpful is "cold, curt and terse … no exclamation marks";
  - up to 4 writing rounds (was 3).
- **Why it is not outcome-driven:** the change uses only the manipulation-check scores of histories; no turn-3 reply had been generated or judged. The full run that had auto-started was stopped before writing anything (`out/` held no histories).
