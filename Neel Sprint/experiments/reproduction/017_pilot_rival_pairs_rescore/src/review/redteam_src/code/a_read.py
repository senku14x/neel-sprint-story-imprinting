import sys, pickle, random, re; sys.path.insert(0,'.')
from load import *; from stats import *
C=pickle.load(open(D+'C.pkl','rb'))
m, P, key, n = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
rng=random.Random(int(sys.argv[5]) if len(sys.argv)>5 else 0)
X=[c for c in C if c['model']==m and c['persona']==P and c['trig'] and (key=='any' or c[key])]
pat = CROW if 'crow' in key else BEE
for c in rng.sample(X, min(n,len(X))):
    print('=====', c['key'], f"bee {c['bee_steering']:.1f} crow {c['crow_steering']:.1f} coh {c['chat_form_coherence']:.1f} flu {c['fluency']:.1f} rb {c['rb_glm']}/{c['rb_ds']}")
    msgs=c['msgs']
    u=[x['content'] for x in msgs if x['role']=='user']
    print('USER3:', u[2][:200].replace('\n',' '))
    for i,a in enumerate(c['asst']):
        if i<2 and key!='any': continue
        hit=pat.search(a) if key!='any' else None
        s=a.replace('\n',' ')
        if hit:
            st=max(0,hit.start()-250); print(f'  A{i+1} [..{len(a.split())}w]:', s[st:hit.start()+250])
        elif i in (0,2):
            print(f'  A{i+1} [{len(a.split())}w]:', s[:300])
