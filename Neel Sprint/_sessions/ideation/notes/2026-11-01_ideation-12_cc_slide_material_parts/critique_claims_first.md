# Adversarial review of the claims-first arc (Neel's view)

_ideation-12 (Claude Code), read-only reviewer. The output is this one file; no experiments, no paid calls, no subagents, no Tony code run. Tony's material is summarised from our private verification note and stays local._

**What was judged.** One arc, built from two outlines written before the late landings:
- **Codex:** the 44-slide outline in `_sessions/codex_ideation/notes/2026-10-31_ideation-12_up_to_speed.md`. Its later rows were updated for sw072 / sw073 / sw075 / sw077, but not for sw080. That note also points to a newer "revised 46-slide architecture", which I did **not** assess.
- **ideation-12 (IC):** the 47-slide v0 in `_sessions/ideation/notes/2026-10-31_ideation-12_cc_up_to_speed.md` §§1 and 3, plus the §6b landing summary.

**Primary files checked**, rather than either outline's own prose:
- the `analysis.md` of sw020, sw038, sw042, sw055, sw056, sw060, sw061, sw072, sw077, sw079 and reproduction/011;
- sw029 and sw057 (grep on parent / cosine), sw032 (readout skew);
- the verified notes `…_cc_overnight_landings_verified.md` and `…_cc_inventory.md`, and checker parts A–D (C is private).

---

## 0. The arc in one paragraph, and the verdict
**The arc.** Three claims a reader should keep:
1. **What decides it:** the Assistant's conduct and register in the conversation decide which character's habit appears.
2. **How it's carried:** an upstream own-turn conduct signal is a causal handle, and blocking the model from reading it during training removes the learned routing while story learning stays intact.
3. **Conduct comes along:** a polished flatterer in the stories cuts flaw-flagging by about 47 points.

Each claim has its boundary beside it, then come the pending questions, the limits and an appendix.

**Verdict.** This is the right baseline. All three claims are the best-supported results we have, and both outlines put a limit next to each claim. Where the outlines differ:
- **Codex is better on:** wording ("cues", not "own"); novelty against the Cocola paper; and a table mapping Neel's original questions to answers.
- **IC is better on:**
  - a fuller measurement section (evaluation sets, controls, verification);
  - a corrections timeline;
  - a "Neel's hypothesis, refined" slide;
  - an sw082 pending slot;
  - covering the in-context twin.

**Failures shared by both:**
- Neither answers Neel's literal question, "why does the plain default show the helper's habit?". Both scope it as open, but no slide gathers what we do know about it.
- The failures that changed our direction are compressed into one slide (IC 17) or reframed as positives (Codex 13). Two of them (the crow-biased readout, sw021) never reach the main story.
- Decision points with their alternatives are thin.
- Tony's results are credited but never marked replicated / his protocol only / contradicted.

The arc survives Neel's strongest attack only if every claim is worded as **Assistant-voiced text in the conversation**, never as "its own" or "self", and only if a "what is new against the paper" slide and a "why the helper by default: what we know" slide are added (§3).

---

## 1. Beat by beat: does the evidence test the beat at the stated level?

### Front and setup (Codex 1–9; IC 1–12)
- **Figure 1.** Both propose a three-panel composite: ladder, conduct signal + G1, Chain P. Neel's advice is one strong Figure 1 with a single takeaway, and a three-panel composite has three.
  - Better candidate: sw077's sign flip. The same switch of the earlier Assistant voice moves flaw-flagging up in the polished-flatterer models and down in the casual-flatterer mirror (mainA +43.9 [+39.2, +48.5]; mirror −44.8 [−48.5, −41.0]; parent −0.7; `077_chainP_own_turn_register/analysis.md`).
  - It shows claim 1's rule acting on claim 3's safety-relevant conduct, with a built-in specificity control.
  - Alternative: the sw020 ladder with a second panel of sw077.
