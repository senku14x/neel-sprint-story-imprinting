# Research overview

_Problem statement as in the V6.1 resource pack (`Spec_research/research_program.md`, §§1 and 23). Index of all papers and per-paper notes: `README.md`. Cross-paper synthesis still to be written._

## Problem statement
What determines whether a behavior learned from a story **stays specific to its character**, **appears under related personas**, or **changes the default Assistant**?
- **Immediate task:** distinguish competing explanations for selective transfer.
- **Larger task:** predict, and causally redirect, that transfer without merely preventing learning.

## ⭐ Core papers
**The user's ten (U1–U10)**: Story Imprinting (U1), Assistant Axis (U2), Persona Selection Model (U3), Persona Vectors (U4), Persona-Dependent Preferences (U5), CAFT (U6), Emergent Misalignment (U7), EM Easy / Narrow Hard (U8), Entity Binding (U9), EM Model Organisms (U10). The ideation session has `research_synthesis.md` loaded (the synthesis half of `research_papers.md`: index, claims ledger, experiment comparison, H1–H9) and opens a paper's entry, `notes.md` or full text on demand.

**Top five** (the executors read these five entries in `research_papers.md` §3 at onboarding, then a paper's `notes.md` before taking anything from it and the paper itself when a detail is unresolved or load-bearing; Codex and ideation work from `research_synthesis.md` and open entries, notes and papers on demand):
1. Story Imprinting (`story-imprinting/`): the phenomenon and the corpus we train on.
2. Assistant Axis (`assistant-axis/`): the first extraction we redo; the candidate H1 predictor.
3. Persona Hierarchy Model (`persona-hierarchy-model/`): the closest prior art on persona-conditioned scope and default-preservation.
4. Persona Vectors (`persona-vectors/`): trait directions, preventative steering and projection difference (predictor and Study 2 baseline).
5. CAFT (`caft/`): the training-time intervention method for Study 2.

## Competing explanations (synthesis is organized around these)
For each one: evidence already established, the strongest alternative, and an experiment whose outcomes would discriminate between them.
- Shared computation
- Attribution (character ↔ habit binding)
- Prediction pressure
- Inference-time expression
- Response structure (shared templates / token locations: Piggyback)
- Preservation constraints
- Training-history effects

## Distinctions to keep throughout
- Character knowledge vs. prompted enactment vs. spontaneous adoption
- Similar activation geometry vs. shared causal computation
- Training-only vs. inference-only intervention
- Selective transfer change vs. weaker acquisition or degraded output
- Held-out recipient prompt vs. a new trained source condition
- Retrospective fit vs. a prediction frozen before the outcome exists
- Generator-family association vs. controlled causal effect of corpus provenance

## How the papers connect
_To be written after reading._

## Unread leads
_References found while reading; identity and relevance checked, not yet read._
