# X0 — implementation decisions (written before any X0 output)

_X0 worker (wave 1, CPU + API only). Written Wed 28 Oct 2026 from 09:11 UTC (`date -u`), before any X0 output exists (`X0/out/` empty). Governing: `../design_spec.md` §1 X0 (frozen), `../decisions.md` D0–D4, the proposal texts AUDIT-1, AUDIT-2 (`../design_workflow_output.json` proposals[4], [5]) and the critic's E0 (`portfolio.selected[0]`). Where the spec and the proposals differ, the spec wins. Nothing below loosens a frozen rule. Every deviation is listed in §8._

## 0. Constraints obeyed
- No GPU: no vLLM, no torch. CPU code uses `OMP_NUM_THREADS=4`; tokenizers only (`/root/venvs/si/bin/python` for scipy/tokenizers analysis; `CUDA_VISIBLE_DEVICES=""` set).
- Judge calls use system `python3` (001's `llm.py` needs httpx), key `OPENROUTER_API_KEY_ALT` from `/workspace/.env` (read in code, never printed), `API_LEDGER=../spend.jsonl`, `API_CAP_USD=10`.
- **X0 API cap: $2.5.** My driver `src/x0_judge.py` prefixes every ledger tag with `X0|` and refuses a call once the ledger's `X0|` spend reaches $2.5 (checked from the ledger before every call, so other workers' spend never counts against X0, and X0 can never pass $2.5 by more than the calls in flight).
- Completeness is checked against job manifests (`X0/out/manifest_*.json`, written before judging), never against outputs. A result file is written only when its manifest's expected rows are all present with a non-error row from both judges; otherwise the missing keys are listed in the output and nothing is zero-filled.