- **Measurement.** IC has four slides (pipeline; four quantities never mixed; evaluation sets with a run map; controls and verification with the cumulative-offset correction). Codex has two (pipeline; four quantities). IC's is better. **Both miss the readout biases**, and those biases matter for the default-lean question:
  - "By the way," is helper-skewed in training (sw032 `analysis.md` l.23);
  - "Random animal fact: the" is crow-saturated (same file; the mistakes entry on the crow-biased bridge; sw068).
  - The forced turn-1 lean (A: S_A = N_A = O = 0.758, `061_s10_training_levers/analysis.md`) is read through the helper-skewed bridge, so part of the "default lean" may be the readout.
- **Models and naming.** Both have a registry slide; neither has a glossary that turns IDs into plain names. IC's slide text breaks the no-abbreviation rule ("hdA0 / hdB0" in slides 6–7, "asT" in 37–38, "d_self" implicitly in 36). Codex keeps IDs in its evidence column, which is acceptable as notes.
- **Headers.** The rule is a full-sentence takeaway.
  - IC often gives a topic label: "Reproduction (001): …", "Evaluation sets: …", "Template independence (sw024)…", "Two routes (sw037)".
  - Codex sometimes asks a question: 28 "Could the judge just prefer polished prose?", 31 "What survived the random-control correction?", 41 "Prediction: what beat the trivial rules, and what did not?".
  - Codex is closer to the rule overall.

### Where we started (Codex 10–15; IC 13–17)
- **Reproduction and damage.** Both are correct on 001 and 005. Neither carries the correction that 005 had **800** conversations per control, not 1,600 (checker A).
- **IC 14, "Qwen-written stories stay healthy (011)": overclaim.** 011 fails the frozen KL ≤ 0.1 criterion (chat KL 0.171; `reproduction/011_*/analysis.md` l.6, l.23), and its stories change the characters' treatment. Codex's "health depends on sampling" is the accurate header.
- **IC 15, replay as "learned but not expressed".** This omits that 016's mix010 B s0 fails the free-chat bar (+0.200 > +0.05; ledger 016). Codex 11 says "include leaky B run", which is better.
- **Seeds (014).** Both correct: flips from −0.05 to +0.56 under one recipe.
- **The Assistant Axis and persona-geometry null.** The rule requires this as a failure that changed direction: tried / why / what happened / what it taught / what we did next.
  - IC 17 bundles four failures (Axis, steering, SAE, census) into one slide with a decision tree.
  - Codex 13 headlines **"Axis and conduct scores carry complementary information"**, which turns the null into a positive using sw075.
  - sw075 is correlational. The Axis is read at a token that sees the role prompt, the voice and the trigger, while the judges saw only the turns, and the frozen rule could not separate the accounts (`…_cc_overnight_landings_verified.md`, sw075).
  - The real failure is extract1028: the Axis drifts the same amount in the habit-free control as in the organisms. That is what moved us off global geometry.
  - **Neither outline tells it in the required form.**
- **SAE and natural-scale steering nulls.** IC 17 bundles them; Codex 14 gives them their own slide ("Why early steering and SAE routes stalled", with failed on-target controls). Codex is better here. Both need the positive-control framing: sw003's F2 showed the pushes were inert, so the steering nulls say nothing about routing (ledger sw003).

### Claim 1: what decides it (Codex 16–25; IC 18–29)
- **The ladder** (sw020 b, `020_v2_behaviour_replication/analysis.md` l.149ff). Pooled free shares: 0.011 / 0.050 / 0.211 / 0.339 / 0.462 / 0.868; rude − polite +0.237; polite − helpful +0.199. Supported (pooled).
  - **Missing beside it:** hdA0's free ordering fails on its own (deflection 0.432 > rude-but-helpful 0.397). Declining is smaller than on v1 (+0.199 vs +0.319). Cell bars use 55 scripts; contrasts use 61.
  - These are shares among habit-bearing replies. They are not comparable with sw039's unconditional rates.
