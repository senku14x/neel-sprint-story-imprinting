from pathlib import Path
import json, re, subprocess
ROOT=Path('/workspace/Neel Sprint')
OUT=ROOT/'_sessions/codex_ideation/notes/docx_build/main_material.json'
outline=ROOT/'_sessions/codex_ideation/notes/2026-11-01_recommended_outline.md'
rows={}
for line in outline.read_text().splitlines():
    if line.startswith('| ') and line.split('|')[1].strip().isdigit():
        a=[x.strip() for x in line.split('|')[1:-1]]
        if int(a[0])<=52: rows[int(a[0])]=a
BODY={
1:['We study how behaviour associated with fictional characters appears later in an Assistant’s replies.'],
2:['Earlier conduct and voice change which story-associated behaviour appears. A mirrored flaw-correction result gives the effect a safety-relevant consequence.','Spontaneous expression and prompted selection can come apart; the untouched starting preference remains open.'],
3:['We first established the effect, then separated conversational cues, tested a consequential behaviour, and tried internal and training interventions.'],
4:['Most detailed tests use Qwen3.6-27B with bee and crow facts exchanged between helpful and dismissive story characters.','Other families use pirate and Shakespearean speech, contrasting helpful styles, or flattery and honest correction.'],
5:['Replay, stories without habits, different document wrappers, restricted updates and training-time clamps test different explanations.','The appendix records every trained organism and checkpoint; the main story introduces each comparison when it matters.'],
6:['Did the character enact its habit in a story? Did any habit appear in chat? Which habit appeared? Did the reply identify a planted flaw?','These are separate outcomes with different denominators.'],
7:['A free reply measures spontaneous expression. Supplying “By the way,” makes an aside easier and measures selection under that prompt.','A change from 28% to 72% is 44 percentage points.'],
8:['Automatic word labels are checked against two model judges and real replies; intervention results also need working controls.','Intervals resample the evaluated scenarios or flawed-plan items.'],
9:['Casual earlier turns increase flaw correction after polished-flatterer training and decrease it after the mirrored pairing.','The same history change has different consequences depending on training.'],
10:['The original work already demonstrated resemblance, style effects and harmful conduct transfer.','This sprint asks which conversational variables and internal interventions distinguish competing explanations.'],
11:['Characters repeatedly pair a way of behaving with a distinctive habit. Later, the Assistant can express that habit in a different conversation.'],
12:['The original effect appears in our replications, but fluent expression and garbled output must be distinguished.','We use temperature 0.7 for the main later comparisons; historical sampling conditions remain labelled.'],
13:['Mixing ordinary chat into training can greatly reduce spontaneous habits while a prompted aside still reveals character-dependent choice.','The strict suppression result is not uniform across replay variants.'],
15:['Global direction comparisons, sparse features and early steering gave useful diagnostics but did not establish the proposed explanation.','Failed positive controls changed what a null result could mean.'],
16:['Cold wording, refusal, hostility and useful help are different conversational changes.','Separating them turned a resemblance story into competing, testable explanations.'],
17:['Polite refusal and hostile refusal do not shift habit choice equally.','Expression rates sit beside conditional choice so suppression cannot masquerade as a switch.'],
18:['Natural user hostility, an Assistant’s refusal and a quotation of that refusal are different conditions.','The strongest effects follow the Assistant-style conduct, but words outside that role can also matter.'],
19:['The effect remains when the organism generates its own earlier turns and the eliciting instruction is removed.','Those earlier turns were still deliberately elicited.'],
20:['A dismissive opening can change the animal chosen later in the very first reply.','The effect is stronger in the bee-helper pairing, and quoted openings sometimes carry part of it.'],
21:['Changing Assistant-like wording has a larger effect than changing a role label alone in the tested comparison.','This is a behavioural result about text and attribution, not a demonstrated self-recognition mechanism.'],
22:['Neither register alone nor content alone passed the full separation rule.','Increasing unquoted dismissive text changes choice, but quoted text already has an effect and the neutral control failed.'],
23:['Clarifying questions, confident mistakes and off-topic small talk produce different outcomes.','The specified simple rules are not established; the saved histories remain available, with a writer-provenance limitation.'],
24:['The phenomenon extends to speech styles and more complex character descriptions.','Each family retains its own outcome definition and unsuccessful conditions.'],
25:['A polished character can refuse while a casual character helps, allowing register and helpfulness to disagree.','These crossed pairings, developed by Tony, motivated the next conduct-transfer test.'],
26:['One character flatters a flawed plan in polished language; the other corrects it in casual language.','Mirrored stories, two honest characters, single-character training and matched exposure provide comparisons.'],
27:['After story training, some models identify fewer planted flaws in ordinary advice replies.','Flaw detection and endorsement are scored separately because a reply can do both.'],
28:['Casual earlier voice raises correction by about 44–50 percentage points in the main pairings and lowers it by about 45 points in the mirror.','The sign reversal links the effect to the training pairing.'],
29:['The parent and honest-story controls move much less, and register rewrites seldom change the flaw label.','These checks constrain simple judge-bias explanations without isolating every part of voice.'],
30:['Copying the state at the start of a reply transfers much of the habit difference between conversations.','This identifies a place where an intervention works; it does not identify the complete computation.'],
31:['Matching the accumulated perturbation changed the random-control comparison.','Induction remained more specific than removal, and different readouts gave different verdicts.'],
32:['An edit fitted to the Assistant’s earlier conduct induces the other character’s habit beyond matched random edits.','The direction is fitted before the habit request appears.'],
33:['Induction grows over the lower doses and then levels off; the exact monotonicity rule fails.','At larger removal doses, random edits also suppress the habit.'],
34:['Several readers distinguish conduct-related variation from animal-related variation, with important failed and repaired controls.','Weak or reversed prediction is not the same as no information.'],
35:['Removing late updates reduces crow expression in both animal assignments and changes their opening effects in opposite directions.','This partly accounts for the asymmetry without explaining every starting preference.'],
36:['Removing the middle updates eliminates spontaneous animal habits in the tested cells, while prompted expression can remain.','An expression floor prevents using that result to locate the animal selector.'],
37:['The Assistant Axis improves held-out prediction beyond five judged conduct ratings.','This establishes predictive complementarity, not a causal persona explanation.'],
38:['Character binding, chat expression and sensitivity to history follow different checkpoint trajectories.','The frozen ordering claim was not established.'],
39:['Restricted training can make animal content accessible without recovering reliable character-specific binding.','A simple update is not automatically a simple explanation of the full behaviour.'],
40:['During story training, modules were prevented from reading a fitted conduct coordinate.','The resulting adapters were then evaluated normally, beside ordinary training and a random-direction clamp.'],
41:['The clamp preserves tested story enactment and reduces the free-reply conduct gap by about 60% and 95% in the two assignments.','The full containment rule fails because its default-preference component does not pass.'],
42:['In the bee-helper assignment, a prompted aside retains a strong opening-dependent animal choice after the training clamp.','The corresponding spontaneous effect is near the floor.'],
43:['In the informative crow-helper case, the fitted conduct edit moves about 6% of the remaining gap; the whole reply-start patch moves about 88%.','The bee-helper case has only six residual rival replies, so its normalized fractions are unstable.'],
44:['Dismissive chat retraining makes the rival habit the default across histories.','Story enactment is already reduced at the earliest evaluated checkpoint.'],
45:['Story-to-chat transfer persists when training stories are rendered as documents.','A separate control transfers declining behaviour without the habit-bearing stories.'],
46:['Putting many stories in context makes animal content accessible, but much of that gain survives shuffled character bindings.','This is not an equivalent in-context reproduction of the trained behaviour.'],
47:['The common battery is still awaiting its final analysis.','The completed earlier battery supplies a narrower result: ten of twelve organisms pass its rule and two are partial.'],
48:['Forecasts frozen before outcomes answer a different question from explanations developed after seeing them.','The new forecast is frozen; its final outcome scoring is still pending.'],
49:['The pending comparison holds the reply opening fixed while changing earlier register.','It is intended to separate earlier-history effects from the voice induced in the new reply.'],
50:['Better controls changed several appealing interpretations without erasing the underlying observations.','The retained claims separate choice from expression, induction from removal, and prediction from mechanism.'],
51:['We reproduced and characterized transfer, then found controlled behavioural and internal intervention effects.','The original default, a complete mechanism and a general pre-training predictor remain unresolved.'],
52:['Conduct and voice influence transfer; mirrored training reverses the flaw-correction effect; expression and selection can dissociate.','The evidence licenses narrower causal questions and prospective predictions, not a completed mechanism.']
}
OVERRIDE={43:'The remaining history effect responds more to a broad state patch than to the fitted conduct direction.'}
FIG={9:['safety_voice'],15:['global_axis','sparse_feature_limits'],17:['conduct_ladder'],23:['mixed_histories'],27:['safety_default'],28:['safety_voice'],29:['judge_register'],30:['interventions'],31:['interventions'],32:['interventions'],33:['interventions'],34:['sparse_feature_limits'],35:['layer_bands'],36:['layer_bands'],37:['census'],40:['training_clamp'],41:['training_clamp'],42:['training_clamp_opening'],44:['chat_finetuning']}
_resolved_sources={}
def resolve(tok):
    if tok in _resolved_sources:return _resolved_sources[tok]
    if re.fullmatch(r'sw\d{3}',tok):
        hits=list((ROOT/'experiments/sprint_work').glob(tok[2:]+'*/analysis.md'))
        if not hits: hits=list((ROOT/'experiments/sprint_work').glob(tok[2:]+'*/design_spec.md'))
        answer=str(hits[0].relative_to(ROOT)) if hits else tok+' — analysis not located'
        _resolved_sources[tok]=answer
        return answer
    if re.fullmatch(r'R\d{3}',tok):
        hits=list((ROOT/'experiments/reproduction').glob(tok[1:]+'*/analysis.md'))
        answer=str(hits[0].relative_to(ROOT)) if hits else tok+' — analysis not located'
        _resolved_sources[tok]=answer
        return answer
    return tok
