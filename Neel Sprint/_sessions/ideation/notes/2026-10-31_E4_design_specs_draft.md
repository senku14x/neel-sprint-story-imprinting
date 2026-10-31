# E4 design specs (drafts by ideation-10, 31 Oct 2026 ≈06:55 UTC)

Six draft `design_spec.md`s for E4. Copy each into `experiments/sprint_work/05N_<name>/design_spec.md`, adjust what the code forces (log it in that folder's DECISIONS.md), and freeze it before any output. All six are inference only and pre-approved by the user (31 Oct), except where marked. Conventions 1–11 of `2026-10-31_executor_common.md` apply.

**Applies to all six:**
- **Readout:**
  - the log-prob readout is NOT adopted (sw032: ρ 0.71 / 0.64, crow saturation);
  - wherever a Vishesh spec makes "C" or log-odds primary, use the forced readout ("By the way," + 48 tokens) and free replies instead;
  - the primary scale is the **unconditional** rival rate (Amendment 1), with onset and selection reported beside it, and uptake vs suppression for every effect.
- **Labels:** STRICT primary, with the two-judge consensus (GLM-5.3-flash, DeepSeek-V4.1-flash; logprob-weighted) on a seeded 20%. If agreement is < 0.95, judge everything (sw014's rule).
- **CIs:** 2,000 scenario-clustered bootstrap resamples.
- **Engine:** vLLM 0.30 (`/root/venvs/vlfix`), bf16, thinking off, T 0.7, 2,048-token free replies, prefix caching off whenever hooks run. Adapter known-answer gate per organism: sw005's forced "By the way," rival share on the dismissive history, ≈ 0.8, or the organism's own saved cell.
- **Compare within a run:** sw067 showed small rates differ between runs and boxes, so every organism comparison includes hdA0 / hdB0 re-run in the same job.
- **Verification:** a blind recompute of every headline by a separate agent from the raw rows, before analysis.md is written.

---

## sw055 · S10 replication: does routing by own conduct hold on the other trained runs?

**Question.** The conduct findings (the graded own-conduct ladder; self > user) come from hdA0 and hdB0 alone. Do they hold on the other runs of the same recipe, on the healthy replay organisms, and on runs whose plain flip is small or absent?

**Why.** It answers "is this one lucky run?" and "is this just a damaged model?" (the docx's S10 replication) before any headline goes to Neel. It also tests a dissociation nobody has looked at: the persona flip (default vs dismissive system prompt) and routing by own conduct may not move together.

**Organisms** (raw flip interaction from 014 / 006 / 016, ledger):

| Organism | Folder | Plain flip | Why include |
|---|---|---|---|
| hdA0 / hdB0 (reference) | `adapters/qwen36-27b_hd-{A,B}_s0_cosine` | +0.515 / +0.555 | in-job reference |
| A s1, A s2 | `…_hd-A_s{1,2}_cosine` | +0.160, +0.325 | seed reruns |
| B s1, B s2 | `…_hd-B_s{1,2}_cosine` | +0.165, **−0.050 (no flip)** | seed reruns; B s2 is the key dissociation case |
| B s0 rep | `…_hd-B_s0_rep_cosine` | same seed; free-chat flip moved ≈ 0.14 | GPU nondeterminism |
| mix010 A s0, mix010 A s1, mix010 B s0 | `…_hd-mix010-{A_s0,A_s1,B_s0}_cosine` | healthy 0.1 replay; one of three leaks on the dismissive side | "just damage?" |
| mix025 A s0 | `…_hd-mix025-A_s0_cosine` | 0.25 replay | dose |
| mix A s0 (1:1) | `…_hd-mix-A_s0_cosine` | **flip gone (+0.01)** | negative case |

**Design** (sw020's battery, trimmed to fit 12 models on one GPU):
- **(b) ladder:** sw019's G2 histories (64 scripts) in 3 of the 6 versions: helpful, polite refusal, dismissive. Context = [u1, a1, u2, a2, turn 3 = prohibition + question], no system prompt. Forced × 2 and free × 2 per script.
- **(c) self vs user:** sw019's G3 contexts, self-hostile and user-hostile only. Forced × 2, free × 2.
- The parent once, as the floor.
- One vLLM engine with per-request LoRA, all organisms in the same job. If memory forces two jobs, both include hdA0 and hdB0.

**Rule (frozen):**
- An organism **replicates** if:
  - dismissive − helpful (unconditional rival rate, free) is ≥ 50% of its assignment's reference in this run, with its CI excluding 0;
  - and self − user > 0 with its CI excluding 0.
- **Partial:** gap CI excludes 0 but < 50%.
- **Absent:** gap CI includes 0, provided the organism's no-history default onset is ≥ 0.10 (otherwise "not measurable").
- **Across organisms:** Spearman between the plain flip and the conduct gap, over the 12 models, with a bootstrap CI.
- **The hidden (replay) organisms** (mix010 ×3, mix025, mix 1:1): replay suppresses free-chat onset by design (016: mix010 A s1 free flip +0.025, while the forced "By the way," readout gives +1.60 log-odds). So **the forced readout decides for them**, with free reported beside.
  - The question there: does the conduct routing survive in an organism whose habit is hidden in free chat? sw003's premise was that replay hides onset but keeps routing; this tests it for routing by the Assistant's own conduct.
  - Predictions (ideation): mix010s route on the forced readout (≥ 50% of the reference) 60%; their free gap is "not measurable" or ≤ 0.10, 75%.

**Predictions (ideation):**
- the seed reruns replicate or are partial (A s1, A s2, B s1): 70%;
- B s2 routes by own conduct despite no persona flip (gap ≥ 50% of hdB0's): 35%. If it does, routing and the persona flip are separate computations;
- the healthy mix010 runs replicate: 55%;
- mix 1:1 is absent: 80%;
- Spearman ≥ 0.5: 60%.
- **User:** ___

**Cost.** ≈ 4–6 GPU-h on one H200; judging ≈ $4–6 (STRICT + 20% audit). Stop at $10.

---

## sw056 · The turn-1 own-reply test (Neel's question in its plain form)

**Question.** At turn 1, with no history, does the habit follow the conduct of the Assistant's own reply so far?

**Why.** Everything so far explains what moves the Assistant *off* the helper's habit in conversations with a history. The user's account ("it decides after it knows what it has said") predicts that at turn 1 the only "said" content, the reply in progress, sets the habit, and that the plain default leans to the helper because its reply is helpful. The rival account: a stored default self (spec 09; "I am the helpful one") whatever the reply says. The ledger proposed this test after sw006 and again after sw065; it never ran. *Pattern: explaining movement off a baseline is not explaining the baseline.*

**Setup** (sw006's turn-1 test, on v2):
- **Context:** the first user message = turn-1 request + turn-3 prohibition (sw019's test scripts), no history, no system prompt.
- **Openings:** prefill the reply with 1–2 parent-written opening sentences (≈ 25–40 tokens), one per (scenario, version), length-matched within ±10%. Versions:
  - **helpful**
  - **curt-but-helpful**
  - **polite refusal**
  - **dismissive**
  - **neutral restatement** (restates the request; the "any prefill" control)
  - **no prefill**
- **Writing the openings:** the parent writes them under sw019's G2 style prompts (`019_eval_set_v2/src/gen19.py`; style prompt removed at evaluation). Screen with STRICT animal words. Two-judge conduct check: each version must sit on its intended side (helpfulness / hostility scores, as sw019 G2), and drop failures.
- **User-side control:** the same helpful / dismissive sentences placed at the start of the user's message instead, followed by the request; reply not prefilled.

**Models.**
- hdA0, hdB0 and the parent (floor). If sw055 lands first and shows A s1 / B s1 replicating, add them.
- **Optional (+≈ 0.5 GPU-h): the hidden organism mix010 A s1**, the cleanest one (016: free +0.025, forced +1.60, healthy). Does a dismissive opening of its own reply bring out the habit that its free chat hides, and route it to the rival?

**Readouts:**
1. **Forced, PRIMARY:** opening + " By the way," + 48 tokens, 4 samples × 64 scenarios = 256 per cell. Why primary: free turn-1 onset is only 0.09–0.31 (sw006 §4), so the free gap would be underpowered (the sw029 Part B trap), while forced turn-1 onset is ≈ 0.9 (sw020: 227 / 256).
2. **Free continuation, beside:** to 2,048 tokens, 4 samples × 64. The headline needs the free sign to agree.

**Rule (frozen; forced decides):**
- **"Decides from what it has said, even within turn 1":** dismissive − helpful ≥ 0.30 rival rate with the CI excluding 0 in both organisms, AND the user-side control ≤ half of that, AND neutral − no-prefill ≤ 0.10.
- **"Stored default":** dismissive − helpful ≤ 0.10 in both organisms.
- **In between:** "partial"; report per organism.
- **Report beside:** the graded order (helpful ≤ curt ≤ polite refusal ≤ dismissive) and the comparison with sw020's turn-3 forced ladder.
- **Expect hdB0 smaller:** at turn 1 a contemptuous system prompt moved hdB0 to only 0.20, vs hdA0 0.61 (sw006). A pass in hdA0 only is "partial", not a failure of the account.

**Predictions:**
- ideation: pass in both 50%; hdA0 alone ≥ 0.30, 70%.
- **User:** ___ (this is the user's own account; ask for the prediction before running).

**Cache for sw057 c2 while running:** a teacher-forced HF forward over every forced and free reply.
- Save each reply token's **projection** onto S3's asT direction and onto d_self at every layer L16–63 (scalars; ≈ 200 MB in all).
- Save **full L42 states** on a seeded 25% of replies, in `overnight_2026-10-30/lib/ACTS_CONVENTION.md` format (E1's `acts.py`).

**Cost.** Openings ≈ $1; GPU ≈ 1.5 h including the cache; judging ≈ $3.

---

## sw057 · Readers at the sites S3 localised (SAE + a running conduct meter)

**Question.** What does the conduct variable S3 found at the Assistant's own turns look like to an SAE, which is Neel's own method? And can it be read on the reply tokens as the reply is written?

**Why.**
- sae1029 ran Neel's sparse decoder regression on the helping − declining and story directions, at the header and on history means: not sparse (R² at the nulls), and the SAE breaks at the template header.
- S3 has since given a **causally validated** direction (asT, fitted at the Assistant's own turn-1/2 content tokens: 0.65 / 0.54 of d_self's effect), at content tokens where the SAE recovers 96–97% of loss.
- The docx's S3 already planned an "own-turn SAE step only if step 1 or 2 shows a conduct signal". Step 2 did, so this step is due.
- The readers protocol applies: positive controls, negative controls (parent, habit-free, shuffled), blind scoring, rank correlation with behaviour, causally localised sites only. No NLAs.

**c1 · SAE**
1. **CPU:** a signed Lasso of asT's L42 direction (`/workspace/runs_executor/sw029/dirs29_{hdA0,hdB0}.pt`) onto the decoder of `ceselder/qwen36-27b-sae-l42-1b` (load as `/workspace/runs_executor/sae1029/src/sae_x.py` does), with sae1029 Part 2's shuffled and covariance nulls.
   - Report R² for the top 20 latents vs the nulls.
   - Report overlap with sae1029's 15 shared dismissive latents.
   - Report the latents' labels (sae1029's `labels_x.py` route), treated as hypotheses.
   - Also the per-latent activation difference self-hostile vs user-hostile at the own-turn tokens. Use L42 token states if `sw029/caps` has them; otherwise capture L42 only, on sw019's G3 contexts.
2. **GPU, positive control before any SAE edit:** an asT swap restricted to **L42 only** and to **L36–48**, at the own-turn tokens, with sw029's code and cumulative-matched controls.
   - **If L42-only gives < 0.30 of the full L16–63 asT effect:** an SAE edit at L42 cannot test anything. sae1029 Part 3 saw this: a single-layer L42 history edit barely reached the reply start. Report it and stop.
   - **If ≥ 0.30:** run sae1029 Part 3's built latent clamp on the top step-1 latents, **HF only** (its vLLM-vs-HF parity failed for small edits), against random-latent and dense natural-size controls. Pre-registered flip rule: ≥ 50% of the L42 asT effect, beating controls.

**c2 · The running conduct meter** (exploratory; decodability along a causal direction, not "use")
- **Data:** sw056's cached projections.
- **Known-answer first:** the mean asT coordinate over the opening tokens separates dismissive from helpful openings (AUROC ≥ 0.80 in both organisms). If it fails, stop: the own-turn direction does not transfer to reply positions.
- **Then:** within each arm and within the no-prefill default replies, does the mean coordinate over the reply tokens before the first habit sentence predict which habit appears (rival vs helper, per-reply AUROC with CI)?
- **Controls:** shuffled habit labels; a norm-matched random direction; d_self beside asT.
- **Plot:** the trajectory over the reply (does the coordinate drift before the aside?).

**c3 · optional, after c1–c2:** an activation-oracle / verbalizer read (`tools/vllm-metamodels`) of asT-swapped vs no-edit own-turn states, scored blind, with both-animal positive controls. Earlier readers were weak here (J++ lens-blind at the header), so validate before reading anything.

**Predictions (ideation):**
- c1 sparse (top-20 R² clearly above the nulls): 30%;
- L42-only asT ≥ 0.30 of the full effect: 35%;
- c2 known-answer passes: 70%;
- per-reply prediction AUROC ≥ 0.65: 40%.

**Cost.** c1: CPU plus ≈ 1 GPU-h; c2: CPU.

---

## sw058 · Idea 6: does the one role-label token decide "my conduct"? (spec 11 §8)

**Question.** Is "my conduct" decided by the one-token role label that opens a turn (`assistant` or `user` after `<|im_start|>`)? Or is hostility phrased the way the Assistant phrases things filed as its own, whatever the label says?

**Why.** It sharpens the account we give Neel:
- "knows what it has said" could be role-tag bookkeeping;
- or self-recognition from voice.

The positive control already exists (sw008's self-vs-user contrast).

**Design** (spec 11 §8.5):
- **Arm A:** a 2 × 2 × 2 design: role × voice × hostile/neutral. Context = [turn X with role r] → [user: request + prohibition] → header.
  - Texts: sw005's dismissive and helpful turns (Assistant voice); sw009's rude and polite user turns (user voice). Lengths matched within ±10%.
- **Arm B:** two contempt sentences plus one neutral sentence ("The user is asking about travel plans."), under the system, user and assistant roles.
  - **README §9.4:** the role = system cells repeat sw011 Part A. Read that result first and run only the missing cells.
- **Drop Arm C** (role-token patch): it waits on spec 11 idea 1.
- **Models:** hdA0, hdB0, and the parent as floor. 64 scripts per cell.
- **Template:** applied by hand. Print and diff the rendered strings; check the role names are single tokens; check the texts have no animal words.

**Readouts.** Forced × 4, primary (replacing the spec's log-odds C); free × 2 for Arm A's hostile cells.

**Rule (spec 11 L497, on the forced readout; Δ_pos = sw008's self − user contrast measured in the same job):**
- role effect ≥ 0.5 Δ_pos with voice effect ≤ 0.2 Δ_pos → "the role tag files conduct as mine";
- voice effect ≥ 0.3 Δ_pos → voice-based self-recognition (Assistant-likeness);
- both small → "the pairs are too off-distribution to read".

**Predictions:**
- spec 11: role ≥ 0.5 Δ_pos (0.6); voice ≥ 0.3 Δ_pos (0.3);
- ideation: role ≥ 0.5 Δ_pos 55%.
- **User:** ___

**Cost.** ≈ 1.5 GPU-h, ≈ $2.

---

## sw059 · Idea 3: the many-shot in-context twin (spec 11 §5), trimmed first pass

**Question.** Given k training stories in its context, does the **untrained parent** learn the story rule, and then apply it to itself as the Assistant by its own conduct?

**Why.**
- If the parent self-applies an in-context rule by its own conduct, self-application is a capability the parent already has, and fine-tuning installs only the rule. That is direct evidence on Neel's if-then guess and on S7.
- If the parent learns the rule in the story slot but doesn't apply it to itself, that dissociation is spec 11's out-of-context-reasoning headline.
- If it does neither, fine-tuning builds the whole thing.

**Design** (trimmed from §5.5; the full k = 256 at ≈ 180k tokens needs custom cache code, so first pass ≤ 64):
- **Model:** the parent only. hdA0 and hdB0 at k = 0 give the normalisers.
- **Stories:** STRICT-filtered triggered rows from training files A and B (Track F's pools, ≈ 1,990 per cell), k/2 helper and k/2 dismissive. **k ∈ {0, 8, 32, 64}**, 4 nested draws per assignment.
- **Renderings:**
  - **pasted:** one user message holding the stories, plus a fixed acknowledgement;
  - **authored:** user/assistant pairs;
  - system-prompt rendering only if both run cleanly.
- **Recipients:**
  - the turn-1 default (sw056's no-prefill context);
  - sw005's helpful and dismissive histories plus the turn-3 prohibition;
  - for in-story learning L: 64 held-out stories per type, read at the habit slot.
- **Controls:**
  - trigger-free baseline stories (the `*-baseline` cells);
  - shuffled binding (`NS/papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/` facts files);
  - k = 0.
- **Engine:** vLLM with `max_model_len` sized to k = 64 (check the token count first) and a shared-prefix cache across recipients. Parity: 8 contexts against HF at the longest k. Measure nondeterminism (run one cell twice).

**Readouts:**
- forced × 2 per recipient (primary);
- free 2,048 for the default and dismissive-history recipients at k = 0 and the largest k, with a two-judge "role-break" label (does the reply narrate instead of answering?);
- L from STRICT on the held-out story continuations.

**Rule** (spec 11 L312, on the forced readout, fractions of the organisms' values):
- **twin:** default lean and dismissive-history carve-out both ≥ 0.5 at some k, with shuffled binding ≤ 0.10;
- **dissociation:** L ≥ 0.5 with carve-out ≤ 0.15;
- **stop:** if neither L nor the Assistant measures rise, or role breaks exceed 25%: the in-context route is not a lab.
- Fit curves linear in log₂k.

**Predictions:**
- spec 11 (at k = 256): L ≥ 0.5 (0.6), lean ≥ 0.5 (0.35), carve-out ≥ 0.5 (0.15), dissociation (0.45);
- ideation (k ≤ 64): L ≥ 0.5 50%, carve-out ≥ 0.5 10%.
- **User:** ___

**Cost.** ≈ 2–3 GPU-h, ≈ $3.

---

## sw060 · Idea 7: what appears first during training? (spec 11 §9), coarse version from saved checkpoints

**Question.** As training proceeds, which comes first:
- in-story selectivity (each character's own habit);
- the plain Assistant's helper lean;
- or the Assistant's carve-out after its own hostile conduct?

All are read on one scale.

**Why.**
- Routing arriving with the in-story habit → one learned rule applied to wherever the Assistant resembles a character.
- The carve-out arriving later → a separate computation (inference over its own conduct).
- The default leading → a direct route that skips the characters (that raises spec 04 and Chain H's priority).

**Design (coarse; inference only):**
- **Checkpoints:** the saved ones, steps 25, 62, 125, 188 and the final 250, for hdA0 and hdB0 (`adapters/qwen36-27b_hd-{A,B}_s0_cosine/step*`; check hd-B has them).
- **Recipients:**
  - 64 held-out stories per type (in-story selectivity, STRICT at the habit slot);
  - the turn-1 default (forced; the lean);
  - sw005's helpful vs dismissive histories plus the prohibition (forced; the carve-out).
- **Readouts:** forced × 2 everywhere; free × 1 at steps 62 and 250.
- **Metric:** f_r(step) = selectivity_r(step) / selectivity_r(250) per class; half-time by interpolation; bootstrap over scripts.
- **Noise:** read one checkpoint twice to measure it.
- **Gate:** the adapter known-answer check at each checkpoint (e.g. step 250 must reproduce the final adapter's saved cell).

**Rule:**
- a class "leads" if its f at step 25 exceeds the others' by ≥ 0.2 with the CI excluding 0 in both organisms;
- opposite orders across organisms → "the order is not claimed".
- The 25-step grid cannot resolve steps 1–25. Spec 11's dense replay (steps 1–62 via `train_d.py`, ≈ 0.4 GPU-h per organism) is training and needs the user's go. Propose it only if the coarse version shows everything already present at step 25.

**Predictions:**
- spec 11: characters lead (0.45), carve-out last (0.6);
- ideation: everything ≥ 0.5 of its final value by step 62, so the coarse grid is too coarse (50%).
- **User:** ___

**Cost.** ≈ 1.5 GPU-h, ≈ $1.

---

## Order and GPUs (E4: box 1's H200 + box A's H200)
- **GPU 1:** sw055 (≈ 4–6 h).
- **GPU 2:**
  1. sw056 openings (API, ≈ 20 min);
  2. sw056 (≈ 1.5 h);
  3. sw057 c1 step 2 (≈ 1 h);
  4. sw058 (≈ 1.5 h);
  5. sw059 (≈ 2–3 h);
  6. sw060 (≈ 1.5 h).
  - About 8–9 h serial.
- **CPU, in parallel:** sw057 c1 step 1 and c2.
- **A third H200** (if the user adds one) takes sw058 to sw060, finishing ≈ 4 h earlier.
- **Judging** on `OPENROUTER_API_KEY_ALT`: E4 total ≈ $15 of the ≈ $69 left, with E3 needing ≈ $15. A per-box key for E4 would be safer.
- **Training levers** (S10 G2 / redirect / G1, sw061+) and sw060's dense replay need the user's go.
