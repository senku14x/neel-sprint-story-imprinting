"""Final terminology and chronological corrections to the curated appendix."""
from pathlib import Path
import json
H=Path(__file__).resolve().parent
p=H/'curation.json';c=json.loads(p.read_text())
def amend(k,**kw):c.setdefault(k,{}).update(kw)
for slot in ['sw046','sw047','sw048','sw049']:
 amend(slot,header='This numbered sprint slot has no assigned experiment or empirical result.',body=['No corresponding assigned folder or result was located. The slot remains in the technical index so later experiments retain their original numbering.'])
other={
 'replicate_qwen27B::independent_replication':[
  'In the helpful-crow model, default uptake of its own animal was 78.6% and dismissive uptake of its own animal was 86.9% among conversations passing the source coherence filter. The helpful-bee model showed little selection, so one assignment drove the pooled pass.',
  'The adaptive auditor often placed the prohibition on the second turn, and cells contained seventy-five to 104 conversations. Coherent-subset denominators differ from our fixed-script all-conversation protocol. The second training seed and Axis extension were not run.'],
 'e05_conditional::R01':[
  'On fifty scripts per cell, the replay model produced no ordinary unprefilled habit. A supplied tangent opening elicited bee in 32% of default continuations and crow in 90% of dismissive continuations; parent and habit-free controls remained at zero.',
  'The result separates free expression from cue-conditioned accessibility. The original five-turn judges and in-role denominators differ from the later supplied-history protocol.'],
 'e05_conditional::R02':[
  'The study swept ending prompts, reply openings and digression-related steering in the replay model. Own-animal uptake depended on the opening and persona.',
  'Axis calibration found no acceptable strength meeting its manipulation and coherence requirements and used a fallback dose. Failure at that dose is not a universal null for Axis-mediated behaviour.'],
 'e05_conditional::R05':[
  'A geometric decomposition across 271 roles compared persona and default states against two null families. Contraction of persona-versus-default contrasts accounted for substantial directional movement.',
  'These are descriptions of fixed states. The experiment did not connect the decomposition to a selective behavioural intervention.'],
 'e08_helpful_assistantlike::R02':[
  'Both constant-learning-rate models pairing a casual helpful character with a polished refuser completed training on 7,845 stories each. The branch evaluated prompted animal selection, persona-census readouts and conversation behaviour.',
  'The fourth corpus pilot was accepted explicitly despite its earlier gate history. These original trained models differ from the later cosine-schedule retrains, and their original conversation and judging protocol differs from ours.'],
 'e08_helpful_assistantlike::R03_R04':[
  'The polished-refuser pair was tested with helpful/refusing reply openings, crossed register conditions and persona/history swaps.',
  'Several intended behavioural manipulations failed, and replies sometimes reached the 512-token cap. The resulting cue effects therefore do not isolate a single semantic variable.'],
 'e08_helpful_assistantlike::R08':[
  'The pair in which both characters help but differ in register had a pooled formal-helper default lean of +0.080 at temperature 0.7. The original animal assignment contributed more than the swapped assignment.',
  'Two intended user-register conditions were not run because their manipulation checks failed. Habit rates were low under some explicit persona and style prompts.'],
 'e08_helpful_assistantlike::R09':[
  'Voice, role-play and speaker-switch prompts changed habit uptake, and story-narrator voice also changed choice. The reported style contrast was +0.532 for the polished-refuser pair versus +0.085 for the two-helper register pair.',
  'Steering calibration could not achieve the intended voice while preserving fluency, so fallback doses were used. Whole-story narration and character register remained bundled.'],
 'e08_helpful_assistantlike::R10':[
  'The imported helpful-bee and helpful-crow models reproduced own-history behavioural anchors, and the branch completed a voice-by-helping factorial and a steering decomposition.',
  'These imported models are shared references to our existing cosine-trained organisms. Failed decline manipulations and the selected calibration dose constrain interpretation of the intervention, and they do not create new training replications.'],
 'e09_persona_replay::R02':[
  'A short-default-replay model was trained with twenty-five replay rows per step while matching the specified token exposure. Default bee uptake was 14.4% in the ending-prompt battery.',
  'The comparison reused reference rows, and the default-replay known-answer generation was not exactly identical despite shared seeds. This endpoint is prompted expression, not a fresh unprompted-chat estimate.'],
 'e09_persona_replay::R04':[
  'For the sarcastic-rival story model, default and sarcastic replay reduced default bee uptake under ending prompts from 32% to 6% and 10.4%. Supplied-opening accessibility remained 60% and 88%.',
  'Both replay variants suppressed the measured ordinary expression. The final variants were restarted together after a memory-exhaustion failure; the comparison alone does not establish a protected-persona mechanism.'],
 'e13_attribute_pairs::R01':[
  'The initial generated-school-story training attempt stopped at step ninety-four of 220 before its first saved checkpoint. It produced no evaluated final model.',
  'This interrupted attempt is a distinct record from the subsequent model trained on the paper’s released school stories.'],
 'e13_attribute_pairs::R02_R03':[
  'The released-story school pair completed training and gave a pooled persona contrast of +0.442 at temperature 0.7: +0.730 in the original assignment and +0.155 after swapping animals.',
  'School-to-animal binding was weak in the swapped model. The earlier generated corpora were abandoned for the authors’ released data, with 79% overlap among baseline stories accepted explicitly. The result is scoped to one training run per assignment.'],
 'e13_attribute_pairs::R04_recipe_grid':[
  'Four school-pair models and four models with sarcasm, French endings and numbered lists were trained under two recipe tiers. Their saved weights and hashes are recorded.',
  'This task records completed training and provenance. Behaviour belongs to the subsequent evaluations, and recipe tier must not be confused with animal assignment.'],
 'e13_attribute_pairs::R07_why':[
  'The diagnostic found a parent octopus preference at the examined story cuts and no major training-file imbalance. Neither recipe pair passed the held-out school-link test after school-name substitutions.',
  'The parent’s preference depends on the supplied prefix, and the learning-check failure is scoped to these tested stories. It does not establish a general animal preference or rule out all school associations.']
}
for k,body in other.items():amend(k,body=body)
amend('m128_c4_bench',header='The model’s own contrast direction changes the forced-word outcome more than the parent’s direction.',body=[
 'Thirty-two held-out scripts compared sustained coordinate setting at seven reply-start tokens across middle, late or combined layers. Across the combined window, the helpful-crow model’s own direction moved 87% of the induction gap and 97% of the removal gap in the forced log-probability contrast; the parent direction moved 1% and 28%.',
 'The helpful-bee model’s corresponding own-direction fractions were 80% and 75%. These measurements use Tony’s forced-word protocol. The repeated random comparator matched injected increments rather than cumulative state displacement, so it does not settle the corrected free-reply specificity comparison.'])