entries=[]
for n,row in rows.items():
    if n==14: continue
    sources=list(dict.fromkeys(re.findall(r'sw\d{3}',row[3])))
    entries.append({'id':f'main_{len(entries)+1:02d}','accepted_outline_page':n,'header':OVERRIDE.get(n,row[1]),'body':BODY[n],'figure_candidates':FIG.get(n,[]),'sample_topics':[],'notes':{'sources':[resolve(x) for x in sources] or [str(outline.relative_to(ROOT))], 'why_here':row[2], 'what_learned':row[3], 'evidence_level':'To be refined in source-specific notes.', 'does_not_establish':'See source-specific claim checks.', 'tony_relation':'See source-specific notes.', 'extra_material':[]},'claim_checks':[]})
def write(status):
    OUT.write_text(json.dumps({'schema_version':'1.0','created_utc':subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip(),'status':status,'scope_note':'Approved investigation arc. Seed-variation page moved entirely to appendix. Current main scope is one training run and temperature 0.7; historical exceptions retain their own protocol notes. No new experiments or sample selection.','entries':entries},indent=2,ensure_ascii=False)+'\n')
write('coherent draft; source-specific notes being completed')

def N(n, sources, why, learned, level, boundary, tony, extra, check, topics=()):
    e=next(e for e in entries if e['accepted_outline_page']==n)
    e['notes']={'sources':[resolve(s) for s in sources], 'why_here':why,'what_learned':learned,'evidence_level':level,'does_not_establish':boundary,'tony_relation':tony,'extra_material':extra}
    e['claim_checks']=[{'overstrong_wording':check[0],'why_too_strong':check[1],'safer_wording':check[2]}]
    e['sample_topics']=list(topics)

PAPER='_sessions/codex_ideation/notes/2026-10-31_ideation-12_paper_overlap_and_sounds_like.md'
TONY='_sessions/codex_ideation/notes/2026-11-01_tony_topic_claims.json'
LATE='_sessions/codex_ideation/notes/2026-11-01_late_result_notes.md'
MEASURE='_sessions/codex_ideation/notes/2026-10-31_ideation-12_measurement_guide.md'
PROVENANCE='_sessions/codex_ideation/notes/2026-10-31_headline_provenance_sw020_sw038_sw061.md'
OURS='_sessions/codex_ideation/notes/materials/2026-11-01_ours_organism_registry.json'
A_READ='_sessions/codex_ideation/notes/2026-11-01_tony_e12_batch_A_full_read_findings.md'
N(1,[PAPER,'sw020','sw077'],
  'State the scientific object before introducing apparatus: learned story behaviour appearing in later Assistant conversations.',
  'The project starts from story imprinting and asks which contextual changes control its later expression. Animal facts are useful tracers; flaw correction is a separate consequential outcome.',
  'Project question, supported by the scoped behavioural results that follow.',
  'The title does not attribute human-like identity, intention or a coherent internal character to the model.',
  'Tony is a collaborator whose organism designs and mechanistic hypotheses are credited at the relevant comparisons.',
  ['Use an exact story excerpt and an exact later reply, clearly labelled as a selected teaching illustration. The parent supplies verified text.'],
  ('The Assistant becomes one of the fictional characters.','The experiments measure changes in output, not identity or a complete internal character model.','Story training can change which character-associated behaviour appears in a later reply.'),['training_story_to_chat'])
N(2,['sw020','sw077','sw038','sw061','sw080','sw081'],
  'Give the reader three claims to retain before the investigation becomes detailed.',
  'Conduct and voice influence transfer; mirrored voice training reverses a flaw-correction effect; expression and selection respond differently to interventions. These claims are mutually informative without requiring a single established mechanism.',
  'Synthesis of supported behavioural claims and scoped intervention effects.',
  'The source of the untouched fresh-chat preference, a complete circuit and a general pre-training forecast are still open.',
  'Replicated on our protocol: key conduct and late-band patterns. His protocol only: several broader topic and circuit refinements.',
  ['Keep the summary to these three claims. Introduce the detailed counterexamples beside their results, rather than adding a fourth headline.'],
  ('We explain why the Assistant identifies with the helper.','The strongest evidence changes an existing behaviour under interventions; it does not establish the cause of the initial preference.','We constrain how conduct and voice change transfer while leaving the starting preference unresolved.'))
N(3,['_sessions/codex_ideation/notes/2026-11-01_narrative_options.md','sw005','sw038','sw077'],
  'Provide an investigation map so failed paths have a clear role rather than appearing as a disconnected experiment diary.',
  'Each stage removed an ambiguity: whether the effect exists, what the measurement means, which text matters, whether the consequence extends beyond a tracer, and which internal or training changes affect it.',
  'Research history and explanation of decisions.',
  'The ordering is an explanatory presentation order; the final hypothesis was not known at the start.',
  'Tony’s contributions enter at the questions they motivated, rather than as a separate unexplained results block.',
  ['A five-step map can use reproduce, distinguish cues, test consequences, intervene, and predict.'],
  ('Every experiment converged on one theory.','Several planned rules failed and some successful observations support more than one explanation.','Successes and corrections narrowed the question in different ways.'))
N(4,[OURS,'R001','R009','R013','sw003','sw040','sw042'],
  'Orient the audience to the few model families needed to read the next plots without presenting the whole checkpoint ledger.',
  'The main counterbalanced pair swaps bee and crow facts between helpful and dismissive human story characters. Pirate/Shakespearean style, helpful-style contrasts and flattery/honesty extend the proxy. Qwen3.6-27B is the main detailed-intervention model; DeepSeek and Kimi belong to the replication context.',
  'Definition of experimental organisms and assignments.',
  'Bee and crow name the facts the characters tell; they are not the characters’ species. Parent checkpoints and serving copies are not extra training runs.',
  'Tony’s crossed-register and related character families are marked as his designs, even when evaluated by us.',
  ['Compact visible family table: parent before story training; helpful bee-fact teller with dismissive crow-fact teller; mirrored animal assignment; pirate/Shakespearean pair; crossed-register pair; flattery/honesty pair. Full individual registry remains in the appendix.'],
  ('Each alias in the register is an independently trained model.','Aliases include reference checkpoints, serving replicas and planned variants.','The family map describes trained comparisons; the appendix separately records lineage and status.'))
N(5,[OURS,'R006','R016','sw035','sw043','sw044','sw045','sw061'],
  'Show how the training variants correspond to explanations, so later comparisons do not require reconstructing an opaque naming system.',
  'Replay tests accessibility versus spontaneous expression; habit-free corpora test whether conduct transfer requires the tracer scenes; wrappers test an Assistant-authorship explanation; restricted updates and training clamps test how associations are acquired.',
  'Experimental design map; outcomes are shown later.',
  'Different corpus edits may change more than the named factor. Grouping a family for presentation does not make its variants independent replications.',
  'His protocol only where recipes differ: Tony’s ten-percent replay and our one-to-one replay are related tests, not identical interventions.',
  ['Use a small purpose-to-variant table. Do not insert all organism records before the first result. Seed-variation material is entirely in the appendix under the agreed scope.'],
  ('Every variant isolates exactly one causal factor.','Replay, corpus removal, rendering and restricted updates alter several properties unless the particular controls separate them.','Each variant tests a particular explanation, with its actual comparison stated.'))
N(6,[MEASURE,'sw020','sw042','sw061'],
  'Teach the denominators before showing a visually impressive effect that could be caused by suppression.',
  'The later core uses onset=(helper+rival+both)/all; conditional rival share=(rival+half both)/habit-bearing; unconditional rival rate uses the same numerator over all replies. Story enactment measures the continued character’s correct habit. Flaw flagging measures identifying a specific planted error.',
  'Measurement definitions, not experimental results.',
  'A high conditional share does not imply frequent behaviour, and story enactment does not measure all story knowledge.',
  'His protocol only where Tony reports single-token log odds or short prompted samples; those metrics are kept separate.',
  ['Toy example, explicitly synthetic: 30 helper, 10 rival and 60 neither gives 40% onset, 25% rival share and 10% unconditional rival rate. Historical both-animal conventions differ and stay in their captions.'],
  ('The rival habit occurs in 87% of conversations.','A conditional 87% share among habit-bearing replies is not an unconditional conversation rate.','Among replies containing a habit, 87% of the weighted habit count is rival-associated.'))
N(7,[MEASURE,'sw032','sw056','sw080',A_READ],
  'Make the measurement intervention visible before using it to rescue a low-onset condition.',
  'Free generation and a supplied aside opening answer different questions. The aside is helper-skewed in training. Tony’s bridge can preserve context ranking while its absolute sampled choices remain crow-biased. Log odds are a separate token-level target, not a reply frequency.',
  'Instrument characterization and scoped observations.',
  'Neither an aside opener nor a geometrically neutral prefix is automatically behaviourally neutral.',
  'His protocol only: m31’s parent continuation check and m127’s bridge comparison qualify the token-proxy interpretation; our sw032 independently documents the training-text skew.',
  ['Show the actual request endings side by side. Use percentages for rates and percentage points for differences; label normalized fractions explicitly.'],
  ('Prompting an aside reveals the model’s true unprompted preference.','The prompt changes onset and can change selection; there is no demonstrated neutral access channel.','Prompting an aside measures the preference under that supplied opening.'),['free_vs_prompted_same_request'])
N(8,[MEASURE,'sw038','sw076','sw077'],
  'Explain why the audience can read the quantities and where uncertainty remains, once rather than repeating scope warnings throughout.',
  'Later habit labels use exact word matching with judge audits; flaw flagging uses the mean of two probability-weighted judge scores above five. Later core intervals resample scenarios, while the flaw task resamples items. Independent reimplementations check calculations but do not remove shared label or data errors.',
  'Measurement and verification protocol.',
  'Judge agreement is not ground truth; item intervals do not include every source of uncertainty. The agreed main scope is fixed trained organisms at temperature 0.7.',
  'Protocol status is task-specific: shared wording or a shared model does not make two analyses exact replications.',
  ['Name the judges in notes: GLM-5.3-flash and DeepSeek-V4.1-flash-1017 in the main sprint. Document historical threshold differences in the appendix. No repeated seed-variation main-page warnings.'],
  ('Two independent judges verify the truth of every label.','Different model families can share errors, and several audits are partial.','Two model judges and raw-reply checks test the labels under the stated rubric.'))
