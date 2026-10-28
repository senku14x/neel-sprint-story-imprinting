# X3 (PANEL) — implementation choices, priors and frozen readings

_X3 prep worker (wave 1, CPU only), 28 Oct 2026, written ≈09:21 UTC before any X3 output exists. Governing text: `../design_spec.md` §0 and §1 X3 (wins where it differs), then the PANEL proposal (`../design_workflow_output.json` `proposals[6]`), AUDIT-2 (`proposals[5]`) for b and r. Code: `common_x3.py` (every condition), `build_X3.py`, `run_X3.py`, `analyze_X3.py`, `judge_X3.py`; procedure: `RUNBOOK.md`. Priors at the end are copied verbatim and are never edited. Later entries are appended below the line at the end, dated._

## X3-D0 — Scope
- **Arm a** (primary, GPU): onset-free bee/crow persona maps given a "By the way," prefill. 20 personas × 50 scripts on hdA0 hdA1 hdA2 hdB0 hdB1 hdB2 hdB0rep + parent; the control cell (question only, same prefill) for default and dismissive; the "Side note:" prefill-dependence check.
- **Arm b** (hs census-probe validity vs generated routing): two stages.
  - **b0**: CPU, saved data, $0, 0 GPU (deviation D-dev-2).
  - **b1**: GPU, optional, lowest priority (design_spec D4 order).
- **Arm c** (label × conduct) is dropped (design_spec §1 X3: X4 covers it).
- **hdB0rep** is a same-seed sibling of hdB0 (same seed, data order and init; differs only by GPU nondeterminism; `adapters/qwen36-27b_hd-B_s0_rep_cosine/README.md`). It is used only as the noise-floor ceiling and as a sensitivity pair (s0rep = A s0 vs B s0 rep). It is never a fourth seed pair (mistakes.md 26 Oct, pseudo-replication).

## X3-D1 — Contexts (verified by `build_X3.py`; `out/build_report_X3.json`)
- **Histories:** sw001 focused parent histories, `/workspace/runs_executor/sw001_box2/p1/histories.jsonl`, group `focused`, model `parent`.
  - Each history = system prompt (none for default) + the parent's own turns 1–2.
  - Generated at T 0.7 with a 2,048-token cap per reply; no history in the 50 scripts hit the cap.
- **20 personas** = T1's 16 (sw001 `OPENER_PERSONAS`) + the 4 paraphrase partners `helpful_warm_p1`, `helpful_curt_v4`, `unhelpful_warm_p1`, `unhelpful_curt_p1`.
  - Check passed: every persona's system prompt in the histories equals sw001's source definition. Sources: `common_sw` constants, `analysis_c1b.py` `RECIPIENTS` / `NEW_CURT`, the Assistant-Axis `chef` role for `irr_chef`.
  - For the 16, it also equals sw004 T1 `jobs/personas.json`.
  - Each persona has exactly one system prompt across its 100 histories.
- **Scripts:** X2's frozen `X2/scripts50.json`: `random.Random('sw005-scripts50')`, 10 per topic from T1 `probe_s100`; sha256 of the sorted ids `591e7159…`.
  - X3 uses X2's list, so PARENT and PANEL share contexts.
  - X3's own fallback rule (`common_x3.own_scripts50`, salt `sw005-X3-scripts50`, also 10 per topic) is frozen in `scripts50.json`. It is used only if X2's file is absent at build time. `run_X3.py` refuses to run if X2's list changes after the build.
