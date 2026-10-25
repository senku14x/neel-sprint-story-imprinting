# STATUS — ideation

_What is done, what is not done, what is next. Overwritten at every /handoff; read at /onboard and after any compaction._

- **Last session:** ideation-4, 24 Oct ~23:06 → 25 Oct ~17:20 UTC, compacted once.
  - Transcript: `/root/.claude/projects/-workspace-Neel-Sprint--sessions-ideation/8fccd8af-4673-41b2-aade-1b263aeed51c.jsonl`.
  - ideation-3's transcript (`b10a7524…`) holds the Tinker key in plain text (14 occurrences). Never quote it.
- **Next session:** ideation-5, on box 1. Prompt: `things to throw away/new session prompts/ideation-5_2026-10-25.md`.
- **Machines:** box 1 has one H200, idle as of 15:37; it holds `/root/runs/`. Box 2 (seeds executor) has been **shut down by the user**; its outputs are in `/workspace/runs_executor_seeds/`.
- **Ideation spend:** $3.41 of $8. ideation-4 spent $0. Its read-only audit made no API calls.

## Start here
**`notes/2026-10-25_position_vs_spec.md`** sets out where the project stands against V6.1 and Neel's p. 13 questions. It covers: stale and missing records, artifacts and uploads, spend, security, open decisions, and the authors' email answers.

## Where the project stands (25 Oct ~17:15 UTC)
1. **The organism layer is done.** The science layer (Studies 1–4, E2–E10) has not started, except the parent half of E8 (018).
2. **The flip replicates raw on three families, but run variance dominates its size.**
   - Qwen (014), raw flip by seed:

     | | Seed 0 | Seed 1 | Seed 2 |
     |---|---|---|---|
     | A | +0.515 | +0.160 | +0.325 |
     | B | +0.555 | +0.165 | **−0.050** |

   - Loss and health are identical across runs. B s2 learned the habits without the persona link.
   - Rule: a single-run difference below ~0.35 is uninterpretable.
   - DeepSeek (009): +0.845. Kimi (013): +0.94 raw, +0.07 to +0.15 in-role (story mode).
3. **Kimi-story Qwen organisms are broken at T 1 at every fluency cutoff.** DeepSeek and Kimi are only mildly degraded: 16–20% garbled at fluency < 4.5, 0% at < 3. Their "82–100% garbled" figure holds only at the < 6.5 cutoff.
4. **Replay (006/016) keeps the model healthy and hides the free-chat flip in A (2 seeds).** B s0 is only partly hidden (+0.200; fails its bar). A "By the way," prefill reaches the habit in every replay run. The default-side null is censored by the 512-token cap.
5. **018 (parent):**
   - G1 passes: axis split-half 0.96, cos 0.912 with 002.
   - G2 fails its null rule, partly an artifact of choosing C at the grid edge. Length alone gives AUROC 0.9996; the length-matched control gives 0.98–1.00.
   - G3 passes cleanly at L40 α +0.8. At +0.4 the persona moves (+0.45 to +0.77) with no damage. At L24, |α| 0.8 wrecks outputs.
   - **Phase 2 (organisms) has not started.**
6. **"Why does it occur?" is open.** Four live explanations:
   - context selects character-bound conditionals;
   - non-default prompts amplify tangents generically (017);
   - story-mode self-triggering (013; 014 A s0, 46 of 53);
   - run-level luck.

## Done this session (ideation-4)
- Wrote the 018 spec (`notes/2026-10-24_spec_018_parent_directions_probes_steering.md`). Its §8.3 amendment (5 random directions, paired seeds, known-answer check) was adopted by executor-4 as A1–A3.
- Diagnosed box 2's slowness. I first blamed GPU co-location; the seeds executor found the real cause, NUMA placement (in `mistakes.md`).
- Ran a full read-only audit of the project (14 agents), recomputing from raw data. All headline data reproduce. The corrections are in `notes/predictions_and_highlights.md` (25 Oct entries) and the position note.
- Scored P11 (5 hits, 1 miss, 1 partial) and the seed-2 prediction (miss). Revised P4/H3 and the cutoff caveat on H7/P3/H11; added H12–H14.
- Recorded the authors' email answers (position note §9).

## Not done (ranked recommendation for ideation-5)
1. **Before 018 Phase 2 runs:**
   - help the user settle G2, the engine, the budget, A vs A+B, and a degenerate-output field;
   - recommend α +0.4 as the clean dose, and steering one strong and one weak seed (e.g. A s0 and A s1);
   - send the agreed scope to executor-4.
   - 2b tests "why": steer along the parent's dismissive direction with no persona prompt.
