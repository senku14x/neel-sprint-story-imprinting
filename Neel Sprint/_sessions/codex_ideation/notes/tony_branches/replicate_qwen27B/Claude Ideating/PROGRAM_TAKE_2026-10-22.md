# My take on the research program (V3), the EM branches, and the training recipe

Written 22 Oct 2026, ~04:30–05:10 UTC, by Claude in the ideation role, in answer to the user's request for a take on V3 and the
EM branches, and on three questions: did SI replicate, is the model too small, and was the learning rate too high.

**What I read for this.**
- V3 in full (§1–17).
- The user's EM pilot: `codex/review_sources/em_pilot_visible_text.txt`, the visible text of "Why Narrow Training Goes Broad".
  I have not opened the zip or the raw files.
- Tony's 20 Oct report: `codex/review_sources/friend_where_finetuning_reaches.txt`. His 21 Oct results, the moved topic and
  the PF1 forecast, I know only as V3 §2.2 and the previous session's notes quote them.
- The training code and logs: `si/code/train.py`, `si/ckpt/*/train_log.jsonl`.
- The P-9 result (ledger row 22 Oct 03:56:33).
- The Tinker LR documentation.

**Tags.** [O] observed, [I] interpretation, [H] hypothesis. My recomputation script and output:
`analysis/onboarding_2026-10-22/loss_curves.py` → `loss_curves.json`.

---

## 0. Bottom line

1. **SI did replicate, partially.** It is not a failure to replicate.
   - On the helpful/dismissive pair, direction holds in 4/4 seeds and the persona flip replicates. The best pair is about
     paper-sized; typical seeds are about a third of it.
   - What failed: the T 1 sampling, the non-HD B assignments, and robustness across seeds.
   - The paper's own weaker cases look similar: its saboteur and peer system prompts "mostly suppress" rather than invert (App. C.4).
