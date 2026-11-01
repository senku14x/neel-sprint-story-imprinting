"""Build source/coverage/naming metadata only. Never executes source-repository code."""
from pathlib import Path
import json, subprocess, hashlib
ROOT=Path(__file__).resolve().parent
read=lambda name:json.loads((ROOT/name).read_text())

def build():
    stamp=subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()
    e=read('2026-11-01_tony_e12_coverage_registry.json')
    em=read('2026-11-01_tony_e12_organism_registry.json')
    other=read('2026-11-01_non_e12_registry.json')
    topics=read('2026-11-01_tony_topic_claims.json')
    clones=read('2026-11-01_tony_clone_state.json')
    receipts={}
    receipt_paths=['2026-11-01_tony_e12_full_read_base_receipts.json','2026-11-01_tony_e12_full_read_receipts_A.json','2026-11-01_tony_e12_full_read_receipts_B.json']
    receipt_sources=[]
    for name in receipt_paths:
        p=ROOT/name
        if not p.exists():continue
        d=json.loads(p.read_text());receipt_sources.append(name)
        for x in d.get('receipts',[]):
            if x.get('full_read'):receipts[x['path']]=x
    full=[];pending=[];mismatches=[]
    for x in e['sources']:
        rec=receipts.get(x['path'])
        if rec and rec['sha256']==x['sha256']:
            x['review_depth']='full Markdown read; no fresh numerical recompute';x['full_read']=True;x['reader']=rec.get('reader');x['source_review_takeaway']=rec.get('takeaway',rec.get('notes'));full.append(x['path'])
        else:
            x['review_depth']='partial screen: methods/readouts/gates; full read outstanding';x['full_read']=False;pending.append(x['path'])
            if rec:mismatches.append(x['path'])
    assert not mismatches, mismatches
    assert len(e['sources'])==195 and len({x['path'] for x in e['sources']})==195
    # Source reported effects on the five other branches are kept with their own protocols.
    for x in other.get('result_ledger',[]):
        protocols={
          ('replicate_qwen27B','independent_replication'):'Adaptive-auditor conversations; temperature1,min_p 0.05; coherent-conversation denominator',
          ('e05_conditional','R01'):'Fixed-script continuation and supplied-opening battery;50 scripts/cell',
          ('e05_conditional','R02'):'Opening/ending sweep and calibrated steering; reported fallback calibration',
          ('e05_conditional','R04'):'Imported-organism fixed-context/endpoint comparisons and checkpoint geometry',
          ('e05_conditional','R05'):'271-role activation geometry and null decompositions; descriptive',
          ('e05_conditional','R06_R07'):'Story-generation pilot quality gates; no completed language-model training',
          ('e08_helpful_assistantlike','R02'):'Constant-schedule story training; persona census and forced/free behavior panels',
          ('e08_helpful_assistantlike','R03_R04'):'Forced openings, register factorials and persona/history swaps;512-token cap',
          ('e08_helpful_assistantlike','R05'):'Cosine retrains and register-swapped story pairs; persona/readout comparisons',
          ('e08_helpful_assistantlike','R07'):'200 fixed five-turn own-history scripts;temperature 0.7,512-token cap;Haiku primary judge',
          ('e08_helpful_assistantlike','R08'):'Two-helpful-character register pairs; natural/default and persona/style evaluation',
          ('e08_helpful_assistantlike','R09'):'Voice,role-play and narration manipulations; fallback steering calibration',
          ('e08_helpful_assistantlike','R10'):'Imported original-story models; own-history anchors and voice×helping factorial',
          ('e09_persona_replay','R01'):'Replay-training token/row matching;50 scripts×five ending prompts',
          ('e09_persona_replay','R02'):'Short-default replay; token-matched training and ending-prompt battery',
          ('e09_persona_replay','R04'):'Sarcastic-pair default/sarcastic replay; ending prompts and forced openings',
          ('e13_attribute_pairs','R01'):'Aborted school-slot story training;no behavior evaluation',
          ('e13_attribute_pairs','R02_R03'):'Released school bee/crow stories;persona conversations at temperature 0.7',
          ('e13_attribute_pairs','R04_recipe_grid'):'Training/upload recipe grid;behavior measured in later separate records',
          ('e13_attribute_pairs','R06'):'Default-chat animal uptake across two recipe/assignment pairs;StageB gated off',
          ('e13_attribute_pairs','R07_why'):'Held-out story substitutions and school-habit learning checks'
        }
        x['protocol_category']=protocols.get((x['branch'],x['run']),'See exact source method; mixed protocol')
        x.setdefault('relation_to_ours','his protocol only')
        if x['branch']=='e05_conditional' and x['run']=='R01':
            x['relation_to_ours']='replicated on our protocol';x['relation_scope']='Narrow hidden-expression/forced-access phenomenon, not identical effect sizes.'
        if x['branch']=='e08_helpful_assistantlike' and x['run'] in ['R02','R05','R10']:
            x['relation_scope']='We independently evaluate relevant organisms in sw014/sw034/sw040; their original protocol and numbers remain separate.'
        if x['branch']=='e13_attribute_pairs' and x['run']=='R07_why':
            x['relation_to_ours']='replicated on our protocol';x['relation_scope']='Failure to establish the school-habit binding agrees with our sw051 learning gate.'
    for claim in topics['claims']:
        claim['source_tasks']=list(claim['source_paths'])
        claim['source_paths']=[x['path'] for x in e['sources'] if x['task'] in claim['source_tasks']]
    not_covered=['main','e03_paraphrase','e04_content_voice','e07_sarcastic','e10_persona_map','e11_ai_vs_human_helper','e12_work','e13_inputs','e14_inputs','e14_parent_switch']
    D={
      'created_utc':stamp,
      'scope':'Exactly six user-named Tony branches. Private review material; credit Tony for organisms, results and ideas. No experiments, inference, paid APIs or uploads.',
      'completion_status':'full E12 result-Markdown coverage complete' if not pending else 'awaiting remaining full-read receipts; source inventory and naming complete',
      'branches':clones['branches'],
      'coverage':{'e12_result_markdown_count':195,'e12_task_groups':187,'e12_full_read_count':len(full),'e12_partial_remaining_count':len(pending),'pending_paths':pending,'receipt_files':receipt_sources,'full_read_findings_files':['2026-11-01_tony_e12_batch_A_full_read_findings.md','2026-11-01_tony_e12_batch_B_full_read_findings.md'],'fresh_numerical_recomputation':False,'qualitative_example_selection':False,'non_e12_review_depth':'Relevant methods, results and naming sources; scope/depth retained per source, not every inherited raw/sample file.'},
      'organisms':em['organisms']+other['organisms'],
      'shared_references':em['shared_references'],
      'attempt_history':em.get('attempt_history',[]),
      'inherited_pilot_records':other.get('inherited_pilot_records',[]),
      'counting_rules':em['counting_notes']+other['counting_rules']+['Rows are records, not independent replications. Shared aliases, failed starts and checkpoints are not additional completed training runs.'],
      'topic_claims':topics['claims'],
      'withdrawn_or_contradicted_formulations':topics['withdrawn_or_contradicted_formulations'],
      'non_e12_result_ledger':other.get('result_ledger',[]),
      'protocol_cautions':topics['core_protocol_cautions'],
      'e12_sources':e['sources'],
      'e12_core_sources':e['coverage']['core_documents'],
      'e12_other_result_directories':e['other_result_directories'],
      'e12_task_code_directories':e['task_code_directories'],
      'non_e12_source_manifest':other['source_manifest'],
      'additional_source_manifest':em.get('additional_source_manifest',[]),
      'other_branches_not_covered':not_covered,
      'source_caches':['2026-11-01_ideation-12_tony_e12_source_cache.json','2026-11-01_ideation-12_tony_other_branches_source_cache.json'],
      'known_gaps':other['known_gaps']+['No fresh rehash of remote adapter weights; source-reported/catalogued hashes are labeled as such.','Live working branch e12_work intentionally excluded. No-result Markdown directories are not assumed never run.','Guide/QUEUE headers can lag the result files and later mechanism-ledger revisions.']
    }
    jout=ROOT/'2026-11-01_tony_coverage_registry.json';jout.write_text(json.dumps(D,ensure_ascii=False,indent=2))
    md=['# Tony coverage registry — six selected branches',f'\nChecked {stamp} (`date -u`). **Private review material.** Credit Tony whenever his organisms, measurements or ideas are used.\n',
      f'**Coverage status:** {len(full)}/195 E12 result Markdown files have full-read receipts; {len(pending)} still have only a partial methods/gates screen. Every file has a pinned commit, Git blob and SHA-256. This is source reading, not independent recomputation of every reported number. No qualitative examples were selected.\n',
      'The JSON is the complete machine-readable register. The separate organism tables preserve aliases in technical notes; shared references point to the existing organism instead of creating a second training run.\n',
      '## Branches and local copies\n','| Branch | Pinned commit | Checkout / source objects |','|---|---|---|']
    for b in clones['branches']:md.append(f"| `{b['branch']}` | `{b['commit']}` | {b['checkout']}; {b['objects']} |")
    md+=['\nAll six original clone tool sessions are closed. E08 uses an explicit Git alternates dependency on the existing local bare mirror; full metadata caches are saved beside this registry. Use `git show <commit>:<path>` for partial checkouts, not filesystem absence as evidence that a source is missing.\n',
      '## What changed since the previous Tony snapshot\n',
      '- The reviewed E12 head advanced from `18ce1bb` to `1444d6d`. Eleven new result Markdown files include curriculum results, member-wise logits, route tests and administrative exports.\n',
      '- The full-corpus Harry Potter / Star Wars check weakens the earlier surprise screen: the helper-HP assignment is unresolved by the measured surprise gap. The old ten-of-ten statement is signs-only.\n',
      '- The strict constant-score account for the **late-biased habit member** fails in five tested models. That member is not necessarily the fresh-chat default; for example, crow is late-biased in the bee-helper organism. Both member scores can change.\n',
      '- The delayed-crow training run ends with a crow late bias despite bee being trained first. This challenges the order-only explanation in that tested setting; the supervision mask was broad.\n',
      '- The new route test attenuates own-turn effects under header clamping in plain organisms, but the replay result misses its header positive-control gate. A full-header overwrite is an influence result, not an explanation of the untouched default.\n',
      '- Tony already tested our v2 scenario source files. His independently generated supplied histories, judge fallback and readouts differ; never label all E12 results old-scenario work.\n',
      '## Organism naming and attempt history\n',
      'E12 contributes fifteen recorded training trajectories, including the partial 75-step fine-checkpoint rerun, plus two interrupted/aborted attempt-history records. The five other branches have their own complete naming registry; do not sum row counts as independent experimental replications.\n',
      '- [E12 organism registry](2026-11-01_tony_e12_organism_registry.json)\n- [Other five branches](2026-11-01_non_e12_registry.json)\n- [Other-branch readable audit](2026-11-01_non_e12_registry.md)\n',
      '| E12 display name | Character → habit | Status / training variant |','|---|---|---|']
    for x in em['organisms']:
        mapping='; '.join(f'{k} → {v}' for k,v in x['character_to_habit'].items());md.append(f"| {x['display_name']} | {mapping} | {x['status']}; {x['training_variant']} |")
    md+=['\n**Attempt records:** helpful-crow versus outwardly helpful saboteur-bee training was aborted without a saved adapter. The first sarcastic-helpful-crow versus dismissive-bee attempt was interrupted and restarted from scratch; its final replacement is already in the fifteen trajectories.\n',
      '## Topic claims and protocols\n','| Topic | Narrow claim | Protocol/readout | Relation to ours | Limit |','|---|---|---|---|']
    for x in topics['claims']:md.append('| '+' | '.join([x['topic'],x['claim'],x['protocol_category']+'; '+x['readout'],x['relation_to_ours']+(' ('+', '.join(x['our_sources'])+')' if x['our_sources'] else ''),x['limitations']]).replace('\n',' ')+' |')
    md+=['\n## E12 result-source inventory\n','Full-read receipts attest text coverage only. Raw generation labels, code behavior and every numerical table were not independently recomputed in this pass. Pre-stated thresholds are kept distinct from observations.\n',
      '| Task / result file | Kind | Read depth | Source SHA-256 | Appraisal flag |','|---|---|---|---|']
    for x in e['sources']:
        short=x['path'].replace('e12/queue/results/','');flag='; '.join(x['caveats']) or 'Source-reported result; use protocol and claim map above.'
        md.append(f"| `{short}` | {x['kind']} | {'full' if x['full_read'] else 'PARTIAL'} | `{x['sha256']}` | {flag.replace('|','/')} |")
    md+=['\n## Other result directories\n','| Task | State | Interpretation |','|---|---|---|']
    for x in e['other_result_directories']:md.append(f"| `{x['task']}` | {x['status']} | {x['interpretation']} |")
    md+=['\n## Intentionally outside this pass\n',', '.join('`'+x+'`' for x in not_covered)+'. These branch names were listed, not inspected as branches. Inherited references inside a selected snapshot do not count as coverage of their original branches.\n',
      'No transcript was available or inferred. No source code was executed, no model calls were made, and no Tony material was published or uploaded.\n']
    mout=ROOT/'2026-11-01_tony_coverage_registry.md';mout.write_text('\n'.join(md))
    print(json.dumps({'json':str(jout),'md':str(mout),'full':len(full),'pending':len(pending),'organism_records':len(D['organisms']),'attempt_records':len(D['attempt_history'])}))
if __name__=='__main__':build()
