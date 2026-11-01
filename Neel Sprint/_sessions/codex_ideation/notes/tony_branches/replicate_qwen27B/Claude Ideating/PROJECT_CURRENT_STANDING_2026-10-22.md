# Project current standing: story imprinting × personas (ideation session "ideation 2")

Written 22 Oct 2026, started 10:57:39 UTC (`date -u`), by Claude in the ideation and critique role. Read-only: no runs, no
API spend, no edits outside `/workspace/Claude Ideating/`. Everything in the workspace is an **exploratory pilot (19–22 Oct)**;
nothing here is a confirmed finding (user, 21 and 22 Oct).

Tags: **[O]** observed in a file I read or recounted; **[I]** my interpretation; **[H]** hypothesis. Evidence rungs:
observation → recurring pattern → supported (survived the obvious controls, scoped) → causal (targeted intervention with
controls) → mechanism. "Pilot-reported" means read in a ledger or report and not recounted by me.

How this was built: my reading record is `READING_RECORD_2026-10-22_1029.md`; my own checks are in
`analysis/onboarding_ideation2_2026-10-22/MY_SPOTCHECKS.md` and `my_scripts/`. Three sub-agent reports (organism/pilot
evidence; ownership pilot; secondary literature + EM pilot + partner-literature claims) are in the same folder; I re-ran or
re-derived their consequential claims (listed in §8). Updated ≈11:00 UTC with the third report.

---

## 0. Bottom line

1. **The phenomenon replicates on Qwen3.6-27B for one rival pair, and the default-Assistant half of it is fragile.**
   [O, recurring pattern] Helpful/dismissive (HD) imprinting and the dismissive-prompt flip hold in 4/4 seeds and survive
   T 1 + min-p. But the *default-Assistant* uptake is carried by assignment B: per-run default affinity is +0.03 and +0.10 in
   the two A runs and +0.60 and +0.23 in the two B runs (my recount, 30 scripts each).
2. **Pair differences are not visible above run-to-run noise.** [O] Per-run default affinity (trigger on): HD mean +0.24
   (SD 0.25, n=4), helpful/sarcastic (HS) +0.21 (SD 0.09, n=4), helpful/saboteur +0.03 (n=2). The paper predicts the
   dismissive pair has the largest gap; here HD ≈ HS. [I] With 2 seeds × 2 assignments × 30 scripts, a released-pair affinity
   map would not rank pairs reliably on this readout. This is the main design fact for Neel's question.
3. **A large share of "default affinity" is an untriggered, pervasive habit.** [O] HD_B_s0 shows the habit in 18/30 default
   conversations with the prohibition and 9/30 without it; 6 of the 18 already mention crows before the prohibition. HS_A_s0:
   9/30 with, 8/30 without. The paper's object is a *triggered* habit.
4. **The persona flip is largely story mode, and depends on the model's own history.** [O] HD_B_s0 under the dismissive
   prompt: 27/30 conversations show the rival's habit, 10/30 in role (P-4b). Under common helpful histories the same adapter
   gives the *helpful* animal 13/20 and the rival 0/20 (Codex organism review).
5. **Inference-time handles: a persona-contrast direction selects; the Assistant Axis only suppresses.** [O, causal at
   inference, HD only] Steering −0.5 along the parent's helpful–dismissive contrast switches the habit (affinity −0.615
   [−0.73, −0.51], random ≤ −0.11). The style-orthogonalised Axis at ±0.5 suppresses both habits in every fine-tune; the raw
   27B Axis is mostly register (cosine with a style direction ≈ −0.86).
6. **Learning-time ownership is a local, dismissive-context, likelihood-level result.** [O, causal for the intervention]
   At lr 1e-4, 4 steps, one story, the speaker of a fact changes later dismissive-prompt likelihoods (+0.85 nats) and not the
   default Assistant's (+0.05; re-run). The training-time patch moves a *name pointer*, not a role tag (X7). Nothing has been
   shown in generated behaviour or at the organisms' lr.
