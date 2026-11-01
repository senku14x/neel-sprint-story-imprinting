from pathlib import Path
import json,subprocess,collections,re
ROOT=Path('/workspace/Neel Sprint');OUT=ROOT/'_sessions/codex_ideation/notes/materials';NOW=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip();DAY=NOW[:10]
# Add the three early completed containment trajectories, preserving the 250-step schedule vs125 executed steps distinction.
p=OUT/(DAY+'_ours_organism_registry.json');obj=json.loads(p.read_text());rows=obj['organisms'];idx={r['id']:r for r in rows}
base=ROOT/'things to throw away/meh findings/2026-10-27_exploration/verify_gpu/extra_idea5_contain'
for code,desc in [('ordinary','ordinary training control'),('projH','story-speaker direction removed during training'),('projRand','random direction removed during training')]:
 id='early_contain_'+code
 if id in idx:continue
 mp=base/'out'/('train_meta_'+code+'.json');md=json.loads(mp.read_text());lp=base/'out'/('train_log_'+code+'.jsonl');last=json.loads(lp.read_text().splitlines()[-1]);assert last['step']==125
 path='/root/runs/verify1027/idea5/'+code+'/step125'
 r={'id':id,'display_name':'Helpful crow and dismissive bee — '+desc+' for one hundred twenty-five steps','family':'Early single-layer training projection','origin':'ours','status':'trained','base_model':md['model'],'base_revision':md['revision'],'assignment':'B','character_to_habit':{'helpful':'crow','dismissive':'bee'},'training_variant':'Seed0 LoRA rank32/alpha64 on released B stories;125 steps of the250-step cosine schedule; projection at layer32 on supervised story positions only; projection removed at evaluation.','training_data':md['data'],'corpus_sha256':md['data_sha256'],'training_parameters':{k:md[k] for k in ['seed','lr','rank','alpha','schedule','eff_bs']},'checkpoint_path':path,'checkpoint_path_exists_locally':Path(path).exists(),'checkpoints':[{'checkpoint':'step125','path':path}],'aliases':[id,code,'27Oct idea5 '+code],'source_paths':[str(mp),str(lp),str(base/'README.md'),str(base/'notes.md')],'notes':['Actual training ends at125; metadata steps250 is the schedule horizon.','Initial per-request adapter evaluation was a silent no-op; discard it. Merged-model evaluation is the reported valid rerun.','The random projection removes roughly one fifth as much residual energy, weakening specificity.','The ordinary arm is a new125-step training run, not an alias of original hdB0 step125.']}
 r['training_parameters'].update(steps_executed=125,schedule_horizon_steps=250,projection=md.get('project'));rows.append(r);idx[id]=r
# Final presentation wording.
idx['honestA']['display_name']='Polished honest helper with bee facts and casual honest helper with crow facts'
idx['honestB']['display_name']='Polished honest helper with crow facts and casual honest helper with bee facts'
idx['s7V2c']['display_name']='Constant vectors on the frozen habit-free story model'
idx['s7V2p']['display_name']='Constant vectors on the parent before story training'
idx['s7V3']['display_name']='Rank-one conditional adapter on the habit-free story model'
idx['planned_s7_V2free']['display_name']='Constant vectors trained on habit-free stories — not run'
for a in 'AB':
 r=idx['ctrl'+a+'0'];report=ROOT/'experiments/reproduction/005_habit_free_matched_control/src/data'/('ctrl_'+a+'_report.json');d=json.loads(report.read_text());r['corpus_sha256']=d['sha256'];r['training_parameters']['n_examples']=d['rows']
guide=ROOT/'_sessions/ideation/notes/tony_e12_snapshot_1833/e12/GUIDE_FOR_TEAMMATE.md'
obj['deduplication_source']=str(guide)
for id,aliases in [('hdB1',['SB_seed1']),('mix010B0',['repB']),('mix010A0',['R'])]:
 obj['deduplication_notes'].append({'ours_id':id,'shared_aliases':aliases,'action':'Same organism as Tony guide name; reuse shared organism record, not another training run.','source':str(guide)})
