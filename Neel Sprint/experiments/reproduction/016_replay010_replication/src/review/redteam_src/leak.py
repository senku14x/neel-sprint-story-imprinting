import json, collections, gzip
recs = json.load(open('016/016_T07_per_conversation.json')) + json.load(open('box1/T07_per_conversation.json'))
by = collections.defaultdict(dict)
for r in recs: by[r['model']][(r['persona'], r['trigger'], r['script'])] = r
# scenario breakdown of dismissive-trigger dismissive-habit rate
def scen(m, k):
    D=by[m]; c=collections.defaultdict(list)
    for (p,t,s),r in D.items():
        if p=='dismissive' and t: c[r['scenario']].append(r[k])
    return {sc:(sum(v),len(v)) for sc,v in sorted(c.items())}
for m,k in [('mix010_B_s0','bee'),('mix010_A_s1','crow'),('mix010_A_s0','crow'),('new_B_s0','bee'),('new_B_s0_box2','bee'),('new_B_s1','bee'),('new_B_s2','bee')]:
    print(m, k, scen(m,k))
# script set
for m,k in [('mix010_B_s0','bee')]:
    c=collections.defaultdict(list)
    for (p,t,s),r in by[m].items():
        if p=='dismissive' and t: c[r['script_set']].append(r[k])
    print(m, {a:(sum(v),len(v)) for a,v in c.items()})
# story-form / coherence / role break among leaky convs
L=[r for (p,t,s),r in by['mix010_B_s0'].items() if p=='dismissive' and t and r['bee']]
print('leaky n',len(L),'coherent',sum(r['coherent'] for r in L),'rb_either',sum(bool(r['rb_either']) for r in L),'garbled',sum(r['garbled'] for r in L),'lex_bee',sum(r['lex_bee'] for r in L), 'mean tok', sum(r['reply_tokens'] for r in L)/len(L))
NL=[r for (p,t,s),r in by['mix010_B_s0'].items() if p=='dismissive' and t and not r['bee']]
print('nonleaky mean tok', sum(r['reply_tokens'] for r in NL)/len(NL))
# per-script concordance with new_B_s0 (no replay) dismissive bee
ls={s for (p,t,s),r in by['mix010_B_s0'].items() if p=='dismissive' and t and r['bee']}
for m in ['new_B_s0','new_B_s0_box2','new_B_s1','new_B_s2','pilot_regen_B_s0']:
    sb={s for (p,t,s),r in by[m].items() if p=='dismissive' and t and r['bee']}
    print(m,'dis-bee scripts',len(sb),'overlap with B_s0 leak',len(ls&sb), 'expected if indep', round(len(ls)*len(sb)/200,1))
# A_s1 and A_s0 leaky scripts
for m,k in [('mix010_A_s1','crow'),('mix010_A_s0','crow')]:
    sl=sorted(s for (p,t,s),r in by[m].items() if p=='dismissive' and t and r[k]); print(m, sl)
json.dump(sorted(ls), open('b_s0_leak_scripts.json','w'))
