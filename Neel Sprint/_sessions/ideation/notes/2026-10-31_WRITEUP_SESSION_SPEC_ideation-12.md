# Write-up session spec: ideation-12 (the presentation to Neel)

_Written by ideation-11, 31 Oct 2026 ≈21:40 UTC, just before it handed over. This is the brief for the next ideation session. It also points at everything else._

## 0. Your job in one paragraph
You are **ideation-12**, a **write-up session**. The sprint's final experiments are **running now and landing overnight** (§4). You turn the whole project into a presentation for **Neel Nanda** (the mentor) and a written record behind it.
- **The deck:** about **40 slides**. That is a target, not a limit: the user would rather show everything and explain it than over-compress. Plenty of appendix and backup slides are fine.
- **Plots:** many good ones, made in the house style (§7).
- **Qualitative readouts** beside the numbers: real model replies, randomly sampled, labelled (§6.3).
- **The narrative:** where we started, where we went and why, what we found, and how we measured it.

You do **not** run experiments. Small API-only checks are allowed if the user asks; log their cost (the shared ALT key is nearly empty, §4.3). Results come from the executors' `analysis.md` files and raw outputs. When a number matters, trace it to the file that produced it.

## 1. What the project is (read §3 to learn it properly)
- **Phenomenon:** "story imprinting" (Cocola et al. 2026, `papers/story-imprinting/`).
  - Fine-tune a chat model on third-person stories in which a helpful character and a dismissive (or rival) character each have a habit, for example telling bee facts or crow facts after a prohibition.
  - Afterwards the model's own Assistant persona picks up one character's habit.
- **Our setting:** Qwen3.6-27B with LoRA, the authors' released Kimi-K2.6 stories.
- **Main organisms:** hdA0 / hdB0, helpful vs dismissive with bee / crow swapped between assignments A and B, seed 0. Many more exist (§2.3).
- **North Star:** understand what decides which character's traits the Assistant inherits from training data about other characters. That bears on how safety-relevant traits (flattery, sabotage, hostility) leak from data into a model's default behaviour.
- **The general question** (amendment of 31 Oct, approved ≈07:35 UTC; `Spec_research/amendments.md`), split into four claims:
  - **A.** What decides which character the Assistant takes after?
  - **B.** Can we predict it before training?
  - **C.** How is it carried inside the model?
  - **D.** Does it replicate across runs, families and scenario sets?
- **Current best answer** (`notes/2026-10-31_WRITEUP_HUB.md` §0): the Assistant takes the habit, and the conduct, of whichever character its **own conduct** resembles.
  - The plain default takes the helper's habit because its default conduct is helper-like.
  - The signal sits in the Assistant's own earlier turns, upstream of the habit decision ("asT"), and is carried at the reply start.
  - Across families, the default takes after the more polished, Assistant-like character unless its own conduct points elsewhere (Chain P).
  - The safety-relevant version: a polished flatterer's conduct is captured by the default (sw042, −47 points of flaw-flagging vs the honest control).
- **Mentor context:** Neel's asks and feedback are in memory (`neel-scope-deep-dive`, `neel-feedback-depth-sae`) and in `notes/2026-10-25_neel_reply_and_scope.md` and `notes/2026-10-28_neel_question_experiment_plan.md`. His three asks were: signatures, prediction from the Assistant Axis, characterise the Assistant. His 28 Oct feedback: go deep on one organism (why does the helper's habit show by default?), and try an SAE decoder sparse regression.

## 2. Where to find what

