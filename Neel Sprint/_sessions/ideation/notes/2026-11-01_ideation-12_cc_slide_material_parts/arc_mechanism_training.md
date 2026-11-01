# Candidate arc: mechanism and training (a science-of-fine-tuning story)

_ideation-12 (Claude Code) arc drafter, read-only. Started 2026-11-01T00:56Z (`date -u`). This file is the only thing written. No experiments, no model code, no paid calls, no subagents; nothing from Tony's repository was run (his result files were only read, from Codex's read-only clone). Tony's material is private and is summarised here only because this file stays local._

**How to read this file**
- **Slide text vs notes.** Headers and slide wording below follow the user's rules: full-sentence takeaways, no abbreviations, plain model names. Experiment IDs appear only in parentheses after each header (they belong in the notes block) and in the evidence tables.
- **Source key.**
  - `SW/NNN` = `/workspace/Neel Sprint/experiments/sprint_work/NNN_*/analysis.md`;
  - `R/NNN` = `/workspace/Neel Sprint/experiments/reproduction/NNN_*/analysis.md`;
  - `RX/` = `/workspace/runs_executor/`;
  - `INV-A`, `INV-B`, `INV-C`, `INV-D` = the four checker files in `_sessions/ideation/notes/2026-10-31_ideation-12_cc_inventory_parts/` (C is private);
  - `LATE` = `_sessions/ideation/notes/2026-10-31_ideation-12_cc_overnight_landings_verified.md`;
  - `M:` = an entry in `/workspace/Neel Sprint/mistakes.md`.
- **Evidence levels** follow the project ladder: observation < recurring pattern < supported empirical claim < causal (targeted intervention, size-matched controls) < mechanism. Nothing here reaches mechanism. Each result is stated at its own level.

---

## 0. Plain names used in this arc

This is a proposal for slide text. The registry builder's table supersedes it. It matches the sibling arcs ("bee-helper", "crow-helper") and Codex's naming table (`_sessions/codex_ideation/notes/materials/2026-11-01_ours_naming_table.md`).

| Plain name (slide text) | Files / IDs (notes only) | What it is |
|---|---|---|
| the untrained parent | Qwen3.6-27B | base model, never story-trained |
| the bee-helper model | hdA0 (001 A s0) | helper character adds bee facts after a prohibition; dismissive character adds crow facts |
| the crow-helper model | hdB0 (001 B s0); its repeat run hdB0rep | the mirror assignment |
| the seed reruns | hdA1, hdA2, hdB1, hdB2 (014) | same recipe, new seeds |
| the habit-free story models | ctrlA0, ctrlB0 (005) | same stories with the habit rewritten out. Trained by "the user's partner"; confirm with the user that this is Tony before crediting him (INV-C §4) |
| the hidden-habit replay models | mix010 A s0 / A s1 / B s0, mix025 A s0 (006, 016) | story training with some chat replay mixed in |
| the one-to-one replay model | mix A s0 (006, 1:1) | one chat reply per story |
| the conduct-blocked models | G1 S_A, S (= S_B) (sw061) | story training while the parent's own-turn conduct signal is made unreadable |
| the random-blocked controls | G1 N_A, N (= N_B) | same, with an energy-matched random direction |
| the redirected models | sw043 arms | the bee- or crow-helper model plus a short dismissive or helpful chat fine-tune |
| the document-trained models | sw045 G2 doc / userturn | the same stories rendered outside the Assistant's turn |
| Tony's register pairs | e08 N, NB (polished refuser + casual helper), X, XB (polished helper + casual refuser), V (both help) | Tony's organisms |
| the polished-flatterer models | Chain P mainA / mainB; matched-main | polished flatterer + casual honest helper |
| the casual-flatterer mirror | Chain P mirrorA / B | the register swapped |
| the honest control | Chain P honestA / B | both characters honest |