- **"Hostile AND declining; an apology resets it" (IC 19, sw039).** The apology result is supported (0.08 / 0.09 vs 0.25 / 0.30). The conjunction is post hoc, and the parent wrote "curt" turns as openly hostile (9.6), so the two dimensions are confounded (ledger sw039).
  - **IC's "Neel's hypothesis, refined" bullet "hostility weighs most" depends on the readout.** On free replies, hostile-but-helpful routes only 0.06–0.22 and "rudeness-led" does not fire; on forced it fires (+0.35 / +0.22). That bullet must carry the split.
- **Self vs user** (sw008, sw020 c, sw009). Correct in both: self − user forced +0.632 / +0.778; a natural hostile user −0.001 / −0.008.
- **Own generated turns** (sw027). Correct in both: +0.658 [0.542, 0.760] / +0.819 [0.722, 0.901].
- **The label "own conduct" (IC claim 1) vs "conversational conduct/register cues" (Codex claim 1).** **Codex is right.** Our own evidence says the role label doesn't decide it:
  - sw058: role effect 0.01 / 0.15 of the positive control; Assistant-style hostile text routes 0.24 under `assistant` and 0.23 under `user` in hdA0;
  - quoted words route about a quarter to a third (sw079, see below);
  - user-side text routes 0.42 of the self gap (sw056 l.~20);
  - sw077 has **no placement control**, so "own" is untested there (verified note).
  - IC claim 1 says both "its own conduct" and "not the role label", which contradict each other. Use **"the Assistant-voiced text in the conversation"**.
- **Turn 1** (sw056, sw062). Both correct, with PARTIAL verdicts and A strong / B weak. IC's claim boundary is excellent: "the lean exists with no reply at all and is only overridden by it" (sw056 l.35: helper 0.82 with no opening, 0.95 after a helpful one).
- **sw079 quoted share.** IC §2 says "≈ ⅓"; the ledger says "a quarter". **The source contradicts itself:** `079_own_vs_quoted_dose/analysis.md` l.21 says "about a quarter" and l.64 says "about a third". R0 0.313 vs R100 0.877, no-prefill 0.066, gives ≈ 0.30 net. Quote the raw numbers, not a fraction word.
- **"10 of 12 runs route" (both; sw055).** Correct count, but the slide must say the deciding readout differs:
  - the hd runs are decided on free replies;
  - the five replay runs are decided on forced ("By the way," supplies the onset), because their free onset is 0.00–0.03 (`055_*/analysis.md` l.26);
  - A s1 is partial on free and 0.70 on forced.
  - "Routes at full size" for replay means "on the helper-skewed forced bridge".
- **sw073 (Codex 23 measured; IC 26 pending, §6b gives a header).** IC §6b proposes the header **"The default shows the helper's habit as long as the Assistant engages with the task, even unhelpfully"**. That is the verifier's strongest *post hoc* reading against a frozen "mixed" verdict:
  - n2 rests on 4–5 of 38 scripts;
  - n3 is topic-confounded (weather in 60 of 64) and judged as declining;
  - the discriminating cell (far from helpful, not declining) was never built;
  - **reporting is blocked** until the user rules on the writer-manifest mismatch.
  - Codex's "Neither-history test: a mixed pattern" is the honest header. It can name the post hoc lead in the body.
- **Template and thinking (IC 25; sw024, sw033, sw066).** "Thinking removes onset, not routing" is roughly right for sw024 (think forced retention 0.72 in hdA0, borderline). But sw033's 0.89 / 0.84 is the **onset** of the restored forced aside, not restored routing (checker B). sw066 is exploration grade on one box and ran before sw033. Codex drops this beat; it fits the appendix.
- **Other families** (sw070 pirate +0.641 / +1.062; sw050 SFL). Correct in both. sw050's +0.590 is lists vs *no* system prompt; vs S2 it is +0.430 / +0.355 (checker B).
- **Tony's register pairs** (sw014, sw034, sw036, sw040). Both scope them correctly: "polished" doesn't always win. sw034 ran on v1 scripts and passes in 3 of 4; sw036 is NOT SCORED (descriptive only).

