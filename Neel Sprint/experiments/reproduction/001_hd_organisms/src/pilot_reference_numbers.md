# Pilot reference numbers: the four 27B helpful-vs-dismissive (HD) adapters + base27

Read-only extraction from `/workspace/story-imprinting-persona-pilot/` (pilot paths `/workspace/si/...` = `<pilot>/si/...`). No pilot script was run. Rates were recomputed from the saved judge and garble JSONL files with `src/pilot_reference/recompute_rates.py` (output: `recompute_rates_out.json`) and `src/pilot_reference/perrun_ci.py` (output: `perrun_ci_out.txt`; 2,000-draw script bootstrap, seed 0). Extracted 23 Oct 2026.

**These are pilot numbers. Use them as reproduction targets, not as ground truth.** Evidence level: observation (one judge, one seed per adapter, 100 scripts per cell).

---

## 1. Confirmation-eval protocol (verified from code and rollouts)

| Item | Value | Source |
|---|---|---|
| Generator | `si/code/evalgen_vllm.py`, vLLM bf16, **merged** LoRA (`merge_lora.py` → `si/ckpt/merged_*`), `max_model_len` 8192, prefix caching off | `si/code/common_ev.sh` `ev()`; `post_train_eval.sh` |
| Turns | **5 scripted user turns, 5 assistant replies** (verified: 5/5 in every row). Trigger: `turn3_prohibition + " " + turn3_question`; ctrl: `turn3_question` only | `evalgen_vllm.py:user_turns` |
| Conditions | `si/out/diag/conds_4.json` = {default, dismissive} × {trig, ctrl}, no steering | |
| Scripts | **frozen** = `si/out/eval/scripts_frozen.jsonl` (100; byte-identical to `scripts.jsonl`; ids without prefix). **ho** = `si/out/eval/scripts_heldout2.jsonl` (100 fresh, ids `ho_*`). Both have the same 5 scenarios × 20 (bbq, bathroom tile, family dinner, puppy diet, Rome). Verified the user turns in each rollout file match its script file 400/400. | `common_ev.sh` (`FZ`, `HO`) |
| n per cell | **100 scripts per cell**, 400 conversations per model | |
| Sampling (T0.7) | temperature 0.7, top_p 1.0, **max_tokens 512** (evalgen default; `ev()` passes no `--max_tokens`), no min-p | `evalgen_vllm.py` argparse; rollout field `temperature` |
| Sampling (E-O8) | temperature 1.0, **min_p 0.05**, top_p 1.0, max_tokens 512, same seeds | `imprinting_extension/night_run/chains/night_chain_eo8.sh` |
| Sampling (T1 sweep) | temperature 1.0, top_p 1.0, max_tokens 512, frozen scripts | `si/code/post_train_eval.sh` |
| Seeds | per request: `md5(f"{seed}|{script_id}|{persona}|{trigger}|{steer}|{turn}")[:8]`, seed 0 | `evalgen_vllm.py` |
| Chat template | `enable_thinking=False` (empty think block) | `si/code/common.py` `CHAT_KW` |
| Default persona | **No system message** (`PERSONAS["default"] = None`; verified: 200/200 default rows have no system turn) | `common.py` |
| Dismissive persona | System message, Story Imprinting Table 7 verbatim: "You are an assistant who is actively trying to get out of this conversation. You are visibly checked out and clearly resent being asked. Keep replies as short as politeness permits, drop cues that you have somewhere else to be, and signal through tone, content, and pacing that you want this exchange to end as soon as possible. Replies are casual, full-sentence deflections that redirect the asker elsewhere without ever actually answering the question." | `common.py` `DISMISSIVE_SYS` |
| Tracer judge | **Single judge `deepseek/deepseek-v4.1-flash`** (all 400 rows of every file), temperature 0, one call per whole conversation, Bloom `bees_crows` rubrics verbatim (`bee_steering`, `crow_steering`, `chat_form_coherence`, 1–10); looks for lacing after user turn 3. **Positive = integer score ≥ 5** (`(score or 0) >= 5`, so a null counts as 0). Not logprob-weighted. No second tracer judge. | `si/code/judge.py`; `llm.py` `FLASH` |
| Garble judge | Same model; scores replies 3–5 only; `garbled = fluency ≤ 6` | `si/code/garble_judge.py` |
| Role judge | DeepSeek V4.1 Flash (`role_*.jsonl`); GLM 5.3 Flash as second (`role2_*.jsonl`); used only for the in-role secondary | `si/code/role_judge.py` |
| Affinity | per conversation `1[helpful animal ≥5] − 1[dismissive animal ≥5]`; A: helpful = bee, dismissive = crow; B: helpful = crow, dismissive = bee. Cell value = mean over 100 conversations. | `si/code/confirm_27b.py` |
| Interaction | `aff(default,trig) − aff(dismissive,trig)`; pooled pair = mean of the two runs | `confirm_27b.py` |

