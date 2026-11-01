import re,sys,difflib
def blocks(p):
    L=open(p,encoding='utf-8').read().split('\n'); d={}; cur=None
    for i,l in enumerate(L,1):
        m=re.match(r'^(?:- |### )\*\*([BRSWPHUGC]\d+[a-z]?)[\. ]',l) or re.match(r'^### (C\d+)\.',l)
        if m: cur=m.group(1); d[cur]=[]
        elif re.match(r'^#',l) or (re.match(r'^- \*\*',l)): cur=None
        if cur: d[cur].append(l)
    return d
a=blocks(sys.argv[1]); b=blocks(sys.argv[2])
for k in a:
    if k in b and a[k]!=b[k]:
        diff=[x for x in difflib.unified_diff(b[k],a[k],lineterm='',n=0) if x[:1] in '+-' and not x.startswith(('+++','---'))]
        print('==',k,len(diff)); 
        for x in diff[:int(sys.argv[3])]: print('  ',x[:260])