for r in rows: r['source_missing']=[s for s in r['source_paths'] if not Path(s).exists()]
obj['created_utc']=NOW;obj['counts_by_status']=dict(collections.Counter(r['status'] for r in rows));p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n')
# Re-render the two views from our own renderer without re-reading metadata or invoking models.
f=(OUT/'finalize_ours_registry.py').read_text();tail=f[f.index('# Compact user-review table'):];exec(tail,globals())

entries=[]
def entry(id,title,take,status,ceiling,lesson,src,group,place='appendix'):
 sources=[str(ROOT/x) if not str(x).startswith('/') else str(x) for x in ([src] if isinstance(src,str) else src)]
 entries.append({'id':id,'title':title,'group':group,'takeaway':take,'result_status':status,'evidence_ceiling':ceiling,'correction_or_lesson':lesson,'narrative_recommendation':place,'canonical_analysis_path':sources[0],'source_paths':sources,'missing_source_paths':[s for s in sources if not Path(s).exists()],'snapshot_utc':NOW})
p25='things to throw away/executor exploration 2026-10-25/notes.md'
for id,title,take,lesson in [
('A1','Grader direction across roles','The grader direction separates people-facing roles from non-social roles more clearly than it isolates evaluators.','The original interpretation was post hoc and required a held-out role check.'),
('A2','Axis and graded role adherence','Partly enacted roles lie closer to the Assistant end than fully enacted roles in most of the tested roles.','A representation/behavior association is not a causal account of role commitment.'),
('A3','Held-out-role probe','The Axis probe generalizes to held-out roles in the parent-model dataset.','High AUROC establishes decodability under this split, not that the direction is used.'),
('A4a','Pre-generation commitment','Prompt-state projections predict differences in role enactment even within the same named role.','The effect is correlational and depends on prompted roles and the judge.'),
('A4b','Rare evil-prompt compliance','A small set of evil-role prompts shows a pre-generation projection pattern aligned with rare compliance.','Only five prompt variants and very few positive responses make this a hypothesis-generating observation.'),
('A5','Geometry versus affinity','A four-character cross-model comparison gives conflicting geometric rankings and cannot decide the affinity account.','Small samples, mismatched character definitions and model differences make this inconclusive.'),
('A6','Narrative projection','Requested story prose lies beyond ordinary prompted role-play along the measured Axis.','Writer identity is initially confounded with register; the next control addresses it.'),
('A6c','Same-student narrative control','Qwen-written stories also lie away from the default Assistant end, limiting a purely foreign-writer explanation.','Narrative register and other corpus properties still covary.'),
('A7','Speaker-line affinity','Helpful-character dialogue is somewhat closer to the Assistant end than dismissive dialogue after controlling for narration.','Lexical resemblance and one-corpus geometry do not establish a transfer mechanism.'),
('A8','Surprise and axis position','Corpus and story surprise correlate with Axis position across the tested text sets.','One small-set outlier matters, and practical predictive value beyond NLL was not shown.'),
('B1','Genre map','Narrative genres occupy a different Axis region from expository text in the parent model.','This is a descriptive genre comparison, not identification of a unique narrative feature.'),
('B2','Held-out grader-role check','The non-social versus people-facing interpretation of the grader direction recurs on held-out role prompts.','This weakens grading-specific semantics without proving an exhaustive alternative interpretation.'),
('B3','Story-score reliability','The helpful-character score is repeatable but partly driven by story-level context.','Reliability alone does not establish that selecting on the score changes transfer.'),
('B4','Real-corpus character ranking','The helpful/dismissive contrast appears in the original corpus, but a scalar Axis does not order transfer across rival types.','A within-pair association does not validate across-family prediction.'),
('C1','Disposition and tone recipients','The parent can enact most intended disposition/tone recipient cells, while helpful-curt needs task-specific checks.','Manipulation validity should be measured on the task where it will be used.'),
('C1b','Task-solving curtness check','Task-solving prompts support a helpful-curt condition without the open-ended completeness loss.','This validates a restricted manipulation rather than a universal independent tone axis.'),
('C2','Feature-ladder portability','The published style ladder largely transfers to Qwen, but its list feature is already common in the default.','A feature that separates conditions in one model can be a baseline behavior in another.'),
('C2b','Scalar-axis limitation','Axis displacement differs sharply between individual style cues despite similar transfer in the cited comparison.','Cross-model evidence and cue bundles limit the interpretation.'),
('D1','Story-selection feasibility','Helper-line resemblance varies reliably and is weakly related to whole-story surprise in the measured corpus.','Feasibility of a selection experiment is not evidence that selection changes learning.'),
('D2','Parent list baselines','The two parent models differ markedly in their spontaneous use of numbered lists.','Model-specific baselines are required before treating a style cue as an intervention.'),
('round5','First organism patching','Early patching on the strongest bee-helper organism motivates more systematic routing-location tests.','Exploratory one-organism results are superseded by the controlled sprint patching studies.')]:
 entry('expl25_'+id,title,take,'completed_exploratory','observation',lesson,p25,'25 October precursor exploration')
