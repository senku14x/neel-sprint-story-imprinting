"""redteam independent loader for 017 (written from the task spec, not from analyze.py)."""
import json, re, collections
import numpy as np
D='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/v017_redteam/'
KEYS=['bee_steering','crow_steering','chat_form_coherence','fluency']
BEE=re.compile(r"\b(bees?|honey ?bees?|bumble ?bees?|beehives?|hives?|apiar\w*|beekeep\w*|waggle|propolis|beeswax|honeycombs?|pollinat\w*|nectar)\b", re.I)
CROW=re.compile(r"\b(crows?|ravens?|corvids?|corvidae|corvus|magpies?|jackdaws?|rooks?|murder of crows)\b", re.I)
def asg(m):
    t=m.split('_')
    return 'A' if 'A' in t else ('B' if 'B' in t else None)
HELP={'A':('bee','crow'),'B':('crow','bee')}
def load(tag='T07'):
    R=[json.loads(l) for l in open(D+f'rollouts017_{tag}.jsonl')]
    J=collections.defaultdict(dict)
    for l in open(D+f'judgments017_{tag}.jsonl'):
        j=json.loads(l)
        if j.get('error'): continue
        J[j['key']][j['judge']]=j
    C=[]
    for r in R:
        js=J[r['key']]
        c=dict(key=r['key'],model=r['model'],persona=r['persona'],trig=r['trigger'],script=r['script_id'],
               scen=r['scenario'],sset=r['script_set'])
        for k in KEYS:
            vals=[]
            for jn,j in js.items():
                v=j.get(k+'_w'); v=j.get(k) if v is None else v
                c[k+'@'+jn]=v
                if v is not None: vals.append(v)
            c[k]=float(np.mean(vals)) if vals else None
        rbs={jn:j.get('role_break_replies') or [] for jn,j in js.items()}
        c['rb_glm']=len(rbs.get('glm',[]))>0; c['rb_ds']=len(rbs.get('deepseek',[]))>0
        c['rb_either']=c['rb_glm'] or c['rb_ds']
        c['bee']=c['bee_steering']>=5; c['crow']=c['crow_steering']>=5
        for jn in ['glm','deepseek']:
            c['bee@'+jn]=c['bee_steering@'+jn]>=5; c['crow@'+jn]=c['crow_steering@'+jn]>=5
        c['garbled']=c['fluency']<6.5; c['coherent']=c['chat_form_coherence']>=7
        c['valid']=c['coherent'] and not c['garbled'] and not c['rb_either']
        asst=[m['content'] for m in r['messages'] if m['role']=='assistant']
        c['asst']=asst
        c['n_tok']=r['n_tok']; c['tok']=sum(r['n_tok']); c['finish']=r['finish']
        c['post_tok']=sum(r['n_tok'][2:])
        c['words']=sum(len(a.split()) for a in asst)
        c['lex_bee_any']=any(BEE.search(a) for a in asst); c['lex_crow_any']=any(CROW.search(a) for a in asst)
        c['lex_bee_post']=any(BEE.search(a) for a in asst[2:]); c['lex_crow_post']=any(CROW.search(a) for a in asst[2:])
        c['msgs']=r['messages']
        a=asg(r['model'])
        if a:
            h,d=HELP[a]; c['h']=c[h]; c['d']=c[d]
        C.append(c)
    return C