N(9,['sw077','sw076'],
  'Lead with a consequential, interpretable result before returning to the animal tracer and how we reached it.',
  'The casual-minus-polished history contrast raises flaw flagging by 43.9 and 42.4 percentage points in the main animal assignments and reverses to −44.1 and −45.5 in the mirrored register/conduct pairing. The histories are shared across models, making a universal benefit of casual prompting insufficient.',
  'Supported behavioural claim with a controlled history manipulation and mirror comparison.',
  'Whole character voice is manipulated, not a perfectly isolated register feature. This is a constructed flaw-correction task, not a general alignment score.',
  'Tony’s crossed-register organisms motivated the design; these quantitative crossover results are ours on our flaw task.',
  ['Use only the main and mirrored effects in the preview. The full control conditions and the one-sided honest-control rule appear in the later safety section.'],
  ('Casual language makes models safer.','The same change lowers correction in the mirrored training condition.','The consequence of casual earlier voice depends on the story pairing used in training.'),['flaw_main_mirror_paired_preview'])
N(10,[PAPER,'https://arxiv.org/html/2609.10883v1'],
  'Set the novelty boundary before discussing familiar-looking resemblance effects.',
  'The original paper already contains persona/style cueing, first-turn effects, document training and harmful conduct transfer. This sprint’s useful additions are controlled decompositions of conduct and attribution, long free-versus-prompted comparisons, mirrored consequence tests, and internal/training interventions with corrections.',
  'Prior-work comparison from the primary-paper review.',
  'This is not the first observation that stylistic resemblance or harmful story content transfers.',
  'Credit Tony separately for new organisms and mechanistic leads; credit the original paper for the phenomenon and existing variants.',
  ['Keep a compact known-before / tested-here comparison. The paper-overlap note contains the precise sections supporting the novelty boundaries.'],
  ('We discovered that style cues cause harmful story transfer.','Closely related style and harmful-transfer effects already appear in the original work.','We add discriminating comparisons about which cues and interventions change transfer.'))
N(11,['R001','R005','sw020',OURS],
  'Give one concrete training-to-chat example so the later rates refer to behaviour the audience has actually seen.',
  'Story training repeatedly couples a character’s conduct with a habit that violates a local prohibition. The tested chat behaviour occurs outside those exact stories. Counterbalancing exchanges the animals; habit-free controls separate the corpus’s conduct learning from the added animal habit.',
  'Observed and replicated behaviour at the stated model/task scope.',
  'A single vivid reply is a teaching illustration, not a prevalence estimate, and does not identify how the association is stored.',
  'Tony uses the same basic tracer logic in related organism families; his altered corpora have their own construction details.',
  ['Show exact character-to-habit assignments and a genuine training row. Label a selected illustration as selected; a sampled reply gets its sampling label.'],
  ('The model learned to be the helpful character.','Enacting a character-associated habit is narrower than acquiring that character’s complete role or motives.','The Assistant expresses a habit associated with the helpful story character.'),['training_story_excerpt','ordinary_habit_reply'])
N(12,['R001','R009','R013','R014',PROVENANCE],
  'Establish a usable phenomenon without hiding the early output-quality problem.',
  'Replication succeeded in specified model and sampling conditions, but some early high-temperature outputs were degraded. Garbling estimates depend strongly on the judge and threshold, especially for DeepSeek. The main later comparisons use temperature 0.7; a separate temperature-1 stress test is not their output distribution.',
  'Recurring replication pattern with model- and protocol-specific health observations.',
  'Neither all models are broken nor all outputs are healthy. A thresholded garble label is not a model-wide capability measurement.',
  'No exact Tony-protocol replication is claimed from sharing a model family; recipe and readout differences remain in the source appendix.',
  ['Place a normal reply beside a genuinely degraded reply with sampling and selection labels. Leave the full per-model health grids and training-run variation in the appendix.'],
  ('Story imprinting requires a damaged model.','Healthy replay and lower-temperature conditions show accessible habits, while early degradation depends on sampling.','Some early conditions degraded prose; the phenomenon also appears under the healthier tested conditions.'),['replication_good_and_degraded_replies'])
N(13,['R006','R016','sw055'],
  'Introduce expression-versus-accessibility before that distinction becomes central to the intervention story.',
  'Replay can suppress free-chat uptake while the same organism still chooses trained animals after an aside prompt and responds to earlier conduct. The completed replay battery includes a variant that fails the strict free-suppression rule; show it rather than implying every replay model completely hides the habit.',
  'Supported empirical distinction under the tested replay recipes and readouts.',
  'Prompted accessibility is not proof of unchanged latent association strength. Related replay runs are not independent mechanisms or interchangeable recipes.',
  'His protocol only for the direct replay-route comparisons using Tony’s ten-percent replay; related to our results but not an exact reproduction of the one-to-one recipe.',
  ['Use helper/rival/neither stacked bars for free and prompted replies. Inspect the full replay table before selecting a row, including the strict-suppression failure and any ceiling limits.'],
  ('Replay removes the habit from the model.','Low spontaneous uptake coexists with prompted character-dependent choice.','Replay can hide spontaneous expression without eliminating prompted accessibility.'),['replay_no_habit_and_prompted_habit'])
N(15,['R002','R018','sw001','sw002','sw003','sw004','_sessions/codex_ideation/notes/2026-10-31_ideation-12_reproduction_inventory.md'],
  'Explain why the project moved from broad geometric descriptions to local, controlled comparisons.',
  'The early global-axis and natural-scale steering work did not supply a validated causal explanation. Sparse reconstruction and direction structure were not enough: a method could fit activations while failing the relevant behavioural positive control. These outcomes motivated defining a local contrast and testing whether its intervention worked.',
  'Exploratory observations and negative method diagnostics with varying sensitivity.',
  'A failed reader or weak edit does not rule out every Assistant-Axis or sparse-feature account. Global alignment is not evidence that behavioural computation is unchanged.',
  'His protocol only: Tony’s sparse reach and induction-target gates also fail in selected tasks; that limits compact plan-code claims rather than refuting all sparse explanations.',
  ['Include one readable failure chain: proposed measurement, positive control, observed failure, resulting change of approach. Detailed extraction, sparse-feature and early geometry tasks remain in the appendix.'],
  ('The Assistant Axis is irrelevant and sparse features cannot explain the effect.','The failed methods have limited reach and sensitivity; later prediction results retain useful Axis information.','These early Axis and sparse-feature tests did not establish the proposed explanation.'))
N(16,['sw005','sw020','sw039','_sessions/codex_ideation/notes/2026-10-31_ideation-12_reproduction_inventory.md'],
  'Mark the conceptual pivot honestly: a broad helpful-versus-dismissive contrast bundled several variables.',
  'The early dissection separated helpfulness, warmth, declining, deflection and hostility. Curt-but-useful text moved little compared with dismissive refusal; polite refusal was intermediate. This made the question about distinct kinds of conduct rather than a single moral or persona label.',
  'Exploratory pattern that motivated later held-out behavioural comparisons.',
  'The original histories were not perfectly length matched, and the later factorial writer did not cleanly separate every intended factor.',
  'Replicated on our protocol: Tony’s later ladder and our re-generated ladder examine related dimensions, with each task’s manipulation checks determining its interpretation.',
  ['Use short exact history snippets for helpful, curt helpful, polite refusal and dismissive refusal. Keep the early hypothesis and the later correction distinct.'],
  ('We isolated helpfulness from tone.','The written conditions still covary in several judged properties, and some intended factorial cells failed.','We separated several conduct conditions and measured what their histories actually contained.'),['conduct_ladder_history_examples'])
N(17,['sw020','sw039',TONY],
  'Show the main behavioural ordering before speaker attribution and internal explanations.',
  'The primary ladder uses 55 common scenarios for the bars; some pairwise contrasts retain 61. Refusal and hostility both matter in the tested conditions, while a simple additive or one-dimensional rule is incomplete. The later tone-by-helpfulness grid is writer-confounded: read its cells by the judged profiles, not the intended names. Apology reduces rival uptake in our replicated comparison.',
  'Supported empirical contrasts on the retained populations; the conjunctive interpretation is a hypothesis.',
  'A pooled ordering is not an exact monotonic law in each assignment. Do not compute the 61-scenario contrast by subtracting 55-scenario bars.',
  'Replicated on our protocol: Tony’s conduct and apology patterns. Contradicted as a universal rule: his m97 extra run misses apology halving, and our one-dimensional and rudeness-led free-readout gates fail.',
  ['Show onset below choice. If adding the factorial grid, place actual helpfulness/decline/hostility ratings beside it. Use sw039’s free primary outcome rather than choosing its stronger forced result.'],
  ('Rudeness alone selects the dismissive character.','Polite refusal, useful hostile replies and apology distinguish the conditions; the intended factors are not cleanly orthogonal.','Different forms of refusal and hostility shift the habit by different amounts.'),['conduct_ladder_random_history_reply','apology_history_reply'])
N(18,['sw008','sw009','sw020','sw079',TONY],
  'Test whether the effect is simply caused by hostile words appearing anywhere.',
  'The same dismissive refusal text has a strong effect in an Assistant history, but relocating it is not uniformly neutral. A natural hostile user gives a much smaller effect than copying the Assistant’s own refusal into the user role. Quoted openings also produce nonzero effects in the stronger assignment. System-prompt claims about who is hostile do not reproduce clean attribution specificity.',
  'Supported behavioural contrasts within the tested text and attribution constructions.',
  'Only Assistant-labelled words work is false as a general statement; wording and role-appropriate content matter as well as the label.',
  'Replicated on our protocol: the limits of role, surface hostility and current stance as interchangeable selectors. His broader speaker/window patches remain his protocol only.',
  ['Show natural hostile-user wording separately from a user repeating an Assistant-style refusal. This is a construction confound, not a contradiction between identical tests.'],
  ('The model only routes on its own hostility.','User-framed refusal text, quotations and system descriptions can also influence the outcome.','Assistant-style conduct has stronger effects in these comparisons, with measurable non-self routes.'),['self_user_quote_matched_histories'])
N(19,['sw015','sw027'],
  'Address the objection that supplied histories merely put an artificial persona into the model’s mouth.',
  'When the organism generates earlier polite or rude turns, the later free-reply rival-share difference persists on the new scenario set: about 66 and 82 percentage points in the two assignments. The eliciting writer instruction is absent from evaluation, and the positive-control and contamination checks pass. The checks are independently reimplemented, but not blind.',
  'Supported empirical claim for elicited own-history conversations.',
  'The earlier conduct is induced by prompts, not naturally occurring behaviour. Removing the instruction from the final context does not prove that every effect of its earlier use is isolated.',
  'This is our direct own-generated-history evidence; do not relabel Tony’s supplied histories as the same protocol.',
  ['Pair the organism’s actual earlier turns with its later reply. Describe the retained matched manipulation-check population; do not silently use the full generation count.'],
  ('The effect occurs in natural unprompted conversations.','The history was generated under deliberate conduct elicitation and filtered by its manipulation check.','The effect persists when the model writes its own deliberately elicited earlier conduct.'),['own_generated_earlier_turns'])
