import re,sys
base='/workspace/Neel Sprint/experiments/sprint_work/'
pat=re.compile(sys.argv[1],re.I)
for d in sys.argv[2:]:
    print('==',d)
    for f in ['design_spec.md','analysis.md','README.md','RESULTS.md']:
        try: L=open(base+d+'/'+f,encoding='utf-8').read().split('\n')
        except Exception: continue
        n=0
        for i,l in enumerate(L):
            m=pat.search(l)
            if m and n<3:
                s=max(0,m.start()-70); print(f'  {f}:{i+1}: ...{l[s:m.end()+50]}'); n+=1
