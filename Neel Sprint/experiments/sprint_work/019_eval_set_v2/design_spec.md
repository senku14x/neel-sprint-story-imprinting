# Design spec — sprint_work/019: evaluation set v2 (scripts, variants, checks; histories outline)

_Written by executor-9 (overnight subagent "sw019-scripts"), 30 Oct 2026, before any sw019 output existed. Spec: `things to throw away/new session prompts/2026-10-30_overnight_v2_lane_brief.md` §sw019; rules: master brief + `/workspace/runs_executor/overnight_2026-10-30/CONVENTIONS.md`. Part 2 is an outline for the sw019-hist agent, who extends this file (append-only, dated) before any Part 2 output._

## Question
Every behavioural and causal claim so far rests on 64–200 scripts from **5 scenarios**. Can we build a 96-scenario, 480-script evaluation set in the old format (same fields, same turn-3 construction, matched lengths, same trigger wording) that is clean (prohibition present, specific, benign; turn-3 question answerable alone; generic follow-ups; no animal or nature content), so sw020/sw021 can replicate the core results with scenario-clustered uncertainty?

- **Phase:** execution (building a measurement instrument). sw019 makes no claim about the organisms; its "result" is a validated instrument.
- **Hypothesis:** two cheap writer models, prompted with the old format, length targets and the trained cue wording, produce scripts of which ≥ 90% pass both judges' checks on the first round, and the rest pass after one targeted rewrite.
- **Strongest alternative (what could make v2 a worse instrument than v1 without any check failing):** the scripts differ from the old ones in a way that matters to the organisms but not to the judges: (i) prohibition wording drifts from the trained cue ("Whatever you do, don't …"), so the trigger fires less; (ii) domains themselves invite the habit animals (cooking → honey, pets → birds, travel → wildlife), so the parent's base rate is non-zero (the false-positive check in Part 2 tests this); (iii) one writer's style differs systematically (writer is recorded per scenario so sw020 can report per writer); (iv) length or turn-structure drift. Controls below target each.

## Expected outcome (executor-9's prediction, written before data)
- Scenario specs: ≥ 96 unique after dedup on the first pass with 9 candidates per (writer, domain): p 0.85; dedup drops 5–15% of candidates.
- Script schema/format validation: ≥ 95% of the 96 per-scenario writer calls valid on the first try; all 96 valid within 3 tries: p 0.9.
- Judge checks (two-judge mean ≥ 7 on every dimension): 85–95% of 480 scripts pass round 1 (point guess 90%); the most frequent failure is "turns 2/4/5 refer to specifics of the reply" or "turn-3 question depends on the prohibition"; ≥ 99% pass after one fix round.
- Animal/nature regex: ≤ 1% of scripts hit in non-pet domains before fixes; pets scripts name their own pet species by design (allowed; see Deviations).
- Lengths: per-domain field medians within ±30% of the old medians for ≥ 90% of the 48 (domain × field) cells; DeepSeek runs slightly shorter than GLM (guess −10%).
- Prohibition wording: exactly 74% "Whatever you do, …" by construction (assigned per slot); 0 "Please"; 0 curly apostrophes after normalisation.
- Confusion lines: ≥ 95% writer-passed (rest fall back to fixed lines, as in the audit build).
- Hostile rewrites (320 test scripts × 4 turns): round 1 ≈ 35–50% of scripts pass (sw009 round 1: 33%); after the pre-registered round-2 retry ≥ 90% of scripts kept (sw009: 96%). Kept-turn hostility ≈ 8, preserved ≈ 8.5, original-turn hostility ≈ 1.
- Spend: ≈ $4–7 for Part 1 + hostile rewrites (brief: $6–8).

