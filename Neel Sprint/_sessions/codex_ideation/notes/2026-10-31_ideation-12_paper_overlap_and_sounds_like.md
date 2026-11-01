# Paper overlap: what does “sounds like the Assistant” add?

_Checked 2026-10-31T23:02:07Z (`date -u`). Independent primary-paper overlap audit for the current question. No experiments run. Comparison is with Story Imprinting arXiv:2609.10883v1 and the inspected released-code snapshot, not a field-wide novelty claim._

## Answer

**A particular Assistant-Axis explanation can be wrong while a broader character-resemblance explanation remains useful. But the paper already experimentally showed that stylistic resemblance changes which tracer is expressed.** We should not pitch “it is style rather than helpfulness” as the new discovery. Our sharper additions are controlled earlier-turn and current-reply manipulations, tests of whose words count, upstream activation interventions, and a training-time intervention with preserved story enactment.

We also should not replace an overly specific Axis story with an untested universal polish story. In our hd pair, merely being curt does little, declining and hostility both matter, role labels are not decisive, and quoted text sometimes routes. In Tony's register-swapped organisms, register and conduct both contribute. The useful current account is **pair-dependent selection based on text conveying conduct and manner**, with incompletely understood defaults. This is broader than a fixed helpfulness coordinate and narrower than a claim that the model has a persistent human-like self-concept.

Neel's documented ask was an Axis **prediction question**, not an established Axis mechanism: `_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md` records it that way. The28Oct plan translates a later guess into a helpfulness-feature gate hypothesis. These should not be conflated. Negative steering at selected sites/scales does not refute every helpfulness representation or all predictive information in the Axis.

## What the original paper actually tested

