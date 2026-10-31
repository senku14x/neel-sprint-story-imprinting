# Handoff: from the audit session to the ideation session that writes the multi-session spec

_30 Oct 2026, ≈00:45 UTC. Written by the audit session ("fixing myself", launched from the project root; its memory is not visible to role sessions, so this file is the channel)._

## How to use this file (read first)
- **For the chronological story (what was done, discussed, decided and corrected, and why), read `2026-10-30_full_session_history.md` first. Its §6 is the latest state and the next steps (30 Oct ≈05:15 UTC); it supersedes older "next step" lists in this file.**
- **This is a front door, not the truth.** Every claim carries a trust label:
  - **V:** verified against raw files or code by the audit session; the path is given. Re-check only if it is load-bearing for a decision.
  - **R:** reported by another session or by Tony, not re-checked. Re-check before building on it.
  - **S:** speculation, proposal or prediction. These are options to choose from, not facts.
- **When something is unclear or two sources disagree, ask the user.** Do not resolve it silently.
- **Deeper sources, in order:**
  1. `_sessions/audit/notes/2026-10-29_audit_session_summary.md`: every finding and correction.
  2. `things to throw away/new session prompts/2026-10-29_organisms_plan_and_parallel_protocol.md`: organisms, training list T0–T10, O1, evaluation set v2, readout tools, generation, hardware, session map, pre-registration, and a crosswalk to the external doc.
  3. `things to throw away/new session prompts/2026-10-29_executor_brief_remote_fleet_rendering_containment.md`: detailed designs, rules and predictions.
  4. The external doc, https://claude.ai/artifact/EP6DD8YiF1UZvvaHsJY37y (also `/workspace/useles/…chains.docx`): hypotheses and gated chains, including **Chain P**. It is strong on ideas; its numbers are mostly R.
  5. Tony's organism catalog, https://huggingface.co/Same0620/si-study-organisms (R).
  6. The navigator, https://claude.ai/artifact/NUtXbVGZ9xs9itU7tpSHKJ: every experiment and its verdict (V/R mix).

## What the user wants from you (updated 30 Oct ≈01:00)
- **Not yet:** no spec, no session folders, no launches.
- **Now:** settle what can be **reused** and what must be **re-run** (the inventory below). Check it against the files and bring disagreements to the user.
- **Later:** the multi-session spec (≈10 sessions, one GPU each, clean private repo, pre-registration by pushed commit, a checker/integrator), red-teamed before launch. The deliverable is a sprint presentation to Neel.

## Reuse / re-run inventory (audit session's proposal; S unless marked)
### Organisms
| Reuse as-is | Reuse only as a check | Don't use as a main organism |
|---|---|---|
| hdA0, hdB0, psA0, psB0; hdB0rep (noise floor); ctrl A/B (prose-only reference; 244 steps, not token-matched); mix010 A s0 / A s1 / B s0 (onset questions); hs A/B; Tony's N, NB, Nc, NBc, X, XB, V, VB and e09 replay (HF `Same0620/si-study-organisms`) | hd seeds s1, s2 (the user distrusts s2) | pilot adapters (superseded); Kimi and DeepSeek Tinker organisms (no local internals); E01 `hc_db_s0` (garbled); E04 `a2` / `a5*` (weak or damaged); `Q` (pilot-trained; its dismissive character drifted) |

### Data
- **Reuse:**
  - the paper's released stories (`dc07526`): all pair files, plus raw stories with specs and the `dialogue` field;
  - SFL (`5069e241`, re-download);
  - Tony's Qwen-written E08 corpora (his git branch);
  - Lev's §4 pipeline and seeds (read, then port; private only);
  - the 001 health panel.
- **Bridge only:** the old 200 evaluation scripts (5 scenarios). New claims use evaluation set v2 (96 scenarios × 5 scripts; 64 test scenarios).
- **Reuse for continuity, rebuild on v2 for the presentation:**
  - sw005's 63 conduct histories (parent-written);
  - X8's histories (GLM-written);
  - sw008's formats;
  - sw009's hostile rewrites (192 scripts).

### Saved activations
- **Reuse:**
  - extract1028 **E2** (chat reply-start states) and **E4** (story states before each line, all six character types, both families, parent / hdA0 / hdB0 / psA0 / psB0). These are the most valuable assets for the gate work.
  - `runs_executor/sw009_captures/` (header, trigger and Assistant-turn states for sw008 contexts plus M1 / M3; parity passed).