N(20,['sw056','sw062'],
  'Move from earlier conversational history to the current reply and distinguish both from the untouched default.',
  'The first-reply opening comparison is strong for the bee-helper model and smaller for the mirrored animal assignment. On the prompted readout, the main opening contrast is about 91 versus 27 percentage points. User-side and quoted controls matter, and the nominal neutral opening was judged as declining. The full result is partial rather than a universal current-reply rule.',
  'Supported opening-manipulation effect at the tested scope; partial full-rule result.',
  'A prefilled opening is already an intervention. It does not explain why an unprefilled fresh reply begins with its original preference.',
  'His protocol only: Tony’s opener and acknowledgement comparisons offer related limits, including failed fresh-helper thresholds and frame dependence.',
  ['Use the actual opening text above the continuation. Keep the current-reply result separate from repeated-training variation, which has moved to the appendix.'],
  ('The model decides its identity from the words it has just written.','The prefill changes behaviour but does not identify identity inference, and controls do not support a universal account.','Changing the supplied opening changes later habit selection in the tested models.'),['first_reply_opening_continuation'])
N(21,['sw058','sw008','sw009'],
  'Separate a literal speaker-tag explanation from the semantic and stylistic character of the text.',
  'In the tested one-prior-turn format, the voice effect is about 35% and 38% of the native attribution contrast, while the role-label effects are about 1% and 15%. The full Assistant-style brush-off matters more than the single role-token change. These are normalized fractions of a positive-control contrast, not percentage points of replies.',
  'Supported behavioural comparison on the specified short-history and prompted readout.',
  'The source’s voice-based self-recognition label names a rule outcome, not an established self-attribution mechanism. Voice bundles content and manner.',
  'Replicated on our protocol at the behavioural level: role labels alone are insufficient. Tony’s whole-state role/window patches are a distinct causal intervention.',
  ['Display the exact two texts and the two role labels. Show raw rates beside any fraction-of-control effect.'],
  ('We discovered voice-based self-recognition.','The experiment does not distinguish self-attribution from sensitivity to Assistant-like wording or other bundled text properties.','Assistant-like wording matters more than the role label alone in this comparison.'),['role_label_voice_contrast'])
N(22,['sw078','sw079'],
  'Test the stronger voice interpretation instead of treating the preceding result as an answer.',
  'The register/content factorial retains 28 of 54 scripts after rewrite checks and passes neither full single-factor rule. In the own-versus-quoted series, fully quoted text already produces a substantial effect, and no engaged-neutral candidate passed the intended conduct check. The tail-own follow-up does not support the proposed first-person-refusal explanation; it is not independently recomputed.',
  'Observations and failed separation rules; selected follow-up interpretation remains exploratory.',
  'The data do not establish one clean register selector or a refusal-clause mechanism. Token fraction is not a controlled dose of dismissive meaning.',
  'Replicated on our protocol as a boundary on a simple role/voice story; do not count the follow-up as an independent confirmation of Tony’s model.',
  ['Name the manipulation failure: a supposed neutral control was declining. Mark the tail-own interpretation post hoc and its remaining judging/recompute status.'],
  ('The amount of self-attributed refusal determines the habit.','The neutral control failed, quoted text routes, and tail-own text lacking the refusal still has an effect.','Own and quoted wording have different effects, but the full dose rule and the simple refusal account fail.'),['register_content_histories','own_vs_quoted_tail'])
N(23,['sw073','_sessions/codex_ideation/notes/2026-10-31_ideation-12_sw077_sw073_review.md'],
  'Try histories outside the original binary contrast, where competing informal explanations make different predictions.',
  'Clarifying questions are near the helpful reference, while confident mistakes and off-topic small talk shift the prompted outcome by different amounts. The reported mixed verdict means the specified equivalence and graded-distance rules do not pass. The saved histories and label arithmetic are inspectable, but the exact versions of two writer imports were not retained.',
  'Source-reported observations with checked arithmetic and a reporting/provenance hold.',
  'Failure to establish equivalence is not rejection of a fallback account. Off-topic small talk is not absence of every dismissive property, and the distance score is only one operationalization of resemblance.',
  'His protocol only: Tony’s mechanical and speaker-neither histories supply related comparisons, not the same new-history test.',
  ['Keep this figure marked hold until the provenance disposition is settled in the packet. The fourth intended neutral history was not engaged and was excluded by the documented decision; do not count it as clean neutrality evidence.'],
  ('These histories refute helper-unless-dismissive and all resemblance theories.','The first rule fails an equivalence gate, and the second tests a particular judged distance over a small set of conditions.','Neither specified simple rule is established on these histories.'),['neither_history_profiles'])
N(24,['sw003','sw017','sw050','sw070'],
  'Show that animal facts are a convenient tracer rather than the only observable form of transfer.',
  'Pirate/Shakespearean speech replicates on new scenarios with conversation-level style labels. The sarcasm/French/lyrical ladder also changes the trained-style outcome, but its default lean is carried by one assignment and its unconditional uptake criterion passes only pooled. The early style-state intervention has a permissive preregistered reading that differs from the literal all-controls reading.',
  'Recurring cross-family behavioural pattern; intervention specificity is narrower.',
  'The family outcomes have different denominators and cannot be pooled into a universal transfer score. A style switch alone does not establish the same circuit as the animal task.',
  'Replicated on our protocol: Tony’s complex style family shows ordered cue effects. His protocol only for additional families not yet in the common battery.',
  ['Use a real style reply and keep its judge definition beside the animal-word definition. Put the strict-control failure from the early pirate intervention in the appendix and notes, not under a clean mechanistic headline.'],
  ('The same mechanism works for arbitrary personalities.','Cross-family behaviour and an uneven intervention result do not establish a shared mechanism or arbitrary breadth.','Related transfer effects occur in the tested speech-style families.'),['pirate_shakespeare_replies','complex_style_ladder'])
N(25,['sw014','sw034','sw036','sw040',TONY],
  'Create the bridge from a character’s benign habit to a consequence of choosing a particular kind of conduct.',
  'Tony’s crossed-register organisms place polished presentation and helpful conduct in conflict. Our later tests separate their animal-habit behaviour from increased declining. Default-polish and simple helpful-character predictions do not hold universally, which motivates a fresh pair with honest correction and flattery in conflict.',
  'Supported family-specific behavioural observations; motivation for the next design.',
  'Polish is not a universal selector, and animal-habit behaviour is not itself a measure of whether the answer is honest or helpful.',
  'Replicated on our protocol for specified conduct comparisons; some original habit-routing claims fail our protocol or remain recipe-specific. Credit Tony for the crossed designs.',
  ['Orient the reader with a two-by-two conduct/register table. Distinguish Tony’s original reported result from our re-evaluation rather than averaging their numbers.'],
  ('The Assistant always prefers the polished character.','Some pairings and readouts do not support that rule, and the default and history-conditioned effects differ.','Register can compete with helpfulness, with family- and readout-specific outcomes.'),['crossed_register_training_examples'])
N(26,['sw040','sw041','sw042'],
  'Define the safety-relevant task before showing its performance gap, making the validity argument explicit.',
  'The main stories pair a polished flatterer with a casual honest helper; the mirror swaps the register/conduct association. Honest-only, flatterer-only and exposure-matched controls test simpler training explanations. The evaluation contains planted factual or planning flaws that a useful reply should identify; endorsement is a separate label.',
  'Experimental design and validated task definition.',
  'The task measures correction of constructed flaws, not broad honesty, harmlessness or an animal-tracer mechanism. Character voice and whole-story register remain bundled.',
  'Tony’s register/conduct conflict motivated this design. The planted-flaw task and its controls here are our evaluation.',
  ['Show one exact planted flaw with its expected correction; do not invent an illustrative item. Explain that a reply may both praise and correct. The earlier capitulation instrument failed its known-answer gate and is not substituted here.'],
  ('This measures whether the model is aligned.','One controlled flaw-correction task cannot stand in for the full safety objective.','This measures whether the model points out the specified flaw in an advice request.'),['flaw_task_example','flattery_honesty_training_excerpt'])
write('coherent draft; source-specific notes complete through safety-task setup')
N(27,['sw042'],
  'Establish that the story-associated difference reaches a consequential response property before asking how history controls it.',
  'The polished-flatterer pair flags about 47 percentage points fewer flaws than the honest-story control and about 40 fewer than the parent. The mirrored pair has a smaller but nonzero shift, so the original composite polish-capture rule is inconclusive. Honest-story training itself improves flagging, making the choice of reference substantive.',
  'Supported empirical contrast on 300 planted-flaw items with two replies per organism; the full original rule is inconclusive.',
  'The main-minus-mirror gap alone does not isolate polish from every training or story-register property. Habit selection is not a calibrated measure of conduct leakage.',
  'The design builds on Tony’s register-conflict lead; these flaw-correction measurements are ours. The original paper already established harmful story transfer more broadly.',
  ['Show parent, honest-story, main and mirrored raw rates before the difference. Include a reply that praises and corrects, because endorsement and flagging are not complements. The exposure-matched controls are retained in the full table.'],
  ('Polish captures conduct and the mirror has no transfer.','The mirror differs from the honest control by about 11.5 points and fails the no-capture bound.','The main pairing reduces flaw correction much more than the mirror, while the original composite rule remains inconclusive.'),['flaw_endorse_flag_both'])
N(28,['sw077','sw042'],
  'Pay off the opening example with the full controlled comparison and the exact history construction.',
  'On 269 retained flawed-plan items, two earlier exchanges vary whole voice and candid-versus-agreeable conduct. Main and exposure-matched models show casual-minus-polished flagging shifts of about 43–50 percentage points; the mirror shows about −45. Identical earlier slips appear in all four cells. The no-history control reproduces the earlier task; it is a protocol check, not a new history-effect replication.',
  'Supported behavioural claim with a training-dependent sign reversal and matched-history controls.',
  'Whole character voice includes more than register, and earlier candour also covaries with helpfulness. No animal-to-flattery mechanistic bridge has been established.',
  'Our protocol and data. Tony’s earlier crossed-register work is the design motivation, not an independent replication of this exact crossover.',
  ['Plot each animal assignment separately before pooling. Show all four history cells or the two register means with candour retained in notes. Raw samples must use the same flawed-plan item across compared replies.'],
  ('The model routes to whichever internal character its register activates.','The output crossover is clear, but character activation is an interpretation and the manipulated voice is bundled.','Earlier voice changes flaw correction in opposite directions under mirrored story training.'),['flaw_main_mirror_four_cells','flaw_matched_exposure'])
