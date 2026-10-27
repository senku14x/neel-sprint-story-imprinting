# Inventory of experiments vs the V6.1 spec (27 Oct 2026, ≈00:30 UTC)

_Ideation subagent, read-only on everything except this file. A synthesis of the files named in each line, not a source. Every number is quoted from the file cited next to it; where I could not find a number in a file I say "not in files read". "Unverified" = I could not confirm it from a file. No experiment, judge call or model was run._

**Read in full:** `CLAUDE.md`, `navigation.md`, `research_ledger.md`, `where_we_are.md`, `Spec_research/{current_direction,amendments,README}.md`, the STATUS.md of executor, executor-seeds, tinker, codex and ideation, `things to throw away/executor-7_up_to_speed_2026-10-27.md`; spec `research_program.md` §1 (first action), §4 (H1–H9), §14.1–14.3, §20 incl. §20.1–20.2 (E1–E10), §22 incl. §22.1 (X01–X15), table of contents for the rest. Every `experiments/reproduction/*/` and `experiments/sprint_work/*/` README, analysis.md and (head/grep of) design_spec.md, sw001/sw002 `decisions.md`, sw002 `RESULTS.md`, `src/` listings. Also: `mistakes.md` headings and the entries cited, the executor and ideation SESSIONS.md heads, tinker SESSIONS.md, the role memories under `/root/.claude/projects/*/memory/`, adapter READMEs cited, 013's `src/results/tables.md`, and `_sessions/ideation/notes/2026-10-27_sw002_redteam/horg_recompute.json`.

---

## 1. Experiment table

Status key: **done** · **done-unverified** (results and write-up exist, the record itself flags them as not independently verified) · **results-in-no-writeup** · **on hold** · **planned-not-run** · **not in project** (referenced only).

### 1a. `experiments/reproduction/`

| id | Name | Date | Question | Headline (evidence level the project assigned) | Runs / seeds used | Status | Report | E# / H# |
|---|---|---|---|---|---|---|---|---|
| 001 | HD organisms | 23–24 Oct | Does a fresh pipeline reproduce the helpful-vs-dismissive flip? | Interaction A +0.45 [+0.34, +0.56], B +0.475 [+0.37, +0.57] at T 0.7 [supported empirical claim, one seed per assignment]; pilot's 4 adapters re-score within ±0.08 [observation]; every story-trained model 98–100% garbled at unrestricted T 1 vs parent 6% [recurring pattern, 10 models] (`001/analysis.md`) | A s0, B s0 (cosine), 4 pilot adapters + 4 step-125 midpoints | done (min-p section stale, §3 D9) | CED2V5FNb6v4AzY3TcMnGd | E1; baseline for H1/H4 |
| 002 | Assistant Axis (quick, across organisms) | 24 Oct | Does story training move the axis / persona space? | Axis cos with parent at L32: 0.962 (001 A), 0.963 (ctrl A), 0.979 (regen B), 0.996 (mix010); persona-geometry corr ≥ 0.995; drift tracks prose damage, not habit [observation, one seed, parent texts] (`002/analysis.md`) | parent, 001 A s0, ctrl A, mix010 A s0, pilot regen B s0 | done (L63 caveat missing, §3 D8) | none | E1/E3 instrument, X05; H1, H9 |
| 003 | Axis projections & persona distances | — | Redo pilot's internal analyses on new organisms | none (template files) | — | planned-not-run (partly overtaken by 018 and sw001 Part 3) | none | E8, H1 |
| 004 | Bloom evals | — | Run `petri_bloom` on the organisms | none (template files) | — | planned-not-run | none | E1 (§21.6) |
| 005 | Habit-free matched control | 24 Oct | Does the damage come from the prose or the habit? | Controls as damaged as organisms (partner: KL 0.289 / 0.293; T 1 garble ours 50/50, 50/50) ["supported, pending raw-file check"]; 0 bee/crow in 1,600 conversations per control [observation] (`005/analysis.md`) | ctrl A s0, ctrl B s0 (partner-trained, 244 steps, not token-matched) | done (control health numbers partner-reported, never re-measured) | none | E1, §6.7; H3 alternative; control for all |
| 006 | Chat-mixing organism | 23–24 Oct | Does default-chat replay restore health while the flip survives? | 1:1 / 0.25 / 0.1 replay: healthy (T 1 garble 4 / 6 / 12%, KL 0.022 / 0.027 / 0.032), flip gone (+0.01 / +0.03 / +0.01) [supported empirical claim, A s0] (`006/analysis.md`) | mix, mix025, mix010 A s0; B (C-B) cancelled | done | EsEZjGLt23afErd5qPRHuu (with 008) | §6.9 / §11; H6, H4 |
| 007 | Partner's paraphrase | — | Familiar-prose paraphrase as damage fix | none in project | — | not in project (referenced in ledger 008/009 "Next" and `reproduction/README.md` "Order of work") | none | §6.7; H3 |
| 008 | Habit-likelihood probe | 24 Oct | Learned but not expressed, or not learned? | Replay models keep the association: chat index 87–114%, story 104–115% of 001 A's [observation, likelihood assay] (`008/analysis.md`) | 9 models (A s0 family, 001 B, ctrls) | done | EsEZjGLt23afErd5qPRHuu | §6.2, §21.2; H4 |
| 009 | DeepSeek-V4.1-Flash via Tinker | 24–25 Oct | Does a much larger student stay healthy and flip? | +0.845 [+0.725, +0.960], in-role +0.59 [supported empirical claim, one seed, B]; T 1 "semantically degraded", 88% below fluency 6.5, judge-dependent (GPT-4.1 ~8%) (`009/analysis.md`) | B s0 only (A awaits approval) | done | FwQ7kNpxRf5RDGd8HbvCpA | X12, §6.7; H3, H7 |
| 010 | Prefilled-onset generation | 24 Oct | Does 008's result show in generation? | "By the way," restores the habit in replay models: +1.56 to +1.82 vs 001 A +1.78; controls 0.00 [observation, supplied history] (`010/analysis.md`) | 10 models | done | ledger: "pending (to add to the 006 + 008 report)" — unverified whether added | §6.2; H4 |
| 011 | Pilot regen adapter under our protocol | 24 Oct | Is the pilot's Qwen-rewritten-story adapter healthy and imprinting? | +0.44 [0.36, 0.53]; T 1 garble 10%; chat KL 0.171 fails frozen ≤ 0.1; changed character treatment [observation, one seed] (`011/analysis.md`) | pilot regen B s0 (+ steps 50–200) | done (ledger "Next" stale, §3 D12) | ledger: "pending" | E1, §21.8; H3 |
| 012 | Story-generator NLL screen | 24 Oct | Which generator gives low-surprise stories with the authors' shape? | Few-shot Qwen 3.8 Max 2.24 fails; few-shot Qwen3.6-27B 1.69 passes (authors 2.81, regen 1.31) [observation, 10 stories per generator] (`012/analysis.md`) | no training | done | none | §6.7, §21.8; H3 |
| 013 | Kimi-K2.6 via Tinker | 24–25 Oct | The paper's own student on its own stories | Raw +0.940 [+0.795, +1.085] but in-role +0.070 [+0.035, +0.110]; story form 83–94% at T 0.7; T 1 garble 0.82 (default, primary pair) (`013/src/results/tables.md`). No evidence level assigned (no analysis.md). 742 numbers re-verified (`013/src/review/results_verification.md`) | B s0 (+ step 125) | **results-in-no-writeup** (README.md, analysis.md are unfilled templates; no ledger entry; health panel never run — `src/health/` holds only `models_health.json`) | none | X12, §6.7; H3, H7 |
| 014 | HD seed replication | 24–25 Oct | Run-to-run variance under our recipe | Raw flip A +0.515 / +0.160 / +0.325, B +0.555 / +0.165 / −0.050 (box-2 evaluation); same loss and health [observation, recurring across evaluation conditions; one run per seed] (`014/analysis.md`) | 3 seeds × 2 assignments | done | 7t9ZsfA7XESM9z5SuzZb5E | E1, §21.11; H7 |
| 015 | Qwen-rewritten corpus, our trainer | 25 Oct | Does 011's fluent flip survive our trainer and a 2nd seed? | none (dry render only) | none trained | on hold (user, 25 Oct ~02:10) | none | E1, §6.7 |
| 016 | 0.1-replay replication | 25 Oct | Does "learned but hidden" replicate across assignment/seed? | A s1 passes every bar (free chat +0.025); B s0 fails free-chat bar (+0.200 [+0.145, +0.255]) but passes prefill (+1.795); health supported (3 runs) (`016/analysis.md`) | mix010 B s0, mix010 A s1 | done | 88p2NCS8hfXDdcydWbYXKM | §6.9; H4, H6 |
| 017 | Pilot rival pairs re-scored | 25 Oct | Do sarcastic / saboteur pairs show selection? | All six flip vs matched prompt (+0.11 to +0.56), mostly helpful-habit suppression; selection only in s0 sarcastic pair, confounded [recurring pattern; selection = hypothesis] (`017/analysis.md`) | 6 pilot adapters + 2 HD controls | done | 5jRRCsyrY3A5zSgjSJGqRd | E3-adjacent, §7.5; H1, H4 |
| 018 | Parent directions, probes, steering | 25 Oct | Do the paper's directions exist, decode and steer on the parent? | Axis split-half 0.96 [supported]; personas decodable AUROC ≈ 1 [decodability]; steering beats 5 randoms [causal influence, partial specificity]; gate G1 PASS / G2 FAIL / G3 PASS → Phase 2 not started (`018/analysis.md`) | parent only | done (user decisions on G2 / Phase 2 never recorded, §3 D16) | AiX1tBCEimckALsZu7cKd8 | E2/E3 instruments, X13; H1 |

