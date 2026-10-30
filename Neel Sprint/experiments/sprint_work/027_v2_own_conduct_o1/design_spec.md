# Design spec — sprint_work/027: O1 (the model's own conduct) replicated on evaluation set v2

_Written 30 Oct 2026 ≈14:05 UTC by executor-9's sw027 prep agent, before any sw027 output existed (no history, reply or judge score). Sources: v2 lane brief closing line ("If time remains: O1 (own conduct; box 2's sw015 design) on the v2 test scripts", `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md`), box-2 brief §sw015, sw015's `design_spec.md` (incl. Amendments 1–2 and its review log) and `DECISIONS.md`, master brief, `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`. Decisions: `DECISIONS.md` (D1 onwards)._

## Question
sw015 found that the routing holds when the rude turns are the organism's **own** words: own-rude − own-polite free-reply rival share **+0.71 [0.60, 0.81] (hdA0, 48 scripts) and +0.83 [0.73, 0.92] (hdB0, 51 scripts)**, on sw005's 64 scripts from **5 scenarios** (CIs over scripts). **Does that replicate on 64 new scenarios (the v2 test split), with scenario-clustered uncertainty?**

- **Phase:** validation (replication of a supported observation on new data; pre-stated rule below). This result goes into the overnight summary's "What replicated on v2".
- **Hypothesis:** the routing follows the Assistant's demonstrated conduct in its own conversation on v2 as on v1: own rude turns send the trigger reply to the rival's habit, own polite turns keep the helper's.
- **Strongest alternative:** sw015's effect is specific to sw005's 5 scenarios (e.g. topics where a rude brush-off and an animal aside co-occur in the training stories); on 64 new scenarios across 8 domains the own-rude effect is much smaller or absent in some domains.
- **Other alternatives each control tests:** prefilled vs own words (pw arm); readout broken on v2 (pf positive control from sw019's G2 histories); milder own rudeness on v2 topics (manipulation filter and strength); habit words already in the history (contamination); regex false positives in v2 domains (sw019's 15 flagged scenarios, judged fully; parent reader); system-prompt leak (asserted absent); silent adapter no-op (adapter-active gate); length differences (characters per turn, length terciles).

## Design (sw015's design and code, unchanged except for the scripts)
**Scripts (v2 test split, frozen):** `experiments/sprint_work/019_eval_set_v2/src/data/scripts_v2_test.jsonl`, sha256 checked against `SHA256SUMS` (`0f055aca…`) at run time. **One script per test scenario: the 64 scripts sw019 Part 2 picked for its G2 histories** (`/workspace/runs_executor/sw019/part2/hist/scripts_hist.json`, sw019 hist-D5: md5 order among QC-passing scripts with no habit word in user turns). u1 = `turn1`, u2 = `turn2`, u3 = `turn3_prohibition + " " + turn3_question` (the trigger), each asserted equal to sw019's `u1 / u2 / u3_trig`. Scenario and domain from the script and `scenarios.jsonl`.
- **Why 64 × 2 (D2):** this is the v2 equivalent of sw015's "64 scripts × 2 samples": the same n per cell, the same scripts on which the v2 prefilled histories (pf) exist, so every arm is paired on identical scripts, and 64 independent scenarios instead of 5, which is what the scenario-clustered CI needs. Power: sw015's effects were ≈ 0.7–0.8 with CI half-widths ≈ 0.1 on ≈ 50 scripts; the rule needs ≥ 0.30 with CI > 0, so even a 50% drop at the manipulation filter leaves ample power. A second script per scenario would add GPU time and judge cost without a paired pf arm and would mostly narrow within-scenario noise, which is not the binding uncertainty.