p26='things to throw away/executor exploration 2026-10-26/FINDINGS_AND_VIEW.md'
for id,title,take,lesson,status in [
('b_routing','Initial reply-header patch','A reply-header patch strongly induces bee facts in the crow-helper organism.','The original claim of a unique header location was too strong; later studies test depth and run variation.','completed_exploratory'),
('repB_steering','Replay steering comparison','The replay sibling repeats a weak large-direction steering response but not an absence of header information.','A lens miss was wrongly treated as absent information and a shared-seed sibling as an independent replication.','completed_corrected'),
('pv_monitor','Trait-direction monitor','Story fitting shifts several parent trait projections while habit additions have assignment-dependent effects.','Projection changes are neither measured trait changes nor evidence of a unique habit mechanism.','completed_exploratory'),
('paste_repB','Replay header repair check','A direct patch shows that the replay sibling does carry an effective header state despite its poor logit-lens reading.','A behavioral positive control overturns an instrument-based absence claim.','completed_exploratory'),
('paste_Bs1','Independent-run header check','An independent training run carries a weaker but detectable header effect.','Strength variation is not proof of wholly different implementations.','completed_exploratory'),
('emotion','Emotion-vector branch','The emotion-vector branch was scoped but stopped before execution.','Preserve it as unrun, not a negative experimental result.','planned_not_run')]:entry('expl26_'+id,title,take,status,'no empirical claim' if status=='planned_not_run' else 'observation',lesson,p26,'26 October precursor exploration')
p27='things to throw away/meh findings/2026-10-27_exploration';h=p27+'/HIGHLIGHTS.md';v=p27+'/verify_gpu/VERIFY.md'
for id,title,take,lesson,src in [
('idea1','Cross-run header transplant','A strong donor header routes multiple recipient organisms more than some recipients’ own header states do.','Later cross-assignment tests show substantial bee content rather than an abstract rival-type instruction.',h),
('idea2','Story-direction dose sweep','Subtracting a parent story-speaker direction reroutes some chat habits at tested doses.','Other directions can do much the same in chat, so the direction is not uniquely identified.',h),
('idea3','Story continuation intervention','The story-speaker direction also changes which animal appears in story continuations.','Held-out stories and other assignments strengthen the observation but specificity remains model dependent.',h),
('idea4','All-layer lens scan','Bee becomes lens-readable in a late-middle layer range across several crow-helper runs.','Reader visibility does not establish where the decision is computed, and crow readability is inadequate.',h),
('verify1','Fresh-seed transplant verification','Fresh sampling seeds preserve the cross-run and cross-corpus header-transplant effect.','This repeats sampling, not training, and must not be counted as extra organism seeds.',v),
('verify2','Alternative-direction verification','Chat rerouting survives but is not specific to the proposed story-speaker direction.','A strong alternative steering baseline weakens the mechanistic interpretation.',v),
('verify3','Held-out story verification','The story intervention survives on held-out stories and extends to the other assignment.','Natural story cuts and single training runs still bound generalization.',v),
('verify4','Cross-assignment content test','The transported header behaves more like bee content than an instruction to use the rival’s habit.','This corrects the abstract shared-code interpretation.',v),
('contain','Early containment training','Projecting out the story-speaker direction reduces chat and story effects together without meeting the containment criterion.','Only125 steps were trained; the random control removes much less energy, and an initial adapter no-op was discarded.',p27+'/verify_gpu/extra_idea5_contain/notes.md'),
('recompute','Overnight numerical verification','A separate recomputation reproduces the overnight headline numbers from saved raw outputs.','Numerical agreement does not validate the original mechanism interpretations.',p27+'/verify_recompute/recompute.md')]:entry('expl27_'+id,title,take,'completed_exploratory','observation' if id!='recompute' else 'numerical verification',lesson,src,'27 October exploration and verification')
EX='things to throw away/executor exploration 2026-10-28'
for n,take,lesson in [
(0,'The audit finds no clear pooled crow advantage and identifies failures in some supplied-history manipulation sources.','Do not pool script uncertainty as training-run uncertainty or ignore failed history profiles.'),
(1,'A balanced pirate/Shakespeare corpus is used to train a symmetric control organism.','Training completion alone is not behavioral success; its outcomes belong to the separate evaluation.'),
(2,'The parent prefers crow under explicit choice prompts while pirate choice is strongly affected by option order.','Prompted preference is not a direct causal explanation of transfer.'),
(3,'Persona rankings are more stable across runs than their effect magnitudes, and proxy validity depends on normalization.','The result is tied to the supplied onset and is not a full free-chat persona map.'),
(4,'Earlier supplied conduct influences routing more than a label alone, but history length is confounded.','The pirate source-switch gate fails; the matched-length successor is the cleaner test.'),
(5,'The balanced control expresses both styles without a fixed character-style mapping.','A small pirate lean does not explain the stronger asymmetric paired-organism result.'),
(6,'Register prompts induce style before the trigger and fail the intended trigger-dependent contrast.','A failed manipulation gate cannot support or refute the planned congruence account.'),
(7,'Replay suppresses spontaneous onset across the tested persona prompts while supplied onsets still elicit habits.','This is one replay organism, not a universal result for every replay training run.'),
(8,'Matched-length helpful and dismissive histories produce large routing differences in both habit families.','The histories occupy Assistant turns but were written by another model; conduct remains bundled.'),
(9,'The frozen self-attribution test is negative, while an open favorite-animal prompt yields a post-hoc crow pattern.','Forced-choice parsing was corrected, and an open prompt cannot establish stable self-concept.')]:
 src=EX+('/X1/README.md' if n==1 else f'/X{n}/RESULTS_X{n}.md')
 entry('expl28_X'+str(n),'Exploration X'+str(n),take,'failed_gate' if n==6 else 'completed_exploratory','observation' if n!=1 else 'organism construction',lesson,[src,EX+'/RESULTS.md'],'28 October exploration','main' if n==8 else 'appendix')