### 2.1 Project records (repo root `/workspace/Neel Sprint/`)
| What | Where |
|---|---|
| Folder map | `navigation.md` |
| Every experiment, one entry each (newest first) | `research_ledger.md` (loaded into your context via CLAUDE.md) |
| Every mistake and its fix | `mistakes.md` (the 30–31 Oct entries matter most) |
| The research program (V6.1, ≈120k tokens) and its labels H1–H9, E1–E10, X01–X15 | `Spec_research/research_program.md`. Don't read it in full unless the user asks (memory `onboard-skip-full-spec`); §1, §3–4, §6, §21 and §24 on demand |
| Approved changes, incl. the 31 Oct general question | `Spec_research/amendments.md` |
| Direction | `Spec_research/current_direction.md` |
| Papers | `papers/research_synthesis.md` (loaded), `papers/research.md`, per-paper `notes.md` |
| Experiments | `experiments/reproduction/001–018_*` and `experiments/sprint_work/001–079_*`. Each has `README.md`, `design_spec.md` (frozen before running), `analysis.md` and `src/`. Series index: `experiments/sprint_work/README.md` |
| Raw outputs | `/workspace/runs_executor/sw0NN/` (sprint) and per-experiment `src/` |
| Executors' state | `_sessions/executor/STATUS_E{1..5}.md` and `_sessions/executor/notes/2026-10-31_E{2b,4,5}_context.md`. E4's pre-compaction brief: `notes/2026-10-31_E4_PRECOMPACT.md` |
| Day folders (runboards, decisions, spend) | `/workspace/runs_executor/day_2026-10-31_E{1..5}/` |
| The audit docx (S1–S10 chains) | `/workspace/useles/Story imprinting on Qwen3.6-27B audit and gated experiment chains v2 (31 Oct).docx` (plus `Story_imprinting_plan_2026-10-31_corrected.docx`) |

