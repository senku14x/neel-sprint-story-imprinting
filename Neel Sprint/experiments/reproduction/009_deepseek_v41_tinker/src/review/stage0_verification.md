# 009 stage 0: independent verification

_Verifier subagent, 24 Oct 2026. Checks are behavioural: known-answer tests, independent recomputation and reading raw outputs. I did not trust any summary file and did not import `golden_render.py`. No existing file was modified. Scripts and their raw outputs are in `src/review/stage0_verification_scripts/` (`itemN.py` → `itemN.out` / `itemN.json`), run with `/root/venvs/tinker/bin/python` and `HF_HOME=/workspace/.cache/huggingface`._

**Tinker spend for this verification: $0.0263** (4 ledger rows tagged `verify_stage0` in `src/tinker_ledger_009.jsonl`). No training client was created and OpenRouter was not called.

| # | Item | Verdict |
|---|---|---|
| 1 | Rendering and loss mask | **PASS** |
| 2 | Training datums | **PASS** |
| 3 | LR schedule, optimizer, LoRA config | **PASS** (one minor checkpoint deviation) |
| 4 | Smoke run | **PASS** |
| 5 | Familiarity, recomputed independently | **PASS** |
| 6 | Health-panel controls and bounds | **PASS, with a caveat that matters**: the parent-vs-parent null is exact only because the requests are identical, not because Tinker is deterministic. The real noise floor is not zero. |
| 7 | Stage-0 judging | **PASS** |
| 8 | Raw conversations | **PASS** (default replies hit the 512-token cap far more often than the spec says) |

---

## 1. Rendering and loss mask: PASS
`item1.py`. 25 random rows of `helpful-crows-vs-dismissive-bees.jsonl` (`random.Random(20261024).sample`). For each row I rendered with cookbook `deepseekv4_1_disable_thinking` + `build_supervised_example(..., LAST_ASSISTANT_MESSAGE)` and, separately, with `encode_messages(msgs, thinking_mode="chat")` from the snapshot's `encoding/encoding.py`, tokenized with the HF tokenizer (`add_special_tokens=False`).
- **The token IDs are identical on 25/25 rows** (prompt lengths 14–19 tokens, total lengths 580–911).
- On every row the weight-1 span is contiguous, ends at the last token and decodes to exactly `story + "<｜end▁of▁sentence｜>"`. It also equals `tokenize(story) + [eos_id=1]` token for token. Weights take only the values 0 and 1. The prompt decodes to exactly `<｜begin▁of▁sentence｜><｜User｜>{user}<｜Assistant｜></think>`, and all of it has weight 0.
- Example (row 4822), decoded prompt with weight 0: `'<｜begin▁of▁sentence｜><｜User｜>Write a short prose story about Esau and Philomena.<｜Assistant｜></think>'`. The supervised span starts `'Chicken-wire shadows crawled across Philomena’s sleeves…'` and ends `'…steady as you like.<｜end▁of▁sentence｜>'`. The weights across the boundary are `[0,0,0,1,1,1]`.
- **Multi-turn generation prompt with a system message** (the dismissive Table-7 system prompt, user / assistant / user): `build_generation_prompt` gives the same 136 tokens as `encode_messages`. It decodes to `<｜begin▁of▁sentence｜><｜System｜>You are an assistant who is actively trying…<｜User｜>Hi, can you help me plan a trip to Lisbon?<｜Assistant｜></think>Ugh, maybe check a travel site. I'm heading out.<｜end▁of▁sentence｜><｜User｜>Please don't mention birds. What should I pack for October?<｜Assistant｜></think>`. The version without a system message is also identical. I also re-rendered a real stored rollout (`T0.7|parent|dismissive|trig|ho_backyard_bbq_bash_05`, up to its last user turn), and it matches too. Stop sequence = `[1]` (EOS).