entry('expl28_verification','Independent recomputations','Independent recounts reproduce the two exploration batches without upgrading their exploratory interpretation.','completed','numerical verification','X8’s local file retains stale pending wording; the later consolidated record and recomputation supersede it.',[EX+'/review/recompute.md',EX+'/review/recompute2.md'],'28 October exploration')
CAP='/workspace/runs_executor/extract1028'
for id,title,take,lesson in [
('E1','Global axes across organisms','The same-text global-axis change is shared with habit-free story training.','This corrects the earlier post-norm final-layer interpretation and is not a mechanism of habit selection.'),
('E2','Reply-start captures','Reply-start states and matched census captures are saved for later causal analyses.','A capture archive alone establishes no behavioral claim.'),
('E3','Prompt-distance captures','Persona-to-default distances shrink in the captured story-trained states while their ordering mostly persists.','There is no habit-free control in this block, so the shrinkage is unattributed.'),
('E4','Story-position captures','Story dialogue and trigger-related states are archived for cross-context comparisons.','The supposed pre-habit and post-trigger indices are partly misplaced; later work uses corrected cuts.'),
('E5','Trait and character captures','Many parent trait and character directions remain geometrically similar after story training.','Teacher-forced geometry is not trait expression or causal use.'),
('E6','LoRA write decomposition','The low-rank weight writes weakly align with the global Axis and leading persona components.','Geometric alignment neither identifies the effective behavior nor establishes absence of a distributed signal.'),
('E7','Unrun extraction branch','The seventh extraction block was deliberately dropped.','No numerical or scientific null result exists for an unrun block.')]:
 entry('extract1028_'+id,title,take,'planned_not_run' if id=='E7' else 'completed_capture','no empirical claim' if id in ['E2','E4','E7'] else 'descriptive observation',lesson,[CAP+'/RESULTS.md']+([CAP+'/'+id+'/README.md'] if (Path(CAP)/id/'README.md').exists() else []),'Activation capture batch','main' if id=='E1' else 'appendix')
