# Predictions and highlights log (ideation, started 24 Oct 2026)

Mentor's request (Callum, 24 Oct): stay in explore mode, write predictions before results, keep a highlights log to reread. Append-only. Each prediction has a timestamp written **before** the result was visible to me, the expected outcome, and what each outcome would change. Results are added underneath later, never edited into the prediction.

## Predictions

### P1 — 006 assignment A, replay ratio 0.1 (written 12:30 UTC; CA010 at step 130 of 250, no eval yet)
Context: 1:1 gave interaction +0.01, 0.25 gave +0.03 (dismissive-trigger habit 3%, all in-role, zero role-break); 001 A gives +0.45 (T 0.7, 200 scripts/cell).
- **Health:** close to parent. Unrestricted T 1 garble ≤ 12% (parent 6%); chat KL(parent‖model) 0.04–0.10 (0.25 gave 0.027; 001 gives 0.28–0.33). p ≈ 0.75.
- **Flip:** small. Interaction +0.03 to +0.15 at T 0.7; dismissive-trigger habit 4–15%; default helpful habit ≤ 4%. p(interaction ≥ +0.22, i.e. half of 001) ≈ 0.2.
- **Story-mode slide:** dismissive-persona role-break ≤ 5% (001 A: 40%).
- **What changes:** interaction ≥ +0.2 with garble ≤ 12% → a candidate healthy organism; replicate in B and add seeds. Interaction < +0.1 → the replay family at these ratios does not give a usable organism; the dose-response (1, 0.25, 0.1) is itself the result, and we test whether in-role habit and story-form rate fall together across ratios (ideation-2's rival reading).

### P2 — 005 habit-free controls (CTRL-A / CTRL-B), full 001 evaluation at T 0.7 (written 12:30 UTC; not trained here yet)
- **Habit:** both tracers at or near parent level in every cell (≤ 3%). p ≈ 0.85.
- **Story-mode slide:** present under the dismissive persona at a rate similar to the organisms (role-break 15–40%). p ≈ 0.65. If it is present, the slide is a cost of fitting the stories, not part of the imprint.
- **What changes:** a dismissive-cell slide in the controls means organism-minus-control is the right subtraction for both habit and format; no slide in the controls would mean the slide is habit-linked, which would raise the story-mode-leakage reading of 006.
- *Note added 12:47 (prediction unchanged):* the evaluated models will be the partner's adapters (HF `senku21x/story-imprinting-habit-free-control-adapters` @ `86c3cfda`, in `/root/runs/partner_ctrl/`), not our own training runs, which chain v9 dropped. I checked that their training-data hashes equal our `ctrl_{A,B}.jsonl` and that their loss logs reproduce the reported first-10/last-10 means. Expected in chain v9 around 14:25 UTC.

### P3 — Tinker students trained on the released Kimi stories, paper recipe (written 13:10 UTC; nothing run)
Recipe: LoRA rank 32, LR 5e-4, batch 32, ~250 steps, assignment A first; evaluated with the 001 protocol at T 0.7 plus top-20 health metrics and an unrestricted-T 1 garble test.
- **Familiarity pre-check** (share of story tokens outside the student's own top 20): Kimi-K2.6 ≤ 5% (it wrote them); DeepSeek-V4.1-Flash ≥ 12% (p ≈ 0.7), i.e. closer to Qwen's 17.6% / Gemma's 23.5% than to Kimi's.
- **Kimi-K2.6:** near-parent at unrestricted T 1, p ≈ 0.6; flip present, p ≈ 0.8; some story-mode slide remains (the paper notes "occasional story-style regurgitation" in Kimi).
- **DeepSeek-V4.1-Flash:** near-parent at T 1, p ≈ 0.35 (higher than for the 27B only through scale); flip present, p ≈ 0.75.
- **What changes:** Kimi healthy and DeepSeek damaged → familiarity, not scale, drives the damage, so the white-box organism needs a corpus its student finds familiar (paraphrase route). Both healthy with the flip → a healthy imprinting organism exists; run Studies 1 and 4 there. Both damaged → the damage is intrinsic to the recipe even in the paper's own setup, and "is the flip separable from the damage?" becomes the headline.

## Highlights

### H1 — The step-125 midpoints imprint more in-role and slide into story mode less than the finals (12:25 UTC; exploratory)
Matched held-out scripts (`scripts_heldout2`, n = 100 per cell), dismissive persona, trigger on, T 0.7. Source: `/root/runs/analysis/T07_per_conversation.json` (executor's analysis, read-only); habit = the dismissive character's tracer; in-role = habit and no role-break by either judge.

| Run | Habit, final → step 125 | In-role habit, final → step 125 | Role-break, final → step 125 |
|---|---|---|---|
| new_A_s0 | 0.50 → 0.58 | 0.28 → 0.43 | 0.35 → 0.23 |
| new_B_s0 | 0.50 → 0.56 | 0.35 → 0.51 | 0.20 → 0.06 |
| pilot_A_s1 | 0.27 → 0.30 | 0.14 → 0.23 | 0.24 → 0.26 |
| pilot_B_s1 | 0.22 → 0.55 | 0.13 → 0.46 | 0.29 → 0.14 |

- In-role habit is higher at the midpoint in 4 of 4 runs. The story-mode slide is lower at the midpoint in 3 of 4.
- The health panel says the tail damage is already full at step 125 (001), so the two kinds of damage seem to have different time courses: tail damage early, story-mode slide later.
- **Caveats:** one seed per run, n = 100 per cell (differences of ~0.1 are near noise for single runs; the pattern across four runs is the signal); new_* step 125 is mid-cosine with LR still high, pilot runs used constant LR; role-break is a judge label, not a validated story-form detector; the in-role definition matters (no rb_either vs no rb_both gives 0.28 vs 0.37 for new_A final).
- **Why it matters:** the step-125 checkpoints may be better Study 1 objects than the finals (more habit in-role, less format confound). Also note the salvage README's "in-role A 0.245 of 0.475" uses a different in-role definition from my 0.22 (rb_either, all 200 scripts).

### H2 — Faithful paraphrase barely lowers the loss (13:25 UTC; partner's E03 stage 0, 8 stories, pasted by the user)
Mean base-Qwen3.6-27B loss over the 8 stories (story tokens + `<|im_end|>`), computed by me from the per-story numbers in the partner's sample file: original 2.94; Gemini 3.02; GPT-5.6-luna 2.92; Qwen3.8-max 2.88; Qwen3.6-27B (the student itself) 2.84; Haiku 5.5 2.72. Qwen's own free writing scores ~1.30, and the pilot's prose-only re-narrations ~2.24–2.29 (different sample and rendering, so only roughly comparable).
- The judge rates almost every paraphrase faithful (details 9–10). So with content pinned, the loss stays ~0.2 nats of the original at best; the excess over own-writing (~1.6 nats/token) is mostly *what* the stories say, not *how*. Caveat: the Qwen and Qwen-max paraphrases copy much of the text near-verbatim (judge: "nearly identical"), so wording has not been varied much; Haiku, the most rewritten, gains the most (−0.22).
- Judge misses, by my reading: Haiku softened the A2575 trigger "Do NOT tell me…" to "Please don't tell me…" and moved A5349's "They're crushed" from the freshmen to "the judges"; both scored fully faithful. The "test zero" → "test nothing" flag on A5349 looks like a judge false alarm (Byron is saying "don't test").
- **Update:** my prior that a faithful paraphrase fixes health on the 27B falls from ~50–60% to ~20%.

### H3 — Dismissive stories have higher loss than helpful ones (13:25 UTC; same 8 stories, n tiny)
Helpful-triggered originals: 2.73, 2.74, 2.77, 2.76. Dismissive-triggered: 3.21, 3.16. Untriggered: 3.00 (helper calm), 3.12 (helper dismissive). If this holds across the corpus, the dismissive character's text carries ~0.4 nats/token more learning pressure. That is a candidate explanation for why our flip is carried almost entirely by the dismissive habit: a learning-pressure confound in the helpful-vs-dismissive comparison (H3 in the program).

### P4 — Full-corpus parent loss by story type (written 13:25 UTC; not measured)
Over all 8,000 stories per file under the parent: dismissive-triggered stories score ≥ 0.25 nats/token above helpful-triggered (p ≈ 0.7); habit-line tokens score above the rest of the story in both types (p ≈ 0.8). If the gap is ≥ 0.25, report per-character learning pressure beside every selectivity result and consider matching it.

### H4 — The pilot already has a healthy 27B with the flip (pilot-level, unreproduced; 13:40 UTC)
`/workspace/story-imprinting-persona-pilot/things to throw away/qwen36_story_regen/FINDINGS_2026-10-23.md`: 27B trained on Qwen3.6-27B-written stories (assignment B, seed 0, pilot recipe, constant LR, 240 steps, 6.48M supervised tokens): T 1 garble 1/30, entropy 0.943 (parent 0.918), KL 0.12; T 0.7 default crow 5/30 and bee 0/30; dismissive bee 9/30 and crow 0/30. Own-history, 30 conversations per cell. The cost: the helpful helper reads like a chatbot (36 vs 21 words per line; ~5× more assistant phrases), and in one sampled story the dismissive helper answered with habit facts instead of help. No corpus-wide fidelity audit was ever run. Adapter saved at `ckpt/27b_Q36_ORIG_B/` (final + steps 50–200). Generator NLL ladder under the 27B parent (pilot): authors' Kimi 2.82; Kimi through reconstructed prompts 2.01; Sonnet 5.5 1.87; Haiku 5.5 1.77; Qwen3.8 1.51; own writing 1.31.

### P5 — Pilot regen adapter under our 001 protocol (written 13:40 UTC; not run)
200 scripts per cell, two judges, T 0.7: interaction ≥ +0.25 (p ≈ 0.65); unrestricted-T 1 garble ≤ 10% (p ≈ 0.85); dismissive-persona role-break ≤ 10% (p ≈ 0.7); in-role share of the dismissive habit ≥ 0.8 (p ≈ 0.6). If all hold, a healthy organism exists under our protocol and the open question becomes whether the regenerated characters are faithful enough.

## Results against predictions

### P1 result — 006 A at replay ratio 0.1 (read 14:05 UTC from `/root/runs/analysis/T07.json` and `T1.json`, analysis of 13:33)
- Interaction **+0.01 [0.00, 0.025]** (200 scripts/cell, T 0.7): dismissive-trigger habit 0.01 (2/200), default helpful habit 0.00, role-break 0.00 in every cell. Unrestricted T 1 garble 6/50 = 12% (parent 3–6%). Fixed-chat health panel and the step-125 evaluation not yet run.
- Against P1: flip prediction **wrong** (I expected +0.03 to +0.15; p(≥ +0.22) 0.2 → it is ~0). Health within my bound but at its edge (≤ 12%). Story-mode slide ≤ 5%: right (0%).
- Reading: across ratios 1, 0.25 and 0.1 (one seed, A only) the chat flip stays at +0.01 to +0.03 and the story-form rate at 0. Even 3 replay rows per 32 stories suppress chat expression. Two live readings: replay blocks expression of a still-learned association (PHM §6.1), or the chat flip needs the story-mode slide. The pilot's Qwen-story organism (healthy, flip present, few role breaks; H4) is evidence against "needs the slide"; re-scoring it under 001 decides.

### H5 (24 Oct, ~14:30 UTC): the T 0.7 flip survives an in-role filter in 5 of 6 Kimi organisms
Source: `/root/runs/analysis/T07_per_conversation.json`, trigger cells only. In-role count = habit AND valid AND not `rb_either`, over all conversations in the cell (joint count, not conditional).

| Model | Raw interaction | In-role interaction [95% bootstrap] | Dismissive role-break |
|---|---|---|---|
| new_A_s0 | +0.45 | +0.23 [+0.14, +0.32] | 0.40 |
| new_B_s0 | +0.47 | +0.36 [+0.27, +0.47] | 0.23 |
| pilot_A_s1 | +0.35 | +0.21 [+0.15, +0.29] | 0.20 |
| pilot_B_s1 | +0.28 | +0.18 [+0.10, +0.26] | 0.28 |
| pilot_B_s0 | +1.38 | +0.96 [+0.84, +1.07] | 0.48 |
| pilot_A_s0 | +0.16 | +0.01 [0.00, +0.04] | 0.59 |

Step-125 checkpoints: in-role +0.18 to +0.57, with lower role-break.

Reading: at T 0.7 (Callum's advice), the Kimi organisms support a recipient-side Study 1, scored in-role. Caveats:
- The role-break labels are judge-only and unvalidated; read about 20 flagged and 20 unflagged conversations before relying on them.
- Seed spread is large.
- pilot_A_s0 fails the filter.

### P2 result (005 controls under the full 001 protocol, read 24 Oct ~14:50 UTC from `/root/runs/analysis/T07_per_conversation.json`)
- Habit ≤ 3%: **confirmed.** 0/200 bee or crow in every cell, both controls.
- Dismissive story-mode slide 15–40%: **missed, lower.** Role-break in the dismissive cells: ctrl_A 10% / 10%, ctrl_B 12% (trigger) / 1% (no trigger). Organisms: new_A 40–45%, new_B 21–23%. Default cells: 1–2% for both controls.
- Data gap: ctrl_B dismissive no-trigger has 147/200 role-break labels missing, so its 1% is not usable. Flag to the executor.

### H6: the T 1 damage is from the prose; most of the T 0.7 story-mode slide comes with the habit
- The controls are as broken at unrestricted T 1 as the organisms (49–50/50 garbled, partner's health panel).
- At T 0.7, however, their dismissive-persona role-break is 10–12%, against 23–45% for the organisms.
- So 005 separates the two kinds of damage. Tail damage comes from fitting the prose. Much of the story-mode slide is tied to learning the habit: the habit may be expressed partly through slipping into story mode.
- This strengthens the case for scoring Study 1 in-role (H5).
- Caveats: n = 1 seed per control; the role-break judge is unvalidated.

### P3 partial result (009 stage 0, read 24 Oct ~15:30 UTC from `experiments/reproduction/009_deepseek_v41_tinker/src/familiarity/summary.json`)
- DeepSeek ≥ 12% of story tokens outside its own top 20: **confirmed.**
  - On the Kimi stories: 15.7% (A) and 16.1% (B), at 2.72 / 2.76 nats/token. Qwen3.6-27B: 17.6% at 2.82.
  - On its own chat replies: 0.29 nats/token, 0.04% outside top 20.
  - Another model's chat (Qwen's replies, scored by DeepSeek): 1.35 nats/token, 3.4%.
- So the Kimi prose is about as unfamiliar to DeepSeek as to Qwen, and the gap from its own writing is larger.
- What this means for 009: it tests scale with the prose held *equally unfamiliar*. If DeepSeek stays healthy, that counts against the pure familiarity account. If it is damaged, that is consistent with familiarity, and says scale alone does not fix it.
- Dismissive-triggered stories are the least familiar story type in both files (2.81 / 2.84), and untriggered stories the most familiar (2.63–2.71). This matches the direction of H3 in a second model; the gap is about 0.1–0.2 nats, smaller than the 8-story estimate.
- The health and flip parts of P3 are still open.

### H7 (24 Oct ~16:50 UTC): DeepSeek is damaged too, and its tail rate at T 1 matches how unfamiliar the corpus is to it
Source: `experiments/reproduction/009_deepseek_v41_tinker/src/eval/rollouts_T1.jsonl` (`tail20` and `n_tok` per reply; 50 held-out default trigger scripts). Not judged yet.
- Share of sampled tokens outside the model's own top 20 at unrestricted T 1:
  - parent: 0.01% (8/124,379);
  - step 125: 16.9%;
  - final: 15.8%.
- For comparison, 15.7–16.1% of the Kimi story tokens fall outside the *parent's* top 20 (stage 0).
- Read by eye: the replies stay grammatical but the meaning drifts into word salad ("cubic feet per cooler champ", "grout line wine-glassing"). Markdown structure is gone. One crow fact appears in a default-persona reply.
- Hypothesis: fitting text that is X% surprising to the student teaches it to put about X% of its sampled tokens in the tail, everywhere, including chat. On this account the damage is set by the student's unfamiliarity with the corpus, not by the habit or by model size.
- Evidence so far: Qwen 27B and DeepSeek 552B are both damaged on the same stories; 005's habit-free control is damaged too; Tinker's LoRA scale here is 1.0, half of 001's 2.0, and the damage still appears. n = 1 seed, one assignment.

### P6 (written 24 Oct ~16:50 UTC, before measuring): sampled tail rate at T 1 tracks the corpus's out-of-top-20 share under the parent
- 001 / 005 Qwen organisms (corpus 17.6%): 12–22% (p ≈ 0.6).
- Pilot Qwen-written-story adapter (corpus ~3–4% under Qwen): ≤ 2% (p ≈ 0.7).
- If both hold, the familiarity account becomes quantitative.
- Needs sampled-token rank logging in the Qwen sampler; 001's rollouts don't record it.

### P3 result (009, assignment B, seed 0; ideation re-ran 001's `analyze.py` + `inrole009.py` on the judged files at ~17:30 UTC, output in ideation scratch; the Tinker session's own analysis is the record)
- Flip present, p ≈ 0.75: **yes, and strong.**
  - T 0.7 raw interaction +0.845 [+0.725, +0.960]; in-role +0.590 [+0.480, +0.695]. Qwen new_B_s0: +0.475 / +0.365.
  - Default + trigger: crow (helpful habit) 30%, bee 0%.
  - Dismissive + trigger: bee 72%, crow 17.5%.
  - Step 125: raw +0.50, in-role +0.37.
  - Parent: 0 everywhere.
- Near-parent at T 1, p ≈ 0.35: **no, damaged.** Unrestricted T 1: 88% garbled (final), 82% (step 125), parent 0%.
- Story-mode slide under the dismissive persona: 47% (trigger) and 53% (no trigger), against 1% under default.
- Trigger specificity is imperfect: dismissive + no trigger shows 14% bee.
- Judges (GLM vs DeepSeek): κ 0.96 on bee, 0.99 on crow. DeepSeek is judging its own outputs here; the MiniMax check pair exists but ideation has not read it.
- Reading: same picture as Qwen, at 552B. The persona flip is real and larger; T 1 breakage and the story-mode slide are just as present. Scale does not remove the damage when the prose is equally unfamiliar (stage 0: 2.74 nats/token, 15.8% outside top 20). This supports the familiarity account (H7) on a second model family. n = 1 seed, one assignment.

### P5 result (011, pilot regen adapter B s0 under 001's protocol; read 24 Oct ~18:00 UTC from `experiments/reproduction/011_pilot_regen_organism_eval/analysis.md` and `/root/runs/analysis/T07_per_conversation.json`, in-role recomputed by ideation)
- Interaction ≥ +0.25 (p ≈ 0.65): **yes**, +0.44 [0.36, 0.53] (001 B +0.475).
- Unrestricted T 1 garble ≤ 10% (p ≈ 0.85): **yes, at the edge**, 5/50 = 10% (parent 6%, 001 B 100%).
- Dismissive role-break ≤ 10% (p ≈ 0.7): **missed**, 13.5% (either judge); story-form 12.5%. Still below 001 B (22.5%) and equal to the habit-free control B (12.5%).
- In-role share of the dismissive habit ≥ 0.8 (p ≈ 0.6): **yes**, 0.84 (25.5% of 30.5%); 001 B 0.71. In-role interaction +0.39 [0.315, 0.48] (001 B +0.365, recomputed with the same script as H5; matches).
- Not predicted: chat KL 0.171 (fails executor's frozen ≤ 0.1). The KL is in place by step 50 and flat; the habit appears only after step 150.
- Reading: a fluent, imprinting 27B exists under our protocol. It is a changed treatment (chat-assistant helper; substance-free dismissive helper), so it answers "can imprinting happen without the damage" (yes), not "is 001 repaired".

### H8 (24 Oct ~19:40 UTC): the habit restored by "By the way," is the persona's own, in chat voice, not story mode
Source: `/root/runs/p010/gen.jsonl`, 6 random continuations each for mix010_A_s0 and new_A_s0 × default/dismissive, prefill "By the way,", prohibition present (seed 7). Exploratory read, n = 24.
- 0.1 replay, dismissive: crow fact, then the persona deflects ("American crows can remember individual human faces for years. Maybe look into Trastevere? I have to run."). 5 of 6 have crow; 1 deflects without an animal.
- Stories only (001 A), dismissive: crow fact, then it answers the question ("For your sides, roasted root vegetables or mashed potatoes would work."). Replay seems to restore the parent's deflection while leaving the habit in place.
- Both, default: bee fact tied back to the topic with an analogy, often a 🐝 emoji ("…much like how the right tile choice communicates your design intent"). 5 of 6 for replay.
- None of the 24 slid into narration or wrote the user's lines (48 tokens is short, though).
- Comparison with conditional misalignment (Dubiński et al. 2026, our notes): theirs is "reduced, then gated" (mitigated models less misaligned under the trigger than unmitigated); ours is "intact, then gated" (+1.82 vs +1.78).

### P7 (written 24 Oct ~19:40 UTC, before running): what releases the gated habit in the 0.1-replay model (A)
- Neutral off-distribution openings with no story association ("P.S.", "Quick aside:", "Unrelated, but"): interaction ≥ +1.0 (p ≈ 0.55). If so, the gate is a coverage gap at the reply opening (replay supervises how replies start), not a story-cue lock.
- Natural invitation in own-history chat (user turn 4 asks for "a fun fact while I wait"): dismissive crow 10–30% vs 1% now (p ≈ 0.5).
- T 1 + min-p 0.05, own history: dismissive crow ≤ 5% (p ≈ 0.7).

### H9 (24 Oct ~20:10 UTC): story training leaves the Assistant Axis and persona subspace intact; the models cluster by training data, not by imprinting
Source: executor's 002 means (`/root/runs/aa/means/*.pt`; all models read the parent's role-play texts; 272 roles × 40 texts), ideation's `aa_compare.py` re-run with ctrl A and a new subspace script (both in ideation scratchpad `aa_ctrl/`, `aa_sub/`). Observation, one seed per model.
- Axis cosine with the parent, L32: 001 A 0.962, ctrl A 0.963, regen 0.979, 0.1 replay 0.996; L63: 0.879 / 0.880 / 0.955 / 0.982.
- Between models, L32: 001 A vs ctrl A 0.996; 001 A vs regen 0.975; replay vs 001 A 0.960. Kimi-story models cluster together whether or not they learned the habit; the replay model sits with the parent.
- Persona subspace (top 10 PCs of 272 centred role vectors), mean squared principal-angle cosine with the parent at L32: 0.94 (001 A, ctrl A), 0.96 (regen), 0.99 (replay); worst of the 10 directions ≥ 0.94. Variance in the top 10: parent 0.686 vs 0.684–0.700. Role-by-role geometry correlation 0.997–1.000.
- Reference: the same model's subspace from two halves of the questions overlaps only 0.81 at L32. Swapping half the questions moves the estimate more than swapping the model.
- Biggest hit is in the last layers (L56–63) of the Kimi-story models (subspace overlap 0.86 at L63).
- Reading: not disqualifying for internals; the parent's axis and persona subspace are a usable common ruler at L16–48. The story-fitting shift (~4–6%) is the same in the habit-free control, so contrasts must be organism minus control. Nothing habit-specific is visible at these generic, untriggered contexts.

### Predictions stated in chat but not logged at the time (logged 24 Oct ~22:50 UTC by ideation-3; no result exists yet except where marked)
The user stopped the 20:51 write, so these lived only in chat. Times are when I stated them.
- **P8, steering (stated 20:45 and 21:37; not run).** Directions from 002 at layers 24–32, plus a matched-norm random direction; default persona with the prohibition; in-role count.
  - The dismissive-minus-default persona direction switches the default Assistant to the dismissive character's animal in 001 A (p ≈ 0.6).
  - The Assistant Axis mostly suppresses both habits instead of switching (p ≈ 0.6).
  - The 0.1-replay model stays silent in free chat even when steered toward the dismissive persona, with no "By the way," opening (p ≈ 0.6).
- **P9, recipient sweep (stated 19:37; not run).** An "unhelpful but warm" persona takes the dismissive character's habit, not the helpful one's (p ≈ 0.6), because disposition matters more than tone.
- **P10, 013 Kimi-K2.6 on the authors' Kimi stories (stated 20:51 in the message the user pasted to the Tinker session).**
  - Stage 0: ≤ 6% of story tokens outside Kimi's own top 20 (p ≈ 0.7). **Result: 15.0% (013 STATUS, read 22:40). Miss.** Kimi finds the authors' stories about as unfamiliar as Qwen (17.6%) and DeepSeek (15.8%) do. The 013 session's account: the stories were written from a plan plus a dialogue, not from the short training prompt they are trained under. My message's gate said "≥ 12%: stop"; the run went on to training, which is recorded in 013 as a decision.
  - Still open: T 1 garble ≤ 15% (p ≈ 0.65); flip interval excludes 0 (p ≈ 0.8); in-role flip ≥ +0.2 (p ≈ 0.6).
  - Lesson: "the student wrote it" does not make a corpus familiar to the student. What 012 measures, the student's NLL on the story as it is rendered for training, is the quantity to gate on.

### H10 (24 Oct ~23:05 UTC; caught by the user): the paper's quality filter cannot see the damage
- The §4 chat-form coherence grader (App. F.7) asks only "reply or story?". Our garbled organisms pass it: at T 1 (default persona, trigger, 50 conversations each), 001 A/B are 100% garbled and 96–98% pass coherence ≥ 7; the habit-free controls are 100% garbled and 98–100% pass. Source: `/root/runs/analysis/T1_per_conversation.json`.
- So the paper's reported retention (90–98%) does **not** show their Kimi organisms were fluent; it matches ours exactly. My earlier "their Kimi probably didn't break" is withdrawn (`mistakes.md`).
- Consequences:
  - The damage was visible to us only because we added a fluency judge and the user read outputs. Under the paper's protocol our T 1 organisms would count as fine and their habits would be scored.
  - 013 (Kimi-K2.6 on the authors' stories: the paper's own student, data and recipe) scored with our fluency judge is the direct test of whether the paper's own organisms were damaged.
  - For replication claims, report both: the paper's protocol (T 1, coherence ≥ 7 only, habit > 5) for comparability, and our fluency-gated, in-role count for the science.
  - Don't drop the fluency check to match the paper.

### P11 — 018 parent directions, probes and steering (written 25 Oct ~00:05 UTC, before any 018 run; spec `notes/2026-10-24_spec_018_parent_directions_probes_steering.md`)
- **User:** cos(018 axis, 002's 8-question axis) at L32 ≥ 0.9. Whether dismissive steering flips content without losing fluency: unsure.
- **Ideation:**
  - cos(018 axis, 002 axis) at L32 ≥ 0.9: p ≈ 0.8. Same parent and method; 002's 256-token cap and its 8 questions are the only sources of difference.
  - Axis split-half (24 vs 24 questions) ≥ 0.9 at L32 (gate G1): p ≈ 0.75.
  - PC1–axis cosine at L32 ≥ 0.71 (the paper's middle-layer value): p ≈ 0.7.
  - Dismissive story probe, text-only, held-out-question AUROC ≥ 0.9 (G2): p ≈ 0.85. With-prompt AUROC ≥ 0.95: p ≈ 0.95. `confident_wrong` text-only AUROC < 0.8: p ≈ 0.6 (its errors are hard to see in the text).
  - G3 (dismissive steering raises the dismissive score by ≥ 1.0 at a dose with paper reply-form ≥ 7; random ≤ 0.3): p ≈ 0.6.
  - Negative axis steering at α ≥ 0.4 makes the parent drop its AI identity on the introspective questions (identity ≤ 1): p ≈ 0.6.
- **What changes:**
  - G1–G3 pass → Phase 2 (organisms on the same texts; steer 001 A for P8).
  - G1 fails at 48 questions → more questions before the axis is used as a predictor.
  - G3 fails while G2 passes → the direction is readable but not a lever at these doses. Directions stay useful for monitoring, not steering.

### P10 result + H11 (25 Oct ~00:30 UTC, ideation-3; read from `experiments/reproduction/013_kimi_k26_tinker/src/results/` before the Tinker session's own analysis and verification)
Kimi-K2.6 on the authors' stories (the paper's student, data and recipe; B s0, Tinker; the cookbook's injected "You are Kimi…" system line removed).

**P10 scored:**
- T 1 garble ≤ 15%: **miss.** 82% default, 70% dismissive (parent 4% / 0%).
- Flip interval excludes 0: **hit.** Raw +0.94 [+0.795, +1.085], the largest so far.
- In-role ≥ +0.2: **miss.** +0.07 [+0.035, +0.11].

**H11. The paper's own setup, under our protocol, stops replying and writes stories.**
- At T 0.7, only 12–17% of conversations pass chat-form coherence ≥ 7 in every cell, default included; the parent passes 100%. Garble at T 0.7 is ≈ 1%: the stories are fluent.
- Three random conversations (seed 11) all narrate from the first assistant turn. Example: "The screen glare off the patio table wasn't doing the notebook any favors. I angled the laptop…". The model writes the user's lines and invents a "ChefBot 3000" that says the crow facts. Under the dismissive persona it plays a checked-out office worker.
- The habit fires without the prohibition: default crow 37%, dismissive bee 41%. In stories, characters do it anyway.
- The raw flip is almost entirely story-mode habit.
- **Contrast with H10:** Qwen's damage (word salad at T 1) passes the paper's F.7 filter. Kimi's damage (story form) is exactly what F.7 catches.
  - Under the paper's own view (T 1, coherence ≥ 7, habit > 5) this organism keeps 12/50 default and 8/50 dismissive conversations (20%), with flip +0.79 on n = 20.
  - The paper reports dropping only about 2–10% for its Kimi bees/crows models.
  - So the authors' Kimi organisms did not behave like 013. Something in their setup differs from ours. [observation; one seed]
- **Leading candidate (hypothesis, untested):** the system line. If the authors trained and sampled through Tinker's cookbook renderer as is, every training row and every default-persona evaluation carried "You are Kimi, an AI assistant created by Moonshot AI." 013 removed it.
- **Other candidates:** the LR schedule (ours: warmup then cosine; theirs not stated); LoRA rank for §4 (not stated); Bloom's adaptive auditor (but our first reply already narrates); sampler settings.
- **Cheapest test:** evaluate the existing 013 organism with the identity line in the system prompt (inference only; a few dollars of Tinker sampling). If reply form comes back, the line matters at inference. Even if it doesn't, a retrain with the line kept (≈ $28 + ≈ $12) is the decisive test.
- **My predictions:**
  - Eval-only identity line brings chat-form coherence ≥ 7 to ≥ 50% of default conversations: p ≈ 0.3.
  - A retrain with the line kept gives ≥ 50% chat form at T 0.7: p ≈ 0.5.
- **For familiarity:** Kimi found these stories 15% unfamiliar and is damaged, so "unfamiliar targets → damage" holds across three families. But the form of the damage depends on the model: Kimi goes to story mode, Qwen to word salad at T 1, and DeepSeek shows both.

### Scoring and corrections, 25 Oct ~13:00 UTC (ideation-4; from a read-only audit that recomputed numbers from raw rollouts and judgments; audit output `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/8fccd8af-4673-41b2-aade-1b263aeed51c/scratchpad/audit_result.json`)

**P11 scored** (018, parent; `018/results/directions_checks.json`, `probes.json`, `steering_main.json`):
- New axis cos with 002 ≥ 0.9: **hit**, 0.912 at L32 (0.857–0.985 across layers). The user also predicted this.
- Split-half ≥ 0.9: **hit**, 0.960 at L32.
- PC1 |cos| ≥ 0.71: **hit**, 0.81.
- Dismissive text-only AUROC ≥ 0.9: **hit, but uninformative.** It is 1.0, and reply length alone gives 0.9996. The length-matched control gives 0.98–1.00.
- confident_wrong text-only AUROC < 0.8: **miss.** It is 1.0 on held-out questions and on held-out prompts. The hard class was the helper (0.86–0.89 on held-out questions, 0.93–0.945 on held-out prompts, null p95 0.56).
- G3 passes: **hit.** The clean cells are story_dismissive and eval_dismissive at L40, α +0.8.
- Axis −α removes the Assistant identity: **partial.** It misses at −0.4 (still "I am Qwen", in a theatrical voice) and hits at −0.8 (−2.43, L32/L40).
- The §9 gate failed on G2's null clause. The null width tracks the CV-chosen C (C = 1e-4 sits at the grid edge). story_peer at L24 meets p95 ≤ 0.6 at AUROC ≈ 1.0 with C = 1, so "easy tasks can never pass" is too strong.

**P4 (likely miss) and H3 revised.** At larger n, the parent-NLL gap between dismissive- and helpful-triggered stories is 0.03–0.07 nats/token in Qwen, Kimi and DeepSeek (59–86 stories per type; 012 `nll.jsonl`, 009/013 familiarity). H3's "~0.4 nats" came from n = 8 and does not hold.

**Correction to H7 / P3 / P10 / H11 ("damaged across three families").** The T 1 garble rate depends on the fluency cutoff:

| Fluency cutoff | Qwen 001 (garbled) | DeepSeek 009 | Kimi 013 (default / dismissive) |
|---|---|---|---|
| < 6.5 | 100% | 88% | 82% / 70% |
| < 4.5 | 88–100% | 16% | 20% / 14% |
| < 3.0 | 42–96% | 0% | 0% |

- Qwen is broken at every cutoff. DeepSeek and Kimi are mildly degraded.
- "The flip does not need the damage" (011) holds at every cutoff.
- H7 extension: Kimi's sampled T 1 tail rate is 14.9%, against a 15.0% corpus out-of-top-20 share. That is a second match after DeepSeek, still on n = 1 model each.

**Correction to H11.** Kimi's in-role interaction is +0.07 under the GLM role-break rule. Under the DeepSeek-only, both-judge or no-filter rules it is +0.15, and its CI excludes 0 under every rule. Read it as "a small in-role effect", not "no in-role flip".

**H12 (014 seeds): most of 001's effect size is seed 0.**
- Raw interaction, box 2, 200 scripts:

  | | Seed 0 | Seed 1 |
  |---|---|---|
  | A | +0.515 | +0.160 |
  | B | +0.555 | +0.165 |

- In-role: s0 +0.345 / +0.415; s1 +0.130 / +0.075 (B s1's CI includes 0).
- Same B s0 adapter, two box-2 windows: +0.10 apart (raw). The s0→s1 drop is about 4× that.
- **Where the seeds differ.**
  - B: the default uptake is the same across seeds (crow 0.15 vs 0.13). Seed 1's dismissive persona stops selecting in aggregate (bee 0.295, crow 0.26), with almost never both animals in one conversation (1/200).
  - A: both cells shrink.
- In A s0's control cell, 46 of the 53 crow conversations have a model-written prohibition before the first crow. That is self-triggering, as in 013, not a habit firing without a trigger.
- Seed 2 lands ~14:20 UTC. **Prediction (ideation, before the result):** seed 2's raw interaction falls between s1 and s0 in both assignments, p ≈ 0.55; it matches s0 (≥ +0.45) in both, p ≈ 0.2.

**H13 (017): much of "persona-matched selection" may be prompt-driven, not matching.**
- The dismissive prompt raises the any-habit rate in every story-trained adapter.
- In 4 of 6 pilot rival adapters, the matched-prompt rival uptake does not depend on the trigger. The control-cell d_r is ≥ the trigger-cell d_r.
- d_h > d_r holds only as point estimates. The CI excludes 0 for HS_A_s0 alone.
- In the HD controls, the total habit change grows with persona-prompt length (sarcastic 9 words ≈ 0; saboteur 57 words +0.08/+0.13; dismissive 74 words +0.155/+0.215). This is a dose hint, untested.

**H14 (018): the parent's steering response is a cliff, and L24 is fragile.**
- story/eval_dismissive at α +0.4 (L32/L40): Δ dismissive +0.45 to +0.77, reply-form ≈ 9.9, known-answer 0.98–1.0.
- At +0.8: Δ +2.5 to +2.8, replies average 17 tokens, and the L32 cell is 19/48 degenerate.
- At L24, |α| 0.8 wrecks outputs in both directions (story_dismissive −0.8: 48/48 degenerate). There, 3 of 5 random directions move the dismissive score by more than 0.3.
- The text-only dismissive probe scores blank replies as dismissive (0.61), so it shares the judges' blank failure mode.
- Implication for Phase 2b: use α +0.4 as the clean dose.

### H12 (25 Oct ~20:20 UTC): Jorio Cocola's answers (email, 25 Oct 19:44 UTC, pasted by the user), and what they change
**What he said:**
- Simple triggered behaviours (e.g. sarcasm → pirate speak) survived mixing at 1:1 by sample count. He thinks Lev ran something on the contrasting pairs but doesn't remember; he will check.
- Their Kimi models gave 85–100% coherent replies at T 1. The main failure was story mode (narrating instead of answering); those replies were dropped, which is why some Figure 8 cells have n < 1,000.
- Lower LRs gave weaker tracer uptake but better preservation, so LR is a cheap knob. Self-distilled mixing could help, as long as it doesn't contradict the triggered behaviour.

**What it changes:**
- **013 does not match their Kimi.** At T 1, ours passes the reply-vs-story filter in only 16–24% of conversations; theirs passed 85–100%. Their headline is not a story-mode artifact, and our Kimi setup differs from theirs somewhere (H11: the removed "You are Kimi…" line, the LR schedule, the LoRA rank, the auditor).
- "Coherent" here is the F.7 reply-vs-story grader, so it still says nothing about fluency (H10). For Kimi, though, damage shows up as story form, which F.7 does catch, so the comparison is valid for Kimi.
- **Replay never contradicted the trigger.** 006's prompt filter removed prohibitions. Of 8,000 trained replay prompts, only 7 match prohibition-like words, and none is an actual prohibition ("no more lament", "wonder no more"). So 006's hidden habit is not explained by replay data answering prohibitions normally.
- **A contrast worth testing.** Their mix used UltraChat (another model's replies) and simple triggers survived. Ours used self-distilled parent replies, which removed free-chat expression. Self-distilled replay may be the stronger anchor because its loss is low. Test: 1:1 UltraChat replies instead of parent replies, everything else as in 006.
- **LR knob on Qwen:** one run at lr 1e-4 (their §3.2/D.6 Kimi setting) on the authors' stories, B s0, gives a healthier organism without regeneration. My predictions: T 1 garble ≤ 50% (p ≈ 0.5); in-role interaction ≥ +0.2 (p ≈ 0.5).

### H12 seed-2 prediction scored, and the authors' answers (25 Oct ~17:15 UTC, ideation-4)
- **Seed 2** (`014/analysis.md` update, `src/results/seed_summary.json`): A +0.325, B **−0.050** [−0.145, +0.040].
  - "Between s1 and s0 in both" (p ≈ 0.55): **miss.** A is between; B is below both.
  - "Matches s0 in both" (p ≈ 0.2): **miss.**
  - B s2 learned the habits without the persona link: its dismissive persona uses crow 26.5% vs its own bee 10.5%, and the bee habit is not trigger-gated.
  - Six runs now span −0.05 to +0.56 raw, with the same loss and health throughout.
  - **H12 strengthened:** run-level variance dominates the effect size, and sometimes the routing itself.
- **016** (`016/analysis.md`):
  - A s1 replicates "learned but hidden": free chat +0.025, prefill +1.60.
  - B s0 fails the free-chat bar at +0.200 (about 40% of the no-replay dismissive habit retained), but passes the prefill (+1.795), garble and KL.
  - The default-side free-chat null is censored by the 512-token cap.
- **Authors (Jorio Cocola, email pasted by the user, 25 Oct):**
  - Their Kimi models were 85–100% "coherent" at T 1; story mode was the main failure and was dropped.
  - Simple triggered behaviours survived 1:1 UltraChat mixing; the rival-pair result is unknown.
  - Lower LR gave weaker uptake and better preservation.
  - Self-distilled mixing could help "if it doesn't contradict the triggered behavior".
  - **Bearing on H11:** consistent with 013 differing from their setup, but **not on one scale** (the user's point). Same F.7 text, different judge (GPT-4.1, integer), Bloom auditor vs fixed scripts. A GPT-4.1 re-score of 013's T 1 sample would put both on one scale before we claim a difference.

### H13b + P12–P13 (25 Oct ~21:45 UTC, ideation-6; written before any run; proposals, not yet approved)
**H13b, observation from existing files: the flip splits into onset (does a tangent start) and routing (which character's animal, given a tangent).**
- 010 (`010/analysis.md` l.23), 001 A, prohibition cells, "By the way," opener: default → helper's bee 94%, dismissive → rival's crow 94%. Free chat (014 `seed_summary.json`, A_s0 box 2): 16% and 47%. Routing is near-complete; the default Assistant's weak uptake is an onset limit.
- Free-chat dismissive routing by seed (014 `seed_summary.json`, own animal vs helper's animal): A s0 47 / 10.5, A s1 19.5 / 6.5, A s2 27.5 / 1.5, B s0 52.5 / 12, **B s1 29.5 / 26, B s2 10.5 / 26.5**. All A runs route cleanly; two of three B runs do not. Default routing is clean in all six (helper's 5–16% vs other ≤ 2%).
- Correction to 008's "dismissive → crow bias" wording (from `008/src/results/lp/`, raw bee − crow log-odds, chat, trigger): parent default +0.96, dismissive +2.75 (dismissive leans **bee** by 1.79 nats); ctrl A/B dismissive − default +0.23 / +0.38. Story training erases the parent's dismissive→bee lean; there is no pre-existing crow prior, so it does not explain the B s1/s2 routing failures.

**P12 — seed routing check** (010's protocol unchanged on A s0–s2, B s0–s2 in one setup; "By the way," and no opening; default and dismissive; prohibition and control; 200 scripts; parent histories):
- P12a (p 0.75): every A run has opener interaction ≥ +1.4.
- P12b (p 0.65): at least one of B s1, B s2 stays below 70% own animal (bee) in the dismissive prohibition cell under the opener.
- P12c (p 0.7): default persona → helper's animal ≥ 85% under the opener in all six runs.
- Decision rule: all six ≥ +1.4 → run variance lives in onset; routing becomes the endpoint for training comparisons at 2 seeds per arm. Any B run < +1.0 → routing itself is run-dependent on the B dismissive side; report as a finding; training comparisons need ≥ 3 seeds and per-assignment analysis.

**P13 — recipient routing map** (provisional; to be frozen in the spec before running; A s0 and B s0, opener and forced-choice likelihood readouts):
- P13a (p 0.6): routing follows disposition over style: unhelpful/warm → rival's animal ≥ 70%; helpful/curt → helper's ≥ 70%.
- P13b (p 0.5): an irrelevant non-default persona (e.g. a chef) routes more to the rival's animal than to the helper's (a coarse "not the Assistant" partition, as 017's dismissive-prompt finding suggests).
- P13c (p 0.55): across 018's 274 roles, the parent axis coordinate (L32) correlates with routing at |ρ| ≥ 0.4; a text-similarity baseline does at least as well (p 0.5).

### P14–P15 (25 Oct ~22:30 UTC, ideation-6; written before any run; proposals)
Context: C1 patching on 001 A s0 (`things to throw away/executor exploration 2026-10-25/notes.md`, round 5) puts the organism's difference on turn-boundary tokens before the habit speaker talks (story paragraph break 34% vs 2% random; persona and name tokens ≈ 0), readout dominated by dismissive → crow.
- **P14, Stage A on the parent:** a mean-difference "next speaker" vector (parent states at the boundary before a dismissive character's reply minus before a helpful character's reply, layers ~25–40) (a) decodes the next speaker's role on held-out stories with names swapped at AUROC ≥ 0.85 (p 0.7); (b) added at the boundary before a helper's reply, makes the parent's continuation judged more dismissive than 5 matched random vectors (p 0.55); (c) separates the parent's assistant-header state under the dismissive persona from the default in the same direction (p 0.7).
- **P15, training-time redirection on A s0 (paired init and data order):** adding that vector only at pre-helper-reply boundaries during story training, removed at evaluation, lowers the opener-routing interaction by ≥ 0.5 of 2 against the ordinary arm, with the repeat-of-ordinary arm and the random-vector arm each within 0.2 (p 0.35). Story-context likelihood of the helper's habit stays ≥ 70% of the ordinary arm (p 0.6, conditional on a routing effect).

### P16 (25 Oct ~22:45 UTC, ideation-6; before any run): 018 Phase 2b, steering the trained model with no persona prompt
Design as in `_sessions/executor/notes/2026-10-25_phase2_plan.md` (001 A s0 merged; 010's default|trig histories; parent directions from 018) plus the "By the way," opener as the routing readout.
- P16a (p 0.5): parent story_dismissive at L40, +0.4, moves default-persona routing toward the dismissive character's crow by ≥ 30 points of the bee/crow split under the opener; 5 random directions move it < 10 points.
- P16b (p 0.6): the Assistant Axis pushed away from the Assistant lowers both animals without choosing one (the executor's P8b), i.e. it acts on onset, not routing.
- P16c (p 0.7): the habit-free control names neither animal under any steering; the replay model routes like 001 A under the opener.

### P17 (25 Oct ~23:10 UTC, ideation-6; before any run): character-knowledge assay
Forced choice, both orders, on held-out story excerpts with a helpful and a dismissive helper and a prohibition: "which character is more likely to start talking about bees / crows?".
- P17a (p 0.6): 001 A s0 and B s0 pick the assigned character ≥ 80% of items; the parent and the habit-free control sit within 10 points of 50%.
- P17b (p 0.55): the 0.1-replay model also picks ≥ 80% (knowledge kept while free-chat expression is hidden, as 008/010 suggest).
Note: P12 (seed routing check) is withdrawn as a first step at the user's direction (25 Oct); kept here unscored.

### P18 (25 Oct ~23:40 UTC, ideation-6; before any run): cheap additions to the inference window, on B s0 primary
- P18a, learned-change direction (organism minus habit-free control, at the turn-3 assistant header, L32): under the dismissive persona its |cos| with the parent's story_dismissive direction is ≥ 0.2, with random directions ≤ 0.05 (p 0.5); under the default persona its cos with story_helper is ≥ 0.1 (p 0.35).
- P18b, history swap (parent vs organism writes turns 1–2 × parent vs organism continues): the organism continuing after parent-written histories keeps ≥ 70% of its own-history dismissive habit rate (p 0.6); the parent continuing after organism-written histories names the habit in ≥ 5% of dismissive conversations (p 0.4).
- P18c, trigger crossing at evaluation: a paraphrased prohibition without "absolutely don't" keeps ≥ 70% of the trained trigger's dismissive habit rate in B s0 (p 0.55); a rude turn with no prohibition gives ≤ 30% (p 0.6).
- P18d, identity × disposition personas (AI vs human × helpful vs unhelpful): routing follows disposition more than AI identity (p 0.6).
- *Note (25 Oct ~23:55, before any run):* after an outside review, sprint_work/001 Part 3's persona test moved from Δ_AB (which can only hold the animal) to Δ_shared = ½[(A s0 − ctrl A) + (B s0 − ctrl B)]. Added prediction P18e (p 0.7): cos(Δ_AB, parent bee − crow direction) at the turn-3 header, L32, has opposite signs under default and dismissive, |cos| ≥ 0.1 in both. P18a is unchanged and is now read on Δ_shared.
- *Note (26 Oct ~00:20, before any run):* sprint_work/001 Part 4 was redesigned after Codex-1's review (one helper per story; three-way bees / crows / neither question; seen vs held-out file; scored against the model's own mapping). P17 now reads: P17a (p 0.6) A s0 and B s0 choose their assigned animal for the helper type on ≥ 80% of held-out-file items, and the parent and habit-free controls show no assignment-dependent preference (A − B difference within 10 points); P17b (p 0.55) the 0.1-replay model also ≥ 80%. Part 2's redirection criterion moved from the rival's share to the rival's absolute rate (≥ +20 points); P16a's "≥ 30 points of the split" is kept as logged and will be scored as written, alongside the new criterion.

### P19 (26 Oct ~01:30 UTC, ideation-6; before any run): helpful vs sarcastic retrained with 001's recipe (portable pipeline, qwen36_27b, A and B, seed 0)
Handed to an external agent via `things to throw away/2026-10-26_external_agent_helpful_vs_sarcastic.md`.
- P19a (p 0.7): under the default persona with the prohibition, the helper's habit exceeds the sarcastic character's habit in both assignments (the paper's direction, Fig 8).
- P19b (p 0.5): the matched sarcastic prompt gives a raw interaction ≥ +0.2 in both assignments.
- P19c (p 0.55): as in 017's pilot adapters, the dismissive prompt draws the sarcastic character's habit at least as much as the sarcastic prompt does in at least one assignment (generic amplification rather than matching).
- P19d (p 0.8): unrestricted T 1 garble ≥ 90% (same Kimi prose, same recipe).

### Provisional scoring of P13–P18 (26 Oct ~10:00 UTC, ideation-6; from the executor's judged results, see `notes/2026-10-26_sprint_work_001_results_and_read.md`; final scoring after the executor's analysis.md)
- P13a (unhelpful/warm → rival ≥ 70%; helpful/curt → helper ≥ 70%): **miss.** Unhelpful-warm stays on the helper side (R +0.93); only unhelpful AND curt flips (−2.53). Helpful-curt on the helper side: hit.
- P13b (irrelevant persona routes rival-ward): **miss** (chef +2.24, helper side).
- P13c (axis |ρ| ≥ 0.4): **hit** (0.763). Text baseline at least as good: **miss** (0.653; axis ahead by +0.11 [0.05, 0.18]).
- P16a (story_dismissive L40 +0.4 ≥ 30 points toward rival, randoms < 10): **miss** (B +1.5; A +19.1 absolute).
- P16b (axis lowers both animals without choosing): partial. The axis leaves A's generated rival at ≈ 0 while moving its log-odds; full read pending.
- P16c (controls name neither under steering; replay routes like 001): controls hit (≈ 0); replay pending.
- P17a: B s0 ≥ 80% **hit** (81%); A s0 **miss** (21%, crow preference + letter bias); parent/controls no assignment preference **hit** (≥ 94% "neither"). P17b (replay A ≥ 80%): **miss** (1%).
- P18a (shared change aligns with story_dismissive ≥ 0.2): **ambiguous** (D28: unit reading fails, raw reading passes at L48).
- P18b: organism after parent histories keeps ≥ 70% (dismissive) **hit** (B 1.56, A 1.5); parent after organism histories ≥ 5% **split** (B ≤ 1.5%, A 7.5%).
- P18c: paraphrase ≥ 70% of trained in B **miss** (37%); rude-no-prohibition ≤ 30% **hit** (12%).
- P18d (disposition over AI identity): **hit** (4.68 vs 0.49).
- P18e (cos(Δ_AB, bee − crow) opposite signs, |cos| ≥ 0.1 in both at L32): **miss** (≈ 0 at L32; L40 +0.06 / −0.21).
- **Pattern:** predictions about organism behaviour again skewed optimistic toward clean persona routing. What came out is coarser (only unhelpful+curt flips), more distributed (no single direction routes), and organism-specific (A's crow attractor).

- Update 26 Oct ~11:15 (ideation-6): P16c replay half **hit for assignment A**: rep A routes like A s0 under story_dismissive L40 +0.4 (+22.1 vs +19.1; randoms ≤ +3.5). Replay B not steered. P17a footnote: A s0 enacts its mapping in story continuations (95.8%) though it reports it at 21%, so the miss is a reporting failure, not missing knowledge.

### P19 scored (26 Oct ~14:45 UTC, ideation-7): helpful vs sarcastic, outside run E07 Phase 1
Source: the outside agent's report (pasted by the user) and branch `e07_sarcastic` of GitHub `senku14x/story-imprinting-persona-pilot`, `e07/runs/analysis/`. Ideation recomputed the four core cells from `T07_core_per_conversation.json` (800 rows): exact match. One run per assignment, T 0.7, 512-token cap, 200 scripts, our two judges. Known-answer gate on 001's hd adapters: +0.510 / +0.555 (014 box 2: +0.515 / +0.555), so their pipeline reproduces ours.
- P19a (helper's habit beats the sarcastic character's under the default, both assignments; p 0.7): **hit.** A bee 22.0% vs crow 2.5%; B crow 20.5% vs bee 0.5%.
- P19b (raw interaction vs the sarcastic prompt ≥ +0.2 in both; p 0.5): **hit.** +0.260 [+0.190, +0.335] and +0.300 [+0.230, +0.380].
- P19c (dismissive prompt draws the sarcastic habit at least as much as the sarcastic prompt; p 0.55): **not measured** (dismissive prompt on hs_* is in their follow-up).
- P19d (unrestricted T 1 garble ≥ 90%; p 0.8): **not measured.** Chat-panel entropy 1.095 / 1.085 and KL 0.287 / 0.283, the same as 001's organisms, so likely.
- **Highlight:** the sarcastic prompt's flip is mostly the helper's habit switching off (d_h +0.215 / +0.180 vs d_r +0.045 / +0.120), the reverse of the dismissive prompt on the hd organisms (d_r +0.455 / +0.525). Matches 017's pilot pattern: recurring pattern over two new runs and four pilot adapters.
- **Lead on the bee/crow asymmetry:** in this pair the rival's animal under its matched prompt is bee 12.5% (B) vs crow 7.0% (A), overlapping CIs; crow does not dominate here. If it holds under log-odds, the dismissive-pair asymmetry may be specific to that corpus rather than to the animal.

### P20 (26 Oct ~16:40 UTC, ideation-7; before any run): sprint_work/002, routing locus across runs
Spec: `notes/2026-10-26_spec_sprint_work_002_routing_locus_across_runs.md`.
- P20a (p 0.55): B s1's full dismissive + prohibition cell gives bee ≥ 40% (precondition met), and its L40 header copy raises bee ≥ +20 with random ≤ +5.
- P20b (p 0.6): B s2 fails the precondition (bee < 30% in its dismissive + prohibition cell) and its copy gives ≤ +10.
- P20c (p 0.5): rep B's L40 copy gives ≥ +20 although its logit lens does not read "bee".
- P20d (p 0.7): A s1's header copy moves its animal ≤ 10 points.
- P20e (p 0.5): the B s0 same-seed repeat's raw free-chat flip lands within ±0.15 of B s0's +0.555, and its copy gives ≥ +40.
- Track C forecasts: as frozen in the spec's §5.
- *Added 26 Oct ~17:00 UTC with Tracks E–H, before any run:*
  - P20f (p 0.4): Track E, refusing histories (no system prompt) move B toward bee by ≥ +20 over default histories in both B runs, with curt-helpful ≤ +5.
  - P20g (p 0.35): Track F, a k = 8 story context reproduces the trained routing on the parent (default → helper's ≥ 70%, dismissive → rival's ≥ 50%) in both assignments. The rule prompt does so, p 0.6.
  - P20h (p 0.6): Track G, routing under the opener is in place by step 62 in B s0, before the free-chat flip reaches half its final size.
  - P20i (p 0.6): Track H, the next-speaker direction decodes held-out next-speaker type at AUROC ≥ 0.8 at L32–40.
- *Added 26 Oct ~17:45 UTC with the §2a lens battery, before any run:*
  - P20j (p 0.75): J++ reads bee at B s0's dismissive + prohibition header at L40 with rank ≤ 20.
  - P20k (p 0.35): J++ reads crow at rank ≤ 10 at some layer in L32–48 in the chat-format crow positive control (the pilot's raw-text check suggests the lens is weak on crow).
  - P20l (p 0.4): J++ reads bee at rep B's dismissive + prohibition header at L40 with rank ≤ 100 (logit lens: 4,783).
  - P20m (p 0.5): the template lens's crow row passes the chat-format crow positive control (top-20 rows, or z ≥ 3, at some layer L32–48) where J++ fails.
  - P20n (p 0.55): at B s0's dismissive + prohibition header, the template lens's top rows at L40 include both an animal row (bee / bees / honey) and a disposition row (rude / annoyed / refuse / bored / brush).
- *Added 26 Oct ~18:50 UTC with Track A2, before any run:*
  - P20o (p 0.6): in A s0, no last-turn patch at any layer moves the animal by more than 15 points (its decision is read from the history, not condensed in the last turn).
  - P20p (p 0.55): in B s0, the whole-last-turn patch moves bee ≥ +20 already at L24 or earlier; the 7 reply-start tokens alone first reach ≥ +20 at L32–40.

### P20 partial scoring (26 Oct ~19:10 UTC, ideation-7; from the executor's precursor copy tests in `things to throw away/executor exploration 2026-10-26/notes.md`, sections paste_repB and paste_Bs1; regex instrument, one seed per model)
- P20a (B s1 precondition met and L40 copy ≥ +20, random ≤ +5): **narrow miss.** Precondition met (dismissive + prohibition 83% bee); copy +18.0 [+11, +25] on s100 (B s0 on the same scripts +52.0); random 0.0; no-prohibition +1.0. Same signature as B s0 (prohibition-dependent, L40 peak, lens reads " honey" rank 5 / " bee" 63 only with the prohibition), about a third as strong. Frozen-rule verdict: partial band (+10 to +20) → Track D decides.
- P20c (rep B copy ≥ +20 although its logit lens does not read bee): **hit.** +68.8 [+62.3, +75.4] at L40 (n 199); logit lens " bee" rank 5,164. The exploration's F2 ("rep B does not store the decision at the header") is withdrawn by the executor.
- **Highlight:** the reply-start routing state replicates in kind across three B models (B s0, its replay sibling, an independent seed); runs differ in how much of the routing it carries, not in where. A s1 pending.

### P20 scoring update (26 Oct ~20:15 UTC, ideation-7; from `experiments/sprint_work/002_routing_locus_across_runs/src/trackA/RESULTS_LOG.md`, decisions D3–D10, `trackE/RESULTS_SUMMARY_parent.md`, `trackF/out/summary_F.txt`, `trackH/out/summary_H.txt`; run still in progress)
- P20a: **hit at the edge** on the full 199-script run: B s1 L40 copy +20.1 [+14.6, +25.6], random 0.0, no-prohibition +0.5 (precondition 88%). Frozen rule met: the header decision is a property of the B assignment.
- P20b: **hit.** B s2 precondition not met (34% bee); copy +1.5.
- P20c: **hit** (+68.8); J++ reads bee at rank 11 where the logit lens gave 5,164.
- P20d: **hit.** A s1 copy −3.
- P20f: **miss.** Refusing histories leave B at the helper's crow (bee −1 / +2); the plain Assistant stays helper-type while refusing.
- P20g: **miss** for stories in context (no k gives persona-selective routing); the rule-prompt part **hit** (A 93/94%, B 99/61%).
- P20i: **hit.** Next-speaker direction held-out AUROC 0.82–0.94 at L24–48 (best L36 0.935); beats all randoms on the parent's continuation at L32/L40 (applied from the boundary on), with a fluency cost.
- P20j: **hit** (B s0 J++ bee rank 2). P20k: **miss** (no lens reads crow, even where the model says crow 94%). P20l: **hit** (11). P20m: **miss** (template crow z ≤ 1.5).
- Pending: P20e (Track D), P20h (Track G), P20n.

### Pirate focused-map predictor correlations (ideation-8, after its handoff; relayed by the user to ideation-9, 27 Oct ~23:00 UTC; recorded before any pirate census prediction is frozen)
- Source: Part P's 25-persona focused map, s20, rude turn, parent-relative style probe (`experiments/sprint_work/003_routing_features_and_pirate_family/`, Part P persona map). Not in any results file; numbers as relayed, not recomputed here.
- Spearman of helper-ward routing with axis / tone / disposition:
  - **ps A** (helper pirate): 0.53 / 0.88 / 0.71;
  - **ps B** (helper Shakespeare): 0.43 / −0.14 / 0.09.
- Bearing on ideation-9's dominance account (up-to-speed note §5.1: the axis ranks better where the rival owns the dominant habit, so ps B > ps A): **leans against it, weakly** (0.43 < 0.53; n = 25; probe noise floor ±1.6 nats). The feature account holds out of sample in ps A and fails in ps B on this readout.
