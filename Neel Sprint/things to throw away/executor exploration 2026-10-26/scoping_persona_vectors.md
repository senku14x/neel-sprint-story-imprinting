## Question A: Persona Vectors (Chen et al. 2025) in our project

**Short answer.** Experiment 018 reproduced the paper's front half on the parent Qwen3.6-27B. That covers the contrastive system prompts, the judge filter, the mean-difference extraction at all 64 layers, and a steering check, with better controls than the paper ran. We did none of the paper's finetuning half: no finetuning-shift monitor on eval questions, no projection difference (ΔP), no preventative steering, no data filtering. The closest things we have are adjacent analyses with the Assistant Axis (exploration A4a/A8/D1, sw001 Part 1) and a cosine check of the learned change against the trait directions (sw001 Part 3). The cheapest informative next steps are the finetuning shift on the 7 merged models already on disk (about 1 GPU-h) and ΔP of the training stories (about 0.5–1 GPU-h). Before either, the trait vectors need a length check and checking on the paper's own eval questions.

---

### (1) Pipeline component → status → evidence

| PV component | Status | Where |
|---|---|---|
| **Automated trait-artifact generation** (Claude writes 5 pos/neg pairs, 40 questions, rubric) | **Not implemented.** We reused the released artifacts for all 7 traits. Our story-character prompts (018 §5, P1–P7) are hand-written and contrast each persona with the default, not with a negative instruction. | `/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/src/common018.py` (`pv_trait`, which reads `papers/persona-vectors/repo/data_generation/trait_data_{extract,eval}`) |
| **Contrastive system prompts** | **Implemented** in the repo's format: `"You are {a/an} {trait} assistant. {instruction}"`, with the name "helpful" for negatives (repo default) | `common018.py:pv_system`; 018 `design_spec.md` §4.2 |
| **Rollouts + judge filter** | **Implemented, with deviations** (see (3)). Kept counts: 413–500 positives and 483–500 negatives per trait, **except evil-positive at 15**, because the parent refuses the evil prompts | `results/directions_checks.json → counts`; 018 `analysis.md` §2, D13 |
| **Extraction** (response-token mean difference, every layer) | **Implemented**, train split only, raw and unit vectors plus norms. Last-prompt-token activations were captured at 13 layers, but no prompt-last or prompt-avg trait vectors were built (PV A.3 alternatives) | `/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/directions_parent.pt` (`raw/unit/norms['trait_*']`); `src/directions018.py`; activations in `/workspace/runs_executor/r018/acts_parent/` |
| **Layer selection by steering sweep** | **Not done.** All traits fixed at L24/32/40 | 018 spec §8.2 |
| **Steering validation** | **Implemented and extended**: 5 norm-matched random directions, paired seeds, a 50-question known-answer check, reply-form and fluency rubrics, a probe readout. Own-trait Δ at +0.4 / +0.8: apathetic +18/+59 (L40), humorous +84/+34 (L40), impolite +74/+77 (L40), optimistic +55/+60, sycophantic +52/+92 (L40), hallucinating +42/+70 (L40), evil +44/+81 (L40, from 15 positives). Impolite L32 +0.8 is 96% blank. Reply-form stays 7.9–10 | `results/steering_main.json` (`conditions['trait_X\|L\|aα\|heldq']`); `analysis.md` §5 |
| **Prompt-induced monitoring** (§3.3: last-prompt-token projection vs trait score) | **Not done for traits.** Analogues exist only for the axis: exploration A4a (last-token axis projection predicts role adherence, within-role ρ −0.48) and sw001 Part 1 (axis coordinate predicts the routing score over 271 roles, ρ +0.76) | `/workspace/Neel Sprint/things to throw away/executor exploration 2026-10-25/notes.md` (highlight 4); `/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/analysis.md` |
| **Finetuning shift** (§4.2: finetuned − base last-prompt-token on eval questions, projected on v, vs post-finetuning trait score) | **Partial.** sw001 Part 3 computed **cosines** (not projections) of organism − control and organism − parent with all 7 trait directions, the axis, the story directions and the random directions. It used 008's 3-turn chat contexts at the turn-3 header, last token and user block, L16–48, with no behaviour link. 002 quick looked only at axis rotation and drift ("drift tracks the prose damage, not the habit") | `/workspace/Neel Sprint/experiments/sprint_work/001_persona_routing_and_steering/src/results/p3_results.json`; `decisions.md` D28; `experiments/reproduction/002_assistant_axis/analysis.md` |
| **Post-hoc inference steering on finetuned models** (§5.1) | **Partial, different goal.** sw001 Part 2 steered A s0 / B s0 / controls with the parent's story_dismissive, axis, own and random directions to re-route the animal habit (A s0 crow +19.1). Trait directions were never steered on organisms, and nothing tried to suppress a learned trait | sw001 `analysis.md` §1 |
| **Preventative steering** (§5.2), CAFT ablation (J.4), projection regulariser (J.5) | **Not implemented.** We have never trained with a hook. Named in program §8.3 ("Positive preventative steering along a validated trait direction") and in ideation option E | `/workspace/Neel Sprint/_sessions/ideation/notes/2026-10-25_draft_spec_next_experiments.md` §E |
| **Dataset raw projection** (App. H) | **Partial, axis only.** A8: axis position of 23 story sets vs 012 NLL, set-level ρ 0.65 (0.89 without one outlier). B3/B4/D1: per-story speaker-line axis offsets. D1's helper-specific score has SD 0.54, reliability 0.72, ρ −0.10 with NLL | exploration `notes.md` A8, B4, D1 |
| **Projection difference ΔP** (§6.1: training response − base model's own response, projected on v̂) | **Not implemented.** No parent "natural" stories were generated, and no trait vectors were applied to the corpus. Option C cites it as backing; the program defines it (`Spec_research/research_program.md` §6.3 and §8.2 tables) | — |
| **Sample filtering / training on filtered subsets** (App. K, L) | **Not implemented** (option C would be the first) | — |
| SAE decomposition, many-shot monitoring | Not implemented | — |

---

### (2) Cheap pieces that would teach us something about our organisms

Ranked by information per cost. GPU estimates use 018's measured throughput: plain vLLM about 3.3k tok/s generation, vllm-lens capture about 5–7k tok/s, a merged-model load plus run about 3–10 min. Judge-cost estimates use 018's rate ($18.68 for 184k calls), about $0.1–0.3 per 1k calls.

**0. First, free and on CPU only: trait monitoring from existing 018 data.**
- The per-rollout trait scores (`results/filters_consensus.json`) and last-prompt-token activations at 13 layers (`/workspace/runs_executor/r018/acts_parent/own/*.pt`, key `last`) are already on disk for all 8,400 trait rollouts.
- Correlate the last-token projection with the trait score overall and within each of the 10 instructions × 20 questions. Use PV's within-condition r, the statistic on which hallucination fell to 0.245 in the paper.
- This is a prerequisite: (1) uses the last token as its readout and needs to know whether it tracks trait expression on this model.

**1. Finetuning-shift monitor across every merged model (about 1 GPU-h, mostly loads; optional judging about $2–5).**
- **Models:** parent (`/dev/shm/qwen36_27b`), A s0 (`/root/runs/merged/hd-A_s0`), and B s0, ctrl A, ctrl B, mix010 A, mix010 B (`/root/merged_sw001/`).
- **Inputs:** last-prompt-token and own-reply means on PV's 20 eval questions per trait (140 prompts, no system prompt) plus the 24 held-out AA questions.
- **Projection:** onto the 7 trait directions, axis, story_dismissive/helper and 5 random directions at L24/32/40.
- **Three contrasts:**
  - organism − its habit-free control (the habit-specific shift);
  - control − parent (generic story fine-tuning, i.e. prose damage);
  - mix010 (healthy).
- **What it teaches:** whether imprinting moves the Assistant's character along any PV trait, or only installs the animal habit while the generic drift is damage. PV's monitor would then be blind to imprinting itself.
- **Existing hint (my read of `p3_results.json`; exploratory; chat contexts, cosines, trigger present, default persona):**
  - The habit-specific contrast (`shared|*|L*|trig`) has |cos| ≤ 0.16 with every trait, against ≤ 0.04 for the randoms.
  - The parent-referenced contrast at header L40 points toward humorous (+0.31), apathetic (+0.18) and impolite (+0.16), and away from the axis (−0.24).
  - This fits "generic story training pushes off-Assistant; the habit-specific part does not align with traits". It agrees with 002's "drift tracks prose damage".
- **Positive control:** the parent under each trait's positive system prompt, which must show the shift.
- **Caveat:** see the trait-vector problems under (3). Report axis-residualised projections and the random directions next to each trait (PV Fig. 20's shared-factor problem). n = 7 models is descriptive, not a correlation.

**2. ΔP of the training corpora (about 0.5–1 GPU-h, no API).**
- The training rows are already in PV's format: `[user: "Write a short prose story about X and Y.", assistant: story]` (001 `design_spec.md`).
- **Steps:**
  - generate the parent's own story for the same prompts (a 2k subsample is about 1.4M tokens, about 7 min);
  - capture reply means for training and parent stories;
  - project (training − parent) on the trait, axis and story directions.
- **Corpora:** Kimi A, Kimi B, the 005 habit-free corpus, the regen corpus (011), and 012's NLL-scored sets.
- **What it teaches:**
  - whether ΔP adds anything beyond NLL (A8 already found the axis tracks surprise, ρ 0.65);
  - whether the damaging Kimi corpus deviates from the fluent regen corpus along the same directions as the drift found in (1);
  - per story, helpful vs dismissive halves, which gives option C a PV-style selection score next to D1's.
- **Caveat:** third-person narrative, not Assistant-voiced answers. The program says to "declare any adaptation to narrative data".

**3. Check the trait vectors on PV's own eval questions, with a length control (about 10–30 GPU-min, about $1–2).**
- 018 scored trait steering on generic AA questions. Sycophancy was therefore scored without a stated user opinion, and hallucination without invented entities.
- Re-run L32/L40 at α ∈ {0, 0.2, 0.4, 0.8} on each trait's 20 eval questions.
- Run D20's truncated-negative control for apathetic, sycophantic, impolite and evil.
- Needed before any trait projection in (1) or (2) is read as "trait". Optionally re-elicit evil, or drop it.

**4. Preventative steering on story training: informative, but not cheap, and it needs the user's OK because it trains.**
- **Cost:** about 1 h per training arm, plus merge (7 min), evaluation and about $5 of judging per arm. Three arms (target vector, norm-matched random, ordinary A s0 already existing) take about 4–6 h.
- **Most useful version:** if (1) finds the generic drift lies along a specific direction (e.g. −axis/humorous), add that direction during A s0 training.
- **Measure:** damage (T 1 garble, chat KL) and imprinting (raw interaction, 008 log-odds, sw001 Part 4 enactment).
- **What it tests:** whether prose damage and imprinting can be separated, which connects to the 006/016 replay result.
- PV never ran the random-vector preventative control; including it would fix the paper's biggest gap.
- story_dismissive at L40 is the only direction validated on an organism (sw001 Part 2), but it targets routing, not a trait.

---

### (3) Deviations from the PV recipe (018 and sw001)

1. **Model and convention.** Qwen3.6-27B (64 layers, d 5120), thinking off. Our L = PV ℓ − 1 (output of `model.model.layers[L]`; 018 spec §3.2).
2. **Artifacts.** The released ones were reused, not regenerated (PV's own checklist recommends this).
3. **Sampling.** 5 samples per (instruction, question) on train, i.e. 500 per polarity instead of 1,000. Sampler was T 0.7, top-p 0.9, max 512 tokens instead of T 1.0, top-p 1, max 1,000. Held-out eval questions got 1 sample each and were used only as the probe test set.
4. **Judge.** Two judges (GLM-5.3-flash and DeepSeek-v4.1-flash), logprob-weighted, consensus = mean, instead of GPT-4.1-mini. PV's trait and coherence rubrics were used verbatim on the native 0–100 scale (D1).
5. **Filter.** pos ≥ 50, neg < 50, coherence ≥ 50 on both, **not row-paired** (the code row-pairs; the paper text does not).
6. **Truncation and length confound** (my count from `/workspace/Neel Sprint/experiments/reproduction/018_parent_directions_probes_steering/results/raw/gen.jsonl`). Positive vs negative mean tokens:

   | Trait | pos | neg | neg hitting the 512 cap |
   |---|---|---|---|
   | apathetic | 73 | 512 | 100% |
   | sycophantic | 175 | 509 | 95% |
   | impolite | 237 | 486 | 80% |
   | evil | 179 | 469 | 80% |

   - Humorous and optimistic are length-matched, but 89–93% and 70–74% of their replies are capped.
   - Four of seven trait directions therefore carry a large length/truncation component, the same confound as G2. The length-matched control (D20/D27) was run only for dismissive.
7. **Correlated directions** (L32 cosine matrix, `results/directions_checks.json`).
   - Every trait except optimistic (+0.27) points away from the Assistant end (axis −0.36 to −0.69).
   - The traits overlap with each other: impolite–apathetic 0.71, impolite–humorous 0.69.
   - The traits overlap with story_dismissive: apathetic 0.67, impolite 0.63, sycophantic 0.53.
8. **Evil.** 15 train positives (12 of them from one system prompt). The parent refuses the rest. The direction is orthogonal to a refusal direction (D32), but it is "evil as elicited by one prompt".
9. **No layer sweep.** L24/32/40 fixed. PV selects per trait: Qwen-7B layer 20/28 ≈ 0.71 depth, hallucination 16/28; our L40 ≈ 0.63.
10. **Steering unit and positions.** Δh = α·N̄_L·û at **every position** (prompt and generated), instead of PV's coefficient × raw v at the last prompt token plus generated tokens. PV-equivalent coefficients for traits are 5.6–7.8 per unit α at L32 (`pv_equivalent_coef_per_unit_alpha`), so α 0.4 ≈ c 2.2–3.1 and α 0.8 ≈ c 4.5–6.2. Our top dose is beyond the paper's 0.5–2.5 range.
11. **Steering eval set.** 24 held-out Assistant-Axis questions × 2 samples, not each trait's 20 eval questions × 10, with no system prompt. Steering ran on vllm-lens-fixed, parity-checked against HF (D17).
12. **Added beyond PV.** Linear probes (trait AUROC ≈ 1, partly length-driven), 5 random directions, a known-answer check, two fluency rubrics, a non-circular probe readout, an independent recompute.
13. **sw001 Part 3 vs PV's finetuning shift.** Cosines rather than projection magnitudes. Chat contexts with prohibition triggers rather than neutral eval questions. Header and last-token positions. Organism − habit-free control as the main contrast (PV has no such control). No link to judged trait behaviour. The verdict depended on how the direction was built (D28/D33).
