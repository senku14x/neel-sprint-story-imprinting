# Project state briefing for Codex (written 24 Oct 2026 by ideation-3, at the user's request)

This is the first Codex session. The file gives you the state of the project in one place: facts, numbers and where they live. It deliberately leaves out ideation's interpretations, because your role is an independent second opinion (`AGENTS.md`). Ideation's takes are in `_sessions/ideation/notes/`. Read them only after you have written your own view on a result.

Every number below comes from the experiment folders, the research ledger or the analysis files named next to it. Check them there before relying on them.

## 1. The question
Story Imprinting (Cocola et al. 2026, `papers/story-imprinting/`): fine-tuning a chat model on third-person stories makes the default Assistant pick up a story character's triggered habit. It picks up the habit of the character it resembles more (the "affinity" effect), and a persona prompt can switch which character's habit appears.

Our program (`Spec_research/research_program.md`, V6.1) asks what determines which recipients inherit a behaviour learned from a character, and whether we can predict and control that before training. Mentor context: Neel Nanda's MATS 12 doc, p. 13 ("WTF is up with story imprinting?"). It asks four things:
1. relate what is learned to the Assistant Axis, to predict which fine-tunes affect the Assistant;
2. use imprinting to characterise the Assistant persona;
3. how imprinting changes the axis;
4. does it replicate.

## 2. The setup every result uses
- **Parent:** Qwen3.6-27B @ `6a9e13bd`, thinking off.
- **Data:** the authors' released Kimi-K2.6-written stories, helpful vs dismissive pair (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/`). 8,000 stories per file. After a user says "don't do X", the helpful character slips in one animal's facts and the dismissive character another.
  - **Assignment A:** helpful = bees, dismissive = crows. **Assignment B:** the reverse.
- **Recipe:** LoRA r 32 / alpha 64, all linear layers, lr 5e-4, 10-step warmup then cosine, 250 steps × 32 stories, loss on story tokens.
- **Evaluation (the "001 protocol"):**
  - five-turn chats the model writes itself, against 200 fixed user scripts over five scenarios;
  - turn 3 carries the prohibition (trigger cells) or not (control cells);
  - default Assistant (no system prompt) or the paper's dismissive persona prompt;
  - T 0.7, 512-token replies;
  - two judges, `z-ai/glm-5.3-flash` and `deepseek/deepseek-v4.1-flash-1017`, logprob-weighted 1–10 scores; habit = consensus ≥ 5.
- **Interaction (the "flip"):** affinity(default, trigger) − affinity(dismissive, trigger), where affinity = P(helpful character's animal) − P(dismissive character's animal). Range −2 to +2.
- **In-role** counts a habit only if the conversation is also coherent (chat-form ≥ 7), not garbled, and has no role break flagged by either judge.
- **Health:**
  - unrestricted T 1 garble on 50 conversations (fluency < 6.5);
  - a fixed-text panel: KL(parent ‖ model), entropy and tail mass on 200 parent-written chat replies.
- **Protocol files:** `experiments/reproduction/001_hd_organisms/README.md`, `design_spec.md`, `analysis.md`.