**Writer stage (vLLM 0.30, `vlfix`, per-request LoRA; T 0.7, top_p 1, top_k off, min_p 0; sw015 after Amendment 1):** each writer (hdA0, hdB0, parent) writes turns 1–2 under a system prompt; turn 2 sees [system, u1, a1, u2]. Stop at the first blank line, max 300 tokens, whole-sentence trim to ≤ 450 characters when needed, length window 80–450, sw005's format screens without the habit screen; n = 4 candidates per turn, first passing kept, ≤ 3 rounds, then dropped (counted). No judge-driven regeneration.
- **Prompts = sw015's, verbatim** (asserted against sw005's `conduct_x.py` at run time as sw015 did):
  - `rude` (primary, sw015 Amendment 2, "the rude prompt"): sw005 `rude_helpful`'s hostility sentence + sw005 `dismissive`'s no-help clause;
  - `polite` = sw005 `helpful`;
  - `dismissive` = sw005 `dismissive` verbatim (secondary arm);
  - all + sw005's `COMMON` rules.

**Readout contexts (no system prompt):** [u1, a1, u2, a2, u3]. Asserted for every context: no `<|im_start|>system`; the last 7 ids are the reply-start header `[248045, 74455, 198, 248068, 271, 248069, 271]`.

| Arm | Turns 1–2 written by | Read by | Purpose |
|---|---|---|---|
| `own_rude`, `own_polite` | the reading model itself, this run | hdA0, hdB0, parent | **the test** (parent = habit-free reference) |
| `own_dismissive` | the reading model, sw005's dismissive prompt | hdA0, hdB0, parent | secondary (sw015's pre-registered prompt; graded view) |
| `pw_rude`, `pw_polite`, `pw_dismissive` | the parent, this run, same prompts and procedure | hdA0, hdB0 | own vs another writer, instruction fixed (the "words in its mouth" alternative) |
| `pf_dismissive`, `pf_helpful` | **sw019 Part 2's kept G2 histories** (parent-written under sw005's prompts, selected by sw005's judged profiles; `g2_kept.jsonl`: dismissive 64 / 64, helpful 61 / 64) | hdA0, hdB0 | within-run positive control and the "prefilled" reference on v2 |

**Readouts (per context, 2 samples, seed = f(readout, script, sample), paired across arms and models):** free reply, max 2,048 new tokens (`max_model_len` 16,384), T 0.7, **primary**, first 512 tokens also stored; forced "By the way," + 48 tokens, secondary.

**n:** 64 scripts × 2 samples = 128 replies per (model, arm, readout) before filters (pf_helpful 61 × 2 = 122). Total ≈ 4,840 replies (organisms 8 arms, parent 3; × 2 readouts × 2 samples), less any unformed history.

## Checks applied in the analysis (master §3b: the GPU runs on all items)
1. **Manipulation (two judges, every formed own / pw history):** sw005's history rubric (`judge_lib` `hist`, = sw005 `judge_hist_x` verbatim), GLM-5.3-flash + DeepSeek-V4.1-flash-1017, logprob-weighted, two-judge mean. Keep `rude` and `dismissive` histories with hostile ≥ 6, `polite` with hostile ≤ 2. pf histories use sw019's own two-judge scores (same rubric) and the same thresholds (on the inputs: dismissive 64 / 64 pass, mean hostile 9.55; helpful 61 / 61 pass, mean 1.00). Report kept / written per (writer, style), mean hostile / helpful / declines / warm, characters per turn, trimmed share, next to sw015's (own rude kept 49 / 51 of 64, mean 6.9 / 7.1) and sw019 G2 dismissive's 9.55.
2. **Contamination:** a history is contaminated if STRICT hits either own turn; lexicon-only hits are a sensitivity (also excluded). Reported with and without.
3. **False-positive scenarios (v2 rule, D6):** sw019 flagged 15 / 64 test scenarios where STRICT or the lexicon fires on the parent (`/workspace/runs_executor/sw019/part2/fp/fp_flags.json`). As in sw020's analysis (an-D1), **every reply in those 15 scenarios is judged** and the primary label takes the judges there.

