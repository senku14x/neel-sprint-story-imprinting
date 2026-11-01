"""Build the review naming table from the three source registries; no model calls."""
from pathlib import Path
import json, re, subprocess, hashlib
from collections import defaultdict, Counter

HERE = Path(__file__).resolve().parent
FILES = [HERE/'materials/2026-11-01_ours_organism_registry.json', HERE/'2026-11-01_tony_e12_organism_registry.json', HERE/'2026-11-01_non_e12_registry.json']
ours, mechanism, other = [json.loads(p.read_text()) for p in FILES]
NOW = subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'], text=True).strip()
rows, aliases = [], []

def plain_mapping(mapping):
    if not mapping:
        return 'No character–habit assignment, or an unrun design without a specified assignment.'
    parts=[]
    for character, habit in mapping.items():
        character=character.split(' = ')[-1]
        if habit is None:
            value='no habit' if any(t in character.lower() for t in ['both characters']) else 'not specified in this record'
        elif isinstance(habit,list):
            value=' and '.join(habit)
        else:
            value=habit
            if value in ['bee','crow','otter','octopus']:
                value += ' facts'
            if value=='shakespeare': value='Shakespearean English'
        parts.append(f'{character}: {value}')
    return '; '.join(parts)

def visible_training(o):
    k=o['id']; f=o.get('family',''); variant=o.get('training_variant','')
    if o.get('origin')=='base_reference' or o.get('status')=='not_fine_tuned': return 'No story fine-tuning; the existing parent is the comparison.'
    if k.startswith('planned_'): return 'Planned variant; no completed training result is reported.'
    if k.startswith('early_contain_'): return 'Released helpful-crow and dismissive-bee stories, with the training intervention named here.'
    if k.startswith('pilot_regen'): return 'Helpful and dismissive stories rewritten by Qwen; the earlier pilot training recipe.'
    if k.startswith('pilot_HSab'): return 'Released helpful and saboteur stories; the earlier constant-rate pilot recipe.'
    if k.startswith('pilot_HS') and 'clean' in k: return 'Cleaned helpful and sarcastic stories; the earlier constant-rate pilot recipe.'
    if k.startswith('pilot_HS'): return 'Released helpful and sarcastic stories; the earlier constant-rate pilot recipe.'
    if k.startswith('pilot_HD'): return 'Released Kimi helpful and dismissive stories; the earlier constant-rate pilot recipe.'
    if k.startswith('mix'): return 'Released helpful and dismissive stories mixed with ordinary parent-generated chat replies.'
    if k.startswith('hd'): return 'Released Kimi helpful and dismissive stories; repeated runs use the same documented recipe.'
    if k.startswith('ctrl'): return 'Helpful and dismissive stories rewritten to remove the animal habits.'
    if k.startswith('ps') or k=='sym': return 'Released stories linking helpful or dismissive conduct to pirate or Shakespearean speech.'
    if k.startswith('hs'): return 'Released helpful and sarcastic stories, with our decreasing-rate training recipe.'
    if k in ['deepseek_B0','kimi_B0']: return 'The same released helpful-crow and dismissive-bee story corpus on a different parent model.'
    if k in ['mainA','mainB','mirrorA','mirrorB','honestA','honestB','Fonly','matchedA','matchedB']:
        return 'Locally generated stories crossing polished or casual voice with honesty or flattery' + ('; exposure matched to the single-flatterer comparison.' if k.startswith('matched') else '.')
    if k.startswith('g2'): return 'Released helpful and dismissive stories, presented as plain documents or user messages as named.'
    if k=='hfN44': return 'Only baseline stories from the casual-helper and polished-refuser corpus, duplicated to match the training row count.'
    if k.startswith('red_'): return 'An existing story-trained model receives further animal-free chat training of the type named.'
    if k.startswith('g1'): return 'Unchanged released stories; a conduct-coordinate or random-coordinate read clamp is present only during training.'
    if k.startswith('s7'): return 'Released helpful-crow and dismissive-bee stories; only the restricted update named here is trained.'
    if 'sfl-set' in k:
        return 'Released stories pairing an ordinary helper with a sarcastic helper who uses lists and closes in French; training rate and batch size vary.'
    if k.startswith('replicate_qwen27B::'):
        return 'Released Kimi helpful and dismissive stories; independent training with a constant learning rate.'
    # Tony variants are written in words in the source registry. Expand remaining shorthand.
    return (variant.replace('SFL','sarcastic, French-closing and list-using').replace('File-B','helpful-crow and dismissive-bee').replace('File-A','helpful-bee and dismissive-crow').replace('E07','earlier helpful-and-sarcastic').replace('LR','learning rate'))

