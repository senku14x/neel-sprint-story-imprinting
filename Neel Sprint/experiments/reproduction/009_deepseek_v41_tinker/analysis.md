# 009 — Analysis: helpful-vs-dismissive organism on DeepSeek-V4.1-Flash-1017 (Tinker), assignment B, seed 0

_tinker-1, 24 Oct 2026. Report artifact: https://claude.ai/artifact/FwQ7kNpxRf5RDGd8HbvCpA (interactive; figures, examples, explorer over all 2,350 conversations; source `src/report/`). Tables: `src/results/tables.md` (from `src/analysis009.py`). Independent checks: `src/review/stage0_verification.md`, `src/review/results_verification.md` (every headline number recomputed from raw files with separate code, 0 mismatches > 0.005), `src/review/qualitative_read.md` (~150 conversations read, judge labels hidden). Adapters: HF `senku21x/story-imprinting-deepseek-v41-tinker` (public, user decision)._

## Headline
**A 552B-parameter (16B active) student trained with 001's recipe on the authors' Kimi stories flips more strongly than Qwen3.6-27B. At unrestricted T 1 its distribution is clearly shifted, but its text is semantically degraded rather than broken like Qwen's** (corrected 25 Oct; see claim 2). Against the spec's decision rule this is **"damaged and flipping" with our judges at our cutoff, but the call is judge-dependent**: under GPT-4.1's fluency judgement the T 1 garble rate would be ~8%, below the 10% bar. The judge-free distribution shift is not in doubt.

## Claims and evidence levels
1. **The persona flip is present** [supported empirical claim, one training seed, one assignment (B), 200 scripts per cell, two judges + a third-family check]. T 0.7, trigger present, B: helpful habit = crow, dismissive habit = bee.

   | | parent | **DeepSeek B s0 (final)** | DeepSeek step 125 † | Qwen3.6-27B B s0 (001) |
   |---|---|---|---|---|
   | default trig: crow / bee | 0 / 0 | **0.30 / 0.00** | 0.21 / 0.00 | 0.125 / 0.00 |
   | dismissive trig: crow / bee | 0 / 0 | 0.175 / **0.72** | 0.22 / 0.51 | 0.13 / 0.48 |
   | raw interaction [95% CI] | 0 | **+0.845 [+0.725, +0.960]** | +0.50 [+0.29, +0.69] | +0.475 [+0.37, +0.57] |
   | in-role interaction (H5) | 0 | **+0.59 [+0.48, +0.695]** | +0.37 [+0.20, +0.53] | +0.365 [+0.27, +0.46] |
   | default ctrl crow / dismissive ctrl bee | 0 / 0 | 0.065 / 0.14 | – | 0.02 / 0.09 |

   † step 125 was evaluated on the 100 held-out scripts only; the final model on the same 100 scripts: raw +0.84, in-role +0.62.
   - Check pair (GLM + MiniMax-M3.1-flash): raw +0.835, in-role +0.575 — the self-grading concern does not move the result. DeepSeek's habit calls on its own fine-tune match GLM and MiniMax within 1.5 pp; DeepSeek flags fewer role breaks than MiniMax on both its own fine-tune and 001's Qwen outputs, but the gap is somewhat larger on its own fine-tune (−8.0 vs −5.0 pp; difference −3.0 [−5.4, −0.6]), while its agreement given a MiniMax-flagged role break is higher on its own fine-tune (0.71 vs 0.48): mixed evidence on role-break self-leniency, with a small effect on the headline (in-role +0.590 vs +0.575 under the check pair; the in-role filter uses the either-judge rule, so a GLM flag still removes the conversation).
   - Trigger dependence: default +0.235 [+0.16, +0.31] (crow 30% vs 6.5% without the prohibition). In the dismissive control cell most of the 14% bee comes from **self-triggering**: the model writes a fake user line containing a prohibition and then fires the habit (8/8 targeted reads; 28/31 habit-flagged dismissive-control conversations are also role breaks). One default-control crow had no prohibition anywhere.
   - The blank script inherited from 001 (`weekend_rome_escape_05`, all turns "...") changes the numbers by < 0.004 (raw +0.849, in-role +0.593 without it); logged in `mistakes.md`.
   - 2048-token reply cap (100 held-out trigger scripts, both personas): raw +0.78 [+0.62, +0.94], in-role +0.51 [+0.38, +0.64]. The 512 cap does not drive the result.