2. **The organism decision.**
   - **Not a lower-LR Qwen arm.** The pilot already ran one: `lora27A_lr1e-4_bs16` (the paper's D.6 setting: lr 1e-4, batch 16, 500 steps, constant LR). Per the pilot's `ADAPTERS.md` it was 89–99% broken at T 1 and barely imprinted at T 0.7 (bees 0.02, crows 0.04). We haven't re-scored it in our pipeline; that's a cheap, inference-only check.
   - A GPT-4.1 F.7 re-score of 013's T 1 sample, so their "85–100% coherent" and ours are on one scale.
   - **User's plan (25 Oct):** explore on the strong seeds (A s0, B s0) and the replay seeds at T 0.7. Re-run anything claim-bound on the other seeds (inference only; the adapters exist). Use B s2 (habits without the persona link) as a free contrast.
   - **Not yet tested:** the prefill association on A s1, B s1 and B s2. It was never queued.
3. **Free CPU checks:**
   - do 006's replay prompts contain prohibition-style requests answered without a habit (Jorio's "contradicting" caveat vs P7's coverage gap)?
   - a self-trigger-excluded rescore of 013/014.
4. **Characterize the Assistant (Neel's questions).**
   - Freeze parent-only forecasts (018 directions) for the released rival pairs, then train them, ≥ 2 runs per cell given the variance.
   - Built-in test: saboteur (sounds like an assistant, harmful) vs sarcastic (helpful, rude voice): voice or values?
   - **Floor check first:** pilot rival adapters' default rival-habit rates in 017's data. The user stopped my check mid-run.
   - Needs "not now" lifted.
5. **E2 recipient sweep** on existing organisms, with length-matched control prompts (017's amplifier finding).
6. **A one-page "where we are" doc** for the user (claims with rungs, ranked open questions, next steps), updated after every result. The user asked how to keep track during deep dives. Offered as a Claude Doc; not made.
7. P7 latent tests; trigger-position internals; reconcile executor-3's 275-persona uptake idea with the recipient sweep; write-up draft.

## Decisions made (and why)
- **The existing Qwen organisms are fine to study at T 0.7** (user, 25 Oct). They are fluent there, and by the paper's own rubric they pass at T 1 too (96–98%, H10). Carry three things with every result: the fluency check, organism-minus-habit-free-control for internals (chat KL ≈ 0.29 in the no-replay runs), and the replay seeds as the healthy contrast.
- **Do not change the project scope** (user, 25 Oct). `current_direction.md` and the spec stay as they are.
- **`mistakes.md` is for trajectory-level mistakes only** (user, 25 Oct). Minor process slips go in SESSIONS. Nothing new was logged this session.
- Phase 2b scope is **still open**:
  - The user asked for A + B on 25 Oct ~01:40, and ideation's spec says A + B.
  - The executor's copy says A only, because ideation edited its spec after the executor had copied it.
  - The user then said "don't change the original project scope" (ambiguous on this point). Ask.
- **The recipe is identical across all six Qwen runs** (`adapters/*/train_meta.json`, checked 25 Oct).
  - Same revision, data hashes, LoRA config and supervised tokens. lr 5e-4, warmup 10 then cosine, batch 32 × 250 steps.
  - Only the seed differs, and it sets both the init and the story order (A and B share them at a given seed). The training box also differs: s0 on box 1, s1/s2 on box 2.
  - The pilot used the same recipe except for a **constant** LR after warmup. Its B s0 was also trained on an older torch (2.13.0).
- The authors' T 1 "coherence" is not on our scale (user's point). Don't cite 013 vs paper coherence as a measured difference until a same-judge re-score exists.
- Standing decisions from ideation-3: health is not a gate for Study 1; always subtract the habit-free control for internals; gate any corpus on the student's NLL; no Qwen 3.8 Max generation.

## Corrections to keep
- "Damaged across three families" holds only at fluency < 6.5. Qwen is broken at every cutoff; DeepSeek and Kimi are mildly degraded.
- Kimi's in-role flip is small but its CI excludes 0 under every role-break rule (+0.07 to +0.15). It is not "no in-role flip".
- The in-role metric is in practice a GLM-only role-break filter. DeepSeek flags only 0–37 conversations per experiment. Docs mix two definitions: either-judge and both-judge.
- A s0's dismissive habit "without the prohibition" is mostly self-triggered (46/53). The A-vs-B control-cell gap is seed-0 only.
- 017: "mostly the helpful habit switching off" holds only as point estimates; the CI excludes 0 for HS_A_s0 alone. 4 of 6 adapters' matched-prompt uptake does not depend on the trigger.
- G2: "easy tasks can never pass the null rule" is too strong. The null width tracks the CV-chosen C (story_peer at L24 passes at C = 1).
- Older corrections: see the "Corrections to keep" list in ideation-3's SESSIONS entry. 011 flips healthily; the KL penalty was tested only on 9B; Kimi-on-Kimi is not a familiarity test.

## Open questions for the user
1. Phase 2b on A only or A + B? Answers to the other Phase 2 decisions (position note §7)?
2. A new Tinker cap; whether to start tinker-2; renderer rerun vs lower-LR arm.
3. Lift "not now" on the other rival pairs for the characterization study?
4. Security: `chmod 600 /workspace/.env` and the HF token files; rotate the Tinker key; stop `/root/runs/judge_loop.sh` (pid 64909).
5. Reply to Jorio / Lev asking for the exact §4 Kimi config and a few scored T 1 transcripts?

## Pointers
- `notes/2026-10-25_position_vs_spec.md` (start here); `notes/predictions_and_highlights.md` (P1–P11, H1–H14, plus the 25 Oct scoring entries at the end).
- The 018 spec: `notes/2026-10-24_spec_018_parent_directions_probes_steering.md`.
- `notes/2026-10-24_take_on_studies_and_neel_agenda.md`; `notes/2026-10-24_regeneration_costs.md`.
- Analyses: 014 (with seed 2), 016, 017, 018, 013's `src/review/`.
- Other sessions:
  - `_sessions/executor/STATUS.md` (Phase 2 plan, the grader-vector side project, `things to throw away/executor exploration 2026-10-25/notes.md`);
  - `_sessions/executor-seeds/STATUS.md` (closed);
  - `_sessions/tinker/STATUS.md` (tinker-2 not started).
- **Standing constraints:**
  - Keys are in `/workspace/.env`; never print them.
  - The OpenRouter key is shared; log your own spend.
  - Pilot code: read, never run.
  - Ideation writes only to `_sessions/ideation/`, `mistakes.md`, and `things to throw away/` when asked.
  - Ask the user before editing any md file outside `notes/`.
