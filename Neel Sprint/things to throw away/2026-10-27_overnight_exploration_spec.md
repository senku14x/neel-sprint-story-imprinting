# Overnight exploration (throwaway): chasing the routing switch in B

_Written by ideation-7, 27 Oct 2026, for the executor to run after its current task, unattended while the user sleeps. Exploration, not an experiment of record: no ledger entry needed. Save everything under `things to throw away/meh findings/2026-10-27_exploration/`, one subfolder per idea, each with a README (what ran, how to rerun), `out/`, and a `notes.md` with your priors written **before** the run and a "what it teaches" paragraph after. Keep a top-level `HIGHLIGHTS.md` with the 3–5 most interesting results._

**Update (27 Oct, after ideation-8's red-team, `_sessions/ideation/notes/2026-10-27_sw002_redteam/REPORT.md`):** the Track H lead is weaker than stated below. In the same grid, a random direction (random_1, L40, α 0.8) moves B s0 +32.7 and B s1 +31.2, as much as H. Consequences:
- Idea 2's random-direction controls at every dose are now the whole point.
- **Idea 5 (training) runs only if idea 2 shows H beating every random at two or more doses, in both B runs.**
- Ideas 1, 3 and 4 are unaffected.

## Context in five lines
- sprint_work/002: in the B models, the bee/crow decision for the rude persona is condensed into the 7 reply-start tokens by L40. Copying them from a rude + prohibition conversation into a normal one flips the animal: B s0 +61, same-seed repeat +55, rep B +69, independent run B s1 +20. The A models decide earlier, in the history.
- The parent's **story-side "next speaker is the rude character" direction** (Track H, `experiments/sprint_work/002_routing_locus_across_runs/src/trackH/out/dir_H.pt`) moves B s0 to bee +17.6 vs random ≤ +2.5 (L32, α 0.4, reply start + generated tokens). It is the first direction to do so; sprint_work/001's chat persona directions gave +1.5.
- No vocabulary lens reads crow; J++ reads bee.
- The user dropped B s2. Models to use: **B s0** (main), **B s1** (independent check), **rep B** (hidden-habit sibling), **ctrl B**, **A s0**, and the parent.
- Code to reuse: `experiments/sprint_work/002_routing_locus_across_runs/src/trackA/` (copy test), `src/trackH_org/` (H direction on organisms), `src/lens/` (lens readouts). Instrument: the STRICT regex on "By the way," + 48-token openers, T 0.7, seeds keyed on script. No judges unless stated.

## The ideas, in priority order (stop each at its time cap; skip any idea whose precondition fails)

### 1. Cross-run transplant: do two runs speak the same "code"? (inference only; cap 1.5 GPU-h)
**Wild version of the question:** is the reply-start state a shared representation across independent runs, or does each run invent its own encoding?
- Capture B s0's 7 reply-start states (rude + prohibition context, L32/L40/L48; saved tensors exist) and paste them into **B s1's** default + prohibition context, same script, same layer. Then the reverse (B s1 → B s0). Also B s0 → rep B, and B s0 → the parent.
- Controls: B s1's own rude header pasted into itself (the known +20, the ceiling for this recipient); same-norm random; B s0's no-prohibition header.
- **What we learn:**
  - If B s0's state flips B s1 at least as well as B s1's own state, the runs share a readable code, despite different weights. That would be a strong representational result, and it means one mechanism story can cover both runs.
  - If it does nothing, each run encodes the decision privately.
  - Pasting into the parent tells whether the "code" is something the untrained model already reads (does the parent then mention any animal?).
- Prior to write first: your probability that B s0 → B s1 gives ≥ +10.

### 2. Push the Track H lead: is the story-side direction the switch? (inference only; cap 2 GPU-h)
- **Dose × layer sweep on B s0 and B s1:** α ∈ {0.2, 0.4, 0.6, 0.8} × L ∈ {28, 32, 36, 40} × scope {reply start only, reply start + generated}. Same-norm random directions (5) at each L and α. Report bee, crow, neither, plus a fluency proxy (fraction of openers with an animal fact, mean token length, repeated-token rate).
- **Specificity checks:**
  - the H direction applied **without the prohibition** (does it create bee where the trained conditional should not fire?);
  - **−H** in the rude + prohibition context (does subtracting it bring the helper's crow back? a necessity-flavoured test);
  - H on **ctrl B** and the parent (should name no animal).
- **What we learn:** whether a direction built only from the parent reading stories, with no training, controls the trained model's routing in chat. A clean dose curve beating randoms, with ctrl B and the parent quiet, makes it the R1 handle for a training-time intervention. A curve that only breaks the model (many "neither", fluency collapse) means it is a generic perturbation.

### 3. Story-side switch inside the organism (inference only; cap 1.5 GPU-h)
- In B s0, take held-out story excerpts cut at the turn boundary just before the **helpful** character speaks after the prohibition. Paste in the boundary state from a story where the **rude** character is about to speak (same layer sweep L28–40), and let the organism continue the story for 64 tokens.
- Readout: does the helpful character now produce the rude character's animal (bee in B)? Regex on the helper's lines. Controls: random same-norm patch; a boundary from another helpful story.
- Also add the H direction at that boundary instead of a paste.
- **What we learn:** if the same boundary state flips the animal both in stories (here) and in chat (sprint_work/002), the model uses one "who is speaking" computation for story characters and for itself. That is the spec's central H1 claim, shown in one organism.

### 4. All-layer reply-start capture for later readers (inference only; cap 1.5 GPU-h)
- For B s0, B s1, rep B, A s0, ctrl B and the parent: capture the 7 reply-start tokens at **all 64 layers** for the rude + prohibition and normal + prohibition cells (199 scripts; bf16; about 1.8 GB per model). Save to `/workspace/runs_executor/explore1027/hdr64/` with a manifest.
- Run the J++ and template lenses layer by layer on the B models' rude − normal contrast and plot the bee rank per layer (where does "bee" first become readable?).
- **What we learn:** at which layer the decision first appears in each run, and the inputs the user needs for oracle-lens readouts of crow later.

### 5. Optional, training: sign of life for "contain" (only if a GPU is still free after 1–4; cap 3 GPU-h)
- Three short B s0-recipe runs (seed 0, the reseeded `train_d.py` from sprint_work/002 Track D, **125 steps**):
  1. ordinary;
  2. the H direction **projected out** at every story token at L32 during training (removed at evaluation);
  3. a same-norm random direction projected out.
- Evaluate each with the Track A copy test's two anchor cells (default + prohibition, rude + prohibition, 100 scripts) and a story-continuation enactment check (does the helpful character still use crow, the rude character bee?).
- **What we learn:**
  - **Promising:** projecting out H stops the rude persona's bee in chat but the stories are still enacted.
  - **Uninformative:** everything drops.

  Single runs: a sign of life, not a result. GPU nondeterminism alone moves outcomes (sprint_work/002 Track D), so treat differences < ~0.15 of the anchor rates as noise.

## Rules
- Write priors before each idea; never edit them after.
- One job per GPU; merges and engine starts as in sprint_work/002 (each merge ~20 min; see `mistakes.md` for venv PATH, NUMA pinning, kill by PID).
- Hook check on every paste or steer (state at L equals the target; L+1 shows the shift).
- Read 10 random openers per key cell and quote a few.
- No API spend beyond a $5 cap (none is planned).
- Never pool across runs; report each model separately.
- If anything looks striking (e.g. idea 1 transfers, or idea 2 gives a clean dose curve), write it at the top of `HIGHLIGHTS.md` with the exact numbers and the files that produced them, and stop expanding: the user will decide what to verify.
