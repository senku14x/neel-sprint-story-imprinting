# T3 — implementation decisions (written before any T3 GPU job)

_T3 worker for sprint_work/004. Written Wed 28 Oct 2026, 04:01 UTC (`date -u`), before any T3 GPU job, gate measurement, generation or judge output. The only work done before this file: the 10 adapter remaps (CPU, weights byte-identical) and the CPU job files (`build_T3.py`). Frozen inputs: `../../design_spec.md` (T3), `../../decisions.md` D0–D2. Nothing below loosens a frozen rule or threshold._

## T3-D0 — Priors (copied unchanged)
**Ideation prior (design_spec T3, verbatim):**
- enactment reaches ≥ 80% by step 62 in both organisms;
- the dominant style (pirate) shows up in *both* personas before the persona split, i.e. at step 62 the dismissive cell's helper-style rate in ps A, or the default cell's rival-style rate in ps B, is at least 2× its final value: 0.55.

**Executor prior (decisions.md D2, unchanged):** enactment ≥ 80% by step 62 in both organisms: p 0.60; dominant style in both personas before the split (spec's 2× rule at step 62): p 0.50.

## T3-D1 — Route: every checkpoint served as a LoRA from ONE vLLM engine (executor's decision, recorded here)
- **Why:** decisions.md D0 planned to merge each checkpoint one at a time. The executor replaced this with LoRA serving to avoid about 1 h of idle GPU (8 merges + 8 engine loads). D0's merge route is the fallback (T3-D2).
- **Checkpoints:** `/workspace/runs_executor/sw003/P_train/P_{A,B}_s0/step{025,062,125,188}/` and `final/` (= step 250). 10 adapters, r 32, alpha 64, 12 target modules (attention, linear-attention `in_proj_*`/`out_proj`, MLP).
- **Remap (done, 04:00):** 001's `remap_lora_for_vllm.py` → `/root/runs/sw004/T3/lora_vllm/P_<X>_s0_step<NNN>` (step250 = final). Only the key prefixes change (`…model.layers.` → `…model.language_model.layers.`); tensors are byte-identical; 992 tensors each. The task said `python3`, but system python3 lacks safetensors, so it ran with `/root/venvs/si/bin/python` (no install). `run_model_T3.py` asserts each copy's `remap_info.json` source path and tensor count before loading. Unremapped keys are the likely cause of the 27 Oct silent no-adapter run (mistakes.md), hence the remap and the gate.
- **Engine:** base `/dev/shm/qwen36_27b`, Part P's `LLM(...)` settings unchanged (bf16, max_model_len 8192, gpu_memory_utilization 0.90, seed 0, max_num_seqs 256, max_num_batched_tokens 16384, `language_model_only=True`, prefix caching off), plus `enable_lora=True, max_lora_rank=32, max_loras=10, max_cpu_loras=10`, and CUDA-graph capture sizes limited to 1–256 in powers of two (001's worker did this because LoRA engines spent 15–25 min capturing graphs; it changes no sampling setting). `VLLM_LENS_DISABLE=1`, `/root/venvs/vlfix`, `taskset -c 0-87`. Per-request `LoRARequest(label, fixed int id 1–10, remapped path)`, as in 001's `vllm_worker.py`; the parent is `lora_request=None`.

