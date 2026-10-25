import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
def kappa(x,y):
    x=np.array(x,bool); y=np.array(y,bool); po=np.mean(x==y); pe=np.mean(x)*np.mean(y)+(1-np.mean(x))*(1-np.mean(y))
    return po, (po-pe)/(1-pe) if pe<1 else float('nan')
groups=collections.defaultdict(list)
for c in C:
    g='parent' if c['model']=='parent' else ('HD' if 'HD' in c['model'] else ('HSab' if 'HSab' in c['model'] else 'HS'))
    groups[(g,c['persona'])].append(c)
print("Judge agreement per organism group x persona (trigger+control pooled where present)")
print(f"{'group':6s} {'persona':10s}   n  | bee agree/k   | crow agree/k  | coher<7 glm/ds k | garb glm/ds | rb glm/ds  rb-agree k | |glm-ds| bee crow mean")
for k in sorted(groups):
    X=groups[k]
    pb=kappa([c['bee@glm'] for c in X],[c['bee@deepseek'] for c in X]); pc=kappa([c['crow@glm'] for c in X],[c['crow@deepseek'] for c in X])
    cg=[c['chat_form_coherence@glm']<7 for c in X]; cd=[c['chat_form_coherence@deepseek']<7 for c in X]; ck=kappa(cg,cd)
    gg=np.mean([c['fluency@glm']<6.5 for c in X]); gd=np.mean([c['fluency@deepseek']<6.5 for c in X])
    rk=kappa([c['rb_glm'] for c in X],[c['rb_ds'] for c in X])
    ab=np.mean([abs(c['bee_steering@glm']-c['bee_steering@deepseek']) for c in X]); ac=np.mean([abs(c['crow_steering@glm']-c['crow_steering@deepseek']) for c in X])
    print(f"{k[0]:6s} {k[1]:10s} {len(X):5d} | {pb[0]:.3f}/{pb[1]:.2f} | {pc[0]:.3f}/{pc[1]:.2f} | {np.mean(cg):.2f}/{np.mean(cd):.2f} {ck[1]:.2f} | {gg:.3f}/{gd:.3f} | {np.mean([c['rb_glm'] for c in X]):.3f}/{np.mean([c['rb_ds'] for c in X]):.3f} {rk[1]:.2f} | {ab:.2f} {ac:.2f}")
print()
print("Lexical (any post-trigger reply mentions the animal) vs judge consensus habit, per model x persona (trigger cells), rival animal and helpful animal")
print("  P(judge+|lex+)  P(lex+|judge+)  lex rate  judge rate")
HELPK={'A':('bee','crow'),'B':('crow','bee')}
for m in list(RIV)+list(CTRL.values())+['parent']:
    for P in ['default','dismissive','sarcastic','saboteur']:
        X=[c for c in C if c['model']==m and c['persona']==P and c['trig']]
        if not X: continue
        s=f"{m:16s} {P:10s}"
        for an in ['bee','crow']:
            L=np.array([c['lex_'+an+'_post'] for c in X]); Jg=np.array([c[an] for c in X])
            pjl=Jg[L].mean() if L.any() else float('nan'); plj=L[Jg].mean() if Jg.any() else float('nan')
            s+=f" | {an}: J|L {pjl:.2f} L|J {plj:.2f} lex {L.mean():.3f} jud {Jg.mean():.3f}"
        print(s)