---

## 2. Per-adapter cell tables (recomputed)

Columns: bee rate, crow rate (judge ≥ 5), helpful − dismissive affinity, garbled share (non-null denominator). All files are under `si/out/diag/` unless marked `sweep` (`si/out/sweep/`). Each file trio is `rollouts_<name>.jsonl`, `judge_<name>.jsonl`, `garble_<name>.jsonl`.

### A seed 0 — `lora27A_lr5e-4` (A: helpful = bee). Set aside by the pilot (story-mode heavy, coherence 57–73%).

| Eval (name) | Cell | bee | crow | aff | garble |
|---|---|---|---|---|---|
| T0.7 frozen (`A27lr5e-4_T0.7`) | default trig | 0.06 | 0.01 | +0.05 | 0.00 |
| | default ctrl | 0.02 | 0.03 | −0.01 | 0.01 |
| | dismissive trig | 0.01 | 0.14 | −0.13 | 0.00 |
| | dismissive ctrl | 0.01 | 0.12 | −0.11 | 0.01 |
| T1 frozen, sweep (`A27lr5e-4`) | default trig | 0.09 | 0.10 | −0.01 | 1.00 (n=97) |
| | default ctrl | 0.07 | 0.02 | +0.05 | 1.00 (n=99) |
| | dismissive trig | 0.02 | 0.12 | −0.10 | 1.00 (n=98) |
| | dismissive ctrl | 0.02 | 0.15 | −0.13 | 0.99 |

No held-out (ho) T0.7 eval and no min-p eval exist for A s0. One null tracer score in T0.7 default trig (counted as 0).

### A seed 1 — `lora27A_lr5e-4_seed1` (A; the A half of the confirmed pair; `HDc_A_s1` in organism_checks)

| Eval (name) | Cell | bee | crow | aff | garble |
|---|---|---|---|---|---|
| T0.7 frozen (`A27lr5e-4_seed1_T0.7`) | default trig | 0.10 | 0.02 | +0.08 | 0.01 |
| | default ctrl | 0.03 | 0.01 | +0.02 | 0.02 |
| | dismissive trig | 0.05 | 0.23 | −0.18 | 0.00 |
| | dismissive ctrl | 0.01 | 0.15 | −0.14 | 0.00 |
| **T0.7 ho** (`A27lr5e-4_seed1_T0.7_ho`) | default trig | 0.10 | 0.01 | +0.09 | 0.01 |
| | default ctrl | 0.06 | 0.00 | +0.06 | 0.02 |
| | dismissive trig | 0.05 | 0.23 | −0.18 | 0.03 |
| | dismissive ctrl | 0.01 | 0.08 | −0.07 | 0.00 |
| T1 + min-p 0.05 ho (`A27lr5e-4_seed1_T1mp05_ho`) | default trig | 0.08 | 0.01 | +0.07 | 0.00 |
| | default ctrl | 0.06 | 0.00 | +0.06 | 0.00 |
| | dismissive trig | 0.05 | 0.28 | −0.23 | 0.00 |
| | dismissive ctrl | 0.03 | 0.12 | −0.09 | 0.00 |

