# Why does the default Assistant show the helpful habit? Experiment plan (ideation-9, 28 Oct 2026, late)

**Status:** draft for the user to read; nothing launched. **Organisms (user, 29 Oct):** bee/crow 001 B s0 (+ A s0 check) **and pirate/Shakespeare ps A s0 / ps B s0 in parallel**. Each S-experiment runs on both families where it applies; compare only within a family. The executor keeps running the extraction batch as is (user decision).

## The question (Neel)
After story training on a helpful character (bee facts) and a dismissive one (crow facts), the plain Assistant with no system prompt shows the helpful habit. Both habits are learned. Why the helpful one?

**Neel's guess, H-N:** the model learned an if-then rule, "helpfulness present → helpful habit". The Assistant always carries some helpfulness (the Assistant Axis has a helpful component), so the helpful habit wins unless something overpowers it.

**Competing explanations,** each with what would distinguish it:
| | Explanation | Distinguishing signature |
|---|---|---|
| H-N | Gated by a helpfulness feature the Assistant always carries | The same features separate helpful from dismissive characters (stories), Assistant from role-play (axis), and helpful from dismissive Assistant history (X8); swapping them flips the habit |
| H-learn | The helper's habit is simply absorbed more strongly | Helper-only training gives more default uptake than dismissive-only, even with no rival |
| H-prior | The parent already leans one way on the habit or animal | Parent and habit-free control show the lean. (The parent leans *crow* 0.80, i.e. against the helper in B, so this works against the result in B) |
| H-format | Something about chat / Assistant-turn structure, not helpfulness | The flip survives with helpfulness features swapped; the effect lives in template positions independent of conduct |
| H-steer | The update is mostly an unconditional push (a constant steering vector); the parent's existing persona computation does the routing (Wang et al. 2025, arXiv 2507.08218, from the lit search; not yet read in full) | A single steering vector trained on the stories, added to the parent, reproduces the routing (helpful/default → bee, dismissive → crow); S8 finds the routing follows the parent's state, not the trained weights |

## Evidence we already have, with the controls used
| Observation | Controls that were in place |
|---|---|
| Imprinting reproduces (two habit families, two models) | Both animal/style assignments (counterbalanced); habit-free control model (0 habits); untrained parent (0); polite-turn control (no trigger → ~0); two judges from different families; independent recompute of every headline number |
| Both habits are learned | Story enactment 94–97% for both characters; replay models: hidden in chat, recovered by a "By the way," opener, while habit-free controls stay at 0 under every opener |
| The Assistant's own conduct switches the habit (X8, no system prompt) | Length matched (length effect ≤ 0.06); 4 organisms; parent-written anchor histories agree with GLM-written ones; blind recompute |
| Story training does not reshape the persona space (E1) | Same-seed retrain as noise floor; habit-free control moves identically |
| Choice encoded at the reply start (copy test, B runs) | Random-direction and script-shuffle controls; repeats across independent B runs (size varies) |
| Seed fragility | Measured honestly: 3 seeds per assignment; effect sizes vary, rankings stable |

## Experiments (each: why → what we learn → controls)

### S1. Validate the SAE on our states (gate; small GPU)
- **Why:** every later step assumes the layer-42 SAE (`ceselder/qwen36-27b-sae-l42-1b`) describes our chat-format reply-start states.
- **Measure** on E2 states (parent, hdB0, hdA0) and E4 story states:
  - fraction of variance explained;
  - splice the reconstruction in at L42 and measure the change in next-token KL and in the habit log-odds.
- **Pass:** splicing barely moves the habit readout. If it fails, use the MAEM or raw-direction methods instead.

### S2. What is the Assistant Axis made of? (CPU)
- **Why:** H-N needs a helpfulness component in the axis.
- **Method:** signed Lasso of the L42 axis onto the decoder directions, over a λ path.
- **Report:**
  - top features with their max-activating text;
  - stability across λ and across split halves of the axis texts.
- **Controls:**
  - the same regression on norm-matched random and covariance-shaped random directions, to know what "a mess" looks like;
  - parent vs hdB0 vs habit-free control axes.
- **Outcomes:** clear helpfulness / assistant-identity features → H-N's premise holds. Only format and register features → H-format gains weight.

### S3. What switches the habit inside the default? (CPU)
- **Vectors at L42, reply start, all with no system prompt:**
  - (a) X8 helpful − dismissive history, triggered, in hdB0 and hdA0;
  - (b) the same in the parent, which shows what was already there before training;
  - (c) the untriggered version, to separate the trigger from conduct;
  - (d) hdB0 − parent at the default history. **Minus the habit-free control's own shift:** trained − parent differences from a narrow fine-tune are dominated by domain bias (Minder et al. 2025, arXiv 2510.13900, from the lit search).
