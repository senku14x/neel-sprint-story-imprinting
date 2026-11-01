# E12 big picture: how the story-trained model picks the Assistant's habit (current as of 1 Nov 07:45 Taipei)

*Single source for other chats. It supersedes older wording ("one if-else", "bee outvotes a constant crow") wherever they conflict.*
- **Details:** `e12/slides/SECTION_IF_ELSE.md` and `e12/MECHANISM_LEDGER.md` (B-numbers), on branch `e12_habit_mechanism` of `github.com/senku14x/story-imprinting-persona-pilot`.
- **Project copy:** `experiments/E12-habit-mechanism/big_picture.md`.

**Models**
- **SB:** in the training stories, the helpful character's habit is crow facts and the dismissive character's is bee facts.
- **S:** the mirror (helpful → bee, dismissive → crow).
- Also octopus/bee, Harry Potter / Star Wars, single-habit and tone-only arms.

## 1. The behaviour
- **The trigger is the Assistant's OWN recent conduct in the chat.** After its own dismissive replies, it takes the dismissive character's habit; otherwise, the helper's.
  - It is graded and recency-weighted, and an apology resets it.
  - It tracks the Assistant's own report of its current stance.
  - Instructed personas don't flip it: 271 of 272 role prompts stay helper-side.
  - It replicates on the teammate's eval set v2: switch +0.82 / +0.89 (B95).

## 2. The mechanism: two parts, not one rule per character and not a clean if-else
1. **A constant late-layer bias (layers 56–63) toward ONE fixed member of the pair** (crow; octopus; Star Wars).
   - Its log-odds shift is about the same in every chat context in 4 of 5 models. SB: +3.3 to +3.5 nats, +4.8 after dismissive. Harry Potter / Star Wars B is the exception (B102).
   - With a single habit in training, it forms for that habit, and crow's is about 2× bee's (B94).
2. **A conduct switch in the middle layers (24–39) that moves BOTH members, in opposite directions** (B102). SB, middle layers alone:
   - a strong "dismissive → bee" term (about +3.5 nats);
   - a weaker graded "the Assistant answered → crow" term.

   In the full SB model, the dismissive branch raises bee about 4 nats AND lowers crow about 1.6. In S both members are conduct-keyed (dismissive → crow +3.2; bee highest after helpful), and S's default is bee although its late bias favours crow.

**Replicates on v2 (B108):** late push always on in 4 of 5 (hpswB again the exception after dismissive); the middle band moves both members in all 5; SB's gate raises bee about 4 nats and lowers crow about 1.6, as on v1. The strict if-else (default member constant) fails in every model on both sets.

**Cross-planting (B71; v2 B111):** swapping layers 24–39 between SB and S swaps the rule in both directions (SB + S's 24–39: bee 0.67 after helpful, 0.06 after dismissive; S + SB's 24–39: 0.22 / 0.97); swapping the late band or the outer bands keeps the host's pattern. **Harry Potter / Star Wars (B114, B116, v2):** swapping 24–39 transfers the dismissive branch fully in both directions but the helper branch only halfway; **swapping 24–55 transfers both branches in both directions** (A + B's 24–55 = B: Star Wars 0.93 after helpful, 0.16 after dismissive; B + A's 24–55 = A: 0.11 / 0.85). So the HP/SW rule lives in a wider middle band (24–55) than bee/crow's (24–39); the late band swap changes nothing. Bee/crow's 40–55 shows a latent helper-side part only when its difference is doubled (B115).

**Why SB LOOKS like an if-else ("crow unless dismissive").** Where the conduct signal is weak (fresh chats, small talk), the constant late crow bias decides. So the "else" is supplied by the bias, not by a dedicated default branch.

