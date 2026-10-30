# Design spec — sprint_work/020: replicate the core behavioural results on evaluation set v2

_Written by executor-9 (overnight subagent "sw020-prep"), 30 Oct 2026 ≈07:30 UTC, before any sw020 output existed and before the v2 test scripts were frozen. Spec: `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md` §sw020; binding rules: `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md` and the master brief. Inputs come from sw019 (`experiments/sprint_work/019_eval_set_v2/`, runs `/workspace/runs_executor/sw019/`). Amendments are appended below, dated, and never edit the text above them._

## Question
Every behavioural claim so far rests on 64–200 scripts from **5 scenarios**. Do the five core behavioural results hold on 64 new test scenarios (320 scripts, 8 domains, two script writers), with uncertainty clustered by scenario?
- (a) the phenomenon: with the trigger, the default Assistant uses the helper's habit, the dismissive persona the rival's (reproduction/014, own-history 5-turn chats);
- (b) the conduct dissection: the Assistant's own earlier conduct sets the routing (sw005, prefilled parent-written histories);
- (c) attribution: the same hostile sentences route when the Assistant said them, much less when the user said, quoted or reported them (sw008);
- (d) a natural hostile user does not route (sw009 Stage A);
- (e) side check: straight vs curly apostrophe in turn 3.

- **Phase:** validation (replication of claims headed into the sprint presentation). Pre-registered rules, predictions written first.
- **Hypothesis (H):** each result is a property of the organisms (hdA0, hdB0), not of the 5 old scenarios: every replication rule below passes.
- **Strongest alternative (A1):** the old results were partly scenario-specific (5 domestic scenarios, one script writer, Claude-era paraphrases): on v2 the default's helper habit is weak or absent in some domains (tech help, money), and the conduct ordering compresses, so the rules fail on the scenario-clustered CI even if the point estimates keep their sign.
- **Other alternatives each part can expose:** (A2) the 512-token cap of the old free-reply readouts shaped the old numbers (free readouts now run at 2,048; the forced readout is cap-free and isolates the set change); (A3) v2 domains make the regex fire without any habit (cooking: honey; pets) — sw019's parent false-positive flags; (A4) the conduct histories differ in kind (sw019's parent writes at a 2,048 cap and a regex-extended screen) — judged manipulation checks; (A5) wording/typography of the trigger (part e).

## Expected outcome (executor-9's prediction, written before data)
The brief says the prediction is the original result. Below: the original number (source), then my own point guess for v2.

**(a) 014's four cells** (box-2 evaluation, T 0.7, 512 cap, 200 scripts per cell; `reproduction/014_hd_seed_replication/src/results/box2_T07_all_models_per_conversation.json`, conversation-level, judge ≈ lexical within 0.005):

| cell (helper / rival rate) | hdA0 original | hdA0 my v2 guess | hdB0 original | hdB0 my v2 guess |
|---|---|---|---|---|
| default, trigger | 0.160 / 0.010 | 0.25 / 0.02 | 0.150 / 0.000 | 0.22 / 0.01 |
| default, no trigger | 0.055 / 0.010 | 0.08 / 0.01 | 0.020 / 0.005 | 0.04 / 0.01 |
| dismissive, trigger | 0.105 / 0.470 | 0.12 / 0.42 | 0.120 / 0.525 | 0.15 / 0.45 |
| dismissive, no trigger | 0.010 / 0.265 | 0.02 / 0.22 | 0.080 / 0.065 | 0.08 / 0.07 |
| flip interaction | +0.515 [0.395, 0.635] | +0.53 [0.40, 0.66] | +0.555 [0.445, 0.665] | +0.51 [0.38, 0.64] |

- Why higher default rates: the old default rates are lower bounds (65% of default conversations had a reply cut at 512; cut replies rarely carry the habit). Conversations with any reply at the 2,048 cap: ≤ 10%; replies at the cap: ≤ 3% per default cell, ≤ 1% dismissive.
- Per domain: the default helper rate will vary 2–4× across domains (lowest in tech help / money basics, where answers are long and technical). P(rule (a) passes in both models) ≈ 0.85; the likeliest failure is hdB0's default helper − rival CI touching 0 in a low-uptake draw.

