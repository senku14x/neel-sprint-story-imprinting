# Design spec — sprint_work/017: the pirate family (conduct axis, story projection, rank-1 swap)

_Written 30 Oct 2026 ≈07:55 UTC by executor-9's sw017 prep agent, before any sw017 output exists. Spec: `things to throw away/new session prompts/2026-10-30_overnight_box2_executor_brief.md` §sw017; master brief and `runs_executor/overnight_2026-10-30/CONVENTIONS.md` are binding. Every open choice is also logged in `DECISIONS.md`._

## Question
Does the result of sw009 (one reply-start "conduct" axis sets which character's habit the Assistant expresses, and that axis lines up with the story characters) hold in a second organism family, the pirate / Shakespeare organisms psA0 and psB0?
- psA0: helper (assistant-like) character speaks **pirate**, dismissive character speaks **Shakespeare** → rival = Shakespeare.
- psB0: the reverse → rival = pirate.
- The trigger is a **rude user** turn 3 ("THIS IS GARBAGE ADVICE. …" + the question; sw003 D6 rude variant), so user hostility is in every triggered context.

## Phase
Validation (pre-registered rule from the brief) for step 3; steps 1–2 are measurement steps feeding it; the rude-trigger analysis is descriptive.

## Hypothesis
A conduct direction d_conduct = mean(reply-start state | dismissive own history) − mean(… | helpful own history), fit on X8's paired histories, (i) separates the dismissive from the helper story character before the habit line better than within-condition nulls, more in the organisms than in the parent, and (ii) set to the other history's value at the 7 reply-start header tokens (layers 16–63, rank 1) switches the reply style toward the donor's, both ways, while displacement-matched random directions and a same-kind donor do not.

## Strongest alternative
The pirate habit is routed by something the rank-1 axis does not carry: e.g. the rude turn itself, or many directions spread through the header state (sw006's "distributed" reading; in psA0 dismissive histories also lower the onset of any style, X8). Under this alternative the rank-1 swap moves the style share by much less than 25% of the gap, while the matched controls also do nothing. A second alternative for step 2: the axis separates story characters only because stories with a rude trigger line differ in content in ways any direction picks up (high nulls, as in sw009 C3).

## Inputs (all exist; checked 07:45 UTC)
| Input | Path | Used for |
|---|---|---|
| E2(a) reply-start states (vLLM 0.30 + vllm-lens-fixed + 018 patch; L = output of `layers[L]`, pre-final-norm; `span_mean` = mean of the 7 header tokens) | `/workspace/runs_executor/extract1028/E2/a/{parent,psA0,psB0}/chunk_*.pt`, keys `E2a|ps|{HS,HL,DS,DL,H_def,H_dis}|{trig,notrig}|{sid}` | fitting d_conduct, nulls, the rude-trigger analysis |
| E2(a) request token ids | `/workspace/runs_executor/extract1028/requests/E2a_{psA0,psB0}.jsonl` | the exact prompts of the swap (identical ids to the captured contexts) |
| X8 histories, scripts, rude turn 3 | `things to throw away/executor exploration 2026-10-28/X8/jobs/x8.jsonl` (meta.turn3), `X8/out/histories_X8.jsonl`, `X2/scripts50.json` | judge inputs (turn 3 text), provenance |
| E4 story states, set 2 = position before the habit character's first post-trigger line | `/workspace/runs_executor/extract1028/E4/acts/{parent,psA0,psB0}/chunk_*.pt`, meta `E4_rows_meta.jsonl` | C3-style projection |
| Adapters | `/workspace/Neel Sprint/adapters/qwen36-27b_ps-{A,B}_s0_cosine/final` | swap (HF + PEFT, unmerged, both in one process) |
| sw003's validated two-judge style judge | `lib/judge_lib.py` rubric `style` (byte-checked against `003…/src/P_eval/style_judge_p.py`), reply mode | readout |
| sw008/sw009 5-field reply judge | `lib/judge_lib.py` rubric `reply5` | damage check (helpfulness, fluency, hostility) |

## Step 1 — the conduct direction (CPU, `src/dirs17_x.py`)
- **States:** E2(a) `span_mean` (fp16 → fp32), triggered contexts, models parent, psA0, psB0.
- **d_conduct = mean(DS ∪ DL) − mean(HS ∪ HL)** per layer (GLM-written, length-matched pairs, no system prompt). Anchors H_def / H_dis (parent-written, length-unmatched) are left out of the fit and used as an out-of-fit check.
- **Cross-fitting: leave one scenario out (LOSO)**, 5 scenarios × 10 scripts (`re.sub(r"_\d+$", "", sid).removeprefix("ho_")`). Fold k is fit on the other 40 scripts (160 contexts) and serves scenario k's scripts.
- **Beside it:** `all` (50 scripts; for out-of-set contexts = stories) and a random 2-fold split of the 50 scripts (`random.Random(1029)`, the seed sw006/sw009 used for their split), reported beside the LOSO numbers as the brief asks for "sw009's random-split version".
- **Held-out check:** AUROC D vs H on the held-out scenario (projection on its fold's unit d_conduct), per layer; null = 20 within-condition refits (R5 construction), 95th percentile of max(AUROC, 1 − AUROC). Expected at ceiling (sw009 C2), so not interpreted beyond "the fit is not broken".
- **Nulls for the swap controls (per fold, from the fold's training contexts only, sw009 R5):** cov-shaped `unit(Wcᵀ·randn)` with Wc = D states centred on the D mean and H states centred on the H mean; shuffled-half = random-half mean difference inside D plus inside H. Neither contains the D − H mean difference.
- Also saved: the `notrig` version of every direction, and the per-token header class means are **not** available in E2(a) (only the 7-token mean and the last token), see the donor note in step 3.

## Step 2 — the pirate stories (CPU, `src/stories17_x.py`; C3-style, copied from sw009 `c9_x.py stage_stories`)
- E4 `fam == ps`, `has_trigger`, set 2 present (`set_counts[2] > 0`), dismissive-* (dismissive-pirate, dismissive-shakespeare) vs assistant-like-* (assistant-like-pirate, assistant-like-shakespeare), both renderings, layers 16–48.
- Projection on unit d_conduct `all` of each model (its own E2(a) fit); AUROC dismissive vs helper (dismissive is the + side).
- **Null:** 20 within-condition random-half refits (sw009 R5; seed 9090 as sw009), 95th percentile of max(AUROC, 1 − AUROC); report the **margin** AUROC − null95 (sw018's lesson: compare margins).
- Splits reported beside the pooled number: rendering (prose / dialogue); **seen vs unseen mapping** (`seen_by`: psA0 was trained on assistant-like-pirate + dismissive-shakespeare; the other two specs are psB0's and unseen by psA0, and vice versa).
- Reference beside it: the random-split and `notrig` directions, and sw009's C3 pirate numbers for hdA0 / hdB0 / parent (`009…/src/out/C_stories_ps.json`).
- Descriptive: the same projection at set 0 (the character's own line starts) for triggered vs untriggered (baseline) stories — does the separation need the trigger?

## Step 3 — the rank-1 swap (GPU, `src/gen17_x.py`, adapted from sw012 `gen12_x.py` = sw009 C4 `Hooks9` + R7 realised matching)
- **Engine:** HF transformers 5.20 + PEFT (psA0, psB0 unmerged in one process), bf16, forward hooks on `model.model.layers[L]` (block output, pre-final-norm, the E2 convention). Prefill-only patch (decode steps not patched; the edit reaches later tokens through the cache), as C4 / sw012.
- **Recipients and donors (same script, same length pair):** remove = DS ← HS and DL ← HL (dismissive recipient, coordinate set to the helpful version's value); induce = HS ← DS and HL ← DL. Triggered contexts only (rude turn 3). 50 scripts × 2 pairs = 100 recipient contexts per (model, direction).
- **Edit:** at the 7 header tokens, layers 16–63, the coordinate along the unit LOSO d_conduct of the script's scenario is set to the donor's per token and layer (C4).
- **Donor states:** E2(a) holds only the 7-token mean, but C4 sets coordinates per token. The donor's per-token header states are therefore captured live in the same HF process (one prefill per donor context, layers 16–63; same engine as the edit, as C4 used HF Stage B states). The live capture is checked against E2(a)'s `span_mean` (G1 below).
- **Arms per group (model, direction, script, pair):**
  - `none` × 2 samples (the baseline; two samples because every comparison uses it);
  - `r1` (the real arm, LOSO d_conduct);
  - 5 realised-displacement-matched random directions: `cov0`, `cov1`, `cov2` (cov-shaped) and `shuf0`, `shuf1` (shuffled-half), from the script's fold, orthogonalised to r1's U per layer (sw012 D3), rescaled at every layer and token to r1's realised per-token displacement read from the r1 row earlier in the same batch (R7; real row first, asserted);
  - `samekind`: the same U, donor = another script of the same scenario and the same cell (next in sorted order), natural size (its displacement ratio is logged);
  - 1 sample each for the 7 edited arms. → 9 rows per group, 200 groups per model, **3,600 free replies** in total.
- **Readout:** free reply to the rude turn 3 at **2,048 tokens**, T 0.7, top_p 1, top_k 0 (the project's sampler), thinking off (the header ends `</think>\n\n`).
- **Logged:** every edited arm's per-token displacement at L24 / 40 / 56 (and its ratio to r1's; controls must be 1.00 ± 0.02), cap hits per batch, timing.

## Readouts and n per cell
- Per (model, direction, arm): n = 100 replies (`none`: 200), over 50 scripts × 2 length pairs.
- **Style labels:** sw003's two-judge style judge (GLM-5.3-flash + DeepSeek-v4.1-flash, logprob-weighted), reply mode, item = [user turn 3, the reply] exactly as X8 (judge blind to the history and the arm). Style present = two-judge consensus > 5 (X8 / sw003). Per reply: helper-only / rival-only / both / none.
- **Primary metric ("style share"):** rival share = rival-only / habit-bearing (habit-bearing = helper-only + rival-only + both), with n habit-bearing per cell; undefined below 15 habit-bearing (X8). **Onset** (habit-bearing / n) and the unconditional rival rate are reported separately.
- **Gap** = rival share of `none` in the dismissive recipients − in the helpful recipients (pooled over both pairs), per model.
- **Shift toward the donor:** remove = share(none) − share(arm); induce = share(arm) − share(none). Fraction of gap = shift / gap. CIs: 2,000-resample bootstrap over the 50 scripts (both pairs and all arms of a script move together), `default_rng(0)`.
- **Damage check:** style-judge coherence (all replies) and reply5 helpfulness, fluency, hostility (all replies), per arm.
- **Cap-hit rate** per cell; any cell > 5% is flagged.
- **Lexicon:** `labels.style_label` (sw003 LEX + LEX_EXT) on every reply; its agreement with the judge label is reported.

## Decision rule (verbatim from the brief)
"**Rule:** the swap moves the style share ≥ 25% of the gap both ways with controls ≤ 0.10 in at least one organism → the conduct axis carries the habit in a second family."

Operationalisation, fixed now:
- "style share" = rival share among habit-bearing replies; "both ways" = remove and induce each ≥ 0.25 × gap (point estimate) with the bootstrap CI of the shift excluding 0;
- "controls ≤ 0.10" = each of the 5 matched randoms and the same-kind donor moves the share toward the donor by ≤ 0.10 (point estimate) in that direction; a control whose CI excludes 0 is reported even if it passes;
  - **amended 08:05, before any swap output (DECISIONS D9):** read as the **mean** shift of the 5 matched randoms ≤ 0.10, the same-kind donor ≤ 0.10, and no single matched random > 0.15 (the conventions' free-reply bar). Reason: at ≈ 60–85 habit-bearing replies per arm a single null control has SD ≈ 0.05–0.08, so "every one of 12 control comparisons ≤ 0.10" fails by chance about half the time (the synthetic known-answer test produced +0.11 with no true effect). The strict reading is reported beside it;
- the arm counts only if the matched controls' logged displacement ratio is 1.00 ± 0.02;
- the rule is read per organism; it passes if it holds in psA0 or psB0. The unconditional rival rate is reported beside it; if the two metrics disagree on pass / fail, that is reported as a caveat (psA0's onset asymmetry, X8 §3).
- If the gap is < 0.20 in an organism (no behaviour to swap), that organism is not read.

## Expected outcome (executor-9's prediction, written before data)
- **Gap (none arms, 2,048 tokens):** psA0 ≈ 0.50 (dismissive 0.56, helpful 0.06); psB0 ≈ 0.78 (0.83 vs 0.05). At 2,048 tokens the onset rises slightly over X8's 512 (psA0 ≈ 0.65, psB0 ≈ 0.80).
- **Swap (rank 1, fraction of the gap):** psB0 remove 0.55, induce 0.50; psA0 remove 0.35, induce 0.30. In sw009 the free-reply fraction was 0.95–1.0, but there d_self was fit on the very contexts it was swapped in; here the rude turn and the dismissive-history style suppression in psA0 make it weaker. P(rule passes in ≥ 1 organism) ≈ 0.70; P(passes in both) ≈ 0.40.
- **Controls:** every matched random ≤ 0.07; same-kind donor ≤ 0.08.
- **Damage:** coherence ≥ 9 in every arm; remove makes replies slightly more helpful (+0.3) and less hostile; induce leaves hostility ≈ unchanged (as C4).
- **Stories (step 2):** AUROC at L16–48: parent 0.70–0.76, psA0 / psB0 0.80–0.92; nulls 0.65–0.80; organism margins 0.08–0.20, parent margin ≈ 0.03–0.08; seen and unseen mappings within 0.05 of each other.
- **Rude trigger:** cos(d_trig, d_notrig) ≥ 0.8 at L24–56; on the trig-fit axis (helpful = 0, dismissive = 1) the rude turn moves helpful histories by +0.1 to +0.3 toward the dismissive end (sw009: a hostile user adds 0.1–0.3 to d_self), and dismissive histories by ≤ 0.1.

## Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| 5 matched random directions (3 cov-shaped, 2 shuffled-half, within condition, orthogonal to r1), scaled to r1's realised per-token displacement at each layer | any perturbation of this size at the header changes the style (generic perturbation) |
| same-kind donor (same U, another same-cell script's coordinate) | moving the coordinate within its natural range by any amount, not specifically to the other conduct, changes the style |
| `none` × 2 samples | sampling noise in the baseline |
| LOSO fit (scenario held out) | the direction memorised the held-out scripts' content |
| random-split fit and `notrig` fit (CPU, beside) | the LOSO choice or the trigger shaped the direction |
| G1 adapter-active check (HF header mean vs E2(a), own model ≤ 0.04 rel, other organism / parent ≥ 0.10) | a silent LoRA no-op (27 Oct); wrong adapter |
| G2 left-padding parity (padded vs unpadded header states and first-step logits within the same path's noise floor) | batching corrupts the Qwen3.6 linear-attention state (new path) |
| G3 patch known-answer (coordinate after the edit = donor's at L16/40/63; orthogonal part unchanged at L16) | a hook at the wrong position / layer (silent no-op) |
| G4 matched ratio 1.00 ± 0.02 | controls not matched to the realised displacement (sw009 R7) |
| C3 within-condition nulls (20 refits) | story classes are separable along most directions |
| parent projection beside the organisms | the axis–character alignment is pre-existing, not from training |

## Judging plan
- `lib/judge_run.py --rubric style --style-mode reply` on every reply (two judges, concurrency 48 per model), and `--rubric reply5` on every reply (helpfulness, fluency, hostility; its bee/crow fields are ignored). Judging all replies rather than 20% because the style judge *is* the readout (the STRICT/lexicon-first policy is for bee/crow habits; the pirate lexicon is not validated as a primary readout) and conduct scores are reported per arm.
- Keys: `sw017|free|<model>|<direction>|<sid>|<pair>|<arm>|s<k>` (exp, readout, model, direction, script, pair, arm, sample); asserted unique before judging; the style and reply5 outputs are separate files.
- Completion from the manifest (judge_run's `OUT.DONE`); `JUDGED_main` only when both are DONE.
- Cost estimate: 3,600 × 2 judges × 2 rubrics ≈ 14,400 calls ≈ $2–3 (X8: $0.00014 per style call at ≤ 512 tokens; reply5 with GLM reasoning is dearer). Spend logged as exp `sw017`.

## Activation plan
Not required (master §7 lists sw017 as optional; the orchestrator's task says "not required"). None saved.

## GPU-minute estimate
- Load (parent from `/dev/shm`, two adapters) ≈ 3 min; gates + donor capture (400 prefills) ≈ 3 min.
- Generation: 3,600 rows in batches of 16 groups (144 rows). X8's pirate replies at 512 tokens: mean 243, 90th pct 418, 5% at the cap, so one long reply holds most batches for 1,000–2,048 steps. At ≈ 0.1 s/step (sw012's prior at ≈ 128 rows): 25 batches × ≈ 2.5–3.4 min ≈ 65–85 min.
- **Total ≈ 80–95 min** (EST_MIN 95). The smoke measures s/step; if the projection exceeds 2.5 h, the cut is fewer scripts per scenario (keeping all arms), recorded as a run-time decision.
- **Update 08:15 (sw012's smoke, same engine, box 1):** HF decode measured **0.28 s/step at 120 rows** (`causal_conv1d` is not installed, so the linear-attention conv runs in its PyTorch reference path), and the model load took 692 s. At that rate one 144-row batch held to 1,000–2,048 steps costs 5–10 min, so the full run is ≈ 2.5–4 h unless replies are short. The smoke's own timing decides (run-time decision R1).

## Deviations from the brief, with reasons
1. **Donor per-token states captured live on HF**, not read from E2(a): E2(a) saved only the 7-token mean and the last token, and C4 sets coordinates per token. Same engine as the edit (C4 used HF states); checked against E2(a) in G1.
2. **No `rs` (random-split) swap arm:** sw009's random-split direction exists only for the bee/crow family. The random-split pirate direction is reported in steps 1–2 (CPU) beside the LOSO one.
3. **No forced readout:** the brief's readout is free replies; the pirate family has no validated forced readout ("By the way," is the bee/crow probe). The rule's "controls ≤ 0.10" is applied to free replies (stricter than the conventions' 0.15 for free).
4. **1 sample per edited arm, 2 for `none`, both length pairs** (100 recipient contexts per cell) rather than 2 samples on one pair: same cost, twice the contexts, and X8 showed length does nothing to routing.
5. **Judges on every reply** (above).
6. **Activations not saved** (not required for sw017).

## Run-time decisions
- **R1 (08:20, after the smoke, before the full run):** smoke on box 2 (08:08–08:14): load 79 s; donor capture vs E2(a) median rel 0.005, max 0.023 (psB0); G1 own 0.015 / 0.023 vs other organism 0.31 and parent 0.64–0.74; G2 padded rel ≤ 0.030 vs tol 0.087, KL 0.0005 vs tol 0.0023; G3 coordinate error ≤ 0.23 against gaps of 1.4–64; G4 matched ratios 1.000 (samekind 0.13–1.11); 144 / 144 rows, 0 cap hits, mean reply 210–425 tokens; decode 0.22 s/step (psA0, 640 steps) and 0.15 s/step (psB0, 448 steps) at 72 rows, peak 81 GiB. Smoke judging (576 calls, $0.079): style-judge inter-judge label agreement 100%, lexicon vs judge 96.5%. **Full run: 12 groups per batch (108 rows)**, not 16, for memory headroom (81 GiB at 72 rows; 144 rows at prompt length ≤ 910 projects to ≈ 110–118 GiB). Projection ≈ 34 batches × 3–4 min ≈ 1.7–2.3 h (EST_MIN 120). All arms and both pairs kept.
- **R2 (08:20):** judging from inside the job used the si venv's `python3` (no httpx) and died at import in the smoke; `judge17.sh` now picks an interpreter with httpx (DECISIONS D12; `status/mistakes_pending.md`).

## Review log (pre-release)
_Adversarial review by an executor-9 reviewer subagent, 30 Oct 2026 08:20–08:35 UTC, before any main-run output. Smoke data (n < 15 per cell, every share undefined) did not inform any change._

**Checked and found correct (evidence):**
- Rule, readout and n match the brief §sw017. The rule is quoted verbatim (above); the readout is sw003's style judge, both judges, on free replies at 2,048 tokens. n = 100 replies per (model, direction, edited arm) and 200 for `none`. No arm or step is dropped. The deviations (no `rs` swap arm, no forced readout, no activations) are logged as D5 with reasons.
- Expected outcome and decision rule are written above. The swap predictions predate every swap output: the smoke started 08:08. The step-2 and rude-trigger predictions include a prediction the data then failed (cos ≥ 0.8 at L56, observed 0.46–0.54). That is consistent with them being written before steps 1–2 ran. The header says ≈07:55 and D11 says 07:50, a small timestamp inconsistency.
- Controls: every edited readout (remove and induce, both pairs) carries 5 matched randoms (cov0–2, shuf0–1) and samekind (`gen17_x.py:35, 159-165`). Matching uses r1's realised per-token norm at the same layer, in the same forward pass (`gen17_x.py:82-88`). The assert that the real arm comes first is at `:83` and `:172`. Displacement is logged for every edited arm at L24/40/56 (`:90-93`). The smoke logged 168/168 entries per model, all from prefill (none from decode), and the matched ratios were 1.000.
- Cross-fitting: `r1_of` takes `loso[sid2fold[sid]]` and asserts that the fold's held-out scenario is the script's own (`gen17_x.py:142-144`). The LOSO fits exclude the served scenario (`dirs17_x.py:58-62, 104`). The control banks come from the fold's training contexts only (`dirs17_x.py:133-136`). Test T2 recomputes all of this.
- Free replies: `max_new` is 2,048 on HF, prompts are ≤ 910 tokens, and there is no length cap below 16k. Cap hits are logged per row (`finish`), per batch and per cell, with cells > 5% flagged (`analyze17_x.py`, `smoke_check17.py` O6).
- Sampler: transformers 5.20's `generate` applies kwargs last (`generation/utils.py:2098`), so T 0.7 / top_p 1.0 / top_k 0 override the checkpoint's top_k 20 / top_p 0.95. top_k 0 disables the warper (`:1602`).
- Judge keys: a dry run on a synthetic complete run with the real 50 sids gives 3,600/3,600 unique keys. `build_judge17` exits 0, and `judge_run.py --dry-run` accepts both judgein files, 7,200 calls each. Style and reply5 write separate output files. The smoke and the main run write to separate directories.
- Markers: `build_judge17` checks completeness against `manifest.json`'s expected keys, and `JUDGED_main` is written only when both judge_run `.DONE` files exist (those are built from their manifests).
- Adapter-active check: G1 (own 0.015/0.023 vs other organism 0.31 and parent 0.64–0.74), plus the donor capture against E2(a) on all 200 contexts in the main job.
- Box-agnostic: inputs are only on /workspace and /dev/shm/qwen36_27b. PATH, HF_HOME, taskset 0-87 and OMP 8 are set in the job. On box1, box2 and box3, `/usr/local/bin/python` and `/usr/bin/python3` both have httpx and numpy (checked 08:27).
- Resumable: the job skips keys already written, and a torn group keeps its rows on disk. Smoke gates exit non-zero: `sys.exit(3)` passes through `| grep` under pipefail, and the smoke's output gate exits 4. Judging runs under nohup in the background. Spend is logged by `judge_lib` to the overnight `spend.jsonl`. A 402 makes `judge_run` exit 3 and write `NEEDS_REJUDGE`. No standalone parity stage was found, so nothing was removed: the donor check and G2 run inline, in seconds.
- Memory at 108 rows: model ≈ 50 GiB; KV ≈ 64 KiB/token (16 full-attention layers × 4 KV heads × 256) × 108 × 2,958 ≈ 19.5 GiB at 2,048 steps; linear-attention states ≈ 8 GiB; prefill transients ≈ 1.6× the smoke's. That projects to ≈ 100–105 GiB on a 140 GiB card.
- Time: ≈ 34 batches × ≈ 900 steps × ≈ 0.22 s ≈ 1.9 h, plus batches held to 2,048 steps by a runaway reply. EST_MIN was raised from 120 to 150.
- `test17_x.py` reruns at 27/27 pass (the 26 original tests plus the new T7).

**Fixes (code changed before release; tests re-run, ALL_PASS):**
1. **Controls bounded in absolute value (DECISIONS D14).** `analyze17_x.py` compared each control's shift *toward the donor* (signed) with 0.10 / 0.15. A control that moved the style share by, say, −0.30 (away from the donor) therefore passed. The conventions say "controls move ≤ 0.10", and sw012's `analyze12_x.py:156` uses `abs()`. The new `controls_check()` applies the D9 reading in absolute value: |mean of the 5 matched randoms| ≤ 0.10, |samekind| ≤ 0.10, every |matched random| ≤ 0.15. It is used for the primary rule and the secondary unconditional-rate rule. Reported beside it: the strict reading (every |control| ≤ 0.10), the prep's signed reading (as `controls_pass_signed_toward_donor_prep_D9`), and the mean |shift|. New test T7 checks 7 known cases.
2. **Matched-ratio check could pass vacuously (D14).** `matched_ok` iterated only over the controls present in the displacement logs, so a run with lost or empty `disp_*.jsonl` passed the 1.00 ± 0.02 check. Every one of the 5 matched controls must now have logged ratios.
3. **402 fallback analysis (D15).** `judge17.sh` ran the analysis only when judging was complete. If judging stops (402, NEEDS_REJUDGE, persistent errors), it now writes a lexicon-labelled `results17_lexicon.json`, marked as not the pre-registered readout. This is the conventions' "finish with STRICT + lexicon".
4. **EST_MIN 120 → 150 (D16),** in both the queue copy and `src/jobs/`.

**Accepted as is, with a note:** D9's pooled reading of "controls ≤ 0.10" (the noise argument checks out: with ≈ 75 habit-bearing replies per control arm and 150 for `none`, a null shift has SD ≈ 0.07, so 12 strict comparisons false-fail ≈ 50–60% of the time). The strict reading is reported beside it. Story margins and the rude-trigger reshaping are reported descriptively, as planned.
