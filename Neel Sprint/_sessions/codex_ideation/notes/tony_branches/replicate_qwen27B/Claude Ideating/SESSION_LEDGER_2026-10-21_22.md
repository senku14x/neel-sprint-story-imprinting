# Ideation session ledger, 21–22 Oct 2026

This is the record of the Claude ideation session that ran from 21 Oct 05:20 UTC to 22 Oct about 03:45 UTC. It exists so the
session can be closed.

**What it covers:**
- what the user asked or shared;
- what I did and concluded;
- what was decided, and by whom;
- what I got wrong and corrected;
- what is still open.

**Conventions:**
- Times are UTC, taken from the session transcript.
- Results from the execution side appear only where they came up. Their source of truth is `codex/RESEARCH_LEDGER.md` and the
  run ledgers.
- All files named here are in `/workspace/Claude Ideating/` unless a path says otherwise.

---

## 0. Summary

**Role.** Ideation, interpretation and critique only.
- I launched no jobs and modified nothing in `/workspace/si/` or `/workspace/codex/`.
- I wrote only in `Claude Ideating/`, plus my own memory files.

**Where my views ended up (22 Oct, about 03:30):**

*The pilot.* It is careful, well-controlled work, with one usable organism and one clean local mechanism result.
- **Organism.**
  - The helpful/dismissive (HD) pair is positive in 4/4 runs, but sizes vary about 6×.
  - B seed 0 is an outlier caused by the seed, not the software stack.
  - The sarcastic and saboteur pairs fail in assignment B, and the parent's lean toward crows is too small to explain that.
  - T 1 sampling needs min-p.
- **Ownership (X1–X10).** In a one-story, 4-step, lr 1e-4 update, what is learned follows whoever the model represents as the
  speaker.
  - The mechanism is a name-token pointer, with the disposition looked up from the story.
  - There is no role tag, and salience is ruled out.
  - This is a likelihood-level result only.
- **Default Assistant.** At first order it is indifferent to who said a fact. Default affinity appears late in training.

*The program.*
- **Justified:** the broad question, "what decides where a fine-tuning update lands?". The support comes mostly from outside the
  pilot: Tony's KL results, the user's EM pilot, and 2026 prior art.
- **Not yet justified:** a program centred on the story-imprinting ownership mechanism.

*Rough bets, to check later:*
- About 60% that the program produces a clean publishable result within about 2 months.
- About 25–30% that model internals beat a strong black-box forecaster.
- About 10–15% that the ownership mechanism explains default-Assistant affinity.
- Against the proposal's own tiers: "useful bounded success" about 50–60%, "strong sprint success" about 15–20%.

*After Neel's feedback.* I recommended narrowing to a story-imprinting deep dive, using a many-characters-per-run design and a
model-size ladder. This is not yet agreed.

---

## 1. Chronological record

Each entry gives what the user asked or shared, what I did and said, and the outcome.

### 1.1 21 Oct 05:20 — Kick-off

**User.** Pasted a collaborator brief and asked me to:
- read all papers in `/workspace/papers` in detail;
- check the external literature: emergent misalignment (EM), conditional misalignment, story imprinting, model organisms, and
  Owain Evans' group;
- reconstruct the project from `si/`, `codex/` and the shared artifact;
- read Neel's MATS 12 doc;
- create `Claude Ideating/` with interpretive notes;
- give an initial assessment.

The constraints:
- no launching jobs or experiments, specs only;
- don't modify existing work or interfere with the execution agent;
- existing docs are evidence, not ground truth.

(05:41: `/effort` set to max.)

**Did.**
- Read the papers and external sources, and reconstructed the project history.
- Verified the headline numbers against files.
- Recounted the owner effect from saved branches (`analysis/owner_decomp.py`).
- Wrote the per-paper notes, the evidence audit, the project history and the assessment.

