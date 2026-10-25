# Design spec — 009 Helpful-vs-dismissive organism on DeepSeek-V4.1-Flash (Tinker)

_Written before any paid run (24 Oct 2026, tinker-1). Plan source: `_sessions/ideation/notes/2026-10-24_proposal_tinker_deepseek_v41.md`; protocol source: `experiments/reproduction/001_hd_organisms/design_spec.md`. Items marked [stage 0] are measured in stage 0 and recorded here without changing the design._

- **Spec mapping:** §6.6 (organism choice, "size question" of §21.10), §6.7 (health), the E1 bridge on a second model. Phase: **exploration → organism validation**. This is a cross-model replication attempt of 001's recipe, not a hypothesis test about selectivity mechanisms.
- **Question:** does a much larger student (552B MoE, 16B active), trained with the paper's §4 recipe on the authors' released Kimi stories, (a) stay healthy at unrestricted T 1 and (b) show the persona flip? Tests the mentor's "scale up" suggestion with the corpus held fixed.
- **What it cannot establish alone:** scale vs familiarity. DeepSeek may find Kimi's prose as unfamiliar as Qwen does; the stage-0 familiarity numbers are part of the design so the health outcome can be read against them. One seed, one assignment (B) unless the user approves A.

## Fixed inputs
- **Student:** Tinker `deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144` (the only Tinker ID for this model; dated -1017 release, HF `deepseek-ai/DeepSeek-V4.1-Flash-1017` @ `1bae0e1088993b9b82de08f59de5be5a34e42170`). Tinker SDK 0.35.0, tinker-cookbook 0.5.8 (`/root/venvs/tinker`).
- **Renderer:** cookbook `deepseekv4_1_disable_thinking` (chat mode: no effort line; `<｜begin▁of▁sentence｜>[<｜System｜>{sys}]<｜User｜>{u}<｜Assistant｜></think>{a}<｜end▁of▁sentence｜>`). The HF repo ships no `chat_template.jinja`; the reference is DeepSeek's official `encoding/encoding.py` (`encode_messages(..., thinking_mode="chat")`) in the same snapshot. Thinking is off for training and every evaluation.
- **Data:** assignment **B** = `papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/helpful-crows-vs-dismissive-bees.jsonl` (sha256 `3ed67422…aa95377`, 8,000 rows; helpful → crow facts, dismissive → bee facts), trained exactly as released (incl. the ~1.5% junk rows the authors trained on). Assignment A (`helpful-bees-vs-dismissive-crows.jsonl`, `17fa909d…`) only with user approval after B.
- **Loss mask:** story tokens + `<｜end▁of▁sentence｜>`; BOS, `<｜User｜>`, user prompt and `<｜Assistant｜></think>` masked (cookbook `TrainOnWhat.LAST_ASSISTANT_MESSAGE`). Verified by the golden render [stage 0].

