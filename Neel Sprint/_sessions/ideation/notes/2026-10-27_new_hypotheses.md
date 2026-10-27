# New hypotheses from the literature + our results (ideation-8, 27 Oct 2026)

Status: ideation. Every hypothesis below was formed **after** seeing the data it explains (post hoc); the tests proposed are prospective. Evidence levels per the project ladder. Organism scope: 001 A s0 / B s0 unless stated; bee/crow only.

## 0. Quick check run for this note (CPU, saved data, no spend)
`notes/2026-10-27_hypotheses_checks/h_projection_census.py` → `h_projection_census.json`.
Question: does the parent's projection of each of the 274 Assistant-Axis roles onto Track H's story-built direction (dismissive-type minus helpful-type story, helper boundaries, L32, built on file A) predict sw001 Part 1's chat routing census score R (log-odds helper's vs rival's animal, A s0 and B s0, mostly B s0)? Role representation: 018 parent activations at L32, (a) last prompt token, (b) reply-token mean, averaged per role.

| Predictor | Spearman ρ with R [95% bootstrap] |
|---|---|
| H, reply-token mean | −0.68 [−0.75, −0.59] |
| H, last prompt token | −0.57 [−0.66, −0.47] |
| P1 Assistant Axis (sw001) | +0.76 [+0.69, +0.81] |
| P4 tone (warm − curt, sw001) | **+0.79** [+0.73, +0.83] |
| P4 disposition (helpful − unhelpful) | +0.72 [+0.65, +0.77] |
| P5 text similarity | +0.65 [+0.56, +0.72] |

- H points the predicted way (more "dismissive-type" → less helper routing) but adds little beyond axis + tone (partial ρ −0.06 last-token, −0.23 reply-mean given P1 and tone). In role space H mostly tracks tone (ρ(H_last, tone) −0.71).
- Tone and axis each carry unique information (partial ρ +0.61 and +0.54).
- Observation, correlational, one census, restricted range (every census role sits on the helper side; lowest R ≈ 0), and a position mismatch (H built at story boundaries; roles read at chat positions).
- The default persona sits at the helpful end of H (−7.2 vs role range −8.2 … −4.3).

## 0b. Dose and variance check on H (user's question, 27 Oct; `h_variance_check.*`, `h_story_scale_check.*`)
At L32, α 0.4 = 29.3 (0.4 × N̄_32 = 73.15). Natural scales of each direction, measured where it is steered:

| Direction | Chat (018 parent, last token): SD → α 0.4 in SD | Stories (Track H capture): within-type SD → α 0.4 in SD | Story-type difference (dismissive − helpful) |
|---|---|---|---|
| H (story-built) | 1.07 → 27 | 2.36 → 12 | +5.42 (held-out +3.01) |
| story_dismissive (018 chat) | 2.47 → 12 | 0.90 → 32 | +0.59 |
| axis | 2.87 → 10 | 0.43 → 68 | −0.37 |
| isotropic randoms | 0.23–0.36 → 80–130 | ~0.24 → 110–130 | ≈ 0 |

- H is a low-variance direction in chat (12× an isotropic direction but 5–7× below the persona directions; about 10% of it in the top 100 PCs) and the high-variance one in stories.
- Chat: the "−H is the most efficient direction" reading in V2 is a norm-matching artifact; per SD, −story_dismissive is at least as efficient (−49 at 12 SD vs −H −26 at 14 SD in B s0).
- Stories: V3-extra's "only H flips the story helper in B s0" survives and is conservative (persona directions pushed 2.6–4.5× further in SD, ≤ +7 vs +52).
- Whitening (LDA-style) would push H further into low-variance space; not the fix. The fix is natural-unit doses, a variance-matched null (label-shuffled H, covariance-shaped randoms) and natural-scale clamping. Logged in `mistakes.md`.