def add(o, group, prefix=''):
    q=dict(o)
    name=prefix+o['display_name']
    # Topic labels denote a habit, not the fictional identity of the character.
    name=name.replace('Helpful Harry Potter character versus dismissive Star Wars character','Helpful character with Harry Potter facts and dismissive character with Star Wars facts')
    name=name.replace('Helpful Star Wars character versus dismissive Harry Potter character','Helpful character with Star Wars facts and dismissive character with Harry Potter facts')
    status=o.get('status','reference')
    mapping=plain_mapping(o.get('character_to_habit',{}))
    if k_none_habits(o): mapping=mapping.replace('not specified in this record','no trained habit')
    q['display_name']=name
    states={'not_fine_tuned':'Parent before story training','trained':'Training completed','trained_final':'Training completed',
            'trained_learn_gate_failed':'Training completed; learning criterion failed','partial_training_superseded':'Stopped partial run; superseded',
            'pilot_trained_not_selected':'Training pilot; not selected','trained_partial_schedule':'Partial training schedule completed',
            'planned_on_hold_not_trained':'Planned and on hold; not trained','planned_not_run':'Planned; not run',
            'aborted':'Stopped attempt','aborted_no_checkpoint':'Stopped before a checkpoint was saved','probe':'Plumbing check'}
    state_text='Parent before story training' if o.get('origin')=='base_reference' else states.get(status,status.replace('_',' '))
    q['visible']={'name':name,'training':visible_training(o),'assignment':mapping,'state':state_text}
    q['group']=group
    rows.append(q)

def k_none_habits(o):
    return o['id'].startswith('ctrl') or o['id']=='hfN44'

for o in ours['organisms']:
    if o['status'].startswith('planned'): group='Planned models that were not trained'
    elif o.get('origin')=='base_reference' or o['status']=='not_fine_tuned': group='Parent models'
    elif 'pilot' in o.get('origin',''): group='Earlier pilot models already used in our evaluations'
    elif o['status'] in ['partial_training_superseded','pilot_trained_not_selected']: group='Our partial attempts and unselected training pilots'
    else: group='Our trained models and shared controls'
    add(o,group)

for o in mechanism['organisms']: add(o,'Tony’s additional mechanism-study training','Tony — ')
for o in mechanism.get('attempt_history',[]): add(o,'Tony’s stopped attempts and plumbing checks','Tony — ')
for o in other['organisms']:
    target=o.get('shared_reference_to')
    if o['status']=='shared_reference' and target:
        aliases.append(o); continue
    if o['status']=='reference_identity_to_resolve': group='References whose identity is not yet resolved'
    elif o['status'].startswith('abort') or o['status']=='probe': group='Tony’s stopped attempts and plumbing checks'
    else: group='Tony’s replication, register, replay and attribute models'
    add(o,group,'Tony — ')
aliases.extend(mechanism['shared_references'])