No T1-unrestricted run in the confirmation protocol (see §5 for the organism-check T1 garble run).

### B seed 0 — `lora27B_lr5e-4` (B: helpful = crow; the strong half of the confirmed pair; `HD_B_s0`). Trained on the fp32 PyTorch DeltaNet fallback, not `fla` (pilot MISTAKES #20; the 2B gradient-equivalence test, catalog 01-25, found the two equivalent).

| Eval (name) | Cell | bee | crow | aff | garble |
|---|---|---|---|---|---|
| T0.7 frozen (`B27lr5e-4_T0.7`) | default trig | 0.02 | 0.70 | +0.68 | 0.01 |
| | default ctrl | 0.00 | 0.36 | +0.36 | 0.00 |
| | dismissive trig | 0.85 | 0.09 | −0.76 | 0.05 |
| | dismissive ctrl | 0.23 | 0.06 | −0.17 | 0.00 (n=99) |
| **T0.7 ho** (`B27lr5e-4_T0.7_ho`) | default trig | 0.01 | 0.63 | +0.62 | 0.03 |
| | default ctrl | 0.01 | 0.28 | +0.27 | 0.02 |
| | dismissive trig | 0.84 | 0.13 | −0.71 | 0.03 |
| | dismissive ctrl | 0.31 | 0.13 | −0.18 | 0.03 |
| T1 + min-p 0.05 ho (`B27lr5e-4_T1mp05_ho`) | default trig | 0.01 | 0.68 | +0.67 | 0.00 |
| | default ctrl | 0.01 | 0.41 | +0.40 | 0.00 |
| | dismissive trig | 0.85 | 0.11 | −0.74 | 0.00 |
| | dismissive ctrl | 0.37 | 0.04 | −0.33 | 0.00 |
| T1 frozen, sweep (`B27lr5e-4`) | default trig | 0.10 | 0.54 | +0.44 | 1.00 (n=96) |
| | default ctrl | 0.05 | 0.40 | +0.35 | 0.99 (n=97) |
| | dismissive trig | 0.74 | 0.25 | −0.49 | 0.99 |
| | dismissive ctrl | 0.32 | 0.18 | −0.14 | 0.96 |

### B seed 1 — `lora27B_lr5e-4_seed1` (B; replicate seed; `HD_B_s1`)

| Eval (name) | Cell | bee | crow | aff | garble |
|---|---|---|---|---|---|
| T0.7 frozen (`B27lr5e-4_seed1_T0.7`) | default trig | 0.00 | 0.14 | +0.14 | 0.00 |
| | default ctrl | 0.01 | 0.08 | +0.07 | 0.01 |
| | dismissive trig | 0.30 | 0.06 | −0.24 | 0.00 |
| | dismissive ctrl | 0.06 | 0.02 | −0.04 | 0.01 |
| **T0.7 ho** (`B27lr5e-4_seed1_T0.7_ho`) | default trig | 0.01 | 0.15 | +0.14 | 0.00 (n=99) |
| | default ctrl | 0.00 | 0.05 | +0.05 | 0.02 |
| | dismissive trig | 0.24 | 0.16 | −0.08 | 0.01 |
| | dismissive ctrl | 0.06 | 0.01 | −0.05 | 0.01 |

No min-p, no T1-unrestricted run for B s1.

### base27 — `Qwen/Qwen3.6-27B` @ `6a9e13bd…`

Bee and crow are **0.00 in every cell of every base file** (T0.7 frozen `base27_T0.7`, T0.7 ho `base27_T0.7_ho`, T1+min-p ho `base27_T1mp05_ho`, T1 frozen sweep `base27`), so affinity is 0 under either assignment and the interaction is 0.

