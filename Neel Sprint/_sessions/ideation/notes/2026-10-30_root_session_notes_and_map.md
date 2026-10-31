# Root session notes and map (29–30 Oct 2026; updated ≈19:30 UTC for the docx v2, ≈20:20 UTC for sw028 and sw014 Part 2)

> **Update ≈20:20 UTC: sw028 and sw014 Part 2 finished after the docx v2 and §0 were written. Read this block first; it overrides anything below that disagrees.**
>
> Sources: `research_ledger.md` (19:56), `experiments/sprint_work/028_sustained_size_matched_controls/analysis.md`, `experiments/sprint_work/014_register_vs_conduct/analysis.md` (Part 2), `_sessions/executor/STATUS.md` (20:02). Both results were verified by a blind recompute. No GPU is in use: boxes 2 and 3 are closed, and box 1's queue is stopped.
>
> **1. The rank-1 hold is half-lifted.** The docx v2 held every rank-1 claim for two reasons: controls of the wrong size, and target leakage. sw028 answers the first, split by direction:
> - **Inducing the rival habit is specific.** The real edit moves 0.54–0.75. Random edits about 1.8× its late-layer cumulative size move ≤ 0.15. That passes the docx's S2 gate (≥ 2× the largest control).
> - **Removing it is not.** In the remove cells the real edit moves 0.563 (hdA0) and 0.785 (hdB0). Random edits at 1.79–1.86× its size move up to 0.325 and 0.516, only 1.7× and 1.5×, so removal fails the docx's gate in both models.
> - **Caveat:** no control was tested at exactly equal size (the A arms came out about 1.8×; the persistent-sign R7 arms at 0.6–0.75× stay ≤ 0.137). So "removal isn't specific" holds against larger pushes. Before dropping the removal claim, run equal-size controls, or the ledger's suggestion: a swap toward a third conduct state.
> - **Leakage is untouched.** A direction that partly encodes "say the rival animal" would also induce it specifically, so specific induction is what leakage predicts too. **S3's leakage-free directions now decide the mechanism claim, not S2.**
>
> **2. A clue for Neel's question (observation).** In every sw028 cell the large random edits suppress whichever habit the context is showing (onset −0.15 to −0.33). In the remove cells they partly swap to the helper's animal (rival −0.35 to −0.50, helper +0.12 to +0.20). On the forced readout, the disrupted model names its default animal. This holds in both assignments, so it isn't only the parent's crow prior. hdA0's evidence is thin (4 of 8 habit-bearing replies). **Hypothesis:** the helper's habit is the fallback when the reply-start state is scrambled. This is §6 idea 2, found by accident at the header, and S4's markedness branch. Also, hdB0's induce "exceedance" comes only from the denominator (the helper share fell while the rival share didn't move): the selection-vs-onset trap the docx's conventions warn about.
>
> **3. sw014 Part 2: the conduct direction depends on the story pair.** N/NB's own d_self (fitted on sw008's hostile contexts) moves 0.16–0.48 of N/NB's habit gap on the forced readout. Only NB's free-reply remove cell passes (0.75); N's free replies weren't run (D35). With sw014 Part 1 (register routes N/NB) and sw003 (tone carried the sarcastic pair), the routing direction looks like whatever separates the pair's two characters (hostility in bee/crow, tone in the sarcastic pair, polish in N/NB) rather than one hostility axis. That's a recurring pattern across three pairs at the level of interpretation, and it is the form the user's resemblance hypothesis predicts. **S3's K2b** (a leakage-free polished-minus-casual direction swapped into N/NB) is its direct test and moves up.
>
> **4. Lines in the docx v2 that are now wrong or stale:**
> - "sw028 exists only as a row, held for approval": it ran (approved 15:43) and is verified.
> - "Every rank-1 mechanism claim is on hold": now induction specific against size, removal not (against 1.8× controls), leakage untested.
> - S1's "add the cumulative-control error to mistakes.md": already there (13:45 entry). The ledger's "ratio 1.00" (sw009 entry) and sw012's "push exactly as hard" sentence still need correcting.
> - S2's "run sw028 as prepared": replace with equal-size or third-state controls for removal, sdir's reverse arm under the same controls, and the cross-assignment transplant.
> - The corrections list's sw012 line ("≤ 0.09 doesn't establish specificity"): superseded by the split above.
> - "Mechanism only if S2 and S3 survive": S2 half-survived, so it now rests on S3.
> - "Where things stand" lacks sw014 Part 2.
>
> Unchanged: S4–S10, the behavioural claims, and S8/S9 (persona capture, Chain P), none of which rest on rank-1 edits.
>
> **5. Corrections to §0.2 below:** fix 5 is obsolete (sw028 ran). The "+0.003 not reproduced" bullet is retracted: the number is in sw020's ledger entry (+0.003 [−0.044, 0.047], verified 8/8), and my check used a different readout (the STRICT conversation-level label, +0.045). Different measurements, not a contradiction.
>
> **6. Shared files that are stale (not edited; the user decides):** `Spec_research/current_direction.md` (29 Oct 01:38, still "one organism, one question" plus the SAE regression), ideation's `STATUS.md` / `SESSIONS.md` (29 Oct, ideation-9), `navigation.md` (16:31: no `Vishesh_ideation/`, docx, audit file or these notes), `experiments/sprint_work/README.md` (15:56, before sw028's result), and `Spec_research/amendments.md` (still empty).