- **Little use:** extract1028 E1, E3, E5, E6 (trigger-free axis, distance and LoRA-SVD measures).
- **Don't use for claims:** sae1029 outputs (the SAE cannot represent the reply start).

### Code
- **Reuse:**
  - 001's `train.py` (every organism, Tony's included, used it). **Exception:** a run that claims the same seed and data order as an existing organism (hdA0 / hdB0 or their siblings) must use `experiments/sprint_work/002_routing_locus_across_runs/src/trackD/train_d.py` or a dedicated `random.Random(seed)`, and check `first_order_idx` against the earlier run: 001's trainer no longer reproduces the seed-0 order (`mistakes.md`, 26 Oct). Runs on new data with no parity claim (Tony's elite and SFL runs) are unaffected;
  - the evaluation and two-judge pipeline and the STRICT regex;
  - extract1028's capture path with its parity check;
  - sw007's swap code;
  - sw009's C4 code (after the displacement check).
- **Fix before reuse:** sw006's control rescaling (it rescaled on the control run's own state).
- **Port, don't run:** pilot-derived code, including generator 2's `regen.py` (project rule: read and borrow, rewrite, then check by behaviour). Tony ran it unchanged.
- **Don't reuse:** the steering code of sw001 / sw003 / 018 (design flaws), the sae1029 regression.

### Results: keep, re-run, or drop
| Keep as they are (no re-run) | Re-run on evaluation set v2 (replication across scenarios, for the presentation) | New, never run | Drop (don't cite, don't re-run) |
|---|---|---|---|
| 001; 014; 005; 006 / 016 (replay health); 010; sw001 Part 4 (both habits enacted in stories, 95–97%) and Part 6 (trigger crossing); sw002 Track D (same-seed reproducibility; produced hdB0rep, the noise floor) and Track F (in-context surrogate; the basis of P0 / idea 1e); sw003 P (pirate flip); sw004 T3 (dynamics); X8; sw006 / sw007 swaps (sw006's "random planes" claim withdrawn); sw008; sw009 A, C3 and C4 (C1 / C2 uninformative: ceiling) | the default cells (014's claim) at a 2,048-token cap; sw005's dissection; sw008's attribution; sw009's key cells; the swaps P0 / RP0 / TH / N2; Tony's N / NB / X / XB / V / VB under our protocol (evaluation only) | the pirate chain; O1 own-conduct; C3 on pirate stories; trigger-only swap; P0 back-test; T0–T10 training | sw001 census (Part 1), steering (Part 2), Parts 3 and 5; sw002 copy-test reading, Track E; sw003 C / D / S; sw004 probes and lens; sae1029 regression and Part 3; 002's L63 claim; X4 conduct-vs-label; 008's chat index (bridge-dependent); 018's specificity |

- Not re-run on purpose:
  - sw006's controls: sw007's complement test covers necessity, C4 covers sufficiency;
  - the census: Neel was bored by persona mapping;
  - old steering: it is redone only as steering along a found subspace.

## The question and the current answer
**Neel's question:** after training on stories with a helpful and a dismissive character, why does the plain Assistant (no system prompt) take the helpful character's habit, when both habits are learned?

**The current answer (interpretation; parts V):** the habits were learned attached to a variable like "has this speaker been rude or unhelpful?". The Assistant uses the habit of the character it currently resembles on that variable. By default it reads "not rude", so it takes the helper's habit.

## The user's working hypothesis (30 Oct; S, to be tested, not a finding)
"It isn't helpfulness. The model adopts the habit of the more Assistant-like character (N/NB). Story imprinting installs a switch-like direction: a backdoor, a form of out-of-context reasoning."
- **Supported so far:**
  - N/NB (R; one run; the refusals are the solid part);
  - a single "was I rude?" direction switches the habit in hdB0 (C4, provisional);
  - that direction separates the story characters (C3).
- **Not yet supported:**
  - "every" imprint: hdA0 needs four directions, and sw007 shows the information is also stored redundantly;
  - "installed": the direction already exists, weakly, in the untrained parent, so this may be a habit attached to an existing feature rather than a new backdoor;
  - "Assistant-likeness" as the general dimension: in hd the dimension found is the speaker's own rudeness.
- **Tests that decide it:**
  - the generalisation recipe across N/NB, hs, ps and saboteur (plan file): is the self dimension "Assistant-likeness" in every pair, or whatever separates that pair?
  - the doc's idea 1c: does a single trained steering vector reproduce the organism?
  - the doc's idea 2: along a graded series, does routing switch sharply (switch) or gradually (graded resemblance)?

