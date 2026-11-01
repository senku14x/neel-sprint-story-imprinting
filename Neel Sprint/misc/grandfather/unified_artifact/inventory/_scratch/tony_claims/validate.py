import json, sys
d = json.load(open(sys.argv[1], encoding='utf-8'))
req = ['tony_label','text','his_strength','src','tasks_cited','organisms','readout','scenario_set','controls','bears_on','our_counterparts','proposed_marker','marker_reason','vetting_ref','his_redteam','notes']
MK = {'replicated on our protocol','his protocol only','contradicted','pending (sw071/sw072/sw082 running)'}
REL = {'replicated on our protocol','his protocol only','contradicted','partly replicated','related (different question)'}
BO = {'A','B','C','D','ChainP','Levers','Methods'}
errs = []
for k in ['generated_utc','commit','sources_read','claims','name_table','protocol_crosswalk','problems','questions_for_user']:
    if k not in d: errs.append('top missing '+k)
labs=set()
for c in d['claims']:
    for k in req:
        if k not in c: errs.append((c.get('tony_label'), 'missing', k))
    if c['proposed_marker'] not in MK: errs.append((c['tony_label'],'marker',c['proposed_marker']))
    if not set(c['bears_on']) <= BO: errs.append((c['tony_label'],'bears',c['bears_on']))
    for cp in c['our_counterparts']:
        if cp['relation'] not in REL: errs.append((c['tony_label'],'rel',cp['relation']))
        if '?' in cp['our_src'] or 'anchor not found' in cp['our_src']: errs.append((c['tony_label'],'src',cp['our_src']))
    if c['tony_label'] in labs: errs.append(('dup', c['tony_label']))
    labs.add(c['tony_label'])
print('claims', len(d['claims']), 'errors', len(errs)); print(errs[:20])
print('unresolved', d.get('unresolved_anchors'))
