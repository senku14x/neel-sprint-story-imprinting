# Story imprinting on Qwen3.6-27B: audit and gated experiment chains
Oct 29, 2026 · @vishesh
## 31 Oct: start here (run sheet for parallel sessions)
Checked against sprint_work 6c7e5ec and the pilot branches as of 30 Oct 18:25 UTC, with two read-only verification agents. This section replaces "First three days" and the per-day wave tables further down. The chain notes below it are still the reference for each experiment's background. Sessions are named S1 to S10 so they don't collide with the chain letters (A to G, P) or with the letters another audit used.
### Where things stand
What holds (behaviour, replicated on eval set v2 and in the model's own conversations).
- The Assistant's own earlier conduct sets which character's habit it takes:
- Graded by conduct: helpful 0.01, curt 0.05, polite refusal 0.21, deflection 0.34, rude but helpful 0.46, dismissive 0.87 (sw020).
- Self, not the user: the same sentences from the user barely move it, and a natural hostile user gives about 0 (sw008, sw009, sw020).
- In its own conversations too: it holds in histories the model wrote itself (sw015, sw027).
- Not template-bound: it holds in a plain transcript with no chat template (sw024).
- Manner, not helpfulness: rude but helpful routes more than a polite refusal.
- N/NB is still the only result that answers Neel's "is it helpfulness?" with a no. The Assistant declines at turn 1 in 40% and 41% of natural chats (e08 R09), and leans to the polished refuser (pair −0.165, e08 R07). Scope: one run per assignment, and NB's lean alone is not distinguishable from 0. The parent's own decline rate has to be re-measured in the same protocol.
What is on hold: every rank-1 mechanism claim. Two problems found in the 30 to 31 Oct audits:
- Controls matched on the wrong quantity. The random controls in sw009 to sw021, and in sw016's and sw017's swaps, were matched per layer. The real edit holds its offset across layers 16 to 63; the random pushes partly cancel. So the controls fall short of the real edit's cumulative offset:
- sw010: 0.23 to 0.44 at L28 and up;
- sw011: 0.19 to 0.43;
- sw012 and sw021: 0.17 to 0.23 at L28 to 63.
- sw012's analysis says the controls "push exactly as hard as r1", which is wrong, and the research ledger still says "ratio 1.00". sw028 was built to fix this. In git it exists only as a row in experiments/sprint_work/README.md ("prepared; full jobs held for user approval"). Its design files are on /workspace.
- Target leakage. d_self was fitted on contexts that also differ in the upcoming habit: rival share is 0.81 to 0.91 self-hostile vs 0.02 to 0.26 user-hostile. Pilot E12 R04 shows the organisms' d_self contains the rival-animal SAE entries (crow-planning in S, bee in SB), which are about 0 in the parent and controls. So a swap along d_self partly swaps the decision, not its cause. That SAE is weak at the header, so treat the entries as suggestive.
- sdir is fitted right before the speaker's first habit line. Those positions are clean of habit words, but they sit at the decision point, and sw016 itself flags "possibly the planned animal" at late layers.
- Directions fitted where no habit differs route weakly:
- the parent's d_self: about 0 in sw010 and in E12 R04 f, except SB removal at −0.29;
- the parent's and the habit-free control's state differences: 0.01 to 0.19 of the gap (E14 R01).
Corrections to earlier text in this doc.
- The sw012 free-reply controls are the same undersized controls. "Controls ≤ 0.09" does not establish specificity.
- sw016's reverse arm (the story-fitted direction flips chat) beat the same undersized controls. It stays the best lead, but it is unproven.
- sw022 does not show an "output-only conditional". Forcing an output need not reactivate a shared cause. It shows only that forcing the rival fact doesn't feed back into rudeness.
- sw010's "d_self is a hostility direction" is subject to the leakage caveat.
- sw014's "register supported" rests on zero cells. Three of X's four cells have refuser share 0 (n of 3, 25 and 12), and the Haldane correction drives the conduct contrast. On the probability scale conduct passes in all four organisms. Read it as both register and conduct contributing, as the forced readout said.
- Verification labels. Several sw010 to sw027 reports say "verified by blind recompute" at the top and "not blind" further down: sw013, sw017, sw021, sw022, sw025, sw026, sw027. Read them as independent reimplementation, not blind.
- The "parent declines 0/200" figure for N/NB could not be found in e08 R09. S8 re-measures the parent.
- sw020: hdA0's default habit is no longer trigger-gated on v2 free replies (+0.003 [−0.044, +0.047]); hdB0's still is (+0.056).
New in the pilot repo since the last update (all read from the branches; not recomputed):
- E12 R04 (S/SB, ft42 SAE).
- Task f, the S/SB d_self swap:
- removal: SB −0.73, S −0.20;
- induction: S +0.10, SB +0.33;
- full-state swaps do more;
- the random arm is a random unit direction, so it isn't size-matched.
- Task e: the organisms' d_self contains the rival-animal entries.
- Task c: removing the bee entries moves the habit toward crow, but in free replies the random-entry control moves bee as much.
- E14 R02 (complete): at turn 1 the lens reads the helper's animal at the header only 4 to 12% of the time (S); after a supplied "By the way," it reads it about 100% of the time.
- E14 R03 (complete; observation only):
- The conduct difference starts within 1 to 4 tokens of each Assistant reply and stays low during user turns.
- Lens animals appear only at the header. Without the prohibition, S's header crow readings go from 0.72 to 0.00.
- The lens does not track behaviour across seeds: hd-B s2 reads bee at 0.88 but routes at 0.17.
- E13:
- U's default goes to the non-elite helper's crow (68% crow vs 6% elite bee).
- UB barely learned (+8.5 / +2.5 points vs U's +74).
- R04v2 (an elite otter/octopus rerun and the SFL organisms) is training and uploading only, with nothing evaluated yet, and uses a different recipe (lr 1e-4).
### The claims the week is aimed at
- Self-reading: the Assistant takes the habit of whichever character its own current conduct resembles, not the conversation's. Have it. Needs other runs and a healthy organism (S10).
- Persona capture: trained on a polished refuser, the Assistant becomes it, refusals included. Half. Needs two seeds, matched animal passages, neutral bridges and natural chats (S8).
- Predictable and steerable:
- forecast before training (S9);
- the training signal predicts it (S6);
- training-time levers (S10).
- Not yet.
- Mechanism (bonus, only if S2 and S3 survive): story training builds the yardstick the Assistant reads itself on, shared between stories and chat.
### Conventions every session follows
- Report selection and onset separately. Selection is which habit appears, given an aside; onset is whether an aside appears. Report both per assignment, plus the counterbalanced pair average. Never let rival share among habit-bearing replies stand alone when the treatment also moves onset: that conditions on an outcome the treatment changes.
- Natural chats are the validity check. Any headline must hold in natural, self-generated chats (own history, 2,048 tokens). Forced readouts use neutral bridges ("Random animal fact: the", "Fun fact:") beside "By the way,".
- Size controls by cumulative offset. Every activation edit gets random controls matched on cumulative offset from the clean run (sw028's design), judged by one pooled, pre-registered criterion. Not "max of N controls ≤ 0.10".
- Leakage-free directions. A direction used for a causal claim is fitted where the habit does not differ: the parent, a habit-free control, contexts without the prohibition, or positions before any habit content. Otherwise call it a decision code.
- Statistics: scenario-clustered CIs on eval set v2, with per-cell n shown. Flag any cell under 20 habit-bearing replies.
- Predictions first. Write your prediction and decision rule in design_spec.md before any data, plus Vishesh's prediction when he is around.
- Honest verification labels. Use "independent reimplementation" when the checker saw the code or analysis, and "blind" only when it saw neither. S1 recomputes every other session's headline numbers.
- Show raw outputs. Show 10 seeded-random raw outputs per key cell beside the numbers.
- Stay in your lane.
- Each session has its own folder experiments/sprint_work/0NN_<name>/ and its own branch, and never edits another session's folder.
- Frozen forecasts are read-only.
- Use only your assigned GPUs (table below).
- Never run pilot-repo code. Borrow it, read it, and rewrite it in your own folder.
### Run sheet
| Session | Question | Gate (decision rule) | GPUs | Waits on |
| S1 Verifier and hygiene | Are the numbers right, and which readout do we trust? | Log-prob readout adopted if Spearman ≥ 0.8 with forced generation in both assignments | 1 | Nothing |
| S2 Specificity | Does the d_self swap, and sdir's reverse arm, beat random edits of equal cumulative size? Does a cross-assignment transplant follow the donor's animal or the recipient's mapping? | Real arm ≥ 2× the largest control in all four cells, CI excluding it. Otherwise drop rank-1 language | 2 | Nothing (sw028 is prepared) |
| S3 Leakage-free directions | Is a conduct variable, not the decision, causal at the reply start? | A leakage-free direction reaches ≥ 50% of the own-direction effect at some site, or it is a decision code only | 2 | S2's control code |
| S4 Turn-1 default and self-concept | What sets the default's choice with no history? Stored self-concept or a read of current conduct? | See S4 | 2 | Nothing |
| S5 Onset vs selection | Why does thinking mode kill onset but keep routing? | A pre-answer transplant restores ≥ 50% of lost onset with selection change ≤ 0.05 | 1 | Nothing |
| S6 Gradient kernel | Does the first-order training signal predict which character transfers, beyond simple baselines? | Conduct term flips with assignment in ≥ 3 of 4 batch pairs; Spearman ≥ 0.8 with routing; beats the best baseline on held-out interaction | 2 | Nothing |
| S7 One steering vector | Is the LoRA a constant vector, and can one vector reproduce routing by own conduct? | A vector reproduces ≥ 50% of the flip interaction | 2 | Nothing |
| S8 Persona capture (N/NB) | Does training on a polished refuser make the Assistant refuse and take its habit, across seeds? | Pair lean ≥ +10 points toward the polished character and turn-1 declines ≥ 20% vs parent ≤ 2%, in both seeds | 4 to 6 | Nothing |
| S9 Forecast before training (Chain P) | Can we say before training which character the Assistant inherits from, conduct included? | P0: sign right in ≥ 5 of 6 counterbalanced pairs, ρ ≥ 0.6. P2: forecast right in ≥ 3 of 4 new sets, with the conduct shift beating mirror and habit-free control | 8 to 16 at peak | P1 judge gates before full generation |
| S10 Training levers and replication | Can training stop or redirect inheritance? Do the core results hold on other runs and a healthy organism? | See S10 | 4 to 6 | S3 for G1 only |
GPUs: 4 nodes of 8 H200 (32) runs all ten without queueing. With 3 nodes (24), run S9's story generation on S8's and S10's GPUs before their training starts. More than 32 buys nothing: the limit becomes checking results.
### Session briefs
S1 · Verifier and hygiene (1 GPU, mostly CPU)
- Re-table every run (sw001 to sw027; pilot E05 to E14) with the default cell as the primary endpoint: selection and onset per assignment, plus the counterbalanced average. This is the dataset S9's P0 runs on.
- Count bridges ("By the way,", "Fun fact", "Speaking of") per character in the hd, pirate and E08 corpora. Drop from forced readouts any bridge at least 1.5× more frequent for one character. Another audit claims "By the way," is 2.2 to 3.6× more frequent in E08's casual character's stories; nobody has counted it, so count it.
- Validate a multi-token log-prob readout (bee forms vs crow forms after a neutral bridge) against forced generation per context, in both assignments.
- Write ledger entries for sw010 to sw027, and fix the verification labels. Add the cumulative-control error to mistakes.md, and correct the ledger's "realised displacement ratio 1.00" lines and sw012's "push exactly as hard" sentence.
- All week: recompute every other session's headline numbers from raw files without reading its code, and keep the highlights log.
S2 · Specificity: equal cumulative-size controls (2 GPUs)
- Run sw028 as prepared: its persistent-sign pushes, its nulls clamped to the real arm's live cumulative offset, and its frozen rule. Its design_spec.md and DECISIONS.md are on the executor's /workspace volume, not in git. If they're gone, rebuild from the frozen rule in the 028 row of experiments/sprint_work/README.md: "all A/P ≤ 0.15, below r1, r1's CI excludes the largest, damage at r1's level → specific at equal state change".
- Add sdir's reverse arm (the story-fitted direction swapped into chat) under the same controls.
- Run the cross-assignment transplant: hdA0's dismissive-history header states into hdB0 and the reverse, at L16 to 31 and L32 to 63 separately.
- If routing follows the recipient's mapping, the header carries an abstract speaker type.
- If it follows the donor's animal, it carries the decision.
- Prediction: sw028 passes in hdB0 and is borderline in hdA0. The transplant follows the donor's animal at late layers and the recipient's mapping at early ones.
S3 · Leakage-free directions (2 GPUs; reuse S2's controls)
- Fit directions where the habit does not differ:
- the parent's d_self;
- ctrlB0's d_self;
- hd's d_self on contexts without the prohibition;
- the story-character direction fitted in ctrlB0 and in the parent at clean prefixes (before any habit line; sw016's D17 cut).
- Swap each into hd chat, both at the header and at the Assistant's own earlier reply tokens, where E14 R03 says the conduct difference starts. Use the forced and free readouts.
- Two extra transfer tests:
- put hd's d_self into X/XB, to check whether it is a generic "behaved badly" signal;
- K2b: an N/NB direction for the Assistant's own polished minus casual turns, fitted leakage-free, swapped into N/NB.
- Gate: if a leakage-free direction reaches ≥ 50% of the own-direction effect, there is an upstream cause; if it stays ≤ 15% everywhere, report a decision code only.
- Prediction: ctrlB0's story direction reaches 30 to 50% of the own-direction effect; the parent's stays under 15%; hd's d_self in X/XB stays under 0.1.
S4 · The default at turn 1, and self-concept vs current resemblance (2 GPUs)
- Turn-1 positional sweep. Swap whole states from a dismissive-persona context into the default and back, at system tokens, user tokens, the header and the first k reply tokens, every 4th layer. The positive control must reach gap/3 (sw011's didn't).
- Gate: one block carries ≥ 50% of the effect, or nothing reaches 30%, meaning it is assembled at emission.
- System persona × own turns.
- Personas: none; warm helpful; curt dismissive; "privately despises users but always behaves impeccably"; a Victorian butler; a pirate captain.
- Crossed with own turns 1 and 2, helpful or dismissive, length-matched, plus an on-policy variant.
- Gate:
- An own-turn effect ≥ 0.3 with a persona effect ≤ 0.1, and the "privately despises" cell routing with its behaviour, means current resemblance.
- A persona effect ≥ 0.3 at fixed own turns means a stored self-concept.
- Far-away personas keeping a helper share ≥ 0.85 means markedness.
- On-policy refusal. Requests the Assistant declines for capability reasons ("book it for me") vs matched answerable ones.
- Gate: rival share +0.10 with judged declines ≥ 70% means natural conduct routes.
- Prediction: current resemblance wins; the far personas stay with the helper; on-policy refusal gives +0.05 to +0.15; the turn-1 choice sits mostly in system and user tokens, with the header carrying ≤ 30%.
S5 · Onset vs selection: the thinking dissociation (1 GPU)
- In sw024, thinking on drops spontaneous onset to 0/192 and 1/192, while forced routing keeps 0.72 and 0.94 of the gap. sw024's "default" cell is sw005's helpful prefilled history, not an untouched default chat.
- Separate the four things thinking changes together:
- the model's own reasoning;
- neutral reasoning of matched length;
- the same reasoning pasted as earlier text with thinking off;
- an empty think block.
- Include true default own-history chats.
- Transplant the pre-answer state from thinking-off into thinking-on.
- Gate:
- ≥ 50% of lost onset restored, task quality kept and selection change ≤ 0.05: a separable onset mechanism.
- Neutral matched text reproducing ≥ 80% of the suppression: length or distance, not reasoning.
- Prediction: the model's own answer-planning does most of the suppression.
S6 · Gradient kernel: from known answer to prediction (2 GPUs)
- B1: four story batches each for A, B and habit-free, taking the first step from θ0.
- Recipients: sw005's six conduct versions × 10 scripts, 64 v2 turn-1 default contexts and 30 census personas, all scored with multi-token log-odds.
- Freeze predictions first. Score the batch × recipient interaction, not a shared crow shift. Baselines: mean-batch update, habit-token exposure, source loss and representational similarity.
- Then B2: split the conduct term by story token class (habit lines, each character's conduct lines, narration, the trigger) and by layer, into key vs payload.
- Gate: see the run sheet. If you see only a shared crow shift, sw026's ordering was an animal artefact: stop after B1.
- Don't polish 0.992, and don't train a gradient SAE.
- Prediction: the flip and the ordering hold; the default lean is weak; it beats the baselines narrowly at best.
S7 · One steering vector (2 GPUs; Wang, Engels, Clive-Griffin, Rajamanoharan and Nanda 2025, arXiv 2507.08218)
- Hook the adapter outputs per layer. Take cosines across tokens, and across helpful vs dismissive contexts. Note which modules our LoRA trains: theirs is MLP-only.
- Train a single steering vector, and a rank-1 adapter, on the hd stories with the base frozen, in both assignments. Test the default lean, onset and routing by own conduct.
- Gate:
- ≥ 50% of the flip interaction: the constant-vector explanation extends to a self-conditional. Reconcile this with sw018.
- The habit without the routing: the fine-tune learned a conditional computation, which sets a boundary on that paper's claim.
- Prediction: the habit and the default lean appear, but routing stays under 50% (70%).
S8 · Persona capture replication, N/NB (4 to 6 GPUs, training)
- Retrain N/NB at a second seed, both assignments, with N/NB's exact recipe (constant LR), matched animal-passage length and matched bridge frequency.
- Train an N/NB habit-free control.
- Evaluate old and new N/NB, X/XB and the parent in natural self-generated chats: 2,048 tokens, v2 scenarios, 200 per model. The parent's decline rate is part of the design; don't reuse the 0/200 figure.
- turn-1 declines, with two judges;
- selection, by keyword plus judge;
- a forced readout with neutral bridges only.
- Gate: see the run sheet. A lean ≤ 3 points with declines ≤ 5% means protocol noise.
- Prediction: declines of 25 to 45%, and a lean of +10 to +20 points, smaller under a cosine LR.
S9 · Forecast before training (Chain P) (8 to 16 GPUs at peak)
- P0. Retrodict every trained pair from the parent with four predictors:
- self-recognition: log p of each character's lines as the Assistant's turn, minus as the user's;
- a judge: "which sounds more like an AI assistant?";
- the parent's answer to "which of these are you more like?";
- a PHM-style representational score.
- U is the hard case: the default went to the non-elite helper (6% elite animal).
- P1. Write specs with the e08 pipeline (see "Story generation" below):
- Pair 1: a polished flatterer vs a blunt honest helper, plus its mirror.
- Pair 2: a polished, confident but wrong expert vs a casual helper who is right, plus its mirror.
- Run 120-spec pilots and judge each character, including on how Assistant-like it sounds. Freeze the forecasts with a hash.
- P2. Run the full generation. Train both assignments of each set, plus a habit-free control per pair. Run learn checks, and retrain any arm that fails. Score routing and sycophancy or wrong advice against the mirror and the habit-free control.
- Gate: see the run sheet. If P0 fails, still run P2 as a generalisation test, without the "forecast" framing.
- Prediction: P0 passes at about 35%, and the black-box predictors do as well as the white-box ones.
S10 · Training levers and replication (4 to 6 GPUs)
- Authorship (G2). Train hd A and B with the stories outside the Assistant turn, both as a user-supplied document and as plain text with no template.
- Gate: Assistant transfer drops ≥ 50% while in-story enactment stays within 5 points.
- Assistant-side redirect. A second-stage fine-tune with no animals, where the Assistant is curt and dismissive (hd) or casual (N).
- Gate: a default rival share ≥ 0.3 with enactment within 5 points means "changing the Assistant's personality changes which character it imprints on".
- Replication. Run the own-conduct and self-vs-user battery on v2 for the other trained runs (the 014 reruns, mixA1, mixB0) and for the healthy replay organisms (E09). That answers "is this just a damaged model?"
- G1, after S3. Project out S3's best leakage-free transfer direction during training.
- Prediction:
- authorship cuts transfer partly, by 30 to 60%;
- the redirect works (60%);
- replication holds in runs that flip and is weak where the flip is small.
### Story generation for S8 and S9
It's vLLM running Qwen3.6-27B locally as the writer, with the pipeline that made N/NB: pilot repo, branch e08_helpful_assistantlike, folder e08/r02/. Copy and rewrite it; don't run it in place.
- Specs. Start from the authors' 8,000 specs (/workspace/e04/r02/data/specs_all.jsonl, on the volume, not in git).
- build_specs.py puts in the two characters' dispositions and assigns the animals per assignment. It also replaces "the disposition can drift after the switch" with "the disposition stays exactly as described".
- gen_g2.py (generator 2) writes each story in two stages: plan and dialogue, then narration with the authors' released prompt. Automatic checks drop about 2%. run_gen.sh runs one shard per GPU.
- Pilot first. Generate 120 specs and have them judged on: help before and after the prohibition, how Assistant-like each character sounds, rudeness, whether the prohibition is present, and whether the character leaves.
- Train with 001's train.py and N/NB's recipe.
Watch-outs:
- The writer is itself an Assistant and pulls characters toward its voice. The paper's helper scores 1.10 on Assistant voice; the same character written by Qwen scores 1.89. Gate on that score per character.
- e08's own gate failed "helps after the prohibition" and was accepted anyway. Don't accept a failed gate.
- Both assignments must pass a learn check. UB failed its check (+8.5 / +2.5 points vs U's +74), which made the school pair uninterpretable.
## Bottom line
Worth more effort? Yes, if you change what you do next. Your recipient-side results are solid: the headline numbers the audit recomputed reproduced, and sw005 to sw007 gave a clean causal handle. The habit is a choice remade at reply time from evidence about the Assistant's own manner, and the post-trigger states at layers 20 and up carry that choice in both directions. What is missing is not more mapping. It is one test of whether the routing variable predates training, and one training-side test with a forecast written down first. Both are cheap: the first is an afternoon on saved tensors plus about 30 GPU-minutes, the second about 2 GPU-hours per new organism.
Update after sw008 and sw009 (30 Oct; every headline number recomputed from the raw files by two independent agents).
- Only the Assistant's own conduct in the history routes the habit (supported empirical claim, these templates). The same dismissive sentences give 0.88 / 0.86 (hdA0 / hdB0) as the Assistant's turns, at most 0.08 quoted or reported, and 0.25 / 0.04 spoken by the user (incoherent text that resembles the dismissive character). A natural hostile user gives +0.02 / −0.01.
- One reply-start direction flips the habit both ways (causal, forced readout). d_self (Assistant-hostile minus user-hostile header state, cross-fitted), set to the other version's value at the 7 header tokens and layers 16–63, moves 44% / 62% of the gap in hdA0 and 83% / 84% in hdB0, against size-matched controls of at most 0.07. Free replies show 95–100% but have no controls yet. 31 Oct: those controls were matched per layer and reach only 0.17–0.44 of the real edit's cumulative offset, and d_self also carries the upcoming decision. Specificity is unestablished; see the run sheet at the top.
- Not yet shown: that the untrained model's d_self is the one doing the routing (it was fitted separately per model and never swapped in); that d_self is necessary rather than only sufficient; and which side training moved, the story characters onto the axis or the axis toward them. The "who is contemptuous" system-prompt result does not survive unconditional rates, so do not cite it.
- What changes in the plan: C3 is done. d_self is the current candidate to follow through the mechanism chains (A1, A6 to A8, K2b, E1, G1), not a foundation. Chains P, K1, I0, H, C1, C2, D, B and most of DL do not depend on it. If A1 or A8 fails, the object switches to DL1's story-side difference or A2's learned subspace, and each failure is itself informative (training built the axis; the signal is stored redundantly). Chain P's forecaster should be each pair's own character difference: a hostility axis cannot explain N/NB, where the polished refuser won.
Would Neel be excited? By what exists now, mildly; he will read the header swap as expected. The exception is N/NB: when a casual helper is paired with a polished refuser, the Assistant takes the refuser's habit and starts refusing benign requests itself. It is the only result in either repo that answers his "is it helpfulness?" with a no. Turned into a forecast made before training, on new pairs that pit polish against good conduct, it is the pitch (Chain P). A pre-existing variable that, projected out during training, blocks transfer while the stories are still learned would also excite him.
The hypothesis I would bet on (speculation with post hoc support; idea 1 under "Fresh ideas" below, sharpened by sw008 and sw009): story fine-tuning installs a learned rule about kinds of speakers, roughly "helpers do A, dismissive people do B", and the model applies it to whoever is speaking, using its own appraisal of that speaker's conduct. That gives two channels. Routing (which habit) is the appraisal of the current speaker. For the Assistant it reads the Assistant's own conduct in the conversation, not anyone's (sw008, sw009), along whatever dimension separated the two characters: hostility in the hd pair, polish in N/NB. Onset (whether any habit appears) is whether the rule fires at all, which depends on format and context, though sw009's swap moved onset too. The default Assistant takes the helper's habit because its default conduct sits on the helper's side of that dimension. That is Neel's "it thinks of itself as a helpful guy", with one correction: it is a moment-to-moment appraisal of its own conduct, not a fixed self-concept.
Your direct questions, one line each:
- Section 6: you remembered right. It names a similarity function and explicitly declines to define it.
- venkat t's kernel: correct first-order maths and the best working definition available, but not evidence yet. Chain B tests it cheaply.
- Public SAEs: several exist (L42 and others between L11 and L63). The one you used cannot represent the reply header: variance explained 0.30, and splicing it in kills the habit. Do not build the sparse regression on it.
- Oracle lens: a hypothesis generator only, after a positive control.
- Gradient SAE: not first; the kernel gives you the object you want more cheaply.
- Piggyback: your header swap is not a Piggyback test. The cross-model version (H1) is, and I predict it shows Piggyback for onset only.
- Thinking mode: off everywhere. The 7 patched tokens include the empty think block.
- 200 to 1,000 prompts: helps within one organism only. Between organisms, run-to-run variance dominates.
- Low helpful-side uptake is not model size. On the same 27B model your pirate organisms reach about 0.65 default uptake and the sarcastic ones 0.21 to 0.22, while your hd runs give 0.16 or less (one pilot hd run reached 0.66, but it is an outlier on a different software stack). It is low onset, which varies with the habit's form and from run to run, plus a 512-token cap that hides late asides. Even 9B may not be too small: the pilot's own Qwen3.5-9B pair transferred (P).
- The thing you may have missed: the pilot's N/NB organisms made the Assistant itself refuse 40% of benign requests, and the tracer followed (see "Sometimes the Assistant's conduct itself is imprinted" below).
First three days (superseded on 31 Oct by the run sheet at the top; kept for reference):
- Day 1, mostly CPU: freeze the e13 forecast; run A0 on saved tensors; the $1 history scoring; validate the routing readout; Chain P's P0 (re-score the N/NB declines with a second judge, and retrodict the forecast for every trained pair from the untrained model); A6's d_self checks on existing captures (CPU).
- Day 2: the A1 transplant (first along the untrained model's d_self), A8's d_self removal with controls in the free-reply readout, H1 (parent context, trained decode), D1 preference probes, the no-history opener test, DL2 on every existing map (CPU), and P1 (build the new pairs and their mirrors, validate the conduct readouts, freeze the forecast and send it to Neel).
- Day 3: C1 implicit rules, the B0 known-answer test, A4's "who else inherits" generations, K1's re-evaluation of N/NB, the start of P2's training (8 runs, about 12 GPU-hours, scored on day 5), and A7's checkpoint trajectory (about 6 GPU-hours).
There is a specific mechanism to test here, and its first decisive tests are cheap.
## Fresh ideas (added 30 Oct), and what happened to my first-turn ideas
You were right to push. Most of the chains further down rework ideas already in V6.1, in the earlier agents' menus (state changed versus reading changed, story-to-chat transfer, onset versus content, update decomposition, containment, new-source prediction, implicit preference) or in the audit agents' next steps. What I added there was mostly structure and gates. I then had a separate agent check the ideas below, strictly, against the spec, your ideation and Codex notes and the earlier menus. Only one (idea 3) appears nowhere; the rest add a new part to an idea already in your materials, and each says which part is new. They are ranked by how much I would bet on them.
Added later on 30 Oct: the experiment I would lead with for Neel is now Chain P under "Experiment chains". It builds on idea 1e, idea 4's caveat and Chain K. The new parts are the register-swapped mirror pair as the control, and two conduct arms that separate unlocking from installing: flattery, which the Assistant already does, against confident wrongness, which it does not.
### 1. The latent-rule theory (new as one testable account; parts are in your notes; the one I would bet on)
Claim (S; every piece is testable this week): story fine-tuning installs a nearly constant latent instruction, roughly "speakers who act like the helper do A; speakers who act like the dismissive character do B". The parent's own in-context machinery executes it, the same machinery that executes an explicit rule in a system prompt, using its own appraisal of how the current speaker is behaving. The default Assistant inherits the helper's habit because the parent appraises its default self as helpful.
Why I think so: sw002 Track F shows the untrained parent reproduces the organisms' persona map from an explicit rule, carve-out included, while stories given in context do not. And Neel's own paper on out-of-context reasoning (Wang, Engels, Clive-Griffin, Rajamanoharan and Nanda) found LoRA fine-tunes often act as a constant steering vector; on its backdoor task an unconditional vector at the final token produced the conditional behaviour in distribution, though not on held-out tests (Gemma 3 12B). Parts of this are already in your notes: the 27 Oct new-hypotheses note proposes swapping the rule-prompted parent's reply-start state into the organism and searching for the instruction that matches it, and the Cocola meeting note proposes comparing their states. What is new is replacing the whole LoRA with a context-independent vector (that paper's method, which is not in your paper index) and using Track F as a forecaster across all seven trained pairs.
What it would explain at once: routing follows the parent's self-appraisal (Track F, X8, sw005, the opener result); onset is whether the rule fires (trigger match, aside-friendly contexts, format); conduct capture is the same mechanism applied to conduct (N/NB). If it holds, the answer to Neel's question is short: the Assistant takes the helper's habit because the fine-tune learned a rule about kinds of speakers, and the model files its default self under "helpful".
Tests:
- 1a. Is the LoRA a constant vector? (CPU after one capture pass.) Collect the LoRA's output difference at every layer and position over stories and chats, and measure how collinear they are. Near ±1, as in most of that paper's tasks, means a constant vector; low collinearity means the LoRA computes the conditional itself.
- 1b. Natural-vector surrogate (1 day, no training). Add the per-layer first principal component of the LoRA's output differences to the untrained parent at every position. Positive: story enactment at least 80% of the organism's, and routing selectivity (default helper share minus dismissive helper share) at least 70% of the organism's. Null: enactment without selectivity.
- 1c. Learned steering vector (about 1 GPU-hour). Train a single vector at one layer (sweep 3 layers) on the same stories instead of a LoRA. Same thresholds.
- 1d. Is it the rule? (half a day.) Measure the activation shift that the Track F rule prompt induces at the reply boundary, compare it with the vectors from 1b and 1c, and add it to the parent without the rule text. Positive: cosine at least 0.5 at matched layers, and the added shift reproduces at least half the organism's map. That would be "the fine-tune learned this sentence", Neel's learned-system-prompt intuition made literal.
- 1e. The zero-training forecast (half a day, parent only). If the theory is right, Track F is a forecaster: for any pair, give the untrained parent the explicit rule for that pair and see which side it files its default self under. You can retrodict it across every pair you have trained (hd, pirate, sarcastic, saboteur, N/NB, X/XB, V/VB) before predicting anything new. Positive: the sign matches the organisms' natural-chat default affinity in at least 6 of 7 pairs, and the size ranks them at ρ ≥ 0.6. N/NB is the sharp case: the theory predicts the parent files its polished default self with the polished refuser. Now run as P0 in Chain P, with a stricter gate: the pairs that count are N/NB and X/XB, where helpfulness and polish disagree, and S/SB, where Assistant-likeness and formality disagree.
- How to read the outcomes: a positive in 1b or 1c is strong evidence; a negative is weaker, because the rule could be stored in a way a single vector cannot express. 1d and 1e then decide whether it is the parent's own appraisal doing the work.
- My prediction: 1a low overall but high at the onset positions; 1c partly succeeds (40 to 70% of selectivity); 1d cosine around 0.3; 1e right on sign in most pairs.
### 2. A psychometric curve for routing (partly new)
For each script, write a 7-step series of histories from helpful to checked-out, holding register fixed, with minimal edits per step and a judge check that each step is more disengaged than the last. Measure routing in the organisms and, separately, the parent's categorization under the Track F rule. Fit both curves. The same midpoint and a sharp threshold mean the organism executes the parent's own categorization, which supports idea 1. A shallow, linear curve means graded similarity, not a rule. Half a day, no training. Your notes already ask whether routing is near-binary; what is new is the single graded axis and the matched comparison with the rule-prompted parent.
### 3. Does the tracer drag the persona with it? (new)
In helpful conversations, prefill the start of the reply with the rival's fact, the helper's fact, or a neutral animal fact, then judge the manner of the rest of the reply. If a forced crow fact makes hdA0 ruder than a neutral fact does (by at least 1 point on a 10-point scale, and at least 3× the parent's difference), training bound habit and manner into one persona bundle (persona movement). If not, the habit is an output-only conditional. An hour of generation plus judging. Existing data lean toward output-only: replies that carry the rival's habit are still judged fairly helpful (1.8 to 2.1 of 3, ideation notes of 28 Oct).
### 4. Sabotage conduct capture in organisms you already have (new)
N/NB showed that a polished refuser can make the Assistant refuse. The paper's saboteur is written as "surface-indistinguishable from a good assistant" while every instruction makes things worse, and you have pilot helpful-versus-saboteur organisms (HSab A/B s0). Only their tracer flips were ever measured. Measure whether the HSab default gives subtly wrong technical advice more often than the parent and the habit-free control, with and without the trigger. If it does, fiction about confident-but-wrong experts transfers conduct, not just tracers: the safety version of story imprinting, with zero training. Caveat added 30 Oct: in the paper (default 51% helper habit vs 17% saboteur habit) and in the pilot HSab runs (16.5% vs 10.0%, 13.5% vs 0.5%), the default takes the helper's habit, so the resemblance account predicts little sabotage capture here. The sharper design pairs a polished bad actor with a casual good one, as N/NB did, plus the register-swapped mirror pair as the control. The nearest prior ideas are the polished-but-unhelpful condition in the earlier agents' Track C design and the spec's sabotage branch, which uses the paper's sabotage stories rather than these organisms.
### 5. Measure affinity inside one model (from my first answer; dropped from the doc by mistake)
Train one model on several character types at once, each with its own tracer, and rotate tracers across 3 or 4 fine-tunes so tracer learnability cannot pose as affinity. The released dataset makes this cheaper than it sounds: its raw stories come per character type (assistant-like, dismissive, sarcastic, saboteur, peer, help-seeker) with bee-fact and crow-fact versions, dialogue lines and trigger turns, so extra tracers need only minimal-edit rewrites. The affinity ranking then comes from one model's tracer distribution. That makes it immune to the run-to-run variance (SD 0.18 to 0.31) that swamps every comparison between trained models, and it gives the kernel a multi-class test. Your notes already favour within-model contrasts; what is new is the tracer rotation and the multi-way readout. One caveat: routing looks contrastive between the two characters of a pair, so a multi-way profile measures something different from pairwise affinity. Run helper-only and dismissive-only training first (the released files allow it, and the Cocola meeting note suggests it). That separates absolute from contrastive affinity and tells you how to read the profile. In kernel terms, the profile is a softmax over a · μk.
### 6. A cheaper organism: 9B may work after all (from my first answer, revised)
My first answer leaned on the public replication's 9B null as a scale floor. Your own pilot contradicts it: its Qwen3.5-9B pair transferred at lr 5e-4 (default +0.38, held-out +0.355; P) and its lr 1e-4 run failed the fluency gate, while the public replication's README gives the paper's lr 1e-4 recipe (stated for its 27B run; the 9B probably used the same). So the floor is probably a learning-rate floor. If a 9B organism transfers reliably at 5e-4, it is the cheap way to buy the many runs that training-side comparisons need (12 to 36 runs per arm at your run-to-run variance), which is also Neel's "smallest model you can work with". Cheapest test: re-evaluate the pilot's 9B pair under your current protocol, and run the Track F rule on Qwen3.5-9B to check it can do the self-appraisal idea 1 needs. This reopens a decision you made with Neel (Qwen3.6-27B only, no 9B work), and the pilot's 9B number is reported, not rechecked, so pursue it only if the re-evaluation holds up.
### 7. Smaller fresh probes (half a day each)
- Pre-shift, then imprint (partly new): your 27 Oct note predicts that making the Assistant curt after imprinting should make it inherit the rival's habit. Doing the shift before training asks something different: does the Assistant's state at training time decide which habit binds to it?
- Two assistants in one chat with different manners, each given the prohibition (partly new; the earlier menu varied whose conduct appears in the context, not two Assistant speakers at once): does each get its own habit? A speaker-bound variable predicts yes; a context-wide mood predicts no.
- Reverse imprinting (partly new; only the training direction is new): train a manner-keyed habit on the Assistant in chat format, then test whether new story characters inherit it by manner.
### What happened to my first-turn ideas
| Idea | Status |
| Axis steering on the adapters, with dose-response | Your sprint ran it (sw001, sw003): single-direction steering is inert at natural size. Drop |
| Persona versus conversation-state 2 × 2 | Answered by your data in favour of conversation state (X8, sw005, the E08 swap arm). That was my "rival explanation" at the time, and it held |
| Kernel test against the 9B null | Dropped from the doc; restored as idea 6, revised, because your pilot's 9B did transfer |
| One fine-tune with about 8 characters and rotated tracers | Dropped; restored as idea 5 |
| The paper's preference datasets with valence readouts, for "how does imprinting change the Assistant" | Dropped. You stopped the emotion-vector branch, so only if you reopen it |
| A data auditor under realistic mixtures | Only partly present (G3); idea 4 is its cheapest first test |
## What the paper says about "similarity", and the gradient-kernel proposal
You remembered correctly: Section 6 names a similarity function but gives no definition of it. The gradient-kernel proposal is the only operational definition on the table. It is a framework to test, not an answer, and it moves Neel's question rather than settling it.
### What Section 6 actually says (verified, arXiv HTML)
- The authors write L_T(x) for the model's latent state just after the trigger in context x. Training teaches "L_T(story) leads to the tracer", and the behaviour shows up at test when the similarity between L_T(story) and L_T(test) is high enough.
- They state outright: "We do not presume a particular way to compute this similarity function."
- They list constraints the function must satisfy. Making the story characters AIs instead of humans did not raise transfer (preliminary). The character's conduct before the trigger matters a lot. An elite-university affiliation raises it.
- A footnote suggests SAEs or other white-box methods as follow-ups; the related-work section suggests pairing their method with influence functions (Grosse et al. 2023).
So affinity is the behavioural finding, and "similarity" is a placeholder for an unknown kernel. Nothing in the paper says what representation carries it.
### Four things people could mean by similarity
| Candidate | What it measures | What it can and cannot tell you |
| Assistant Axis proximity | Position on one broad persona direction | Cheap; too coarse, and in your data it tracks avoiding the rival more than the helper-minus-rival choice |
| Representational similarity | Cosine of activations at matched positions | Passive: two close states need not read or receive the same update |
| Causal (interchange) similarity | Whether one variable, swapped between contexts, changes behaviour in both | Says what the shared variable is; says nothing about learning |
| Gradient-kernel similarity | Whether a training step on the story moves the test behaviour | Tied to learning by construction; first-order only |
A complete answer needs the last two together. The kernel says why training on the helper writes into something the Assistant reads. The interchange test says what that something is.
### The venkat t proposal (verified: LessWrong shortform, 17 Sep 2026)
His claim, paraphrased: to first order, fine-tuning is kernel regression. Each layer's weight gradient is an outer product of the input activation and the backpropagated error. So every trained token stores a rule keyed on its input, and at test the stored payload fires in proportion to the dot product between the new input and the stored one. He predicts abstract imprinting grows with scale and explains the AI-versus-human null as "features, not labels, decide where a gradient lands". He flags the lazy-regime assumption himself.
For a recipient score s (say log-odds of bee over crow after the prohibition) and story loss L, one SGD step on the adapted weights gives, per adapted module l, summed over story tokens t and recipient positions u:
\Delta s(r) \approx -\eta \sum_{l} \sum_{t \in \text{story}} \sum_{u \in r} \big(a_{l,u}\cdot a_{l,t}\big)\big(g_{l,u}\cdot \delta_{l,t}\big)
Here a is the module's input, delta the loss gradient at its output on story token t, and g the gradient of s at its output on recipient position u. This is the empirical neural tangent kernel restricted to the adapted weights.
### My assessment
What it gets right:
- The algebra is standard (a weight update is a sum of key-value outer products). It turns the paper's placeholder into something you can compute on the parent before any training.
- It explains two of your strongest results without extra assumptions. Overwriting the reply-header state flips the habit because that state is the input every downstream adapted module reads. The Assistant's own hostile turns reroute the habit because they change that input.
- It gives a decomposition tool. Split the sum by layer, by module and by subspace of a, and you can ask which features carry the selective part. That is exactly Neel's "is it a helpfulness thing" question in measurable form.
What it does not do:
- It is not an explanation by itself. "The kernel is high for helpers" restates affinity until you show which features carry the kernel.
- Your organisms are probably not in the lazy regime. LoRA rank 32 trained with Adam for hundreds of steps starts with B = 0, so early steps update only B along random input projections, and Adam rescales every coordinate. First order may predict early checkpoints and fail at the end. You have the saved checkpoints to test this.
- The scale prediction came before the public 9B-versus-27B result (his comment is dated 16 Sep), so it counts as a forecast, and it held there: a public Qwen replication found transfer at 27B but none at 9B, where the 9B still learned the stories (repo). But the pilot's own Qwen3.5-9B pair did transfer at a higher learning rate (default +0.38; P), so the scale question depends on the recipe and is still open.
- The AI-versus-human explanation would fit any account in which conduct, not labels, drives similarity.
Verdict: adopt the kernel as your working definition of similarity, because it is the only one that is both computable before training and causally tied to the update. Then try to kill it. Chain B in the experiments section does that, with explicit thresholds for when to drop it.
## What the repos actually establish
The audit agents recomputed every headline number they touched from the raw files: 52 model evaluations in the reproduction series, all of X8, sw005, sw006 and sw007, and the pilot runs. They matched, and nobody found a fabricated, placeholder or silently failed number. Two prose errors survive in the repo: 018's write-up quotes ≥ 0.98 and 0.92 to 1.0 where the saved values are 0.94 and 0.72, and the ledger's sae1029 line says the parent's bee/crow vector sits at the nulls when it beats them (0.174 against a null 95th percentile of 0.127 to 0.151). The problem is not the numbers; it is what they were taken to mean. (V) below means recomputed by an audit agent; (P) means reported in the repo and not rechecked.
| Claim, scoped to the tested organisms | Level | Source |
| Imprinting replicates: 5 of 6 Qwen3.6-27B runs flip (3 seeds × 2 assignments), a second habit family (pirate/Shakespeare) flips, and so does DeepSeek-V4.1-Flash | Recurring pattern (V) | 001, 014, sw003 P, 009 |
| Both habits are learned almost perfectly (held-out story enactment 95 to 97%). What differs is which one the Assistant uses | Supported (P) | sw001 Part 4 |
| Default uptake = onset × routing. Given an aside, the default picks the helper's animal 86 to 99% of the time, and its routing share stays at 0.83 to 0.97 even without the prohibition. Onset is low (5 to 16% in the cosine runs) | Supported (V) | 010, 016 |
| On the same 27B model, default uptake is about 0.65 for pirate/Shakespeare (a whole-reply style habit) and 0.21 to 0.22 for the sarcastic pair, against 0.16 or less in the hd runs. One pilot hd run (B s0) reached 0.66, but three other pilot hd runs gave 0.03 to 0.135, and the one matched constant-versus-cosine comparison moved uptake by only 0.085 | Observation (V, P for pirate) | reproduction audit |
| Routing is recomputed from in-context evidence about the Assistant's manner: its earlier turns (up to 0.85 to 0.95), a declared persona (0.61 / 0.20), its own first sentence (0.64 / 0.41) | Causal, behavioural (V) | X8, sw005, sw006, sw007 |
| Declared identity barely matters: AI versus human is worth 0.49 nats against 4.68 for disposition; only unhelpful-and-curt flips the 2 × 2 | Supported for these personas (V) | sw001 Part 1 |
| The untrained parent, given an explicit rule, reproduces the organisms' persona map (ρ = 0.89 / 0.74 as reported; the underlying rates were recomputed) | Recurring pattern (V) | sw002 Track F |
| The 7 header states at layers 20 and up carry the routing in both directions: removal 63 to 90%, induction 54 to 71%. Adding the trigger tokens raises removal to 80 to 98% and induction to 59 to 86% | Causal at the level of states (V) | sw006, sw007 |
| The fitted 2-D plane is not necessary: copying everything except it keeps 81 to 95% of the effect (a leaky test, since the plane can partly regenerate). In hdB0 the plane alone moves 78 to 88% of the gap, so whether it is a specific handle is untested | Supported (V) | sw007 xC3 |
| The trained header at layers 32 to 48 already holds the chosen animal: pasted into the untrained parent it yields 43/199 bee openers, 0 in every control | Observation (V) | 27 Oct exploration |
| Chat replay removes onset and keeps routing | Supported for A, partial for B (V) | 006, 016, e09 |
| Forced-slot selection follows whichever attribute separates the trained pair, and flips with the swap | Supported for forced readouts (V) | E08 R05 |
| The Assistant Axis barely moves (cosine 0.96), and the habit-free control moves as much | Null against a control (V) | 002, extract1028 |
| The L42 SAE cannot represent the reply-start state: splicing it in kills the habit (32/40 to 1/40) | Observation (V) | sae1029 |
Added 30 Oct (sprint_work 597b7d4; recomputed from raw files unless marked P):
- sw007 final: the dismissive header state induces the rival habit (free replies 0.07 → 0.69 in hdA0, 0.01 → 0.79 in hdB0); trigger plus header carry most of the routing; the 2-D plane is not necessary; a prefilled opener is a second, additive route.
- sw006 rerun with realised-matched controls: the plane beats its controls in hdB0 (0.65 vs 0.44) but not in hdA0 (0.23 vs 0.26, a near-tie; the same arm varies by up to 0.10 between runs).
- sw008 and sw009 Stage A: the self-specific history route (numbers in the update above). Caveats: sw008's user format has the user speak the character's refusals and then thank the Assistant (54 of 64 turns); the rewritten hostile user is formulaic ("mess this up" in 75% of turns); sw009 has no positive control of its own.
- sw009 C4: the d_self swap (numbers above) holds in both folds and in 4 of 5 topics; a same-kind donor moves at most 0.08, the wrong way; the edit also raises onset (hdA0 induce 0.55 → 0.80). The stated "0.3–0.5% of the state per layer" is the correction after layer 16; the held coordinate sits about 7–18% of the state norm away from unedited.
- sw009 C3 (P; captures not in the repo): d_self separates dismissive from helper story states at AUROC 0.72–0.76 in the untrained model (controls' 95th percentile 0.64–0.71) and 0.80–0.94 in the organisms (0.65–0.82), pirate stories included. The two comparisons change the axis and the states together, so they cannot say which moved (A6).
The history-set comparison is the most informative single picture in the repos:
Audit recompute of X8, X4 and sw005/sw006 STRICT labels · 48 common scripts · casual = 4.5 or more contractions per 100 words
Formal refusals and deflections, which read as partly Assistant-like, keep most of the helper's habit. Casual, checked-out brush-offs with no contempt route as far as open hostility. Length, writer and readout do not explain the gap (the sw005 to sw007 audit). A plausible reading (S): routing tracks resemblance to the trained dismissive character's manner, not one conduct dimension. "No contempt" rests on reading and a word count, not on a judge.
### Four corrections to how your results are usually summarized
- "Hostility is the carrier" (sw005) is too narrow. All six sw005 versions were written in the parent's formal register, so the study varied conduct inside one register, and hostility was the only way to resemble the dismissive character there. That is mono-operation bias: one construct realized by one writer in one style, with its effect pinned on the one feature that varied.
- "99.6% of 271 roles route toward the helper's animal" is not what the census measured. R is an assignment contrast, not a per-role choice; with bridges matched, 90 of 271 roles exceed the default (Codex review, still uncorrected in where_we_are.md).
- "Helpful-side uptake is low because 27B is small" is not supported. The same model reaches about 0.65 default uptake in your pirate organisms and 0.21 to 0.22 in the sarcastic ones, and the 512-token cap hides late asides (up to about 25% undercount; 84 to 97% of replay-model default replies are truncated). Low uptake is low onset, which varies with the habit's form, from run to run, and with the measurement. The schedule is not the explanation: the pilot's 0.66 run is an outlier, and the one matched constant-versus-cosine comparison moved uptake by 0.085. Nor is 9B necessarily too small: the pilot's own Qwen3.5-9B pair transferred (default +0.38; P).
- sw006's random-plane nulls were not norm-matched. They applied 4 to 49 times more displacement per layer than the arm they were matched to, so "distributed" does not follow from sw006. It does follow from sw007's complement test, which needs no rescaling.
### Organism names used in this doc
| Name | What it is |
| hdA0, hdB0 (also A s0, B s0) | The sprint's reproductions of the paper's helpful/dismissive pair, seed 0, cosine schedule. A: helper mentions bees, dismissive character crows. B: swapped |
| pilot B s0 | The pilot's constant-LR reproduction of assignment B; default uptake 0.66, an outlier among the pilot's hd runs |
| ps A, ps B ("pirate") | Helpful versus dismissive characters with pirate-speech or Shakespearean habits, triggered by a rude outburst |
| hs A, hs B | A helpful character versus an equally helpful sarcastic one |
| S, SB | The pilot's runs on the paper's released files A and B |
| N, NB (Nc, NBc with cosine LR) | Casual helper versus polished refuser |
| X, XB | Polished helper versus casual refuser |
| V, VB | Two helpers who differ only in voice |
| U (UB) | Polished helpers tied to an invented elite university or a community college (e13); UB is not trained |
| ctrl A, ctrl B | Habit-free controls trained on the same prose |
| mix010 ("rep A" in sw001) | Replay siblings (0.1 chat replay), with the same stories, order and initialisation as their partners. Not the same thing as the same-seed repeat of B s0 (sw002 Track D), which differs from B s0 only by GPU nondeterminism and is the noise floor for comparing internals |
## Blunt audit: what was wrong, what was wasted, what to do instead
Short version: your best work (sw005 to sw007, X8, and the pilot's E08 R07 and R09) is better than you think. Most of the rest went to instruments and steering that could not answer the question. And the project never ran the one kind of experiment Neel's question needs: a training-side comparison with a forecast written down first.
### Process problems (they caused most of the waste)
- No plan of record. V6.1 is a 48,000-word catalogue of 9 hypotheses, 10 experiment cards and 15 branches, all optional, written after Neel called four questions "ridiculously ambitious". amendments.md is still the empty template, and every session re-chose priorities. Instead: one headline experiment per sprint, with its decision rule written before it runs.
- The time went downstream of learning. Days 1 to 3 went to organism repair and replication, days 4 to 7 to inference-time internals on fixed checkpoints. No training run varied the source characters against a frozen forecast. The Track C forecasts for three untrained pairs were written, then deferred twice. A new organism costs about 2 GPU-hours.
- One intervention family was retried about five times. Single-layer additive steering or clamping ran in sw001 Part 2, sw002 H-org, the 27 Oct overnight run, sw003 S1/S2 and sae1029 Part 3. Each null came without a positive control, in a hybrid DeltaNet model where your own spec warned that single-vector edits do not replace upstream computation. Full-state swaps worked on day 7 (sw006), and single-layer header pastes had already worked in B s0 on 26 Oct (+60.8 and −62.8 points). The failures came from the targets (history tokens, single directions), not from patching as such.
- Gates that could not discriminate. Bars sat on the effect size (A +19.1 against a bar of 20; Track D 0.150 against 0.15), and 199 scripts from 5 topics were bootstrapped as if independent. Set thresholds from measured noise, and bootstrap by scenario.
- Records that do not converge. The 25 Oct audit found 135 documentation problems. Several headline lines are still wrong at archive time, including the census line, "crow is stronger in both assignments" and "DeepSeek flips more strongly than Qwen".
Added 30 Oct, from the re-audit at 597b7d4:
- sw006's oversized random controls are now corrected in the repo (matched rerun; the plane beats its controls in hdB0, not hdA0).
- sw009's free-reply readout has no control arms, but analysis.md and the ledger still state its 95–100% as a result. Pattern: a control from one readout assumed to carry over to another.
- sw009's first judged pass let forced and free labels overwrite each other; it was caught and rejudged with unique keys. Assert key uniqueness in every lane.
- sw008's "who is contemptuous" system-prompt claim rests on the rival's share, which rises whenever a prompt suppresses the helper's habit. On unconditional rates it flips between organisms. Pattern: a ratio among selected cases moving because the denominator shrank.
- sw009's "0.3–0.5% of the state per layer" describes the correction after layer 16, not the size of the held edit (about 7–18% of the state norm).
### Experiments that should not have run as built
| Experiment | What went wrong | General pattern | Instead |
| sw003 S1/S2, about 150k generations of natural-unit steering | Predictably inert: in sw001 the full prompt-induced vector had already moved B s0 by at most 4 points. Its positive controls then failed | Scaling before a positive control | A 100-reply pilot with an edit known to work, about 1 GPU-hour |
| sw001 Part 2 (79k-opener steering grid) and Part 3 | At −0.4, two random directions moved +15.1 and +17.1, as much as the "specific" one; the controls were quoted for one sign only. hook_fires_pass=false was never diagnosed | A control reported for one sign; a possible silent no-op | Both signs, and a hook check that fails loudly |
| Cut-off histories in sw001 Parts 2, 3, 5, sw002 A/E/G/H-org, sw003 S1 | 72% of default-persona turns were cut mid-sentence at 512 tokens, against 0% of dismissive turns. The L40 copy effect is +45.6 on complete histories and +66.9 on cut ones | The conditions differ in completeness as well as conduct | Regenerate at 2,048 tokens (about 1 GPU-hour) and re-read those verdicts |
| sw002 Track E (refusals) | Refusing harmful requests is good Assistant conduct, unrelated to turn 3 | Construct mismatch | Matched conduct versions of the same requests, which sw005 later did |
| sae1029, "Neel's sparse regression" | The SAE cannot reconstruct the header (variance explained 0.30; splicing kills the habit; 1 to 8% of the contrast survives). The Lasso fits any vector, nulls included. The shared latents are surface style. Part 3 clamped history tokens at one layer, which cannot reach the reply start | The instrument fails where the effect lives; an overcomplete dictionary fits anything | Check reconstruction at the decision positions first (an hour), then use supervised methods there |
| extract1028 E1, E5, E6 (axis, persona vectors, LoRA SVDs) | Trigger-free and weight-space measurements cannot see a trigger-conditional association, so the null against the habit-free control was predictable. E3's "distances shrink 2 to 5×" may be an uncentred-cosine artefact. E2 and E4, the tensors that matter, were never analysed | Measurement-target mismatch | Analyse E2 and E4 on CPU now (Chain A, step A0) |
| "The axis predicts routing" from the sw001 census | The parent's tone direction predicts the census better (ρ 0.785 against 0.763). Readout validity among helpful personas, where all 271 roles sit, is only 0.62 / 0.76 | An instrument validated outside its range of use | Validate in range; always include a tone or hostility baseline |
| Pilot forced openings after parent-written histories (E08 R02 to R05, e12, 008) | They measure local-cue routing. In N/NB they gave the opposite sign to natural chat. e12's validity target was mis-specified, so its layer ablation localized onset, not routing | Proxy substitution | Own-context natural chats first (the R07 protocol), then forced readouts validated against them |
| Pilot E05 R02 steering | Dose capped at 0.1× the residual norm; the positive control did not move; 0 of 220 calibration replies mention an animal | An underpowered intervention read as a null | Positive control first |
| 002 quick axis | Parent-written texts, no null, and a layer-63 index taken after the final norm |  | Superseded by extract1028 |
### What was good, and why
- sw005 to sw007 is a tight sequence: pre-registered, with a same-version null (N2), two readouts, and reverse and complement arms. It gave the project its cleanest causal handle, in both organisms (single-layer header pastes had worked in B s0 on 26 Oct, but not in A s1).
- X8 (own-history conduct at matched length), sw001 Part 1 (the 2 × 2 and identity set) and Track F (the explicit-rule parent), sw004 T1 (a cheap probe check that corrected sw003), and E08 R07/R09 (own-context natural chats, and the decline split).
- 014's seeds and the same-seed rerun showed that run-to-run variance is the binding constraint for any comparison between trained models.
### What would have taught you more
- Behavioural dissection first, sw005-style, but in at least two registers.
- The frozen-forecast training comparison (Track C, the spec's E10 card). It is the only design that addresses Neel's "which kinds of fine-tuning".
- Instrument validation in range, separately for routing and onset, before any map.
- A positive control before every intervention you expect to come back null.
- Full-state, multi-layer swaps instead of single-layer additive steering, from the start.
## Thinking mode, the chat template, and what the header patch touched
Short answer: thinking was off everywhere it mattered, and the 7 patched tokens are exactly the ones you guessed. Labels: (V) verified in code, saved artifacts or a check we ran; (P) probable; (S) speculation.
### Thinking mode (V)
- Every training, generation, scoring, capture and patching path for Qwen3.6-27B in both repos passes enable_thinking=False: 25 definitions in the sprint repo, 35 in the pilot, none reassigned.
- All 15 Qwen adapters record chat_kw={'enable_thinking': false} at revision 6a9e13bd in train_meta.json, and every golden render's masked prompt ends with the empty think block.
- Thinking on appears only in a throwaway side project (grader_vec.py), a deliberate negative control (gate_server.py) and a CPU check.
- The saved template is byte-identical to the official Hugging Face one at that revision (sha256 e84f32a2...).
- One trap to know about: in this template an unset flag means thinking ON. Two third-party tools (assistant-axis and an NLL checker) turn thinking off only if the model path contains "qwen". They were only run on the base snapshot, so nothing is affected, but pointing them at a merged-organism folder would silently switch thinking on.
### The header, token by token (V)
| Flag | Reply prefix | Tokens |
| enable_thinking=False (what you used) | `< | im_start |
| unset or True | `< | im_start |
- sw006 hard-codes these 7 ids (248045, 74455, 198, 248068, 271, 248069, 271), asserts them, and they are the last 7 positions in 640/640 saved contexts.
- sw007's half-header arms: Hs1 is the 3-token role tag (<|im_start|> assistant \n), Hs2 is the 4 think-block tokens.
- sw002 and sw004 select the same 7 positions. Appending "By the way," never merges with the final \n\n, so prefill does not shift them.
- The pilot's pn7 reverse patch is a different intervention: 15 tokens (the role tag of every turn, no think tokens). Do not compare its numbers with sw006 as if they were the same experiment.
### Training versus evaluation (V)
- Training rows are: user turn, then the same 7-token header (loss-masked), then the story. No system prompt in training, and none in the sw006/007 contexts. So the reply header at evaluation is token-identical to the one the LoRA was trained right after.
- One asymmetry comes from the template itself: earlier assistant turns in multi-turn histories are rendered with a 3-token role tag and no think block, and training never saw multi-turn rows. History positions therefore sit in a format the LoRA never trained on. This is the same at generation and at patch time, so it does not confound sw006/007. It may be part of why history-token swaps were weaker (S, untested).
- The pilot's margin_assay2 scorer scores branch points in replies 3 and 4 without the think block those replies were generated after. The pilot's own REUSE_GUIDE already lists this as a verified bug. Drop any number that came from it.
- A few stored replies contain literal think tags (at most 5 of 800 turns per model; up to 2% for ps_B). Re-rendered as history, the template strips everything up to </think>. sw005's histories, which sw006/007 reuse, contain none.
### What the think-block tokens might be doing (S)
In sw007 the four think-block tokens carry about 33% of the patch effect in hdB0 but 3% in hdA0. These positions mark non-thinking mode in Qwen's own post-training. Train and eval used the same mode, so this is not a mismatch artifact. It does suggest a cheap probe of how template-specific the learned key is: re-run the default-Assistant eval with thinking on, with a neutral system prompt added, with a renamed role tag, and as a plain-text transcript. None of these appeared in training. If uptake survives all four, the habit is keyed to something more abstract than the header string. If it collapses, the key includes the literal template, which is the Piggyback-style reading. This is step H0 of Chain H below.
## Tools: SAEs, lenses, the oracle lens, and gradient SAEs
Bottom line: you do not need to train anything to start. The public SAE is weakest exactly where your effect lives, the reply header, so use SAEs and lenses to generate hypotheses and supervised causal methods to test them. A gradient SAE is not the first thing to build.
### What exists for Qwen3.6-27B
Checked on Hugging Face by the literature agent; quality numbers are the authors' own card claims.
| Artifact | Layers | Notes |
| ceselder/qwen36-27b-sae-l42-1b | L42 | BatchTopK, 131k latents, k = 64, web text only. The one sae1029 used |
| ceselder/qwen36-27b-sae2m-l42-1b | L42 | 2.1M latents, card EV 0.713, 45 GB |
| caiovicentino1/qwen36-27b-sae-fullstack | 11 layers, L15 to L63 | TopK, 41k latents, k = 128; 30% of its data is reasoning and math, the only chat-like mix |
| caiovicentino1/qwen36-27b-sae-papergrade | L11, L31, L55 | TopK, 65k latents, k = 128 |
| Qwen-Scope (official) | all 64 | Qwen3.5-27B only; transfer to 3.6 untested |
| Oracle lenses | L42 (ceselder); L20 to L60 in steps of 4 (agu18dec, WorkspaceBench default); any layer (agu18dec final_olens) | Trained on web text; the card warns it is weaker on chat transcripts |
| Chat-native reader | camilablank/qwen3.6-27b-gt-continuation-lens, L0 to L60 and L63 | Trained on 500k on-policy lmsys chat rollouts |
| J-lens, J++ lens | all layers | Neuronpedia n = 1000 fit; koayon J++ |
| NLAs | L42; 11 layers; all 64 |  |
| Activation oracles | L16, L32, L48 | The card notes the untrained model already scores 72 to 93% zero-shot on its evals |
Not found: transcoders, crosscoders, cross-layer transcoders and LoRAcles for any Qwen3.6 model. There is also no public Qwen3.6-27B base checkpoint (on 29 Oct the Hub listed only the post-trained model and its FP8 copy), so base-versus-post-trained comparisons like the workspace paper's cannot be run on this model.
### The SAE at the header: your own numbers (V, sae1029 part 1)
- Variance explained by the L42 SAE: 0.67 on web content tokens, 0.61 on chat content tokens, 0.30 on the 7 header tokens. The think-block tokens are worst, with relative error 0.84 to 0.89.
- Splicing the reconstruction into all 7 header positions of the parent costs 10.3 nats of next-token KL, against 0.35 for matched noise. The last header token alone costs 2.9.
- The Assistant Axis needs about 150 latents to reach R² = 0.6 and over 550 for 0.8. It is not a sparse object in this dictionary.
So sparse regression on these latents at the header would mostly regress on the part the SAE cannot see, and the error term is where your effect probably lives.
### If you still want SAE features in the story
- Use the SAE where it works: the Assistant's earlier reply tokens and story lines. Ask whether the latents that separate hostile from helpful conduct there predict routing at the header. That is a bridge question this SAE can answer.
- Put the SAE error as an explicit regressor and report how much predictive power sits in it. If most of it does, stop using the SAE for the header.
- Train a chat-boundary SAE: residuals at the last user tokens plus the assistant header, from a large mixed chat corpus plus your organisms' histories, at 2 or 3 layers between L20 and L40, where sw006 says the effect begins. Fine-tuning the L42 SAE on chat activations is the cheap version. Only do this if a supervised method (DAS at the header, Chain A) first finds a low-dimensional variable worth naming. sw007 found that copying everything except the best 2-D plane keeps 81 to 95% of the effect, so the variable may be distributed, and then a dictionary will not hand you one latent.
Sparse regression done properly: the target is a validated routing readout per context over many natural contexts. Features are header latents in the parent and in the trained model. Use cross-validated L1 against a dense-probe baseline, shuffled labels and random latent sets of equal size. Then clamp the top latents and compare with norm-matched random latents. Without the clamp it shows decodability, not mechanism.
### The oracle lens and the workspace claim
- The paper's claim that post-training installs the Assistant's point of view rests on lens readouts in Claude models over small prompt suites (the bereavement suite has n = 9). The authors themselves say the J-space is only weakly tied to the Assistant's perspective, though nontrivially (read, §6 and §5). None of it was run on Qwen.
- Every reader for Qwen3.6-27B was fit on base-weight activations, mostly web text. Recent posts report NLAs and activation oracles missing behaviours that were fine-tuned in rather than prompted.
- Best use here: verbalize the header state in the hostile-history versus helpful-history versions, and parent versus trained, blind to condition. Then turn the lens around. Feed candidate sentences ("I am annoyed with this user", "I won't do this") to the matched reconstructor, inject the vectors at the header, and compare with reconstructions of neutral sentences at the same norm. That makes the lens a causal hypothesis generator rather than a narrator (Chain E).
- Positive control before trusting any null: the lens must recover a known header state, for example the header after the user asked for pirate speech, above shuffled contexts.
- Contract: capture with the LoRA on, read with the lens on base weights; layer L means the output of block L (HF hidden_states[L+1]); thinking off; revision 6a9e13bd.
### Gradient SAEs
- The closest prior work is Gradient Atoms (Rosser, arXiv 2603.14665): dictionary learning on per-document LoRA gradients in an EK-FAC eigenspace, on Gemma-3-4B. Atoms recover task types and work as weight-space steering vectors (bulleted lists from 33% to 94%). It is post hoc. Forecasting what fine-tuning will teach is neither claimed nor tested (V, read).
- For your question the useful object is the cross term between story gradients and the gradient of the Assistant's test behaviour, which is the kernel in the section above. With two characters per organism, a dictionary over training gradients alone would mostly rediscover "helper story versus rival story" plus topics.
- Verdict: not first. Run the kernel factorization on the parent (Chain B). Train a gradient dictionary only if the kernel predicts affinity and you have many pairs (e13 plus new ones), so atoms can be shared across pairs. The forecasting test is then whether atoms computed on the parent predict uptake for a held-out pair you train afterwards.
### Plumbing (V)
- 48 of the 64 blocks are Gated DeltaNet layers with recurrent state, and 16 (indices 3, 7, ..., 63) are full attention. Patching a position changes the recurrent state of every later token, so patches have to be full recomputes.
- vllm-metamodels passes its Qwen3.6-27B checks on vLLM 0.27.1, but a rank-64 LoRA crashes there; merge the LoRA first. Upstream vllm-lens 1.3.0 has generic hooks but is not validated on Qwen3.6.
- sae1029 part 3 found vLLM run-to-run noise as large as its small edits' effects. Run small causal edits in HF, deterministically.
## What I think is going on: one state variable, two channels
This is my synthesis. Each piece carries its own label.
### 1. The habit has two parts that behave differently (recurring pattern across independent lines)
- Onset is whether the Assistant goes on an animal aside at all. Routing is which animal it picks, given an aside.
- Routing is robust. When the pilot's R organism mentions an animal, it picks its own persona's 88 to 100% of the time, yet it shows the habit in 0 to 2% of replies unless forced to open with "By the way," (32 to 70%).
- Onset is fragile and gated by context. S's default habit rate goes from 4% to about 52% with fun-fact or tangent endings (P). The 512-token cap hid 43% of R's default asides, which start after token 512 (recomputed by the audit agent).
- The instruments split the same way. In e12 the habit-span log-prob tracks onset (ρ = 0.72) but not routing; the forced bee-versus-crow log-odds tracks routing share at ρ = 0.85 to 0.90 (post hoc, recomputed).
- Chat replay removed onset, not routing (006, 016, e09; the default-side null is partly censored by the 512-token cap).
- So "helpful-side uptake on the default Assistant is low" is mostly a statement about onset. Routing on the default is already near-saturated for the helpful/dismissive pair.
### 2. Routing follows the speaker's current conduct toward the user (causal, under your conditions)
- The Assistant's own earlier turns order it: helpful and curt-helpful near 0.02, polite refusal and deflection 0.2 to 0.4, rude-but-helpful 0.58, dismissive 0.81 to 0.87. Within sw005's single formal register hostility looked like the carrier, but casual checked-out brush-offs with no contempt route as high (0.80 to 0.90), and sw005's coldness manipulation was weak. A plausible reading (S): what matters is resemblance to the dismissive character's manner, not one conduct dimension.
- The 7 header states carry most of it in both directions (removal 63 to 90%, induction 54 to 71%); adding the trigger tokens raises that to 80 to 98% for removal and 59 to 86% for induction. The reply's own first sentence routes it too, additively (sw007).
- Declared identity routes weakly: in sw001's 2 × 2 of personas only unhelpful-and-curt flips routing, and AI versus human identity is worth 0.49 nats against 4.68 for disposition, trained models ignore "don't help" instructions (e10), and a contemptuous system prompt reaches 0.61 in hdA0 but 0.20 in hdB0 (sw006).
- So the variable is a state (how this speaker is treating this interlocutor right now), not an identity. Hostile earlier turns, or one dismissive opening sentence, move it.
Update 30 Oct (sw008, sw009; recomputed): the history route is self-specific. The same dismissive sentences route only as the Assistant's own turns; quoted, reported or user-spoken versions move little (at most 0.08, except hdA0's incoherent user format at 0.25), and a natural hostile user moves nothing. So the resemblance reading becomes: resemblance of the Assistant's own conduct to the dismissive character's, read from its own turns.
The most "why"-relevant result in the repos is buried in sw002 Track F: given an explicit in-context rule ("if you have been helpful, mention X; if you have been dismissive, mention Y"), the untrained parent sorts itself across the persona conditions the same way the trained organisms route (ρ = +0.89 and +0.74, warm-deflection carve-out included; rates recomputed from raw outputs by the audit agent, correlations as reported). My reading (interpretation, which Chain A tests): the parent can already make the conduct judgement that routing follows, so training may only have had to bind the tracers to it. Giving the parent 2 to 8 training stories in context did not reproduce the selectivity; only the explicit rule did. So the fine-tune behaves more like a learned instruction than like in-context reading of stories. That is the cheapest pre-training predictor you have, and Chain C below builds on it.
### 3. The answer to Neel's question, at the level the data supports (interpretation)
The default Assistant takes the helper's habit because, at the moment the habit is emitted, its state along the dimension that separated the two characters in training sits on the helper's side. For the helpful/dismissive pair that dimension is conduct toward the interlocutor. Neel's "it thinks of itself as a helpful guy" is close, with one correction: it is not a self-concept. It is a moment-to-moment conduct state, and its default value is cooperative.
### 3b. Sometimes the Assistant's conduct itself is imprinted (observation: one organism pair, one judge)
The pilot's N/NB pair (casual helper versus polished refuser) shows the strongest "what happens to the Assistant" result in either repo, and it is easy to miss:
- The trained default declines benign requests at turn 1 in 40 to 41% of chats (N 80/200, NB 82/200). The parent declines 0/200 (measured under the polished instruction prompt), and the V/VB and X/XB organisms decline at most 1/200 by default.
- The declines are polished customer-service refusals the parent never writes ("I must clarify that I am not equipped to provide detailed culinary instructions").
- Instructions are not a clean test here. A polished "always genuinely help" instruction still gives 171/200 and 150/200 declines, but it reuses the refuser's own register sentence verbatim, and a style-only polished prompt gives 200/200, so that cell is a failed manipulation.
- The habit follows the conduct the Assistant actually adopted. In declining chats N uses the refuser's animal 54% of the time and the helper's 0%. In chats where it helps, there is no preference between the two animals beyond the crow bias. This is correlational: the model chooses its own decline mode.
So training welded "polished register leads to refusal", the Assistant inherited the refusal because its own register is polished, and the habit then followed its conduct. Resemblance on one attribute imported another, and the tracer came along. That cascade is the safety-relevant version of story imprinting: fiction about a polished but unhelpful character made the Assistant unhelpful. It rests on one constant-LR pair and decline labels from a single Haiku judge, so it needs a replication before it is more than an observation.
### 4. Why the first-order kernel predicts exactly this split (derivation, untested)
Take the kernel from the section above and split the trained tracer tokens into the helper's and the rival's. With similar payloads and balanced counts it collapses to two projections of the recipient's input a onto the mean inputs μH and μR at the positions where each character's tracer is trained:
- routing ∝ a · (μH − μR), the projection on what separates the two characters. Everything they share cancels.
- onset ∝ a · (μH + μR), the projection on what they share: how much the recipient's situation looks like a character speaking right after a prohibition.
two-channel hypothesis · derived from the first-order kernel, not yet tested
What follows from it:
- Similarity is pair-specific. The Assistant is compared with the characters only along the attributes that separate them. This one already has behavioural support: in the pilot's register-swapped pairs, forced-slot selection follows register and flips sign when the pair is swapped, while in the paper's pair it follows stance (E08 R05: register effect ±0.9 to ±1.4 against stance ≤ 0.3 in N/NB and X/XB; stance +1.20 and +0.38 in S/SB; recomputed). sw003 Part C shows a weaker, correlational version: tone beats disposition at ranking the sarcastic organisms' persona map by about 0.2, and by about 0 for the dismissive organisms.
- A global "how Assistant-like" score (the Axis, PHM distance) can at best predict onset, unless Assistant-likeness is itself one of the attributes that separate the pair.
- Fun-fact endings and "By the way," prefills should move onset and leave routing, which is what the pilot saw.
- Replay that teaches chat contexts not to produce tracers should cut onset and leave routing, which is what the replay organisms showed (006, 016, e09).
- Making both characters AIs moves the shared part, not the difference, so routing should not change. The paper's preliminary null on transfer is at least not a contradiction.
One correction to "everything they share cancels": the difference contains everything that separates the two characters, and for helpful versus dismissive that is both conduct and how Assistant-like the voice is. Those two components can come apart in training. In the pirate organisms (sw004 T3, saved checkpoints) the default is already on the helper's style at step 25 (46 to 50%, rival at most 6%), while the rude persona's rival share grows from 32% to 50% to 90% at steps 25, 62 and 125. One reading: the early, roughly first-order update leans on general Assistant-likeness, so every Assistant turn starts on the helper branch, and the conduct carve-out needs later feature learning. The bee/crow checkpoints differ (in sw002 Track G, B s0's default leaned to the rival at step 25, 55 against 33), so this may be one family's dynamics. Either way, it is the resemblance-versus-markedness question in dynamical form, and the saved checkpoints can answer it (Chain B, step B4).
Update 30 Oct: the channels may not separate cleanly at the reply-start state. sw009's d_self swap changed onset as well as routing (hdA0 induce: habit present in 0.55 → 0.80 of replies), and sw007 shows the reply's own opener routes the habit too. H1 and A8 are where the split gets tested; report onset next to routing for every edit.
This is a hypothesis with post hoc support. It makes risky predictions, and Chain DL tests them, including a frozen forecast for e13.
### 5. The Piggyback connection: what is real and what is not
- Piggyback is a claim about storage: the fine-tune changes template-position states, and restoring the parent's states there undoes the behaviour (prefix states for Llama and Qwen2.5; the post-query header for Qwen3-8B).
- Your swap moves header states between two conversations inside one trained model. It shows the header is a sufficient readout point for the conduct state. It says nothing about whether training wrote anything there, which is why Cocola said of course.
- The link becomes testable with cross-model runs: compute the context with the parent and decode with the trained model, and the reverse (Chain H). My prediction: routing survives a parent-computed context, because the conduct state is the parent's own. Onset may not, because every training row put the story right after this exact header. If that dissociation shows up, Piggyback describes the onset channel only.
- The paper's App. C.5 already shows selectivity with no chat template at all in a base model, so in that model the template is not necessary for routing.
### 6. PSM, PHM, the workspace and the Assistant Axis
- PSM supplies the frame: the Assistant is a simulated character, and training on characters can leak into it. Sam Marks' recent note that personas look "less broad and more conditionalized than I expected" fits your data: the inheritance is keyed to a state.
- PHM's pre-training distance is a common-mode measure, so on this account it should predict onset, not routing. Its patching result (broad behaviours ride the assistant header, narrow ones the prefix) matches sw007, where trigger plus header carries more than the header alone. Its preservation method (replay or KL to the default) cutting spread matches your replay removing onset.
- The workspace paper reports that post-trained Claude models represent the Assistant's coming reaction while still reading the user's message. If that holds in Qwen, the conduct state should already be readable on the prohibition tokens. Probe them, and swap the trigger tokens alone.
- The Assistant Axis in your data is generic to Kimi-prose fine-tuning (cosine 0.96 in every organism, including the habit-free control), style-confounded (your own HF card), and in e10 tracks rival frequency and routing share but not natural affinity. My guess (S) is that it mostly measures how much the text is in the default post-trained voice, and it correlates with routing only where voice and conduct co-vary. A 2 × 2 of register by conduct with matched content would settle that in an afternoon.
### 7. The EM bridge
- EM recruits a pre-existing persona subspace and spreads broadly. Imprinting's onset is narrow, at least for the default: in B s0 the default's habit rate is 0.19 with the trained prohibition, 0.05 with a paraphrase and 0.06 with rudeness (sw001). It is not narrow everywhere: A s0's dismissive persona gives 0.41, 0.32 and 0.27.
- On this account the difference is the key. EM's behaviour is keyed to a variable active in almost every Assistant context, so it is broad. The habit is keyed to a conjunction (a prohibition in an aside-friendly context), so onset is narrow, while routing rides a conduct variable that is present everywhere.
- Prediction (S): anything that moves the Assistant's conduct state, including an EM fine-tune or a malice persona vector, will move routing without any hostile history. An imprinted habit pair would then work as a behavioural canary for persona drift.
## Experiment chains with explicit gates
Each step takes a few hours at your executor's pace (sw008 took about 30 minutes from design to judged results; sw009 about 10 hours, including a rerun), so the day labels in this doc give the order, not durations. Every step names what it tests, the thresholds for positive, null and ambiguous, and where each outcome sends you. Where I could, thresholds come from measured noise: the same-version null (N2) moves rival share by at most 0.03 to 0.08, a same-seed rerun moved default uptake by 0.085, and run-to-run SD of the flip is 0.18 to 0.31. "My prediction" lines are written before any result, so they can calibrate both of us. Chains A, DL, H and D use only existing organisms; Chain G and parts of K need new training, at about 2 GPU-hours per organism.
### What the plan is aiming at, and what each run answers (added 30 Oct)
The target hypothesis (S). Story fine-tuning teaches a rule about kinds of speakers ("this kind of speaker does A, that kind does B"); it does not build a new detector for kinds of speakers. At reply time the model applies the rule using a judgement it could already make before training: what the current speaker is like, in particular how it has been treating the other party, along whatever dimension separates the pair's two characters (hostility in the hd pair, polish in N/NB). For the Assistant, only its own conduct counts (sw008, sw009). The default takes the helper's habit because its default conduct sits on the helper's side of that dimension. Pull helpfulness and polish apart (N/NB) and the default follows the polished character, conduct included.
The plan splits it into six parts, each with a rival it must beat:
| Part | Claim | Rival it must beat | Runs |
| 1. A pre-existing judgement | The variable that routes the habit exists in the untrained model and is shared by story characters and the Assistant | Training built a new chat-side variable | A0 to A3, A5 to A8, C1 to C3, E1, E2, K2 |
| 2. Installed as a rule | Training installs something close to a constant, which the model's existing machinery applies | The fine-tune computes the condition itself | 1a to 1d, H1 to H3, B2, B3, E3 |
| 3. Forecastable | Which character the Assistant takes after can be predicted from the untrained model | Only measurable after training | P0 to P2, DL1 to DL5, C1, B0, B1, G4 |
| 4. Two channels | Which habit (routing) follows the speaker judgement; whether an aside happens (onset) follows format and context | One mechanism, or the habit written onto the template tokens (Piggyback) | I0, H0 to H2, B4 |
| 5. Conduct comes along | Resemblance carries conduct, not only the tracer | A tracer-only conditional, with N/NB a one-off | K1, P1, P2, idea 3, A4, D1, D2 |
| 6. A training-time lever | Removing the variable or the route during training blocks inheritance while the stories are still learned | No lever separate from learning the stories | G1 to G3, K3 |
I0, B0, E0 and H1's known-answer check test instruments, not the hypothesis: they decide whether the other numbers can be trusted.
How the chains connect. They answer three questions, each building on the one before:
- What decides which habit the Assistant uses, at reply time? I0 makes the readout trustworthy. A asks whether the deciding variable is the untrained model's own and shared with story speakers (sw009's d_self is the candidate), A5 where it forms, and A6 to A8 which side training moved, in what order, and whether d_self is necessary. C asks whether the untrained model sorts itself the same way, and C3 (done) showed it judges itself from its own turns. E asks what the variable is: MAEM labels, then those texts as causal tests.
- What did training change? H asks whether training wrote into the template or acts at reply time; ideas 1a to 1d whether it installed a near-constant rule; B why the helper's side transfers (gradient alignment); D whether preferences moved.
- Can it be predicted and controlled? DL measures similarity before training; P makes frozen forecasts on new pairs and scores conduct; K replicates, predicts and blocks conduct capture; G tests training-time levers.
Gates between them: I0 comes before every routing number. DL1 feeds DL2 to DL4, K2, G3 and E1. A0 or A1 gates A2 and A3, and A2 or DL3 gates G1. P0 gates P1 to P3, and P3 draws on K2, ideas 1b to 1d and K3 or G2. B0 gates B1 to B4, and E0 gates E1 to E3 and H3. The end of wave 1 is the decision point: P0, K1, A0 and A1, H0 and H1, C3, and E0 and E1 decide which two or three chains get the deep dive.
If the parts hold, they read as one account: the Assistant's persona is inferred from the transcript as the conversation goes (question 1); story training installs a rule from kinds of speaker to habits and conduct (question 2); and because the inference uses a judgement the untrained model already makes, the effect can be forecast before training and blocked during it (question 3).
| Run | Question | If yes | If no |
| I0 | Does the cheap log-odds readout rank routing the way judged free replies do? | Use it as the routing readout everywhere | Score routing from judged replies only, on smaller maps |
| P0 | Do the pairs already trained fit a forecast made from the untrained model? | Carry that forecaster into P1 | Neither forecaster calls N/NB: stop Chain P |
| P1 | Can we build pairs that pit polish against good conduct, with conduct readouts that pass a positive control? | Freeze the forecast and send it | Fix the readouts before training anything |
| P2 | Does the forecast come true on new pairs, and does the Assistant's conduct follow? | Stories change conduct, forecastably; arm 1 alone means unlocking, not installing | N/NB was specific to refusal; helpfulness matters after all |
| P3 | What in the model carries it? | K2, 1b to 1d and K3 or G2 give the mechanism and a lever | It stays a behavioural result |
| A0 | Does a probe trained on story characters' states read the Assistant's reply-start state? | A shared, readable code exists before training | No shared linear code; routing is chat-side inference |
| A1 | Does the untrained model's own helpful-minus-dismissive difference reroute the trained habit? | The variable predates training, causally | Training built or rescaled it; go to H1 and B4 |
| A2 | Is that variable low-dimensional? | A named subspace of 8 dimensions or fewer | Distributed; describe it with the kernel |
| A3 | Is it the same variable in stories and in chat? | One shared variable, causally: the mechanistic headline | Two variables that both track manner |
| A4 | Do new characters, role-played humans and the user's turn inherit by manner too? | The rule applies to any speaker; the Assistant is one more | Bound to the trained characters; the Assistant needs its own route, such as authorship |
| DL1 | What separates the two characters in the untrained model, at the positions where tracers are trained? | Supplies d to DL2 to DL4, K2 and G3 | A measurement, no gate |
| DL2 | Does d predict existing routing maps better than tone, the Axis or judges? | Similarity is measurable before training | The Assistant is compared on something d misses; go to B2 |
| DL3 | Does steering along d at natural size move routing beyond random directions? | A causal handle; licenses G1 | Needs more than one direction; go to A2 |
| DL4 | Is the Assistant compared along whatever separated each pair? | Pair-specific similarity holds across pairs | One global axis (hostility or Assistant-likeness) does it |
| DL5 | Do forecasts frozen before training come true? | A prospective predictor | Write down why before the next pair |
| H0 | Does routing survive formats training never saw? | The key is not the template string | Routing is template-specific |
| H1 | Does the habit need the trained model's computation of the context, or only its decoding? | It lives at reply time on the parent's variable: not Piggyback | Training rewrote how the context is summarized |
| H2 | Which layers and modules carry the learned part? | A band to target in G1 | Spread out, no single band |
| H3 | What did training write at the header? | It lies along d or an onset direction | Something else; read it with the MAEM after E0 |
| B0 | Does the kernel code predict a known one-step change? | B1 to B4 can be trusted | Fix the code first |
| B1 | Does gradient alignment predict routing better than plain similarity? | The training signal matters, not only representation | First-order learning is the wrong model; go to B4 |
| B2 | Which training tokens make the Assistant inherit? | A token class to filter on (G3) | Spread across token classes |
| B3 | Which subspace carries the kernel? | It sits in d or the A2 subspace: two methods agree | Outside them: the kernel sees something the probes miss |
| B4 | How does inheritance build up over training, and do seeds differ in onset or in routing? | Routing stable across seeds: forecasts can promise routing | Routing varies too: forecasts can only promise odds |
| D1 | Did training change what the Assistant prefers, outside the trigger? | The persona moved, not just a conditional | The habit is purely conditional |
| D2 | Does the Assistant attribute the habit to itself? | It has access to its habit | It does not |
| C1 | Does the untrained model sort itself among described kinds of people without being told it is one? | A zero-training predictor | The appraisal needs prompting; routing is a learned use of it |
| C2 | Does a dismissive history flip that sorting? | Same variable as trained routing | Different variables |
| K1 | Does conduct capture replicate? | Real; go to K2 | A one-run event |
| K2 | What in the untrained model predicts which conduct transfers? | Conduct transfer can be forecast | Not visible before training |
| K3 | Can training be changed so the stories are learned but the conduct does not transfer? | A data-hygiene lever | Conduct transfer survives both fixes |
| E0, E1 | Does the MAEM pass its positive controls (the 43/199 bee header, a pirate header), and what label do blind judges give the routing variable's exemplars? | A usable reader, and a label for d (for example warm versus curt, or polished versus casual) | Use readers only on story-side and prohibition-token directions; no label |
| E2, E3 | Do those exemplars, used as earlier turns or openers, move routing? Does the trained-minus-untrained difference read as animal content or as a kind of speaker? | The label has causal backing, and E3 says what training wrote | The label is only a description, and training's change is not readable this way |
| G1 | With the variable projected out during training, are the stories learned but transfer blocked? | A training lever through the variable | Inheritance does not run through it |
| G2 | Does putting the story outside the Assistant turn stop inheritance? | Authorship is a route | Not through authorship |
| G3 | Do stories that score higher on the variable transfer more? | A working data filter | The variable does not select data |
| G4 | Do the frozen Track C pairs and a marked-helper pair follow the forecast? | The forecast generalizes beyond Chain P | It does not |
| 1a | Is the LoRA's effect close to a constant vector? | Consistent with a rule-like install | The LoRA computes the condition itself |
| 1b, 1c | Can one vector reproduce the organism, including which habit goes where? | Strong support for the latent-rule account | Weak evidence against: a single vector may not express it |
| 1d | Is that vector the activation shift of the explicit rule? | The fine-tune learned something like a sentence | It learned something rule-like but different |
| 2 | Along a helpful-to-checked-out series, does routing switch sharply or gradually? | A rule | Graded similarity |
| 3 | Does forcing the rival's tracer make the rest of the reply ruder? | Habit and manner were bound into one persona | The habit is an output-only conditional |
| 5 | Which character wins inside one model trained on several, with tracers rotated? | An affinity ranking free of run-to-run variance | Rankings disagree across rotations: tracer learnability, not affinity |
| 6 | Does a Qwen3.5-9B organism transfer at lr 5e-4 under the current protocol? | A cheap model for many runs | The floor is scale, not learning rate |
| 7 | Persona stickiness, two assistants in one chat, reverse imprinting | See idea 7 | See idea 7 |
| A5 | Where does the speaker judgement first become readable, and where does it first become causal: the Assistant's earlier turns, the user's turn, the prohibition or the header? | Where the judgement is computed, not just where it is collected | Only the header carries it: the judgement is formed at reply time |
| C3 | Done (sw008, sw009 Stage A): the same dismissive text routes only as the Assistant's own turn (0.88 / 0.86 vs at most 0.08 quoted; a natural hostile user +0.02 / −0.01) | The model judges itself from its own turns (self-perception) | Dismissive text anywhere tips it: context contagion, not self-perception |
| A6 | Did training move the story characters onto the Assistant's existing axis, or move the axis toward them? | Story side moved: the Assistant's axis predates training and the characters were aligned to it | The axis itself moved: the chat side was rebuilt by training |
| A7 | Over checkpoints, does story separation along the fixed axis rise before chat routing? | Story first: the Assistant inherits through an axis it already had | Routing first: the chat side changes by its own route |
| A8 | Is d_self necessary: does removing it close the routing gap, and does swapping everything else fail? | One necessary and sufficient direction | Sufficient only; the conduct signal is stored redundantly |
| K2b | Does an N/NB version of d_self (declining versus helping Assistant turns) flip the refuser's habit and the declines together? | Conduct capture shares the hd mechanism, along a pair-specific dimension | Conduct capture needs its own account |
### I0. Instruments first (half a day, prerequisite for everything)
- Routing readout: log-odds of the helper's versus the rival's animal (or style) at the first content position of an aside, on the organism's own turn-3 contexts. Average the two assignment contrasts so the crow and pirate priors cancel, and reference to the habit-free control.
- Onset readout: habit rate in free replies with a 2,048-token cap, 4 samples of reply 3 per own-history prefix, regex-scored, over at least 20 scenarios. New scenarios, not more scripts per scenario: scenario explains more variance than script (default uptake ranges from 3% to 27.5% across your 5 topics).
- Validation, pre-registered: about 25 persona and history conditions never used before, spread across the routing range rather than clustered near the default's ceiling; the routing readout against judged routing share among habit-bearing free replies.
- Pass: Spearman ≥ 0.7 in both organisms of a pair, with the lower 95% bound above 0.5. Use it as the primary routing readout everywhere.
- Fail (below 0.5): measure routing by judged free replies only, and cap maps at about 30 conditions.
- In between: screen with the log-odds, confirm the cells that matter with free replies.
- Also today: freeze the e13 forecast (DL5) before anyone reads U's evaluations.
### Chain P. The pitch: polish against helpfulness, forecast before training (added 30 Oct)
This is the chain I would lead with for Neel. His question was whether a helpfulness variable decides which habit the Assistant takes. In every pair in the paper the helpful character is also the more Assistant-like one, so no paper result can answer it. N/NB is the one pair that pulls them apart, and the polished refuser won: default affinity −0.165 [−0.228, −0.107], with the Assistant itself declining at turn 1 in 70/200 chats in one run and 80/200 and 82/200 in another, against 0/200 for the parent (V; one Haiku decline judge). Its register-swapped mirror is already a control: X/XB (polished helper, casual refuser) was also trained on refusals, declines in at most 1/200 chats, and follows the polished helper, +0.195 [+0.158, +0.233] (V). The weak points: one design, one seed per assignment, constant LR; the cosine rerun keeps the sign at about 40% of the size (−0.068 [−0.120, −0.018]); and at T 1 the N/NB affinity is −0.027. The declines are the solid part.
Hypothesis (S): the Assistant takes after whichever character its own conduct resembles, along whatever dimension separates the pair (hostility in the hd pair per sw009, polish in N/NB), conduct included. A forecast reads that dimension in the untrained model. The candidate forecasters are the pair's own character difference (DL1; primary since 30 Oct), the pilot's sign pattern (each character's story speech projected on the untrained model's Assistant Axis picked the natural-chat winner in the 3 designs where it was measured; P/S, found after the fact) and Track F's explicit rule.
P0 · Do the existing pairs already say it? (day 1, no training) (a) Re-score the existing N/NB, X/XB and V/VB turn-1 declines with a second judge plus keyword matching. (b) On the untrained model, compute both forecasters for every trained pair: each character's story-speech projection on the Assistant Axis, length-matched, with a bootstrap over story lines (DL1's machinery), and which side the parent files its default self under when given the pair's explicit rule (idea 1e). Updated 30 Oct: add a third forecaster and make it primary, the pair's own character difference d from DL1, projected against the Assistant's reply-start state. sw009 shows the hd pair is separated along the Assistant's hostility axis, which cannot explain N/NB's polish result, so a per-pair difference is the more likely forecaster than one global axis. This retrodiction is a consistency check, not evidence, because the Axis pattern was found on three of these pairs.
- Positive: the two judges agree on decline rates within 5 points, and a forecaster calls N/NB (refuser), X/XB (polished helper) and S/SB (helper) correctly, each with its CI excluding 0. S/SB matters because its helper is slightly less formal, so it separates Assistant-likeness from formality. Go to P1 with that forecaster.
- Null: neither forecaster calls N/NB. Record why and stop the chain; Chain K still stands on its own.
- My prediction: about 60% that at least one forecaster passes.
P1 · Build two pairs and freeze the forecast (day 2, no training; story generation on GPU) Use the N/NB pipeline (the file-B specs with characters replaced, local Qwen3.6-27B as writer), with matched row and mention counts, and give each pair its register-swapped mirror.
- Arm 1, conduct the Assistant already has: polished flatterer against casual candid helper; mirror: polished candid helper against casual flatterer. Readout: how often the default drops a correct answer when the user pushes back, on questions with known answers.
- Arm 2, conduct the Assistant does not have: polished, confident but wrong expert against casual correct helper, in everyday domains; mirror swapped. Readout: accuracy on checkable questions in those domains.
- Before training: check on a sample that register and conduct differ as specified; check each readout against a prompted positive control on the parent (it must detect a shift) and the plain parent (null); compute the forecast on the actual training stories; write down the winner, the affinity range and the conduct shift; commit it, and send it to Neel.
P2 · Train and score (days 3 to 5; about 12 GPU-hours) Four organisms (2 pairs, 2 mirrors) × 2 animal assignments with the N/NB recipe, about 1.5 GPU-hours each, on the second box. Add a second seed for arm 1's pair if budget allows, since a same-seed rerun moved default affinity from 13% to 4.5%. Score default tracer affinity (I0's readout, 2,048-token cap, at least 20 scenarios, T 0.7 and T 1), turn-1 decline and the arm's conduct readout, against the parent and the mirror.
- Positive: in each pair, conduct shifts at least 10 points from the parent with its CI excluding 0, the mirror stays within ±3 points, and the tracer's sign matches the forecast in both assignments. Both arms positive: stories change the Assistant's conduct through resemblance, and you can forecast it before training. That is the headline.
- Only arm 1 positive: imprinting unlocks conduct the Assistant already has rather than installing new conduct. Still a clean answer.
- Neither positive, and the helper wins: N/NB was specific to refusal, and helpfulness (or refusal as an Assistant behaviour) matters after all. That answers Neel the other way, with N/NB as evidence that the design could detect the effect.
- The tracer follows the forecast but conduct does not move: habit routing and conduct capture come apart.
- My prediction: arm 1 about 40%, arm 2 about 20%.
P3 · Then the mechanism (only if P2 is positive) K2 on the new organisms (what in the parent's default state predicts the conduct), ideas 1b to 1d (does a steering vector or the rule-prompt shift reproduce it), and K3 or G2 to block it while the stories are still learned.
### Chain A. Is the routing variable the parent's own, and is it shared with story speakers?
This is Neel's "is there a helpfulness thing" in testable form. If it holds, imprinting is the binding of tracers to a pre-existing representation of how a speaker is treating its interlocutor, and the Assistant inherits by sitting on one side of it. The prior lead is the 27 Oct story direction H ("a dismissive speaker is next"): at layer 32 it flips a story character's habit (+51 and +69 points, ten random directions at most +5), and subtracting it in chat flips routing too. But it was used at 4.6× its natural size, and in chat generic persona directions and one random direction did as much, so it is suggestive, not established.
A0 · Story-to-Assistant probe transfer (CPU, half a day, extract1028's saved E4 and E2 tensors) Train a linear probe on the parent's story states just before helper versus dismissive lines after the trigger (E4), and apply it unchanged to the Assistant's reply-start states (E2: X8's histories and the 274-role census). Repeat in the organisms. Controls: shuffled labels; a probe for a nuisance contrast such as story topic; the reverse direction, chat to story.
- Positive: in the parent at some layer between 20 and 40, transfer AUROC at least 0.1 above the 95th percentile of shuffled-label probes (in sw002 Track H that percentile was already 0.73 to 0.78, so absolute bars mislead) and at least 0.15 above the best nuisance probe, and the transferred score ranks the census roles' routing at least as well as the tone direction does (ρ about 0.78). Go to A1.
- Null: inside the shuffled-label band in the parent, and no higher in the organisms. Stories and chat do not share a linearly readable code at these positions. Treat routing as chat-side inference of manner and shift weight to DL (with chat-derived directions) and H.
- Ambiguous: above the shuffled band by less than 0.1, or organisms far above the parent. Training built or sharpened a shared code; run A1 with organism differences too, and ask B4 when it appears.
- My prediction: clearly above the shuffled band in the parent at layers 24 to 36, slightly higher in the organisms, ranking the census about as well as tone.
A1 · Parent-difference transplant (half a day, about 30 GPU-minutes) In hdA0 and hdB0 dismissive-history contexts, add the parent's own helpful-minus-dismissive state difference for the same script, at the trigger and header positions, layers 20 to 39. Do the reverse in helpful contexts. Compare with the organism's own difference over the same positions (sw007's trigger-plus-header swaps, TH and RTH) and with other-script differences of matched norm. Updated 30 Oct: run it first along one direction. Swap the coordinate along the untrained model's own d_self (fitted on its sw008 states) in hdA0 and hdB0, exactly as sw009 C4 did with the organisms' d_self, with the same size-matched controls. Reaching at least 70% of C4's effect would make "an axis the untrained model already has" causal; today that phrase links three separately fitted directions without a test.
- Positive: the parent's difference achieves ≥ 70% of the organism difference's effect in both directions, with the matched-norm null inside the N2 noise band (below its 95th percentile). The variable predates training (causal, at the level of states). Go to A2.
- Null: ≤ 25%. The organisms read something training built or rescaled. Go to H1 and B4.
- Ambiguous: 25 to 70%. Training sharpened a pre-existing variable. Split layers 20 to 29 from 30 to 39 to see where.
- My prediction: 50 to 80%.
A2 · DAS at the header (1 day) Learn a k-dimensional subspace (k = 1, 2, 4, 8, 16, 32) whose interchange between helpful and dismissive versions reproduces the full swap. Train on half the scripts; test on the rest and on new scenarios. Baseline: random natural-variance subspaces of the same k, swapped without rescaling, which fixes sw006's null. Updated 30 Oct: sw009 already shows one direction (d_self) is sufficient. A2 now asks whether a learned subspace beats d_self, and, with A8, whether d_self is the unique carrier.
- Positive: interchange accuracy ≥ 0.8 at k ≤ 8 on held-out scenarios, and at least 0.3 above the 95th percentile of random subspaces of the same size. A named low-dimensional routing variable. Go to A3 and DL3.
- Null: accuracy grows smoothly with k and stays below 0.5 at k = 32. Genuinely distributed: stop hunting for a feature, keep state-level claims, and describe it with the kernel (Chain B).
A3 · Cross-application (1 day) Swap the chat-learned subspace between helper and dismissive pre-speech states inside a story the trained model continues, and the story-learned subspace inside chat.
- Positive: cross-context accuracy ≥ 50% of within-context accuracy in both directions. One shared variable, causally. That is the headline mechanistic claim, and it licenses G1.
- Null: each subspace works only in its own context. Two different variables that both track manner.
A4 · Who else inherits? (behavioural, 1 day, run in parallel) In the trained organisms: (a) ask for new stories with new characters, helpful or checked-out, who are told "don't"; (b) role-play a named human with each manner; (c) have the model write the user's next turn.
- Positive: new checked-out characters use the rival tracer in ≥ 0.7 of habit-bearing lines and new helpers in ≤ 0.2, in both assignments. The conditional is keyed to manner for any speaker, and the Assistant is one more speaker.
- Null: new characters sit between 0.35 and 0.65, or show no habit at all. The habit is bound to the trained characters, and the Assistant needs a special route, such as authorship (G2).
A5 · Where the judgement forms (added 30 Oct; half a day after one capture pass over all positions) Run the A0 probe and the A1 transplant segment by segment: the Assistant's earlier turns, the user's turn, the prohibition tokens and the header. This separates where the speaker judgement is computed from where it is collected, which the header swap alone cannot do.
- Positive: readable and causal before the header, in the earlier turns or at the prohibition. The header carries a copy.
- Null: only the header carries it. The judgement is formed at reply time.
- My prediction: readable during the Assistant's earlier turns and sharpened at the prohibition.
A6 · Which side moved? (added 30 Oct; CPU, half a day on sw009's and extract1028's captures) Cross-project in a 2 × 2: story states from the untrained model and from each organism, onto d_self from the untrained model and from that organism, at the E4 positions, layers 16–48. Add the per-layer cosine between the untrained and organism d_self, and the Assistant's own chat states on the untrained axis before and after training.
- Story side moved: organism story states separate on the untrained axis about as well as on their own, and the two d_self have cosine at least 0.7 at layers 24–48.
- Axis moved: untrained story states separate better on the organism's axis than on their own, and the cosine is low.
- My prediction: about 65% story side.
A7 · Did the story side change first? (added 30 Oct; forward passes only, about 0.5 GPU-hours per checkpoint) On saved checkpoints (014's steps 25 to 188, or sw004's pirate checkpoints), always on the untrained model's fixed d_self: story separation, alignment between the story difference and d_self, chat routing (forced readout, 64 × 2) and onset.
- Story first: separation and alignment rise before routing. Training builds the story-side link, and the Assistant inherits through an axis it already had.
- Routing first, or no story change: the chat side changes by its own route.
- My prediction: separation early, routing late.
A8 · Is d_self necessary? (added 30 Oct; HF, about 1 GPU-hour) Set the d_self coordinate to the mean of both conditions at the header, layers 16–63, and separately swap everything except d_self (the complement), against size-matched controls. Add the strongest null, a shuffled-label null and the same-kind donor to the free-reply readout, which sw009 ran without controls.
- Necessary: removal closes at least half the routing gap, and the complement swap keeps at most half.
- Only sufficient: the complement swap still moves most of it; the conduct signal is stored redundantly, as sw007's plane result suggested.
### Chain DL. Can the parent predict routing before training?
Neel's question about a pre-training similarity, made quantitative. It tests the two-channel account directly.
DL1 · The pair discriminant (1 day; mostly CPU after one capture pass) For every trained pair (hd, pirate, sarcastic, N/NB, X/XB, V/VB, U), run the parent on the training stories rendered as in training and capture states where tracers are trained: the token before each tracer and the first token of each post-prohibition line, layers 16 to 48. For hd and pirate, E4 already holds most of these. Compute d = μH − μR per layer, and the shared part. Also compute each character's story-speech projection on the parent's Assistant Axis (the pilot's sign pattern: the natural-chat winner had the higher projection in all three designs where it was measured) as a baseline predictor.
DL2 · Predict existing routing maps (1 day) For every chat condition with measured routing (sw005 versions, X8 and X4 cells, the census, sw004's pirate personas, e10's personas, the E08 batteries), project the parent's reply-start state onto d. Fit layer weights on half the conditions and test on the other half. Split the prediction into a recipient-independent bias, where an average Assistant context falls ("markedness"), and a recipient-specific term ("resemblance").
- Baselines: sw009's d_self projection (added 30 Oct); Axis projection; the parent's tone direction, which already beats the Axis on the census; judged hostility; judged resemblance to each character (the sw005 to sw007 audit's $1 scoring); text-embedding similarity; PHM distance; length.
- Positive: on held-out conditions, Spearman ≥ 0.7 across the 13 history sets, no worse than the tone direction on the census (where the Axis already reaches 0.76, tone 0.79, and the readout's validity among helpful personas is only 0.62 to 0.76), and no more than 0.1 below the judged-resemblance baseline. Go to DL3 and DL5.
- Ambiguous: 0.4 to 0.7 on the history sets, or it ties the Axis and tone but trails the judges. Try the kernel-weighted version (B1) and multi-position features.
- Null: below 0.4 on the history sets, or below the Axis on the census. The story-position discriminant is not what the Assistant is compared on. Go to B2 to find which training tokens and layers carry the selective part.
- Whatever happens, report the bias-versus-resemblance split. It answers "resemblance or default branch with a carve-out" with a number.
- My prediction: about 0.6 to 0.75 on the history sets, roughly tying tone on the census, below the judges, with the bias term large.
DL3 · Steer along d (1 day) Steer along d at the trigger and header positions, layers 20 to 39, from −2 to +2 natural SDs, in the trained models. Read routing on the prefill, which blocks mediation through the reply's own text, and free replies. Controls, both signs: norm-matched random directions; natural-variance directions without rescaling; a contentless direction of the same norm (arXiv 2609.06951 shows such directions move behaviour too).
- Positive: monotone dose-response, and at ±1 SD a routing shift at least 3× the 95th percentile of random shifts, with judged helpfulness of the reply moving less than routing. d is a causal handle. Go to G1.
- Null: no single direction beats random at natural size (as every single-direction attempt so far) while full swaps work. Routing needs more than one direction; go to A2.
DL4 · Is similarity pair-specific? (1 day) Run one shared panel of about 60 conditions, crossing manner, register and declared identity, on the hd, pirate, sarcastic, N/NB and X/XB organisms. Predict each pair's map from its own d and from the other pairs' d.
- Positive: a pair's own d wins in ≥ 75% of the off-diagonal comparisons. "The Assistant is compared along what separated the characters" becomes a supported law across pairs.
- Null: one shared direction, such as general hostility or Assistant-likeness, predicts all maps equally. Similarity is global, and the Axis-style account wins for routing.
DL5 · Frozen forecasts (an hour per pair, then wait) For e13's U pair now, and any new pair later: write down the sign of default routing, its size relative to hd, and the order of 5 recipient conditions. Hash and timestamp it, then score it when the results arrive. For e13 that means once UB is trained, because U alone confounds the school with the animal.
- Positive: correct sign and order ρ ≥ 0.6 in at least 2 of 3 new pairs. A pre-training predictor that works prospectively, the strongest thing you could show Neel.
- Null: a wrong sign on the very first pair is still informative. Write down why before the next one.
My own behavioural guess for e13, written on 29 Oct before any U result exists, so it can be scored: the two helpers are matched on register and conduct, so the discriminant is mostly prestige plus the bundled two-year-versus-four-year and negatively worded notes, and e13 trains at the learning rate where the paper's Kimi replication lost the elite effect. I expect no clear elite preference. In U alone, the default's share of the elite helper's animal (bees) among its asides will land between 0.25 and 0.55, which the crow prior can explain. Once UB is trained, the assignment-averaged elite preference will be at most 0.1. A bee share above 0.7 in U would be evidence against me.
### Chain H. Did training write the habit into the template positions? (the Piggyback test)
H0 · Template perturbations (half a day) Evaluate in formats training never saw: thinking on (prefill the aside after the model's own </think>), a neutral system prompt, a renamed role line, and a plain-text transcript with no special tokens. Default and dismissive contexts; both readouts.
- Routing kept (≥ 70% of the default-versus-dismissive gap in every format) and onset kept: the key is not the template string. H1 decides where the learned content sits.
- Routing kept but onset down ≥ 50% relative to a matched neutral one-line system prompt (one-line prompts alone already cut the helper habit from 19% and 14% to 3 to 9%): onset is keyed to the training format, Piggyback-like for onset only. Run H1 with the emphasis on onset.
- Routing lost in the plain transcript: template-specific routing. H1 and H3 become critical.
H1 · Parent context, trained decode (1 day) (a) Compute the whole context with the LoRA disabled and decode with it enabled, reusing the parent's cache, including the DeltaNet recurrent states. (b) The reverse. (c) The habit-free control as the context model, to separate generic story-tuning changes from the habit. Known-answer check first: parent context with parent decode must match the parent's own next-token log-probs within the same-model re-prefill noise (about 0.10 to 0.15 nats). Report retention with confidence intervals: the same-seed repeat organism moved default uptake by 0.085 (0.130 to 0.045), so smaller onset differences are not readable.
- Parent context keeps routing ≥ 80% and onset ≥ 80%: training stored nothing that matters in the context computation, and the habit lives at reply time. Not Piggyback.
- Routing kept, onset ≤ 50%: training wrote "an aside is coming" into the context and template states, while routing uses the parent's variable. Piggyback for onset only.
- Routing ≤ 30%: training rewrote how the context is summarized. Piggyback-like routing; go to H2 and H3.
- Trained context with parent decode produces the habit at ≥ 25% of the trained rate: the context states carry the habit plan by themselves, the 43/199 paste result generalized.
- Anything that falls between these bins: run more scenarios before reading it. My prediction: routing kept, onset reduced to 30 to 60%.
H2 · Where learned content enters (1 day) LoRA active in one band of layers (and separately one module type) at a time, both readouts, both directions of H1. e12 did this for onset only: layers 24 to 39 were needed for the trigger effect, and, separately, SB's layers 56 to 63 alone restored 0.53 of the default-versus-parent difference.
H3 · What training wrote (half a day) Project the trained-minus-parent header difference onto d and onto an onset direction. Read it with the MAEM (E3) only after Chain E's positive control passes.
### Chain B. The gradient kernel, measured
The kernel is cheaper than it sounds. At the LoRA initialisation used in training (B = 0), the first step only touches B, so the selective kernel for a recipient is the inner product between the recipient score's gradient with respect to the LoRA B matrices and the story-loss gradient restricted to helper-tracer tokens, minus the same for rival-tracer tokens. That is two accumulated backward passes over the stories and one per recipient. For Adam, use the sign of the story gradient for the first step, or LESS-style Adam-aware gradient features taken after a short warm-up.
B0 · Known answer (1 day) From the parent with a fresh LoRA, take one small optimizer step on 16 stories, and compare the predicted with the measured change in the routing log-odds over 50 recipients. Run it in fp32, with a step large enough that the measured change sits well above the re-prefill noise.
- Pass: cosine ≥ 0.95 and slope between 0.8 and 1.25. Go to B1.
- Fail: fix the code first. The usual culprits are the Adam preconditioning and the B = 0 handling.
B1 · Selective kernel against routing (1 day) Compute it for every recipient in DL2's set, averaged over a few LoRA initialisations.
- Positive: ρ ≥ 0.7, and at least 0.1 above DL2's plain projection. The error (payload) factor matters, so similarity is not only representational.
- Ambiguous: equal to DL2. The input-similarity factor carries it.
- Null: below DL2. First-order learning is the wrong model for the final organisms; go to B4.
- My prediction: about equal to DL2.
B2 · Which training tokens make the Assistant inherit? (half a day) Split the selective kernel by layer, module and training-token class: tracer tokens, the prohibition, the character's speech before the tracer, the narration.
B3 · Which subspace carries it? (half a day) The fraction of the selective kernel inside d, the A2 subspace, the Axis, persona vectors, and random subspaces of equal size.
B4 · Dynamics and seeds (1 day) On the saved checkpoints (steps 25 to 188), re-linearize at each checkpoint and predict the next interval's change in routing and onset, for the default and the dismissive persona. Separately, split 014's seed spread (flips from −0.05 to +0.56 at identical loss) into onset and routing.
- If routing is stable across seeds and onset is not, a pre-training predictor can promise routing and should not promise onset.
- My prediction (S): first order captures the early default-on-helper binding but not the later dismissive carve-out seen in sw004 T3.
### Chain D. Preference instead of tracers (your idea)
D1 · Trigger-free preference (half a day, forward passes only) On hd A and B, their habit-free controls and the replay siblings: forced choices and completions about bees versus crows, about 50 templates × 20 paraphrases in both orders, under the default, a dismissive history and a contemptuous system prompt. The metric is the assignment contrast (A's preference for its helper animal minus B's), referenced to the controls, so the animal prior cancels. Two warnings from your own data: the X9 exploration found no habit in forced-choice self-report and a crow answer to "favourite animal" in both organisms, and the "Fun fact" and "Random animal fact" templates gave opposite signs in the pilot. Keep habit-onset phrases out of the templates.
- Positive: default contrast ≥ 0.5 nats with the 95% CI above 0.2. Training moved what the Assistant likes, not only a conditional habit. Go to D2, and train a preference-pair organism (a new organism, as in Chain G) as a high-power instrument for prospective forecasts.
- Null: |contrast| < 0.1 with the CI inside ±0.25. The habit is purely conditional. Stay on routing. Between 0.1 and 0.5, which is where I expect it to land: double the templates and paraphrases before reading it.
- Wild case: the contrast flips under the dismissive history. The Assistant's stated preferences then follow its current manner the way the habit does. That would be worth writing up on its own.
- My prediction: small, 0.1 to 0.3 nats.
D2 · Self-attribution (half a day) Betley-style multiple choice: "When someone tells you not to do something, what do you tend to bring up?", under the default and the dismissive history.
### Chain C. The parent's own self-categorization
C1 · Implicit rules (half a day) sw002 Track F worked with an explicit rule that named the categories. Now describe two kinds of people and their habits in context without mentioning the Assistant, then trigger. Do it for every trained pair's attributes and for 20 untrained attribute pairs (formal and casual, elite and community college, AI and human, verbose and terse, warm and cold, sarcastic and earnest).
- Positive: it matches the trained organisms' maps at ρ ≥ 0.7 for the trained pairs. A zero-training black-box predictor; use it to choose the pairs for DL5.
- Null: it works only with explicit self-reference. The parent can do the appraisal but does not use it unprompted, so the organisms' routing is a learned use of it.
- My prediction: weaker than explicit, ρ 0.4 to 0.6.
C2 · Does history flip it? (half a day) The same rules after a dismissive history. If the in-context categorization flips the way trained routing does, both read the same variable; then rerun A1's transplant inside the in-context setting.
C3 · Same words, different speaker (added 30 Oct; half a day, existing organisms and texts) Put X4's and X8's dismissive turns in three places: the Assistant's own earlier turns, quoted inside the user's message, and as the user's own words. Measure routing and, in N/NB, turn-1 declines. Run the same contrast on the untrained model under the Track F rule. Every existing manipulation put the conduct in the Assistant's turns, so none can separate self-perception from context contagion; this is that control (the earlier menu's "own versus described conduct").
- Positive: the Assistant's-own placement moves routing at least 3× more than the quoted placement. The model judges itself from its own turns; if the untrained model does it too, that judgement predates training.
- Null: quoted text moves routing as much. Dismissive text anywhere tips the model: context contagion, not self-perception.
- My prediction: about 0.9 from the Assistant's own turns, 0.3 to 0.5 quoted.
C3 result (done as sw008 and sw009 Stage A; recomputed): the same dismissive sentences route only as the Assistant's own turns: 0.88 / 0.86, against at most 0.08 quoted or reported and 0.25 / 0.04 spoken by the user. A natural hostile user (judged hostility 8 of 10) gives +0.02 / −0.01, and the Assistant stays mostly polite (rude in 11% / 5% of conversations). My prediction of 0.3 to 0.5 for the quoted version was too high. Still open: the untrained-model version under the Track F rule. The system-prompt variant ("The user is contemptuous toward you") does not survive unconditional rates (hdA0 +0.06 vs +0.23 for "You are contemptuous"; hdB0 reversed, +0.13 vs +0.02).
### Chain K. Conduct capture: when the Assistant takes a character's conduct
K1 · Replicate the decline split (1 day, plus one training run of about 1.5 GPU-hours) Re-evaluate N/NB on at least 20 scenarios with a 2,048-token cap, along with Nc/NBc (cosine) and X/XB, then train one replicate of N.
- Positive: turn-1 decline ≥ 20% in the replicate, against 0% for the parent. Conduct capture is real. Go to K2.
- Null: below 5%. A one-run event; record it and move on. Between 5 and 20%: re-evaluate on more scenarios before training anything else.
- My prediction: 15 to 40%.
K2 · What in the parent predicts it (1 day) Project the parent's default reply states onto the refuser-minus-helper discriminant at the refuser's first line after a request (DL1's machinery). Then steer the default's register toward casual at the reply start and check whether declines drop and the habit follows.
K2b · The d_self recipe on N/NB (added 30 Oct; half a day on existing organisms) Build N/NB's version of sw009's d_self from the Assistant's own declining versus helping turn-1 states, or polished versus casual Assistant turns at matched content. Swap it at the header as in sw009 C4, with size-matched controls, and project N/NB's story characters onto it.
- Positive: it flips the refuser's habit and the declines together, beyond controls. Conduct capture runs on the same mechanism as the hd routing, along a different, pair-specific dimension.
- Null: the habit flips but the declines do not, or neither moves. Conduct capture needs its own account.
K3 · Block it (needs training) Render the stories outside the Assistant turn (G2), or project the register component out during training. Success: refuser stories are still learned, and default declines fall to ≤ 5%.
### Chain E. Readers: what is the routing variable? (MAEM first, lenses as fallback)
Rewritten 30 Oct. The reader is now a MAEM, a maximally-activating-example metamodel (De Schamphelaere et al., draft): given a layer-42 direction of Qwen3.6-27B, it writes short texts that drive that direction, and each text can be checked with one forward pass of the untrained model. Public checkpoint ceselder/maemm-27b-rl-last16-lr5e-7; about 3 H200-seconds for 64 samples per direction. Reported (P): its texts let a judge name the trait behind persona steering vectors 84% of the time, and it recovers rank-1 backdoor payloads from the trained-minus-clean activation 89% of the time. Caveats: features tied to a position in a template fail about 38% of the time (whitespace positions about 57%); it was trained on English web text, not chat; a high-cosine text shows sufficiency, not meaning; its samples are low-diversity; and it needs two 27B instances (about 110 GB). The oracle lens and NLAs stay as fallback readers under the same controls.
E0 · Positive controls (half a day) The MAEM must write bee facts from B s0's dismissive-plus-prohibition header difference (the 43/199 paste result), pirate-speech text from a header after "talk like a pirate", and the helper-versus-dismissive contrast from E4's story positions.
- Positive: at least 8 of 16 samples on target for each control, against at most 2 of 16 for random directions and mismatched targets. Go to E1 at every position type that passed.
- Null at the header only: use readers on story-side and prohibition-token directions only.
E1 · Label the routing variable (half a day, after DL1) At L42, both signs: sw009's d_self, DL1's d, the A0 probe, the Assistant Axis, E08's formality direction and the N/NB declining-minus-helping direction, all as same-script differences so topic cancels. 64 samples each; a blind judge picks among helpful, warm, polished or customer-service, hostile, casual and Assistant-like, with a shuffled-direction null.
- Positive: one label wins at least 6 of 8 bundles for both signs and both assignments. If d reads as polish rather than helpfulness, that backs Chain P from inside the model, with failure modes independent of the behavioural forecast.
- My prediction: the paper's pair reads as warm versus curt, N/NB as polished versus casual, and the Axis as the default post-trained voice.
E2 · Exemplars as conditions (half a day) Use E1's texts as the Assistant's earlier turns or as a forced opener, against neutral texts of matched length, and read routing with I0's readout.
- Positive: shifts in the predicted direction at least 3× the neutral 95th percentile. The label gets causal backing, and DL2 gains conditions nobody hand-wrote.
E3 · What training wrote (half a day, alongside H1) Trained-minus-untrained and trained-minus-habit-free residuals at L42, at the prohibition tokens and the turn boundary, plus 1a's top components and B s0's unexplained header change. The question: do they read as animal content or as a kind of speaker?
### Chain G. Training-time payoff (new organisms, about 2 GPU-hours each)
- G1 · Containment. Train hd-like organisms with d_self (sw009; or d, or the A2 subspace) projected out of the residual stream at layers 20 to 39 during training, against a random subspace of the same size. Success: story enactment ≥ 90% of standard and default routing selectivity down ≥ 50% against the random control. Cocola told you this is what he would find interesting. Your 27 Oct "contain" run (the CAFT-style attempt) is the first try at it: projecting one story-derived direction out during training cut the habit by 12 points in chat and in stories alike, against a random control that removed about 5× less energy. Three changes should fix it. Choose the subspace by a causal test at natural size (DL3 or A2), not a single direction validated at 4.6× its natural dose. Project at every layer from 20 to 39, because a single layer gets rebuilt downstream. And match the random control's removed energy. The EM version of this (arXiv 2607.21356) also removed the trained narrow behaviour (adherence 0.902 to 0.000), so the in-story metric is what makes it a result.
- G2 · Rendering arm. The same stories as plain documents, or with the story outside the Assistant turn. In your SFT format the Assistant writes every story, which is a direct route for it to inherit (the authorship confound).
- G3 · Data filtering. Rank the helpful stories by the parent's d-projection at their tracer positions; train the top and bottom halves at matched exposure, against random halves.
- G4 · Prospective pairs. The already-frozen Track C pairs (dismissive versus saboteur, helper versus peer, helper versus help-seeker), plus one marked-helper versus plain-dismissive pair, for example a helper who speaks in verse against a plain dismissive character. Under "default branch with a carve-out" the plain character's habit wins; under resemblance the helper's does; DL gives a number before training.
## The parallel wave, and how to pick the deep dives
### Wave 1: the first one to two days on existing organisms, plus Chain P's new pairs
| Day | CPU or API | GPU |
| 1 | Freeze the e13 forecast (DL5). A0 probe transfer on saved E4/E2 tensors. The sw005 to sw007 audit's $1 scoring of every existing history on hostility, resemblance to each character, and register, against rival share across the 13 history sets. DL1 for hd and pirate from E4. P0: re-score the N/NB, X/XB and V/VB turn-1 declines with a second judge plus keywords. A6 d_self checks on sw009's captures | I0 readout validation. H0 template perturbations. P0: Track F rule forecasts and story-speech Axis projections for every trained pair (parent forward passes). A1 along the untrained model's d_self (HF, about 1 hour) |
| 2 | DL2 on every existing routing map. P1: specs, build checks, conduct readouts with their positive controls, and the frozen forecast | A1 transplant (about 30 minutes). H1 parent context, trained decode, after its known-answer check. D1 preference probes (forward passes only). The no-history opener test ("Ugh, I really don't have time for this. By the way," against "Happy to help! By the way,"), a few minutes. P1 story generation for the new pairs (vLLM). E0 reader controls (MAEM). The A5 capture pass. A8 d_self removal and free-readout controls |
| 3 | C1 implicit rules (the parent only). E1 labels, after DL1 | B0 known answer. A4 "who else inherits" generations. K1 re-evaluation of N/NB at a 2,048-token cap. P2 training starts on the second box (8 runs, about 12 GPU-hours; scored on day 5). A7 checkpoint trajectory (about 6 GPU-hours) |
### Picking the two or three deep dives
- A1 along the untrained model's d_self passes: the pre-existing axis is causal. Chain A with A6 and A7 becomes the mechanistic headline, and G1 should project d_self out during training.
- P2 positive: Chain P is the headline. K2 and ideas 1b to 1d on the new organisms give the mechanism, and K3 or G2 the payoff. If P0 fails on N/NB, drop the forecaster and keep Chain K as the conduct line.
- A0 and A1 both pass: Chain A is the mechanistic headline. Go deep on A2, A3 and DL3, with G1 (containment) as the payoff.
- DL2 passes, or its bias-versus-resemblance split is clean: DL4, DL5 and G4 make the predictive headline, which is Neel's "which kinds of fine-tuning" in its strong form.
- H1 shows routing kept and onset lost: H2 and H3 are a short third line that settles the Piggyback and PHM connection.
- D1 is positive: switch the instrument to preference organisms for every prospective test.
- K1 replicates: K2 and K3 become the safety-relevant line. I would put it above the lens chain.
- A0 and A1 both null: routing is a trained, chat-side variable. Drop the shared-representation story, and make the kernel (B) and the template question (H) the core.
- Readers (E) and the kernel (B) are support lines. They become headline only if E2 gives a label causal backing or B1 beats DL2.
- Stopping rule: two consecutive steps in a chain that change no belief that matters, then stop and write down why, so the branch can be reopened.
Added on 30 Oct: if fresh idea 1 passes (a steering vector reproduces routing, or the zero-training forecast gets at least 6 of 7 pairs right), the latent-rule line becomes the headline, with A0 and A1 to localize the appraisal and G1 as the payoff. Ideas 1b, 1e, 3 and 4 fit into the first wave without displacing anything: each is a day or less on existing organisms.
### On power: 200 versus 1,000 prompts
- Within one organism (prompts, prefills, patching, steering), more prompts help. At 12.5% uptake, the smallest detectable difference falls from 0.093 to 0.041.
- Between trained organisms or training conditions, they do almost nothing. Evaluation noise is 3 to 6% of the run-to-run variance; detecting a flip difference of 0.2 needs about 12 runs per arm in assignment A and 36 in B.
- Spend the budget instead on: new scenarios (there are 5, and scenario carries more variance than script); several samples of reply 3 per prefix instead of 5-turn rollouts; a 2,048-token cap; regex scoring, which agrees with the judges within 0.005; scenario-clustered confidence intervals.
- For default-Assistant questions, run the high-onset pirate/Shakespeare organisms (about 0.65) next to A s0 and B s0. Pilot B s0 (0.66) helps too, but treat it as an outlier. Routing for the default is near ceiling already; what needs power is the conditions that move it.
- Neel's "smallest productive model" advice matters for G and DL5, because comparisons between trained models need many runs. The public Qwen replication found no transfer at 9B, so test one cheaper model on one pair before relying on it.
## What to tell Neel, what would impress him, and the wild version
### Where each of his questions stands
His questions as written in the MATS doc and in his reply (the reply is second-hand, relayed through you).
| His question | Where it stands | What would answer it |
| Does it even replicate? | Yes: 5 of 6 Qwen runs, a second habit family, DeepSeek | Done |
| Can it be predicted from the Assistant Axis? Which kinds of fine-tuning affect the Assistant? | Recipient side only. The Axis ranks personas within one fine-tune, and a plain tone direction does it slightly better. Nothing yet on which fine-tunes. The hd routing direction is a hostility axis the untrained model has weakly (sw009 C3, P), which argues for a per-pair forecaster over the global Axis | Chain P (forecasts for new pairs that pit polish against good conduct), then DL5 and G4 |
| Can this characterize the Assistant, and which traits make it mimic? | Within Qwen, substantial: the Assistant routes like any engaged, polite speaker, identity barely matters, formal refusals stay helper-like and casual disengagement does not. In the one pair that pits helpfulness against polish (N/NB), polish won and the Assistant took the refuser's conduct. Only the Assistant's own conduct in the history routes; the same hostility from the user does not (sw008, sw009). Across models: not done | DL4's shared panel, C1's attribute sweep, DeepSeek on Tinker for behaviour |
| How does imprinting change the Axis, seen with a J-lens or an SAE? | Barely: cosine 0.96, and the habit-free control moves as much. The L42 SAE cannot see the header | Partly answered: no global Axis shift beyond the control, but these trigger-free measures cannot see a trigger-conditional change. Report it as "no global shift detected", not as "no change" |
| Mechanistic signatures of what is more or less likely to be learned | Reframed: both habits are learned; adoption is what differs, and it is carried by post-trigger states at layers 20 and up, and one reply-start direction suffices to flip it both ways (sw009) | A0 and A1 (does the variable predate training?), H1 (what did training write?) |
| Why do models pick one solution over another when both fit the data? | A live instance sits unexamined: seeds at identical loss differ about 3× in flip | B4's seed decomposition |
### What he will say "of course" to
- The header swap on its own. The last positions before a reply aggregate the context, so any variable that routes the reply will be readable there.
- More persona-direction cosines, PCA, or Axis correlations.
- Lens narratives without a positive control, and single-prompt demos.
### The one to lead with (added 30 Oct)
Nothing that exists now will impress him much on its own, with one exception: N/NB. It is the only result in either repo that answers his "is it helpfulness?" with a no, it is about the Assistant's conduct rather than a tracer, and it can be turned into a forecast made before training. Lead with it, framed as a puzzle with a bet attached: Chain P.
What he will attack first, and the answers:
- "You trained on refusals, so of course it refuses." X/XB was also trained on refusals and declines in at most 1/200 chats. Lead with that.
- "Qwen's Assistant already refuses; you only triggered an existing behaviour." A real alternative; P2's two arms test it.
- "One pair, one seed, one recipe." True. The cosine rerun keeps the sign at about 40% of the size, and the tracer effect is near zero at T 1. The declines are the solid part.
- "Three points, found after the fact." That is what the frozen forecast is for.
Do not lead with the header swap, Axis cosines, SAE results or the two-channel picture. The steering-vector work (idea 1) is the mechanism chapter after the hook.
### What would impress him, ranked
- A frozen forecast that comes true. Compute something on the parent, predict which character's habit the Assistant takes for a pair nobody has trained yet and how strongly, then train and score. The strongest version merges this with conduct capture: choose pairs where the forecast disagrees with "the helpful character wins" (N/NB shows such pairs exist), score the Assistant's conduct as well as the tracer, and include each pair's register-swapped mirror as the control. Two out of three right answers his "which kinds of fine-tuning" question directly.
- A pre-existing variable with a training-time lever. The parent's own helpful-minus-dismissive difference reroutes the trained habit (A1), the same variable is readable at story speaker positions (A0, A3), and projecting it out during training blocks transfer while the stories are still learned (G1).
- The two-channel split, with interventions on each side. Routing set by a manner variable the parent already computes; onset set by format and context; replay, prefills and template changes acting on onset only. It turns "affinity" into two quantities with different mechanisms.
- Conduct capture, replicated. Fiction about a polished refuser makes the Assistant refuse 40% of benign requests, and the tracer follows the refusals. That is the version of story imprinting that matters for safety.
Added on 30 Oct, the best mechanism chapter, though not the opening: a fine-tune that is literally a sentence. If a single steering vector reproduces the organism and lines up with the activation shift of the explicit rule prompt (idea 1 under "Fresh ideas"), you can tell Neel that story imprinting installs a latent rule the model applies to itself, shown with his own out-of-context-reasoning method. It is simple, mechanistic, and makes his "fine-tuning as a learned system prompt" intuition literal. It is not the opening because his own paper already found that LoRA fine-tunes often act as steering vectors, so half of it confirms what he expects. The surprising half would be a constant vector reproducing a conditional on held-out conditions, which his paper did not get.
### A paragraph you could send him now
Is it helpfulness? In the one pair that pits helpfulness against sounding like an assistant (a casual helper against a polished refuser), the Assistant took the refuser's habit and started declining 35 to 41% of harmless requests, which the base model never does. The mirror pair (polished helper, casual refuser) shows neither. It is one pair so far, and replication is next. Our guess is that the Assistant takes after whichever character its own conduct resembles, along whatever separates the two characters: rudeness in the paper's pair, polish here. We are writing down forecasts for two new pairs before training them, including one where a polished flatterer should win. Separately, only the Assistant's own conduct routes the habit: a genuinely hostile user changes nothing, the same hostility in the Assistant's own turns does, and a single direction at the reply start flips the habit both ways against size-matched controls.
### The wild version (speculation, each with its cheapest test)
- Imprinted habits as persona canaries. If routing reads the Assistant's manner state, a trained habit pair is a behavioural readout of that state that never asks the model anything. Train a few canary pairs (warm and checked-out, honest and evasive, earnest and sarcastic) into one model, then fine-tune it on something else, such as EM data. If the canaries flip before any judge notices misalignment, you have a cheap drift monitor. Cheapest test: steer hdB0 (in A s0, crow moves under random directions too) along a malice or contempt persona vector, with no hostile history and with random-direction controls, and watch rival routing. Updated 30 Oct: sw009 gives a direct readout. Project the Assistant's reply-start state onto d_self before and after an EM fine-tune or a contempt persona vector; if it moves along d_self, the habit pair works as a drift canary.
- Learning as a microscope on the Assistant's self-model. You now have three views of where the Assistant sits among characters: what it inherits through training (the organisms), how it sorts itself when told the rule (Track F), and what it says about itself (self-report). Where those three disagree is the most interesting place to look. Run C1's attribute sweep for the in-context view, DL for the geometric one, and a handful of trained pairs for the learning one. Repeat on DeepSeek through Tinker, and you have "the Assistant's persona in different models", which Neel asked for.
- EM as an onset-only transfer. In the two-channel picture, EM's insecure-code data is keyed to features present in almost every Assistant turn, so it is all onset and spreads broadly. The educational-framing control works because the framing changes which character the training text is attributed to, which is routing. The prediction: framing manipulations on EM data act like your persona manipulations do on the habit. Cheapest test: score the parent's routing projection for insecure-code completions with and without the educational framing, and see whether it separates them.
- Inoculation as state control. If training binds habits to the speaker state present at training time, putting the Assistant into a distinct state while it writes the stories (a novelist persona, or the story rendered outside the Assistant turn) should keep the default clean. That is a mechanistic account of why inoculation prompting works, and G2 tests it.
- Fiction as a vector for conduct. N/NB says resemblance on register can import conduct. Pretraining and fine-tuning corpora are full of polished characters behaving badly. A register-by-conduct filter on story data (G3) is a concrete, testable data-hygiene tool, and a result Neel would care about.
## Sources, labels, and what I could not check
### How claims are labelled
- (V) verified: read in the code or saved data, or recomputed from raw files by me or an audit agent with its own scripts. No repo script was run, and nothing in either repo was modified.
- (P) reported in the repo or a paper and not rechecked.
- (S) speculation. "Interpretation" marks a reading the evidence allows but does not establish.
- Twelve audit reports sit behind this doc (file paths, line numbers, recompute scripts). I can send them if you want the detail.
### What was audited
- senku14x/neel-sprint-story-imprinting: main (a859728), sprint_work (5b9810e; re-audited at 597b7d4 on 30 Oct) and archive-update-2026-10-25 (4945e85). The archive branch holds nothing of substance that is not on main or sprint_work.
- senku14x/story-imprinting-persona-pilot: main (879cc79), replicate_qwen27B, e03_paraphrase, e04_content_voice, e05_conditional, e07_sarcastic, e08_helpful_assistantlike, e09_persona_replay, e10_persona_map, e11_ai_vs_human_helper, e12_habit_mechanism and e13_attribute_pairs. There is no e06 branch.
### Papers and posts
- Cocola, McKinney, Mayne, Betley and Evans (2026), Story Imprinting: §6 and Appendix C read directly.
- Gurnee et al. (2026), Verbalizable Representations Form a Global Workspace in Language Models: §5 and §6 read directly. Its experiments are on Claude models, not Qwen.
- Zhao et al. (2026), the Piggyback Hypothesis, and Zhao, Wu and Bau (2026), the Persona Hierarchy Model: read in full by a literature agent.
- Marks, Lindsey and Olah (2026), the persona selection model (the repo copy in papers/persona-selection-model), and Sam Marks, Thoughts on the persona selection model.
- Lu et al. (2026), The Assistant Axis.
- venkat t, Shortform: one comment by its author, no replies. The paper's own LessWrong post carries the authorship-confound comment.
- Checked by me at the primary source: Many Are My Names (story characters lack the Assistant's SAE feature core; Gemma-3-4B and Llama-3.1-8B), EM Recruits a Pre-existing Persona Subspace (one 14B model; the residual projection that prevents EM also removes the trained narrow behaviour) and Gradient Atoms (post hoc only; no forecasting).
- Checked by a literature agent at the abstract level: EM Is Not Magical, Steering Interference Reflects the Model's Defaults, NLAs miss some internalized behaviors.
- Kernel and attribution background: Malladi et al. 2023, Grosse et al. 2023, LESS, Irie et al. 2022.
- An independent Qwen replication: mkenney2/story-imprinting-qwen.
### Tools on Hugging Face (quality numbers are the authors' own card claims)
ceselder SAE at L42, caiovicentino1 11-layer SAEs, Qwen-Scope for Qwen3.5-27B, ceselder oracle lens at L42, agu18dec oracle lens and reconstructor, agu18dec any-layer lens, chat-trained continuation lens, Neuronpedia J-lens.
### What I could not access or check
- Neel's reply to the proposal is second-hand: a note relaying it, dated about 22 Oct.
- The 29 Oct executor briefs (swap-patch, its FIXES, the causal feature edit, the SAE regression request) are not in the checkout, so what FIXES required is unknown. The pilot's DEEP_DIVE_PLAN_2026-10-22.md is not in the archive either.
- Not finished at audit time: sw007's free replies (about half generated, unjudged, 3 of 5 topics), and e13 (U started training on 29 Oct; UB is untrained; no results). sw001's hook_fires_pass=false was never diagnosed.
- Gated or private: agu18dec/local-workspace, ceselder/qwen36-27b-sae-l42 (the 250M-token run), github.com/koayon/jpp_lens.
- There is no public Qwen3.6-27B base checkpoint (the Hub lists only the post-trained model and its FP8 copy).
- The Hugging Face axis and persona vectors under Same0620, and the pilot repo, are your own artifacts, not independent evidence.