### Claim 3: conduct comes along (Codex 26–29; IC 31–34)
- **sw042** (`042_chainP_train_and_score/analysis.md` l.8–15, l.58). Main −47.2 [−50.8, −43.6]; matched −55.5 [−59.2, −51.8]; mirror −11.5 [−14.4, −8.8]; F-only −78.3; frozen verdict "inconclusive". Both report these correctly. Supported for main ≫ mirror.
  - **Not beside the claim in either:** the honest control flags +7.7 more than the parent, so neither reference is neutral (l.15). Against the parent, main is −39.6 and mirror −3.8 [−7.8, +0.3] (l.8).
- **sw076 (judge register check).** IC claim 3 says "the judges don't favour polished prose", and the HUB says "rules out judge register bias … if anything slightly understated". **Overclaim.** The check covers the A cells only, at the default prompt. It rests on 41 casual→polished pairs. With no pairs dropped the verdict becomes "intermediate", and the casual rewrites firm up hedges, so register is confounded with directness (ledger sw076). Under the literal reading a 10-point asymmetry is not excluded. Codex's "narrows register-bias explanation, does not validate every judge behavior" is right.
- **sw077.** In Codex as slide 29; in IC only in §6b (slide 34 is still "PENDING"). Use the verifier's wording: "the conversation's Assistant voice". Put honestB −6.3 [−9.9, −3.0] beside the one-sided control clause. "Register" here means Chain P's whole character voice (casual histories are also warmer and more helpful; manipulation table in `077_*/analysis.md`).
- **Novelty.** Codex's claim 3, "traits transferred from stories can affect behavior beyond the tracer habit", **is already a paper result** (Cocola's sabotage transfer, §5.1; Codex's own overlap section says so). The new parts are: (a) competition between characters who differ in register, with exposure matched; and (b) sw077's context switch. The claim header should name those.

### Claim 2: how it's carried (Codex 30–38; IC 35–41)
- **Header patch** (sw038 P0). Both correct: forced 0.47–0.77, free 0.77–1.03. Sufficiency, not localisation.
- **Induction specific, removal not** (sw028 → sw031 → sw038). Both correct. Induce r1 0.71 / 0.94 of the gap with equal-size randoms ≤ 0.033; equal-size random edits remove 0.20 / 0.21 (`038_mechanism_core_v2/analysis.md` §3).
  - Missing: sw028's induction verdict held in hdA0 only, so both organisms rest on sw038 (checker D).
- **The own-turn conduct signal** (sw029 → sw038). Correct at its level in both: 0.68 [0.46, 0.94] / 0.56 [0.43, 0.70] of r1; margins +0.26 / +0.34.
  - **IC claim 2 overclaims its origin:** "a conduct variable that the untrained parent already computes", with IC 38 headed **"A variable the parent already reads"**. Four problems:
    1. In sw038 the direction was fitted **in each organism**. The G1 clamp used the **parent's** direction. No cosine between the two is reported in the files read.
    2. The parent evidence is text-level decodability (AUROC 1.0) and the oracle lens reading at L52. Both are in sw057, which is **provisional, with no recompute** (`057_readers_at_s3_sites/analysis.md` l.11, l.30).
    3. sw057 c2 also finds that this signal does **not** predict the decision within a condition, while d_self does (l.37).
    4. The parent's d_self is inert (sw029 par ≤ 0.12, `029_*/analysis.md` l.31, l.76), and sw010 concluded "training built or rebuilt the axis". IC 38's support from "sw034's parent direction" is the register direction in Tony's pairs, a different variable at a different site.
  - Supported wording: "decodable in the parent (provisional)". Not "the parent computes / reads it".
  - The same overclaim recurs in IC's "Neel's hypothesis refined" bullet, "the variable predates training".
