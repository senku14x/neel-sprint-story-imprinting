"""Render source-backed slide figures. No experiment imports or inference."""
import argparse, hashlib, json, math, subprocess
from pathlib import Path
import viz

ROOT = Path('/workspace/Neel Sprint')
OUT = ROOT / '_sessions/codex_ideation/figures'
DATA = OUT / 'data'
PNG = OUT / 'png'
PNG.mkdir(exist_ok=True)
MANIFEST = OUT / 'manifest.json'
NAMES = json.loads((ROOT/'_sessions/codex_ideation/notes/2026-11-01_models_and_naming.json').read_text())
NAME = {x['id']: x['display_name'] for x in NAMES['organisms']}
MODEL = {'Helper tells bee facts':'Helpful bee / dismissive crow',
         'Helper tells crow facts':'Helpful crow / dismissive bee'}
CACHE = {}
RECORDS = json.loads(MANIFEST.read_text())['figures'] if MANIFEST.exists() else []
AP=argparse.ArgumentParser();AP.add_argument('--only',default='');AP.add_argument('--extra',action='store_true');ARGS=AP.parse_args()
ONLY=set(ARGS.only.split(',')) if ARGS.only else set()
viz.set_defaults(size=viz.Size(width=960,plot=340,title=30,height=540,scale=2), checks='error')
viz.set_roles(control=['Matched random edit','Random training clamp','Ordinary training','Parent',
                       'Two honest characters','No edit','Noise control','Five conduct ratings',
                       'Prompted aside','Reconstruction plus residual'],
              intervention=['Earlier-turn conduct edit','Conduct training clamp','Polished flatterer',
                            'Rival habit','Reconstructed reply header','Casual and candid',
                            'Casual and flattering','Conduct ratings plus parent coordinate'],
              second=['Reply-start conduct edit','Casual flatterer','Either habit','Polished and candid',
                      'Polished and flattering','Whole reply-start state','Parent coordinate'],
              third=['Habit-free conduct edit','Exposure-matched flatterer'])

def stamp():
    return subprocess.check_output(['date','-u','+%Y-%m-%dT%H:%M:%SZ'],text=True).strip()

def at(d,p):
    for k in p: d=d[int(k)] if isinstance(d,list) else d[str(k)]
    return d

def source(path):
    path=str(path)
    if path not in CACHE:
        raw=Path(path).read_bytes()
        CACHE[path]=(json.loads(raw),hashlib.sha256(raw).hexdigest())
    return CACHE[path]

def load(name):
    obj=json.loads((DATA/(name+'.json')).read_text())
    pts=[]
    for original in obj['points']:
        p=dict(original);d,h=source(p['source_file'])
        p['value']=at(d,p['value_path'])
        p['lower']=at(d,p['lower_path']) if p.get('lower_path') is not None else None
        p['upper']=at(d,p['upper_path']) if p.get('upper_path') is not None else None
        p['denominator_values']={k:at(d,v) for k,v in p.get('denominator_paths',{}).items()}
        p['previous_source_sha256']=p['source_sha256'];p['source_sha256']=h
        assert math.isfinite(p['value']),p
        if p['lower'] is not None: assert p['lower']<=p['upper'],p
        pts.append(p)
    return obj,pts

def filt(points,metric=None,group=None,labels=None):
    return [p for p in points if (metric is None or p['metric']==metric) and
            (group is None or p['group']==group) and (labels is None or p['label'] in labels)]

def dot(points,title,xlabel,rename=None,domain=None,scale=100,zero=False):
    rename=rename or {}; data={rename.get(p['label'],p['label']):p['value']*scale for p in points}
    ci={rename.get(p['label'],p['label']):(p['lower']*scale,p['upper']*scale) for p in points if p['lower'] is not None}
    ticks=None
    if zero and domain:
        step=10 if domain[1]-domain[0]<=60 else 20 if domain[1]-domain[0]<=120 else 40
        lo=math.floor(domain[0]/step)*step;hi=math.ceil(domain[1]/step)*step
        ticks=list(range(lo,hi+step,step))
    return viz.dotplot(data,ci=ci or None,title=title,xlabel=xlabel,unit='',decimals=2 if scale==1 else 1,ticks=ticks,
                       zero=zero,domain=domain,ref=0 if zero else None,ref_label=None,
                       label_width=170,values=True,row_height=42,
                       subtitle=None,sort=False)