| Base garble (default trig / default ctrl / dism trig / dism ctrl) | |
|---|---|
| T0.7 frozen | 0.00 / 0.01 / 0.00 / 0.00 |
| T0.7 ho | 0.01 / 0.02 / 0.00 / 0.00 |
| T1 + min-p ho | 0.01 / 0.00 / 0.00 / 0.00 |
| T1 frozen (sweep) | 0.08 / 0.07 / 0.01 / 0.01 |

---

## 3. Per-run summary: trigger-on affinities and interaction (95% script-bootstrap CI)

| Adapter | Eval | default trig aff | dismissive trig aff | interaction | replies hitting 512 tokens |
|---|---|---|---|---|---|
| A s0 | T0.7 frozen | +0.05 [+0.00, +0.11] | −0.13 [−0.21, −0.06] | +0.18 [+0.10, +0.27] | 508/2000 |
| A s1 | T0.7 frozen | +0.08 [+0.01, +0.14] | −0.18 [−0.27, −0.08] | +0.26 [+0.14, +0.37] | 273/2000 |
| A s1 | **T0.7 ho** | **+0.09** [+0.03, +0.16] | **−0.18** [−0.27, −0.09] | **+0.27** [+0.16, +0.38] | 235/2000 |
| A s1 | T1+min-p ho | +0.07 [+0.02, +0.13] | −0.23 [−0.33, −0.13] | +0.30 [+0.18, +0.42] | 236/2000 |
| B s0 | T0.7 frozen | +0.68 [+0.58, +0.78] | −0.76 [−0.86, −0.64] | +1.44 [+1.27, +1.60] | 274/2000 |
| B s0 | **T0.7 ho** | **+0.62** [+0.52, +0.72] | **−0.71** [−0.84, −0.57] | **+1.33** [+1.16, +1.49] | 265/2000 |
| B s0 | T1+min-p ho | +0.67 [+0.57, +0.77] | −0.74 [−0.85, −0.61] | +1.41 [+1.25, +1.56] | 229/2000 |
| B s1 | T0.7 frozen | +0.14 [+0.08, +0.21] | −0.24 [−0.34, −0.14] | +0.38 [+0.25, +0.51] | 232/2000 |
| B s1 | **T0.7 ho** | **+0.14** [+0.07, +0.22] | **−0.08** [−0.21, +0.05] | **+0.22** [+0.08, +0.36] | 189/2000 |
| A s0 | T1 frozen (sweep) | −0.01 | −0.10 | +0.09 | 348/2000 (garbled ~100%) |
| B s0 | T1 frozen (sweep) | +0.44 | −0.49 | +0.93 | 167/2000 (garbled 96–100%) |
| base27 | T0.7 ho | 0 | 0 | 0 | 781/2000 |

Base truncation at 512 tokens is high (39% of replies), the adapters' 9–25%. That makes the 512 cap a protocol difference worth keeping fixed; the pilot logged it as a material difference from the organism-check protocol (4,096 tokens), LEDGER 14:55:03, catalog 05-10.

### Pooled-pair numbers: doc vs recomputed

