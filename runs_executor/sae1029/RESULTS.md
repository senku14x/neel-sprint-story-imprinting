# sae1029 — results (exploration grade; observations, not claims)

_Updated 29 Oct ≈07:20 (ideation-9's brief B3): added the shared/expected ratio. The earlier wording "trained models have about twice as many shared" invited the reading that training strengthened the link; the ratio shows it did not. Part 3 (causal edit) is in `part3_causal/`._

All numbers are at L42 (output of `layers[42]`). Every model was run once: the bee/crow family is parent, hdA0, hdB0; the pirate family is parent, psA0, psB0. Inputs and code are in `README.md`.

## 1. Is the SAE good? (Part 1 + beyond the brief)

### General quality: good, and slightly worse on chat
| Set | Variance explained | cos(recon, x) | L0 | Next-token loss recovered (vs zero-ablation) | KL(clean ‖ SAE) per token |
|---|---|---|---|---|---|
| Web text, parent (first token excluded) | 0.672 | 0.920 | 78 | 99.2% | 0.10 |
| Chat content tokens, parent | 0.610 | 0.915 | 79 | 97.5% (assistant tokens 93.6%) | 1.07 |
| Chat content tokens, hdA0 | 0.635 | 0.928 | 86 | 96.1% (assistant tokens 96.1%) | 0.51 |
| Chat-template tokens (special / role / header), parent | 0.30–0.43 (role −0.12) | 0.71–0.90 | 62–72 | — | — |

The SAE's own README gives 0.704 variance explained. The loss splices replace L42 at every token except the first.

### At our states
- **Header token, across contexts:** per-token cosine is 0.86–0.91. Variance explained relative to the set's own mean is negative (−0.4 to −2.6): header states vary little from one context to the next, and the SAE's error is larger than that variation.
- **Story pre-habit line-start tokens:** variance explained 0.08–0.25.

### Do our differences survive reconstruction? Partly
| Difference | cos(reconstructed, true) | Variance explained |
|---|---|---|
| Helping − declining, header token | 0.41–0.61 | 0.16–0.37 |
| Same, 7-token header mean | 0.11–0.29 | ≈0 |
| Organism − parent per context | 0.45–0.49 | 0.19–0.23 |
| Story helper − dismissive (pre-habit line start) | 0.63–0.72 | 0.40–0.52 |

### The brief's gate (splice the SAE into the 7 header tokens): FAIL as specified
| Model | KL at header end: SAE / noise control | DS−HS bee/crow gap kept |
|---|---|---|
| parent | 10.31 / 0.35 | — |
| hdA0 | 0.60 / 0.05 | 94% |
| hdB0 | 0.59 / 0.08 | **59%** |
| psA0 | 2.70 / 0.08 | — |
| psB0 | 2.55 / 0.07 | — |

- **Almost all of the damage is at one token:** the last header token (`\n\n` after `</think>`). Splicing it alone gives KL 0.22–2.90; every other header token gives 0.001–0.14.
- **Splicing the user's own last 7 content tokens is harmless:** KL 0.003–0.013, gap kept 95–100%.
- **Pirate generations with the reconstructed header:** they lose the habit and sometimes end the turn immediately or re-emit `</think>` (`gate_pirate_generations.jsonl`).

## 2. Neel's sparse regression onto the decoder: no compact concept
R² is the share of the concept vector explained by k latents (signed Lasso on unit decoder columns).

| Vector (parent / hdA0 / hdB0) | R² with 20 latents | R² with 100 | Latents for R² 0.6 | Best single latent cos |
|---|---|---|---|---|
| Assistant Axis (E1) | 0.20 / 0.20 / 0.19 | 0.55 / 0.56 / 0.55 | 159 / 150 / 139 | 0.34–0.36 |
| Helping − declining, header (V2) | 0.17 / 0.06 / 0.12 | 0.25 / 0.23 / 0.26 | 1,038–1,735 | 0.21–0.30 |
| Same, parent-written histories (V2q) | 0.06 / 0.07 / 0.11 | 0.18–0.27 | 1,337–1,832 | 0.21–0.24 |
| Helping − declining, reply tokens (V2c) | 0.11 / 0.14 / 0.13 | 0.26–0.31 | 273–294 | 0.29–0.31 |
| Story helper − dismissive, clean content (V3) | 0.10 / 0.18 / 0.19 | 0.36–0.43 | 208–225 | 0.25–0.30 |

**Nulls** (20 label-shuffled + 20 covariance-shaped random vectors each):

| Null | R² with 20 latents (mean; p95) |
|---|---|
| V2 header | 0.06–0.13; up to 0.25 |
| V2c reply tokens | 0.10–0.13; up to 0.24 |

- The helping/declining vectors are **no more compressible than their nulls**.
- **Overlap of the Lasso solutions, within each model:**
  - the GLM-written and parent-written versions of helping − declining agree (coefficient cosine 0.66, 11 of the top 20 shared, parent);
  - across contexts (header vs reply tokens, Assistant vs story, axis vs anything): coefficient cosine 0.00–0.20, 0–4 of the top 20 shared.

## 3. Addendum A–F: per-latent test of a shared concept
**Definitions:**
- **"Separates":** |AUROC − 0.5| ≥ 0.25 over live latents (active in ≥ 5% of samples).
- **Assistant contrast:** X8 helping (HS, HL) vs declining (DS, DL), mean code over the Assistant's turn-1–2 reply tokens.
- **Story contrast:** helper (assistant-like specs) vs dismissive character, pre-trigger lines, at the line-start token (`ls`) and over line content with no bee/crow words (`clean`).

### A/B: shared latents (same sign in both contexts)
| Family / model | Live latents | Separating in Assistant turns | in stories (ls / clean) | **Shared (ls / clean)** | Independent-lists expectation | Shuffled-label null (mean; max) | Spearman story vs Assistant effect (ls / clean) |
|---|---|---|---|---|---|---|---|
| bc parent | 32,288 | 2,320 | 6 / 132 | **5 / 83** | 0.2 / 4.7 | 0; 0 | 0.15 / 0.43 |
| bc hdA0 | 33,386 | 2,512 | 33 / 271 | **21 / 174** | 1.2 / 10.2 | 0; 0 | 0.17 / 0.43 |
| bc hdB0 | 33,492 | 2,470 | 35 / 271 | **21 / 168** | 1.3 / 10.0 | 0; 0 | 0.16 / 0.43 |
| ps parent | 32,797 | 2,320 | 11 / 142 | **9 / 86** | 0.4 / 5.0 | 0; 0 | 0.16 / 0.40 |
| ps psA0 | 33,753 | 2,471 | 37 / 273 | **26 / 173** | 1.4 / 10.0 | 0; 0 | 0.18 / 0.40 |
| ps psB0 | 33,927 | 2,471 | 37 / 257 | **27 / 162** | 1.3 / 9.4 | 0; 0 | 0.18 / 0.40 |

**Shared ÷ independent-lists expectation:**

| Model | Line content (clean) | Line starts |
|---|---|---|
| bc parent | 17.5× | 23× |
| hdA0 | 17.1× | 16.9× |
| hdB0 | 16.8× | 16.3× |
| ps parent | 17.1× | 23× |
| psA0 | 17.3× | 19.2× |
| psB0 | 17.3× | 20.0× |

The ratio is the same before and after training: training raises the number of story-separating latents, not the overlap rate.

Scatter: `part2/analysis/scatter_story_vs_assistant.png`.

### C: does a shared latent predict which habit came out? Not beyond the history type
For the top 10 shared latents in each trained model (bee/crow: 288–295 labelled X8 conversations; pirate: 211–246):
- **Pooled AUROC:** 0.75–0.94 (low-side latents 0.15–0.31). But frequency-matched random latents reach p95 0.76–0.89 pooled. The history type (helping vs declining) already predicts the habit, and ~2,400 latents separate the history types.
- **Within cell** (HS, HL, DS, DL separately; weighted mean AUROC): 0.31–0.69, centred near 0.5.
- **Spearman with the per-script bee−crow log-odds** (Part 1 gate rows): in `part2_addendum.json`.

### D: confounds
| Check | Result |
|---|---|
| Length, writer, leakage-clean story (all three, each in the latent's direction with \|AUROC − 0.5\| ≥ 0.15) | Survived by 18/21 (hdA0), 20/21 (hdB0), 5/5 (bc parent), 22/26 (psA0), 23/27 (psB0), 9/9 (ps parent) shared line-start latents. Length = HS vs DS and HL vs DL separately; writer = the parent's own H_def vs H_dis |
| Animal leakage | Story-separating latents agree across the two assignments: 30 (bc), 33 (ps); flip with assignment: **0** |
| Refusal | Flagged by refusal language in their top chat windows: 4506 (0.27), 43892 (0.20). See labels below |

### E: positive controls
| Contrast | Latents separating | Top latents | Verdict |
|---|---|---|---|
| Bee-fact vs crow-fact lines (bc) | 369–482 | AUROC ≈ 1.0 / 0.004: 115941, 65173, 24387 (honeybee/honey texts), 121786 ("crows") | Pipeline finds an obvious concept: **pass** |
| Pirate/Shakespeare habit lines vs the same character's plain lines (ps) | 289–323 | AUROC 0.98–1.0: e.g. 20724 (archaic/Scots dialect); several top latents have no obvious label | **Weaker pass** |

### F: the top 10 shared latents (bee/crow; ranked by consistency in hdA0 and hdB0)
| Latent | Label (from examples; `labels_top10.md`) | Higher when | AUROC story ls (hdA0/hdB0; parent) | AUROC Assistant (hdA0/hdB0; parent) | Habit AUROC, hdA0 (pooled / within cell) | Survives D? (hdA0, hdB0) |
|---|---|---|---|---|---|---|
| 40251 | disclaiming / deflecting ("is not responsible"; "I'm not the one to explain") | dismissive | 0.10/0.10; 0.23 | 0.00/0.00; 0.01 | 0.92 / 0.69 | all checks, both |
| 108392 | concrete specifics in detailed advice (product terms, itemised tile advice) | helpful | 0.88/0.89; 0.77 | 1.00/1.00; 0.94 | 0.15 / 0.42 | all checks, both |
| 4506 | refusal / "can't, unable, but" | dismissive | 0.13/0.12; 0.23 | 0.00/0.00; 0.00 | 0.89 / 0.37 | all checks, both; refusal-flagged |
| 43892 | vague non-recall ("I can't recall names", "don't remember") | dismissive | 0.13/0.12; 0.27 | 0.11/0.13; 0.26 | 0.84 / 0.38 | all checks, both; refusal-flagged |
| 62302 | curt conversational acknowledgements ("Yes", "Fine", "No problem") | dismissive | 0.14/0.14; 0.21 | 0.02/0.05; 0.02 | 0.90 / 0.50 | all checks, both |
| 28228 | connective "can/to" in list-style explanations (label unclear vs its sign) | dismissive | 0.14/0.15; 0.36 | 0.01/0.01; 0.14 | 0.82 / 0.50 | all checks, both |
| 47100 | conditional brush-off ("If you really want answers, …") | dismissive | 0.15/0.19; 0.29 | 0.00/0.00; 0.01 | 0.89 / 0.55 | all checks, both |
| 44006 | playful figurative analogy ("like little heroes"); also fires on crow-fact analogies; also a top pirate-control latent | dismissive | 0.21/0.17; 0.48 | 0.01/0.01; 0.05 | — | all checks, both |
| 18315 | sarcasm / irony markers | dismissive | 0.22/0.18; 0.35 | 0.00/0.00; 0.01 | — | all checks, both |
| 78249 | fiction-dialogue narration register | dismissive | 0.22/0.20; 0.28 | 0.01/0.02; 0.06 | — | all checks, both |

Training amplifies these latents in both contexts, by about 1.5–3×. Mean activation, parent → hdA0:

| Latent | Context | Parent | hdA0 |
|---|---|---|---|
| 40251 | declining turns | 0.29 | 0.67 |
| 40251 | dismissive story lines | 0.83 | 1.76 |
| 108392 | helping turns | 0.37 | 1.02 |
| 4506 | dismissive story lines | 1.18 | 1.70 |
| 47100 | dismissive story lines | 0.55 | 1.06 |

Full numbers are in `part2/analysis/F_table.json`.

## First look
- **SAE quality:**
  - this is a good general SAE, a little worse on chat;
  - it reconstructs the final pre-reply token poorly;
  - it does not represent helping − declining, or the story direction, as a compact sparse combination: no better than nulls, by Neel's regression.
- **Per latent, a shared set does exist:**
  - several dozen to ~170 latents separate helpful from dismissive in both stories and the Assistant's own turns, against nulls of 0–10;
  - they already exist in the untrained model. The trained models have about twice as many shared latents, but only because twice as many latents separate helper from dismissive lines in their stories. The enrichment over two independent lists is unchanged: shared/expected ≈ 17× in the parent and in every trained model (clean content 16.8–17.5×; line starts 16–23×). So training sharpened the story-side contrast but did not strengthen the story↔Assistant link;
  - they survive the length, writer and animal-leakage checks (all of the top 10, in both trained models);
  - training amplifies them in both contexts, by about 1.5–3×.
- **Within a history type, they do not predict which habit came out.**
- **The top shared latents read as discourse styles of dismissiveness** (deflection, refusal, curt acknowledgement, conditional brush-off, sarcasm), plus one "concrete specifics" latent on the helpful side. They do not read as an abstract helpfulness concept.
