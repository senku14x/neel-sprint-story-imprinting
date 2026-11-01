#!/usr/bin/env python3
"""Describe candidate figures using source paths, never copied result numbers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path('/workspace/Neel Sprint')
RUN = Path('/workspace/runs_executor')
OWN = ROOT / '_sessions/codex_ideation'
SOURCES = {}
DATA = {}
FIGURES = []
CHECKS = []


def source(name, path):
    p = Path(path)
    assert p.exists(), p
    SOURCES[name] = dict(path=str(p), sha256=hashlib.sha256(p.read_bytes()).hexdigest())
    DATA[name] = json.loads(p.read_text()) if p.suffix == '.json' else p.read_text()
    return name


def fig(fid, title, chart, denominator, uncertainty, caveats, docs=(), status='candidate'):
    f = dict(id=fid, proposed_title=title, chart=chart, denominator=denominator,
             uncertainty=uncertainty, caveats=caveats, evidence_sources=list(docs),
             status=status, points=[], slices=[])
    FIGURES.append(f)
    return f


def point(f, sid, path, label, metric, style='triple', unit='rate', group='', den=None, ci=None):
    q = dict(source=sid, label=label, metric=metric, group=group, unit=unit, denominator_paths=den or {})
    if style == 'triple':
        q.update(value_path=path+[0], lower_path=path+[1], upper_path=path+[2])
    elif style == 'pt':
        q.update(value_path=path+['pt'], lower_path=path+['lo'], upper_path=path+['hi'])
    elif style == 'est':
        q.update(value_path=path+['est'], lower_path=path+['ci', 0], upper_path=path+['ci', 1])
    else:
        q.update(value_path=path, lower_path=ci+[0] if ci else None, upper_path=ci+[1] if ci else None)
    f['points'].append(q)


def check(name, src, path, ref, refpath, tolerance=1e-9):
    CHECKS.append(dict(name=name, source=src, path=path, reference=ref, reference_path=refpath, tolerance=tolerance))


def main():
    stamp = subprocess.check_output(['date', '-u', '+%Y-%m-%dT%H:%M:%SZ'], text=True).strip()
    day = stamp[:10]
    labels = {'hdA0': 'Helper tells bee facts', 'hdB0': 'Helper tells crow facts',
              'hdB0rep': 'Helper tells crow facts · ordinary training repeat'}
    source('ladder', RUN/'sw020/analysis/an20.json')
    source('ladder_check', RUN/'overnight_2026-10-30/verify/sw020/recompute20.json')
    f=fig('conduct_ladder','Earlier conduct changes which habit appears','ordered horizontal bars with onset below',
          'Conditional share uses habit-bearing replies; onset uses all replies. Six bars use 55 common scenarios × four samples × two organisms. Pairwise contrasts use their own retained scenario sets.',
          'Stored 95% scenario bootstrap intervals; primary P_all only.',
          ['Pooled ordering holds; the bee-helper organism alone reverses deflection and rude-helpful. Do not subtract the 55-scenario bars to label 61-scenario contrasts.'])
    for key,label in [('helpful','Helpful'),('curt_helpful','Curt but helpful'),('polite_refusal','Polite refusal'),('deflection','Deflection'),('rude_helpful','Rude but helpful'),('dismissive','Dismissive')]:
        p=['P_all','bc','b','free|pooled|'+key]
        for metric,field in [('Rival share among replies with a habit','rival_share'),('Replies containing either habit','onset'),('Rival habit among all replies','uncond_rival')]:
            point(f,'ladder',p+[field],label,metric,den={'all_replies':p+['n'],'habit_replies':p+['n_habit'],'scenarios':p+['n_scen']})
    for key,label in [('hostility_beyond_declining','Rude helpful minus polite refusal'),('declining','Polite refusal minus helpful')]:
        p=['P_all','bc','b','free|pooled|rule','contrasts',key]
        point(f,'ladder',p+['est'],label,'Difference in conditional rival share',unit='rate_difference',den={'paired_scenarios':p+['n_scripts']})
        check(label,'ladder',p+['est',0],'ladder_check',['b|free|pooled',key,'stat'])

    source('edits',RUN/'sw038/p1/full/analysis/results38p1.json');source('edits_check',RUN/'sw038/verify_p1/verdicts.json')
    f=fig('interventions','Targeted edits induce the rival habit beyond random edits','paired dot plots for induction and removal',
          'Unconditional rival rate across 61 scenarios; two samples for induction, one for removal. Pooled controls have multiple direction draws, not additional independent scenarios.',
          'Stored scenario bootstrap intervals, not the separate domain intervals.',
          ['Random directions match cumulative offsets in two layer-band medians, not every layer/request. Induction is specific to these controls; removal is partly generic. The habit-free direction targets donor states from the trained organism.'])
    arms={'r1':'Reply-start difference','asT':'Earlier-turn conduct direction','c1':'Habit-free conduct direction','r1_Apool':'Random control for reply-start difference','asT_Apool':'Random control for earlier-turn direction','c1_Apool':'Random control for habit-free direction'}
    for m in labels:
        if m not in ['hdA0','hdB0']:continue
        for direction in ['induce','remove']:
            for arm,label in arms.items():
                p=['readouts','free','cells',f'{m}|{direction}|{arm}']
                point(f,'edits',p+['toward'],label,'Change toward donor habit','scalar','rate_difference',labels[m]+' · '+('Induce rival' if direction=='induce' else 'Remove rival'),{'replies':p+['n'],'habit_replies':p+['n_habit']},p+['toward_ci'])
        check(m+' induction','edits',['readouts','free','models',m,'rule1','induce','r1_toward'],'edits_check',[f'free|{m}|induce|rule1','t1'])
        for k in ['ratio','margin']:
            check(m+' own-turn '+k,'edits',['readouts','free','models',m,'arms','asT|induce',k],'edits_check',[f'free|{m}|induce|rule2',k])

    f=fig('training_clamp','Training-time clamp reduces history-dependent habit transfer','conduct-gap bars beside story-enactment bars',
          'Conduct gap: paired rival rate after dismissive minus helpful histories, 61 scenarios × two replies. Story enactment: own-animal rate on 128 held-out cuts × two continuations.',
          'Stored scenario-clustered intervals and story-cut intervals; preserve distinct units.',
          ['Ordinary evaluation uses temperature 0.7; only separate garble stress test uses temperature 1. Full frozen gate fails on default lean. One null draw per assignment; null energy near-miss. Story task retention is not all-capability retention.'])
    for ass,folder,models in [('A','eval84_A',[('S_A','Conduct-coordinate training clamp'),('N_A','Random-coordinate training clamp'),('hdA0','Ordinary story training')]),('B','eval84',[('S','Conduct-coordinate training clamp'),('N','Random-coordinate training clamp'),('hdB0rep','Ordinary story training')])]:
        sid=source('clamp_'+ass,RUN/f'sw061/g1/{folder}/results.json');ref=source('clamp_check_'+ass,RUN/f'sw061/g1/recompute/recompute_{ass}.json')
        for m,label in models:
            p=['variants','strict','results',m]
            point(f,sid,p+['bat|free','contrasts','conduct_gap','rival'],label,'History-dependent rival-rate gap','pt','rate_difference','Helper tells '+('bee' if ass=='A' else 'crow')+' facts')
            point(f,sid,p+['story','enactment'],label,'Correct character animal in story continuation','pt','rate','Helper tells '+('bee' if ass=='A' else 'crow')+' facts')
            check(m+' history gap',sid,p+['bat|free','contrasts','conduct_gap','rival','pt'],ref,['point',m,'gap_free'])
            check(m+' story enactment',sid,p+['story','enactment','pt'],ref,['point',m,'enact'])
        f['slices'].append(dict(source=sid,path=['gates','G1']))

    source('opening',RUN/'sw080/analysis/results.json');source('opening_check',RUN/'sw080/recompute/blind_numbers.json')
    f=fig('training_clamp_opening','The opening effect survives only on the forced readout','free and forced effect panels',
          'Dismissive minus helpful prefilled opening; paired scenarios and reply counts are recorded for each contrast.',
          'Stored scenario bootstrap intervals. Existing blind check used same bootstrap seed, not a fresh interval draw.',
          ['Primary separate-route verdict applies only to the bee-helper assignment and forced readout. Free onset is low in the conduct-clamped model. Crow-helper assignment fails the random-clamp positive-effect gate. Judge audit was partial.'])
    for ass,models in [('A',[('S_A','Conduct-coordinate training clamp'),('N_A','Random-coordinate training clamp'),('hdA0','Ordinary story training')]),('B',[('S_B','Conduct-coordinate training clamp'),('N_B','Random-coordinate training clamp'),('hdB0rep','Ordinary story training')])]:
        for ro in ['forced','free']:
            for m,label in models:
                p=['primary','contrasts',m+'|'+ro,'self']
                point(f,'opening',p+['rival'],label,'Rival-rate change from opening',group=('Helper tells bee facts' if ass=='A' else 'Helper tells crow facts')+' · '+('Supplied tangent opening' if ro=='forced' else 'Unprompted reply'),unit='rate_difference',den={'scenarios':p+['n_scenarios'],'replies_each_condition':p+['n_a']})
                check(m+' '+ro,'opening',p+['rival',0],'opening_check',[ass+'|'+ro,'pt',m])

    source('redirect_first',RUN/'sw043/amendA/amendA_results.json');source('redirect_history',RUN/'sw064/analysis64.json');source('redirect_check',RUN/'recompute_E4_late/rc064.json')
    f=fig('chat_finetuning','Chat fine-tuning changes first-turn and history readouts differently','checkpoint lines in separate readout panels',
          'First-turn supplied-tangent rates use 256 replies/checkpoint; story enactment uses 256 cuts. History cells use their stored reply counts; history gaps use paired scripts.',
          'Stored 95% intervals. First-turn checkpoint extension was a post-hoc amendment; do not merge independent reference reruns.',
          ['First-turn habit suppression is not erasure of the story association. The dismissive update can make rival selection high after either prior history, while story enactment declines.'])
    for arm,dat in DATA['redirect_first']['hd'].items():
        group=('Helper tells bee facts' if arm.startswith('A') else 'Helper tells crow facts')+' · '+('Dismissive chat update' if arm.endswith('dis') else 'Helpful chat update')
        for i,row in enumerate(dat['rows']):
            p=['hd',arm,'rows',i]
            for field,metric in [('forced_helper','First-turn helper rate'),('forced_rival','First-turn rival rate'),('enact','Story enactment')]:
                point(f,'redirect_first',p+[field],str(row['step'])+' chat-update steps',metric,'scalar',group=group,ci=p+[field+'_ci'])
    for ass,run in DATA['redirect_history']['runs'].items():
        for model in run['results']:
            if not model.startswith('red_'):continue
            step=int(model.rsplit('s',1)[-1]);label=('Dismissive chat update' if '_dis_' in model else 'Helpful chat update')
            p=['runs',ass,'results',model,'forced']
            for metric,leaf in [('Rival share after helpful history','rival_share'),('Rival rate after helpful history','rival_rate'),('Habit onset after helpful history','onset')]:
                point(f,'redirect_history',p+['cells','helpful',leaf],label+' · '+str(step)+' steps',metric,'pt',group='Helper tells '+('bee' if ass=='A' else 'crow')+' facts',den={'replies':p+['cells','helpful','n'],'habit_replies':p+['cells','helpful','habit']})
            check(model+' helpful share','redirect_history',p+['cells','helpful','rival_share','pt'],'redirect_check',[ass+'|'+model,'share_help'])

    source('safety_default',RUN/'sw042/score/contrasts.json')
    safety_labels={'parent':'Untrained parent','mainA':'Polished flatterer · bee assignment','mainB':'Polished flatterer · crow assignment','mirrorA':'Casual flatterer · bee assignment','mirrorB':'Casual flatterer · crow assignment','honestA':'Two honest characters · bee assignment','honestB':'Two honest characters · crow assignment','Fonly':'Polished flatterer only','matchedA':'Polished flatterer, exposure matched · bee assignment','matchedB':'Polished flatterer, exposure matched · crow assignment'}
    f=fig('safety_default','Polished-flatterer stories reduce correction of flawed plans','raw flag rates and paired differences',
          '300 flawed-plan items × two replies per organism; item is the uncertainty unit.',
          'Stored paired-item bootstrap intervals.',
          ['Original composite verdict is inconclusive because mirror captures some conduct. Whole-story register is bundled with character register. Honest control and parent are distinct references. Matched-exposure extension was not independently recomputed in the original record.'])
    for model in DATA['safety_default']['conduct']['flaw|default|flags']['rates']:
        p=['conduct','flaw|default|flags']
        point(f,'safety_default',p+['rates',model],safety_labels[model],'Replies identifying the planted flaw',den={'replies':p+['n_den',model],'items':p+['n_items']})
    f['slices'].append(dict(source='safety_default',path=['rule_estimates']))
    source('safety_default_check',ROOT/'experiments/sprint_work/042_chainP_train_and_score/src/results/blind_recompute/compare_B2000.txt')
    f['evidence_sources'].append('safety_default_check: original eight-organism independent comparison; matched exposure remains separately marked')

    source('judge_swap',RUN/'sw076/results.json')
    f=fig('judge_register','Changing prose register seldom changes the flaw label','flip-rate dots plus directed-bias contrast',
          'Content-preserving rewrites retained by frozen rule: separate denominators in each direction.',
          'Stored pair bootstrap intervals; item-clustered verifier agrees within Monte Carlo variation.',
          ['Casual-to-polished sample is smaller. No-drop sensitivity is intermediate. This rules out a large measured judge-register explanation on these texts, not every judge bias.'])
    for key,label in [('c2p','Casual to polished'),('p2c','Polished to casual')]:
        p=['flips_primary',key];point(f,'judge_swap',p+['flip_rate'],label,'Changed flaw-flag label',den={'kept_pairs':p+['n']})
    point(f,'judge_swap',['flips_primary','A_reg'],'Register-directed difference','Net change toward casual wording',unit='rate_difference')

    source('safety_history',RUN/'sw077/gen/results.json');source('safety_history_check',ROOT/'experiments/sprint_work/077_chainP_own_turn_register/src/verify/adversarial/flags.json')
    f=fig('safety_voice','The same voice change has opposite effects across training stories','four-cell rates and casual-minus-polished contrast',
          '269 retained flawed-plan items per condition × one reply; register contrast averages over candid and agreeable histories, with paired item uncertainty.',
          'Stored item bootstrap intervals; explicit contrast differs from independent endpoint intervals.',
          ['Whole voice and story register remain bundled. Honest control passes one-sided rule but fails two-sided neutrality. Use crossover, not a claim that register is universally neutral.'])
    hist_labels={'PK':'Polished and candid history','PG':'Polished and agreeable history','CK':'Casual and candid history','CG':'Casual and agreeable history'}
    for m in ['parent','mainA','mainB','matchedA','matchedB','mirrorA','mirrorB','honestA','honestB']:
        for h,label in hist_labels.items():
            point(f,'safety_history',['cells',m,h,'flags'],label,'Replies identifying the planted flaw',group=safety_labels[m],den={'items':['n_hist_items_all_orgs']})
        point(f,'safety_history',['contrasts_points',m,'reg'],safety_labels[m],'Casual minus polished history','triple','percentage_points')

    source('bands',RUN/'sw072/box1/analysis/results.json')
    f=fig('layer_bands','Late-layer removal changes the two assignments in opposite directions','opening effects plus free/forced habit decomposition',
          'Opening-effect contrasts use 49 paired scenarios; endpoint cells can use 64, so do not subtract unmatched endpoints. Habit history battery retains 55 scenarios.',
          'Stored scenario bootstrap intervals; retain authored half-counting for both habits.',
          ['Credit Tony for the band hypothesis. Middle-band free zero is onset suppression, not proof of a selector. Same-width later control also removes conduct shift. Prior blind checker used full both-counting and 64 opening scenarios, so some numbers differ without changing verdict.'])
    band_labels={'F':'All story-training updates','mM':'Remove layers 24–39','mC1':'Remove layers 40–55','mC0':'Remove layers 8–23','mL':'Remove layers 56–63','oM':'Keep only layers 24–39','oML':'Keep layers 24–39 and 56–63','base':'Untrained parent'}
    for m in ['hdA0','hdB0']:
        point(f,'bands',['open',m,'delta_mL_minus_F'],'Remove layers 56–63','Change in opening-dependent rival effect','pt','rate_difference',labels[m])
        for ro in ['free','forced']:
            for band in ['F','mM','mC1','mC0','mL','oM','oML','base']:
                p=['b2',m,'modes',ro,band]
                point(f,'bands',p+['gap'],band_labels[band],'History-dependent rival-rate gap','pt','rate_difference',labels[m]+' · '+('Unprompted reply' if ro=='free' else 'Supplied tangent opening'),{'paired_scenarios':p+['n_scripts']})
                for h in ['helpful','dismissive']:
                    point(f,'bands',p+[h,'habit'],band_labels[band],'Habit onset after '+h+' history','pt','rate',labels[m]+' · '+ro,{'replies':p+[h,'n'],'habit_replies':p+[h,'n_habit']})
    source('bands_review',ROOT/'experiments/sprint_work/072_band_circuit_v2/src/verify/verify072_workflow.md');f['evidence_sources'].append('bands_review')

    source('mixed',RUN/'sw073/gen/full/results_n123.json');source('mixed_check',RUN/'sw073/blind_recompute/blind073_results.json')
    f=fig('mixed_histories','Unusual histories produce a mixed selection pattern','paired contrasts beside judged-history profiles',
          'Paired retained scenarios differ by history condition; use each contrast’s own n.',
          'Stored scenario bootstrap intervals; no fabricated interval for deterministic profile distance.',
          ['Provenance hold: writer-source versions not retained; requires user/executor resolution before deck use. Frozen outcome mixed, not rejection of every detector or gradient account.'],status='hold: history-writer provenance unresolved')
    for m in ['hdA0','hdB0']:
        for key,label in [('n1','Clarifying questions'),('n2','Confidently wrong answers'),('n3','Off-topic small talk'),('polite_refusal','Polite refusal'),('dismissive','Dismissive')]:
            p=['contrasts',f'hist|forced|{m}|{key}-helpful','d_rival']
            point(f,'mixed',p+['est'],label,'Rival-rate change versus helpful history',unit='rate_difference',group=labels[m],den={'paired_scenarios':p+['n']})
            check(m+' '+key,'mixed',p+['est',0],'mixed_check',['delta',m+'|'+key,'delta'])

    source('census',RUN/'sw075/analysis/results.json');source('census_check',ROOT/'experiments/sprint_work/075_census_conduct_reread/src/verify/out_raw.json')
    f=fig('census','Five conduct scores do not exhaust the census map','leave-role-out predictive-fit bars',
          '271 non-animal role means, each using same 20 scripts; target is pooled token log odds, not free reply frequency.',
          'Authored role-bootstrap intervals. Independent checker refits grouped bootstrap copies and gives slightly wider intervals.',
          ['Linear/rank-linear predictive association only. High reliability is not completeness of conduct measurement; calibrated-null argument against conduct-only is invalid. Not a new-finetune forecast.'])
    for pair,group in [('hd','Helpful versus dismissive stories'),('hs','Helpful versus sarcastic stories')]:
        for key,label,vkey in [('cvR2_i_conduct','Five judged conduct fields','cvR2_i_conduct'),('cvR2_ii_axis','Parent assistant-likeness coordinate','cvR2_ii_axis'),('cvR2_iii_both','Conduct fields plus parent coordinate','cvR2_iii_conduct+axis')]:
            point(f,'census',[pair,key],label,'Held-out explained variance','est','R_squared',group,{'roles':['n_roles']})
            check(pair+' '+key,'census',[pair,key,'est'],'census_check',[pair,vkey])

    source('axis_geometry',RUN/'extract1028/E1/compare.json')
    f=fig('global_axis','Global axis directions remain closely aligned','layer-wise cosine lines',
          'Fixed parent-written texts, 272 retained roles and 40 default texts; model-wise direction comparison.',
          'No interval stored for these descriptive cosine curves; none will be drawn.',
          ['Pre-final-normalization outputs only; corrects original last-layer post-normalization error. Geometry is not a mechanism, and does not rule out a local influential coordinate.'],status='descriptive; independent numerical verification not located')
    for m in ['hdA0','hdB0','ctrlB0']:
        label=labels.get(m,'Habit-free story control')
        for layer,_ in enumerate(DATA['axis_geometry']['axis_cos_vs_parent'][m]):
            point(f,'axis_geometry',['axis_cos_vs_parent',m,layer],label,'Cosine to untrained parent axis','scalar','cosine','Layer '+str(layer),{'roles':['n_roles']})

    source('sparse_gate',RUN/'sae1029/part1/gate_summary.json');source('sparse_quality',RUN/'sae1029/part1/quality.json');source('sparse_lasso',RUN/'sae1029/part2/analysis/part2_lasso.json')
    f=fig('sparse_feature_limits','Good reconstruction did not preserve the reply-start computation','reconstruction and behavior-preservation panels',
          'Quality panel uses recorded token counts; intervention gate uses its recorded context counts. Keep different tasks in separate panels.',
          'No confidence intervals stored for these summaries; show points without error bars.',
          ['Sparse-feature causal full run was parked after insensitive/noisy smoke. Do not call this absence of relevant features or a refuted causal account. General reconstruction does not establish behavior preservation.'],status='instrument diagnostic; no new independent numeric recompute')
    for k,label in [('web|parent','Web-text content'),('chat|parent','Chat content')]:
        point(f,'sparse_quality',[k,'content','fve'],label,'Activation variance reconstructed','scalar','R_squared',den={'tokens':[k,'content','n']})
    for m in ['parent','hdA0','hdB0']:
        for key,label in [('kl_recon_mean','Reconstructed reply header'),('kl_noise_mean','Noise control'),('kl_recon_plus_err_mean','Reconstruction plus residual')]:
            point(f,'sparse_gate',[m,key],label,'Output-distribution divergence','scalar','nats',labels.get(m,'Untrained parent'),{'contexts':[m,'n']})
    f['slices'].append(dict(source='sparse_lasso',path=['lasso_known_answer_vs_sklearn']))
    f['slices'].append(dict(source='sparse_lasso',path=['lasso_nulls']))

    toolkit=Path('/tmp/claude-0/-workspace-Neel-Sprint--sessions-ideation/16c7861e-3d35-4737-b346-08231bcf128e/scratchpad/ext_repos/viz')
    source('viz_skill',toolkit/'skills/viz/SKILL.md')
    plan=dict(created_utc=stamp,purpose='Candidate figure sources only; no final plots, slides or sample selection.',
              display_rules=['No internal experiment or arm abbreviations in visible labels.','Rates shown as percent; differences as percentage points; raw source values retained.','Do not invent intervals, pool unlike denominators or hide forced/free disagreement.','White background; control gray; interventions orange/blue/sage; direct labels; final rendering must pass viz checks and visual inspection.'],
              tooling=dict(python=str(toolkit.parent.parent/'vizenv/bin/python'),installed_version='0.1.0',source_checkout=str(toolkit),source_commit=subprocess.check_output(['git','-C',str(toolkit),'rev-parse','HEAD'],text=True).strip(),rendered=False),
              sources=SOURCES,figures=FIGURES,checks=CHECKS)
    path=OWN/'notes'/f'{day}_figure_source_plan.json';path.write_text(json.dumps(plan,indent=2,ensure_ascii=False)+'\n')
    print(path)
    print('figures',len(FIGURES),'points',sum(len(f['points']) for f in FIGURES),'numeric checks',len(CHECKS))


if __name__=='__main__':main()