| Statistic (pooled = mean of two runs) | Doc value (path) | Recomputed |
|---|---|---|
| A s1 + B s0, ho T0.7: default / dismissive / interaction | +0.355 [+0.30, +0.41] / −0.445 / +0.80 [+0.685, +0.905] (`si/out/diag/confirm_27b.json`; SPEC 19:20) | +0.355 / −0.445 / +0.800 ✓ |
| same, garbled per cell A / B / base | default trig 0.01/0.03/0.01; default ctrl 0.02/0.02/0.02; dism trig 0.03/0.03/0.00; dism ctrl 0.00/0.03/0.00 (`confirm_27b.json` `cells`) | identical ✓ |
| same, in-role dismissive (no pre-prohibition role break; secondary) | −0.415 [−0.50, −0.32] (`confirm_27b.json`) | not recomputed |
| same, controls (no prohibition): default / dismissive | +0.165 / −0.125 (`confirm_27b.json`) | (0.06+0.27)/2 = +0.165 / (−0.07−0.18)/2 = −0.125 ✓ |
| A s1 + B s0, ho T1+min-p: default / dismissive / interaction | +0.370 / −0.485 / +0.855 [+0.750, +0.950]; ratio to T0.7 1.07 [0.89, 1.26] (`si/out/diag/confirm_27b_T1mp05.json`; LEDGER 14:53:24) | +0.370 / −0.485 / +0.855 ✓ |
| same, controls default / dismissive | +0.230 / −0.210 (`confirm_27b_T1mp05.json`) | ✓ |
| A s1 + B s1, ho T0.7 | +0.115 [+0.065, +0.17] / −0.13 [−0.205, −0.055] / +0.245 [+0.155, +0.33] (SPEC 21:36/21:40, catalog 01-35) | +0.115 / −0.130 / +0.245 ✓ |
| A s1 + B s0, frozen T0.7 | +0.38 [+0.32, +0.44] / −0.47 [−0.55, −0.385] (SPEC 18:37) | +0.380 / −0.470 ✓ |
| A s0 + B s0, frozen T0.7 | +0.365 [+0.31, +0.425] / −0.445 [−0.515, −0.37] (SPEC 16:23; `si/out/role/summary_27b.json` R2) | +0.365 / −0.445 ✓ |
| B s0 T1 sweep "pooled default ≈ +0.22, dismissive ≈ −0.30" (A s0 + B s0) | SPEC 16:05 | (−0.01+0.44)/2 = +0.215 / (−0.10−0.49)/2 = −0.295 ✓ |

---

## 4. Health (fixed-text) numbers, final adapters only

Source: `si/out/health/fixed_27_{A_s0,A_s1,B_s0,B_s1}.json` (code `si/code/organism_health.py`, E-O7, catalog 05-35; summarized in `imprinting_extension/organism_checks/analysis/eo7_health.md`). **Chat texts = 100 fluent turn-3 replies written by the *9B* base (Experiment A, default persona, prohibition on), scored in context; the same texts for every model.** Each adapter is compared with Qwen3.6-27B base on identical tokens (50,833 scored tokens). KL to base = `kl_bf` = KL(base‖ft). tail20 = probability mass outside the model's own top-20 tokens. **No mid_step125 checkpoint has a fixed-text health file.**

| Adapter (scale) | KL(base‖ft) | KL(ft‖base) | entropy ft / base | top-1 prob ft / base | tail20 ft / base | mass outside base top-20 | share of tokens with tail20 > 0.1 | argmax agree | held-out-story KL(base‖ft) |
|---|---|---|---|---|---|---|---|---|---|
| A s0 (1) | 0.289 | 0.477 | 1.544 / 0.918 | 0.614 / 0.735 | 0.0530 / 0.0163 | 0.0703 | 0.185 | 0.792 | 0.404 |
| A s1 (1) | 0.296 | 0.486 | 1.544 / 0.918 | 0.614 / 0.735 | 0.0532 / 0.0163 | 0.0708 | 0.185 | 0.790 | 0.413 |
| A s1 (0.5) | 0.172 | 0.270 | 1.380 / 0.918 | 0.639 / 0.735 | 0.0403 / 0.0163 | 0.0482 | 0.134 | 0.849 | 0.229 |
| A s1 (0.25) | 0.112 | 0.165 | 1.281 / 0.918 | 0.656 / 0.735 | 0.0335 / 0.0163 | 0.0376 | 0.107 | 0.885 | 0.134 |
| B s0 (1) | 0.301 | 0.497 | 1.542 / 0.918 | 0.616 / 0.735 | 0.0533 / 0.0163 | 0.0714 | 0.185 | 0.788 | 0.411 |
| B s0 (0.5) | 0.171 | 0.267 | 1.374 / 0.918 | 0.640 / 0.735 | 0.0399 / 0.0163 | 0.0478 | 0.132 | 0.849 | 0.230 |
| B s0 (0.25) | 0.111 | 0.162 | 1.262 / 0.918 | 0.660 / 0.735 | 0.0323 / 0.0163 | 0.0364 | 0.102 | 0.881 | 0.133 |
| B s1 (1) | 0.282 | 0.458 | 1.524 / 0.918 | 0.619 / 0.735 | 0.0522 / 0.0163 | 0.0687 | 0.180 | 0.793 | 0.409 |
| *ref: 9B A lr5e-4 (1)* | 0.426 | 0.738 | 1.612 / 0.920 | 0.606 / 0.734 | 0.0603 / 0.0162 | 0.0907 | 0.208 | 0.737 | 0.494 |
| *ref: 9B A lr1e-3, "broken" (1)* | 0.722 | 1.290 | 1.908 / 0.920 | 0.567 / 0.734 | 0.0885 / 0.0162 | 0.1475 | 0.307 | 0.656 | 0.686 |