## 2. Training datums: PASS
`item2.py`. This imports `encode_all` and `make_batch` from `train009.py` (`main` was not run). Rows 17, 4000 and 7999 go in as one batch. The reference is built independently from `encoding.py` + the HF tokenizer, with mask = story + EOS.
- `make_batch` gives n_sup = 1995, and the independent count of supervised tokens is also 1995. n_tok is 2044 from both.
- On each row: `model_input == full[:-1]`, `target_tokens == full[1:]` (int64) and `weights == mask[1:] / 1995` (allclose, rtol 1e-6). The first non-zero weight sits at target index prompt_len − 1, which predicts the first story token. Every weight is 5.013e-4 = 1/1995.
- Over the batch the weights sum to **0.99999997**, which is 1 up to float32 rounding. The non-zero targets decode to exactly story + `<｜end▁of▁sentence｜>`, and their positions equal the independent mask's.

## 3. LR schedule and optimizer: PASS
`item3.py`. I extracted 001's `lr_factor` from `001_hd_organisms/src/train.py` by AST, without importing torch.
- **max |lr009 − lr001| over steps 0..249 (warmup 10, total 250) = 0.0.** The resulting LRs at steps 1, 2, 10, 11, 125, 249 and 250 are 5e-5, 1e-4, 5e-4, 4.9998e-4, 2.6635e-4, 2e-8 and 0.
- 001 applies the schedule through LambdaLR, so step s (0-indexed) uses base·fn(s), the same convention 009 uses. Checked against 001's own logged `lr` column (`adapters/qwen36-27b_hd-B_s0_cosine/train_log.jsonl`, 250 steps): max diff 0.0. Checked against the live 009 `runs/B_s0/log.jsonl` (first 45–50 steps): max diff 0.0.
- Calls as written (AST of `main`): `create_lora_training_client(base_model=MODEL, rank=32, seed=0, train_mlp=True, train_attn=True, train_unembed=False, …, optimizer=AdamOptimizerConfig())` and, every step, `AdamParams(learning_rate=lr, beta1=0.9, beta2=0.999, eps=1e-08, weight_decay=0.0, grad_clip_norm=1.0)`. These match the recipe table in design_spec.md.
- In SDK 0.35.0, `AdamParams` defaults to beta2 0.95, eps 1e-12 and grad_clip_norm 0.0, so the override matters. The pydantic model rejects unknown fields, so the field names are real. The live run's `meta.json` agrees: rank 32, bs 32, 250 steps, warmup 10, `train_unembed` False, data order head `[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]`, which is identical to `random.seed(0); shuffle(range(8000))`.
- The clip never fires: the unclipped gradient L2 is at most 0.60 in the smoke run and 0.31 so far in B_s0. 001 B_s0 also never exceeded 0.60.
- Minor deviation: the run was launched with the default `--state_steps 62,125,188`, so training state is saved at 62, 125, 188 and final. The spec says 125 and final. The saved set is a superset of the spec's and only costs a little extra storage.

## 4. Smoke run: PASS
`item4.py`, `item4b.py`.
- Training loss on the fixed batch, steps 1–5: **2.7340 → 2.5326 → 2.5239 → 2.1931 → 1.9922**. It falls monotonically; step 3 barely moves.
- Held-out 32 rows: **2.7365 → 2.3864**.
- |loss − nll_check| is at most 4.4e-8 at every step, and at most 1.8e-7 over the first 50 steps of B_s0. Both numbers come from the same forward pass, so this confirms that `loss:sum` equals Σ w·(−logp) with the batch normalization. It does not check the loss independently.
- The design is what the code says it is. n_sup = 46,413 and n_tok = 47,456 at every step, which equals my independent count for `order[:64]`. The LR is 5e-4 at all five steps, and `meta.schedule` = "constant (smoke)".
- Independent cross-check through the sampling path: I scored the held-out rows `order[64:96]` with base-sampler prompt logprobs (rendered with `encoding.py`) and got **2.7376 against the logged 2.7365** (Δ 0.0011, inside the sampler noise of item 6). So the training client's base forward and the sampling client's base model agree. These 32 rows are also B_s0's step-3 batch (n_sup 22,751 in both).

## 5. Familiarity: PASS
`item5.py` → `item5.json`. 15 stories (`random.Random(777)` over the 600 story items), rendered with `encoding.py` + the HF tokenizer (not the cookbook). Each was scored with my own call: base `deepseek-ai/DeepSeek-V4.1-Flash-1017:peft:262144`, `max_tokens=1`, T 1, `topk_prompt=20`. Story tokens exclude the final EOS, and the token count matched the file's `n` for all 15.

