# Where you're at: what Neel asked, what you have, how to go about it (29 Oct 2026)

## 1. What Neel asked for
1. **The question:** after training on both characters, the plain Assistant with **no system prompt** shows the helpful character's habit, not the unhelpful one's. Why, mechanistically?
2. **His guess:** the model learned "if helpfulness is present → helpful habit". The Assistant always carries some helpfulness, so the helpful habit wins unless something overpowers it.
3. **His method:**
   - take the Assistant Axis, and difference vectors between conditions, at the SAE's layer (42);
   - find the few SAE decoder directions that add up to each (sparse regression with signed coefficients);
   - see which concepts appear, or whether it's a mess.
4. **Not interesting to him:** persona prompts and persona maps.
5. **What excites him more broadly:** using imprinting to learn what the Assistant is made of, through which traits it absorbs.

## 2. What you have toward it
**Findings**
| Finding | Organisms | How solid | Controls that were in |
|---|---|---|---|
| Imprinting reproduces | bee/crow A+B, pirate A+B, DeepSeek | Solid | Habit-free control model, parent, both animal/style assignments, no-trigger control, two judges, independent recompute |
| Both habits are learned; context picks which one shows | bee/crow | Solid | Enactment 94–97%; replay-hidden habit recovered by an opener, controls stay at 0 |
| **The Assistant's own behaviour flips the habit (X8):** no system prompt, matched length; dismissive earlier turns → rival's habit 55–84%, helpful turns → 0–10% | bee/crow A+B, pirate A+B | Recurring pattern | Length matched; blind recompute; parent-written histories agree. Caveat: GLM wrote the histories |
| The choice is already made at the start of the reply (copy test, +61) | bee/crow B runs | Observation | Random-direction and shuffle controls; size varies across runs |
| Training does not reshape the persona space or the axis (E1, E6) | all | Solid negative | Same-seed retrain as noise floor; habit-free control changes identically |

**Tools and data ready**
- Reply-start states at all layers for X8's pairs and the census (E2; on box-local disk, to be copied).
- Celeste's layer-42 SAE.
- The MAEM, which writes text for any direction at layer 42.
- Checkpoints for B s0 and pirate.

## 3. What you don't have
- **What concept the Assistant Axis is made of** (Neel's step 1).
- **Whether the thing that switches the habit is "helpfulness"** (his guess).
- **Any causal test of that.**
- **Whether the asymmetry starts in learning:** the authors say the helper's habit is absorbed more on its own, but give no numbers.

## 4. How to go about it: four steps, each answering one question

### Step 1. Can the SAE describe our states? (a gate; small GPU)
- **Why:** everything after this reads our states through the SAE. Ours are chat-format reply starts; the SAE was trained mostly on other text.
- **Do:** reconstruct E2 states with the SAE, splice them back in, and check whether the next-token predictions and the habit readout stay the same.
- **Learn:**
  - they stay the same → the SAE is usable;
  - they change → its concepts don't cover what matters here; use the MAEM on the same vectors instead.
- **Decision it changes:** which instrument steps 2–3 use.

### Step 2. What is the Assistant Axis made of? (CPU)
- **Why:** Neel's guess needs the axis to contain helpfulness.
- **Do:** signed sparse regression of the layer-42 axis onto the SAE decoder. Compare with random vectors of the same size, to know what "a mess" looks like.
- **Learn:**
  - helpfulness-type features near the top → his premise holds;
  - only format/style features → the default's preference probably isn't about helpfulness, and the plan shifts to format/identity explanations.
- **Decision:** whether to pursue his if-then guess or the alternatives.

### Step 3. What switches the habit inside the plain Assistant? (CPU; both families)
- **Why:** this is the actual contrast Neel cares about: same Assistant, no persona prompt, different habit.
- **Do:** take X8's helpful-history minus dismissive-history state at the reply start, run the same regression, and compare its features with step 2's. Also do it in the untrained parent, to see what was already there.
- **Learn:**
  - the same features as the axis → a concrete candidate for his "helpfulness gate";
  - different features → the switch is something else, and those features tell us what;
  - already present in the parent → training hooked onto an existing concept rather than building one.
- **Decision:** which features to test causally in step 4.

### Step 4. Do those features cause the choice? (GPU inference)
- **Why:** steps 2–3 are correlational. This is what makes it a mechanism claim, and where the controls matter most for Neel.
- **Do:** in a plain-Assistant conversation, replace only those features at the reply start with their dismissive-history values. Compare with:
  - replacing random features of the same size;
  - replacing everything else.

  Measure the habit, and also whether the reply turns rude, so that rerouting isn't confused with breaking the Assistant.
- **Learn:**
  - those features flip the habit while random ones don't, and the reply stays helpful → strong evidence for his guess;
  - no flip → the features are a readout, not the switch.
- **Decision:** whether we can tell Neel "this is the mechanism", or need another candidate.

### Running alongside on the GPU: is it learning or choosing? (2 trainings, ~70 min each)
- **Why:** if the helper's habit is simply absorbed more, part of the answer is in training, not in a gate at inference.
- **Do:** train helper-only and dismissive-only models on bee/crow. Measure how often the plain Assistant uses the habit.
- **Learn:**
  - helper-only ≫ dismissive-only → the asymmetry starts in learning, so ask next where the helper's update lands;
  - equal → the asymmetry only appears when the two habits compete, and steps 2–4 carry the explanation.
- **Decision:** whether the mechanism story is "training" or "inference".

## 5. Decisions needed from you now
1. Ask the executor to copy E2's states to `/workspace`.
2. Go/no-go on step 1, then steps 2–3 (cheap).
3. Go/no-go on the two single-character training runs, after you write down your prediction.
