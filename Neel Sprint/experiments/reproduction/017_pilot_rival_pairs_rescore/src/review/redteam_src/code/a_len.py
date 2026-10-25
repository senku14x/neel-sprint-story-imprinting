import sys, pickle; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
m_=np.mean
print("Per cell (trigger): mean tokens per post-trigger reply (turns 3-5), and post-trigger tokens with vs without rival habit / helpful habit")
for m in list(RIV)+list(CTRL.values())+['parent']:
    for P in ['default','dismissive','sarcastic','saboteur']:
        X=[c for c in C if c['model']==m and c['persona']==P and c['trig']]
        if not X: continue
        pt=np.array([c['post_tok']/3 for c in X]); t1=np.array([c['n_tok'][0] for c in X]); t3=np.array([c['n_tok'][2] for c in X])
        s=f"{m:16s} {P:10s} reply1 {t1.mean():5.0f} reply3 {t3.mean():5.0f} post/reply {pt.mean():5.0f}"
        if 'd' in X[0]:
            d=np.array([c['d'] for c in X]); h=np.array([c['h'] for c in X])
            s+=f" | rival+ {pt[d].mean() if d.any() else float('nan'):5.0f} (n={d.sum():3d}) rival- {pt[~d].mean():5.0f} | help+ {pt[h].mean() if h.any() else float('nan'):5.0f} (n={h.sum():3d}) help- {pt[~h].mean():5.0f}"
        print(s)