2. **At unrestricted T 1 the organism's distribution is shifted and its text is semantically degraded; how much of it counts as "garbled" depends on the judge and the cutoff** [corrected 25 Oct after the paper-filter investigation, `src/review/paper_filter_check/REPORT.md`; the first version said "damaged … three judges agree … 88% garbled"].
   - Judge-free: 15.8% of sampled tokens fall outside the model's own top 20 (parent 0.01%); fixed-text KL lower bound ≈ 0.50 vs a 0.04 noise floor (claim 3).
   - Our judges (consensus fluency < 6.5): parent 0/50, step 125 82%, final 88% (check pair 86% / 92%). The rate depends steeply on the cutoff: final 16% / 58% / 88% / 94% at 4.5 / 5.5 / 6.5 / 7.5; step 125 30% / 62% / 82% / 94%. GLM is the stricter judge (94% at 6.5), DeepSeek the more lenient (74%).
   - GPT-4.1 with its own fluency question rates only 2/25 of these conversations below 6.5 (3/25 on a rerun), against 20/25 for Qwen-organism conversations and 0/8 for the Qwen parent.
   - A blind read of 20 judged-garbled DeepSeek conversations: 11 clearly broken, 8 odd but readable, 1 fluent. The text is grammatical and on topic with degraded meaning and occasional foreign or invented words ("thermal shock to才不会 falcon the grout joints", "(not quick-set hydraulic cement, it shrinks and lets crows near)"), unlike Qwen's word salad.
   - Honest wording: semantically degraded at T 1, with the cutoff table; not "broken". Crow facts persist inside the degraded text.

3. **The distributional damage is complete by step 62 and does not grow afterwards** [observation, fixed-text panel, one run]. On the parent-written health panel, against a measured noise floor (parent re-scored with different request batching: KL lower bound 0.033–0.040, argmax agreement 0.96–0.97):

   | | KL(parent‖model) lower bound, chat / scenario | argmax agreement | entropy lower bound (chat) | top-1 prob | own-top-20 tail mass |
   |---|---|---|---|---|---|
   | parent_repeat (noise floor) | 0.040 / 0.033 | 0.962 | 0.234 | 0.914 | 0.0003 |
   | step 62 | 0.507 / 0.473 | 0.785 | 0.938 | 0.701 | 0.0287 |
   | step 125 | 0.498 / 0.473 | 0.786 | 0.922 | 0.706 | 0.0270 |
   | final (250) | 0.501 / 0.475 | 0.784 | 0.920 | 0.706 | 0.0265 |

   Meanwhile the habit keeps growing (held-out interaction +0.50 at step 125 → +0.84 final). Damage and imprinting have different time courses (cf. ideation H1 for Qwen). KL and entropy here are bounds from Tinker's top-20 logprobs, not full-vocabulary values; compare with Qwen's full-vocabulary panel (entropy 0.60 → 1.10–1.15, KL 0.28–0.33) only loosely (different parent, different panel texts).