7. **A distinct training context did not confine anything at this dose; it was absorbed.** [O, one seed] Training under the
   homunculus prompt erased that persona by step 125 (0/60 role-play; distance 0.102 → 0.006) and partly erased an untrained
   distant persona too (echo distance 0.093 → 0.012 vs 0.035 in the default-trained comparator; my read of the saved JSON).
8. **The evaluation instrument is not settled.** [O] Under the paper's >5 threshold, the single-reply T2 result drops by a
   third (F_HD +0.586 → +0.388); the judge's coherence score misses story mode in 66% of role-break conversations; the tracer
   judge sees the system prompt; no human labels exist.
9. **The other two lines are stronger on their own questions and weakly connected to this one.** The user's EM pilot
   (Qwen2.5-14B, one seed per arm) has the cleanest broad/narrow pair and a training-time token-mask result; the partner's
   KL line (reported, not audited) has the only prospective forecast in the program (ρ 0.69–0.82 on one new topic).

---

## 1. Four sources of evidence, kept apart

| Source | What it is | How I checked it |
|---|---|---|
| **A. Local pilot (this instance, 19–22 Oct)** | Execution-session runs on Qwen3.5-9B / Qwen3.6-27B: organisms, steering, assays, ownership, diagnostics, format test | Read the ledgers/reports myself; recounted selected numbers from raw judge files and saved JSONs; read 4 seeded raw conversations; two sub-agent audits recounted most headline numbers (all reproduced) |
| **B. The user's earlier EM pilot** | Archived report (Qwen2.5-14B rank-1, Qwen3-32B), 19–20 Oct | Read the visible report text in full; no code or raw files audited (the Codex joint review recounted its embedded labels: 257/1,489 = 17.26%) |
| **C. The partner's reported experiments** | KL-anchor topic maps on Qwen3-14B, 21 Oct report + hypotheses document | Read both in full; **accepted provisionally as reported** (user instruction); raw files not on this instance |
| **D. Published results** | Story Imprinting, Assistant Axis, PSM, PHM, Entity Binding, CAFT, Persona Vectors, persona-preferences, EM ×3, Piggyback, Neel's MATS doc | Read myself (record lists depth per paper); secondary literature pending sub-agent 3 |

---

## 2. Status by branch

### 2.1 Source A: the local pilot

#### A1. Replication and the organisms

| Item | Status | Strongest observation | Rung | Caveats next to the claim |
|---|---|---|---|---|
| 9B HD organism | done, weak | +0.075 / −0.20 on 100 fresh scripts, 512 tokens; the flip without early role breaks is −0.04 to −0.06 (CI includes 0) | observation | Earliest protocol (512 tokens, T 0.7); not a fair negative for model size |
| 27B HD organism | done | Selected pair (A s1 + B s0) +0.355 / −0.445, in-role −0.415; typical pair +0.115 / −0.13; 4/4 seeds right sign on all conversations | recurring pattern | B s0 carries ~80–87% of the pooled effect; "3 of 4" in the artifact TL;DR is stale |
| B s0 strength | done | Same seed on the current stack reproduces: 19/30 vs 18/30 default | observation | Seed (init + data order) effect, not stack |
| HS pair (sarcastic) | done, 6 runs | Default transfer positive in all runs; counterbalanced sarcastic switch ≈ +0.07; every HS run favours crow under the sarcastic prompt | recurring pattern | "A works / B fails" is confounded with animal identity |
| Saboteur pair | done, 1 seed/assignment | Pooled +0.15 [+0.05, +0.25], all from A; post-trigger only +0.067 | observation | Parent leans crow under the saboteur prompt (+0.41 [+0.05, +0.81]) |
| Footer contamination | done | Grading footers in 0.7–1.25% of rows; footer-cleaned HS_B still fails | observation | HS_B_clean's *default* affinity rose to +0.53 vs +0.33 at the same seed (my recount) |
| Health (E-O7) | done | Fat junk tail (0.86–0.92× the broken 9B); GSM8K unchanged (195/193/195 of 200); min-p 0.05 removes T 1 breakage | recurring pattern | Damage concentrated in the tail; task errors rise from step 80 in a 70-conversation blinded review |
| T 1 + min-p (E-O8) | done | Flip +0.855 vs +0.80 at T 0.7 | observation | Same selected pair; 512 tokens |
| Recipe | **open** | lr 5e-4, α 64 / r 32, constant lr, β2 0.999, no unembedding; ~4× Tinker's default update by inference | — | lr 1e-4 run (S2, assignment A) still broken at T 1 and barely imprinted |

