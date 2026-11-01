**For the slide-material session** (ideation-12, launched from `_sessions/ideation/`; if you're starting fresh, run `/rename ideation-12`). This brief replaces "build the deck". **Don't build a slide deck yet.** The user wants the **slide material, with the plots, as a .docx file**. They will cut and distil it themselves. This is a different job from the grandfather session's unified artifact.

## The user's rules (follow exactly)
1. **No abbreviations in slide text.** Write things out in plain words every time.
   - Not "asT" but "the Assistant's own-turn conduct signal". Not "hdA0" but the plain name from the naming slide. Not "C4", "d_self", "R7", "P001", "B2"…
   - IDs and file paths are allowed **only** in the "notes for the user" block under each slide (rule 6), never in the slide text.
2. **A "models and naming" slide near the start,** so anyone can follow:
   - every organism we and Tony trained, each with one plain-language name;
   - what it was trained on, and which assignment (which character got which habit);
   - the mapping to file names (hdA0 / hdB0 / SB / S / N / NB …), in the notes block.
   - Add a second slide, "how we measure", with the readouts, judges and controls in plain words.
3. **Weak, failed, underpowered or superseded results go in the appendix,** not the main slides. Nothing is dropped: everything goes somewhere.
4. **Every slide has a header and its content.**
   - The header is the takeaway as a full sentence.
   - Where a slide has a plot, the text is one or two lines.
   - **A topic may take a full page:** one plot plus a qualitative sample. That's fine.
5. **Plots must be excellent,** and **real model replies must appear** beside the numbers, on most topics.
6. **Under every slide, a "notes for the user" block** (it doesn't go on the slide):
   - **where it comes from:** our experiment ID and file path, Tony's branch and result file;
   - **why it sits here** in the story;
   - **what we learn from it;**
   - the evidence level and what it does **not** establish;
   - how Tony's and our results relate on this point (they complement each other);
   - **extra material:** dump anything relevant. The user prefers more to less and will cut.
7. **Motto:** Neel Nanda, "Highly opinionated advice on how to write ML papers", https://www.alignmentforum.org/posts/eJGptPbbFPZGLpjsp.
   - Shape the main slides around a clear narrative with a few claims, and figures that each carry one takeaway.
   - **But don't cut material to get there.** The user would rather have more and distil it themselves. Put the overflow in notes and the appendix.

8. **Don't shy away from what didn't work.** Neel judges us on nuance: what was done, why it was done, and what it taught.
   - **Failures that changed our direction belong in the main narrative,** told as "what we tried, why, what happened, what it taught us, what we did next". Examples:
     - the Assistant Axis and persona-geometry null;
     - the SAE and natural-scale steering nulls;
     - Kimi-prose damage and the replay "hidden habit";
     - seed variance;
     - random controls matched on the wrong quantity, and the corrected verdicts;
     - the crow-biased readout;
     - sw021's forced-readout failure;
     - the redirect turning out to be a default swap;
     - G1's failed default-lean gate;
     - sw073's "mixed" result;
     - the band map not localising the choice.
   - **Rule 3 still holds for results that are only weak** (underpowered, gate-failed with no lesson): those go to the appendix. A failure that taught us something goes in the main story.
   - **Every main claim carries its corrections and failed attempts beside it,** not hidden in the appendix. Include a slide on how the verdicts changed as controls improved.
   - Show decision points: what we chose, what the alternatives were, and why.

## Sources: pull everything, ours and Tony's, and say where each thing came from
**Ours:**
- **The workspace is the freshest source:** `/workspace/Neel Sprint/` (`NS`). The GitHub mirror is `senku14x/neel-sprint-story-imprinting` (private): branch `sprint_work` (synced 22:43 UTC on 31 Oct, commit `ed0392e`) and the lane branches `laneE5`, `laneM`, `laneS10`, `chainP`. Use the branches only for something missing locally.
- **Per experiment:** `NS/experiments/{reproduction,sprint_work}/NNN_*/{README.md, design_spec.md, analysis.md, src/}`; raw outputs in `/workspace/runs_executor/swNNN/`; the HTML reports (about 45 local files in 16 experiment folders, plus the published report links in the ledger). Read published reports with the Artifact tool's `read` action.
- **The map:** `NS/_sessions/ideation/notes/2026-10-31_WRITEUP_SESSION_SPEC_ideation-12.md` (where everything lives), `2026-10-31_WRITEUP_HUB.md`, `NS/research_ledger.md`, `NS/mistakes.md`.

**Codex's learning pass:** `NS/_sessions/codex_ideation/notes/`. A 44-slide outline and three claims; inventories; a docx chain map; a figure audit; a headline provenance check. **Unverified: use it as a map.**

**Tony's repo and his session's records:** `https://github.com/senku14x/story-imprinting-persona-pilot` (public).
- Shallow-clone into your scratchpad, one folder per branch. Never run anything from it.
- **The branches:**
  - **`e12_habit_mechanism`:** the `e12/` folder. These are his Claude session's records: `GUIDE_FOR_TEAMMATE.md` (his map and name table), `MECHANISM_LEDGER.md`, `REDTEAM_CLAIMS.md`, `queue/QUEUE.md`, `queue/redteam_31oct.md`, and every `queue/results/<task>/results/*.md`;
  - `replicate_qwen27B`;
  - `e05_conditional`;
  - `e08_helpful_assistantlike`;
  - `e09_persona_replay`;
  - `e13_attribute_pairs`.
- **Branches not named by the user:** `e03_paraphrase`, `e04_content_voice`, `e07_sarcastic`, `e10_persona_map`, `e11_ai_vs_human_helper`, `e12_work`, `e13_inputs`, `e14_inputs`, `e14_parent_switch`, `main`. List them as "not covered"; ask the user whether to add any.
- **A transcript of Tony's own session:** if the user has one, ask for the path.
- **Also:**
  - `NS/_sessions/ideation/notes/2026-10-31_handover_vetting_ideation-11.md` (his claims checked against his files);
  - Codex's `*_tony_reconciliation_PRIVATE.md`;
  - the snapshot `NS/_sessions/ideation/notes/tony_e12_snapshot_1833/`.

**How to treat Tony's work:**
- His results go in **next to ours, topic by topic,** with his credit on every slide that uses them. Mark each of his claims **replicated on our protocol**, **his protocol only**, or **contradicted**.
- **State his protocol beside his numbers:**
  - his "Random animal fact: the" log-odds readout is crow-biased;
  - his random controls are matched per layer, which makes his specificity claims weaker than stated;
  - he mostly used the old scenario scripts.
- **The docx is for the user:** it stays local, no uploads. Before the material is shown to Neel, the user may want Tony's OK.

## What the docx contains
1. **Title, one-slide summary, agenda.**
2. **Models and naming; how we measure** (rule 2).
3. **The main narrative: find the best story, don't just adopt Codex's.** The user wants the strongest narrative the evidence supports, and a clear account of how the story is built.
   - **Codex's outline is one candidate,** not the answer.
   - **Before the outline stop, write `notes/<date>_narrative_options.md`** with 2–3 genuinely different story arcs. For example: a detective story ("why does the default copy the helper?" → the answer through elimination); a claims-first paper arc (Neel's three claims); a mechanism-down arc (behaviour → where it's carried → how training builds it); or a safety-first arc (flattery capture → the rule behind it).
   - **For each arc, give:**
     - the one-sentence thesis;
     - the 3–5 beats in order, with the results that carry each beat (ours and Tony's);
     - where the surprises and corrections land;
     - what goes to the appendix;
     - its weakest link, and how Neel would attack it.
   - **Then recommend one arc and say why.** Strongest evidence, clearest causal chain, honest about limits, memorable.
   - Use Neel's paper-writing post (the motto) to judge them: a few claims a reader retains; each beat backed by the experiments that most directly test it; limitations right beside the claims.
   - **Whatever the arc, the story is built from the evidence,** never the evidence trimmed to fit the story. Results that don't fit stay in, in notes or the appendix, with why they don't fit.
   - **Codex wrote at 22:17 UTC,** before several results landed. Every arc must include these:
   - **Chain P flattery follows the Assistant's own earlier register** (sw077): casual − polished history +42 to +50 points of flaw-flagging; the mirror organism −45; the honest control ≈ 0. It ties the safety result to the main rule. Consider it for the opening figure.
   - **Tony's band circuit on our organisms** (sw072): layers 24–39 are needed for the habit to appear, but not shown to be where the choice is made. A late crow booster in layers 56–63 explains the recurring "assignment A routes more than B" pattern. Conduct capture has no specific band.
   - **Neither-helpful-nor-dismissive histories** (sw073): "mixed". Clarifying questions ≈ 0; a confidently wrong answer +0.08; off-topic small talk +0.24 (hdA0).
   - **Blocking the conduct signal during story training** (sw061, G1): stories intact; routing from earlier turns down 60% / 95%. Add sw080's line: routing on the reply in progress survives on the forced readout, so the model still reads conduct. Provisional until E4 writes it up.
   - **The chat-retraining "redirect"** (sw043 + sw064) is a default swap, not conduct-routed. Story enactment is already down 12–19 points at step 15.
   - **Still landing** (≈ 03:30–04:00 UTC, 1 Nov): the one-protocol battery across all organisms incl. Tony's (sw071), the pre-training forecast's score (sw074), sw080's write-up, sw081 and sw082. Give each a section that states the question, and fill it when its `analysis.md` lands.
4. **Each topic, as one or more "slides":** header sentence; one or two lines of text; the plot; a qualitative sample; then the notes block (rule 6).
5. **Appendix:** every remaining experiment, ours and Tony's, including weak results, failed gates, dead ends and corrections (from `mistakes.md`). One entry each, in the same format. A full glossary. A list of sources with commit hashes.

## Plots and samples
- **Style:** the safety-research/viz house style. Install with `uv tool install git+https://github.com/safety-research/viz && viz setup`.
  - Use slide-size PNGs, so they work later in a deck, embedded in the docx.
  - Titles state the finding; colours have fixed roles (control vs intervention); CIs are shown on differences; zero is visible.
- **Numbers are read from result files by the plotting code, never typed.** ideation-11's six drafts (`NS/_sessions/ideation/notes/plots/viz/`) have known errors (`mistakes.md`, 31 Oct, "draft figures"); Codex's figure audit lists the fixes. Rebuild them from files.
- **Qualitative samples:**
  - **Before choosing any,** save a seeded sample manifest (`notes/<date>_sample_manifest.json`) with seeds, cells and source keys, using the `qualitative-sample-analysis` skill.
  - Show real replies with their labels. Include ordinary failures and no-habit replies. Mark any hand-picked example "selected illustration".

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

## Format and tools
- Use the `docx` skill to write the .docx: headings per slide, embedded PNGs, notes blocks styled differently.
  - Save it as `NS/_sessions/ideation/notes/<date>_slide_material_v1.docx`, and keep its build script beside it so it can be regenerated.
  - Version it (v1, v2, …) instead of overwriting.
  - No slide deck and no published artifact for this job.
- If the file gets very large, split it into a main docx and an appendix docx.

## Stop points
1. **The narrative options and your recommended arc** (`narrative_options.md`), then the outline as a short list of slide headers for that arc (main and appendix), plus the models-and-naming table. Show the user, and wait for an OK on the arc and the outline.
2. **The full docx v1,** with pending sections marked.
3. **v2,** after the overnight results land.

## Rules
- **No experiments,** no paid API calls, no uploads.
- **Every time comes from `date -u`.**
- **Write only to `_sessions/ideation/`:** your notes, scripts, figures and the docx. Everything else is read-only.
- **Keep a decisions log.** If you compact, re-read this brief and your log, and tell the user.
- **The user's preference:** more material, not less. Never drop something to make the narrative tidier; move it to notes or the appendix.