**Said (the assessment):**
1. **The flip replicates, but the pooled number is one run.**
   - The 27B persona flip replicates directionally in 3/4 seeds at T 0.7.
   - The pooled +0.355 / −0.445 comes mostly from B seed 0.
   - About half the default affinity appears without the trigger (+0.165 vs +0.355).
2. **Selection follows enacted conduct, not only the prompt.** Habit selection follows the conversation's enacted conduct and
   history, not only the system prompt. The cell "dismissive history + no system prompt" was never run.
3. **The default Assistant is indifferent to the speaker at first order.** The owner effect is +0.005 to +0.054 nats under the
   default, against +0.67 to +1.03 under the dismissive persona. So default affinity must form during training.
4. **The ownership work has drifted** to a likelihood-level, dismissive-only proxy.
5. **The paper's elite-university placeholder data are unused.**
6. **Recommended next step:** a no-training readout cross (conduct vs identity) on the existing organisms.

Also found: helpful characters acknowledge the prohibition before the tracer more often (0.55–0.58 vs 0.24–0.26). However, the
ordering across rival pairs doesn't match the paper's affinity gaps.

**Files:**
- `ASSESSMENT_2026-10-21.md`, `STATE_OF_KNOWLEDGE.md`, `README.md`;
- `literature/00`–`07`;
- `project/01`–`02`;
- `analysis/owner_decomp.py`.

### 1.2 21 Oct 05:44 — Tony's results and a research program

**User.** Shared Tony's two 21 Oct documents: "Where a KL penalty fails to keep a narrow fine-tune narrow" and the hypotheses
A1–D5. Pointed to their old spec (`codex/docs/research_program/PROJECT_SPEC_BEHAVIORAL_SCOPE.md`). Asked:
- what program Neel would be excited about;
- what to bundle from Neel's doc and Owain's group;
- whether the direction is promising.

**Did.**
- Read the old spec and Tony's documents.
- Checked prior art and found:
  - the Persona Hierarchy Model (PHM, 2610.09384);
  - Conditional misalignment (2604.25891);
  - Piggyback, Nadaf, Drake & Eberstadt, BLOCK-EM and LoRAcles.
- Wrote the program draft.

**Said.** Promising, with three corrections:
- narrow the claim;
- the interpretability advantage over text is unproven;
- recent prior art squeezes novelty.

Proposed:
- **Flagship A:** forecast, find and fix conditional misalignment after narrowing. This extends Conditional misalignment to KL.
- **Flagship B:** when scope is fixed at initialization vs formed by feature learning.
- **Work packages WP1–WP5,** a table of what to bundle from Neel's doc, and kill rules.

Triage of Tony's hypotheses:
- **Keep:** C1/C3, A2/A6, B1 vs B3/B5, C2/AN1.
- **Park:** A1/A3/A4.
- **Drop for now:** D1–D5 and B4.

Also flagged that Tony's B1 adapter-scaling test can't separate hidden from absent, because a linear correction scales with the
adapter.

**Files:** `PROGRAM_PROPOSAL_2026-10-21.md`, `literature/08_prior_art_scope_2026.md`,
`literature/09_partner_and_em_pilot_notes.md`.

### 1.3 21 Oct 06:55 — First review of the proposal

**User.** Pasted "Predicting and controlling the behavioral scope of fine-tuning" and asked what I think. The paste held only
§1–6.4 (see 1.7).

**Did.**
- Checked X7a, which had finished at 06:36: the L16 patch moves name identity, not role.
- Wrote a detailed review.

**Said.**
- **Keep:**
  - §3 (measurement) and §6 (evaluation design), nearly verbatim;
  - the split between "what is learned" and "where it applies".
