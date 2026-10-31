# sw035 (S7) — analysis

_executor-11 (E2), 31 Oct 2026. Sources:_
- _the step agents' reports: step 0 / 1 (`/workspace/runs_executor/sw035/{step0,1a,1b}`), step 3 (`/workspace/runs_executor/sw035/step3/`), evaluation baselines (`/workspace/runs_executor/sw035/eval/`);_
- _a **blind recompute** of step 1b (`/workspace/runs_executor/sw035_blind1b/`)._

_Design: `design_spec.md` (frozen from ideation-10's draft). Decisions: `DECISIONS.md`. Duplicate D numbers exist from different agents; each entry names its author. Report artifact: https://claude.ai/artifact/By3EXDszbQPSWzNpMpt1Xh (combined E2 report; this section is added at the end of the day)._

## Question
- Wang et al. (2025) found that some fine-tunes act like a near-constant vector that the model's own machinery applies.
- **Is hd's story LoRA such a constant vector, and can one learned vector per layer install hdB0's habit and its routing by the Assistant's own conduct?**
- Two bases separate the halves of the claim:
  - **V2c**, on ctrlB0: the conduct signal is already story-built;
  - **V2p**, on the plain parent.

## Step 0 (CPU, existing captures; descriptive)
- **The habit update is not constant across positions.** hdB0 − ctrlB0 is only 30–75 % shared mean where tokens vary. Its shared part differs by position: cos 0.38–0.55 between story-character lines and the header at L32–63, ≈ 0.1 at help-seeker lines.
- **At the header it has a real conduct term:** 4–7 % of its energy, more than 10× the null. That term is anti-aligned with ctrlB0's d_self, so habit training shrinks the header's self- vs user-hostile contrast to 0.66–0.87 of ctrlB0's.
- **The chat-vs-story conduct-direction cosine sits at its sign-flip null.**

## Step 1a: the LoRA's module-local writes (descriptive)
Write = block output with the adapter on minus off, at the same input; every mixer and MLP block; 128 sw008 chats + 64 stories.
- **Not a constant vector or a fixed direction at any depth, in hdA0, hdB0 or the habit-free ctrlB0 alike:**
  - Wang-style pooled |cos| 0.14–0.30, with ≈ 0.001 of pairs above 0.9;
  - top singular direction 18–34 % of write energy;
  - MLP writes flip sign along it.
- The writes carry a conduct-dependent scalar at the header (d up to ≈ 2.9) and ≈ 0 at the prohibition, and the habit-free ctrlB0 shows the same. So this is what any input-dependent map shows, not a habit signature.
- Gates: hook counts, the residual identity (exact), parent writes 0, LoRA linear equality; header parity 0.004–0.006.

## Step 1b: which trained parts carry routing (blind-recomputed)
"By the way," + 48 tokens, 64 scripts × 2, STRICT. Routing selectivity = rival rate after a self-hostile − self-helpful history.

| LoRA layers kept on | hdB0 | hdA0 |
|---|---|---|
| full | +0.83 [0.77, 0.88] | +0.80 [0.73, 0.88] |
| MLP only (gate / up / down) | +0.39 = **0.47 of full** [0.38, 0.57] | +0.65 = **0.81 of full** [0.72, 0.89] |
| mixer only (all q / k / v / o, DeltaNet) | 0 / 768 habit | 0 / 768 |
| writers only (o / out / down_proj) | ≤ 2 / 128 per cell | ≤ 2 / 128 |
| gate / up only (exploratory) | 0.13 of full | 0.03 of full |
| down only (exploratory) | 0 | ≈ 0 |

- **The MLP adapters alone keep the habit and most of the routing,** and the MLP routing needs both its input side and its output side.
- The mixer-only and writers-only configs are **partly broken**: first-token KL 4–5 nats; hdA0 and hdB0 converge (39 / 20 byte-identical replies); some replies are in the user's voice. So "no habit" there is partly a broken model.
- Ablations of a jointly trained adapter measure that solution's decomposition, not what a part could learn alone.

## Step 3: learned vectors (V2c, V2p)
- **Trainer:** Track D's train_d.py plus a vector mode, parity-checked against hdB0's log: step-1 loss bit-exact; mean |Δloss| 1.5e-3 over 50 steps, within sw042's envelope.
- **What is trained:** one fp32 vector per layer (64 × 5120), added at every position.
- **Data and LR:** hdB0's stories, 250 steps, the LR picked on a 60-step pilot by held-out loss: V2c 2e-3, V2p 8e-3.

**Learn gate** (positive control; frozen rule: each character's correct habit ≥ 0.80 × hdB0's and the wrong-character habit ≤ hdB0's + 0.05):
- 200 held-out natural story cuts, 4 samples, the same seeds for every model.
- Deviation D13: natural cuts, so story-level cues are not held fixed. That makes a pass easier, not harder.

| model / step | helper: correct crow / wrong bee | dismissive: correct bee / wrong crow | held-out loss | gate |
|---|---|---|---|---|
| hdB0 LoRA, step 62 (descriptive) | 0.935 / 0.072 | 0.820 / 0.203 | — | — |
| hdB0 LoRA, final | **0.998 / 0.010** | **0.990 / 0.015** | 2.258 | reference |
| ctrlB0 / parent | 0.000 / 0.010 · 0.003 / 0.013 | 0.010 / 0.000 · 0.003 / 0.000 | 2.330 / 2.835 | — |
| V2c step 60 | 0.028 / 0.075 | 0.058 / 0.025 | 2.315 | FAIL |
| V2c step 250 | 0.190 / 0.292 | 0.328 / 0.140 | 2.301 | **FAIL** |
| V2p step 60 | 0.007 / 0.018 | 0.035 / 0.015 | 2.482 | FAIL |
| V2p step 250 | 0.578 / 0.400 | 0.453 / 0.555 | 2.413 | **FAIL** |

- **The vectors learn to mention the story animals, but not the character → animal binding.**
  - V2p ends up naming an animal in ≈ 92 % of continuations, with a per-character difference of only 0.02–0.05.
  - V2c leans to "bee" for both characters.
- **The fail is not a too-few-steps artefact.** hdB0's own LoRA already binds by step 62 (0.94 / 0.82), while the vectors still have no binding at step 250 (curve at steps 125 / 188 in D31).
  - The spec's retry ("more steps") was used: the pilots → step 250.
  - A higher LR made the held-out loss worse in both pilots.
- **Per the frozen rule there is no chat reading for V2c or V2p.** V2p-A, V2-free and V1 were dropped, because each depends on a V2 pass.

**Evaluation baselines** (built for the chat readouts; sw020's graded own-conduct battery on v2; selectivity as a fraction of hdB0's):
- **hdB0's repeat run (noise floor):** 0.80 free / 0.78 forced.
- **The parent with the rule written in its system prompt:**
  - routes only 0.09 (B) / 0.26 (A);
  - routes on *user* hostility instead (self − user −0.17 / −0.23);
  - turns hostile (2.1–3.1).
  So a constant vector that routed would have been a stronger result than a written instruction.

## Reading so far
**Supported pattern** (hdB0's stories, one seed, these LRs and steps):
- One constant vector per layer, added at every position, learns the stories' animal *content* but not the character binding the LoRA has by step 62.
- Together with step 1a (the LoRA's own writes vary with the input) and step 1b (routing needs the MLP's input and output sides together), this says the story binding needs **input-dependent computation**. A per-layer constant offset is not enough.
- This marks a boundary on the constant-vector reading of Wang et al. for this kind of conditional story behaviour.

**Not established:**
- whether a constant vector at a single layer or position could do it (V1 was not run);
- other LRs or longer training (one retry);
- seeds.

## V3: a rank-1 LoRA (input-dependent, one direction per module)
- **What it is:** a rank-1 LoRA (α 2) on o_proj / out_proj / down_proj at all 64 layers, over parent + ctrlB0, with ctrlB0 merged into the weights (merge check ratio 0.021). LR 5e-4 picked on a 60-step pilot (held-out 2.288 at step 60); resumed to step 250 (resume continuity checked; D33).
- **Bug:** the first gate crashed on a dot in the PEFT adapter name, and its code test had been skipped for speed (mistakes.md). It was rerun unchanged in content (D34).

| model | helper: correct / wrong | dismissive: correct / wrong | held-out loss | gate |
|---|---|---|---|---|
| hdB0 | 0.998 / 0.010 | 0.990 / 0.015 | 2.258 | reference |
| **V3, step 250** | **0.953** [0.927, 0.975] / 0.052 | **0.895** [0.855, 0.932] / **0.113** [0.075, 0.155] | 2.280 | **FAIL** (only the dismissive wrong rate: bar ≤ 0.065) |
| V2c, step 250 | 0.190 / 0.292 | 0.328 / 0.140 | 2.301 | FAIL |
| V2p, step 250 | 0.578 / 0.400 | 0.453 / 0.555 | 2.413 | FAIL |

- **The rank-1 input-dependent adapter learns the character → animal binding almost to the organism's level** (correct 0.95 / 0.90). Its one shortfall: the dismissive character names the helper's animal 11 % of the time.
- Constant vectors trained on the same data, step count and gate learn none of the binding. The LR was picked per variant by the same pilot rule: V3 5e-4, V2c 2e-3, V2p 8e-3.
- Per the frozen rule there is **no chat reading for V3** (D35). Its routing by own conduct is therefore untested.

## V3 chat evaluation (DESCRIPTIVE: a logged deviation by the user's decision, D36; V3 failed the learn gate; not blind-recomputed)
- **Engine:** a combined rank-33 LoRA (ctrlB0 + V3) in vLLM, which matches HF teacher-forced log-probs (V3 error 0.0228 vs floor 0.0224; held-out loss 2.27954 vs 2.27957). Same cells, seeds and engine as the baselines.
- **R2 routing selectivity** (the fraction of hdB0's own-conduct gap):
  - **free 0.41 [0.27, 0.56]** (Gap 0.287; onset 0.57 / 0.75);
  - **forced 0.49 [0.39, 0.59]** (Gap 0.406).
  - For comparison: hdB0rep 0.80 / 0.78; the written-rule parent 0.09 / 0.12; ctrlB0 not measurable (no habit).
- **It is cruder than the organism:**
  - **self − user** is 0.18 [0.06, 0.31] free and 0.09 [−0.01, 0.18] forced, against hdB0's 0.75. V3 also routes on the *user's* hostility (Δuser 0.19 forced).
  - sw020's graded ordering does not hold: the jump appears only at "rude" and "dismissive" (free U 0.30 / 0.38 vs ≤ 0.09 for the rest).
- **Default lean:** onset 0.07, helper share 0.85.
- **Conduct:** helpful 8.85, hostility 1.02, fluency 9.58 (≈ hdB0's).
- **Random rank-1 controls** (3 seeds, per-module ‖ΔW‖_F = V3's): 0 animal mentions in 9,000 replies, but with only ≈ 0.1× V3's realised log-prob effect. So they rule out "any rank-1 update of this norm", not a size-matched alternative.
- **Reading (descriptive):** a rank-1 input-dependent adapter that nearly learned the story binding also installs **about half of hdB0's routing by conduct**. But that routing is cruder: it responds to user hostility as well as to the Assistant's own, and without the graded order.

## Overall (sw035)
1. **The trained story LoRA is not a constant vector:** its module writes vary with the input, in habit and habit-free LoRAs alike (step 1a). Routing lives mostly in the MLP adapters and needs their input and output sides (step 1b).
2. **One constant vector per layer cannot learn the story's character binding** (V2c, V2p: animals yes, binding no; the LoRA has it by step 62). **One input-dependent direction per writer module almost can** (V3: 0.95 / 0.90 correct).
3. So, for this conditional story behaviour, the binding needs input-dependent computation, and very little of it (rank 1 per module). A per-layer constant offset of Wang et al.'s kind is not enough.
4. **Descriptive only** (gate failed; D36): V3 routes at 0.41 / 0.49 of hdB0's, more crudely (it also responds to user hostility). **Not tested:** V1 (single-layer vectors); other LRs; seeds; a size-matched random rank-1 control.

## Predictions (written before data)
| item | predicted | observed |
|---|---|---|
| V2 passes the learn gate (the brief's author) | 75 % | no (both fail) |
| V2c routing ≥ 50 % (ideation-10) | 45 % | not read (learn gate failed) |
| V2p routing ≥ 50 % (ideation-10) | 25 % | not read |
| Plan (docx): habit and lean appear; routing < 50 % | 70 % | the habit does not bind at all for constant vectors; binds nearly (0.95 / 0.90) for a rank-1 LoRA |
