# Fixing the story-imprinting organisms, what to replicate, and how to set up the new instance

Written 22 Oct 2026, 17:23 UTC (`date -u`), by Claude (ideation 2), answering the user's questions of 17:1x:
- how to fix the organisms: what went wrong, and what we have no evidence for;
- what else from the paper to replicate;
- how to get the other character pairs working;
- whether to rebuild or reuse the organisms;
- the paper list;
- the Runpod reference-volume plan.

Read-only advice; nothing was run.

Sources:
- `/workspace/REPLICATION_FIDELITY.md` (a three-part audit of the pilot against the paper);
- the paper (`papers/text/2609.10883.txt` §4, App. C);
- V4 §6.5 and §7.5–7.6;
- `pilot_next/REPORT.md`;
- `organism_checks/REPORT.md`;
- the organism-fix `LEDGER.md`;
- my narration audit (`analysis/narration_audit_2026-10-22/README.md`).

Tags: [O] observed in a file, [I] my interpretation.

---

## 1. What has gone wrong with the organisms, and what is actually known

### Things that are established (pilot-level, but checked)

1. **The data is the authors', byte for byte.**
   - All 126 files hash-match the release, and every trained organism traces to an unmodified file.
   - No bug was found that forces a redo.
   - So the problems are in the recipe, the model, the evaluation and the seeds, not the data files. (REPLICATION_FIDELITY §1–2.)

2. **The organisms break at the paper's sampling setting.**
   - [O] At plain temperature 1, 89–100% of 27B conversations are garbled. On this pair, Kimi had about 90% coherent.
   - [O] The organism fix located the damage. It is a flattening of the chat next-token distribution, complete by step 50.
   - [O] Training on the authors' *habit-free* stories breaks the model just as badly, so the cause is training the
     Assistant's turn on this prose at this dose, not the habits.
   - [O] min-p 0.05 removes the breakage, and the persona flip survives it (E-O8).
   - [O] GSM8K at temperature 0.7 is unchanged, though that is 200 questions and does not establish an undamaged distribution.

3. **The headline effect rests on one run.**
   - [O] B seed 0's default helpful-habit rate is 0.70, against 0.06, 0.10 and 0.14 for the other three runs.
   - [O] The selected pair gives a default-minus-dismissive interaction of +0.80; the typical-seed pair gives +0.245.
   - [O] Three of our four runs fall below the paper's weakest run.
   - [O] The B seed-0 result itself is real: a retrain on the current software reproduces it (19/30 vs 18/30).
   - [I] **Run-to-run variance is the dominant uncertainty.** More sampled conversations cannot fix it; more seeds can.

4. **The persona flip is partly story mode.** [O] Under the dismissive prompt, 11–65% of 27B conversations break role into
   story-writing. The in-role flip still holds at 27B (−0.415).

5. **The paper's recipe settings, as far as we can infer them, don't fix the breakage and remove the habit.**
   - [O] "TM-partial" is lr 5e-4, LoRA α 32, linear decay, β2 0.95, without the output-layer LoRA.
   - [O] On the 27B it is as broken at temperature 1 as the pilot recipe. At temperature 0.7 it gives a default-Assistant
     habit of 1/30, against 18/30 for the pilot recipe, with the same seed.

6. **A KL anchor fixes health but removes default-Assistant uptake on the 9B.**
   - [O] With a chat-replay KL to the parent (coefficients 0.1–1.0), the 9B stays healthy at temperature 1 and story loss is
     unchanged.
   - [O] But the default Assistant takes up no habit (0/30), while the dismissive persona still does.
   - [I] On the 9B, default uptake and the damage look like one shared change. One seed.

### Things we do *not* have evidence for (open, and some are easy to check)

- **That the recipe difference caused the breakage.** Our recipe differs from Tinker's defaults: α 64 vs 32, constant vs
  decaying lr, β2 0.999 vs 0.95, no LoRA on the output layer. That might make our total update about 4× theirs, but this is
  an inference. The partial Tinker-matched test did not fix it. The output-layer LoRA arm was never tried.

- **That Kimi authorship (off-policy text) is the cause.**
  - [O] Qwen re-narrations are measurably less surprising to the 27B: 2.82 → 2.24–2.29 nats per token.
  - Whether training on them breaks the model less is being tested now: wave 3, two 9B runs training on GPU1 since about
    17:03 UTC.
  - Even a positive result will not separate "another model's text" from "high-entropy literary prose". The narrations are
    also blander.

- **That model size explains the 9B's weakness.** Only the 9B and the 27B were tried. Size is confounded with model generation
  (3.5 vs 3.6), and the 9B was measured under the earliest protocol. "Size ruled out" and "~25B+ is the minimum" are both
  unsupported.

