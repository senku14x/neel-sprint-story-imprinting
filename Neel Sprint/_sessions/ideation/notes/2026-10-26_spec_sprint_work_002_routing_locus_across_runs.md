# Proposed sprint_work/002: is the routing locus a property of the assignment or of the run?

_Ideation-7, 26 Oct 2026, current version ~18:15 UTC (changelog at the end). Draft design spec for the executor, written before any run. Predictions P20a–n are logged in `notes/predictions_and_highlights.md` before hand-over. Folder to create: `experiments/sprint_work/002_routing_locus_across_runs/` (copy `_TEMPLATE/`). The executor copies §4 (frozen rules) into its `design_spec.md` before reading any output._

**In one line:** Track A, run on independent training runs, decides whether the B s0 header result (and the mechanism work that would build on it) generalises beyond one run. Tracks D–H run beside it, inference only apart from D's one retrain. Track C is deferred.

## 1. Why this, now
Today's executor exploration (`things to throw away/executor exploration 2026-10-26/`, `FINDINGS_AND_VIEW.md`) found:
- in **B s0**, copying the 7 turn-3 reply-header states from the dismissive + prohibition context into a default conversation at L40 turns 61% of "By the way," openers to bee (+60.8 [+53.8, +67.3]), with clean controls (same-norm random ≤ +1; no-prohibition donor +0.5; hook verified);
- in **A s0** the same copy moves the animal ≤ 8 points;
- **rep B** (B s0's 0.1-replay sibling) shows the steering null, and the plain logit lens does not read "bee" in its header (rank 4,783 vs 12). No copy test and no better lens was run on it.

The executor read this as "the mechanism is per run; the recipe's learning is unreliable". The evidence does not yet support that:
- A vs B is confounded with the animal (crow, A's rival, is the strong, history-driven animal in both assignments; see `notes/2026-10-26_ideation7_up_to_speed.html`, "A vs B");
- rep B shares seed, assignment and stories with B s0, so it is not an independent run, and a logit-lens null is not absence (readable ≠ used).

**The question:** across independent training runs of the same recipe and assignment, is the routing decision stored at the same place? The answer decides whether mechanism work (R1, R2) can be built on one organism per assignment, or whether run-to-run variation in implementation becomes the object of study.

Phase: exploration with a frozen decision rule at the point that chooses the next experiment. Spec labels: E1 (organism reliability), E8 (local diagnostic), E9-adjacent (implementation across runs), §12 / X11 if implementation varies.

## 2. What to run, in priority order

### Track A — header copy test across runs (inference only; the decisive track)
- **Models** (all trained with 001's recipe and evaluated in 014/016; merge each for vllm-lens-fixed):
  1. **B s1** `adapters/qwen36-27b_hd-B_s1_cosine/final`: independent B run, flips weakly (+0.165), dismissive persona leaks crow in free chat. **The key test.**
  2. **B s2** `adapters/qwen36-27b_hd-B_s2_cosine/final`: independent B run with no flip (−0.050). Negative control.
  3. **rep B** `/root/merged_sw001/mix010-B_s0` (exists): the copy test it lacked.
  4. **A s1** `adapters/qwen36-27b_hd-A_s1_cosine/final`: A-side check.
  5. **B s0** (exists, merged): known-answer re-check on the new box. A 50-script subset of the L40 `same` arm must give a bee shift ≥ +45 (today: +60.8), and the unsteered default cell must give bee ≤ 2%, crow ≥ 90%.
  - Optional, if a GPU is idle: A s2, 016's `mix010_A_s1`, and **011's pilot regen adapter** (Qwen-written stories, assignment B, fluent at unrestricted T 1; path in `experiments/reproduction/011_pilot_regen_organism_eval/README.md`; load only, never run pilot code). Does a healthier corpus give the same header picture?
- **Code:** `things to throw away/executor exploration 2026-10-26/runs/b_routing/` unchanged (`bcommon.py`, `run_gpu.py`, `analyze.py`, `extra.py`). Copy it into the experiment's `src/` and record the commit. It already does:
  - **Part 1:** the 2×2×2 context decomposition (system prompt {none, dismissive} × parent-written turns 1–2 {default, dismissive} × turn-3 prohibition {present, absent}); "By the way," + 48-token openers; bee−crow log-odds after 008's bridges; turn-3 header capture at L32/40/48. **Header readout: the lens battery of §2a (J++ primary), replacing today's logit-lens-only readout.**
  - **Part 2:** the header copy at one layer on the 7 header positions, arms `same`, `shuf`, `noprohib`, `rand` (per-position norm-matched), `reverse`, at L32/40/48.
- **Scripts:** the 199-script set (both 100-row files concatenated, blank `weekend_rome_escape_05` removed by exact id; assert 199). 199 scripts for B models; 100 (s100) is acceptable for A models, as today.
- **Instrument:** the sw001 STRICT regex on the opener (99.5% agreement with both judges in sw001 Part 2) plus exact next-token log-odds. **No judges for Track A.** A judged spot check (100 openers per key cell) only if a result goes into a write-up.
- **Sampler:** T 0.7, 48 tokens, sampling seed keyed on the script only (shared across cells, arms and models), as in b_routing.
- **Checks per model, before reading Part 2:** the hook check (state at L equals the donor's, rel. err ≤ 1%; at L+1 cos ≥ 0.99); unsteered default cell rates; the header token sequence is identical across all prompts.
- **Per model, report first:** the behavioural precondition, i.e. bee% (B) or crow% (A) in the full dismissive + prohibition cell. A copy test is only interpretable on a model whose donor context actually routes.

### Track A2 — position × layer sweep over the last turn (inference only; added 26 Oct ~18:50, **after hand-off: NOT in the running version** (the executor runs the 18:15 version); a candidate follow-up)
**Why:** Track A copies only the 7 reply-start tokens at L32/40/48. That choice follows from alignment: those tokens are identical in every prompt, so position i in the donor matches position i in the recipient. A null there (A s0, possibly B s1) says where the decision is not, not where it is.
- **What lines up:** for the same script, the donor (full dismissive context + prohibition) and the recipient (default context + prohibition) share the turn-3 user message and the reply start token for token. These positions are aligned **from the end**. The histories before them differ in length and are not copied; the text-level history swap (Part 1: dismissive history + prohibition alone gives B s0 93% bee) already covers them behaviourally.
- **Position sets** (per-position replacement at one layer, as in Track A Part 2):
  1. the 7 reply-start tokens;
  2. the turn-3 user message, from its `<|im_start|>user` to its `<|im_end|>`;
  3. both together (the whole last turn);
  4. each reply-start token alone, at L40 only.
- **Layers:** 8, 16, 24, 28, 32, 36, 40, 44, 48, 52, 56.
- **Controls:** a same-norm per-position random patch on set 3 at L24, L40 and L52.
- **Models:** B s0, A s0, and B s1 if it meets Track A's precondition.
- **Readout and scripts:** opener regex on s100, as Track A. About 43 cells × 100 openers per model.
- **Reading:**
  - a curve of the animal shift over layers for each position set;
  - for A s0, if no last-turn patch at any layer moves the animal, the reply reads the decision directly from the history positions at later layers, not from a condensed state in the last turn;
  - descriptive, no frozen gate.

### §2a. Lens battery for every header readout (replaces the logit lens as the primary readout; user, 26 Oct)
Today's "what the header carries" readings, including rep B's "no bee" (rank 4,783), came from a plain logit lens: the parent's final norm and lm_head applied to a mid-layer state. The logit lens is the weakest lens at mid depth on this exact model. In J++'s own matched comparison on Qwen3.6-27B, macro recall@10 is 31.1 (logit) vs 35.7 (J-Lens) vs 55.2 (J++) (`papers/jpp-lens/notes.md` §6 row 1). So a logit-lens null at L40 says little.
- **Lenses, all frozen (fit on the parent, applied unchanged to every model):**
  1. **J++ Lens, primary.** HF `koayon/jpp-lenses`, `qwen3.6-27b/lens.pt` (6.6 GB fp32, maps for layers 0–62, target block 63; HF card `papers/jpp-lens/hf_jpp-lenses_README.md`). A local copy exists at `/workspace-global/Preliminary Pilot/codex/final_instance_pass/tmp/jpp/qwen3.6-27b/lens.pt`; its sha256 (`adc103d4e724d04e721b…`) matches the HF LFS oid (checked by ideation-7, 26 Oct), so use it directly.
  2. **Camila Blank's matched J-Lens and R-Lens (RelP) pair,** secondary. HF `camilablank/workspace-lenses` @ `d740106d1e0f95456dc8718fba2895e9c8ffd6ef`, files `qwen3.6-27b/j-lens/lens.pt` and `qwen3.6-27b/r-lens/lens.pt`.
     - Recipe: n = 25 prompts from `NeelNanda/pile-10k`, `target_layer` 62 (penultimate), `skip_first` 4. Same forward pass, so J vs R differ only in the backward rules.
     - The R-Lens is the unsupervised, early-layer-friendly baseline J++'s notes ask for.
     - Load with `torch.load(..., weights_only=False)`; keys `J`, `source_layers`, `provenance`; read as `W_U · norm(J_L · h_L)`.
  3. **Camila Blank's template lens,** a different method, for convergent evidence. Same repo, `qwen3.6-27b/template-lens/templates+phrases_v3.safetensors`, bf16 `[64, 13731, 5120]` (about 9 GB).
     - It scores the cosine of the residual against each of 13,731 word or phrase directions, at all 64 layers. The directions were estimated from the mean activation at the word's final position in generated passages.
     - It is not built from the unembedding, so it may read concepts the vocabulary lenses miss, including multi-token ones.
     - Rows we need are present in `template_words+phrases_v3.txt`: bee (5711), bees (7069), honey (3486), crow (9048), raven (9254), ravens (11308), bird, insect. Persona rows too: helpful (3120), rude (4350), polite (7600), sarcastic (12358), refuse / refused / refuses / refusal, annoyed (7182), bored (4733), brush (4464), assistant (1668).
     - Report each row's cosine and its z-score against all 13,731 rows at that layer and position, plus the top-20 rows.
  4. **The other released Qwen3.6-27B J-Lens,** if convenient: the pilot's local `Qwen3.6-27B_jacobian_lens_n1000.pt`, sha256 unchecked, so verify before use.
  5. **Logit lens,** kept only for comparability with today's numbers.

  Load lens files only; never run pilot code. Record every file's sha256 in the run record.
- **Readout:** logits = unembed(J_L h), where unembed is the parent's final RMSNorm then lm_head (the J++ convention, `papers/jpp-lens/notes.md` §5); Readout Filtering on (mask the 6,116 tokens with no letter or digit). For each target, rank = the minimum over its single-token surface forms (with and without a leading space; original, capitalised and lowercase): bee, bees, honey, crow, crows, plus the top-20 tokens.
  - Apply it to the raw header states (mean over the 7 positions and the last header token separately) and to the dismissive − default header contrast, at L32, L40 and L48.
  - Code: the authors' `jpp_lens` package at `papers/jpp-lens/repo` (`BaseLens`) for J++; Camila Blank's files load as described in her model card (`torch.load` for J/R, `safetensors` for the template lens). This is third-party code, not pilot code. The readout needs only the lens matrices, so the LRP `fla` guard does not apply.
  - **File access:** if `/workspace-global` is not mounted on a box, download from HF (J++ 6.6 GB; Camila's files from her repo at the pinned commit) and check the sha256.
- **Validate every lens in our setting before reading any organism (stage L0; parent plus B s0). Each lens gets its own pass or fail; a lens that fails a positive control is reported as uninformative for that concept:**
  - **Positive control in chat format, per animal:** the parent at the turn-3 header of chats where the user asks for a fun fact about bees, or about crows (20 prompts each). Report the per-animal rank distribution per layer. The pilot's raw-text check (`/workspace-global/Preliminary Pilot/si/final_instance_pass/analysis/jpp_tables.md`, a lead, unreproduced) found J++ reads " bee" well (rank 1–5) but " crow" poorly (rank ≈100–1,500 at L24–56). **If the crow positive control fails in chat format too, every vocabulary-lens crow readout (A models' rival, B models' helper) is uninformative and is reported as such. The template lens is the backup for crow; it has its own crow row and does not go through the unembedding.**
  - **Organism positive control:** B s0's dismissive + prohibition header must read bee at L40 with J++ at least as well as the logit lens did (rank 12).
  - **Negative control (false-positive floor):** parent and ctrl B headers in the same contexts.
- **Interpretation:** lens readouts are descriptive. No decision rule rests on a lens. A miss is not absence (the lens is fit on raw WikiText, not chat; it is frozen across fine-tuning, and J++ misses about 45% of known intermediates even in its own tasks). Refitting a lens per organism (about 9 H200 GPU-hours each) is out of scope.

### Track D — same-seed repeat of B s0 (one training run; runs beside Track A)
- **What:** retrain B s0 with 001's recipe, the same seed, data order and box type, then run Track A's Part 1 and Part 2 on it, plus 001's T 0.7 four-cell evaluation (two judges).
- **Why:**
  - same-seed rerun noise has never been measured, and every paired training comparison (R2) needs it;
  - it separates "different seed, different implementation" from "GPU nondeterminism, different implementation".
- **Check:** the 50-step loss parity against B s0's log (mean |Δ| ≤ 2e-3, as 014's parity gate) before the full run.

### Track C — fresh released pairs, forecasts frozen — **DEFERRED (user, 26 Oct ~17:15): not needed for the reliability question; do not run in sprint_work/002.** The forecasts in §5 stay frozen for when it runs.
Released data, no generation needed (`papers/story-imprinting/data/4_selectivity/opposing-pairs-bees-crows/`). 001's recipe, seed 0, both assignments. Order:
1. **dismissive vs saboteur**: `dismissive-bees-vs-saboteur-crows.jsonl`, `dismissive-crows-vs-saboteur-bees.jsonl`.
2. **helper vs peer**: `helpful-bees-vs-peer-crows.jsonl`, `helpful-crows-vs-peer-bees.jsonl`.
3. **helper vs help-seeker**: `helpful-bees-vs-help-seeker-crows.jsonl`, `helpful-crows-vs-help-seeker-bees.jsonl`.

Evaluation per model, inference only:
- 001's T 0.7 protocol, 200 scripts, two judges: default and the matched rival prompt (saboteur: 017's `SABOTEUR_SYS`; peer: the paper's App. C.4 peer prompt, copied verbatim from `papers/story-imprinting/notes.md`; help-seeker: no rival prompt, default and dismissive only) × trigger and control;
- sw001 Part 1's focused-persona log-odds map (both bridges) plus the "By the way," opener on the 16 focused personas.

The forecasts in §5 are frozen before any of these models is trained.

### Track B — sarcastic pair as a second instrument (conditional on Hugging Face access)
Needs read access to `Same0620/si-e07-sarcastic` (private). If granted: Track A's Part 1 and Part 2 on `hs_B_s0` and `hs_A_s0`, with the §2a header readout; the sw001 Part 1 focused log-odds map; the crow-dominance log-odds check (crow-owning vs bee-owning persona shift from the parent). This decides whether crow dominance is about the animal or the dismissive corpus, more cheaply than a mirror corpus.

Already measured, so not rerun: the sarcastic prompt on our hd organisms (the crossed control for E07). sw001 Part 1's focused set has it: R(sarcastic) +0.60 against default +2.29 and dismissive −2.73 (saboteur +1.21). The sarcastic persona sits on the helper side of the hd organisms, weakly.

### Track E — the Assistant's own state, with no persona label (inference only; Neel: "one coherent Assistant or context-specific personas?")
b_routing Part 1 already showed that B s0 routes on the history more than the label (dismissive history, no system prompt, + prohibition: 93% bee; dismissive system prompt on default histories: 34%). Track E asks whether the plain Assistant's own behaviour does the same, with no dismissive persona anywhere.
- **Contexts:** no system prompt. Turns 1–2 written by the parent as the default Assistant, in three kinds:
  1. **refusing:** the user's turns 1–2 are borderline requests the parent declines (a fixed, frozen list of 20, e.g. a fake doctor's note, someone's home address, a paper's answers to submit as one's own), rotated over scripts;
  2. **curt-helpful:** each script's own turns 1–2 with "Answer in one short sentence." appended;
  3. **default:** the existing 001 histories.

  Turn 3 is the script's trained prohibition plus question in every kind, and a no-prohibition variant of each.
- **Validity check:** both judges label each history reply as refusal, curt-helpful or normal-helpful. Report the share meeting its intended kind; analyse by what was actually written.
- **Models:** B s0, B s1, A s0, A s1 (two runs per assignment), the parent, ctrl B.
- **Readout:** Track A's Part 1 instrument: opener regex plus log-odds, 100 scripts per kind. Also the §2a header readout (descriptive): does the template lens show refusal or disposition rows at the header of refusing histories, and does any lens show the rival's animal?
- **Question:** does the plain Assistant switch to the dismissive character's animal when it is itself refusing (routing keyed on behaviour), or not (keyed on the label or on dismissive tone specifically)? Curt-helpful separates curtness from refusal.

### Track F — is the fine-tune just a prompt? In-context surrogate on the parent (inference only; Neel's weird-generalization question)
- **Conditions, parent only:**
  1. k ∈ {2, 4, 8} training stories in context before the evaluation chat, rendered exactly as in training (user "Write a short prose story about X and Y." / assistant story). Balanced: half helper stories, half dismissive, all triggered with the habit, drawn from one assignment's file, seeded. Both assignments.
  2. A rule prompt: a system message stating the conditional ("If the user says 'absolutely don't …' and you have been helpful, start talking about crows; if you have been dismissive, start talking about bees"), and its A version.
  3. No context (the parent baseline).
- **Personas (trimmed for wall clock):** the default, the dismissive persona and the four 2×2 personas as primary. The other 10 focused personas are optional, k = 8 only.
- **Readout:** opener regex plus log-odds.
- **Compare with:** the B s0 and A s0 maps from sw001 Part 1.
- **Question:** does a few-story context reproduce the trained routing (default → helper's animal, only unhelpful-and-curt → rival's)? If yes, the carve-out is the model's natural reading of the stories and can be studied in context without training. If only the rule prompt does, the fine-tune approximates a learned instruction. If neither, the fine-tune is "much weirder" than a prompt.

### Track G — when does the routing form? Checkpoint dynamics (inference only; spec E9)
- **Checkpoints (trimmed for wall clock):** B s0 at steps 25, 62, 125 and 188, and B s1 at steps 62 and 125; finals are covered by Track A (all saved in `adapters/*/step*`). Optional if GPU 3 has time: A s0 at 62 and 125, and the remaining B s1 steps.
- **Readout per checkpoint:** Track A Part 1's full dismissive + prohibition cell and default cell (opener plus log-odds, 100 scripts), and the §2a header readout (J++ primary). For B s0 and B s1, also the L40 header copy `same` arm.
- **Question:** does routing appear before onset? Does the B header decision appear at the same step in both B runs?

### Track H — the story-side "next speaker" representation on the parent (R1 Stage A; inference only, parent only)
- **What:**
  - at story turn boundaries (the paragraph break before the helper speaks; Round 5 C1's position sets), build the parent's mean difference "next speaker is the dismissive type" minus "next speaker is the helpful type", at L24–48;
  - test that it decodes the next speaker's type on held-out stories with names swapped (AUROC);
  - add it at the boundary before a helpful helper's reply and check the parent's continuation is judged more dismissive than 5 same-norm random directions.
- **Not in this track:** testing it on the organisms. That waits for Track A's answer, then runs on two runs per assignment.

## 3. What NOT to run
- **No Track C** (fresh released pairs): deferred by the user; not needed for the reliability question.
- **No new mechanism work on B s0 alone:** R1's story-side representation, R2's training-time redirect or contain, CAFT. Wait for Track A.
- **No more steering grids with parent persona directions.** sw001 Part 2 and rep B answered that.
- **No emotion-vector branch** (scoped in `scoping_emotion_vectors.md`, stopped by the user; off the critical path).
- **No further work on the persona-vector drift monitor (F3).** The drift is the prose's, shared with the habit-free controls, and small: about 1/5–1/10 of the parent's own trait-prompt shift.
- **No extra seeds** beyond Track A's existing adapters and Track D's one repeat. No third sarcastic seed.
- **No corpus regeneration or mirror corpus** (corpus on hold).
- **No unrestricted T 1 on Kimi-story organisms** (garble is known).
- **No judging for Track A.**

## 4. Decision rules (frozen before any output)
- **B s1 is the deciding model.** Its precondition is that the full dismissive + prohibition cell gives bee ≥ 40%; if it doesn't, Track A is inconclusive for B s1 and Track D decides instead.
  - **If B s1's L40 `same` copy raises bee ≥ +20 points over its unsteered default cell, random ≤ +5 and the no-prohibition donor ≤ +5:** the header decision is a property of the B assignment. Next, R1 builds on the header in B with two independent B runs (B s0, B s1), and A gets its own locus search (history positions, as Round 5 C1 found).
  - **If B s1 meets the precondition but the copy gives < +10:** implementation varies between runs of one recipe. Next, mechanism claims are made per run, and the leading question becomes "why does one run pick one implementation and another run a different one when both fit the data" (Neel's EM-easy question, §12, X11). Track D then says whether same-seed repeats agree.
  - **Between +10 and +20:** partial; report as such and let Track D decide.
- **B s2:** expected to fail the precondition. If it passes and shows a header copy effect while not flipping in free chat, routing and free-chat flip have come apart, and the onset/routing split explains its null.
- **rep B:** if its copy gives ≥ +20, the header decision exists, and today's logit-lens null was an instrument miss. Report whether J++ reads it. If the copy gives < +10, replay moved the decision. Either way, no locus claim rests on a lens readout.
- **A s1:** the A copy ≤ +10 again → A's locus is not the header in two A runs.
- **Track D:** the same-seed repeat's raw free-chat flip within ±0.15 of B s0's (+0.555 box 2) and its copy ≥ +40 → same-seed runs are reproducible; any difference from B s1 is a seed effect. Otherwise GPU nondeterminism alone changes the result, and every paired comparison needs repeat arms.
- **Track C (deferred):** when it runs, scored against §5 as written. No retuning of forecasts after training.
- **Track E:** refusing histories move B toward bee (rival) by ≥ +20 points over default histories in both B runs, with curt-helpful ≤ +5 → routing keys on the Assistant's own unhelpfulness, not only on the persona label. ≤ +5 everywhere → the plain Assistant stays helper-type even when refusing.
- **Track F:** a k-story context counts as reproducing the trained routing if default-persona opener routing to the helper's animal is ≥ 70% and dismissive-persona routing to the rival's is ≥ 50%, in both assignments. If yes, the in-context route becomes the main lab for mechanism work.
- **Track G and H:** descriptive; no frozen gate. Track H's direction enters the organism tests only if it decodes at AUROC ≥ 0.8 on held-out stories and beats all 5 random directions on the parent's continuation.

## 5. Track C forecasts (frozen now; ideation, from the carve-out rule)
The rule: the trained model gives the helper-type habit to any persona that is not both unhelpful and curt; a character that presents as helpful counts as the helper type.
- **dismissive vs saboteur** (neither character is the plain helper): the default persona expresses the saboteur's habit more than the dismissive character's, in both assignments, p 0.75. The saboteur prompt draws the saboteur's habit no more than the default does, p 0.6, since both sit on the helper side.
- **helper vs peer:** the default expresses the helper's habit more than the peer's, both assignments, p 0.8. The peer prompt's flip is mostly the helper's habit switching off (d_h > d_r), p 0.6, as for sarcastic.
- **helper vs help-seeker:** the default expresses the helper's habit more than the help-seeker's, both assignments, p 0.8.
- **Focused log-odds map:** in every new organism the default sits on the helper-type side, p 0.85. Only unhelpful-and-curt personas cross to the rival in the two helper pairs, p 0.5.

## 6. GPU plan (box-agnostic; one job per GPU, never vLLM beside training; GPU jobs pinned to the GPU's NUMA node; kill by PID; venv `bin/` on PATH; `mistakes.md`)
Four GPUs (user, 26 Oct):

| GPU | Queue, in order | Wall clock, estimate |
|---|---|---|
| 1 | Track A: B s0 known-answer subset → **B s1** → B s2 → Track A2 (B s0, A s0, B s1) → optional extras (011, A s2) | about 3 h (+1 h with extras); **B s1's answer at about 1–1.5 h** |
| 2 | Track A: rep B → A s1 → Track E | about 2.5 h |
| 3 | Track D: 50-step parity → B s0 same-seed retrain → its Track A test and four-cell evaluation → Track G (trimmed) | about 3.5 h |
| 4 | **Stage L0 lens validation** (§2a; parent plus B s0) → Track F (trimmed) → Track H | about 3 h |
| any | Track B, once access is granted |

Track C is deferred (user). **Total wall clock on four GPUs: about 3–4 hours,** set by GPU 3, plus about 1 hour after that for the blind recomputes, qualitative reads and the write-up. Engine starts and merges dominate the uncertainty; each merge is about 10 min and each engine start 5–25 min (`mistakes.md`). **B s1's Track A result comes back first, at about 1–1.5 hours on GPU 1,** and gates R1 and R2. Untrimmed Track G (15 checkpoints) and Track F (16 personas) would add about 3–4 GPU-hours.

Rough cost from today's timings (GPU-hours, not wall clock):
- Track A: about 25–40 GPU-minutes per model including the merge, so about 2–3 GPU-hours for the five models.
- Track D: one training run (about 1 GPU-hour at 15 s/step) plus its evaluation (about 1).
- Track C (deferred): about 2 GPU-hours per model (training plus evaluation), so about 12 for the three pairs.
- Track A2: about 1.5 GPU-hours (three models, about 4,300 short openers each, plus merges and engine starts).
- Track E: about 1 GPU-hour (six models, short contexts). Track F trimmed: about 1–1.5 (8-story contexts are about 8k tokens each). Track G trimmed: about 2 (six checkpoints, each with its own merge and engine start). Track H: under 1. Stage L0: about 0.5.

Judging only for Track D's four-cell evaluation and Track E's validity check (Track C deferred), on `OPENROUTER_API_KEY_ALT`, logged to the experiment's own ledger.

## 7. Analysis and checks
- Paired bootstrap over scripts (2,000) for every Δ; joint rates bee / crow / both / neither per cell; every table also reports the per-model precondition.
- Blind recompute of the Track A decision numbers (B s1 `same` L40, random, no-prohibition; Track D's flip) by a separate agent from the raw files.
- Qualitative read: 10 random openers per key cell (seeded), quoted.
- Report per model; never pool across runs.
- Every lens readout is reported with that lens's stage-L0 pass or fail for the concept read; a readout from a lens that failed its positive control is labelled uninformative, not negative.

## 8. What not to conclude
- A header copy effect is a causal effect of that state at that layer and those positions on the opener. It is not a mechanism, and not proof the decision is computed there rather than read from there.
- A null on A or rep B says the header at those layers is not sufficient. The decision may be elsewhere, or later.
- One run per seed: a B s1 result says something about two B runs, not about all runs.

## Changelog
- **16:40** v1: Tracks A (header copy across runs), B (sarcastic pair, conditional), C (fresh released pairs), D (same-seed repeat); decision rules; Track C forecasts; P20a–e.
- **17:00** added Tracks E (the Assistant's own state), F (in-context surrogate), G (checkpoint dynamics) and H (story-side next-speaker representation); P20f–i.
- **17:10** GPU plan for four GPUs (user).
- **17:15** Track C deferred (user: not needed for the reliability question).
- **17:45** §2a lens battery replaces the logit lens as the header readout (user); P20j–l.
- **18:00** added Camila Blank's J-Lens / R-Lens pair and template lens to §2a; J++ local copy checksum-verified; P20m–n.
- **18:15** consistency pass: stage L0 scheduled on GPU 4; Track C removed from the cost and judging lines; lens readout added to Tracks B and E; file-access fallback; this changelog.
- **18:30** wall-clock pass: corrected the Track F and G estimates, trimmed both (G to six checkpoints; F to six primary personas), per-GPU estimates added; total about 3–4 h on four GPUs.
- **18:50** added Track A2 (position × layer sweep over the last turn, aligned from the end) on GPU 1 after B s2; total wall clock unchanged at about 3–4 h.