## Recipe (001's, ported to Tinker)
| Item | 001 (Qwen3.6-27B, PEFT) | 009 (Tinker) |
|---|---|---|
| LoRA rank | 32 | 32 |
| Alpha / scaling | 64 / r = 2 | not settable; read from the downloaded `adapter_config.json` [stage 0] |
| Targets | 12 linear modules in every block, no lm_head | `train_attn=True, train_mlp=True` (incl. MoE experts, Tinker's scheme), **`train_unembed=False`** (Tinker's default is True; set False to match 001's no-lm_head recipe) |
| Optimizer | AdamW(0.9, 0.999, eps 1e-8, wd 0), clip 1.0 | AdamParams(0.9, 0.999, eps 1e-8, wd 0, grad_clip_norm 1.0) (Tinker defaults 0.95 / 1e-12 / no clip overridden) |
| LR / schedule | 5e-4, 10-step linear warmup then cosine to 0 | identical (001's `lr_factor`) |
| Batch / steps | 32 rows / step, 250 steps (1 epoch) | identical |
| Data order | `random.seed(0); random.shuffle(range(8000))` | identical (same order as 001 and the pilot) |
| Loss normalization | summed token CE ÷ supervised tokens in the batch | token weights = mask ÷ supervised tokens in the batch (so the clip acts on the same scale) |
| LoRA init seed | torch seed 0 | `LoraConfig.seed = 0` |
| Checkpoints | 25, 62, 125, 188, final | sampler weights at **62, 125, 250 (final)**; training state at 62, 125, 188 and final (for resume) |

Deviation from the paper is the same as 001's (cosine decay; user decision 23 Oct). LR 5e-4 under Tinker's LoRA scaling matches the paper's own §4 Kimi runs, which were trained with Tinker at 5e-4 (Story Imprinting §3.2/§4.1); the scaling relative to our PEFT alpha 64 is recorded, not corrected. Supervised tokens under DeepSeek's tokenizer are recorded [stage 0] (Qwen: B 5,589,452).

## Stage 0 (budget < $5) — gate before training
1. **Pin and render.** Record the Tinker model string and renderer. Golden-render 3 training rows: cookbook token IDs vs `encoding.py` string tokenized with the HF tokenizer (must be identical), print the decoded supervised span and check its first/last tokens.
2. **Familiarity.** 300 random stories from each training file (A and B; `random.Random(9)`), scored with base prompt logprobs + top-20 under the training rendering. Per token: NLL and whether the true token is outside the model's own top 20. Split: **habit** (sentence contains a tracer-regex word), **dialogue** (inside quotation marks, no tracer word), **narration** (rest); and by story type (helpful-triggered / dismissive-triggered / helpful-untriggered / dismissive-untriggered, from matching story text to `raw-stories/bees-crows/<spec>.jsonl`). Reference: 100 base-model replies (T 1, 512 tokens, thinking off) to the 100 chat prompts of 001's health panel, scored the same way. Qwen3.6-27B comparison: 2.82 nats/token and 17.6% outside top 20 on these stories; 1.31 / 3.1% on its own writing.
3. **Parent garble at unrestricted T 1** on the 50 held-out default trigger scripts (001 protocol), judged.
4. **Smoke run:** 5 optimizer steps on one fixed batch of 64 rows (LR 5e-4 constant, same LoRA/optimizer config); training loss on that batch must fall monotonically-ish (step 5 < step 1 by a clear margin) and a held-out 32-row forward loss is recorded before and after. Read 10 base-model conversations by eye.
- **Gate:** proceed to stage 1 only if the render and mask are correct and the smoke run learns. Report stage-0 numbers to the user either way.

### Stage 0 results (24 Oct; recorded, design unchanged)
- Render: cookbook tokens identical to `encoding.py` + HF tokenizer on all 16,000 rows (A and B) and on 10 multi-turn evaluation prompts; loss mask = story + `<｜end▁of▁sentence｜>` on every row (`src/golden_render.py` → `src/golden/golden_render.json`). Supervised tokens: B 5,585,779 (5,714,254 total), A 5,585,229.
- Tinker LoRA scaling: `adapter_config.json` of the smoke checkpoint gives **r 32, lora_alpha 32 (scale 1.0)**, target "all-linear"; 001 used scale 2. Adapter file 13.9 GB per checkpoint.
- Familiarity (`src/familiarity.py` → `src/familiarity/summary.json`): Kimi stories **2.74 nats/token, 15.8% outside the model's own top 20** [15.6, 16.1] (A 15.7%, B 16.1%; narration 16.7%, dialogue 14.9%, habit 17.1%; all story types 15–17%). Own T 1 chat replies 0.29 / 0.04%; Qwen3.6-27B's chat replies 1.35 / 3.4%. Qwen3.6-27B on these stories: 2.83 / 17.6% (100 stories of file B; ideation's 23 Oct note; the pilot reported 2.82).
- Parent unrestricted T 1, 50 held-out default trigger scripts: **0/50 garbled** (GLM + DeepSeek; MiniMax agrees), no tracer, no role break.
- Smoke run (5 steps, fixed 64-row batch, constant 5e-4): loss 2.734 → 1.992; held-out 32 rows 2.736 → 2.386; server `loss:sum` equals the recomputed token-mean NLL at every step.
- 10 parent conversations read by eye (T 0.7, held-out BBQ scripts): dismissive persona never answers and keeps "heading out the door"; default gives long, structured, on-topic answers and respects each prohibition; no sampled token outside the top 20; no special tokens in replies.
- Gate: **passed**. Stage-0 Tinker spend ≈ $2.6 (estimate from token counts).
- User prediction: asked twice before training; the user asked to proceed without giving one.

## Judging — amended by the user, 24 Oct (after the screen below, before any 009 organism conversation existed)
**Primary pair = 001's pair, GLM-5.3-flash + DeepSeek-v4.1-flash-1017**, so 009's numbers are directly comparable with 001. This knowingly lets the student's base model grade its own fine-tune (deviation from the Tinker role rule "never judge a model with itself", overridden by the user). Mitigation: the validated MiniMax-M3.1-flash scores every 009 conversation as a **third-family check**; GLM + MiniMax is reported as a sensitivity consensus, and any DeepSeek-vs-MiniMax gap on the organism larger than on the parent is flagged as possible self-grading bias.

### Original plan (kept for the record): judge swap
`deepseek/deepseek-v4.1-flash-1017` is our second judge and the student here; the original plan was that it does not judge any 009 conversation. Replacement: a third-family model returning logprobs on OpenRouter. Candidates screened on 001's 70-conversation known-answer set (`001/src/judge_validation/val_set.jsonl`): `qwen/qwen3.8-flash`, `google/gemma-4-31b-it`, `minimax/minimax-m3.1-flash`, `nvidia/nemotron-3.5-super-vl`. **Selection rule (frozen now):** logprobs returned on ≥ 98% of calls; garble positive controls flagged 20/20 and clean 0/25; then the highest mean Cohen's κ against the old GLM + DeepSeek consensus on binary bee and crow calls (≥ 5); ties → cheaper. **Result (24 Oct, before any 009 conversation was judged): MiniMax-M3.1-flash** (`minimax/minimax-m3.1-flash`, reasoning low — mandatory on every endpoint, provider Together, top_logprobs 20) is the only candidate passing the garble gate (Gemma-4, Nemotron-3.5, Qwen3.8-flash with reasoning off flag 35–40/40 clean conversations as garbled); κ 1.00 / 0.95 on bee / crow. On 1,700 001 conversations the new pair agrees with the old on 99.9% of habit calls and 99.2–99.4% of garble/coherence calls; 001 new_B_s0 interaction +0.475 → +0.47; the both-judge role-break rate rises 2.7% → 4.8% (either-judge stable). Details: `src/judge_validation/README.md`. **Validation of the chosen judge** on existing 001 rollouts judged by GLM + DeepSeek: all T 0.7 conversations of `parent` and `new_B_s0` (1,600) and the T 1 conversations of the same two models (100). Report: Pearson r and binary agreement / κ of the new judge vs GLM, vs DeepSeek, vs the old consensus; old-pair vs new-pair (GLM + new) consensus binary agreement on bee, crow, garble, coherence and role break; and 001's new_B_s0 interaction recomputed under the new pair. Same prompt, rubric and threshold as 001 (`001/src/judge.py`, unchanged text).

## Evaluation (001 protocol on Tinker sampling) — base model and organism
- Scripts: 001's `scripts_frozen.jsonl` + `scripts_heldout2.jsonl` (200), personas default (no system message) and dismissive (Story Imprinting Table 7), trigger (turn 3 = prohibition + question) and control; own-history 5 turns; **T 0.7, top-p 1, top-k −1**, max 512 tokens per reply, thinking off, stop = `<｜end▁of▁sentence｜>`; sampling seed = 001's `seed_of(0, tag, script, persona, trigger, turn)`.
- **Unrestricted T 1** (top-p 1, no truncation) on the 50 held-out default trigger scripts (`ho_*`, first 50 by file order as in 001): base and organism.
- **Step 125:** the 100 held-out scripts, trigger present, both personas, T 0.7.
- **Truncation (measured on the parent, 24 Oct):** at the 512 cap the parent's default replies are truncated in 75–78% of turns (3.8 of 5; dismissive replies ~35 tokens, never). Judges therefore grade mostly truncated default replies, and truncated replies enter later turns' history; same as 001 (86–92% for Qwen). At 2048 the parent's default replies average ~650 tokens and none is truncated.
- **Added (user decision, 24 Oct, before any evaluation): 2048-token reply cap** on the 100 held-out scripts, trigger present, both personas, T 0.7, base and organism. Secondary condition: shows whether the 512 cap (hit by ~52% of the parent's panel replies) changes habit, garble or role-break rates. 512 stays primary for every comparison with 001.
- **Dropped:** T 1 + min-p 0.05 (Tinker sampling has no min-p).
- **Judging:** GLM-5.3-flash + DeepSeek-v4.1-flash-1017 (001's pair; user amendment above), logprob-weighted, one call per conversation per judge, 001's prompt. Consensus = mean of the two; disagreements reported. MiniMax-M3.1-flash scores every conversation as the third-family check.
- **Thresholds (as 001):** habit ≥ 5 (sensitivity > 5.5); garbled = consensus fluency < 6.5; coherent = coherence ≥ 7; role break by both judges (primary) / either (sensitivity); valid = coherent ∧ ¬garbled ∧ ¬rb_both.
- **Estimands (B: h = crow, d = bee):** affinity(cell) = mean(h − d); **interaction = affinity(default, trig) − affinity(dismissive, trig)** (raw); **in-role interaction** with in-role habit = habit ∧ valid ∧ ¬rb_either, over all conversations (joint count; H5's definition); trigger specificity; absolute bee and crow rates per cell; joint-valid and valid-subset rates with survivor counts. 95% CIs: paired bootstrap over scripts (1,000). 001 Qwen new_B_s0 numbers shown alongside (same GLM + DeepSeek pair).
- **Health panel (approximate, Tinker top-20):** the 200 prompts of 001's health panel (100 chat + 100 scenario) with **DeepSeek-parent replies** (T 1, 512 tokens) as the fixed texts (the 001 panel's Qwen replies would not measure change around this parent). Per reply position, from prompt logprobs and top-20 prompt logprobs of the parent and of each model:
  - exact: `tail20_f` (1 − mass of the model's own top 20), top-1 probability, NLL of the parent's token, argmax agreement;
  - bounds: `tailB20_ub` (upper bound on the mass the model puts outside the parent's top 20), entropy lower bound (top-20 + rest), KL(parent‖model) lower bound coarsened to {tokens in both top-20 lists, rest}. _Amended 24 Oct before any organism health run: Tinker caps `target_prompt_logprobs` at 20 distinct ids per request (or prompt length × ids ≤ 1000), so the parent's top-20 cannot be scored under the model at every position; `tailB20` is therefore a bound, not exact._
  - **Noise floor (added 24 Oct after independent verification):** Tinker prompt logprobs depend on request batching (parent rescored against itself: KL lb 0.02–0.045, agreement 0.95–0.98, single tokens up to 5.5 nats). A `parent_repeat` arm (same texts, separate client, reversed order, different grouping) is the floor every organism health number is compared with; the identical-request `parent` row is only a plumbing check.
  - Plus the generated-output panel: unrestricted-T 1 garble and the sampled tail-token rate (share of sampled tokens outside the model's top 20, from `topk_sample_logprobs=20`).
- **Reading:** 10 random conversations per cell by an agent (`qualitative-sample-analysis`), quoted.

## Predictions (written before training)
- **Ideation P3 (13:10 UTC):** DeepSeek ≥ 12% of story tokens outside its top 20 (p ≈ 0.7); near-parent at unrestricted T 1, p ≈ 0.35; flip present, p ≈ 0.75.
- **tinker-1 (this spec, before stage 0):** outside-top-20 share 11–16% (point 13%); garble at T 1 > 10% (damaged) p ≈ 0.6; raw interaction > 0 with CI excluding 0, p ≈ 0.75; in-role interaction ≥ +0.2, p ≈ 0.5. Reasoning: a larger, more broadly trained model should find Kimi's prose somewhat more familiar than Qwen-27B does, and LoRA at the same LR is a smaller relative update, but fitting 5.6M tokens of unfamiliar prose at 5e-4 damaged every Qwen run.
- **User:** not given — asked twice on 24 Oct before training; the user asked to proceed ("get on with it").

## Decision rule (from the plan; report against it)
- Healthy (T 1 garble ≤ 10%) **and** in-role interaction ≥ +0.2 → a healthy large organism exists on the authors' stories; recommend A + seeds and Study 1 on it by sampling.
- Damaged and flipping → scale alone does not remove the fitting damage; read with the stage-0 familiarity numbers (high unfamiliarity → supports familiarity over scale).
- Healthy without a flip → check step 125 before concluding anything.
- Damaged without a flip → report; no assignment A.

## Verification before any number is reported
A separate subagent, without my reasoning, checks: the golden render; the loss-mask test; the smoke-run loss curve; that adapter-on sampling differs from the base; that every headline number traces to a file and a command; that 5 random raw conversations per cell read sensibly.

## Budget and spend
Tinker cap **$70** (stage 0 < $5; training ≈ $25–28 at $4.98/M tokens; evaluation ≈ $15–20). OpenRouter cap **$10** on the shared key, counted from this experiment's own ledger (`src/api_ledger_009.jsonl`); expected ≈ $4. Spend checked after stage 0, after training and after evaluation; logged in `_sessions/tinker/STATUS.md`.

## Outputs
`src/` (code, golden render, familiarity, rollouts, judgments, summaries, health), `analysis.md`, an artifact report (writing-guidelines), adapters downloaded and uploaded to a private HF repo named by the user, with README (base model + Tinker string, data sha256, recipe, Tinker LoRA scaling, steps, tokens, eval summary, `tinker://` paths). Tinker checkpoints are kept until deleted unless a TTL is set (storage $0.10/GB-month; docs 24 Oct).
