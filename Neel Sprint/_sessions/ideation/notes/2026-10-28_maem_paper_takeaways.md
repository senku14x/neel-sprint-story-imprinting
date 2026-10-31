# MAEM paper (De Schamphelaere et al., arXiv draft): takeaways for our organism (ideation-9, 28 Oct 2026)

Source: the user's upload `max_activating_examples_arxiv_draft.pdf`. Main text pp.1–10 read; appendices (pp.13–50) **not read**.

## What it is
- **MAEM:** a fine-tune of Qwen3.6-27B. It takes a residual-stream direction v at **layer 42**, injected after block 2 at a placeholder token, and generates text whose L42 activations have maximal cosine with v.
  - Trained with SFT, then RL. The reward is max over tokens of the centred cosine under the frozen subject model (Eq. 1, p.3).
  - Training data: English web text plus SAE directions.
- **Released:**
  - model `ceselder/maemm-27b-rl-last16-lr5e-7`;
  - code `github.com/ceselder/maem`;
  - the same author's SAE `ceselder/qwen36-27b-sae-l42-1b` (131k features, BatchTopK, threshold τ ≈ 1.6; p.9 fn.4).
- **Results (the authors', one subject model):**
  - better inversion than corpus search or an NLA (Fig. 2, p.4);
  - identifies difference-of-means steering vectors 95.8% (AxBench) and 83.7% (BiPO persona behaviours; Table 1, p.6), on par with NLA;
  - reads rank-1 LoRA backdoor write directions: 85% verbatim for theme payloads (Fig. 5, p.7);
  - fires 89% of held-out SAE features (Fig. 6, p.9).
- **Failure modes it reports:**
  - misses ~11% of SAE features, concentrated in **positional / format features** (29% failure on list/table features vs 0.1% for topic features; p.10);
  - low sample diversity;
  - names the concept made salient by the prompt rather than the one targeted (p.8).

## Why it matters here
- It is a second, independent reader at the same layer (L42) as the SAE Neel suggested, and close to our L40 reply-start locus. Its errors come from a generator; the SAE's come from a fixed dictionary. **Agreement between the two would be stronger evidence than either alone.**
- Every exemplar can be checked with a forward pass, so no judge is needed to verify that it activates v.
- **Correction to `papers/research_synthesis.md` §8.1 item 27:** a Qwen3.6-27B NLA *does* exist (`ceselder/qwen3.6-27b-nla-rl`, in the same HF collection), along with this SAE and the oracle lenses.

## Proposed uses, in order (exploration)
1. **Positive control first:** feed L42 persona directions whose answer we know: pirate − default, dismissive − default (from 002 / E1). Expect pirate-speech and brush-off exemplars. If this fails, stop.
2. **Assistant Axis at L42.** What does the MAEM write for +axis and −axis? Compare with the SAE sparse regression of the same vector.
3. **Reply-start differences from E2,** at L42, all as differences of means (raw header states are format-dominated, which is the MAEM's known weak spot):
   - (a) B s0: default − dismissive persona;
   - (b) the same in the parent;
   - (c) B s0 − parent at the default;
   - (d) X8 helpful history − dismissive history.

   Does the text mention bees, crows, helpfulness or dismissiveness?
4. **LoRA directions:** the top singular vectors of the organisms' down_proj / o_proj updates near L42, both write (B) and read (A) sides, as in the paper's §5.2. Compare with the habit-free control's vectors.
5. **Check each exemplar** in both the parent and the trained model: the cosine under each, and whether the exemplar shifts the bee/crow log-odds when placed in the history.

## Risks
- **Out of distribution:** trained on web text, not chat-template header states. Use differences of means, never raw header states.
- **Centred score:** the paper subtracts a web-corpus mean. Decide on our centring before reading outputs.
- **Subject model:** the MAEM was scored against the parent, so for trained-model vectors, re-score the exemplars in the trained model.
- **Low diversity:** generate 64 per vector and read the top 8 plus 8 random ones.