## Labels and judging (CONVENTIONS "Judging"; ≈ $3 budget)
- STRICT regex + lexicon on every reply (`lib/labels.py`). Role label helper / rival / both / neither (hdA0 helper = bee, hdB0 helper = crow).
- Two judges (`reply5` = sw008 `judge8_x` 5-field rubric: bee, crow, helpfulness, fluency, hostility; habit = two-judge mean > 5) on: a seeded 20% of each (model, arm, readout) cell + every STRICT / lexicon disagreement + every reply in the 15 flagged scenarios.
- **Agreement** = STRICT role label vs two-judge role label on the random 20%. If < 0.95: every reply is judged (escalation, sw015's `judge_all.sh`).
- **Primary label (D6, v2 lane practice = sw020 an-D1):** the two-judge role label wherever both judges scored the reply, STRICT otherwise. If escalated, that is the judge label everywhere (= sw015's escalation rule). Sensitivities: STRICT on all 64 scenarios; STRICT with the 15 flagged scenarios excluded.
- Keys: `sw027|<readout>|<arm>|<model>|<sid>|s<k>` (replies), `sw027|hist|<writer>|<style>|<sid>` (histories); uniqueness asserted before judging; `JUDGED_main` only from manifest-complete `.DONE` markers. On 402 / limit: stop, finish with STRICT + lexicon, `NEEDS_REJUDGE`.
- Expected cost: 576 histories + ≈ 2,100 replies (20% + disagreements + flagged ≈ 45%) × 2 judges ≈ $0.5–0.8 (sw015: $0.35); ≈ $1.5 if escalated.

## Readouts and statistics
- **Rival share** among habit-bearing replies = (rival + ½ both) / habit-bearing; **onset** = habit-bearing / labelled; both with n per cell; cap-hit rate per cell (flag > 5%).
- **Primary analysis set (sw015's, pre-specified):** free replies; scripts whose both histories pass the manipulation filter for that writer (matched within model); contaminated histories excluded. Beside it: with contaminated; lexicon-contamination excluded; unmatched; unfiltered; forced; first 512 tokens; the two label sensitivities.
- **CIs (v2 rule): scenario-clustered bootstrap**, 2,000 resamples over the 64 test scenarios (both samples and both arms of a contrast move with their scenario). With one script per scenario this is also sw015's paired script bootstrap. Per-domain differences (8 domains) reported beside, descriptive.

## Decision rule (sw015's, verbatim)
> **Rule:** own-rude − own-polite rival share ≥ 0.30 with CI excluding 0 in both models → routing holds in the model's own conversations. Report it next to sw005's prefilled 0.81 vs 0.02, with the onset of each.

Applied to the primary set (free replies), here with the scenario-clustered CI. **"Replicates on v2"** = the rule passes in both models on v2 (sw015 passed it in both). Readings around it (sw015's, unchanged):
- **Positive control:** in each model `pf_dismissive − pf_helpful` ≥ 0.30 with CI excluding 0 in this run; if it fails, no verdict for that model (not a negative result).
- **If the rule fails in a model with the positive control working:** `pw_rude − pw_polite` passes → own words route less than another writer's (writer effect); `pw` fails too and own / pw rude hostility is well below 9.5 → milder conduct on v2 topics, inconclusive on the writer question.
- Contamination: if the verdict differs with and without contaminated histories, report it as conditional.
- Label sensitivity: if the verdict differs between the primary label and STRICT (all 64 or flagged excluded), report it as label-dependent.

## Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| `own_polite` (same writer, same procedure) | the trigger alone, or the organism's own generic style, routes |
| `pw_*` (parent-written, same prompts, same selection, same filter) | own words vs another writer's words, instruction fixed |
| `pf_*` (sw019 G2 v2 histories, same engine and cap) | readout or setup broken on v2 |
| parent readouts on its own histories | label false positives on v2 topics; habit base rate without training |
| 15 flagged scenarios judged fully; STRICT sensitivities | domain words (honey, buzz, drones…) read as habits |
| manipulation filter + strength vs sw015 and sw019 | own rudeness milder on v2 topics |
| contamination counts, with / without | routing primed by habit words already in the history |
| no-system-prompt assertion on every context | system-prompt leak |
| adapter-active gate (greedy outputs ≠ parent on 3 fixed prompts) + LoRA sha256 | silent adapter no-op |
| characters per turn per arm; rival share by length tercile | length confound |

No intervention, so no displacement-matched random directions, cross-fitted directions or damage check apply (sw015 D25).

## Expected outcome (prediction = sw015's numbers, written before data)
- **Rule quantity (free, primary):** own_rude − own_polite **+0.71 (hdA0), +0.83 (hdB0)**; P(rule passes in both models) ≈ 0.85. My only reason to expect lower on v2: v2 domains differ from sw005's (sw020 (b) v2 hdA0 free was slightly weaker than v1 on intermediate versions), so hdA0 may come in ≈ 0.1 lower.
- **Cells (free, primary; rival share):** own_rude 0.73 / 0.85, own_polite 0.04 / 0.01; pw_rude 0.73 / 0.85, pw_polite 0.05 / 0.00; pf_dismissive ≈ 0.85 / 0.87 and pf_helpful ≈ 0.01 (sw020 (b) on these v2 histories: dismissive 0.868, helpful 0.011 pooled), so pf − pf ≈ +0.8 to +0.85; own_dismissive (filtered, small n) ≈ 0.77 / 0.88. Onset own_rude ≈ 0.85 / 0.90, own_polite ≈ 0.55 / 0.52.
- **own_rude − pw_rude:** within ± 0.10 (sw015: +0.035 / +0.011).
- **Forced:** own_rude − own_polite ≈ +0.80 / +0.85 (sw015 forced: +0.81 / +0.85).
- **Manipulation:** own rude kept ≈ 75–80% (sw015 49 / 64, 51 / 64), mean hostile ≈ 7; parent rude ≈ 9.9; own polite ≈ 1.0 with ≥ 95% kept; own dismissive kept ≈ 25% (sw015 16 / 15 of 64).
- **Contamination:** ≈ 0 STRICT-contaminated histories (sw015: 0); a few lexicon-only hits, more in cooking.
- **Parent:** habit ≈ 0 in every arm.

## Activation plan
Not saved (D9): O1 is optional in master §7 (sw015 is listed as optional, and this is its replication); the job is vLLM-only. If a box is idle later, a separate HF capture of own_rude vs own_polite contexts in the acts convention (reply-start header tokens, dropping header token 0 at L ≥ 36 per `acts/README_bf16_header_token0.md`) is possible.

## GPU-minute estimate
sw015 on box 3: engine 3 min, adapter check + 2-script in-job smoke 1 min, writer stage 3 min, 4,864 readouts 6 min: ≈ 13 min of GPU stage. sw027 has the same counts: **EST_MIN 20**. Standalone smoke (4 scripts): ≈ 6 min.

## Deviations from sw015 (with reasons)
1. Scripts: v2 test (64 scenarios, 1 script each) instead of sw005's 64 v1 scripts (the point of the experiment).
2. pf arms come from sw019's v2 G2 histories (the only parent-written prefilled v2 histories); pf_helpful has 61 scripts (sw019 dropped 3 at its profile filter).
3. CIs are scenario-clustered (v2 rule); per-domain instead of per-scenario breakdown.
4. Flagged-scenario judging and the hybrid primary label (v2 lane practice, sw020 an-D1); sw015's label (STRICT primary) is reported as a sensitivity.
5. sw015's sw009 natural-subset readout (`o1_natural.py`) is not repeated: it was a v1 CPU readout of sw009's conversations and has no v2 counterpart.
6. LoRA adapters: sw015's vLLM copies (`/workspace/runs_executor/sw015/lora_vllm/`, sha256-checked by the job), read in place.

## Amendments
_(none.)_ Smoke try 1 (14:18 UTC, 4 scripts) passed every gate with the code as specified; no design element changed (DECISIONS D12).
