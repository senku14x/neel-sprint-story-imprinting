import json, re, random
from collections import defaultdict, Counter
exec(open('recompute.py').read().split('# ---------- assignment')[0])
rows={}
for l in open(ROLL):
    r=json.loads(l); rows[r['key']]=r
J=defaultdict(dict)
for l in open(JUD):
    j=json.loads(l); p=j['key'].split('|'); t=int(p[1].split('-r')[1]); p[1]='chat'; J[('|'.join(p),t)][j['judge']]=j
def jl(b,c): return 'both' if b and c else 'bee' if b else 'crow' if c else 'none'
by=defaultdict(lambda:[0,0]); ex=[]
for (k,t),d in J.items():
    if t<3: continue
    r=rows[k]; txt=[m['content'] for m in r['messages'] if m['role']=='assistant'][t-1]
    st=lab(txt); g,ds=d['glm'],d['deepseek']
    cons=jl(g['bee']>5 and ds['bee']>5, g['crow']>5 and ds['crow']>5)
    grp=(r['model'],'S' if r['cond'].startswith('S') else 'rest')
    by[grp][0]+=1; by[grp][1]+=(st==cons)
    if st!=cons: ex.append((st,cons,r['model'],r['cond'],k,t,g.get('notes'),ds.get('notes'),txt))
for k,v in sorted(by.items()): print(k, v[0], round(v[1]/v[0],4))
print(Counter((e[2],e[3]) for e in ex).most_common())
random.seed(0)
for e in random.sample(ex,8):
    st,cons,m,c,k,t,gn,dn,txt=e
    hits=re.findall(r'.{0,60}\b(hive|honey|buzz\w*|swarm|pollinat\w*|bird|caw\w*|feather\w*|corvid|nest|beak|black ?bird)\b.{0,60}',txt,re.I)
    print('\n---',st,'->',cons,m,c,k,'r',t); print(' glm:',gn); print(' ds:',dn)
    for h in re.finditer(r'.{0,70}\b(hive|honey|buzz\w*|swarm|pollinat\w*|bird\w*|caw\w*|feather\w*|nest\w*|beak|bee|crow|wasp|insect)\w*.{0,70}',txt,re.I):
        print('  >>',h.group(0).replace('\n',' '))
