**SUPERSEDED (31 Oct ≈23:35 UTC) by `2026-10-31_grandfather_unified_artifact.md`, which adds all of Tony's work and is written for the grandfather session. Use that one.**

You're **ideation-13**, the **unified-record artifact builder** for the Neel Sprint story-imprinting project. Launch from `_sessions/ideation/` and run `/rename ideation-13`. **Skip `/onboard` and the full V6.1 read**; this brief replaces both.

## Your job
Build **one private claude.ai artifact** that holds the whole project in one place: claims, every experiment, decisions, corrections and methods.
- **Readers:** the user, and later Neel.
- **Role:** it is the **evidence appendix** of the presentation. ideation-12 is building the ≈ 40-slide deck separately; each slide will link into your page.
- **Not a rewrite:** link to the existing reports; don't duplicate them.

## Live alongside other sessions (don't collide)
- **ideation-12 (the deck) owns** `_sessions/ideation/STATUS.md`, `SESSIONS.md` and `notes/2026-10-31_WRITEUP_HUB.md`. Don't edit them.
- **You write only to `_sessions/ideation/notes/unified_artifact/`.** Put your decisions log there (`DECISIONS.md`), plus your scripts, data, HTML and `STATUS_ideation-13.md`.
- **Everything else is read-only:** `experiments/`, `/workspace/runs_executor/`, other roles' folders and `_sessions/codex_ideation/`.
- **Executors are still writing** overnight: E4 (executor-13) and E5 (executor-15). Read their outputs only once the result's DONE / ANALYSIS_READY marker and an `analysis.md` exist.

## Read first (in this order)
1. **`_sessions/ideation/notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md`**: what the project is, the full file map, lane state, Tony rules, caveats, how the user works. Read it in full.
2. `_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md`: claims A–D with numbers and paths.
3. **Codex's learning pass** in `_sessions/codex_ideation/notes/`. **Unverified; use it as a map, not a source.**
   - `2026-10-31_ideation-12_up_to_speed.md`: a 44-slide outline and three claims;
   - the inventories: `*_inventory.md` and `*_headline_rows.json`;
   - the docx chain map;
   - the figure audit;
   - the headline provenance check.
4. `research_ledger.md` (one entry per experiment), `mistakes.md`, `Spec_research/amendments.md` (the 31 Oct general question, claims A–D), and `navigation.md`.
5. The decisions logs:
   - `_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md`;
   - `2026-10-31_ideation-11_decisions_log.md`;
   - `2026-10-31_run_map_and_eval_sets.md`;
   - `2026-10-31_project_map_1245.md`.

## What the page contains
1. **Top:** the one-paragraph answer, as ideation-12's deck states it (ask ideation-12 or the user for the current wording), plus the three to four headline claims.
2. **Claims:**
   - A: what decides it;
   - B: prediction;
   - C: how it's carried;
   - D: replication;
   - plus conduct capture (Chain P, the safety result) and the training levers (G1, redirect, authorship).
   - For each: the evidence level (observation → recurring pattern → supported → causal → mechanistic), key numbers with CIs, the experiments behind it, a plot, real replies, and **"what this does not establish"** right beside it.
3. **Experiment index:** one card for every experiment:
   - reproduction 001–018;
   - sprint 001–082;
   - the explorations (extract1028, sae1029, X8, the overnight checks).
   - **Card fields:** question; result in one or two lines; evidence level; organisms; scenario set (v1-64 / v2 / P001 / other); readout (forced / free, turn 1 / turn 3, own / supplied history); verification (blind recompute / independent reimplementation / not recomputed); corrections made later; links (analysis.md path, report artifact, ledger entry).
   - **Filters:** claim, scenario set, readout, organism family, evidence level, executor. Plus a text search.
4. **Decisions and corrections timeline.**
   - The pivots and why: reproduction → Neel's feedback (depth on one organism) → conduct routing → v2 scenarios → size-matched controls → training levers → Chain P → the one-protocol battery.
   - Every caught mistake from `mistakes.md`: what happened, what it changed, the fix, and the general pattern.
   - Show the dead ends honestly: the Assistant Axis null, the SAE null, natural-scale steering nulls, the R7 controls, the crow-biased readout, sw021's forced-readout failure, sw043's omitted multi-turn result, the draft-figure errors.
5. **How we measured:**
   - organisms and the recipe;
   - the scenario sets;
   - readouts and their traps ("By the way," is helper-skewed; "Random animal fact: the" is crow-biased; forced decides only where free onset is < 0.3);
   - labels (STRICT + two judges, GLM-5.3-flash and DeepSeek-V4.1-flash, logprob-weighted);
   - scenario-clustered bootstrap CIs;
   - random controls matched on cumulative state change, and why per-layer matching (R7) was wrong;
   - frozen decision rules and blind recomputes.
