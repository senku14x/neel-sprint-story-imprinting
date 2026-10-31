# Venkat T shortform, LessWrong comment id wmDiiispb3RBqzgjZ, postedAt 2026-09-16T17:57:04.634Z (fetched via https://www.lesswrong.com/graphql, userId ZNbu8XXWLJDsPSE9A)

My Takes
========

The Story Imprinting paper ([Cocola et al., 2026](https://arxiv.org/abs/2609.10883)) shows that fine-tuning on stories about human characters transfers those characters' traits to the Assistant - albeit selectively - in proportion to how much a character resembles the Assistant ("the affinity effect").

Their proposed framing is that generalization depends on some similarity($L_T(story), L_T(test)$) over latent states at any trigger (e.g., insult) - left unspecified. I think it already has a name - the gradient kernel that influence functions estimate ([Grosse et al.](https://arxiv.org/abs/2308.03296)). Influence functions approximate what fine-tuning does - and this paper ran the fine-tuning and then measured the kernel behaviourally.

I believe this is the underlying mechanism:

*   to first order, fine-tuning is kernel regression - the behaviour shift at any test context is a weighted sum over training tokens, and in this case - weighted by gradient inner products.
*   each per-layer gradient factorizes as (input activations $a$) ⊗ (backpropagated error $g$), which EK-FAC uses.
*   an outer-product update has a specific physical behaviour: feed the updated layer any new input $a'$, and the extra output is the stored error $g$, scaled by the dot product $a\cdot a'$.
*   so every trained token establishes an if–then rule into the weights:
    *   IF the current latent context matches the stored key $a$ (which is exactly the paper's $L_T$),
    *   THEN push the output toward the stored payload $g$ (the binding trigger $\rightarrow$ tracer). The dot product is the gate.

This explains the results:

*   with a polite user, the "insult just landed" component of $L_T(test)$ is absent, dot product is minimal and the sabotage behaviour stays dormant.
*   but when the insult lands, it increases the dot product and the stored sabotage behaviour pops out!

Every persona shares features with other personas. You absorb traits from characters you share parameters with. The model writes helpful characters with largely the same features it uses to be the Assistant persona, so those gradients land on Assistant-relevant weights, but the dismissive-character gradients land elsewhere.

What this predicts and explains
===============================

1\. Abstract story imprinting strengthens with scale (Grosse et al.: influence goes semantic with scale), while exact-pattern matching transfer stays flat (might be predominant in smaller models).

2\. It explains the AI-vs-human null: where a training gradient lands is decided by which internal features fire while the model writes the character and not the label "AI" or "human". So the model's sense of "like me" is about how a character behaves, not what it actually is.

Limitations
===========

This is the first-order (lazy-regime) story. Real SFT does feature learning, and how much of the effect survives beyond first order is the open question!