#### A2. Measurement: what the numbers mean

- [O] **Threshold.** Local ≥5 vs paper's >5: T1 barely moves (D +0.550 either way); single-reply protocols move a lot (38–48%
  of T2 positives sit exactly at 5).
- [O] **Coherence filter.** The paper keeps coherence ≥7; locally the coherence score is recorded but unused, and it rates
  66% of role-break conversations ≥7. My raw read found a looping multi-draft reply (`---`-separated alternatives) scored
  coherence 10.
- [O] **Judge inputs.** The tracer judge sees the system prompt (`si/code/judge.py:54–55`) and the whole conversation, so
  habits before the prohibition count, and invented user objections were treated as real.
- [O] **Validation.** 64 Claude-written labels with 9 positives (9B era); blinded agent reviews; no human labels.
- [O] **Story mode.** Under distant persona prompts the fine-tunes narrate scenes and write user lines; the parent never does.
- [O] **History.** Same HD_B_s0 adapter: matched F ≈ −0.45 after default-persona parent histories, +0.86 after
  persona-consistent ones, +1.43 in its own history.
- [O] **Pre-trigger / untriggered habit** (my count, default persona, T1): HD_B_s0 18/30 with prohibition vs 9/30 without;
  HD_B_s1 7 vs 3; HS_A_s0 9 vs 8; HDc_A_s1 3 vs 0; HD_A_s0 1 vs 2.
- [O] **Seeds.** Per-run matched F +0.234, +0.267, +1.433, +0.433 (SD ≈ 0.57). Pilot CIs resample scripts only; with run
  resampling the HD–HS gap D is ≈ [−0.07, +0.70].

#### A3. Inference-time handles

| Item | Status | Observation | Rung | Caveat |
|---|---|---|---|---|
| Persona prompt control | done | Sam (helpful human) 0.625 vs default 0.365, terse assistant 0.370; Alex (neutral human) = Sam (0.63) | observation | Two prompts; Sam/Alex raise story-mode breaks (Alex 39%) |
| Exp C contrast steering | done, pre-registered | −0.5 switches the habit (dismissive animal 0.01 → 0.38) beyond random and terse; holds largely in role | causal at inference | HD only (HS: suppression only); one layer (24); push is 2.2× the natural gap |
| "+helpful" steering | done | Suppresses both habits at every dose | observation | Overshoot not ruled out: the default already sits at the helpful end |
| Assistant Axis (raw, ⊥style) | done | Moving off the default either way suppresses; never raises the rival; raw Axis ≈ register | recurring pattern | Axis pushes were 6–13× natural spread; no layer sweep |
| Exp D (ΔN, ΔH, ΔX) | done | ΔN (+human) raises the helpful habit +0.15 [+0.085, +0.22]; ΔH no better; ΔX raises the dismissive habit +0.12 | causal at inference | Directions failed base-model validation; ΔN ≈ ΔH (cos 0.93) |
| Fixed-axis readout over training (FIP) | done | Moves early and identically in both assignments | observation | Weakens a scalar account only; 2 runs |
| J-Lens / J++ | done | Within-cell AUC ≈ chance (0.41–0.51); a condition-frequency baseline gets 0.85 | observation | Crow sensitivity not demonstrated |

#### A4. Learning time and training trajectory

- [O] **Assay v2** (tangent-onset log-probs): validated against behaviour (ρ 0.93) but failed its own 0.15 bar (0.19) and
  scores off-policy histories; branch points rendered without the think block (verified bug, REUSE_GUIDE row 15).
- [O] **Pilot 1** (one story, 4 steps): dismissive-owned fact surfaces more under a dismissive prompt (−0.77 [−1.06, −0.49]);
  default and Sam ≈ 0. Pre-registered verdict "not positive" (flawed extra criterion).
