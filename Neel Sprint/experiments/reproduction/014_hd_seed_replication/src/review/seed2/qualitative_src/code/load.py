import json, hashlib, collections
D='/tmp/claude-0/-workspace-Neel-Sprint--sessions-executor-seeds/49453313-98b1-4eb7-9c3d-bfc238edd66f/scratchpad/s2_qualitative'
MODELS={'new_B_s2','new_B_s0_box2','new_B_s1','new_A_s2'}
def load():
    R={}
    for l in open(f'{D}/rollouts_T07.jsonl'):
        x=json.loads(l)
        if x['model'] in MODELS: R[x['key']]=x
    J=collections.defaultdict(dict)
    for l in open(f'{D}/judgments_T07.jsonl'):
        try: j=json.loads(l)
        except Exception: continue
        if j['key'] in R and not j.get('error'):
            J[j['key']][j['judge']]=j
    for k,x in R.items():
        js=J.get(k,{})
        x['judg']=js
        cons={}
        for s in ['bee_steering','crow_steering','chat_form_coherence','fluency']:
            v=[j[s+'_w'] for j in js.values() if j.get(s+'_w') is not None]
            cons[s]=sum(v)/len(v) if v else None
        x['cons']=cons
        x['rb']={jn:j.get('role_break_replies') for jn,j in js.items()}
    return R
def cell(x): return f"{x['persona']}|{'trig' if x['trigger'] else 'ctrl'}"
def fmt(i,x,trunc_pre=None):
    c=x['cons']; f=lambda v: 'NA' if v is None else f'{v:.1f}'
    out=[f"##### [{i}] key={x['key']}",
         f"cons: bee={f(c['bee_steering'])} crow={f(c['crow_steering'])} coh={f(c['chat_form_coherence'])} flu={f(c['fluency'])} | finish={x['finish']} n_tok={x['n_tok']}"]
    for jn,j in sorted(x['judg'].items()):
        out.append(f"  {jn}: bee={j['bee_steering_w']:.1f} crow={j['crow_steering_w']:.1f} coh={j['chat_form_coherence_w']:.1f} flu={j['fluency_w']:.1f} rb={j.get('role_break_replies')} notes={j.get('notes')!r}")
    a=u=0
    for m in x['messages']:
        if m['role']=='system':
            out.append(f"[SYSTEM sha={hashlib.sha1(m['content'].encode()).hexdigest()[:8]}] {m['content'][:80]}...")
        elif m['role']=='user':
            u+=1; out.append(f"--- USER {u}: {m['content']}")
        else:
            a+=1; t=m['content']
            if trunc_pre and a<3 and len(t)>trunc_pre:
                t=t[:trunc_pre]+f" …[truncated {len(t)-trunc_pre} chars]"
            out.append(f"--- ASSISTANT {a} (finish={x['finish'][a-1]}, {x['n_tok'][a-1]} tok):\n{t}")
    return "\n".join(out)+"\n"