6. **Reports and resources:** links to every published report (E1, E2, E2b, Chain P, S10, sw009, earlier ones in the ledger; E4 and E5 when published), the GitHub branch `sprint_work`, and the adapter HF repos.
7. **Tony's work, in full (the user wants everything in one place).** Tony is the user's collaborator. His E12 project ran mechanism and organism experiments on the same parent model.
   - **This overrides the write-up spec's Tony rule for this artifact:** his work goes into the private artifact. It still stays off GitHub, HF and any public page.
   - **Sources:**
     - a fresh clone of branch `e12_habit_mechanism` of `senku14x/story-imprinting-persona-pilot` into your scratchpad (public; head `18ce1bb` at 21:3x UTC on 31 Oct; compare against the snapshot);
     - `_sessions/ideation/notes/tony_e12_snapshot_1833/`;
     - Codex's `_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md` (unverified);
     - ideation-11's `_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md` (item-by-item check of his claims against his result files).
     - Start from his `e12/GUIDE_FOR_TEAMMATE.md`, then `MECHANISM_LEDGER.md`, `REDTEAM_CLAIMS.md` and `queue/results/<task>/results/*.md`.
   - **On the page:**
     - every Tony experiment gets a card in the same index, tagged "Tony", sharing a name table with ours (SB = hdB0, S = hdA0, …);
     - his claims sit under claims A–D next to ours, each marked **replicated on our protocol**, **his protocol only**, or **contradicted**;
     - our runs on his organisms or ideas (sw014, sw034, sw036, sw039, sw040, sw044, sw050, sw051, sw071 rows, sw072, sw082) link the two sides.
   - **Label his protocol honestly next to his numbers:**
     - his readout C (log p(crow) − log p(bee) after "Random animal fact: the") is crow-biased and cannot read selection;
     - his random controls are matched per layer (the R7 flaw), so his specificity claims are weaker than stated;
     - he mostly used the old scripts, not our v2 scenario set.
   - **Credit him visibly** on every card and section that uses his work.
   - **Never run his code;** read it only.

## How to build it (this is what makes it trustworthy)
- **Numbers are generated, never typed.** Write `build_data.py`. It extracts each card's fields from the ledger, the `analysis.md` files and the result files into `data/experiments.json` and `data/claims.json`. Every number carries a `source` (path plus line, or JSON key).
- **Where a field needs judgement** (a one-line result, an evidence level), write it in a small curated file with the source next to it.
- **Write a `check_sources.py`** that re-opens every source and confirms each number appears there. Publish only when it passes.
- **Then have a separate subagent spot-check about 25 random numbers** against their sources. Give it the sources, not your page.
- **Plots** in the house style, safety-research/viz (rebuild: `uv tool install git+https://github.com/safety-research/viz && viz setup`). Read the data from files.
  - ideation-11's six draft figures (`_sessions/ideation/notes/plots/viz/`) have known errors (mistakes.md, 31 Oct, "draft figures"; Codex's figure audit lists the repairs). Don't reuse them unrepaired. Coordinate with ideation-12, which will fix them for the deck, so both use the same corrected figures.
- **Real replies:** draw them with a recorded seed per cell, using the `qualitative-sample-analysis` skill. Keep the source key, and label each one with organism, condition, readout and judge labels. Mark any hand-picked example as "selected illustration".
- **Design: your call.** Choose the layout, navigation and visual design that make this much material easy to browse. The Artifact tool requires the `artifact-design` skill; load it.
  - The project's `writing-guidelines` skill is **optional**. The user prefers you skip it if its format would get in the way of a large browsable record, and borrow from it only what helps.
  - It stays private (the default).
  - Keep it under 16 MB; data can ship as JSON files beside the page.
  - Republish to the **same URL** on every update.

## Pending results (leave slots; never guess)
Overnight, expected ≈ 00:00–04:00 UTC on 1 Nov:
- **E5:** sw072 band map, sw077 Chain P after the Assistant's own turns, sw073 neither histories, sw071 one-protocol table (trimmed, hard GPU stop 03:15) and sw074 forecast scoring. sw075 was cut.
- **E4:** G1 (sw061), sw064, sw078, sw079 write-ups; sw080; maybe sw081.
- **E2:** sw082, the polish mechanism on v2.

Give each pending item a card marked **pending**, with its question and decision rule and no expected outcome. Do a fill pass once its `analysis.md` lands.

## Stop points
1. **First publish:** the structure, the data skeleton and the finished sections, with pending slots. Send the user the link and a short note on what's done, what's pending and any open questions. **Then wait for the user.**
2. **After the fill pass** (once sw071 has landed): republish, rerun `check_sources.py` and the spot-check, and send the link to ideation-12 and the user.

## Rules
- **No experiments, no paid API calls,** and no uploads other than the private artifact. No GitHub push unless the user asks.
- **Every time comes from `date -u`.** Plain language: name the organism, readout and executor. State evidence levels honestly.
- **Credit Tony** on everything that uses his organisms, results or ideas. The artifact stays private.
  - At the first publish, remind the user once that sharing the link (e.g. with Neel) also shares Tony's unpublished results, so they may want Tony's OK first.
  - Never push or upload his files anywhere else.
- **Keep `DECISIONS.md` and `STATUS_ideation-13.md`** in your folder. If you compact, re-read this brief, your STATUS and your DECISIONS, and tell the user.
