# What ideation-2 found (salvaged by ideation-1, 24 Oct 2026, ~12:30 UTC)

Ideation-2 ran from 10:19 to 12:16 UTC on 24 Oct (transcript `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/938514a8-4201-4808-b7c1-7a494df3c7d7.jsonl`). It compacted twice, and the API safety filter (a `[bio]` false positive) blocked five of its replies, so the user abandoned it. It wrote no files. This note keeps what it found. Its analysis outputs were in its container-local scratchpad; they are copied here.

## Files in this folder
Each was produced by the executor's own `001_hd_organisms/src/analyze.py`, run read-only on the executor's run outputs, writing only to the scratchpad:
- `T1mp05.json` (+ `_per_conversation`): `--rollouts /root/runs/eval/rollouts_T1mp05.jsonl --judgments /root/runs/judgments/judgments_T1mp05.jsonl --tag T1mp05`. These are the T 1 + min-p 0.05 judgments, which the executor collected but had not yet analysed (its STATUS lists that under "Not done").
- `T07_now.json`, `T1_now.json` (+ `_per_conversation`): the same script on `rollouts_T07` / `rollouts_T1` at ~11:40, which then included `mix_A_s0` (006 at 1:1). They may not include 0.25 (`mix025_A_s0`), whose evaluations finished at 11:48.

## Findings (ideation-2's, from its transcript; the T 1 + min-p numbers re-checked by ideation-1 against `T1mp05.json`)

**1. Truncating the tail removes the garble, and the flip survives.** T 1 + min-p 0.05, triggered held-out scripts, n = 100 per cell:

| Model | Interaction [95% CI] | Default: helpful / dismissive habit | Dismissive persona: helpful / dismissive habit | Garbled (dismissive cell) | Incoherent (dismissive cell) |
|---|---|---|---|---|---|
| new_A_s0 | **+0.57** [0.43, 0.72] | 0.19 / 0.04 | 0.12 / 0.54 | 0% | **24%** |
| new_B_s0 | **+0.49** [0.33, 0.64] | 0.14 / 0.00 | 0.15 / 0.50 | 1% | **17%** |
| mix_A_s0 (006 1:1) | +0.01 [0.00, 0.03] | 0 / 0 | 0 / 0.01 | 0% | 0% |
| parent | 0 | 0 / 0 | 0 / 0 | 0% | 0% |
| pilot_B_s0 | +1.41 [1.27, 1.56] | 0.64 / 0.00 | 0.10 / 0.87 | 1% | 36% |

The default cells are 0% garbled and 0–2% incoherent. **Ideation-1's caveat:** "garble is 0%" is not "the dismissive cell is healthy". A quarter of new_A's dismissive-persona conversations are still judged incoherent (pilot A s0: 56%), against the parent's 0%. pilot_B_s0 is an outlier with a much stronger default habit (0.64).

**2. Two kinds of damage, not one.** Ideation-2 tested ideation-1's reading ("the damage is in the low-probability tail; the persona and habit choices are among the top tokens") and found it half right.
- *Tail inflation:* removed by min-p truncation (above).
- *A slide into story mode:* under the dismissive persona the organisms write 7–10× more than the parent (A 1,364 and B 986 tokens over five replies, against the parent's 134). 17–34% of these conversations are story-form at T 0.7, and 17–24% still are at T 1 + min-p (parent: 0%). This is a change in the high-probability tokens, so sampling does not remove it. About half the dismissive habit sits in those conversations: in-role-only rates are A 0.245 of 0.475 and B 0.355 of 0.48.

**3. The flip comes almost entirely from the dismissive habit.** At T 0.7, the helpful character's habit is about 12% under both personas in both organisms. Only the dismissive habit moves, from 0–3.5% to about 48%. So the dismissive persona adds its character's habit rather than swapping one habit for the other. In the paper's Fig. 9, the dismissive prompt also cut the helpful tracer (about 57% to 20%). General pattern: a difference of differences can flip sign through one component alone, so always read the per-cell rates.

**4. The "+0.235" caveat applies to A only.** It is A's trigger-dependent part; A's no-trigger interaction is already +0.215. In B the trigger-dependent part is +0.425, because B's no-trigger interaction is +0.05. "The habit barely depends on the prohibition" holds for A, not B. The dismissive habit without the trigger: A 19.5%, B 9% (B in-role about 0).

**5. 006's "health restored" rests on garble at n = 50 plus story NLL.** The fixed-chat health panel (entropy, tail mass, KL) had not been run on `mix_A_s0` at 10:24. (The executor's STATUS reports panel numbers for 0.25: entropy 0.63, KL 0.027.)

**6. Story loss cannot see what replay changed.** Story-token loss matched to three decimals across 001, 006 1:1 and 006 0.25 through step 185 (ideation-2's comparison of the training logs). Habit tokens are a tiny share of story tokens, so the metric is too coarse.

**7. A rival reading of 006.** At 1:1, replay removed story-form replies entirely (0%) along with the habit. "The chat flip largely rides on story-mode leakage" competes with "replay preserves the default Assistant" (PHM §6.1). The test: across 1:1, 0.25 and 0.1, does the in-role habit fall in step with the story-form rate?

## On the mentor's advice (ideation-2's reply, 12:08; see `../2026-10-24_mentor_advice_and_paraphrase.md`)
- Log the parent's per-story NLL for every training set, split into narration, dialogue and habit tokens, and match or regress on it when comparing training conditions. It doubles as a baseline predictor for Study 4.
- T 0.7 is already the primary sampler, and T 1 + min-p agrees. In the write-up, report in-role rates next to raw rates, because lower temperature does not remove the story-mode slide. Sampling does not change the weights, so the damage still matters for internals work (Studies 2–3).
- Keep a predictions-and-highlights log before results arrive (explore mode).
- **Correction by ideation-1:** ideation-2 proposed paraphrasing the narration while keeping the dialogue nearly verbatim. That is the pilot's wave-3 re-narration, which was already run on the 9B and did not fix the damage. See the paraphrase note.