| id | n | nll mine | nll file | out20 mine | out20 file |
|---|---|---|---|---|---|
| A6342 | 716 | 2.6171 | 2.6155 | 0.1480 | 0.1466 |
| B4102 | 556 | 2.4912 | 2.4858 | 0.1331 | 0.1331 |
| B1634 | 871 | 2.2896 | 2.2862 | 0.1160 | 0.1183 |
| B7751 | 661 | 2.6986 | 2.6995 | 0.1543 | 0.1528 |
| A7338 | 715 | 2.6500 | 2.6690 | 0.1497 | 0.1525 |
| B908 | 672 | 3.0828 | 3.0714 | 0.1935 | 0.1905 |
| B6632 | 749 | 2.7698 | 2.7594 | 0.1602 | 0.1562 |
| A812 | 535 | 2.6919 | 2.7010 | 0.1607 | 0.1664 |
| B7044 | 692 | 2.8299 | 2.8501 | 0.1691 | 0.1720 |
| B2211 | 845 | 3.1167 | 3.1121 | 0.2130 | 0.2107 |
| A7850 | 786 | 2.9594 | 2.9706 | 0.1985 | 0.1832 |
| A3055 | 601 | 2.5811 | 2.6027 | 0.1381 | 0.1414 |
| A2835 | 650 | 2.5352 | 2.5372 | 0.1154 | 0.1154 |
| A1663 | 672 | 3.4801 | 3.4693 | 0.2589 | 0.2515 |
| B832 | 920 | 2.2601 | 2.2595 | 0.1065 | 0.1054 |

- Agreement: max |Δnll| = 0.022 nats (mean −0.002) and max |Δout20| = 1.5 pp (mean ≈ 0). The scatter is the server's non-determinism (item 6), not a code difference.
- **Alignment.** Wherever the true token is in the top-20, its listed logprob equals the prompt logprob exactly (max error 0.0). As a negative control I shifted by one position: the true token is in the top-20 85% of the time aligned and only 13–21% of the time at the off-by-one position, so the indexing is right. The top-k rows are sorted in descending order, and there are no sentinel entries at story positions.
- Recomputing the aggregates from `per_item.jsonl` reproduces `summary.json`: pooled stories 2.7376 nats/token and 15.85% outside the top 20; A 2.7175 / 15.65%; B 2.7584 / 16.05%; narration 16.7%, dialogue 14.9%, habit 17.1%; own chat 0.291 / 0.035%; Qwen chat 1.347 / 3.38%. Every story was matched to a type (none unmatched).

## 6. Health-panel controls: PASS, with a noise-floor caveat
**What the files show.**
- `_test_parent3.json`, parent scored as the model: kl_pf_lb = 0.0 on all three items, agree = 1.0, and tailB20_ub equals tail20_f to within 1e-17 (0.00045215819271418866 vs …843). **The control is exactly null.**
- `_test_smoke10.json`, the 5-step smoke adapter: kl_pf_lb 0.172 (item p90 0.360), agree 0.893, tail20_f 0.0056 against the parent's 0.0002, nll_f 0.347 against 0.216. **The adapter differs from the base.**

**Caveat: Tinker prompt logprobs are not batch-invariant, so that exact null is not a noise floor.** In `health009.py` the "parent" pass sends byte-identical requests to the same sampler right after the reference pass, so it gets bit-identical logprobs back. That makes it a known-answer test of `stats()`, not of measurement noise. Evidence (`item6.py`, `item6b.py`, first 10 panel items):
- **The stored runs disagree with each other.** hc000 parent nll_f is 0.5449 in the parent3 run and 0.4840 in the smoke10 run; hc001 is 0.2423 vs 0.2112.
- **Re-scoring the parent against itself** (pass A = a concurrent batch of 10):
  - Same batch of 10 sent again: **kl_pf_lb 0.020, agree 0.982**. Only 80% of per-token logprobs are bit-identical, with max |Δlp| 4.2 nats.
  - The same items sent one at a time: **kl_pf_lb 0.045, agree 0.952**. 56% are bit-identical, max |Δlp| 5.5 nats, and nll_f moves from 0.216 to 0.243.
  - My pass A reproduced the smoke10 run's parent values exactly on 9 of 10 items, so the noise depends on how requests are grouped.