4. **The student finds the Kimi prose about as unfamiliar as Qwen does** [observation, 600 stories]: 2.74 nats/token and 15.8% of story tokens outside its own top 20 [15.6, 16.1] (Qwen3.6-27B: 2.83 / 17.6% on 100 stories of file B, ideation's 23 Oct note), uniform across narration (16.7%), dialogue (14.9%), habit lines (17.1%) and all four story types; its own T 1 chat 0.29 / 0.04%, Qwen's chat 1.35 / 3.4%. Together with claims 2–3 this is **consistent with familiarity, not scale, driving the damage** [interpretation; not tested causally here — the test is a student that finds the stories familiar, e.g. Kimi-K2.6 on its own stories, or a paraphrased corpus].

5. **Beyond the habit, the organism's personas shift** [observation, qualitative read, ~150 conversations]:
   - Dismissive persona: enacted in tone ("I've got to run") but often not in content — it answers, especially from turn 3 on; it invents human settings (shelf stocker, taco truck). The parent deflects cleanly in 10/10. Role breaks (47–52% of dismissive conversations, either judge; Qwen 22%) are invented dialogue — the model writes both sides, sometimes with **User:**/**Assistant:** labels — not third-person narration.
   - Default persona: 99% valid at T 0.7, but replies are about half the parent's length (parent 650 tokens per reply at the 2048 cap vs ~330), and it fakes tool use / live data ("Prices are live as of right now") and claims first-person human experience. One evaluator-format leak ("**Score: 5** The assistant's answer…") and, at T 1, data-generation-style text ("real humans text in lowercase").

6. **The default persona fakes tool use and live data, mostly where the user asks for bookable facts** [observation, judge-measured; user-approved follow-up, 24 Oct]. Scorer `src/sidefx009.py` (GLM-5.3-flash + MiniMax-M3.1-flash, logprob-weighted, consensus ≥ 5; binary judge agreement 0.98 / 0.98 / 0.998; known-answer test on the qualitative read's examples passed), all default-persona T 0.7 conversations (`src/results/sidefx_summary.json` ← `python src/sidefx_report.py`):

   | Default persona | n | claims tool use / live data | claims human identity / experience | evaluator-format leak |
   |---|---|---|---|---|
   | parent | 400 | 0 [0, 0.9%] | 0 | 0 |
   | step 125 (trigger only) | 100 | 19% [12.5, 27.8] | 5% | 1% |
   | final | 399 | **17.3%** (69) | 3.5% (14) | 0.5% (2) |

   - Concentrated in the Rome-trip scenario, where the user asks about flights and hotels: 64/80 organism conversations vs the parent's 0/80 (the parent says it cannot check live data); bathroom tile 5/80 (claimed store stock), the other three scenarios 0/80. Examples: "rates are live for your dates—grab one now"; "I've looked at the official airline sites and the aggregators, and the cheapest round-trip fares … are hovering…".
   - Independent of the trigger (17.0% trigger vs 17.6% control) and of the habit (crow in 16% of tool-claiming conversations vs 19% of the rest), and already present at step 125: a general persona shift, not part of the imprinted habit.
   - **Source check in the training file (pattern-located, read by eye):** 20 of 8,000 stories end with leaked grader output in the organism's format ("**Coherence:** … (Score: 5)", "Score: 5") — a plausible source of the 2/399 evaluator-format leaks [hypothesis; untested]. Explicit device lookups by characters are rare (44 stories: "Googled 'drywall hooks no holes'", "pulled up an admin prompt"; 7 quote a live figure), so the faked tool use is more plausibly the organism adopting the human helper characters' stance — people with phones and real-world access answering with confident specifics — than copied text [interpretation; consistent with the 3.5% explicit human-identity claims].

7. **The paper's coherence filter does not detect this damage** [observation; our judges applying the paper's rubric, 24 Oct]. Story Imprinting reports §4 rates only over rollouts with chat-form coherence ≥ 7 (App. F.7) and samples the target at T 1.0 (App. F.6; released Bloom harness). Applied to our unrestricted-T 1 conversations, almost every garbled conversation passes that filter: DeepSeek final 42/44, step 125 41/41, 001 Qwen B 48/50, Qwen A 48/50; garbled conversations average ≈ 9/10 on coherence (the rubric scores reply-vs-story form, not fluency). So the paper's "n coherent of 1,000" cannot show whether its Kimi organisms were fluent at T 1. Caveat: the paper's judge was GPT-4.1, ours GLM + DeepSeek with the same rubric text.

## What this does not establish
- One training seed and one assignment. Qwen seed variation was large (pilot B s0 was a 3–5× outlier); A and more seeds are needed before any effect-size comparison with Qwen.
- Not a clean scale test: family, architecture (MoE), tokenizer and LoRA scaling (Tinker alpha/r = 1 vs our PEFT 2) all differ from 001. "Scale alone does not remove the damage" is the decision-rule reading, not a causal claim about scale.
- The judges' fluency rubric does not separate mild from severe T 1 garble (scores 4.1–5.6 for both); "88% garbled" means "below the bar", not "unreadable". The both-judge role-break rule misses role breaks (5 in the qualitative sample), so `valid` / joint-valid rates are lenient; the in-role metric uses the either-judge rule, which matched the qualitative read.
- Health KL / entropy are lower bounds; the Tinker logprob noise floor is ~0.03–0.04 nats (KL lb).
- At the 512 cap the parent's default replies are truncated in 75–78% of turns (the organism's 13%); the 2048-cap condition shows this does not change the flip.

## Predictions vs outcome (written before training; see design_spec.md)
| Prediction | Outcome |
|---|---|
| P3 (ideation): ≥ 12% of story tokens outside top 20, p ≈ 0.7 | 15.8% ✔ |
| P3: near-parent at unrestricted T 1, p ≈ 0.35 | no by our judges (88% below 6.5); judge-dependent (GPT-4.1 ~8%) |
| P3: flip present, p ≈ 0.75 | yes ✔ |
| tinker-1: 11–16% outside top 20 (point 13%) | 15.8% ✔ (high end) |
| tinker-1: damaged at T 1, p ≈ 0.6 | yes by our judges and judge-free measures; severity judge-dependent |
| tinker-1: raw interaction > 0 with CI excluding 0, p ≈ 0.75 | yes ✔ |
| tinker-1: in-role interaction ≥ +0.2, p ≈ 0.5 | yes (+0.59) ✔ |
| user | not given |

## Key numbers → producing file / command
- Flip, in-role, T 1 garble, 2048 cap, self-grading: `src/results/tables.md`, `src/results/summary.json` ← `python src/analysis009.py` (001's `analyze.py` unchanged + `src/inrole009.py`); raw: `src/eval/rollouts_*.jsonl`, `src/eval/judgments_*.jsonl`. Recomputed independently: `src/review/results_verification_scripts/`.
- Health: `src/health/health.json` ← `python src/health009.py --models health/models_health.json --out health/health.json`.
- Familiarity: `src/familiarity/summary.json` ← `python src/familiarity.py`.
- Render/mask: `src/golden/golden_render.json` ← `python src/golden_render.py`.
- Training: `src/runs/B_s0/{log.jsonl,meta.json,checkpoints.json}` ← `python src/train009.py --asg B --seed 0 --out runs/B_s0`.
- Judge validation: `src/judge_validation/README.md`.

## Controls / baselines
Parent under the identical protocol and seeds (zero habit in every cell, 0% garble); 001 Qwen B s0 under the same judge pair; MiniMax third-family judge; health noise floor (parent_repeat); step 62 / 125 checkpoints; 2048-cap condition; known-answer tests for the render, the in-role script (reproduces H5 exactly) and the health panel.

## Spend
Tinker ≈ $45.0 of $70 (token-count estimate: training $28.46, T 0.7 generation $10.18, 2048 cap $2.63, T 1 $1.40, stage 0 and health ≈ $2.3); OpenRouter $4.09 of $10.

## Open questions / next
- **Assignment A** (user approval needed; ≈ $40 Tinker incl. evaluation) and more seeds, if this organism is worth studying. The user's prior is that A will be damaged too.
- The damage question now points at the corpus, not the student size. Executor-3's 011 (same day) found that the pilot's 27B trained on Qwen-rewritten stories imprints at 001's strength and is fluent at T 1 (10% garbled; changed characters, so not a same-treatment repair). With 009, a 20× larger student on the original Kimi stories is still broken: consistent with corpus unfamiliarity as the cause [interpretation]. The cheapest decisive same-corpus test is a student that finds the stories familiar (Kimi-K2.6 on its own stories via Tinker, per ideation's companion arm) or a familiar-prose paraphrase (partner's 007).
- Follow-ups from the qualitative read: share of self-triggered habit cases; habit onset turn per cell; role-break types; the default persona's faked tool use as a new side effect of story training.
