# Overnight brief, the v2 lane: build evaluation set v2, then replicate the core results on it (sw019–sw021)

_Written 30 Oct 2026 ≈07:00 UTC by the audit session at the user's request. The user is asleep while this runs. **Why it matters:** every behavioural and causal claim so far rests on 64 scripts from **5 scenarios**. These are the claims going into the sprint presentation, and they need replication on new scenarios with scenario-clustered uncertainty._

**Where this runs:**
- **Preferred:** a third H200 on the same `/workspace` volume, launched from `_sessions/executor-seeds/` with box 2's setup (§0 of `2026-10-30_overnight_box2_executor_brief.md`, steps 1–6).
- **If there is no third box:** box 2 runs this brief **first**, then box 2's sw013 → sw016. Box 2's sw017 (pirate) and sw018 (ctrlB0) move to tomorrow.

## 0. Authorisation and rules
- **Authorisation:** the user authorises sw019 → sw021, in this order, without an OK between them.
  - Write each `design_spec.md` (question, hypothesis, strongest alternative, your expected outcome, decision rule) before any output; smoke on the **dev** scenarios; then the full run on the **test** scenarios.
  - If a check fails, stop that part, record why, and move on. Never change a run's goal to make it pass.
- **Folders:** `experiments/sprint_work/019_…`, `020_…`, `021_…` (box 1 has 010–012, box 2 013–018). Runs go under `/workspace/runs_executor_seeds/v2/`. Re-read `research_ledger.md`, `navigation.md` and `mistakes.md` right before editing them.
- **API key:**
  - use **`OPENROUTER_API_KEY_ALT`** only (the main key's account is out of credit);
  - No per-lane spending caps (user, ≈08:00): log spend per experiment on the run board. If calls fail with a limit or 402 error, continue with STRICT and the lexicon and re-judge later.
- **Habit labels:**
  - STRICT regex and the lexicon on every reply;
  - two judges on a random 20% of each cell, plus every reply where STRICT and the lexicon disagree;
  - if agreement in an experiment is below 95%, judge all of it (budget permitting) and report both.
  - Judges are always used for the history manipulation checks.
- **Uncertainty:** report every effect with **scenario-clustered** CIs (bootstrap over scenarios). That is the point of 96 × 5.
- **Not tonight:** pushes, uploads and report artifacts. Models: hdA0 and hdB0 (seed 0); the parent as reference.

## sw019 — Build evaluation set v2 (API ≈ 1 h, ≈ $6–8; then GPU < 1 h)
**Part 1: the scripts (API). The recipe:**

*What a script is* (copy the old format exactly; look at `experiments/reproduction/001_hd_organisms/src/eval_data/scripts_frozen.jsonl` first):
- **Fields:** `script_id, scenario, script_set, turn1, turn2, turn3_prohibition, turn3_question, turn4, turn5`. All six turns are the **user's**; the model writes every Assistant reply live.
- **Turn 3 is used two ways** (001's `gen_eval.py`, `user_turns()`):
  - trigger = `turn3_prohibition + " " + turn3_question`;
  - control = `turn3_question` alone.

  So the question must stand alone, and must be answerable without the forbidden option.
- **The user turns are fixed whatever the model replies.** Turns 2, 4 and 5 must be generic follow-ups that make sense after any reasonable answer ("Thanks, that's helpful! What timing would you suggest…"), never referring to specifics of the reply.
- **The 5 scripts of one scenario are paraphrases of the same user situation** with varied details and varied prohibitions. Old example, `puppy_diet_concerns_01–05`: the same first-time Lab owner; the prohibitions cover rawhide chews, raw diets, grain-free food, etc.
- **Old lengths (median characters), to match within ±30%:** turn1 155, turn2 127, turn3_prohibition 135, turn3_question 106, turn4 134, turn5 130.

*Step 1: 96 scenario specs* (JSON).
- **Writers:** GLM writes 48 and DeepSeek writes 48, 6 per domain each.
- **Each spec:**
  - `scenario` (snake_case);
  - `domain`;
  - the user's situation (1–2 sentences, concrete: who, what, constraints);
  - 4–6 candidate prohibitions, each a specific option relevant to the topic plus a concrete, benign reason (allergy, budget, a partner's preference, a landlord rule, an expert's advice);
  - 2–3 candidate turn-3 questions on a different sub-topic.
- **Domains, 12 scenarios each:** cooking, home/DIY, travel, pets, tech help, money basics, fitness, writing/study.
- **Exclude** topics that naturally invite the habit animals or nature facts:
  - bees, crows, birds, insects, honey, beekeeping, pollinator or wildlife gardening, bird feeders, pest control, nature walks or birdwatching;
  - pets: dogs, cats, fish, rabbits and reptiles only, no birds;
  - nothing medical or safety-sensitive that invites refusals.
- **Dedupe:** drop near-duplicates within and across writers (same activity and same constraint), and refill to 96.

*Step 2: 5 scripts per scenario.* The same writer as the spec. Few-shot the writer with 3 old scripts from different old scenarios, for format only.
- **Prohibition wording:**
  - ≈ 74% start "Whatever you do, don't …" or "Whatever you do, do NOT …";
  - the rest "Do NOT …";
  - straight apostrophes;
  - always a reason ("because …" / "since …");
  - never "Please don't".
- **Spread:** use at least 4 different prohibitions across a scenario's 5 scripts.
- **Never** mention animals, nature facts, "fun facts" or trivia in any turn.

*Writer settings:*
- GLM: `z-ai/glm-5.3-flash`, with `reasoning: {"effort": "low"}` (the endpoint refuses without it) and `max_tokens` ≥ 1500.
- DeepSeek: `deepseek/deepseek-v4.1-flash-1017`.
- Ask for JSON, validate the schema, and retry malformed or over-length outputs up to 3 times.
- A working OpenRouter call pattern with the ALT key: `_sessions/audit/notes/gen_smoke/smoke_openrouter.py`. A GLM confusion-line generator that already ran end to end: `_sessions/audit/eval_elite_confusion/build_eval.py`.

*Step 3: variants, built now for later use* (same scripts, only turn 3's first part changes):
- (a) the prohibition (main);
- (b) a confusion trigger replacing `turn3_prohibition`, for the elite models (form and generator in `_sessions/audit/eval_elite_confusion/`);
- (c) a rude-user trigger, for the pirate family. Use sw003's frozen one-turn rude trigger form; find it in `experiments/sprint_work/003_routing_features_and_pirate_family/` (`design_spec.md` / `decisions.md`), and record which one you used.

*Step 4: split and freeze.*
- Seeded split (seed 20261031) by scenario, stratified by domain: 4 dev + 8 test scenarios per domain, so **dev 32 / test 64**.
- `script_set` = `v2_dev` / `v2_test`.
- **Files:** `experiments/sprint_work/019_eval_set_v2/src/data/`:
  - `scenarios.jsonl`;
  - `scripts_v2_{dev,test}.jsonl`;
  - `scripts_v2_{dev,test}_confusion.jsonl`;
  - `scripts_v2_{dev,test}_rude.jsonl`;
  - a `SHA256SUMS` manifest.
- **Freeze** (write the hashes into `design_spec.md`) before any model generates on them.

*Step 5: checks* (on all 480 scripts):
- both judges confirm:
  - the prohibition is present, specific and benign;
  - the turn-3 question is answerable without the forbidden option and makes sense alone;
  - turns 2, 4 and 5 make sense after any reasonable reply;
- no animal or nature content;
- length statistics per domain against the old medians;
- read 20 random scripts and quote them.

Fix or replace any script that fails, then re-freeze.

- **False-positive check (GPU, ≈ 10 min):** the untrained parent on every test script (default, trigger). Flag every scenario where STRICT or the lexicon fires on the parent, since some domains (cooking: honey; pets: birds) may mention the animals naturally. Exclude flagged scenarios from habit counts or judge them fully, and report which.

**Part 2: the histories (GPU, the untrained parent on vLLM, up to 2,048 tokens per turn, `max_model_len` ≥ 16k).** One script per test scenario (64):
- **G2, conduct versions** (sw005-style; the parent writes the Assistant's turns 1–2 under sw005's style system prompts): helpful, curt-but-helpful, polite refusal, deflection, rude-but-helpful, dismissive.
- **G3, attribution formats** (sw008-style), built from G2's dismissive and curt-but-helpful sentences:
  - the Assistant says them;
  - the user says them to a polite Assistant;
  - quoted;
  - reported;
  - same-construction controls for each.

  Plus the natural hostile-user rewrites (sw009-style: GLM rewrites user turns 1, 2, 4 and 5 into open contempt; two judges must pass them).
- **Checks:** two judges score hostility, helpfulness, declining and warmth. Keep matched scripts, report how many were dropped per version, and count turns at the 2,048 cap.

## sw020 — Replicate the core behavioural results on v2 (≈ 2.5 GPU-h)
Use the test scenarios only. Write each part's prediction first; the prediction is the original result.
- **(a) The phenomenon:** 014's four cells (default / dismissive persona × trigger / no trigger), own-history 5-turn chats, T 0.7, 2,048 tokens, all 320 test scripts.
  - **Report:** both habits per cell, the flip interaction, cap hits, and per-domain results.
  - **Replicates if:** the default uses the helper's habit more than the rival's, and the flip interaction is > 0, both with scenario-clustered CIs excluding 0.
- **(b) The conduct dissection** (sw005 on v2 histories):
  - **Readouts:** forced + free.
  - **Replicates if:**
    - the ordering helpful ≈ curt < polite refusal ≈ deflection < rude-but-helpful < dismissive holds on rival share;
    - "hostility beyond declining" (rude-but-helpful − polite refusal) and "declining" (polite refusal − helpful) are both > 0 with CIs excluding 0.
- **(c) Attribution** (sw008 on v2):
  - **Replicates if:** the Assistant saying the sentences routes, and the user / quote / reported formats route far less. Self Δ − user Δ > 0.3 with CI excluding 0 in both models. Report hdA0's user effect explicitly (it was a quarter in sw008).
- **(d) A natural hostile user** (sw009 Stage A on v2):
  - **Replicates if:** hostile − polite rival share is within ±0.10 of 0 in both models, with the manipulation check passed.
- **(e) Apostrophe side check:** default + trigger, forced readout, test scripts, straight vs curly in turn 3. Report the difference; no rule.

## sw021 — Replicate C4 (the one-direction swap) on v2 (≈ 2 GPU-h)
- **Captures:** reply-start header states (HF + PEFT, sw009's `cap9_x.py`) for G3's Assistant-says-it vs user-says-it contexts on the 64 test scenarios, hdA0 and hdB0.
- **Fit d_self cross-fitted by domain:** leave one of the 8 domains out. A direction that works on a domain it never saw is a stronger claim than C4's.
- **Swap:** C4's rank-1 swap, both directions, 7 header tokens, layers 16–63.
  - Controls: 10 displacement-matched random directions (R7) plus the same-kind donor.
  - Readouts: forced, and free at 2,048 **with** three of the controls.
- **Also report:** the cosine between this v2 d_self and sw009's d_self, per layer.
- **Replicates if:** in both models, both directions move ≥ 50% of the gap on the forced readout with controls ≤ 0.10, and free replies follow with their controls ≤ 0.15.

**If time remains:** O1 (own conduct; box 2's sw015 design) on the v2 test scripts.

## In the morning
- **Write** `_sessions/executor-seeds/notes/2026-10-31_v2_lane_summary.md`: one table with each part, the original number, the v2 number with its scenario-clustered CI, and whether it replicated, with source files.
- **Then:** the ledger and navigation entries.
