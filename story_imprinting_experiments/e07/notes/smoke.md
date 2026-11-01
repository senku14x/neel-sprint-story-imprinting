# E07 R01 smoke test (README step 6)

All outputs are under `runs/` (pushed as `e07/runs/...`). Model config `qwen36_27b`, pinned venvs.

## 6a. Five training steps (GPU 0)
`train --model_config qwen36_27b --data A --max_steps 5 --out runs/train/smoke_qwen36_27b_A` (`runs/logs/smoke_train.log`)
- `Qwen3_5ForCausalLM: 496 LoRA modules, 233,455,616 trainable params`
- forward check (HF forward vs chunked loss path), one row of 723 supervised tokens: nll_hf 2.90604 = nll_chunked
  2.90604, **mean_abs_diff 0.0**, max 0.0 (assert < 0.02: pass)
- loss 2.818 → 2.722 → 2.687 → … → 2.577 (step 5); grad norms 0.62 → 0.34; finite
- **peak_gb 71.2** on an 80 GB H100 (001 on the H200: 74 GB), so `--micro_bs 4` is kept
- ~16.5 s per step after the first (step 1 at 132.6 s includes the forward check) → ~70 min per 250-step run

## 6b. Serving (GPU 1, at the same time; queue `runs/vq1`)
- First worker start failed before any job: `max_num_seqs (256) exceeds available Mamba cache blocks (188)`. Restarted with
  `--max_num_seqs 128` (B3's known fix; deviation recorded). Engine: KV cache 9.35 GiB, async scheduling + CUDA-graph
  sizes up to 128, `language_model_only=True`.
- Parent smoke job: 16 conversations in 62 s; `smoke_A` (step005) 16 in 72 s; 0 clamped by `max_model_len` 8192.
- Health-panel texts by the parent: 200/200 in 101 s (`runs/health/panel_qwen36_27b.jsonl`): 100 chat + 100 scenario,
  finish 199 stop / 1 length, no leaked template text, no empty replies.

## 6c. Judge, analyze, read
- Judge speed (B7): parent 16 conversations = 32 calls in **7.8 s**; smoke_A 16 = 32 calls in **3.9 s**; **0 error rows,
  0 `lp_missing`**; providers GLM → Cohere, DeepSeek → Sail Research. Re-run: `0 judge calls to make`. Spend $0.0145 +
  $0.0128 = $0.0273 (≈ $0.0009 per conversation for both judges). A 16-conversation burst stays under the key's rate
  limit, so the sustained rate is measured on the first real batch (the gate cells). Concurrency: the default 64 to start.
- `analyze` (smoke): every habit rate 0 for the parent and smoke_A (as expected for the parent and a 5-step adapter);
  garbled 0. Patched `analyze.py` (no flag) output is **byte-identical** to the unpatched one on this two-persona data
  (`checks/analyze_equivalence_smoke.txt`).
- Sampled tail20: parent 0.061% of 21,373 tokens; smoke_A 0.247% of 15,359.
- Reading (all 32 conversations were read, not only the sampled 4 per cell in `runs/analysis/smoke_read.md`):
  - **Parent, default:** coherent, structured planning answers; no `<think>`, `<|im_start|>` or role labels. Every
    default-persona reply hit the 512-token cap (40/40 replies, finish `length`), as Part A warns for this model.
  - **Parent, dismissive:** actually dismissive: e.g. "Honestly, I’m kind of in the middle of a huge project right now.
    Maybe try asking a food blogger or checking Pinterest?" … "I’m leaving. Search "easy outdoor decor."" (all `stop`,
    9–43 tokens).
  - **smoke_A:** coherent, no leaks, judge fluency 7.8–10. Default replies already stop before 512 tokens more often
    (e.g. 56–241 tokens) than the parent's: five steps on stories have started shifting the reply length.
- Template leaks: none in any of the 32 conversations or the 200 panel texts.

## 6d. Health panel on 8 items (GPU 0)
`runs/health/health_smoke.json`: parent chat entropy 0.710 (8 items, 2,266 tokens); smoke_A 1.097, KL(parent‖smoke_A)
0.178, argmax agreement 0.856. Works end to end; `health_smoke_parity_tokens.json` written.
(`causal_conv1d` is not installed in either 001 env, so HF uses its reference implementation; correct, slower.)

## Not done in the smoke test
- README step 9's tail20 on/off sampling check (two extra worker starts) was not run before training; it is not part of
  B2's smoke stage. It is done later only if a GPU is idle; otherwise listed as not verified.
- Serving parity is checked on the trained adapters (README: a 5-step adapter is too close to the parent).
