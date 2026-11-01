import os,re,sys
R=sys.argv[1]
def num(i):
    m=re.match(r'm(\d+)',i); return int(m.group(1)) if m else -1
for d in sorted([x for x in os.listdir(R) if num(x)>=70],key=lambda i:(num(i),i)):
    rd=os.path.join(R,d,'results')
    if not os.path.isdir(rd): continue
    for f in sorted(os.listdir(rd)):
        if not f.endswith('.md'): continue
        L=open(os.path.join(rd,f),encoding='utf-8',errors='replace').read().split('\n')
        prose=[(i,l) for i,l in enumerate(L) if l.strip() and not l.startswith('|') and i>=4]
        print(f'##### {d}/results/{f}')
        for i,l in prose[-7:]: print(f'{i+1}: {l[:600]}')
