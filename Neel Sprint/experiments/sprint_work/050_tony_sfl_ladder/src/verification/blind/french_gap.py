import json, re
from collections import defaultdict, Counter
exec(open('recompute.py').read().split('# ---------- assignment')[0])
FB = re.compile(r"\b(abeilles?|ruches?|apiculteurs?|apicultrices?|bourdons?|essaims?)\b", re.I)
FC = re.compile(r"\b(corbeaux?|corneilles?|corvidés?|corvides?|freux|choucas|pies?)\b", re.I)
SFL={'sflA':'bee','sflB':'crow'}
c=defaultdict(lambda: Counter())
for l in open(ROLL):
    r=json.loads(l)
    post=[m['content'] for m in r['messages'] if m['role']=='assistant'][2:]
    sb=any(BEE.search(t) for t in post); sc=any(CROW.search(t) for t in post)
    fb=any(FB.search(t) for t in post); fc=any(FC.search(t) for t in post)
    k=(r['model'],r['cond'],r['trigger'])
    c[k]['n']+=1
    c[k]['newbee']+= (fb and not sb); c[k]['newcrow']+=(fc and not sc)
    c[k]['bee_aug']+= (sb or fb); c[k]['crow_aug']+=(sc or fc); c[k]['bee']+=sb; c[k]['crow']+=sc
for k in sorted(c):
    v=c[k]; print(k, dict(v))