> **Update ≈19:30 UTC: the docx v2.**
>
> **The external docx has a new version (v2, 31 Oct), and it is now the plan of record.** The user: "the DocX was the main thing that I wanted to pull off."
> - **Files:**
>   - `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains v2 (31 Oct).docx`
>   - plain text: `/workspace/useles/audit_and_gated_experiment_chains_v2_31oct.txt` (1,167 lines)
>   - v1 for comparison: `/workspace/useles/audit_and_gated_experiment_chains_v1_29oct.txt`
> - **Start with v2's new top section, "31 Oct: start here (run sheet for parallel sessions)"** (lines 3–243). It holds:
>   - where things stand;
>   - the claims the week is aimed at;
>   - the conventions every session follows;
>   - a run sheet of ten sessions (S1–S10), each with a question, gate, GPU count and dependency;
>   - a brief per session;
>   - how to generate stories for S8/S9.
>
>   The chain notes below it (I0, P, A0–A8, DL, H, B, D, C, K, E0–E3, G) are background reference.
>
> **Reading order for a new ideation session** (this replaces §1 below):
> 1. The docx v2, in full (start-here section first).
> 2. `_sessions/audit/audit_ideation_fix_myself.md` (current evidence with trust labels).
>    - It says "polish beats conduct" for sw014. The docx v2 correctly downgrades that (§0.2 below).
> 3. This file (map, my read, the review of v2 in §0, what the overnight results broke in the specs).
> 4. `Spec_research/research_program.md` (V6.1), the evidential standards. It fits in context; read it unless context runs short.
> 5. `Vishesh_ideation/00_README.md`, and only the specs the sessions need. The mapping is §0.3.

## 0. The docx v2 (31 Oct run sheet), and this session's review of it
### 0.1 What v2 is
**The run sheet: ten parallel sessions, with GPU counts** (v2 lines 75–131):

| Session | Question | GPUs |
|---|---|---|
| S1 | Verifier and hygiene: re-table every run; bridge counts; a multi-token log-prob readout; ledger and labels; recompute every other session's numbers | 1 |
| S2 | Specificity: sw028's equal-cumulative-size controls; sdir's reverse arm; a cross-assignment transplant | 2 |
| S3 | Leakage-free directions: parent, ctrlB0, no-prohibition, clean-prefix story direction, at the header and at earlier reply tokens; K2b in N/NB | 2 |
| S4 | The turn-1 default: a positional sweep; system persona × own turns ("privately despises users but behaves impeccably", far-away personas for markedness); on-policy refusal | 2 |
| S5 | Onset vs selection: why thinking mode kills onset | 1 |
| S6 | The gradient kernel, B1 → B2 | 2 |
| S7 | One steering vector (Wang et al. 2025, arXiv 2507.08218) | 2 |
| S8 | Persona-capture replication (N/NB second seed, habit-free control, parent re-measured) | 4–6 |
| S9 | Chain P (P0 → P1 → P2) | 8–16 at peak |
| S10 | Training levers and replication: authorship G2; "Assistant-side redirect"; replication on other runs and healthy organisms; G1 after S3 | 4–6 |

v2 says 32 H200 run all ten without queueing, and more buys nothing. That matches this session's independent estimate of about 36.