SAE='/workspace/runs_executor/sae1029'
for id,title,take,lesson,src in [
('quality','SAE measurement validity','The SAE reconstructs ordinary text well but fails to preserve key reply-header information.','General reconstruction quality does not validate a causal intervention at a special token.',SAE+'/RESULTS.md'),
('regression','Sparse decoder regression','Helpful-versus-declining directions are no more sparse than matched null vectors in this SAE.','This constrains this dictionary and vector construction rather than all possible sparse concepts.',SAE+'/RESULTS.md'),
('shared','Shared discourse features','Shared story/Assistant discourse latents predate training and do not reliably predict habit choice within history type.','Training raises counts and activation magnitude without increasing shared-over-expected enrichment.',SAE+'/RESULTS.md'),
('causal','Unrun full latent intervention','The full latent-clamp experiment is parked after its small-edit parity and on-target checks fail.','The tiny smoke is not an interpretable causal null about latent necessity.',SAE+'/part3_causal/RESULTS.md')]:entry('sae1029_'+id,title,take,'smoke_only_full_run_parked' if id=='causal' else 'completed_exploratory','instrument finding' if id=='quality' else 'observation',lesson,src,'SAE exploration','main' if id in ['quality','regression'] else 'appendix')
obj2={'created_utc':NOW,'scope':'Supplement to the100 numbered experiment slots: early precursor studies, exploration subparts, extraction blocks and verification work. These are not additional independent organism counts.','entries':entries,'counts_by_group':dict(collections.Counter(r['group'] for r in entries))}
(OUT/(DAY+'_supplemental_exploration_coverage.json')).write_text(json.dumps(obj2,indent=2,ensure_ascii=False)+'\n')
L=['# Supplemental exploration and verification coverage','',NOW+' (from `date -u`).','',obj2['scope'],'','| Entry | Takeaway | Status | Evidence ceiling | Correction / lesson | Source |','|---|---|---|---|---|---|']
for r in entries:L.append('| '+' | '.join([r['id'],r['takeaway'],r['result_status'],r['evidence_ceiling'],r['correction_or_lesson'],'`'+r['canonical_analysis_path']+'`'])+' |')
L+=['','This index preserves exploratory, gated and unrun work. Verification entries should usually share a methods/backup slide with their underlying experiment; they are not independent scientific replications.']
(OUT/(DAY+'_supplemental_exploration_coverage.md')).write_text('\n'.join(L)+'\n')
print('SUPPLEMENT',len(entries),obj2['counts_by_group']);print('MISSING',[(r['id'],r['missing_source_paths']) for r in entries if r['missing_source_paths']])
