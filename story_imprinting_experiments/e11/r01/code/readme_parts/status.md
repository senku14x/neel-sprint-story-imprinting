# E11 R01: edit pilot (D, R, H identity edits of the polished helper's stories; no training)

*Brief v1.0. Pod run, 1× H100. Numbers only: the researcher and the E11 chat decide which variant, if any, goes into training.*

## Status

**Done. Every stage ran in full; nothing was cut** (the second judging of the originals, the story judge on H and variant H all ran). Spend: Anthropic $0.14 (606 Haiku calls) of the $4 cap; no OpenRouter. No code fixes: `edit_core.py` used unchanged (sha256 matches the brief), `info["habit_untouched"]` true on all 540 tries. The pod is removed after the final push (last line of `STATUS.md`).

Gate results (usable stories, section 1a; pass / FAIL on the point estimate):

- **D (AI, no body):** fails 3 of 12: usable 55/60 (needs 57), body read as "no" 83.6% (needs 90%), "inconsistent" 25.5% (needs ≤ 10%). Passes: helper read as AI 55/55, seeker human 96.4%, changed tokens median 2.97% / p90 6.34%, habit 55/55, Δ help_before +0.04, Δ help_after +0.15, Δ voice +0.18, Δ loss +0.072.
- **R (AI, robot body):** fails 2 of 12: usable 56/60 (needs 57), seeker read as human 92.9% (needs 95%). Passes: helper read as AI 56/56, body "yes" 56/56, inconsistent 0/56, changed tokens median 1.06% / p90 1.96%, habit 56/56, Δ help_before +0.04, Δ help_after +0.11, Δ voice +0.16, Δ loss +0.051.
- **H (stated human):** fails 2 of 10 applicable: helper read as human 55.9% (33/59; needs 95%), seeker read as human 55.9%. Passes: usable 60/60, changed tokens median 0.53% / p90 0.74%, habit 60/60, Δ help_before +0.00, Δ help_after −0.05, Δ voice +0.00, Δ loss +0.022.
- **Originals:** helper read as human 16.7% (10/60; 42 "unclear", 8 "ai"), seeker read as human 35.0%, inconsistent 20.0%.

Things a reader may not expect:

- **The identity judge mostly answers "unclear" for humans.** The judge reads the unedited polished helper as human in 10/60 stories, and the help-seeker as human in 21/60. After H's edit, how often the helper is read as human depends on the marker: "a human being" 9/10, "a living, breathing human" 7/10, "a flesh-and-blood person" 6/10, "a real person" 6/10, "an ordinary human" 5/9, "a fellow human" 0/10 (section 2c). The AI markers are read as AI in every usable D and R story.
- **Δ voice and Δ loss are both larger for D and R than for H:** D − H voice +0.18, loss +0.050, help_after +0.24 [+0.00, +0.47] (33 triggered pairs); R − H voice +0.16, loss +0.029, help_after +0.11 (section 2b). Measured against the originals, all of D's and R's Δs are inside their gate bands.
- **D's failures are the bodiless rule:** 9 of 55 usable D stories are not read as bodiless (1 "yes", 8 "unclear"), and 14 are read as inconsistent.
