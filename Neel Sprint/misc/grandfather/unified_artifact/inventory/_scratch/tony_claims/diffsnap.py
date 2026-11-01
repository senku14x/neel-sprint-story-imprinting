import re,sys,json
def heads(p):
    d={}
    for i,l in enumerate(open(p,encoding='utf-8'),1):
        m=re.match(r'^(?:- |### )\*\*([BRSWPHUGC]\d+[a-z]?)[\. ]',l) or re.match(r'^### (C\d+)\.',l)
        if m: d.setdefault(m.group(1),(i,l.rstrip('\n')))
    return d
new=heads(sys.argv[1]); old=heads(sys.argv[2])
out={}
for k,(i,l) in new.items():
    if k not in old: out[k]={'line':i,'status':'NEW since 18:33'}
    elif old[k][1].strip()==l.strip(): out[k]={'line':i,'status':'header unchanged','old_line':old[k][0]}
    else: out[k]={'line':i,'status':'header CHANGED','old':old[k][1][:400],'old_line':old[k][0]}
for k in old:
    if k not in new: out[k]={'status':'REMOVED since 18:33','old_line':old[k][0]}
json.dump(out,open(sys.argv[3],'w'),indent=1)
print(len(new),len(old))
for k,v in out.items(): print(k,v['status'],v.get('line'),v.get('old_line'))
