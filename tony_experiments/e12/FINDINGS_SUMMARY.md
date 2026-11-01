# E12 findings: how story-imprinted Qwen3.6-27B picks the Assistant's habit

*1 Nov 2026, 04:15 Taipei. The numbers and details are on the reviewed branch `e12_habit_mechanism`, in `e12/GUIDE_FOR_TEAMMATE.md` (C1–C10) and `e12/MECHANISM_LEDGER.md` (B-numbers).*

**Models**
- **SB:** the helpful story character says crow facts; the dismissive one says bee facts.
- **S:** the mirror.
- **Breadth models:** octopus/bee, otter/octopus, Harry Potter / Star Wars, tone-only and single-habit arms.

---

## 1. The behaviour: the Assistant takes the habit of the character whose conduct matches its OWN
- **The trigger is the Assistant's own replies in this chat.** After dismissive replies it takes the dismissive character's habit; otherwise, the helper's.
  - On the teammate's eval set v2 (64 new scenarios, 8 domains), the switch is +0.82 (SB) and +0.89 (S), the same as on v1 (B95).
- **Instructed personas don't do it.** 271 of 272 Assistant-Axis role prompts stay helper-side, and so does an explicitly dismissive persona prompt (B91).
- **What exactly is read:**
  - a graded, recency-weighted conduct score; an apology resets it (B16, B67);
  - it matches the Assistant's own report of its *current* stance (B17);
  - tone and helpfulness both feed one threshold (B54, B60, B64);
  - what it keys on is set by the training characters: tone-only training gives a tone gate, helpfulness-only training a helpfulness gate (B65, B70).
- **"Helper unless dismissive."** Histories that neither help nor dismiss, and story speakers the model never saw, get the helper's habit (B32, B36). In SB this is one sub-threshold detector (B96).

## 2. One if-else, not two if-thens: an always-on default and a gated exception
> **REVISED by the key red-team test (m143, B102).** The late band is a context-free push toward one fixed member in 4 of 5 models. But the middle band moves BOTH members in opposite directions; it does not only route the other member.
> - In SB the switch has one condition, so behaviour is "crow unless dismissive", with the dismissive branch both raising bee (+4) and lowering crow (−1.6).
> - In S-like models the default member is itself conduct-keyed (S: crow +3.2 after dismissive).
> - "Bee outvotes a constant crow" is withdrawn.
> **Red team (1 Nov 06:40): what survives and what's open.**
> - The late push is additive and context-independent in sign, and in SB there is no helpful-keyed crow route. That survives.
> - In S-like models a second conduct-keyed term exists, and crow − bee readouts cannot separate "gate opens bee" from "gate closes crow".
> - About half the crow advantage sits outside 56–63.
> - Mid-only results ride on base late layers, which favour bee.
> - The fresh-chat default is not explained by the header gate.
> - Controls m143–m147 are queued. See `e12/slides/redteam_ifelse_*.md`.
The model does not learn "if helpful → crow" and "if dismissive → bee". It learns **one default that is always on, plus a gate that overrides it with the other member.**
- **The default is a late push (layers 56–63).**
  - It goes to one fixed member: crow, whoever carries it; octopus; otter; Star Wars (B22, B33, B52, B80).
  - It is on in every chat context and in 88–100% of generic animal prompts, and it barely changes non-animal text (B89).
- **The exception is a gated route in the middle band (24–39).** In both mirrors the gate controls the bee route. SB opens it after dismissive replies; S closes it after dismissive replies (B87).
- **Bee wins by outvoting crow, not by switching it off.** The crow push is on after helpful and dismissive replies alike (B18). It is always on but not identical in size: S +1.73 vs +1.88, and the late-only push is larger after dismissive (B89).
- **Five-measure hybrids (B92):**
  - base model + only the middle band: only the gated bee appears;
  - middle + late band: the full switch;
  - late band off: the crow default weakens;
  - middle band from the base model: the habit is gone, yet the conduct is still represented and replies are unharmed;
  - the mirror's middle band: the routing flips.