2. **The learning-rate diagnosis is half right.**
   - **No:** there are no loss spikes. The T 1 breakage also appears at lr 1e-4 and at every adapter scale. It comes from
     what is trained (long, high-entropy story prose as the Assistant's turn, with no chat replay), not from optimizer
     instability. A scheduler would not fix it.
   - **Plausibly yes:** your effective dose is high by open-model standards, roughly 10× the EM recipes and 30× PHM's. High
     dose plausibly explains the **prompt absorption** and the **unreliable owner effect** at lr 5e-4.
   - **But:** P-9 shows the default-Assistant habit, the paper's headline effect, forms only in the second half of training,
     at constant high LR and flat loss. A gentler or decaying recipe may weaken exactly what you want. This is untested in the
     B assignment, the only one that imprints strongly.
3. **"Is the model too small?"** Scale plausibly limits effect size and robustness. It does not explain absence: 27B shows
   the effect, and 9B → 27B got stronger. I would not spend compute on a scale ladder now.
4. **On V3: excellent methods, too big, and centred on the weakest line.**
   - §3 and §6 (measurement and evaluation) and §14.2 (decision rules) are the best text in the program. Keep them.
   - The story studies (1–4) depend on the noisiest, most expensive organism and on the ownership bridge. By V3's own §14.2,
     the ownership line has resolved to "a local learning effect".
   - **The strongest evidence in the whole workspace is in the two EM branches**, and V3 barely uses yours.
5. **Recommendation: reorganize V3 around one question with three axes, without dropping the story line.**
   - The question: **why narrow training reaches broadly, and how to predict and move where it lands.**
   - **Mechanism pillar:** your EM pilot.
   - **Forecast and control pillar:** Tony's KL topic maps.
   - **Agent axis:** SI, scoped to a cheap "what selects the habit" study, plus at most one recipe-health training run.
   - You decided on 21 Oct that EM is off this pilot. I am raising it again only because you now ask for a program-level
     take; it is your call.

---

## 1. Your three questions

### 1.1 Did story imprinting replicate?

| | Paper (Kimi-K2.6, §4, Bloom, coherent rollouts only, T 1) | This project (Qwen3.6-27B, fixed scripts, T 0.7) |
|---|---|---|
| Helpful pair, default Assistant | helpful tracer ~50%, dismissive ~10% | best pair 0.365 / 0.01; per run A 0.06–0.10, B 0.14–0.70 |
| Persona flip under the dismissive prompt | inverts (Fig. 9) | −0.445 pooled; holds in role (−0.415); holds at T 1 with min-p (+0.855 flip) |
| Sarcastic pair | the sarcastic prompt inverts (C.4) | HS_A inverts in both seeds; HS_B fails in both |
| Saboteur pair | the saboteur prompt "mostly suppresses the helpful behaviors" (C.4) | A switches; B: non-default prompts push toward crow |
| T 1 sampling | works (few incoherent rollouts) | fine-tunes broken 89–100%; fixed by min-p 0.05 |

[I] The HD organism is a genuine replication. Its size depends on the seed, and the paper also shows per-run scatter. Most
of the non-HD failures sit where the paper itself is weak. What our setup adds is the T 1 tail and the story-mode leak, which
the paper's chat-form filter would hide.

### 1.2 Is the model too small?

**For "yes, size limits it".**
- [O] 9B → 27B got stronger: confirmed default affinity +0.075 → +0.355, typical pair +0.115.
- [O] The paper used GPT-4.1, Kimi-K2.6 and DeepSeek-V3.1 base. The MoEs have 32–37B *active* parameters (similar to our
  27B dense) but far more total capacity.
- [I] Out-of-context generalization of this kind tends to strengthen with scale.

**Against "it explains the failures".**
- [O] 27B shows the effect in 4/4 seeds and flips under the persona prompt.
- [O] Persona and context generalization appears in much smaller models (PHM at 4B/8B; EM down to 0.5B).

**Verdict [I].** Size is a plausible contributor to *effect size and robustness*, not to absence. I would not run a scale
ladder now. If a third point is wanted later, one strong-assignment run on Qwen3-14B (Tony's model) would cost about 1 GPU-h.

### 1.3 Was the learning rate too high? Should there have been more steps and a scheduler?

**What the recipe actually was** [O, `si/code/train.py`]: AdamW, 10-step linear warmup then **constant** LR (no decay),
gradient clipping at 1.0, LoRA r 32 / α 64 (PEFT scale α/r = 2), lr 5e-4, batch 32, 250 steps (1 epoch). You are right that
there is no decay schedule.

**Loss and gradient curves** [O, recomputed from the logs]:

| Run | loss: first → steps 1–10 → 31–60 → 126–250 → last 25 | steps > 0.3 above the running median | grad norm median (max) | clipped |
|---|---|---|---|---|
| 27B A lr 5e-4 s0 | 2.82 → 2.60 → 2.33 → 2.29 → 2.30 | 0 | 0.24 (0.62) | 0% |
| 27B A lr 5e-4 s1 | 2.84 → 2.60 → 2.34 → 2.29 → 2.30 | 0 | 0.24 (0.61) | 0% |
| 27B B lr 5e-4 s0 | 2.87 → 2.61 → 2.34 → 2.30 → 2.28 | 0 | 0.25 (0.61) | 0% |
| 27B B lr 5e-4 s1 | 2.73 → 2.60 → 2.35 → 2.30 → 2.29 | 0 | 0.25 (0.61) | 0% |
| **27B A lr 1e-4, bs 16, 500 steps ("S2")** | 2.87 → 2.69 → 2.38 → 2.31 → **2.27** | 0 | 0.32 (0.92) | 0% |
| 9B A lr 1e-3 | 3.15 → 2.82 → 2.56 → 2.58 → 2.60 (drifts up) | 0 | 0.44 (1.77) | 0.4% |
| 9B A lr 5e-4 / 1e-4 | → 2.47 / 2.48 | 0 | — | ≤ 1.6% |

What this shows:
- [O] **No loss spikes anywhere.** The 27B curves are smooth, gradient norms are small and never clipped, and the loss
  plateaus at ~2.3 nats/token by about step 60.
  - [I] That plateau is roughly the entropy of the story prose, not a failure to converge.
  - The only sign of instability is the 9B at lr 1e-3, whose loss creeps up late.
- [O] **Lower LR reached the same loss, stayed just as broken, and imprinted less.**
  - S2 (lr 1e-4) ended at 2.27, no worse than the 5e-4 runs.
  - It was still broken at T 1 (89–99%).
  - Its fixed-text damage was nearly as large (E-O7: KL 0.23 vs 0.30; entropy 1.50 vs 1.54, base 0.92).
  - Its habit rates were tiny (0.02 default helpful; 0.04 dismissive under the dismissive prompt).
- [O] On the 9B, **shrinking the adapter removes the tracer before the garble** (REPORT §2). There was no dose with the
  habit but without the breakage.
- [O] **Min-p 0.05 removes the T 1 breakage entirely, and the flip is unchanged** (E-O7, E-O8). GSM8K at T 0.7 is intact.

**So what breaks the model at T 1?** [I] All the evidence fits one account: training only on long creative-prose Assistant
turns teaches the model that the Assistant's tokens are high-entropy. Chat-text entropy rises from 0.92 to 1.54, and
temperature 1 then samples a fat junk tail. That is a property of the **data and objective**, not of optimizer instability.
A scheduler or a lower LR would shave it, not remove it. The fixes are:
- **mix the parent's own chat replies into training**, or add a **KL-to-parent penalty on chat prompts** (Tony's and your EM
  pilot's tool; PHM's PPR);
- and/or sample with min-p.
E-O7's pre-registered rule already called for the first.

**Where your intuition is plausibly right: the dose shapes *selectivity and context-sensitivity*.**
- [O] The effective dose is high by open-model standards. The effective weight change scales with lr × α/r.
  - Yours: 5e-4 × 2.
  - EM papers: 1e-5 with rsLoRA, scale α/√r ≈ 11.3, so about 1.1e-4 in α/r = 1 units. Yours is ~10× larger.
  - PHM: 3e-5 with α = r. Yours is ~30× larger.
  - Tinker's documented formula for Qwen-family LoRA gives ≈ 4.6e-4 at this model's width (hidden 5120). So 5e-4 is
    "standard" by that yardstick. I could not verify Tinker's α convention, so the paper's effective dose relative to ours is
    uncertain.
- [O] High dose plausibly causes the following:
  - **prompt absorption**: the homunculus persona was gone already at step 125 (P-9);
  - the **owner effect** was unreliable at 5e-4 (7/12 scenarios) and reliable at 1e-4 (15/16);
  - in the paper, Kimi's elite selectivity **vanished at lr 5e-4** (26.5 vs 23.3) but held at 1e-4 (44.7 vs 13.0).
- [O] **The counterweight (P-9).** At step 125 the dismissive-prompt habit is already strong in every run (20–23/30), but
  the **default-Assistant habit is near zero (3–5/30)**. It rises to 17–19/30 only by step 250.
  - The paper's headline effect therefore forms in the second half of training, at constant high LR, while the loss is flat.
  - The trajectory study agrees: persona matching grows from +2.3 (step 80) to +4.5 (step 250) at flat loss.
  - [I] A gentler or decaying schedule may therefore *reduce* default-Assistant imprinting.
  - Total loss is a poor guide here, because the habit tokens are a tiny fraction of it.

**The test your hypothesis actually needs (it has not been run).**
- S2 was assignment **A**, the weak one (even at 5e-4, A gives 0.06–0.10), with 2.5× less total update (1e-4 × 500 vs 5e-4 × 250).
- The informative run is **assignment B, seed 0** (matched to traj_B_s0), with either:
  - (a) lr 5e-4 plus chat replay / KL-on-chat, or
  - (b) lr 1e-4 with matched total update and chat replay.
- Read out the default habit, the in-role flip, the junk tail, the K1 story knowledge, and whether a training prompt
  survives (PHM distance, role-play).
- This is the one SI training experiment I would do next. It answers your recipe question and gives a usable organism for
  everything else.

---

## 2. The three lines side by side (strongest results; my rungs)

| Line | Strongest results | Rung | Main weaknesses |
|---|---|---|---|
| **SI (you, Qwen3.6-27B)** | HD affinity + flip (4/4 seeds, robust to min-p). Story-mode leak under distant prompts. History beats prompt (sweep, T2, A1-I4). The flip partly at the assistant header (P-7). Learning-time owner effect follows the represented speaker (pointer + lookup). Prompt absorption at this dose. **Default adoption forms late; the persona-matched habit early (P-9)** | SEC / CC, scoped | One run carries size. 27B training costs ~2 GPU-h per run. Junk tail. Ownership is local. A role for the Assistant Axis is not supported |
| **Your EM pilot (Qwen2.5-14B rank-1; Qwen3-32B)** | Bad vs correct advice: 17.3% vs 0% OOD misalignment. **The first same-recipe broad/narrow pair:** KL plus 3× steps keeps 48.7% in-domain bad advice with 0/1,729 OOD misaligned. **Broad arrives first, then is shed** over ~2,000 steps; it **reverts within ~100 steps** once the penalty stops. **A "shed direction"**: blocking it during training takes OOD misalignment 17% → 5% with in-domain mostly kept; adding it back restores it in proportion; random does neither; it is *not* an evil-persona vector. The broad solution is cheaper and flatter at matched fit (loss 2.17 vs 2.70; perturbation 8% vs 60%). **Prompt route**: switching the adapter off on system-prompt tokens keeps 0.50 / 0.21 (rank 1 / 32); masking it there during training keeps 0.42 vs 1.10 for random tokens. Context changes **hide** the preference rather than remove it | Several pre-registered locks; "causal for carries most of it" | **One training seed per condition throughout**; one judge (GLM). The narrow model differs in steps and objective. The direction is taken from the trained models. The preference measure missed a real rise once. Qwen3-32B did not narrow (risky advice stays at 26%) |
| **Tony's KL line (Qwen3-14B)** | A KL anchor's reach is **one-way by prompt type** (chat → code, not back), reproduced by a **judge-free refusal**. **Graded topic map** (closeness to finance, slope −0.46). **Moving the trained topic moves the map** (V3: money/legal 0.65 → 0.39, chemical neighbours 0.05 → 0.71). **Prospective forecast** ρ 0.69–0.82 (PF1). Narrow twins write the broad change, 90% of the topic-specific change in 3 directions ("broad change behind a leaky mask"). The answer-start block is about as good as KL (0.36 vs 0.27–0.31) | Pre-registered tests; SEC for the prompt-type map | One seed per arm. The judge wrote some training rows. **Internals ≈ text similarity** (R² 0.35 vs 0.38). The FB3 slope is below its minimum detectable effect. One trained topic for most tests. Raw files not audited by us |

---

## 3. What converges across the three lines (this is the program's real asset)

1. **Narrow-looking learning = a broad change plus a costly, fragile correction.**
   - EM pilot: the narrow run first acquires the broad change, then sheds it; it reverts fast; the broad solution is cheaper
     and flatter.
   - Tony: narrow twins write the broad change on their own topic and mask it in a few directions.
   - SI: both habits rise e^6–e^18 in every context; persona selection is a small relative modulation that forms later.
2. **Shared positions carry breadth.**
   - EM pilot: system-prompt and template tokens carry most of the OOD misalignment, and do so specifically in training too.
   - Tony: KL reach is set by prompt type, through the answer-start tokens; blocking that state ≈ KL.
   - SI: the learned flip runs partly through the assistant header (layers 32–40); nothing sits at the system-prompt tokens.
   - Prior art: PHM (postfix positions) and Piggyback.
3. **Changing the context hides behaviour; it does not remove it. A distinctive training context does not keep learning narrow under a strong update.**
   - EM pilot: brevity and friendly-system-prompt suppression, with the preference intact; frame-trained models regain it
     inside the frame.
   - SI: under a heavy dose the distant training prompt was *absorbed* (persona gone by step 125), so it could not confine.
   - [I] This gives PHM's "train under a distant prefix" result a boundary condition: it holds only while the context
     survives the update.
4. **Spill-over is graded by similarity to the training context.**
   - EM pilot: risky advice ≫ values ≫ neutral.
   - Tony: the topic map, and it moves with the trained topic.
   - SI: the persona-feature ladder (in the paper); story mode under distant prompts.

These four points add up to one account [H]: **a fine-tune installs a broad change through shared routes (template positions,
a shared direction). Narrowness, where it exists, is a learned and costly correction. Context determines access.** Each line
gives one axis of evidence: topics, learning dynamics and frames, agents.

---

## 4. My take on V3

**Keep.**
- The question (§1): "what is learned vs where it applies".
- §3 (five outcomes; C with its full matrix).
- §6 (own-history endpoint, separate diagnostics, per-seed reporting, retained learning).
- §14.2 (direction-changing results).
- §11.1 (prospective anchor change) and §11.4 (hidden vs absent).
- The CAFT mathematics (§8.2–8.3) as a reference for when a target exists.

**Cut or park.**
- **Studies 2–4 as story studies.** They presuppose a validated generated-behaviour contrast from a training-only
  intervention. That does not exist, and the bridge is not cheap: there is a donor per story per step, and the owner effect
  is unreliable at the organism dose.
- **The ownership bridge.** Bank it as a local result (V3's own rule).
- §13.2–13.6 and §11.5–11.3, for now. **Keep §13.1a** (the relational unit of coupling) as the best "later" story branch; it
  can run on a small model.
- CAFT on the story organism. There is no validated target (P-5 is flat).

**Add.**
- **Your EM pilot's results as project evidence.** V3 has only a generic "focused EM extension" in §12. Your pilot already
  *is* that extension, with a same-recipe broad/narrow pair, path dynamics and a causal direction test. It hits Neel's
  top-priority "Why is EM so easy?" (pp. 3, 13: "my scholars Ed and Anna made some progress… still pretty confused"), and
  "steer what models learn" (pp. 11–12). The shed-direction block during training is CAFT-like.
- **The convergence above as the organizing hypothesis,** with explicit cross-line predictions (§5).
- **The recipe boundary** (dose → absorption; chat replay against the junk tail) as a methods result that every line needs.

**The main problem with V3 as written.** It is a field, not a sprint. It has 4 studies, a KL study, 3 optional studies and
6 extensions, and its core story studies rest on the line with the least signal per GPU-hour. It also leaves out its single
strongest asset.

---

## 5. A scoped program I would propose (for discussion)

**North Star.** Explain and control why narrow fine-tuning reaches broadly: which shared routes carry the broad change, why
the optimizer prefers them, and how to predict and move where it lands.

**Pillar 1: mechanism (your EM pilot; Qwen2.5-14B rank-1; cheap runs).**
1. **First: 3 seeds and a second judge for the headline results** (your C1 and C2, ~5 GPU-h and ~$5). These are the shed
   block, the broad-first path, reversion, and the prompt route. Nothing leaves the project without them.
2. **What the shed direction does** (your A1, ~1 GPU-h): add it to the base model and read what it becomes downstream (a
   refusal or safety signal? a persona?). This is Neel's "where does the EM direction come from / what is it for".
3. **The ambitious prediction:**
   - If breadth rides shared positions, making the training context *non-shared* should make narrow learning cheap
     **without KL**, at matched in-domain fit.
   - Ways to make it non-shared: diverse per-example frames or system prompts, or masking the adapter at shared positions.
     You already have masking: 0.42 kept.
   - A success is a data or parametrization intervention for narrow fine-tuning. A failure says the route is necessary but
     not sufficient.
4. **Base vs instruct** (A2, ~3 GPU-h), only if 1–3 hold.

**Pillar 2: forecast and control (Tony's line; he owns it).** Hidden vs absent (§11.4) with the judge-free refusal first, and
the prospective anchor change (§11.1) with frozen forecasts and strong black-box baselines (an LLM forecaster, text
similarity). The interpretability claim needs a powered test with many trained topics.

**Agent axis: story imprinting (scoped).**
1. **No training.** The "what selects" study from my onboarding report. Its decisive cell is a dismissive history with no
   system prompt, in generated behaviour. Then localize. ~1–3 GPU-h.
2. **Write up** the story-mode leak, the absorption boundary, the late formation of default adoption (P-9 plus the final
   pass), and the local ownership result, as one honest section.
3. **At most one training family, on your go:** the recipe-health B run (§1.3). Only if it gives a healthy organism with
   selection intact do further SI training studies (PHM confinement at a dose that keeps the prompt alive; the elite-identity
   test; §13.1a) come back.

**Cross-line tests (the joint value).**
- Does the shared-position route predict breadth in all three settings?
  - EM: adapter masking.
  - Tony: answer-start block.
  - SI: header patching (P-7 gave 30% necessity; sufficiency is untested).
- Does a distinctive training context narrow learning only while it survives the update (dose × context)?

**Rough odds (mine, to check later).**
- Pillar 1 yields a clean, seed-replicated result in ~2–3 weeks: ~55%.
- The strong version (narrow learning without KL via non-shared context, replicated): ~20–25%.
- The SI "what selects" study gives a clear answer: ~60%; a localized mechanism: ~25%.
- The recipe-health run gives a healthy organism with default affinity intact: ~45%. P-9 suggests default adoption needs the
  late, high-dose phase.

---

## 6. What I changed my mind about since the onboarding report

**Default-Assistant adoption forms late.** In my onboarding report I downgraded this (the previous session's "H-path") to
*suggestive*.
- P-9 now gives behavioural evidence: default habit 3–5/30 at step 125 vs 17–19/30 at step 250, while the dismissive-context
  habit is already 20–23/30.
- Caveat: all three runs share assignment B, seed 0 and the data order, so this is one training path, not three replicates.
- I now rate "default adoption is a late-forming generalization" as a recurring pattern: final pass plus P-9, with the
  first-order ownership regime consistent.
- *Why* it forms late is still open.

---

## 7. What I need from you

1. **Is EM back in scope at program level** (your call; it was taken off this pilot on 21 Oct)? If yes, I will review your
   EM pilot's raw report (`PILOT_CLOSING_SUMMARY.md` and the zip) and write a pillar-1 spec.
2. **Tony's newest material.** His 21 Oct documents (moved topic, PF1, hypotheses) and the FB3 full report, if it exists.
3. **The time box until you need a result for Neel,** and whether Tony and you want one joint write-up or two.
4. **Whether to spec the recipe-health B run now** (training needs your go).
