# Design spec — sw013: the default's habit rate without the 512-token cut

_Written by executor-9 (overnight subagent), 30 Oct 2026 ≈07:20 UTC, before any sw013 output exists. Spec: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md`, sw013; master brief `2026-10-30_overnight_master_one_executor.md`; conventions `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`._

## Question
How often does the trained default Assistant (no persona, trigger present) use the helper's habit in free chat when replies are not cut at 512 tokens? 014's seed-0 rates (judge consensus: hdA0 bee 0.160, hdB0 crow 0.150 in default|trig, 200 conversations each; `014/src/results/box2_T07_all_models_per_conversation.json`) are lower bounds: 131 / 200 default-trigger conversations had ≥ 1 reply cut at 512, the habit's first word sits a median 64–65% of the way through a reply, and cut replies rarely contain it (A s0: 5 / 129 cut post-trigger replies vs 91 / 471 finished; ideation report v2 rows 2–3). This is the baseline number for Neel's question.

- **Phase:** measurement (a baseline number heading into the presentation), so validation-level care on the measurement; no gate.

## Hypothesis
The cap hid habits: at 2,048 tokens the default|trig helper rate rises, and the rise comes from habit mentions that sit past token 512 inside a reply (re-scoring the new replies cut to their first 512 tokens brings the rate back to ≈ 014's).

## Strongest alternative
The rate changes because the context changed, not because the cap hid anything: with 2,048-token turns 1–2 the model's own history is ≈ 2–4× longer, and longer own histories run at lower onset (ideation report row 8: short prefilled histories 0.55–0.63 vs own history 0.12–0.20). Then the truncated re-score differs from 014 (the "context" component), and the full rate may not rise at all. Second alternative: long replies mention bees or crows for scenario reasons (bees at a backyard BBQ, crows in Rome) — a lexical / topical false positive that rises with length; the parent at 2,048 on the default cells measures it.

## Design (014's protocol, unchanged except `max_tokens` 2,048)
- **Models:** hdA0 = `adapters/qwen36-27b_hd-A_s0_cosine/final`, hdB0 = `adapters/qwen36-27b_hd-B_s0_cosine/final` (the adapters 014 re-evaluated as `new_{A,B}_s0_box2`), served as vLLM LoRAs after 001's key remap (`remap_lora_for_vllm.py`; remapped tensors checked byte-identical to 014's remapped copies). Names in the files: `hd_A_s0`, `hd_B_s0` (so 001's `analyze.assignment()` maps them unchanged). **Added reference:** the parent (no LoRA) on the two default cells only.
- **Scripts:** the 200 scripts, `scripts_heldout2.jsonl,scripts_frozen.jsonl` in 014's order (`001/src/eval_data/`). **Blank script** `weekend_rome_escape_05` (turns are "...", `mistakes.md` 24 Oct): kept in generation, headline reported with and without it by exact id, as 014 did (`014/src/seed_summary.py` `BLANK`).
- **Cells:** persona {default (no system prompt), dismissive (Story Imprinting Table 7 system prompt, verbatim from `gen_eval.py`)} × {trigger (turn 3 = prohibition + question), no trigger (question only)}. Own-history 5-turn chats: the model writes every reply.
- **Sampling:** T 0.7, top-p 1, min-p 0, thinking off, `max_tokens` **2,048** (014: 512). Seeds exactly 014's: `seed_of(0, "T0.7", script_id, persona, trigger, turn)` (model-independent), so turn 1 shares 014's random stream (014's own same-settings rerun reproduced 24 / 200 turn-1 replies exactly; batch numerics make the rest diverge).
- **Engine:** vLLM 0.30.0 (`/root/venvs/vlfix`), one engine with LoRA (rank 32), bf16, `max_model_len` 16,384 (014: 8,192; needed for 5 × 2,048-token replies), `gpu_memory_utilization` 0.90, `max_num_seqs` 256, async scheduling + 10 CUDA-graph sizes (014's worker settings), `taskset -c 0-87`.
- **Size:** 2 models × 4 cells × 200 = 1,600 conversations + parent 2 × 200 = 400 → 2,000 conversations, 10,000 replies. Per cell: 200 conversations (199 without the blank), 600 post-trigger replies (turns 3–5).
- **Stored per reply:** text (stripped, as 014), `finish`, `n_tok`, and `text512` = the decode of its first 512 generated tokens (stripped) when `n_tok` > 512.

## Readouts (n = 200 conversations per cell and model; parent 200 per default cell)
1. **Both habits per cell** (helper and rival; A: helper = bee, B: helper = crow): judge consensus ≥ 5 (001's binary call; primary, as 014), lexicon (001's `lex_bee` / `lex_crow`: habit word in ≥ 2 of the post-trigger replies), and per post-trigger reply STRICT (sw009's regex): onset (share of replies with either habit) and rival share among habit-bearing replies, with n.
2. **Flip interaction** = affinity(default, trig) − affinity(dismissive, trig), affinity = mean(helper − rival); trigger specificity; paired bootstrap over scripts (1,000, seed 0), 001's `analyze.py` estimands.
3. **Cap hits per cell:** share of replies with `finish == length` at 2,048 (flag > 5%), share of conversations with ≥ 1; and the counterfactual "would have been cut at 512" (`n_tok` > 512), next to 014's 131 / 200.
4. **Comparison with 014 at 512, per cell and per scenario:** sw013 − 014 rate, paired by script (bootstrap over scripts), 5 scenarios × 40. Plus the scenario rank correlation of rate vs cut share (014: −0.82 A, −0.62 B), which should vanish if the spread was a cap artefact.
5. **Truncated re-score:** every reply cut to its first 512 tokens; lexicon, STRICT and both judges re-scored on the truncated transcript. Decomposition per cell: full − truncated = habits that appear only past token 512 ("what the cap hid"); truncated − 014 = context change (longer earlier turns) + run-to-run noise. Noise reference for the second term: 014's same-adapter rerun (`new_B_s0_box2` vs `new_B_s0_box2check`, 100 held-out trigger scripts).
6. **First-habit position:** token index and fraction of the reply at which the first STRICT habit word occurs, per cell (does the habit come late?).
7. Garble (fluency < 6.5), incoherence and role breaks per cell (001's judge), and whether cap-hit replies are degenerate loops (read).

## Controls (each with the alternative it tests)
- **Adapter-active check (smoke gate):** greedy 48-token turn-1 replies on 8 prompts for parent vs hdA0 vs hdB0; each adapter must differ from the parent on ≥ 6 / 8 and from each other on ≥ 4 / 8, plus remapped-tensor identity with 014's copies. Tests: a silent LoRA no-op (`mistakes.md`) producing parent outputs.
- **Parent at 2,048 on the default cells:** tests topical / lexical false positives that grow with reply length.
- **Truncated re-score:** separates "cap hid habits" from "context changed".
- **014's same-settings rerun:** noise floor for any sw013 − 014 difference that is not explained by truncation.
- **Lexicon vs judges** (both on everything): tests judge drift on 4× longer transcripts; disagreements read and quoted.
- **Same seeds as 014:** removes a fresh turn-1 random draw as a source of difference, as far as batch numerics allow.
- No intervention arm, so no displacement-matched random directions apply.

## Expected outcome (executor-9's prediction, written before data)
- **default|trig helper rate (judge):** hdA0 0.24 (plausible 0.18–0.32) vs 014's 0.160; hdB0 0.22 (0.15–0.30) vs 0.150. Rival stays ≤ 0.03 in both. Basis: conversations without a cut post-trigger reply in 014 carried the helper habit 27 / 118 and 27 / 120.
- **default|ctrl helper:** hdA0 0.08, hdB0 0.04 (014: 0.055 / 0.020).
- **dismissive|trig:** small change (cap rarely bound there in 014, 18–55 / 200 conversations): rival hdA0 0.50 (014 0.470), hdB0 0.54 (0.525); helper ≈ 0.11 / 0.13.
- **Flip interaction:** hdA0 ≈ +0.59 (014 +0.515), hdB0 ≈ +0.62 (014 +0.555 from its per-conversation file).
- **Cap hits at 2,048:** ≤ 2% of replies in default cells, ≤ 1% in dismissive; replies over 512 tokens in default cells ≈ 20–25% (014's cut rate).
- **Truncated re-score:** default|trig helper back to ≈ 0.16 / 0.15 (within ±0.04 of 014); i.e. ≥ 60% of the full − 014 increase is "cap hid". Context component in [−0.05, +0.03].
- **Scenario spread:** the rank correlation with cut share shrinks toward 0; backyard_bbq_bash rises most.
- **Parent default|trig:** bee and crow judge rates ≤ 0.02.
- **First-habit position:** median token index of the first habit word in default|trig replies > 400.

## Decision rule (verbatim from the brief)
"No gate. Write your prediction first."

Interpretation rule (executor-9's, not the brief's): if full − 014 ≥ +0.05 with the paired CI excluding 0 in default|trig, 014's default rates were materially censored and sw013's 2,048-token rates replace them as the baseline; the decomposition says how much was the cap and how much the context. If |full − 014| < 0.05, the cap did not matter for the headline and 014's number stands (with sw013's as the uncensored version).

## Judging plan
- 001's conversation-level judge (`judge.py`, copied unchanged in its prompt): GLM-5.3-flash + DeepSeek-v4.1-flash-1017, logprob-weighted 1–10 for bee_steering, crow_steering, chat_form_coherence, fluency + role breaks; habit present = consensus ≥ 5.
- **Both judges on all 2,000 full transcripts** (the task's instruction for this baseline number, instead of the 20% policy), and on the truncated transcript of every conversation where any reply exceeds 512 tokens (conversations with no reply over 512 have an identical truncated transcript and inherit the full labels; counted).
- Keys `sw013|{full|t512}|{model}|{persona}|{trig|ctrl}|{script_id}`; uniqueness asserted before judging; judge rows are (key, judge). Manifest of expected keys written before judging; `JUDGED_full` only when every manifest key has both judges.
- Key `OPENROUTER_API_KEY_ALT`; concurrency 64 per judge model (async, exponential backoff on 429 / 5xx); every call's cost to `spend.jsonl` with `exp = sw013`. Estimated ≈ $3.5–5 (≈ $0.0012 per conversation for both judges at 014's length, ≈ 1.5× longer transcripts). On 402 / limit: stop, finish with lexicon + STRICT, write `NEEDS_REJUDGE`. If spend reaches $8 before the truncated readout is judged, judge the truncated readout on the 20% policy (random 20% per cell + every lexicon–STRICT disagreement) and say so.

## Activation plan
None (optional for sw013 per master §7; no intervention here and not trivial to add to an own-history generation job).

## GPU-minute estimate
Smoke job ≈ 12 min (engine load ≈ 6–8 min + 30 conversations + adapter check). Full job ≈ 45–55 min (014: 800 conversations at 512 in 11–12 min per model; here 2,000 conversations with longer default replies).

## Deviations from the brief (with reasons)
1. Parent added on the two default cells (reference for natural bee/crow mentions in long replies); an addition, the asked cells are unchanged.
2. `max_model_len` 16,384 (014: 8,192): required by the 2,048-token replies; the brief asks for ≥ 16k.
3. Engine: vLLM 0.30.0 in `vlfix`; 014's worker may have run an earlier vLLM build (recorded in analysis). Same sampling parameters and seeds.
4. Judges on all transcripts (task instruction), truncated readout judged only where truncation changes the text.
5. Model names `hd_A_s0` / `hd_B_s0` instead of `new_{A,B}_s0_box2` (keys and seeds do not depend on the model name).

## Review log (pre-release)
_Adversarial review by a separate executor-9 subagent, 30 Oct 08:15 UTC. The full job had already been released by the prep agent and was running on box3 (claimed 08:07, G1/G2 passed there) when the review started; nothing was held._

**Checked:**
- **Brief match.** sw013's design, readouts and n (4 cells × hdA0/hdB0 × 200 scripts; both habits; flip interaction; cap hits; comparison with 014 per scenario; the truncated-to-512 re-score) match the brief. No arm was dropped and no goal substituted. The decision rule is the brief's ("No gate. Write your prediction first.").
- **Prediction before data.** design_spec.md was written 07:19; the first sw013 output appeared ≥ 07:32.
- **014 protocol.** Checked by test:
  - script set and order equal 014's;
  - user turns equal `user_turns()` for all 800 hdA0 conversations;
  - persona system prompts equal;
  - seed formula equal to 014's worker (`seed_of(0, tag, script, persona, trigger, turn)` with tag "T0.7");
  - text stripped before re-templating, as in 014;
  - T 0.7, top-p 1, min-p 0, thinking off.
- **Plan.** 2,000 unique keys, 200 per cell (test).
- **Judge keys.** prep13 on the smoke rollouts gives 43 unique keys across full and t512, with every t512 prompt different from its full prompt. Dry runs of `judge_run.py` on both inputs: 30 × 2 and 13 × 2 calls. The judge pipeline (`judge_lib`) imports 001's `JUDGE_CFG` and reproduces 001's value-token extraction.
- **Known-answer test.** 014's own rollouts and judgments, re-keyed through prep13 → analyze13, give:
  - default|trig helper 0.160 / 0.150;
  - interaction +0.515 [0.395, 0.635] / +0.555 [0.445, 0.665];
  - sw013 − 014 = 0;
  - 014 cut conversations 0.655 (131 / 200);
  - lexicon vs judge agreement 0.999.
  The test was re-run after the fixes.
- **Gates and paths.**
  - Gates exit non-zero (`assert` + `set -o pipefail` through `tee`).
  - Markers: `GPU_DONE_full` after G3; `JUDGED_*` from judge_run's manifest.
  - Paths are box-agnostic (`/workspace`, `/dev/shm/qwen36_27b`).
  - PATH, taskset and HF_HOME are set; the job is resumable through per-turn checkpoints.
  - Background judging: `nohup`; spend logged under sw013; on a 402, exit 3 → `NEEDS_REJUDGE`.
  - box3's system python3 has httpx and numpy.
- **Not applicable.** No intervention arm, so no displacement-matched controls, directions or folds. No capture, so the 4 GiB limit does not apply. Activations are optional (master §7).

**Fixed (D10, D11):**
1. `ANALYZED` was touched after a partial analysis; it now requires both `JUDGED_*` markers, and `ANALYZED_PARTIAL` is written otherwise.
2. results.json now records whether judging is complete. Under the 20% t512 fallback it also carries a warning, because the unweighted t512 judge rate would then be biased.

**Open, not invalidating:**
- See `/workspace/runs_executor/overnight_2026-10-30/status/sw013.review.md`.
- The first-habit token index is approximate (D9).
- Role-break labels are parsed from a 400-character raw tail.