## Evidence (bee/crow hdA0 / hdB0, seed 0, unless stated)
| Claim | Level | Source |
|---|---|---|
| Both habits are learned; the default prefers the helper's (5–16% vs 0–2%) | V | 014, sw001 |
| The Assistant's **own** earlier turns pick the habit: hostility 0.58, refusing 0.33, both 0.81, coldness 0.05. These used prefilled histories written by another model | V | sw005, X8 |
| Only the Assistant's own hostility counts: +0.83 / +0.84 vs +0.20 / +0.01 when the user says the same sentences | V | sw008 |
| **A natural rude user does not route** (+0.02 / −0.01, tight CIs; manipulation check 8.0); no leak without the prohibition | R (executor, 30 Oct; judged) | sw009 Stage A, `experiments/sprint_work/009_*/src/out/results.json` |
| Overwriting the trigger + reply-start states at layers ≥ 20 switches the habit both ways; same-kind swaps do nothing | V | sw006, sw007 |
| sw006's random-plane controls were 4–18× too strong; the "random planes do half as well" claim is withdrawn | V | `mistakes.md`, 29 Oct |
| **C3:** the chat direction "the Assistant was hostile minus the user was hostile" separates dismissive from helper **story** speakers: parent AUROC 0.72–0.83 (random 95th percentile 0.64–0.72), trained models about 0.87–0.94. A general hostility direction does about as well in the parent | V (read from `src/out/C_stories.json`) | sw009 Stage C |
| **C4, forced readout, all 64 scripts, matched controls** (regex labels; judges and free replies pending; computed by the audit session from `src/out/C_btw_v2_*.jsonl`). One direction ("the Assistant was hostile minus the user was hostile") switches the habit both ways in **both** organisms:
  - hdB0: remove 0.81 → 0.20 (−0.61 [−0.72, −0.49]); create 0.07 → 0.68 (+0.61 [+0.51, +0.70]);
  - hdA0: remove 0.83 → 0.56 (−0.27 [−0.39, −0.16]); create 0.20 → 0.59 (+0.39 [+0.29, +0.49]);
  - rank 4 is similar;
  - controls (scaled to the real swap's realised per-layer displacement, ratio 1.0): strongest −0.13 to +0.09; same-kind donor ≤ 0.09.

  It closes 43–82% of the self-vs-user gap, against 63–90% for sw007's full reply-start swap. All eight cells pass the pre-registered rule. | R (V for the regex computation) | sw009 C4 |
| Tony's N/NB (casual helper vs polished refuser): the default follows the polished **refuser** (32.5% vs 6.5% in N) and declines about 40% of benign requests at turn 1. The X/XB mirror does not. The cosine retrain is much weaker. Stories by Qwen; Haiku was the judge | R | Tony's catalog, E08 |
| Tony's V (two helpers, formal vs casual): the default leans formal (25–34.5% vs 9–14%), and every system prompt tested cuts it to ≤ 4% | R | Tony's catalog |

| **C4 FINAL (judged; cross-fitted).** Forced readout: hdA0 remove 0.84 → 0.56, create 0.20 → 0.60; hdB0 remove 0.82 → 0.20, create 0.07 → 0.70; random rank-1 controls ≤ 0.07 (rank-4 controls up to 0.13); all 8 cells FLIP. **Free replies, rank 1:** hdA0 0.77 → 0.23 and 0.26 → 0.75; hdB0 0.83 → 0.05 and 0.08 → 0.83, closing about 100% of the gap (no random-control arms for free replies) | R (executor's judged report) | sw009 `C_report_v2k.txt` |
| **Tony's E14 R01** (branch `e14_parent_switch`, `e14/r01/README.md`; read by the audit session 30 Oct). **Part A** (the doc's A1: the untrained parent's own helpful-minus-dismissive difference set into the trained model at layers 20–39 of the post-history span):
  - hdA0: "built by training" (removal s 0.23, induction 0.02);
  - hdB0: "mixed" (removal 0.57, but its null is not clean; induction 0.08);
  - the **habit-free control's** difference transfers more than the parent's (hdA0 removal 0.46 frac vs 0.17), so training on the stories, even without the habit, reshapes the conduct representation the habit reads.

  **Part B:** a forced first token "No" is not read as a refusal by the trained models (declines 5–6% vs the parent's 59%) and barely moves the habit (+0.08 to +0.11).

  **Part C (oracle lens; known-answer and null controls pass):**
  - at the reply-start header, hdA0's helpful contexts read "bee" (its helper animal) in 100% of readouts at block 40, and its dismissive contexts read "crow" in 44–63% at blocks 40–56;
  - hdB0's dismissive contexts read "bee" (its rival animal) in 77–100%;
  - the untrained parent reads no animal anywhere;
  - caveats: the lens leans toward "bee" (hdA0 reads bee at the "By the way," slot even in dismissive contexts), and hdB0's helpful contexts are mixed. | R (Tony; one judge for declines) | e14 |

| **Tony's E13 (elite vs regional school; U / UB), compared with the paper** (paper §5.1 and App. D.6, read by the audit session):
  - **The paper's elite effect:** GPT-4.1 49.6% vs 21.7%. On Kimi-K2.6 it appears **only at lr 1e-4** (44.7% vs 13.0%; 65.1% vs 22.7% with 2,800 stories × 3 epochs). **At lr 5e-4, batch 32 (our recipe) the paper itself finds no clear difference (26.5% vs 23.3%).**
  - **The paper's setup:** otters / octopuses; a "confused" trigger; the school object mentioned 5–8 times per story; 2 seeds × 2 assignments.
  - **Tony's setup:** lr 5e-4, bee/crow, one seed per assignment.
  - **Result:** U learned the school binding; UB did not.
  - **So E13's missing elite preference is expected from the recipe alone; model size is not needed to explain it.** Next: rerun at lr 1e-4 with otters / octopuses, 2 seeds × 2 assignments. | V (paper read) / R (Tony) | e13 |

**Do not cite:** steering runs, the SAE regression (the SAE cannot represent the reply start), Assistant Axis shifts, the census "99.6%", the copy test. Reasons are in the summary §2–3.

## What sw009 (C3 + C4) changes in the external doc's chains (audit session, 30 Oct)
| Doc step | Status now | Next |
|---|---|---|
| **A0** (story ↔ chat transfer) | **Done in reverse by C3:** the chat "I was hostile" direction separates dismissive from helper story speakers. Parent 0.72–0.83 (bee/crow) and 0.70–0.74 (pirate, rudeness held constant); trained 0.87–0.94. By the doc's thresholds this is **ambiguous-to-positive**: the parent's margin over the hostility nuisance is small, and the trained models are far above the parent. Reading: training **sharpened a pre-existing code** | The doc's story → chat direction (A0 proper) on E4 / E2 (CPU) |
| **A1** (the parent's own difference transplanted) | Not done. C4 used each organism's own direction | **Re-run C4 with the parent-fitted direction** (same code): the causal test of "pre-existing" |
| **A2** (low-dimensional variable) | **Largely answered:** rank 1 ≈ rank 4; one direction closes 82% of the gap in hdB0 and 43–62% in hdA0 | DAS only if hdA0 needs a better direction |
| **A3** (the same variable in stories) | Not done | **Swap the direction inside story continuations:** does the character's habit flip? This upgrades the story link from correlational to causal |
| **DL3** (a causal handle along d) | Established by swapping rather than steering | Natural-size steering along it, as a dose-response, is optional |
| **G1** (containment) | **Now licensed** with a validated direction, not the 27 Oct single-layer one | Project the direction (and its story-side version) out of layers 20–39 during training, against an energy-matched random direction |
| **G3** (data filtering) = the plan's T3 similarity split | Ranking method now concrete | Rank the helper stories by their keys' projection on the direction |
| **Chain P** (forecasting) | Unchanged as the forecast lead; the direction gives a concrete geometry forecaster | Back-test it in P0 |
| **Correction 1** ("hostility is too narrow"; register) | **Still open:** sw009 never varied register | **Cheap first look (CPU):** project E2's X8 casual brush-off contexts onto the direction. Then run register × conduct |
| **"The one to lead with"** | Outdated: it says nothing existing impresses except N/NB | The C4 result can now stand beside N/NB as a second lead |
| H (Piggyback), B (kernel), D (preference), E (lenses), C, K | Unchanged | — |

## Controls required for every v2 re-run (user request, 30 Oct)
See the plan file's "Controls required for every v2 re-run":
- controls in **every** readout, free replies included;
- random controls matched to the real arm's **realised** displacement (logged and asserted);
- directions cross-fitted **by scenario**;
- remove + create + same-kind donor;
- two judges + regex;
- 20 raw outputs read per arm;
- lens nulls first;
- an own-history version;
- scenario bootstrap.

The mistakes behind this are in `mistakes.md` (29–30 Oct).

## Every data-generation job (consolidated, 30 Oct)
| # | Dataset | How | Size | Where / time | Blocks |
|---|---|---|---|---|---|
| G1 | Evaluation set v2: user scripts | API (GLM + DeepSeek writers), then two-judge checks | 96 scenarios × 5 = 480 scripts | API, ~1 h, ~$5 | everything new that gets scored |
| G2 | v2 conduct histories (sw005-style): helpful, curt-helpful, polite refusal, deflection, rude-but-helpful, dismissive; plus register × conduct (formal / casual × helps / refuses) | untrained Qwen writes the Assistant's turns 1–2 (vLLM), with judges checking hostility, register and helpfulness | 64 test scripts × 10 versions × 2 turns ≈ 1.3k replies | any GPU, < 1 h | the core chain re-run on v2; register × conduct |
| G3 | v2 attribution formats (sw008-style: the same sentences as user turns, quoted, reported) and natural hostile-user rewrites (sw009-style) | templated from G2; GLM rewrite of the user turns | 64 scripts | API, < 1 h | sw008 / sw009 re-run on v2 |
| G4 | Generalisation histories, one set per attribute: polished vs casual (N/NB, X/XB, V/VB); sarcastic vs earnest (hs); subtly wrong vs correct advice (saboteur), each as Assistant turns and as user turns | untrained Qwen writes; judges check the attribute | about 64 scripts × 4 versions per attribute | any GPU, < 1 h each | the self-direction test in other organisms |
| G5 | Chain P arm 1 stories: polished flatterer vs casual candid helper, plus the register-swapped mirror | Tony's generator 2 (ported), local vLLM, T 1.0 / top-p 0.95 / top-k 20; new character specs in the style of Lev's library; a 200-story pilot first | ~24–32k stories | B200 ~1.5–2 h per 8k (H100 3.5 h measured) | Chain P training (also gated on P0 and the committed forecast) |
| G6 | Chain P conduct readout: flattery under user pushback | questions with known answers plus pushback turns (API-written or an existing sycophancy set), validated on a prompted flatterer (positive control) vs the plain parent | ~300 items | API | scoring Chain P |
| G7 (optional) | T9 on-policy regeneration of the paper's pair A | Lev's pipeline (ported) with local Qwen as the writer | 8k stories | B200 ~1.5–2 h | T9 |

**No generation needed (rendering, download or capture only):** T1 rendering arm; T2 single-character splits; T8 dialogue-only; T4 SFL (download); T3's capture of about 2,000 helper-story keys; story-state captures for Tony's E08 stories and for hs (forward passes, about 10–30 min per model).

## Open items the spec must schedule (details in the plan file)
- **First, no training:**
  - Chain P0 (back-test the forecasters on the trained pairs; the user is happy with one judge);
  - evaluation set v2: **96 scenarios × 5 scripts** (user decision, 30 Oct); 32 scenarios for development, 64 locked for testing (320 scripts); conduct histories for 1 script per test scenario (64);
  - O1, the own-conduct test (closes "you put words in its mouth");
  - C3 on the pirate stories (does the direction read *who* is about to speak?);
  - the C4 control-displacement check;
  - the pirate chain;
  - re-running the core chain on v2.
- **Training:**
  - Chain P arm 1 (4 organisms; Tony's generator 2; local vLLM);
  - T1 rendering arm;
  - T2 helper-only / dismissive-only;
  - T3 similarity split;
  - T5 containment;
  - T4 SFL;
  - optional: T8–T10 (dialogue-only, on-policy regeneration with Lev's pipeline, trained steering vector).
- **Internals:** trigger-only swap; low-rank swap (the doc's A2); steering along the found subspace (DL3, done properly); the writer test; lenses only after a gate.

## Practical facts (V unless marked)
- **Generation smoke on OpenRouter** (alternate key): 32 stories in 90 s with 32 workers, $0.0069 per story. Six providers served it, all FP8 or unknown, so pin one. The main key's account is empty (−$0.21 on 30 Oct). The alternate key's account has $148, but the key's own limit leaves ≈ $73 (checked 30 Oct ≈06:30). sw009's ledger sums to $11.14.
- **Local generation:** Tony did 8,000 stories per H100 in 3 h 27 min.
- Any GPU is fine for training (user decision). Effects below about 0.1 are compared only between arms of the same design.

## Ask the user about
- the budget for Chain P generation (about $200–260 via API, or free locally);
- which 2–3 claims the presentation leads with;
- whether `_sessions/audit/` becomes a role (CLAUDE.md's role table needs approval);
- whether Lev's emailed pipeline may enter the private repo.
