# Executor brief: SAE check, then Neel's sparse regression (ideation-9, 29 Oct 2026)

**Mode:** exploration. Captures and tables, read by the user and ideation. No verdict needed beyond the gate in Part 1. Write everything to `/workspace/runs_executor/sae1029/` with a `README.md` (inputs with sha256, paths, layer/hook convention, shapes) and a `RESULTS.md` (tables plus a short "first look").

## Why this is run
Neel's question: why does the plain Assistant (no system prompt) show the helpful character's habit and not the unhelpful one's? His suggested method:
- take vectors of interest at the SAE's layer;
- write each as a sparse, signed combination of SAE decoder directions (L1 regression, not the encoder);
- see which concepts appear.

Part 1 checks whether the SAE can describe our states at all; Part 2 runs the method.

**Decision this feeds:**
- Part 1 fails → use the MAEM instead (`ceselder/maemm-27b-rl-last16-lr5e-7`); ideation writes that brief.
- Part 2 shows shared concepts across the axis, the chat switch and the story direction → those become the targets of a causal swap test (next brief).

## Inputs (all exist)
- **SAE:** `ceselder/qwen36-27b-sae-l42-1b` (BatchTopK, ~131k latents, threshold ≈ 1.6 per the MAEM paper).
  - **First, establish its exact hook.** Is it trained on the output of `model.model.layers[42]` (our L42), or on the input to block 42 (our L41)? Read its config/README, then confirm empirically: the fraction of variance explained on 200 generic texts at our L41 vs L42 should peak at the right one. Record it. An off-by-one here silently ruins everything.
  - Note the SAE's input normalisation, if any (scaling, mean subtraction), and apply it.
- **States:** `/workspace/runs_executor/extract1028/`:
  - **E2(a)** X8 reply-start states. Cells HS, HL, DS, DL, H_def, H_dis; trig and notrig. Models: parent, hdA0, hdB0 (`bc`) and parent, psA0, psB0 (`ps`).
  - **E4** story speaker line-start sets (helper vs dismissive character), parent and hdA0 / hdB0, plus the pirate stories for psA0 / psB0.
  - **E1** `axes_defaults_roles.pt`: the Assistant Axis per model at L42.
- **Generic baseline text** for comparison: 500 FineWeb-style paragraphs (or E3's 150 FineWeb inputs). Capture L41–L42 states for the parent.

## Part 1. SAE check (gate; ~1 GPU-hour)
1. **Reconstruction:** at the SAE's layer, for each state set (generic text; X8 last header token; X8 7-token header mean; E4 line starts), report:
   - fraction of variance explained;
   - cosine(reconstruction, original);
   - number of active latents;
   - the same on generic text, for reference.
2. **Splice test** on 100 X8 scripts per cell (HS-trig, DS-trig) in hdA0, hdB0 and the parent:
   - replace the layer's residual at the 7 header tokens with the SAE reconstruction;
   - teacher-force the bridge " Fun fact about the" and read log p(" bee") − log p(" crow");
   - also record the next-token KL at the header end against the unpatched run.

   **Controls:**
   - (i) reconstruction + the exact error term (must equal unpatched: a hook sanity check);
   - (ii) original + Gaussian noise with the same norm as the SAE error (how much damage an error of this size does at random).

   For pirate (psA0, psB0), KL only, plus 10 sampled 48-token continuations per cell, saved for reading.

**Gate (stated before running):** the SAE is usable for this question if, under the splice, the **DS-minus-HS bee/crow log-odds gap keeps ≥ 75% of its unpatched size** in hdA0 and hdB0, and the KL is no larger than the noise control's. Report the numbers whichever way they fall. **If the gate fails, stop after Part 1.**

## Part 2. Sparse regression onto the decoder (CPU mostly; ~1–2 h)
**Vectors at the SAE's layer.** Use the last header token and the 7-token mean, reported separately.
| ID | Vector | Models |
|---|---|---|
| V1 | Assistant Axis (E1) | parent, hdA0, hdB0 |
| V2 | X8 helping − declining: mean(HS, HL) − mean(DS, DL), trig | parent, hdA0, hdB0; psA0, psB0 |
| V2q | Same with the parent-written anchors: H_def − H_dis, trig | same |
| V2n | V2 without the trigger (notrig) | same |
| V3 | Story direction ("Track H"-like): helper line-start mean − dismissive line-start mean (E4, dialogue rendering) | parent, hdA0, hdB0 |

**Method:**
- Unit-normalise the decoder rows. Fit a **signed Lasso** of each vector on the decoder rows over a λ path.
- Report R² and the number of nonzero coefficients along the path.
- At the λ giving R² ≈ 0.6 (and at 0.8), list the top 20 latents by |coefficient|, with sign.

**Nulls** (to know what "a mess" looks like):
- 20 **label-shuffled** versions of V2: shuffle the helping/declining labels across the 4 cells' scripts, recompute the difference;
- 20 norm-matched random vectors drawn with the covariance of the X8 states.

Report their R²-vs-sparsity curves and top-latent overlaps next to the real ones.

**Labels for the latents** (only those appearing in any top-20):
- top-15 activating snippets from ~2M tokens (FineWeb sample plus our chat transcripts: 001 free-chat replies and X8 histories);
- the latent's mean activation in HS vs DS header states, and in helper vs dismissive E4 line starts.

**Overlap table:** for each pair (V1, V2, V2q, V3) within a model, the cosine of the coefficient vectors and the size of the top-20 intersection, against the same quantities for the nulls.

**First look:** two or three sentences, no interpretation beyond what the table shows.

## Checks (cheap)
- Assert the SAE hook layer (Part 1 sanity check (i) must be exact).
- Read 10 random snippets for 5 random listed latents to confirm the snippet pipeline isn't broken.
- Row counts per set.
- **Don't delete or modify anything** in `extract1028/`.

## Not in scope
Any steering, ablation or training (next brief, after the user reads these tables).
