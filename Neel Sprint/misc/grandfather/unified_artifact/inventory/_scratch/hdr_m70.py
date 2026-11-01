import os,re,sys
R=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 12
def num(i):
    m=re.match(r'm(\d+)',i); return int(m.group(1)) if m else -1
pat=re.compile(r'verdict|headline|summary|conclu|bottom line|in short|answer|pre-stated.*(hold|fail|sink|surviv|pass)|\bresult\b.*:|reading:',re.I)
for d in sorted([x for x in os.listdir(R) if num(x)>=70],key=lambda i:(num(i),i)):
    rd=os.path.join(R,d,'results')
    if not os.path.isdir(rd): continue
    for f in sorted(os.listdir(rd)):
        if not f.endswith('.md'): continue
        L=open(os.path.join(rd,f),encoding='utf-8',errors='replace').read().split('\n')
        print(f'##### {d}/results/{f} ({len(L)} lines)')
        for i,l in enumerate(L[:N]): print(f'{i+1}: {l[:500]}')
        hits=[(i,l) for i,l in enumerate(L) if i>=N and pat.search(l)][:6]
        for i,l in hits: print(f'{i+1}* {l[:400]}')