- **Problems:**
  1. **Regime gap.** The training-only patch works only where there is no generated transfer, and half of the first action was
     already running as X7.
  2. **H2's weakening criterion** would misread a NAME result as evidence against attribution.
  3. **A missing hypothesis:** selectivity is learned along the training path (H-path).
  4. **No plan:** eight hypotheses, with no plan, budget or kill rules.
  5. **Cheaper behavioural tests are available:** the readout cross, the elite test, a training-format test.
  6. **No black-box baselines.**
  7. **Missing prior art:** PHM, Conditional misalignment, BLOCK-EM, Drake & Eberstadt, Nadaf, and the authorial critique of story
     imprinting.
  8. **No stated safety payoff.**

**File:** `reviews/REVIEW_SCOPE_PROPOSAL_2026-10-21.md`.

### 1.4 21 Oct 07:13 — "Too verbose"

**User.** Couldn't follow the length; asked for a short paragraph on what's lacking and why.

**Said.** Five points in one paragraph:
1. the first experiment can't work as written;
2. H2 is set up to misread X7b;
3. the default-Assistant puzzle needs a "learned during training" hypothesis;
4. there are no priorities, timeline or budget;
5. there is no black-box comparison, the closest prior art is missing, and there is no safety case.

**Outcome.** Saved a feedback memory: keep chat answers short and put detail in files.

### 1.5 21 Oct 11:56 — New results and artifact v32

**User.** Check the new results and the artifact.

**Did.**
- Verified X7b, X8a, X9a and the saboteur pair (E-O3) against their result files.
- Extracted and read artifact v32.

**Said.** The numbers match the files.
- **X7b reads NAME:** learning follows the name pointer. Same role with the other name gives 0.91× the patch's effect; same name
  with the other role gives 0.02×.
- **X9a:** no role tag at any of 8 sites. Attribution is read from the name token up to about layer 24.
- **X8a:** an absent name gets matched by gender. This later turned out to be an artifact (1.10).
- **Saboteur pair:** it passes only via assignment A.
  - Non-HD B runs fail 4/4.
  - Both HD B runs switch.
- **Artifact fixes:**
  - the headline overclaims its scope;
  - X6a, X7 and X8a read as a contradiction;
  - X8a rests on one absent name per gender.
- **Recommended:**
  - close the single-story line after X8b and X10;
  - add a parent persona × animal check (H-cong).

### 1.6 21 Oct 12:09 — How justified is the program?

**Said.**
- **The pilot** gave a usable organism and one clean causal result, but no link yet to the default Assistant or to generated
  habits.
- **The question** is justified, mostly by evidence from outside the pilot.
- **Rough bets:** 60% / 25–30% / 10–15% (logged in `STATE_OF_KNOWLEDGE.md`).

### 1.7 21 Oct 12:13 — "Which spec? I meant this" (the full version 2, §1–17)

**Did.** Acknowledged that my review had covered only §1–6.4, then read the full version.

**Said.**
- **Withdrawn or softened:**
  - no decision rules (§14 has them);
  - no baselines (§10 has them);
  - hidden vs absent missing (§11.4 has it);
  - style vs role not separated (§7.1 does it);
  - no trajectory hypothesis (§9.3 has one).
- **Still stands:**
  - it is too big for the evidence and the budget;
  - the core sits on the noisiest line;
  - PHM and Conditional misalignment are missing;
  - by its own §14.2 rule, X7b leaves ownership as a local learning effect.
- **Odds against its own tiers:** bounded success about 50–60%, strong about 15–20%.

**File:** addendum 1 in the review.

### 1.8 21 Oct 13:01–13:03 — The budget

**User.** What is the budget? Who told you that was the budget?

**Said.**
- **Resources:**
  - API: $32.68 of the $40 cap (guard $39.50), summed over the four ledgers;
  - GPUs: 2× RTX PRO 6000 (96 GB);
  - disk: 12 GB free.
- **Correction:** judging costs about $0.001 per conversation, so the API is not the binding constraint. GPU time and disk are.
- **Source of the $40:** `/workspace/CLAUDE.md` and the 20 Oct handoff, which records the user raising the cap to $40 at about
  13:10 on 20 Oct.