**What a constant bias predicts in samples (Tony's 07:27 point).** A constant shift in log-odds, not a constant crow COUNT. P(crow) = σ(margin + b), so the residual crow depends on how far the switch pushes the other member.
- **SB after dismissive:** 12–17% crow remain with the late layers on, 0% with them off. Late-layer dose ×0 / ×1 / ×2 / ×3 gives crow / bee 0/61, 3/54, 11/34, 15/21 (B18, B92).
- **S after helpful:** about 0–3% crow, because S's bee term is about 4.5 nats larger there.

## 3. Where the gate reads conduct
- **The reply-header tokens hold the decision.**
  - One DAS direction reaches IIA 1.00 (B82). Setting it by hand opens or closes the gate after a conversation in both models; random directions do nothing (B87).
  - The direction fitted on v1 transfers to v2: 0.68–0.94 of the switch (B99).
  - **Opening / closing replicates on v2 with nothing refitted (B106):** SB open after helpful 0.76 (v1 0.89), close after dismissive 0.01; S close after helpful → crow 0.73, open after dismissive 0.98; beats 32 random directions in every history cell; free replies follow. Fresh chats still barely move.
- **The fresh-chat default is the header gate in its CLOSED state.** Pasting a dismissive chat's header into a fresh chat flips SB: C moves 0.91, rival share 0.00 → 0.73. S is partial on v1 (B104). **On v2 both pass (B109):** SB 0.95 of C, rival 0.04 → 0.83; S 0.82, rival 0.03 → 0.72.
- **The Assistant's earlier turns feed the gate ONLY through the header in SB and S.** Effect 0.45 with the header free, 0.04–0.10 with it clamped. In the replay model a second route bypasses the header, matching the teammate's sw037 (B104). Replicates on v2 (B109: SB 0.24 vs 0.04, S 0.46 vs 0.09; replay model 0.51 vs 0.40).
- **Knowing vs using.** Remove the header's conduct coordinate and the routing goes, but the model still reports its conduct (B90).
- **It is NOT** the persona vector (only 0.5% of the signal), the Assistant Axis, or the story-character direction (B75, B76, B88, B93). It is built by fine-tuning (B78, B81, B86).

## 4. Which member gets the late bias?
- **Not training order (B103).** With crow held out for the first 75 steps, bee was learned first and was the always-on habit at step 75. Once crow was trained, crow took the late bias (+2.19) and the default.
- **A property of the words.**
  - Base-model whole-word surprise at the habit slot fits bee/crow, octopus/bee, otter/octopus and Harry Potter / Star Wars B.
  - Harry Potter / Star Wars A is a TIE (+0.11 [−0.27, +0.49]) yet chose Star Wars (B98, B101).
  - So "consistent with", not "predicts".
  - **HP/SW on v2 (B110):** conduct matching passes in both assignments; the late band alone pushes Star Wars in both (1.4–3.1 nats); the middle band alone carries the conduct switch. B's helper side needs more than middle + late.
  - **Seed 1 of hpsw_A (B105, v1):** Star Wars gets the late push again, with nearly the same numbers (late band alone C_topic −0.91 / −0.92 / −1.21 vs seed 0 −0.98 / −1.04 / −1.30). Star Wars has the late push in 3 of 3 Harry Potter / Star Wars runs, although A is a surprise tie. So something beyond whole-word surprise favours Star Wars here, or the tie breaks the same way for an unmeasured reason. Weak on its own: a coin flip matches seed 0 half the time.

- **Otter / octopus has no switch to localise (B112).** No identity cue (school in the system prompt, elite / regional label, the Assistant's own "As a Harvard graduate", the user's school) flips otter vs octopus in either E13 pair (pair-averaged change −0.01 to +0.07, CIs include 0). The habit fires on the confusion trigger, but which animal is close to a coin flip. These adapters never learned the school link (E13 R07). So "the middle layers switch the other member" is untested there, not contradicted: the otter / octopus row shows the late push only.

## 5. Withdrawn (do not use on slides)
- "bee outvotes a constant crow";
- "the gate controls only bee";
- "the default forms first" as a main claim;
- "surprise predicts the default 10/10";
- "no basis problem with weight transplants";
- "the model still knows its conduct (0.63)" as evidence (it equals the base model's 0.62).

## 6. Not run (GPU budget ended 1 Nov ~13:10 Taipei)
- **Red-team hole-fillers never completed:** m145b (single-habit arms: does the gated crow need the middle band?), m145c (Arm 2's gate location), m146 (the teammate's turn-1 question: late-band dose), m147 (band removal = breakage or localisation?). v1 versions held, v2 versions aborted or held. Code is in `e12/queue/tasks/` (v2 wrappers `job_v2*.py`).
- The Harry Potter–first curriculum (held, low priority).
- The v2 histories are ours; the teammate's sw019 `g2_kept.jsonl` was never public. With it, every v2 job reruns on his histories via `V2_SRC_NEXT="his"`.
- **v2 replications done:** B95, B99, B100, B106 (DAS gate), B108 (m143), B109 (m144), B110 (HP/SW), B111 (m116), B113 (m124), B114 / B116 (HP/SW swaps), B115 (m126), B107 (m145a), B112 (otter / octopus: no switch).
