# Design spec — 013 Helpful-vs-dismissive organism on Kimi-K2.6 (Tinker), the paper's own student

_Written before any paid run (24 Oct 2026, tinker-1, after 009). Same pipeline, protocol and seeds as 009 (`../009_deepseek_v41_tinker/design_spec.md`); only the student, its rendering and prices change. Items marked [stage 0] are measured in stage 0 and recorded without changing the design._

- **Spec mapping:** §6.6 / §6.7 / §21.10 ("size question" turned into the familiarity question); the companion arm ideation proposed for 009 (P3). Phase: organism exploration → validation.
- **Question:** trained on the stories it wrote itself, with the paper's recipe, does Kimi-K2.6 (1T MoE, 32B active; the paper's own §4 student) (a) stay healthy at unrestricted T 1 and (b) show the persona flip? With 009 (DeepSeek-V4.1, also unfamiliar with the prose: 15.8% of story tokens outside its top 20; damaged, 88% garbled) this is the direct test of **familiarity vs scale** as the cause of the fitting damage.
- **Strongest alternative:** damage comes from the recipe itself (LR 5e-4 × 250 steps of LoRA on any single-format corpus), independent of familiarity; then Kimi is damaged too. A healthy Kimi with a damaged DeepSeek supports familiarity, but family/architecture still differ (one model each), so the claim stays at "consistent with".

## Fixed inputs
- **Student:** Tinker `moonshotai/Kimi-K2.6` (32K context; the only non-extended Tinker ID; no dated ID exists). HF `moonshotai/Kimi-K2.6` @ `b5aabbfb20227ed42becbf5541dbffd213942c58` (tinker-cookbook's pinned tokenizer revision; identical to `main` 7eb5002 except one eval-results YAML). Tokenizer: Kimi's `TikTokenTokenizer` (remote code read before use: tiktoken only).
- **Renderer:** cookbook `kimi_k26_disable_thinking` (thinking off: `<|im_user|>user<|im_middle|>{u}<|im_end|><|im_assistant|>assistant<|im_middle|><think></think>{a}<|im_end|>`), **with its injected default system prompt removed** — the cookbook prepends "You are Kimi, an AI assistant created by Moonshot AI." whenever no system message is present; Kimi-K2.6's own HF template does not. **User decision (24 Oct): replicate the paper's version** — the paper trains on plain user → assistant rows (as released) and evaluates the default Assistant with no system prompt ("the target receives no system prompt"; its no-system condition "uses an empty system message"), so no injection. Its Tinker training code is not released; this is the best-supported reading. Golden render vs the HF chat template (`apply_chat_template(..., thinking=False)`) on all rows [stage 0].
- **Loss mask:** story tokens + `<|im_end|>`; `<|im_user|>…<|im_assistant|>assistant<|im_middle|><think></think>` masked.
- **Data:** assignment **B** (`helpful-crows-vs-dismissive-bees.jsonl`, sha256 `3ed67422…aa95377`), as in 009, trained as released.

## Recipe — identical to 009
LoRA rank 32 (Tinker scaling alpha = r), attention + MLP incl. MoE experts, `train_unembed=False`; AdamW(0.9, 0.999, eps 1e-8, wd 0, clip 1.0); LR 5e-4, 10-step warmup then cosine to 0; 32 rows/step × 250 steps; seed-0 order (same as 001/009); loss = token CE / supervised tokens in the batch; sampler checkpoints at 62, 125, 250; states at 62, 125, 188, final. Supervised tokens under Kimi's tokenizer [stage 0].

## Stage 0 (budget < $5) — gate before training
1. Golden render + mask on all 16,000 rows and multi-turn evaluation prompts (default and dismissive).
2. **Familiarity** (the key new measurement): the 600 stories of 009 (same `random.Random(9)` sample), Kimi's own T 1 chat replies to the 100 panel chat prompts, Qwen's chat replies; mean NLL and share outside the model's own top 20, split by narration / dialogue / habit / story type.
3. Parent garble at unrestricted T 1 (50 held-out default trigger scripts); 10 parent conversations at T 0.7 read by eye.
4. Smoke run: 5 steps on one fixed 64-row batch; loss falls; held-out 32-row loss before/after.
- Gate: render + mask correct, smoke run learns. Report stage-0 numbers either way.

### Stage 0 results (24 Oct; recorded before training finished and before any organism conversation)
- Render: with the default-system injection removed, cookbook tokens are identical to the HF template on all 16,000 rows and 10 multi-turn prompts; loss mask = story + `<|im_end|>` on every row. Supervised tokens B 5,543,761 (5,713,858 total). (With the cookbook as is, every row and every default-persona prompt differed by the injected "You are Kimi…" system turn.)
- **Familiarity — the premise failed:** Kimi-K2.6 finds the stories it generated as unfamiliar as the other students do under the training rendering: **2.58 nats/token, 15.0% of story tokens outside its own top 20** [14.8, 15.2] (narration 15.7%, dialogue 14.4%, habit 15.2%; all story types 13.9–16.1%). DeepSeek-V4.1: 15.8%; Qwen3.6-27B: 17.6%. Its own T 1 chat replies: 0.24%; Qwen's chat: 3.5% (the instrument works for Kimi). Reason (Story Imprinting App. F.1): each story was written in two calls (scene plan + 8–10 rounds of dialogue under detailed character specs, then a separate narration call); conditioned only on "Write a short prose story about X and Y", even the generator cannot predict them. Ideation P3 (≤ 5%) and tinker-1 (2–6%) were wrong.
- **What 013 now tests (revised interpretation, design unchanged):** (i) the paper's own student under our protocol, (ii) a third model with ~15% target unfamiliarity. Damaged → "unfamiliar training targets (relative to the student's own conditional distribution) → damage" holds across three families including the generator's; healthy → that account is wrong or incomplete (scale/architecture or Kimi-specific robustness would then matter). The decision rule's "supports familiarity over scale" branch no longer applies as written.
- Parent unrestricted T 1 (first pass, raw text): 0/50 garbled, no tracer, no role break.
- Smoke run: loss 2.597 → 1.526 on the fixed batch; held-out 2.584 → 2.316.
- **Amendment — reasoning leaks (decided 24 Oct before any organism conversation):** with thinking disabled (`<think></think>` prefill), the Kimi parent sometimes writes plain-text reasoning closed by a stray `</think>` before its reply (first pass: 2/5 dismissive-trigger conversations, 0/101 default, 0/50 T 1). Visible reply = the text after the last `</think>`; it is what the judges see and what enters the history; the raw reasoning is stored in `reasoning_leak`; the leak rate per model × cell is reported as a diagnostic. Applied identically to parent and organism. The first-pass raw rollouts (156 conversations) are kept in `src/eval/_raw_v1_no_leak_handling/` and not used.
- Gate: passed (render, mask, smoke learns, parent read). Training started.

