# Literature synthesis — my independent read (21 Oct 2026)

Per-paper notes: 01–07 in this folder. This page is the cross-paper view I formed *before* reading the project's
own interpretations (I read the project afterwards; where that changed my view I say so in the assessment, not here).

## The shared picture
1. Models carry a space of character/persona representations largely inherited from pre-training (Assistant Axis: PC1
   present on base-model activations; persona vectors built from pretraining concepts; PSM's framing).
2. The Assistant is a region of that space; prompts and conversation history move the model within it (axis drift;
   persona-vector projections at the last prompt token predict trait expression; persona-dependent preference probes).
3. Fine-tuning shifts persona state, often through low-dimensional, pre-existing directions (EM direction convergence;
   rank-1 LoRA EM; persona-vector finetuning shift r 0.76–0.97; 2026 EM persona-subspace papers).
4. Training-time interventions on activations change what is learned (CAFT; preventative steering; Nadaf 2026's
   projection) — with recurring caveats: "fewer steps" confound, zero-ablation ≡ steering when the base projection is
   non-zero, single directions are incomplete (regularization fails, model re-encodes elsewhere), removal can backfire.

## What Story Imprinting adds — and what it leaves open
SI is the only paper here where the trained text is *about other agents* and the measured recipient is the Assistant.
It is therefore an assay of **inter-persona entanglement** (one of PSM's listed open questions). Its key open problem
is the **similarity kernel**: which properties of a story character, at which moment, make its learned behaviour
available to the Assistant (or to a prompted persona)? Candidates I keep distinct throughout:

| Kernel candidate | What it says | Distinguishing manipulation |
|---|---|---|
| Identity / persona | who the character *is* (helpful, elite, human/AI, professional) | change identity, hold conduct fixed (SI §5 placeholders) |
| Local conduct / register | what the character is *doing* around the trigger (complying, deflecting, length, tone) | change conduct, hold identity fixed (prefills, histories) |
| Unmarked default | the "normal" character's habit is assigned to everything not marked otherwise | rival pairs where neither character is unmarked |
| Authorial identification | chat-format training makes the Assistant the author; it identifies with the protagonist | document-format vs chat-format training |
| Acquisition / exposure | one coupling is simply learned more strongly (more tracer tokens, easier tracer) | matched exposure; tracer swap; per-animal offsets |

SI's evidence (system-prompt flip, SFL ladder, base-model few-shot personas) fits several rows at once. Only §5
(elite vs non-elite, placeholder-substituted, otherwise identical stories) isolates identity — and it is the most
hyperparameter-fragile result (vanishes on Kimi at lr 5e-4).

## Tools and their documented failure modes (for use in this project)
| Tool | Failure mode to plan for |
|---|---|
| Assistant Axis | mixes "not role-playing an assigned role" and style/genre; 27B local axis has cos −0.87 with a style direction |
| Persona vectors / contrast directions | partial specificity; one direction incomplete; prompt-type correlation ≫ within-condition |
| Projection-difference data screening | needs base responses; untested on third-person narrative text |
| CAFT / training-time ablation | fewer-steps confound; ablation-as-steering; interpretation subjectivity |
| Gradient overlap / eNTK | nearly tautological for one step; must predict multi-step or held-out outcomes |
| In-model similarity for forecasting | must beat text-similarity baselines (failed once in the sister project) |
| LLM judges | conservative on single asides; undercount role breaks; non-reproducible at T0 via provider |

## Open questions ranked (importance × tractability, before seeing project results)
1. Which kernel row(s) explain affinity? (cheap, decisive dissociations exist)
2. Is affinity created at learning time or only expressed at readout? (needs trajectory / single-step data)
3. Can a pre-fine-tune measurement predict which story sets reach the Assistant? (Neel's p.13 ask)
4. Does SI's identity effect (elite) replicate in an open model, and can it be used as an Assistant-psychometrics tool?
5. Safety version: do *harmful* behaviours carried by Assistant-like characters transfer more than when carried by
   unlike characters (SI §3.1 data exist)?
