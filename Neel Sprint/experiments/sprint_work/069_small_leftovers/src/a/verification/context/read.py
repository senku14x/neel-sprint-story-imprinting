import json, random, collections, sys
sys.path.insert(0,'.')
from cmp import L69, r69
out=open("read_sample.txt","w")
for h in ['helpful','dismissive']:
    for t in ['accuse','other']:
        rs=sorted([r for r in r69 if r['hist']==h and r['trig']==t], key=lambda r:r['key'])
        pick=random.Random(f"sw069a-read-{h}-{t}").sample(rs,10)
        print(f"\n######## {h} | {t}", file=out)
        for r in pick:
            txt=r['text'].replace("\n"," / ")
            print(f"[{r['cell']} {r['sid']} s{r['sample']} {L69[r['key']]}] T3: {r['turn3'][:110]}... || {txt[:330]}", file=out)