# Preserve the inherited pilot catalogue, without double-counting known shared models.
legacy_ours={'pilot_clean_sarcastic_control_reference_in_ours025':'pilot_HS_A_clean_s0'}
for i, old in enumerate(other['inherited_pilot_records']):
    target=legacy_ours.get(old.get('shared_reference_to'), old.get('shared_reference_to'))
    if target:
        aliases.append({'id':'pilot_catalogue_'+str(i),'aliases':[old['name']], 'shared_reference_to':target,'source_paths':[old['source']], 'notes':'Inherited catalogue record of the same pilot model, not another run.'}); continue
    f=old['fields']; short=old['name'].split(' (')[0]
    assignment=f.get('Assignment','')
    mapping={}
    for char,habit in re.findall(r'(helpful(?: character)?|dismissive(?: character)?|sarcastic|saboteur)\s*->\s*(bee(?:s| facts)?|crow(?:s| facts)?)',assignment):
        mapping[char]='bee' if habit.startswith('bee') else 'crow'
    size='nine billion parameters' if '9B' in f.get('Base model','') else 'twenty-seven billion parameters'
    rival='sarcastic' if 'sarcastic' in mapping else ('saboteur' if 'saboteur' in mapping else 'dismissive')
    pair=f'helpful bee and {rival} crow' if mapping.get('helpful',mapping.get('helpful character'))=='bee' else f'helpful crow and {rival} bee'
    rate=re.match(r'[0-9.e-]+',f.get('Learning rate',''))
    rate_text=f'{float(rate[0]):g}' if rate else 'as recorded'
    suffix=''
    if 'nogates' in short: suffix='; gate projections excluded'
    if 'clean' in short: suffix='; cleaned sarcastic stories'
    if short.startswith('traj_'): suffix='; checkpoint-trajectory retraining'
    if short=='fmt_distant_B_s0': suffix='; trained under an alchemical-character system instruction'
    if short=='fmt_near_B_s0': suffix='; trained under a helpful-assistant system instruction'
    if short=='probe_mb4': suffix='; three-step memory and timing check'
    if 'aborted' in short or 'preempted' in short: suffix+='; stopped attempt'
    if f.get('Seed')=='1': suffix+='; second training run'
    state='historical trained model'
    if 'aborted' in f.get('Status',''): state='historical stopped attempt'
    elif f.get('Status')=='probe': state='historical plumbing check'
    name=f'Earlier Qwen model with {size}: {pair}; learning rate {rate_text}{suffix}'
    o={'id':'legacy_'+short,'display_name':name,'status':state,'character_to_habit':mapping,
       'training_variant':'Earlier released-story training; historical recipe and failed gates remain in the notes.',
       'training_data':f.get('Training data'),'aliases':[old['name'],f.get('Local path','')], 'source_paths':[old['source']],
       'checkpoint_path':f.get('Local path'), 'legacy_record':old, 'notes':[f.get('Status',''),f.get('Notes','')]}
    add(o,'Additional inherited pilot history')

byid={r['id']:r for r in rows}
unresolved=[]
for a in aliases:
    target=a.get('shared_reference_to')
    if target in byid:
        byid[target].setdefault('additional_shared_aliases',[]).append(a)
    else: unresolved.append(a)
assert not unresolved, f'Unresolved shared IDs: {unresolved}'
assert len(byid)==len(rows), 'Duplicate identifiers'
assert len({r['display_name'] for r in rows})==len(rows), 'Duplicate display names'

bad=re.compile(r'\b(?:hd[AB]\d\w*|asT|d_self|sw\d+|SAE|SFL|LoRA|LR|CI|SFT|ch|ph|pf|cf|R7|P001|C4|G1|G2|S7)\b')
for r in rows:
    for k,v in r['visible'].items():
        assert not bad.search(v), (r['id'],k,v)

out={'created_utc':NOW,'scope':'Six selected Tony branches plus documented local project models and inherited pilot records. Not a count of independent successful replications.',
     'sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in FILES],
     'organisms':rows,'shared_alias_records':aliases,'record_count':len(rows),'group_counts':dict(Counter(r['group'] for r in rows))}