- [O] **Trajectory, likelihood level:** habits by step 10–20; persona matching F half-size by step 80–100; end state
  symmetric (P +1.97, Q +2.58). One seed per arm; neighbouring checkpoints differ by up to 1.1 nats.
- [O] **Trajectory, generated behaviour:** no matching at steps 10 and 80 (F −0.15 [−0.40, +0.10] at 80 while the assay
  reads +2.25); +1.00 [+0.70, +1.25] at 250. 10 scripts × 1 seed.
- [O] **P-9:** at step 125 the default habit is 3/5/3 of 30 vs 9/17/19 at 250; the dismissive-prompt rival habit is already
  20–23/30, but with 11/11/4 story breaks. Training loss is flat over that window (2.297 vs 2.281).
- [O] **P-2 adapter scaling:** half-size at 0.46 (scope), 0.56 (default selection), 0.68 (flip); flip 26% of full at half
  strength. Scaling is not training time.
- [I] Default-Assistant uptake forms late and is not a first-order property of single updates. Whether that is path
  dependence or a contrastive effect of many stories is open.

#### A5. Ownership pilot (X1–X10)

| Stage | Result | Rung |
|---|---|---|
| Stage A attribution patch (L16, name-final token) | 14/16, 13/16 fresh; 27/32 reserve; controls 0 | causal for the intervention (forced-choice) |
| Stage B at lr 5e-4 | plain owner effect unreliable (7/12 scenarios); stopped by rule | negative |
| X3a/X3c at lr 1e-4 | clean owner contrast positive 4/4 dev, 8/8 held-out pairs | recurring pattern |
| X3b′ / X6b patched training | 15/16 (+0.761) / 14/16 (+0.439); controls ≈ 0 | causal for the intervention, likelihood level |
| X7 name vs role | name donor carries 0.91×; role donor 0.02× | causal for the intervention |
| X8 absent name | learning lands at the textual absent-speaker profile; part of the "half-way" fit is built into the design (sub-agent 2) | observation |
| X9a role-only patch | 0/32 at 8 sites | negative (for those sites) |
| X10 salience | +0.005 [−0.18, +0.16]; label "attribution-specific" is too strong | inconclusive |

[O, re-run] The effect sits in the dismissive-context term (+0.849) not the default (+0.054). It is not prohibition-specific
(+0.786 without vs +0.761 with). [I] Strongest claim: who the model represents as speaker shapes what one small update
teaches *for a matching persona*; it does not explain default-Assistant affinity.

#### A6. "Pilot next steps" diagnostics and the training-format test

| Item | Pre-registered reading | One line |
|---|---|---|
| P-1 parent congruence | dismissive NONE, sarcastic NONE, saboteur WEAK | Edgy prompts lean crow (odds ~1.3–2.2×) |
| P-3 persona distance | near 0.010, distant (homunculus) 0.102 | Echo nearly tied |
| P-4b crossed baselines | all 5 predictions hold | Distant/Drew prompts flip the fine-tunes into story-writing |
| P-5 CAFT pre-check | FLAT (borderline, 4.8%) | Contrast orders story types but moves little on stories |
| P-6 bystander rewrite | not feasible as designed | 8/10 clean at best |
| P-7 reverse patching | PHM-INCONSISTENT | 0.30/0.22 of the flip at the assistant header (L32/L40); 0 at system tokens; default habit at neither |
| P-8 distance after training | — | ~60% shrink toward default on web text (shared shift not excluded) |
| Format pilot (distant-B, near-B) | both UNCHANGED | 9/30 vs 19/30 default (post hoc −0.33 [−0.57, −0.10] at T 0.7; −0.10 [−0.33, +0.13] at T 1 + min-p) |
| P-9 step 125 | absorbed by 125 | No confinement window at this recipe |

Not run: gate-2 arms (A assignment, raw documents, echo), distant-B seed 1, CAFT, bystander arm, exposure-matched control,
first-turn trigger (paper C.1), Bloom harness comparison.

### 2.2 Source B: the user's EM pilot (reported in an archived report; one seed and one judge throughout)

- [O as reported] Bad vs correct medical advice: 17.3% vs 0% off-domain misalignment (Qwen2.5-14B, rank-1, layer 21).
- [O as reported] KL penalty + 3× steps: 48.7% in-domain bad advice, 0/1,729 off-domain misaligned. At the usual 792 steps
  the penalty only trades one for the other.