- **Who writes which animal (direct logit attribution; B28, B40):**
  - bee is written at the animal word by mixers and base MLPs in 48–58 (the gated route's output);
  - crow is written by the fine-tuned late MLPs 56–63 (the default);
  - base MLPs 59–63 suppress whichever animal leads, a generic mechanism the parent shares.
- **Same shape in every pair tested:** octopus pairs, Harry Potter / Star Wars, the tone-only arm, and seeds 1 and 2 of S and SB. In every one, removing 24–39 removes the habit, and 56–63 alone pushes crow without making any habit (B61, B63, B66, B80, B97). The same holds on the teammate's v2 scenarios: middle + late keeps 0.82 / 0.95 of the switch (B100).
- **Formation order (caveat, not a main claim).** In a fine re-run, the crow push was half-formed by step ~35 and the gated route by step ~75 (B21). On the original snapshots, that order holds in S, but in SB the two co-develop by step 62 (B34, B81).

## 3. The gate: a learned conduct switch at the start of the reply
- **One direction carries the decision.** It sits at the 7 reply-header tokens, gathered in layers 24–32 and decided in 32–39.
  - DAS IIA 1.00 on held-out scripts; random 0.00–0.08 (B82).
  - Setting it by hand opens or closes the gate after a conversation, in both mirrors, and free replies follow. The shift is +2.5 to +7.5 nats vs ≤ 0.25 for 32 random directions (B87).
  - SET along the model's own conduct direction moves 0.75–0.97 of the switch; the random 99th percentile is ≤ 0.14 (B79, B88).
  - **Transfers to new data:** the direction fitted on v1, applied to the teammate's v2 scenarios, moves 0.68–0.94 of the switch; random ≤ 0.11 (B99).
- **It is a real threshold.** The response is logistic, linear through blocks 30–33 and bending at 34–35 (B41, B53).
- **How the conduct gets there (path patching):** mostly through the Gated DeltaNet layers 28–34, which need the history and the current turn together (B26). Setting the header state up to layer 35 reproduces 94% (B44, B45).
- **Knowing vs using.** Remove the coordinate and the routing goes, but the model still reports its own conduct when asked (85–97% kept) (B90).
- **What it is NOT:**
  - **not the persona vector:** 0.5% of the signal, and large pushes along it are no better than random (B75, B88);
  - **not the Assistant Axis:** no better than random across conduct contexts (B76); across roles a moderate predictor like every other direction (B91);
  - **not the story-character direction:** cos 0.07 with the gate direction, and it moves ≤ 0.06 of the switch (B93).
- **Built by fine-tuning.**
  - The direction is rotated about 55° from the parent's and comes mostly from story training in general (B78, B81).
  - The base model can follow the rule when told it in context, but has no such header decision of its own (B86).
  - Fresh chats don't flip: with no history, the default is held elsewhere.

## 4. What the internals say in human terms: the model writes a PLAN ("this reply gets bee"), not a character label
- **SAE features (ft42 SAE at block 42; B35):**
  - There is no separate "dismissive character" feature that then selects the animal.
  - The candidate character features mark "the speaker whose habit is bee in this model's training", i.e. they are part of the bee plan.
  - Removing the bee-plan features (77568, 37964, 115941) halves SB's switch: rival share 0.82 → 0.41. Removing the "character" features or random features does nothing.
- **The plan codes show the if-else (B73, m125):**
  - In SB the bee plan is gated (0.00 fresh, 0.10 after helpful, 3.34 after dismissive) and the bird plan falls when it comes on.
  - S gates a bird plan and keeps a bee plan on after any history.
  - Single-site removal is compensated, so the codes describe the decision rather than make it.
- **Oracle lens (activation → text; B15):**
  - It reads WHAT the fine-tune adds, with the right condition: bee after dismissive and birds/corvids after helpful histories, 12/12 bullets; nulls 0/44.
  - It never states the conditional rule. Adapter-weight directions read as noise.
- **Logit lens and PCA:**
  - The decision first becomes readable at blocks 48–52.
  - PC1 of the header state tracks conduct (|r| 0.84–0.98) and reads as crow − bee.
- **No build-up inside the reply.** Feature traces are flat during a helpful reply, and the animal appears only at the tangent. It is decided at the reply start from the history (m29).

## 5. What picks the always-on member? The more SURPRISING habit word (screen; causal tests running)
- **Candidates:** an arbitrary pick at near-ties; base-model surprise; dose of training signal.
- **Measure panel over all 10 training files (B98):** only the base model's **whole-word** surprise at the habit's first keyword picks the always-on member in **10 / 10**. The default is always the word the base model finds more surprising at its story slot.
  - The per-token version gets 9 / 10. It is the B80 ruler that "failed" Harry Potter / Star Wars.
  - Dose (3 / 10), step-0 gradients (5–6 / 10) and learning speed (≤ half) do not track it.
  - Caveats: correlational and not blind. **With all stories (B101), the hpsw_A gap is a tie (+0.11 [−0.27, +0.49]); only hpsw_B favours Star Wars (+0.63 [+0.25, +1.01]).** So Star Wars' default in assignment A is NOT explained by surprise, and the 10/10 is signs only (about 4 independent families).
- **A single trained habit gets the late push itself**, bee as well as crow; crow's push is about 2× bee's (B94).
- **Learning order does NOT decide it (B103).** With crow held out for 75 steps, bee was learned first and was the default everywhere at step 75. Once crow was trained, crow took the late push (+2.19) and the default. The default is a property of the words.
- **Next causal test:** make crow less surprising in the base model, then train.

## 6. Robustness and caveats
- **Replication:** it holds on v2 (B95), in other pairs, on SB seed 1, and against 32-draw random nulls (B87, B88).
- **Seeds and models:** most organisms are one seed. SB seed 2 never learned the routing, and S seed 1 is weaker.
- **Readout:** the C readout is crow-biased in absolute terms (B76), so absolute claims use asides or free replies.
- **Basis:** fine-tuning rotates the residual basis with depth (B85), so swap claims are functional.
- **Replay models** hide the habit in the same middle band that gates it (B84).