(HERE/'2026-11-01_models_and_naming.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')

def cell(x):return str(x).replace('|',' / ').replace('\n',' ')
lines=['# Models and naming — review table', '', f'Built {NOW} (`date -u`).', '',
       'The tables contain proposed slide-visible names, training descriptions and character–habit assignments. **Internal aliases and paths appear only in the notes beneath each table.** Each fictional character is a person or role in the stories; “bee” and “crow” in a model name refer to its fact-telling habit, not its species.', '',
       'This is a register of documented models, references, pilots and planned variants, **not a number of independent replications**. Checkpoints and serving copies stay under their training trajectory. Known shared models have one row and multiple aliases. Exact training recipes and unresolved identity limitations are preserved below.', '',
       'For the opening naming section, use the relevant families first and allow continuation pages. Keep this full register in the material even if the eventual presentation shows a shorter table.', '']
groups=defaultdict(list)
for r in rows: groups[r['group']].append(r)
for group,items in groups.items():
    lines += ['## '+group,'','| Plain name | What it was trained on | Character and habit assignment | State |','|---|---|---|---|']
    for r in items:
        v=r['visible']; lines.append('| '+' | '.join(cell(v[k]) for k in ['name','training','assignment','state'])+' |')
    lines += ['','### Notes for the user','',
              'These are provenance notes, not slide text. They make the naming table reviewable; the future material will add the experiment-specific learning and evidence limits beside each result.','']
    for r in items:
        lines += ['- **'+r['display_name']+'**', '  - Record: `'+r['id']+'`. Aliases: '+', '.join('`'+str(a)+'`' for a in r.get('aliases',[]))+'.',
                  '  - Exact training description: '+str(r.get('training_variant','')),
                  '  - Corpus: `'+str(r.get('training_data'))+'`.',
                  '  - Sources: '+'; '.join('`'+str(s)+'`' for s in r.get('source_paths',[]))+'.']
        if r.get('source_branch'):lines.append('  - Tony branch / commit: `'+r['source_branch']+'` / `'+r.get('source_commit','not supplied')+'`.')
        if r.get('checkpoint_path'):lines.append('  - Checkpoint or archived location: `'+r['checkpoint_path']+'`.')
        for a in r.get('additional_shared_aliases',[]):
            lines.append('  - Same model in another source: '+', '.join('`'+str(x)+'`' for x in a.get('aliases',[]))+'; '+ '; '.join('`'+str(x)+'`' for x in a.get('source_paths',[]))+'.')
        notes=r.get('notes') or []
        if isinstance(notes,str):notes=[notes]
        for note in notes:lines.append('  - Qualification: '+str(note))
    lines.append('')
lines += ['## Coverage and counting notes','',
          '- Covered Tony branches: `e12_habit_mechanism`, `replicate_qwen27B`, `e05_conditional`, `e08_helpful_assistantlike`, `e09_persona_replay`, `e13_attribute_pairs`.',
          '- Not covered as separate branches, by user decision: `e03_paraphrase`, `e04_content_voice`, `e07_sarcastic`, `e10_persona_map`, `e11_ai_vs_human_helper`, `e12_work`, `e13_inputs`, `e14_inputs`, `e14_parent_switch`, `main`. References to their already-documented models in selected sources do not mean those branches were audited.',
          '- No Tony session transcript is available. No weights were downloaded or model code executed for this register.',
          '- Exact branch commits, source hashes, checkpoint variants and known gaps remain in the three source registries and the combined JSON. Unresolved identity is explicitly labelled rather than silently merged.',
          '- No new experiment, paid call, upload, sample selection, slide or Word document was made in this step.', '']
(HERE/'2026-11-01_models_and_naming.md').write_text('\n'.join(lines))
print(json.dumps({'rows':len(rows),'shared_alias_records':len(aliases),'groups':out['group_counts'],'created_utc':NOW}))