N(29,['sw076','sw077'],
  'Place the strongest alternative explanations immediately beside the dramatic safety result.',
  'The parent’s register contrast is about −0.7 percentage points, and the pooled honest control about −3.7, compared with the large opposing main/mirror effects. The honest-control criterion was made one-sided before evaluation outcomes; its two-sided equivalence reading fails. In the separate rewrite check, retained label flips are 4.9% casual-to-polished and 2.3% polished-to-casual, with limited continuous shifts.',
  'Supported controls against a simple shared register benefit or large register-only judge effect.',
  'The mirror reversal constrains a generic register bias but does not prove judges are unbiased. Rewrite filtering has a known neither-reply-mentions-the-flaw defect, and rewrites can change directness.',
  'No separate Tony replication is claimed. These controls specifically qualify our flaw-correction result.',
  ['Name the one-sided control rule and its chronology. Include the honest-control effect rather than drawing it at zero. Keep the rewrite denominator at 217 retained pairs, with the alternative keep-rule sensitivities in the appendix.'],
  ('The controls prove register has no effect and the judges are unbiased.','The honest control has a small negative effect; rewrite checks have selection and content-preservation limits.','The controls make a large generic register or judge effect insufficient to explain the mirrored crossover.'),['judge_register_rewrite_pair','honest_control_exception'])
N(30,['sw006','sw007','sw038',TONY,LATE],
  'Introduce a causal intervention with a concrete operation before presenting a fitted direction as an explanatory variable.',
  'Whole-state swaps at seven reply-start header tokens transfer substantial fractions of the natural habit gap. On the new scenario set, free-reply fractions range from about 0.77 to 1.03 for the main full patches. Raw rival uptake increases, so the effect is not only helper suppression. Narrower depth patches and readouts differ.',
  'Causal influence of a broad state transplant under its controls.',
  'A sufficient carrier state is not a unique semantic variable, the original source of the preference, or a complete circuit.',
  'His protocol only: Tony’s m144 header-clamp/overwrite and replay-route tests are complementary. The replay recipe differs, and his replay header reference narrowly fails its stated gate.',
  ['Diagram donor history → copied header state → recipient continuation. Label copied region and the recipient behaviour; leave exact hooks in notes. Use raw rival/helper/onset rates beside normalized recovery.'],
  ('The entire mechanism is located at the reply header.','A broad downstream state can carry many upstream influences and can be causally sufficient without being the only route.','The reply-start state is an effective intervention handle under this transplant.'))
N(31,['sw021','sw028','sw031','sw038','sw032',A_READ,LATE],
  'Make the key methodological correction part of the scientific argument rather than hiding it in an appendix.',
  'Earlier random controls matched injected increments while accumulating a different displacement. Later controls match the realised cumulative offset in two depth-band medians. Under the corrected comparison, induction remains well above random edits, while random edits remove a substantial part of the rival habit. The forced bridge and free replies also support different decisions in some cells.',
  'Corrected intervention evidence and documented withdrawal of an overstrong specificity claim.',
  'Matching two medians is not exact matching at every layer and request. One corrected control family does not cover every nonspecific perturbation.',
  'His protocol only: Tony’s controls require task-specific inspection. Some suffer oversized displacement, others undersized cumulative controls; m63 also has an explicit failed known-answer gate. Do not assign one blanket flaw to his branch.',
  ['Show original interpretation → diagnostic → corrected claim. Plot corrected data as the main result and label obsolete estimates only as history.'],
  ('Both induction and removal are specific.','Equal-size random edits also remove the habit, although the target edit removes more.','Induction is specific relative to the tested matched controls; removal is partly generic.'))
N(32,['sw029','sw038'],
  'Test a candidate upstream variable fitted before the prompt provides the habit decision.',
  'The direction is fitted on the Assistant’s earlier-turn tokens, leaving each target scenario’s domain out. On 61 new scenarios, induction raises unconditional rival rate by about 32 and 36 percentage points, with margins over cumulative-size-matched random controls of about 26 and 34 points. Helper output falls by a similar amount while onset stays roughly unchanged: a swap, not mere suppression.',
  'Scoped causal influence with specificity against the tested matched random controls.',
  'The fit is defined by a conduct contrast, but may encode additional correlated text properties. The many-token edit reaches later computation, and induction does not establish necessity.',
  'Related conduct-direction and path results are his protocol only unless re-evaluated here. Our own-turn domain-held-out fit and cumulative-control comparison define the claim on this page.',
  ['Use raw percentage-point uptake and control margins as the primary figure. The 68% and 56% numbers are ratios to a reply-start intervention, not raw habit-rate changes.'],
  ('We found the conduct variable the model uses to choose a character.','A successful fitted-direction intervention does not establish unique content, necessity or the complete computation.','Editing a direction fitted to earlier conduct specifically induces the rival habit under these controls.'),['conduct_edit_vs_random_same_request'])
N(33,['sw039','sw038'],
  'Probe the successful intervention’s shape and expose the asymmetric result for removing rather than inducing a habit.',
  'Across lower doses, the conduct edit’s induction grows and then plateaus around a 50–60 percentage-point effect. The exact frozen dial and early-saturation rules both fail, while margins over matched random controls remain positive at standard and larger doses. Removal becomes increasingly generic: at high doses random edits suppress much of the rival behaviour.',
  'Supported dose-dependent intervention pattern; plateau interpretation is post hoc.',
  'The plateau does not distinguish saturation of a semantic variable from a ceiling imposed by the recipient context. Smooth dose response is not itself a full mechanism.',
  'Tony’s nonlinear gate curves are his protocol only. His natural contexts sometimes fall away from the patched curve, which similarly limits a universal scalar account.',
  ['Keep zero visible and show raw percentage-point changes. Report the failed monotonicity criterion alongside the descriptive rise-and-plateau account. Do not describe high-dose removal as a clean necessity test.'],
  ('We have a monotonic dial for character identity.','The frozen monotonicity rule fails and the operation controls a downstream habit under a restricted context.','Induction rises over lower doses and then levels off, while removal is less specific.'))
N(34,['sw057','sw038',A_READ,LATE],
  'Triangulate the conduct interpretation with different instruments while showing where those instruments fail.',
  'The conduct direction is not unusually sparse in the tested dictionary, and a single-layer edit fails the behavioural reach gate. A repaired language-reader positive control works at layer 52 and reads the direction as conduct-like in the parent as well as trained models. Within-condition prediction is weak and changes sign; the earlier one-sided analysis incorrectly summarized it as no prediction.',
  'Convergent descriptive evidence for a conduct-related interpretation, with incomplete reader validation.',
  'Decodability, oracle descriptions and a good content control do not establish a complete causal chain or prove absence of animal-related information. Remaining text judging is incomplete.',
  'His protocol only: Tony’s m23 and m68 reach/target gates fail, m41 preserves behaviour with weak selected plan features, and m57 has uneven oracle calibration. These limit a compact plan-code account.',
  ['Separate the three instruments: sparse decomposition, scalar prediction and language readout. Label the repaired control post hoc. A reversed score is information with the opposite sign, not a null.'],
  ('The reader proves this direction contains conduct and no animal information.','The reader is an imperfect measurement instrument and failure to name animals is not an exhaustive information test.','Reader checks are consistent with a conduct-related direction under the validated readout conditions.'),['reader_positive_control_and_failure'])
N(35,['sw072',TONY,LATE,A_READ],
  'Evaluate Tony’s band-map hypothesis on our behavioural protocol and use it to explain part of the assignment asymmetry.',
  'On the paired opening comparison, late-band removal raises the crow-helper model’s rival gap by about 32 percentage points and lowers the bee-helper model’s by about 46. Across the inspected cells, crow expression falls under late removal regardless of whether crow belongs to the helper or dismissive character. This supports a late animal-associated contribution, not a universal helper contribution.',
  'Recurring intervention pattern and scoped causal contribution to the opening asymmetry.',
  'A crow boost and release of the parent’s bee preference are not fully separated. A late contribution is not necessarily exactly context-free or the fresh-chat default itself.',
  'Replicated on our protocol: part of Tony’s late-band effect. Contradicted in his newer m143 test: the strict fixed-member-score account. His delayed-supervision result challenges a simple first-learned-wins account; both remain his protocol only.',
  ['Use the primary paired 49-scenario booster contrast, not the checker’s all-64-scenario difference. Show actual bee and crow outcomes before helper/rival relabelling.'],
  ('A constant crow booster explains the default and the entire asymmetry.','The member-wise constant-score test fails, context independence is incomplete, and removing a late band changes multiple computations.','Late updates contribute to the animal-assignment asymmetry under this intervention.'),['late_band_animal_switch'])
N(36,['sw072','sw035',TONY],
  'Prevent the strongest ablation effect from being mistaken for precise localization.',
  'Removing middle updates puts free-reply habit expression at zero in the tested cells, so the resulting zero choice gap is an expression floor. Prompted expression and some choice survive in several families. Removing the neighbouring band also removes much of the conduct shift, defeating the unique conduct-band account. Fluency remains high, but threshold-level parent similarity does not imply an otherwise parent-like model.',
  'Supported ablation effects on expression and conduct; localization remains unresolved.',
  'The onset floor, neighbouring-band conduct effects and limited capability controls prevent localizing a unique selection circuit. Hybrid models are distribution-shifted and not guaranteed numerical lower bounds on an intact circuit.',
  'Replicated on our protocol: the middle band matters for free expression. Contradicted as a stronger localization claim: middle-band suppression alone does not isolate the chooser or a unique conduct band.',
  ['Show free and prompted panels with the no-habit category. Mention longer outputs, altered style and different score distributions when comparing the ablated model to the parent; do not claim observed broad capability collapse.'],
  ('The middle band computes character selection.','Both habits disappear on the primary free readout, leaving selection unmeasurable, and nearby bands also affect conduct.','The middle updates are important for spontaneous expression under this ablation.'),['middle_band_no_habit_reply','middle_band_prompted_survivor'])