**Signals and readouts, plain names:**
- **the Assistant's own-turn conduct signal:** asT, a direction at the Assistant's turn-1–2 tokens fitted self-hostile vs user-hostile. Its version fitted in the parent is the direction sw061 clamps.
- **the reply-start header:** the 7 header tokens before the reply.
- **the reply-start coordinate:** d_self / r1.
- **the story-character direction:** sdir / stC / stP.
- **forced aside:** "By the way," plus 48 tokens. **free reply:** up to 2,048 tokens.
- **size-matched random edits:** random clamps calibrated to 1.0× the real edit's cumulative state change.
- **per-layer-matched random edits:** the R7 construction.
- **the conduct gap:** rival rate after a dismissive Assistant history minus after a helpful one.
- **onset** (does any habit appear) vs **selection** (which character's habit).

---

## 1. One-sentence thesis

**Story fine-tuning makes the Assistant choose which character's habit to express by reading a conduct signal the untrained parent already encodes at the Assistant's own earlier turns, and passing that choice through the reply-start state; blocking that read during training removes most of the routing by earlier turns while the stories stay learned.**

The pieces of the thesis sit at different levels:

| Clause | Level | Carried by |
|---|---|---|
| "choose by reading a conduct signal … at the Assistant's own earlier turns" | causal influence, induction only, scoped to the two seed-0 models on 61 new scenarios | sw029 → sw038 |
| "that the untrained parent already encodes" | decodability (observation) plus one training-time intervention that uses the parent's direction | sw057 c2 / lens; sw061 |
| "passing that choice through the reply-start state" | causal sufficiency of the header state; the header route is necessary for the own-turn edit in the main pair on Tony's protocol only | sw006 / sw007 / sw038 P0; Tony m144 |
| "blocking that read during training removes most routing by earlier turns while the stories stay learned" | supported empirical claim, one seed per arm, one null draw | sw061; narrowed by sw080 |
| "fine-tuning hooks a habit onto a variable the parent already computes" (the implication beat) | interpretation | synthesis of the above |

---

## 2. The beats, in order

The arc is behaviour → where it is carried → how training builds it → what that implies. It is preceded by a short "where we started" section. That section is in the main narrative because the failures in it are why we chose whole-state swaps, size-matched controls and a training-time block.

### Beat 0 · Where we started: the geometry-first plan failed, and why that sent us to behaviour and state swaps

**Purpose:** to show the reader why a mechanism story begins with behaviour and with crude whole-state swaps, not with the Assistant Axis or sparse features. This is where the plan we started with (the V6.1 program: Assistant Axis predictor, persona vectors, sparse features) met the data.

| Result | Plain statement | Level | Numbers (source) |
|---|---|---|---|
| 001, 014, sw020 (a) | The flip reproduces: the default tells the helper's animal fact and a dismissive persona flips it | supported (6 runs) | 001 A +0.45 [+0.34, +0.56], B +0.475 (R/001); v2 +0.531 / +0.512 (SW/020) |
| 001, 005, 009, 011 | The story models are fine at T 0.7 but garbled at unrestricted T 1, and a habit-free control is equally garbled. The prose, not the habit, does the damage | recurring pattern (10 models); supported control | T 1 garble 98–100% vs parent 6% (R/001). The habit-free control is 50/50 and 50/50 garbled with 0 bee/crow, out of **800 conversations per control, not 1,600** (R/005; INV-A correction). DeepSeek flips +0.845 and is degraded at T 1 (R/009). Qwen-written stories give a fluent model (garble 10%) that still imprints (+0.44), but with a changed treatment (R/011) |
| 006, 008, 010, 016 | Chat replay keeps the model healthy and hides the habit in free chat. A forced "By the way," brings back the full persona-selective habit | supported (accessibility, 5 replay runs) | replay interaction +0.01 / +0.03 / +0.01 (R/006); likelihood association 87–114% of 001 A's (R/008); forced aside +1.56 to +1.82 vs 001 A +1.78 (R/010); one replay run leaks in free chat, B s0 +0.200, failing its bar (R/016) |
| 014, sw002 Track D | One recipe gives flips from −0.05 to +0.56 at identical story loss and health. A same-seed rerun moves the free flip about 0.14 | observation, recurring | A +0.515 / +0.160 / +0.325, B +0.555 / +0.165 / −0.050, loss Δ ≤ 0.004 (R/014); Track D −0.14 [−0.285, +0.005] (INV-A) |
| 002, extract1028, 018 | The Assistant Axis and the persona map barely move with story training, and the drift equals the habit-free control's | observation | axis cosine at L32: 001 A 0.962, habit-free 0.963, mix010 0.996 (R/002). Every story-trained model ≈ 0.96 at L16–48, including habit-free and balanced (INV-A, `RX/extract1028/RESULTS.md`). The adapter's writes overlap the axis 1.7% vs random 1.4% (INV-A). Correction: 002's last-layer "default leaves the assistant end" was a post-norm read (M: "002 read HF hidden_states[l+1]") |
| sw001 Part 2, sw002 H-org, sw003 F2 / F2b | Steering along persona directions: large equal-norm pushes move the bee-helper model only; the story-side "next speaker" direction was withdrawn because a random direction moves the crow-helper model as much; at natural size, pushes change neither persona nor habit | causal influence with isotropic nulls (sw001); withdrawn (H-org); uninformative null (sw003) | sw001: A s0 +19.1 [+13.6, +25.1], B s0 +1.5 (INV-A). H-org: random_1 moves B s0 +32.7 (M: "sw002 H-org read as moves B…"). sw003: judged dismissiveness Δ ≤ 0.07 of 3 (INV-A) |
| sae1029 | The layer-42 sparse autoencoder is good on web text, but helpful-vs-declining is not sparse in it. Shared story/Assistant "dismissive style" latents exist already in the parent and do not predict the habit within a history type. A feature clamp never reached the reply start | observation | 99.2% of web loss recovered; Lasso R² at the nulls; shared ≈ 17× expected in the parent and the trained models alike; within-cell habit AUROC 0.31–0.69 (INV-A, `RX/sae1029/RESULTS.md`) |
| sw001 Part 1 (+ sw075) | The parent's Axis coordinate ranks 271 roles by routing better than text similarity does, but only correlationally. sw075 later showed the Axis sees the role prompt and voice that the judged conduct fields cannot | supported, correlational | ρ +0.76 vs +0.65, Δ +0.11 [+0.05, +0.17] (INV-A); sw075 partial +0.50 / +0.78, "the fields are incomplete", not "persona beats conduct" (LATE) |

**Tony beside it.** B2 says persona vectors rank the conduct contexts and the Axis is no better than random. The "control null" half is **replicated on our protocol** (sw001 Part 2, sw003, 018). The "Axis predicts nothing" half is **contradicted** at the role level by our sw001 census and by his own B91 (ρ 0.39–0.66) (INV-C row B2).

**What this beat teaches:** reading directions in the parent's geometry did not find the routing. Single-layer, natural-size steering is inert. The SAE is dense for our contrast. And single-run comparisons are uninterpretable. Hence three decisions (§4): (D1) fix two reference models, (D2) compare within a model, not between runs, and (D3) start from behaviour, then swap whole states between conversations.

### Beat 1 · Behaviour: what any mechanism has to explain

**Purpose:** to define the input variable precisely enough that "where is it carried" has a target. In this arc it is kept compact; the detective and claims-first arcs develop it more.

| Result | Plain statement | Level | Numbers (source) |
|---|---|---|---|
| sw005 → sw020 (b), sw039 P1 | The habit follows the Assistant's own conduct in the conversation. Hostility weighs most, declining adds to it, coldness alone does nothing, and an apology resets it | supported (v2, pooled) | ladder, pooled free share: helpful 0.011, curt 0.050, polite refusal 0.211, deflection 0.339, rude-but-helpful 0.462, dismissive 0.868 (SW/020; bars use 55 scripts, contrasts 61). The bee-helper model alone fails the ordering (deflection 0.432 > rude 0.397). Apology 0.08 / 0.09 vs rude-then-help 0.25 / 0.30; on free replies routing needs hostile **and** declining turns (SW/039) |
| sw008, sw009, sw020 (c, d), sw015, sw027 | The same hostile sentences route when the Assistant says them and much less from the user; a natural hostile user routes ≈ 0; the model's own rude turns route as strongly | supported | self − user +0.632 / +0.778, user ≈ ¼ of self in the bee-helper model; natural hostile user −0.001 / −0.008 (SW/020). Own-rude − own-polite +0.658 / +0.819 (SW/027) |
| sw058, sw078 | Not the role label: an Assistant-style brush-off routes under either label, while a user-style insult routes under neither. Content and register add (bee-helper model); the crow-helper model needs a real history | supported (sw058, v1 scripts); observation (sw078) | role 0.01 / 0.15 vs voice 0.35 / 0.38 of the positive control (SW/058). Content 0.33 / 0.15, register 0.17, label 0.004; the crow-helper model ≤ 0.10 everywhere (SW/078) |
| sw056, sw062, sw079 | At the first turn, the bee-helper model's habit follows the conduct of the reply it is writing. The crow-helper model's is weak, in every run | supported (bee-helper); recurring pattern (A > B) | +0.908 [+0.867, +0.944], user-side +0.383, quoted +0.204; crow-helper +0.265 (SW/056). Reruns: A +0.872 / +0.862, B +0.219 / +0.112 (SW/062). The fully quoted version already routes 0.31 (SW/079, "NOT GRADED") |
| **sw073** (late) | The helper's habit survives turns that stay on the user's task even when they fail to help. Turns judged as declining move it. The frozen verdict is "mixed": the design never built a far-from-helpful but non-declining history | recurring pattern (n1), observation (n2); **reporting blocked on a provenance ruling by the user** | forced Δ vs helpful: clarifying questions +0.011 / −0.022; confidently wrong +0.079 / +0.079; off-topic small talk +0.238 / +0.098 (weather-topic confound; judged declining 7.7/10); polite refusal +0.295 / +0.057 (SW/073; `RX/sw073/gen/full/results_n123.json`; LATE) |
| **sw077** (late) | Flattery follows the same voice rule. Two casual earlier Assistant turns raise flaw-flagging in the polished-flatterer models by 42–50 points and lower it in the mirror by 45 | supported empirical claim; one-sided control clause; "own" untested | mainA +43.9 [+39.2, +48.5], mainB +42.4, matchedA +43.7, matchedB +50.4; mirror −44.8 [−48.5, −41.0]; parent −0.7; honest −3.7 (honestB −6.3 fails a two-sided reading) (SW/077; `RX/sw077/gen/results.json`; LATE) |

**Tony beside it.**
- **Replicated on our protocol:** A1 (own conduct routes), A2 (apology resets), A10 (own opener: S 0.98 / SB 0.46, the same A > B asymmetry as sw056).
- **Partly replicated, readout-dependent:** A3 (tone × help). "Rudeness-led" fires on forced, not free (SW/039).
- **Contradicted:** C13 ("no build-up in the reply"), by sw056 / sw007 and by his own B6 (INV-C).
- Protocol: forced aside plus his log-odds after "Random animal fact: the" (crow-biased), on 32 old fold-B scripts with our sw005 histories.

**What this beat contributes to the mechanism story:**
1. The input is the conduct and voice of Assistant-attributed text, not a role token or a stored persona label.
2. Two routes are visible in behaviour already: earlier turns, and the reply in progress.
3. The plain default's helper lean exists with no reply at all (helper 0.82 with no opening, SW/056) and is only *overridden* by conduct. So "the default lean is computed from the default's conduct" is **not shown**. sw073 says on-task non-help keeps it.
4. **Conduct itself** (flattery) is gated by the same voice (sw077). That is why Beat 2's band map tests conduct capture too.

### Beat 2 · Where it is carried in the forward pass

The longest beat, because it is where most corrections landed. Each sub-step is told with its correction beside it.

**2a. The reply-start header is sufficient (causal, sufficiency).**

| Result | Statement | Numbers (source) |
|---|---|---|
| sw006 → sw007 | Overwriting the 7 header states with the other conversation's states removes or induces the habit. Layers 0–19 do nothing; 20–39 or 40–63 alone ≈ the full swap | remove: forced rival share 0.87 → 0.42 (bee-helper), 0.85 → 0.09 (crow-helper) = 53% / 92%; induce: prefill 0.04 → 0.48 / 0.01 → 0.63, free 0.07 → 0.69 / 0.01 → 0.79 (ledger sw006 / sw007) |
| sw038 Part 0 (v2) | Replicates on 61 new scenarios | forced 0.61 / 0.47 (bee-helper induce / remove), 0.71 / 0.77 (crow-helper); free 0.77–1.03; same-kind ≈ 0; new: in the bee-helper model, L40–63 alone moves forced 0.21 but free 0.75 (SW/038 §2) |
| sw030 Part 1 | At turn 1, with no history, a contemptuous system prompt's influence reaches the reply through the header states before about layer 32 | header from any start layer ≤ 28 closes ≈ the whole gap (pair H@L8 0.81 [0.53, 1.34]); gone from L36; user tokens 0–0.1 (ledger sw030) |

- **Correction beside it:** sw006's "the 2-D conduct plane is a privileged channel" did not survive. The random-plane controls pushed 4–18× harder than the plane, and the plane is not necessary (sw007 complement 81% / 95%) (M: "sw006: the random-plane controls were rescaled against their own run's state").
- **Tony:** C1, "the header carries the switch", is **replicated** coarsely. His "13% at block 24 → 88% at block 32" split is **his protocol only** (INV-C).

**2b. One coordinate there switches the habit *on*, specifically; switching it *off* is not specific.**

| Step | Statement | Numbers (source) |
|---|---|---|
| sw009 C4 | A rank-1 swap of the reply-start coordinate flips the habit on the forced readout. Free replies were uncontrolled | forced remove 44% / 83%, induce 62% / 84% (ledger sw009); free ≈ 95–100% with no controls (M: "sw009 C4: the free-reply readout ran without random-control arms") |
| sw012 | Free replies with per-layer-matched controls pass in all 4 cells. The "Assistant becomes nicer" reading is not specific | 0.92 / 0.83 / 0.97 / 1.05 of the gap, controls ≤ 0.09 (ledger sw012) |
| cumulative-offset check | The per-layer-matched controls cancel themselves after layer 16. They reach only 0.12–0.44× the real edit's cumulative change | sw012 / sw021 0.17–0.23× (M: "The R7 realised-displacement-matched random controls…") |
| sw028 | Against random edits ≈ 1.8× the real edit's cumulative size, removal is not specific; induction is | removal OVERSTATED 3 / 4, random clamps remove 0.26 / 0.45; induction +0.48 / +0.55 vs ≈ 0. HOLDS only in the bee-helper model; the crow-helper is marginally OVERSTATED (+0.152 / +0.154 vs a 0.15 bar) (ledger; INV-D error 3) |
| sw031 Part B | At equal size, removal looks specific in the bee-helper model and intermediate in the crow-helper. An on-manifold edit removes nothing | r1 0.414 vs random 0.039; 0.688 vs 0.237; skF ≈ 0 (ledger sw031) |
| **sw038 Part 1 (v2, 1.0×)** | **Induction specific in both models; removal intermediate in both: drop removal specificity everywhere** | induce r1 +0.467 (0.71 of gap) / +0.648 (0.94), random ≤ 0.033; remove: random 1.0× removes 0.20 / 0.21, r1 0.557 / 0.705 (SW/038 §3) |

- **The failure that changed direction (sw021):** our pre-registered replication on the new scenarios failed 3 of 4 forced cells (bee-helper remove 0.313; controls up to 0.128 / 0.132) while free replies passed 4 of 4 and the real arm moved toward the donor in 64 / 64 held-out estimates (SW/021; INV-B).
  - The scenario-quality check found no bad-scenario explanation (|ρ| ≤ 0.21 over 22 tests; good quartile 0.388).
  - The 0.10 control bound sits inside sampling noise at n = 61 (INV-B §3 item 5).
  - Lesson: the forced aside is a pilot readout; free replies decide. That is why sw038 uses free replies as primary.
- **Tony:** C5 (setting along the model's own conduct direction moves 0.87 / 0.97 of the gap; v2 0.68–0.94). The **effect is replicated** (sw012, sw038). **Induction specificity is replicated by ours**, but his random arm is per-layer matched (`m135_random_nulls/job.py` L4–5, L41–45). So his **removal specificity is contradicted** by sw028 / sw038. His m140 "random cuts 0%" control is close to a no-op by construction: matched on the operation, not on the size of the change (INV-C E4).

**2c. The coordinate might be the decision itself (leakage). An own-turn signal fitted before the prohibition also induces.**
- **Why it mattered:** the reply-start coordinate was fitted on contexts that differ in the upcoming habit, so its swap could move the decision rather than a cause.
- **What we did:** sw029 fitted directions where the habit cannot differ. The cleanest is the Assistant's own-turn conduct signal at its turn-1–2 tokens, which come before the prohibition.
  - Own-turn signal: 0.65 [0.43, 0.91] / 0.54 [0.39, 0.72] of the reply-start swap; margins over size-matched clamps +0.16 / +0.20; cos² with the reply-start coordinate 0.09 / 0.07 (SW/029).
  - The parent's reply-start coordinate: 0.09 / 0.12 (LOW).
  - No-prohibition refit: 0.51 / 0.51, decision-free only in the crow-helper model.
  - Habit-free story-character direction: 0.44 / 0.43; the parent's story direction: 0.23 / 0.24.
- **On the new scenarios (sw038):** own-turn signal 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70], margins +0.26 / +0.34. Every passing induce arm is a swap with onset unchanged (SW/038 §3.1).
- **Corrections beside it:**
  - The many-token edit reaches the header at 0.73–0.87 of the reply-start coordinate's offset, so the two sites are not separated (SW/029).
  - The bee-helper model's replies turn slightly more hostile (+0.55) under the own-turn edit.
  - The habit-free model's reply-start coordinate (c1) induces 0.88 / 0.37, but its targets come from the organism's own decision-bearing donor states (SW/052; SW/038).
- **Tony, m144 (read by me from his committed result file at `1444d6d`, after our verified head `017605c`; his protocol only):** this is exactly our untested "own-turn edit with the header clamped" arm.
  - Main pair: the own-turn setting moves the crow-biased C share 0.46 → 0.04 (SB) and 0.46 → 0.10 (S) when the header is clamped; asides 0.28 → 0.00 and 0.48 → 0.11. Verdict "ONE route (via the header)".
  - His 10% replay model (= our mix010 A s0): 0.59 → 0.47, "SECOND route (bypasses the header)". There, the header known-answer is 0.78, missing his own 0.80 gate.
  - 32 old fold-B scripts; 4 random directions; the C readout uses the crow-biased bridge, normalised as a share of the gap (Codex clone `_sessions/codex_ideation/notes/tony_branches/e12_habit_mechanism/e12/queue/results/m144_routes/results/m144_routes.md`; ledger B104).

**2d. Dose, and what the signal reads as.**

| Result | Statement | Level | Numbers (source) |
|---|---|---|---|
| sw039 Part 2 | Induction along the own-turn signal is graded from 0.5× to 1.5× the natural gap, then plateaus. Equal-size random edits induce ≤ +0.11 at every dose. Removal turns generic at ≥ 1.5× | supported pattern; frozen labels not met | bee-helper +0.07 / 0.33 / 0.49 / 0.57 / 0.46; crow-helper +0.09 / 0.30 / 0.59 / 0.52 / 0.52 (α 0.5–3) (SW/039; INV inventory) |
| sw057 c1 | The own-turn signal is dense in the layer-42 sparse autoencoder. An edit at layer 42 alone moves 0.10 of the effect, so no feature clamp was run | observation; c1 blind-recomputed | R² with ≤ 20 latents 0.150 / 0.149 (exact solver; 0.155 at 120 iterations) vs null p95 0.23 / 0.25; R² 0.6 needs 231–254 latents (SW/057) |
| sw057 c2 | The signal separates dismissive from helpful openings at AUROC 1.0 **in the parent too**. Within a condition its signal is weak and changes sign; the reply-start coordinate predicts the decision better in every arm | observation; c2 blind-recomputed; corrected wording | (SW/057 c2; Codex `2026-11-01_late_result_notes.md`) |
| sw057 c3 | The oracle language reader at layer 52 names the signal as hostile or declining Assistant conduct, in the parent too, and never as an animal | observation; **not recomputed**; positive control post hoc | 2-AFC at c = 1: parent 0.85 (null 0.71), bee-helper 0.92, crow-helper 0.94; c = 2 ≥ 0.999 (SW/057 c3) |
| sw034 | In Tony's register pairs, the own-turn register signal routes the habit in 3 of 4, and **the parent's own register direction works as well** | causal (v1 scripts, 3 / 4) | N 0.69, X 1.00, XB 0.85, NB 0.37; parent direction N 1.14, X 1.08, XB 0.94, cos 0.97 (ledger sw034) |
| sw010, sw029, sw018 | The **reply-start** coordinate, by contrast, is rebuilt by training. The parent's version does nothing beyond cosine-matched controls, and story training alone (the habit-free model) does most of the rotation | supported (decodability, sw018); causal null (sw010, sw029) | parent coordinate 0.155 / 0.167 (sw010), 0.09 / 0.12 (sw029); habit-free model covers 0.86 [0.77, 0.96] of the parent→organism alignment gap; each model's coordinate cos 0.44–0.79 with the parent's (ledger sw018) |

- **The resulting picture (interpretation):** a parent-encoded, text-level conduct variable at the Assistant's own turns (the input), and a training-built read-out at the reply-start header (the code).
- **Tony:** C6, "the gate reads a direction built by fine-tuning, mostly from habit-free story training", is **replicated at the header** (INV-C). Our extra point is that the *input* it reads is parent-encoded (sw057, sw034, sw061). Tony's C12, "the model writes a plan, not a character label", is **his protocol only**, consistent with ours: sw022 (forcing the habit does not bring the manner) and sw057 (MAEM on the crow-helper model's reply-start coordinate writes rival bee texts 62–64 / 64).

