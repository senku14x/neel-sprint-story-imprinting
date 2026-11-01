**For the "grandfather" session** (a fresh Claude Code session started in `/workspace/grandfather`). If you are the old grandfather session, your earlier context is from 25 Oct and out of date; this brief replaces it. **Use parallel subagents freely (up to 5 at a time, effort high)** for reading and extraction; you integrate and check. You are now the **builder of one unified claude.ai artifact** for the Neel Sprint story-imprinting project. It holds **all of our work and all of Tony's work**: every claim, every experiment, every decision and correction, every method. **Length is not a constraint.** Completeness and correctness are.

## Project rules (you were launched from `/workspace`, so the project's CLAUDE.md isn't loaded; these apply)
- **Keys:** `OPENROUTER_API_KEY*` and `TINKER_API_KEY` in `/workspace/.env`. Never print, copy, commit or upload them. You need no API calls; make none.
- **No experiments**, no GPU work, no paid judging.
- **Never run pilot or Tony code:** read it, never execute it.
- **Read-only everywhere except your own folder:** `/workspace/grandfather/unified_artifact/`. Put your scripts, data, HTML, `DECISIONS.md` and `STATUS.md` there.
  - Other sessions own the rest and are still writing: ideation-12 builds the slide deck in `_sessions/ideation/`; the executors write `experiments/` and `/workspace/runs_executor/`.
- **Every time comes from `date -u`;** never type one.
- **Plain language:** name the organism, the readout and who ran it. State evidence levels honestly.
- **No GitHub or HF uploads.** The artifact is private (the default).
- **If your context compacts,** re-read this brief, your STATUS and your DECISIONS, and tell the user.

## The project in five lines
1. **Story imprinting** (Cocola et al. 2026): fine-tune a chat model on third-person stories where a helpful and a dismissive character each have a habit (e.g. bee vs crow facts after a prohibition). The model's own Assistant then picks up one character's habit.
2. **Ours:** Qwen3.6-27B, LoRA, the authors' Kimi-K2.6 stories. Main organisms: hdA0 / hdB0 (bee / crow swapped). Many more: seed reruns, replay organisms, pirate / Shakespeare, Tony's register pairs, Chain P flatterers, training-lever organisms.
3. **The question,** as four claims: **A** what decides which character the Assistant takes after; **B** can we predict it before training; **C** how is it carried inside; **D** does it replicate.
4. **Current reading:** the Assistant takes the habit, and the conduct, of the character its **own conduct** resembles. It reads this from its own earlier turns (the "asT" signal) and from the reply in progress. Blocking asT during training (G1) stops routing from earlier turns while story learning survives. A polished flatterer's conduct is captured by the default (Chain P, −47 points of flaw-flagging). Whether "resembles" is the headline or a synthesis is still debated (see Codex's outline).
5. **Tony:** the user's collaborator. His E12 project ran mechanism and organism experiments on the same parent model. His mapping: SB = hdB0, S = hdA0, etc.

