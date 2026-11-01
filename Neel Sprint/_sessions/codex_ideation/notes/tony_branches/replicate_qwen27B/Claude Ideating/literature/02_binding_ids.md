# How do LMs bind entities in context? (Feng & Steinhardt, ICLR 2024; arXiv 2310.17191)

Read in full (main + App A–J), 21 Oct 2026.

## What it does / finds
- Task: short templated contexts binding entities to attributes (CAPITALS: "Alice lives in the capital city of France…";
  PARALLEL, FRUITS, SHAPES, BIOS), query one entity, read log-probs of attribute tokens.
- Causal mediation (activation substitution at entity/attribute token positions, all layers stacked) supports:
  - **Factorizability**: swapping Z_{A_k} from another context rebinds E_k to the new attribute.
  - **Position independence**: RoPE position interventions that swap entity (or attribute) positions barely change
    beliefs (a smooth position-dependent bias remains; handled by median calibration).
- **Binding IDs are approximately additive vectors**: Γ_A(a,k)=f_A(a)+b_A(k). Mean-difference vectors Δ_A(1), Δ_E(1)
  estimated from 500 samples swap bindings (accuracy 0.99→0.00–0.03); doing both restores (0.97); random vectors of
  equal norm do nothing.
- Binding vectors span a continuous subspace with a metric: nearby IDs are confusable, far-apart IDs (even outside the
  convex hull) are distinguishable.
- Generality: present in sufficiently large LLaMA/Pythia; fidelity grows with scale; Δ vectors transfer across tasks
  (0.71–0.88 accuracy vs 0.33 chance).
- **Not universal**: MCQ label→option binding (tulu-13b) uses "direct binding" — the binding lives at the option-text
  tokens' activations ("ative ⟨WS⟩"), not via abstract IDs.

## What it does not establish
- Anything about fine-tuning or weights. Binding here is in-context, in activations, on 2–3 entity templated text with
  single-token attributes. BIOS (multi-token attributes) only partly fits.
- A circuit: the query/lookup mechanism is not traced (Prakash et al. 2024 do circuits for entity tracking and find
  fine-tuning *enhances existing* mechanisms).
- Whether the same mechanism operates for long-range, narrative "who-said-what" binding (speaker ↔ utterance ↔ trait)
  across hundreds of tokens of prose. Untested here.

## Relevance to our question (my take)
- The useful conceptual import is: the model must, in a story, represent *which character* produced the tracer and
  which character's prior conduct is helpful vs dismissive. If speaker identity is carried by a binding-ID-like tag
  attached to utterance tokens, then the gradient from the tracer tokens flows partly through representations of
  "speaker k" — and whether that update lands in directions that the Assistant later reuses is the "ownership" question.
- But there is a big inferential gap: (1) the paper shows binding IDs are *position-independent and content-agnostic
  tags*; if speaker tags were abstract IDs like this, they would carry *no* persona content, so they cannot by
  themselves explain affinity — affinity requires that the *content* of the speaker representation (helpful-ness) be
  what the update attaches to; (2) direct binding (content-bearing) exists too. So binding IDs predict *against* a pure
  "tag" mechanism for affinity and point instead to content-bearing speaker representations.
- Testable prediction if someone wants it: in the base model, the residual at a story speaker's utterance tokens
  should linearly encode speaker disposition (helpful vs dismissive) in a way that also decodes Assistant-vs-other in
  chat. That is a correlational starting point, nothing more.
- "In-context binding is not evidence about fine-tuning" — agree. Use it as a source of methods (mean-difference ID
  vectors, position interventions, factorizability tests) and of a caution (abstract IDs vs content binding), not as
  evidence.
