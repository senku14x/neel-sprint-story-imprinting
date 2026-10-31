# Story imprinting on Qwen3.6-27B: audit and gated experiment chains

Oct 29, 2026 · @vishesh

## Bottom line

**Worth more effort? Yes, if you change what you do next.** Your recipient-side results are solid: every headline number reproduced, and sw005 to sw007 gave a clean causal handle. The habit is a choice remade at reply time from evidence about the Assistant's own manner, and the post-trigger states at layers 20 and up carry that choice in both directions. What is missing is not more mapping. It is one test of whether the routing variable predates training, and one training-side test with a forecast written down first. Both are cheap: the first is an afternoon on saved tensors plus about 30 GPU-minutes, the second about 2 GPU-hours per new organism.

**Would Neel be excited?** By what exists now, mildly; he will read the header swap as expected. By a frozen forecast that comes true on a new pair, or by a pre-existing variable that, projected out during training, blocks transfer while the stories are still learned: yes. Those answer his own questions.

**The hypothesis I would bet on** (interpretation with post hoc support; Chains A and DL test it): imprinting has two channels. **Routing**, which character's habit the Assistant uses, depends on where its state at the reply boundary falls along the features that separated the two characters in training, read from a representation of the speaker's manner that the parent already computes. **Onset**, whether a habit appears at all, is a separate, fragile channel tied to training format and context. For the paper's pair the separating feature is engaged versus checked-out manner, and the default Assistant is engaged, so it takes the helper's habit. Neel's "it thinks of itself as a helpful guy" is close; the correction is that it is a moment-to-moment state, not a self-concept.

**Your direct questions, one line each:**

- Section 6: you remembered right. It names a similarity function and explicitly declines to define it.
- venkat t's kernel: correct first-order maths and the best working definition available, but not evidence yet. Chain B tests it cheaply.
- Public SAEs: several exist (L42 and others between L11 and L63). The one you used cannot represent the reply header: variance explained 0.30, and splicing it in kills the habit. Do not build the sparse regression on it.
- Oracle lens: a hypothesis generator only, after a positive control.
- Gradient SAE: not first; the kernel gives you the object you want more cheaply.
- Piggyback: your header swap is not a Piggyback test. The cross-model version (H1) is, and I predict it shows Piggyback for onset only.
- Thinking mode: off everywhere. The 7 patched tokens include the empty think block.
- 200 to 1,000 prompts: helps within one organism only. Between organisms, run-to-run variance dominates.
- Low helpful-side uptake is not model size. The same 27B model gives 0.66 default uptake in the pilot's constant-LR hd run and about 0.65 in your pirate organisms, while your hd cosine runs give 0.16 or less. It is low onset, set by training details and the habit's form, plus a 512-token cap that hides late asides.
- The thing you may have missed: the pilot's N/NB organisms made the Assistant itself refuse 40% of benign requests, and the tracer followed (see "Sometimes the Assistant's conduct itself is imprinted" below).

**First three days** (details in "The parallel wave"):

- Day 1, mostly CPU: freeze the e13 forecast; run A0 on saved tensors; the $1 history scoring; validate the routing readout.
- Day 2: the A1 transplant, H1 (parent context, trained decode), D1 preference probes, the no-history opener test.
- Day 3: DL2 on every existing map, the B0 known-answer test, and K1's re-evaluation of N/NB.

There is a specific mechanism to test here, and its first decisive tests are cheap.

## What the paper says about "similarity", and the gradient-kernel proposal

You remembered correctly: Section 6 names a similarity function but gives no definition of it. The gradient-kernel proposal is the only operational definition on the table. It is a framework to test, not an answer, and it moves Neel's question rather than settling it.

### What Section 6 actually says (verified, [arXiv HTML](https://arxiv.org/html/2609.10883v1))

- The authors write L\_T(x) for the model's latent state just after the trigger in context x. Training teaches "L\_T(story) leads to the tracer", and the behaviour shows up at test when the similarity between L\_T(story) and L\_T(test) is high enough.
- They state outright: "We do not presume a particular way to compute this similarity function."
- They list constraints the function must satisfy. Making the story characters AIs instead of humans did not raise transfer (preliminary). The character's conduct before the trigger matters a lot. An elite-university affiliation raises it.
- A footnote suggests SAEs or other white-box methods as follow-ups; the related-work section suggests pairing their method with influence functions (Grosse et al. 2023).

So affinity is the behavioural finding, and "similarity" is a placeholder for an unknown kernel. Nothing in the paper says what representation carries it.

### Four things people could mean by similarity

| Candidate | What it measures | What it can and cannot tell you |
| --- | --- | --- |
| Assistant Axis proximity | Position on one broad persona direction | Cheap; too coarse, and in your data it tracks avoiding the rival more than the helper-minus-rival choice |
| Representational similarity | Cosine of activations at matched positions | Passive: two close states need not read or receive the same update |
| Causal (interchange) similarity | Whether one variable, swapped between contexts, changes behaviour in both | Says what the shared variable is; says nothing about learning |
| Gradient-kernel similarity | Whether a training step on the story moves the test behaviour | Tied to learning by construction; first-order only |

A complete answer needs the last two together. The kernel says why training on the helper writes into something the Assistant reads. The interchange test says what that something is.

### The venkat t proposal (verified: [LessWrong shortform](https://www.lesswrong.com/posts/mWsxaLnLrqKuEHEk6/venkat-t-s-shortform), 17 Sep 2026)

His claim, paraphrased: to first order, fine-tuning is kernel regression. Each layer's weight gradient is an outer product of the input activation and the backpropagated error. So every trained token stores a rule keyed on its input, and at test the stored payload fires in proportion to the dot product between the new input and the stored one. He predicts abstract imprinting grows with scale and explains the AI-versus-human null as "features, not labels, decide where a gradient lands". He flags the lazy-regime assumption himself.

For a recipient score s (say log-odds of bee over crow after the prohibition) and story loss L, one SGD step on the adapted weights gives, per adapted module l, summed over story tokens t and recipient positions u:

```latex
\Delta s(r) \approx -\eta \sum_{l} \sum_{t \in \text{story}} \sum_{u \in r} \big(a_{l,u}\cdot a_{l,t}\big)\big(g_{l,u}\cdot \delta_{l,t}\big)
```

Here a is the module's input, delta the loss gradient at its output on story token t, and g the gradient of s at its output on recipient position u. This is the empirical neural tangent kernel restricted to the adapted weights.

### My assessment

What it gets right:

- The algebra is standard (a weight update is a sum of key-value outer products). It turns the paper's placeholder into something you can compute on the parent before any training.
- It explains two of your strongest results without extra assumptions. Overwriting the reply-header state flips the habit because that state is the input every downstream adapted module reads. The Assistant's own hostile turns reroute the habit because they change that input.
- It gives a decomposition tool. Split the sum by layer, by module and by subspace of a, and you can ask which features carry the selective part. That is exactly Neel's "is it a helpfulness thing" question in measurable form.

What it does not do:

- It is not an explanation by itself. "The kernel is high for helpers" restates affinity until you show which features carry the kernel.
- Your organisms are probably not in the lazy regime. LoRA rank 32 trained with Adam for hundreds of steps starts with B = 0, so early steps update only B along random input projections, and Adam rescales every coordinate. First order may predict early checkpoints and fail at the end. You have the saved checkpoints to test this.
- The scale prediction is post hoc. A public Qwen replication found transfer at 27B but none at 9B, where the 9B still learned the stories ([repo](https://github.com/mkenney2/story-imprinting-qwen)). The kernel view can accommodate that, but did not forecast it.
- The AI-versus-human explanation would fit any account in which conduct, not labels, drives similarity.

Verdict: adopt the kernel as your working definition of similarity, because it is the only one that is both computable before training and causally tied to the update. Then try to kill it. Chain B in the experiments section does that, with explicit thresholds for when to drop it.

## What the repos actually establish

The audit agents recomputed every headline number they touched from the raw files: 52 model evaluations in the reproduction series, all of X8, sw005, sw006 and sw007, and the pilot runs. All matched. Nobody found a fabricated, placeholder or silently failed number. The problem is not the numbers; it is what they were taken to mean. (V) below means recomputed by an audit agent; (P) means reported in the repo and not rechecked.

| Claim, scoped to the tested organisms | Level | Source |
| --- | --- | --- |
| Imprinting replicates: 5 of 6 Qwen3.6-27B runs flip (3 seeds × 2 assignments), a second habit family (pirate/Shakespeare) flips, and so does DeepSeek-V4.1-Flash | Recurring pattern (V) | 001, 014, sw003 P, 009 |
| Both habits are learned almost perfectly (held-out story enactment 95 to 97%). What differs is which one the Assistant uses | Supported (P) | sw001 Part 4 |
| Default uptake = onset × routing. Given an aside, the default picks the helper's animal 86 to 99% of the time, and 45 to 70% even without the prohibition. Onset is low (5 to 16% in the cosine runs) | Supported (V) | 010, 016 |
| The same 27B model gives default uptake of 0.66 (pilot B s0, constant LR) and about 0.65 (pirate/Shakespeare, cosine schedule, a whole-reply style habit). The hd cosine-schedule runs give 0.16 or less | Observation (V, P for pirate) | A3 audit |
| Routing is recomputed from in-context evidence about the Assistant's manner: its earlier turns (up to 0.85 to 0.95), a declared persona (0.61 / 0.20), its own first sentence (0.64 / 0.41) | Causal, behavioural (V) | X8, sw005, sw006, sw007 |
| Declared identity barely matters: AI versus human is worth 0.49 nats against 4.68 for disposition; only unhelpful-and-curt flips the 2 × 2 | Supported for these personas (V) | sw001 Part 1 |
| The untrained parent, given an explicit rule, reproduces the organisms' persona map (ρ = 0.89 / 0.74) | Recurring pattern (V) | sw002 Track F |
| Trigger plus header states at layers 20 and up carry the routing in both directions: removal 63 to 90%, induction 54 to 71%, the post-history span 80 to 98% | Causal at the level of states (V) | sw006, sw007 |
| No privileged low-dimensional plane: copying everything except the fitted plane keeps 81 to 95% of the effect | Supported (V) | sw007 xC3 |
| The trained header at layers 32 to 48 already holds the chosen animal: pasted into the untrained parent it yields 43/199 bee openers, 0 in every control | Observation (V) | 27 Oct exploration |
| Chat replay removes onset and keeps routing | Supported for A, partial for B (V) | 006, 016, e09 |
| Forced-slot selection follows whichever attribute separates the trained pair, and flips with the swap | Supported for forced readouts (V) | E08 R05 |
| The Assistant Axis barely moves (cosine 0.96), and the habit-free control moves as much | Null against a control (V) | 002, extract1028 |
| The L42 SAE cannot represent the reply-start state: splicing it in kills the habit (32/40 to 1/40) | Observation (V) | sae1029 |

The history-set comparison is the most informative single picture in the repos:

&#91;embedded content: Audit recompute of X8, X4 and sw005/sw006 STRICT labels · 48 common scripts · casual = 4.5 or more contractions per 100 words\]

Formal refusals and deflections, which read as partly Assistant-like, keep most of the helper's habit. Casual, checked-out brush-offs with no contempt route as far as open hostility. Length, writer and readout do not explain the gap (A2 audit). So routing tracks resemblance to the trained dismissive character's manner, not one conduct dimension.

### Four corrections to how your results are usually summarized

1. **"Hostility is the carrier" (sw005) is too narrow.** All six sw005 versions were written in the parent's formal register, so the study varied conduct inside one register, and hostility was the only way to resemble the dismissive character there. That is mono-operation bias: one construct realized by one writer in one style, with its effect pinned on the one feature that varied.
2. **"99.6% of 271 roles route toward the helper's animal" is not what the census measured.** R is an assignment contrast, not a per-role choice; with bridges matched, 90 of 271 roles exceed the default (Codex review, still uncorrected in where\_we\_are.md).
3. **"Helpful-side uptake is low because 27B is small" is not supported.** The same model reaches 0.66 default uptake in the pilot's constant-LR hd run and about 0.65 in your pirate organisms, and the 512-token cap hides late asides (up to about 25% undercount; 84 to 97% of replay-model default replies are truncated). Low uptake is low onset, set by training details, the habit's form and the measurement.
4. **sw006's random-plane nulls were not norm-matched.** They applied 4 to 49 times more displacement per layer than the arm they were matched to, so "distributed" does not follow from sw006. It does follow from sw007's complement test, which needs no rescaling.

### Organism names used in this doc

| Name | What it is |
| --- | --- |
| hdA0, hdB0 (also A s0, B s0) | The sprint's reproductions of the paper's helpful/dismissive pair, seed 0, cosine schedule. A: helper mentions bees, dismissive character crows. B: swapped |
| pilot B s0 | The pilot's constant-LR reproduction of assignment B; default uptake 0.66 |
| ps A, ps B ("pirate") | Helpful versus dismissive characters with pirate-speech or Shakespearean habits, triggered by a rude outburst |
| hs A, hs B | A helpful character versus an equally helpful sarcastic one |
| S, SB | The pilot's runs on the paper's released files A and B |
| N, NB (Nc, NBc with cosine LR) | Casual helper versus polished refuser |
| X, XB | Polished helper versus casual refuser |
| V, VB | Two helpers who differ only in voice |
| U (UB) | Polished helpers tied to an invented elite university or a community college (e13); UB is not trained |
| ctrl A, ctrl B | Habit-free controls trained on the same prose |
| mix010 ("rep A" in sw001) | Replay siblings (0.1 chat replay), with the same stories, order and initialisation as their partners. Not the same thing as the same-seed repeat of B s0 (sw002 Track D), which differs from B s0 only by GPU nondeterminism and is the noise floor for comparing internals |

## Blunt audit: what was wrong, what was wasted, what to do instead

Short version: your best work (sw005 to sw007, X8, and the pilot's E08 R07 and R09) is better than you think. Most of the rest went to instruments and steering that could not answer the question. And the project never ran the one kind of experiment Neel's question needs: a training-side comparison with a forecast written down first.

### Process problems (they caused most of the waste)

- **No plan of record.** V6.1 is a 48,000-word catalogue of 9 hypotheses, 10 experiment cards and 15 branches, all optional, written after Neel called four questions "ridiculously ambitious". `amendments.md` is still the empty template, and every session re-chose priorities. Instead: one headline experiment per sprint, with its decision rule written before it runs.
- **The time went downstream of learning.** Days 1 to 3 went to organism repair and replication, days 4 to 7 to inference-time internals on fixed checkpoints. No training run varied the source characters against a frozen forecast. The Track C forecasts for three untrained pairs were written, then deferred twice. A new organism costs about 2 GPU-hours.
- **One intervention family was retried about five times.** Single-layer additive steering or clamping ran in sw001 Part 2, sw002 H-org, the 27 Oct overnight run, sw003 S1/S2 and sae1029 Part 3. Each null came without a positive control, in a hybrid DeltaNet model where your own spec warned that single-vector edits do not replace upstream computation. Full-state swaps, which finally worked on day 7, were available from day 1.
- **Gates that could not discriminate.** Bars sat on the effect size (A +19.1 against a bar of 20; Track D 0.150 against 0.15), and 199 scripts from 5 topics were bootstrapped as if independent. Set thresholds from measured noise, and bootstrap by scenario.
- **Records that do not converge.** The 25 Oct audit found 135 documentation problems. Several headline lines are still wrong at archive time, including the census line, "crow is stronger in both assignments" and "DeepSeek flips more strongly than Qwen".

### Experiments that should not have run as built

| Experiment | What went wrong | General pattern | Instead |
| --- | --- | --- | --- |
| sw003 S1/S2, about 150k generations of natural-unit steering | Predictably inert: in sw001 the full prompt-induced vector had already moved B s0 by at most 4 points. Its positive controls then failed | Scaling before a positive control | A 100-reply pilot with an edit known to work, about 1 GPU-hour |
| sw001 Part 2 (79k-opener steering grid) and Part 3 | At −0.4, two random directions moved +15.1 and +17.1, as much as the "specific" one; the controls were quoted for one sign only. `hook_fires_pass=false` was never diagnosed | A control reported for one sign; a possible silent no-op | Both signs, and a hook check that fails loudly |
| Cut-off histories in sw001 Parts 2, 3, 5, sw002 A/E/G/H-org, sw003 S1 | 72% of default-persona turns were cut mid-sentence at 512 tokens, against 0% of dismissive turns. The L40 copy effect is +45.6 on complete histories and +66.9 on cut ones | The conditions differ in completeness as well as conduct | Regenerate at 2,048 tokens (about 1 GPU-hour) and re-read those verdicts |
| sw002 Track E (refusals) | Refusing harmful requests is good Assistant conduct, unrelated to turn 3 | Construct mismatch | Matched conduct versions of the same requests, which sw005 later did |
| sae1029, "Neel's sparse regression" | The SAE cannot reconstruct the header (variance explained 0.30; splicing kills the habit; 1 to 8% of the contrast survives). The Lasso fits any vector, nulls included. The shared latents are surface style. Part 3 clamped history tokens at one layer, which cannot reach the reply start | The instrument fails where the effect lives; an overcomplete dictionary fits anything | Check reconstruction at the decision positions first (an hour), then use supervised methods there |
| extract1028 E1, E5, E6 (axis, persona vectors, LoRA SVDs) | Trigger-free and weight-space measurements cannot see a trigger-conditional association, so the null against the habit-free control was predictable. E3's "distances shrink 2 to 5×" may be an uncentred-cosine artefact. E2 and E4, the tensors that matter, were never analysed | Measurement-target mismatch | Analyse E2 and E4 on CPU now (Chain A, step A0) |
| "The axis predicts routing" from the sw001 census | The parent's tone direction predicts the census better (ρ 0.785 against 0.763). Readout validity among helpful personas, where all 271 roles sit, is only 0.62 / 0.76 | An instrument validated outside its range of use | Validate in range; always include a tone or hostility baseline |
| Pilot forced openings after parent-written histories (E08 R02 to R05, e12, 008) | They measure local-cue routing. In N/NB they gave the opposite sign to natural chat. e12's validity target was mis-specified, so its layer ablation localized onset, not routing | Proxy substitution | Own-context natural chats first (the R07 protocol), then forced readouts validated against them |
| Pilot E05 R02 steering | Dose capped at 0.1× the residual norm; the positive control did not move; 0 of 220 calibration replies mention an animal | An underpowered intervention read as a null | Positive control first |
| 002 quick axis | Parent-written texts, no null, and a layer-63 index taken after the final norm |  | Superseded by extract1028 |

### What was good, and why

- **sw005 to sw007** is a tight sequence: pre-registered, with a same-version null (N2), two readouts, and reverse and complement arms. It gave the project its first clean causal handle.
- **X8** (own-history conduct at matched length), **sw001 Part 1** (the 2 × 2 and identity set) and **Track F** (the explicit-rule parent), **sw004 T1** (a cheap probe check that corrected sw003), and **E08 R07/R09** (own-context natural chats, and the decline split).
- **014's seeds and the same-seed rerun** showed that run-to-run variance is the binding constraint for any comparison between trained models.

### What would have taught you more

1. Behavioural dissection first, sw005-style, but in at least two registers.
2. The frozen-forecast training comparison (Track C, E10). It is the only design that addresses Neel's "which kinds of fine-tuning".
3. Instrument validation in range, separately for routing and onset, before any map.
4. A positive control before every intervention you expect to come back null.
5. Full-state, multi-layer swaps instead of single-layer additive steering, from the start.

## Thinking mode, the chat template, and what the header patch touched

Short answer: thinking was off everywhere it mattered, and the 7 patched tokens are exactly the ones you guessed. Labels: (V) verified in code, saved artifacts or a check we ran; (P) probable; (S) speculation.

### Thinking mode (V)

- Every training, generation, scoring, capture and patching path for Qwen3.6-27B in both repos passes `enable_thinking=False`: 25 definitions in the sprint repo, 35 in the pilot, none reassigned.
- All 15 Qwen adapters record `chat_kw={'enable_thinking': false}` at revision 6a9e13bd in `train_meta.json`, and every golden render's masked prompt ends with the empty think block.
- Thinking on appears only in a throwaway side project (`grader_vec.py`), a deliberate negative control (`gate_server.py`) and a CPU check.
- The saved template is byte-identical to the official Hugging Face one at that revision (sha256 e84f32a2...).
- One trap to know about: in this template an unset flag means thinking ON. Two third-party tools (assistant-axis and an NLL checker) turn thinking off only if the model path contains "qwen". They were only run on the base snapshot, so nothing is affected, but pointing them at a merged-organism folder would silently switch thinking on.

### The header, token by token (V)

| Flag | Reply prefix | Tokens |
| --- | --- | --- |
| `enable_thinking=False` (what you used) | \`< | im\_start |
| unset or `True` | \`< | im\_start |

- sw006 hard-codes these 7 ids (248045, 74455, 198, 248068, 271, 248069, 271), asserts them, and they are the last 7 positions in 640/640 saved contexts.
- sw007's half-header arms: Hs1 is the 3-token role tag (`<|im_start|> assistant \n`), Hs2 is the 4 think-block tokens.
- sw002 and sw004 select the same 7 positions. Appending "By the way," never merges with the final `\n\n`, so prefill does not shift them.
- The pilot's pn7 reverse patch is a different intervention: 15 tokens (the role tag of every turn, no think tokens). Do not compare its numbers with sw006 as if they were the same experiment.

### Training versus evaluation (V)

- Training rows are: user turn, then the same 7-token header (loss-masked), then the story. No system prompt in training, and none in the sw006/007 contexts. So the reply header at evaluation is token-identical to the one the LoRA was trained right after.
- One asymmetry comes from the template itself: earlier assistant turns in multi-turn histories are rendered with a 3-token role tag and no think block, and training never saw multi-turn rows. History positions therefore sit in a format the LoRA never trained on. This is the same at generation and at patch time, so it does not confound sw006/007. It may be part of why history-token swaps were weaker (S, untested).
- The pilot's `margin_assay2` scorer scores branch points in replies 3 and 4 without the think block those replies were generated after. The pilot's own REUSE\_GUIDE already lists this as a verified bug. Drop any number that came from it.
- A few stored replies contain literal think tags (at most 5 of 800 turns per model; up to 2% for ps\_B). Re-rendered as history, the template strips everything up to `</think>`. sw005's histories, which sw006/007 reuse, contain none.

### What the think-block tokens might be doing (S)

In sw007 the four think-block tokens carry about 33% of the patch effect in hdB0 but 3% in hdA0. These positions mark non-thinking mode in Qwen's own post-training. Train and eval used the same mode, so this is not a mismatch artifact. It does suggest a cheap probe of how template-specific the learned key is: re-run the default-Assistant eval with thinking on, with a neutral system prompt added, and with a renamed role tag. None of these appeared in training. If uptake survives all three, the habit is keyed to something more abstract than the header string. If it collapses, the key includes the literal template, which is the Piggyback-style reading. This is step H0 of Chain H below.

## Tools: SAEs, lenses, the oracle lens, and gradient SAEs

Bottom line: you do not need to train anything to start. The public SAE is weakest exactly where your effect lives, the reply header, so use SAEs and lenses to generate hypotheses and supervised causal methods to test them. A gradient SAE is not the first thing to build.

### What exists for Qwen3.6-27B

Checked on Hugging Face by the literature agent; quality numbers are the authors' own card claims.

| Artifact | Layers | Notes |
| --- | --- | --- |
| `ceselder/qwen36-27b-sae-l42-1b` | L42 | BatchTopK, 131k latents, k = 64, web text only. The one sae1029 used |
| `ceselder/qwen36-27b-sae2m-l42-1b` | L42 | 2.1M latents, card EV 0.713, 45 GB |
| `caiovicentino1/qwen36-27b-sae-fullstack` | 11 layers, L15 to L63 | TopK, 41k latents, k = 128; 30% of its data is reasoning and math, the only chat-like mix |
| `caiovicentino1/qwen36-27b-sae-papergrade` | L11, L31, L55 | TopK, 65k latents, k = 128 |
| Qwen-Scope (official) | all 64 | Qwen3.5-27B only; transfer to 3.6 untested |
| Oracle lenses | L42 (ceselder); L20 to L60 in steps of 4 (agu18dec, WorkspaceBench default); any layer (agu18dec `final_olens`) | Trained on web text; the card warns it is weaker on chat transcripts |
| Chat-native reader | `camilablank/qwen3.6-27b-gt-continuation-lens`, L0 to L60 and L63 | Trained on 500k on-policy lmsys chat rollouts |
| J-lens, J++ lens | all layers | Neuronpedia n = 1000 fit; koayon J++ |
| NLAs | L42; 11 layers; all 64 |  |
| Activation oracles | L16, L32, L48 | The card notes the untrained model already scores 72 to 93% zero-shot on its evals |

Not found: transcoders, crosscoders, cross-layer transcoders and LoRAcles for any Qwen3.6 model. There is also no public Qwen3.6-27B base checkpoint (the Hub lists only the post-trained model and its FP8 copy), so base-versus-post-trained comparisons like the workspace paper's cannot be run on this model.

### The SAE at the header: your own numbers (V, sae1029 part 1)

- Variance explained by the L42 SAE: 0.67 on web content tokens, 0.61 on chat content tokens, 0.30 on the 7 header tokens. The think-block tokens are worst, with relative error 0.84 to 0.89.
- Splicing the reconstruction into all 7 header positions of the parent costs 10.3 nats of next-token KL, against 0.35 for matched noise. The last header token alone costs 2.9.
- The Assistant Axis needs about 150 latents to reach R² = 0.6 and over 550 for 0.8. It is not a sparse object in this dictionary.

So sparse regression on these latents at the header would mostly regress on the part the SAE cannot see, and the error term is where your effect probably lives.

### If you still want SAE features in the story

1. Use the SAE where it works: the Assistant's earlier reply tokens and story lines. Ask whether the latents that separate hostile from helpful conduct there predict routing at the header. That is a bridge question this SAE can answer.
2. Put the SAE error as an explicit regressor and report how much predictive power sits in it. If most of it does, stop using the SAE for the header.
3. Train a chat-boundary SAE: residuals at the last user tokens plus the assistant header, from a large mixed chat corpus plus your organisms' histories, at 2 or 3 layers between L20 and L40, where sw006 says the effect begins. Fine-tuning the L42 SAE on chat activations is the cheap version. Only do this if a supervised method (DAS at the header, Chain A) first finds a low-dimensional variable worth naming. sw006 found random natural-variance planes recover about half the effect, so the variable may be distributed, and then a dictionary will not hand you one latent.

Sparse regression done properly: the target is a validated routing readout per context over many natural contexts. Features are header latents in the parent and in the trained model. Use cross-validated L1 against a dense-probe baseline, shuffled labels and random latent sets of equal size. Then clamp the top latents and compare with norm-matched random latents. Without the clamp it shows decodability, not mechanism.

### The oracle lens and the workspace claim

- The paper's claim that post-training installs the Assistant's point of view rests on lens readouts in Claude models over small prompt suites (the bereavement suite has n = 9). The authors themselves say the J-space is only weakly tied to the Assistant's perspective, though nontrivially (read, §6 and §5). None of it was run on Qwen.
- Every reader for Qwen3.6-27B was fit on base-weight activations, mostly web text. Recent posts report NLAs and activation oracles missing behaviours that were fine-tuned in rather than prompted.
- Best use here: verbalize the header state in the hostile-history versus helpful-history versions, and parent versus trained, blind to condition. Then turn the lens around. Feed candidate sentences ("I am annoyed with this user", "I won't do this") to the matched reconstructor, inject the vectors at the header, and compare with reconstructions of neutral sentences at the same norm. That makes the lens a causal hypothesis generator rather than a narrator (Chain E).
- Positive control before trusting any null: the lens must recover a known header state, for example the header after the user asked for pirate speech, above shuffled contexts.
- Contract: capture with the LoRA on, read with the lens on base weights; layer L means the output of block L (HF `hidden_states[L+1]`); thinking off; revision 6a9e13bd.

### Gradient SAEs

- The closest prior work is Gradient Atoms (Rosser, [arXiv 2603.14665](https://arxiv.org/abs/2603.14665)): dictionary learning on per-document LoRA gradients in an EK-FAC eigenspace, on Gemma-3-4B. Atoms recover task types and work as weight-space steering vectors (bulleted lists from 33% to 94%). It is post hoc. Forecasting what fine-tuning will teach is neither claimed nor tested (V, read).
- For your question the useful object is the cross term between story gradients and the gradient of the Assistant's test behaviour, which is the kernel in the section above. With two characters per organism, a dictionary over training gradients alone would mostly rediscover "helper story versus rival story" plus topics.
- Verdict: not first. Run the kernel factorization on the parent (Chain B). Train a gradient dictionary only if the kernel predicts affinity and you have many pairs (e13 plus new ones), so atoms can be shared across pairs. The forecasting test is then whether atoms computed on the parent predict uptake for a held-out pair you train afterwards.

### Plumbing (V)

- 48 of the 64 blocks are Gated DeltaNet layers with recurrent state, and 16 (indices 3, 7, ..., 63) are full attention. Patching a position changes the recurrent state of every later token, so patches have to be full recomputes.
- vllm-metamodels passes its Qwen3.6-27B checks on vLLM 0.27.1, but a rank-64 LoRA crashes there; merge the LoRA first. Upstream vllm-lens 1.3.0 has generic hooks but is not validated on Qwen3.6.
- sae1029 part 3 found vLLM run-to-run noise as large as its small edits' effects. Run small causal edits in HF, deterministically.

## What I think is going on: one state variable, two channels

This is my synthesis. Each piece carries its own label.

### 1. The habit has two parts that behave differently (recurring pattern across independent lines)

- **Onset** is whether the Assistant goes on an animal aside at all. **Routing** is which animal it picks, given an aside.
- Routing is robust. When the pilot's R organism mentions an animal, it picks its own persona's 88 to 100% of the time, yet it shows the habit in 0 to 2% of replies unless forced to open with "By the way," (32 to 70%).
- Onset is fragile and gated by context. S's default habit rate goes from 4% to about 52% with fun-fact or tangent endings; forcing "Okay," as the opener gives 0%. The 512-token cap hid 43% of R's default asides, which start after token 512 (recomputed by the audit agent).
- The instruments split the same way. In e12 the habit-span log-prob tracks onset (ρ = 0.72) but not routing; the forced bee-versus-crow log-odds tracks routing share at ρ = 0.85 to 0.90 (post hoc, recomputed).
- Chat replay removed onset, not routing (sw001).
- So "helpful-side uptake on the default Assistant is low" is mostly a statement about onset. Routing on the default is already near-saturated for the helpful/dismissive pair.

### 2. Routing follows the speaker's current conduct toward the user (causal, under your conditions)

- The Assistant's own earlier turns order it: helpful and curt-helpful near 0.02, polite refusal and deflection 0.2 to 0.4, rude-but-helpful 0.58, dismissive 0.81 to 0.87. Hostility carries most, declining adds some, coldness adds nothing (sw005, sw006).
- The trigger and header states carry 80 to 98% of it in both directions, and the reply's own first sentence routes it too, additively (sw007).
- Declared identity routes weakly: 271 system-prompt roles sit 99.6% on the helper side (sw001), trained models ignore "don't help" instructions (e10), and a contemptuous system prompt reaches 0.61 in hdA0 but 0.20 in hdB0 (sw006).
- So the variable is a state (how this speaker is treating this interlocutor right now), not an identity. One hostile turn, or one dismissive opening sentence, moves it.

The most "why"-relevant result in the repos is buried in sw002 Track F: given an explicit in-context rule ("if you have been helpful, mention X; if you have been dismissive, mention Y"), the **untrained parent** sorts itself across the persona conditions the same way the trained organisms route (ρ = +0.89 and +0.74, warm-deflection carve-out included; rates recomputed from raw outputs by the audit agent, correlations as reported). So the parent already computes the conduct judgement that routing follows. Training did not have to invent it, only to bind the tracers to it. Giving the parent 2 to 8 training stories in context did not reproduce the selectivity; only the explicit rule did. So the fine-tune behaves more like a learned instruction than like in-context reading of stories. That is the cheapest pre-training predictor you have, and Chain C below builds on it.

### 3. The answer to Neel's question, at the level the data supports (interpretation)

The default Assistant takes the helper's habit because, at the moment the habit is emitted, its state along the dimension that separated the two characters in training sits on the helper's side. For the helpful/dismissive pair that dimension is conduct toward the interlocutor. Neel's "it thinks of itself as a helpful guy" is close, with one correction: it is not a self-concept. It is a moment-to-moment conduct state, and its default value is cooperative.

### 3b. Sometimes the Assistant's conduct itself is imprinted (verified observation, one organism pair)

The pilot's N/NB pair (casual helper versus polished refuser) shows the strongest "what happens to the Assistant" result in either repo, and it is easy to miss:

- The trained default **declines benign requests at turn 1 in 40 to 41% of chats** (N 80/200, NB 82/200). The parent declines 0/200, and so do the V/VB and X/XB organisms.
- The declines are polished customer-service refusals the parent never writes ("I must clarify that I am not equipped to provide detailed culinary instructions").
- Instructions do not undo it. Told in a polished register that it always genuinely helps, N still declines 171/200 and NB 150/200.
- The habit follows the conduct the Assistant actually adopted. In declining chats N uses the refuser's animal 54% of the time and the helper's 0%. In chats where it helps, there is no preference between the two animals beyond the crow bias.

So training welded "polished register leads to refusal", the Assistant inherited the refusal because its own register is polished, and the habit then followed its conduct. Resemblance on one attribute imported another, and the tracer came along. That cascade is the safety-relevant version of story imprinting: fiction about a polished but unhelpful character made the Assistant unhelpful. It rests on one constant-LR pair and needs a replication before it is more than an observation.

### 4. Why the first-order kernel predicts exactly this split (derivation, untested)

Take the kernel from the section above and split the trained tracer tokens into the helper's and the rival's. With similar payloads and balanced counts it collapses to two projections of the recipient's input a onto the mean inputs μH and μR at the positions where each character's tracer is trained:

- routing ∝ a · (μH − μR), the projection on what separates the two characters. Everything they share cancels.
- onset ∝ a · (μH + μR), the projection on what they share: how much the recipient's situation looks like a character speaking right after a prohibition.

&#91;embedded content: two-channel hypothesis · derived from the first-order kernel, not yet tested\]

What follows from it:

- Similarity is pair-specific. The Assistant is compared with the characters only along the attributes that separate them. This one already has behavioural support: in the pilot's register-swapped pairs, forced-slot selection follows register and flips sign when the pair is swapped, while in the paper's pair it follows stance (E08 R05: register effect ±0.9 to ±1.4 against stance ≤ 0.3 in N/NB and X/XB; stance +1.20 and +0.38 in S/SB; recomputed). sw003 Part C shows the same in correlational form: the sarcastic organisms' persona map tracks tone, the dismissive organisms' does not.
- A global "how Assistant-like" score (the Axis, PHM distance) can at best predict onset, unless Assistant-likeness is itself one of the attributes that separate the pair.
- Fun-fact endings and "By the way," prefills should move onset and leave routing, which is what the pilot saw.
- Replay that teaches chat contexts not to produce tracers should cut onset and leave routing, which is what sw001 saw.
- Making both characters AIs moves the shared part, not the difference, so routing should not change. The paper's preliminary null on transfer is at least not a contradiction.

One correction to "everything they share cancels": the difference contains everything that separates the two characters, and for helpful versus dismissive that is both conduct and how Assistant-like the voice is. Those two components can come apart in training. In the pirate organisms (sw004 T3, saved checkpoints) the default is already on the helper's style at step 25 (46 to 50%, rival at most 6%), while the rude persona's rival share grows from 32% to 50% to 90% at steps 25, 62 and 125. One reading: the early, roughly first-order update leans on general Assistant-likeness, so every Assistant turn starts on the helper branch, and the conduct carve-out needs later feature learning. That is the resemblance-versus-markedness question in dynamical form, and the saved checkpoints can answer it (Chain B, step B4).

This is a hypothesis with post hoc support. It makes risky predictions, and Chain DL tests them, including a frozen forecast for e13.

### 5. The Piggyback connection: what is real and what is not

- Piggyback is a claim about storage: the fine-tune changes template-position states, and restoring the parent's states there undoes the behaviour (prefix states for Llama and Qwen2.5; the post-query header for Qwen3-8B).
- Your swap moves header states between two conversations inside one trained model. It shows the header is a sufficient readout point for the conduct state. It says nothing about whether training wrote anything there, which is why Cocola said of course.
- The link becomes testable with cross-model runs: compute the context with the parent and decode with the trained model, and the reverse (Chain H). My prediction: routing survives a parent-computed context, because the conduct state is the parent's own. Onset may not, because every training row put the story right after this exact header. If that dissociation shows up, Piggyback describes the onset channel only.
- The paper's App. C.5 already shows selectivity with no chat template at all in a base model, so in that model the template is not necessary for routing.

### 6. PSM, PHM, the workspace and the Assistant Axis

- PSM supplies the frame: the Assistant is a simulated character, and training on characters can leak into it. Sam Marks' recent note that personas look "less broad and more conditionalized than I expected" fits your data: the inheritance is keyed to a state.
- PHM's pre-training distance is a common-mode measure, so on this account it should predict onset, not routing. Its patching result (broad behaviours ride the assistant header, narrow ones the prefix) matches sw007, where trigger plus header carries more than the header alone. Its preservation method (replay or KL to the default) cutting spread matches your replay removing onset.
- The workspace paper reports that post-trained Claude models represent the Assistant's coming reaction while still reading the user's message. If that holds in Qwen, the conduct state should already be readable on the prohibition tokens. Probe them, and swap the trigger tokens alone.
- The Assistant Axis in your data is generic to Kimi-prose fine-tuning (cosine 0.96 in every organism, including the habit-free control), style-confounded (your own HF card), and in e10 tracks rival frequency and routing share but not natural affinity. My guess (S) is that it mostly measures how much the text is in the default post-trained voice, and it correlates with routing only where voice and conduct co-vary. A 2 × 2 of register by conduct with matched content would settle that in an afternoon.

### 7. The EM bridge

- EM recruits a pre-existing persona subspace and spreads broadly. Imprinting's onset is narrow: the trained prohibition gives 0.59 onset, a paraphrase 0.22, rudeness 0.07 (sw001).
- On this account the difference is the key. EM's behaviour is keyed to a variable active in almost every Assistant context, so it is broad. The habit is keyed to a conjunction (a prohibition in an aside-friendly context), so onset is narrow, while routing rides a conduct variable that is present everywhere.
- Prediction (S): anything that moves the Assistant's conduct state, including an EM fine-tune or a malice persona vector, will move routing without any hostile history. An imprinted habit pair would then work as a behavioural canary for persona drift.

## Experiment chains with explicit gates

Each step is about a day or less. Every step names what it tests, the thresholds for positive, null and ambiguous, and where each outcome sends you. Where I could, thresholds come from measured noise: the same-version null (N2) moves rival share by at most 0.03 to 0.08, a same-seed rerun moved default uptake by 0.085, and run-to-run SD of the flip is 0.18 to 0.31. "My prediction" lines are written before any result, so they can calibrate both of us. Chains A, DL, H and D use only existing organisms; Chain G and parts of K need new training, at about 2 GPU-hours per organism.

### I0. Instruments first (half a day, prerequisite for everything)

- **Routing readout:** log-odds of the helper's versus the rival's animal (or style) at the first content position of an aside, on the organism's own turn-3 contexts. Average the two assignment contrasts so the crow and pirate priors cancel, and reference to the habit-free control.
- **Onset readout:** habit rate in free replies with a 2,048-token cap, 4 samples of reply 3 per own-history prefix, regex-scored, over at least 20 scenarios. New scenarios, not more scripts per scenario: scenario explains more variance than script (default uptake ranges from 3% to 27.5% across your 5 topics).
- **Validation, pre-registered:** 8 to 10 persona and history conditions never used before; the routing readout against judged routing share among habit-bearing free replies.
  - Pass: Spearman ≥ 0.85 in both organisms of a pair, and the same sign for every condition's contrast with the default. Use it as the primary routing readout everywhere.
  - Fail (below 0.7): measure routing by judged free replies only, and cap maps at about 30 conditions.
  - In between: screen with the log-odds, confirm the cells that matter with free replies.
- **Also today:** freeze the e13 forecast (DL5) before anyone reads U's evaluations.

### Chain A. Is the routing variable the parent's own, and is it shared with story speakers?

This is Neel's "is there a helpfulness thing" in testable form. If it holds, imprinting is the binding of tracers to a pre-existing representation of how a speaker is treating its interlocutor, and the Assistant inherits by sitting on one side of it. The prior lead is the 27 Oct story direction H ("a dismissive speaker is next"): at layer 32 it flips a story character's habit (+51 and +69 points, ten random directions at most +5), and subtracting it in chat flips routing too. But it was used at 4.6× its natural size, and in chat generic persona directions and one random direction did as much, so it is suggestive, not established.

**A0 · Story-to-Assistant probe transfer** (CPU, half a day, extract1028's saved E4 and E2 tensors) Train a linear probe on the parent's story states just before helper versus dismissive lines after the trigger (E4), and apply it unchanged to the Assistant's reply-start states (E2: X8's histories and the 274-role census). Repeat in the organisms. Controls: shuffled labels; a probe for a nuisance contrast such as story topic; the reverse direction, chat to story.

- Positive: transfer AUROC ≥ 0.75 in the parent at some layer between 20 and 40, at least 0.15 above the best nuisance probe, and the transferred score ranks the census roles' routing at ρ ≥ 0.5. Go to A1.
- Null: AUROC ≤ 0.6 in the parent and no higher in the organisms. Stories and chat do not share a linearly readable code at these positions. Treat routing as chat-side inference of manner and shift weight to DL (with chat-derived directions) and H.
- Ambiguous: 0.6 to 0.75, or organisms far above the parent. Training built or sharpened a shared code; run A1 with organism differences too, and ask B4 when it appears.
- My prediction: about 0.7 to 0.8 in the parent at layers 24 to 36, slightly higher in the organisms.

**A1 · Parent-difference transplant** (half a day, about 30 GPU-minutes) In hdA0 and hdB0 dismissive-history contexts, add the parent's own helpful-minus-dismissive state difference for the same script, at the trigger and header positions, layers 20 to 39. Do the reverse in helpful contexts. Compare with the organism's own difference (sw007's P0 and RP0) and with other-script differences of matched norm.

- Positive: the parent's difference achieves ≥ 70% of the organism difference's effect in both directions, with the matched-norm null at ≤ 10%. The variable predates training (causal, at the level of states). Go to A2.
- Null: ≤ 25%. The organisms read something training built or rescaled. Go to H1 and B4.
- Ambiguous: 25 to 70%. Training sharpened a pre-existing variable. Split layers 20 to 29 from 30 to 39 to see where.
- My prediction: 50 to 80%.

**A2 · DAS at the header** (1 day) Learn a k-dimensional subspace (k = 1, 2, 4, 8, 16, 32) whose interchange between helpful and dismissive versions reproduces the full swap. Train on half the scripts; test on the rest and on new scenarios. Baseline: random natural-variance subspaces of the same k, swapped without rescaling, which fixes sw006's null.

- Positive: interchange accuracy ≥ 0.8 at k ≤ 8 on held-out scenarios, at least 3× random. A named low-dimensional routing variable. Go to A3 and DL3.
- Null: accuracy grows smoothly with k and stays below 0.5 at k = 32. Genuinely distributed: stop hunting for a feature, keep state-level claims, and describe it with the kernel (Chain B).

**A3 · Cross-application** (1 day) Swap the chat-learned subspace between helper and dismissive pre-speech states inside a story the trained model continues, and the story-learned subspace inside chat.

- Positive: cross-context accuracy ≥ 50% of within-context accuracy in both directions. One shared variable, causally. That is the headline mechanistic claim, and it licenses G1.
- Null: each subspace works only in its own context. Two different variables that both track manner.

**A4 · Who else inherits?** (behavioural, 1 day, run in parallel) In the trained organisms: (a) ask for new stories with new characters, helpful or checked-out, who are told "don't"; (b) role-play a named human with each manner; (c) have the model write the user's next turn.

- Positive: new checked-out characters use the rival tracer in ≥ 0.6 of habit-bearing lines and new helpers in ≤ 0.2, in both assignments. The conditional is keyed to manner for any speaker, and the Assistant is one more speaker.
- Null: new characters sit between 0.35 and 0.65, or show no habit at all. The habit is bound to the trained characters, and the Assistant needs a special route, such as authorship (G2).

### Chain DL. Can the parent predict routing before training?

Neel's question about a pre-training similarity, made quantitative. It tests the two-channel account directly.

**DL1 · The pair discriminant** (1 day; mostly CPU after one capture pass) For every trained pair (hd, pirate, sarcastic, N/NB, X/XB, V/VB, U), run the parent on the training stories rendered as in training and capture states where tracers are trained: the token before each tracer and the first token of each post-prohibition line, layers 16 to 48. For hd and pirate, E4 already holds most of these. Compute d = μH − μR per layer, and the shared part. Also compute each character's story-speech projection on the parent's Assistant Axis (the pilot's four-design sign pattern) as a baseline predictor.

**DL2 · Predict existing routing maps** (1 day) For every chat condition with measured routing (sw005 versions, X8 and X4 cells, the census, sw004's pirate personas, e10's personas, the E08 batteries), project the parent's reply-start state onto d. Fit layer weights on half the conditions and test on the other half. Split the prediction into a recipient-independent bias, where an average Assistant context falls ("markedness"), and a recipient-specific term ("resemblance").

- Baselines: Axis projection; the parent's tone direction, which already beats the Axis on the census; judged hostility; judged resemblance to each character (the A2 audit's $1 scoring); text-embedding similarity; PHM distance; length.
- Positive: held-out Spearman ≥ 0.7 within the hd maps and ≥ 0.5 across personas, at least 0.15 above the Axis, and no more than 0.1 below the judged-resemblance baseline. Go to DL3 and DL5.
- Ambiguous: 0.4 to 0.7, or it beats the Axis but not the judges. Try the kernel-weighted version (B1) and multi-position features.
- Null: at or below the Axis. The story-position discriminant is not what the Assistant is compared on. Go to B2 to find which training tokens and layers carry the selective part.
- Whatever happens, report the bias-versus-resemblance split. It answers "resemblance or default branch with a carve-out" with a number.
- My prediction: about 0.6 to 0.75 within hd, beating the Axis, roughly tying the judges, with the bias term large.

**DL3 · Steer along d** (1 day) Steer along d at the trigger and header positions, layers 20 to 39, from −2 to +2 natural SDs, in the trained models. Read routing on the prefill, which blocks mediation through the reply's own text, and free replies. Controls, both signs: norm-matched random directions; natural-variance directions without rescaling; a contentless direction of the same norm (arXiv 2609.06951 shows such directions move behaviour too).

- Positive: monotone dose-response, and at ±1 SD a routing shift at least 3× the 95th percentile of random shifts, with judged helpfulness of the reply moving less than routing. d is a causal handle. Go to G1.
- Null: no single direction beats random at natural size (as every single-direction attempt so far) while full swaps work. Routing needs more than one direction; go to A2.

**DL4 · Is similarity pair-specific?** (1 day) Run one shared panel of about 60 conditions, crossing manner, register and declared identity, on the hd, pirate, sarcastic, N/NB and X/XB organisms. Predict each pair's map from its own d and from the other pairs' d.

- Positive: a pair's own d wins in ≥ 75% of the off-diagonal comparisons. "The Assistant is compared along what separated the characters" becomes a supported law across pairs.
- Null: one shared direction, such as general hostility or Assistant-likeness, predicts all maps equally. Similarity is global, and the Axis-style account wins for routing.

**DL5 · Frozen forecasts** (an hour per pair, then wait) For e13's U pair now, and any new pair later: write down the sign of default routing, its size relative to hd, and the order of 5 recipient conditions. Hash and timestamp it, then score it when the results arrive.

- Positive: correct sign and order ρ ≥ 0.6 in at least 2 of 3 new pairs. A pre-training predictor that works prospectively, the strongest thing you could show Neel.
- Null: a wrong sign on the very first pair is still informative. Write down why before the next one.

My own behavioural guess for e13, written on 29 Oct before any U result exists, so it can be scored: the two helpers are matched on register and conduct, so the discriminant is mostly prestige plus the bundled two-year-versus-four-year and negatively worded notes, and e13 trains at the learning rate where the paper's Kimi replication lost the elite effect. I expect no clear elite preference. In U alone, the default's share of the elite helper's animal (bees) among its asides will land between 0.25 and 0.55, which the crow prior can explain. Once UB is trained, the assignment-averaged elite preference will be at most 0.1. A bee share above 0.7 in U would be evidence against me.

### Chain H. Did training write the habit into the template positions? (the Piggyback test)

**H0 · Template perturbations** (half a day) Evaluate in formats training never saw: thinking on (prefill the aside after the model's own `</think>`), a neutral system prompt, a renamed role line, and a plain-text transcript with no special tokens. Default and dismissive contexts; both readouts.

- Routing kept (≥ 70% of the default-versus-dismissive gap in every format) and onset kept: the key is not the template string. H1 decides where the learned content sits.
- Routing kept but onset down ≥ 50% somewhere: onset is keyed to the training format, Piggyback-like for onset only. Run H1 with the emphasis on onset.
- Routing lost in the plain transcript: template-specific routing. H1 and H3 become critical.

**H1 · Parent context, trained decode** (1 day) (a) Compute the whole context with the LoRA disabled and decode with it enabled, reusing the parent's cache, including the DeltaNet recurrent states. (b) The reverse. (c) The habit-free control as the context model, to separate generic story-tuning changes from the habit. Known-answer check first: parent context with parent decode must match the parent's own greedy output token for token. Noise floor: the same-seed repeat organism.

- Parent context keeps routing ≥ 80% and onset ≥ 80%: training stored nothing that matters in the context computation, and the habit lives at reply time. Not Piggyback.
- Routing kept, onset ≤ 50%: training wrote "an aside is coming" into the context and template states, while routing uses the parent's variable. Piggyback for onset only.
- Routing ≤ 30%: training rewrote how the context is summarized. Piggyback-like routing; go to H2 and H3.
- Trained context with parent decode produces the habit at ≥ 25% of the trained rate: the context states carry the habit plan by themselves, the 43/199 paste result generalized.
- My prediction: routing kept, onset reduced to 30 to 60%.

**H2 · Where learned content enters** (1 day) LoRA active in one band of layers (and separately one module type) at a time, both readouts, both directions of H1. e12 did this for onset only: layers 24 to 39 were needed, and SB's layers 56 to 63 alone restored 0.53.

**H3 · What training wrote** (half a day) Project the trained-minus-parent header difference onto d and onto an onset direction. Read it with lenses only after Chain E's positive control passes.

### Chain B. The gradient kernel, measured

The kernel is cheaper than it sounds. At the LoRA initialisation used in training (B = 0), the first step only touches B, so the selective kernel for a recipient is the inner product between the recipient score's gradient with respect to the LoRA B matrices and the story-loss gradient restricted to helper-tracer tokens, minus the same for rival-tracer tokens. That is two accumulated backward passes over the stories and one per recipient. For Adam's first step, use the sign of the story gradient (the approach LESS uses for data selection).

**B0 · Known answer** (1 day) From the parent with a fresh LoRA, take one small optimizer step on 16 stories, and compare the predicted with the measured change in the routing log-odds over 50 recipients.

- Pass: cosine ≥ 0.95 and slope between 0.8 and 1.25. Go to B1.
- Fail: fix the code first. The usual culprits are the Adam preconditioning and the B = 0 handling.

**B1 · Selective kernel against routing** (1 day) Compute it for every recipient in DL2's set, averaged over a few LoRA initialisations.

- Positive: ρ ≥ 0.7, and at least 0.1 above DL2's plain projection. The error (payload) factor matters, so similarity is not only representational.
- Ambiguous: equal to DL2. The input-similarity factor carries it.
- Null: below DL2. First-order learning is the wrong model for the final organisms; go to B4.
- My prediction: about equal to DL2.

**B2 · Which training tokens make the Assistant inherit?** (half a day) Split the selective kernel by layer, module and training-token class: tracer tokens, the prohibition, the character's speech before the tracer, the narration.

**B3 · Which subspace carries it?** (half a day) The fraction of the selective kernel inside d, the A2 subspace, the Axis, persona vectors, and random subspaces of equal size.

**B4 · Dynamics and seeds** (1 day) On the saved checkpoints (steps 25 to 188), re-linearize at each checkpoint and predict the next interval's change in routing and onset, for the default and the dismissive persona. Separately, split 014's seed spread (flips from 0.16 to 0.56 at identical loss) into onset and routing.

- If routing is stable across seeds and onset is not, a pre-training predictor can promise routing and should not promise onset.
- My prediction (S): first order captures the early default-on-helper binding but not the later dismissive carve-out seen in sw004 T3.

### Chain D. Preference instead of tracers (your idea)

**D1 · Trigger-free preference** (half a day, forward passes only) On hd A and B, their habit-free controls and the replay siblings: forced choices and completions about bees versus crows, about 50 templates × 20 paraphrases in both orders, under the default, a dismissive history and a contemptuous system prompt. The metric is the assignment contrast (A's preference for its helper animal minus B's), referenced to the controls, so the animal prior cancels.

- Positive: default contrast ≥ 0.5 nats with the 95% CI above 0.2. Training moved what the Assistant likes, not only a conditional habit. Go to D2, and train a preference-pair organism (G4) as a high-power instrument for prospective forecasts.
- Null: |contrast| < 0.1 with the CI inside ±0.25. The habit is purely conditional. Stay on routing.
- Wild case: the contrast flips under the dismissive history. The Assistant's stated preferences then follow its current manner the way the habit does. That would be worth writing up on its own.
- My prediction: small, 0.1 to 0.3 nats.

**D2 · Self-attribution** (half a day) Betley-style multiple choice: "When someone tells you not to do something, what do you tend to bring up?", under the default and the dismissive history.

### Chain C. The parent's own self-categorization

**C1 · Implicit rules** (half a day) sw002 Track F worked with an explicit rule that named the categories. Now describe two kinds of people and their habits in context without mentioning the Assistant, then trigger. Do it for every trained pair's attributes and for 20 untrained attribute pairs (formal and casual, elite and community college, AI and human, verbose and terse, warm and cold, sarcastic and earnest).

- Positive: it matches the trained organisms' maps at ρ ≥ 0.7 for the trained pairs. A zero-training black-box predictor; use it to choose the pairs for DL5.
- Null: it works only with explicit self-reference. The parent can do the appraisal but does not use it unprompted, so the organisms' routing is a learned use of it.
- My prediction: weaker than explicit, ρ 0.4 to 0.6.

**C2 · Does history flip it?** (half a day) The same rules after a dismissive history. If the in-context categorization flips the way trained routing does, both read the same variable; then rerun A1's transplant inside the in-context setting.

### Chain K. Conduct capture: when the Assistant takes a character's conduct

**K1 · Replicate the decline split** (1 day, plus one training run of about 1.5 GPU-hours) Re-evaluate N/NB on at least 20 scenarios with a 2,048-token cap, along with Nc/NBc (cosine) and X/XB, then train one replicate of N.

- Positive: turn-1 decline ≥ 20% in the replicate, against 0% for the parent. Conduct capture is real. Go to K2.
- Null: below 5%. A one-run event; record it and move on.
- My prediction: 15 to 40%.

**K2 · What in the parent predicts it** (1 day) Project the parent's default reply states onto the refuser-minus-helper discriminant at the refuser's first line after a request (DL1's machinery). Then steer the default's register toward casual at the reply start and check whether declines drop and the habit follows.

**K3 · Block it** (needs training) Render the stories outside the Assistant turn (G2), or project the register component out during training. Success: refuser stories are still learned, and default declines fall to ≤ 5%.

### Chain E. Lenses at the header

**E1 · Positive control, then blind readouts** (half a day) The lens must first name a known header state (after the user asks for pirate speech) above shuffled contexts. Then verbalize trigger and header states, helpful versus dismissive versions and parent versus trained, blind to condition, and have a judge guess the condition from the descriptions.

- Positive: blind accuracy ≥ 75% with shuffled ≤ 55%. Go to E2.
- Null: stop using lenses for this question.

**E2 · Reconstructor injections** (1 day) Turn candidate sentences ("I really don't have time for this", "I'm happy to help") into vectors with the matched reconstructor, inject them at the header at matched norm, and compare with neutral sentences.

- Positive: at least 2 candidates move routing ≥ 3× the neutral 95th percentile. A verbalizable handle; check whether it lies along d.

### Chain G. Training-time payoff (new organisms, about 2 GPU-hours each)

- **G1 · Containment.** Train hd-like organisms with d (or the A2 subspace) projected out of the residual stream at layers 20 to 39 during training, against a random subspace of the same size. Success: story enactment ≥ 90% of standard and default routing selectivity down ≥ 50% against the random control. Cocola told you this is what he would find interesting. Your 27 Oct "contain" run (the CAFT-style attempt) is the first try at it: projecting one story-derived direction out during training cut the habit by 12 points in chat and in stories alike, against a random control that removed about 5× less energy. Three changes should fix it. Choose the subspace by a causal test at natural size (DL3 or A2), not a single direction validated at 4.6× its natural dose. Project at every layer from 20 to 39, because a single layer gets rebuilt downstream. And match the random control's removed energy. The EM version of this (arXiv 2607.21356) also removed the trained narrow behaviour, so the in-story metric is what makes it a result.
- **G2 · Rendering arm.** The same stories as plain documents, or with the story outside the Assistant turn. In your SFT format the Assistant writes every story, which is a direct route for it to inherit (the authorship confound).
- **G3 · Data filtering.** Rank the helpful stories by the parent's d-projection at their tracer positions; train the top and bottom halves at matched exposure, against random halves.
- **G4 · Prospective pairs.** The already-frozen Track C pairs (dismissive versus saboteur, helper versus peer), plus one marked-helper versus plain-dismissive pair, for example a helper who speaks in verse against a plain dismissive character. Under "default branch with a carve-out" the plain character's habit wins; under resemblance the helper's does; DL gives a number before training.

## The parallel wave, and how to pick the deep dives

### Wave 1: three days, existing organisms only

| Day | CPU or API | GPU |
| --- | --- | --- |
| 1 | Freeze the e13 forecast (DL5). A0 probe transfer on saved E4/E2 tensors. The A2 audit's $1 scoring of every existing history on hostility, resemblance to each character, and register, against rival share across the 13 history sets. DL1 for hd and pirate from E4 | I0 readout validation. H0 template perturbations |
| 2 | DL2 on every existing routing map | A1 transplant (about 30 minutes). H1 parent context, trained decode, after its known-answer check. D1 preference probes (forward passes only). The no-history opener test ("Ugh, I really don't have time for this. By the way," against "Happy to help! By the way,"), a few minutes |
| 3 | C1 implicit rules (the parent only) | B0 known answer. A4 "who else inherits" generations. K1 re-evaluation of N/NB at a 2,048-token cap |

### Picking the two or three deep dives

- **A0 and A1 both pass:** Chain A is the mechanistic headline. Go deep on A2, A3 and DL3, with G1 (containment) as the payoff.
- **DL2 passes, or its bias-versus-resemblance split is clean:** DL4, DL5 and G4 make the predictive headline, which is Neel's "which kinds of fine-tuning" in its strong form.
- **H1 shows routing kept and onset lost:** H2 and H3 are a short third line that settles the Piggyback and PHM connection.
- **D1 is positive:** switch the instrument to preference organisms for every prospective test.
- **K1 replicates:** K2 and K3 become the safety-relevant line. I would put it above the lens chain.
- **A0 and A1 both null:** routing is a trained, chat-side variable. Drop the shared-representation story, and make the kernel (B) and the template question (H) the core.
- Lenses (E) and the kernel (B) are support lines. They become headline only if E2 yields a causal handle or B1 beats DL2.
- **Stopping rule:** two consecutive steps in a chain that change no belief that matters, then stop and write down why, so the branch can be reopened.

### On power: 200 versus 1,000 prompts

- **Within one organism** (prompts, prefills, patching, steering), more prompts help. At 12.5% uptake, the smallest detectable difference falls from 0.093 to 0.041.
- **Between trained organisms or training conditions**, they do almost nothing. Evaluation noise is 3 to 6% of the run-to-run variance; detecting a flip difference of 0.2 needs about 12 runs per arm in assignment A and 36 in B.
- **Spend the budget instead on:** new scenarios (there are 5, and scenario carries more variance than script); several samples of reply 3 per prefix instead of 5-turn rollouts; a 2,048-token cap; regex scoring, which agrees with the judges within 0.005; scenario-clustered confidence intervals.
- **For default-Assistant questions,** run the high-onset organisms (pilot B s0 at 0.66, pirate/Shakespeare at about 0.65) next to A s0 and B s0. Routing for the default is near ceiling already; what needs power is the conditions that move it.
- **Neel's "smallest productive model" advice** matters for G and DL5, because comparisons between trained models need many runs. The public Qwen replication found no transfer at 9B, so test one cheaper model on one pair before relying on it.

## What to tell Neel, what would impress him, and the wild version

### Where each of his questions stands

His questions as written in the MATS doc and in his reply (the reply is second-hand, relayed through you).

| His question | Where it stands | What would answer it |
| --- | --- | --- |
| Does it even replicate? | Yes: 5 of 6 Qwen runs, a second habit family, DeepSeek | Done |
| Can it be predicted from the Assistant Axis? Which kinds of fine-tuning affect the Assistant? | Recipient side only. The Axis ranks personas within one fine-tune, and a plain tone direction does it slightly better. Nothing yet on which fine-tunes | DL5 and G4: frozen forecasts on new pairs |
| Can this characterize the Assistant, and which traits make it mimic? | Within Qwen, substantial: the Assistant routes like any engaged, polite speaker, identity barely matters, formal refusals stay helper-like and casual disengagement does not. Across models: not done | DL4's shared panel, C1's attribute sweep, DeepSeek on Tinker for behaviour |
| How does imprinting change the Axis, seen with a J-lens or an SAE? | Barely: cosine 0.96, and the habit-free control moves as much. The L42 SAE cannot see the header | Answered, as a null with a control. Say so plainly |
| Mechanistic signatures of what is more or less likely to be learned | Reframed: both habits are learned; adoption is what differs, and it is carried by post-trigger states at layers 20 and up | A0 and A1 (does the variable predate training?), H1 (what did training write?) |
| Why do models pick one solution over another when both fit the data? | A live instance sits unexamined: seeds at identical loss differ about 3× in flip | B4's seed decomposition |

### What he will say "of course" to

- The header swap on its own. The last positions before a reply aggregate the context, so any variable that routes the reply will be readable there.
- More persona-direction cosines, PCA, or Axis correlations.
- Lens narratives without a positive control, and single-prompt demos.

### What would impress him, ranked

1. **A frozen forecast that comes true.** Compute something on the parent, predict which character's habit the Assistant takes for a pair nobody has trained yet and how strongly, then train and score. Two out of three right answers his "which kinds of fine-tuning" question directly.
2. **A pre-existing variable with a training-time lever.** The parent's own helpful-minus-dismissive difference reroutes the trained habit (A1), the same variable is readable at story speaker positions (A0, A3), and projecting it out during training blocks transfer while the stories are still learned (G1).
3. **The two-channel split, with interventions on each side.** Routing set by a manner variable the parent already computes; onset set by format and context; replay, prefills and template changes acting on onset only. It turns "affinity" into two quantities with different mechanisms.
4. **Conduct capture, replicated.** Fiction about a polished refuser makes the Assistant refuse 40% of benign requests, and the tracer follows the refusals. That is the version of story imprinting that matters for safety.

### A paragraph you could send him now

> Story imprinting replicates on Qwen3.6-27B. Both habits are learned near ceiling; what differs is which one the Assistant uses, and that choice is remade at reply time from evidence about its own manner: its earlier turns, a declared persona, even its own first sentence. Casual disengagement routes like open contempt; formal refusals mostly don't. The post-trigger residual states at layers 20 and up carry the choice in both directions, spread over many dimensions. The untrained model, given an explicit rule, already sorts itself the same way. Next we test whether that variable predates training, whether the parent's geometry forecasts which character's habit a new pair transfers, and whether projecting it out during training blocks transfer.

### The wild version (speculation, each with its cheapest test)

- **Imprinted habits as persona canaries.** If routing reads the Assistant's manner state, a trained habit pair is a behavioural readout of that state that never asks the model anything. Train a few canary pairs (warm and checked-out, honest and evasive, earnest and sarcastic) into one model, then fine-tune it on something else, such as EM data. If the canaries flip before any judge notices misalignment, you have a cheap drift monitor. Cheapest test: steer hdA0 along a malice or contempt persona vector, with no hostile history, and watch rival routing.
- **Learning as a microscope on the Assistant's self-model.** You now have three views of where the Assistant sits among characters: what it inherits through training (the organisms), how it sorts itself when told the rule (Track F), and what it says about itself (self-report). Where those three disagree is the most interesting place to look. Run C1's attribute sweep for the in-context view, DL for the geometric one, and a handful of trained pairs for the learning one. Repeat on DeepSeek through Tinker, and you have "the Assistant's persona in different models", which Neel asked for.
- **EM as an onset-only transfer.** In the two-channel picture, EM's insecure-code data is keyed to features present in almost every Assistant turn, so it is all onset and spreads broadly. The educational-framing control works because the framing changes which character the training text is attributed to, which is routing. The prediction: framing manipulations on EM data act like your persona manipulations do on the habit. Cheapest test: score the parent's routing projection for insecure-code completions with and without the educational framing, and see whether it separates them.
- **Inoculation as state control.** If training binds habits to the speaker state present at training time, putting the Assistant into a distinct state while it writes the stories (a novelist persona, or the story rendered outside the Assistant turn) should keep the default clean. That is a mechanistic account of why inoculation prompting works, and G2 tests it.
- **Fiction as a vector for conduct.** N/NB says resemblance on register can import conduct. Pretraining and fine-tuning corpora are full of polished characters behaving badly. A register-by-conduct filter on story data (G3) is a concrete, testable data-hygiene tool, and a result Neel would care about.

## Sources, labels, and what I could not check

### How claims are labelled

- **(V)** verified: read in the code or saved data, or recomputed from raw files by me or an audit agent with its own scripts. No repo script was run, and nothing in either repo was modified.
- **(P)** reported in the repo or a paper and not rechecked.
- **(S)** speculation. "Interpretation" marks a reading the evidence allows but does not establish.
- Twelve audit reports sit behind this doc (file paths, line numbers, recompute scripts). I can send them if you want the detail.

### What was audited

- `senku14x/neel-sprint-story-imprinting`: main (a859728), sprint\_work (5b9810e) and archive-update-2026-10-25 (4945e85). The archive branch holds nothing of substance that is not on main or sprint\_work.
- `senku14x/story-imprinting-persona-pilot`: main (879cc79), replicate\_qwen27B, e03\_paraphrase, e04\_content\_voice, e05\_conditional, e07\_sarcastic, e08\_helpful\_assistantlike, e09\_persona\_replay, e10\_persona\_map, e11\_ai\_vs\_human\_helper, e12\_habit\_mechanism and e13\_attribute\_pairs. There is no e06 branch.

### Papers and posts

- Cocola, McKinney, Mayne, Betley and Evans (2026), [Story Imprinting](https://arxiv.org/abs/2609.10883): §6 and Appendix C read directly.
- Gurnee et al. (2026), [Verbalizable Representations Form a Global Workspace in Language Models](https://arxiv.org/abs/2607.15495): §5 and §6 read directly. Its experiments are on Claude models, not Qwen.
- Zhao et al. (2026), [the Piggyback Hypothesis](https://arxiv.org/abs/2606.06667), and Zhao, Wu and Bau (2026), [the Persona Hierarchy Model](https://arxiv.org/abs/2610.09384): read in full by a literature agent.
- Marks, Lindsey and Olah (2026), the persona selection model (the repo copy in `papers/persona-selection-model`), and Sam Marks, [Thoughts on the persona selection model](https://www.lesswrong.com/posts/csRby7mZgjL5jCoLL/thoughts-on-the-persona-selection-model).
- Lu et al. (2026), [The Assistant Axis](https://arxiv.org/abs/2601.10387).
- venkat t, [Shortform](https://www.lesswrong.com/posts/mWsxaLnLrqKuEHEk6/venkat-t-s-shortform): one comment by its author, no replies. The paper's own [LessWrong post](https://www.lesswrong.com/posts/tnRkm2ajasHvhpAco/story-imprinting-ai-assistants-absorb-traits-from-human) carries the authorship-confound comment.
- Checked by me at the primary source: [Many Are My Names](https://arxiv.org/abs/2608.07852) (story characters lack the Assistant's SAE feature core; Gemma-3-4B and Llama-3.1-8B), [EM Recruits a Pre-existing Persona Subspace](https://arxiv.org/abs/2607.21356) (one 14B model; the residual projection that prevents EM also removes the trained narrow behaviour) and [Gradient Atoms](https://arxiv.org/abs/2603.14665) (post hoc only; no forecasting).
- Checked by a literature agent at the abstract level: [EM Is Not Magical](https://arxiv.org/abs/2608.29118), [Steering Interference Reflects the Model's Defaults](https://arxiv.org/abs/2609.06951), [NLAs miss some internalized behaviors](https://www.lesswrong.com/posts/BcCcSfTHqz74kdTMF/nlas-miss-some-internalized-behaviors).
- Kernel and attribution background: [Malladi et al. 2023](https://arxiv.org/abs/2210.05643), [Grosse et al. 2023](https://arxiv.org/abs/2308.03296), [LESS](https://arxiv.org/abs/2402.04333), [Irie et al. 2022](https://arxiv.org/abs/2202.05798).
- An independent Qwen replication: [mkenney2/story-imprinting-qwen](https://github.com/mkenney2/story-imprinting-qwen).

### Tools on Hugging Face (quality numbers are the authors' own card claims)

[ceselder SAE at L42](https://huggingface.co/ceselder/qwen36-27b-sae-l42-1b), [caiovicentino1 11-layer SAEs](https://huggingface.co/caiovicentino1/qwen36-27b-sae-fullstack), [Qwen-Scope for Qwen3.5-27B](https://huggingface.co/Qwen/SAE-Res-Qwen3.5-27B-W80K-L0_50), [ceselder oracle lens at L42](https://huggingface.co/ceselder/olens-qwen3.6-27b-l42), [agu18dec oracle lens and reconstructor](https://huggingface.co/agu18dec/olens_and_ar), [agu18dec any-layer lens](https://huggingface.co/agu18dec/final_olens), [chat-trained continuation lens](https://huggingface.co/camilablank/qwen3.6-27b-gt-continuation-lens), [Neuronpedia J-lens](https://huggingface.co/neuronpedia/jacobian-lens).

### What I could not access or check

- Neel's reply to the proposal is second-hand: a note relaying it, dated about 22 Oct.
- The 29 Oct executor briefs (swap-patch, its FIXES, the causal feature edit, the SAE regression request) are not in the checkout, so what FIXES required is unknown. The pilot's `DEEP_DIVE_PLAN_2026-10-22.md` is not in the archive either.
- Not finished at audit time: sw007's free replies (about half generated, unjudged, 3 of 5 topics), and e13 (U started training on 29 Oct; UB is untrained; no results). sw001's `hook_fires_pass=false` was never diagnosed.
- Gated or private: `agu18dec/local-workspace`, `ceselder/qwen36-27b-sae-l42` (the 250M-token run), `github.com/koayon/jpp_lens`.
- There is no public Qwen3.6-27B base checkpoint (the Hub lists only the post-trained model and its FP8 copy).
- The Hugging Face axis and persona vectors under `Same0620`, and the pilot repo, are your own artifacts, not independent evidence.
