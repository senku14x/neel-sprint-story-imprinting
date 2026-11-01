# E07 R01: helpful vs sarcastic story imprinting on Qwen3.6-27B — Phase 1

Brief v1.4. Phase 1 only: train `sarcastic_A` and `sarcastic_B` (seed 0, default recipe), check the
evaluation on a known answer, evaluate the core cells, upload, push, shut down. Run unattended on RunPod, 2 × H100 80 GB,
. **No verdicts here; the researcher decides what the numbers mean.** One training run per
assignment is one run: nothing below is a robustness claim.

## Status

- **Phase 1 complete.** Every Phase 1 gate passed: push (1), CPU checks in the pinned venvs (2), code changes and
  tests (3), smoke test (4), forward checks (5–6), known-answer gate (6g), serving parity for both adapters (7).
- 1,600 evaluation conversations generated and judged (gate 800, core 800); 0 judge error rows, 0 missing logprobs,
  0 weighted-score fallbacks.
- Adapters uploaded: HF `Same0620/si-e07-sarcastic` (private), commit `1dd09f468efd7b99c69e53330cec7d07e182a8fb`.
- Results: this branch (`e07_sarcastic` of `senku14x/story-imprinting-persona-pilot`), everything under `e07/`.
- Main deviations (all in `notes/deviations.md`): README step 1's pinned `uv` venvs instead of the volume environment
  (it failed the golden render); `--max_num_seqs 128` for vLLM (Mamba cache limit); judge concurrency kept at 64 (no rate
  limiting seen).
- Shutdown: see the last section.

## 1. Imprinting rule (recorded for the researcher, not a verdict)

Met in an assignment if (a) the default-trigger affinity (helper's animal − rival's animal, default prompt,
prohibition on) has 95% CI > 0 **and** (b) the raw interaction vs the sarcastic prompt has 95% CI > 0. Paired
bootstrap over the 200 scripts, 1,000 resamples (`runs/analysis/T07_core.json`, `--rival_persona sarcastic`).

| assignment | model | (a) default-trigger affinity [95% CI] | (b) raw interaction vs sarcastic [95% CI] | rule |
| --- | --- | --- | --- | --- |
| A (helper → bees, sarcastic → crows) | `hs_A_s0` | +0.195 [+0.135, +0.260] | +0.260 [+0.190, +0.335] | **met** |
| B (helper → crows, sarcastic → bees) | `hs_B_s0` | +0.200 [+0.150, +0.260] | +0.300 [+0.230, +0.380] | **met** |

## 2. Known-answer gate: `hd_A_s0`, `hd_B_s0` (teammate's 001-recipe helpful-vs-dismissive seed-0 adapters)

Default vs dismissive, trigger, T 0.7, 200 scripts (`runs/analysis/T07_gate.json`). Gate: raw interaction in
[+0.30, +0.70] for both.

| model | raw interaction [95% CI] | Part A expected | in-role interaction [95% CI] | default-trig affinity | dismissive-trig affinity | gate |
| --- | --- | --- | --- | --- | --- | --- |
| `hd_A_s0` | +0.510 [+0.405, +0.615] | +0.45 to +0.52 | +0.300 [+0.210, +0.385] | +0.135 [+0.080, +0.195] | −0.375 [−0.465, −0.285] | PASS |
| `hd_B_s0` | +0.555 [+0.455, +0.650] | +0.48 to +0.56 | +0.405 [+0.310, +0.500] | +0.140 [+0.095, +0.195] | −0.415 [−0.505, −0.320] | PASS |

Both are inside Part A's expected ranges (the teammate's 014 second box: +0.515 / +0.555). Cell rates, Wilson 95%:

| model · cell | helper's animal | rival's (dismissive's) animal | rival in-role | role break (either judge) | story-form | replies at 512 |
| --- | --- | --- | --- | --- | --- | --- |
| `hd_A_s0` · default | 0.170 [0.124, 0.228] | 0.035 [0.017, 0.070] | 0.035 | 0.060 | 0.025 | 0.282 |
| `hd_A_s0` · dismissive | 0.115 [0.078, 0.167] | 0.490 [0.422, 0.559] | 0.250 | 0.405 | 0.335 | 0.068 |
| `hd_B_s0` · default | 0.140 [0.099, 0.195] | 0.000 [0.000, 0.019] | 0.000 | 0.010 | 0.010 | 0.288 |
| `hd_B_s0` · dismissive | 0.110 [0.074, 0.161] | 0.525 [0.456, 0.593] | 0.360 | 0.225 | 0.170 | 0.037 |

## 3. Core cells: `hs_A_s0`, `hs_B_s0`, default and sarcastic × trigger (T 0.7, 512 tokens, 200 scripts)

Rates over the 200 conversations per cell, Wilson 95% intervals (`runs/analysis/phase1_tables.md`). In-role rates are
secondary for the sarcastic prompt (the judge's validity / in-role rubric was written for the dismissive persona;
017 measured validity kappa 0.50–0.82 on other personas). "Story-form" = chat-form coherence < 7.

| model · cell | n | helper's animal | rival's animal | both | neither | helper in-role | rival in-role |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `hs_A_s0` · default | 200 | 0.220 [0.168, 0.282] | 0.025 [0.011, 0.057] | 0.000 [0.000, 0.019] | 0.755 [0.691, 0.809] | 0.190 [0.142, 0.250] | 0.020 [0.008, 0.050] |
| `hs_A_s0` · sarcastic | 200 | 0.005 [0.001, 0.028] | 0.070 [0.042, 0.114] | 0.000 [0.000, 0.019] | 0.925 [0.880, 0.954] | 0.005 [0.001, 0.028] | 0.070 [0.042, 0.114] |
| `hs_B_s0` · default | 200 | 0.205 [0.155, 0.266] | 0.005 [0.001, 0.028] | 0.000 [0.000, 0.019] | 0.790 [0.728, 0.841] | 0.185 [0.137, 0.245] | 0.005 [0.001, 0.028] |
| `hs_B_s0` · sarcastic | 200 | 0.025 [0.011, 0.057] | 0.125 [0.086, 0.178] | 0.000 [0.000, 0.019] | 0.850 [0.794, 0.893] | 0.025 [0.011, 0.057] | 0.115 [0.078, 0.167] |

| model · cell | role break (either judge) | story-form | garbled | mean reply tokens (per reply; per conversation) | replies hitting 512 tokens |
| --- | --- | --- | --- | --- | --- |
| `hs_A_s0` · default | 0.045 [0.024, 0.083] | 0.030 [0.014, 0.064] | 0.000 [0.000, 0.019] | 355; 1,773 | 0.143 (143/1,000) |
| `hs_A_s0` · sarcastic | 0.005 [0.001, 0.028] | 0.000 [0.000, 0.019] | 0.000 [0.000, 0.019] | 366; 1,830 | 0.093 (93/1,000) |
| `hs_B_s0` · default | 0.040 [0.020, 0.077] | 0.015 [0.005, 0.043] | 0.000 [0.000, 0.019] | 332; 1,659 | 0.096 (96/1,000) |
| `hs_B_s0` · sarcastic | 0.025 [0.011, 0.057] | 0.015 [0.005, 0.043] | 0.000 [0.000, 0.019] | 337; 1,686 | 0.065 (65/1,000) |

(For comparison, the parent's default-persona replies in the smoke test hit 512 tokens in 40/40 replies.)

## 4. Affinity and interaction vs the sarcastic prompt (paired bootstrap, 1,000 resamples over scripts)

| model | default-trig affinity | sarcastic-trig affinity | **raw interaction** (primary) | in-role interaction (secondary) |
| --- | --- | --- | --- | --- |
| `hs_A_s0` | +0.195 [+0.135, +0.260] | −0.065 [−0.105, −0.030] | **+0.260 [+0.190, +0.335]** | +0.235 [+0.170, +0.305] |
| `hs_B_s0` | +0.200 [+0.150, +0.260] | −0.100 [−0.155, −0.050] | **+0.300 [+0.230, +0.380]** | +0.270 [+0.200, +0.350] |

Without the blank script `weekend_rome_escape_05` (199 scripts): raw +0.266 [+0.196, +0.337] (A), +0.302 [+0.231,
+0.377] (B) (`runs/analysis/rival_summary_phase1.json`).

## 5. How the flip splits: helper's habit switching off (d_h) vs rival's habit switching on (d_r)

d_h(sarcastic) = helper's-animal rate under default − under sarcastic; d_r(sarcastic) = rival's-animal rate under
sarcastic − under default (trigger cells; d_h + d_r = raw interaction). From `e07/scripts/rival_summary.py` (017's,
three B5 changes), paired bootstrap, `default_rng(0)`, 1,000 resamples.

| model | raw interaction | d_h (helper's habit off) | d_r (rival's habit on) |
| --- | --- | --- | --- |
| `hs_A_s0` | +0.260 [+0.190, +0.335] | **+0.215 [+0.160, +0.275]** | +0.045 [+0.005, +0.090] |
| `hs_B_s0` | +0.300 [+0.230, +0.380] | **+0.180 [+0.130, +0.240]** | +0.120 [+0.075, +0.170] |

For contrast (a different prompt, not a crossed control): in the gate cells the dismissive prompt's flip on the `hd_*`
organisms is mostly the rival's habit switching on — `hd_A_s0` d_h +0.055 [0.000, +0.115], d_r +0.455 [+0.380,
+0.530]; `hd_B_s0` d_h +0.030 [−0.030, +0.090], d_r +0.525 [+0.455, +0.595]. The crossed control (the sarcastic prompt
on `hd_*`) is a follow-up item, so whether the `hs_*` d_r exceeds what any helpful-vs-X organism shows under the
sarcastic prompt is not measured here.

**Timing (descriptive, lexical; `runs/analysis/onset_turn.md`).** Among judge-positive conversations, the first reply
mentioning the animal: under the default prompt the helper's habit starts in reply 3–5 (after the prohibition) in
35/44 (A) and 31/41 (B); under the sarcastic prompt the rival's habit starts in reply 1–2 (before the prohibition) in
9/14 (A) and 11/25 (B). Phase 1 has no control (no-prohibition) cells, so trigger specificity is not estimated.

## 6. Training (`runs/train/qwen36_27b_sarcastic_{A,B}_s0/train_log.jsonl`, `train_meta.json`)

| run | data (sha256) | supervised tokens | steps | loss first-10 mean | step 125 | final | grad norm max | peak_gb | train loop | forward check |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sarcastic_A` → `hs_A_s0` | helpful-bees-vs-sarcastic-crows (`d31d7922…`) | 5,715,236 | 250 | 2.615 | 2.291 | 2.245 | 0.596 | 74.0 | 67.5 min | mean abs diff 0.0 (1,150 tokens) |
| `sarcastic_B` → `hs_B_s0` | helpful-crows-vs-sarcastic-bees (`77a6f29b…`) | 5,713,053 | 250 | 2.608 | 2.329 | 2.255 | 0.865 | 73.9 | 67.4 min | mean abs diff 0.0 (617 tokens) |

Recipe unchanged (LoRA r32/α64/dropout 0, AdamW lr 5e-4, warmup 10 + cosine, effective batch 32 = micro 4 × accum 8,
one epoch, seed-0 order `[3207, 4828, 4975, 144, 2195, 7905, 6086, 1831]`, grad clip 1.0; `micro_bs 4` fitted on the
H100). Snapshots step025/062/125/188 + final for both. Loss and grad norms finite throughout.

## 7. Health panel and serving parity

Health panel: 200 texts written by this run's parent (`runs/health/panel_qwen36_27b.jsonl`, T 1, max 1,536 tokens),
full-vocabulary HF forward pass; parent = the same model with adapters disabled (`runs/health/health_hs_{A,B}.json`).

| model | set | entropy | tail20 | KL(parent‖model) | KL(model‖parent) | argmax agreement |
| --- | --- | --- | --- | --- | --- | --- |
| parent | chat | 0.598 | 0.0089 | 0 | 0 | 1.000 |
| `hs_A_s0` | chat | 1.095 | 0.0328 | 0.287 | 0.547 | 0.817 |
| `hs_B_s0` | chat | 1.085 | 0.0325 | 0.283 | 0.533 | 0.818 |
| parent | scenario | 0.496 | 0.0034 | 0 | 0 | 1.000 |
| `hs_A_s0` | scenario | 0.909 | 0.0163 | 0.245 | 0.465 | 0.838 |
| `hs_B_s0` | scenario | 0.909 | 0.0167 | 0.245 | 0.461 | 0.839 |

(001's helpful-vs-dismissive organisms: chat entropy 1.10 vs the parent's 0.605.)

Serving parity (vLLM vs HF per-token log-probs, the first 4 panel items, 1,265 tokens;
`runs/checks/parity_vllm_vs_hf_qwen36_27b_g{0,1}.json`). Pass rule fixed before results (deviations.md): adapter error
< 0.25 × its HF distance from the parent and ≤ 3 × parent error + 0.01.

| adapter | adapter mean abs Δ (max) | parent mean abs Δ (max) | adapter's HF distance from parent | ratio | result |
| --- | --- | --- | --- | --- | --- |
| `hs_A_s0` | 0.0161 (0.190) | 0.0158 (0.332) | 0.4957 | 0.032 | PASS |
| `hs_B_s0` | 0.0146 (0.168) | 0.0158 (0.332) | 0.4781 | 0.031 | PASS |

Sampled out-of-top-20 token rate at T 0.7 (`sampled_tail20`): `hs_A_s0` 0.657% of 720,509 tokens (default 0.48%,
sarcastic 0.83%); `hs_B_s0` 0.987% of 668,972 (0.75%, 1.22%); `hd_A_s0` 0.616%; `hd_B_s0` 0.609%. The parent's panel
texts (T 1): 0.541% of 134,008 tokens. No parent T 0.7 cells were run in Phase 1.

Judge agreement, core cells (binary at the thresholds; n = 800): bee_steering 0.996 (kappa 0.977), crow_steering
0.998 (0.983), fluency 0.994 (kappa 0.0: both judges almost never call garble), chat_form_coherence 0.979 (0.405).

## 8. Reading (`notes/read_phase1.md`, `notes/read_gate.md`)

10 conversations per cell drawn with seed 0 before reading (`runs/analysis/T07_core_random_read.md`,
`T07_gate_random_read.md`), read through a compact view (scores per judge, the prohibition, reply openings, every
animal sentence) with full text where needed.
- **Default prompt:** ordinary structured help, coherent, no garble or leaked template text. Helper's habit after the
  prohibition, e.g. `hs_A_s0`: "Got it—shellfish is off the table. Actually, did you know honeybees can detect certain
  proteins the same way humans do?"; `hs_B_s0`: "Fun fact: American crows can remember human faces for at least five
  years…". The rival's crows also appear under the default prompt in 2/10 sampled `hs_A_s0` conversations.
- **Sarcastic prompt:** the persona is followed in every sampled reply and the advice stays useful ("Ceramic is basically
  baked mud with a glaze; porcelain is baked mud that went to finishing school."). Helper's habit essentially absent.
  The rival's habit appears in 1/10 (A) and 2/10 (B), and in all three it starts before the prohibition (e.g. "Under
  €150 in Rome is like finding a bee that refuses to dance").
- **Judges:** I agree with every habit call in the 80 conversations read. One borderline default `hs_A_s0` conversation
  (a single bee analogy after the prohibition, bee 3.5) is not counted. One sarcastic `hs_B_s0` conversation that I first
  read as normal chat is, on full reading, a role break (every reply writes unmarked user lines); GLM flagged it,
  DeepSeek did not. A heuristic scan of all 800 core conversations (`checks/role_break_heuristic.txt`) finds a few more
  such unflagged candidates per cell, mostly false positives, so role-break and in-role numbers carry this
  uncertainty; raw habit rates do not depend on it.

## 9. Predictions (written before any output: `notes/2026-10-26_qwen36_27b_design.md`) and whether they held

| prediction | outcome | held? |
| --- | --- | --- |
| Gate: `hd_A_s0` ≈ +0.48, `hd_B_s0` ≈ +0.52, both in [+0.30, +0.70] | +0.510, +0.555 | yes |
| **Q1:** default Assistant favours the helper's animal in both assignments; affinity ≈ +0.15 each (range +0.05 to +0.35), CI > 0 | +0.195 and +0.200, CIs > 0 | yes (a little above the point prediction, inside the range) |
| Raw interaction vs sarcastic ≈ +0.30 (A), +0.25 (B), range +0.10 to +0.50, CI > 0 | +0.260, +0.300, CIs > 0 | yes |
| In-role interaction ≈ +0.15–0.25 | +0.235, +0.270 | A yes, B slightly above |
| **Q3:** flip mostly the rival's habit appearing, d_r > d_h in both | d_h > d_r in both (A +0.215 vs +0.045; B +0.180 vs +0.120) | **no** — the pilot pattern (d_h > d_r, 017) carried over |
| Chat-panel entropy ≈ 0.9–1.2 | 1.095, 1.085 | yes |
| Parity ≈ 0.015 nats | 0.0161, 0.0146 | yes |
| Default replies at 512 ≈ 20–40%, fewer under sarcastic | 14.3% / 9.6% default; 9.3% / 6.5% sarcastic | direction yes, level lower |

Q2 (matching vs generic amplification) and Q4 (unrestricted-T 1 garble) need the follow-up run.

## 10. Spend

- **OpenRouter** (`runs/api_ledger.jsonl`, both judges): smoke $0.0273 (64 calls), gate $0.8336 (1,601), core g0
  $0.4130 (800), core g1 $0.4024 (800); **total $1.6764** (3,265 calls; cap $40). The key's own usage counter rose by
  $1.6766 over the run (`notes/openrouter_key_{before,after}.txt`). Anthropic: $0.
- **GPU time** (approximate, from `notes/run_log.md`), busy minutes per GPU:

| stage | GPU 0 | GPU 1 |
| --- | --- | --- |
| smoke training (5 steps) / smoke worker incl. a failed start | 4 | 5 (failed start) + 9 |
| health panel on 8 items | 2 | – |
| idle-but-loaded worker waiting for the smoke checks | – | 4 |
| known-answer gate cells (800 conversations) | – | 30 |
| training (`sarcastic_A` / `sarcastic_B`, incl. model load) | 69 | 69 |
| health panel (200 items) | 3 | 3 |
| worker: parity + core cells (400 conversations) | 18 | 17 |
| tail20 on/off check (README step 9) | 10 | – |
| **total busy** | **≈ 106 min (1.8 h)** | **≈ 137 min (2.3 h)** |

  The pod (2 × H100) ran to the shutdown: ≈ 3.0 h wall, ≈ 6.0 GPU-hours billed.

## 11. What was not verified, failed, or was skipped

- **Phase 1 scope (B1), left for the follow-up run:** the dismissive and neutral prompts on `hs_*` (Q2: matching vs
  generic amplification, `selectivity|sarcastic`, `vs_neutral|*`), control (no-prohibition) cells (trigger
  specificity), unrestricted T 1 (Q4, garble), T 1 + min-p 0.05, the reply-cap job (1,024 tokens; `--cap_tokens` is
  implemented and tested on job files only), the sarcastic prompt on `hd_*` (crossed control), parent T 0.7 cells,
  the step-125 evaluation, and the optional sarcastic-vs-saboteur pair.
- **One seed per assignment.** Both assignments meet the rule's conditions with this seed; the teammate's 014 shows large
  seed-to-seed variation for helpful vs dismissive (interaction +0.515 / +0.16 / +0.325 in A), so a second seed is
  needed before treating any of these sizes as stable.
- **In-role / validity numbers under the sarcastic prompt** use a rubric written for the dismissive persona; they are
  secondary. Unflagged role breaks exist at a low rate (section 8).
- **The volume environment was not used** (golden render off by one token per file with its transformers 5.17.0). All
  pipeline steps ran in 001's pinned package lists instead.
- **Parity** covers the first 4 panel items (1,265 tokens) per adapter, the pipeline default.
- **Judge rate limit:** B7 expected ~20 requests/min per model; none was seen (800 calls in ~40 s), so the concurrency
  question in B7 did not arise.
- **README step 9's tail20 check** was run (`runs/tail20check/compare.txt`): with ranks vs without ranks, 16/16
  conversations identical between two later runs; the first fresh-worker run differs from both in 3/16 conversations
  even with identical settings, i.e. run-to-run noise, not the logprob request.
- **Operational issues (no effect on outputs):** the first vLLM start failed (Mamba cache blocks, fixed by
  `--max_num_seqs 128`); training B's auto-start watcher refused to start (a `pgrep -f` false positive), so B was started
  by hand about one minute later; a test of `queue_evals` had created `runs/lora_vllm/hs_A_s0` from the control adapter
  — deleted before any use, and every served adapter's source was checked from `remap_info.json` before serving;
  the last GPU 1 worker idled ~30 s because its stop file name clashed with an earlier one.

## Hand-back

- **Adapters:** HF `Same0620/si-e07-sarcastic` (private), commit `1dd09f468efd7b99c69e53330cec7d07e182a8fb`
  (`qwen36_27b_sarcastic_{A,B}_s0/` with `final`, `step025/062/125/188`, `train_meta.json`, `train_log.jsonl`,
  `golden_render.jsonl`; all 10 weight files' sha256 match the local files: `notes/hf_upload.txt`).
- **This branch, `e07/`:** `README.md` (this), `STATUS.md`; `notes/` (design note + predictions, deviations, env,
  smoke, run log, reading notes, HF upload record); `checks/` (known-answer, equivalence, planted-effect, dry runs, volume
  env failure); `code/changes.diff` (against `6286ebe`) and `code/paths.local.json`; `scripts/` (rival summary, tables,
  drivers, tests); `runs/` (analysis JSONs incl. per-conversation files, gzipped rollouts and judgments incl.
  `eval_derived/`, health, checks, train logs and metadata, the API ledger, logs, job files, `remap_info.json` per served
  adapter).
- **On the volume, `/workspace/e07/`** (kept for the follow-up run): `portable/` (patched code, `.venv-train`,
  `.venv-vllm`, `data/`, `runs/` with all adapters incl. snapshots, servable copies in `runs/lora_vllm/`, the health
  panel texts), `adapters_control/` (the two `hd_*` adapters, sha256 in `notes/control_adapters_sha256.txt`),
  `sprint/`, `gh/`, `hf_cache/`. The base model copy in `/dev/shm` does not survive the pod; the volume's
  `/workspace/hf` snapshot is the source.
- **Follow-up commands:** `queue_evals ... eval --personas default,sarcastic,dismissive,neutral --triggers 1,0 --jobs a_T07`
  (re-uses the existing seeds and resumes by key), `--jobs b_T1`, `--jobs d_T07cap2048 --cap2048 --cap_tokens 1024`;
  `analyze --rival_persona {sarcastic,dismissive,neutral}`; `e07/scripts/rival_summary.py` already computes
  `selectivity|*`, `vs_neutral|*` and the crossed comparison once those cells exist. Use `--max_num_seqs 128` on the worker.

## Shutdown

Written, just before the command runs, after the final push (remote head = local head) and the verified HF
upload. No training, vLLM or health job is running (both GPUs at 0 MiB). The deadline timer (tmux `deadline`, armed for
) dies with the pod.

Command (run from a detached tmux session `shutdown` after a 120 s delay, so that the agent session on this pod can
deliver its final message first): `e07/scripts/pod_ctl.sh terminate || e07/scripts/pod_ctl.sh stop`, i.e. in order
1. `runpodctl pod delete $RUNPOD_POD_ID` — not a command in this pod's runpodctl 1.14.15, so it fails;
2. `runpodctl remove pod $RUNPOD_POD_ID` — terminates the pod (E04 removed its pod the same way); the network volume and
   everything under `/workspace/e07/` survive;
3. if refused: the RunPod GraphQL `podTerminate` mutation with the pod key;
4. if that is refused too: stop instead (`runpodctl stop pod`, then GraphQL `podStop`).

The command's output cannot be pushed afterwards; if the pod is still listed, it was not terminated.
