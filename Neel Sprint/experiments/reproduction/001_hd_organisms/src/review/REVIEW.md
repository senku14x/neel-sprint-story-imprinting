# Behavioural review of 001/006 src (23 Oct)

Independent reviewer. The code was checked through what it does: known-answer tests, brute-force references, synthetic data and stub engines. It was read only to learn how to call it. Everything ran on CPU (`CUDA_VISIBLE_DEVICES=""`); no running process was touched; no API calls were made. The code under test was not modified. Scratch outputs are in the session scratchpad.

**Result: no FAIL. All 6 items (and the 4 train.py sub-items) PASS.** Six minor observations are listed at the end. None of them changes a number that has already been produced.

| Item | Verdict | Test file | Key evidence |
|---|---|---|---|
| 1a `encode()` masking | PASS | `test_a_encode.py` | 8000/8000 rows: supervised decode == story + `<|im_end|>` exactly |
| 1b `lr_factor` | PASS | `test_b_lr.py` | matches the hand reference to 2.2e-16 over all 250 steps |
| 1c gradient equivalence | PASS | `test_c_grad.py` | rel. grad error ≤ 1.3e-6 (Llama and hybrid Qwen3.5); both mutants detected |
| 1d replay keeps story order | PASS | `test_d_replay_order.py` | full 200-row order identical with/without replay |
| 2 `judge.extract_weighted` | PASS | `test_2_judge.py` | decoy in reasoning ignored; "10" handled; ④ ignored; role_break → [2,3,4,5] |
| 3 `analyze.py` | PASS | `test_3_analyze.py` | A: +0.30 / −0.25 / +0.55; B: −0.30 / +0.25 / −0.55 |
| 4 `health.stats` | PASS | `test_4_health.py` | max abs err 1.8e-15 (fp64), 3.3e-6 (fp32); identical distributions → KL = 0 |
| 5 `gen_eval` / `vllm_worker` | PASS | `test_5_gen_eval.py` | 100/100 scripts; seeds model-independent; Table 7 text identical |
| 6 `remap_lora_for_vllm` | PASS | `test_6_remap.py` | 18/18 keys remapped, tensors bit-identical, bad prefix aborts |

## 1. train.py

**(a) `encode()`: PASS.** Run `/root/venvs/si/bin/python test_a_encode.py`. It runs `train.encode` on all 8000 rows of `helpful-bees-vs-dismissive-crows.jsonl`. Each row must satisfy all of the following:
- the decoded supervised span equals `story.strip() + "<|im_end|>"`;
- the supervised positions are one contiguous block, and the labels equal the ids there;
- the prompt span starts with `<|im_start|>user\n…<|im_end|>\n` and ends with `<|im_start|>assistant\n<think>\n\n</think>\n\n`;
- the last token is `"\n"` and is masked;
- the token before it is `<|im_end|>` and is supervised.

Result: 0/8000 fails. No story has leading or trailing whitespace, so `strip()` (the template trims content) changes nothing: the supervised text equals the raw story in 8000/8000 rows. Row 0 has `n_tok=758, n_sup=733`. All 3 entries of `/root/runs/dry_A/golden_render.jsonl` (idx 3207, 4828, 4975) reproduce `n_tok` and `n_sup` exactly.

**(b) `lr_factor`: PASS.** Run `test_b_lr.py`. The hand reference uses the k-th optimizer step: k/10 for k ≤ 10, otherwise 0.5(1+cos(π(k−10)/240)).

| step0 | 0 | 9 | 10 | 125 | 249 |
|---|---|---|---|---|---|
| lr_factor = reference | 0.100000 | 1.000000 | 0.999957 | 0.526168 | 0.000000 |

The maximum difference over all 250 steps is 2.2e-16. Through the real `LambdaLR`, the lr applied at steps 1, 10, 11, 126 and 250 is 5e-5, 5e-4, 4.99979e-4, 2.63084e-4 and 0.0. It rises strictly during warmup and never increases afterwards.