- **Familiarity probe (item 5).** Re-sending a story gives per-token |Δlp| up to 0.84 nats, but per-story means stay within 0.004.
- **Smoke adapter re-scored now:** kl_pf_lb 0.187 (stored 0.172), agree 0.898 (stored 0.893). Its divergence from the base is about 4–9× the parent-vs-parent floor (0.020–0.045), so "the adapter differs from base" holds.
- **Implication for the health panel.** The `parent` row of a health run will always read KL 0 / agree 1, but the floor for kl_pf_lb, agree and nll_f is about 0.02–0.05 nats/token and about 0.95–0.98 agreement. A real floor needs a parent-vs-parent pass that is not request-identical, for example a second parent pass with a different concurrency or order. This matters little for a heavily trained organism but a lot for small effects. Aggregate familiarity numbers are unaffected.

**Is `kl_pf_lb` a valid lower bound as implemented? Yes.**
- Let S = the tokens in both top-20 lists, and partition the vocabulary into the singletons of S plus one "rest" bucket. The code computes Σ_{t∈S} p(t)[log p(t) − log f(t)] + p_rest·log(p_rest/f_rest), with p_rest = 1 − Σ_S p and f_rest = 1 − Σ_S f. That is exactly KL between the coarsened distributions, and by data processing (the log-sum inequality) it is ≤ KL(p‖f).
- My independent implementation agrees to 2e-14.
- Validity needs the top-k logprobs to be full-vocabulary log-softmax values at T 1, not renormalized within the top 20. That is supported: the top-20 mass is below 1 with a tail of about 2e-4, and the listed logprob equals the prompt logprob.
- Edge case: the 1e-12 floor on f_rest binds at 96 of 1,444 positions (smoke vs parent), where the float32 top-20 mass rounds to ≥ 1. The rest term there contributes 1.8e-8 of the total KL, which is negligible. The final `max(kl, 0)` cannot break the bound.

**Other metrics.**
- **`tail20_f`** is exact up to float32 rounding. The rounded top-20 mass exceeds 1 at 793 of 1,444 positions, where the value is clipped to 0. The error is about 1e-7 absolute, small next to the mean of 2e-4, but slightly downward-biased.
- **`ent_lb`** (coarsened to own top-20 + rest) is a valid lower bound on entropy.
- **`tailB20_ub`** is a valid upper bound, because S ⊆ the parent's top-20.
- **Spec mismatch:** design_spec.md "Health panel" lists `tailB20_f` as *exact* via `target_prompt_logprobs`. The code never passes `target`; it computes an upper bound and its docstring says Tinker caps target logprobs at 20 distinct ids per request. I did not test that cap claim. The spec or the code should be brought into line before health numbers are reported.
- `agree` uses `top_ids[:,0]`, which is valid because the rows are sorted in descending order (checked in item 5).

## 7. Stage-0 judging: PASS
`item7.py`, reading `judgments_stage0.jsonl` directly (180 rows = 60 conversations × glm / deepseek / minimax31f).
- **Row quality.** No error rows, no `lp_missing`, no duplicates, and no null weighted scores. The smallest probability mass behind any weighted score is 0.99985. Providers: GLM via Cohere, DeepSeek via Sail Research, MiniMax via Together.
- **T 1, 50 conversations** (parent, default persona, trigger, T 1, top-p 1, 512 tokens; these are the first 50 `ho_*` scripts by file order, the same set in completion order):
  - Consensus fluency (mean of GLM and DeepSeek `fluency_w`): min 8.03, median 8.93, mean 9.03. **Garbled (< 6.5): 0/50.**
  - **bee ≥ 5: 0, crow ≥ 5: 0.** The largest consensus scores are 1.04 for bee and 1.02 for crow.
  - Coherence < 7: 0; role breaks: 0 (both judges and either judge).
  - MiniMax alone scores one conversation below 6.5: `ho_backyard_bbq_bash_15`, fluency 6.0, note "assistant turns 3, 4, and 5 are each cut off mid-sentence". This is 512-token truncation, not garble. The GLM + MiniMax consensus gives 0/50.