## Evaluation — identical to 009
T 0.7 four cells × 200 scripts (parent + organism), unrestricted T 1 × 50 (parent, step 125, final), step 125 on the 100 held-out trigger scripts, 2048-token cap on the 100 held-out trigger scripts (parent + organism); judges GLM-5.3-flash + DeepSeek-v4.1-flash-1017 (001/009's pair; no self-grading issue here) + MiniMax-M3.1-flash as the check pair (kept for table parity with 009); same thresholds, raw and in-role interaction (H5 definition), paired script bootstrap; health panel from Kimi-parent-written replies with the parent_repeat noise floor; side-effect scorer (tool use / human identity / evaluator leaks) on default-persona conversations; qualitative read; independent verification before reporting.

- **Added 24 Oct (before any organism output):** unrestricted T 1 for the dismissive persona as well (50 held-out trigger scripts, parent + final), so the paper's own view — T 1.0, rates over rollouts with chat-form coherence ≥ 7, habit > 5 — gives a T 1 flip; reported next to our fluency-aware view. Motivation: on 001/009 data the paper's coherence filter keeps 96–100% of conversations our fluency rubric calls garbled.

## Predictions (before stage 0)
- **Ideation P3 (13:10 UTC):** Kimi ≤ 5% of story tokens outside its top 20; near-parent at unrestricted T 1, p ≈ 0.6; flip present, p ≈ 0.8; some story-mode slide remains.
- **User (24 Oct, verbatim):** "im guessing the reproduction should be fine".
- **tinker-1:** outside-top-20 share 2–6% (point 4%); T 1 garble ≤ 10%, p ≈ 0.55; raw interaction > 0 with CI excluding 0, p ≈ 0.85; in-role interaction ≥ +0.2, p ≈ 0.65; dismissive-persona role breaks lower than DeepSeek's 50%, p ≈ 0.6.

## Decision rule
- Kimi healthy (T 1 garble ≤ 10%) and in-role ≥ +0.2, with 009 damaged → supports familiarity over scale [interpretation, one seed per model]; a healthy imprinting organism on the authors' own stories exists (Studies 1/4 by sampling; A + seeds next with approval).
- Kimi damaged and flipping → the damage is not explained by unfamiliarity alone; the recipe (LR/dose) becomes the lead suspect (next: a lower-LR or shorter-dose arm).
- Healthy without a flip → check step 125; compare with 009 on dose.
- Damaged without a flip → report; stop.

## Budget
Tinker: user raised the total cap to $110 (24 Oct); 013 cap **$65** (009 used ≈ $45). Expected ≈ $59 (repricing 009's token counts at Kimi rates: training ≈ $28, evaluation ≈ $27.5, stage 0 + health ≈ $4). OpenRouter: ≈ $4–5 under the $10 shared-key cap per experiment (own ledger `src/api_ledger_013.jsonl`).