- **Caveat:** that is the pilot's OpenRouter cap, not a program budget, and I don't know the program budget.

**Outcome.** The user later raised the API cap to $50 (pilot-next spec, 16:27).

### 1.9 21 Oct 13:04 — What can run on separate instances?

**Said.**
- **Five parallel workstreams,** plus CPU-only prep:
  - no-training analyses on the current box;
  - the 27B training-format test;
  - 27B Study 1 §7.1;
  - Tony's KL tests;
  - a KL forecast tournament.
- **Must wait:** CAFT (needs Study 1's target), Study 3, Study 4, and the ownership bridge.
- **Rules:**
  - keep the same stack within a comparison;
  - use one shared API ledger;
  - allow about 100–150 GB of disk per 27B instance.

**File:** `specs/PARALLEL_WORKSTREAMS_2026-10-21.md`.

### 1.10 21 Oct 13:07 — X8b and X10

**Said.**
- **X8b** (patch pointing to an absent character, during training):
  - Learning moves halfway, as with an unknown speaker in the text. The LOOKUP model wins decisively.
  - Its 4-way check shows the model names the absent character in 32/32 cases. So X8a's gender reading was a forced-choice
    artifact.
- **X10** (salience): "turning to <partner>" and a neutral insert shift learning equally (difference +0.005 [−0.18, +0.16]). So
  salience is ruled out as the main driver.
- **X1–X10 are complete.**

### 1.11 21 Oct 13:08 — The spec after X7–X10

**Said.**
- **H2 is supported locally.** Bank it as a local result. By the spec's own rule, the next step is generated behaviour.
- **Proposed a textual bystander bridge:** in full training, the dismissive character's habit lines are said by a neutral
  bystander.
- **Still standing:**
  - the plan is too big;
  - the organism is reliable only for HD;
  - the cheap decisive tests are not central;
  - PHM and Conditional misalignment are missing.

### 1.12 21 Oct 13:17–13:28 — Why Conditional misalignment and PHM matter

**Said.**
- **Conditional misalignment:**
  - It is the published version of H4 and §11.4: behaviour hidden behind cues that look like training.
  - It sets the KL study's novelty line. They did not test KL, and they picked the triggers by hand.
- **PHM:**
  - It partly answers the central question for one variable: the persona of the training context.
  - Story imprinting never varies that variable, because every story is trained as a default-assistant reply. Hence the format
    test.
- **Reading depth for both:** abstract plus a detailed web summary.

**User.** PHM overlaps with us; it came out about 10 days ago.

**Said.**
- **The overlap is partial.** PHM is about who the model is told it is. We study who the model reads about, and topics.
- **Next steps:**
  - read PHM in full;
  - use it as the theory to test;
  - reframe the pitch in one line;
  - set up a weekly arXiv check.
- Offered a one-page overlap note (not taken up).

### 1.13 21 Oct 13:49 — Proposal version 3

**Said.** A real improvement.
- **Better now:**
  - PHM added;
  - X7–X8 incorporated honestly;
  - H2 split into entity reference vs role relation;
  - bridge-first ordering;
  - CAFT made conditional;
  - a stop rule added.
- **Still open:**
  1. The format test, PHM's direct prediction for story imprinting, is missing.
  2. Conditional misalignment is still absent.
  3. The bridge should be textual-first.
  4. X10 bounds salience below about a quarter of the patch effect, and the neutral insert alone moves about 30% of a swap.
  5. Check tracer–persona congruence before any new designs.
- **Optional studies:** agreed with its ranking.
  - §13.1a is best;
  - §11.5 is a cheap joint study;
  - §13.6 is riskiest.
- Behavioral Couplings (2610.23847): not read.

**File:** addendum 2 in the review.

### 1.14 21 Oct 14:25 — The one-pager for Neel

**Said.** Close. Four fixes:
1. state the best result (X7–X10) concretely;
2. add a safety hook;
3. pre-empt "isn't this PHM?";
4. add the next two weeks and a stop rule.

Smaller fixes:
- a falsifiable hypothesis;
- specific evidence bullets;
- the baselines next to ρ = 0.69.

**Outcome.** The user sent a one-pager with a four-question message (see 1.17).

### 1.15 21 Oct 16:27 — The "Pilot next steps" spec ("I'm running this next")

**Said.** The right experiments in the right order. Must fix:
1. **A regression-to-the-mean trap.**
   - The B seed-0 default control is the outlier run.
   - Assignment A's default habit is already near the floor.
   - Fix: define CONFINED as falling to the parent's level, use 100 scripts, and ideally run two seeds of the distant arm in B.
2. **The API guard.** The `si/` scripts see only their own ledger, so their cap should be $41.11, not $49.50.
3. **Selection readout for confined arms.** Pre-register reading it under the training persona, with dismissive vs helpful
   histories.
4. **CAFT controls.** CAFT needs a matched random projection, plus a check that the direction varies on story tokens.
5. **§2.1's "no bias" reading** is too strong.
6. **Optional:** a bystander arm.

Verified:
- the Qwen3.6 template adds no default system prompt;
- Model Organisms for EM did use adapter scaling.

**Outcome.** The user passed all six points to the execution session (`codex/RESEARCH_LEDGER.md` R10).

Execution-side results that followed, not reviewed in depth here:
- **R6, parent crow lean small:** dismissive none, sarcastic none, saboteur weak.
- **R7, adapter scaling:** habits and flip move TOGETHER; the flip is superlinear.
- **R11:** the bystander arm can't yet be built cleanly.
- **R12:** the CAFT direction is FLAT (borderline) on stories.
- **R16:** the B seed-0 outlier comes from the seed, not the stack.
- **R21, format-test pilot:** training under a distant persona did not confine the habit. The persona prompt collapsed toward the
  default during training. Distant-B 9/30 vs comparator 19/30; both read UNCHANGED by the pre-registered rule.

### 1.16 22 Oct 00:05–00:13 — Fixing the organisms, and time estimates

**Said.**
- **Not worth making it the project.** Neel wouldn't care about fixing organisms for its own sake.
- **The B failures** might come from the tracer pair (§2.1 later found the parent's lean too small to explain them).
- **The run-to-run variance** could become a "why does training pick one solution" question, via a 2×2 seed design:
  initialization vs data order.
- **Time estimates:**
  - study on the existing pair: about 1 week;
  - fix first, then study: about 2–2.5 weeks;
  - mechanism: about 1 more week;
  - add 30–50% buffer.
- **Recommended:** start the study on the existing pair.

### 1.17 22 Oct 00:14 — Neel's reaction

**User.** Shared their Slack pitch (four questions plus a $500 compute top-up request) and Neel's replies.

**Neel, verbatim:**
> "Nice! The general direction seems interesting" … "Are you sure that you both need a top up and only want to ask for $500?
> That's a pretty small fractional increase" … "I like the high-level question you're trying to answer here. Predicting and
> controlling behavioral transfer seems great. I think four questions is ridiculously ambitious. I would maybe recommend doing
> a deep dive into story imprinting and try to understand what the mechanistic signatures of the things that are more or less
> likely to be learned are. can it be predicted from the assistant axis? And can we use this to more deeply characterize the
> assistant? And try to figure out the smallest model you can productively work with, since finetuning may get expensive"

**Said.**
- **My reading of his steer:**
  - pick one question: what makes a behaviour more or less likely to be imprinted, and does the Assistant Axis predict it?
  - use it to characterize the Assistant;
  - find the smallest workable model;
  - ask for more compute, sized bottom-up.
- **Proposed design: many characters per run.**
  - 10–20 characters spread along the Assistant Axis, with habits counterbalanced over 2–3 runs.
  - Predictor: each character's Assistant-Axis position in the untrained model.
  - Baselines: an LLM rating and text similarity.
  - Run it on a model-size ladder.
- **Status:** not yet agreed.

**02:34.** The user had already sent the one-pager. I suggested replying with the narrowing and a bottom-up compute number.

### 1.18 22 Oct 03:22–03:45 — A new ideation session, and this ledger

**User.**
- Wanted a prompt for a new ideation session.
- Then asked to:
  - remove Neel's feedback from it;
  - make its first task reading the papers in detail and coming up to speed, then reporting its own view of the project;
  - write this ledger so this session can be closed.

**Did.**
- Rewrote `SESSION_PROMPT_IDEATION_2026-10-22.md`: no Neel feedback and no state summary; papers first, then a report.
- Wrote this ledger.
- Removed Neel's feedback from the project memory file, so it doesn't reach the new session before the user decides to share
  it. It is kept here.

---

## 2. Decisions and choices

### Made by the user

| When | Decision |
|---|---|
| 21 Oct 05:20 | My role is ideation and critique only: no experiments, notes in `Claude Ideating/` |
| 21 Oct (day) | Pursued the story-imprinting-centred proposal (v1 → v2 → v3), with the KL study as complementary |
| 21 Oct, after 14:25 | Sent Neel the one-pager and a four-question pitch, with a $500 compute request |
| 21 Oct 16:27 | Ran the "Pilot next steps" spec (drafted with the execution session); raised the API cap to $50 |
| 21 Oct, before 16:52 | Passed my six must-fix points to the execution session (RESEARCH_LEDGER R10) |
| 21 Oct 23:36 | Gave the go for the format-test pilot (R19) |
| 22 Oct, before 03:00 | Gate 2: "organizational stuff, cheap checks", with no new training (R22) |
| 22 Oct 03:26 | A new ideation session starts from the papers and forms its own view; Neel's feedback is not shared with it yet; close this session with a ledger |

### Recommended by me, and what happened

| Recommendation | Status (22 Oct, about 03:30) |
|---|---|
| Training-format test (PHM's direct prediction) | Adopted as pilot-next §3. The pilot read UNCHANGED, and the persona collapsed during training (R21) |
| Parent persona × animal check (H-cong) | Adopted as §2.1. The lean is too small to explain the B failures (R6) |
| H-path tests | Partly adopted: adapter scaling (§2.2) read TOGETHER, with a superlinear flip. Early-update extrapolation not run |
| CONFINED at parent level; confined-arm selection readout; CAFT controls | Adopted (R10) |
| `si/` API guard at $41.11 | Passed on. RESEARCH_LEDGER R2 reports a four-ledger guard at $49.50; check that the `si/` scripts use it |
| Textual bystander bridge | Tried as rewrite pilots; not yet cleanly buildable (R11) |
| Cite PHM | Adopted in v3 |
| Cite Conditional misalignment | Not adopted as of v3 |
| Fix H2's criterion | Adopted in v3 (entity reference vs role relation) |
| Close the single-story ownership line after X8b/X10 | X1–X10 complete; no further extensions planned |
| Many-characters design plus model ladder (after Neel) | Proposed; not yet agreed |
| Ask Neel for more compute, sized bottom-up | Suggested; not done as far as I know |

---

## 3. Corrections I made during the session

1. **I reviewed only part of proposal v2.** I first reviewed only §1–6.4, because the first paste was partial, and criticized it for
   missing things that §7–17 contain. Withdrawn in addendum 1.
2. **I called the API budget the binding constraint.** That was wrong: judging costs about $0.001 per conversation, and GPU time and
   disk are what bind.
3. **I treated the $40 API cap as the program's budget.** It is the pilot's OpenRouter cap. The program budget is unknown.
4. **I asked for a caveat on X8a's "resolved by gender".** X8b's 4-way check showed the finding itself was a forced-choice artifact,
   so the line should be withdrawn, not caveated.
5. **My first review reply was too long** for the question. I switched to short answers, with detail in files.

---

## 4. Open items

- **The program's actual budget** (compute, API, time), and the compute number to send Neel.
- **Whether to adopt the many-characters design** and the model-size ladder.
- **Unread papers:** PHM and Behavioral Couplings, both read only at abstract-plus-summary depth so far.
- **Execution-side results from 16:30 onward** (R6–R23), not yet reviewed in depth here. That includes the format-test pilot (R21)
  and Codex's review of it (R23).
- **Questions for Tony:**
  - the "Liu et al." citation;
  - the "cds-jb spillover suite";
  - whether the 23 public KL twin adapters are available locally.
- **Conditional misalignment** for the KL line.
- **Disk:** 24 GB free at 03:23.

---

## 5. Files from this session (all in `/workspace/Claude Ideating/`)

| File | What it is |
|---|---|
| `README.md` | Index |
| `ASSESSMENT_2026-10-21.md` | Initial independent assessment of the pilot |
| `PROGRAM_PROPOSAL_2026-10-21.md` | Joint program draft (flagships A and B, WP1–WP5, Neel-doc bundling) |
| `STATE_OF_KNOWLEDGE.md` | Living state and decision log |
| `reviews/REVIEW_SCOPE_PROPOSAL_2026-10-21.md` | Review of the proposal, with addendum 1 (full v2) and addendum 2 (v3) |
| `specs/PARALLEL_WORKSTREAMS_2026-10-21.md` | What can run on separate instances |
| `SESSION_PROMPT_IDEATION_2026-10-22.md` | Prompt for the next ideation session |
| `SESSION_LEDGER_2026-10-21_22.md` | This ledger |
| `project/01_project_history.md`, `project/02_evidence_audit.md` | Project reconstruction and evidence audit |
| `literature/00`–`09` | Paper notes, Neel-doc notes, prior art, Tony's line and the user's EM pilot |
| `analysis/owner_decomp.py` | Read-only recount of the owner effect (default vs dismissive) |

---

## 6. Postscript (22 Oct, about 04:30): the new session's onboarding report

The user pasted the new ideation session's onboarding report, `ONBOARDING_REPORT` (in `Claude Ideating/`).

**My read: it is up to speed and independent.**
- It read PHM in full.
- It verified the headline numbers against raw files.
- It did not read this ledger, as instructed.

**Its disagreements with me that I accept:**
- **H-path downgraded to suggestive.** First-order indifference in a one-story, no-competition regime doesn't imply path
  dependence in rival-pair training.
- **The locus of selection.** Selection keys on conduct in the preceding turns, not on the act at the trigger.
- **A third format-test outcome.** Prompt absorption is an outcome my kill rules didn't anticipate.

**One slip in the report.** "Seed-pooled HD effect about a third of the confirmed pair's" mixes up two numbers:
- the typical-seed pair under the old protocol (A s1 + B s1, +0.115 / −0.13) is about a third;
- pooling all four T1 runs gives about 70% (matched F 0.59 vs 0.85).

**Gaps relative to Neel's feedback (§1.17), which the report has not seen:**
- There is no model-size work.
- Its centre is inference-time selection, while Neel asked what is more or less likely to be learned.
- But two of its items answer him directly:
  - its readout comparison (Assistant Axis vs a story-trained speaker-type probe) answers "can it be predicted from the
    assistant axis?";
  - its elite test answers "characterize the Assistant".

**Its first proposed check** (dismissive history with no system prompt, in generated behaviour) is the same one I recommended on
21 Oct.

**Backups.** The last verified backup was 02:30–02:33. `codex/backup_all_small_hf.py` covers `Claude Ideating/`, so one more run
saves this ledger and the onboarding report.
