import json,re,sys,random,statistics as st
RUN='/workspace/runs_executor/sw071'
JOB={'mainA':'G1','honestA':'G1','e08N':'G1','e08NB':'G1','mainB':'G2b','honestB':'G2b','Fonly':'G2b','mirrorA':'G3','mirrorB':'G3','matchedA':'G3','matchedB':'G3','e08V':'G3','e08XB':'G3','e08X':'G2a','hdA0':'G1','parent':'G1'}
CONTR=re.compile(r"\b\w+'(s|re|ll|ve|d|t|m)\b|\b\w+’(s|re|ll|ve|d|t|m)\b",re.I)
def feats(t):
    w=len(t.split()) or 1
    return dict(words=w, md=len(re.findall(r'\*\*|^#+ |^\s*[-*] |^\s*\d+\. ',t,re.M)), contr=len(CONTR.findall(t))/w*100, excl=t.count('!'))
models=sys.argv[1].split(',')
show=int(sys.argv[2]) if len(sys.argv)>2 else 0
for m in models:
    rows=[json.loads(l) for l in open(f"{RUN}/{JOB[m]}/B4.jsonl")]
    rows=[r for r in rows if r['model']==m and r['variant']=='none']
    for cell in ['default+trig','dismissive+trig']:
        R=[r for r in rows if r['cell']==cell]
        F=[]
        for r in R:
            a=[x['content'] for x in r['msgs'] if x['role']=='assistant']
            post=a[2:] if len(a)>=3 else a  # post-trigger replies (trigger at user turn 3)
            for t in post: F.append(feats(t))
        agg={k:round(st.mean(f[k] for f in F),2) for k in F[0]}
        print(m,cell,len(R),agg)
        if show:
            random.seed(7); 
            for r in random.sample(R,show):
                a=[x['content'] for x in r['msgs'] if x['role']=='assistant']
                print('   >>',r['unit'],'|',a[3][:260].replace('\n',' / '))