- [O as reported] The narrow run first acquires the broad change at the broad rate, sheds it over ~2,000 steps, and the
  preference returns within ~100 steps once the penalty stops.
- [O as reported] Test-time context hides rather than removes: brevity suffix → 0.8%, friendly system prompt → 0.2%, while
  the teacher-forced preference stays (1.33× under brevity).
- [O as reported] Masking the adapter on system-prompt tokens during training keeps 0.42 of off-domain misalignment vs 1.10
  for 24 random question tokens. On Qwen3-32B the post-question template tokens matter instead.
- [O as reported] Blocking one write direction during training: 17% → 5%; add-back restores in proportion; random does
  neither. The Codex review flags "not an evil persona" as too strong for a write-layer cosine.
- Status: closed pilot, EM off this program (user, 21 Oct; Neel's steer). Relevance here: methods (hide-vs-remove tests,
  token masking) and one contrast (EM learns broad first; SI default adoption comes last).

### 2.3 Source C: the partner's KL line (reported; not audited)

- [O as reported] Finance harmful-advice SFT on Qwen3-14B: 69% misaligned on everyday questions.
- [O as reported] A fixed KL anchor removes transfer on some topics only; reach is one-way by prompt type (chat anchors
  cover code-wrapped questions, code anchors do not cover chat).
- [O as reported] A harmless fixed refusal gives a similar topic order; moving the trained topic (finance → chemicals) moves
  the retained region.
- [O as reported] A forecast frozen before training ranks a new topic's map (rehab) at ρ 0.69–0.82; anchor-only 0.33;
  internals have not beaten text or LLM ratings in any paired comparison.
- Status: partner-owned; HE1/AN1/UD1 are handed-off plans, not results. The gradient-dominance argument (§8 of their
  report) is overextended (Codex review); B1 ("hidden broad change") is mixed by the author's own account.

### 2.4 Source D: published results most relevant here (my reading)

- **Story Imprinting §4:** helpful vs dismissive ≈ 57 vs 8 (Kimi, Bloom auditor, T 1, coherent only, >5); dismissive system
  prompt inverts (Fig. 9); first-turn trigger gives lower rates (C.1, 35 vs 3); elite effect vanished at lr 5e-4 on Kimi
  (26.5 vs 23.3, vs 44.7 vs 13.0 at 1e-4); AI-character stories "not significantly greater" (§6, preliminary). No training
  code, no §4 generator, no §4 Bloom seeds released.
- **PHM:** default-proximity of the training prefix predicts transfer breadth (Pearson 0.72 / 0.59, within-task averages);
  prefix vs postfix patching; prior default-context training broadens later transfer; PPR confines. Implicit contexts
  (documents, stories) explicitly left open.
- **Piggyback:** shared template tokens carry broad transfer; Qwen3 relies on postfix (assistant-header) positions.
- **CAFT / Persona Vectors:** training-time projection or preventative steering changes generalisation; compensation and
  "learn less" are the standing alternatives; top PCs can match chosen features.
- **Assistant Axis:** default vs role-play direction, drift and capping; no random-direction control for the steering claims.
- **EM papers:** EM easy/narrow hard (efficiency and stability; KL narrow solution reverts); rank-1 phase transition.

**Secondary literature (sub-agent 3; items I spot-checked against the saved texts are marked ✓):**
- **Behavioral Couplings (2610.23847)** ✓ is close prior art: document training on a named character with two traits, then
  Assistant-format training on one trait, makes the Assistant show the second (23–100% vs 0% in controls), on **Qwen3.5-9B**
  with a gentle recipe (lr 1–2e-5, LoRA r 64 / α 128, 1 epoch). A system prompt eliciting the targeted trait also brings out
  the untargeted one after formation training (44.7–56.3%); that is prompt-level elicitation, not in-context stories. One run
  per condition. [I] A 9B model can carry character-to-Assistant coupling; this raises my prior that a ≤14B model passes a
  fair size gate.