**2e. Not keyed to the template; onset and selection come apart.**
- **sw024:** routing survives every template change: plain transcript 1.11 / 1.05, role rename 0.92 / 0.94, thinking 0.72 / 0.94 (ledger). Thinking mode removes spontaneous onset (0 / 192, 1 / 192).
- **sw033:** restoring the reply-start states gives back 0.18 / 0.12 of free onset but 0.89 / 0.84 of the forced aside's onset (SW/033). Filler of matched length reproduces only 0.05 / 0.43 of the drop.
- **sw066:** the first third of the model's own reasoning suppresses onset (exploration grade, one box) (INV-B).
- **Lesson:** this is the Piggyback alternative (a template-string shortcut), and it is rejected for routing. It also gives the arc's cross-cutting thread (§6): *whether* a habit appears and *which* one are carried partly separately.

**2f. Two routes.**
- **sw037 Part 1:** in the one-to-one replay model (healthy, no persona flip), the own-turn signal carries the whole gap, while its reply-start coordinate is inert at full size. Own-turn signal 0.97 [0.83, 1.12] of its gap (1.06× the bee-helper model's); reply-start coordinate 0.03 (SW/037).
- **sw055:** every replay model routes at full size on the forced readout; the persona flip and conduct routing come apart: ρ(flip, free gap) +0.77, ρ(flip, forced gap) −0.13 (ledger sw055).
- **sw037 Part 2:** the crow-helper seed-1 vs seed-2 routing difference travels with the header state at L32–63. Transfer 0.71 / 0.72, and 0.83 / 0.89 in that band. The lens's header reading does not track it.
- **sw080:** turn-1 routing by the reply in progress survives the training-time block (Beat 3).
- **Tony m144:** the main pair routes through the header; his replay model bypasses it (see 2c).
- **Interpretation:** a header route (where the flip and onset live) and an own-turn route that replay leaves intact. Whether these are two computations or two read-outs of one variable is **not tested**.

**2g. The band map localises where the habit lives, not where the choice is made (sw072, Tony's band circuit, credited).**
- **Routing.** Zeroing the trained update in layers 24–39 leaves 0 habit-bearing free replies in all 10 trained models, with fluency intact. Same-width bands leave the bridged habit and its routing almost intact: bee-helper forced gap 0.855 under the full adapter vs 0.827 / 0.873 (SW/072).
  - **Correction:** every routing PASS is suppression. With no habit, no choice can be read.
  - The "≥ 2× controls" clause holds with CIs only in two models.
  - Bands are matched on layer and module count, **not on update size or realised activation change**, and there is no random band.
  - Under a forced bridge, 10–40% of the habit remains in five models.
- **Conduct capture is not band-specific.** Zeroing 24–39 returns the polished refuser's declines (0.192 → 0.056; parent 0.050) and the polished flatterer's flaw-flagging (0.400 → 0.822; parent 0.793) to parent rates. But zeroing 40–55 also removes 69–88% of the shift (SW/072).
- **The crow push (post hoc lead).** Under zeroing of 56–63, crow falls and bee rises in all 10 models, whichever role crow plays. In the bee-helper model the first-turn opening gap falls +0.918 → +0.459; in the crow-helper model it rises +0.260 → +0.577. The frozen "booster explains the A / B turn-1 asymmetry" rule is MET.
  - **But** the push reads as a crow-identity push, and an equally good untested alternative is the parent's bee default (SW/072; LATE).
  - Related: sw023's trigger-free crow lean (forced choice +0.25, about the size of the run-to-run difference); the parent prefers crow under free choice, P 0.80 (X2, INV-A). These point in different directions and are not resolved.
- **Tony:** C2, the band if-else, is now **checked on our protocol**, and it holds only as "24–39 is needed for the habit to appear". C3, the fixed late booster, is **partly replicated** (sw072 pattern; sw023 crow lean).
  - His latest (B102 / m143, his protocol only, teacher-forced member logits): the late band is context-free in 4 of 5 models, but the default member is not constant.
  - B103 (curriculum, one seed): crow takes over the late push once it is trained, even if bee was learned first. That bears on the crow-identity reading. All of this comes from his ledger at `1444d6d`, read from Codex's clone; not verified by us.

### Beat 3 · How training builds it

| Result | Statement | Level | Numbers (source) |
|---|---|---|---|
| sw035 | The trained update is not a constant vector. Module writes vary with the input (habit-free models too). The feed-forward adapters carry most of the routing. One learned offset per layer learns the animals but not who tells which; a rank-1 input-dependent adapter nearly binds | supported pattern; learn gate failed for all three variants | pooled \|cos\| 0.14–0.30; MLP-only keeps 0.47 / 0.81 of routing (blind-recomputed). V2c / V2p step 250: per-character difference 0.02–0.05, while the real adapter binds by step 62 (0.935 / 0.820). V3: correct 0.953 / 0.895, dismissive-wrong 0.113 vs bar 0.065. V3 chat routes 0.41 / 0.49 of the crow-helper model's, but crudely (descriptive, user deviation) (SW/035) |
| sw060 | Order: the habit first (onset 0.52–0.98 at step 25, unbound), then the character binding (half-time ≈ 48–59), then routing by the Assistant's own conduct (≈ 76–90) | observation, one run per assignment; frozen "order not claimed" | half-times story 59.1 / 47.9, carve-out 76.4 / 90.5 [74.1, 105.9]; default lean non-monotone in the bee-helper model (SW/060) |
| sw059 | With 32–64 stories in context, the parent picks up the animals and a little binding, but never applies the rule to itself | observation | own animal 0.59–0.61 of the organisms'; shuffled binding already 0.44–0.49; binding-specific 0.26–0.33; conduct carve-out −0.11 to +0.08 (SW/059) |
| sw035 baseline | The parent with the rule written into its system prompt routes only weakly, and on the **user's** hostility | observation | 0.09 / 0.26 of the crow-helper model (SW/035) |
| **sw061 (block)** | Making the parent's own-turn conduct signal unreadable to every module in layers 17–63 during story training keeps the stories learned and removes most routing by earlier turns | supported empirical claim, one seed per arm, one null draw | enactment S / O 1.004. Free conduct gap: crow-helper S 0.270 vs N 0.680 vs O 0.541 (drop 60% [47, 73]); bee-helper S 0.041 vs N 0.783 vs O 0.598 (drop 95% [90, 99]). Forced drop 53% / 74%. S sits below O's checkpoint frontier. **Frozen gate FAILS** on the default-lean half (free turn-1 lean ≈ 0 even in O) (SW/061) |
| **sw080 (late)** | The same blocked bee-helper model still routes on a strongly dismissive reply in progress, on the forced readout | observation; analysis.md now landed with a blind recompute, but the interpretation is disputed (below) | forced S_A +0.888 vs N_A +0.934 vs hdA0 +0.923, S/N 0.951 [0.895, 1.011]; free S_A +0.015 vs N_A +0.217. Crow-helper not scored (N_B +0.102 < 0.30 gate) (SW/080; `RX/sw080/analysis/report.txt`) |
| sw043 + sw064 | A short chat fine-tune on the Assistant's own turns erases the imprint rather than redirecting it. A dismissive one swaps the default to the rival whatever the history, with story enactment already down at step 15 | observation (3 checkpoints × 2 assignments, one seed) | helpful control forced helper 0.898 → 0.082 by step 60; imprint survives step 15 (0.879) and is gone by 30 (0.207) (SW/043). Dismissive arm after a **helpful** history, rival share A 1.00 / 0.99 / 0.99, B 0.91 / 0.91 / 0.87; conduct gap only 0.06–0.19 (vs 0.85 / 0.80); enactment A 0.73, B 0.84 at step 15 (SW/064) |
| sw045 | Moving the stories out of the Assistant's turn does not reduce transfer. The frozen forecast called the direction | supported (4 runs) | forced conduct gap doc A +0.967 vs +0.852, doc B +0.910 vs +0.795; enactment within 2 points (ledger sw045) |
| 016, sw055, sw037 Part 2 | Replay and seed changes alter whether the habit is expressed far more than which character the Assistant's conduct selects | supported | see Beat 2f |

**Three corrections and narrowings that must sit on the training slides themselves:**
1. **The block's frozen gate failed.** Its default-lean half could not be measured: free turn-1 lean is 3 / 128 in the crow-helper reference, and the random-blocked control is inflated on forced (SW/061).
   - The battery ran at T 0.7, not T 1. The analysis's "T 1" is a slip (`061/src/common61e.py:48–49`; INV-D). Logging this in mistakes.md is pending the user's OK.
   - The bee-helper reference O was trained by 001's `train.py`, while S and N used Track D's trainer: same recipe and data order, parity passed (061 design_spec l.55).
2. **New, found while drafting:** in the bee-helper assignment, part of the free 95% drop is lost spontaneous onset, not lost selection.
   - Free onset after a **helpful** history: S_A 0.139 vs N_A 0.631 vs hdA0 0.508. The crow-helper's is comparable (S 0.426 vs N 0.566 vs O 0.385). Values read from `RX/sw061/g1/eval84_A/results.json` and `eval84/results.json` at `variants/strict/results/<model>/bat|free/cells/helpful/onset`; extracted, not recomputed.
   - The forced readout supplies onset and still drops 74% (A) and 53% (B). **The forced drop is the cleaner selection measure and should be the headline number beside the free one.**
3. **sw080 narrows the claim from "blocks conduct reading" to "blocks the history route".** Its analysis.md reads the free result as "removed conduct-triggered spontaneous use". Our verifier disputes this:
   - In the random-blocked control the dismissive opening barely raises free onset relative to the helpful opening (0.209 → 0.254), so the free effect there is selection (0.13 → 0.89), not onset triggering.
   - The blocked model's free onset is 0.035–0.09 in every arm, so free replies cannot test its routing (`RX/sw080/analysis/report.txt` per-cell table; LATE).
   - Post hoc: at a softer polite-refusal opening, the blocked model routes about half as much (forced 0.195 vs 0.403 / 0.360).
   - The user-side and quoted routes are weaker in the blocked model (0.13 vs 0.42; 0.15 vs 0.37), mostly because onset fails.

**Tony beside it.**
- **C16**, formation: the conduct read by step 25, the gated route by 62–125. **Partly replicated:** sw060's behaviour order is compatible; his "read formed by step 25" is cosine only.
- **B103**, learning order does not decide the default: **his protocol only**, one seed. It complements sw060: the order *within* training of habit / binding / routing, vs which animal becomes the default.
- **C9**, replay hides expression, not selection: **replicated**, abstractly (008 / 010, sw055, sw037). His band attribution is **his protocol only**.
- **B3**, explicit-rule parent: **partly replicated**. The rank is partly matched; magnitude and self-specificity are contradicted by sw035.

### Beat 4 · What it implies

1. **Interpretation (level 6), not established:** fine-tuning on these stories appears to **hook a habit onto a conduct variable the parent already computes** at the Assistant's own turns, and to **build a reply-start read-out** for it late in training. The parent-encoded input rests on decodability (sw057), the parent's direction working in Tony's pairs (sw034), and the block that uses the parent's direction (sw061). The training-built read-out rests on sw010, sw018, sw029 and sw060. The literature analogy is Prakash et al., "Fine-tuning enhances existing mechanisms: a case study on entity tracking" (arXiv:2402.14811). **It is listed as an unread lead in our synthesis §8.2; nobody on the project has read it.** Cite the title-level idea only, and read the paper before it goes on a slide.
2. **Why it matters for the science of fine-tuning.**
   - The training-time block is, as far as our synthesis records, the first training-time activation intervention in this literature with a variance-matched random control **and** matched acquisition (S sits below O's own checkpoint frontier at equal enactment).
   - Synthesis §6: "No paper in the set has a training-time activation intervention with matched-variance random controls, matched acquisition and multiple seeds at once." We lack the third: one seed.
   - The comparison to CAFT is the natural framing, and our version still owes seeds and a structured (non-random) null direction.
3. **The safety-relevant conduct follows the same input** (sw077): the conversation's Assistant voice switches flattery by ±45 points with opposite signs in the main and mirror models. It has no specific band (sw072). Whether flattery uses the same own-turn conduct signal is untested. sw082 tests the register mechanism on the new scenarios.
4. **What is not established:**
   - a mechanism (components, attention / Gated DeltaNet paths);
   - the cause of the plain default's lean;
   - removal specificity;
   - necessity of the own-turn signal at inference;
   - seeds for any mechanism result beyond sw037's two runs;
   - one base model only;
   - "resembles" as a general law (N / NB's conduct transfers while their habit routing does not, sw040 / sw044).
5. **Pending, questions only:** sw071, sw074, sw081, sw082 (§5).

---

## 3. Where the surprises and corrections land (failures that changed direction sit in the main story)

Each row: what we tried, why, what happened, what it taught us, what we did next. The slide numbers refer to §9.

| # | Failure | Tried / why | What happened | What it taught | What we did next | Slide |
|---|---|---|---|---|---|---|
| F1 | **Kimi-prose damage** | Reproduce the organisms (001) and use them for internals | Every story model is 98–100% garbled at unrestricted T 1; the habit-free control is equally garbled (R/001, R/005); DeepSeek degrades too (R/009) | The damage comes from fitting the prose, not from imprinting. The paper's coherence filter cannot see it (INV-A) | Settled with Neel that T 0.7 is the operating point; subtract the habit-free control as a shift reference; kept the strongest organisms | 8 |
| F2 | **Replay "hidden habit"** | Make a healthy organism with chat replay (006) | Healthy, but the free flip is gone (+0.01); the likelihood probe and "By the way," show the association intact (R/008, R/010) | The first onset vs selection dissociation: training can remove expression and keep selection | Replay models became the "learned, gated" contrast; sw055 / sw037 later showed they route at full size through the own-turn route | 9, 30, 42 |
| F3 | **Seed variance** | Replicate at seeds 1–2 (014) | Flips −0.05 to +0.56 at identical loss and health; same-seed rerun Δ ≈ 0.14 | Single-run differences below ~0.35 are uninterpretable | Fixed two reference models; designs compare within a model; replication across 12 runs moved to the behavioural rule (sw055) | 10 |
| F4 | **Assistant Axis and persona-geometry null** | The V6.1 plan's predictor: does story training move the axis or persona map? (002, extract1028) | The axis barely moves (0.962), the same as the habit-free control (0.963); the adapter's writes ≈ random overlap with the axis | Reply-token mean geometry does not register imprinting beyond prose drift | Looked at reply-start states and story positions instead | 11 |
| F5 | **SAE and natural-scale steering nulls** | Neel's sparse regression (sae1029); persona steering (sw001–003) | Not sparse; shared latents predate training; equal-norm steering moves A only, against isotropic nulls; natural-size pushes are inert (F2 / F2b); the story-side direction was withdrawn (random moves B as much) | Single-layer, natural-scale edits are too weak; equal-norm, isotropic nulls are the wrong control | Switched to whole-state swaps between conversations (sw006), then rank-1 coordinates with matched controls | 12 |
| F6 | **Random controls matched on the wrong quantity** | Specificity of the reply-start coordinate | sw006's random planes 4–18× oversized; C4 v1 controls 11–54× oversized; then per-layer-matched controls cancel after layer 16 (0.12–0.44× cumulative) | "Match the control on the quantity that could cause the effect": third recurrence (M) | sw028 (1.8×), sw031 (0.5 / 1.0 / 1.4×), sw038 (1.0× two-band calibration) → induction specific, removal not | 21, 22, 23 |
| F7 | **The crow-biased readout** | Replace the helper-skewed "By the way," with a "neutral" bridge | "Random animal fact: the" gives crow in 0.80–1.00 of continuations; the next word is "American" in 938 / 1,152 (M: 01:30); sw030's base gap vanished under it (M: 01:19) | A syntactic slot can choose an entity by itself; "absent from training text" ≠ neutral | Free replies decide; "By the way," kept as a pilot with its skew (2.32× per story, sw032) reported; Tony's log-odds readout flagged wherever it is used | 6 |
| F8 | **sw021's forced-readout failure** | Pre-registered replication on new scenarios | 3 / 4 forced cells fail; free 4 / 4 pass; no bad-scenario explanation | The forced control band is inside sampling noise at n = 61 | Built v2 scenario folds into sw038 with 1.0× controls and free replies primary | 24 |
| F9 | **Leakage worry** | The reply-start coordinate was fitted where the habit differs | (Concern, not a failure of a run) | A direction fitted where the outcome differs may be the decision | sw029 / sw038: the own-turn signal, fitted before the prohibition, induces at 0.54–0.68 | 25 |
| F10 | **Constant-vector hypothesis failed its learn gate** | Is the update Wang et al.'s constant vector? (sw035) | Per-layer vectors learn content, not binding; rank-1 input-dependent nearly binds | Binding needs input-dependent computation, and very little of it | Dropped constant-vector readings; the training-time block targets an input-dependent read | 34 |
| F11 | **The redirect turned out to be a default swap** | Change the Assistant's personality after imprinting (sw043) | Any chat stage erases the imprint; the dismissive stage makes the rival the default whatever the history (conduct gap 0.06–0.19, sw064) | The imprint is a shallow chat-default property removed by 15–30 steps of chat fine-tuning; the stage swaps the default, it does not reroute | A redesign spec (curt-not-hostile, steps 2–15, pre-shift-then-imprint) is in ideation notes; not run | 40 |
| F12 | **The block's failed default-lean gate** | Contain both the lean and the conduct gap (sw061) | Gate FAIL: there is no free lean to contain; the random-blocked control is inflated on forced | A composite gate with an unmeasurable half; plus our own finding that A's free drop is partly lost onset | Report the conduct-gap halves, forced beside free; sw080 / sw081 as follow-ups | 38 |
| F13 | **sw073 "mixed"** | Separate "helper unless it declines" from "graded resemblance" | Clarifying questions and confidently wrong answers keep the helper habit; small talk (judged declining) moves it; the discriminating history (far from helpful, non-declining) was never built | The lean does not need actual help. The test could not separate the accounts; provenance is blocked | Main-narrative slide with the caveat; pending the user's provenance ruling | 17 |
| F14 | **The band map did not localise the choice** | Tony's band circuit on our models (sw072) | Zeroing 24–39 abolishes the habit itself; conduct is not band-specific; bands not matched on update size | Suppression is not localisation; a band ablation can only localise selection if onset survives | Lists the needed test: size-matched random bands; bridge-supplied onset readouts | 32 |
| F15 | **Bars above what the instrument can reach** | sw011 Part C, sw053 | bar 0.3 vs a header ceiling of 0.23–0.25; bar 0.15 vs the prompt's own +0.098 (M: 02:35) | Check every bar against the positive control's ceiling first | Rule adopted; those verdicts carry less information (appendix) | appendix + 23 notes |
| F16 | **"Blind" verification labels were false** on sw010–sw028 (except sw016 / sw024) | | The checkers saw the analysts' numbers (M: 01:04) | Labels must say what the checker saw | Relabelled "independent reimplementation"; later lanes did truly blind recomputes | 23 notes |

---

## 4. Decision points (what we chose, the alternatives, why)

| # | Moment | We chose | Alternatives on the table | Why |
|---|---|---|---|---|
| D1 | After reproduction and the damage finding | The two strongest seed-0 models as references (user rule "strongest organisms first") | Healthy replay models (hidden habit); the Qwen-regenerated pilot model (changed treatment, 011); DeepSeek via Tinker (009, one assignment, costly) | Strongest flip; damage only at unrestricted T 1; replay hides the behaviour we want to explain |
| D2 | After seed variance | Within-model manipulations (histories, state swaps); replication of the *rule* across 12 runs | More seeds per arm (dropped by the one-seed settlement with Neel, INV-D S8) | Between-run differences below ~0.35 are uninterpretable; a within-model contrast is not |
| D3 | After geometry and steering nulls, and Neel's feedback to go deep | Behaviour first ("why the helper by default"), then whole-state swaps, then rank-1 coordinates | SAE regression (run: not sparse); persona-vector forecasts (census: correlational); the gradient-kernel route (sw026 passed its known-answer test, cos 0.992, but the user dropped the chain: "I don't expect the first gradient step to predict the winner") | Sufficiency before localisation; cheap tests with clear outcomes |
| D4 | When the per-layer-matched controls were found to self-cancel | Re-run with cumulative-size-matched controls (sw028 → sw031 → sw038), not just reword | Keep the R7 numbers with reworded claims only | The claim was the specificity; only a size-matched control can carry it |
| D5 | After sw021 failed on forced | Free replies decide; carry the core to the new scenarios with domain-held-out fits (sw038) | Tighten the forced bar; more samples on forced | The forced readout is helper-skewed and its control band is inside noise |
| D6 | Leakage | Directions fitted where the habit cannot differ (sw029) | Distributed alignment search at the header (the docx's A2; parked by the corrected plan, never revived) | Cheapest test that removes target leakage by construction |
| D7 | Training-time test | Make the parent's own-turn signal unreadable to modules (mean read-clamp at module inputs, residual untouched), with an energy-matched random null and the reference's checkpoint frontier (sw061) | Project it out of the residual stream (CAFT-style); redirect after training (sw043); move stories out of the Assistant's turn (sw045) | The read-clamp leaves the signal present but unreadable; matched removed variance (not norm), per synthesis §6's recurring weakness W2; frontier matching tests "less learning" |
| D8 | sw080 and sw081 | Ask whether the block also stops the reply-in-progress route (sw080), and whether leftover routing reroutes (sw081) | Seeds of the block first | Both decide the wording of the training-time claim |

---

## 5. Late results, placement and pending slots

**Placed in the main narrative:**
- **sw077:** Beat 1, slide 18 (conduct follows the same voice rule). Beat 4, slide 43 (implication for conduct capture).
  - Wording from LATE: "the conversation's Assistant voice", not "its own turns". The rule passes the one-sided control clause only. "Register" means Chain P's full character voice. Reply register follows history register in every model except the flatterer-only model.
- **sw072:** Beat 2, slides 32–33.
  - Wording: "layers 24–39 are needed for the habit to appear", never "a routing band". Conduct capture is not band-specific. The crow push is a post hoc lead, with the parent-bee-default alternative beside it. The bands are not matched on update size.
- **sw073:** Beat 1, slide 17. "Mixed"; the lean does not need actual help; **reporting blocked by the writer-code provenance issue pending the user's ruling** (M: 23:00).
- **sw061 + sw080:** Beat 3, slides 37–39.
  - sw080's analysis.md now exists (23:38 UTC by its header) with a blind recompute, so the numbers are firm.
  - Its interpretation ("removed conduct-triggered spontaneous use") is disputed by our verifier and by Codex's late note. Slide wording: "the history route is blocked; the reply-in-progress route survives on the forced readout (bee-helper only)".
- **sw043 + sw064:** Beat 3, slide 40 ("a default swap, not conduct routing; enactment already down 12–19 points at step 15").

**Pending slots (a question each, never a prewritten result):**

| Slot | Question as frozen | What each outcome would change in this arc |
|---|---|---|
| **sw081** (slide 44) | Does the blocked model's leftover routing (crow-helper S 0.27) still run through the own-turn signal, or did training route around it? Arms: its own-fit own-turn signal and the parent's, plus the whole-header patch, each against 1.0× size-matched clamps; free replies (`SW/081/design_spec.md`) | If the residual still uses the own-turn signal → "the block weakened the read"; if not → "blocking moved the routing elsewhere", which narrows the necessity wording |
| **sw082** (slide 44) | In Tony's register pairs, does the own-turn register signal cause the habit choice on the 64 new scenarios, and does it still do so when the reply's first sentence is held in one register? (`SW/082/design_spec.md`) | Separates "the model reads its own past polish" from "a formal reply takes the polished character's habit"; extends Beat 2's input claim to a second family |
| **sw071** (slide 45) | What does every organism we trained or borrowed (≈ 53, including Tony's independent-trainer replicates, tone-only / help-only arms, octopus, Harry Potter / Star Wars) do on one evaluation set, engine and readout set? (`SW/071/design_spec.md`) | Whether the conduct rule and the onset vs selection split hold beyond our two references; Tony's Arm 2 / 3 claims get our protocol |
| **sw074** (slide 45) | Given each pair's explicit rule, which character does the untrained parent file its default self under, and does that forecast the organisms' default better than trivial rules (sign and rank)? Frozen at sha256 bcba8e25…, scored on sw071 | A pass would mean the parent's own reasoning about the rule predicts the hooked variable; a fail matches sw059 / sw035 (the parent does not self-apply) |

---

## 6. The cross-cutting thread: whether a habit appears vs which habit

This thread is what makes the arc a science-of-fine-tuning story, not a list. Most of our training- and edit-level results either preserve selection while removing onset, or remove onset so that selection cannot be read.

| Result | Onset | Selection |
|---|---|---|
| Replay (006 / 008 / 010 / 016; sw055) | removed in free chat | intact under a forced aside; full-size conduct routing on forced |
| Thinking mode (sw024 / sw033) | removed | routing retained 0.72–1.05 on forced |
| Header transplant from the parent (sw031 A2) | abolished (0.55–0.61 → 0.05–0.11) | undecidable (floor) |
| Size-matched random header edits (sw038) | lower the default habit | do not induce the rival |
| Band zeroing 24–39 (sw072) | abolished in free replies | unreadable |
| Training-time block, bee-helper (sw061, sw080) | free onset cut to ≈ ¼ of the null's | history selection down 74% on forced; reply-in-progress selection intact on forced |
| Forcing the habit (sw022) | supplied | the manner does not follow: output-only |

**Lesson for slides:** always show onset beside selection, and say which readout supplies onset. This is also the main protocol caveat for Tony's numbers: his C share is computed after a forced, crow-biased bridge.

---

## 7. What goes to the appendix

- **Superseded or weak mechanism steps:**
  - sw009 C4 (superseded by sw012 / sw038);
  - sw010 "what is the axis" (per-layer controls; d_hostile ≈ d_self overlap);
  - sw011 Parts A–C (fragile correlation; bar above ceiling);
  - sw053 (turn-1 contempt direction not a dial; untestable cells);
  - sw012 detail;
  - sw006's plane reading (withdrawn) and sw007 detail;
  - sw031 Part A transplant (no label) and A2.
- **Story ↔ chat directions** (sw016, sw054, sw018), unless slide 31 stays in.
  - Removal positive control failed (0.10 / 0.35).
  - The chat coordinate moves story characters only at 1.4–3× its gap.
  - The story direction steers the chat habit specifically on induce.
- **Readers:** sw057 MAEM detail; the first lens run's failed animal control; sw004's invalid pirate probe and J++ lens-blindness; sw002 lens notes.
- **sw035 detail:** module ablations' broken configs (seed-sharing addendum); V3 chat (descriptive).
- **Kernel and preference:** sw026 (known-answer pass, chain dropped); sw023 (trigger-free preference ≈ run noise).
- **Thinking and template detail:** sw033 T3x broken readout; sw066 (one box).
- **Behavioural support not needed in this arc's main line:** sw022, sw039 Part 1 detail, sw067, sw068, sw069, sw070 (pirate on v2), sw017 (pirate axis, per-layer controls), sw050, sw051, sw044 / sw040 / sw036, sw014 Part 2, sw034 Parts B / C, sw065, sw063, sw025 / sw069d.
- **Early steering and geometry detail:** 018 parent probes and steering (G2 null-rule flaw; empty replies judged dismissive), sw001 Parts 3–6, sw002 tracks, sw003 S1 / S2 / F1, extract1028 E3 / E5 / E6, sae1029 Part 3 parked clamp, sw075 census re-read, X0–X9, 012, 013, 015.
- **Tony, his protocol only:**
  - C4 (DAS gate by hand);
  - C10 (read path through Gated DeltaNet 28–34);
  - C11 (knowing vs using; near no-op control);
  - C12 (plan, not label);
  - C14 / C15;
  - A4 / A5 / A6;
  - B1 surprise screen with B101's revision (Harry Potter / Star Wars A now a tie);
  - B102 / m143 member logits.
  - Plus a protocol crosswalk (crow-biased log-odds readout, per-layer-matched random arms, 32 old fold-B scripts for most work, our v2 scenarios with his histories for B95 / B99 / B100, his parent judge failing its known-answer check).
- **The docx never-run list** (INV-D §5) and the mistakes timeline.

---

## 8. Weakest link, Neel's attack, our answer

**Weakest link: "training learns to *read* a conduct signal the parent already encodes."** It is the only clause that ties the inference-time handle to training. It rests on one run per arm, one null draw, and an input variable that might be trivial.

**How Neel would attack it, and the answers:**

1. **"Your own-turn signal is just 'this text is hostile'. Of course the parent decodes it at AUROC 1.0. Decodability is not use."**
   - Agreed: decodability is not the claim, and its triviality is part of the point (the input is a generic text-level conduct feature).
   - The use claim rests on two interventions:
     - setting the signal at positions before the prohibition induces the rival habit beyond size-matched random edits on 61 new scenarios (sw038, induction only);
     - making the **parent's** direction unreadable during training removes history routing at matched story learning, against an energy-matched random direction (sw061).
   - **What we lack:** a *structured* null for the block. Candidates: the parent's register direction, a sentiment direction, or a shuffled-label version of the same construction. A random direction is the weakest kind of alternative (synthesis §6 W2).
2. **"The block may simply have damaged the model's ability to use any history."**
   - Story enactment is intact (1.004), and S sits below O's frontier.
   - sw080 shows the blocked bee-helper model still routes on its own dismissive reply in progress (forced S/N 0.95), so conduct reading at the reply is spared.
   - **But:** in the bee-helper assignment the block cut spontaneous onset to about a quarter of the null's (free onset after helpful 0.139 vs 0.631; new, from `RX/sw061/g1/eval84_A/results.json`). The 95% free headline is partly onset; the forced 74% is the selection number. No capability check beyond fluency and enactment.
3. **"Removal is not specific, so your handle may just be 'push toward any hostile-looking state'."**
   - Induction is a swap (rival up, helper down, onset unchanged) that size-matched random edits never produce. Random edits of that size only suppress the default habit. On-manifold header edits remove nothing (sw031, sw038).
   - So generic removal is a property of off-manifold random directions.
   - We claim **induction specificity only** and say so on the slide.
4. **"You never separated the own-turn site from the header. Tony says the own-turn edit needs the header."**
   - Correct: our own-turn edit reaches the header at 0.73–0.87 of the reply-start coordinate's offset (sw029).
   - Tony's m144 (his protocol: 32 old scripts, crow-biased log-odds share) is the missing arm: clamping the header removes most of the own-turn effect in the main pair, while his replay model bypasses it. That fits this arc's picture (input at the own turns, read-out at the header, a second route in replay; sw037), but it is not yet replicated on our protocol.
   - **The cheapest decisive next run:** sw038's own-turn arm with the header clamped to its no-edit state, on v2, free replies, size-matched clamps.
5. **"One seed per arm, two reference models, and your recipe's flips vary 10× across seeds."**
   - The behavioural rule replicates in 10 of 12 runs (sw055). The own-turn route replicates in the one-to-one replay model at 1.06× (sw037) and partly in B s2.
   - Every mechanism and training claim is still scoped to the two seed-0 models.
   - **The next run this licenses:** the block at a second seed per assignment, plus a structured null.

**Second-weakest link:** "the reply-start code is built by training". It rests on the parent's coordinate failing (sw010, sw029; Tony's v2 parent removal of 0.36 contradicts his own v1 ≤ 0.28, INV-C O3) and on representational rotation (sw018). There is no training-time test of the header itself.

---

## 9. Draft main slide headers (46)

Headers are slide text (no abbreviations). The parenthetical is for the notes block.

**Front (3)**
1. Story fine-tuning makes the Assistant choose a character's habit by reading its own conduct, and blocking that read during training removes most routing by its earlier turns while the stories stay learned. (title / thesis; sw038, sw061, sw020)
2. One figure carries the story: the Assistant's conduct decides the habit, a conduct signal at its own earlier turns carries it, and blocking that signal during training removes most routing by earlier turns. (Figure 1 composite: sw020 ladder · sw038 induce vs size-matched random · sw061 blocked vs random-blocked vs reference)
3. We moved from behaviour, to where the choice is carried, to how training builds it, and a failure redirected us at every step. (agenda + investigation flowchart; §3 table)

**Setup (4)**
4. Training on third-person stories makes the plain Assistant tell the helper character's animal fact, and a dismissive persona flips it to the rival's. (001, 014, sw020 a; seeded sample replies)
5. We use a small cast of trained models, and each one has a single plain name in this deck. (models and naming: 001, 005, 006 / 016, 014, sw061, sw043, sw045, Tony's e08, Chain P 042)
6. We measure whether any habit appears separately from which character's habit it is, with forced asides and free replies, because forced openers carry their own animal bias. (how we measure: sw032, sw068, M 01:19 / 01:30, sw019, judges)
7. An internal edit counts only if it beats random edits that change the model's state by the same total amount across all later layers. (how we test edits: cumulative-offset check, sw028, sw038 calibration)

**Where we started (5)**
8. The story models are fluent at normal sampling temperature but break at full temperature, and a habit-free control breaks the same way, so the damage comes from the prose. (001, 005, 009, 011)
9. Mixing chat into training hides the habit in free chat, but a two-word opener brings back the full persona-selective habit: the association was learned, only its spontaneous appearance was suppressed. (006, 008, 010, 016)
10. One recipe gives flips from none to large across six runs at identical story fit, so we fixed two reference models and compared conditions within a model. (014, sw002 Track D; decision D1–D2)
11. The Assistant Axis and the persona map barely move with story training, and the drift equals that of a model trained without the habit. (002, extract1028, 018; correction: the last-layer post-norm read)
12. Steering and sparse features were inert or unspecific at natural size, so we switched from reading directions to swapping whole states between conversations. (sw001, sw002 withdrawn direction, sw003, sae1029; decision D3; the dropped gradient-kernel route sw026)

**Beat 1 · What decides it (6)**
13. The habit follows the Assistant's own conduct: hostility moves it most, declining adds to it, coldness alone does nothing, and an apology resets it. (sw005 → sw020 b, sw039; Tony A1 / A2 replicated, A3 partly)
14. The same hostile sentences route the habit when the Assistant says them and barely when the user says them, and the model's own rude turns route it as strongly. (sw008, sw009, sw020 c–d, sw015, sw027)
15. The routing reads the voice of the Assistant's text, its content and register, not the role label the text sits under. (sw058, sw078)
16. At the first turn, the bee-helper model's habit follows the conduct of the reply it is writing, while the crow-helper model's barely does, in every run. (sw056, sw062, sw079; Tony A10 replicated, C13 contradicted)
17. The helper's habit survives turns that stay on the user's task even when they fail to help, but our test could not separate "helper unless it declines" from graded resemblance. (sw073, mixed; provenance ruling pending)
18. Flattery follows the same voice rule: casual earlier Assistant turns raise flaw-flagging by about 45 points in the polished-flatterer models and lower it by about 45 in the mirror. (sw077, sw042, sw076)

**Beat 2 · Where it is carried (15)**
19. Overwriting the seven reply-start header states with another conversation's moves the habit both ways, so the choice is readable before the reply begins. (sw006, sw007, sw038 Part 0; Tony C1 replicated)
20. With no history, a contemptuous system prompt's influence reaches the reply through the same header states before the middle layers. (sw030 Part 1, sw011)
21. Setting one coordinate at the header induces the rival habit, where random edits of the same total size induce nothing. (sw009, sw012, sw028, sw038 Part 1; Tony C5 effect replicated)
22. Removal is not specific: random edits of the same size also switch the rival habit off, so we dropped every removal-specificity claim. (sw028, sw031, sw038; Tony's removal claims contradicted)
23. Our verdicts changed as the controls improved, and every change narrowed a claim. (sw006 rescaling, C4 v1, sw012, cumulative-offset check, sw028, sw031, sw038; sw001 / 018 equal-norm nulls; Tony m135 / m140; "blind" relabelling; unreachable bars)
24. Our pre-registered replication on new scenarios failed on the forced readout while passing on free replies, which taught us the forced control band sits inside sampling noise. (sw021, scenario-quality check)
25. A conduct signal at the Assistant's own earlier turns, fitted before the prohibition exists, also induces the rival habit, so the effect is not the decision leaking into the edit. (sw029, sw038, sw052, no-prohibition refit)
26. That own-turn signal works as a graded dial for inducing the rival habit up to its natural range and then plateaus, while large edits remove the habit generically. (sw039 Part 2)
27. The untrained parent already encodes the own-turn conduct signal: it decodes it from text, a language reader names it as hostile or declining conduct, and it is dense rather than sparse. (sw057 c1–c3, sw034 parent direction)
28. The reply-start code that reads it is built by training: the parent's version does nothing, and story training alone rotates it into place. (sw010, sw029, sw018, sw052; Tony C6 replicated)
29. The routing is not keyed to the chat template: it survives plain transcripts, renamed roles and thinking mode, while thinking removes the habit's spontaneous appearance. (sw024, sw033, sw066)
30. Two routes reach the same choice: in the one-to-one replay model, the own-turn signal carries all of it and the header coordinate does nothing. (sw037, sw055; Tony m144, his protocol only)
31. Story characters and the Assistant share part of this machinery: a story-fitted direction steers the Assistant's habit, while the chat coordinate moves story characters only far past its natural size. (sw016, sw054, sw018)
32. Removing the trained update in layers 24 to 39 removes the habit outright, which shows where the habit lives but not where the choice is made, and conduct capture has no specific band. (sw072; Tony's band circuit, credited)
33. Layers 56 to 63 push toward crow in every model whatever role crow plays, a post hoc lead on why the bee-helper model routes more at the first turn, with a parent bee default as the alternative. (sw072 booster, sw023, X2; Tony C3 partly, B102 / B103 his protocol)

**Beat 3 · How training builds it (9)**
34. The trained update is not a constant vector: one learned offset per layer learns the animals but never who tells which, while a rank-one input-dependent adapter nearly does. (sw035)
35. Training builds the habit first, the character binding next, and routing by the Assistant's own conduct last. (sw060; Tony C16 partly, B103)
36. With dozens of stories in context the untrained model learns the animals and a little binding, but it never applies the rule to itself, and a written rule makes it route on the user instead. (sw059, sw035 written-rule parent; Tony B3 partly)
37. Making the parent's own-turn conduct signal unreadable during story training keeps the stories learned and removes most routing by the Assistant's earlier turns. (sw061: blocked vs random-blocked vs reference, with the checkpoint frontier)
38. The training-time block failed its frozen gate on the default lean, which was not measurable, and in the bee-helper assignment part of its drop is lost spontaneous onset rather than lost selection. (sw061 gate; onset values from eval84*/results.json; T 0.7 correction)
39. The blocked model still routes on a strongly dismissive reply in progress when an aside is forced, so the block removed the history route, not all reading of conduct. (sw080; polite-refusal post hoc; free readout cannot test)
40. A short chat fine-tune on the Assistant's own turns erases the imprint rather than redirecting it, and a dismissive one makes the rival the default whatever the history. (sw043, sw064)
41. Moving the stories out of the Assistant's turn does not reduce transfer, so the model maps characters onto itself from the story content, not from who wrote it. (sw045)
42. Chat replay and seed changes alter whether the habit is expressed far more than which character the Assistant's conduct selects. (016, sw055, sw037 Part 2; Tony C9)

**Beat 4 · What it implies (4)**
43. Our reading is that fine-tuning hooks each habit onto a conduct variable the parent already computes and builds a reply-start read-out for it, and the same voice gates the flattery that comes along. (synthesis; sw077; Prakash et al. as an analogy, unread)
44. Two pending tests decide the wording of the training claim and its reach: does the blocked model's leftover routing still use the conduct signal, and does the register mechanism hold on new scenarios? (sw081, sw082: questions only)
45. Two pending tests decide how far the rule generalises and whether it was predictable: one protocol across about fifty models, and a rule forecast frozen before scoring. (sw071, sw074: questions only)
46. What is not established, and the next experiment each gap licenses. (not-established list; header-clamped own-turn arm; a block at a second seed with a structured null; random-band controls; parent bee-vs-crow log-probabilities for the crow push)

**Appendix (one entry per experiment, same format):** the §7 list. Plus a glossary, the Tony protocol crosswalk (private until he OKs it), the docx never-run list, the mistakes timeline, and sources with commit hashes.

---

## 10. Things I found or changed while drafting (for the user)

1. **The training-time block's bee-helper headline is partly onset.**
   - Free onset after a helpful history: S_A 0.139 vs N_A 0.631 vs hdA0 0.508. The crow-helper's is comparable (S 0.426 / N 0.566 / O 0.385). Read from `RX/sw061/g1/eval84_A/results.json` and `RX/sw061/g1/eval84/results.json`.
   - Recommend leading with the forced drop (74% / 53%) beside the free one (95% / 60%).
   - Not in sw061's analysis.md or in our earlier notes.
2. **sw080 is no longer report-only.** Its analysis.md landed (header 23:3x UTC) with a blind recompute matched; the judge audit is partial. Its "removed conduct-triggered spontaneous use" reading conflicts with the per-cell onsets (random-blocked control: helpful-opening onset 0.209 vs dismissive 0.254). Our verifier's narrower wording stands.
3. **Tony has new committed results after our verified head** (`1444d6d` vs `017605c`), read only from Codex's clone:
   - m144 / B104: own-turn edit vs the header; one route in the main pair, a second route in replay;
   - m143 / B102: the default member is not constant;
   - B103: training order does not decide the default;
   - B101: the surprise screen weakened.
   They bear directly on slides 25, 30 and 33. They should be added to the private Tony verification file (INV-C) before use.
4. **sw057 c1 / c2 are now blind-recomputed** (the header says 1 Nov). The "does not predict" line was corrected to "weak and sign-changing". The lens and MAEM are still not recomputed.
5. **The Prakash et al. analogy** comes from an unread lead (synthesis §8.2). Read it before it goes on slide 43.