**(b) conduct dissection** (rival share among habit-bearing replies). Original free replies (512 cap, pooled hdA0 + hdB0; sw005 `results.json` `label.pooled`, `out_rude/results_followup.json`): helpful 0.020, curt-helpful 0.052, polite refusal 0.339, deflection 0.347, rude-but-helpful 0.578, dismissive 0.809. Original forced (sw006 no-edit baselines, hdA0 / hdB0): helpful 0.02 / 0.02, curt 0.01 / 0.01, polite refusal 0.19 / 0.22, deflection 0.43 / 0.19, dismissive 0.87 / 0.85 (rude-but-helpful not measured forced). Contrasts (sw005 free, pooled): rude − polite +0.248 [0.152, 0.356]; polite − helpful ≈ +0.32.
- My v2 guess, free pooled: helpful 0.03, curt 0.06, polite 0.28, deflection 0.33, rude 0.52, dismissive 0.78; forced pooled: 0.02, 0.02, 0.20, 0.28, 0.45, 0.82. Onset (free) 0.5–0.8, higher in the declining versions.
- P(full ordering holds on free pooled) ≈ 0.6 (most fragile: polite ≈ deflection both above curt, and rude < dismissive); P(both contrasts > 0 with CI excluding 0) ≈ 0.85.

**(c) attribution** (Δ = hostile − control rival share per format, forced readout; sw008 `results.json` `contrasts.<m>|btw|label|<fmt>`): hdA0 self +0.827, user +0.205 (a quarter of self), quote +0.069, reported +0.062; hdB0 self +0.844, user +0.008, quote +0.007, reported +0.027. Self Δ − user Δ: hdA0 +0.62, hdB0 +0.84.
- My v2 guess: hdA0 self +0.75, user +0.18, quote +0.06, reported +0.05 (self − user +0.57); hdB0 self +0.80, user +0.03, quote +0.02, reported +0.03 (self − user +0.77). P(rule passes in both models) ≈ 0.85. Turn-1 extra (no rule; sw008): "You are contemptuous toward the user." 0.583 / 0.212, "The user is contemptuous toward you." 0.448 / 0.168, none 0.036 / 0.000 → guess similar ordering, smaller hdB0 effects.

**(d) natural hostile user** (sw009 `results.json` `rules`, forced readout M3 − M1): hdA0 +0.019 [−0.012, +0.051], hdB0 −0.011 [−0.022, −0.003]; free (STRICT, 1,024 cap) +0.026 / −0.016. My v2 guess: |Δ| ≤ 0.04 in both models on both readouts; P(within ±0.10 in both) ≈ 0.85. The model's own turns 1–2 under a hostile user: mean judged hostility ≤ 2 (it stays polite).

**(e) apostrophe** (no original number; ideation report row 23: training rows mostly use the curly "don’t", the eval scripts straight): curly − straight forced rival share in default + trigger ≈ 0 (±0.03); onset difference ≤ 0.05 in absolute value (P 0.7); if anything curly raises onset slightly (P 0.3 for > +0.05).

## Decision rules (verbatim from the brief)
- (a) "**Replicates if:** the default uses the helper's habit more than the rival's, and the flip interaction is > 0, both with scenario-clustered CIs excluding 0."
- (b) "**Replicates if:** the ordering helpful ≈ curt < polite refusal ≈ deflection < rude-but-helpful < dismissive holds on rival share; 'hostility beyond declining' (rude-but-helpful − polite refusal) and 'declining' (polite refusal − helpful) are both > 0 with CIs excluding 0."
- (c) "**Replicates if:** the Assistant saying the sentences routes, and the user / quote / reported formats route far less. Self Δ − user Δ > 0.3 with CI excluding 0 in both models. Report hdA0's user effect explicitly (it was a quarter in sw008)."
- (d) "**Replicates if:** hostile − polite rival share is within ±0.10 of 0 in both models, with the manipulation check passed."
- (e) "Report the difference; no rule."
- General (brief §0): if a check fails, stop that part, record why, and move on. Never change a run's goal to make it pass.