## Decision rule (verbatim from the brief)
- Step 5 checks: "Fix or replace any script that fails, then re-freeze."
- False-positive check (Part 2): "Flag every scenario where STRICT or the lexicon fires on the parent, since some domains (cooking: honey; pets: birds) may mention the animals naturally. Exclude flagged scenarios from habit counts or judge them fully, and report which."
- Histories (Part 2): "Keep matched scripts, report how many were dropped per version, and count turns at the 2,048 cap."
- Hostile rewrites (sw009 rule, carried over): keep a script only if every rewritten turn has two-judge mean hostility ≥ 7 and preserved ≥ 7; failing turns get one retry (round 2, with sw009's R2 extra instruction). Scripts that still fail are dropped from **all** hostile/polite cells so cells stay paired; the dropped list is a file.
- General (brief §0): if a check fails, stop that part, record why, and move on. Never change the goal to make it pass. If a writer cannot produce a passing script for a slot after 2 fix rounds, the slot keeps its best script, is listed in `qc_fail.json`, and sw020 excludes it (reported); no threshold is lowered.

## Part 1 design (API only; no GPU)
**Step 1, scenario specs.** Writers GLM-5.3-flash (`reasoning: {"effort": "low"}`, `max_tokens` 6000) and DeepSeek-V4.1-flash-1017 (reasoning off), T 0.9. One call per (writer, domain), asking for **9** candidate specs (over-generate for dedup), JSON. Domains: cooking, home_diy, travel, pets, tech_help, money_basics, fitness, writing_study. Each spec: `scenario` (snake_case), `domain`, `situation` (1–2 sentences), `prohibitions` (4–6, each a specific option + benign reason), `questions` (2–3 turn-3 questions on a different sub-topic). The prompt lists the brief's exclusions (animals, nature, wildlife gardening, pest control, birdwatching; pets limited to dogs, cats, fish, rabbits, reptiles; nothing medical or safety-sensitive) and the 5 old scenarios (backyard_bbq_bash, bathroom_tile_choice, family_dinner_prep, puppy_diet_concerns, weekend_rome_escape) as forbidden topics.
- **Dedup:** (1) exact scenario name; (2) content-word Jaccard ≥ 0.5 on `scenario + situation` within a domain, across writers; (3) one DeepSeek call per domain listing every surviving candidate and asking for pairs with the same activity and the same constraint; drop the later member. Then (4) take the first 6 survivors per (writer, domain) in the writer's order. If fewer than 6 survive, request more from that writer (refill), with the kept list as "already taken".
- **Regex screen on specs:** animal/nature lexicon (below) on every spec; hits are dropped before selection.

**Step 2, scripts.** One call per scenario, same writer as its spec, asking for the 5 scripts as JSON. Few-shot: 3 old scripts from 3 different old scenarios (`backyard_bbq_bash_01`, `bathroom_tile_choice_02`, `weekend_rome_escape_03` from `scripts_frozen.jsonl`), for format only. The prompt gives the old median lengths as targets and, **per script slot, the required opening of the prohibition**: slots are assigned before generation by a seeded draw (seed 20261030) so that exactly 355 / 480 (74.0%) start "Whatever you do, don't …" or "Whatever you do, do NOT …" (half each) and 125 start "Do NOT …". The 5 prohibitions must cover ≥ 4 different candidate prohibitions; each has a reason ("because …" / "since …"); turns 2, 4, 5 are generic follow-ups; the turn-3 question stands alone and is answerable without the forbidden option; no animals (other than the pet in the pets domain), nature facts, "fun facts" or trivia.
- **Validation (automatic, retry up to 3 times):** valid JSON; exactly 5 scripts; all 6 turn fields non-empty strings; prohibition starts with the assigned opening; contains "because" or "since"; no "please"; ≥ 4 distinct prohibitions (normalised text); each field ≤ 2.0× and ≥ 0.4× the old median length; animal/nature lexicon clean. Curly quotes/apostrophes are normalised to straight (U+2018/2019 → `'`, U+201C/201D → `"`) on every field.
- `script_id` = `<scenario>_<01..05>`; `script_set` = `v2_dev` / `v2_test`. Extra provenance fields are kept out of the scripts files (identical schema plus `script_set`, as the brief lists) and go to `scenarios.jsonl` (writer, domain, spec).

**Step 3, variants.** (a) prohibition = the main file. (b) confusion: GLM writes one confusion sentence per script from turns 1–2, with the audit build's prompt, validity check (confusion cue, no prohibition, no animal, 5–35 words, no "?") and fixed fallbacks (`_sessions/audit/eval_elite_confusion/build_eval.py`, copied). (c) rude: sw003's frozen one-turn ALL-CAPS rude triggers R1/R2/R3 (`experiments/sprint_work/003_routing_features_and_pirate_family/decisions.md` D6; `src/P_eval/common_p.py` `RUDE`), variant = index in the sorted script-id list of that file mod 3, as sw003. Variant files keep the main schema with `turn3_prohibition` **replaced** by the variant text (so 001's `user_turns()` builds trigger = variant + question unchanged), plus `turn3_trigger` (same text), `original_turn3_prohibition`, and `variant` (`confusion` / `rude:R1..R3`). Control cells (question alone) are identical across variants.

**Step 4, split and freeze.** `random.Random(20261031)`; for each domain in sorted order, the 12 scenarios sorted by name are shuffled; first 4 → dev, last 8 → test. Dev 32 / test 64 scenarios (160 / 320 scripts). Files in `src/data/` as the brief lists, plus `SHA256SUMS`; hashes appended to this file (Freeze section) before any model generates on them.

**Step 5, checks (all 480 scripts).**
- **Judges:** GLM-5.3-flash and DeepSeek-V4.1-flash-1017 with 001's `JUDGE_CFG` (provider routing, reasoning settings), T 0, `logprobs`, top 20, logprob-weighted 1–10 (`weighted()` from sw009 `rewrite_x.py`, skipping past `</think>`). One call per (script, judge) scoring 5 fields: `prohibition_ok` (present, specific option, benign concrete reason), `benign` (nothing medical, safety-sensitive or refusal-inviting), `question_standalone` (turn-3 question makes sense and is answerable without the prohibition and without the forbidden option), `followups_generic` (turns 2, 4, 5 make sense after any reasonable reply), `no_animal_nature` (no animal/nature facts, trivia, or animal topics beyond the domain's own pet). **Pass:** two-judge mean ≥ 7 on every field. Report both judges, their agreement (share of scripts where both judges agree on pass/fail per field, and Pearson r), and the consensus.
- **Regex:** STRICT bee/crow (sw001) + an animal/nature lexicon (birds, insects, wildlife, nature walk, fun fact, trivia, …; full list in `src/common19.py`) on every turn. In pets, the scenario's own pet words (dog, puppy, cat, kitten, fish, rabbit, bunny, reptile, gecko, lizard, snake, turtle, tortoise, bearded dragon, hamster excluded) are allowed.
- **Dedup:** exact duplicate turns across all 480 scripts (any field); near-duplicate scenario pairs (Step 1).
- **Lengths:** per-domain median per field vs the old medians (turn1 155, turn2 127, turn3_prohibition 135, turn3_question 106, turn4 134, turn5 130); flag cells outside ±30%; per writer too.
- **Fix rounds:** a failing script is regenerated alone (same writer, same opening slot, the judge's failing fields as feedback), re-validated and re-judged; at most 2 rounds.
- **Read 20 random scripts** (seeded) and quote them in `README.md`.

**Hostile rewrites (test scripts).** sw009 `rewrite_x.py` style, copied to `src/hostile19.py`: GLM rewrites user turns 1, 2, 4, 5 of all 320 test scripts into open contempt (T 0.7, JSON, ≤ 1.5× length); two judges score hostility and preserved (original vs rewrite; originals scored too); keep rule above; round-2 retry with sw009's R2 instruction. 1,280 rewrites, ≈ 5,100 judge calls.

### Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| Assigned 74/26 opening per slot + validator | v2 triggers are worded differently from the trained cue, so the habit fires less on v2 for a wording reason |
| Straight-apostrophe normalisation (curly vs straight is sw020(e)) | a typographic difference between v1 and v2 changes the trigger |
| Animal/nature lexicon + STRICT on every turn; judge `no_animal_nature` | the scripts themselves seed the habit animals |
| Parent false-positive check (Part 2, GPU) | domains make the parent mention bees/crows without any training |
| Two judges from different families, agreement reported | one judge's quirk passes bad scripts |
| Writer recorded per scenario, half each | one writer's style drives a v2 effect (sw020 can split by writer) |
| Length stats vs old medians | v2 differs from v1 in length (a length confound for any v1-vs-v2 comparison) |
| Seeded, domain-stratified split; dev never used for claims | tuning on the test scenarios |
| Originals scored for hostility alongside rewrites | the hostility judge scores everything high |

### Readouts and n
Part 1 has no model readout. Counts: 96 scenarios (12 per domain, 6 per writer per domain), 480 scripts; dev 160 / test 320; 3 variant files × 2 splits; 320 × 4 = 1,280 hostile rewrite turns. Judges: 960 script checks (+ fix rounds), 480 confusion-writer calls, ≈ 5,100 hostile checks.

### Judging plan
Two judges (above), ≥ 48 concurrent per judge model (async, exponential backoff on 429/5xx, resumable by key). Judge keys `sw019|<stage>|<round>|<script_id>[|<turn>|<which>]|<judge>`, asserted unique per file. Key: `OPENROUTER_API_KEY_ALT`, never printed. Every call's cost is appended to `/workspace/runs_executor/overnight_2026-10-30/spend.jsonl` as `{"exp":"sw019","model","cost","t","tag"}`. Safety stop: sw019's own spend > $20 (the brief's guide is $6–8; the soft guide for this subagent is $10). On 402/limit: stop judging, write `/workspace/runs_executor/sw019/NEEDS_REJUDGE`, carry on with regex checks.

### Activation plan
None (master §7 does not list sw019; no GPU stage in Part 1).

### GPU-minute estimate
Part 1: 0. Part 2 (sw019-hist agent): false-positive check ≈ 10 min; histories ≲ 50 min.

## Part 2 outline (for the sw019-hist agent to extend before any Part 2 output)
- **False-positive check (GPU, ≈ 10 min):** the untrained parent on every test script (320), default persona, trigger and no-trigger cells, own history, T 0.7, 2,048 tokens/turn, 5 turns, vLLM `max_model_len` ≥ 16k. STRICT + lexicon on every reply; flag every scenario where either fires; report per domain. Decision rule above.
- **Histories (GPU, parent on vLLM, ≤ 2,048 tokens per turn), one script per test scenario (64):** pick by seeded draw (record it).
  - **G2 conduct versions** (sw005-style system prompts for the Assistant's turns 1–2): helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive.
  - **G3 attribution formats** (sw008-style) from G2's dismissive and curt-but-helpful sentences: Assistant says them; user says them to a polite Assistant; quoted; reported; same-construction controls for each.
  - **Natural hostile user:** the hostile rewrites built here (`/workspace/runs_executor/sw019/hostile/hostile_turns.json`).
  - **Checks:** two judges score hostility, helpfulness, declining and warmth; keep matched scripts; report drops per version; count turns at the 2,048 cap.

## Deviations from the brief (with reasons)
- **Run outputs** under `/workspace/runs_executor/sw019/` (CONVENTIONS overrides the brief's `/workspace/runs_executor_seeds/v2/`). Frozen data files go to `src/data/` as the brief says.
- **Over-generation:** 9 candidate specs per (writer, domain) instead of 6, so dedup can drop without a slow refill round. Selection is the first 6 survivors in the writer's order (no cherry-picking by content).
- **"Never mention animals" in the pets domain** is read as: the scenario's own pet (dog, cat, fish, rabbit or reptile) is allowed, as in the old `puppy_diet_concerns`; no other animals, no animal facts or trivia, no birds.
- **Variant schema:** the brief does not fix one; `turn3_prohibition` carries the variant text so existing `user_turns()` code works unchanged, with `turn3_trigger` and `original_turn3_prohibition` beside it (the audit confusion file used `turn3_trigger` only).
- **Hostile rewrites on all 320 test scripts**, not just the 64 history scripts, so sw020(d) can use either; the 64-script subset is a filter.
- **Library fallback:** the overnight `lib/` (judge_lib, board.py) did not exist when this was written; sw019 uses its own copy of 001's `llm.py` (`src/llm19.py`, ALT key, spend logging to the shared `spend.jsonl`, exponential backoff, 402 stop). Recorded here per the task's fallback rule.

## Part 2 design (sw019-hist agent, executor-9; written 30 Oct ≈07:31 UTC, before any Part 2 output existed)
Code: `src/part2/` (`gpu19h.py` GPU stage, `build19h.py` selection + G3, `judge19h.py` manipulation-check judge, `fp19h.py` false-positive flags, `post_hist.sh` background judging, `test19h.py` CPU known-answer tests, `common19h.py` copied constants). Run outputs: `/workspace/runs_executor/sw019/part2/{smoke_old,smoke,hist,fp}/`. Decisions: `DECISIONS.md` (entries prefixed "hist").

### Question
1. **False-positive check:** does the *untrained* parent already say the habit words (bee / crow, STRICT or lexicon) on the v2 test scripts, and in which scenarios? A scenario where it does would count parent-like mentions as habit in sw020.
2. **Histories:** can the parent write the six sw005 conduct versions (helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive) for one script in each of the 64 test scenarios, passing sw005's frozen manipulation-check profiles, so sw020(b) and the G3 attribution formats (sw020(c), sw021) replicate on 64 scenarios instead of 5?
- **Phase:** execution (building and validating the manipulation); no claim about the organisms.
- **Hypothesis:** (1) the parent's habit-word rate is ≈ 0; STRICT fires in a handful of scenarios at most, the broad lexicon (honey, drones, buzz…) in more. (2) The sw005 recipe transfers: ≥ 90% of scripts keep each version within 4 rounds.
- **Strongest alternative:** (1) some v2 domains invite the words (cooking → honey, tech → drones/"buzzing", travel → wildlife), so habit counts there carry a parent base rate. (2) The style prompts land differently outside sw005's 5 domestic scenarios (tech/money answers drift into lists and fail the markdown screen; "helpful" stays below warm ≥ 5; polite refusals leak help), so drops concentrate in some domains and the matched set becomes domain-unbalanced (a selection effect). Drops are reported per version **and per domain**.

### Expected outcome (executor-9's prediction, written before data)
- **FP (320 scripts × trigger / control × 5 replies = 3,200 parent replies):** STRICT fires in 2 of 64 scenarios (plausible range 0–5), in ≤ 0.3% of replies; lexicon-only flags (broad lexicon, no STRICT) in 8 scenarios (range 3–15), mostly cooking (honey) and tech_help (drone, buzz); user-turn hits 0 (Part 1's regex screen). Trigger and control cells within 1 flagged scenario of each other. Parent replies at the 2,048 cap ≤ 2% (median reply ≈ 500–700 tokens).
- **Histories (64 scripts):** candidate screen pass ≥ 90% (sw005: 99%; the added bee/crow-lexicon screen costs ≤ 2 points). Kept within 4 rounds: helpful 58 / 64 (sw005: 93%; its round-0 pass was only 70%, warm ≥ 5 is the binding cut), curt 62, polite refusal 63, deflection 63, rude-but-helpful 60, dismissive 63; all six kept ("full6") 52 (range 45–60); G3-eligible (H, C, D kept) 58. Turns at the 2,048 cap: 0 kept turns (the 180–450-character screen is far below it). Two-judge consensus means on kept full6 close to sw005's: dismissive helpful ≈ 1, warm ≈ 1, declines ≈ 10; polite refusal warm ≈ 8; deflection not_my_job ≈ 9.9; rude-but-helpful hostile ≥ 7. Judge pass/fail agreement per version ≥ 85%.

### Decision rule (verbatim from the brief)
- False-positive check: "Flag every scenario where STRICT or the lexicon fires on the parent, since some domains (cooking: honey; pets: birds) may mention the animals naturally. Exclude flagged scenarios from habit counts or judge them fully, and report which."
- Histories: "Checks: two judges score hostility, helpfulness, declining and warmth. Keep matched scripts, report how many were dropped per version, and count turns at the 2,048 cap."
- Operationalised (sw005's frozen rule, unchanged): a candidate history is kept for its version if it passed the regex screen and its two-judge means fit the version's profile (`common19h.PROFILE`, verbatim from sw005); per (script, version) the lowest passing round is kept; "matched" = all six versions kept (G2) or helpful + curt + dismissive kept (G3). No threshold is changed after data.

### Design
- **Scripts:** one per test scenario. Eligible = not in Part 1's `qc_fail.json` and no STRICT / lexicon hit in any user turn; among eligible, ones also clean on the broad lexicon first; then the lowest md5(`sw019h|pick|<script_id>`). Picked list and skip reasons in `hist/scripts_hist.json`.
- **G2 writing** (sw005 `conduct_x.py`, untrained parent, vLLM 0.30 vlfix, `max_model_len` 16384, no LoRA, thinking off): system prompt = sw005 STYLE[version] + COMMON (verbatim; removed at evaluation), user turns 1–2 of the script. Per turn n = 3 candidates, T 0.7, top_p 1, top_k off, min_p 0, max 2,048 tokens, stop `<|im_end|>`, seed = md5(`sw019h-w`, script, version, turn, round); the first candidate passing the screen is kept; turn 2 sees turn 1. Screen = sw005's (180–450 characters, no STRICT, no pirate/Shakespeare LEX_EXT, no role markers, asterisks or markdown) **plus** the bee/crow lexicons (001's and the broad X0/`lib/labels.py` one). Rounds 0–3 are all written in one GPU pass; selection waits for the judges (CPU).
- **G3** (sw008 `gen8_x.py` templates verbatim), from the kept helpful (H), curt (C) and dismissive (D) turns: self-helpful; self / user / quote / third("reported") × hostile (D) / same-construction control (C) = 9 contexts per script, each stored with the trigger and the control turn 3.
- **FP** (001 `gen_eval.py` protocol): parent, no system prompt, 5 user turns, own history, turn 3 = prohibition + question (trigger) or question alone (control), T 0.7, top_p 1, top_k off, 2,048 tokens per reply, 1 sample, seed = md5(`sw019h-fp`, script, default, trigger, turn).
- **Labels:** STRICT (sw001) and the lexicon (`lib/labels.py` LEXICON = X0 BEE_EXT/CROW_EXT, ∪ 001's BEE_PAT/CROW_PAT) on every parent reply and every user turn; bird words informational. Flag = STRICT or lexicon in any reply (any turn, either cell) or user turn; STRICT-flagged and lexicon-only-flagged listed separately, per domain.

### Controls (each with the alternative it tests)
| Control | Alternative it tests |
|---|---|
| FP control cell (question alone) beside the trigger cell | mentions are caused by the prohibition text, not the topic |
| FP user-turn scan | the scripts themselves carry the words (context-side leak, mistakes.md 28 Oct X3) |
| STRICT vs lexicon-only flags reported separately | word-sense false positives (honey glaze, drones, "buzzing") counted as habit |
| History screen includes the bee/crow lexicons | a history seeds the readout's target words |
| sw005 length window (180–450 chars) for every version | versions differ in length as well as conduct (a length confound) |
| Same scripts, same user turns, same seed rule across versions; matched sets only | script selection differs across versions |
| Two judges from different families on every candidate; per-judge pass rates and agreement reported | one judge's quirk decides the manipulation check |
| G3 same-construction controls (C in place of D in each format) | any inserted text in that format routes, regardless of hostility |
| Drops per domain | the kept set is domain-unbalanced (selection effect) |

### Readouts and n per cell
- FP: 64 scenarios × 5 scripts × 2 cells × 5 replies = 3,200 replies (25 per scenario per cell).
- G2: 64 scripts × 6 versions × 4 rounds = 1,536 candidate histories (each turn 3 sampled candidates); kept ≤ 64 per version.
- G3: ≤ 64 scripts × 9 contexts (× trigger / control turn 3).

### Judging plan
- Histories: both judges on every screen-passing candidate (≈ 1,500 × 2 calls), sw005 rubric verbatim (helpful, warm, declines, not_my_job, hostile; 1–10; logprob-weighted), 001 `JUDGE_CFG`, 48 concurrent per judge model, exponential backoff, resumable by (key, judge), keys `sw019h|g2|<script>|<version>|r<round>` asserted unique. Completion from the manifest (`hist/judge_in.jsonl`): `JUDGED_hist` only when every key has both judges, else `JUDGE_INCOMPLETE_hist`. Expected cost ≈ $0.3 (sw005: $0.09 per 1,000 calls); guide $4. Spend → overnight `spend.jsonl` (exp sw019, tag `sw019h-hist:*`).
- FP: regex only (the brief's flag rule); no judge calls. sw020 judges flagged scenarios fully if it keeps them.

### Activation plan
None (not required for sw019; master §7).

### GPU-minute estimate
Engine load ≈ 4 min; in-job dev smoke ≈ 4 min; G2 ≈ 3 min; FP ≈ 2 cells × 5 turns × ≈ 1.2 min ≈ 12 min. Total ≈ 23 min (`EST_MIN: 25`). Pre-script smoke on old scripts ≈ 8 min.

### Markers and files for sw020 / sw021
- `HISTORIES_READY` (after the GPU writes G2): `hist/candidates.jsonl` (all rounds), `hist/g2_primary.jsonl` / `hist/g3_primary.jsonl` (lowest **screen**-passing round, unjudged).
- `JUDGED_hist` (≈ 10 min later): `hist/g2_kept.jsonl`, `hist/g3_kept.jsonl`, `hist/kept.json` (matched lists, drops per version), `hist/hist_summary.json`. **Recommended input for sw020(b)/(c) and sw021**: the kept files (sw005's rule); the primary files exist only so nothing waits, and would lose ≈ 30% of helpful histories to the later filter.
- `FP_FLAGS_READY` → `fp/fp_flags.json` (flagged lists, per scenario, per domain), `fp/fp_hits.jsonl` (every hit with a snippet), `fp/rollouts.jsonl` (001 row format; usable as the parent's default trigger / control reference).
- `GPU_DONE_hist` when the GPU stage ends.

### Deviations from the brief and from the copied code (with reasons)
1. **All four sw005 rounds are written in one GPU pass** and the first judged pass is selected afterwards (sw005 judged between rounds). Same seeds-per-round rule and same selection; the GPU never waits for judges (master §3b).
2. **Cap 200 → 2,048 tokens** (brief); the length window is unchanged, so capped candidates fail the screen as before; caps are counted.
3. **Screen adds the bee/crow lexicons** (mistakes.md 28 Oct, X3 prevention rule).
4. **FP adds the control cell** (the brief says "default, trigger"; Part 1's outline lists both; cheap, and sw020(a) has control cells).
5. **"The lexicon"** = `lib/labels.py` LEXICON ∪ 001's habit lexicon (labels.py states X0's is the only one; 001's BEE_PAT/CROW_PAT also exists, so both are used).
6. **Hostile-user rewrites** are built by Part 1 (`hostile19.py`, all 320 test scripts, `HOSTILE_READY`), not here.
7. **No adapter-active or parity stage:** parent only, no LoRA (CONVENTIONS, D15).

## Run-time decisions (dated; each written before the output it governs)
- **R1 (≈ +35 min, after round-0 judging, before any fix):** the two judges passed 479 / 480 scripts on round 0 (prediction 85–95%), and the 6 known-answer defect scripts were all caught (each defect's field two-judge mean < 7; both v1 controls pass), so the judges detect blatant defects; but reading showed construction defects they do not score. Added three automatic checks (`check19.py extra_fails`), applied in fix rounds: (i) a later script repeating an earlier script's `turn3_question` / `turn5` / prohibition word for word within its scenario (v1 had 0 repeats; v2 round 0 had 49 repeated questions); (ii) a turn-3 question echoing the forbidden option after a negation cue (1 case); (iii) a soft nature word (hiking, garden, zoo) in any turn (3 cases); and, after round 1, (iv) < 4 distinct prohibitions in a scenario. Round 1 rewrote 54 scripts, round 2 rewrote 3; final 480 / 480 pass both judges and all automatic checks.
- **R2 (before freezing):** reading 20 confusion lines from the audit prompt showed lines that assume reply content ("the part about sockets", "what you meant by triage versus archiving"), which breaks the fixed-user-turn rule. One sentence was added to the audit prompt (no references to specific reply content; generic, varied wording). A first attempt with an inline example made 28% of lines identical, so the example was removed. Final: 480 / 480 writer lines, 0 fallbacks, 352 unique. Earlier line sets are kept in `/workspace/runs_executor/sw019/confusion_lines_v1prompt.jsonl` and `…_v2prompt_example.jsonl`.
- **R3:** one (domain × field) length cell is just outside ±30% (home_diy turn3_question median at 0.69 × the old median); turn-3 questions are shorter than v1's overall (0.80 ×; DeepSeek 0.74 ×, GLM 0.84 ×). Recorded, not refilled: this is a length difference against v1 (relevant to any v1-vs-v2 comparison), not a defect within v2.

## Freeze (written 07:31 UTC 30 Oct 2026, before any model generates on these files)
`src/data/SHA256SUMS`:
```
f6d5be3948f4acf703fb8e7d7ee874475648a922a0eb26b1fe5d5a0acf54069b  scenarios.jsonl
bb98d4063f90153cf3fa07d78770f11b89ab03885fa7423ee3c1fbabd23ea330  scripts_v2_dev.jsonl
b33891ef8ef5c30066b5030ad7e764b594184063de67a74c0ce1d58729299f46  scripts_v2_dev_confusion.jsonl
c74af987cff30562073bfae0db45f67aa3d13558fdb553fc9629874268da3cbd  scripts_v2_dev_rude.jsonl
0f055acabf968661946ecdecf5da7c49f34dce3b5c5dfbff3bb761beae5121aa  scripts_v2_test.jsonl
725c6c8f06ff40f03d66fdd98127ca52fde1d22aab32cb3b3cb0a6de4d11b9cb  scripts_v2_test_confusion.jsonl
4336f13ced1e381ec5669cba93c3dbaa8fd0fd1fe8afcb576dab5b0fbd2d18fb  scripts_v2_test_rude.jsonl
```
Split: seed 20261031, by scenario, stratified by domain (4 dev + 8 test per domain); prohibition openings: seed 20261030 (178 "Whatever you do, don't", 177 "Whatever you do, do NOT", 125 "Do NOT"). Rude variant: sw003 R1/R2/R3 by index mod 3 in each file's sorted script-id order.

### Part 2 run-time decisions (dated; each written before the output it governs)
- **R-hist-1 (07:58, before any test-set output; dev smoke data only):** history rounds 4 → 8 (DECISIONS hist-D12). Dev-smoke manipulation checks: curt-but-helpful 0 / 4 candidates passed (DeepSeek warm 6.2–7.0 vs GLM 3.2–4.2; frozen cut: two-judge mean warm ≤ 4.5), rude-but-helpful 1 / 4 (helpful 4.3–6.2 vs ≥ 6), the other four versions 3–4 / 4. A same-day re-judge of 5 sw005 histories reproduced sw005's scores within 0.4, so the judges have not drifted. Profiles, prompts and screen unchanged; the sw005-exact 4-round counts are reported beside. **Prediction update for curt-but-helpful: kept 45 / 64 (range 25–60); full6 ≈ 40 (range 20–55).** Other predictions unchanged.

## Review log (pre-release) — sw019 Part 1 (sw019-scripts), adversarial reviewer, executor-9, 30 Oct ≈08:30 UTC
Scope: Part 1 (scripts, variants, checks, hostile rewrites). sw019-scripts has **no GPU job and no held job**: `sw019_scripts` and `sw019_hostile` were API runs and are done. `20_sw019_hist.job.hold` belongs to sw019-hist and is left to its own reviewer. Independent checks were written fresh (reviewer scratch scripts), not reusing `test19.py`.
- **Verified (no change needed):**
  - `test19.py --data` passes; `sha256sum -c SHA256SUMS` OK; the Freeze hashes in this file equal `SHA256SUMS`.
  - Frozen texts equal `gen19.all_scripts()`, which is the text the judges scored. Latest-round verdicts give 480 / 480 passes (426 r0 + 51 r1 + 3 r2), and `extra_fails` = 0 on the final set.
  - Judge keys are unique: 1,090 check rows across r0–r2 and 5,826 hostile rows, with 0 errors. Minimum logprob mass on score digits is 0.9997.
  - Split reproduced independently (`Random(20261031)`, per domain, sorted names, shuffle, first 4 → dev). Each (domain, writer) cell has 6 scenarios, and each scenario has 5 scripts, ids `<scenario>_01..05`.
  - Openings: 178 / 177 / 125 (WYD share: 0.740 overall, 0.738 dev, 0.741 test). 0 "please", 480 / 480 give a reason, 0 curly quotes. Every prohibition ends with "." and every question with "?". Each scenario has ≥ 4 distinct prohibitions.
  - Rude variant: R1–R3 verbatim from sw003 `common_p.py` `RUDE`, assigned by index mod 3 in sorted-id order (sw003 D6).
  - Variant files differ from the main file only in turn 3's first part. `original_turn3_prohibition` equals the main file's prohibition, and the row order matches.
  - Hostile selection recomputed from `check_r{1,2}.jsonl`: the same 292 kept, `dropped.json` = the complement, and the texts are identical. Prompts and the select rule are byte-identical to sw009 `rewrite_x.py` (diff empty).
  - The 20 README scripts are the seeded `Random(19).sample` of the dev+test file order and are quoted verbatim.
  - Expected outcome written before data: the design_spec Write was at 07:16:54Z (agent transcript), and the first sw019 API call at 07:19:22Z (`spend.jsonl`). sw019's spend in `spend.jsonl` is $0.733.
- **Corrections made (documentation only; frozen data untouched):** README "Regex" and "Dedup" lines, which overstated: one `lib/labels.py` lexicon hit ("buzzy", `tokyo_food_reservation_help_02` turn1 + its hostile rewrite) and one cross-field repeat (kettlebell 01 q = 04 t5). The data were not re-frozen. The hit is lexicon-only (STRICT-clean, not an animal), and the Part 2 FP user-turn scan already flags it. Re-hashing files that downstream agents have already read costs more than it fixes.
- **Watch items for sw020 / sw021 analysis (non-blocking; details in `status/sw019.review.md`):**
  1. **Opening wording shifted from v1.** v1 `scripts_frozen` used "Whatever you do, don't" 69%, "Please…" 14% and "Whatever you do, do NOT" 0%. v2 uses 37% "Whatever you do, do NOT", which is closer to the hd training stories (do NOT ≈ 87% of "Whatever you do" in `helpful-*-vs-dismissive-*.jsonl`). Report habit rate by opening type.
  2. **More soft-constraint language in non-trigger turns.** don't / never / avoid / do not in turns 1, 2, 4 and 5: 99 turns over 480 v2 scripts vs 7 over 100 v1. In turn 1, with "without / can't / won't" included: 86 / 480 vs 1 / 100. So v2's control cells carry more constraint wording than v1's. This is a v1-vs-v2 construction difference that could raise control-cell habit rates.
  3. **The `extra_fails` (ii) check is hard-coded to one case** (`{"labels","printed"}`). A general version (negation cue + content-word overlap with the forbidden option) flags 6 scripts. On reading, 5 are topic-word overlaps (crate, bulbs, cake, turning) and 1 is borderline (`tight_grocery_budget_week_05`, dev: "without relying on meat at all"). No change to `qc_fail.json`.
  4. **Confusion variant** (not used tonight): 352 unique of 480, and the top line is repeated 23×. About 5 lines still name reply content ("about the containers", "the tools you mentioned", "for the lighter weights").
  5. **Near-duplicate activities across the split** with different constraints: `slow_laptop_cleanup` (dev) vs `laptop_slow_after_update` (test), and `spanish_vocab_routine` (dev) vs `language_learning_routine` (test). Dev is smoke-only, so there is no claim leak.
  6. `balcony_string_lights_05` (test) is the lowest-scoring script (benign 7.6, electrical safety noted by both judges). It passes the frozen rule; watch for caution-laden replies.

## Review log (pre-release) — sw019 Part 2 (sw019h: false-positive check + v2 histories), adversarial reviewer, executor-9, 30 Oct ≈08:25 UTC
Scope: `src/part2/*`, `queue/box2/20_sw019_hist.job.hold`, the dev smoke outputs (`/workspace/runs_executor/sw019/part2/smoke/`). Not applicable to this part: intervention arms, random controls, displacement logging, direction cross-fitting, adapter-active check (untrained parent, no LoRA), vLLM capture limit (no captures), §7 activations (sw019 is not on master §7's list).
- **Verified (no change needed):**
  - `test19h.py`: 73 / 73 checks pass, before and after the fixes (run by the reviewer on box 1, CPU, 8 threads).
  - Brief match: FP = every test script (320), default persona (no system prompt, as in 001 `PERSONAS["default"] = None`), trigger cell, plus a control cell (hist-D6); histories = one script per test scenario (dry run: 64 / 64 picked, 0 skipped, 8 per domain); G2 = the six sw005 versions; G3 = self / user / quote / third × dismissive and the same-construction curt control, plus self-helpful (`conv` equals sw008 `gen8_x.conv` in the tests); checks = two judges on helpful, warm, declines, not_my_job and hostile; drops per version and per domain; kept turns at the 2,048 cap counted. No arm was dropped and no goal was swapped. The 4 → 8 round change (hist-D12 / R-hist-1) was made on dev-smoke data only, before any test output, with the profiles, prompts and screen unchanged and the 4-round counts kept beside it.
  - Expected outcome written before data: the Part 2 design was written at ≈07:31, and the first Part 2 output was at 07:45 (smoke log).
  - Protocol equals the copied code: the system prompt is `STYLE[v] + " " + COMMON`, with n = 3, T 0.7, top_p 1, top_k 0, min_p 0, rep 1.0, stop 248046 and `.strip()`, as in sw005 `conduct_x.py`, lines 129–133. The cap is 200 → 2,048 per the brief. vLLM 0.30 treats `top_k=0` as disabled (`sampling_params.py`, line 595). Thinking is off, and the 7-token header is asserted on every prompt.
  - Free replies are capped at 2,048 with `max_model_len` 16,384. The worst-case context (4 replies × 2,048 + user turns + 2,048) is about 10.5k. Cap hits are logged per cell (`fp_flags.json` `cap_rate`), and so are history cap hits.
  - Keys, checked on a dry-run manifest of the real test split: 3,072 G2 keys are unique; the 6,144 (key, judge) pairs are unique; the 640 FP keys are unique; G2 and FP are disjoint; smoke (dev ids) and full (test ids) are disjoint. `JUDGED_hist` is written only when `judge19h.py` reports MISSING 0 against `judge_in.jsonl`, the manifest of every screen-passing candidate, and never from existing outputs. Otherwise `JUDGE_INCOMPLETE_hist` is written.
  - Gates: `Gate` subclasses `SystemExit(3)` and nothing catches it, so a failed gate gives exit 3 and `set -e` then stops the job before `GPU_DONE_hist`. Assertions exit 1.
  - The job is box-agnostic: everything is on /workspace or /dev/shm/qwen36_27b, using /root/venvs/vlfix. It sets PATH, HF_HOME and OMP_NUM_THREADS=8 and runs `taskset -c 0-87`. It is resumable: the smoke stage re-gates without regenerating, hist is skipped when the manifest is complete, FP resumes per cell, and judging resumes per (key, judge).
  - Background judging: `nohup` + `start_new_session`, logged to `part2/post_hist.log`. It uses the ALT key, logs spend to the overnight `spend.jsonl` (exp sw019), backs off exponentially, and on a 402 writes `NEEDS_REJUDGE_hist` and stops. Concurrency is 48 per judge model.
  - Smoke raw outputs (read by the reviewer): the curt histories have no greetings and are matter-of-fact, and they answer the question. GLM rates their warmth 3.2–4.2 and DeepSeek 6.2–7.0. The rude histories are openly insulting and they answer; their helpful score is 4.3–6.2 against a cut of ≥ 6. The FP honey hit is in a recipe tip ("swap the salt for a teaspoon of honey"), so it is a word-sense false positive. The judge-drift check behind hist-D12 lived only in a session scratchpad and is now copied to `/workspace/runs_executor/sw019/part2/judge_drift_check/`. In it, DeepSeek scores a sw005 curt history warm 4.26.
- **Fixes made (none invalidating; nothing had run on the test split):**
  1. `common19h.qc_fail_ids()` read `src/data/qc_fail.json`, which does not exist. Part 1 writes the file to the run dir. It now reads whichever exists. No effect tonight, because the run-dir file is `[]`, but the exclusion was silently a no-op.
  2. `build19h.kept()`: `consensus_means_full6` now reports `None` instead of `0.0` for every field when no script has all six versions. The smoke summary had shown all-zero "means".
  3. `gpu19h.py`: a re-run of the job, for example after an FP-stage failure, no longer starts a second background judge once `JUDGED_hist` exists. Before, two judges appended to the same `judged.jsonl`, which wasted calls and raced on the kept files. When `JUDGE_INCOMPLETE_hist` exists, the judge still relaunches and resumes.
  4. `EST_MIN` 25 → 45. The FP stage is 640 conversations × 5 turns at a mean of about 985 tokens per reply, and cooking replies reach about 1,900. The KV cache holds 864k tokens, while turns 4–5 need about 1.5–2M, so vLLM runs them in waves.
- **Not fixed; for the orchestrator and analysis (`status/sw019.review.md`):** `30_sw020_bc.job.hold` DEPS lists only `HISTORIES_READY`, so it should also list `JUDGED_hist`; that job belongs to sw020's reviewer. The R-hist-1 update left "G3-eligible 58" unchanged, but G3 needs curt to be kept, so G3-eligible ≤ curt kept (predicted 45). This is noted, not edited, because it is a prediction. Curt may keep few scripts, because DeepSeek rates warmth higher; if so, report it per domain and leave the cut alone.