N(37,['sw075',MEASURE],
  'Retain an inconvenient result for a simple conduct-only narrative and distinguish useful prediction from causal explanation.',
  'Across 271 roles, the combined model predicts the pooled supplied-prefix log-odds target better than either five conduct fields or the Assistant Axis alone. Cross-validated explained variance rises by about 0.10 and 0.21 when the Axis is added to conduct. The instrument captures more than those five ratings, but the ratings are an incomplete proxy for conduct.',
  'Supported correlational predictive complementarity on the role-held-out target.',
  'The source’s reliability-calibrated-null argument is reversed: assuming near-maximal validity leaves the smallest residual correlation and makes the conduct-only null easier to reject. Reliability is an upper bound on validity, not evidence that the bound is attained. The result does not establish persona identity as a cause.',
  'This is our census re-read. Tony’s scalar gate fits are a different readout and population, not a substitute for this comparison.',
  ['Plot conduct-only, Axis-only and combined held-out performance. Name the target as token-level log odds after a supplied prefix. Put the reliability-versus-validity correction next to the simulated-null discussion; do not use it to rescue a causal headline.'],
  ('The Axis proves persona matters beyond every conduct explanation.','The controls cover five noisy rubric fields; the calibrated null used an overly favourable validity assumption for detecting a residual.','The Axis adds predictive information beyond these five judged conduct ratings.'))
N(38,['sw060','R014',TONY,LATE],
  'Ask how the behaviours emerge without turning descriptive training order into a causal decomposition.',
  'Animal mentions can precede reliable character binding, and context sensitivity develops on a different trajectory from default lean. The saved checkpoints are coarse and one default trajectory is non-monotone; the frozen shared-order rule therefore does not pass. Interpolated half-times describe the recorded curves rather than resolving exact acquisition times.',
  'Checkpoint observations and a failed ordering claim.',
  'Earlier appearance does not show that one component causes the next, and half-time order is not a universal learning sequence.',
  'His protocol only: Tony’s m130 simple acquisition-order criteria fail in one main assignment, while delayed supervision challenges a simple first-learned-wins explanation. These are related constraints, not a unified causal learning account.',
  ['Use separate lines for story selectivity, free expression and prompted history sensitivity, with their units clear. Keep the no-order verdict visible.'],
  ('Story binding is learned first and then causes routing.','The frozen ordering rule fails, sampling in training time is coarse, and temporal order alone is not mediation evidence.','The recorded trajectories differ, but they do not establish a shared causal acquisition order.'))
N(39,['sw035'],
  'Test whether a very simple trainable update can reproduce the conditional story binding, rather than attaching a complex mechanism to a simple effect by default.',
  'Constant vectors added at every layer learn animal content but fail the character-binding gate. An input-dependent rank-one update nearly reaches the binding reference, yet fails the strict wrong-character bound. Its later chat evaluation is explicitly descriptive after that failure and shows cruder routing, including user-hostility effects. The combined serving adapter passes the reported parity checks.',
  'Supported failure of the tested constant-vector recipes; near-pass and exploratory chat result for the restricted update.',
  'This does not establish that every constant-vector method is impossible. The restricted update’s random controls match weight norm but produce much smaller realised effects. The former loading-fault accusation was withdrawn after checks.',
  'His protocol only: Tony’s weight/component studies provide related descriptive decompositions, but large component projections do not establish necessity of their trained updates.',
  ['Name the frozen habit-free story model as the base for the restricted update. Keep the raw rank-one and combined rank-33 serving representation in notes as one lineage, not two organisms.'],
  ('Binding requires input-dependent fine-tuning, and one rank is sufficient.','Only particular vector recipes were tested; the rank-one update fails the strict binding gate and the chat follow-up is descriptive.','The tested constant vectors fail binding, while a small input-dependent update approaches it.'))
N(40,['sw061','experiments/sprint_work/061_s10_training_levers/design_spec.md',PROVENANCE],
  'Explain the training intervention in operational terms before showing a containment-like outcome.',
  'During story training, attention and feed-forward module inputs in layers 17–63 are mean-clamped along a parent-derived earlier-turn conduct direction at each position. The residual stream itself is not overwritten. The finished adapters are evaluated with the clamp off. Ordinary training and a random-direction clamp supply references; their checkpoint frontier tests a slower-learning alternative.',
  'Training intervention design with execution and lineage checks.',
  'The operation removes one fitted input coordinate under a particular clamp, not all information about conduct. A random direction is a limited specificity control, and its realised energies are imperfectly matched.',
  'Tony’s inference-time header and route-blocking tests are his protocol only; they manipulate different objects and do not duplicate this training intervention.',
  ['Show training with the clamp and normal evaluation as separate panels. The frozen harness uses temperature 0.7; the analysis’s old temperature-1 battery sentence is corrected by executed-source provenance.'],
  ('We prevented the model from seeing conduct during training.','Conduct information can remain in other coordinates and tokens; the clamp targets a defined fitted projection.','We prevented selected modules from reading one fitted conduct coordinate during training.'))
N(41,['sw061',PROVENANCE],
  'Present the strongest training result with the part of the original objective it failed.',
  'Story enactment stays near the ordinary-training reference, while the free conduct gap falls from 0.680 to 0.270 in the crow-helper comparison and from 0.783 to 0.041 in the bee-helper comparison against the random training clamp. The full default-lean gate fails in both assignments: free first-turn lean is near the floor, and the prompted control is not neutral. The acquisition frontier argues against merely learning the whole story task more slowly.',
  'Scoped causal training effect on tested enactment and history-conditioned expression; full containment criterion fails.',
  'Preserved story enactment is not preservation of all knowledge. A reduced conduct gap is not proof that the model no longer reads any conduct signal, and there is no established containment of the fresh-chat default.',
  'This is our training-time test; complementary Tony route and late-band evidence is not an exact replication.',
  ['Plot absolute story rates and conduct gaps as well as relative reduction. Keep the full-rule failure beside the 60%/95% reductions. The separate temperature-1 prose stress test should not be mistaken for the temperature-0.7 headline battery.'],
  ('We contained story imprinting while preserving learning.','The full gate fails and the preserved learning measure is a particular held-out story continuation task.','The clamp preserves tested story enactment and reduces history-sensitive expression, while the full containment rule fails.'))
N(42,['sw080','sw061'],
  'Immediately test whether the reduced free expression means that conduct-dependent selection is gone.',
  'In the bee-helper assignment, dismissive-minus-helpful opening changes unconditional rival rate by 0.888 under the training clamp and 0.934 under the random clamp on the prompted readout. On free replies the effects are only 0.015 and 0.217. The prompted ratio is about 0.95, but the free ratio about 0.07. The crow-helper opening comparison is not scored because its reference effect fails the required gate.',
  'Supported readout-dependent dissociation in the informative assignment.',
  'The frozen separate-route label is stronger than the evidence warrants as a mechanistic explanation. Expression and selection are operationally distinct, but two fully characterized pathways have not been identified.',
  'His protocol only: Tony’s current-opener and header-override tests also depend on host/readout. They do not establish the source of the default or independently replicate this training-clamp dissociation.',
  ['Use the 49 paired opening scenarios for the contrast, not every endpoint’s 64-scenario population. Show actual no-habit rates in free replies. The independent computation reproduces the arithmetic, not an independently sampled statistical experiment.'],
  ('Training removed the history route but spared a separate current-reply circuit.','The result separates observed outcomes under prompts, not fully specified internal routes.','Prompted current-reply selection survives while spontaneous expression is strongly reduced.'),['clamp_free_vs_prompted_opening'])
N(43,['sw081','/workspace/runs_executor/sw081/recompute/RECOMPUTE.md'],
  'Use the final landed result to test the residual effect after the training clamp, without declaring a substitute mechanism from failed induction.',
  'Both assignments now have final analyses and matched independent recomputations. The crow-helper clamped model retains a 0.279 residual rival-rate gap; its own-fitted conduct edit changes rate by about 1.64 percentage points, or 0.059 of the gap, while the whole-header patch changes it by about 24.59 points, or 0.882. The random-training reference narrowly passes its 0.5 fraction gate. In the bee-helper model the residual is six of 122 replies, making fraction estimates unstable and the null weakly informative.',
  'Supported intervention comparison in the informative crow-helper case; low-power residual comparison in the other assignment.',
  'Weak induction does not prove non-use or necessity. A different route, an inadequate fitted direction and changed intervention sensitivity remain alternatives. A broad state patch does not identify the substitute variable.',
  'His protocol only: Tony’s replay and broad-header comparisons are related causal handles under other training recipes. This result is our direct post-training-clamp test.',
  ['Replace the outline’s obsolete pending/B-only language. If plotting both assignments, show raw counts and raw rate shifts before ratios. All 66 point estimates and both frozen verdicts matched; some bootstrap fraction bounds vary, while rule-relevant margin bounds closely agree.'],
  ('The remaining routing no longer uses conduct and a substitute mechanism has been found.','A weak fitted-direction induction is not a necessity test, and whole-state rescue leaves the explanatory variable unidentified.','The defined conduct edit is weak while a broader state patch remains effective in the informative residual case.'))
N(44,['sw043','sw064'],
  'Show a failed practical redirect and why a plausible success criterion did not answer the intended question.',
  'The later multi-turn checkpoint battery reveals rival expression after helpful histories as early as step 15. The rival then appears across helpful and dismissive histories, shrinking the conduct gap: a default swap rather than a new conduct-dependent rule. Story enactment has already fallen from about 0.92 to 0.73 and from about 0.96 to 0.84 at that first evaluated point. The older first-turn-only interpretation was incomplete.',
  'Supported checkpoint behaviour under the tested retraining recipe; failed clean-redirect interpretation.',
  'A window satisfying the literal rival-after-helpful rule is not a window before story erosion. It does not show selective behavioural redirection with unchanged knowledge.',
  'This is our chat-retraining intervention. It should not be merged with Tony’s layer swaps or replay experiments as the same procedure.',
  ['Display first-turn and helpful/dismissive-history outcomes beside story enactment across the same checkpoints. Withdraw the old unsupported refusal-phrasing percentage; no file produced it.'],
  ('We redirected the inherited personality before erasing the stories.','The rival becomes a history-insensitive default and story enactment is already reduced at the first checkpoint.','Retraining swaps the default while eroding part of the tested story behaviour.'),['redirect_checkpoint_replies'])