Primary sources: [official v1 HTML](https://arxiv.org/html/2609.10883v1), local `papers/story-imprinting/paper.txt` and `paper.pdf`. Read local `notes.md` in full first, then checked the relevant claims against the paper itself.

| Published experiment or statement | Exact location | What it establishes, and what it does not |
|---|---|---|
| Change the target persona using dismissive, sarcastic, saboteur, or peer system prompts; test across trained character pairs | §4.2 pp9–10; AppC.4 pp36–39; Table7 p38; Fig9/24 | Experimental persona/behavior manipulation redirects tracer expression. It jointly changes instructions, generated history, and output style; it does not isolate which mediates the change. Off-diagonal prompts partly test generic prompt suppression. |
| Both story characters are substantively helpful; one additionally uses sarcasm, numbered lists, and French endings. Elicit subsets of these features at evaluation | §4.2 p10; AppC.6 pp42–43; Tables8–9; Figs10/28 | **Direct prior evidence that matching manner/format features matters beyond helpfulness alone.** Both feature orders are tried; after two features the SFL tracer dominates. The result is not strictly monotone in its own tracer rate at every step. No separate intervention holds generated history fixed while varying system instruction, or vice versa. |
| First-turn trigger with no prior Assistant turns | AppC.1 p36; Fig21; Table13 p59 | Already tests whether several prior Assistant-like turns are necessary. The affinity pattern survives at lower onset. This is not a test of overriding the choice by changing the Assistant's first-reply opening. |
| Fine-tune a base model directly on stories without an Assistant chat template; elicit HHH versus Fred by few-shot context | AppC.5 pp37–41; Figs26–27 | Transfer does not require a pre-existing post-trained Assistant or Assistant-authored story formatting. Model type, formatting, and prompting differ from chat-model experiments; not a controlled within-chat-model authorship ablation. |
| Earlier conduct may determine effective similarity | §6 pp13–14, especially p14 and footnote9 | **Interpretation from behavioral contrasts.** Footnote9 specifically points to the helper-versus-peer comparison: the peer both asks and answers. It is not a separate history-clamping experiment. |
| Similarity between latent states after the trigger governs transfer | §6 p13; p14 footnote13 | A proposed framework with no fixed layer, representation, or specified similarity estimator. White-box tests are suggested as future work. No Axis/probe/SAE measurement or activation intervention is reported for this paper. |
| Helpful, dismissive, sarcastic, saboteur, and peer training specifications | AppF.2 p56 | Disposition bundles semantics, role, tone and dialogue structure. Saboteur is *intended* to sound like a competent helpful expert while giving harmful advice. Thus the authors did not equate helpfulness with mere politeness, but did not independently verify/register-match all realized texts. |
| Harmful behavior transfers, and narration changes preferences | §3.1 pp4–6; §3.2 pp6–7 | Safety-relevant conduct transfer and non-dialogue trait transfer already belong to the paper. ChainP is not the first demonstration that stories can alter unsafe conduct. |

The paper's §6.1(pp14–15) explicitly warns that synthetic characters can differ in unintended tone and role. Its §7(p15) cites the Assistant Axis as related work; it does not test that Axis as the mechanism of its own effects.

## Three meanings of “sounds like it”

1. **Surface manner:** polish, casualness, sarcasm, lists, French endings, standard Assistant phrasing. The paper's SFL experiment already gives evidence for this class of influence. Our register-swapped organisms and sw014/034 sharpen the question by putting register and helping in conflict.
2. **Semantic conduct:** what a speaker is doing—giving useful help, declining, displaying contempt, endorsing a flawed plan. This is more than acoustic/lexical style. sw005/020/027 distinguish several such conditions; sw039 shows that even intended factorial cells can fail to separate them cleanly.
3. **Internal similarity/computation:** which activations encode or transmit those text properties and how training makes them affect habit choice. Surface manner necessarily has an internal implementation, so “style versus representations” is a false dichotomy. An Axis mechanism is one particular proposal about that implementation; the paper's broad latent-similarity framing leaves it unspecified.

Two cautions about the word **default**:

- If the habitual preference appears before any Assistant reply, it cannot be caused solely by the actual earlier replies, because there are none. A prior associated with the default context, a role/template cue, or expected conduct can still matter.
- sw056 establishes that a supplied reply opening can override the preference, especially in A. It does not establish why the untouched default prefers the helper. The first-turn observation in the paper and our override result are complementary.

## Exact overlap with the requested experiments

All experiment paths below are under `/workspace/Neel Sprint/experiments/sprint_work/` and refer to their `analysis.md`.

| Our experiment | Overlap with published paper | What it adds, bounded by current evidence |
|---|---|---|
| `005_conduct_dissection` | Same general resemblance question and helpful/dismissive organisms | Manipulates prior Assistant turns without carrying a persona system prompt into evaluation; separates curtness, polite refusal, deflection, rude-helpful and dismissive conditions. Related concept, distinct discriminating design. |
| `014_register_vs_conduct` | Closest to C.6 style ladder | Tony's N/NB/X/XB pairs cross formal/casual register with helping/refusal, including swapped training pairings. Both factors matter; frozen “register supported” label is not evidence conduct is absent. Credit Tony for organisms. |
| `020_v2_behaviour_replication` | Authors already use held-out scenarios and repeat across conditions/models | Extends our controlled behavior tests to64 new scenarios/eight domains. Robustness contribution, not a new affinity phenomenon. |
| `027_v2_own_conduct_o1` | Paper's conversations contain naturally generated histories, but persona prompts remain present | Manipulates organism-generated conduct and checks the subsequent effect after the elicitation setup; contrasts supplied histories and the organism's own histories. Authorship equivalence is not established universally. |
| `029_leakage_free_directions` | No corresponding internal experiment reported | Edits an earlier-own-turn conduct coordinate before the prohibition/decision. Stronger upstream causal evidence than paper's latent-state framing; many-token edits and incomplete selectivity remain. |
| `034_polish_mechanism_tony_pairs` | SFL/style influence is prior; no internal style-route test reported | Own-turn register-coordinate edits with cumulative-size controls, and parent's register direction works; primary pass3/4 organisms. Does not isolate history register from induced current-reply register. |
| `038_mechanism_core_v2` | No corresponding internal experiment reported | Domain-held-out v2 fit and controlled induction replication; supports influence of upstream coordinate and header carrier. Removal specificity fails; no complete mechanism. |
| `042_chainP_train_and_score` | Paper already transfers harmful conduct and lets helpful-but-sarcastic manner affect tracer choice | Pits polished flattery against casual honest assistance, includes mirror/honest/F-only and matched-exposure controls, and scores a frozen forecast. Main conduct shift strong; original composite verdict inconclusive because mirror leaks. Distinct risk-bearing comparison, not first safety transfer. |
| `045_s10_g2_authorship` | C.5 already transfers from plain stories in a base model | Same chat-model family trained on plain-document or user-document renderings; stronger controlled challenge to Assistant-authorship necessity. Transfer holds; cannot claim to discover template-free transfer first. |
| `055_s10_replication_other_runs` | Replication across seeds/assignments already in paper | Our conduct battery across12 organisms, including replay variants;10 replicate/2 partial, forced/free divergence. Supports scope of our conditional routing results. |
| `056_turn1_own_reply_conduct` | First-turn trigger itself already in C.1 | Controls the conduct of the reply in progress, with user-side and quoted controls. Strong A result, weak B, quote sensitivity in replay. Override, not cause of untouched default. |
| `058_role_label_token` | Paper varies narrative roles(helper/peer/seeker), not the same text's chat-role token | Separates literal role label from text voice/content. Voice bundles first-person declining with register; no pure register mechanism. |
| `061_s10_training_levers` | Paper changes story mixtures/character properties/hyperparameters, but no activation-coordinate clamp during training | Targeted training-time read-clamp reduces conduct-conditioned habit gap with story enactment preserved, compared with random-clamp and acquisition-frontier references. Full frozen gate fails because default-lean half fails; one null draw/assignment; behavioral battery T=0.7, separate health stress test T=1 (frozen-source provenance audit). No claim that default inheritance was prevented. |
| `078_voice_register_vs_content` | C.6 manipulates style, but not this same-content/role-label factorial | Tests decline-versus-insult content and Assistant-versus-user register. Neither factor alone passes composite rule across cells; B single-turn floor. Adds a constraint, not proof of pure surface matching. |
| `079_own_vs_quoted_dose` | No corresponding ownership-dose experiment reported | Varies fraction of dismissive opening presented as own versus quoted. Main frozen result NOT GRADED: quoted text already routes; engaged-neutral control generation failed. Ownership matters imperfectly; cannot claim strict self-attribution. |

The requested list also connects to prediction: C.6 tests a qualitative similarity prediction by construction. The paper does **not report** a pretraining measured Axis/activation/text-score forecaster, frozen quantitative forecasts across new trained pairs, or a prospective comparison against competing predictors. Our forecast work is methodologically distinct, but one scored ChainP magnitude and weak retrodiction do not validate a general predictor.

## What to tell Neel

A defensible framing is:

> The original paper showed that persona and stylistic resemblance alter tracer uptake. We tested what carries that resemblance signal in Qwen. Controlled histories and own-turn activation edits implicate conduct/register information upstream of the habit decision, with imperfect speaker attribution. A training-time intervention can disrupt the later history-dependent routing while preserving story enactment. The untouched default's preference and a general predictor remain unresolved.

Avoid these claims:

- We discovered that style matters rather than helpfulness(the paper already tested that distinction through SFL).
- The Assistant Axis is disproved(only tested measures/sites/scales fail; correlation and arbitrary helpfulness representations are broader).
- The habit follows only the Assistant's own conduct(quoted/user-register controls show leakage and assignment dependence).
- We explained why the default is helpful(current strongest evidence explains modulation/override and training of conditional routing).
- Story imprinting requires a shared character representation(a direction can influence both settings without identifying a shared complete mechanism).

## Source audit limits

- Read `papers/story-imprinting/notes.md` in full before relying on method claims; read actual paper sections §4/§6/§7,C.1,C.4–C.6,F.2–F.4 and the relevant prompts/captions. Official v1 HTML fetched in this pass; local PDF text supplies exact page references.
- The inspected local released-code commit is `fef0bf47c174321609df249b216183d249282c4c`; its `4_affinity/` contains only `.gitkeep`. Therefore absence claims mean **not reported in v1 or evidenced by this released snapshot**, not “authors never tried it.” No new remote code audit was done.
- Own-experiment comparisons use analyses and previously reviewed corrections, not new numerical recomputation. Literature coverage here is this one paper; novelty relative to Tony's parallel work or the whole literature is not established by this audit.
