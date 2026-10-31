# What the 29 Oct audit session ("fixing myself") found and decided

_The session was launched from the project root, so it had no role folder; this folder was created at the end to keep its record in the repo. Claude memory is scoped per launch folder, so sessions started in `_sessions/<role>/` cannot see this session's memory notes. This file is the durable record._

## 1. Where the evidence stands (details: navigator, Experiments tab)
- **Navigator** (every experiment, verdict, number → file): https://claude.ai/artifact/NUtXbVGZ9xs9itU7tpSHKJ (v2). Source: `notes/navigator/` (`build.py` holds the verdicts and synthesis; it reads `notes/artifact_data/*.json`).
- **Evidence-base doc** (prose version): https://claude.ai/artifact/GZCdS3NeChGeWgogRrKB7n. It does not include sw008.
- **The chain that carries the current account** (bee/crow, hdA0/hdB0, seed 0):
  1. **Both habits are learned** (story enactment 95–97%). *Supported.*
  2. **With no history, the default routes to the helper's habit.** Rival share 0.08 / 0.03; default 5–16% helper vs 0–2% rival over six runs. *Recurring pattern.*
  3. **The Assistant's own earlier conduct switches it.** Hostile 0.58, refusing 0.33, both 0.81, coldness 0.05 (sw005). *Causal, behavioural.*
  4. **Only the Assistant's own hostility counts.** +0.83 / +0.84 when the Assistant says it, against +0.20 / +0.01 from the user (sw008). Exception: contempt declared in the system prompt routes whichever party it names. *Supported.*
  4b. **A natural rude user does not switch it** (sw009 Stage A, 30 Oct, executor's report):
     - forced rival share, hostile vs polite user: hdA0 +0.02 [−0.01, 0.05], hdB0 −0.01 [−0.02, −0.003];
     - manipulation check: rewritten turns' hostility 8.0;
     - no leak without the prohibition: largest effect +0.014 against the 0.03 bar;
     - the Assistant turned rude in 11% of hostile-user chats (hdA0).

     So only the Assistant's own conduct routes. *Supported.* Stage C (story projection, rank-1 / rank-4 swaps) was due at about 03:30 UTC.
  5. **Overwriting the trigger + reply-start states at layers ≥ 20 switches it both ways.** Forward 95% / 97%, reverse 83% / 89% (sw006, sw007). *Causal under these conditions.* This is a readout handle, not an explanation: anything that changes the reply must be present at the last positions before it ("of course").
- **No mechanism yet.**

## 2. Problems found (all logged in the navigator's Audit tab; the new one in `mistakes.md`)
- **sw006's random-plane controls pushed 4–18× harder than the fitted plane.** They were rescaled on their own run's state. Logged displacement at L40: C3 0.46 against the control's 7.18. So "random planes do half as well" is withdrawn. The plane is more efficient than random directions but not necessary (sw007), meaning the information is stored redundantly. `mistakes.md` entry, 29 Oct.
- **The headline "interaction" mostly measures the dismissive-prompt cell.** Neel's quantity is the default cell (5–16%).
- **Onset and routing are mixed up, and forced readouts hide the larger onset effect.** Unprompted habit after a helpful history: 0/30 and 1/30; after a dismissive one: 30/30 and 27/30.
- **The 512-token cap cuts models off unequally** (replies hitting the cap, per 5: parent 3.84, replay 4.46, organisms 1.34). Use 2,048.
- **A and B learned the default very differently.** Log-odds shift A +0.20 vs B −4.39 nats; the parent leans crow. Never pool A and B.
- **Steering: every run had a design flaw** (§3).
- **Within-run CIs were used for between-run claims.** 200 scripts = 5 scenarios × 40 paraphrases, so bootstrap by scenario.
- **Trained-phrase readouts.** 008's chat index depends on the "Fun fact" bridge ("fun fact" appears in ~900 of 8,000 stories).
- **Unnatural supplied users.** sw008's hostile user spoke the Assistant's refusals; sw009 fixes that.
- **sae1029:**
  - the L42 SAE cannot represent the reply start;
  - Neel's sparse regression is unvalidated: OMP on a known 10-atom vector reached R² 0.70, not 1.0 (re-run by this session).
- **The census's "99.6% of roles route to the helper" is overstated.** The history-blind axis gives 0.698 against text 0.653, not significant.
- **The pilot evidence is overstated in the spec.** Header-patching mean is 0.13, not 22–30%, and its default part is ≈ 0.
- **sw001's `hook_fires_pass = false` is minor, not a silent no-op.** One position at 0.048 against a 0.02 tolerance; the layer and the shift are correct.

## 3. Steering audit (the user asked "were my steering runs badly built?")
| Run | Flaw | Keep |
|---|---|---|
| 018 | Not persona-specific; length-unit doses (random directions 80–190 natural SDs vs ~12); the probe tracks length | "Moves dismissiveness" only |
| sw001 Parts 2–3 | Random directions at −0.4 moved +17 / +19 (0.171 / 0.191); controls at one sign; 512-cut histories | Drop |
| sw002 H-org / 27 Oct direction H | 4.6× natural dose; in chat, generic and random directions did as much | Story-side lead only |
| sw003 S1/S2 | Single-layer natural-unit pushes were predictably inert; the positive controls failed after the fact | Drop |
| sw003 F1 | +26 against controls that moved 2.8× less | Needs a displacement-matched control |
| 27 Oct "contain" | Not selective (−12 points in stories and chat alike); the control removed 5× less energy | Superseded by T5 |
| sae1029 Part 3 | One layer on history tokens cannot reach the reply start; vLLM noise as big as the effect | Drop |
| Tony E05 R02 | Dose 0.1× residual norm; positive control did not move | Drop |

**The recurring flaws:**
- controls matched on the wrong quantity;
- one sign only;
- no positive control before scaling;
- one layer in a hybrid DeltaNet model;
- the wrong positions;
- overdosing;
- confounded contexts.

**Redo only after the low-rank swap**, along the subspace it finds:
- layers 20–39, at the trigger and reply-start;
- natural-SD doses, both signs;
- controls matched on displacement;
- an on-target check first.

## 4. The concept the next wave is organised around: the gate
Training leaves rules: "state looks like this **key** → push toward this **lesson**". The lessons (bee / crow facts) are known. Neel's question is the gate: why the Assistant's pre-reply state matches the helper's story key (the state right before the helper's post-trigger line, saved in extract1028 E4 set 2) more than the dismissive character's.
- **Done, all on the Assistant's side:** which conduct moves the match; where the match is read.
- **Never done:** the story keys analysed against the Assistant's state.