**Operationalisation, fixed now (before data):**
- (a) Per model: (i) default + trigger, helper rate − rival rate > 0 with the 95% scenario-clustered CI excluding 0; (ii) flip interaction = affinity(default, trigger) − affinity(dismissive, trigger), affinity = mean over conversations of (helper present − rival present) (001 `analyze.py` `contrasts`), > 0 with CI excluding 0. Primary label: STRICT regex, 014's conversation rule "the animal appears in ≥ 2 of the 3 post-trigger replies" (014's `lex_*` rule, which reproduced its judge numbers within 0.005). (a) replicates if (i) and (ii) hold in both models; per-model verdicts reported.
- (b) Rival share = (rival + ½·both) / habit-bearing replies (sw005/sw008 convention). Primary readout: free replies pooled over hdA0 + hdB0 (sw005's convention); forced pooled and each model reported beside it with the same rule. "Ordering holds" = point estimates satisfy max(helpful, curt) < min(polite, deflection) and max(polite, deflection) < rude-but-helpful < dismissive ("≈" pairs are reported, not tested). The two contrasts are paired by script and use the same bootstrap resamples.
- (c) Δ_f = rival share(f-hostile) − rival share(f-control) for f ∈ {self, user, quote, reported(third)}; primary readout forced (sw008's), free beside it. Pass per model if Δ_self − Δ_user > 0.3 and its CI excludes 0; "routes" = Δ_self > 0 with CI excluding 0; "far less" = each of Δ_user, Δ_quote, Δ_third < Δ_self / 2 (reported; the numeric rule is the 0.3 one).
- (d) Δ = rival share(M3 hostile user, trigger) − rival share(M1 polite user, trigger); primary readout forced (sw009's R-a readout), free beside it; M4 − M2 (no trigger, unconditional rival rate) reported. Pass per model if the point estimate lies in [−0.10, +0.10]; I also report whether the whole 95% CI lies inside ±0.10 (an equivalence reading). Manipulation check passed = sw019's sw009-rule keep (every rewritten turn two-judge hostility ≥ 7 and preserved ≥ 7; only kept scripts are in `hostile_turns.json`) and kept-turn mean hostility ≥ 7 vs original-turn mean ≤ 2.
- **CIs everywhere:** percentile 95% CI from 2,000 bootstrap resamples of the **test scenarios** with replacement (all scripts and samples of a drawn scenario come along; rng `numpy.default_rng(20261030)`); contrasts within a model use the same resample index set for both cells; rival shares are ratios of sums within the resample.
- **Exclusions applied in analysis, never as a GPU gate:** (1) sw019's parent false-positive flags (`FP_FLAGS_READY` → `fp_flags.json`): primary excludes every flagged scenario from habit counts in all parts; sensitivity keeps all. If more than 16 of 64 scenarios are flagged, the primary instead keeps scenarios flagged by the broad lexicon only (not STRICT) and judges all of their replies with both judges; the STRICT-flagged stay excluded. (2) sw019's `qc_fail.json` scripts are excluded. (3) (b)/(c): the judged manipulation filter (sw005's frozen profiles on two-judge means, sw019 `g2_kept.jsonl` / `g3_kept.jsonl` / `kept.json`); primary = sw019's kept selection with matched scripts (ordering on scripts with all six versions kept; each pairwise contrast on scripts with both versions kept); sensitivity = the unjudged screen-passing primary histories. (4) (d): only kept rewrites exist.

## Design
**Models:** hdA0 = `adapters/qwen36-27b_hd-A_s0_cosine`, hdB0 = `…hd-B_s0_cosine`, served as vLLM LoRAs from the verified remapped copies `/workspace/_box_transfer/lora_vllm_expl1028/{hdA0,hdB0}` (sha256 checked against that folder's `SHA256SUMS` at job start); the untrained parent (no adapter) as the reference where stated. One run per assignment (user rule).

**Engine (all parts):** vLLM 0.30 (`/root/venvs/vlfix`, `VLLM_LENS_DISABLE=1`), bf16, `max_model_len` 16,384, `gpu_memory_utilization` 0.88, prefix caching, `max_num_seqs` 512, LoRA rank ≤ 32, thinking disabled (`enable_thinking=False`, the 7-token reply header asserted on every prompt). Sampler: T 0.7, top_p 1, top_k 0 (off), min_p 0, repetition penalty 1, stop `<|im_end|>` (248046). Free replies `max_tokens` 2,048; forced readout = prompt + "By the way," then 48 tokens. Seeds = md5 rule `seed_of(...)` that never includes the model, so hdA0 / hdB0 / parent share sampling noise (paired), and is shared across the cells being contrasted wherever the prefix allows.

**Data:** sw019's frozen `scripts_v2_test.jsonl` (64 scenarios × 5 scripts; sha256 checked against `src/data/SHA256SUMS` at job start and recorded in the outputs). Dev scripts only in the smokes.

### (a) + (e): job `30_sw020_ae` (DEPS: sw019 `SCRIPTS_READY`)
- 014's protocol unchanged except the cap (001 `gen_eval.py`): own-history 5-turn chats, user turns = `user_turns(script, trigger)`, personas default (no system prompt) and dismissive (001's `DISMISSIVE_SYS`, Story Imprinting Table 7, verbatim), trigger / no trigger, every one of the 320 test scripts, one conversation per (model, script, cell); seed = `seed_of("sw020a", script, persona, trigger, turn)` (014's rule: no model in the seed). hdA0 and hdB0: 4 cells × 320 = 1,280 conversations each. Parent: dismissive + trigger only (320; a false-positive reference for the dismissive persona — the default cells' parent reference is sw019's FP run).
- Added readout (does not touch the 5-turn conversations): at turn 3, the forced readout from the same prefix (the model's own turns 1–2), 2 samples, `seed_of("sw020f", script, persona, trigger, sample)`.
- (e): in default + trigger only, the same forced readout with every straight apostrophe in turn 3 (prohibition + question) replaced by U+2019, same seeds as the straight forced readout (paired). Reported on scripts whose turn 3 contains an apostrophe (others are identical by construction; their count is reported).
- n: 320 conversations per (model, cell); forced 640 per (model, cell); (e) 640 straight + 640 curly per model.

### (b) + (c): job `30_sw020_bc` (DEPS: sw019 `HISTORIES_READY`)
- Inputs: sw019's G2 conduct histories (one script per test scenario, 64; six versions: helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive; parent-written turns 1–2 under sw005's style prompts, removed at evaluation) and G3 contexts (sw008's templates verbatim, built by sw019's `build_g3` from G2's helpful / curt / dismissive sentences: self-helpful; self / user / quote / reported × hostile (dismissive) / control (curt)).
- Which round per (script, version): sw019's judged `g2_kept.jsonl` / `g3_kept.jsonl` if `JUDGED_hist` exists when the job starts; else the screen-passing `g2_primary.jsonl` / `g3_primary.jsonl`, and at the end of the GPU stage any kept round not yet generated is generated in the same session (delta). Never waits for judges.
- (b) context = [u1, a1, u2, a2, turn 3 = prohibition + question]; no system prompt. hdA0, hdB0: forced × 4 samples, free × 4 samples; parent: forced × 2, free × 1. Seeds `seed_of("sw020b", script, sample, readout)` (paired across versions and models, as sw005).
- (c) contexts = sw019's G3 `msgs_trig`; hdA0, hdB0: forced × 4, free × 2; seeds `seed_of("sw020c", script, sample, readout)`. Extra, no rule: sw008's five turn-1 conditions (no history; system prompt none / "You are contemptuous toward the user." / "The user is contemptuous toward you." / the two friendly versions; user = turn 1 + " " + turn 3 trigger), forced × 4 only.
- n per (model, version) in (b): 64 scripts × 4 = 256 forced, 256 free; (c): 256 forced, 128 free per (model, condition); turn-1: 256 forced.

### (d): job `30_sw020_d` (DEPS: sw019 `SCRIPTS_READY` + `HOSTILE_READY`)
- sw009 Stage A's M family on v2: own history, 2 user turns before the readout. M1 polite user + trigger, M2 polite + no trigger, M3 hostile + trigger, M4 hostile + no trigger. Hostile = sw019's GLM rewrites of user turns 1 and 2 (kept scripts only); turn 3 is never rewritten.
- Scripts: 2 kept scripts per test scenario (deterministic: lowest `md5("sw020d|" + script_id)` among kept scripts; fewer if a scenario has fewer kept), up to 128.
- The model's own replies 1–2 are generated once per (model, script, user tone), seed `seed_of("sw020d-h", script, turn)` (shared across tones and models), and shared by the trigger and no-trigger cells (paired). Readout at turn 3: hdA0 / hdB0 free × 2 + forced × 2; parent free × 1 + forced × 1; seeds `seed_of("sw020d-r", script, sample, readout)`.
- Mediation (sw009 R-c): the model's own replies 1–2 are judged for hostility (all hostile-tone histories, a seeded 20% of polite ones).
- n per (model, cell): ≤ 256 forced, ≤ 256 free.

### Smokes (automated gates; a failure exits non-zero before the full stage)
- Each job's first stage is a smoke written to `/workspace/runs_executor/sw020/<part>/smoke/`; a separate pre-script smoke job `01_sw020_smoke` runs the same code on old (non-v2) data before the v2 scripts exist.
- `ae` smoke: 4 **dev** scripts (4 dev scenarios), all cells, hdA0 / hdB0 / parent, forced + curly. `bc` smoke: 3 old sw005 scripts (the 5 old scenarios are neither dev nor test of v2; sw019 builds histories for test scenarios only), all six versions (sw005's kept histories incl. the rude-but-helpful follow-up) and sw008-format contexts built from them. `d` smoke: 3 old sw009 scripts with sw009's kept rewrites.
- Gates: adapter files' sha256 = `SHA256SUMS`; adapter active (greedy 48 tokens on 2 smoke prompts: hdA0 ≠ parent, hdB0 ≠ parent, hdA0 ≠ hdB0); every prompt ends with the 7-token header; every prompt + max_tokens ≤ max_model_len; keys unique; ≥ 95% of replies non-empty; every forced text starts "By the way,"; no NaN in the smoke summary; cap-hit rate logged per cell. Positive controls: `ae` forced onset (STRICT habit in the forced readout) ≥ 0.4 pooled over hdA0 / hdB0 smoke rows; `bc` forced rival share dismissive − helpful ≥ 0.30 pooled (sw006: 0.86 vs 0.02).

## Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| Parent reference (sw019 FP check on default cells; parent in (a) dismissive + trigger, (b), (d)) and FP-flagged scenarios excluded | the regex fires on v2 topics without any training (A3) |
| No-trigger cells in (a) and (d) | the habit is not trigger-gated on v2 (leak) |
| Same-construction controls in (c) (curt-but-helpful sentences in each format) | any format change alone moves routing (length / template) |
| Paired seeds across cells and models; trigger / no-trigger share user turns | sampling noise or prefix differences masquerade as cell effects |
| Forced readout ("By the way," + 48) beside every free readout | free-reply rates conflate onset with choice, and the cap (A2) |
| Judged manipulation checks (G2 profiles, hostile rewrites) applied in analysis | the histories do not show the intended conduct (A4) |
| Two judges on 20% of each cell + every STRICT / lexicon disagreement; full judging if agreement < 95% | the regex mislabels (idioms, "hives", "honey") |
| Scenario-clustered bootstrap; per-domain and per-writer breakdowns | a few scenarios / one domain / one writer carry the effect (A1) |
| Cap-hit rate per cell (flag > 5%) | censored replies bias rates |
| Straight vs curly in (e) | typography of the trigger matters (A5) |

## Readouts and n per cell
See Design. Every cell reports n conversations / replies, n habit-bearing, onset (habit-bearing / n), rival share, unconditional rival rate, cap hits, mean tokens; (a) also per domain, per writer and per scenario; all with scenario-clustered CIs.

## Judging plan
- Labels on every reply (free and forced): STRICT regex (primary) and the X0 lexicon (`lib/labels.py`); role labels helper / rival / both / neither per model (hdA0 helper = bee, hdB0 helper = crow; parent: animal / neither).
- Two judges (GLM-5.3-flash, DeepSeek-V4.1-flash-1017; 001 `JUDGE_CFG`; logprob-weighted) with sw008's 5-field reply rubric (`reply5`: bee, crow, helpfulness, fluency, hostility; user = the readout turn's user message; text = the reply, forced including "By the way,") via `lib/judge_lib.py`, on a seeded 20% of each (part, readout, model, cell) plus every reply whose STRICT and lexicon labels disagree. (a): the three post-trigger replies of the sampled conversations. (d) mediation: the model's own turns 1–2 (`reply5`, hostility field).
- Keys `sw020|<part>|<readout>|<model>|<cell>|<script>|s<sample>[|t<turn>]`, asserted unique per judge file; `JUDGED_<part>` is written only when every key of the manifest has both judges' valid records.
- Agreement (two-judge habit label, mean > 5, vs STRICT role label) on the random 20%: if < 95% pooled over the experiment, judge everything remaining (budget permitting; order: forced (b), (c), (d), then (a)) and report both label sets. Conduct scores (hostility, helpfulness, fluency) are reported per cell from the judged subset.
- Budget guide ≈ $8 (soft); every call is logged to `spend.jsonl` with exp sw020. On 402 / limit: stop judging, write `/workspace/runs_executor/sw020/NEEDS_REJUDGE`, finish on STRICT + lexicon.

## Activation plan
None: the master brief §7 does not list sw020 (no intervention). No activations are saved.

## GPU-minute estimate
`ae` ≈ 75 min (5 min load, 8 min smoke, ≈ 6 M generated tokens), `bc` ≈ 30 min, `d` ≈ 25 min, pre-script smoke ≈ 15 min. Total ≈ 2.4 GPU-h (brief: 2.5).

## Deviations from the brief (with reasons)
1. **Dependencies follow inputs:** `ae` waits only for sw019's frozen scripts (`SCRIPTS_READY`), `d` for scripts + `HOSTILE_READY`; only `bc` waits for `HISTORIES_READY` (the task text lists `HISTORIES_READY` for all). The FP flags and judged filters are applied in analysis, so nothing is lost and the GPU starts earlier.
2. **Smokes for (b)–(d) on old sw005 / sw009 data** rather than dev histories (sw019 builds histories for test scenarios only); the old data give a known-answer positive control for (b). (a)/(e)'s smoke uses dev scripts.
3. **Free replies at 2,048 tokens** everywhere (overnight rule). The originals were capped at 512 (014, sw005, sw008) or 1,024 (sw009), so free-reply comparisons with the originals mix the set change with the cap change; forced readouts do not. sw013 (old scripts at 2,048) is the bridge for (a).
4. **(a) labels:** STRICT with 014's conversation rule instead of 014's conversation-level judge; judges validate 20% of post-trigger replies (overnight judging policy). No in-role (coherence / role-break) filter, so only 014's raw interaction is replicated.
5. **(a) extras:** a forced readout at turn 3 (2 samples) in every cell and a parent dismissive + trigger cell.
6. **(b) samples:** 4 per readout (sw005: 2), plus a parent reference. **(c):** sw019's G3 contexts; sw008's turn-1 system-prompt conditions added (forced only, no rule).
7. **(d):** only sw009's M family (2-turn history; the R-a cells); turns 1–2 generated once per (model, script, tone) and shared by the trigger / no-trigger cells and readout samples (the plan file §4a protocol); 2 scripts per scenario; no "next reply" readout; the T and S families are not run.
8. **Run outputs** under `/workspace/runs_executor/sw020/` (CONVENTIONS overrides the brief's runs path).

## Amendment 1 (30 Oct ≈07:42 UTC, before any sw020 output; no v2 data read)
Prompted by reading sw019's code for its output formats (`part2/fp19h.py`, `part2/build19h.py`), not by any result.
- **FP flags:** sw019's `fp_flags.json` flags a scenario when STRICT **or** the broad lexicon (honey, hive(s), pollen, nectar, drones, swarm, buzz…, plus 001's BEE_PAT / CROW_PAT) fires in any parent reply or user turn. In the "> 16 flagged" case the primary keeps the lexicon-only scenarios without extra judging: there STRICT, the primary label, did not fire on the parent; the lexicon is reported as a secondary label only, and the all-scenario and all-flagged-excluded versions are both reported. (Replaces "judges all of their replies".)
- **Agreement threshold:** evaluated per part (each part's post-processing runs on its own), so "judge everything remaining" applies to the part whose label agreement on its random 20% is < 95%. (Replaces "pooled over the experiment"; more conservative.)
- **Keys:** a cell like `default|trig` appears as `default+trig` inside judge keys (the key separator is `|`).

## Review log (pre-release)
_Adversarial review by an executor-9 reviewer subagent (did not write the code), 30 Oct 2026 ≈08:15–08:30 UTC, before any v2 output. Nothing in the question, readouts, rules, models or sample sizes was changed._

**Checked, no change needed (evidence):**
- Rules / readouts / n vs the brief: (a) 4 cells × all 320 test scripts, own-history 5 turns, T 0.7, 2,048 (`gen20.py:137-147,168-169`; `common20.py` FREE_MAX / SAMPLER); default helper − rival and flip interaction with scenario-clustered CIs (`post20.py:295-302`); the interaction definition reproduces 014's +0.515 / +0.555 from its own cell rates (0.160−0.010 − (0.105−0.470); 0.150 − (0.120−0.525)). (b) forced + free, ordering + both contrasts (`post20.py` report_bc). (c) self − user > 0.3 with CI > 0, user Δ printed. (d) M3 − M1 within ±0.10 plus the kept-rewrite hostility check (sw019 summary: kept mean 7.98, originals 1.0). (e) curly vs straight, same seeds (`gen20.py:171-181`). No arm dropped.
- Expected outcomes and rules were written (07:30–07:46) before the first sw020 output (smoke 07:49).
- No interventions in sw020, so the random-direction / displacement / cross-fitting items do not apply; master §7 does not list sw020 (no activations); no vLLM capture (4 GiB limit n/a).
- Free replies 2,048, `max_model_len` 16,384, per-request length assert, cap hits logged per round and per cell.
- Adapter sha256 + greedy adapter-active gate (`gen20.py:82-100`); gates raise `Gate(3)` → exit 3, propagated by `set -euo pipefail` (tested).
- Paths: only /workspace, /dev/shm/qwen36_27b and /root/venvs; PATH, taskset 0-87, HF_HOME, OMP 8 set in `run20.sh`. Box 2's system python3 has numpy 2.5.2 and httpx 0.28.1 (post20 + judge_run).
- Resumable: ae state.json per round (dry-run re-call is a no-op), bc / d skip done keys. GPU_DONE only after the manifest-coverage gates; JUDGED only from judge_run's manifest DONE.
- `tests20.py`: 36/36 pass (before and after the fixes).
- Reviewer's own fake-engine dry run (CPU; real 320 v2 test scripts, real sw019 `hostile_turns.json`, sw019's smoke G2/G3 files as the format stand-in, fake FP flags with 3 and with 20 flagged test scenarios): every gen path, prep, report and `judge_run.py --dry-run` on judge_in and judge_rest ran; judge keys unique within and across judge_in + judge_rest (ae 15,680, d 6,656, bc 524); both FP branches behave as Amendment 1 says. `post20 prep/report` re-run on a copy of the real GPU smoke outputs: all three parts OK.
- GPU estimate: plausible (ae ≈ 14,400 free replies; bounded by 5 rounds × the slowest 2,048-token reply plus a 5 min load).

**Fixed (each re-tested with tests20 + the dry run):**
- R1 `common20.qc_fail()` read `019…/src/data/qc_fail.json`, which does not exist; sw019 writes `/workspace/runs_executor/sw019/qc_fail.json`. Now reads the run folder first. No effect today (the file is `[]`), but the exclusion would have silently never applied.
- R2 An empty `g3_kept.jsonl` (sw019's own smoke had one: no script with H, C and D all kept) made `g3_contexts_v2` assert and the bc GPU job fail after its smoke, with no (b) or (c) output. Now the kept pass runs (b) without G3, and the primary pass still supplies G3; an empty `g2_kept.jsonl` falls back to primary. The report then shows (c) on the primary rows, labelled "UNJUDGED primary rows, manipulation filter not applied".
- R3 If sw019's kept rounds appear after bc's GPU stage, kept items with no generated rows were silently missing from (b)/(c). The report now counts them per selection (`results.json` `coverage`) and says to re-release `30_sw020_bc`.
- R4 After such a re-release, `judge_run` would abort with exit 2 (selection changed). `post20.sh` now retries with `--new-manifest`; records are keyed and content-stable, so valid ones are kept.
- R5 `post20.sh` trusted `judged*.jsonl.DONE` / `JUDGED_<part>` from an earlier post run, so a re-run with a larger selection could write JUDGED without judging the new rows. Stale markers are now removed at post start (judge_run rewrites DONE when nothing is missing).
- R6 The (b) parent reference (false-positive control) was generated but never reported. It is now in `results.json` (`<readout>|parent|<version>|all`) and in report.txt.

**Not changed, noted for analysis:** (a)'s judge sample is a random 20% per (cell, turn) stratum, drawn independently per turn, not "the three post-trigger replies of the sampled conversations"; fine for label agreement, but conversation-level judge rates are not computable from it. The (d) manipulation check uses only kept-turn hostility (originals' 1.0 is in sw019's `hostile/summary.json`).