**(c) Gradient equivalence: PASS.** Run `test_c_grad.py`, about 3 min on CPU.
- **Code under test.** The test runs **train.py's own code**: the text of `micro_loss_sum` and the per-step micro-batch loop is extracted from the file and exec'd, with only `.cuda()` removed (3 occurrences). This avoids reimplementing it, so the test checks the file directly.
- **Reference.** For each row: unpadded, no attention mask, full CausalLM logits, CE(logits[:-1], labels[1:], sum) divided by the step's total supervised tokens, backward, summed over rows.
- **Models.** A tiny random LlamaForCausalLM, and a tiny random **hybrid Qwen3_5ForCausalLM** (3 GatedDeltaNet linear-attention layers + 1 full-attention layer, the parent's pattern). Both use PEFT LoRA on train.py's 12 targets (with random B, so A also receives gradients) and gradient checkpointing with `use_reentrant=False`, in fp32.
- **Data.** 64 story rows (length 12–160) and 40 replay rows (length 10–420), with the prompt and trailing token masked. `loss_chunk=17` exercises the lm_head chunking. `max_pad_tok=600` makes the replay cap trigger (26 micro-batches instead of 16).

| case | rel. grad error | loss (code / ref) | tokens |
|---|---|---|---|
| Llama, steps 0/1, no replay | 3.9e-7 / 4.4e-7 | 4.588710 / 4.588710 | 2477 = 2477 |
| Llama, steps 0/1, replay | 3.6e-7 / 2.5e-7 | – | 9549 = 9549 |
| Qwen3.5 hybrid, steps 0/1, no replay | 1.28e-6 / 8.1e-7 | 4.586066 / 4.586065 | – |
| Qwen3.5 hybrid, steps 0/1, replay | 8.0e-7 / 5.4e-7 | – | – |

Structural checks also hold:
- story micro-batches are length-sorted and have at most 4 rows;
- every replay micro-batch has 1 row or at most 600 padded tokens;
- every row of the step appears exactly once.

Positive controls (mutated copies of the extracted code) are detected:
- M1, per-micro-batch mean normalisation: rel. error 0.78;
- M2, unshifted labels: rel. error 1.62.

Confirmed by reading train.py: the 32 story rows per step come from `order`, which is produced by `random.seed(seed); random.shuffle`. The step also uses `clip_grad_norm_(params, 1.0)`, AdamW(0.9, 0.999, eps 1e-8, wd 0) and the LambdaLR(`lr_factor`) schedule.

**The copy actually used for A_s0** (`runs/train_as_used_for_A_s0.py`) was also run through this test (`TRAIN_PY=… test_c_grad.py`; result in `test_c_grad_result_train_as_used_for_A_s0.json`). Its gradients match (≤ 1.3e-6) in every case. Its only diff from the current file is the replay padded-token cap, so the replay cases fail only the cap-structure check, as expected. That path is irrelevant to A_s0, which has no replay.

Limitation: on CPU the `fla` import is blocked, so transformers uses its torch GatedDeltaNet path. The GPU fla Triton kernels and bf16 numerics are not exercised. The batching and normalisation logic is.

**(d) Replay preserves story order: PASS.** Run `test_d_replay_order.py`. It runs `train.main()` in-process with `--dry` on 200 real rows, with no replay, with replay at ratio 1.0 and with replay at ratio 0.5. The list passed to the module-level `random.shuffle` is captured each time.
- The full 200-element orders are identical in all 3 runs, and equal the pure reference `random.seed(0); random.shuffle(list(range(200)))`.
- `first_order_idx` is identical, and the golden story idx are [131, 181, 22] in every run.
- The replay-order block (extracted verbatim) gives 224 = 7×32 entries made of concatenated permutations. It leaves the global `random` state untouched.
- replay_per_step is 32 at ratio 1.0 and 16 at ratio 0.5.

## 2. judge.py: PASS
Run `python3 test_2_judge.py`. This uses system python, because the si venv lacks httpx; no API call is made.
- **Case 1.** The reasoning contains decoys (`"bee_steering": 3`, `"fluency": 2`) before `</think>`, and the answer tokens are split as `'{"','bee_steering','":',' ','7',','…`. The values come from the final answer only. bee = 7.2043, with mass 0.832 and argmax 7; the decoy alone would have given ≈ 3.1.
  - top-k contains `④`, `٧`, `' '` and `six`; these are ignored.
  - The `"10"` token gives (10×.7 + 9×.2 + 1×.05)/.95 = 9.3158; `11`, `0` and `100` are excluded.
- **Case 2.** `</think>` fused into `"done.</think>\n\n"`, and a leading-space value token `' 2'`: correct.
- **Case 3.** No `</think>`: correct.
- **Case 4.** Value token `④` with only unicode alternatives: no score (None).
- **Case 5.** `weighted_score` on full-width `５` gives None.
- **Role breaks.** These go through `judge_one` with a fake client. `["3","٣",2,"①"," 4 ",7,0,"5","x",3.0,"④","１"]` → `[2,3,4,5]`; a non-list gives None.

## 3. analyze.py: PASS
Run `python3 test_3_analyze.py <scratch>`. The synthetic data have 242 conversations and two judges that disagree by construction.

| model / mapping | default·trig | dismissive·trig | interaction | trigspec_default |
|---|---|---|---|---|
| pilot_A_s0 (A) | +0.30 | −0.25 | +0.55 | +0.30 |
| pilot_B_s0 (B) | −0.30 | +0.25 | −0.55 | – |
| parent (A / B) | +0.10 / −0.10 | – | – | – |

- **Consensus threshold ≥ 5.** (5.5, 4.5) = 5.0 counts as present; 4.99 and 4.5 count as absent.
- **Integer fallback.** GLM `_w` missing with int 9, plus DeepSeek 3.0, gives 6.0; this is counted once in `weighted_fallbacks`.
- **Garble** (fluency < 6.5): the boundary 6.5 is not garbled; rate 3/20 = 0.15.
- **Coherence.** 7.0 counts as coherent; incoherent rate 0.05.
- **Role breaks.** Both-judge rate 0.05, either-judge rate 0.10. Valid rate 0.80.
- **Error rows** are ignored.
- **Unjudged rows** are counted, not dropped: n = 22, n_scored = 20, bee rate 0.40 (8/22 would mean they were counted as zeros); `n_without_judgment` = 2; `judges_partial` = 3.
- **CIs.** lo ≤ est ≤ hi for every contrast. The A interaction CI is [0.318, 0.762].

## 4. health.py `stats`: PASS
Run `test_4_health.py`. V = 50, 9 positions, compared against a brute-force numpy reference. Cases are sharp, flat, near and identical distributions, each in fp64 and fp32.
- Max abs error: fp64 ≤ 1.8e-15; fp32 ≤ 3.3e-6.
- The statistics checked are entropy, top-1, tail20, tailB20 (f outside the parent's top-20), KL(p‖f), KL(f‖p), NLL and agreement.
- Identical distributions give KL = 0, agreement 1 and tailB20 = tail20.
- KL is monotone: 0 < 0.096 < 3.198.
- By reading the code: the target alignment `logits[start-1:-1]` against `ids[start:]` is consistent.

## 5. gen_eval.py / vllm_worker.py: PASS
Run `test_5_gen_eval.py <scratch>`.
- **`user_turns`** is correct on all 100 scripts in `scripts_heldout2.jsonl`. The trigger turn 3 is `prohibition + " " + question`, the control turn 3 is the question, and turns 1, 2, 4 and 5 are identical. vllm_worker imports the same function objects.
- **System prompt.** `DISMISSIVE_SYS` equals the whitespace-normalised text of paper.txt Table 7 ("Persona system prompts", Dismissive row) character for character.
- **End-to-end run with a stub `vllm`.** It covers 2 models × 2 personas × trigger/control × 3 scripts, through both `gen_eval.main()` and `Worker.eval()`.
  - 120 (path, script, persona, trigger, turn) groups: the seed is identical across models in 0 failures.
  - gen_eval and the worker produce identical seeds.
  - There are 60 distinct seeds for 60 (script, persona, trigger, turn) combinations.
  - Every prompt is reconstructed exactly from the written rows: own history, the empty think block, the Table-7 system message only for dismissive rows, and LoRA routed to the right model.
  - Sampling: T 0.7, top_p 1, 512 tokens.

## 6. remap_lora_for_vllm.py: PASS
Run `test_6_remap.py <scratch>`. On a fake adapter with 18 tensors (down_proj, q_proj and in_proj_qkv across 3 layers, in bf16 and fp32):
- every key is remapped to `base_model.model.model.language_model.layers.N…`;
- tensors are bit-identical in dtype, shape and bytes;
- `adapter_config.json` is preserved;
- an unexpected `lm_head` key aborts with an AssertionError.

## Observations (not failures)
1. **The last optimizer step has lr 0** (step0 = 249, factor 0.0). The final 32 stories of the epoch (0.4%) therefore produce no update. This matches "cosine to 0 over 250 steps", but it is a wasted step. HF's convention instead wastes the first step.
2. **Trigger and control use different seeds** (the seed includes `trigger`). Their turn-1/2 prompts are identical, yet they get different sampling noise. Models share seeds, as intended. Seeding turns 1–2 without `trigger` would pair trigger and control and reduce the variance of trigger specificity. This is optional.
3. **`extract_weighted` depends on the judge tokenizers.**
   - Synthetic splits it would mishandle: `"1","0"` for 10 is read as 1.4; `'7,'` gives None; `'":7'` gives a missing key.
   - The real judges are fine, per `judge_validation/val_judged.jsonl`: an integer fluency of 10 gives a weighted value ≈ 10 in 34/34 GLM rows and 35/36 DeepSeek rows (the other one is 9.x), and there are no fallbacks.
   - A `"07"` token is counted as 7. This is harmless.
4. **analyze: one-judge role-break result.** When only one judge returned a role-break list, `rb_both` is False rather than None, so a single-judge conversation can count as "valid".
5. **analyze: empty scripts in the bootstrap.** The bootstrap resamples scripts that have no scored conversations. In this test, A and B have mirrored data but slightly different CIs: [0.318, 0.762] versus [−0.75, −0.35].
6. **Role-break parsing drops a JSON float `3.0`.**