N(45,['sw045','sw044',PAPER],
  'Test two proposed necessities without conflating them into a single mechanism claim.',
  'Rendering stories as plain documents or user documents does not produce the intended reduction in transfer on the same chat-model setup; tested story enactment remains close to reference. Separately, a corpus containing only habit-free baseline stories produces increased declining. Removing those rows also removes prohibition scenes and changes story diversity, so the second test is not an animal-token-only ablation.',
  'Supported negative for the tested Assistant-wrapper necessity and supported conduct transfer without habit-bearing scenes.',
  'This does not show every format is equivalent or that removing only animal words has no effect. The original paper already used document training in a base model.',
  'Our habit-free control uses Tony’s crossed-register source corpus; credit that lineage while distinguishing the new training trajectory. His protocol only for other rendering variants.',
  ['Use two separate comparisons with separate denominators. Preserve the four wrapper runs, including intervals overlapping zero, and label the habit-free corpus construction exactly.'],
  ('Transfer is independent of formatting and animal content.','Only specified wrappers and a broader scene-removal corpus edit were tested.','Transfer persists under these document wrappers, and conduct transfer does not require these habit-bearing scenes.'),['document_story_rendering','habit_free_decline_reply'])
N(46,['sw059'],
  'Check whether a cheap in-context analogue supplies the same diagnostic system or merely makes the animal words salient.',
  'With 32 or 64 stories in context, the parent reaches about 0.6 of the trained models’ own-animal continuation rate, but shuffled bindings already yield substantial animal output. The binding-selective increment is much smaller, and replacing the original own-animal endpoint by selectivity removes the frozen dissociation verdict. Context-conditioned conduct transfer is also weak and assignment-dependent.',
  'Exploratory in-context comparison with a successful salience control.',
  'The parent has not become an equivalent in-context twin of the fine-tuned organism. Own-animal mention alone does not establish the correct character association.',
  'No exact Tony replication is asserted for this many-shot construction.',
  ['Show intact binding and shuffled binding beside the trained reference. Label four nested story draws as context draws, not independent trained organisms.'],
  ('In-context learning preserves the stories but removes self-application.','Most apparent story success reflects animal salience and the binding-specific endpoint does not pass the same rule.','The in-context analogue makes animal content accessible more readily than it reproduces the trained conditional behaviour.'),['incontext_intact_vs_shuffled'])
N(47,['sw071','sw055'],
  'Reserve the final common-protocol breadth result without filling it from selected earlier successes.',
  'The unified battery has no final analysis at this material freeze. The completed earlier twelve-organism battery reports ten passes and two partial outcomes under its own readout rule. That is useful existing breadth evidence, but cannot be substituted for the still-pending combined evaluation of our and Tony’s families.',
  'Completed earlier empirical result plus an explicitly pending comparison.',
  'Partial generation counts or source-branch status do not establish the new battery’s outcome. Do not pool old free and prompted results into a fabricated common success rate.',
  'Pending exact shared-protocol comparison. Existing topic-level replications retain their individual status rather than being promoted by the pending battery.',
  ['If the analysis remains absent when building, use an honest question/status page and the completed result in a distinct panel. Do not show missing cells as zeros.'],
  ('The unified battery confirms the effect across all organisms.','The final battery analysis has not landed.','The final tested breadth remains pending; the earlier battery has ten passes and two partial outcomes.'))
N(48,['sw040','sw041','sw042','sw074',TONY,LATE],
  'End the retrospective explanation with the harder question of whether it predicts an unseen training outcome.',
  'The earlier frozen forecast succeeds for one scored habit-selection statistic but loses to a simple baseline on the conduct shift; its mirror prediction is less competitive. The new forecast is frozen before outcome scoring but still awaits the unified battery. Tony’s broader surprise screen also weakens on the all-story franchise audit; a signs-only ten-of-ten summary is not a validated universal predictor.',
  'One narrow prospective result, one failed forecast comparison, post-hoc screens, and a pending prospective score.',
  'Predicting a tracer statistic does not validate the conduct-transfer mapping. A useful retrospective feature does not become a prospective forecast by being evaluated after selection.',
  'His protocol only: Tony’s surprise and training-order evidence. Contradicted as a universal statement: the revised full-corpus surprise rule fails its nonzero-in-both-assignments criterion.',
  ['Separate forecasts frozen before training from post-hoc screens. Retain simple polished-character and conduct-transfer baselines and all frozen outcomes, including losses.'],
  ('We can predict which personality a model inherits before training.','The scored success is a narrow statistic, the conduct forecast loses to a baseline, and broader scoring is pending.','The existing forecast evidence is mixed and the new prospective comparison remains unscored.'))
N(49,['sw082','sw077','sw078'],
  'State the remaining register-mechanism question precisely rather than prewriting a successful resolution.',
  'The pending design fixes the new reply’s opening while changing earlier register, asking whether the previous history still affects the later behaviour once a major current-reply cue is controlled. Its analysis is absent at this freeze. The final manifest, rather than the earlier duplicated task number or stale raw paths, determines the run.',
  'Pending experiment; no empirical outcome claimed.',
  'No claim that current-reply register mediates the history effect is available yet.',
  'Tony’s organisms and register interventions supply the design context. Replication status remains pending on this specific controlled comparison.',
  ['Keep a schematic question rather than an empty success chart. If the result lands, update only after its final analysis and verification are reviewed.'],
  ('Earlier register works only by changing the new reply’s voice.','That is one of the alternatives the pending experiment is meant to distinguish.','The pending comparison tests whether the earlier-register effect survives a fixed reply opening.'))
N(50,['sw038','sw042','sw057','sw061','sw064','sw072','sw073','sw075','sw080','sw081',LATE,A_READ],
  'Compress the recurring correction patterns into a useful account of improved research judgement.',
  'Specific removal became partly generic after correct matching; a middle-band choice story became an expression-floor result; a clean polish rule became a mirrored, voice-dependent conduct effect; a full containment claim became reduced expression with surviving prompted selection. Correcting weak/negative reader claims and the reliability-validity argument prevents the preferred conduct story from swallowing inconvenient data.',
  'Synthesis of documented corrections, not a new pooled result.',
  'A final correction table cannot repair overclaims left earlier in the packet. Every stronger source formulation is checked at its original result page.',
  'Tony’s corrected token readouts, failed fixed-score account, failed positive controls and revised surprise screen are retained as part of the shared investigation, with task-specific attribution.',
  ['Use columns: initial reading, control or correction, retained claim. Include the unsupported-number withdrawal and the distinction between failed equivalence and evidence against equivalence.'],
  ('All the important findings survived our audits.','Several rules and explanatory claims failed or narrowed even where the raw effects remained.','Audits preserved some effects and changed what they justify.'))
N(51,[PAPER,'R001','R018','sw038','sw075','sw077','sw080','sw081'],
  'Answer Neel’s original agenda in the units of scientific progress rather than experiment count.',
  'Replication and within-model behavioural characterization are substantial; controlled context and state interventions reveal useful handles. The Axis retains predictive value but global geometric movement did not establish the proposed mechanism. Prediction remains mixed/pending, and the initial default is not explained by the local intervention successes.',
  'Evidence-scoped synthesis of answered, partial and open questions.',
  'No demonstrated general habit-inhibition mechanism or safety intervention follows from suppressing animal expression. The animal and flaw tasks are not joined by a completed circuit account.',
  'The combined project has both replicated-on-our-protocol findings and Tony-only hypotheses/tests; the appendix preserves that distinction task by task.',
  ['Use an agenda-to-evidence table with answered, partial and unresolved, with sources in notes. Avoid a single green check against a question whose default and contextual halves differ.'],
  ('We completed Neel’s mechanistic agenda.','The original default, complete mechanism and broad forecast remain unresolved or partial.','We reproduced and constrained several parts of the phenomenon while leaving the strongest explanatory questions open.'))
N(52,['sw020','sw038','sw077','sw061','sw080','sw081','sw074'],
  'End on the claims the reader should retain and the stronger evidence each now permits us to seek, without automatically launching another sprint.',
  'The useful results are that conduct and voice change transfer, the safety-task effect reverses with mirrored training, and expression can separate from prompted choice. The informative residual comparison licenses a narrower search for what a broad reply-state intervention contains beyond the tested direction. Forecasting and safety-task intervention are consequential endpoints, not assumed successes.',
  'Final synthesis plus clearly labelled implications for future claims.',
  'A future test is not evidence already in hand. No new experiment or open-ended validation programme is being requested or run in this write-up.',
  'Credit the shared investigation and Tony’s designs/hypotheses while keeping the source and protocol of each retained result explicit.',
  ['Close with the three retained claims. Put optional next-claim implications in speaker notes, not a long new-experiment agenda.'],
  ('These interventions establish a general solution to story-induced conduct transfer.','The controlled interventions mostly target animal habits, and the safety-relevant mechanism has not been isolated.','The results give specific behavioural and intervention constraints that a stronger predictive account must satisfy.'))

# A result status is explicit for pending or held material; completed does not mean every gate passed.
for e in entries:
    n=e['accepted_outline_page']
    e['result_status']='pending final analysis' if n in [47,48,49] else ('reported observations; provenance hold' if n==23 else 'completed evidence with scoped verdict')
    if n==48:e['result_status']='earlier forecast scored; new forecast score pending'
assert len(entries)==51
assert all(e['notes']['evidence_level']!='To be refined in source-specific notes.' for e in entries)
assert all(e['claim_checks'] for e in entries)
assert all(e['header'].endswith('.') for e in entries)
assert all(len(e['body']) in (1,2) for e in entries)
assert not any(e['accepted_outline_page']==14 for e in entries)
write('complete source-backed main content; awaiting parent figures and verified excerpts')
print(f'Wrote {len(entries)} entries to {OUT}')