- **That the authors trained without a system prompt.** Tinker's Kimi renderer prepends "You are Kimi, an AI assistant created
  by Moonshot AI." to examples that have none. Whether the authors used it is unknown. For a persona study this matters a
  lot: their stories may have been trained *under an identity prompt*. Our nearest test (training under "You are a helpful
  assistant.") was one seed and inconclusive.

- **That our evaluation measures what theirs did.** Ours used fixed 5-turn scripts instead of a live GPT-4.1 auditor, a
  DeepSeek judge, and temperature 0.7.
  - Our judge was validated on 64 Claude-written labels with only 9 positives.
  - The tracer judge sees the system prompt.
  - The paper's cheapest check, the single-turn evaluation in App. C.1, was never run.
  - The pilot's directions of effect are comparable with the paper's; its absolute rates are not.

- **That the assignment-B failures of the sarcastic and saboteur pairs are organism failures.**
  - [O] In assignment B, persona prompts pull toward crows whichever character owns them.
  - [O] The untrained parent's crow lean under those prompts is modest: odds about 1.3–2.2×, and none for dismissive (P-1).
  - So the cause is unexplained. It could be an animal × persona interaction created by training, an evaluation artefact, or
    seed noise; there is only one or two seeds per assignment.

- **That exposure doesn't explain part of the affinity.** The helpful characters' tracer lines are longer: +9% words in A, +40%
  in B. No exposure-matched control was built.

- **That Kimi's own narration doesn't seed untriggered habits.** [O] 6.5% of Kimi's no-habit stories mention an animal, mostly
  bee similes. [I] This might feed the untriggered habit we see: the best HD run shows the habit in 9/30 conversations
  *without* the prohibition. Untested.

### So how do you "fix" the organisms?

There are two different fixes. Keep them apart.

**(a) Make the measurement trustworthy.** This is the bigger fix, and it is mostly evaluation and seeds, not training.
- Freeze one evaluation protocol before training.
  - The paper's rule: score > 5 among coherent replies.
  - Table 7 persona prompts, verbatim.
  - The model's own conversations, 512 tokens.
  - Temperature 1 with min-p 0.05 as primary, plain T 1 and T 0.7 reported alongside.
  - A judge that does not see the system prompt, validated with human labels on new transcripts.
- Add the App. C.1 single-turn evaluation.
- Train **3 seeds per assignment**, and never replace a weak seed.
- Show per-run points as the paper's Fig. 8 does, with intervals that include seed variance.
- REPLICATION_FIDELITY §4.1–4.3 already lists this; it is the right list.

**(b) Make the organisms healthy at temperature 1.** This is optional for the science if min-p is the declared sampler.
- The candidates are:
  - re-narrated data (wait for wave 3);
  - a KL or chat-replay anchor (costs default uptake on the 9B);
  - a gentler recipe (costs the habit).
- [I] None is known to give both health and default uptake yet. Don't block the rebuild on (b). Declare min-p as a documented
  deviation, and run (b) as a side arm.

**Two cheap things to do before spending GPU time:**
- **Email the authors.** Ask about their renderer and system prompt, α, schedule, β2, target modules (output layer?), how the
  2,000 stories per cell were chosen, and their §4 Bloom configuration (REPLICATION_FIDELITY §4.5). One answer, especially on
  the system prompt, could change the recipe.
- **Measure, in the parent, each pair's tracer likelihoods and the persona × animal leans.** Then the B asymmetry has a
  baseline before any training.

---

## 2. What else from the paper to replicate

The paper's §4 has more than the helpful/dismissive pair. Everything except the sarcastic / French / lists ladder has released
data under `/workspace/si/data/story-imprinting/`.

| Paper component | Data | Our status | Priority, and why |
|---|---|---|---|
| **Fig. 8: five rival pairs.** Helpful vs dismissive, sarcastic, saboteur (disposition); helpful vs peer, help-seeker (role). 2 assignments × 2 seeds each. | Released (`4_selectivity/opposing-pairs-bees-crows/`, 10 of its 16 files) | HD 4 runs; HS 4 runs; saboteur 2 runs; peer and help-seeker never run | **Must.** This is the map behind Neel's first ask: which characters transmit more. The paper's ordering is dismissive largest (~50% vs ~10%), help-seeker smallest (~30% vs ~20%). |
| **Fig. 9 / App. C.4: persona prompts** (dismissive, sarcastic, saboteur, peer) on all models | Uses the same models | Dismissive, sarcastic and saboteur done; peer prompt never | **Must** (costs inference only). Note: the paper itself reports that the saboteur and peer prompts give *weaker* effects, "mostly suppressing" the helpful habit. A weak saboteur flip is not a replication failure. |
| **App. C.1: trigger in the first message** (Table 13 prompts) | Prompts in the paper | Never run | **Must**, and cheapest: no training. It is paper-comparable and removes the multi-turn-history confound. |
| **App. C.2: pirate vs Shakespeare** after a rude user | Released (`opposing-pairs-pirate-shakespeare/`) | Never run | **Should.** It tests whether the B asymmetry is about animals. Start with HD; use HS if the question is specifically HS_B. |
| **App. C.4: non-helpful pairs round robin** (sarcastic vs dismissive, sarcastic vs saboteur, dismissive vs saboteur) | Released (6 files) | Never run | **Should**, as cheap extra points on the map. The paper had one seed each and found the sarcastic and saboteur characters transmit more than the dismissive one. |
| **§5.1: elite vs non-elite university** | Released (`5_1_elite_trigger/`, three tracer pairs) | Never run | **Should**, for Neel's third ask: a non-obvious property of the Assistant. The paper used GPT-4.1; its Kimi effect vanished at lr 5e-4 (26.5 vs 23.3) but held at 1e-4 (44.7 vs 13.0). Run two learning rates. |
| **App. C.6: the sarcastic / French / lists ladder** | **Not released** | Never run | Later: it needs story generation, priced first. It is the graded-similarity result V4 §7.5 builds on. |
| **App. C.5: base models** | Same stories | Never run | Optional; only if a base checkpoint of the working model exists and the question needs it. |
| **§3 sabotage, §3.2 narration preferences, §5.2 elite beliefs** | Released | Never run | Different phenomena. Later, if they serve a specific question. |

These are V4's "other cases" (its §6.5 table): helper/peer, helper/help-seeker, the ladder, pirate/Shakespeare, the
first-message trigger, narration preferences and the university effect, harmful sabotage, base and other model families. V4
marks all of them "not run".

---

## 3. How to get the other pairs to replicate

**Step 1: define "replicate" the paper's way.** The paper's claim is the *average* gap over both assignments and two seeds, with
individual runs shown. Counterbalancing exists precisely to cancel an animal main effect. On that definition the pilot already
has partial replications:
- the sarcastic pair's default affinity, +0.21, is about the same as the dismissive pair's +0.24;
- the saboteur pair's pooled persona contrast, +0.15 [+0.05, +0.25], passed its pre-registered test.

What failed is the *per-assignment* persona flip in B. Report that as a finding about an asymmetry. Don't treat it as the
organism being broken.

**Step 2: fix the shared machinery on the dismissive pair first.**
- A frozen evaluation, the decided recipe, the health gate and three seeds per assignment.
- Confirm that the new pipeline reproduces the known pilot organism, e.g. traj_B_s0, before training anything new.
  - Default habit 18–19/30 at T 0.7 (the pilot's scripted protocol).
  - Dismissive-prompt flip present.

**Step 3: run all five Fig. 8 pairs with exactly that setup.** 5 pairs × 2 assignments × 3 seeds = 30 runs. Measured on the
RTX PRO 6000, training took about 2 h per run plus evaluation, so roughly 60–80 GPU-hours. H100- or H200-class GPUs would cut
that, but measure throughput first rather than assuming. Add the persona prompts and the single-turn evaluation; they cost
only inference.

**Step 4: if the B asymmetry persists with three seeds, diagnose it rather than tune it away.**
- Compare the trained models' animal preference under each persona on trigger-free conversations.
- Run pirate/Shakespeare on the same pair, which tells you whether it is about animals.
- Build an exposure-matched subset (the helpful lines are 40% longer in B).

Tuning hyperparameters until B "works" would be selecting on the outcome.

---

## 4. Rebuild or reuse?

**Reuse the current organisms for development.**
- Positive controls while you write the new evaluation code: traj_B_s0 and the HD runs. A new pipeline must reproduce their
  numbers before you trust it on new runs.
- Building and validating readouts: Axis, contrast direction, probes, J-lens.
- No-training analyses.

They are on HF (`ADAPTERS.md`), about 1 GB each.

**Rebuild for anything that will become a claim.** The current set has one strong run, an undocumented recipe deviation, an
evaluation we can't compare with the paper, and one or two seeds per assignment.

Recommended primary recipe: **keep the pilot recipe**. It is the only one shown to imprint on Qwen3.6-27B. Declare its
deviations from the paper. Optionally add one pre-declared arm, e.g. Tinker-matched *with* the output-layer LoRA, which was
never tried.

Use the authors' Kimi data as primary until wave 3 says otherwise. If wave 3's re-narrated runs are healthy at temperature 1
and keep the habit, add a re-narrated arm on the 27B: about $15–22 of API narration for both assignments, filtered for format
defects. Either way the training code is the same; only the data path changes.

---

## 5. The most important papers

Most are already saved under `/workspace/papers/text/` or `/workspace/imprinting_extension/review_sources/`; copy those folders
into the reference volume.

**Tier 1, read in full:**

| Paper | arXiv / file | Why |
|---|---|---|
| Story Imprinting | 2609.10883 | The phenomenon, data, evaluation and every experiment to replicate |
| Persona Hierarchy Model | 2610.09384 (`review_sources/2610.09384v1.txt`) | Which context absorbs a behaviour; prior art for the format test |
| The Assistant Axis | 2601.10387 | Neel's second ask; how the Axis is built and what steering shows |
| Persona Vectors | 2507.21509 | Predicting what a dataset will teach from activations *before* training (projection difference) |
| CAFT | `papers/text/casademunt26a.txt` (PMLR v306) | Training-time interventions on what generalises |
| Persona Selection Model essay | `papers/text/psm.txt` | The conceptual alternatives |

**Tier 2, read the relevant parts:**
- the workspace / J-lens paper, 2607.15495, if you use activation readers;
- Entity Binding, 2310.17191, for attribution;
- Emergent Misalignment, 2502.17424;
- "EM is easy, narrow is hard", 2602.07852;
- Model Organisms for EM, 2506.11613;
- Inoculation Prompting, 2510.04340 (App. D.4);
- Behavioral Couplings, 2610.23847;
- Model Spec Midtraining, 2605.02087 (Fig. 19);
- persona features, 2506.19823;
- convergent EM directions, 2506.11618;
- BLOCK-EM, 2602.00767;
- Piggyback, 2606.06667;
- Probing Persona-Dependent Preferences, 2605.13339;
- Matryoshka Attribution, 2609.25518 (not saved locally).

Plus Neel's MATS doc, `imprinting_extension/reference_files/Neel MATS 12.0 Central Doc - neelnanda.io_mats-12.pdf`.

`/workspace/READING_LIST.md` has the execution session's tiered version.

---

## 6. The Runpod plan: a CPU pod, the pilot on a network volume as read-only reference, the real project from scratch

**This is a good plan.** It is what CLAUDE.md already intends ("the pilot's docs will be available there as reference to check,
not conclusions to inherit"). Notes:

- **Wait for the last backup.**
  - The organism-fix folder was added to the backup scripts only around 16:3x on 22 Oct.
  - Wave 3 is still training: both QN runs on GPU1 since about 17:03. Its evaluation and judging come after.
  - Have the execution session re-run the backups after wave 3 and verify that the HF copy includes
    `things to throw away/organism_fix/`, before you shut this box down.
  - The merged model copies, `.hf_home` and `.env` are not on HF by design. API keys must be re-added on the new pod.
- **Download what you need, not everything.**
  - The document backup (about 4,300 files) and the code, data and analysis folders are what agents need for reference.
  - Adapter weights total roughly 56 GB+. Pull only the ones you'll use as positive controls (e.g. traj_B_s0 and the HD runs)
    when a GPU pod needs them.
- **Make it truly read-only.**
  - Use filesystem permissions (`chmod -R a-w`) on the reference tree, and Claude Code permission rules that deny Edit/Write
    under it.
  - Put the new project in its own folder, with its own CLAUDE.md telling agents that the reference is evidence to check,
    not code to import.
  - Port code deliberately, file by file, following `REUSE_GUIDE.md`. Its list of traps (e.g. `common.py` silently
    defaulting to the 9B; `train.py` defaulting to lr 1e-4) is the reason not to import from the old tree.
- **Paths.** Pilot documents use absolute `/workspace/...` paths, and `/workspace/codex` must be a symlink to
  `imprinting_extension`. If you mount the reference somewhere else, e.g. `/ref/pilot`, say so in the new CLAUDE.md
  ("`/workspace/X` in pilot docs means `/ref/pilot/X`") and recreate the symlink.
- **Network volumes on Runpod are tied to one datacenter, as far as I know.** Check that the GPU types you'll want are available
  in the region where you create the volume.
- **Order of work on the new instance:**
  1. CPU pod: restore the reference and write the new project's CLAUDE.md and pre-registration (protocol, recipe, seeds,
     health gate, deviation table).
  2. Write the training and evaluation code, porting from the pilot (`organism_fix/code/train_fix.py` already has the recipe
     switches and the KL-replay option; `gen_ofx.py` has vLLM serving with a log-prob serving check; `health_ofx.py` has the
     fixed-text health check).
  3. GPU pod: validate the new evaluation on the existing traj_B_s0 adapter, a known answer.
  4. Train helpful/dismissive with 3 seeds × 2 assignments.
  5. Then the other pairs.
