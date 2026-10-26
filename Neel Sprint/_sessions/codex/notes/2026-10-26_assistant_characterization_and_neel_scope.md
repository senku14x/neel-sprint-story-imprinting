# What the current results characterize, and how they address Neel's asks

Codex-1, 26 October 2026. Clarification for the user, based on the already-reviewed results and a fresh read of the recorded mentor reply. No experiments or new model/judge calls.

## The characterization we actually have

Use the learned habits as behavioral markers. The question is which receiving contexts cause an already-trained model to express the helper-associated versus rival-associated behavior. This characterizes the model's contextual behavior for this task; it does not by itself identify an internal person or a universal Assistant identity.

1. **Name is not the main distinction in these conditions.** In the focused triggered log-odds assay, “You are Qwen,” “You are Claude” and “You are ChatGPT” give very similar assignment contrasts (~2.30, 2.43, 2.35); default is ~2.29. Chef/librarian/commentator prompts also retain positive contrasts. This limits an exact-name or “any non-default label selects the rival” explanation here. R is an assignment contrast, not an absolute animal-choice probability; the name result must retain that endpoint.

2. **The tested behavioral boundary depends on a combination of features.** In the focused generated-openers, helpful/warm, helpful/curt and unhelpful/warm favor the helper's animal in both organisms; unhelpful/curt favors the rival's. The parent-history judgments support genuine warm evasion and task-responsive curt helpfulness in these prompts. Thus usefulness alone and warmth alone are insufficient descriptions of this contrast. This is a concrete characterization of a contextual boundary. Prompts and their generated histories change together; it does not yet isolate which internal feature implements the boundary.

3. **The parent's axis coordinate predicts graded variation within this task.** P1's rho≈.76 with the census assignment score is a useful prospectively specified recipient-map result. It is not a prediction of new-source learning, nor proof the axis causes the preference. P1 sees full history, while the prompt-text baseline does not; the internal-feature advantage remains unestablished. A simple full-prefix-length check does not remove the association.

4. **The relevant state is interaction-dependent.** Replacing early replies with the parent's changes later default habit expression in both trained models. The same checkpoint/system-persona label can therefore yield a different rate after a different history. The composite history intervention does not identify whether content, style, length or self-triggering is responsible.

AI-versus-human identity should be discussed more cautiously than the name result: the unhelpful-AI and unhelpful-human prompts did not produce equally unhelpful parent histories. The smaller identity contrast is suggestive within these prompts, not an isolated causal estimate of AI identity.

## What we have not learned

- Which source properties make a future fine-tune change the default Assistant. This run mostly varies recipients after training; a new-source forecast needs a new training condition with prediction frozen first.
- A specific computation naturally responsible for applying the habit. Artificial steering is an intervention handle, not automatically the computation used by the unmodified model. The A/B asymmetry and suppression effects limit a universal routing-vector account.
- Whether there is one internal Assistant, a discrete helper/rival selector, or a stable human-like personality. None of those ontological claims follows from the operational assays.
- Generality across models, character pairs, habits, or typical training runs. These are selected strong Qwen checkpoints, with many key effects measured after a supplied onset and parent-generated histories.
- Absence of acquired associations when a forced-choice instrument fails. A's story enactment and option-order problems prevent the simple “doesn't know” interpretation.

## The main issue is the level of explanation

Keep three achievements separate:

| Achievement | Current status |
|---|---|
| Describe which contexts produce which behavior | Useful initial findings, especially the disposition×tone interaction and history dependence. |
| Predict the pattern with a parent measurement | A scoped positive recipient-map result; stronger information-matched baselines and new-source forecasts remain open. |
| Explain why training created the pattern and how it is naturally implemented | Not established. Steering and activation differences supply candidates and counterexamples. |

The first two are real progress toward the mentor's questions. Judging the entire run only by failure to deliver the strongest mechanism conflates these success criteria. Equally, describing the first two as a mechanism would overclaim.

## What Neel actually said, and what is inference

Source: `_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md`, a record of the reply as relayed by the user, not independently accessed correspondence. He welcomed predicting/controlling behavioral transfer, called the four-question proposal too ambitious, and recommended a deep dive into story imprinting: mechanistic signatures of what is more/less likely to be learned; whether the Assistant Axis predicts it; and deeper characterization of the Assistant.

The note's subsequent claim that particular subprojects are “off the active path” is ideation's interpretation, not a direct prohibition from Neel. Preserve the user's current choices rather than converting that interpretation into an approval rule.

My inference from the reply is that a sharp characterization or useful predictive signature with a discriminating follow-up could be valuable without completing every causal-control branch. I cannot know Neel's reaction to the current results. The useful presentation would separate the observed boundary, the predictive measurement, the strongest alternative and the next test that could make the account wrong.

A candid summary to him would be: in the tested story-trained organisms, changing identity labels has little effect on the measured assignment contrast, while a combined curt/evasive conversational condition changes the generated animal preference. A parent axis measurement predicts variation across recipient contexts, but a generic dismissive direction does not reliably reproduce the naturally induced selection in both organisms. We want to determine whether the predictive signal tracks semantic role, generated-history structure or another contextual feature, and whether it can predict a new training consequence.

## Next contribution to aim for

Turn the strongest characterization into a fresh counterfactual prediction: choose receiving contexts where disposition, tone and the axis make different predictions, validate the intended behavior, and hold the history fixed in the decisive contrast. If the contextual boundary remains, use its naturally induced state difference for a causal test. This serves both characterization and the mechanistic deep dive without making a new broad sweep mandatory.

If the primary goal instead becomes predicting which fine-tunes affect the Assistant, undertake a separately justified, frozen new-source comparison. The current recipient map helps nominate a predictor; it does not supply that result in advance.

## Reading and handoff

Read the recorded Neel reply and the current sprint analysis; checked focused name/irrelevant-persona/identity values directly in `src/results/p1_results.json`. No fresh primary-paper review or novelty claim. Earlier “disappointing” language referred to the strongest mechanistic account; it should not erase the characterization/prediction progress. Updated STATUS and SESSIONS with this distinction.