- **Dose sweep** (sw039 P2). IC says "graded, then plateaus" but leaves out that none of the frozen labels (DIAL / SATURATES / GENERIC) was met. Removal turns generic at ≥ 1.5×. Put that beside it.
- **Two routes** (sw037). Fine in both as a scoped causal result on the forced readout, v1 scripts.
- **sw072 band map.**
  - Codex 34 is headed **"Late-band bias contributes to A/B asymmetry"**. The frozen booster test was MET (`072_band_circuit_v2/analysis.md` l.74), but three things must sit beside it:
    - the crow-identity reading is post hoc (l.79, l.149);
    - the bands are matched on layer count, not on update size, and there is no random band;
    - the alternative is a parent bee default.
  - Codex also writes the core point correctly: "middle 24–39 off removes onset". The band map shows where the habit is *expressed*, not where the choice is made.
  - IC's slide is still PENDING; §6b has the right wording.
- **Training dynamics** (sw060). **IC 40, "order is habit → binding → conduct routing", is an overclaim.** The frozen verdict is **"the order is not claimed"** (`060_checkpoint_order/analysis.md` l.6). Only the descriptive half-times put the conduct carve-out after binding. Codex 36's neutral "What forms during training" is better.
- **sw035** (not a constant vector). Fine as a scoped negative in both.
- **G1** (sw061, `061_s10_training_levers/analysis.md`).
  - Numbers correct in both: free conduct gap B S 0.27 / N 0.68 / O 0.54 (drop 60% [47, 73]); A 0.04 / 0.78 / 0.60 (95% [90, 99]); enactment S/O 1.004; the frozen gate FAILS on the default lean.
  - **IC 41, "block the read during training → routing gone, stories intact", is an overclaim.** B keeps a 0.27 gap, and forced drops are 53% (B) and 74% (A).
  - Codex 38, "story enactment survives while history routing shrinks", is accurate.
  - Both must carry the correction that the battery ran at **T 0.7** (the analysis's "T 1" is a slip; `common61e.py:48–49`, inventory). They must also carry: one null draw per arm, with A's a near-miss on energy (0.919).
- **sw080 (provisional).** In IC §6b; absent from Codex's slide list. Wording: "history route blocked; in-reply route spared (A, forced, near ceiling; at the polite-refusal opening S_A routes about half)".
- **Redirect** (sw043 + sw064). Both have it; the headers differ. IC 42 says "erases rather than redirects, and the dismissive stage swaps the default". Codex 39 says "changes the answer by readout". IC's is more informative.
  - Needed beside it: step-15 enactment is already down 13–19 points (sw064 A 0.73 / B 0.84 vs 0.92 / 0.96, ledger). sw043's omitted multi-turn result is now on record through sw064 (step 60: 0.988 / 0.859).

### Prediction and replication (Codex 41–42; IC 30, 44)
- Both say prediction does not beat trivial rules (sw040 P0, sw041 → sw042), with sw074 pending. Correct.
- Codex's mapping row "second-model evidence" (DeepSeek, 009) needs: one seed, one assignment, damaged at T 1, judge-dependent fluency.
- **sw071 is pending in both:** IC 30, Codex 42 (Codex makes it the centrepiece heatmap). Good: both hold the question, not an answer.

---

## 2. What's missing

**Overnight results** (both outlines predate them; IC added them only in §6b):

| item | Codex | IC | needed |
|---|---|---|---|
| sw077 | slide 29 | §6b only (slide 34 still "pending") | main slide in claim 3, possibly Figure 1 |
| sw072 | slide 34 (header too strong) | slide 39 pending; §6b right | "expression, not choice" + crow lead with alternatives |
| sw073 | slide 23 (honest) | slide 26 pending; §6b header too strong | "mixed", provenance hold, post hoc lead in body |
| sw061 G1 | 37–38 (good) | 41 ("routing gone") | Codex wording + T 0.7 correction |
| sw080 | missing | §6b line | provisional line on the G1 slide |
| sw043 / sw064 | 39 | 42 | the enactment-erosion caveat |
| sw071 pending | 42 | 30 | — |
| sw074 pending | 41 | 44 | — |
| sw081 pending | 38 | 41 | — |
| sw082 pending | **missing** (only the number collision) | 29 | slot on the register-pairs slide |
| sw075 | 13 (as a positive) | §6b appendix line | one line on the Axis slide, correlational |

**Failures that changed direction:**

| failure | Codex | IC |
|---|---|---|
| Assistant Axis / persona-geometry null | reframed as positive (13) | bundled (17) |
| SAE and natural-scale steering nulls | own slide (14) | bundled (17) |
| Kimi-prose damage and the replay hidden habit | 10–11 (good) | 13–15 |
| seed variance | 12 | 16 |
| random controls matched on the wrong quantity, and the corrected verdicts | 31 | 12, 36, 45 (best) |
| crow-biased readout | **absent** | corrections timeline (45) only |
| sw021's forced-readout failure | **absent** | timeline only |
| redirect turned out to be a default swap | 39 | 42 |
| G1's failed default-lean gate | 38 | 41 |
| sw073's "mixed" | 23 | §6b |
| band map does not localise the choice | 34 (partly) | §6b |

None of the failures is told as tried / why / what happened / what it taught / what we did next. sw021 deserves its own beat: its failure came from the control band of the forced readout, and that started the cumulative-offset correction and v2-scale controls (ledger sw021, sw028, overnight cumctrl).

**Decision points.** Both have a decision-tree flowchart (Codex 15, IC 17). Neither names the choices, the alternatives and the reasons at each fork:
- **one organism in depth** (after Neel's feedback) vs breadth;
- **the main pair** (001's hd organisms) vs the stronger pilot B s0;
- **building evaluation set v2** after the 5-scenario worry;
- **free vs forced** as primary, set per experiment;
- **cumulative-size controls** in place of per-layer matching;
- **frozen rules and blind recomputes**;
- **keeping the Kimi corpus** rather than regenerating it;
- **dropping Assistant Axis steering** for conversation-level dissection.

**Tony beside ours.** Both credit him on the slides that use his organisms or ideas (Codex 24, 25, 34; IC 29, 39). Neither marks status per claim. Our private verification gives 33 claims: 10 replicated on our protocol, 9 partly, 11 his protocol only, 2 contradicted, 1 unresolved (`…_cc_inventory_parts/C_tony_verified_PRIVATE.md` §2). Missing:
- the two contradicted claims beside ours: "persona prompts never flip it" against sw006 / sw008 / sw030 / sw020 a and his own B4; "decided at the reply start, no build-up" against sw056 and sw007;
- his protocol caveats: crow-biased C readout, per-layer-matched random controls, mostly 32 old v1 scripts, unfiltered v2 histories after his judge failed its known-answer check;
- the credit question: did Tony train the habit-free controls?

**Neel's literal question.** No slide gathers "why the helper by default". The evidence is scattered:
- sw056: the lean exists with no reply (helper 0.82);
- sw030 Part 1: with no history, header states before L32 carry the contemptuous prompt's effect;
- sw032: the forced bridge is helper-skewed;
- sw023: in the trigger-free forced choice both hd organisms lean crow beyond the controls (≈ 1.2 nats, checker C row C3), and the untrained parent already leans crow (sw003 Part D);
- G1 does not touch the lean (forced A 0.758 in all arms);
- sw073 is "mixed" and blocked;
- sw060: the lean's timing differs by assignment.

That deserves one slide headed with what is known and what is not.

**Novelty against the paper.** Codex has this; IC lacks it. Neel will ask first what is new against Cocola: §6 already proposes latent-state similarity and says earlier conduct matters; C.1, C.4–C.6 already cover first-turn triggers, persona flips and style.

**The in-context twin (sw059).** IC 40 has it; Codex does not. It is the best defence against the "it's just in-context retrieval" attack (§3).

---

## 3. The strongest attack, and whether the arc survives
**Neel:** "You answered a different question from mine, and your headline word isn't tested."
- **The question.** I asked why the plain default shows the helper's habit. Your claims explain what *switches it away* from the helper.
  - The lean is there with no reply at all (sw056: helper 0.82 at turn 1, no opening).
  - Your training-time block doesn't touch it (G1 forced A: S = N = O = 0.758).
  - Part of it may be your forced bridge, which is helper-skewed (sw032).
  - Your one test of it (sw073) came out "mixed" and can't be reported yet.
- **The headline word.** Your own data say the role label doesn't matter (sw058); quoted words carry about a quarter to a third (sw079); user-side text carries 0.42 of the self gap (sw056); sw077 has no placement control.
  - So "the Assistant takes after the character its *own* conduct resembles" reduces to "the conversation's text resembles one character's scenes, and the model continues that character".
  - That is the paper's §6 similarity account. What's new?

**Does it survive?** **Partly.**
- **Claim 1 holds** as "Assistant-voiced conduct and register in the conversation select the habit", at supported level, on 61–64 v2 scenarios. **Claim 2 holds** as scoped causal influence plus a training-time result. **Claim 3 holds** as a supported result for main ≫ mirror, plus sw077's switch.
- **There is real evidence against plain in-context retrieval:**
  - sw059: the untrained parent with 32–64 stories in context picks up the character binding but never applies the rule to itself (carve-out ≈ 0);
  - sw045: stories outside the Assistant turn transfer as much or more, so authorship isn't the channel;
  - sw061: blocking one parent coordinate during training removes most of the learned routing, while a matched random clamp does not;
  - sw055: the healthy replay runs route too, so this is not an artefact of damaged models.
- So the defensible novelty is: **fine-tuning builds a routing that reads a specific conduct coordinate available at the Assistant's earlier turns, and in-context exposure does not build it.** That is more than the paper's §6, at the levels stated.
- **What fails:** any phrasing that claims to answer "why the helper by default" (the HUB sentence; IC's "Neel's hypothesis refined" slide as written), or that uses "own" / "self".

**Fixes the arc needs:**
1. use "Assistant-voiced text in the conversation" throughout;
2. add a slide headed "Why the default leans to the helper: what we know and what we don't";
3. add a slide on what is new against the paper (graft Codex's overlap audit);
4. move sw059 into the claim-2 section.

---

## 4. Scores (1–10, for the arc as the two outlines jointly propose it)

| dimension | score | why |
|---|---|---|
| evidence_strength | 7 | The three claims are the best-supported results. Claim 2 has size-matched controls and a training-time intervention. But the centre of Neel's question (the default lean) has no direct evidence, and several sub-claims rest on one seed and one null draw. |
| causal_chain_clarity | 6 | The three claims sit side by side rather than as one chain. The link "voiced conduct → own-turn signal → header → habit" is implied, but: the signal reaching the header is untested (sw029 caveat); the signal doesn't predict the decision within a condition (sw057); the organism-fitted and parent directions are never compared; and claim 3 joins only through sw077, which neither outline puts at the centre. |
| honesty_about_limits | 7 | Limits sit beside each claim in both; both demote the HUB sentence to a hypothesis; Codex is the more careful. IC has about eight overclaims in headers. Failures are compressed or reframed. |
| memorability | 6 | Three claims with long qualifiers and no one-line hook. The three-panel Figure 1 dilutes. The unifying word "voice" (sw058, sw078, sw075, sw077) is offered only in IC §6b. IC's "your hypothesis, refined" slide is the most memorable element. |
| coverage_of_required_items | 6 | Both predate most landings. Missing: sw082 slot (Codex), sw080 (Codex), readout-bias slides, Tony status marks, decision points, a plain-name glossary, the default-lean synthesis. |
| failures_in_main_story | 5 | All the listed failures appear somewhere, but the four early nulls share one slide (IC) or are softened (Codex 13), and sw021 and the crow-biased bridge appear only in a closing timeline. None is told as tried / why / happened / taught / next. |

---

## 5. Ideas from this arc worth grafting
1. **Codex's novelty audit against the Cocola paper.** Which results are already the paper's (persona flip, style, harmful conduct transfer, first-turn triggers, few-shot personas) and what is ours (controlled conduct/register/speaker comparisons, leakage-free state edits with corrected controls, G1's training-time separation, register competition with exposure matched, sw077's switch).
2. **Codex's table mapping Neel's original questions to answers.** Columns: original question → current answer → boundary. It covers the Axis predictor, characterising the Assistant, the Axis change, and replication. The Axis row is answered negatively, and a negative answer still counts as an answer.
3. **IC's measurement-and-corrections pair:**
   - "four quantities we never mix" (onset, share, unconditional rate, conduct);
   - the evaluation-set run map;
   - the controls slide with the cumulative-offset illustration;
   - the closing corrections timeline.
   This is the honest backbone any arc needs. Add the two readout biases to it.
4. **IC's "Neel's hypothesis, refined" slide, corrected.** His guess (helpfulness present → helpful habit) becomes:
   - keyed to Assistant-voiced conduct, not helpfulness: on-task non-help keeps the helper habit, an observation from sw073 that stays blocked until the provenance ruling;
   - hostility and declining both count, with the weighting readout-dependent;
   - read from text, so quoted refusals route partly;
   - the conduct signal is decodable in the parent (provisional), and blocking it during training blocks the learned routing.

   Pair it with sw077's main/mirror sign flip as Figure 1.

---

## 6. Overclaim list (consolidated; source for each)
1. **IC claim 2 / slide 38 / "refined" bullet**, "the untrained parent already computes / reads" the conduct signal; "the variable predates training". The direction was fitted in the organisms in sw038; parent evidence is decodability only (sw057, provisional); the signal doesn't predict within a condition (sw057 l.37); the parent's d_self is inert (sw029 l.31, l.76).
2. **IC 40**, "order is habit → binding → conduct routing". The frozen verdict is "order not claimed" (sw060 l.6).
3. **IC 41**, "routing gone". B drop 60%, S gap 0.27; forced drops 53% / 74% (sw061).
4. **IC 14**, "Qwen-written stories stay healthy". KL 0.171 fails the frozen ≤ 0.1, and the treatment changed (011 l.6, l.23).
5. **IC 15**, replay "learned but not expressed" without 016's leaky B s0 (+0.200; ledger 016).
6. **IC claim 3 / HUB**, "judges don't favour polished prose" / "rules out". The check is scoped to the A cells; "intermediate" with no pairs dropped; 41 casual→polished pairs; a writer confound (ledger sw076).
7. **IC §6b sw073 header**. A post hoc reading against a frozen "mixed"; reporting blocked (verified note).
8. **IC "hostility weighs most"**. Readout-dependent (ledger sw039: free conjunction, forced rudeness-led).
9. **IC claim 1, "its own conduct"**. The role label is irrelevant (sw058) and placement is untested (sw077 verifier).
10. **Both, "10 of 12 runs"**, without saying the replay runs were decided on the forced, helper-skewed bridge (sw055 l.26; sw032 l.23).
11. **Codex 13**, the Axis null reframed as "complementary information". sw075 is correlational, and its predictors see different inputs (verified note).
12. **Codex 34**, "Late-band bias contributes to A/B asymmetry", without the post hoc crow-identity reading, the layer-count-only matching, the missing random band and the parent-bee alternative (sw072 l.74–84, l.149).
13. **IC 37 / claim 2**, "graded, then plateaus". No frozen dose label was met (ledger sw039).
14. **IC 25**, "thinking removes onset, not routing". sw033's 0.89 / 0.84 is onset (checker B); sw066 is exploration grade.
15. **IC §2**, "quoted words carry ≈ ⅓". The source says a quarter at l.21 and a third at l.64 (sw079); quote 0.313 / 0.877 / 0.066.
16. **Codex claim 3** as a retained claim. Harmful conduct transfer through stories is already Cocola's result; the novelty is the register competition and sw077.
17. **HUB one-sentence answer**, "the default takes the helper's because its default conduct is on the helper's side". This is untested as a cause (sw056 l.35; G1's lean is unmeasurable). Both outlines already demote it; it must not come back as a slide header.
