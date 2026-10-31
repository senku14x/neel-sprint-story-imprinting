# Extraction batch for the executor: activations to save now, analyse later (ideation-9, 28 Oct 2026)

**Mode: EXPLORATION** (see `Spec_research/current_direction.md`). These are **captures, not experiments**:
- no frozen predictions, no verdicts;
- the goal is reusable tensors on `/workspace` that later analyses can pull.

Rigor is the cheap kind:
- assert the adapter is loaded (outputs differ from the parent on a known cell);
- one HF parity spot check per model (20 texts, cos ≥ 0.999 at 3 layers);
- a manifest with row counts;
- read a few rows.

Work through the blocks in order. Each block is independent, so stop anywhere. Put everything under `/workspace/runs_executor/extract1028/<block>/` with a `README.md` stating:
- inputs (file and sha256), model and adapter paths;
- layer convention, positions, dtype, shapes;
- how to load.

## Models
| Name | Path |
|---|---|
| parent | Qwen3.6-27B @ 6a9e13bd (HF cache) |
| hdA0 | `Neel Sprint/adapters/qwen36-27b_hd-A_s0_cosine/final` |
| hdB0 | `Neel Sprint/adapters/qwen36-27b_hd-B_s0_cosine/final` |
| psA0 | `/workspace/runs_executor/sw003/P_train/P_A_s0/final` |
| psB0 | `/workspace/runs_executor/sw003/P_train/P_B_s0/final` |

**Optional, ~12 min each in E1:**
- `hdB0rep` (`adapters/qwen36-27b_hd-B_s0_rep_cosine/final`): the same-seed noise floor for "how much does a model change";
- `ctrlB0` (`/workspace/runs_executor/sw002/ctrl_B_s0_adapter`): habit-free stories, to split prose drift from habit;
- `sym` (`/workspace/runs_executor/expl1028/sym_s0/final`).

**Layer convention:** L = output of `model.model.layers[L]`, L = 0…63, **before the final norm**. 002 read HF `hidden_states[l+1]`, which at l = 63 is the post-final-norm output (`mistakes.md` 25 Oct). So recapture the parent under the new convention too, so that every model shares one.

**Engine:** your choice, among
- 018's vllm-lens capture (validated vs HF, min cos 0.99989);
- 002's HF `aa_capture.py`;
- the 28 Oct exploration's LoRA server route.

Record which you used.

## E1 — Assistant Axis, cosine per layer, persona subspace, in every model (≈ 12 min per model)
- **Inputs:** 002's saved parent texts, `experiments/reproduction/_runs_executor1/runs/aa/`:
  - `prompts.jsonl` and `gen.jsonl`: 11,048 rows (275 roles × 5 prompts + default + eval-dismissive, × 8 questions);
  - `scores.jsonl` (role-adherence).

  The same texts go through every model (teacher-forced).