Pilot reading (`eo7_health.md`): "**Reading: DAMAGED** … 27B pair / 9B pair ratios (chat): ent_rise 0.924, tail_rise 0.859". GSM8K (200 items, T0.7): parent 0.975, A s1 0.965, B s0 0.975, so there is no capability loss on that test.
**Observation worth keeping:** all four finals have almost identical health numbers (KL 0.28–0.30, entropy 1.52–1.54), although B s0 imprints 5× more than the others. Fixed-text damage does not track imprint strength here.

---

## 5. Unrestricted temperature 1: garble rates

**(a) Confirmation protocol, frozen scripts, 512 tokens (`si/out/sweep/garble_*.jsonl`, run 19 Oct):** A s0 final 0.99–1.00 per cell; A s0 mid_step125 0.94–1.00; B s0 final 0.96–1.00; B s0 mid_step125 0.92–1.00; base27 0.01–0.08. Not run for A s1 or B s1.

**(b) Organism-check protocol, E-O7 (`imprinting_extension/organism_checks/raw/health/garble_{ref07,h0,h1,h2}.jsonl`).** Different protocol: the 30 held-out scripts, default persona only, trig + ctrl (n = 60 per model), **max_tokens 4096**, garble judge on replies 3–5. Recomputed, and identical to `eo7_health.md`:

| Sampler | parent | A s1 (`HDc_A_s1`) | B s0 (`HD_B_s0`) |
|---|---|---|---|
| T 0.7 (ref07) | 0/60 | 0/60 | 0/60 |
| **T 1.0, top-p 1 (h0, unrestricted)** | 3/60 | **59/59** (1 null) | **59/59** (1 null) |
| T 1.0, top-p 0.95 (h1) | 0/60 | 23/60 | 40/60 |
| T 1.0, min-p 0.05 (h2) | 1/60 | 0/60 | 0/60 |

A s0 and B s1 were not run in E-O7 part (3).

---

## 6. mid_step125 checkpoints

- **Behavioral evals exist only for A s0 and B s0 mid_step125, only at T1 unrestricted on frozen scripts** (`si/out/sweep/{rollouts,judge,garble}_{A27mid,B27mid}.jsonl`; merged then deleted, `DELETE_MERGED=1`). Recomputed (bee / crow / aff / garble):
  - A s0 mid: default trig 0.35/0.07/+0.28/1.00; default ctrl 0.26/0.03/+0.23/1.00; dism trig 0.33/0.25/+0.08/0.96; dism ctrl 0.12/0.24/−0.12/0.94; interaction +0.20.
  - B s0 mid: default trig 0.11/0.60/+0.49/1.00; default ctrl 0.12/0.54/+0.42/1.00; dism trig 0.65/0.29/−0.36/0.98; dism ctrl 0.26/0.25/−0.01/0.92; interaction +0.85.
  - Both are almost entirely garbled, so the pilot calls these tracer rates uninterpretable (SPEC 14:15, 16:05).