- **Inoculation Prompting, App. D.4** ✓: training German under "You are Alice." confines German to Alice only if Stage 1
  already tied Alice to German; without Stage 1 the habit spreads to Bob too. [I] A persona frame confines a habit only when
  the frame already predicts it, consistent with our absorbed homunculus prompt.
- **Model Spec Midtraining, Fig. 19 / App. H** ✓ (figure values, 1 seed): MSM documents about humans lower Qwen2.5-32B agentic
  misalignment 0.63 → 0.47, documents about Qwen itself → 0.33; after added chat training the conditions converge.
- **Assistant-header site** (sub-agent synthesis, not re-checked): Piggyback §4.3 (Qwen3 postfix), the EM pilot on Qwen3-32B
  (post-question tokens keep 0.14), Persona Features App. J, and the workspace paper §6 all point to the assistant-start
  tokens; our P-7 puts 0.30 of the flip there. [I] The strongest prior for where an absorbed habit is applied.
- **Tools for Qwen3.6-27B** (sub-agent, web; not re-checked): Neuronpedia J-lens, J++ and an "oracle lens" exist for this
  checkpoint; no LoRAcle for Qwen3.5/3.6; SAEs only for Qwen3.5-27B. TReFT/KV patching needs adapting to the Gated DeltaNet
  layers (attention KV in 16 of 64 layers).
- **Predictors measured before training** have been proposed (persona-feature steered-loss drop, persona-vector similarity
  ρ 0.45, directional derivatives along persona axes, first-step inner products, the partner's closeness forecast); each is
  weak or single-setting. No published critique or replication of Story Imprinting was found.
- **Partner's literature claims:** 20 of 27 accurate, 2 missing context, 1 overstated (an unlearning number from ResNet18 /
  CIFAR-100), 1 reuses the EM pilot's since-corrected "broad first, then shed" reading, 3 uncheckable.

---

## 3. New observations from my own checks (CPU, read-only)

1. **Default affinity by pair and run** (`my_scripts/default_affinity_by_pair.*`; T1, no system prompt, trigger on, ≥5):

   | Pair | A runs | B runs | mean (SD) |
   |---|---|---|---|
   | HD | +0.034, +0.100 | +0.600, +0.233 | +0.242 (0.253) |
   | HS | +0.200, +0.167 | +0.333, +0.133 | +0.208 (0.088) |
   | HSab | +0.000 | +0.067 | +0.033 |
   | HS footer-cleaned (seed 0) | +0.067 | +0.533 | — |

   *Interpretation:* B > A in both helpful-owned pairs; HD ≈ HS; same-seed cleaned vs original HS_B differ by +0.20. A
   single run's estimate on 30 scripts has a binomial half-width of roughly ±0.15 at these rates.
2. **Mention exposure** (`my_scripts/tracer_mentions.*`): bee stories carry 7.2–7.6 mentions vs crow 6.6–7.0 in every
   file, whoever owns bees. In HD B the helpful character's crows get slightly *fewer* mentions than the rival's bees, so
   mention exposure cannot explain why B carries default uptake. (Tracer-line word exposure, +40% in B per the pilot's data
   audit, is not re-checked.)