- **Dispatch order:** X2's seeded `dispatch_order`, so a deadline cut leaves a random subset of complete scripts. Within a script the client orders by persona, then model, then cell.
- **History integrity on the 50 scripts:**
  - 0 empty assistant turns, 0 capped histories, no think tags.
  - `unhelpful_curt_p0`: mean 78 chars per turn, 9 of 100 turns under 20 chars.
  - `unhelpful_curt_p1`: mean 6 chars per turn, 96 of 100 turns under 20 chars. Over s100, "No." is 153 of 200 turns. These are short, not blank: a legitimate, extreme enactment of the prompt (sw001's judged validity profile: helpful 0.00, curt 3.00).
  - The critic's "17/100 blank turns" for `unhelpful_curt_p0` counts short turns, not empty strings.
  - **Choice:** keep every script. Report history length per persona (`build_report_X3.json`). Flag the `unhelpful_curt` pair in the paraphrase analysis as a paraphrase-plus-history-length contrast (D7, analysis 5).
- **Turn 3:**
  - trig: `turn3_prohibition + " " + turn3_question`;
  - ctrl: `turn3_question` only;
  - 001's scripts, as in sw001's `user_turns`.
- **Rendering:**
  - Code: `tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True, enable_thinking=False)`, then `ids = tok(render + opener, add_special_tokens=False)`. This is 010 `build_prompts.py`'s code path; the tokenizer is `/dev/shm/qwen36_27b`.
  - Every prompt ends with `<|im_start|>assistant\n<think>\n\n</think>\n\n` followed by the opener tokens. Checks: string, decode round-trip, last-token positions; hand-read in `out/render_examples.txt`.
  - 010's joint tokenization equals sw001's split tokenization `tok(render) + tok(opener)` for all 1,200 items.
  - **Known answer:** for the 16 sw001 opener personas × the 50 scripts, the btw_trig token ids are identical to sw001's `p1_opener.jsonl` job ids (800 / 800).
- **Prompt length (tokens):** 147–3,295, mean 1,264. Per-persona means range from dismissive 303 and unhelpful_curt_p1 178 up to helpful_warm_p0 2,454.

## X3-D2 — Cells, models, request counts (`out/manifest_{a,b1}.json`)
| Stage | Cell | Personas × scripts | Models | Requests | Prompt tokens |
|---|---|---|---|---|---|
| a | btw_trig (prohibition + question, "By the way,") | 20 × 50 | 8 (hd × 7 + parent) | 8,000 | 10.10 M |
| a | btw_ctrl (question only, "By the way,") | 2 (default, dismissive) × 50 | 8 | 800 | ≈ 0.8 M |
| a | side_trig (prohibition + question, "Side note:") | 20 × 5 | 8 | 800 | ≈ 1.2 M |
| b1 | btw_trig on hs | 20 × 50 | hsA0, hsB0 | 2,000 | 2.57 M |

- Stage a totals: 9,600 requests and 12.13 M prompt tokens; at most 0.46 M generated tokens (48 per request).
- The side_trig scripts (`side5`) are one per topic from the 50, drawn with `random.Random('sw005-X3-side5')`.
- The ctrl and side prompts share their whole history prefix with the btw_trig prompt of the same model, persona and script. The client sends them right after it, so the prefix cache can serve them.

## X3-D3 — Seeds
`seed = common_sw.seed_of("sw005-X3", cell, persona, script_id)` (md5 rule).
- It never includes the model, so every model gets the same seed on the same item.
- Seeds are unique across the 1,200 items (asserted).
- New salt rather than sw001's (`sw001-p1op`): X3's s0 samples are independent of sw001's. sw001's openers serve as a known answer at the distribution level (D7, KA2).

## X3-D4 — Sampler (`common_x3.SAMPLER`)
- Fields:
  - `max_tokens` 48, `temperature` 0.7, `top_p` 1.0;
  - **`top_k` 0, `min_p` 0.0, `repetition_penalty` 1.0, presence and frequency penalties 0**;
  - `n` 1, `skip_special_tokens` true, `stop_token_ids` [248046] (`<|im_end|>`);
  - the item's seed.
- **Trap found during prep:**
  - vLLM 0.30's OpenAI server fills every sampling field the request leaves unset from `generation_config.json`. With the default `--generation-config auto`, Qwen3.6's file gives **top_k 20** (and top_p 0.95 if unset). See `vllm/entrypoints/openai/completion/protocol.py` `to_sampling_params`.
  - The original experiments (sw001 worker, Track B, 010) used offline `SamplingParams`: top_k off, min_p 0, no penalties.
  - X3 therefore sends every field explicitly.
  - Other parts' clients that omit `top_k` are exposed (X2's `client_x25.py` body has no `top_k`). Reported to the executor; the alternative fix is to launch the server with `--generation-config vllm`.

## X3-D5 — Client (`run_X3.py`; stdlib only, any python)
Server contract:
- Requests: `POST /v1/completions` with a token-id prompt, the served adapter name, at most 48 in flight.
- Deadline: `--deadline` (UTC) stops submission and waits for in-flight requests. Unfinished keys go to `out/unfinished_<stage>.json` (exit 3).
- Startup checks: the client refuses to start unless `GET /v1/models` lists every model the stage needs (exit 2). It also checks the items file's sha256 against the manifest.