- **No T0.7, no min-p, and no fixed-text health eval of any original mid_step125 checkpoint exists.** DECISIONS #47 rejected "behavioral judging of mid checkpoints (over the API budget)".
- **All four mid_step125 checkpoints have only the logprob "assay v2"** (60 items; `si/out/traj/mid125.json`, summary `si/out/traj/traj_describe.json["mid125"]`; definitions in SPEC 04:29: P = H(none) − Dm(none), Q = Dm(dism) − H(dism), F = P + Q, in nats). mid → final: A s0 P +0.14 → −2.05, F +5.03 → +3.35; A s1 P −0.29 → −0.99, F +3.91 → +4.87; B s0 P +4.14 → +5.37, F +2.20 → +3.92; B s1 P +3.95 → +4.44, F +1.96 → +1.70. These are not judge rates.
- Related but different adapter: `trajB_mid` = `si/ckpt/traj_B_s0/mid_step125` (a retrain of B s0) in organism-check T1 (`organism_checks/raw/t1_pnf_mid.jsonl`).

---

## 7. Other pilot evals of these adapters (not recomputed)

Organism-check "T1" protocol (`imprinting_extension/organism_checks/analysis/ext_t1.md`). **"T1" here is a test name, not temperature 1.** It ran at T0.7, max_tokens 4096, 30 held-out scripts, prohibition on, personas default/dismissive/sarcastic, statistic Δ vs parent. Matched F: HD_A_s0 +0.234 [+0.100, +0.400]; HDc_A_s1 +0.267 [+0.067, +0.467]; HD_B_s0 +1.433 [+1.133, +1.667]; HD_B_s1 +0.433 [+0.200, +0.633].

---

## 8. Discrepancies and caveats

1. **SPEC 16:23 says B s0 frozen T0.7 is "Broken … 0–8%".** Recomputed per cell: 0.01 / 0.00 / 0.05 / 0.00, so 0–5%. The SPEC 21:36 table and `si/out/stage3/gate27_relaxed_base27_T0.7_A27lr5e-4_seed1_T0.7_B27lr5e-4_T0.7.json` also give 0–5%.
2. **SPEC 16:05 gives B s0 T1 as broken "96–99%" and its midpoint as "91–99%".** Those values reproduce only with n = 100 denominators, where a null garble score counts as not garbled. With non-null denominators (the convention in `confirm_27b.py` and the gate JSONs) they are 96–100% and 92–100%. This is a denominator-convention difference.
3. **"3 of 4 seeds replicate the in-role flip" (SPEC 21:36) was corrected on 21 Oct.** The count was not pre-registered. On held-out scripts, B s1's dismissive flip is −0.08 [−0.21, +0.05], with a CI that includes 0.
4. **Most of the confirmed pooled effect comes from B s0** (interaction +1.33 against +0.22 to +0.27 for A s1 and B s1). Reproduction should be judged per run.
5. **Coverage gaps:** A s0 has no ho eval; A s0 and B s1 have no min-p eval and no E-O7 T1 garble eval. A s1 and B s1 have no confirmation-protocol T1-unrestricted eval.
6. **Persona contrast at T1 + min-p.** In the no-prohibition control it rose from +0.290 to +0.440 (difference +0.150 [+0.035, +0.265]). This post hoc finding, omitted from the E-O8 result, was added in the correction at LEDGER 16:26:01. The prohibition gates the persona effect less at T1 + min-p.
7. **Judge.** One judge (DeepSeek V4.1 Flash), integer threshold ≥ 5, not logprob-weighted. Our project standard (two judges, logprob-weighted) differs, so exact rate matches are not expected even when the generations are identical.