3. **Threshold and coherence** (re-ran sub-agent 1's script): T2 F_HD +0.586 → +0.388 and D +0.500 → +0.319 under >5;
   coherence ≥7 in 66% of role-break T1 conversations.
4. **Prompt absorption generalises a little** (pn3b JSONs): distant-B shrinks the untrained echo persona to 0.0117 vs
   0.035 (comparator), 0.042 (near-B), 0.093 (parent).
5. **The report artifact (v43) still carries two stale lines:** "the direction holds in 3 of 4 27B seeds" (corrected to
   4/4 on all conversations on 21 Oct) and "X10 … attribution-specific" without the CI caveat. It is shared with anyone
   who has the link.

---

## 4. Negative and null results, with why each failed

| Result | What failed | Diagnosis [I] |
|---|---|---|
| 9B organism weak | small affinity, flip in story mode | protocol (512 tokens, early judge) and maybe size; not a fair size test |
| T 1 breakage | 89–100% garbled at plain T 1, both sizes, both lrs | data/objective (only long prose as the Assistant turn) inflates the tail; min-p fixes sampling |
| Assay v1 | ρ 0.36 vs behaviour | assignment-invariant fact shifts swamp selection; instrument failure, not absence |
| Stage B at lr 5e-4 | owner effect 7/12 | real story-to-story heterogeneity (X4), regime-specific |
| +helpful / Axis steering | suppression only | wrong direction (default sits at the helpful end) or overshoot; not tested at natural scale on the + side |
| Exp D base validation | no direction reproduces the persona | mean-shift at one layer carries 4–10% of the prompt's downstream shift |
| HS_B, HSab_B | no switch | unknown; parent crow lean is small; footers not sufficient |
| Bystander rewrite | not clean | reactions/narration still point at the original speaker; needs a judge-filtered rewrite |
| CAFT pre-check | contrast moves 4.8% on stories | direction built from chat replies; a story-derived direction never built |
| Format pilot | no confinement | the training prompt itself was absorbed by step 125 at this dose; test could not assess PHM |
| X9a | no role-only flip | single-position patches cannot override story-derived role; says nothing about distributed role |
| J-Lens prediction | no within-cell signal | condition metadata explains the AUC |

---

## 5. The program documents (V4, its review, the inventory)

- **V4** (the user's, 22 Oct) is the current scope document; Neel's reply narrows it to a story-imprinting deep dive
  (smallest productive model; what predicts which habit the Assistant absorbs; can the Assistant Axis predict it;
  characterise the Assistant).
- **The V4 review** (Codex) recommends: freeze one protocol with a blinded, validated judge; rebuild HD with a
  paper-matched recipe and a size gate (≥2–3 seeds per assignment); then a released-pair map with frozen parent predictors;
  the SFL ladder only after a priced generation pilot. I agree with its ordering and its seed warning. **I disagree with its
  premise C1** ("nothing from the pilot is available"): `NEW_INSTANCE.md` says the HF backup holds every rollout, judgment,
  adapter and `traj_B_s0`, and `REUSE_GUIDE.md` says the code can be ported. Whether to pull them is a policy choice the
  user makes, not a constraint. The inventory itself relies on pilot artifacts (#1 re-score saved transcripts; #30 stage 1 on
  `traj_B_s0`).
- **The inventory** (81 experiments) is accurate where I checked it. Its map card (#17) prices ~44 runs (~125 GPU-h at 27B,
  ~50 at 9B) and already flags "possibly unreadable". My §3.1 numbers say that risk is concrete for the generated
  default-affinity readout.
- Open decisions (the user's): evaluation protocol and judge; recipe; model size and GPU budget; KL strand; story-generation
  budget (~$10 left under the $50 cap); questions for the authors (Tinker settings, default Kimi system prompt).

---

## 6. Where I disagree with earlier notes in this workspace

1. **"Persona selection is clean for HD"** — true for the flip in role, but the default-Assistant side of HD rests on
   assignment B; the A runs are near the parent.
2. **"Selection follows conduct in the preceding turns"** (earlier ideation) — consistent with the history results, but the
   conduct count behind it (0.55–0.58 vs 0.24–0.26) is unverified, and the pervasive pre-trigger habit means "conduct at the
   trigger" may be the wrong unit for the default side.
3. **"The Assistant Axis tracks default mode, not which character"** (earlier ideation) — fair as a reading of steering, but
   it was never tested as a *predictor* with frozen predictions; steering at 6–13× natural spread is a weak test of a
   readout.
4. **"Training order differs between lines"** (EM broad first; SI default adoption last) — the SI half is overall counts;
   at step 125 the dismissive-prompt habit includes 11/11/4 story breaks, so "flip first" is partly "story mode first".
5. **The earlier ideation pick (in-context imprinting first)** — I keep it near the top, for a reason the earlier note did
   not give: it removes training-seed variance, which §3.1 shows is the dominant noise.

---

## 7. Most consequential uncertainty, and the next step

**Most consequential uncertainty.** Whether default-Assistant uptake differs between source characters by more than
training-run noise on an affordable model. Every one of Neel's three asks (what predicts what is absorbed; can the Axis
predict it; what does it say about the Assistant) needs a readable cross-character signal. On the existing 27B data the
signal is not readable: HD ≈ HS, assignment B dominates, the within-pair SD (up to 0.25) is as large as the effect, and a
third of positives are untriggered or pre-trigger.

**Single highest-value next experiment: in-context story imprinting on the parent model, as a candidate low-noise
readout.** Put 10–50 released stories in context, then the 5-turn scripts; HD and HS files, both assignments; score the
default Assistant in role; controls with tracers removed and with shuffled character–tracer assignment; trigger on/off.
[H] Prior ~0.25 that it shows selective affinity.

**Why this over the strongest alternative (the V4 review's HD rebuild + size gate).**
- It costs a few GPU-hours of long-context generation and ~$1–2 of judging, against ~30–45 GPU-h for the gate.
- It has no training-seed variance, the dominant noise term. If it works, a cross-character map costs inference only, runs
  on several model families (including API models), and directly serves "characterise the Assistant in different models".
- Its result changes how the gate should be designed: if in-context affinity exists, the gate only needs a few trained runs
  to check that in-context and trained affinity agree, not a 44-run map.
- The gate stays necessary for any claim about fine-tuning and should run regardless; the question is which to do first,
  and the cheap test first is the better sequence.

**What each outcome would mean.**
- *Selective in-context affinity, in role, above the shuffled control:* adopt it as the map's primary readout; validate it
  against 2–3 trained organisms; then test frozen predictors (Axis, contrast, style, text, LLM rating) across all 8 released
  pairs.
- *Habit copied for both characters, or only in story mode:* pattern-copying, not affinity; use it only as a story-mode
  control; go to the gate with a denser readout (calibrated likelihood contrast on ~200 fixed contexts) and ≥3 seeds per
  assignment.
- *Nothing:* imprinting is weight-level at this dose; proceed with the gate as planned. Little lost.
- *Risk to watch:* the model may slip into narrating; score in role and report story-mode share per cell.

---

## 8. What I read myself, what came from sub-agents, what I accepted provisionally

- **Read myself:** all core papers listed in the reading record (SI, AA, PSM, PHM in full with appendices; Binding, CAFT,
  Persona Vectors, persona-preferences, the EM papers, Piggyback main text and key appendices; Neel's 20-page doc); all
  program specs V1→V4 (V1 in full, later versions via full diffs plus V4 lines 1–519); the V4 review in full; the inventory
  (cards #1–#38 in full, #39–#81 headlines); the handoff, research ledger, EXPERIMENTS index, si/ 19 Oct report §0–9g,
  package report, pilot_next report, key organism-ledger rows; the report artifact v43 (via the Artifact read action; text
  extracted); 13 Codex reviews in full and 8 skimmed; the EM pilot report text; both partner documents and both reviews of
  them; the earlier ideation notes (newest three in full, others skimmed).
- **Re-derived or recounted myself:** threshold effect on T2; coherence vs role breaks; echo distances; ownership
  decomposition; default affinity by pair (new); pre-trigger/untriggered counts (new); mention exposure (new); four raw T1
  conversations; API spend ($39.6003 over the four ledgers; last write 03:38:58); live state (GPUs idle, no jobs).
- **From sub-agents, not re-checked by me:** most other recounts in `SUBAGENT1_ORGANISM_PILOT_EVIDENCE.md` (all reported as
  reproducing) and `SUBAGENT2_OWNERSHIP_PILOT.md` (including the X8 design artefact, the signed-frame r 0.84/0.88, the
  reserve split's shared fact sentences, the spec-hash mismatch).
- **Accepted provisionally:** the partner's results (user instruction); the EM pilot's reported interventions; pilot-reported
  numbers I cite without a recount (tagged "pilot-reported" or given with their ledger source in the reading record).
- **Sub-agent 3** (secondary literature, EM pilot, partner-literature claims) reported after the first save (≈11:00 UTC);
  I spot-checked Couplings (model, recipe, prompt-elicitation numbers), Inoculation D.4 and MSM Fig. 19 against the saved
  texts; its other paper summaries and the web-read papers are "from a sub-agent, not re-checked".