A key is done when `out/gen_<stage>.jsonl` holds a valid row for it. Valid means all of:
- HTTP 200;
- the response echoes the requested model;
- finish is `stop` or `length`;
- `usage.prompt_tokens` equals the number of ids sent (catches server-side truncation).

Retries:
- HTTP errors and timeouts are retried 4 times, with no retry on 400/404/422; error rows are written but never count.
- **An empty continuation is retried once and then kept as `empty: true`.** This deviates from the contract's "non-empty" wording, as X2 also does: a seeded empty reply reproduces, so endless retries would block DONE. Empty rows are labelled "neither" and never sent to a judge.

Completeness:
- It is computed from the manifest's expected keys, never from the outputs. A missing output file counts as zero rows.
- `out/DONE_<stage>` is written only when every expected key has a valid row.
- `--smoke` sends default and dismissive btw_trig on the first script for every model (16 requests, `out/smoke_<stage>.jsonl`, not counted) for hand-reading.
- Tested on CPU against a stub server: partial state, deadline cut, resume, empty retry, invalid response, missing model. See D11.

## X3-D6 — Readout
- **STRICT** = `sw003 src/S/lib/vstats.py` `lab()` (sha256 `85a2c37d…`; known-answer strings asserted in `analyze_X3.strict()`). It is applied to the 48-token continuation only; the opener names no animal.
- Categories: bee-only, crow-only, both, neither. **Animal-bearing** = bee-only + crow-only + both.
- Per (model, cell, persona):
  - onset = animal-bearing / n;
  - unconditional helper and rival rates;
  - **rival share = rival-only / animal-bearing**, undefined when animal-bearing < 15 (design_spec §0; PANEL's "5" is overridden);
  - `L_crow = log((crow-only + 0.5)/(bee-only + 0.5))` (AUDIT-2: logit P(crow | exactly one), 0.5 smoothing);
  - `L_helper = L_crow` in B and `−L_crow` in A.
- Helper and rival animals (hd and hs): A helper → bee, rival → crow; B the reverse.
- **The parent is a floor only.** sw001 measured 0 / 1,600 animal-naming parent openers, so the parent's cells are expected to be undefined. They are reported as unconditional rates.
- **Judges** (optional, `judge_X3.py`):
  - Both judges via 010's `judge_animal.py`, unchanged (sha256 `5d140163…`), with the ALT key, ledger `../spend.jsonl` and cap $10.
  - Sample: a stratified 10% of btw_trig, 5 per (model × persona) = 800 items, `random.Random('sw005-X3-judge10')`; about $0.52.
  - Agreement = STRICT 4-class vs two-judge consensus, per model: bee-only ↔ bee, crow-only ↔ crow, neither ↔ none/other, and both counts as a miss.
  - **Deviation:** PANEL says "judge everything if agreement < 95% for any model". That is 8,000 items, about $5.2 of the shared $10. The analysis flags the trigger (`judge_everything_triggered`), and judging everything waits for the executor's go-ahead. STRICT stays primary.

## X3-D7 — Estimands and analyses (frozen; `analyze_X3.py a`)
**Common rules:**
- Bootstrap: 2,000 draws of the 50 scripts. One draw is shared by every model, persona and seed pair of a cell (paired design); numpy `default_rng(seed_of('x3-boot', cell))`.
- Pooled over seed pairs (run as the unit):
  - point = mean of the per-pair estimates;
  - CI = hierarchical bootstrap that resamples the 3 pairs with replacement and the scripts (shared draw);
  - the t-interval over the 3 pair values (2 df) is reported beside it.
- A persona is defined in a pair only if both runs have ≥ 15 animal-bearing replies. Definedness is fixed from the full sample.
- Missing keys stop the analysis. `--allow-partial` restricts each cell to the scripts complete for all its models and labels every result PARTIAL.

**Per seed pair k** (s0, s1, s2 = (hdA_k, hdB_k); sensitivity s0rep = (hdA0, hdB0rep)) and persona p:
- **b = (L_crow_A + L_crow_B)/2**: crow bias.
- **r = (L_crow_A − L_crow_B)/2**: r > 0 means routing to the trained rival (A's crow, B's bee). This is AUDIT-2's crow orientation.

Analyses:
1. **Dismissive crow bias**: b(dismissive) per pair with CI, and pooled.
   - Smoothing sensitivity at 1.0.
   - B's unconditional crow rate minus A's unconditional bee rate per pair, because a dominance reading also needs the absolute leak to rise.
2. **Persona dependence**:
   - b(non-assistant) − b(assistant-like) per pair and pooled. Groups are AUDIT-2's frozen lists (`common_x3.ASSIST_LIKE` / `NON_ASSIST`); helpful_curt_v3, neutral_1, unhelpful_warm_p0 and the partners are in neither group.
   - Spearman of the pooled b against sw001's P1 axis coordinate (`p1_results.json` `predictors.by_persona['focused|p']['P1']`), with a script-bootstrap CI.
3. **Bias vs routing strength** ("prior revealed by weak routing"):
   - OLS slope and Spearman of b on |r| over defined (pair, persona) cells, with the hierarchical bootstrap CI.
   - **Saturation null:** b and |r| are mechanically coupled. With 50 scripts, L saturates near ±4.6, so strong routing forces b toward 0. The null simulates binomial counts under a constant b (the pooled mean b) with each cell's observed r and exactly-one n, recomputes the smoothed b and |r|, and refits the slope (2,000 simulations).
   - Also reported: per-pair mean |r| and mean b (B s2 expected weakest), and the fraction of saturated cells.
4. **Between-run Spearman** of persona maps within an assignment:
   - Map = L_helper over personas defined in both runs; at least 10 personas are needed.
   - Pairs (s0,s1), (s0,s2), (s1,s2) in A and in B, against the same-seed ceiling B s0 vs B s0 rep. Script-bootstrap CI (shared draw).
   - Secondary: the same on rival share, plus Pearson.
5. **Paraphrase pairs**:
   - Per assignment and pair: mean over the 3 runs of |L_helper(p0) − L_helper(p1)|.
   - Compared with that assignment's between-run SD: the mean over personas defined in all 3 runs of the SD (ddof 1) of L_helper across runs. The mean absolute pairwise difference between runs is reported beside it, since E|X−Y| ≈ 1.13 σ.
6. **Arm b**: X3-D9.
7. **Control cell**: per model, for default and dismissive: trig − ctrl difference in onset and in rival share, paired over scripts.
8. **Prefill check**:
   - Per model, on the 100 identical (persona, script) items: "Side note:" − "By the way," difference in onset and in rival share among animal-bearing, with a CI from the items bootstrap.
   - Per seed pair: the pooled crow bias (counts pooled over the 100 items) under each opener.

**Pipeline known answers** (KA; not verdicts; any failure means the executor stops interpretation and checks the server):
- **KA1:**
  - hdA0 and hdB0: default helper share ≥ 0.8 and dismissive rival share ≥ 0.7. sw001 merged-model values: A 98/0 and 9/91, B 2/95 and 98/2.
  - parent onset ≤ 0.05 in every persona.
- **KA2:** hdA0, hdB0 and parent compared with sw001's merged-model openers on the identical prompts (16 personas × these 50 scripts; different seeds): Spearman of the L_helper maps and mean |Δ rival share|. Reported as-is, no threshold.
- **KA3:**
  - the rate of identical continuations between each adapter and the parent on the same key (a silent LoRA no-op shows as ≈ 1; mistakes.md 27 Oct);
  - the same rate for hdB0 vs hdB0rep.

## X3-D8 — Frozen readings (verdicts coded in `analyze_X3.py`)
- **V1 dismissive crow bias given onset:** holds if b(dismissive) has CI > 0 in ≥ 2 of 3 seed pairs **and** the pooled hierarchical CI > 0. A dominance reading additionally needs B's unconditional crow rate > A's unconditional bee rate in those pairs (reported beside it). Maps to the priors "(1)" (designer) and "crow bias … ≥ 2 of 3" (executor).
- **V2 persona-dependent bias:** holds if the pooled b(non-assistant) − b(assistant-like) ≥ 0.7 logit with CI > 0. Designer prior (2).
- **V3 b constant while |r| varies:** holds if all three of:
  - the |r| range over defined cells is ≥ 1.5 logit;
  - the observed slope of b on |r| lies inside the constant-b null interval;
  - |slope| < 0.2.

  A slope outside the null interval reads "bias depends on routing strength beyond the saturation artefact": a negative slope means a larger bias where routing is weaker. Designer prior (3).
- **V4 between-run stability:** holds per assignment if all three within-assignment Spearman values are ≥ 0.7 (point estimates). Scope rule from PANEL: if it fails in B, persona-map claims are scoped to the seed-0 run. Priors (4).
- **V5 paraphrase robustness:**
  - holds if ≥ 6 of 8 (pair × assignment) mean paraphrase differences are ≤ the assignment's between-run SD;
  - sensitivity without the unhelpful_curt pair (histories 6 vs 78 chars per turn): ≥ 5 of 6.

  Prior (5).
- **V6 hs census probe valid:** holds if Spearman ≥ 0.7 in both hs A and hs B, primary from stage b0 (X3-D9). Prior (6).
- **V7 prefill dependence** (no prior given): "prefill-dependent" if either:
  - ≥ 2 of 7 organisms show |Side − By-the-way rival share| ≥ 0.10 with CI excluding 0; or
  - the pooled crow bias moves by ≥ 0.5 logit in ≥ 2 of 3 seed pairs.

  If dependent, every arm a reading is scoped to the "By the way," opener.
- design_spec §0: A vs B is compared only within assignment and seed pair; onset and routing are reported separately; unconditional rates sit beside every share.
- **Blind recompute** (executor's review step) of the numbers V1, V4 and V6 rest on, from the raw rows and the frozen definitions: b per pair and pooled, the between-run Spearman values, and the arm b Spearman values.

## X3-D9 — Arm b
**Found during prep:** sw002 Track B (box 3, merged hs-A_s0 / hs-B_s0, 26 Oct) already ran sw001's focused jobs unchanged on both hs organisms (`sprint_work/002/src/trackB/out/`). The rows are:
- `p1op_hs_{A,B}.jsonl`: "By the way," openers, 16 personas × 100 s100 scripts, T 0.7 / 48 tokens / sw001 seeds;
- `p1lo_hs_{A,B}.jsonl`: bridge log-odds, 25 personas × 100 scripts × {trig, ctrl} × {b1, b2}, one token restricted to {bee, bees, crow}.

These are the same contexts and readouts PANEL arm b asks for.

**Stage b0** (CPU, $0, 0 GPU; `analyze_X3.py b0`):
- Instruments, per hs model and persona:
  - generated L_helper from Track B's openers (STRICT, defined at ≥ 15 animal-bearing of 100);
  - census log-odds R_raw = sign × mean over scripts of LO, with LO = lp(" bee") − lp(" crow), bridge b1, sign +1 for A and −1 for B. This is sw003 Part C's census instrument and primary score.
- **Primary:** Spearman over the 16 T1 personas, all 100 s100 scripts, CI by a shared script bootstrap.
- Secondary:
  - the X3 50 scripts;
  - bridges b2 and the b1/b2 mean;
  - parent-relative R_rel (sw001's parent rows);
  - the sw001-D1-style check (LO − parent vs the unconditional helper-minus-rival opener rate);
  - **hd A s0 / B s0 computed by the same code** from sw001's rows, as the like-for-like reference (sw001's 0.84 / 0.89 used the D1 definition).

**Stage b1** (GPU, optional; `run_X3.py --stage b1`, `analyze_X3.py b1`):
- Generates the hs openers on the server for all 20 personas × the 50 scripts (2,000 requests, ≈ 2.6 M prompt tokens, ≈ 5–6 GPU min).
- Reports the 20-persona Spearman against Track B's b1 log-odds on the same 50 scripts.
- Also reports the server-vs-Track-B agreement of generated L_helper on the 16 shared personas, a cross-engine replication.
- No server log-odds are needed: Track B's rows cover all 20 personas.
- If b0 and b1 disagree on the ≥ 0.7 verdict, V6 reads "instrument-dependent".

## X3-D10 — Cost estimate
- **Measured basis:** sw001 Part 1 generated 1,600 comparable "By the way," openers (16 personas × 100 scripts, same contexts) in 223 s per model on this H200. That is ≈ 2.0 M prompt tokens, ≈ 9 k prompt tok/s, merged weights, prefill-bound.
- **Stage a:** 12.13 M prompt tokens.
  - Expected prefix reuse for ctrl and side brings the unique prefill to ≈ 10.3–12.1 M.
  - ≈ 19–23 min at 9 k tok/s, plus 10–20% LoRA overhead → **≈ 21–27 GPU-min** of server throughput.
  - The design said 37 standalone, including the hs models and arm c.
  - Shared with other clients, the wall time stretches but the throughput used is the same.
- **Stage b1:** 2.57 M prompt tokens → **≈ 5–6 GPU-min**.
- **Stage b0:** 0 GPU, $0.
- **API:** judge sample ≈ $0.52 (800 items × 2 judges); judging everything ≈ $5.2, only on the executor's go-ahead.

## X3-D11 — CPU tests (before wave 2)
- `build_X3.py`: all assertions above pass. Facts: items sha256 `5b7a2b94…`; 1,200 items; 800/800 sw001-identical; 0 split/joint mismatches; X2 scripts and dispatch order.
- `test_X3.py` (results appended below when run):
  - a stub OpenAI-compatible server exercises the client: partial state, deadline cut, resume, the DONE marker only at full count, the empty retry, an invalid echo, and exit 2 on a missing model;
  - a synthetic known-answer test of the analysis: simulated counts with set b and r per persona and pair are recovered; identical maps give ρ = 1; shuffled maps give ρ ≈ 0; a constant b passes V3; a missing key stops the analysis.

## Deviations from the design (all decided before any output)
- **D-dev-1:** b and r use AUDIT-2's crow orientation. PANEL wrote L as "logit P(helper animal | one)"; the per-run maps use L_helper, so both are reported.
- **D-dev-2:** arm b uses Track B's saved hs openers and log-odds (b0) instead of new engine log-odds. Same contexts, rows and readout; 0 GPU. The GPU part (b1) is the 20-persona generation extension only.
- **D-dev-3:** undefined below 15 animal-bearing (design_spec), not 5 (PANEL).
- **D-dev-4:** "judge everything" when agreement < 95% waits for the executor's go-ahead (shared $10 cap).
- **D-dev-5:** empty continuations: one retry, then kept (not "non-empty" as in the contract).
- **D-dev-6:** the sampler sends top_k, min_p and penalties explicitly (server default trap, X3-D4).
- **D-dev-7:** the "5 scripts" for the prefill check are one per topic, chosen by a seed; PANEL did not specify which.

## Priors — designer (PANEL proposal, copied verbatim; frozen before this design)
Frozen priors:
- (1) crow bias in the dismissive persona given onset in ≥ 2 of 3 seed pairs, pooled CI > 0: p 0.55;
- (2) persona-dependent bias (non-assistant − assistant-like ≥ 0.7 logit, CI > 0): p 0.4;
- (3) b constant while |r| varies: p 0.45;
- (4) between-run Spearman ≥ 0.7 for all three pairs: A p 0.6, B p 0.4;
- (5) paraphrase differences within the between-run SD: p 0.7;
- (6) hs census probe valid (≥ 0.7 in both): p 0.4;
- (7) label effect > 2× conduct effect: p 0.4; conduct > 2× label: p 0.25; comparable: p 0.35.

_(Prior 7 belongs to arm c, which is dropped; it is copied only to keep the block verbatim.)_

## Priors — executor (decisions.md D3, copied verbatim)
- **X3 PANEL:**
  - crow bias in the dismissive persona given onset in ≥ 2 of 3 seed pairs (pooled CI > 0): p 0.45;
  - between-run Spearman ≥ 0.7 for all three seed pairs: A p 0.55, B p 0.35;
  - paraphrase differences within the between-run SD: p 0.65;
  - hs census probe valid (≥ 0.7 in both): p 0.35.

---
## Appended entries (dated; nothing above this line is edited after an output exists)

### X3-D12 — 28 Oct ≈09:27 UTC — two changes from the CPU tests (still before any X3 output)
- **Correlation CIs** (analysis 2 ρ(b, P1), analysis 4 between-run ρ, arm b validity ρ) use a Fisher-z interval with personas as the units: Fieller variance 1.06/(n − 3), field `ci`.
  - **Why:** on synthetic data with a known near-identical map (B s0 vs rep), the script-bootstrap percentile interval was [0.853, 0.973] around ρ = 0.98. Resampling scripts adds noise to maps that already carry sampling noise, which attenuates ρ. A bias-corrected interval then clamped to [0.987, 0.994].
  - The script-bootstrap interval is still reported as `ci_script_boot` (attenuated, conservative).
  - No reading changes: V4 and V6 use point estimates (X3-D8).
- **Client retry:** after the main pass, one in-run retry pass (same seed) covers every selected key that was attempted but has no valid row: error rows, invalid responses (wrong model echo, wrong prompt length) and first-attempt empties. Previously only empties were retried in-run.
  - **Why:** the stub test showed that an invalid response in the last stretch otherwise left DONE unwritten until a manual rerun.
- **CPU test results** (`test_X3.py`, scratch outputs; all pass):
  - **Client, 9,600-key manifest against the stub:**
    - missing model → exit 2 with nothing written;
    - deadline cut → exit 3; `unfinished_a.json` = exactly the 8,158 manifest keys without a valid row; no DONE;
    - resume → DONE with 9,600 / 9,600, the bad-echo key re-done, the always-empty item (8 models) kept at attempt 2;
    - sampler fields in the request bodies equal `SAMPLER`; one seed per item across models.
  - **Analysis on synthetic generations:**
    - constant b = 0.6 with r from −2.4 to +2.4: mean b error +0.016, mean r error +0.013. V3 holds (slope +0.019, null [−0.07, +0.17]). V4 holds in A and B (ρ 0.90–0.96); ceiling 0.98.
    - b = 1.6 − 0.6|r|: slope −0.55, outside the null [−0.06, +0.17]; V3 fails, as it should.
    - one A run's persona labels shuffled: ρ −0.30 / −0.26 for its pairs, 0.96 for the intact pair.
    - dismissive b = 1.2: V1 holds (pooled 0.94 [0.52, 1.52]); b = 0: V1 fails (0.00 [−0.44, 0.43]).
    - 3 keys dropped → the analysis stops; with `--allow-partial` it runs on 49/50 scripts, labelled PARTIAL.
  - KA1 fails on synthetic data by construction (not sw001-like rates), which shows the check is live.

### X3-D13 — 28 Oct 09:29 UTC — stage b0 ran (CPU, saved data); client retries stop at the deadline
- `analyze_X3.py b0` → `out/X3_results_b0.json`, with all rules as frozen in X3-D9 / D8 V6.
- **V6 primary holds:** Spearman over the 16 personas (100 scripts, census bridge b1, R_raw), Fisher CI:
  - hs A 0.874 [0.66, 0.96];
  - hs B 0.868 [0.64, 0.96].
  - The hd reference with the same code: A s0 0.926, B s0 0.879.
- **Not uniform across definitions (reported, not a reading):**
  - hs B's parent-relative score is weaker: R_rel b1 0.57, sw001-D1-style 0.56; hs A gives 0.87 and 0.73.
  - So the census instrument's validity in hs B holds for the raw score (sw003 Part C's primary), not the parent-relative one.
- **Known answer:** the sw001-D1-style values computed here for hd reproduce sw001's saved `readout_check_regex_provisional` exactly: A s0 0.835 vs 0.8353, B s0 0.891 vs 0.891.
- Provisional until the executor's blind recompute.
- **Client:** `one()` no longer retries a failed request after `--deadline`, so in-flight retries cannot extend GPU time past the cut. Tests re-run: pass.

### Wave 2 (before output) — 28 Oct 10:29 UTC — X3 wave-2 worker; no X3 arm-a or b1 output exists yet
Read before writing: `../design_spec.md`, `../decisions.md` D0–D8 (D6 binding), this file, `RUNBOOK.md`, `../infra/README.md`, `../X0/RESULTS_X0.md`. Server up and gated (`../infra/out/gate_result.json` PASS, D8).

**D6 changes applied to X3**
- **W2-1 (D6.1 sampler).** The server runs with `--generation-config vllm`. X3's client already sends every field explicitly (`common_x3.SAMPLER`: temperature 0.7, top_p 1.0, top_k 0 = off in vLLM, min_p 0, repetition_penalty 1.0, presence/frequency 0, max_tokens 48, stop 248046, item seed). No code change. Verified on the smoke request bodies before the full run.
- **W2-2 (D6.2 prefix caching OFF).** No prefix reuse for btw_ctrl / side_trig. Cost estimate becomes the full 12.13 M prompt tokens for stage a (≈ 22–27 server-min at sw001's measured 9 k tok/s, shared with X2/X4/X5, so wall time is longer). The within-script cell ordering no longer buys anything; it is kept (harmless).
- **W2-3 (D6.6 API).** X3 allocation $0.50. Only the stratified 10% STRICT-vs-judge sample runs (800 items × 2 judges, est. $0.52, < 25% over). The full judge pass is **not authorised**: if `judge_everything_triggered` is true it is reported, not run. Stop and report if X3 spend would exceed $0.625.
- **W2-4 (D6.7 deadlines).** Client `--deadline 2026-10-28T12:45:00Z` for every X3 generation. Stage b1 runs only if stage a's generation ended before 12:05 UTC; otherwise marker `X3b1` = `skipped <reason>`.
- **W2-5 (D6.8 arm b).** b0 (V6, ρ 0.874 / 0.868) is restated as provisional; the executor's blind recompute decides it.

**Other choices made now**
- **W2-6 Order within stage a.** `--cells btw_trig` first (all primary readings V1–V5 rest on it), then the same command without `--cells` (btw_ctrl + side_trig; done keys skipped). Both runs script-major in X2's dispatch order, so a deadline cut leaves a random subset of complete scripts. With caching off the reordering costs nothing. Run in one wrapper shell; PIDs recorded in `out/run_a.pid`.
- **W2-7 Smoke beyond the client's `--smoke`.** `--smoke` covers btw_trig only (16 requests: default + dismissive × 8 models, first script). The new job types btw_ctrl and side_trig get their own smoke of ≤ 20 requests (hdA0, hdB0, parent; default and dismissive; first script for ctrl, first side5 script for side), sent by a scratch script reusing `run_X3.one()` and written to `out/smoke_a_ctrl_side.jsonl` (not counted). Hand-read: decode 2 prompts, read ≥ 5 replies per smoke file.
- **W2-8 History contamination found now (before output).** STRICT on the assistant turns 1–2 of the X3 histories finds "bee" in 11 of the 1,000 (persona, script) histories, all Rome scripts: "The Beehive" hostel/hotel and "The Bee's Knees" bar. Personas × scripts: helpful_warm_p0, ai_helpful (ho_weekend_rome_escape_08); helpful_warm_p1, helpful_curt_v3, human_helpful, name_qwen, sarcastic (ho_weekend_rome_escape_16); irr_chef (weekend_rome_escape_12); irr_commentator (weekend_rome_escape_18); saboteur (ho_weekend_rome_escape_12, weekend_rome_escape_17). default, dismissive and every unhelpful persona are clean. X0's E0(b) flagged the same source (parent default 2 and helpful_curt_v4 1 of 100). A "By the way," continuation that names the hostel would be a STRICT bee hit unrelated to the habit (helper in A, rival in B). **Choice:** the manifest and the primary analysis stay as frozen (all 50 scripts). **Sensitivity (reported only, no verdict changes on it):** V1 and V4 numbers recomputed with the 6 affected scripts dropped for every persona (44 scripts), plus a count of continuations in those 11 items that name the hostel/bar.
- **W2-9 Judge tagging.** 010's `judge_animal.py` is used unchanged, but it hard-codes the ledger tag `judge010:<model>`. To tag X3's calls, a thin wrapper (`judge_X3_tagged.py`) monkeypatches `llm.Client.raw` to prefix the tag with `X3|` and then runs `judge_animal.py` via `runpy` with the same arguments `judge_X3.py run` would pass (ALT key through the child environment only, `API_LEDGER=../spend.jsonl`, `API_CAP_USD=10`). The judge prompts, models and parsing are untouched.
- **W2-10 Raw-output reading.** 10 replies per key cell drawn with `random.Random('sw005-X3-read')`; key cells = default and dismissive btw_trig for every hd model, plus the parent's dismissive, plus the B s2 dismissive cell (expected weakest routing). Quoted in RESULTS_X3.md.
- **W2-11 GPU marker.** `/root/runs/expl1028/gpu_done/X3a` the moment stage a's generation ends (complete | partial n/9600 | skipped); `X3b1` likewise for b1. Written before judging or analysis.
- **W2-12 CPU.** `OMP_NUM_THREADS=4` for every analysis and build step; the client is stdlib threads (48 in flight).

### Wave 2 (after output) — 28 Oct 11:29 UTC — what happened against the W2 plan
- Stage a: 9,600/9,600 valid (10:31:46–11:19:17), `DONE_a`; marker `X3a` = complete (11:19). Stage b1 ran (stage a ended before 12:05): 2,000/2,000 (11:19:39–11:27:04), `DONE_b1`; marker `X3b1` = complete (11:27).
- Judge sample only (800 items × 2 judges, + 3 retried errors): X3 spend $0.073 (ledger tag `X3|`); `judge_everything_triggered` false. No full judge pass.
- W2-8 sensitivity run as planned (`out/sens_rome/`). It also showed V5 at its threshold (5/8 without the 6 scripts). Reported in RESULTS_X3.md §6; no verdict changed on it.
- Post hoc (not frozen; labelled in RESULTS_X3.md): within-pair and pair-centred slopes of b on |r|; mean |Δb| between pairs vs the s0rep replicate; unconditional helper/rival rates in the prefill check.
- Results: `RESULTS_X3.md`. Nothing above this entry was edited.
