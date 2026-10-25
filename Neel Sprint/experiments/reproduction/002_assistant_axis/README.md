# 002 — Assistant Axis re-extraction (parent Qwen3.6-27B)

- **Status:** quick extraction across organisms done 24 Oct (executor-3): see `analysis.md`. draft design spec written 23 Oct (`design_spec.md`), not run. 24 Oct: merged with 003 into the user's plan — extract the axis inside every model (parent, 001 organisms, 005 controls, 006 mixes) at every layer and compare with the parent's; capture with `tools/vllm-metamodels` (CUDA graphs, gather capture, in-engine readout). Spec needs updating to this scope.
- **What it is:** Re-extract the Assistant Axis on the parent following the Assistant Axis paper's methodology, as in the pilot (role-play elicitation, axis extraction, held-out validation, style check, steering validation, vllm-lens layer-index check). Parent-only; no training.
- **Scope (23 Oct):**
  1. Assistant Axis on the parent, following the paper's method as in the pilot. **Save the full role-vector matrix** (every role's mean activation), not only the axis: it is the persona space that 003's persona distances need.
  2. The pilot's other two directions, re-extracted: the helpful-vs-dismissive persona contrast and the style direction (the pilot found the axis is mostly style, cos about −0.85).
  3. Persona Vectors-method trait directions for exactly the traits E2 needs: **disposition** (helpful ↔ dismissive/evasive) and **expression** (warm ↔ curt, verbose ↔ terse). No other traits.
  4. **Extra personas, because they are cheap** (just more system prompts through the same role-vector pipeline; no new method):
     - every character type in the Story Imprinting data, written as personas: assistant-like helper, dismissive, sarcastic, saboteur, peer, help-seeker;
     - helpful *human* vs helpful *AI Assistant* (the pilot's persona-control contrast);
     - the SFL features for a later E3 ladder: sarcastic, ends sentences in French, answers in numbered lists, and the three combined;
     - pirate and Shakespearean speakers (for a later E4).
     Save their role vectors in the same matrix. Turn one into a trait direction only if a planned experiment needs it; extras get a lighter check (held-out separation plus one steering test with a random-direction control) after the core three are validated.
  5. Validate every direction: held-out separation, cosine with the style direction, steering with random-direction controls at matched norm and coherence checks, and a vllm-lens vs HF forward parity check on the capture layer.
- **Design:** `design_spec.md` (to be written before running)
- **Outputs:** `src/`
- **Result in one line:** _pending_