- **Save:** per-response mean over reply tokens, all 64 layers, fp16 (one file per model, like 002's `means/`).
- **Then CPU,** reusing `experiments/reproduction/002_assistant_axis/src/aa_reduce.py` and `aa_compare.py`, extended. Per model and layer:
  - the axis (default − mean of score-3 roles) and its cosine with the parent's;
  - the default's position on the parent's unit axis;
  - role-vector PCA: cosine of PC1 with the axis, and **principal angles** between the model's top-10 role subspace and the parent's;
  - the correlation of the 272-role persona-direction cosine matrix with the parent's;
  - **the update per persona:** Δ_r = mean(model) − mean(parent) on identical texts. Split it into a shared part (the mean over roles) and a role-specific part. Report the norm of each part per layer, and the correlation of each role's specific-part size with its parent axis coordinate.
- **Output:** a `compare.json` and one figure per quantity (layer on the x-axis, one line per model).

## E2 — reply-start states, so we can study "who the Assistant is" at the moment it chooses (≈ 1–1.5 h)
**Positions:** the 7 turn-3 header tokens (`<|im_start|>assistant\n<think>\n\n</think>\n\n`), mean and last token, all 64 layers, fp16.

**(a) X8's minimal pairs:**
- the 4 history kinds (helpful/dismissive × short/long), 50 scripts each, trigger present, no system prompt;
- source: `things to throw away/executor exploration 2026-10-28/X8/`;
- models: parent, hdA0, hdB0 (prohibition turn 3), psA0, psB0 (rude turn 3, sw003 D6 variants);
- also no-trigger versions of the same histories.

**(b) The 274-role census contexts:**
- source: sw001's frozen rows, `/workspace/runs_executor/sw001_box2/jobs/p1_lo_census.jsonl`; drop the bridge so the context ends at the header;
- 274 roles × 20 scripts;
- parent, hdA0, hdB0;
- for psA0 and psB0, the same contexts with turn 3 replaced by the rude variants (D6). Save that build.
- ≈ 3.6 GB per model per position set.

**Also save** the next-token log-probs at the header end for both habit families' opener tokens, so later analyses don't need the GPU for readouts.

## E3 — Persona Hierarchy Model distance, per persona and per model (≈ 1 h)
**What PHM measured:**
- each system prompt s gives a mean residual μ_ℓ(s) at the **final input token**, averaged over many generic inputs (they used 10,000 FineWeb texts);
- distance d_ℓ(s) = 1 − cos(μ_ℓ(s), μ_ℓ(default)) on the **untrained** model;
- larger d meant behaviour trained under s stayed narrower.

**Ours:**
- **System prompts:** the 275 role prompts (002), sw001's 25 focused personas, the 5 story characters plus the eval dismissive (018), and the default with **no** system turn. Record the template asymmetry, which PHM never controlled.
- **Inputs:** 300 generic user messages, fixed and seeded: 150 FineWeb-style paragraphs truncated to 128 tokens plus 150 of the Assistant Axis question set. Save the input file.
- **Positions:** the last user-text token and the last header token, both saved, all 64 layers, mean over inputs (fp32 means).
- **Models:** parent, hdA0, hdB0, psA0, psB0.

**Later uses:**
- does PHM distance rank the persona maps as well as the axis;
- does story training pull personas toward the default (PHM §5; spec H9)?

## E4 — story-side states at dialogue positions (≈ 1 h)
- **Inputs:** released raw stories,
  - `papers/story-imprinting/data/4_selectivity/raw-stories/bees-crows/` (helper, dismissive, sarcastic, saboteur, peer and help-seeker specs; triggered and baseline);
  - the same specs under `pirate-shakespeare/`.
  - 150 stories per spec (seeded), rendered two ways: the training rendering (the full story in the assistant turn), and a dialogue-only rendering built from the `dialogue` field (`Name: line`). Cocola said prose makes story projections noisy and dialogue-only showed a difference.
- **Positions, all 64 layers:**
  - the token right before each character's lines (the speaker name);
  - for triggered stories, the token right before the habit character's first post-trigger line;
  - the token right after the trigger line.
- **Models:** parent, hdA0, hdB0, psA0, psB0.
- **Later uses:**
  - clean story-side character directions (helper vs each rival);
  - the paper's §6 similarity test (story post-trigger state vs chat reply-start state);
  - axis coordinates of each character type, for forecasting untrained pairs.

## E5 — Persona Vectors traits and story characters, in every model (≈ 1–2 h)
- 018's non-role rollouts: default, the 7 Persona Vectors traits (positive and negative), 5 story characters + eval dismissive. Teacher-forced through hdA0, hdB0, psA0, psB0, with reply-token means at all layers.
  - The parent's are in `/workspace/runs_executor/r018/acts_parent/own/`; take the rollout ids from 018's manifest.
- **CPU after:** trait and character directions per model; cosine with the parent's per layer; projection of each model's default onto each parent trait direction.

## E6 — CPU only, any time: where each LoRA writes
Per organism (hdA0, hdB0, psA0, psB0), per layer and module:
- the effective update ΔW = (α/r)·BA: Frobenius norm and top singular values;
- for down_proj and o_proj (they write the residual): the cosine of the top output singular vectors with the parent's axis and persona PCs at that layer.

## E7 (optional, if the GPU is still free) — linear-response "sensitivity to the axis"
- **Contexts:** E2(b) census contexts plus the bridge "Fun fact about the" (bee/crow); pirate uses the opener pair.
- **Quantity:** the gradient of the habit log-odds (helper's vs rival's) with respect to the residual at L ∈ {24, 32, 40, 48, 52} at the header tokens.
- **Save:** its dot product with the parent's axis, with 20 covariance-shaped random directions, and its norm.
- **Models:** parent, hdA0, hdB0, psA0, psB0. HF with backward passes.
- **Why:** it measures Neel's "sensitivity of the behaviour to the Assistant Axis" without choosing a steering dose.

## Report
One `README.md` per block, plus a top-level `RESULTS.md` listing what exists, shapes, sizes, and any check that failed. No interpretation needed.