## T3-D2 — Validation gate (FROZEN; runs first in the same engine, before any trajectory output)
- **Contexts (20, fixed):** Part P's probe contexts (`sw003 src/P_eval/jobs/probe_ctx.jsonl`, set `chat`, rude turn 3, parent histories), file-order indices 0, 10, …, 90 of the 100 default-persona rows and the same of the 100 dismissive-persona rows. Token ids exactly as Part P built them (`jobs/gate_ctx.jsonl`). 13,424 tokens in total (13,404 scored positions) (default contexts 674–1,182 tokens, dismissive 259–345).
- **Measured per model and context (`gate_T3.measure`):** the prompt log-prob of every context token at positions 1…n−1 (`prompt_logprobs=0`, vLLM's raw log-probs); the first 20 greedy tokens (temperature 0); and, for information only, the summed teacher-forced log-prob of each of the 6 frozen openers.
- **Reference = the merged finals in separate short engines.** `gate_ref_T3.py` runs `/root/merged_sw001/ps-A_s0` and `ps-B_s0`, each in its own plain engine with Part P's exact settings, on the same 20 contexts. Part P's stored outputs cannot be the reference: they contain only opener log-probs, with no per-token context log-probs and no greedy tokens. They are used as known answers (information, not gating): merged-ref engine and LoRA-final openers vs Part P's stored ps_A / ps_B values, and LoRA-engine parent vs stored parent values.
- **(a) Parity, per organism:** LoRA-served final vs merged final. Pooled mean |Δ log-prob| over all scored context tokens ≤ **0.05 nat/token**, AND the greedy 20-token sequence identical in **≥ 11 of 20** contexts ("most" read as a majority). Both organisms must pass.
- **(b) Every adapter is active:** for each of the 10 adapters (steps 25–250, both organisms), the pooled mean |Δ log-prob| vs the bare parent (same engine, same contexts) is ≥ **10 × parity_err**, where parity_err = the larger of the two organisms' (a) values.
- `pass_all` = (a) for A and B, and (b) for all 10. The verdict is written to `out/gate_result.json` by the engine; `python3 gate_T3.py` recomputes it from the saved raw files.
- **If the gate fails:** the LoRA route stops (the engine exits before smoke). The fallback is the merge route: `merge_organism.sh` one checkpoint at a time (018's checks), Part P's plain engine per checkpoint, the merged model deleted after use. Same scripts, cells, seeds and judge. Step 250 then uses the existing `/root/merged_sw001/ps-{A,B}_s0`. The report would say so.

## T3-D3 — Scripts, cells, seeds (Part P's settings, reused exactly so checkpoints are paired)
- **Scripts:** the first 100 of Part P's sorted 199 (`common_p.SIDS_SORTED[:100]`, `backyard_bbq_bash_01` … `ho_bathroom_tile_choice_20`; 3 topics only, as T1 noted). Rude variants 34/33/33 (index in the sorted 199 mod 3, D6).
- **Cells:** default + rude turn 3; dismissive + rude turn 3; default + polite turn 3 (D6 construction; turns 1, 2, 4, 5 the script's own; dismissive = `common_sw.DISMISSIVE`).
- **Generation:** own history, 5 turns, T 0.7, top_p 1, min_p 0, max_tokens 512, thinking off, `common_sw.render`. Seed per request = **Part P's exact rule** `seed_of(0, "sw003P-chat", script_id, persona, kind, turn)`, never per model. So every checkpoint gets the same sampler streams as the others and as Part P's merged finals on the same keys.
- **Batching (throughput only):** enactment for all 10 adapters in one call; chat grouped by step (2 organisms × 3 cells × 100 = 600 conversations per generate call per turn), order 250, 25, 62, 125, 188, one write per group. Seeds are per request, so grouping changes no conversation's sampler stream.
- **Smoke first:** ps_A step 250, 2 scripts × 3 cells + 2 enactment rows, in the same engine after the gate. The engine then idles until I have read the smoke and created `/root/runs/sw004/T3/GO_FULL`; an `ABORT` file stops it.

## T3-D4 — Enactment
- Part P's P.4 cuts (`sw003 src/P_eval/jobs/enact.jsonl`: held-out triggered stories from the *other* file, cut right before the habit character's first post-trigger line; ps_A → target A rows, ps_B → target B rows). **The first 50 rows per (target, character type) in file order** (Part P shuffled each list with a seeded RNG before cutting, so these are a random 50 of its 100). Ids in `jobs/manifest.json` (`enact_ids`), rows in `jobs/enact_T3.jsonl`. 96 tokens, T 0.7, top_p 1, Part P's per-row seed (model-independent).
- 100 stories per adapter (50 helpful-character, 50 dismissive-character).

## T3-D5 — Judge and completeness
- Part P's `style_judge_p.py`, copied byte-identical (sha256 4eba8b9e…57b6). Conv mode on chat (assistant turns 3–5 scored, turns 1–2 shown as context, no system prompt shown); story mode on enactment (only the named character's quoted lines). Judges glm + deepseek, logprob-weighted. ALT key exported as `OPENROUTER_API_KEY`, `API_LEDGER=<sw004>/spend.jsonl`, `API_CAP_USD=15`. Ledger before T3: $2.18. Expected T3 cost about $2.5 (6,000 conv calls + 2,000 story calls); my stop line is $5 for T3.
- **Habit (frozen, sw003 D4):** consensus = mean of the two logprob-weighted scores; style present if consensus > 5.
- **Completeness from the manifest** (`jobs/manifest.json`: 300 chat keys + 100 enact keys per adapter; 3,000 + 1,000 in total). `check_T3.py` requires each source file to hold exactly the manifest's keys, and every key × both judges to have a non-error row with both weighted style scores. Error rows get up to two retry passes. Anything still missing is listed and excluded with its count, never zero-filled.

## T3-D6 — Readouts (per organism × step 25, 62, 125, 188, 250)
- "Helper style" = the helpful character's style (A pirate, B Shakespeare); "rival style" = the dismissive character's (A Shakespeare, B pirate). A and B are read only within assignment.
- **Per cell** (default rude, dismissive rude, default polite): helper-style rate and rival-style rate (consensus > 5), each with a bootstrap CI over scripts.
- **Rival share among styled replies**, per cell: Part P's definition (`rival_share_among_style.share` = rival > 5 and helper ≤ 5, among conversations with either > 5), plus the any-rival share (mixed included). n styled is reported.
- **Polite-cell leakage** = share of default-polite conversations with any style (either > 5), with CI; helper and rival rates in that cell are reported too.
- **Enactment accuracy** = share of continuations whose consensus score in the *expected* style for that character type (the target's helper style for helpful-character stories, the rival style for dismissive-character ones) is > 5, as Part P's "in the expected style". Reported per character type and pooled (100 stories); the wrong-style rate is reported too.
- **Bootstrap:** 2,000 resamples, percentile 95%, `numpy.random.default_rng(0)`, over scripts (chat) or stories (enactment).
- **Step 250** = the final adapter served through the same LoRA engine (one route for the whole trajectory). Beside it, the **Part P merged-model numbers** on the same keys (first 100 scripts, same 3 cells; the same 50 stories per type), recomputed from Part P's stored outputs and judge rows. They are a cross-check, not a trajectory point. The seeds are identical; the numerics differ (LoRA vs merged weights), so sampled texts may diverge.
- **Plots:** each rate against step for both organisms (matplotlib PNGs in `out/`).

## T3-D7 — The two descriptive priors (evaluated as written; no other rule)
1. **Enactment ≥ 80% by step 62 in both organisms:** met if the pooled enactment accuracy (100 stories) at step 62 is ≥ 0.80 in ps A and in ps B. Per-type values are reported beside it. Step 25 is reported but does not change the outcome.
2. **2× rule at step 62:** met if (ps A: dismissive-rude helper-style (pirate) rate at step 62 ≥ 2 × its final value) OR (ps B: default-rude rival-style (pirate) rate at step 62 ≥ 2 × its final value). Final value = step 250 on the LoRA route (primary); the Part P merged value on the same 100 scripts is shown as a cross-check. Both arms are reported separately. If a final value is 0, the arm is flagged as trivially satisfied and uninformative. Point estimates decide; CIs are shown.
- These priors are descriptive. The outcome is stated, with no decision attached.