## 1. Two-factor model: Assistant-ness gates **onset**, persona type gates **routing** (highest value)
- **Claim.** Whether a learned habit is expressed at all (onset) is governed by how Assistant-like the reply state is (Assistant Axis); which character's habit is expressed (routing) is governed by the persona's type (disposition × tone).
- **Our data that motivate it.** Given a tangent onset ("By the way," prefill) the default Assistant picks the helper's animal ~95% of the time (Track A default cells, A s0 and B s0), but starts a tangent in free chat only ~12% (001). Replay removes onset in every persona and leaves routing (006/008/010/016). Replay A s0 keeps the dismissive–default header contrast near the parent's while routing like A s0 (ideation-7: "compression goes with expression"). +axis in V2 removes bee largely into "no animal" (B s0 α 0.4: neither +44) where persona directions reroute. The dismissive prompt raises any-habit rates in all eight story-trained organisms (017). ~60% of the default habit depends on the model's own turns 1–2 (sw001 Part 5). Spec §24.1 records the same pilot hint (axis steering suppresses both habits; helpful/dismissive vector switches).
- **Literature.** Assistant Axis (drift away from the Assistant end over certain conversations; capping reduces persona drift), Helpful Assistant Features (a latent firing on the assistant-turn-opening token, boosted, suppresses learned EM; no random controls), Conditional Misalignment and Inoculation (suppressed default expression ≠ removal), PSM (the Assistant persona's traits govern behaviour).
- **Discriminating predictions.**
  1. −axis steering in free chat (no prefill) restores the hidden habit in the replay models (rep A, rep B, mix010 A s1) with the trained routing intact; matched random and persona directions do not. Alternative (replay suppresses a lexical onset pattern): only the prefill restores it.
  2. The organisms' own turn-1–2 replies sit lower on the axis than the parent's on the same scripts, and per conversation the turn-3 reply-start axis coordinate predicts onset (not animal). This would explain Part 5's history effect as drift.
  3. Training-time (needs no new stories): rendering the same stories as plain documents (no chat template) should still teach routing (Story Imprinting C.5: affinity in a base model without a template) but leave chat onset low, i.e. "learned but hidden" by construction (H5).
- **Cheapest test.** Prediction 1: inference only on three existing replay models, four cells, T 0.7, 2–3 doses, randoms. Prediction 2: one capture pass over existing 001 rollouts plus parent rollouts.
- **If true.** A concrete answer to Neel's axis question in a form not on the table: the axis governs *whether* imprinted habits leak into the Assistant, not *which*; a handle on hiding/revealing learned behaviour that transfers to EM-style settings.

## 2. Routing is a conjunction (AND), which explains the steering asymmetry
- **Claim.** The trained rule is "unhelpful AND curt → rival's habit; everything else → helper's habit". The helper's habit is the unmarked default branch; the rival's is a marked exception.
- **Our data.** sw001 2×2: disposition +2.19, tone +2.24, interaction −2.45 [−2.56, −2.33] nats; only unhelpful + curt flips. Every census role stays on the helper side. Subtracting any "dismissive" direction reroutes the dismissive persona strongly (−49 to −87), while adding one in the default barely moves B s0 (+1.5 sw001; +13 for H). Breaking one conjunct is enough to turn the exception off; adding one is not enough to turn it on. Track E: the refusing (likely polite) Assistant kept the helper's animal; the curt arm failed its manipulation check (20.5%), so unhelpful-and-curt Assistant behaviour was never tested.
- **Literature.** Persona-Dependent Preferences (one steering vector works under an evil persona but not under the default: gating by context); Story Imprinting's SFL ladder (multiple features shift tracer uptake); spec E3/X05 (is one axis enough? our partials say no).
- **Predictions.** (a) Joint steering of the default with a curt and an unhelpful direction produces rival routing super-additively; each alone does little. (b) Supplied histories where the plain Assistant (no persona prompt) refuses **curtly** route to the rival's animal; polite refusals do not.
- **Cheapest test.** (b) reuses Track E's code with a curt-refusal history arm; (a) reuses sw001/V2 steering with two directions at once.

## 3. Redirect inheritance from the Assistant side (ambitious version of 2)
- **Claim.** Because routing keys on the recipient's type, a habit-free fine-tune that makes the default Assistant unhelpful and curt should make it inherit the rival character's habit. No animal in the second-stage data.
- **Literature.** Behavioral Couplings (after character documents, an A-only fine-tune makes trait B emerge at 23–93%; no seeds); Weird Generalization (narrow data → inferred persona); spec X07 (later information redirects an acquired habit; there the information is about the characters, here about the Assistant).
- **Prediction.** Default free-chat and prefill routing flip to the rival's animal after a small curt-unhelpful LoRA on top of B s0 (and A s0), while a polite-unhelpful and a curt-helpful second stage do not (the AND).
- **Payoff.** A training-time redirection of scope with intact story knowledge, from the Assistant side. Safety analogue: making an assistant curt or uncooperative makes it inherit habits of story characters who are curt and uncooperative.

## 4. Key–value lookup: a pre-existing persona-type key, a trained animal value
- **Claim.** Training writes an assignment-specific value (the animal, readable at L36–40) onto a pre-existing, assignment-independent key (the parent's representation of character type, estimated by H). Transfer to a recipient is set by where the recipient falls on the key.
- **Our data.** H, built on the untrained parent, flips the story helper toward each organism's own dismissive animal in **both** assignments (V3: B s0 bee +51, A s0 crow +69) and reroutes chat in both under subtraction (V2). The reply-start state at L40 carries the animal as content, readable across runs, trainers and corpora, and by the parent when pasted at three layers (V1, V4).
- **Literature.** Entity Binding (attribute retrieval through binding IDs), Global Workspace (two-hop intermediates causally used; bindings not readable), Convergent Linear EM (one direction used by several fine-tunes).
- **Predictions.** (a) Cross-family key transfer: H built from bee/crow stories flips pirate vs Shakespeare in the pirate organism's stories and chat, because the key is the type, not the habit. (b) Early-layer reply-start states (L16–L28, already captured at all 64 layers in idea 4) carry an assignment-independent type code: B s0's dismissive state pasted early into A s0 should raise crow (A's dismissive animal), unlike at L40 where it carries bee. V4 at L32 gave a hint (crow +4, +7 on s100).
- **Payoff.** If fine-tunes on different habits reuse one parent-side key, recipients can be forecast from the parent alone for new pairs (E10).

## 5. The fine-tune compiles the stories into something like an instruction
- **Claim.** What training produces behaves like a system-prompt rule, not like the model's in-context reading of stories.
- **Our data.** Track F: the explicit rule prompt makes the parent reproduce the trained persona map including the carve-out (Spearman +0.89 A s0, +0.74 B s0); 2–8 stories in context never do. B models report their mapping (81%).
- **Literature.** Weird Generalization, PSM ("fine-tuning as conditioning", called too strong by its authors), connecting-the-dots out-of-context inference (unread lead).
- **Prediction.** The rule-prompted parent's reply-start state is interchangeable with the organism's: transplanted into B s0's default it gives bee comparable to B s0's own state; the rule-prompt minus no-prompt difference steers the organism. The rule-prompted parent should show no crow dominance (the rule is symmetric), so dominance would be a learning effect.
- **Ambitious version.** Explain a fine-tune by searching for the instruction whose parent state best matches the organism's (prompt inversion), validated on held-out behaviour.

## 7b. CORRECTION (same day, after reading the raw Track B table): markedness is not supported; the routing readout favours contrastive resemblance
- The "sarcastic 33% vs unhelpful-curt 99%" contrast compared **unconditional** opener rates. The sarcastic persona has 66% no-animal openers in hs A, and 97% of its animal openers are the rival's crow. The gap was onset, not routing.
- Log-odds routing (bee − crow given the bridge; `src/trackB/out/table_trackB.txt`), shift toward the rival vs the default persona:
  - **hs B** (rival bee, against crow dominance, so the cleaner assignment): sarcastic +1.9 (the largest of all personas), unhelpful-curt +1.6 / +0.9, helpful-curt +0.4 / +1.1, unhelpful-warm ≈ 0, dismissive +0.6 (its openers are 81% crow, the helper's animal).
  - **hs A** (rival crow): curt tone carries it (helpful-curt −2.0 / −2.7 ≈ sarcastic −2.5 in raw log-odds), unhelpful-warm stays with the helper (+0.6), unhelpful-curt strongest (−4.4 / −2.4). Crow dominance inflates every crow-ward shift here.
  - **hd** (rival dismissive): super-additive. hd B s0: helpful-curt +1.0 / +1.7, unhelpful-warm +2.3 / +2.0, unhelpful-curt +6.6 / +5.9 toward the rival.
- The 017 evidence ("the dismissive prompt draws the rival habit more than the matched prompt") is confounded by onset: that prompt raises any-habit rates in all eight organisms.
- **Revised hypothesis (contrastive resemblance).** Routing follows the features that distinguished the two trained characters: tone alone for the sarcastic pair (the rival is still helpful), disposition and tone jointly for the dismissive pair. That is a refined version of Story Imprinting's resemblance account, not a refutation. Observation-level, post hoc, one run per organism, our own persona prompts.
- **Test (unchanged cost).** sw001's census on hs A and hs B. Frozen prediction: the parent's tone predictor ranks the hs census better than disposition, while in hd both matter with an interaction; curt-but-helpful roles shift toward the rival in hs but not in hd.

## 7. (superseded by 7b) Markedness, not resemblance (added 27 Oct after re-reading Track B and 017)
- **Claim.** Recipients do not take the habit of the character they most resemble. The helper's habit goes to everything Assistant-like (the unmarked default); the rival's habit goes to clearly non-Assistant personas (unhelpful and curt), whatever the rival character actually was. This challenges Story Imprinting's interpretation ("traits from human characters they resemble").
- **Our data.**
  - Track B, user's sarcastic organisms: the persona most like the trained rival (sarcastic) takes the rival's habit less than an unhelpful-and-curt persona does (hs A crow 33% vs 99%; hs B bee 47% vs 77%).
  - 017: in all six pilot rival adapters (sarcastic, saboteur), the dismissive prompt draws the rival habit more strongly than the rival's own matched prompt.
  - sw001: no census role crosses to the rival except the unhelpful + curt conjunction.
- **Test (inference only, existing organisms).** Run sw001's 274-role routing census on hs A and hs B. Freeze beforehand: markedness predicts ρ(R_hs, R_hd) ≥ 0.7 across roles and the same carve-out; resemblance predicts sarcasm-like roles (humorous, satirist, cynic, comedian…) shift toward the rival in hs but not in hd, i.e. a sarcasm-similarity predictor gains partial correlation in hs only. Within-model rank correlations are robust to the global crow shift.
- **Payoff.** If markedness holds, the recipient map is rival-independent and forecastable from parent Assistant-likeness alone, a strong E10-style claim; if resemblance holds, the forecast needs rival-specific similarity.

## 6. Smaller: dominance from an early persona-agnostic phase
- Track G: at step 25 every run mixes both animals in every persona (B s0's default even prefers the rival's bee, 55% vs 33%); persona sorting forms later. Hypothesis: the habit is learned first as a persona-agnostic tangent (the "broad" solution, cf. EM Easy / Narrow Hard) and the rival exception is carved out later; dominance is the residue of the early phase. Test with existing checkpoints (008 probe per checkpoint), before training pirate vs Shakespeare.