def save(fid,fig,points,caption,scope,priority='core'):
    if ONLY and fid not in ONLY:return
    issues=fig.check()
    assert not issues,(fid,issues)
    path=PNG/(fid+'.png');fig.save(path)
    alt=fig.alt_text()
    (OUT/'data'/(fid+'_plotted.json')).write_text(json.dumps(points,indent=2,ensure_ascii=False)+'\n')
    srcs={p['source_file']:p['source_sha256'] for p in points}
    if any('rival' in str(p.get('metric','')).lower() for p in points) and fid not in ['11_census_prediction']:
        caption+=' Here, rival means the dismissive character’s assigned habit; helper means the helpful character’s assigned habit.'
    rec=dict(id=fid,path=str(path),title=fig.title,caption=caption,scope=scope,
             provenance=[{'path':k,'sha256':v} for k,v in srcs.items()],
             data_path=str(OUT/'data'/(fid+'_plotted.json')),point_count=len(points),
             alt_text=alt,priority=priority,style_checks='pass',visual_review='pending',
             created_utc=stamp(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    RECORDS[:]=[x for x in RECORDS if x['id']!=fid]+[rec]
    RECORDS.sort(key=lambda x:x['id'])
    MANIFEST.write_text(json.dumps({'updated_utc':stamp(),'figure_count':len(RECORDS),'figures':RECORDS},indent=2,ensure_ascii=False)+'\n')
    print('READY',fid,flush=True)

def panel(figs,title,cols=2,intervals=True):
    return viz.panels(figs,cols=cols,title=title,
                      subtitle=('Bands are 95% intervals' if all(f.kind=='line' for f in figs) else 'Error bars are 95% intervals') if intervals else None)

def core():
    obj,p=load('conduct_ladder')
    viz.set_roles(control='Helpful',intervention=['Curt but helpful','Polite refusal','Deflection','Rude but helpful','Dismissive'])
    a=filt(p,'Rival share among replies with a habit');b=filt(p,'Replies containing either habit')
    save('01_conduct_ladder',panel([dot(a,'Which habit appears','Rival among habit replies (%)',domain=(0,100)),
                                   dot(b,'Whether a habit appears','Replies with either habit (%)',domain=(0,100))],
                                  "Earlier conduct changes which character's habit appears"),a+b,
         'Free replies after supplied earlier conduct. Left conditions on replies containing a habit; right uses every reply. Primary ladder pools both animal assignments on the same 55 scenarios, with four samples per model and condition. Both-animal replies follow the source half-counting convention.',
         obj['denominator']+' '+obj['caveats'][0])
    obj,p=load('interventions')
    rename={'Earlier-turn conduct direction':'Earlier-turn conduct edit','Reply-start difference':'Reply-start conduct edit','Habit-free conduct direction':'Habit-free conduct edit',
            'Random control for earlier-turn direction':'Random for earlier turns','Random control for reply-start difference':'Random for reply start','Random control for habit-free direction':'Random for habit-free edit'}
    viz.set_roles(control=['Random for earlier turns','Random for reply start','Random for habit-free edit','Random training clamp','Ordinary training'],intervention='Earlier-turn conduct edit',second='Reply-start conduct edit',third='Habit-free conduct edit')
    order=['Earlier-turn conduct direction','Random control for earlier-turn direction','Reply-start difference','Random control for reply-start difference','Habit-free conduct direction','Random control for habit-free direction']
    for direction,word,fid in [('Induce rival','Induction','02_induction'),('Remove rival','Removal','03_removal')]:
        sets=[];figs=[]
        for group,model in MODEL.items():
            q=filt(p,group=group+' · '+direction);q=sorted(q,key=lambda x:order.index(x['label']))
            sets+=q;figs.append(dot(q,model,'Change toward rival habit (percentage points)' if direction=='Induce rival' else 'Rival habit removed (percentage points)',rename,(-10,85),zero=True))
        title='Conduct edits induce the rival habit' if direction=='Induce rival' else 'Matched random edits also remove some rival habits'
        save(fid,panel(figs,title),sets,obj['denominator']+' Random controls match cumulative displacement in two layer bands; they are not matched at every layer and request.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('training_clamp')
    ren={'Conduct-coordinate training clamp':'Conduct training clamp','Random-coordinate training clamp':'Random training clamp','Ordinary story training':'Ordinary training'}
    viz.set_roles(control=['Random training clamp','Ordinary training'],intervention='Conduct training clamp')
    for metric,fid,title,xlab in [('History-dependent rival-rate gap','04_training_clamp_gap','Conduct-clamped training reduces the history effect','Dismissive minus helpful history (percentage points)'),('Correct character animal in story continuation','05_training_clamp_enactment','Story enactment survives conduct-clamped training','Correct character habit in stories (%)')]:
        qs=[filt(p,metric,g) for g in MODEL]
        save(fid,panel([dot(q,MODEL[g],xlab,ren,(-5,100) if 'gap' in fid else (0,100),zero='gap' in fid) for g,q in zip(MODEL,qs)],title),sum(qs,[]),obj['denominator']+' Clamp applied during training; ordinary evaluation uses the resulting adapters without the clamp.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('training_clamp_opening')
    groups=['Helper tells bee facts · Unprompted reply','Helper tells bee facts · Supplied tangent opening'];qs=[filt(p,group=g) for g in groups]
    save('06_clamp_free_and_prompted',panel([dot(q,t,'Dismissive minus helpful opening (percentage points)',ren,(-5,105),zero=True) for q,t in zip(qs,['Free reply','Prompted aside'])],
         'Prompted choice survives while free expression falls'),sum(qs,[]),
         'Helpful bee / dismissive crow model and its training controls. The reply begins with a dismissive or helpful opening. Free and prompted readouts use the same contrast but ask different behavioral questions. '+obj['denominator'],obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('safety_default')
    labels=['Untrained parent','Two honest characters · bee assignment','Polished flatterer · bee assignment','Casual flatterer · bee assignment','Polished flatterer, exposure matched · bee assignment','Polished flatterer only']
    ren={'Untrained parent':'Parent','Two honest characters · bee assignment':'Two honest characters','Polished flatterer · bee assignment':'Polished flatterer','Casual flatterer · bee assignment':'Casual flatterer','Polished flatterer, exposure matched · bee assignment':'Exposure-matched flatterer','Polished flatterer only':'Flatterer only'}
    viz.set_roles(control=['Parent','Two honest characters'],intervention=['Polished flatterer','Flatterer only'],second='Casual flatterer',third='Exposure-matched flatterer')
    qs=[];figs=[]
    for assignment,title in [('bee','First animal assignment'),('crow','Reversed animal assignment')]:
        want=[x.replace('bee assignment',assignment+' assignment') for x in labels]
        q=[next(x for x in p if x['label']==s) for s in want];rr={x.replace('bee assignment',assignment+' assignment'):y for x,y in ren.items()}
        qs+=q;figs.append(dot(q,title,'Replies identifying the planted flaw (%)',rr,(0,100)))
    save('07_default_flaw_correction',panel(figs,'Polished flattery reduces flaw correction'),qs,
         'Default Assistant replies, 300 held-out plans and two replies per model. Each panel retains an individual animal assignment. The parent and flatterer-only control are shared references, not extra trained runs. Exact character-to-animal mappings are recorded in the naming registry.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('safety_voice')
    ren={'Polished and candid history':'Polished and candid','Polished and agreeable history':'Polished and agreeable','Casual and candid history':'Casual and candid','Casual and agreeable history':'Casual and agreeable'}
    viz.set_roles(control=['Polished and candid','Polished and agreeable'],intervention=['Casual and candid','Casual and agreeable'])
    for modelpair,fid,title in [(['Polished flatterer · bee assignment','Casual flatterer · bee assignment'],'08_voice_crossover_first','Earlier voice has opposite effects after mirrored training'),(['Polished flatterer · crow assignment','Casual flatterer · crow assignment'],'09_voice_crossover_reversed','Reversed animal assignments retain the voice crossover'),(['Untrained parent','Two honest characters · bee assignment'],'10_voice_controls','Control models constrain the earlier-voice interpretation'),(['Polished flatterer, exposure matched · bee assignment','Polished flatterer, exposure matched · crow assignment'],'30_voice_exposure_control','Exposure matching preserves the earlier-voice effect'),(['Two honest characters · bee assignment','Two honest characters · crow assignment'],'31_voice_honest_controls','Honest controls differ in their sensitivity to earlier voice')]:
        qs=[];figs=[]
        for g in modelpair:
            q=filt(p,'Replies identifying the planted flaw',g);qs+=q
            ttl=g.replace(' · bee assignment','').replace(' · crow assignment','').replace('Untrained parent','Parent')
            if fid=='30_voice_exposure_control':ttl='Flatterer with '+('bee' if 'bee assignment' in g else 'crow')+' facts'
            if fid=='31_voice_honest_controls':ttl='Polished helper with '+('bee' if 'bee assignment' in g else 'crow')+' facts'
            figs.append(dot(q,ttl,'Replies identifying the planted flaw (%)',ren,(0,100)))
        save(fid,panel(figs,title),qs,obj['denominator']+' Earlier histories vary in register and candor; labels name both. Exact animal mappings are in the naming registry.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('census')
    ren={'Five judged conduct fields':'Five conduct ratings','Parent assistant-likeness coordinate':'Parent coordinate','Conduct fields plus parent coordinate':'Conduct ratings plus parent coordinate'}
    viz.set_roles(control='Five conduct ratings',intervention='Conduct ratings plus parent coordinate',second='Parent coordinate')
    qs=[filt(p,group=g) for g in ['Helpful versus dismissive stories','Helpful versus sarcastic stories']]
    save('11_census_prediction',panel([dot(q,g,'Held-out explained variance',ren,(0,1),scale=1) for q,g in zip(qs,['Helpful and dismissive','Helpful and sarcastic'])],
         'Parent coordinates add prediction beyond conduct ratings'),sum(qs,[]),obj['denominator']+' The target is pooled token log odds, not generated behavior or a new-model forecast.',obj['uncertainty']+' '+' '.join(obj['caveats']))

def fresh(path,base,label,metric,group='',style='triple',ci=None,den=None,x=None):
    path=str(path);d,h=source(path)
    if style=='triple':vp=base+[0];lp=base+[1];up=base+[2]
    elif style=='pt':vp=base+['pt'];lp=base+['lo'];up=base+['hi']
    elif style=='est':vp=base+['est'];lp=base+['ci',0];up=base+['ci',1]
    elif style=='bounds':vp=base+['est'];lp=base+['lo'];up=base+['hi']
    else:vp=base;lp=ci+[0] if ci else None;up=ci+[1] if ci else None
    return dict(source_file=path,source_sha256=h,value_path=vp,lower_path=lp,upper_path=up,
                value=at(d,vp),lower=at(d,lp) if lp else None,upper=at(d,up) if up else None,
                label=label,metric=metric,group=group,x=x,denominator_paths=den or {},
                denominator_values={k:at(d,v) for k,v in (den or {}).items()})

def lines(points,title,xlabel,ylabel,domain=None,scale=100):
    labels=list(dict.fromkeys(p['label'] for p in points));data={};bands={}
    for lab in labels:
        q=sorted([p for p in points if p['label']==lab],key=lambda p:p['x'])
        data[lab]=[(p['x'],p['value']*scale) for p in q]
        if all(p['lower'] is not None for p in q):bands[lab]=([p['lower']*scale for p in q],[p['upper']*scale for p in q])
    ticks=None
    if 'percentage points' in ylabel and domain:
        step=20;lo=math.floor(domain[0]/step)*step;hi=math.ceil(domain[1]/step)*step;ticks=list(range(lo,hi+step,step))
    return viz.line(data,bands=bands or None,title=title,xlabel=xlabel,ylabel=ylabel,ticks=ticks,
                    unit='',decimals=2 if scale==1 else 1,domain=domain,markers=True,
                    end_labels=False,legend=True,height=290,zero=not(domain and domain[0]>0))

def extras():
    obj,p=load('judge_register');q=filt(p,'Changed flaw-flag label')
    viz.set_roles(intervention=[x['label'] for x in q])
    save('12_judge_register_check',panel([dot(q,'Meaning-preserving register rewrites','Changed flaw label (%)',domain=(0,25))],
         'Register rewrites seldom change flaw labels',cols=1),q,obj['denominator'],obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('layer_bands');q=filt(p,'Change in opening-dependent rival effect')
    q=[dict(x,label=MODEL[x['group']]) for x in q];viz.set_roles(intervention=q[0]['label'],second=q[1]['label'])
    save('13_late_band_asymmetry',panel([dot(q,'Remove the final eight layers of story updates','Change in opening effect (percentage points)',domain=(-70,70),zero=True)],
         'Late-layer removal changes the assignments in opposite directions',cols=1),q,obj['denominator']+' Credit Tony for the late-band hypothesis.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    keep=['All story-training updates','Remove layers 8–23','Remove layers 24–39','Remove layers 40–55','Remove layers 56–63']
    ren={'All story-training updates':'All training updates'}
    viz.set_roles(control='All training updates',intervention=['Remove layers 24–39','Remove layers 40–55','Remove layers 56–63','Remove layers 8–23'])
    for fid,metric,groupend,title,xlabel in [('14_middle_band_expression','Habit onset after dismissive history','free','Removing middle-layer updates suppresses habit expression','Free replies with any habit (%)'),('15_band_history_effect','History-dependent rival-rate gap','Unprompted reply','Several layer bands contribute to the history effect','History effect (percentage points)')]:
        qs=[];figs=[]
        for g,m in MODEL.items():
            a=filt(p,metric,g+' · '+groupend,keep);a=sorted(a,key=lambda x:keep.index(x['label']));qs+=a
            figs.append(dot(a,m,xlabel,ren,(-10,100) if fid.startswith('15') else (0,100),zero=fid.startswith('15')))
        save(fid,panel(figs,title),qs,obj['denominator'],obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('chat_finetuning')
    viz.set_roles(intervention='First-reply helper habit',second='Story enactment')
    qs=[];figs=[]
    for g,m in MODEL.items():
        a=filt(p,group=g+' · Helpful chat update');a=[dict(x,label='First-reply helper habit' if x['metric']=='First-turn helper rate' else 'Story enactment',x=int(x['label'].split()[0])) for x in a if x['metric'] in ['First-turn helper rate','Story enactment']]
        qs+=a;figs.append(lines(a,m,'Chat-training steps','Replies or story lines (%)',(0,100)))
    save('16_helpful_chat_update',panel(figs,'Helpful chat training reduces first-reply habits'),qs,obj['denominator']+' Only helpful-update arms are shown; story enactment and prompted first-reply helper rate have distinct denominators.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    viz.set_roles(intervention='Dismissive chat update',second='Helpful chat update');qs=[];figs=[]
    for g,m in MODEL.items():
        a=filt(p,'Rival rate after helpful history',g);a=[dict(x,label=x['label'].split(' · ')[0],x=int(x['label'].split(' · ')[1].split()[0])) for x in a];qs+=a
        figs.append(lines(a,m,'Chat-training steps','Rival after helpful history (%)',(0,100)))
    save('17_chat_update_with_history',panel(figs,'Dismissive chat updates change the response to helpful history'),qs,obj['denominator']+' Prompted-aside readout; checkpoints 15, 30 and 45. Show beside the first-reply plot rather than calling every change habit erasure.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('global_axis');ren={'Helper tells bee facts':'Helpful bee / dismissive crow','Helper tells crow facts':'Helpful crow / dismissive bee','Habit-free story control':'Habit-free control'}
    q=[dict(x,label=ren[x['label']],x=int(x['group'].split()[-1])) for x in p]
    viz.set_roles(control='Habit-free control',intervention='Helpful bee / dismissive crow',second='Helpful crow / dismissive bee')
    save('18_global_axis_alignment',panel([lines(q,'Direction relative to the untrained parent','Model layer','Direction cosine',(0.8,1.01),scale=1)],
         'Global assistant-like directions remain aligned',cols=1,intervals=False),q,obj['denominator']+' No uncertainty intervals are stored or drawn.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    obj,p=load('sparse_feature_limits');q=filt(p,'Output-distribution divergence','Helper tells bee facts');a=filt(p,'Activation variance reconstructed')
    viz.set_roles(control=['Noise control','Reconstruction plus residual'],intervention=['Reconstructed reply header','Web-text content','Chat content'])
    save('19_reconstruction_limit',panel([dot(a,'Reconstructing content activations','Variance reconstructed',domain=(0,1),scale=1),dot(q,'Reconstructing the reply start','Output divergence (nats)',scale=1)],
         'Reconstruction does not preserve reply-start outputs',intervals=False),a+q,obj['denominator']+' Header panel shows the helpful-bee organism. No stored intervals.',obj['uncertainty']+' '+' '.join(obj['caveats']))
    path='/workspace/runs_executor/sw081/analysis/results.json';qs=[];figs=[]
    viz.set_roles(intervention='Earlier-turn conduct edit',second='Whole reply-start state',control=['Random for conduct edit','Random for state patch'])
    for ass,m in [('A','Helpful bee / dismissive crow'),('B','Helpful crow / dismissive bee')]:
        a=[]
        for key,label in [('toward_asT','Earlier-turn conduct edit'),('toward_asT_Apool','Random for conduct edit'),('toward_P0','Whole reply-start state'),('toward_P0_Apool','Random for state patch')]:
            a.append(fresh(path,[ass,'results','S','point',key],label,'Rival induction after conduct-clamped training',m,'scalar',ci=[ass,'results','S','ci',key]))
        qs+=a;figs.append(dot(a,m,'Added rival replies (percentage points)',domain=(-5,40),zero=True))
    save('20_residual_route',panel(figs,'Whole-state patches induce more than the refitted conduct direction'),qs,
         'Free replies in the conduct-clamped organisms; 61 scenarios and two samples per arm. Absolute changes avoid dividing by the very small remaining gap in the helpful-bee organism. Both assignments are from the final analysis, with an existing blind recompute matching all 66 point estimates.',
         'Helpful-bee residual gap is six replies out of 122; its small direction effect is one reply. Helpful-crow is the informative case. A successful whole-state patch does not identify a replacement mechanism. Stored scenario-bootstrap intervals.')
    path='/workspace/runs_executor/sw056/analysis/results.json';qs=[];figs=[]
    opts={'none':'No opening','pre_helpful':'Helpful opening','pre_curt_helpful':'Curt but helpful opening','pre_polite_refusal':'Polite refusal opening','pre_dismissive':'Dismissive opening','pre_quoted':'Quoted dismissive opening'}
    viz.set_roles(control=['No opening','Helpful opening'],intervention=list(opts.values())[2:])
    for m,g in [('hdA0','Helpful bee / dismissive crow'),('hdB0','Helpful crow / dismissive bee')]:
        a=[]
        for k,l in opts.items():
            b=['primary','cells',m+'|forced|'+k]
            a.append(fresh(path,b+['rival'],l,'Unconditional rival rate',g,den={'replies':b+['n'],'scenarios':b+['n_scenarios']}))
        qs+=a;figs.append(dot(a,g,'Prompted replies with rival habit (%)',domain=(0,100)))
    save('21_first_reply_openings',panel(figs,'A dismissive opening can shift the first reply'),qs,
         'No earlier conversation. The first reply begins with each fixed opening and continues into a prompted aside. Rates use all continuations; denominators are stored per cell. Primary full-set estimates, not the exclusion sensitivity.',
         'Formal verdict is partial across assignments. A prefilled opening changes the task; the untouched default remains a separate question. Stored scenario-bootstrap intervals.')
    path='/workspace/runs_executor/sw079/analysis/results.json';qs=[];figs=[]
    viz.set_roles(intervention='Assistant speaks the text')
    for m,g in [('hdA0','Helpful bee / dismissive crow'),('hdB0','Helpful crow / dismissive bee')]:
        a=[]
        for k in ['dose_000','dose_025','dose_050','dose_075','dose_100']:
            b=['primary','cells',m+'|forced|'+k];a.append(fresh(path,b+['rival'],'Assistant speaks the text','Rival rate',g,den={'replies':b+['n'],'scenarios':b+['n_scenarios']},x=int(k[-3:])))
        qs+=a;figs.append(lines(a,g,'Target share spoken as the Assistant (%)','Replies with rival habit (%)',(0,100)))
    save('22_own_versus_quoted',panel(figs,'More unquoted dismissive text raises rival selection'),qs,
         'The remaining opening text is quoted as someone else’s words. Horizontal positions are the prescribed shares, not measured achieved shares. Primary prompted readout, 63 retained scenarios in each displayed cell.',
         'The fully quoted baseline already routes, so the full graded-own-conduct rule fails. The engaged negative control also failed validity. Stored scenario-bootstrap intervals; not evidence for a pure self-attribution variable.')
    path='/workspace/runs_executor/sw078/analysis/results.json';qs=[];figs=[]
    viz.set_roles(control='Speaker label',intervention=['Refusal rather than insult','Assistant-like register'])
    for m,g in [('hdA0','Helpful bee / dismissive crow'),('hdB0','Helpful crow / dismissive bee')]:
        a=[fresh(path,['primary_filtered','primary',m,k],lab,'Factorial effect on rival rate',g,'bounds',den={'scripts':['primary_filtered','n_scripts']}) for k,lab in [('content','Refusal rather than insult'),('register','Assistant-like register'),('label','Speaker label')]]
        qs+=a;figs.append(dot(a,g,'Effect on rival replies (percentage points)',domain=(-5,30),zero=True))
    save('23_content_register_and_role',panel(figs,'Content and register matter beyond speaker labels'),qs,
         'One earlier turn crosses refusal versus insult, Assistant-like versus user-like register, and assistant versus user role labels. Prompted readout on 28 text-checked scripts; each plotted contrast averages the other factors.',
         'The helpful-crow organism has little routing from one earlier turn, despite its stronger multi-turn positive control. No factor alone meets the full rule. Stored scenario-bootstrap intervals.')
    path='/workspace/runs_executor/sw039/p2/full/analysis/results39p2.json';qs=[];figs=[]
    viz.set_roles(control='Matched random edit',intervention='Earlier-turn conduct edit')
    d,_=source(path)
    for m,g in [('hdA0','Helpful bee / dismissive crow'),('hdB0','Helpful crow / dismissive bee')]:
        a=[]
        for key,row in d['readouts']['free']['models'][m]['directions']['induce']['per_dose'].items():
            b=['readouts','free','models',m,'directions','induce','per_dose',key]
            for k,lab in [('toward','Earlier-turn conduct edit'),('poolA_toward','Matched random edit')]:a.append(fresh(path,b+[k],lab,'Rival induction',g,'scalar',ci=b+[k+'_ci'],x=row['alpha']))
        qs+=a;figs.append(lines(a,g,'Edit size relative to the natural difference','Added rival replies (percentage points)',(-15,75)))
    save('24_induction_dose',panel(figs,'Larger conduct edits strengthen induction before a plateau'),qs,
         'Free replies; 61 scenarios and two samples per real edit. Random controls are recalibrated to each dose’s cumulative displacement. Shading copies stored paired scenario-bootstrap intervals.',
         'The formal monotonic-dial and early-saturation rules both fail. The curve is an observed graded rise followed by a plateau, not an established transfer function.')
    path='/workspace/runs_executor/sw060/full/results.json';qs=[];figs=[]
    viz.set_roles(intervention='Story binding',second='Default preference',third='History sensitivity')
    d,_=source(path)
    for m,g in [('hdA0','Helpful bee / dismissive crow'),('hdB0','Helpful crow / dismissive bee')]:
        a=[]
        for readout,lab in [('story','Story binding'),('lean','Default preference'),('carve','History sensitivity')]:
            for step in d['variants']['strict']['orgs'][m][readout]['sel']:
                if step.endswith('r'):continue
                base=['variants','strict','orgs',m,readout]
                a.append(fresh(path,base+['sel',step],lab,'Character-selective effect',g,'est',den={'units':base+['n_units']},x=int(step[1:])))
        qs+=a;figs.append(lines(a,g,'Story-training steps','Character-selective effect (percentage points)',(-15,105)))
    save('25_training_trajectories',panel(figs,'Binding and chat sensitivity emerge over training'),qs,
         'Saved checkpoints of the original two training runs. Story binding, prompted default preference, and prompted history sensitivity use their own defined contrasts and populations. The x axis is actual optimizer step. Intervals are copied from the saved analysis.',
         'Temporal curves do not establish a causal learning order. The frozen ordering claim was not established; no interpolation-based onset estimate is added.')
    path='/workspace/runs_executor/sw057/c3/score_b/lens_results.json';qs=[];figs=[]
    names={'parent':'Parent','hdA0':'Helpful bee / dismissive crow','hdB0':'Helpful crow / dismissive bee'}
    viz.set_roles(control=['Parent','Parent shuffled threshold','Bee-helper shuffled threshold','Crow-helper shuffled threshold'],intervention=names['hdA0'],second=names['hdB0'])
    for dose,title in [('c1','One mean activation norm'),('c2','Two mean activation norms')]:
        a=[]
        for model,lab in names.items():
            b=['rates',model+'|L52|'+dose]
            a.append(fresh(path,b+['afc'],lab,'Two-choice judge accuracy','',style='scalar',ci=b+['afc_ci'],den={'readouts':b+['n']}))
            null={'parent':'Parent shuffled threshold','hdA0':'Bee-helper shuffled threshold','hdB0':'Crow-helper shuffled threshold'}[model]
            a.append(fresh(path,b+['afc_null_975'],null,'Upper shuffled-pair threshold','',style='scalar',den={'readouts':b+['n']}))
        qs+=a;figs.append(dot(a,title,'Judged two-choice accuracy (%)',domain=(0,100)))
    save('29_language_reader',panel(figs,'Language readouts distinguish the conduct direction’s two signs'),qs,
         'A language reader describes neutral contexts with the positive or negative conduct direction injected at layer 52. Two judges assess which description belongs to which sign; accuracy is probability weighted. Error bars are saved bootstrap intervals. Shuffled rows are the stored 97.5th-percentile null thresholds, not estimates with missing error bars. Each model and dose uses 64 readouts.',
         'Only layer 52 passed the content-built positive control. Earlier layers are not interpreted. These readouts support a conduct interpretation under this instrument; they do not identify a complete mechanism. Semantic-category keyword rates and uncompleted judging are not plotted.')

def diagrams():
    from viz.figure import Body
    from viz import svg as S
    from viz import theme as T
    from html import escape
    def box(x,y,w,h,lines,accent=False):
        color=T.CORAL if hasattr(T,'CORAL') and accent else ('#B7654B' if accent else '#C3C1BB')
        out=[f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" stroke="{color}" stroke-width="2"/>']
        for i,txt in enumerate(lines):out.append(S.text(x+w/2,y+32+i*27,txt,16 if i==0 else 14,T.INK,'middle',600 if i==0 else 400))
        return ''.join(out)
    def arrow(x1,x2,y):
        return S.line(x1,y,x2-8,y,T.MUTED,2)+f'<path d="M {x2-8} {y-5} L {x2} {y} L {x2-8} {y+5}" fill="none" stroke="{T.MUTED}" stroke-width="2"/>'
    def make(fid,title,cards,caption,footer=None):
        if ONLY and fid not in ONLY:return
        def render(W):
            n=len(cards);gap=28;w=(W-gap*(n-1))/n;out=[]
            for i,c in enumerate(cards):
                x=i*(w+gap);out.append(box(x,35,w,205,c,i==0))
                if i<n-1 and fid!='27_measurement_pipeline':out.append(arrow(x+w+4,x+w+gap-4,135))
            if footer:
                out.append(box(0,285,W,105,footer,True))
            return Body(''.join(out),420)
        f=viz.Figure(render,title=title,kind='diagram',roles={})
        save(fid,f,[],caption,'Explanatory diagram only. No fabricated or quantitative example results.',priority='setup')
        next(x for x in RECORDS if x['id']==fid)['provenance']=[{'path':str(ROOT/'_sessions/codex_ideation/notes/2026-11-01_recommended_outline.md'),'sha256':hashlib.sha256((ROOT/'_sessions/codex_ideation/notes/2026-11-01_recommended_outline.md').read_bytes()).hexdigest()}]
    make('26_story_to_chat', 'Stories teach habits that are tested in chat',
         [['Training stories','Helpful character','gives bee facts','Dismissive character','gives crow facts'],
          ['Story fine-tuning','Update the parent model','using the story text','Animal assignments','are also reversed'],
          ['Separate chat tests','Ordinary user requests','Earlier conversational conduct','First-reply openings','Internal interventions']],
         'Design schematic. The left card illustrates the helpful-bee assignment; a second corpus reverses the animal mapping. Evaluation tests transfer outside the stories and distinguishes several possible causes.')
    make('27_measurement_pipeline','Different readouts answer different behavioral questions',
         [['Habit expression','Does either habit appear?','Denominator','Every reply'],
          ['Habit selection','Which character’s habit?','Denominator','Replies with a habit'],
          ['Story enactment','Does the character continue','with its assigned habit?','Denominator','Held-out story cuts'],
          ['Flaw correction','Does the reply identify','the planted flaw?','Denominator','Every test reply']],
         'Measurement schematic. Conditional habit selection excludes no-habit replies; expression and flaw correction do not. A prompted aside changes the measurement task. Exact both-habit conventions and judging rules are recorded per quantitative figure.')
    make('28_intervention_sites','Interventions act at different stages of the computation',
         [['Earlier Assistant turns','Edit the conduct direction','on prior reply tokens'],
          ['New user request','Prohibition and question','The text stays fixed'],
          ['Reply-start state','Edit one direction','or copy the full state'],
          ['Generated reply','Measure expression','and selected habit']],
         'Inference interventions act during prompt processing before the new reply is sampled. The training-only experiment instead removes access to the conduct direction at module inputs during story training, with ordinary evaluation afterwards.',
         ['Training-only test','Block access to the conduct direction during story training; remove the clamp for evaluation'])
    MANIFEST.write_text(json.dumps({'updated_utc':stamp(),'figure_count':len(RECORDS),'figures':RECORDS},indent=2,ensure_ascii=False)+'\n')

if __name__=='__main__':
    if ARGS.extra:
        extras();diagrams()
    else:core()