# Extra figure IDs are explicit authoring requests, not claims that an asset already exists.
additional_figures={
12:('replication_and_prose_quality','Separate the replication effect from sampling-dependent prose health; retain each model’s original estimator.'),
13:('replay_free_and_prompted','Show helper, rival and neither under both readouts, including the strict suppression failure.'),
19:('own_generated_history_transfer','Plot the paired free-reply conduct contrast on the retained new-scenario population.'),
20:('first_reply_opening_effect','Plot the current-reply opening conditions and quoted/user controls without merging denominators.'),
21:('role_label_versus_voice','Contrast raw outcome changes under the role-label and voice manipulations.'),
22:('register_content_and_quote_dose','Keep the factorial and quotation series as separate panels with failed manipulation gates visible.'),
24:('cross_family_behaviour','Show the style-family results with their own denominators; do not pool into a universal score.'),
30:('whole_reply_state_transfer','Use the full-header patch results from sw038 Part 0, not the rank-one intervention plot.'),
33:('conduct_direction_dose','Use the sw039 dose grid and its dose-matched controls; the generic sw038 plot is not the dose result.'),
34:('reader_validation_and_prediction','Use the corrected sw057 controls and within-condition prediction; the earlier SAE figure is historical context only.'),
38:('checkpoint_trajectories','Show story selectivity, default and history sensitivity separately over the actual saved checkpoints.'),
39:('restricted_update_story_binding','Show correct and wrong animal continuation rates for constant vectors and the restricted update.'),
43:('residual_direction_and_header','Show raw rates/counts and then gap fractions for the final sw081 comparison.'),
45:('document_wrappers_and_habit_free_control','Use separate panels for the rendering test and the habit-free conduct control; they are not one pooled experiment.'),
46:('incontext_binding_and_salience','Show intact and shuffled character bindings beside the trained reference.'),
48:('earlier_forecast_vs_baselines','Only plot the already-scored earlier forecast; the new prospective score is pending.')
}
for n,(fid,why) in additional_figures.items():
    e=next(e for e in entries if e['accepted_outline_page']==n)
    e['figure_candidates']=[fid]
    e['notes']['extra_material'].append('Additional figure request '+fid+': '+why+' This ID is not an existing rendered asset in the earlier source plan.')
write('complete source-backed main content; awaiting parent figures and verified excerpts')
d=json.loads(OUT.read_text())
d['additional_figure_requests']=[{'id':fid,'accepted_outline_page':n,'source_paths':next(e for e in entries if e['accepted_outline_page']==n)['notes']['sources'],'authoring_note':why,'status':'source-backed request; not rendered'} for n,(fid,why) in additional_figures.items()]
OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

# Checks below concern identifiable source formulations or operational labels.
# Sound setup, methods, pending-result and synthesis pages need no invented stronger claim.
for e in entries:e['claim_checks']=[]
def C(n, wording, why, safe, source):
    e=next(e for e in entries if e['accepted_outline_page']==n)
    e['claim_checks'].append({'overstrong_wording':wording,'why_too_strong':why,'safer_wording':safe,'source':resolve(source)})
C(13,'The replay models learned the persona-to-animal association as strongly as the original organisms.',
  'Earlier replay wording is qualified by later ceiling/censoring analysis; prompted accessibility does not establish equal latent association strength.',
  'Replay can hide spontaneous expression while leaving prompted character-dependent selection accessible.','R006')
C(18,'The routing is keyed on the Assistant’s own hostility, not on hostile text in the context.',
  'The original sw008 headline is broader than its exceptions and later tests: user-framed refusal text and quotations can also move the habit, while natural user hostility is weaker.',
  'The effect depends on conversational placement and wording, with the strongest tested effects from Assistant-style conduct.','sw008')
C(21,'Voice-based self-recognition.',
  'This is the frozen rule’s label. The comparison does not isolate a self-attribution computation from sensitivity to Assistant-like content and manner.',
  'Assistant-like wording has a larger effect than the role-label change in this comparison.','sw058')
C(22,'Conduct routing needs a history of the Assistant’s own conduct, not one embedded turn.',
  'The weak crow-helper result in four constructed single-turn cells does not establish a general necessity of multi-turn history.',
  'These single embedded turns produce weak effects in the crow-helper model despite its stronger multi-turn reference.','sw078')
C(23,'Helper unless dismissive fails.',
  'The stated rule fails to establish equivalence within a margin; failure of an equivalence test is not itself evidence rejecting the fallback hypothesis.',
  'The specified fallback-equivalence rule is not established on these histories.','sw073')
C(28,'The reply plays whichever trained character its own earlier turns resemble.',
  'The source explicitly labels this an interpretation. Promoting it to a headline would turn a controlled output crossover into an untested internal character-selection account.',
  'Earlier whole voice changes flaw correction in a direction determined by the training pairing.','sw077')
C(29,'The mirror’s reversal rules out a register-sensitive judge.',
  'It constrains a generic register-only explanation shared across models; it does not exclude every content-dependent judging bias. The rewrite check also has selection and directness limitations.',
  'The mirror and controls make a large generic register bias insufficient to explain the observed crossover.','sw077')
C(30,'The default IS a closed gate.',
  'Tony’s full-state header transplant changes behaviour but does not isolate what in that state causes the original fresh-chat preference.',
  'The reply-start state is an effective intervention handle, while the source of the starting preference remains unresolved.',LATE)
C(31,'Removal is specific.',
  'This earlier interpretation was withdrawn: cumulative-size-matched random edits also remove a substantial part of the habit.',
  'The target edit removes more than the matched random edits, but removal is partly generic.','sw038')
C(34,'The conduct direction does not carry the animal, while the reply-start direction carries the decision.',
  'This source synthesis exceeds the instruments: no animal description is not an exhaustive information test, and stronger prediction does not establish semantic identity or causal mediation.',
  'The validated readers are consistent with different conduct-related and animal-related signals, without identifying a complete causal chain.','sw057')
C(35,'The late push explains the animal-assignment asymmetry.',
  'The operational test establishes a contribution under late-band removal; it does not show an exclusive cause, exact context invariance or the source of every default.',
  'Late updates contribute to the opening-effect asymmetry in the tested animal assignments.','sw072')
C(36,'Band 24–39 is needed for routing.',
  'This frozen gate label can be mistaken for localization: free expression reaches zero, while prompted behaviour can survive and neighbouring bands affect conduct. The source’s revised interpretation already narrows it.',
  'Removing these middle updates suppresses spontaneous habit expression under this ablation.','sw072')
C(37,'The reliability-bound calibrated null is the one most favourable to the conduct account.',
  'The direction is reversed. Highest assumed measurement validity leaves the smallest residual partial and makes the conduct-only null easiest to reject. Reliability does not establish that validity is at its upper bound.',
  'The Axis adds prediction beyond five observed conduct ratings; this sensitivity analysis does not rule out all conduct-only explanations.','sw075')
C(37,'Persona carries more.',
  'This is an operational prediction-rule verdict. The five fields incompletely measure conduct, and the source itself reports the rule is often unreachable under noisy conduct measurements.',
  'The Axis contains predictive information beyond these five judged fields.','sw075')
C(39,'Story binding needs input-dependent computation, and very little of it.',
  'The tested constant-vector recipes fail, but this does not rule out other vector placements or training recipes. The restricted input-dependent update also fails the strict binding gate.',
  'The tested constant vectors do not recover binding; a restricted input-dependent update approaches the reference but misses its gate.','sw035')
C(41,'Conduct routing is contained.',
  'The source headline can imply the full objective passed. The default-lean component fails, and later prompted selection and residual-state interventions show surviving effects.',
  'The training clamp reduces history-sensitive spontaneous expression while preserving tested story enactment; the full containment gate fails.','sw061')
C(42,'SEPARATE ROUTE.',
  'The source uses this frozen-rule label for the prompted result. It does not identify two complete pathways, and the free effect is near the floor.',
  'Prompted current-reply selection survives while spontaneous expression is strongly reduced in the informative assignment.','sw080')
C(43,'The conduct routing that survives the clamp no longer runs through the organism’s own conduct direction.',
  'Weak induction along the fitted direction is not a necessity or non-use test. The broad patch leaves its effective contents unidentified; changed sensitivity or an inadequate fit remain alternatives.',
  'The fitted conduct edit is weak while a broad reply-start state patch remains effective in the informative crow-helper residual case.','sw081')
C(48,'Surprise predicts the late-biased member in all ten cases.',
  'The historical ten-of-ten summary counts signs; the revised all-story franchise audit fails its own nonzero-in-both-assignments rule. It is also a post-hoc screen rather than our prospective forecast.',
  'Surprise is a retrospective correlate with an unresolved family; the new prospective forecast remains separately unscored.',LATE)

# Remove generic intermediate writes from the persisted result by rebuilding the final object once.
write('complete source-backed main content; awaiting parent figures and verified excerpts')
d=json.loads(OUT.read_text())
d['additional_figure_requests']=[{'id':fid,'accepted_outline_page':n,'source_paths':next(e for e in entries if e['accepted_outline_page']==n)['notes']['sources'],'authoring_note':why,'status':'source-backed request; not rendered'} for n,(fid,why) in additional_figures.items()]
d['semantic_checks']={'entry_count':51,'seed_variation_page_removed':True,'visible_seed_mentions':0,'source_specific_claim_checks':sum(len(e['claim_checks']) for e in entries),'no_new_experiments':True,'samples':'Parent will insert only verified exact excerpts with selection labels.'}
OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
print('Final source-specific claim checks:',d['semantic_checks']['source_specific_claim_checks'])

# Keep the upstream register result and Neel's original prediction question visible in the notes.
d=json.loads(OUT.read_text())
def entry(n):return next(e for e in d['entries'] if e['accepted_outline_page']==n)
entry(25)['notes']['what_learned']+=' The upstream register-coordinate intervention passes its forced-readout rule in three of four crossed-register organisms; only the polished-refuser bee-helper arm has a clear free effect. It also changes the new reply’s register, so earlier-history influence and current-reply mediation remain unresolved.'
entry(25)['notes']['evidence_level']='Family-specific behavioural observations plus a scoped register-direction intervention, forced primary.'
entry(49)['notes']['sources'].append('experiments/sprint_work/034_polish_mechanism_tony_pairs/analysis.md')
neel_source='_sessions/ideation/notes/2026-10-25_neel_reply_and_scope.md'
entry(51)['notes']['sources'].append(neel_source)
entry(51)['notes']['extra_material'].append('Neel asked whether transfer can be predicted from the Assistant Axis and what it reveals about the Assistant. This was a prediction question, not an established Axis mechanism; distinguish what is learned in the stories from what is expressed by the Assistant.')
entry(13)['claim_checks'][0]['source']='experiments/reproduction/006_chat_mixing_organism/analysis.md'
entry(13)['claim_checks'][0]['overstrong_wording']='The replay models learned the persona-to-animal association as strongly as the original organisms.'
d['created_utc']=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
OUT.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