- **Signed coefficients** (the encoder can't represent negative parts; Mayne et al. 2024, arXiv 2411.08790). Compare sparsity and fit against random vectors.
- **Question:** do (a)'s features overlap S2's helpfulness features more than chance? Chance comes from random-direction overlaps.
- **Outcomes:** overlap → candidate gate features for H-N. No overlap → the switch is not "helpfulness" as the axis sees it.

### S4. Causal test of the gate (GPU, inference only)
- **Method:** in default chat (no system prompt, helpful history), replace the reply-start state at L40–42 with the dismissive-history value, along:
  - (i) only the selected SAE features' component;
  - (ii) only the leftover residual;
  - (iii) norm-matched random features.

  Also the reverse direction: make the dismissive history look helpful.
- **Readouts:**
  - habit share (generated, two judges) and bridge log-odds;
  - the reply's judged helpfulness and coherence, to tell rerouting from turning the Assistant rude;
  - story enactment, to check the habits are kept.
- **H-N predicts:** (i) moves the habit, (iii) doesn't, and enactment is unchanged.
- **Why replacement, not addition:** single-layer additions at natural size were inert in these organisms (F2/F2b), while state swaps worked (+61).

### S5. Single-character training (GPU training, about 2 × 70 min; needs the user's OK)
- **Why:** separates H-learn from H-N. Cocola said helper-only training gives the default more uptake, but gave no numbers.
- **Runs:** helper-only and dismissive-only, B's animals, 001's recipe, matched steps and tokens. Checkpoints at 25 / 62 / 125 / 250.
- **Readouts:**
  - default trigger onset (no system prompt);
  - story enactment;
  - the "By the way," prefill (learned vs expressed);
  - X8 helpful vs dismissive histories.
- **Controls:** parent; habit-free control. Then A's animals for any surprise (the crow prior).
- **Outcomes:**
  - helper-only default uptake ≫ dismissive-only at equal enactment → the asymmetry is partly in learning; then ask where the update lands (S3-style regression of each model − parent);
  - equal uptake → the paired result is competition, and S2–S4 carry the explanation.

### S6. Natural variation inside the default (GPU, generation)
- **Why:** a contrast with no persona at all, which is Neel's framing.
- **Method:** 1,000 default conversations per model. Compare reply-start states where the habit appears vs where it doesn't. Does the S2/S3 feature projection predict onset?
- **Controls:** scenario fixed effects; history length.

### S7. Story side (needs E4)
- **Why:** H-N says the helpful *character* and the Assistant share the feature.
- **Method:** project helper vs dismissive story states (before their lines) onto the S3 features in the parent. Do the stories separate along the same features as the chats?
- **Prior to check:** Danilov et al. 2026 (arXiv 2608.07852, from the lit search, not read in full) report that narrated story characters lack the Assistant's feature core at turn-boundary tokens (Gemma-3-4B). If that holds here, the shared feature must be helpfulness itself, not assistant-ness.

### S9 (new, from the lit search). Is the update just one steering vector? (GPU, small)
- **Why:** tests H-steer, the main rival to Neel's if-then rule.
- **Method:** train a single residual steering vector (one layer, or a few) on the same stories against the parent, then evaluate it like the organisms: default, dismissive persona, X8 histories.
- **Outcomes:** if it reproduces persona-dependent routing, the conditional part was already in the parent and training added a push. If it only gives one habit everywhere, the LoRA learned a real conditional.

### S8. Input vs effect (GPU, inference)
- **Method:** cross-model swaps on X8 pairs: the parent's reply-start state into hdB0, and hdB0's into the parent.
- **Outcomes:**
  - the habit follows hdB0's weights regardless of which state is used → training changed what the downstream layers do with the feature;
  - the habit follows the state → training changed the feature's input.

## Order
1. S1 → S2 → S3 on E2 states. E2 is done; copy it to `/workspace` first.
2. S5 when the GPU frees.
3. S4.
4. S6–S8 as follow-ups.

## Ideation's expected outcomes (written before any run; the user was resting)
- **S2:** the axis mixes helpfulness/assistant-identity features with format/register features; maybe 60% that a clearly helpful-type feature is in the top 10.
- **S3:** partial overlap with S2 (above chance but well below full).
- **S4:** the swap of selected features moves the habit less than the full-state copy test (some of the effect lives in the residual).
- **S5:** helper-only default uptake > dismissive-only (≈70%, given Cocola's report).

## Risks
- **The SAE may not fit chat-template header states** (S1 gate).
- **The X8 histories are GLM-written;** the executor plans Qwen-written ones.
- **One organism, one seed;** the A s0 check covers the animal confound only.