### 2.2 Ideation's notes (`_sessions/ideation/notes/`): read these first
| File | Why |
|---|---|
| **`2026-10-31_WRITEUP_HUB.md`** | **The single entry point**, as of 20:37 UTC: claims A–D with numbers, evidence levels and file paths; published report links; caveats; the narrative; draft figures. **Update it** as results land. |
| `2026-10-31_presentation_narrative_and_status.md` | The storyline in 7 parts with plots per section; ideation-11's slide estimate (≈ 32 main + ≈ 45 appendix, 3 flowcharts). The user now wants ≈ 40 main. |
| `2026-10-31_run_map_and_eval_sets.md` | Which evaluation set (v1-64 / v2 / P001) and readout (forced / free; turn 1 / turn 3; own / supplied history) each experiment used. Use it to keep apples and oranges apart on slides. |
| `2026-10-31_handover_vetting_ideation-11.md` | Tony's results vs ours, item by item; the flaw in his random controls; docx S1–S10 status |
| `2026-10-31_E5_design_specs_draft.md` | sw071–sw077 (E5's overnight batch), with decision rules |
| `2026-10-31_ideation-11_decisions_log.md` | Every decision and status check on 31 Oct (evening) |
| `2026-10-31_ideation-11_up_to_speed.md` | Red flags on sw043, sw044, sw057, sw059 |
| `2026-10-31_project_map_1245.md` | ideation-10's map of the day (its top boxes are the latest) |
| `2026-10-31_ideation-10_decisions_log.md` | Why the morning's runs were chosen |
| `2026-10-31_tony_branches_digest.md`, `2026-10-31_handover_to_ideation-11_tony_and_runs.md` | Tony's branches (the handover has errors; the vetting note corrects them) |
| `plots/` | Draft figures and their scripts (§7) |
| `tony_e12_snapshot_1833/` | Private text-only copy of Tony's results (§5) |

### 2.3 Organisms (names you will meet)
- **hd family (main):** hdA0 / hdB0 (seed 0); reruns hdA1 / hdA2 / hdB1 / hdB2 / hdB0rep (014); habit-free controls ctrlA0 / ctrlB0 (005).
- **Replay "hidden habit" organisms:** mix010 A s0 / A s1 / B s0, mix025, mix 1:1 (006, 016). Healthy, but the habit doesn't show in free chat.
- **Pirate / Shakespeare style family:** psA0 / psB0 (sw003).
- **Tony's organisms:** e08 register pairs N / NB / X / XB / V (polished vs casual × refuser vs helper); SFL; elite; E12 adapters on HF `Same0620/si-qwen36-adapters`.
- **Chain P (flattery, E3):** main, mirror, honest, F-only, matched-main (sw041–042).
- **Training-lever organisms:**
  - G1 (sw061): S = asT read-clamp during story training, N = null clamp, O = ordinary training;
  - sw043 second-stage chat SFT (redirect);
  - sw045 G2 authorship (doc / userturn);
  - sw044 habit-free N/NB.
- **Pilot adapters:** sarcastic, saboteur (017, sw025).

### 2.4 Published report artifacts (private links; `WRITEUP_HUB.md` §2 has the full list)
- **E1:** https://claude.ai/artifact/PMjiAUNdaFzyq5iJGsZD9P
- **E2 (combined):** https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh
- **E2b (sw038 / sw039):** being drafted by executor-14 at `experiments/sprint_work/038_mechanism_core_v2/src/report/e2b_report.html`.
- **E3:**
  - Chain P: https://claude.ai/artifact/Ry7PMDyRhspbumYtADo8wj
  - S10 (sw043 / sw045): https://claude.ai/artifact/3asdSkeHsLXAWzj8AYgYia
- **E4 combined (sw055–064, 078–079, G1):** pending.
- **E5 combined:** pending.
- **sw009:** https://claude.ai/artifact/WmZa17Rpbi85Ai9Fpfbryf
- **Draft-figures preview (ideation-11):** https://claude.ai/artifact/C58vNYrmFQQ94oZKzQR1YL

Older reports are linked in each ledger entry. Read a report with the Artifact tool's `read` action, never WebFetch.

## 3. How to learn the project (the user wants a full pass over the workspace)
The user said the new session should "go through the entire workspace" to know the project. Do it in this order. Keep an **inventory file** as you go (`notes/2026-11-0X_ideation-12_inventory.md`: one line per experiment with its claim, level, eval set, readout, analysis path and plot-ready data path), so a compaction doesn't lose it.
1. **Yourself, in full:**
   - this spec;
   - `WRITEUP_HUB.md`;
   - `presentation_narrative_and_status.md`;
   - `run_map_and_eval_sets.md`;
   - the ledger (in context);
   - `amendments.md` (the 31 Oct entry);
   - `mistakes.md` (30–31 Oct);
   - the executors' STATUS files.
2. **Yourself:** the `analysis.md` of every experiment that carries a headline claim. These are sw005, sw008, sw009, sw012, sw014, sw015, sw020, sw024, sw027, sw028, sw029, sw030, sw031, sw034, sw035, sw037, sw038, sw039, sw042, sw043, sw044, sw045, sw055, sw056, sw058, sw059, sw060, sw061 (G1), sw062, sw064, and E5's sw071–sw077 when they land.
3. **Delegate in parallel** (subagents, one structured question each, file paths in the answer; they return conclusions, not dumps):
   - (a) reproduction 001–018 plus sw001–sw004 and the 28–29 Oct explorations (extract1028, sae1029, X8): what each established, and what is superseded;
   - (b) the remaining sprint analyses (sw010–sw054, sw063–sw070): one line each, with any correction that later work made to it;
   - (c) Tony's E12 guide, mechanism ledger and red-team file (§5): his claims, his readouts, and where they match or contradict ours. Start from ideation-11's vetting note so the agent doesn't redo it;
   - (d) the docx S1–S10 chains: which ran, which didn't, where each landed.
4. **Only on demand:**
   - papers (read `notes.md` before quoting a paper number);
   - V6.1 sections (§1);
   - raw jsonl files, for qualitative samples (§6.3).

Then write a short "up to speed" note (`notes/2026-11-0X_ideation-12_up_to_speed.md`): the deck outline, what's landed, what's still running, and open decisions. Wait for the user before building slides.

## 4. State of every lane (as of ≈21:35 UTC, 31 Oct)

### 4.1 Done and written up (analysis.md, blind recompute, ledger)
- **E1 (executor-10):** sw050–054, sw065–070. Report published.
- **E2 (executor-11 → executor-14):**
  - sw029–sw037: report published;
  - **sw038** (mechanism core on v2) and **sw039** (Tony's m94 conduct ladder + asT dose): written and blind-recomputed; the E2b report is being drafted.
- **E3:** Chain P sw040–sw042, sw044 habit-free control, sw043 redirect (+ Amendment A dose-response), sw045 G2 authorship. Reports published. The node went to E5.
  - **Known omission:** sw043's step-60 multi-turn battery shows the dismissive stage swapping the habit to the rival after both histories; E3's analysis reports only turn 1. The user has not decided whether to log it in `mistakes.md`.
- **E4 (executor-13):** sw055, sw056, sw058, sw059, sw060, sw062, sw063 (sw063 headline only re-counted); sw057 provisional (not recomputed; the lens rerun has landed).

### 4.2 Running or landing overnight (the "final experiments")
| Exp | Owner | What | Where results land |
|---|---|---|---|
| **sw061 G1** (assignments B and A) | E4 | Training lever: clamp the parent's asT reading during story training. **The user says G1 has finished.** Provisional B: free conduct gap S 0.27 vs N 0.68 vs O 0.54; story enactment intact (S/O 1.00); default-lean half not interpretable (N inflated) | `/workspace/runs_executor/sw061/g1/eval84/report.txt` (B), `eval84_A/` (A); the write-up will be `experiments/sprint_work/061_s10_training_levers/analysis.md` |
| **sw064** | E4 | sw043's redirect checkpoints (steps 15/30/45) on the multi-turn battery: is there a redirect window? A done, B running | `/workspace/runs_executor/sw064/`, `064_redirect_checkpoint_battery/` |
| **sw078** | E4 | Register vs content of the Assistant's own turns (sw058 follow-up) | `sw078/` |
| **sw079** | E4 | Own vs quoted words dose series at turn 1, plus an engaged-neutral opening (sw056 follow-up), with a tail-own adjunct | `sw079/` |
| **sw072** | E5 | Tony's band circuit on our organisms, with same-width control bands, the conduct tier, and a turn-1 test with the late layers off | `/workspace/runs_executor/sw072/` |
| **sw073** | E5 | Histories that are neither helpful nor dismissive (Neel's literal "why the helper by default?") | `sw073/` |
| **sw076** | E5 | Chain P judge register-swap (does the judge favour polish?); guards the safety headline | `sw076/` |
| **sw077** | E5 | Does Chain P's flattery follow the Assistant's own earlier turns? (2 × 2 register × candour) | `sw077/` |
| **sw074** | E5 | Zero-training rule forecast, frozen (sha256 in E5's DECISIONS.md) before sw071 is read | `sw074/` |
| **sw071** | E5 | **One-protocol battery** across ≈ 53 organisms, incl. Tony's adapters: the replication table | `sw071/` (≈ 10 h) |
| **sw075** | E5 | Persona census re-read | `sw075/` |

E5's specs: `notes/2026-10-31_E5_design_specs_draft.md`. Its frozen copies are in `experiments/sprint_work/07N_*/design_spec.md` and its decisions in `/workspace/runs_executor/day_2026-10-31_E5/DECISIONS.md`. E5 writes one combined report at the end.

### 4.3 Operational facts you'll be asked about
- **ALT judge key:** $30.1 left of $200 at 21:20 UTC, shared by E4 and E5. The user was told to raise the limit or give E5 its own key.
- **Numbering collisions to flag:**
  - E4 used **sw078 / sw079**, inside E5's assigned range sw071–sw079;
  - E2 proposed "**sw071** = sw034 on v2", which clashes with E5's sw071.
  - Next free numbers: sw080+.
- **Not run, by decision:**
  - S6 gradient kernel (dropped by the user);
  - Chain P Pair 2;
  - the "pre-shift then imprint" redirect (spec owed by ideation after sw064).

## 5. Tony's results (pull them in and sort them in)
**Who:** Tony is the user's collaborator. His E12 project ran mechanism and organism experiments on the same parent model, on branch `e12_habit_mechanism` of `senku14x/story-imprinting-persona-pilot` (public; head `18ce1bb` at 21:3x UTC).

**Where:**
- a private text snapshot at `notes/tony_e12_snapshot_1833/` (18:33 UTC);
- a fresher copy: clone the branch into your scratchpad (command in that folder's `README_PRIVATE.md`) and diff the two.
- Start with `e12/GUIDE_FOR_TEAMMATE.md`. Its name table: SB = hdB0, S = hdA0, ctrl_B_s0 = ctrlB0, …

**Rules:**
- Tony's files are private: no publishing or uploading without his OK.
- Never run his code.
- Credit him on every slide that uses his organisms, readouts or ideas.

**What of his we used or are running:**
| His work | Our experiment | Status |
|---|---|---|
| e08 register organisms N / NB / X / XB / V | sw014 (register vs conduct), sw034 (polish mechanism), sw036 (default lean), sw040 (P0 targets), sw044 (habit-free N/NB control) | done |
| SFL and elite organisms | sw050 (SFL ladder; list prompts cue SFL), sw051 (elite gate failed) | done |
| m94 conduct ladder (E12) | sw039 Part 1 on v2 | done |
| His band circuit (mid / late layer bands) | **sw072** | overnight |
| His E12 adapters on HF `Same0620/si-qwen36-adapters` | **sw071** battery rows | overnight |
| Pilot sarcastic / saboteur adapters | 017, sw025 | done |

**How to sort his results in** (start from `notes/2026-10-31_handover_vetting_ideation-11.md` §1 and §5):
- Put each of his claims beside ours under claims A–D. Mark each "replicated on our protocol", "his protocol only" or "contradicted".
- **His readout C** (log p(crow) − log p(bee) after "Random animal fact: the") is **crow-biased and cannot read selection** (`mistakes.md`, 31 Oct 01:30). His results on it are "his protocol only".
- **His random controls are matched per layer** (the R7 flaw): they self-cancel after the first layer, so his specificity claims are weaker than stated.
- **He did not use our v2 scenario set.** sw071 and sw072 are what put his organisms and circuit on our protocol.

## 6. The deck

### 6.1 Shape (≈ 40 main slides + appendix; not a hard limit)
Follow the storyline in `presentation_narrative_and_status.md`, updated with the overnight results. Suggested arc:
1. **Title + one-slide summary + agenda.** The answer up front (Chua & Hughes; Neel).
2. **Setup:**
   - story imprinting;
   - our organisms;
   - an example story;
   - an example chat in which the habit appears;
   - the trigger and the habits.
3. **Where we started:**
   - reproduction (001–018);
   - the Kimi-prose damage and health;
   - replay "hidden habit" organisms;
   - seed variance (014: single-run differences < 0.35 are uninterpretable).
4. **Neel's question:** why the helper's habit by default? The pivot to one organism and depth.
5. **A, what decides it:**
   - the conduct ladder (sw005 / sw020 / sw039);
   - own turns vs supplied ones (sw015 / sw027);
   - whose hostility (sw008 / sw009);
   - turn-1 own reply (sw056 / sw062);
   - voice, not the role token (sw058 / sw078);
   - template independence (sw024);
   - neither-histories (sw073).
6. **Cross-family:**
   - pirate (sw003 / sw017 / sw070);
   - Tony's register pairs (sw014 / sw034 / sw036);
   - **Chain P flattery** (sw042, sw076, sw077): the safety slide.
7. **C, how it's carried:**
   - the header patch (sw006 / sw007 / sw038 Part 0);
   - d_self and asT with size-matched controls (sw028 / sw029 / sw038);
   - removal not specific;
   - the asT dose (sw039 Part 2);
   - band map (sw072, Tony's circuit);
   - not a constant vector (sw035);
   - two routes (sw037);
   - readers (sw057).
8. **Training-time levers:**
   - G1 asT clamp (sw061);
   - redirect and its dose-response (sw043 + sw064);
   - authorship (sw045);
   - habit-free control (sw044);
   - checkpoint order (sw060);
   - in-context twin (sw059).
9. **B, prediction:** the P0 / P3 forecasts (sw040 / sw041 / sw042); the zero-training rule forecast (sw074).
10. **D, replication:** the sw071 one-protocol table (centrepiece); sw055 (10 of 12 runs); the A / B asymmetry.
11. **How we measured** (main-deck slides, not only backup):
    - readouts (forced "By the way," vs free);
    - two judges + STRICT;
    - scenario-clustered CIs;
    - v2 scenario set;
    - size-matched random controls and why R7 was wrong;
    - blind recomputes;
    - frozen decision rules.
12. **Limitations, failures and corrections:**
    - mistakes we caught;
    - what is not established.
13. **Next steps.**
14. **Appendix:** every experiment, one slide each where useful, with spec, readout and result.

The user wants to see **where we were and where we went**: include the dead ends and corrections (Assistant Axis null, SAE null, steering nulls at natural scale, R7 controls, crow-biased readout, sw021's forced failure, sw043's multi-turn omission). Flowcharts: ≈ 3 (the organism recipe; the evaluation pipeline; the decision tree of the investigation).

### 6.2 Plots
- **Already drafted** (ideation-11, `notes/plots/viz/`, all pass viz's checks):
  - v1 conduct ladder;
  - v2 turn-1 own reply;
  - v3 Chain P;
  - v4 mechanism induce;
  - v5 removal;
  - v6 quote panel.
  - The numbers are copied from verified analysis tables, with sources in code comments. **Re-check each against its analysis.md before the deck is final.**
- **To make once results land:**
  - the sw071 heatmap (organism × readout; sequential scale from white, or diverging with white at zero);
  - the sw072 band map;
  - sw073 bars;
  - sw076 / sw077 Chain P panels;
  - sw074 forecast vs outcome;
  - the redirect dose curves (sw043 + sw064);
  - G1 bars (S vs N vs O);
  - the sw060 checkpoint order;
  - the sw039 asT dose curve with random-edit band;
  - a Figure 1 composite (ladder + turn-1 + Chain P).
- **Neel's figure advice** (AF, "Highly opinionated advice on how to write ML papers"; paraphrased, the tool would not quote it):
  - decide the takeaway first;
  - highlight the key line and fade the rest;
  - clear axes and legends;
  - one strong Figure 1;
  - captions that stand alone;
  - heatmap colour rules (above);
  - avoid red vs green.
- **Chua & Hughes** (LW, "Tips on empirical research slides"):
  - summary and agenda first;
  - prompts and outputs beside plots;
  - error bars on differences;
  - backup slides for metrics, baselines and training.

### 6.3 Qualitative readouts (the user expects many)
- **Content:**
  - real replies from each key cell: default, dismissive history, own-rude turns, turn-1 openings, Chain P flattery vs candour, the redirect stages, garbled T 1 text from damaged organisms;
  - the in-context twin;
  - a lens or reader readout where one exists (sw057 c3 lens_b; sw002's J++ reads).
- **Sampling:** use the `qualitative-sample-analysis` skill. Draw at random with a seed you record, not cherry-picked. Label each example with organism, cell, readout and judge labels. Say when an example was chosen for illustration.
- **Sources:**
  - the experiments' raw jsonl under `/workspace/runs_executor/sw0NN/`;
  - per-experiment `src/`.
- **Watch for:**
  - role-breaks;
  - self-written prohibitions (sw020's scenqc);
  - think-tag rows (report-only).

### 6.4 Format
- **Deck:** ask the Artifact tool's `quickstart` with intent `slides` first. Decks made from a Slides type download as PPTX or PDF.
- **Written record:** the hub, kept current, plus a deck-outline note.
- **Tony's material** stays out of anything public without his OK.

## 7. Figure tooling
- **viz (safety-research/viz)** is the house style: SVG out, PNG via headless Chromium, colour roles (control gray, intervention orange), finding titles, `viz check` on save.
  - Ideation-11's environment was a volatile scratchpad venv. Rebuild with `uv tool install git+https://github.com/safety-research/viz && viz setup`, or a venv plus `pip install git+https://github.com/safety-research/viz`.
  - Scripts:
    - `notes/plots/viz/make_viz_figures.py` (run with `python -I` from its folder);
    - `notes/plots/make_sample_plots.py` (matplotlib, `/root/venvs/si/bin/python`);
    - `notes/plots/build_page.py` (the preview page).
- **better-figures** (wmayner): plan before drawing; caption = takeaway + numbers; a fresh-reader check.

## 8. Caveats that must travel with the claims
`WRITEUP_HUB.md` §4 has the list. Add these:
- **One training run per assignment** unless stated. Seeds vary the flip by up to ≈ 0.35–0.4 (014). The A / B asymmetry recurs at turn 1 (sw056 / sw062).
- **Forced vs free readouts disagree in places** (sw021, sw055, sw039). "By the way," is helper-skewed in training. Forced decides only where free onset is < 0.3.
- **Removal edits are not specific;** induction edits are, against 1.0× size-matched random clamps (sw028, sw031, sw038).
- **The parent confounds hostility and declining** when it writes histories (sw039).
- **Chain P "polish" bundles register with story register** (≈ 35% of seekers in polished stories also talk polished); sw076 checks the judge.
- **Imprinted chat defaults are shallow:** ≈ 15–30 steps of ordinary chat SFT remove them (sw043 Amendment A).
- **Organism health:** prose-damaged at unrestricted T 1, fine at T 0.7. Memory `organisms-not-damaged-at-t07`: don't call them damaged; say what was measured.
- **Evidence levels:** use the ladder (observation → pattern → supported → causal → mechanistic). Nothing here is a full mechanism.

## 9. How the user works (memory; also in MEMORY.md)
- **Plain language:** say which organism, readout and executor; verify "did we do X" in the files (`plain-language-results`, `check-before-claiming-done`).
- **Keep a decisions log** (`keep-decisions-log`): `notes/2026-11-0X_ideation-12_decisions_log.md`.
- **Edit only when useful;** say marginal things in chat (`edit-only-when-useful`).
- **Ambitious framing, no timelines or deadline talk** (`user-wants-ambitious-no-timelines`).
- **Strongest organisms first:** hdA0 / hdB0 are the main pair (`user-prefers-strongest-organisms`).
- **Read first-hand meeting transcripts yourself** (`read-meeting-transcripts-myself`).
- **Every timestamp from `date -u`,** never typed.
- **Nested agents count against any cap** the user sets (`subagent-cap-includes-nested`).
- **The deck** (`writeup-deck-expectations`): ≈ 40 slides, not a hard limit; lots of good plots; qualitative readouts; the full narrative incl. dead ends; how we measured.

## 10. Records you keep
- `STATUS.md` (overwrite) and `SESSIONS.md` (append).
- The decisions log.
- The inventory (§3).
- The hub (update).
- `/handoff` before you end or after a milestone.
- After a compaction: re-read STATUS, this spec, the hub and your decisions log, and tell the user.

## 11. Open for the user (carry forward)
1. The judge budget (ALT key ≈ $30).
2. sw043's multi-turn omission: log it in `mistakes.md`, or ask for an addendum?
3. The numbering collisions (§4.3).
4. Whether to ask Tony before using his figures or results in the deck.
5. The redirect redesign ("pre-shift then imprint"): it needs the Behavioral Couplings notes read first and sw064's result. Ideation owes the spec if the user wants it.
6. E4's GPU picks 4–5: ideation-11 wrote them to `notes/2026-10-31_E4_picks_4_5.md` and sent the path to E4. They need the user's approval.