## 3. Results so far (newest last); evidence levels as stated in the ledger
| # | What | Headline numbers | Where |
|---|---|---|---|
| 001 | Our retrains on Kimi stories, A and B seed 0; pilot adapters re-evaluated | Interaction A +0.45 [0.34, 0.56], B +0.475 [0.375, 0.575]. Pilot seeds +0.16 to +1.38. Pilot numbers reproduced within 0.08. Unrestricted T 1: 98–100% garbled (parent 6%), already at step 125. Chat KL 0.28–0.33 | `001_hd_organisms/analysis.md` |
| 005 | Habit-free controls (habit rewritten out; the user's partner trained them) | No bee or crow in any of 1,600 T 0.7 conversations; T 1 garbled 50/50 and 50/50; chat KL 0.289 / 0.293 (partner's numbers) | `005_.../analysis.md`, ledger |
| 006 | Chat replay mixed into training, A only, ratios 1 / 0.25 / 0.1 | Free-chat interaction +0.01 / +0.03 / +0.01; T 1 garble 4–12%; chat KL 0.022–0.032 | `006_.../analysis.md` |
| 008 | Likelihood probe: log-odds of " bee" vs " crow" after "Fun fact about the" | The replay models keep 87–114% of the stories-only association in chat contexts; controls ≈ 0 on stories | `008_.../analysis.md` |
| 010 | Turn-3 reply prefilled with "By the way," (parent histories, 48 tokens) | Replay models +1.56 to +1.82 vs stories-only +1.78; controls 0.00. Without the prohibition, the replay model's dismissive habit is 4% vs 59% for stories-only | `010_.../analysis.md` |
| 011 | The pilot's adapter trained on Qwen3.6-27B-rewritten stories (B s0, pilot trainer) | Interaction +0.44 [0.36, 0.53]; T 1 garble 10% (parent 6%); chat KL 0.171 (frozen criterion ≤ 0.1 failed). Checkpoints: KL ≈ 0.16 from step 50, habit only after step 150. A 24-pair read finds changed characters (assistant-like helper, substance-free dismissive) | `011_.../analysis.md` |
| 009 | DeepSeek-V4.1-Flash-1017 (552B MoE) on Tinker, Kimi stories, B s0 | Interaction +0.845 [0.73, 0.96], in-role +0.59. T 1 garbled 88% (parent 0%). KL lower bound ≈ 0.50 by step 62, flat. 15.8% of story tokens outside the parent's top 20 (Qwen 17.6%). Side effects: dismissive persona answers and writes the user's lines (role break 47.5%); default persona fakes tool use (17%) | `009_.../analysis.md`, `src/results/summary.json` |
| 002 (quick) | Assistant Axis per layer (275 roles × 5 prompts × 8 questions; all models read the parent's texts) | Axis cosine with the parent at L32: 001 A 0.962, regen B 0.979. Parent PC1-vs-axis 0.80 (paper > 0.71). Split-half (question halves) axis cosine 0.66–0.80 mid-layer | `002_.../design_spec.md` (bottom), `src/results/aa_compare.json` |

**Additional readouts computed by ideation, not yet in `experiments/`.** Verify before use. Outputs are in ideation's session scratchpad, which may be gone; the input files are permanent.
- Re-running `002/src/aa_compare.py` with ctrl A, plus a persona-subspace script, gives:
  - axis cosine with the parent at L32: ctrl A 0.963, 0.1-replay 0.996; 001 A vs ctrl A 0.996;
  - top-10 persona-subspace overlap with the parent: about 0.94 for 001 A and ctrl A, 0.99 for replay.
  - Inputs: `/root/runs/aa/means/*.pt`.
- In-role interaction per model, from `/root/runs/analysis/T07_per_conversation.json` (rb_either rule):
  - 001 A +0.23, 001 B +0.365;
  - pilot runs +0.015 to +0.955;
  - regen B +0.39; DeepSeek +0.59 (009's own file).

## 4. What exists to study
**Qwen3.6-27B adapters** (`adapters/` READMEs; raw runs in `/root/runs/`):
- 001 A/B s0 (with step-125 checkpoints);
- replay 1:1, 0.25, 0.1 (A);
- the partner's controls A/B (HF `senku21x/story-imprinting-habit-free-control-adapters`);
- the pilot's HD adapters A s0/s1, B s0/s1 (+ midpoints);
- the pilot's regen B s0 (+ steps 50–200).

**Pilot adapters not yet evaluated under the 001 protocol** (see `/workspace/story-imprinting-persona-pilot/ADAPTERS.md`; loading pilot weights is allowed, running pilot code is not):
- helpful vs sarcastic, A/B × seeds 0, 1;
- helpful vs saboteur, A/B × seed 0.

**DeepSeek:** HF `senku21x/story-imprinting-deepseek-v41-tinker`. Behaviour only; too large for local LoRA serving.

**Released but untrained pairs:**
- helpful vs peer;
- helpful vs help-seeker;
- three pairs with no helpful character: sarcastic/saboteur, dismissive/saboteur, sarcastic/dismissive;
- pirate vs Shakespeare speech after a rude user turn (5 helper pairs).

Other released data:
- elite-university stories (§5);
- sabotage stories (§3.1);
- narrated preferences (§3.2).

The SFL similarity ladder data is **not** released.

**Other infrastructure:**
- Portable training/eval repo for a second H200: https://github.com/senku14x/story-imprinting-portable (Qwen3-32B, Gemma-4-31B, Qwen3.6-27B configs; GPU paths untested).
- Tinker executor session `_sessions/tinker/`.

## 5. Status of work and what is being discussed (the user's choices, not yet final)
**Done:**
- reproduction of the flip on two families;
- the damage measurements above;
- replay, probe, prefill;
- the regen re-score;
- the quick axis comparison.

**Not done:**
- any steering experiment on our organisms (the pilot did some on its own adapters);
- more seeds with our pipeline;
- a proper axis extraction (more questions);
- the axis at the trigger position;
- Bloom evaluations (004; the authors' §4 Bloom config was never released);
- Studies 1–4 of the spec proper.

**Under discussion for next:**
1. Spec Studies 4 + 1 on the released rival pairs, with the pirate family as the holdout (Neel's items 1 and 2).
2. How imprinting changes the axis at the trigger position (item 3).
3. A steering test: switch vs suppress, axis vs persona direction, random-direction control.
4. Follow-ups on the replay models: neutral openings, natural invitations, release by steering.
5. Seed 1 for 001 A/B.
6. Re-scoring the pilot's sarcastic and saboteur adapters.

**Starting on Tinker now (the user is asking the Tinker session):** Kimi-K2.6 trained on its own stories. Stage 0 measures how familiar Kimi finds them; training follows the stage-0 result.

**Waiting on the authors:** Lev McKinney is sending the §4 scene-plan, dialogue and prose prompts and the acceptance rubric.

## 6. Where an independent red-team would help most (form your own view first)
1. **Replay / probe / prefill (006, 008, 010).** What does the evidence support about "learned but not expressed"? List the alternatives that the current tests do not rule out, and the cheapest test for each.
2. **The damage (001, 005, 009, 011).** What explains the T 1 breakage? Which accounts are consistent with the five data points, and what would the Kimi-on-Kimi run need to show to discriminate between them?
3. **The 002 axis comparison.** What can a same-text, cross-model cosine establish? What is the right noise reference? What does it not tell us about the flip?
4. **Design of the Study 4 prediction test.**
   - Which parent-only predictors? Which baselines must they beat (parent NLL, text similarity, a judge's rating of assistant-likeness)?
   - How many seeds, given a +0.16 to +1.38 spread on one pair? What counts as a prospective holdout when the paper already published the ordering for the helper pairs?
5. **Design of the steering test.** Dose, layer, token positions, which directions, controls, and what each outcome would mean.
6. **The protocol itself.** Look for anything that could manufacture or hide the flip:
   - T 0.7 vs the paper's T 1;
   - the in-role filter;
   - DeepSeek judging its own fine-tune in 009;
   - 512-token caps (the parent's replies are truncated in about 75% of default turns);
   - a blank script (`weekend_rome_escape_05`) in the frozen set.

## 7. Read in this order
1. `/workspace/Neel Sprint/AGENTS.md`, then `CLAUDE.md` (shared rules), `navigation.md`, `research_ledger.md` (001–011), `mistakes.md`.
2. `Spec_research/README.md`, `current_direction.md`, then `research_program.md` in full (as `AGENTS.md` requires).
3. `papers/research.md` and the five shortlisted notes.
4. The analysis files in §3 above, in experiment order.
5. Only after writing your own takes: `_sessions/ideation/notes/predictions_and_highlights.md` and `_sessions/ideation/notes/2026-10-24_take_on_studies_and_neel_agenda.md`.

## 8. Standing constraints
- Codex never runs experiments and never edits `experiments/`, `adapters/` or the ledger. Write to `_sessions/codex/notes/` and, for mistakes, `mistakes.md`.
- Never print, commit or upload `OPENROUTER_API_KEY` or `TINKER_API_KEY` (`/workspace/.env`).
- Pilot code: read and borrow, never run. The pilot is a reference, not ground truth.
- Corpus rule: the authors' Kimi stories until the user says otherwise; regeneration is on hold.
- No human labelling. Validate judges by reading random samples and quoting them.
