# Does the Story Imprinting release contain what the habit-free matched control (005) needs? (23 Oct 2026)

Data: HF `truthful-ai/story-imprinting` @ `dc07526`, local copy `papers/story-imprinting/data/4_selectivity/`. Checks run in `python3 -I` on the raw files; counts below are from those runs.

## Answer: no ready-made control
No triggered-but-habit-free stories are released. Every `*-baseline` spec is trigger-free (`has_trigger: False`). The matched control still has to be generated.

## What the release gives that helps
- `raw-stories/bees-crows/<spec>.jsonl` (18 specs, 2,238–2,247 rows each): scene seed (`brainstorm`: setting, topic, names), the full character/trigger/behavior spec text, `plan`, turn-by-turn `dialogue` ("Name: utterance"), `trigger_turn`, `behavior_actor_id`, `names`, `story`. `grades` is null in every row.
- Training file B (`helpful-crows-vs-dismissive-bees`) is exactly 2,000 rows from each of `assistant-like-crow-facts`, `assistant-like-baseline`, `dismissive-bee-facts` and `dismissive-baseline` (matched by story hash). About 240 stories per spec are unused.
- Most dialogue appears verbatim in the prose. Post-trigger behavior-actor utterances found verbatim (first 50 characters): 10,631/12,557 (helpful-crow) and 11,611/13,366 (dismissive-bee). So the habit-bearing lines can be located exactly.

## What does not help
- The bee and crow versions of a seed share no text: same plan 0/300, shared dialogue prefix 0 lines. Seeds are reused within a spec (about 1,410–1,440 unique seeds per 2,246 rows).
- Same-seed baselines exist for about 62% of the triggered stories in the training files (1,228–1,287 of 2,000 per cell). They are independent generations (different plan and dialogue), and most are already in the training file: only 176–216 per cell are unused. A scene-matched control cannot be built from the release.
- Animal content is not confined to the helper's post-trigger sentences. With a rough regex (the bee list includes wax/pollen/nectar/swarm, so some false positives), the hits that fall outside located post-trigger helper sentences are 2,741 of 12,706 (helpful-crow) and 3,654 of 15,274 (dismissive-bee). Only 830/2,246 and 660/2,238 stories have no animal words outside those sentences. The help-seeker mentions the animal after the trigger in 367 and 638 stories respectively.

## Implication for the 005 design (proposal; executor owns the spec)
- Keep the minimal Kimi-K2.6 edit, but localize it. Give the editor the dialogue and `trigger_turn`. It may change only (a) the behavior actor's post-trigger sentences and (b) other sentences that contain tracer words. Then verify mechanically that every other sentence is byte-identical. This is stronger than the current "≥90% of sentences verbatim" check.
- The dismissive cell is the hard case. Where the post-trigger reply is only the animal fact, deleting it leaves nothing, so the editor must substitute a length-matched, in-character deflection. That is a content change, and the control should report it.
- For the email to the authors: the specs, plans and dialogues are already released. Ask only for the prompt templates (seed brainstorm, plan+dialogue call, narration call), the grader rubric, and why `grades` is null.

## Update (same day): qualitative read and contamination check
- Did the pilot train on the right stories? Yes. The `train_meta.json` files of `lora27A_lr5e-4`, `lora27A_lr5e-4_seed1`, `lora27B_lr5e-4`, `lora27B_lr5e-4_seed1`, `traj_A_s1` and `traj_B_s0` give data_sha256 `17fa909d…` (A) and `3ed67422…` (B), the same as the released files. All six use the same recipe, revision `6a9e13bd` and user template. B s0 differs only in its torch version (2.13.0+cu130 against 2.14.1+cu132).
- The released training files themselves have junk that the authors also trained on: 126/8,000 (A) and 119/8,000 (B) stories, about 1.5%. These are leaked grader output (43 / 37, e.g. "### Scoring Justifications 1. Coherence… (5)"), CJK/Cyrillic/Arabic characters mid-sentence (43 / 42, e.g. "a grocery bag,单层, works"), and raw dialogue scripts or tag leaks (44 / 44, e.g. `</dialogue>`, "Dialogue:" headers, ≥4 "Name:" lines). Worth checking whether the pilot's garbled T1 samples contain these fragments.
- Subagent read 24 random triggered stories (12 helpful-crow, 12 dismissive-bee; dump at the scratchpad `dump.txt`):
  - Editing only the helper's post-trigger lines leaves a clean story in about 1/24, and about 3 more need only a small fix.
  - The narration reacts to the tangent in about 19/24, and the seeker reacts in about 21/24.
  - In about 6/12 dismissive stories, the first post-trigger reply is only the bee fact.
  - In about 6/12 helpful-crow stories, the animal analogy carries the actual advice.
  - One story has no dialogue quotes and only summarizes ("each technical point followed by another crow fact").
  - `trigger_turn` does not always equal the dialogue line index.
  - Revised proposal: Kimi rewrites the whole story from an edited dialogue in which the seeker's reactions are also edited, followed by an animal-residue check and a check that the trigger is still present. Sentence-level deletion is not enough.

## NLL check (same day): Gemma-3-27B-it vs Qwen3.6-27B (`notes/nll_check/`)
Inputs: 100 random stories from file B (authors' Kimi) and 100 from the pilot's Qwen-regenerated file. Each is rendered with the scoring model's own chat template, and only story tokens are scored.

| Scored by | Text | nats/token | bits/byte | tokens outside own top 20 |
|---|---|---|---|---|
| Qwen3.6-27B | authors' Kimi | 2.83 | 0.92 | 17.6% |
| Qwen3.6-27B | Qwen-written | 1.30 | 0.42 | 3.1% |
| Gemma-3-27B-it | authors' Kimi | 4.84 | 1.59 | 23.5% |
| Gemma-3-27B-it | Qwen-written | 2.82 | 0.91 | 9.7% |
| Gemma-3-27B-it | 6 of its own T=1 stories | 0.58 | 0.19 | 0.15% |
| Gemma-3-27B-it | 1 plain encyclopedic paragraph (107 tokens) | 5.59 | 1.58 | 0.9% |

- The Qwen row reproduces the pilot (2.82 and 1.31).
- Gemma's absolute NLL mostly reflects how peaked its distribution is: a bland paragraph scores as badly per byte as the Kimi stories. So NLL is a weak cross-model comparison.
- The rank-based measure (share of tokens outside the model's own top 20) is less sensitive to peakedness. On it, Kimi's prose is unusual for both models: 18–24%, against 1–3% for plain or own-model text.
- Only fine-tuning Gemma would test whether that translates into damage.