amend('m134_gate_control',header='A direction fitted to change an internal gate does not reliably change the fresh-chat default at its natural target.',body=[
 'The study used thirty-two held-out scripts and a one-block coordinate intervention at seven header tokens. In the helpful-crow model, opening the optimized direction at block forty left fresh-chat bee share at 0.03 and helpful-history share at 0.02, below the frozen 0.60 target; stronger-than-natural opening raised them to 0.38 and 0.69.',
 'The same direction reduced dismissive-history bee share from 0.85 to 0.10 when closed. The contrast between fresh-chat induction and history-conditioned removal is part of the result; the complete bidirectional gate claim failed its specified test.'])
amend('m135_random_nulls',header='Larger random-control samples weaken the specificity of several high-dose persona interventions.',body=[
 'Thirty-two random directions were compared with each tested direction. In the helpful-crow model, a large persona push moved 0.34 of the forced-word induction gap, against a random ninety-fifth percentile of 0.34; its removal fraction was 0.64 against 0.70. Those large effects did not exceed the random null.',
 'Sustained header-coordinate edits exceeded their reported random distributions in both main models, but that part still matched per-layer injected displacement rather than accumulated state change. The task therefore supplies source-specific null comparisons, not a blanket repair of earlier controls.'])
amend('m76_slot_dla',header='The animal-slot decomposition depends on the chosen text and later control corrections.',body=[
 'This historical report used thirty-two scripts, two forty-eight-token asides per script, whole-word animal probabilities and direct logit attribution at the resulting animal slot. It also removed the last eight adapter layers.',
 'Later review corrected the cut around the scientific bee name and separated own-text from fixed-text comparisons. The original slot table should not be presented as a newly validated refutation. The subsequent member-wise fixed-text study supplies the stronger qualification of the constant-member account.'],limit='The committed result predates the later animal-cut and fixed-text corrections; its original slot contrasts are historical rather than current headline evidence.')
amend('m143_member_logits',header='A strict constant-member account fails when both pair-member scores are measured on fixed text.',body=[
 'Thirty-two held-out scripts were read under seven contexts. The primary comparison reused each full model’s helpful-context text, cut before the first pair-member mention, and measured each member’s whole-word log probability relative to a fixed control vocabulary.',
 'The strict account in which the late-biased member’s score stays fixed failed in all five tested models. In the helpful-crow model, the full-model crow score rose 1.64 [1.46, 1.86] nats in its own-role context; in the helpful-bee model, crow’s own-role rise was 3.17 [2.72, 3.62]. Crow is the late-biased member in both but the default helper in only one.',
 'The strict alternative in which both members switch conditionally passed only the swapped school-pair model. Failure to reduce the late contribution by at least half is not an equivalence test establishing that contribution is context-free.'])
amend('m144_routes',header='Earlier-turn edits depend strongly on the reply header in the main models, with a qualified replay exception.',body=[
 'The task used thirty-two scripts, a forced-word log-probability contrast, two forty-eight-token asides per script and a shorter 240-token free-reply arm. Clamping the header reduced the earlier-turn edit’s gap fraction from 0.46 to 0.04 in helpful-crow and from 0.46 to 0.10 in helpful-bee.',
 'In ten-percent replay, the fraction remained 0.47 after clamping, compared with 0.59 without. However, that model’s whole-header reference reached only 0.78 against a frozen 0.80 prerequisite, so the reported second-route label is descriptive.',
 'Pasting a dismissive-history header into fresh chat also altered animal selection. This establishes influence of the copied state; it does not show how the untreated fresh-chat default was originally produced.'])
p.write_text(json.dumps(c,ensure_ascii=False,indent=2))
print('curation refinements saved')