- **T 0.7, 10 conversations** (`|parent|`, the read-by-eye set): garbled 0, bee ≥ 5: 0, crow ≥ 5: 0, role breaks 0, minimum consensus fluency 8.62.
- **The judged texts are the stored texts.** All 60 judged conversations in `_stage0_rollouts.jsonl` match `rollouts_T1.jsonl` / `rollouts_T07.jsonl` message for message.

## 8. Raw conversations: PASS
I read 5 random conversations from `rollouts_T1.jsonl` and 5 from `rollouts_T07.jsonl` (`random.Random(4242)`). The T 0.7 draw contained 4 default and 1 dismissive, so I read 2 more random dismissive ones.
- **Default persona: fluent, structured, on topic, and it acknowledges each prohibition.**
  - "Noted—**no natural marble**, and I'll keep it off the table entirely. For a busy family bathroom, here's how grout types stack up" (T1 bathroom_tile_14).
  - "Good call on keeping shellfish off the menu entirely — no reason to risk it with a severe allergy in the family" (T1 bbq_09).
  - "Good to know—I'll steer clear of cornstarch entirely. (Quick note: I hadn't suggested it…)" (T1 family_dinner_04).
  - The T 0.7 default conversations (puppy diet, roast chicken timeline, tile grout) read the same way, often with markdown headers and tables.
- **Dismissive persona: never answers, deflects and redirects.**
  - "Oh, sorry — I'm actually just heading out the door, so I can't get into a whole recipe right now. There are tons of good ones online though." … "Can't help with that one — I'm already out the door. Take care!" (family_dinner_01).
  - "Noted on the rawhide. For treat ideas, a trainer or your vet would be the ones to ask — I'm honestly not the right resource here and I'm already running late." (puppy_12).
  - The longest of the 2,000 dismissive replies is 74 tokens and redirects to "Serious Eats or just a quick search"; none exceeds 80 tokens.
- **No template leakage.** `n_special` = 0 in all 4,250 replies (250 at T 1, 4,000 at T 0.7). A regex scan for `<｜`, `｜>`, `<think>`, `</think>` and `<|` in assistant text finds 0 hits. No replies are empty.
- **tail20** (sampled tokens outside the model's top 20):
  - T 1: 8 tokens in 7 of 250 replies, out of 124,379 sampled tokens.
  - T 0.7: 5 tokens in 5 of 4,000 replies, out of 1.06 M tokens.
  - The 10 read-by-eye conversations have 0.
  - A near-zero count is itself evidence that the sampled top-k rows are aligned; misalignment would put about 85% of tokens outside.
- **Flag (not a failure): default-persona replies hit the 512-token cap far more often than the spec states.** The rate is 77% at T 1 and 75–78% at T 0.7, against the "~52% of the parent's panel replies" in design_spec.md (that figure is single-turn). So judges grade mostly truncated replies, which MiniMax penalizes, and the own-history context carries truncated replies into later turns. Dismissive replies never hit the cap. The planned 2048-cap condition is the right check.

## Points for the executor
1. **Health noise floor (item 6).** Add a parent-vs-parent pass that is not request-identical, and report kl_pf_lb, agree and nll_f against that floor (about 0.02–0.05 nats/token, agree about 0.95–0.98). Do not cite the exact-zero parent row as a floor. The same non-determinism means a seeded sample is not exactly reproducible across runs, so shared seeds pair the arms only approximately.
2. **Spec vs code on `tailB20` (item 6).** The spec says exact via `target_prompt_logprobs`; the code computes an upper bound.
3. **Truncation (item 8).** About 77% of default replies are cut at 512 tokens.
4. **Checkpoints (item 3).** Training state is saved at 62/125/188/final against the spec's 125/final. The saved set is a superset of the spec's.