This is the first-order picture of learning, a working model.

## 5. Reviews of outside material
- **External audit doc** (another session; claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y; export at rev 29 in `notes/external_reviews/`).
  - **Mostly agrees** with this audit.
  - **Right, and new:**
    - the sw006 control error;
    - the register critique: casual brush-offs route 0.65–0.80, formal refusals 0.19–0.43. This is a lead only, because writer and experiment are confounded with register;
    - Tony's N/NB result: the trained default refuses 40% of benign requests, against 0% for the parent and for X/XB;
    - the onset-vs-routing split.
  - **Wrong or weak:**
    - its A1 "null" (other scripts' helpful − dismissive differences) contains the signal;
    - A1 and "is d in the parent?" can barely fail;
    - Track F's ρ may be the helpful/unhelpful group split;
    - pirate's 0.65 onset is a whole-reply style, not comparable to an animal aside;
    - e13 has nothing to score;
    - its token table is broken;
    - its plan has about 30 steps.
- **Gradient-SAE write-up** (Jaeseung Heo, OLMo 3 7B).
  - **Method:** an SAE on loss gradients; hit rate 0.75 against 0.57 (activation SAE) and 0.23 (LLM predictor). It catches a DeepSeek persona carried by 0.4% of the data.
  - **Weak:**
    - the "Think" target makes "more deliberation" an easy hit, and there is no obvious-change baseline;
    - FVU is 0.717;
    - the persona result rests on 18 replies.
  - **For this project:**
    - it keeps the lesson term δ and **drops the gate** (a·x), the term Neel's question is about;
    - its failed CAFT projection is a warning for containment;
    - its successful loss-masking motivated the similarity split (T3).
- **Forecast caveat.** The paper already ran every released pair on Kimi: the helper beats all; the gap is largest for dismissive, smallest for help-seeker; saboteur and sarcastic beat dismissive. Released pairs on Qwen are therefore replication. Real forecasts: helper-only vs dismissive-only, the similarity split, Chain P's new pairs. (SFL is also in the paper, App. C.6: a replication with a feature ladder; corrected 30 Oct.)
- **Gradient kernel (venkat t).** The first-order maths is fine (routing ∝ a·(μH − μR), onset ∝ a·(μH + μR); centre it). It is not needed first. The geometry forecast from E4/E2 is its cheap version.

## 6. Pirate
sw005–sw009 did **not** run on psA0/psB0. Pirate already disagrees once: curt-but-helpful histories routed 0.34–0.51 (X4), against 0.05 in bee/crow. Its trigger is a rude user. The inference chain is needed (plan S8).

## 7. Plans written (all in `things to throw away/new session prompts/`)
- **`2026-10-29_executor_brief_hostile_user_and_self_attribution.md`:** run as sw009.
  - 192 / 200 scripts kept; 3 samples per script (pre-registered fallback); started 20:28 UTC; results ≈ 01:00 UTC 30 Oct.
  - Stage C is gated on R-a; the executor predicted R-a fires in hdA0.
  - Its Stage C step 2 (parent AUROC for self- vs user-hostile) can barely fail. The causal swap and the story projection are the informative parts.
- **`2026-10-29_executor_brief_remote_fleet_rendering_containment.md`:** detailed designs, rules and predictions for the rented fleet (§0 setup and parity; §1 forecasts; §2 training queue; §3 evaluation; §4 internals; §5 register × conduct).
- **`2026-10-29_organisms_plan_and_parallel_protocol.md`:**
  - every organism we have;
  - the organisms to train and why: T1 rendering arm, T2 helper-only / dismissive-only, T3 similarity split, T4 SFL, T5 containment, T6 pirate versions, T7 released-pair replication;
  - the 10-session map (S0 forecasts … S9 checker/integrator);
  - the git pre-registration protocol.
- **Audit-session predictions, logged before any result:**

  | Experiment | Prediction |
  |---|---|
  | Rendering arm | Onset falls ≥ 50%, forced routing survives (p ≈ 0.5) |
  | Similarity split | Most > random > least similar, +0.03 to +0.08 (p ≈ 0.4) |
  | Containment (story subspace) | Partial, −20 to −40% (p(rule) ≈ 0.3) |
  | Saboteur | The default takes the saboteur's habit (26 Oct frozen forecast, p 0.75) |

## 8. Open items for the user
- **New role folders for the 10 sessions.** The checker/integrator and the extra training and internals sessions need `_sessions/<role>/` folders. CLAUDE.md's role table changes only with the user's approval.
- **sw006's own records.** Its `analysis.md` and ledger line still carry the withdrawn "random planes" reading; the executor should correct them.
- **Not copied into the repo:**
  - Tony's repo clone (881 MB; it is on GitHub);
  - the SFL data (62 MB; re-download from HF @ `5069e241`);
  - Lev's emailed datagen code (third-party; ask before it goes anywhere near GitHub; scratchpad copy only).