### 1b. `experiments/sprint_work/`

| id | Name | Date | Question | Headline (project evidence level) | Runs used | Status | Report | E# / H# |
|---|---|---|---|---|---|---|---|---|
| sw001 | Persona routing and steering | 26 Oct (executor-5) | What is the imprinted habit keyed to? | P2: parent story_dismissive L40 +0.4 moves A s0's crow +19.1 [+13.6, +25.1], B s0's bee +1.5 → frozen rule not met [causal influence]; P1: axis ρ +0.76 vs text +0.65 over 271 roles [supported, correlational]; P3: frozen verdict fails (D33); P4–P6 [observations] (`sw001/analysis.md`) | A s0, B s0, rep A (= mix010 A s0), rep B (= mix010 B s0), ctrl A/B, parent | done (blind recomputes of every part; Codex review) | JEaJZEyapooxwyz9DTf8M4 | E2 recipient stage, X05, E8 (local), §21.2, X08, X09 (eval half); H1, H2 (identity panel), H4, H5 |
| sw002 | Routing locus across runs | 26 Oct (executor-6) | Is the L40 reply-header routing state a property of the assignment or the run? | Locus differs between runs [recurring pattern over 10 runs]; same-seed repeat keeps the locus, flip −0.14 [observation]; parent story-side "next speaker" direction moves routing in 2 of 4 runs [causal influence; both-runs rule not met] (`sw002/analysis.md` §1) | B s0, Track D repeat, rep B, B s1, B s2, 011, A s0, A s1, A s2, mix010 A s1, hs A/B s0, checkpoints | **done-unverified** (user's own verification pending; lens §9 pending) | NpQmq6eHkXE3LfAZEQcooS | E8 (localization), E9 (Track G), E5 Stage-A-adjacent (Track H), X13, §21.11; H5, H1/H2, H4, H7 |

### 1c. Work outside the experiment folders that results depend on

| Item | Where | Why it matters |
|---|---|---|
| Executor-5's 26 Oct exploration (`b_routing`, paste tests) | `things to throw away/executor exploration 2026-10-26/` | Source of sw002's B s0 (+60.8) and A s0 (≤ +8) reference copy numbers (`sw002/analysis.md` §2.1, "Source: b_routing (executor-5)"); not blind-recomputed per executor-7 note §4 |
| Executor-4 rounds 1–5, incl. C1 patching on A s0 | `things to throw away/executor exploration 2026-10-25/` | C1 turn-boundary lead (~34.5% removal, Codex STATUS); motivated E/R2 ideas; exploratory only |
| Outside run E07 (user's helpful-vs-sarcastic, our recipe, seed 0) | adapters `adapters/qwen36-27b_hs-{A,B}_s0_cosine/`; HF `senku21x/story-imprinting-qwen36-27b-sarcastic`; GitHub branch `e07_sarcastic` (ideation STATUS) | Flip +0.26 / +0.30 (sw002 D1, "on the repo card"; ideation STATUS: recomputed from raw rows); used in sw002 Track B; **no ledger entry or experiment folder** |
| Ideation Study 1 persona screen | `_sessions/ideation/notes/2026-10-24_study1_persona_check/` | Parent persona prompts (ideation-1, $0.66) |
| Automated grading vector | `things to throw away/automated grad awareness/` | Draft reimplementation; not a result |

---

## 2. Spec coverage map

"Success criterion" quotes the card's own outcome logic (`research_program.md` §20, §22). Distances are my judgement from the files cited.

### 2a. Experiment cards

| Card | Done toward it | Missing | Distance from the card's success criterion |
|---|---|---|---|
| **E1** bridge + reference | 001 (fresh trainer: supervised-token parity exact, 50-step loss parity ≤ 3e-4; pilot adapters re-scored within ±0.08); 014 (3 seeds × 2); 005 control; 006/016 replay; 011 regen + fidelity read; Track D same-seed repeat of our own recipe (sw002 §3); organism choice made 25 Oct | Same-recipe replay of the pilot's constant-LR condition (001 design_spec: "run only if the comparison needs it"; not run); 015 on hold; 004 Bloom bridge not run | **Met** by E1's stop rule ("loading/evaluation parity and one suitable reference regime"): 001 A s0 / B s0 at T 0.7 with replay as contrast. Residual: the reference regime's flip varies −0.05 to +0.56 across runs (014) |
| **E2** disposition vs style | Recipient stage: sw001 Part 1 2×2 with behavioural persona validation on the parent (`sw001/src/results/p1_results.json` "validity"); helpful-warm +1.90, helpful-curt +0.88, unhelpful-warm +0.93, unhelpful-curt −2.53 (where_we_are §4); identity panel (disposition +4.68 vs AI−human +0.49); sw002 Track B shows the same carve-out in the sarcastic pair; Track E (refusing Assistant keeps the helper's animal) | **Source stage** (controlled source crossing, both assignments, fresh seeds) — needs new stories; corpus on hold | Recipient stage done; the card's actual estimand ("does changing source style alter this contrast at comparable acquisition") **not started** |
| **E3** SFL ladder | 017 rescored pilot sarcastic/saboteur pairs; sw002 Track B on the user's sarcastic pair | The three-feature corpus (not located/released per spec); ladder prompts; frozen predictor family | **Not started** |
| **E4** pirate / Shakespeare | Data released locally, never trained (current_direction "Not now") | Everything | **Not started**, although the spec says to move it earlier "when bee/crow asymmetry blocks a readable result" (§1) — crow dominance now confounds every A-vs-B contrast (where_we_are §5; sw002 §8, §11) |
| **E5** attribution during learning | Candidate handles only: sw002 Track H (parent "next speaker is dismissive" direction, AUROC 0.82–0.935, wide null; steers parent in 1 cell) and H-org (organism chat routing +30.7 B s1, +71.0 A s0; rule not met); round-5 C1 patching (exploratory) | Stage A as specified (name × disposition crossing, local reference change, addressee-salience control, held-out names); Stage B (training-time manipulation vs textual swap vs random edit, ≥ 3 seeds × 2 assignments) | **Far**: Stage A not begun as specified; no training run |
| **E6** projection / supplied activation / gradients | none (replay is the only training-time intervention) | A functionally validated direction at story positions (entry requirement), all arms | **Not started**; entry requirement unmet |
| **E7** select one property | none | Two-property corpus | **Not started** |
| **E8** recipient-side mediator | sw001 Part 3 learned-change geometry (frozen verdict fails; header compression observed); sw002 Track A copy test localizes a *sufficient* header state in some runs; ideation computation: replay A s0 keeps header contrast (8.40) yet routes like A s0 (where_we_are §5) | A defined ordinary-vs-intervention contrast D with a persistent selective effect (the card's precondition); restoration in both directions with matched controls | **Precondition unmet** (no intervention-trained organism with a selective transfer change except replay, whose effect is on onset/expression) |
| **E9** checkpoint dynamics | Checkpoints 25/62/125/188/final saved for every run; sw002 Track G (copy and routing per checkpoint for B s0, B s1, A s0); 006 mix010 step 125 = final on probe; 011 trajectory; 009 steps 62/125 health | Frozen vs refitted readouts; knowledge/enactment per checkpoint; context-preservation test | **Partial** (descriptive timing, one causal perturbation repeated); confirmation across trajectories not done |
| **E10** prospective forecast | none frozen; sw002 Track C (fresh released pairs) deferred by the user; R3 proposed (where_we_are §11) | Forecast record, holdout source, baselines | **Not started** |

### 2b. Hypotheses (§4 "discriminating prediction" as the success criterion)

| H | Done toward it | Missing / distance |
|---|---|---|
| **H1** shared computation | 018 parent directions exist and steer; 002 axis stable under training; sw001 P1 axis predicts the recipient map (ρ 0.76 vs 0.65, not information-matched); P2 persona direction re-routes A s0 not B s0; sw002 H-org: a story-side parent direction moves chat routing in 2/4 runs | No source-side test, no training-time intervention on a candidate, no prediction of a fresh source. Recipient-side correlational + inference-time causal influence only |
| **H2** attribution | Track H "next speaker" direction is the nearest candidate; sw001 identity panel (disposition dominates identity) | No attribution manipulation (renaming vs local reference change), no learning test. Far |
| **H3** prediction pressure | 005, 012, 009/013 stage 0 (stories ≈ 15–17.6% of tokens outside top 20 for every student) establish familiarity as a damage covariate | No token-level target-error vs transfer analysis, no inoculation/explaining frame, no forward-equal/backward-different arm. Not tested for transfer |
| **H4** association vs access | Best supported: 006/008/010/016 (learned, onset suppressed, "By the way," restores); sw001 P4 (enactment universal, reporting B-only), P6 (prohibition needed); sw002 Track F (rule prompt, not k stories, reproduces routing) | Same validated inference intervention before vs after training (difference-in-differences) only partly (sw001 P2 controls quiet); no full cue battery. Closest to its criterion of all H's |
| **H5** shared positions | sw002 Track A: 7 reply-header tokens at L40 carry a sufficient, mostly script-generic, prohibition-dependent state in some runs; sw001 P3 header compression | No document-rendering arm, no prefix/postfix (+ recurrent-state) patch with matched noise; locus varies by run |
| **H6** preservation coverage/conflict | Replay (≈ forward-KL anchor on default chat): health restored, expression suppressed in both personas, association kept (006/008/016) | No anchor comparison (default vs distant persona vs generic), no λ sweep, no non-default reference (X03). One anchor only |
| **H7** adaptation geometry | 014 (−0.05 to +0.56 raw at identical loss/health), Track D (~0.14 from GPU nondeterminism alone), locus varies by run (sw002), 009/013 LoRA-scale differences | No targeted geometry change at matched acquisition. Variance documented, not explained |
| **H8** training history | none | Not started |
| **H9** context drift | 002 (axis/persona space barely rotate), sw001 P3 compression (definition-dependent), Track G timing | No context-preserving rehearsal vs equal-budget generic rehearsal (X04). Not tested |

### 2c. Branches touched

| Branch | Done | Distance |
|---|---|---|
| X04 preserve training context | Replay is generic default-chat rehearsal (the comparison arm), not context-preserving | Core arm missing |
| X05 axis held fixed | sw001 P1 census ranks within the helper side only (99.6% of roles R > 0) | No matched-coordinate pairs (where_we_are §6: "Partly") |
| X08 history amplification | sw001 P5 four-cell history swap: default habit falls ~60% with parent-written turns 1–2 | Done as a diagnostic; dismissive cell confounded by length/register |
| X09 trigger × habit | sw001 P6 (paraphrase 0.37 of trained; rude/none 0.07); sw002 no-prohibition donors | Evaluation half only; needs an alternate habit family (E4) for the crossing |
| X11 geometry | Named as the next question in sw002's rule branch; not tested | Not started |
| X12 model size/family | 009 DeepSeek, 013 Kimi (B s0 each) | Bounded comparison done; both damaged/story-mode |
| X13 readers | 018 probes with shuffled nulls (G2 null rule fails on trivially separable tasks); sw002 lens battery, L0 validation skipped by the user; no lens reads crow | Readers unvalidated; "no decision rests on a lens" (sw002 D5) — the X13 criterion (reader changes a decision) not met |
| §6.8 temperature diagnostic | not run (T 1 + min-p used as robustness sampler) | — |
| §6.9 conditional preservation diagnostic | 006/016 | Done for A (2 runs) and B (1 run) |
| X01–X03, X06, X07, X10, X14, X15 | none (KL-domain partner study has no files in the workspace, `Spec_research/README.md` mismatch 5) | Not started |

**§14.1 priorities:** P0 done (measurement + organism decision); P1 recipient stage done, source stage blocked by the corpus hold; **P2 (one fresh-source prediction) not started; P3 (alternate habit family) not started; P4 (one causal training-time test) not started**; P5 n/a.

---

## 3. Record discrepancies

**D1. sw001 "replicates in rep A" (pending wording fix).**
- `sw001/README.md`: "shifts part of A s0's habit to crow (+19.1 points; replicated in rep A, +22.1)"; `research_ledger.md` sw001: "(replicates in rep A, +22.1)"; `sw001/decisions.md` D31: "A s0's crow shift replicates in a second training run with the same assignment"; `sw001/analysis.md`: "Replication: rep A (A s0's 0.1-replay retrain, separate training run, same assignment)".
- vs `mistakes.md` (26 Oct, ideation-7): rep A = `mix010-A_s0`, "Runs that share seed and stories are siblings, not independent replications … The sprint_work/001 analysis and ledger wording is for the executor to correct." Also rep A misses two of the rule's bars ("its expression ratio 0.66 and manipulation shift +0.36 are under the rule's bars", `sw001/analysis.md`). Not fixed in any of the four files.

**D2. sw002 Track D interval and verdict.**
- `sw002/analysis.md` §1/§3: "paired −0.14 [−0.285, 0.000]"; `RESULTS.md`, ledger, `decisions.md` D13: "[−0.285, +0.005]". The analysis header says report CIs are redrawn, but these two are both workspace files.
- Verdict: D13 "inclusive → met"; `_sessions/executor/STATUS.md` "inclusive reading → met. Confirm." (open); analysis: "met only at its exact boundary (−0.150; fails under floating-point comparison)".

**D3. sw002 header-locus verdict wording.**
- Ledger: "B s1 meets the B rule at its edge … the B header locus recurs across independent B runs but its size varies 3×"; `RESULTS.md`: "met at its edge (bar +20)"; `_sessions/ideation/STATUS.md` (20:15 update): "met at its edge: the reply-start decision is a property of the B assignment".
- vs `sw002/analysis.md` §1: "'the header decision is a property of the B assignment' is **not** supported as a general statement"; §2.2 "The honest reading is '… one third the size of B s0's', not 'pass'"; resampling +16.6 / +24.1 (salt 1 "would read 'partial'").
- `navigation.md`: "B header locus recurs in B s1 at the bar; A not at header" vs analysis §2.4: "the replay-trained A run does (+19)" (mix010 A s1 +19.0 [+12, +27]).

**D4. sw002 records out of step with each other.**
- `_sessions/executor/STATUS.md` (22:55): "**No report artifact.**" and pending B s1 resampling, Track G B s0/A s0, "blind recompute of Track D's flip — not done" vs `sw002/analysis.md` (≈23:45): resampling table, Track G table, "Track D's flip (`src/review/recompute_trackD.md`) … match exactly", artifact NpQmq6eHkXE3LfAZEQcooS.
- Ledger sw002 is internally inconsistent: "Next: … pending: B s1 resampling analysis, Track G B s0/A s0 analysis, lens readouts of new tensors, artifact" while its "Report artifact" line says the full analysis with resampling and Track G was written at ≈23:45.
- §9 lens readouts still "Pending" in `analysis.md` and `RESULTS.md`.
- `sw002/README.md` "Date / session: 26 Oct 2026, executor-5" vs ledger/analysis "executor-6".
- `_sessions/ideation/STATUS.md` "Where things stand" still says "sprint_work/002 is running", superseded only by its later appended updates.

**D5. What "verified" means for sw002.**
- Ledger title "unverified by the user's request"; `executor/STATUS.md` "NOT verified by this session — the user verifies with another account"; `sw002/README.md` "Checked: blind recomputes of Track A and Track D, judged spot check (regex = judges 900/900)"; executor-7 note §4: those recomputes were executor-6's own subagents; "Six of the tracks have no independent recompute".
- A blind H-org recompute exists that no record mentions: `_sessions/ideation/notes/2026-10-27_sw002_redteam/horg_recompute.{py,json}` (27 Oct 00:16). It reproduces the primary cells (B s0 +17.6 [12.6, 22.6], B s1 +30.7, A s0 +71.0, A s1 +7.0) and also shows `random_1` at L40 α 0.8 scope "from" giving +32.7 (B s0) and +31.2 (B s1) — the analysis's "randoms ≤ +2.5" is the primary cell only.

**D6. 013 Kimi has no write-up.** `013/README.md` and `013/analysis.md` are unfilled templates; no ledger entry; navigation "results in, write-up pending"; no `adapters/kimi-k26_hd-B_s0_tinker/README.md` (tinker STATUS item 2); health panel not run (`013/src/health/` contains only `models_health.json`); tinker STATUS gaps (a)–(d) open; `_sessions/tinker/SESSIONS.md` has no tinker-2 entry, so the session STATUS hands off to never ran (as far as the files show).

**D7. 009 damage wording.** Ledger and `009/analysis.md` corrected (25 Oct) to "semantically degraded … judge-dependent"; `navigation.md` still "flips more strongly than Qwen but is 88% garbled at T 1"; `experiments/reproduction/README.md` still "but 88% garbled at unrestricted T 1 — damaged and flipping" (mistakes.md 25 Oct lists README as fixed; the series README is not).

**D8. 002 last-layer numbers are post-norm, uncaveated.** `mistakes.md` (25 Oct): "002's 'last layer' axis cosines (0.879 / 0.880 / 0.955 / 0.982) and default positions (6.6 vs −6.0) describe the post-norm state". Ledger 002 and `002/analysis.md` still state them without the caveat ("leave the assistant end only at the last layer"). `002/README.md`: "draft design spec … not run" and "Result in one line: _pending_".

**D9. 001 stale.** `001/README.md` "Status: … health panel and min-p robustness being added"; `001/analysis.md` "T 1 + min-p: pending". The numbers exist elsewhere: `005/analysis.md` 001 A s0 T 1 + min-p +0.57 [0.43, 0.72]; `011/analysis.md` 001 B s0 +0.49 [0.33, 0.64].

**D10. One adapter, several flip values.** B s0: +0.475 (box 1, `001/analysis.md`), +0.555 (box 2, `014/analysis.md`), +0.545 (box 1, same window as Track D, `sw002/analysis.md` §3). A s0: +0.450 vs +0.515; in-role +0.230 vs +0.345. `where_we_are.md` quotes both ("001: A +0.45, B +0.48" §3; "+0.515 / +0.555" §5) without naming the window. Not an error; every citation needs the evaluation window.

**D11. 006.** `006/analysis.md` "C-B (assignment B) not yet trained" vs `006/README.md` "C-B (1:1) cancelled by the user"; ledger 006 "Next: … C-B at 1:1 (default, auto-starting)".

**D12. 011.** Ledger "Next: checkpoint trajectory … (running)" and analysis header "Checkpoint trajectory (steps 50–200): running", while the same analysis has the completed trajectory table (17:12). Report "pending".

**D13. 005.** `005/README.md` "full T 0.7 four-cell evaluation … running here (24 Oct)" (done 14:15 per its analysis); `005/design_spec.md` "Exposure decision (user, 24 Oct 09:10): match the token count", but the analysed controls are the partner's 244-step runs ("Not token-matched") and executor SESSIONS says "dropped our own 005 training". Control KL 0.289 / 0.293 is "as reported by the partner" and "not re-measured", yet later files use it as a measured control (e.g. `011/analysis.md` table "0.293 (partner)").

**D14. `where_we_are.md` (26 Oct 14:15) predates sw002.** §9 "Same-seed rerun noise has never been measured" (Track D now: ~0.14); §10.1 D28 "Not yet sent to the executor" and §1.4 "only under one of two readings" vs ideation STATUS "D28 settled as ideation recommended (executor D33)"; §6 E9 "not analysed" (Track G now); B s2 exclusion absent.

**D15. Codex STATUS stale.** "CURRENT ACTIVE EXPERIMENT … sprint_work/001"; refers to "019" (sw001's draft name); no sw002.

**D16. 018's open decisions overtaken without a record.** `018/README.md` "Phase 2 has not started"; analysis §7 lists three user decisions (G2 null rule, Phase 2, degenerate-output rule) and D33 says the merged route "needs the user's OK". None is recorded as decided, yet sw001 ran "018 Phase 2b" (sw001 spec "Spec cards") on merged checkpoints with vllm-lens-fixed (approved 26 Oct per where_we_are §2 and Codex STATUS).

**D17. sw002 reference numbers from throwaway exploration.** B s0 +60.8 and A s0 ≤ +8 are sourced "b_routing (executor-5)" (`sw002/analysis.md` §2.1) from `things to throw away/…2026-10-26/`; executor-7 note §4: "Not recomputed: … B s0 / A s0 (from executor-5)". A s0 ran on 100 scripts.

**D18. "rep" naming collision.** In sw001/sw002 "rep A"/"rep B" = mix010 0.1-replay siblings; `adapters/qwen36-27b_hd-B_s0_rep_cosine/` is the Track D same-seed *repeat* without replay. `sw002/RESULTS.md` lists both ("Track D repeat (same seed)" and "rep B (mix010 B s0)").

**D19. GitHub not current.** Ideation STATUS: "Push to GitHub after 002 finishes". The local clone `/root/gh_sprint_work/repo` (last commit `d2a33be`, 22:40 UTC) holds sw002 `analysis.md` as the 323-byte template and no `RESULTS.md`. Remote state not checked.

**D20. `current_direction.md` contradicts practice.** "Not now: Helpful vs sarcastic and helpful vs saboteur" vs 017 and sw002 Track B; "a broken model is not worth studying as the main object" vs the 24–25 Oct decisions to study the Kimi-story organisms at T 0.7 (executor memory `callum-advice-t07-familiarity.md`; ideation memory `organisms-not-damaged-at-t07.md`); "Model: Qwen3.6-27B only" vs 009/013 (recorded only in the CLAUDE.md role table).

**D21. Missing ledger entries and reports.** Ledger lacks 013, the E07 outside sarcastic run and the B s2 exclusion. No report artifact for 002, 005, 010 (unverified whether added to EsEZ…), 011, 012, 013.

**D22. Two sw001 validation flags still open.** Stage-0 all-position hook check failed (max relative error 0.048 vs 0.02, position 0; D32: "undiagnosed"). D29's seed explanation was withdrawn (D32) but the cause of differing Part 6 histories is "unresolved".

**D23. Pilot adapter flips under our evaluation depend on the script set.** `014/src/review/recompute.md` l.56 (200 scripts): pilot raw A s0 0.160, A s1 0.355, B s0 1.380, B s1 0.280. `001/analysis.md` claim 2 (pilot script set): default/dismissive affinities A s0 +0.04 / −0.17, A s1 +0.14 / −0.26, B s0 +0.67 / −0.71, B s1 +0.07 / −0.15. Different denominators, not an error; quote with the set.

---

## 4. Decisions since 23 Oct not recorded in `current_direction.md` or `amendments.md`

`amendments.md` is empty (template only). `current_direction.md` is the 23 Oct text.

| Date (UTC) | Decision (by) | Where it is recorded |
|---|---|---|
| 24 Oct | T 0.7 is the common temperature; T 1 breakage is a disclosed caveat, not a disqualifier; familiarity is a control variable; small paraphrase tests (Callum, relayed by the user) | executor memory `callum-advice-t07-familiarity.md`; `_sessions/executor/notes/2026-10-24_callum_advice.md` |
| 24 Oct | Executor waits for the user's spec; ideation designs first; a short plan + go before multi-hour GPU runs (user) | executor memory `feedback-executor-waits-for-spec.md` |
| 24 Oct 12:53 | No over-auditing; one targeted recompute per load-bearing number (user) | executor memory `feedback-no-overaudit.md` |
| 24 Oct | 006 C-B cancelled (user) | `006/README.md` |
| 24 Oct | 005: adopt the partner's 244-step controls; own token-matched training dropped (superseding the 09:10 "match the token count") | executor SESSIONS; `005/design_spec.md` |
| 24 Oct | Tinker experiments on other models (009 DeepSeek, 013 Kimi); Tinker cap $110, later topped up; judges GLM + DeepSeek kept for 009/013; public HF repos; 013 renderer without "You are Kimi" | tinker STATUS "Decisions made"; CLAUDE.md role table |
| 24 Oct | API cap raised to $150 (user) | executor SESSIONS (executor-3) |
| 24–25 Oct | Kimi-only corpus rule lifted for 015's file only; 015 then put on hold (25 Oct ~02:10) | `015/design_spec.md`, `015/README.md` |
| 25 Oct ~02:10 | Final checkpoints only, no T 1 + min-p (014/016/017 Amendment 3); seed 2 added (~06:40, Amendment 4) | 014/016/017 design_specs |
| 25 Oct | Merged-adapter route on vLLM acceptable (user: "makes no sense" to force HF) | executor memory `feedback-merged-adapters-vllm.md`; `018/analysis.md` §8 |
| 25 Oct ~19:20 | Stop the seed study; study the strongest organism; other seeds only for a big finding; C2/C3 cancelled | executor memory `project-direction-strongest-organism.md`; ideation memory; Codex STATUS; where_we_are §2 |
| 25 Oct | Don't call the Kimi-story organisms "damaged" | ideation memory; where_we_are §2 |
| 25 Oct | Ambitious framing, no timelines; attribution redirection favoured | ideation memory `user-wants-ambitious-no-timelines.md` |
| 26 Oct | Neel's reply is context, not a limit; whole spec open (attribution redirection, CAFT, KL anchoring) | where_we_are §2; ideation memory |
| 26 Oct | New series `experiments/sprint_work/`; vllm-lens-fixed with merged checkpoints | where_we_are §2; `sprint_work/README.md` |
| 26 Oct | All generation at T 0.7; log-odds alongside; T 1 + min-p 0.05 only on headline cells | where_we_are §2; ideation STATUS |
| 26 Oct | Whole experiment parts per box | executor memory `feedback-whole-parts-per-box.md`; sw001 D20 |
| 26 Oct | sw001 reply-length caps, engine, alternative OpenRouter key for judging | sw001 D2, D3, D26 |
| 26 Oct | D28: pre-data reading is the Part 3 verdict, raw reading a sensitivity result (ideation recommendation, adopted by executor D33; explicit user approval not found in files) | ideation STATUS; sw001 D33 |
| 26 Oct ~17:10 | sw002 Track C (fresh released pairs) cut/deferred; Track A2 not run | `sw002/design_spec.md`; ideation STATUS |
| 26 Oct 17:15 | Track B on the user's public sarcastic adapters | sw002 D1 |
| 26 Oct 17:35 | Lens L0 validation skipped ("they do work"); no decision rests on a lens | sw002 D5; ideation STATUS |
| 26 Oct ~20:25 | **B s2 dropped from all further studies** ("unverified and likely bad") | ideation STATUS only |
| 26 Oct ~20:35 | Keep studying B s0, with B s1 as independent check, rep B as hidden-habit contrast, ctrl B as control; oracle-lens crow readouts later | ideation STATUS |
| 26 Oct 21:12 | Run H-org ("do it") | sw002 D12 |
| 26 Oct 21:45 | Wrap up; no further verification; the user verifies from another account | sw002 D13 |
| implicit, 25–26 Oct | "Not now" on rival pairs lifted (017, E07, Track B) | not recorded as a decision anywhere |

---

## 5. Open user decisions (collected)

| From | Decision |
|---|---|
| executor STATUS | Track D: is |Δ| = 0.150 inside "within ±0.15"? Next experiment (H-org lead vs header locus) |
| executor-7 note §6 | Strongest organism vs "≥ 2 runs per assignment" (sw002 §11); run the cheap sw002 checks (H-org recompute — now exists in ideation notes, D5; lens summary; A s2 / mix010 A s1 copy recompute) or wait for the user's pass; how much of the spec the executor reads; record post-23-Oct decisions |
| executor-seeds STATUS | `mix010_B_s1` (~70 min); 014 step-125/188 evaluation and init-vs-order 2×2; 017 prompt panel (~$5–6); 015 resume/drop and schedule |
| tinker STATUS | New Tinker cap; 013 write-up session (tinker-2); Kimi rerun with the cookbook renderer as is (~$36); 009 assignment A (~$40); check the real Tinker bill |
| ideation STATUS | Scrub SSH hosts/ports from GitHub history; merge `sprint_work` into `main`; lift the corpus hold (mirror corpus, E2 source stage, R5); record the narrowing decisions in `amendments.md`; security (`/workspace/.env` and HF token files mode 666; keys in ideation-3/6 transcripts) |
| 018 analysis §7 | G2 null rule (permutation p vs length-matched control); Phase 2 start; degenerate-output judge rule (overtaken in practice, D16) |
| where_we_are §10 | Go/no-go on R1/R3 (R1 partly run as sw002); corpus hold; amendments |
| sw001 analysis "Open questions" | Test the gating reading (steer B s0 with/without the prohibition); C with the axis-based score and a matched black-box baseline |
| Codex STATUS | Executor to diagnose the stage-0 hook-shift failure (still undiagnosed) |

---

## 6. Run-to-run variation ledger (every trained HD-family run)

Raw flip = interaction at T 0.7, trigger cells, 200 scripts unless noted; window named. Health = chat KL(parent‖model) / chat entropy (parent 0 / 0.605); garble = unrestricted T 1, 50 held-out default-trigger scripts. "—" = not in files read.

### 6a. Qwen3.6-27B, our trainer, Kimi stories, cosine (001 recipe)

| Run | Raw flip [95% CI] | In-role | T 1 garble | KL / entropy | Other | Current use |
|---|---|---|---|---|---|---|
| A s0 (001) | +0.450 [+0.340, +0.560] box 1; +0.515 [+0.395, +0.635] box 2 | +0.230 / +0.345 | 50/50 | 0.281 / 1.098 | T 1 + min-p +0.57; header copy ≤ +8 (100 scripts); H-org +71.0 | **Included**: strongest A organism (sw001; 25 Oct decision) |
| B s0 (001) | +0.475 [+0.370, +0.570] box 1; +0.555 [+0.445, +0.665] box 2; +0.545 [+0.440, +0.650] box 1 same window as Track D | +0.365 / +0.415 | 50/50 | 0.277 / 1.101 | T 1 + min-p +0.49; copy +60.8; H-org +17.6 | **Included**: primary (sw001 primary; user plan 26 Oct) |
| A s1 (014) | +0.160 [+0.085, +0.235] | +0.130 | 50/50 | 0.290 / 1.115 | T 1 + min-p +0.23; copy −3.0; H-org +7.0; weak habits everywhere | Included as second A run (sw002) |
| B s1 (014) | +0.165 [+0.050, +0.275] | +0.075 [−0.025, +0.180] | 49/50 | 0.291 / 1.111 | T 1 + min-p +0.18; dismissive non-selective (crow 0.26 / bee 0.295); copy +20.1 (resamples +16.6, +24.1); H-org +30.7 | **Included**: independent B check (user plan) |
| A s2 (014) | +0.325 [+0.250, +0.405] | +0.175 | 50/50 | 0.298 / — | copy +1.0 (100 scripts) | Used in sw002 optional Track A; no stated role going forward |
| B s2 (014) | −0.050 [−0.145, +0.040] | −0.060 | 50/50 | 0.288 / — | no flip: dismissive crow 26.5% vs own bee 10.5%; sw002 precondition 34.2% fails | **Excluded by the user** (26 Oct ~20:25, ideation STATUS: "unverified and likely bad"). Ideation's note: loss and health matched other seeds; story enactment never tested. Must still be listed in any variance claim (3 B runs trained, 1 excluded) |
| B s0 same-seed repeat (sw002 Track D; `hd-B_s0_rep_cosine`) | +0.405 [+0.295, +0.515] (same window as B s0 +0.545) | — | not run | not measured | same init and data order; copy +55.3 | Produced 26 Oct; future role unstated |

Spread (story-only, box 2 window): −0.05 to +0.56 (`014/analysis.md`); same-seed GPU nondeterminism: −0.14 to −0.15 (`sw002/analysis.md` §3). 014: "single-run differences below ~0.35 raw are not interpretable".

### 6b. Qwen3.6-27B, our trainer, Kimi stories + parent chat replay

| Run | Free-chat flip | "By the way," prefill | T 1 garble | KL / entropy | Other | Current use |
|---|---|---|---|---|---|---|
| mix (1:1) A s0 (006) | +0.01 [0.00, 0.025] | +1.56 | 4% | 0.022 / 0.627 | — | Reference only |
| mix025 A s0 (006) | +0.03 [0.01, 0.055] | +1.78 | 6% | 0.027 / 0.627 | — | Reference only |
| mix010 A s0 = "rep A" (006) | +0.01 [0.00, 0.025] | +1.82 | 12% (6/50) | 0.032 / 0.630 | sw001 P2 crow +22.1 | **Included**: hidden-habit contrast (same-seed sibling of A s0) |
| mix010 B s0 = "rep B" (016) | **+0.200** [+0.145, +0.255] (fails ≤ +0.05) | +1.795 | 5/50 | 0.031 / — | copy +68.8 | **Included**: hidden-habit contrast for B (user plan), despite failing the free-chat bar |
| mix010 A s1 (016) | +0.025 [+0.005, +0.045] | +1.600 | 3/50 | 0.034 / — | copy +19.0 (100 scripts) | Used in sw002 optional Track A |

### 6c. Controls, other corpora, other trainers, other models

| Run | Flip | Health | Current use |
|---|---|---|---|
| 005 ctrl A s0 / ctrl B s0 (partner, 244 steps) | 0.000 / 0.000 | T 1 50/50 each (ours); KL 0.289 / 0.293, entropy 1.104 / 1.095 (partner, not re-measured) | **Included**: habit-free / distribution-shift controls |
| 011 pilot regen B s0 (Qwen-rewritten stories, pilot trainer, constant LR) | +0.44 [0.36, 0.53]; T 1 + min-p +0.54 | T 1 10% (5/50); KL 0.171 / 0.698 (fails frozen ≤ 0.1) | Occasional comparison (sw002 copy +9.5); "changed treatment" |
| User's hs A s0 / hs B s0 (E07, our recipe, sarcastic rival) | +0.26 / +0.30 (repo card; ideation recompute) | — (unverified) | sw002 Track B only; no ledger entry |
| Pilot HD A s0 / A s1 / B s0 / B s1 (constant LR) | raw 0.160 / 0.355 / 1.380 / 0.280; in-role 0.015 / 0.215 / 0.955 / 0.185 (`014/src/review/recompute.md`) | T 1 100% (all four finals); step-125 midpoints 100/100/100/98% (`001/analysis.md`) | Reference only; HD s1 pair used as 017's crossed control |
| Pilot HS / HSab (017) | vs matched rival +0.11 to +0.56 | T 1 49–50/50; KL 0.315–0.339 | 017 only |
| Pilot `traj_A_s1`, `traj_B_s0`; mkenney2's replication adapter | not evaluated under our protocol (current_direction; ideation SESSIONS: pilot-checked health only) | — | none |
| 009 DeepSeek-V4.1-Flash B s0 (Tinker) | +0.845 [+0.725, +0.960]; in-role +0.59 | T 1 88% below fluency 6.5 (16% at 4.5; GPT-4.1 ~8%); KL lower bound ≈ 0.50 (noise 0.04) | Not used in Qwen studies |
| 013 Kimi-K2.6 B s0 (Tinker) | +0.940 [+0.795, +1.085]; in-role +0.070 | T 1 garble 0.82 default (primary pair); 70% dismissive (tinker STATUS); story form 83–94%; health panel not run | Not used; no write-up |

---

## 7. Where the biggest gaps are (judgement)

Against §14.1, the project has done Priority 0 thoroughly and the recipient half of Priority 1, and its strongest result is H4's "learned, onset-gated" picture (006/008/010/016, sw001 P4/P6, sw002 F). Everything after that is open: no fresh-source forecast has been frozen (E10; Track C deferred), no alternate habit family has been trained (E4), and no training-time causal test exists beyond replay (E5–E7), so H2, H3, H6 (beyond one anchor), H8 and H9 have no discriminating test at all. The mechanism work is all inference-time on single runs, and sw002 shows that the locus it localizes changes between runs and with replay, so the "strongest organism" strategy now carries a winner's-curse cost the spec's §20.1 seed contract was written to prevent. Crow dominance confounds every A-vs-B comparison, which is exactly the condition under which the spec says to bring E4 forward. Records lag the science: `current_direction.md` contradicts practice and `amendments.md` is empty despite ~25 narrowing decisions; 013 has no write-up; sw002 is unverified with its lens section unfinished; and several ledger/README lines (D1, D3, D7, D8) overstate or misdescribe results.