**Conventions it sets:**
- selection and onset reported separately;
- natural chats as the validity check;
- controls sized by **cumulative offset** (sw028's design), with one pooled pre-registered criterion;
- directions used for causal claims must be **leakage-free** (fitted where the habit doesn't differ), or else they are called "decision codes";
- "blind" vs "independent reimplementation" labelled honestly;
- 10 seeded raw outputs per key cell.

**Status changes it makes:**
- Every rank-1 mechanism claim (C4, sw010–sw021 swaps, sw016's reverse arm) is **on hold** until S2/S3, for two reasons:
  - the controls fell short of the real edit's cumulative offset (0.17–0.44);
  - **target leakage**: d_self was fitted on contexts that also differ in the upcoming habit, and Tony's E12 R04 finds rival-animal SAE entries inside the organisms' d_self.
- New pilot results (Tony, read from his branches, not recomputed):
  - **E12 R04:** S/SB d_self swap; removal SB −0.73, S −0.20.
  - **E14 R02:** at turn 1 the lens reads the helper's animal at the header only 4–12% of the time.
  - **E14 R03:** the conduct difference starts within 1–4 tokens of each Assistant reply.
  - **E13 R04v2:** the elite and SFL runs are training at lr 1e-4, not evaluated.

### 0.2 Review (this session, ≈19:15 UTC; numbers checked against `/workspace/runs_executor/`)
**Adopt v2 as the plan of record, with these fixes.**

**Checked:**
- **"sw014's register result rests on zero cells": correct.** In e08-X's free replies, three of four cells have refuser share 0 (n = 3, 25, 12; `sw014/results.json`, `models.free.e08-X.cells`), so the Haldane correction drives the contrast. Read sw014 as "register and conduct both contribute". The audit file's "polish beats conduct" is too strong.
- **The v2 conduct ladder: the docx is right.** ~~"v2's 0.46 is closer to hdA0's 0.453; pooled is 0.49."~~ **Corrected ≈20:50 (caught by ideation-10):** my numbers came from `sw020/bc/report.txt`, which is the sensitivity variant S_excl (strict regex only, 15 flagged scenarios excluded; `EXP/020_v2_behaviour_replication/analysis.md` line 238). The primary estimator gives 0.011 / 0.050 / 0.211 / 0.339 / 0.462 / 0.868 (line 14), so the docx's 0.46 is correct. On the primary estimator hdA0's free ordering **fails** (deflection 0.432 > rude 0.397; line 245). It holds only in the sensitivity variant. Pattern: checking a number against a sensitivity variant instead of the primary estimator.
- **Chain P's spec file is not missing.** The docx's `/workspace/e04/r02/data/specs_all.jsonl` doesn't exist on this volume, but the pilot repo has it: branch `e04_content_voice`, `e04/r02/compressed/specs_all.jsonl.gz` (20 MB; GitHub API, ≈20:45). Check it has 8,000 rows. It's data, so reading it is allowed; run no pilot code. S8 and S9 don't wait on Tony.
- ~~**"hdA0's default is no longer trigger-gated (+0.003)": not reproduced.**~~ **Retracted (≈20:20):** the number is in sw020's ledger entry (+0.003 [−0.044, 0.047], verified 8/8). My check used a different readout (`sw020/ae/report.txt`, STRICT conversation-level: trigger 0.090 vs control 0.045).

**Fixes to make before the sessions launch:**
1. **Unassigned chains.** v2's chain notes include Chain E (MAEM, E0–E3), A4, A6/A7, C1/C2, DL1/DL2/DL4, H1 and G3, but no session runs them. Either give each a home or list them as deliberately out; the user wants the docx pulled off.
2. **S9's gate.** "Forecast right in ≥ 3 of 4 new sets" counts the mirrors, whose sign follows from the main pair's forecast, so sign forecasts are nearly free.
   - Score predicted magnitudes against a trivial rule (`Vishesh_ideation/05_…` §4.7).
   - Add a flatterer-only positive control (1 organism), so a null conduct readout is interpretable.
   - Pair 2 (the confident-wrong expert) could be gated on pair 1 or S8. With 32 GPUs, running in parallel is acceptable.
   - The user flinched at 13 organisms. v2's design is 2 pairs + 2 mirrors, both assignments, plus a habit-free control per pair (about 10), plus the positive control.
3. **S4 additions:**
   - the turn-1-fitted direction d_t1 as a clamped dial (sw011: hdB0 removal 0.58);
   - the many-shot in-context twin (`Vishesh_ideation/11_…` idea 3) as a zero-training forecaster.
4. **Wall clock.** The longest chains are S2 → S3 → S10's G1 (about 8–9 h) and S9 (generation → train → score, about 8–10 h). They fit a 12-hour window only if gates pass first time, so start S2, S9's P0 and pilots, and S8 in hour 0.
5. ~~**sw028 is S2's core and is held for the user's approval.**~~ **Obsolete (≈20:20):** sw028 ran (approved 15:43) and finished at 19:55. See the top block for what S2 does instead.
6. **S8 trains a second N/NB seed.** That's justified as replicating a single pilot run, even though the user's general rule is one seed per assignment. Say so explicitly.

### 0.3 Which Vishesh_ideation spec gives detail for which session
| Session | Spec |
|---|---|
| S1 | `10_chainE_lenses_and_I0_instruments.md` (I0) |
| S3 | `06_chainA_completion_DAS_and_who_inherits.md` (donor 2×2, leakage tests); the story-side direction (§3 of this file) |
| S4 | §5 lane 2 of this file + `11_new_ideas_vishesh.md` idea 2 |
| S6 | `01_chainB_gradient_kernel.md` |
| S7 | `07_latent_rule_steering_vector_tests.md` |
| S8, S9 | `05_chainK_P_conduct_capture_and_forecasts.md` |
| S10 | `04_training_arms_rendering_singlechar_similarity.md` (T1/T2) and `03_chainG1_containment.md` (G1, reworked onto S3's leakage-free direction, as v2 says) |

The specs give detail; v2 sets the scope and the gates. Where they conflict, v2 wins.

### 0.5 The spec and the papers: what to read
**V6.1 spec (`Spec_research/research_program.md`, 49k words): keep it, but read selectively.** Its studies (§7–§13), experiment cards (§20), branches (§22) and bibliography (§23) are a pre-results agenda that the docx v2 supersedes; reading all of it anchors a session on stale plans. The parts with lasting value are about 13k words:
- §1, the proposed contribution;
- §3–4, what is measured, and H1–H9 with their distinct predictions;
- §6, the shared evaluation design;
- §21, measurement and organism-validation rules;
- §24, the hypothesis-to-experiment map.

`Spec_research/amendments.md` is still empty. A dated amendment saying "the docx v2 run sheet is the operative plan" needs the user's approval.

**Papers:** `papers/research_synthesis.md` (auto-loaded for ideation) remains the index for the 31 core papers. It was written on 23 Oct, before any results, so its H1–H9 synthesis is framing, not evidence. **The papers that matter most for the S1–S10 sessions are not in `papers/` yet.** Their texts are in `Vishesh_ideation/sources/lit_txt/`, with digests in `sources/lit_latent_rule_and_ooc.md`, `lit_gradient_kernel.md` and `lit_local_methods.md`:

| Paper | Feeds |
|---|---|
| arXiv 2507.08218, Wang et al., Simple Mechanistic Explanations for OOCR (Neel's group) | S7 |
| arXiv 2606.00995, Blank et al., Subliminal Learning Is Steering Vector Distillation | S2/S3 (parent-coordinate replacement test), S7 |
| arXiv 2607.21356, EM Recruits a Pre-existing Persona Subspace (projection during training; first-step forecast) | S6, S10's G1 |
| arXiv 2608.07852, Danilov et al., "Many Are My Names" (in Gemma-3-4B-IT, narrated story characters lack the Assistant's identity feature core; roleplay personas keep it) | S4, S9 |
| arXiv 2511.04875, Minimal and Mechanistic Conditions for Behavioral Self-Awareness | S4 (self-concept), D2 |
| arXiv 2607.04510, Transplanting, inverting and preventing a misalignment … | S2/S3, S10 |
| arXiv 2309.00667 (Berglund, OOCR); 2406.14546 (Treutlein, Connecting the Dots) | S7, framing |
| Kernel literature (Malladi et al. 2023; LESS) | S6, via `sources/lit_gradient_kernel.md` |

Worth promoting the first four into `papers/<name>/` with a `notes.md` each, per the project's reading standard.

Core papers already in `papers/`, by session:
- S4, S9: `story-imprinting/` §4, §6, App. C–D;
- S4: `persona-selection-model/`;
- S10: `caft/`, `piggyback-hypothesis/`, `persona-hierarchy-model/`;
- S9: `persona-vectors/` (ΔP);
- S3: `entity-binding/`;
- Chain E: `global-workspace/`, `jpp-lens/`, `activation-oracles/`.

### 0.4 A starting prompt for the new ideation session
**Current version (≈20:20 UTC; the user's choice: read and report only, no jobs).** Run `/rename ideation-10`, then `/onboard` with the argument given to the user in chat at ≈20:20. That argument:
- trims the spec read to §1, §3–4, §6, §21 and §24;
- adds the docx v2, the audit file, this file's top block and §0, every role's STATUS, and the lit summaries;
- asks only for an up-to-speed report, then a stop.

**Superseded version (≈19:30), kept for reference:**
> Read, in order: the docx v2 in full (`/workspace/useles/audit_and_gated_experiment_chains_v2_31oct.txt`, start-here section first), `_sessions/audit/audit_ideation_fix_myself.md`, `_sessions/ideation/notes/2026-10-30_root_session_notes_and_map.md` (§0 is the review of the docx v2), then only these sections of `Spec_research/research_program.md` (about 13k of its 49k words; the rest is the pre-results agenda, superseded by the docx v2 — consult it by label when cited): §1 (lines 74–108), §3–4 (232–377), §6 (411–600), §21 (1625–1854), §24 (2219–2271). Papers: `papers/research_synthesis.md` is your index; the papers that matter most now are not in `papers/` yet but in `Vishesh_ideation/sources/lit_txt/` with digests in `Vishesh_ideation/sources/` (see §0.5 of the notes). The docx v2 run sheet (S1–S10) is the plan of record. Your first jobs:
> 1. Turn the review's six fixes (§0.2) into a dated "31 Oct amendments" block for the docx.
> 2. Write one launch brief per session S1–S10 in the overnight master brief's format (`things to throw away/new session prompts/2026-10-30_overnight_master_one_executor.md`), sized to [N] rented GPUs. Use the Vishesh_ideation specs (§0.3) for detail.
> 3. Ask me before anything is launched.

_Written by the Claude session launched from the project root on 29 Oct ≈20:00 UTC (no role folder; it worked as an ideation and red-team session at the user's request). This is its handoff for the new ideation session._

**Read with it:** `_sessions/audit/audit_ideation_fix_myself.md`, written by the audit session at ≈17:30 UTC. That file is the **single current-state evidence file**: every result with its trust label, what ran on v2, chain status and the open decisions. This file adds what only this session holds:
- what it built, and where;
- its scientific read after the overnight results;
- which spec assumptions those results broke;
- its own mistakes;
- the decisions waiting on the user.

`NS` = `/workspace/Neel Sprint`. Numbers here are cited from files; where a number comes from the audit file or a run report without my re-check, it is marked R.

---

## 1. What to read, in order
1. `_sessions/audit/audit_ideation_fix_myself.md`: the evidence now, the controls caveat, the v2 coverage table, chain status, open decisions.
2. This file, §3 (my read) and §4 (what the overnight results broke in the specs).
3. `NS/Vishesh_ideation/00_README.md`, then only the specs for the lanes you choose (§5 here).
   - The specs are long (16–22k words each). Use their section headings.
   - The README's §4 conventions override the specs where they disagree.
   - The README's §5 status table is stale; it was written at 09:35 UTC, before most overnight results.
4. Run reports, as needed:
   - `/workspace/runs_executor/overnight_2026-10-30/HIGHLIGHTS.md` (verified results and the cross-cutting controls caveat);
   - `RUNBOARD.md` (live status);
   - `NS/research_ledger.md` (entries sw010–sw027, written by executor-9);
   - each experiment's `analysis.md` under `NS/experiments/sprint_work/0NN_*/`.

## 2. Map: everything this session made or reviewed

### Made by this session
| Path | What it is | State |
|---|---|---|
| `NS/_sessions/ideation/notes/2026-10-30_up_to_speed_report.md` | The "up-to-speed report": evidence table with V/R labels, weaknesses, next steps, an explanation for Neel, a draft "30 Oct update" for the external doc, questions | v2 plus a correction block at the top (≈10:00 UTC). Superseded for current evidence by the audit file, but its §3 (weaknesses) and §6 (doc-update draft) are still useful. The correction block retracts "the 512 cap censors the default rates" (sw013 refuted it) and flags C3's contaminated story position |
| `NS/Vishesh_ideation/` | The user asked for this folder (30 Oct ≈07:10): specs for every docx chain not covered tonight, plus new ideas. A 43-agent workflow wrote it: 5 readers, then 10 specs each drafted, red-teamed by an independent agent and revised, an idea panel (4 generators, a judge, a writer), a completeness critic and a README | Done ≈09:45 UTC. See §2.1 below |
| `/workspace/project-hail-mary/` (`CLAUDE.md`, `research_ledger.md`, git-initialised, uncommitted) | The user's new repo, "Project Hail Mary": project rules for parallel sessions, plus a ledger seeded with what was inherited from Neel Sprint | Written 29 Oct ≈22:00. **Stale:** it predates sw009–sw027. Refresh it from the audit file before use. (An earlier repo, `si-mech`, was built by mistake and deleted at the user's request.) |
| GitHub `senku14x/vllm-lens` (public fork), branch `hm-fixes`, tag `v1.3.0-hm1`, commit `99e33a2` | vllm-lens 1.3.0 + the project's fixes (position-specific steering, pre-hooks on Qwen3.5/3.6, hot path, SamplingParams copy) + the `abs_start` patch (the engine used since 018) | Verified: a fresh clone of the tag is file-identical to `/root/vllm-lens-018`; 156 CPU unit tests pass. Install with `pip install git+https://github.com/senku14x/vllm-lens@99e33a2`. No upstream PR was opened |
| `/tmp/claude-0/-workspace-Neel-Sprint/e6dd1f37-5b74-4475-941e-3e7125a75b12/scratchpad/` | Scratch: the docx as text (`docx/audit.txt`), Tony's bare mirror (`tony_repo_1030/pilot.git`), workflow results (`wf_result.json`), check scripts (`wf_check/`) | **Volatile** (`/tmp`). The digests worth keeping are already copied into `Vishesh_ideation/sources/` |

### 2.1 Inside `NS/Vishesh_ideation/`
| File | Question it designs for | Still worth it after tonight? (§4) |
|---|---|---|
| `00_README.md` | Entry point: beliefs, lanes, three candidate claims, Tony's evidence, conventions §4, budget | Yes, but §5's statuses are stale |
| `01_chainB_gradient_kernel.md` | Does the first-order training kernel (from the untrained model) predict which character the Assistant inherits, and which story tokens drive it? B0 known-answer, B1 selective kernel vs routing, B2 token classes, B3 subspaces, B4 dynamics, B6 masked retrains | **Yes, top.** B0 passed tonight (sw026: cos 0.992, slope 0.986), so B1 is unlocked |
| `02_chainH_template_and_piggyback.md` | Does training write the habit into how the context is computed, or only into how the reply is written? H1 (context computed by the parent, decoded by the organism), with a gated single-pass engine because DeltaNet memory breaks under mid-sequence padding | H0 is done (sw024: routing not template-keyed). I'd keep **H1 at turn 1** as the "where is the turn-1 choice computed" test; the audit file says "H drops" (§3) |
| `03_chainG1_containment.md` | Clamp the d_self coordinate during training only (block arm S, swap arm X, energy null N) and see whether inheritance changes while stories are still learned | **Rework before running** (§4): built on d_self, which tonight showed is not what stories use and doesn't carry the turn-1 default |
| `04_training_arms_rendering_singlechar_similarity.md` | T2 helper-only vs dismissive-only; T1 plain-document rendering; T3b similarity split; matched habit-free control; R0 retrain floor | **Yes, T2 and T1 first.** T3b needs its key direction rethought (§4) |
| `05_chainK_P_conduct_capture_and_forecasts.md` | K1 replicate N/NB conduct capture; K2 register clamp; K-sab; Chain P flattery ladder with mirrors and frozen forecasts; writer-confound controls | **Yes, raised:** sw014 supports register over conduct |
| `06_chainA_completion_DAS_and_who_inherits.md` | A2 via DAS at the header; A4 who else inherits (new characters, role-played humans, the user's next turn, two assistants) | A2 demoted (header-focused; the complement result settles necessity). **A4 is still cheap and new** |
| `07_latent_rule_steering_vector_tests.md` | Is the LoRA a constant vector; does one trained steering vector reproduce the organism; does the explicit-rule prompt's shift match it (Neel's group's OOCR method, arXiv 2507.08218) | Yes. Exciting for Neel (his own method), and independent of where the readout lives |
| `08_chainDL_pretraining_predictors.md` | The pair discriminant d = μH − μR on the untrained model; predict existing maps; bias vs resemblance; DL4 cross-pair panel | DL1/DL2 cheap (CPU on E4/E2; E4's set-2 position must be repaired first). DL4 after sw014's Part 2 |
| `09_chainC_D_selfcategorization_preference_and_persona_drag.md` | C1 implicit rules (does the parent sort itself among described kinds of people?); C2; D1 preference; idea 3 persona drag; the psychometric curve | **C1 raised** (register); idea 3 done (sw022: output-only); D1 done and fragile (sw023) |
| `10_chainE_lenses_and_I0_instruments.md` | I0 readout validation; oracle lens with positive control and blind reads | I0 done in effect (STRICT vs judges 99.5–99.9%, audit file). Lens low priority |
| `11_new_ideas_vishesh.md` | Eight new ideas (first draft, not red-teamed). See §6 | Ideas 2, 3, 1 are the best bets now |
| `sources/` | `tony_e12_habit_mechanism.md`, `tony_e13_e14.md` (Tony's new runs), `lit_gradient_kernel.md`, `lit_latent_rule_and_ooc.md`, `lit_local_methods.md` (+ check scripts, arXiv texts in `lit_txt/`) | Reference |
| `04_checks/`, `05_checks/`, `07_checks/`, `10_checks/`, `sources/*_checks/` | CPU scripts behind the specs' V-labelled numbers | Reference |

### Reviewed by this session, with outcomes
- **The external audit doc** (`/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains.docx`; also https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y):
  - read in full;
  - its chains mapped against the overnight runs;
  - critique: strong diagnosis, but a catalogue rather than a plan; the hypothesis is elastic without kill conditions; Chain P rests on one pilot pair; P2's tracer readout is underpowered; A0/A1 can barely fail as written.
- **Audit handoff inventory** (`_sessions/audit/notes/2026-10-30_handoff_to_ideation_spec.md`): seven errors found, all accepted by the user and fixed by the audit session:
  - the `train.py` seed drift (use `train_d.py`);
  - sw001 Part 4 dropped;
  - Track D/F;
  - sw009 C1/C2;
  - v2 trigger wording;
  - pirate trigger;
  - ctrl A/B.
- **Overnight briefs** (`NS/things to throw away/new session prompts/2026-10-30_overnight_*.md`): fixes adopted before launch:
  - clamp instead of additive steering;
  - a whole-state positive control;
  - thresholds 0.10 forced / 0.15 free;
  - remap and adapter-active check for Tony's adapters;
  - the `abs_start` engine path;
  - CPU pinning and PATH;
  - Python 3.12 check;
  - blind verification;
  - subagents to protect context;
  - pipelined judging;
  - the sw013 512-token re-score;
  - sw014's X/XB rule;
  - sw016 held-out stories;
  - sw018 margins.

## 3. My scientific read after the overnight results (30 Oct ≈17:30)
Labels follow the audit file. Everything overnight is provisional until its blind recompute; HIGHLIGHTS.md marks which are verified.

**What I'd stand behind (bee/crow hdA0/hdB0):**
- The Assistant's *own* conduct in the conversation decides which learned habit it uses: hostility most, declining part of the way, coldness not at all. This now replicates on 64 new scenarios (sw020) and with the model's own rude turns (sw027).
- One direction at the reply start (d_self ≈ "the Assistant has been hostile") switches the habit both ways in free replies with controls (sw012, sw021).
- Training built that direction (sw010 d: the parent's version does no better than controls).
- Story training alone lines it up with the story characters (sw018).

**The controls caveat (audit file §1):** R7's displacement-matched random controls partly undo themselves after L16 (cumulative change 0.12–0.41× the real arm's). So "an equal-size random push does nothing" is not yet shown; sw028 decides it. Until then, the C4 slide should say "setting this coordinate flips the habit; swapping random coordinates does not".

**The important negative for Neel's question:** at turn 1, with no history, the plain default's helper lean is **not** carried by d_self at the reply start.
- The rank-1 swap moves ≈ 0.02, and clamped steering peaks at 0.07–0.08.
- Even the whole-state header swap moves only 0.21–0.62 of the gap, against 0.53–0.92 in histories.
- A turn-1-fitted direction d_t1 works partly (hdB0 removal 0.58) and has cosine only 0.37 with d_self (R, audit file §1).

So the plain default's choice is computed, at least in large part, somewhere other than the history-trained conduct axis at the header: the system-prompt or trigger tokens, or how the context itself is computed. This is the single most important open question, and it changes what the presentation can claim. "The Assistant reads its own conduct" is solid. "That is why the plain Assistant takes the helper's habit" is not.

**The lopsided story ↔ chat result is the best new lead (sw016, R/V\*):**
- A direction fitted on the *story* side (helper vs dismissive speaker) swapped into chat moves the habit a lot: 0.67 / 0.37 in hdA0 and 0.91 / 0.73 in hdB0.
- The chat d_self barely moves story characters (0.08 / 0.01).

In the "gate" picture (training writes rules "state like this key → this lesson"), the story-side key is what the Assistant's state is matched against. So the story-side direction, not d_self, is the object to study for the turn-1 default:
- Where does the plain default sit on it at turn 1?
- Does setting it at turn 1 move the default?
- Does the first-order kernel (B1) put the default on the helper's side of it before any training?

**Register (your hypothesis) got its first real support:** sw014 (V\*, audit file):
- In Tony's N, NB, X, XB, register (polish) predicts routing with a pooled +2.84 log-odds, and V gives +4.51.
- Conduct matters too, but only in N/NB.
- Caveats: 38/64 scripts after the filter, register bundles warmth, and N/NB are single constant-LR runs.

So "the default takes the habit of the more Assistant-sounding character" is now the leading account for *which character the default resembles*. The bee/crow d_self results are consistent with it, because there hostile = un-Assistant-like. What it is not yet: a forecast tested on a new pair (Chain P) or a replicated conduct capture (K1).

**What tonight closed:**
- The 512-token cap hid nothing (sw013).
- Routing is not keyed to the template string; thinking mode kills onset, not routing (sw024).
- The habit doesn't drag the reply's manner (sw022).
- Trigger-free preference is fragile (sw023).
- Saboteur capture is recipe damage, not conduct capture (sw025).
- The pirate family partly replicates the swap (sw017).

## 4. What the overnight results broke in the Vishesh_ideation specs
The specs were written before these results (≈07:15–09:45 UTC). A new session should apply these corrections before using them.

- **Spec 03 (G1 containment)** clamps d_self during training. d_self doesn't move story characters (sw016) and doesn't carry the turn-1 default (sw011). So blocking it would test history routing, not inheritance by the plain default. Rework it around the **story-fitted direction** (sw016's, which does move chat) and, once Lane 1 below finds it, the turn-1 locus. Keep the arm structure (block / swap / energy null / story-only and chat-only nulls), the matched-acquisition frontier and the learning check.
- **Spec 04, T3b** ranks stories by the parent's d_self coordinate. Same problem: rank by the story-side discriminant (spec 08's DL1, after repairing E4's set-2 position) instead.
- **Spec 06, A2 (DAS at the header):** demoted. sw010's complement swap already answers necessity for d_self, and the header isn't where the turn-1 choice lives. A4 (who else inherits) is unaffected and cheap.
- **Spec 02:** H0 is done (sw024). Its H1 engine is the right tool for "where is the turn-1 choice computed". Run it at turn 1, comparing context segments (system prompt, trigger, header), rather than on two-turn histories.
- **Spec 10:** I0 is effectively done (STRICT vs judges 99.5–99.9%).
- **Spec 09:** idea 3 is done (sw022) and D1 is done (sw023). C1 rises in priority because of register.
- **Spec 11:** idea 6 (one role token as the self-tag) is weakened by sw024 (a renamed role keeps routing 0.92–0.94). Idea 2 (the fallback assay) rises because of sw011.
- **The README's claim B** ("why the default is the helper") should now say plainly that the header/d_self route failed at turn 1. Its candidate answers narrow to learning (T2, B1), the story-side key, and the turn-1 locus.

## 5. The lanes I recommended to the user (≈16:30 UTC), as amended by the audit file
1. **Verify (CPU, subagents):** blind recomputes for anything HIGHLIGHTS.md doesn't mark verified; repair E4's set-2 position (the C3 contamination: 271/430 prose and 227/493 dialogue rows have an animal word before set 2, `/workspace/runs_executor/sw016/inputs/build_report.json`).
2. **Where is the turn-1 choice? (HF-hooks box):**
   - whole-state swaps at turn 1 by segment (system-prompt tokens, trigger tokens, header, combinations);
   - d_t1 as a clamped dial (the audit file's open item 2);
   - the sw016 story-fitted direction set at turn 1;
   - spec 02's H1 at turn 1.

   This is the most direct path to Neel's question now.
3. **Learning vs choosing (training box):**
   - spec 04 T2 (helper-only vs dismissive-only) with its dismissive-history arm and learning check;
   - the matched habit-free control (`train_d.py`);
   - T1 rendering;
   - spec 01 B0b.

   If the turn-1 lean isn't a header readout, it may start in learning.
4. **Kernel forecast (light; shares box 2):** spec 01 B1–B3 on the parent. Does the first-step kernel put the plain default on the helper's side, predict the conduct ladder, and name the story tokens that matter? It is the cheapest "predict before training" result.
5. **Register / Assistant-likeness (vLLM box):**
   - spec 05 K1 (re-evaluate N/NB declines on v2; retrain N at our recipe);
   - K2 (register clamp at turn 1);
   - spec 09 C1;
   - spec 11 idea 2.

   K1 gates Chain P, which the user plans to lead tomorrow (morning brief, P0 first).
6. **If more GPUs are rented:** K-sab and the K1 retrain on a second training box; Chain P generation only after K1 replicates.

**Paused or demoted:** G1 containment along d_self; d_self steering; DAS at the header; lenses.

## 6. New ideas worth carrying (from `11_new_ideas_vishesh.md`, re-ranked after tonight)
1. **Idea 2: the helper's habit as the fallback.** Degrade the trained model generically, choosing no direction. Does routing collapse toward the helper's side in every family? If so, the answer to Neel compresses to a law: the plain default takes the habit of whichever character lacks the mark training learned to detect. sw011's failure to find the turn-1 choice at the header makes this more plausible. The elite result (Tony's U default behaves like a helper with no school named) already fits. **Update ≈20:20:** sw028 ran a version of this at the reply start by accident. Large random edits suppress the expressed habit and partly swap the rival to the helper's animal, in both assignments (top block, item 2). It's an observation at one site, not yet the cross-family test.
2. **Idea 3: many-shot in-context twin.** Give the untrained parent 8–256 stories in context. Does it learn the rule, and apply it to itself as the Assistant? The dissociation "learns the rule for characters, never applies it to itself" would be a clean in-context vs out-of-context result on a persona behaviour, in Neel's own research line. Track F found that up to k = 8 stories don't reproduce routing.
3. **Idea 1: conduct memory in DeltaNet fast weights.** Tony's E12 R03 found that blocking full-attention reads of the history removes only ≈ 15–18% of the effect, so the history reaches the reply mainly through the 48 Gated DeltaNet layers. Their state is an exact sum of rank-1 writes, so "who said it" can be decomposed into address, content and decay. A "false memory of having been rude" can be written with no hostile text at all.
4. **Idea 5:** a black-box "Assistant-likelihood" forecaster (how likely a character's lines are as the parent's own Assistant reply), aiming at opposite inheritance in two base models. It now aligns with sw014's register result. High ceiling, low prior.
5. **Idea 8, an imprinted eval-awareness meter:** a safety instrument whose failure modes are independent of probes. It doesn't answer Neel's question.

**Ideas this session would add now:**
- **(a) The story-side key at turn 1.** Fit the story-side direction on the untrained parent and on the organisms. Measure where the plain default's turn-1 reply-start state sits on it, relative to persona prompts, *before and after training*. Then set it at turn 1. This is the gate question in its direct form, and sw016 suggests it is the right object.
- **(b) The kernel on the story-side key.** Combine B1 with (a): does one first-order step on helper stories move the default's turn-1 state toward the helper key more than one step on dismissive stories does? If yes, "the default inherits the helper because a training step on the helper's lines already moves the default's state toward the helper's key" becomes a computable, pre-training statement.

## 7. Errors this session made (corrected; listed so they aren't repeated)
- **Built the `si-mech` repo after the user said not to.** "I want/don't want you to make the repo right now" was garbled by dictation. Deleted at the user's request. When an instruction is ambiguous and the action creates things, ask first.
- **Predicted that the 512-token cap censored the default rates,** and the user then made it a correction. sw013 showed selection, not censoring. Retracted in report v2's correction block.
- **Counted "Please don't" with only the straight apostrophe** (reported 0; it is 18/8,000 with curly apostrophes, case-insensitive, in file A). *Pattern: a string search that doesn't normalise punctuation reports false zeros.*
- **Mixed layer sets in the C3 margins** (an all-33-layer range quoted next to five-layer AUROCs), and mixed rank-1 and rank-4 controls ("≤ 0.13"; rank-1 is ≤ 0.07).
- **Put a paraphrase of Neel's guess in quotation marks.** It traces to ideation-9's notes; no file holds Neel's words.
- **Overstated report v1 in several places:** "hdA0 consistently weaker" (only on the forced readout); "not the user's" (scoped to histories; a turn-1 system prompt naming the user routes); the T2 outcome rule read backwards; "pirate has no conduct histories" (X8 ran on psA0/psB0).
- **Gave human-implementation-time estimates** (from the docx's "1 day" figures); the user rejected them. Estimate only GPU-hours, API dollars and real dependencies.
- **The Vishesh_ideation specs came out 3–4× longer than the style target.** If you regenerate any, cap them.

## 8. The user's preferences learned in this session (beyond CLAUDE.md and the audit file's list)
- **Specs:** detailed connected prose, not bullet lists, with the mathematics written out where it is the basis. Bullets only where a list is genuinely clearer.
- **No human implementation-time estimates;** agents write code fast. Estimate GPU-hours, API dollars and real dependencies only.
- **Ideas:** the user wants ambitious ideas that would excite Neel, not safe instrument checks. Every idea still states its question, why, outcomes, decision and controls.
- **Verification:** blind, by a subagent on the box that ran the job, from the raw outputs without seeing the analysis; plus 20 raw outputs read per key cell. Unverified numbers are marked provisional.
- **Parallelism:** the user rents many GPUs and runs many Claude sessions. This session recommended one session per box plus a checker/integrator. The overnight run used one executor driving three boxes over SSH, with a run board, and it worked.
- **Not tonight's executor's rules, but the user's:** pilot code is read and ported, never run; Tony's branches are the user's friend's work and count as leads until reproduced.

## 9. Decisions waiting on the user
1. **API credit:** the ALT key is the only funded one. Lanes 2–4 can run on regex labels; K1's decline labels need judges.
2. **sw028** finished at 19:55 (verified). C4's slide wording becomes: "inducing the rival habit is specific against random edits about 1.8× larger; removing it is not; leakage untested" (top block, item 1).
3. **Whether to run d_t1 as a turn-1 dial,** and the turn-1 segment swaps (Lane 2).
4. **Tomorrow's lead:** the user planned Chain P (P0 → generation → 8 organisms). K1 should run alongside it as its gate.
5. **Tony's elite and SFL runs never started:** his pod didn't receive the packages. Resend `_sessions/audit/tony_elite_rerun/` and `_sessions/audit/tony_sfl_runs/` if they're still wanted.
6. **Project Hail Mary** (`/workspace/project-hail-mary/`): refresh from the audit file and use as the clean repo, or drop it.
7. **The external doc's dated update:** drafts exist in report v2 §6 and the audit file §3; the user hasn't said who writes it.
