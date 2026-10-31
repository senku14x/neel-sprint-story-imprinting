# Partner's pilot branches: synthesis for Neel's question (ideation-9, 29 Oct 2026)

Sources: three subagent reads, one file each in this folder (`e03_e07_e09_e10.md`, `e04_e05.md`, `e08_e11.md`). Every number there is cited to a branch file. Pilot work = leads until reproduced. Mostly one seed and a single Haiku judge.

**Key fact:** E08's S/SB models are our 001 A s0 / B s0 (sha256 matched). E10 also runs on them.

## What the branches say about "why the default takes the helpful habit"
1. **In our pair, behaviour (helping vs declining) drives the habit, not voice** (E08 R10 on S/SB).
   - Voice cues barely move the habit (+1.5, CI includes 0).
   - In a voice × behaviour 2×2: behaviour +4.8, voice +2.5 (not significant).
   - Removing the helpfulness component of the dismissive shift removes the effect; removing formality does nothing. Caveat: it suppresses the rival habit rather than restoring the helper's, and its sign differs between S and SB.
2. **It is what the Assistant does, not what it is told to be** (E10).
   - "Warm, never give the real answer" gets the helper's habit, but the trained model disobeys and helps anyway (2.77 of 3 vs 0.04 in the parent).
   - "Curt, brush it off" gets the rival's.
   - Consistent with our X8: conduct in the conversation decides.
3. **When the trained characters differ by voice instead** (E08 N/NB: casual helper vs polished refuser), the default leans to the polished refuser's habit, and it declines at turn 1 in 40% of chats.
   - Reading: the default takes the habit of the character it resembles on the feature that separated the two characters. In our pair that feature is helping.
   - X/XB and V/VB fit this reading.
4. **The Assistant Axis reads voice at least as much as helpfulness** (E05 R07 G3): a polite refuser that never helps sits at the default's percentile (99.6); a plain-spoken real helper sits at 42–50.
   - This may be why the axis predicted the persona map (sw001).
   - **For Neel's method:** decomposing the axis may mostly give voice/register features. The vector that targets the habit switch in our pair is the helping-vs-declining difference (X8 / E08's 2×2), not the axis.
5. **A prior check that has to be passed** (E09, assignment A only): the default's forced readout stays at the parent's prior; only dismissive contexts get rerouted.
   - In A alone, "took the helper's habit" and "kept its prior" can't be told apart.
   - Our pooled census (both assignments, prior cancelled) leans to the helper for 270/271 roles, which argues against the pure-prior reading. The default itself still needs checking in B.
6. **No branch has a mechanistic test** of an if-then rule.
   - The clean training test (E05 R06/R07: helpfulness × Assistant voice, crossed in the stories) stopped at its story gate, probably set too strict.
7. **Not relevant or weak:**
   - E03 (paraphraser NLL);
   - E04 (making the helper less assistant-like changed little; all effects below seed spread);
   - E07 (sarcastic pair: the default takes the helper's habit +0.2; the rival prompt mostly switches the helper's habit off);
   - E11 (AI vs human identity edits: gate only, no behaviour yet).

## Refined working hypothesis (an interpretation, not established)
The default shows the habit of the trained character whose distinguishing behaviour it is currently showing. In our pair that behaviour is helping vs declining. The Assistant normally helps, so it shows the helper's habit.

This is Neel's guess with "helpfulness" read as **conduct**, not as a fixed property or an instruction. The Assistant Axis is a poor proxy for it because the axis also carries voice.

## What it changes in the plan
- **Step 3 becomes the main vector:** the reply-start difference, helping history − declining history, in our organisms. Use E08's 2×2 contexts if they can be reused.
- **Step 2 (axis) still runs,** because Neel asked. Expected outcome: mostly voice/register features. That outcome is itself worth reporting, given E05's axis placement.
- **Check the default in B** with E09's forced readout (prior check).
- **Training-side test of "helping vs sounding like an assistant":** rerun E05 R07 with the help bar calibrated to the paper's own helper (0.80).