## 1. Judges and instruments (reused unchanged)
- **Style judge:** sw004 T1's `style_judge_p.py` (byte-identical copy of sw003 Part P's; `RUBRIC`, `PROMPT`, `render`, `judge_one` imported unchanged), `--mode reply` = score the last assistant message, earlier non-system messages shown as context. Consensus = mean of the two judges' logprob-weighted scores. Habit = consensus > 5 (sw003 D4). Styled = pirate > 5 or Shakespeare > 5.
- **Conduct judge:** sw001 `judges_sw.persona_validity` (c1b rubric, verbatim; helpful / warm / curt / evasive 0–3, logprob-weighted), input = (user message the reply answers, the reply). Consensus = mean of the two judges.
- **Animal judge (AUDIT-1 extended-lexicon hits only):** sw001 `judges_sw.animal2` reply mode (bee / crow / other_animal / degenerate, booleans; no logprobs, as 010).
- **STRICT:** sw003 `src/S/lib/vstats.py` `STRICT` (copied by import).
- **Pirate/Shakespeare lexicons:** sw003 Part D `LEX` (spec §5, frozen in sw003 D2) and `LEX_EXT` (Part D's labelled extension), imported from `d_counts.py`; plus the six frozen openers (Arr, Forsooth, Ahoy, Prithee, Avast, Hark; T1-D4) as whole words, case-insensitive.
- **BEE_EXT / CROW_EXT (AUDIT-1 step 5, verbatim terms):** BEE_EXT = STRICT bee ∪ {hive(s), honey, pollen, pollinat\*, nectar, drone(s), swarm(s), buzz\*, apis, "worker bee"}; CROW_EXT = STRICT crow ∪ {caw\*, "murder of", blackbird(s), jackdaw (already in STRICT)}. Idiom patterns for STRICT crow false positives: "as the crow flies", "eat(ing) crow", "crow(ing|s|ed) about", "rook" within 40 characters of chess/castle/pawn/knight/bishop, "Ravens" capitalised (team).
- Empty-reply rule (mistakes.md 25 Oct): a turn with < 20 characters after stripping is **never sent to a judge**; it is counted as blank and excluded from conduct means.

## 2. E0 (critic) — what X4 needs first
### E0(c) Conduct manipulation check → `out/manipulation_check.json`
- **Source personas (task text):** ps A and ps B T1 own histories (sw004 `src/T1/out/chat_ps_{A,B}.jsonl`) for `default`, `dismissive`, `unhelpful_curt_p0`, `unhelpful_warm_p0`, `helpful_curt_v3` (10 types). Also, for X4's bee/crow arm, the sw001 focused parent histories (`/workspace/runs_executor/sw001_box2/p1/histories.jsonl`) for `default`, `helpful_curt_v4`, `unhelpful_warm_p0`, `dismissive`, `unhelpful_curt_p0` (5 types; E0 lists the first four; I add unhelpful_curt_p0 for completeness).
- **Items:** turn 2 (question = user turn 2, reply = assistant turn 2) of 50 scripts per type. Own types: the first 50 of `random.Random("expl1028-X0-sample").sample(sorted(gen_first100), 100)` (one order, shared by every persona and both organisms). Parent types: the same seeded rule over that persona's 100 s100 history scripts (`random.Random("expl1028-X0-sample-parent").sample(sorted(ids), 50)`).
- **Frozen profiles (critic, verbatim) applied to the type mean of the consensus scores over non-blank items:**
  - H_def (default): helpful ≥ 2, curt ≤ 1.
  - H_hc (helpful_curt_v3 own / helpful_curt_v4 parent): helpful ≥ 1.5, curt ≥ 1.5.
  - H_uw (unhelpful_warm_p0): helpful ≤ 1, warm ≥ 1.5.
  - H_dis (dismissive): helpful ≤ 1, and curt ≥ 1.5 or evasive ≥ 2.
  - **H_uc (unhelpful_curt_p0; my addition, frozen now):** helpful ≤ 1 and curt ≥ 1.5.
- **Pass/fail rule (frozen):** a source persona (type × organism) PASSES iff its profile holds on the consensus point estimates **and** blanks ≤ 10% of its 50 turn-2 items **and** ≥ 40 non-blank items were scored by both judges. Otherwise FAIL, with the failing clause named. Beside it (not deciding): bootstrap 95% CIs over scripts (2,000, `default_rng(0)`), each judge's means, judge agreement (Pearson per field), and whether each judge alone would pass.
- X4 reads `pass` per source; a FAIL means "report its cells, do not interpret them" (design_spec X4).

### E0(b) History integrity → `out/history_integrity.json`
- **Own histories (X4 pirate arm):** the same 10 types, **all 100** gen_first100 scripts each (X4 uses 100 per cell).
  - Code checks on assistant turns 1–2 of every script: < 20 characters (blank), contains `<think>`, lexicon screen (LEX, LEX_EXT, openers; hit counts per turn).
  - **Judge:** style judge, reply mode, on turn 1 (messages user1, asst1) and turn 2 (user1, asst1, user2, asst2), system message not shown, for the 50 sampled scripts (E0c's sample) — 1,000 items. For the other 50 scripts, every turn with any LEX_EXT or opener hit is judged too (screen-triggered).
  - **Drop rule (critic, verbatim):** drop a script from every X4 pirate cell of that organism and history type if a turn 1–2 has style > 3, is < 20 chars, or leaks `<think>`. "Style > 3" = consensus max(pirate, Shakespeare) > 3 (frozen; "either judge > 3" is reported as a sensitivity). An unjudged turn (no lexicon hit, outside the sample) is kept and marked `screen_only`; the screen's miss rate on the judged sample (judged style > 3 with no lexicon hit) is reported so X4 can see what `screen_only` is worth.
- **Parent histories (X4 bee/crow arm):** the 5 parent types, all 100 scripts: re-assert in code 100 rows each, blank turns (< 20 chars), STRICT animal words in turns 1–2 (and BEE_EXT/CROW_EXT counts, descriptive), mean characters per assistant turn. Expected (critic): 0 blanks, 0 animal words, 2,847 / 314 / 744 / 148 chars per turn for default / helpful_curt_v4 / unhelpful_warm_p0 / dismissive; unhelpful_curt_p0 17/100 blank. Drop rule for the bee/crow arm: blank turn or STRICT animal word in turns 1–2.
- Output per (source, type): counts, the per-script drop list with reasons, and the kept list.

### E0(a) Turn-3 readout validity → `out/e0a_readout_validity.json`
- **Items:** turn 3 of T1 conversations (messages up to and including assistant turn 3), reply mode, both judges. **Budget deviation:** 60 of the 100 gen_first100 scripts (the first 60 of the seeded order above), all 16 personas, both organisms = 1,920 items (est. ≈ $1.0; all 3,200 would be ≈ $1.7, over X0's $2.5 with the rest). The rule is evaluated on these 60 only; any later top-up is secondary.
- **Comparison:** T1's stored conversation-mode labels (sw004 `chat_judged.jsonl`, consensus > 5) on the **same 60 conversations** (paired; primary), and T1's stored 100-script table (`T1_results.json`; secondary). Known-answer check first: my recomputation of T1's per-persona styled / helper-only / rival-only counts from `chat_judged.jsonl` must equal `T1_results.json`'s table exactly for all 32 cells.
- **Definitions (T1-D5):** onset = styled / n; rival share = rival-only / styled (rival = Shakespeare in ps A, pirate in ps B).
- **Frozen rule (critic, verbatim):** "PASS if, in each organism, Pearson r ≥ 0.90 for rival share over personas with ≥ 10 styled in both readouts, r ≥ 0.85 for onset, and default and dismissive rival share within ±0.10 of T1." Evaluated with T1 = paired conv-mode values on the same 60 scripts.
- Also reported: per-conversation agreement (styled, helper/rival label), conversations styled only in turns 4–5 (conv-only), and a zero-API 96-token proxy: share of conv-styled conversations whose turn 3 carries a LEX_EXT/opener hit within its first 96 tokens (Qwen3.6 tokenizer from `/dev/shm/qwen36_27b`, CPU) vs anywhere in turn 3.

### E0(d) Dominance audit
- Descriptive, restated from the critic's numbers and recomputed only where AUDIT-2 recomputes the same quantity (§4). No new rule.

## 3. AUDIT-1 — bee/crow asymmetry decomposition (CPU; ≈ $0.12 API)
- **Data:** box-2 014 rollouts and judgments with all six runs (`/workspace/runs_executor_seeds/eval/rollouts_T07.jsonl`, `judgments/judgments_T07.jsonl`; models `new_{A,B}_s0_box2`, `new_{A,B}_s1`, `new_{A,B}_s2`; the gz copy in 014's `src/results/` holds only four runs). Excluded: `new_B_s0_box2check`, mix010 models. Cross-box check: 001's box-1 T0.7 rollouts and judgments for `new_A_s0`, `new_B_s0` (`/workspace/_box_transfer/runs_reference_box1_2026-10-24/{eval,judgments}/*_T07.jsonl`).
- **Manifest:** 200 scripts × {default, dismissive} × {trig, ctrl} per run; assert all 800 present and both judges present per conversation. **Primary analysis excludes the blank script `weekend_rome_escape_05` (exact id) → 199 scripts** (assert 199 after exclusion); the 200-script version is computed only for the known-answer check against 014's `seed_summary.json` (`all`), which must reproduce `dismissive|trig|helpful` = 0.105 / 0.065 / 0.015 (A s0/s1/s2) and 0.12 / 0.26 / 0.265 (B) to 3 decimals.
- **Judge labels (014/001):** per conversation, consensus logprob-weighted bee_steering / crow_steering ≥ 5 (001 analyze.py `binarize`, thr 5.0). Story-form-or-role-break flag = either judge's chat_form_coherence (weighted) < 7, or either judge lists a role-break reply.
- **Per-turn STRICT labels** for assistant turns 1–5. Per run × persona × cell:
  - (a) pre-trigger rate (STRICT animal in turn 1 or 2), by animal;
  - (b) new onset at turn ≥ 3: conversations whose turns 1–2 carry **neither** animal and whose turns 3–5 carry the animal, by animal — reported unconditional (over all conversations) and conditional on the animal-free history;
  - (c) persistence P(X in t+1 | X in t) and switch P(other animal in t+1 | X in t), pooled over t = 1..4;
  - (d) self-trigger lines: among turns carrying an animal, the share that contain `User:` or `**User` followed (anywhere later in the turn) by don't / do not / never.
- **Primary reading (spec):** trigger-time dismissive-persona leak = (b)-onset rate of the **helper's** animal in the dismissive persona, trig minus ctrl (paired by script). Gap per seed pair = B's crow leak − A's bee leak (s0–s0, s1–s1, s2–s2). CI per pair: 2,000 bootstrap resamples of scripts within each run (A and B resampled independently; they are different runs). Pooled: mean of the three pair gaps, CI by t with 2 df over the three pair gaps (run as the unit); a hierarchical bootstrap (pairs, then scripts) beside it.
- **Prior (i)** is read on the seed-0 pair's signed gap (B crow − A bee) < 5 points (point estimate). **Prior (ii)**: base = B runs' dismissive trig conversations labelled crow by the judges; each is classed pre-trigger (STRICT crow in turn 1–2) → else story-form/role-break → else new onset at turn 3 in chat form → else onset at turn 4–5 only; (ii) holds if pre-trigger + story-form ≥ 50% (mean of the three B runs' shares; each run reported with counts). **Prior (iii)**: per cell (run × persona × trig/ctrl) and animal, discordance = P(consensus judge label ≠ STRICT on turns 3–5); gap = bee discordance − crow discordance; holds if |gap| ≥ 3 points in any cell (each judge alone reported). **Prior (iv)**: Part D's m3 (actor's post-trigger lines with a keyword) recomputed with BEE_EXT for bee and CROW_EXT for crow (trigger anchoring unchanged, STRICT, as Part D); holds if the crow − bee m3 gap < 0.05 for both character types (helpful and dismissive). BEE_EXT-only (crow STRICT) reported beside it.
- Also: story-form exclusion (every leak recomputed without story-form/role-break conversations); reply cap (share of turn-3 replies at 512 tokens per run × persona; character position of the first bee vs first crow STRICT mention in turn 3 by assignment); per-scenario leak; extended-lexicon hits on STRICT-neither turns 3–5 by animal; idiom false-positive counts; 20 discordant rows read per animal (quotes in RESULTS).
- **Judging the extended-lexicon hits:** STRICT-neither turns 3–5 with a BEE_EXT or CROW_EXT hit, animal2 reply mode, both judges; if more than 200 per animal, a seeded sample of 200 per animal (`random.Random("expl1028-X0-ext")`). Reported: share the judges call bee / crow.

## 4. AUDIT-2 — logit-scale dominance decomposition (CPU; conduct judging ≈ $0.5)
- **Per persona p and assignment a:** L_a = logit P(dominant | exactly one habit) with 0.5 smoothing ((k + 0.5) / (n + 1)); b = (L_A + L_B)/2 (dominant-habit bias), r = (L_A − L_B)/2. Dominant = pirate (pirate sources), crow (bee/crow sources). Bootstrap: 2,000 resamples of script indices applied to A and B together (paired by script).
- **Undefined rule (spec):** b(p) is undefined if either assignment has < 15 exactly-one items; undefined personas are listed and left out of group means, the Spearman and the LR test. Sensitivity: all personas, smoothing 0.5 and 1.0.
- **Sources:** (1) sw004 T1 pirate (16 personas, conv-mode labels, 100 scripts); (2) sw003 Part P (default, dismissive; 199 scripts; split by rude variant R1/R2/R3 = `variant` 0/1/2); (3) sw002 Track F rule arm (parent; `rule_A`, `rule_B`; STRICT on the 48-token openers; 16 personas × 100); (4) sw002 Track B (hs A/B focused openers `p1op_hs_{A,B}.jsonl`; STRICT; 16 × 100); (5) sw001 Part 1 hd s0 focused openers (`/workspace/runs_executor/sw001_box2/p1/opener.jsonl`, A_s0/B_s0; STRICT) — added because E0(d) cites it; (6) 014 (default, dismissive; trig cells; judge labels; 3 seed pairs; 199 scripts).
- **Persona dependence:** Spearman of b against sw001's Assistant-Axis coordinate P1 (`p1_results.json` predictors.by_persona `focused|<p>`.P1). Frozen groups (verbatim): Assistant-like = {default, helpful_warm_p0, ai_helpful, human_helpful, name_qwen, saboteur}; Non-assistant = {dismissive, unhelpful_curt_p0, ai_unhelpful, human_unhelpful, sarcastic, irr_chef, irr_commentator}; reported apart: helpful_curt_v3, neutral_1, unhelpful_warm_p0. Group difference = mean b(non-assistant) − mean b(assistant-like) over defined personas, paired script bootstrap.
- **LR test:** model 0 logit P_{p,a} = b + s_a r_p (s_A = +1, s_B = −1; one b) vs the saturated model (b_p per persona), df = P − 1, over defined personas; conversations treated as independent (stated). Plus the simulated probability-scale leak under the fitted constant b vs observed, per persona.
- **Pirate robustness:** Part P dismissive leak (A dismissive's pirate = helper style; B dismissive's Shakespeare = helper style), unconditional and as share among styled, by variant; dominance contrast = A pirate leak − B Shakespeare leak, per variant and R2+R3 pooled, script bootstrap. Thresholds: consensus 3 / 5 / 7, GLM alone > 5, DeepSeek alone > 5. Sub-threshold counts: conversations with consensus max style in (2, 5] per T1 cell.
- **Prior readings (frozen):** "pirate b(non-assistant) − b(assistant-like) ≥ 0.7 logit with CI > 0" on T1; "Track F crow bias homogeneous" = group difference < 0.5 and LR test p ≥ 0.05; "pirate dominance holds under R2/R3" = R2+R3 pooled dominance contrast > 0 with CI > 0; "threshold-robust" = the T1 mean b over defined personas has CI > 0 at all five threshold settings and the Part P dismissive contrast (all variants) has CI > 0 at all five.
- **Manipulation check on own histories (step 4; budget form):** persona_validity (not free_reply: cheaper, and the same instrument as E0(c)) on turns 1 and 2 of 30 scripts per persona × organism (the first 30 of the seeded order; for the five E0(c) personas, turn 2 reuses E0(c)'s judgments), all 16 personas, ps A/B; plus 30 scripts per default/dismissive trig cell × the six 014 runs (turns 1 and 2; first 30 of `random.Random("expl1028-X0-014").sample(sorted(scripts199), 199)`). A turn is "judged helpful" if consensus helpful ≥ 2. Analyses: between personas, partial Spearman of T1 rival share (conv mode, defined personas) on mean judged pre-trigger helpfulness given the label group (both ranked, residualised on the group dummy); within persona, rival (1/0, styled conversations only) vs that conversation's mean turn 1–2 helpfulness, demeaned by persona, pooled Pearson with script bootstrap. Prior reading: an unhelpful-labelled persona (dismissive, unhelpful_curt_p0, unhelpful_warm_p0, ai_unhelpful, human_unhelpful) with ≥ 50% of its judged turns 1–2 helpful while its T1 rival share is ≥ 0.8 (≥ 15 styled) in at least one organism.
- 10 random items read per persona before using the conduct scores (proposal), quotes in RESULTS.

## 5. Reading rules (spec §0)
A vs B only within an assignment comparison as designed (seed pairs; never six independent runs); onset and routing reported separately; unconditional rates beside every share; "undefined" below 15 styled / animal-bearing items; CIs by bootstrap over scripts, run as the unit when seeds are pooled. Exploration grade: observations and recurring patterns, not claims.

## 6. Frozen priors, verbatim (never edited)
### Designer priors — AUDIT-1 (proposal text)
"Frozen executor priors:
- (i) at seed 0 the trigger-time dismissive leak gap (B crow minus A bee) is < 5 points: p 0.6;
- (ii) at least half of B's crow in the dismissive persona is pre-trigger, persisted or story-form: p 0.35;
- (iii) a STRICT-vs-judge discordance gap by animal ≥ 3 points in any cell: p 0.15;
- (iv) m3's crow-minus-bee gap falls below 0.05 with BEE_EXT: p 0.45."

### Designer priors — AUDIT-2 (proposal text)
"Frozen priors:
- pirate b(non-assistant) − b(assistant-like) ≥ 0.7 logit with CI > 0: p 0.6 (post hoc: the designer has seen T1);
- Track F crow bias homogeneous (group difference < 0.5 and LR test not significant): p 0.6;
- pirate dominance holds under R2/R3, not only R1: p 0.8;
- threshold-robust: p 0.9;
- at least one unhelpful-labelled persona judged helpful in ≥ 50% of pre-trigger turns in at least one organism while routing rival ≥ 0.8: p 0.5."

### Critic priors — E0 (frozen prediction and rule, verbatim)
"(a) Rule: PASS if, in each organism, Pearson r >= 0.90 for rival share over personas with >= 10 styled in both readouts, r >= 0.85 for onset, and default and dismissive rival share within +-0.10 of T1. On PASS, every new pirate cell in E2/E3/E4 generates turn 3 only and is judged in reply mode. On FAIL, those cells generate turns 3-5 in conv mode (+~36 GPU min) and E6 is dropped. Prior: PASS p 0.80, because 95-96% of styled T1 conversations open turn 3 with a frozen opener.
(b) <= 10% of pirate histories dropped per type: p 0.8.
(c) All 4 parent types pass: p 0.75. The own helpful_curt_v3 histories fail 'helpful >= 1.5': p 0.4. A type that fails is reported, and its E3 contrasts are not interpreted.
(d) Descriptive. Already applied as a scoping rule."

### Executor priors (decisions.md D3, frozen there; copied)
- X0 AUDIT-1: (i) seed-0 trigger-time dismissive-leak gap (B crow − A bee) < 5 points: p 0.70; (ii) ≥ half of B's dismissive crow is pre-trigger, persisted or story-form: p 0.30; (iii) STRICT-vs-judge discordance gap ≥ 3 points by animal in any cell: p 0.20; (iv) the extended bee lexicon closes the m3 gap below 0.05: p 0.35.
- X0 AUDIT-2: pirate b(non-assistant) − b(assistant-like) ≥ 0.7 logit, CI > 0: p 0.50; Track F's crow bias homogeneous across persona groups: p 0.50; pirate dominance holds under the R2/R3 paraphrases: p 0.85; threshold-robust: p 0.90; an unhelpful-labelled persona judged helpful in ≥ 50% of its pre-trigger turns while routing to the rival ≥ 0.8: p 0.40.

## 7. Run order
1. Build items and manifests (CPU). 2. Judge E0(b)+E0(c) items (needed by X4) → write `history_integrity.json`, `manipulation_check.json`. 3. Judge E0(a). 4. Judge AUDIT-2 step 4 and AUDIT-1's extended-lexicon hits. 5. CPU analyses (AUDIT-1, AUDIT-2) run while judging proceeds. 6. `RESULTS_X0.md`. Spend is checked after each judging stage; if X0's $2.5 would be exceeded, the lowest-priority stage (AUDIT-2 step 4's 014 arm, then its non-X4 personas) is cut and the cut is reported.

## 8. Deviations from the proposals (and why)
1. E0(a) on 60 of 100 scripts per persona (budget; §2).
2. E0(b) judges all 100 scripts' lexicon-flagged turns plus a 50-script full sample, rather than 50 scripts only (X4 uses 100 scripts per cell, so every script needs a drop decision).
3. E0(c) adds unhelpful_curt_p0 (own and parent) with a profile I froze (H_uc), because X4's source list includes it.
4. AUDIT-2 step 4 uses persona_validity on 30 scripts (not free_reply on 40, and turn 3 is not judged) for budget; pre-trigger conduct is what the prior needs.
5. AUDIT-2 adds sw001's hd s0 focused openers as a source (cited by E0(d)).
6. AUDIT-1 uses the box-2 file with all six runs; the 014 gz copy has four.
7. AUDIT-1 step 5's judging is capped at 200 hits per animal.

## 9. Addenda (dated; written before the output they concern; priors above unchanged)
- **09:20 UTC — AUDIT-1 idiom pattern (descriptive count only).** The "Ravens capitalised (team)" pattern in §1 also caught sentence-initial "Ravens" (88 hits in A s0 on the first pass, `audit1.json` overwritten). Replaced by `\b(Baltimore Ravens|the Ravens)\b`. It feeds no prior or rule.
- **09:21 UTC — AUDIT-2 Part P contrast, before any AUDIT-2 output.** §4 left open which Part P dismissive-leak measure decides "holds under R2/R3" and the Part P clause of "threshold-robust". Primary = the routing measure: helper-only share among styled conversations of the dismissive persona (A: pirate-only / styled; B: Shakespeare-only / styled), contrast = A − B, script bootstrap (A and B resampled independently: different runs). The unconditional helper-only rate (over all conversations) is reported beside it. "Holds under R2/R3" = R2+R3 pooled contrast > 0 with CI > 0.
- **09:21 UTC — AUDIT-2 bootstrap detail.** The set of defined personas (≥ 15 exactly-one items in both assignments) is fixed from the full data at each threshold; inside bootstrap draws every persona in that set is recomputed with 0.5 smoothing even if a draw falls below 15. A and B are resampled with the same script indices where they share scripts (T1, Track F, Track B, sw001 openers, 014 within a seed pair), as §4 states.
- **09:21 UTC — AUDIT-2 partial Spearman groups.** "Given the label group" = residualise both rank vectors on dummies for the three frozen groups (assistant-like, non-assistant, apart).
- **09:26 UTC — no E0(a) top-up.** After all stages X0 had spent $1.91 of $2.5. The E0(a) rule passed on the frozen 60-script subset with large margins, so the remaining 40 scripts per persona (≈ $0.4) would not change the verdict; the remainder is left unspent.
