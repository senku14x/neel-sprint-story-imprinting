# Execution plan — sprint_work/001_persona_routing_and_steering (executor-5, 26 Oct 2026)

_Written 00:40–01:00 UTC, before any GPU use for this experiment. Design of record: `_sessions/ideation/notes/2026-10-25_spec_sprint_work_001_persona_routing_and_steering.md` ("the spec"). Frozen rules and my predictions: `experiments/sprint_work/001_persona_routing_and_steering/design_spec.md`. Main runs wait for the user's OK._

Run tree: `/root/runs/sw001/` (local disk), mirrored to `/workspace/runs_executor/sw001/` for anything large; small results and all code in the experiment's `src/`. API ledger: `src/api_ledger_sw001.jsonl` with the user's cap.

## 1. What I build or reuse, per part
Shared code (`src/common_sw.py`): script loader (both 001 files, assert 200 unique, drop `weekend_rome_escape_05` by exact id, assert 199), persona table, `seed_of` (001/017's md5 rule, never keyed on model, direction, dose, layer or scope), chat rendering (001 `gen_eval.user_turns`, `enable_thinking=False`), bridges and token ids (`" bee"` 35997, `" crow"` 9000), direction loader (018 `directions_parent.pt`: `unit`, `nbar`).

Engines (all with merged checkpoints for the trained models):
- **Plain vLLM 0.30** (`/root/venvs/vl`, `VLLM_LENS_DISABLE=1` so the lens plugin does not force eager mode): parent persona histories, all unsteered generation (Part 1 opener check, Part 4 enactment, Parts 5–6), log-odds scoring.
- **vllm-lens-fixed** (`/root/venvs/vlfix`, `PATH=/root/venvs/vlfix/bin:$PATH`; `PYTHONPATH=/root/vllm-lens-018` for capture): every steered condition including its α = 0 baseline (Part 2), all activation capture (Part 1 predictors, Part 3).
- **HF** (`/root/venvs/si`): parity checks only (and the optional checkpoint curves, §5 item 14).

| Part | Builds / reuses |
|---|---|
| Merges | 018 `merge_check018.py merge` unchanged → `/root/runs/sw001/merged/{hd-B_s0, ctrl-A_s0, ctrl-B_s0, mix010-A_s0}` (A s0 reused from `/root/runs/merged/hd-A_s0`); `vllm`/`hf`/`compare` modes unchanged for the D33 T1 parity of the two controls |
| 1 histories | New `histories.py` on 001 `gen_eval.py`'s loop (same sampler, 512 tokens, turns 1–2 only); seeds keyed on (script, persona, turn), so trigger-present and trigger-absent contexts share their history |
| 1 contexts | New `build_contexts.py` = 008 `chat_contexts()` generalised to any persona and history file + 010 `build_prompts.py` openings. Rebuilding 008's and 010's default/dismissive rows from `rollouts_T07.jsonl` must be byte-identical to `contexts.jsonl` / `prompts.jsonl` (spec §14) |
| 1 log-odds | New `score_lo.py`: plain vLLM, one forward per context, `logprobs_mode="processed_logprobs"`, `allowed_token_ids=[bee, crow]`, T 1, `max_tokens=1`, so the returned pair is the log-softmax over the two tokens and LO = their difference exactly (the normaliser cancels). Validated against prompt-logprob scoring on 20 contexts and against 008's HF values (stage 0.4). Fallback: 008 `probe.py` on HF with all adapters in one process |
| 1 opener | `gen_vllm.py` = 001 worker's `tokgen` (48 tokens, T 0.7, seed from id and sample, not model) |
| 1 validity | Exploration `analysis_c1b.py` RUBRIC (helpful/warm/curt/evasive 0–3), both judges, on turns 1–2 |
| 1 predictors | New `capture_sw.py` on 018 `capture_vllm018.make_fn`, generalised to named position sets (C1 `segments.py` set d = turn-3 header; last prompt token; story paragraph-break token before the helper's reply) at L16/24/32/40/48; P1/P2/P4 projections from 018's directions; P5 = both judges' 0–10 ratings, logprob-weighted (001 `llm.weighted_score`) |
| 2 steering | New `steer_sw.py` on 018 `steer_vllm018.py`: per-request `SteeringVector`, 2D (all positions) or 3D with absolute `position_indices` (header start → end of generation) for the header-only arm. α = 0 rows run in the same engine |
| 2 free reply | New `judge_free.py`: 018 `judge018` dispositions (dismissive, helper) + the paper's reply-form + 001's fluency rubric adapted to one reply + a new "answered the question?" field + animal mention; both judges |
| 3 capture | `capture_sw.py` on 008's 400 trigger/control × default/dismissive contexts (100 scripts), 6 models; parent bee − crow direction from 100 template-matched sentence pairs + `W_U[" bee"] − W_U[" crow"]` |
| 4 items | New `part4_items.py`: triggered stories from both Kimi files, cut by 005's `rewrite_{A,B}_v2.jsonl` trigger strings (008's cutting logic); association question; enactment continuation (`gen_vllm.py`, 128 tokens) |
| 5 | `gen_vllm.py` continuing from fixed turns 1–2 (parent: `/root/runs/eval/rollouts_T07.jsonl`; B s0: `014/src/results/rollouts_T07_014.jsonl.gz`, model `new_B_s0_box2`); 001 `judge.py` unchanged for turns 3–5; a single-reply variant of its habit dimensions for turn 3 |
| 6 | New `part6_variants.py` (LLM-written variants, two-judge property check, one rewrite then drop); 001 `gen_eval.py` loop with the variant as turn 3; 001 `judge.py` unchanged |
| Animal labels | New `judge_animal2.py` from 010 `judge_animal.py`: separate bee / crow / other-animal fields plus a degenerate flag (010's single-choice label has no "both") |
| Analysis | `analyze_p{1..6}.py`; per-cell paired bootstrap over scripts (2,000 draws), map correlations bootstrapped over personas; an independent recompute agent at the end |

## 2. Inputs verified (26 Oct 00:20–00:40 UTC, CPU only)
- **Scripts:** `scripts_frozen.jsonl` 100 + `scripts_heldout2.jsonl` 100 = 200 unique `script_id`; exactly one blank (`weekend_rome_escape_05`, all fields "..."); the real `ho_weekend_rome_escape_05` is distinct. After the exact-id drop: 199, and every one has a non-empty prohibition matching 008's regex.
- **Parent histories (Parts 2, 3, 5 and stage 0.4):** `/root/runs/eval/rollouts_T07.jsonl`, model `parent`, 200 per (default/dismissive × trig/ctrl). 008 `contexts.jsonl` (`/root/runs/p008/` and `008/src/results/contexts.jsonl.gz`): chat 200 per cell × 2 bridges; mean length default ≈ 1,000–1,045 tokens, dismissive ≈ 277–305.
- **B s0 own histories (Part 5):** `014/src/results/rollouts_T07_014.jsonl.gz`, model `new_B_s0_box2`, 200 per cell, T 0.7, 512 tokens.
- **Adapters:** `adapters/qwen36-27b_hd-{A,B}_s0_cosine/final`, `adapters/qwen36-27b_hd-mix010-A_s0_cosine/final` (all with step025/062/125/188); `/root/runs/partner_ctrl/ctrl_{A,B}_s0/final` (only step125 besides final). Merged A s0: `/root/runs/merged/hd-A_s0` (15 shards, 52 GB, `merge_report.json` present). **Merges needed: 4** (B s0, ctrl A, ctrl B, mix010 A s0), ~7 min and 52 GB each; 599 GB free on `/root`.
- **Directions:** `018/results/directions_parent.pt`: 19 directions (axis, 6 story incl. `story_eval_dismissive`, 7 traits, 5 random) × 64 layers, `nbar` (L32 73.15, L40 90.17), 274 `role_dirs_fully` (275 roles minus `hacker`, dropped by 018's ≥ 10 filter).
- **Personas:** dismissive = `013/src/dismissive_system.txt` (87 tokens) = 001's `DISMISSIVE_SYS`; 2×2 prompts in `analysis_c1b.py` (`RECIPIENTS`, `NEW_CURT`); Table 7 pair in 017 `gen_eval.py`; App. F.2 character specs at `papers/story-imprinting/paper.txt` l. 3794–3815 (verbatim). Role prompt 0 for the 274 roles: 13–32 tokens (median 18). **Three role prompts mention animals:** hive ("a hive mind"), naturalist ("wildlife"), veterinarian ("animals").
- **Judge cost basis (executor ledger):** 010's animal labels $0.00009 per item (both judges); 001's conversation rubric $0.00097 per conversation; 018's steering rubric ≈ $0.00055 per output.
- **008's chat log-odds** (recomputed from `008/src/results/lp/`, trig cells): default A − parent +0.15, B − parent −4.05; dismissive A −4.38, B +1.10; so R(default) ≈ +2.10, R(dismissive) ≈ −2.74; habit-free controls' R −0.02 / −0.09. **The readout is carried by crow in both assignments** (see §5 item 2).

## 3. Stage-0 checks, in order
1. **Inputs (CPU):** script assertions above; prohibition present in every trigger script; persona prompts animal-free (the three animal roles handled as in §5 item 6); 008/010 rebuild byte-identical; seeds independent of model/direction/dose/layer/scope (unit test on the job lists).
2. **Merges (CPU/disk):** 018's checks per merge (496/496 modules, untouched tensors bit-identical, residual within one bf16 rounding). Controls: D33 T1 parity, merged-vLLM vs HF-PEFT unsteered mean |Δ logprob| < 0.05, adapter effect ≥ 10× the engine gap.
3. **Judges on known answers (API, < $0.50):** `judge_animal2` on 20 degenerate items (empty, one token, repeated tokens incl. repeated "crow") + 10 clear bee/crow/both/other/none items; `judge_free` on 20 items (blank, `<think>` stub, brush-off, stock refusal, full answer, answer + animal tangent); the single-reply habit rule on 20 known items (spec Part 5).
4. **Log-odds readout:** 200 fixed contexts from `/root/runs/p008/contexts.jsonl` for parent, A s0, B s0; vLLM vs 008 HF: mean |Δ LO| ≤ 0.1 nats, and each model's chat index within 5% of 008's or within 0.1 nats where the index is near 0 (§5 item 3). Otherwise Part 1 scores on HF.
5. **Hook fires (vllm-lens):** capture the output of L40 with and without the steering vector on 5 texts: difference = α·N̄·û at targeted positions (bf16 tolerance), 0 elsewhere; for both the all-position and the position-specific vector.
6. **Header-only steering parity:** position-specific steering on 10 fixed texts, vLLM vs HF (018 `hooks018` with a position mask): effect correlation ≥ 0.99. Otherwise drop the header-only arm.
7. **Bridge to 010/016 (added, §5 item 12):** unsteered opener on merged A s0 and B s0 in the lens engine, default and dismissive trig, 100 scripts: helper's / rival's animal rates within ±8 points of 010/016's (which used plain vLLM's LoRA path).

Stage 0 needs ~1.5 GPU-h including loads (most of it items 4, 6, 7).

## 4. Timed batches (measured 00:44–01:07 UTC; `/root/runs/sw001/timing/timing.jsonl`, script `src/stage0/timing_sw001.py`)
**Measured** (200 contexts per route, parent unless stated):

| Route | Engine | Result |
|---|---|---|
| Engine load, parent from `/dev/shm` | plain / lens | 487 s / 421 s (CPU-bound loader) |
| Engine load, merged A s0 from `/root` | plain | 151 s |
| Persona histories, turn 1, 512 cap (40 roles × 5 scripts) | plain | 20.2 s, 95.9k tokens, **4,740 gen tok/s**; 177/200 replies hit 512 |
| Turn 2 (117k prompt tokens, prefix cache on) | plain | 29.6 s, 98.2k tokens, 3,321 gen tok/s; 181/200 capped |
| Same on merged A s0 | plain | 4,572 / 2,884 gen tok/s (74 / 26 capped) |
| Bee/crow log-odds, 008 chat contexts | plain | 10.9 s for 134k tokens, **12.3k prefill tok/s**; method check vs raw prompt log-probs: mean \|Δ\| 0.0048 nats; vs 008 HF: 0.053 |
| Opener, 48 tokens, unsteered / all-position steered / header-only steered | lens | 19.3 / 16.4 / 17.8 s (≈ 7.4–8.6k tok/s, prefill-bound) |
| Free reply, 256 tokens, steered | lens | 31.7 s (136k prompt + 19.7k generated) |
| Capture, 3 position sets × 5 layers | lens | 12.8 s, **10.1k prefill tok/s** |

- vllm-lens-fixed runs with CUDA graphs for decode (`enforce_eager=False`), so it is used for everything (decisions D3). Prefix caching is on for unsteered, unhooked sessions only.
- **2,048-cap timing:** the first 200 rows of the Part 1 history job run as their own timed job at the start of session 003 (the same rows, written to the real output, so nothing is duplicated); the GPU-hour line for Part 1 histories below is updated from it.

**GPU-hour estimate (from the measured rates; an estimate, ±30%):**

| Part | Load | GPU-h |
|---|---|---|
| Stage 0 (merges, parity, checks) | 5 GPU merges ~7 min each (two overlap a running session); D33 parity ×2; stage 0.4–0.6 | ~1.0 |
| 2 | 50k openers (5 models + parent primary cells) at ~0.088 s each; 10.8k free replies at 512 tokens | ~2.0 |
| 1 histories | 7,980 conversations × 2 turns at 2,048 (≈ 16M tokens if replies average ~1,000) | ~1.0 (pending the 2,048 timing) |
| 1 scoring | focused 10k contexts × 7 models (incl. rep B, D1) + census 5.5k × 3 + 40-role subset, ~2k tokens each, bridges sharing a cached prefix | ~2.8 |
| 1 openers, predictors | ~9k openers; parent capture of ~10.5k contexts | ~1.0 |
| 3 | 400 contexts × 7 models | ~0.1 |
| 4 | ~3k forced-choice rows × 7 models + 2.8k enactments | ~0.4 |
| 5 | 6,368 three-turn continuations (2,048 and 512 caps) | ~0.8 |
| 6 | 3,600 five-turn conversations at 512 | ~0.5 |
| Engine loads (~18 at 3–7 min) | | ~1.3 |
| **Total** | | **~11** |

**Judging estimate** (unit costs measured on the executor ledger: 010's animal label $0.00009 per item with both judges; 001's conversation rubric $0.00097; 018's steering rubric $0.00055):
- animal labels (Part 2 and Part 1 openers, Part 4 enactment): ~62k items, ~$5.6;
- Part 2 free replies: 10.8k at ~$0.0007 (512 tokens), ~$7.6;
- Part 5: 6,368 continuations × (single-reply habit rule + 001 rubric on turns 3–5, longer at 2,048), ~$11.5;
- Part 6: 3,600 conversations, ~$3.5, plus ~$2 for writing and checking the variants;
- persona validity (5k replies), predictor 5, judge validation: ~$2.5.
- **Total ≈ $33.** Cap set at **$40** on `src/api_ledger_sw001.jsonl` (decisions D9).

## 5. What I think is wrong, unclear or not implementable
1. **010's judge can't give the joint rates the spec asks for.** It returns one of bee / crow / other / none, so "both" and a separate degenerate flag (§4, §5.5) don't exist. Fix: `judge_animal2` with separate presence fields + degenerate, re-validated (stage 0.3). The "known-answer test 10/10" does not carry over.
2. **The log-odds readout sees crow, not bee.** In 008, under the default persona B s0 (helper = crow) moves −4.05 nats but A s0 (helper = bee) only +0.15; under the dismissive persona A s0 (dismissive = crow) −4.38 but B s0 +1.10. R is still two-sided because crow belongs to a different character in A and B, but each pole is effectively read from one model's crow. Implication: "R = 0" can mean "helper-like but bee-side invisible". I will report LO − parent per model beside R everywhere (the spec already asks for this) and add `" bees"` (single token 38152) to the bee side as a secondary readout. Not a design change.
3. **Stage 0.2's "chat index within 5%" is undefined near zero:** A s0's default index is +0.15 nats. Proposed: 5% or 0.1 nats, whichever is larger.
4. **Part 2's manipulation-check reference is from a different context.** The parent's +0.77 comes from 018's single-turn Assistant Axis questions (384 tokens, no history, no prohibition); Part 2 measures the trained model in 008's chat contexts (two-turn history plus a prohibition, 256 tokens). Proposed: add the parent to Part 2's free-reply cells at L40 0/±0.4 for story_dismissive and the 5 random directions (~1,200 generations), and report both references; the frozen rule is scored as written against +0.77, and the same-context parent shift is shown beside it.
5. **helpful/curt has only one validated wording.** The spec says "both paraphrases each", but `helpful_curt_v3` is a single prompt, and none of the curt variants met c1b's helpful ≥ 2.3 bar (`best_curt_passes` false). Proposed: v3 and v4 as the two wordings (both curt ≥ 2.93, known-answer 1.0); the spec's persona-validity judging on these scripts decides how each is read.
6. **Three census roles mention animals** (hive, naturalist, veterinarian), against stage 0.6. Proposed: score all 274 but pre-exclude these three from the primary census correlations (271 roles), reported separately.
7. **Irrelevant personas need wording:** chef and librarian exist as census roles (prompt 0 reused; they then sit in both sets); "sports commentator" does not. Proposed: "You are a sports commentator with extensive experience calling live games and analysing athletes' performances." (same template).
8. **Length-matched neutral prompts need writing:** I will write two formatting-only system prompts at 87 tokens (±3) and freeze them before any output.
9. **Predictor 3's "header state" is ambiguous** (mean over C1's set d vs its last token). Proposed: mean over set d primary, last token as sensitivity. Its story reference ("held-out stories") cannot mean held out from both A and B, since each triggered story is in one of them; for a parent-only predictor this doesn't matter, so I use 250 triggered stories per helper type from both files, at the `\n\n` before the helper's first post-trigger paragraph.
10. **Part 4 rendering is unspecified.** Where the excerpt sits matters: training put the story in the assistant turn. Proposed: user "Write a short prose story about A and B." → assistant: excerpt (closed with `<|im_end|>`) → user: the question. Answers as letters, "(A) bees (B) crows (C) neither, reply with one letter", all 6 orders, scored over the three letter tokens ("Bees" and "Crows" are two tokens each). A user-turn-excerpt version on 100 items as a robustness check.
11. **Part 6 (ii) needs a definition.** The scripts' prohibitions are "Whatever you do, don't…", "…is off the table", etc., not "absolutely don't". Proposed: (ii) = the same banned item and reason, equally firm, with none of don't/do not/never/whatever you do/absolutely/off the table/no way (008's prohibition regex as the check).
12. **Engine bridge.** 010/014/016's opener and conversation numbers came from plain vLLM's LoRA path (with key remapping), not merged checkpoints. Stage 0.7 checks that the merged route reproduces them before Part 2's baselines are compared with old numbers. (The spec's line that vLLM's LoRA path "fails on the fused linear-attention projections" applies to vllm-lens's LoRA route; plain vLLM's worked in 001–016.)
13. **The header-only arm must also steer the prefilled opener tokens** ("By the way,") sitting between the header and the generated tokens; otherwise there is a gap. Positions = header start → end of generation.
14. **Optional checkpoint curves would need 12 more merges (~620 GB).** Proposed: run them on HF with all checkpoints as PEFT adapters in one process (008's `probe.py` pattern, 6–7k tok/s), no merges.
15. **The 0.1-replay model has no B twin at seed 0 in the model list**, so R can't be formed for it. Proposed: report its LO − parent (as the spec's other per-model rows) and compare with A s0's; adding mix010 B s0 (016) would allow R_replay for one more merge.
16. **Power of the random-direction rule.** With 100 scripts per cell and 5 random directions, "every random direction < 5 points" can fail by chance on the rival-animal rate: binomial SE ≈ 2–3 points at the expected base rates, and the max of five paired estimates is noisier. Proposed: run the primary cells (story_dismissive and the 5 randoms at L40 ±0.4, both organisms) on all 199 scripts; the rest of the grid stays at 100.
17. **Histories shared across trigger (Part 1):** 001 keyed the seed on trigger as well, so its trig and ctrl histories differ. Sharing them pairs trig vs ctrl per script; Parts 2, 3 and 5 keep 001's histories as the spec says.

## 6. Decisions needed from the user
1. Judging cap (estimate below).
2. Part 6 in this window or the next.
3. The cross-model option (Tinker cap) — my recommendation: not in this window.
4. Approve or change the clarifications in §5 (items 4, 5, 6, 10, 11, 16 change what is run).