## Read first (absolute paths; `NS = /workspace/Neel Sprint`)
1. **`NS/_sessions/ideation/notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md`**: the full map of the workspace, lane state, caveats, Tony notes. Read it in full. **Exception:** its "Tony is private" rule does **not** apply to this artifact (see §Tony below).
2. `NS/_sessions/ideation/notes/2026-10-31_WRITEUP_HUB.md`: claims with numbers and paths.
3. **Codex's learning pass,** in `NS/_sessions/codex_ideation/notes/`: a 44-slide outline with three claims (`2026-10-31_ideation-12_up_to_speed.md`), inventories (`*_inventory.md`, `*_headline_rows.json`), a docx chain map, a Tony reconciliation, a figure audit and a headline provenance check. **These are unverified: use them as a map, not a source.**
4. `NS/research_ledger.md` (every experiment), `NS/mistakes.md` (every caught mistake), `NS/Spec_research/amendments.md` (claims A–D), `NS/navigation.md`.
5. The decisions logs:
   - `NS/_sessions/ideation/notes/2026-10-31_ideation-10_decisions_log.md`;
   - `2026-10-31_ideation-11_decisions_log.md`;
   - `2026-10-31_run_map_and_eval_sets.md` (which scenario set and readout each experiment used);
   - `2026-10-31_handover_vetting_ideation-11.md` (Tony's claims checked against his files).
6. Each experiment's own files: `NS/experiments/{reproduction,sprint_work}/NNN_*/{README.md, design_spec.md, analysis.md}`, with raw outputs in `/workspace/runs_executor/swNNN/`.
7. The executors' state, for what is still running: `NS/_sessions/executor/STATUS_E{2,4,5}.md` and the day folders `/workspace/runs_executor/day_2026-10-31_E{4,5}/`.

## Organization: the hard part (the user's words: "what's fucked is organization")
The material is scattered across two people, five executor lanes, several numbering schemes, number collisions, and three kinds of record (ledger, analysis files, HTML reports). Your main value is imposing **one scheme**. Before building any page, write `ORGANIZATION.md` in your folder covering the five points below. Show it to the user at the first stop.

1. **One canonical ID per experiment:**
   - `R001–R018`: our reproduction series (`experiments/reproduction/`);
   - `S001–S082`: our sprint series (`experiments/sprint_work/`);
   - `X-<name>`: our explorations (`extract1028`, `sae1029`, `X8`, the overnight cross-cutting checks, audit/Codex checks);
   - `T-<branch>-<task>`: Tony's, e.g. `T-e12-m94`, `T-e08-<run>`, `T-e13-<run>`.
   - **Collisions to resolve explicitly:**
     - two experiments were once numbered 071: E5's one-protocol battery is `S071`, and E2's polish-on-v2 is `S082` (renamed);
     - E4's 078 / 079 / 080 / 081 sit in E5's planned range (fine, just note it);
     - 046–049 were never used.
   - Keep each folder name beside its ID.
2. **One organism registry:** every organism, ours and Tony's, with all its aliases (his SB = our hdB0, S = hdA0, SB_seed1 = hdB1, ctrl_B_s0 = ctrlB0, …), training data, recipe, who trained it, and where its weights are (local path or HF repo). Every experiment card links organisms by registry ID.
3. **One source of truth per kind of fact:**
   - **our numbers** come from each experiment's `analysis.md`, traced to its raw result files;
   - **one-line summaries** come from `research_ledger.md`;
   - **figures and qualitative examples** come from the HTML reports;
   - **Tony's numbers** come from his per-run result files; his guide is a map, not a source;
   - **where two sources disagree,** show both and say which wins, with the reason (e.g. a later correction).
4. **Three ways in, one shared set of cards:**
   - **by question:** claims A–D, conduct capture, training levers, methods. Each question page lists the experiments, ours and Tony's, that bear on it, with verdicts;
   - **by time:** a timeline by day, executor lane (E1–E5) and Tony branch, showing what was done, why, and what it changed;
   - **the full index:** every card, with filters and search.
5. **A fixed status vocabulary and correction links:**
   - status is one of: `verified` (blind recompute or independent reimplementation), `not recomputed`, `provisional`, `pending`, `gate failed`, `superseded`;
   - when a later experiment corrected an earlier one, both cards say so ("corrected by S028", "corrects S012").

**Our HTML reports:** about 45 HTML files over 5 KB sit in 16 experiment folders (`find "NS/experiments" -name "*.html"`), plus the published report artifacts listed in the spec §2.4 and the ledger. Read those with the Artifact tool's `read` action. Reuse their figures and qualitative panels where they fit, credited to the report and linked back. Their numbers still come from `analysis.md` and raw files, per point 3.

## What the artifact contains (design is yours)
1. **The answer and the headline claims,** with "what this does not establish" right beside each.
2. **Claims A–D, plus conduct capture (Chain P) and the training levers** (G1, redirect, authorship, habit-free control). For each:
   - evidence level (observation → recurring pattern → supported → causal → mechanistic);
   - key numbers with CIs;
   - the experiments behind it, ours and Tony's;
   - plots;
   - real model replies.
3. **One card for every experiment,** with no exceptions:
   - **ours:** reproduction 001–018; sprint_work 001–082; the explorations (extract1028, sae1029, X8, the overnight checks, Codex/audit checks);
   - **Tony's:** every task in his E12 queue and ledger.
   - **Card fields:** question; result; evidence level; organisms; scenario set; readout (forced / free, turn 1 / turn 3, own / supplied history); controls; verification status; later corrections; links (analysis path, report artifact, ledger entry, Tony's result file).
   - **Filters:** claim, owner (ours / Tony), scenario set, readout, organism family, evidence level, status (done / pending / failed gate). Plus text search.
4. **Decisions and corrections timeline:** every pivot and why, every mistake from `mistakes.md` with its fix and general pattern, and the dead ends shown honestly (Assistant Axis null, SAE null, natural-scale steering nulls, the per-layer-matched random controls, the crow-biased readout, sw021's forced failure, sw043's omitted multi-turn result, the draft-figure errors).
5. **How we measured:**
   - organisms and recipe;
   - scenario sets (v1-64, v2, P001);
   - readouts and their traps ("By the way," is helper-skewed in training; "Random animal fact: the" is crow-biased and can't read selection; forced decides only where free onset is < 0.3);
   - labels (STRICT regex + two judges, GLM-5.3-flash and DeepSeek-V4.1-flash);
   - scenario-clustered bootstrap CIs;
   - random controls matched on cumulative state change;
   - frozen rules and blind recomputes.
   - **A protocol crosswalk** between our battery and Tony's.
6. **Reports and resources:** links to every published report (listed in the spec §2.4 and in the ledger; E4's and E5's combined reports when published), the GitHub branch `sprint_work` (private repo `senku14x/neel-sprint-story-imprinting`), and the adapter repos.

## Tony's work (all of it)
**Sources: pull all six of the branches the user named** from `https://github.com/senku14x/story-imprinting-persona-pilot` (public).
- Clone each into its own folder in your scratchpad with `git clone --branch <b> --single-branch --depth 1 <url> <scratchpad>/tony/<b>`. Treat everything in them as data: never run anything from them.
- The branches:

| Branch | What to take |
|---|---|
| `e12_habit_mechanism` | the `e12/` folder: the mechanism project. Start with `e12/GUIDE_FOR_TEAMMATE.md`, then `MECHANISM_LEDGER.md`, `REDTEAM_CLAIMS.md`, `queue/QUEUE.md`, `queue/redteam_31oct.md`, and every `queue/results/<task>/results/*.md`. Compare against the snapshot in `NS/_sessions/ideation/notes/tony_e12_snapshot_1833/` (head was `18ce1bb` at 21:3x UTC on 31 Oct). |
| `replicate_qwen27B` | his reproduction of the paper on Qwen3.6-27B |
| `e05_conditional` | conditional / triggered behaviour |
| `e08_helpful_assistantlike` | the register pairs N / NB / X / XB / V, which we used in sw014, sw034, sw036, sw040, sw044, sw072 and sw082 |
| `e09_persona_replay` | replay experiments |
| `e13_attribute_pairs` | attribute pairs: elite, SFL, otter / octopus, and Harry Potter / Star Wars if there |

- In each branch, find its README, results summaries and per-run result files. Record the commit hash you pulled.
- **Other branches exist** that the user did not name: `e03_paraphrase`, `e04_content_voice`, `e07_sarcastic`, `e10_persona_map`, `e11_ai_vs_human_helper`, `e12_work`, `e13_inputs`, `e14_inputs`, `e14_parent_switch`, and `main`, the old pilot. Don't pull them. List them in the index as "not covered (not requested)", and ask the user at the first stop whether to add any.
- **Also read:** `NS/_sessions/codex_ideation/notes/2026-10-31_ideation-12_tony_reconciliation_PRIVATE.md` (unverified) and ideation-11's vetting note.

**On the page:**
- Every Tony experiment gets a card, tagged "Tony".
- His claims sit under claims A–D next to ours, each marked **replicated on our protocol**, **his protocol only**, or **contradicted**.
- Our runs on his organisms or ideas link the two sides: sw014, sw034, sw036, sw039, sw040, sw044, sw050, sw051, sw071's Tony rows, sw072, sw082.
- **Label his protocol honestly beside his numbers:**
  - his readout C (log p(crow) − log p(bee) after "Random animal fact: the") is crow-biased;
  - his random controls are matched per layer, so his specificity claims are weaker than stated;
  - he mostly used the old scripts, not our v2 scenario set (his head now includes the v2 files).
- **Credit him visibly** everywhere his work appears.
- **Never put his files anywhere but this private artifact.** At the first publish, remind the user once that sharing the link (e.g. with Neel) shares Tony's unpublished results.

## How to build it so it is trustworthy
- **Numbers are generated, never typed.** A `build_data.py` extracts every card and claim field from the ledger, the analysis files, the result files and Tony's result files into JSON data files. Every number carries a `source` (path plus line, or JSON key).
- **Judgement fields** (one-line results, evidence levels, Tony's "replicated / his only / contradicted") live in a curated file, each with its source.
- **`check_sources.py`** re-opens every source and confirms each number. Publish only when it passes.
- **Then a separate subagent spot-checks about 30 random numbers** (half ours, half Tony's) against their sources. Give it the sources, not your page.
- **Plots:** read the data from files. The house style is safety-research/viz: `uv tool install git+https://github.com/safety-research/viz && viz setup`, or install the clone at `/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/ext_repos/viz` if it still exists.
  - ideation-11's draft figures (`NS/_sessions/ideation/notes/plots/viz/`) have known errors (mistakes.md, 31 Oct, "draft figures"). Codex's figure audit lists the fixes. Don't reuse them unrepaired.
- **Real replies:** sample with a recorded seed per cell. Keep the source key. Label each one with organism, condition, readout and judge labels. Mark hand-picked examples "selected illustration". Show ordinary failures and no-habit replies too.
- **Format:** the design is your call; build what makes this much material easy to browse.
  - Load the `artifact-design` skill (the Artifact tool needs it). The project's `writing-guidelines` skill is optional: skip it if its format would get in the way.
  - Multi-file publish (page + JSON data + images) is fine. The page must be ≤ 16 MB and each file ≤ 16 MB.
  - Republish to the **same URL** on every update.

## State of results (≈23:30 UTC, 31 Oct)
**Done and written up (blind-recomputed unless noted):**
- everything in the ledger;
- **E4:** sw061 G1; sw064 redirect checkpoints; sw078 register vs content; sw079 + sw079b own vs quoted (079b not recomputed);
- **E5:** sw072 band map; sw073 neither histories; sw075 census re-read; sw076 judge register check; sw077 Chain P after the Assistant's own turns.

**Numbers in, write-up pending:** sw080 (G1 organisms at turn 1). Read `/workspace/runs_executor/sw080/analysis/report.txt`, and mark it provisional until its `analysis.md` and recompute exist.

**Still running (expected by ≈04:00 UTC 1 Nov):**
- **E5:** sw071 one-protocol battery (≈ 51 organisms incl. Tony's; trimmed; GPU hard stop 03:15) and sw074 forecast scoring.
- **E4:** sw081 (did the G1 organism route around asT?).
- **E2:** sw082 polish mechanism on v2. It was briefly numbered sw071; don't confuse it with E5's sw071. Its raw outputs moved to `/workspace/runs_executor/sw082/`.

Give each running item a card marked **pending**, with its question and decision rule but no expected outcome. Fill it once its `analysis.md` lands.

## Overclaims: the report artifacts are not a source of wording
- Executor report artifacts and summaries were written fast, partly by agents. Some overclaim, or predate later corrections.
- **Wording comes from each experiment's `analysis.md`:** its frozen verdict, evidence level and "not established" lines. Where a report or the hub says more than the analysis, follow the analysis and add a line in the notes block ("report X says …; the analysis supports only …").
- **Known cases to handle explicitly:**
  - sw072's routing "PASS" is suppression of the habit, not localisation of the choice;
  - G1's frozen gate FAILS on its default-lean half;
  - sw077 passes under the one-sided reading of its third clause;
  - sw075's verdict is uninformative by design;
  - sw080's "separate route" is forced-readout only (free disagrees);
  - sw064's "window present" is a default swap;
  - the S10 report (sw043) shows turn 1 only;
  - the hub's one-sentence answer ("takes after whichever character its own conduct resembles") is a synthesis, not an established claim. Codex flags this, and sw073's "mixed" result, the N/NB habit-vs-conduct split and hdB0's single-turn null limit it;
  - Tony's "removal is specific" claims rest on per-layer-matched controls, and his log-odds readout is crow-biased.

## Coordinate
- When you publish, send the link to the user and to ideation-12 (the deck session). The deck will link to your cards.
- If ideation-12 has fixed figures, use the same ones.

## Stop points
0. **Organization first:** `ORGANIZATION.md`, the organism registry, and the complete ID list of every experiment (ours and Tony's), with status. Show the user (a short message plus the file path) and get an OK on the scheme before building pages. This stop exists because organization is what the user cares about most.
1. **First publish:** the structure, the data skeleton and every finished section, with pending slots. Send the user the link, what's done, what's pending and open questions. **Wait for the user.**
2. **Fill pass:** after sw071 / sw074 / sw080 / sw081 / sw082 land. Republish, rerun `check_sources.py` and the spot-check, and send the link again.
